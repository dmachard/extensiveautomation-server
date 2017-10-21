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
Releases notes dialog
"""

try:
    from PyQt4.QtGui import (QTreeWidgetItem, QFont, QColor, QIcon, QDialog, QVBoxLayout, QLabel, QTreeWidget, 
                            QFrame, QAbstractItemView, QPalette, QBrush, QHBoxLayout, QPushButton)
    from PyQt4.QtCore import (Qt, QSize)
except ImportError:
    from PyQt5.QtGui import (QFont, QColor, QIcon, QPalette, QBrush)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QDialog, QVBoxLayout, QLabel, QTreeWidget, 
                                QFrame, QAbstractItemView, QHBoxLayout, QPushButton)
    from PyQt5.QtCore import (Qt, QSize)
    
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
# FONT_NAME="courier"
# FONT_SIZE=8

class KeyItem(QTreeWidgetItem):
    """
    Key item
    """
    def __init__(self, key, parent = None, type = None ):
        """
        Constructs KeyItem widget item

        @param parent:
        @type parent: 
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.siz = len(key)
        self.setText( 0, key )
        self.setKeyFont( type = type )  

    def setKeyFont(self, type):
        """
        Set the font of the key
        """
        font = QFont()
        if type == 2:
            # font = QFont(FONT_NAME, FONT_SIZE)
            font.setItalic(True)
            self.setFont( 0, font)
        elif type == 0 and self.siz > 0:
            # self.setTextColor(0, QColor(Qt.darkBlue) )
            self.setForeground(0, QColor(Qt.darkBlue) )
            self.setIcon(0, QIcon(":/dot.png") )
            # font = QFont(FONT_NAME, FONT_SIZE)
            font.setBold(True)
            self.setFont( 0, font)          
        else:
            # font = QFont(FONT_NAME, FONT_SIZE)
            self.setFont( 0, font) 

class ReleaseNotesDialog(QDialog):
    """
    Release notes dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        
        self.name = dialogName
        self.createDialog()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( "%s %s" % (self.tr("Release Notes"), self.name) )
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)

        layout = QVBoxLayout()
        self.toRead = QLabel( "%s" % self.tr("Release notes of the application. More details in HISTORY.")  )
        layout.addWidget(self.toRead)

        self.rn = QTreeWidget(self)
        self.rn.setHeaderHidden(True)
        self.rn.setFrameShape(QFrame.NoFrame)
        self.rn.setSelectionMode(QAbstractItemView.NoSelection)
        self.rn.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.rn.setRootIsDecorated(False)

        palette = QPalette()
        brush = QBrush(QColor(240, 240, 240))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        self.rn.setPalette(palette)

        layout.addWidget(self.rn)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()

        self.closeButton = QPushButton( self.tr("Close"), self)
        self.closeButton.clicked.connect(self.reject)

        buttonLayout.addWidget(self.closeButton)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        
        # resise the window
        size = QSize(700, 500) 
        self.resize(size)

        
    def parseRn (self, text ):
        """
        Parse the release notes
        """
        rootItem = None
        subItem = None
        for line in text.splitlines():
            if not line.startswith('\t'):
                rootItem = KeyItem( key = line, parent = self.rn, type = 0)
                rootItem.setExpanded(True)
            elif line.startswith('\t\t'):
                KeyItem( key = line[2:], parent = subItem, type = 2)
            elif line.startswith('\t'):
                subItem = KeyItem( key = self.tr(line[1:]), parent = rootItem, type = 1)
                subItem.setExpanded(True)