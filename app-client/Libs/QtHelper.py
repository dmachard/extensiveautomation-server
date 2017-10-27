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
Helper for qt
"""

import sys

IS_QT5 = False
try:
	from PyQt4.QtGui import (QColor, QToolButton, QApplication, QTextEdit, QCompleter, QWidget, QPlainTextEdit,
							QLineEdit, QPushButton, QHBoxLayout, QLabel, QDialog, QIcon, QCursor,
							QDesktopWidget, QVBoxLayout, QSizePolicy, QMovie, QProgressBar, 
							QPixmap, QAction, QPainter, QRadialGradient, QTransform, QFrame)
	from PyQt4.QtCore import (Qt, pyqtSignal, QVariant, QSize, QPointF, QRect)
	from PyQt4.Qsci import (QsciScintilla, QsciLexerPython, QsciLexerXML, QsciLexerBash)
	if sys.version_info < (3,): from PyQt4.QtCore import (QString)
except ImportError:
	from PyQt5.QtGui import (QColor, QIcon, QMovie, QPixmap, QPainter, QRadialGradient, QTransform, QCursor)
	from PyQt5.QtWidgets import (QToolButton, QApplication, QTextEdit, QCompleter, QWidget, QLineEdit, QPlainTextEdit,
							QPushButton, QHBoxLayout, QLabel, QDialog, QDesktopWidget, 
							QVBoxLayout, QSizePolicy, QProgressBar, QAction, QFrame)
	from PyQt5.QtCore import (Qt, pyqtSignal, QVariant, QSize, QPointF, QRect)
	from PyQt5.Qsci import (QsciScintilla, QsciLexerPython, QsciLexerXML, QsciLexerBash)
	IS_QT5 = True
	
import os
import imp
import random
import math
import time

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
CHART_COLOR_BLUE    = QColor(0, 0, 255, 200)
CHART_COLOR_RED     = QColor(255, 0, 0, 200)
CHART_COLOR_BLACK   = QColor(9, 0, 0, 200)
CHART_COLOR_GREEN   = QColor(0, 128, 0, 200)
CHART_COLOR_GREY    = QColor(176, 176, 176, 200)
CHART_COLOR_ORANGE  = QColor(237, 189, 45, 200)



def bytes_to_unicode(ob):
    """
    Byte to unicode with exception...
    Only for py3, will be removed on future version...
    """
    t = type(ob)
    if t in (list, tuple):
        try:
            l = [str(i, 'utf-8') if type(i) is bytes else i for i in ob]
        except UnicodeDecodeError as e:
            l = [ i for i in ob] # keep as bytes
        l = [bytes_to_unicode(i) if type(i) in (list, tuple, dict) else i for i in l]
        ro = tuple(l) if t is tuple else l
    elif t is dict:
        byte_keys = [i for i in ob if type(i) is bytes]
        for bk in byte_keys:
            v = ob[bk]
            del(ob[bk])
            try:
                ob[str(bk,'utf-8')] = v
            except UnicodeDecodeError as e:
                ob[bk] = v # keep as bytes
        for k in ob:
            if type(ob[k]) is bytes:
                try:
                    ob[k] = str(ob[k], 'utf-8')
                except UnicodeDecodeError as e:
                    ob[k] = ob[k] # keep as bytes
            elif type(ob[k]) in (list, tuple, dict):
                ob[k] = bytes_to_unicode(ob[k])
        ro = ob
    else:
        ro = ob
        print("unprocessed object: {0} {1}".format(t, ob))
    return ro
    
class CloseToolButton(QToolButton):
    """
    Close all button
    """
    def __init__(self, parent):
        """
        Close all button
        """
        QToolButton.__init__(self, parent)
        
    def enterEvent (self, event):
        """
        On mouse move event
        """
        if not self.isEnabled():
            event.accept()
        else:
            # not a good thing to use the override function
            QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))
            event.accept()
        
    def leaveEvent (self, event):
        """
        On mouse move event
        """
        if not self.isEnabled():
            event.accept()
        else:
            # not a good thing to use the override function
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
            
def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val
        
def clearLayout(layout):
    """
    Remove widgets from layout

    @param layout: 
    @type layout:
    """
    while layout.count():
        child = layout.takeAt(0)
        child.widget().close()

def formatTimestamp ( timestamp, milliseconds=False):
    """
    Returns human-readable time

    @param timestamp: 
    @type timestamp:

    @param milliseconds: 
    @type milliseconds: boolean

    @return:
    @rtype:
    """
    if isinstance( timestamp, str):
        return "  %s  " % timestamp
    t = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(timestamp) ) 
    if milliseconds:
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) + ".%3.3d" % int((timestamp * 1000)  % 1000)
    return t

def bytes2human(n):
    """
    Bytes to human

    @param n: 
    @type n: 

    @return:
    @rtype: string
    """
    symbols = ('KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f %s' % (value, s)
    return "%s Bytes" % n

class RawPythonEditor(QsciScintilla):
    """
    Raw xml editor
    """
    def __init__(self, parent):
        """
        Text raw editor 
        """
        QsciScintilla.__init__(self, parent)
        self.createWidget()

    def createWidget(self):
        """
        Create qt widget
        """
        self.setFolding( QsciScintilla.BoxedTreeFoldStyle)
        self.setLexer( QsciLexerPython(self) )
        self.setMarginLineNumbers(0, False)
        self.setMarginWidth(1,0)
        self.setTabWidth(2)
        self.setIndentationsUseTabs(True)
    def toPlainText(self):
        """
        Return text as plain text
        """
        return self.text()

class RawXmlEditor(QsciScintilla):
    """
    Raw xml editor
    """
    def __init__(self, parent):
        """
        Text raw editor 
        """
        QsciScintilla.__init__(self, parent)
        self.createWidget()

    def createWidget(self):
        """
        Create qt widget
        """
        self.setFolding( QsciScintilla.BoxedTreeFoldStyle)
        self.setLexer( QsciLexerXML() )
        self.setMarginLineNumbers(0, False)
        self.setMarginWidth(1,0)
        
class CustomLexer(QsciLexerBash):
    """
    Custom python lexer
    """
    def keywords(self, index):
        """
        Reimplement keyword and add personnal keywords
        """
        keywords = QsciLexerBash.keywords(self, index) or ''
        if index == 1:
            return keywords
        return keywords
        
class CustomEditor(QsciScintilla):
    """
    Raw xml editor
    """
    def __init__(self, parent, jsonLexer=False):
        """
        Text raw editor 
        """
        QsciScintilla.__init__(self, parent)
        
        self.jsonLexer = jsonLexer
        
        self.createConnections()
        self.createWidget()

    def createWidget(self):
        """
        Create qt widget
        """
        self.setLexer( CustomLexer() )

    def createConnections (self):
        """
        create qt connections
        """
        self.linesChanged.connect( self.onLinesChanged )
        
    def onLinesChanged(self):
        """
        Update the line counter margin's width.
        """
        width = math.log( self.lines(), 10 ) + 2
        if sys.version_info > (3,): # for python3 support
            self.setMarginWidth( 1, '0'*int(width) )
        else:
            self.setMarginWidth( 1, QString( '0'*int(width) ) )
            
class RawEditor(QTextEdit):
    """
    Raw editor
    """
    def __init__(self, parent):
        """
        Text raw editor 
        """
        QTextEdit.__init__(self, parent)
        self.createWidget()

    def createWidget(self):
        """
        Create qt widget
        """
        # change the color of the selection
        self.setStyleSheet(
                "QTextEdit {"
                " selection-color: white;"
                " selection-background-color: black;"
                " color: black" 
                "}" )

    def searchNext(self, what):
        """
        Search next
        """
        cur = self.textCursor()
        return self.search(what=what, cur=cur)

    def search(self, what, cur=None):
        """ 
        Search
        """
        if cur is None:
            newcur = self.document().find(what)
        else:
            newcur = self.document().find(what, cur)
        if not newcur.isNull():
            self.setTextCursor(newcur)
            return True
        else:
            return False

class RawFind(QWidget):  
    """
    Raw find widget
    """
    def __init__(self, parent, editor, buttonNext=True):
        """
        Constructor
        """
        QWidget.__init__(self, parent)
        self.editor = editor
        self.buttonNext = buttonNext
        self.createWidgets()
        self.createConnections()

    def createWidgets (self):
        """
        Create qt widget
        """

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Search text?")
        if self.buttonNext:
            self.buttonNext = QPushButton("Next")

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.edit)
        if self.buttonNext:
            hlayout.addWidget(self.buttonNext)
        hlayout.setContentsMargins(0,0,0,0)
        self.setLayout(hlayout)
    
    def resetLine(self):
        """
        Reset line
        """
        self.edit.setText("")
        self.edit.setStyleSheet( "" )

    def createConnections (self):
        """
        QtSignals connection
        """
        self.edit.textChanged.connect(self.textHasChanged )
        if self.buttonNext:
            self.buttonNext.clicked.connect( self.enterPressed )
        else:
            self.edit.returnPressed.connect(self.enterPressed )
    
    def enterPressed(self):
        """
        Called on enter pressed
        """
        text = self.edit.text()
        if len(text) > 0:
            found = self.editor.searchNext(text)
            if not found:
                self.edit.setStyleSheet( "background-color:rgb(255, 175, 90);" )
            else:
                self.edit.setStyleSheet( "background-color:rgb(144, 238, 144);" )
        else:
            self.edit.setStyleSheet( "" )

    def textHasChanged(self):
        """
        Text has changed
        """
        text = self.edit.text()
        if len(text) > 0:
            found = self.editor.search(text)
            if not found:
                self.edit.setStyleSheet( "background-color:rgb(255, 175, 90);" )
            else:
                self.edit.setStyleSheet( "background-color:rgb(144, 238, 144);" )
        else:
            self.edit.setStyleSheet( "" )

    def setReadOnly(self, readonly):
        """
        Set editor to read only
        """
        self.edit.setReadOnly(readonly)
        
class LineTextWidget(QFrame):
    """
    Line text widget
    """
    class NumberBar(QWidget):
        """
        Number bar widget
        """
        def __init__(self, *args):
            """
            Constructor
            """
            QWidget.__init__(self, *args)
            self.edit = None
            # This is used to update the width of the control.
            # It is the highest line that is currently visibile.
            self.highest_line = 0
 
        def setTextEdit(self, edit):
            """
            Set the text of the edit
            """
            self.edit = edit
 
        def update(self, *args):
            """
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            """
            # The + 4 is used to compensate for the current line being bold.
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QWidget.update(self, *args)

        def paintEvent(self, event):
            """
            Paint the widget event
            """
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())
 
            painter = QPainter(self)
 
            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1
 
                # The top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
 
                # Check if the position of the block is out side of the visible
                # area.
                if position.y() > page_bottom:
                    break
 
                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
 
                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                x = self.width() - font_metrics.width(str(line_count)) - 3
                y = round(position.y()) - contents_y + font_metrics.ascent()
                t = str(line_count)

                painter.drawText(x,y,t)
 
                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
     
                block = block.next()
 
            self.highest_line = line_count
            painter.end()
 
            QWidget.paintEvent(self, event)
 
    def __init__(self, *args):
        """
        Constructor
        """
        QFrame.__init__(self, *args)
 
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        self.edit = RawEditor(parent=self)
        self.edit.setFrameStyle(QFrame.NoFrame)

        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)
 
        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins (0, 0, 0, 0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)
 
        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)
 
    def eventFilter(self, object, event):
        """
        On event filter
        """
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(object, event)
 
    def getTextEdit(self): 
        """
        return the text of the edit
        """
        return self.edit
        
class EnhancedQDialog(QDialog):
    """
    Dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor

        @param dialogName: 
        @type dialogName:

        @param parent: 
        @type parent:
        """
        QDialog.__init__(self, parent)
        self.setWindowIcon( QIcon(":/main.png") ) 
    def center(self):
        """
        Center the dialog
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class ProgressDialog(QDialog):
    """
    Progress bar dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor

        @param dialogName: 
        @type dialogName:

        @param parent: 
        @type parent:
        """
        QDialog.__init__(self, parent)
        self.setWindowIcon( QIcon(":/main.png") ) 
        self.name = dialogName
        self.createDialog()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( "%s" % self.name )
        layout = QVBoxLayout()

        self.loadingLabel = QLabel("Loading...")
        self.imageLabel = QLabel()
        
        layout2 = QHBoxLayout()
        layout2.addWidget( self.imageLabel )    
        layout2.addWidget(  self.loadingLabel  )

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")

        layout.addLayout(layout2)
        layout.addWidget( self.progressBar )

        self.setLayout(layout)

        flags = Qt.WindowFlags()
        flags |= Qt.MSWindowsFixedSizeDialogHint
        self.setWindowFlags(flags)

