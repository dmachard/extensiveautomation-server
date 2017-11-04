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
Main app
"""
                            
import sip
import sys

# to support py2.7 and pyqt4 on linux
if sys.version_info < (3,):
    sip.setapi('QString', 2)
    
try:
    sip.setdestroyonexit(False)
except:
    pass
    
try:
	from PyQt4.QtCore import (pyqtSignal, QTimer, Qt, QRect, QSize, QT_VERSION_STR, PYQT_VERSION_STR, 
							 QFile, QByteArray, QBuffer, QIODevice, QTranslator, QLibraryInfo,
                             QProcess)
	from PyQt4.QtGui import (QGridLayout, QVBoxLayout, QHBoxLayout, QApplication, QColor,
							QWidget, QDialog, QPushButton, QLineEdit, QLabel, QTextEdit, 
							QComboBox, QTextCursor, QIcon, QFont, QCheckBox , QStandardItem,
							QListWidgetItem, QMessageBox, QFrame, QIntValidator, QSizePolicy,
							QSortFilterProxyModel, QSystemTrayIcon, QToolBar, QTabWidget, 
							QAction, QMenu, QSystemTrayIcon, QPixmap, qApp, QListWidget)
except ImportError:
	from PyQt5.QtCore import (pyqtSignal, QTimer, Qt, QRect, QSize, QT_VERSION_STR, PYQT_VERSION_STR, 
							 QFile, QByteArray, QBuffer, QIODevice, QTranslator, QLibraryInfo,
							 QSortFilterProxyModel, QProcess)
	from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QHBoxLayout, QApplication,
							QWidget, QDialog, QPushButton, QLineEdit, QLabel, QTextEdit, 
							QComboBox, QCheckBox , 
							QListWidgetItem, QMessageBox, QFrame, QSizePolicy,
							QSystemTrayIcon, QToolBar, QTabWidget, 
							QAction, QMenu, QSystemTrayIcon, qApp, QListWidget)
	from PyQt5.QtGui import (QTextCursor, QIcon, QFont, QIntValidator,
							QPixmap, QGuiApplication, QStandardItem, QColor )

from Libs import Logger, Settings, QtHelper
from Resources import Resources
from Translations import Translations
import Mobile
import Core.GenericTool as GenericTool


# name of the main developer
__AUTHOR__ = 'Denis Machard'
# email of the main developer
__EMAIL__ = 'd.machard@gmail.com'
# list of testers
__TESTERS__ = ""
# list of contributors
__CONTRIBUTORS__ = [ "" ]
# project start in year
__BEGIN__ = "2010"
# year of the latest build
__END__="2017"
# date and time of the buid
__BUILDTIME__="04/11/2017 18:04:27"
# Redirect stdout and stderr to log file only on production
REDIRECT_STD=True

__LICENCE__ = """This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
<br /><br />
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
<br /><br />
You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301 USA"""

import ReleaseNotes as RN
import time
import os
import inspect
import threading
import platform
import subprocess
import shutil
import uuid
import json
import base64
try:
    import ConfigParser
except ImportError: # python 3 support
    import configparser as ConfigParser
try:
    import StringIO
except ImportError: # support python 3
    import io as StringIO

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

    
settingsFile = '%s/settings.ini' % QtHelper.dirExec()
if not os.path.exists(settingsFile):
    print('config file settings.ini doesn\'t exist.')
    sys.exit(-1)

# adding missing folders
if not os.path.exists( "%s/Logs/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Logs" % QtHelper.dirExec() )
if not os.path.exists( "%s/Tmp/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Tmp" % QtHelper.dirExec() )
if not os.path.exists( "%s/Plugins/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Plugins" % QtHelper.dirExec() )

Settings.initialize()
Logger.initialize( logPathFile = "%s/%s/systray.log" % (Settings.getDirExec(),Settings.get('Paths', 'logs'))  )   


# Enable redirects output and error on production
if sys.version_info < (3,):
    if REDIRECT_STD:
        buf_arg = 0
        sys.stdout = open( "%s/%s/systray.log" % (Settings.getDirExec(),Settings.get('Paths', 'logs')) ,"a", buf_arg)
        sys.stderr = open( "%s/%s/systray.log" % (Settings.getDirExec(),Settings.get('Paths', 'logs')) ,"a", buf_arg)
else: # python 3 support
    if REDIRECT_STD:
        sys.stdout = open( "%s/Logs/systray_sdtout.log" % QtHelper.dirExec() ,"a", 1) # 1 to select line buffering (only usable in text mode)
        sys.stderr = open( "%s/Logs/systray_sdterr.log" % QtHelper.dirExec() ,"a", 1) # 1 to select line buffering (only usable in text mode)
        sys.excepthook = Logger.log_exception

from Embedded import * # for exe mode 
# loading all plugins
plugins = {}
for pluginName in dir(__import__( "Embedded" )):
    if not pluginName.startswith('__') and not pluginName.endswith('__'):
        pkg =  __import__( "Embedded.%s" % pluginName )
        for listing in dir(pkg):
            obj = getattr(pkg, listing)
            if inspect.ismodule(obj):
                plugins[(obj.__TOOL_TYPE__,obj.__TYPE__)] = obj
                
PLUGINS_AGENT_EXTERNAL = {}
PLUGINS_PROBE_EXTERNAL = {}

def str2bool(value):
    """
    Convert str two bool
    """
    return {"True": True, "true": True}.get(value, False)

        
TOOL_AGENT=0
TOOL_PROBE=1  
TOOL_EXT_AGENT=2
TOOL_EXT_PROBE=3  

TOOLS_DESCR = {
    TOOL_AGENT: "embedded agent",
    TOOL_PROBE: "embedded probe",
    TOOL_EXT_AGENT: "external agent",
    TOOL_EXT_PROBE: "external agent"
}

class PluginProcess(QProcess):
    """
    Plugin process
    """
    DataReceived = pyqtSignal(bytes, object)
    def __init__(self, parent, cmd, toolPage, tmpArea):
        """
        """
        QProcess.__init__(self, parent)
        self.__cmd = cmd
        self.toolPage = toolPage
        self.tmpArea = tmpArea
        self.setProcessChannelMode(QProcess.MergedChannels)   
        self.readyReadStandardOutput.connect(self.onData)
        self.keepAliveTimer = QTimer(parent)
        self.keepAliveTimer.timeout.connect(self.sendKeepAlive)
        self.keepAliveTimer.setInterval(10000)
        
    def widgetPage(self):
        """
        Return the tool page widget
        """
        return self.toolPage
        
    def onData(self):
        """
        On data received
        """
        # d -> qbytearray
        d = self.readAllStandardOutput()
        self.DataReceived.emit(d.data(), self)
        
    def startPlugin(self):
        """
        Start the plugin
        """
        self.start(self.__cmd)
        
    def startKeepAlive(self):
        """
        Start the keepalive
        """
        self.keepAliveTimer.start()
        
    def sendKeepAlive(self):
        """
        Send keep alive
        """
        self.sendCommand(cmd='keepalive')
        
    def sendCommand(self, cmd, data='', more={}):
        """
        Send command
        """
        inData = False
        msg = {'cmd': cmd }
        
        # save data to temp area
        idFile = ''
        
        
        if len(data):
            try:
                idFile = "%s" % uuid.uuid4()
                pluginDataFile = '%s/%s' % (self.tmpArea, idFile)
                with open( pluginDataFile, mode='w') as myfile:
                    myfile.write( json.dumps( data )  )
                inData = True
            except Exception as e:
                print("unable to write plugin data file: %s" % e)

        msg.update( { 'in-data': inData } )
         
        # add data parameters
        if inData: msg.update( { 'data-id': idFile } )
             
        # add more params
        msg.update(more)
        
        # send command
        datagram = json.dumps( msg ) 
        datagramEncoded = base64.b64encode( bytes(datagram, "utf8")  )
        self.write( str(datagramEncoded, "utf8") + "\n\n" )

class QListItemEnhanced(QListWidgetItem):
    """
    Item widget class
    """
    def __init__(self, toolId, toolType, toolName, toolPlugin, toolDescr, toolIp, 
                 toolPort, proxyIp, proxyPort, proxyEnable=False):
        """
        Constructor
        """
        super(QListItemEnhanced, self).__init__()

        self.toolId = toolId
        self.toolType = toolType
        self.toolName = toolName
        self.toolPlugin = toolPlugin
        self.toolDescr = toolDescr
        self.toolIp = toolIp
        self.toolPort = toolPort
        
        self.proxyEnable = proxyEnable
        self.proxyIp = proxyIp
        self.proxyPort = proxyPort
        
        self.createWidget()
        
    def createWidget(self):
        """
        Create the qt widget
        """
        if self.toolType == TOOL_AGENT or self.toolType == TOOL_EXT_AGENT :
            self.setIcon(QIcon(':/agent.png'))
        else:
            self.setIcon(QIcon(':/probe.png'))
        if self.proxyEnable:
            self.setText( "[Addr:%s Proxy:Yes][%s] %s - %s" % ( self.toolIp, 
                                                                TOOLS_DESCR[self.toolType], 
                                                                self.toolName, 
                                                                self.toolPlugin) )
        else:
            self.setText( "[Addr:%s Proxy:No][%s] %s - %s" % ( self.toolIp, 
                                                               TOOLS_DESCR[self.toolType], 
                                                               self.toolName, 
                                                               self.toolPlugin) )

class ToolPage(QWidget):
    """
    Tool page widget
    """
    StopTool = pyqtSignal(object)  
    LogWarning = pyqtSignal(str)  
    LogError = pyqtSignal(str)  
    LogSuccess = pyqtSignal(str)  
    UpdateScreen = pyqtSignal(str,str)  
    AskUser = pyqtSignal(str)  
    TakeScreenshot = pyqtSignal(object, dict, str, str, str, str , int)  
    StartExternalTool = pyqtSignal(object, int, str, str)  
    def __init__(self, parent, delayStartup=0):
        """
        Tool page widget constructor
        """
        super(ToolPage, self).__init__()

        self.__mutex__ = threading.RLock()
        
        self.mainApp = parent
        
        self.toolObj = None
        self.toolType = TOOL_AGENT
        self.toolName = ""
        self.toolPlugin = ""
        self.toolDescr = ""

        self.controllerIp = "127.0.0.1"
        self.controllerPort = 443
        self.proxyEnable = False
        self.proxyIp = "127.0.0.1"
        self.proxyPort = 8080
        
        self.maxReconnect = int(Settings.get('Server','max-reconnect'))
        self.currentReconnect = 0
        
        self.featureRestartReady = False
        self.timerRestart = None
        self.timerReconnect = None

        self.delayStartup = delayStartup
        self.delayTimer = QTimer()
        self.delayTimer.setInterval(self.delayStartup*1000)
        self.delayTimer.timeout.connect(self.startTool)
        
        self.pluginProcess = None
        self.createWidget()
        self.createConnections()

    def createConnections(self):
        """
        Create qt connections
        """
        self.stopButton.clicked.connect(self.closeTool)
        self.clearLogsButton.clicked.connect(self.clearLogs)
        self.copyLogsButton.clicked.connect(self.copyLogs)
        
        self.LogWarning.connect(self.addLogWarning)
        self.LogError.connect(self.addLogError)
        self.LogSuccess.connect(self.addLogSuccess)
        
        self.UpdateScreen.connect(self.updateScreen)
        self.AskUser.connect(self.onAskUser)
        
        self.mobileWidget.RefreshScreen.connect(self.refreshScreen)
        self.mobileWidget.RefreshAutomatic.connect(self.onRefreshChanged)
        self.mobileWidget.TapOn.connect(self.tapOn)
    
    def createWidget(self):
        """
        Create qt widget
        """
        self.clearLogsButton = QPushButton(self.tr("Clear Logs"), self)
        self.copyLogsButton = QPushButton(self.tr("Copy Logs"), self)
        self.stopButton = QPushButton(self.tr("Terminate"), self)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.clearLogsButton)
        buttonLayout.addWidget(self.copyLogsButton)
        buttonLayout.addWidget(self.stopButton)

        self.nameEdit = QLineEdit()
        self.nameEdit.setEnabled(False)
        self.descriptionEdit = QLineEdit( )
        self.descriptionEdit.setEnabled(False)
        self.typeEdit = QLineEdit()
        self.typeEdit.setEnabled(False)
        
        self.remoteServerEdit = QLineEdit( )
        self.remoteServerEdit.setEnabled(False)

        toolLayout = QGridLayout()
        
        toolLayout.addWidget( QLabel("Name:"), 1, 1 )
        toolLayout.addWidget(self.nameEdit, 1, 2)
        
        toolLayout.addWidget(QLabel("Type:"), 2, 1)
        toolLayout.addWidget(self.typeEdit, 2, 2)
        
        toolLayout.addWidget( QLabel("Description:"), 4, 1)
        toolLayout.addWidget(self.descriptionEdit, 4, 2)
        
        toolLayout.addWidget( QLabel("Remote Server:"), 5, 1)
        toolLayout.addWidget(self.remoteServerEdit, 5, 2)
        
        toolLayout.addWidget( QLabel(""), 6, 0)
        
        self.logsEdit = QTextEdit()
        self.logsEdit.setReadOnly(True)
        self.logsEdit.setOverwriteMode(True)
        self.logsEdit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.logsEdit.setMinimumWidth(400)
        
        globalLayout = QHBoxLayout()
        
        self.mobileWidget = Mobile.MobileWidget()
        self.mobileWidget.hide()

        main2Layout = QVBoxLayout()

        main2Layout.addLayout(toolLayout)
        main2Layout.addWidget(self.logsEdit)
        main2Layout.addLayout(buttonLayout)

        globalLayout.addLayout(main2Layout)
        globalLayout.addWidget(self.mobileWidget)

        self.setLayout(globalLayout)
        
    def onTakeScreenshot(self, request, action, actionId, adapterId, testcaseName, replayId):
        """
        On take screenshot
        """
        self.TakeScreenshot.emit(self, request, action, actionId, adapterId, testcaseName, replayId)

    def onRefreshChanged(self, state):
        """
        Activate or not the automatic refresh of the screen
        """
        if state:
            self.toolObj.startAutomaticRefresh()
        else:
            self.toolObj.stopAutomaticRefresh()

    def plugin(self):
        """
        Return the plugin object
        """
        return self.toolObj
        
    def refreshScreen(self):
        """
        Refresh the screen
        Only for the ADB agent
        """
        self.toolObj.getScreen()
 
    def hideMobilePart(self):
        """
        Hide the modible part
        Only for ADB agent
        """
        self.mobileWidget.hide()
        
    def tapOn(self, x, y):
        """
        Tap on the position
        Only for the ADB agent
        """
        if self.toolObj is not None:
            self.toolObj.tapOn(x=x,y=y)
        
    def showMobilePart(self):
        """
        Show the mobile part
        Only for the ADB agent
        """
        self.mobileWidget.show()
        self.mobileWidget.center()

    def onDeviceReady(self):
        """
        Event raised when the device is ready
        Only for the ADB agent
        """
        self.mobileWidget.onDeviceReady()
        
    def updateScreen(self, filename, xml=''):
        """
        Update the screen
        Only for the ADB agent
        """
        self.mobileWidget.updateScreen(filename=filename, xmlPath=xml)
        
    def clearLogs(self):
        """
        Clear logs
        """
        self.logsEdit.clear()

    def info (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        Logger.info( "[%s] %s" % (self.__class__.__name__, txt ) )

    def trace (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        Logger.debug( "[%s] %s" % (self.__class__.__name__,  txt ) )

    def error (self, err):
        """
        Log error

        @param err:
        @type err:
        """
        Logger.error( "[%s] %s" % ( self.__class__.__name__,  err ) )

    def autoScrollOnTextEdit(self):
        """
        Autoscroll on text edit
        """
        cursor = self.logsEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logsEdit.setTextCursor(cursor)
        
    def copyLogs(self):
        """
        Copy logs
        """
        logs = self.logsEdit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText( logs )
    
    def strip_html(self, txt):
        """
        Strip html
        """
        if "<" in txt:
            txt = txt.replace( '<', '&lt;' )
        if ">" in txt:
            txt = txt.replace( '>', '&gt;' )
        return txt
        
    def addLogSuccess(self, txt):
        """
        Add log success
        """
        self.__mutex__.acquire()
        self.info( txt )

        self.logsEdit.insertHtml( "<span style='color:darkgreen'>%s - %s</span><br />" % ( self.formatTimestamp(time.time()), 
                                                                                           self.strip_html(txt)) )
        self.autoScrollOnTextEdit()
        self.__mutex__.release()

    def addLogWarning(self, txt):
        """
        Add log warning
        """
        self.__mutex__.acquire()
        self.info( txt )
        self.logsEdit.insertHtml( "<span style='color:darkorange'>%s - %s</span><br />" % (self.formatTimestamp(time.time()), 
                                                                                           self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()
        self.__mutex__.release()

    def addLogError(self, txt):
        """
        Add log error
        """
        self.__mutex__.acquire()
        self.error( txt )
        self.logsEdit.insertHtml( "<span style='color:red'>%s - %s</span><br />" % (self.formatTimestamp(time.time()), 
                                                                                    self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()
        self.__mutex__.release()

    def addLog(self, txt):
        """
        Append log to the logsEdit widget
        """
        self.__mutex__.acquire()
        self.logsEdit.insertHtml( "%s - %s<br />" % (self.formatTimestamp(time.time()), unicode( self.strip_html(txt) )) )
        self.autoScrollOnTextEdit()
        self.__mutex__.release()
        
    def formatTimestamp ( self, timestamp, milliseconds=False):
        """
        Returns human-readable time

        @param timestamp: 
        @type timestamp:

        @param milliseconds: 
        @type milliseconds: boolean

        @return:
        @rtype:
        """
        if isinstance( timestamp, str):
            return "  %s  " % timestamp
        t = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(timestamp) ) 
        if milliseconds:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) + ".%3.3d" % int((timestamp * 1000)  % 1000)
        return t

    def onCleanup(self):
        """
        On cleanup event
        """
        try:
            if self.timerRestart is not None:
                self.timerRestart.cancel()
                    
            if self.toolObj is not None:
                if self.toolObj.regRequest is not None: # cancel the registration request if not None
                    self.toolObj.regRequest.set()
                self.toolObj.onPreCleanup()
                self.toolObj.stopCA()
                self.toolObj.join()
                self.toolObj = None
        except Exception as e:
            self.error("unable to cleanup properly: %s" % e)
            
    def closeTool(self):
        """
        Close tool
        """
        self.delayTimer.stop()
        self.stopTool(autoRestart=False, exitAfter=True)
        
    def onReconnectTool(self):
        """
        Event raised on reconnect
        """
        self.mainApp.updateTabName(self, tabText="%s (unregistered)" % self.toolName)
        
        # check if max reconnect is not reached
        if self.currentReconnect <= self.maxReconnect:

            self.LogWarning.emit('>> Auto reconnect. Retries (%s/%s)' % (self.currentReconnect,self.maxReconnect))
            
            interval = Settings.getInt('Server','initial-retry')
            interval = interval * self.currentReconnect
            intervalMsec = interval*1000

            self.LogWarning.emit('>> Waiting %s sec. before to retry...' % interval)
            
            self.timerReconnect = threading.Timer(interval, self.reconnectTool)
            self.timerReconnect.start()
                
        else:
            self.LogError.emit('>> Auto reconnect failed. Retries (%s/%s)' % (self.currentReconnect,self.maxReconnect))
            
    def stopTool(self, autoRestart=False, exitAfter=False):
        """
        Stop the tool
        """
        self.mainApp.updateTabName(self, tabText="%s (stopping)" % self.toolName)
        self.LogSuccess.emit(">> Stopping agent")
        try:
            if self.timerRestart is not None:
                self.timerRestart.cancel()
                
            if self.toolObj is not None:
                if self.toolObj.regRequest is not None: # cancel the registration request if not None
                    self.toolObj.regRequest.set()
                self.toolObj.onPreCleanup()
                self.toolObj.stopCA()
                self.toolObj.join()
                self.toolObj = None
        except Exception as e:
            self.error("unable to stop properly: %s" % e)
        
        self.mainApp.updateTabName(self, tabText="%s (stopped)" % self.toolName)
        self.LogSuccess.emit(">> Agent stopped")
        
        if autoRestart:
            # check if max reconnect is not reached
            if self.currentReconnect <= self.maxReconnect:

                self.LogWarning.emit('>> Auto reconnect. Retries (%s/%s)' % (self.currentReconnect,self.maxReconnect))
                
                interval = Settings.getInt('Server','initial-retry')
                interval = interval * self.currentReconnect
                intervalMsec = interval*1000

                self.LogWarning.emit('>> Waiting %s sec. before to retry...' % interval)

                self.timerRestart = threading.Timer(interval, self.restartTool)
                self.timerRestart.start()
                
        if exitAfter:
            self.StopTool.emit(self)

    def setTool(self, toolName, toolType, toolPlugin, toolDescr, toolIp=None):
        """
        Configure the tool
        """
        self.toolType = toolType
        self.toolName = toolName
        self.toolPlugin = toolPlugin
        self.toolDescr = toolDescr
        
        self.nameEdit.setText(toolName)
        self.descriptionEdit.setText(toolDescr)
        self.typeEdit.setText(toolPlugin)
        if toolIp is not None:  self.remoteServerEdit.setText(toolIp)

        if "adb" in toolPlugin:
            self.showMobilePart()
            self.updateScreen(filename='%s\%s\Adb\screncapture.png' % (Settings.getDirExec(), Settings.get('Paths', 'bin') ) )
        else:
            self.hideMobilePart()
        
    def setNetwork(self, controllerIp, controllerPort, proxyEnable, proxyIp, proxyPort):
        """
        Set network config
        """
        self.controllerIp = controllerIp
        self.controllerPort = int(controllerPort)
        self.proxyEnable = proxyEnable
        if proxyEnable:
            self.proxyIp = proxyIp
            self.proxyPort = int(proxyPort)
    
    def reconnectTool(self):
        """
        Just restart a registration with the server
        """
        if self.toolObj is not None:
            self.mainApp.updateTabName(self, tabText="%s (reconnecting)" % self.toolName)
            
            self.toolObj.startConnection()
        
    def restartTool(self):
        """
        Restart tool (complete restart with external tool also)
        """
        self.mainApp.updateTabName(self, tabText="%s (starting)" % self.toolName)
        self.startTool(autoReconnect=True)
     
    def startToolDelayed(self):
        """
        Start the tool with delay
        """
        if self.delayStartup > 0:
            self.mainApp.updateTabName(self, tabText="%s (delaying)" % self.toolName)
            self.onToolLogWarningCalled( ">> Startup is delayed of %s seconds, please wait..." % self.delayStartup)
            self.delayTimer.start()
        else:
            self.startTool()
            
    def startTool(self, autoStart=False, autoReconnect=False):
        """
        Start the tool
        """
        self.delayTimer.stop()
        
        if not autoReconnect: self.currentReconnect = 0
        if autoStart: self.LogWarning.emit('<< Auto connect on startup activated')
        
        if self.toolType == TOOL_AGENT or self.toolType == TOOL_EXT_AGENT:   
            self.addLogSuccess( ">> Starting agent '%s...'" % self.toolName)
        else:
            self.addLogSuccess( ">> Starting probe '%s...'" % self.toolName)
        self.trace("tool name: %s" % self.toolName)
        self.trace("tool type: %s" % self.toolPlugin)
        self.trace("tool descr: %s" % self.toolDescr)
        self.trace("destination server ip: %s" % self.controllerIp)
        self.trace("destination server port: %s" % self.controllerPort)
        
        self.trace("Saving cfg..")
        Settings.set('Server','ip', str(self.controllerIp) )
        Settings.set('Server','port', str(self.controllerPort) )
        Settings.set('Server','addr-proxy-http', str(self.proxyIp) )
        Settings.set('Server','port-proxy-http', str(self.proxyPort) )
        Settings.set('Server','proxy-active', str(self.proxyEnable) )
        Settings.save()
        self.trace("Cfg saved..")

        initPlugin = False
        
        toolPlugin = self.toolPlugin.strip()

        self.trace("tool type: %s" % self.toolType )
        self.trace("tool plugin: %s" % toolPlugin )

        if ( self.toolType, toolPlugin) in plugins:
            if self.toolType == TOOL_AGENT:
                self.info("Initialize %s agent..." % str(toolPlugin) )
            else:
                self.info("Initialize %s probe..." % str(toolPlugin) )

            try:
                self.toolObj = plugins[(self.toolType, toolPlugin)].initialize( 
                                    controllerIp=str(self.controllerIp), toolName=str(self.toolName), toolDesc=str(self.toolDescr), 
                                    defaultTool=False, controllerPort=int(self.controllerPort), supportProxy=self.proxyEnable,
                                    proxyIp=str(self.proxyIp), proxyPort=int(self.proxyPort), 
                                    sslSupport=str2bool(Settings.instance().get( 'Server', 'ssl-support' ))
                                )
                self.toolObj.checkPrerequisites()
                initPlugin = True
            except Exception as e:
                self.LogError.emit("<< Unable to initialize plugin: %s" %  e)
                
        elif toolPlugin in PLUGINS_AGENT_EXTERNAL:
            self.toolObj = GenericTool.Tool( 
                                controllerIp=str(self.controllerIp), controllerPort=int(self.controllerPort), 
                                toolName=str(self.toolName), toolDesc=str(self.toolDescr), defaultTool=False, 
                                supportProxy=self.proxyEnable, proxyIp=str(self.proxyIp), proxyPort=int(self.proxyPort), 
                                sslSupport=str2bool(Settings.instance().get( 'Server', 'ssl-support' )),
                                toolType = "Agent", fromCmd=False, name=toolPlugin.title()
                            )
            initPlugin = True
            
        elif toolPlugin in PLUGINS_PROBE_EXTERNAL:
            self.toolObj = GenericTool.Tool( 
                                controllerIp=str(self.controllerIp), controllerPort=int(self.controllerPort), 
                                toolName=str(self.toolName), toolDesc=str(self.toolDescr), defaultTool=False, 
                                supportProxy=self.proxyEnable, proxyIp=str(self.proxyIp), proxyPort=int(self.proxyPort), 
                                sslSupport=str2bool(Settings.instance().get( 'Server', 'ssl-support' )),
                                toolType = "Probe", fromCmd=False, name=toolPlugin.title()
                            )
            initPlugin = True
            
        else:
            self.LogError.emit("<< plugin type not supported: %s" %  self.toolPlugin)
        
        if initPlugin:
            self.toolObj.onPluginStarted = self.onPluginStarted
            self.toolObj.onRegistrationRefused = self.onRegistrationRefused
            self.toolObj.onToolLogWarningCalled = self.onToolLogWarningCalled
            self.toolObj.onToolLogSuccessCalled = self.onToolLogSuccessCalled
            self.toolObj.onToolLogErrorCalled = self.onToolLogErrorCalled
            self.toolObj.onRegistrationFailed = self.onRegistrationFailed
            self.toolObj.onRegistrationSuccessful = self.onRegistrationSuccessful
            self.toolObj.onResolveHostnameFailed = self.onResolveHostnameFailed
            self.toolObj.onConnectionRefused = self.onConnectionRefused
            self.toolObj.onConnectionTimeout = self.onConnectionTimeout
            self.toolObj.onToolDisconnection = self.onToolDisconnection
            self.toolObj.onProxyConnectionTimeout = self.onProxyConnectionTimeout
            self.toolObj.onProxyConnectionRefused = self.onProxyConnectionRefused
            self.toolObj.onProxyConnectionError = self.onProxyConnectionError
            self.toolObj.onWsHanshakeError = self.onWsHanshakeError
            self.toolObj.onResetAgentCalled = self.stopTool
            self.toolObj.onScreenCaptured = self.onScreenCaptured
            self.toolObj.onTakeScreenshot = self.onTakeScreenshot
            self.toolObj.userConfirm = self.onUserConfirm
            self.toolObj.onDeviceReady = self.onDeviceReady
            if self.toolType == TOOL_EXT_AGENT:
                self.toolObj.onAgentNotify = self.onAgentNotify
                self.toolObj.onAgentReset = self.onAgentReset
                self.toolObj.onAgentInit = self.onAgentInit
                self.toolObj.onAgentAlive = self.onAgentAlive
                self.toolObj.onStart = self.onStartingProbe
                self.toolObj.onStop = self.onStoppingProbe
                
            self.toolObj.startCA()

    def onStartingProbe(self, callid, tid, data):
        """
        On starting the probe event
        """
        if self.pluginProcess is None: 
            return
        
        self.pluginProcess.sendCommand(cmd="start-probe", data='', more={'callid': tid, 'data': data, 'tid': tid})
        
    def onStoppingProbe(self,  tid, data):
        """
        On stopping probe event
        """
        if self.pluginProcess is None: 
            return
        
        self.pluginProcess.sendCommand(cmd="stop-probe", data='', more={'data': data, 'tid': tid})
        
    def onAgentNotify(self, client, tid, request): 
        """
        On agent notify event
        """
        if self.pluginProcess is None: 
            return
        
        self.pluginProcess.sendCommand(cmd="notify", data=request, more={'tid': tid, 'client': client})
        
    def onAgentReset(self, client, tid, request): 
        """
        On agent reset event
        """
        if self.pluginProcess is None: 
            return
        
        self.pluginProcess.sendCommand(cmd="reset", data=request, more={'tid': tid, 'client': client})
        
    def onAgentInit(self, client, tid, request): 
        """
        On agent init event
        """
        if self.pluginProcess is None: 
            return
        
        self.pluginProcess.sendCommand(cmd="init", data=request, more={'tid': tid, 'client': client})
        

    def onAgentAlive(self, client, tid, request): 
        """
        On agent alive event
        """
        if self.pluginProcess is None: 
            return
        
        self.pluginProcess.sendCommand(cmd="alive", data=request, more={'tid': tid, 'client': client})
        
        
    def onUserConfirm(self, msg):
        """
        On user confirm event
        """
        self.AskUser.emit(msg)
        
    def onAskUser(self, msg):
        """
        Function to ask validation to the user
        """
        messageBox = QMessageBox(self)
        reply = messageBox.question(self, self.tr("User action"), self.tr(msg), QMessageBox.Ok )
        if self.toolObj is not None:
            self.toolObj.onUserConfirmed()

    def onScreenCaptured(self, filename, xml=''):
        """
        On screen captured
        Only for the ADB agent
        """
        self.UpdateScreen.emit(filename, xml)

    def onPluginStarted(self):
        """
        On plugin started
        """
        self.mainApp.updateTabName(self, tabText="%s (running)" % self.toolName)
        
    def onToolLogSuccessCalled(self, msg):
        """
        On tool log success called
        """
        self.LogSuccess.emit("%s" % msg )
        
    def onToolLogWarningCalled(self, msg):
        """
        On tool log warning called
        """
        self.LogWarning.emit("%s" % msg )

    def onToolLogErrorCalled(self, msg):
        """
        On tool log error called
        """
        self.LogError.emit("%s" % msg )

    def onWsHanshakeError(self, err):
        """
        On websocket handshake error
        """
        self.LogError.emit("<< connection error")
        autoRestart = False
        if self.featureRestartReady:
            if Settings.get('Server','reconnect-on-error') =="True":
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    autoRestart = True
        if autoRestart:
            self.onReconnectTool()
        else:
            self.stopTool() 

    def onToolDisconnection(self, byServer=False, inactivityServer=False):
        """
        On tool disconnection
        """
        if (byServer or inactivityServer):
            if byServer:
                self.LogError.emit("<< Disconnection by the remote server")
            if inactivityServer:
                self.LogError.emit("<< Inactivity detected with the remote server")
            autoRestart = False
            if self.featureRestartReady:
                if Settings.get('Server','reconnect-on-disconnect') =="True":
                    if self.currentReconnect <= self.maxReconnect:
                        self.currentReconnect += 1
                        autoRestart = True
            
            if autoRestart:
                self.onReconnectTool()
            else:
                self.stopTool()
        else:
            pass

    def onResolveHostnameFailed(self, err):
        """
        On resolve hostname failed
        """
        self.LogError.emit("<< Hostname resolution failed: %s" % err.lower())
        self.stopTool()

    def onProxyConnectionError(self, err):
        """
        On prox connection error
        """
        self.LogError.emit("<< Proxy connection error: %s" % err.lower())
        self.stopTool()

    def onProxyConnectionTimeout(self, err):
        """
        On proxy connection timeout
        """
        self.LogError.emit("<< Proxy connection timeout: %s" % err.lower())
        autoRestart = False
        if self.featureRestartReady:
            if Settings.get('Server','reconnect-on-timeout') =="True":
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    autoRestart = True
                    
        if autoRestart:
            self.onReconnectTool()
        else:
            self.stopTool()

    def onProxyConnectionRefused(self, err):
        """
        On proxy connection refused
        """
        self.LogError.emit("<< Proxy connection refused: %s" % err.lower())
        autoRestart = False
        if self.featureRestartReady:
            if Settings.get('Server','reconnect-on-refused') =="True":
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    autoRestart = True
                    
        if autoRestart:
            self.onReconnectTool()
        else:
            self.stopTool()

    def onConnectionRefused(self, err):
        """
        On connection refused
        """
        self.LogError.emit("<< Connection refused: %s" % err.lower())
        autoRestart = False
        if self.featureRestartReady:
            if Settings.get('Server','reconnect-on-refused') =="True":
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    autoRestart = True
                    
        if autoRestart:
            self.onReconnectTool()
        else:
            self.stopTool()

    def onConnectionTimeout(self, err):
        """
        On connection timeout
        """
        self.LogError.emit("<< Connection timeout: %s" % err.lower())
        autoRestart = False
        if self.featureRestartReady:
            if Settings.get('Server','reconnect-on-timeout') =="True":
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    autoRestart = True
                    
        if autoRestart:
            self.onReconnectTool()
        else:
            self.stopTool()
 
    def onRegistrationRefused(self, err):
        """
        On registration refused
        """
        self.LogError.emit("<< Registration refused: %s" % err.lower())
        self.stopTool()

    def onRegistrationFailed(self, err):
        """
        On registration failed
        """
        self.LogError.emit("<< Registration failed: %s" % err.lower())
        self.stopTool()

    def onRegistrationSuccessful(self):
        """
        On registration succesful
        """
        self.featureRestartReady = True
        self.currentReconnect = 0
        self.toolObj.regRequest = None
        self.toolObj.prepareTempDir()
        
        if self.toolType == TOOL_AGENT or self.toolType == TOOL_EXT_AGENT:  
            self.LogSuccess.emit("<< Agent successfully registered.")
        else:
            self.LogSuccess.emit("<< Probe successfully registered.")
            
        self.mainApp.updateTabName(self, tabText="%s (starting)" % self.toolName)
        
        if self.toolType == TOOL_EXT_AGENT or self.toolType == TOOL_EXT_PROBE:

            self.StartExternalTool.emit(self, self.toolType, self.toolPlugin, self.toolName)

        else:
            self.mainApp.setTrayIconToolTip( "(Running)")
            self.toolObj.initAfterRegistration()
        
class ComboBoxEnhanced(QComboBox):
    """
    Combo box widget
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(ComboBoxEnhanced, self).__init__()

    def addSeparator(self, label):
        """
        Add separator in the list
        """
        item = QStandardItem(label)
        item.setSelectable(False)
        
        font = item.font()
        font.setBold(True)
        font.setItalic(True)
        item.setFont(font)
        
        self.model().appendRow( item )
        
    def addAgent(self, name):
        """
        Add agent to the list
        """
        item = QStandardItem( " %s" % name)
        item.setData(TOOL_AGENT)
        
        font = item.font()
        font.setPixelSize (15)
        item.setFont(font)
        
        self.model().appendRow(item)
        
    def addProbe(self, name):
        """
        Add probe to the list
        """
        item = QStandardItem( " %s" % name)
        item.setData(TOOL_PROBE)
        
        font = item.font()
        font.setPixelSize (15)
        item.setFont(font)
        
        self.model().appendRow(item)
        
    def addExtAgent(self, name):
        """
        Add external agent to the list
        """
        item = QStandardItem( " %s" % name)
        item.setData(TOOL_EXT_AGENT)
        
        font = item.font()
        font.setPixelSize (15)
        item.setFont(font)
        
        self.model().appendRow(item)
        
    def addExtProbe(self, name):
        """
        Add external probe to the list
        """
        item = QStandardItem( " %s" % name)
        item.setData(TOOL_EXT_PROBE)
        
        font = item.font()
        font.setPixelSize (15)
        item.setFont(font)
        
        self.model().appendRow(item)
        
