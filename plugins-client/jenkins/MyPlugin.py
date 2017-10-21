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
__BUILDTIME__="16/02/2017 19:32:33"
# debug mode
DEBUGMODE=False

try:
    from PyQt4.QtGui import (QWidget, QApplication, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                QMessageBox, QFileDialog,QAbstractItemView, QTableView, QTabWidget, QLabel,
                                QGridLayout, QGroupBox, QLineEdit, QDesktopServices )
    from PyQt4.QtCore import ( Qt, QObject, pyqtSignal, QAbstractTableModel, QModelIndex,
                                QAbstractTableModel, QUrl)         
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                 QMessageBox, QFileDialog, QAbstractItemView, QTableView, QTabWidget, QLabel,
                                 QGridLayout, QGroupBox, QLineEdit, QDesktopServices)
    from PyQt5.QtCore import ( Qt, QObject, pyqtSignal, QAbstractTableModel, QModelIndex,
                                QAbstractTableModel, QUrl)    
    
from Core import CorePlugin
from Core import Settings
from Core.Libs import QtHelper, Logger

import sys
import json
import threading
import sip
import base64

import copy

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


class MainPage(QWidget):
    """
    """
    def __init__(self, parent):
        """
        """
        super(MainPage, self).__init__()
        self.__core = parent

        if DEBUGMODE: self.core().debug().addLogWarning("Debug mode activated")
        
        # Create widget
        self.createWidget()
        self.createConnections()
        
    def onReloadSettings(self):
        """
        """
        pass
        
    def core(self):
        """
        """
        return self.__core

    def createConnections(self):
        """
        """
        self.getPlugin.clicked.connect( self.downloadPlugin )
        self.gotoLocal.clicked.connect( self.gotoLocalServer )
        
    def createWidget(self):
        """
        """
        self.getPlugin = QPushButton(self.tr("Download Plugin"), self)
        self.gotoLocal = QPushButton(self.tr("Go to jenkins homepage"), self)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.getPlugin)
        mainLayout.addWidget(self.gotoLocal)
        self.setLayout(mainLayout)
        
    def downloadPlugin(self):
        """
        """
        url = QUrl('https://wiki.jenkins-ci.org/display/JENKINS/ExtensiveTesting+Plugin')
        QDesktopServices.openUrl(url)
        
    def gotoLocalServer(self):
        """
        """
        url = QUrl('%s' % self.core().settings().config["jenkins-server"]["url"] )
        QDesktopServices.openUrl(url)
        
    def insertData(self, data):
        """
        """
        pass

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

        self.createWidgets()
        self.createConnections()
        
        self.loadCfg()
        
    def core(self):
        """
        """
        return self.__core

    def createConnections(self):
        """
        """
        self.saveButton.clicked.connect( self.saveCfg )

    def createWidgets(self):
        """
        """
        jenkinsSvrGroup = QGroupBox(self.tr("Jenkins server informations"))
        self.jenkinsSvrURL = QLineEdit()

        jenkinsSvrLayout = QGridLayout()
        jenkinsSvrLayout.addWidget( QLabel("URL"), 0, 0)
        jenkinsSvrLayout.addWidget( self.jenkinsSvrURL, 0, 1)
        jenkinsSvrGroup.setLayout(jenkinsSvrLayout)
        
        layoutCtrls = QHBoxLayout()
        self.saveButton = QPushButton(self.tr("Save Settings"), self)
        layoutCtrls.addWidget(self.saveButton)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(jenkinsSvrGroup)
        mainLayout.addLayout(layoutCtrls)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        
    def loadCfg(self):
        """
        """
        with open( "%s/config.json" % (QtHelper.dirExec()) ) as f:
            CONFIG_RAW = f.read()
        self.config = json.loads(CONFIG_RAW)

        self.jenkinsSvrURL.setText(self.config["jenkins-server"]["url"])

    def saveCfg(self):
        """
        """
        if not len(self.jenkinsSvrURL.text()):
            QMessageBox.warning(self, self.tr("Save Settings") , self.tr("Please to set the server url") )
            return

        self.config["jenkins-server"]["url"] = self.jenkinsSvrURL.text()

        with open( "%s/config.json" % (QtHelper.dirExec()), "w" ) as f:
            f.write( json.dumps(self.config) )

        self.ReloadSettings.emit()

        QMessageBox.information(self, self.tr("Save Settings") ,  self.tr("Settings saved.") )
 
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
                        pluginDescription=WidgetSettings.cfg()["plugin"]["description"],
                        showMaximized=WidgetSettings.cfg()["plugin"]["show-maximized"]
                       )

    lic = LICENSE % (WidgetSettings.cfg()["plugin"]["name"], 
                    WidgetSettings.cfg()["plugin"]["version"],
                    name, ','.join(__CONTRIBUTORS__) )   
    aboutPage = "<br/><br/><b>License:</b><br /><span>%s</span>" % lic
    MyPlugin.updateAboutPage(text=aboutPage)

    # debug mode
    if DEBUGMODE: 
        if WidgetSettings.cfg()["plugin"]["show-maximized"]:
            MyPlugin.showMaximized()
        else:
            MyPlugin.show()
            
    sys.exit(app.exec_())