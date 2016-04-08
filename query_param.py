import os
from PyQt4.uic import loadUiType
from PyQt4.QtGui import QDialog, QLabel, QLineEdit, QDateEdit, QComboBox

from customSqlQuery import CustomSqlQuery
from translate import tr

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'query_param.ui'))

# header param that should not be shown to user
HIDDEN_HEADER_VALUE = {'gid', 'geom', 'layer storage'}

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

    # dialog init
    def showEvent(self, evnt):
        super(QueryParamDialog, self).showEvent(evnt)
        self.ParametersToDialogUpdate()

    # add widgets to the dialog that are related to each editable parameter
    def ParametersToDialogUpdate(self):
        query = self.query
        self.labelQueryName.setText(query.name)

        # index for param, header param separated from other param
        self.widgetParam = {"header": {}, "param": {}}

        for header_or_param in {"header", "param"}:

            listParam = self.query.param
            if header_or_param == "header":
                listParam = self.query.header

            def sort_param(key):
                return listParam[key]["order"]

            for paramName in sorted(listParam, key=sort_param): # in listParam:

                # ignore hidden header parameters
                if header_or_param == "header":
                    if paramName in HIDDEN_HEADER_VALUE:
                        continue

                value = listParam[paramName]
                # add param to dialog and index its widget
                self.widgetParam[header_or_param][paramName] = self.addParam(tr(paramName), value)

        # adjust dialog size
        self.setFixedHeight(40 + self.gridLayoutHeader.rowCount() * 25)

    # add a param in dialog
    def addParam(self, paramName, value):
        grid = self.gridLayoutHeader

        row_number = grid.rowCount()

        # type of parameter
        [type_widget, type_options, name] = splitParamNameAndType(paramName)

        # name
        grid.addWidget(QLabel(name), row_number, 0)

        # value
        if "value" in value:
            value = value["value"]
        else:
            value = value["default"]

        # update widget

        if type_widget == "text":
            edit_widget = QLineEdit()
            edit_widget.setText(value)

        elif type_widget == "date":
            edit_widget = QDateEdit()
            edit_widget.setCalendarPopup(True)
            edit_widget.lineEdit().setText(value)

        elif type_widget == "select":
            edit_widget = QComboBox()
            edit_widget.setEditable(True)
            self.dbrequest.sqlFillQtWidget(type_options, edit_widget)
            edit_widget.setEditText(value)

        grid.addWidget(edit_widget, row_number, 1)
        return edit_widget

    # update parameters of query
    def DialogToParametersUpdate(self):

        # update all parameters from dialog widget
        for header_or_param in {"header", "param"}:

            listParam = self.query.param
            if header_or_param == "header":
                listParam = self.query.header

            for paramName in self.widgetParam[header_or_param].keys():

                # widget linked to this parameter
                widget = self.widgetParam[header_or_param][paramName]
                param = listParam[paramName]

                [type_widget, type_options, name] = splitParamNameAndType(paramName)

                # update value param

                if type_widget == "text":
                    param["value"] = widget.text()

                elif type_widget == "date":
                    param["value"] = widget.lineEdit().text()

                elif type_widget == "select":
                    param["value"] = widget.currentText()


# return the type of parameter
def splitParamNameAndType(paramName):
    # default values
    type_widget = "text"
    type_options = ""
    name = paramName

    for possible_type in ["text", "date", "select"]:
        searched = possible_type + " "
        i = paramName.strip().find(searched)
        if i == 0:
            type_widget = possible_type

            # type options
            if possible_type == "select":
                i_end_select = paramName.strip().find(";")
                type_options = paramName.strip()[:i_end_select]
                searched = type_options + ";"

            name = paramName.strip()[len(searched):].strip()

            return [type_widget, type_options, name]

    return [type_widget, type_options, name]
