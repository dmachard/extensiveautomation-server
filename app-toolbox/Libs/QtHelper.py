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
Qt helper
"""

try:
	from PyQt4.QtCore import (pyqtSignal, Qt, QVariant, QSize, QPointF, QRect)
	from PyQt4.QtGui import (QColor, QDialog, QDesktopWidget, QHBoxLayout, 
							QPushButton, QProgressBar, QToolButton, QLabel,
							QAction, QWidget, QPainter, QPixmap, QIcon,
							QVBoxLayout)
except ImportError:
	from PyQt5.QtCore import (pyqtSignal, Qt, QVariant, QSize, QPointF, QRect)
	from PyQt5.QtWidgets import (QDesktopWidget, QDialog, QPushButton, QProgressBar, 
								QToolButton, QAction, QWidget, QLabel)
	from PyQt5.QtGui import (QColor, QIcon, QPixmap, QPainter)
	
import os
import sys
import imp
import random
import math
import time

CHART_COLOR_BLUE    = QColor(0, 0, 255, 200)
CHART_COLOR_RED     = QColor(255, 0, 0, 200)
CHART_COLOR_BLACK   = QColor(9, 0, 0, 200)
CHART_COLOR_GREEN   = QColor(0, 128, 0, 200)
CHART_COLOR_GREY    = QColor(176, 176, 176, 200)
CHART_COLOR_ORANGE  = QColor(237, 189, 45, 200)

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
    Bytes 2 human convertion
    
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



class QDialogEnhanced(QDialog):
    """
    Qt dialog enhanced
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
    Progress dialog
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
        Close event
        
        @param event: 
        @type event:
        """
        pass

    def setDownload(self, title, txt, url):
        """
        Set dialog for download purpose
        
        @param title: 
        @type title:

        @param txt: 
        @type txt:

        @param url: 
        @type url:
        """
        self.url = url
        self.setWindowTitle( title  )
        self.progressBar.hide()
        self.imageLabel.setPixmap(QPixmap(':/information.png'))
        self.loadingLabel.setText( txt )
        self.downloadButton.show()
        self.cancelButton.show()
        self.okButton.hide()
        self.imageLabel.show()
    
    def setTxt (self, title, txt, error=False):
        """
        Set dialog with text
        
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
        Set dialog for loading
        
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
        Set connection message
        """
        self.loadingLabel.setText( "Connection..." )

    def setInitialization (self ):
        """
        Set init message
        """
        self.loadingLabel.setText( "Initialization..." )
        self.show()

    def download (self):
        """
        Emit download signla
        """
        self.Download.emit(self.url)

    def onReject(self):
        """
        On cancel
        """
        self.DownloadCanceled.emit()
        self.reject()
        
    def updateDataReadProgress(self, bytesRead, totalBytes):
        """
        Update progress bar
        
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
    value = value.toString()
    return unicode(value)


def createButton(parent, icon=None, text=None, triggered=None, tip=None):
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
                toggled = False, tooltip=None, cb_arg=None, iconText=None, checkable=None):
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
                action.triggered.connect(lambda: callback(cb_arg) )
    if icon:
        action.setIcon(icon)
    if shortcut: 
        action.setShortcut(shortcut)
    if tip: 
        action.setStatusTip(tip)
    if tooltip:
        action.setToolTip(tooltip)
    if data is not None: 
        action.setData( QVariant(data) )
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
        #
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
    Return random colour 
    
    @param txt: 
    @type txt:

    @param txt: 
    @type txt:
    """
    func = lambda: int(random.random() * (max-min) + min)
    r, g, b = func(), func(), func()
    return QColor().setRgb(r, g, b)