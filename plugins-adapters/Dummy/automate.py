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

__NAME__="""AUTOMATE"""

AGENT_EVENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='myagent'

ACTION_PLAY = "play"
ACTION_PAUSE = "pause"
ACTION_STOP = "stop"
ACTION_POWERON = "power on"
ACTION_POWEROFF = "power off"

STATE_PLAYING         = "playing"
STATE_ON                 = "on"
STATE_STANDBY         = "standby"
STATE_PAUSING        = "pausing"
STATE_OFF                = "off"

import adapter

class Automate(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False, agentSupport=False, agent=None):
		"""
		My adapter

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
		"""
		# check the agent
		if agent is not None:
			if agentSupport:
				if not isinstance(agent, dict) : 
					raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
				if not len(agent['name']): 
					raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
				if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
					raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
				
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name,
																							agentSupport=agentSupport, agent=agent, shared=shared)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		if agent is not None:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = agentSupport

		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		if agent is not None:
			if self.cfg['agent-support']:
				self.prepareAgent(data={'shared': shared})
				if self.agentIsReady(timeout=30) is None: 
					raise TestAdapter.ValueException(TestAdapter.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )

				self.TIMER_ALIVE_AGT.start()
			
		# state and timer initialization
		self.state = TestAdapter.State(parent=self, name='AUTOMATE', initial=STATE_OFF)
		self.TIMER_A = TestAdapter.Timer(parent=self, duration=2, name="TIMER A", callback=self.onTimerA_Fired, 
																										logEvent=True, enabled=True, callbackArgs={})
		self.TIMER_A.start()
		
		self.ADP = adapter.Adapter(parent=parent, debug=debug, name=None, shared=shared)
		
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 

	def onReset(self):
		"""
		Called automatically on reset adapter
		"""
		if self.cfg['agent-support'] :
			# stop timer
			self.TIMER_ALIVE_AGT.stop()
			# cleanup remote agent
			self.resetAgent()

	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['cmd'] == AGENT_EVENT_INITIALIZED:
			tpl = TestTemplates.TemplateMessage()
			layer = TestTemplates.TemplateLayer('AGENT')
			layer.addKey("ready", True)
			tpl.addLayer(layer= layer)
			self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )	

	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.error( 'Error on agent: %s' % data )

	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( 'Data received from agent: %s' % data )

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
		tpl.addLayer(layer= layer)
		evt = self.received( expected = tpl, timeout = timeout )
		return evt
		
	def encapsule(self, cmd):
		"""
		pass
		"""
		tpl = TestTemplates.TemplateMessage()
		layer = TestTemplates.TemplateLayer(name='AUTOMATE')
		layer.addKey(name='cmd', data=cmd)
		tpl.addLayer(layer)
		return tpl
		
	def onTimerA_Fired(self):
		"""
		"""
		self.info("Timer A fired, restart")
		self.onCallback()
		self.TIMER_A.restart()
	
	def onCallback(self):
		"""
		Function to reimplement
		"""
		pass
		
	def setKO(self):
		"""
		"""
		self.testcase().step1.setFailed("Result set to KO")	
		
	def setOK(self):
		"""
		"""
		self.testcase().step1.setPassed("Result set to OK")	
		
	def Play(self):
		"""
		pass
		"""
		# adding event in queue
		self.logSentEvent(shortEvt=ACTION_PLAY, tplEvt=self.encapsule(cmd=ACTION_PLAY) )
			
		if self.state.get() in [ STATE_STANDBY, STATE_ON ]:
			self.state.set(state=STATE_PLAYING)
			
			self.logRecvEvent(shortEvt=STATE_PLAYING, tplEvt=self.encapsule(cmd=STATE_PLAYING) )

	def Stop(self):
		"""
		pass
		"""
		# adding event in queue
		self.logSentEvent(shortEvt=ACTION_STOP, tplEvt=self.encapsule(cmd=ACTION_STOP) )
		
		if self.state.get() in [ STATE_PLAYING, STATE_PAUSING ]:
			self.state.set(state=STATE_STANDBY)
			
			self.logRecvEvent(shortEvt=STATE_STANDBY, tplEvt=self.encapsule(cmd=STATE_STANDBY) )

	def Pause(self):
		"""
		pass
		"""
		# adding event in queue
		self.logSentEvent(shortEvt=ACTION_PAUSE, tplEvt=self.encapsule(cmd=ACTION_PAUSE) )
			
		if self.state.get() in [ STATE_PLAYING ]:
			self.state.set(state=STATE_PAUSING)
			
			self.logRecvEvent(shortEvt=STATE_PAUSING, tplEvt=self.encapsule(cmd=STATE_PAUSING) )
			
	def On(self):
		"""
		pass
		"""
		# adding event in queue
		self.logSentEvent(shortEvt=ACTION_POWERON, tplEvt=self.encapsule(cmd=ACTION_POWERON) )
			
		self.state.set(state=STATE_ON)

	def Off(self):
		"""
		pass
		"""
		# adding event in queue
		self.logSentEvent(shortEvt=ACTION_POWEROFF, tplEvt=self.encapsule(cmd=ACTION_POWEROFF) )
			
		self.state.set(state=STATE_OFF)
		
	def getNbPlaying(self, nb=2, timeout=10):
		"""
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		events = []

		events.append( self.encapsule(cmd=STATE_PLAYING) )
		events.append( self.encapsule(cmd=STATE_PLAYING) )

		return self.received(expected=events, timeout=timeout, AND=True, XOR=False)
		