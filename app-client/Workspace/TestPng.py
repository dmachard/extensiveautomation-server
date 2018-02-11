#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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
Test png module
"""

import base64
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QIcon, QToolBar, QLabel, QPalette, QSizePolicy, QScrollArea, 
                            QFont, QVBoxLayout, QImage, QPixmap)
    from PyQt4.QtCore import (QSize, QFile, QIODevice)
except ImportError:
    from PyQt5.QtGui import (QIcon, QPalette, QFont, QImage, QPixmap)
    from PyQt5.QtWidgets import (QToolBar, QLabel, QSizePolicy, QScrollArea, QVBoxLayout)
    from PyQt5.QtCore import (QSize, QFile, QIODevice)
    
from Libs import QtHelper, Logger

try:
    import Document
except ImportError: # python3 support
    from . import Document
import UserClientInterface as UCI


TYPE = 'png'

class WTestPng(Document.WDocument):
    """
    Test png widget
    """
    def __init__(self, parent = None, path = None, filename = None, extension = None, 
                    nonameId = None, remoteFile=True, repoDest=None, project=0):
        """
        Constructs WScript widget

        @param parent: 
        @type parent: 

        @param path: 
        @type path: 

        @param filename: 
        @type filename: 

        @param extension: 
        @type extension: 

        @param nonameId: 
        @type nonameId: 
        """
        Document.WDocument.__init__(self, parent,path, filename, extension, nonameId, remoteFile, repoDest, project)
        self.scaleFactor = 0.0
        self.rawContent = ''
        self.createWidgets()
        self.createActions()
        self.createToolbar()
        self.createConnections()    
    
    def createActions(self):
        """
        Create qt actions
        """
        self.zoomInAct = QtHelper.createAction(self, "&Zoom &In (25%.", self.zoomIn, 
                                                icon=QIcon(":/zoom-in.png") ) 
        self.zoomOutAct = QtHelper.createAction(self, "Zoom &Out (25%.", self.zoomOut, 
                                                icon=QIcon(":/zoom-out.png") ) 
        self.normalSizeAct = QtHelper.createAction(self, "&Normal Size", self.normalSize, 
                                                   icon=QIcon(":/zoom-normal.png") ) 

    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|------|||
        || Open | Save |||
        ||------|------|||
        """
        self.dockToolbar.setObjectName("Test Config toolbar")
        self.dockToolbar.addAction(self.zoomInAct)
        self.dockToolbar.addAction(self.zoomOutAct)
        self.dockToolbar.addAction(self.normalSizeAct)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))
    
    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border


        self.imageLabel = QLabel(self)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

        title = QLabel("Image:")
        title.setStyleSheet("QLabel { padding-left: 2px; padding-top: 2px }")
        font = QFont()
        font.setBold(True)
        title.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.dockToolbar)
        layout.addWidget(self.scrollArea)
        layout.setContentsMargins(2,2,2,2)
        self.setLayout(layout)

    def zoomIn(self):
        """
        Zoom in
        """
        self.scaleImage(1.25)

    def zoomOut(self):
        """
        Zoom out
        """
        self.scaleImage(0.8)

    def normalSize(self):
        """
        Normal size
        """
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def scaleImage(self, factor):
        """
        Scale image
        """
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

    def adjustScrollBar(self, scrollBar, factor):
        """
        Adjust scrollbar
        """
        scrollBar.setValue(int(factor * scrollBar.value()  + ((factor - 1) * scrollBar.pageStep()/2)))
                            
    def createConnections (self):
        """
        QtSignals connection
        """
        pass

    def write (self, force = False ):
        """
        Save 
        """
        absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
        try:
            with open( absPath, mode='wb') as myfile:
                myfile.write(self.rawContent)
        except Exception as e:
            self.error("unable to write png file: %s" % e)
            return None
        else:
            self.setUnmodify()
            return True


    def load (self, content=None):
        """
        Open file
        """
        if content is None:
            absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
            file = QFile(absPath)
            if not file.open(QIODevice.ReadOnly):
                self.error( "Error opening image file: %s" %  absPath)
                return False
            else:
                content= file.readAll()

        self.rawContent = content
        image = QImage()
        image.loadFromData(content)
        if image.isNull():
            self.error( "cannot load image" )
            return False
        else:
            self.imageLabel.setPixmap(QPixmap.fromImage(QImage(image)))
            self.scaleFactor = 1.0
            self.imageLabel.adjustSize()

            return True

    def getraw_encoded(self):
        """
        Returns raw data encoded
        """
        encoded = ''
        try:
            encoded = base64.b64encode(self.rawContent)
        except Exception as e:
            self.error( 'unable to encode raw image: %s' % str(e) )
        return encoded

