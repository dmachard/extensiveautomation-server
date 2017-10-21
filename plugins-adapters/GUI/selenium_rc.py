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
import TestExecutorLib.TestExecutorLib as TestExecutor
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import base64

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import templates
import threading

from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium import webdriver


__NAME__="""Selenium"""

ACTION_SCREENSHOT = "SCREENSHOT"
ACTION_OK = "OK"
ACTION_FAILED = "FAILED"
ACTION_TIMEOUT = "TIMEOUT"

SELENIUM_FIREFOX = DesiredCapabilities.FIREFOX
SELENIUM_INTERNETEXPLORER = DesiredCapabilities.INTERNETEXPLORER
SELENIUM_CHROME = DesiredCapabilities.CHROME
SELENIUM_OPERA = DesiredCapabilities.OPERA
SELENIUM_EDGE= DesiredCapabilities.EDGE

SELENIUM_KEY_NULL         =  Keys.NULL 
SELENIUM_KEY_CANCEL       = Keys.CANCEL 
SELENIUM_KEY_HELP         = Keys.HELP 
SELENIUM_KEY_BACKSPACE    = Keys.BACKSPACE 
SELENIUM_KEY_TAB          = Keys.TAB 
SELENIUM_KEY_CLEAR        = Keys.CLEAR 
SELENIUM_KEY_RETURN       = Keys.RETURN  
SELENIUM_KEY_ENTER        = Keys.ENTER 
SELENIUM_KEY_SHIFT        = Keys.SHIFT 
SELENIUM_KEY_CONTROL      = Keys.CONTROL 
SELENIUM_KEY_ALT          = Keys.ALT 
SELENIUM_KEY_PAUSE        = Keys.PAUSE 
SELENIUM_KEY_ESCAPE       = Keys.ESCAPE 
SELENIUM_KEY_SPACE        = Keys.SPACE  
SELENIUM_KEY_PAGE_UP      = Keys.PAGE_UP 
SELENIUM_KEY_PAGE_DOWN    = Keys.PAGE_DOWN 
SELENIUM_KEY_END          = Keys.END 
SELENIUM_KEY_HOME         = Keys.HOME 
SELENIUM_KEY_LEFT         = Keys.LEFT 
SELENIUM_KEY_UP           = Keys.UP 
SELENIUM_KEY_RIGHT        = Keys.RIGHT 
SELENIUM_KEY_DOWN         = Keys.DOWN  
ISELENIUM_KEY_INSERT       = Keys.INSERT 
SELENIUM_KEY_DELETE       = Keys.DELETE 
SELENIUM_KEY_SEMICOLON    = Keys.SEMICOLON 
SELENIUM_KEY_EQUALS       = Keys.EQUALS  

SELENIUM_KEY_NUMPAD0      = Keys.NUMPAD0 
SELENIUM_KEY_NUMPAD1      = Keys.NUMPAD1 
SELENIUM_KEY_NUMPAD2      = Keys.NUMPAD2 
SELENIUM_KEY_NUMPAD3      = Keys.NUMPAD3 
SELENIUM_KEY_NUMPAD4      = Keys.NUMPAD4 
SELENIUM_KEY_NUMPAD5      = Keys.NUMPAD5 
SELENIUM_KEY_NUMPAD6      = Keys.NUMPAD6 
SELENIUM_KEY_NUMPAD7      = Keys.NUMPAD7 
SELENIUM_KEY_NUMPAD8      = Keys.NUMPAD8 
SELENIUM_KEY_NUMPAD9      = Keys.NUMPAD9 

SELENIUM_KEY_MULTIPLY     = Keys.MULTIPLY 
SELENIUM_KEY_ADD          = Keys.ADD  
SELENIUM_KEY_SEPARATOR    = Keys.SEPARATOR 
SELENIUM_KEY_SUBTRACT     = Keys.SUBTRACT 
SELENIUM_KEY_DECIMAL      = Keys.DECIMAL 
SELENIUM_KEY_DIVIDE       = Keys.DIVIDE 

SELENIUM_KEY_F1           =  Keys.F1 
SELENIUM_KEY_F2           = Keys.F2 
SELENIUM_KEY_F3           = Keys.F3 
SELENIUM_KEY_F4           = Keys.F4 
SELENIUM_KEY_F5           = Keys.F5 
SELENIUM_KEY_F6           = Keys.F6 
SELENIUM_KEY_F7           = Keys.F7 
SELENIUM_KEY_F8           = Keys.F8 
SELENIUM_KEY_F9           = Keys.F9 
SELENIUM_KEY_F10          = Keys.F10 
SELENIUM_KEY_F11          = Keys.F11 
SELENIUM_KEY_F12          = Keys.F12 

SELENIUM_KEY_META         = Keys.META 
SELENIUM_KEY_COMMAND      = Keys.COMMAND 

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='seleniumserver'

class NotReady(Exception): pass