class PluginObj(object):
    """
    Plugin object
    """
    def __init__(self, description=None, withIde=False):
        """
        Constructor
        """
        self.__RESUME__ = "no description"
        if description is not None:
            self.__RESUME__ = description
        self.__WITH_IDE__ = withIde
        
class OptionPage(QWidget):
    """
    Option page widget
    """
    DeployTool = pyqtSignal(int)  
    def __init__(self, parent):
        """
        Constructor
        """
        super(OptionPage, self).__init__()
       
        self.nbPluginSaved = 0
        self.mainApp = parent
        
        self.defaultProxyHttpAddr = Settings.get( 'Server', 'addr-proxy-http' )
        self.defaultProxyHttpPort = Settings.get( 'Server', 'port-proxy-http' )

        self.createWidget()
        self.createConnections()
        
        self.initComboTools()
        
    def createConnections(self):
        """
        Create qt connections
        """
        self.deployButton.clicked.connect(self.deployTool)
        self.deleteButton.clicked.connect(self.deleteTool)
        self.startButton.clicked.connect(self.startTool)
        
        self.withProxyCheckBox.stateChanged.connect(self.enableProxy)
        self.autoMinimize.stateChanged.connect(self.onAutoMinimizeCfgChanged)
        self.autoStartup.stateChanged.connect(self.onAutoStartupCfgChanged)
        self.autoReconnect.stateChanged.connect(self.onAutoReconnectCfgChanged)

        self.typeComboBox.currentIndexChanged[int].connect(self.onTypeComboChanged)
        self.ideButton.clicked.connect(self.openIDE)
        self.listTools.itemClicked.connect(self.onToolSelected)

    def createWidget(self):
        """
        Create qt widget
        """
        # select plugin to start
        if sys.platform == "win32" :
            self.nameEdit = QLineEdit( "%s" % Settings.get( 'DefaultWin','agent-name' ) )
            self.descriptionEdit = QLineEdit( Settings.get( 'DefaultWin','agent-description' ) )
        elif sys.platform.startswith("linux") :
            self.nameEdit = QLineEdit( "%s" % Settings.get( 'DefaultLinux','agent-name' ) )
            self.descriptionEdit = QLineEdit( Settings.get( 'DefaultLinux','agent-description' ) )
        else:
            self.nameEdit = QLineEdit( "agent.unknown.example01" )
            self.descriptionEdit = QLineEdit( "Remote Unknown Tool" )
            
        self.typeLabel = QLabel()
        fontType = QFont()
        fontType.setItalic(True)
        self.typeLabel.setFont(fontType)
        
        self.purposeLabel = QLabel()
        fontPurpose = QFont()
        fontPurpose.setItalic(True)
        self.purposeLabel.setFont(fontPurpose)
   
        self.typeComboBox = ComboBoxEnhanced(self)
        self.typeComboBox.setMinimumHeight(25)
 
        self.ideButton = QPushButton("Open IDE")
        self.ideButton.setEnabled(False)
        

        toolLayout = QGridLayout()
        
        toolLayout.addWidget( QLabel("Register Agent/Probe"), 0, 0  )
        toolLayout.addWidget( QLabel("Name:"), 1, 1 )
        toolLayout.addWidget(self.nameEdit, 1, 2)
        
        toolLayout.addWidget(QLabel("Selection:"), 2, 1)
        toolLayout.addWidget(self.typeComboBox, 2, 2)
        toolLayout.addWidget(self.ideButton, 2, 3)
        
        toolLayout.addWidget( QLabel("Type:"), 3, 1)
        toolLayout.addWidget(self.typeLabel, 3, 2)
        
        toolLayout.addWidget(QLabel("Purpose:"), 4, 1)
        toolLayout.addWidget(self.purposeLabel, 4, 2)
        
        toolLayout.addWidget( QLabel("Description:"), 5, 1)
        toolLayout.addWidget(self.descriptionEdit, 5, 2)
        toolLayout.addWidget( QLabel(""), 6, 0)
        
        self.sep1 = QFrame()
        self.sep1.setGeometry(QRect(110, 221, 51, 20))
        self.sep1.setFrameShape(QFrame.HLine)
        self.sep1.setFrameShadow(QFrame.Sunken)
        
        # controler ip
        self.controlerIpEdit = QLineEdit( Settings.get('Server','ip') )
        self.controlerPortEdit = QLineEdit( Settings.get('Server','port') )
        validator2Proxy = QIntValidator (self)
        self.controlerPortEdit.setValidator(validator2Proxy)
        
        self.proxyHttpAddrEdit = QLineEdit(self.defaultProxyHttpAddr)
        self.proxyHttpAddrEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.proxyHttpAddrEdit.setDisabled(True)
        self.proxyHttpPortEdit = QLineEdit(self.defaultProxyHttpPort)
        self.proxyHttpPortEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.proxyHttpPortEdit.setDisabled(True)
        validatorProxy = QIntValidator (self)
        self.proxyHttpPortEdit.setValidator(validatorProxy)
        self.proxyHttpPortEdit.setMinimumWidth(60)
        
        self.proxyLoginEdit = QLineEdit()
        self.proxyLoginEdit.setDisabled(True)
        self.proxyPasswordEdit = QLineEdit()
        self.proxyPasswordEdit.setEchoMode( QLineEdit.Password )
        self.proxyPasswordEdit.setDisabled(True)
        
        # proxy support
        self.withProxyCheckBox = QCheckBox( "Use a HTTPS proxy server" )
        if QtHelper.str2bool(Settings.get( 'Server','proxy-active' )):
            self.withProxyCheckBox.setChecked(True)
            self.proxyHttpAddrEdit.setDisabled(False)
            self.proxyHttpPortEdit.setDisabled(False)
 
        self.deployButton = QPushButton(self.tr(" Deploy the tool "), self)
        self.deleteButton = QPushButton(self.tr("Delete"), self)
        self.deleteButton.setEnabled(False)
        self.startButton = QPushButton(self.tr("Start"), self)
        self.startButton.setEnabled(False)
        
        tool2Layout = QGridLayout()
        tool2Layout.addWidget( QLabel( "My %s" % Settings.get( 'Common','acronym-server' ) ), 0, 0  )
        
        tool2Layout.addWidget(QLabel("Address:"), 1, 1)
        tool2Layout.addWidget(self.controlerIpEdit, 1, 2)
        tool2Layout.addWidget(self.deployButton, 1, 3)
        tool2Layout.addWidget(QLabel("Port:"), 2, 1)
        tool2Layout.addWidget(self.controlerPortEdit, 2, 2)
        tool2Layout.addWidget(self.withProxyCheckBox, 3, 1)
        tool2Layout.addWidget(QLabel("Proxy Address:"), 4, 1)
        tool2Layout.addWidget(self.proxyHttpAddrEdit, 4, 2)
        tool2Layout.addWidget(QLabel("Proxy Port:"), 5, 1)
        tool2Layout.addWidget(self.proxyHttpPortEdit, 5, 2)
        tool2Layout.addWidget( QLabel(""), 6, 0)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addWidget(self.startButton)

        self.autoMinimize = QCheckBox( 'Automatic minimize toolbox on startup' )

        if Settings.get('Common','minimize-on-startup') =="True":
            self.autoMinimize.setCheckState(2)
        else:
            self.autoMinimize.setCheckState(0)  

        self.autoStartup = QCheckBox( 'Save and automatic connect on startup' )
        if Settings.get('Common','connect-on-startup') =="True":
            self.autoStartup.setCheckState(2)
        else:
            self.autoStartup.setCheckState(0)   
            
        self.autoReconnect = QCheckBox( 'Automatic reconnect on error after registration' )
        if Settings.get('Server','reconnect-on-error') =="True":
            self.autoReconnect.setCheckState(2)
        else:
            self.autoReconnect.setCheckState(0)   
            
        self.delayStartupEdit = QLineEdit( Settings.get('Common','delay-startup') )
        self.delayStartupEdit.setValidator(QIntValidator(self.delayStartupEdit))
        
        tool3Layout = QGridLayout()
        tool3Layout.addWidget( QLabel("Miscellaneous"), 0, 0  )
        tool3Layout.addWidget( self.autoMinimize, 1, 1  )
        tool3Layout.addWidget( self.autoStartup, 1, 2  )
        tool3Layout.addWidget( self.autoReconnect, 2, 1  )
        
        tool3Layout.addWidget( QLabel("Delaying automatic deployment (in seconds)"), 4, 1 )
        tool3Layout.addWidget( self.delayStartupEdit, 4, 2  )
        
        # list of tool
        self.listTools = QListWidget()
        
        tool4Layout = QGridLayout()
        tool4Layout.addWidget( QLabel("Tools saved"), 0, 0  )
        tool4Layout.addWidget( self.listTools, 1, 1 )

        # final layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(toolLayout)
        mainLayout.addLayout(tool2Layout)
        mainLayout.addLayout(tool3Layout)
        mainLayout.addLayout(tool4Layout)
        mainLayout.addLayout(buttonLayout)

        self.setMinimumWidth(600)
                
        self.setLayout(mainLayout)

    def initComboTools(self):
        """
        Init the combox
        """
        # load combobox with agent
        # insert a separator 
        # and finaly load combobox with probe
        tmp_agt = []
        for pluginId, pluginObj in plugins.items():
            plugType, plugId  = pluginId  
            if not plugType: tmp_agt.append( "%s" % plugId )    
        tmp_agt = sorted(tmp_agt)
        
        tmp_prb = []
        for pluginId, pluginObj in plugins.items():
            plugType, plugId  = pluginId
            if plugType: tmp_prb.append( "%s" % plugId )
        tmp_prb = sorted(tmp_prb)
        
        # new in v8.2
        tmp_ext_agt = []
        for pluginId, plugMore in PLUGINS_AGENT_EXTERNAL.items():
            plugPath, plugExe, pluginCfg = plugMore
            tmp_ext_agt.append( "%s" % pluginCfg["plugin"]["name"].lower() )
        tmp_ext_agt = sorted(tmp_ext_agt)
        
        tmp_ext_prb = []
        for pluginId, plugMore in PLUGINS_PROBE_EXTERNAL.items():
            plugPath, plugExe, pluginCfg = plugMore
            tmp_ext_prb.append( "%s" % pluginCfg["plugin"]["name"].lower() )
        tmp_ext_prb = sorted(tmp_ext_prb)
        # end of new
            

        self.typeComboBox.addSeparator(label="Default Agents")
        for row in tmp_agt:
            self.typeComboBox.addAgent(row)

        if len(tmp_ext_agt):
            self.typeComboBox.addSeparator(label="External Agent(s)")
            for row in tmp_ext_agt:
                self.typeComboBox.addExtAgent(row)

        self.typeComboBox.addSeparator(label="Default Probes")
        for row in tmp_prb:
            self.typeComboBox.addProbe(row)

        if len(tmp_ext_prb):
            self.typeComboBox.addSeparator(label="External Probe(s)")
            for row in tmp_ext_prb:
                self.typeComboBox.addExtProbe(row)

        self.typeComboBox.setCurrentIndex(1)
        self.onTypeComboChanged(itemIndex = self.typeComboBox.currentIndex())
        
    def initListTools(self):
        """
        Init the list of tools
        """
        for i in xrange(50):
            try:
                toolInfo =  Settings.get('Tool_%s' % i ,'name')
            except ConfigParser.NoSectionError as e:
                pass
            else:
                self.nbPluginSaved = i
                
                toolType = Settings.getInt('Tool_%s' % i ,'type')
                toolName = Settings.get('Tool_%s' % i ,'name')
                toolPlugin = Settings.get('Tool_%s' % i ,'plugin')
                toolDescr = Settings.get('Tool_%s' % i ,'description')
                try:
                    toolIp = Settings.get('Tool_%s' % i ,'ip')
                except ConfigParser.NoOptionError as e:
                    toolIp = self.getControllerIp()
                try:
                    toolPort = Settings.get('Tool_%s' % i ,'port')
                except ConfigParser.NoOptionError as e:
                    toolPort = self.getControllerPort()
                try:
                    proxyEnable = Settings.getBool('Tool_%s' % i ,'proxy-enable')
                except ConfigParser.NoOptionError as e:
                    proxyEnable = self.getProxyEnable()
                try:
                    proxyIp = Settings.get('Tool_%s' % i ,'proxy-ip')
                except ConfigParser.NoOptionError as e:
                    proxyIp = self.getProxyIp()
                try:
                    proxyPort = Settings.get('Tool_%s' % i ,'proxy-port')
                except ConfigParser.NoOptionError as e:
                    proxyPort = self.getProxyPort()
                listItem = QListItemEnhanced(   
                                                toolId=self.nbPluginSaved,
                                                toolType=toolType, 
                                                toolName=toolName,
                                                toolPlugin=toolPlugin.strip(), 
                                                toolDescr=toolDescr,
                                                toolIp=toolIp,
                                                toolPort=toolPort,
                                                proxyEnable=proxyEnable,
                                                proxyIp=proxyIp,
                                                proxyPort=proxyPort,
                                            )
                self.listTools.addItem( listItem )
                if Settings.get('Common','connect-on-startup') =="True":
                    self.mainApp.automaticDeployTool(toolType, toolName, toolPlugin, toolDescr,
                                                    toolIp=toolIp, toolPort=toolPort, 
                                                    proxyEnable=proxyEnable, 
                                                    proxyIp=proxyIp, proxyPort=proxyPort)
                    
        # set the focus on the option page
        self.mainApp.mainTab.setCurrentIndex(0)

    def openIDE(self):
        """
        Open the external IDE
        """
        # get the current app
        curIndex = self.typeComboBox.currentIndex()
        pluginId =  self.typeComboBox.itemText(curIndex)
        pluginId = pluginId.strip()
        pluginType =  self.typeComboBox.itemData(curIndex, role=Qt.UserRole+1)
        if pluginType is None: 
            self.ideButton.setEnabled(False)
            return 
            
        # to support py2.7 and pyqt4 on linux
        if sys.version_info < (3,):
            pluginType = str(pluginType)
            
        # check combobox
        pluginDetected=None
        for pId, pluginObj in plugins.items():
            plugType, plugId  = pId
            if plugType == pluginType and pluginId == plugId:
                pluginDetected = pluginObj
                break

        # open the app
        if pluginDetected is not None:
            if pluginDetected.__WITH_IDE__:
                if sys.platform == "win32":
                    subprocess.Popen (['cmd.exe', '/c', pluginDetected.__APP_PATH__ ], shell=True)
    
    def onTypeComboChanged(self, itemIndex):
        """
        On type combo changed
        """
        pluginId =  self.typeComboBox.itemText(itemIndex)
        pluginId = pluginId.strip()
        pluginType =  self.typeComboBox.itemData(itemIndex, role=Qt.UserRole+1)

        if pluginType is None: 
            self.typeLabel.setText("")
            self.deployButton.setEnabled(False)
            self.purposeLabel.setText("")
            self.ideButton.setEnabled(False)
            return
        else:
            self.deployButton.setEnabled(True)
            
        # to support py2.7 and pyqt4 on linux
        if sys.version_info < (3,):
            pluginType = str(pluginType)
            
        pluginDetected=None
        for pId, pluginObj in plugins.items():
            plugType, plugId  = pId
            if plugType == pluginType and pluginId == plugId:
                pluginDetected = pluginObj
                break
                
        if pluginDetected is None:
            for plugId, plugMore in PLUGINS_AGENT_EXTERNAL.items():
                plugPath, plugExe, pluginCfg  = plugMore
                if pluginType == TOOL_EXT_AGENT and pluginCfg["plugin"]["name"].lower() == pluginId.lower():
                    pObj = PluginObj(pluginCfg["plugin"]['resume'], pluginCfg["plugin"]['with-ide'])
                    pluginDetected = pObj
                    break
                    
        if pluginDetected is not None:
            self.typeLabel.setText(TOOLS_DESCR[pluginType])
            self.purposeLabel.setText(pluginDetected.__RESUME__)
            if pluginDetected.__WITH_IDE__:
                self.ideButton.setEnabled(True)
            else:
                self.ideButton.setEnabled(False)

    def onAutoStartupCfgChanged(self, state):
        """
        On autostartup timeout config changed
        """
        stateCfg = "False"
        if state == 2: stateCfg = "True"
        Settings.set('Common','connect-on-startup', stateCfg)
        Settings.save()
        
    def onAutoReconnectCfgChanged(self, state):
        """
        On auto reconnect configuration changed
        """
        stateCfg = "False"
        if state == 2: stateCfg = "True"
        Settings.set('Server','reconnect-on-inactivity', stateCfg)
        Settings.set('Server','reconnect-on-timeout', stateCfg)
        Settings.set('Server','reconnect-on-refused', stateCfg)
        Settings.set('Server','reconnect-on-error', stateCfg)
        Settings.set('Server','reconnect-on-disconnect', stateCfg)
        Settings.save()
        
    def onAutoMinimizeCfgChanged(self, state):
        """
        On autominimize timeout config changed
        """
        stateCfg = "False"
        if state == 2: stateCfg = "True"
        Settings.set('Common','minimize-on-startup', stateCfg)
        Settings.save()
        
    def enableProxy(self, state):
        """
        Enable proxy
        """
        if state != 0:
            self.proxyHttpAddrEdit.setEnabled(True)
            self.proxyHttpPortEdit.setEnabled(True)
        else:
            self.proxyHttpAddrEdit.setEnabled(False)
            self.proxyHttpPortEdit.setEnabled(False)
        
    def getProxyIp(self):
        """
        Get the proxy ip
        """
        return self.proxyHttpAddrEdit.text()
        
    def getProxyPort(self):
        """
        Get the proxy port
        """
        return self.proxyHttpPortEdit.text()
        
    def getProxyEnable(self):
        """
        Get if proxy if enabled
        """
        if self.withProxyCheckBox.checkState() == Qt.Checked:
            return True
        else:
            return False
        
    def getControllerIp(self):
        """
        Get the server ip
        """
        return self.controlerIpEdit.text()
        
    def getControllerPort(self):
        """
        Get the server port 
        """
        return self.controlerPortEdit.text()
        
    def getToolName(self):
        """
        Get the tool name
        """
        return self.nameEdit.text()
        
    def getToolPlugin(self):
        """
        Get the type of plugin
        """
        return self.typeComboBox.currentText().strip()
        
    def getToolDescription(self):
        """
        Get the description of the tool
        """
        return self.descriptionEdit.text()
        
    def getToolIp(self):
        """
        Get the description of the tool
        """
        return self.removeServerEdit.text()
    
    def startTool(self):
        """
        Start tool from list
        """
        currentItem = self.listTools.currentItem()
        if currentItem is None:
            self.startButton.setEnabled(False)
        else:
            self.mainApp.automaticDeployTool(
                                toolType=int(currentItem.toolType), 
                                toolName=currentItem.toolName,
                                toolPlugin=currentItem.toolPlugin,
                                toolDescription=currentItem.toolDescr,
                                toolIp=currentItem.toolIp,
                                proxyEnable=currentItem.proxyEnable,
                                proxyIp=currentItem.proxyIp,
                                proxyPort=currentItem.proxyPort,
                                ignoreDelayedStartup=True,
                            )
        
    def deleteTool(self):
        """
        Delete tool
        """
        currentItem = self.listTools.currentItem()
        if currentItem is None:
            self.deleteButton.setEnabled(False)
        else:
            for i in xrange(50):
                try:
                    toolInfo =  Settings.get('Tool_%s' % i ,'name')
                except ConfigParser.NoSectionError as e:
                    pass
                else:
                    if toolInfo == currentItem.toolName:
                        Settings.removeSection('Tool_%s' % i )
                        Settings.save()
                        break

            rowId = self.listTools.row( currentItem )
            w = self.listTools.takeItem ( rowId )
            del w
            
            if not self.listTools.count():
                self.deleteButton.setEnabled(False)
                self.startButton.setEnabled(False)
            
    def onToolSelected(self):
        """
        On selected tool event
        """
        self.deleteButton.setEnabled(True)
        self.startButton.setEnabled(True)
        
    def deployTool(self):
        """
        Deploy Agent/Probe
        """
        toolName = self.nameEdit.text()
        if not len(toolName):
            QMessageBox.critical(None, "Start Agent/Probe", "Agent/probe name is missing!")
            return
        
        toolDescr = self.descriptionEdit.text()
        if not len(toolDescr):
            QMessageBox.critical(None, "Start Agent/Probe", "Agent/probe description is missing!")
            return  
            
        serverIp = self.controlerIpEdit.text()
        if not len(serverIp):
            QMessageBox.critical(None, "Start Agent/Probe", "Test server IP is missing!")
            return     
            
        serverPort = self.controlerPortEdit.text()
        if not len(serverPort):
            QMessageBox.critical(None, "Start Agent/Probe", "Test server port is missing!")
            return      
            
        proxyIp = self.proxyHttpAddrEdit.text()
        proxyPort = self.proxyHttpPortEdit.text()
        supportProxy = self.withProxyCheckBox.isChecked()
        if supportProxy:
            if not len(proxyIp):
                QMessageBox.critical(None, "Start Agent/Probe", "Proxy IP is missing!")
                return 
            if not len(proxyPort):
                QMessageBox.critical(None, "Start Agent/Probe", "Proxy port is missing!")
                return  

        pluginName = self.typeComboBox.currentText()
        internalType = TOOL_AGENT
        for (tType, tDescr) in TOOLS_DESCR.items():
            if tDescr == self.typeLabel.text():
                internalType = tType
                break

        saveTool = self.autoStartup.isChecked()
        if saveTool:
            self.nbPluginSaved += 1

            # save in settings
            Settings.addSection('Tool_%s' % self.nbPluginSaved)
            Settings.set('Tool_%s' % self.nbPluginSaved,'name', str(toolName) )
            Settings.set('Tool_%s' % self.nbPluginSaved,'plugin', str(pluginName).strip() )
            Settings.set('Tool_%s' % self.nbPluginSaved,'type', str(internalType) )
            Settings.set('Tool_%s' % self.nbPluginSaved,'description', str(toolDescr) )
            # new in v7
            Settings.set('Tool_%s' % self.nbPluginSaved,'ip', str(serverIp) )
            Settings.set('Tool_%s' % self.nbPluginSaved,'port', str(serverPort) )
            Settings.set('Tool_%s' % self.nbPluginSaved,'proxy-enable', str(supportProxy) )
            Settings.set('Tool_%s' % self.nbPluginSaved,'proxy-ip', str(proxyIp) )
            Settings.set('Tool_%s' % self.nbPluginSaved,'proxy-port', str(proxyPort) )
            
            Settings.save()
            
            # adding in list
            listItem = QListItemEnhanced(   toolId = self.nbPluginSaved,
                                            toolType=internalType, 
                                            toolName=toolName,
                                            toolPlugin=pluginName, 
                                            toolDescr=toolDescr,
                                            toolIp=str(serverIp),
                                            toolPort=str(serverPort),
                                            proxyEnable=supportProxy,
                                            proxyIp=str(proxyIp),
                                            proxyPort=str(proxyPort),
                                        )
            self.listTools.addItem( listItem )

        # emit the signal
        if internalType == TOOL_AGENT:
            self.DeployTool.emit(TOOL_AGENT)
        elif internalType == TOOL_PROBE:
            self.DeployTool.emit(TOOL_PROBE)
        elif internalType == TOOL_EXT_AGENT:
            self.DeployTool.emit(TOOL_EXT_AGENT)
        elif internalType == TOOL_EXT_PROBE:
            self.DeployTool.emit(TOOL_EXT_PROBE)
        else:
            pass
            
