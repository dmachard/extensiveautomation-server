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
Test suite module
"""

import sys
import json

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QMessageBox, QVBoxLayout, QSplitter, QApplication)
    from PyQt4.QtCore import (Qt)
except ImportError:
    from PyQt5.QtWidgets import (QMessageBox, QVBoxLayout, QSplitter, QApplication)
    from PyQt5.QtCore import (Qt)
    
from Libs import QtHelper, Logger
try:
    from PythonEditor import PyEditor
    from PythonEditor import EditorWidget
except ImportError: # python3 support
    from .PythonEditor import PyEditor
    from .PythonEditor import EditorWidget
try:
    import Document
except ImportError: # python3 support
    from . import Document
try:
    import FileModels.TestSuite as FileModelTestSuite
except ImportError: # python3 support
    from .FileModels import TestSuite as FileModelTestSuite
    
import Settings
import DefaultTemplates

TYPE = 'tsx'

class WTestSuite(Document.WDocument):
    """
    Test suite widget
    """
    TEST_DEF_EDITOR = 0
    TEST_EXEC_EDITOR = 1
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
        """
        Document.WDocument.__init__(self, parent, path, filename, extension, nonameId, remoteFile, repoDest, project, isLocked)
        
        self.srcEditor = None
        self.execEditor = None
        # prepare model with default value
        userName = Settings.instance().readValue( key = 'Server/last-username' )
        defaultTemplates = DefaultTemplates.Templates()
        testdef = defaultTemplates.getTestDefinition()
        testexec = defaultTemplates.getTestExecution()
        if not 'default-library' in Settings.instance().serverContext:
            if not Settings.instance().offlineMode:
                QMessageBox.critical(self, "Open" , 
                        "Server context incomplete (default library is missing), please to reconnect!")
            defLibrary = 'v000'
        else:
            defLibrary = Settings.instance().serverContext['default-library']
        if not 'default-adapter' in Settings.instance().serverContext:
            if not Settings.instance().offlineMode:
                QMessageBox.critical(self, "Open" , 
                        "Server context incomplete (default adapter is missing), please to reconnect!")
            defAdapter = 'v000'
        else:
            defAdapter = Settings.instance().serverContext['default-adapter']
           
        # new in v17
        defaultTimeout = Settings.instance().readValue( key = 'TestProperties/default-timeout' )
        
        _defaults_inputs = []
        _defaults_outputs = []
        try:
            defaultInputs = Settings.instance().readValue( key = 'TestProperties/default-inputs')
            _defaults_inputs = json.loads(defaultInputs)
        except Exception as e:
            self.error("bad default inputs provided: %s - %s" % (e,defaultInputs))
        try:
            defaultOutputs = Settings.instance().readValue( key = 'TestProperties/default-outputs')
            _defaults_outputs = json.loads(defaultOutputs)
        except Exception as e:
            self.error("bad default outputs provided: %s - %s" % (e,defaultOutputs))
        # end of new
        
        self.dataModel = FileModelTestSuite.DataModel(userName=userName, testDef=testdef, testExec=testexec,
                                                    defLibrary=defLibrary, defAdapter=defAdapter, 
                                                    timeout=defaultTimeout, inputs=_defaults_inputs, 
                                                     outputs=_defaults_outputs)

        self.createWidgets()
        self.createConnections()    
    
    def createWidgets (self):
        """
        QtWidgets creation
         _______________________
        |                       |
        |       PyEditor        |
        |_______________________|
        |________QSplitter______|
        |                       |
        |       PyEditor        |
        |_______________________|
        """
        self.srcWidget = EditorWidget( self.TEST_DEF_EDITOR, "Test Definition:", self,
                                        wrappingText=QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/code-wrapping' ) ) )
        self.execWidget = EditorWidget( self.TEST_EXEC_EDITOR, "Test Execution:",  self,
                                        wrappingText=QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/code-wrapping' ) ),
                                        toolbar=False)
        
        self.srcEditor = self.srcWidget.editor
        self.execEditor = self.execWidget.editor

        layout = QVBoxLayout()

        hSplitter = QSplitter(self)
        hSplitter.setOrientation(Qt.Vertical)

        hSplitter.addWidget(self.srcWidget)
        hSplitter.addWidget(self.execWidget)
        hSplitter.setContentsMargins(0,0,0,0)
        hSplitter.setStretchFactor(0, 1)

        layout.addWidget(hSplitter)
        layout.setContentsMargins(2,0,0,0)
        
        self.setLayout(layout)
    
    def createConnections (self):
        """
        QtSignals connection
        """
        self.srcEditor.FocusChanged.connect( self.focusChanged )
        self.execEditor.FocusChanged.connect( self.focusChanged )
        
        self.srcEditor.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.execEditor.cursorPositionChanged.connect(self.onCursorPositionChanged)

        self.srcEditor.textChanged.connect(self.setModify)
        self.execEditor.textChanged.connect(self.setModify)

        self.srcEditor.textChanged.connect(self.updateTotalLines)
        self.execEditor.textChanged.connect(self.updateTotalLines)
    
    def viewer(self):
        """
        return the document viewer
        """
        return self.parent
        
    def updateTotalLines(self):
        """
        On total lines changed
        """
        self.viewer().TotalLinesChanged.emit( self.editor().lines() )
        
    def onCursorPositionChanged (self , ln, col):
        """
        Emit signal from parent to update the position of the cursor
        
        @param ln: line index
        @type ln: Integer

        @param col: column index
        @type col: Integer
        """
        self.viewer().CursorPositionChanged.emit( ln, col )

    def setDefaultCursorPosition(self):
        """
        Set the default cursor position
        """
        self.srcEditor.setFocus()
        self.srcEditor.setCursorPosition(0,0)

    def setWrappingMode(self, wrap):
        """
        Set wrap mode
        """
        self.srcEditor.setWrappingMode(wrap=wrap)
        self.execEditor.setWrappingMode(wrap=wrap)

    def foldAll(self):
        """
        Fold all
        """
        self.srcEditor.foldAllLines()
        self.execEditor.foldAllLines()

    def setFolding (self, fold):
        """
        Active or deactivate the code folding
        
        @param fold: 
        @type fold: boolean
        """
        if fold:
            self.srcEditor.activeFolding(fold)
            self.execEditor.activeFolding(fold)
        else:
            self.srcEditor.activeFolding(fold)
            self.execEditor.activeFolding(fold)

    def setLinesNumbering (self, visible):
        """
        Active or deactivate the lines numbering
        
        @param visible: 
        @type visible: boolean
        """
        if visible:
            self.srcEditor.setMarginLineNumbers(1, visible)
            self.srcEditor.onLinesChanged()
            self.execEditor.setMarginLineNumbers(1, visible)
            self.execEditor.onLinesChanged()
        else:
            self.srcEditor.setMarginLineNumbers(1, visible)
            self.srcEditor.setMarginWidth(1, 0)
            self.execEditor.setMarginLineNumbers(1, visible)
            self.execEditor.setMarginWidth(1, 0)

    def setWhitespaceVisible (self, visible):
        """
        Active or deactivate the whitespace visibility
        
        @param visible: 
        @type visible: boolean
        """
        if visible:
            self.srcEditor.setWhitespaceVisible(visible)
            self.execEditor.setWhitespaceVisible(visible)
        else:
            self.srcEditor.setWhitespaceVisible(visible)
            self.execEditor.setWhitespaceVisible(visible)

    def setIndentationGuidesVisible (self, visible):
        """
        Active or deactivate indentation guides visibility
        
        @param visible: 
        @type visible: boolean
        """
        if visible:
            self.srcEditor.setIndentationGuidesVisible(visible)
            self.execEditor.setIndentationGuidesVisible(visible)
        else:
            self.srcEditor.setIndentationGuidesVisible(visible)
            self.execEditor.setIndentationGuidesVisible(visible)

    def editor(self):
        """
        Return the current editor
        """
        return self.currentEditor()
        
    def currentEditor (self):
        """
        Returns the editor that has the focus

        @return: Focus editor 
        @rtype: PyEditor
        """
        weditor = QApplication.focusWidget()
        if isinstance(weditor, PyEditor):
            if weditor.editorId == self.TEST_DEF_EDITOR:
                return self.srcEditor
            elif weditor.editorId == self.TEST_EXEC_EDITOR:
                return self.execEditor
            else:
                return self.srcEditor
        else:
            return self.srcEditor

    def focusChanged (self):
        """
        Called when focus on editors
        Emit the signal "focusChanged"
        """
        weditor = QApplication.focusWidget()
        if isinstance(weditor, PyEditor):
            if weditor.editorId == self.TEST_DEF_EDITOR:
                self.viewer().findWidget.setEditor( editor = self.srcEditor)
            if weditor.editorId == self.TEST_EXEC_EDITOR:
                self.viewer().findWidget.setEditor( editor = self.execEditor)

            self.viewer().FocusChanged.emit(self)

    def defaultLoad (self, testDef=None, testExec=None, testInputs=None, testOutputs=None, testAgents=None):
        """
        Load default empty script
        """
        if testDef is not None:
            self.srcEditor.setText( testDef )
        else:
            self.srcEditor.setText( self.dataModel.testdef )
        self.srcEditor.setFocus()
        if testExec is not None:
            self.execEditor.setText( testExec )
        else:
            self.execEditor.setText( self.dataModel.testexec )
        
        if testInputs is not None:
            self.dataModel.properties['properties']['inputs-parameters']['parameter'].extend( testInputs )
        if testOutputs is not None:
            self.dataModel.properties['properties']['outputs-parameters']['parameter'].extend( testOutputs )
        if testAgents is not None:
            self.dataModel.properties['properties']['agents']['agent'].extend( testAgents )

        self.setReadOnly( readOnly=False )

    def load (self, content=None):
        """
        Open file and contruct the data model
        """
        if content is not None:
            res =  self.dataModel.load( rawData = content )
        else:
            absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
            res = self.dataModel.load( absPath = absPath )
        if res:
            self.srcEditor.setText( self.dataModel.testdef )
            self.srcEditor.setFocus()
            self.execEditor.setText( self.dataModel.testexec )
            self.setReadOnly( readOnly=False )
        return res

    def write (self, force = False ):
        """
        Save the data model to file
        """
        # update data model
        self.dataModel.setTestDef( testDef=self.srcEditor.text() )
        self.dataModel.setTestExec( testExec=self.execEditor.text() )

        # if not forced and no change in the document, do nothing and return
        if not force:
            if not self.isModified():
                return False

        saved = self.dataModel.write( absPath='%s/%s.%s' % (self.path, self.filename, self.extension) )
        if saved:
            self.setUnmodify()
            return True
        else:
            self.path = None
            return None

    def getraw_encoded(self):
        """
        Returns raw data encoded
        """
        # update data model
        self.dataModel.setTestDef( testDef=self.srcEditor.text() )
        self.dataModel.setTestExec( testExec=self.execEditor.text() )

        # return raw file
        return self.dataModel.getRaw()