class MessageBoxDialog(QDialog):
    """
    Message box dialog
    """
    Download = pyqtSignal(str)
    DownloadCanceled = pyqtSignal()
    def __init__(self, dialogName, parent = None):
        """
        Constructor

        @param dialogName: 
        @type dialogName:

        @param parent: 
        @type parent:
        """
        QDialog.__init__(self, parent)
        self.setWindowIcon( QIcon(":/main.png") ) 
        self.name = dialogName
        self.url = None
        self.createDialog()
    
    def closeEvent(self, event):
        """
        On close event

        @param event: 
        @type event:
        """
        pass

    def setDownload(self, title, txt, url, cancelButton=True):
        """
        Set as download

        @param title: 
        @type title:

        @param txt: 
        @type txt:

        @param url: 
        @type url:
        """
        self.setWindowFlags(Qt.Drawer | Qt.CustomizeWindowHint)
        self.url = url
        self.setWindowTitle( title  )
        self.progressBar.hide()
        self.imageLabel.setPixmap(QPixmap(':/information.png'))
        self.loadingLabel.setText( txt )
        self.downloadButton.show()
        if cancelButton:
            self.cancelButton.show()
        else:
            self.cancelButton.hide()
        self.okButton.hide()
        self.imageLabel.show()
    
    def setTxt (self, title, txt, error=False):
        """
        Set text

        @param title: 
        @type title:

        @param txt: 
        @type txt:
        """
        self.setWindowTitle( title  )
        self.progressBar.hide()
        self.loadingLabel.setText( txt )
        self.imageLabel.show()
        if error:
            self.imageLabel.setPixmap(QPixmap(':/warning.png'))
        else:
            self.imageLabel.setPixmap(QPixmap(':/information.png'))
        self.okButton.show()
        self.downloadButton.hide()
        self.cancelButton.hide()

    def setLoading (self, msg='Loading data...' ):
        """
        Set as loading

        @param msg: 
        @type msg:
        """
        self.setWindowTitle( "%s" % self.name )
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)

        self.progressBar.show()
        self.loadingLabel.setText( msg )
        self.loadingLabel.show()
        self.okButton.hide()
        self.downloadButton.hide()
        self.cancelButton.hide()
        self.imageLabel.hide()

    def setConnection (self ):
        """
        Set text with connection
        """
        self.loadingLabel.setText( "Connection..." )

    def setInitialization (self ):
        """
        Set text with initialization
        """
        self.loadingLabel.setText( "Initialization..." )
        self.show()

    def download (self):
        """
        Emit download signal
        """
        self.Download.emit(self.url)
        self.accept()
    
    def onReject(self):
        """
        Called on cancel
        """
        self.DownloadCanceled.emit()
        self.reject()
        
    def updateDataReadProgress(self, bytesRead, totalBytes):
        """
        Update the progress bar

        @param bytesRead: 
        @type bytesRead:

        @param totalBytes: 
        @type totalBytes:
        """
        self.progressBar.setMaximum(totalBytes)
        self.progressBar.setValue(bytesRead)

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( "%s" % self.name )
        layout = QVBoxLayout()

        self.loadingLabel = QLabel("Loading...")
        self.imageLabel = QLabel()
        
        layout2 = QHBoxLayout()
        layout2.addWidget( self.imageLabel )    
        layout2.addWidget(  self.loadingLabel  )

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        #
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        self.okButton = QPushButton("Ok", self)
        self.downloadButton = QPushButton("Download", self)
        self.cancelButton = QPushButton("Cancel", self)
        
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.downloadButton)
        buttonLayout.addWidget(self.cancelButton)
        self.okButton.clicked.connect(self.accept)
        self.downloadButton.clicked.connect(self.download)
        self.cancelButton.clicked.connect(self.onReject)
        self.okButton.hide()

        layout.addLayout(layout2)
        layout.addWidget( self.progressBar )
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

        flags = Qt.WindowFlags()
        flags |= Qt.WindowCloseButtonHint
        flags |= Qt.MSWindowsFixedSizeDialogHint
        self.setWindowFlags(flags)

