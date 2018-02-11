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
Network probe
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings

import time
import sys
import shlex
import subprocess
import os
import signal

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__WITH_IDE__ = False  
__RESUME__ = """This probe enables to dump traffic on a network.
Multiple network interface can be dumped at once with filter support"""
__TOOL_TYPE__ = GenericTool.TOOL_PROBE
__TYPE__="""network"""
__DESCRIPTION__="""This probe enables to dump traffic on a network.
Multiple network interface can be dumped at once with filter support.
Tcpdump or tshark must be present on the machine.

Command messages:
    - start (callid, tid, data)
    - stop (tid, data)

This probe can be deployed on server or on the target machine.
Targetted operating system: Windows, Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                supportProxy, proxyIp, proxyPort, sslSupport=True):
    """
    Wrapper to initialize the object
    """
    return Network( controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                    supportProxy, proxyIp, proxyPort, sslSupport)
    
class Network(GenericTool.Tool):
    """
    Network class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                    supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Network constructor
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, 
                    defaultTool, supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort,
                    sslSupport=sslSupport, toolType = "Probe")
        self.__type__ = __TYPE__
        self.__args__ = [ 'interfaces' ]
        self.binTcpdump = Settings.get( 'BinLinux', 'tcpdump' )
        self.binTshark = Settings.get( 'BinWin', 'tshark' )
        self.__pids__ = {}
        if sys.platform == "win32" :
            self.detectTshark()
        else:
            self.detectTcpdump()
        
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
        
    def detectTcpdump(self):
        """
        Detect tcpdump
        """
        if not os.path.exists( self.binTcpdump ):
            raise Exception('tcpdump binary is not installed')

    def detectTshark(self):
        """
        Detect tshark
        """
        if not os.path.isfile( self.binTshark ):
            raise Exception('tshark is not installed')
            
    def initAfterRegistration(self):
        """
        List all interface on windows
        """
        # list interface available
        if sys.platform == "win32" : 
            self.onToolLogWarningCalled(">> Listing network interfaces")
            __cmd__ = '"%s" -D' % (self.binTshark)
            __cmd_args__ = shlex.split(__cmd__)
            p = subprocess.Popen(__cmd_args__, stdout=subprocess.PIPE, shell=True )
            out, err = p.communicate()
            for line in out.splitlines():
                if sys.version_info > (3,):
                    self.onToolLogWarningCalled( str(line, "utf8") )
                else:
                    self.onToolLogWarningCalled( str(line) )
        self.onPluginStarted()
        
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

    def onStart (self, callid, tid, data):
        """
        Reimplemented

        @param tid:
        @type tid:

        @param args:
        @type args:
        """
        ret = {}
        ret['callid'] = GenericTool.CALL_FAILED
        try:
            if sys.platform == "win32":
                self.info( "starting tshark" )
            else:
                self.info( "starting tcpdump" )

            # read arguments
            ethsToDump = []
            params =  data['args']
            if 'interfaces' in params:
                for eth in params['interfaces']:
                    tpl = {'interface': 'any', 'filter': ''}
                    if 'interface' in eth:
                        tpl['interface'] = eth['interface']
                    if 'filter' in eth:
                        tpl['filter'] = eth['filter']
                    ethsToDump.append(tpl) 
            
            # start every capture
            self.__pids__[ callid ] = []
            
            if sys.platform == "win32" : self.onToolLogWarningCalled("<< Starting capture network")
            for eth in ethsToDump:
                if sys.platform == "win32" :
                    __dump_name__ = 'probe-netdump-%s.cap' % time.time()
                    __outputFile = "%s/%s/%s" % ( self.__tmpPath__ , callid, __dump_name__) 
                    __cmd__ = '"%s" -i "%s" -p -w "%s" %s' % (self.binTshark, 
                                                              eth['interface'], 
                                                              __outputFile , 
                                                              eth['filter'])
                else:
                    __dump_name__ = 'probe-netdump-%s-%s.cap' % ( eth['interface'] ,time.time() )
                    __outputFile = "%s/%s/%s" % ( self.__tmpPath__ , callid, __dump_name__) 
                    __cmd__ = "%s -i %s -s0 -nn -w %s %s" % ( self.binTcpdump, 
                                                              eth['interface'], 
                                                              __outputFile, 
                                                              eth['filter'])
                    
                self.trace( "[onStart] %s" % __cmd__ )
                try:
                    __cmd_args__ = shlex.split(__cmd__)
                    if sys.platform == "win32" :
                        p = subprocess.Popen(__cmd_args__, 
                                             stdin=sys.stdout, 
                                             stdout=sys.stdout, 
                                             stderr=sys.stdout, 
                                             shell=True )
                    else:
                        p = subprocess.Popen(__cmd_args__, 
                                             stdin=sys.stdout, 
                                             stdout=sys.stdout, 
                                             stderr=sys.stdout )
                    if sys.platform == "win32":  time.sleep(5.0)
                    self.__pids__[ callid ].append( p.pid )             
                except Exception as e:
                    self.error( "[onStart] call cmd error: %s" %  str(e) )
            
            if sys.platform == "win32":
                self.info( "tshark started" )
            else:
                self.info( "tcpdump started" )
            ret['callid'] = callid
        except Exception as e:
            self.error( "[onStart] %s" % str(e) )               
        self.startResponse( tid, ret )

    def onStop (self, tid, data):
        """
        Reimplemented

        @param tid:
        @type tid:

        @param args:
        @type args:
        """
        if sys.platform == "win32":
            self.info( "stopping tshark" )
        else:
            self.info( "stopping tcpdump" )

        # Terminate all process
        ret = {'callid': None }
        if not data['callid'] in self.__pids__:
            # nothing todo
            self.trace( "already stopped" )
            self.stopResponse(tid, ret, data, dataToSend=False)
        else:
            pids = self.__pids__[ data['callid'] ]
            self.trace( 'pid to stop: %s' % str(pids) )
            
            try:
                if sys.platform == "win32" : self.onToolLogWarningCalled("<< Stopping capture network")
                for p_id in pids:
                    try:
                        if sys.platform == "win32":
                            os.system("taskkill /f /t /im %s" % p_id)
                        else:
                            os.kill(p_id, signal.SIGTERM) # SIGKILL
                            os.wait()
                    except Exception as e:
                        self.error( "Unable to kill %d: %s" % (p_id, str(e)) )
                ret['callid'] = 0

                if sys.platform == "win32":
                    self.trace( "tshark stopped " )
                else:
                    self.trace( "tcpdump stopped " )
                self.__pids__.pop( data['callid'] )
            except Exception as e:
                self.error( "[onStop] %s" % str(e) )
            
            time.sleep(0.25)

            # finalize
            self.stopResponse(tid, ret, data)