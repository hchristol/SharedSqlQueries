# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SharedSqlQueries
                                 A QGIS plugin
 This plugin allows to share SQL customised queries (with keywords) written by a db manager and that can be used in a friendly interface by QGIS end users.
                              -------------------
        begin                : 2016-01-07
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Ville de Clermont-Ferrand
        email                : hchristol@ville-clermont-ferrand.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import glob
import os.path

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStandardItem, QIcon, QAction, QComboBox, QSizePolicy, \
    QStandardItemModel, QTreeView, QPushButton, QHBoxLayout, QDialog

from qgis.gui import QgsMessageBar

# Initialize Qt resources from file resources.py
import resources

from config import JsonFile

import translate
from customSqlQuery import CustomSqlQuery
from dbrequest import Connection
from dbrequest import makeSqlValidForLayer
from query_param import QueryParamDialog


# Import the code for the DockWidget
from shared_sqlqueries_dockwidget import SharedSqlQueriesDockWidget



class SharedSqlQueries:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale UNUSED
        # locale = QSettings().value('locale/userLocale')[0:2]
        # locale_path = os.path.join(
        #     self.plugin_dir,
        #     'i18n',
        #     'SharedSqlQueries_{}.qm'.format(locale))
        #
        # if os.path.exists(locale_path):
        #     self.translator = QTranslator()
        #     self.translator.load(locale_path)
        #
        #     if qVersion() > '4.3.3':
        #         QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Shared SQL Queries')

        self.toolbar = self.iface.addToolBar(u'SharedSqlQueries')
        self.toolbar.setObjectName(u'SharedSqlQueries')

        #print "** INITIALIZING SharedSqlQueries"

        #self.dockwidget = None

        #combo of queries files
        self.comboxQueries = None

        #config file (in plugin directory) :
        self.config = JsonFile()
        self.queriesFolder = self.config.value("queries_folder")

        #database
        self.dbrequest = Connection(self.config.value("bdpostgis"))

        self.selectedQueryPath = None

        self.pluginIsActive = False


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        #return QCoreApplication.translate('SharedSqlQueries', message)

        return translate.tr(message) #simplier


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SharedSqlQueries/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Shared SQL Queries'),
            callback=self.run,
            parent=self.iface.mainWindow())

        #combo of queries files
        self.comboxQueries = QComboBox()
        self.comboxQueries.setMinimumHeight(27)
        self.comboxQueries.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # its model :
        self.queriesModel = QStandardItemModel()
        self.comboxQueries.setModel(self.queriesModel)

        # and its view (treeview) :
        self.queriesView = QTreeView()
        self.queriesView.setHeaderHidden(True)
        self.queriesView.setMinimumHeight(300)
        setWidgetWidth(self.comboxQueries, 0, 0) #no visible
        self.comboxQueries.setView(self.queriesView)

        # capture last clicked query
        self.queriesView.activated.connect(self.querySelected)
        self.queriesView.pressed.connect(self.querySelected)




        self.toolbar.addWidget(self.comboxQueries)

        #Run query button
        self.buttonRunQuery = QPushButton(self.tr("Open"))
        setWidgetWidth(self.buttonRunQuery, 0, 0) #no visible
        self.buttonRunQuery.clicked.connect(self.runQuery)

        self.toolbar.addWidget(self.buttonRunQuery)





    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING SharedSqlQueries"

        # disconnects
        #self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD SharedSqlQueries"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'Shared SQL Queries'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #first init

            #print "** STARTING SharedSqlQueries"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            #if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
            #    self.dockwidget = SharedSqlQueriesDockWidget()

            # connect to provide cleanup on closing of dockwidget
            #self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            #self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockwidget)
            #self.dockwidget.show()

        #Togle visibility of toolbar options (set width coz visible is not usable in toolbar)
        show_options = (self.comboxQueries.minimumWidth() == 0)
        if show_options:
            self.updateComboQueries()
            setWidgetWidth(self.comboxQueries, 300, 300)
            setWidgetWidth(self.buttonRunQuery, 0, 120)
        else:
            setWidgetWidth(self.comboxQueries, 0, 0)
            setWidgetWidth(self.buttonRunQuery, 0, 0)


    #display an error
    def errorMessage(self, message):
        self.iface.messageBar().pushMessage(self.tr(u"Error"), message, level=QgsMessageBar.CRITICAL)

    #read file in query folder and show them in combo tree view
    def updateComboQueries(self):
        self.queriesModel.clear()
        self.queriesModel.setHorizontalHeaderLabels(['Files'])

        item = QStandardItem(self.tr(u"Query File"))
        item.setSelectable(False)
        self.queriesModel.appendRow(item)

        # read directories with sql files
        for path, dirs, files in os.walk(self.queriesFolder):
            for rep in dirs:
                item = QStandardItem(rep)
                item.setData(rep, Qt.UserRole)
                item.setSelectable(False)
                self.queriesModel.appendRow(item)
                # in each directory, look for sql files
                for nomfich in glob.glob(self.queriesFolder + "/" + rep + "/*.sql"):
                    fileName, fileExtension = os.path.splitext(os.path.basename(nomfich))

                    # one item found
                    subitem = QStandardItem(fileName)
                    subitem.setData(nomfich, Qt.UserRole)

                    item.appendRow(subitem)



    #last selected query
    def querySelected(self, index):
        item = self.queriesModel.itemFromIndex(index)
        self.selectedQueryPath = item.data(Qt.UserRole)

    #run selected query
    def runQuery(self):
        #print self.comboxQueries.currentText()
        #print self.selectedQueryPath

        try:
            query = CustomSqlQuery(self.selectedQueryPath)
        except UnicodeDecodeError:
            self.errorMessage(self.tr(u"Query File is not UTF8 encoded ! Please convert it to UTF8 !"))
            return
        except SyntaxError as e:
            self.errorMessage(e.text)
            return
        except Exception as e:
            self.errorMessage(str(e))
            return

        # open param dialog
        dialog = QueryParamDialog(self.iface, self.dbrequest, query, self.toolbar)
        if dialog.exec_() == QDialog.Accepted:

            # format query as a Qgis readable sql source
            sql = query.updateFinalSql()

            # add the corresponding layer
            try:

                # save query in a memory layer
                if query.headerValue("layer storage") == "memory":
                    layer = self.dbrequest.sqlAddMemoryLayer(sql, query.headerValue("layer name"), query.headerValue("gid"), query.headerValue("geom"))

                # save query directly as a sql layer
                elif query.headerValue("layer storage") == "source":
                    layer = self.dbrequest.sqlAddLayer(sql, query.headerValue("layer name"), query.headerValue("gid"), query.headerValue("geom"))

                # save query in a file layer
                else:
                    type = query.headerValue("layer storage").lower()
                    driver = None
                    if type == "geojson":
                        driver = "GeoJSON"
                    if type == "shp":
                        driver = "ESRI Shapefile"

                    if driver is None:
                        self.errorMessage(self.tr(u"Unknown file type : ") + str(type))
                        return

                    directory = query.headerValue("layer directory")
                    if directory is None:
                        self.errorMessage(self.tr(u"No layer directory parameter found in query !"))
                        return
                    name = query.headerValue("layer name")

                    # new layer name and file name if file already exists
                    filepath = directory + "/" + name + "." + type
                    filecount = 1
                    new_name = name
                    while os.path.exists(filepath):
                        # file already exists
                        filecount += 1
                        new_name = name + "_" + str(filecount)
                        filepath = directory + "/" + new_name + "." + type
                    name = new_name

                    # add new layer
                    layer = self.dbrequest.sqlAddFileLayer(sql, driver, filepath, name,
                                    query.headerValue("gid"), query.headerValue("geom"))



            except SyntaxError as e:
                # sql is correct but does not fit QGIS requirement (like '%' char)
                self.errorMessage(self.tr(e.text))
                return

            if layer is None:
                self.errorMessage(self.tr(u"Unable to add a layer corresponding to this query !") + sql)
                # sql which is used in layer query
                print makeSqlValidForLayer(sql)
                return

            # if there's a qml style file corresponding to the query, apply it to the newly added layer
            if os.path.exists(query.styleFilePath()):
                layer.loadNamedStyle(query.styleFilePath())


# change width of widget to make it visible (or not)  in toolbar
def setWidgetWidth(widget, minwidth, maxwidth):
    widget.setMinimumWidth(minwidth)
    widget.setMaximumWidth(maxwidth)
