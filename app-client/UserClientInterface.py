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
User client interface
"""

# import standard modules
import sys
import time
import base64
import zlib
import hashlib
import copy
import os
import urllib
import json
from threading import Thread
import subprocess

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QDialog)
    from PyQt4.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)
except ImportError:
    from PyQt5.QtWidgets import (QDialog)
    from PyQt5.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)

from Libs import PyBlowFish, QtHelper, Logger
import Libs.NetLayerLib.ClientAgent as NetLayerLib
import Libs.NetLayerLib.Messages as Messages

import TestResults
import Settings
import ServerExplorer

import Workspace as WWorkspace
import RestClientInterface as RCI

EXT_TESTUNIT = "tux"
EXT_TESTSUITE = "tsx"
EXT_TESTPLAN = "tpx"
EXT_TESTGLOBAL = "tgx"
EXT_TESTABSTRACT = "tax"


############## RESPONSE CODE ##############

# CODE_ERROR                  = 500
# CODE_DISABLED               = 405
# CODE_ALLREADY_EXISTS        = 420
# CODE_NOT_FOUND              = 404
# CODE_LOCKED                 = 421
# CODE_ALLREADY_CONNECTED     = 416
# CODE_FORBIDDEN              = 403
# CODE_FAILED                 = 400
# CODE_OK                     = 200

############## USERS TYPE ##############
RIGHTS_ADMIN                =   "Administrator"
RIGHTS_TESTER               =   "Tester"
RIGHTS_MONITOR              =   "Monitor"

RIGHTS_USER_LIST            =  [ 
                                    RIGHTS_ADMIN, 
                                    RIGHTS_MONITOR,
                                    RIGHTS_TESTER
                                ]

############## SCHEDULATION TYPE ##############
SCHED_NOW                   =   0      # one run 
SCHED_AT                    =   1       # run postponed
SCHED_IN                    =   2       # run postponed
SCHED_EVERY_SEC             =   3
SCHED_EVERY_MIN             =   4
SCHED_HOURLY                =   5
SCHED_DAILY                 =   6
SCHED_EVERY_X               =   7
SCHED_WEEKLY                =   8
SCHED_NOW_MORE              =   9
SCHED_QUEUE                 =   10      # run enqueued
SCHED_QUEUE_AT              =   11     # run enqueued at


SCHED_DAYS_DICT =   {
                        0           :   'monday',
                        1           :   'tuesday',
                        2           :   'wednesday',
                        3           :   'thursday',
                        4           :   'friday',
                        5           :   'saturday',
                        6           :   'sunday',
                    }

############## TASKS TYPE ##############
TASKS_RUNNING                       =   0
TASKS_WAITING                       =   1
TASKS_HISTORY                       =   2

############## REPOSITORY TYPE ##############
REPO_TESTS                          =   0
REPO_ADAPTERS                       =   1
REPO_TESTS_LOCAL                    =   2
REPO_UNDEFINED                      =   3
REPO_ARCHIVES                       =   4
REPO_LIBRARIES                      =   5

REPO_TYPES_DICT =   {
                        REPO_TESTS          :   'remote-tests',
                        REPO_ADAPTERS       :   'remote-adapters',
                        REPO_TESTS_LOCAL    :   'local-tests',
                        REPO_UNDEFINED      :   'undefined',
                        REPO_ARCHIVES       :   'archives',
                        REPO_LIBRARIES      :   'remote-libraries'
                    }

############## PROBES RESULT START ##############

PROBE_REG_OK                    =   0
PROBE_REG_FAILED                =   1
PROBE_REG_TIMEOUT               =   2
PROBE_REG_REFUSED               =   3
PROBE_REG_HOSTNAME_FAILED       =   4
PROBE_REG_CONN_REFUSED          =   5
PROBE_TYPE_UNKNOWN              =   -2

AGENT_REG_OK                    =   0
AGENT_REG_FAILED                =   1
AGENT_REG_TIMEOUT               =   2
AGENT_REG_REFUSED               =   3
AGENT_REG_HOSTNAME_FAILED       =   4
AGENT_REG_CONN_REFUSED          =   5
AGENT_TYPE_UNKNOWN              =   -2

ACTION_MERGE_PARAMS     = 7
ACTION_UPDATE_PATH      = 6
ACTION_IMPORT_OUTPUTS   = 5
ACTION_IMPORT_INPUTS    = 4
ACTION_RELOAD_PARAMS    = 3
ACTION_INSERT_AFTER     = 2
ACTION_INSERT_BELOW     = 1
ACTION_ADD              = 0

FOR_DEST_TP             = 1
FOR_DEST_TG             = 2
FOR_DEST_TS             = 3
FOR_DEST_TU             = 4
FOR_DEST_ALL            = 10


def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val

class UserClientInterface(QObject, Logger.ClassLogger, NetLayerLib.ClientAgent):
    """
    User client interface
    """ 
    CriticalMsg = pyqtSignal(str, str)  
    WarningMsg = pyqtSignal(str, str)  
    InformationMsg = pyqtSignal(str, str)  
    Disconnected = pyqtSignal()
    Notify = pyqtSignal(tuple)  
    Interact = pyqtSignal(int, str, float, int, str) 
    Pause = pyqtSignal(int, str, str, float, int) 
    BreakPoint = pyqtSignal(int, int, float) 
    ArrowCursor = pyqtSignal() 
    BusyCursor = pyqtSignal()
    def __init__(self, parent = None, clientVersion=None):
        """
        Qt Class User Client Interface
        Signals:
         * Connected
         * Disconnected
         * Notify
         * RefreshRepo
         * refreshStatsRepo
         * getFileRepo
         * addDirRepo
         * testKilled
         * testCancelled

        @param parent: 
        @type parent:
        """
        QObject.__init__(self, parent)
        NetLayerLib.ClientAgent.__init__(self, typeAgent = NetLayerLib.TYPE_AGENT_USER,
                            keepAliveInterval=int(Settings.instance().readValue( key = 'Network/keepalive-interval' )), 
                            inactivityTimeout=int(Settings.instance().readValue( key = 'Network/inactivity-timeout' )),
                            timeoutTcpConnect=int(Settings.instance().readValue( key = 'Network/tcp-connect-timeout' )),
                            responseTimeout=int(Settings.instance().readValue( key = 'Network/response-timeout' )),
                            selectTimeout=float(Settings.instance().readValue( key = 'Network/select-timeout' )),
                            sslSupport=QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' )),
                            wsSupport=QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' )),
                            pickleVer=int(Settings.instance().readValue( key = 'Network/pickle-version' )),
                            tcpKeepAlive=QtHelper.str2bool(Settings.instance().readValue( key = 'Network/tcp-keepalive' )), 
                            tcpKeepIdle=int(Settings.instance().readValue( key = 'Network/tcp-keepidle' )),
                            tcpKeepCnt=int(Settings.instance().readValue( key = 'Network/tcp-keepcnt' )), 
                            tcpKeepIntvl=int(Settings.instance().readValue( key = 'Network/tcp-keepintvl' ))
                        )
        self.parent = parent
        self.password = ""
        self.login = ""
        self.channelId = None
        self.clientVersion = clientVersion
        self.appName = Settings.instance().readValue( key = 'Common/name' )
        self.address = ""
        self.addressResolved = ""
        self.portWs = 0
        
        self.addressProxyHttp = ""
        self.addressProxyHttpResolved = ""
        self.proxyActivated = False

        self.portData = Settings.instance().readValue( key = 'Server/port-data' )
        self.loaderDialog = QtHelper.MessageBoxDialog(dialogName = self.tr("Loading"))

        self.parent.DataProgress.connect(self.updateDataReadProgress)

    def application(self):
        """
        return main application instance
        """
        return self.parent

    def getLogin(self):
        """
        Returns login
        """
        return self.login

    def updateDataReadProgress (self, bytesRead, totalBytes):
        """
        Called to update progress bar

        @param bytesRead: 
        @type bytesRead:

        @param totalBytes: 
        @type totalBytes:
        """
        self.loaderDialog.updateDataReadProgress(bytesRead, totalBytes) 

    def getScheme(self):
        """
        Return scheme
        """
        if eval( Settings.instance().readValue( key = 'Server/api-ssl' ) ):
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def getHttpPort(self):
        """
        Return http port
        """
        httpPort = Settings.instance().readValue( key = 'Server/port-api' )
        return httpPort
    
    def getHttpAddress(self):
        """
        Return http address
        """
        addr =  Settings.instance().readValue( key = 'Server/last-addr' )
        if ":" in addr:
            return addr.split(":")[0]
        else:
            return addr
            
    def setCtx(self, address, login, password, supportProxy, addressProxyHttp, portProxyHttp):
        """
        Sets login and password given by the user
        Password is encoded to md5

        @param address: 
        @type address:

        @param port: 
        @type port:

        @param login: 
        @type login:
        
        @param password: 
        @type password:
        """
        if supportProxy:
            self.proxyActivated = True
        else:
            self.proxyActivated = False
            
        NetLayerLib.ClientAgent.unsetProxy(self)
        ServerExplorer.instance().RestService.unsetWsProxy()
        
        self.address = address
        self.addressProxyHttp = addressProxyHttp
        self.portProxyHttp = portProxyHttp

        self.login = login
        self.password = hashlib.sha1( password.encode('utf8') ).hexdigest()
        # resolve server address

        # read port from settings, can be changed from preferences
        self.portWs = int( Settings.instance().readValue( key = 'Server/port-api' ) )
        self.portData = int( Settings.instance().readValue( key = 'Server/port-data' ) )
        
        resolved = NetLayerLib.ClientAgent.setServerAddress(self, ip = address, port = int(self.portData) )
        if resolved is None:
            ret = resolved
        else:
            dst_ip, dst_port = resolved
            self.addressResolved = dst_ip

            # set the agent name
            NetLayerLib.ClientAgent.setAgentName( self, self.login ) 

            scheme = "http"
            if Settings.instance().readValue( key = 'Server/api-ssl' ) == "True" :
                scheme = "https"
            
            # do not resolve ip in this case
            if self.proxyActivated and len(addressProxyHttp) and portProxyHttp:
                dst_ip = address
                
            ServerExplorer.instance().configureServer( address= dst_ip, port = self.portWs,
                                                        scheme=scheme, hostname=self.address )

            # resolve proxy if activated 
            if self.proxyActivated and len(addressProxyHttp) and portProxyHttp:
                resolvedProxyHttp = NetLayerLib.ClientAgent.setProxyAddress(self, ip = addressProxyHttp, 
                                                                            port = int(portProxyHttp) )
                if resolvedProxyHttp is None:
                    ret = resolvedProxyHttp
                else:
                    dst_ip, dst_port = resolvedProxyHttp
                    self.addressProxyHttpResolved = dst_ip
                
                # set proxy on ws http
                ServerExplorer.instance().configureProxy(ip=self.addressProxyHttpResolved, 
                                                         port=portProxyHttp)
            ret = True
        return ret

    def connectChannel(self):
        """
        Connect channel
        """
        self.startConnection()

    def onResolveHostnameFailed(self, err):
        """
        On resolve hostname failed

        @param err: message
        @type err: string
        """
        if 'Errno 11004' in err:
            msgErr = 'Server address resolution failed'
        else:
            msgErr = err
            
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection") , 
                              "%s:\n%s" % (self.tr("Error occured"),msgErr) )

    def onResolveHostnameProxyFailed(self, err):
        """
        On resolve proxy hostname failed

        @param err: message
        @type err: string
        """
        if 'Errno 11004' in str(err):
            msgErr = 'Proxy address resolution failed'
        else:
            msgErr = err
            
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection Proxy") , 
                              "%s:\n%s" % (self.tr("Error occured"),msgErr) )
    
    def onConnectionRefused(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        if 'Errno 10061' in err:
            msgErr = 'The connection has been refused by the server'
        else:
            msgErr = err
            
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection") , 
                              "%s:\n%s" % (self.tr("Error occured"),msgErr) )

    def onConnectionTimeout(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection") , "%s %s.\n%s\n\n%s" % ( self.tr('Connection'), err,  self.tr("Please retry!"),
                                                                            self.tr("If the problem persists contact your administrator.") )
                            )

    def onWsHanshakeError(self, err):
        """
        Called on websocket error
        """
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection") , "%s %s.\n%s\n\n%s" % ( self.tr('Connection'), err,  self.tr("Please retry!"),
                                                                            self.tr("If the problem persists contact your administrator.") )
                            )

    def onProxyConnectionRefused(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        if 'Errno 10061' in err:
            msgErr = 'Proxy: the connection has been refused by the server'
        else:
            msgErr = err
            
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection Proxy") , str(msgErr) )

    def onProxyConnectionError(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        ServerExplorer.instance().stopWorking()
        self.closeConnection()
        ServerExplorer.instance().enableConnect()
        WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        
        self.emitCriticalMsg( self.tr("Connection Proxy") , str(err) )

    def onProxyConnectionTimeout(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
            
        self.emitCriticalMsg( self.tr("Connection Proxy") , "%s %s.\n%s\n\n%s" % ( self.tr("Connection Proxy"), err, self.tr("Please retry!"),
                                                                self.tr("If the problem persists contact your administrator.") )
                             )

    def onProxyConnection(self):
        """
        On proxy connection
        """
        self.trace('Proxy initialization...')
        try:
            self.sendProxyHttpRequest()
        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Connection Proxy") , str(e) )

    def onConnection(self):
        """
        On connection
        """
        try:
            websocketSupport = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' ))
            websocketSsl = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' ))
            if websocketSupport:
                self.trace('Websocket initialization...')
                wspath = Settings.instance().readValue( key = 'Server/websocket-path' )
                if websocketSsl:
                    wspath = Settings.instance().readValue( key = 'Server/websocket-secure-path' )
                self.handshakeWebSocket(resource=wspath, hostport=self.address)
        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Channel handshake") , str(e) )

    def onProxyConnectionSuccess(self):
        """
        On proxy connection with success
        """
        try:
            websocketSupport = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' ))
            websocketSsl = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' ))
            if websocketSupport:
                self.trace('Websocket initialization through proxy...')
                wspath = Settings.instance().readValue( key = 'Server/websocket-path' )
                if websocketSsl:
                    wspath = Settings.instance().readValue( key = 'Server/websocket-secure-path' )
                self.handshakeWebSocket(resource=wspath, hostport=self.address)
        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Channel handshake through proxy") , str(e) )

    def onFirstNotify(self):
        """
        On first notify received from server
        """
        self.trace('API Authentication...')

        # rest call
        RCI.instance().login(  login=self.login, 
                               password=self.password, 
                               channelId=self.channelId  )

    def emitCriticalMsg(self, title, err):
        """
        Emit a critical message
        """
        self.CriticalMsg.emit(title, err)  
    
    def emitWarningMsg(self, title, err):
        """
        Emit a warning message
        """
        self.WarningMsg.emit(title, err)  
    
    def emitInformationMsg(self,title, err):
        """
        Emit a infomational message
        """
        self.InformationMsg.emit(title, err)  

    def onDisconnection(self, byServer=False, inactivityServer=False):
        """
        Reimplemented from ClientDataChannel
        Emit "Disconnected" on disconnection
        """
        self.trace('on disconnection byserver=%s inactivitserver=%s...' %(byServer, inactivityServer) )
           
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/rest-support' ) ):
            if not byServer:
                RCI.instance().logout()

        if inactivityServer:
            if ServerExplorer.instance() is not None: ServerExplorer.instance().stopWorking()

            self.channelId = None
            
            self.Disconnected.emit() 
            
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageWarningTray(msg="%s\n%s" % (self.tr("Inactivity detected, connection closed"), 
                                                                            self.tr("Please to reconnect!")))
            else:  
                self.emitCriticalMsg( self.tr("Connection") , "%s\n%s" % (self.tr("Inactivity detected, connection closed"), 
                                                                            self.tr("Please to reconnect!")) )

            
        else:
            if self.isConnected():  self.trace('Disconnection...')
            self.channelId = None

            NetLayerLib.ClientAgent.onDisconnection(self)
            if ServerExplorer.instance() is not None: ServerExplorer.instance().stopWorking()
            
            self.Disconnected.emit() 
            
            msg = "Disconnected by the server.\nPlease to reconnect"
            if byServer:
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageWarningTray(msg=self.tr(msg))
                else: 
                    self.emitWarningMsg(title=self.tr("Connection"), err=self.tr(msg))
        
    def onRequest (self, client, tid, request):
        """
        Reimplemented from ClientAgent
        Emit "Notify" when NOTIFY message is received

        @param event: 
        @type event:
        """
        if request['cmd'] == Messages.RSQ_NOTIFY:
            if  request['body'][0] == 'reg':
                if self.channelId is None:
                    self.channelId = request['body'][1]['channel-id']
                    self.onFirstNotify()
                else:
                    self.channelId = request['body'][1]['channel-id']
            else:
                self.Notify.emit( request['body'] )
                
        elif request['cmd'] == Messages.RSQ_CMD:
            if 'cmd' in request['body']:
                if request['body']['cmd'] == Messages.CMD_INTERACT:
				
                    if 'ask' in request['body']:
					
                        # new in v12.2
                        defaultValue = ''
                        if 'default' in request['body']:
                            defaultValue = request['body']['default']
                        # end of new
                        self.Interact.emit( tid, request['body']['ask'], request['body']['timeout'], 
											int(request['body']['test-id']), defaultValue )
											
                    if 'pause' in request['body']:
                        self.Pause.emit( tid, request['body']['step-id'], 
                                         request['body']['step-summary'],
                                         request['body']['timeout'], 
                                         int(request['body']['test-id']) )
                                         
                    if 'breakpoint' in request['body']:
                        self.BreakPoint.emit( tid, 
                                              int(request['body']['test-id']), 
                                              request['body']['timeout'] )
                                              
                else:
                    NetLayerLib.ClientAgent.forbidden(self, tid=tid, body='' )
            else:
                NetLayerLib.ClientAgent.forbidden(self, tid=tid, body='' )
        else:
            self.trace('%s received ' % request['cmd'])

UCI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return UCI

def initialize (parent, clientVersion):
    """
    Initialize the class UserClientInterface

    @param parent:
    @type: parent:

    @param clientVersion:
    @type: clientVersion:
    """
    global UCI
    UCI = UserClientInterface(parent, clientVersion)

def finalize ():
    """
    Destroy Singleton
    """
    global UCI
    if UCI:
        del UCI
        UCI = None