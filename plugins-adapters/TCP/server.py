#!/usr/bin/env python
# -*- coding=utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
import TestExecutorLib.TestExecutorLib as TestExecutorLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapterLib.getVersion()]
AdapterDNS = sys.modules['SutAdapters.%s.DNS' % TestAdapterLib.getVersion()]

import threading
import socket
import select
import time
import Queue
import templates

__NAME__="""TCP"""

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='socket'

class ClientThread(threading.Thread):
    def __init__(self, sock, ip, port, parent, id, filter = None, filterTime = None, destIp = None):
        """
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
        self.filter = filter
        self.filterTime = filterTime
        self.destIp = destIp
        
    def getId(self):
        """
        """
        return self.ID
    def getAddress(self):
        """
        """
        return self.clientAddress
    def getSocket(self):
        """
        """
        return self.socket
    def parent(self):
        """
        """
        return self.__parent
        
    def run(self):
        """
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
                            # begin new feature filtering
                            self.parent().debug("localtime: " + str(self.filterTime))
                            self.parent().debug(self.clientAddress[0])
                            self.parent().debug(self.destIp)
                            if self.destIp is not None:
                                if self.clientAddress[0] != self.destIp:
                                        read = ""
                            if self.filterTime is not None:
                                import re
                                for line in read.splitlines():
                                    packetTime=re.sub(".*\[(\d*)\].*","\\1",line)
                                    if len(packetTime)>0 and re.search("\D",packetTime) is None:
                                        self.parent().debug("detected time : " + str(packetTime))
                                        if int(self.filterTime) > int(packetTime):
                                            read = ""
                                        break
                            if len(read)>0 and self.filter is not None:
                                if not self.filter.seekIn(read):
                                    read = ""
                            # end of filtering feature
                            if not read:
                                self.onIncomingData(noMoreData=True)
                                raise EOFError("nothing to read: disconnecting")
                            self.parent().debug( '%d bytes received' % len(read) )
                            self.lastActivity = time.time()
                            if self.parent().cfg['sep-disabled']:
                                self.onIncomingData(data=read)
                            else:
                                self.buf = ''.join([self.buf, read])
                                self.onIncomingData()
                    
                    # Check inactivity timeout
                    elif self.parent().cfg['inactivity-timeout']:
                        if time.time() - self.lastActivity > self.parent().cfg['inactivity-timeout']:
                            self.parent().warning( "Inactivity detected: disconnecting client #%s" % self.getId() )
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
                                        self.socket.sendall(message)
                                        self.parent().debug( "packet sent" )
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
        """
        self.stopEvent.set()
    
    def onDisconnection(self, e):
        """
        """
        self.parent().debug(e)
        self.stop()
        self.parent().onClientDisconnected(self.clientAddress)

    def onIncomingData(self, data=None, noMoreData=False):
        """
        """ 
        (ip, port) = self.clientAddress
        try:
            if noMoreData:
                if self.parent().cfg['ssl-support']:
                    tpl = self.parent().encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received() )
                    lower = self.parent().ssl.encapsule(tpl=tpl, ssl_event=AdapterSSL.received()) 
                else:
                    lower = self.parent().encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(id=self.ID), src=ip, srcP=port )
                self.parent().onClientNoMoreData(clientAddress=self.clientAddress, lower=lower)
            else:
                if data is not None: # separator feature is disabled
                    pdu_size = len(data)
                    # log event
                    if self.parent().cfg['ssl-support']:
                        encap = self.parent().encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size), id=self.ID) )
                        self.parent().ssl.onIncomingDecodedData(data=data, tpl=encap, msg="client #%s data" % self.ID)
                    else:
                        tpl = self.parent().encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data=data, data_length=str(pdu_size), id=self.ID),
                                                                                                            src=ip, srcP=port )
                        if self.parent().logEventReceived:
                            tpl.addRaw(raw=data)
                            self.parent().logRecvEvent( shortEvt = "client #%s data" % self.ID, tplEvt = tpl )
                    
                    if self.parent().cfg['ssl-support']:
                        tpl = self.parent().encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size), id=self.ID) )
                        lower = self.parent().ssl.encapsule(tpl=tpl, ssl_event=AdapterSSL.received()) 
                    else:
                        lower = self.parent().encapsule( ip_event=AdapterIP.received(), 
                                                                                                                    tcp_event=templates.received(data_length=str(pdu_size), id=self.ID),
                                                                                                                    src=ip, srcP=port )
                    
                    # handle data
                    self.parent().onClientIncomingData( clientAddress=self.clientAddress, data=data, lower=lower )
                
                else: # separator feature is enabled, split the buffer by the separator
                    datas = self.buf.split(self.parent().cfg['sep-in'])
                    for data in datas[:-1]:
                        pdu = data+self.parent().cfg['sep-in']
                        pdu_size = len(pdu)
                        
                        # log event
                        if self.parent().cfg['ssl-support']:
                            encap = self.parent().encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size)) )
                            tpl = self.parent().ssl.onIncomingDecodedData(data=pdu, tpl=encap, msg="client #%s data" % self.ID)
                        else:
                            tpl = self.parent().encapsule( ip_event=AdapterIP.received(), 
                                                                                                                tcp_event=templates.received(data=pdu, data_length=str(pdu_size), id=self.ID),
                                                                                                                src=ip, srcP=port )
                            if self.parent().logEventReceived:
                                tpl.addRaw(raw=pdu)
                                self.parent().logRecvEvent( shortEvt = "client #%s data" % self.ID, tplEvt = tpl )
                                
                        # handle data
                        self.parent().onClientIncomingData( clientAddress=self.clientAddress, data=pdu, lower=tpl )
                    
                    self.buf = datas[-1]
        except TestExecutorLib.AbortException as e:
            raise TestExecutorLib.AbortException(e)
        except Exception as e:
            self.parent().error( str(e) )


class Server(TestAdapterLib.Adapter):
    @doc_public
    def __init__ (self, parent, bindIp = '', bindPort=0, name=None,
                                socketTimeout=1, socketFamily=AdapterIP.IPv4, inactivityTimeout=30.0,
                                tcpKeepAlive=False, tcpKeepAliveInterval=30.0,
                                separatorIn='\\x00', separatorOut='\\x00', separatorDisabled=False, 
                                sslSupport=False, sslVersion=AdapterSSL.SSLv23, checkCert=AdapterSSL.CHECK_CERT_NO,
                                debug=False, logEventSent=True, logEventReceived=True, parentName=None, shared=False,
                                agentSupport=False, agent=None, verbose = True, filter = None, filterTime = None, destIp = None
                        ):
        """
        This class enable to use TCP as server only, with support and dns resolution.
        Lower network layer (IP, Ethernet) are not controlable.
        
        @param parent: parent testcase
        @type parent: testcase

        @param name: adapter name used with from origin/to destination (default=None)
        @type name: string/none
        
        @param bindIp: bind on ip (source ip)
        @type bindIp: string

        @param bindPort: bind on port (source port)
        @type bindPort: integer

        @param socketTimeout: timeout to connect in second (default=1s)
        @type socketTimeout: float

        @param socketFamily: SutAdapters.IP.IPv4 (default)| SutAdapters.IP.IPv6 
        @type socketFamily: integer

        @param tcpKeepAlive: turn on tcp keep-alive (defaut=False)
        @type tcpKeepAlive: boolean

        @param tcpKeepAliveInterval: tcp keep-alive interval (default=30s)
        @type tcpKeepAliveInterval: float
        
        @param inactivityTimeout: close automaticly the socket (default=30s), set to zero to disable this feature.
        @type inactivityTimeout: float
        
        @param separatorIn: data separator (default=\\x00)
        @type separatorIn: string

        @param separatorOut: data separator (default=\\x00)
        @type separatorOut: string

        @param separatorDisabled: disable the separator feature, if this feature is enabled then data are buffered until the detection of the separator (default=False)
        @type separatorDisabled: boolean

        @param sslSupport: activate SSL channel (default=False)
        @type sslSupport: boolean

        @param sslVersion: SutAdapters.SSL.SSLv2 | SutAdapters.SSL.SSLv23 (default) | SutAdapters.SSL.SSLv3 | SutAdapters.SSL.TLSv1 
        @type sslVersion: strconstant

        @param checkCert: SutAdapters.SSL.CHECK_CERT_NO | SutAdapters.SSL.CHECK_CERT_OPTIONAL | SutAdapters.SSL.CHECK_CERT_REQUIRED
        @type checkCert: strconstant
        
        @param debug: True to activate debug mode (default=False)
        @type debug: boolean
        
        @param verbose: True to activate verbose mode (default=True)
        @type verbose: boolean

        @param shared: shared adapter (default=False)
        @type shared:   boolean
        
        @param filter: operator to filter the messages
        @type filter:   operators
        
        @param filterTime: time to filter the messages
        @type filterTime:   string
        """
        # check agent
        if agentSupport and agent is None:
            raise Exception('Agent cannot be undefined!')   
        if agentSupport:
            if not isinstance(agent, dict):
                raise Exception('Bad value passed on agent!')           
            if not len(agent['name']):
                raise Exception('Agent name cannot be empty!')  
            if unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED):
                raise Exception('Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED)) )    
        
        # init adapter
        TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared, 
                                                                                                                    showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose)
        if parentName is not None:
            TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__)  )
        self.__mutex__ = threading.RLock()
        self.queueTcp = Queue.Queue(0)
        self.parent = parent
        self.islistening = False    
        self.sourceIp = bindIp
        self.sourcePort = bindPort
        self.logEventSent = logEventSent
        self.logEventReceived = logEventReceived
        self.clientsThreads = {}
        self.clientId = 0
        self.idMutex = threading.RLock()
        self.filter = filter
        self.filterTime = filterTime
        self.destIp = destIp
        
        self.cfg = {}
        # transport options
        self.cfg['bind-ip'] = bindIp
        self.cfg['bind-port'] = bindPort
        # socket options
        self.cfg['sock-timeout'] =  socketTimeout
        self.cfg['sock-family'] =  int(socketFamily)
        # tcp 
        self.cfg['inactivity-timeout'] = inactivityTimeout
        self.cfg['tcp-keepalive'] = tcpKeepAlive
        self.cfg['tcp-keepalive-interval'] = tcpKeepAliveInterval
        # data separators 
        self.cfg['sep-in'] = separatorIn
        self.cfg['sep-out'] = separatorOut
        self.cfg['sep-disabled'] = separatorDisabled    
        
        # agent support
        self.cfg['agent-support'] = agentSupport
        if agentSupport:
            self.cfg['agent'] = agent
            self.cfg['agent-name'] = agent['name']
        
        # ssl support
        self.cfg['ssl-support'] = sslSupport
        self.ssl = AdapterSSL.Server(parent=parent, sslVersion=sslVersion, debug=debug, name=name,
                                                                logEventSent=logEventSent, logEventReceived=logEventReceived, shared=shared)
                                                                
        self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
                                                                                                                                logEvent=False, enabled=True)
        self.__checkConfig()

        if agentSupport:
            self.prepareAgent(data={'shared': shared})
            if self.agentIsReady(timeout=30) is None:
                raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
            self.TIMER_ALIVE_AGT.start()

    def receivedNotifyFromAgent(self, data):
        """
        Function to reimplement
        """
        self.debug( data )
        if 'cmd' in data:
            if data['cmd'] == AGENT_INITIALIZED:
                    tpl = TestTemplatesLib.TemplateMessage()
                    layer = TestTemplatesLib.TemplateLayer('AGENT')
                    layer.addKey("ready", True)
                    layer.addKey(name='name', data=self.cfg['agent']['name'] )
                    layer.addKey(name='type', data=self.cfg['agent']['type'] )
                    tpl.addLayer(layer= layer)
                    self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl ) 
        else:
            if 'tcp-event' in data:
                if data['tcp-event'] == 'initialized':
                    self.sourceIp = data['src-ip']
                    self.sourcePort = data['src-port']      
                elif data['tcp-event'] == 'listening':
                    self.onListening()
                elif data['tcp-event'] == 'stopped':
                    self.onStopListening()
                elif data['tcp-event'] == 'listening-failed':
                    self.onListeningFailed()
                elif data['tcp-event'] == 'client-connected':
                    self.onClientConnected(clientAddress=(data['ip'], data['port']), clientSocket=None)
                elif data['tcp-event'] == 'client-disconnected':
                    self.onClientDisconnected(clientAddress=(data['ip'], data['port']))
                elif data['tcp-event'] == 'client-data':
                    # prepare a template message
                    client = self.getClientByAddress(clientAddress=(data['ip'], data['port']))
                    if client is None:
                        return
                    tpl = self.encapsule( ip_event=AdapterIP.received(),    tcp_event=templates.received(id=client['id']),  src=data['ip'], srcP=data['port'] )
                    tpl.addRaw(raw=data['payload'])
                    
                    if self.logEventReceived:
                        self.logRecvEvent( shortEvt = "client #%s data" % client['id'], tplEvt = tpl )
                    
                    self.onClientIncomingData(clientAddress=(data['ip'], data['port']), 
                                                                                            data=data['payload'], lower=tpl)
                elif data['tcp-event'] == 'client-no-more-data':
                    tpl = self.encapsule( ip_event=AdapterIP.received(), 
                                                                                tcp_event=templates.received(), 
                                                                                src=data['ip'], srcP=data['port'] )
                    self.onClientNoMoreData(clientAddress=(data['ip'], data['port']), lower=tpl)
                else:
                    self.error("agent mode - tcp event unknown on notify: %s" % data['tcp-event'] )

    def receivedErrorFromAgent(self, data):
        """
        Function to reimplement
        """
        if 'tcp-event' in data:
            if data['tcp-event'] == 'listening-error':
                self.error( "listening error: %s" % data['more'] )
            elif data['tcp-event'] == 'client-socket-error':
                self.onClientSocketError(clientAddress=(data['ip'], data['port']), e=data['more'])
            else:
                self.error("agent mode - tcp event unknown on error: %s" % data['tcp-event'] )
        else:
            self.error("agent mode - global error: %s" % data )
            
    def receivedDataFromAgent(self, data):
        """
        Function to reimplement
        """
        pass
        
    def sendNotifyToAgent(self, data):
        """
        """
        self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
    def prepareAgent(self, data):
        """
        prepare agent
        """
        self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
    def initAgent(self, data):
        """
        Init agent
        """
        self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
    def resetAgent(self):
        """
        Reset agent
        """
        self.parent.sendResetToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData='')
    def aliveAgent(self):
        """
        Keep alive agent
        """
        self.parent.sendAliveToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData='')
        self.TIMER_ALIVE_AGT.restart()
        
    def agentIsReady(self, timeout=1.0):
        """
        Waits to receive "agent ready" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float    
        
        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        tpl = TestTemplatesLib.TemplateMessage()
        layer = TestTemplatesLib.TemplateLayer('AGENT')
        layer.addKey("ready", True)
        layer.addKey(name='name', data=self.cfg['agent']['name'] )
        layer.addKey(name='type', data=self.cfg['agent']['type'] )
        tpl.addLayer(layer= layer)
        evt = self.received( expected = tpl, timeout = timeout )
        return evt
    def __checkConfig(self):
        """
        private function
        """
        if self.cfg['agent-support'] :
            self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
            
        try:
            self.cfg['bind-port'] = int(self.cfg['bind-port'])
        except Exception as e:
            raise TestAdapterLib.AdapterException(TestAdapterLib.caller(), "config tcp: wrong bind port type: %s" % str(self.cfg['bind-port']) )

        self.debug("config: %s" % self.cfg)
    
    def __setSource(self):
        """
        """
        srcIp, srcPort = self.socket.getsockname() # ('127.0.0.1', 52318)
        self.sourceIp = srcIp
        self.sourcePort = srcPort       
    
    def setSource(self, bindIp, bindPort):
        """
        Set the source ip/port
        
        @param bindIp: bind on ip (source ip)
        @type bindIp: string

        @param bindPort: bind on port (source port)
        @type bindPort: integer
        """
        self.cfg['bind-ip'] = bindIp
        self.cfg['bind-port'] = bindPort

    def encapsule(self, ip_event, tcp_event, src="", srcP=""):
        """
        """
        # prepare layers
        if ip_event == AdapterIP.received():
            dst = self.sourceIp
            dstP = self.sourcePort
            srcIp = src
            srcPort = srcP
        else:
            dst = src
            dstP = srcP
            srcIp = self.sourceIp
            srcPort = self.sourcePort

        layer_ip = AdapterIP.ip( source=srcIp, destination=dst, version=self.cfg['sock-family'], more=ip_event ) 
        layer_tcp = templates.tcp(source=srcPort, destination=dstP)
        layer_tcp.addMore(more=tcp_event)
        
        # prepare template
        if self.cfg['agent-support']:
            layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
            layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
            layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
            
        # prepare template
        tpl = TestTemplatesLib.TemplateMessage()
        if self.cfg['agent-support']:
            tpl.addLayer(layer=layer_agent) 
        tpl.addLayer(layer=layer_ip)
        tpl.addLayer(layer=layer_tcp)
        return tpl
    
    @doc_public
    def startListening(self):
        """
        Start to listen
        """
        if self.islistening:
            self.debug( 'already listening' )
            return 

        # log event
        tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.start_listening() )
        self.logSentEvent( shortEvt = "starting", tplEvt = tpl )
        
        if self.cfg['agent-support']:
            remote_cfg = {
                'cmd': 'starting',
                'sock-type': 'tcp',  'sock-family': self.cfg['sock-family'],
                'sock-timeout': self.cfg['sock-timeout'],
                'inactivity-timeout': self.cfg['inactivity-timeout'],
                'tcp-keepalive': self.cfg['tcp-keepalive'],
                'tcp-keepalive-interval': self.cfg['tcp-keepalive-interval'] ,
                'bind-ip': self.cfg['bind-ip'], 'bind-port': self.cfg['bind-port'],
                'sep-in': self.cfg['sep-in'] ,  'sep-out': self.cfg['sep-out'] , 
                'sep-disabled': self.cfg['sep-disabled']
            }
            self.sendNotifyToAgent(data=remote_cfg)
        else:
            try:
                # set the socket version
                if self.cfg['sock-family'] == AdapterIP.IPv4:
                    sockType = TestAdapterLib.INIT_STREAM_SOCKET
                elif  self.cfg['sock-family'] == AdapterIP.IPv6:
                    sockType = TestAdapterLib.INIT6_STREAM_SOCKET
                else:
                    raise Exception('socket family unknown: %s' % str(self.cfg['socket-family']) )  
                
                # Create the socket
                self.socket = TestAdapterLib.getSocket(sockType=sockType)
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
                self.debug( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
                self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
                self.socket.listen(0)
    
                # Listening successful
                self.__setSource()  
                self.islistening = True
                self.onListening()
                    
                # start thread
                self.setRunning()
            except socket.error as e:
                (errno, errstr) = e
                self.onListeningFailed(errno=errno, errstr=errstr)
            except Exception as e:
                self.error( "listening error: %s" % str(e) )
            
    @doc_public
    def stopListening(self):
        """
        Close the TCP connection
        """
        self.__mutex__.acquire()
        if self.islistening:
            self.debug( 'no more listen started' )
            
            # log event
            tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.stop_listening() )
            self.logSentEvent( shortEvt = "stopping", tplEvt = tpl )
        
            if self.cfg['agent-support']:
                self.unsetRunning()
                # stop timer
                self.TIMER_ALIVE_AGT.stop()

                # cleanup remote agent
                remote_cfg = {'cmd': 'stopping'}
                self.sendNotifyToAgent(data=remote_cfg)
            else:
                self.cleanSockets()
                self.onStopListening()
        self.__mutex__.release()
        
    def cleanSockets(self):
        """
        """
        self.debug( 'clean the socket' )
        self.unsetRunning()
        # clean the socket
        if self.socket is not None:
            self.socket.close()
            self.islistening = False

    def getId(self):
        """
        """
        self.idMutex.acquire()
        self.clientId += 1
        ret = self.clientId
        self.idMutex.release()
        return ret

    def getClientByAddress(self, clientAddress):
        """
        """
        if clientAddress in self.clientsThreads:
            return self.clientsThreads[clientAddress]
        else:
            return None

    def getClientById(self, id):
        """
        """
        ret = None
        for clientAddress, client in self.clientsThreads.items():
            if client['id'] == int(id):
                ret = client['thread']
                break
        return ret
    def getClientAddrById(self, id):
        """
        """
        ret = None
        for clientAddress, client in self.clientsThreads.items():
            if client['id'] == int(id):
                ret = clientAddress
                break
        return ret
    def onReset(self):
        """
        Reset
        """
        self.stopRunning()
        
        if self.cfg['agent-support']:
            self.TIMER_ALIVE_AGT.stop()
            remote_cfg = {'cmd': 'stopping'}
            self.sendNotifyToAgent(data=remote_cfg)
        else:
            # stop all client
            for clientAddress, client in self.clientsThreads.items():
                client['thread'].stop()
                client['thread'].join()
            
            self.clientsThreads = {} 
            self.stopListening()

    def onRun(self):
        """
        """
        self.__mutex__.acquire()
        try:
            # check if we have incoming data
            if self.socket is not None:  
                if self.islistening:
                    ( sock, (ip, port) ) = self.socket.accept()
                    if self.cfg['ssl-support']:
                        id = self.getId()
                        tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.client_connected(id=id), src=ip, srcP=port )
                        self.logRecvEvent( shortEvt = "client #%s connected" % id, tplEvt = tpl )                           
                        try:
                            # log ssl event
                            s_encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent() )
                            self.ssl.logDoHandshake( tpl_s=s_encap, msg='client #%s do handshake' % id )
                            
                            # wrap socket
                            sock = self.ssl.initSocketSsl(sock=sock) 
                            
                            # log ssl ok
                            r_encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(id=id) )
                            self.ssl.logHandshakeAccepted( tpl_r=r_encap, msg='client #%s handshake accepted' % id )
                        except Exception as e:
                            # log ssl error
                            r_encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(id=id) )
                            self.ssl.logHandshakeFailed( r_encap, err=str(e), msg='client #%s handshake failed' % id )
                        else:
                            # start a independant thread 
                            newthread = ClientThread(sock, ip, port, parent=self, id=id,
                                                                                                        filter = self.filter, filterTime = self.filterTime, destIp=self.destIp)
                            newthread.start()
                            self.clientsThreads[(ip, port)] = {'thread': newthread, 'id': id }
                    else:
                        self.onClientConnected(clientAddress=(ip, port), clientSocket=sock)
        except socket.error as e:
            pass
        except Exception as e:
            self.error( "on run %s" % str(e) )
        self.__mutex__.release()
        
    def onListening(self):
        """
        """
        self.debug( "is listening" )
        if self.cfg['agent-support']:
            self.islistening = True
            
        # log event
        tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.is_listening() )
        self.logRecvEvent( shortEvt = "listening", tplEvt = tpl )

    def onStopListening(self):
        """
        """
        self.debug( "stop listening" )
        self.islistening = False
        
        # log event
        tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.is_stopped() )
        self.logRecvEvent( shortEvt = "stopped", tplEvt = tpl )

    def onListeningFailed(self, errno, errstr):
        """
        """
        self.debug( "connection failed" )
        
        # log event
        tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.listening_failed(errno=str(errno), errstr=errstr) )
        self.logRecvEvent( shortEvt = "listening failed", tplEvt = tpl )
        
        # clean the socket
        if not self.cfg['agent-support']:
            self.cleanSockets()


    def onClientSocketError(self, clientAddress, e):
        """
        """
        self.error( "socket error: %s" % str(e) )
        
        # log event
        tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.generic_error() )
        self.logRecvEvent( shortEvt = "error", tplEvt = tpl )
        
        # clean the socket
        if not self.cfg['agent-support']:
            client = self.getClientByAddress(clientAddress=clientAddress)
            if client is not None:
                client.getSocket().close()

    def onClientConnected(self, clientAddress, clientSocket):
        """
        """
        (ip, port) = clientAddress
        self.debug( "new connection from %s" % str(clientAddress) )
        
        # log event
        id = self.getId()
        if self.logEventReceived:
            tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.client_connected(id=id), src=ip, srcP=port )
            self.logRecvEvent( shortEvt = "client #%s connected" % id, tplEvt = tpl )
        
        # start a independant thread 
        newthread = None
        if not self.cfg['agent-support']:
            newthread = ClientThread(clientSocket, ip, port, parent=self, id=id, filter = self.filter, filterTime = self.filterTime, destIp=self.destIp)
            newthread.start()
        
        self.clientsThreads[(ip, port)] = {'thread': newthread, 'id': id }
        
    def onClientDisconnected(self, clientAddress):
        """
        """
        (ip, port) = clientAddress
        self.debug( "client disconnected: %s" % str(clientAddress) )
        