def isExe ():
    """
    Indicates whether the execution is exe with py2exe or. py with the Python interpreter

    @return:
    @rtype: boolean
    """
    return imp.is_frozen("__main__") # cx_freeze

def str2bool(v):
    """
    Converts string to boolean

    @param v: 
    @type v:

    @return:
    @rtype: boolean
    """
    return v.lower() in ["true"]

def dirExec():
    """
    Returns the directory of execution

    @return:
    @rtype:
    """
    arg = sys.argv[0]
    pathname = os.path.dirname(arg)
    full = os.path.abspath(pathname)
    return full

def displayToValue(value):
    """
    Convert back to value

    @param value: 
    @type value:

    @return:
    @rtype:
    """
    if sys.version_info < (3,):
        value = value.toString()
    return unicode(value)

def createButton(parent, icon=None, text=None, triggered=None, tip=None, toggled=None):
    """
    Create a QToolButton

    @param parent: 
    @type parent:

    @param icon: 
    @type icon:

    @param text: 
    @type text:

    @param triggered: 
    @type triggered:

    @param tip: 
    @type tip:

    @param toggled: 
    @type toggled:

    @return:
    @rtype:
    """
    button = QToolButton(parent)
    if text is not None:
        button.setText(text)
    if icon is not None:
        button.setIcon(icon)
    if text is not None or tip is not None:
        button.setToolTip(text if tip is None else tip)
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setAutoRaise(True)
    if triggered is not None:
        button.clicked.connect(triggered)  
    return button

