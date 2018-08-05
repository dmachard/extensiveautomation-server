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

try:
	import templates
	import codec
except ImportError: # python3 support
	from . import templates
	from . import codec

import threading
import socket
import select

__NAME__="""ETHERNET-II"""

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='socket'

class Sniffer(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, debug=False, macResolution=True, padding=True, 
										logEventSent=True, logEventReceived=True, name=None,
										protocol2sniff=codec.ALL, parentName=None, agentSupport=False,
										agent=None, shared=False):
		"""
		This class enables to send/receive Ethernet II frame.

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param macResolution: mac address resolution (default=True)
		@type macResolution:	boolean
		
		@param protocol2sniff: SutAdapters.Ethernet.ALL (default)  | SutAdapters.Ethernet.IPv4 | SutAdapters.Ethernet.IPv6 | SutAdapters.Ethernet.ARP | SutAdapters.Ethernet.RARP | SutAdapters.Ethernet.DOT1Q | SutAdapters.Ethernet.SNMP
		@type protocol2sniff:	strconstant
		
		@param padding: the data padding is necessary to avoid collisions. (default=True)
		@type padding:	boolean
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent,
																										debug=debug, shared=shared,
																										realname=name, agentSupport=agentSupport, agent=agent,
																										caller=TestAdapterLib.caller(),
																										agentType=AGENT_TYPE_EXPECTED)
		if parentName is not None:
			TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__)  )
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.__mutex__ = threading.RLock()
		self.__mutex2__ = threading.RLock()
		
		self.parent = parent
		self.protocol2sniff = protocol2sniff
		self.sniffing = False
		self.socket = None
		self.src_mac = None
		self.mac_resolution = macResolution
		self.padding = padding
		self.etherCodec = codec.Codec(parent=self, macResolution=macResolution)

		self.cfg = {}
		self.cfg['src-eth'] = None
		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']		
			
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
		private function
		"""
		self.debug("config: %s" % self.cfg)
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
			
	def setname(self, name):
		"""
		"""
		TestAdapterLib.Adapter.setName(self, name="%s>%s" % (name, __NAME__) )
		
	def encapsule(self, layer_ether):
		"""
		"""
		# prepare template
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_ether)
		return tpl
		
	@doc_public
	def getSourceMac(self):
		"""
		Returns the source MAC address
		
		@return: MAC address
		@rtype: string
		"""
		if self.src_mac == None:
			return ''
		return self.src_mac

	def onReset(self):
		"""
		Reset
		"""
		if self.cfg['agent-support']:
			# stop timer
			self.TIMER_ALIVE_AGT.stop()
