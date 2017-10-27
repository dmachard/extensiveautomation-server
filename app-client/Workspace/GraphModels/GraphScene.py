#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
# This file is part of the extensive testing project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

"""
Graph scene for test abstract
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QGraphicsRectItem, QGraphicsLineItem, QPolygonF, QGraphicsItem, 
                            QPen, QColor, QBrush, QPainterPathStroker, QGraphicsPolygonItem, 
                            QPainterPath, QMessageBox, QDialog, QGraphicsScene, QFont, QWidget, 
                            QToolBar, QGraphicsView, QPainter, QToolButton, QIcon, QButtonGroup, 
                            QComboBox, QLabel, QVBoxLayout, QApplication, QMenu, QGroupBox, QHBoxLayout,
                            QClipboard, QFrame)
    from PyQt4.QtCore import (Qt, QRectF, QLineF, QPointF, pyqtSignal, QSize, QPoint, 
                                QMimeData, QByteArray, QSizeF, )
except ImportError:
    from PyQt5.QtGui import (QPolygonF, QPen, QColor, QBrush, QPainterPathStroker, 
                            QPainterPath, QFont, QPainter, QIcon, QClipboard)
    from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsLineItem, QGraphicsItem, 
                                QGraphicsPolygonItem, QMessageBox, QDialog, QGraphicsScene, QFrame,
                                QWidget, QToolBar, QGraphicsView, QToolButton, QButtonGroup,
                                QComboBox, QLabel, QVBoxLayout, QApplication, QMenu, QGroupBox, QHBoxLayout)
    from PyQt5.QtCore import (Qt, QRectF, QLineF, QPointF, pyqtSignal, QSize, QPoint, 
                                QMimeData, QByteArray, QSizeF)
                                
from Libs import QtHelper, Logger
import Settings

try:
    import GenericConfigDialog
except ImportError: # python3 support
    from . import GenericConfigDialog

# import standard libraries
import math
import re
try:
    import pickle
except ImportError: # support python3
    import cPickle as pickle
    
BLOCK_START = 0
BLOCK_END = 1
BLOCK_STEP = 2
BLOCK_CONDITIONAL = 3
BLOCK_ACTION = 4

FUNCTION_ADD_STEP           = "addStep"
FUNCTION_ADD_BREAKPOINT     = "BreakPoint"

ACTION_BREAKPOINT           = "TestCase >> BreakPoint"
ACTION_STEP                 = "Step"
ACTION_TESTCASE             = "TestCase"
ACTION_ADAPTER              = "Adapter"
ACTION_LIBRARY              = "Library"
ACTION_TEMPLATE             = "Template"
ACTION_VALIDATOR            = "Validator"
ACTION_MANIPULATOR          = "Manipulator"
ACTION_LABEL                = "Label"
ACTION_DO                   = "Do"
ACTION_CACHE                = "Cache"
ACTION_TIME                 = "Time"
ACTION_PRIVATE              = "Private"
ACTION_PUBLIC               = "Public"
ACTION_INTERACT             = "Interact"
ACTION_TRACE                = "Trace"

COLOR_LABEL                 = "#FFC000"
COLOR_TESTCASE              = "#FFE599"
COLOR_STEP                  = "#C5E0B3"
COLOR_ADAPTER               = "#7CAFDD"
COLOR_LIBRARY               = "#33D2C5"
COLOR_TEMPLATE              = "#B4908B"
COLOR_CONDITION             = "#F7CAAC"
COLOR_STARTEND              = "#DBDBDB"
COLOR_ARROW                 = "#C1D9EF"
COLOR_MANIPULATOR           = "#D8F5D4"
COLOR_VALIDATOR             = "#D8F5D4"
COLOR_DO                    = "#DEEAF6"
COLOR_CACHE                 = "#688B8C"
COLOR_TIME                  = "#688B8C"
COLOR_PRIVATE               = "#688B8C"
COLOR_PUBLIC                = "#688B8C"
COLOR_INTERACT              = "#688B8C"
COLOR_TRACE                 = "#688B8C"

ACTION_PASS                 = "PASS"
ACTION_CONDITION_IF         = "IF"
ACTION_CONDITION_THEN       = "THEN"
ACTION_CONDITION_ELSE       = "ELSE"
ACTION_CONDITION_ENDIF      = "END IF"

GRAPHIC_SCENE_SIZE = 4000

class Hotspots(QGraphicsRectItem, Logger.ClassLogger):
    """
    Hotspots class
    """
    def __init__(self, x, y, parent=None, scene=None, id = 0):
        """
        Constructor
        """
        if QtHelper.IS_QT5:
            super(Hotspots, self).__init__(x-2, y-2, 4, 4, parent)
        else:
            super(Hotspots, self).__init__(x-2, y-2, 4, 4, parent, scene)
        self.id = id
        self.isConnected = False
        self.setOpacity(0.01)
        
    def setConnected(self):
        """
        Connected flag
        """
        self.isConnected = True
        
    def setDisconnected(self):
        """
        Disconnected flag
        """
        self.isConnected = False 
        
class Arrow(QGraphicsLineItem, Logger.ClassLogger):
    """
    The Arrow class is a graphics item that connects two DiagramItems. 
    It draws an arrow head to one of the items. To achieve this the item needs 
    to paint itself and also re implement methods used by the graphics scene to 
    check for collisions and selections. The class inherits QGraphicsLine item, 
    and draws the arrowhead and moves with the items it connects.
    """
    def __init__(self, startItem, endItem, parent=None, scene=None, arrow_start_point = None, arrow_end_point = None, 
                        toHotspotId=None, fromHotspotId=None):
        """
        We set the start and end diagram items of the arrow. 
        The arrow head will be drawn where the line intersects the end item.
        """
        Logger.ClassLogger.__init__(self)
        if QtHelper.IS_QT5:
            super(Arrow, self).__init__(parent)
        else:
            super(Arrow, self).__init__(parent, scene)

        self.arrowHead = QPolygonF()

        # get hotspot directly on creation
        self.toHotspotId = toHotspotId
        self.fromHotspotId = fromHotspotId

        # save id on paint
        self.toHotspotID = 0
        self.fromHotspotID = 0

        self.myStartItem = startItem
        self.myEndItem = endItem

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        self.arrow_start_point = arrow_start_point
        self.arrow_end_point = arrow_end_point
        
        self.startingPoint = None
        self.endingPoint = None

        self.text = ""
    
    def setText(self, text):
        """
        Set text
        """
        self.text = text

    def setColor(self, color):
        """
        Set the color
        """
        self.myColor = color

    def startItem(self):
        """
        Return the start item
        """
        return self.myStartItem

    def endItem(self):
        """
        Return the end item
        """
        return self.myEndItem

    def boundingRect(self):
        """
        Boudin rect function
        """
        extra = (self.pen().width() + 40) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        """
        The shape function returns a QPainterPath that is the exact shape of the item. 
        The QGraphicsLineItem::shape() returns a path with a line drawn with the current pen, 
        so we only need to add the arrow head. 
        This function is used to check for collisions and selections with the mouse.
        """
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        """
        Update position
        """
        # This slot updates the arrow by setting the start and end points 
        # of its line to the center of the items it connects.
        line = QLineF( self.mapFromItem(self.myStartItem, 0, 0), 
                        self.mapFromItem(self.myEndItem, 0, 0) )
        self.setLine(line)
    
    def itemChange(self, change, value):
        """
        Item change
        """

        if change == QGraphicsItem.ItemSelectedChange:
            if self.startingPoint is not None and self.endingPoint is not None:
                if value == True:
                    self.startingPoint.setOpacity(1)
                    self.endingPoint.setOpacity(1)
                else:
                    self.startingPoint.setOpacity(0.01)
                    self.endingPoint.setOpacity(0.01)
    
        return value

        
    def paint(self, painter, option, widget=None):
        """
        Paint function

        If the start and end items collide we do not draw the arrow; 
        the algorithm we use to find the point the arrow should be drawn at may fail if the items collide.
        We first set the pen and brush we will use for drawing the arrow.
        """
        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 10.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_ARROW )
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # We then need to find the position at which to draw the arrowhead. The head should be drawn where 
        # the line and the end item intersects. This is done by taking the line between each point in the polygon 
        # and check if it intersects with the line of the arrow. Since the line start and end points are set to the 
        # center of the items the arrow line should intersect one and only one of the lines of the polygon. Note that 
        # the points in the polygon are relative to the local coordinate system of the item. We must therefore add the 
        # position of the end item to make the coordinates relative to the scene.
        if (self.startingPoint is None) or (self.endingPoint is None):
            p1 = myStartItem.pos()
            
            i = 0

            # compute best distance ?
            for hs in myStartItem.hs:
                if hs.isConnected: continue
                
                x = hs.mapRectToScene(hs.rect()).center().x()
                y = hs.mapRectToScene(hs.rect()).center().y()
                if self.arrow_start_point is not None:
                    myeix=self.arrow_start_point.x()
                    myeiy=self.arrow_start_point.y()
                else:
                    myeix=myEndItem.pos().x()
                    myeiy=myEndItem.pos().y()
                

                distance1 = ((x-myeix)**2 + (y-myeiy)**2)
                distance2 =(((p1.x()-myeix)**2) + ((p1.y()-myeiy)**2))
                
                
                if (distance1 < distance2):
                    p1 = QPointF(x,y)
                    self.fromHotspotID = i
                    self.startingPoint = hs
                
                i += 1

     
            p2 = myEndItem.pos()
            
            i = 0

            # compute best distance ?
            for  hs2 in myEndItem.hs:
                if hs2.isConnected: continue
                
                x = hs2.mapRectToScene(hs2.rect()).center().x()
                y = hs2.mapRectToScene(hs2.rect()).center().y()
                
                if self.arrow_end_point is not None:
                    myeix=self.arrow_end_point.x()
                    myeiy=self.arrow_end_point.y()
                else:
                    myeix=p1.x()
                    myeiy=p1.y()
                
                distance1 = (x-myeix)**2 + (y-myeiy)**2
                distance2 = ((myeix-p2.x())**2) + ((myeiy-p2.y())**2)

                if ( distance1 < distance2):
                    p2 = QPointF(x,y)
                    self.toHotspotID = i
                    self.endingPoint = hs2
                i += 1

        else:
            self.startingPoint.setConnected()
            self.endingPoint.setConnected()
            x1 = self.startingPoint.mapRectToScene(self.startingPoint.rect()).center().x()
            y1 = self.startingPoint.mapRectToScene(self.startingPoint.rect()).center().y()
            x2 = self.endingPoint.mapRectToScene(self.endingPoint.rect()).center().x()
            y2 = self.endingPoint.mapRectToScene(self.endingPoint.rect()).center().y()
            p1 = QPointF(x1,y1)
            p2 = QPointF(x2,y2)
        
        if isinstance(p1, QPointF) and isinstance(p2, QPointF):
            self.setLine(QLineF(p2, p1))
        
        line = self.line()
        
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            return
        
        # We calculate the angle between the x-axis and the line of the arrow. We need to turn the arrow head to this angle 
        # so that it follows the direction of the arrow. If the angle is negative we must turn the direction of the arrow.
        # We can then calculate the three points of the arrow head polygon. One of the points is the end of the line, 
        # which now is the intersection between the arrow line and the end polygon. Then we clear the arrowHead polygon 
        # from the previous calculated arrow head and set these new points
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)
            
        # If the line is selected, we draw two dotted lines that are parallel with the line of the arrow. 
        # We do not use the default implementation, which uses boundingRect() because the QRect bounding rectangle 
        # is considerably larger than the line.
        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QPen(myColor, 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            myLine = QLineF(line)

            stroker = QPainterPathStroker()
            stroker.setWidth( 10 )

            stroke = stroker.createStroke( self.shape() )
            
            painter.drawPath( stroke.simplified() )

        # drawing text
        blackText = QColor(0,0,0)
        painter.setPen(blackText)
        painter.drawText(self.boundingRect(), Qt.AlignCenter|Qt.AlignVCenter, self.text)

class DiagramItem(QGraphicsPolygonItem):
    """
    Diagram item class
    """
    Action, Conditional, StartEnd, Step, Adapter, BreakPoint, Abort, Library, \
        Template, Manipulator, Validator, Label, Do, Cache, Time, Private, Public = range(17)
    def __init__(self, diagramType,  parentWidget=None, parent=None, scene=None ):
        """
        Constructor
        """
        if QtHelper.IS_QT5:
            super(DiagramItem, self).__init__(parent)
        else:
            super(DiagramItem, self).__init__(parent, scene)
        self.setAcceptHoverEvents(True)
        
        self.name = "name"
        self.inputs = []
        self.outputs = []

        self.hs = list()
        
        self.itemId = 0
        self.diagramType = diagramType
        self.parentWidget = parentWidget    
        self.itemMoved = False

        self.data = { 'item-data': '' }
        self.data['item-id'] = str(self.itemId)
        self.data['item-type'] = str(self.diagramType)
        self.data['item-text'] = ''
        self.data['item-links'] = []

        blockColor = "#000000"

        path = QPainterPath()
        if self.diagramType == self.StartEnd: # Circle
            self.maxInputs = 0
            self.maxOutputs = 1
            self.name = "Start"
            boundingRectangle = QRectF(-25,25,50,-50)
            path.addEllipse(boundingRectangle)
            self.myPolygon = path.toFillPolygon()
            
            # hotspot definition
            hspot = Hotspots(   (boundingRectangle.topLeft().x() + boundingRectangle.topRight().x())/2, 
                                (boundingRectangle.topLeft().y() + boundingRectangle.topRight().y())/2, 
                                self, scene, id = 0)
            self.hs.append(hspot)
            
            hspot = Hotspots(   (boundingRectangle.bottomRight().x() + boundingRectangle.topRight().x())/2, 
                                (boundingRectangle.bottomRight().y() + boundingRectangle.topRight().y())/2, 
                                self, scene, id = 1)
            self.hs.append(hspot)
            hspot = Hotspots(   (boundingRectangle.bottomLeft().x() + boundingRectangle.bottomRight().x())/2, 
                                (boundingRectangle.bottomLeft().y() + boundingRectangle.bottomRight().y())/2, 
                                self, scene, id = 2)
            self.hs.append(hspot)
            
            hspot = Hotspots(   (boundingRectangle.bottomLeft().x() + boundingRectangle.topLeft().x())/2, 
                                (boundingRectangle.bottomLeft().y() + boundingRectangle.topLeft().y())/2, 
                                self, scene, id = 3)
            self.hs.append(hspot)
            
        elif self.diagramType == self.Conditional: # diamond
            self.maxInputs = 1
            self.maxOutputs = 2
            self.name = "Condition"
            self.myPolygon = QPolygonF([
                    QPointF(-100, 0), QPointF(0, 50),
                    QPointF(100, 0), QPointF(0, -50),
                    QPointF(-100, 0)])
            
            # hotspot definition            
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(self.myPolygon.at(i).x(), self.myPolygon.at(i).y(), self, scene, id = i)
                self.hs.append(hspot)

        elif self.diagramType == self.Do: # diamond
            self.maxInputs = 1
            self.maxOutputs = 2
            self.name = "Do"
            self.myPolygon = QPolygonF([
                        QPointF(-100, -30), QPointF(100, -30),
                        QPointF(100, 30), QPointF(-100, 30),
                        QPointF(-100, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)
                         
        elif self.diagramType == self.Adapter: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Adapter"
            self.myPolygon = QPolygonF([
                        QPointF(-100, -30), QPointF(100, -30),
                        QPointF(100, 30), QPointF(-100, 30),
                        QPointF(-100, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2,
                                    self, scene, id = i)
                self.hs.append(hspot)
                
        elif self.diagramType == self.Library: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Library"
            self.myPolygon = QPolygonF([
                        QPointF(-100, -30), QPointF(100, -30),
                        QPointF(100, 30), QPointF(-100, 30),
                        QPointF(-100, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i)
                self.hs.append(hspot)
                
        elif self.diagramType == self.Template: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Template"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)

        elif self.diagramType == self.Manipulator: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Manipulator"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)

        elif self.diagramType == self.Validator: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Validator"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)
                
        elif self.diagramType == self.Cache: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Cache"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)
                
        elif self.diagramType == self.Time: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Time"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)
                
        elif self.diagramType == self.Private: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Private"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)
                
        elif self.diagramType == self.Public: # rectangle
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Public"
            self.myPolygon = QPolygonF([
                        QPointF(-90, -30), QPointF(90, -30),
                        QPointF(90, 30), QPointF(-90, 30),
                        QPointF(-90, -30)]
                    )
            # hotspot definition   
            for i in range(self.myPolygon.size()-1):
                hspot = Hotspots(   (self.myPolygon.at(i).x() + self.myPolygon.at(i+1).x())/2, 
                                    (self.myPolygon.at(i).y() + self.myPolygon.at(i+1).y())/2, 
                                    self, scene, id = i )
                self.hs.append(hspot)
                 
        elif self.diagramType == self.Action: # Trapeze
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Action"
               
            boundingRectangle = QRectF(-70,40,140,-50)
            path.addRoundedRect(boundingRectangle,10,10)
            self.myPolygon = path.toFillPolygon()
            hspot = Hotspots(   (boundingRectangle.topLeft().x() + boundingRectangle.topRight().x())/2, 
                                (boundingRectangle.topLeft().y() + boundingRectangle.topRight().y())/2, 
                                self, scene, id = 0)
            self.hs.append(hspot)
            
            hspot = Hotspots(   (boundingRectangle.bottomRight().x() + boundingRectangle.topRight().x())/2, 
                                (boundingRectangle.bottomRight().y() + boundingRectangle.topRight().y())/2, 
                                self, scene, id = 1)
            self.hs.append(hspot)
            hspot = Hotspots(   (boundingRectangle.bottomLeft().x() + boundingRectangle.bottomRight().x())/2, 
                                (boundingRectangle.bottomLeft().y() + boundingRectangle.bottomRight().y())/2, 
                                self, scene, id = 2)
            self.hs.append(hspot)
            
            hspot = Hotspots(   (boundingRectangle.bottomLeft().x() + boundingRectangle.topLeft().x())/2, 
                                (boundingRectangle.bottomLeft().y() + boundingRectangle.topLeft().y())/2, 
                                self, scene, id = 3)
            self.hs.append(hspot)

        elif self.diagramType == self.Label: # Trapeze
            self.maxInputs = 0
            self.maxOutputs = 0
            self.name = "Label"
               
            boundingRectangle = QRectF(-70,40,140,-50)
            path.addRoundedRect(boundingRectangle,10,10)
            self.myPolygon = path.toFillPolygon()

        else:
            #Ellipse
            self.maxInputs = 1
            self.maxOutputs = 1
            self.name = "Step"

            boundingRectangle = QRectF(-50,25,100,-50)
            path.addEllipse(boundingRectangle)
            self.myPolygon = path.toFillPolygon()
            # hotspot definition   
            hspot = Hotspots(   (boundingRectangle.topLeft().x() + boundingRectangle.topRight().x())/2, 
                                (boundingRectangle.topLeft().y() + boundingRectangle.topRight().y())/2, 
                                self, scene, id = 0)
            self.hs.append(hspot)
            
            hspot = Hotspots(   (boundingRectangle.bottomRight().x() + boundingRectangle.topRight().x())/2, 
                                (boundingRectangle.bottomRight().y() + boundingRectangle.topRight().y())/2, 
                                self, scene, id = 1)
            self.hs.append(hspot)
            hspot = Hotspots(   (boundingRectangle.bottomLeft().x() + boundingRectangle.bottomRight().x())/2, 
                                (boundingRectangle.bottomLeft().y() + boundingRectangle.bottomRight().y())/2, 
                                self, scene, id = 2)
            self.hs.append(hspot)
            
            hspot = Hotspots(   (boundingRectangle.bottomLeft().x() + boundingRectangle.topLeft().x())/2, 
                                (boundingRectangle.bottomLeft().y() + boundingRectangle.topLeft().y())/2, 
                                self, scene, id = 3)
            self.hs.append(hspot)

        self.setPolygon(self.myPolygon)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def itemChange(self, change, value):
        """
        Item change
        """
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.inputs:
                arrow.updatePosition()
            for arrow in self.outputs:
                arrow.updatePosition()
        if change == QGraphicsItem.ItemSelectedChange:
            if value == True:
                for hs in self.hs:
                    hs.setOpacity(1)
            else:
                for hs in self.hs:
                    hs.setOpacity(0.01)
        return value

    def paint(self, painter, option, widget=None):
        """
        Paint function
        """
        super(DiagramItem, self).paint(painter, option, widget)

        whiteText = QColor(255,255,255)
        blackText = QColor(0,0,0)
        redText = QColor(255,0,0)
        greenText = QColor(0,255,0)

        painter.setPen(blackText)
        try:
            if sys.version_info > (3,): # python 3 support
                textItem = self.name
            else:
                textItem = self.name.decode('utf8')
        except UnicodeDecodeError as e:
            textItem = self.name
        except UnicodeEncodeError as e:
            textItem = self.name
        painter.drawText(self.boundingRect(), Qt.AlignCenter|Qt.AlignVCenter, textItem)

    def showHotspots(self):
        """
        Show hotspots
        """
        for hs in self.hs:
            hs.setOpacity(1)
            
    def hideHotspots(self):
        """
        hide hotspots
        """
        for hs in self.hs:
            hs.setOpacity(0.01)
            
    def hoverEnterEvent(self, event):
        """
        On hover enter event
        """
        if not self.isSelected():
            for hs in self.hs:
                hs.setOpacity(1)
        super(DiagramItem, self).hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """
        On hover leave event
        """
        if not self.isSelected():
            for hs in self.hs:
                hs.setOpacity(0.01)
        super(DiagramItem, self).hoverLeaveEvent(event)
        
    def mouseMoveEvent  (self, event):
        """
        On mouse move event
        """
        self.itemMoved = True
        super(DiagramItem, self).mouseMoveEvent(event)

    def mouseReleaseEvent (self, event):
        """
        On mouse release event
        """
        if self.itemMoved:
            self.parentWidget.DataChanged.emit()
            self.itemMoved = False; 
        super(DiagramItem, self).mouseReleaseEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """
        On mouse double click event
        """
        if (event.button() == Qt.LeftButton):
            self.openDialog()
        super(DiagramItem, self).mouseDoubleClickEvent(event)
        
    def openDialog(self):
        """
        Open settings dialog
        """
        # cannot edit the start item
        if isinstance(self, DiagramItem):
            if self.diagramType == DiagramItem.StartEnd:
                return

        # read all available variables
        var2add = self.parentWidget.getVariables()
        
        if not len(self.data['item-data']['data']['obj']):
            QMessageBox.information(self.parentWidget, "Configuration action", "No argument for this action")
        else:
            actionDialog = GenericConfigDialog.ActionDialog(self, self.parentWidget.helper,  self.data['item-data'], 
                                                    owner=self.parentWidget, variables=var2add,
                                                    testParams = self.parentWidget.testParams)
            if actionDialog.exec_() == QDialog.Accepted:
                actionParams = actionDialog.getValues()
                self.data['item-data']['data']['obj'] = actionParams

                textItem = None
                if self.data['item-data']['action'] == ACTION_TESTCASE:
                    textItem = self.parentWidget.prepareTextTestcase(itemId=int(self.itemId), tcData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_CACHE:
                    textItem = self.parentWidget.prepareTextCache(itemId=int(self.itemId), tcData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_TIME:
                    textItem = self.parentWidget.prepareTextTime(itemId=int(self.itemId), tcData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_PRIVATE:
                    textItem = self.parentWidget.prepareTextPrivate(itemId=int(self.itemId), tcData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_PUBLIC:
                    textItem = self.parentWidget.prepareTextPublic(itemId=int(self.itemId), tcData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_LABEL:
                    textItem = self.parentWidget.prepareTextLabel(itemId=int(self.itemId), labelData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_TEMPLATE:
                    textItem = self.parentWidget.prepareTextTemplate(itemId=int(self.itemId), tplData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_MANIPULATOR:
                    textItem = self.parentWidget.prepareTextManipulator(itemId=int(self.itemId), manData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_VALIDATOR:
                    textItem = self.parentWidget.prepareTextValidator(itemId=int(self.itemId), valData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_CONDITION_IF:
                    textItem = self.parentWidget.prepareTextCondition(conditionData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_ADAPTER:
                    textItem = self.parentWidget.prepareTextAdapter(itemId=int(self.itemId), adapterId=self.data['item-data']['adapter-id'],
                                        adapterData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_DO:
                    textItem = self.parentWidget.prepareTextAdapter(itemId=int(self.itemId), adapterId=self.data['item-data']['adapter-id'],
                                        adapterData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_LIBRARY:
                    textItem = self.parentWidget.prepareTextLibrary(itemId=int(self.itemId), libId=self.data['item-data']['library-id'],
                                        libData=self.data['item-data'])
                elif self.data['item-data']['action'] == ACTION_STEP:
                    self.parentWidget.DataChanged.emit()
                else:
                    print('bad action: %s' % self.data['item-data']['action'])
                 
                if textItem is not None:
                    self.setText(textItem)
                    self.parentWidget.DataChanged.emit()
    
    def removeArrow(self, arrow):
        """
        Remove arrow
        """
        try:
            if arrow.startItem() == self:
                self.outputs.remove(arrow)
                for arrow in self.outputs:
                    self.setTextArrow(arrow=arrow)
                    arrow.update()
            else:
                self.inputs.remove(arrow)
            if arrow.startingPoint is not None:
                arrow.startingPoint.setOpacity(0.01)
                arrow.startingPoint.setDisconnected()
            if arrow.endingPoint is not None:
                arrow.endingPoint.setOpacity(0.01)
                arrow.endingPoint.setDisconnected()
        except ValueError:
            pass

    def removeArrows(self):
        """
        Remove arrows
        """
        while len(self.inputs):
            arrow = self.inputs.pop()
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)

        while len(self.outputs):
            arrow = self.outputs.pop()
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)
            
    def addArrow(self, arrow):
        """
        Add arrow
        """
        if arrow.startItem() == self:
            self.addOutput(arrow)
            self.setTextArrow(arrow=arrow)
        else:
            self.addInput(arrow)

    def setTextArrow(self, arrow):
        """
        Set text for arrow
        """
        if self.diagramType == DiagramItem.Conditional:
            if len(self.outputs) == 1: arrow.setText(text="True" )
            if len(self.outputs) == 2: arrow.setText(text="False" )

        if self.diagramType == DiagramItem.Do:
            if len(self.outputs) == 1: arrow.setText(text="OK" )
            if len(self.outputs) == 2: arrow.setText(text="KO" )

    def setItemId(self, itemId):
        """
        Set item id
        """
        self.itemId = itemId
        self.data['item-id'] = str(self.itemId)

    def setData(self, data):
        """
        Set data
        """
        self.data['item-data'] = data

    def setPosition(self):
        """
        Set the position of the item
        """
        self.data['pos-x'] = "%s" % self.x()
        self.data['pos-y'] = "%s" % self.y()

    def setText(self,newName):
        """
        Set the name of item
        """
        self.name = newName
        self.data['item-text'] = newName

    def setLinks(self):
        """
        Set the links
        """
        links = []
        for out in self.outputs:
            nextItemId = self.getNextItemID(arrow=out)
            links.append( { 
                            'next-item-id': str(nextItemId),
                            'to-hotspot-id': str(out.toHotspotID),
                            'from-hotspot-id': str(out.fromHotspotID) 
                            } 
                        )
        self.data['item-links'] = links

    def getName(self):
        """
        Get item name
        """
        return self.name
   
    def getNextItemID(self, arrow):
        """
        Get the next item ID
        """
        nextItemID = None
        try:
            for gItem in self.parentWidget.scene.items():
                if not isinstance(gItem, DiagramItem):
                    continue   
                if gItem.hasInputs():
                    if arrow == gItem.getInput(0):
                        nextItemID = gItem.itemId
                        break
        except Exception as e:
            print("error on get next item ID: %s" % e)
        
        return nextItemID

    def addInput(self, arrow):
        """
        Add input
        """
        if len(self.inputs) >= self.maxInputs:
            return

        self.inputs.append( arrow )
        self.parentWidget.DataChanged.emit()
 
    def addOutput(self, arrow):
        """
        Add output
        """
        if len(self.outputs) >= self.maxOutputs:
            return
        self.outputs.append( arrow )
        self.parentWidget.DataChanged.emit()

    def getOutput(self, id):
        """
        Get output
        """
        return self.outputs[id]

    def getInput(self, id):
        """
        Get input
        """
        return self.inputs[id]

    def hasInputs(self):
        """
        Has inputs  ?
        """
        return len(self.inputs)

    def hasOutputs(self):
        """
        Has outputs ?
        """
        return len(self.outputs)

class DiagramScene(QGraphicsScene):
    """
    Diagram scene class
    """
    itemInserted = pyqtSignal()
    InsertItem, InsertLine, MoveItem  = range(3)
    def __init__(self, parent, contextMenu=None, itemMenu=None):
        """
        Constructor
        """
        super(DiagramScene, self).__init__(parent)
        self.parentWidget = parent
        self.contextMenu = contextMenu
        self.currentMousePosition = None

        self.myItemMenu = itemMenu
        self.myMode = self.MoveItem
        self.myItemType = DiagramItem.Action
        self.line = None
        self.textItem = None
        self.myItemColor = Qt.white
        self.myTextColor = Qt.black
        self.myLineColor = Qt.black
        self.myFont = QFont()
        
        self.endItem = None

    def setMode(self, mode):
        """
        Set mode
        """
        self.myMode = mode

    def setItemType(self, type):
        """
        Set item type
        """
        self.myItemType = type
 
    def keyReleaseEvent (self, event):
        """
        On key release event
        """
        super(DiagramScene, self).keyReleaseEvent(event)

    def mousePressEvent(self, mouseEvent):
        """
        On mouse press event
        """
        self.startingMousePosition = mouseEvent.scenePos()
        self.endMousePosition = mouseEvent.scenePos()
        self.currentMousePosition = mouseEvent.scenePos()

        if self.myMode == self.InsertLine:
            self.line = QGraphicsLineItem(QLineF(mouseEvent.scenePos(), mouseEvent.scenePos()))
            self.line.setPen(QPen(self.myLineColor, 2))
            self.addItem(self.line)

        super(DiagramScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        On mouse move event
        """
        if self.myMode == self.InsertLine and self.line:
            newLine = QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
            
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)
                
                if len(endItems) and isinstance(endItems[0], DiagramItem) :
                    self.endItem = endItems[0]
                    self.endItem.showHotspots()
                else:
                    if self.endItem is not None:
                        self.endItem.hideHotspots()
                        self.endItem = None
        else:
            super(DiagramScene, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        On mouse release event
        """
        if self.line and self.myMode == self.InsertLine:
            p1 = self.line.line().p1()
            p2 = self.line.line().p2()
            
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)
            self.line = None

            if len(startItems) and len(endItems) and startItems[0] != endItems[0]: 
                if (isinstance(startItems[0], DiagramItem) and  isinstance(endItems[0], DiagramItem) ):
                    startItem = startItems[0]
                    endItem = endItems[0]
                    if len(startItem.outputs)<startItem.maxOutputs and len(endItem.inputs)<endItem.maxInputs:
                        arrow = Arrow(startItem, endItem, arrow_start_point =  p1, arrow_end_point= p2)
                        arrow.setColor(self.myLineColor)
                        startItem.addArrow(arrow)
                        endItem.addArrow(arrow)
                        arrow.setZValue(-1000.0)
                        self.addItem(arrow)
                        arrow.updatePosition()
        self.line = None
        super(DiagramScene, self).mouseReleaseEvent(mouseEvent)

    def isItemChange(self, type):
        """
        Is item change
        """
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False

class GraphAbstract(QWidget, Logger.ClassLogger):
    """
    Graph abstract widget
    """
    DataChanged = pyqtSignal()
    AddStep = pyqtSignal()
    def __init__(self, parent, helper, testParams):
        """
        Constructor
        """
        super(GraphAbstract, self).__init__(parent)
        self.__parent = parent
        self.helper = helper
        self.testParams = testParams
        self.itemId = 0
        self.__mime__ = "application/x-%s-test-abstract" % Settings.instance().readValue( key='Common/acronym' ).lower()

        self.createWidget()
        self.createActions()
        self.createConnections()
        self.createToolBar()
        
    def createWidget(self):
        """
        Create widget
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarClipboard = QToolBar(self)
        self.dockToolbarClipboard.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarClipboard.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarTest = QToolBar(self)
        self.dockToolbarTest.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarTest.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.scene = DiagramScene(self)
        self.scene.setSceneRect(QRectF(0, 0, GRAPHIC_SCENE_SIZE, GRAPHIC_SCENE_SIZE))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.setMouseTracking(1)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse) 

        self.pointerButton = QToolButton()
        self.pointerButton.setCheckable(True)
        self.pointerButton.setChecked(True)
        self.pointerButton.setText("Pointer")
        self.pointerButton.setIcon(QIcon(":/pointer.png"))
        self.pointerButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.linePointerButton = QToolButton()
        self.linePointerButton.setCheckable(True)
        self.linePointerButton.setIcon(QIcon(":/linepointer.png"))
        self.linePointerButton.setText("Arrow")
        self.linePointerButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.pointerTypeGroup = QButtonGroup()
        self.pointerTypeGroup.addButton(self.pointerButton, DiagramScene.MoveItem)
        self.pointerTypeGroup.addButton(self.linePointerButton, DiagramScene.InsertLine)

        self.sceneScaleCombo = QComboBox()
        self.sceneScaleCombo.setStyleSheet( """QComboBox {border: 0px; }""" )
        self.sceneScaleCombo.setMinimumWidth(80)
        self.sceneScaleCombo.addItems([ "25%", "50%", "75%", "100%", "125%", "150%"])
        self.sceneScaleCombo.setCurrentIndex(3)
        layoutZoom = QVBoxLayout()
        layoutZoom.addWidget(QLabel(self.tr(" Zoom:")))
        layoutZoom.addWidget(self.sceneScaleCombo)
        self.frameZoom = QFrame()
        self.frameZoom.setLayout(layoutZoom)
        
        title = QLabel(self.tr("Test Abstract Definition:"))
        title.setStyleSheet("QLabel { padding-left: 2px; padding-top: 2px }")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        
        self.drawBox = QGroupBox("Draw")
        self.drawBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutDrawBox = QHBoxLayout()
        layoutDrawBox.addWidget(self.dockToolbar)
        layoutDrawBox.setContentsMargins(0,0,0,0)
        self.drawBox.setLayout(layoutDrawBox)
        
        self.clipBox = QGroupBox("Clipboard")
        self.clipBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """)
        layoutClipBox = QHBoxLayout()
        layoutClipBox.addWidget(self.dockToolbarClipboard)
        layoutClipBox.setContentsMargins(0,0,0,0)
        self.clipBox.setLayout(layoutClipBox)
        
        self.testBox = QGroupBox("Configure")
        self.testBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutTestBox = QHBoxLayout()
        layoutTestBox.addWidget(self.dockToolbarTest)
        layoutTestBox.setContentsMargins(0,0,0,0)
        self.testBox.setLayout(layoutTestBox)
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.testBox)
        layoutToolbars.addWidget(self.drawBox)
        layoutToolbars.addWidget(self.clipBox)

        layoutToolbars.addWidget( QLabel(self.tr(" Right click to draw your test!")) )
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        layoutFinal = QVBoxLayout()
        layoutFinal.addWidget(title)
        layoutFinal.addLayout(layoutToolbars)
        layoutFinal.addWidget(self.view)
        layoutFinal.setContentsMargins(0,0,0,0)

        self.setLayout(layoutFinal)
    
    def createToolBar(self):
        """
        Create toolbar
        """
        self.dockToolbar.addWidget(self.pointerButton)
        self.dockToolbar.addWidget(self.linePointerButton)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addWidget(self.frameZoom)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.deleteAction)
        self.dockToolbar.setIconSize(QSize(16, 16))
        

        self.dockToolbarClipboard.addAction(self.copyAction)
        self.dockToolbarClipboard.addAction(self.pasteAction)
        self.dockToolbarClipboard.setIconSize(QSize(16, 16))
        
        self.dockToolbarTest.addAction(self.addStepAction)
        self.dockToolbarTest.setIconSize(QSize(16, 16))
        
    def toolbar(self):
        """
        Return toolbar
        """
        return self.dockToolbar
        
    def createConnections(self):
        """
        Create connections
        """
        self.pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)
        self.sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)
        self.view.customContextMenuRequested.connect(self.onPopupMenu)
        self.scene.selectionChanged.connect(self.onItemSelected)

    def createActions(self):
        """
        Create actions
        """
        self.addBreakpointAction = QtHelper.createAction(self, self.tr("&Breakpoint"), self.addBreakpoint )
        self.deleteAction = QtHelper.createAction(self, "Delete", self.deleteItem,  icon = QIcon(":/param-delete.png"),
                                                    tip = 'Delete item', shortcut='Delete' )
        self.copyAction = QtHelper.createAction(self, "Copy", self.copyItem,  icon = QIcon(":/param-copy.png"),
                                                    tip = 'Copy item', shortcut='Ctrl+C' )
        self.pasteAction = QtHelper.createAction(self, "Paste", self.pasteItem,  icon = QIcon(":/param-paste.png"),
                                                    tip = 'Paste item', shortcut='Ctrl+V' )
        self.reloadAction = QtHelper.createAction(self, "Reload Item", self.reloadItem,  icon = None,
                                                    tip = 'Reload item from original' )
                                                    
        self.addStepAction = QtHelper.createAction(self, self.tr("&Step"), self.addDesignStep, icon = QIcon(":/step-add.png"),
                                                    tip = self.tr('Add a new step') )
                                                    
        self.setDefault()

    def addDesignStep(self):
        """
        Add design step
        """
        self.AddStep.emit()
        
    def print_(self, printer):
        """
        internal print accessor
        """
        painter = QPainter(printer)
        self.view.render(painter)
        
    def setDefault(self):
        """
        Set default action
        """
        self.deleteAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.pasteAction.setEnabled(False)
        self.pasteToActive()

    def pasteToActive(self):
        """
        Paste to active
        """
        mimeData = QApplication.clipboard().mimeData()
        if mimeData.hasFormat(self.__mime__):
            self.pasteAction.setEnabled(True)
        else:
            self.pasteAction.setEnabled(False)

    def getItemId(self):
        """
        Get a new item id
        """
        self.itemId += 1
        return self.itemId

    def onItemInserted(self):
        """
        Item inserted
        """
        self.DataChanged.emit()

    def onItemSelected(self):
        """
        Item selected
        """
        if len(self.scene.selectedItems()):
            self.deleteAction.setEnabled(True)
            self.copyAction.setEnabled(True)
        else:
            self.deleteAction.setEnabled(False)
            self.copyAction.setEnabled(False)

    def sceneScaleChanged(self, scale):
        """
        On scale changed
        """
        if sys.version_info > (3,): # python3 support
            newScale = float(scale.split("%")[0]) / 100.0
        else:
            newScale = scale.left(scale.indexOf("%")).toDouble()[0] / 100.0

        if QtHelper.IS_QT5:
            oldMatrix = self.view.transform()
            self.view.resetTransform()
        else:
            oldMatrix = self.view.matrix()
            self.view.resetMatrix()
        
        self.view.translate(oldMatrix.dx(), oldMatrix.dy())
        self.view.scale(newScale, newScale)
    
    def pointerGroupClicked(self, i):
        """
        On pointer clicked
        """
        self.scene.setMode(self.pointerTypeGroup.checkedId())

    def addItem(self, itemType, itemId, itemText, itemColor, itemPos, itemData):
        """
        Add item
        """
        item = DiagramItem(itemType, parentWidget=self, scene=self.scene)
        item.setItemId(itemId=int(itemId) )
        item.setPen(QPen(itemColor, 1))
        item.setBrush(itemColor)
        item.setText(itemText)
        item.setData(itemData)
        self.scene.addItem(item)

        item.setPos( itemPos )

        self.onItemInserted()

    def addStart(self):
        """
        Add begin
        """
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_STARTEND )
        self.addItem(   itemType=DiagramItem.StartEnd, itemId=self.getItemId(), itemText="Start", 
                        itemColor=QBrush(color),  itemPos=QPointF(GRAPHIC_SCENE_SIZE/2, (GRAPHIC_SCENE_SIZE/2) - 150), itemData=''  )
                        
    def getVariables(self):
        """
        Get variables
        """

        # read all available variables
        var2add = []
        for gItem in self.scene.items():
            if isinstance(gItem, DiagramItem):
                if gItem.diagramType in [ DiagramItem.Action, DiagramItem.Adapter, DiagramItem.Template, DiagramItem.Library,
                                           DiagramItem.Manipulator, DiagramItem.Validator, DiagramItem.Do, DiagramItem.Cache,
                                           DiagramItem.Time, DiagramItem.Private, DiagramItem.Public ]:
                    if 'return-value' in gItem.data['item-data']['data']:
                        if gItem.data['item-data']['data']['return-value'] == 'True':
                            var2add.append( "ACTION%s" % gItem.itemId )
        
        return var2add

    def __parseValue(self, val):
        """
        Parse value
        """
        lines = val.splitlines()
        if not len(lines):
            return val
        else:
            if len(lines[0]) > 25:
                return "%s..." % lines[0][:20]
            else:
                return lines[0]

    def prepareTextCondition(self, conditionData):
        """
        prepare text item for condition
        """
        if 'function' not in conditionData['data']:
            return 'Condition'
            
        # extract name
        funcName = conditionData['data']['function']

        funcArgType = "%s" % conditionData['data']['obj'][0]['selected-type']
        funcArg = "%s" % conditionData['data']['obj'][0]['value']

        leftVal = "%s: %s" % (funcArgType, funcArg)

        funcArgType = "%s" % conditionData['data']['obj'][1]['selected-type']
        if isinstance( conditionData['data']['obj'][1]['value'], dict):
            condVal = "%s" % conditionData['data']['obj'][1]['value']['operator']
        else:
            condVal = 'Undefined'

        funcArgType = "%s" % conditionData['data']['obj'][2]['selected-type']
        funcArg = "%s" % conditionData['data']['obj'][2]['value']
        if funcArgType == 'none':
            rightVal = 'None'
        else:
            rightVal = "%s: %s" % (funcArgType, funcArg)

        if condVal == 'Undefined':
            textItem = '%s\n%s' % (funcName.title(), condVal)
        else:
            textItem =  "%s\n%s\n%s" % (leftVal, condVal, rightVal)
        return textItem

    def prepareTextLabel(self, itemId, labelData):
        """
        prepare text label
        """
        funcArgType = "%s" % labelData['data']['obj'][0]['selected-type']
        funcArg = "%s" % unicode( labelData['data']['obj'][0]['value'] )

        textItem =  "%s" % (funcArg)
        return textItem

    def prepareTextTestcase(self, itemId, tcData):
        """
        prepare text testcase
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%s%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%s%s" % (funcRet, funcName)
        return textItem

    def prepareTextTemplate(self, itemId, tplData):
        """
        prepare text testcase
        """
        # extract name
        funcName = tplData['data']['function']

        funcRet = ""
        if len(tplData['data']['obj']) >= 1:
            funcArgType = "%s" % tplData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tplData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tplData['data']:
            if tplData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%s\n%s%s\n%s: %s" % (ACTION_TEMPLATE, funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%s\n%s%s" % (ACTION_TEMPLATE, funcRet, funcName)
        return textItem

    def prepareTextAdapter(self, itemId, adapterId, adapterData):
        """
        Prepare text item for adapter
        """
        funcName = adapterData['data']['function']
        adpName = adapterData['data']['main-name']

        funcRet = ""
        if len(adapterData['data']['obj']) >= 1:
            funcArgType = "%s" % adapterData['data']['obj'][0]['selected-type']
            funcArg = "%s" % adapterData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in adapterData['data']:
            if adapterData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%s %s #%s\n%s\n%s: %s" % (funcRet, adpName, adapterId, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%s %s #%s\n%s" % (funcRet, adpName, adapterId, funcName)

        return textItem

    def prepareTextLibrary(self, itemId, libId, libData):
        """
        Prepare text item for library
        """
        funcName = libData['data']['function']
        libName = libData['data']['main-name']

        funcRet = ""
        if len(libData['data']['obj']) >= 1:
            funcArgType = "%s" % libData['data']['obj'][0]['selected-type']
            funcArg = "%s" % libData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in libData['data']:
            if libData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%s %s #%s\n%s\n%s: %s" % (funcRet, libName, libId, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%s %s #%s\n%s" % (funcRet, libName, libId, funcName)

        return textItem

    def prepareTextManipulator(self, itemId, manData):
        """
        prepare text manipulator
        """
        # extract name
        mainName = manData['data']['main-name']
        funcName = manData['data']['function']

        funcRet = ""
        if len(manData['data']['obj']) >= 1:
            funcArgType = "%s" % manData['data']['obj'][0]['selected-type']
            funcArg = "%s" % manData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in manData['data']:
            if manData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%s::%s\n%s%s\n%s: %s" % (ACTION_MANIPULATOR, mainName, funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%s::%s\n%s%s" % (ACTION_MANIPULATOR, mainName, funcRet, funcName)
        return textItem
        
    def prepareTextCache(self, itemId, tcData):
        """
        prepare text cache
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%sCache::%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%sCache::%s" % (funcRet, funcName)
        return textItem
        
    def prepareTextInteract(self, itemId, tcData):
        """
        prepare text cache
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%sInteract::%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%sInteract::%s" % (funcRet, funcName)
        return textItem
        
    def prepareTextTrace(self, itemId, tcData):
        """
        prepare text cache
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%sTrace::%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%sTrace::%s" % (funcRet, funcName)
        return textItem
        
    def prepareTextTime(self, itemId, tcData):
        """
        prepare text time
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%sTime::%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%sTime::%s" % (funcRet, funcName)
        return textItem
        
    def prepareTextPrivate(self, itemId, tcData):
        """
        prepare text private
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%sPrivate::%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%sPrivate::%s" % (funcRet, funcName)
        return textItem
        
    def prepareTextPublic(self, itemId, tcData):
        """
        prepare text public
        """
        # extract name
        funcName = tcData['data']['function']

        funcRet = ""
        if len(tcData['data']['obj']) >= 1:
            funcArgType = "%s" % tcData['data']['obj'][0]['selected-type']
            funcArg = "%s" % tcData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in tcData['data']:
            if tcData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%sPublic::%s\n%s: %s" % (funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%sPublic::%s" % (funcRet, funcName)
        return textItem
        
    def prepareTextValidator(self, itemId, valData):
        """
        prepare text validator
        """
        # extract name
        mainName = valData['data']['main-name']
        funcName = valData['data']['function']

        funcRet = ""
        if len(valData['data']['obj']) >= 1:
            funcArgType = "%s" % valData['data']['obj'][0]['selected-type']
            funcArg = "%s" % valData['data']['obj'][0]['value']
        else:
            funcArg = ""
            funcArgType = ""

        if 'return-value' in valData['data']:
            if valData['data']['return-value'] == 'True':
                funcRet = "ACTION%s = " % itemId

        if len(funcArg):
            funcArgParsed = self.__parseValue(val=funcArg)
            textItem =  "%s::%s\n%s%s\n%s: %s" % (ACTION_VALIDATOR, mainName, funcRet, funcName, funcArgType, funcArgParsed)
        else:
            textItem =  "%s::%s\n%s%s" % (ACTION_VALIDATOR, mainName, funcRet, funcName)
        return textItem

    def addLabel(self, fctParams):
        """
        Add label function
        """ 
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_LABEL,  'data': fctParams, 'item-id': str(itemId) }
        textItem = 'label'
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_LABEL )

        self.addItem(   itemType=DiagramItem.Label, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(Qt.transparent),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addTc(self, fctParams):
        """
        Add testcase function
        """ 
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_TESTCASE,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextTestcase(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_TESTCASE )

        self.addItem(   itemType=DiagramItem.Action, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addTpl(self, fctParams):
        """
        Add template function
        """ 
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_TEMPLATE,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextTemplate(itemId=itemId, tplData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_TEMPLATE )
        self.addItem(   itemType=DiagramItem.Template, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addIf(self, fctParams):
        """
        Add if condition
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_CONDITION_IF,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextCondition(conditionData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_CONDITION )
        self.addItem(   itemType=DiagramItem.Conditional, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addStep(self, fctParams):
        """
        Add step
        """
        stpId, stpArgs = fctParams
        tpl = { 'action': ACTION_STEP,   'step-id': str(stpId),  'data': stpArgs }

        stepId = tpl['step-id']
        funcName = tpl['data']['function']
        textItem = "%s #%s\n%s" % (ACTION_STEP, stepId, funcName)
                        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_STEP )
        self.addItem(   itemType=DiagramItem.Step, itemId=self.getItemId(), itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addAdapter(self, fctParams):
        """
        Add adapter
        """
        itemId = self.getItemId()
        
        adpId, adpArgs = fctParams
        tpl = { 'action': ACTION_ADAPTER, 'adapter-id': str(adpId), 'item-id': str(itemId), 'data': adpArgs  }

        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_ADAPTER )
        textItem = self.prepareTextAdapter(itemId=itemId, adapterId=adpId, adapterData=tpl)
        self.addItem(   itemType=DiagramItem.Adapter, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addDo(self, fctParams):
        """
        Add do 
        """
        itemId = self.getItemId()
        
        adpId, adpArgs = fctParams
        tpl = { 'action': ACTION_DO, 'adapter-id': str(adpId), 'item-id': str(itemId), 'data': adpArgs  }

        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_DO )
        textItem = self.prepareTextAdapter(itemId=itemId, adapterId=adpId, adapterData=tpl)
        self.addItem(   itemType=DiagramItem.Do, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addLibrary(self, fctParams):
        """
        Add library
        """
        itemId = self.getItemId()
        
        libId, libArgs = fctParams
        tpl = { 'action': ACTION_LIBRARY, 'library-id': str(libId), 'item-id': str(itemId), 'data': libArgs  }

        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_LIBRARY )
        textItem = self.prepareTextLibrary(itemId=itemId, libId=libId, libData=tpl)
        self.addItem(   itemType=DiagramItem.Library, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addBreakpoint(self):
        """
        Add breakpoint
        """
        tpl = { 'action': ACTION_BREAKPOINT,  'data': {'obj': [] } }
        textItem = ACTION_BREAKPOINT
        
        # set color
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_TESTCASE )
        # add item
        self.addItem(   itemType=DiagramItem.Action, itemId=self.getItemId(), itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addElse(self):
        """
        Add else condition
        """
        tpl = { 'action': ACTION_CONDITION_ELSE, 'data': { 'obj': [ {} ] }  }
        return tpl

    def addEndIf(self):
        """
        Add end if condition
        """
        tpl = { 'action': ACTION_CONDITION_ENDIF, 'data': { 'obj': [ {} ] }  }
        return tpl
   
    def addPass(self):
        """
        Add pass
        """
        tpl = { 'action': ACTION_PASS, 'data': { 'obj': [ {} ] }  }
        return tpl

    def addManipulator(self, fctParams):
        """
        Add manipulator
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_MANIPULATOR,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextManipulator(itemId=itemId, manData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_MANIPULATOR )
        self.addItem(   itemType=DiagramItem.Manipulator, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addValidator(self, fctParams):
        """
        Add validator
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_VALIDATOR,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextValidator(itemId=itemId, valData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_VALIDATOR )
        self.addItem(   itemType=DiagramItem.Validator, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addCache(self, fctParams):
        """
        TODO
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_CACHE,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextCache(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_CACHE )
        self.addItem(   itemType=DiagramItem.Cache, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addInteract(self, fctParams):
        """
        TODO
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_INTERACT,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextInteract(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_INTERACT )
        self.addItem(   itemType=DiagramItem.Cache, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )

    def addTrace(self, fctParams):
        """
        Add trace elements
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_TRACE,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextTrace(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_TRACE )
        self.addItem(   itemType=DiagramItem.Cache, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )
                        
    def addTime(self, fctParams):
        """
        Add time elements
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_TIME,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextCache(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_TIME )
        self.addItem(   itemType=DiagramItem.Time, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )
        
    def addPrivate(self, fctParams):
        """
        Add private elements
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_PRIVATE,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextPrivate(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_PRIVATE )
        self.addItem(   itemType=DiagramItem.Private, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )
        
    def addPublic(self, fctParams):
        """
        Add public elements
        """
        itemId = self.getItemId()
        
        tpl = { 'action': ACTION_PUBLIC,  'data': fctParams, 'item-id': str(itemId) }
        textItem = self.prepareTextPublic(itemId=itemId, tcData=tpl)
        
        # add item
        color = QColor(0, 0, 0)
        color.setNamedColor( COLOR_PUBLIC )
        self.addItem(   itemType=DiagramItem.Public, itemId=itemId, itemText=textItem, 
                        itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=tpl  )
                        
    def deleteItem(self):
        """
        Delete all selected items
        """
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                # dont remove the start diagram
                if item.diagramType == DiagramItem.StartEnd:
                    break
                item.removeArrows()                
            else:#Arrow
                item.startItem().removeArrow(item)
                item.endItem().removeArrow(item)
            self.scene.removeItem(item)
            self.onItemInserted()
        
        self.setDefault()
    
    def reloadItem(self):
        """
        Reload item
        Can be used when adapter changed
        """
        # extract all selected item
        itms = []
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                if item.diagramType in [ DiagramItem.Do, DiagramItem.Adapter ]:
                    itms.append(item)

        # update it with original
        for item in itms:
            if item.diagramType in [ DiagramItem.Do, DiagramItem.Adapter ]:
                funName = item.data['item-data']['data']['function']
                mainName = item.data['item-data']['data']['main-name']
                adpName, clsName = mainName.split('::')
                
                adapters = self.helper.helpAdapters()
                for adp in adapters:
                    for cls in adp['classes']:
                        if adp['name'] == adpName and cls['name'] == clsName:
                            for fct in cls['functions']:
                                if fct['name'] == funName:
                                    # read data and update it
                                    argsFct = self.parseDocString(docstring=fct['desc'])
                                    argsFct['function'] = fct['name']
                                    argsFct['main-name'] = mainName
                                    if 'default-args' in fct:
                                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)

                                    item.data['item-data']['data'] = argsFct
                                    
    def copyItem(self):
        """
        Copy all selected items
        """
        # extract all selected item
        itms = []
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                itms.append(item.data)

        # pickle data
        mime = QMimeData()
        mime.setData( self.__mime__ , QByteArray(pickle.dumps(itms)) )

        # copy to clipboard
        QApplication.clipboard().setMimeData(mime,QClipboard.Clipboard)
        self.pasteAction.setEnabled(True)

    def pasteItem(self):
        """
        Paste all selected items
        """
        # read from clipboard
        mimeData = QApplication.clipboard().mimeData()
        if not mimeData.hasFormat(self.__mime__):
            return None

        # extract data
        data = mimeData.data(self.__mime__)
        if data:
            try:
                items = pickle.loads(data.data())
                for itm in items:
                    # extract item info
                    itemType = int(itm['item-type'])
                    itemText = itm['item-text']
                    itemData = itm['item-data']

                    # define the color of the item
                    color = self.getItemColor(itemType=itemType)
                        
                    # add item in first
                    itemId = self.getItemId()
                    self.addItem(   itemType=itemType, itemId=itemId, itemText=itemText, 
                                    itemColor=QBrush(color),  itemPos=self.scene.currentMousePosition, itemData=itemData  )
            except Exception as e:
                self.error( "unable to deserialize %s" % str(e) )

    def loadDefault(self):
        """
        Load default view with a start item
        """
        self.addStart()

    def getItemColor(self, itemType):
        """
        Return color according to the item type
        """
        # define the color of the item
        if itemType == DiagramItem.Action:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_TESTCASE )
        elif itemType == DiagramItem.Conditional:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_CONDITION )
        elif itemType == DiagramItem.Step:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_STEP )
        elif itemType == DiagramItem.Adapter:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_ADAPTER )
        elif itemType == DiagramItem.Do:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_DO )
        elif itemType == DiagramItem.Library:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_LIBRARY )
        elif itemType == DiagramItem.Template:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_TEMPLATE )
        elif itemType == DiagramItem.Manipulator:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_MANIPULATOR )
        elif itemType == DiagramItem.Validator:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_VALIDATOR )
        elif itemType == DiagramItem.Cache:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_CACHE )
        elif itemType == DiagramItem.Time:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_TIME )
        elif itemType == DiagramItem.Private:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_PRIVATE )
        elif itemType == DiagramItem.Public:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_PUBLIC )
        elif itemType == DiagramItem.Label:
            color = Qt.transparent
        else:
            color = QColor(0, 0, 0)
            color.setNamedColor( COLOR_STARTEND )

        return color

    def loadData(self, actions):
        """
        Set data, add all items and arrows
        """
        # begin to clear the scene
        self.scene.clear()

        # and draw all items
        maxItemId = self.itemId
        for graphicalItem in actions:

            # extract item info
            itemType = int(graphicalItem['item-type'])
            itemId = graphicalItem['item-id']
            if sys.version_info > (3,): # py3 support
                graphicalItem['item-text'] = graphicalItem['item-text']
            else:
                graphicalItem['item-text'] = graphicalItem['item-text'].decode('utf8')
            itemText = graphicalItem['item-text']
            posX = float(graphicalItem['pos-x'])
            posY = float(graphicalItem['pos-y'])
            itemData = graphicalItem['item-data']


            # define the color of the item
            color = self.getItemColor(itemType=itemType)
                
            # add item in first
            self.addItem(   itemType=itemType, itemId=itemId, itemText=itemText, 
                            itemColor=QBrush(color),  itemPos=QPointF(posX,posY), itemData=itemData  )
                            
            # kept the max id
            if int(itemId) > maxItemId:
                maxItemId = int(itemId)
        
        self.itemId = maxItemId

        # endly draw all arrows
        for curItem in self.scene.items():
            for saveItem in actions:
                if not isinstance(curItem, DiagramItem):
                    continue
                if curItem.itemId == int(saveItem['item-id']):
                    if 'item-links' in saveItem:
                        if isinstance(saveItem['item-links'], dict):
                            saveItem['item-links'] = [saveItem['item-links']]
                        for lnk in saveItem['item-links']:
                            itemId = lnk['next-item-id']
                            toHotspotId = lnk['to-hotspot-id']
                            fromHotspotId = lnk['from-hotspot-id']
                            
                            endItem = self.findItem(id=itemId)
                            if endItem is not None:
                                self.trace( "Arrow: %s -> %s" % (fromHotspotId,toHotspotId) )
                                arrow = Arrow(curItem, endItem, toHotspotId=toHotspotId, fromHotspotId=fromHotspotId)
                                arrow.setColor(self.scene.myLineColor)
                                curItem.addArrow(arrow)
                                endItem.addArrow(arrow)
                                arrow.setZValue(-1000.0)
                                self.scene.addItem(arrow)
                                arrow.updatePosition()

    def findItem(self, id):
        """
        Find item by id
        """
        itemFound = None
        for curItem in self.scene.items():
            if not isinstance(curItem, DiagramItem):
                continue        
            if curItem.itemId == int(id):
                itemFound = curItem
                break
        return itemFound

    def getInputs(self):
        """
        Get test inputs 
        """
        return self.testParams.parameters.table().model.getData()

    def getOutputs(self):
        """
        Get test outputs 
        """
        return self.testParams.parametersOutput.table().model.getData()

    def getAgents(self):
        """
        Get test agents 
        """
        return self.testParams.agents.table().model.getData()
        
    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu(self)

        # sub menu for adding library
        libsMenu = QMenu("Libraries", self)
        libsMenu.setIcon( QIcon(":/libraries-add.png") )
        for i in xrange(len(self.__parent.libraries().model.getData())):
            currentName = self.__parent.libraries().model.getData()[i]['data']['function']
            
            libMenu = QMenu("%s #%s" % (currentName, (i+1)), self)

            libraries = self.__parent.getHelpLibraries()
            if libraries is not None:
                for lib in libraries:
                    for cls in lib['classes']:
                        if "%s::%s" %(lib['name'], cls['name']) == currentName:
                            for fct in cls['functions']:
                                if fct['name'] == '__init__':
                                    continue
                                argsFct = self.parseDocString(docstring=fct['desc'])
                                argsFct['function'] = fct['name']
                                argsFct['main-name'] = currentName
                                if 'default-args' in fct:
                                    self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                                libMenu.addAction( QtHelper.createAction(self, fct['name'], self.addLibrary,
                                                    icon=QIcon(":/methods.png"), cb_arg=( (i+1), argsFct ) ) )
                                libMenu.addSeparator()      
            libsMenu.addMenu(libMenu)
            libsMenu.addSeparator()

        # sub menu for adding adapter
        adpsMenu = QMenu("Adapters", self)
        adpsMenu.setIcon( QIcon(":/adapters-add.png") )
        for i in xrange(len(self.__parent.adapters().model.getData())):
            currentName = self.__parent.adapters().model.getData()[i]['data']['function']
            
            adpMenu = QMenu("%s #%s" % (currentName, (i+1)), self)

            adpMoreMenu = QMenu("More...", self)

            adapters = self.__parent.getHelpAdapters()
            if adapters is not None:
                for adp in adapters:
                    for cls in adp['classes']:
                        if "%s::%s" %(adp['name'], cls['name']) == currentName:
                            for fct in cls['functions']:
                                if fct['name'] == '__init__':
                                    continue
                                argsFct = self.parseDocString(docstring=fct['desc'])
                                argsFct['function'] = fct['name']
                                argsFct['main-name'] = currentName
                                if 'default-args' in fct:
                                    self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)

                                if re.match(r"do[A-Z]", fct['name']) :
                                    adpMenu.addAction( QtHelper.createAction(self, fct['name'], self.addDo,
                                                        icon=QIcon(":/methods.png"), cb_arg=( (i+1), argsFct ) ) )
                                else:
                                    adpMoreMenu.addAction( QtHelper.createAction(self, fct['name'], self.addAdapter,
                                                        icon=QIcon(":/methods.png"), cb_arg=( (i+1), argsFct ) ) )

            adpMenu.addSeparator()
            adpMenu.addMenu(adpMoreMenu)
                           
            adpsMenu.addMenu(adpMenu)
            adpsMenu.addSeparator()
            
            
        # sub menu for adding step
        stepMenu = QMenu("Steps", self)
        stepMenu.setIcon( QIcon(":/steps.png") )

        for stp in self.__parent.steps().model.getData():
            stpMenu = QMenu("Step #%s" % stp['id'], self)

            functions = self.helper.helpFramework(moduleName='TestExecutor', className='Step')
            if functions is not None:
                for fct in functions:
                    if fct['type'] == 'method': 
                        argsFct = self.parseDocString(docstring=fct['desc'])
                        argsFct['function'] = fct['name']
                        stpMenu.addAction( QtHelper.createAction(self, fct['name'], self.addStep,
                                                    icon=QIcon(":/methods.png"), cb_arg=(stp['id'],argsFct) ) )
                        stpMenu.addSeparator()
            stepMenu.addMenu(stpMenu)
            stepMenu.addSeparator()
            
        # sub menu for adding cache functions
        cacheMenu = QMenu("Cache", self)
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='Cache')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    cacheMenu.addAction( QtHelper.createAction(self, fct['name'], self.addCache, 
                                            icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                    cacheMenu.addSeparator()
            
        # sub menu for adding Interact functions
        interactMenu = QMenu("Interact", self)
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='Interact')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    interactMenu.addAction( QtHelper.createAction(self, fct['name'], self.addInteract, 
                                            icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                    interactMenu.addSeparator()
                    
        # sub menu for adding Interact functions
        traceMenu = QMenu("Trace", self)
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='Trace')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    traceMenu.addAction( QtHelper.createAction(self, fct['name'], self.addTrace, 
                                            icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                    traceMenu.addSeparator()
                    
        # sub menu for adding time functions
        timeMenu = QMenu("Time", self)
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='Time')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    timeMenu.addAction( QtHelper.createAction(self, fct['name'], self.addTime, 
                                            icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                    timeMenu.addSeparator()
        
        # sub menu for adding storage functions
        storageMenu = QMenu("Storage", self)
        privateMenu = QMenu("Private", self)
        publicMenu = QMenu("Public", self)
        storageMenu.addMenu( privateMenu )
        storageMenu.addMenu( publicMenu )
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='Private')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    if fct['name'] not in [ '__init__' ]:
                        argsFct = self.parseDocString(docstring=fct['desc'])
                        argsFct['function'] = fct['name']
                        if 'default-args' in fct:
                            self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                        privateMenu.addAction( QtHelper.createAction(self, fct['name'], self.addPrivate, 
                                                icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                        privateMenu.addSeparator()
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='Public')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    if fct['name'] not in [ '__init__' ]:
                        argsFct = self.parseDocString(docstring=fct['desc'])
                        argsFct['function'] = fct['name']
                        if 'default-args' in fct:
                            self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                        publicMenu.addAction( QtHelper.createAction(self, fct['name'], self.addPublic, 
                                                icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                        publicMenu.addSeparator()
                    
        # sub menu for adding testcase function
        tcMenu = QMenu("TestCase", self)
        tcMenu.setIcon( QIcon(":/main.png") )
        functions = self.helper.helpFramework(moduleName='TestExecutor', className='TestCase')
        if functions is not None:
            for fct in functions:
                if fct['type'] == 'method': 
                    if fct['name'] in [ 'addStep', 'condition', 'label' ]:
                        pass # skip this function because steps can be added on the other part
                    else:
                        argsFct = self.parseDocString(docstring=fct['desc'])
                        argsFct['function'] = fct['name']
                        if 'default-args' in fct:
                            self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                        tcMenu.addAction( QtHelper.createAction(self, fct['name'], self.addTc, 
                                        icon=QIcon(":/methods.png"), cb_arg=argsFct ) )
                        tcMenu.addSeparator()

        # sub menu for templates
        tplsMenu = QMenu("Templates", self)
        functions = self.helper.helpFramework(moduleName='TestTemplates')
        if functions is not None:
            for valid in functions:
                if valid['name'] in [ "TemplateLayer", "TemplateMessage" ]:
                    continue
                tplMenu = QMenu(valid['name'], self)
                for fct in valid['functions']:
                    if fct['name'] == '__init__':
                        continue
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    tplMenu.addAction( QtHelper.createAction(self, fct['name'], self.addTpl,
                                        icon=QIcon(":/methods.png"), cb_arg=argsFct  ) )
                    tplMenu.addSeparator()
                tplsMenu.addMenu(tplMenu)
                tplsMenu.addSeparator()

        # condition
        function = self.helper.helpFramework(moduleName='TestExecutor', className='TestCase', functionName='condition')
        if function is None:
            argsFct = {}
        else:
            argsFct = self.parseDocString(docstring=function['desc'])
            argsFct['function'] = function['name']
            if 'default-args' in function:
                self.addDefaultValues(defaultValues=function['default-args'], currentFunction=argsFct)
        condAct = QtHelper.createAction(self, "Condition", self.addIf, icon=None, cb_arg=argsFct )

        # label
        function = self.helper.helpFramework(moduleName='TestExecutor', className='TestCase', functionName='label')
        if function is None:
            argsFct = {}
        else:
            argsFct = self.parseDocString(docstring=function['desc'])
            argsFct['function'] = function['name']
            if 'default-args' in function:
                self.addDefaultValues(defaultValues=function['default-args'], currentFunction=argsFct)
        labelAct = QtHelper.createAction(self, "Label", self.addLabel, icon=None, cb_arg=argsFct )


        # sub menu for manipulators
        manipsMenu = QMenu("Manipulators", self)
        functions = self.helper.helpFramework(moduleName='TestManipulators')
        if functions is not None:
            for manip in functions:
                manMenu = QMenu(manip['name'], self)
                currentName = manip['name']
                for fct in manip['functions']:
                    if fct['name'] == '__init__':
                        continue
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    argsFct['main-name'] = currentName
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    manMenu.addAction( QtHelper.createAction(self, fct['name'], self.addManipulator,
                                        icon=QIcon(":/methods.png"), cb_arg=argsFct  ) )
                    manMenu.addSeparator()
                manipsMenu.addMenu(manMenu)
                manipsMenu.addSeparator()

        # sub menu for validators
        valsMenu = QMenu("Validators", self)
        functions = self.helper.helpFramework(moduleName='TestValidators')
        if functions is not None:
            for valid in functions:
                valMenu = QMenu(valid['name'], self)
                currentName = valid['name']
                for fct in valid['functions']:
                    if fct['name'] == '__init__':
                        continue
                    argsFct = self.parseDocString(docstring=fct['desc'])
                    argsFct['function'] = fct['name']
                    argsFct['main-name'] = currentName
                    if 'default-args' in fct:
                        self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                    valMenu.addAction( QtHelper.createAction(self, fct['name'], self.addValidator,
                                        icon=QIcon(":/methods.png"), cb_arg=argsFct  ) )
                    valMenu.addSeparator()
                valsMenu.addMenu(valMenu)
                valsMenu.addSeparator()

        self.menu.addMenu( stepMenu )
        self.menu.addSeparator()
        self.menu.addAction( condAct )
        self.menu.addAction( labelAct )
        self.menu.addSeparator()
        self.menu.addMenu( tcMenu )
        self.menu.addMenu( tplsMenu )
        self.menu.addMenu( manipsMenu )
        self.menu.addMenu( valsMenu )
        self.menu.addSeparator()
        self.menu.addAction( self.addBreakpointAction )
        self.menu.addMenu( traceMenu )
        self.menu.addMenu( interactMenu )
        self.menu.addMenu( cacheMenu )
        self.menu.addMenu( timeMenu )
        self.menu.addMenu( storageMenu )
        self.menu.addSeparator()
        self.menu.addMenu( adpsMenu )
        self.menu.addMenu( libsMenu )
        self.menu.addSeparator()
        self.menu.addAction( self.deleteAction )
        self.menu.addAction( self.copyAction )
        self.menu.addAction( self.pasteAction )
        self.menu.addAction( self.reloadAction )
        self.menu.addSeparator()
   
        self.menu.popup( self.mapToGlobal(pos) )

    def addDefaultValues(self, defaultValues, currentFunction):
        """
        Add default values
        """
        for curArg in currentFunction['obj']:
            for k,v in defaultValues:
                if k == curArg['name']:
                    curArg['advanced'] = "True"
                    if curArg['type'] in ['strconstant', 'intconstant']:
                        curArg['default-value'] =  self.parseConstant(descr=curArg['descr'])
                    else:
                        curArg['default-value'] = unicode(v)

    def parseDocString(self, docstring):
        """
        Parse doc string
        """
        val = {}

        desc = docstring.strip()
        desc_splitted = desc.splitlines()
        
        val['return-value'] = "False"
        val['action-descr'] = desc.split("@param", 1)[0].strip()
        params = []
        param = {}
        
        for line in desc_splitted:
            line = line.strip() 
            if line.startswith('@param '):
                paramName = line.split(':', 1)[0].split('@param ')[1].strip()
                paramDescr = line.split(':', 1)[1].strip()
                param['name'] = paramName
                param['value'] = ''
                param['descr'] = paramDescr
                param['selected-type'] = ''
                param['advanced'] = "False"
            elif line.startswith('@type '):
                paramType = line.split(':', 1)[1].strip()
                param['type'] = paramType
                params.append( param )
                param = {}
            elif line.startswith('@return'):
                val['return-value'] = "True"
                val['return-descr'] = line.split(':', 1)[1].strip()
            else:   
                pass

        val['obj'] = params
        return val

    def parseConstant(self, descr):
        """
        Parse constant
        """
        tmpvals = descr.split("|")
        nameConstant = ''
        for zz in xrange(len(tmpvals)):
            if '(default)' in tmpvals[zz]:
                nameConstant = tmpvals[zz].split('(default)')[0].strip()
        return nameConstant 