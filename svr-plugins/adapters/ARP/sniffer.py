#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

AdapterEthernet = sys.modules['SutAdapters.%s.Ethernet' % TestAdapterLib.getVersion()]

try:
	import codec
	import templates
except ImportError: # python3 support
	from . import codec
	from . import templates

__NAME__="""ARP"""

AGENT_TYPE_EXPECTED='socket'

class Sniffer(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, debug=False, name=None, senderIp=None, logEventSent=True, logEventReceived=True,
									hideOperations=False, cacheEnabled=True, agentSupport=False, agent=None, shared=False
							):
		"""
		This class enables to send/receive ARP packet. 
		The lower layer is based on the Ethernet adapter.
		Cache support and dynamically updated.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param senderIp: sender ip (default=None)
		@type senderIp: string/none
		
		@param hideOperations: hide all operations (default=False)
		@type hideOperations:	boolean
		
		@param cacheEnabled: cache mechanism enabled (default=True)
		@type cacheEnabled:	boolean
		
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, 
																									realname=name, agentSupport=agentSupport, agent=agent,
																									caller=TestAdapterLib.caller(),
																									agentType=AGENT_TYPE_EXPECTED)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.ether = AdapterEthernet.Sniffer(parent=parent, debug=debug, macResolution=True, 
																												logEventSent=False, logEventReceived=False, 
																												protocol2sniff=AdapterEthernet.ARP, parentName=__NAME__ , 
																												agentSupport=agentSupport, agent=agent,
																												shared=shared, name=name)
		# wrappers
		self.ether.onReceiving = self.onReceiving
		self.startListening = self.ether.startListening
		self.stopListening = self.ether.stopListening
		self.isSniffing = self.ether.isSniffing
		self.isSniffingFailed = self.ether.isSniffingFailed
		self.isStopped = self.ether.isStopped
		
		self.senderIp = senderIp
		# codec arp
		self.arpCodec = codec.Codec(parent=self)

		self.cfg = {}
		self.cfg['hide-operations'] = hideOperations
		self.cfg['cache-enabled'] = cacheEnabled
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		
		# used to recognize the response
		self.__sender_mac = ''
		self.__sender_ip = ''
		
		# cache
		self.cache = {}

		self.__checkConfig()

	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)

	@doc_public
	def getCache(self):
		"""
		Get the content of the cache
		
		@return: arp cache
		@rtype: dict	
		"""
		if not self.cfg['cache-enabled']:
			self.warning( 'cache mechanism is disabled' )
		return self.cache
	
	@doc_public
	def searchCache(self, ip):
		"""
		Search the mac address associated to the ip in the cache
		
		@param ip: destination IP
		@type ip: string
		
		@return: mac address associated to the ip
		@rtype: string/none	
		"""
		if not self.cfg['cache-enabled']:
			self.warning( 'cache mechanism is disabled' )
		if self.cache.has_key(ip):
			return self.cache[ip]
		else:
			return None
			
	@doc_public
	def setSender(self, ip):
		"""
		Set the sender IP
		
		@param ip: destination IP
		@type ip: string
		"""
		self.senderIp = ip
		
	
	@doc_public
	def startListening(self, eth, srcMac=None):
		"""
		Start listening 
		
		@param eth: device
		@type eth: string
		
		@param srcMac: source mac address
		@type srcMac: string/none
		"""
		return self.ether.startListening(eth=eth, srcMac=srcMac)
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		return self.ether.stopListening()
	
	@doc_public
	def isSniffing(self, timeout=1.0):
		"""
		Wait sniffing event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.ether.isSniffing(timeout=timeout)

	@doc_public
	def isStopped(self, timeout=1.0):
		"""
		Wait stopped event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.ether.isStopped(timeout=timeout)
		
	def onReset(self):
		"""
		Reset
		"""
		self.ether.stopListening()
		
	def onReceiving(self, data, lower):
		"""
		"""
		try:
			arp_tpl, summary = self.arpCodec.decode(arp=data)		
			lower.addLayer( arp_tpl )
		except Exception as e:
			self.error( 'Cannot decode arp: %s' % str(e))
		else:
			op = arp_tpl.get('op-code').getName()
			target_ip = arp_tpl.get('target-ip')
			target_mac = arp_tpl.get('target-mac')
			# event summary	
			if self.logEventReceived:
				if self.cfg['hide-operations']:
					self.debug( 'hide operations activated' )
					if self.__sender_mac == target_mac and self.__sender_ip == target_ip:
						self.logRecvEvent( shortEvt = summary, tplEvt = lower )
						self.__sender_ip = ''
						self.__sender_mac = ''
				else:
					self.logRecvEvent( shortEvt = summary, tplEvt = lower )
	
			# update the cache
			if not self.cfg['cache-enabled']:
				self.warning( 'cache mechanism is disabled' )
			else:
				if op == codec.OP_REQUEST:
					ip = arp_tpl.get('sender-ip')
					mac = arp_tpl.get('sender-mac')
					self.cache[ip] = mac
				
			
	@doc_public
	def hasReceivedPacket(self, timeout=1.0, op=None, dstEthernet=None, srcEthernet=None, targetIp=None, senderIp=None,
													targetMac=None, senderMac=None):
		"""
		Wait event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param op: SutAdapters.ARP.OP_REQUEST (default) | SutAdapters.ARP.OP_REPLY
		@type op: none/strconstant/operator
		
		@param dstEthernet: ethernet destination mac 
		@type dstEthernet: none/string/operator
		
		@param srcEthernet: ethernet source mac 
		@type srcEthernet: none/string/operator
		
		@param targetIp: arp target ip
		@type targetIp: none/string/operator
		
		@param senderIp: arp sender ip
		@type senderIp: none/string/operator
		
		@param targetMac: arp target mac
		@type targetMac: none/string/operator
		
		@param senderMac: arp sender ip
		@type senderMac: none/string/operator
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		expected = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			expected.addLayer( layer_agent )
			
		layer_ether = AdapterEthernet.ethernet(destAddr=dstEthernet, srcAddr=srcEthernet)
		expected.addLayer(layer=layer_ether)
		layer_arp = templates.arp(op=op, sha=senderMac, spa=senderIp, tha=targetMac, tpa=targetIp)
		expected.addLayer(layer=layer_arp)
		
		# try to match the template 
		evt = self.received( expected = expected, timeout = timeout )
		return evt
		
	@doc_public
	def sendPacket(self, hardwareType=codec.HARDWARE_TYPE, protocolType=AdapterEthernet.IPv4, 
											op=codec.OP_REQUEST, hardwareLen=codec.HARDWARE_LEN, protocolLen=codec.PROTOCOL_LEN,
											senderIp='0.0.0.0', senderMac='00:00:00:00:00:00',
											targetIp='0.0.0.0', targetMac='00:00:00:00:00:00',
											ethernetDstMac='FF:FF:FF:FF:FF:FF'):
		"""
		Send ARP packet
		
		@param hardwareType: SutAdapters.ARP.HARDWARE_TYPE (default)
		@type hardwareType: strconstant
		
		@param protocolType: SutAdapters.Ethernet.IPv4 (default)
		@type protocolType: strconstant
		
		@param op: SutAdapters.ARP.OP_REQUEST (default) | SutAdapters.ARP.OP_REPLY
		@type op: strconstant
		
		@param hardwareLen: SutAdapters.ARP.HARDWARE_LEN (default)
		@type hardwareLen: strconstant
		
		@param protocolLen: SutAdapters.ARP.PROTOCOL_LEN (default)
		@type protocolLen: strconstant
		
		@param senderIp: sender ip (default=0.0.0.0)
		@type senderIp: string
		
		@param targetIp: target ip (default=0.0.0.0)
		@type targetIp: string
		
		@param senderMac: sender mac (default=00:00:00:00:00:00)
		@type senderMac: string
		
		@param targetMac: target mac (default=00:00:00:00:00:00)
		@type targetMac: string
		
		@param ethernetDstMac: ethernet destination mac (default=FF:FF:FF:FF:FF:FF)
		@type ethernetDstMac: string
		"""
		try:
			self.__sender_mac = senderMac
			self.__sender_ip = senderIp
			arp_tpl = templates.arp(hrd=hardwareType, pro=protocolType, hln=hardwareLen, pln=protocolLen, op=op, 
															sha=senderMac, spa=senderIp, tha=targetMac, tpa=targetIp)
			try:
				(pkt, summary) = self.arpCodec.encode(arp_tpl=arp_tpl)
			except Exception as e:
				raise Exception("Cannot encode arp: %s" % str(e))
			else:
				# Send packet
				try:
					lower = self.ether.sendFrame( data=pkt, dstMac=ethernetDstMac, protocolType=AdapterEthernet.ARP )
				except Exception as e:
					raise Exception("send frame failed: %s" % str(e))	
				else:
					lower.addLayer( arp_tpl )
					arp_tpl.addRaw(raw=pkt)
					if self.logEventSent:
						self.logSentEvent( shortEvt = summary, tplEvt = lower ) 	
				
		except Exception as e:
			raise Exception('Unable to send arp packet: %s' % str(e))
			
	@doc_public
	def whoHas(self, targetIp, timeout=1.0, ethernetMac=False, senderIp=None):
		"""
		Who has the target IP passed as argument.
		Wait reply until the end of the timeout.
		The mac address is saved in the cache.
		
		@param targetIp: target ip to discover
		@type targetIp: string
		
		@param senderIp: sender ip (default=None)
		@type senderIp: none/string
		
		@param ethernetMac: save the mac address of the ethernet layer on cache, otherwise the sender mac address (default=False)
		@type ethernetMac: boolean
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		senderMac = self.ether.getSourceMac()
		if senderIp is None:
			if self.senderIp is not None:
				senderIp = self.senderIp
			else:
				senderIp = '0.0.0.0'
		targetMac = TestValidatorsLib.MacAddress().getNull()
		
		# send request
		self.sendPacket(  op=codec.OP_REQUEST,
											senderIp=senderIp,  targetIp=targetIp, 
											senderMac=senderMac, targetMac=targetMac)
		# wait reply
		rsp = self.hasReceivedPacket( timeout=timeout, op=codec.OP_REPLY,
																		targetMac=senderMac,  targetIp=senderIp, senderIp=targetIp,
																	dstEthernet=senderMac	)
		# save mac on the cache
		if rsp is not None:
			if not self.cfg['cache-enabled']:
				self.warning( 'cache mechanism is disabled' )
			else:
				ether = rsp.get('ETHERNET-II')
				arp = rsp.get('ARP')
				if ethernetMac:
					dst_mac = ether.get('mac-source').getName()
				else:
					dst_mac = arp.get('sender-mac')
				self.cache[targetIp] = dst_mac
			
		return rsp
		
	@doc_public
	def gratuitousArp(self, opRequest=False):
		"""
		A Gratuitous ARP could be a request or a reply. 
		Systems that receive gratuitous ARP reply packets will automatically update 
		the ARP table with the IP address with the new MAC Address.
		
		@param opRequest: True to send request otherwise reply (default=False)
		@type opRequest: boolean
		"""
		if opRequest:
			op =codec.OP_REQUEST
		else:
			op =codec.OP_REPLY
			
		senderMac = self.ether.getSourceMac()
		senderIp = '0.0.0.0'
		if self.senderIp is not None:
			senderIp = self.senderIp
		targetMac = TestValidatorsLib.MacAddress().getBroadcast()
			
		# send request
		self.sendPacket(  op=op, senderIp=senderIp,  targetIp=senderIp, senderMac=senderMac, targetMac=targetMac)	