#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import codec4
import templates

__NAMEV4__="""ICMP4"""
__NAMEV6__="""ICMP6"""

ICMPv4    = 1
ICMPv6    = 58

AGENT_TYPE_EXPECTED='socket'

class Sniffer(TestAdapterLib.Adapter):
	def __init__(self, parent, debug=False, lowerIpVersion=AdapterIP.IPv4, version=ICMPv4, errorsOnly=False,
								logEventSent=True, logEventReceived=True, agentSupport=False, agent=None, shared=False,
								name=None):
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
		if version == ICMPv4:
			__NAME__ = __NAMEV4__
		if version == ICMPv6:
			__NAME__ = __NAMEV6__
			
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, realname=name, debug=debug,
																		shared=shared, agentSupport=agentSupport, agent=agent)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		# init icmp
		self.icmpCodec = codec4.Codec(parent=self, testcase=parent, debug=debug)
		
		# init ip layer
		self.ip = AdapterIP.SnifferV4(parent=parent, debug=debug, protocol2sniff=AdapterIP.ICMP,
																logEventSent=False, logEventReceived=False, disableArp=errorsOnly, 
															parentName=__NAME__, agentSupport=agentSupport, agent=agent, shared=shared)
		self.ip.onReceiving = self.onDecodeData

		self.cfg = {}
		self.cfg['listen-errors-only'] = errorsOnly
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

	def onReset(self):
		"""
		Reset
		"""
		self.stopListening()
	
	def stopListening(self):
		"""
		"""
		return self.ip.stopListening()
	
	def startListening(self, eth, srcIp, srcMac=None):
		"""
		"""
		return self.ip.startListening(eth=eth, srcIp=srcIp, srcMac=srcMac)

	def isSniffing(self, timeout=1.0):
		"""
		"""
		return self.ip.isSniffing(timeout=timeout)

	def isStopped(self, timeout=1.0):
		"""
		"""
		return self.ip.isStopped(timeout=timeout)
		
	def onDecodeData(self, data, lower=None):
		"""
		"""
		try:
			icmp_tpl, summary = self.icmpCodec.decode(icmp=data)
			type_icmp = icmp_tpl.get('type')
			if isinstance(type_icmp, TestTemplatesLib.TemplateLayer):
				type_icmp = type_icmp.getName()
		except Exception as e:
			self.error( "Cannot decode the icmp message: %s" % str(e) )		
		# decode OK
		else:
			if self.cfg['listen-errors-only'] and int(type_icmp) in \
						[ codec4.ECHO, codec4.ECHO_REPLY, codec4.TIMESTAMP, codec4.TIMESTAMP_REPLY, 
								codec4.INFORMATION, codec4.INFORMATION_REPLY, codec4.MASK, codec4.MASK_REPLY]:
				self.debug('listen errors only activated, discard packet')
			else:
				# add icmp layer
				lower.addLayer( icmp_tpl )
	
#				##### TODO ##### ip version 
#				src_ip = lower.get('IP4', 'source-ip')
#				if src_ip == self.ip.getSourceIP() :
#					self.logSentEvent( shortEvt = summary, tplEvt = lower )
#				else:
				if self.logEventReceived: 
					self.logRecvEvent( shortEvt = summary, tplEvt = lower )
				self.onIcmpError(error=lower)
					
	def onIcmpError(self, error):
		"""
		"""
		pass
		
