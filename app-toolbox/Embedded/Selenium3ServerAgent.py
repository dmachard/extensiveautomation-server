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
Selenium3 agent
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
import socket
import re
import base64

try:
    import StringIO
except ImportError: # support python 3
    import io as StringIO
import time


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
 
SELENIUM_READY=True
try:
    from selenium import webdriver
    from selenium.webdriver.remote import utils
    from selenium.webdriver.remote.command import Command
except ImportError:
    SELENIUM_READY=False
    
    
__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False
__APP_PATH__ = ""
__TYPE__="""selenium3-server"""
__RESUME__="""This agent enables to control a website through the selenium project.
Selenium automates browsers. Can be used on Windows only."""

__DESCRIPTION__="""This agent enables to control a website through the selenium project

Events messages:
    Agent->Server
        * Error( msg )
        * Data( action, action-id, data, filename )
        * Notify( action, action-id, result)

    Server->Agent
        * Init( ... ) - not used
        * Notify( action, action-id, img, main-img, code )
        * Reset( ... ) - not used

Targetted operating system: Windows and Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, 
                defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return SeleniumServer( controllerIp, controllerPort, toolName, toolDesc, 
                            defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )

class SeleniumWait(object):
    """
    Selenium wait object
    """
    def __init__(self):
        """
        Constructor
        """
        pass
        
class SeleniumServer(GenericTool.Tool):
    """
    Selenium tool class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=0, 
                        proxyIp=None, proxyPort=None, sslSupport=True, seleniumIp="127.0.0.1", seleniumPort=4444):
        """
        Selenium tool constructor
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                                    supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, 
                                    sslSupport=sslSupport)
        self.__type__ = __TYPE__
        self.__mutex__ = threading.RLock()

        self.seleniumIp = seleniumIp
        self.seleniumPort = seleniumPort
        self.seleniumProcess = None
        
        self.urlHost = "http://%s:%s/wd/hub/" % (self.seleniumIp, self.seleniumPort)
             
    def checkPrerequisites(self):
        """
        Check prerequisites
        """
        if not SELENIUM_READY: 
            self.onToolLogErrorCalled("Selenium external library is missing!")
            raise Exception("Selenium external library is missing!")
            
        # Adding limitation
        # Blocking the run of several selenium server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        result = sock.connect_ex( (self.seleniumIp, self.seleniumPort))
        if result == 0:
            self.onToolLogErrorCalled("Selenium Server already started in another instance!")
            raise Exception("Selenium Server already started in another instance!")
        
    def initAfterRegistration(self):
        """
        Called after registration
        """
        if self.seleniumProcess is not None:
            self.trace("Selenium Server already started")
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
        
    def pluginStopped(self):
        """
        Function to reimplement
        """
        pass
        
    def getType(self):
        """
        Return the type of the agent
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
        """
        self.stopProcess()

    def stopProcess(self):
        """
        Stop the process
        """
        self.onToolLogWarningCalled("Stopping Selenium Server...")
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
        if self.seleniumProcess is not None:
            self.trace('killing process with pid %s' % self.seleniumProcess.pid)
            if sys.platform == "win32" :
                try:
                    self.trace('killing process')
                    kill = subprocess.Popen( 
                                                r'taskkill /PID %s /F /T' % self.seleniumProcess.pid, 
                                                stdin=subprocess.PIPE, 
                                                stdout=subprocess.DEVNULL, 
                                                stderr=subprocess.STDOUT,
                                                shell=True
                                            )
                    kill.communicate()
                    kill.terminate()
                    kill.wait()
                    self.trace('process killed')
                except Exception as e:
                    self.error( "unable to kill the process: %s" % e )
            else:
                pass
   
            self.seleniumProcess.terminate()
            self.seleniumProcess.wait()
            
        self.onToolLogWarningCalled("Selenium Server is stopped")
        
        # cleanup
        del self.seleniumProcess
        self.seleniumProcess = None
        
    def startProcess(self):
        """
        Start the process
        """
        self.onToolLogWarningCalled("Starting Selenium Server...")
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
            if sys.platform == "win32" :
                __cmd__ = r'"%s\%s\%s" -jar ' % (   Settings.getDirExec(), 
                                                    Settings.get( 'Paths', 'bin' ), 
                                                    Settings.get( 'BinWin', 'selenium3' ) )
                __cmd__ += r' -Dwebdriver.ie.driver="%s\Selenium3\IEDriverServer.exe" ' % (
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'bin' ))
                                                                                )
                __cmd__ += r' -Dwebdriver.chrome.driver="%s\Selenium3\chromedriver.exe" ' % (
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'bin' ))
                                                                                )
                __cmd__ += r' -Dwebdriver.opera.driver="%s\Selenium3\operadriver.exe" ' % (
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'bin' ))
                                                                                )
                __cmd__ += r' -Dwebdriver.gecko.driver="%s\Selenium3\geckodriver.exe" ' % (
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'bin' ))
                                                                                )
                __cmd__ += r' -Dwebdriver.edge.driver="%s\Selenium3\MicrosoftWebDriver.exe" ' % (
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'bin' ))
                                                                                )
                                                                                
                __cmd__ +=  r' "%s\Selenium3\selenium-server-standalone.jar"' % (
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'bin' ))
                                                                                )
                
                __cmd__ += r' -log "%s\selenium3_%s.log" -debug true' % ( "%s\%s" % ( Settings.getDirExec(), 
                                                                                        Settings.get( 'Paths', 'logs' )), 
                                                                          self.toolName)
            else:
                __cmd__ = r'%s -jar \"%s/%s/%s\" -log "%s/selenium_%s.log" -debug true' % (
                                                                                Settings.get( 'BinLinux', 'java' ),  
                                                                                Settings.getDirExec(), Settings.get('Paths', 'bin'), 
                                                                                Settings.get('BinLinux', 'selenium' ),
                                                                                "%s\%s" % ( Settings.getDirExec(), 
                                                                                            Settings.get( 'Paths', 'logs' )),
                                                                                self.toolName
                                                                                )
            self.trace( "external program called: %s" % __cmd__)

            self.seleniumProcess = subprocess.Popen(
                                                    __cmd__, 
                                                    stdin=subprocess.PIPE, 
                                                    stdout=subprocess.DEVNULL, 
                                                    stderr=subprocess.STDOUT,
                                                    shell=True 
                                                  )
            self.trace("Selenium Server thread started Pid=%s" % self.seleniumProcess.pid)

            # checking if the server is properly started
            currentTime = startedTime = time.time()
            started = False
            while((currentTime-startedTime)<timeout):
                try:
                    requestlib.urlopen(self.urlHost).read()
                except Exception as err:
                    currentTime = time.time()
                    time.sleep(2.0)
                    continue
                started = True
                break
            if not started:
                raise RuntimeError('Start Selenium java process failed!')
            else:
                time.sleep(2.0)
                self.trace("start ok")
                self.onToolLogWarningCalled("Selenium Server is started")
                self.onPluginStarted()  

        except Exception as e:
            self.onToolLogErrorCalled("Unable to start Selenium Server")
            self.error( "unable to start Selenium Server: %s" % str(e))  
            self.onResetAgentCalled()
        
    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass

    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        On reset test context event
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
        self.trace('init received')

    def onAgentReset(self, client, tid, request):
        """
        Reset the socket 
        """
        self.trace('reset received')

    def onAgentNotify(self, client, tid, request):
        """
        Received a notify from server
        """
        self.__mutex__.acquire()
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                a = self.context()[request['uuid']][request['source-adapter']]
                a.putItem( lambda: self.execAction(request) )
            else:
                self.error("Adapter context does not exists ScriptId=%s AdapterId=%s" % (request['uuid'], request['source-adapter'] ) )
        else:
            self.error("Test context does not exits ScriptId=%s" % request['uuid'])
        self.__mutex__.release()
        
    def onFinalizeScreenshot(self, request, commandName, commandId, adapterId, testcaseName, replayId, screenshot, thumbnail):
        """
        On finalize screenshot procedure
        """
        extension = Settings.get( 'Screenshot', 'extension' )
        fileName = "%s_%s_ADP%s_step%s_%s.%s" % (testcaseName, replayId, request['source-adapter'], 
                                                 commandId, commandName, extension.lower())
        
        self.trace('screenshot size=%s' % len(screenshot) )
        self.trace('thumbnail size=%s' % len(thumbnail) )
        # send screenshot
        if 'result-path' in request: 
            self.onToolLogWarningCalled( "<< Uploading screenshot...")
            self.uploadData(fileName=fileName,  resultPath=request['result-path'], data=screenshot ) 

        # send through notify only a thumbnail
        try:
            self.sendData(request=request, data={   'data': thumbnail, 'filename': '%s_%s.%s' % (commandName, commandId, extension),
                                                    'command-name': commandName, 'command-id': "%s" % commandId, 
                                                    'adapter-id': "%s" % adapterId  } )
        except Exception as e:
            self.error("unable to send notify through notify: %s" % e)
            
        self.trace('screenshot sent')   
        
    def takeScreenshot(self, request, commandName, commandId, adapterId, testcaseName, replayId=0):
        """
        Take a screenshot
        Only for windows, can works on linux and graphical mode
        
        TODO: use selenium the internal screnshot as file function to run in linux or windows
        """
        self.trace("taking screenshot")
        if sys.platform == "win32" :
            self.onTakeScreenshot(request, commandName, str(commandId), str(adapterId), testcaseName, int(replayId) )
        elif sys.platform == "linux2" and not self.getFromCmd() :
            self.onTakeScreenshot(request, commandName, str(commandId), str(adapterId), testcaseName, int(replayId) )
        else:
            self.error( 'take screenshot not supported on system=%s from cmd=%s' %  (sys.platform,self.getFromCmd()) )
            
    def execAction(self, request):
        """
        Execute the action received from the server
        """
        # read the request
        waitUntil = False
        waitUntil_Timeout = 10.0
        waitUntil_Not = False
        waitUntil_Pool = 0.5
        waitUntil_Value = None
        
        # extract selenium data
        try:
            self.trace('starting extract data for selenium')
            driver_command = request['data']['command-name']
            driver_params = request['data']['command-params']
            driver_capabilities = request['data']['command-capabilities']
            if 'sessionId' in driver_params:
                sessionId = driver_params['sessionId']
            else:
                sessionId = None
                
            if "wait-until" in request['data']: waitUntil = request['data']["wait-until"]
            if "wait-until-timeout" in request['data']: waitUntil_Timeout = request['data']["wait-until-timeout"]
            if "wait-until-pool" in request['data']: waitUntil_Pool = request['data']["wait-until-pool"]
            if "wait-until-value" in request['data']: waitUntil_Value = request['data']["wait-until-value"]
        except Exception as e:
            self.error('unable to extract request from server: %s' % e )
            return
            
        # prepare id   
        try:
            globalId = "%s_%s_%s" % (request['script_id'], request['source-adapter'], request['data']['command-id'] )
            self.onToolLogWarningCalled( "<< %s #%s [%s %s %s]" % (request['data']['command-name'], globalId, 
                                                                    waitUntil, waitUntil_Timeout, waitUntil_Value) )
        except Exception as e:
            self.error('unable to read request: %s' % e )
            
        # prepare driver for selenium
        try:
            self.trace('preparing selenium driver')
            
            seleniumDriver = webdriver.Remote(  command_executor='http://%s:%s/wd/hub' % (self.seleniumIp, self.seleniumPort), 
                                                start_session=False, session_id=sessionId,
                                                handle_error=False, unwrap_value=False)
            seleniumDriver.capabilities = driver_capabilities
        except Exception as e:
            self.error('unable to prepare driver: %s' % e )
            self.sendError(request=request, data='unable to run selenium: %s' % e)
            self.onToolLogErrorCalled( "<< Unable to run selenium")
            return

        # execute the selenium command
        try:
            if waitUntil:
                end_time = time.time() + waitUntil_Timeout
                timeout_raised = False
                while True:
                    try:
                        response = seleniumDriver.execute(driver_command=driver_command, params=driver_params)
                        send_notify = False
                        if waitUntil_Value != None:
                            if response['status'] == 0 and response['value'] == waitUntil_Value:
                                send_notify = True
                        else:
                            if response['status'] == 0:
                                send_notify = True
                        
                        if send_notify:
                            self.sendNotify( request=request, data={ 'command-name': request['data']['command-name'],
                                                            'command-id': request['data']['command-id'],
                                                            'command-value': response }  )
                            break 
                    except Exception as e:
                        pass
                    time.sleep(waitUntil_Pool)
                    if time.time() > end_time:
                        timeout_raised = True
                        break
                        
                # timeout raised
                if timeout_raised:
                    self.sendNotify( request=request, data={ 'command-name': request['data']['command-name'],
                                                    'command-id': request['data']['command-id'],
                                                    'command-value': {"status": 1000, 'value': None} }  )
                    self.takeScreenshot( request=request, commandName=request['data']['command-name'],
                                         commandId=request['data']['command-id'], adapterId=request['source-adapter'],
                                         testcaseName=request['testcase-name'], replayId=request['test-replay-id'] )
              

            else:

                    self.trace('executing the selenium command %s with params %s' % (driver_command, driver_params) )
                    response = seleniumDriver.execute(driver_command=driver_command, params=driver_params)
                    self.onToolLogWarningCalled( ">> Action #%s terminated" % globalId )
                    
                    # remove image on error response
                    if response['status'] != 0: 
                        self.error("error on selenium response - %s" % response)
                        if isinstance(response['value'], str):
                            if ',"screen":"' in response['value']:
                                begin, left = response['value'].split(',"screen":"')
                                junk, left = left.split('"', 1)
                                del junk
                                response['value'] = "%s%s" % (begin, left)
                                
                    # notify user
                    self.sendNotify( request=request, data={ 'command-name': request['data']['command-name'],
                                                            'command-id': request['data']['command-id'],
                                                            'command-value': response }  )  


                    # manually take screenshot
                    if driver_command == "screenshot":
                        self.onToolLogWarningCalled( "<< Uploading screenshot...")
                        extension = Settings.get( 'Screenshot', 'extension' )
                        fileName = "%s_%s_ADP%s_step%s_%s.%s" % (request['testcase-name'], request['test-replay-id'], 
                                                                request['source-adapter'], 
                                                                request['data']['command-id'], 
                                                                request['data']['command-name'], extension.lower())
                        screenshot = base64.b64decode(response['value'].encode('ascii'))
                        self.uploadData(fileName=fileName,  resultPath=request['result-path'], data=screenshot) 
                        
                    # automatic take screenshot on error
                    if response['status'] != 0: 
                        self.takeScreenshot( request=request, commandName=request['data']['command-name'],
                                             commandId=request['data']['command-id'], adapterId=request['source-adapter'],
                                             testcaseName=request['testcase-name'], replayId=request['test-replay-id'] )

                    self.trace('executing the selenium command - terminated - notify sent')
        except Exception as e:
            self.error('unable to execute action: %s' % e )
            self.sendError(request=request, data='unable to execute action: %s' % e)
            self.onToolLogErrorCalled( ">> Unable to run #%s" % globalId)
            
            self.takeScreenshot(request=request, 
                                commandName=request['data']['command-name'], 
                                commandId=request['data']['command-id'], 
                                adapterId=request['source-adapter'],
                                testcaseName=request['testcase-name'], 
                                replayId=request['test-replay-id'] )