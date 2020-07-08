#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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


from ea.testexecutorlib import TestSettings
from ea.libs.NetLayerLib import ClientAgent as NetLayerLib
import time
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class TestClientInterface(NetLayerLib.ClientAgent):
    """
    Test client interface
    """

    def __init__(self, address, name):
        """
        Constructor for the test client interface
        """

        self.DEBUG_MODE = TestSettings.get('Trace', 'level')

        NetLayerLib.ClientAgent.__init__(self,
                                         typeAgent=NetLayerLib.TYPE_AGENT_USER,
                                         agentName='TEST', startAuto=True, forceClose=False,
                                         keepAliveInterval=TestSettings.getInt(
                                             'Network', 'keepalive-interval'),
                                         inactivityTimeout=TestSettings.getInt(
                                             'Network', 'inactivity-timeout'),
                                         timeoutTcpConnect=TestSettings.getInt(
                                             'Network', 'tcp-connect-timeout'),
                                         responseTimeout=TestSettings.getInt(
                                             'Network', 'response-timeout')
                                         )
        _ip, _port = address
        self.setServerAddress(ip=_ip, port=_port)
        self.__test_name = name

    def onRequest(self, client, tid, request):
        """
        On request
        """
        pass

    def trace(self, txt):
        """
        Display txt on screen
        """
        if self.DEBUG_MODE == 'DEBUG':
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) \
                + ".%3.3d" % int((time.time() * 1000) % 1000)
            print(
                "%s | [%s] %s" %
                (timestamp,
                 self.__class__.__name__,
                 unicode(txt).encode('utf-8')))


TCI = None


def instance():
    """
    Return instance
    """
    return TCI


def initialize(address, name):
    """
    Initiliaze
    """
    global TCI
    TCI = TestClientInterface(address=address, name=name)
    instance().startCA()


def finalize():
    """
    Finalize
    """
    instance().stopCA()
    global TCI
    if TCI:
        TCI = None
