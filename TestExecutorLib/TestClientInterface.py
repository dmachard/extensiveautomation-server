#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
# This file is part of the extensive automation project
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

try:
    import Libs.NetLayerLib.ClientAgent as NetLayerLib
    import TestSettings
except ImportError: # python3 support
    from Libs.NetLayerLib import ClientAgent as NetLayerLib
    from . import TestSettings
    
import time

class TestClientInterface(NetLayerLib.ClientAgent):
    """
    Test client interface
    """
    def __init__(self, address, name):
        """
        Constructor for the test client interface

        @param address:
        @type address:
        
        @param name:
        @type name: 
        """
        NetLayerLib.ClientAgent.__init__(self, typeAgent = NetLayerLib.TYPE_AGENT_USER, 
                                        agentName = 'TEST', startAuto = True, forceClose=False,
                                        keepAliveInterval=TestSettings.getInt( 'Network', 'keepalive-interval' ), 
                                        inactivityTimeout=TestSettings.getInt( 'Network', 'inactivity-timeout' ),
                                        timeoutTcpConnect=TestSettings.getInt( 'Network', 'tcp-connect-timeout' ),
                                        responseTimeout=TestSettings.getInt( 'Network', 'response-timeout' )
                                     )
        _ip, _port = address
        self.setServerAddress( ip = _ip, port = _port)
        self.__test_name = name

    def onRequest(self, client, tid, request):
        """
        On request
        """
        pass

    def trace (self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """ 
        if __debug__:
            timestamp =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) \
                + ".%3.3d" % int((time.time() * 1000) % 1000)
            print("%s | [%s] %s" % (timestamp, self.__class__.__name__, unicode(txt).encode('utf-8')))

TCI = None

def instance():
    """
    Return instance

    @return:
    @rtype:
    """
    return TCI

def initialize( address , name):
    """
    Initiliaze

    @param address:
    @type address:

    @param address:
    @type address:
    """
    global TCI
    TestSettings.initialize()
    TCI = TestClientInterface(address = address, name = name)
    instance().startCA()

def finalize():
    """
    Finalize
    """
    instance().stopCA()
    global TCI
    if TCI:
        TCI = None
    TestSettings.finalize()
