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
File probe
"""

import Core.GenericTool as GenericTool

import shutil
import sys
import glob

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__WITH_IDE__ = False  
__RESUME__ = """This probe enables to retrieve file like configuration file.
Multiple files can be retrieved at once."""
__TOOL_TYPE__ = GenericTool.TOOL_PROBE
__TYPE__="""file"""
__DESCRIPTION__="""This probe enables to retrieve file like configuration file.
Multiple files can be retrieved at once.

Command messages:
    - start (callid, tid, data)
    - stop (tid, data)

This probe must be deployed on the target machine.
Targetted operating system: Linux, Windows"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport=True):
    """
    Wrapper to initialize the object agent
    """
    return File( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    
class File(GenericTool.Tool):
    """
    File agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                        supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Constructor
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, 
                        defaultTool, supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, 
                        sslSupport=sslSupport, toolType = "Probe")
        self.__type__ = __TYPE__
        self.__args__ = [ 'files' ]
        self.__pids__ = {}
        
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
        
    def getType(self):
        """
        Return the agent type
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
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
        self.onToolLogWarningCalled(msg="Start called")
        ret = {}
        ret['callid'] = GenericTool.CALL_FAILED
        try:
            params =  data['args']
            self.info( "starting copy files " )
            filesToCopy = []
            if 'files' in params:
                for f in params['files']:
                    filesToCopy.append(f) 
            #
            self.__pids__[ callid ] = []
            if sys.platform == "win32" :
                __outputFile = "%s\\%s\\" % ( self.__tmpPath__ , callid )
            else:
                __outputFile = "%s/%s/" % ( self.__tmpPath__ , callid )
            for f in filesToCopy:
                self.onToolLogWarningCalled(msg="Get file: %s" % f)
                for f_iter in glob.glob(f.strip()):
                    shutil.copy( src=f_iter, dst=__outputFile )
                
            self.info( "copy successful" )
            ret['callid'] = callid
        except Exception as e:
            self.error( "[onStart] %s" % str(e) )     
            self.onToolLogErrorCalled(msg="%s" % e)
        self.startResponse( tid, ret )

    def onStop (self, tid, data):
        """
        Reimplemented

        @param tid:
        @type tid:

        @param data:
        @type data:
        """
        self.onToolLogWarningCalled(msg="Stop called")
        self.info( "stopping..." )
        ret = {'callid': 0 }
        if not data['callid'] in self.__pids__:
            # nothing todo
            self.trace( "already stopped" )
            self.stopResponse(tid, ret, data, dataToSend=False)
        else:
            self.onToolLogWarningCalled(msg="Uploading result to the center")
            self.__pids__.pop( data['callid'] )
            self.stopResponse(tid, ret, data)
            self.info( "stopped..." )