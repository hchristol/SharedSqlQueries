# -*- coding: utf-8 -*-
"""
/***************************************************************************
connection to pg a database whose paramaters are read in json config
 ***************************************************************************/
"""

import os
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from qgis.core import *
from processing.tools.vector import VectorWriter

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

        sql = makeSqlValidForLayer(sql)

        # allow query with no geometry column
        if geom_column == 'None':
            geom_column = None

        # print "DEBUG sqlAddLayer geom_column " + str(geom_column)
        self.uri.setDataSource("", "(" + sql + ")", geom_column, sqlFilter, key_column)

        layer = QgsVectorLayer(self.uri.uri(), layer_name, "postgres")

        return addLayer(layer)


    # add a layer into memory from sql. Suited for time consuming query.
    def sqlAddMemoryLayer(self, sql, layer_name, key_column, geom_column="geom", sqlFilter=""):

        sql = makeSqlValidForLayer(sql)

        self.uri.setDataSource("", "(" + sql + ")", geom_column, sqlFilter, key_column)

        # layer postgis to read features
        pg_layer = QgsVectorLayer(self.uri.uri(), "temporary layer", "postgres")

        # print "DEBUG sqlAddMemoryLayer : pg_layer.geometryType() =" + str(pg_layer.geometryType())

        # memory layer to store features
        srs = pg_layer.crs()
        if pg_layer.geometryType() > 2:
            exc = SyntaxError()
            exc.text = u"No geometry type found for memory layer ! Unable to load unknown geometry type !"
            raise exc

        memory_layer = QgsVectorLayer(['Point', 'MultiLineString', 'MultiPolygon'][pg_layer.geometryType()] +
                                      "?crs=" + srs.authid(),
                                      layer_name, "memory")

        # provider used to create fields of memory layer
        provider = memory_layer.dataProvider()
        # add fields to memory layer
        memory_layer.startEditing()
        provider.addAttributes(pg_layer.dataProvider().fields().toList())
        memory_layer.updateFields()

        # Export features from pg_layer to memory_layer
        features = pg_layer.getFeatures()
        for feat in features:
            memory_layer.addFeature(feat)

        # validate
        result_commit = memory_layer.commitChanges()
        memory_layer.updateExtents()

        # print "DEBUG sqlAddMemoryLayer : memory_layer commit = " + str(result_commit)

        # add to legend
        return addLayer(memory_layer)


# transform sql so it can be loader as a layer data source
def makeSqlValidForLayer(sql):
    # remove utf8 header character :
    sql = sql.replace(unichr(65279), '')
    # remove new line characters
    sql = sql.replace(chr(13), ' ').replace(chr(10), ' ').replace('\t', ' ')
    # remove ; and blanck at the end of sql
    sql = sql.strip(' ;')

    #print sql

    # error if forbiden caracter %
    if '%' in sql:
        exc = SyntaxError()
        exc.text = u"% is not allowed in SQL QGIS layer : please use mod function instead"
        raise exc

    return sql

def addLayer(layer):

    # Existing layer ?
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layer.name())
    if (len(layerList)>0):
        QgsMapLayerRegistry.instance().removeMapLayer(layerList[0].id())

    # add layer to registry and affect same layer variable to the result,
    # to be sure it had been correctly added (None result if not)
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer, True)

    return layer