#       if not self.cfg['agent-support']:
        client = self.getClientByAddress(clientAddress=clientAddress)
        if client is not None:
            id = client['id']
            self.clientsThreads.pop(clientAddress)
    
        # log event
        if self.logEventReceived:
            tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.client_disconnected(id=id), src=ip, srcP=port  )
            self.logRecvEvent( shortEvt = "client #%s disconnected" % id, tplEvt = tpl )
        
    def onClientIncomingData(self, clientAddress, data, lower=None):
        """
        Function to overwrite
        Called on incoming data

        @param clientAddress: client id (ip,port)
        @type clientAddress: tuple
        
        @param data: tcp data received
        @type data: string
        
        @param lower: template tcp data received
        @type lower: templatemessage
        """
        pass
    
    def onClientNoMoreData(self, clientAddress, lower=None):
        """
        Function to reimplement

        @param clientAddress: client id (ip,port)
        @type clientAddress: tuple
        
        @param lower:
        @type lower: templatemessage
        """
        pass    
        

    def getExpectedTemplate(self, tpl, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
        """
        Return an expected template with ip and tcp layers
        """
        # prepare layers
        defaultVer = self.cfg['sock-family']
        if versionIp is not None:
            defaultVer = versionIp
        layer_ip = AdapterIP.ip( source=sourceIp, destination=destinationIp, version=defaultVer )       
        layer_tcp = templates.tcp(source=sourcePort, destination=destinationPort)
        layer_tcp.addMore(more=tpl)
        
        # prepare template
        if self.cfg['agent-support']:
            layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
            layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
            layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
            
        # prepare template
        tpl = TestTemplatesLib.TemplateMessage()
        if self.cfg['agent-support']:
            tpl.addLayer(layer=layer_agent)
        tpl.addLayer(layer=layer_ip)
        tpl.addLayer(layer=layer_tcp)
        return tpl
        
    @doc_public
    def sendData(self, clientId, data):
        """
        Send data

        @param clientId: client id number 
        @type clientId: integer/string
        
        @param data: data to send over tcp
        @type data: string

        @return: tcp layer encapsulate in ip
        @rtype: templatemessage
        """
        if not self.islistening:
            self.debug( "not listening " )
            return
        
        # find the client 
        if self.cfg['agent-support']:
            (ip,port)  = self.getClientAddrById(id=int(clientId))
        else:
            client = self.getClientById(id=int(clientId))
            if client is None:
                self.debug( "clients knowned: %s" % self.clientsThreads)
                self.error( "client id %s does not exist!" % clientId )
                return
            (ip,port) = client.getAddress()
        
        # add the separator to the end of the data, if the feature is enabled   
        if self.cfg['sep-disabled']:
            pdu = data
        else:
            pdu = data + self.cfg['sep-out']
        
        pdu_size = len(pdu)

        if self.cfg['ssl-support']:
            encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data_length=str(pdu_size)) )
            tpl = self.ssl.sendData(decodedData=data, tpl=encap, msg="client #%s data" % clientId )
        else:
            # log event
            if self.logEventSent:
                tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data=pdu, data_length=str(pdu_size), id=clientId), src=ip, srcP=port )
            else:
                tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data_length=str(pdu_size), id=clientId), src=ip, srcP=port )
            if self.logEventSent:
                tpl.addRaw(raw=pdu)
                self.logSentEvent( shortEvt = "client #%s data" % clientId, tplEvt = tpl )
    
        # enqueue pdu
        if self.cfg['agent-support']:
            remote_cfg = {'cmd': 'send-data', 'payload': pdu, 'to-ip':ip, 'to-port': port}
            self.sendNotifyToAgent(data=remote_cfg)
        else:
            client.queueTcp.put( pdu )
        return tpl  
    @doc_public
    def isListening(self, timeout=1.0):
        """
        Wait to receive "listening" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float        

        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
        
        # construct the expected template
        tpl = templates.is_listening()
        expected = self.getExpectedTemplate(tpl=tpl)
        
        # try to match the template 
        evt = self.received( expected=expected, timeout=timeout )
        return evt
    @doc_public
    def isListeningFailed(self, timeout=1.0):
        """
        Wait to receive "listening failed" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float        
        
        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
        
        # construct the expected template
        tpl = templates.listening_failed()
        expected = self.getExpectedTemplate(tpl=tpl)
        
        # try to match the template 
        evt = self.received( expected=expected, timeout=timeout )
        return evt
        
    @doc_public
    def isStopped(self, timeout=1.0):
        """
        Wait to receive "stopped" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float        

        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
        
        # construct the expected template
        tpl = templates.is_stopped()
        expected = self.getExpectedTemplate(tpl=tpl)
        
        # try to match the template 
        evt = self.received( expected=expected, timeout=timeout )
        return evt
    
    @doc_public
    def hasClientConnection(self, timeout=1.0, clientId=None):
        """
        Wait to receive "new client connection" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float        

        @param clientId: client id number
        @type clientId: integer/None
        
        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
        
        # construct the expected template
        tpl = templates.client_connected(id=clientId)
        expected = self.getExpectedTemplate(tpl=tpl)
        
        # try to match the template 
        evt = self.received( expected=expected, timeout=timeout )
        return evt
        
    @doc_public
    def hasClientDisconnection(self, timeout=1.0, clientId=None):
        """
        Wait to receive "client disconnection" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float        
        
        @param clientId: client id number
        @type clientId: integer/None
        
        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
        
        # construct the expected template
        tpl = templates.client_disconnected(id=clientId)
        expected = self.getExpectedTemplate(tpl=tpl)
        
        # try to match the template 
        evt = self.received( expected=expected, timeout=timeout )
        return evt
    @doc_public
    def hasClientData(self, timeout=1.0, clientId=None, data=None, versionIp=None, sourceIp=None, destinationIp=None, 
                                                    sourcePort=None, destinationPort=None, sslVersion=None, sslCipher=None):
        """
        Waits to receive "data" event until the end of the timeout
        
        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float    

        @param clientId: client id number
        @type clientId: integer/None
        
        @param data: data expected
        @type data: string/operators/none   
    
        @param versionIp: version ip expected
        @type versionIp: string/operators/none  

        @param sourceIp: source ip expected
        @type sourceIp: string/operators/none   
        
        @param destinationIp: destination ip expected
        @type destinationIp: string/operators   
        
        @param sourcePort: source port expected
        @type sourcePort:   string/operators/none

        @param destinationPort: destination port expected
        @type destinationPort: string/operators 

        @return: an event matching with the template or None otherwise
        @rtype: templatemessage     
        """
        if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
        
        if self.cfg['ssl-support']:
            tpl = templates.received()
        else:
            tpl = templates.received(data=data, id=clientId)
        expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
                                                                                sourcePort=sourcePort, destinationPort=destinationPort)
        
        if self.cfg['ssl-support']:
            evt = self.ssl.hasReceivedData(tpl=expected, timeout=timeout, data=data, sslVersion=sslVersion, sslCipher=sslCipher)
        else:
            evt = self.received( expected = expected, timeout = timeout )
        return evt