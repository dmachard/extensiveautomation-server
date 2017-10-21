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
__CONTRIBUTORS__ = [ "Emmanuel Monsoro" ]
# list of contributors
__TESTERS__ = [ "Emmanuel Monsoro" ]
# project start in year
__BEGIN__="2016"
# year of the latest build
__END__="2017"
# date and time of the buid
__BUILDTIME__="27/05/2017 15:17:02"
# debug mode
DEBUGMODE=False

try:
    from PyQt4.QtGui import (QWidget, QApplication, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                QMessageBox, QFileDialog,QAbstractItemView, QTableView, QTabWidget, QLabel,
                                QGridLayout, QGroupBox, QLineEdit, QCheckBox, QRadioButton  )
    from PyQt4.QtCore import ( Qt, QObject, pyqtSignal, QAbstractTableModel, QModelIndex,
                                QAbstractTableModel, QFile )         
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                 QMessageBox, QFileDialog, QAbstractItemView, QTableView, QTabWidget, QLabel,
                                 QGridLayout, QGroupBox, QLineEdit, QCheckBox, QRadioButton )
    from PyQt5.QtCore import ( Qt, QObject, pyqtSignal, QAbstractTableModel, QModelIndex,
                                QAbstractTableModel, QFile)    
    
from Core import CorePlugin
from Core import Settings
from Core.Libs import QtHelper, Logger

import RestAPI
# import ComAPI
import DesignPage
import VerdictPage

import sys
import json
import threading
import sip
# from Crypto.Cipher import XOR
import base64

import copy

import os

# adding missing folders
if not os.path.exists( "%s/Core/Logs/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Core/Logs" % QtHelper.dirExec() )

    
LICENSE = """<br />
&nbsp;&nbsp;%s plugin <b>%s</b> for the <b>%s</b><br />
&nbsp;&nbsp;Developed and maintained by <b>Denis Machard</b><br />
&nbsp;&nbsp;Contributors: <b>%s</b><br />
&nbsp;&nbsp;<br />
&nbsp;&nbsp;This program is free software; you can redistribute it and/or<br />
&nbsp;&nbsp;modify it under the terms of the GNU Lesser General Public<br />
&nbsp;&nbsp;License as published by the Free Software Foundation; either<br />
&nbsp;&nbsp;version 2.1 of the License, or (at your option) any later version.<br />
&nbsp;&nbsp;<br />
&nbsp;&nbsp;This library is distributed in the hope that it will be useful,<br />
&nbsp;&nbsp;but WITHOUT ANY WARRANTY; without even the implied warranty of<br />
&nbsp;&nbsp;MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU<br />
&nbsp;&nbsp;Lesser General Public License for more details.<br />
&nbsp;&nbsp;<br />
&nbsp;&nbsp;You should have received a copy of the GNU Lesser General Public<br />
&nbsp;&nbsp;License along with this library; if not, write to the Free Software<br />
&nbsp;&nbsp;Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,<br />
&nbsp;&nbsp;MA 02110-1301 USA<br />
"""
    
TAB_DESIGN_PAGE = 0
TAB_VERDICT_PAGE = 1

