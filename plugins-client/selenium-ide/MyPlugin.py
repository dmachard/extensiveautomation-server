#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2017 Denis Machard
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
#
# Gfi Informatique, Inc., hereby disclaims all copyright interest in the
# extensive testing project written by Denis Machard
# 
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

"""
Main module 
"""
# to support new print style on python 2.x
from __future__ import print_function 

# name of the main developer
__AUTHOR__ = 'Denis Machard'
# email of the main developer
__EMAIL__ = 'd.machard@gmail.com'
# list of contributors
__CONTRIBUTORS__ = [ "" ]
# list of contributors
__TESTERS__ = [ "" ]
# project start in year
__BEGIN__="2016"
# year of the latest build
__END__="2017"
# date and time of the buid
__BUILDTIME__="16/02/2017 19:32:43"
# debug mode
DEBUGMODE=False

try:
    from PyQt4.QtGui import (QWidget, QApplication, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                QMessageBox, QFileDialog, QLabel, QAbstractItemView, QTableView)
    from PyQt4.QtCore import ( QFile, Qt, QIODevice, pyqtSignal, QAbstractTableModel, QModelIndex)                             
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                 QMessageBox, QFileDialog, QLabel, QAbstractItemView, QTableView)
    from PyQt5.QtCore import ( QFile, Qt, QIODevice, pyqtSignal, QAbstractTableModel, QModelIndex)    
    
from Core import CorePlugin
from Core import Settings
from Core.Libs import QtHelper, Logger

import SeleniumParser

import sys
import json
import sip
import os

# adding missing folders
if not os.path.exists( "%s/Core/Logs/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Core/Logs" % QtHelper.dirExec() )

LICENSE = """<br />
%s plugin <b>%s</b> for the <b>%s</b><br />
Developed and maintained by <b>Denis Machard</b><br />
Contributors: <b>%s</b><br />
<br />
This program is free software; you can redistribute it and/or<br />
modify it under the terms of the GNU Lesser General Public<br />
License as published by the Free Software Foundation; either<br />
version 2.1 of the License, or (at your option) any later version.<br />
<br />
This library is distributed in the hope that it will be useful,<br />
but WITHOUT ANY WARRANTY; without even the implied warranty of<br />
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU<br />
Lesser General Public License for more details.<br />
<br />
You should have received a copy of the GNU Lesser General Public<br />
License along with this library; if not, write to the Free Software<br />
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,<br />
MA 02110-1301 USA<br />
"""

COL_ACTION              =   0
COL_TARGET              =   1
COL_VALUE               =   2

HEADERS             = ( 'Action', 'Target', 'Value' )
 