def createAction( parent, label, callback=None, icon = None, tip = None, shortcut = None, data = None, 
                toggled = False, tooltip=None, cb_arg=None, cb_args=None, iconText=None, checkable=None):
    """
    Create a QAction

    @param parent: 
    @type parent:

    @param label: 
    @type label:

    @param callback: 
    @type callback:

    @param icon: 
    @type icon:

    @param tip: 
    @type tip:

    @param shortcut: 
    @type shortcut:

    @param data: 
    @type data:

    @param toggled: 
    @type toggled:

    @return:
    @rtype:
    """
    action = QAction(label, parent)
    if toggled:
        if callback is not None:
            action.toggled.connect(callback)
            action.setCheckable(True)
    else:
        if callback is not None:
            if cb_arg is None:
                action.triggered.connect(callback)
            else:
                if cb_args is None:
                    action.triggered.connect(lambda: callback(cb_arg) )
                else:
                    action.triggered.connect(lambda: callback(**cb_args) )
    if icon:
        action.setIcon(icon)
    if shortcut: 
        action.setShortcut(shortcut)
    if tip: 
        action.setStatusTip(tip)
    if tooltip:
        action.setToolTip(tooltip)
    if data is not None: 
        action.setData( data )
    if iconText is not None:
        action.setIconText(iconText)
    if checkable is not None:
        action.setCheckable(checkable)
    return action

