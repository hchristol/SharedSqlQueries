# -*- coding: utf-8 -*-
"""
/***************************************************************************
connection to pg a database whose paramaters are read in json config
 ***************************************************************************/
"""

import os
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from qgis.core import *


class Connection:
    #param : list with host, port, dbname :
    def __init__(self, param):
        self.param = param
        #set connector property for the given database type and parameters
        self.uri = QgsDataSourceURI()

        user=""
        if self.param.has_key('user'): user=unicode(self.param['user'])
        pwd=""
        if self.param.has_key('password'): pwd=unicode(self.param['password'])

        self.uri.setConnection(
            unicode(self.param['host']),
            unicode(self.param['port']),
            unicode(self.param['dbname']),
            user,
            pwd
        )

    # perform sql command and return data : [header, data, rowCount]
    def sqlExec(self, sql):
        # Execute a SQL query and, return [header, data, rowCount]
        connector = PostGisDBConnector(self.uri)

        #print "DEBUG dbrequest : sql = " + sql

        try:
            c = connector._execute(None, unicode(sql))
            data = []
            header = connector._get_cursor_columns(c)
        except:
            print "Erreur SQL : " + str(sql)  # debug purpose
            raise

        if header is None:
            header = []

        if len(header) > 0:
            data = connector._fetchall(c)

        row_count = c.rowcount
        if row_count == -1:
            row_count = len(data)

        if c:
            c.close()
            del c

        connector.__del__()

        return [header, data, row_count]

    #perform sql and return 1 value (None if no data)
    def sqlExec1Value(self, sql):
        [header, data,  row_count] = self.sqlExec(sql)
        if row_count == 0: return None
        return data[0][0]

    #perform sql and return 1 list of values (empty list if no data)
    def sqlExec1Column(self, sql):
        [header, data, row_count] = self.sqlExec(sql)
        list = []
        for row in data: list.append(row[0])
        return list

    # add a layer from an sql query. If another layer with the same name already exists, delete it.
    # return the added layer
    def sqlAddLayer(self, sql, layer_name, key_column, geom_column="geom", sqlFilter=""):

        # remove utf8 header character :
        sql = sql.replace(unichr(65279), '')
        # remove new line characters
        sql = sql.replace(chr(13), ' ').replace(chr(10), ' ').replace('\t', ' ')
        # remove ; and blanck at the end of sql
        sql = sql.strip(' ;')

        # allow query with no geometry column
        if geom_column == 'None':
            geom_column = None;

        # print "DEBUG sqlAddLayer geom_column " + str(geom_column)
        self.uri.setDataSource("", "(" + sql + ")", geom_column, sqlFilter, key_column)

        layer = QgsVectorLayer(self.uri.uri(), layer_name, "postgres")
        if not layer:
            print "Layer failed to load!"
            return None

        # Existing layer ?
        layerList = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)
        if (len(layerList)>0):
            QgsMapLayerRegistry.instance().removeMapLayer(layerList[0].id() )

        layer = QgsMapLayerRegistry.instance().addMapLayer(layer, True)

        # print "Debug dbrequest sqlAddLayer : " + layer.name() + u" ajouté !"

        return layer
