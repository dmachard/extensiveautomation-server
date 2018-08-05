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

AdapterEthernet = sys.modules['SutAdapters.%s.Ethernet' % TestAdapterLib.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IP' % TestAdapterLib.getVersion()]

try:
	import sniffer
except ImportError: # python3 support
	from . import sniffer
	
__NAME__="""Ping"""

AGENT_TYPE_EXPECTED='socket'

class Ping(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, debug=False, name=None, ipVersion=AdapterIP.IPv4, version=sniffer.ICMPv4, shared=False, 
											agentSupport=False, agent=None ):
		"""
		This class enables to send ping request
		The lower layer is based on the ICMP adapter.
	
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param ipVersion: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6
		@type ipVersion: intconstant	
		
		@param version: SutAdapters.ICMP.ICMPv4 (default) | SutAdapters.ICMP.ICMPv6
		@type version: intconstant	
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean		

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None
		"""
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																										debug=debug, shared=shared, 
																										realname=name, agentSupport=agentSupport, agent=agent,
																										caller=TestAdapterLib.caller(),
																										agentType=AGENT_TYPE_EXPECTED)
		self.icmp = sniffer.SnifferV4(parent=parent, debug=debug, logEventSent=True, logEventReceived=True,
																				shared=shared, agentSupport=agentSupport, agent=agent )
		
		self.cfg = {}
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
		self.icmp.stopListening()
		
	@doc_public
	def ip(self, interface, source, destination, timeout=1.0, destMac=None):
		"""
		Ping the destination ip passed as argument and wait a response.
		
		@param interface: network interface
		@type interface: string
		
		@param source: source ip
		@type source: string
		
		@param destination: destination ip
		@type destination: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@param destMac: destination mac address (default=None)
		@type destMac: string/none
		
		@return: pong response
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.icmp.startListening(eth=interface, srcIp=source )
		ipSniffing = self.icmp.isSniffing( timeout=timeout )
		if not ipSniffing:
			raise Exception('failed to start icmp')
		
		pong = self.icmp.echoQuery(destIp=destination, timeout=timeout, destMac=destMac)
		
		self.icmp.stopListening()
		ipStopped = self.icmp.isStopped( timeout=timeout ) 
		if not ipStopped:
			raise Exception('failed to stop icmp')	
		
		return pong
		