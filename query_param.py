import os
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QDialog, QLabel, QLineEdit

from customSqlQuery import CustomSqlQuery
from translate import tr

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'query_param.ui'))

# dialog to edit query parameters
class QueryParamDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, dbrequest, query, parent=None):

        """Constructor."""
        super(QueryParamDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface
        self.dbrequest = dbrequest
        self.query = query

        #translate widget
        self.setWindowTitle(tr(self.windowTitle()))

        # index of widget by param name
        self.widgetParam = None

        self.buttonBox.accepted.connect(self.DialogToParametersUpdate)

    # update parameters of query
    def DialogToParametersUpdate(self):

        # update all parameters from dialog widget
        for header_or_param in {"header", "param"}:

            listParam = self.query.param
            if header_or_param == "header":
                listParam = self.query.header

            for paramName in self.widgetParam[header_or_param].keys():

                widget = self.widgetParam[header_or_param][paramName]
                param = listParam[paramName]

                # update text param
                param["value"] = widget.text()


    # initialisation de la boite de dialogue
    def showEvent(self, evnt):
        super(QueryParamDialog, self).showEvent(evnt)

        query = self.query
        self.labelQueryName.setText(query.name)

        #index for param, header param separated from other param
        self.widgetParam = {"header": {}, "param": {}}

        # show header parameters of query
        header = self.query.header
        if header is not None:
            for paramName in header.keys():
                value = header[paramName]
                # add param to dialog and index its widget
                self.widgetParam["header"][paramName] = self.addParam(tr(paramName), value)

        # show other sql parameters
        param = self.query.param
        if param is not None:
            for paramName in param.keys():
                value = param[paramName]
                # add param to dialog and index its widget
                self.widgetParam["param"][paramName] = self.addParam(paramName, value)


        #adjust dialog size
        self.setFixedHeight(40 + self.gridLayoutHeader.rowCount() * 25)

    #add a param in dialog
    def addParam(self, paramName, value):
        grid = self.gridLayoutHeader

        row_number = grid.rowCount()
        # name
        grid.addWidget(QLabel(paramName), row_number, 0)

        # value
        if "value" in value:
            value = value["value"]
        else:
            value = value["default"]

        # value : string
        edit_widget = QLineEdit()
        edit_widget.setText(value)
        grid.addWidget(edit_widget, row_number, 1)
        return edit_widget
