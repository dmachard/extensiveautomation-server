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
User client interface
"""

# import standard modules
import sys
import time
import base64
import zlib
import hashlib
import copy
import os
import urllib
import json
from threading import Thread

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtCore import (QObject, pyqtSignal)
except ImportError:
    from PyQt5.QtCore import (QObject, pyqtSignal)
    
from Libs import PyBlowFish, QtHelper, Logger
import Libs.NetLayerLib.ClientAgent as NetLayerLib
import Libs.NetLayerLib.Messages as Messages

import UserClientInterface as UCI
import Settings

class TestsPool(QObject, Logger.ClassLogger):
    """
    Tests pool class
    """
    Run = pyqtSignal(tuple)  
    Notify = pyqtSignal(tuple)  
    def __init__(self, parent = None):
        """
        Constructor
        """
        QObject.__init__(self, parent)
        self.parent = parent
        self.tests = []

    def newChannel(self, testId):
        """
        Create a new channel
        """
        test = TestClientInterface( parent = self.parent )
        test.setServerAddress(ip = UCI.instance().addressResolved, port = int(UCI.instance().portData) )
        
        test.onConnectionSuccessful = self.onConnectionSuccessful
        test.onWsHanshakeSuccess = self.onWsHanshakeSuccess
        test.onRequest = self.onRequest
        test.startCA()

        self.tests.append( (testId,test) ) 
        test.startConnection()
    
    def onConnectionSuccessful(self, instance):
        """
        On connection successful
        """
        websocketSupport = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' ))
        websocketSsl = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' ))
        if websocketSupport:
            self.trace('Websocket initialization...')
            wspath = Settings.instance().readValue( key = 'Server/websocket-path' )
            if websocketSsl:
                wspath = Settings.instance().readValue( key = 'Server/websocket-secure-path' )
            instance.handshakeWebSocket(resource=wspath, hostport=UCI.instance().address)
            
    def onWsHanshakeSuccess(self, instance):
        """
        On websocket handshake success
        """
        pass
    
    def onRequest(self, client, tid, request, instance):
        """
        On request
        """
        if request['cmd'] == Messages.RSQ_NOTIFY:
            if  request['body'][0] == 'reg':
                self.Run.emit( request['body'][1]['channel-id'] )
            else:
                self.Notify.emit( request['body'] )
        
    def closeAll(self):
        """
        Close all
        """
        for testId, test in self.tests:
            test.closeConnection()
            test.stopCA()
            
class TestClientInterface(QObject, Logger.ClassLogger, NetLayerLib.ClientAgent):
    """
    User client interface
    """
    Notify = pyqtSignal(tuple)  
    def __init__(self, parent = None):
        """
        Qt Class User Client Interface
        Signals:
         * Notify

        @param parent: 
        @type parent:
        """
        QObject.__init__(self, parent)
        NetLayerLib.ClientAgent.__init__(self, typeAgent = NetLayerLib.TYPE_AGENT_USER,
                            keepAliveInterval=int(Settings.instance().readValue( key = 'Network/keepalive-interval' )), 
                            inactivityTimeout=int(Settings.instance().readValue( key = 'Network/inactivity-timeout' )),
                            timeoutTcpConnect=int(Settings.instance().readValue( key = 'Network/tcp-connect-timeout' )),
                            responseTimeout=int(Settings.instance().readValue( key = 'Network/response-timeout' )),
                            selectTimeout=float(Settings.instance().readValue( key = 'Network/select-timeout' )),
                            sslSupport=QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' )),
                            wsSupport=QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' )),
                            pickleVer=int(Settings.instance().readValue( key = 'Network/pickle-version' )),
                            tcpKeepAlive=QtHelper.str2bool(Settings.instance().readValue( key = 'Network/tcp-keepalive' )), 
                            tcpKeepIdle=int(Settings.instance().readValue( key = 'Network/tcp-keepidle' )),
                            tcpKeepCnt=int(Settings.instance().readValue( key = 'Network/tcp-keepcnt' )), 
                            tcpKeepIntvl=int(Settings.instance().readValue( key = 'Network/tcp-keepintvl' ))
                        )
        self.parent = parent

TCI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return TCI

def initialize (parent):
    """
    Initialize the class UserClientInterface

    @param parent:
    @type: parent:

    @param clientVersion:
    @type: clientVersion:
    """
    global TCI
    TCI = TestsPool(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global TCI
    if TCI:
        del TCI
        TCI = None