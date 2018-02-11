#!/usr/bin/env python
# -*- coding=utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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
AdapterDNS = sys.modules['SutAdapters.%s.DNS' % TestAdapterLib.getVersion()]

import threading
import socket
import select
import time

import templates

__NAME__="""UDP"""

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, bindIp = '', bindPort=0, name=None,
								destinationIp='', destinationPort=0, destinationHost='',
								socketFamily=AdapterIP.IPv4, inactivityTimeout=0.0,
								separatorIn='\\x00', separatorOut='\\x00', separatorDisabled=False,
								debug=False, logEventSent=True, logEventReceived=True,
								parentName=None, agentSupport=False, agent=None, shared=False
						):
		"""
		This class enable to use the protocol UDP as client only.
		Lower network layer (IP, Ethernet) are not controlable.
		Support data separator for upper application and inactivity detection.
		
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

		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: intconstant
		
		@param separatorIn: data separator (default=\\x00)
		@type separatorIn: string

		@param separatorOut: data separator (default=\\x00)
		@type separatorOut: string

		@param separatorDisabled: disable the separator feature, if this feature is enabled then data are buffered until the detection of the separator (default=False)
		@type separatorDisabled: boolean
		
		@param inactivityTimeout: feature disabled by default (value=0.0)
		@type inactivityTimeout: float
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean
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
			
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, 
																realname=name, agentSupport=agentSupport, agent=agent)
		if parentName is not None:
			TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__) )
		self.__mutex__ = threading.RLock()
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived		
		self.isreading = True
		self.parent = parent
		self.socket = None
		self.sourceIp = bindIp
		self.sourcePort = bindPort
		self.islistening = False
		self.buf = {}
		
		self.dns = AdapterDNS.Client(parent=parent, debug=debug, logEventSent=True, logEventReceived=True, name=name, shared=shared)
																
		self.cfg = {}
		# transport options
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		self.cfg['dst-ip'] = destinationIp
		self.cfg['dst-port'] = destinationPort
		self.cfg['dst-host'] = destinationHost
		# socket options
		self.cfg['sock-family'] =  int(socketFamily)
		# data separators 
		self.cfg['sep-in'] = separatorIn
		self.cfg['sep-out'] = separatorOut
		self.cfg['sep-disabled'] = separatorDisabled
		self.cfg['inactivity-timeout'] = inactivityTimeout
		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		if agentSupport:
			self.prepareAgent(data={'shared': shared})
			if self.agentIsReady(timeout=10) is None:
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
#				raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
			self.TIMER_ALIVE_AGT.start()
			
	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
			
	def __setSource(self):
		"""
		"""
		srcIp, srcPort = self.socket.getsockname() # ('127.0.0.1', 52318)
		self.sourceIp = srcIp
		self.sourcePort = srcPort		
		
	@doc_public
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
	def setDestination(self, destinationIp, destinationPort, destinationHost=''):
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
		self.cfg['dst-port'] = int(destinationPort)
		self.cfg['dst-host'] = destinationHost
		
		# resolv the hostname
		if self.cfg['dst-host'] != '':
			self.cfg['dst-ip'] = self.dns.resolveHost(host=self.cfg['dst-host'])
		
	def encapsule(self, ip_event, udp_event, src_ip=None, src_port=None):
		"""
		"""
		# prepare layers
		src = self.sourceIp
		dst = self.cfg['dst-ip']
		srcP = self.sourcePort
		dstP = self.cfg['dst-port']
		if src_ip is not None:
			src = src_ip
			dst = self.sourceIp
		if src_port is not None:
			srcP = src_port
			dstP = self.sourcePort
		layer_ip = AdapterIP.ip( source=src, destination=dst, version= "%s" % self.cfg['sock-family'], more=ip_event ) 
		layer_udp = templates.udp(source=srcP, destination=dstP)
		layer_udp.addMore(more=udp_event)
		
		# prepare template
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_udp)
		return tpl
		
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		self.__mutex__.acquire()
		if self.islistening:
			self.debug( 'stopping to listen' )
			# log event
			self.islistening = False
			tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.stopping() )
			self.logSentEvent( shortEvt = "stopping", tplEvt = tpl )		
			
			if self.cfg['agent-support']:
				self.cleanSocket()

				# cleanup remote agent
				#self.resetAgent()
				remote_cfg  = {'cmd': 'disconnect'}
				self.sendNotifyToAgent(data=remote_cfg)
				
			else:
				#	clean socket	
				self.cleanSocket()
				
				# dispatch
				self.onStopListening()
		self.__mutex__.release()
		
	def cleanSocket(self):
		"""
		"""
		self.debug( 'clean the socket' )
		self.unsetRunning()
		# clean the socket
		if self.socket is not None:
			self.socket.close()
			self.islistening = False

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
			if 'udp-event' in data:
				if data['udp-event'] == 'initialized':
					self.sourceIp = data['src-ip']
					self.sourcePort = data['src-port']		
				elif data['udp-event'] == 'listening':
					self.onStartListening()
				elif data['udp-event'] == 'stopped':
					self.onStopListening()				
				elif data['udp-event'] == 	'listening-failed':
					self.onStartListeningFailed(e=data['more'])		
				else:
					self.error("agent mode - udp event unknown on notify: %s" % data['udp-event'] )
			
	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['udp-event'] == 'on-run':
			self.error( "error: %s" % data['more'] )
		elif data['udp-event'] == 'socket-error':
			self.onSocketError(e=data['more'])
		elif data['udp-event'] == 'connect-error':
			self.error( "connect error: %s" % data['more'] )
			self.stopListening()
		else:
			self.error("agent mode - udp event unknown on error: %s" % data['tcp-event'] )
			
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		try:
			pdu = data['pdu']
			addr = data['from-addr']
			self.lastActivity = time.time()
			if self.cfg['sep-disabled']:
				self.onIncomingData(data=pdu, fromAddr=addr)
			else:
				if self.buf.has_key(addr):
					self.buf[addr] = ''.join([self.buf[addr], pdu])
				else:
					self.buf[addr] = pdu
				self.onIncomingData(fromAddr=addr)		
		except Exception as e:
			self.error( e )
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
	@doc_public
	def startListening(self):
		"""
		Start listening
		"""
		if self.islistening:
			self.debug( 'already listening' )
			return 
			
		# Optional: resolve destination hostname
		if self.cfg['dst-host'] != '':
			self.cfg['dst-ip'] = self.dns.resolveHost(host=self.cfg['dst-host'])
			if not len(self.cfg['dst-ip']):
				return 
				
		# Start the tcp connection
		self.debug( 'starting to listen' )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.starting() )
		self.logSentEvent( shortEvt = "starting", tplEvt = tpl )		
		if self.cfg['agent-support']:
			remote_cfg = {
				'cmd':  'connect',
				'sock-type': 'udp', 
				'bind-ip': self.cfg['bind-ip'], 'bind-port': self.cfg['bind-port'],
				'sock-family': self.cfg['sock-family'],
				'dst-ip': self.cfg['dst-ip'], 'dst-port':self.cfg['dst-port'],
			}
			#self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=remote_cfg)
			self.sendNotifyToAgent(data=remote_cfg)
			
			# start thread
			self.lastActivity = time.time()
			self.setRunning()
		else:
			self.__mutex__.acquire()
			try:
				# set the socket version
				if self.cfg['sock-family'] == AdapterIP.IPv4:
					sockType = TestAdapterLib.INIT_DGRAM_SOCKET
				elif  self.cfg['sock-family'] == AdapterIP.IPv6:
					sockType = TestAdapterLib.INIT6_DGRAM_SOCKET
				else:
					raise Exception('socket family unknown: %s' % str(self.cfg['socket-family']) )	
				
				# Create the socket
				self.socket = TestAdapterLib.getSocket(sockType=sockType)
				self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.debug( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
				self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
				
				# listening successful
				self.__setSource()	
				
				# dispatch 
				self.lastActivity = time.time()
				self.islistening = True
				self.onStartListening()
				
				# start thread
				self.setRunning()
			except socket.error, e:
				self.onStartListeningFailed(e)
			except Exception as e:
				self.error( "start listen error: %s" % str(e) )
				self.stopListening()
			self.__mutex__.release()

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
		
	def onRun(self):
		"""
		"""
		self.__mutex__.acquire()
		try:
			if self.cfg['agent-support']:
					if self.islistening:
						if self.isreading:
							if self.cfg['inactivity-timeout']:
								if time.time() - self.lastActivity > self.cfg['inactivity-timeout']:
									self.onInactivityTimeout()
			else:
				if self.socket is not None:  
					if self.islistening:
						if self.isreading:
							r, w, e = select.select([ self.socket ], [], [], 0.01)
							for s in r:
								if s is not None:
									(data, addr) = s.recvfrom(65535)
									self.lastActivity = time.time()
									if self.cfg['sep-disabled']:
										self.onIncomingData(data=data, fromAddr=addr)
									else:
										if self.buf.has_key(addr):
											self.buf[addr] = ''.join([self.buf[addr], data])
										else:
											self.buf[addr] = data
										self.onIncomingData(fromAddr=addr)		
							if self.cfg['inactivity-timeout']:
								if time.time() - self.lastActivity > self.cfg['inactivity-timeout']:
									self.onInactivityTimeout()
		except socket.error, e:
			self.onSocketError(e)					
		except Exception as e:
			self.error( "on run %s" % str(e) )
		self.__mutex__.release()
				
	def addSeparator(self, data):
		"""
		Add the separator to the end of the data, if the feature is enabled	
		"""
		if self.cfg['sep-disabled']:
			return data
		else:
			return  data + self.cfg['sep-out']
			
	@doc_public
	def sendData(self, data, to=None):
		"""
		Send data over the udp protocol

		@param data: data to send over udp
		@type data: string		

		@param to: address of destination (ip,port)
		@type to: tuple/none

		@return: udp layer encapsulate in ip, return False on error
		@rtype: templatemessage
		"""
		try:
			#self.debug( "data to sent (bytes %s) to %s"  % (len(data), to) )
			if not self.islistening:
				self.debug( "not listening" )
				return False
				
			# prepare destination address
			addr = (self.cfg['dst-ip'], self.cfg['dst-port'])
			
			if to is not None:
				addr = to
				self.cfg['dst-ip'] = addr[0]
				self.cfg['dst-port'] = addr[1]
			
			# add the separator to the end of the data, if the feature is enabled	
			pdu = self.addSeparator(	data=data )

			# log event
			pdu_size = len(pdu)
			if self.logEventSent:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.sent(data=pdu, data_length=str(pdu_size)) )
			else:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.sent( data_length=str(pdu_size) ) )
			if self.logEventSent:
				tpl.addRaw(raw=pdu)
				self.logSentEvent( shortEvt = "data", tplEvt = tpl )
			
			if self.cfg['agent-support']:
				data = { 'cmd':  'send-data', 'pdu': pdu, 'addr': addr}
				self.sendNotifyToAgent(data=data)
			else:
				# send the packet
				self.socket.sendto(pdu, addr)
			self.debug( "data sent (bytes %s)"  % len(pdu) )
			return tpl
		except Exception as e:
			self.error('Unable to send data: %s' % str(e))
			return False
		
	@doc_public
	def onInactivityTimeout(self):
		"""
		"""
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received(), 
						src_ip=self.cfg['dst-ip'], src_port=self.cfg['dst-port'] )
		self.onInactivity(lower=tpl)
		
	def onInactivity(self, lower):
		"""
		Function to reimplement
		"""
		pass
		
	def onIncomingData(self, data=None, fromAddr=None):
		"""
		"""
		try:
			ip, port = fromAddr
			# separator feature is disabled
			if data is not None: 
				# log event
				data_size = len(data)
				if self.logEventReceived:
					tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received(data=data, data_length=str(data_size)), src_ip=ip, src_port=port )
				else:
					tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received(data_length=str(data_size)), src_ip=ip, src_port=port )
				if self.logEventReceived:
					tpl.addRaw(raw=data)
					self.logRecvEvent( shortEvt = "data", tplEvt = tpl )
				
				# handle data
				self.handleIncomingData( data, lower=tpl )
			# separator feature is enabled, split the buffer by the separator
			else: 
				datas = self.buf[fromAddr].split(self.cfg['sep-in'])
				for data in datas[:-1]:
					pdu = data+self.cfg['sep-in']
					# log event
					pdu_size = len(data)
					if self.logEventReceived:
						tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received( data=pdu, data_length=str(pdu_size) ), src_ip=ip, src_port=port )
					else:
						tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received( data_length=str(pdu_size) ), src_ip=ip, src_port=port )
					if self.logEventReceived:
						tpl.addRaw(raw=pdu)
						self.logRecvEvent( shortEvt = "data reassembled", tplEvt = tpl )
					# handle data
					self.handleIncomingData( pdu, lower=tpl)
				self.buf[fromAddr] = datas[-1]
		except Exception as e:
			self.error( str(e) )

	def handleIncomingData(self, data, lower=None):
		"""
		Function to reimplement
		Called on incoming packet

		@param data: udp data received
		@type data: string
		
		@param lower: template udp data received
		@type lower: templatemessage
		"""
		pass
		
	def onStartListening(self):
		"""
		"""
		self.debug( 'on start listening called' )
		
		if self.cfg['agent-support']:
			self.islistening = True
			
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.listening() )
		self.logRecvEvent( shortEvt = "listening", tplEvt = tpl )
		
	def onStopListening(self):
		"""
		"""
		self.debug( 'on stop listening called' )	
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.stopped() )
		self.logRecvEvent( shortEvt = "stopped", tplEvt = tpl )
		
	def onSocketError(self, e):
		"""
		"""
		self.error( "generic error: %s" % str(e) )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.generic_error() )
		self.logRecvEvent( shortEvt = "error", tplEvt = tpl )
		
		# clean the socket
		self.cleanSocket()

	def onReset(self):
		"""
		Reset
		"""
		if self.cfg['agent-support']:
			# stop timer
			self.TIMER_ALIVE_AGT.stop()
			self.resetAgent()
			
		self.stopListening()
		
	def onStartListeningFailed(self, e):
		"""
		"""
		self.debug( e )
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.listening_failed() )
		self.logRecvEvent( shortEvt = "listening failed", tplEvt = tpl )

	def getExpectedTemplate(self, tpl, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Return an expected template with ip and udp layers
		"""
		# prepare layers
		defaultVer = "%s" % self.cfg['sock-family']
		if versionIp is not None:
			defaultVer = versionIp
		layer_ip = AdapterIP.ip( source=sourceIp, destination=destinationIp, version=defaultVer ) 		
		layer_udp = templates.udp(source=sourcePort, destination=destinationPort)
		layer_udp.addMore(more=tpl)
		
		# prepare template
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_udp)
		return tpl
		
	@doc_public
	def isListening(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "listening" event until the end of the timeout
		
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
		tpl = templates.listening()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isListeningFailed(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "listening failed" event until the end of the timeout
		
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
		tpl = templates.listening_failed()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isStopped(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "stopped" event until the end of the timeout
		
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
		tpl = templates.stopped()
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def hasReceivedData(self, timeout=1.0, data=None, versionIp=None, sourceIp=None, destinationIp=None, 
													sourcePort=None, destinationPort=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param data: data expected
		@type data:	string/operators	
	
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
		tpl = templates.received(data=data)
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 			
		evt = self.received( expected = expected, timeout = timeout )
		return evt