class MainPage(QWidget):
    """
    """
    def __init__(self, parent):
        """
        """
        super(MainPage, self).__init__()
        self.__core = parent

        if DEBUGMODE: self.core().debug().addLogWarning("Debug mode activated")
    
        # COM object
        # self.ComALM = ComAPI.ComHpAlmClient( parent=self, core=parent )

        # REST api
        self.RestHP = RestAPI.RestHpAlmClient(parent=self, core=parent)
                                        
        # Create widget
        self.createWidget()
        self.createConnections()
        
    def core(self):
        """
        """
        return self.__core

    def createConnections(self):
        """
        """
        self.designPage.ExportTests.connect(self.onExportTests)
        self.verdictPage.ExportResults.connect(self.onExportResults)

        # self.ComALM.Error.connect(self.onComError)
        # self.ComALM.ConnectionOk.connect(self.onTestedConnectionOk)
        # self.ComALM.TestsExported.connect(self.onTestsExported)
        # self.ComALM.ResultsExported.connect(self.onResultsExported)
        # self.ComALM.LogTestsStatus.connect(self.onLogTestsStatus)
        # self.ComALM.LogResultsStatus.connect(self.onLogResultsStatus)

        self.RestHP.Error.connect(self.onRestError)
        self.RestHP.ConnectionOk.connect(self.onTestedConnectionOk)
        self.RestHP.LogAuthStatus.connect(self.onLogAuthStatus)
        self.RestHP.TestsExported.connect(self.onTestsExported)
        self.RestHP.ResultsExported.connect(self.onResultsExported)
        self.RestHP.LogTestsStatus.connect(self.onLogTestsStatus)
        self.RestHP.LogResultsStatus.connect(self.onLogResultsStatus)
        
    def createWidget(self):
        """
        """
        self.mainTab = QTabWidget()
        
        self.designPage = DesignPage.DesignPage(parent=self, core=self.core(), debugMode=DEBUGMODE)
        self.verdictPage = VerdictPage.VerdictPage(parent=self, core=self.core(), debugMode=DEBUGMODE)
        
        self.mainTab.addTab( self.designPage, "Export Test(s)")
        self.mainTab.addTab( self.verdictPage, "Export Result(s)")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.mainTab)
        self.setLayout(mainLayout)
        
    def onReloadSettings(self):
        """
        """
        # update network api interface to reload credentials
        self.RestHP.loadConfig()
        # self.ComALM.loadConfig()
        
    def insertData(self, data):
        """
        """
        if "verdict-xml" in data.keys():
            self.mainTab.setTabEnabled(TAB_DESIGN_PAGE, False)
            self.mainTab.setTabEnabled(TAB_VERDICT_PAGE, True)
            self.verdictPage.readXml(rawXml=data['verdict-xml'])
        elif "design-xml" in data.keys():
            self.mainTab.setTabEnabled(TAB_DESIGN_PAGE, True)
            self.mainTab.setTabEnabled(TAB_VERDICT_PAGE, False)
            self.designPage.readXml(rawXml=data['design-xml'])
        else:
            self.mainTab.setTabEnabled(TAB_DESIGN_PAGE, False)
            self.mainTab.setTabEnabled(TAB_VERDICT_PAGE, False)
    
    def onLogAuthStatus(self, status):
        """
        """
        self.core().debug().addLogSuccess(status)

    def onLogTestsStatus(self, status):
        """
        """
        self.core().debug().addLogSuccess(status)
        self.designPage.logStatus(status)

    def onLogResultsStatus(self, status):
        """
        """
        self.core().debug().addLogSuccess(status)
        self.verdictPage.logStatus(status)

    def onExportResults(self, testcases, config):
        """
        """
        funcArgs = { 'testcases': testcases, 'config': config  }
        
        # target = self.ComALM.addResultsInTestLab
        # if self.core().settings().cfg()["qc-server"]["use-rest"]:
        target = self.RestHP.addResultsInTestLab
            
        t = threading.Thread(target=target, kwargs=funcArgs )
        t.start()
        
    def onExportTests(self, testcases, config):
        """
        """
        funcArgs = { 'testcases': testcases, 'config': config  }
        
        # target = self.ComALM.addTestsInTestPlan
        # if self.core().settings().cfg()["qc-server"]["use-rest"]:
        target = self.RestHP.addTestsInTestPlan
            
        t = threading.Thread(target=target, kwargs=funcArgs )
        t.start()

    def onTestsExported(self):
        """
        """
        self.designPage.enableExport()    
        QMessageBox.information(self, self.tr("Export Test(s)") , 
                                self.tr("Test(s) exported with success.") )
    
    def onResultsExported(self):
        """
        """
        self.verdictPage.enableExport()    
        QMessageBox.information(self, self.tr("Export Result(s)") , 
                                self.tr("Result(s) exported with success.") )

    def onComError(self, err):
        """
        """
        self.designPage.enableExport()
        self.verdictPage.enableExport()
        self.core().debug().addLogError( "COM Generic: %s" % err)
        QMessageBox.critical(self, self.tr("Com Error") , "%s" % err )
        
    def onRestError(self, err):
        """
        """
        self.designPage.enableExport()
        self.verdictPage.enableExport()
        self.core().debug().addLogError( "REST Generic: %s" % err)
        QMessageBox.critical(self, self.tr("Rest Error") , "%s" % err )
    
    def onTestedConnectionOk(self):
        QMessageBox.information(self, self.tr("Test Connection") , 
                                self.tr("Connection test successful !") )
    
    def testConnection(self, config):
        funcArgs = { 'config': config  }
        
        # target = self.ComALM.testConnection
        # if self.core().settings().cfg()["qc-server"]["use-rest"]:
        target = self.RestHP.testConnection
            
        t = threading.Thread(target=target, kwargs=funcArgs )
        t.start()
        
