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
from TestExecutorLib.TestExecutorLib import doc_public

import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapter.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapter.getVersion()]
AdapterTelnet = sys.modules['SutAdapters.%s.Telnet' % TestAdapter.getVersion()]

__NAME__="""Catalyst"""

import templates_catalyst
import codec_catalyst

import copy

class Catalyst(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent,  bindIp = '0.0.0.0', bindPort=0,  destIp='127.0.0.1', destPort=23,  name=None, debug=False,
													shared=False, prompt='>', promptEnable='#', agent=None, agentSupport=False):
		"""
		Adapter for catalyst switch cisco. Based on telnet.

		@param parent: parent testcase
		@type parent: testcase

		@param bindIp: bind ip (default=0.0.0.0)
		@type bindIp: string
		
		@param bindPort: bind port (default=0)
		@type bindPort: integer
		
		@param destIp: destination ip (default=127.0.0.1)
		@type destIp: string
		
		@param destPort: destination port (default=23)
		@type destPort: integer
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param prompt: prompt (default=#)
		@type prompt: string
		"""
		if not isinstance(bindPort, int):
			raise TestAdapter.ValueException(TestAdapter.caller(), "bindPort argument is not a integer (%s)" % type(bindPort) )
		if not isinstance(destPort, int):
			raise TestAdapter.ValueException(TestAdapter.caller(), "destPort argument is not a integer (%s)" % type(destPort) )
			
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		
		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			
		self.__checkConfig()

		self.codec = codec_catalyst.Codec(parent=self)
		self.buf = ''
		
		self.prompt = '>'
		self.promptEnable = '#'
		self.ADP_TRANSPORT = AdapterTelnet.Client(parent=parent, bindIp = bindIp, bindPort=bindPort, 
																	destIp=destIp, destPort=destPort,  debug=debug, logEventSent=False, logEventReceived=False,
																	parentName=__NAME__ , agent=agent, agentSupport=agentSupport)
		self.ADP_TRANSPORT.handleIncomingData = self.handleIncomingData		

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
	
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		self.ADP_TRANSPORT.onReset() 
		
	@doc_public
	def connect(self):
		"""
		TCP connection
		uses connect() from telnet library 
		"""
		self.ADP_TRANSPORT.connect()

	@doc_public
	def disconnect(self):
		"""
		TCP connection
		uses connect() from telnet library 
		"""
		self.ADP_TRANSPORT.disconnect()
		
	@doc_public
	def isConnected(self, timeout=1.0):
		"""
		Is Connected

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_TRANSPORT.isConnected(timeout=timeout)
		
	@doc_public
	def isDisconnected(self, timeout=1.0):
		"""
		Is Disconnected

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_TRANSPORT.isDisconnected(timeout=timeout)
		
	def handleIncomingData(self, data, lower):
		"""
		"""
		layer_app = lower.get('TELNET')
		app_data = layer_app.get('data')
		try:
			self.buf += app_data
			decoded_msgs, left = self.codec.decode(data=self.buf)
			self.buf = left
			for d in decoded_msgs:
				summary, tpl_catalyst = d
				new_tpl = self.encapsule(lower_event=copy.deepcopy(lower), layer_catalyst=tpl_catalyst)
				new_tpl.addRaw(app_data)
				self.logRecvEvent( shortEvt = summary, tplEvt = new_tpl ) 
		except Exception as e:
			self.error('Error while waiting on incoming data: %s' % str(e))

	def encapsule(self, lower_event, layer_catalyst):
		"""
		Encapsule
		"""
		# add layer to tpl
		lower_event.addLayer(layer=layer_catalyst)
		return lower_event

	@doc_public
	def sendCommand(self, tpl):
		"""
		Send command
		"""
		try:
			try:
				(summary, encodedMessage) = self.codec.encode(catalyst_cmd=tpl)
			except Exception as e:
				raise Exception("Cannot encode catalyst command: %s" % str(e))	

			# Send request
			try:
				tpl_telnet = AdapterTelnet.dataOutgoing(data='%s\r\n' % encodedMessage)
				lower = self.ADP_TRANSPORT.sendData(tpl=tpl_telnet)
			except Exception as e:
				raise Exception("telnet failed: %s" % str(e))	
		
			tpl.addRaw( encodedMessage )
			lower.addLayer( tpl )
	
			# Log event
			lower.addRaw(raw=encodedMessage)
			self.logSentEvent( shortEvt = summary, tplEvt = lower ) 

		except Exception as e:
			raise Exception('Unable to send catalyst command: %s' % str(e))
		return lower
		
	@doc_public
	def hasReceivedResponse(self, expected, timeout=1.0):
		"""
		Wait response until the end of the timeout.
		
		@param expected: response template
		@type expected: templatemessage

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: response
		@rtype: template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = TestTemplates.TemplateMessage()
		
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		tpl.addLayer(  AdapterTelnet.dataIncoming() )
		tpl.addLayer( expected )
		
		evt = self.received( expected = tpl, timeout = timeout )
		
		return evt
		
	@doc_public
	def hasReceivedData(self, data="", timeout=1.0):
		"""
		Wait response until the end of the timeout.
		
		@param data: data
		@type data: string

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: response
		@rtype: template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_expected= templates_catalyst.catalyst_data(data=data)
		
		tpl = TestTemplates.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		tpl.addLayer(  AdapterTelnet.dataIncoming() )
		tpl.addLayer(  tpl_expected )
		
		evt = self.received( expected = tpl, timeout = timeout )
		
		ret = None
		if evt is not None:
			ret = evt.get('TELNET', 'data')
		return ret
		
	@doc_public
	def hasReceivedUsername(self, timeout=1.0):
		"""
		Wait prompt username until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: response
		@rtype: template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates_catalyst.catalyst_prompt_username()
		return self.hasReceivedResponse( expected=tpl, timeout=timeout)
		
	@doc_public
	def hasReceivedPassword(self, timeout=1.0):
		"""
		Wait prompt password until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: response
		@rtype: template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates_catalyst.catalyst_prompt_password()
		return self.hasReceivedResponse( expected=tpl, timeout=timeout)

	@doc_public
	def hasReceivedPrompt(self, timeout=1.0):
		"""
		Wait general prompt until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: response
		@rtype: template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates_catalyst.catalyst_prompt()
		return self.hasReceivedResponse( expected=tpl , timeout=timeout)

	@doc_public
	def hasReceivedPromptEnable(self, timeout=1.0):
		"""
		Wait prompt enable until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: response
		@rtype: template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates_catalyst.catalyst_prompt_enable()
		return self.hasReceivedResponse( expected=tpl , timeout=timeout)
		
	@doc_public
	def login(self, username, password, timeout=1.0):
		"""
		Login to the catalyst
		
		@param username: telnet username
		@type username: string		
		
		@param password: telnet password
		@type password: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: True on success, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = None
		# username
		if not self.hasReceivedUsername( timeout=timeout ):
			self.error( 'prompt login not detected' ); ret = False
		else:
			tpl = templates_catalyst.catalyst_username(data=username)
			self.sendCommand(tpl=tpl)
			
			# password
			if not self.hasReceivedPassword( timeout=timeout ):
				self.error( 'prompt password not detected' ); ret = False
			else:
				tpl = templates_catalyst.catalyst_password(data=password)
				self.sendCommand(tpl=tpl)

				# prompt
				if not self.hasReceivedPrompt( timeout=timeout ):
					self.error( 'prompt not detected' ); ret = False
				else:
					ret = True
		return ret
	
	@doc_public
	def writeMem(self, timeout=1.0):
		"""
		Write to memory
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: True on success, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret  = None
		tpl = templates_catalyst.catalyst_writemem(data="write mem")
		self.sendCommand(tpl=tpl)

		# prompt
		if not self.hasReceivedPromptEnable( timeout=timeout ):
			self.error( 'prompt enable not detected' ); ret = False
		else:
			ret = True
		return ret
		
	@doc_public
	def enable(self, password, timeout=1.0):
		"""
		Enable session
		
		@param password: password to enable
		@type password: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: True on success, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret  = None
		tpl = templates_catalyst.catalyst_enable(data="enable")
		self.sendCommand(tpl=tpl)
		# password
		if not self.hasReceivedPassword( timeout=timeout ):
			self.error( 'prompt password not detected' ); ret = False
		else:
			tpl = templates_catalyst.catalyst_password(data=password)
			self.sendCommand(tpl=tpl)
				
			# prompt
			if not self.hasReceivedPromptEnable( timeout=timeout ):
				self.error( 'prompt enable not detected' ); ret = False
			else:
				ret = True
		return ret
	
	@doc_public
	def config(self, timeout=1.0):
		"""
		Enter in config mode
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: True on success, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret  = None
		tpl = templates_catalyst.catalyst_config(data="conf t")
		self.sendCommand(tpl=tpl)
		# prompt
		if not self.hasReceivedPromptEnable( timeout=timeout ):
			self.error( 'prompt enable not detected' ); ret = False
		else:
			ret = True
		return ret
	
	@doc_public
	def exit(self, timeout=1.0):
		"""
		Exit mode
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: True on success, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret  = None
		tpl = templates_catalyst.catalyst_exit(data="exit")
		self.sendCommand(tpl=tpl)
		# prompt
		if not self.hasReceivedPromptEnable( timeout=timeout ):
			self.error( 'prompt enable not detected' ); ret = False
		else:
			ret = True
		return ret
		
	@doc_public
	def command(self, cmd, timeout=1.0):
		"""
		Run command
		
		@param cmd: command to run
		@type cmd: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates_catalyst.catalyst_cmd(data=cmd)
		self.sendCommand(tpl=tpl)