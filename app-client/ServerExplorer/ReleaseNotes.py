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
Plugin release notes
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    from PyQt4.QtGui import (QTreeWidgetItem, QFont, QColor, QIcon, QWidget, QTabWidget, 
                            QVBoxLayout, QLabel, QPalette, QBrush, QTreeWidget, 
                            QFrame, QAbstractItemView)
    from PyQt4.QtCore import (Qt)
except ImportError:
    from PyQt5.QtGui import (QFont, QColor, QIcon, QPalette, QBrush)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QWidget, QTabWidget, QVBoxLayout, QLabel, 
                                QTreeWidget, QFrame, QAbstractItemView)
    from PyQt5.QtCore import (Qt)
    
from Libs import QtHelper, Logger
import Settings
import zlib

class KeyItem(QTreeWidgetItem):
    """
    Treewidget item for key
    """
    def __init__(self, key, parent = None, type = None ):
        """
        Constructs KeyItem widget item

        @param key:
        @type key: 

        @param parent:
        @type parent: 

        @param type:
        @type type: 
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.siz = len(key)
        self.setText( 0, unicode(key, "utf8") ) # wrap to str to support python3
        self.setKeyFont( type = type )

    def setKeyFont(self, type):
        """
        Set the font of the key

        @param type:
        @type type: 
        """
        font = QFont()
        if type == 2:
            font.setItalic(True)
            self.setFont( 0, font)
            
        elif type == 0 and self.siz > 0:
            self.setForeground(0, QColor(Qt.darkBlue) )
            self.setIcon(0, QIcon(":/dot.png") )

            font.setBold(True)
            self.setFont( 0, font)        
        else:
            self.setFont( 0, font) 

class WServerReleaseNote(QWidget, Logger.ClassLogger):
    """
    Widget for display all release notes
    """
    def __init__(self, parent = None):
        """
        Constructs WServerReleaseNote widget 

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Release Notes")
        self.createWidgets()
        self.deactivate()

    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.mainTab = QTabWidget()
        mainLayout = QVBoxLayout()
    
        self.toRead = QLabel( "%s" % "Release notes are specific to each version of the server, SUT adapters, libraries and toolbox. More details on each HISTORY files."  )

        mainLayout.addWidget(self.toRead)
        mainLayout.addWidget(self.mainTab)

        palette = QPalette()
        brush = QBrush(QColor(240, 240, 240))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)

        # treewidget for server rn
        self.rn = QTreeWidget(self)
        self.rn.setHeaderHidden(True)
        self.rn.setFrameShape(QFrame.NoFrame)
        self.rn.setSelectionMode(QAbstractItemView.NoSelection)
        self.rn.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.rn.setRootIsDecorated(False)
        self.rn.setPalette(palette)

        # treewidget for adapter rn
        self.rnAdp = QTreeWidget(self)
        self.rnAdp.setHeaderHidden(True)
        self.rnAdp.setFrameShape(QFrame.NoFrame)
        self.rnAdp.setSelectionMode(QAbstractItemView.NoSelection)
        self.rnAdp.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.rnAdp.setRootIsDecorated(False)
        self.rnAdp.setPalette(palette)

        # treewidget for library rn
        self.rnLibAdp = QTreeWidget(self)
        self.rnLibAdp.setHeaderHidden(True)
        self.rnLibAdp.setFrameShape(QFrame.NoFrame)
        self.rnLibAdp.setSelectionMode(QAbstractItemView.NoSelection)
        self.rnLibAdp.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.rnLibAdp.setRootIsDecorated(False)
        self.rnLibAdp.setPalette(palette)
        
        # treewidget for agent rn
        self.rnToolbox = QTreeWidget(self)
        self.rnToolbox.setHeaderHidden(True)
        self.rnToolbox.setFrameShape(QFrame.NoFrame)
        self.rnToolbox.setSelectionMode(QAbstractItemView.NoSelection)
        self.rnToolbox.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.rnToolbox.setRootIsDecorated(False)
        self.rnToolbox.setPalette(palette)

        self.mainTab.addTab( self.rn, Settings.instance().readValue( key = 'Common/acronym-server' )  )
        self.mainTab.addTab( self.rnAdp, "Sut Adapters" )
        self.mainTab.addTab( self.rnLibAdp, "Sut Librairies" )
        self.mainTab.addTab( self.rnToolbox, "Toolbox" )

        self.setLayout(mainLayout)

    def active (self):
        """
        Enables QTreeWidget
        Active all qwidget
        """
        self.rn.setEnabled(True)
        self.rnAdp.setEnabled(True)
        self.rnLibAdp.setEnabled(True)
        self.rnToolbox.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.rn.clear()
        self.rn.setEnabled(False)
        
        self.rnAdp.clear()
        self.rnAdp.setEnabled(False)

        self.rnLibAdp.clear()
        self.rnLibAdp.setEnabled(False)
        
        self.rnToolbox.clear()
        self.rnToolbox.setEnabled(False)

    def loadData (self, data, dataAdp, dataLibAdp, dataToolbox):
        """
        Dispatch data between tas tab and adapter tab

        @param data: 
        @type data:

        @param dataAdp: 
        @type dataAdp:

        @param dataProbes: 
        @type dataProbes:
        """
        # load server rn
        self.constructItem(parent=self.rn, data= data )

        # load adapters rn
        if not len(dataAdp): # dataAdp is false then adapters are not installed on the server
            emptyItem = KeyItem( key = b"", parent = self.rnAdp, type = 0)
            notInstalledItem = KeyItem( key = b"   Package adapters not installed on server", 
                                        parent = self.rnAdp, type = 1)
        else:
            try:
                self.constructItem(parent=self.rnAdp, data=dataAdp )
            except Exception as e:
                self.error( e )

        # load libraries rn
        if not len(dataLibAdp): # dataLibAdp is false then libraries are not installed on the server
            emptyItem = KeyItem( key = b"", parent = self.rnLibAdp, type = 0)
            notInstalledItem = KeyItem( key = b"   Package libraries not installed on server", 
                                        parent = self.rnLibAdp, type = 1)
        else:
            try:
                self.constructItem(parent=self.rnLibAdp, data=dataLibAdp )
            except Exception as e:
                self.error( e )
                
        # load toolbox rn
        if not len(dataToolbox): # dataToolbox is false then toolbox are not installed on the server
            emptyItem = KeyItem( key = b"", parent = self.rnToolbox, type = 0)
            notInstalledItem = KeyItem( key = b"   Package toolbox not installed on server", 
                                        parent = self.rnToolbox, type = 1)
        else:
            try:
                self.constructItem(parent=self.rnToolbox, data=dataToolbox )
            except Exception as e:
                self.error( e )

    def constructItem (self, parent, data):
        """
        Add items to tree widget

        @param data: 
        @type data:

        @param parent: 
        @type parent:
        """
        rootItem = None
        subItem = None
        for line in data.splitlines():
            if sys.version_info > (3,):
                line = bytes(line, 'utf8')
            if not line.startswith(b'\t'): # wrap to bytes for python 3 support
                rootItem = KeyItem( key = line, parent = parent, type = 0)
                rootItem.setExpanded(True)

            elif line.startswith(b'\t\t'): # wrap to bytes for python 3 support
                KeyItem( key = line[2:], parent = subItem, type = 2)

            elif line.startswith(b'\t'): # wrap to bytes for python 3 support
                subItem = KeyItem( key = line[1:], parent = rootItem, type = 1)
                subItem.setExpanded(True)

SI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return SI

def initialize (parent):
    """
    Initialize WServerReleaseNote widget
    """
    global SI
    SI = WServerReleaseNote(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global SI
    if SI:
        SI = None