class Window(QDialog):
    """
    Main window dialog
    """
    def __init__(self):
        """
        Constructor for the main window
        """
        super(Window, self).__init__()

        self.mainPage = None
        
        # new in 8.2
        self.pluginsStarted = {}
        self.pluginsBuffers = {}
        # loading plugin
        self.loadingPlugins()
        # end of new
        
        self.createDialog()
        self.createActions()
        self.createTrayIcon()
        self.createConnections()
        self.createToolbar()

        self.loadingPluginsActions()
        
        # cleanup temp folder
        if sys.platform == "win32" :
            dirpath = "%s\\%s\\" % (Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ))
        else:
            dirpath = "%s/%s/" % (Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ))
           
        # cleanup tmp area
        try:
            for filename in os.listdir(dirpath):
                filepath = os.path.join(dirpath, filename)
                try:
                    shutil.rmtree(filepath)
                except OSError:
                    os.remove(filepath)
        except Exception as e:
            pass
            
        # init tools from settings
        self.mainPage.initListTools()

    def loadingPlugins(self):
        """
        Loading all plugins
        """
        files=os.listdir("%s//Plugins//" % (QtHelper.dirExec()))
        for x in files:
            
            curpath=os.path.join( "%s//Plugins//" % (QtHelper.dirExec()), x)
            if not os.path.isfile( curpath ):
                for y in os.listdir( curpath ):
                    fullpath=os.path.join( "%s//Plugins//%s//%s" % (QtHelper.dirExec(), x, y) )
                    if os.path.isfile(fullpath):
                        if y.endswith(".exe"):
                        
                            # read the json config
                            configJson = {}
                            try:
                                f = open("%s/config.json" % ( "%s//Plugins//%s//" % (QtHelper.dirExec(), x) ), "br" )
                                configStr = f.read()
                                if sys.version_info > (3,): # python 3 support
                                    configJson = json.loads( str(configStr, "utf8") )
                                else:
                                    configJson = json.loads( configStr )
                                f.close()
                            except Exception as e:
                                print(e)

                            if configJson["plugin"]["type"] == "agent":
                                pluginId = configJson["plugin"]["name"]
                                PLUGINS_AGENT_EXTERNAL[pluginId.lower()] = ( "%s//Plugins//%s//" % (QtHelper.dirExec(), x), y, configJson)
                            elif configJson["plugin"]["type"] == "probe":
                                pluginId = x
                                PLUGINS_PROBE_EXTERNAL[pluginId.lower()] = ( "%s//Plugins//%s//" % (QtHelper.dirExec(), x), y, configJson)
                            else:
                                pass    
        
    def loadingPluginsActions(self):
        """
        Loading all actions for plugins
        """
        for plugId, plugMore in PLUGINS_AGENT_EXTERNAL.items():
            
            plugPath, plugExe, pluginCfg = plugMore
            
            # read icon
            icon = None
            try:
                f = open("%s/plugin.png" % (plugPath), "rb" )
                icon = f.read()
                f.close()
            except Exception as e:
                print(e)
            
            # read about
            if icon is not None:
                p = QPixmap()
                p.loadFromData(icon, format="png")
            
                plugAction = QtHelper.createAction(parent=self, label="About\n%s Plugin" % pluginCfg["plugin"]["name"], icon=QIcon(p), 
                                                callback=self.onAboutPlugin, cb_arg= { 'plugId': plugId, 'plugPath': plugPath,
                                                                                'plugCfg': pluginCfg } )
                self.dockToolbar.addAction(plugAction)
            else:
                plugAction =  QtHelper.createAction( parent=self, label="About\n%s Plugin" % pluginCfg["plugin"]["name"],
                                                callback=self.onAboutPlugin, cb_arg={ 'plugId': plugId, 'plugPath': plugPath,
                                                                                'plugCfg': pluginCfg} )
                self.dockToolbar.addAction(plugAction)
                
    def onAboutPlugin(self, plugInfo):
        """
        About plugin event
        """
        plugId = plugInfo['plugId']
        plugPath = plugInfo['plugPath']
        plugCfg = plugInfo['plugCfg']

        QMessageBox.information(self, "About %s Plugin" % plugCfg["plugin"]["name"], 
                                    plugCfg["plugin"]['about'] % (plugCfg["plugin"]["name"],
                                    plugCfg["plugin"]['version'], Settings.get( 'Common', 'name' )))
   
    def createConnections(self):
        """
        Create qt connections
        """
        self.mainPage.DeployTool.connect(self.deployTool)
        self.trayIcon.activated.connect(self.onTrayIconActivated)
        
    def onTrayIconActivated(self, reason):
        """
        On tray icon activated
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()

    def onStartExternalTool(self, toolPage, pluginType, pluginId, pluginName):
        """
        On start a external tool event
        """
        if pluginType == TOOL_EXT_AGENT:
            plugPath, plugExe, pluginCfg  = PLUGINS_AGENT_EXTERNAL[pluginId]

            p = PluginProcess(self, cmd='"%s/%s"' % (plugPath, plugExe), toolPage=toolPage, tmpArea=toolPage.plugin().getTemp())
            toolPage.pluginProcess = p
            p.DataReceived.connect(self.onPluginData)
            p.startPlugin()
            
            self.updateTabName(toolPage, tabText="%s (running)" % pluginName)
            
        elif pluginType == TOOL_EXT_PROBE:
            plugPath, plugExe, pluginCfg  = PLUGINS_PROBE_EXTERNAL[pluginId]
            
            p = PluginProcess(self, cmd='"%s/%s"' % (plugPath, plugExe), toolPage=toolPage, tmpArea=toolPage.plugin().getTemp())
            toolPage.pluginProcess = p
            p.DataReceived.connect(self.onPluginData)
            p.startPlugin()
            
        else:
            pass
        
    def onPluginData(self, data, plugin):
        """
        On data received from plugin
        """
        if plugin in self.pluginsBuffers:
            self.pluginsBuffers[plugin] += data
        else:
            self.pluginsBuffers.update( {plugin: data } )
            
        pdus = self.pluginsBuffers[plugin].split(b"\r\n")
        for pdu in pdus[:-1]:
            try:
                datagramDecoded = base64.b64decode(pdu)
                if sys.version_info > (3,): # python 3 support
                    messageJson = json.loads( str(datagramDecoded, "utf8") )
                else:
                    messageJson = json.loads( datagramDecoded )
            except Exception as e:
                pass
            else:
                self.onPluginMessage(msg=messageJson, plugProcess=plugin)
        self.pluginsBuffers[plugin] = pdus[-1]
        
    def onPluginMessage(self, msg, plugProcess):
        """
        On message received from plugin
        """
        if msg['cmd'] == 'register' and msg['id'].lower() not in self.pluginsStarted :
            if plugProcess.widgetPage().plugin() is None: return
            
            self.pluginsStarted.update( {msg['id'].lower() : (msg['name'], msg['type'], plugProcess ) } )
            
            plugProcess.sendCommand( cmd='registered', more={'tmp-path': plugProcess.toolPage.plugin().getTemp()} )
            plugProcess.startKeepAlive()
            self.setTrayIconToolTip( "(Running)")
            
        elif msg['cmd'] == 'log-warning' and msg['id'].lower() in self.pluginsStarted :
            plugProcess.widgetPage().onToolLogWarningCalled(msg=msg['msg'])
            
        elif msg['cmd'] == 'log-success' and msg['id'].lower() in self.pluginsStarted :
            plugProcess.widgetPage().onToolLogSuccessCalled(msg=msg['msg'])
            
        elif msg['cmd'] == 'log-error' and msg['id'].lower() in self.pluginsStarted :
            plugProcess.widgetPage().onToolLogErrorCalled(msg=msg['msg'])
            
        elif msg['cmd'] in [ 'send-data', 'send-error', 'send-notify' ] and msg['id'].lower() in self.pluginsStarted :
            if plugProcess.widgetPage().plugin() is None: return
            
            pluginJson = ''
            if msg['in-data']:
                # read the file
                f = open( '%s/%s' % (plugProcess.toolPage.plugin().getTemp(), msg['data-id'] ), 'r')
                pluginData = f.read()
                f.close()

                pluginJson = json.loads( pluginData )
                
                # delete them
                os.remove( '%s/%s' % (plugProcess.toolPage.plugin().getTemp(), msg['data-id']  ) )
                
            if msg['cmd'] == 'send-notify' and msg['id'].lower() in self.pluginsStarted :
                if plugProcess.widgetPage().plugin() is None: return
                
                plugProcess.widgetPage().plugin().sendNotify(request=msg['request'], data=pluginJson)
                
            elif msg['cmd'] == 'send-data' and msg['id'].lower() in self.pluginsStarted :
                if plugProcess.widgetPage().plugin() is None: return
                
                plugProcess.widgetPage().plugin().sendData(request=msg['request'], data=pluginJson)
                
            elif msg['cmd'] == 'send-error' and msg['id'].lower() in self.pluginsStarted :
                if plugProcess.widgetPage().plugin() is None: return
                
                plugProcess.widgetPage().plugin().sendError(request=msg['request'], data=pluginJson)
            else:
                pass
        
        elif msg['cmd'] == "probe-started"  and msg['id'].lower() in self.pluginsStarted :
            if plugProcess.widgetPage().plugin() is None: return
            
            plugProcess.widgetPage().plugin().startResponse(tid=msg['tid'], body=msg['body'])
            
        elif msg['cmd'] == "probe-stopped"  and msg['id'].lower() in self.pluginsStarted :
            if plugProcess.widgetPage().plugin() is None: return
            
            plugProcess.widgetPage().plugin().stopResponse(tid=msg['tid'], body = msg['body'], 
                                                            additional = msg['additional'], 
                                                            dataToSend=msg['dataToSend'])
            
        else:
            pass
        
    def automaticDeployTool(self, toolType, toolName, toolPlugin, toolDescription, toolIp=None, toolPort=None, 
                                    proxyEnable=False, proxyIp=None, proxyPort=None, ignoreDelayedStartup=False):
        """
        Automatic deploy tool on boot
        """
        toolPage = ToolPage(parent=self, delayStartup=int(Settings.get( 'Common' ,'delay-startup')) )
        toolPage.StopTool.connect(self.onStopTool)
        toolPage.TakeScreenshot.connect(self.onTakeScreenshot)
        toolPage.StartExternalTool.connect(self.onStartExternalTool)
        
        # configure params
        toolPage.setTool(   
                            toolName=toolName, 
                            toolType=int(toolType), 
                            toolPlugin=toolPlugin, 
                            toolDescr=toolDescription,
                            toolIp=toolIp
                        )
            
        controllerIp = toolIp
        if toolIp is None: controllerIp=Settings.get( 'Server' ,'ip')
        controllerPort = toolPort
        if toolPort is None: controllerPort=Settings.get( 'Server' ,'port')
        
        controllerProxyIp = proxyIp
        if proxyIp is None: controllerProxyIp=Settings.get( 'Server' ,'addr-proxy-http')
        controllerProxyPort = proxyPort
        if proxyPort is None: controllerProxyPort=Settings.get( 'Server' ,'port-proxy-http')
        
        toolPage.setNetwork(
                            controllerIp=controllerIp, 
                            controllerPort=controllerPort,
                            proxyEnable=proxyEnable, 
                            proxyIp=controllerProxyIp, 
                            proxyPort=controllerProxyPort
                        )
        
        # select icon 
        toolIcon = QIcon(':/agent.png')
        if toolType == TOOL_PROBE or toolType == TOOL_EXT_PROBE: 
            toolIcon = QIcon(':/probe.png')
        
        # create the tab and set as current
        self.mainTab.addTab( toolPage, toolIcon, "%s (registering)" % toolName )
        self.mainTab.setCurrentIndex( self.mainTab.count()-1 )
        
        if ignoreDelayedStartup:
            toolPage.startTool()
        else:
            toolPage.startToolDelayed()
        
    def setTrayIconToolTip(self, msg):
        """
        Set the tray icon tooltip
        """
        self.trayIcon.setToolTip( "%s %s" % (Settings.get('Common', 'name'), msg) )
        
    def deployTool(self, toolType):
        """
        Deploy a tool (agent or probe)
        """
        toolPage = ToolPage(parent=self)
        toolPage.StopTool.connect(self.onStopTool)
        toolPage.TakeScreenshot.connect(self.onTakeScreenshot)
        toolPage.StartExternalTool.connect(self.onStartExternalTool)
        
        # configure params
        toolPage.setTool(   
                            toolName=self.mainPage.getToolName(), 
                            toolType=int(toolType), 
                            toolPlugin=self.mainPage.getToolPlugin(), 
                            toolDescr=self.mainPage.getToolDescription(),
                            toolIp=self.mainPage.getControllerIp()
                        )
        toolPage.setNetwork(
                            controllerIp=self.mainPage.getControllerIp(), 
                            controllerPort=self.mainPage.getControllerPort(), 
                            proxyEnable=self.mainPage.getProxyEnable(), 
                            proxyIp=self.mainPage.getProxyIp(), 
                            proxyPort=self.mainPage.getProxyPort()
                        )
        
        # select icon 
        toolIcon = QIcon(':/agent.png')
        if toolType == TOOL_PROBE or toolType == TOOL_EXT_PROBE: 
            toolIcon = QIcon(':/probe.png')
        
        # create the tab and set as current
        self.mainTab.addTab( toolPage, toolIcon, "%s (starting)" % self.mainPage.getToolName() )
        self.mainTab.setCurrentIndex( self.mainTab.count()-1 )

        toolPage.startTool()
        
    def updateTabName(self, pageInstance, tabText):
        """
        Update the name of the tab
        """
        # get index of the current tab and remove it
        tabId =  self.mainTab.indexOf(pageInstance)
        self.mainTab.setTabText(tabId, tabText)
        
    def onStopTool(self, toolWidget):
        """
        Called on stop tool
        """
        # get index of the current tab and remove it
        tabId =  self.mainTab.indexOf(toolWidget)
        self.mainTab.removeTab( tabId )
        
        # set the main page as current
        self.mainTab.setCurrentWidget( self.mainPage )
        
        #refresh tooltip of the tray icon
        if self.mainTab.count() == 1:
            self.setTrayIconToolTip(msg='(Stopped)')
            
    def info (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        Logger.info( "[%s] %s" % (self.__class__.__name__, txt ) )

    def trace (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        Logger.debug( "[%s] %s" % (self.__class__.__name__,  txt ) )

    def error (self, err):
        """
        Log error

        @param err:
        @type err:
        """
        Logger.error( "[%s] %s" % ( self.__class__.__name__,  err ) )

    def setVisible(self, visible):
        """
        Set as visible
        """
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super(Window, self).setVisible(visible)

    def closeEvent(self, event):
        """
        Close event
        """
        if self.trayIcon.isVisible():
            QMessageBox.information(self, "Systray",
                "The toolbox will keep running in the system tray. To "
                "terminate the toolbox, choose <b>Quit</b> in the "
                "context menu of the system tray entry.")
            self.hide()
            event.ignore()
    
    def createToolbar(self):
        """
        Create toolbar
        """
        self.dockToolbar.setObjectName("Toolbar")
        self.dockToolbar.addAction(self.minimizeAction)
        self.dockToolbar.addAction(self.quitAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.showRnAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.aboutAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))
        
    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowIcon(QIcon(':/toolbox.png'))
        
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }");
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.mainTab = QTabWidget( )
        self.mainTab.setTabPosition(QTabWidget.North)

        self.mainPage = OptionPage(parent=self)
        self.mainTab.addTab( self.mainPage, "Options" )
        
        globalLayout = QHBoxLayout()
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dockToolbar)
        mainLayout.addWidget(self.mainTab)

        globalLayout.addLayout(mainLayout)

        self.setLayout(globalLayout)
        
        self.setWindowTitle( "%s %s" % (Settings.get('Common', 'name'), Settings.getVersion()) )

        flags = Qt.WindowFlags()
        flags |= Qt.WindowMinimizeButtonHint
        flags |= Qt.WindowMaximizeButtonHint
        flags |= Qt.CustomizeWindowHint
        self.setWindowFlags(flags)
        
    def createActions(self):
        """
        Create qt actions
        """
        self.restoreAction = QAction("&Restore", self, triggered=self.showNormal)
        self.quitAction = QAction( QIcon(':/close.png'), "&Quit", self,triggered=self.quitTools)
        self.aboutAction = QAction( QIcon(':/about.png'), "&About", self,triggered=self.showAbout)
        self.minimizeAction = QAction( QIcon(':/minimize.png'),"&Minimize", self,triggered=self.minimizeWindow)
        self.showRnAction = QAction( QIcon(':/changelogs.png'),"&Change Logs", self,triggered=self.releaseNotes)
        
    def minimizeWindow(self):
        """
        Minimize window
        """
        self.hide()
    
    def quitTools(self):
        """
        Quit tools
        """
        # stop all plugins
        for i in xrange(self.mainTab.count()):
            page = self.mainTab.widget(i)
            if isinstance(page, ToolPage): page.onCleanup()
            
        # finalize
        self.onQuit()
        
    def showAbout(self):
        """
        Show about
        """
        url = Settings.instance().get( 'Common', 'url' )
        name = Settings.instance().get( 'Common', 'name' )
        
        about = [ "<b>%s %s</b>" % (name,Settings.getVersion()) ]
        about.append( "Part of the extensive testing project  (c) %s-%s" % (__BEGIN__,__END__) )
        about.append( "" ) 
        about.append( "Developed and maintained by <b>%s</b>" % __AUTHOR__ ) 
        about.append( "<i>%s python %s (%s) - Qt %s - PyQt %s on %s</i>" % ( 
                                    self.tr("Built with"), 
                                    platform.python_version(), platform.architecture()[0],
                                    QT_VERSION_STR, PYQT_VERSION_STR,
                                    platform.system() 
                     ) )
        about.append( "<i>%s %s</i>" % ( 
                                    self.tr("Built at: "), 
                                    __BUILDTIME__
                     ) )
        if QtHelper.str2bool(Settings.get( 'Common','portable' )): about.append( "%s" % self.tr("Portable edition") )
        about.append( "" )
        about.append( "Contact: <a href='mailto:%s'>%s</a>" %( __EMAIL__,__EMAIL__) )
        about.append( "Website: <a href='%s'>%s</a>" % (url,url) )

        about.append( "<hr />") 
        about.append( "<i>%s</i>" % __LICENCE__ ) 
        QMessageBox.about(self, self.tr("About %s" % name ), "<br />".join(about) )

    def createTrayIcon(self):
        """
        Create tray icon 
        """
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon(':toolbox.png'))        
        self.trayIcon.setToolTip( "%s (Stopped)" % Settings.get('Common', 'name') )
        
        self.trayIcon.show()    
 
    def releaseNotes (self):
        """
        Read the release notes
        """
        rn = ''
        try:
            fh = QFile(":/releasenotes.txt")
            fh.open(QFile.ReadOnly)
            rn = fh.readAll()
            
            # convert qbytearray to str
            if sys.version_info > (3,):
                rn = unicode(rn, 'utf8') # to support python3 
            else:
                rn = unicode(rn)
            
            fh.close()
        except Exception as e:
            self.error( "Unable to read release notes: " + str(e) )
        
        # open the dialog
        name = Settings.instance().get( 'Common', 'name' )
        rnDialog = RN.ReleaseNotesDialog( dialogName = name, parent = self)
        rnDialog.parseRn( text = rn )
        rnDialog.exec_()
        
    def onTakeScreenshot(self, tool, request, action, actionId, adapterId, testcaseName, replayId):
        """
        Resize the pixmap gived in argument
        """
        extension = Settings.get( 'Screenshot', 'extension' )
        
        # original screen
        if QT_VERSION_STR.startswith("4."):
            pixmap = QPixmap.grabWindow(QApplication.desktop().winId())
        else: # to support pyqt5
            primaryScreen = QGuiApplication.primaryScreen()
            pixmap = primaryScreen.grabWindow(QApplication.desktop().winId())
            
        # reduce the size of the original 
        scale= float( Settings.get( 'Screenshot', 'scale' ) )
        screenshot = pixmap.scaled( pixmap.width() * scale, pixmap.height() * scale, 
                                    Qt.KeepAspectRatio,  Qt.SmoothTransformation)
        
        #convert to raw
        byteArray = QByteArray()
        buffer = QBuffer(byteArray)
        buffer.open(QIODevice.WriteOnly)
        screenshot.save(buffer, extension, quality=int(Settings.get( 'Screenshot', 'quality' )) )

        if sys.version_info > (3,): # python 3 support
            screenIo = StringIO.BytesIO(byteArray)
        else:
            screenIo = StringIO.StringIO(byteArray)

        screenRaw =  screenIo.read()
        
        # generate a thumbnail
        scale= float( Settings.get( 'Screenshot', 'thumbnail-scale' ) )
        thumbnail = pixmap.scaled( pixmap.width() * scale, pixmap.height() * scale, 
                                   Qt.KeepAspectRatio,  Qt.SmoothTransformation)
        
        # convert to raw
        byteArray = QByteArray()
        buffer = QBuffer(byteArray)
        buffer.open(QIODevice.WriteOnly)
        thumbnail.save(buffer, extension, quality=int(Settings.get( 'Screenshot', 'thumbnail-quality' )) )

        if sys.version_info > (3,): # python 3 support
            thumbnailIo = StringIO.BytesIO(byteArray)
        else:
            thumbnailIo = StringIO.StringIO(byteArray)

        thumbnailRaw =  thumbnailIo.read()
        
        # finalize generation
        tool.plugin().onFinalizeScreenshot(request, action, actionId, adapterId, testcaseName, replayId, screenRaw, thumbnailRaw)

    def onQuit(self):
        """
        On quit
        """
        # cleanup all plugin process
        for pluginId, pluginInfos in self.pluginsStarted.items():
            pluginName, pluginType, pluginProcess = pluginInfos
            pluginProcess.kill()
            
        # hide the tray icon
        self.trayIcon.hide()  
        # quit
        qApp.quit()

if __name__ == '__main__':
    """
    Main
    """
    app = QApplication(sys.argv)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray", "I couldn't detect any system tray on this system.")
        sys.exit(1)

    if QT_VERSION_STR.startswith("5."): QApplication.setStyle( "Fusion" )
    
    # load internal qt translations for generic message box: en_US, fr_FR
    # according to the language configurated on the setting file
    translatorQt = QTranslator()
    translatorQt.load("qt_%s" % Settings.instance().get( 'Common', 'language' ), 
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath) )
    qApp.installTranslator(translatorQt)

    # install private translation file according to the language configurated on the setting file
    translator = QTranslator()
    translator.load(":/%s.qm" % Settings.instance().get( 'Common', 'language' ) )
    qApp.installTranslator(translator)

    QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    

    if QtHelper.str2bool(Settings.get( 'Common','minimize-on-startup' )):
        window.hide()
    else:
        window.show()
    sys.exit(app.exec_())
