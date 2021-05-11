#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
