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
Tcp server module
"""
import sys
import threading
try:
    import SocketServer
except ImportError:  # python3 support
    import socketserver as SocketServer
import select
try:
    import Queue
except ImportError:  # support python 3
    import queue as Queue
import time
import socket
import ssl

try:
    xrange
except NameError:  # support python3
    xrange = range

from ea.libs.NetLayerLib import WebSocket

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class NoMoreData(Exception):
    """
    No more data exception
    """
    pass


class TcpRequestHandler(SocketServer.BaseRequestHandler):
    """
    Tcp request handler
    """

    def __init__(self, request, clientAddress, server, terminator=b'\x00'):
        """
        TCP request handler

        @param request:
        @type request:

        @param clientAddress:
        @type clientAddress:

        @param server:
        @type server:

        @param terminator:
        @type terminator: string
        """
        self.__mutex__ = threading.RLock()
        self.clientId = clientAddress  # (ip,port)
        self.publicIp = clientAddress[0]  # external ip with rp
        self.stopEvent = threading.Event()
        self.buf = b''  # contains all received data.
        self.bufWs = b''  # contains just ws data
        self.queue = Queue.Queue(0)
        self.socket = None
        self.terminator = terminator
        self.keepAlivePdu = b''
        self.lastActivityTimestamp = time.time()
        self.lastKeepAliveTimestamp = time.time()
        self.wsHandshakeSuccess = False
        self.wsCodec = WebSocket.WebSocketCodec(parent=self)
        SocketServer.BaseRequestHandler.__init__(
            self, request, clientAddress, server)

    def mainReceiveSendLoop(self):
        """
        Main loop to receive and send data
        """
        while not self.stopEvent.isSet():

            # Check if we have incoming data
            r, w, e = select.select(
                [self.socket], [], [self.socket], self.server.selectTimeout)
            if self.socket in e:
                raise EOFError("Socket select error: disconnecting")
            elif self.socket in r:
                read = self.socket.recv(4096)
                if not read:
                    raise NoMoreData("no more data, connection lost")
                else:
                    self.lastActivityTimestamp = time.time()
                    self.buf = b''.join([self.buf, read])
                    self.onIncomingData()

            # Check inactivity timeout
            elif self.server.inactivityTimeout:
                if (time.time() -
                        self.lastActivityTimestamp) > self.server.inactivityTimeout:
                    raise EOFError("Inactivity timeout: disconnecting")

            try:
                if self.server.wsSupport:
                    keepAlive = False
                    if self.server.wsSupport and self.wsHandshakeSuccess:
                        keepAlive = True
                    if keepAlive:
                        if self.server.keepAliveInterval:
                            if time.time() - self.lastKeepAliveTimestamp > self.server.keepAliveInterval:
                                self.lastKeepAliveTimestamp = time.time()
                                wsping, pingid = self.wsCodec.encodePing()
                                self.trace(
                                    "sending ws ping message to %s" % pingid)
                                self.queue.put(wsping)
                else:
                    # Send (queue) a Keep-Alive if needed
                    if self.server.keepAliveInterval:
                        if time.time() - self.lastKeepAliveTimestamp > self.server.keepAliveInterval:
                            self.lastKeepAliveTimestamp = time.time()
                            self.trace("sending keep-alive to %s" %
                                       str(self.clientId))
                            self.sendPacket(self.keepAlivePdu)
            except Exception as e:
                raise Exception("keepalive error: %s" % e)

            try:
                # Send queued messages
                while not self.queue.empty():
                    try:
                        r, w, e = select.select(
                            [], [
                                self.socket], [
                                self.socket], self.server.selectTimeout)
                        if self.socket in e:
                            raise IOError(
                                "Socket select error when sending a message: disconnecting")
                        elif self.socket in w:
                            message = self.queue.get(False)
                            self.socket.sendall(message)
                            del message
                        else:
                            self.trace(
                                "Not ready to send a queued message. Queue size: %s" %
                                self.queue.qsize())
                            break
                    except Queue.Empty:
                        pass
                    except IOError as e:
                        self.error(
                            "IOError while sending a packet to client (%s) - disconnecting" %
                            str(e))
                        self.stop()
                    except Exception as e:
                        self.error("Unable to send message: %s" % str(e))
            except Exception as e:
                raise Exception("send error: %s" % e)
        self.socket.close()

    def handshakeWebSocket(self, keyReceived):
        """
        Build websocket handshake response and send-it

        @param keyReceived: key received
        @type keyReceived: string
        """
        try:
            # construct handshake
            headers = []
            headers.append(b"HTTP/1.1 101 Web Socket Protocol Handshake")
            headers.append(b"Upgrade: websocket")
            headers.append(b"Connection: upgrade")
            wsAccept = self.wsCodec.createSecWsAccept(key=keyReceived)
            headers.append(b"Sec-WebSocket-Accept: %s" % wsAccept)
            headers.append(b"")
            headers.append(b"")

            # send packet
            self.sendHttpPacket(packet=b"\r\n".join(headers))
        except Exception as e:
            self.error("unable to respond to the web socket handshake: %s" % e)

    def onIncomingData(self):
        """
        Called on incoming data
        """
        readTrueData = False
        if self.server.wsSupport and not self.wsHandshakeSuccess:
            self.trace('Opening ws handshake expected')
            readTrueData = self.decodeWsHandshake()
            if self.wsHandshakeSuccess:
                self.server.onWsHanshakeSuccess(self.clientId, self.publicIp)
        else:
            readTrueData = True

        if readTrueData:
            if self.server.wsSupport:
                while len(self.buf) >= 2:
                    time.sleep(self.server.selectTimeout)
                    try:
                        (data, opcode, left, needmore) = self.wsCodec.decodeWsData(
                            buffer=self.buf)
                    except Exception as e:
                        raise Exception("unable to decode ws: %s" % e)
                    self.buf = left
                    if opcode == WebSocket.WEBSOCKET_OPCODE_TEXT:
                        try:
                            if len(data):
                                self.bufWs = b''.join([self.bufWs, data])
                        except Exception as e:
                            raise Exception("unable to bufferize ws: %s" % e)
                    else:
                        try:
                            if opcode == WebSocket.WEBSOCKET_OPCODE_PING:
                                self.trace(
                                    "received ws ping message id=%s" % data)
                                wspong = self.wsCodec.encodePong(data=data)
                                self.queue.put(wspong)
                                self.trace("sending pong message id=%s" % data)
                            elif opcode == WebSocket.WEBSOCKET_OPCODE_PONG:
                                self.trace(
                                    "received ws pong message id=%s" % data)
                            else:
                                self.error(
                                    'unknown ws opcode received: %s' % opcode)
                                break
                        except Exception as e:
                            raise Exception("unable to ping ws: %s" % e)
                    self.readBufferWs()
                    if needmore:
                        break
            else:
                self.readBuffer()

    def readBufferWs(self):
        """
        Read websocket buffer
        """
        try:
            pdus = self.bufWs.split(self.terminator)
            for pdu in pdus[:-1]:
                self.handlePacket(pdu)
            self.bufWs = pdus[-1]
        except Exception as e:
            raise Exception("read buffer ws: %s" % e)

    def readBuffer(self):
        """
        Read tcp buffer
        """
        try:
            pdus = self.buf.split(self.terminator)
            for pdu in pdus[:-1]:
                if not pdu == self.keepAlivePdu:
                    self.handlePacket(pdu)
                else:
                    self.trace("received keep-alive from client")
            self.buf = pdus[-1]
        except Exception as e:
            raise Exception("read buffer: %s" % e)

    def decodeWsHandshake(self):
        """
        Decode incoming websocket handshake request
        """
        readTrueData = False
        try:
            if self.buf.find(b"\r\n\r\n") != -1:
                req = self.buf.split(b"\r\n\r\n")[0]

                self.trace('ws complete request received')
                reqline = req.splitlines()[0].split(b" ", 2)
                if reqline[2] not in (
                        b"HTTP/1.1") and reqline[0] not in (b"GET"):
                    self.error("Malformed HTTP message: %s" % reqline)
                    response = b'HTTP/1.1 400 Bad Request\r\n\r\n'
                    self.sendHttpPacket(response)
                    self.server.onWsHanshakeError(self.clientId)
                else:
                    # checking ws headers
                    status, key = self.wsCodec.checkingWsReqHeaders(
                        request=req)
                    if not status:
                        self.error("handshake ws refused")
                        response = b'HTTP/1.1 500 Internal Server Error\r\n\r\n'
                        self.sendHttpPacket(response)
                        self.server.onWsHanshakeError(self.clientId)
                    else:
                        publicIp = self.wsCodec.getHeaderForwardedFor(
                            request=req)
                        if publicIp is not None:
                            self.trace("ws public ip: %s" % publicIp)
                            self.publicIp = publicIp
                        self.handshakeWebSocket(keyReceived=key)
                        self.trace('ws handshake accepted')
                        self.wsHandshakeSuccess = True
                        self.buf = b""
                        readTrueData = True
            else:
                raise Exception('need more ws headers on request')
        except Exception as e:
            self.error("more data needed for ws handshake: %s" % e)
        return readTrueData

    def stop(self):
        """
        Stop thread
        """
        self.stopEvent.set()

    def sendHttpPacket(self, packet):
        """
        Send packet without terminator

        @param packet:
        @type packet:
        """
        self.queue.put(packet)

    def sendPacket(self, packet):
        """
        Send packet

        @param packet:
        @type packet:
        """
        if self.server.wsSupport and self.wsHandshakeSuccess:
            payload_data = packet + self.terminator
            # make chunk
            chunks = [payload_data[x:x + self.server.wsMaxPayloadSize]
                      for x in xrange(0, len(payload_data), self.server.wsMaxPayloadSize)]

            # encode data in the websocket packet and enqueue it
            for chunk in chunks:
                wsdata = self.wsCodec.encodeText(data=chunk)
                self.queue.put(wsdata)
        else:
            self.queue.put(packet + self.terminator)

    def handle(self):
        """
        BaseRequestHandler Reimplentation
        """
        self.socket = self.request
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        while not self.stopEvent.isSet():
            try:
                self.mainReceiveSendLoop()
            except NoMoreData as e:
                self.trace("handle no more data: %s" % e)
                self.stop()
            except Exception as e:
                self.error("unable to handle tcp client thread: %s" % e)
                self.stop()

    def handlePacket(self, packet):
        """
        Handle packet

        @param packet:
        @type packet:
        """
        self.server.handlePacket(self.clientId, packet)

    def setup(self):
        """
        Called on connection
        """
        self.server.onConnection(self)

    def finish(self):
        """
        Called on disconnection
        """
        try:
            self.stop()
            SocketServer.BaseRequestHandler.finish(self)
            self.server.onDisconnection(self)
        except Exception as e:
            self.error('unable to finish: %s' % e)

    def trace(self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """
        self.server.trace('[TcpClientThread]: %s %s' %
                          (str(self.clientId), txt))

    def error(self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """
        self.server.error('[TcpClientThread]: %s %s' %
                          (str(self.clientId), txt))

    def warning(self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """
        self.server.warning('[TcpClientThread]: %s %s' %
                            (str(self.clientId), txt))


class TcpServerThread(
        threading.Thread, SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    Tcp server thread
    """
    allow_reuse_address = True

    def __init__(self, listeningAddress, inactivityTimeout=120,
                 keepAliveInterval=40, selectTimeout=0.1,
                 sslSupport=False, certFile='', keyFile='',
                 sslVersion=ssl.PROTOCOL_TLSv1,
                 wsMaxPayloadSize=WebSocket.WEBSOCKET_MAX_BASIC_DATA1024,
                 wsSupport=False):
        """
        @param listeningAddress: listening address ip and port
        @type listeningAddress: tuple

        @param inactivityTimeout: default value of 60 seconds
        @type inactivityTimeout: integer

        @param keepAliveInterval: default value of 40 seconds
        @type keepAliveInterval: integer

        @param selectTimeout: default value of 0.01 seconds
        @type selectTimeout: float

        @param wsSupport: websocket support
        @type wsSupport: boolean

        @param sslSupport: ssl support
        @type sslSupport: boolean

        @param certFile: certificate file
        @type certFile: boolean

        @param keyFile: key file
        @type keyFile: boolean

        @param sslVersion: ssl version
        @type sslVersion: boolean

        @param wsMaxPayloadSize: websocket payload size
        @type wsMaxPayloadSize: boolean
        """
        threading.Thread.__init__(self)
        SocketServer.TCPServer.__init__(
            self, listeningAddress, TcpRequestHandler)  # , bind_and_activate=True
        self.mutex = threading.RLock()
        self.stopEvent = threading.Event()
        self.listeningAddress = listeningAddress
        self.clients = {}
        self.inactivityTimeout = inactivityTimeout
        self.keepAliveInterval = keepAliveInterval
        self.selectTimeout = float(selectTimeout)
        # web socket
        self.wsSupport = wsSupport
        if wsSupport:
            self.__trace__(
                'Web socket activated - version %s' %
                WebSocket.WEBSOCKET_VERSION)
        self.wsMaxPayloadSize = wsMaxPayloadSize

        # ssl support
        self.sslSupport = sslSupport
        self.certFile = certFile
        self.keyFile = keyFile
        self.sslVersion = sslVersion
        if sslSupport:
            self.__trace__('Ssl activated - version %s' % self.sslVersion)

        self.dataReceived = 0

    def get_request(self):
        """
        Called on incomming request
        Wrap ssl to the socket if activated

        @return:
        @rtype:
        """
        newsocket, fromaddr = self.socket.accept()
        if self.sslSupport:
            self.__trace__(
                "new client %s, ssl activated, wrap socket to ssl" %
                str(fromaddr))
            connstream = ssl.wrap_socket(newsocket,
                                         server_side=True,
                                         certfile=self.certFile,
                                         keyfile=self.keyFile,
                                         ssl_version=self.sslVersion)
        else:
            connstream = newsocket
        return connstream, fromaddr

    def run(self):
        """
        In run
        """
        self.__trace__("Started, listening on %s" %
                       (str(self.listeningAddress)))
        while not self.stopEvent.isSet():
            self.handleRequestWithTimeout(self.selectTimeout)

    def stop(self):
        """
        Stop server
        """
        self.__trace__("Stopping...")
        for client in self.clients.values():
            client.stop()
        self.stopEvent.set()
        self.__trace__("Stopped.")

    def stopClient(self, client):
        """
        Stop client

        @param client:
        @type client:
        """
        self.__trace__("Stopping client %s ..." % str(client))
        if client in self.clients:
            c = self.clients[client]
            c.stop()
            self.__trace__("Client stopped %s ..." % str(client))

    def onConnection(self, client):
        """
        Called on connection

        @param client: object tcp client thread
        @type client: tcpclientthread
        """
        self.__trace__("New client connected: privateaddress=%s publicip=%s" % (str(client.client_address),
                                                                                client.publicIp))
        self.mutex.acquire()
        self.clients.update({client.client_address: client})
        self.mutex.release()
        self.__trace__("New client added: %s" % str(client.client_address))

    def onDisconnection(self, client):
        """
        Called on disconnection

        @param client: object tcp client thread
        @type client: tcpclientthread
        """
        self.__trace__("Client disconnected: %s" % str(client.client_address))
        self.mutex.acquire()
        del self.clients[client.client_address]
        self.mutex.release()
        self.__trace__("Client removed: %s" % str(client.client_address))

    def onWsHanshakeError(self, clientId):
        """
        Called on websocket handshake error

        @param clientId:
        @type clientId:
        """
        self.__trace__(
            "WS opening handshake error for client %s" %
            str(clientId))

    def onWsHanshakeSuccess(self, clientId, publicIp):
        """
        Called on websocket handshake success

        @param clientId:
        @type clientId:
        """
        self.__trace__(
            "WS handshake successful for client %s public ip=%s" %
            (str(clientId), publicIp))

    def sendPacket(self, client, packet):
        """
        Send packet to the client

        @param client:
        @type client:

        @param packet:
        @type packet:
        """
        self.__trace__("Sending packet to client: %s" % str(client))
        self.mutex.acquire()
        if client in self.clients:
            client = self.clients[client]
        else:
            client = None
        self.mutex.release()
        if client:
            self.__trace__("Client found for %s" % str(client.client_address))
            client.sendPacket(packet)

    def handlePacket(self, client, packet):
        """
        Handle incoming packet

        @param client:
        @type client:

        @param packet:
        @type packet:
        """
        pass

    def handleRequestWithTimeout(self, timeout):
        """
        Handle request with timeout

        @param timeout:
        @type timeout:
        """
        r, w, e = select.select([self.socket], [], [], timeout)
        if r:
            self.handle_request()

    def __trace__(self, txt):
        """
        Added class name and calls the function trace

        @param txt:
        @type txt:
        """
        msg_ = "[TcpServerThread] %s" % txt
        self.trace(msg_)

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

    def warning(self, txt):
        """
        Display txt on screen

        @param txt: message
        @type txt: string
        """
        print(txt)