class ActionsTableModel(QAbstractTableModel):
    """
    Table model for parameters
    """
    def __init__(self, parent, core):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        
        self.mydata = []
        self.owner = parent
        self.__core = core
        self.nbCol = len(HEADERS)

    def core(self):
        """
        """
        return self.__core
        
    def getData(self):
        """
        Return model data

        @return:
        @rtype:
        """
        return self.mydata

    def getValueRow(self, index):
        """
        Return all current values of the row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        return self.mydata[ index.row() ]

    def setDataModel(self, data):
        """
        Set model data

        @param data: 
        @type data:
        """
        self.mydata = data
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, qindex=QModelIndex()):
        """
        Array column number
    
        @param qindex: 
        @type qindex:

        @return:
        @rtype:
        """
        return self.nbCol

    def rowCount(self, qindex=QModelIndex()):
        """
        Array row number
    
        @param qindex: 
        @type qindex:
    
        @return:
        @rtype:
        """
        return len( self.mydata )
  
    def getValue(self, index):
        """
        Return current value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.column() == COL_ACTION:
            return self.mydata[ index.row() ]['action-name']
        elif index.column() == COL_TARGET:
            return self.mydata[ index.row() ]['action-params']
        elif index.column() == COL_VALUE:
            return self.mydata[ index.row() ]['action-value']
        else:
            pass
        
    def data(self, index, role=Qt.DisplayRole):
        """
        Cell content

        @param index: 
        @type index:

        @param role: 
        @type role:

        @return:
        @rtype:
        """
        if not index.isValid(): return None
        value = self.getValue(index)
        
        if role == Qt.DisplayRole:
            return value
        elif role == Qt.EditRole:
            return value
            
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Overriding method headerData

        @param section: 
        @type section:

        @param orientation: 
        @type orientation:

        @param role: 
        @type role:

        @return:
        @rtype:
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[section]

        return None

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        if index.column() == COL_TARGET:
            self.mydata[ index.row() ]['action-params'] = value
        elif index.column() == COL_VALUE:
            self.mydata[ index.row() ]['action-value'] = value

    def setData(self, index, value, role=Qt.EditRole):
        """
        Cell content change

        @param index: 
        @type index:

        @param value: 
        @type value:

        @param role: 
        @type role:

        @return:
        @rtype:
        """
        if not index.isValid(): return False
        value = QtHelper.displayToValue( value )
        self.setValue(index, value)
        return True

    def flags(self, index):
        """
        Overriding method flags

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == COL_ACTION:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
     
class ActionsTableView(QTableView):
    def __init__(self, parent, core):
        """
        """
        QTableView.__init__(self, parent)
        self.__core = core
        
        self.createWidgets()
        self.createConnections()
    
    def core(self):
        """
        """
        return self.__core
        
    def createConnections(self):
        """
        """
        self.clicked.connect( self.onAbstractItemClicked) 
        
    def createWidgets(self):
        """
        """
        self.model = ActionsTableModel(self, core=self.core())
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)

    def onAbstractItemClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return

    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in range(len(data)):
            self.resizeRowToContents(row)
    
    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_ACTION, COL_TARGET, COL_VALUE]:
            self.resizeColumnToContents(col)

    def clear(self):
        """
        Clear all widget
        """
        self.model.setDataModel( [] )
        
    def loadTable (self, data):
        """
        Load data

        @param data: 
        @type data:
        """
        self.model.setDataModel( data )
        
        self.adjustRows()
        self.adjustColumns()
   
   
class MainPage(QWidget):
    """
    """
    def __init__(self, parent):
        """
        """
        super(MainPage, self).__init__()
        self.__core = parent

        if DEBUGMODE: self.core().debug().addLogWarning("Debug mode activated")
        
        self.createWidgets()
        self.createConnections()
        
    def core(self):
        """
        """
        return self.__core
    
    def createConnections(self):
        """
        """
        self.readButton.clicked.connect(self.onRead)
        self.exportButton.clicked.connect(self.onImport)

    def createWidgets(self):
        """
        """
        self.readButton = QPushButton("&Read SeleniumIDE\n(HTML File)")
        self.exportButton = QPushButton("&Import in %s" % Settings.instance().readValue( key = 'Common/product-name' ))
        self.exportButton.setEnabled(False)
        
        self.actsTable = ActionsTableView(self, core=self.core())
        
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(QLabel("Controls"))
        rightLayout.addWidget(self.readButton)
        rightLayout.addWidget(self.exportButton)
        rightLayout.addStretch(1)
        
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(QLabel("Actions"))
        leftLayout.addWidget(self.actsTable)
        
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        
        self.setLayout(mainLayout)
        
    def onReloadSettings(self):
        """
        Called by the core when settings are updated
        """
        pass
        
    def insertData(self, data):
        """
        Called by the core when new data are received
        """
        pass

    def onRead(self):
        """
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open SeleniumIDE file"),
                            '', "HTML (*.html)")
        if not len(fileName):
            return

        # read the file
        file = QFile(fileName)
        if not file.open(QIODevice.ReadOnly):
            QMessageBox.warning(self, self.tr("Error opening html file"), self.tr("Could not open the file ") + fileName)
            return

        htmlPage = file.readAll()
        parser = SeleniumParser.SeleniumIDEParser()
        
        # unescape html
        htmlPage = htmlPage.replace("&quot;", "\"")
        
        # feed the page in the parser
        parser.feed( str(htmlPage, "utf8")  )
        
        self.core().debug().addLogWarning( "ide support: %s" % parser.ide_supported )
        self.core().debug().addLogWarning( "url: %s" % parser.ide_url )
        
        if not parser.ide_supported:
            QMessageBox.critical(self, self.tr("Error opening html file"), "File not supported" )
            return
        else:
            steps = []
            try:
                for act in parser.ide_actions:
                    a, c, v = act
                    stp = {}
                    for m in self.core().settings().cfg()["mapping"] :
                        if a == "select":
                            if v.startswith("label="):
                                a = "selectByText"
                            else:
                                a = "selectByValue"
                                
                        if m["src"] == a:
                            stp["action-name"] = m["dst"]
                            stp["action-description"] = ""
                            stp["action-params"] = c
                            stp["action-value"] = v
                            if a == "open": stp["action-value"] = parser.ide_url
                            if a == "selectByText": 
                                if v.startswith("label="): 
                                    stp["action-value"] = v.split("label=")[1]
                            if a == "selectByValue":
                                if v.startswith("value="):
                                    stp["action-value"] = v.split("value=")[1]
                                    
                    if len(stp): steps.append(stp)
            except Exception as e:
                self.core().debug().addLogError( "%s - %s" % (e, parser.ide_actions) )
                QMessageBox.critical(self, self.tr("Error opening html file"), "Parser error, more details in debug page." )
                return
            else:
                self.actsTable.loadTable(data=steps)
                if len(steps): self.exportButton.setEnabled(True)
        
    def onImport(self):
        """
        """
        actions = self.actsTable.model.getData()
        if DEBUGMODE: self.core().debug().addLogWarning("List actions to import: %s" % actions)
        
        if not DEBUGMODE: 
            self.core().sendMessage( cmd='import', data = {"steps": actions} )
            self.core().hide()
        
