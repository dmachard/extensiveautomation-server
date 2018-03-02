#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2018 Denis Machard
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
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

"""
Main module 
"""
# to support new print style on python 2.x
from __future__ import print_function 

# define the current version
__VERSION__ = '18.0.0'
# name of the main developer
__AUTHOR__ = 'Denis Machard'
# email of the main developer
__EMAIL__ = 'd.machard@gmail.com'
# list of contributors
__CONTRIBUTORS__ = [ "", "Emmanuel Monsoro (logo, graphical abstract engine)" ]
# list of contributors
__TESTERS__ = [ "Emmanuel Monsoro", "Thibault Lecoq"  ]
# project start in year
__BEGIN__="2010"
# year of the latest build
__END__="2018"
# date and time of the buid
__BUILDTIME__="10/02/2018 10:04:08"
# Redirect stdout and stderr to log file only on production
REDIRECT_STD=True
# disable warning from qt framework on production 
QT_WARNING_MODE=False
# workspace offline, for dev only
WORKSPACE_OFFLINE=False

LICENSE="""<i>This program is free software; you can redistribute it and/or
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
MA 02110-1301 USA</i>"""

# import standard modules
import sys
import os
import platform
import subprocess
import json
import uuid
import shutil
import base64 

if sys.platform == "win32":
    import sip
    sip.setdestroyonexit(False)

from Libs import QtHelper, Logger

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
# adding missing folders
if not os.path.exists( "%s/Logs/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Logs" % QtHelper.dirExec() )
if not os.path.exists( "%s/Update/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Update" % QtHelper.dirExec() )
if not os.path.exists( "%s/ResultLogs/" % QtHelper.dirExec() ):
    os.mkdir( "%s/ResultLogs" % QtHelper.dirExec() )
if not os.path.exists( "%s/Plugins/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Plugins" % QtHelper.dirExec() )
if not os.path.exists( "%s/Tmp/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Tmp" % QtHelper.dirExec() )

# Enable redirects output and error on production
if sys.version_info < (3,):
    if REDIRECT_STD:
        sys.stdout = open( "%s/Logs/output.log" % QtHelper.dirExec() ,"a", 0)
        sys.stderr = open( "%s/Logs/output.log" % QtHelper.dirExec() ,"a", 0)
else: # python 3 support
    if REDIRECT_STD:
        # 1 to select line buffering (only usable in text mode)
        sys.stdout = open( "%s/Logs/output_stdout.log" % QtHelper.dirExec() ,"a", 1) 
        sys.stderr = open( "%s/Logs/output_stderr.log" % QtHelper.dirExec() ,"a", 1)
        sys.excepthook = Logger.log_exception

# checking the presence of the settings file
# if not present then the application does not start
settingsFile = '%s/Files/settings.ini' % QtHelper.dirExec()
if not os.path.exists(settingsFile):
    print('The settings file is missing.')
    sys.exit(-1)

# Detect the operating system 
# For Unix systems, this is the lowercased OS name as returned
# by uname -s with the first part of the version as returned by uname -r
if sys.platform in [ "win32", "linux2", "linux", "darwin" ]:
    try:
        from PyQt4.QtGui import (QMainWindow, QApplication, QMessageBox, QTabWidget, QIcon, QToolButton, 
                                QAction, qApp, QDesktopServices, QFileDialog, QSystemTrayIcon, QDialog, 
                                QMenu, QWidget, QCursor, QTabBar, QColor, QPixmap, QSplashScreen, 
                                QProgressBar, QLabel, QFont, QVBoxLayout, QPushButton, QDesktopWidget)
        from PyQt4.QtCore import (QDateTime, QtDebugMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg, 
                                QThread, pyqtSignal, QT_VERSION_STR, PYQT_VERSION_STR, QSettings, 
                                QFile, Qt, QTimer, QSize, QUrl, QIODevice, QT_VERSION_STR, QEvent,
                                qInstallMsgHandler, QTranslator, QLibraryInfo, QObject, QProcess,
                                QByteArray, QLocale )
        from PyQt4.QtNetwork import (QUdpSocket, QHostAddress)
    except ImportError:
        from PyQt5.QtGui import (QIcon, QDesktopServices, QCursor, QColor, QPixmap, QFont)
        from PyQt5.QtWidgets import (QMainWindow, QApplication, QMessageBox, QTabWidget, 
                                QToolButton, QAction, qApp, QFileDialog, QSystemTrayIcon, 
                                QDialog, QMenu, QWidget, QTabBar, QSplashScreen,  QDesktopWidget,
                                QProgressBar, QLabel, QVBoxLayout, QPushButton)
        from PyQt5.QtCore import (QDateTime, QtDebugMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg, 
                                QThread, pyqtSignal, QT_VERSION_STR, PYQT_VERSION_STR, QSettings, 
                                QFile, Qt, QTimer, QSize, QUrl, QIODevice, QT_VERSION_STR, 
                                QTranslator, QLibraryInfo, QObject, QProcess, QEvent, QByteArray,
                                QLocale )
        from PyQt5.QtCore import qInstallMessageHandler as qInstallMsgHandler
        from PyQt5.QtNetwork import (QUdpSocket, QHostAddress)
else:
    print('os not supported')
    sys.exit(-1)

import zlib
try:
    import cStringIO
except ImportError: # support python 3
    import io as cStringIO
import time
try:
    import cPickle
except ImportError: # support python 3
    import pickle as cPickle
import base64
import inspect

import UserClientInterface as UCI
import RestClientInterface as RCI
import Workspace as WWorkspace
from Workspace.Repositories.LocalRepository import Repository
import TestResults
import ServerExplorer as WServerExplorer
from Resources import Resources
from Translations import Translations
import Workspace.FileModels.TestResult as TestResultModel
import Settings

import Recorder as WRecorder
import ReleaseNotes as RN
import Workspace.Repositories as Repositories

# set locale to english
if QtHelper.IS_QT5:
    newLocale = QLocale(QLocale().English)
    QLocale().setDefault(newLocale)

class MessageHandler(object):
    """
    Qt message handler
    """
    def __init__(self, qDebug=False, qWarning=QT_WARNING_MODE):
        """
        Constructor
        """
        self.qDebug = qDebug
        self.qWarning = qWarning
  
    def process(self, msgType, msg):
        """
        On process message
        """
        now = QDateTime.currentDateTime().toString(Qt.ISODate)

        if msgType == QtDebugMsg:
            if self.qDebug: print('%s [DEBUG] %s' % (now, msg))
            
        elif msgType == QtWarningMsg:
            if sys.version_info > (3,): # python 3 support
                if self.qWarning: print( '%s [WARNING] %s' % (now, msg), file=sys.stderr )
            else:
                if self.qWarning: print >> sys.stderr, '%s [WARNING] %s' % (now, msg)
                
        elif msgType == QtCriticalMsg:
            if sys.version_info > (3,): # python 3 support
                print( '%s [CRITICAL] %s' % (now, msg), file=sys.stderr )
            else:
                print >> sys.stderr, '%s [CRITICAL] %s' % (now, msg)
                
        elif msgType == QtFatalMsg:
            if sys.version_info > (3,): # python 3 support
                print( '%s [FATAL] %s' % (now, msg), file=sys.stderr )
            else:
                print >> sys.stderr, '%s [FATAL] %s' % (now, msg)

class PluginProcess(QProcess):
    """
    Plugin process
    """
    DataReceived = pyqtSignal(bytes, object)
    def __init__(self, parent, cmd):
        """
        Constructor
        """
        QProcess.__init__(self, parent)
        self.__cmd = cmd
        self.setProcessChannelMode(QProcess.MergedChannels)   
        self.readyReadStandardOutput.connect(self.onData)
        self.keepAliveTimer = QTimer(parent)
        self.keepAliveTimer.timeout.connect(self.sendKeepAlive)
        self.keepAliveTimer.setInterval(10000)
        
    def onData(self):
        """
        Called when data are received from plugin
        """
        # d -> qbytearray
        d = self.readAllStandardOutput()
        self.DataReceived.emit(d.data(), self)
        
    def startPlugin(self):
        """
        Start plugin
        """
        self.start(self.__cmd)
        
    def startKeepAlive(self):
        """
        Start keepalive
        """
        self.keepAliveTimer.start()
        
    def sendKeepAlive(self):
        """
        Send keepalive
        """
        self.sendCommand(cmd='keepalive')
        
    def sendCommand(self, cmd, data='', more={}):
        """
        Send command to the plugin
        """
        inData = False
        msg = {'cmd': cmd }
        
        # save data to temp area
        idFile = ''

        if len(data):
            try:
                idFile = "%s" % uuid.uuid4()
                pluginDataFile = '%s/Tmp/%s' % (QtHelper.dirExec(), idFile)
                with open( pluginDataFile, mode='w') as myfile:
                    myfile.write( json.dumps( data )  )
                inData = True
            except Exception as e:
                print("unable to write plugin data file: %s" % e)
                print("data: %s" % data)

        msg.update( { 'in-data': inData } )
         
        # add data parameters
        if inData: msg.update( { 'data-id': idFile } )
             
        # add more params
        msg.update(more)
        
        # send command
        datagram = json.dumps( msg ) 
        datagramEncoded = base64.b64encode( bytes(datagram, "utf8")  )

        self.write( datagramEncoded + b"\n\n" )


