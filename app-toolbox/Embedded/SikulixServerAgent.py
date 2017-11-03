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
Sikuli agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import sys
import threading
import subprocess
import time
import os
import socket
import shutil

# import urllib to use it with device
try:
    import urllib2 as requestlib
except ImportError: # support python 3
    from urllib import request as requestlib
    
# disable system proxy for urllib, use only in localhost
proxy_handler = requestlib.ProxyHandler({})
opener = requestlib.build_opener(proxy_handler)
requestlib.install_opener(opener)


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = True
  
__APP_PATH__ = '%s\%s\%s' % (Settings.getDirExec(), Settings.get('Paths', 'bin'), Settings.get('BinWin', 'sikuli') )
if sys.platform == "linux2": __APP_PATH__ = Settings.get('BinLinux', 'sikulix')

__TYPE__="""sikulix-server"""
__RESUME__="""Just a dummy agent. Use only for development.
Can be used on Linux or Windows."""

__DESCRIPTION__="""Example, just a dummy agent.
This agent enables to receive or send data from or to the test server.

Events messages:
    Agent->Server
        * Error(data)
        * Notify(data)
        * Data(data)

    Server->Agent
        * Init(data)
        * Notify(data)
        * Reset(data)

The data argument can contains anything, but a dictionary is prefered.

Targetted operating system: Windows, Linux"""

