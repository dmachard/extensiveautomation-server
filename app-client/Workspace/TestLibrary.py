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
Test library module
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
import UserClientInterface as UCI
import DefaultTemplates


import base64

TYPE = 'py'

class WTestLibrary(Document.WDocument):
    """
    Test library widget
    """
    TEST_LIBRARY_EDITOR = 0
    def __init__(self, parent = None, path = None, filename = None, extension = None,
                    nonameId = None, remoteFile=True, repoDest=None, project=0, isLocked=False):
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
        self.srcWidget = EditorWidget( editorId=self.TEST_LIBRARY_EDITOR, title="Library Definition:", parent=self )
        self.srcEditor = self.srcWidget.editor

        layout = QVBoxLayout()
        layout.addWidget(self.srcWidget)
        layout.setContentsMargins(2,0,0,0)
        
        self.setLayout(layout)
    
    def createConnections (self):
        """
        QtSignals connection
        """
        # self.connect(self.srcEditor, SIGNAL("focusChanged"), self.focusChanged)
        self.srcEditor.FocusChanged.connect( self.focusChanged )
        
        # self.connect(self.srcEditor, SIGNAL("cursorPositionChanged(int, int)"), self.onCursorPositionChanged)
        self.srcEditor.cursorPositionChanged.connect(self.onCursorPositionChanged)
        
        # self.connect(self.srcEditor, SIGNAL("textChanged()"), self.setModify)
        self.srcEditor.textChanged.connect(self.setModify)
        
        # self.connect(self.srcEditor, SIGNAL("textChanged()"), self.updateTotalLines)
        self.srcEditor.textChanged.connect(self.updateTotalLines)

    def viewer(self):
        """
        return the document viewer
        """
        return self.parent
       
    def updateTotalLines(self):
        """
        On total lines changed
        """
        # self.parent.emit( SIGNAL("totalLinesChanged"), self.editor().lines() )
        self.viewer().TotalLinesChanged.emit( self.editor().lines() )
        
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
        
    def onCursorPositionChanged (self , ln, col):
        """
        Emit signal from parent to update the position of the cursor
        
        @param ln: line index
        @type ln: Integer

        @param col: column index
        @type col: Integer
        """
        # self.parent.emit( SIGNAL("cursorPositionChanged"), ln, col )
        self.viewer().CursorPositionChanged.emit( ln, col )

    def setDefaultCursorPosition(self):
        """
        Set the default cursor position
        """
        self.srcEditor.setFocus()
        self.srcEditor.setCursorPosition(0,0)

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
            if weditor.editorId == self.TEST_LIBRARY_EDITOR:
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
            if weditor.editorId == self.TEST_LIBRARY_EDITOR:
                self.viewer().findWidget.setEditor( editor = self.srcEditor)
            # self.parent.emit( SIGNAL("focusChanged"), self )
            self.viewer().FocusChanged.emit(self)
            
    def defaultLoad (self):
        """
        Load default empty script
        """
        defaultTemplates = DefaultTemplates.Templates()
        
        content = defaultTemplates.getLibrary()
        
        # workaround to convert \r\n to \n (dos2unix)
        # bad syntax occured only when the server is running with python2.6
        content = "\n".join(content.splitlines()) 
        
        self.srcEditor.setText(  content )
        self.srcEditor.setFocus()
        self.setReadOnly( readOnly=False )

    def load (self, content=None):
        """
        Open file
        """
        self.srcEditor.setText( content.decode("utf-8") )
        self.srcEditor.setFocus()
        self.setReadOnly( readOnly=False )
        return True

    def getraw_encoded(self):
        """
        Returns raw data encoded
        """
        encoded = ""
        try:
            encoded = base64.b64encode( unicode(self.srcEditor.text()).encode('utf-8') )
        except Exception as e:
            self.error( "unable to encode: %s" % e )
        return encoded
