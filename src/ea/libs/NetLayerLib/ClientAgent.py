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
Client agent module
"""

import time
import sys

from ea.libs.NetLayerLib import TransactionManager
from ea.libs.NetLayerLib import Messages
from ea.libs.NetLayerLib import TcpClient

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


TYPE_AGENT_AGENT = "Agent"
TYPE_AGENT_PROBE = "Probe"
TYPE_AGENT_USER = "User"
TYPE_AGENT_USER = "Test"

TYPE_REG_ANONYMOUS = "Anonymous"
TYPE_REG_ACCOUNT = "Account"


class ClientAgent(TcpClient.TcpClientThread,
                  TransactionManager.TransactionManager):
    """
    Client agent
    """

    def __init__(self, typeAgent, agentName=None,
                 startAuto=False, inactivityTimeout=60,
                 keepAliveInterval=40, timeoutTcpConnect=5,
                 responseTimeout=30.0, forceClose=True,
                 selectTimeout=0.01, wsSupport=False,
                 sslSupport=False, pickleVer=2,
                 regType=TYPE_REG_ANONYMOUS,
                 regLogin='', regPass='',
                 tcpKeepAlive=True, tcpKeepIdle=3,
                 tcpKeepCnt=3, tcpKeepIntvl=3):
        """
        Constructor

        @param typeAgent:
        @type typeAgent:

        @param agentName:
        @type agentName: string or None

        @param startAuto:
        @type startAuto: boolean

        @param timeoutTcpConnect:
        @type timeoutTcpConnect: float
        """
        TcpClient.TcpClientThread.__init__(self, inactivityTimeout=inactivityTimeout,
                                           keepAliveInterval=keepAliveInterval,
                                           timeout=timeoutTcpConnect,
                                           selectTimeout=selectTimeout,
                                           wsSupport=wsSupport,
                                           sslSupport=sslSupport,
                                           tcpKeepAlive=tcpKeepAlive,
                                           tcpKeepIdle=tcpKeepIdle,
                                           tcpKeepCnt=tcpKeepCnt,
                                           tcpKeepIntvl=tcpKeepIntvl)
        TransactionManager.TransactionManager.__init__(self)
        self.__responseCmdTimeout = responseTimeout
        self.__codec = Messages.Messages(userId=agentName, pickleVer=pickleVer)
        self.__agentName = agentName
        self.__localAddress = None

        self.__typeAgent = typeAgent
        self.__registered = False
        self.__startAuto = startAuto
        self.__connected = False
        self.__forceClose = forceClose

        self.regType = regType
        self.regLogin = regLogin
        self.regPass = regPass

        self.ver = None
        self.desc = None
        self.name = None

    def getTypeClientAgent(self):
        """
        Get type client
        """
        return self.__typeAgent

    def setAgentName(self, name):
        """
        Set the agent name

        @param name:
        @type name:
        """
        self.__agentName = name
        self.__codec.setUserId(name)

    def setDetails(self, name, desc, ver):
        """
        Set more details about this agent

        @param name:
        @type name:

        @param desc:
        @type desc:

        @param ver:
        @type ver:
        """
        self.ver = ver
        self.desc = desc
        self.name = name

    def isConnected(self):
        """
        Return the connection status

        @return:
        @rtype:
        """
        return self.__connected

    def isRegistered(self):
        """
        Return the registration status

        @return:
        @rtype:
        """
        return self.__registered

    def startCA(self):
        """
        Start the client agent
        """
        TransactionManager.TransactionManager.start(self)
        TcpClient.TcpClientThread.start(self)
        res = self.getLocalAddress()
        if res[0] == '':
            self.__localAddress = ('127.0.0.1', res[1])
        else:
            self.__localAddress = res
        if self.__startAuto:
            TcpClient.TcpClientThread.startConnection(self)

    def stopCA(self):
        """
        Stop the client agent
        """
        if self.__startAuto and self.__connected:
            TcpClient.TcpClientThread.closeConnection(self)
        if not self.__forceClose:
            # wait to empty the queue before to close the connection
            while self.__connected:
                time.sleep(0.01)
        TransactionManager.TransactionManager.stop(self)
        TcpClient.TcpClientThread.stop(self)
        TcpClient.TcpClientThread.join(self)

    def handleIncomingPacket(self, pdu):
        """
        Reimplementation from TcpClientThread
        """
        try:
            decoded = self.__codec.decode(msgraw=pdu)
        except Exception as e:
            self.error('unable to decode new message: %s' % str(e))
        else:
            try:
                TransactionManager.TransactionManager.onMessage(self, decoded)
            except Exception as e:
                self.error('unable to handle new message: %s' % str(e))

    def onConnection(self):
        """
        Reimplementation from TcpClientThread
        """
        self.__connected = True
        self.onConnectionSuccessful()

    def onProxyConnection(self):
        """
        Reimplementation from TcpClientThread
        """
        self.__connected = True
        self.trace('Proxy initialization...')
        try:
            self.sendProxyHttpRequest()
        except Exception as e:
            self.error('unable to init proxy: %s' % str(e))

    def doRegistration(self, cancelEvent=None):
        """
        Send a registration
        """
        self.trace('Do registration...')
        data = {
            'version': self.ver,
            'description': self.desc,
            'name': self.name,
            'type': self.__typeAgent,
            'start-at': time.time(),
            'reg-type': self.regType,
            'reg-login': self.regLogin,
            'reg-pass': self.regPass
        }

        rsp = self.hello(data, cancelEvent=cancelEvent)
        if rsp is None:
            self.trace('Registration failed, no response.')
            self.onRegistrationFailed('No response')
        elif rsp['code'] == b'403':
            self.trace('Registration refused')
            self.onRegistrationRefused(err='Registration refused')
        elif rsp['code'] == b'400':
            self.trace('Registration failed, conflict name')
            self.onRegistrationFailed(err='Conflict name')
        elif rsp['code'] == b'500':
            self.error('Server Error')
            self.onRegistrationFailed(err='Server Error')
        elif rsp['code'] == b'200':
            self.trace('Registered')
            self.__registered = True
            self.onRegistrationSuccessful()
        else:
            self.error('Unknown error on registration: %s' % rsp['code'])

    def onConnectionSuccessful(self):
        """
        On connection successful
        """
        pass

    def onDisconnection(self, byServer=False, inactivityServer=False):
        """
        Reimplementation from TcpClientThread
        """
        self.__registered = False
        self.__connected = False

    def onRegistrationRefused(self, err):
        """
        You should override this method

        @param err:
        @type err:
        """
        pass

    def onRegistrationFailed(self, err):
        """
        You should override this method

        @param err:
        @type err:
        """
        pass

    def onRegistrationSuccessful(self):
        """
        You should override this method
        """
        pass

    def bad(self, tid, body=None):
        """
        Send a bad message

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        # encode message
        try:
            rspEncoded = self.__codec.error(tid=tid, body=body)
        except Exception as e:
            self.error('unable to encode bad message: %s' % str(e))
        else:
            # send packet
            try:
                TcpClient.TcpClientThread.sendPacket(self, rspEncoded)
                self.trace("-> 500 BAD %s" % tid)
            except Exception as e:
                self.error('[failed] reply error %s' % str(e))

    def failed(self, tid, body=None):
        """
        Send a failed message

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        # encode message
        try:
            rspEncoded = self.__codec.failed(tid=tid, body=body)
        except Exception as e:
            self.error('unable to encode failed message: %s' % str(e))
        else:
            # send packet
            try:
                TcpClient.TcpClientThread.sendPacket(self, rspEncoded)
                self.trace("-> 400 FAILED %s" % tid)
            except Exception as e:
                self.error('[failed] reply error %s' % str(e))

    def forbidden(self, tid, body=None):
        """
        Send a forbidden message

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        # encode message
        try:
            rspEncoded = self.__codec.forbidden(tid=tid, body=body)
        except Exception as e:
            self.error('unable to encode forbidden message: %s' % str(e))
        else:
            # send packet
            try:
                TcpClient.TcpClientThread.sendPacket(self, rspEncoded)
                self.trace("-> 403 OK %s" % tid)
            except Exception as e:
                self.error('[forbidden] reply error: %s' % str(e))

    def ok(self, tid, body=None):
        """
        Send a ok message

        @param tid:
        @type tid:

        @param body:
        @type body:
        """
        # encode message
        try:
            rspEncoded = self.__codec.ok(tid=tid, body=body)
        except Exception as e:
            self.error('unable to encode ok message: %s' % str(e))
        else:
            # send packet
            try:
                TcpClient.TcpClientThread.sendPacket(self, rspEncoded)
                self.trace("-> 200 OK %s" % tid)
            except Exception as e:
                self.error('unable to send ok message: %s' % str(e))

    def notify(self, data):
        """
        Send a notify

        @param data:
        @type data:
        """
        # encode message
        try:
            tid = TransactionManager.TransactionManager.getNewTransactionId(
                self)
            encoded = self.__codec.notify(tid=tid, body=data)
        except Exception as e:
            self.error('unable to encode notify message: %s' % str(e))
        else:
            # send packet
            try:
                TcpClient.TcpClientThread.sendPacket(self, encoded)
                self.trace("-> NOTIFY %s" % tid)
            except Exception as e:
                self.error('[notify] request notify error %s' % str(e))

    def cmd(self, data, timeout=0.0, cancelEvent=None):
        """
        Send a command

        @param data:
        @type data:

        @param timeout:
        @type timeout: float

        @return:
        @rtype:
        """
        # encode message
        try:
            ret = None
            tid, event = TransactionManager.TransactionManager.newTransaction(
                self, waitResponse=True)
            encoded = self.__codec.cmd(tid=tid, body=data)
        except Exception as e:
            self.error('unable to encode cmd message: %s' % str(e))
        else:
            try:
                # send packet
                TcpClient.TcpClientThread.sendPacket(self, encoded)

                # wait response according to the timeout
                maxTime = self.__responseCmdTimeout
                if timeout > 0:
                    maxTime = timeout
                self.trace("-> REQUEST %s, timeout of %s" % (tid, maxTime))
                ret = TransactionManager.TransactionManager.waitResponse(
                    self, event, tid, responseTimeout=maxTime, cancelEvent=cancelEvent)
            except Exception as e:
                self.error('[cmd] %s' % str(e))
            return ret

    def hello(self, data, cancelEvent=None):
        """
        Send a hello

        @param data:
        @type data:

        @return:
        @rtype:
        """
        ret = None

        if self.__typeAgent == TYPE_AGENT_PROBE or self.__typeAgent == TYPE_AGENT_AGENT:
            self.trace('Registration...')
            tpl = {'cmd': Messages.CMD_HELLO}
            tpl.update(data)
            ret = self.cmd(data=tpl, cancelEvent=cancelEvent)
        return ret

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

    def trace(self, txt):
        """
        Display message in the screen

        @param txt: message
        @type txt: string
        """
        if __debug__:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) \
                + ".%3.3d" % int((time.time() * 1000) % 1000)
            print(
                "%s | [%s] %s" %
                (timestamp,
                 self.__class__.__name__,
                 unicode(txt).encode('utf-8')))

    def error(self, err):
        """
        Display an error

        @param err:
        @type err:
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) \
            + ".%3.3d" % int((time.time() * 1000) % 1000)
        sys.stderr.write(
            "%s | [%s]%s\n" %
            (timestamp, self.__class__.__name__, err))
