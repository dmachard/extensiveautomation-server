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
Module to export the verdict
"""
from __future__ import print_function

import sys
import codecs

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QToolBar, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QVBoxLayout, QFont, QPrinter, QPrintDialog, QDialog, QFileDialog, QGroupBox, 
                            QCheckBox, QIcon, QTextDocument, QDialogButtonBox, QTabWidget, QTextEdit)
    from PyQt4.QtCore import (QSize, Qt)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon, QTextDocument)
    from PyQt5.QtWidgets import (QWidget, QToolBar, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                                QVBoxLayout, QDialog, QFileDialog, QTextEdit,
                                QGroupBox, QCheckBox, QDialogButtonBox, QTabWidget)
    from PyQt5.QtPrintSupport import (QPrinter, QPrintDialog)
    from PyQt5.QtCore import (QSize, Qt)
    
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
        Raw view widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.__data = data

        self.toCsv = toCsv
        self.toXml = toXml
        self.toCsv = toCsv
        self.toHtml = toHtml
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
        
        layout = QVBoxLayout()

        if self.toXml:
            self.txtEdit = QtHelper.RawXmlEditor(parent=self)
            self.txtEdit.setText( self.__data )
            # self.txtEdit.setUtf8(True)
            self.txtEdit.setFont( QFont("Courier", 9) )
        else:
            self.txtEdit = QtHelper.RawEditor(parent=self) 
            self.txtEdit.setTabStopWidth(10)
            self.txtEdit.setText( self.__data )
            self.txtEdit.setFont( QFont("Courier", 9) )

        self.txtEdit.setMinimumWidth(650)
        self.txtEdit.setMinimumHeight(400)


        self.delGroup = QGroupBox("Remove line")
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
        layout.addWidget( self.delGroup)
        layout.addWidget(self.txtEdit)
        if not self.toXml:
            self.rawFind = QtHelper.RawFind(parent=self, editor=self.txtEdit, buttonNext=True)
            layout.addWidget(self.rawFind)

        
        self.setLayout(layout)

    def createConnections(self):
        """
        All qt connections
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
        if self.toCsv: self.toolbar.addAction(self.saveCsvAction)
        if self.toTxt: self.toolbar.addAction(self.saveTxtAction)
        if self.toHtml:  self.toolbar.addAction(self.saveHtmlAction)
        if self.toPdf: self.toolbar.addAction(self.savePdfAction)
        if self.toXml: self.toolbar.addAction(self.saveXmlAction)
        if self.toPrinter: self.toolbar.addAction(self.toPrinterAction)
        self.toolbar.setIconSize(QSize(16, 16))

    def registerPlugin(self, pluginAction):
        """
        Register plugin
        """
        self.toolbarPlugins.addAction(pluginAction)
        self.toolbarPlugins.setIconSize(QSize(16, 16))
        self.pluginsBox.show()
        
    def onRemoveLines(self):
        """
        Called to remove lines
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
            doc = QTextDocument()
            doc.setPlainText( self.txtEdit.text() )
            doc.print_(printer)

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
                self.error('unable to save report file as html: %s' % str(e) )

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

class WExportVerdict(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Export verdict widget
    """
    def __init__(self, parent, data, dataXml): 
        """
        Constructs export verdict dialog

        @param parent: 
        @type parent:
        """     
        super(WExportVerdict, self).__init__(parent)

        self.__data = data
        self.__dataXml = dataXml

        self.createWidgets()
        self.createConnections()

    def pluginDataAccessor(self):
        """
        Return data for plugins
        """
        return {    
                    'verdict-csv': self.rawWidget.txtEdit.toPlainText(),
                    'verdict-xml': self.xmlWidget.txtEdit.text(),
               }
        
    def addPlugin(self, pluginAct):
        """
        Add plugins in widgets
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

        self.rawWidget = RawView(self, self.__data, toCsv=True, toHtml=False, 
                                toXml=False, toPrinter=True, toTxt=False, toPdf=True)
        self.xmlWidget = RawView(self, self.__dataXml, toCsv=False, toHtml=False, 
                                toXml=True, toPrinter=True, toTxt=False, toPdf=True)
        
        self.mainTab = QTabWidget()
        self.mainTab.addTab( self.rawWidget , 'Raw')
        self.mainTab.addTab( self.xmlWidget , 'Xml')

        layout.addWidget(self.mainTab)
        layout.addWidget(self.buttonBox)
        
        self.setWindowTitle("Export Test Verdict")
        self.setLayout(layout)

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)