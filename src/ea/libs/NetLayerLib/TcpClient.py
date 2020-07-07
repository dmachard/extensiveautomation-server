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
Tcp client module
"""

import errno
import sys
import struct
import ssl
import time
import socket
import select
import threading

try:
    import xrange
except ImportError:  # support python3
    xrange = range

try:
    import Queue
except ImportError:  # support python 3
    import queue as Queue

from ea.libs.NetLayerLib import WebSocket

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
else:
    # these exceptions does not exist in python2.X
    class ConnectionAbortedError(Exception):
        pass

    class ConnectionRefusedError(Exception):
        pass

    class ConnectionResetError(Exception):
        pass


PROXY_TYPE_NONE = -1
PROXY_TYPE_SOCKS4 = 0
PROXY_TYPE_SOCKS5 = 1
PROXY_TYPE_HTTP = 2


class TcpClientThread(threading.Thread):
    """
    Tcp client thread
    """

    def __init__(self, serverAddress=None, localAddress=('', 0), inactivityTimeout=30,
                 keepAliveInterval=20, timeout=5, proxyAddress=None, proxyUserId=b'client',
                 selectTimeout=0.01, terminator=b'\x00',
                 sslSupport=False, sslVersion=ssl.PROTOCOL_TLSv1, checkSsl=False,
                 wsSupport=False, wsMaxPayloadSize=WebSocket.WEBSOCKET_MAX_BASIC_DATA1024,
                 tcpKeepAlive=True, tcpKeepIdle=3, tcpKeepCnt=3, tcpKeepIntvl=3):
        """
        TCP Client thread

        @param serverAddress: remote ip or hostname and port
        @type serverAddress: tuple

        @param localAddress: local bind on ip and port
        @type localAddress: tuple

        @param inactivityTimeout: default value of 30 seconds
        @type inactivityTimeout: Integer

        @param keepAliveInterval: default value of 20 seconds, ping or pong with websocket
        @type keepAliveInterval: integer

        @param timeout: default value of 5 second
        @type timeout: integer

        @param proxyAddress: proxy address
        @type proxyAddress: integer

        @param proxyUserId: default value : client
        @type proxyUserId: string

        @param selectTimeout: socket io timeout, default value of 0.01
        @type selectTimeout: integer

        @param terminator: packet terminator, default value 0x00
        @type terminator: integer

        @param wsSupport: websocket support
        @type wsSupport: boolean

        @param sslSupport: ssl support
        @type sslSupport: boolean

        @param sslVersion: default value of 1 second
        @type sslVersion: integer

        @param wsMaxPayloadSize: websocket payload size
        @type wsMaxPayloadSize: integer
        """
        threading.Thread.__init__(self)
        self.serverAddress = serverAddress
        self.proxyAddress = proxyAddress  # sock4
        self.localAddress = localAddress
        self.serverDstHostname = None

        # proxy
        self.proxyDstHostname = None
        self.proxyConnectSuccess = False
        self.proxyType = PROXY_TYPE_NONE
        self.proxyUserId = proxyUserId

        # web socket
        self.wsCodec = WebSocket.WebSocketCodec(parent=self)
        self.wsSupport = wsSupport
        if wsSupport:
            self.trace(
                'Web socket activated - version %s' %
                WebSocket.WEBSOCKET_VERSION)
        self.wsHandshakeSuccess = False
        self.wsKey = b''
        self.wsMaxPayloadSize = wsMaxPayloadSize

        # ssl
        self.sslSupport = sslSupport
        self.sslVersion = sslVersion
        self.checkSsl = checkSsl
        if sslSupport:
            self.trace('Ssl activated - version %s' % self.sslVersion)

        # buffer
        self.buf = b''
        self.bufWs = b''
        self.queue = Queue.Queue(0)
        self.event = threading.Event()
        self.socket = None
        self.running = True
        self.closeSocket = False
        self.inactivityServer = False
        self.timeout = timeout

        self.terminator = terminator
        self.keepAlivePdu = b''
        self.inactivityTimeout = inactivityTimeout
        self.keepAliveInterval = keepAliveInterval
        self.selectTimeout = float(selectTimeout)

        self.tcpKeepAlive = tcpKeepAlive
        self.tcpKeepIdle = tcpKeepIdle
        self.tcpKeepIntvl = tcpKeepIntvl
        self.tcpKeepCnt = tcpKeepCnt

        self.trace('Tcp Client Thread Initialized')

    def unsetProxy(self):
        """
        Unset the proxy
        """
        self.proxyAddress = None
        self.proxyDstHostname = None
        self.proxyConnectSuccess = False
        self.proxyType = PROXY_TYPE_NONE

    def setProxyAddress(self, ip, port):
        """
        Set the destination server address

        @param ip: destination ip address
        @type ip: string

        @param port: destination tcp port
        @type port: Integer

        @return:
        @rtype:
        """
        try:
            if not len(ip):
                return None
            self.proxyAddress = (ip, port)
            # check if ip or dns
            # (hostname, aliaslist, ipaddrlist)
            ret = socket.gethostbyname(str(ip))
            if ret != ip:
                self.proxyAddress = (ret, port)
                self.proxyDstHostname = ip
        except Exception as e:
            self.error(e)
            self.onResolveHostnameProxyFailed(err=e)
            return None
        return self.proxyAddress

    def setServerAddress(self, ip, port):
        """
        Set the destination server address

        @param ip: destination ip address
        @type ip: string

        @param port: destination tcp port
        @type port: Integer

        @return:
        @rtype:
        """
        try:
            self.serverAddress = (ip, port)
            # check if ip or dns
            # (hostname, aliaslist, ipaddrlist)
            ret = socket.gethostbyname(str(ip))
            if ret != ip:
                self.serverAddress = (ret, port)
                self.serverDstHostname = ip
        except Exception as e:
            if sys.version_info > (3,):  # python 3 support
                self.error(str(e))
                self.onResolveHostnameFailed(err=str(e))
            else:
                self.error(str(e).decode('iso-8859-15'))
                self.onResolveHostnameFailed(err=str(e).decode('iso-8859-15'))
            return None
        return self.serverAddress

    def sendProxySocks4Request(self):
        """
        Requesting socks4 proxy
        """
        self.proxyType = PROXY_TYPE_SOCKS4
        try:
            destIp, destPort = self.serverAddress
            # Construct the request packet
            ipAddr = socket.inet_aton(destIp)
            # 0x04 = version = socks4
            # 0x01 = command = connect
            req = b"\x04\x01" + struct.pack(">H", destPort) + ipAddr
            # Add userid
            req += self.proxyUserId
            # send packet
            self.sendPacket(packet=req)
        except Exception as e:
            self.error("unable to initiate proxy socks4: %s" % str(e))

    def sendProxySocks5Request(self, login=None, password=None):
        """
        Requesting socks5 proxy
        """
        self.proxyType = PROXY_TYPE_SOCKS5
        try:
            if login is not None and password is not None:  # The username/password
                req = b"\x05\x02\x00\x02"
            else:
                req = b"\x05\x01\x00"  # No username/password were entered
            # send packet
            self.sendPacket(packet=req)
        except Exception as e:
            self.error("unable to initiate proxy socks5: %s" % str(e))

    def sendProxyHttpRequest(self):
        """
        Requesting http proxy
        """
        self.proxyType = PROXY_TYPE_HTTP
        try:
            destIp, destPort = self.serverAddress
            if self.serverDstHostname is not None:
                destIp = self.serverDstHostname
            # Construct request
            reqProxy = []
            reqProxy.append("CONNECT %s:%s HTTP/1.1" % (destIp, str(destPort)))
            reqProxy.append("Host: %s:%s" % (destIp, str(destPort)))
            reqProxy.append("")
            reqProxy.append("")
            # send packet
            self.sendHttpPacket(packet="\r\n".join(reqProxy))
        except Exception as e:
            self.error("unable to initiate proxy http: %s" % e)

    def handshakeWebSocket(self, resource="/", hostport='localhost'):
        """
        Build websocket handshake and send-it
        """
        try:
            # construct handshake
            headers = []
            headers.append("GET %s HTTP/1.1" % resource)
            headers.append("Upgrade: websocket")
            headers.append("Connection: keep-alive, upgrade")
            headers.append("Host: %s" % hostport)
            headers.append("Origin: http://%s" % hostport)
            self.wsKey = self.wsCodec.createSecWsKey()
            headers.append("Sec-WebSocket-Key: %s" % self.wsKey)
            headers.append(
                "Sec-WebSocket-Version: %s" %
                WebSocket.WEBSOCKET_VERSION)
            headers.append("")
            headers.append("")

            # send packet
            self.sendHttpPacket(packet="\r\n".join(headers))
        except Exception as e:
            self.error("unable to initiate web socket: %s" % e)

    def startConnection(self, threadingConnect=True):
        """
        Start connection
        """
        if threadingConnect:
            t = threading.Thread(target=self.__startConnection)
            t.start()
        else:
            self.__startConnection()

    def __startConnection(self):
        """
        Starts TCP connection (SYN)
        """
        self.inactivityServer = False
        self.wsHandshakeSuccess = False
        self.proxyConnectSuccess = False
        if self.proxyAddress is not None:
            self.trace(
                "connecting from %s to %s with the proxy %s" %
                (str(
                    self.localAddress), str(
                    self.serverAddress), str(
                    self.proxyAddress)))
        else:
            self.trace(
                "connecting from %s to %s" %
                (str(
                    self.localAddress), str(
                    self.serverAddress)))
        try:
            self.buf = b''
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.tcpKeepAlive:
                self.socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if sys.platform == "win32":
                if self.tcpKeepAlive:
                    self.socket.ioctl(socket.SIO_KEEPALIVE_VALS,
                                      (1, self.tcpKeepIdle * 1000, self.tcpKeepIntvl * 1000))
            elif sys.platform == "darwin":
                # interval in seconds between keepalive probes
                if self.tcpKeepAlive:
                    self.socket.setsockopt(socket.SOL_TCP,
                                           socket.TCP_KEEPINTVL,
                                           self.tcpKeepIntvl)
                # failed keepalive probes before declaring the other end dead
                if self.tcpKeepAlive:
                    self.socket.setsockopt(socket.SOL_TCP,
                                           socket.TCP_KEEPCNT,
                                           self.tcpKeepCnt)
            else:
                # seconds before sending keepalive probes
                if self.tcpKeepAlive:
                    self.socket.setsockopt(socket.SOL_TCP,
                                           socket.TCP_KEEPIDLE,
                                           self.tcpKeepIdle)
                # interval in seconds between keepalive probes
                if self.tcpKeepAlive:
                    self.socket.setsockopt(socket.SOL_TCP,
                                           socket.TCP_KEEPINTVL,
                                           self.tcpKeepIntvl)
                # failed keepalive probes before declaring the other end dead
                if self.tcpKeepAlive:
                    self.socket.setsockopt(socket.SOL_TCP,
                                           socket.TCP_KEEPCNT,
                                           self.tcpKeepCnt)

            if self.sslSupport and self.proxyAddress is None:
                certReqs = ssl.CERT_NONE
                if self.checkSsl:
                    certReqs = ssl.CERT_REQUIRED
                self.socket = ssl.wrap_socket(self.socket,
                                              cert_reqs=certReqs,
                                              ssl_version=self.sslVersion)

            self.socket.settimeout(self.timeout)
            self.socket.bind(self.localAddress)
            if self.proxyAddress is not None:
                self.socket.connect(self.proxyAddress)
                self.lastActivityTimestamp = time.time()
                self.lastKeepAliveTimestamp = time.time()
                self.event.set()
                self.trace("proxy connected.")
                self.onProxyConnection()
            else:
                self.socket.connect(self.serverAddress)
                self.lastActivityTimestamp = time.time()
                self.lastKeepAliveTimestamp = time.time()
                self.event.set()
                self.trace("connected.")
                self.onConnection()
        except socket.timeout as e:
            if self.proxyAddress is not None:
                self.error("socket tcp proxy %s on connection." % (str(e)))
                self.onProxyConnectionTimeout(err=str(e))
            else:
                self.error("socket tcp %s on connection." % (str(e)))
                self.onConnectionTimeout(err=str(e))
        except Exception as e:
            if self.proxyAddress is not None:
                self.error("Proxy %s." % (str(e)))
                self.onProxyConnectionRefused(err=str(e))
            else:
                self.error("%s." % (str(e)))
                self.onConnectionRefused(err=str(e))

    def closeConnection(self):
        """
        Close TCP connection (RESET)
        """
        self.closeSocket = True

    def run(self):
        """
        Main loop
        """
        while self.running:
            self.event.wait()
            if self.running:
                try:
                    # check if we have incoming data
                    if self.socket is not None:
                        r, w, e = select.select(
                            [self.socket], [], [self.socket], self.selectTimeout)
                        if self.socket in e:
                            raise EOFError(
                                "socket select error: disconnecting")
                        elif self.socket in r:
                            read = self.socket.recv(8192)
                            if not read:
                                raise EOFError("no more data, connection lost")
                            else:
                                self.lastActivityTimestamp = time.time()
                                self.buf = b''.join([self.buf, read])
                                self.onIncomingData()

                        # Check inactivity timeout
                        elif self.inactivityTimeout:
                            if time.time() - self.lastActivityTimestamp > self.inactivityTimeout:
                                if self.proxyAddress is not None:
                                    raise EOFError(
                                        "Inactivity proxy/server timeout")
                                else:
                                    raise EOFError("Inactivity timeout")

                        if self.wsSupport:
                            # Prepare Keep-Alive if needed
                            keepAlive = False
                            if self.wsSupport and self.wsHandshakeSuccess:
                                keepAlive = True

                            if keepAlive:
                                if self.keepAliveInterval:
                                    if time.time() - self.lastKeepAliveTimestamp > self.keepAliveInterval:
                                        self.lastKeepAliveTimestamp = time.time()
                                        wsping, pingId = self.wsCodec.encodePing()
                                        self.trace(
                                            "sending ws ping message id=%s" % pingId)
                                        self.queue.put(wsping)
                        else:  # old style
                            # Prepare Keep-Alive if needed
                            keepAlive = False
                            if self.proxyAddress is not None and self.proxyConnectSuccess:
                                keepAlive = True
                            else:
                                if self.proxyAddress is None:
                                    keepAlive = True

                            # Send (queue) a Keep-Alive if needed, old style
                            if keepAlive:
                                if self.keepAliveInterval:
                                    if time.time() - self.lastKeepAliveTimestamp > self.keepAliveInterval:
                                        self.lastKeepAliveTimestamp = time.time()
                                        # self.lastActivityTimestamp = time.time()
                                        self.trace("sending keep-alive")
                                        self.sendPacket(self.keepAlivePdu)

                        # send queued messages
                        while not self.queue.empty():
                            r, w, e = select.select(
                                [], [
                                    self.socket], [
                                    self.socket], self.selectTimeout)
                            if self.socket in e:
                                raise EOFError(
                                    "socket select error when sending a message: disconnecting")
                            elif self.socket in w:
                                try:
                                    message = self.queue.get(False)
                                    self.socket.sendall(message)
                                    del message
                                except Queue.Empty:
                                    if self.closeSocket:
                                        self.event.set()
                                except Exception as e:
                                    self.error(
                                        "unable to send message: " + str(e))
                            else:
                                break
                except EOFError as e:
                    if "Inactivity timeout" in str(e):
                        self.error("disconnecting, inactivity timeout")
                        self.inactivityServer = True
                        # self.onInactivityTimeout()
                        self.event.clear()
                        self.closeSocket = True
                    else:
                        self.error("disconnected by the server: %s" % str(e))
                        self.onDisconnection(byServer=True)
                        self.event.clear()

                # new with python3
                except ConnectionAbortedError:
                    self.error("connection aborted by peer")
                    self.onDisconnection(byServer=True)
                    self.event.clear()
                except ConnectionRefusedError:
                    self.error("connection refused by peer")
                    self.onDisconnection(byServer=True)
                    self.event.clear()
                except ConnectionResetError:
                    self.error("connection reseted by peer")
                    self.onDisconnection(byServer=True)
                    self.event.clear()
                # end of new

                # new in v20, for alpine support
                except select.error as e:
                    _errno, _ = e
                    if _errno != errno.EINTR:
                        raise
                # end of new

                except Exception as e:
                    if "[Errno 10054]" in str(e):
                        self.error("connection reseted by peer")
                        self.onDisconnection(byServer=True)
                        self.event.clear()
                    else:
                        self.error("generic error on run: %s" % str(e))
                        self.closeSocket = True
                        self.event.clear()

            # close socket
            if self.closeSocket:
                self.trace("cleanup socked")
                if self.socket is not None:
                    # cleanup the queue
                    while not self.queue.empty():
                        try:
                            message = self.queue.get(False)
                            self.socket.sendall(message)
                        except Queue.Empty:
                            pass
                    # close the tcp connection
                    self.trace("closing socket")
                    self.socket.close()
                    # cleanup the buffer
                    self.buf = b''
                    self.closeSocket = False
                    self.onDisconnection(
                        inactivityServer=self.inactivityServer)
                    self.event.clear()
                    self.trace("closed")

        self.onDisconnection()

    def onIncomingData(self):
        """
        Called on incoming data
        """
        try:
            if self.running:
                # handle proxy handshake
                readTrueData = False
                if self.proxyAddress is not None and not self.proxyConnectSuccess and self.buf:
                    self.trace(
                        'data received for proxy handshake of len %s' % len(
                            self.buf))
                    readTrueData = self.decodeProxyResponse()
                    if self.proxyConnectSuccess:
                        self.onProxyConnectionSuccess()
                else:
                    readTrueData = True

                # handle websocket handshake
                readTrueData = False
                if self.wsSupport and not self.wsHandshakeSuccess and self.buf:
                    if not readTrueData and not self.proxyConnectSuccess and self.proxyAddress is not None:
                        pass
                    else:
                        self.trace(
                            'data received for ws handshake of len %s' % len(
                                self.buf))
                        readTrueData = self.decodeWsHandshake()
                        if self.wsHandshakeSuccess:
                            self.onWsHanshakeSuccess()
                else:
                    readTrueData = True

                # handle other data
                if readTrueData:  # other than proxy and websocket handshake
                    if self.wsSupport:
                        (data, opcode, left, needmore) = self.wsCodec.decodeWsData(
                            buffer=self.buf)
                        self.buf = left
                        if not needmore:
                            if opcode == WebSocket.WEBSOCKET_OPCODE_TEXT:
                                self.bufWs = b''.join([self.bufWs, data])
                            else:
                                if opcode == WebSocket.WEBSOCKET_OPCODE_PONG:
                                    self.trace(
                                        "received ws pong message id=%s" % data)
                                elif opcode == WebSocket.WEBSOCKET_OPCODE_PING:
                                    self.trace(
                                        "received ws ping message id=%s" % data)
                                    wspong = self.wsCodec.encodePong(data=data)
                                    self.queue.put(wspong)
                                    self.trace(
                                        "sending pong message id=%s" % data)
                                else:
                                    self.error(
                                        'unknown ws opcode received: %s' % opcode)

                            self.readBufferWs()
                            if len(self.buf) >= 2:
                                self.onIncomingData()

                    else:  # old style
                        self.readBuffer()

        except Exception as e:
            self.error("error on incoming data: %s" % e)

    def readBufferWs(self):
        """
        Read buffer for websocket
        """
        pdus = self.bufWs.split(self.terminator)
        for pdu in pdus[:-1]:
            self.handleIncomingPacket(pdu)
        self.bufWs = pdus[-1]

    def readBuffer(self):
        """
        Read tcp buffer
        """
        pdus = self.buf.split(self.terminator)
        for pdu in pdus[:-1]:
            if not pdu == self.keepAlivePdu:
                self.handleIncomingPacket(pdu)
            else:
                self.trace("received keep-alive from server")
        self.buf = pdus[-1]

    def decodeWsHandshake(self):
        """
        Decode websocket handshake

        @return: True if the websocket handshake is successful, False otherwise
        @rtype: boolean
        """
        readTrueData = False
        try:
            if self.buf.find(b"\r\n\r\n") != -1:
                datasplitted = self.buf.split(b"\r\n\r\n", 1)
                rsp = datasplitted[0]
                self.trace('ws complete response received')
                statusline = rsp.splitlines()[0].split(b" ", 2)
                if statusline[0] not in (b"HTTP/1.1"):
                    self.buf = b''
                    self.closeConnection()
                    self.error("Malformed HTTP ws message: %s" % statusline)
                    self.onWsHanshakeError(
                        err="Malformed HTTP message ws: %s" %
                        statusline)
                else:
                    statuscode = int(statusline[1])
                    if statuscode != 101:
                        self.buf = b''
                        self.closeConnection()
                        self.error(
                            "Handshake ws refused\nInvalid http status code: %s" %
                            statuscode)
                        self.onWsHanshakeError(
                            err="Handshake ws refused\nInvalid http status code %s" %
                            statuscode)
                    else:
                        # checking ws headers
                        if not self.wsCodec.checkingWsHeaders(
                                response=rsp, key=self.wsKey):
                            self.buf = b''
                            self.closeConnection()
                            self.error("Handshake ws refused, invalid headers")
                            self.onWsHanshakeError(err="Handshake ws refused")
                        else:
                            self.trace('Ws handshake accepted')
                            self.wsHandshakeSuccess = True
                            if len(datasplitted) > 1:
                                self.buf = datasplitted[1]
                            else:
                                self.buf = b''
                            readTrueData = True
            else:
                raise Exception('need more ws headers on response')
        except Exception as e:
            self.trace(e)
        return readTrueData

    def decodeProxyResponse(self):
        """
        Decode proxy response

        @return: True when client is ready to received application data, False otherwise
        @rtype: boolean
        """
        readTrueData = False
        try:
            # handle socks4
            if self.proxyType == PROXY_TYPE_SOCKS4:
                if ord(self.buf[0]) != 0:  # bad version on response
                    self.buf = b''
                    self.closeConnection()
                    self.error(
                        "Socks4: bad response from proxy: %s" %
                        self.buf[0])
                    self.onProxyConnectionError(
                        err="Socks4: bad response from proxy: %s" %
                        self.buf[0])
                else:
                    if ord(self.buf[1]) != 90:  # granted
                        self.buf = b''
                        self.error("Socks4 proxy refused the connection!")
                        self.closeConnection()
                        self.onProxyConnectionError(
                            err="Socks4 proxy refused the connection!")  # Server returned an error
                    else:
                        self.trace('Proxy tunnel established')
                        readTrueData = True
                        # Get the bound address/port
                        self.proxyConnectSuccess = True
                        self.buf = b''

            # handle http
            elif self.proxyType == PROXY_TYPE_HTTP:
                self.trace("http proxy activated")
                self.trace("response received: %s" % self.buf)

                # if \r\n\r\n if detected then the response if complete
                # otherwise we must wait more data
                if self.buf.find(b"\r\n\r\n") != -1:
                    # read the status line
                    statusline = self.buf.splitlines()[0].split(b" ", 2)
                    if statusline[0] not in (b"HTTP/1.0", b"HTTP/1.1"):
                        self.buf = b''
                        self.closeConnection()
                        self.error(
                            "Bad http response from proxy: %s" %
                            statusline)
                        self.onProxyConnectionError(
                            err="Bad http response from proxy: %s" % statusline)
                    else:
                        # extract the status code
                        statuscode = int(statusline[1])
                        if statuscode != 200:
                            self.buf = b''
                            self.closeConnection()
                            self.error(
                                "Http proxy refuses the connection: %s" %
                                statusline)
                            self.onProxyConnectionError(
                                err="The HTTP proxy refuses the connection!\nStatus code received: %s" %
                                statuscode)

                        else:
                            # tunnel established
                            # continue with ssl if needed
                            self.trace('Proxy tunnel established')
                            if self.sslSupport:
                                certReqs = ssl.CERT_NONE
                                if self.checkSsl:
                                    certReqs = ssl.CERT_REQUIRED
                                try:
                                    self.socket = ssl.wrap_socket(
                                        self.socket, cert_reqs=certReqs, ssl_version=self.sslVersion)
                                    self.socket.do_handshake()
                                except Exception as e:
                                    self.buf = b''
                                    self.closeConnection()
                                    self.error(
                                        "SSL Http proxy refuses to establish the tunnel: %s" % e)
                                    self.onProxyConnectionError(
                                        err="The SSL HTTP proxy refuses to establish the tunnel")
                                else:
                                    self.proxyConnectSuccess = True
                                    self.buf = b''
                                    readTrueData = True
                            else:
                                # set final step
                                self.proxyConnectSuccess = True
                                self.buf = b''
                                readTrueData = True
                else:
                    raise Exception('need more proxy headers: %s' % self.buf)

            # handle socks5: not implemented
            elif self.proxyType == PROXY_TYPE_SOCKS5:
                if ord(self.buf[0]) != 5:  # bad version on response
                    self.error(
                        "Socks5: bad response from proxy: %s" %
                        self.buf[0])
                    self.onProxyConnectionError(
                        err="Socks5: bad response from proxy: %s" %
                        self.buf[0])
                else:
                    if ord(self.buf[1]) == 0:  # No authentication is required
                        pass
                    # we need to perform a basic username/password
                    elif ord(self.buf[1]) == 2:
                        pass
                    else:
                        self.buf = b''
                        self.error(
                            "Socks5: authentication type not supported: %s" %
                            self.buf[1])
                        self.onProxyConnectionError(
                            err="Socks5: authentication type not supported: %s" %
                            self.buf[1])
            else:
                self.error('proxy type unknown: %s' % self.proxyType)
                readTrueData = True
        except Exception as e:
            self.error("more data needed for proxy handshake: %s" % e)
        return readTrueData

    def stop(self):
        """
        Stops the thread
        """
        self.running = False
        self.event.set()
        self.trace('Tcp Client Thread Stopped')

    def sendHttpPacket(self, packet):
        """
        Send packet without terminator

        @param packet: packet to send
        @type packet: string
        """
        if isinstance(packet, bytes):  # python 3 support
            self.queue.put(packet)
        else:
            if sys.version_info[0] == 3:  # python 3 support
                self.queue.put(bytes(packet, "UTF-8"))
            else:
                self.queue.put(packet)

    def sendPacket(self, packet):
        """
        Send packet to network, terminator added at the end

        @param packet: packet to send
        @type packet: string
        """
        if self.wsSupport and self.wsHandshakeSuccess:

            if sys.version_info[0] == 3:  # python 3 support
                if isinstance(packet, bytes):
                    payload_data = packet + self.terminator
                else:
                    payload_data = bytes(packet, "UTF-8") + self.terminator
            else:
                payload_data = packet + self.terminator

            # make chunk
            if sys.version_info[0] == 3:  # python 3 support
                chunks = [payload_data[x:x + self.wsMaxPayloadSize]
                          for x in range(0, len(payload_data), self.wsMaxPayloadSize)]
            else:
                chunks = [payload_data[x:x + self.wsMaxPayloadSize]
                          for x in xrange(0, len(payload_data), self.wsMaxPayloadSize)]

            # encode data in the websocket packet and enqueue it
            for chunk in chunks:
                # encode in text websocket
                wsdata = self.wsCodec.encodeText(data=chunk)

                if isinstance(packet, bytes):  # python 3 support
                    self.queue.put(wsdata)
                else:
                    if sys.version_info[0] == 3:  # python 3 support
                        self.queue.put(bytes(wsdata, "UTF-8"))
                    else:
                        self.queue.put(wsdata)
        else:
            if isinstance(packet, bytes):  # python 3 support
                self.queue.put(packet + self.terminator)
            else:
                if sys.version_info[0] == 3:  # python 3 support
                    self.queue.put(bytes(packet, "UTF-8") + self.terminator)
                else:
                    self.queue.put(packet + self.terminator)

    def handleIncomingPacket(self, pdu):
        """
        Function to reimplement
        Called on incoming packet

        @param pdu: payload received
        @type pdu: string
        """
        self.trace(pdu)

    def getLocalAddress(self):
        """
        Returns the binding address

        @return: local bind address (ip, port)
        @rtype: tuple
        """
        rslt = self.localAddress
        s = self.socket
        if s:
            try:
                rslt = s.getsockname()
            except Exception:
                pass
        return rslt

    def onWsHanshakeError(self, err):
        """
        Function to reimplement
        Called on ws handshake error

        @param err: error message
        @type err: string
        """
        pass

    def onWsHanshakeSuccess(self):
        """
        Function to reimplement
        Called on successful ws handshake
        """
        pass

    def onProxyConnectionSuccess(self):
        """
        Function to reimplement
        Called on successful proxy handshake
        """
        pass

    def onConnection(self):
        """
        Function to reimplement
        Called on successful tcp connection
        """
        pass

    def onProxyConnection(self):
        """
        Function to reimplement
        Called on successful tcp connection on proxy
        """
        pass

    def onDisconnection(self, byServer=False, inactivityServer=False):
        """
        Function to reimplement
        Called on successful tcp disconnection

        @param byServer: True if the server closes the connection
        @type byServer: boolean
        """
        pass

    def onConnectionRefused(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onResolveHostnameFailed(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onResolveHostnameProxyFailed(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onConnectionTimeout(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onInactivityTimeout(self):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onProxyConnectionRefused(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onProxyConnectionError(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def onProxyConnectionTimeout(self, err):
        """
        Function to reimplement

        @param err: error message
        @type err: string
        """
        pass

    def trace(self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """
        print(txt)

    def error(self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """
        print(txt)
