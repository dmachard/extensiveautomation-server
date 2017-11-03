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
Command agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import sys
import shlex
import subprocess
import threading
import os
import signal
import shutil
import re
try:
    import StringIO
except ImportError: # support python 3
    import io as StringIO
import time


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = ""
__TYPE__="""command"""
__RESUME__="""This agent enables to execute system commands. 
Be careful: interact command are not supported!
Can be used on Linux or Windows (command prompt)."""

__DESCRIPTION__="""This agent enables to execute system commands.
Can be used on Linux or Windows (command prompt).

Events messages:
    Agent->Server
        * Error( msg )
        * Data( ... ) - not used
        * Notify( result, get )

    Server->Agent
        * Init( ... ) - not used
        * Notify( cmd )
        * Reset( ... ) - not used

Targetted operating system: Windows and Linux"""

class CommandThread(threading.Thread):
    """
    Command thread object
    """
    def __init__(self, parent):
        """
        Individual command thread
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.parent = parent
        self.commandProcess = None
        self.isStarted = False
        self.isCancelled = False

    def error(self, msg):
        """
        Log error
        """
        self.parent.error( msg )
        
    def trace(self, msg):
        """
        Log a trace
        """
        self.parent.trace( msg )
        
    def readData(self, maxTimeout=50.0, prompt=b'[FAKEPROMPT]', searchPrompt=True):
        """
        Read data from the process
        """
        timeout = False
        startTime = time.time()
        outputs = []
        
        if self.isCancelled: return ( False, outputs )
        
        while (not timeout or not self.isCancelled):
            time.sleep(0.1)
            
            if (time.time() - startTime) >= maxTimeout:
                self.error( 'timeout raised' )
                timeout = True
                break

            line = self.commandProcess.stdout.readline()
            self.trace( line )
            if line: outputs.append( line )

            if searchPrompt:
                if line.startswith(prompt): break
            else:
                if prompt in line: break
                
        if timeout:
            return ( False, outputs )
        else:
            return ( True, outputs )
            
    def sendPrompt(self):
        """
        Simulate a prompt
        """
        self.commandProcess.stdin.write(b'echo [FAKEPROMPT]\n')
    
    def sendData(self, data, maxTimeout=50.0):
        """
        Send data to the process
        """
        cmd = '%s & echo [FAKEPROMPT]\n' % data
        if sys.version_info > (3,):
            self.commandProcess.stdin.write( bytes(cmd, "utf8") )
        else:
            self.commandProcess.stdin.write(cmd)
        ret, lines = self.readData(searchPrompt=True, maxTimeout=maxTimeout)
        if ret:
            joined = b''.join(lines)
            finalVal = joined.split(b'[FAKEPROMPT]')[1]
            return finalVal
        else:
            return '[error]'
            
    def run(self):
        """
        On run function
        """
        __cmd__ = r'C:\Windows\System32\cmd.exe'
        try:
            self.commandProcess = subprocess.Popen(__cmd__, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                    stderr=subprocess.STDOUT, bufsize=0 )
            pid = self.commandProcess.pid
            self.parent.trace("command thread started Pid=%s" % pid)
            
            ret, lines = self.readData(prompt=b'Microsoft Corporation.', searchPrompt=False)
            if ret:
                self.sendPrompt()
                ret, lines = self.readData(searchPrompt=True)
                if ret:
                    self.parent.onToolLogWarningCalled("Command started")
                    self.parent.onPluginStarted()
                    self.isStarted = True   
                else:
                    self.parent.onToolLogErrorCalled("Unable to start Command")                         
            else:
                self.parent.onToolLogErrorCalled("Unable to start Command")
        except Exception as e:
            self.parent.onToolLogErrorCalled("Unable to start Command")
            self.parent.error( "unable to start interactive Command: %s" % str(e))  
            self.parent.onResetAgentCalled()

    def stop(self):
        """
        Stop the thread
        """
        try:
            self.parent.onToolLogWarningCalled("Stopping command...")
            
            self.parent.trace('killing process with pid %s' % self.commandProcess.pid)
            kill = subprocess.Popen( 
                                        r'taskkill /PID %s /F /T' % self.commandProcess.pid, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.STDOUT,
                                        shell=True
                                    )
            kill.communicate()
            kill.terminate()
            kill.wait()
            self.parent.onToolLogWarningCalled("Command stopped")
        except Exception as e:
            self.parent.error( "unable to stop interactive Command: %s" % str(e))  

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Command( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    
class Command(GenericTool.Tool):
    """
    Command agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Command agent constructor
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__
        self.__mutex__ = threading.RLock()
        if sys.platform not in [ "win32", "linux2" ] :
            raise Exception( 'System %s not supported'   % sys.platform  )          

        self.commandThread = None
    
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        if sys.platform == "win32" :
            if self.commandThread is not None:
                self.trace("command already started")
                self.onPluginStarted()
            else:
                self.onToolLogWarningCalled("Starting command")
                self.commandThread = CommandThread(parent=self)
                self.commandThread.start()

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
        
    def getType(self):
        """
        Return agent type
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
        """
        if self.commandThread is not None:
            self.commandThread.isCancelled = True

        try:
            if self.commandThread is not None:
                self.commandThread.stop()
                self.commandThread.join()
        except Exception as e:
            self.error( "unable to cleanup: %s"  % e )

    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass
        
    def onToolLogWarningCalled(self, msg):
        """
        Function to reimplement
        """
        pass
    
    def onToolLogErrorCalled(self, msg):
        """
        Function to reimplement
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
        Initialize a new socket the agent 
        """
        pass

    def onAgentReset(self, client, tid, request):
        """
        Reset the socket 
        """
        pass

    def execAction(self, request):
        """
        Execute action
        """
        self.onToolLogWarningCalled( "<< Command called"  )
        if not isinstance( request['data'], dict ):
            self.error( 'bad data type: %s' % type(request['data']) )
            
        # windows support
        if sys.platform == "win32" :
            self.trace("command to run: %s" % request['data']['cmd'])
            if 'timeout' in request['data']:
                output = self.commandThread.sendData(data=request['data']['cmd'], 
                                                    maxTimeout=request['data']['timeout'])
            else:
                output = self.commandThread.sendData(data=request['data']['cmd'])
            self.sendNotify(request, data={'result':output, 'get': request['data']['get'] })
        
        # linux support
        if sys.platform == "linux2":
            try:
                # exception to find the system on linux platform
                if request['data']['get'] == 'Os':
                    PATH = '/etc/'
                    releaseFile = [ f for f in os.listdir(PATH) if os.path.isfile(os.path.join(PATH,f)) and f.endswith('-release') ]
                    # 2014-05-13 07:07:39,366 - ERROR - [Command] ['/etc/redhat-release', '/etc/java/jpackage-release']
                    if len(releaseFile) > 1 or len(releaseFile) == 0:
                        ret = [ 'Unknown system' ]
                    else:
                        f = open( "%s/%s" % (PATH,releaseFile[0]) )
                        ret = [ f.read() ]
                        f.close() 
                else:
                    __cmd = request['data']['cmd']
                    __cmd_args = shlex.split(__cmd)
                    p = subprocess.Popen(__cmd_args, shell=False, stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
                    out, err = p.communicate()
                    self.trace( str(out) )
                    self.trace( str(err) )

                    ret = []
                    if out is not None:
                        ret.append(out)
                    if err is not None:
                        ret.append(err)

                    self.error( str(ret) )
                self.sendNotify(request, data={'result': '\n'.join(ret), 'get': request['data']['get'] })
            except Exception as e:
                self.error( 'unable to run command: %s' % str(e) )
                self.sendError(request, data="unable to run command")

        self.onToolLogWarningCalled( "<< Command terminated")

    def onAgentNotify(self, client, tid, request):
        """
        Received a notify from server and dispatch it to the good socket
        """
        self.__mutex__.acquire()
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                a = self.context()[request['uuid']][request['source-adapter']]
                a.putItem( lambda: self.execAction(request) )
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()