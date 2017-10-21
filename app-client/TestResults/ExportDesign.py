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
Module to export the design of a test
"""
import sys
import codecs

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QToolBar, QVBoxLayout, QFont, QIcon, QPrinter, QPrintDialog, QHBoxLayout, 
                            QDialog, QTextDocument, QFileDialog, QDialogButtonBox, QTabWidget, QGroupBox)
    from PyQt4.QtCore import (Qt, QSize, QByteArray)
    from PyQt4.QtWebKit import (QWebView)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon, QTextDocument)
    from PyQt5.QtWidgets import (QWidget, QToolBar, QVBoxLayout, QGroupBox, QHBoxLayout,
                                QDialog, QFileDialog, QDialogButtonBox, QTabWidget)
    from PyQt5.QtCore import (Qt, QSize, QByteArray)
    from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
    from PyQt5.QtPrintSupport import (QPrinter, QPrintDialog)
    
import UserClientInterface as UCI
from Libs import QtHelper, Logger
import Settings

import base64
import zlib

class RawView(QWidget, Logger.ClassLogger):
    """
    Raw view widget
    """
    def __init__(self, parent, data, toCsv=False, toHtml=False, toXml=False, toPrinter=False, toTxt=False, toPdf=False):
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
        self.toHtml = toHtml
        self.toPrinter = toPrinter
        self.toTxt = toTxt
        self.toPdf = toPdf

        self.createWidgets()
        self.createActions()
        self.createToolbars()

    def createWidgets (self):
        """
        Create qt widgets
        """
        # prepare menu
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
        self.exportBox.setMaximumHeight(70)
        
        layout = QVBoxLayout()

        if self.toXml:
            self.txtEdit = QtHelper.RawXmlEditor(parent=self)
            self.txtEdit.setText( self.__data )
            self.txtEdit.setUtf8(True)
            self.txtEdit.setFont( QFont("Courier", 9) )
        else:
            self.txtEdit = QWebView(parent=self)
            # convert to qbyte array to support qt5
            tmp_ = QByteArray()
            tmp_.append(self.__data)
            
            self.txtEdit.setContent( tmp_, "text/html; charset=utf-8") 

        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.exportBox)
        layoutToolbars.addWidget(self.pluginsBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        layout.addLayout(layoutToolbars)
        layout.addWidget(self.txtEdit)

        self.setLayout(layout)

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
        self.saveXmlAction = QtHelper.createAction(self, "&To XML", self.saveXml, 
                                tip = 'Save to XML file', icon = QIcon(":/xml.png") )
        self.toPrinterAction = QtHelper.createAction(self, "&To Printer", self.savePrinter, 
                                tip = 'Print', icon = QIcon(":/printer.png") )

    def createToolbars(self):
        """
        Toolbar creation
        """
        self.toolbar.setObjectName("Export toolbar")
        if self.toTxt: self.toolbar.addAction(self.saveTxtAction)
        if self.toHtml: self.toolbar.addAction(self.saveHtmlAction)
        if self.toPdf:  self.toolbar.addAction(self.savePdfAction)
        if self.toXml: self.toolbar.addAction(self.saveXmlAction)
        if self.toPrinter: self.toolbar.addAction(self.toPrinterAction)
        self.toolbar.setIconSize(QSize(16, 16))

    def registerPlugin(self, pluginAction):
        """
        """
        self.toolbarPlugins.addAction(pluginAction)
        self.toolbarPlugins.setIconSize(QSize(16, 16))
        self.pluginsBox.show()
        
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


    def saveTxt(self):
        """
        Save to txt file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save TXT file", "", "TXT file (*.txt);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = filename
        else:
            _filename = filename
        # end of new
        
        if _filename:
            try:
                frame = self.txtEdit.page().mainFrame()
                with codecs.open(_filename, "w", "utf-8") as f:
                    f.write( frame.toPlainText()  )
            except Exception as e:
                self.error('unable to save design file as txt: %s' % str(e) )

    def saveXml(self):
        """
        Save to xml file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save XML file", "", "XML file (*.xml);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = filename
        else:
            _filename = filename
        # end of new
        
        if _filename:
            try:
                with codecs.open(_filename, "w", "utf-8") as f:
                    f.write( self.txtEdit.text()  )
            except Exception as e:
                self.error('unable to save design file as xml: %s' % str(e) )

    def saveHtml(self):
        """
        Save to html file
        """
        fileName = QFileDialog.getSaveFileName(self, "Save HTML file", "", "HTML file (*.html);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = filename
        else:
            _filename = filename
        # end of new
        
        if _filename:
            frame = self.txtEdit.page().mainFrame()
            try:
                with codecs.open(_filename, "w", "utf-8") as f:
                    f.write( frame.toHtml()  )
            except Exception as e:
                self.error('unable to save design file as html: %s' % str(e) )

    def savePdf(self):
        """
        Save to pdf file
        """
        filename = QFileDialog.getSaveFileName(self, 'Save to PDF', "", "PDF file (*.pdf);;All Files (*.*)")
        
        # new in v17.1
        if QtHelper.IS_QT5:
            _filename, _type = filename
        else:
            _filename = filename
        # end of new 
        
        if _filename:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setColorMode(QPrinter.Color)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(_filename)

            if isinstance(self.txtEdit, QWebView):
                self.txtEdit.print_(printer)
            else:
                doc = QTextDocument()
                if self.toXml:
                    doc.setPlainText( self.txtEdit.text())
                else:
                    doc.setHtml( self.txtEdit.toHtml() )
                doc.print_(printer)
                
class WExportDesign(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Export design widget
    """
    def __init__(self, parent, data, dataXml): 
        """
        Constructs export design dialog

        @param parent: 
        @type parent:
        """     
        super(WExportDesign, self).__init__(parent)

        self.__data = ''
        self.__dataXml = ''
        self.decodeData(data)
        self.decodeDataXml(dataXml)

        self.createWidgets()
        self.createConnections()

    def decodeData(self, b64data):
        """
        Decode data
        """
        try:
            data_decoded = base64.b64decode(b64data)
        except Exception as e:
            self.error( 'unable to decode from base64 structure design: %s' % str(e) )
        else:
            try:
                self.__data = zlib.decompress(data_decoded)
                try:
                    self.__data = self.__data.decode('utf8')
                except UnicodeDecodeError as e:
                    self.__data = self.__data
            except Exception as e:
                self.error( 'unable to decompress design: %s' % str(e) )

    def decodeDataXml(self, b64data):
        """
        Decode data xml
        """
        try:
            data_decoded = base64.b64decode(b64data)
        except Exception as e:
            self.error( 'unable to decode from base64 structure design: %s' % str(e) )
        else:
            try:
                self.__dataXml = zlib.decompress(data_decoded)
                try:
                    self.__dataXml = self.__dataXml.decode('utf8')
                except UnicodeDecodeError as e:
                    self.__dataXml = self.__dataXml
            except Exception as e:
                self.error( 'unable to decompress design: %s' % str(e) )

    def pluginDataAccessor(self):
        """
        """
        frame = self.rawWidget.txtEdit.page().mainFrame()
        
        return {
                    'design-html': frame.toHtml(),
                    'design-xml': self.xmlWidget.txtEdit.text()
                }
        
    def addPlugin(self, pluginAct):
        """
        """
        self.rawWidget.registerPlugin(pluginAct)
        self.xmlWidget.registerPlugin(pluginAct)
  
    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)


        layout = QVBoxLayout()
        self.mainTab = QTabWidget()
        
        self.rawWidget = RawView(self, self.__data, toCsv=True, toHtml=True, toXml=False, toPrinter=True, toTxt=True, toPdf=True)
        self.xmlWidget = RawView(self, self.__dataXml, toCsv=False, toHtml=False, toXml=True, toPrinter=True, toTxt=False, toPdf=True)
        self.mainTab.addTab( self.rawWidget , 'Raw')
        self.mainTab.addTab( self.xmlWidget , 'Xml')

        layout.addWidget(self.mainTab)
        layout.addWidget(self.buttonBox)
        
        self.setWindowTitle("Export Test Design")
        self.setLayout(layout)

    def createConnections (self):
        """
        Qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