class RecordButton(QWidget):
    """
    Record button widget
    """
    CapturePressed = pyqtSignal()
    CancelPressed = pyqtSignal()
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(RecordButton, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
    
    def createWidgets(self):
        """
        Create qt widgets
        """
        mainLayout = QVBoxLayout()
        
        self.buttonCapture = QPushButton(QIcon(":/screenshot.png"), "Capture")
        self.buttonCancel = QPushButton("Cancel")
        mainLayout.addWidget( self.buttonCapture )
        mainLayout.addWidget( self.buttonCancel )
        
        flags = Qt.WindowFlags()
        flags |= Qt.Window
        flags |= Qt.WindowTitleHint
        flags |= Qt.WindowStaysOnTopHint
        flags |= Qt.MSWindowsFixedSizeDialogHint
        flags |= Qt.CustomizeWindowHint
        self.setWindowFlags(flags)
        self.setLayout(mainLayout)
        
        self.setWindowIcon( QIcon(":/main.png") )
        self.setWindowTitle("Capture Assistant")
        
    def createConnections(self):
        """
        Create qt connections
        """
        self.buttonCapture.clicked.connect(self.onCapture)
        self.buttonCancel.clicked.connect(self.onCancel)
        
    def onCapture(self):
        """
        On capture
        """
        self.CapturePressed.emit()

    def onCancel(self):
        """
        On cancel
        """
        self.CancelPressed.emit() 

class MainApplication(QMainWindow, Logger.ClassLogger):
    """
    Qt application
    """
    TAB_WORKSPACE   =   0
    TAB_SERVER      =   1
    TAB_TEST_RESULT =   2
    DataProgress = pyqtSignal(int, int)
    Notify = pyqtSignal(tuple)
    LoadLocalTestResult = pyqtSignal(tuple)
    LoadLocalTestResultTerminated = pyqtSignal(int)
    def __init__(self):
        """
        Constructor

        - WWorkspace ( tab 0 )
        - WServerExplorer (tab 1)
        - WTestResult ( tab N)
        - UserClientInterface, used to communicate with the server
         _____________________________________________________
        | FILE | EDIT | SOURCE | SERVER | ?                   |
        | --------------------------------------------------- |
        |                                                     |
        |           __________________________________________|
        \ Workspace / \ Server Explorer / \ ....  /
        """
        super(MainApplication, self).__init__()
        
        # initialize logger
        logPathFile = "%s/%s" % ( QtHelper.dirExec(), Settings.instance().readValue( key = 'Trace/file' ) )
        level = Settings.instance().readValue( key = 'Trace/level' )
        size = Settings.instance().readValue( key = 'Trace/max-size-file' )
        nbFiles = int( Settings.instance().readValue( key = 'Trace/nb-backup-max' ) )
        Logger.initialize( logPathFile=logPathFile, level=level, size=size, 
                            nbFiles=nbFiles, noSettings=True )
        
        # log python module version
        self.trace( "Running platform: %s" %  platform.system() )
        if sys.version_info < (3,):
            self.trace( "System encoding (in): %s" % sys.stdin.encoding )
            self.trace( "System encoding (out): %s" % sys.stdout.encoding )

        self.trace( "Python version: %s" % platform.python_version() )
        self.trace( "Qt version: %s" % QT_VERSION_STR )
        self.trace( "PyQt version: %s" % PYQT_VERSION_STR )

        self.trace( "Locale Country: %s" % QLocale().countryToString(QLocale().country()) )
        self.trace( "Locale Point: %s" % QLocale().decimalPoint() )
        
        # read update settings ?
        settingsBackup = "%s//Update//backup_settings.ini" % QtHelper.dirExec()
        if os.path.exists(settingsBackup):
            self.updateSettingsFromBackup(settingsBackup)
                
        self.widgetRecord = RecordButton()
        self.widgetRecord.hide()

        # continue to start
        showMessageSplashscreen( self.tr('Initializing API interface...') )
        UCI.initialize( parent = self, clientVersion=__VERSION__ )
        RCI.initialize( parent = self, clientVersion=__VERSION__  )
        UCI.instance().startCA()

        showMessageSplashscreen( self.tr('Initializing test results...') )
        TestResults.initialize( parent = self )

        showMessageSplashscreen( self.tr('Initializing recorder engine...') )
        WRecorder.initialize(parent=self, offlineMode=WORKSPACE_OFFLINE)    

        self.listActionsRecentFiles = []
        self.mainTab = None

        showMessageSplashscreen( self.tr('Initializing user interface...') )   

        self.createWidgets()
        self.createActions()
        self.createTrayIcon()
        self.createStatusBar()

        showMessageSplashscreen( self.tr('Initializing menus...') )
        self.createMenus()
        self.createConnections()
        self.moreMenu()
    
        name = Settings.instance().readValue( key = 'Common/name' )
        self.updateWindowTitle( title = None)

        self.os_ = sys.platform
        if QT_VERSION_STR.startswith("4."):
            style = Settings.instance().readValue( key = 'Common/style-%s' % self.os_ )
        else:
            style = Settings.instance().readValue( key = 'Common/style-qt5' )
        self.changeStyle( styleName = style )
        self.setCentralWidget(self.mainTab)

        self.currentMainTabChanged( tabId = WWorkspace.instance().type )
        WWorkspace.instance().documentViewerEmpty()

        # cleanup all test result, new in v11.2
        showMessageSplashscreen( self.tr('Empty storage...') )   
        self.removeTestResults()
        self.cleanupTmp()
        # end of new
        
        # initialize all extensions 
        self.pluginsStarted = {}
        self.pluginsConfigured = {}
        self.pluginsBuffers = {}
        self.pluginsIcons = {}
        self.loadingPlugins()

        # Move the window on the position 0,0
        pos = self.pos()
        pos.setX(0)
        pos.setY(0)
        self.move(pos)
        
    def getCurrentVersion(self):
        """
        Private function
        Returns current version

        @return:
        @rtype: dict
        """
        data = { 
                    'client-version': __VERSION__, 
                    'client-platform': sys.platform, 
                    'client-portable': QtHelper.str2bool(Settings.instance().readValue( key = 'Common/portable')) 
               }
        return data
        
    def updateSettingsFromBackup(self, settingsBackup): 
        """
        Update settings from backup
        """
        settingsUpdate = QSettings( settingsBackup,  QSettings.IniFormat    )
        
        lastAddrUpdate = settingsUpdate.value("Server/last-addr")
        if lastAddrUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/last-addr', value =lastAddrUpdate )
            else:
                Settings.instance().setValue( key = 'Server/last-addr', value =lastAddrUpdate.toString()  )
        lastUserUpdate = settingsUpdate.value("Server/last-username")
        if lastUserUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/last-username', value =lastUserUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/last-username', value =lastUserUpdate.toString()  )
        lastPwdUpdate = settingsUpdate.value("Server/last-pwd")
        if lastPwdUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/last-pwd', value =lastPwdUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/last-pwd', value =lastPwdUpdate.toString()  )
        runNewWinUpdate = settingsUpdate.value("TestRun/new-window")
        if runNewWinUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'TestRun/new-window', value =runNewWinUpdate )
            else:
                Settings.instance().setValue( key = 'TestRun/new-window', value =runNewWinUpdate.toString()  )
        patternTestUpdate = settingsUpdate.value("TestRun/event-filter-pattern")
        if patternTestUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'TestRun/event-filter-pattern', value =patternTestUpdate  )
            else:
                Settings.instance().setValue( key = 'TestRun/event-filter-pattern', value =patternTestUpdate.toString()  )
        portDataUpdate = settingsUpdate.value("Server/port-data")
        if portDataUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/port-data', value =portDataUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/port-data', value =portDataUpdate.toString()  )
        portApiUpdate = settingsUpdate.value("Server/port-api")
        if portApiUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/port-api', value =portApiUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/port-api', value =portApiUpdate.toString()  )

        # new in v13.1
        portProxyUpdate = settingsUpdate.value("Server/port-proxy-http")
        if portProxyUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/port-proxy-http', value =portProxyUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/port-proxy-http', value =portProxyUpdate.toString()  )
        addrProxyUpdate = settingsUpdate.value("Server/addr-proxy-http")
        if addrProxyUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/addr-proxy-http', value =addrProxyUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/addr-proxy-http', value =addrProxyUpdate.toString()  )
        activeProxyUpdate = settingsUpdate.value("Server/proxy-active")
        if activeProxyUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/proxy-active', value =activeProxyUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/proxy-active', value =activeProxyUpdate.toString()  )
        activeWebProxyUpdate = settingsUpdate.value("Server/proxy-web-active")
        if activeWebProxyUpdate:
            if sys.version_info > (3,): # python3 support
                Settings.instance().setValue( key = 'Server/proxy-web-active', value =activeWebProxyUpdate  )
            else:
                Settings.instance().setValue( key = 'Server/proxy-web-active', value =activeWebProxyUpdate.toString()  )
        # end of new
                
        # remove the file
        try:
            backupSettings = QFile(settingsBackup)
            backupSettings.remove()
        except Exception as e:
            pass
                
    def loadingPlugins(self):
        """
        Load plugins present in the plugins folder
        """
        files=os.listdir("%s//Plugins//" % (QtHelper.dirExec()))
        for x in files:
            
            curpath=os.path.join( "%s//Plugins//" % (QtHelper.dirExec()), x)
            if not os.path.isfile( curpath ):
                for y in os.listdir( curpath ):
                    fullpath=os.path.join( "%s//Plugins//%s//%s" % (QtHelper.dirExec(), x, y) )
                    if os.path.isfile(fullpath):
                    
                        # for dev only
                        if y.endswith(".exe"):
                            pluginId = x
                            
                            showMessageSplashscreen( self.tr('Loading plugin(s)...') )  

                            self.trace("plugin %s detected" % pluginId)
                            p = PluginProcess(self, cmd='"%s"' % fullpath)
                            p.DataReceived.connect(self.onPluginData)
                            p.startPlugin()
                            self.trace("plugin started")

    def onPluginData(self, data, plugin):
        """
        On data from plugins
        """
        # workaround, libpng can be present in console
        if b"warning:" in data: data = data.split(b"\n", 1)[1]
            
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
                self.onPluginMessage(msg=messageJson, plugin=plugin)
        self.pluginsBuffers[plugin] = pdus[-1]
        
    def onPluginMessage(self, msg, plugin):
        """
        On mesage from plugins
        """
        # plugins registration
        if msg['cmd'] == 'register' and msg['id'].lower() not in self.pluginsStarted :
            self.trace("register plugin: %s" % msg['id'].lower())
            self.pluginsStarted.update( {msg['id'].lower() : (msg['name'], msg['type'], plugin ) } )
            
            plugin.sendCommand( cmd='registered', more={'tmp-path': '%s/Tmp/' % QtHelper.dirExec(), 
                                'client-version': __VERSION__ } )
            plugin.startKeepAlive()
            
        elif msg['cmd'] == 'register' and msg['id'].lower() in self.pluginsStarted :
            plugin.sendCommand(cmd='registered', more={'tmp-path': '%s/Tmp/' % QtHelper.dirExec(), 
                                'client-version': __VERSION__  })
        
        elif msg['cmd'] == 'configure' and msg['id'].lower() in self.pluginsConfigured :
            pass
            
        elif msg['cmd'] == 'configure' and not msg['id'].lower() in self.pluginsConfigured :
            self.trace("configure plugin: %s" % msg['id'].lower())
            
            # new in v15
            pluginIcon = QIcon(":/plugin.png")
            if msg['in-data']:
                # read the file
                f = open( '%s/Tmp/%s' % (QtHelper.dirExec(), msg['data-id'] ), 'r')
                pluginData = f.read()
                f.close()

                iconPlugin = json.loads( pluginData )
                
                iconPixmap = QPixmap()
                iconPixmap.loadFromData(base64.b64decode(iconPlugin))
                pluginIcon = QIcon(iconPixmap)
                self.pluginsIcons[msg['id']] = pluginIcon
                
                # delete them
                os.remove( '%s/Tmp/%s' % (QtHelper.dirExec(), msg['data-id']  ) )
            # end of new
            
            mainAct  =  QtHelper.createAction(self, self.tr("%s" % msg['name']), self.openPluginMain,
                                                cb_arg={ 'pluginId': msg['id'], 'pluginData':""}, icon=pluginIcon )
                                            
            self.pluginsMenu.addAction( mainAct )
            
            # register all static plugins on all gui elements
            if msg['type'] in ['basic', 'recorder-web', 'recorder-app', 'recorder-android', 
                                'recorder-framework', 'test-results',
                                'remote-tests', 'recorder-system' ]:
                WWorkspace.WDocumentViewer.instance().welcomePage.addPlugin(name=msg['id'], 
                                                                            description=msg['description'], 
                                                                            icon=pluginIcon)
            
            if msg['type'] == 'recorder-web':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WRecorder.instance().gui(), 
                                        widgetDestData=WRecorder.instance().gui().selenium(),
                                        pluginIcon=pluginIcon )
                
            if msg['type'] == 'recorder-app':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WRecorder.instance().gui(), 
                                        widgetDestData=WRecorder.instance().gui().sikuli(),
                                        pluginIcon=pluginIcon )
            
            if msg['type'] == 'recorder-android':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WRecorder.instance().gui(), 
                                        widgetDestData=WRecorder.instance().gui().android(),
                                        pluginIcon=pluginIcon )
            
            if msg['type'] == 'recorder-framework':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WRecorder.instance().gui(), 
                                        widgetDestData=WRecorder.instance().gui().framework(),
                                        pluginIcon=pluginIcon)

            if msg["type"] == 'test-results':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WServerExplorer.Archives.instance(),
                                        pluginIcon=pluginIcon)

            if msg["type"] == 'remote-tests':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WWorkspace.WRepositories.instance().remote(),
                                        pluginIcon=pluginIcon)

            if msg["type"] == 'recorder-system':
                self.integratePlugin( pluginId=msg['id'], pluginName=msg['name'], 
                                        widgetDest=WRecorder.instance().gui(), 
                                        widgetDestData=WRecorder.instance().gui().system(),
                                        pluginIcon=pluginIcon)

            self.pluginsConfigured.update( {msg['id'].lower() : (msg['name'], msg['type'], plugin ) } )
            
        elif msg['cmd'] == 'import' and msg['id'].lower() in self.pluginsConfigured :

            pluginData = {}
            if msg['in-data']:
                # read the file
                f = open( '%s/Tmp/%s' % (QtHelper.dirExec(), msg['data-id'] ), 'r')
                pluginData = f.read()
                f.close()

                pluginJson = json.loads( pluginData )

                # delete them
                os.remove( '%s/Tmp/%s' % (QtHelper.dirExec(), msg['data-id']  ) )

            if msg['type'] == 'recorder-web' and len(pluginData):
                WRecorder.instance().startWeb()
                WRecorder.instance().gui().selenium().onPluginImport(dataJson=pluginJson)
                
            if msg['type'] == 'recorder-system' and len(pluginData):
                WRecorder.instance().startSys()
                WRecorder.instance().gui().system().onPluginImport(dataJson=pluginJson)
                
            if msg['type'] == 'recorder-app' and len(pluginData):
                WRecorder.instance().startGui()
                WRecorder.instance().gui().sikuli().onPluginImport(dataJson=pluginJson)
                
            if msg['type'] == 'remote-tests' and len(pluginData):
                WWorkspace.WRepositories.instance().remote().onPluginImport(dataJson=pluginJson)
                
        else:
            self.error("unknown message from plugin: %s" % msg)
    
    def integratePlugin(self, pluginId, pluginName, widgetDest, widgetDestData=None, pluginIcon=None):
        """
        Integrate plugin in the application
        """
        if widgetDestData is not None:
            pluginData = widgetDestData.pluginDataAccessor
        else:
            pluginData = widgetDest.pluginDataAccessor
        plugIcon = pluginIcon
        if plugIcon is None: plugIcon = QIcon(":/plugin.png")
        pluginAct  =  QtHelper.createAction(self, pluginName, self.openPluginMain, 
                            cb_arg= { 'pluginId': pluginId, 'pluginData': pluginData },
                            icon=plugIcon)
        widgetDest.addPlugin(pluginAct)

    def openPluginMain(self, pluginInfos):
        """
        open the main page of the plugin
        """
        pluginId = pluginInfos['pluginId']
        if pluginId.lower() in self.pluginsConfigured:
            pluginName, pluginType, pluginProcess = self.pluginsConfigured[pluginId.lower()]
            
            # call accessor to retrieve data
            if isinstance(pluginInfos['pluginData'], str):
                pluginData = {}
            else:
                pluginData = pluginInfos['pluginData']()
            
            if pluginProcess.state() == 0:
                pluginProcess.startPlugin()
                QMessageBox.warning(self, self.tr("Plugin Error"), 
                                    "Plugin %s no more running!\nRestart in progress..." % pluginId.lower() )
            else:
                pluginProcess.sendCommand(cmd='open-main', data=pluginData)

    def removeTestResults(self):
        """
        New in v11.2
        Remove all testresults in folder on each start of the client
        """
        try:
            files=os.listdir("%s//ResultLogs//" % (QtHelper.dirExec()))
            for x in files:
                fullpath=os.path.join( "%s//ResultLogs//" % (QtHelper.dirExec()), x)
                if os.path.isfile(fullpath):
                    os.remove( fullpath )
        except Exception as e:
            pass

    def cleanupTmp(self):
        """
        New in v12.2
        Remove all files in tmp
        """
        try:
            files=os.listdir("%s//Tmp//" % (QtHelper.dirExec()))
            for x in files:
                fullpath=os.path.join( "%s//Tmp//" % (QtHelper.dirExec()), x)
                if os.path.isfile(fullpath):
                    os.remove( fullpath )
        except Exception as e:
            pass

    def setVisible(self, visible):
        """
        Set as visible
        """
        self.restoreAction.setEnabled(not self.isMaximized() or not visible)
        super(MainApplication, self).setVisible(visible)
        
    def changeStyle(self, styleName):
        """
        Change the style of the window
        Styles availables:
         - Windows
         - WindowsXP
         - WindowsVista
         - Motif
         - CDE
         - Plastique
         - Cleanlooks
         - GTK

        @param styleName:
        @type styleName:
        """
        QApplication.setStyle( styleName )

    def keyPressEvent(self, e):
        """
        Called on key press
        """
        if e.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.fullScreenAction.setChecked(False)
                self.fullScreen(state=False)
        QMainWindow.keyPressEvent(self, e)

    def closeEvent(self, event):
        """
        Reimplementation from QMainWindow
        Quit the application
        - Destroy the connection with server
        - Destroy widgets
        - Checks if all documents are saved

        @param event:
        @type event:
        """
        allDocumentSaved = WWorkspace.WDocumentViewer.instance().saveAllTabs( question = True )
        if not allDocumentSaved:
            event.ignore()
            return
        if RCI.instance().authenticated:
            messageBox = QMessageBox(self)
            reply = messageBox.question(self, self.tr("Quit program"), 
                        self.tr("You are connected to the test center.\nAre you really sure to quit?"),
                        QMessageBox.Yes | QMessageBox.Cancel )
            if reply == QMessageBox.Yes:
                UCI.instance().closeConnection()
            else:
                event.ignore()
                return
        
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/rest-support' ) ):        
            RCI.instance().logout()
        UCI.instance().Disconnected.disconnect()
        
        # hide the tray icon
        self.trayIcon.hide()    

        # clear the clipboard
        QApplication.clipboard().clear()

        # also close separate dialog if exists
        self.separateTestResult.close()
        
        UCI.instance().stopCA()
        UCI.finalize()
        RCI.finalize()
        TestResults.finalize()
        WWorkspace.finalize()
        WServerExplorer.finalize()
        WRecorder.finalize()

        
        QApplication.processEvents()
        
        # cleanup plugins
        for pluginId, pluginInfos in self.pluginsStarted.items():
            pluginName, pluginType, pluginProcess = pluginInfos
            pluginProcess.kill()
        
        # finalize  settings
        Settings.finalize( )

        event.accept()

    def createStatusBar (self):
        """
        Display short message in the left bottom corner
        """
        self.sendToStatusbar( self.tr('Ready to start.') )

    def sendToStatusbar (self, message):
        """
        Add widget in the right bottom corner
        """
        self.statusBar().showMessage( message )
        if len(message):
            self.showMessageTray( msg=message )

    def createWidgets (self):
        """
        QtWidgets creation

        QTabWidget
         _____________________________________________________
        | QMenu                                               |
        | --------------------------------------------------- |
        |          ___________________________________________|
        \ QWidget / \ QWidget / \ ..... /

        """
        if QtHelper.IS_QT5:
            self.setAutoFillBackground(True)
            p = self.palette()
            p.setColor(self.backgroundRole(), Qt.white)
            self.setPalette(p)
        
        self.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);

            dialog-yes-icon: url(:/ok.png);
            dialog-no-icon: url(:/ko.png);

            dialog-open-icon: url(:/ok.png);

            dialog-apply-icon: url(:/ok.png);
            dialog-reset-icon: url(:/ko.png);
        }""")
        self.mainTab = QTabWidget()
        self.mainTab.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.mainTab.setDocumentMode(True)
        if Settings.instance().readValue( key = 'Common/maintab-orientation' ) == "South":
            self.mainTab.setTabPosition(QTabWidget.South)

        showMessageSplashscreen( self.tr('Initializing workspace...') )  
        WWorkspace.initialize( parent = self )
        showMessageSplashscreen( self.tr('Initializing explorer...') )   
        WServerExplorer.initialize( parent = self )

        self.mainTab.addTab( WWorkspace.instance(), QIcon(":/workspace.png") , WWorkspace.instance().name )

        self.buttonCloseAll = QToolButton()
        self.buttonCloseAll.setIcon(QIcon(":/close-all.png"))
        self.buttonCloseAll.setIconSize(QSize(15,15))
        self.buttonCloseAll.setToolTip(self.tr("Close all test results"))
        self.buttonCloseAll.setStyleSheet( """
                         QToolButton {
                             border: none;
                             margin: 5px;
                             padding-top: 1px;
                             padding-bottom: 1px;
                         }

                         QToolButton:hover
                        {
                            border: 1px solid #8f8f91;

                        }
                      """)

        self.buttonCloseAll.setEnabled(False)
        self.buttonCloseAll.clicked.connect(self.delAllTabsFromMenu)

        self.mainTab.setCornerWidget(self.buttonCloseAll)

        self.mainTab.addTab( WServerExplorer.instance(), QIcon(":/main.png") , 
                                WServerExplorer.instance().name )
        if not WORKSPACE_OFFLINE:
            self.mainTab.setTabEnabled( self.TAB_SERVER, False )

        self.setWindowIcon( QIcon(":/main.png") )
        
        self.separateTestResult = TestResults.TestResults.SeparateResults(self)

    def showRecordButton(self, mouseLocation=False, mousePosition=False):
        """
        Show the record button
        """
        self.widgetRecord.showNormal()
        self.widgetRecord.show()
        
    def createActions (self):
        """
        QtActions creation
        Actions defined:
         * quit
         * about this application
         * about qt
        """
        self.restoreAction = QAction("&Restore", self, triggered=self.showMaximized)
        self.captureRecorderAction = QAction("&Capture Desktop", self, triggered=self.onCaptureRecorder)
        self.captureRecorderAction.setEnabled(False)
        
        self.quitAction = QtHelper.createAction(self, self.tr("&Exit"), self.close, 
                                                shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/exit' ), 
                                                tip = self.tr('Quit program') )
        self.settingsAction = QtHelper.createAction(self, self.tr("&Preferences..."), self.setSettings, 
                                                icon=QIcon(":/server-config.png") )
        self.rnAction = QtHelper.createAction(self, self.tr("&Release Notes"), self.releaseNotes, 
                                                icon=QIcon(":/releasenotes.png") )
        self.aboutAction = QtHelper.createAction(self, self.tr("&About"), self.about,  icon=QIcon(":/about.png"), 
                                                shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/about' ) )
        self.aboutQtAction = QtHelper.createAction(self, self.tr("Qt"), qApp.aboutQt)
        self.openTestResultAction = QtHelper.createAction(self, self.tr("Open Test Result"), 
                                                self.openTestResult)
        self.openAllRecentFilesAction = QtHelper.createAction(self, self.tr("Open All Recent Files"), 
                                                self.openAllRecentFiles)
        self.emptyRecentFilesListAction = QtHelper.createAction(self, self.tr("Empty Recent Files List"), 
                                                self.emptyRecentFilesList)
        self.openAllRecentFilesAction.setEnabled(False)
        self.emptyRecentFilesListAction.setEnabled(False)

        self.fullScreenAction = QtHelper.createAction(self, self.tr("&Full screen"), self.fullScreen, checkable=True, 
                                                shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/fullscreen' ) )
        self.minimizeAction = QtHelper.createAction(self, self.tr("&Minimize"), self.minimizeWindow, 
                                                checkable=False)
        self.maximizeAction = QtHelper.createAction(self, self.tr("&Maximize"), self.maximizeWindow, 
                                                checkable=False)
        
        self.closeAllTests = QtHelper.createAction(self, self.tr("Close all"), self.delAllTabsFromMenu,
                                                icon = QIcon(":/close-all.png"))
        self.closeAllTests.setEnabled(False)

        # to hide toolbar
        self.hideStatusBarAction = QtHelper.createAction(self, self.tr("Status"), self.hideStatusBar, 
                                                checkable=True)
        self.hideDocumentBarAction = QtHelper.createAction(self, self.tr("Document"), self.hideDocumentBar, 
                                                checkable=True)
        self.hideExecuteBarAction = QtHelper.createAction(self, self.tr("Execute"), self.hideExecuteBar, 
                                                checkable=True)
        self.hideRepositoriesBarAction = QtHelper.createAction(self, self.tr("Repositories"), self.hideRepositoriesBar, 
                                                checkable=True)

        # to hide window
        self.hideHelperWindowAction = QtHelper.createAction(self, self.tr("Assistant Window"), self.hideHelperWindow, 
                                                checkable=True)
        self.hideHelperWindowAction.setChecked(True)
        self.hideRepositoriesWindowAction = QtHelper.createAction(self, self.tr("Repositories Window"), 
                                                self.hideRepositoriesWindow, checkable=True)
        self.hideRepositoriesWindowAction.setChecked(True)

        self.gotoHomepageAction = QtHelper.createAction(self, self.tr("My ExtensiveTesting..."), 
                                                self.gotoHomepage, icon=QIcon(":/main.png") )
        self.gotoHomepageAction.setEnabled(False)

        self.importImageAction = QtHelper.createAction(self, self.tr("Image file"), 
                                                self.importImageFile, checkable=False)
        self.importImageAction.setEnabled(False)

    def createMenus(self):
        """
        Contruction of the menu

        File || Edit  || Source || Server || ?

        File:
         * New TestSuite
         * New TestPlan
         * Open
         * ---
         * Save
         * Save As
         * Save All
         * ---
         * Exit

        Edit
         * Undo
         * Redo
         * ---
         * Cut
         * Copy
         * Paste
         * ---
         * Select All
         * Delete Selection

        Source
         * Comment
         * Uncomment
         * Indent
         * Unindent
         * ---
         * Code Folding

        Server
         * Connect
         * Disconnect

        ?
         * About
         * About Qt
        """
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        # sub new menu
        self.newMenu = self.fileMenu.addMenu(self.tr("&New..."))
        if not WORKSPACE_OFFLINE:
            self.newMenu.setEnabled(False)
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestAbstractAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestUnitAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestSuiteAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestPlanAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestGlobalAction )
        self.newMenu.addSeparator()
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestConfigAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTestDataAction )
        self.newMenu.addSeparator()
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newAdapterAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newLibraryAction )
        self.newMenu.addAction( WWorkspace.WDocumentViewer.instance().newTxtAction )

        self.fileMenu.addSeparator()
        # sub new menu
        self.openMenu = self.fileMenu.addMenu( QIcon(":/folder_add.png"), self.tr("&Open..."))
        self.openMenu.addAction( WWorkspace.WDocumentViewer.instance().openAction )
        self.openMenu.addAction( self.openTestResultAction )

        self.importMenu = self.fileMenu.addMenu( self.tr("&Import...") )
        self.importMenu.addAction( self.importImageAction )

        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().exportAsAction )

        self.fileMenu.addSeparator()
        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().closeTabAction )
        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().closeAllTabAction )
        self.fileMenu.addSeparator()
        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().saveAction)
        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().saveAsAction)
        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().saveAllAction)
        self.fileMenu.addAction( WWorkspace.WDocumentViewer.instance().printAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction( self.settingsAction )
        self.fileMenu.addSeparator()
        # sub menu recent
        self.recentMenu = self.fileMenu.addMenu(self.tr("&Recent Files..."))
        self.fileMenu.addAction( self.openAllRecentFilesAction )
        self.fileMenu.addAction( self.emptyRecentFilesListAction )
        self.fileMenu.addSeparator()
        # finalize file menu with quit
        self.fileMenu.addAction(self.quitAction)

        # view menu
        self.viewMenu = self.menuBar().addMenu( self.tr("&View") )
        # sub menu of view
        self.viewToolbarsMenu = self.viewMenu.addMenu(self.tr("&Toolbars..."))
        self.viewToolbarsMenu.addAction( self.hideStatusBarAction )
        self.initStatusBarDisplay()
        self.viewToolbarsMenu.addAction( self.hideDocumentBarAction )
        self.initDocumentBarDisplay()
        self.viewToolbarsMenu.addAction( self.hideExecuteBarAction )
        self.initExecuteBarDisplay()
        self.viewToolbarsMenu.addSeparator()
        self.viewToolbarsMenu.addAction( WWorkspace.WDocumentViewer.instance().hideFindReplaceAction )
        self.viewMenu.addSeparator()
        self.viewMenu.addAction( WWorkspace.instance().hideDeveloperModeAction )
        self.viewMenu.addSeparator()
        self.viewMenu.addAction( self.hideHelperWindowAction )
        self.viewMenu.addAction( self.hideRepositoriesWindowAction )
        self.viewMenu.addSeparator()
        self.viewMenu.addAction( self.fullScreenAction )
        self.viewMenu.addAction( self.minimizeAction )
        self.viewMenu.addAction( self.maximizeAction  )
        
        # edit menu
        self.editMenu = self.menuBar().addMenu(self.tr("&Test Editor"))
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().undoAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().redoAction )
        self.editMenu.addSeparator()
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().cutAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().copyAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().pasteAction )
        self.editMenu.addSeparator()
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().selectAllAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().deleteAction )

        # sub menu of source
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().commentAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().uncommentAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().indentAction)
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().unindentAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().codeWrappingAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().codefoldingAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().whitespaceVisibilityAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().indentGuidesVisibilityAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().linesNumberingAction )
        self.editMenu.addSeparator()
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().foldAllAction )
        self.editMenu.addAction( WWorkspace.WDocumentViewer.instance().findAction )
        
        # source menu
        self.sourceMenu = self.menuBar().addMenu(self.tr("&Test Execution"))
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction( WWorkspace.WDocumentViewer.instance().runAction )
        self.sourceMenu.addAction( WWorkspace.WDocumentViewer.instance().runStepByStepAction )
        self.sourceMenu.addAction( WWorkspace.WDocumentViewer.instance().runBreakpointAction )
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction( WWorkspace.WDocumentViewer.instance().runSchedAction )
        self.sourceMenu.addAction( WWorkspace.WDocumentViewer.instance().runSeveralAction )
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction( WWorkspace.WDocumentViewer.instance().checkAction )
        self.sourceMenu.addSeparator()
        
        self.sourceMenu.addSeparator()
        self.resultMenu = self.sourceMenu.addMenu( self.tr("&Results...") )
        self.resultMenu.addAction( self.closeAllTests )
        
        # archives menu
        self.archivesMenu = self.menuBar().addMenu(self.tr("&Test Logging"))
        # sub menu of archives menu
        self.refreshArchivesMenu = self.archivesMenu.addMenu( self.tr("&Refresh...") )
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().refreshAction )
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().fullRefreshAction )
        self.archivesMenu.addSeparator()
        self.archivesMenu.addAction( WServerExplorer.Archives.instance().expandAllAction )
        self.archivesMenu.addAction( WServerExplorer.Archives.instance().expandSubtreeAction )
        self.archivesMenu.addAction( WServerExplorer.Archives.instance().collapseAllAction )
        self.archivesMenu.addSeparator()
        self.refreshArchivesMenu = self.archivesMenu.addMenu(self.tr("&Results..."))
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().zipAction )
        self.refreshArchivesMenu.addSeparator()
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().openAction )
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().saveAction )
        self.refreshArchivesMenu.addSeparator()
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().exportTestVerdictAction )
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().exportTestReportAction )
        self.refreshArchivesMenu.addAction( WServerExplorer.Archives.instance().exportTestDesignAction )
        self.archivesMenu.addSeparator()
        self.archivesMenu.addAction( WServerExplorer.Archives.instance().emptyAction )
        self.archivesMenu.addSeparator()
        self.archivesMenu.addAction( WServerExplorer.Repositories.instance().backupArchivesAction )
        self.archivesMenu.addAction( WServerExplorer.Repositories.instance().deleteAllBackupsArchivesAction )

        # recorder menu
        self.recorderMenu = self.menuBar().addMenu(self.tr("&Test Conception"))
         
        # scheduler menu
        self.schedMenu = self.menuBar().addMenu(self.tr("&Scheduler"))
        self.schedMenu.addAction( WWorkspace.WDocumentViewer.instance().runSchedAction )
        self.schedMenu.addSeparator()
        self.taskMenu = self.schedMenu.addMenu( QIcon(":/process-icon.png"), self.tr("&Task...") )
        self.taskMenu.addAction( WServerExplorer.TestManager.instance().editWaitingAction )
        self.taskMenu.addSeparator()
        self.taskMenu.addAction( WServerExplorer.TestManager.instance().disableAction )
        self.taskMenu.addAction( WServerExplorer.TestManager.instance().cancelAction )
        self.taskMenu.addAction( WServerExplorer.TestManager.instance().killAction )
        self.tasksMenu = self.schedMenu.addMenu( QIcon(":/processes.png"), self.tr("&All Tasks...") )
        self.tasksMenu.addAction( WServerExplorer.TestManager.instance().cancelAllAction )
        self.tasksMenu.addAction( WServerExplorer.TestManager.instance().killAllAction )
        self.schedMenu.addSeparator()
        self.tasksRefreshMenu = self.schedMenu.addMenu( QIcon(":/act-refresh.png"), self.tr("&Refresh...") )
        self.tasksRefreshMenu.addAction( WServerExplorer.TestManager.instance().refreshWaitingAction )
        self.tasksRefreshMenu.addAction( WServerExplorer.TestManager.instance().refreshRunningAction )
        self.tasksRefreshMenu.addSeparator()
        self.tasksRefreshMenu.addAction( WServerExplorer.TestManager.instance().refreshHistoryAction )
        self.tasksRefreshMenu.addAction( WServerExplorer.TestManager.instance().partialRefreshHistoryAction )
        self.schedMenu.addSeparator()
        self.schedMenu.addAction( WServerExplorer.TestManager.instance().clearHistoryAction )

        # repositories menu
        self.repositoriesMenu = self.menuBar().addMenu(self.tr("&Repositories"))

        # sub menu of tests menu
        self.localTestsMenu = self.repositoriesMenu.addMenu( self.tr("&Local Tests...") )
        self.localTestsMenu.addAction( WWorkspace.WRepositories.instance().local().refreshAction )
        self.localTestsMenu.addSeparator()
        self.localTestsMenu.addAction( WWorkspace.WRepositories.instance().local().addDirAction )
        self.localTestsMenu.addAction( WWorkspace.WRepositories.instance().local().delFileAction )
        self.localTestsMenu.addAction( WWorkspace.WRepositories.instance().local().delDirAction )
        self.localTestsMenu.addAction( WWorkspace.WRepositories.instance().local().renameAction )

        # sub menu of tests menu
        self.remoteTestsMenu = self.repositoriesMenu.addMenu( self.tr("&Remote Tests...") )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().refreshRemoteAction )
        self.remoteTestsMenu.addSeparator()
        self.remoteTestsMenu.addAction( WServerExplorer.Repositories.instance().backupAction )
        self.remoteTestsMenu.addAction( WServerExplorer.Repositories.instance().deleteAllBackupsAction )
        self.remoteTestsMenu.addSeparator()
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().openFileAction )
        self.remoteTestsMenu.addSeparator()
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().addDirAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().delDirAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().delAllDirAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().renameAction )
        self.remoteTestsMenu.addSeparator()
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().duplicateDirAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().duplicateFileAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().duplicateFileAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().deleteFileAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().moveFileAction )
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().moveFolderAction )
        self.remoteTestsMenu.addSeparator()
        self.remoteTestsMenu.addAction( WWorkspace.WRepositories.instance().remote().openPropertiesAction )

        self.repositoriesMenu.addAction( WWorkspace.WRepositories.instance().remote().createSamplesAction )
        self.repositoriesMenu.addSeparator()


        # sub menu of repositories
        self.repositoriesMenu.addSeparator()
        self.adaptersMenu = self.repositoriesMenu.addMenu( QIcon(":/repository-adapters.png"), self.tr("&Adapters...") )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().refreshRemoteAction )
        self.adaptersMenu.addSeparator()
        self.adaptersMenu.addAction( WServerExplorer.Repositories.instance().backupAdaptersAction )
        self.adaptersMenu.addAction( WServerExplorer.Repositories.instance().deleteAllBackupsAdaptersAction )
        self.adaptersMenu.addSeparator()
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().addAdapterAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().checkAdaptersAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().setAsDefaultAction )
        self.adaptersMenu.addSeparator()
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().openFileAction )
        self.adaptersMenu.addSeparator()
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().addDirAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().delDirAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().delAllDirAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().renameAction )
        self.adaptersMenu.addSeparator()
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().duplicateDirAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().duplicateFileAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().duplicateFileAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().deleteFileAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().moveFileAction )
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().moveFolderAction )
        self.adaptersMenu.addSeparator()
        self.adaptersMenu.addAction( WWorkspace.WRepositories.instance().remoteAdapter().openPropertiesAction )

        self.repositoriesMenu.addAction( WWorkspace.WHelper.instance().generateAdaptersAction )
        self.repositoriesMenu.addSeparator()

        # sub menu of repositories
        self.librariesMenu = self.repositoriesMenu.addMenu( QIcon(":/repository-libraries.png"), self.tr("&Libraries...") )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().refreshRemoteAction )
        self.librariesMenu.addSeparator()
        self.librariesMenu.addAction( WServerExplorer.Repositories.instance().backupLibrariesAction )
        self.librariesMenu.addAction( WServerExplorer.Repositories.instance().deleteAllBackupsLibrariesAction )
        self.librariesMenu.addSeparator()
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().addLibraryAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().checkLibrariesAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().setAsDefaultAction )
        self.librariesMenu.addSeparator()
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().openFileAction )
        self.librariesMenu.addSeparator()
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().addDirAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().delDirAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().delAllDirAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().renameAction )
        self.librariesMenu.addSeparator()
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().duplicateDirAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().duplicateFileAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().duplicateFileAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().deleteFileAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().moveFileAction )
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().moveFolderAction )
        self.librariesMenu.addSeparator()
        self.librariesMenu.addAction( WWorkspace.WRepositories.instance().remoteLibrary().openPropertiesAction )

        self.repositoriesMenu.addAction( WWorkspace.WHelper.instance().generateLibrariesAction )

        # plugins
        self.toolsMenu = self.menuBar().addMenu(self.tr("&Shortcuts"))
        self.toolsMenu.addSeparator()
        self.toolsMenu.addAction( self.gotoHomepageAction )
        self.toolsMenu.addSeparator()

        # plugins menu
        self.pluginsMenu = self.menuBar().addMenu(self.tr("&Plugins"))
        self.pluginsMenu.setEnabled(False)
        
        # server menu
        self.serverMenu = self.menuBar().addMenu( self.tr("Get &Started") )
        self.serverMenu.addAction( WServerExplorer.instance().connectAction )
        self.serverMenu.addAction( WServerExplorer.instance().disconnectAction )
        self.serverMenu.addSeparator()
        self.serverMenu.addAction( WServerExplorer.instance().checkUpdateAction )

        # help menu
        self.helpMenu = self.menuBar().addMenu("&?")
        self.helpMenu.addAction( self.rnAction )
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.aboutAction)

        self.initRecentList()
        self.initToolsList()
        self.recentMenu.setEnabled(False)
        self.openAllRecentFilesAction.setEnabled(False)
        self.emptyRecentFilesListAction.setEnabled(False)

    def moreMenu(self):
        """
        Init the main menu more
        After the init of the main application
        """
        if sys.platform == "win32":
            self.recorderMenu.addAction( WRecorder.instance().restartGuiAction )
            self.recorderMenu.addSeparator()
            
            self.basicCaptureMenu = self.recorderMenu.addMenu( self.tr("&Basic...") )
            self.basicCaptureMenu.addAction( WRecorder.instance().startBasicAction )
            self.basicCaptureMenu.setEnabled(False)
            
            self.sysCaptureMenu = self.recorderMenu.addMenu( self.tr("&System...") )
            self.sysCaptureMenu.addAction( WRecorder.instance().startSysAction )
            self.sysCaptureMenu.setEnabled(False)
            
            self.desktopCaptureMenu = self.recorderMenu.addMenu( self.tr("&Applications...") )
            self.desktopCaptureMenu.addAction( WRecorder.instance().startGuiAction )
            self.desktopCaptureMenu.setEnabled(False)
            
            self.webCaptureMenu = self.recorderMenu.addMenu( self.tr("&Web...") )
            self.webCaptureMenu.addAction( WRecorder.instance().startWebAction )
            self.webCaptureMenu.setEnabled(False)
            
            self.mobCaptureMenu = self.recorderMenu.addMenu( self.tr("&Mobile...") )
            self.mobCaptureMenu.addAction( WRecorder.instance().startMobileAction )
            self.mobCaptureMenu.setEnabled(False)

            self.recorderMenu.addSeparator()
            
        self.networkCaptureMenu = self.recorderMenu.addMenu( self.tr("&Network...") )
        self.networkCaptureMenu.addAction( WRecorder.instance().startTcpAction )
        self.networkCaptureMenu.addAction( WRecorder.instance().startUdpAction )
        self.networkCaptureMenu.addSeparator()
        self.networkCaptureMenu.addAction( WRecorder.instance().startHttpAction )
        self.networkCaptureMenu.setEnabled(False)
            
        self.recorderMenu.addSeparator()
        self.docsMenu = self.recorderMenu.addMenu( self.tr("&Documentations") )
        self.docsMenu.addAction( WWorkspace.WHelper.instance().reloadAllAction )
        self.docsMenu.addSeparator()
        self.docsMenu.addAction( WWorkspace.WHelper.instance().rebuildCacheAction )
        # self.docsMenu.addAction( WWorkspace.WHelper.instance().prepareAssistantAction )

        self.adapsMenu = self.recorderMenu.addMenu( self.tr("&Adapters") )
        # self.adapsMenu.addAction( WWorkspace.WHelper.instance().generateAllAction )
        self.adapsMenu.addAction( WWorkspace.WHelper.instance().generateAdapterWsdlAction )

    def initToolsList(self):
        """
        Init tools list
        """
        i = 1
        toolInfo =  Settings.instance().readToolValue( key = 'Tool_%s/app-name' % i )
        if len(toolInfo):
            toolEnable =  Settings.instance().readToolValue( key = 'Tool_%s/app-enable' % i )
            toolType = Settings.instance().readToolValue( key = 'Tool_%s/app-ide' % i )
            if QtHelper.str2bool(toolType):
                toolAct  =  QtHelper.createAction(self, "Open %s..." % toolInfo, self.openTool, cb_arg=i )
            else:
                toolAct  =  QtHelper.createAction(self, "Go to %s..." % toolInfo, self.openTool, cb_arg=i )
            self.toolsMenu.addAction( toolAct )
            if QtHelper.str2bool(toolEnable):  
                self.toolsMenu.addAction( toolAct )
        while len(toolInfo):
            i += 1
            toolInfo = Settings.instance().readToolValue( key = 'Tool_%s/app-name' % i )
            toolType = Settings.instance().readToolValue( key = 'Tool_%s/app-ide' % i )
            toolEnable =  Settings.instance().readToolValue( key = 'Tool_%s/app-enable' % i )
            if len(toolInfo):
                if QtHelper.str2bool(toolType):
                    toolAct  =  QtHelper.createAction(self, "Open %s..." % toolInfo, self.openTool, cb_arg=i )
                else:
                    toolAct  =  QtHelper.createAction(self, "Go to %s..." % toolInfo, self.openTool, cb_arg=i )
                
                if QtHelper.str2bool(toolEnable):  
                    self.toolsMenu.addAction( toolAct )
    
    def openTool(self, toolId):
        """
        Open the tool
        """
        # read settings
        toolName = Settings.instance().readToolValue( key = 'Tool_%s/app-name' % toolId )
        toolLocal = Settings.instance().readToolValue( key = 'Tool_%s/app-local' % toolId )
        toolType = Settings.instance().readToolValue( key = 'Tool_%s/app-ide' % toolId )
        toolPath = Settings.instance().readToolValue( key = 'Tool_%s/app-path' % toolId )

        # open the app
        if QtHelper.str2bool(toolType):
            if QtHelper.str2bool(toolLocal):
                appPath = '%s\Externals\%s' % (QtHelper.dirExec(), toolPath)
            else:
                appPath = '%s' % toolPath
                
            if sys.platform == "win32":
               subprocess.Popen (['cmd.exe', '/c', appPath ], shell=True)
            
            if sys.platform == "linux2":
                subprocess.Popen ([appPath ], shell=True)
            
        else:
            url = QUrl(toolPath)
            QDesktopServices.openUrl(url)
        
    def importImageFile(self):
        """
        Import image file
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open Image"),
                '', "Images (*.png)")
                
        # new in v17.1
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if _fileName:
            # extract the name
            tmp = str(_fileName).rsplit("/", 1)
            path = tmp[0]
            if len(tmp) > 1:
                imageName = tmp[1].rsplit(".", 1)[0]
                imageExtension = tmp[1].rsplit(".", 1)[1]
            else:
                imageName = tmp[0].rsplit(".", 1)[0]
                imageExtension =  tmp[0].rsplit(".", 1)[1]

            # read the file
            file = QFile(_fileName)
            if not file.open(QIODevice.ReadOnly):
                QMessageBox.warning(self, self.tr("Error opening image file"), 
                                    self.tr("Could not open the file ") + _fileName)
            else:
                imageData= file.readAll()
                self.trace( "import image file with a length of %s" % len(imageData) )

                # the local repository is configured ?
                if Settings.instance().readValue( key = 'Repositories/local-repo' ) != "Undefined":
                    buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                    answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ),
                                                    self.tr("Import in the local repository?") , buttons)
                    if answer == QMessageBox.Yes:
                        self.importImageToLocal(imageName, imageData, imageExtension)
                    else:
                        self.importImageToRemote(imageName, imageData, imageExtension)
                else:
                    self.importImageToRemote(imageName, imageData, imageExtension)

    def onCaptureCancelActivated(self):
        """
        On capture canceled
        """
        self.widgetRecord.hide()
        WRecorder.instance().restoreAssistant()
        
    def onCaptureActivated(self):
        """
        On capture mode activated
        """
        self.widgetRecord.showMinimized()
        self.widgetRecord.hide()
        WRecorder.instance().captureDesktop()
        
    def onCaptureRecorder(self):
        """
        Show capture window
        """
        WRecorder.instance().captureDesktop()
        
    def onTrayIconActivated(self, reason):
        """
        On tray icon activated
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.setVisible(True)

    def onTrayMessageClicked(self):
        """
        Tray message is clicked
        """
        if sys.platform == "win32":
            if WRecorder.instance().recorderEngaged():
                WRecorder.instance().showGui()
            elif WRecorder.instance().snapshotEngaged():
                self.setVisible(True)
            else:
                self.setVisible(True)
        else:
            self.setVisible(True)
                
    def fullScreen(self, state):
        """
        Go to the full screen
        """
        if state:
            self.setWindowState(Qt.WindowFullScreen)
            self.statusBar().hide()
        else:
            self.setWindowState(Qt.WindowNoState) # to support properly linux
            self.statusBar().show()

    def importImageToLocal(self, imageName, imageData, imageExtension):
        """
        Import image to the local repository
        """
        WWorkspace.WDocumentViewer.instance().iRepo.localDialogSave().setImportFilename( imageName )
        WWorkspace.WDocumentViewer.instance().iRepo.localDialogSave().refresh()
        dialog = WWorkspace.WDocumentViewer.instance().iRepo.localDialogSave()
        if dialog.exec_() == QDialog.Accepted:
            completeFileName = dialog.getSelection()

            try:
                absPath = "%s.%s" % (completeFileName, imageExtension)
                f = open(absPath, 'wb')
                f.write( imageData )
                f.close()
            except Exception as e:
                self.error( "unable to save image in the local repo: %s" % str(e) )

            # refresh repo
            Repositories.instance().local().refreshAll()

    def importImageToRemote(self, imageName, imageData, imageExtension):
        """
        Import image in the remote repository
        """
        if RCI.instance().isAuthenticated():
            WWorkspace.WDocumentViewer.instance().iRepo.remote().saveAs.setImportFilename( imageName )
            dialog = WWorkspace.WDocumentViewer.instance().iRepo.remote().saveAs
            if dialog.exec_() == QDialog.Accepted:
                completeFileName = dialog.getSelection()
                newProject = dialog.getProjectSelection()
                projectid = WWorkspace.WDocumentViewer.instance().iRepo.remote().getProjectId(project=str(newProject))

                # extract the name
                tmp = str(completeFileName).rsplit("/", 1)
                newImagePath = tmp[0]
                if len(tmp) > 1:
                    newImageName = tmp[1].rsplit(".", 1)[0]
                else:
                    newImageName = tmp[0].rsplit(".", 1)[0]

                # call the ws
                content_encoded = base64.b64encode(imageData)
                if sys.version_info > (3,): # python3 support
                    content_encoded = content_encoded.decode("utf8")
                    
                RCI.instance().uploadTestFile(filePath=newImagePath, 
                                              fileName=newImageName, 
                                              fileExtension=imageExtension, 
                                              fileContent=content_encoded, 
                                              projectId=projectid, 
                                              updateMode=False, 
                                              closeTabAfter=False)                                
        else:
            QMessageBox.critical(self, self.tr("Import") , self.tr("Connect you to the test center!"))

    def gotoHomepage(self):
        """
        Goto the homepage
        """
        url = QUrl('%s://%s:%s/index.php' % (    UCI.instance().getScheme(),
                                            UCI.instance().getHttpAddress(),
                                            UCI.instance().getHttpPort()
                                        ) )
        QDesktopServices.openUrl(url)

    def hideRepositoriesWindow(self):
        """
        Hide the repositories part on the left
        """
        if not self.hideRepositoriesWindowAction.isChecked():
            WWorkspace.WRepositories.instance().hide()
        else:
            WWorkspace.WRepositories.instance().show()

    def hideHelperWindow(self):
        """
        Hide the assistant windows on the right
        """
        if not self.hideHelperWindowAction.isChecked():
            WWorkspace.instance().hideHelper()
            Settings.instance().setValue( key = 'View/helper', value = 'False' )
        else:
            WWorkspace.instance().showHelper()
            Settings.instance().setValue( key = 'View/helper', value = 'True' )

    def initStatusBarDisplay(self):
        """
        Init the status bar
        """
        if ( Settings.instance().readValue( key = 'View/status-bar' ) == 'True' ):
            self.hideStatusBarAction.setChecked(True)
            self.statusBar().show()
        else:
            self.hideStatusBarAction.setChecked(False)
            self.statusBar().hide()

    def createTrayIcon(self):
        """
        Create tray icon 
        """
        self.trayIconMenu = QMenu()
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.aboutAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon()
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon(":/main.png"))        
        
        self.trayIcon.show()    

    def showMessageTray(self, msg):
        """
        Show message in the system tray
        """
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.trayIcon.showMessage( Settings.instance().readValue( key = 'Common/name' ), 
                                        msg, QSystemTrayIcon.Information )

    def showMessageWarningTray(self, msg):
        """
        Show message in the system tray
        """
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.trayIcon.showMessage( Settings.instance().readValue( key = 'Common/name' ), 
                                        msg, QSystemTrayIcon.Warning )

    def showMessageCriticalTray(self, msg):
        """
        Show message in the system tray
        """
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.trayIcon.showMessage( Settings.instance().readValue( key = 'Common/name' ), 
                                        msg, QSystemTrayIcon.Critical )

    def minimizeWindow(self):
        """
        Minimize window
        """
        self.showMinimized()

    def restoreWindow(self):
        """
        Restore the window
        """
        self.setWindowState(Qt.WindowNoState)
        
    def maximizeWindow(self):
        """
        Maximize window
        """
        self.showMaximized()
        
    def initDocumentBarDisplay(self):
        """
        Init the document bar 
        """
        if ( Settings.instance().readValue( key = 'View/document-bar' ) == 'True' ):
            WWorkspace.WDocumentViewer.instance().showDocumentBar()
            self.hideDocumentBarAction.setChecked(True)
        else:
            self.hideDocumentBarAction.setChecked(False)
            WWorkspace.WDocumentViewer.instance().hideDocumentBar()

    def initExecuteBarDisplay(self):
        """
        Init execute bar
        """
        if ( Settings.instance().readValue( key = 'View/execute-bar' ) == 'True' ):
            WWorkspace.WDocumentViewer.instance().showExecuteBar()
            self.hideExecuteBarAction.setChecked(True)
        else:
            self.hideExecuteBarAction.setChecked(False)
            WWorkspace.WDocumentViewer.instance().hideExecuteBar()

    def hideStatusBar(self):
        """
        Hide the status bar
        """
        if not self.hideStatusBarAction.isChecked():
            self.statusBar().hide()
            Settings.instance().setValue( key = 'View/status-bar', value = 'False' )
        else:
            self.statusBar().show()
            Settings.instance().setValue( key = 'View/status-bar', value = 'True' )

    def hideDocumentBar(self):
        """
        Hide the document bar
        """
        if not self.hideDocumentBarAction.isChecked():
            WWorkspace.WDocumentViewer.instance().hideDocumentBar()
            Settings.instance().setValue( key = 'View/document-bar', value = 'False' )
        else:
            WWorkspace.WDocumentViewer.instance().showDocumentBar()
            Settings.instance().setValue( key = 'View/document-bar', value = 'True' )

    def hideExecuteBar(self):
        """
        Hide the execute bar
        """
        if not self.hideExecuteBarAction.isChecked():
            WWorkspace.WDocumentViewer.instance().hideExecuteBar()
            Settings.instance().setValue( key = 'View/execute-bar', value = 'False' )
        else:
            WWorkspace.WDocumentViewer.instance().showExecuteBar()
            Settings.instance().setValue( key = 'View/execute-bar', value = 'True' )

    def hidePrepareBar(self):
        """
        Hide the prepare bar
        """
        if not self.hidePrepareBarAction.isChecked():
            WWorkspace.WDocumentViewer.instance().hidePrepareBar()
            Settings.instance().setValue( key = 'View/prepare-bar', value = 'False' )
        else:
            WWorkspace.WDocumentViewer.instance().showPrepareBar()
            Settings.instance().setValue( key = 'View/prepare-bar', value = 'True' )

    def hideRepositoriesBar(self):
        """
        Hide the repositories bar
        """
        if not self.hideRepositoriesBarAction.isChecked():
            WWorkspace.WRepositories.instance().hideToolbars()
        else:
            WWorkspace.WRepositories.instance().showToolbars()

    def initRecentList(self):
        """
        Fill the recent list files from settings
        """
        # define positions
        self.listActionsRecentFiles = []
        for i in xrange( int( Settings.instance().readValue( key = 'Common/nb-recent-files-max' ) ) ):
            act  =  QtHelper.createAction(self, "%s:" % (i+1), self.openFileFromRecent, cb_arg=i )
            self.listActionsRecentFiles.append( act )
            self.recentMenu.addAction( act )
        # read recent files and update sub menu
        recentListFiles = self.readFromRecent()
        if recentListFiles:
            self.recentMenu.setEnabled(True)
            self.openAllRecentFilesAction.setEnabled(True)
            self.emptyRecentFilesListAction.setEnabled(True)
            for i in xrange(len(recentListFiles)):
                if recentListFiles[i]['type'] in [ UCI.REPO_TESTS_LOCAL, UCI.REPO_ADAPTERS, UCI.REPO_LIBRARIES ]:
                    projectName = ""
                else:
                    projectName = "(%s)" % recentListFiles[i]['project']
                type_file = "%s%s:%s" % ( UCI.REPO_TYPES_DICT[recentListFiles[i]['type']],  
                                            projectName, recentListFiles[i]['file'] )
                self.listActionsRecentFiles[i].setText( "%s: %s" % ( i+1, type_file) )

    def setSettings (self):
        """
        Save settings in the file
        """
        settingsDialog = Settings.SettingsDialog( self )
        if settingsDialog.exec_() == QDialog.Accepted:
            WWorkspace.WRepositories.instance().localRepoPath = Settings.instance().readValue( key = 'Repositories/local-repo' )
            WWorkspace.WRepositories.instance().localRepository.repositoryPath = Settings.instance().readValue( key = 'Repositories/local-repo' )
            if isinstance(WWorkspace.WRepositories.instance().localRepository, Repository):
                WWorkspace.WRepositories.instance().localRepoIsPresent()
                if Settings.instance().readValue( key = 'Repositories/local-repo' ) == "Undefined":
                    WWorkspace.WRepositories.instance().cleanLocalRepo()
                else:
                    WWorkspace.WRepositories.instance().initLocalRepo()
            
            # update checkbox state of the test editor according to the configuration
            WWorkspace.WDocumentViewer.instance().codeWrappingAction.setChecked( 
                    QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/code-wrapping' ) )
            )
            WWorkspace.WDocumentViewer.instance().codefoldingAction.setChecked( 
                    QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/code-folding' ) )
            )

            WWorkspace.WDocumentViewer.instance().indentGuidesVisibilityAction.setChecked( 
                    QtHelper.str2bool(Settings.instance().readValue( key = 'Editor/indent-guides-visible' )) 
            )

            WWorkspace.WDocumentViewer.instance().whitespaceVisibilityAction.setChecked( 
                    QtHelper.str2bool(Settings.instance().readValue( key = 'Editor/ws-visible' )) 
            )

            WWorkspace.WDocumentViewer.instance().linesNumberingAction.setChecked( 
                    QtHelper.str2bool(Settings.instance().readValue( key = 'Editor/lines-numbering' )) 
            )
            
            # update checkbox state of find/replace bar according to the configuration
            WWorkspace.WDocumentViewer.instance().findWidget.caseCheck.setChecked( 
                                       QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/find-case-sensitive' ))
            )
            WWorkspace.WDocumentViewer.instance().findWidget.caseWordCheck.setChecked( 
                                           QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/find-whole-word' ))
            )
            WWorkspace.WDocumentViewer.instance().findWidget.allCheck.setChecked( 
                                           QtHelper.str2bool(Settings.instance().readValue( key = 'Replace/replace-all' ))
            )
            WWorkspace.WDocumentViewer.instance().findWidget.caseRegexpCheck.setChecked( 
                                           QtHelper.str2bool(Settings.instance().readValue( key = 'Editor/find-regexp' ))
            )
            WWorkspace.WDocumentViewer.instance().findWidget.caseWrapCheck.setChecked( 
                                           QtHelper.str2bool( Settings.instance().readValue( key = 'Editor/find-wrap' ))
            )

    def addWidgetToStatusBar (self, widget, stretch=0):
        """
        Adds widget to status bar

        @param widget:
        @type widget: QWidget
        """
        self.statusBar().addPermanentWidget(widget,stretch )
        self.statusBar().setSizeGripEnabled(False)

    def createConnections(self):
        """
        QtSignals connection
         * QTabWidget <=> currentMainTabChanged
         * UCI <=> onConnection
         * UCI <=> onDisconnection
         * UCI <=> onNotify
        """
        self.widgetRecord.CapturePressed.connect(self.onCaptureActivated)
        self.widgetRecord.CancelPressed.connect(self.onCaptureCancelActivated)
        
        self.trayIcon.activated.connect(self.onTrayIconActivated)
        self.trayIcon.messageClicked .connect(self.onTrayMessageClicked )

        self.mainTab.tabBar().customContextMenuRequested.connect(self.onPopupMenu)
        self.mainTab.currentChanged.connect(self.currentMainTabChanged)

        WWorkspace.instance().UpdateWindowTitle.connect(self.updateWindowTitle)
        WWorkspace.instance().RecentFile.connect(self.recentFileUpdated)
        WWorkspace.instance().BusyCursor.connect(self.setCursorBusy)
        WWorkspace.instance().ArrowCursor.connect(self.setCursorWait)

        WWorkspace.WDocumentViewer.instance().LinkConnect.connect(self.onLinkConnectClicked)
        WWorkspace.WDocumentViewer.instance().LinkDisconnect.connect(self.onLinkDisconnectClicked)

        WWorkspace.WDocumentViewer.instance().LinkMacro.connect(self.onLinkMacroClicked)
        WWorkspace.WDocumentViewer.instance().LinkWebMacro.connect(self.onLinkWebMacroClicked)
        WWorkspace.WDocumentViewer.instance().LinkBasicMacro.connect(self.onLinkBasicMacroClicked)
        WWorkspace.WDocumentViewer.instance().LinkMobileMacro.connect(self.onLinkMobileMacroClicked)
        WWorkspace.WDocumentViewer.instance().OpenWeb.connect(self.onOpenWebsite)
        WWorkspace.WDocumentViewer.instance().OpenWebProduct.connect(self.onOpenProductWebsite)
        WWorkspace.WDocumentViewer.instance().GoMacroMode.connect(self.onMacroMode)

        WWorkspace.WDocumentViewer.instance().LinkSysMacro.connect(self.onLinkSysMacroClicked)
        WWorkspace.WDocumentViewer.instance().LinkPlugin.connect(self.onLinkPluginClicked)
        WWorkspace.WDocumentViewer.instance().NbReplaced.connect(self.onTextNbReplaced)

        RCI.instance().CriticalMsg.connect(self.displayCriticalMsg)
        RCI.instance().WarningMsg.connect(self.displayWarningMsg)
        RCI.instance().InformationMsg.connect(self.displayInformationMsg)
        RCI.instance().BusyCursor.connect(self.setCursorBusy)
        RCI.instance().IdleCursor.connect(self.setCursorWait)
        RCI.instance().WebCall.connect(WServerExplorer.instance().onRestCall)
        RCI.instance().CloseConnection.connect(UCI.instance().closeConnection)

        UCI.instance().CriticalMsg.connect(self.displayCriticalMsg)
        UCI.instance().WarningMsg.connect(self.displayWarningMsg)
        UCI.instance().InformationMsg.connect(self.displayInformationMsg)

        UCI.instance().Disconnected.connect(self.onDisconnection)
        UCI.instance().Notify.connect(self.onNotify)

        self.Notify.connect(self.onNotify)
        self.LoadLocalTestResult.connect(self.onLoadLocalTestResult)
        self.LoadLocalTestResultTerminated.connect(self.onLoadLocalTestResultTerminated)

        UCI.instance().Interact.connect(self.onInteractCalled )
        UCI.instance().Pause.connect(self.onPauseCalled )
        UCI.instance().BreakPoint.connect(self.onBreakPointCalled )
        UCI.instance().BusyCursor.connect(self.setCursorBusy)
        UCI.instance().ArrowCursor.connect(self.setCursorWait)

        WServerExplorer.instance().BusyCursor.connect(self.setCursorBusy)
        WServerExplorer.instance().BusyCursorChannel.connect(self.setCursorChannelBusy)
        WServerExplorer.instance().ArrowCursor.connect(self.setCursorWait)
        WServerExplorer.instance().Disconnect.connect(self.closeConnection)
        WServerExplorer.instance().ConnectCancelled.connect(self.onConnectionCancelled)

        # new in v18
        RCI.instance().Connected.connect(self.onConnection)
        
        RCI.instance().AddTestTab.connect(self.addTab)
        RCI.instance().OpenTestResult.connect(self.openLog)
        RCI.instance().GetTrReports.connect(WServerExplorer.Archives.instance().onGetTestPreview)
        RCI.instance().GetTrImage.connect(WServerExplorer.Archives.instance().images().onGetImagePreview)
        RCI.instance().RefreshResults.connect(WServerExplorer.instance().onRefreshResults)
        RCI.instance().CommentTrAdded.connect( WServerExplorer.Archives.instance().comments().onCommentAdded)
        RCI.instance().CommentsTrDeleted.connect(WServerExplorer.Archives.instance().comments().onDeleteComments)
        RCI.instance().GetTrReviews.connect(self.onTestReportLoaded)
        RCI.instance().GetTrDesigns.connect(self.onTestDesignLoaded)
        RCI.instance().GetTrVerdicts.connect(self.onTestVerdictLoaded)
        RCI.instance().ResetStatistics.connect(self.onStatisticsResetted)
        
        RCI.instance().RefreshContext.connect( WServerExplorer.instance().onRefreshContextServer)
        RCI.instance().RefreshUsages.connect( WServerExplorer.instance().onRefreshStatsServer)
        
        RCI.instance().TasksWaiting.connect(WServerExplorer.instance().onRefreshTasksWaiting)
        RCI.instance().TasksRunning.connect(WServerExplorer.instance().onRefreshTasksRunning)
        RCI.instance().TasksHistory.connect(WServerExplorer.instance().onRefreshTasksHistory)
        RCI.instance().TasksHistoryCleared.connect(WServerExplorer.instance().onClearTasksHistory)
        
        RCI.instance().TestKilled.connect(self.onTestKilled)
        RCI.instance().TestsKilled.connect(self.onTestsKilled)
        
        RCI.instance().RefreshRunningProbes.connect( WServerExplorer.instance().onRefreshRunningProbes )
        RCI.instance().RefreshRunningAgents.connect( WServerExplorer.instance().onRefreshRunningAgents )
        RCI.instance().RefreshHelper.connect(WWorkspace.WHelper.instance().onRefresh)
        RCI.instance().RefreshStatsTests.connect( WServerExplorer.instance().onRefreshStatsRepo )
        RCI.instance().RefreshStatsAdapters.connect(WServerExplorer.instance().onRefreshStatsRepoAdapters )
        RCI.instance().RefreshStatsLibraries.connect( WServerExplorer.instance().onRefreshStatsRepoLibraries )
        RCI.instance().RefreshStatsResults.connect( WServerExplorer.instance().onRefreshStatsRepoArchives)
        RCI.instance().RefreshDefaultProbes.connect( WServerExplorer.instance().onRefreshDefaultProbes )
        RCI.instance().RefreshDefaultAgents.connect( WServerExplorer.instance().onRefreshDefaultAgents )
        
        RCI.instance().OpenTestFile.connect(WWorkspace.WDocumentViewer.instance().openRemoteTestFile)
        RCI.instance().OpenAdapterFile.connect(WWorkspace.WDocumentViewer.instance().openRemoteAdapterFile)
        RCI.instance().OpenLibraryFile.connect(WWorkspace.WDocumentViewer.instance().openRemoteLibraryFile)
        
        RCI.instance().FileTestsUploaded.connect(WWorkspace.WDocumentViewer.instance().onRemoteTestFileSaved)
        RCI.instance().FileAdaptersUploaded.connect(WWorkspace.WDocumentViewer.instance().onRemoteAdapterFileSaved)
        RCI.instance().FileLibrariesUploaded.connect(WWorkspace.WDocumentViewer.instance().onRemoteLibraryFileSaved)
        RCI.instance().FileTestsUploadError.connect(WWorkspace.WDocumentViewer.instance().onRemoteTestFileSavedError)
        RCI.instance().FileAdaptersUploadError.connect(WWorkspace.WDocumentViewer.instance().onRemoteAdapterFileSavedError)
        RCI.instance().FileLibrariesUploadError.connect(WWorkspace.WDocumentViewer.instance().onRemoteLibraryFileSavedError)
         
        RCI.instance().FolderTestsRenamed.connect(WWorkspace.WDocumentViewer.instance().remoteTestsDirRenamed)
        RCI.instance().FolderAdaptersRenamed.connect(WWorkspace.WDocumentViewer.instance().remoteAdaptersDirRenamed)
        RCI.instance().FolderLibrariesRenamed.connect(WWorkspace.WDocumentViewer.instance().remoteLibrariesDirRenamed)
        
        RCI.instance().FileTestsRenamed.connect( WWorkspace.WDocumentViewer.instance().remoteTestsFileRenamed)
        RCI.instance().FileAdaptersRenamed.connect( WWorkspace.WDocumentViewer.instance().remoteAdaptersFileRenamed)
        RCI.instance().FileLibrariesRenamed.connect( WWorkspace.WDocumentViewer.instance().remoteLibrariesFileRenamed)
        
        RCI.instance().GetFileRepo.connect(self.onGetFileRepo)
        
        RCI.instance().RefreshTestsRepo.connect( self.onRefreshTestsRepo )
        RCI.instance().RefreshAdaptersRepo.connect( self.onRefreshAdaptersRepo ) 
        RCI.instance().RefreshLibrariesRepo.connect( self.onRefreshLibrariesRepo ) 
        
    def onTextNbReplaced(self, counter):
        """
        On number of occurrenced replaced from editor
        """
        if counter:
            self.sendToStatusbar( self.tr('Replace All: %s occurence(s) were replaced.' % counter) )
        else:
            self.sendToStatusbar( self.tr('Replace All: 0 occurence(s) was replaced.') )
        
    def onRunTest(self, channelId):
        """
        Run a test
        """
        WWorkspace.WDocumentViewer.instance().runTest(channelId=channelId)
        
    def onConnectionCancelled(self):
        """
        On connection cancelled
        """
        WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
       
    def onMacroMode(self, isTu=True, isTs=False):
        """
        On show assistant automation
        """
        WRecorder.instance().restartGui(isTu=isTu, isTs=isTs)
        
    def onOpenWebsite(self):
        """
        On open website
        """
        self.showMessageTray(msg="Opening test center website...")

        destUrl = '%s://%s:%s/index.php' % (    
                                            UCI.instance().getScheme(),
                                            UCI.instance().getHttpAddress(),
                                            UCI.instance().getHttpPort()
                                        )

        if sys.platform == "win32":
            subprocess.call('start iexplore %s' % destUrl, shell=True)
        else:
            url = QUrl( destUrl )
            QDesktopServices.openUrl(url)
        
    def onOpenProductWebsite(self):
        """
        On open website
        """
        self.showMessageTray(msg="Opening product website...")

        if sys.platform == "win32":
            destUrl = Settings.instance().readValue( key = 'Common/url' )
            subprocess.call('start iexplore %s' % destUrl, shell=True)
        else:
            destUrl = QUrl( Settings.instance().readValue( key = 'Common/url' ) )
            url = QUrl( destUrl )
            QDesktopServices.openUrl(url)
        
    def onLinkPluginClicked(self, plugId):
        """
        On plugin clicked
        """
        self.openPluginMain( {"pluginId": plugId, "pluginData": ""} )
        
    def onLinkMacroClicked(self):
        """
        On link macro clicked
        """
        WRecorder.instance().startGui()
        
    def onLinkWebMacroClicked(self):
        """
        On link macro clicked
        """
        WRecorder.instance().startWeb()
        
    def onLinkBasicMacroClicked(self):
        """
        On link macro clicked
        """
        WRecorder.instance().startBasic()
        
    def onLinkSysMacroClicked(self):
        """
        On link macro clicked
        """
        WRecorder.instance().startSys()
        
    def onLinkMobileMacroClicked(self):
        """
        On link macro clicked
        """
        WRecorder.instance().startMobile()
        
    def onWsdlMacroClicked(self):
        """
        On wsdl macro clicked
        """
        WWorkspace.WHelper.instance().generateAdapterWSDL()

    def onLinkConnectClicked(self):
        """
        On connect link clicked
        """
        WServerExplorer.instance().startConnection()
    
    def onLinkDisconnectClicked(self):
        """
        On disconnect link clicked
        """
        WServerExplorer.instance().stopConnection()
        
    def closeConnection(self):
        """
        Close connection
        """
        nbDocsUnsaved = WWorkspace.WDocumentViewer.instance().docAreModified()
        if nbDocsUnsaved:
            messageBox = QMessageBox(self)
            reply = messageBox.question(
                                        self, self.tr("Disconnect"), 
                                        self.tr( "Remote tests are not saved.\nAre you really sure to disconnect?"),
                                        QMessageBox.Yes | QMessageBox.No 
                                        )
            if reply == QMessageBox.Yes:
                if UCI.instance() is not None: UCI.instance().closeConnection()
            else:
                 WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=True)
        else:
            if UCI.instance() is not None: UCI.instance().closeConnection()
        
    def setCursorBusy(self):
        """
        Set the cursor as busy
        """
        self.setCursor(QCursor(Qt.BusyCursor))

    def setCursorChannelBusy(self):
        """
        Set the cursor busy
        """
        self.setCursor(QCursor(Qt.BusyCursor))
        WServerExplorer.instance().start2Connection()

    def setCursorWait(self):
        """
        Set the cursor as wait
        """
        self.setCursor(QCursor(Qt.ArrowCursor))

    def displayCriticalMsg(self, title, err):
        """
        Display a critical message
        """
        QMessageBox.critical(self, title , err)

    def displayWarningMsg(self, title, err):
        """
        Display a warning message
        """
        QMessageBox.warning(self, title , err)

    def displayInformationMsg(self, title, err ):
        """
        Display a information message
        """
        QMessageBox.information(self, title , err)

    def openTestResult (self):
        """
        Open a local test result
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "", 
                                                "Test Result (*.trx)")
                
        # new in v17.1
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if not len(_fileName):
            return

        extension = str(_fileName).rsplit(".", 1)[1]
        if not ( extension.lower() == "trx" ):
            QMessageBox.critical(self, self.tr("Open") , self.tr("File not supported") )
            return

        _fileName = str(_fileName)
        testName = _fileName.rsplit("/", 1)[1]
        
        self.openLog( (_fileName,testName), removeFile= False, fromServer=False)

    def openLog (self, result, removeFile = True, fromServer=True):
        """
        Open log file

        @param result:
        @type result:

        @param removeFile:
        @type removeFile: boolean
        """
        testId = TestResults.instance().getTestId()
        fileName, testName = result
        wTest = TestResults.instance().newTest( name = "%s" % testName, tid = testId, local = True )
        self.addTab( wTest )

        try:
            UCI.instance().loaderDialog.setLoading()
            UCI.instance().loaderDialog.show()

            dataModel = TestResultModel.DataModel()
            loaded = dataModel.load( absPath=fileName )
            if not loaded:
                raise Exception( 'unable to load data model' )

            # read only the header of the test result
            # other parts will be loaded only if the user click on it
            if len(dataModel.testheader): # new in v11.2, better performance
                startFlag = time.time()

                # move file to unique filename
                idFile = "%s" % uuid.uuid4()
                newPath = "%s/ResultLogs/%s.trx" % (QtHelper.dirExec(),idFile)
                
                if not fromServer:
                    shutil.copyfile(fileName, newPath )
                else:
                    shutil.move(fileName, newPath )
                
                wTest.setLocalData(newPath)

                try:
                    self.trace("convert to io v2")
                    f = cStringIO.StringIO( dataModel.testheader )
                except Exception as e:
                    self.error( "unable to io logs v2: %s" % str(e) )
                    raise Exception(e)
                else:
                    all = f.readlines()
                    maxSize = len(all)

                    i = 1
                    # change the cursort to busy
                    self.setCursorBusy()
                    for line in all:
                        self.DataProgress.emit(i,maxSize)
                        try:
                            # decode in base 64 and unpickle the data
                            if sys.version_info > (3,): # python3 support
                                l = base64.b64decode(line)
                                event = cPickle.loads( l, encoding="bytes")
                                event = QtHelper.bytes_to_unicode(event)
                            else:
                                l = base64.b64decode(line)
                                event = cPickle.loads( l )
                        except Exception as e:
                            self.error( line )
                            self.error( "unable to load line: %s" % e )
                        else:
                            event['test-id'] = testId
                        # self.Notify.emit(('event', event ))
                        self.LoadLocalTestResult.emit( ('event', event ) )
                        i += 1

                    f.close()
                    
                    self.LoadLocalTestResultTerminated.emit( int(testId) )

                # the work is terminated
                UCI.instance().loaderDialog.done(0)
                self.setCursorWait()
                
                stopFlag = time.time()
                self.trace("time to load test result v2 (in seconds): %0.2f" % (stopFlag-startFlag))
                
                wTest.headerReady = True
            # end of new
            else: # backward compatibility, not efficient with big test result
                startFlag = time.time()
                try:
                    self.trace("convert to io")
                    f = cStringIO.StringIO( dataModel.testresult )
                except Exception as e:
                    self.error( "unable to io logs: %s" % str(e) )
                    raise Exception(e)
                else:
                    all = f.readlines()
                    maxSize = len(all)
                    i = 1
                    # change the cursort to busy
                    self.setCursorBusy()
                    for line in all:
                        self.DataProgress.emit(i,maxSize)
                        try:
                            try:
                                # decode in base 64 and unpickle the data
                                if sys.version_info > (3,): # python3 support
                                    l = base64.b64decode(line)
                                    event = cPickle.loads( l, encoding="bytes")
                                    event = QtHelper.bytes_to_unicode(event)
                                else:
                                    l = base64.b64decode(line)
                                    event = cPickle.loads( l )
                            except Exception as e:
                                self.error( "unable to depickle line, trying old style: %s" % e )
                                event =  eval( line ) # old style
                        except Exception as e:
                            self.error( line )
                            self.error( "unable to eval line: %s" % e )
                        else:
                            event['test-id'] = testId
                        self.Notify.emit(('event', event ))
                        i += 1

                    f.close()
                    UCI.instance().loaderDialog.done(0)
                    if removeFile:
                        os.remove(fileName)
                    # no more busy, change the cursor
                    self.setCursorWait()
                    
                stopFlag = time.time()
                self.trace("time to load test result (in seconds): %0.2f" % (stopFlag-startFlag))
        except Exception as e:
            self.error( "Unable to read log: " + str(e) )
            UCI.instance().loaderDialog.done(0)
            QMessageBox.critical(self, self.tr("Open test result") , 
                                    self.tr("Unable to read test result, file corrupted!") )
        
    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos:
        @type pos:
        """
        #
        idx = self.mainTab.tabBar().tabAt(pos)
        if idx >= 0:
            wid = self.mainTab.widget(idx)
            if wid.type == self.TAB_TEST_RESULT:
                self.selectedWid = wid
                self.mainTab.setCurrentWidget(wid)
                self.menu = QMenu()
                self.menu.addAction( wid.logsItem.replayAction )
                self.menu.addAction( wid.logsItem.killAction )
                self.menu.addAction( wid.logsItem.addCommentAction )
                self.menu.addAction( wid.logsItem.exportVerdictAction )
                self.menu.addAction( wid.logsItem.exportReportAction )
                self.menu.addSeparator()
                self.menu.addAction( wid.logsItem.closeResultAction)
                self.menu.popup( self.mainTab.tabBar().mapToGlobal(pos))
            elif wid.type == self.TAB_WORKSPACE:
                if TestResults.instance().getNumberOfTests() > 0:
                    self.closeAllTests.setEnabled(True)
                else:
                    self.closeAllTests.setEnabled(False)
                self.selectedWid = wid
                self.mainTab.setCurrentWidget(wid)
                self.menu = QMenu()
                self.menu.addAction( self.closeAllTests )
                self.menu.addSeparator()
                self.menu.popup( self.mainTab.tabBar().mapToGlobal(pos))

    def delAllTabsFromMenu(self):
        """
        Delete all tabulations from menu
        """
        reply = QMessageBox.question(self, self.tr("Close all tests"), 
                                    self.tr("Are you sure?"),
                                    QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            for wd in TestResults.instance().getWidgetTests():
                wd.closeTest()
            TestResults.instance().resetTests()
            self.closeAllTests.setEnabled(False)

    def recentFileUpdated(self, fileDescription):
        """
        Called when recent files is updated

        @param fileDescription:
        @type fileDescription:
        """
        recentListFiles = []
        # read settings
        recentListFiles = self.readFromRecent()
        if recentListFiles:
            # search if already exist in the list
            for rf in recentListFiles:
                if rf['file'] == fileDescription['file'] and \
                    rf['type'] == fileDescription['type'] and rf['project'] == fileDescription['project']:
                    self.trace('already exist in the list, nothing todo')
                    return

        self.recentMenu.setEnabled(True)
        self.emptyRecentFilesListAction.setEnabled(True)
        self.openAllRecentFilesAction.setEnabled(True)

        if len(recentListFiles) == int( Settings.instance().readValue( key = 'Common/nb-recent-files-max' ) ):
            recentListFiles.pop()
        recentListFiles.insert(0, fileDescription)
        if fileDescription['type'] in [ UCI.REPO_TESTS_LOCAL, UCI.REPO_ADAPTERS, UCI.REPO_LIBRARIES ]:
            projectName = ""
        else:
            projectName = "(%s)" %  fileDescription['project']
        type_file = "%s%s:%s" % (  fileDescription['type'], projectName, fileDescription['file'] )
        for i in xrange(len(recentListFiles)):
            if recentListFiles[i]['type'] in [ UCI.REPO_TESTS_LOCAL, UCI.REPO_ADAPTERS, UCI.REPO_LIBRARIES ]:
                projectName = ""
            else:
                projectName = "(%s)" % recentListFiles[i]['project']
            type_file = "%s%s:/%s" % ( UCI.REPO_TYPES_DICT[ recentListFiles[i]['type'] ], 
                                        projectName, recentListFiles[i]['file'] )
            self.listActionsRecentFiles[i].setText( "%s: %s" % ( i+1, type_file) )
        # update settings
        try:
            pickled =  cPickle.dumps( recentListFiles )
            compressed = zlib.compress(pickled)
            self.saveToRecent( data=compressed )
        except Exception as e:
            self.error('failed to encode recent files list: %s' % e)

    def saveToRecent(self, data):
        """
        Save list file to recent
        """
        if sys.version_info > (3,):
            if isinstance(data, str): # convert to bytes
                data = data.encode()
                
        try:
            recentFile = '%s/Files/recent.dat' % QtHelper.dirExec()
            with open( recentFile, mode='wb') as myfile:
                myfile.write(data)
        except Exception as e:
            self.error("unable to write recent file list: %s" % e)

    def readFromRecent(self):
        """
        Read list of file from recent
        """
        recentListFiles = []
        try:
            recentFile = '%s/Files/recent.dat' % QtHelper.dirExec()
            if os.path.exists(recentFile):
                compressed = ''
                with open( recentFile, mode='rb') as myfile:
                    compressed = myfile.read()
                if len(compressed):
                    decompressed = zlib.decompress(compressed)
                    recentListFiles =  cPickle.loads( decompressed )
        except Exception as e:
            self.error( "unable to read recent file: %s" % e )
        return recentListFiles

    def emptyRecentFilesList(self):
        """
        Remove all files from the recent list
        """
        # clean recent menu
        for i in xrange( int( Settings.instance().readValue( key = 'Common/nb-recent-files-max' ) ) ):
            self.listActionsRecentFiles[i].setText( "%s:" % str(i+1) )

        # clean settings
        self.saveToRecent(data=b'')

        # disable recent menu
        self.recentMenu.setEnabled(False)
        self.openAllRecentFilesAction.setEnabled(False)
        self.emptyRecentFilesListAction.setEnabled(False)

    def openAllRecentFiles(self):
        """
        Open all recent files
        """
        recentListFiles = self.readFromRecent()
        if recentListFiles:
            self.recentMenu.setEnabled(True)
            self.openAllRecentFilesAction.setEnabled(True)
            self.emptyRecentFilesListAction.setEnabled(True)

        for i in xrange(len(recentListFiles)):
            self.openFileFromRecent(fileIndex=i)

    def openFileFromRecent(self, fileIndex):
        """
        Open the recent file

        @param fileIndex:
        @type fileIndex:
        """
        recentListFiles = self.readFromRecent()
        if recentListFiles:
            # reopen the file
            try:
                tplFile= recentListFiles[fileIndex]
            except IndexError as e:
                self.error( "open recent file: %s" % e )
            else:
                if tplFile['type']==UCI.REPO_TESTS:
                    if RCI.instance().isAuthenticated():
                        cur_prj_id = Repositories.instance().remote().getProjectId(tplFile['project'])
                        RCI.instance().openFileTests( projectId=int(cur_prj_id), filePath=tplFile['file'])
                    else:
                        QMessageBox.warning(self, self.tr("Open file") , 
                                            self.tr("Connect you to the test center!") )
                        
                elif tplFile['type']==UCI.REPO_ADAPTERS:
                    if RCI.instance().isAuthenticated():
                        cur_prj_id = Repositories.instance().remote().getProjectId(tplFile['project'])
                        RCI.instance().openFileAdapters(filePath=tplFile['file'])
                    else:
                        QMessageBox.warning(self, self.tr("Open file") , 
                                            self.tr("Connect you to the test center!") )
                        
                elif tplFile['type']==UCI.REPO_LIBRARIES:
                    if RCI.instance().isAuthenticated():
                        cur_prj_id = Repositories.instance().remote().getProjectId(tplFile['project'])
                        RCI.instance().openFileLibraries(filePath=tplFile['file'])
                    else:
                        QMessageBox.warning(self, self.tr("Open file") , 
                                            self.tr("Connect you to the test center!") )
                           
                elif tplFile['type']==UCI.REPO_TESTS_LOCAL or tplFile['type']==UCI.REPO_UNDEFINED :
                    # if UCI.RIGHTS_DEVELOPER in RCI.instance().userRights:
                        # QMessageBox.warning(self, self.tr("Authorization") , 
                                            # self.tr("You are not authorized to do that!") )
                    # else:
                    extension = str(tplFile['file']).rsplit(".", 1)[1]
                    tmp = str(tplFile['file']).rsplit("/", 1)
                    path = tmp[0]
                    filename = tmp[1].rsplit(".", 1)[0]
                    WWorkspace.WDocumentViewer.instance().newTab( path = path, filename = filename, 
                                                                  extension = extension, 
                                                                  repoDest=tplFile['type'])
                else:
                    self.error('type unkwnown')

    def delTabFromMenu (self):
        """
        Deletes tab from the popup menu
        """
        self.delTab( wTestResult = self.selectedWid )

    def addTab (self, wTestResult):
        """
        Adds tab

        @param wTestResult:
        @type wTestResult: QWidget
        """
        self.closeAllTests.setEnabled(True)
        self.buttonCloseAll.setEnabled(True)
            
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/new-window' ) ):
            self.separateTestResult.setFocus()
            if self.separateTestResult.isHidden():
                self.separateTestResult.showMaximized()
            self.separateTestResult.addResult(wTestResult=wTestResult)
        else:
            # new in v17
            nameLimit = Settings.instance().readValue( key = 'TestRun/tab-testname-limit' )
            nameLimit = int(nameLimit)

            if nameLimit == 0:
                _tabName = wTestResult.name
            else:
                if len(wTestResult.name) > nameLimit:
                    _tabName = "%s..." % wTestResult.name[:nameLimit]
                else:
                    _tabName = wTestResult.name
            # end of new in v17
            
            tabIndex = self.mainTab.addTab( wTestResult , QIcon(":/trx.png"), _tabName )
            self.mainTab.setTabToolTip(tabIndex, wTestResult.name)
            
            button = QToolButton()
            button.setIcon(QIcon(":/test-close.png"))
            button.setIconSize(QSize(15,15))
            button.setToolTip(self.tr("Close"))
            button.setStyleSheet( """
                         QToolButton {
                             border: none;
                             padding-right: 1px;

                         }

                         QToolButton:hover
                        {
                            border: 1px solid #8f8f91;

                        }

                      """)

            button.clicked.connect(wTestResult.closeTest)

            self.mainTab.tabBar().setTabButton(self.mainTab.count()-1, QTabBar.RightSide, button)

            if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-focus' ) ):
                self.mainTab.setCurrentWidget( wTestResult )

    def delTab (self, wTestResult):
        """
        Deletes tab

        @param wTestResult: test result widget
        @type wTestResult: QWidget
        """
        tesdId = TestResults.instance().getTestIdByWidget(wTestResult)
        TestResults.instance().delWidgetTest( testId=tesdId )
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/new-window' ) ):
            tabId = self.separateTestResult.delResult(wTestResult=wTestResult)
            # try to remove from the main if does not exist on the separate windows
            if tabId == -1:
                tabId =  self.mainTab.indexOf(wTestResult)
                self.mainTab.removeTab( tabId )
                self.mainTab.setCurrentWidget( WWorkspace.instance() )
        else:
            if TestResults.instance().getNumberOfTests() == 0:
                self.closeAllTests.setEnabled(False)
                self.buttonCloseAll.setEnabled(False)

            tabId =  self.mainTab.indexOf(wTestResult)
            self.mainTab.removeTab( tabId )
            self.mainTab.setCurrentWidget( WWorkspace.instance() )

    def updateTabColor (self, wTestResult, color ):
        """
        Update text color tab

        @param wTestResult: test result widget
        @type wTestResult: QWidget

        @param color:
        @type color:  QColor
        """
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/new-window' ) ):
            self.separateTestResult.updateTabColor(wTestResult, color)
        else:
            tabId =  self.mainTab.indexOf(wTestResult)
            self.mainTab.tabBar().setTabTextColor(tabId, color )

    def updateWindowTitle(self, title ):
        """
        Update the window title application

        @param title: new windows title
        @type title: string
        """
        name = Settings.instance().readValue( key = 'Common/name' )
        if title is None:
            self.setWindowTitle( "%s %s" % ( name, __VERSION__ ) )
        elif not len(title):
            self.setWindowTitle( "%s %s" % ( name, __VERSION__ ) )
        else:
            self.setWindowTitle( "%s %s - [%s]" % ( name, __VERSION__, title) )

    def onConnection (self, data):
        """
        Called on successful authentication with the server

        @param data: data received on connection
        @type data:
        """
        self.sendToStatusbar('Welcome %s' % UCI.instance().login )

        self.pluginsMenu.setEnabled(True)
        self.mainTab.setTabEnabled( self.TAB_SERVER, True )

        self.gotoHomepageAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=True)
        WWorkspace.WDocumentViewer.instance().updateMacroLink()

        WServerExplorer.instance().onConnection(data = data)
        WWorkspace.WRepositories.instance().onLoadRemote(data = data)
        WWorkspace.WHelper.instance().onLoad(data=data)

        self.mainTab.setTabEnabled( self.TAB_WORKSPACE, True )
        self.mainTab.setCurrentIndex( self.TAB_WORKSPACE )
        WWorkspace.WDocumentViewer.instance().enableWorkspace()
        WWorkspace.WDocumentViewer.instance().enableTabs()
        if not WWorkspace.WDocumentViewer.instance().isEmpty():
            # active test properties only if the first tab need it
            currentIndexTab = WWorkspace.WDocumentViewer.instance().tab.currentIndex()
            if WWorkspace.WDocumentViewer.instance().supportProperties( tabId=currentIndexTab ):
                WWorkspace.WDocumentProperties.instance().setEnabled(True)
       
        self.editMenu.setDisabled(False)
        self.sourceMenu.setDisabled(False)
        self.newMenu.setEnabled(True)
        if len(self.listActionsRecentFiles) > 0:
            self.recentMenu.setEnabled(True)
            self.openAllRecentFilesAction.setEnabled(True)
            self.emptyRecentFilesListAction.setEnabled(True)

        WWorkspace.Repositories.instance().initLocalRepo()
        WWorkspace.WDocumentViewer.instance().runSeveralAction.setEnabled(True)
        if not WWorkspace.WDocumentViewer.instance().isEmpty():
            WWorkspace.WDocumentViewer.instance().setCurrentActions()
        else:
            WWorkspace.WDocumentViewer.instance().runAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runStepByStepAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runBreakpointAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runBackgroundAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().checkAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().checkSyntaxAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().checkDesignAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runSchedAction.setEnabled(False)

        WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(True)
        WWorkspace.WDocumentViewer.instance().openAction.setEnabled(True)
        self.importImageAction.setEnabled(True)

        if UCI.RIGHTS_MONITOR in RCI.instance().userRights :
            WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(True)
            WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(True)
            WWorkspace.WDocumentViewer.instance().openAction.setEnabled(True)
            self.importImageAction.setEnabled(False)
            
        if sys.platform == "win32": 
            WRecorder.instance().restartGuiAction.setEnabled(True)
            self.desktopCaptureMenu.setEnabled(True)
            self.webCaptureMenu.setEnabled(True)
            self.mobCaptureMenu.setEnabled(True)
            self.basicCaptureMenu.setEnabled(True)
            self.sysCaptureMenu.setEnabled(True)
            
            if UCI.RIGHTS_MONITOR in RCI.instance().userRights :
                WRecorder.instance().restartGuiAction.setEnabled(False)
                self.desktopCaptureMenu.setEnabled(False)
                self.webCaptureMenu.setEnabled(False)
                self.mobCaptureMenu.setEnabled(False)
                self.basicCaptureMenu.setEnabled(False)
                self.sysCaptureMenu.setEnabled(False)
                
        self.networkCaptureMenu.setEnabled(True)
        if UCI.RIGHTS_MONITOR in RCI.instance().userRights :
            self.networkCaptureMenu.setEnabled(False)

    def onDisconnection (self):
        """
        Called on disconnection with the server
        """
        if sys.platform == "win32": 
            WRecorder.instance().restartGuiAction.setEnabled(False)
            self.desktopCaptureMenu.setEnabled(False)
            self.webCaptureMenu.setEnabled(False)
            self.mobCaptureMenu.setEnabled(False)
            self.basicCaptureMenu.setEnabled(False)
            self.sysCaptureMenu.setEnabled(False)
                
        self.networkCaptureMenu.setEnabled(False)
        
        self.mainTab.setTabEnabled( self.TAB_WORKSPACE, True )
        self.mainTab.setCurrentIndex( self.TAB_WORKSPACE )
        self.mainTab.setTabEnabled( self.TAB_SERVER, False )
        self.newMenu.setEnabled(False)
        self.openMenu.setEnabled(True)
        
        self.gotoHomepageAction.setEnabled(False)
        WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
                
        self.pluginsMenu.setEnabled(False)
        self.recentMenu.setEnabled(False)
        self.openAllRecentFilesAction.setEnabled(False)
        self.emptyRecentFilesListAction.setEnabled(False)

        if WServerExplorer.instance() is not None:
            WServerExplorer.instance().onDisconnection()

        if WWorkspace.WRepositories.instance() is not None:
            WWorkspace.WRepositories.instance().onResetRemote()

        if WWorkspace.WHelper.instance() is not None:
            WWorkspace.WHelper.instance().onReset()

        if WWorkspace.WDocumentViewer.instance() is not None:
            WWorkspace.Repositories.instance().cleanLocalRepo()

            WWorkspace.WDocumentViewer.instance().runSeveralAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().hideRunDialogs()

            WWorkspace.WDocumentViewer.instance().runAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runStepByStepAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runBreakpointAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runBackgroundAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().checkAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().checkSyntaxAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().checkDesignAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().runSchedAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(False)
            #
            WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(False)

            WWorkspace.WDocumentViewer.instance().openAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().setCurrentTabWelcome()
            self.importImageAction.setEnabled(False)

            WWorkspace.WDocumentViewer.instance().disableTabs()
            WWorkspace.WDocumentViewer.instance().disableWorkspace()
            WWorkspace.WDocumentProperties.instance().clear()
            WWorkspace.WDocumentProperties.instance().setEnabled(False)
            
        if TestResults.instance() is not None:
            for wTest in TestResults.instance().getWidgetTests():
                wTest.resetActions()

    def onLoadLocalTestResultTerminated(self, testId):
        """
        On load local testresult terminated
        """
        if TestResults.instance() is not None:
            TestResults.instance().onLoadLocalTestResultTerminated( testId=testId )
    
    def onLoadLocalTestResult(self, data):
        """
        On load local testresult
        """
        if data[0] in [ 'event' ] :
            if TestResults.instance() is not None:
                TestResults.instance().dispatchNotify( data = data[1], fromLocal=True )
        else:
            self.error( str(data) )
            
    def onNotify (self, data):
        """
        Called when a notify is received from server
        Dispatch notify between ServerExplorer and TestResults

        @param data: data received from server
        @type data:
        """
        if data[0] in [ 'task', 'archive', 'stats',
                        'users', 'users-stats',
                        'probes', 'probes-default',
                        'agents', 'agents-default',
                        'task-running', 'task-waiting', 'task-history', 'task-enqueued',
                        'repositories', "progressbar",
                        'archives', 'context-server', 'rn-libraries', 'rn-adapters',
                        ] :
            if WServerExplorer.instance() is not None:
                WServerExplorer.instance().notifyReceived(data)
        elif data[0] in [ 'event' ] :
            if TestResults.instance() is not None:
                TestResults.instance().dispatchNotify( data = data[1] )
        elif data[0] in [ 'supervision' ]:
            self.onTrap(data=data[1])
        elif data[0] in [ 'test' ]:
            self.onTestFileEvents(data=data[1])
        else:
            self.error( str(data) )
        
    def onTestFileEvents(self, data):
        """
        On test file events
        """
        try:
            actionName, actionData = data
            if actionName == "changed":
                changedBy=''
                if "modified-by" in actionData: changedBy = actionData["modified-by"]
                fileChanged = actionData["path"].split("/", 1)[1]
                
                msg = "The test (%s) has been modified by %s" % (fileChanged, changedBy)
                msg += "\n Please to re-open this file!"
                self.displayWarningMsg(title="Test changed", err=msg )
        except Exception as e:
            self.error("bad test changed event received: %s" % e)
  
    def onTrap(self, data):
        """
        Called on trap

        @param data: data received from server
        @type data:
        """
        try:
            trapLevel, trapData = data
            self.showMessageCriticalTray(msg=trapData)
        except Exception as e:
            self.error("bad trap received: %s" % e)
            
    def currentMainTabChanged (self, tabId):
        """
        Called when the current tab is changed
        Enable or disable actions

        @param tabid: tab id
        @type tabid: integer
        """
        tab = self.mainTab.widget(tabId)
        if tab.type == WWorkspace.instance().type:
            if len(self.listActionsRecentFiles) > 0:
                self.recentMenu.setEnabled(True)
                self.openAllRecentFilesAction.setEnabled(True)
                self.emptyRecentFilesListAction.setEnabled(True)

            if RCI.instance().isAuthenticated():
                WWorkspace.WDocumentViewer.instance().enableWorkspace()
                # if UCI.RIGHTS_DEVELOPER in RCI.instance().userRights or UCI.RIGHTS_ADMIN in RCI.instance().userRights:
                    # WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(True)
                    # WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(True)
                    # WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(True)
                    # WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(False)
                    # WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(False)
                    # WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(False)
                    # WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(False)
                    # WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(False)
                    # WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(False)
                    # WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(False)
                    # self.openTestResultAction.setEnabled(False)
                if UCI.RIGHTS_TESTER in RCI.instance().userRights or UCI.RIGHTS_ADMIN in RCI.instance().userRights :
                    WWorkspace.WDocumentViewer.instance().setCurrentActions()
                        
                    WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(True)
                    
                    WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(True)
                    self.openTestResultAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().openAction.setEnabled(True)
                if not WWorkspace.WDocumentViewer.instance().isEmpty():
                    WWorkspace.WDocumentViewer.instance().closeTabAction.setEnabled(True)
                    WWorkspace.WDocumentViewer.instance().closeAllTabAction.setEnabled(True)
                self.editMenu.setEnabled(True)
                self.sourceMenu.setEnabled(True)
            else:
                if not WORKSPACE_OFFLINE:
                    WWorkspace.WDocumentViewer.instance().disableWorkspace()
                    WWorkspace.WDocumentViewer.instance().openAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().closeTabAction.setEnabled(False)
                    WWorkspace.WDocumentViewer.instance().closeAllTabAction.setEnabled(False)

        elif tab.type == WServerExplorer.instance().type:
            WWorkspace.WDocumentViewer.instance().hideFindReplaceWidget()
            
            WWorkspace.WDocumentViewer.instance().runSchedAction.setEnabled(False)
            
            WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().openAction.setEnabled(False)
            self.openTestResultAction.setEnabled(True)
            WWorkspace.WDocumentViewer.instance().closeTabAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().closeAllTabAction.setEnabled(False)
            self.editMenu.setEnabled(False)
            self.sourceMenu.setEnabled(False)
            self.recentMenu.setEnabled(False)
            self.openAllRecentFilesAction.setEnabled(False)
            self.emptyRecentFilesListAction.setEnabled(False)
        else:
            WWorkspace.instance().hideStatusBar()
            self.editMenu.setEnabled(False)
            self.sourceMenu.setEnabled(False)
            self.recentMenu.setEnabled(False)
            self.openAllRecentFilesAction.setEnabled(False)
            self.emptyRecentFilesListAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestUnitAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestAbstractAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestSuiteAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestPlanAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestGlobalAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestDataAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTestConfigAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newAdapterAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newLibraryAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().newTxtAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().openAction.setEnabled(False)
            self.openTestResultAction.setEnabled(True)
            WWorkspace.WDocumentViewer.instance().closeTabAction.setEnabled(False)
            WWorkspace.WDocumentViewer.instance().closeAllTabAction.setEnabled(False)

    def about(self):
        """
        Display About Menu
        """
        url = Settings.instance().readValue( key = 'Common/url' )
        name = Settings.instance().readValue( key = 'Common/name' )
        #
        about = [ "<b>%s %s</b>" % (name,__VERSION__) ]
        about.append( "Copyright (c) %s-%s %s" % (__BEGIN__,__END__, __AUTHOR__) )
        about.append( "Extensive Testing<br />" )

        about.append( "%s" % self.tr("This application tries to save your time and make your life easier at work.") )
        about.append( "%s" % self.tr("Use at your own risk, no warranty, no promises...") )
        about.append( "%s" % self.tr("Enjoy!") )
        about.append( "" )           
        about.append( "%s: <a href='mailto:%s'>%s</a>" %(self.tr("Contact"), __EMAIL__,__EMAIL__) )
        about.append( "%s: <a href='%s'>%s</a>" % (self.tr("Home page"), url, url) )
        about.append( "" )
        about.append( "%s: <i>%s</i>" % (self.tr("Contributors"), ' '.join(__CONTRIBUTORS__)))
        about.append( "%s: <i>%s</i>" % (self.tr("Testers"), ', '.join(__TESTERS__)))

        about.append( "<hr />" )
        about.append( "%s <b>%s</b>" % (self.tr("Developed and maintained by"), __AUTHOR__) ) 

        about.append( "%s python %s (%s) - Qt %s - PyQt %s on %s" % (self.tr("Built with: "), 
                                                                        platform.python_version(), 
                                                                        platform.architecture()[0],
                                                                        QT_VERSION_STR, PYQT_VERSION_STR,  
                                                                        platform.system() )
                    )
        about.append( "%s %s" % (self.tr("Built time: "), __BUILDTIME__ )  )
        if QtHelper.str2bool(Settings.instance().readValue( key = 'Common/portable')): 
            about.append( "%s" % self.tr("Portable edition") )
        about.append( "<hr />" )
        about.append( LICENSE ) 
        QMessageBox.about(self, "%s - %s" % (name, self.tr("About")), "<br />".join(about) )

    def releaseNotes (self):
        """
        Read the release notes
        """
        rn = ''
        try:
            # open the release note from resources and read all
            fh = QFile(":/releasenotes.txt")
            fh.open(QFile.ReadOnly)
            rn = fh.readAll()
            
            # convert qbytearray to str
            if sys.version_info > (3,):
                rn = unicode(rn, 'utf8') # to support python3 
            else:
                rn = unicode(rn)
                
            # close the file descriptor
            fh.close()
        except Exception as e:
            self.error( "Unable to read release notes: " + str(e) )
            
        # open the dialog
        name = Settings.instance().readValue( key = 'Common/name' )
        rnDialog = RN.ReleaseNotesDialog( dialogName = name, parent = self)
        rnDialog.parseRn( text = rn )
        rnDialog.exec_()

    def onRefreshTestsRepo(self, data, projectId, forSaveAs, forRuns):
        """
        """
        if forRuns:
            WWorkspace.WDocumentViewer.instance().onRefreshRepositoryRuns(data, projectId)
        else:
            WWorkspace.WRepositories.instance().onRefreshRemoteTests(data, projectId, forSaveAs)

    def onRefreshAdaptersRepo(self, data):
        """
        """
        WWorkspace.WRepositories.instance().onRefreshRemoteAdapters(data)

    def onRefreshLibrariesRepo(self, data):
        """
        """
        WWorkspace.WRepositories.instance().onRefreshRemoteLibraries(data)
        
    def onGetFileRepo(self, path_file, name_file, ext_file, encoded_data, 
                        project, forDest, actionId, testId):
        """
        Called on get file from remote repository

        @param data: data received from server
        @type data:
        """
        # for test plan
        if forDest == UCI.FOR_DEST_TP:
            if actionId == UCI.ACTION_ADD:
                WWorkspace.WDocumentViewer.instance().addRemoteTestToTestplan( data=(str(path_file), str(name_file), 
                                                                                str(ext_file), encoded_data, project), 
                                                                                testParentId=testId )
            elif actionId == UCI.ACTION_INSERT_AFTER:
                WWorkspace.WDocumentViewer.instance().insertRemoteTestToTestplan( data=(str(path_file), str(name_file), 
                                                                                    str(ext_file), encoded_data, project),
                                                                                  below=False, testParentId=testId )
            elif actionId == UCI.ACTION_INSERT_BELOW:
                WWorkspace.WDocumentViewer.instance().insertRemoteTestToTestplan( data=(str(path_file), str(name_file), 
                                                                                    str(ext_file), encoded_data, project),
                                                                                  below=True, testParentId=testId )
                
            elif actionId == UCI.ACTION_RELOAD_PARAMS:
                WWorkspace.WDocumentViewer.instance().updateRemoteTestOnTestplan( data=(
                                                                                        str(path_file), str(name_file), str(ext_file),
                                                                                        encoded_data, testId, project
                                                                                        ) 
                                                                                 )
                
            elif actionId == UCI.ACTION_MERGE_PARAMS:
                WWorkspace.WDocumentViewer.instance().updateRemoteTestOnTestplan( data=(
                                                                                        str(path_file), str(name_file), str(ext_file),
                                                                                        encoded_data, testId, project
                                                                                        )  ,
                                                                                    mergeParameters=True
                                                                                 )

            elif actionId == UCI.ACTION_UPDATE_PATH:
                WWorkspace.WDocumentViewer.instance().updateRemoteTestOnTestplan( data=(
                                                                                        str(path_file), str(name_file), str(ext_file),
                                                                                        encoded_data, testId, project
                                                                                        ),
                                                                                  parametersOnly=False
                                                                                 )

            else:
                self.error( 'unknown action id for tp: %s' % actionId )

        # for test global
        elif forDest == UCI.FOR_DEST_TG:
            if actionId == UCI.ACTION_ADD:
                WWorkspace.WDocumentViewer.instance().addRemoteTestToTestglobal( data=(str(path_file), str(name_file), 
                                                                                    str(ext_file), encoded_data, project), 
                                                                                        testParentId=testId )
            elif actionId == UCI.ACTION_INSERT_AFTER:
                WWorkspace.WDocumentViewer.instance().insertRemoteTestToTestglobal( data=(str(path_file), str(name_file), 
                                                                                    str(ext_file), encoded_data, project),
                                                                                    below=False, testParentId=testId )
            elif actionId == UCI.ACTION_INSERT_BELOW:
                WWorkspace.WDocumentViewer.instance().insertRemoteTestToTestglobal( data=(str(path_file), str(name_file), 
                                                                                    str(ext_file), encoded_data, project),
                                                                                    below=True, testParentId=testId )
            elif actionId == UCI.ACTION_RELOAD_PARAMS:
                WWorkspace.WDocumentViewer.instance().updateRemoteTestOnTestglobal( data=(
                                                                                            str(path_file), str(name_file), 
                                                                                            str(ext_file),
                                                                                            encoded_data, testId, project
                                                                                          ) 
                                                                                   )
            elif actionId == UCI.ACTION_MERGE_PARAMS:
                WWorkspace.WDocumentViewer.instance().updateRemoteTestOnTestglobal( data=(
                                                                                            str(path_file), str(name_file), 
                                                                                            str(ext_file),
                                                                                            encoded_data, testId, project
                                                                                          ) ,
                                                                                    mergeParameters=True
                                                                                   )
            elif actionId == UCI.ACTION_UPDATE_PATH:
                WWorkspace.WDocumentViewer.instance().updateRemoteTestOnTestglobal( data=(
                                                                                            str(path_file), str(name_file), 
                                                                                            str(ext_file),
                                                                                            encoded_data, testId, project
                                                                                          ),
                                                                                    parametersOnly=False
                                                                                   )
            else:
                self.error( 'unknown action id for tg: %s' % actionId )

        # for all type of tests
        elif forDest == UCI.FOR_DEST_ALL:
            if actionId == UCI.ACTION_IMPORT_INPUTS:
                WWorkspace.WDocumentProperties.instance().addRemoteTestConfigToTestsuite( data=(str(path_file), str(name_file), 
                                                                                            str(ext_file),  encoded_data, project), 
                                                                                          inputs=True )
            elif actionId == UCI.ACTION_IMPORT_OUTPUTS:
                WWorkspace.WDocumentProperties.instance().addRemoteTestConfigToTestsuite( data=(str(path_file), str(name_file), 
                                                                                          str(ext_file), encoded_data, project),
                                                                                          inputs=False )
            else:
                self.error( 'unknown action id for all: %s' % actionId )
        
        else:
            self.error( 'unknown destination id: %s' % forDest )

    def onTestKilled(self, data):
        """
        Called when a test is killed
        """
        TestResults.instance().killWidgetTest(tid=data)

    def onTestsKilled(self):
        """
        Called when a test is killed
        """
        WServerExplorer.TestManager.instance().testKilled()

    def onTestVerdictLoaded(self, data, dataXml):
        """
        Called when a test result verdict is returned
        """
        
        dexport = TestResults.WExportVerdict(self, data=data, dataXml=dataXml)
        
        # register plugin
        for pluginId, pluginDescr in self.pluginsStarted.items():
            pluginName, pluginType, pluginProcess = pluginDescr
            if pluginType == "test-results":
                plugIcon = QIcon(":/plugin.png")  
                if pluginName in self.pluginsIcons: plugIcon = self.pluginsIcons[pluginName]
                pluginAct  =  QtHelper.createAction(self, pluginName, self.openPluginMain, 
                                                    cb_arg= { 'pluginId': pluginId, 
                                                            'pluginData': dexport.pluginDataAccessor },
                                                    icon=plugIcon
                                                )
                dexport.addPlugin(pluginAct)
                
        dexport.exec_()

    def onTestReportLoaded(self, data, dataXml):
        """
        Called when a test result verdict is returned
        """
        dexport = TestResults.WExportReport(self, data=data, dataXml=dataXml)      

        
        # register plugin
        for pluginId, pluginDescr in self.pluginsStarted.items():
            pluginName, pluginType, pluginProcess = pluginDescr
            if pluginType == "test-results":
                plugIcon = QIcon(":/plugin.png")  
                if pluginName in self.pluginsIcons: plugIcon = self.pluginsIcons[pluginName]
                pluginAct  =  QtHelper.createAction(self, pluginName, self.openPluginMain, 
                                                cb_arg= { 'pluginId': pluginId, 
                                                            'pluginData': dexport.pluginDataAccessor },
                                                icon=plugIcon                                       
                                    )
                dexport.addPlugin(pluginAct)
                
        dexport.exec_()

    def onTestDesignLoaded(self, data, dataXml):
        """
        Called when a test result design is returned
        """
        dexport = TestResults.WExportDesign(self, data=data, dataXml=dataXml)
        
        # register plugin
        for pluginId, pluginDescr in self.pluginsStarted.items():
            pluginName, pluginType, pluginProcess = pluginDescr
            if pluginType == "test-results":
                plugIcon = QIcon(":/plugin.png")  
                if pluginName in self.pluginsIcons: plugIcon = self.pluginsIcons[pluginName]
                pluginAct  =  QtHelper.createAction(self, pluginName, self.openPluginMain, 
                                                    cb_arg= { 'pluginId': pluginId,  
                                                            'pluginData': dexport.pluginDataAccessor },
                                                    icon= plugIcon   
                                    )
                dexport.addPlugin(pluginAct)
                
        dexport.exec_()

    def onPauseCalled(self, tid, stepId, stepSummary, timeout, testId):
        """
        Called on test pause
        """
        wtest = TestResults.instance().getWidgetTest(testId=testId)
        if wtest is not None:
            wtest.pause(tid=tid, stepId=stepId, stepSummary=stepSummary)

    def onBreakPointCalled(self, tid, testId, timeout):
        """
        Called on test breakpoint
        """
        wtest = TestResults.instance().getWidgetTest(testId=testId)
        if wtest is not None:
            wtest.breakpoint(tid=tid)

    def onInteractCalled(self, tid, ask, timeout, testId, default):
        """
        Called on interact 
        timeout in seconds
        """
        wtest = TestResults.instance().getWidgetTest(testId=testId)
        if wtest is not None:
            wtest.interact(tid=tid, ask=ask, counter=timeout, default=default)

    def onStatisticsResetted(self):
        """
        On statistics Resetted
        """
        WServerExplorer.Counters.instance().resetCounters()
        
def showMessageSplashscreen(msg, sleep=0):
    """
    Show message on splahsscreen
    """
    time.sleep(sleep)
    progress.setValue( progress.value()+1 )
    splash.showMessage( msg, Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    
if __name__ == '__main__':
    """
    Main part
    """
    # performance measurement only for debug mode
    starttime = time.time()

    # Construct the main app
    if sys.platform == "win32":
        app = QApplication(sys.argv)
    if sys.platform in [ "linux", "linux2" , "darwin"] :
        app = QApplication(sys.argv)

        
    # register an alternative Message Handler to hide warning
    # messageHandler = MessageHandler()
    # qInstallMsgHandler(messageHandler.process) # disable in v11, crash with webkit


    # Qt erroneously thinks you want to quit the application when the main windows is minimized
    # so we disable this behaviour added to introduce properly the menu in the system tray
    # app.setQuitOnLastWindowClosed(False) # disable in v11, not necessary ?

    # Create and display the splash screen
    nbEvents = 8
    splash_pix = QPixmap(':/splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)

    progress = QProgressBar(splash)
    progress.setAlignment(Qt.AlignCenter)
    progress.setMaximum(nbEvents)
    progress.setGeometry( splash.width()/10, 7.5*splash.height()/10, 
                            8*splash.width()/10, splash.height()/10)

    qlabel = QLabel(splash)
    qfont = QFont()
    qfont.setBold(True)
    qlabel.setAlignment(Qt.AlignRight)
    qlabel.setText(__VERSION__)
    qlabel.setFont(qfont)
    qlabel.setGeometry( splash.width()/10, 6*splash.height()/10, 
                        7.8*splash.width()/10, splash.height()/10)

    
    splash.setMask(splash_pix.mask())
    splash.show()


    # initiliaze settings application, read settings from the ini file
    Settings.initialize(offlineMode=WORKSPACE_OFFLINE)

    # load internal qt translations for generic message box: en_US, fr_FR
    # according to the language configurated on the setting file
    translatorQt = QTranslator()
    translatorQt.load("qt_%s" % Settings.instance().readValue( key = 'Common/language' ), 
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath) )
    qApp.installTranslator(translatorQt)

    # install private translation file according to the language configurated on the setting file
    translator = QTranslator()
    translator.load(":/%s.qm" % Settings.instance().readValue( key = 'Common/language' ) )
    qApp.installTranslator(translator)
    
    showMessageSplashscreen( QObject().tr('Starting...') )
    showMessageSplashscreen( QObject().tr('Installing localizations...') )

    # Instantiate the main application and display-it
    showMessageSplashscreen( QObject().tr('Initializing main application...') )
    window = MainApplication()

    showMessageSplashscreen( QObject().tr('Terminated...') )

    window.show()

    # change the view according to the settings user
    if ( Settings.instance().readValue( key = 'View/helper' ) == 'False' ):
        window.hideHelperWindowAction.setChecked(False)
        WWorkspace.instance().hideHelper() 
    if ( Settings.instance().readValue( key = 'View/developer' ) == 'True' ):
        WWorkspace.instance().hideDeveloperModeAction.setChecked(True)
        WWorkspace.instance().activeDeveloperView() 
        
    # no more display the splash
    if sys.platform == "win32":
        splash.finish(window)
    if sys.platform in [ "linux", "linux2", "darwin" ]:
        splash.finish(window)

    # performance measurement only  for debug mode
    stoptime = time.time()
    startuptime =  stoptime - starttime
    Logger.debug( "Startup in %s seconds" % startuptime)

    # show maximized by default, to support pyqt5
    # added in v17.1
    window.showMaximized()
    
    # exec the application and exit on stop
    sys.exit(app.exec_())