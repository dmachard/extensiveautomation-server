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
Socket agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import os
import socket
import select
import time
import threading
try:
    import Queue
except ImportError: # support python 3
    import queue as Queue
import sys


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
else:
    # these exceptions does not exist in python2.X
    class ConnectionAbortedError(Exception): 
        """
        Connection aborted exception
        """
        pass
    class ConnectionRefusedError(Exception): 
        """
        Connection refused exception
        """
        pass
    class ConnectionResetError(Exception): 
        """
        Connection reset exception
        """
        pass
    
# SSL support 
try:
    import ssl
except ImportError as x:
    print("error to import ssl module: %s" % x)
    sys.exit(-1)

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False
__APP_PATH__ = ""
__TYPE__="""socket"""
__RESUME__="""This agent enables to open one or more sockets on a remote peer and return the network flow.
Types of sockets supported : tcp, udp and raw (linux only)."""
__DESCRIPTION__="""This agent enables to open one or more sockets on a remote peer and return the network flow.
Types of sockets supported : tcp, udp and raw (linux only).

Events messages:
    Agent->Server
        * Error( ... )
        * Notify( socket-raw-event=initialized|listen-error|sniffing-failed|sniffing|stopped|socket-error|on-run )
        * Notify( udp-event=socket-family-unknown|connect-error|listening-failed|listening|initialized|stopped|on-run|socket-error )
        * Notify( ssl-event=version-unknown|check-certificate-unknown|init-failed|handshake|handshake-accepted|handshake-failed
        * Notify( tcp-event=socket-family-unknown|connect-error|initialized|connected|connection-refused|connection-failed|
                  connection-timeout|disconnected-by-peer|socket-error|no-more-data|sending-error|on-run|closed )
        * Data( sock-data )

    Server->Agent
        * Init( sock-type=tcp|udp|raw )
        * Notify( ... )
        * Reset( ... )

Targetted operating system: Windows and linux"""

MAX_INACTIVITY = 3600

IPv4    = 4
IPv6    = 6

COOKED_PACKET_SOCKET    = 0     # AF_PACKET,SOCK_DGRAM, Ethernet protocol, cooked Linux packet socket
RAW_PACKET_SOCKET       = 1     # AF_PACKET, SOCK_RAW, Ethernet protocol, raw Linux packet socket
UNIX_DGRAM_SOCKET       = 2     # AF_UNIX, SOCK_DGRAM, 0, Unix-domain datagram socket
UNIX_STREAM_SOCKET      = 3     # AF_UNIX, SOCK_STREAM, 0, Unix-domain stream socket

INET6_RAW_SOCKET        = 4     # AF_INET6, SOCK_RAW, an IP protocol, IPv6 raw socket
INIT6_DGRAM_SOCKET      = 5     # AF_INET6, SOCK_DGRAM, 0 (or IPPROTO_UDP), UDP over IPv6
INIT6_STREAM_SOCKET     = 6     # AF_INET6, SOCK_STREAM, 0 (or IPPROTO_TCP), TCP over IPv6

INIT_ICMP_SOCKET        = 7     # AF_INET, SOCK_RAW, 0x01
INIT_DGRAM_SOCKET       = 8     # AF_INET, SOCK_DGRAM, 0 (or IPPROTO_UDP), UDP over IPv4
INIT_STREAM_SOCKET      = 9     # AF_INET, SOCK_STREAM, 0 (or IPPROTO_TCP), TCP over IPv4
INIT_UDP_SOCKET         = 10    # AF_INET, SOCK_RAW, 0x11
INIT_TCP_SOCKET         = 11    # AF_INET, SOCK_RAW, 0x06

SOCKET_BUFFER = 65535

def getSocket(sockType):
    """
    Get socket 

    @param sockType: TestAdapter.RAW_PACKET_SOCKET | TestAdapter.INIT6_STREAM_SOCKET | TestAdapter.INIT_STREAM_SOCKET
    @type sockType: integer

    @return: socket
    @rtype: socket
    """
    if sockType == COOKED_PACKET_SOCKET: # cooked Linux packet socket
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM, socket.SOCK_RAW)
    elif sockType == RAW_PACKET_SOCKET: # raw Linux packet socket
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
    elif sockType == UNIX_DGRAM_SOCKET: # Unix-domain datagram socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM, socket.SOCK_RAW)
    elif sockType == UNIX_STREAM_SOCKET: # Unix-domain stream socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, socket.SOCK_RAW)
    elif sockType == INET6_RAW_SOCKET: # IPv6 raw socket
        sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_IP)
    elif sockType == INIT6_DGRAM_SOCKET: # UDP over IPv6
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    elif sockType == INIT6_STREAM_SOCKET: # TCP over IPv6
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    elif sockType == INIT_ICMP_SOCKET: # ICMP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, 0x01)  # 0x01 == ICMP
    elif sockType == INIT_UDP_SOCKET: # UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, 0x11)  # 0x11 == UDP
    elif sockType == INIT_TCP_SOCKET: # TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, 0x06)  # 0x06 == TCP
    elif sockType == INIT_DGRAM_SOCKET: # UDP over IPv4
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    elif sockType == INIT_STREAM_SOCKET: #  TCP over IPv4
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    else:
        sock = None
    return sock


#CERT_NONE - no certificates from the other side are required (or will
#be looked at if provided)
#CERT_OPTIONAL - certificates are not required, but if provided will be
#validated, and if validation fails, the connection will
#also fail
#CERT_REQUIRED - certificates are required, and will be validated, and
#if validation fails, the connection will also fail

CHECK_CERT_NO = 'No'
CHECK_CERT_OPTIONAL = 'Optional'
CHECK_CERT_REQUIRED = 'Required'

#client / server    SSLv2   SSLv3   SSLv23  TLSv1
#SSLv2  yes     no  yes     no
#SSLv3  no  yes     yes     no
#SSLv23     yes     no  yes     no
#TLSv1  no  no  yes     yes

SSLv2 = "SSLv2" 
SSLv23 = "SSLv23" 
SSLv3 = "SSLv3"
TLSv1 = "TLSv1"
TLSv11 = "TLSv11"
TLSv12 = "TLSv12"

class HandshakeFailed(Exception):
    """
    Handshake failed exception
    """
    pass
    
