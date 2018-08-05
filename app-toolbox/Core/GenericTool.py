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
Generic tool class
Used on plugins
"""

import Libs.NetLayerLib.ClientAgent as NetLayerLib
import Libs.NetLayerLib.Messages as Messages

from Libs import Logger, Settings
import Libs.FifoQueue as FifoQueue

import os
import threading
import time
import sys
import shutil
import zipfile
import json
import base64
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str    

AGENT_INITIALIZED       = "AGENT_INITIALIZED"

CALL_FAILED             =   None
ARGUMENTS_MISSING       =   -1
SYSTEM_ERROR            =   -10

REG_OK                  =   0
REG_FAILED              =   1
REG_TIMEOUT             =   2
REG_REFUSED             =   3

REG_HOSTNAME_FAILED     =   4
REG_CONN_REFUSED        =   5

WS_HANDSHAKE_FAILED     =   6

TOOL_AGENT=0
TOOL_PROBE=1

class TestThread(threading.Thread):
    """
    Test Thread
    """
    def __init__(self, parent, testUuid, scriptId, adapterId, interval=40, shared=False):
        """
        """
        threading.Thread.__init__(self)
        self.parent = parent
        self.stopEvent = threading.Event()
        self.event = threading.Event()
        self.scriptId = scriptId
        self.testUuid = testUuid
        self.adapterId = adapterId
        self.shared = shared
        self.timestamp = time.time()
        
        self.__fifo_incoming_events_thread = FifoQueue.FifoCallbackThread()
        self.__fifo_incoming_events_thread.start()
        
        self.ctx_plugin = None
        self.interval = interval
    
    def ctx(self):
        """
        Return the context
        """
        return self.ctx_plugin
        
    def updateTimestamp(self):
        """
        Update the timestamp
        """
        self.timestamp = time.time()
        
    def run(self):
        """
        On run
        """
        while not self.stopEvent.isSet():
            if (time.time() - self.timestamp) > self.interval:
                self.parent.trace("timeout raised, no more keepalive received from test server" )
                break
            time.sleep(1)
        self.onTerminated(testUuid=self.testUuid, scriptId=self.scriptId, adapterId=self.adapterId)
    
    def putItem(self, item):
        """
        Add item in the queue
        """
        self.__fifo_incoming_events_thread.putItem(item)
        
    def stop(self):
        """
        Stop the thread
        """

        self.__fifo_incoming_events_thread.removeAll()
        
        self.__fifo_incoming_events_thread.stop()
        self.__fifo_incoming_events_thread.join()
        
        if self.ctx_plugin is not None:
            self.ctx_plugin.onReset()
            
        self.stopEvent.set()
        
    def onTerminated(self, testUuid, scriptId, adapterId):
        """
        On terminated event
        """
        pass
        
class Tool(NetLayerLib.ClientAgent):
    """
    Tool client agent
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                    supportProxy=False, proxyIp=None, proxyPort=None, sslSupport=True,
                    toolType = NetLayerLib.TYPE_AGENT_AGENT, fromCmd=False, name=None):
        """
        Constructor for tool

        @param version:
        @type version: string
        """
        self.__LAST_ERROR=None
        self.defaultTool = defaultTool
        self.login = "anonymous"
        self.password = "anonymous"
        self.toolType = toolType
        self.fromCmd = fromCmd
        
        # init ssl
        self.sslSupportFinal=sslSupport
        if not Settings.getBool( 'Server', 'ssl-support' ): self.sslSupportFinal=False 

        # init websocket
        wsSupport=False  
        if Settings.getBool( 'Server', 'websocket-support' ): wsSupport=True 

        NetLayerLib.ClientAgent.__init__(self, typeAgent = toolType, startAuto = True,
                                            keepAliveInterval=Settings.getInt( 'Network', 'keepalive-interval' ),
                                            inactivityTimeout=Settings.getInt( 'Network', 'inactivity-timeout' ),
                                            timeoutTcpConnect=Settings.getInt( 'Network', 'tcp-connect-timeout' ),
                                            responseTimeout=Settings.getInt( 'Network', 'response-timeout' ),
                                            selectTimeout=Settings.get( 'Network', 'select-timeout' ),
                                            sslSupport=self.sslSupportFinal,
                                            wsSupport=wsSupport,
                                            pickleVer=Settings.getInt( 'Network', 'pickle-version' ),
                                            tcpKeepAlive=Settings.getBool( 'Network', 'tcp-keepalive' ), 
                                            tcpKeepIdle=Settings.getInt( 'Network', 'tcp-keepidle' ),
                                            tcpKeepCnt=Settings.getInt( 'Network', 'tcp-keepcnt' ), 
                                            tcpKeepIntvl=Settings.getInt( 'Network', 'tcp-keepintvl' )
                                        )
        serverPort = Settings.getInt( 'Server', 'port' )
        if controllerPort is not None:
            serverPort = int(controllerPort)
        
        self.setServerAddress( ip = controllerIp, port = serverPort)
        if supportProxy:
            self.setProxyAddress(ip = proxyIp, port = int(proxyPort) )
        self.setAgentName( name = toolName )
        toolMore = {'details': toolDesc, 'default': defaultTool}
        if name is not None:
            self.setDetails( name = name, desc = toolMore, ver = Settings.getVersion() )
        else:
            self.setDetails( name = self.__class__.__name__, desc = toolMore, ver = Settings.getVersion() )
        
        self.controllerIp = controllerIp
        self.controllerPort = serverPort
        
        self.pathTraces = Settings.get( 'Paths', 'tmp' )
        self.toolName = toolName
        self.__mutex__ = threading.RLock()
        self.regThread = None
        self.__REGISTERED_BEFORE__=False
        self.regRequest =  None
        
        if sys.platform == "win32" :
            self.__tmpPath__ =  "%s\\%s\\[%s]_%s\\" % ( Settings.getDirExec(), self.pathTraces, 
                                                        toolType, self.toolName  )
        else:
            self.__tmpPath__ =  "%s/%s/[%s]_%s/" % ( Settings.getDirExec(), self.pathTraces, 
                                                     toolType, self.toolName  )
        self.__callId__ =  0
        self.__callIds__ = {}
        self.__args__ = []

        # new in v6.2
        self.testsContext = {}
    
    def getFromCmd(self):
        """
        Return the plugin is executed from command line
        """
        return self.fromCmd
        
    def setFromCmd(self):
        """
        Set to True when the plugin is executed from command line
        """
        self.fromCmd = True
        
    def getTemp(self):
        """
        Return the path of the temp area
        """
        return self.__tmpPath__
   
    def onScreenCaptured(self, filename, xml=''):
        """
        Function must be reimplement
        """
        pass
        
    def checkPrerequisites(self):
        """
        Function must be reimplement
        """
        pass
        
    def context(self):
        """
        Get the tests context
        """
        return self.testsContext
        
    def getLastError(self):
        """
        Return the last error
        """
        return self.__LAST_ERROR

    def getTimestamp(self):
        """
        Return timestamp
        """
        ret = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))  + ".%3.3d" % int((time.time() * 1000)% 1000  )
        return ret
        
    def onRequest(self, client, tid, request):
        """
        Reimplemented from ClientAgent

        @param client:
        @type client:

        @param tid:
        @type tid: integer

        @param request:
        @type request:
        """
        try:
            if request['cmd'] == Messages.RSQ_CMD:
            ############################################################
                _body_ = request['body']
                if 'cmd' in _body_:
                    self.trace( 'On request, receiving <-- CMD: %s' % _body_['cmd'] )
                    
                    if _body_['cmd'] == Messages.CMD_START_PROBE:
                        if _body_['opts']['args'] == '':
                            _body_['opts']['args'] = "{}"
                        _body_['opts']['args'] = eval(_body_['opts']['args'])
                        self.onInitialize( tid, _body_['opts'] )
                    
                    elif _body_['cmd'] == Messages.CMD_STOP_PROBE:
                        self.onStop( tid, _body_['opts'] )
                    
                    else:
                        self.error( 'Cmd unknown %s' % _body_['cmd'])
                        rsp = {'cmd': _body_['cmd'], 'res': Messages.CMD_ERROR }
                        NetLayerLib.ClientAgent.failed(self, tid, body = rsp )
                else:
                    self.error( 'Cmd is missing')
            ############################################################
            elif request['cmd'] == Messages.RSQ_NOTIFY:
                self.onNotify(client, tid, request=request['body'])
            else:
                self.error( '[onRequest] request unknown %s' % request['cmd'])
        except Exception as e:
            self.error( "[onRequest] %s" % str(e) )

    def onNotify(self, client, tid, request):
        """
        Called on incoming request from server

        @param client: server address ip/port
        @type client:  tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        if request['event'] == 'agent-notify':
            try:
                self.__onAgentNotify(client, tid, request)
            except Exception as e:
                self.error( "__onAgentNotify %s" % str(e) ) 
        elif request['event'] == 'agent-ready':
            try:
                self.__onAgentReady(client, tid, request)
            except Exception as e:
                self.error( "__onAgentReady %s" % str(e) ) 
        elif request['event'] == 'agent-init':
            try:
                self.__onAgentInit(client, tid, request)
            except Exception as e:
                self.error( "__onAgentInit %s" % str(e) ) 
        elif request['event'] == 'agent-reset':
            try:
                self.__onAgentReset(client, tid, request)
            except Exception as e:
                self.error( "__onAgentReset %s" % str(e) ) 
        elif request['event'] == 'agent-alive':
            try:
                self.__onAgentAlive(client, tid, request)
            except Exception as e:
                self.error( "__onAgentAlive %s" % str(e) ) 
        else:
            self.error( "unknown event request received: %s" % str(request['event']) )
        
    def __onAgentReady(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        self.trace("Init agent testUuid=%s ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                        request['script_id'], 
                                                                        request['source-adapter'])  )
        self.trace("Tests context before init: %s" % self.testsContext)
        test_ctx = TestThread(parent=self, testUuid=request['uuid'], 
                              scriptId=request['script_id'], 
                              adapterId=request['source-adapter'] )
        if 'shared' in request['data']: 
            test_ctx.shared = request['data']['shared']
        if request['uuid'] in self.testsContext:
            self.testsContext[request['uuid']][request['source-adapter']] = test_ctx
        else:
            self.testsContext[request['uuid']] = {request['source-adapter']: test_ctx }
        test_ctx.onTerminated = self.onResetTestContext
        test_ctx.start()

        self.sendNotify(request, data={ 'cmd': AGENT_INITIALIZED, 'ready': True } )                         
        self.trace("Agent initialized testUuid=%s ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                               request['script_id'], 
                                                                               request['source-adapter']) )
        
        self.onAgentReady(client, tid, request)
 
    def __onAgentNotify(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        self.onAgentNotify(client, tid, request)
 
    def __onAgentInit(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        self.onAgentInit(client, tid, request)

    def __onAgentReset(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        self.trace("Resetting agent testUuid=%s ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                             request['script_id'], 
                                                                             request['source-adapter']) )
        self.trace("Tests context before reset: %s" % self.testsContext)
        
        # workaround to support old plugins
        self.onOldAgentReset(client, tid, request)
        
        if request['uuid'] in self.testsContext:
            try:
                if request['source-adapter'] in self.testsContext[request['uuid']]:
                    test_ctx = self.testsContext[request['uuid']][request['source-adapter']]
                    if test_ctx.shared:
                        self.trace("Shared adapter detected, ignore reset")
                    else:   
                        test_ctx.stop()
                        test_ctx.join()
                        
                        test_ctx = self.testsContext[request['uuid']].pop(request['source-adapter'])
                        del test_ctx
                        if not len(self.testsContext[request['uuid']]):
                            test_ctx  = self.testsContext.pop(request['uuid'])
                            del test_ctx
                        self.trace("Agent resetted testUuid=%s ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                                            request['script_id'], 
                                                                                            request['source-adapter']) ) 
                        self.onAgentReset(client, tid, request)
                else:
                    self.trace("AdapterId=%s does not exists in test context" % request['source-adapter'] )
            except Exception as e:
                pass # not really nice to bypass exception here...
        else:
            self.trace("TestUuid=%s does not exists in test context" % request['uuid'] )

    def __onAgentAlive(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        self.trace("Updating keepalive testUuid=%s ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                                request['script_id'], 
                                                                                request['source-adapter']) )
        if request['uuid'] in self.testsContext:
            if request['source-adapter'] in self.testsContext[request['uuid']]:
                test_ctx = self.testsContext[request['uuid']][request['source-adapter']]
                test_ctx.updateTimestamp()
                self.trace("Agent alive testUuid=%s ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                                 request['script_id'], 
                                                                                 request['source-adapter']) )                 
                self.onAgentAlive(client, tid, request)
    
    def onAgentReady(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        pass
 
    def onAgentNotify(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        pass
 
    def onAgentInit(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        pass
        
    def onOldAgentReset(self, client, tid, request):
        """
        Function to reimplement on old plugin
        """
        pass
        
    def onAgentReset(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        pass
 
    def onAgentAlive(self, client, tid, request):
        """
        Function to reimplement on plugin
        """
        pass
        
    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        Function to reimplement on plugin
        """
        pass
        
    def userConfirm(self, msg):
        """
        Function to reimplement
        """
        pass
        
    def onUserConfirmed(self):
        """
        Function to reimplement
        """
        pass
        
    def onInitialize(self, tid, data):
        """
        Called on initialization
        """
        self.trace( 'Data received: %s'  % str(data) )
        try:
            ret = {}
            ret['callid'] = CALL_FAILED
            callId = self.prepareTmpDir()
            if callId is None:
                ret['callid'] = SYSTEM_ERROR
                self.startResponse( tid, ret )
            else:
                ret['callid'] = callId
                # check params
                params =  data['args']
                argsOk = True
                for a in self.__args__:
                    if not a in params:
                        argsOk = False
                if not argsOk:
                    ret['callid'] = ARGUMENTS_MISSING
                    self.startResponse( tid, ret )
                else:
                    self.onStart( callId, tid, data )
        except Exception as e:
            self.error( "Generic exception  %s" % str(e) )

    def onDisconnection(self, byServer=False, inactivityServer=False):
        """
        On disconnection
        """
        self.trace( "[onDisconnection] started by server=%s and inactivity from server=%s" % (byServer, inactivityServer) )
        NetLayerLib.ClientAgent.onDisconnection(self)
        self.onToolDisconnection(byServer=byServer, inactivityServer=inactivityServer)
        self.trace( "[onDisconnection] terminated" )
        
    def onToolDisconnection(self, byServer=False, inactivityServer=False):
        """
        On tool disconnection
        """
        self.info("Disconnnection")
    
    def onProxyConnectionSuccess(self):
        """
        On proxy connection success
        """
        self.info("Connection successful")
        if self.wsSupport:
            self.info("Do ws handshake")
            if self.getTypeClientAgent() ==  NetLayerLib.TYPE_AGENT_AGENT:
                wspath = Settings.get( 'Server', 'websocket-path' )
                if self.sslSupport:
                    wspath = Settings.get( 'Server', 'websocket-secure-path' )
            else:
                wspath = Settings.get( 'Server', 'websocket-path-probe' )
                if self.sslSupport:
                    wspath = Settings.get( 'Server', 'websocket-secure-path-probe' )
            self.handshakeWebSocket(resource=wspath, hostport=self.controllerIp)
        else:
            self.doRegistration()
            
    def onConnectionSuccessful(self):
        """
        On connection successful
        """
        self.info("Connection successful")
        if self.wsSupport:
            self.info("Do ws handshake")
            if self.getTypeClientAgent() ==  NetLayerLib.TYPE_AGENT_AGENT:
                wspath = Settings.get( 'Server', 'websocket-path' )
                if self.sslSupport:
                    wspath = Settings.get( 'Server', 'websocket-secure-path' )
            else:
                wspath = Settings.get( 'Server', 'websocket-path-probe' )
                if self.sslSupport:
                    wspath = Settings.get( 'Server', 'websocket-secure-path-probe' )
            self.handshakeWebSocket(resource=wspath, hostport=self.controllerIp)
        else:
            self.doRegistration()

    def onWsHanshakeSuccess(self):
        """
        On websocket hanshake success
        """
        self.regRequest = threading.Event()
        self.info("Handshake OK")
        self.regThread = threading.Thread(target=self.doRegistration, args=(self.regRequest,))
        self.regThread.start()

    def onRegistrationSuccessful(self):
        """
        On registration successful
        """
        self.info("Registration successful")
        self.__REGISTERED_BEFORE__=True
        self.prepareTempDir()

    def initAfterRegistration(self):
        """
        Init after the registration
        Can be reimplement
        """
        pass
        
    def onRegistrationRefused(self, err):
        """
        On registration refused
        """
        self.error( err )
        self.__LAST_ERROR = REG_REFUSED     

    def onRegistrationFailed(self, err):
        """
        On registration failed
        """
        self.error( err )
        self.__LAST_ERROR = REG_FAILED      

    def onWsHanshakeError(self, err):
        """
        On websocket hanshake error
        """
        self.error( err )
        self.__LAST_ERROR = WS_HANDSHAKE_FAILED    

    def onConnectionRefused(self, err):
        """
        On connection refused
        Function to reimplement

        @param err:
        @type err:
        """
        self.error( '[onConnectionRefused]' )
        if self.getLastError() is None:
            self.__LAST_ERROR = REG_CONN_REFUSED    

    def onResolveHostnameFailed(self, err):
        """
        On resolve hostname failed
        Function to reimplement

        @param err:
        @type err:
        """
        self.error( "[onResolveHostnameFailed]" )
        if self.getLastError() is None:
            self.LAST_ERROR = REG_HOSTNAME_FAILED   

    def onConnectionTimeout(self, err):
        """
        On connection timeout
        Function to reimplement

        @param err:
        @type err:
        """
        self.error( "[onConnectionTimeout]" )
        if self.getLastError() is None:
            self.__LAST_ERROR = REG_TIMEOUT 

    def onPreCleanup(self):
        """
        Called on program stop
        """
        self.trace("pre cleanup called")
        try:
            # reset all tests
            self.trace("Tests context before cleanup: %s" % self.testsContext)
            for scriptId, s  in self.testsContext.items():
                for adapterId, a in s.items():
                    try:
                        if a.ctx() is not None:
                            a.ctx().stop()
                            a.ctx().join()
                    except Exception as e:
                        pass
                    a.stop()
                    a.join()
        except Exception as e:
            pass
        self.trace("Tests context after cleanup: %s" % self.testsContext)    
        self.onCleanup()
        
    def cleanupTestContext(self, testUuid, scriptId, adapterId):
        """
        Try to clean up the test context in all
        """
        self.trace("cleanup test context called")        
        # remove the adapter thead from the test context
        self.trace('removing adapterId=%s thread from test context' % adapterId)
        try:
            adapterThread = self.context()[testUuid].pop(adapterId)
        except Exception as e:
            pass # by pass exception, sometime adapterID is already removed from the context
            
        try:
            adapterThread.stop()
            adapterThread.join()
        except Exception as e:
            pass # by pass exception and ignore errors
        del adapterThread
        
        # current test uuid is empty ?
        if not len(self.context()[testUuid]):
            self.trace('removing testUuid=%s from test context' % testUuid)
            try:
                test = self.context().pop(testUuid)
                del test
            except Exception as e:
                pass # by pass exception, sometime testUuid is already removed from the context
                
        self.trace("Tests context: %s" % self.testsContext)
        
    def onCleanup(self):
        """
        Called on program stop
        """
        pass
        
    def sendError(self, request, data):
        """
        Send error to the server with a notify

        @param request: request received from the server
        @type request: dict

        @param data: data to send
        @type data: dict/string
        """
        self.error( "send error: %s"  % str(data) )
        req =  request
        req['event'] = "agent-error"
        req['data'] = data
        self.notify( data=req )

    def sendNotify(self, request, data):
        """
        Send notify to the server

        @param request: request received from the server
        @type request: dict

        @param data: data to send
        @type data: dict/string
        """
        self.trace( "send notify: %s"  % len(data) )
        req =  request
        req['event'] = "agent-notify"
        req['data'] = data
        self.notify( data=req )

    def sendData(self, request, data):
        """
        Send notify to the server

        @param request: request received from the server
        @type request: dict

        @param data: data to send
        @type data: dict/string
        """
        self.trace( "send notify: %s"  % len(data) )
        req =  request
        req['event'] = "agent-data"
        req['data'] = data
        self.notify( data=req )

    def info (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        if sys.version_info[0] < 3:
            if not isinstance(txt, unicode):
                txt =  unicode(txt, 'latin2')
        Logger.info( "[%s] %s" % (self.__class__.__name__, txt ) )

    def trace (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        if sys.version_info[0] < 3:
            if not isinstance(txt, unicode):
                txt =  unicode(txt, 'latin2')
        Logger.debug( "[%s] %s" % (self.__class__.__name__, txt ) )

    def error (self, err):
        """
        Log error

        @param err:
        @type err:
        """
        if sys.version_info[0] < 3:
            if not isinstance(err, unicode):
                err =  unicode(err, 'latin2')
        Logger.error( "[%s] %s" % ( self.__class__.__name__, err ) )

    def prepareTmpDir(self):
        """
        Prepare the temp folder
        """
        callId = self.getCallId()
        dirCreated = self.addCallIdTmpDir( dirName=callId )
        if not dirCreated:
            return None
        else:
            return callId

    def getCallId (self):
        """
        Return the call id

        @return:
        @rtype:
        """
        self.__mutex__.acquire()
        self.__callId__ += 1
        self.__mutex__.release()
        return self.__callId__

    def addTmpDir(self):
        """
        Add temp folder 
        """
        ret = False
        try:
            if os.path.exists( self.__tmpPath__ ): self.delTmpDir()
            self.trace( "Adding the temp folder %s" % self.__tmpPath__ )   
            os.mkdir( self.__tmpPath__ )
            ret = True
            self.trace( "Temp folder added with success" )
        except Exception as e:
            self.error( "Unable to add the temp folder %s" % str(e) )
        return ret

    def delTmpDir(self):
        """
        Delete temp folder
        """
        try:
            self.trace( "Deleting the temp folder %s" % self.__tmpPath__ )
            shutil.rmtree( self.__tmpPath__ )
            self.trace( "Temp folder deleted with success" )
        except Exception as e:
            self.error( "Unable to delete the temp folder %s" % str(e) )

    def addCallIdTmpDir(self, dirName):
        """
        Add callid folder in temp
        """
        ret = False
        try:
            if sys.platform == "win32" :
                completepath = "%s\\%s" % ( self.__tmpPath__ , dirName )
            else:
                completepath = "%s/%s" % ( self.__tmpPath__ , dirName )
            if os.path.exists( completepath ):
                self.delCallIdTmpDir(dirName=dirName)   
            self.trace( "Adding callid folder %s in temp" % dirName )
            os.mkdir( completepath )
            ret = True
            self.trace( "CallID folder %s created with success" % dirName )
        except Exception as e:
            self.error( "Unable to add the callid folder in temp %s" % str(e) )
        return ret

    def delCallIdTmpDir(self, dirName):
        """
        Delete callid folder from temp
        """
        try:
            if sys.platform == "win32" :
                completepath = "%s\\%s" % ( self.__tmpPath__ , dirName  )
            else:
                completepath = "%s/%s" % ( self.__tmpPath__ , dirName  )
            self.trace( "Deleting folder %s in temp" % completepath )
            shutil.rmtree( completepath )
            self.trace( "CallId folder %s deleted with success" % dirName )
        except Exception as e:
            self.error( "Unable to delete the call id folder in %s" % str(e) )

    def prepareTempDir(self):
        """
        Prepare temp folder
        """
        # create temp directory
        dirCreated = self.addTmpDir()
        if not dirCreated:
            self.error( 'Unable to create the temp folder' )
            self.stopCA()
        else:
            self.trace( 'Temp folder OK, the probe is ready' )
            self.__REGISTERED_BEFORE__=True
            
    def onStart (self, callid, tid, data):
        """
        Called on start

        @param tid:
        @type tid:

        @param args:
        @type args:
        """
        pass

    def onStop (self, tid, data):
        """
        Called on stop

        @param tid:
        @type tid:

        @param args:
        @type args:
        """
        pass

    def requestNotify (self, resultPath, fileName):
        """
        Send a notify

        @param body:
        @type body:

        @param body:
        @type body:
        """
        self.info( 'Notify the server'  )
        try:
            tpl =  { 'cmd': Messages.CMD_NEW_FILE, 'result-path': resultPath, 'filename': fileName } 
            NetLayerLib.ClientAgent.notify( self, data = tpl )
        except Exception as e:
            self.error( "unable to send notify: %s"  % str(e) )
            
    def startResponse (self, tid, body = None):
        """
        Send ok reponse

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        NetLayerLib.ClientAgent.ok(self, tid, body)

    def stopResponse(self, tid, body = None, additional = None, dataToSend=True):
        """
        Stop response
        """
        NetLayerLib.ClientAgent.ok(self, tid, body)
        if dataToSend:
            ret, pathZip, fileName = self.createZip( callId=additional['callid'], 
                                                     zipReplayId=additional['replay-id'])
            if not ret:
                self.trace( 'Unable to create zip'  )
            else:
                self.uploadData(fileName=fileName, 
                                resultPath=additional['result-path'], 
                                data=None, 
                                filePath=pathZip, 
                                callId=additional['callid'])
        
    def createZip(self, callId, zipReplayId, zipPrefix="probe"):
        """
        Create zip
        """
        if sys.platform == "win32" :
            completepath = "%s\\%s" % ( self.__tmpPath__ , callId )
        else:
            completepath = "%s/%s" % ( self.__tmpPath__ , callId )
        fileName = '%s_%s_%s_%s_%s_%s' % ( zipPrefix, self.__type__, self.toolName, 
                                            callId , self.getTimestamp(), zipReplayId)
        
        self.trace( 'Starting to create the zip file %s ' % fileName )
        if sys.platform == "win32" :
            ret = self.toZip(   file=completepath,
                                filename= '%s\\%s.zip' % (completepath, fileName) , 
                                fileToExclude = [ '%s.zip' % fileName ] )
            return ( ret, '%s\\%s.zip' % (completepath, fileName), '%s.zip' % fileName )
        else:
            ret = self.toZip(   file=completepath,
                                filename= '%s/%s.zip' % (completepath, fileName) , 
                                fileToExclude = [ '%s.zip' % fileName ] )
            return ( ret, '%s/%s.zip' % (completepath, fileName), '%s.zip' % fileName )

    def toZip(self, file, filename, fileToExclude):
        """
        Add file to zip
        """
        self.trace( 'Zip to %s' % file )
        ret = False
        try:
            zip_file = zipfile.ZipFile(filename, 'w')
            if os.path.isfile(file):
                zip_file.write(file)
            else:
                self.addFolderToZip(zip_file, file, fileToExclude)
            zip_file.close()
            ret = True
        except IOError as e:
            self.error( "Io error  %s " % str(e) )
        except Exception as e:
            self.error( "General exception %s" % str(e) )
        return ret

    def addFolderToZip(self, zip_file, folder, fileToExclude=[]): 
        """
        Add folder to zip
        """
        try:
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                if os.path.isfile(full_path):
                    excludeFile = False
                    for f in fileToExclude:
                        if file == f:
                            excludeFile = True
                    if not excludeFile:
                        zip_file.write(filename=full_path, arcname=file)
                elif os.path.isdir(full_path):
                    self.addFolderToZip(zip_file, full_path, fileToExclude)
        except IOError as e:
            raise IOError(e)
        except Exception as e:
            raise Exception( "addFolderToZip - %s" % str(e) )

    def uploadData(self, fileName, resultPath, data=None, filePath=None, callId=None):
        """
        Send data
        """
        self.trace("Upload binary data")
                      
        if data is not None:
            fileContent = base64.b64encode(data)
            
        if filePath is not None:
            fd = open(filePath, 'rb')
            fileContent = base64.b64encode(fd.read())
            fd.close()

        t = threading.Thread(target=self.__callRest, args=(resultPath, fileName, 
                                                           fileContent, callId)  )
        t.start()
        
    def onUploadError(self, callId=None):
        """
        On upload error
        """
        self.upload('upload error, cleanup temp folder')
        if callId is not None:
            self.delCallIdTmpDir(callId)
        
    def onUploadTerminated(self, resultPath, fileName, callId=None):
        """
        On upload terminated
        """
        if callId is not None:
            # remove temp folder
            self.delCallIdTmpDir(callId)
    
    def onTakeScreenshot(self, request, action, actionId, adapterId, testcaseName, replayId):
        """
        On take screenshot
        """
        pass
 
    def __callRest(self, resultPath, fileName, fileContent, callId=None):
        """
        Rest call
        """
        # set proxy is activated
        proxyDict = {}
        if eval( Settings.get( 'Server', 'proxy-active' ) ):
            proxyAddr = Settings.get( 'Server', 'addr-proxy-http' )
            proxyPort = Settings.get( 'Server', 'port-proxy-http' )
            self.trace("Proxy activated for rest Ip=%s Port=%s" % (proxyAddr, proxyPort) )
            
            https_proxy = "https://%s:%s" % (proxyAddr, proxyPort)
            proxyDict = { "https" : https_proxy}
            
        req = '{"result-path": "%s", "file-name": "%s", "file-content": "%s"}' % ( resultPath,
                                                                                   fileName,
                                                                                   fileContent.decode("utf8") )
        r = requests.post("https://%s:%s/rest/results/upload/file" % (self.controllerIp, self.controllerPort),
                            headers = {'Content-Type': 'application/json;charset=utf-8'},
                            data = req.encode("utf8"),
                            proxies=proxyDict, verify=False)
        if r.status_code != 200:
            self.error('Unable to reach the rest api: %s - %s' % (r.status_code, r.text) )
            self.onUploadError(callId=callId)
        else:
            self.onUploadTerminated(resultPath=resultPath, 
                                    fileName=fileName,
                                    callId=callId)