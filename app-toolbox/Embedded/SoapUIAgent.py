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
SoapUI agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import os
import sys
import threading
import subprocess


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = True  
__APP_PATH__ = '%s\%s\%s' % (Settings.getDirExec(), Settings.get('Paths', 'bin'), Settings.get('BinWin', 'soapui-ide') )
__TYPE__="""soapui"""
__RESUME__="""This agent enables to execute SoapUI test file.
Can be used on Linux or Windows."""
__DESCRIPTION__="""This agent enables to execute SoapUI test file.
Can be used on Linux or Windows.

Events messages:
    Agent->Server
        * Error( msg )
        * Data( ... ) - not used
        * Notify( content, cmd, file )

    Server->Agent
        * Init( ... ) - not used
        * Notify( cmd, path )
        * Reset( ... ) - not used

Targetted operating system: Windows and Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return SoapUI( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    

class SoapUI(GenericTool.Tool):
    """
    SoapUI agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                    supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        File agent

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
        
        self.thread_actions = []

        self.detectSoapUI()

    def detectSoapUI(self):
        """
        Detect soapui
        """
        testrunnerBin = None
        
        if sys.platform == "win32":
            testrunnerBin = Settings.get('BinWin', 'soapui-testrunner')
        if sys.platform == "linux2":
            testrunnerBin = Settings.get('BinLinux', 'soapui-testrunner')
            
        if testrunnerBin is not None:
            if not os.path.isfile( testrunnerBin ):
                raise Exception('soap ui is not installed')
            
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
        for th in self.thread_actions:
            th.join()
        while len(self.thread_actions):
            try:
                t = self.thread_actions.pop()
                del t
            except Exception as e:
                pass
                
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        for th in self.thread_actions:
            th.join()
        while len(self.thread_actions):
            try:
                t = self.thread_actions.pop()
                del t
            except Exception as e:
                pass
            
        self.onToolLogWarningCalled("Starting SoapUI agent")
        self.onToolLogWarningCalled("SoapUI agent started")
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
        Execute action
        """
        try:
            projectPath = request['data']['project-path']
            projectFile = request['data']['project-file']
            testsuiteName = request['data']['testsuite-name']
            testcaseName = request['data']['testcase-name']
            soapuiOptions = request['data']['options']
        except Exception as e:
            self.error('unable to read request: %s' % e )
        else:   
            self.onToolLogWarningCalled( "<< Run test [%s->%s]" % (testsuiteName,testcaseName) )

            if sys.platform == "win32":
                testrunnerBin = Settings.get('BinWin', 'soapui-testrunner')
                testRunnerCmd = '"%s" %s -s "%s" -c "%s" "%s\%s"' % (   testrunnerBin, 
                                                                        " ".join(soapuiOptions), 
                                                                        testsuiteName, 
                                                                        testcaseName, 
                                                                        projectPath, 
                                                                        projectFile)
            elif sys.platform == "linux2":
                testrunnerBin = '%s' % Settings.get('BinLinux', 'soapui-testrunner')
                testRunnerCmd = '"%s" %s -s "%s" -c "%s" "%s/%s"' % (   testrunnerBin, 
                                                                        " ".join(soapuiOptions), 
                                                                        testsuiteName, 
                                                                        testcaseName, 
                                                                        projectPath, 
                                                                        projectFile)
            else:
                self.error( 'Platform not yet supported: %s' % sys.platform )

            try:
                self.trace("cmd: %s" % testRunnerCmd)
                proc = subprocess.Popen(testRunnerCmd, shell=True, bufsize=0, 
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            except Exception as e:
                self.error('unable to lauch testrunner: %s' % e )
            else:
                try:    
                    while True:
                        line = proc.stdout.readline()
                        if not line:
                            break
                        self.trace("testrunner: %s" % line)    
                        self.sendNotify(request=request, data={ 'msg': line }  )   
                except Exception as e:
                    self.error('unable to run testrunner: %s' % e )
            self.onToolLogWarningCalled( "<< Run terminated"  )

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
        self.__mutex__.acquire()
        try:
            thread = threading.Thread(target = self.execAction, args = (request,) )
            thread.start()
            self.thread_actions.append(thread)
        except Exception as e:
            self.error( e )
        self.__mutex__.release()
