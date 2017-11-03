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
Dummy probe
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings

import sys

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__WITH_IDE__ = False  
__RESUME__ = """Example, just a dummy probe.
This probe enables to start or stop an action and to send the result to the test server."""
__TOOL_TYPE__ = GenericTool.TOOL_PROBE
__TYPE__="""dummy"""
__DESCRIPTION__="""Example, just a dummy probe.
This probe enables to start or stop an action and to send the result to the test server.

Command messages:
    - start (callid, tid, data)
    - stop (tid, data)

On start, various data can be received from args variable from the server, example:
    {'replay-id': 1, 'result-path': '...', 'cmd': 2, 'name': '...', 'args': {...} }
On stop command, various can also send to the server through http

This probe must be deployed on the target machine.
Targetted operating system: Windows, Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport=True):
    """
    Wrapper to initialize the object agent
    """
    return Dummy( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    
class Dummy(GenericTool.Tool):
    """
    Dummy probe
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=0, 
                        proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Dummy probe

        @param controllerIp:
        @type controllerIp:

        @param controllerPort:
        @type controllerPort:

        @param toolName:
        @type toolName:

        @param toolDesc:
        @type toolDesc:

        @param defaultTool:
        @type defaultTool:
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                                    supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, 
                                    sslSupport=sslSupport, toolType = "Probe")
        self.__type__ = __TYPE__
        self.probestarted = False

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
        Returns probe type

        @return:
        @rtype:
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
        self.probestarted = True
        self.onToolLogWarningCalled(msg="Start called")
        self.onToolLogWarningCalled(msg="Data received: %s" % data['args'])
        ret = {}   
        # response ok
        ret['callid'] = GenericTool.CALL_FAILED

        # create a temp file
        __outputFile = "%s/%s/dummy.txt" % ( self.__tmpPath__ , callid )
        f = open(__outputFile,'w')
        f.write('hello world')
        f.close()

        # response ok
        ret['callid'] = callid
        self.startResponse( tid, ret )

    def onStop (self, tid, data):
        """
        Reimplemented from Probe

        @param tid:
        @type tid:

        @param data:
        @type data:
        """

        ret = {}
        ret['callid'] = 0

        if not self.probestarted:
            self.stopResponse(tid, ret, data, dataToSend=False)
            return
            
        self.probestarted = False
        self.onToolLogWarningCalled(msg="Stop called")

        # send response and data too
        # the temp file created during the start is automatically sent to the server
        self.onToolLogWarningCalled(msg="Uploading logs")
        self.stopResponse(tid, ret, data)