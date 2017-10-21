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
from TestExecutorLib.TestExecutorLib import doc_public

import sys

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapterLib.getVersion()]
AdapterDNS = sys.modules['SutAdapters.%s.DNS' % TestAdapterLib.getVersion()]
AdapterSOCKS = sys.modules['SutAdapters.%s.SOCKS' % TestAdapterLib.getVersion()]

import threading
import socket
import select
import time
import Queue
import templates


__NAME__="""TCP"""

PROXY_HTTP = 'http'
PROXY_SOCKS4 = 'socks4'
PROXY_SOCKS5 = 'socks5'

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, bindIp = '', bindPort=0, name=None,
								destinationIp='127.0.0.1', destinationPort=0,  destinationHost='', 
								proxyType=PROXY_SOCKS4, proxyUserID='xtc', proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False,
								socketTimeout=30, socketFamily=AdapterIP.IPv4, inactivityTimeout=30.0,
								tcpKeepAlive=False, tcpKeepAliveInterval=30.0,
								separatorIn='\\x00', separatorOut='\\x00', separatorDisabled=False, 
								sslSupport=False, sslVersion=AdapterSSL.SSLv23, checkCert=AdapterSSL.CHECK_CERT_NO,
								debug=False, logEventSent=True, logEventReceived=True, parentName=None,
								agentSupport=False, agent=None, shared=False, 
								caCerts=None, checkHost=False, hostCn=None, verbose=True, 
								certfile=None, keyfile=None
						):
		"""
		This class enable to use TCP as client only, with support and dns resolution.
		Proxy socks4 and socks5 supported.
		Lower network layer (IP, Ethernet) are not controlable.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer

		@param destinationIp: destination ip
		@type destinationIp: string

		@param destinationPort: destination port
		@type destinationPort: integer

		@param destinationHost: destination host (automatic dns resolution)
		@type destinationHost: string
		
		@param proxyType: SutAdapters.TCP.PROXY_HTTP | SutAdapters.TCP.PROXY_SOCKS4 | SutAdapters.TCP.PROXY_SOCKS5 (default=PROXY_SOCKS4)
		@type proxyType: strconstant
		
		@param proxyUserID: user id with socks (default=xtc)
		@type proxyUserID: string
		
		@param proxyIp: proxy ip
		@type proxyIp: string

		@param proxyPort: proxy port
		@type proxyPort: integer

		@param proxyHost: proxy host (automatic dns resolution)
		@type proxyHost: string
		
		@param proxyEnabled: True to support proxy (default=False)
		@type proxyEnabled: boolean
		
		@param socketTimeout: timeout to connect in second (default=1s)
		@type socketTimeout: float

		@param socketFamily: SutAdapters.IP.IPv4 (default)| SutAdapters.IP.IPv6 
		@type socketFamily: intconstant

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

		@param sslVersion: SutAdapters.SSL.SSLv2 | SutAdapters.SSL.SSLv23 (default) | SutAdapters.SSL.SSLv3 | SutAdapters.SSL.TLSv1 | SutAdapters.SSL.TLSv11  | SutAdapters.SSL.TLSv12 
		@type sslVersion: strconstant

		@param checkCert: SutAdapters.SSL.CHECK_CERT_NO | SutAdapters.SSL.CHECK_CERT_OPTIONAL | SutAdapters.SSL.CHECK_CERT_REQUIRED
		@type checkCert: strconstant
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param caCerts: path to the ca certificates (default=None)
		@type caCerts: string/none
		
		@param checkHost: validate the common name field (default=False)
		@type checkHost: boolean
		
		@param hostCn: common name to check (default=None)
		@type hostCn: string/none

		@param certfile: path to the cert file (default=None)
		@type certfile: string/none

		@param keyfile: path to the key file (default=None)
		@type keyfile: string/none
		"""
		# check agent
		if agentSupport and agent is None:
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent cannot be undefined!" )
			
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
				
		if not isinstance(bindPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "bindPort argument is not a integer (%s)" % type(bindPort) )
		if not isinstance(destinationPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "destinationPort argument is not a integer (%s)" % type(destinationPort) )
		if not isinstance(proxyPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "proxyPort argument is not a integer (%s)" % type(proxyPort) )
		
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, 
																			shared=shared, realname=name, agentSupport=agentSupport, agent=agent, showEvts=verbose, 
																			showSentEvts=verbose, showRecvEvts=verbose)
		if parentName is not None:
			TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__)  )
		self.__mutex__ = threading.RLock()
		self.queueTcp = Queue.Queue(0)
		self.parent = parent
		self.connected = False	
		self.isreading = True
		self.socket = None
		self.sourceIp = bindIp
		self.sourcePort = bindPort
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.proxyRspReceived = False
		self.proxyRspWait = False
		self.proxyNegoReceived = False

		self.buf = ''
		
		self.cfg = {}
		# transport options
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		self.cfg['dst-ip'] = destinationIp
		self.cfg['dst-port'] = destinationPort
		self.cfg['dst-host'] = destinationHost
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
		# proxy
		self.cfg['proxy-enabled'] = proxyEnabled
		self.cfg['proxy-ip'] = proxyIp
		self.cfg['proxy-host'] = proxyHost
		self.cfg['proxy-port'] = proxyPort
		self.cfg['proxy-userid'] = proxyUserID
		self.cfg['proxy-type'] = proxyType
		
		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		
		# ssl support
		self.cfg['ssl-support'] = sslSupport
		self.ssl = AdapterSSL.Client(parent=parent, sslVersion=sslVersion, checkCert=checkCert,	debug=debug,
																						logEventSent=logEventSent, logEventReceived=logEventReceived, 
																						shared=shared, name=name, caCerts=caCerts, checkHost=checkHost, 
																						host=hostCn, verbose=verbose,
																						keyfile=keyfile,certfile=certfile)
		
		# dns client
		self.dns = AdapterDNS.Client(parent=parent, debug=debug, logEventSent=True, logEventReceived=True,
																shared=shared, name=name, verbose=verbose)
		
		self.socks = AdapterSOCKS.Client( parent=parent, debug=debug,name=name, proxyType=proxyType, verbose=verbose)
		
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()

		if agentSupport:
			self.prepareAgent(data={'shared': shared})
			if self.agentIsReady(timeout=30) is None:
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
			self.TIMER_ALIVE_AGT.start()

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

		try:
			self.cfg['dst-port'] = int(self.cfg['dst-port'])
		except Exception as e:
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(), "config tcp: wrong destination port type: %s" % str(self.cfg['dst-port']) )
			
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
	
	def setDestination(self, destinationIp, destinationPort,  destinationHost=''):
		"""
		Set the destination ip/port or host/port
		
		@param destinationIp: destination ip
		@type destinationIp: string

		@param destinationPort: destination port
		@type destinationPort: integer		

		@param destinationHost: destination host (automatic dns resolution)
		@type destinationHost: string
		"""
		self.cfg['dst-ip'] = destinationIp
		self.cfg['dst-port'] = destinationPort
		self.cfg['dst-host'] = destinationHost
		if self.cfg['dst-host'] != '':
			self.cfg['dst-ip'] = self.dns.resolveHost(host=self.cfg['dst-host'])
	
	def setProxyDestination(self, destinationIp, destinationPort, destinationHost=''):
		"""
		Set the destination ip/port or host/port for the proxy
			
		@param destinationIp: destination ip
		@type destinationIp: string
	
		@param destinationPort: destination port
		@type destinationPort: integer		
	
		@param destinationHost: destination host (automatic dns resolution)
		@type destinationHost: string
		"""
		self.cfg['proxy-enabled'] = True
		self.cfg['proxy-ip'] = destinationIp
		self.cfg['proxy-port'] = destinationPort
		self.cfg['proxy-host'] = destinationHost
		if self.cfg['proxy-host'] != '':
			self.cfg['proxy-ip'] = self.dns.resolveHost(host=self.cfg['proxy-host'])	
		
	def encapsule(self, ip_event, tcp_event):
		"""
		"""
		# prepare layers
		src = self.sourceIp
		dst = self.cfg['dst-ip']
		srcP = self.sourcePort
		dstP = self.cfg['dst-port']
		
		if self.cfg['proxy-enabled']:
			dst = self.cfg['proxy-ip']
			dstP = self.cfg['proxy-port']
			
		if ip_event == AdapterIP.received():
			src = self.cfg['dst-ip']
			dst = self.sourceIp
			srcP = self.cfg['dst-port']
			dstP = self.sourcePort
			
			if self.cfg['proxy-enabled']:
				src = self.cfg['proxy-ip']
				srcP = self.cfg['proxy-port']
			
		layer_ip = AdapterIP.ip( source=src, destination=dst, version=str(self.cfg['sock-family']), more=ip_event ) 
		layer_tcp = templates.tcp(source=srcP, destination=dstP)
		layer_tcp.addMore(more=tcp_event)
		
		# prepare template
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_tcp)
		
		if self.cfg['proxy-enabled']:
			if self.proxyRspReceived:
				if ip_event == AdapterIP.received():
					sock_more = AdapterSOCKS.received()
				else:
					sock_more = AdapterSOCKS.sent()
				layer_sock = AdapterSOCKS.socks(
																				more=sock_more,
																				remotePort=self.cfg['dst-port'], remoteAddress=self.cfg['dst-ip'],
																				type=self.cfg['proxy-type']
																			)
				tpl.addLayer(layer=layer_sock)
				
		return tpl
	
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
				elif data['tcp-event'] == 'connected':
					self.onConnection()
				elif data['tcp-event'] == 'connection-timeout':
					self.onConnectionTimeout(e=data['more'])	
				elif data['tcp-event'] == 'no-more-data':
					self.onIncomingData(noMoreData=True)		
				elif data['tcp-event'] == 'connection-refused':
					self.onConnectionRefused()	
				elif data['tcp-event'] == 'connection-failed':
					self.onConnectionFailed(errno=data['err-no'], errstr=data['err-str'])		
				elif data['tcp-event'] == 'disconnected-by-peer':
					self.onDisconnectionByPeer(e=data['more'])
				elif data['tcp-event'] == 'closed':
					self.onDisconnection()		
				else:
					self.error("agent mode - tcp event unknown on notify: %s" % data['tcp-event'] )
			
			if 'ssl-event' in data:
				s_encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent() )
				r_encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received() )
				if data['ssl-event'] == 'handshake':
					self.ssl.logHandshake( tpl_s=s_encap )
				elif data['ssl-event'] == 'handshake-accepted':
					self.ssl.logHandshakeAccepted(tpl_r=r_encap, cipher=data['cipher'], version=data['version'],
																		bits=data['bits'], certpem=data['cert-pem'])		
				elif data['ssl-event'] == 'handshake-failed':
					self.ssl.logHandshakeFailed(tpl_r=r_encap, err=data['error'])
					self.onSslHandshakeFailed()					

				else:
					self.error("agent mode - ssl event unknown on notify: %s" % data['ssl-event'] )
					
	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if 'tcp-event' in data:
			if data['tcp-event'] == 'on-run':
				self.error( "error: %s" % data['more'] )
			elif data['tcp-event'] == 'socket-error':
				self.onSocketError(e=data['more'])
			elif data['tcp-event'] == 'connect-error':
				self.error( "connect error: %s" % data['more'] )
				self.disconnect()
			elif data['tcp-event'] == 'sending-error':
				self.error( data['more'])
			else:
				self.error("agent mode - tcp event unknown on error: %s" % data['tcp-event'] )

	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.lastActivity = time.time()
		if self.cfg['sep-disabled']:
			self.onIncomingData(data=data)
		else:
			self.buf = ''.join([self.buf, data])
			self.onIncomingData()
		
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
	@doc_public
	def connect(self):
		"""
		Start the TCP connection
		"""
		self.proxyRspReceived = False
		self.proxyRspWait = False
		self.proxyNegoReceived = False
		
		if self.connected:
			self.debug( 'already connected' )
			return 

		# Optional: resolve hostname
		if self.cfg['dst-host'] != '':
			self.cfg['dst-ip'] = self.dns.resolveHost(host=self.cfg['dst-host'])
			if not len(self.cfg['dst-ip']):
				return 
				
		# Optional: resolve hostname for proxy
		if self.cfg['proxy-enabled']:
		  if self.cfg['proxy-host'] != '':
		     self.cfg['proxy-ip'] = self.dns.resolveHost(host=self.cfg['proxy-host'])
		     if not len(self.cfg['proxy-ip']):
		        return

		# Start the tcp connection
		self.debug( 'connection started' )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.connection() )
		self.logSentEvent( shortEvt = "connection", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': 'connect',
							'sock-type': 'tcp', 
							'bind-ip': self.cfg['bind-ip'], 'bind-port': self.cfg['bind-port'],
							'sock-timeout': self.cfg['sock-timeout'], 'tcp-keepalive': self.cfg['tcp-keepalive'],
							'tcp-keepalive-interval': self.cfg['tcp-keepalive-interval'] ,
							'sock-family': self.cfg['sock-family'],
							'dst-ip': self.cfg['dst-ip'], 'dst-port':self.cfg['dst-port'],
							'ssl-support': self.cfg['ssl-support'], 'ssl-version': self.ssl.cfg['ssl-version'],
							'check-cert': self.ssl.cfg['check-cert'],
							'ca-certs': self.ssl.cfg['ca-certs'], 'host': self.ssl.cfg['host'],
							'check-host': self.ssl.cfg['check-host'],
						}
			self.sendNotifyToAgent(data=remote_cfg)
			
			# start thread
			self.lastActivity = time.time()
			self.setRunning()
		else:
			try:
				# set the socket version
				if self.cfg['sock-family'] == AdapterIP.IPv4:
					sockType = TestAdapterLib.INIT_STREAM_SOCKET
				elif  self.cfg['sock-family'] == AdapterIP.IPv6:
					sockType = TestAdapterLib.INIT6_STREAM_SOCKET
				else:
					raise Exception('socket family unknown: %s' % str(self.cfg['sock-family']) )	
				
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
				self.debug( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
				self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
	
				# Optional: initialize the ssl
				if self.cfg['ssl-support'] and not self.cfg['proxy-enabled']:
					self.socket = self.ssl.initSocketSsl(sock=self.socket)
					
				# Connect the socket
				if self.cfg['proxy-enabled']:
					self.socket.connect( (self.cfg['proxy-ip'], self.cfg['proxy-port']) )
				else:
					self.socket.connect( (self.cfg['dst-ip'], self.cfg['dst-port']) )
				
				# Connection successful
				self.__setSource()	
				self.lastActivity = time.time()
				self.connected = True
				self.onConnection()
				
				# Optional: do ssl handshake
				if self.cfg['ssl-support']  and not self.cfg['proxy-enabled']:
					try:
						s_encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent() )
						r_encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received() )
						self.ssl.doSslHandshake(sock=self.socket, tpl_s=s_encap, tpl_r=r_encap)
					except AdapterSSL.HandshakeFailed:
						self.onSslHandshakeFailed()
					else:
						self.onSslConnection()
						
				# start thread
				self.setRunning()
			except socket.timeout as e:
				self.onConnectionTimeout(e)
			except socket.error as e:
				(errno, errstr) = e
				if errno == 111:
					self.onConnectionRefused()
				elif errno == 104: # 'Connection reset by peer'
					self.onDisconnectionByPeer( e=errstr )
				else:
					self.onConnectionFailed(errno=errno, errstr=errstr)
			except Exception as e:
				self.error( "connect error: %s" % str(e) )
				self.disconnect()
	
	@doc_public
	def startSsl(self):
		"""
		"""
		if self.cfg['ssl-support']:
			self.socket = self.ssl.initSocketSsl(sock=self.socket)
			try:
				s_encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent() )
				r_encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received() )
				self.ssl.doSslHandshake(sock=self.socket, tpl_s=s_encap, tpl_r=r_encap)
			except AdapterSSL.HandshakeFailed:
				self.onSslHandshakeFailed()
			else:
				self.onSslConnection()
				
	@doc_public
	def connection(self, timeout=1.0):
		"""
		Tcp connection and wait the connection event until the end of the timeout
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: connection result
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		self.connect()
		if self.isConnected(timeout=timeout) is None:
			return False
		
		if self.cfg['ssl-support']:
			if self.isConnectedSsl(timeout=timeout) is None:
				return False
				
		return ret
		
	@doc_public
	def disconnection(self, timeout=1.0):
		"""
		Tcp disconnection and wait the disconnection event until the end of the timeout
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: disconnection result
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		self.disconnect()
		if self.isDisconnected(timeout=timeout) is None:
			ret = False
		return ret
		
	@doc_public
	def disconnect(self):
		"""
		Close the TCP connection
		"""
		self.proxyRspReceived = False
		self.proxyRspWait = False
		self.proxyNegoReceived = False
		
		self.__mutex__.acquire()
		if self.connected:
			self.debug( 'disconnection started' )
			
			# log event
			tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.disconnection() )
			self.logSentEvent( shortEvt = "disconnection", tplEvt = tpl )
		
			if self.cfg['agent-support']:
				self.unsetRunning()
				# stop timer
				self.TIMER_ALIVE_AGT.stop()

				# cleanup remote agent
				remote_cfg = {'cmd': 'disconnect'}
				self.sendNotifyToAgent(data=remote_cfg)
				#self.resetAgent()
			else:
				self.cleanSocket()
				self.onDisconnection()
		self.__mutex__.release()
			
	def cleanSocket(self):
		"""
		"""
		self.debug( 'clean the socket' )
		self.unsetRunning()
		# clean the socket
		if self.socket is not None:
			self.socket.close()
			self.connected = False

	def onReset(self):
		"""
		Reset
		"""
		self.stopRunning()
		self.disconnect()
		
		if self.cfg['agent-support']:
			# stop timer
			self.TIMER_ALIVE_AGT.stop()
