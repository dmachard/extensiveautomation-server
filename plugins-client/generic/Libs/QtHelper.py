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
Helper for QT
"""

try:
	from PyQt4.QtGui import (QColor, QToolButton, QApplication, QTextEdit, QWidget, 
							QLineEdit, QPushButton, QHBoxLayout, QLabel, QDialog, QIcon, 
							QDesktopWidget, QVBoxLayout, QSizePolicy, QMovie, QProgressBar, 
							QPixmap, QAction, QPainter, QRadialGradient, QTransform)
	from PyQt4.QtCore import (Qt, pyqtSignal, QVariant, QSize, QPointF, QRect)
	from PyQt4.Qsci import (QsciScintilla, QsciLexerPython, QsciLexerXML)
except ImportError:
	from PyQt5.QtGui import (QColor, QIcon, QMovie, QPixmap, QPainter, QRadialGradient, QTransform)
	from PyQt5.QtWidgets import (QToolButton, QApplication, QTextEdit, QWidget, QLineEdit, 
							QPushButton, QHBoxLayout, QLabel, QDialog, QDesktopWidget, 
							QVBoxLayout, QSizePolicy, QProgressBar, QAction)
	from PyQt5.QtCore import (Qt, pyqtSignal, QVariant, QSize, QPointF, QRect)
	from PyQt5.Qsci import (QsciScintilla, QsciLexerPython, QsciLexerXML)
	
import os
import sys
import imp
import random
import math
import time

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

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
        #action.setData( QVariant(data) )
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
