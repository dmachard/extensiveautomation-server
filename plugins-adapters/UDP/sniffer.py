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

AdapterEthernet = sys.modules['SutAdapters.%s.Ethernet' % TestAdapterLib.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IP' % TestAdapterLib.getVersion()]
AdapterICMP = sys.modules['SutAdapters.%s.ICMP' % TestAdapterLib.getVersion()]

import client
import codec
import templates

import struct
import time

AGENT_TYPE_EXPECTED='socket'

class Sniffer(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, debug=False, logEventSent=True, logEventReceived=True,
								ipVersion=AdapterIP.IPv4, port2sniff=codec.ALL,  name=None,
								separatorIn='0x00', separatorOut='0x00', separatorDisabled=True, inactivityTimeout=0.0,
								parentName=None, agentSupport=False, agent=None, shared=False):
		"""
		This class enables to send/receive UDP data.
		The lower layer is based on the IP adapter.
		Support data separator for upper application and inactivity detection.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param separatorIn: data separator (default=0x00)
		@type separatorIn: string
		
		@param port2sniff: udp port to sniff
		@type port2sniff: integer

		@param separatorOut: data separator (default=0x00)
		@type separatorOut: string

		@param separatorDisabled: disable the separator feature, if this feature is enabled then data are buffered until the detection of the separator (default=False)
		@type separatorDisabled: boolean
		
		@param inactivityTimeout: feature disabled by default (value=0.0)
		@type inactivityTimeout: float

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
		
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = client.__NAME__, parent = parent, debug=debug, shared=shared,
																	realname=name, agentSupport=agentSupport, agent=agent)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.port2sniff = port2sniff
		
		# udp codec
		self.udpCodec = codec.Codec(parent=self, testcase=parent, debug=debug, srcPort=port2sniff)
		
		# init ip layer
		## TODO: version IP
		self.ip = AdapterIP.SnifferV4(parent=parent, debug=debug, protocol2sniff=AdapterIP.UDP,
														logEventSent=False, logEventReceived=False, parentName=client.__NAME__,
														agentSupport=agentSupport, agent=agent, 
														name=name, shared=shared)
		if parentName is not None:
			self.ip.setname(name="%s>%s" % (parentName,client.__NAME__))
		self.ip.onReceiving = self.onDecodeData
		
		self.icmp = AdapterICMP.SnifferV4(parent=parent, debug=debug, lowerIpVersion=4, errorsOnly=True,
																				logEventSent=False, logEventReceived=False,
																				agentSupport=agentSupport, agent=agent, 
																				name=name, shared=shared)
		self.icmp.onIcmpError = self.onIcmpError
		
	
		self.cfg = {}
		self.cfg['ip-version'] = ipVersion
		self.cfg['sep-in'] = separatorIn
		self.cfg['sep-out'] = separatorOut
		self.cfg['sep-disabled'] = separatorDisabled
		self.cfg['inactivity-timeout'] = inactivityTimeout
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.__checkConfig()
		
		self.buf = {}

	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)
		if self.cfg['agent-support'] :
			self.warning('Agent mode activated') 
			
	def encapsule(self, layer):
		"""
		"""
		# prepare template
		tpl = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer(layer=layer)
		return tpl
		
	def onReset(self):
		"""
		Reset
		"""
		self.stopListening()
	
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		# stop thread
		self.unsetRunning()
		# stop all others adapters
		self.icmp.stopListening()
		self.ip.stopListening()
		
	
	@doc_public
	def startListening(self, eth, srcIp, srcMac=None ):
		"""
		Start listening
		
		@param eth: network interface identifier
		@type eth: string
		
		@param srcIp: source ip
		@type srcIp: string
		
		@param srcMac: source mac address
		@type srcMac: none/string
		"""
		self.icmp.startListening(eth=eth, srcIp=srcIp, srcMac=srcMac)
		self.ip.startListening(eth=eth, srcIp=srcIp, srcMac=srcMac)
		# start thread
		self.lastActivity = time.time()
		self.setRunning()
			
	@doc_public
	def isSniffing(self, timeout=1.0):
		"""
		Wait sniffing event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		snifferReady = True
		icmpSniff = self.icmp.isSniffing( timeout=timeout )
		if not icmpSniff:
			snifferReady = False
		
		if snifferReady:	
			snifferReady = self.ip.isSniffing(timeout=timeout)

		return snifferReady
		
	@doc_public
	def isStopped(self, timeout=1.0):
		"""
		Wait stopped event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		snifferStopped = True
		icmpStopped = self.icmp.isStopped( timeout=timeout )
		if not icmpStopped:
			snifferStopped = False
		
		if snifferStopped:	
			snifferStopped = self.ip.isStopped(timeout=timeout)

		return snifferStopped
	
	def onIcmpError(self, error):
		"""
		"""
		## TODO: version IP
		icmp = error.get('ICMP4') 
		icmp_type = icmp.get('type')
		icmp_type_str = icmp_type.get('string')
		if icmp_type_str is None:
			icmp_type_str = 'Unknown'
			
		icmp_code = icmp.get('code')
		icmp_code_str = icmp_code.get('string')
		if icmp_code_str is None:
			icmp_code_str = 'Unknown'
			
		icmp_data = icmp.get('data')
		if isinstance(icmp_data, TestTemplatesLib.TemplateLayer):
			icmp_data = icmp_data.getName()
		
		# check if the response is for me ?
		if icmp_data[:64] == self.ip.getLast64bSent():
			tpl = TestTemplatesLib.TemplateMessage()
			tpl.addLayer( layer=templates.udp( more=templates.icmp_error(error=icmp_type_str, details=icmp_code_str) ) )
			if self.logEventReceived: 
				self.logRecvEvent( shortEvt = 'icmp error', tplEvt = tpl )
					
	def onDecodeData(self, data, lower=None):
		"""
		"""
		# extract source and destination IP
		src_ip = lower.get('IP4', 'source-ip')
		if isinstance(src_ip, TestTemplatesLib.TemplateLayer):
			src_ip = src_ip.getName()
		dst_ip = lower.get('IP4', 'destination-ip')
		if isinstance(dst_ip, TestTemplatesLib.TemplateLayer):
			dst_ip = dst_ip.getName()
		self.debug ( 'ip level info extracted' )
		
		# try to decode the udp payload
		try:
			udp_tpl, summary, data_upper = self.udpCodec.decode(udp=data, ipSrc=src_ip, ipDst=dst_ip)
			if isinstance(udp_tpl.get('destination-port'), TestTemplatesLib.TemplateLayer):
				dst_port = udp_tpl.get('destination-port').getName()
			else:
				dst_port = udp_tpl.get('destination-port')
			if isinstance(udp_tpl.get('source-port'), TestTemplatesLib.TemplateLayer):
				src_port = udp_tpl.get('source-port').getName()
			else:
				dst_port = udp_tpl.get('source-port')
			fromAddr = ( src_ip, int(src_port) )
			toAddr = ( dst_port, int(dst_port) )
		except Exception as e:
			self.error( "Cannot decode the udp payload: %s" % str(e) )		
		
		# decode OK, we continue
		else:
			self.debug ( 'decode OK, we continue' )
			lower.addLayer( udp_tpl )
			self.debug ( 'upper layer added' )
			
			try:
				# log this event
				if self.port2sniff == codec.ALL:
					if self.logEventReceived: self.logRecvEvent( shortEvt = summary, tplEvt = lower )
					try:
						self.onReceiving(data=data_upper, lower=lower, fromAddr=fromAddr, toAddr=toAddr)
					except Exception as e:
						self.error( "on receiving all udp, upper layer problem: %s" % str(e) )
				else:
					if self.port2sniff == int(dst_port):
						if self.logEventReceived: self.logRecvEvent( shortEvt = summary, tplEvt = lower )
						try:
							self.onReceiving(data=data_upper, lower=lower, fromAddr=fromAddr, toAddr=toAddr)
						except Exception as e:
							self.error( "on receiving udp, upper layer problem: %s" % str(e) )
					else:
						self.debug( 'discarding packet, not for me' )
			except Exception as e:
				self.error( "on logging event udp: %s" % str(e) )		
				
	def onReceiving(self, data, fromAddr, toAddr, lower):
		"""
		Function to overwrite
		Called on incoming data

		@param data: data received
		@type data: string
		
		@param lower: template data received
		@type lower: templatemessage
		"""
		# extract transport info
		self.lastActivity = time.time()
		srcIp, srcPort = fromAddr
		dstIp, dstPort = toAddr
					
		# the separator feature is disabled, to nothing
		if self.cfg['sep-disabled']:
			try:
				self.handleIncomingData(data=data, lower=lower)
			except Exception as e:
				self.error( "on handle incoming udp data, upper layer problem: %s" % str(e) )
		else:
			# bufferize data
			if self.buf.has_key(fromAddr):
				self.buf[fromAddr] = ''.join([self.buf[fromAddr], data])
			else:
				self.buf[fromAddr] = data
			
			# split data with the separator
			datas = self.buf[fromAddr].split(self.cfg['sep-in'])
			for d in datas[:-1]:
				udp_data = d + self.cfg['sep-in']
				udp_data_size = len(udp_data)
				
				# construct high template and log it
				tpl = TestTemplatesLib.TemplateMessage()
				tpl.addLayer( layer=AdapterIP.ip( source=srcIp, destination=dstIp, more=AdapterIP.received(), version=self.cfg['ip-version'] ) )
				if self.logEventReceived: 
					udp_layer = templates.udp(source=srcPort, destination=dstPort, more=templates.received(data=udp_data, data_length=str(udp_data_size) ) )
				else:
					udp_layer = templates.udp(source=srcPort, destination=dstPort, more=templates.received(data_length=str(udp_data_size) ) )
				tpl.addLayer( layer=udp_layer )
				
				if self.logEventReceived: 
					tpl.addRaw(raw=udp_data)
					self.logRecvEvent( shortEvt = 'data reassembled', tplEvt = tpl )
				
				# handle data
				self.handleIncomingData( udp_data, lower=tpl)
			self.buf[fromAddr] = datas[-1]
		
	def onRun(self):
		"""
		"""
		if self.cfg['inactivity-timeout']:
			if time.time() - self.lastActivity > self.cfg['inactivity-timeout']:
				self.onInactivityTimeout()
				
	def onInactivityTimeout(self):
		"""
		"""
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer( layer=AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( layer=templates.udp( more=templates.received() ) )
		self.onInactivity(lower=tpl)

	def onInactivity(self, lower):
		"""
		Function to reimplement
		"""
		pass
		
		
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
		
	def addSeparator(self, data):
		"""
		Add the separator to the end of the data, if the feature is enabled	
		"""
		if self.cfg['sep-disabled']:
			return data
		else:
			return  ''.join( [ data, struct.pack('!B', int( self.cfg['sep-out'], 16 ) ) ] )
			
	@doc_public
	def sendData(self, data, destIp=None, destPort=0, srcPort=0, totalLength=None, checksum=None, destMac=None):
		"""
		Send data to the ip/port passed as argument
		
		@param data: data to send over udp
		@type data: string
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param totalLength: total length, auto computed if not provided
		@type totalLength: none/integer
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		"""
		try:
			if self.port2sniff == codec.ALL:
				src_port = int(srcPort)
			else:
				src_port = int(self.port2sniff)
			
			# add the separator 
			data = self.addSeparator(	data=data )
			
			layer_udp = templates.udp( source=src_port, destination=int(destPort), length=totalLength, sum=checksum, data=data )
		except Exception as e:
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  'Cannot prepare udp template: %s' % str(e) )
		else:
			# encode the template udp		
			try:
				udp_pkt, summary = self.udpCodec.encode(udp_tpl=layer_udp, ipSrc=self.ip.getSourceIP(), ipDst=destIp)
			except Exception as e:
				raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "Cannot encode udp data: %s" % str(e) )
			else:
				# Send packet	
				try:
					lower = self.ip.sendDatagram(dstMac=destMac, dstIp=destIp, data=udp_pkt, protocol=AdapterIP.UDP)
				except Exception as e:
					raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "Unable to send udp data: %s" % str(e) )
				else:
					lower.addLayer( layer_udp )
					if self.logEventSent:
						layer_udp.addRaw(raw=udp_pkt)
					else:
						layer_udp.addRaw(raw=udp_pkt[:codec.UDP_LEN])
					if self.logEventSent:
						self.logSentEvent( shortEvt = summary, tplEvt = lower ) 	
						
		return lower	
	
	@doc_public
	def hasReceivedIcmpError(self, timeout=1.0):
		"""
		Waits to receive "icmp error" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# prepare the expected template
		expected = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			expected.addLayer( layer_agent )
			
		expected.addLayer( layer=templates.udp( more=templates.icmp_error() ) )
			
		# wait 
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	
	@doc_public
	def hasReceivedData(self, timeout=1.0, dstIp=None, srcIp=None, srcPort=None, dstPort=None, data=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@param dstIp: destination ip
		@type dstIp: none/string/operators
		
		@param srcIp: source ip
		@type srcIp: none/string/operators
		
		@param srcPort: source port
		@type srcPort: none/integer/operators

		@param dstPort: destination port
		@type dstPort: none/integer/operators
		
		@param data: upper data
		@type data: none/string/operators

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# prepare the expected template
		ether_tpl = AdapterEthernet.ethernet()
		expected = self.encapsule(layer=ether_tpl)
		
		ip_tpl = AdapterIP.ip(source=srcIp, destination=dstIp)
		expected.addLayer(ip_tpl)
		
		udp_tpl = templates.udp(source=srcPort, destination=dstPort, data=None)
		expected.addLayer(udp_tpl)
		# wait 
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt