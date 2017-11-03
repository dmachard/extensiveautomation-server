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
Textual probe
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings

import subprocess
import shlex
import time
import os
import signal
import sys

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__WITH_IDE__ = False  
__RESUME__ = """This probe enables to watch log files or logs in real-time.
Multiple files can be watched at once."""
__TOOL_TYPE__ = GenericTool.TOOL_PROBE
__TYPE__="""textual"""
__DESCRIPTION__="""This probe enables to watch log files or logs in real-time.
Multiple files can be watched at once.

Command messages:
    - start (callid, tid, data)
    - stop (tid, data)

This probe must be deployed on the target machine.
Targetted operating system: Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport=True):
    """
    Wrapper to initialize the object probe
    """
    return Textual( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport)
    
class Textual(GenericTool.Tool):
    """
    Textual probe class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool,
                    supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Constructor for probe
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, 
                    defaultTool, supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, 
                    sslSupport=sslSupport, toolType = "Probe")
        self.__type__ = __TYPE__
        self.__args__ = [ 'files' ]
        self.binTail = Settings.get( 'BinLinux', 'tail' )
        self.__pids__ = {}
    
    def getType(self):
        """
        Return the probe type
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
        """
        pass
        
    def initAfterRegistration(self):
        """
        Initialize the probe after the registration
        """
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
        
    def onResetProbeCalled(self):
        """
        Function to reimplement
        """
        pass
        
    def onToolLogWarningCalled(self, msg):
        """
        Logs warning on main application

        @param msg:
        @type msg:
        """
        pass

    def onToolLogErrorCalled(self, msg):
        """
        Logs error on main application

        @param msg:
        @type msg:
        """
        pass
        
    def onToolLogSuccessCalled(self, msg):
        """
        Logs success on main application

        @param msg:
        @type msg:
        """
        pass
        
    def getFileName(self, completePath):
        """
        Return filename extracted from the provided path
        """
        fileName = completePath.rsplit('/', 1)
        if len(fileName) == 1:
            fileName = fileName[0]
        elif len(fileName) > 1:
            fileName = fileName[1]
        return fileName


    def onStart (self, callid, tid, data):
        """
        Reimplemented from Probe

        @param callid:
        @type callid:

        @param tid:
        @type tid:

        @param data:
        @type data:
        """
        ret = {}
        ret['callid'] = GenericTool.CALL_FAILED
        try:
            if sys.platform == "win32":
                self.error( 'Platform not yet supported: %s' % sys.platform )
                self.onToolLogErrorCalled("The request can be performed - platform not yet supported!")
                
            # BEGIN - Issue 103 - DM
            # check if the binary tailf is present on the system 
            if not os.path.exists( self.binTail ):
                raise Exception('tail binary is not installed')
            # END - Issue 103 - DM

            params =  data['args']
            self.info( "starting tailfs " )
            filesToWatch = []
            if 'files' in params:
                for f in params['files']:
                    filesToWatch.append(f) 
            #
            self.__pids__[ callid ] = []
            for f in filesToWatch:
                __fileName = self.getFileName( completePath= f )
                __outputFile = "%s/%s/%s" % ( self.__tmpPath__ , callid, __fileName )
                self.trace( __outputFile )
                __cmd = "%s -f %s" % ( self.binTail, f  )
                self.trace( __cmd )
                try:
                    __cmd_args = shlex.split(__cmd)
                    p = subprocess.Popen(__cmd_args,
                            stdin=open( __outputFile,"a", 0 ),
                            stdout=open( __outputFile,"a", 0 ) ,
                            stderr=open( __outputFile,"a", 0 )
                        )
                    self.__pids__[ callid ].append( p.pid )             
                except Exception as e:
                    self.error( "[onStart] call cmd error: %s" %  str(e) )
            #time.sleep(0.20)
            self.info( "tailf started " )
            ret['callid'] = callid
        except Exception as e:
            self.error( "[onStart] %s" % str(e) )               
        self.startResponse( tid, ret )

    def onStop (self, tid, data):
        """
        Reimplemented from Probe

        @param tid:
        @type tid:

        @param data:
        @type data:
        """
        self.info( "stopping tailfs " )
        # Terminate all process
        ret = {'callid': None }
        if not data['callid'] in self.__pids__:
            # nothing todo
            self.trace( "already stopped" )
            self.stopResponse(tid, ret, data, dataToSend=False)
        else:
            pids = self.__pids__[ data['callid'] ]
            self.trace( 'pid to stop: %s' % str(pids) )
            #
            try:
                for p_id in pids:
                    try:
                        os.kill(p_id, signal.SIGKILL)
                        os.wait()
                    except Exception as e:
                        self.error( "Unable to kill %d: %s" % (p_id, str(e)) )
                ret['callid'] = 0
                self.info( "tailf stopped " )
                self.__pids__.pop( data['callid'] )
            except Exception as e:
                self.error( "[onStop] %s" % str(e) )

            # finalize
            self.stopResponse(tid, ret, data)
