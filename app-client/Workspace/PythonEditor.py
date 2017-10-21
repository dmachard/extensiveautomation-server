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
Python editor module
"""
import sys

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QWidget, QLabel, QFont, QVBoxLayout, QFrame, QColor, QIcon, QTextCursor,
                            QKeySequence, QMenu, QLineEdit, QGridLayout, QCheckBox, QHBoxLayout,
                            QGroupBox, QComboBox, QSizePolicy, QToolBar)
    from PyQt4.QtCore import (pyqtSignal, Qt, QRegExp, QThread, QRect, QSize)
    from PyQt4.Qsci import (QsciLexerPython, QsciScintilla, QsciLexerXML, QsciLexerProperties,
                            QsciAPIs )
    if sys.version_info < (3,):
        from PyQt4.QtCore import (QString)
except ImportError:
    from PyQt5.QtGui import (QFont, QColor, QIcon, QKeySequence, QTextCursor)
    from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QFrame, QMenu, QLineEdit, QGroupBox,
                                QGridLayout, QCheckBox, QHBoxLayout, QSizePolicy, QComboBox,
                                QToolBar)
    from PyQt5.QtCore import (pyqtSignal, Qt, QRegExp, QThread, QRect, QSize)
    from PyQt5.Qsci import (QsciLexerPython, QsciScintilla, QsciLexerXML, QsciLexerProperties,
                            QsciAPIs )
    
import math
import re

from Libs import QtHelper, Logger
import Settings

class EditorWidget(QWidget, Logger.ClassLogger):
    """
    Widget editor for python
    """
    def __init__(self, editorId, title, parent, activePyLexer=True, 
                        activePropertiesLexer=False, wrappingText=False, toolbar=True  ):
        """
        Contructs EditorWidget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.toolbar = toolbar
        self.title = title
        self.editor = PyEditor(editorId,parent, activePyLexer, activePropertiesLexer, wrappingText)
        self.createWidgets()
        self.createToolbars()
    
    def getEditor(self):
        """
        Return editor
        """
        return self.editor

    def createWidgets (self):
        """
        Create qt widget
        """
        self.dockToolbarClipboard = QToolBar(self)
        self.dockToolbarClipboard.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarClipboard.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarText = QToolBar(self)
        self.dockToolbarText.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarText.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
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
        
        self.textBox = QGroupBox("Formatting")
        self.textBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutTextBox = QHBoxLayout()
        layoutTextBox.addWidget(self.dockToolbarText)
        layoutTextBox.setContentsMargins(0,0,0,0)
        self.textBox.setLayout(layoutTextBox)
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.textBox)
        layoutToolbars.addWidget(self.clipBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(0,0,0,0)

        title = QLabel(self.title)
        title.setStyleSheet("QLabel { padding-left: 1px; padding-top: 2px }")
        font = QFont()
        font.setBold(True)
        title.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget( title )
        if self.toolbar:
            layout.addLayout( layoutToolbars )
        layout.addWidget( self.editor )
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def createToolbars(self):
        """
        """
        self.dockToolbarClipboard.addAction(self.editor.copyAction)
        self.dockToolbarClipboard.addAction(self.editor.cutAction)
        self.dockToolbarClipboard.addAction(self.editor.pasteAction)
        self.dockToolbarClipboard.addSeparator()
        self.dockToolbarClipboard.addAction(self.editor.undoAction)
        self.dockToolbarClipboard.addAction(self.editor.redoAction)
        self.dockToolbarClipboard.setIconSize(QSize(16, 16))
        
        self.dockToolbarText.addAction(self.editor.foldAllAction)
        self.dockToolbarText.addSeparator()
        self.dockToolbarText.addAction(self.editor.commentAction)
        self.dockToolbarText.addAction(self.editor.uncommentAction)
        self.dockToolbarText.setIconSize(QSize(16, 16))

class CustomPythonLexer(QsciLexerPython):
    """
    Custom python lexer
    """
    def keywords(self, index):
        """
        Reimplement keyword and add personnal keywords
        """
        keywords = QsciLexerPython.keywords(self, index) or ''
        if index == 1:
            return Settings.instance().readValue( key = 'Editor/keywords-list' ) + " " + keywords
        return keywords
        
class PyEditor(QsciScintilla, Logger.ClassLogger):
    """
    Python editor
    """
    FocusChanged = pyqtSignal()
    __indicator_word = 0
    def __init__(self, editorId, parent = None, activePyLexer=True,
                        activePropertiesLexer=False, wrappingText=False ):
        """
        Python editor based on QsciScintilla

        @param editorId: 
        @type editorId:

        @param parent: 
        @type parent:
        """
        QsciScintilla.__init__(self, parent)
        self.editorId = editorId
        self.activePyLexer = activePyLexer
        self.activePropertiesLexer = activePropertiesLexer
        self.setAcceptDrops(True)
        self.wrappingText = wrappingText
        
        self.opening = ['(', '{', '[', "'", '"']
        self.closing = [')', '}', ']', "'", '"']
        
        self.createActions()
        self.createWidgets()
        self.createConnections()
        self.setupContextMenu()
  
    def enterEvent (self, event):
        """
        On mouse move event
        """
        event.accept()

    def leaveEvent (self, event):
        """
        On mouse move event
        """
        event.accept()

    def activeXmlLexer(self):
        """
        Active Xml Lexer
        """
        self.setLexer( QsciLexerXML(self) )

    def activeIniLexer(self):
        """
        Deactive Xml Lexer
        """
        self.setLexer( QsciLexerProperties(self) )

    def dragEnterEvent(self, event):
        """
        Drag enter event
        """
        if event.mimeData().hasFormat('application/x-%s-help-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.accept()
        elif event.mimeData().hasFormat('application/x-%s-parameter-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.accept()
        elif event.mimeData().hasFormat('application/x-%s-agent-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.accept()
        elif event.mimeData().hasFormat('application/x-%s-description-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.accept()
        else:
            QsciScintilla.dragEnterEvent(self, event)
        
    def dragMoveEvent(self, event):
        """
        Drag move event
        """
        if event.mimeData().hasFormat("application/x-%s-help-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        elif event.mimeData().hasFormat("application/x-%s-parameter-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        elif event.mimeData().hasFormat("application/x-%s-agent-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        elif event.mimeData().hasFormat("application/x-%s-description-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower()):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            QsciScintilla.dragMoveEvent(self, event)
  
    def dropEvent(self, event):
        """
        Drop event
        """
        # drag and drop from assistant
        if (event.mimeData().hasFormat('application/x-%s-help-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() )):
            event.acceptProposedAction()
            if sys.version_info > (3,): # python 3 support
                data = event.mimeData().data("application/x-%s-help-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() )
            else:
                data = QString(event.mimeData().data("application/x-%s-help-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ))
            if sys.version_info > (3,): # python 3 support
                d = eval( data )
            else:
                d = eval( str(data) )

            self.beginUndoAction()
            if self.editorId == 2: # testunit
                try:
                    self.insert( d[2] )
                except IndexError as e:
                    self.insert( d[0] )
            else: # testsuite
                if self.editorId == 0:
                    self.insert( d[0] )
                else:
                    self.insert( d[1] )
            self.endUndoAction()

        # drag and drop from test parameters
        elif (event.mimeData().hasFormat('application/x-%s-parameter-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() )):
            event.acceptProposedAction()
            if sys.version_info > (3,): # python 3 support
                data = event.mimeData().data("application/x-%s-parameter-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() )
            else:
                data = QString(event.mimeData().data("application/x-%s-parameter-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ))
            
            if sys.version_info > (3,): # python 3 support
                data = str(data, 'utf8')
                    
            self.beginUndoAction()
            if self.editorId == 0:
                self.insert( data )
            else:
                self.insert( data )
            self.endUndoAction()

        # drag and drop from test agents
        elif (event.mimeData().hasFormat('application/x-%s-agent-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() )):
            event.acceptProposedAction()
            if sys.version_info > (3,): # python 3 support
                data = event.mimeData().data("application/x-%s-agent-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() )
            else:
                data = QString(event.mimeData().data("application/x-%s-agent-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ))
                
            if sys.version_info > (3,): # python 3 support
                data = str(data, 'utf8')
                
            self.beginUndoAction()
            if self.editorId == 0:
                self.insert( data )
            else:
                self.insert( data )
            self.endUndoAction()

        # drag and drop from test description
        elif (event.mimeData().hasFormat('application/x-%s-description-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower() )):
            event.acceptProposedAction()
            if sys.version_info > (3,): # python 3 support
                data = event.mimeData().data("application/x-%s-description-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() )
            else:
                data = QString(event.mimeData().data("application/x-%s-description-item" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ))
                
            if sys.version_info > (3,): # python 3 support
                data = str(data, 'utf8')
                
            self.beginUndoAction()
            if self.editorId == 0:
                self.insert( data )
            else:
                self.insert( data )
            self.endUndoAction()
        else:
            QsciScintilla.dropEvent(self, event)   

    def createWidgets (self):
        """
        QsciScintilla widget creation
        """
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Lexer/Highlighter settings
        lexer = CustomPythonLexer(self)

        fontSettings = Settings.instance().readValue( key = 'Editor/font' ).split(",")
        font = fontSettings[0]
        fontSize =  fontSettings[1]
        defaultFont = QFont(font, int(fontSize))
        defaultFont.setFixedPitch(True)
        
        lexer.setDefaultFont(defaultFont)

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        lexer.setIndentationWarning(QsciLexerPython.Inconsistent)
        
        if self.activePyLexer:
            self.setLexer(lexer)
            
            # api = QsciAPIs(lexer)
            # api.add('aLongString')
            # api.add('aLongerString')
            # api.add('aDifferentString')
            # api.add('sOmethingElse')
            # api.prepare()
            
            # self.setAutoCompletionThreshold(1)
            # self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

        lexerProperties = QsciLexerProperties(self)
        if self.activePropertiesLexer:
            self.setLexer(lexerProperties)

        ## Editing line color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor( 
                                            QColor( Settings.instance().readValue( key = 'Editor/color-current-line' ) )
                                        ) 
        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setTabWidth(2)
        self.setIndentationsUseTabs(True)
        self.setEolMode(QsciScintilla.EolUnix)
        self.activeFolding( False )
        self.setIndentationGuidesVisible( False )
        self.setTabIndents(True)
        
        # margins
        self.setMarginLineNumbers(1, False)
        self.setMarginWidth(1, 0)
        self.setMarginsBackgroundColor(Qt.gray)
        marginFont = QFont()
        marginFont.setBold(False)
        self.setMarginsFont (marginFont)
        self.setMarginsForegroundColor(Qt.white)
        
        # text wrapping
        if self.wrappingText: self.setWrappingMode(wrap=True)

        # folding
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        self.setFoldMarginColors( QColor('#d3d7cf'), QColor('#d3d7cf'))
        
        # indicators
        if sys.version_info > (3,):
            self.matchIndicator = self.indicatorDefine(QsciScintilla.INDIC_FULLBOX, 9)
            self.setIndicatorForegroundColor( QColor( Settings.instance().readValue( key = 'Editor/color-indicator' )), self.matchIndicator)
            self.setIndicatorDrawUnder(True, self.matchIndicator)
                
            self.findOccurenceThread = FindOccurenceThread()
            self.findOccurenceThread.markOccurrence.connect(self.markOccurence)
            
        # selection
        self.setSelectionBackgroundColor( 
                                            QColor( Settings.instance().readValue( key = 'Editor/color-selection-background' ) )
                                        )
        
    def setWrappingMode(self, wrap):
        """
        Set wrap mode
        """
        if wrap:
            self.setWrapMode(QsciScintilla.WrapCharacter  )
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setWrapMode(QsciScintilla.WrapNone)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def setIndentationGuidesVisible(self, state):
        """
        Show/hide guides

        @param state: 
        @type state: boolean
        """
        if state:
            self.setIndentationGuides( state )
        else:
            self.setIndentationGuides( state )

    def setWhitespaceVisible(self, state):
        """
        Show/hide whitespace

        @param state: 
        @type state: boolean
        """
        if state:
            self.setWhitespaceVisibility( QsciScintilla.WsVisible )
        else:
            self.setWhitespaceVisibility( QsciScintilla.WsInvisible )

    def activeFolding (self, fold):
        """
        Active folding

        @param fold: 
        @type fold: boolean
        """
        if fold:
            self.foldAllAction.setEnabled(True)
            self.setFolding( QsciScintilla.PlainFoldStyle        )
            self.SendScintilla( QsciScintilla.SCI_SETFOLDFLAGS, 0);
        else:
            self.foldAllAction.setEnabled(False)
            self.unfoldAll()
            self.setFolding(QsciScintilla.NoFoldStyle)
   
    def foldHeader(self, line):
        """
        Is it a fold header line?

        @param line: 
        @type line:
        """
        lvl = self.SendScintilla(QsciScintilla.SCI_GETFOLDLEVEL, line)
        return lvl & QsciScintilla.SC_FOLDLEVELHEADERFLAG

    def foldExpanded(self, line):
        """
        Is fold expanded?

        @param line: 
        @type line:
        """
        return self.SendScintilla(QsciScintilla.SCI_GETFOLDEXPANDED, line)

    def getFoldedLines(self):
        """
        Return the list of folded line numbers
        """
        return [line for line in xrange(self.lines()) \
        if self.foldHeader(line) and not self.foldExpanded(line) ]

    def unfoldAll(self):
        """
        Unfold all folded lines
        """
        for line in self.getFoldedLines():
            self.foldLine(line)

    def foldAllLines(self):
        """
        Fold all lines
        """
        if sys.platform == "win32":
            self.foldAll(children=True)
        else:
            self.foldAll()

    def createConnections (self):
        """
        create qt connections
        """
        self.linesChanged.connect( self.onLinesChanged )
        self.copyAvailable.connect( self.copyAction.setEnabled )
        self.copyAvailable.connect( self.cutAction.setEnabled )
        self.copyAvailable.connect( self.deleteAction.setEnabled )

    def createActions(self):
        """
        QtActions creation
        Actions defined:
         * undo
         * redo
         * cut
         * copy
         * paste
         * delete
         * comment
         * uncomment
        """
        self.undoAction = QtHelper.createAction(self, "Undo", callback = self.undo, icon = QIcon(":/undo.png"),
                                                shortcut = "Ctrl+Z", tip = 'Undoes the last action' )
        self.redoAction = QtHelper.createAction(self, "Redo", callback = self.redo,  icon = QIcon(":/redo.png"),
                                                shortcut = "Ctrl+Y", tip = 'Redoes the previously undone action' )
        self.cutAction = QtHelper.createAction(self, "Cut", callback = self.cut, shortcut = QKeySequence.Cut,
                                                icon = QIcon(":/cut.png"), tip = 'Cuts the selection and puts it on the clipboard' )
        self.copyAction = QtHelper.createAction(self, "Copy", callback = self.copy,  shortcut = QKeySequence.Copy,
                                                icon = QIcon(":/copy.png"), tip = 'Copies the selection and puts it on the clipboard' )
        self.pasteAction = QtHelper.createAction(self, "Paste", callback = self.paste,  shortcut = QKeySequence.Paste,
                                                icon = QIcon(":/paste.png"), tip = 'Inserts clipboard contents' )

        self.deleteAction = QtHelper.createAction( self, "Delete Selection", callback = self.removeSelectedText,
                                                tip = 'Deletes the selection' )
        self.commentAction = QtHelper.createAction(self, "Comment", callback = self.comment,
                                                icon = QIcon(":/comment.png"), tip = 'Insert comment sign at the begining of line' )
        self.uncommentAction = QtHelper.createAction(self, "Uncomment", callback = self.uncomment,
                                                icon = QIcon(":/uncomment.png"), tip = 'Remove comment sign at the begining of line' )
        
        self.foldAllAction = QtHelper.createAction( self, "Fold\nUnfold", callback = self.foldAllLines,
                                                icon = QIcon(":/folding.png"), tip = 'Fold/Unfold all lines' )
    
    def setupContextMenu (self):
        """
        Setup context menu
        """
        self.menu = QMenu()
        self.menu.addAction( self.undoAction )
        self.menu.addAction( self.redoAction )
        self.menu.addSeparator()
        self.menu.addAction( self.commentAction )
        self.menu.addAction( self.uncommentAction )
        self.menu.addSeparator()
        self.menu.addAction( self.cutAction )
        self.menu.addAction( self.copyAction )
        self.menu.addAction( self.pasteAction )
        self.menu.addAction( self.deleteAction )
        self.menu.addAction( "Select All", self.selectAll)
        self.menu.addSeparator()
        self.menu.addAction( self.foldAllAction )

    def onLinesChanged(self):
        """
        Update the line counter margin's width.
        """
        width = math.log( self.lines(), 10 ) + 2
        if sys.version_info > (3,): # for python3 support
            self.setMarginWidth( 1, '0'*int(width) )
        else:
            self.setMarginWidth( 1, QString( '0'*int(width) ) )
    
    def comment(self):
        """
        Comment current line or selection
        """
        self.addPrefix('#')

    def uncomment(self):
        """
        Uncomment current line or selection
        """
        self.removePrefix('#')
   
    def indent(self):
        """
        Indent current line or selection
        """
        self.addPrefix( "\t" )

    def unindent(self):
        """
        Unindent current line or selection
        """
        self.removePrefix( "\t" )
    
    def keyPressEvent(self, event):
        """
        Reimplement Qt method
    
        @param event: 
        @type event:
        """
        key = event.key()
        startLine, startPos, endLine, endPos = self.getSelection()
        line, index = self.getCursorPosition()
        cmd = self.text(line)
        
        if (key == Qt.Key_Tab ):
            self.indent()
            event.accept()
        elif key == Qt.Key_Backtab:
            self.unindent()
            event.accept()
        else:
            # new in v13.1
            t = event.text()

            # extract option from settings file
            autoCloseBracket = QtHelper.str2bool(  Settings.instance().readValue( key = 'Editor/auto-close-bracket' )   )
            
            txt = cmd[:index].replace('>>> ', '').replace('... ', '')

            # new in v16
            afterTxt = cmd[index:]
            if len(afterTxt): afterTxt = afterTxt.splitlines()[0]
            # end of new
            
            if t in self.opening and autoCloseBracket:
                i = self.opening.index(t)
                if self.hasSelectedText():
                    selText = self.selectedText()
                    self.removeSelectedText()
                    self.insert(self.opening[i] + selText + self.closing[i])
                    self.setCursorPosition(endLine, endPos + 2)
                    return
                else:
                    if len(afterTxt):
                        pass
                    elif t == '(' and (re.match(r'^[ \t]*def \w+$', txt)
                                       or re.match(r'^[ \t]*class \w+$', txt)):
                        self.insert('):')
                    else:
                        self.insert(self.closing[i])
            elif t in [')', ']', '}'] and autoCloseBracket:
                txt = self.text(line)
                try:
                    if txt[index - 1] in self.opening and t == txt[index]:
                        self.setCursorPosition(line, index + 1)
                        self.SendScintilla(QsciScintilla.SCI_DELETEBACK)
                except IndexError:
                    pass
            else:
                pass
            # end new in v13.1    
            
            QsciScintilla.keyPressEvent(self, event)

    def addPrefix(self, prefix):
        """
        Add prefix to current line or selected line(s)

        @param prefix: 
        @type prefix:
        """
        if self.hasSelectedText():
            # Add prefix to selected line(s)
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            if indexTo == 0:
                lineTo -= 1
            self.beginUndoAction()
            for line in range( lineFrom, lineTo+1 ):
                self.insertAt( prefix, line, 0 )
            self.endUndoAction()
            if indexTo == 0:
                lineTo += 1
            else:
                indexTo += len(prefix)
            self.setSelection( lineFrom, indexFrom+len(prefix),
                              lineTo, indexTo )
        else:
            # Add prefix to current line
            line, index = self.getCursorPosition()
            self.beginUndoAction()
            self.insertAt( prefix, line, 0 )
            self.endUndoAction()
            self.setCursorPosition( line, index+len(prefix) )

    def removePrefix(self, prefix):
        """
        Remove prefix from current line or selected line(s)

        @param prefix: 
        @type prefix:       
        """
        if self.hasSelectedText():
            # Remove prefix from selected line(s)
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            if indexTo == 0:
                lineTo -= 1
            self.beginUndoAction()
            for line in range( lineFrom, lineTo+1 ):
                if sys.version_info > (3,): # python3 support
                    if not self.text(line).startswith(prefix):
                        continue
                else:
                    if not self.text(line).startsWith(prefix):
                        continue
                self.setSelection(line, 0, line, len(prefix))
                self.removeSelectedText()
                if line == lineFrom:
                    indexFrom = max([0, indexFrom-len(prefix)])
                if line == lineTo and indexTo != 0:
                    indexTo = max( [0, indexTo-len(prefix)] )
            if indexTo == 0:
                lineTo += 1
            self.setSelection( lineFrom, indexFrom, lineTo, indexTo )
            self.endUndoAction()
        else:
            # Remove prefix from current line
            line, index = self.getCursorPosition()
            if sys.version_info > (3,): # python3 support
                if not self.text(line).startswith(prefix):
                    return
            else:
                if not self.text(line).startsWith(prefix):
                    return
            self.beginUndoAction()
            self.setSelection(line, 0, line, len(prefix))
            self.removeSelectedText()
            self.setCursorPosition( line, index-len(prefix) )
            self.endUndoAction()
            self.setCursorPosition( line, max([0, index-len(prefix)]) )
    
    def contextMenuEvent(self, event):
        """
        Reimplement Qt method
        Menu on right click

        @param event: 
        @type event:
        """
        self.undoAction.setEnabled( self.isUndoAvailable() )
        self.redoAction.setEnabled( self.isRedoAvailable() )
        self.menu.popup(event.globalPos())
        event.accept()
    
    def findText(self, text, changed=True, forward=True, wraps=True, case=False, 
                        words=False, regexp=False, line=-1, index=-1):
        """
        Find text

        @param text: 
        @type text:     

        @param changed: 
        @type changed: boolean      
        
        @param forward: 
        @type forward: boolean  

        @param case: 
        @type case: boolean     

        @param words: 
        @type words: boolean                
        """
        if changed or not forward:
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            self.setCursorPosition( lineFrom, max([0, indexFrom-1]) )
        return self.findFirst(text, regexp, case, words, wraps, forward, line, index, True)    
    
    def focusInEvent(self, event):
        """
        Reimplemented to handle focus

        @param event: 
        @type event:
        """
        if self.isVisible(): self.FocusChanged.emit()
        QsciScintilla.focusInEvent(self, event)

    def focusOutEvent(self, event):
        """
        Reimplemented to handle focus

        @param event: 
        @type event:
        """
        if self.isVisible(): self.FocusChanged.emit()
        QsciScintilla.focusOutEvent(self, event)

    def wheelEvent(self, ev):
        """
        Use ctrl+wheel to zoom in/out
        """
        if Qt.ControlModifier & ev.modifiers():
            if ev.delta() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
                
            # update margin size
            self.onLinesChanged()
        else:
            return super(PyEditor, self).wheelEvent(ev)
    
    def mouseDoubleClickEvent(self, event):
        """
        Intercept double click
        """
        super(PyEditor, self).mouseDoubleClickEvent(event)
        if event.button() == Qt.LeftButton:
            self.findOccurences()

    def clearAllIndicators(self, indicator):
        """
        Clear all indicators
        """
        self.clearIndicatorRange(0, 0, self.lines(), 0, indicator)        
  
    def markOccurence(self, foundList):
        """
        """
        if sys.version_info > (3,):
            self.clearAllIndicators(self.matchIndicator)
            if len(foundList) == 1: return
            for i in foundList:
                self.fillIndicatorRange( i[0], i[1], i[0], i[2], self.matchIndicator)
        
    def findOccurences(self):
        """
        Find all occurences of the text
        """
        if sys.version_info > (3,):
            self.clearAllIndicators(self.matchIndicator)
        
            word = self.textUnderCursor()
            if not word:
                return
                
            wholeWord = True
            self.findOccurenceThread.find(word, wholeWord, self.text())
         
    def textUnderCursor(self):
        """
        Return current word at cursor position
        """
        line, index = self.getCursorPosition()
        text = self.text(line)
        wc = self.wordCharacters()
        if wc is None:
            regexp = QRegExp('[^\w_]')
        else:
            regexp = QRegExp('[^{0}]'.format(re.escape(wc)))
        start = regexp.lastIndexIn(text, index) + 1
        end = regexp.indexIn(text, index)
        if start == end + 1 and index > 0:
            # we are on a word boundary, try again
            start = regexp.lastIndexIn(text, index - 1) + 1
        if start == -1: start = 0
        if end == -1: end = len(text)
        if end > start:
            word = text[start:end]
        else:
            word = ''
        return word
        
class FindOccurenceThread(QThread):
  
    markOccurrence = pyqtSignal(list)
  
    def run(self):
        """
        """
        word = re.escape(self.word)
        if self.wholeWord:
            word = "\\b{0}\\b".format(word)
        flags = re.UNICODE | re.LOCALE
        search = re.compile(word, flags)
  
        lineno = 0
        foundList = []
        for lineText in self.source.splitlines():
            for i in search.finditer(lineText):
                start = i.start()
                end = i.end()
                foundList.append([lineno, start, end])
            lineno += 1
        self.markOccurrence.emit(foundList)
  
    def find(self, word, wholeWord, source):
        """
        """
        self.source = source
        self.word = word
        self.wholeWord = wholeWord
  
        self.start()

class QLineEditMore(QComboBox):
    """
    Line edit more
    """
    EnterPressed = pyqtSignal()  
    def __init__(self, parent):
        """
        Construstor
        """
        QComboBox.__init__(self,parent)
    def keyPressEvent(self, e):
        """
        Called on key press
        """
        if e.key() == Qt.Key_Return:
            self.EnterPressed.emit() 
        QComboBox.keyPressEvent(self, e)
        
class FindReplace(QWidget):   
    """
    Find replace widget bar
    """
    NbReplaced = pyqtSignal(int)
    def __init__(self, parent):
        """
        This class provides an graphical interface to find and replace text

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.editor = None
        self.styleEdit = { False: "background-color:rgb(255, 175, 90);", True: "" }
        
        self.createButton()
        self.createWidgets()
        self.createConnections()

    def showEnhanced(self, textSelected=''):
        """
        Show enhanced (focus and text selected)
        """
        self.show()
        if len(textSelected): self.edit.setEditText(textSelected)
        self.edit.setFocus()
        self.edit.lineEdit().selectAll()
        
    def createButton (self):
        """
        create qt buttons
        Buttons defined:
         * Previous
         * Next
         * Replace
        """
        self.previousButton = QtHelper.createButton(self, text= self.tr("Find Previous"),  triggered=self.findPrevious,
            icon=QIcon(":/find_previous.png") )
        self.nextButton = QtHelper.createButton(self, text=self.tr("Find Next"), triggered=self.findNext,
            icon=QIcon(":/find_next.png") )
        self.replaceButton = QtHelper.createButton(self,  text=self.tr("Replace..."), triggered=self.replaceFind, 
            icon=QIcon(":/replace.png") )

    def createWidgets (self):
        """
        QtWidgets creation

        QHBoxLayout
         -------------------------------------------.....
        | QLabel: QLineEdit QButton QButton QCheckBox |
         -------------------------------------------.....

        ....--------------------------------------
             QLabel: QLineEdit QButton QCheckBox |
        ....--------------------------------------
        """
        glayout = QGridLayout()
        glayout.setContentsMargins(0, 0, 0, 0)

        # findWhat = QLabel(  self.tr("Find :") )
        # replaceWith = QLabel(  self.tr("Replace With:") )
        
        self.edit = QLineEditMore(parent=self)
        # self.edit.setMinimumWidth(250)
        self.edit.setEditable(1)
        self.edit.setMaxCount(10)
        self.edit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.edit.lineEdit().setPlaceholderText("Search text in your test?")
        
        #self.replaceEdit = QComboBox(parent=self)
        self.replaceEdit = QComboBox(self)
        # self.replaceEdit.setMinimumWidth(250)
        self.replaceEdit.setEditable(1)
        self.replaceEdit.setMaxCount(10)
        self.replaceEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.replaceEdit.lineEdit().setPlaceholderText("Replace the text with?")
        
        self.line = QFrame()
        self.line.setGeometry( QRect(110, 221, 51, 20) )
        self.line.setFrameShape( QFrame.VLine )
        self.line.setFrameShadow( QFrame.Sunken )

        self.caseCheck = QCheckBox( self.tr("Case Sensitive") )
        self.caseCheck.setChecked( 
                                       QtHelper.str2bool( 
                                                            Settings.instance().readValue( key = 'Editor/find-case-sensitive' )
                                                         )
                                      )
        self.caseWordCheck = QCheckBox( self.tr("Whole word only") )
        self.caseWordCheck.setChecked( 
                                       QtHelper.str2bool( 
                                                            Settings.instance().readValue( key = 'Editor/find-whole-word' )
                                                         )
                                      )
        self.allCheck = QCheckBox(  self.tr("All occurences") )
        self.allCheck.setChecked( 
                                       QtHelper.str2bool( 
                                                            Settings.instance().readValue( key = 'Editor/replace-all' )
                                                         )
                                      )
        self.caseRegexpCheck = QCheckBox(  self.tr("Regular expression") )
        self.caseRegexpCheck.setChecked( 
                                       QtHelper.str2bool( 
                                                            Settings.instance().readValue( key = 'Editor/find-regexp' )
                                                         )
                                      )
        self.caseWrapCheck = QCheckBox(  self.tr("Wrap at the end") )
        self.caseWrapCheck.setChecked( 
                                       QtHelper.str2bool( 
                                                            Settings.instance().readValue( key = 'Editor/find-wrap' )
                                                         )
                                      )
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.allCheck)
        hlayout.addWidget(self.line)

        # glayout.addWidget( findWhat, 0, 0 )
        glayout.addWidget( self.edit, 0, 1 )
        glayout.addWidget( self.nextButton, 0, 2 )
        glayout.addWidget( self.previousButton, 0, 3 )
        glayout.addWidget( self.caseCheck, 0, 4 )
        glayout.addWidget( self.caseWrapCheck, 0, 5 )
        glayout.addWidget( self.caseWordCheck, 1, 4 )
        glayout.addWidget( self.caseRegexpCheck, 1, 5 )

        # glayout.addWidget( replaceWith, 1, 0 )
        glayout.addWidget( self.replaceEdit, 1, 1 )
        glayout.addWidget( self.replaceButton, 1, 2 )
        glayout.addLayout( hlayout, 1, 3)

        self.previousButton.setDisabled(True)
        self.nextButton.setDisabled(True)

        self.setLayout(glayout)

    def createConnections (self):
        """
        create qt connection
        """
        self.edit.editTextChanged.connect(self.textHasChanged)
        self.edit.EnterPressed.connect(self.returnPressed)
        self.caseCheck.stateChanged.connect(self.find )
        
    def returnPressed(self):
        """
        Return key pressed
        Find next in this case
        """
        self.findNext()

    def setEditor(self, editor):
        """
        Set the target to find the text

        @param editor: 
        @type editor:   
        """
        self.editor = editor
    
    def textHasChanged (self, txt):
        """
        Find text has changed
        """
        # text = self.edit.text()
        text = self.edit.currentText()
        if len(text) > 0:
            self.previousButton.setEnabled(True)
            self.nextButton.setEnabled(True)            
            self.find( changed=True, forward=True)
        else:
            self.previousButton.setDisabled(True)
            self.nextButton.setDisabled(True)

    def updateComboBox(self):
        """
        """
        comboUpdated = False
        for i in range(self.edit.count()):
            if self.edit.itemText(i) ==  self.edit.currentText():
                comboUpdated = True
        if not comboUpdated:
            self.edit.addItem( self.edit.currentText() )
            
        comboUpdated = False
        for i in range(self.replaceEdit.count()):
            if self.replaceEdit.itemText(i) ==  self.replaceEdit.currentText():
                comboUpdated = True
        if not comboUpdated:
            self.replaceEdit.addItem( self.replaceEdit.currentText() )
            
    def clearText (self):
        """
        Clear all QlineEdit
        """
        self.edit.setStyleSheet("")

        self.edit.clearEditText()
        
        self.replaceEdit.clearEditText()
        
    def findPrevious (self):
        """
        Find previous occurence
        """
        # update combobox 
        self.updateComboBox()
            
        # find previous
        self.find( changed=False, forward=False )

    def findNext (self, line=-1, index=-1):
        """
        Find next occurence
        """
        # update combobox
        self.updateComboBox()
            
        return self.find( changed=False, forward=True, line=line, index=index )

    def find(self, changed=True, forward=True, line=-1, index=-1 ):
        """
        Call the find function

        @param changed: 
        @type changed: boolean  

        @param forward: 
        @type forward: boolean      
        """
        # text = self.edit.text()
        text = self.edit.currentText()
        if len(text)==0:
            self.edit.setStyleSheet("")
            return None
        else:
            found = self.editor.findText( text, changed, forward, case=self.caseCheck.isChecked(), 
                                            words=self.caseWordCheck.isChecked(),
                                            regexp=self.caseRegexpCheck.isChecked(),
                                            wraps=self.caseWrapCheck.isChecked(),
                                            line=line, index=index                                         
                                            )
            self.edit.setStyleSheet( self.styleEdit[found] )
            return found
            
    def replaceFind(self):
        """
        Replace and find
        """
        if (self.editor is None): return

        replaceText = self.replaceEdit.currentText()
        searchText = self.edit.currentText()
        if not self.caseCheck.isChecked(): searchText = searchText.lower()
        current = -1; nbReplaced=0
        
        # find the first occurence from the beginning of the doc or not
        if not self.allCheck.isChecked():
            detected = self.findNext()
        else:
            detected = self.findNext(line=0, index=0)
        (line, _) = self.editor.getCursorPosition()

        while detected:
            previous = current
            selectedText = self.editor.selectedText()

            # normalize the text in lower case if the case sensitive is not activated
            if not self.caseCheck.isChecked(): selectedText = selectedText.lower()
            
            # replace the selection
            if self.editor.hasSelectedText() and selectedText == searchText:
                self.editor.replace(replaceText)
                nbReplaced += 1

            # find the next occurence of the word
            detected = self.findNext()
            (current, _) = self.editor.getCursorPosition()

            # all doc readed ? break the loop
            if previous > current: break
            if current == line and previous != -1: break 

            # just execute one replace
            if not self.allCheck.isChecked(): break 

        self.allCheck.setCheckState( Qt.Unchecked )      
        self.NbReplaced.emit(nbReplaced)

class WCursorPosition(QWidget, Logger.ClassLogger):
    """
    Cursor position widget
    """
    def __init__(self, parent):
        """
        This widget provides the position of the cursor in the editor (line|column)
         -------------------------
        | Line: xxx   Column: xxx |
         -------------------------

        @param parent: 
        @type parent:       
        """
        QWidget.__init__(self, parent)
        self.createWidgets()

    def createWidgets (self):
        """
        create  qt widget

        QHBoxLayout
         ---------------------------------
        | QLabel: QLabel | QLabel: QLabel |
         ---------------------------------
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget( QLabel("|  line:") )
        self.line = QLabel()
        layout.addWidget( self.line )
        layout.addWidget( QLabel("|  total lines:") )
        self.nbLines = QLabel()
        layout.addWidget( self.nbLines )
        self.setLayout( layout )

        self.hide()
    
    def setNumberLines(self, nb):
        """
        Set the number of lines
        """
        self.nbLines.setText("%s  |" % nb)
        
    def cursorPositionChanged(self, line, index):
        """
        Updated the position of the cursor

        @param line: 
        @type line: 
        
        @param index: 
        @type index:    
        """
        self.line.setText("%-6d column: %-4d" % ( (line+1), (index+1)) )
        self.show()