class SettingsPage(QWidget):
    """
    """
    ReloadSettings = pyqtSignal()
    def __init__(self, parent):
        """
        """
        super(SettingsPage, self).__init__()
        self.__core = parent
        self.config = None
        
        self.createWidget()
        self.loadCfg()

    def createWidget(self):
        """
        """
        self.inDataEdit = QPlainTextEdit("No settings!")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.inDataEdit)

        self.setLayout(mainLayout)
        
    def loadCfg(self):
        """
        """
        with open( "%s/config.json" % (QtHelper.dirExec()) ) as f:
            CONFIG_RAW = f.read()
        self.config = json.loads(CONFIG_RAW)
        
    def cfg(self):
        """
        """
        return self.config

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # initiliaze settings application, read settings from the ini file
    Settings.initialize()
    
    # initialize logger
    logPathFile = "%s/%s" % ( QtHelper.dirExec(), Settings.instance().readValue( key = 'Trace/file' ) )
    level = Settings.instance().readValue( key = 'Trace/level' )
    size = Settings.instance().readValue( key = 'Trace/max-size-file' )
    nbFiles = int( Settings.instance().readValue( key = 'Trace/nb-backup-max' ) )
    Logger.initialize( logPathFile=logPathFile, level=level, size=size, nbFiles=nbFiles, noSettings=True )
    
    
    # init the core plugin
    MyPlugin = CorePlugin.MainWindow(debugMode=DEBUGMODE)
   
    # create the main  widget   
    WidgetSettings = SettingsPage(parent=MyPlugin)
    MyPlugin.addSettingsPage( widget=WidgetSettings )

    WidgetMain = MainPage(parent=MyPlugin) 
    MyPlugin.addMainPage(  
                            pageName=WidgetSettings.cfg()["plugin"]["name"], 
                            widget=WidgetMain
                        )
                        
                        
    # register the main and settings page of the plugin
    name = Settings.instance().readValue( key = 'Common/name' )
    MyPlugin.configure(
                        pluginName=WidgetSettings.cfg()["plugin"]["name"], 
                        pluginType=WidgetSettings.cfg()["plugin"]["type"],
                        pluginVersion=WidgetSettings.cfg()["plugin"]["version"],
                        pluginDescription=WidgetSettings.cfg()["plugin"]["description"]
                       )

    lic = LICENSE % (WidgetSettings.cfg()["plugin"]["name"], 
                    WidgetSettings.cfg()["plugin"]["version"],
                    name, ','.join(__CONTRIBUTORS__) )   
    aboutPage = "<br/><br/><b>License:</b><br /><span>%s</span>" % lic
    MyPlugin.updateAboutPage(text=aboutPage)
    
    # debug mode
    if DEBUGMODE: 
        MyPlugin.show()
        #MyPlugin.showMaximized()
    
    sys.exit(app.exec_())