#			self.resetAgent()
			remote_cfg = {'cmd': 'disconnect'}
			self.sendNotifyToAgent(data=remote_cfg)
			
	@doc_public
	def startRead(self):
		"""
		Start read data from the socket
		"""
		self.isreading = True
	
	@doc_public
	def stopRead(self):
		"""
		Stop read data on the socket
		"""
		self.isreading = False
		
	def proxyInitialized(self):
		"""
		"""
		self.proxyRspReceived = True
		
	def onRun(self):
		"""
		"""
		self.__mutex__.acquire()
		try:
			if self.cfg['agent-support']:
					if self.connected:
						if self.isreading:
							if self.cfg['inactivity-timeout']:
								if time.time() - self.lastActivity > self.cfg['inactivity-timeout']:
									raise EOFError("inactivity timeout: disconnecting")	
			else:
				# check if we have incoming data
				if self.socket is not None:  
						if self.connected:
							if self.isreading:			
								r, w, e = select.select([ self.socket ], [], [ self.socket ], 0.01)
								if self.socket in e:
										raise EOFError("socket select error: disconnecting")
								elif self.socket in r:
										read = self.socket.recv(1024*1024)
										if not read:
											self.onIncomingData(noMoreData=True)
											raise EOFError("nothing to read: disconnecting")
										self.debug( '%d bytes received' % len(read) )
										self.lastActivity = time.time()
										if self.cfg['sep-disabled']:
											self.onIncomingData(data=read)
										else:
											self.buf = ''.join([self.buf, read])
											self.onIncomingData()
								
								# Check inactivity timeout
								elif self.cfg['inactivity-timeout']:
										if time.time() - self.lastActivity > self.cfg['inactivity-timeout']:
												raise EOFError("inactivity timeout: disconnecting")
		
								# send queued messages
								while not self.queueTcp.empty():
										r, w, e = select.select([ ], [ self.socket ], [ self.socket ], 0.01)
										if self.socket in e:
												raise EOFError("socket select error when sending a message: disconnecting")
										elif self.socket in w: 
												try:
														message = self.queueTcp.get(False)
														try:
															self.socket.sendall(message)
														except UnicodeError:
															self.socket.sendall(message.encode('utf-8'))
														self.debug( "packet sent" )
												except Queue.Empty:
														pass
												except Exception as e:
														self.error("unable to send message: " + str(e))
										else:
												break
		except EOFError as e:
			if self.cfg['agent-support']:
				self.onInactivityDetected()
			else:
				self.onDisconnectionByPeer(e)
		except socket.error as e:
			(errno, errstr) = e
			if errno == 104: # 'Connection reset by peer'
				self.onDisconnectionByPeer( e=errstr )
			else:
				self.onSocketError(e)
		except Exception as e:
			self.error( "on run %s" % str(e) )
		self.__mutex__.release()
		
	def onSslConnection(self):
		"""
		"""
		pass
	def onConnection(self):
		"""
		"""
		self.debug( "connected" )
		if self.cfg['agent-support']:
			self.connected = True
			
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.connected() )
		self.logRecvEvent( shortEvt = "connected", tplEvt = tpl )
		
		if self.cfg['proxy-enabled']:
			self.debug( "proxy to initialize" )
			self.onProxyInitialization()

	def onHttpProxyInitialization(self):
		"""
		"""
		pass
		
	def onProxyInitialization(self):
		"""
		Function to overwrite
		"""		
		if self.cfg['proxy-type'] == PROXY_HTTP:
			self.onHttpProxyInitialization()
		else:
			self.proxyRspWait = True
			if self.cfg['proxy-type'] == PROXY_SOCKS5:
				self.negoProxy()
			else:
				self.connectProxy()
	
	def negoProxy(self):
		"""
		"""
		tpl_sock, req_raw, summary = self.socks.prepareNego()	
		pdu_size = len(req_raw)
		if self.cfg['ssl-support']:
			encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data_length=str(pdu_size)) )
			tpl = self.ssl.sendData(decodedData=req_raw, tpl=encap)
		else:
			# log event
			tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data=req_raw, data_length=str(pdu_size)) )
			tpl.addLayer( tpl_sock )
			tpl.addRaw(raw=req_raw)
			self.logSentEvent( shortEvt = summary, tplEvt = tpl )
	
		# enqueue pdu
		try:
			if self.cfg['agent-support']:
				remote_cfg = {'cmd': 'send-data', 'payload': req_raw}
				self.sendNotifyToAgent(data=remote_cfg)
			else:
				self.queueTcp.put( req_raw )
		except Exception as e:
			self.error("unable to enqueue sock req to send: %s" % str(e) )
			
	def connectProxy(self):
		"""
		"""		
		if self.cfg['proxy-type'] == PROXY_SOCKS5:
			#			IP V4 address: X'01'
			#			DOMAINNAME: X'03'
			#			IP V6 address: X'04'
			tpl_sock, req_raw, summary = self.socks.prepareConnect(
																			destinationPort=self.cfg['dst-port'],
																			destinationIp=self.cfg['dst-ip'],
																			destinationType=1,
																			reserved=0
													)	
		else:
			
			self.cfg['dst-ip'] = self.dns.resolveHost(host=self.cfg['dst-ip'])
			if not len(self.cfg['dst-ip']):
				raise Exception("resolution failed for proxy")
			tpl_sock, req_raw, summary = self.socks.prepareConnect(
																			userId=self.cfg['proxy-userid'], 
																			destinationPort=self.cfg['dst-port'],
																			destinationIp=self.cfg['dst-ip']
													)	
		
		pdu_size = len(req_raw)
		if self.cfg['ssl-support']:
			encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data_length=str(pdu_size)) )
			tpl = self.ssl.sendData(decodedData=req_raw, tpl=encap)
		else:
			# log event
			tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data=req_raw, data_length=str(pdu_size)) )
			tpl.addLayer( tpl_sock )
			tpl.addRaw(raw=req_raw)
			self.logSentEvent( shortEvt = summary, tplEvt = tpl )
	
		# enqueue pdu
		try:
			if self.cfg['agent-support']:
				remote_cfg = {'cmd': 'send-data', 'payload': req_raw}
				self.sendNotifyToAgent(data=remote_cfg)
			else:
				self.queueTcp.put( req_raw )
		except Exception as e:
			self.error("unable to enqueue sock req to send: %s" % str(e) )
	
	def onInactivityDetected(self):
		"""
		"""
		self.unsetRunning()
