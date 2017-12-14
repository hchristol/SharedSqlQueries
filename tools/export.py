# -*- coding: utf-8 -*-

# to export result of a query into listbox or xls file

import os
import PyQt4.Qt as qt 
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtXml
from win32com.client import Dispatch
from qgis.core import *
import xlwt
import datetime

# Fill a listbox with data from an sql query
#         headerStringArray :         ["Identifiant", "Support", "Marque", "Modele", "Puissance"], \
#         Optional  headerWidths :             [70, 100, 100, 100, 60] )
def fillMultiColumnListWithData(list, data, headerStringArray, headerWidths=None, dateFormat="%Y-%m-%d"):
    model = QtGui.QStandardItemModel()
    model.clear()
    model.setHorizontalHeaderLabels(headerStringArray) #noms des colonnes

    # add lines to model
    for line in data:
        values=[]
        iColonne=0
        for cell in line:
            if (iColonne<len(headerStringArray)): # do not fill list beyond header length
                # cas particulier des dates
                if isinstance(cell, datetime.date):
                    item = QtGui.QStandardItem(cell.strftime("%d-%m-%Y"))
                    item.setData(cell)
                else :
                    item=QtGui.QStandardItem(unicode(cell))
                item.setData(line, Qt.UserRole) # underlying data stored in item
                values.append(item)
                iColonne+=1
        model.appendRow(values)

    list.setModel(model)

    if headerWidths is not None:
        for i in range(0,len(headerWidths)): # columns witdh
            list.setColumnWidth(i, headerWidths[i])

    list.show()

    return model #return selected model


# Export listbox model to xls
def exportQModeleToXls(filename, titre, model, openfile = False):
    book = xlwt.Workbook()
    sh = book.add_sheet(titre)

    # write Header
    for col in range(model.columnCount()):
        nom_colonne =  model.horizontalHeaderItem(col).text()
        sh.write(0, col, nom_colonne)

    # write Data
    for row in range(model.rowCount()):
        for col in range(model.columnCount()):
            #value = modele.index( row, col, QModelIndex()).data( Qt.DisplayRole ) #.toString()
            item = model.item(row, col)
            value = ""
            if item.isCheckable():
                state = ['UNCHECKED', 'TRISTATE',  'CHECKED'][item.checkState()]
                if state =='CHECKED':value ="True"
                else:value ="False"
            else:
                # if item.text() == "":
                #     data = item.data(Qt.UserRole)
                #    if data != "": value = data
                # else:
                value = item.text()
            try:
                sh.write(row + 1, col, unicode(value))
            except Exception as e:
                print u"ERROR line " + str(row) + " : " + e.message + u"   problem here : " + unicode(value)
    try:
        # Ecriture du fichier
        book.save(filename)
    except BaseException as e:
        # Error
        return [False, None]
    
    if openfile:
        try:
            # import os
            import subprocess
            # os.system(filename)
            subprocess.call(filename, shell=True)
        except BaseException:
            raise IOError(u"File Error : unable to open " + filename)

    return [True, book]

