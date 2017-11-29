"""
/***************************************************************************
 tools
                                 A QGIS plugin
                                 
 Outils (maptools)
  
                              -------------------
        begin                : 2014-09-02
        copyright            : (C) 2014 by JLebouvier
        email                : jlebouvier@ville-clermont-ferrand.fr
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

import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class CreatePointTool(QgsMapTool):
    
    def __init__(self, canvas, deltaAngle = -90):
        QgsMapTool.__init__(self, canvas)
        self.mCanvas = canvas
        self.mLayer = None
        self.mRb = None
        self.mColor = QColor(255, 50, 50, 100)
        self.mWidth = 5
        self.cursor = QCursor(QPixmap(["17 17 3 1",
                                      "      c None",
                                      ".     c None",
                                      "+     c #000000",
                                      "                 ",
                                      "        +        ",
                                      "      +++++      ",
                                      "     +  +  +     ",
                                      "    +   +   +    ",
                                      "   +    +    +   ",
                                      "  +     +     +  ",
                                      " ++     +     ++ ",
                                      " ++++++++++++++++",
                                      " ++     +     ++ ",
                                      "  +     +     +  ",
                                      "   +    +    +   ",
                                      "   ++   +   +    ",
                                      "    ++  +  +     ",
                                      "      +++++      ",
                                      "       +++       ",
                                      "        +        "]))



    def canvasPressEvent(self, event):
        if self.mRb:
            self.mRb.reset(True)

    def canvasMoveEvent(self,event):
        if not self.mRb:
            self.mRb = QgsRubberBand(self.mCanvas, True)
            self.mRb.setColor(self.mColor)
            self.mRb.setWidth(self.mWidth)   
                 
        self.mRb.reset(True)
        x = event.pos().x()
        y = event.pos().y()        
        pos = self.mCanvas.getCoordinateTransform().toMapCoordinates(x, y)

        newGeom = QgsGeometry().fromPoint (pos)
        # Affectation de la géométrie au rubber
        self.mRb.setToGeometry( newGeom, None )  

        
    def canvasReleaseEvent(self,event):

        # Récupération des informations       
        x = event.pos().x()
        y = event.pos().y()        
        pos = self.mCanvas.getCoordinateTransform().toMapCoordinates(x, y)


        newGeom = QgsGeometry().fromPoint(pos)
        self.mRb.reset(True)
        self.mRb.setToGeometry(newGeom, None)

        #HC emet feature crée avant sa validation pour pouvoir renseigner attributs par défaut, notamment l'identifiant
        self.emit(SIGNAL("evInit(QgsGeometry*)"), newGeom )

    
    def activate(self):
        self.mCanvas.setCursor(self.cursor)
        # modif HC Aout 2015 : désactive le passage en mode edition
        # self.mLayer.startEditing()
  
    def deactivate(self):
        if self.mRb:
            self.mRb.reset(True)
            self.mRb = None
        if self != None:
            self.emit(SIGNAL("evDeactivated(PyQt_PyObject)"), self)

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return False 
    

