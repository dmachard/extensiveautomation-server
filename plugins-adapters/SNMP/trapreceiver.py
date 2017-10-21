#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.proto import rfc1902

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterUDP = sys.modules['SutAdapters.%s.UDP' % TestAdapterLib.getVersion()]

import templates

__NAME__="""TRAPRECEIVER"""

AGENT_TYPE_EXPECTED='socket'

TRAP_V1 = "trap-v1"
TRAP_V2C = "trap-v2c"
TRAP_V3 = "trap-v3"

class TrapReceiver(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, name=None, debug=False, bindIp = '', bindPort=0,
								logEventReceived=True, agentSupport=False, agent=None, shared=False,
								):
		"""
		SNMP trap receiver v1 and v2c

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer
		
		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/none
		
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.logEventReceived = logEventReceived

		# init udp layer
		self.ADP_UDP = AdapterUDP.Client(parent=parent, debug=debug, name=name, 
											bindIp = bindIp, bindPort=bindPort, 
											destinationIp='', destinationPort=0,  destinationHost='', 
											socketFamily=AdapterIP.IPv4, separatorDisabled=True, inactivityTimeout=0,
											logEventSent=False, logEventReceived=False, parentName=__NAME__, agentSupport=agentSupport,
											agent=agent, shared=shared)
		
		# callback udp
		self.ADP_UDP.handleIncomingData = self.onIncomingData

		self.cfg = {}
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.__checkConfig()

	def udp(self):
		"""
		"""
		return self.ADP_UDP
	
	@doc_public
	def startListening(self):
		"""
		Start listening
		"""
		self.ADP_UDP.startListening()
	
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		self.ADP_UDP.stopListening()
		
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	

	def onReset(self):
		"""
		"""
		self.stopListening()

	def onIncomingData(self, data, lower):
		"""
		"""
		try:
			snmpVersion = int(api.decodeMessageVersion(data))
			if snmpVersion in api.protoModules:
				# detect version
				if snmpVersion == api.protoVersion1:
					self.debug( 'snmp v1 detected' )
				if snmpVersion == api.protoVersion2c:
					self.debug( 'snmp v2c detected' )	
					
				# get lib according to the version
				pMod = api.protoModules[snmpVersion]
				snmpMsg, m = decoder.decode(data, asn1Spec=pMod.Message() )
				snmpPdu = pMod.apiMessage.getPDU(snmpMsg)
				snmpError = pMod.apiPDU.getErrorStatus(snmpPdu)
				
				isTrap = snmpPdu.isSameTypeWith(pMod.TrapPDU())
				if not isTrap:
					self.error('unknown snmp data received')
				else:
					varBinds = pMod.apiTrapPDU.getVarBindList(snmpPdu)
					varbinds_tpl = TestTemplatesLib.TemplateLayer(name='')
					i = 0
					for varBind in varBinds:
						oid = varBind[0]
						value = varBind[1]
						varbind = TestTemplatesLib.TemplateLayer(name='')
						varbind.addKey(name='oid', data="%s" % oid)
						if value.getComponent().getComponent().typeId is None:
							varbind.addKey(name='value', data=value.getComponent().getComponent().prettyPrint() )
						else:
							varbind.addKey(name='value', data=value.getComponent().getComponent().getComponent().prettyPrint() )
						varbind.addKey(name='type-value', data=value.getComponent().getName() )
						varbinds_tpl.addKey(name=str(i), data=varbind)
						i += 1
							
					# trap v1
					if snmpVersion == api.protoVersion1:
						
						
							
						tpl_snmp = templates.snmp( 
																		version=TRAP_V1,
																		community= "%s" % pMod.apiMessage.getCommunity(snmpMsg) ,
																		agentAddr= "%s" % pMod.apiTrapPDU.getAgentAddr(snmpPdu).prettyPrint(),
																		enterprise= "%s" % pMod.apiTrapPDU.getEnterprise(snmpPdu).prettyPrint(),
																		genericTrap= "%s" % pMod.apiTrapPDU.getGenericTrap(snmpPdu).prettyPrint(),
																		specificTrap= "%s" % pMod.apiTrapPDU.getSpecificTrap(snmpPdu).prettyPrint(),
																		uptime = "%s" % pMod.apiTrapPDU.getTimeStamp(snmpPdu).prettyPrint(),
																		varbinds=varbinds_tpl
																	)
						if self.logEventReceived:
							lower.addLayer( tpl_snmp )
							self.logRecvEvent(shortEvt='Trap v1', tplEvt=lower)
					
					# trap v2c
					if snmpVersion == api.protoVersion2c:	
						tpl_snmp = templates.snmp( 	
																		version=TRAP_V2C,
																		community= "%s" % pMod.apiMessage.getCommunity(snmpMsg) ,
																		requestId= "%s" % pMod.apiPDU.getRequestID(snmpPdu),
																		errorStatus = "%s" % pMod.apiPDU.getErrorStatus(snmpPdu),
																		errorIndex = "%s" % pMod.apiPDU.getErrorIndex(snmpPdu),
																		varbinds=varbinds_tpl
																		)
						if self.logEventReceived:
							lower.addLayer( tpl_snmp )
							self.logRecvEvent(shortEvt='Trap v2c', tplEvt=lower)												

			else:
				self.error('Unsupported SNMP version %s' % snmpVersion)
		except Exception as e:
			self.error('Error while waiting traps: %s' % str(e))		
			
	@doc_public
	def isListening(self, timeout=1.0):
		"""
		Wait to receive "listening" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_UDP.isListening(timeout=timeout)

	@doc_public
	def isStopped(self, timeout=1.0):
		"""
		Wait to receive "stopped" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_UDP.isStopped(timeout=timeout)
	
	@doc_public
	def hasReceivedTrap(self, timeout=1.0, version=None, community=None, agentAddr=None, enterprise=None, 
												genericTrap=None, specificTrap=None, uptime=None, requestId=None, errorStatus=None, 
												errorIndex=None):
		"""
		Waits to receive "trap" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param version: SutAdapters.SNMP.TRAP_V1 | SutAdapters.SNMP.TRAP_V2C
		@type version: strconstant/none
		
		@param community: community expected
		@type community: string/operators/none	
		
		@param agentAddr: agent address expected
		@type agentAddr: string/operators/none	
		
		@param enterprise: enterprise oid expected
		@type enterprise: string/operators/none	
		
		@param genericTrap: generic trap expected
		@type genericTrap: string/operators/none	
		
		@param specificTrap: specific trap  expected
		@type specificTrap: string/operators/none	
		
		@param uptime: uptime expected
		@type uptime: string/operators/none	
		
		@param requestId: request id expected
		@type requestId: string/operators/none	
		
		@param errorStatus: error status expected
		@type errorStatus: string/operators/none	
		
		@param errorIndex: error index expected
		@type errorIndex: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_ip = AdapterIP.ip() 		
		layer_udp = AdapterUDP.udp()
		layer_snmp = templates.snmp(version=version, 
																									community=community,
																									agentAddr=agentAddr,
																									enterprise=enterprise,
																									genericTrap=genericTrap,
																									specificTrap=specificTrap,
																									uptime=uptime,
																									requestId=requestId,
																									errorStatus=errorStatus,
																									errorIndex=errorIndex)
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_udp)
		tpl.addLayer(layer=layer_snmp)
		
		return self.received( expected=tpl,  	timeout=timeout)
		