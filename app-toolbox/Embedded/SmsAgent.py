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
Sms agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import sys
import threading
import time

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    import httplib as httpclient
except ImportError: # support python3
    import http.client as httpclient

try:
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
except ImportError: # support python3
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
import urllib

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = ""
__TYPE__="""gateway-sms"""
__RESUME__="""Sms gateway through real device."""
__DESCRIPTION__="""Sms gateway through real device.
This agent enables to receive or send sms from or to the test server.

Targetted operating system: Windows, Linux"""

SG = None # Singleton

def initialize (controllerIp, controllerPort, toolName, toolDesc, 
                defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    global SG
    SG = SmsGateway( controllerIp, controllerPort, toolName, toolDesc, 
                       defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    return SG
    
def instance ():
    """
    Returns Singleton
    """
    return SG

    
class GetHandler(BaseHTTPRequestHandler):
    """
    GET request handler
    """
    def do_GET(self):
        """
        On GET request
        """
        phone = self.path.split("?phone=")[1].split("&smscenter=")[0]
        msg = self.path.split("&text=")[1]
        
        instance().addSms(msg, phone)
        
        self.send_response(200)
        self.end_headers()
        return
        
class SmsGateway(GenericTool.Tool):
    """
    SMS gateway agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=0, 
                        proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Dummy agent

        @param controllerIp: controller ip/host
        @type controllerIp: string

        @param controllerPort: controller port
        @type controllerPort: integer

        @param toolName: agent name
        @type toolName: string

        @param toolDesc: agent description
        @type toolDesc: string

        @param defaultTool: True if the agent is started by the server, False otherwise
        @type defaultTool: boolean
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, 
                                defaultTool, supportProxy=supportProxy, proxyIp=proxyIp, 
                                proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__

        self.mailboxSms = []
        self.httpThread = threading.Thread(target = self.startHttpServer )
        self.httpThread.start()
          
    def addSms(self, msg, phone):
        """
        Add SMS received to the mailbox
        """
        self.trace("adding texto to the mailbox")
        if sys.version_info > (3,):
           __phone = urllib.parse.unquote_plus(phone) 
           __msg = urllib.parse.unquote_plus(msg) 
        else:
            __phone = urllib.unquote_plus(phone) 
            __msg = urllib.unquote_plus(msg) 
        self.mailboxSms.append( (time.time(), __msg, __phone) )
        
    def startHttpServer(self):
        """
        Start the http server
        """
        self.HTTP_SVR = HTTPServer(('0.0.0.0', 80), GetHandler)
        self.HTTP_SVR.serve_forever()
        
    def getType(self):
        """
        Returns agent type

        @return: agent type
        @rtype: string
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
        In this function, you can stop your program
        """
        self.HTTP_SVR.shutdown()
        self.httpThread.join()
        
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        self.onToolLogWarningCalled("Starting SMS gateway agent")
        self.onToolLogWarningCalled("SMS gateway started")

        self.onToolLogSuccessCalled( "Configure the SMS gateway application on your device mobile!")
        self.onPluginStarted()
        
    def pluginStarting(self):
        """
        Function to reimplement
        """
        pass
        
    def onPluginStarted(self):
        """
        Function to reimplement
        """
        pass

    def pluginStopped(self):
        """
        Function to reimplement
        """
        pass

    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass
        
    def onToolLogWarningCalled(self, msg):
        """
        Logs warning on main application

        @param msg: warning message
        @type msg: string
        """
        pass

    def onToolLogErrorCalled(self, msg):
        """
        Logs error on main application

        @param msg: error message
        @type msg: string
        """
        pass

    def onToolLogSuccessCalled(self, msg):
        """
        Logs success on main application

        @param msg: error message
        @type msg: string
        """
        pass
    
    def onAgentAlive(self, client, tid, request):
        """
        Called on keepalive received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass
        
    def onAgentInit(self, client, tid, request):
        """
        Called on init received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass

    def onAgentReset(self, client, tid, request):
        """
        Called on reset received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}
        or 
        {'event': 'agent-reset', 'source-adapter': '1', 'script_id': '7_3_0'}
        
        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass
            
    def execAction(self, request):
        """
        Exec action
        """
        reqData = request['data']
        
        try:
            if reqData['action'] == 'SEND SMS':
                self.onToolLogWarningCalled( "<< Action=%s Id=%s to the mobile gateway ip=%s port=%s" % (reqData['action'], 
                                                                                                         reqData['action-id'],
                                                                                                         reqData['gw-ip'], 
                                                                                                         reqData['gw-port']) )
                
                # http://xxxx:9090/sendsms?phone=xxx&text=fdsfds&password=qdsds
                conn = httpclient.HTTPConnection(reqData['gw-ip'], reqData['gw-port'])
                
                uri_dict = {'phone': reqData['phone'], 'text': reqData['msg'], 'password': ''}
                if sys.version_info > (3,):
                    uri = "/sendsms?%s" % urllib.parse.urlencode(uri_dict)
                else:
                    uri = "/sendsms?%s" % urllib.urlencode(uri_dict)
                    
                self.trace("uri: %s" % uri)
                conn.request("GET", uri, "", headers={})
                response = conn.getresponse()
                data = response.read()
                self.trace("response received: %s" % data)
                if b'SENT' not in data:
                    self.trace( 'send sms failed' )
                    self.sendNotify(request=request, data={'action': reqData['action'], 
                                                            'action-id': reqData['action-id'], 
                                                            'result': 'FAILED'} )
                else:
                    self.trace( 'action ok' )
                    self.sendNotify(request=request, data={'action': reqData['action'], 
                                                            'action-id': reqData['action-id'], 
                                                            'result': 'OK'} )
                
                self.onToolLogWarningCalled( "<< SMS sent" )
                
            elif reqData['action'] == 'READ MAILBOX':
                self.trace( 'read the mailbox' )
                while len(self.mailboxSms):
                    texto = self.mailboxSms.pop()
                    self.sendNotify(request=request, data={'action': reqData['action'], 'result': texto} )

            else:
                raise Exception('unknown action received: %s' % reqData['action'])
        except Exception as e:
            self.error('unable to send sms: %s' % e)
            self.sendError(request=request, data='unable to send sms: %s' % e)
            
    def onAgentNotify(self, client, tid, request):
        """
        Called on notify received from test server and dispatch it
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        try:
            thread = threading.Thread(target = self.execAction, args = (request,) )
            thread.start()
            thread.join()   
        except Exception as e:
            self.error( e )