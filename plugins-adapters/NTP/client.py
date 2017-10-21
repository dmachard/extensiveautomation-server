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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import codec
import templates
import time

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapter.getVersion()]
AdapterUDP = sys.modules['SutAdapters.%s.UDP' % TestAdapter.getVersion()]

__NAME__="""NTP"""

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False, agentSupport=False, agent=None,
											bindIp = '', bindPort=0):
		"""
		This class enables to send NTP request.

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param agentSupport: agent support (default=False)
		@type agentSupport: boolean
		
		@param agent: agent to use (default=None)
		@type agent: string/none

		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer
		"""
		# check the agent
		if agentSupport and agent is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent cannot be undefined!" )
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapter.ValueException(TestAdapter.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name,
																							agentSupport=agentSupport, agent=agent, shared=shared)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)

		self.ntpCodec = codec.Codec( parent=self)
	
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
			
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	

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
		
	def onReset(self):
		"""
		Called automatically on reset adapter
		"""
		self.stopListening()
		
	def encapsule(self, lower_event, layer_ntp):
		"""
		"""
		# add layer to tpl
		lower_event.addLayer(layer=layer_ntp)
		return lower_event
	
	def onIncomingData(self, data, lower):
		"""
		"""
		# try the packet
		tpl = self.ntpCodec.decode(pkt=data, dest_timestamp=time.time())
		
		# enqueue the message
		lower.addLayer(layer=tpl)
		
		# log event 	
		self.logRecvEvent( shortEvt = "response", tplEvt = lower ) 	
		
	@doc_public
	def queryServer(self, serverIp, serverPort=123, ntpVersion=3, ntpMode=3, leap=0, stratum=0,
								poll=0, precision=0, rootDelay=0, rootDispersion=0, refId=0, refTimestamp=0, origTimestamp=0,
								recvTimestamp=0, txTimestamp=0):
		"""
		Query the ntp server
		
		@param serverIp: ntp server
		@type serverIp: string	
		
		@param serverPort: ntp server port (default=123)
		@type serverPort: integer	
		
		@param ntpVersion: ntp version (default=3)
		@type ntpVersion: integer	
		
		@param ntpMode: ntp mode (default=3)
		@type ntpMode: integer	
		
		@param stratum: stratum (default=0)
		@type stratum: integer	
		
		@param leap: leap (default=0)
		@type leap: integer	
		
		@param poll: poll (default=0)
		@type poll: integer	
		
		@param precision: precision (default=0)
		@type precision: integer	
		
		@param rootDelay: rootDelay (default=0)
		@type rootDelay: integer	
		
		@param rootDispersion: rootDispersion (default=0)
		@type rootDispersion: integer	
		
		@param refId: refId (default=0)
		@type refId: integer	
		
		@param refTimestamp: refTimestamp (default=0)
		@type refTimestamp: integer	
		
		@param origTimestamp: origTimestamp (default=0)
		@type origTimestamp: integer	
		
		@param recvTimestamp: recvTimestamp (default=0)
		@type recvTimestamp: integer	
		
		@param txTimestamp: txTimestamp (default=0)
		@type txTimestamp: integer	
		"""
		if not txTimestamp: 
			txTimestamp = time.time()
		
		pkt, layer_ntp= self.ntpCodec.encode(
																		leap=leap , version=ntpVersion, mode=ntpMode , 
																		stratum=stratum, poll=poll, precision=precision, 
																		root_delay=rootDelay, root_dispersion=rootDispersion, 
																		ref_id=refId,  ref_timestamp=refTimestamp, 
																		orig_timestamp=origTimestamp,  recv_timestamp=recvTimestamp, 
																		tx_timestamp=txTimestamp)
		tpl_udp= self.udp().sendData(data=pkt, to=(serverIp, serverPort) )
		
		self.logSentEvent( shortEvt = "request", tplEvt = self.encapsule(lower_event=tpl_udp, layer_ntp=layer_ntp) ) 	
		
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
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
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
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_UDP.isStopped(timeout=timeout)
		
	@doc_public
	def hasReceivedResponse(self, timeout=1.0, leap=None, version=None, mode=None, stratum=None, poll=None, precision=None,
									rootDelay=None, rootDispersion=None, refId=None, refTimestamp=None,
									origTimestamp=None, recvTimestamp=None, txTimestamp=None, destTimestamp=None,
									offset=None, delay=None, leapMsg=None, modeMsg=None, stratumMsg=None, refIdMsg=None):
		"""
		Waits to receive "ntp response" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param offset: offset (default=None)
		@type offset: integer/none
		
		@param delay: delay (default=None)
		@type delay: integer/none	
		
		@param mode: mode (default=None)
		@type mode: integer/none	
		
		@param modeMsg: mode  tetx (default=None)
		@type modeMsg: string/none	
		
		@param version: version (default=None)
		@type version: integer/none	
		
		@param stratumMsg: stratum  text (default=None)
		@type stratumMsg: string/none	
		
		@param stratum: stratum (default=None)
		@type stratum: integer/none	
		
		@param leap: leap (default=None)
		@type leap: integer	/none
		
		@param leapMsg: leap text (default=None)
		@type leapMsg: string/none	
		
		@param poll: poll (default=None)
		@type poll: integer/none	
		
		@param precision: precision (default=None)
		@type precision: integer/none	
		
		@param rootDelay: rootDelay (default=None)
		@type rootDelay: integer/none	
		
		@param rootDispersion: rootDispersion (default=None)
		@type rootDispersion: integer/none	
		
		@param refId: refId (default=None)
		@type refId: integer/none	
		
		@param refIdMsg: refId text (default=None)
		@type refIdMsg: string	/none
		
		@param refTimestamp: refTimestamp (default=None)
		@type refTimestamp: integer/none	
		
		@param origTimestamp: origTimestamp (default=None)
		@type origTimestamp: integer/none	
		
		@param recvTimestamp: recvTimestamp (default=None)
		@type recvTimestamp: integer/none	
		
		@param txTimestamp: txTimestamp (default=None)
		@type txTimestamp: integer/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_ip = AdapterIP.ip() 		
		layer_udp = AdapterUDP.udp()
		layer_ntp = templates.msg(leap=leap, version=version, mode=mode, stratum=stratum, poll=poll, precision=precision,
									rootDelay=rootDelay, rootDispersion=rootDispersion, refId=refId, refTimestamp=refTimestamp,
									origTimestamp=origTimestamp, recvTimestamp=recvTimestamp, txTimestamp=txTimestamp, destTimestamp=destTimestamp,
									offset=offset, delay=delay, leapMsg=leapMsg, modeMsg=modeMsg, stratumMsg=stratumMsg, refIdMsg=refIdMsg)
		
		tpl = TestTemplates.TemplateMessage()
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_udp)
		tpl.addLayer(layer=layer_ntp)
		
		return self.received( expected=tpl, timeout=timeout)
		