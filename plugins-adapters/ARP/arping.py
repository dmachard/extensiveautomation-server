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

import sniffer

__NAME__="""Arping"""

AGENT_TYPE_EXPECTED='socket'

class Arping(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, debug=False, name=None, shared=False, agentSupport=False, agent=None):
		"""
		This class enables to send arp request
		The lower layer is based on the ARP adapter.
	
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
	
		@param shared: shared adapter (default=False)
		@type shared:	boolean	

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, 
																			realname=name, agentSupport=agentSupport, agent=agent)
		self.arp = sniffer.Sniffer(parent=parent, debug=debug, logEventSent=True, logEventReceived=True,
																		shared=shared, name=name, agentSupport=agentSupport, agent=agent)
		
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
		self.arp.stopListening()
		
	@doc_public
	def ip(self, interface, sourceMac, sourceIp, destinationIp, timeout=1.0):
		"""
		Arping the destination ip passed as argument and wait a response.
		
		@param interface: network interface
		@type interface: string
		
		@param sourceMac: source mac
		@type sourceMac: string
		
		@param sourceIp: source ip
		@type sourceIp: string
		
		@param destinationIp: destination ip
		@type destinationIp: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@return: pong response
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.arp.startListening(eth=interface, srcMac=sourceMac )
		arpSniffing = self.arp.isSniffing( timeout=timeout )
		if not arpSniffing:
			raise Exception('failed to start arp')
		
		pong = self.arp.whoHas(targetIp=destinationIp, senderIp=sourceIp, timeout=timeout)
		
		self.arp.stopListening()
		arpStopped = self.arp.isStopped( timeout=timeout ) 
		if not arpStopped:
			raise Exception('failed to stop arp')	
		
		return pong