class Selenium(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, agent, name=None, debug=False, verbose=True, shared=False, navigId=None, waitUntil=True):
		"""
		Selenium adapter

		@param parent: parent testcase
		@type parent: testcase

		@param agent: agent to use, selenium type expected
		@type agent: string
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param navigId: navigator id (default=None)
		@type navigId: string/none

		@param waitUntil: use the wait until mode (default=True)
		@type waitUntil:	boolean
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# check the agent
		if not isinstance(agent, dict) : 
			raise TestAdapter.ValueException(TestAdapter.caller(), "agent argument is not a dict (%s)" % type(agent) )
		if not len(agent['name']): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "agent name cannot be empty" )
		if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
			raise TestAdapter.ValueException(TestAdapter.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared,
																									showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)

		self.cfg = {}
		self.cfg['agent-support'] = True
		self.cfg['agent'] = agent
		self.cfg['agent-name'] = agent['name']
		
		self.cfg['wait-until'] = waitUntil
		
		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		self.cmdId = 0
		self.isStarted = False
		self.__mutexCmdId__ = threading.RLock()
		
		self.capabilities = {}
		self.navigId = navigId
		self.errorHandler = ErrorHandler()

		# load navig id from storage
		self.sessionName = None
		self.navigId = TestExecutor.Cache().get(name="%s-navig-id-default" % AGENT_TYPE_EXPECTED )

		# initialize the agent with no data
		self.prepareAgent(data={'shared': shared})
		if self.agentIsReady(timeout=30) is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )	
		self.TIMER_ALIVE_AGT.start()

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
		self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
	
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		# stop timer
		self.TIMER_ALIVE_AGT.stop()
		
		# cleanup remote agent
		self.resetAgent()

	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( "response: %s" % data)
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
			try:
				commandId = data['command-id']
				commandName = data['command-name']
				commandValue =  data['command-value']

				response = self.parseResponse(commandValue)
				responseResult = ACTION_FAILED
				responseState = None

				layerValue = TestTemplates.TemplateLayer(name='')
				if 'state' in response:
					layerValue.addKey(name='state', data="%s" % response ['state'] )

				if 'status' in response:
					if response['status'] == 0: responseResult = ACTION_OK
					
					# timeout
					if response['status'] == 1000: 
						responseResult = ACTION_TIMEOUT
						tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																					state=responseState) )
						self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
						return
						
					# error
					if response['status'] != 0: 
						layerValue.addKey(name='value', data="%s" % response['value'] )
						tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																					state=responseState) )
						tpl.addRaw("%s" % response['value'])
						self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
						return
						
				if response['value'] is not None:
					if isinstance(response["value"], dict):
						if 'state' in response['value']:
							responseState = response['value']['state']

				if commandName == Command.NEW_SESSION:
					if 'sessionId' not in response:
						self.error("error on selenium agent: %s" %  response['value'])
					else:
						# save the session id in the cache
						self.navigId = response['sessionId']
						TestExecutor.Cache().set(name="%s-navig-id-%s" % (AGENT_TYPE_EXPECTED, self.sessionName ),  data=self.navigId)

						self.capabilities = response['value']
						self.debug("capabilities: %s" % self.capabilities)
						if 'platform' not in self.capabilities:
							self.error("Platform missing on response, please to configure browser properly!")
						else:	
							version = ""
							if "version" in self.capabilities:
								version = self.capabilities['version']

							self.isStarted = True
							
							layerValue.addKey(name='navig-id', data="%s" % self.navigId )
							
							capsTpl= TestTemplates.TemplateLayer(name='')
							capsTpl.addMore(self.capabilities)
							layerValue.addKey(name='capabilities', data=capsTpl )
							
							tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																						state=responseState) )
							self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
						
				elif commandName == Command.SCREENSHOT:
					screenshot = base64.b64decode(response['value'].encode('ascii'))
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult , img=screenshot,
																																				state=responseState) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
					
				elif commandName == Command.GET_ELEMENT_SIZE:
					if 'height' in response['value']:
						layerValue.addKey(name='height', data=response['value'] ['height'] )
					if 'width' in response['value']:
						layerValue.addKey(name='width', data=response['value'] ['width'] )
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																			state=responseState	) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
					
				elif commandName == Command.GET_ELEMENT_LOCATION:
					if 'x' in response['value']:
						layerValue.addKey(name='x', data=response['value'] ['x'] )
					if 'y' in response['value']:
						layerValue.addKey(name='y', data=response['value'] ['y'] )
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																					state=responseState	) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
					
				elif commandName == Command.FIND_ELEMENT:
	
					if 'ELEMENT' in response['value']:
						layerValue.addKey(name='element-id', data=response['value'] ['ELEMENT'] )
					
					if 'screen' in response['value']:
						screenshot = base64.b64decode(response['value'] ['screen'].encode('ascii'))
						layerValue.addKey(name='screenshot', data=screenshot)

					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																	state=responseState	) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
						
				elif commandName == Command.QUIT:
					self.isStarted = False
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, state=responseState  ) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
				elif commandName == Command.GET_ELEMENT_TEXT:
					layerValue.addKey(name='value', data= response['value'].encode('utf8') )
					
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																			state=responseState) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
				elif commandName == Command.GET_WINDOW_HANDLES:
					layerHandles = TestTemplates.TemplateLayer(name='')
					for i in xrange(len(response ['value'] )):
						layerHandles.addKey(name='%s' % i, data="%s" % response ['value'] [i])
					layerValue.addKey(name='handles', data=layerHandles)
					
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																					state=responseState) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
				else:
					layerValue.addKey(name='value', data="%s" % response['value'] )
					
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=responseResult, value=layerValue,
																																				state=responseState) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, responseResult), tplEvt = tpl )
				
			except Exception as e:
				self.error('received notify: %s' % e)
	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( data )
		self.error( data )
		
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( 'data received from agent' )

		# log event
		tpl = self.encapsule( 
													layer_gui=templates.gui(
																			action=data['command-name'], 
																			actionId=data['command-id'],
																			description=ACTION_SCREENSHOT,
																			length=str(len(data['data'])),
																			img=data['data']
																		)
												)
		tpl.addRaw( data['data'] )
		self.logRecvEvent( shortEvt = ACTION_SCREENSHOT, tplEvt = tpl )
		
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
		
	
	def getCommandId(self):
		"""
		"""
		self.__mutexCmdId__.acquire()
		self.cmdId += 1
		ret = self.cmdId
		self.__mutexCmdId__.release()
		return ret
		
	def encapsule(self, layer_gui):
		"""
		Encapsule layer in template message
		"""
		layer_agent= TestTemplates.TemplateLayer('AGENT')
		layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
		layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_gui)
		return tpl
		
	def parseResponse(self, response):
		"""
		Parse response
		"""
		if response: return response
		return {'success': 0, 'value': None, 'sessionId': self.navigId}

	def _wrap_value(self, value):
		"""
		Wrap value
		"""
		if isinstance(value, dict):
			converted = {}
			for key, val in value.items():
				converted[key] = self._wrap_value(val)
			return converted
		elif isinstance(value, WebElement):
			return {'ELEMENT': value.id}
		elif isinstance(value, list):
			return list(self._wrap_value(item) for item in value)
		else:
			return value

	def create_web_element(self, element_id):
		"""
		Creates a web element with the specified element_id.
		"""
		return WebElement(self, element_id)

	def _unwrap_value(self, value):
		"""
		Unwrap value
		"""
		if isinstance(value, dict) and 'ELEMENT' in value:
			return self.create_web_element(value['ELEMENT'])
		elif isinstance(value, list):
			return list(self._unwrap_value(item) for item in value)
		else:
			return value

	def prepareParams(self,  params=None):
		"""
		Prepare parameters
		"""
		if self.navigId is not None:
			if not params:
				params = {'sessionId': self.navigId}
			elif 'sessionId' not in params:
				params['sessionId'] = self.navigId
		params = self._wrap_value(params)
		return params

	def executeCommand(self, command, params=None, more={}):
		"""
		"""
		if command != Command.NEW_SESSION and self.navigId is None:
			#raise NotReady("No nagivation id defined!")
			raise TestAdapter.AdapterException(TestAdapter.caller(), "No nagivation id defined!" )
			
		# prepare agent request
		cmdId = self.getCommandId()
		agentData = { 'command-id': cmdId, 'command-name':  command }
		agentData['command-params'] = self.prepareParams(params=params)
		agentData['command-capabilities'] = self.capabilities

		# add additionnal keys
		agentData.update(more)
		
		# send command to agent
		self.debug( "request: %s" % agentData)
		self.sendNotifyToAgent(data=agentData)

		# log event
		layerParams = TestTemplates.TemplateLayer(name='')
		for k,v in agentData['command-params'].items():
			layerParams.addKey("%s" % k, "%s" % v)
		
		tpl = self.encapsule(layer_gui=templates.gui(action=command, actionId=cmdId, parameters=layerParams))
		self.logSentEvent( shortEvt = command, tplEvt = tpl )
		
		return cmdId
		
	def setNavigId(self, navigId):
		"""
		Set navigation Id manually
		
		@param navigId: navagator id
		@type navigId: string
		"""
		self.navigId = navigId

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
	# do functions
	@doc_public
	def doSwitchToSession(self, sessionName):
		"""
		Switch to the session according to the name provided
		
		@param sessionName: session name
		@type sessionName: string
		"""
		self.navigId = TestExecutor.Cache().get(name="%s-navig-id-%s" % (AGENT_TYPE_EXPECTED, sessionName) )
		if self.navigId is None:
			raise Exception("the session (%s) does not exists!" % sessionName )
		return True
		
	@doc_public
	def doOpen(self, targetUrl, timeout=30.0, withFirefox=True, withIe=False, withChrome=False, withOpera=False, withEdge=False, useMarionette=True,
												browserProfile=None, sessionName="default" ):
		"""
		Open firefox and load url passed as argument

		@param targetUrl: url to load
		@type targetUrl: string
		
		@param timeout: time max to wait to open the browser and load url in second (default=30s)
		@type timeout: float		

		@param withFirefox: open firefox (default=True)
		@type withFirefox: boolean

		@param withIe: open internet explorer (default=False)
		@type withIe: boolean

		@param withChrome: open chrome (default=False)
		@type withChrome: boolean

		@param withOpera: open opera (default=False)
		@type withOpera: boolean

		@param withEdge: open edge (default=False)
		@type withEdge: boolean

		@param useMarionette: use marionette for gecko support (default=True)
		@type useMarionette: boolean

		@param browserProfile: browser profile (default=None)
		@type browserProfile: none/object

		@param sessionName: session name (default=default)
		@type sessionName: string
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		if withFirefox:
			cap = SELENIUM_FIREFOX
			cap['marionette'] = useMarionette
			cap['acceptInsecureCerts'] = True
		elif withIe:
			cap = SELENIUM_INTERNETEXPLORER
		elif withChrome:
			cap = SELENIUM_CHROME
		elif withOpera:
			cap = SELENIUM_OPERA
		elif withEdge:
			cap = SELENIUM_EDGE
		else:
			cap = SELENIUM_FIREFOX
		cmdId = self.openNavig( desiredCapabilities=cap, browserProfile=browserProfile, sessionName=sessionName)	
		if self.isNavigStarted(timeout=timeout, commandId=cmdId) is None:
			ret = False
		else:
			if not( targetUrl.startswith("http://") or targetUrl.startswith("https://")  ):
				raise TestAdapter.ValueException(TestAdapter.caller(), "target url not start with http(s):// (%s)" % type(targetUrl) )
			cmdId = self.loadUrl(url=targetUrl)
			if self.isUrlLoaded(timeout=timeout, commandId=cmdId) is None:
				ret = False
		return ret
	@doc_public
	def doClose(self, timeout=30.0):
		"""
		Close the browser

		@param timeout: time max to wait to close window in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.quitNavig()
		if self.isNavigStopped(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doCloseWindow(self, timeout=30.0):
		"""
		Close the current window

		@param timeout: time max to wait to close window in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.closeWindow()
		if self.isWindowClosed(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doSwitchToWindow(self, windowName, timeout=30.0):
		"""
		Switch to the provided window

		@param windowName: windows name
		@type windowName: string		
		
		@param timeout: time max to wait to close window in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		ret = True
		
		cmdId = self.getAllWindowHandles()
		rsp = self.hasWindowHandles(timeout=timeout, commandId=cmdId)
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			listHandles =  elementVall.get('handles').getItems()
		
			matched = False
			for (i,h) in listHandles:
				cmdId = self.switchToWindow(	windowName=h )
				rsp = self.isWindowsSwitched(timeout=timeout, commandId=cmdId)
				if rsp is None: 	ret = False; break;

				cmdId = self.getTitle( )
				rsp = self.hasWindowTitle(timeout=timeout, commandId=cmdId)
				if rsp is None: ret = False; break;
				elementVall = rsp.get('GUI',  'value')
				title = elementVall.get('value')
				
				while not len(title):
					time.sleep(0.5)
					cmdId = self.getTitle( )
					rsp = self.hasWindowTitle(timeout=timeout, commandId=cmdId)
					if rsp is None: ret = False; break;
					elementVall = rsp.get('GUI',  'value')
					title = elementVall.get('value')
					
				if windowName in title: 
					matched = True
					break
					
			if not matched:
				ret = False
					
		return ret
	@doc_public
	def doGetPageTitle(self, timeout=10.0):
		"""
		Return the title of the current page

		@param timeout: time max to wait to get page title in second (default=10s)
		@type timeout: float		
		
		@return: False on action KO, the text otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getTitle()
		rsp = self.hasWindowTitle(timeout=timeout, commandId=cmdId)
		if rsp is None:
			ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			ret = elementVall.get('value') # title of the window
		return ret
	@doc_public
	def doFindTextPageTitle(self, expectedText, timeout=10.0):
		"""
		Find the text provided as argument in the title of the current page

		@param expectedText: text to find
		@type expectedText: string/operators
		
		@param timeout: time max to wait to get page title in second (default=10s)
		@type timeout: float		
		
		@return: True if text found, False otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getTitle()
		rsp = self.hasWindowTitle(timeout=timeout, commandId=cmdId, expectedText=expectedText)
		if rsp is None:
			ret = False
		return ret
	@doc_public
	def doGetPageUrl(self, timeout=10.0):
		"""
		Return the url of the current page

		@param timeout: time max to wait to get page url in second (default=10s)
		@type timeout: float	
		
		@return: False on action KO, the text otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getUrl()
		rsp = self.hasUrl(timeout=timeout, commandId=cmdId)
		if rsp is None:
			ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			ret = elementVall.get('value') # url of the window
		return ret
	@doc_public
	def doFindTextPageUrl(self, expectedText, timeout=10.0):
		"""
		Find the text provided as argument in the url of the current page
		
		@param expectedText: text to find
		@type expectedText: string/operators
		
		@param timeout: time max to wait to get page url in second (default=10s)
		@type timeout: float	
		
		@return: True if text found, False otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getUrl()
		rsp = self.hasUrl(timeout=timeout, commandId=cmdId, expectedText=expectedText)
		if rsp is None:
			ret = False
		return True
	@doc_public
	def doGetPageSource(self, timeout=10.0):
		"""
		Return the code source of the current page
		
		@param timeout: time max to wait to get source code in second (default=10s)
		@type timeout: float		
		
		@return: False on action KO, the text otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getPageSource()
		rsp = self.hasSource(timeout=timeout, commandId=cmdId)
		if rsp is None:
			ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			ret = elementVall.get('value') # code source of the window
		return ret
	@doc_public
	def doFindTextPageSource(self, expectedText, timeout=10.0):
		"""
		Find the text provided as argument in the code source of the current page
		
		@param expectedText: text to find
		@type expectedText: string/operators
		
		@param timeout: time max to wait to get source code in second (default=10s)
		@type timeout: float		
		
		@return: True if text found, False otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getPageSource()
		rsp = self.hasSource(timeout=timeout, commandId=cmdId, expectedText=expectedText)
		if rsp is None:
			ret = False
		return True
	@doc_public
	def doWaitElement(self,  timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Wait element until the end of the timeout
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait element in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		ret = True
		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout}

		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret

		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																				id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, cssSelector=cssSelector,
																				location=location,  more=more)
		rsp = self.hasElement(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: ret = False	
		return ret
	@doc_public
	def doWaitVisibleElement(self,  timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Wait element to be visible until the end of the timeout
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait element in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		ret = True
		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout}

		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret

		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																				id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, cssSelector=cssSelector,
																				location=location, more=more)
		rsp = self.hasElement(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False	
			return ret
		elementVall = rsp.get('GUI',  'value')
		elementId = elementVall.get('element-id')

		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout, "wait-until-value": True}

		cmdId = self.displayedElement(elementId=elementId, more= more)
		rsp = self.isElementDisplayed(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False	
		return ret
	@doc_public
	def doWaitNotVisibleElement(self,  timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Wait element to be not visible until the end of the timeout
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait element in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		ret = True
		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout}

		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret

		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																				id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, cssSelector=cssSelector, 
																				location=location, more=more)
		rsp = self.hasElement(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False	
			return ret
		elementVall = rsp.get('GUI',  'value')
		elementId = elementVall.get('element-id')

		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout, "wait-until-value": False}

		cmdId = self.displayedElement(elementId=elementId, more= more)
		rsp = self.isElementDisplayed(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False	
		return ret
	@doc_public
	def doWaitClickElement(self,  timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Wait element until the end of the timeout and click on it
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait element in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout}
			
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret

		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																				id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, cssSelector=cssSelector,
																				location=location, more=more)
		rsp = self.hasElement(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False
			return ret
	
		elementVall = rsp.get('GUI',  'value')
		elementId = elementVall.get('element-id')
	
		cmdId = self.clickElement(elementId=elementId)
		if self.isElementClicked(timeout=timeout, commandId=cmdId)  is None:
			ret = False
		return ret
	@doc_public
	def doWaitVisibleClickElement(self,  timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Wait element to be visible until the end of the timeout and click on it
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait element in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout}
			
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret

		# locate the element
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																				id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, cssSelector=cssSelector,
																				location=location, more=more)
		rsp = self.hasElement(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False
			return ret
	
		elementVall = rsp.get('GUI',  'value')
		elementId = elementVall.get('element-id')
		
		# checking if visible
		more = {}
		if self.cfg['wait-until']:
			more = {"wait-until": True, "wait-until-timeout": timeout, "wait-until-value": True}
		cmdId = self.displayedElement(elementId=elementId, more= more)
		rsp = self.isElementDisplayed(timeout=timeout+10, commandId=cmdId) 
		if rsp is None: 
			ret = False	
			return ret
			
		# finally click on it
		cmdId = self.clickElement(elementId=elementId)
		if self.isElementClicked(timeout=timeout, commandId=cmdId)  is None:
			ret = False
		return ret
	@doc_public
	def doGetText(self, timeout=10.0, name=None, tagName=None, className=None,
																id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																location=None):
		"""
		Get the text of the element

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to get the text of the element in second (default=10s)
		@type timeout: float		
		
		@return: False on action KO, the text otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
		
			cmdId = self.getTextElement(elementId=elementId)
			rsp = self.hasTextElement(timeout=timeout, commandId=cmdId)
			if  rsp is None: 	ret = False
			else:
				elementVall = rsp.get('GUI',  'value')
				ret = elementVall.get('value')
				
		return ret
	@doc_public
	def doFindText(self, expectedText, timeout=10.0, name=None, tagName=None, className=None,
																id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																location=None):
		"""
		Find the text provided as argument in the element

		@param expectedText: text to find
		@type expectedText: string/operators

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to get the text of the element in second (default=10s)
		@type timeout: float		
		
		@return: False on action KO, the text otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if expectedText is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "expectedText argument cannot be equal to none" )

		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText,
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
		
			cmdId = self.getTextElement(elementId=elementId)
			rsp = self.hasTextElement(timeout=timeout, commandId=cmdId, expectedText=expectedText)
			if rsp is None:
				ret = False
			return True
		return ret
		
	@doc_public
	def doClickElement(self, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, 
																				cssSelector=None, location=None):
		"""
		Click on element

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to click on element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.clickElement(elementId=elementId)
			if self.isElementClicked(timeout=timeout, commandId=cmdId)  is None:
				ret = False
		return ret
	@doc_public
	def doDoubleClickElement(self, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, 
																				cssSelector=None, location=None):
		"""
		Double Click on element

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to click on element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.hoverElement(elementId=elementId)
			if self.hasMouseMoved(timeout=timeout, commandId=cmdId)  is None:
				ret = False
			else:
				cmdId = self.doubleClick()
				if self.isDoubleClicked(timeout=timeout, commandId=cmdId)  is None:
					ret = False

		return ret
	@doc_public
	def doRightClickElement(self, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, 
																				cssSelector=None, location=None):
		"""
		Right Click on element

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to click on element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.hoverElement(elementId=elementId)
			if self.hasMouseMoved(timeout=timeout, commandId=cmdId)  is None:
				ret = False
			else:
				cmdId = self.rightClick()
				if self.isClicked(timeout=timeout, commandId=cmdId)  is None:
					ret = False

		return ret
	@doc_public
	def doHoverElement(self, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Hover mouse on element

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to hover on element in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.hoverElement(elementId=elementId)
			if self.hasMouseMoved(timeout=timeout, commandId=cmdId)  is None:
				ret = False
				
		return ret
		
	@doc_public
	def doTypeText(self, text, timeout=10.0, name=None, tagName=None, className=None,
																	id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																	location=None):
		"""
		Find element and type text on it

		@param text: text to type
		@type text: string

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to type text in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if text is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "text argument cannot be equal to none" )

		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.typeTextElement(elementId=elementId, text=str(text) )
			if self.hasTextEntered(timeout=timeout, commandId=cmdId)  is None:
				ret = False
		return ret
	@doc_public
	def doCheckLocationElement(self, x, y, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Check the location of the element

		@param x: x position
		@type x: integer
		
		@param y: y position
		@type y: integer

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to type text in second (default=10s)
		@type timeout: float		
		
		@return: True if the size if OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if x is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "x argument cannot be equal to none")
		if y is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "y argument cannot be equal to none" )

		ret = False
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.locationElement(elementId=elementId)
			rsp2 = self.isElementLocation(timeout=timeout, commandId=cmdId)  
			if rsp2 is None: 	ret = False
			else:
				elementVall = rsp2.get('GUI',  'value')
				elementX = elementVall.get('x')
				elementY = elementVall.get('y')
				
				if int(x) == int(elementX) and int(y) == int(elementY):
					ret = True
		return ret
	@doc_public
	def doCheckSizeElement(self, width, height, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None):
		"""
		Check the size of the element

		@param width: width element
		@type width: integer
		
		@param height: heigth element
		@type height: integer

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to type text in second (default=10s)
		@type timeout: float		
		
		@return: True if the size if OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if width is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "width argument cannot be equal to none" )
		if height is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "height argument cannot be equal to none" )
		
		ret = False
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.sizeElement(elementId=elementId)
			rsp2 = self.isElementSize(timeout=timeout, commandId=cmdId)  
			if rsp2 is None: 	ret = False
			else:
				elementVall = rsp2.get('GUI',  'value')
				elementWidth = elementVall.get('width')
				elementHeight = elementVall.get('height')
				
				if int(width) == int(elementWidth) and int(height) == int(elementHeight):
					ret = True
		return ret

	@doc_public
	def doTypeKey(self, key, timeout=10.0, name=None, tagName=None, className=None,
														id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None, 
														location=None, repeat=0):
		"""
		Find element and type a  key on it

		@param key: SutAdapters.GUI.SELENIUM_KEY_NULL | SutAdapters.GUI.SELENIUM_KEY_CANCEL | SutAdapters.GUI.SELENIUM_KEY_HELP | SutAdapters.GUI.SELENIUM_KEY_BACKSPACE | SutAdapters.GUI.SELENIUM_KEY_TAB | SutAdapters.GUI.SELENIUM_KEY_CLEAR | SutAdapters.GUI.SELENIUM_KEY_RETURN | SutAdapters.GUI.SELENIUM_KEY_ENTER | SutAdapters.GUI.SELENIUM_KEY_SHIFT | SutAdapters.GUI.SELENIUM_KEY_CONTROL | SutAdapters.GUI.SELENIUM_KEY_ALT | SutAdapters.GUI.SELENIUM_KEY_PAUSE | SutAdapters.GUI.SELENIUM_KEY_ESCAPE | SutAdapters.GUI.SELENIUM_KEY_SPACE | SutAdapters.GUI.SELENIUM_KEY_PAGE_UP | SutAdapters.GUI.SELENIUM_KEY_PAGE_DOWN | SutAdapters.GUI.SELENIUM_KEY_END | SutAdapters.GUI.SELENIUM_KEY_HOME | SutAdapters.GUI.SELENIUM_KEY_LEFT | SutAdapters.GUI.SELENIUM_KEY_UP | SutAdapters.GUI.SELENIUM_KEY_RIGHT | SutAdapters.GUI.SELENIUM_KEY_DOWN | SutAdapters.GUI.SELENIUM_KEY_INSERT | SutAdapters.GUI.SELENIUM_KEY_DELETE | SutAdapters.GUI.SELENIUM_KEY_SEMICOLON | SutAdapters.GUI.SELENIUM_KEY_EQUALS | SutAdapters.GUI.SELENIUM_KEY_NUMPAD0 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD1 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD2 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD3 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD4 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD5 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD6 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD7 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD8 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD9 | SutAdapters.GUI.SELENIUM_KEY_MULTIPLY | SutAdapters.GUI.SELENIUM_KEY_ADD | SutAdapters.GUI.SELENIUM_KEY_SEPARATOR | SutAdapters.GUI.SELENIUM_KEY_SUBTRACT | SutAdapters.GUI.SELENIUM_KEY_DECIMAL | SutAdapters.GUI.SELENIUM_KEY_DIVIDE | SutAdapters.GUI.SELENIUM_KEY_F1 | SutAdapters.GUI.SELENIUM_KEY_F2 | SutAdapters.GUI.SELENIUM_KEY_F3 | SutAdapters.GUI.SELENIUM_KEY_F4 | SutAdapters.GUI.SELENIUM_KEY_F5 | SutAdapters.GUI.SELENIUM_KEY_F6 | SutAdapters.GUI.SELENIUM_KEY_F7 | SutAdapters.GUI.SELENIUM_KEY_F8 | SutAdapters.GUI.SELENIUM_KEY_F9 | SutAdapters.GUI.SELENIUM_KEY_F10 | SutAdapters.GUI.SELENIUM_KEY_F11 | SutAdapters.GUI.SELENIUM_KEY_F12 | SutAdapters.GUI.SELENIUM_KEY_META | SutAdapters.GUI.SELENIUM_KEY_COMMAND
		@type key: strconstant

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to type key in second (default=10s)
		@type timeout: float		
		
		@param repeat: number to key to type (default=0)
		@type repeat: integer	
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			for r in xrange(repeat + 1):
				cmdId = self.typeKeyElement(elementId=elementId, key=key)
				if self.hasTextEntered(timeout=timeout, commandId=cmdId)  is None:
					ret = False
		return ret
	@doc_public
	def doMaximizeWindow(self, timeout=10.0, windowHandle='current'):
		"""
		Do maximize window
		
		@param timeout: time max to wait to maxime window in second (default=10s)
		@type timeout: float		

		@param windowHandle: window handle (default=current)
		@type windowHandle: string
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.maximizeWindow( windowHandle=windowHandle)
		if self.isMaximized(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doRefreshPage(self, timeout=10.0):
		"""
		Do refresh page
		
		@param timeout: time max to wait to refresh page in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.refreshPage()
		if self.isRefreshed(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doGoBack(self, timeout=10.0):
		"""
		Do go back
		
		@param timeout: time max to wait to go back in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.navigBack()
		if self.isGoBack(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doGoForward(self, timeout=10.0):
		"""
		Do go forward
		
		@param timeout: time max to wait to go forward in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.navigForward()
		if self.isGoForward(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doDismissAlert(self, timeout=10.0):
		"""
		Do dismiss alert
		
		@param timeout: time max to wait to dismiss alert in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.dismissAlert()
		if self.isAlertDismissed(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doAcceptAlert(self, timeout=10.0):
		"""
		Do accept alert
		
		@param timeout: time max to wait to accept alert in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.acceptAlert()
		if self.isAlertAccepted(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doGetTextAlert(self, timeout=10.0):
		"""
		Do get text alert
		
		@param timeout: time max to wait to get text alert in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getTextAlert()
		rsp = self.hasTextAlert(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			ret = elementVall.get('value')
		return ret
	@doc_public
	def doAuthenticateAlert(self, username, password, timeout=10.0):
		"""
		Do authenticate alert (basic http for example)
		
		@param username: username
		@type username: string
		
		@param password: password
		@type password: string
		
		@param timeout: time max to wait to authenticate alert in second (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.authenticateDialog(username=username, password=password)
		if self.isAlertAuthenticated(timeout=timeout, commandId=cmdId) is None:
			ret = False
		return ret
	@doc_public
	def doSwitchToFrame(self, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None,
																				location=None, timeout=10.0):
		"""
		Do switch to frame 
		Example by css selector: iframe[src='tab.jsp']
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to switch to element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.switchToFrame(reference={'ELEMENT': str(elementId) })
			if self.isFrameSwitched(timeout=timeout, commandId=cmdId)  is None:
				ret = False
		return ret
		
	@doc_public
	def doSwitchToNextWindow(self, timeout=10.0):
		"""
		Do switch to the next windows
		
		@param timeout: time max to wait to switch to element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.getCurrentWindowHandle()
		rsp = self.hasWindowHandle(timeout=timeout, commandId=cmdId)
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			currentHandle = elementVall.get('value')
			
			cmdId = self.getAllWindowHandles()
			rsp = self.hasWindowHandles(timeout=timeout, commandId=cmdId)
			if rsp is None: ret = False
			else:
				elementVall = rsp.get('GUI',  'value')
				listHandles =  elementVall.get('handles').getItems()
				
				z = 0
				for h in sorted(listHandles):
					if h == currentHandle: 
						break
					z += 1
				
				z += 1
				nextHandle = listHandles[z]

				cmdId = self.switchToWindow(	windowName=nextHandle )
				rsp = self.isWindowsSwitched(timeout=timeout, commandId=cmdId)
				if rsp is None: ret = False
				
		return ret
		
	@doc_public
	def doClearTextElement(self, timeout=10.0, name=None, tagName=None, className=None,
																				id=None, xpath=None, linkText=None,  partialLinkText=None, cssSelector=None, location=None):
		"""
		Do clear the text if it's a text entry element.

		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to get the text of the element in second (default=10s)
		@type timeout: float		
		
		@return: False on action KO, the text otherwise
		@rtype: string	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(elementId=None, name=name, tagName=tagName, className=className,
																					id=id, xpath=xpath, linkText=linkText,  partialLinkText=partialLinkText, 
																					cssSelector=cssSelector, location=location)
		rsp = self.hasElement(timeout=timeout, commandId=cmdId) 
		if rsp is None: ret = False
		else:
			elementVall = rsp.get('GUI',  'value')
			elementId = elementVall.get('element-id')
			
			cmdId = self.clearTextElement(elementId=elementId)
			if self.isElementCleared(timeout=timeout, commandId=cmdId)  is None:
				ret = False
		return ret
		
	@doc_public
	def doSelectByValue(self, text, timeout=10.0, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None,  
																		partialLinkText=None, cssSelector=None, location=None):
		"""
		Select item in a list/combo by the value attribute
		
		@param text: text expected for the value
		@type text: string
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to switch to element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(name=name, tagName=tagName, className=className, id=id,  xpath=xpath, linkText=linkText, 
																							partialLinkText=partialLinkText, cssSelector=cssSelector, location=location)
		selectElement = self.hasElement(timeout=timeout, commandId=cmdId) 
		if selectElement is  None:
			ret = False
		else:
			selectValue= selectElement.get('GUI',  'value')
			selectId = selectValue.get('element-id')
			
			css = "option[value =%s]" % self._escapeString(text)
			cmdId = self.findChildElements(elementId=selectId, cssSelector=css)
			optionsSelect = self.hasChildElements(timeout=timeout, commandId=cmdId) 
			if optionsSelect is None:
				ret = False
			else:
				optionsValue = optionsSelect.get('GUI',  'value')
				optionsIds = eval( optionsValue.get('value') )
				
				if not len(optionsIds): 
					ret = False
				else:
					for opId in optionsIds:
						cmdId = self.clickElement(elementId=opId['ELEMENT'])
						elementClicked = self.isElementClicked(timeout=timeout, commandId=cmdId) 
						if elementClicked is None:
							ret = False
						else:
							ret = True
		return ret
	@doc_public
	def doSelectByText(self, text, timeout=10.0, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None,  
																		partialLinkText=None, cssSelector=None, location=None):
		"""
		Select item in a list/combo by the text
		
		@param text: text expected
		@type text: string
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to switch to element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(name=name, tagName=tagName, className=className, id=id,  xpath=xpath, linkText=linkText, 
																							partialLinkText=partialLinkText, cssSelector=cssSelector, location=location)
		selectElement = self.hasElement(timeout=timeout, commandId=cmdId) 
		if selectElement is  None:
			ret = False
		else:
			selectValue= selectElement.get('GUI',  'value')
			selectId = selectValue.get('element-id')
			
			xpath = ".//option[normalize-space(.) = %s]" % self._escapeString(text)
			cmdId = self.findChildElements(elementId=selectId, xpath=xpath)
			optionsSelect = self.hasChildElements(timeout=timeout, commandId=cmdId) 
			if optionsSelect is None:
				ret = False
			else:
				optionsValue = optionsSelect.get('GUI',  'value')
				optionsIds = eval( optionsValue.get('value') )
				
				if not len(optionsIds): 
					ret = False
				else:
					for opId in optionsIds:
						cmdId = self.clickElement(elementId=opId['ELEMENT'])
						elementClicked = self.isElementClicked(timeout=timeout, commandId=cmdId) 
						if elementClicked is None:
							ret = False
						else:
							ret = True
		return ret
	@doc_public
	def doRunJsElement(self, js, timeout=10.0, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None,  
																		partialLinkText=None, cssSelector=None, location=None):
		"""
		Run javascript on element
		
		@param js: javascript code
		@type js: string
		
		@param name: search element by name
		@type name: string/none

		@param tagName: search element by tag name
		@type tagName: string/none

		@param className: search element by class name
		@type className: string/none
		
		@param id: search element by identifier
		@type id: string/none

		@param xpath: search element by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: search element by link text
		@type linkText: string/none

		@param partialLinkText: search element by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: search element by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@param timeout: time max to wait to switch to element in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		if not self.cfg['wait-until']:
			cmdId = self.implicitlyWait(timeout=timeout)
			if self.isWait(timeout=timeout, commandId=cmdId) is None:
				ret = False
				return ret
				
		cmdId = self.findElement(name=name, tagName=tagName, className=className, id=id,  xpath=xpath, linkText=linkText, 
																							partialLinkText=partialLinkText, cssSelector=cssSelector, location=location)
		selectElement = self.hasElement(timeout=timeout, commandId=cmdId) 
		if selectElement is  None:
			ret = False
		else:
			elementValue= selectElement.get('GUI',  'value')
			elementId = elementValue.get('element-id')
			
			cmdId = self.runJavascriptElement(js=js, elementId=elementId)
			rsp = self.isScriptExecuted(timeout=timeout, commandId=cmdId)
			if rsp is None:
				ret = False
			return True
		return ret
		
	def _escapeString(self, value):
		"""
		internal function to escape string
		"""
		if '"' in value and "'" in value:
			substrings = value.split("\"")
			result = ["concat("]
			for substring in substrings:
				result.append("\"%s\"" % substring)
				result.append(", '\"', ")
			result = result[0:-1]
			if value.endswith('"'):
				result.append(", '\"'")
			return "".join(result) + ")"

			if '"' in value:
				return "'%s'" % value
		return "\"%s\"" % value
	@doc_public
	def doSwitchToDefaultWindow(self,  timeout=10.0):
		"""
		Do switch to default window
		@param timeout: time max to wait to switch to element in second (default=10s)
		@type timeout: float       
		@return: True on action OK, False otherwise
		@rtype: boolean   
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool):
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		cmdId = self.switchToDefaultFrame()
		if self.isFrameSwitched(timeout=timeout, commandId=cmdId)  is None:
			ret = False
		return ret
	# function to make actions
	@doc_public
	def getFirefoxProfile(self, profileDirectory=None):
		"""
		Return a firefox profile
		
		@param profileDirectory: Directory of profile that you want to use. (default=None)
		@type profileDirectory: string		
		
		@return: firefox profile instance 
		@rtype: object	
		"""
		fp = webdriver.FirefoxProfile(profile_directory=profileDirectory)
		return fp
		
	@doc_public
	def openNavig(self, desiredCapabilities, browserProfile=None, useMarionette=None, sessionName="default"):
		"""
		Start browser
			
		@return: internal command id
		@rtype: string
		"""
		self.navigId = None
		self.sessionName  = sessionName
		
		if browserProfile:
			desiredCapabilities['firefox_profile'] = browserProfile.encoded
		
		if useMarionette is not None:
			# True to use gecko driver, support firefox >= 48
			desiredCapabilities['marionette'] = useMarionette
			
		# send command to agent
		cmdId = self.executeCommand(Command.NEW_SESSION, { 'desiredCapabilities': desiredCapabilities,})
		return cmdId

	@doc_public
	def quitNavig(self):
		"""
		Stop browser
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.QUIT)
		return cmdId
		
	@doc_public
	def closeWindow(self):
		"""
		Closes the current window.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.CLOSE)
		return cmdId
		

	@doc_public
	def loadUrl(self, url):
		"""
		Loads a web page in the current browser session.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET, {'url': url})
		return cmdId
		
	@doc_public
	def getTitle(self):
		"""
		Gets the title of the current page.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_TITLE)
		return cmdId
		
	@doc_public
	def getUrl(self):
		"""
		Gets the URL of the current page.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_CURRENT_URL)
		return cmdId
		
	@doc_public
	def getPageSource(self):
		"""
		Gets the source of the current page.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_PAGE_SOURCE)
		return cmdId
		
	@doc_public
	def implicitlyWait(self, timeout=10.0):
		"""
		Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete. 
		This method only needs to be called one time per session.

		@param timeout: time max to wait to receive navig stopped event in second (default=10s)
		@type timeout: float		
		
		@return: internal command id
		@rtype: string
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		cmdId = self.executeCommand(Command.IMPLICIT_WAIT, {'ms': float(timeout) * 1000})
		return cmdId
		
	# function for windows
	@doc_public
	def maximizeWindow(self, windowHandle='current'):
		"""
		Maximizes the current window that webdriver is using

		@param windowHandle: window handle (default=current)
		@type windowHandle: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.MAXIMIZE_WINDOW, {"windowHandle": windowHandle})
		return cmdId
		
	@doc_public
	def setWindowSize(self, width, height, windowHandle='current'):
		"""
		Sets the width and height of the current window.

		@param width: width position
		@type width: integer

		@param height: height position
		@type height: integer
		
		@param windowHandle: window handle (default=current)
		@type windowHandle: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SET_WINDOW_SIZE, {'width': int(width), 'height': int(height), 
																								"windowHandle": windowHandle})
		return cmdId
		
	@doc_public
	def getWindowSize(self, windowHandle='current'):
		"""
		Gets the width and height of the current window.

		@param windowHandle: window handle (default=current)
		@type windowHandle: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_WINDOW_SIZE, {"windowHandle": windowHandle})
		return cmdId
		
	@doc_public
	def getWindowPosition(self, windowHandle='current'):
		"""
		Gets the x,y position of the current window.
		
		@param windowHandle: window handle (default=current)
		@type windowHandle: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_WINDOW_POSITION, {"windowHandle": windowHandle})
		return cmdId
		
	@doc_public
	def setWindowPosition(self, x, y , windowHandle='current'):
		"""
		Sets the x,y position of the current window.

		@param x: x position
		@type x: integer

		@param y: y position
		@type y: integer

		@param windowHandle: window handle
		@type windowHandle: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SET_WINDOW_POSITION, {'x': int(x), 'y': int(y),"windowHandle": windowHandle})
		return cmdId
		
	@doc_public
	def getCurrentWindowHandle(self):
		"""
		Gets the handle of the current window.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_CURRENT_WINDOW_HANDLE)
		return cmdId
		
	@doc_public
	def getAllWindowHandles(self):
		"""
		Get the handles of all windows within the current session.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_WINDOW_HANDLES)
		return cmdId
		
	@doc_public
	def switchToWindow(self, windowName):
		"""
		Switches focus to the specified window by name or handle

		@param windowName: window name
		@type windowName: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SWITCH_TO_WINDOW, {'name': windowName})
		return cmdId

	@doc_public
	def switchToFrame(self, reference):
		"""
		Switches focus to the specified window by frame or index

		@param reference: frame reference (by index, name, or id)
		@type reference: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SWITCH_TO_FRAME, {'id': reference})
		return cmdId
		
	@doc_public
	def switchToDefaultFrame(self):
		"""
		Switch focus to the default frame.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SWITCH_TO_FRAME, {'id': None})
		return cmdId
		
	# functions for alert
	@doc_public
	def dismissAlert(self):
		"""
		Dismiss alert
			
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.DISMISS_ALERT)
		return cmdId
		
	@doc_public
	def acceptAlert(self):
		"""
		Accept alert
			
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.ACCEPT_ALERT)
		return cmdId
		
	@doc_public
	def getTextAlert(self):
		"""
		Get the text of the alert
			
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_ALERT_TEXT)
		return cmdId
		
	@doc_public
	def authenticateDialog(self, username, password):
		"""
		Authenticate with username and password (Basic HTTP Auth for example)
		
		@param username: username
		@type username: string
		
		@param password: password
		@type password: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SET_ALERT_CREDENTIALS, {'username':username, 'password':password})
		return cmdId
		
	# function for navigation
	@doc_public
	def navigBack(self):
		"""
		Goes one step backward in the browser history.
			
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GO_BACK)
		return cmdId
		
	@doc_public
	def navigForward(self):
		"""
		Goes one step forward in the browser history.
			
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GO_FORWARD)
		return cmdId
		
	@doc_public
	def refreshPage(self):
		"""
		Refreshes the current page.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.REFRESH)
		return cmdId
		
	# function for interact with element
	@doc_public
	def findElement(self, elementId=None, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None, 
															partialLinkText=None, cssSelector=None, location=None, more={}):
		"""
		Find element
		
		@param elementId: element id
		@type elementId: string/none
		
		@param name: by name
		@type name: string/none

		@param tagName: by tag name
		@type tagName: string/none

		@param className: by class name
		@type className: string/none
		
		@param id: by identifier
		@type id: string/none

		@param xpath: by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: by link text
		@type linkText: string/none

		@param partialLinkText: by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@return: internal command id
		@rtype: string
		"""
		by = None
		
		if name is not None: 
			by = By.NAME
			value = name
			
		if id is not None: 
			by = By.ID
			value = id

		if xpath is not None: 
			by = By.XPATH
			value = xpath

		if linkText is not None: 
			by = By.LINK_TEXT
			value = linkText

		if partialLinkText is not None: 
			by = By.PARTIAL_LINK_TEXT
			value = partialLinkText

		if tagName is not None: 
			by = By.TAG_NAME
			value = tagName

		if className is not None: 
			by = By.CLASS_NAME
			value = className

		if cssSelector is not None: 
			by = By.CSS_SELECTOR
			value = cssSelector
		
		if by is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "please to specify how to find the element" )
		if location is not None: 
			by = By.XPATH
			value = location

		params = {'using': by, 'value': value}
		if elementId is not None:
			params['id'] = elementId
		cmdId = self.executeCommand(Command.FIND_ELEMENT, params, more=more)
		return cmdId
		
	@doc_public
	def findElements(self, elementId=None, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None, 
															partialLinkText=None, cssSelector=None, location=None):
		"""
		Find elements
		
		@param elementId: by element id
		@type elementId: string/none
		
		@param name: by name
		@type name: string/none

		@param tagName: by tag name
		@type tagName: string/none

		@param className: by class name
		@type className: string/none
		
		@param id: by identifier
		@type id: string/none

		@param xpath: by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: by link text
		@type linkText: string/none

		@param partialLinkText: by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@return: internal command id
		@rtype: string
		"""
		by = None
		
		if name is not None: 
			by = By.NAME
			value = name
			
		if id is not None: 
			by = By.ID
			value = id

		if xpath is not None: 
			by = By.XPATH
			value = xpath

		if linkText is not None: 
			by = By.LINK_TEXT
			value = linkText

		if partialLinkText is not None: 
			by = By.PARTIAL_LINK_TEXT
			value = partialLinkText

		if tagName is not None: 
			by = By.TAG_NAME
			value = tagName

		if className is not None: 
			by = By.CLASS_NAME
			value = className

		if cssSelector is not None: 
			by = By.CSS_SELECTOR
			value = cssSelector
		if location is not None: 
			by = By.XPATH
			value = location
		if by is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "please to specify how to find the element" )

		params = {'using': by, 'value': value}
		if elementId is not None:
			params['id'] = elementId
		cmdId = self.executeCommand(Command.FIND_ELEMENTS, params)
		return cmdId
	@doc_public
	def findChildElement(self, elementId, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None, 
															partialLinkText=None, cssSelector=None, location=None):
		"""
		Find child element
		
		@param elementId: parent element id
		@type elementId: string/none
		
		@param name: by name
		@type name: string/none

		@param tagName: by tag name
		@type tagName: string/none

		@param className: by class name
		@type className: string/none
		
		@param id: by identifier
		@type id: string/none

		@param xpath: by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: by link text
		@type linkText: string/none

		@param partialLinkText: by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@return: internal command id
		@rtype: string
		"""
		by = None
		
		if name is not None: 
			by = By.NAME
			value = name
			
		if id is not None: 
			by = By.ID
			value = id

		if xpath is not None: 
			by = By.XPATH
			value = xpath

		if linkText is not None: 
			by = By.LINK_TEXT
			value = linkText

		if partialLinkText is not None: 
			by = By.PARTIAL_LINK_TEXT
			value = partialLinkText

		if tagName is not None: 
			by = By.TAG_NAME
			value = tagName

		if className is not None: 
			by = By.CLASS_NAME
			value = className

		if cssSelector is not None: 
			by = By.CSS_SELECTOR
			value = cssSelector
		if location is not None: 
			by = By.XPATH
			value = location
		if by is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "please to specify how to find the element" )

		params = {'using': by, 'value': value}
		params['id'] = elementId
		cmdId = self.executeCommand(Command.FIND_CHILD_ELEMENT, params)
		return cmdId
		
	@doc_public
	def findChildElements(self, elementId, name=None, tagName=None, className=None, id=None, xpath=None, linkText=None, 
															partialLinkText=None, cssSelector=None, location=None):
		"""
		Find child elements
		
		@param elementId: by element id
		@type elementId: string/none
		
		@param name: by name
		@type name: string/none

		@param tagName: by tag name
		@type tagName: string/none

		@param className: by class name
		@type className: string/none
		
		@param id: by identifier
		@type id: string/none

		@param xpath: by xpath, example /html/body/form[1]
		@type xpath: string/none
		
		@param linkText: by link text
		@type linkText: string/none

		@param partialLinkText: by partial link text
		@type partialLinkText: string/none
		
		@param cssSelector: by css, example: p.content
		@type cssSelector: string/none

		@param location: as by xpath, example /html/body/form[1]
		@type location: string/none
		
		@return: internal command id
		@rtype: string
		"""
		by = None
		
		if name is not None: 
			by = By.NAME
			value = name
			
		if id is not None: 
			by = By.ID
			value = id

		if xpath is not None: 
			by = By.XPATH
			value = xpath

		if linkText is not None: 
			by = By.LINK_TEXT
			value = linkText

		if partialLinkText is not None: 
			by = By.PARTIAL_LINK_TEXT
			value = partialLinkText

		if tagName is not None: 
			by = By.TAG_NAME
			value = tagName

		if className is not None: 
			by = By.CLASS_NAME
			value = className

		if cssSelector is not None: 
			by = By.CSS_SELECTOR
			value = cssSelector
		if location is not None: 
			by = By.XPATH
			value = location
		if by is None: 
			raise TestAdapter.ValueException(TestAdapter.caller(), "please to specify how to find the element" )

		params = {'using': by, 'value': value}
		params['id'] = elementId
		cmdId = self.executeCommand(Command.FIND_CHILD_ELEMENTS, params)
		return cmdId
	@doc_public
	def getTextElement(self, elementId):
		"""
		Get the text of the element
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_ELEMENT_TEXT, {'id': elementId})
		return cmdId
		
	@doc_public
	def getAttributeElement(self, name, elementId):
		"""
		Gets the given attribute or property of the element
		
		@param name: name element
		@type name: string
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""	
		cmdId = self.executeCommand(Command.GET_ELEMENT_ATTRIBUTE, {'id': elementId, 'name': name})
		return cmdId

	@doc_public
	def clickElement(self, elementId):
		"""
		Clicks on element
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.CLICK_ELEMENT, {'id': elementId, 'button': 0})
		return cmdId
		
	@doc_public
	def hoverElement(self, elementId):
		"""
		Moving the mouse to the middle of an element.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.MOVE_TO, {'element': elementId})
		return cmdId
		
	@doc_public
	def getTagNameElement(self, elementId):
		"""
		Get tag name
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId =self.executeCommand(Command.GET_ELEMENT_TAG_NAME, {'id': elementId})
		return cmdId
		
	@doc_public
	def submitElement(self, elementId):
		"""
		Submits a form.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SUBMIT_ELEMENT, {'id': elementId})
		return cmdId

	@doc_public
	def clearTextElement(self, elementId):
		"""
		Clears the text if it's a text entry element.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.CLEAR_ELEMENT, {'id': elementId})
		return cmdId
	
	@doc_public
	def selectedElement(self, elementId):
		"""
		Return if the element is selected.
		Can be used to check if a checkbox or radio button is selected.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.IS_ELEMENT_SELECTED, {'id': elementId})
		return cmdId

	@doc_public
	def enabledElement(self, elementId):
		"""
		Return if the element is enabled.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.IS_ELEMENT_ENABLED, {'id': elementId})
		return cmdId
		
	@doc_public
	def displayedElement(self, elementId, more={}):
		"""
		Whether the element is visible to a user.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.IS_ELEMENT_DISPLAYED, {'id': elementId}, 	more=more)
		return cmdId
		
	@doc_public
	def sizeElement(self, elementId):
		"""
		The size of the element.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_ELEMENT_SIZE, {'id': elementId})
		return cmdId
		
	@doc_public
	def locationElement(self, elementId):
		"""
		The location of the element in the renderable canvas.
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_ELEMENT_LOCATION, {'id': elementId})
		return cmdId
		
	@doc_public
	def typeTextElement(self, elementId, text):
		"""
		Simulates typing text into the element.
		
		@param elementId: element id
		@type elementId: string
		
		@param text: text
		@type text: string
		
		@return: internal command id
		@rtype: string
		"""
		text = unicode(text, 'utf8')
		typing = []
		for val in text:
			if isinstance(val, Keys):
				typing.append(val)
			elif isinstance(val, int):
				val = val.__str__()
				for i in range(len(val)):
					typing.append(val[i])
			else:
				for i in range(len(val)):
					typing.append(val[i])
		cmdId = self.executeCommand(Command.SEND_KEYS_TO_ELEMENT, {'id': elementId, 'value': typing})
		return cmdId
		
	@doc_public
	def typeKeyElement(self, elementId, key):
		"""
		Simulates typing key into the element.

		@param elementId: element id
		@type elementId: string
		
		@param key: SutAdapters.GUI.SELENIUM_KEY_NULL | SutAdapters.GUI.SELENIUM_KEY_CANCEL | SutAdapters.GUI.SELENIUM_KEY_HELP | SutAdapters.GUI.SELENIUM_KEY_BACKSPACE | SutAdapters.GUI.SELENIUM_KEY_TAB | SutAdapters.GUI.SELENIUM_KEY_CLEAR | SutAdapters.GUI.SELENIUM_KEY_RETURN | SutAdapters.GUI.SELENIUM_KEY_ENTER | SutAdapters.GUI.SELENIUM_KEY_SHIFT | SutAdapters.GUI.SELENIUM_KEY_CONTROL | SutAdapters.GUI.SELENIUM_KEY_ALT | SutAdapters.GUI.SELENIUM_KEY_PAUSE | SutAdapters.GUI.SELENIUM_KEY_ESCAPE | SutAdapters.GUI.SELENIUM_KEY_SPACE | SutAdapters.GUI.SELENIUM_KEY_PAGE_UP | SutAdapters.GUI.SELENIUM_KEY_PAGE_DOWN | SutAdapters.GUI.SELENIUM_KEY_END | SutAdapters.GUI.SELENIUM_KEY_HOME | SutAdapters.GUI.SELENIUM_KEY_LEFT | SutAdapters.GUI.SELENIUM_KEY_UP | SutAdapters.GUI.SELENIUM_KEY_RIGHT | SutAdapters.GUI.SELENIUM_KEY_DOWN | SutAdapters.GUI.SELENIUM_KEY_INSERT | SutAdapters.GUI.SELENIUM_KEY_DELETE | SutAdapters.GUI.SELENIUM_KEY_SEMICOLON | SutAdapters.GUI.SELENIUM_KEY_EQUALS | SutAdapters.GUI.SELENIUM_KEY_NUMPAD0 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD1 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD2 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD3 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD4 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD5 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD6 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD7 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD8 | SutAdapters.GUI.SELENIUM_KEY_NUMPAD9 | SutAdapters.GUI.SELENIUM_KEY_MULTIPLY | SutAdapters.GUI.SELENIUM_KEY_ADD | SutAdapters.GUI.SELENIUM_KEY_SEPARATOR | SutAdapters.GUI.SELENIUM_KEY_SUBTRACT | SutAdapters.GUI.SELENIUM_KEY_DECIMAL | SutAdapters.GUI.SELENIUM_KEY_DIVIDE | SutAdapters.GUI.SELENIUM_KEY_F1 | SutAdapters.GUI.SELENIUM_KEY_F2 | SutAdapters.GUI.SELENIUM_KEY_F3 | SutAdapters.GUI.SELENIUM_KEY_F4 | SutAdapters.GUI.SELENIUM_KEY_F5 | SutAdapters.GUI.SELENIUM_KEY_F6 | SutAdapters.GUI.SELENIUM_KEY_F7 | SutAdapters.GUI.SELENIUM_KEY_F8 | SutAdapters.GUI.SELENIUM_KEY_F9 | SutAdapters.GUI.SELENIUM_KEY_F10 | SutAdapters.GUI.SELENIUM_KEY_F11 | SutAdapters.GUI.SELENIUM_KEY_F12 | SutAdapters.GUI.SELENIUM_KEY_META | SutAdapters.GUI.SELENIUM_KEY_COMMAND
		@type key: strconstant
		
		@return: internal command id
		@rtype: string
		"""
		typing = [ key ]
		cmdId = self.executeCommand(Command.SEND_KEYS_TO_ELEMENT, {'id': elementId, 'value': typing})
		return cmdId
		

	@doc_public
	def runJavascriptElement(self, js, elementId):
		"""
		Execute javascript on element

		@param js: javascript to execute on element
		@type js: string
		
		@param elementId: element id
		@type elementId: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.executeScript(js, {"ELEMENT": elementId} )
		
	@doc_public
	def executeScript(self, script, *args):
		"""
		Execute javascript

		@param script: javascript to execute
		@type script: string

		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.EXECUTE_SCRIPT, {'script': script, 'args': list(args)} )
		return cmdId
		
	# function for mouse
	@doc_public
	def click(self):
		"""
		Mouse click
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.CLICK, {'button': 0})
		return cmdId
		
	@doc_public
	def rightClick(self):
		"""
		Rigth click from mouse
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.CLICK, {'button': 2})
		return cmdId
		
	@doc_public
	def doubleClick(self):
		"""
		Double click from mouse
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.DOUBLE_CLICK)
		return cmdId
		
	@doc_public
	def clickDown(self):
		"""
		Mouse button down
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.MOUSE_DOWN)
		return cmdId
		
	@doc_public
	def clickUp(self):
		"""
		Mouse button up
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.MOUSE_UP)
		return cmdId
		
	@doc_public
	def mouseMove(self, xoffset, yoffset):
		"""
		Moving the mouse to an offset from current mouse position.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.MOVE_TO, {'xoffset': int(xoffset), 'yoffset': int(yoffset)} )
		return cmdId
		
	# function for cookies
	@doc_public
	def getCookies(self):
		"""
		Get a set of dictionaries, corresponding to cookies visible in the current session.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.GET_ALL_COOKIES)
		return cmdId

	@doc_public
	def deleteCookies(self):
		"""
		Delete all cookies in the scope of the session.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.DELETE_ALL_COOKIES)
		return cmdId
		
	@doc_public
	def deleteCookie(self, name):
		"""
		Deletes a single cookie with the given name.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.DELETE_COOKIE, {'name': name})
		return cmdId
		
	@doc_public
	def addCookie(self, cook):
		"""
		Adds a cookie to your current session.
		
		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.ADD_COOKIE, {'cookie': cook})
		return cmdId
	# functions for screenshots
	@doc_public
	def getScreenshot(self):
		"""
		Gets the screenshot of the current window

		@return: internal command id
		@rtype: string
		"""
		cmdId = self.executeCommand(Command.SCREENSHOT)
		return cmdId
	# function to check responses
	@doc_public
	def isActionAccepted(self, timeout=10.0, commandName=None, commandId=None, expectedValue=None):
		"""
		Waits to receive "action accepted" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=10s)
		@type timeout: float		

		@param commandName:  name action
		@type commandName: string/none

		@param commandId: action id
		@type commandId: string/none
		
		@param expectedValue: text expected in vallue
		@type expectedValue: string/templates/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		expected = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=ACTION_OK, value=expectedValue ))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isFrameSwitched(self, timeout=30.0, commandId=None):
		"""
		Waits to receive "iframe switched" event until the end of the timeout
		
		@param timeout: time max to wait to receive is switched event in second (default=20s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.SWITCH_TO_FRAME, commandId=commandId)
	@doc_public
	def isWindowsSwitched(self, timeout=30.0, commandId=None):
		"""
		Waits to receive "iwindows switched" event until the end of the timeout
		
		@param timeout: time max to wait to receive is switched event in second (default=20s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.SWITCH_TO_WINDOW, commandId=commandId)
	@doc_public
	def isNavigStarted(self, timeout=30.0, commandId=None):
		"""
		Waits to receive "navigator started" event until the end of the timeout
		
		@param timeout: time max to wait to receive navig started event in second (default=20s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.NEW_SESSION, commandId=commandId)
	
	@doc_public
	def isNavigStopped(self, timeout=30.0, commandId=None):
		"""
		Waits to receive "navigator stopped" event until the end of the timeout
		
		@param timeout: time max to wait to receive navig stopped event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.QUIT, commandId=commandId)
	@doc_public
	def isWindowClosed(self, timeout=30.0, commandId=None):
		"""
		Waits to receive "window closed" event until the end of the timeout
		
		@param timeout: time max to wait to receive window closed event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.CLOSE, commandId=commandId)
		
	@doc_public
	def isUrlLoaded(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "url loaded" event until the end of the timeout
		
		@param timeout: time max to wait to receive url loaded event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET, commandId=commandId)
		
	@doc_public
	def isMaximized(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "maximized" event until the end of the timeout
		
		@param timeout: time max to wait to receive maximized event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.MAXIMIZE_WINDOW, commandId=commandId)
	@doc_public
	def isRefreshed(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "refreshed" event until the end of the timeout
		
		@param timeout: time max to wait to receive refresh event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.REFRESH, commandId=commandId)
	@doc_public
	def isGoBack(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "go back" event until the end of the timeout
		
		@param timeout: time max to wait to receive go back event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GO_BACK, commandId=commandId)
	@doc_public
	def isGoForward(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "go forward" event until the end of the timeout
		
		@param timeout: time max to wait to receive go forward event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GO_FORWARD, commandId=commandId)
	@doc_public
	def hasWindowHandle(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "window handle" event until the end of the timeout
		
		@param timeout: time max to wait to receive window handle event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_CURRENT_WINDOW_HANDLE, 
																						commandId=commandId)
																						
	@doc_public
	def hasWindowHandles(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "window handles" event until the end of the timeout
		
		@param timeout: time max to wait to receive window handles event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_WINDOW_HANDLES, 
																						commandId=commandId)
																						
	@doc_public
	def hasUrl(self, timeout=20.0, commandId=None, expectedText=None):
		"""
		Waits to receive "url event" until the end of the timeout
		
		@param timeout: time max to wait to receive url event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none

		@param expectedText: text expected in url
		@type expectedText: string/operators/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		valueLayer = TestTemplates.TemplateLayer(name="")
		if expectedText is not None:
			valueLayer.addKey(name="value", data=expectedText)
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_CURRENT_URL, 
																						commandId=commandId, expectedValue=valueLayer)
																						
	@doc_public
	def hasSource(self, timeout=20.0, commandId=None, expectedText=None):
		"""
		Waits to receive "code source" event until the end of the timeout
		
		@param timeout: time max to wait to receive code source event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none

		@param expectedText: text expected in source
		@type expectedText: string/operators/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		valueLayer = TestTemplates.TemplateLayer(name="")
		if expectedText is not None:
			valueLayer.addKey(name="value", data=expectedText)
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_PAGE_SOURCE, 
																						commandId=commandId, expectedValue=valueLayer)
																						
	@doc_public
	def hasWindowTitle(self, timeout=20.0, commandId=None, expectedText=None):
		"""
		Waits to receive "window title" event until the end of the timeout
		
		@param timeout: time max to wait to receive window title event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none

		@param expectedText: text expected in title
		@type expectedText: string/operators/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		valueLayer = TestTemplates.TemplateLayer(name="")
		if expectedText is not None:
			valueLayer.addKey(name="value", data=expectedText)
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_TITLE, 
																						commandId=commandId, expectedValue=valueLayer)
																						
	@doc_public
	def hasScreenshot(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "screenshot" event until the end of the timeout
		
		@param timeout: time max to wait to receive screenshot event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.SCREENSHOT, 
																						commandId=commandId)
																						
	@doc_public
	def hasElement(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element" event until the end of the timeout
		
		@param timeout: time max to wait to receive element event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.FIND_ELEMENT, 
																						commandId=commandId)
																						
	@doc_public
	def hasElements(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "elements" event until the end of the timeout
		
		@param timeout: time max to wait to receive elements event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.FIND_ELEMENTS, 
																						commandId=commandId)
	@doc_public
	def hasChildElement(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element" event until the end of the timeout
		
		@param timeout: time max to wait to receive element event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.FIND_CHILD_ELEMENT, 
																						commandId=commandId)
																						
	@doc_public
	def hasChildElements(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "elements" event until the end of the timeout
		
		@param timeout: time max to wait to receive elements event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.FIND_CHILD_ELEMENTS, 
																						commandId=commandId)
	@doc_public
	def hasTextElement(self, timeout=20.0, commandId=None, expectedText=None):
		"""
		Waits to receive "text element" event until the end of the timeout
		
		@param timeout: time max to wait to receive text element event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@param expectedText: text expected in value
		@type expectedText: string/operators/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		valueLayer = TestTemplates.TemplateLayer(name="")
		if expectedText is not None:
			valueLayer.addKey(name="value", data=expectedText)
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_ELEMENT_TEXT, 
																						commandId=commandId, expectedValue=valueLayer)
																						
	@doc_public
	def hasAttributeElement(self, timeout=20.0, commandId=None, expectedText=None):
		"""
		Waits to receive "text attribute" element event until the end of the timeout
		
		@param timeout: time max to wait to receive text attribute element event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@param expectedText: text expected in value
		@type expectedText: string/operators/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		valueLayer = TestTemplates.TemplateLayer(name="")
		if expectedText is not None:
			valueLayer.addKey(name="value", data=expectedText)
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_ELEMENT_ATTRIBUTE,  
																						commandId=commandId, expectedValue=valueLayer)
																						
	@doc_public
	def isElementClicked(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element clicked" event until the end of the timeout
		
		@param timeout: time max to wait to receive element clicked event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.CLICK_ELEMENT, 
																						commandId=commandId)
																						
	@doc_public
	def isElementSubmitted(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element submitted" event until the end of the timeout
		
		@param timeout: time max to wait to receive element submitted event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.SUBMIT_ELEMENT, 
																						commandId=commandId)
																						
	@doc_public
	def isElementCleared(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element cleared" event until the end of the timeout
		
		@param timeout: time max to wait to receive element cleared event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.CLEAR_ELEMENT, 
																						commandId=commandId)
																						
	@doc_public
	def isElementSelected(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element selected" event until the end of the timeout
		
		@param timeout: time max to wait to receive element selected event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.IS_ELEMENT_SELECTED, 
																						commandId=commandId)
																						
	@doc_public
	def isElementEnabled(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element enabled" event until the end of the timeout
		
		@param timeout: time max to wait to receive element enabled event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.IS_ELEMENT_ENABLED, 
																						commandId=commandId)
																						
	@doc_public
	def isElementDisplayed(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element displayed" event until the end of the timeout
		
		@param timeout: time max to wait to receive element displayed event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.IS_ELEMENT_DISPLAYED, 
																						commandId=commandId)
																						
	@doc_public
	def isElementSize(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element size" event until the end of the timeout
		
		@param timeout: time max to wait to receive element size event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_ELEMENT_SIZE, 
																						commandId=commandId)
																						
	@doc_public
	def isElementLocation(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "element location" event until the end of the timeout
		
		@param timeout: time max to wait to receive element location event in second (default=10s)
		@type timeout: float	
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_ELEMENT_LOCATION, 
																						commandId=commandId)
																						
	@doc_public
	def hasTextEntered(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "text entered" event until the end of the timeout
		
		@param timeout: time max to wait to receive text entered event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.SEND_KEYS_TO_ELEMENT, 
																						commandId=commandId)
																						
	@doc_public
	def hasMouseMoved(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "mouse moved" event until the end of the timeout
		
		@param timeout: time max to wait to receive mouse moved event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.MOVE_TO, 
																						commandId=commandId)
																						
	@doc_public
	def isClicked(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "clicked event" until the end of the timeout
		
		@param timeout: time max to wait to receive clicked event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.CLICK, 
																						commandId=commandId)
																						
	@doc_public
	def isDoubleClicked(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "double clicked" event until the end of the timeout
		
		@param timeout: time max to wait to receive double clicked event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.DOUBLE_CLICK, 
																						commandId=commandId)
																						
	@doc_public
	def isClickedDown(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "clicked down" event until the end of the timeout
		
		@param timeout: time max to wait to receive click down event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.MOUSE_DOWN, 
																						commandId=commandId)
																						
	@doc_public
	def isClickedUp(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "clicked up" event until the end of the timeout
		
		@param timeout: time max to wait to receive click up event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.MOUSE_UP, 
																						commandId=commandId)
																						
	@doc_public
	def isWait(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "wait" event until the end of the timeout
		
		@param timeout: time max to wait to receive wait event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.IMPLICIT_WAIT, 
																						commandId=commandId)
	@doc_public
	def isAlertDismissed(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "dismiss alert" event until the end of the timeout
		
		@param timeout: time max to wait to receive dismiss alert event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.DISMISS_ALERT, 
																						commandId=commandId)
	@doc_public
	def isAlertAccepted(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "accept alert" event until the end of the timeout
		
		@param timeout: time max to wait to receive accept alert event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.ACCEPT_ALERT, 
																						commandId=commandId)
	@doc_public
	def hasTextAlert(self, timeout=20.0, commandId=None, expectedText=None):
		"""
		Waits to receive "text alert" event until the end of the timeout
		
		@param timeout: time max to wait to receive text alert event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		valueLayer = TestTemplates.TemplateLayer(name="")
		if expectedText is not None:
			valueLayer.addKey(name="value", data=expectedText)
		return self.isActionAccepted(timeout=timeout, commandName=Command.GET_ALERT_TEXT, 
																						commandId=commandId, expectedValue=valueLayer)
	@doc_public
	def isAlertAuthenticated(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "authenticated" event until the end of the timeout
		
		@param timeout: time max to wait to receive authenticated event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.SET_ALERT_CREDENTIALS, 
																						commandId=commandId)
	@doc_public
	def isScriptExecuted(self, timeout=20.0, commandId=None):
		"""
		Waits to receive "script executed" event until the end of the timeout
		
		@param timeout: time max to wait to receive script executed event in second (default=10s)
		@type timeout: float		
		
		@param commandId: action id
		@type commandId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.isActionAccepted(timeout=timeout, commandName=Command.EXECUTE_SCRIPT, 
																						commandId=commandId)