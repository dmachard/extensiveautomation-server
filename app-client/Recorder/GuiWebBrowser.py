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
Browser assistant module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QWidget, QKeySequence, QPixmap, QDialog, QApplication, QCursor, 
                            QIcon, QToolBar, QGroupBox, QLineEdit, QDoubleValidator, QComboBox, 
                            QGridLayout, QLabel, QFrame, QVBoxLayout, QIntValidator, QHBoxLayout, 
                            QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                            QCheckBox, QSplitter, QMessageBox, QDesktopWidget)
    from PyQt4.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal, QT_VERSION_STR)
    from PyQt4.QtWebKit import (QWebView, QWebInspector, QWebSettings, QWebPage)
    from PyQt4.QtNetwork import (QNetworkProxy)
except ImportError:
    from PyQt5.QtGui import (QKeySequence, QPixmap, QCursor, QIcon, QDoubleValidator, QIntValidator)
    from PyQt5.QtWidgets import (QWidget, QDialog, QApplication, QToolBar, QGroupBox, QLineEdit, 
                                QComboBox, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                                QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                                QCheckBox, QSplitter, QMessageBox, QDesktopWidget)
    from PyQt5.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal, QT_VERSION_STR)
    from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
    from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
    from PyQt5.QtWebEngineWidgets import QWebEnginePage as QWebPage
    from PyQt5.QtNetwork import (QNetworkProxy)
        
from Libs import QtHelper, Logger
import Settings

class WBrowserWeb(QWidget, Logger.ClassLogger):
    """
    Browser web widget
    """
    TagsHtml = pyqtSignal(dict, dict, dict, dict ,dict, dict)  
    def __init__(self, parent):
        """
        Constructor
        """
        QWidget.__init__(self)
        
        self.createActions()
        self.createWidgets()
        self.createToolbar()
        self.createConnections()
        self.center()

    def createToolbar(self):
        """
        Create toolbar
        """
        self.dockToolbarWebBrowser.setObjectName("Toolbar for web browser")
        self.dockToolbarWebBrowser.addAction(self.loadWebPageAction)
        self.dockToolbarWebBrowser.addAction(self.webView.pageAction(QWebPage.Back))
        self.dockToolbarWebBrowser.addAction(self.webView.pageAction(QWebPage.Forward))
        self.dockToolbarWebBrowser.addAction(self.webView.pageAction(QWebPage.Reload))
        self.dockToolbarWebBrowser.addAction(self.webView.pageAction(QWebPage.Stop))
        self.dockToolbarWebBrowser.setIconSize(QSize(16, 16))
        self.dockToolbarWebBrowser.addSeparator()
        
    def createWidgets(self):
        """
        Create all qt widgets
        """
        self.setWindowTitle( self.tr("Extensive Testing Client - Web Browser") )
        self.setWindowIcon( QIcon(":/main.png") )
        
        self.dockToolbarWebBrowser = QToolBar(self)
        self.dockToolbarWebBrowser.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        browserLayoutGroup = QVBoxLayout()
        browserLayoutGroup.addWidget(self.dockToolbarWebBrowser)
        
        toolbarBrowserLayoutGroup = QHBoxLayout()

        self.locationEdit = QLineEdit(self)
        self.locationEdit.setSizePolicy(QSizePolicy.Expanding, self.locationEdit.sizePolicy().verticalPolicy())

        self.webCounter = QLabel("(0%)") 
         
        toolbarBrowserLayoutGroup.addWidget( QLabel("Load URL:") )
        toolbarBrowserLayoutGroup.addWidget( self.webCounter )
        toolbarBrowserLayoutGroup.addWidget( self.locationEdit )
               
        self.webTitle = QLabel("Title:") 
        
        self.webView  = QWebView()
        
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/proxy-web-active') ):

            proxy = QNetworkProxy()
            proxy.setType(3); # http
            proxy.setHostName( Settings.instance().readValue( key = 'Server/addr-proxy-http' ) )
            proxy.setPort( int( Settings.instance().readValue( key = 'Server/port-proxy-http' ) ) )   
            self.webView.page().networkAccessManager().setProxy(proxy)
        
        if QT_VERSION_STR.startswith("4."):
            self.webInspector = QWebInspector()
            self.webView.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled,True)
            self.webInspector.setPage(self.webView.page())
        
        self.webView.setHtml('<html><head></head><body>No content loaded</body></html>')
        self.webView.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)

        browserLayoutGroup.addLayout(toolbarBrowserLayoutGroup)
        browserLayoutGroup.addWidget( self.webTitle)
        
        self.webTab = QTabWidget()
        self.webTab.addTab( self.webView, "Web Page")
        if QT_VERSION_STR.startswith("4."):
            self.webTab.addTab( self.webInspector, "Source Inspector")
        
        browserLayoutGroup.addWidget(self.webTab)

        self.setLayout(browserLayoutGroup)
        
    def createConnections(self):
        """
        Create toolbar
        """
        self.locationEdit.returnPressed.connect(self.onChangeWebLocation)
        self.webView.loadProgress.connect(self.onWebProgress)
        self.webView.loadFinished.connect(self.onFinishLoading)

    def createActions (self):
        """
        Create qt actions
        """
        self.loadWebPageAction = QtHelper.createAction(self, "&Go to...", self.onChangeWebLocation, 
                                            icon=QIcon(":/act-half-refresh.png"), tip = 'Load Webpage')

    def stop(self):
        """
        Stop the web view
        """
        self.webView.stop()

    def onChangeWebLocation(self):
        """
        On change web location
        """
        self.webCounter.setText( "(1%)" )
        url = QUrl.fromUserInput(self.locationEdit.text())
        self.webView.load(url)
        self.webView.setFocus()

    def onWebProgress(self, p):
        """
        On web progress
        """
        self.webCounter.setText( "(%s%%)" % p )
        
    def onFinishLoading(self):
        """
        On finish loading
        """
        self.webTitle.setText( "Title: %s" % self.webView.title() )
        
        # need complete refonte with qt5
        if QT_VERSION_STR.startswith("5."):
            return
            
        frame = self.webView.page().mainFrame()
        document = frame.documentElement()
        
        elements = []
        self.examineChildElements(document, elements)
        
        tagList = {}
        idList = {}
        classList = {}
        nameList = {}
        linkList = {}
        cssList = {}

        for el in elements:
            # by tagname
            if 'tagname' in el: 
                if el['tagname'] not in tagList: tagList[el['tagname']] = ''
                
            # by id
            if 'id' in el: 
                if el['id'] not in idList: idList[el['id']] = ''
            
            # by name
            if 'name' in el: 
                if el['name'] not in nameList: nameList[el['name']] = ''
                
            # by class
            if 'class' in el: 
                if el['class'] not in classList: classList[el['class'].replace(" ", ".")] = ''
                
            # by link text
            if 'text' in el: 
                if 'tagname' in el: 
                    if sys.version_info > (3,):
                        if el['tagname'].lower() == 'a':
                            if el['text'] not in linkList: linkList[el['text']] = ''
                    else:
                        if str(el['tagname']).lower() == 'a':
                            if el['text'] not in linkList: linkList[el['text']] = ''
                                
            # by css selector
            if 'tagname' in el: 
                if sys.version_info > (3,):
                    cssSelector = "%s" % el['tagname'].lower()
                else:
                    cssSelector = "%s" % str(el['tagname']).lower()
                if 'id' in el: 
                    cssSelector += "#%s" % el['id']
                if 'class' in el: 
                    cssSelector += ".%s" % el['class'].replace(" ", ".")
                cssList[cssSelector] = ''
                
        self.TagsHtml.emit( tagList, idList, classList, nameList, linkList, cssList )

    def examineChildElements(self, parentElement, listResult):
        """
        Examine child elements
        """
        # Traverse the document.
        element = parentElement.firstChild()
        while not element.isNull():
            el = {}
            if element.attribute("id"): el['id'] = element.attribute("id")
            if element.attribute("name"): el['name'] = element.attribute("name")
            if element.attribute("class"): el['class'] = element.attribute("class")
            if element.tagName(): el['tagname'] = element.tagName()
            if element.toPlainText(): el['text'] = element.toPlainText()
            
            listResult.append( el )
            self.examineChildElements(element, listResult)
            element = element.nextSibling()
    
    def center(self):
        """
        Center the dialog
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
   