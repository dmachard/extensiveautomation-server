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
AdapterARP = sys.modules['SutAdapters.%s.ARP' % TestAdapterLib.getVersion()]

import common
import codec4
import codec6
import templates

__NAMEV4__="""IP4"""
__NAMEV6__="""IP6"""

IPv4    = 4
IPv6    = 6

AGENT_TYPE_EXPECTED='socket'

class Sniffer(TestAdapterLib.Adapter):
	def __init__(self, parent, debug=False, logEventSent=True, logEventReceived=True,
								version=IPv4, protocol2sniff=common.ALL, disableArp=False, parentName=None,
								agentSupport=False, agent=None, shared=False, name=None):
		"""
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
		if version == IPv4:
			__NAME__ = __NAMEV4__
		if version == IPv6:
			__NAME__ = __NAMEV6__
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug,
																		shared=shared, agentSupport=agentSupport, agent=agent, realname=name)

		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.protocol2sniff = protocol2sniff
		self.version = version
		self.srcIp = None
		
		# init encoder/decoder
		if self.version == IPv4:
			etherSniff = AdapterEthernet.IPv4
			self.ipCodec = codec4.CodecV4(parent=self, testcase=parent, debug=debug)
		elif self.version == IPv6:
			etherSniff = AdapterEthernet.IPv6
			self.ipCodec = codec6.CodecV6(parent=self)
		else:
			raise Exception('unknown ip version: %s' % self.version)

		self.ether = AdapterEthernet.Sniffer(parent=parent, debug=debug, macResolution=False,
															padding=True, logEventSent=False, logEventReceived=False, 
															protocol2sniff=etherSniff, parentName=__NAME__,
															agentSupport=agentSupport, agent=agent, shared=shared)
		if parentName is not None:
			self.ether.setname(name="%s>%s" % (parentName,__NAME__))
		self.ether.onReceiving = self.onDecodeData
		

		self.arp = AdapterARP.Sniffer(parent=parent, debug=debug, senderIp=None, hideOperations=True,
																	agentSupport=agentSupport, agent=agent, shared=shared)
	
		self.cfg = {}
		self.cfg['disable-arp'] = disableArp
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']	
		self.__checkConfig()
		
	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)

	def setname(self, name):
		"""
		"""
		if self.version == IPv4:
			__NAME__ = __NAMEV4__
		if self.version == IPv6:
			__NAME__ = __NAMEV6__
		TestAdapterLib.Adapter.setName(self, name="%s>%s" % (name, __NAME__) )
			
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
		
	def stopListening(self):
		"""
		"""
		if not self.cfg['disable-arp']:
			self.arp.stopListening()
		self.ether.stopListening()
		
	def startListening(self, eth, srcIp, srcMac=None):
		"""
		"""
		self.srcIp = srcIp
		self.ipCodec.setSrcIp(ip=self.srcIp)
		
		if not self.cfg['disable-arp']:
			self.arp.setSender(ip=self.srcIp)
			self.arp.startListening(eth=eth)
			
		self.ether.startListening(eth=eth, srcMac=srcMac)
		
		self.debug( "source ip: %s" % self.srcIp )
		
	def getSourceIP(self):
		"""
		"""
		return self.srcIp
		
	def isSniffing(self, timeout=1.0):
		"""
		"""
		snifferReady = True
		ipSniff = self.ether.isSniffing( timeout=timeout )
		if not ipSniff:
			snifferReady = False
		if not self.cfg['disable-arp']:	
			arpSniff = self.arp.isSniffing( timeout=timeout )
			if not arpSniff:
				snifferReady = False
		return 	snifferReady	
	def isStopped(self, timeout=1.0):
		"""
		"""
		snifferStopped = True
		ipStopped = self.ether.isStopped( timeout=timeout )
		if not ipStopped:
			snifferStopped = False
		if not self.cfg['disable-arp']:
			arpStopped = self.arp.isStopped( timeout=timeout )
			if not arpStopped:
				snifferStopped = False
		return 	snifferStopped	
		
	def onSending(self, lower):
		"""
		Function to reimplement
		
		@param lower: template message
		@type lower: template
		"""
		pass

	def onDecodeData(self, data, lower=None):
		"""
		"""
#		self.__mutexsniff__.acquire()
		try:
			ip_tpl, summary, data_upper = self.ipCodec.decode(ip=data)
			pro = ip_tpl.get('protocol').getName()
		except Exception as e:
			self.error( "Cannot decode the packet: %s" % str(e) )		
		# decode OK
		else:
			# encapsule
			self.debug ( 'decode OK, we continue' )
			try:
				lower.addLayer( ip_tpl )
			except Exception as e:
				self.error( "add layer failed: %s" % str(e) )
			else:
				self.debug ( 'upper layer added' )

			try:
				# log event
				if self.logEventSent == False and self.logEventReceived == False:
					# handle incoming data
					if self.protocol2sniff == common.ALL:
						try:
							self.onReceiving(data=data_upper, lower=lower)
						except Exception as e:
							self.error( "on receiving all ip, upper layer problem: %s" % str(e) )
					else:
						if self.protocol2sniff == int(pro):
							try:
								self.onReceiving(data=data_upper, lower=lower)
							except Exception as e:
								self.error( "on receiving ip, upper layer problem: %s" % str(e) )
						else:
							self.debug( 'discarding packet, not for me' )
				else:
					if summary.startswith('To'):
						self.logSentEvent( shortEvt =  summary, tplEvt = lower )
					else:
						self.logRecvEvent( shortEvt = summary, tplEvt = lower )
			except Exception as e:
				self.error( "on logging event ip: %s" % str(e) )
#			self.__mutexsniff__.release()
			
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

class SnifferV4(Sniffer):
	@doc_public
	def __init__(self, parent, name=None, debug=False, logEventSent=True, logEventReceived=True, protocol2sniff=common.ALL,
								disableArp=False, parentName=None, agentSupport=False, agent=None, shared=False):
		"""
		This class enables to send/receive IP v4 datagram.
		The lower layer is based on the Ethernet adapter.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param protocol2sniff: SutAdapters.IP.ALL (default) | SutAdapters.IP.ICMP | SutAdapters.IP.TCP | SutAdapters.IP.UDP
		@type protocol2sniff: strconstant

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/none

		@param shared: shared adapter (default=False)
		@type shared:	boolean
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
		Sniffer.__init__(self, parent=parent, debug=debug, logEventSent=logEventSent, logEventReceived=logEventReceived,
												version=IPv4, protocol2sniff=protocol2sniff, disableArp=disableArp, parentName=parentName,
												agentSupport=agentSupport, agent=agent, shared=shared, name=name)
		self.last64bSent = '' # last 64 bits sent
	
	@doc_public
	def getLast64bSent(self):
		"""
		Return 64 bits of the last data datagram sent
		
		@return: 64 bits of data datagram
		@rtype:	string
		"""
		return self.last64bSent
		
	@doc_public
	def getSourceIP(self):
		"""
		Return the source IP
		
		@return: source ip
		@rtype: string
		"""
		return Sniffer.getSourceIP(self)
		
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		Sniffer.stopListening(self)
		
	@doc_public
	def startListening(self, eth, srcIp, srcMac=None):
		"""
		Start listening
		
		@param eth: network interface identifier
		@type eth: string
		
		@param srcIp: source ip
		@type srcIp: string
		
		@param srcMac: source mac address
		@type srcMac: none/string
		"""		
		Sniffer.startListening(self, eth=eth, srcIp=srcIp, srcMac=srcMac)
		
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
		
		return Sniffer.isSniffing(self, timeout=timeout)
		
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
		
		return Sniffer.isStopped(self, timeout=timeout)
		
	@doc_public
	def sendDatagram(self, dstIp, data, dstMac=None, protocol=common.ICMP, ttl=64, headerLength=None, checksum=None,
										totalLength=None, identification="0x0000", flags="0x00", typeService=None,  fragmentOffset=None,
										version=None):
		""" 
		Send an IP datagram.
		The checksum is automaticly computed if not provided.
		
		@param dstIp: destination ip to send the datagram
		@type dstIp: string

		@param data: data to send
		@type data: string
		
		@param dstMac: destination mac address
		@type dstMac: none/string

		@param protocol: SutAdapters.IP.ICMP (default) | SutAdapters.IP.UDP | SutAdapters.IP.TCP
		@type protocol: intconstant
		
		@param ttl: time to live value (default=128)
		@type ttl: integer
		
		@param headerLength: header length
		@type headerLength: none/string
		
		@param checksum: ip header checksum
		@type checksum: none/string
		
		@param totalLength: total length
		@type totalLength: none/string
		
		@param identification: datagram identification (default=0x0000)
		@type identification: string
		
		@param typeService: type of service
		@type typeService: none/string
		
		@param flags: flags (default=0x02)
		@type flags: string
		
		@param fragmentOffset: fragment offset
		@type fragmentOffset: none/string
		
		@param version: overwrite the version
		@type version: none/integer
	
		@return: ip layer encapsulate in ethernet
		@rtype:	templatemessage
		"""
		# set the destination mac addr 
		if dstMac is not None:
			dst_mac = dstMac
		else:
			# search mac address in the arp cache  or 
			# resolve the IP if not found
			if not self.cfg['disable-arp']:
				mac = self.arp.searchCache(ip=dstIp)
			else:
				mac = None
			if mac is not None:
				dst_mac = mac
			else:
				# resolv the mac addr ?
				if not self.cfg['disable-arp']:
					rsp_fr = self.arp.whoHas(targetIp=dstIp)
				else:
					rsp_fr = None
				if rsp_fr is not None:
					arp = rsp_fr.get('ARP')
					dst_mac = arp.get('sender-mac')
