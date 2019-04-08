# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SharedSqlQueriesDockWidget
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
from __future__ import absolute_import

import os

from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QDockWidget

from . import translate

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'shared_sqlqueries_dockwidget_base.ui'))

#TODO : deprecated, to be deleted
class SharedSqlQueriesDockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(SharedSqlQueriesDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        #translate widget
        self.setWindowTitle(translate.tr(self.windowTitle()))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

