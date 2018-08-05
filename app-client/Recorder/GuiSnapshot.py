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
Recorder Snapshot extension for the extensive client
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QDialog, QDesktopWidget, QApplication, QRubberBand, 
                            QVBoxLayout, QLabel, QPixmap, QWidget, QHBoxLayout)
    from PyQt4.QtCore import (Qt, QRect)
except ImportError:
    from PyQt5.QtGui import (QPixmap)
    from PyQt5.QtWidgets import (QDialog, QDesktopWidget, QApplication, QRubberBand, 
                                QVBoxLayout, QLabel, QWidget, QHBoxLayout)
    from PyQt5.QtCore import (Qt, QRect)
    
from Libs import QtHelper, Logger

"""
Capture desktop
"""
class DSnapshot(QDialog):
    """
    Snapshot dialog
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)

        self.state = 0
        
        self.posX = 0
        self.posY = 0
        self.posW = 0
        self.posH = 0
        
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # maximize window
        screen = QDesktopWidget().screenGeometry()        
        self.setGeometry(screen)


        # set cross cursor
        self.setCursor(Qt.CursorShape(Qt.CrossCursor))

        # display        
        self.show()

        # create rubberband
        self.rb = QRubberBand(QRubberBand.Rectangle)
        self.rb.setWindowOpacity(0.4) # new in v18, to support pyqt5 properly
        
        self.snapshotResult = None
        
        layout = QVBoxLayout()

        self.backgroundLabel = QLabel()
        layout.addWidget(self.backgroundLabel) 
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout) 

    def setBackground(self, pixmap):
        """
        Set background
        """
        self.backgroundLabel.setPixmap(pixmap)
  
    def mousePressEvent(self,ev):
        """
        On mouse press event
        """
        if ev.button() != Qt.LeftButton:
            self.abort()
            
        if self.state == 0:        
            self.state = 1                        
            self.origin = ev.globalPos()
         
            self.rb.setGeometry(QRect(self.origin,ev.globalPos()).normalized())
            self.rb.show()
    
    def mouseMoveEvent(self,ev):
        """
        On mouse move event
        """
        if self.state == 1:
            self.rb.setGeometry(QRect(self.origin,ev.globalPos()).normalized())
    
    def mouseReleaseEvent(self,ev):
        """
        On mouse release event
        """
        if self.state == 1:
            self.state = 2
            self.end = ev.globalPos()        
            self.rb.hide()
            self.doSnip()
   
    def keyPressEvent(self, ev):
        """
        On key press event
        """
        if ev.key() == Qt.Key_Escape: 
            self.abort()
    
    def doSnip(self):   
        """
        Do snip
        """
        x = min(self.origin.x(),self.end.x())
        y = min(self.origin.y(),self.end.y())
        w = abs(self.origin.x() - self.end.x())
        h = abs(self.origin.y() - self.end.y())
        
        self.posX = x
        self.posY = y
        self.posW = w
        self.posH = h
        
        self.hide()
        if QtHelper.IS_QT5:
            pixmap = self.backgroundLabel.grab( QRect(x,y,w,h) )
        else:
            pixmap = QPixmap.grabWidget(self.backgroundLabel,x,y,w,h)

        self.snapshotResult = pixmap
        self.accept()
    
    def getSnapshot(self):
        """
        Return snapshot as pixmap
        """
        return self.snapshotResult
    
    def getLocation(self):
        """
        Return snapshot as pixmap
        """
        return (self.posX, self.posY, self.posW, self.posH)

    def abort(self):
        """
        close both windows and exit program
        """
        pass
        
"""
Capture mouse position
"""
class QLabelMouse (QLabel):
    """
    Label widget for mouse coordinate
    """
    def __init__ (self, parent = None):
        """
        Constructor
        """
        super(QLabelMouse, self).__init__(parent)
        
        self.dialog = parent

        self.setMouseTracking(True)
        self.setTextLabelPosition(0, 0)
        self.setAlignment(Qt.AlignCenter)

    def mouseMoveEvent (self, event):
        """
        On mouse move event
        """
        self.setTextLabelPosition(event.x(), event.y())
        QWidget.mouseMoveEvent(self, event)

    def mousePressEvent (self, event):
        """
        On mouse press event
        """
        if event.button() == Qt.LeftButton:
            self.posX = self.x
            self.posY = self.y
            
            QWidget.mousePressEvent(self, event)
            self.dialog.capture()
        else:
            QWidget.mousePressEvent(self, event)

    def keyPressEvent(self, event):
        """
        On key press event
        """
        if event.key() == Qt.Key_Escape: 
            self.abort()
            
    def setTextLabelPosition (self, x, y):
        """
        Set the position on the label
        """
        self.x, self.y = x, y
        self.setText('Please click on screen ( %d : %d )' % (self.x, self.y))

class DCaptureMouse(QDialog):
    """
    Dialog for capture the mouve position
    """
    def __init__ (self, parent = None):
        """
        Constructor
        """
        super(DCaptureMouse, self).__init__(parent)
        self.setWindowOpacity(0.7)

        self.posLabel = QLabelMouse(self)

        layoutQHBoxLayout = QHBoxLayout()
        layoutQHBoxLayout.addWidget(self.posLabel)
        layoutQHBoxLayout.setMargin(0)
        layoutQHBoxLayout.setSpacing(0)
        self.setLayout(layoutQHBoxLayout)
        self.showFullScreen()
        
    def keyPressEvent(self, ev):
        """
        On key press event
        """
        if ev.key() == Qt.Key_Escape: 
            self.abort()
            
    def capture(self):
        """
        Capture the possition and close the dialog
        """
        self.accept()
        
    def abort(self):
        """
        close both windows and exit program
        """
        pass
        