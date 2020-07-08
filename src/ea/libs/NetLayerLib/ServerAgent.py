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

"""
Server agent module
"""

import time
import sys

from ea.libs.NetLayerLib import TransactionManager
from ea.libs.NetLayerLib import Messages
from ea.libs.NetLayerLib import TcpServer

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class ServerAgent(TcpServer.TcpServerThread,
                  TransactionManager.TransactionManager):
    """
    Server agent
    """

    def __init__(self, listeningAddress, agentName, inactivityTimeout=60,
                 keepAliveInterval=40, responseTimeout=30.0,
                 selectTimeout=0.01, wsSupport=False, sslSupport=False,
                 certFile='', keyFile='', pickleVer=2):
        """
        @param listeningAddress:
        @type listeningAddress:

        @param agentName:
        @type agentName:
        """
        TcpServer.TcpServerThread.__init__(self,
                                           listeningAddress,
                                           inactivityTimeout=inactivityTimeout,
                                           keepAliveInterval=keepAliveInterval,
                                           selectTimeout=selectTimeout,
                                           wsSupport=wsSupport,
                                           sslSupport=sslSupport,
                                           certFile=certFile,
                                           keyFile=keyFile)
        self.__responseCmdTimeout = responseTimeout
        TransactionManager.TransactionManager.__init__(self)
        self.__codec = Messages.Messages(userId=agentName, pickleVer=pickleVer)
        self.__listeningAddress = listeningAddress
        self.__agentName = agentName
        self.started = False

    def startSA(self):
        """
        Start server agent
        """
        if not self.started:
            TransactionManager.TransactionManager.start(self)
            TcpServer.TcpServerThread.start(self)
            self.started = True

    def stopSA(self):
        """
        Stop server agent
        """
        if self.started:
            TransactionManager.TransactionManager.stop(self)
            TcpServer.TcpServerThread.stop(self)
            self.started = False

    def notify(self, client, data):
        """
        Send a notify

        @param data:
        @type data:
        """
        try:
            tid = TransactionManager.TransactionManager.getNewTransactionId(
                self)
            encoded = self.__codec.notify(tid=tid, body=data)
            TcpServer.TcpServerThread.sendPacket(self, client, encoded)
            self.trace("-> NOTIFY %s" % tid)
        except Exception as e:
            self.error('[notify] request error %s' % str(e))

    def cmd(self, client, data, timeout=0.0):
        """
        Send a command

        @param client:
        @type client:

        @param data:
        @type data:

        @param timeout:
        @type timeout: float
        """
        try:
            ret = None
            tid, event = TransactionManager.TransactionManager.newTransaction(self,
                                                                              waitResponse=True,
                                                                              client=client)
            encoded = self.__codec.cmd(tid=tid, body=data)
            TcpServer.TcpServerThread.sendPacket(self, client, encoded)
            maxTime = self.__responseCmdTimeout
            if timeout > 0:
                maxTime = timeout
            self.trace("-> REQUEST %s, timeout of %s" % (tid, maxTime))
            ret = TransactionManager.TransactionManager.waitResponse(self,
                                                                     event,
                                                                     tid,
                                                                     client=client,
                                                                     responseTimeout=maxTime)
        except Exception as e:
            self.error('[cmd] %s' % str(e))
        return ret

    def handlePacket(self, client, packet):
        """
        Handle incoming packet

        @param client:
        @type client:

        @param packet:
        @type packet:
        """
        try:
            if len(packet):
                decoded = self.__codec.decode(msgraw=packet)
                TransactionManager.TransactionManager.onMessage(
                    self, decoded, client)
        except Exception as e:
            self.error('[handlePacket] got an unknown message, %s' % str(e))

    def failed(self, client, tid, body=None):
        """
        Send a failed message

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        try:
            rspEncoded = self.__codec.failed(tid=tid, body=body)
            TcpServer.TcpServerThread.sendPacket(self, client, rspEncoded)
            self.trace("-> 400 FAILED %s" % tid)
        except Exception as e:
            self.error('[failed] reply error %s' % str(e))

    def forbidden(self, client, tid, body=None):
        """
        Send a forbidden message

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        try:
            rspEncoded = self.__codec.forbidden(tid=tid, body=body)
            TcpServer.TcpServerThread.sendPacket(self, client, rspEncoded)
            self.trace("-> 403 OK %s" % tid)
        except Exception as e:
            self.error('[forbidden] reply error %s' % str(e))

    def ok(self, client, tid, body=None):
        """
        Send an ok message

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        try:
            rspEncoded = self.__codec.ok(tid=tid, body=body)
            TcpServer.TcpServerThread.sendPacket(self, client, rspEncoded)
            self.trace("-> 200 OK %s" % tid)
        except Exception as e:
            self.error('[ok] reply error %s' % str(e))

    def onResponse(self, client, tid, response):
        """
        You should override this method

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        pass

    def onRequest(self, client, tid, request):
        """
        You should override this method

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        pass

    def get_timestamp(self):
        """
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) \
            + ".%3.3d" % int((time.time() * 1000) % 1000)
        return timestamp

    def trace(self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        if __debug__:
            print("%s | [%s] %s" % (self.get_timestamp(),
                                    self.__class__.__name__,
                                    unicode(txt).encode('utf-8'))
                  )

    def error(self, err):
        """
        Display error

        @param err:
        @type err:
        """
        sys.stderr.write("%s | [%s] %s\n" % (
            self.get_timestamp(),
            self.__class__.__name__,
            err
        )
        )

    def warning(self, war):
        """
        Display warning

        @param err:
        @type err:
        """
        print("%s | [%s] %s" % (
            self.get_timestamp(),
            self.__class__.__name__,
            unicode(war).encode('utf-8'))
        )