#		self.resetAgent()
		if self.cfg['agent-support']:
			remote_cfg = {'cmd': 'disconnect'}
			self.sendNotifyToAgent(data=remote_cfg)
		
	def onDisconnection(self):
		"""
		"""
		self.debug( "disconnected" )
		if self.cfg['agent-support']:
			self.connected = False
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.disconnected() )
		self.logRecvEvent( shortEvt = "disconnected", tplEvt = tpl )
		
	def onDisconnectionByPeer(self, e):
		"""
		"""
		self.debug("disconnected by the server: %s" % str(e) )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.disconnected_by_server() )
		self.logRecvEvent( shortEvt = "disconnected by peer", tplEvt = tpl )
		
		if not self.cfg['agent-support']:
			# clean the socket
			self.cleanSocket()

	def onConnectionRefused(self):
		"""
		"""
		if not self.cfg['agent-support']:
			self.__setSource()	
		self.debug( "connection refused" )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.connection_refused() )
		self.logRecvEvent( shortEvt = "connection refused", tplEvt = tpl )
		
		if not self.cfg['agent-support']:
			# clean the socket
			self.cleanSocket()

	def onConnectionTimeout(self, e):
		"""
		"""
		if not self.cfg['agent-support']:
			self.__setSource()
		self.debug( "connection timeout: %s" % str(e) )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.connection_timeout() )
		self.logRecvEvent( shortEvt = "connection timeout", tplEvt = tpl )
		
		if not self.cfg['agent-support']:
			# clean the socket
			self.cleanSocket()

	def onConnectionFailed(self, errno, errstr):
		"""
		"""
		self.debug( "connection failed" )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.connection_failed(errno=str(errno), errstr=errstr) )
		self.logRecvEvent( shortEvt = "connection failed", tplEvt = tpl )
		
		if not self.cfg['agent-support']:
			# clean the socket
			self.cleanSocket()


	def onSocketError(self, e):
		"""
		"""
		self.error( "socket error: %s" % str(e) )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.generic_error() )
		self.logRecvEvent( shortEvt = "error", tplEvt = tpl )
		
		if not self.cfg['agent-support']:
			# clean the socket
			self.cleanSocket()

	
	def onSslHandshakeFailed(self):
		"""
		"""
		self.disconnect()
	
	@doc_public
	def sendData(self, data):
		"""
		Send data over the tcp channel

		@param data: data to send over tcp
		@type data: string

		@return: tcp layer encapsulate in ip, return False if failed
		@rtype: templatemessage
		"""
		if not self.connected:
			self.debug( "not connected" )
			return False
		
		# add the separator to the end of the data, if the feature is enabled	
		if self.cfg['sep-disabled']:
			pdu = data
		else:
			pdu = data + self.cfg['sep-out']
		
		pdu_size = len(pdu)
		
		if self.cfg['ssl-support']:
			encap = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data_length=str(pdu_size)) )
			tpl = self.ssl.sendData(decodedData=data, tpl=encap)
		else:
			# log event
			if self.logEventSent:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data=pdu, data_length=str(pdu_size)) )
			else:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), tcp_event=templates.sent(data_length=str(pdu_size)) )
			if self.logEventSent:
				tpl.addRaw(raw=pdu)
				self.logSentEvent( shortEvt = "data", tplEvt = tpl )
		
		# enqueue pdu
		try:
			if self.cfg['agent-support']:
				remote_cfg = {'cmd': 'send-data', 'payload': pdu}
				self.sendNotifyToAgent(data=remote_cfg)
			else:
				self.queueTcp.put( pdu )
		except Exception as e:
			self.error("unable to enqueue data to send: %s" % str(e) )
			return False
		return tpl

	def onIncomingData(self, data=None, noMoreData=False):
		"""
		Called on incoming data
		"""
		# decode response from proxy
		if self.proxyRspWait:
			if data is None:
				return
			
			pdu_size = len(data)
			self.debug( '%s data received' % len(data) )
			
			if self.cfg['proxy-type'] == PROXY_SOCKS5:
				doConnect = False
				rspSocks5received = False
				if not self.proxyNegoReceived:
					sock_tpl, summary = self.socks.codec().decodenego(sock=data)
					self.proxyNegoReceived = True
					doConnect = True
				else:
					self.proxyRspWait = False
					sock_tpl, summary = self.socks.codec().decode(sock=data)
					rspSocks5received = True
					
			else: # socks version 4
				self.proxyRspWait = False
				sock_tpl, summary = self.socks.codec().decode(sock=data)
					

			# log response
			if self.cfg['ssl-support']:
				encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size)) )
				tpl = self.ssl.onIncomingDecodedData(data=data, tpl=encap)
			else:
				tpl = self.encapsule( ip_event=AdapterIP.received(), 
															tcp_event=templates.received(data=data, data_length=str(pdu_size))	)
			
			tpl.addLayer( sock_tpl )
			tpl.addRaw(raw=data)
			self.logRecvEvent( shortEvt = summary, tplEvt = tpl )

			if self.cfg['proxy-type'] == PROXY_SOCKS4:
				self.proxyRspReceived = True
				
			if self.cfg['proxy-type'] == PROXY_SOCKS5:
				if rspSocks5received:
					self.proxyRspReceived = True
					
			if self.cfg['proxy-type'] == PROXY_SOCKS5 and self.proxyNegoReceived:
				if doConnect:
					self.connectProxy()
				
			
		# decode real tcp data		
		else:
			try:
				if noMoreData:
					if self.cfg['ssl-support']:
						tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received() )
						lower = self.ssl.encapsule(tpl=tpl, ssl_event=AdapterSSL.received()) 
					else:
						lower = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received() )
					self.handleNoMoreData(lower=lower)
				else:
					if data is not None: # separator feature is disabled
						pdu_size = len(data)
						if self.cfg['ssl-support']:
							encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size)) )
							self.ssl.onIncomingDecodedData(data=data, tpl=encap)
						else:
							# log event
							tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data=data, data_length=str(pdu_size)) )
							if self.logEventReceived:
								tpl.addRaw(raw=data)
								self.logRecvEvent( shortEvt = "data", tplEvt = tpl )
						
						if self.cfg['ssl-support']:
							tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size)) )
							lower = self.ssl.encapsule(tpl=tpl, ssl_event=AdapterSSL.received()) 
						else:
							lower = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size)) )
						
						# handle data
						self.handleIncomingData( data, lower=lower )
					else: # separator feature is enabled, split the buffer by the separator
						datas = self.buf.split(self.cfg['sep-in'])
						for data in datas[:-1]:
							pdu = data+self.cfg['sep-in']
							pdu_size = len(pdu)
							if self.cfg['ssl-support']:
								encap = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data_length=str(pdu_size)) )
								tpl = self.ssl.onIncomingDecodedData(data=pdu, tpl=encap)
							else:
								# log event
								tpl = self.encapsule( ip_event=AdapterIP.received(), tcp_event=templates.received(data=pdu, data_length=str(pdu_size)) )
								if self.logEventReceived:
									tpl.addRaw(raw=pdu)
									self.logRecvEvent( shortEvt = "data", tplEvt = tpl )
							# handle data
							self.handleIncomingData( pdu, lower=tpl )
						self.buf = datas[-1]
			except Exception as e:
				self.error( str(e) )
			
	def handleIncomingData(self, data, lower=None):
		"""
		Function to overwrite
		Called on incoming data

		@param data: tcp data received
		@type data: string
		
		@param lower: template tcp data received
		@type lower: templatemessage
		"""
		pass
		
	def handleNoMoreData(self, lower):
		"""
		Function to reimplement

		@param lower:
		@type lower:
		"""
		pass
		
		
	def getExpectedTemplate(self, tpl, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Return an expected template with ip and tcp layers
		"""
		# prepare layers
		defaultVer = str(self.cfg['sock-family'])
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
			
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_tcp)
		if self.cfg['proxy-enabled']:
			if self.proxyRspReceived:
				layer_sock = AdapterSOCKS.socks(more=AdapterSOCKS.received())
				tpl.addLayer(layer=layer_sock)
			
		return tpl
		
	@doc_public
	def isAcceptedProxy(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "accepted proxy" event until the end of the timeout
		
		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		defaultVer = "%s"  % self.cfg['sock-family']
		if versionIp is not None:
			defaultVer = versionIp
		layer_ip = AdapterIP.ip( source=sourceIp, destination=destinationIp, version=defaultVer ) 		
		layer_tcp = templates.tcp(source=sourcePort, destination=destinationPort)
		layer_tcp.addMore(more=templates.received() )
		
		# prepare template
		expected = TestTemplatesLib.TemplateMessage()
		expected.addLayer(layer=layer_ip)
		expected.addLayer(layer=layer_tcp)
		
		if self.cfg['proxy-enabled']:
			if self.cfg['proxy-type'] == PROXY_SOCKS5:
				result = "0"
			else:
				result = "90"
			layer_sock = AdapterSOCKS.socks(more=AdapterSOCKS.received(), result=result)
			expected.addLayer(layer=layer_sock)
			
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isConnected(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.connected()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isConnectionRefused(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "connection refused" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.connection_refused()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isConnectionTimeout(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "connection timeout" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.connection_timeout()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isConnectionFailed(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None, errNo=None, errStr=None):
		"""
		Wait to receive "connection failed" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	

		@param errNo: error code
		@type errNo: string/operators

		@param errStr: error phrase
		@type errStr: string/operators
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.connection_failed(errno=errNo, errstr=errStr)
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isConnectedSsl(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None, sslVersion=None, sslCipher=None):
		"""
		Wait to receive "connected ssl" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators	

		@param sslVersion: ssl version expected
		@type sslVersion: string/operators/none
		
		@param sslCipher: ssl cipher expected
		@type sslCipher: string/operators/none
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.received()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.ssl.isConnected(tpl=expected, timeout=timeout,sslVersion=sslVersion,sslCipher=sslCipher)
		return evt
		
	@doc_public
	def isDisconnected(self, timeout=1.0, byServer=False, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Wait to receive "disconnected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@param byServer: indicate if the disconnection is initiated by the server
		@type byServer: boolean		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		if byServer:
			tpl = templates.disconnected_by_server()
		else:
			tpl = templates.disconnected()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp,
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def hasReceivedData(self, timeout=1.0, data=None, versionIp=None, sourceIp=None, destinationIp=None, 
													sourcePort=None, destinationPort=None, sslVersion=None, sslCipher=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param data: data expected
		@type data:	string/operators/none	
	
		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators	

		@param sslVersion: ssl version expected
		@type sslVersion: string/operators/none
		
		@param sslCipher: ssl cipher expected
		@type sslCipher: string/operators/none

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		if self.cfg['ssl-support']:
			tpl = templates.received()
		else:
			tpl = templates.received(data=data)
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 		
		if self.cfg['ssl-support']:
			evt = self.ssl.hasReceivedData(tpl=expected, timeout=timeout, data=data, sslVersion=sslVersion, sslCipher=sslCipher)
		else:		
			evt = self.received( expected = expected, timeout = timeout )
		return evt
