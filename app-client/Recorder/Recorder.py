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
Recorder module
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QMessageBox, QDialog)
except ImportError:
    from PyQt5.QtWidgets import (QMessageBox, QDialog)
    
from Libs import QtHelper, Logger

try:
    import Gui
except ImportError: # support python3
    from . import Gui
try:
    import Http
except ImportError: # support python3
    from . import Http
try:
    import Tcp
except ImportError: # support python3
    from . import Tcp
try:
    import Udp
except ImportError: # support python3
    from . import Udp
    
import UserClientInterface as UCI

import Workspace as WWorkspace
import Workspace.TestUnit as TestUnit
import Workspace.TestSuite as TestSuite

MODE_APP = 0
MODE_WEB = 1
MODE_MOB = 2
MODE_BAS = 3
MODE_SYS = 4
MODE_DBB = 5

class WRecorder(object):
    """
    Recorder engine
    """
    def __init__(self, parent, offlineMode=False):
        """
        Recorder constructor
        """
        self.parent = parent
        self.offlineMode = offlineMode

        Gui.initialize(parent=self, offlineMode=offlineMode, mainParent=parent)

        self.createActions()

    def gui(self):
        """
        Return gui instance
        """
        return Gui.instance()
        
    def createActions (self):
        """
        Create qt actions
        """
        self.startHttpAction = QtHelper.createAction(self.parent, "&Read Http", self.startHttp, 
                                                        icon=None, tip = 'Start the http capture')
        self.startTcpAction = QtHelper.createAction(self.parent, "&Read Tcp", self.startTcp, 
                                                        icon=None, tip = 'Start the tcp capture')
        self.startUdpAction = QtHelper.createAction(self.parent, "&Read Udp", self.startUdp, 
                                                        icon=None, tip = 'Start the udp capture')

        self.startGuiAction = QtHelper.createAction(Gui.instance(), "&New Test...", self.startGui, 
                                                    icon=None, tip = 'Start the capture of the desktop')
        self.restartGuiAction = QtHelper.createAction(Gui.instance(), "&Update Test...", self.restartGui, 
                                                    icon=None, tip = 'Update the current test for the desktop')
        self.stopGuiAction = QtHelper.createAction(Gui.instance(), "&Stop", self.stopGui, 
                                                    icon=None, tip = 'Stop the capture of the desktop')

        self.startWebAction = QtHelper.createAction(Gui.instance(), "&New Test...", self.startWeb, 
                                                    icon=None, tip = 'Start the capture of the web interface')
        self.startMobileAction = QtHelper.createAction(Gui.instance(), "&New Test...", self.startMobile, 
                                                    icon=None, tip = 'Start mobile assistant')
        self.startBasicAction = QtHelper.createAction(Gui.instance(), "&New Test...", self.startBasic, 
                                                    icon=None, tip = 'Start basic assistant')
        self.startSysAction = QtHelper.createAction(Gui.instance(), "&New Test...", self.startSys, 
                                                    icon=None, tip = 'Start system assistant')
                                                        
    def startUdp(self):
        """
        Start udp capture
        """
        if not self.offlineMode:
            if not UCI.instance().isAuthenticated():
                QMessageBox.warning(Gui.instance(), "Assistant Automation" , "Connect to the test center in first!")
                return

        plugin = Udp.DUdpReplay( offlineMode=self.offlineMode )
        if plugin.exec_() == QDialog.Accepted:
            if plugin.testType == Udp.TS:
                WWorkspace.WDocumentViewer.instance().newTestSuiteWithContent(testDef=plugin.newTest, 
                                                                              testExec=plugin.newTestExec, 
                                                                              testInputs=plugin.newInputs)
            if plugin.testType == Udp.TU:
                WWorkspace.WDocumentViewer.instance().newTestUnitWithContent(testDef=plugin.newTest, 
                                                                            testInputs=plugin.newInputs)
                
    def startTcp(self):
        """
        Start tcp capture
        """
        if not self.offlineMode:
            if not UCI.instance().isAuthenticated():
                QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                    "Connect to the test center in first!")
                return

        plugin = Tcp.DTcpReplay( offlineMode=self.offlineMode )
        if plugin.exec_() == QDialog.Accepted:
            if plugin.testType == Tcp.TS:
                WWorkspace.WDocumentViewer.instance().newTestSuiteWithContent(testDef=plugin.newTest, 
                                                                                testExec=plugin.newTestExec, 
                                                                                testInputs=plugin.newInputs)
            if plugin.testType == Tcp.TU:
                WWorkspace.WDocumentViewer.instance().newTestUnitWithContent(testDef=plugin.newTest, 
                                                                             testInputs=plugin.newInputs)
                
    def startHttp(self):
        """
        Start http capture
        """
        if not self.offlineMode:
            if not UCI.instance().isAuthenticated():
                QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                    "Connect to the test center in first!")
                return

        plugin = Http.DHttpReplay( offlineMode=self.offlineMode )
        if plugin.exec_() == QDialog.Accepted:
            if plugin.testType == Http.TS:
                WWorkspace.WDocumentViewer.instance().newTestSuiteWithContent(testDef=plugin.newTest, 
                                                                            testExec=plugin.newTestExec,
                                                                            testInputs=plugin.newInputs)
            if plugin.testType == Http.TU:
                WWorkspace.WDocumentViewer.instance().newTestUnitWithContent(testDef=plugin.newTest, 
                                                                            testInputs=plugin.newInputs)

    def showMessageTray(self, msg):
        """
        Show message tray
        """
        self.parent.showMessageTray(msg=msg)

    def showMainApplication(self):
        """
        Show main application
        """
        self.parent.setVisible(True)

    def hideMainApplication(self):
        """
        Hide the main application
        """
        self.parent.minimizeWindow()

    def restoreMainApplication(self):
        """
        Restore the main application
        """
        self.parent.restoreWindow()
        self.parent.maximizeWindow()
        # self.parent.minimizeWindow()
        
    def restartGui(self, isTu=True, isTs=False):
        """
        Restart the gui recorder from test
        """
        if not self.offlineMode:
            if not UCI.instance().isAuthenticated():
                QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                    "Connect to the test center in first!")
                return
            
        # extract the current test
        currentDocument = WWorkspace.DocumentViewer.instance().getCurrentDocument()
        if isinstance(currentDocument, WWorkspace.WDocumentViewer.WelcomePage):
            QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                "No valid test detected!")
            return
        else:
            if currentDocument is not None:
                if currentDocument.extension == TestUnit.TYPE or currentDocument.extension == TestSuite.TYPE:
                    testContent = currentDocument.srcEditor.text()
                    testInputs = currentDocument.dataModel.properties['properties']['inputs-parameters']
                    testAgents = currentDocument.dataModel.properties['properties']['agents']

                    Gui.instance().clearSteps()
                    Gui.instance().loadAgents()
                    Gui.instance().show()
                    Gui.instance().loadCurrentTest( currentDoc=currentDocument, 
                                                    testContent=testContent,
                                                    testInputs=testInputs, 
                                                    testAgents=testAgents, 
                                                    isTu=isTu, isTs=isTs)
      
                else:
                    QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                        "No valid test detected!" )
                return
            else:
                QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                    "No valid test detected!" )
                return
            
    def startGui(self, mode=MODE_APP):
        """
        Start gui recorder
        """
        if not self.offlineMode:
            if not UCI.instance().isAuthenticated():
                QMessageBox.warning(Gui.instance(), "Assistant Automation" , 
                                    "Connect to the test center in first!")
                return

        Gui.instance().clearSteps()
        Gui.instance().loadAgents()
        
        if mode == MODE_APP:
            Gui.instance().focusAppPart()
            
        if mode == MODE_WEB:
            Gui.instance().focusWebPart()
            
        if mode == MODE_MOB:
            Gui.instance().focusMobPart()  
            
        if mode == MODE_BAS:
            Gui.instance().focusBasPart()  
            
        if mode == MODE_SYS:
            Gui.instance().focusSysPart()  
            
        if mode == MODE_DBB:
            Gui.instance().focusBasPart()  
            
        Gui.instance().show()
    
    def startMobile(self):
        """
        Start the assistant on the mobile part
        """
        self.startGui(mode=MODE_MOB)
    
    def startWeb(self):
        """
        Start the assistant on the web part
        """
        self.startGui(mode=MODE_WEB)
    
    def startBasic(self):
        """
        Start the assistant on the framework part
        """
        self.startGui(mode=MODE_BAS)
    
    def startSys(self):
        """
        Start the assistant on the system part
        """
        self.startGui(mode=MODE_SYS)
    
    def startDatabase(self):
        """
        Start the assistant on the database part
        """
        self.startGui(mode=MODE_DBB)
        
    def stopGui(self):
        """
        Stop gui recorders
        """
        # new in v17.1
        self.parent.showNormal()
        self.parent.showMaximized()
        # end of new
        
    def snapshotEngaged(self):
        """
        Return if the snapshot mode is engaged
        """
        if Gui.instance().snapshotActivated:
            return True
        return False

    def recorderEngaged(self):
        """
        Return if the recorder mode is engaged
        """
        if Gui.instance().recorderActivated:
            return True
        return False

    def showGui(self):
        """
        Show gui
        """
        Gui.instance().show()

    def captureDesktop(self):
        """
        Capture the desktop
        """
        Gui.instance().onGlobalShortcutPressed()

    def restoreAssistant(self):
        """
        Restore the assistant
        """
        Gui.instance().restoreAssistant()
        
Recorder = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return Recorder

def initialize (parent, offlineMode=False):
    """
    Initialize WWorkspace widget
    """
    global Recorder
    Recorder = WRecorder(parent=parent, offlineMode=offlineMode)

def finalize ():
    """
    Destroy Singleton
    """
    global Recorder
    if Recorder:
        if sys.platform == "win32":
            Gui.finalize()
        del Recorder
        Recorder = None