#					ether = rsp_fr.get('ETHERNET-II')
#					dst_mac = ether.get('mac-source').getName()
				else:
					dst_mac = TestValidatorsLib.MacAddress().getBroadcast()
		
		ver = self.version
		if version is not None:
			ver = version
		# init the ip layer
		layer_ip = templates.ip(version=ver, data=data, data_size=len(data), ttl=ttl, source=self.srcIp, destination=dstIp,
															pro=protocol, sum=checksum, ihl=headerLength, tl=totalLength, id=identification, tos=typeService,
															flg=flags, frg=fragmentOffset)
		
		# encode the template ip		
		try:
			datagram, summary = self.ipCodec.encode(ip_tpl=layer_ip)
		except Exception as e:
			raise Exception("Cannot encode the datagram: %s" % str(e))
		else:
			# Send packet
			try:
				lower = self.ether.sendFrame( data=datagram, dstMac=dst_mac, protocolType=AdapterEthernet.IPv4 )
			except Exception as e:
				raise Exception("send frame failed: %s" % str(e))	
			else:
				# save the first 64 bits of this datagram, these bytes are used with icmp destination unreachable
				self.last64bSent = datagram[:64]
				
				# log event
				lower.addLayer( layer_ip )
				if self.logEventSent:
					layer_ip.addRaw(raw=datagram)
				else:
					layer_ip.addRaw(raw=datagram[:codec4.IPV4_LEN])
				if self.logEventSent:
					self.logSentEvent( shortEvt = summary, tplEvt = lower ) 	
					
		return lower
		
	@doc_public
	def hasReceivedDatagram(self, timeout=1.0, dstIp=None, srcIp=None, protocolIp=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@param dstIp: destination ip
		@type dstIp: none/string/operators
		
		@param srcIp: source ip
		@type srcIp: none/string/operators
		
		@param protocolIp: upper protocol
		@type protocolIp: none/string/operators

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# prepare the expected template
		ether_tpl = AdapterEthernet.ethernet()
		expected = self.encapsule(layer=ether_tpl)
		ip_tpl = templates.ip(source=srcIp, destination=dstIp, pro=protocolIp)
		expected.addLayer(ip_tpl)
		# wait 
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
		
class SnifferV6(Sniffer):
	def __init__(self, parent, debug=False, logEventSent=True, logEventReceived=True, protocol2sniff=common.ALL,
								disableArp=False, parentName=None, agentSupport=False, agent=None):
		"""
		This class enables to send/receive IP v6 datagram.
		The lower layer is based on the Ethernet adapter.
		
		@param parent: parent testcase
		@type parent: testcase
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param protocol2sniff: SutAdapters.IP.ALL (default) | SutAdapters.IP.ICMP | SutAdapters.IP.TCP | SutAdapters.IP.UDP
		@type protocol2sniff: intconstant

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None
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
		Sniffer.__init__(self, parent=parent, debug=debug, logEventSent=logEventSent, logEventReceived=logEventReceived,
												version=IPv6, protocol2sniff=protocol2sniff, disableArp=disableArp, parentName=parentName,
												agentSupport=agentSupport, agent=agent)
	def getSourceIP(self):
		"""
		Return the source IP
		
		@return: source ip
		@rtype: string
		"""
		return Sniffer.getSourceIP(self)
	def stopListening(self):
		"""
		Stop listening
		"""
		Sniffer.stopListening(self)		
	def startListening(self, eth, srcIp, srcMac=None):
		"""
		Start listening
		
		@param eth: network interface identifier
		@type eth: string
		
		@param srcIp: source ip
		@type srcIp: string
		
		@param srcMac: source mac address
		@type srcMac: none/string
		"""		
		Sniffer.startListening(self, eth=eth, srcIp=srcIp, srcMac=srcMac)
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
		
		return Sniffer.isSniffing(self, timeout=timeout)
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
		
		return Sniffer.isStopped(self, timeout=timeout)		