class SockRawThread(threading.Thread):
    """
    Raw socket thread
    """
    def __init__(self, parent, request):
        """
        Individual raw socket
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__mutex__ = threading.RLock()
        self.parent = parent
        self.request = request 
        self.socket = None
        self.cfg = request['data']
        self.sniffing = False   
        self.__checkConfig()

    def onReset(self):
        """
        On reset thread
        """
        self.stop()
        
    def trace(self, txt):
        """
        Trace
        """
        self.parent.trace(txt)


    def error(self, err):
        """
        Log error
        """
        self.parent.error(err)
        
    def __checkConfig(self):
        """
        private function
        """
        # log all configuration parameters
        self.trace( "cfg: %s"  % self.cfg )
        # checking all parameters 
        if not ('sock-type' in self.cfg ):
            self.sendError(data="sock-type configuration key is missing")
    
    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )

    def sendNotify(self, data):
        """
        Send notify to the server
        """
        self.trace( "send notify: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-notify"
        req['data'] = data
        self.parent.notify( data=req )
    

    def sendData(self, data):
        """
        Send data to the server
        """
        self.trace( "send data: %s"  % len(data) )
        req =  self.request
        req['event'] = "agent-data"
        req['data'] = data
        self.parent.notify( data=req )

    def createRawSocket(self):
        """
        Create a raw socket and start to listen
        """
        try:
            # Create the socket for windows
            self.socket = getSocket(sockType=RAW_PACKET_SOCKET)
            self.socket.bind( ( self.cfg['src-eth'], socket.SOCK_RAW ) )

            # extract reel source mac addr
            src_mac = ':'.join( ["%02X" % (ord(ch),) for ch in self.socket.getsockname()[-1]] )
            self.sendNotify(data={'socket-raw-event': 'initialized', 'src-mac': src_mac  } )

            self.sniffing = True
            self.onStartSniffing()
        except socket.error as e:
            self.onStartSniffingFailed(e)
        except Exception as e:
            self.sendError( data= { 'socket-raw-event': "listen-error", 'more': "%s" % str(e) } )
            self.stop()
    
    def onNotify(self, client, tid, request):
        """
        Called from remote peer to send data to the socket
        """
        self.sendRawData(data=request['data']['payload'])
        
    def sendRawData(self, data):
        """
        Send data to the raw socket
        """
        if not self.sniffing:
            self.trace( "not sniffing" )
            return
        self.socket.send( data )
        self.trace( "raw data sent" )

    def onStartSniffingFailed(self, e):
        """
        On start sniffing failed
        """
        self.sendNotify(data={'socket-raw-event': 'sniffing-failed', 'more': str(e) } )
        self.stop()

    def onStartSniffing(self):
        """
        On connection tcp
        """
        self.sendNotify(data={'socket-raw-event': 'sniffing' } )

    def cleanSocket(self):
        """
        Clean socket
        """
        if self.socket is not None: 
            self.socket.close()
            self.sendNotify(data={'socket-raw-event': 'stopped' } )

    def stop(self):
        """
        Stop the thread
        """
        self.sniffing = False
        self.stopEvent.set()

    def run(self):
        """
        On run function
        """
        while not self.stopEvent.isSet():
            time.sleep(0.1)
            self.__mutex__.acquire()
            try:
                if self.socket is not None: 
                    if self.sniffing:
                        r, w, e = select.select([ self.socket ], [], [ self.socket ], 0.01)
                        if self.socket in e:
                            raise EOFError("raw socket select error")
                        elif self.socket in r:  
                            read = self.socket.recv( SOCKET_BUFFER )
                            self.trace('data received (bytes %d)...' % len(read))
                            self.sendData(data=read)
            except socket.error as e:
                self.onSocketError(e)
            except Exception as e:    
                self.sendError( data={ 'socket-raw-event': "on-run", "more": "%s" % str(e) } )
            self.__mutex__.release()
        self.cleanSocket()
    
    def onSocketError(self, e):
        """
        On tcp socket error
        """
        self.sendError( data={ 'socket-raw-event': "socket-error", "more": "%s" % str(e) } )
        self.stop()

class SockUdpThread(threading.Thread):
    """
    UDP socket thread
    """
    def __init__(self, parent, request):
        """
        Individual udp socket
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__mutex__ = threading.RLock()
        self.parent = parent
        self.request = request 
        self.socket = None
        self.cfg = request['data']
        self.islistening = False    
        self.__checkConfig()

    def onReset(self):
        """
        On reset
        """
        self.stop()
        
    def trace(self, txt):
        """
        Trace
        """
        self.parent.trace(txt)


    def error(self, err):
        """
        Log error
        """
        self.parent.error(err)
        
    def __checkConfig(self):
        """
        Private function
        Check the configuration of the socket
        """
        # log all configuration parameters
        self.trace( "cfg: %s" % self.cfg )
        # checking all parameters 
        if not ('sock-type' in self.cfg ):
            self.sendError(data="sock-type configuration key is missing")
    
    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )

    def sendNotify(self, data):
        """
        Send notify to the server
        """
        self.trace( "send notify: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-notify"
        req['data'] = data
        self.parent.notify( data=req )
    

    def sendData(self, data):
        """
        Send data to the server
        """
        self.trace( "send data: %s"  % len(data) )
        req =  self.request
        req['event'] = "agent-data"
        req['data'] = data
        self.parent.notify( data=req )
    
    def onNotify(self, client, tid, request):
        """
        Called from remote peer to send data to the socket
        """
        self.sendUdpData(data=request['data']['pdu'], addr=request['data']['addr'])

    def sendUdpData(self, data, addr):
        """
        Send data to the tcp socket
        """
        if not self.islistening:
            self.trace( "not connected" )
            return
        self.socket.sendto(data, addr)
        self.trace( "pdu sent" )

    def createUdpSocket(self):
        """
        Create the socket
        """
        # Start the tcp connection
        self.trace( 'starting to listen' )
        try:
            # set the socket version
            if self.cfg['sock-family'] == IPv4:
                sockType = INIT_DGRAM_SOCKET
            elif  self.cfg['sock-family'] == IPv6:
                sockType = INIT6_DGRAM_SOCKET
            else:
                self.sendError( { 'udp-event':'socket-family-unknown', 'more': '%s' % str(self.cfg['socket-family'])} )
                self.stop()

            # Create the socket
            self.socket = getSocket(sockType=sockType)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.trace( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
            
            # listening successful
            self.__setSource()  

            self.islistening = True
            self.lastActivity = time.time()
            self.onStartListening()
        except socket.error as e:
            self.onStartListeningFailed(e)
        except Exception as e:
            self.sendError( data= { 'udp-event': "connect-error", 'more': "%s" % str(e) } )
            self.stop()

    def onStartListeningFailed(self, e):
        """
        On connection timeout
        """
        self.sendNotify(data={'udp-event': 'listening-failed', 'more': str(e) } )
        self.stop()

    def onStartListening(self):
        """
        On connection tcp
        """
        self.sendNotify(data={'udp-event': 'listening' } )


    def __setSource(self):
        """
        Set the source ip and port
        """
        srcIp, srcPort = self.socket.getsockname()
        self.sendNotify(data={'udp-event': 'initialized', 'src-ip': srcIp, 'src-port': srcPort} )

    def cleanSocket(self):
        """
        Clean the socket
        """
        if self.socket is not None: 
            self.socket.close()
            self.sendNotify(data={'udp-event': 'stopped' } )

    def stop(self):
        """
        Stop the thread
        """
        self.stopEvent.set()

    def run(self):
        """
        On run function
        """
        while not self.stopEvent.isSet():
            self.__mutex__.acquire()
            try:
                if self.socket is not None:  
                    if self.islistening:
                        r, w, e = select.select([ self.socket ], [], [], 0.01)
                        for s in r:
                            if s is not None:
                                (data, addr) = s.recvfrom(65535)
                                self.lastActivity = time.time()
                                self.sendData(data={'pdu': data, 'from-addr': addr } )
                        
                        # Check inactivity timeout, global protection
                        if time.time() - self.lastActivity > MAX_INACTIVITY:
                            self.trace( "nothing happens since a long time ago, force to stop me" )
                            # self.closeSocket()
                            self.stop()
            except socket.error as e:
                self.onSocketError(e)
            except Exception as e:
                self.sendError( data={ 'udp-event': "on-run", "more": "%s" % str(e) } )
            self.__mutex__.release()
        self.cleanSocket()

    def onSocketError(self, e):
        """
        On tcp socket error
        """
        self.sendError( data={ 'udp-event': "socket-error", "more": "%s" % str(e) } )
        self.stop()

class SockTcpThread(threading.Thread):
    """
    TCP socket thread
    """
    def __init__(self, parent, request):
        """
        Individual socket
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__mutex__ = threading.RLock()
        self.parent = parent
        self.request = request 
        self.socket = None
        self.cfg = request['data']
        self.tcpConnected = False   
        self.__checkConfig()
        self.sslCipher = ''
        self.sslVersion = ''
        self.sslBits = ''
   
    def onReset(self):
        """
        On reset
        """
        self.stop()
        
    def trace(self, txt):
        """
        Trace
        """
        self.parent.trace( str(txt) )

    def error(self, err):
        """
        Log error
        """
        self.parent.error( str(err) )
        
    def __checkConfig(self):
        """
        private function
        """
        # log all configuration parameters
        self.trace(  "cfg: %s"  %  self.cfg )
        # checking all parameters 
        if not ('sock-type' in self.cfg ):
            self.sendError(data="sock-type configuration key is missing")

    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )

    def sendNotify(self, data):
        """
        Send notify to the server
        """
        self.trace( "send notify: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-notify"
        req['data'] = data
        self.parent.notify( data=req )

    def sendData(self, data):
        """
        Send data to the server
        """
        self.trace( "send data: %s"  % len(data) )
        req =  self.request
        req['event'] = "agent-data"
        req['data'] = data
        self.parent.notify( data=req )

    def onNotify(self, client, tid, request):
        """
        Called from remote peer to send data to the socket
        """
        self.sendTcpData(data=request['data']['payload'])

    def sendTcpData(self, data):
        """
        Send data to the tcp socket
        """
        if not self.tcpConnected:
            self.trace( "not connected" )
            return
        self.queueTcp.put( data )

    def initSocketSsl(self, sock):
        """
        Initialize the socket for ssl
        """
        try:
            # set ssl version
            self.trace( 'initialize ssl' )
            ver = ssl.PROTOCOL_TLSv1 # default value
            if  self.cfg['ssl-version'] == SSLv2:
                ver = ssl.PROTOCOL_SSLv2
            elif self.cfg['ssl-version'] == SSLv23:
                ver = ssl.PROTOCOL_SSLv23
            elif self.cfg['ssl-version'] == SSLv3:
                ver = ssl.PROTOCOL_SSLv3
            elif self.cfg['ssl-version'] == TLSv1:
                ver = ssl.PROTOCOL_TLSv1        
            elif self.cfg['ssl-version'] == TLSv11:
                ver = ssl.PROTOCOL_TLSv1_1  
            elif self.cfg['ssl-version'] == TLSv12:
                ver = ssl.PROTOCOL_TLSv1_2      
            else:
                raise Exception('ssl init - version unknown: %s' % str(self.cfg['ssl-version']) )   
            
            # set cehck certificate option
            if self.cfg['check-cert'] == CHECK_CERT_NO:
                check = ssl.CERT_NONE
            elif self.cfg['check-cert'] == CHECK_CERT_OPTIONAL:
                check = ssl.CERT_OPTIONAL
            elif self.cfg['check-cert'] == CHECK_CERT_REQUIRED:
                check = ssl.CERT_REQUIRED               
            else:
                raise Exception('check certificate unknown: %s' % str(self.cfg['check-cert']) )

            self.sslVersion = self.cfg['ssl-version']
            if check == ssl.CERT_REQUIRED and self.cfg['ca-certs'] is None:
                raise Exception("certificate required from the other side of the connection - no CA certificates")

            if sock is not None:
                sock = ssl.wrap_socket(sock, cert_reqs=check, do_handshake_on_connect=False, 
                                        ssl_version=ver, ca_certs=self.cfg['ca-certs'] )
        except Exception as e:
            raise Exception('SSL init failed: %s' % str(e)) 
        return sock
    
    def getPEMcert(self, DERcert):
        """
        Return the DER cert to PEM
        """
        return ssl.DER_cert_to_PEM_cert(DERcert)
    
    def getSslError(self, err):
        """
        enum py_ssl_error {
            /* these mirror ssl.h */
            PY_SSL_ERROR_NONE,                 
            PY_SSL_ERROR_SSL,                   
            PY_SSL_ERROR_WANT_READ,             
            PY_SSL_ERROR_WANT_WRITE,            
            PY_SSL_ERROR_WANT_X509_LOOKUP,      
            PY_SSL_ERROR_SYSCALL,     /* look at error stack/return value/errno */
            PY_SSL_ERROR_ZERO_RETURN,           
            PY_SSL_ERROR_WANT_CONNECT,
            /* start of non ssl.h errorcodes */ 
            PY_SSL_ERROR_EOF,         /* special case of SSL_ERROR_SYSCALL */
            PY_SSL_ERROR_INVALID_ERROR_CODE
        };      
        """
        errMsg = ""
        try:
            sslError = err.split('SSL routines:')[1].split(':')[1]
            errMsg = sslError[:-2]
        except Exception as e:
            errMsg = str(err)
        return errMsg
        
    def doSslHandshake(self, sock):
        """
        Perform the SSL setup handshake.
        """
        try:
            self.sendNotify(data={'ssl-event': 'handshake' } )
            self.trace( 'starting handshake ')
            
            # do handshake ssl
            sock.do_handshake()
            
            self.trace( 'handshake done')
            # extract ssl informations
            self.sslCipher, self.sslVersion, self.sslBits = sock.cipher()
            dercert = sock.getpeercert(True)
            certPEM = self.getPEMcert( dercert )

            self.sendNotify(data={'ssl-event': 'handshake-accepted', 'cipher': self.sslCipher, 
                                    'version': self.sslVersion,  'bits': self.sslBits, 'cert-pem': certPEM} )
        except ssl.SSLError as x: 
            self.sendNotify(data={'ssl-event': 'handshake-failed', 'error': self.getSslError(str(x)) } )
            # raise failure to parent
            raise HandshakeFailed()

    def createTcpSocket(self):
        """
        Create a tcp socket and start the connection
        """
        try:
            # set the socket version
            if self.cfg['sock-family'] == IPv4:
                sockType = INIT_STREAM_SOCKET
            elif  self.cfg['sock-family'] == IPv6:
                sockType = INIT6_STREAM_SOCKET
            else:
                self.sendError( { 'tcp-event':'socket-family-unknown', 'more': '%s' % str(self.cfg['socket-family'])} )
                self.stop()
                
            # Create the socket
            self.socket = getSocket(sockType=sockType)
            self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            if self.cfg['tcp-keepalive']:
                # active tcp keep alive
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                if sys.platform == "win32":
                    self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, self.cfg['tcp-keepalive-interval']*1000, 
                                                                    self.cfg['tcp-keepalive-interval']*1000))
                elif sys.platform == "darwin":
                    # interval in seconds between keepalive probes
                    self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.cfg['tcp-keepalive-interval']) 
                    # failed keepalive probes before declaring the other end dead
                    self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5) 
                else:
                    # seconds before sending keepalive probes
                    self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.cfg['tcp-keepalive-interval'] ) 
                    # interval in seconds between keepalive probes
                    self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.cfg['tcp-keepalive-interval']) 
                    # failed keepalive probes before declaring the other end dead
                    self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5) 

            self.socket.settimeout( self.cfg['sock-timeout'] )
            self.trace( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.__setSource()  

            # Optional: initialize the ssl
            if self.cfg['ssl-support']:
                self.socket = self.initSocketSsl(sock=self.socket)
            
            # Connect the socket
            self.socket.connect( (self.cfg['dst-ip'], self.cfg['dst-port']) )

            # Connection successful
            self.tcpConnected = True
            self.lastActivity = time.time()
            self.queueTcp = Queue.Queue(0)
            self.onConnectionTcp()      
            
            # Optional: do ssl handshake
            if self.cfg['ssl-support']:
                try:
                    self.doSslHandshake(sock=self.socket)
                except HandshakeFailed:
                    self.onSslHandshakeFailed()
        except socket.timeout as e:
            self.onConnectionTimeout(e)
        except socket.error as e:
            if sys.version_info > (3,):
                errno = e.errno
                strerror = os.strerror(errno)
                self.onConnectionFailed(errno=errno, errstr=strerror)
            else:
                (errno, errstr) = e
                if errno == 111:
                    self.onConnectionRefused()
                else:
                    self.onConnectionFailed(errno=errno, errstr=errstr)
                
        # new with python3
        except ConnectionAbortedError as e:
            self.onDisconnectionByPeer(msg=e)
        except ConnectionRefusedError as e:
            self.onConnectionRefused()
        except ConnectionResetError as e:
            self.onDisconnectionByPeer(msg=e)
        # end of new
                
        except Exception as e:
            self.sendError( data= { 'tcp-event': "connect-error", 'more': "%s" % str(e) } )
            self.stop()

    def __setSource(self):
        """
        Set the source ip and port
        """
        srcIp, srcPort = self.socket.getsockname()
        self.sendNotify(data={'tcp-event': 'initialized', 'src-ip': srcIp, 'src-port': srcPort} )

    def onSslHandshakeFailed(self):
        """
        On ssl handshake failed
        """
        self.stop()

    def onConnectionTcp(self):
        """
        On connection tcp
        """
        self.sendNotify(data={'tcp-event': 'connected' } )
    
    def onConnectionRefused(self):
        """
        On connection refused
        """
        self.sendNotify(data={'tcp-event': 'connection-refused' } )
        self.stop()

    def onConnectionFailed(self, errno, errstr):
        """
        On connection failed
        """
        self.sendNotify(data={'tcp-event': 'connection-failed', 'err-no': errno, 'err-str': errstr} )
        self.stop()

    def onConnectionTimeout(self, e):
        """
        On connection timeout
        """
        self.sendNotify(data={'tcp-event': 'connection-timeout', 'more': str(e) } )
        self.stop()

    def onDisconnectionByPeer(self, msg):
        """
        On disconnection by peer
        """
        self.sendNotify(data={'tcp-event': 'disconnected-by-peer', 'more': str(msg)} )
        self.stop()

    def onSocketError(self, e):
        """
        On tcp socket error
        """
        self.sendError( data={ 'tcp-event': "socket-error", "more": "%s" % str(e) } )
        self.stop()

    def run(self):
        """
        On run function
        """
        while not self.stopEvent.isSet():
            self.__mutex__.acquire()
            try:
                if self.socket is not None: 
                    if self.tcpConnected:
                        r, w, e = select.select([ self.socket ], [], [ self.socket ], 0.01)
                        if self.socket in e:
                            raise EOFError("socket select error: disconnecting")
                        elif self.socket in r:
                            read = self.socket.recv(1024*1024)
                            if not read:
                                self.sendNotify(data={'tcp-event': 'no-more-data' } )
                                raise EOFError("nothing to read: disconnecting")
                            self.trace( '%d bytes received' % len(read) )
                            self.lastActivity = time.time()
                            self.sendData(data=read)

                        # Check inactivity timeout, global protection
                        elif time.time() - self.lastActivity > MAX_INACTIVITY:
                            self.trace( "nothing happens since a long time ago, force to stop me" )
                            # self.closeSocket()
                            self.stop()

                        # send queued messages
                        while not self.queueTcp.empty():
                            r, w, e = select.select([ ], [ self.socket ], [ self.socket ], 0.001)
                            if self.socket in e:
                                raise EOFError("socket select error when sending a message: disconnecting")
                            elif self.socket in w: 
                                try:
                                    message = self.queueTcp.get(False)
                                    if sys.version_info > (3,):
                                        if isinstance(message, bytes):
                                            self.socket.sendall(message)
                                        else:
                                            self.socket.sendall( bytes(message, "utf8") )
                                    else:
                                        try:
                                            self.socket.sendall(message)
                                        except UnicodeError:
                                            self.socket.sendall(message.encode('utf-8'))
                                    self.trace( "packet sent" )
                                except Queue.Empty:
                                    pass
                                except Exception as e:
                                    self.sendError(data= { 'tcp-event': "sending-error", 
                                                            "more": "unable to send message: %s" % str(e) } )
                            else:
                                break
            except EOFError as e:
                self.onDisconnectionByPeer(e)
            except socket.error as e:
                self.onSocketError(e)
            except Exception as e:
                self.sendError( data={ 'tcp-event': "on-run", "more": "%s" % str(e) } )
            self.__mutex__.release()
        self.cleanSocket()

    def cleanSocket(self):
        """
        Clean the socket
        """
        self.trace( 'cleaning socket connected=%s...' % self.tcpConnected )    
        if self.socket is not None: 
            if self.tcpConnected:
                self.trace( 'closing socket...' )    
                self.socket.close()
                self.sendNotify(data={'tcp-event': 'closed' } )
        self.tcpConnected = False
    
    def stop(self):
        """
        Stop the thread
        """
        self.stopEvent.set()

class SockUdpServerThread(threading.Thread):
    """
    UDP Socket server thread
    """
    def __init__(self, parent, request):
        """
        Constructor
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__mutex__ = threading.RLock()
        self.parent = parent
        self.request = request 
        self.socket = None
        self.islistening = False
        self.cfg = request['data']
        self.__checkConfig()
        
    def __checkConfig(self):
        """
        private function
        """
        # log all configuration parameters
        self.trace(  "cfg: %s"  %  self.cfg )
        # checking all parameters 
        if not ('sock-type' in self.cfg ):
            self.sendError(data="server sock-type configuration key is missing")
            
    def createUdpServerSocket(self):
        """
        Create the UDP server socket
        """
        pass
        
    def __setSource(self):
        """
        Set the source ip and port
        """
        srcIp, srcPort = self.socket.getsockname()
        self.sendNotify(data={'tcp-event': 'initialized', 'src-ip': srcIp, 'src-port': srcPort} )

    def onNotify(self, client, tid, request):
        """
        On notify
        """
        pass
   
    def onReset(self):
        """
        On reset
        """
        self.stop()
        
    def trace(self, txt):
        """
        Trace
        """
        self.parent.trace( str(txt) )

    def error(self, err):
        """
        Log error
        """
        self.parent.error( str(err) )
    
    def stop(self):
        """
        Stop the thread
        """
        self.stopEvent.set()

    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )

    def sendNotify(self, data):
        """
        Send notify to the server
        """
        self.trace( "send notify: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-notify"
        req['data'] = data
        self.parent.notify( data=req )

    def sendData(self, data):
        """
        Send data to the server
        """
        self.trace( "send data: %s"  % len(data) )
        req =  self.request
        req['event'] = "agent-data"
        req['data'] = data
        self.parent.notify( data=req )

    def run(self):
        """
        On run function
        """
        while not self.stopEvent.isSet():
            self.__mutex__.acquire()
            self.__mutex__.release()

# NEW in v12.1.0
class ClientThread(threading.Thread):
    """
    Client thread
    """
    def __init__(self, sock, ip, port, parent, id):
        """
        Constructor
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__parent = parent
        self.clientAddress = (ip,port)
        self.ID = id
        self.socket = sock
        self.buf = ''
        self.queueTcp = Queue.Queue(0)
        self.__mutex__ = threading.RLock()
        self.lastActivity = time.time()
        
    def getId(self):
        """
        Return the id
        """
        return self.ID
        
    def getAddress(self):
        """
        Return the client adress
        """
        return self.clientAddress
        
    def getSocket(self):
        """
        Return the socket
        """
        return self.socket
        
    def parent(self):
        """
        Return the parent object
        """
        return self.__parent
        
    def run(self):
        """
        On run thread
        """
        while not self.stopEvent.isSet():
            try:
                # check if we have incoming data
                if self.socket is not None:         
                    r, w, e = select.select([ self.socket ], [], [ self.socket ], 0.01)
                    if self.socket in e:
                            raise EOFError("socket select error: disconnecting")
                    elif self.socket in r:
                            read = self.socket.recv(1024*1024)
                            if not read:
                                self.onIncomingData(noMoreData=True)
                                raise EOFError("nothing to read: disconnecting")
                            self.parent().trace( '%d bytes received' % len(read) )
                            self.lastActivity = time.time()
                            if self.parent().cfg['sep-disabled']:
                                self.onIncomingData(data=read)
                            else:
                                self.buf = ''.join([self.buf, read])
                                self.onIncomingData()
                    
                    # Check inactivity timeout
                    elif self.parent().cfg['inactivity-timeout']:
                        if time.time() - self.lastActivity > self.parent().cfg['inactivity-timeout']:
                            self.parent().trace( "Inactivity detected: disconnecting client #%s" % self.getId() )
                            raise EOFError("inactivity timeout: disconnecting")
    
                    # send queued messages
                    while not self.queueTcp.empty():
                            r, w, e = select.select([ ], [ self.socket ], [ self.socket ], 0.001)
                            if self.socket in e:
                                self.parent().error("Socket select error when sending a message: disconnecting client #%s" % self.getId() )
                                raise EOFError("socket select error when sending a message: disconnecting")
                            elif self.socket in w: 
                                try:
                                        message = self.queueTcp.get(False)
                                        self.socket.sendall( message )
                                        self.parent().trace( "packet sent" )
                                except Queue.Empty:
                                        pass
                                except Exception as e:
                                        self.parent().error("unable to send message: " + str(e))
                            else:
                                    break
            except EOFError as e:
                self.onDisconnection(e)
            except socket.error as e:
                self.parent().onClientSocketError(self.clientAddress, e )
                self.stop()
            except Exception as e:
                self.parent().error( "on run %s" % str(e) )
                self.stop()
        
        self.socket.close()
        self.stop()
        
    def stop(self):
        """
        Stop the thread
        """
        self.stopEvent.set()
        
    def onDisconnection(self, e):
        """
        On disconnection event
        """
        self.parent().trace(e)
        self.stop()
        self.parent().onClientDisconnected(self.clientAddress)
        
    def onIncomingData(self, data=None, noMoreData=False):
        """
        On incoming data event
        """ 
        (ip, port) = self.clientAddress
        try:
            if noMoreData:
                self.parent().onClientNoMoreData(clientAddress=self.clientAddress)
            else:
                if data is not None: # separator feature is disabled
                    self.parent().onClientIncomingData( clientAddress=self.clientAddress, pdu=data )
                
                else: # separator feature is enabled, split the buffer by the separator
                    datas = self.buf.split(self.parent().cfg['sep-in'])
                    for data in datas[:-1]:
                        pdu = data+self.parent().cfg['sep-in']
                        self.parent().onClientIncomingData( clientAddress=self.clientAddress, pdu=pdu)
                    
                    self.buf = datas[-1]
        except Exception as e:
            self.parent().error( str(e) )

class SockTcpServerThread(threading.Thread):
    """
    TCP Socket server thread
    """
    def __init__(self, parent, request):
        """
        Constructor
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__mutex__ = threading.RLock()
        self.parent = parent
        self.request = request 
        self.socket = None
        self.islistening = False
        self.cfg = request['data'] # save the init request
        
        self.clientsThreads = {}
        self.clientId = 0
        self.idMutex = threading.RLock()
        
        self.__checkConfig()
        
    def __checkConfig(self):
        """
        private function
        """
        # log all configuration parameters
        self.trace(  "cfg: %s"  %  self.cfg )
        
        # checking all parameters 
        if not ('sock-type' in self.cfg ):
            self.sendError(data="server sock-type configuration key is missing")

    def createTcpServerSocket(self):
        """
        Create the TCP server socket
        """
        try:
            # set the socket version
            if self.cfg['sock-family'] == IPv4:
                sockType = INIT_STREAM_SOCKET
            elif  self.cfg['sock-family'] == IPv6:
                sockType = INIT6_STREAM_SOCKET
            else:
                raise Exception('socket family unknown: %s' % str(self.cfg['socket-family']) )  
            
            # Create the socket
            self.socket = getSocket(sockType=sockType)
            self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            if self.cfg['tcp-keepalive']:
                # active tcp keep alive
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # seconds before sending keepalive probes
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.cfg['tcp-keepalive-interval'] ) 
                # interval in seconds between keepalive probes
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.cfg['tcp-keepalive-interval']) 
                # failed keepalive probes before declaring the other end dead
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5) 

            self.socket.settimeout( self.cfg['sock-timeout'] )
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.trace( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.socket.listen(0)

            # Listening successful
            self.__setSource()  
            self.islistening = True
            self.sendNotify(data={'tcp-event': 'listening' } )
                
        except socket.error as e:
            (errno, errstr) = e
            self.sendNotify(data={'tcp-event': 'listening-failed', 'err-no': errno, 'err-str': errstr} )
            self.stop()
        except Exception as e:
            self.error( "listening error: %s" % str(e) )
            self.sendError( data= { 'tcp-event': "listening-error", 'more': "%s" % str(e) } )
            self.stop()
            
    def __setSource(self):
        """
        Set the source ip and port
        """
        srcIp, srcPort = self.socket.getsockname()
        self.sendNotify(data={'tcp-event': 'initialized', 'src-ip': srcIp, 'src-port': srcPort} )

    def onNotify(self, client, tid, request):
        """
        On notify event
        """
        ip = request['data']['to-ip']
        port = request['data']['to-port']
        
        self.sendTcpData(clientAddress=(ip,port), pdu=request['data']['payload'])

    def sendTcpData(self, clientAddress, pdu):
        """
        Send data to the tcp socket
        """
        if not self.islistening:
            self.trace( "not listening" )
            return
        client = self.getClientByAddress(clientAddress)
        if client is None:
            return
            
        # send data
        if sys.version_info[0] == 3: # python 3 support
            client['thread'].queueTcp.put( bytes(pdu, "UTF-8") )
        else:
            client['thread'].queueTcp.put( pdu )
        
    def onReset(self):
        """
        On reset event
        """
        self.stop()
        
    def trace(self, txt):
        """
        Trace
        """
        self.parent.trace( str(txt) )

    def error(self, err):
        """
        Log error
        """
        self.parent.error( str(err) )
    
    def stop(self):
        """
        Stop the thread
        """
        self.stopEvent.set()

    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )

    def sendNotify(self, data):
        """
        Send notify to the server
        """
        self.trace( "send notify: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-notify"
        req['data'] = data
        self.parent.notify( data=req )

    def sendData(self, data):
        """
        Send data to the server
        """
        self.trace( "send data: %s"  % len(data) )
        req =  self.request
        req['event'] = "agent-data"
        req['data'] = data
        self.parent.notify( data=req )

    def run(self):
        """
        On run function
        """
        while not self.stopEvent.isSet():
            self.__mutex__.acquire()
            try:
                if self.socket is not None:  
                    if self.islistening:    
                        ( sock, (ip, port) ) = self.socket.accept()
                        self.onClientConnected(clientAddress=(ip, port), clientSocket=sock)
            except socket.error as e:
                pass
            except Exception as e:
                self.error( "on run %s" % str(e) )
            self.__mutex__.release()
        self.cleanSockets()
        
    def getId(self):
        """
        Return the ID
        """
        self.idMutex.acquire()
        self.clientId += 1
        ret = self.clientId
        self.idMutex.release()
        return ret
        
    def getClientByAddress(self, clientAddress):
        """
        Return the client thread by address
        """
        if clientAddress in self.clientsThreads:
            return self.clientsThreads[clientAddress]
        else:
            return None

    def getClientById(self, id):
        """
        Return the client thread by ID
        """
        ret = None
        for clientAddress, client in self.clientsThreads.items():
            if client['id'] == int(id):
                ret = client['thread']
                break
        return ret
        
    def cleanSockets(self):
        """
        Clean all sockets
        """
        if self.socket is not None: 
            self.socket.close()
            self.sendNotify(data={'tcp-event': 'stopped' } )
            self.islistening = False

    def onClientConnected(self, clientAddress, clientSocket):
        """
        On client connected event
        """
        # extract the ip and port of the client
        # and generate a id for this new client
        (ip, port) = clientAddress
        id = self.getId()
        
        # init a thread for this client
        newthread = ClientThread(clientSocket, ip, port, parent=self, id=id)
        newthread.start()
        self.clientsThreads[(ip, port)] = {'thread': newthread, 'id': id }
        
        # notify the server
        self.sendNotify(data={'tcp-event': 'client-connected', 'ip': ip, 'port': port } )
        
    def onClientSocketError(self, clientAddress, error):
        """
        On client socket error event
        """
        (ip, port) = clientAddress
        
        # notify the server
        self.sendError( data= { 'tcp-event': "client-socket-error", 'more': "%s" % error, 'ip': ip, 'port': port } )
        
    def onClientDisconnected(self, clientAddress):
        """
        On client disconnected event
        """
        (ip, port) = clientAddress
        
        # notify the server
        self.sendNotify(data={'tcp-event': 'client-disconnected', 'ip': ip, 'port': port } )
        
    def onClientNoMoreData(self, clientAddress):
        """
        On client no more data event
        """
        (ip, port) = clientAddress
        
        # notify the server
        self.sendNotify(data={'tcp-event': 'client-no-more-data', 'ip': ip, 'port': port } )
        
    def onClientIncomingData(self, clientAddress, pdu):
        """
        On incoming data from client event
        """
        (ip, port) = clientAddress
        
        # notify the server
        self.sendNotify(data={'tcp-event': 'client-data', 'ip': ip, 'port': port, 'payload': pdu } )
# END OF NEW

def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Socket( controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                    supportProxy, proxyIp, proxyPort, sslSupport )

class Socket(GenericTool.Tool):
    """
    Socket agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                        supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Constructor
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=supportProxy,
                                        proxyIp=proxyIp, proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__

    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass
        
    def onToolLogWarningCalled(self, msg):
        """
        Function to reimplement
        """
        pass
    
    def onToolLogErrorCalled(self, msg):
        """
        Function to reimplement
        """
        pass

    def onToolLogSuccessCalled(self, msg):
        """
        Logs success on main application

        @param msg: error message
        @type msg: string
        """
        pass
        
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        self.onToolLogWarningCalled("Starting socket agent")
        self.onToolLogWarningCalled("Socket agent started")
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
        Return agent type
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all sockets, all threads
        """
        pass

    def onAgentAlive(self, client, tid, request):
        """
        Called on keepalive received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass
        
    def onAgentInit(self, client, tid, request):
        """
        Initialize a new socket the agent 
        """
        pass

    def onAgentReset(self, client, tid, request):
        """
        On agent reset event
        """
        pass

    def execAction(self, client, tid, request):
        """
        Execute action
        """
        currentTest = self.context()[request['uuid']][request['source-adapter']]

        try:
            cmd = request['data']['cmd']
            
            # NEW IN V12.1.0
            if cmd == 'starting':
                if request['data']['sock-type'] == 'tcp':
                    self.onToolLogWarningCalled( "<< Starting TCP Server socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                              request['script_id'], 
                                                                                                              request['source-adapter']) )
                    if sys.platform == "win32" or sys.platform == "linux2":
                        self.info( 'New TCP server socket on platform: %s' % sys.platform )
                        self.trace( 'Starting tcp server thread...' )
                        
                        newthread = SockTcpServerThread(parent=self, request=request)
                        currentTest.ctx_plugin = newthread
                        newthread.createTcpServerSocket()

                        # starting the thread
                        newthread.start()

                        self.onToolLogWarningCalled( "<< Started TCP Server socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                                 request['script_id'],
                                                                                                                 request['source-adapter']) )
                    else:
                        self.error( 'Init tcp server - platform not yet supported: %s' % sys.platform )
                        self.onToolLogErrorCalled( 'Initialize tcp server socket failed - platform not yet supported: %s' % sys.platform )
                elif request['data']['sock-type'] == 'udp':
                    self.onToolLogWarningCalled( "<< Starting UDP Server socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                              request['script_id'],
                                                                                                              request['source-adapter']) )
                    if sys.platform == "win32" or sys.platform == "linux2":
                        self.info( 'New UDP server socket on platform: %s' % sys.platform )
                        self.trace( 'Starting udp server thread...' )
                        
                        newthread = SockUdpServerThread(parent=self, request=request)
                        currentTest.ctx_plugin = newthread
                        newthread.createUdpServerSocket()
                        
                        newthread.start()

                        self.onToolLogWarningCalled( "<< Started UDP Server socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                                 request['script_id'], 
                                                                                                                 request['source-adapter']) )
                    else:
                        self.error( 'Init udp server - platform not yet supported: %s' % sys.platform )
                        self.onToolLogErrorCalled( 'Initialize udp server socket failed - platform not yet supported: %s' % sys.platform )
                else:
                    self.error('server socket type unknown: %s' % request['data']['sock-type'] )
                    self.onToolLogErrorCalled( 'Initialize server socket failed - generic error: %s' % sys.platform )

            elif cmd == 'stopping':
                self.onToolLogWarningCalled( "<< Closing server socket=%s TestId=%s AdapterId=%s" % (cmd, 
                                                                                                     request['script_id'],
                                                                                                     request['source-adapter']) )
                if currentTest.ctx() is not None:
                    currentTest.ctx().stop()
                    currentTest.ctx().join()
                self.onToolLogWarningCalled( "<< Closed server socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                    request['script_id'],
                                                                                                    request['source-adapter']) )
            # END OF NEW
            
            elif cmd == 'connect':

                if request['data']['sock-type'] == 'tcp':

                    self.onToolLogWarningCalled( "<< Starting TCP socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                       request['script_id'],
                                                                                                       request['source-adapter']) )

                    if sys.platform == "win32" or sys.platform == "linux2":
                        self.info( 'New TCP socket on platform: %s' % sys.platform )
                        self.trace( 'Starting tcp thread...' )
                        
                        newthread = SockTcpThread(parent=self, request=request)
                        currentTest.ctx_plugin = newthread
                        newthread.createTcpSocket()

                        # starting the thread
                        newthread.start()

                        self.onToolLogWarningCalled( "<< Started TCP socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                          request['script_id'],
                                                                                                          request['source-adapter']) )
                    else:
                        self.error( 'Platform not yet supported: %s' % sys.platform )
                        self.onToolLogErrorCalled( 'Initialize tcp socket failed - platform not yet supported: %s' % sys.platform )

                elif request['data']['sock-type'] == 'raw':
                    self.onToolLogWarningCalled( "<< Starting Raw socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                       request['script_id'],
                                                                                                       request['source-adapter']) )
                    
                    if sys.platform == "win32":
                        self.error( 'Platform not yet supported: %s' % sys.platform )
                        self.onToolLogErrorCalled( 'Starting raw socket failed - platform not yet supported: %s' % sys.platform )
                        self.sendNotify(request=request, data={'socket-raw-event': 'sniffing-failed', 
                                                                'more': 'platform not yet supported: %s' % sys.platform } )
                    elif sys.platform == "linux2":
                        self.info( 'New RAW socket on platform: %s' % sys.platform )
                        self.trace( 'Starting raw thread...' )
                        
                        newthread = SockRawThread(parent=self, request=request)
                        currentTest.ctx_plugin = newthread
                        newthread.createRawSocket()

                        newthread.start()
                        
                        self.onToolLogWarningCalled( "<< Started Raw socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                          request['script_id'],
                                                                                                          request['source-adapter']) )
                    else:
                        self.error( 'Platform not yet supported: %s' % sys.platform )
                        self.onToolLogErrorCalled( 'Initialize raw socket failed - platform not yet supported: %s' % sys.platform )

                elif request['data']['sock-type'] == 'udp':
                    self.onToolLogWarningCalled( "<< Starting UDP socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                       request['script_id'],
                                                                                                       request['source-adapter']) )
                    
                    if sys.platform == "win32" or sys.platform == "linux2":
                        self.info( 'New UDP socket on platform: %s' % sys.platform )
                        self.trace( 'Starting udp thread...' )
                        
                        newthread = SockUdpThread(parent=self, request=request)
                        currentTest.ctx_plugin = newthread
                        newthread.createUdpSocket()
                        
                        newthread.start()

                        self.onToolLogWarningCalled( "<< Started UDP socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                                          request['script_id'],
                                                                                                          request['source-adapter']) )
                    else:
                        self.error( 'Platform not yet supported: %s' % sys.platform )
                        self.onToolLogErrorCalled( 'Initialize socket failed - platform not yet supported: %s' % sys.platform )

                else:
                    self.error('sock type unknown: %s' % request['data']['sock-type'] )
                    self.onToolLogErrorCalled( 'Initialize socket failed - generic error: %s' % sys.platform )

            elif cmd == 'disconnect':
                self.onToolLogWarningCalled( "<< Closing socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                              request['script_id'],
                                                                                              request['source-adapter']) )
                if currentTest.ctx() is not None:
                    currentTest.ctx().stop()
                    currentTest.ctx().join()
                self.onToolLogWarningCalled( "<< Closed socket=%s TestId=%s AdapterId=%s" % (cmd,
                                                                                             request['script_id'], 
                                                                                             request['source-adapter']) )
            
            else:
                if currentTest.ctx() is not None:
                    currentTest.ctx().onNotify(client, tid, request)

        except Exception as e:
            self.error( 'unable to run sock action: %s - %s' % ( str(e), request['data'] ) )
            self.sendError( request , data="unable to run sock action")

    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        On reset the test context event
        """
        self.onToolLogWarningCalled( "<< Resetting Context TestID=%s AdapterId=%s" % (scriptId, adapterId) )
        self.trace("Resetting TestUuid=%s ScriptId=%s AdapterId=%s" % (testUuid, scriptId, adapterId) )

        currentTest = self.context()[testUuid][adapterId]
        if currentTest.ctx() is not None:
            try:
                self.trace('closing socket and stopping thread')
                currentTest.ctx().stop()
                currentTest.ctx().join()
                self.trace('sock thread stopped')
            except Exception as e:
                self.error( "unable to reset sock thread: %s" % e)
                
        # cleanup test context
        self.cleanupTestContext(testUuid, scriptId, adapterId)
        
    def onAgentNotify(self, client, tid, request):
        """
        Received a notify from server and dispatch it to the good socket
        """
        self.__mutex__.acquire()
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                ctx_test = self.context()[request['uuid']][request['source-adapter']]
                ctx_test.putItem( lambda: self.execAction(client, tid, request) )
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()