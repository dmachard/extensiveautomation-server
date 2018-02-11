#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import threading

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import templates

__NAME__="""SMS GATEWAY"""

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='smsgateway'

ACTION_READ_MAILBOX = "READ MAILBOX"
ACTION_SEND_SMS = "SEND SMS"
SMS_SENT = "SMS SENT"
SMS_RECEIVED = "SMS RECEIVED"

RESULT_OK = "OK"

class Gateway(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False, agent=None, 
														agentSupport=False, gwIp='127.0.0.1', gwPort=9090, checkInterval=10):
		"""
		Adapter to receive or send SMS through a gateway

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param gwIp: gateway ip (mobile device)
		@type gwIp: string
		
		@param gwPort: gateway port (mobile device)
		@type gwPort: integer
		
		@param checkInterval: interval to check the mailbox (default=10s)
		@type checkInterval: integer
		"""
		# check agent
		if agentSupport and agent is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent cannot be undefined!" )
			
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapter.ValueException(TestAdapter.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.__mutexActionId__ = threading.RLock()
		self.actionId = 0
		
		self.cfg = {}
		self.cfg['gw-ip']  = gwIp
		self.cfg['gw-port']  = gwPort
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		
		self.timer_mailbox = TestAdapter.Timer(parent=self, duration=checkInterval, name="mailbox timer", 
																													callback=self.checkMailbox, logEvent=False, enabled=True)

		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		self.prepareAgent(data={'shared': shared})
		if self.agentIsReady(timeout=10) is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
#			raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
		self.TIMER_ALIVE_AGT.start()
		
		self.timer_mailbox.start()
		
	def checkMailbox(self):
		"""
		Checking the mailbox
		"""
		data = { 'action': ACTION_READ_MAILBOX }
		self.sendNotifyToAgent(data=data)
		
		# timer restart
		self.timer_mailbox.restart()
		
	def getActionId(self):
		"""
		"""
		self.__mutexActionId__.acquire()
		self.actionId += 1
		ret = self.actionId
		self.__mutexActionId__.release()
		return ret
		
	def encapsule(self, layer_sms):
		"""
		"""
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplates.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_sms)
		return tpl

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
	
	def onReset(self):
		"""
		Called automatically on reset adapter
		"""
		# stop timer
		self.TIMER_ALIVE_AGT.stop()
		
		# cleanup remote agent
		self.resetAgent()
	
		
	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if 'cmd' in data:
			if data['cmd'] == AGENT_INITIALIZED:
				tpl = TestTemplates.TemplateMessage()
				layer = TestTemplates.TemplateLayer('AGENT')
				layer.addKey("ready", True)
				layer.addKey(name='name', data=self.cfg['agent']['name'] )
				layer.addKey(name='type', data=self.cfg['agent']['type'] )	
				tpl.addLayer(layer= layer)
				self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )	
		else:
			if data['action'] == ACTION_SEND_SMS:
				tpl = self.encapsule(layer_sms=templates.sms(action=SMS_SENT, actionId=data['action-id'], result=data['result']))
				self.logRecvEvent( shortEvt = SMS_SENT, tplEvt = tpl )
				
			elif data['action'] == ACTION_READ_MAILBOX:
				timestamp, msg, phone = data['result']
				tpl = self.encapsule(layer_sms=templates.sms(action=SMS_RECEIVED, phone=phone, msg=msg, timestamp="%s" % timestamp))
				self.logRecvEvent( shortEvt = SMS_RECEIVED, tplEvt = tpl )
				
			else:
				self.error("unknown action received:%s" % data['action'] )
				
	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.error(data)
		
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		pass
		
	def sendNotifyToAgent(self, data):
		"""
		Send notify to agent
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
		
	def sendSms(self, phone, msg):
		"""
		Send sms to the phone number passed as argument
		
		@param phone: phone number
		@type phone: string
		
		@param msg: message to send
		@type msg: string
		
		@return: action id
		@rtype: string	
		"""
		actionId = self.getActionId()
		if self.cfg['agent-support'] :
			data = { 
										'gw-ip': self.cfg['gw-ip'], 
										'gw-port': self.cfg['gw-port'],
										'phone': phone,
										'msg': msg,
										'action': ACTION_SEND_SMS, 
										'action-id': actionId 
								}
			self.sendNotifyToAgent(data=data)
			
		# log event
		tpl = self.encapsule(layer_sms=templates.sms(action=ACTION_SEND_SMS, actionId=actionId, phone=phone, msg=msg))
		self.logSentEvent( shortEvt = ACTION_SEND_SMS, tplEvt = tpl )
		
		return actionId
		
	def agentIsReady(self, timeout=1.0):
		"""
		Waits to receive "agent ready" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		tpl = TestTemplates.TemplateMessage()
		layer = TestTemplates.TemplateLayer('AGENT')
		layer.addKey("ready", True)
		layer.addKey(name='name', data=self.cfg['agent']['name'] )
		layer.addKey(name='type', data=self.cfg['agent']['type'] )
		tpl.addLayer(layer= layer)
		evt = self.received( expected = tpl, timeout = timeout )
		return evt
	@doc_public
	def isSmsSent(self, timeout=1.0, actionId=None):
		"""
		Wait to receive "sent sms" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_expected = self.encapsule( layer_sms=templates.sms(action=SMS_SENT, actionId=actionId, result=RESULT_OK))
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedSms(self, timeout=1.0, msg=None, phone=None):
		"""
		Wait to receive "sms" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param msg: expected msg
		@type msg: string/none		
		
		@param phone: expected phone
		@type phone: string/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_expected = self.encapsule( layer_sms=templates.sms(action=SMS_RECEIVED, phone=phone, msg=msg))
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt