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
Document viewer module
"""
# import standard libraries
import datetime
import base64
import json
import zlib
import os
try:
    import pickle
except ImportError: # python3 support
    import cPickle as pickle
import sys
import copy

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication, QCursor, QFrame, 
                            QPixmap, QMessageBox, QDesktopServices, QTabWidget, QToolBar, 
                            QIcon, QKeySequence, QMenu, QDialog, QTextDocument, 
                            QPrinter, QPrintPreviewDialog,
                            QFileDialog, QToolButton, QTabBar)
    from PyQt4.QtCore import (Qt, pyqtSignal, QUrl, QSize, QFile, QIODevice)
except ImportError:
    from PyQt5.QtGui import (QCursor, QPixmap, QDesktopServices, QIcon, QKeySequence, QTextDocument)
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication, 
                                QFrame, QMessageBox, QTabWidget, QToolBar, QMenu, 
                                QDialog,  QFileDialog, 
                                QToolButton, QTabBar)
    from PyQt5.QtPrintSupport import (QPrinter, QPrintPreviewDialog)
    from PyQt5.QtCore import (Qt, pyqtSignal, QUrl, QSize, QFile, QIODevice)
    
try:
    from PythonEditor import FindReplace
    from PythonEditor import PyEditor
    from PythonEditor import EditorWidget
except ImportError: # python3 support
    from .PythonEditor import FindReplace
    from .PythonEditor import PyEditor
    from .PythonEditor import EditorWidget
    
from Libs import QtHelper, Logger

try:
    import TestUnit
    import TestSuite
    import TestPlan
    import TestConfig
    import TestAdapter
    import TestLibrary
    import TestTxt
    import TestData
    import TestPng
    import TestAbstract
except ImportError: # python3 support
    from . import TestUnit
    from . import TestSuite
    from . import TestPlan
    from . import TestConfig
    from . import TestAdapter
    from . import TestLibrary
    from . import TestTxt
    from . import TestData
    from . import TestPng
    from . import TestAbstract
    
import Settings

import TestResults
import UserClientInterface as UCI
import RestClientInterface as RCI

import Workspace.FileModels.TestData as FileModelTestData
import Workspace.FileModels.TestSuite as FileModelTestSuite
import Workspace.FileModels.TestUnit as FileModelTestUnit
import Workspace.FileModels.TestAbstract as FileModelTestAbstract
import Workspace.FileModels.TestPlan as FileModelTestPlan

try:
    import ScheduleDialog as SchedDialog
    import RunsDialog as RunsDialog
except ImportError: # python3 support
    from . import ScheduleDialog as SchedDialog
    from . import RunsDialog as RunsDialog
    
try:
    import Queue
except ImportError: # support python 3
    import queue as Queue
    
TAB_LOCAL_POS       =   0
TAB_REMOTE_POS      =   1
TAB_ADAPTER_POS     =   2
TAB_LIBRARY_POS     =   3

def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val

class QLabelEnhanced(QWidget):
    """
    Label enhanced widget
    """
    def __init__ (self, parent = None, linkId=None):
        """
        Constructor for qlabel
        """
        super(QLabelEnhanced, self).__init__(parent)
        
        self.linkId = linkId
        
        self.setMouseTracking(True)
        self.createWidgets()
        
    def createWidgets(self):
        """
        Create widgets
        """
        self.textQVBoxLayout = QVBoxLayout()

        self.textUpQLabel    = QLabel()
        self.textDownQLabel  = QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.textQVBoxLayout.setSpacing(0)
        
        self.allQHBoxLayout  = QHBoxLayout()
        self.iconQLabel      = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.allQHBoxLayout.setContentsMargins(0, 0, 0, 0)     
        self.allQHBoxLayout.setSpacing(0)
        
        # set the main layout
        self.setLayout(self.allQHBoxLayout)
        
        # setStyleSheet
        self.setStyleSheet("""
                             QWidget {
                                margin-left: 10px;
                               padding-top: 6px;
                             } """
                           )
        
        self.textUpQLabel.setStyleSheet("""
            margin: 0 0 0 0;
            padding: 15px 0 0 2px;
            color: black;
            font-weight: bold;
            font-size: 12px;
        """)
        self.textDownQLabel.setStyleSheet("""
            margin: 0 0 0 0;
            padding: -10px 0 0 2px;
            color: #6B6B6B;
        """)
        self.iconQLabel.setStyleSheet("""
            padding-left: 2px;
        """)
    
    def mouseReleaseEvent(self, event):
        """
        On mouse release
        """
        event.accept()
        self.onClicked(linkId=self.linkId)
        
    def onClicked(self, linkId=None):
        """
        Function to reimplement
        """
        pass
        
    def enterEvent (self, event):
        """
        On mouse move event
        """
        if not self.isEnabled():
            event.accept()
        else:
            self.setStyleSheet( """
                             QWidget {
                                background: #D7DCE0;
                                   margin-left: 10px;
                                   padding-top: 6px;
                             } """)
            event.accept()

    def leaveEvent (self, event):
        """
        On mouse move event
        """
        if not self.isEnabled():
            event.accept()
        else:
            #  background: #EAEAEA;
            self.setStyleSheet( """
                             QWidget {
                                   margin-left: 10px;
                                   padding-top: 6px;
                             } """)
            event.accept()
    
    def disable(self):
        """
        Disable the widget
        """
        self.setEnabled(False)
        
    def setTextLink (self, text):
        """
        Set the text of the link
        """
        self.textUpQLabel.setText(text)

    def setTextDescription (self, text):
        """
        Set the text description
        """
        self.textDownQLabel.setText(text)

    def setTextDescriptionBis (self, text):
        """
        Set the text description
        """
        self.textDown2QLabel.setText(text)

    def setIcon (self, icon):
        """
        Set the icon
        """
        self.iconQLabel.setPixmap(icon)

class WelcomePage(QWidget):
    """
    Welcome page widget
    """
    LinkConnect = pyqtSignal() 
    LinkDisconnect = pyqtSignal() 
    LinkTax = pyqtSignal() 
    LinkTux = pyqtSignal() 
    LinkTsx = pyqtSignal() 
    LinkTpx = pyqtSignal() 
    LinkTgx = pyqtSignal() 
    LinkBasicMacro = pyqtSignal() 
    LinkMacro = pyqtSignal() 
    LinkWebMacro = pyqtSignal() 
    LinkMobileMacro = pyqtSignal() 
    LinkSysMacro = pyqtSignal() 
    LinkPlugin = pyqtSignal(str)  
    OpenWeb = pyqtSignal()  
    OpenProductWeb = pyqtSignal()  
    def __init__(self, parent):
        """
        Welcome page constructor
        """
        QWidget.__init__(self, parent)
        self.connectClicked = False
        self.plugins = {}
        
        self.createWidgets()
    
    def createWidgets(self):
        """
        Create widgets
        """
        mainLayout = QHBoxLayout()
        
        # main left frame
        leftFrame = QFrame(self)
        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)     
        leftFrame.setLayout(leftLayout)

        # main right frame   
        rightFrame = QFrame(self)
        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)     
        rightFrame.setLayout(rightLayout)
        
        # prepare the product frame
        self.productFrame = QFrame(self)
        productLayout = QVBoxLayout()
        self.productFrame.setLayout(productLayout)
        titleProduct = QLabel("Product Information")
        titleProduct.setStyleSheet( """
                         QLabel {
                            background: #0C9105;
                            color: white;
                            padding: 4px;
                            font-weight: bold;
                         } """)
        self.productLink = QLabelEnhanced(self)
        self.productLink.setTextLink( Settings.instance().readValue( key = 'Common/product-name' ) )
        self.productLink.setTextDescription("Visit the project's website")
        self.productLink.setIcon(QPixmap(":/logo.png") )
        self.productLink.onClicked = self.onProductLinkClicked
        
        productLayout.addWidget(titleProduct)
        productLayout.addWidget(self.productLink)
        productLayout.setSpacing(0)
        productLayout.addStretch(1)
        
        # prepare the generators frame
        self.devFrame = QFrame(self)
        self.devFrame.setEnabled(False)
        self.devLayout = QVBoxLayout()
        self.devFrame.setLayout(self.devLayout)
        titleDev = QLabel("Plugins")
        titleDev.setStyleSheet( """
                         QLabel {
                            background: #0C9105;
                            color: white;
                            padding: 4px;
                            font-weight: bold;
                         } """)

        self.devLayout.addWidget(titleDev)
        self.devLayout.setSpacing(0)
        self.devLayout.addStretch(1)
        
        #*****************************************#
        # prepare the generators frame
        self.captureFrame = QFrame(self)
        self.captureFrame.setEnabled(False)
        capturetLayout = QVBoxLayout()
        self.captureFrame.setLayout(capturetLayout)
        titleCapture = QLabel("Automation Assistant")
        titleCapture.setStyleSheet( """
                         QLabel {
                            background: #0C9105;
                            color: white;
                            padding: 4px;
                            font-weight: bold;
                         } """)
                         
        self.basicLink = QLabelEnhanced(self)
        self.basicLink.setTextLink("New Basic Test")
        self.basicLink.setTextDescription("Simple testing")
        self.basicLink.setIcon(QPixmap(":/recorder-basic.png") )
        self.basicLink.onClicked = self.onBasicLinkClicked
        
        self.sysLink = QLabelEnhanced(self)
        self.sysLink.setTextLink("New System Test")
        self.sysLink.setTextDescription("System testing")
        self.sysLink.setIcon(QPixmap(":/recorder-system.png") )
        self.sysLink.onClicked = self.onSysLinkClicked
        
        self.captureLink = QLabelEnhanced(self)
        self.captureLink.setTextLink("New Application Test")
        self.captureLink.setTextDescription("Graphical user interface testing")
        self.captureLink.setIcon(QPixmap(":/recorder-app.png") )
        self.captureLink.onClicked = self.onCaptureLinkClicked
        
        self.captureWebLink = QLabelEnhanced(self)
        self.captureWebLink.setTextLink("New Web Test")
        self.captureWebLink.setTextDescription("Graphical user interface testing")
        self.captureWebLink.setIcon(QPixmap(":/recorder-web.png") )
        self.captureWebLink.onClicked = self.onCaptureWebLinkClicked
        
        self.captureMobileLink = QLabelEnhanced(self)
        self.captureMobileLink.setTextLink("New Mobile Test")
        self.captureMobileLink.setTextDescription("Graphical user interface testing")
        self.captureMobileLink.setIcon(QPixmap(":/recorder-mobile.png") )
        self.captureMobileLink.onClicked = self.onCaptureMobileLinkClicked

        capturetLayout.addWidget(titleCapture)
        capturetLayout.addWidget(self.basicLink)
        capturetLayout.addWidget(self.sysLink)
        capturetLayout.addWidget(self.captureLink)
        capturetLayout.addWidget(self.captureWebLink)
        capturetLayout.addWidget(self.captureMobileLink)
        capturetLayout.setSpacing(0)
        capturetLayout.addStretch(1)
        
        # prepare the get started frame
        self.connectFrame = QFrame(self)
        self.connectFrame.setStyleSheet( """
                         QFrame {
                            padding: 0px;
                         } """)
        connectLayout = QVBoxLayout()

        title = QLabel("Get Started") #0C9105 #6B6B6B
        title.setStyleSheet( """
                         QLabel {
                            background: #0C9105;
                            color: white;
                            padding: 4px;
                            font-weight: bold;
                         } """)
        self.connectLink = QLabelEnhanced(self)
        self.connectLink.setTextLink("Log In")
        self.connectLink.setTextDescription("Connection to the automation center")
        self.connectLink.setIcon(QPixmap(":/connect.png") )
        self.connectLink.onClicked = self.onConnectLinkClicked

        self.onlineLink = QLabelEnhanced(self)
        self.onlineLink.setTextLink("Online")
        self.onlineLink.setTextDescription("Website of the automation center")
        self.onlineLink.setIcon(QPixmap(":/http.png") )
        self.onlineLink.onClicked = self.onOnlineLinkClicked
        
        connectLayout.addWidget(title)
        connectLayout.addWidget(self.connectLink)
        connectLayout.addWidget(self.onlineLink)
        connectLayout.setSpacing(0)
        connectLayout.addStretch(1)
        self.connectFrame.setLayout(connectLayout)

        # prepare the files frame
        self.filesFrame = QFrame(self)
        self.filesFrame.setStyleSheet( """
                         QFrame {
                            padding: 0px;
                         } """)
        titleFiles = QLabel("New Tests")
        titleFiles.setStyleSheet( """
                         QLabel {
                            background: #0C9105;
                            color: white;
                            padding: 4px;
                            font-weight: bold;
                         } """)
                         
        self.taxLink = QLabelEnhanced(self)
        self.taxLink.setTextLink("Test Abstract")
        self.taxLink.setTextDescription("Testcase modelisation")
        self.taxLink.setIcon(QPixmap(":/tax48.png") )
        self.taxLink.onClicked = self.onTaxLinkClicked
        
        self.tuxLink = QLabelEnhanced(self)
        self.tuxLink.setTextLink("Test Unit")
        self.tuxLink.setTextDescription("Testcase scripting")
        self.tuxLink.setIcon(QPixmap(":/tux48.png") )
        self.tuxLink.onClicked = self.onTuxLinkClicked

        self.tsxLink = QLabelEnhanced(self)
        self.tsxLink.setTextLink("Test Suite")
        self.tsxLink.setTextDescription("Multiple testcases scripting")
        self.tsxLink.setIcon(QPixmap(":/tsx48.png") )
        self.tsxLink.onClicked = self.onTsxLinkClicked

        self.tpxLink = QLabelEnhanced(self)
        self.tpxLink.setTextLink("Test Plan")
        self.tpxLink.setTextDescription("Procedural test conception")
        self.tpxLink.setIcon(QPixmap(":/tpx48.png") )
        self.tpxLink.onClicked = self.onTpxLinkClicked

        self.tgxLink = QLabelEnhanced(self)
        self.tgxLink.setTextLink("Test Global")
        self.tgxLink.setTextDescription("End to end test conception")
        self.tgxLink.setIcon(QPixmap(":/tgx48.png") )
        self.tgxLink.onClicked = self.onTgxLinkClicked
        
        filesLayout = QVBoxLayout()
        filesLayout.addWidget(titleFiles)
        filesLayout.addWidget(self.taxLink)
        filesLayout.addWidget(self.tuxLink)
        filesLayout.addWidget(self.tsxLink)
        filesLayout.addWidget(self.tpxLink)
        filesLayout.addWidget(self.tgxLink)
        filesLayout.setSpacing(0)
        filesLayout.addStretch(1)
        self.filesFrame.setLayout(filesLayout)
        self.filesFrame.setEnabled(False)

        leftLayout.addWidget(self.connectFrame)
        leftLayout.addWidget(self.productFrame)
        leftLayout.addWidget(self.filesFrame)
        leftLayout.addStretch(1)
        

        rightLayout.addWidget(self.captureFrame)
        rightLayout.addWidget(self.devFrame)
        rightLayout.addStretch(1)
        
        mainLayout.addWidget(leftFrame)
        mainLayout.addWidget(rightFrame)
        mainLayout.setContentsMargins(0, 0, 0, 0)     
        self.setLayout(mainLayout)
     
    def addPlugin(self, name, description, icon=None):
        """
        Add plugin
        """
        
        plugLink = QLabelEnhanced(self, linkId=name)
        plugLink.setTextLink(name)
        plugLink.setTextDescription(description)
        if icon is not None: plugLink.setIcon( icon.pixmap(48,48) )
        plugLink.onClicked = self.onPluginLinkClicked
        
        self.devLayout.addWidget(plugLink)
        
        self.plugins[name] = plugLink
        
    def onPluginLinkClicked(self, linkId):
        """
        On plugin link clicked
        """
        self.LinkPlugin.emit(linkId)
        
    def onCaptureMobileLinkClicked(self, linkId=None):
        """
        On capture mobile link clicked
        """
        self.LinkMobileMacro.emit()
        
    def onCaptureWebLinkClicked(self, linkId=None):
        """
        On capture web link clicked
        """
        self.LinkWebMacro.emit()

    def onCaptureLinkClicked(self, linkId=None):
        """
        On capture link clicked
        """
        self.LinkMacro.emit()
        
    def onBasicLinkClicked(self, linkId=None):
        """
        On basic link clicked
        """
        self.LinkBasicMacro.emit()
        
    def onSysLinkClicked(self, linkId=None):
        """
        On basic link clicked
        """
        self.LinkSysMacro.emit()
        
    def onTaxLinkClicked(self, linkId=None):
        """
        On tax link clicked
        """
        self.LinkTax.emit()
        
    def onTuxLinkClicked(self, linkId=None):
        """
        On tux link clicked
        """
        self.LinkTux.emit()
        
    def onTsxLinkClicked(self, linkId=None):
        """
        On tsx link clicked
        """
        self.LinkTsx.emit()
        
    def onTpxLinkClicked(self, linkId=None):
        """
        On tpx link clicked
        """
        self.LinkTpx.emit()
        
    def onTgxLinkClicked(self, linkId=None):
        """
        On tgx link clicked
        """
        self.LinkTgx.emit()
        
    def onOnlineLinkClicked(self, linkId=None):
        """
        On online link clicked
        """
        if not len(UCI.instance().getHttpAddress()):
            QMessageBox.warning(self, self.tr("Website"), 
                                self.tr("Please to configure a test server."))
        else:
            self.OpenWeb.emit()

    def onProductLinkClicked(self, linkId=None):
        """
        On product link clicked
        """
        self.OpenProductWeb.emit()

    def onConnectLinkClicked(self, linkId=None):
        """
        On connect link clicked
        """
        if self.connectClicked:
            return
            
        self.connectClicked = True
        if self.connectLink.textUpQLabel.text() == 'Log In':
            self.LinkConnect.emit()
        else:
            self.LinkDisconnect.emit()
         
    def updateMacroLink(self):
        """
        Update macro link
        """
        if UCI.RIGHTS_TESTER in RCI.instance().userRights or UCI.RIGHTS_ADMIN in RCI.instance().userRights:
            self.captureLink.setEnabled(True)
            self.captureWebLink.setEnabled(True)
            self.captureMobileLink.setEnabled(True)
            self.basicLink.setEnabled(True)
            self.sysLink.setEnabled(True)
        else:
            self.captureLink.setEnabled(False)
            self.captureWebLink.setEnabled(False)
            self.captureMobileLink.setEnabled(False)
            self.basicLink.setEnabled(False)
            self.sysLink.setEnabled(False)
            
    def updateConnectLink(self, connected=False):
        """
        Update connect link
        """
        self.connectClicked = False
        if connected:
            if UCI.RIGHTS_TESTER in RCI.instance().userRights or UCI.RIGHTS_ADMIN in RCI.instance().userRights:
                self.filesFrame.setEnabled(True)
                self.devFrame.setEnabled(True)
                
            if self.connectLink.textUpQLabel.text() == 'Log Out':
                return
                
            self.connectLink.setTextLink("Log Out")
            self.connectLink.setTextDescription("Disconnection from the automation center")
            self.connectLink.setIcon(QPixmap(":/disconnect.png") )
            self.captureFrame.setEnabled(True)
        else:
            self.filesFrame.setEnabled(False)
            self.captureFrame.setEnabled(False)
            self.devFrame.setEnabled(False)
            if self.connectLink.textUpQLabel.text() == 'Log In':
                return
            self.connectLink.setTextLink("Log In")
            self.connectLink.setTextDescription("Connection to the automation center")
            self.connectLink.setIcon(QPixmap(":/connect.png") )
            
class WorkspaceTab(QTabWidget):
    """
    Workspace tab widget
    """
    def __init__(self, parent):
        """
        Constructor
        """
        QTabWidget.__init__(self, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """
        Drag enter event
        """
        if event.mimeData().hasFormat('application/x-%s-repo-openfile' % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.accept()
        else:
            QTabWidget.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        """
        Drag move event
        """
        if event.mimeData().hasFormat("application/x-%s-repo-openfile" % Settings.instance().readValue( key = 'Common/acronym' ).lower()):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            QTabWidget.dragMoveEvent(self, event)

    def dropEvent(self, event):
        """
        Drop event
        """
        if (event.mimeData().hasFormat('application/x-%s-repo-openfile' % Settings.instance().readValue( key = 'Common/acronym' ).lower() )):
            event.acceptProposedAction()
            
            # extract data from drag
            data = pickle.loads( event.mimeData().data("application/x-%s-repo-openfile" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ) )
            if data['repotype'] == UCI.REPO_TESTS_LOCAL:
                instance().newTab(path = data['pathfile'], filename = data['filename'], extension = data['ext'],
                            remoteFile=False, contentFile=None, repoDest=data['repotype'])
            else: 
                # open the file from the remote repo
                if data['repotype'] == UCI.REPO_TESTS:
                    RCI.instance().openFileTests(projectId=data['projectid'], 
                                                 filePath=data['pathfile'])
                elif data['repotype'] == UCI.REPO_ADAPTERS:
                    RCI.instance().openFileAdapters(filePath=data['pathfile'], 
                                                    ignoreLock=False, readOnly=False)
                elif data['repotype'] == UCI.REPO_LIBRARIES:
                    RCI.instance().openFileLibraries(filePath=data['pathfile'], 
                                                     ignoreLock=False, readOnly=False)
                else:
                    pass
                    
        else:
            QTabWidget.dropEvent(self, event)   

class WDocumentViewer(QWidget, Logger.ClassLogger):
    """
    Document viewer widget
    """
    DocumentViewerEmpty = pyqtSignal()
    UpdateWindowTitle = pyqtSignal(str)
    CurrentDocumentChanged = pyqtSignal(str) 
    RefreshLocalRepository = pyqtSignal()
    DocumentOpened = pyqtSignal(object)
    RecentFile = pyqtSignal(dict)
    CurrentDocumentChanged = pyqtSignal(object)
    BusyCursor = pyqtSignal() 
    ArrowCursor = pyqtSignal() 
    # new in v10.1
    LinkConnect = pyqtSignal() 
    LinkDisconnect = pyqtSignal() 
    # new in v11
    LinkMacro = pyqtSignal() 
    LinkWebMacro = pyqtSignal() 
    LinkMobileMacro = pyqtSignal() 
    LinkBasicMacro = pyqtSignal()
    LinkSysMacro = pyqtSignal()     
    OpenWeb = pyqtSignal()
    OpenWebProduct = pyqtSignal()
    GoMacroMode = pyqtSignal(bool, bool) 
    # new in v15
    LinkPlugin = pyqtSignal(str) 
    TotalLinesChanged = pyqtSignal(int)
    CursorPositionChanged = pyqtSignal(int, int)
    FocusChanged = pyqtSignal(object)
    PropertiesChanged = pyqtSignal(dict, bool, str)
    NbReplaced = pyqtSignal(int)
    # new in v16
    ShowPropertiesTab = pyqtSignal() 
    def __init__(self, parent=None, iRepo=None, lRepo=None, rRepo=None):
        """
        Constructs WDocumentViewer widget 

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.iRepo = iRepo
        self.lRepo = lRepo
        self.rRepo = rRepo
        self.nonameIdTs = 1
        self.nonameIdTp = 1
        self.nonameIdTa = 1
        self.tab = None
        self.welcomePage = None

        self.codeWrapping = QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/code-wrapping' ) )
        self.codeFolding = QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/code-folding' ) )
        self.indentationGuidesVisible = QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/indent-guides-visible' ) )
        self.whitespaceVisible = QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/ws-visible' ) )
        self.linesNumbering = QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/lines-numbering' ) )

        self.runsDialog = RunsDialog.RunsDialog(self, 
                                                iRepo=self.iRepo, 
                                                lRepo=self.lRepo, 
                                                rRepo=self.rRepo )

        self.createWidgets()
        self.createActions()
        self.createConnections()
        self.createToolbar()

        # add default tab
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/welcome-page' ) ):
            self.createDefaultTab()
    
    def createWidgets(self):
        """
        QtWidgets creation
         ________________________________
        |           QToolBar             |
        |________________________________|
          _________   ____
         / WTestSuite \ /... \______________
        |                                |
        |    QTabWidget            |
        | _______________________________|
         ________________________________
        |           FindReplace          |
        |________________________________|

        """
        self.tab = WorkspaceTab( self )
        self.tab.setMinimumWidth(500)
        self.tab.setDocumentMode( False )
        self.tab.setMovable( True )

        self.dockToolbar = QToolBar(self)
        self.dockToolbar2 = QToolBar(self)
        self.dockToolbar2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.findWidget = FindReplace(self)
        self.findWidget.setDisabled(True)
        self.findWidget.hide()
        
        layoutBar = QHBoxLayout()
        layoutBar.addWidget( self.dockToolbar )

        layoutBar2 = QHBoxLayout()
        layoutBar2.addWidget( self.dockToolbar2 )

        layout = QVBoxLayout()
        layout.addLayout( layoutBar )
        layout.addLayout( layoutBar2 )
        layout.addWidget( self.tab )
        layout.setContentsMargins(0,0,0,0)

        
        self.setLayout(layout)
    
    def createConnections(self):
        """
        create qt connections
        """
        self.runsDialog.RefreshRepository.connect(self.onProjectChangedInRuns)

        self.tab.tabCloseRequested.connect(self.closeTab)
        self.tab.currentChanged.connect(self.currentTabChanged)
        
        self.findWidget.NbReplaced.connect(self.onNbReplaced)

    def createActions (self):
        """
        create qt actions reimplementation from PyEditor
        Because there are two editors in this widget, then a global callback function is used 
        to dispatch actions between theses editors
        
        Actions defined:
         * undo
         * redo
         * cut
         * copy
         * paste
         * delete
         * comment
         * uncomment
         * select all
         * indent
         * unindent
         * run
        """
        self.closeTabAction = QtHelper.createAction(self, self.tr("Close"), self.closeCurrentTab,
                                        tip = 'Closes the current document')
        self.closeAllTabAction = QtHelper.createAction(self, self.tr("Close All"), self.closeAllTab, 
                                        tip = 'Closes all document')
        
        self.newTestAbstractAction = QtHelper.createAction(self, "Test Abstract", self.newTestAbstract,
                                        icon = QIcon(":/%s.png" % TestAbstract.TYPE), 
                                        tip = 'Creates a new test abstract')

        self.newTestUnitAction = QtHelper.createAction(self, "Test Unit", self.newTestUnit,
                                        icon = QIcon(":/%s.png" % TestUnit.TYPE), 
                                        tip = 'Creates a new test unit')
        self.newTestConfigAction = QtHelper.createAction(self, "Test Config", self.newTestConfig,
                                        icon = QIcon(":/%s.png" % TestConfig.TYPE), 
                                        tip = 'Creates a new test config')
        self.newTestSuiteAction = QtHelper.createAction(self, "Test Suite", self.newTestSuite,
                                        icon = QIcon(":/%s.png" % TestSuite.TYPE), 
                                        shortcut = "Ctrl+N", tip = 'Creates a new test suite')
        self.newTestPlanAction = QtHelper.createAction(self, "Test Plan", self.newTestPlan,
                                        icon = QIcon(":/%s.png" % TestPlan.TYPE), 
                                        tip = 'Creates a new test plan')
        self.newTestGlobalAction = QtHelper.createAction(self, "Test Global", self.newTestGlobal,
                                        icon = QIcon(":/%s.png" % TestPlan.TYPE_GLOBAL), 
                                        tip = 'Creates a new test global')
        self.newTestDataAction = QtHelper.createAction(self, "Test Data", self.newTestData,
                                        icon = QIcon(":/%s.png" % TestData.TYPE), 
                                        tip = 'Creates a new test data')
        self.newAdapterAction = QtHelper.createAction(self, "Adapter", self.newTestAdapter,
                                        icon = QIcon(":/file-adp2.png"), tip = 'Creates a new adapter')
        self.newLibraryAction = QtHelper.createAction(self, "Library", self.newTestLibrary,
                                        icon = QIcon(":/file-lib-adp.png"), tip = 'Creates a new library')
        self.newTxtAction = QtHelper.createAction(self, "Txt", self.newTestTxt,
                                        icon = QIcon(":/file-txt.png"), tip = 'Creates a new txt')

        self.openAction = QtHelper.createAction(self, self.tr("Open"), self.openDoc,
                                        icon = QIcon(":/open-test.png"), shortcut = "Ctrl+O", tip = 'Open')
        self.saveAction = QtHelper.createAction(self, self.tr("Save"), self.saveTab, 
                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/save' ),
                                        icon = QIcon(":/save-test.png"), 
                                        tip = 'Saves the active document')
        self.saveAsAction = QtHelper.createAction(self, self.tr("Save As"), self.saveTabAs,
                                        icon = QIcon(":/filesave.png"), tip = 'Saves the active document as ...')
        self.exportAsAction = QtHelper.createAction(self, self.tr("Export"), self.exportTabAs,
                                        icon = None, tip = 'Export the active document as ...')

        self.saveAllAction = QtHelper.createAction(self, self.tr("Save all"), self.saveAllTabs,
                                        icon = QIcon(":/save_all.png"), tip = 'Saves all documents')

        self.printAction = QtHelper.createAction(self, self.tr("Print"), self.printDoc,
                                        icon = QIcon(":/printer.png"), tip = 'Print the current document', 
                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/print' ) )

        self.undoAction = QtHelper.createAction(self, self.tr("Undo"), callback = self.globalCallback,
                                        icon = QIcon(":/undo.png"),  data='undo', 
                                        shortcut = "Ctrl+Z", tip = 'Undoes the last action' )
        self.redoAction = QtHelper.createAction(self, self.tr("Redo"), callback = self.globalCallback, 
                                        icon = QIcon(":/redo.png"), data='redo', 
                                        shortcut = "Ctrl+Y", tip = 'Redoes the previously undone action' )
        self.cutAction = QtHelper.createAction(self, self.tr("Cut"), callback = self.globalCallback,
                                        shortcut = QKeySequence.Cut, data='cut', 
                                        tip = 'Cuts the selection and puts it on the clipboard' )
        self.copyAction = QtHelper.createAction(self, self.tr("Copy"), callback = self.globalCallback,
                                        shortcut = QKeySequence.Copy, data='copy', 
                                        tip = 'Copies the selection and puts it on the clipboard' )
        self.copyAction.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.pasteAction = QtHelper.createAction(self, self.tr("Paste"), callback = self.globalCallback,
                                        data='paste', shortcut = QKeySequence.Paste, 
                                        tip = 'Inserts clipboard contents' )
        self.pasteAction.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.deleteAction = QtHelper.createAction( self, "Delete Selection", callback = self.globalCallback,
                                        data='removeSelectedText', tip = 'Deletes the selection' )
        self.commentAction = QtHelper.createAction(self, "Comment", callback = self.globalCallback,
                                        icon = QIcon(":/comment.png"), data='comment', 
                                        tip = 'Insert comment sign at the begining of line' )
        self.uncommentAction = QtHelper.createAction(self, "Uncomment", callback = self.globalCallback,
                                        icon =  QIcon(":/uncomment.png"), data='uncomment', 
                                        tip = 'Remove comment sign at the begining of line' )
        self.selectAllAction = QtHelper.createAction(self, "Select All", self.globalCallback, 
                                        QIcon(":/select_all.png"), data='selectAll', 
                                        tip = 'Selects the entire document' )
        self.indentAction = QtHelper.createAction(self, "Indent", self.globalCallback, data='indent', 
                                        shortcut = "Tab", tip = 'Indent current line or selection' )
        self.unindentAction = QtHelper.createAction(self, "Unindent", self.globalCallback, data='unindent', 
                                        shortcut = "Shift+Tab", tip = 'Unindent current line or selection' )
        
        self.foldAllAction = QtHelper.createAction(self, "Fold/Unfold all", callback = self.globalCallback,
                                        icon = QIcon(":/toggle-expand.png"), 
                                        data='foldAllLines', tip = 'Fold all lines' )
        self.codefoldingAction = QtHelper.createAction(self, "Code Folding", self.toggleCodeFolding, 
                                        icon =  QIcon(":/folding.png"), toggled = True)
        self.codefoldingAction.setChecked( self.codeFolding )
        self.whitespaceVisibilityAction = QtHelper.createAction(self, "Show whitespace and tabulation", 
                                        self.toggleWhitespaceVisibility, toggled = True)
        self.whitespaceVisibilityAction.setChecked( self.whitespaceVisible )
        self.indentGuidesVisibilityAction = QtHelper.createAction(self, "Show indentation guides", 
                                        self.toggleIndentGuidesVisibility, toggled = True)
        self.indentGuidesVisibilityAction.setChecked( self.indentationGuidesVisible )
        self.linesNumberingAction = QtHelper.createAction(self, "Line Numbering", self.toggleLineNumbering, 
                                        toggled = True)
        self.linesNumberingAction.setChecked( self.linesNumbering )
        self.codeWrappingAction = QtHelper.createAction(self, "Code Wrapping", self.toggleCodeWrapping, 
                                        icon =  None, toggled = True)
        self.codeWrappingAction.setChecked( self.codeWrapping )
        
        
        self.runAction = QtHelper.createAction(self, "Execute", self.runDocument,
                                        tip = 'Executes the current test', icon=QIcon(":/test-play.png") )
        
        self.runNowAction = QtHelper.createAction(self, "Immediately", self.runDocument,
                                        tip = 'Executes the current test',
                                        shortcut=Settings.instance().readValue( key = 'KeyboardShorcuts/run' ) )
        self.runMinimizeAction = QtHelper.createAction(self, "Immediately + Minimize", self.runDocumentMinimize,
                                        tip = 'Executes the current test and minimize the application' )
        self.runReduceAction = QtHelper.createAction(self, "Immediately + Reduce", self.runDocumentReduce,
                                        tip = 'Executes the current test and reduce the application' )
        self.runBackgroundAction = QtHelper.createAction(self, "Background", self.runDocumentInBackground,
                                        tip = 'Executes the current test in background')

        self.runWithoutProbesAction = QtHelper.createAction(self, "Without probes", self.runDocumentWithoutProbes,
                                        tip = 'Executes the current test without probes', 
                                        icon=QIcon(":/test-play-without-probes.png") )
        self.runDebugAction = QtHelper.createAction(self, "&Debug", self.runDocumentDebug,
                                        tip = 'Executes the current test with debug traces on server' )
        self.runWithoutNotifAction = QtHelper.createAction(self, "&Without notifications", self.runDocumentWithoutNotif,
                                        tip = 'Executes the current test without mail notifications' )
        self.runNoKeepTrAction = QtHelper.createAction(self, "&Do not keep test result", self.runDocumentNoKeepTr,
                                        tip = 'Do not keep test result on archive' )

        self.runSchedAction = QtHelper.createAction(self, self.tr("Schedule"), self.schedRunDocument,
                                        icon =  QIcon(":/schedule.png"), 
                                        tip = self.tr('Scheduling a run of the current tab') )
        
        self.runSeveralAction = QtHelper.createAction(self, self.tr("Grouped"), self.runSeveralTests,
                                        icon =  QIcon(":/test-play-several.png"), tip = self.tr('Run several tests')  )
        self.runSeveralAction.setEnabled(False)

        self.runStepByStepAction = QtHelper.createAction(self, "Steps", self.runDocumentStepByStep,
                                        tip = 'Execute the current test step by step', 
                                        icon=QIcon(":/run-state.png"),
                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/steps' ) )
        self.runBreakpointAction = QtHelper.createAction(self, "Break Point", self.runDocumentBreakpoint,
                                        tip = 'Execute the current test with breakpoint', 
                                        icon=QIcon(":/breakpoint.png"),
                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/breakpoint' ) )

        self.checkSyntaxAction = QtHelper.createAction(self, self.tr("&Syntax"), self.checkSyntaxDocument,
                                        icon =  QIcon(":/check-syntax.png"), 
                                        tip = self.tr('Checking syntax of the current tab'),
                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/syntax' ) )
        self.checkDesignAction = QtHelper.createAction(self, self.tr("&Design"), self.checkDesignDocument,
                                        icon =  QIcon(":/tds.png"), 
                                        tip = self.tr('Checking design of the current tab') )
        self.updateTestAction = QtHelper.createAction(self, self.tr("&Assistant"), self.updateMacro,
                                        icon =  QIcon(":/recorder.png") , 
                                        tip = self.tr('Update the test with the automation assistant'),
                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/assistant' ) )
                             
        menu1 = QMenu(self)
        menu1.addAction( self.checkSyntaxAction )
        menu1.addAction( self.checkDesignAction )
        self.checkAction = QtHelper.createAction(self, self.tr("Prepare"), self.prepareDocument,
                                tip = self.tr('Prepare the current test'), icon=QIcon(":/warning.png") )
        self.checkAction.setMenu(menu1) 
        
        menu = QMenu(self)
        menu.addAction( self.runNowAction )
        menu.addAction( self.runBackgroundAction )
        menu.addSeparator()
        menu.addAction( self.runMinimizeAction )
        menu.addAction( self.runReduceAction )
        menu.addSeparator()
        menu.addAction( self.runWithoutNotifAction )
        menu.addAction( self.runWithoutProbesAction )
        menu.addAction( self.runNoKeepTrAction )
        menu.addSeparator()
        menu.addAction( self.runDebugAction )
        self.runAction.setMenu(menu)

        self.hideFindReplaceAction = QtHelper.createAction(self, self.tr("Find/Replace"), self.hideFindReplace,
                                                icon =  QIcon(":/find.png"), 
                                                tip = self.tr('Hide or show the find and replace window'), checkable=True)
        self.hideFindReplaceAction.setChecked(True)
        self.findAction = QtHelper.createAction(self, self.tr("Search Text"), self.searchText,
                                                icon =  QIcon(":/find.png"), tip = self.tr('Search text'),
                                                shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/search' )  )
        self.findAction.setChecked(True)
        
        self.setDefaultActionsValues()

    def createDefaultTab(self):
        """
        Create the default tab
        """
        self.welcomePage = WelcomePage(self)
        tabId = self.tab.addTab(self.welcomePage, "" )
        self.tab.setTabIcon(tabId, QIcon(":/main.png") )

        self.welcomePage.LinkConnect.connect(self.onConnectLinkClicked)
        self.welcomePage.LinkDisconnect.connect(self.onDisconnectLinkClicked)
        self.welcomePage.LinkTax.connect(self.newTestAbstract)
        self.welcomePage.LinkTux.connect(self.newTestUnit)
        self.welcomePage.LinkTsx.connect(self.newTestSuite)
        self.welcomePage.LinkTpx.connect(self.newTestPlan)
        self.welcomePage.LinkTgx.connect(self.newTestGlobal)
        self.welcomePage.LinkMacro.connect(self.onMacroLinkClicked)
        self.welcomePage.LinkBasicMacro.connect(self.onBasicMacroLinkClicked)
        self.welcomePage.LinkWebMacro.connect(self.onWebMacroLinkClicked)
        self.welcomePage.LinkMobileMacro.connect(self.onMobileMacroLinkClicked)
        self.welcomePage.OpenWeb.connect(self.onOpenWebsite)
        self.welcomePage.OpenProductWeb.connect(self.onOpenProductWebsite)
        self.welcomePage.LinkSysMacro.connect(self.onSysMacroLinkClicked)
        self.welcomePage.LinkPlugin.connect(self.onPluginLinkClicked)
        
    def onNbReplaced(self, counter):
        """
        On number line replaced
        """
        self.NbReplaced.emit(counter)
        
    def onPluginLinkClicked(self, plugId):
        """
        On plugin link clicked
        """
        self.LinkPlugin.emit(plugId)
        
    def onOpenProductWebsite(self):
        """
        On open website
        """
        self.OpenWebProduct.emit()
        
    def onOpenWebsite(self):
        """
        On open website
        """
        self.OpenWeb.emit()
        
    def updateConnectLink(self, connected=False):
        """
        Update the connect link
        """
        self.welcomePage.updateConnectLink(connected=connected)
        
    def updateMacroLink(self):
        """
        Update the macro link
        """
        self.welcomePage.updateMacroLink()

    def onWebMacroLinkClicked(self):
        """
        On macro link clicked
        """
        self.LinkWebMacro.emit()
        
    def onMobileMacroLinkClicked(self):
        """
        On macro link clicked
        """
        self.LinkMobileMacro.emit()
        
    def onMacroLinkClicked(self):
        """
        On macro link clicked
        """
        self.LinkMacro.emit()
        
    def onBasicMacroLinkClicked(self):
        """
        On basic macro link clicked
        """
        self.LinkBasicMacro.emit()
        
    def onSysMacroLinkClicked(self):
        """
        On basic macro link clicked
        """
        self.LinkSysMacro.emit()
        
    def onConnectLinkClicked(self):
        """
        On connect link clicked
        """
        self.LinkConnect.emit()
        
    def onDisconnectLinkClicked(self):
        """
        On disconnect link clicked
        """
        self.LinkDisconnect.emit()
        
    def hideRunDialogs(self):
        """
        Close the run dialog
        """
        self.runsDialog.close()

    def hideToolbars(self):
        """
        hide toolbars
        """
        self.dockToolbar.hide()
        self.dockToolbar2.hide()

    def showToolbars(self):
        """
        Show toolbars
        """
        self.dockToolbar.show()
        self.dockToolbar2.show()

    def hideDocumentBar(self):
        """
        Hide document bar
        """
        self.dockToolbar.hide()
       
    def showDocumentBar(self):
        """
        Show document bar
        """
        self.dockToolbar.show()

    def hideExecuteBar(self):
        """
        Hide execute bar
        """
        self.dockToolbar2.hide()
       
    def showExecuteBar(self):
        """
        Show execute bar
        """
        self.dockToolbar2.show()

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-----|------|||------|-------|||------|------|||---------|-----------|||-----||
        || New | Open ||| Save | SaveA ||| Undo | Redo ||| Comment | Uncomment ||| Run ||
        ||-----|------|||------|-------|||------|------|||---------|-----------|||-----||
        """
        self.dockToolbar.setObjectName("File toolbar")
        self.dockToolbar.addAction(self.newTestAbstractAction)
        self.dockToolbar.addAction(self.newTestUnitAction)
        self.dockToolbar.addAction(self.newTestSuiteAction)
        self.dockToolbar.addAction(self.newTestPlanAction)
        self.dockToolbar.addAction(self.newTestGlobalAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.newTestConfigAction)
        self.dockToolbar.addAction(self.newTestDataAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.newAdapterAction)
        self.dockToolbar.addAction(self.newLibraryAction)
        self.dockToolbar.addAction(self.newTxtAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.openAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.saveAction)
        self.dockToolbar.addAction(self.saveAllAction)
        self.dockToolbar.addAction(self.printAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.findAction)
        self.dockToolbar.setIconSize(QSize(16, 16))
        
        self.dockToolbar2.setObjectName("Run")
        self.dockToolbar2.addAction(self.runAction)
        self.dockToolbar2.addAction(self.runSchedAction)
        self.dockToolbar2.addAction(self.runSeveralAction)
        self.dockToolbar2.addSeparator()
        self.dockToolbar2.addAction(self.runStepByStepAction)
        self.dockToolbar2.addAction(self.runBreakpointAction)
        self.dockToolbar2.addSeparator()
        self.dockToolbar2.addAction(self.checkSyntaxAction)
        self.dockToolbar2.addAction(self.checkDesignAction)
        self.dockToolbar2.addAction(self.updateTestAction)
        self.dockToolbar2.addSeparator()
        self.dockToolbar2.setIconSize(QSize(16, 16))

    def decodeData(self, b64data):
        """
        Decode data
        """
        data_json = ''
        try:
            data_decoded = base64.b64decode(b64data)
        except Exception as e:
            self.error( 'unable to decode from base64 structure: %s' % str(e) )
        else:
            try:
                data_uncompressed = zlib.decompress(data_decoded)
            except Exception as e:
                self.error( 'unable to decompress: %s' % str(e) )
            else:
                try:
                    if sys.version_info > (3,): # python3 support
                        data_json = json.loads( data_uncompressed.decode('utf-8') )
                    else:
                        data_json = json.loads( data_uncompressed )
                except Exception as e:
                    self.error( 'unable to decode from json structure: %s' % str(e) )
        return data_json

    def runSeveralTests(self):
        """
        Run several tests
        """
        self.runsDialog.initProjects( projects= Settings.instance().serverContext['projects'],
                                      defaultProject=Settings.instance().serverContext['default-project'] )
        if self.runsDialog.exec_() == QDialog.Accepted:
            tests, runLater, runAt, runSimultaneous = self.runsDialog.getTests()

            # rest call
            RCI.instance().scheduleTests(tests=tests,
                                         postponeMode=runLater,
                                         postponeAt=runAt,
                                         parallelMode=runSimultaneous)
                                         
    def onProjectChangedInRuns(self, projectName):
        """
        On project changed for several runs
        """
        projectId = self.iRepo.remote().getProjectId(project=projectName)

        # rest call
        RCI.instance().listingTests(projectId=projectId, forSaveAs=False, forRuns=True)
        
    def onRefreshRepositoryRuns(self, data, projectid):
        """
        On refresh repository runs
        """
        self.runsDialog.initializeTests(listing=data )

    def printDoc(self):
        """
        Print document
        """
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False

        currentDocument = self.tab.widget(tabId)

        if currentDocument.extension == TestUnit.TYPE or currentDocument.extension == TestTxt.TYPE or  \
            currentDocument.extension == TestData.TYPE or currentDocument.extension == TestAdapter.TYPE or \
            currentDocument.extension == TestLibrary.TYPE:
            doc = QTextDocument()
            doc.setPlainText( currentDocument.srcEditor.text() )
        elif currentDocument.extension == TestSuite.TYPE:
            doc = QTextDocument()
            doc.setPlainText( "%s\n\n%s" % (currentDocument.srcEditor.text(), currentDocument.execEditor.text()) )
        elif currentDocument.extension == TestPlan.TYPE or currentDocument.extension == TestPlan.TYPE_GLOBAL:
            # prepare a new view of the testplan/testglobal and load the model on it
            doc = TestPlan.PrintTreeView()
            doc.setModel(currentDocument.tp.model())
        elif currentDocument.extension == TestAbstract.TYPE:
            doc = currentDocument
        else:
            pass

            
        printer = QPrinter(QPrinter.ScreenResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setDocName(currentDocument.getShortName(withAsterisk = False, withExtension = True) )

        dialog = QPrintPreviewDialog(printer, self)
        dialog.setWindowState(Qt.WindowMaximized)
        dialog.paintRequested.connect(doc.print_)
        dialog.exec_()

    def initFindReplaceBarDisplay(self):
        """
        Init find/replace bar displya
        """
        if ( Settings.instance().readValue( key = 'View/findreplace-bar' ) == 'True' ):
            self.findWidget.show()
            self.hideFindReplaceAction.setChecked(True)
        else:
            self.hideFindReplaceAction.setChecked(False)
            self.findWidget.hide()

    def hideFindReplaceWidget(self):
        """
        Hide find/Replace widget
        """
        self.findWidget.hide()
        
    def hideFindReplace(self):
        """
        Hide find/replace
        """
        tabId = self.tab.currentIndex()
        if tabId == -1: return False
        currentDoc = self.tab.widget(tabId)
        
        if not self.hideFindReplaceAction.isChecked():
            Settings.instance().setValue( key = 'View/findreplace-bar', value = 'False' )
            self.findWidget.hide()
        else:
            Settings.instance().setValue( key = 'View/findreplace-bar', value = 'True' )
            
            if isinstance(currentDoc, WelcomePage):
                return
                
            if currentDoc.extension in [ TestUnit.TYPE, TestSuite.TYPE, TestAdapter.TYPE,
                                          TestData.TYPE, TestLibrary.TYPE, TestTxt.TYPE  ]:
                self.findWidget.show()
    
    def searchText(self):
        """
        Search text in find/replace widget
        """
        tabId = self.tab.currentIndex()
        if tabId == -1: return False
        currentDoc = self.tab.widget(tabId)
        
        if isinstance(currentDoc, WelcomePage):
            return
            
        if currentDoc.extension in [ TestUnit.TYPE, TestSuite.TYPE, TestAdapter.TYPE,
                                      TestData.TYPE,  TestLibrary.TYPE, TestTxt.TYPE  ]:
            selectedText = ''
            if currentDoc.editor().hasSelectedText():
                selectedText = currentDoc.editor().selectedText()
            self.hideFindReplaceAction.setChecked(True)
            self.findWidget.showEnhanced(textSelected=selectedText)
        
    def addActionToolbar(self, action):
        """
        Add action to toolbar
        """
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(action)

    def toggleLineNumbering(self, checked):
        """
        Toggles code folding on all opened documents

        @param checked: 
        @type checked: boolean
        """
        self.lineNumbering = checked
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            if doc.extension != TestPlan.TYPE and doc.extension != TestPlan.TYPE_GLOBAL and doc.extension != TestConfig.TYPE:
                doc.setLinesNumbering(checked)
                
    def toggleCodeWrapping(self, checked):
        """
        Toggles code wrapping on all opened documents

        @param checked: 
        @type checked: boolean
        """
        self.codeWrapping = checked
        try:
            if checked:
                self.codeWrappingAction.setEnabled(True)
            else:
                self.codeWrappingAction.setEnabled(False)
        except Exception as e:
            self.error( ' toggle code wrapping: %s' % str(e) )

        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            if doc.extension != TestPlan.TYPE_GLOBAL and doc.extension != TestPlan.TYPE and \
                    doc.extension != TestPng.TYPE and doc.extension != TestConfig.TYPE and \
                        doc.extension != TestAbstract.TYPE:
                doc.setWrappingMode(checked)
                
    def toggleCodeFolding(self, checked):
        """
        Toggles code folding on all opened documents

        @param checked: 
        @type checked: boolean
        """
        self.codeFolding = checked
        try:
            if checked:
                self.foldAllAction.setEnabled(True)
            else:
                self.foldAllAction.setEnabled(False)
        except Exception as e:
            self.error( ' toggle code folding: %s' % str(e) )

        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            if doc.extension != TestPlan.TYPE and doc.extension != TestTxt.TYPE and doc.extension != TestConfig.TYPE:
                doc.setFolding(checked)

    def toggleIndentGuidesVisibility(self, checked):
        """
        Toggles indentation guides on all opened documents

        @param checked: 
        @type checked: boolean
        """
        self.indentationGuidesVisible = checked
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            if doc.extension != TestPlan.TYPE and doc.extension != TestConfig.TYPE:
                doc.setIndentationGuidesVisible(checked)

    def toggleWhitespaceVisibility(self, checked):
        """
        Toggles whitespace visibility on all opened documents

        @param checked: 
        @type checked: boolean
        """
        self.whitespaceVisible = checked
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            if doc.extension != TestPlan.TYPE and doc.extension != TestPlan.TYPE_GLOBAL and doc.extension != TestConfig.TYPE:
                doc.setWhitespaceVisible(checked)

    def openDoc (self):
        """
        Opens file
        Get the filename 
        Call the function newTab()
        """
        fileName = QFileDialog.getOpenFileName(self,
              self.tr("Open File"), "", "All documents (*.%s;*.%s;*.%s;*.%s;*.%s;*.%s;*.%s);;Tests abstract (*.%s);;Tests unit (*.%s);;Tests suite (*.%s);;Tests plan (*.%s);;Tests global (*.%s);;Tests config (*.%s);;Tests data (*.%s)" %
                    ( TestAbstract.TYPE, TestUnit.TYPE, TestSuite.TYPE, TestPlan.TYPE, TestPlan.TYPE_GLOBAL, TestConfig.TYPE, TestData.TYPE, 
                      TestAbstract.TYPE, TestUnit.TYPE, TestSuite.TYPE, TestPlan.TYPE, TestPlan.TYPE_GLOBAL, TestConfig.TYPE, TestData.TYPE) )
                
        # new in v17.1
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if not len(_fileName):
            return
        
        extension = str(_fileName).rsplit(".", 1)[1]
        if not ( extension.lower() in [ TestSuite.TYPE, TestPlan.TYPE, TestPlan.TYPE_GLOBAL, TestConfig.TYPE,
                                        TestData.TYPE, TestUnit.TYPE, TestAbstract.TYPE  ] ):
            QMessageBox.critical(self, self.tr("Open Failed") , self.tr("File not supported") )
            return
        
        tmp = str(_fileName).rsplit("/", 1)
        path = tmp[0]
        if len(tmp) > 1:
            _filename = tmp[1].rsplit(".", 1)[0]
        else:
            _filename = tmp[0].rsplit(".", 1)[0]
        self.newTab( path = path, filename = _filename, 
                     extension = extension, repoDest=UCI.REPO_UNDEFINED)

    def openRemoteTestFile(self, filePath, fileName, fileExtension, fileContent, 
                           projectId, isLocked, lockedBy, subtest_id):
        """
        """
        content = base64.b64decode(fileContent)
        
        newTab = False
        isReadOnly = False
        if not isLocked:
            newTab = True
        else:
            messageBox = QMessageBox(self)

            lockedByDecoded = base64.b64decode(lockedBy)
            if sys.version_info > (3,): # python3 support
                lockedByDecoded = lockedByDecoded.decode("utf8")

            msg = "User (%s) is editing this file. Edit the file anyway?\n\n" % lockedByDecoded
            msg += "Yes = Edit the file\n"
            msg += "No = Open as read only\n"
            msg += "Cancel = Do nothing.\n" 
            
            reply = messageBox.warning(self, self.tr("File locked"), msg, 
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
                        
            # force to open the file
            if reply == QMessageBox.Yes:
                RCI.instance().openFileTests(projectId=int(projectId), 
                                             filePath="%s/%s.%s" % (filePath, fileName, fileExtension), 
                                             ignoreLock=True, 
                                             readOnly=False)
            # force as read only
            if reply == QMessageBox.No: 
                RCI.instance().openFileTests(projectId=int(projectId), 
                                             filePath="%s/%s.%s" % (filePath, fileName, fileExtension), 
                                             ignoreLock=True, 
                                             readOnly=True)
            # cancel the opening
            else:
                newTab = False
        
        if newTab:
            self.newTab( path = filePath, filename = fileName, extension = fileExtension, 
                        remoteFile=True, contentFile=content,  repoDest=UCI.REPO_TESTS, newAdp=False, 
                        newLib=False, project=projectId, isReadOnly=isReadOnly, isLocked=isLocked,
                        subtest_id=subtest_id)
                        
    def openRemoteAdapterFile(self, filePath, fileName, fileExtension, fileContent, isLocked, lockedBy):
        """
        """
        content = base64.b64decode(fileContent)
        
        newTab = False
        isReadOnly = False
        if not isLocked:
            newTab = True
        else:
            messageBox = QMessageBox(self)

            lockedByDecoded = base64.b64decode(lockedBy)
            if sys.version_info > (3,): # python3 support
                lockedByDecoded = lockedByDecoded.decode("utf8")

            msg = "User (%s) is editing this file. Edit the file anyway?\n\n" % lockedByDecoded
            msg += "Yes = Edit the file\n"
            msg += "No = Open as read only\n"
            msg += "Cancel = Do nothing.\n" 
            
            reply = messageBox.warning(self, self.tr("File locked"), msg, 
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
                        
            # force to open the file
            if reply == QMessageBox.Yes: 
                RCI.instance().openFileAdapters(projectId=0, 
                                                 filePath="%s/%s.%s" % (path_file, name_file, ext_file), 
                                                 ignoreLock=True, 
                                                 readOnly=False)
            # force as read only
            if reply == QMessageBox.No:
                RCI.instance().openFileAdapters(projectId=0, 
                                                 filePath="%s/%s.%s" % (path_file, name_file, ext_file), 
                                                 ignoreLock=True, 
                                                 readOnly=True)
            # cancel the opening
            else:
                newTab = False
        
        if newTab:
            self.newTab( path = filePath, filename = fileName, extension = fileExtension, 
                        remoteFile=True, contentFile=content,  repoDest=UCI.REPO_ADAPTERS, newAdp=True, 
                        newLib=False, project=0, isReadOnly=isReadOnly, isLocked=isLocked)
                        
    def openRemoteLibraryFile(self, filePath, fileName, fileExtension, fileContent, isLocked, lockedBy):
        """
        """
        content = base64.b64decode(fileContent)
        
        newTab = False
        isReadOnly = False
        if not isLocked:
            newTab = True
        else:
            messageBox = QMessageBox(self)
            
            lockedByDecoded = base64.b64decode(lockedBy)
            if sys.version_info > (3,): # python3 support
                lockedByDecoded = lockedByDecoded.decode("utf8")

            msg = "User (%s) is editing this file. Edit the file anyway?\n\n" % lockedByDecoded
            msg += "Yes = Edit the file\n"
            msg += "No = Open as read only\n"
            msg += "Cancel = Do nothing.\n" 

            reply = messageBox.warning(self, self.tr("File locked"), msg, 
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
                        
            # force to open the file
            if reply == QMessageBox.Yes: 
                RCI.instance().openFileLibraries(projectId=0, 
                                                 filePath="%s/%s.%s" % (path_file, name_file, ext_file), 
                                                 ignoreLock=True, 
                                                 readOnly=False)
            # force as read only
            if reply == QMessageBox.No: 
                RCI.instance().openFileLibraries(projectId=int(projectId), 
                                                 filePath="%s/%s.%s" % (path_file, name_file, ext_file), 
                                                 ignoreLock=True, 
                                                 readOnly=True)
            # cancel the opening
            else:
                newTab = False
        
        if newTab:
            self.newTab( path = filePath, filename = fileName, extension = fileExtension, 
                        remoteFile=True, contentFile=content,  repoDest=UCI.REPO_LIBRARIES, newAdp=False, 
                        newLib=True, project=0, isReadOnly=isReadOnly, isLocked=isLocked)
 
    def onRemoteTestFileSaved(self, filePath, fileName, fileExtension,
                                projectId, overwriteFile, closeAfter):
        """
        Called when a remote file is saved
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % ( fileName, fileExtension)
        
        tabId = None

        if overwriteFile:
            tabId = self.checkAlreadyOpened(path = complete_path, 
                                            remoteFile=True, 
                                            repoType=UCI.REPO_TESTS, 
                                            project=projectId)
        else:
            for tid in xrange( self.tab.count() ):
                doc = self.tab.widget(tid)
                
                # bypass the welcome page
                if isinstance(doc, WelcomePage): continue

                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.project == projectId and doc.repoDest==UCI.REPO_TESTS:
                    tabId = tid
                    break
                
                # first remote save
                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.repoDest==UCI.REPO_UNDEFINED:
                    tabId = tid
                    break

        if tabId is not None:
            doc = self.tab.widget(tabId)
            doc.setUnmodify(repoType=UCI.REPO_TESTS)
            # close the tab ?
            if closeAfter:
                self.closeTab( tabId = tabId )
                        
    def onRemoteAdapterFileSaved(self, filePath, fileName, fileExtension,
                                    overwriteFile, closeAfter):
        """
        Called when a remote file is saved

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % ( fileName, fileExtension)
        
        tabId = None

        if overwriteFile:
            tabId = self.checkAlreadyOpened(path = complete_path, 
                                            remoteFile=True, 
                                            repoType=UCI.REPO_ADAPTERS, 
                                            project=0)
        else:
            for tid in xrange( self.tab.count() ):
                doc = self.tab.widget(tid)
                
                # bypass the welcome page
                if isinstance(doc, WelcomePage): continue

                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.project == 0 and doc.repoDest==UCI.REPO_ADAPTERS:
                    tabId = tid
                    break
                
                # first remote save
                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.repoDest==UCI.REPO_UNDEFINED:
                    tabId = tid
                    break

        if tabId is not None:
            doc = self.tab.widget(tabId)
            doc.setUnmodify(repoType=UCI.REPO_ADAPTERS)
            # close the tab ?
            if closeAfter:
                self.closeTab( tabId = tabId )
                        
    def onRemoteLibraryFileSaved(self, filePath, fileName, fileExtension,
                                    overwriteFile, closeAfter):
        """
        Called when a remote file is saved

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % ( fileName, fileExtension)
        
        tabId = None

        if overwriteFile:
            tabId = self.checkAlreadyOpened(path = complete_path, 
                                            remoteFile=True, 
                                            repoType=UCI.REPO_LIBRARIES, 
                                            project=0)
        else:
            for tid in xrange( self.tab.count() ):
                doc = self.tab.widget(tid)
                
                # bypass the welcome page
                if isinstance(doc, WelcomePage): continue

                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.project == 0 and doc.repoDest==UCI.REPO_LIBRARIES:
                    tabId = tid
                    break
                
                # first remote save
                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.repoDest==UCI.REPO_UNDEFINED:
                    tabId = tid
                    break

        if tabId is not None:
            doc = self.tab.widget(tabId)
            doc.setUnmodify(repoType=UCI.REPO_LIBRARIES)
            # close the tab ?
            if closeAfter:
                self.closeTab( tabId = tabId )
  
    def remoteTestsFileRenamed(self, projectId, filePath, fileName, fileExtension, newName):
        """
        Called when a remote file is renamed

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % ( fileName, fileExtension)
        tabId = self.checkAlreadyOpened(path = complete_path, 
                                        remoteFile=True, 
                                        repoType=UCI.REPO_TESTS, 
                                        project=projectId)
        if tabId is not None:
            doc = self.tab.widget(tabId)
            self.tab.setCurrentIndex(tabId)
            buttons = QMessageBox.Yes | QMessageBox.No 
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("This file has been renamed.\nDo you want to update the name ?") , buttons)
            if answer == QMessageBox.Yes:
                doc.updateFilename( filename=newName )
                doc.setUnmodify()
            elif answer == QMessageBox.No:
                doc.unSaved()
                doc.setModify()
                
    def remoteAdaptersFileRenamed(self, filePath, fileName, fileExtension, newName):
        """
        Called when a remote file is renamed

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % ( fileName, fileExtension)
        tabId = self.checkAlreadyOpened(path = complete_path, 
                                        remoteFile=True, 
                                        repoType=UCI.REPO_ADAPTERS, 
                                        project=0)
        if tabId is not None:
            doc = self.tab.widget(tabId)
            self.tab.setCurrentIndex(tabId)
            buttons = QMessageBox.Yes | QMessageBox.No 
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("This file has been renamed.\nDo you want to update the name ?") , buttons)
            if answer == QMessageBox.Yes:
                doc.updateFilename( filename=newName )
                doc.setUnmodify()
            elif answer == QMessageBox.No:
                doc.unSaved()
                doc.setModify()
                
    def remoteLibrariesFileRenamed(self, filePath, fileName, fileExtension, newName):
        """
        Called when a remote file is renamed

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % ( fileName, fileExtension)
        tabId = self.checkAlreadyOpened(path = complete_path, 
                                        remoteFile=True, 
                                        repoType=UCI.REPO_LIBRARIES, 
                                        project=0)
        if tabId is not None:
            doc = self.tab.widget(tabId)
            self.tab.setCurrentIndex(tabId)
            buttons = QMessageBox.Yes | QMessageBox.No 
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("This file has been renamed.\nDo you want to update the name ?") , buttons)
            if answer == QMessageBox.Yes:
                doc.updateFilename( filename=newName )
                doc.setUnmodify()
            elif answer == QMessageBox.No:
                doc.unSaved()
                doc.setModify()

    def remoteTestsDirRenamed(self, projectId, directoryPath, directoryName, newName):
        """
        Called when a remote directory is renamed
        """
        if len(directoryPath) > 0:
            complete_old = "%s/%s" % (directoryPath, directoryName)
            complete_new = "%s/%s" % (directoryPath, newName)
        else:
            complete_old = directoryName
            complete_new = newName

        for tabId in xrange( self.tab.count() ):    
            doc = self.tab.widget(tabId)
            
            # bypass the welcome page
            if isinstance(doc, WelcomePage): 
                continue
            # end of bypass
            
            
            if doc.isRemote == True and doc.getPathOnly().startswith(complete_old) and \
                    doc.project == int(projectId) and doc.repoDest==UCI.REPO_TESTS:  
                to_keep = doc.getPathOnly().split(complete_old)
                if len(to_keep) > 1: to_keep = to_keep[1]
                else: to_keep = to_keep[0]

                full_new_path = "%s%s" % (complete_new, to_keep)

                self.tab.setCurrentIndex(tabId)
                
                msg = self.tr("The path of this file has been renamed.\nDo you want to update the path ?")
                buttons = QMessageBox.Yes | QMessageBox.No 
                answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                                              msg, buttons)
                if answer == QMessageBox.Yes:
                    doc.updatePath( pathFilename=full_new_path )
                    doc.setUnmodify()
                elif answer == QMessageBox.No:
                    doc.unSaved()
                    doc.setModify()
                    
    def remoteAdaptersDirRenamed(self, directoryPath, directoryName, newName):
        """
        Called when a remote directory is renamed
        """
        if len(directoryPath) > 0:
            complete_old = "%s/%s" % (directoryPath, directoryName)
            complete_new = "%s/%s" % (directoryPath, newName)
        else:
            complete_old = directoryName
            complete_new = newName
        
        for tabId in xrange( self.tab.count() ):    
            doc = self.tab.widget(tabId)
            
            # bypass the welcome page
            if isinstance(doc, WelcomePage): 
                continue
            # end of bypass
            
            if doc.isRemote == True and doc.getPathOnly().startswith(complete_old) and \
                    doc.project == 0 and doc.repoDest==UCI.REPO_ADAPTERS:  
                to_keep = doc.getPathOnly().split(complete_old)
                if len(to_keep) > 1: to_keep = to_keep[1]
                else: to_keep = to_keep[0]

                full_new_path = "%s%s" % (complete_new, to_keep)

                self.tab.setCurrentIndex(tabId)
                
                msg = self.tr("The path of this file has been renamed.\nDo you want to update the path ?")
                buttons = QMessageBox.Yes | QMessageBox.No 
                answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                                              msg, buttons)
                if answer == QMessageBox.Yes:
                    doc.updatePath( pathFilename=full_new_path )
                    doc.setUnmodify()
                elif answer == QMessageBox.No:
                    doc.unSaved()
                    doc.setModify()
                    
    def remoteLibrariesDirRenamed(self, directoryPath, directoryName, newName):
        """
        Called when a remote directory is renamed
        """
        if len(directoryPath) > 0:
            complete_old = "%s/%s" % (directoryPath, directoryName)
            complete_new = "%s/%s" % (directoryPath, newName)
        else:
            complete_old = directoryName
            complete_new = newName
        
        for tabId in xrange( self.tab.count() ):    
            doc = self.tab.widget(tabId)
            
            # bypass the welcome page
            if isinstance(doc, WelcomePage): 
                continue
            # end of bypass
            
            if doc.isRemote == True and doc.getPathOnly().startswith(complete_old) and \
                    doc.project == 0 and doc.repoDest==UCI.REPO_LIBRARIES:  
                to_keep = doc.getPathOnly().split(complete_old)
                if len(to_keep) > 1: to_keep = to_keep[1]
                else: to_keep = to_keep[0]

                full_new_path = "%s%s" % (complete_new, to_keep)

                self.tab.setCurrentIndex(tabId)
                
                msg = self.tr("The path of this file has been renamed.\nDo you want to update the path ?")
                buttons = QMessageBox.Yes | QMessageBox.No 
                answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                                              msg, buttons)
                if answer == QMessageBox.Yes:
                    doc.updatePath( pathFilename=full_new_path )
                    doc.setUnmodify()
                elif answer == QMessageBox.No:
                    doc.unSaved()
                    doc.setModify()
                    
    def onRemoteTestFileSavedError(self, filePath, fileName, fileExtension,
                                    projectId, overwriteFile, closeAfter):
        """
        Called when the save of a remote file failed

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % (fileName, fileExtension)

        tabId = None # issue Issue 224
        if overwriteFile:
            tabId = self.checkAlreadyOpened(path = complete_path, remoteFile=True, 
                                            repoType=UCI.REPO_TESTS, project=projectId)
        else:
            for tid in xrange( self.tab.count() ):
                doc = self.tab.widget(tid)
                
                # bypass the welcome page
                if isinstance(doc, WelcomePage): 
                    continue
                # end of bypass
                
                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.project == projectId  and doc.repoDest==UCI.REPO_UNDEFINED:
                    tabId = tid
                    break

        if tabId is not None:
            doc = self.tab.widget(tabId)
            doc.unSaved()
                    
    def onRemoteAdapterFileSavedError(self, filePath, fileName, fileExtension,
                                        overwriteFile, closeAfter):
        """
        Called when the save of a remote file failed

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % (fileName, fileExtension)

        tabId = None # issue Issue 224
        if overwriteFile:
            tabId = self.checkAlreadyOpened(path = complete_path, remoteFile=True, 
                                            repoType=UCI.REPO_ADAPTERS, project=0)
        else:
            for tid in xrange( self.tab.count() ):
                doc = self.tab.widget(tid)
                
                # bypass the welcome page
                if isinstance(doc, WelcomePage): 
                    continue
                # end of bypass
                
                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.project == projectId  and doc.repoDest==UCI.REPO_UNDEFINED:
                    tabId = tid
                    break

        if tabId is not None:
            doc = self.tab.widget(tabId)
            doc.unSaved()
                    
    def onRemoteLibraryFileSavedError(self, filePath, fileName, fileExtension,
                                        overwriteFile, closeAfter):
        """
        Called when the save of a remote file failed

        @param data: 
        @type data: 
        """
        if len(filePath) > 0:
            complete_path = "%s/%s.%s" % (filePath, fileName, fileExtension)
        else:
            complete_path = "%s.%s" % (fileName, fileExtension)

        tabId = None # issue Issue 224
        if overwriteFile:
            tabId = self.checkAlreadyOpened(path = complete_path, remoteFile=True, 
                                            repoType=UCI.REPO_LIBRARIES, project=0)
        else:
            for tid in xrange( self.tab.count() ):
                doc = self.tab.widget(tid)
                
                # bypass the welcome page
                if isinstance(doc, WelcomePage): 
                    continue
                # end of bypass
                
                if doc.isRemote == True and doc.getPath() == complete_path and \
                        doc.project == projectId  and doc.repoDest==UCI.REPO_UNDEFINED:
                    tabId = tid
                    break

        if tabId is not None:
            doc = self.tab.widget(tabId)
            doc.unSaved()

    def updateRemoteTestOnTestglobal(self, data, parametersOnly=True, 
                                     mergeParameters=False, refreshOtherItems=False):
        """
        Update remote testsuite on testplan

        @param data: 
        @type data: 
        
        @param parametersOnly: 
        @type parametersOnly: 
        """
        path_file, name_file, ext_file, encoded_data, testId, project  = data
        tabId = self.tab.currentIndex()
        if tabId == -1: return False
        currentDoc = self.tab.widget(tabId)

        if currentDoc.extension == TestPlan.TYPE_GLOBAL :
            content = base64.b64decode(encoded_data)
            if parametersOnly:
                currentDoc.onUpdateRemotePropertiesSubItem(path_file, 
                                                           name_file, 
                                                           ext_file, 
                                                           content, 
                                                           testId, 
                                                           project, 
                                                           mergeParameters=mergeParameters)
            else:
                currentDoc.onUpdateRemoteTestSubItem(path_file, 
                                                     name_file, 
                                                     ext_file, 
                                                     content, 
                                                     testId, 
                                                     project, 
                                                     refreshOtherItems=refreshOtherItems)

    def addRemoteTestToTestglobal(self, data, testParentId=0):
        """
        Add remote testsuite to testplan

        @param data: 
        @type data: 
        """
        path_file, name_file, ext_file, encoded_data, project = data
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDoc = self.tab.widget(tabId)

        if currentDoc.extension == TestPlan.TYPE_GLOBAL :
            content = base64.b64decode(encoded_data)
            currentDoc.addRemoteSubItem(path_file, 
                                        name_file, 
                                        ext_file, 
                                        content, 
                                        project, 
                                        testParentId=testParentId)

    def insertRemoteTestToTestglobal(self, data, below=False, testParentId=0):
        """
        Add remote testsuite to testplan

        @param data: 
        @type data: 
        
        @param below: 
        @type below: 
        """
        path_file, name_file, ext_file, encoded_data, project = data
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDoc = self.tab.widget(tabId)
 
        if currentDoc.extension == TestPlan.TYPE_GLOBAL :
            content = base64.b64decode(encoded_data)
            currentDoc.insertRemoteSubItem(path_file, 
                                           name_file, 
                                           ext_file, 
                                           content, 
                                           project, 
                                           below, 
                                           testParentId=testParentId)

    def updateRemoteTestOnTestplan(self, data, parametersOnly=True, 
                                   mergeParameters=False, refreshOtherItems=False):
        """
        Update remote testsuite on testplan

        @param data: 
        @type data: 

        @param parametersOnly: 
        @type parametersOnly: 
        """
        path_file, name_file, ext_file, encoded_data, testId, project  = data
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDoc = self.tab.widget(tabId)

        if currentDoc.extension == TestPlan.TYPE :
            content = base64.b64decode(encoded_data)
            if parametersOnly:
                currentDoc.onUpdateRemotePropertiesSubItem(path_file, 
                                                           name_file, 
                                                           ext_file, 
                                                           content, 
                                                           testId, 
                                                           project, 
                                                           mergeParameters=mergeParameters)
            else:
                currentDoc.onUpdateRemoteTestSubItem(path_file, 
                                                     name_file, 
                                                     ext_file, 
                                                     content, 
                                                     testId, 
                                                     project,
                                                     refreshOtherItems=refreshOtherItems)

    def addRemoteTestToTestplan(self, data, testParentId=0):
        """
        Add remote testsuite to testplan

        @param data: 
        @type data: 
        """
        path_file, name_file, ext_file, encoded_data, project = data
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDoc = self.tab.widget(tabId)
        # 
        if currentDoc.extension == TestPlan.TYPE :
            content = base64.b64decode(encoded_data)
            currentDoc.addRemoteSubItem(path_file, 
                                        name_file, 
                                        ext_file, 
                                        content, 
                                        project, 
                                        testParentId=testParentId)

    def insertRemoteTestToTestplan(self, data, below=False, testParentId=0):
        """
        Add remote testsuite to testplan

        @param data: 
        @type data: 
        """
        path_file, name_file, ext_file, encoded_data, project = data
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDoc = self.tab.widget(tabId)

        if currentDoc.extension == TestPlan.TYPE :
            content = base64.b64decode(encoded_data)
            currentDoc.insertRemoteSubItem(path_file, 
                                           name_file, 
                                           ext_file, 
                                           content, 
                                           project, 
                                           below, 
                                           testParentId=testParentId)

    def setDefaultActionsValues (self):
        """
        Set default values of each actions
        Disabled actions:
         * save
         * undo
         * redo
         * comment
         * uncomment
         * run
        """
        self.closeAllTabAction.setEnabled(False)
        self.closeTabAction.setEnabled(False)
        self.saveAction.setEnabled(False)
        self.saveAsAction.setEnabled(False)
        self.exportAsAction.setEnabled(False)
        self.saveAllAction.setEnabled(False)
        self.printAction.setEnabled(False)
        self.cutAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.pasteAction.setEnabled(False)
        self.selectAllAction.setEnabled(False)
        self.deleteAction.setEnabled(False)
        self.undoAction.setEnabled(False)
        self.redoAction.setEnabled(False)
        self.commentAction.setEnabled(False)
        self.uncommentAction.setEnabled(False)
        self.indentAction.setEnabled(False)
        self.unindentAction.setEnabled(False)
        self.findAction.setEnabled(False)
        
        self.checkSyntaxAction.setEnabled(False)
        self.checkDesignAction.setEnabled(False)
        self.updateTestAction.setEnabled(False)
        self.checkAction.setEnabled(False)
        self.runSchedAction.setEnabled(False)
        self.runAction.setEnabled(False)
        self.runStepByStepAction.setEnabled(False)
        self.runBreakpointAction.setEnabled(False)
        self.runDebugAction.setEnabled(False)
        self.runNowAction.setEnabled(False)
        self.runBackgroundAction.setEnabled(False)
        self.runWithoutProbesAction.setEnabled(False)
        self.runWithoutNotifAction.setEnabled(False)
        
        self.codeWrappingAction.setEnabled(False)
        self.codefoldingAction.setEnabled(False)
        self.foldAllAction.setEnabled(False)
        self.whitespaceVisibilityAction.setEnabled(False)
        self.indentGuidesVisibilityAction.setEnabled(False)
        self.linesNumberingAction.setEnabled(False)

    def updateActions(self, wdocument = None):
        """
        Updates QActions

        @param wdocument: 
        @type wdocument: 
        """
        if RCI.instance() is None:
            return
            
        if wdocument is None:
            return

        # begin fix for the issue 506
        docsModified = False
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            
            # bypass the welcome page
            if isinstance(doc, WelcomePage): 
                continue
            # end of bypass
            
            # check is modified ?
            if doc is not None:
                if doc.isModified():
                    docsModified = True
        
        if docsModified:
            self.saveAllAction.setEnabled(True)
        else:
            self.saveAllAction.setEnabled(False)
        # end of the fix for the issue 506

        if isinstance(wdocument, WelcomePage):
            self.saveAction.setEnabled(False)
            
            self.findAction.setEnabled(False)
            self.printAction.setEnabled(False)
            self.commentAction.setEnabled(False)
            self.uncommentAction.setEnabled(False)
            self.indentAction.setEnabled(False)
            self.unindentAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            
            self.checkSyntaxAction.setEnabled(False)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(False)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)
            
        elif isinstance(wdocument, TestUnit.WTestUnit):
            curEditor = wdocument.currentEditor()
            if curEditor is None:
                return
            self.exportAsAction.setEnabled(True)
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(True)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(True)
            self.uncommentAction.setEnabled(True)
            self.indentAction.setEnabled(True)
            self.unindentAction.setEnabled(True)

            state = curEditor.hasSelectedText()
            self.copyAction.setEnabled(state)
            self.cutAction.setEnabled(state)
            self.deleteAction.setEnabled(state)
            self.pasteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)

            self.undoAction.setEnabled( curEditor.isUndoAvailable() )
            self.redoAction.setEnabled( curEditor.isRedoAvailable() )

            if RCI.instance().isAuthenticated():
                self.checkSyntaxAction.setEnabled(True)
                self.checkDesignAction.setEnabled(True)
                self.updateTestAction.setEnabled(True)
                self.checkAction.setEnabled(True)
                self.runAction.setEnabled(True)
                self.runStepByStepAction.setEnabled(True)
                self.runBreakpointAction.setEnabled(True)
                self.runNowAction.setEnabled(True)
                self.runDebugAction.setEnabled(True)
                self.runSchedAction.setEnabled(True)
                self.runBackgroundAction.setEnabled(True)
                self.runWithoutProbesAction.setEnabled(True)
                self.runWithoutNotifAction.setEnabled(True)
            else:
                self.checkSyntaxAction.setEnabled(False)
                self.checkDesignAction.setEnabled(False)
                self.updateTestAction.setEnabled(False)
                self.checkAction.setEnabled(False)
                self.runAction.setEnabled(False)
                self.runStepByStepAction.setEnabled(False)
                self.runBreakpointAction.setEnabled(False)
                self.runNowAction.setEnabled(False)
                self.runDebugAction.setEnabled(False)
                self.runSchedAction.setEnabled(False)
                self.runBackgroundAction.setEnabled(False)
                self.runWithoutProbesAction.setEnabled(False)
                self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(True)
            self.codefoldingAction.setEnabled(True)
            if self.codeFolding:
                self.foldAllAction.setEnabled(True)
            else:
                self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(True)
            self.indentGuidesVisibilityAction.setEnabled(True)
            self.linesNumberingAction.setEnabled(True)

        elif isinstance(wdocument, TestSuite.WTestSuite):
            curEditor = wdocument.currentEditor()
            if curEditor is None:
                return
            self.exportAsAction.setEnabled(True)
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(True)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(True)
            self.uncommentAction.setEnabled(True)
            self.indentAction.setEnabled(True)
            self.unindentAction.setEnabled(True)

            state = curEditor.hasSelectedText()
            self.copyAction.setEnabled(state)
            self.cutAction.setEnabled(state)
            self.deleteAction.setEnabled(state)
            self.pasteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)

            self.undoAction.setEnabled( curEditor.isUndoAvailable() )
            self.redoAction.setEnabled( curEditor.isRedoAvailable() )

            if RCI.instance().isAuthenticated():
                self.checkSyntaxAction.setEnabled(True)
                self.checkDesignAction.setEnabled(True)
                self.updateTestAction.setEnabled(True)
                self.checkAction.setEnabled(True)
                self.runAction.setEnabled(True)
                self.runStepByStepAction.setEnabled(True)
                self.runBreakpointAction.setEnabled(True)
                self.runNowAction.setEnabled(True)
                self.runDebugAction.setEnabled(True)
                self.runSchedAction.setEnabled(True)
                self.runBackgroundAction.setEnabled(True)
                self.runWithoutProbesAction.setEnabled(True)
                self.runWithoutNotifAction.setEnabled(True)
            else:
                self.checkSyntaxAction.setEnabled(False)
                self.checkDesignAction.setEnabled(False)
                self.updateTestAction.setEnabled(False)
                self.checkAction.setEnabled(False)
                self.runAction.setEnabled(False)
                self.runStepByStepAction.setEnabled(False)
                self.runBreakpointAction.setEnabled(False)
                self.runNowAction.setEnabled(False)
                self.runDebugAction.setEnabled(False)
                self.runSchedAction.setEnabled(False)
                self.runBackgroundAction.setEnabled(False)
                self.runWithoutProbesAction.setEnabled(False)
                self.runWithoutNotifAction.setEnabled(False)

            self.codefoldingAction.setEnabled(True)
            if self.codeFolding:
                self.foldAllAction.setEnabled(True)
            else:
                self.foldAllAction.setEnabled(False)
            self.codeWrappingAction.setEnabled(True)
            self.whitespaceVisibilityAction.setEnabled(True)
            self.indentGuidesVisibilityAction.setEnabled(True)
            self.linesNumberingAction.setEnabled(True)

        elif isinstance(wdocument, TestPlan.WTestPlan):
            self.exportAsAction.setEnabled(True)
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(False)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(False)
            self.uncommentAction.setEnabled(False)
            self.indentAction.setEnabled(False)
            self.unindentAction.setEnabled(False)

            self.copyAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.pasteAction.setEnabled(False)
            self.selectAllAction.setEnabled(False)

            self.undoAction.setEnabled( False )
            self.redoAction.setEnabled( False )

            if RCI.instance().isAuthenticated():
                self.checkSyntaxAction.setEnabled(True)
                self.checkDesignAction.setEnabled(True)
                self.updateTestAction.setEnabled(False)
                self.checkAction.setEnabled(True)
                self.runAction.setEnabled(True)
                self.runStepByStepAction.setEnabled(True)
                self.runBreakpointAction.setEnabled(True)
                self.runNowAction.setEnabled(True)
                self.runDebugAction.setEnabled(True)
                self.runSchedAction.setEnabled(True)
                self.runBackgroundAction.setEnabled(True)
                self.runWithoutProbesAction.setEnabled(True)
                self.runWithoutNotifAction.setEnabled(True)
            else:
                self.checkSyntaxAction.setEnabled(False)
                self.checkDesignAction.setEnabled(False)
                self.updateTestAction.setEnabled(False)
                self.checkAction.setEnabled(False)
                self.runAction.setEnabled(False)
                self.runStepByStepAction.setEnabled(False)
                self.runBreakpointAction.setEnabled(False)
                self.runDebugAction.setEnabled(False)
                self.runNowAction.setEnabled(False)
                self.runSchedAction.setEnabled(False)
                self.runBackgroundAction.setEnabled(False)
                self.runWithoutProbesAction.setEnabled(False)
                self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(False)
            self.codefoldingAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(False)
            self.indentGuidesVisibilityAction.setEnabled(False)
            self.linesNumberingAction.setEnabled(False)

        elif isinstance(wdocument, TestAbstract.WTestAbstract):
            self.exportAsAction.setEnabled(True)
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(False)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(False)
            self.uncommentAction.setEnabled(False)
            self.indentAction.setEnabled(False)
            self.unindentAction.setEnabled(False)

            self.copyAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.pasteAction.setEnabled(False)
            self.selectAllAction.setEnabled(False)

            self.undoAction.setEnabled( False )
            self.redoAction.setEnabled( False )

            if RCI.instance().isAuthenticated():
                self.checkSyntaxAction.setEnabled(True)
                self.checkDesignAction.setEnabled(True)
                self.updateTestAction.setEnabled(False)
                self.checkAction.setEnabled(True)
                self.runAction.setEnabled(True)
                self.runStepByStepAction.setEnabled(True)
                self.runBreakpointAction.setEnabled(True)
                self.runNowAction.setEnabled(True)
                self.runDebugAction.setEnabled(True)
                self.runSchedAction.setEnabled(True)
                self.runBackgroundAction.setEnabled(True)
                self.runWithoutProbesAction.setEnabled(True)
                self.runWithoutNotifAction.setEnabled(True)
            else:
                self.checkSyntaxAction.setEnabled(False)
                self.checkDesignAction.setEnabled(False)
                self.updateTestAction.setEnabled(False)
                self.checkAction.setEnabled(False)
                self.runAction.setEnabled(False)
                self.runStepByStepAction.setEnabled(False)
                self.runBreakpointAction.setEnabled(False)
                self.runDebugAction.setEnabled(False)
                self.runNowAction.setEnabled(False)
                self.runSchedAction.setEnabled(False)
                self.runBackgroundAction.setEnabled(False)
                self.runWithoutProbesAction.setEnabled(False)
                self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(False)
            self.codefoldingAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(False)
            self.indentGuidesVisibilityAction.setEnabled(False)
            self.linesNumberingAction.setEnabled(False)

        elif isinstance(wdocument, TestPng.WTestPng):
            self.exportAsAction.setEnabled(True)
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(False)
            self.printAction.setEnabled(False)
            self.commentAction.setEnabled(False)
            self.uncommentAction.setEnabled(False)
            self.indentAction.setEnabled(False)
            self.unindentAction.setEnabled(False)

            self.copyAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.pasteAction.setEnabled(False)
            self.selectAllAction.setEnabled(False)

            self.undoAction.setEnabled( False )
            self.redoAction.setEnabled( False )
            
            self.checkSyntaxAction.setEnabled(False)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(False)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)
            
            self.codeWrappingAction.setEnabled(False)
            self.codefoldingAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(False)
            self.indentGuidesVisibilityAction.setEnabled(False)
            self.linesNumberingAction.setEnabled(False)

        elif isinstance(wdocument, TestConfig.WTestConfig):
            self.exportAsAction.setEnabled(True)
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(False)
            self.printAction.setEnabled(False)
            self.commentAction.setEnabled(False)
            self.uncommentAction.setEnabled(False)
            self.indentAction.setEnabled(False)
            self.unindentAction.setEnabled(False)

            self.copyAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.pasteAction.setEnabled(False)
            self.selectAllAction.setEnabled(False)

            self.undoAction.setEnabled( False )
            self.redoAction.setEnabled( False )
            
            self.checkSyntaxAction.setEnabled(False)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(False)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)
            
            self.codeWrappingAction.setEnabled(False)
            self.codefoldingAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(False)
            self.indentGuidesVisibilityAction.setEnabled(False)
            self.linesNumberingAction.setEnabled(False)
       
        elif isinstance(wdocument, TestAdapter.WTestAdapter):
            self.exportAsAction.setEnabled(False)
            curEditor = wdocument.currentEditor()
            if curEditor is None:
                return
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)

            self.findAction.setEnabled(True)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(True)
            self.uncommentAction.setEnabled(True)
            self.indentAction.setEnabled(True)
            self.unindentAction.setEnabled(True)
            
            state = curEditor.hasSelectedText()
            self.copyAction.setEnabled(state)
            self.cutAction.setEnabled(state)
            self.deleteAction.setEnabled(state)
            self.pasteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)
            
            self.undoAction.setEnabled( curEditor.isUndoAvailable() )
            self.redoAction.setEnabled( curEditor.isRedoAvailable() )

            self.checkSyntaxAction.setEnabled(True)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(True)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(True)
            self.codefoldingAction.setEnabled(True)
            self.foldAllAction.setEnabled(True)
            self.whitespaceVisibilityAction.setEnabled(True)
            self.indentGuidesVisibilityAction.setEnabled(True)
            self.linesNumberingAction.setEnabled(True)
        
        elif isinstance(wdocument, TestLibrary.WTestLibrary):
            self.exportAsAction.setEnabled(False)
            curEditor = wdocument.currentEditor()
            if curEditor is None:
                return
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)
  
            self.findAction.setEnabled(True)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(True)
            self.uncommentAction.setEnabled(True)
            self.indentAction.setEnabled(True)
            self.unindentAction.setEnabled(True)
            
            state = curEditor.hasSelectedText()
            self.copyAction.setEnabled(state)
            self.cutAction.setEnabled(state)
            self.deleteAction.setEnabled(state)
            self.pasteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)
            
            self.undoAction.setEnabled( curEditor.isUndoAvailable() )
            self.redoAction.setEnabled( curEditor.isRedoAvailable() )

            self.checkSyntaxAction.setEnabled(True)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(True)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(True)
            self.codefoldingAction.setEnabled(True)
            self.foldAllAction.setEnabled(True)
            self.whitespaceVisibilityAction.setEnabled(True)
            self.indentGuidesVisibilityAction.setEnabled(True)
            self.linesNumberingAction.setEnabled(True)
        
        elif isinstance(wdocument, TestTxt.WTestTxt):
            self.exportAsAction.setEnabled(False)
            curEditor = wdocument.currentEditor()
            if curEditor is None:
                return
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)
     
            self.findAction.setEnabled(True)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(True)
            self.uncommentAction.setEnabled(True)
            self.indentAction.setEnabled(True)
            self.unindentAction.setEnabled(True)
            
            state = curEditor.hasSelectedText()
            self.copyAction.setEnabled(state)
            self.cutAction.setEnabled(state)
            self.deleteAction.setEnabled(state)
            self.pasteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)
            
            self.undoAction.setEnabled( curEditor.isUndoAvailable() )
            self.redoAction.setEnabled( curEditor.isRedoAvailable() )
    
            self.checkSyntaxAction.setEnabled(False)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(False)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(True)
            self.codefoldingAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(True)
            self.indentGuidesVisibilityAction.setEnabled(True)
            self.linesNumberingAction.setEnabled(True)
        
        elif isinstance(wdocument, TestData.WTestData):
            self.exportAsAction.setEnabled(True)
            curEditor = wdocument.currentEditor()
            if curEditor is None:
                return
            if wdocument.isModified():
                self.saveAction.setEnabled(True)
            else:
                self.saveAction.setEnabled(False)
   
            self.findAction.setEnabled(True)
            self.printAction.setEnabled(True)
            self.commentAction.setEnabled(True)
            self.uncommentAction.setEnabled(True)
            self.indentAction.setEnabled(True)
            self.unindentAction.setEnabled(True)
            
            state = curEditor.hasSelectedText()
            self.copyAction.setEnabled(state)
            self.cutAction.setEnabled(state)
            self.deleteAction.setEnabled(state)
            self.pasteAction.setEnabled(True)
            self.selectAllAction.setEnabled(True)
            
            self.undoAction.setEnabled( curEditor.isUndoAvailable() )
            self.redoAction.setEnabled( curEditor.isRedoAvailable() )
    
            self.checkSyntaxAction.setEnabled(False)
            self.checkDesignAction.setEnabled(False)
            self.updateTestAction.setEnabled(False)
            self.checkAction.setEnabled(False)
            self.runAction.setEnabled(False)
            self.runStepByStepAction.setEnabled(False)
            self.runBreakpointAction.setEnabled(False)
            self.runNowAction.setEnabled(False)
            self.runDebugAction.setEnabled(False)
            self.runSchedAction.setEnabled(False)
            self.runBackgroundAction.setEnabled(False)
            self.runWithoutProbesAction.setEnabled(False)
            self.runWithoutNotifAction.setEnabled(False)

            self.codeWrappingAction.setEnabled(True)
            self.codefoldingAction.setEnabled(False)
            self.foldAllAction.setEnabled(False)
            self.whitespaceVisibilityAction.setEnabled(True)
            self.indentGuidesVisibilityAction.setEnabled(True)
            self.linesNumberingAction.setEnabled(True)
        else:
            pass
    
    def globalCallback (self):
        """
        Global callback to dispatch actions to editors
        """
        widget = QApplication.focusWidget()
        action = self.sender()
        if sys.version_info > (3,): # python3 support
            callback = action.data()
        else:
            callback = unicode(action.data().toString())
        if isinstance(widget, PyEditor):
            getattr(widget, callback)()

    def updateTabTitle (self, wdoc, title):
        """
        Updates the title of the tab

        @param wdoc: 
        @type wdoc: 

        @param title: new title of the document
        @type title: string
        """
        tabId = self.tab.indexOf(wdoc)
        self.tab.setTabText( tabId, self.addTag( repoType=wdoc.repoDest, txt=title, 
                                                addSlash=False, project=wdoc.project) )
        self.updateActions(wdocument=wdoc)
        windowTitle = wdoc.getPath( absolute=True, withAsterisk = True )
        windowTitleFinal = self.addTag( repoType=wdoc.repoDest, txt=windowTitle, 
                                        project=wdoc.project )
        # emit signal
        self.UpdateWindowTitle.emit(windowTitleFinal)

    def addTag(self, repoType, txt, addSlash=True, project=0):
        """
        Add repository tag
         * local-tests
         * remote-tests
         * remote-adapters
         * remote-libraries
         * undefined
         * unknown
        """
        # add fix to support & in filename, ampersand is used 
        # as a shortcut for the tab by pyqt
        txt = txt.replace("&", "&&")
        # end of fix
         
        if repoType == UCI.REPO_TESTS_LOCAL:
            repo = "local-tests"
        elif repoType == UCI.REPO_TESTS:
            repo = "remote-tests"
            project_name = self.iRepo.remote().getProjectName(project=project)
            repo += '(%s)' % project_name
        elif repoType == UCI.REPO_ADAPTERS:
            repo = "remote-adapters"
        elif repoType == UCI.REPO_LIBRARIES:
            repo = "remote-libraries"
        elif repoType == UCI.REPO_UNDEFINED:
            repo = "undefined"
        else:
            repo = "unknown"
            self.error( "repo unknown: %s" % repoType )
        if addSlash:
            if repoType == UCI.REPO_TESTS_LOCAL:
                ret = "%s:%s" % (repo,  txt) 
            else:
                ret = "%s:/%s" % (repo, txt) 
        else:
            ret = "%s: %s" % (repo, txt) 
        return ret

    def closeAllTab (self):
        """
        Close all tab
        """
        for tabId in xrange( self.tab.count() ):
            self.closeCurrentTab()

    def closeCurrentTab (self):
        """
        Close the current tab
        """
        tabId = self.tab.currentIndex()
        doc = self.tab.widget(tabId)
        
        # put the index on the second tab
        if isinstance(doc, WelcomePage): 
            if self.tab.count() >=1 :
                self.tab.setCurrentIndex(1)
            else:
                return
            
        self.closeTab( tabId = tabId )

    def closeTabWidget(self, wtab):
        """
        Close tabwidget
        """
        tabId =  self.tab.indexOf(wtab)
        self.closeTab(tabId=tabId)

    def closeTab (self, tabId):
        """
        Called when a tab is closed

        @param tabId: Tab's index in the QTabWidget
        @type tabId: Integer
        """
        doc = self.tab.widget(tabId)
        # bypass the welcome page
        if isinstance(doc, WelcomePage): 
            return
        # end of bypass
        
        if doc.isModified():
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ) ,
                self.tr("Save changes to %s ?" % doc.filename) , buttons)
            if answer == QMessageBox.Yes:
                isSaved = self.saveTab(tabId = tabId, closeTabAfter=True)
                if isSaved:
                    self.removeTab(tabId, doc)
                    #del doc
            elif answer == QMessageBox.No:
                self.removeTab(tabId, doc)
        else:
            self.removeTab(tabId, doc)
        
        if doc.isSaved():
            project_name = self.iRepo.remote().getProjectName(project=doc.project)
            self.addToRecent( filepath = doc.getPath(absolute=True), 
                                repodest=doc.repoDest, project=project_name )
        
        # destroy doc
        del doc
        
        self.resetTab()
    
    def removeTab(self, tabId, doc):
        """
        Remove tab
        """
        self.tab.removeTab(tabId)
        
        # unlock the file on server side
        if doc.extension not in [ TestPng.TYPE ]:
            if doc.isRemote and doc.path is not None:
                if RCI.instance().isAuthenticated():
                    if doc.repoDest == UCI.REPO_TESTS:
                        RCI.instance().unlockTestFile(filePath=doc.path, fileName=doc.filename, 
                                                      fileExtension=doc.extension, 
                                                      projectId=int(doc.project) )
                    elif doc.repoDest == UCI.REPO_ADAPTERS:
                        RCI.instance().unlockAdapterFile(filePath=doc.path, fileName=doc.filename, 
                                                         fileExtension=doc.extension )
                    elif doc.repoDest == UCI.REPO_LIBRARIES:
                        RCI.instance().unlockLibraryFile(filePath=doc.path, fileName=doc.filename, 
                                                         fileExtension=doc.extension )
                    else:
                        pass
                        
    def resetTab(self):
        """
        Reset the tab
        """
        if self.tab.count() == 0:
            self.clearWorkspace()
        else:
            if self.tab.count() == 1:
                wdoc = self.tab.widget(0)
                if isinstance(wdoc, WelcomePage):
                    self.clearWorkspace()

    def clearWorkspace(self):
        """
        Clear the workspace
        """
        self.findWidget.clearText()
        self.findWidget.setDisabled(True)
        self.DocumentViewerEmpty.emit()
        self.UpdateWindowTitle.emit("")
        self.setDefaultActionsValues()
        
    def currentTabChanged (self, tabId):
        """
        Called when the current tab changed

        @param tabId: Tab's index in the QTabWidget
        @type tabId: Integer
        """
        if tabId == -1:
            windowTitle = None
        else:
            wdoc = self.tab.widget(tabId)

            if not isinstance(wdoc, WelcomePage):
                windowTitle = wdoc.getPath( absolute=True, withAsterisk = True )
                windowTitleFinal = self.addTag( repoType=wdoc.repoDest, 
                                                txt=windowTitle, project=wdoc.project )

            # emit signal
            self.CurrentDocumentChanged.emit(wdoc)

            if isinstance(wdoc, WelcomePage):
                self.findWidget.setDisabled(True)
                self.findWidget.hide()
            elif wdoc.extension == TestAbstract.TYPE:
                self.findWidget.setDisabled(True)
                self.findWidget.hide()
            elif wdoc.extension == TestUnit.TYPE:
                # self.findWidget.show()
                self.findWidget.setDisabled(False)
                self.findWidget.setEditor( editor = wdoc.srcEditor)
            elif wdoc.extension == TestData.TYPE:
                # self.findWidget.show()
                self.findWidget.setDisabled(False)
                self.findWidget.setEditor( editor = wdoc.srcEditor)
            elif wdoc.extension == TestSuite.TYPE:
                # self.findWidget.show()
                self.findWidget.setDisabled(False)
                self.findWidget.setEditor( editor = wdoc.srcEditor)
            elif wdoc.extension == TestPlan.TYPE or wdoc.extension == TestPlan.TYPE_GLOBAL:
                wdoc.reloadSelectedItem()
                self.findWidget.setDisabled(True)
                self.findWidget.hide()
            elif wdoc.extension == TestConfig.TYPE:
                self.findWidget.setDisabled(True)
                self.findWidget.hide()
            elif wdoc.extension == TestAdapter.TYPE:
                # self.findWidget.show()
                self.findWidget.setDisabled(False)
                self.findWidget.setEditor( editor = wdoc.srcEditor)
            elif wdoc.extension == TestLibrary.TYPE:
                # self.findWidget.show()
                self.findWidget.setDisabled(False)
                self.findWidget.setEditor( editor = wdoc.srcEditor)
            elif wdoc.extension == TestTxt.TYPE:
                # self.findWidget.show()
                self.findWidget.setDisabled(False)
                self.findWidget.setEditor( editor = wdoc.srcEditor)
            else:
                self.findWidget.setDisabled(True)
                self.findWidget.hide()

            if RCI.instance().isAuthenticated():
                self.updateActions(wdocument = wdoc)
            else:
                self.findWidget.setDisabled(True)
                
            # emit signal
            if isinstance(wdoc, WelcomePage):
                self.UpdateWindowTitle.emit("")
            else:
                self.UpdateWindowTitle.emit(windowTitleFinal)

    def setCloseButton(self, tabId, doc):
        """
        Set the closable button
        """
        button = QToolButton()
        button.setIcon(QIcon(":/test-close-black.png"))
        button.setToolTip(self.tr("Close"))
        button.setIconSize(QSize(15,15))
        button.setStyleSheet( """
                     QToolButton {
                         border: none;
                         padding-right: 1px;

                     }

                     QToolButton:hover
                    {
                        border: 1px solid #8f8f91;
                        
                    }

                  """)
        action = lambda: self.closeTabWidget(doc)
        button.clicked.connect(action)

        self.tab.tabBar().setTabButton(tabId, QTabBar.RightSide, button)

    def prepareDocument(self):
        """
        Prepare document
        Check the syntax
        """
        self.checkSyntaxDocument()

    def newTab(self, path = None, filename = None, extension = None, remoteFile=False, contentFile=None, 
                    repoDest=None, newAdp=False, newLib=False, project=0, testDef=None, testExec=None,
                    testInputs=None, testOutputs=None, testAgents=None, isReadOnly=False, isLocked=False,
                    subtest_id=""):
        """
        Called to open a document

        @param path: path of the document "c:\test\"
        @type path: string

        @param filename: filename of the document "sample"
        @type filename: string

        @param extension: extension of the document (tsx)
        @type extension: string

        @param remoteFile:
        @type remoteFile: boolean

        @param contentFile:
        @type contentFile: 
        """
        if RCI.instance() is None: return
        
        if RCI.instance().authenticated: self.runAction.setEnabled(True)
        if RCI.instance().authenticated: self.runStepByStepAction.setEnabled(True)
        if RCI.instance().authenticated: self.runBreakpointAction.setEnabled(True)
        if RCI.instance().authenticated: self.runBackgroundAction.setEnabled(True)
        if RCI.instance().authenticated: self.checkSyntaxAction.setEnabled(True)
        if RCI.instance().authenticated: self.checkDesignAction.setEnabled(True)
        if RCI.instance().authenticated: self.updateTestAction.setEnabled(True)
        if RCI.instance().authenticated: self.runSchedAction.setEnabled(True)
        if RCI.instance().authenticated: self.checkAction.setEnabled(True)
        
        self.saveAsAction.setEnabled(True)
        self.codefoldingAction.setEnabled(True)
        self.codeWrappingAction.setEnabled(True)
        self.whitespaceVisibilityAction.setEnabled(True)
        self.indentGuidesVisibilityAction.setEnabled(True)
        self.closeTabAction.setEnabled(True)
        self.closeAllTabAction.setEnabled(True)
        
        # normalize extension to lower case
        extension = extension.lower()
        
        absPath = r'%s/%s.%s' % (path, filename, extension)
        if path is not None:
            if len(path) == 0:
                absPath = r'%s.%s' % (filename, extension)

        if extension == TestAdapter.TYPE or extension == TestLibrary.TYPE or  extension == TestTxt.TYPE:
            cur_prj_id = 0
        else:
            cur_prj_id = project
                    
        # new in v17
        nameLimit = Settings.instance().readValue( key = 'Editor/tab-name-limit' )
        nameLimit = int(nameLimit)
        # end of new
        
        tabId = self.checkAlreadyOpened(path = absPath, remoteFile=remoteFile, 
                                        repoType=repoDest, project=cur_prj_id)
        if tabId is not None:
            self.tab.setCurrentIndex(tabId)
            
            # dbr13 >>> Find usage
            if extension in [TestPlan.TYPE, TestPlan.TYPE_GLOBAL]:
                doc = self.getCurrentDocument()
                doc.showFileUsageLine(line_id=subtest_id)
            # dbr13 <<<
            
        else:
            __error__ = False
            if extension == TestAbstract.TYPE:
                doc = TestAbstract.WTestAbstract(self, path, filename, extension, self.nonameIdTp,
                                                remoteFile,repoDest, project, isLocked)
                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTa += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Test Abstract file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )

                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestAbstract.TYPE) )
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'TestProperties/show-on-opening' ) ): 
                        self.ShowPropertiesTab.emit()
                    self.setCloseButton(tabId=tabId, doc=doc)
 
            elif extension == TestUnit.TYPE:
                doc = TestUnit.WTestUnit(self, path, filename, extension, self.nonameIdTs, 
                                            remoteFile, repoDest, project, isLocked)
                if filename is None:
                    doc.defaultLoad(testDef=testDef, testInputs=testInputs, 
                                    testOutputs=testOutputs, testAgents=testAgents)
                    doc.setModify()
                    self.nonameIdTs += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Test Unit file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )

                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName)
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestUnit.TYPE) )
                    self.setCloseButton(tabId=tabId, doc=doc)
                    
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'TestProperties/show-on-opening' ) ): 
                        self.ShowPropertiesTab.emit()
                    
                    doc.setFolding( self.codeFolding )
                    doc.setIndentationGuidesVisible( self.indentationGuidesVisible )
                    doc.setWhitespaceVisible( self.whitespaceVisible )
                    doc.setLinesNumbering( self.linesNumbering )
                    doc.foldAll()
                    doc.setDefaultCursorPosition()
            
            elif extension == TestPng.TYPE:
                doc = TestPng.WTestPng(self, path, filename, extension, self.nonameIdTs, 
                                        remoteFile, repoDest, project)
                self.BusyCursor.emit()
                res = doc.load(contentFile)
                self.ArrowCursor.emit()
                if not res:
                    __error__ = True
                    del doc
                    QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Png file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/png.png") )
                    self.setCloseButton(tabId=tabId, doc=doc)

            elif extension == TestSuite.TYPE:
                # self.findWidget.show()
                doc = TestSuite.WTestSuite(self, path, filename, extension, self.nonameIdTs, 
                                            remoteFile, repoDest, project, isLocked)
                if filename is None:
                    doc.defaultLoad(testDef=testDef, testExec=testExec, testInputs=testInputs, 
                                        testOutputs=testOutputs, testAgents=testAgents)
                    doc.setModify()
                    self.nonameIdTs += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , 
                                            self.tr("Corrupted Test Suite file") )
                if not __error__:

                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName)
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestSuite.TYPE) )
                    self.setCloseButton(tabId=tabId, doc=doc)

                    if QtHelper.str2bool( Settings.instance().readValue( key = 'TestProperties/show-on-opening' ) ): 
                        self.ShowPropertiesTab.emit()
                    
                    doc.setFolding( self.codeFolding )
                    doc.setIndentationGuidesVisible( self.indentationGuidesVisible )
                    doc.setWhitespaceVisible( self.whitespaceVisible )
                    doc.setLinesNumbering( self.linesNumbering )
                    doc.foldAll()
                    doc.setDefaultCursorPosition()
            
            elif extension == TestPlan.TYPE:
                doc = TestPlan.WTestPlan(self, path, filename, extension, self.nonameIdTp,remoteFile,repoDest, project, 
                                            iRepo=self.iRepo, lRepo=self.lRepo, isLocked=isLocked )
                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTp += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Test Plan file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestPlan.TYPE) )
                    self.setCloseButton(tabId=tabId, doc=doc)
                    
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'TestProperties/show-on-opening' ) ): 
                        self.ShowPropertiesTab.emit()

            elif extension == TestPlan.TYPE_GLOBAL:
                doc = TestPlan.WTestPlan(self, path, filename, extension, self.nonameIdTp,remoteFile,repoDest, project, 
                                            iRepo=self.iRepo, testGlobal=True, lRepo=self.lRepo, isLocked=isLocked )
                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTp += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Test Global file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestPlan.TYPE_GLOBAL) )
                    self.setCloseButton(tabId=tabId, doc=doc)
                    
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'TestProperties/show-on-opening' ) ): 
                        self.ShowPropertiesTab.emit()

            elif extension == TestConfig.TYPE:
                doc = TestConfig.WTestConfig(self, path, filename, extension, self.nonameIdTp,
                                            remoteFile,repoDest, project, isLocked)
                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTp += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted config file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestConfig.TYPE) )
                    self.setCloseButton(tabId=tabId, doc=doc)

            elif extension == TestAdapter.TYPE and newAdp:
                # self.findWidget.show()
                doc = TestAdapter.WTestAdapter(self, path, filename, extension, self.nonameIdTs,
                                                remoteFile, repoDest, project=0, isLocked=isLocked)

                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTs += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted adapter file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/file-adp2.png") )
                    self.setCloseButton(tabId=tabId, doc=doc)

                    doc.setFolding( self.codeFolding )
                    doc.setIndentationGuidesVisible( self.indentationGuidesVisible )
                    doc.setWhitespaceVisible( self.whitespaceVisible )
                    doc.setLinesNumbering( self.linesNumbering )
                    doc.setDefaultCursorPosition()

            elif extension == TestLibrary.TYPE and newLib:
                # self.findWidget.show()
                doc = TestLibrary.WTestLibrary(self, path, filename, extension, self.nonameIdTs, 
                                                remoteFile, repoDest, project=0, isLocked=isLocked)

                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTs += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted library file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/file-lib-adp.png") )
                    self.setCloseButton(tabId=tabId, doc=doc)

                    doc.setFolding( self.codeFolding )
                    doc.setIndentationGuidesVisible( self.indentationGuidesVisible )
                    doc.setWhitespaceVisible( self.whitespaceVisible )
                    doc.setLinesNumbering( self.linesNumbering )
                    doc.setDefaultCursorPosition()

            elif extension == TestTxt.TYPE:
                # self.findWidget.show()
                doc = TestTxt.WTestTxt(self, path, filename, extension, self.nonameIdTs, remoteFile,
                                        repoDest, project=0, isLocked=isLocked)
                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTs += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)
                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Txt file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/file-txt.png") )
                    self.setCloseButton(tabId=tabId, doc=doc)
                    
                    doc.setFolding( self.codeFolding )
                    doc.setIndentationGuidesVisible( self.indentationGuidesVisible )
                    doc.setWhitespaceVisible( self.whitespaceVisible )
                    doc.setLinesNumbering( self.linesNumbering )
                    doc.setDefaultCursorPosition()
            
            elif extension == TestData.TYPE:
                # self.findWidget.show()
                doc = TestData.WTestData(self, path, filename, extension, self.nonameIdTs, 
                                        remoteFile, repoDest, project, isLocked)
                if filename is None:
                    doc.defaultLoad()
                    doc.setModify()
                    self.nonameIdTs += 1
                else:
                    self.BusyCursor.emit()
                    res = doc.load(contentFile)

                    # active xml lexer, depend of the value in data mode in the description of the test
                    # new in 8.0.0
                    if 'descriptions' in doc.dataModel.properties['properties']:
                        dataMode = None
                        for kv in doc.dataModel.properties['properties']['descriptions']['description']:
                            if kv['key'] == 'data mode':
                                dataMode = kv['value']
                        if dataMode is not None:
                            if dataMode.lower() == 'xml':
                                doc.activeXmlLexer()
                    # end in 8.0.0

                    self.ArrowCursor.emit()
                    if not res:
                        __error__ = True
                        del doc
                        QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted Test Data file") )
                if not __error__:
                    tabName = self.addTag( repoType=doc.repoDest, txt=doc.getShortName(), 
                                            addSlash=False, project=doc.project )
                    
                    # new in v17
                    if nameLimit == 0:
                        _tabName = tabName
                    else:
                        if len(tabName) > nameLimit:
                            _tabName = "%s..." % tabName[:nameLimit]
                        else:
                            _tabName = tabName
                    # end of new in v17
                    
                    tabId = self.tab.addTab(doc, _tabName )
                    self.tab.setTabIcon(tabId, QIcon(":/%s.png" % TestData.TYPE) )
                    self.setCloseButton(tabId=tabId, doc=doc)
                    
                    self.ShowPropertiesTab.emit()
                    
                    doc.setFolding( self.codeFolding )
                    doc.setIndentationGuidesVisible( self.indentationGuidesVisible )
                    doc.setWhitespaceVisible( self.whitespaceVisible )
                    doc.setLinesNumbering( self.linesNumbering )
                    doc.setDefaultCursorPosition()
            
            else:
                self.error( "extension unknown %s" % extension )
            
            if not __error__:     
                # set the current tab index
                self.tab.setCurrentIndex( tabId )
                # update tooltip of the tab
                self.tab.setTabToolTip( tabId, doc.getPath(absolute=True) )
                self.updateActions( wdocument=doc )
                self.findWidget.setEnabled(True)
                self.DocumentOpened.emit(doc)
                
                # dbr13 >>>> Find Usage functionality
                if extension in [TestPlan.TYPE, TestPlan.TYPE_GLOBAL]:
                    doc.showFileUsageLine(line_id=subtest_id)
                # dbr13 <<<
                
    def addToRecent(self, filepath, repodest, project=''):
        """
        Add file to recent list
        Emit signal
        """
        tpl = {'file': filepath, 'type': repodest, 'project': project }
        self.RecentFile.emit(tpl)

    def newTestConfig(self):
        """
        Creates one new empty TestConfig file
        Call the function newTab()
        """
        self.newTab( extension = TestConfig.TYPE, repoDest=UCI.REPO_UNDEFINED )
        self.findWidget.setDisabled(True)

    def newTestAdapter(self):
        """
        Creates one new empty TestAdapter file
        Call the function newTab()
        """
        self.newTab( extension = TestAdapter.TYPE, repoDest=UCI.REPO_UNDEFINED, newAdp=True )

    def newTestLibrary(self):
        """
        Creates one new empty TestLibrary file
        Call the function newTab()
        """
        self.newTab( extension = TestLibrary.TYPE, repoDest=UCI.REPO_UNDEFINED, newLib=True  )

    def newTestTxt(self):
        """
        Creates one new empty TestTxt file
        Call the function newTab()
        """
        self.newTab( extension = TestTxt.TYPE, repoDest=UCI.REPO_UNDEFINED )

    def newTestAbstract(self):
        """
        Creates one new empty TestAbstract file
        Call the function newTab()
        """
        self.newTab( extension = TestAbstract.TYPE, repoDest=UCI.REPO_UNDEFINED )

    def newTestUnit(self):
        """
        Creates one new empty TestUnit file
        Call the function newTab()
        """
        self.newTab( extension = TestUnit.TYPE, repoDest=UCI.REPO_UNDEFINED )

    def newTestSuite (self):
        """
        Creates one new empty TestSuite file
        Call the function newTab()
        """
        self.newTab( extension = TestSuite.TYPE, repoDest=UCI.REPO_UNDEFINED )

    def newTestSuiteWithContent (self, testDef=None, testExec=None, testInputs=None, 
                                    testOutputs=None, testAgents=None):
        """
        Creates one new empty TestSuite file
        Call the function newTab()
        """
        self.newTab( extension = TestSuite.TYPE, repoDest=UCI.REPO_UNDEFINED, testDef=testDef, 
                        testExec=testExec, testInputs=testInputs, 
                        testOutputs=testOutputs, testAgents=testAgents )
 
    def newTestAbstractWithContent(self, testDef=None, testInputs=None, testOutputs=None, testAgents=None):
        """
        Creates one new empty TestAbstract file
        Call the function newTab()
        """
        self.newTab( extension = TestAbstract.TYPE, repoDest=UCI.REPO_UNDEFINED, 
                        testDef=testDef, testInputs=testInputs,
                        testOutputs=testOutputs, testAgents=testAgents )
                        
    def newTestUnitWithContent(self, testDef=None, testInputs=None, testOutputs=None, testAgents=None):
        """
        Creates one new empty TestUnit file
        Call the function newTab()
        """
        self.newTab( extension = TestUnit.TYPE, repoDest=UCI.REPO_UNDEFINED, 
                    testDef=testDef, testInputs=testInputs,
                    testOutputs=testOutputs, testAgents=testAgents )
    
    def newTestPlan (self):
        """
        Creates one new empty TestPlan file
        Calls the function newTab()
        """
        self.newTab( extension = TestPlan.TYPE, repoDest=UCI.REPO_UNDEFINED )
        self.findWidget.setDisabled(True)

    def newTestGlobal (self):
        """
        Creates one new empty TestGlobal file
        Calls the function newTab()
        """
        self.newTab( extension = TestPlan.TYPE_GLOBAL, repoDest=UCI.REPO_UNDEFINED )
        self.findWidget.setDisabled(True)

    def newTestData(self):
        """
        Creates one new empty TestData file
        Call the function newTab()
        """
        self.newTab( extension = TestData.TYPE, repoDest=UCI.REPO_UNDEFINED )

    def saveTab (self, tabId = False, closeTabAfter=False):
        """
        Called to save the document identified by the tabId

        @param tabId: Tab's index in the QTabWidget
        @type tabId: Integer

        @return:
        @rtype: boolean
        """
        if tabId is False: tabId = self.tab.currentIndex()
        if tabId == -1:  return False
        currentDoc = self.tab.widget(tabId)
        
        if currentDoc is None:
            return
            
        # bypass welcome page
        if isinstance(currentDoc, WelcomePage):
            return False
        
        if currentDoc.isSaved():
            if currentDoc.isRemote:
                if currentDoc.isModified():
                    if RCI.instance().isAuthenticated():
            
                        if currentDoc.repoDest == UCI.REPO_ADAPTERS:
                            RCI.instance().uploadAdapterFile( filePath=currentDoc.path, fileName=currentDoc.filename, 
                                                              fileExtension=currentDoc.extension, 
                                                              fileContent=currentDoc.getraw_encoded(), 
                                                              updateMode=True, closeTabAfter=closeTabAfter )
                        elif currentDoc.repoDest == UCI.REPO_LIBRARIES:
                            RCI.instance().uploadLibraryFile( filePath=currentDoc.path, fileName=currentDoc.filename, 
                                                              fileExtension=currentDoc.extension, 
                                                              fileContent=currentDoc.getraw_encoded(), 
                                                              updateMode=True, closeTabAfter=closeTabAfter )
                        elif currentDoc.repoDest == UCI.REPO_TESTS:
                            RCI.instance().uploadTestFile( filePath=currentDoc.path, 
                                                           fileName=currentDoc.filename, 
                                                           projectId=int(currentDoc.project),
                                                           fileExtension=currentDoc.extension, 
                                                           fileContent=currentDoc.getraw_encoded(), 
                                                           updateMode=True, closeTabAfter=closeTabAfter )
                        else:
                            pass

                        return False
                    else:
                        QMessageBox.warning(self, self.tr("Save") , self.tr("Connect to the test center first!") )
                        return False
            else:
                isSaved = currentDoc.write()
                if isSaved is None:
                    QMessageBox.warning(self, self.tr("Save") , self.tr("Unable to save the file...") )
                    isSaved = False
                return isSaved
        else:
            if currentDoc.isModified():
                return self.saveTabAs(callFromSave=True, tabId=tabId)
            else:
                return False

    def exportTabAs (self):
        """
        Export tab as
        """
        ret = False
        
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDoc = self.tab.widget(tabId)

        if not ( isinstance(currentDoc, TestAdapter.WTestAdapter) or isinstance(currentDoc, TestLibrary.WTestLibrary) \
                    or isinstance(currentDoc, TestTxt.WTestTxt) ):
            ret = self.saveToAnywhere(tabId,currentDoc)
        return ret 

    def saveTabAs (self, callFromSave=False, tabId = False):
        """
        Saves the current document as

        @return:
        @rtype: boolean
        """
        ret = False
        
        if tabId is False: tabId = self.tab.currentIndex()
        if tabId == -1: return False
        currentDoc = self.tab.widget(tabId)
        
        if isinstance(currentDoc, TestAdapter.WTestAdapter) or isinstance(currentDoc, TestLibrary.WTestLibrary) \
                        or isinstance(currentDoc, TestTxt.WTestTxt):
            if RCI.instance().isAuthenticated():
                ret = self.saveToRemote(tabId,currentDoc)
            else:
                QMessageBox.warning(self, self.tr("Save") , self.tr("Connect to the test center first!") )
        else:
            self.localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
            
            if callFromSave:
                if Settings.instance().readValue( key = 'Repositories/default-repo-test' ) == str(TAB_REMOTE_POS):
                    if RCI.instance().isAuthenticated():
                        ret = self.saveToRemote(tabId,currentDoc)
                    else:
                        QMessageBox.warning(self, self.tr("Save") , self.tr("Connect to the test center first!") )
                else:
                    if self.localConfigured != "Undefined":
                        ret = self.saveToLocal(tabId,currentDoc)
                    else:
                        QMessageBox.warning(self, self.tr("Save") , self.tr("Local repository not configured!") )
            else:
                if self.localConfigured != "Undefined":
                    buttons = QMessageBox.Yes | QMessageBox.No
                    answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                                                    self.tr("Save in the local repository?") , buttons)
                    if answer == QMessageBox.Yes:
                        ret = self.saveToLocal(tabId,currentDoc)
                    else:
                        if RCI.instance().isAuthenticated():
                            ret = self.saveToRemote(tabId,currentDoc)
                        else:
                            QMessageBox.warning(self, self.tr("Save") , self.tr("Connect to the test center first!") )
                else:
                    if RCI.instance().isAuthenticated():
                        ret = self.saveToRemote(tabId,currentDoc)
                    else:
                        QMessageBox.warning(self, self.tr("Save") , self.tr("Connect to the test center first!") )
        return ret 

    def saveToLocal(self, tabId, currentDoc):
        """
        Save document to the local repository

        @param tabId: 
        @type tabId:

        @param currentDoc: 
        @type currentDoc:
        """
        ret = False

        self.iRepo.localDialogSave().setFilename( filename=currentDoc.getShortName( withAsterisk = False, 
                                                                                    withExtension = False, 
                                                                                    withLocalTag=False) )
        self.iRepo.localDialogSave().refresh()
        dialog = self.iRepo.localDialogSave()
        if dialog.exec_() == QDialog.Accepted:
            fileName = dialog.getSelection()
            currentDoc.isRemote = False
            ret = self.save( fileName = fileName, document = currentDoc, tabId = tabId, newFile=True )
            self.RefreshLocalRepository.emit()
        return ret

    def saveToRemote(self, tabId, currentDoc):
        """
        Save document to the remote repository

        @param tabId: 
        @type tabId:

        @param currentDoc: 
        @type currentDoc:
        """
        ret = False
        dialog = None
        repoDest = UCI.REPO_TESTS
        project = self.iRepo.remote().getCurrentProject()

        if isinstance(currentDoc, TestAdapter.WTestAdapter):
            repoDest = UCI.REPO_ADAPTERS
            self.iRepo.remoteAdapter().saveAs.setFilename( currentDoc.getShortName( withAsterisk = False, 
                                                                                    withExtension = False, 
                                                                                    withLocalTag=False) )
            dialog = self.iRepo.remoteAdapter().saveAs
        
        elif isinstance(currentDoc, TestLibrary.WTestLibrary):
            repoDest = UCI.REPO_LIBRARIES
            self.iRepo.remoteLibrary().saveAs.setFilename( currentDoc.getShortName( withAsterisk = False, 
                                                                                    withExtension = False, 
                                                                                    withLocalTag=False) )
            dialog = self.iRepo.remoteLibrary().saveAs
        
        elif currentDoc.extension == TestTxt.TYPE:
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ),  
                                            self.tr("Save in the adapters repository ?") , buttons)
            if answer == QMessageBox.Yes:
                repoDest = UCI.REPO_ADAPTERS
                self.iRepo.remoteAdapter().saveAs.setFilename( currentDoc.getShortName( withAsterisk = False, 
                                                                                        withExtension = False, 
                                                                                        withLocalTag=False) )
                dialog = self.iRepo.remoteAdapter().saveAs
            elif answer == QMessageBox.No:
                buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ),  
                                                self.tr("Save in the libraries repository ?") , buttons)
                if answer == QMessageBox.Yes:
                    repoDest = UCI.REPO_LIBRARIES
                    self.iRepo.remoteLibrary().saveAs.setFilename( currentDoc.getShortName( withAsterisk = False, 
                                                                                            withExtension = False, 
                                                                                            withLocalTag=False) )
                    dialog = self.iRepo.remoteLibrary().saveAs
        else:
            self.iRepo.remote().saveAs.setFilename( currentDoc.getShortName(withAsterisk = False, 
                                                                            withExtension = False, 
                                                                            withLocalTag=False), 
                                                    project=project )
            dialog = self.iRepo.remote().saveAs

        if dialog is not None:
            if dialog.exec_() == QDialog.Accepted:
                fileName = dialog.getSelection()
                newProject = dialog.getProjectSelection()
                projectid = self.iRepo.remote().getProjectId(project=str(newProject))
                try:
                    # workaround to detect special characters, same limitation as with python2 because of the server
                    # this limitation will be removed when the server side will be ported to python3
                    if sys.version_info > (3,): # python3 support only 
                        fileName.encode("ascii") 
                    else:
                        fileName = str(fileName)
                except UnicodeEncodeError as e:
                    QMessageBox.warning(self, self.tr("Save") , self.tr("Invalid name!") )
                else:
                    if "'" in fileName:
                        QMessageBox.warning(self, self.tr("Save") , self.tr("Invalid name!") )
                    else:
                        currentDoc.isRemote = True
                        ret = self.save( fileName = fileName, document = currentDoc, tabId = tabId, 
                                        repoDest=repoDest, project=projectid)
        return ret

    def saveToAnywhere(self, tabId, currentDoc):
        """
        Save document to anywhere

        @param tabId: 
        @type tabId:

        @param currentDoc: 
        @type currentDoc:
        """
        ret = False
        #
        fileName = QFileDialog.getSaveFileName(self, self.tr("Save file"), 
                                                currentDoc.filename, "*.%s" % currentDoc.extension)
                
        # new in v17.1
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if len(_fileName):
            if "'" in _fileName:
                QMessageBox.warning(self, self.tr("Save") , self.tr("Invalid name!") )
            else:
                currentDoc.isRemote=False
                ret = self.save( fileName = _fileName, document = currentDoc, 
                                tabId = tabId, newFile=True, fromAnywhere=True )
        return ret

    def save (self, fileName, document, tabId, newFile=False, fromAnywhere=False, repoDest=None, project=''):
        """
        Save 

        @param fileName: 
        @type fileName: 

        @param document: 
        @type document: 

        @param tabId: 
        @type tabId: 
        """
        isSaved = False
        
        # issue 8 fix begin
        if not fromAnywhere:
            completeFileName = "%s.%s" % (fileName, document.extension)
        else:
            completeFileName = fileName
        # issue 8 fix end 
        
        tmp = str(completeFileName).rsplit("/", 1)
        path = tmp[0]
        if len(tmp) > 1:
            filename = tmp[1].rsplit(".", 1)[0]
        else:
            filename = tmp[0].rsplit(".", 1)[0]
        
        document.path = path
        document.filename = filename

        if not fromAnywhere:
            if newFile:
                res = os.path.exists( completeFileName )
                if res:
                    document.path = None
                    QMessageBox.warning(self, 
                                        self.tr("Save As") , 
                                        self.tr("This filename already exists!") )
                    isSaved = False
                    return isSaved
        if not document.isRemote:
            isSaved = document.write(force = True)
            if isSaved:
                self.tab.setTabText(tabId, filename )
            if isSaved is None:     
                QMessageBox.critical(self, 
                                     self.tr("Save As") , 
                                     self.tr("Unable to save the file...") )
                isSaved = False
            self.iRepo.local().refreshAll()
            
            QMessageBox.information(self, 
                                    self.tr("Export"), 
                                    self.tr("File exported with success!") )
            
        else:
            document.project = project
            
            if repoDest == UCI.REPO_ADAPTERS:
                RCI.instance().uploadAdapterFile( filePath=document.path, 
                                                  fileName=document.filename, 
                                                  fileExtension=document.extension, 
                                                  fileContent=document.getraw_encoded(), 
                                                  updateMode=False, 
                                                  closeTabAfter=False )
            elif repoDest == UCI.REPO_LIBRARIES:
                RCI.instance().uploadLibraryFile( filePath=document.path, 
                                                  fileName=document.filename, 
                                                  fileExtension=document.extension, 
                                                  fileContent=document.getraw_encoded(), 
                                                  updateMode=False, 
                                                  closeTabAfter=False )
            elif repoDest == UCI.REPO_TESTS:
                RCI.instance().uploadTestFile( filePath=document.path, 
                                               fileName=document.filename, 
                                               projectId=int(project),
                                               fileExtension=document.extension, 
                                               fileContent=document.getraw_encoded(), 
                                               updateMode=False, 
                                               closeTabAfter=False )
            else:
                pass

        return isSaved
    
    def docAreModified(self):
        """
        Return the number of document modified
        """
        nbDoc = 0
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            
            if doc.isModified():
                nbDoc +=1
        return nbDoc
        
    def saveAllTabs (self, question = False):
        """
        Saves all documents

        @param question: 
        @type question: boolean

        @return: 
        @rtype: boolean
        """
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            
            if question and doc.isModified():
                buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                        self.tr("Save changes to %s ?" % doc.filename) , buttons)
                if answer == QMessageBox.Yes:
                    saved = self.saveTab(tabId = tabId)
                elif answer == QMessageBox.Cancel:
                    return False
            else:
                self.saveTab(tabId = tabId)
        return True

    def updateMacro(self):
        """
        Update macro
        """
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        
        currentDocument = self.tab.widget(tabId)
        
        isTu = False
        isTs = False
        if currentDocument.extension == TestUnit.TYPE:
            isTu = True
        if currentDocument.extension == TestSuite.TYPE:
            isTs = True
        self.GoMacroMode.emit(isTu, isTs)
        
    def checkDesignDocument (self):
        """
        Gets the current document and send it the server to check the syntax
        """

        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False

        currentDocument = self.tab.widget(tabId)
        projectName = self.iRepo.remote().getProjectName(project=currentDocument.project)

        _json = self.prepareTest( wdocument = currentDocument, 
                                  prjId=currentDocument.project, 
                                  basicMode=False)    
            
        if currentDocument.extension in [ RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT, RCI.EXT_TESTUNIT]:
            RCI.instance().createTestDesign( req=_json )
        elif currentDocument.extension in [ RCI.EXT_TESTPLAN, RCI.EXT_TESTGLOBAL]:
            RCI.instance().createTestDesignTpg( req=_json )
        else:
            pass
            
    def prepareTest (self, wdocument=None, tabId=0, background = False, runAt = (0,0,0,0,0,0), 
                           runType=0, runNb=-1, withoutProbes=False, debugActivated=False, 
                           withoutNotif=False, keepTr=True, prjId=0, testFileExtension=None, 
                           testFilePath=None, testFileName=None, fromTime=(0,0,0,0,0,0), 
                           toTime=(0,0,0,0,0,0), prjName='', stepByStep=False, breakpoint=False,
                           channelId=False, basicMode=False):
        """
        Prepare test

        @param testId: 
        @type testId:

        @param background: 
        @type background: boolean

        @param runAt: 
        @type runAt: tuple of integer

        @param runType: 
        @type runType: Integer

        @param runNb: 
        @type runNb:

        @param withoutProbes: 
        @type withoutProbes:

        @param debugActivated: 
        @type debugActivated:

        @param withoutNotif: 
        @type withoutNotif:

        @param noKeepTr: 
        @type noKeepTr:

        @param prjId: 
        @type prjId:

        @param testFileExtension: 
        @type testFileExtension:

        @param testFilePath: 
        @type testFilePath:

        @param testFileName: 
        @type testFileName:
        
        @return:
        @rtype:
        """
        data__ = {}
        try:
            if not basicMode:
                data__ =  { 'project-id': prjId, 
                            'tab-id': tabId, 
                            'background-mode': background, 
                            'schedule-at': runAt, 
                            'schedule-id': runType, 
                            'schedule-repeat': runNb, 
                            'probes-enabled': withoutProbes, 
                            'debug-enabled': debugActivated, 
                            'notifications-enabled': withoutNotif, 
                            'logs-enabled': keepTr,
                            'from-time': fromTime, 
                            'to-time': toTime, 
                            'step-mode': stepByStep, 
                            'breakpoint-mode': breakpoint, 
                            'channel-id': channelId 
                            }

            if wdocument is None:
                self.trace('no content, prepare test, type %s' % testFileExtension)
                data__.update( { 'test-definition': '', 
                                 'test-execution': '', 
                                 'test-properties': '',
                                 'test-name': testFileName,
                                 'test-path': testFilePath,
                                 'test-extension': testFileExtension } )
            else:
                self.trace('prepare test, type %s' % wdocument.extension)
                properties = copy.deepcopy( wdocument.dataModel.properties['properties'] )
                testfileName = wdocument.getShortName( withAsterisk = False, 
                                                       withLocalTag=False)
                testPath = ""
                if wdocument.isRemote:
                    testPath = wdocument.getPath(withExtension = False, withLocalTag=False)

                if wdocument.extension in [ RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT, RCI.EXT_TESTUNIT]:
                    # load datasets
                    self.__loadDataset(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadDataset(parameters=properties['outputs-parameters']['parameter'])

                    # load images
                    self.__loadImage(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadImage(parameters=properties['outputs-parameters']['parameter'])

                if wdocument.extension == RCI.EXT_TESTSUITE:
                    data__.update( { 'test-definition': unicode( wdocument.srcEditor.text() ), 
                                     'test-execution': unicode( wdocument.execEditor.text() ), 
                                     'test-properties': properties, 
                                     'test-name': testfileName,
                                     'test-path': testPath,
                                     'test-extension': wdocument.extension } )

                elif wdocument.extension == RCI.EXT_TESTABSTRACT:
                    data__.update( { 'test-definition': unicode( wdocument.constructTestDef() ), 
                                     'test-execution': '', 
                                     'test-properties': properties,
                                     'test-name': testfileName, 
                                     'test-path': testPath,
                                     'test-extension': wdocument.extension } )

                elif wdocument.extension == RCI.EXT_TESTUNIT:
                    data__.update( { 
                                        'test-definition': unicode( wdocument.srcEditor.text() ), 
                                        'test-execution': '', 
                                        'test-properties': properties,
                                        'test-name': testfileName, 
                                        'test-path': testPath,
                                        'test-extension': wdocument.extension } )

                elif wdocument.extension == RCI.EXT_TESTGLOBAL:
                    testglobal =  copy.deepcopy( wdocument.getDataModelSorted() )
                    localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
                    alltests = []
                    all_id = [] 
                    for ts in testglobal:   
                        all_id.append(ts['id'])
                        if ts['type'] == RCI.TESTPLAN_REPO_FROM_LOCAL or ts['type'] == RCI.TESTPLAN_REPO_FROM_LOCAL_REPO_OLD:
                            if localConfigured != "Undefined":
                                absPath = '%s/%s' % ( localConfigured, ts['file'] )
                            else:
                                raise Exception("local repository not configured")
                        elif ts['type'] == RCI.TESTPLAN_REPO_FROM_OTHER or ts['type'] == RCI.TESTPLAN_REPO_FROM_HDD:
                            absPath = ts['file'] 
                        elif ts['type'] == RCI.TESTPLAN_REPO_FROM_REMOTE:
                            pass
                        else:
                            raise Exception("test type from unknown: %s" % ts['type'])
                        
                        # load dataset
                        self.__loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'])

                        # load image
                        self.__loadImage(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadImage(parameters=ts['properties']['outputs-parameters']['parameter'])

                        if ts['type'] != RCI.TESTPLAN_REPO_FROM_REMOTE:
            
                            if not os.path.exists( absPath ):
                                raise Exception("the following test file is missing: %s " % absPath)
                            
                            if absPath.endswith(EXT_TESTSUITE):
                                doc = FileModelTestSuite.DataModel()
                            elif absPath.endswith(EXT_TESTUNIT):
                                doc = FileModelTestUnit.DataModel()
                            elif absPath.endswith(EXT_TESTABSTRACT):
                                doc = FileModelTestAbstract.DataModel()
                            elif absPath.endswith(EXT_TESTPLAN):
                                doc = FileModelTestPlan.DataModel()
                            else:
                                raise Exception("the following test extension file is incorrect: %s " % absPath)

                            res = doc.load( absPath = absPath )
                            if res:
                                try:
                                    tmp = str(ts['file']).rsplit("/", 1)
                                    if len(tmp) ==1:
                                        filenameTs = tmp[0].rsplit(".", 1)[0]
                                    else:
                                        filenameTs = tmp[1].rsplit(".", 1)[0]
                                except Exception as e:
                                    self.error( 'fail to parse filename: %s' % e)
                                    raise Exception('fail to parse filename')                                
                                # Update current test suite parameters with testplan parameter
                                self.__updateParameter( currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                                            newParam=ts['properties']['inputs-parameters']['parameter'] )
                                self.__updateParameter( currentParam=doc.properties['properties']['outputs-parameters']['parameter'],
                                                            newParam=ts['properties']['outputs-parameters']['parameter'] )

                                ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']
                                ts['properties']['outputs-parameters'] = doc.properties['properties']['outputs-parameters']

                                if absPath.endswith(RCI.EXT_TESTSUITE):
                                    ts.update( { 'test-definition': doc.testdef, 
                                                 'test-execution': doc.testexec, 
                                                 'path': filenameTs } )
                                    alltests.append( ts )
                                elif absPath.endswith(RCI.EXT_TESTUNIT):
                                    ts.update( { 'test-definition': doc.testdef, 
                                                 'test-execution': '', 
                                                 'path': filenameTs } ) 
                                    alltests.append( ts )
                                elif absPath.endswith(RCI.EXT_TESTABSTRACT):
                                    ts.update( { 'test-definition': doc.testdef, 
                                                 'test-execution': '', 
                                                 'path': filenameTs } ) 
                                    alltests.append( ts )
                                elif absPath.endswith(RCI.EXT_TESTPLAN):
                                    pass #todo
                        else:
                            alltests.append( ts )
                    data__.update( { 
                                        'test-execution': alltests, 
                                        'test-properties': properties, 
                                        'test-name': testfileName, 
                                        'test-path': testPath,
                                        'test-extension': wdocument.extension 
                                     } )
                    self.trace('TestGlobal, tests id order: %s' % all_id)

                elif wdocument.extension == RCI.EXT_TESTPLAN:
                    testplan =  copy.deepcopy( wdocument.getDataModelSorted() )                    
                    self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
                    all_id = [] 
                    for ts in testplan: 
                        all_id.append(ts['id'])
                        if ts['type'] == RCI.TESTPLAN_REPO_FROM_LOCAL or ts['type'] == RCI.TESTPLAN_REPO_FROM_LOCAL_REPO_OLD:
                            if self.localConfigured != "Undefined":
                                absPath = '%s/%s' % ( self.localConfigured, ts['file'] )
                            else:
                                raise Exception("local repository not configured")
                        elif ts['type'] == RCI.TESTPLAN_REPO_FROM_OTHER or ts['type'] == RCI.TESTPLAN_REPO_FROM_HDD:
                            absPath = ts['file'] 
                        elif ts['type'] == RCI.TESTPLAN_REPO_FROM_REMOTE:
                            pass
                        else:
                            raise Exception("test type from unknown: %s" % ts['type'])
                        
                        # load dataset
                        self.__loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'])

                        # load image
                        self.__loadImage(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadImage(parameters=ts['properties']['outputs-parameters']['parameter'])

                        if ts['type'] != RCI.TESTPLAN_REPO_FROM_REMOTE:
            
                            if not os.path.exists( absPath ):
                                raise Exception("the following test file is missing: %s " % absPath)
                            
                            if absPath.endswith(RCI.EXT_TESTSUITE):
                                doc = FileModelTestSuite.DataModel()
                            elif absPath.endswith(RCI.EXT_TESTABSTRACT):
                                doc = FileModelTestAbstract.DataModel()
                            else:
                                doc = FileModelTestUnit.DataModel()
                            res = doc.load( absPath = absPath )
                            if res:
                                tmp = str(ts['file']).rsplit("/", 1)
                                filenameTs = tmp[1].rsplit(".", 1)[0]
                                
                                # Update current test suite parameters with testplan parameter
                                self.__updateParameter( currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                                            newParam=ts['properties']['inputs-parameters']['parameter'] )
                                self.__updateParameter( currentParam=doc.properties['properties']['outputs-parameters']['parameter'],
                                                            newParam=ts['properties']['outputs-parameters']['parameter'] )

                                ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']
                                ts['properties']['outputs-parameters'] = doc.properties['properties']['outputs-parameters']

                                ts.update( { 'test-definition': doc.testdef, 
                                             'test-execution': doc.testexec, 
                                             'path': filenameTs } )
            
                    data__.update( { 
                                        'test-execution': testplan, 
                                        'test-properties': properties, 
                                        'test-name': testfileName, 
                                        'test-path': testPath,
                                        'test-extension': wdocument.extension 
                                        } )
                    self.trace('TestPlan, tests id order: %s' % all_id)

            # compress
            self.trace('test prepared')
        except Exception as e:
            self.error( e )
        return data__

    def __loadImage(self, parameters):
        """
        Private function
        Load image

        @param parameters: 
        @type parameters:
        """
        # self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
        for pr in parameters:
            if pr['type'] == 'image':
                if pr['value'].startswith('undefined:/'):
                    fileName = pr['value'].split('undefined:/')[1]
                    if not os.path.exists( fileName ):
                        raise Exception("the following image file is missing: %s " % fileName)

                    file = QFile(fileName)
                    if not file.open(QIODevice.ReadOnly):
                        raise Exception("error opening image file %s" % fileName )
                    else:
                        imageData= file.readAll()
                        pr['value'] = "undefined:/%s" % base64.b64encode(imageData)
                elif pr['value'].startswith('local-tests:/'):
                    fileName = pr['value'].split('local-tests:/')[1]

                    if not os.path.exists( fileName ):
                        raise Exception("the following image file is missing: %s " % fileName)
                    
                    file = QFile(fileName)
                    if not file.open(QIODevice.ReadOnly):
                        raise Exception("error opening image file %s" % fileName )
                    else:
                        imageData= file.readAll()
                        pr['value'] = "local-tests:/%s" % base64.b64encode(imageData)
                else:
                    pass

    def __loadDataset(self, parameters):
        """
        Private function
        Load dataset

        @param parameters: 
        @type parameters:
        """
        # self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
        for pr in parameters:
            if pr['type'] == 'dataset':
                if pr['value'].startswith('undefined:/'):
                    fileName = pr['value'].split('undefined:/')[1]
                    if not os.path.exists( fileName ):
                        raise Exception("the following test data file is missing: %s " % fileName)

                    doc = FileModelTestData.DataModel()
                    res = doc.load( absPath = fileName )
                    pr['value'] = "undefined:/%s" % doc.getRaw()
                elif pr['value'].startswith('local-tests:/'):
                    fileName = pr['value'].split('local-tests:/')[1]

                    if not os.path.exists( fileName ):
                        raise Exception("the following test data file is missing: %s " % fileName)
                    
                    doc = FileModelTestData.DataModel()
                    res = doc.load( absPath = fileName )
                    pr['value'] = "local-tests:/%s" % doc.getRaw()
                else:
                    pass

    def __updateParameter(self, currentParam, newParam):
        """
        Private function
        Update current test suite parameters with testplan parameter

        @param currentParam: 
        @type currentParam:

        @param newParam: 
        @type newParam:
        """
        for i in xrange(len(currentParam)):
            for np in newParam:
                if np['name'] == currentParam[i]['name']:
                    currentParam[i] = np
        
    def checkSyntaxDocument (self):
        """
        Gets the current document and send it the server to check the syntax
        """
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False

        currentDocument = self.tab.widget(tabId)
        
        if isinstance(currentDocument, TestAdapter.WTestAdapter):
            RCI.instance().checkSyntaxAdapter( fileContent=currentDocument.getraw_encoded() )
            
        elif isinstance(currentDocument, TestLibrary.WTestLibrary):
            RCI.instance().checkSyntaxLibrary( fileContent=currentDocument.getraw_encoded() )
            
        else:
            testId = TestResults.instance().getTestId()

            _json = self.prepareTest( wdocument = currentDocument, basicMode=True)    
            
            if currentDocument.extension in [ RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT, RCI.EXT_TESTUNIT]:
                RCI.instance().checkTestSyntax( req=_json )
            elif currentDocument.extension in [ RCI.EXT_TESTPLAN, RCI.EXT_TESTGLOBAL]:
                RCI.instance().checkTestSyntaxTpg( req=_json )
            else:
                pass
                
    def schedRunDocument (self):
        """
        Gets the current document, send to the server and schedule the launch
        """
        dSched = SchedDialog.SchedDialog( self )
        if dSched.exec_() == QDialog.Accepted:
            runAt, runType, runNb, withoutProbes, runEnabled, keepTr, withoutNotifs, runFrom, runTo = dSched.getSchedtime()
            recursive = False
            if runType > UCI.SCHED_IN:
                recursive = True
            self.runDocument( background = True, runAt = runAt, runType=runType, runNb=runNb, 
                                withoutProbes=withoutProbes, keepTr=not keepTr, 
                               withoutNotif=withoutNotifs, fromTime=runFrom, toTime=runTo)
        
    def runDocumentNoKeepTr(self):
        """
        Run document without keep testresult
        """
        self.runDocument(keepTr=False)

    def runDocumentWithoutNotif(self):
        """
        Run document without notification
        """
        self.runDocument(withoutNotif=True)

    def runDocumentWithoutProbes(self):
        """
        Run document without probes
        """
        self.runDocument(withoutProbes=True)

    def runDocumentStepByStep(self):
        """
        Run document step by step
        """
        self.runDocument(stepByStep = True)

    def runDocumentBreakpoint(self):
        """
        Run document step by step
        """
        self.runDocument(breakpoint = True)
        
    def runDocumentInBackground (self):
        """
        Run document in background
        """
        self.runDocument(background = True)

    def runDocumentDebug(self):
        """
        Run document in debug mode
        """
        self.runDocument(debugActivated=True)

    def runDocumentMinimize(self):
        """
        Run document in minimize mode
        """
        # run as usual
        self.runDocument(hideApplication=True)

    def runDocumentReduce(self):
        """
        Run document in reduce mode
        """
        # run as usual
        self.runDocument(reduceApplication=True)

    def getCurrentDocument(self):
        """
        Return the current document
        """
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return None
        
        currentDocument = self.tab.widget(tabId)
        return currentDocument

    def runDocument (self, background = False, runAt = (0,0,0,0,0,0) , 
                     runType=None, runNb=-1, withoutProbes=False, debugActivated=False, 
                     withoutNotif=False, keepTr=True, fromTime=(0,0,0,0,0,0), 
                     toTime=(0,0,0,0,0,0), hideApplication=False,
                     reduceApplication=False, stepByStep=False, breakpoint=False):
        """
        Run document
    
        @param runAt:  ( year, month, day, hour, minute, sec )
        @type runAt: tuple of integer
    
        @param runType:  0=sched_at, 1 = sched_in
        @type runType: integer

        @return:
        @rtype: boolean
        """

        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False

        # auto save ?
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-save' ) ):
            self.saveTab(tabId = tabId)

        if QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/minimize-app' ) ) or hideApplication:
            # the first parent is the workspace
            # the second parent is the main app
            self.parent.parent.minimizeWindow()

        if QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/reduce-app' ) ) or reduceApplication:
            # the first parent is the workspace
            # the second parent is the main app
            self.parent.parent.showMinimized()

        if runType is None:
            schedType = UCI.SCHED_NOW
        else:
            schedType = runType

        currentDocument = self.tab.widget(tabId)
        testId = TestResults.instance().getTestId()

        _json = self.prepareTest (  wdocument=currentDocument, 
                                    tabId=testId, 
                                    background = background, 
                                    runAt = runAt, 
                                    runType=schedType, 
                                    runNb=runNb, 
                                    withoutProbes=withoutProbes, 
                                    debugActivated=debugActivated, 
                                    withoutNotif=withoutNotif, 
                                    keepTr=keepTr, 
                                    prjId=currentDocument.project, 
                                    fromTime=fromTime, 
                                    toTime=toTime, 
                                    stepByStep=stepByStep, 
                                    breakpoint=breakpoint  )

        if currentDocument.extension in [ RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT, RCI.EXT_TESTUNIT]:
            RCI.instance().scheduleTest(req=_json, wdocument=currentDocument)
        elif currentDocument.extension in [ RCI.EXT_TESTPLAN, RCI.EXT_TESTGLOBAL]:
            RCI.instance().scheduleTestTpg(req=_json, wdocument=currentDocument)
        else:
            pass
            
    def checkAlreadyOpened (self, path, remoteFile=False, repoType=None, project=0):
        """
        Returns tab id if the document is already opened

        @param path:  
        @type path: string

        @return: TabId
        @rtype: None or Integer
        """
        # convert to int
        project = int(project)
        
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            # bypass the welcome page
            if isinstance(doc, WelcomePage):
                continue
            # end of bypass
            
            if project:
                if not remoteFile:
                    if doc.isRemote == remoteFile and doc.getPath() == path \
                        and doc.repoDest==repoType:
                        return tabId
                else:
                    if doc.isRemote == remoteFile and doc.getPath() == path \
                        and doc.repoDest==repoType and doc.project==project:
                        return tabId
            else:
                if doc.isRemote == remoteFile and doc.getPath() == path \
                    and doc.repoDest==repoType :
                    return tabId
        return None

    def disableTabs(self):
        """
        Disable tabs
        """
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            if not isinstance(doc, WelcomePage):
                self.tab.setTabEnabled(tabId,False)
            
    def enableTabs(self):
        """
        Enable tabs
        """
        for tabId in xrange( self.tab.count() ):
            self.tab.setTabEnabled(tabId,True)
            
    def supportProperties(self, tabId=0):
        """
        Return True if the tabID passed as argument support test properties
        """
        supportProperties = False
        doc = self.tab.widget(tabId)
        if not isinstance(doc, WelcomePage):
            if doc.extension in [ TestAbstract.TYPE, TestUnit.TYPE, TestData.TYPE, 
                                    TestSuite.TYPE, TestPlan.TYPE, TestPlan.TYPE_GLOBAL ]:
                supportProperties = True
        return supportProperties
    
    def setCurrentTabWelcome(self):
        """
        Set the welcome tab as current
        """
        doc = self.tab.widget(0)
        if isinstance(doc, WelcomePage):
            self.tab.setCurrentIndex(0)
        
    def isEmpty (self):
        """
        Returns True if document viewer is empty, False in other cases

        @return: True if empty
        @rtype: boolean
        """
        if  self.tab.count() > 0:
            return False
        return True

    def setCurrentActions(self):
        """
        New in 3.1.0, function called only on server connection
        Set current actions
        """
        tabId = self.tab.currentIndex()
        if tabId == -1:
            return False
        currentDocument = self.tab.widget(tabId)
        self.updateActions( currentDocument )

    def enableWorkspace(self):
        """
        Enable the workspace and all tabulations
        """
        # enable tabs
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            doc.setEnabled(True)
            
        # enable findwidget if needed ?
        currentTab = self.tab.currentIndex()
        currentDoc = self.tab.widget(currentTab)
        if currentDoc is not None:
            if not isinstance(currentDoc, WelcomePage):
                if currentDoc.extension in [ TestUnit.TYPE, TestData.TYPE, TestSuite.TYPE,
                                            TestAdapter.TYPE, TestLibrary.TYPE, TestTxt.TYPE ]:
                    self.findWidget.setEnabled(True)

    def disableWorkspace(self):
        """
        Disable the workspace except the welcome page
        """
        # disable tabs
        for tabId in xrange( self.tab.count() ):
            doc = self.tab.widget(tabId)
            if isinstance(doc, WelcomePage):
                continue
            doc.setEnabled(False)
            
        # disable findwidget if needed ?
        currentTab = self.tab.currentIndex()
        currentDoc = self.tab.widget(currentTab)
        if currentDoc is not None:
            if not isinstance(currentDoc, WelcomePage):
                if currentDoc.extension in [ TestUnit.TYPE, TestData.TYPE, TestSuite.TYPE,
                                        TestAdapter.TYPE, TestLibrary.TYPE, TestTxt.TYPE ]:
                    self.findWidget.setEnabled(False)
            
WD = None # Singleton
def instance ():
    """
    Returns Singleton

    @return: Return singleton of the class WDocumentViewer
    @rtype: WDocumentViewer
    """
    return WD

def initialize (parent, iRepo, lRepo, rRepo):
    """
    Initialize WDocumentViewer widget
    """
    global WD
    WD = WDocumentViewer(parent, iRepo, lRepo, rRepo)

def finalize ():
    """
    Destroy Singleton
    """
    global WD
    if WD:
        WD = None