#			self.resetAgent()
			remote_cfg = { 'cmd':  'disconnect'}
			self.sendNotifyToAgent(data=remote_cfg)
			
		self.stopListening()
		
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		self.debug( 'acquire the mutex' )
		self.__mutex__.acquire()
		if self.sniffing:
			self.debug( 'stopping to sniff' )

			# log event
			ether_tpl = templates.ethernet( more=templates.stopping(interface=self.cfg['src-eth']) )
			frame_tpl = self.encapsule(layer_ether=ether_tpl)
			self.logSentEvent( shortEvt = "stopping", tplEvt = frame_tpl )		
			
			if self.cfg['agent-support']:
				self.cleanSocket()
				
			else:
				self.cleanSocket()
				self.onStopListening()
		self.__mutex__.release()
		self.debug( 'release the mutex' )
		
	def cleanSocket(self):
		"""
		"""
		self.debug( 'clean the socket' )
		self.sniffing = False
		self.unsetRunning()
		if self.socket is not None:
				self.socket.close()
				
	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['socket-raw-event'] == 'on-run':
			self.error( "error: %s" % data['more'] )
		elif data['socket-raw-event'] == 'socket-error':
			self.onSocketError(e=data['more'])
		elif data['socket-raw-event'] == 'connect-error':
			self.error( "connect error: %s" % data['more'] )
			self.stopListening()			
		else:
			self.error("agent mode - socket event unknown on error: %s" % data['tcp-event'] )
			
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.onHandleData(read=data)
		
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
			if 'socket-raw-event' in data:
				if data['socket-raw-event'] == 'initialized':
					if self.src_mac is None:
						self.src_mac = data['src-mac']
				elif data['socket-raw-event'] == 'sniffing':
					self.onStartSniffing()
				elif data['socket-raw-event'] == 'stopped':
					self.onStopListening()				
				elif data['socket-raw-event'] == 	'sniffing-failed':
					self.onStartSniffingFailed(e=data['more'])
				else:
					self.error("agent mode - socket raw event unknown on notify: %s" % data['socket-raw-event'] )		
					
	def sendNotifyToAgent(self, data):
		"""
		"""
		self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
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
	def prepareAgent(self, data):
		"""
		prepare agent
		"""
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
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
	def onStopListening(self):
		"""
		"""
		self.debug( 'on stop sniffing called' )	
		
		# log event
		ether_tpl = templates.ethernet( more=templates.stopped(interface=self.cfg['src-eth']) )
		frame_tpl = self.encapsule(layer_ether=ether_tpl)
		self.logRecvEvent( shortEvt = "stopped", tplEvt = frame_tpl )
		
	@doc_public
	def startListening(self, eth, srcMac=None):
		"""
		Start listening 
		
		@param eth: device
		@type eth: string
		
		@param srcMac: source mac address
		@type srcMac: none/string
		"""
		if self.sniffing:
			self.debug( 'already sniffing' )
			return 
		
		self.cfg['src-eth'] = eth
		# log event
		ether_tpl = templates.ethernet( more=templates.starting(interface=self.cfg['src-eth']) )
		frame_tpl = self.encapsule(layer_ether=ether_tpl)
		self.logSentEvent( shortEvt = "starting", tplEvt = frame_tpl )
		
		if self.cfg['agent-support']:
			if srcMac is not None:
				if not isinstance(srcMac, str) and not isinstance(srcMac, unicode):
					raise Exception('Adapter>startListening: bad source mac type: %s' % type(srcMac) )

				if not len(srcMac):
					raise Exception('Adapter>startListening: source mac address can not be empty')
					
				self.src_mac = srcMac
			
			remote_cfg = { 'cmd': 'connect', 'sock-type': 'raw', 'src-eth': self.cfg['src-eth'] }
			#self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=remote_cfg)
			self.sendNotifyToAgent(data=remote_cfg)
			
			self.setRunning()
		else:
			try:
				# Create the socket: ethernet protocol, raw Linux packet socket
				self.socket = TestAdapterLib.getSocket(sockType=TestAdapterLib.RAW_PACKET_SOCKET)
				self.socket.bind( ( eth, socket.SOCK_RAW ) )
				
				# save source mac addr
				if srcMac is not None:
					if not isinstance(srcMac, str) and not isinstance(srcMac, unicode):
						raise Exception('Adapter>startListening: bad source mac type: %s' % type(srcMac) )
					if not len(srcMac):
						raise Exception('Adapter>startListening: source mac address can not be empty')
					
					self.src_mac = srcMac
				else:
					self.src_mac = ':'.join( ["%02X" % (ord(ch),) for ch in self.socket.getsockname()[-1]] )
				self.debug( "source mac: %s" % self.src_mac )
				
				self.sniffing = True
				
				# start thread
				self.onStartSniffing()
				self.setRunning()
			except socket.error as e:
				self.onStartSniffingFailed(e)
			except Exception as e:
				self.error( "listen error: %s" % str(e) )	
				self.stopListening()
	
	def onStartSniffingFailed(self, e):
		"""
		"""
		self.debug( e )
		# log event
		ether_tpl = templates.ethernet( more=templates.sniffing_failed(err=str(e), interface=self.cfg['src-eth']) )
		frame_tpl = self.encapsule(layer_ether=ether_tpl)
		self.logRecvEvent( shortEvt = "sniffing failed", tplEvt = frame_tpl )
		
	def onStartSniffing(self):
		"""
		"""
		self.debug( 'on start listening called' )

		if self.cfg['agent-support']:
			self.sniffing = True
		
		# log event
		ether_tpl = templates.ethernet( more=templates.sniffing( macSrc=self.getSourceMac(), interface=self.cfg['src-eth'] ) )
		frame_tpl = self.encapsule(layer_ether=ether_tpl)
		self.logRecvEvent( shortEvt = "sniffing", tplEvt = frame_tpl )
		 
	@doc_public
	def sendFrame(self, data, dstMac, protocolType):
		"""
		Send a frame, with automatic data padding support
		
		@param data: upper data
		@type data: hexa
		
		@param dstMac: destination mac address
		@type dstMac: string
		
		@param protocolType: SutAdapters.Ethernet.IPv4 | SutAdapters.Ethernet.IPv6 | SutAdapters.Ethernet.ARP | SutAdapters.Ethernet.RARP | SutAdapters.Ethernet.DOT1Q | SutAdapters.Ethernet.SNMP
		@type protocolType: strconstant
		
		@return: template message
		@rtype: template
		"""
		if not self.sniffing:
			self.debug( "not sniffing" )
			return

		if not isinstance(dstMac, str):
			raise Exception('Adapter>sendFrame: bad destination mac type: %s' % type(dstMac) )

		if not len(dstMac):
			raise Exception('Adapter>sendFrame: destination mac address can not be empty')
			
		# The padding is necessary to avoid collisions. Ethernet packets must at least
		# have a size of 60 bytes without the Frame Check Sequence (FCS, 4 bytes).
		padding = None
		if self.padding:
			minSize = 60 - (2*6 + 2)
			if len(data) < minSize:
				padding = "\x00" * ( minSize - len(data) )
				data += padding	

		ether_tpl = templates.ethernet(destAddr=dstMac, srcAddr=self.src_mac, etherType=protocolType, data=data,
																	 padding=padding )
		frame_tpl = self.encapsule(layer_ether=ether_tpl)
		
		try:
			frame, ether_hdr = self.etherCodec.encode(frame_tpl=frame_tpl)
			# add the raw data without upper data
			ether_tpl.addRaw(ether_hdr)
		except Exception as e:
			raise Exception("Cannot encode the frame: %s" % str(e))
		else:
			frame_tpl.addRaw(frame)

			dst_mac_tpl = ether_tpl.get('mac-destination')
			dst_mac = dst_mac_tpl.getName()
			dst_summary = 'To %s' % dst_mac
			vendor_dst = dst_mac_tpl.get('vendor')
			if vendor_dst is not None:
				dst_summary = 'To %s:%s' % ( vendor_dst.replace(' ', ''), ':'.join( dst_mac.split(':')[3:] ) )
				
			if self.logEventSent:
				self.logSentEvent( shortEvt =  dst_summary, tplEvt = frame_tpl )
			else:
				self.onSending(lower=frame_tpl)
				
			# enqueue pdu
			self.debug( 'sending frame' )
			if self.cfg['agent-support']:
				remote_cfg = { 'cmd': 'send-data', 'payload': frame }
				self.sendNotifyToAgent(data=remote_cfg)
			else:
				if self.socket is not None: 
					self.socket.send( frame )
		return frame_tpl
	
	def onSending(self, lower):
		"""
		Function to reimplement
		
		@param lower: template message
		@type lower: template
		"""
		pass
	
	def onHandleData(self, read):
		"""
		"""
		self.__mutex2__.acquire()
		try:
			try:
				data_upper, ether_tpl = self.etherCodec.decode(frame=read)
			except Exception as e:
				self.error( "Cannot decode the frame: %s" % str(e) )		
			else:
				frame_tpl = self.encapsule(layer_ether=ether_tpl)
				frame_tpl.addRaw(read)
				try:
					# prepare event summary
					src_mac_tpl = ether_tpl.get('mac-source')
					src_mac = src_mac_tpl.getName()
					src_summary = 'From %s' % src_mac
					vendor_src = src_mac_tpl.get('vendor')
					if vendor_src is not None:
						 src_summary = 'From %s:%s' % ( vendor_src.replace(' ', ''), ':'.join( src_mac.split(':')[3:] ) )
						 
					dst_mac_tpl = ether_tpl.get('mac-destination')
					dst_mac = dst_mac_tpl.getName()
					dst_summary = 'To %s' % dst_mac
					vendor_dst = dst_mac_tpl.get('vendor')
					if vendor_dst is not None:
						 dst_summary = 'To %s:%s' % ( vendor_dst.replace(' ', ''), ':'.join( dst_mac.split(':')[3:] ) )
				except Exception as e:
					self.error( "failed to summarize: %s" % str(e) )		
				
				# log event
				ptype = ether_tpl.get('protocol-upper').getName()
				if self.logEventSent == False and self.logEventReceived == False:
					if self.protocol2sniff == codec.ALL:
						try:
							self.onReceiving(data=data_upper, lower=frame_tpl)
						except Exception as e:
							self.error( "on receiving ethernet, upper layer problem: %s" % str(e) )
					else:
						if self.protocol2sniff == ptype:
							try:
								self.onReceiving(data=data_upper, lower=frame_tpl)
							except Exception as e:
								self.error( "on receiving ethernet, upper layer problem: %s" % str(e) )		
						else:
							self.debug( 'discarding packet, not for me' )
				else:	
						if src_mac == self.src_mac:
								self.logSentEvent( shortEvt =  dst_summary, tplEvt = frame_tpl )						
						else:
							self.logRecvEvent( shortEvt = src_summary, tplEvt = frame_tpl )
		except Exception as e:
			self.error( "on handle data: %s" % str(e) )		
		self.__mutex2__.release()
		
	def onRun(self):
		"""
		"""
		self.__mutex__.acquire()
		try:
			if self.socket is not None: 
				if self.sniffing:
					r, w, e = select.select([ self.socket ], [], [ self.socket ], 0.01)
					if self.socket in e:
						raise EOFError("raw socket select error")
					elif self.socket in r:	
						read = self.socket.recv( TestAdapterLib.SOCKET_BUFFER )
						# decode data
						self.debug('data received (bytes %d), decoding attempt...' % len(read))
						self.onHandleData(read=read)
		except socket.error as e:
			self.onSocketError(e)
		except Exception as e:
			self.error( "on run ethernet: %s" % str(e) )		
		self.__mutex__.release()

	def onSocketError(self, e):
		"""
		"""
		self.error( "socket error: %s" % str(e) )
		
		# log event
		ether_tpl = templates.ethernet( more=templates.sniffing_failed(err=str(e)) )
		frame_tpl = self.encapsule(layer_ether=ether_tpl)
		self.logRecvEvent( shortEvt = "error", tplEvt = frame_tpl )
		
		# clean the socket
		self.cleanSocket()
		
	def onReceiving(self, data, lower=None):
		"""
		Function to overwrite
		Called on incoming data

		@param data: data received
		@type data: string
		
		@param lower: template data received
		@type lower: templatemessage
		"""
		pass
	
	@doc_public
	def hasReceivedFrame(self, timeout=1.0, dstMac=None, srcMac=None, protocolType=None, data=None):
		"""
		Waits to receive "frame" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ether_tpl = templates.ethernet(destAddr=dstMac, srcAddr=srcMac, etherType=protocolType, data=data)
		expected = self.encapsule(layer_ether=ether_tpl)
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
		
	@doc_public
	def isSniffing(self, timeout=1.0):
		"""
		Waits to receive "sniffing" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ether_tpl = templates.ethernet( more=templates.sniffing() )
		expected = self.encapsule(layer_ether=ether_tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isSniffingFailed(self, timeout=1.0):
		"""
		Waits to receive "sniffing failed" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
	
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage			
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ether_tpl = templates.ethernet( more=templates.sniffing_failed() )
		expected = self.encapsule(layer_ether=ether_tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isStopped(self, timeout=1.0):
		"""
		Waits to receive "stopped" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ether_tpl = templates.ethernet( more=templates.stopped() )
		expected = self.encapsule(layer_ether=ether_tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt