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
Plugin archives
"""
from __future__ import print_function

import sys
import codecs

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QTreeWidgetItem, QIcon, QFont, QBrush, QTreeWidget, QColor,
                            QTreeView, QWidget, QToolBar, QVBoxLayout, QPrinter, QPrintDialog, 
                            QDialog, QFileDialog, QLabel, QPalette, QSizePolicy, QScrollArea, 
                            QPixmap, QImage, QTextEdit, QMessageBox, QHBoxLayout, QTabWidget, 
                            QStyle, QComboBox, QSplitter, QFrame, QMenu, QApplication,
                            QGroupBox, QCheckBox, QTextDocument)
    from PyQt4.QtCore import (Qt, QSize, QFile, QIODevice, QTextStream, QByteArray)
    from PyQt4.QtWebKit import (QWebView, QWebSettings)
    from PyQt4.QtNetwork import (QNetworkProxy)
except ImportError:
    from PyQt5.QtGui import (QIcon, QFont, QBrush, QColor, QPalette, QPixmap, QImage, QTextDocument)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QTreeWidget, QTreeView, QWidget, QToolBar,
                                QVBoxLayout, QDialog, QFileDialog, QLabel, 
                                QSizePolicy, QScrollArea, QTextEdit, QMessageBox, QHBoxLayout, 
                                QTabWidget, QStyle, QComboBox, QSplitter, QFrame, QMenu, QApplication,
                                QGroupBox, QCheckBox)
    from PyQt5.QtCore import (Qt, QSize, QFile, QIODevice, QTextStream, QByteArray)
    from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
    from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
    from PyQt5.QtPrintSupport import (QPrinter, QPrintDialog)
    from PyQt5.QtNetwork import (QNetworkProxy)

import RestClientInterface as RCI
import UserClientInterface as UCI
import Settings
from Libs import QtHelper, Logger
    
import base64
import time
import zlib
from operator import itemgetter

COL_NAME        =   0
COL_VERDICT     =   1
COL_RUN         =   2
COL_REPLAY      =   3
COL_TIMESTAMP   =   4
COL_USER        =   5
COL_SIZE        =   6
COL_COMMENTS    =   7

COL_BACKUP_NAME         =   0
COL_BACKUP_DATE         =   1
COL_BACKUP_SIZE         =   2

EXTENSION_TESTRESULT    = "trx"

TAB_REPORTS             = 0
TAB_BASIC_REPORTS       = 1
TAB_XML_VERDICTS        = 2
TAB_VERDICTS            = 3
TAB_IMAGES              = 4
TAB_COMMENTS            = 5

TYPE_ITEM_TEST_OTHERS       = 3
TYPE_ITEM_TEST_RESULT       = 2
TYPE_ITEM_FOLDER_TEST       = 1
TYPE_ITEM_FOLDER_DATE       = 0
 
class ArchiveItem(QTreeWidgetItem, Logger.ClassLogger):
    """
    Treewidget item for archive
    """
    def __init__(self, archiveDescr, icon = None, parent = None, itemType = QTreeWidgetItem.UserType+0, 
                 colored=False, childTest=None):
        """
        Constructs ArchiveItem widget item

        @param archiveDescr: 
        @type archiveDescr: dict

        @param icon: 
        @type icon:

        @param parent: 
        @type parent:

        @param type: 
        @type type:

        @param colored: 
        @type colored:
        """
        QTreeWidgetItem.__init__(self, parent, itemType)
        self.parent = parent
        self.typeItem = None
        self.archiveDescr = archiveDescr
        self.childTest = childTest # new in 12.2

        if icon is not None:
            self.setIcon(COL_NAME, icon )
        
        # root
        if itemType == QTreeWidgetItem.UserType+10: 
            # wrap to str for py3 support
            self.setText(COL_NAME, str(archiveDescr) ) 
            self.setToolTip(COL_NAME, str(archiveDescr) )

        # files
        if itemType == QTreeWidgetItem.UserType+3:
            self.setText(COL_SIZE, QtHelper.bytes2human( int(archiveDescr['size']) ) ) 
            if archiveDescr["name"].endswith('cap'): # network trace
                self.setIcon(COL_NAME, QIcon(":/binary.png") )
            elif archiveDescr["name"].endswith('txt'): # text file
                self.setIcon(COL_NAME, QIcon(":/file-txt.png") )
            elif archiveDescr["name"].endswith('png'): # image file
                self.setIcon(COL_NAME, QIcon(":/png.png") )
            elif archiveDescr["name"].endswith('jpg'): # image file
                self.setIcon(COL_NAME, QIcon(":/png.png") )
            elif archiveDescr["name"].endswith('zip'): # zip file
                self.setIcon(COL_NAME, QIcon(":/file-zip.png") )
                if colored:
                    self.setIcon(COL_NAME, QIcon(":/file-zip-new.png") )
                
            else:
                self.error( "this type of file is not supported" )
                
            # wrap to str for py3 support
            self.setText(COL_NAME, str(archiveDescr["name"]) ) 
            self.setToolTip(COL_NAME, str(archiveDescr["name"]) )
            self.typeItem = TYPE_ITEM_TEST_OTHERS

            # test file
            if archiveDescr["name"].endswith('zip'): 
                self.parseNameZip(archiveDescr["name"])

        # # files
        if itemType == QTreeWidgetItem.UserType+2:
            self.setText(COL_SIZE, QtHelper.bytes2human( int(archiveDescr['size']) ) ) 
            archiveName = archiveDescr["name"]
            if archiveDescr["name"].endswith(EXTENSION_TESTRESULT): # test result
                self.parseName( archiveName=archiveDescr["name"])
                
                # new in v12.2, load report directly from folder
                self.parent.childTest = archiveDescr
                
            else:
                self.error( "this type of file is not supported" )
                # wrap to str for py3 support
                self.setText(COL_NAME, str(archiveName) )  
                self.setToolTip(COL_NAME, str(archiveName) )
            self.typeItem = TYPE_ITEM_TEST_RESULT
        
        #folders
        if itemType == QTreeWidgetItem.UserType+0:

            # folder name example: 2017-06-08_18:23:26.c1692fe3-405a-4b73-b4dc-a10638842563.Tm9uYW1lMQ==.denis.machard
            # YYYY-MM-DD_hh:mm:ss.testid.testname(base64).user
            # the username can contains dot 
            ret = archiveDescr["name"].split(".", 3)

            # new in v16, to support long file test
            if "virtual-name" in archiveDescr:
                if len(archiveDescr["virtual-name"]):
                    ret = archiveDescr["virtual-name"].split(".", 3)
            # end of new 
            
            # sub directory
            if len(ret) == 4:
                timeArch, testid, testName, testUser = ret

                self.testId = testid
                self.testName = base64.b64decode(testName)
                self.testUser = testUser
                
                # wrap to str for py3 support
                self.setText(COL_NAME, unicode(self.testName, "utf8") ) 
                self.setToolTip(COL_NAME, unicode(self.testName, "utf8") )
                
                self.setText(COL_TIMESTAMP, timeArch.replace("_", " ") )
                self.setText(COL_USER, str(testUser) )
                self.typeItem = TYPE_ITEM_FOLDER_TEST
            else:
            
                # wrap to str for py3 support
                self.setText(COL_NAME, str(archiveDescr["name"]) ) 
                self.setToolTip(COL_NAME, str(archiveDescr["name"]) )
                self.typeItem = TYPE_ITEM_FOLDER_DATE
                
        if colored:
            self.setColor()
    
    def parseNameZip(self, zipName):
        """
        Parse the name of zip file

        @param archiveName: 
        @type archiveName:
        """
        # remove extension
        leftstr, ext = zipName.rsplit(".", 1)
        # split by _
        nameleft, yearzip, datezip, replayidzip = leftstr.rsplit("_", 3) # str, year, date, replayid
        
        # date format : 12-23-22.2222
        dateStr = datezip.split('.')[0].replace("-", ":")
        self.setText(COL_NAME, "%s.zip" % nameleft )
        self.setText(COL_TIMESTAMP, "%s %s" % (yearzip, dateStr) )
        self.setText(COL_REPLAY, str(replayidzip)  )# wrap to str for py3 support

    def parseName(self, archiveName):
        """
        Parse the name of archive file

        @param archiveName: 
        @type archiveName:
        """
        self.setIcon(COL_NAME, QIcon(":/%s.png" % EXTENSION_TESTRESULT) )
        # extract replay id:  Noname1_0_UNDEFINED_0.trx  
        # [testname] [replayid] [verdict] [nbcomments]
        leftover, rightover = str(archiveName).rsplit("_", 1)
        nbComments = rightover.split(".%s" % EXTENSION_TESTRESULT)[0]
        try: # backward compatibility, verdict added on the name
            leftover2, verdict = leftover.rsplit("_", 1)
            runName, runId = leftover2.rsplit("_", 1)
        except Exception as e:
            runName, runId = leftover.rsplit("_", 1)
            verdict = 'UNDEFINED'
        archiveNameParsed = "%s.%s" % (runName, EXTENSION_TESTRESULT)
        if verdict == 'PASS':
            iconVerdict = QIcon(":/ok.png")
        if verdict == 'FAIL':
            iconVerdict = QIcon(":/ko.png")
        if verdict == 'UNDEFINED':
            iconVerdict = QIcon(":/kill.png")
        self.testName = archiveNameParsed
        self.setIcon(COL_VERDICT, iconVerdict )
        
        # new in v12.2
        self.parent.setIcon(COL_VERDICT, iconVerdict )
        # end of new
        
        # wrap to str for python3 support
        self.runId = str(runId)
        self.setText(COL_REPLAY, str(runId) ) 
        self.setText(COL_NAME, str(archiveNameParsed) )
        self.setToolTip(COL_NAME, str(archiveNameParsed) ) 

    def setNbRun(self, nb):
        """
        Set the number of run
        """
        self.setText(COL_RUN, str(nb) )

    def setNumberOfComments(self, nbComments):
        """
        Set the number of comments
        """
        if int(nbComments) > 0:
            font = QFont()
            font.setBold(True)
            self.setFont(COL_COMMENTS, font)
            self.setForeground( COL_COMMENTS, QBrush( QColor( Qt.red ) ) )
            
        # wrap to str for python3 support
        self.setText(COL_COMMENTS, str(nbComments) ) 

    def setColor(self):
        """
        Change the color of new item
        """
        for i in xrange(7):
            self.setForeground( i, QBrush( QColor( Qt.blue ) ) )
    
    def getTextValue(self):
        """
        Returns the test name
        """
        return self.testName
    
class DeselectableTreeWidget(QTreeWidget):
    """
    Deselectable treewidget
    """
    def mousePressEvent(self, event):
        """
        On mouse press
        """
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)

class PreviewReport(QWidget, Logger.ClassLogger):
    """
    Raw view widget
    """
    def __init__(self, parent, data, toCsv=False, toHtml=False, toPrinter=False, 
                 toTxt=False, toPdf=False):
        """
        Raw view widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.__data = data
        self.toCsv = toCsv
        self.toHtml = toHtml
        self.toPrinter = toPrinter
        self.toTxt = toTxt
        self.toPdf = toPdf

        self.fileName = None
        self.cacheHtml = ""
        
        self.createWidgets()
        self.createActions()
        self.createToolbars()
    
    def createWidgets (self):
        """
        Create qt widgets
        """
        self.toolbar = QToolBar(self)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbarPlugins = QToolBar(self)
        self.toolbarPlugins.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbarPlugins.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.pluginsBox = QGroupBox("Plugins")
        self.pluginsBox.setStyleSheet( """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutPlugins = QHBoxLayout()
        layoutPlugins.addWidget(self.toolbarPlugins)
        layoutPlugins.setContentsMargins(0,0,0,0)
        self.pluginsBox.setLayout(layoutPlugins)
        self.pluginsBox.setMaximumHeight(70)
        self.pluginsBox.hide()
        
        self.exportBox = QGroupBox("Exports")
        self.exportBox.setStyleSheet( """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutExports = QHBoxLayout()
        layoutExports.addWidget(self.toolbar)
        layoutExports.setContentsMargins(0,0,0,0)
        self.exportBox.setLayout(layoutExports)
        self.exportBox.setMaximumHeight(70)
        
        layout = QVBoxLayout()

        self.txtEdit = QWebView(self)
        self.txtEdit.settings().setAttribute(QWebSettings.JavascriptEnabled, True)

        if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/proxy-web-active') ):
        
            proxy = QNetworkProxy()
            proxy.setType(3); # http
            proxy.setHostName( Settings.instance().readValue( key = 'Server/addr-proxy-http' ) )
            proxy.setPort( int( Settings.instance().readValue( key = 'Server/port-proxy-http' ) ) )   
            self.txtEdit.page().networkAccessManager().setProxy(proxy)

        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.exportBox)
        layoutToolbars.addWidget(self.pluginsBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        layout.addLayout(layoutToolbars)
        layout.addWidget(self.txtEdit)

        self.setLayout(layout)

    def createToolbars(self):
        """
        Toolbar creation
        """
        self.toolbar.setObjectName("Export toolbar")
        if self.toTxt: self.toolbar.addAction(self.saveTxtAction)
        if self.toHtml: self.toolbar.addAction(self.saveHtmlAction)
        if self.toPdf: self.toolbar.addAction(self.savePdfAction)
        if self.toPrinter: self.toolbar.addAction(self.toPrinterAction)
        self.toolbar.setIconSize(QSize(16, 16))

    def registerPlugin(self, pluginAction):
        """
        Called to register a plugin
        """
        self.toolbarPlugins.addAction(pluginAction)
        self.toolbarPlugins.setIconSize(QSize(16, 16))
        self.pluginsBox.show()
        
    def createActions (self):
        """
        Qt Actions
        """     
        self.saveTxtAction = QtHelper.createAction(self, "&To TXT", self.saveTxt, 
                                tip = 'Save to TXT file', icon = QIcon(":/file-txt.png") )
        self.saveHtmlAction = QtHelper.createAction(self, "&To HTML", self.saveHtml, 
                                tip = 'Save to HTML file', icon = QIcon(":/web.png") )
        self.savePdfAction = QtHelper.createAction(self, "&To PDF", self.savePdf, 
                                tip = 'Save to PDF file', icon = QIcon(":/to_pdf.png") )
        self.toPrinterAction = QtHelper.createAction(self, "&To Printer", self.savePrinter, 
                                tip = 'Print', icon = QIcon(":/printer.png") )

    def savePrinter(self):
        """
        Save to printer
        """
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("Print")

        if dialog.exec_() != QDialog.Accepted:
            return

        if QtHelper.IS_QT5: # new in v18
            self.fileName = printer
            self.txtEdit.page().toHtml(self.__toPrinter)
        else:
            self.txtEdit.print_(printer)

    def __toPrinter(self, html):
        """
        New in v18
        Callback from QWebpage
        """
        textEdit = QTextEdit(self)
        textEdit.setHtml(html)
        textEdit.print(self.fileName)
        textEdit.deleteLater()
        
        self.fileName = None

        # notify user
        self.parent.app().showMessageTray("Report printing...")
            
    def saveTxt(self):
        """
        Save to txt file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save TXT file", "", 
                                               "TXT file (*.txt);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new
        
        if _filename:

            if QtHelper.IS_QT5: # new in v18
                self.fileName = _filename
                self.txtEdit.page().toPlainText(self.__toPlainText)
            else:
                frame = self.txtEdit.page().mainFrame()
                txtReport = frame.toPlainText()

                try:
                    with codecs.open(_filename, "w", "utf-8") as f:
                        f.write( txtReport )
                except Exception as e:
                    self.error('unable to save report file as txt: %s' % str(e) )

    def __toPlainText(self, text):
        """
        New in v18
        Callback from QWebpage
        """
        if self.fileName is None:
            return
            
        try:
            with codecs.open(self.fileName, "w", "utf-8") as f:
                f.write( text )
        except Exception as e:
            self.error('unable to save report file as txt: %s' % str(e) )
        else:
            # notify user
            self.parent.app().showMessageTray("Plain text report saved!")
        
        self.fileName = None
        
    def saveHtml(self):
        """
        Save to html file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save HTML file", "", 
                                                "HTML file (*.html);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new
        
        if _filename:
            if QtHelper.IS_QT5: # new in v18
                self.fileName = _filename
                self.txtEdit.page().toHtml(self.__toHtml)
            else:
                frame = self.txtEdit.page().mainFrame()
                htmlReport = frame.toHtml()

                try:
                    with codecs.open(_filename, "w", "utf-8") as f:
                        f.write( htmlReport  )
                except Exception as e:
                    self.error('unable to save report file as html: %s' % str(e) )

    def __toHtml(self, html):
        """
        New in v18
        Callback from QWebpage
        """
        if self.fileName is None:
            return
            
        try:
            with codecs.open(self.fileName, "w", "utf-8") as f:
                f.write( html  )
        except Exception as e:
            self.error('unable to save report file as html: %s' % str(e) )
        else:
            # notify user
            self.parent.app().showMessageTray("HTML report saved!")
            
        self.fileName = None
        
    def savePdf(self):
        """
        Save to pdf file
        """
        fileName = QFileDialog.getSaveFileName(self, 'Save to PDF', "", 
                                                "PDF file (*.pdf);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new 
            
        if _filename:
        
            if QtHelper.IS_QT5: # new in v18
                self.fileName = _filename
                self.txtEdit.page().printToPdf(self.__toPdf)            
            else:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setPageSize(QPrinter.A4)
                printer.setColorMode(QPrinter.Color)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(_filename)

                self.txtEdit.print_(printer)
    
    def __toPdf(self, pdf):
        """
        New in v18
        Callback from QWebpage
        """
        if self.fileName is None:
            return
            
        try:
            with codecs.open(self.fileName, "wb") as f:
                f.write( pdf  )
        except Exception as e:
            self.error('unable to save report file as pdf: %s' % str(e) )
        else:   
            # notify user
            self.parent.app().showMessageTray("PDF report saved!")
            
        self.fileName = None
        
    def loadReports(self, content):
        """
        Load the report
        """
        # convert to qbyte array to support qt5
        tmp_ = QByteArray()
        tmp_.append(content)
        
        self.cacheHtml = content
        self.txtEdit.setContent( tmp_, "text/html; charset=utf-8") 

    def deactive(self):
        """
        Deactive the widget
        """
        self.txtEdit.setHtml( "" )
        
class PreviewImages(QWidget):
    """
    Image view
    """
    def __init__(self, parent):
        """
        The image view
        """
        QWidget.__init__(self, parent)
        self.scaleFactor = 0.0
        self.createWidgets()
        self.createActions()
        self.createToolbar()

    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|------|||
        || Open | Save |||
        ||------|------|||
        """
        self.dockToolbar.setObjectName("Test Config toolbar")
        self.dockToolbar.addAction(self.zoomInAct)
        self.dockToolbar.addAction(self.zoomOutAct)
        self.dockToolbar.addAction(self.normalSizeAct)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.saveImageAct)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

    def createActions(self):
        """
        Create qc actions
        """
        self.zoomInAct = QtHelper.createAction(self, "&Zoom &In (25%.", self.zoomIn, 
                                                icon=QIcon(":/zoom-in.png") ) 
        self.zoomOutAct = QtHelper.createAction(self, "Zoom &Out (25%.", self.zoomOut, 
                                                icon=QIcon(":/zoom-out.png") ) 
        self.normalSizeAct = QtHelper.createAction(self, "&Normal Size", self.normalSize, 
                                                    icon=QIcon(":/zoom-normal.png") ) 
        self.saveImageAct = QtHelper.createAction(self, "&Save", self.saveImage, 
                                                    icon=QIcon(":/filesave.png") ) 

    def createWidgets(self):
        """
        Create qt widgets
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.imageLabel = QLabel(self)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

        layout = QVBoxLayout()
        layout.addWidget(self.dockToolbar)
        layout.addWidget(self.scrollArea)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    
    def saveImage(self):
        """
        Save image
        """
        if QtHelper.IS_QT5:
            graphPixmap = self.imageLabel.grab()
        else:
            graphPixmap = QPixmap.grabWidget(self.imageLabel)
        format = 'jpg'
        fileName = QFileDialog.getSaveFileName(self, self.tr("Save As"), "", 
                                               "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if _fileName:
            graphPixmap.save(_fileName, format)

    def resetView(self):
        """
        Reset the view
        """
        self.imageLabel.setText('')
        self.imageLabel.hide()

    def setEnabled(self, state):
        """
        Set enabled
        """
        self.scrollArea.setEnabled(state)
        self.dockToolbar.setEnabled(state)

    def setImage(self, content):
        """
        Set the image
        """
        image = QImage()
        ret = image.loadFromData(content)
        if image.isNull():
            self.imageLabel.setText('unable to load image')
            self.setEnabled(False)
            self.imageLabel.show()
            self.imageLabel.adjustSize()
        else:
            self.setEnabled(True)
            self.imageLabel.setText('')
            self.imageLabel.show()
            self.imageLabel.setPixmap(QPixmap.fromImage(QImage(image)))
            self.scaleFactor = 1.0
            self.imageLabel.adjustSize()

    def zoomIn(self):
        """
        Zoom in
        """
        self.scaleImage(1.25)

    def zoomOut(self):
        """
        Zoom out
        """
        self.scaleImage(0.8)

    def normalSize(self):
        """
        Normal size
        """
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def adjustScrollBar(self, scrollBar, factor):
        """
        Adjust the scrollbar
        """
        scrollBar.setValue(int(factor * scrollBar.value()  + ((factor - 1) * scrollBar.pageStep()/2)))

    def scaleImage(self, factor):
        """
        Scale the image
        """
        self.scaleFactor *= factor
        if self.imageLabel.pixmap() is not None:
            self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
    
    def onGetImagePreview(self, content):
        """
        Called on image preview received
        """
        self.resetView()
        self.setImage(content=base64.b64decode(content))
        self.scaleImage(1.0)
        
class PreviewComments(QWidget):
    """
    Preview comments widget
    """
    def __init__(self, parent):
        """
        Constructor
        """
        QWidget.__init__(self, parent)
        self.itemCurrent = None
        self.createActions()
        self.createWidgets()
        self.createToolbar()
        self.createConnections()
    
    def createConnections (self):
        """
        Widgets connections
        """
        self.commentTextarea.textChanged.connect(self.onTextChanged)

    def createActions (self):
        """
        Actions defined:
        """
        # comments actions
        self.addCommentAction = QtHelper.createAction(self, "&Add", self.addComment, 
                                            tip = 'Add comment', icon = QIcon(":/add_post.png") )
        self.clearAction = QtHelper.createAction(self, "&Clear", self.clearText, 
                                            tip = 'Clear fields', icon = QIcon(":/clear.png") )
        self.delCommentsAction = QtHelper.createAction(self, "&Delete all", self.delComments, 
                                            tip = 'Delete all comments', icon = QIcon(":/del-posts.png") )

    def createWidgets(self):
        """
        Create the widgets
        """
        self.dockToolbarComments = QToolBar(self)
        self.dockToolbarComments.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.commentTextarea = QTextEdit()
        self.commentTextarea.setEnabled(False)
        self.commentTextarea.setFixedHeight(150)
        self.commentsTextarea = QTextEdit()
        self.commentsTextarea.setReadOnly(True)
        self.commentsTextarea.setStyleSheet ( """background-color: #EAEAEA; """ )
        
        layoutAddComment = QVBoxLayout()
        layoutAddComment.addWidget(self.dockToolbarComments) 
        layoutAddComment.addWidget(self.commentTextarea) 
        layoutAddComment.addWidget(self.commentsTextarea) 
        self.setLayout(layoutAddComment)

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-------||
        || Empty ||
        ||-------||
        """
        self.dockToolbarComments.setObjectName("Archives comments toolbar")
        self.dockToolbarComments.addAction(self.addCommentAction)  
        self.dockToolbarComments.addSeparator()        
        self.dockToolbarComments.addAction(self.delCommentsAction)
        self.dockToolbarComments.addAction(self.clearAction)
        self.dockToolbarComments.addSeparator()
        self.dockToolbarComments.setIconSize(QSize(16, 16))
    
    def active(self, item):
        """
        Active comment textarea and actions
        """
        self.itemCurrent = item
        self.commentTextarea.setEnabled(True)
        self.commentTextarea.setText('')
        self.commentsTextarea.setText('')

    def deactive(self):
        """
        Deactive comment textarea and actions
        """
        self.commentTextarea.setEnabled(False)
        self.commentTextarea.setText('')
        self.commentsTextarea.setText('')
        self.addCommentAction.setEnabled(False)

    def clearText(self):
        """
        Clear the comment text area
        """
        self.commentTextarea.setText('')

    def addComment(self):
        """
        Add comment to the selected test result
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # prepare vars
        cur = self.itemCurrent

        if cur.typeItem != TYPE_ITEM_TEST_RESULT:
            return
            
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        logFileName =  cur.archiveDescr['name']
        projectId =  cur.archiveDescr['project']
        filePath = '%s/%s/%s/%s' % (projectId, logDirName,logSubDirName, logFileName )
        postComment = self.commentTextarea.toPlainText()
        if sys.version_info > (3,): # python 3 support
            postComment_encoded = base64.b64encode( bytes(postComment, 'utf8') )
            postComment_encoded = str(postComment_encoded, 'utf8')
        else:
            postComment_encoded = base64.b64encode( postComment.toUtf8() )
        
        # call web services
        UCI.instance().addCommentArchive(   archiveFile = filePath, 
                                            archivePost = postComment_encoded, 
                                            postTimestamp=time.time() )
    
    def readComments(self):
        """
        Read comments from the selected test result
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # prepare vars
        cur = self.itemCurrent
        
        if cur.typeItem != TYPE_ITEM_TEST_RESULT:
            return
            
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        logFileName =  cur.archiveDescr['name']
        projectId =  cur.archiveDescr['project']
        filePath = '%s/%s/%s/%s' % ( projectId, logDirName, logSubDirName, logFileName )
        
        # call web services
        UCI.instance().readCommentsArchive( archiveFile = filePath )

    def delComments(self):
        """
        Delete comments on the selected test result
        """
        reply = QMessageBox.question(self, "Delete comments", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            # prepare vars
            cur = self.itemCurrent
            
            if cur.typeItem != TYPE_ITEM_TEST_RESULT:
                return
                
            logDirName = cur.parent.parent.archiveDescr['name']
            logSubDirName = cur.parent.archiveDescr['name']
            logFileName =  cur.archiveDescr['name']
            projectId =  cur.archiveDescr['project']
            filePath = '%s/%s/%s/%s' % ( projectId, logDirName, logSubDirName, logFileName )
            
            # call web services
            UCI.instance().delCommentsArchive( archiveFile = filePath )

    def parseComments(self, comments):
        """
        Parse comments 

        @param comments: 
        @type comments:
        """
        commentsParsed = []
        for archive_comment in comments:
            dt = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( float(archive_comment['datetime'])) )  \
                                    + ".%3.3d" % int(( float(archive_comment['datetime']) * 1000) % 1000 )
            post_decoded = base64.b64decode(archive_comment['post'])
            post_decoded = post_decoded.decode('utf8').replace('\n', '<br />')
            commentsParsed.append( 'By <b>%s</b>, %s<p style="margin-left:20px">%s</p>' % (archive_comment['author'], 
                                                                                           dt, 
                                                                                           post_decoded) )
        commentsParsed.reverse()
        self.commentsTextarea.setHtml( "<br />".join(commentsParsed)   )

    def onDeleteComments(self, archivePath):
        """
        On comments deleted

        @param archivePath: 2012-05-23/15:00:00.001772.Tm9uYW1lMQ==.tester/Noname1_0_7.trx
        @type archivePath: string

        @param archiveComments: 
        @type archiveComments:
        """
        self.commentsTextarea.setHtml('')
        archPath, righover = str(archivePath).rsplit('/', 1)
        archiveName = righover.rsplit('_',1)[0]
        newArchiveName = "%s_0.trx" % archiveName
        newArchivePath = '%s/%s' % (archPath, newArchiveName)
        
        self.onCommentAdded(oldArchivePath=archivePath, newArchivePath=newArchivePath, 
                            archiveComments=[], displayPosts=False)

    def onLoadComments(self, archivePath, archiveComments):
        """
        On comments loaded

        @param archivePath: 2012-05-23/15:00:00.001772.Tm9uYW1lMQ==.tester/Noname1_0_7.trx
        @type archivePath: string

        @param archiveComments: 
        @type archiveComments:
        """
        self.parseComments( comments=archiveComments )
    
    def onCommentAdded(self, oldArchivePath, newArchivePath, archiveComments, displayPosts):
        """
        On comment added

        @param oldArchivePath: 
        @type oldArchivePath:

        @param newArchivePath: 2012-05-23/15:00:00.001772.Tm9uYW1lMQ==.tester/Noname1_0_7.trx
        @type newArchivePath: string

        @param archiveComments: 
        @type archiveComments:

        @param displayPosts: 
        @type displayPosts:
        """
        # display all comments
        if displayPosts: self.parseComments( comments=archiveComments )

        # clean field
        self.addCommentAction.setEnabled(False)
        self.commentTextarea.setText('')

    def onTextChanged(self):
        """
        On text changed on the comment text area
        """
        archivePost = self.commentTextarea.toPlainText()
        if len(archivePost):
            self.addCommentAction.setEnabled(True)
            self.clearAction.setEnabled(True)
        else:
            self.addCommentAction.setEnabled(False)
            self.clearAction.setEnabled(False)

class PreviewVerdict(QWidget, Logger.ClassLogger):
    """
    Raw view widget
    """
    def __init__(self, parent, data, toCsv=False, toXml=False,
                    toPrinter=False, toTxt=False, toPdf=False):
        """
        Raw view widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.__data = data

        self.toXml = toXml
        self.toCsv = toCsv
        self.toPrinter = toPrinter
        self.toTxt = toTxt
        self.toPdf = toPdf

        self.createActions()
        self.createWidgets()
        self.createToolbars()
        self.createConnections()

    def createWidgets (self):
        """
        Create qt widgets
        """
        self.toolbar = QToolBar(self)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbarPlugins = QToolBar(self)
        self.toolbarPlugins.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbarPlugins.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.pluginsBox = QGroupBox("Plugins")
        self.pluginsBox.setStyleSheet( """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutPlugins = QHBoxLayout()
        layoutPlugins.addWidget(self.toolbarPlugins)
        layoutPlugins.setContentsMargins(0,0,0,0)
        self.pluginsBox.setLayout(layoutPlugins)
        self.pluginsBox.hide()
        
        self.exportBox = QGroupBox("Exports")
        self.exportBox.setStyleSheet( """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutExports = QHBoxLayout()
        layoutExports.addWidget(self.toolbar)
        layoutExports.setContentsMargins(0,0,0,0)
        self.exportBox.setLayout(layoutExports)
        
        layout = QVBoxLayout()

        fontName = Settings.instance().readValue( key = 'TestArchives/verdict-font' )
        fontSize = Settings.instance().readValue( key = 'TestArchives/verdict-font-size' )
        
        if self.toXml:
            self.txtEdit = QtHelper.RawXmlEditor(parent=self)
            self.txtEdit.setText( self.__data )
            self.txtEdit.setUtf8(True)
            self.txtEdit.setFont( QFont( "%s" % fontName, int(fontSize)) )
        else:
            self.txtEdit = QtHelper.RawEditor(parent=self) 
            self.txtEdit.setTabStopWidth(10)
            self.txtEdit.setText( self.__data )
            self.txtEdit.setFont( QFont( "%s" % fontName, int(fontSize)) )
            self.txtEdit.setStyleSheet(
                "QTextEdit {"
                " selection-color: white;"
                " selection-background-color: black;"
                " color: gray" 
                "}" )

        self.txtEdit.setMinimumWidth(650)
        self.txtEdit.setMinimumHeight(400)


        self.delGroup = QGroupBox("Remove line")
        self.delGroup.setStyleSheet(   """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        self.delTG  = QCheckBox( "TESTGLOBAL" )
        self.delTP  = QCheckBox( "TESTPLAN" )
        self.delTS  = QCheckBox( "TESTSUITE" )
        self.delTU  = QCheckBox( "TESTUNIT" )
        self.delTA  = QCheckBox( "TESTABSTRACT" )
        self.delTC  = QCheckBox( "TESTCASE" )
        self.delSTP  = QCheckBox( "STEP" )
        
        layoutDel = QHBoxLayout()
        layoutDel.addWidget(self.delTG)
        layoutDel.addWidget(self.delTP)
        layoutDel.addWidget(self.delTS)
        layoutDel.addWidget(self.delTU)
        layoutDel.addWidget(self.delTA)
        layoutDel.addWidget(self.delTC)
        layoutDel.addWidget(self.delSTP)
        self.delGroup.setLayout(layoutDel)
        
        if self.toXml: self.delGroup.setEnabled(False)

        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.exportBox)
        layoutToolbars.addWidget(self.pluginsBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        layout.addLayout(layoutToolbars)
        layout.addWidget(self.delGroup)
        layout.addWidget(self.txtEdit)

        if not self.toXml:
            self.rawFind = QtHelper.RawFind(parent=self, editor=self.txtEdit, 
                                            buttonNext=True)
            layout.addWidget(self.rawFind)

        
        self.setLayout(layout)

    def createConnections(self):
        """
        Create all qt connections
        """
        self.delTG.stateChanged.connect(self.onRemoveLines)
        self.delTP.stateChanged.connect(self.onRemoveLines)
        self.delTS.stateChanged.connect(self.onRemoveLines)
        self.delTU.stateChanged.connect(self.onRemoveLines)
        self.delTA.stateChanged.connect(self.onRemoveLines)
        self.delTC.stateChanged.connect(self.onRemoveLines)
        self.delSTP.stateChanged.connect(self.onRemoveLines)
        
    def createActions (self):
        """
        Qt Actions
        """
        self.saveCsvAction = QtHelper.createAction(self, "&To CSV", self.saveCsv, 
                                tip = 'Save to CSV file', icon = QIcon(":/csv.png") )
        self.saveTxtAction = QtHelper.createAction(self, "&To TXT", self.saveTxt, 
                                tip = 'Save to TXT file', icon = QIcon(":/file-txt.png") )
        self.savePdfAction = QtHelper.createAction(self, "&To PDF", self.savePdf, 
                                tip = 'Save to PDF file', icon = QIcon(":/to_pdf.png") )
        self.toPrinterAction = QtHelper.createAction(self, "&To Printer", self.savePrinter, 
                                tip = 'Print', icon = QIcon(":/printer.png") )
        self.saveXmlAction = QtHelper.createAction(self, "&To XML", self.saveXml, 
                                tip = 'Save to XML file', icon = QIcon(":/xml.png") )
    
    def createToolbars(self):
        """
        Toolbar creation
        """
        self.toolbar.setObjectName("Export toolbar")
        if self.toXml: self.toolbar.addAction(self.saveXmlAction)
        if self.toCsv: self.toolbar.addAction(self.saveCsvAction)
        if self.toTxt: self.toolbar.addAction(self.saveTxtAction)
        if self.toPdf: self.toolbar.addAction(self.savePdfAction)
        if self.toPrinter: self.toolbar.addAction(self.toPrinterAction)
        self.toolbar.setIconSize(QSize(16, 16))

    def registerPlugin(self, pluginAction):
        """
        Register a plugin
        """
        self.toolbarPlugins.addAction(pluginAction)
        self.toolbarPlugins.setIconSize(QSize(16, 16))
        self.pluginsBox.show()
        
    def onRemoveLines(self):
        """
        Called when lines must be removed
        """
        ret = []
        for l in self.__data.splitlines():
            if self.delTG.checkState() and l.startswith("TESTGLOBAL"):
                continue
            elif self.delTP.checkState() and l.startswith("TESTPLAN"):
                continue
            elif self.delTS.checkState() and l.startswith("TESTSUITE"):
                continue
            elif self.delTU.checkState() and l.startswith("TESTUNIT"):
                continue
            elif self.delTA.checkState() and l.startswith("TESTABSTRACT"):
                continue
            elif self.delTC.checkState() and l.startswith("TESTCASE"):
                continue
            elif self.delSTP.checkState() and l.startswith("STEP"):
                continue
            else:
                ret.append(l)
        self.txtEdit.setText( "\n".join(ret) )
        del ret

    def saveXml(self):
        """
        Save to xml file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save XML file", "", 
                                                "XML file (*.xml);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new
        
        if _filename:
            try:
                with codecs.open(_filename, "w", "utf-8") as f:
                    f.write( self.txtEdit.text()  )
            except Exception as e:
                self.error('unable to save design file as xml: %s' % str(e) )

            else:
                # notify user
                self.parent.app().showMessageTray("XML verdict report saved")
        
    def savePrinter(self):
        """
        Save to printer
        """
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("Print")

        if dialog.exec_() != QDialog.Accepted:
            return

        doc = QTextDocument()
        doc.setPlainText( self.txtEdit.text() )
        doc.print_(printer)

        # notify user
        self.parent.app().showMessageTray("PDF verdict printing...")
        
    def saveCsv(self):
        """
        Save to csv file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save CSV file", "", 
                                                "CSV file (*.csv);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new
        
        if _filename:
            try:
                f = open( _filename, 'w'  )
                f.write( self.txtEdit.toPlainText() )
                f.close()
            except Exception as e:
                self.error('unable to save report file as txt: %s' % str(e) )

            else:
                # notify user
                self.parent.app().showMessageTray("CSV verdict report saved")
        
    def saveTxt(self):
        """
        Save to txt file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save TXT file", "", 
                                                "TXT file (*.txt);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new
        
        if _filename:
            try:
                f = open( _filename, 'w'  )
                f.write( self.txtEdit.toPlainText() )
                f.close()
            except Exception as e:
                self.error('unable to save report file as txt: %s' % str(e) )

            else:
                # notify user
                self.parent.app().showMessageTray("TXT verdict report saved")
        
    def savePdf(self):
        """
        Save pdf file
        """
        fileName = QFileDialog.getSaveFileName(self, 'Save to PDF', "", 
                                               "PDF file (*.pdf);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = fileName
        else:
            _filename = fileName
        # end of new
        
        if _filename:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setColorMode(QPrinter.Color)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(_filename)

            doc = QTextDocument()
            if self.toXml:
                doc.setPlainText( self.txtEdit.text() )
            else:
                doc.setHtml( self.txtEdit.toHtml() )
            doc.print_(printer)

            # notify user
            self.parent.app().showMessageTray("PDF verdict report saved")
        
    def loadVerdicts(self, content):
        """
        Load verdicts in the widget
        """
        self.__data = content
        self.txtEdit.setText( content )

    def deactive(self):
        """
        Deactive the widget
        """
        self.__data = ''
        self.txtEdit.setText( "" )     
        
class WArchives(QWidget, Logger.ClassLogger):
    """
    Widgets for archives
    """
    def __init__(self, parent, mainParent):
        """
        Constructs WArchives widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.mainParent = mainParent
        self.name = self.tr("Tests Results")
        self.archivesItems = []

        self.projects = []
        self.projectClicked = False
        self.projectInitialized = False
        self.archives = None
        self.itemCurrent = None
        self.backupsRoot = None
        
        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.createToolbar()
        self.deactivate()
        
    def app(self):
        """
        accessor to the main application
        """
        return self.mainParent
        
    def createConnections (self):
        """
        Widgets connections
        """
        self.archives.customContextMenuRequested.connect(self.onPopupMenu)
        self.archives.itemDoubleClicked.connect(self.onDoubleClicked)
        self.archives.currentItemChanged.connect(self.currentItemChanged)

        self.prjComboBox.currentIndexChanged.connect(self.onProjectChanged)
        self.prjComboBox.highlighted.connect(self.onProjectHighlighted)
        
    def createActions (self):
        """
        Actions defined:
         * empty
         * open test result
         * save file
         * zip test result
         * partial refresh of the repository
         * complete refresh of the repository
         * read comments of a test result
         * add comment on a test result
         * delete all comments of a test result
         * backup all archives
         * delete all backups
         * export a backups
         * expand all items on archive tree
         * collapse all items on archive tree
         * export test verdict of a test result
         * export test report of a test result
         * export test design of a test result
         * expand sub tree of a item on archive tree
        """
        self.deleteTrAction = QtHelper.createAction(self, "&Delete\nResult", self.deleteTestResult, 
                                                    tip = 'Delete the selected test result', 
                                                    icon = QIcon(":/delete_file.png"), shortcut = "Del" )

        self.emptyAction = QtHelper.createAction(self, "&Empty\nall", self.emptyArchives, 
                                                    tip = 'Remove all archives', 
                                                    icon = QIcon(":/trash.png") )
        self.openAction = QtHelper.createAction(self, "&Open", self.openResult, 
                                                    tip = 'Open the selected test result', 
                                                    icon = QIcon(":/open-test.png"))
        self.saveAction = QtHelper.createAction(self, "&Save", self.saveFile, 
                                                    tip = 'Save the selected test result', 
                                                    icon = QIcon(":/save-test.png"))
        self.zipAction = QtHelper.createAction(self, "&Create package", self.createPkg, 
                                                tip = 'Create a package of the selected directory', 
                                                icon = QIcon(":/file-zip-logs.png") )
        self.refreshAction = QtHelper.createAction(self, "&Partial", self.partialRefreshRepo, 
                                                    tip = 'Refresh partial results', tooltip='Partial refresh', 
                                                    icon = QIcon(":/act-half-refresh.png") )
        self.fullRefreshAction = QtHelper.createAction(self, "&Full", self.fullRefreshRepo, 
                                                    tip = 'Refresh all test results', tooltip='Full refresh', 
                                                    icon = QIcon(":/act-refresh.png") )   

        self.expandAllAction = QtHelper.createAction(self, "&Expand All...", self.expandAllItems, icon = None, 
                                                    tip = 'Expand all items' )
        self.collapseAllAction = QtHelper.createAction(self, "&Collapse All...", self.collapseAllItems, icon = None, 
                                                    tip = 'Collapse all items' )

        # export csv
        self.exportTestVerdictAction = QtHelper.createAction(self, "&Verdict", self.exportTestVerdict,
                                                        tip = 'Export test verdict', icon = QIcon(":/tvr.png"))
        self.exportTestReportAction = QtHelper.createAction(self, "&Report", self.exportTestReport,
                                                        tip = 'Export test report', icon = QIcon(":/trp.png"))
        self.exportTestDesignAction = QtHelper.createAction(self, "&Design", self.exportTestDesign,
                                                        tip = 'Export test design', icon = QIcon(":/tds.png"))

        self.expandSubtreeAction = QtHelper.createAction(self, "&Expand subtree...", self.expandSubtreeIteem, icon = None, 
                                                        tip = 'Expand subtree' )

    def createWidgets (self):
        """
        QtWidgets creation

        QTreeWidget (Type, Name, Size (KB))
         _______________
        |    QToolBar   |
        |---------------|
         _______________
        |  QStringList  |
        |---------------|
        |               |
        |               |
        |_______________|
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbarManage = QToolBar(self)
        self.toolbarManage.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbarManage.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbarActions = QToolBar(self)
        self.toolbarActions.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.toolbarExports = QToolBar(self)
        self.toolbarExports.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        # prepare menu
        self.refreshBox = QGroupBox("Refresh")
        self.refreshBox.setStyleSheet( """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutRefresh = QHBoxLayout()
        layoutRefresh.addWidget(self.dockToolbar)
        layoutRefresh.setContentsMargins(0,0,0,0)
        self.refreshBox.setLayout(layoutRefresh)
        
        self.manageBox = QGroupBox("Manage")
        self.manageBox.setStyleSheet(  """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutManage = QHBoxLayout()
        layoutManage.addWidget(self.toolbarManage)
        layoutManage.setContentsMargins(0,0,0,0)
        self.manageBox.setLayout(layoutManage)
        
        self.exportBox = QGroupBox("Exports")
        self.exportBox.setStyleSheet(  """
                                       QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                       QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                       QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutExports = QVBoxLayout()
        layoutExports.addWidget(self.toolbarExports)
        layoutExports.addWidget(self.toolbarActions)
        layoutExports.setContentsMargins(0,0,0,0)
        self.exportBox.setLayout(layoutExports)
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.refreshBox)
        layoutToolbars.addWidget(self.manageBox)
        layoutToolbars.addWidget(self.exportBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        
        layoutFinal = QHBoxLayout(self)
        layoutLeft = QVBoxLayout()

        layoutRight = QVBoxLayout()       
 
        self.tabComments = PreviewComments(self)
        self.tabImages = PreviewImages(self)
        self.tabReports = PreviewReport(self, data='', toCsv=True, toHtml=True, 
                                        toPrinter=True, toTxt=True, toPdf=True)
        self.tabVerdicts = PreviewVerdict(self, data='', toCsv=True, 
                                        toPrinter=True, toTxt=True, toPdf=True)
        self.tabXmlVerdicts = PreviewVerdict(self, data='', toCsv=False, toXml=True, 
                                        toPrinter=True, toTxt=False, toPdf=True)
        self.tabBasicReports = PreviewReport(self, data='', toCsv=True, toHtml=True, 
                                        toPrinter=True, toTxt=True, toPdf=True)
        
        self.previewTab = QTabWidget()
        self.previewTab.setMinimumWidth(700)
        self.previewTab.addTab( self.tabReports, QIcon(":/trp.png") , "Advanced Report" )
        self.previewTab.addTab( self.tabBasicReports, QIcon(":/trp.png") , "Basic Report" )
        self.previewTab.addTab( self.tabXmlVerdicts, QIcon(":/tvr.png") , "Xml Verdict" )
        self.previewTab.addTab( self.tabVerdicts, QIcon(":/tvr.png") , "Text Verdict" )
        self.previewTab.addTab( self.tabImages, QIcon(":/png.png") , "Preview" )
        self.previewTab.addTab( self.tabComments, QIcon(":/read-posts.png") , "Comments" )

        layoutRight.addWidget(self.previewTab)

        style = self.style()
        self.folderIcon = QIcon()
        self.folderIcon.addPixmap(style.standardPixmap(QStyle.SP_DirClosedIcon), 
                                  QIcon.Normal, QIcon.Off)
        self.folderIcon.addPixmap(style.standardPixmap(QStyle.SP_DirOpenIcon), 
                                  QIcon.Normal, QIcon.On)
        self.rootIcon = QIcon()       
        self.rootIcon.addPixmap( style.standardPixmap(QStyle.SP_DriveNetIcon) )

        self.archives = DeselectableTreeWidget(self)
        self.archives.setEnabled(False)
        self.archives.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labels = [ self.tr("Name"), self.tr("Result"), self.tr("Run"), 
                        self.tr("Replay Id"), self.tr("Created"), 
                        self.tr("User"), self.tr("Size on disk") ]
        self.archives.setHeaderLabels(self.labels)
        self.archives.setColumnWidth(COL_NAME, 370)
        self.archives.setColumnWidth(COL_VERDICT, 40 )
        self.archives.setColumnWidth(COL_RUN, 30 )
        self.archives.setColumnWidth(COL_REPLAY, 60 )
        self.archives.setColumnWidth(COL_TIMESTAMP, 110 )
        self.archives.setColumnWidth(COL_SIZE, 70)

        self.prjComboBox = QComboBox(self) 
        self.prjComboBox.setStyleSheet( """QComboBox {border: 0px; }""" )
        self.prjComboBox.setMinimumWidth(100)
        
        layoutPrj = QVBoxLayout()
        layoutPrj.addWidget(QLabel(self.tr(" Project:")))
        layoutPrj.addWidget(self.prjComboBox)
        self.frameProject = QFrame()
        self.frameProject.setLayout(layoutPrj)

        hSplitter = QSplitter(self)
        hSplitter.setOrientation(Qt.Vertical)
        hSplitter.addWidget( self.archives )
        hSplitter.setContentsMargins(0,0,0,0)
        hSplitter.setStretchFactor(0, 2)

        layoutLeft.addLayout(layoutToolbars)
        layoutLeft.addWidget( hSplitter )

        layoutLeft.setContentsMargins(0,0,0,0)
        layoutRight.setContentsMargins(0,0,0,0)
        

        frame_left = QFrame(self)
        frame_left.setFrameShape(QFrame.NoFrame)
        frame_left.setLayout(layoutLeft)

        frame_right = QFrame(self)
        frame_right.setFrameShape(QFrame.NoFrame)
        frame_right.setLayout(layoutRight)


        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(frame_left)
        splitter1.addWidget(frame_right)
        splitter1.setStretchFactor(0, 1)

        layoutFinal.addWidget(splitter1)
        self.setLayout(layoutFinal)

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-------||
        || Empty ||
        ||-------||
        """
        self.dockToolbar.setObjectName("Archives toolbar")
        self.dockToolbar.addWidget(self.frameProject)
        self.dockToolbar.addAction(self.refreshAction)
        self.dockToolbar.addAction(self.fullRefreshAction)
        self.dockToolbar.setIconSize(QSize(16, 16))
        
        self.toolbarManage.addAction(self.emptyAction)
        self.toolbarManage.addAction(self.deleteTrAction)
        self.toolbarManage.addAction(self.openAction)
        self.dockToolbar.setIconSize(QSize(16, 16))

        self.toolbarActions.addAction(self.saveAction)
        self.toolbarActions.setIconSize(QSize(16, 16))
        
        self.toolbarExports.addAction(self.exportTestVerdictAction)
        self.toolbarExports.addAction(self.exportTestReportAction)
        self.toolbarExports.addAction(self.exportTestDesignAction)
        self.toolbarExports.setIconSize(QSize(16, 16))

    def pluginDataAccessor(self):
        """
        Return the data for plugin
        """
        ret = {}
        ret['verdict-xml'] = self.tabXmlVerdicts.txtEdit.text()
        ret['verdict-csv'] = self.tabVerdicts.txtEdit.toPlainText()
        ret['report-html'] =  self.tabReports.cacheHtml
        ret['basic-report-html'] = self.tabBasicReports.cacheHtml
        
        return ret

    def addPlugin(self, pluginAct):
        """
        Register the plugin in the widget
        """
        self.tabReports.registerPlugin(pluginAct)
        self.tabVerdicts.registerPlugin(pluginAct)
        self.tabBasicReports.registerPlugin(pluginAct)
        self.tabXmlVerdicts.registerPlugin(pluginAct)

    def deleteTestResult(self):
        """
        Deete a test result
        """
        
        cur = self.itemCurrent
        
        messageBox = QMessageBox(self)
        
        if cur.typeItem == 0: # date folder
            logDirName = cur.archiveDescr['name']
            projectId =  cur.archiveDescr['project']
       
            reply = messageBox.warning(self, self.tr("Delete Test Result"), 
                                        self.tr("Are you sure you want to delete?"),
                                        QMessageBox.Yes |QMessageBox.Cancel )
            #call web service
            if reply == QMessageBox.Yes:   
                UCI.instance().deleteTestResult(  '%s/' % (logDirName), projectId=projectId )
            
        elif cur.typeItem == 1: # test result folder
            logDirName = cur.parent.archiveDescr['name']
            logSubDirName = cur.archiveDescr['name']
            projectId =  cur.archiveDescr['project']
       
            
            reply = messageBox.warning(self, self.tr("Delete Test Result"), 
                                       self.tr("Are you sure you want to delete?"),
                                       QMessageBox.Yes |QMessageBox.Cancel )
            #call web service
            if reply == QMessageBox.Yes:   
                UCI.instance().deleteTestResult('%s/%s' % (logDirName,logSubDirName), 
                                                projectId=projectId )
        else:
            pass
        del messageBox
        
    def comments(self):
        """
        Returen the comments tabulation
        """
        return self.tabComments
        
    def images(self):
        """
        Return the images tabulation
        """
        return self.tabImages
        
    def reports(self):
        """
        Return the reports tabulation
        """
        return self.tabReports
        
    def verdicts(self):
        """
        Return the verdict tabulation
        """
        return self.tabVerdicts
        
    def basicReports(self):
        """
        Return the basic report tabulation
        """
        return self.tabReports
        
    def xmlVerdicts(self):
        """
        Return the xml verdict tabulation
        """
        return self.tabVerdicts
        
    def active (self):
        """
        Enables QTreeWidget
        """
        self.previewTab.setEnabled(True)
        
        self.archives.setEnabled(True)
        self.refreshAction.setEnabled(True)
        self.fullRefreshAction.setEnabled(True)

        if UCI.RIGHTS_ADMIN in UCI.instance().userRights :
            self.emptyAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.projects = []
        self.projectClicked = False
        self.projectInitialized = False

        self.archives.clear()
        self.archives.setEnabled(False)
        self.archivesItems = []
        self.setDefaultActionsValues()
    
        self.itemCurrent = None
        
        self.previewTab.setEnabled(False)
        self.resetPreview()

    def setDefaultActionsValues (self):
        """
        Set default values for qt actions
        """
        self.expandSubtreeAction.setEnabled(False)
        self.expandAllAction.setEnabled(False)
        self.collapseAllAction.setEnabled(False)
        self.emptyAction.setEnabled(False)
        self.openAction.setEnabled(False)
        self.saveAction.setEnabled(False)
        self.zipAction.setEnabled(False)
        self.refreshAction.setEnabled(False)
        self.fullRefreshAction.setEnabled(False)

        self.exportTestVerdictAction.setEnabled(False)
        self.exportTestReportAction.setEnabled(False)
        self.exportTestDesignAction.setEnabled(False)
        
        # new in v12
        self.previewTab.setEnabled(False)
        self.previewTab.setTabEnabled(TAB_VERDICTS, False)
        self.previewTab.setTabEnabled(TAB_REPORTS, False)
        self.previewTab.setTabEnabled(TAB_IMAGES, False)
        self.previewTab.setTabEnabled(TAB_COMMENTS, False)
        self.deleteTrAction.setEnabled(False)
        
        self.previewTab.setTabEnabled(TAB_BASIC_REPORTS, False)
        
    def expandAllItems(self):
        """
        Expand all items
        """
        self.archives.expandAll()
    
    def collapseAllItems(self):
        """
        Collapse all items
        """
        self.archives.collapseAll()

    def exportTestReport(self):
        """
        Expot test report
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # test path
        cur = self.itemCurrent
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        
        # filename without extension, example : "Noname1_0_PASS_0.trx
        logFileName =  cur.archiveDescr['name'].rsplit('.', 1)[0]
        
        # and without nb comment and result
        logFileName =  logFileName.rsplit('_', 2)[0]
        projectId = cur.archiveDescr['project']
        
        # call web services
        UCI.instance().exportTestReport( testPath= '%s/%s' % (logDirName,logSubDirName), 
                                            testFileName=logFileName, projectId=projectId )

    def exportTestDesign(self):
        """
        Export test design
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # test path
        cur = self.itemCurrent
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        # filename without extension, example : "Noname1_0_PASS_0.trx
        logFileName =  cur.archiveDescr['name'].rsplit('.', 1)[0]
        # and without nb comment and result
        logFileName =  logFileName.rsplit('_', 2)[0]
        projectId = cur.archiveDescr['project']

        # call web services
        UCI.instance().exportTestDesign( testPath= '%s/%s' % (logDirName,logSubDirName), 
                                        testFileName=logFileName, projectId=projectId )

    def exportTestVerdict(self):
        """
        Export test verdict
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # test path
        cur = self.itemCurrent
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        
        # filename without extension, example : "Noname1_0_PASS_0.trx
        logFileName =  cur.archiveDescr['name'].rsplit('.', 1)[0]
        
        # and without nb comment and result
        logFileName =  logFileName.rsplit('_', 2)[0]
        projectId = cur.archiveDescr['project']
        
        # call web services
        UCI.instance().exportTestVerdict( testPath= '%s/%s' % (logDirName,logSubDirName), 
                                            testFileName=logFileName, projectId=projectId )

    def partialRefreshRepo(self):
        """
        Refresh statistics of the archives
        """
        projectName = self.prjComboBox.currentText()
        projectId = self.getProjectId(project="%s" % projectName)
        
        # web service call
        UCI.instance().refreshRepo(repo=UCI.REPO_ARCHIVES, partialRefresh=True, 
                                    project=projectId)

    def fullRefreshRepo(self):
        """
        Refresh statistics of the archives
        """
        projectName = self.prjComboBox.currentText()
        projectId = self.getProjectId(project="%s" % projectName)
        UCI.instance().refreshRepo(repo=UCI.REPO_ARCHIVES, partialRefresh=False, 
                                    project=projectId, showPopup=False)

    def createRootItem(self):
        """
        Create the root item
        """
        self.backupsRoot =  ArchiveItem(parent = self.archives, archiveDescr = "Root", 
                                        icon = self.rootIcon, itemType= QTreeWidgetItem.UserType+10 )
        self.backupsRoot.setExpanded(True)
        return self.backupsRoot

    def currentItemChanged(self, currentItem, previousItem):
        """
        On current item changed

        @param currentItem: 
        @type currentItem:

        @param previousItem: 
        @type previousItem:
        """
        if currentItem is not None:
            self.itemCurrent = currentItem
            
            # trx file
            if currentItem.type() ==  QTreeWidgetItem.UserType+2:
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.openAction.setEnabled(True)
                self.saveAction.setEnabled(True)
                self.exportTestVerdictAction.setEnabled(True)
                self.exportTestReportAction.setEnabled(True)
                self.exportTestDesignAction.setEnabled(True)
                
                self.zipAction.setEnabled(False)
                
                # new in v12
                self.deleteTrAction.setEnabled(False)
                self.loadTestPreview()
                
            # other file
            elif currentItem.type() ==  QTreeWidgetItem.UserType+3:
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.openAction.setEnabled(False)
                self.saveAction.setEnabled(True)
                self.zipAction.setEnabled(False)
                self.exportTestVerdictAction.setEnabled(False)
                self.exportTestReportAction.setEnabled(False)
                self.exportTestDesignAction.setEnabled(False)
                
                # new in v12
                self.deleteTrAction.setEnabled(False)
                self.loadImagePreview()
                
            # folder
            elif currentItem.type() ==  QTreeWidgetItem.UserType+0:
                self.expandSubtreeAction.setEnabled(True)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.openAction.setEnabled(False)
                self.saveAction.setEnabled(False)
                self.exportTestVerdictAction.setEnabled(False)
                self.exportTestReportAction.setEnabled(False)
                self.exportTestDesignAction.setEnabled(False)

                if currentItem.typeItem == TYPE_ITEM_FOLDER_TEST: # sub dir
                    self.zipAction.setEnabled(True)
                    self.deleteTrAction.setEnabled(True)
                    
                    # new in v12.2
                    if currentItem.childTest is not None:
                        self.loadTestPreview()
                    else:
                        self.resetPreview()
                        
                else:
                    self.zipAction.setEnabled(False)  
                    self.deleteTrAction.setEnabled(True)

                    # new in v12
                    self.resetPreview()
                
            else:
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(True)
                self.collapseAllAction.setEnabled(True)
                self.openAction.setEnabled(False)
                self.saveAction.setEnabled(False)
                self.zipAction.setEnabled(False)
                self.exportTestVerdictAction.setEnabled(False)
                self.exportTestReportAction.setEnabled(False)
                self.exportTestDesignAction.setEnabled(False)
                
                # new in v12
                self.deleteTrAction.setEnabled(False)
                self.resetPreview()
                
        if UCI.RIGHTS_ADMIN not in UCI.instance().userRights :
            self.deleteTrAction.setEnabled(False)
        
    def onDoubleClicked (self, wfile):
        """
        Open result logs on double click

        @param wfile: 
        @type wfile:
        """
        if wfile.type() ==  QTreeWidgetItem.UserType+2:
            self.itemCurrent = wfile
            self.openResult()
        elif wfile.type() ==  QTreeWidgetItem.UserType+3:
            self.itemCurrent = wfile
            self.saveFile()

    def onPopupMenu(self, pos):
        """
        Display menu on right click for the archives list

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.archives.itemAt(pos)
        if item:
            self.itemCurrent = item
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+10:
                self.menu.addAction( self.expandAllAction )
                self.menu.addAction( self.collapseAllAction )
                self.menu.addSeparator()
                self.menu.addAction( self.refreshAction )
                self.menu.addAction( self.fullRefreshAction )
            
            # folder date
            elif self.itemCurrent.typeItem == 0:
                self.menu.addAction( self.expandSubtreeAction )
                # not yet fully implemented!!
                self.menu.addSeparator()
                self.menu.addAction( self.deleteTrAction )
            
            # folder
            elif self.itemCurrent.typeItem == 1:
                trxDetected = False
                for i in xrange(self.itemCurrent.childCount()):
                    if self.itemCurrent.child(i).type() ==  QTreeWidgetItem.UserType+2:
                        trxDetected = True
                if trxDetected:
                    self.menu.addAction( self.zipAction )
                else:
                    self.menu.addAction( "Partial load...", self.loadCache)
                self.menu.addSeparator()
                self.menu.addAction( "Copy location...", self.copyArchiveLocationIteem) 

                # not yet fully implemented!!
                if trxDetected:
                    self.menu.addSeparator()
                    self.menu.addAction( self.deleteTrAction )
            
            # file trx
            elif item.type() ==  QTreeWidgetItem.UserType+2:
                self.menu.addAction( self.openAction )
                self.menu.addSeparator()
                self.menu.addAction( self.saveAction )
                self.menu.addAction( self.exportTestVerdictAction )
                self.menu.addAction( self.exportTestReportAction )
                self.menu.addAction( self.exportTestDesignAction )
                self.menu.addSeparator()
                self.menu.addAction( "Copy Filename...", self.copyArchiveLocationIteem) 

            # other files
            elif item.type() ==  QTreeWidgetItem.UserType+3:
                self.menu.addAction( self.saveAction )
            self.menu.popup(self.archives.mapToGlobal(pos))

    def expandItem(self, itm):
        """
        Expand item
        """
        itm.setExpanded(True)
        if itm.childCount() > 0:
            for i in xrange( itm.childCount() ):
                itm.child(i).setExpanded(True)
                if itm.child(i).childCount() > 0:
                    self.expandItem(itm=itm.child(i))

    def expandSubtreeIteem(self):
        """
        Expand the subtree item
        """
        if self.itemCurrent is not None:
            self.expandItem(itm=self.itemCurrent)

    def copyArchiveLocationIteem(self):
        """
        Copy the archive location of the item
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # retrieve the text to copy
        itemValue = self.itemCurrent.getTextValue()
        
        if sys.version_info > (3,): # python3 support
            if isinstance(itemValue, bytes):
                itemValue = str(itemValue, "utf8")

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemValue)

    def loadCache(self):
        """
        Load test from cache
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        # {'content': [], 'type': 'folder', 'name': '16:00:03.219498.Tm9uYW1lMQ==.admin'}
        cur = self.itemCurrent
        logDirName = cur.parent.archiveDescr['name']
        logSubDirName = cur.archiveDescr['name']
        projectId =  cur.archiveDescr['project']
        
        # call web services
        UCI.instance().loadTestCache(  logDirName, logSubDirName, projectId )

    def createPkg(self):
        """
        Create a package of the selected test result
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        cur = self.itemCurrent
        logDirName = cur.parent.archiveDescr['name']
        logSubDirName = cur.archiveDescr['name']
        projectId =  cur.archiveDescr['project']

        # call web services
        UCI.instance().createZipArchives(  logDirName, logSubDirName, projectId=projectId )

    def saveFile (self):
        """
        Save the selected file
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        cur = self.itemCurrent
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        logFileName =  cur.archiveDescr['name']
        projectId =  cur.archiveDescr['project']
        
        if Settings.instance().readValue( key = 'TestArchives/download-directory' ) != 'Undefined':
            _destfileName = "%s/%s" % ( Settings.instance().readValue( key = 'TestArchives/download-directory' ), 
                                        logFileName )
        else:
            extension = self.tr("All Files (*.*)")
            destfileName = QFileDialog.getSaveFileName(self, self.tr("Save Test Result"), 
                                                        logFileName, extension )
            # new in v17.1
            if QtHelper.IS_QT5:
                _destfileName, _type = destfileName
            else:
                _destfileName = destfileName
            # end of new
            
        if _destfileName:
            # call web services
            UCI.instance().downloadResultLogsV2( '%s/%s' % (logDirName,logSubDirName), logFileName, projectId, 
                                                        andSave=True, destFile="%s" % _destfileName )
        else:
            # display bug
            self.archives.setVisible(False)
            self.archives.setVisible(True)

    def openResult (self):
        """
        Open the selected test result
        """
        if self.itemCurrent is None:
            self.error( 'current item is none' )
            return

        cur = self.itemCurrent
        logDirName = cur.parent.parent.archiveDescr['name']
        logSubDirName = cur.parent.archiveDescr['name']
        logFileName =  cur.archiveDescr['name']
        projectId =  cur.archiveDescr['project']

        # call web service
        UCI.instance().downloadResultLogsV2(  '%s/%s' % (logDirName,logSubDirName), 
                                                logFileName, projectId=projectId )

    def loadData( self, data, parent, fileincluded=True, subCall=False):
        """
        Load data received from the server

        @param listing: 
        @type listing: list

        @param parent: 
        @type parent:

        @param fileincluded: 
        @type fileincluded: boolean
        """
        nbFolders = 0
        # fill the tree view    
        try:
            # example of data
            # [{'size': '22', 'project': '1', 'name': 'private_storage_2016-05-20_15-55-17.144
            # _0.zip', 'type': 'file', 'modification': 1463774117}, {'size': '22', 'project':
            # '1', 'name': 'private_storage_2016-05-20_15-55-19.173_1.zip', 'type': 'file', 'm
            # odification': 1463774119}, {'size': '22', 'project': '1', 'name': 'private_stora
            # ge_2016-05-20_15-55-21.127_2.zip', 'type': 'file', 'modification': 1463774121},
            # {'size': '22', 'project': '1', 'name': 'private_storage_2016-05-20_15-55-22.839_
            # 3.zip', 'type': 'file', 'modification': 1463774122}, {'size': '5018', 'project':
             # '1', 'name': 'verdict_0_PASS_0.trx', 'type': 'file', 'modification': 1463774117
            # }, {'size': '5024', 'project': '1', 'name': 'verdict_1_PASS_0.trx', 'type': 'fil
            # e', 'modification': 1463774119}, {'size': '5014', 'project': '1', 'name': 'verdi
            # ct_2_PASS_0.trx', 'type': 'file', 'modification': 1463774121}, {'size': '4920',
            # 'project': '1', 'name': 'verdict_3_FAIL_0.trx', 'type': 'file', 'modification':
            # 1463774122}]
            for dct in  data:
                # loading folder and all files
                if dct["type"] == "folder":
                    nbFolders += 1
                    item = ArchiveItem(parent = parent, archiveDescr = dct, icon = self.folderIcon )
                    if not subCall: item.setExpanded(True) # new in v11.3
                    self.archivesItems.append(item)

                    # new in v12.2
                    nb = self.loadData( data=sorted(dct["content"], key=lambda k: k['name']), parent=item, 
                                        fileincluded=fileincluded, subCall=True )
                    if nb > 0:
                        item.setNbRun(nb=nb)
                        
                else:
                    if fileincluded:
                        if dct["type"] == "file":
                            if dct["name"].endswith('trx'):
                                typeFile = QTreeWidgetItem.UserType+2
                            else:
                                typeFile = QTreeWidgetItem.UserType+3
                            item = ArchiveItem(parent = parent, archiveDescr = dct, itemType=typeFile )
                            self.archivesItems.append(item)
            self.archives.sortItems(COL_NAME, Qt.DescendingOrder)
            self.archives.sortItems(COL_TIMESTAMP, Qt.DescendingOrder)
        except Exception as e:
            self.error( e )
        return nbFolders
        
    def cleanTreeView(self):
        """
        Clean the archives treeview and stats
        """
        self.archives.clear()
        self.archivesItems = []

    def refreshData (self, data, data_stats, action):
        """
        Refresh archives in realtime

        @param data:  [{'content': [{'content': [], 'type': 'folder', 'name': '12:19:07.783.dG1w.admin'}], 'type': 'folder', 'name': '2012-02-08'}]
        @type data: dict

        @param data_stats: 
        @type data_stats:

        @param action: 
        @type action:
        """
        try:
            # new in v10
            # check project - two cases
            # - received a project notification not authorized
            # - the current project in the combobox does not correspond to the project id received
            projectId = data[0]['project']
            if not self.checkProjectId(projectId=projectId):
                return
            projectName = self.prjComboBox.currentText()
            projectIdCurrent = self.getProjectId(project="%s" % projectName)
            if "%s" % projectIdCurrent !=  "%s" % projectId:
                return
            # end in v10
            
            
            if self.backupsRoot is None:
                self.createRootItem() 
            # extract main dir, sub dir
            mainDir = data[0]['name']
            subDir = data[0]['content'][0]['name']

            newFile = None
            if len(data[0]['content'][0]['content']) >= 1:
                newFile = data[0]['content'][0]['content'][0]['name']
                
            # search main dir date
            mainItemFound = None
            for itm in self.archivesItems:
                if itm.archiveDescr['name'] == mainDir and itm.typeItem == 0:
                    mainItemFound = itm
                    break
            if mainItemFound is None:
                item = ArchiveItem(parent = self.backupsRoot, archiveDescr = data[0], 
                                    icon = self.folderIcon, colored=True )
                self.archivesItems.append(item) 
                mainItemFound = item
            else:
                mainItemFound.setColor()
                
            # search sub dir
            subItemFound = None
            for itm in self.archivesItems:
                if itm.archiveDescr["name"] == subDir and itm.typeItem == 1:
                    if itm.parent == mainItemFound:
                        subItemFound = itm
                        break

            if subItemFound is None:
                item = ArchiveItem(parent = mainItemFound, archiveDescr = data[0]['content'][0], 
                                    icon = self.folderIcon, colored=True )
                self.archivesItems.append(item) 
                subItemFound = item 
            else:
                subItemFound.setColor()
                
            # add file
            if newFile is not None:
            
                trxFile = False
                if data[0]['content'][0]['content'][0]["name"].endswith('trx'):
                    typeFile = QTreeWidgetItem.UserType+2
                    trxFile = True
                else:
                    typeFile = QTreeWidgetItem.UserType+3

                item = ArchiveItem(parent = subItemFound, archiveDescr = data[0]['content'][0]['content'][0],
                                        itemType=typeFile, colored=True )
                self.archivesItems.append(item) 

                # update the counter of run
                if trxFile: # fix in v12.2 count only trx file
                    nb = mainItemFound.text(COL_RUN)
                    if not nb:
                        nb = 0
                    nb = int(nb) + 1
                    mainItemFound.setNbRun(nb=nb)
            # sort item
            self.archives.sortItems(COL_NAME, Qt.DescendingOrder)
            self.archives.sortItems(COL_TIMESTAMP, Qt.DescendingOrder)
        except Exception as e:
            self.error( "unable to refresh data: %s" % e )

    def emptyArchives(self):
        """
        Removes archives on server
        """
        reply = QMessageBox.question(self, "Empty archives", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            # call web services
            projectName = self.prjComboBox.currentText()
            projectId = self.getProjectId(project="%s" % projectName)
            UCI.instance().emptyRepo(repo=UCI.REPO_ARCHIVES, project=projectId)

    def initializeProjects(self, projects=[], defaultProject=1):
        """
        Create the root item and load all subs items

        @param listing: 
        @type listing: list
        """
        self.projects = projects
        self.prjComboBox.clear()
        
        # sort project list by  name
        projects = sorted(projects, key=lambda k: k['name'])
        i = 0
        for p in projects:
            if p["name"].lower() == "common":
                break
            i += 1
        common = projects.pop(i)      
        projects.insert(0, common)
        
        self.projects = projects
        
        # insert data
        pname = ''
        for p in projects:
            self.prjComboBox.addItem ( p['name']  )
            if defaultProject == p['project_id']:
                pname = p['name']
        self.prjComboBox.insertSeparator(1)
        
        for i in xrange(self.prjComboBox.count()):
            item_text = self.prjComboBox.itemText(i)
            if str(pname) == str(item_text):
                self.prjComboBox.setCurrentIndex(i)
        self.projectInitialized = True
        
    def onProjectHighlighted(self):
        """
        Called on project highlighted
        """
        if self.projectInitialized:
            self.projectClicked = True

    def onProjectChanged(self, comboIndex):
        """
        Called on project changed
        """
        projectName = self.prjComboBox.itemText(comboIndex)
        if self.projectClicked and self.projectInitialized:
            self.projectClicked = False
    
    def checkProjectId(self, projectId):
        """
        Check the project id
        """
        ret = False
        for p in self.projects:
            if "%s" % p['project_id'] == "%s" % projectId:
                ret = True; break;
        return ret
        
    def getProjectId(self, project):
        """
        Returns the project id according to the project passed as argument
        """
        pid = 0
        for p in self.projects:
            if p['name'] == project:
                pid = p['project_id']
                break
        if pid == 0:
            self.error( 'project not found : %s' % project )
        return pid

    def loadTestPreview(self):
        """
        Load test preview
        """
        if self.itemCurrent is None: return

        # cursor to the selected item
        cur = self.itemCurrent
        replayId = "0"
        
        if cur.typeItem == TYPE_ITEM_FOLDER_TEST: 
            if cur.childTest is not None:
                testId = cur.testId
                projectId =  cur.childTest['project']
            else:
                return
        else:
            testId = cur.parent.testId
            replayId = cur.runId
            projectId =  cur.archiveDescr['project']
       
        self.tabComments.active(item=self.itemCurrent)

        # call web service
        RCI.instance().getTestReports( testId=testId, replayId=replayId, 
                                       projectId=projectId )
         
    def loadImagePreview(self):
        """
        Load image preview
        """
        if self.itemCurrent is None: return
        
        if self.itemCurrent.archiveDescr["name"].endswith('png') or self.itemCurrent.archiveDescr["name"].endswith('jpg'):
            self.previewTab.setTabEnabled(TAB_REPORTS, False)
            self.previewTab.setTabEnabled(TAB_BASIC_REPORTS, False)
            self.previewTab.setTabEnabled(TAB_IMAGES, True)
            self.previewTab.setTabEnabled(TAB_VERDICTS, False)
            self.previewTab.setTabEnabled(TAB_XML_VERDICTS, False)
            self.previewTab.setTabEnabled(TAB_COMMENTS, False)
            
            self.tabComments.deactive()
            
            self.previewTab.setCurrentIndex(TAB_IMAGES)   

            cur = self.itemCurrent
            logDirName = cur.parent.parent.archiveDescr['name']
            logSubDirName = cur.parent.archiveDescr['name']
            logFileName =  cur.archiveDescr['name']
            projectId =  cur.archiveDescr['project']

            # call web service
            UCI.instance().getImagePreview( '%s/%s' % (logDirName,logSubDirName), 
                                            logFileName, projectId=projectId )
        else:
            self.resetPreview()
            
    def resetPreview(self):
        """
        Reset the preview widget
        """
        self.previewTab.setTabEnabled(TAB_XML_VERDICTS, False)
        self.previewTab.setTabEnabled(TAB_VERDICTS, False)
        self.previewTab.setTabEnabled(TAB_BASIC_REPORTS, False)
        self.previewTab.setTabEnabled(TAB_REPORTS, False)
        self.previewTab.setTabEnabled(TAB_IMAGES, False)
        self.previewTab.setTabEnabled(TAB_COMMENTS, False)
        
        self.previewTab.setCurrentIndex(TAB_REPORTS)   
        
        defaultTab = Settings.instance().readValue( key = 'TestArchives/default-report-tab' )
        self.previewTab.setCurrentIndex(int(defaultTab))   

        self.tabReports.deactive()
        self.tabBasicReports.deactive()
     
    def onGetTestPreview(self, content):
        """
        On get test preview
        """
        self.previewTab.setCurrentIndex(TAB_REPORTS)   
        
        defaultTab = Settings.instance().readValue( key = 'TestArchives/default-report-tab' )
        self.previewTab.setCurrentIndex(int(defaultTab))   

        self.previewTab.setTabEnabled(TAB_REPORTS, True)
        self.previewTab.setTabEnabled(TAB_BASIC_REPORTS, True)
        self.previewTab.setTabEnabled(TAB_IMAGES, False)
        self.previewTab.setTabEnabled(TAB_COMMENTS, True)
        
        # load reports
        if 'html-report' in content:
            self.tabReports.loadReports( self.decodeData(content['html-report']) )
        else:
            self.tabReports.loadReports( "No test report available" )
            self.previewTab.setTabEnabled(TAB_COMMENTS, False)
            
        # load comments
        if 'comments-report' in content:
            self.tabComments.onLoadComments(archivePath="", archiveComments=content['comments-report'])

        if 'csv-report' in content:
            self.previewTab.setTabEnabled(TAB_VERDICTS, True)
            self.tabVerdicts.loadVerdicts( self.decodeData(content['csv-report']) )
        else:
            self.tabVerdicts.loadVerdicts( "No test verdict available" )
            self.previewTab.setTabEnabled(TAB_VERDICTS, False)

        if 'xml-report' in content:
            self.previewTab.setTabEnabled(TAB_XML_VERDICTS, True)
            self.tabXmlVerdicts.loadVerdicts( self.decodeData(content['xml-report']) )
        else:
            self.tabXmlVerdicts.loadVerdicts( "No test verdict available" )
            self.previewTab.setTabEnabled(TAB_XML_VERDICTS, False)
            
        if 'html-basic-report' in content:
            self.tabBasicReports.loadReports( self.decodeData(content['html-basic-report']) )
        else:
            self.tabBasicReports.loadReports( "No basic test report available" )
            self.previewTab.setTabEnabled(TAB_BASIC_REPORTS, False)
        
    def decodeData(self, b64data):
        """
        Decode data
        """
        data = ''
        try:
            data_decoded = base64.b64decode(b64data)
        except Exception as e:
            self.error( 'unable to decode from base64 structure: %s' % str(e) )
        else:
            try:
                data = zlib.decompress(data_decoded)
                try:
                    data = data.decode('utf8')
                except UnicodeDecodeError as e:
                    data = data
            except Exception as e:
                self.error( 'unable to decompress: %s' % str(e) )
        return data
        
AR = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return AR

def initialize (parent, mainParent):
    """
    Initialize WArchives widget
    """
    global AR
    AR = WArchives(parent, mainParent)

def finalize ():
    """
    Destroy Singleton
    """
    global AR
    if AR:
        AR = None