class SettingsPage(QWidget):
    """
    """
    ReloadSettings = pyqtSignal()
    TestSettings = pyqtSignal(dict) 
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
        self.saveButton.clicked.connect( self.__saveCfg )
        self.testButton.clicked.connect( self.testConnection )
        
    def createWidgets(self):
        """
        """
        qcCredGroup = QGroupBox(self.tr("HP ALM server credentials"))
        self.hpCredLogin = QLineEdit()
        self.hpCredPwd = QLineEdit()
        self.hpCredPwd.setEchoMode(QLineEdit.Password)
        qcCredLayout = QGridLayout()
        qcCredLayout.addWidget( QLabel("Login"), 0, 0)
        qcCredLayout.addWidget( self.hpCredLogin, 0, 1)
        qcCredLayout.addWidget( QLabel("Password"), 1, 0)
        qcCredLayout.addWidget( self.hpCredPwd, 1, 1)
        qcCredGroup.setLayout(qcCredLayout)
        
        qcSvrGroup = QGroupBox(self.tr("HP ALM server informations"))
        self.hpSvrURL = QLineEdit()
        self.hpSvrDomain = QLineEdit()
        self.hpSvrProject = QLineEdit()

        self.comAPI = QRadioButton("COM")
        self.comAPI.setChecked(False)
        self.comAPI.setEnabled(False)
        
        self.restAPI = QRadioButton("REST")
        self.restAPI.setChecked(True)
        
        layoutApi = QHBoxLayout()
        layoutApi.addWidget(self.comAPI)
        layoutApi.addWidget(self.restAPI)
        
        qcSvrLayout = QGridLayout()
        qcSvrLayout.addWidget( QLabel("URL"), 0, 0)
        qcSvrLayout.addWidget( self.hpSvrURL, 0, 1)
        qcSvrLayout.addWidget( QLabel("Domain"), 1, 0)
        qcSvrLayout.addWidget( self.hpSvrDomain, 1, 1)
        qcSvrLayout.addWidget( QLabel("Project"), 2, 0)
        qcSvrLayout.addWidget( self.hpSvrProject, 2, 1)
        qcSvrLayout.addWidget( QLabel("API"), 3, 0)
        qcSvrLayout.addLayout( layoutApi, 3, 1)
        
        qcSvrGroup.setLayout(qcSvrLayout)

        # begin export result settings
        qcExportResultGroup = QGroupBox(self.tr("Export results"))
        self.ignoreTcCheckBox = QCheckBox(self.tr("Ignore testcase(s)"))
        self.ignoreUncompleteCheckBox = QCheckBox(self.tr("Ignore uncomplete test(s)"))
        self.addFoldersTlCheckBox = QCheckBox(self.tr("Create missing folders in test lab"))
        self.addTestsetCheckBox = QCheckBox(self.tr("Create testset if missing in test lab"))
        self.addTestinstanceCheckBox = QCheckBox(self.tr("Create test instance in test set"))
        self.cfgsTestsetTable = DesignPage.ConfigsTableView(self, core=self.core())
        qcExportResultLayout = QVBoxLayout()
        qcExportResultLayout.addWidget( self.ignoreTcCheckBox )
        qcExportResultLayout.addWidget( self.ignoreUncompleteCheckBox )
        qcExportResultLayout.addWidget( self.addFoldersTlCheckBox )
        qcExportResultLayout.addWidget( self.addTestsetCheckBox )
        qcExportResultLayout.addWidget( self.addTestinstanceCheckBox )
        qcExportResultLayout.addWidget( QLabel("Custom TestSet Fields"))
        qcExportResultLayout.addWidget( self.cfgsTestsetTable )
        qcExportResultLayout.addStretch(1)
        qcExportResultGroup.setLayout(qcExportResultLayout)
        # end 
        
        # begin export test settings
        qcExportGroup = QGroupBox(self.tr("Export tests"))
        
        self.mergeCheckBox = QCheckBox(self.tr("Merge all tests in one"))
        self.mergeStepsCheckBox = QCheckBox(self.tr("Merge all steps in one"))
        self.showTcNameCheckBox = QCheckBox(self.tr("Load with original test name"))
        self.replaceTcCheckBox = QCheckBox(self.tr("Replace testcase with testname"))
        self.addFoldersTpCheckBox = QCheckBox(self.tr("Create missing folders in test plan"))
        self.overwriteTcCheckBox = QCheckBox(self.tr("Overwrite testcases in test plan"))
        self.cfgsTable = DesignPage.ConfigsTableView(self, core=self.core())

        qcExportLayout = QGridLayout()
        qcExportLayout.addWidget( self.mergeCheckBox, 0, 0)
        qcExportLayout.addWidget( self.mergeStepsCheckBox, 1, 0)
        qcExportLayout.addWidget( self.showTcNameCheckBox, 2, 0)
        qcExportLayout.addWidget( self.replaceTcCheckBox, 3, 0)
        qcExportLayout.addWidget( self.addFoldersTpCheckBox, 4, 0)
        qcExportLayout.addWidget( self.overwriteTcCheckBox, 5, 0)
        qcExportLayout.addWidget( QLabel("Custom Test Fields"), 6, 0)
        qcExportLayout.addWidget( self.cfgsTable, 7, 0)
        qcExportGroup.setLayout(qcExportLayout)
        # end 
        
        layoutCtrls = QHBoxLayout()
        self.saveButton = QPushButton(self.tr("Save Settings"), self)
        self.testButton = QPushButton(self.tr("Test Connection"), self)
        layoutCtrls.addWidget(self.saveButton)
        layoutCtrls.addWidget(self.testButton)
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(qcSvrGroup, 0, 0)
        mainLayout.addWidget(qcCredGroup, 0, 1)
        mainLayout.addWidget(qcExportGroup, 2, 0)
        mainLayout.addWidget(qcExportResultGroup, 2, 1)
        mainLayout.addLayout(layoutCtrls, 3, 1)
        # mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        
    def loadCfg(self):
        """
        """
        with open( "%s/config.json" % (QtHelper.dirExec()) ) as f:
            CONFIG_RAW = f.read()
        self.config = json.loads(CONFIG_RAW)

        self.hpCredLogin.setText(self.config["credentials"]["login"])
        
        
        self.hpSvrURL.setText(self.config["qc-server"]["url"])
        self.hpSvrDomain.setText(self.config["qc-server"]["domain"])
        self.hpSvrProject.setText(self.config["qc-server"]["project"])
        
        # if self.config["qc-server"]["use-rest"]: 
            # self.restAPI.setChecked(True) 
            # self.comAPI.setChecked(False) 
        # else:
            # self.comAPI.setChecked(True) 
            # self.restAPI.setChecked(False)
        # com api removed and deprecated
        self.restAPI.setChecked(True) 
        
        if self.config["export-tests"]["merge-all-tests"]: self.mergeCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-tests"]["merge-all-steps"]: self.mergeStepsCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-tests"]["original-test"]: self.showTcNameCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-tests"]["replace-testcase"]: self.replaceTcCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-tests"]["add-folders"]: self.addFoldersTpCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-tests"]["overwrite-tests"]: self.overwriteTcCheckBox.setCheckState(Qt.Checked) 
        self.cfgsTable.loadTable(data=self.config["custom-test-fields"])
        
        if self.config["export-results"]["ignore-testcase"]: self.ignoreTcCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-results"]["ignore-uncomplete"]: self.ignoreUncompleteCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-results"]["add-folders"]: self.addFoldersTlCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-results"]["add-testset"]: self.addTestsetCheckBox.setCheckState(Qt.Checked) 
        if self.config["export-results"]["add-testinstance"]: self.addTestinstanceCheckBox.setCheckState(Qt.Checked) 
        self.cfgsTestsetTable.loadTable(data=self.config["custom-testset-fields"])
        
        # decrypt password
        if len(self.config["credentials"]["password"]):
            decrypted = self.decryptPwd(
                                        key=bytes(self.config["credentials"]["login"], "utf8" ),
                                        ciphertext=bytes(self.config["credentials"]["password"], "utf8" )
                                        )
            self.config["credentials"]["password"] = decrypted
            self.hpCredPwd.setText(decrypted)

    def __saveCfg(self):
        """
        """
        self.saveCfg(successMsg=True)
        
    def saveCfg(self, successMsg=True):
        """
        """
        # if successMsg:
        if not len(self.hpSvrURL.text()):
            QMessageBox.warning(self, self.tr("Save Settings") , self.tr("Please to set the server url") )
            return
        if not len(self.hpSvrDomain.text()):
            QMessageBox.warning(self, self.tr("Save Settings") , self.tr("Please to set the server domain") )
            return
        if not len(self.hpSvrProject.text()):
            QMessageBox.warning(self, self.tr("Save Settings") , self.tr("Please to set the server project") )
            return

        if not len(self.hpCredLogin.text()):
            QMessageBox.warning(self, self.tr("Save Settings") , self.tr("Please to set a login") )
            return
        if not len(self.hpCredPwd.text()):
            QMessageBox.warning(self, self.tr("Save Settings") , self.tr("Please to set a password") )
            return
            
        self.config["credentials"]["login"] = self.hpCredLogin.text()
        # encrypt password
        encryptPwd = self.encryptPwd(
                                    key=self.hpCredLogin.text(),
                                    plaintext=self.hpCredPwd.text()
                                   )
        self.config["credentials"]["password"] = str(encryptPwd, "utf8")
        
        self.config["qc-server"]["url"] = self.hpSvrURL.text()
        self.config["qc-server"]["domain"] = self.hpSvrDomain.text()
        self.config["qc-server"]["project"] = self.hpSvrProject.text()
        self.config["qc-server"]["use-rest"] = False
        if self.restAPI.isChecked(): self.config["qc-server"]["use-rest"] = True
        
        self.config["export-tests"]["merge-all-tests"] = False
        self.config["export-tests"]["merge-all-steps"] = False
        self.config["export-tests"]["original-test"] = False
        self.config["export-tests"]["replace-testcase"] = False
        self.config["export-tests"]["add-folders"] = False
        self.config["export-tests"]["overwrite-tests"] = False
        if self.mergeCheckBox.isChecked(): self.config["export-tests"]["merge-all-tests"] = True
        if self.mergeStepsCheckBox.isChecked(): self.config["export-tests"]["merge-all-steps"] = True
        if self.showTcNameCheckBox.isChecked(): self.config["export-tests"]["original-test"] = True
        if self.replaceTcCheckBox.isChecked(): self.config["export-tests"]["replace-testcase"] = True
        if self.addFoldersTpCheckBox.isChecked(): self.config["export-tests"]["add-folders"] = True
        if self.overwriteTcCheckBox.isChecked(): self.config["export-tests"]["overwrite-tests"] = True
        self.config["custom-test-fields"] = self.cfgsTable.model.getData()
        
        self.config["export-results"]["add-folders"] = False
        self.config["export-results"]["ignore-testcase"] = False
        self.config["export-results"]["ignore-uncomplete"] = False
        self.config["export-results"]["add-testset"] = False
        self.config["export-results"]["add-testinstance"] = False
        if self.ignoreTcCheckBox.isChecked(): self.config["export-results"]["ignore-testcase"] = True
        if self.ignoreUncompleteCheckBox.isChecked(): self.config["export-results"]["ignore-uncomplete"] = True
        if self.addFoldersTlCheckBox.isChecked(): self.config["export-results"]["add-folders"] = True
        if self.addTestsetCheckBox.isChecked(): self.config["export-results"]["add-testset"] = True
        if self.addTestinstanceCheckBox.isChecked(): self.config["export-results"]["add-testinstance"] = True
        self.config["custom-testset-fields"] = self.cfgsTestsetTable.model.getData()
        
        with open( "%s/config.json" % (QtHelper.dirExec()), "w" ) as f:
            f.write( json.dumps(self.config) )
            
        if len(self.config["credentials"]["password"]):
            self.config["credentials"]["password"] = self.decryptPwd(
                                            key=bytes(self.config["credentials"]["login"], "utf8" ),
                                            ciphertext=bytes(self.config["credentials"]["password"], "utf8" )
                                  )
                
        self.ReloadSettings.emit()
        
        if successMsg: QMessageBox.information(self, self.tr("Save Settings") ,  self.tr("Settings saved.") )
                                
    def cfg(self):
        """
        """
        return self.config
        
    def encryptPwd(self, key, plaintext):
        """
        """
        # cipher = XOR.new(key)
        # return base64.b64encode(cipher.encrypt(plaintext))
        return base64.b64encode( bytes( plaintext, "utf8" ) )

    def decryptPwd(self, key, ciphertext):
        """
        """
        # cipher = XOR.new(key)
        # return str(cipher.decrypt(base64.b64decode(ciphertext)), "utf8")
        return str( base64.b64decode(ciphertext) , "utf8")
    
    def testConnection(self):
        """
        """
        # self.saveCfg(successMsg=False)
        self.TestSettings.emit(self.config)
    
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
    WidgetSettings.TestSettings.connect(WidgetMain.testConnection)

    # debug mode
    if DEBUGMODE: 
        if WidgetSettings.cfg()["plugin"]["show-maximized"]:
            MyPlugin.showMaximized()
        else:
            MyPlugin.show()
    
    sys.exit(app.exec_())