class TestWidget(QWidget):
    """
    Test widget
    """
    def __init__(self, parent, txt = "Just For Test", minHeight=None):
        """
        Constructor

        @param parent: 
        @type parent:

        @param txt: 
        @type txt:

        @param minHeight: 
        @type minHeight:
        """
        QWidget.__init__(self, parent)
        
        self.minHeight = minHeight
        self.txt = txt
        self.createWidgets()

    def createWidgets (self):
        """
        Create qt widget
        """
        layout = QHBoxLayout()
        self.label = QLabel(self.txt, self)
        layout.addWidget( self.label  )
        self.setLayout( layout )
        if self.minHeight is not None:
            self.setMinimumHeight(self.minHeight)
    
    def active(self):
        """
        Active the widget
        """
        self.setEnabled(True)
        self.label.setEnabled(True)
    
    def deactive(self):
        """
        Deactive the widget
        """
        self.setEnabled(False)
        self.label.setEnabled(False)

def random_colour(min=20, max=200):
    """
    Return a random color

    @param min: 
    @type min:

    @param max: 
    @type max:
    """
    func = lambda: int(random.random() * (max-min) + min)
    r, g, b = func(), func(), func()
    return QColor().setRgb(r, g, b)

class PieChart(QWidget):
    """
    Pie chart widget
    """
    __startAngle = 0
    __datas = []
    def __init__(self, parent = None):
        """
        Constructor

        @param txt: 
        @type txt:
        """
        QWidget.__init__(self, parent)

    def paintEvent(self, event):
        """
        On paint event

        @param txt: 
        @type txt:
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = QSize(1, 1)
        size.scale(self.width() - 1, self.height() - 1, Qt.KeepAspectRatio)

        matrix = QTransform()
        matrix.translate((self.width() - size.width()) / 2, (self.height() - size.height()) / 2)
        painter.setWorldTransform(matrix)
        
        self.__startAngle = 0
        for __data in self.__datas:
            self.drawData(painter, size, __data[0], __data[1], __data[2])
        self.__startAngle = 0
        for __data in self.__datas:
            self.drawText(painter, size, __data[0], __data[1], __data[2])
  
    def drawData(self, painter, size, angle, dataname, color):
        """
        Draw data

        @param painter: 
        @type painter:

        @param size: 
        @type size:

        @param angle: 
        @type angle:

        @param dataname: 
        @type dataname:

        @param color: 
        @type color:
        """
        col1 = QColor(color)
        col2 = QColor(color)
        col3 = QColor(color)
        col1 = col1.lighter(105)
        col2 = col1.darker(140)
        col3 = col3.darker()
        gradient = QRadialGradient(QPointF(size.width() / 2, size.height() / 2), size.width() / 2 - 20)
        gradient.setColorAt(0.0, col1)
        gradient.setColorAt(0.6, col2)
        gradient.setColorAt(1.0, col3)
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawPie(QRect(20, 20, size.width() - 40, size.height() - 40), self.__startAngle, angle)
        self.__startAngle = self.__startAngle + angle
  
  
    def drawText(self, painter, size, angle, dataname, color):
        """
        Draw text 

        @param painter: 
        @type painter:

        @param size: 
        @type size:

        @param angle: 
        @type angle:

        @param dataname: 
        @type dataname:

        @param color: 
        @type color:
        """
        x = 0;
        y = 0;

        start = float(self.__startAngle) / 16.0;
        end   = float(self.__startAngle + angle) / 16.0;
        a = (start + end) / 2.0;
        x = math.cos((180.0 + a) / 180.0 * math.pi) * (size.width() / 2.5)
        y = math.sin(a / 180.0 * math.pi) * (size.height() / 2.5)

        font = self.font()
        font.setBold(True)
        painter.setFont(font)

        painter.setOpacity(0.5);
        painter.setPen(Qt.black)
        painter.drawText(QRect(size.width() / 2 - x - 99, size.height() / 2 - y -19, 200, 40), Qt.AlignCenter, dataname)
        painter.setOpacity(0.8);
        painter.setPen(Qt.lightGray)
        painter.drawText(QRect(size.width() / 2 - x - 100, size.height() / 2 - y -20, 200, 40), Qt.AlignCenter, dataname)
        painter.setOpacity(1.0);
        self.__startAngle = self.__startAngle + angle

  
    def minimumSizeHint(self):
        """
        Minimum size hint
        """
        return QSize(80, 80)
  
    def itemsCount(self):
        """
        Return the number of items
        """
        return len(self.__datas)
  
    def removeItem(self, index):
        """
        Remove item

        @param index: 
        @type index:
        """
        self.__datas.pop(index)
        self.update()
  
    def addItem(self, currentValue, maxValue, nameValue, colorValue=None):
        """
        Add item

        @param currentValue: 
        @type currentValue:

        @param maxValue: 
        @type maxValue:

        @param nameValue: 
        @type nameValue:

        @param colorValue: 
        @type colorValue:
        """
        percentValue = round( ( 100 * currentValue ) / maxValue , 1 )
        percentValueStr = str(percentValue) + " %"
        angle = int(360.0 * 16.0 * (float(currentValue) / maxValue))
        if colorValue is None:
            colorValue = random_colour()
        nameValue = "%s (%s)" % (nameValue, percentValueStr)
        self.__datas.append([angle, nameValue, colorValue])
        self.update()
  
    def removeItems(self):
        """
        Remove all items
        """
        self.__datas = []
        self.update()