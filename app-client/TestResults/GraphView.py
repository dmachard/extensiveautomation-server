#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive automation project
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
Module to display events logs in a flow chart
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QGraphicsLineItem, QColor, QGraphicsRectItem, QGraphicsTextItem, 
                            QPen, QBrush, QCursor, QWidget, QGraphicsScene, QGraphicsView, QPainter, 
                            QVBoxLayout, QTextEdit, QSplitter)
    from PyQt4.QtCore import (Qt)
except ImportError:
    from PyQt5.QtGui import (QColor, QPen, QBrush, QCursor, QPainter)
    from PyQt5.QtWidgets import (QGraphicsLineItem, QGraphicsRectItem, QGraphicsTextItem, 
                                QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout, 
                                QTextEdit, QSplitter)
    from PyQt5.QtCore import (Qt)

from Libs import QtHelper, Logger
import Settings

import math


class LineItem(QGraphicsLineItem ):
    """
    Line Item
    """
    def __init__(self, sourceItem, destItem, colorStr="#A5A2A5", arrowWidth=1  ):
        QGraphicsLineItem .__init__(self)

        color = QColor(0, 0, 0)
        color.setNamedColor( colorStr )
        
        self.arrowWidth = arrowWidth
        self.arrowColor = color

        self.sourceItem = sourceItem
        self.destItem = destItem
        
        self.setTestLine()
        
    def setTestLine(self):
        """
        Set the test line
        """        
        pos1 = self.sourceItem.scenePos()
        pos2 = self.destItem.scenePos()
        
        fromRect = self.sourceItem.rect()
        toRect = self.destItem.rect()
        
        h1 = fromRect.height()
        w1 = fromRect.width()
        h2 = toRect.height()
        w2 = toRect.width()
        
        self.setLine( pos1.x() + w1 / 2, pos1.y() + h1,  pos2.x() + w2 / 2, pos2.y() )
        
class TimestampItem(QGraphicsRectItem):
    """ 
    Represents a block in the diagram
    """
    def __init__(self, parent, name='Untitled', width=180, height=40):
        """
        Constructor
        """
        QGraphicsRectItem.__init__(self)

        self.parentWidget = parent

        if sys.version_info > (3,):
            if isinstance(name, bytes):
                name = str(name, "utf8", errors="ignore")
            
        self.label = QGraphicsTextItem(name, self)

        self.setColor(blockColor="#FFFFFF")

        self.changeSize(width, height)

    def setColor(self, blockColor):
        """
        Set color
        """
        color = QColor(0, 0, 0)
        color.setNamedColor( blockColor )
        self.setPen(QPen(color, 1))
        
        self.setBrush(QBrush(color))

    def changeSize(self, w, h):
        """
        Resize block function
        """
        # Limit the block size
        self.setRect(0.0, 0.0, w, h)

        # center label:
        rect = self.label.boundingRect()
        lw, lh = rect.width(), rect.height()
        lx = (w - lw) / 2
        ly = (h - lh) / 2
        self.label.setPos(lx, ly)

        return w, h

