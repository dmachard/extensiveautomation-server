#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterDNS = sys.modules['SutAdapters.%s.DNS' % TestAdapterLib.getVersion()]

EXT_SSH_LIB_INSTALLED=True
try:
	import paramiko
except ImportError:
	EXT_SSH_LIB_INSTALLED=False
	
import threading
import select
import socket
try:
	import Queue
except ImportError: # python3 support
	import queue as Queue
import io

try:
	import templates
except ImportError: # python3 support
	from . import templates
	
__NAME__="""SSHv2"""

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='ssh'

class TransportSsh(object):
	def __init__(self):
		"""
		"""
		self.authenticated = False
	def is_authenticated(self):
		"""
		"""
		self.authenticated = True
		return self.authenticated
	def close(self):
		"""
		"""
		pass	
		
class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent,  destIp, destPort=22, bindIp = '0.0.0.0', bindPort=0,  destHost='',
									login='admin', password='admin', privateKey=None, privateKeyPath=None, verbose=True,
									socketTimeout=10.0, socketFamily=AdapterIP.IPv4,  name=None, tcpKeepAlive=True, tcpKeepAliveInterval=30,
									debug=False, logEventSent=True, logEventReceived=True, parentName=None, shared=False, sftpSupport=False,
									terminalType='vt100', terminalWidth=100, terminalHeight=200,
									agent=None, agentSupport=False):
		"""
		This class enable to use SSH v2 as client only,
		Authentication by login/password or by key are supported
		lower network layer (IP, Ethernet) are not controlable.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param login: ssh login (default=admin)
		@type login: string
		
		@param privateKey: string private key to use to authenticate, push your public key on the remote server
		@type privateKey: string/none
		
		@param privateKeyPath: path to the private key to use to authenticate, push your public key on the remote server
		@type privateKeyPath: string/none
		
		@param password: ssh password (default=admin)
		@type password: string
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer

		@param destIp: destination ip
		@type destIp: string

		@param destPort: destination port
		@type destPort: integer

		@param destHost: destination host (automatic dns resolution)
		@type destHost: string

		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: intconstant

		@param socketTimeout: timeout to connect in second (default=1s)
		@type socketTimeout: float

		@param tcpKeepAlive: turn on tcp keep-alive (defaut=False)
		@type tcpKeepAlive: boolean

		@param tcpKeepAliveInterval: tcp keep-alive interval (default=30s)
		@type tcpKeepAliveInterval: float
		
		@param terminalType: terminal type to emulate (default=vt100)
		@type terminalType: string
		
		@param terminalWidth: terminal width in characters (default=300)
		@type terminalWidth: integer
		
		@param terminalHeight: terminal height in characters  (default=300)
		@type terminalHeight: integer
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean

		@param agent: agent to use, ssh type expected
		@type agent: string/none
		
		@param agentSupport: agent support (default=False)
		@type agentSupport:	boolean
		"""
		if not isinstance(bindPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "bindPort argument is not a integer (%s)" % type(bindPort) )
		if not isinstance(destPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "destPort argument is not a integer (%s)" % type(destPort) )

		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																									realname=name, shared=shared, debug=debug, 
																									showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose,
																									agentSupport=agentSupport, agent=agent, 
																									caller=TestAdapterLib.caller(),
																									agentType=AGENT_TYPE_EXPECTED)
		if parentName is not None:
			TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__)  )
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.parent = parent
		self.__mutex__ = threading.RLock()
		if not EXT_SSH_LIB_INSTALLED:
			raise Exception('External ssh lib not installed!')
		
		# adding log
		if not agentSupport: paramiko.util.log_to_file("%s/sshlog.internal" % self.getTestResultPath() )
		
		self.socket = None
		self.sshTranport = None
		self.sshChannel = None
		self.sourceIp = bindIp
		self.sourcePort = bindPort
		self.connected = False
		self.channelOpened = False
		
		# sftp support
		self.sftpOpened = False
		self.sftpSupport = sftpSupport
		
		
		# dns client
		self.dns = AdapterDNS.Client(parent=parent, debug=debug, logEventSent=True, logEventReceived=True,
																							verbose=verbose, shared=shared, name=name)
	
		
		# ssh options
		self.cfg = {}	
		# transport options
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		self.cfg['dst-ip'] = destIp
		self.cfg['dst-port'] = destPort
		self.cfg['dst-host'] = destHost
		# tcp options
		self.cfg['tcp-keepalive'] = tcpKeepAlive
		self.cfg['tcp-keepalive-interval'] = tcpKeepAliveInterval
		# ssh 
		self.cfg['login'] = login
		self.cfg['password'] = password
		self.cfg['private-key'] = privateKey
		self.cfg['private-key-path'] = privateKeyPath
		# socket options
		self.cfg['sock-timeout'] =  socketTimeout
		self.cfg['sock-family'] =  int(socketFamily)
		
		self.cfg['terminal-type'] = terminalType
		self.cfg['terminal-width'] = terminalWidth
		self.cfg['terminal-height'] = terminalHeight
		
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			self.cfg['agent-type'] = agent['type']
			
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
			
		self.__checkConfig()
		
		# initialize the agent with no data
		if agentSupport:
			self.prepareAgent(data={'shared': shared})
			if self.agentIsReady(timeout=30) is None:
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
			self.TIMER_ALIVE_AGT.start()

		
	def __checkConfig(self):
		"""
		"""
		self.debug("config: %s" % self.cfg)
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
		
	def __setSource(self):
		"""
		Set the source ip and port
		"""
		if self.socket is not None:
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
	
	@doc_public
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
			
	def encapsule(self, ip_event, ssh_event):
		"""
		encapsule template
		"""
		# prepare layers
		# ip 
		src = self.sourceIp
		dst = self.cfg['dst-ip']
		srcP = self.sourcePort
		dstP = self.cfg['dst-port']
		if ip_event == AdapterIP.received():
			src = self.cfg['dst-ip']
			dst = self.sourceIp
			srcP = self.cfg['dst-port']
			dstP = self.sourcePort
		layer_ip = AdapterIP.ip( source=src, destination=dst, version=self.cfg['sock-family'], more=ip_event ) 
		
		# tcp
		if ip_event == AdapterIP.received():
			moreTcp = AdapterTCP.received()
		else:
			moreTcp = AdapterTCP.sent()
		layer_tcp = AdapterTCP.tcp(source=srcP, destination=dstP, more=moreTcp)
		
		# ssh 
		layer_ssh = templates.ssh()
		layer_ssh.addMore(more=ssh_event)
		
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
		tpl.addLayer(layer=layer_ssh)
		return tpl

	def cleanSocket(self):
		"""
		Clean socket
		"""
		self.debug( 'clean the socket' )
		
		self.unsetRunning()

		try:
			# clean the socket
			if self.socket is not None:
				self.socket.close()
				self.connected = False
		except Exception as e :
			pass
			
	def onReset(self):
		"""
		On reset
		"""
		if self.cfg['agent-support']:
			self.resetAgent()
		
		self.cleanSocket()
		
	def channel(self):
		"""
		Return the channel
		"""
		return self.sshChannel
		
	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( data )
		if 'cmd' in data and data['cmd'] == AGENT_INITIALIZED:
					tpl = TestTemplatesLib.TemplateMessage()
					layer = TestTemplatesLib.TemplateLayer('AGENT')
					layer.addKey("ready", True)
					layer.addKey(name='name', data=self.cfg['agent']['name'] )
					layer.addKey(name='type', data=self.cfg['agent']['type'] )
					tpl.addLayer(layer= layer)
					self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )	
		else:
			if 'sftp-event' in data:
				self.onSftpEvent(event=data)
			if 'ssh-event' in data:
				if data['ssh-event'] == 'initialized':
					self.sourceIp = data['src-ip']
					self.sourcePort = data['src-port']		
				elif data['ssh-event'] == 'connected':
					self.connected = True
					self.onConnection()
				elif data['ssh-event'] == 'connection-failed':
					self.onConnectionFailed(errno=data['err-no'], errstr=data['err-str'])		
				elif data['ssh-event'] == 'connection-timeout':
					self.onConnectionTimeout(e=data['more'])	
				elif data['ssh-event'] == 'connection-refused':
					self.onConnectionRefused()	
				elif data['ssh-event'] == 'disconnected-by-peer':
					self.onDisconnectionByPeer(e=data['more'])
				elif data['ssh-event'] == 'closed':
					self.onDisconnection()		
				elif data['ssh-event'] == 'negotiation-ok':
					self.sshTranport = TransportSsh()
					self.onNegotiationOk()		
				elif data['ssh-event'] == 'negotiation-failed':
					#self.debug(data['err'])
					self.onNegotiationFailed(err=data['err'])		
				elif data['ssh-event'] == 'authentication-ok':
					self.sshTranport.authenticated = True
					self.onAuthenticationOk()
				elif data['ssh-event'] == 'authentication-failed':
					#self.debug(data['err'])
					self.onAuthenticationFailed(err=data['err'])
				elif data['ssh-event'] == 'channel-opened':
					self.channelOpened = True
					self.onChannelOpened()
				elif data['ssh-event'] == 'sftp-opened':
					self.__onSftpOpened()
				elif data['ssh-event'] == 'channel-opening-failed':
					#self.debug(data['err'])
					self.onChannelOpeningFailed(err=data['err'])
				elif data['ssh-event'] == 'sftp-opening-failed':
					#self.debug(data['err'])
					self.__onSftpFailed(err=data['err'])
				else:
						self.error("agent mode - ssh event unknown on notify: %s" % data['ssh-event'] )

	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['ssh-event'] == 'on-run':
			self.error( "error: %s" % data['more'] )
		elif data['ssh-event'] == 'socket-error':
			self.onSocketError(e=data['more'])
		elif data['ssh-event'] == 'connect-error':
			self.error( "connect error: %s" % data['more'] )
			self.disconnect()
		elif data['ssh-event'] == 'send-data-error':
			self.error( "error on send data: %s" % data['more'] )
		else:
			self.error("agent mode - ssh event unknown on error: %s" % data['ssh-event'] )	
			
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if len(data) == 0:
			self.onIncomingData(noMoreData=True)
		else:
			self.onIncomingData(data=data)

	def sendNotifyToAgent(self, data):
		"""
		"""
		self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	def initAgent(self, data):
		"""
		Init agent
		"""
		self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	def prepareAgent(self, data):
		"""
		prepare agent
		"""
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
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
		Waits to receive agent ready event until the end of the timeout
		
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
		
	def onSftpEvent(self, event):
		"""
		Function to reimplement
		"""
		pass
		
	@doc_public
	def connect(self):
		"""
		Start the TCP connection
		"""
		if self.connected:
			self.debug( 'already connected' )
			return 
			
		# Optional: resolve hostname
		if self.cfg['dst-host'] != '':
			self.cfg['dst-ip'] = self.dns.resolveHost(host=self.cfg['dst-host'])
			if not len(self.cfg['dst-ip']):
				return 

		# Start the tcp connection
		self.debug( 'connection started' )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.connection() )
		if self.logEventSent: self.logSentEvent( shortEvt = "connection", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': 'connect',
							'bind-ip': self.cfg['bind-ip'], 'bind-port': self.cfg['bind-port'],
							'sock-timeout': self.cfg['sock-timeout'], 'tcp-keepalive': self.cfg['tcp-keepalive'],
							'tcp-keepalive-interval': self.cfg['tcp-keepalive-interval'] ,
							'sock-family': self.cfg['sock-family'],
							'dst-ip': self.cfg['dst-ip'], 'dst-port':self.cfg['dst-port'],
							'shared': self.isShared()
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
	
				# Connect the socket
				self.socket.connect( (self.cfg['dst-ip'], self.cfg['dst-port']) )
				
				# Connection successful
				self.__setSource()	
				self.connected = True
				self.onConnection()
	
				# start thread
				self.setRunning()
			except socket.timeout as e:
				self.onConnectionTimeout(e)
			except socket.error as e:
				(errno, errstr) = e
				if errno == 111:
					self.onConnectionRefused()
				else:
					self.onConnectionFailed(errno=errno, errstr=errstr)
			except Exception as e:
				self.error( "connect error: %s" % str(e) )
				self.disconnectTcp()
		return tpl
	@doc_public
	def disconnect(self):
		"""
		Close the TCP connection
		"""
		self.__mutex__.acquire()
		if self.connected:
			self.debug( 'disconnection started' )

			# log event
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.disconnection() )
			if self.logEventSent: self.logSentEvent( shortEvt = "disconnection", tplEvt = tpl )
		
			if self.cfg['agent-support']:
				self.unsetRunning()
				remote_cfg = {'cmd': 'disconnect'}
				self.sendNotifyToAgent(data=remote_cfg)
				self.debug( 'reset sent to agent' )
			else:
				self.cleanSocket()
				self.onDisconnection()
				
			return tpl
		self.__mutex__.release()
		

	def onConnection(self):
		"""
		On connection
		"""
		self.debug( "connected" )

		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.connected() )
			self.logRecvEvent( shortEvt = "connected", tplEvt = tpl )

		# start ssh negotation
		self.negotiation()
		
	def onDisconnection(self):
		"""
		On disconnection
		"""
		self.channelOpened = False
		self.connected = False
		self.debug( "disconnected" )

		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.disconnected() )
			self.logRecvEvent( shortEvt = "disconnected", tplEvt = tpl )

		self.unsetRunning()
		self.sshChannel = None
		
	def onDisconnectionByPeer(self, e):
		"""
		On disconnection by peer
		"""
		self.debug("disconnected by the server: %s" % str(e) )
		
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.disconnected_by_server() )
			self.logRecvEvent( shortEvt = "disconnected by peer", tplEvt = tpl )
			
		self.cleanSocket()

	def onConnectionRefused(self):
		"""
		On connection refused
		"""
		self.__setSource()	
		self.debug( "connection refused" )
		
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.connection_refused() )
			self.logRecvEvent( shortEvt = "connection refused", tplEvt = tpl )
		
		self.cleanSocket()

	def onConnectionTimeout(self, e):
		"""
		On connection timeout
		"""
		self.__setSource()
		self.debug( "connection timeout: %s" % str(e) )
		
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.connection_timeout() )
			self.logRecvEvent( shortEvt = "connection timeout", tplEvt = tpl )
		
		self.cleanSocket()

	def onConnectionFailed(self, errno, errstr):
		"""
		On connection failed
		"""
		self.debug( "connection failed" )
		
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.connection_failed(errno=str(errno), errstr=errstr) )
			self.logRecvEvent( shortEvt = "connection failed", tplEvt = tpl )
		
		self.cleanSocket()


	def onSocketError(self, e):
		"""
		On socket error
		"""
		self.error( "socket error: %s" % str(e) )
		
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.generic_error() )
			self.logRecvEvent( shortEvt = "error", tplEvt = tpl )
		
		self.cleanSocket()

	def notifyAgent(self, cfg):
		"""
		"""
		self.sendNotifyToAgent(data=cfg)
		
	@doc_public
	def negotiation(self):
		"""
		Start ssh negotiation
		"""
		if not self.connected:
			self.debug( 'tcp not connected' )
			return
			
		# log event
		if self.logEventSent:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.negotiation() )
			self.logSentEvent( shortEvt = "negotiation", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			remote_cfg = { 'cmd': 'negotiation'}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			t = threading.Thread(target=self.__negotiation)
			t.start()

	def __negotiation(self):
		"""
		Sub function to start the negotiation
		"""
		self.sshTranport = paramiko.Transport(self.socket)
		try:
			self.sshTranport.start_client()
		except Exception as e:	
			#self.error( e ) 
			self.onNegotiationFailed(err="%s" % e)
		
		# nego ok
		else:
			self.onNegotiationOk()
			
	def onNegotiationOk(self):
		"""
		On negotiation ok
		"""
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.negotiation_ok() )
			self.logRecvEvent( shortEvt = "negotiated", tplEvt = tpl )
		
		# auth with password
		self.authentication()
		
	def onNegotiationFailed(self, err=""):
		"""
		On negotiation failed
		"""
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.negotiation_failed(err=err) )
			self.logRecvEvent( shortEvt = "negotiation failed", tplEvt = tpl )
		
		# close transport
		if self.sshTranport is not None:
			self.sshTranport.close()
		self.sshTranport = None
		self.connected = False
		
		self.handleConnectionFailed(err=err)
	
	@doc_public
	def authentication(self):
		"""
		authentication ssh with login and password
		"""
		if self.sshTranport is None:
			self.debug( 'negotiation todo before' )
			return
			
		# log event
		if self.logEventSent:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.authentication() )
			self.logSentEvent( shortEvt = "authentication", tplEvt = tpl )

		if self.cfg['agent-support']:
			remote_cfg = { 'cmd': 'authentication', 'login': self.cfg['login'], 'password': self.cfg['password'] }
			if self.cfg['private-key'] is not None:
				remote_cfg['private-key'] = self.cfg['private-key']
			else:
				remote_cfg['private-key'] = ''
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				if self.cfg['private-key']  is not None or self.cfg['private-key-path'] is not None  :
					key = self.sshTranport.get_remote_server_key()
					
					if self.cfg['private-key-path'] is not None:
						f = open(self.cfg['private-key-path'], 'r')
						self.cfg['private-key'] = f.read()
						f.close()
						
					# read first line of the private key to detect the type
					key_head=self.cfg['private-key'].splitlines()[0]
					if 'DSA' in key_head:
						keytype=paramiko.DSSKey
					elif 'RSA' in key_head:
						keytype=paramiko.RSAKey
					else:
						raise Exception("Invalid key type: %s" % key_head)
					
					# construct the key
					keyfile = io.StringIO( unicode(self.cfg['private-key']) )
					pkey=keytype.from_private_key(keyfile)
					
					# try to make the authen
					self.sshTranport.auth_publickey(self.cfg['login'], pkey)
				else:
					self.sshTranport.auth_password(self.cfg['login'], self.cfg['password'])
			except Exception as e:
				#self.debug( e ) 
				self.onAuthenticationFailed(err="%s" % e )
			
			# authen ok 
			else:
				self.onAuthenticationOk()
					
	def onAuthenticationOk(self):
		"""
		On authentication ok
		"""
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.authentication_ok() )
			self.logRecvEvent( shortEvt = "authenticated", tplEvt = tpl )

		# open session
		self.openSession()
		
	def onAuthenticationFailed(self, err=""):
		"""
		On authentication failed
		"""
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.authentication_failed(err=err) )
			self.logRecvEvent( shortEvt = "authentication failed", tplEvt = tpl )
		
		# close transport
		if self.sshTranport is not None:
			self.sshTranport.close()
		self.sshTranport = None
		self.connected = False
		
		self.handleConnectionFailed(err=err)
	def handleConnectionFailed(self, err):
		"""
		"""
		pass
	@doc_public
	def openSession(self):
		"""
		Open a ssh session
		"""
		if self.sshTranport is None:
			return
			
		if not self.sshTranport.is_authenticated():
			self.debug( 'not authenticated' )
			return
			
		# log event
		if self.sftpSupport:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.open_channel() )
			self.logSentEvent( shortEvt = "open sftp channel", tplEvt = tpl )
		else:
			if self.logEventSent:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.open_channel() )
				self.logSentEvent( shortEvt = "open channel", tplEvt = tpl )

		if self.cfg['agent-support']:
			remote_cfg = { 'cmd': 'open-session', 'sftp-support':  self.sftpSupport,  'terminal-type': self.cfg['terminal-type'],
														'terminal-width': self.cfg['terminal-width'] , 'terminal-height': self.cfg['terminal-height']}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				if self.sftpSupport:
					self.sshChannel = self.sshTranport.open_sftp_client()
				else:
					self.sshChannel = self.sshTranport.open_session()
					self.sshChannel.get_pty(term=self.cfg['terminal-type'],
																						width=self.cfg['terminal-width'] , height =self.cfg['terminal-height'] )
					self.sshChannel.invoke_shell()
					self.sshChannel.settimeout(0.0)
			except Exception as e:
				#self.debug( e )
				if self.sftpSupport:
					self.__onSftpFailed(err="%s" % e )
				else:
					self.onChannelOpeningFailed(err="%s" % e)
	
			# channel opened 
			else:
				if self.sftpSupport:
					self.__onSftpOpened()
				else:
					self.onChannelOpened()
	
	def __onSftpOpened(self):
		"""
		to reimplement
		"""
		self.sftpOpened = True
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.open_channel_ok() )
		self.logRecvEvent( shortEvt = "sftp channel opened", tplEvt = tpl )
		
		self.onSftpOpened()
		
	def onSftpOpened(self):
		"""
		to reimplement
		"""
		pass
		
	def onSftpFailed(self):
		"""
		to reimplement
		"""
		pass
		
	def __onSftpFailed(self, err=""):
		"""
		to reimplement
		"""
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.authentication_failed(err=err) )
		self.logRecvEvent( shortEvt = "open sftp channel failed", tplEvt = tpl )
		
		# close transport
		if self.sshTranport is not None:
			self.sshTranport.close()
		self.sshTranport = None
		self.sshChannel = None
		
		self.onSftpFailed()
		
		
	def onChannelOpened(self):
		"""
		On channel opened
		"""
		self.channelOpened = True
		
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.open_channel_ok() )
			self.logRecvEvent( shortEvt = "channel opened", tplEvt = tpl )
			
		# begin to run
		self.setRunning()
		
	def onChannelOpeningFailed(self, err=""):
		"""
		On channel opening failed
		"""
		# log event
		if self.logEventReceived:
			tpl = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.authentication_failed(err=err) )
			self.logRecvEvent( shortEvt = "open channel failed", tplEvt = tpl )
			
		# close transport
		if self.sshTranport is not None:
			self.sshTranport.close()
		self.sshTranport = None
		self.sshChannel = None
		
	def onRun(self):
		"""
		"""
		try:
			if self.connected:
				if self.channelOpened:
					if self.cfg['agent-support']:
						pass
					else:
						r, w, e = select.select([self.sshChannel], [], [self.sshChannel])
						if self.sshChannel in r:
							data = self.sshChannel.recv(2048)
							# no data
							if len(data) == 0:
								self.onIncomingData(noMoreData=True)
								raise EOFError("nothing to read: disconnecting")
							
							# incoming data
							self.onIncomingData(data=data)
		except EOFError as e:
				self.onDisconnectionByPeer(e)
		except socket.error as e:
			self.onSocketError(e)
		except Exception as e:
			self.error( "on run %s" % str(e) )

	def onIncomingData(self, data=None, noMoreData=False):
		"""
		On incoming data
		"""
		try:
			if noMoreData:
				lower = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.data_received() )
				self.handleNoMoreData(lower=lower)
			else:
				lower = self.encapsule( ip_event=AdapterIP.received(), ssh_event=templates.data_received(data=data) )
				
				# log event 	
				if self.logEventReceived:	
					lower.addRaw(raw=data)		
					self.logRecvEvent( shortEvt = 'data', tplEvt = lower )	
					
				# handle data
				self.handleIncomingData( data, lower=lower )
		except Exception as e:
			self.error( "on incoming ssh data: %s" % e )
			
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

	def getExpectedTemplate(self, event, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Return an expected template with ip and tcp layers
		"""
		# prepare layers
		defaultVer = self.cfg['sock-family']
		if versionIp is not None:
			defaultVer = versionIp
		layer_ip = AdapterIP.ip( source=sourceIp, destination=destinationIp, version=defaultVer ) 		
		
		# tcp
		layer_tcp = AdapterTCP.tcp(source=sourcePort, destination=destinationPort)

		# ssh
		layer_ssh = templates.ssh(more=event)

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
		tpl.addLayer(layer=layer_ssh)
		return tpl
		
	@doc_public
	def isConnected(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		tpl = templates.connected()
		expected = self.getExpectedTemplate(event=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isDisconnected(self, timeout=1.0, byServer=False, versionIp=None, sourceIp=None, destinationIp=None, 
										sourcePort=None, destinationPort=None):
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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		if byServer:
			tpl = templates.disconnected_by_server()
		else:
			tpl = templates.disconnected()
		expected = self.getExpectedTemplate(event=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp,
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def isNegotiated(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Waits to receive "negotiated" event until the end of the timeout

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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		tpl = templates.negotiation_ok()
		expected = self.getExpectedTemplate(event=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
	
	@doc_public
	def isAuthenticated(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Waits to receive "authenticated" event until the end of the timeout

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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		tpl = templates.authentication_ok()
		expected = self.getExpectedTemplate(event=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isChannelOpened(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Waits to receive "channel opened" event until the end of the timeout

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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		tpl = templates.open_channel_ok()
		expected = self.getExpectedTemplate(event=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def doConnect(self, timeout=1.0, prompt='~]#'):
		"""
		Do connect with authentification

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@param prompt: ssh prompt (default=~]#)
		@type prompt: string
		
		@return: True is successfully connected, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = True
		self.connect()
		if self.isConnected(timeout=timeout) is None:
			ret = False
		else:
			if self.isChannelOpened(timeout=timeout) is None:
				self.disconnect()
				ret = False			
			else:
				if self.searchPrompt(timeout=timeout, prompt=prompt) is None:
					self.disconnect()
					ret = False
		return ret

	@doc_public
	def doDisconnect(self, timeout=1.0):
		"""
		Do disconnect

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: True is successfully disconnected, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = True
		self.disconnect()
		if self.isDisconnected(timeout=timeout) is None:
			ret = False
		return ret
		
	@doc_public
	def sendData(self, tpl=None, dataRaw=None):
		"""
		Send ssh data

		@param tpl: ssh template data (default=None)
		@type tpl: templatelayer/none
		
		@param dataRaw: ssh data (default=None)
		@type dataRaw: string/none
	
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		if self.sshTranport is None:
			return
			
		if not self.sshTranport.is_authenticated():
			self.debug( 'not authenticated' )
			return
			
		if not self.connected:
			self.debug( "not connected" )
			return

				
		# log event
		if self.logEventSent:
			if dataRaw is not None:
				ssh_tpl = templates.data_sent(data=dataRaw)
			else:
				ssh_tpl = tpl
			tpl_final = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=ssh_tpl )
		else:
			tpl_final = self.encapsule( ip_event=AdapterIP.sent(), ssh_event=templates.data_sent() )
		
		data = dataRaw
		if dataRaw is None:
			data = tpl.get('data')
		
		self.debug( data )	
		if data is None:
			return
			
		if self.logEventSent:
			tpl_final.addRaw(raw=data)
			self.logSentEvent( shortEvt = "data", tplEvt = tpl_final )
		
		if self.cfg['agent-support']:
			remote_cfg = { 'cmd': 'send-data', 'data': data }
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.sshChannel.send(data)
			except Exception as e:
				self.error("unable to send data through ssh: %s" % str(e) )
		return tpl_final
		
	@doc_public
	def hasReceivedData(self, timeout=1.0, dataExpected=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param dataExpected: data expected (default=None)
		@type dataExpected:	string/operators/None			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage/none
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		tpl = templates.data_received(data=dataExpected)
		expected = self.getExpectedTemplate(event=tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
	
	@doc_public
	def searchPrompt(self, timeout=1.0, prompt='~]#'):
		"""
		Search prompt

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@param prompt: ssh prompt (default=~]#)
		@type prompt: string
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage/none		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		data = self.hasReceivedData(
											dataExpected=TestOperatorsLib.Contains(needle=[ prompt ] , AND=True, OR=False),
											timeout=timeout)
		return data
		
	@doc_public
	def doSendCommand(self, command,  timeout=1.0, expectedData=None, prompt='~]#'):
		"""
		Send command and waiting data
		Automatic connect and disconnection if not done before
	
		@param command: ssh command
		@type command: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
	
		@param expectedData: data expected (default=None)
		@type expectedData:	string/operators/None			

		@param prompt: ssh prompt (default=~]#)
		@type prompt: string
		
		@return: command response as string or None otherwise
		@rtype: string/none		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = None
		
		internalConnect = False
		if not self.channelOpened:
			internalConnect = True
			# connect phase
			self.connect()
			if self.isChannelOpened(timeout=timeout) is None:
				self.disconnect()
				return None
			
			if self.searchPrompt(timeout=timeout, prompt=prompt) is None:
				self.disconnect()
				return None
			
		# send command
		cmd = "%s\n" % command
		self.sendData( dataRaw=cmd )

		if expectedData is None:
			dataRsp = TestOperatorsLib.Contains(needle=[ prompt ] , AND=True, OR=False)
		else:
			dataRsp = expectedData
		data = self.hasReceivedData(
											dataExpected=dataRsp,
											timeout=timeout)
		if data is not None:
			ret = data.get('SSH', 'data') 

		if internalConnect:
			# disconnect phase
			self.disconnect()
			if self.isDisconnected(timeout=timeout) is None:
				return None
		return ret