CODE_OK = 0
CODE_ERROR = 1
CODE_GET = 2

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return SikulixServer( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    

class SikulixServer(GenericTool.Tool):
    """
    Sikulix Server agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=0,
                        proxyIp=None, proxyPort=None, sslSupport=True, sikulixIp="127.0.0.1", sikulixPort=50001):
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
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                                    supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__
        self.__mutex__ = threading.RLock()
        
        if sys.platform == "win32" :
            self.binJava = Settings.get( 'BinWin', 'java' )
        elif sys.platform == "linux2":
            if not os.path.exists( Settings.get( 'BinLinux', 'java' ) ):
                raise Exception('java is not installed')
            if not os.path.exists( Settings.get( 'BinLinux', 'sikulix' ) ):
                raise Exception('sikulix is not installed')
        else:
            raise Exception( 'System %s not supported'   % sys.platform  )    
            
        self.sikulixIp = sikulixIp
        self.sikulixPort = sikulixPort
        self.sikulixProcess = None
        
        
        # get the home folder of the user
        if sys.platform == "win32" :
            homepath = os.path.expanduser(os.getenv('USERPROFILE'))
        elif sys.platform == "linux2":
            homepath = os.getenv('HOME')
        
        self.nameFolder= Settings.get('Common', 'acronym-server').lower()
        self.homeFolder = "%s\\%s" % (homepath, self.nameFolder)
        
        self.urlHost = "http://%s:%s" % (self.sikulixIp, self.sikulixPort)
                
    def checkPrerequisites(self):
        """
        Check prerequisites
        """
        # Adding limitation
        # Blocking the run of several sikulix server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        result = sock.connect_ex( (self.sikulixIp, self.sikulixPort))
        if result == 0:
            self.onToolLogErrorCalled("Sikulix Server already started in another instance!")
            raise Exception("Sikulix Server already started in another instance!")
        
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
        self.stopProcess()

    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        if self.sikulixProcess is not None:
            self.trace("Sikulix Server already started")
            self.onPluginStarted()
        else:
            self.startProcess()

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
    
    def stopProcess(self):
        """
        Stop the process
        """
        self.onToolLogWarningCalled("Stopping Sikulix Server...")
        try:
            thread = threading.Thread(target = self.__stopProcess )
            thread.start()
            thread.join()   
        except Exception as e:
            self.error( "unable to make a thread to stop process: %s" % e )
        
    def __stopProcess(self):
        """
        Internal function to stop the process
        """
        if self.sikulixProcess is not None:
            self.trace('killing process with pid %s' % self.sikulixProcess.pid)
            if sys.platform == "win32" :
                kill = subprocess.Popen( 
                                            r'taskkill /PID %s /F /T' % self.sikulixProcess.pid, 
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.DEVNULL, 
                                            stderr=subprocess.STDOUT,
                                            shell=True 
                                        )
                kill.communicate()
                kill.terminate()
                kill.wait()
            else:
                pass
   
            self.sikulixProcess.terminate()
            self.sikulixProcess.wait()
            
        self.onToolLogWarningCalled("SikuliX Server is stopped")
        
        # cleanup
        del self.sikulixProcess
        self.sikulixProcess = None
        
    def startProcess(self):
        """
        Start the sikulix process
        """
        self.onToolLogWarningCalled("Starting Sikulix Server...")
        try:
            thread = threading.Thread(target = self.__startProcess )
            thread.start()
            thread.join()   
        except Exception as e:
            self.error( "unable to make a thread to start process: %s" % e )
            
    def __startProcess(self, timeout=20):
        """
        Internal function to start the process
        """
        try:
            # prepare path
            if sys.platform == "win32" :
                __cmd__ = '%s\%s\%s' % (Settings.getDirExec(), 
                                        Settings.get('Paths', 'bin'), 
                                        Settings.get('BinWin', 'sikuli') )
            else:
                __cmd__ = Settings.get('BinLinux', 'sikulix')
            __cmd__ = r'"%s" -s' % __cmd__
            self.trace( "external program called: %s" % __cmd__)

            self.sikulixProcess = subprocess.Popen(
                                                    __cmd__, 
                                                    stdin=subprocess.PIPE, 
                                                    stdout=subprocess.DEVNULL, 
                                                    stderr=subprocess.STDOUT,
                                                    shell=True 
                                                  )
            self.trace("Sikulix Server thread started Pid=%s" % self.sikulixProcess.pid)
            
            # checking if the server is properly started
            currentTime = startedTime = time.time()
            started = False
            while((currentTime-startedTime)<timeout):
                try:
                    requestlib.urlopen(self.urlHost).read()
                except Exception as err:
                    currentTime = time.time()
                    time.sleep(1.0)
                    continue
                started = True
                break
            if not started:
                raise RuntimeError('Start sikuli java process failed!')
            else:
                self.trace("start ok")
                self.onToolLogWarningCalled("Sikulix Server is started")
                self.onPluginStarted()  
                self.configurePlugin()

        except Exception as e:
            self.onToolLogErrorCalled("Unable to start Sikulix Server")
            self.error( "unable to start Sikulix Server: %s" % str(e))  
            self.onResetAgentCalled()
        
    def configurePlugin(self):
        """
        Configure the plugin
        """
        self.onToolLogWarningCalled("Configuring Sikulix Server...")
        
        try:
            thread = threading.Thread(target = self.__configurePlugin )
            thread.start()
            thread.join()   
        except Exception as e:
            self.error( "unable to make a thread to configure process: %s" % e )

    def __configurePlugin(self):
        """
        Internal function to configure the plugin
        """
        self.trace("Initialize server")

        #initiates a Jython runner
        try:
            url = "%s/startp" % self.urlHost
            response = requestlib.urlopen(url).read()
        except Exception as err:
            self.onToolLogErrorCalled("Unable to configure Sikulix Server")
            self.error( "unable to configure Sikulix Server server: %s" % err)  
            self.onResetAgentCalled()
        else:
            if b'PASS 200' in response:
                self.onToolLogWarningCalled("Successfully configured")

                # prepare the temp folder in the home directory of the user
                self.onToolLogWarningCalled("Preparing Sikulix Server...")
                try:
                    shutil.rmtree( self.homeFolder )
                except Exception as e:
                    pass
                try:
                    os.mkdir( self.homeFolder )
                except Exception as e:
                    self.error("unable to create temp folder: %s" % e)
                    self.onToolLogErrorCalled("Unable to prepare temp folder")
                    self.onResetAgentCalled()
                else:

                    try:
                        url = "%s/scripts/home/%s" % (self.urlHost,self.nameFolder)
                        response = requestlib.urlopen(url).read()
                    except Exception as err:
                        self.onToolLogErrorCalled("Unable to prepare home folder")
                        self.error( "unable to prepare home folder: %s" % err)  
                        self.onResetAgentCalled()
                    else:
                        if b'PASS 200' in response:
                            self.onToolLogWarningCalled("Successfully prepared")
                            self.onPluginStarted()
                        else:
                            self.onToolLogErrorCalled("Unable to prepare Sikulix Server")
                            self.error( "unable to prepare Sikulix Server server: %s" % response)  
                            self.onResetAgentCalled()
            else:
                self.onToolLogErrorCalled("Unable to configure Sikulix Server")
                self.error( "unable to configure Sikulix Server server: %s" % response)  
                self.onResetAgentCalled()

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
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                a = self.context()[request['uuid']][request['source-adapter']]
                a.putItem( lambda: self.execAction(request) )
            else:
                self.error("Adapter context does not exists ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits ScriptId=%s" % request['uuid'])
        self.__mutex__.release()
        
    def takeScreenshot(self, request, action, actionId, adapterId, testcaseName, replayId=0):
        """
        Take a screenshot
        """
        self.trace('taking a screenshot')

        if sys.platform == "win32" :
            self.onTakeScreenshot(request, action, str(actionId), str(adapterId), 
                                    testcaseName, int(replayId) )
        elif sys.platform == "linux2" and not self.getFromCmd() :
            self.onTakeScreenshot(request, action, str(actionId), str(adapterId), 
                                    testcaseName, int(replayId) )
        else:
            self.error( 'take screenshot not supported on system=%s from cmd=%s' %  (sys.platform, self.getFromCmd()) )
        
    def onFinalizeScreenshot(self, request, action, actionId, adapterId, testcaseName, replayId, screenshot, thumbnail):
        """
        On finalize the screenshot procedure
        """
        self.trace('ReplayId=%s screenshot size=%s and thumbnail size=%s' % (replayId, len(screenshot), len(thumbnail)) )
        
        extension = Settings.get( 'Screenshot', 'extension' )
        fileName = "%s_%s_ADP%s_step%s_%s.%s" % (testcaseName, replayId, request['source-adapter'], 
                                                 actionId, action, extension.lower())

        # send screenshot
        if 'result-path' in request: 
            self.onToolLogWarningCalled( "<< Uploading screenshot...")
            self.uploadData(fileName=fileName,  resultPath=request['result-path'], data=screenshot ) 

        # send through notify only a thumbnail
        try:
            self.sendData(request=request, data={ 'data': thumbnail, 'filename': '%s_%s.%s' % (action, actionId, extension),
                                                    'action': action, 'action-id': "%s" % actionId, 'adapter-id': "%s" % adapterId  } )
        except Exception as e:
            self.error("unable to send notify through notify: %s" % e)
            
        self.trace('screenshot sent')  
        
    def execAction(self, request):
        """
        Exec action
        """
        # globalID = <id_script>_<test_replay_id>_<id_adapter>_<id_action>
        globalId = "%s_%s_%s_%s" % (request['script_id'], request['test-replay-id'],
                                    request['source-adapter'], request['data']['action-id'] )
        self.onToolLogWarningCalled( "<< Action (%s) called: %s" % (globalId, request['data']['action'])  )
        
        # dispatch action
        if request['data']['action'] == 'SCREENSHOT':
            self.takeScreenshot(
                                    request=request, 
                                    action=request['data']['action'], 
                                    actionId=request['data']['action-id'], 
                                    adapterId=request['source-adapter'],
                                    testcaseName=request['testcase-name'], 
                                    replayId=request['test-replay-id']
                                )
        else:
            # run sikuli script
            if os.path.exists("%s/%s.sikuli" % (self.homeFolder, self.nameFolder) ):
                self.sendNotify(request=request, data={'action': request['data']['action'], 
                                'action-id': request['data']['action-id'], 'result': 'BUSY',
                                'output': ""} )
            else:
            
                # prepare the sikuli folder
                sikuliFolder = "%s//%s.sikuli//" % (self.homeFolder, self.nameFolder)
                try:
                    os.mkdir( sikuliFolder )
                except Exception as e:
                    self.error("unable to add the sikuli folder: %s" % sikuliFolder)
                else:
                    
                    self.trace("adding the code script")
                    # prepare the code and save it
                    code = request['data']['code']
                    code = code.replace('__PATH__',  os.path.normpath(sikuliFolder).replace("\\", "\\\\") )
                    self.trace("code to run")
                    self.trace(code)
                    try:
                        absPath = "%s\\%s.py" % (sikuliFolder, self.nameFolder )
                        f = open(absPath, 'w')
                        f.write( code )
                        f.close()
                    except Exception as e:
                        self.error('unable to save sikuli script: %s' % str(e) )
                        self.sendError(request=request, data='Fails to save action')
                    else:
                    
                        # save images
                        if 'main-img' in request['data']:
                            try:
                                absPath = "%s\\%s.png" % (sikuliFolder, request['data']['main-img-name'])
                                self.trace('save main image in %s' % absPath )
                                f = open(absPath, 'wb')
                                f.write( request['data']['main-img'] )
                                f.close()
                            except Exception as e:
                                self.error('unable to save main image: %s %s' % str(e) )
                                self.sendError(request=request, data='Fails to save main image')
                                
                        if 'img' in request['data']:
                            try:
                                absPath = "%s\\%s.png" % (sikuliFolder, request['data']['img-name'] )
                                self.trace('save image in %s' % absPath )
                                f = open(absPath, 'wb')
                                f.write( request['data']['img'] )
                                f.close()
                            except Exception as e:
                                self.error('unable to save image: %s %s' % str(e) )
                                self.sendError(request=request, data='Fails to save image')

                        # running the script
                        self.trace("running the script")
                        try:
                            url = "%s/run/%s" %  (self.urlHost, self.nameFolder)
                            response = requestlib.urlopen(url).read()
                        except Exception as err:
                            self.error( 'sikuli action ko on server: %s'  % err )
                            self.sendError(request=request, data='Fails to run action')
                        else:
                            self.trace("response received from sikulix: %s" % response)
                            if b'PASS 200' in response:
                                # read value returned by script
                                try:
                                    returnCode = response.split(b"runScript: returned:")[1].strip()
                                    returnCode = int(returnCode)
                                except Exception as err:
                                    self.error("unable to read returned code: %s" % err)
                                    self.sendError(request=request, data='Fails to read return code')
                                    
                                else:
                                    if returnCode == CODE_ERROR :
                                        # read data
                                        try:
                                            absPath = "%s\\debug.log" % (sikuliFolder)
                                            f = open(absPath, 'r')
                                            debug_log = f.read()
                                            f.close()
                                        except Exception as err:
                                            self.error("unable to read debug log: %s" % err)
                                            self.sendError(request=request, data='Fails to read debug log')
                                        else:
                                            self.sendNotify(    
                                                            request=request, 
                                                            data={  
                                                                    'action': request['data']['action'], 
                                                                    'action-id': request['data']['action-id'], 
                                                                    'result': 'FAILED', 
                                                                    'output': debug_log
                                                                } 
                                                        )
                                            self.takeScreenshot(
                                                                    request=request, action=request['data']['action'], 
                                                                    actionId=request['data']['action-id'], 
                                                                    adapterId=request['source-adapter'],
                                                                    testcaseName=request['testcase-name'], 
                                                                    replayId=request['test-replay-id']
                                                                )  
                                                            
                                    elif returnCode == CODE_GET:
                                        
                                        # read data
                                        try:
                                            absPath = "%s\\text.dat" % (sikuliFolder)
                                            f = open(absPath, 'r')
                                            text = f.read()
                                            f.close()
                                        except Exception as err:
                                            self.error("unable to read data: %s" % err)
                                            self.sendError(request=request, data='Fails to read data')
                                        else:
                                            self.sendNotify(    
                                                                request=request, 
                                                                data={  
                                                                        'action': request['data']['action'], 
                                                                        'action-id': request['data']['action-id'], 
                                                                        'result': 'OK', 
                                                                        'text-result': text
                                                                    } 
                                                            )
                                    elif returnCode == CODE_OK:
                                        self.sendNotify(    
                                                            request=request, 
                                                            data={  
                                                                    'action': request['data']['action'], 
                                                                    'action-id': request['data']['action-id'], 
                                                                    'result': 'OK', 
                                                                    'output': ""
                                                                } 
                                                        )
                                    else:
                                        self.error("unknown return code received: %s" % returnCode)
                                        self.sendError(request=request, data='Fails to read return code, unknown code: %s' % returnCode)
                                        
                            else:
                                self.sendError(request=request, data='Fails to read server response')
                            
                    # delete the sikuli folder                
                    self.trace("delete the temp folder")
                    try:
                        shutil.rmtree( sikuliFolder )
                    except Exception as e:
                        self.error('delete sikuli folder failed: %s' % str(e) )
                        
        self.onToolLogWarningCalled( "<< Action (%s) terminated." % globalId)

