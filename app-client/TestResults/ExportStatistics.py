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
Module to export statistics of a test
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QToolBar, QVBoxLayout, QFont, QIcon, QPrinter, 
                            QPrintDialog, QDialog, QTextDocument, QFileDialog, 
                            QDialogButtonBox, QTabWidget)
    from PyQt4.QtCore import (Qt, QSize)
    from PyQt4.Qsci import (QsciScintilla, QsciLexerXML)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon, QTextDocument)
    from PyQt5.QtWidgets import (QWidget, QToolBar, QVBoxLayout, QDialog, QFileDialog, 
                                QDialogButtonBox, QTabWidget)
    from PyQt5.QtCore import (Qt, QSize)
    from PyQt5.Qsci import (QsciScintilla, QsciLexerXML)
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
    def __init__(self, parent, data, toCsv=False, toHtml=False, toXml=False, 
                 toPrinter=False, toTxt=False, toPdf=False):
        """
        Raw view widgets

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
        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        layout = QVBoxLayout()

        if self.toXml:
            self.txtEdit = QtHelper.RawXmlEditor(parent=self)
            self.txtEdit.setFolding( QsciScintilla.BoxedTreeFoldStyle)
            self.txtEdit.setLexer( QsciLexerXML() )
            self.txtEdit.setText( self.__data )
            self.txtEdit.setUtf8(True)
            self.txtEdit.setFont( QFont("Courier", 9) )
        else:
            self.txtEdit = QtHelper.RawEditor(parent=self) 
            self.txtEdit.setTabStopWidth(10)
            self.txtEdit.setText( self.__data )
            self.txtEdit.setFont( QFont("Courier", 9) )

        self.txtEdit.setMinimumWidth(650)
        self.txtEdit.setMinimumHeight(400)     
        
        layout.addWidget(self.toolbar)
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
        if self.toTxt:
            self.toolbar.addAction(self.saveTxtAction)
            self.toolbar.addSeparator()
        if self.toHtml:
            self.toolbar.addAction(self.saveHtmlAction)
            self.toolbar.addSeparator()
        if self.toPdf:
            self.toolbar.addAction(self.savePdfAction)
            self.toolbar.addSeparator()
        if self.toXml:
            self.toolbar.addAction(self.saveXmlAction)
            self.toolbar.addSeparator()
        if self.toPrinter:
            self.toolbar.addAction(self.toPrinterAction)
            self.toolbar.addSeparator()
        self.toolbar.setIconSize(QSize(16, 16))



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
                self.error('unable to save design file as txt: %s' % str(e) )

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
                f = open( _filename, 'w'  )
                f.write( self.txtEdit.text() )
                f.close()
            except Exception as e:
                self.error('unable to save design file as xml: %s' % str(e) )

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
            try:
                f = open( _filename, 'w'  )
                f.write( self.txtEdit.toHtml() )
                f.close()
            except Exception as e:
                self.error('unable to save design file as html: %s' % str(e) )

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

class WExportStatistics(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Export statistics dialog
    """
    def __init__(self, parent, dataXml): 
        """
        Constructs export statistics dialog

        @param parent: 
        @type parent:
        """     
        super(WExportStatistics, self).__init__(parent)

        self.__dataXml = dataXml

        self.createWidgets()
        self.createConnections()

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

        self.xmlWidget = RawView(self, self.__dataXml, toCsv=False, toHtml=False, 
                                 toXml=True, toPrinter=True, toTxt=False, toPdf=True)
        
        layout = QVBoxLayout()
        self.mainTab = QTabWidget()
        self.mainTab.addTab(  self.xmlWidget, 'Xml')

        layout.addWidget(self.mainTab)
        layout.addWidget(self.buttonBox)
        
        self.setWindowTitle("Export Test Statistics")
        self.setLayout(layout)

    def createConnections (self):
        """
        Qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
