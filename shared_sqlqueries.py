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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object

import glob
import os.path

from qgis.PyQt import uic

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItem, QIcon, QAction, QComboBox, QSizePolicy, \
    QStandardItemModel, QTreeView, QPushButton, QHBoxLayout, QDialog, QApplication

from qgis.gui import QgsMessageBar
from qgis.core import QgsMessageLog

# Initialize Qt resources from file resources.py
from . import resources

from .config import JsonFile
from shutil import copyfile

from . import translate
from .customSqlQuery import CustomSqlQuery
from .dbrequest import Connection
from .dbrequest import makeSqlValidForLayer
from .query_param import QueryParamDialog


# Import the code for the DockWidget
from .shared_sqlqueries_dockwidget import SharedSqlQueriesDockWidget



class SharedSqlQueries(object):
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

        self.config = None
        self.queriesFolder = None
        self.dbrequest = None

        self.selectedQueryPath = None

        self.pluginIsActive = False

    # init related to config file. Return False if no config.json has been found
    def init_config(self):

        #just once
        if self.config is not None:
            return True

        #config file (in plugin directory) :
        configpath = os.path.dirname(__file__) + '/config.json'
        try:
            self.config = JsonFile(configpath)
        except IOError:
            # copy default config json if it does not exist
            self.errorMessage(self.tr(
                u"No config.json file found ! A default one is created but you have to edit it (in your plugin directory)"))
            configpath_default = os.path.dirname(__file__) + '/config_default.json'
            copyfile(configpath_default, configpath)
            return False

        self.queriesFolder = self.config.value("queries_folder")

        #database
        self.dbrequest = Connection(self.config.value("bdpostgis"))

        return True


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

        # look for config file (required at the first run)
        if not self.init_config():
            # invalid config file
            return

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
        self.iface.messageBar().pushMessage(self.tr(u"Error"), message, level=Qgis.Critical)

    #display an error
    def infoMessage(self, message):
        self.iface.messageBar().pushMessage(self.tr(u"Info"), message, level=Qgis.Info)

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

        # Open query file
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


        # dialog parameter of query accepted
        def DialogAccepted():

            if dialog.errorMessage != "":
                self.errorMessage(dialog.errorMessage)
                return

            # format query as a Qgis readable sql source
            sql = query.updateFinalSql()

            QgsMessageLog.logMessage(sql, "SharedSql", QgsMessageLog.INFO)

            # type of request :
            firstword = "" # first word of request : select, update, insert, delete
            i = 1000

            for word in ["select", "update", "insert", "delete"]:
                i2 = sql.lower().find(word)
                if i2 > 0 and i2 < i: # pick the first signifiant word
                    firstword = word
                    i = i2

            if firstword == "" :
                self.errorMessage("Unrecognized query, please use only select, update, insert or delete query")
                return

            if firstword == "select":
                # add the corresponding layer
                try:

                    # wait cursor
                    QApplication.setOverrideCursor(Qt.WaitCursor)

                    # add new layer if required :
                    if 'layer' in query.headerValue("result as"):

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
                                QApplication.setOverrideCursor(Qt.ArrowCursor)
                                self.errorMessage(self.tr(u"Unknown file type : ") + str(type))
                                return

                            directory = query.headerValue("layer directory")
                            if directory is None:
                                QApplication.setOverrideCursor(Qt.ArrowCursor)
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


                            layer = self.dbrequest.sqlAddFileLayer(sql, driver, filepath, name,
                                            query.headerValue("gid"), query.headerValue("geom"))


                        if layer is None:
                            QApplication.setOverrideCursor(Qt.ArrowCursor)
                            self.errorMessage(self.tr(u"Unable to add a layer corresponding to this query !") + sql)
                            # sql which is used in layer query
                            print(makeSqlValidForLayer(sql))
                            return

                        # if there's a qml style file corresponding to the query, apply it to the newly added layer
                        if os.path.exists(query.styleFilePath()):
                            layer.loadNamedStyle(query.styleFilePath())



                    # optional list widget viewer for results :
                    if 'list' in query.headerValue("result as"):
                        savedirectory = query.headerValue("layer directory")
                        if savedirectory is None:
                            savedirectory = ""
                        # open a list data
                        self.openListDialog(sql,
                                # default path
                                (savedirectory  + "/" + query.headerValue("layer name") + ".xls").replace(" ", "_"))

                    QApplication.setOverrideCursor(Qt.ArrowCursor)

                except SyntaxError as e:
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
                    # sql is correct but does not fit QGIS requirement (like '%' char)
                    self.errorMessage(self.tr(e.text))
                    return




            if firstword == "update" or firstword == "insert" or firstword == "delete":
                try:
                    self.dbrequest.sqlExec(sql)
                    self.infoMessage(self.tr(u"Request performed"))

                except SyntaxError as e:
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
                    # sql is correct but does not fit QGIS requirement (like '%' char)
                    self.errorMessage(self.tr(e.text))
                    return

            # once validated, clear rubber for edited geom
            dialog.mRb.reset()


        # open parameter dialog
        dialog = QueryParamDialog(self.iface, self.dbrequest, query, self.toolbar)
        dialog.buttonBox.accepted.connect(DialogAccepted)
        dialog.setModal(False)
        dialog.show()


    # Open the optional dialog which displays a list widget of data and allow xls export
    def openListDialog(self, sql, filepath):

        # clean ascii file
        # and  (remove blank spaces which cause failure while opening file)
        filepath = remove_accent(filepath).replace(" ", "_")

        dresult = listDialog(None)
        dresult.setWindowTitle(translate.tr(u"Result"))
        dresult.label_outputfile.setText(translate.tr(u"Output file :"))
        dresult.pushButton_open_file.setText(translate.tr(u"Open"))
        dresult.line_edit_file.setText(filepath)
        model = None

        from .tools import export
        QApplication.setOverrideCursor(Qt.WaitCursor)
        [header, data, rowCount] = self.dbrequest.sqlExec(sql)
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        if rowCount > 0:
            model = export.fillMultiColumnListWithData(dresult.list_queryresult, data, header)

        def open_file():
            finalfilepath = remove_accent(dresult.line_edit_file.text()).replace(" ", "_")
            if model is not None:
                export.exportQModeleToXls(finalfilepath, translate.tr(u"Result"), model, True)

        dresult.setModal(True)
        dresult.pushButton_open_file.clicked.connect(open_file)
        dresult.exec_() # show does not work :-(






# change width of widget to make it visible (or not)  in toolbar
def setWidgetWidth(widget, minwidth, maxwidth):
    widget.setMinimumWidth(minwidth)
    widget.setMaximumWidth(maxwidth)

def remove_accent(text):
    if type(text) is str:
        import unicodedata
        return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
    return text # str type


# ressource dialog
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'list_dialog.ui'))


# dialog list showing result array
class listDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(listDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        # initialisation de la boite de dialogue


    def showEvent(self, evnt):
        super(listDialog, self).showEvent(evnt)