class BlockItem(QGraphicsRectItem):
    """ 
    Represents a block in the diagram
    """
    def __init__(self, parent, name='Untitled', width=180, 
                       height=40, blockColor="#A5A2A5", 
                       data=None, bold=False, italic=False, status=True):
        """
        Constructor
        """
        QGraphicsRectItem.__init__(self)

        self.parentWidget = parent
        self.internalData = data
        self.status = status
        
        color = QColor(0, 0, 0)
        color.setNamedColor( blockColor )
        self.setPen(QPen(color, 2)) 

        if sys.version_info > (3,) and isinstance(name, bytes): 
            name = str(name, "utf8", errors="ignore")
            
        self.label = QGraphicsTextItem(name, self)

        self.setFlags(self.ItemIsSelectable)    
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.changeSize(width, height)

    def setData(self, data):
        """
        Set data
        """
        self.internalData = data

    def setColor(self, blockColor):
        """
        Set color
        """
        color = QColor(0, 0, 0)
        color.setNamedColor( blockColor )
        self.setPen(QPen(color, 1))
        
        self.setBrush(QBrush(color))

    def changeSize(self, w, h):
        """
        Resize block function
        """
        # Limit the block size
        self.setRect(0.0, 0.0, w, h)

        # center label:
        rect = self.label.boundingRect()
        lw, lh = rect.width(), rect.height()
        lx = (w - lw) / 2
        ly = (h - lh) / 2
        self.label.setPos(lx, ly)

        return w, h
    
    def mouseReleaseEvent (self, event):
        """
        On mouse release event
        """
        if self.internalData is not None:
            data = self.internalData
            if isinstance(self.internalData, list):
                # [('Step 1', {'expected': 'result expected', 'action': 'step description', 
                # 'actual': 'success', 'result': 'PASS',
                # 'summary': 'step sample'}), ('%payload-v1%', {'raw': '', 
                # 'len': 0, 'time': 1421484488.314928})]
                data_tmp = self.internalData[0]
                data = "%s\n" % data_tmp[0]

                data += "\nSummary: %s" % data_tmp[1]['summary']

                data += "\n\nAction: %s" % data_tmp[1]['action']
                data += "\nExpected: %s" % data_tmp[1]['expected']

                data += "\n\nResult: %s" % data_tmp[1]['result']
                
                if 'actual' in data_tmp[1]:
                    data += "\nActual: %s" % data_tmp[1]['actual']

            self.parentWidget.logEdit.setText(data)
        else:
            self.parentWidget.logEdit.setText("")
            
class FlowChartView(QWidget):
    """
    Flowchart view
    """
    def __init__(self, parent):
        """
        Constructs FlowChartView widget 

        @param parent:
        @type parent: 
        """
        QWidget.__init__(self, parent)
        
        self.steps = []
        self.timestamps = []
        self.arrows = []
        
        self.createWidget()
    
    def createWidget(self):
        """
        Create the widget
        """
        self.diagramScene = QGraphicsScene(self)

        self.view = QGraphicsView(self.diagramScene)
        
        self.view.setRenderHint(QPainter.Antialiasing)

        # set the main layout
        layout = QVBoxLayout()
  
        self.logEdit = QTextEdit() 
        self.logEdit.setReadOnly(True)
        
        hSplitter2 = QSplitter(self)
        hSplitter2.setOrientation(Qt.Vertical)
        
        
        hSplitter2.addWidget( self.view )
        hSplitter2.addWidget( self.logEdit )
        
        hSplitter2.setStretchFactor(0, 1)
        
        layout.addWidget(hSplitter2)
        self.setLayout(layout)

    def reset(self):
        """
        Clear all 
        """
        #self.diagramScene.clear()
  
        for stp in self.steps:
            self.diagramScene.removeItem(stp)

        for stp in self.arrows:
            self.diagramScene.removeItem(stp)
            
        for stamp in self.timestamps:
            self.diagramScene.removeItem(stamp)
            
        self.diagramScene.clear()
        self.diagramScene.update()
        self.view.resetCachedContent()

        self.steps = []
        self.arrows = []
        self.timestamps = []
        self.logEdit.setText("")
        
    def addStep(self, text, color="#A5A2A5", width=400, height=40, data=None, 
                      textBold=False, textItalic=False, timestamp="00:00:00"):
        """
        Add step
        """
        # take the last one
        if len(self.steps):
            latestBlock = self.steps[-1:][0]
        else:
            latestBlock = None
        
        newBlock = BlockItem(self, text, blockColor=color, width=width, 
                             height=height, data=data, bold=textBold, 
                             italic=textItalic)
        if width == 100:
            newBlock.setPos( 400/2 - 100/2, len(self.steps) * 80 )
        elif width == 300:
            newBlock.setPos( 400/2 - 300/2, len(self.steps) * 80 )
        else:
            newBlock.setPos(0, len(self.steps) * 80 )
        
        self.steps.append( newBlock )
        self.diagramScene.addItem(newBlock)
        
        newTimestampBlock = TimestampItem(self, timestamp)
        newTimestampBlock.setPos(-200, len(self.timestamps) * 80 )
        
        self.timestamps.append( newTimestampBlock )
        self.diagramScene.addItem(newTimestampBlock)
        
        if latestBlock is not None:
            newArrow = LineItem(latestBlock, newBlock)
            self.diagramScene.addItem(newArrow)
            self.arrows.append( newArrow )
        
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-scrolling-graph' ) ):
            self.view.centerOn(newBlock)
        return newBlock
        