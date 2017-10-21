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
__BUILDTIME__="27/05/2017 10:44:35"
# debug mode
DEBUGMODE=False

try:
    from PyQt4.QtGui import (QWidget, QApplication, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                             QLabel, QMessageBox)
    from PyQt4.QtCore import ( Qt, pyqtSignal )     
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                 QLabel, QMessageBox)
    from PyQt5.QtCore import ( Qt, pyqtSignal )   
    
from Core import CorePlugin
from Core import Settings
from Core.Libs import QtHelper, Logger

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

# List of types available for a plugin:
# - test-results
# - recorder-web
# - recorder-app
# - remote-tests

class MainPage(QWidget):
    """
    """
    def __init__(self, parent):
        """
        """
        super(MainPage, self).__init__()
        self.__core = parent
        
        if DEBUGMODE: self.core().debug().addLogWarning("Debug mode activated")
        self.createWidget()
        
    def core(self):
        """
        """
        return self.__core
        
    def createWidget(self):
        """
        """
        self.inDataEdit = QPlainTextEdit()
        
        exportButton = QPushButton("&Import")
        exportButton.clicked.connect(self.onImport)

        createTsLayout = QHBoxLayout()
        createTsLayout.addWidget(exportButton)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Imported/Exported json data: "))
        mainLayout.addWidget(self.inDataEdit)
        mainLayout.addLayout(createTsLayout)
        
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
        self.core().debug().addLogSuccess( "new data received: %s" % data)
        self.inDataEdit.setPlainText( "%s" % data)

    def onImport(self):
        """
        Export data
        """
        self.core().debug().addLogSuccess( "exporting data" )
        # import selenium example
        # {
            # "steps": [ 
                        # { "action-name": "OPEN BROWSER", "action-description": "", "action-params": "", "action-value": "https://www.google.fr"},
                        # { "action-name": "CLICK ELEMENT", "action-description": "", "action-params": "id=test", "action-value": ""}
                    # ]                
        # }
        
        # import sikuli example
        # {
            # "steps": [ 
                        # { "action-name": "CLICK ON",  "action-description": "", "image-base64": "iVBORw0KGgoAAAANSUhEUgAAAEgAAAAYCAIAAADWASznAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAASdEVYdFNvZnR3YXJlAEdyZWVuc2hvdF5VCAUAAAK9SURBVFhH3Zhda9NQGMdPk9565Y1XCvsOBkREEEEZCjIYjslATFDxZggKo+CFnyAbG2MX+hn2wpbdbrdt19LKKoTaObRpN0JWF/uWtjk+T3LSppkbZVCxefhdPOd/npfzH11hI1TdpZ+m6dwN+jo62oAFMKLu5vP5XC5HaGwsWDHSxMZs285mMsR+FQ0Z9POMruuk8zIaNmavWpZF2lI0fFBKifUiGj7QWPM5Hz7QWH2G/2c0t1VYaW8LAd1B6sAdVaygfhnQWPUZ/38gtR1jzaB+GdCYOcX3WFFwuBsludpVSqrz4/TEmIxHyPFWafy1cYpvpJngRnvFK0tLgdvOltBfrDQGWXG2xgNkUpnkGXNY19kUMF/GKZg7CdVkc5KvpTBtLbNKqrluldoFjSkJxF6jJ5qb+JlkLQyphXdKzT0OsiJQw+YgcCbGBOfyawOX9cWeaCw5T4FkgqvuYWotccZ7ZyJVquc39or9jd40f0tnQ3AeIFp4YjMHWRGo8QMq0Z9wLpV1bG6vC10FWXSekhQhN5OYNhc5/Z2Mvw+aXDm/sVfsz33TWO4GKmITM8V0JwywIlDjB2Ry/JhjLLiblNOu0hUTIuSnCUybC9zxW2diUTb8Nf2NxprzlDWhr9E3jeGOQoUZY0MGWBGs8QEyKY1zPWadUi/aq0Jp3pkYF+G2Ese0Me+VFWX9gsZx4XeRHd3ARm+avur7aHlzfKJSGWTF2RoPkEnxQWTI3DR/wqKtk6A+RNDYj/uR4SDWYTwL1XwTuB0usJIc3ouEDzR2cDcSMg4fXmm1WuTbnUjIOPo4jX9ofp+4nr9NQgPYsW07k8mQWmqn9OFp4dE19RYZacACGAE77J85X7LZcrlcr/u+w0YzwAIYATtfczlN08hBoZDb30+nUslEIhEfyYBnw+PBAhgBO0fl8olh/AEFAxxb9lhHWwAAAABJRU5ErkJggg==", "opt-c": "0.6" }
                    # ]                
        # }
        
        # import remote-tests
        # supported file PY_EXT, PNG_EXT, TXT_EXT, TEST_UNIT_EXT, TEST_SUITE_EXT, TEST_PLAN_EXT, TEST_GLOBAL_EXT, TEST_CONFIG_EXT, TEST_DATA_EXT
        # content must be encoded in base 64
        # {
            # "files": [ 
                        # { "file-path": "/A/B/test.tux", "content-file": "SGVsbG8gd29ybGQuIEJvbmpvdXIgw6Agdm91cyE="}     
                    # ]                       
        # }
        
        jsonStr = self.inDataEdit.toPlainText()
        try:
            jsonObj = json.loads(jsonStr)
        except Exception as e:
            QMessageBox.warning(self, "Plugin %s" % Settings.instance().readValue( key = 'Plugin/name' ), "Bad json message!" )
          
        if not DEBUGMODE: 
            self.core().sendMessage( cmd='import', data = jsonObj )
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