class SnifferV4(Sniffer):
	@doc_public
	def __init__(self, parent, name=None, debug=False, lowerIpVersion=AdapterIP.IPv4, errorsOnly=False,
				logEventSent=True, logEventReceived=True, agentSupport=False, agent=None, shared=False):
		"""
		This class enables to send/receive ICMPv4 packet.
		The lower layer is based on the IP adapter.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param lowerIpVersion: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6
		@type lowerIpVersion: intconstant		
		
		@param errorsOnly: support errors message only (default=False)
		@type errorsOnly:	boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None
		
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
		Sniffer.__init__(self, parent=parent, debug=debug, lowerIpVersion=lowerIpVersion, errorsOnly=errorsOnly,
										logEventSent=logEventSent, logEventReceived=logEventSent , agentSupport=agentSupport, 
										agent=agent, shared=shared, name=name)
		
	def onIcmpError(self, error):
		"""
		Function to overwrite, called on incoming icmp errors

		@param error: icmp error
		@type error: templatemessage
		"""
		pass
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		return Sniffer.stopListening(self)
		
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
		return Sniffer.startListening(self, eth=eth, srcIp=srcIp, srcMac=srcMac)
		
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
	def sendPacket(self, destIp, type=8, code=0, checksum=None, identifier=None, sequenceNumber=None,
						data=None, destMac=None, timeOrig=None, timeReceive=None, timeTransmit=None, mask=None, gw=None, unused=None,
						pointer=None):
			"""
			Send ICMP packet.
			The destination MAC address is automatically resolved if not passed on argument.
			
			@param destIp: destination ip
			@type destIp: string
			
			@param type: icmp type (default=8)
			@type type: integer
			
			@param code: icmp code (default=0)
			@type code: integer
			
			@param checksum: icmp checksum
			@type checksum: none/string
			
			@param identifier: icmp identifier
			@type identifier: none/string
			
			@param sequenceNumber: icmp sequence number
			@type sequenceNumber: none/string
			
			@param data: icmp data
			@type data: none/string
			
			@param destMac: destination mac address
			@type destMac: none/string
			
			@param timeOrig: originate timestamp
			@type timeOrig: none/string
			
			@param timeReceive: receive timestamp
			@type timeReceive: none/string
			
			@param timeTransmit: transmit timestamp
			@type timeTransmit: none/string
			
			@param mask: netmask
			@type mask: none/string
			
			@param gw: gateway internet address
			@type gw: none/string
			
			@param unused: unused bytes
			@type unused: none/string
			
			@param pointer: pointer 
			@type pointer: none/string
			"""
			try:
				icmp_tpl = templates.icmp(code=code, id=identifier, seq_num=sequenceNumber, sum=checksum, data=data,
																	tp=type, time_orig=timeOrig, time_rx=timeReceive, time_tx=timeTransmit,
																	mask=mask, gw_addr=gw, unused=unused, pointer=pointer)
			except Exception as e:
				raise Exception('Cannot prepare icmp template: %s' % str(e))
			else:
				try:
					(pkt, summary) = self.icmpCodec.encode(icmp_tpl=icmp_tpl)
				except Exception as e:
					raise Exception("Cannot encode icmp: %s" % str(e))
				else:
					# Send packet	
					try:
						lower = self.ip.sendDatagram(dstMac=destMac, dstIp=destIp, data=pkt, protocol=AdapterIP.ICMP)
					except Exception as e:
						raise Exception("Unable to send datagram: %s" % str(e))	
					else:
						lower.addLayer( icmp_tpl )
						icmp_tpl.addRaw(raw=pkt)
						self.logSentEvent( shortEvt = summary, tplEvt = lower ) 	
						
	@doc_public
	def hasReceivedPacket(self, timeout=1.0, icmpCode=None, icmpType=None, icmpId=None, icmpSeq=None, icmpData=None,
														icmpTimeOrig=None, icmpTimeReceive=None, icmpTimeTransmit=None, icmpMask=None):			
		"""
		Waits to receive data event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@param icmpCode: icmp code
		@type icmpCode: none/string/operators
		
		@param icmpType: icmp type
		@type icmpType: none/string/operators
		
		@param icmpId: icmp identifier
		@type icmpId: none/string/operators
		
		@param icmpSeq: icmp sequence number
		@type icmpSeq: none/string/operators
		
		@param icmpData: icmp data
		@type icmpData: none/string/operators
		
		@param icmpTimeOrig: originate timestamp
		@type icmpTimeOrig: none/string/operators
		
		@param icmpTimeReceive: receive timestamp
		@type icmpTimeReceive: none/string/operators
		
		@param icmpTimeTransmit: transmit timestamp
		@type icmpTimeTransmit: none/string/operators
		
		@param icmpMask: icmp mask
		@type icmpMask: none/string/operators
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			expected.addLayer( layer_agent )
			
		# add layer ethernet
		layer_ether = AdapterEthernet.ethernet()
		expected.addLayer(layer=layer_ether)
		# add layer ip
		layer_ip = AdapterIP.ip()
		expected.addLayer(layer=layer_ip)
		# add layer icmp
		layer_icmp = templates.icmp(code=icmpCode, tp=icmpType, id=icmpId, seq_num=icmpSeq, data=icmpData,
																time_orig=icmpTimeOrig, time_rx=icmpTimeReceive, time_tx=icmpTimeTransmit,
																mask=icmpMask	)
		expected.addLayer(layer=layer_icmp)
		
		# try to match the template 
		evt = self.received( expected = expected, timeout = timeout )
		return evt
		
	@doc_public
	def echoQuery(self, destIp, timeout=1.0, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None, data=None):
		"""
		Send a echo request to the destination IP passed as argument and wait a response.
		The checksum is computed automatically if not provided.
		The default data sent is ABCDEFGHIJKLMNOPKRSTUVWXYZ.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string
		
		@param data: icmp echo data (default=None)
		@type data: none/string
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.ECHO, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, data=data, destMac=destMac)
		# wait reply
		return self.hasReceivedPacket( timeout=timeout, icmpCode=str(code), icmpType=str(codec4.ECHO_REPLY), 
												icmpId=identifier, icmpSeq=sequence )

	@doc_public
	def echoReply(self, destIp, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None, data=None):
		"""
		Send a echo reply to the destination IP passed as argument.
		The checksum is computed automatically if not provided.
		The default data sent is ABCDEFGHIJKLMNOPKRSTUVWXYZ.
		
		@param destIp: destination ip
		@type destIp: string

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string
		
		@param data: icmp echo data (default=None)
		@type data: none/string
		"""
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.ECHO_REPLY, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, data=data, destMac=destMac)
												
	@doc_public
	def informationQuery(self, destIp, timeout=1.0, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None):
		"""
		Send an information request  to the destination IP passed as argument and wait a response. The checksum is computed automatically if not provided.
		The ICMP Information Request/Reply pair was intended to support self-configuring systems such 
		as diskless workstations at boot time, to allow them to discover their network address.
		A host SHOULD NOT implement these messages.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.INFORMATION, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, destMac=destMac)
		# wait reply
		return self.hasReceivedPacket( timeout=timeout, icmpCode=code, icmpType=codec4.INFORMATION_REPLY, 
												icmpId=identifier, icmpSeq=sequence )

	@doc_public
	def informationReply(self, destIp, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None):
		"""
		Send an information request  to the destination IP passed as argument. The checksum is computed automatically if not provided.
		The ICMP Information Request/Reply pair was intended to support self-configuring systems such 
		as diskless workstations at boot time, to allow them to discover their network address.
		A host SHOULD NOT implement these messages.
		
		@param destIp: destination ip
		@type destIp: string

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string
		"""
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.INFORMATION_REPLY, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, destMac=destMac)
												
	@doc_public
	def timestampQuery(self, destIp, timeout=1.0, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None,
														timeOrig=None, timeReceive=None, timeTransmit=None):
		"""
		Send a timestamp request to the destination IP passed as argument and wait a response.
		The checksum is computed automatically if not provided.

		@param destIp: destination ip
		@type destIp: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string

		@param timeOrig: The originate timestamp is 32 bits of milliseconds since midnight UT
		@type timeOrig: none/integer/string
		
		@param timeReceive: The originate timestamp is 32 bits of milliseconds since midnight UT
		@type timeReceive: none/integer/string
		
		@param timeTransmit: The originate timestamp is 32 bits of milliseconds since midnight UT
		@type timeTransmit: none/integer/string
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.TIMESTAMP, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, destMac=destMac,
										timeOrig=timeOrig, timeReceive=timeReceive, timeTransmit=timeTransmit)
		# wait reply
		return self.hasReceivedPacket( timeout=timeout, icmpCode=code, icmpType=codec4.TIMESTAMP_REPLY, 
												icmpId=identifier, icmpSeq=sequence )

	@doc_public
	def timestampReply(self, destIp, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None,
														timeOrig=None, timeReceive=None, timeTransmit=None):
		"""
		Send a timestamp reply to the destination IP passed as argument.
		The checksum is computed automatically if not provided.

		@param destIp: destination ip
		@type destIp: string
		
		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string

		@param timeOrig: The originate timestamp is 32 bits of milliseconds since midnight UT
		@type timeOrig: none/integer/string
		
		@param timeReceive: The originate timestamp is 32 bits of milliseconds since midnight UT
		@type timeReceive: none/integer/string
		
		@param timeTransmit: The originate timestamp is 32 bits of milliseconds since midnight UT
		@type timeTransmit: none/integer/string
		"""
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.TIMESTAMP_REPLY, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, destMac=destMac,
										timeOrig=timeOrig, timeReceive=timeReceive, timeTransmit=timeTransmit)
												
	@doc_public
	def maskQuery(self, destIp, timeout=1.0, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None,
														mask="0.0.0.0"):
		"""
		Send a mask request to the destination IP passed as argument and wait a response.
		The checksum is computed automatically if not provided.

		@param destIp: destination ip
		@type destIp: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string

		@param mask: netmask (default=0.0.0.0)
		@type mask: string
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.MASK, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, destMac=destMac, mask=mask)
		# wait reply
		return self.hasReceivedPacket( timeout=timeout, icmpCode=code, icmpType=codec4.MASK_REPLY, 
												icmpId=identifier, icmpSeq=sequence )

	@doc_public
	def maskReply(self, destIp, destMac=None, code=0, identifier="0x0001", sequence="0x0001", checksum=None,
														mask="0.0.0.0"):
		"""
		Send a mask reply to the destination IP passed as argument.
		The checksum is computed automatically if not provided.

		@param destIp: destination ip
		@type destIp: string

		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param identifier: icmp echo id (default=0x0001)
		@type identifier: string
		
		@param sequence: icmp echo seq (default=0x0001)
		@type sequence: string
		
		@param checksum: overwrite the icmp checksum (default=none)
		@type checksum: none/string

		@param mask: netmask (default=0.0.0.0)
		@type mask: string
		"""
		if self.cfg['listen-errors-only']:
			self.debug('listen errors only activated')
			return None
			
		self.sendPacket(destIp=destIp, code=code, type=codec4.MASK_REPLY, checksum=checksum, identifier=identifier, 
										sequenceNumber=sequence, destMac=destMac, mask=mask)
	
	@doc_public
	def redirectError(self, destIp, destMac=None, code=0, checksum=None, gwAddr='0.0.0.0', data=None):
		"""
		Send a redirect error.
		The checksum is computed automatically if not provided.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: SutAdapters.ICMP.CODE_NETWORK (default) | SutAdapters.ICMP.CODE_HOST | SutAdapters.ICMP.CODE_TOS_NETWORK | SutAdapters.ICMP.CODE_TOS_HOST
		@type code: intconstant
		
		@param checksum: icmp checksum
		@type checksum: string
		
		@param gwAddr: gateway internet address
		@type gwAddr: string
		
		@param data: internet header and 64 bits of data datagram
		@type data: none/string
		"""
		self.sendPacket(destIp=destIp, code=code, type=codec4.REDIRECT, checksum=checksum, destMac=destMac, data=data, gw=gwAddr )
	
	@doc_public
	def sourceQuenchError(self, destIp, destMac=None, code=0, checksum=None, unused="0x00000000", data=None):
		"""
		Send a source quench error.
		The checksum is computed automatically if not provided.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: icmp code (default=0)
		@type code: integer
		
		@param checksum: icmp checksum
		@type checksum: string

		@param unused: unused bytes (default=0x00000000)
		@type unused: none/string

		@param data: internet header and 64 bits of data datagram
		@type data: none/string
		"""
		self.sendPacket(destIp=destIp, code=code, type=codec4.SOURCE_QUENCH, checksum=checksum, destMac=destMac, data=data, 
										unused=unused )		

	@doc_public
	def parameterProblemError(self, destIp, destMac=None, code=0, checksum=None, pointer="0x00", unused="0x000000", data=None):
		"""
		Send a parameter problem error.
		The checksum is computed automatically if not provided.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: if the coded is equal to zero then the pointer indicates the error. (default=0) 
		@type code: integer
		
		@param checksum: icmp checksum
		@type checksum: string

		@param pointer: identifies the octet where an error was detected. (default=0x00)
		@type pointer: string
		
		@param unused: unused bytes (default=0x000000)
		@type unused: string

		@param data: internet header and 64 bits of data datagram
		@type data: none/string
		"""
		self.sendPacket(destIp=destIp, code=code, type=codec4.PARAMETER_PROBLEM, checksum=checksum, destMac=destMac, data=data, 
										pointer=pointer, unused=unused )		

	@doc_public
	def timeExceededError(self, destIp, destMac=None, code=0, checksum=None, unused="0x00000000", data=None):
		"""
		Send a time exceeded error.
		The checksum is computed automatically if not provided.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: SutAdapters.ICMP.CODE_TTL (default) | SutAdapters.ICMP.CODE_FRAG
		@type code: intconstant
		
		@param checksum: icmp checksum
		@type checksum: string

		@param unused: unused bytes (default=0x00000000)
		@type unused: none/string

		@param data: internet header and 64 bits of data datagram
		@type data: none/string
		"""
		self.sendPacket(destIp=destIp, code=code, type=codec4.TIME_EXCEEDED, checksum=checksum, destMac=destMac, data=data, 
										unused=unused )		

	@doc_public
	def destinationUnreachableError(self, destIp, destMac=None, code=0, checksum=None, unused="0x00000000", data=None):
		"""
		Send a destination unreachable error.
		The checksum is computed automatically if not provided.
		
		@param destIp: destination ip
		@type destIp: string
		
		@param destMac: destination mac (default=none)
		@type destMac: none/string
		
		@param code: SutAdapters.ICMP.CODE_NET_UNREACH (default) | SutAdapters.ICMP.CODE_HOST_UNREACH | SutAdapters.ICMP.CODE_PROTOCOL_UNREACH | SutAdapters.ICMP.CODE_PORT_UNREACH | SutAdapters.ICMP.CODE_FRAG_NEEDED | SutAdapters.ICMP.CODE_SRC_ROUTE_FAILED
		@type code: intconstant
		
		@param checksum: icmp checksum
		@type checksum: string

		@param unused: unused bytes (default=0x00000000)
		@type unused: none/string

		@param data: internet header and 64 bits of data datagram
		@type data: none/string
		"""
		self.sendPacket(destIp=destIp, code=code, type=codec4.DESTINATION_UNREACHABLE, checksum=checksum, destMac=destMac, data=data, 
										unused=unused )	