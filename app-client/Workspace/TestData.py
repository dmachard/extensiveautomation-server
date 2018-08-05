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
Test data module
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QVBoxLayout, QApplication)
except ImportError:
    from PyQt5.QtWidgets import (QVBoxLayout, QApplication)
    
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
    import FileModels.TestData as FileModelTestData
except ImportError: # python3 support
    from .FileModels import TestData as FileModelTestData
import Settings

TYPE = 'tdx'

class WTestData(Document.WDocument):
    """
    Test data widget
    """
    TEST_DATA_EDITOR = 0
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
        Document.WDocument.__init__(self, parent, path, filename, extension, 
                                    nonameId, remoteFile, repoDest, project, isLocked)
        
        # prepare data model
        userName = Settings.instance().readValue( key = 'Server/last-username' )
        self.dataModel = FileModelTestData.DataModel(userName=userName)
        
        # create widget
        self.createWidgets()
        self.createConnections()    
    
    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.srcWidget = EditorWidget( editorId=self.TEST_DATA_EDITOR, title="Test Data:", parent=self, 
                                        activePyLexer=False, activePropertiesLexer=True )
        self.srcEditor = self.srcWidget.editor

        layout = QVBoxLayout()
        layout.addWidget(self.srcWidget)
        layout.setContentsMargins(2,0,0,0)
        
        self.setLayout(layout)

    def createConnections (self):
        """
        QtSignals connection
        """
        self.srcEditor.FocusChanged.connect( self.focusChanged )
        self.srcEditor.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.srcEditor.textChanged.connect(self.setModify)
        self.srcEditor.textChanged.connect(self.updateTotalLines)

    def viewer(self):
        """
        return the document viewer
        """
        return self.parent
       
    def editor(self):
        """
        Return the editor
        """
        return self.srcEditor
        
    def setWrappingMode(self, wrap):
        """
        Set wrap mode
        """
        self.srcEditor.setWrappingMode(wrap=wrap)
        
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

    def activeXmlLexer(self):
        """
        Active XML lexer
        """
        self.srcEditor.activeXmlLexer()

    def deactiveXmlLexer(self):
        """
        Deactive XML lexer
        """
        self.srcEditor.activeIniLexer()

    def setFolding (self, fold):
        """
        Active or deactivate the code folding
        
        @param fold: 
        @type fold: boolean
        """
        if fold:
            self.srcEditor.activeFolding(fold)
        else:
            self.srcEditor.activeFolding(fold)
    
    def setLinesNumbering (self, visible):
        """
        Active or deactivate the lines numbering
        
        @param visible: 
        @type visible: boolean
        """
        if visible:
            self.srcEditor.setMarginLineNumbers(1, visible)
            self.srcEditor.onLinesChanged()
        else:
            self.srcEditor.setMarginLineNumbers(1, visible)
            self.srcEditor.setMarginWidth(1, 0)

    def setWhitespaceVisible (self, visible):
        """
        Active or deactivate the whitespace visibility
        
        @param visible: 
        @type visible: boolean
        """
        if visible:
            self.srcEditor.setWhitespaceVisible(visible)
        else:
            self.srcEditor.setWhitespaceVisible(visible)

    def setIndentationGuidesVisible (self, visible):
        """
        Active or deactivate indentation guides visibility
        
        @param visible: 
        @type visible: boolean
        """
        if visible:
            self.srcEditor.setIndentationGuidesVisible(visible)
        else:
            self.srcEditor.setIndentationGuidesVisible(visible)

    def currentEditor (self):
        """
        Returns the editor that has the focus

        @return: Focus editor 
        @rtype: PyEditor
        """
        weditor = QApplication.focusWidget()
        if isinstance(weditor, PyEditor):
            if weditor.editorId == self.TEST_DATA_EDITOR:
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
            if weditor.editorId == self.TEST_DATA_EDITOR:
                self.viewer().findWidget.setEditor( editor = self.srcEditor)

            self.viewer().FocusChanged.emit(self)
            
    def setDefaultCursorPosition(self):
        """
        Set the default cursor position
        """
        self.srcEditor.setFocus()
        self.srcEditor.setCursorPosition(0,0)

    def defaultLoad (self):
        """
        Load default empty script
        """
        self.srcEditor.setText( "" )
        self.srcEditor.setFocus()
        self.setReadOnly( readOnly=False )

    def load (self, content=None):
        """
        Open file
        """
        if content is not None:
            res =  self.dataModel.load( rawData = content )
        else:
            absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
            res = self.dataModel.load( absPath = absPath )
        if res:
            self.srcEditor.setText( self.dataModel.testdata )
            self.srcEditor.setFocus()
            self.setReadOnly( readOnly=False )
        return res

    def write (self, force = False ):
        """
        Save the data model to file

        @param force: 
        @type force: boolean
        """
        # update data model
        self.dataModel.setTestData( testData=self.srcEditor.text() )

        if not force:
            if not self.isModified():
                return False
        
        saved = self.dataModel.write( absPath='%s/%s.%s' % (self.path, 
                                                            self.filename, 
                                                            self.extension) )
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
        self.dataModel.setTestData( testData=self.srcEditor.text() )

        # return raw file
        return self.dataModel.getRaw()