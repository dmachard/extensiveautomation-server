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
Init the tool
"""

from Libs import Logger, Settings

import sys
import time
import inspect
import sys
import os
import threading


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
arg = sys.argv[0]
pathname = os.path.dirname(arg)
path_install = os.path.abspath(pathname)

settingsFile = '%s/settings.ini' % path_install
if not os.path.exists(settingsFile):
    print('config file settings.ini doesn\'t exist.')
    sys.exit(-1)

Settings.initialize()

# loading all plugins
plugins = {}
# for pluginID, pluginName in Settings.getItems('Plugins'):
for pluginName in dir(__import__( "Embedded" )):
    if not pluginName.startswith('__') and not pluginName.endswith('__'):
        pkg =  __import__( "Embedded.%s" % pluginName )
        for listing in dir(pkg):
            obj = getattr(pkg, listing)
            if inspect.ismodule(obj):
                plugins[(obj.__TOOL_TYPE__,obj.__TYPE__)] = obj

try:
    import Toolbox.Embedded as ToolPlugins
except Exception as e:
    import Embedded as ToolPlugins

RETURN_CONFIG               =   -1
RETURN_TYPE_UNKNOWN         =   -2
RETURN_ERR                  =   -3

class Tool(object):
    """
    Toolbox object handler
    """
    def __init__(self): 
        """
        Constructor for toolbox class
        """
        self.maxReconnect = int(Settings.get('Server','max-reconnect'))
        self.currentReconnect = 0
        self.timersList = []
        self.defaultTool = False
        
    def initialize (self, ip, port, type, name, descr, defaultTool, supportProxy=False,
                    proxyIp=None, proxyPort=None, sslSupport=True, isAgent=0, fromCmd=False):
        """
        Initialize the tool

        @param ip:
        @type ip: 

        @param type:
        @type type: 

        @param name:
        @type name: 

        @param descr:
        @type descr: 
        """
        self.running = False
        self.defaultTool = defaultTool
        self.tool = None
        if not Settings.cfgFileIsPresent():
            sys.stdout.write( " (config file doesn't exist)" )
            sys.exit(RETURN_CONFIG)

        try:
            Settings.initialize()
            Logger.initialize( logPathFile = "%s/%s/%s.log" % (Settings.getDirExec(), Settings.get('Paths', 'logs'), name)  )
            if (isAgent, str(type)) in plugins:
                self.info( "Initialize %s tool type=%s..." % (type,isAgent) )
                
                if not len(ip): raise Exception("No controller ip specified!")
                if not len(name): raise Exception("No tool name specified!")
                
                self.tool = plugins[(isAgent, str(type))].initialize( 
                                                        controllerIp=str(ip), toolName=str(name), toolDesc=str(descr), 
                                                        defaultTool=defaultTool, controllerPort=int(port), supportProxy=supportProxy,
                                                        proxyIp=str(proxyIp), proxyPort=proxyPort, sslSupport=sslSupport
                                                    )
                self.tool.setFromCmd()
                
                self.tool.onRegistrationSuccessful = self.onRegistrationSuccessful
                self.tool.onRegistrationFailed = self.onRegistrationFailed
                self.tool.onRegistrationRefused = self.onRegistrationRefused
                self.tool.onToolWarningCalled = self.onToolLogWarningCalled
                self.tool.onToolLogErrorCalled = self.onToolLogErrorCalled
                self.tool.onToolDisconnection = self.onToolDisconnection
                self.tool.onConnectionRefused = self.onConnectionRefused
                self.tool.onConnectionTimeout = self.onConnectionTimeout
                self.tool.onProxyConnectionTimeout = self.onProxyConnectionTimeout
                self.tool.onProxyConnectionRefused = self.onProxyConnectionRefused
                self.tool.onProxyConnectionError = self.onProxyConnectionError
                self.tool.checkPrerequisites()
                self.tool.startCA()
            else:
                self.error('tool type unknown: %s' % type)
                self.finalize(RETURN_TYPE_UNKNOWN)
        except Exception as e:
            self.error("unable to start tool: " + str(e))
            try:
                Settings.finalize()
            except: pass
            Logger.finalize()

        else:
            # run in loop
            self.running = True
            self.run()
        
    def onToolDisconnection(self, byServer=False, inactivityServer=False):
        """
        On tool disconnection
        """
        if self.currentReconnect > 0:
            if self.currentReconnect <= self.maxReconnect:
                self.currentReconnect += 1
                self.info( 'Connection retry #%s' % self.currentReconnect )
                self.restartTool()
            else:
                self.info( 'Max connection retries reached' )
                self.setReturnCode()
        else:
            if Settings.get('Server','reconnect-on-disconnect') =="True":
                if ((byServer or inactivityServer) and not self.defaultTool):
                    self.currentReconnect += 1
                    self.info( 'Connection retry #%s' % self.currentReconnect )
                    self.restartTool()
                else:
                    self.setReturnCode()
            else:
                self.setReturnCode()
                
    def restartTool(self):
        """
        Restart tool
        """
        if self.running:
            # stop the plugin before to restart
            self.info("Stopping the plugin before to restart" )
            self.tool.onPreCleanup()
            
            # init the interval, exponential restart
            # 0       1         2           3           4
            # 0 ----> 5s -----> 15s ------> 30s ------> 50s 
            # 0       5s        10s         15s         20s
            # max: 5s x 10 = 50s
            interval = int(Settings.get('Server','initial-retry'))
            interval = interval * self.currentReconnect
            
            self.info("Sleeping %s sec before to restart" % interval )
            
            # start timer
            t = threading.Timer(interval, self.tool.startConnection)
            self.timersList.append( t )
            t.start()
        
    def onToolLogWarningCalled(self, msg):
        """
        On tool log warning called
        """
        self.info(msg)
    
    def onToolLogErrorCalled(self, msg):
        """
        On tool log error called
        """
        self.error(msg)
    
    def onRegistrationRefused(self, err):
        """
        On registration refused
        """
        self.error( "Registration refused!")
        self.running = False
        
    def onRegistrationSuccessful(self):
        """
        On registration successful
        """
        self.currentReconnect = 0
        self.info( "Successfully started!")
        self.tool.prepareTempDir()
        self.tool.initAfterRegistration()
        
    def onRegistrationFailed(self, err):
        """
        On registration failed
        """
        self.error( "Registration failed!")
        self.running = False

    def onConnectionRefused(self, err):
        """
        On connection refused
        """
        self.error( "Connection refused!")
        if Settings.get('Server','reconnect-on-refused') =="True":
            if self.currentReconnect > 0:
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    self.info( 'Connection retry #%s' % self.currentReconnect )
                    self.restartTool()
                else:
                    self.info( 'Max connection retries reached' )
                    self.running = False
            else:
                self.running = False
        else:
            self.running = False
        
    def onConnectionTimeout(self, err):
        """
        On connection timeout
        """
        self.error( "Connection timeout!")
        if Settings.get('Server','reconnect-on-timeout') =="True":
            if self.currentReconnect > 0:
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    self.info( 'Connection retry #%s' % self.currentReconnect )
                    self.restartTool()
                else:
                    self.info( 'Max connection retries reached' )
                    self.running = False
            else:
                self.running = False
        else:
            self.running = False

    def onProxyConnectionRefused(self, err):
        """
        On proxy connection refused
        """
        self.error( "Proxy connection refused!")
        if Settings.get('Server','reconnect-on-refused') =="True":
            if self.currentReconnect > 0:
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    self.info( 'Connection retry #%s' % self.currentReconnect )
                    self.restartTool()
                else:
                    self.info( 'Max connection retries reached' )
                    self.running = False
            else:
                self.running = False
        else:
            self.running = False
        
    def onProxyConnectionTimeout(self, err):
        """
        On proxy connection timeout
        """
        self.error( "Proxy connection timeout!")
        if Settings.get('Server','reconnect-on-timeout') =="True":
            if self.currentReconnect > 0:
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    self.info( 'Connection retry #%s' % self.currentReconnect )
                    self.restartTool()
                else:
                    self.info( 'Max connection retries reached' )
                    self.running = False
            else:
                self.running = False
        else:
            self.running = False
            
    def onProxyConnectionError(self, err):
        """
        On proxy connection error
        """
        self.error( "Proxy connection error!")
        if Settings.get('Server','reconnect-on-error') =="True":
            if self.currentReconnect > 0:
                if self.currentReconnect <= self.maxReconnect:
                    self.currentReconnect += 1
                    self.info( 'Connection retry #%s' % self.currentReconnect )
                    self.restartTool()
                else:
                    self.info( 'Max connection retries reached' )
                    self.running = False
            else:
                self.running = False
        else:
            self.running = False
        
    def status(self):
        """
        Status
        """
        pass

    def finalize(self, errCode=RETURN_ERR):
        """
        Stops all modules

        @param errCode:
        @type errCode: 
        """
        try:
            self.running = False
            if self.tool is not None:
                self.tool.onPreCleanup()
                self.tool.stopCA()
            self.info('Return code: %s' % errCode)
        except Exception as e:
            pass
        sys.exit(errCode)

    def run(self):
        """
        On run
        """
        try:
            while self.running:
                time.sleep(0.01)
            self.finalize()
        except KeyboardInterrupt:
            self.info('Keyboard interrupt from user detected')
            # reset timers
            for timer in self.timersList:
                timer.cancel()
            # and finalize
            self.finalize()

    def setReturnCode(self):
        """
        Set the return code
        """
        self.info('Set the final return code')
        if self.tool is not None:
            self.finalize( errCode=self.tool.getLastError() )

    def info (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        Logger.info( "[%s] %s" % (self.__class__.__name__, unicode(txt).encode('utf-8') ) )

    def trace (self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        Logger.debug( "[%s] %s" % (self.__class__.__name__, unicode(txt).encode('utf-8') ) )

    def error (self, err):
        """
        Log error

        @param err:
        @type err:
        """
        Logger.error( "[%s] %s" % ( self.__class__.__name__, unicode(err).encode('utf-8') ) )
    
TOOLBOX = None # singleton
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    global TOOLBOX
    return TOOLBOX

def start(serverIp, serverPort, toolType, toolName, toolDescr, defaultTool=False, supportProxy=False, 
                    proxyIp=None, proxyPort=None, sslSupport=True, isAgent=0, fromCmd=True):
    """
    Start the tool
    
    @param serverIp:
    @type serverIp: 

    @param toolType:
    @type toolType: 

    @param toolName:
    @type toolName: 

    @param toolDescr:
    @type toolDescr: 
    """
    instance().initialize(serverIp, serverPort, toolType, toolName, toolDescr, defaultTool,
                            supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, 
                            sslSupport=sslSupport, isAgent=isAgent, fromCmd=fromCmd)

def stop():
    """
    Finalize the tool
    """
    
    instance().finalize()

def status():
    """
    Return the status of the tool
    """
    instance().status()

def initialize ():
    """
    Instance creation

    @param txt:
    @type txt: 
    """
    global TOOLBOX
    TOOLBOX = Tool() 