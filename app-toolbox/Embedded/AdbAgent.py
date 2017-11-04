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
ADB agent
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

# import urllib to use it with device
try:
    import urllib2
except ImportError: # support python 3
    from urllib import request as urllib2

# disable system proxy for urllib, use only in localhost
proxy_handler = urllib2.ProxyHandler({})
opener = urllib2.build_opener(proxy_handler)
urllib2.install_opener(opener)

# import json, use to interact with json server on device
import json

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = '%s\%s\%s' % (Settings.getDirExec(), Settings.get('Paths', 'bin'), Settings.get('BinWin', 'adb') )
__TYPE__="""adb"""
__RESUME__="""This agent enables to control mobile phone throught android debug bridge.
Can be used on Windows only."""

__DESCRIPTION__="""This agent enables to control mobile phone throught android debug bridge.

Events messages:
    Agent->Server
        * Error( msg )
        * Data( action, action-id, data, filename )
        * Notify( action, action-id, result)

    Server->Agent
        * Init( ... ) - not used
        * Notify( action, action-id, img, main-img, code )
        * Reset( ... ) - not used
        
Targetted operating system: Windows"""

import sys

    
    
class UiAutomatorThread(threading.Thread):
    """
    UiAutomator Thread class
    """
    def __init__(self, parent):
        """
        Individual adb thread
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.parent = parent
        self.uiProcess = None
        self.isCancelled = False
        self.isStarted  = False
        
    def trace(self, msg):
        """
        Trace to log file
        """
        self.parent.trace(msg)
        
    def readData(self, maxTimeout=30, prompt=b'INSTRUMENTATION_STATUS_CODE: 1'):
        """
        Read data
        """
        self.trace("read data from adb thread")
        timeout = False
        startTime = time.time()
        outputs = []
        
        if self.isCancelled: return ( False, outputs )
        
        while (not timeout or not self.isCancelled):
            time.sleep(0.1)
            timeRef = time.time() 
            if ( timeRef- startTime) >= maxTimeout:
                self.parent.error( 'timeout raised - start time: %s' %  startTime)
                timeout = True 
                break

            line = self.uiProcess.stdout.readline()
            if line:
                self.trace("line adb: %s" % line)
                outputs.append( line )
            if prompt in line:
                break
        if timeout:
            return ( False, outputs )
        else:
            return ( True, outputs )
            
    def run(self):
        """
        On running thread
        """
        self.parent.onToolLogWarningCalled("Starting UIautomator on device...")

        __adbexe__ = '%s\%s\%s' % (Settings.getDirExec(), Settings.get('Paths', 'bin'), Settings.get('BinWin', 'adb-exe') )
        __adbbin__ = '%s\%s' % (Settings.getDirExec(), Settings.get('Paths', 'bin'))
        
        self.trace("uploading jar files on devices")
        __cmd__ = '"%s" push "%s\\Adb\\bundle.jar" /data/local/tmp/' % (__adbexe__, __adbbin__ )
        ret = subprocess.call(  __cmd__, shell=True, 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.trace("uploading ret: %s" % ret)
        
        __cmd__ = '"%s" push "%s\\Adb\\uiautomator-stub.jar" /data/local/tmp/' % (__adbexe__,  __adbbin__)
        ret = subprocess.call(  __cmd__, shell=True, 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.trace("uploading ret: %s" % ret)

        __cmd__ = r'"%s" shell uiautomator runtest uiautomator-stub.jar bundle.jar -c com.github.uiautomatorstub.Stub' % __adbexe__
        self.parent.trace(__cmd__)
        try:
            self.uiProcess = subprocess.Popen(  __cmd__, shell=True, 
                                                stdin=subprocess.PIPE, 
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                bufsize=0 )
            pid = self.uiProcess.pid
            self.parent.trace("UIautomator thread started with pid=%s" % pid)
            if sys.version_info > (3,):
                ret, lines = self.readData(prompt=b'INSTRUMENTATION_STATUS_CODE: 1', maxTimeout=10)
            else:
                ret, lines = self.readData(prompt='INSTRUMENTATION_STATUS_CODE: 1', maxTimeout=10) 
            if ret:
                self.parent.trace("prompt uiautomator detected")
         
                self.parent.onToolLogWarningCalled("UIautomator is started")
                
                
                __cmd__ = '"%s" forward tcp:%s tcp:%s' % (__adbexe__, self.parent.localPort, self.parent.devicePort )
                self.trace("activate forward: %s" % __cmd__)
                ret = subprocess.call(__cmd__, shell=True)
                self.trace("%s" % ret)

                self.parent.startScreenCapture()

                self.isStarted = True                                 
            else:
                self.parent.onToolLogErrorCalled("Unable to start UIautomator")
        except Exception as e:
            self.parent.onToolLogErrorCalled("Unable to start UIautomator")
            self.parent.error( "Unable to start UIautomator: %s" % str(e))  
            self.parent.onResetAgentCalled()
        
    def stop(self):
        """
        Stop the thread
        """
        self.parent.onToolLogWarningCalled("Stopping UIautomator...")
        self.isCancelled = False
        
        self.parent.trace('killing process with pid %s' % self.uiProcess.pid)
        kill = subprocess.Popen( 
                                    r'taskkill /PID %s /F /T' % self.uiProcess.pid, 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.STDOUT,
                                    shell=True
                                )
        kill.communicate()
        kill.terminate()
        kill.wait()
        self.parent.onToolLogWarningCalled("UIautomator is stopped")
        
MAX_ERROR_SCREEN=5

class AdbScreenThread(threading.Thread):
    """
    ADB screen thread
    """
    def __init__(self, parent):
        """
        Individual screen thread
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.parent = parent
        self.running = False

    def trace(self, msg):
        """
        Trace to log file
        """
        self.parent.trace(msg)
        
    def run(self):
        """
        On running thread
        """
        __adbexe__ = '%s\%s\%s' % (Settings.getDirExec(), Settings.get('Paths', 'bin'), Settings.get('BinWin', 'adb-exe') )
        __ret__ = '%s\screncapture.png' % self.parent.getTemp()
        __cmd__ = '"%s" pull /data/local/tmp/screncapture.png "%s"' % ( __adbexe__, __ret__)
        __ret2__ = '%s\layout.xml' % self.parent.getTemp()  
        __cmd2__ = '"%s" pull /data/local/tmp/local/tmp/layout.xml "%s"' % ( __adbexe__, __ret2__)
        
        req = urllib2.Request('http://127.0.0.1:%s/jsonrpc/0' % self.parent.localPort )
        req.add_header('Content-Type', 'application/json')

        nbError = 0
        while not self.stopEvent.isSet():
            time.sleep(0.1)
            
            if self.running:
                try:
                    response = urllib2.urlopen(req, b'{"jsonrpc":"2.0","method":"takeScreenshot","id":1, "params": [ "screncapture.png", 1.0, 90] }' )
                    
                    response2 = urllib2.urlopen(req, b'{"jsonrpc":"2.0","method":"dumpWindowHierarchy","id":1, "params": [ true, "layout.xml" ] }' )
                    subprocess.call(__cmd2__, shell=True, 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

                except Exception as e:
                    self.parent.error("error on adb screen thread: %s" % e )
                    nbError += 1
                    if nbError >= MAX_ERROR_SCREEN: self.stop()
                else:
                
                    ret = subprocess.call(  __cmd__, shell=True, 
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)
                    if not ret:
                        self.parent.onScreenCaptured(filename=__ret__,xml=__ret2__)

    def stop(self):
        """
        Stop the thread
        """
        self.parent.onToolLogWarningCalled("Stopping screen capture...")
        self.stopEvent.set()
        self.parent.onToolLogWarningCalled("Screen capture is stopped")
        
class AdbServerThread(threading.Thread):
    """
    ADB server thread
    """
    def __init__(self, parent):
        """
        Individual ADB server thread
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.parent = parent
        self.adbProcess = None
        self.isStarted = False
        self.isCancelled = False

    def trace(self, msg):
        """
        Trace to log file
        """
        self.parent.trace(msg)
        
    def readData(self, maxTimeout=30, prompt=b'OK'):
        """
        Read data
        """
        self.trace("read data from adb thread")
        timeout = False
        startTime = time.time()
        outputs = []
        
        if self.isCancelled: return ( False, outputs )
        
        while (not timeout or not self.isCancelled):
            time.sleep(0.1)
            timeRef = time.time() 
            if ( timeRef- startTime) >= maxTimeout:
                self.parent.error( 'timeout raised - start time: %s' %  startTime)
                timeout = True 
                break

            line = self.adbProcess.stdout.readline()
            if line:
                self.trace("line adb: %s" % line)
                outputs.append( line )
            if prompt in line:
                break
        if timeout:
            return ( False, outputs )
        else:
            return ( True, outputs )

    def run(self):
        """
        On run function
        """
        __cmd__ = r'"%s"' % __APP_PATH__
        self.parent.trace(__cmd__)
        try:
            self.adbProcess = subprocess.Popen( __cmd__, shell=True, 
                                                stdin=subprocess.PIPE, 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.STDOUT, bufsize=0 )
            pid = self.adbProcess.pid
            self.parent.trace("Adb thread started with pid=%s" % pid)
            if sys.version_info > (3,):
                ret, lines = self.readData(prompt=b'OK', maxTimeout=30)
            else:
                ret, lines = self.readData(prompt='OK', maxTimeout=30) 
            if ret:
                self.parent.trace("prompt adb detected")
         
                self.parent.onToolLogWarningCalled("Adb is started")
                
                self.parent.onPluginStarted()
                self.parent.startUiautomator()

                self.isStarted = True                                 
            else:
                self.parent.onToolLogErrorCalled("Unable to start ADB")
        except Exception as e:
            self.parent.onToolLogErrorCalled("Unable to start ADB server")
            self.parent.error( "Unable to start adb server: %s" % str(e))  
            self.parent.onResetAgentCalled()

    def stop(self):
        """
        Stop the thread
        """
        self.parent.onToolLogWarningCalled("Stopping Adb Server...")
        self.isCancelled = False
        
        self.parent.trace('killing process with pid %s' % self.adbProcess.pid)
        kill = subprocess.Popen( 
                                    r'taskkill /PID %s /F /T' % self.adbProcess.pid, 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.STDOUT,
                                    shell=True 
                                )
        kill.communicate()
        kill.terminate()
        kill.wait()
        self.parent.onToolLogWarningCalled("Adb server is stopped")


def initialize (controllerIp, controllerPort, toolName, toolDesc, 
                    defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Adb( controllerIp, controllerPort, toolName, toolDesc, 
                    defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    

class Adb(GenericTool.Tool):
    """
    ADB agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                        supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Android Debug Bridge constructor
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                                    supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, 
                                    sslSupport=sslSupport)
        self.__type__ = __TYPE__
        self.__mutex__ = threading.RLock()
   
        self.adbServerThread = None
        self.adbScreenThread = None
        self.adbUiThread = None
        
        self.devicePort = 9008
        self.localPort = 8080
    
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        if self.adbServerThread is not None:
            self.trace("adb already started")
            self.onPluginStarted()
        else:
            self.onToolLogWarningCalled("Starting Android Debug Bridge...")
            self.adbServerThread = AdbServerThread(parent=self)
            self.adbServerThread.start()
        
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
        
    def startUiautomator(self):
        """
        Start the UiAutomator
        """
        self.userConfirm( msg='Please to use USB for transfer (PTP or MTP)\nand accept RSA connection on the device!' )

    def onUserConfirmed(self):
        """
        On confirm received by user
        """
        self.adbUiThread = UiAutomatorThread(parent=self)
        self.adbUiThread.start()
        
    def startScreenCapture(self):
        """
        Start to capture the screen
        """
        self.adbScreenThread = AdbScreenThread(parent=self)
        self.adbScreenThread.start()
        
        # get the screen one
        self.getScreen()
        
        # device is ready
        self.onDeviceReady()
        
    def startAutomaticRefresh(self):
        """
        Activate automatic refresh
        """
        self.adbScreenThread.running = True
        
    def stopAutomaticRefresh(self):
        """
        Stop the automatic refresh
        """
        self.adbScreenThread.running = False
        
    def onDeviceReady(self):
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
        Return the agent type
        """
        return self.__type__

    def onScreenCaptured(self, filename, xml=''):
        """
        On screen captured event
        """
        pass
        
    def onCleanup(self):
        """
        Cleanup all
        """
        self.trace( "cleanup all" )

        try:
            if self.adbScreenThread is not None:
                self.adbScreenThread.stop()
                self.adbScreenThread.join()
        except Exception as e:
            self.error( "unable to cleanup screen capture: %s"  % e )
            
        if self.adbUiThread is not None:
            self.adbUiThread.isCancelled = True
        try:
            if self.adbUiThread is not None:
                self.adbUiThread.stop()
                self.adbUiThread.join()
        except Exception as e:
            self.error( "unable to cleanup uiautomator: %s"  % e )

        if self.adbServerThread is not None:
            self.adbServerThread.isCancelled = True

        try:
            if self.adbServerThread is not None:
                self.adbServerThread.stop()
                self.adbServerThread.join()
        except Exception as e:
            self.error( "unable to cleanup adb server: %s"  % e )

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
       
    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        On reset test context event
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

    def onAgentNotify(self, client, tid, request):
        """
        Received a notify from server
        """
        self.__mutex__.acquire()
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                a = self.context()[request['uuid']][request['source-adapter']]
                a.putItem( lambda: self.runAction(request) )
            else:
                self.error("Adapter context does not exists ScriptId=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits ScriptId=%s" % request['uuid'])
        self.__mutex__.release()
        
    def tapOn(self, x, y):
        """
        Tap on the screen to the x,y position
        """
        t = threading.Thread(target=self.__tapOn, kwargs={'x': x, 'y': y} )
        t.start()
 
    def __tapOn(self, x, y):
        """
        Internal function to tap on position
        """    
        __adbexe__ = '%s\%s\%s' % ( Settings.getDirExec(), 
                                    Settings.get('Paths', 'bin'), 
                                    Settings.get('BinWin', 'adb-exe') )
        __cmd__ = '"%s" shell input tap %s %s' % (__adbexe__, x,y)
        try:
            subprocess.call(__cmd__, shell=True, 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        except Exception as e:
            self.error("error on adb click thread: %s" % e )
                
    def getScreen(self):
        """
        Retreive screen capture from device
        """
        t = threading.Thread(target=self.__getScreen, kwargs={} )
        t.start()

    def __getScreen(self):
        """
        Internal function to retreive the screen from the device
        """
        __adbexe__ = '%s\%s\%s' % ( Settings.getDirExec(), 
                                    Settings.get('Paths', 'bin'), 
                                    Settings.get('BinWin', 'adb-exe') )
        __ret__ = '%s\screncapture.png' % self.getTemp()
        __ret2__ = '%s\layout.xml' % self.getTemp()  
        __cmd__ = '"%s" pull /data/local/tmp/screncapture.png "%s"' % ( __adbexe__, __ret__)
        __cmd2__ = '"%s" pull /data/local/tmp/local/tmp/layout.xml "%s"' % ( __adbexe__, __ret2__)
        
        req = urllib2.Request('http://127.0.0.1:%s/jsonrpc/0' % self.localPort )
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        try:
            response = urllib2.urlopen(req, b'{"jsonrpc":"2.0","method":"takeScreenshot","id":1, "params": [ "screncapture.png", 1.0, 90] }' )
            
            response2 = urllib2.urlopen(req, b'{"jsonrpc":"2.0","method":"dumpWindowHierarchy","id":1, "params": [ true, "layout.xml" ] }' )
            subprocess.call(__cmd2__, shell=True, 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT)

        except Exception as e:
            self.error("error on adb get screen thread: %s" % e )
        else:
        
            ret = subprocess.call(  __cmd__, shell=True,
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT)
            if not ret:
                self.onScreenCaptured(filename=__ret__,xml=__ret2__)
                
    def runAction(self, request):
        """
        Run action received from server
        """
        try:
            globalId = "%s_%s_%s" % (request['script_id'], request['source-adapter'], request['data']['command-id'] )
            self.onToolLogWarningCalled( "<< %s #%s" % (request['data']['command-name'], globalId) )
        except Exception as e:
            self.error('unable to read request: %s' % e )
        else:
            t = threading.Thread(target=self.__runAction, kwargs={ 'request': request, 'method': request['data']['command-name'], 
                                                                    'params': request['data']['command-params'] } )
            t.start()

    def __runAction(self, request, method, params):
        """
        Internal function to run action
        """
        if method == 'adb':
            __adbexe__ = '%s\%s\%s' % ( Settings.getDirExec(), 
                                        Settings.get('Paths', 'bin'), 
                                        Settings.get('BinWin', 'adb-exe') )
            __cmd__ = '"%s" %s' % (__adbexe__, params)
            stdout = ''
            returncode = 1
            try:
                proc = subprocess.Popen(__cmd__, shell=True, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                stdout, stderr = proc.communicate()
                returncode =  proc.returncode
            except Exception as e:
                self.error("error on adb: %s" % e )
            else:
                # notify the tester
                self.sendNotify( request=request, data={ 'command-name': request['data']['command-name'],
                                                        'command-id': request['data']['command-id'],
                                                        'command-value': stdout,
                                                        'command-result': returncode }  )  

        else:
            req = urllib2.Request('http://127.0.0.1:%s/jsonrpc/0' % self.localPort)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            
            ret = False
            try:
                body = '{"jsonrpc":"2.0","method":"%s","id":1, "params": %s }' %   ( method, params)

                # make the http request
                response = urllib2.urlopen(req, bytes(body, 'utf8') )
                json_decoded = json.loads(response.read().decode('utf8'))

                if 'result' in json_decoded:
                    ret = {"result": json_decoded['result']}
                if "error" in json_decoded:
                    ret = {"error": json_decoded['error']}

            except Exception as e:
                self.error("error on %s on: %s" % (method,e) )
            else:

                # notify the tester
                self.sendNotify( request=request, data={ 'command-name': request['data']['command-name'],
                                                        'command-id': request['data']['command-id'],
                                                        'command-result': False,
                                                        'command-value': ret }  )  
                                                                