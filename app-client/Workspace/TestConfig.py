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
Test config module
"""

import sys
import json

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
import zlib
import base64

try:
    from PyQt4.QtGui import (QToolBar, QLabel, QFont, QVBoxLayout, QGroupBox, QHBoxLayout)
    from PyQt4.QtCore import (QSize, Qt)
except ImportError:
    from PyQt5.QtGui import (QFont)
    from PyQt5.QtWidgets import (QToolBar, QLabel, QVBoxLayout, QGroupBox, QHBoxLayout)
    from PyQt5.QtCore import (QSize, Qt)
    
from Libs import QtHelper, Logger

try:
    import Document
except ImportError: # python3 support
    from . import Document
try:
    import FileModels.TestConfig as FileModelTestConfig
except ImportError: # python3 support
    from .FileModels import TestConfig as FileModelTestConfig
    
import Settings

try:
    import DocumentProperties.Parameters as TestParameters
except ImportError: # python3 support
    from .DocumentProperties import Parameters as TestParameters
    
TYPE = 'tcx'

class WTestConfig(Document.WDocument):
    """
    Test config widget
    """
    def __init__(self, parent = None, path = None, filename = None, extension = None, 
                    nonameId = None, remoteFile=False, repoDest=None, project=0, isLocked=False):
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

        @param remoteFile: is remote
        @type remoteFile: boolean
        """
        Document.WDocument.__init__(self, parent, path, filename, extension, nonameId, remoteFile, repoDest, project, isLocked)
        
        self.tc = TestParameters.ParametersQWidget(self, forTestConfig=True)
        
        # new in v17
        defaultTimeout = Settings.instance().readValue( key = 'TestProperties/default-timeout' )
        
        _defaults_params = []
        try:
            defaultInputs = Settings.instance().readValue( key = 'TestProperties/default-inputs')
            _defaults_params = json.loads(defaultInputs)
        except Exception as e:
            self.error("bad default inputs provided: %s - %s" % (e,defaultInputs))
        # end of new
        
        self.dataModel = FileModelTestConfig.DataModel(timeout=defaultTimeout, parameters=_defaults_params)

        self.createWidgets()
        self.createToolbar()
        self.createConnections()    
        
    
    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarClipboard = QToolBar(self)
        self.dockToolbarClipboard.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarClipboard.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.clipBox = QGroupBox("Clipboard")
        self.clipBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutClipBox = QHBoxLayout()
        layoutClipBox.addWidget(self.dockToolbarClipboard)
        layoutClipBox.setContentsMargins(0,0,0,0)
        self.clipBox.setLayout(layoutClipBox)
        
        self.paramsBox = QGroupBox("Parameters")
        self.paramsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutParamBox = QHBoxLayout()
        layoutParamBox.addWidget(self.dockToolbar)
        layoutParamBox.setContentsMargins(0,0,0,0)
        self.paramsBox.setLayout(layoutParamBox)
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.paramsBox)
        layoutToolbars.addWidget(self.clipBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        title = QLabel("Test Config:")
        title.setStyleSheet("QLabel { padding-left: 2px; padding-top: 2px }")
        font = QFont()
        font.setBold(True)
        title.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(layoutToolbars)
        layout.addWidget(self.tc)
        layout.setContentsMargins(0,0,0,0)
        
        self.setLayout(layout)
    
    def createConnections (self):
        """
        QtSignals connection
        """
        self.tc.table().DataChanged.connect(self.setModify)

    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|------|||
        || Open | Save |||
        ||------|------|||
        """
        self.dockToolbar.setObjectName("Test Config toolbar")
        self.dockToolbar.addAction(self.tc.table().addAction)
        self.dockToolbar.addAction(self.tc.table().delAction)
        self.dockToolbar.addAction(self.tc.table().clearAction)
        self.dockToolbar.addAction(self.tc.table().openAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.tc.table().colorsAction)
        self.dockToolbar.setIconSize(QSize(16, 16))
        
        self.dockToolbarClipboard.setObjectName("Clipboard toolbar")
        self.dockToolbarClipboard.addAction(self.tc.table().copyAction)
        self.dockToolbarClipboard.addAction(self.tc.table().pasteAction)
        self.dockToolbarClipboard.addAction(self.tc.table().undoAction)
        self.dockToolbarClipboard.setIconSize(QSize(16, 16))
        
    def defaultLoad (self):
        """
        Default load
        """
        self.setReadOnly( readOnly=False )
        self.tc.table().loadData(data=self.dataModel.properties['properties']['parameters']) 

    def load (self, content=None):
        """
        Open file and contruct the data model from file or directly with data

        @param content:
        @type content:
        """
        if content is not None:
            res =  self.dataModel.load( rawData = content )
        else:
            absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
            res = self.dataModel.load( absPath = absPath )
        if res:
            self.setReadOnly( readOnly=False )
            self.tc.table().loadData(data=self.dataModel.properties['properties']['parameters']) 
        return res

    def write (self, force = False, fromExport=False):
        """
        Write data to file, data are compressed 

        @param force:
        @type force: boolean

        @param fromExport:
        @type fromExport: boolean
        """
        if not force:
            if not self.isModified():
                return False

        saved = self.dataModel.write( absPath='%s/%s.%s' % (self.path, self.filename, self.extension) )
        if saved:
            if not fromExport:
                self.setUnmodify()
            return True
        else:
            self.path = None
            return None
    
    def getraw_encoded(self):
        """
        Return raw data encoded in base64
        """
        return self.dataModel.getRaw()