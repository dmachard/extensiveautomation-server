#!/usr/bin/env python
# -*- coding=utf-8 -*-

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
import threading
import uuid

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

try:
	import templates
except ImportError: # python3 support
	from . import templates

__NAME__="""Sikuli"""

ACTION_SCREENSHOT = "SCREENSHOT"
ACTION_THUMBNAIL = "THUMBNAIL"
ACTION_OK = "OK"
ACTION_FAILED = "FAILED"

ACTION_RAW_CODE = "RAW_CODE"

ACTION_WHEEL_DOWN = "WHEEL_DOWN"
ACTION_WHEEL_UP = "WHEEL_UP"

ACTION_MOVE_POSITION = "MOVE_POSITION"
ACTION_RIGHT_CLICK_POSITION = "RIGHT_CLICK_POSITION"
ACTION_DOUBLE_CLICK_POSITION = "DOUBLE_CLICK_POSITION"
ACTION_CLICK_POSITION = "CLICK_POSITION"

ACTION_COUNT_IMAGE = "COUNT_IMAGE"
ACTION_COUNT_WORD = "COUNT WORD"

ACTION_DRAGDROP_IMAGE = "DRAPDROP_IMAGE"
ACTION_HOVER_IMAGE = "HOVER_IMAGE"

ACTION_CLICK_IMAGE = "CLICK_IMAGE"
ACTION_CLICK_TEXT = "CLICK_TEXT"
ACTION_CLICK_WORD = "CLICK_WORD"
ACTION_DOUBLE_CLICK_IMAGE = "DOUBLE_CLICK_IMAGE"
ACTION_DOUBLE_CLICK_TEXT = "DOUBLE_CLICK_TEXT"
ACTION_DOUBLE_CLICK_WORD = "DOUBLE_CLICK_WORD"
ACTION_RIGHT_CLICK_IMAGE = "RIGHT_CLICK_IMAGE"
ACTION_RIGHT_CLICK_TEXT = "RIGHT_CLICK_TEXT"
ACTION_RIGHT_CLICK_WORD = "RIGHT_CLICK_WORD"
ACTION_FIND_IMAGE = "FIND_IMAGE"
ACTION_DONT_FIND_IMAGE = "DONT_FIND_IMAGE"
ACTION_FIND_CLICK_IMAGE = "FIND_CLICK_IMAGE"
ACTION_WAIT_IMAGE = "WAIT_IMAGE"
ACTION_WAIT_WORD = "WAIT_WORD"
ACTION_WAIT_CLICK_IMAGE = "WAIT_CLICK_IMAGE"
ACTION_WAIT_CLICK_WORD = "WAIT_CLICK_WORD"
ACTION_FIND_TEXT = "FIND_TEXT"
ACTION_TYPE_TEXT = "TYPE_TEXT"
ACTION_GET_TEXT = "GET_TEXT"
ACTION_TYPE_SHORTCUT = "TYPE_SHORCUT"
ACTION_GET_CLIPBOARD = "GET_CLIPBOARD"

KEY_ENTER="Key.ENTER"
KEY_TAB="Key.TAB"
KEY_ESC="Key.ESC"
KEY_BACKSPACE="Key.BACKSPACE"
KEY_DELETE="Key.DELETE"
KEY_INSERT="Key.INSERT"

KEY_SPACE="Key.SPACE"

KEY_HOME="Key.HOME"
KEY_END="Key.END"
KEY_LEFT="Key.LEFT"
KEY_RIGHT="Key.RIGHT"
KEY_DOWN="Key.DOWN"
KEY_UP="Key.UP"
KEY_PAGE_DOWN="Key.PAGE_DOWN"
KEY_PAGE_UP="Key.PAGE_UP"

KEY_F1="Key.F1"
KEY_F2="Key.F2"
KEY_F3="Key.F3"
KEY_F4="Key.F4"
KEY_F5="Key.F5"
KEY_F6="Key.F6"
KEY_F7="Key.F7"
KEY_F8="Key.F8"
KEY_F9="Key.F9"
KEY_F10="Key.F10"
KEY_F11="Key.F11"
KEY_F12="Key.F12"
KEY_F13="Key.F13"
KEY_F14="Key.F14"
KEY_F15="Key.F15"

KEY_PRINTSCREEN="Key.PRINTSCREEN"
KEY_PAUSE="Key.PAUSE"
KEY_CAPS_LOCK="Key.CAPS_LOCK"
KEY_SCROLL_LOCK="Key.SCROLL_LOCK"
KEY_NUM_LOCK="Key.NUM_LOCK"

KEY_NUM0="Key.NUM0"
KEY_NUM1="Key.NUM1"
KEY_NUM2="Key.NUM2"
KEY_NUM3="Key.NUM3"
KEY_NUM4="Key.NUM4"
KEY_NUM5="Key.NUM5"
KEY_NUM6="Key.NUM6"
KEY_NUM7="Key.NUM7"
KEY_NUM8="Key.NUM8"
KEY_NUM9="Key.NUM9"
KEY_SEPARATOR="Key.SEPARATOR"
KEY_ADD="Key.ADD"
KEY_MINUS="Key.MINUS"
KEY_MULTIPLY="Key.MULTIPLY"
KEY_DIVIDE="Key.DIVIDE"

KEY_ALT="KeyModifier.ALT"
KEY_CMD="KeyModifier.CMD"
KEY_CTRL="KeyModifier.CTRL"
KEY_META="KeyModifier.META"
KEY_SHIFT="KeyModifier.SHIFT"
KEY_WIN="KeyModifier.WIN"

MOD_KEY_ALT="Key.ALT"
MOD_KEY_CMD="Key.CMD"
MOD_KEY_CTRL="Key.CTRL"
MOD_KEY_META="Key.META"
MOD_KEY_SHIFT="Key.SHIFT"
MOD_KEY_WIN="Key.WIN"

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='sikulixserver'

class Sikuli(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, agent, name=None, debug=False, shared=False, verbose=True):
		"""
		This class enables to control all gui throught a agent and sikuli

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param agent: agent to use, sikuli type expected
		@type agent: string
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		"""
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, 
																										realname=name, agentSupport=True, agent=agent, shared=shared,
																										showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose,
																										caller=TestAdapterLib.caller(),
																										agentType=AGENT_TYPE_EXPECTED)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.__mutexActionId__ = threading.RLock()
		self.actionId = 0
		
		self.cfg = {}
		self.cfg['agent-support'] = True
		self.cfg['agent'] = agent
		self.cfg['agent-name'] = agent['name']
		self.cfg['debug'] = debug

		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		self.prepareAgent(data={'shared': shared})
		if self.agentIsReady(timeout=30) is None: 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
		self.TIMER_ALIVE_AGT.start()
		
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
		self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
		
	def getActionId(self):
		"""
		"""
		self.__mutexActionId__.acquire()
		self.actionId += 1
		ret = "%s" % self.actionId
		self.__mutexActionId__.release()
		return ret
		
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		# stop timer
		self.TIMER_ALIVE_AGT.stop()
		
		# cleanup remote agent
		self.resetAgent()
	
	def encapsule(self, layer_gui):
		"""
		"""
		layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
		layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
		layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_gui)
		return tpl

	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if 'cmd' in data:
			if data['cmd'] == AGENT_INITIALIZED:
				tpl = TestTemplatesLib.TemplateMessage()
				layer = TestTemplatesLib.TemplateLayer('AGENT')
				layer.addKey("ready", True)
				layer.addKey(name='name', data=self.cfg['agent']['name'] )
				layer.addKey(name='type', data=self.cfg['agent']['type'] )
				tpl.addLayer(layer= layer)
				self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )	
		else:	
			if data['result'] == ACTION_FAILED:
				self.debug( 'unable to execute action %s on remote agent' %  data['action'] )
				
			# log event
			if 'text-result' in data:
				tpl = self.encapsule(layer_gui=templates.gui(action=data['action'], actionId=data['action-id'], 
																				result=data['result'] , textResult=data['text-result'].strip()) )
				self.logRecvEvent( shortEvt = "%s [text-length=%s]" % (data['action'], len(data['text-result'].strip())), tplEvt = tpl )		
			else:
				tpl = self.encapsule(layer_gui=templates.gui(action=data['action'], actionId=data['action-id'], result=data['result'], 
																																			out=data['output']	) )
				self.logRecvEvent( shortEvt = "%s [result=%s]" % (data['action'], data['result']), tplEvt = tpl )
			
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
																			action=data['action'], 
																			actionId=data['action-id'],
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
		if self.cfg['debug']:
			if "code" in data: 
				data['code'] = 'HOME_PATH = "__PATH__";\n' + data['code'] 
				data['code'] = 'Settings.Highlight = True;\n' + data['code'] 
		else:
			if "code" in data: 
				data['code'] = 'HOME_PATH = "__PATH__";\n' + data['code'] 
				data['code'] = 'Settings.Highlight = False;\n' + data['code'] 

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
		
	@doc_public
	def getTimeout(self, timeout=None):
		"""
		"""
		threshold = 90 # reduce to 90% of the interval
		if timeout is None:
			return timeout
		else:
			return (timeout*threshold) / 100
		
	@doc_public
	def takeScreenshot(self):
		"""
		Take a screenshot on the remote machine
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_SCREENSHOT
		actionId = self.getActionId()

		data = {'action': action, 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	
	@doc_public
	def rawAction(self, rawCode, img1=None, img2=None, description='unknown'):
		"""
		Send raw action to the agent
		Use this function with caution!
		
		@param rawCode: code
		@type rawCode: string
		
		@param img1: first image to use in the raw code with tag __IMG1__
		@type img1: image	
		
		@param img2: second image to use in the raw code with tag __IMG2__
		@type img2: image	

		@param description: image name (default='unknown')
		@type description: string	
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_RAW_CODE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		rawCode = rawCode.replace("__IMG1__", "r\"__PATH__\\%s.png\"" %  imgName)
		rawCode = rawCode.replace("__IMG2__", "r\"__PATH__\\%s.png\"" %  mainImgName)
		
		code = [ rawCode ]
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		if img1 is not None:
			data['main-img'] = img1
			data['main-img-name'] = mainImgName
		if img2 is not None:
			data['img'] = img2
			data['img-name'] = imgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, 
																		img=img2, mainImg=img1) )
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def typeShorcut(self, key=None, modifier=None, special=None, other=None, description='unknown', repeat=0):
		"""
		Type shortcut with keyboard
		CTRL +ALT+DELETE cannot be typed simulated, only on the real keyboard.

		@param key: SutAdapters.GUI.MOD_KEY_ALT | SutAdapters.GUI.MOD_KEY_CMD | SutAdapters.GUI.MOD_KEY_CTRL | SutAdapters.GUI.KEY_META | SutAdapters.GUI.MOD_KEY_SHIFT | SutAdapters.GUI.MOD_KEY_WIN
		@type key: strconstant/none			
	
		@param modifier: SutAdapters.GUI.MOD_KEY_ALT | SutAdapters.GUI.MOD_KEY_CMD | SutAdapters.GUI.MOD_KEY_CTRL | SutAdapters.GUI.KEY_META | SutAdapters.GUI.MOD_KEY_SHIFT | SutAdapters.GUI.MOD_KEY_WIN
		@type modifier: strconstant/none						

		@param special: SutAdapters.GUI.KEY_ENTER | SutAdapters.GUI.KEY_TAB | SutAdapters.GUI.KEY_ESC | SutAdapters.GUI.KEY_BACKSPACE | SutAdapters.GUI.KEY_DELETE | SutAdapters.GUI.KEY_INSERT | SutAdapters.GUI.KEY_SPACE | SutAdapters.GUI.KEY_HOME | SutAdapters.GUI.KEY_END | SutAdapters.GUI.KEY_LEFT | SutAdapters.GUI.KEY_RIGHT | SutAdapters.GUI.KEY_DOWN | SutAdapters.GUI.KEY_UP | SutAdapters.GUI.KEY_PAGE_DOWN | SutAdapters.GUI.KEY_UP | SutAdapters.GUI.KEY_F1 | SutAdapters.GUI.KEY_F2 | SutAdapters.GUI.KEY_F3 | SutAdapters.GUI.KEY_F4 | SutAdapters.GUI.KEY_F5 | SutAdapters.GUI.KEY_F6 | SutAdapters.GUI.KEY_F7 | SutAdapters.GUI.KEY_F8 | SutAdapters.GUI.KEY_F9 | SutAdapters.GUI.KEY_F10 | SutAdapters.GUI.KEY_F11 | SutAdapters.GUI.KEY_F12 | SutAdapters.GUI.KEY_F13 | SutAdapters.GUI.KEY_F14 | SutAdapters.GUI.KEY_F15 | SutAdapters.GUI.KEY_PRINTSCREEN | SutAdapters.GUI.KEY_PAUSE | SutAdapters.GUI.KEY_CAPS_LOCK | SutAdapters.GUI.KEY_SCROLL_LOCK | SutAdapters.GUI.KEY_NUM_LOCK | SutAdapters.GUI.KEY_NUM0 | SutAdapters.GUI.KEY_NUM1 | SutAdapters.GUI.KEY_NUM2 | SutAdapters.GUI.KEY_NUM3 | SutAdapters.GUI.KEY_NUM4 | SutAdapters.GUI.KEY_NUM5 | SutAdapters.GUI.KEY_NUM6 | SutAdapters.GUI.KEY_NUM7 | SutAdapters.GUI.KEY_NUM8 | SutAdapters.GUI.KEY_NUM9 | SutAdapters.GUI.KEY_SEPARATOR | SutAdapters.GUI.KEY_ADD | SutAdapters.GUI.KEY_MINUS | SutAdapters.GUI.KEY_MULTIPLY | SutAdapters.GUI.KEY_DIVIDE
		@type special: string/none	
		
		@param other: all others keys
		@type other: string/none		
		
		@param repeat: repeat shorcut (default=0)
		@type repeat: integer
	
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_TYPE_SHORTCUT
		actionId = self.getActionId()
		code = [ "try:" ]
		
		keys = []
		
		code.append( "\tfor i in xrange(%s):" % (repeat +1))
		
		if key is not None:
			code.append( '\t\tkeyDown(%s)' % ( key ) )
			keys.append(key)
		if modifier is not None:
			code.append( '\t\tkeyDown(%s)' % ( modifier ) )			
			keys.append(modifier)
		if special is not None:
			code.append( '\t\tkeyDown(%s)' % ( special ) )		
			keys.append(special)	
		if other is not None:
			code.append( '\t\tkeyDown("%s")' % ( other ) )			
			keys.append(other)	

		if key is not None:
			code.append( '\t\tkeyUp(%s)' % ( key ) )
		if modifier is not None:
			code.append( '\t\tkeyUp(%s)' % ( modifier ) )			
		if special is not None:
			code.append( '\t\tkeyUp(%s)' % ( special ) )			
		if other is not None:
			code.append( '\t\tkeyUp("%s")' % ( other ) )			
			
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')

		# for backward compatiblity, replace keymodifier by key
		sikuliCode = "\n".join(code)
		sikuliCode = sikuliCode.replace("KeyModifier.", "Key.")
		self.debug( sikuliCode )
		
		data = {'action': action, 'code': sikuliCode, 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text='+'.join(keys),
																																	repeat=repeat))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def typeText(self, text='', keys=[], keysModifiers=[], img=None, description='unknown', similar=0.70):
		"""
		Type the text on the image passed as argument

		@param text: text to type
		@type text: string	
		
		@param img: image to find
		@type img: image	

		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@return: action id
		@rtype: string	
		"""
		if not isinstance( keys, list): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "keys argument is not a list (%s)" % type(keys) )
		if not isinstance( keysModifiers, list): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "keysModifiers argument is not a list (%s)" % type(keysModifiers) )
		if text is None: 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "text argument is none" )
		
		action =  ACTION_TYPE_TEXT
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		if img is not None:
			code.append( '\tpaste(Pattern("%s.png").similar(%s), "%s")' % ( imgName, similar, text) )
		else:
			if len(keysModifiers):
				if len(keys):
					code.append( '\ttype( "%s" + %s, %s)' % (text, '+'.join(keys), '+'.join(keysModifiers)) )
				else:
					code.append( '\ttype( "%s", %s)' % (text, '+'.join(keysModifiers)) )
			else:
				if len(keys):
					code.append( '\ttype( "%s" + %s)' % ( text, '+'.join(keys)) )
				else:
					code.append( '\tpaste( unicode("%s", "utf8") )' % ( text ) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')

		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		if img is not None:
			data.update( {'img': img, 'img-name': imgName} )
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=text))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def typePath(self, text='', keys=[], keysModifiers=[], img=None, description='unknown', similar=0.70):
		"""
		Type the path on the image passed as argument

		@param text: text to type
		@type text: string	
		
		@param img: image to find
		@type img: image	

		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@return: action id
		@rtype: string	
		"""
		if not isinstance( keys, list): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "keys argument is not a list (%s)" % type(keys) )
			#raise Exception('list expected for keys')
		if not isinstance( keysModifiers, list): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "keysModifiers argument is not a list (%s)" % type(keysModifiers) )
			#raise Exception('list expected for keys modifiers')
		if text is None: 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "text argument is none" )
			#raise Exception('text to type is equal to none')
		
		action =  ACTION_TYPE_TEXT
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		# escape the text 
		text = text.replace('\\', r'\\')
		
		code = [ "try:" ]
		if img is not None:
			code.append( '\tpaste(Pattern("%s.png").similar(%s), "%s")' % (imgName, similar, text) )
		else:
			if len(keysModifiers):
				if len(keys):
					code.append( '\ttype( "%s" + %s, %s)' % (text, '+'.join(keys), '+'.join(keysModifiers)) )
				else:
					code.append( '\ttype( "%s", %s)' % (text, '+'.join(keysModifiers)) )
			else:
				if len(keys):
					code.append( '\ttype( "%s" + %s)' % ( text, '+'.join(keys)) )
				else:
					code.append( '\tpaste( unicode("%s", "utf8") )' % ( text ) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')

		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		if img is not None:
			data.update( {'img': img, 'img-name': imgName} )
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=text))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def getTextClipboard(self, description='unknown'):
		"""
		Get the text present in the clipboard

		@param description: action description (default='unknown')
		@type description: string	

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_GET_CLIPBOARD
		actionId = self.getActionId()
		code = [  ]
		code.append( 'clip = Env.getClipboard()' )
		
		code.append( 'f = open("%s\\\\text.dat" % HOME_PATH, "w")')
		code.append( 'f.write( clip.encode("utf8") )' )
		code.append( 'f.close()')
		
		code.append( 'sys.exit(2)')
		data = {'action': action, 'code': "\n".join(code),  'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId,  description=description))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def getText(self, img, similar=0.70, description='unknown', mainImg=None):
		"""
		Get the text of the image passed on argument

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_GET_TEXT
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append( "try:" )
		if mainImg is not None:
			code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
			code.append( '\ttextFound = mainRegion.find(Pattern("%s.png").similar(%s)).text()' % (imgName, similar) )
		else:
			code.append( '\ttextFound = find(Pattern("%s.png").similar(%s)).text()' % (imgName, similar) )				
			
		code.append( '\tf = open("%s\\\\text.dat" % HOME_PATH, "w")')
		code.append( '\tf.write( textFound.encode("utf8") )' )
		code.append( '\tf.close()')

		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		code.append( 'else:')
		code.append( '\tsys.exit(2)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId,  description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def getTextArround(self, img, left=True, right=False, below=False, above=False, deviationPixel=50, similar=0.70, 
															description='unknown', mainImg=None):
		"""
		Get the text on arround of the image passed on argument

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param left:  find text on the left (default=True)
		@type left: boolean
		
		@param right:  find text on the right (default=False)
		@type right: boolean
		
		@param below:  find text on the below (default=False)
		@type below: boolean
		
		@param above:  find text on the above (default=False)
		@type above: boolean
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param deviationPixel: deviation in pixel (default=50)
		@type deviationPixel: integer

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_GET_TEXT
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append( "try:" )
		if mainImg is not None:
			code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
			if left:
				code.append( '\ttextFound = mainRegion.find(Pattern("%s.png").similar(%s)).left(%s).text()' % (imgName, similar, deviationPixel) )
			elif right:
				code.append( '\ttextFound = mainRegion.find(Pattern("%s.png").similar(%s)).right(%s).text()' % (imgName, similar,deviationPixel) )
			elif above:
				code.append( '\ttextFound = mainRegion.find(Pattern("%s.png").similar(%s)).above(%s).text()' % (imgName, similar,deviationPixel) )
			elif below:
				code.append( '\ttextFound = mainRegion.find(Pattern("%s.png").similar(%s)).below(%s).text()' % (imgName, similar,deviationPixel) )
			else:
				code.append( '\ttextFound = mainRegion.find(Pattern("%s.png").similar(%s)).left(%s).text()' % (imgName, similar,deviationPixel) )
		else:
			if left:
				code.append( '\ttextFound = find(Pattern("%s.png").similar(%s)).left(%s).text()' % (imgName, similar,deviationPixel) )
			elif right:
				code.append( '\ttextFound = find(Pattern("%s.png").similar(%s)).right(%s).text()' % (imgName, similar,deviationPixel) )	
			elif above:
				code.append( '\ttextFound = find(Pattern("%s.png").similar(%s)).above(%s).text()' % (imgName, similar,deviationPixel) )	
			elif below:
				code.append( '\ttextFound = find(Pattern("%s.png").similar(%s)).below(%s).text()' % (imgName, similar,deviationPixel) )					
			else:
				code.append( '\ttextFound = find(Pattern("%s.png").similar(%s)).left(%s).text()' % (imgName, similar,deviationPixel) )		
			
		code.append( '\tf = open("%s\\\\text.dat" % HOME_PATH, "w")')
		code.append( '\tf.write( textFound.encode("utf8") )' )
		code.append( '\tf.close()')
		
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		code.append( 'else:')
		code.append( '\tsys.exit(2)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId,  description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def waitImage(self, img, description='unknown', similar=0.70, timeout=10.0, mainImg=None):
		"""
		Wait the image passed as argument to appear on the screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float

		@param timeout: timeout value (threshold to 90% )
		@type timeout: float/none
		
		@return: action id
		@rtype: string	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		action =  ACTION_WAIT_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		if mainImg is not None:
			if timeout is not None:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.wait(Pattern("%s.png").similar(%s), %s)' % (imgName, similar, self.getTimeout(timeout)) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.find(Pattern("%s".png").similar(%s))' % (imgName, similar) )
		else:
			if timeout is not None:
				code.append( '\twait(Pattern("%s.png").similar(%s), %s)' % ( imgName, similar, self.getTimeout(timeout)) )
			else:
				code.append( '\tfind(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId,  description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def waitClickImage(self, img, description='unknown', similar=0.70, timeout=10.0, mainImg=None, findAll=False):
		"""
		Find the image to appear on the screen and performs a mouse click on the image passed as argument,
		Search the image on all screen by default

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: timeout value (default=10.0)  (threshold to 90% )
		@type timeout: float/none
		
		@param findAll: find all image and click on it
		@type findAll: boolean	
		
		@return: action id
		@rtype: string	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		action =  ACTION_WAIT_CLICK_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		if mainImg is not None:
			if findAll:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\telements = mainRegion.findAll(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if findAll:
				code.append( '\telements = findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				if timeout is not None:
					code.append( '\twait(Pattern("%s.png").similar(%s), %s)' % (imgName, similar, self.getTimeout(timeout)) )
				else:
					code.append( '\tfind(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tclick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def findImage(self, img, description='unknown', similar=0.70, timeout=None, mainImg=None):
		"""
		Find the image passed as argument on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float

		@param timeout: timeout value (default=None)  (threshold to 90% )
		@type timeout: float/none
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_FIND_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
				
		code = [ "try:" ]
		if mainImg is not None:
			if timeout is not None:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.wait(Pattern("%s.png").similar(%s), %s)' % (mgName, similar, self.getTimeout(timeout)) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.find(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if timeout is not None:
				code.append( '\twait(Pattern("%s.png").similar(%s), %s)' % (imgName, similar, self.getTimeout(timeout)) )
			else:
				code.append( '\tfind(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId,  description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def dontFindImage(self, img, description='unknown', similar=0.70, timeout=None, mainImg=None):
		"""
		Don't find the image passed as argument on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float

		@param timeout: timeout value (default=None)  (threshold to 90% )
		@type timeout: float/none
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_DONT_FIND_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()

		code = [ "try:" ]
		if mainImg is not None:
			if timeout is not None:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.wait(Pattern("%s.png").similar(%s), %s)' % (imgName, similar, self.getTimeout(timeout)) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.find(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if timeout is not None:
				code.append( '\twait(Pattern("%s.png").similar(%s), %s)' % (imgName, similar, self.getTimeout(timeout)) )
			else:
				code.append( '\tfind(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( '\tsys.exit(1)')
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName,  'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId,  description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def findClickImage(self, img, description='unknown', similar=0.70, timeout=None, mainImg=None, findAll=False):
		"""
		Find the image and performs a mouse click on the image passed as argument, search the image on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: timeout value (default=None)  (threshold to 90% )
		@type timeout: float/none
		
		@param findAll: find all image and click on it
		@type findAll: boolean	
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_FIND_CLICK_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()

		code = [ "try:" ]
		if mainImg is not None:
			if findAll:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\telements = mainRegion.findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if findAll:
				code.append( '\telements = findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				if timeout is not None:
					code.append( '\twait(Pattern("%s.png").similar(%s), %s)' % (imgName, similar, self.getTimeout(timeout)) )
				else:
					code.append( '\tfind(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tclick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def countWord(self, word, locX=0, locY=0, locW=0, locH=0, description='unknown', all=False):
		"""
		Count word passed as argument, 
		Search the word on the rectangle provided or on all screen

		@param word: word to find
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param description: word name (default='unknown')
		@type description: string	

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_COUNT_WORD
		actionId = self.getActionId()

		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append( 'HOME_PATH = "__PATH__"' )
		code.append( "count=0" )

		if locX==0 and locY==0 and locW==0 and locH==0:
			code.append( "region = Region(Screen().getBounds())" )
		else:
			code.append( "region = Region(%s, %s, %s, %s)" % (locX, locY, locW, locH) )			
		code.append( "matches = region.listText()" )
		code.append( "for m in matches:" )
		code.append( '\tif "%s" in m.getText().encode("utf8"):' %  word)
		code.append( "\t\tcount += 1" )
		
		code.append( 'f = open("%s\\\\text.dat" % HOME_PATH, "w")')
		code.append( 'f.write( "%s" % count )' )
		code.append( 'f.close()')
		code.append( 'sys.exit(2)')

		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=word))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def clickWord(self, word, locX=0, locY=0, locW=0, locH=0, description='unknown', all=False):
		"""
		Perform a mouse click on the word passed as argument, 
		Search the word on the rectangle provided or on all screen

		@param word: word to find
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param description: word name (default='unknown')
		@type description: string	

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_CLICK_WORD
		actionId = self.getActionId()

		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append("try:")
		if locX==0 and locY==0 and locW==0 and locH==0:
			code.append( "\tregion = Region(Screen().getBounds())" )
		else:
			code.append( "\tregion = Region(%s, %s, %s, %s)" % (locX, locY, locW, locH) )			
		code.append( "\tmatches = region.listText(); matched = False;" )
		code.append( "\twords = []" )
		code.append( "\tfor m in matches:" )
		code.append( '\t\twords.append(m.getText().encode("utf8"))')
		code.append( '\t\tif "%s" in m.getText().encode("utf8"):' %  word)
		code.append( "\t\t\tmatched = True" )
		code.append( "\t\t\tclick(m)" )
		if not all:
			code.append( "\t\t\tbreak" )
		code.append( "\tif not matched: raise Exception(words)" )

		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')

		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=word))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def doubleClickWord(self, word, locX=0, locY=0, locW=0, locH=0, description='unknown', all=False):
		"""
		Perform a mouse double click on the word passed as argument, 
		Search the word on the rectangle provided or on all screen

		@param word: word to find
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param description: word name (default='unknown')
		@type description: string	

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_DOUBLE_CLICK_WORD
		actionId = self.getActionId()
		
		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append("try:")
		if locX==0 and locY==0 and locW==0 and locH==0:
			code.append( "\tregion = Region(Screen().getBounds())" )
		else:
			code.append( "\tregion = Region(%s, %s, %s, %s)" % (locX, locY, locW, locH) )			
		code.append( "\tmatches = region.listText(); matched = False;" )
		code.append( "\tfor m in matches:" )
		code.append( '\t\tif "%s" in m.getText().encode("utf8"):' %  word)
		code.append( "\t\t\tmatched = True" )
		code.append( "\t\t\tdoubleClick(m)" )
		if not all:
			code.append( "\t\t\tbreak" )
		code.append( "\tif not matched: raise Exception()" )

		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=word))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def rightClickWord(self, word, locX=0, locY=0, locW=0, locH=0, description='unknown', all=False):
		"""
		Perform a mouse right click on the word passed as argument, 
		Search the word on the rectangle provided or on all screen

		@param word: word to find
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param description: word name (default='unknown')
		@type description: string	

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_RIGHT_CLICK_WORD
		actionId = self.getActionId()
		
		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append("try:")
		if locX==0 and locY==0 and locW==0 and locH==0:
			code.append( "\tregion = Region(Screen().getBounds())" )
		else:
			code.append( "\tregion = Region(%s, %s, %s, %s)" % (locX, locY, locW, locH) )			
		code.append( "\tmatches = region.listText(); matched = False;" )
		code.append( "\tfor m in matches:" )
		code.append( '\t\tif "%s" in m.getText().encode("utf8"):' %  word)
		code.append( "\t\t\tmatched = True" )
		code.append( "\t\t\trightClick(m)" )
		if not all:
			code.append( "\t\t\tbreak" )
		code.append( "\tif not matched: raise Exception()" )

		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=word))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def waitWord(self, word, locX=0, locY=0, locW=0, locH=0, description='unknown', timeout=10.0 ):
		"""
		Perform a mouse click on the word passed as argument.
		Search the word on the rectangle provided or on all screen

		@param word: word to find
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param description: word name (default='unknown')
		@type description: string	

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_WAIT_WORD
		actionId = self.getActionId()
		
		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append("import time")
		code.append("try:")
		code.append("\tmatched = False; timeout = False; maxtime = (%s*90)/100;" % timeout)
		code.append("\tstartTime = time.time()")
		if locX==0 and locY==0 and locW==0 and locH==0:
			code.append( "\tregion = Region(Screen().getBounds())" )
		else:
			code.append( "\tregion = Region(%s, %s, %s, %s)" % (locX, locY, locW, locH) )			
		code.append("\twhile ((not matched) and (not timeout)):")
		code.append("\t\ttime.sleep(0.1)")
		code.append("\t\tif (time.time() - startTime) >= maxtime:")
		code.append("\t\t\ttimeout = True")

		code.append( "\t\twords = []" )
		code.append( "\t\tmatches = region.listText(); " )
		code.append( "\t\tfor m in matches:" )
		code.append( '\t\t\twords.append(m.getText().encode("utf8"))')
		code.append( '\t\t\tif "%s" in m.getText().encode("utf8"):' %  word)
		code.append( "\t\t\t\tmatched = True" )
		code.append( "\tif timeout: raise Exception(words)" )
		code.append( "\tif not matched: raise Exception(words)" )
		code.append( "\tif matched: print(\"OK\")" )

		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=word))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def waitClickWord(self, word, locX=0, locY=0, locW=0, locH=0, description='unknown', timeout=10.0 ):
		"""
		Perform a mouse click on the word passed as argument.
		Search the word on the rectangle provided or on all screen

		@param word: word to find
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param description: word name (default='unknown')
		@type description: string	
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_WAIT_CLICK_WORD
		actionId = self.getActionId()
		
		code = [ "Settings.OcrTextSearch = True" ]
		code.append( "Settings.OcrTextRead = True" )
		code.append("import time")
		code.append("try:")
		code.append("\tmatched = False; timeout = False; maxtime = (%s*80)/100;" % timeout)
		code.append("\tstartTime = time.time()")
		if locX==0 and locY==0 and locW==0 and locH==0:
			code.append( "\tregion = Region(Screen().getBounds())" )
		else:
			code.append( "\tregion = Region(%s, %s, %s, %s)" % (locX, locY, locW, locH) )			
		code.append("\twhile ((not matched) and (not timeout)):")
		code.append("\t\ttime.sleep(0.1)")
		code.append("\t\tif (time.time() - startTime) >= maxtime:")
		code.append("\t\t\ttimeout = True")
		
		code.append( "\t\twords = []" )
		code.append( "\t\tmatches = region.listText(); " )
		code.append( "\t\tfor m in matches:" )
		code.append( '\t\t\twords.append(m.getText().encode("utf8"))')
		code.append( '\t\t\tif "%s" in m.getText().encode("utf8"):' %  word)
		code.append( "\t\t\t\tmatched = True" )
		code.append( "\t\t\t\tclick(m)" )
		code.append( "\tif timeout: raise Exception(words)" )
		code.append( "\tif not matched: raise Exception(words)" )
		code.append( "\tif matched: print(\"OK\")" )

		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, text=word))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def mouseWheelDown(self, steps=1,  description='unknown'):
		"""
		Mouse wheel down
		
		@param steps:  an integer indicating the amoung of wheeling (default=1)
		@type steps: integer

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_WHEEL_DOWN
		actionId = self.getActionId()
		code = [ "try:" ]
		code.append( '\twheel(WHEEL_DOWN, %s)' % (steps)  )
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, steps=steps))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def mouseWheelUp(self, steps=1,  description='unknown'):
		"""
		Mouse wheel up
		
		@param steps:  an integer indicating the amoung of wheeling (default=1)
		@type steps: integer

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_WHEEL_UP
		actionId = self.getActionId()
		code = [ "try:" ]
		code.append( '\twheel(WHEEL_UP, %s)' % (steps)  )
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, steps=steps))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def rightClickPosition(self, toX=0, toY=0,  description='unknown'):
		"""
		Right click on position x and y
		
		@param toY: position y (in pixel)
		@type toY: integer
		
		@param toX: position x (in pixel)
		@type toX: integer
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_RIGHT_CLICK_POSITION
		actionId = self.getActionId()
		code = [ "try:" ]
		code.append( '\trightClick(Location(%s,%s))' % (toX, toY )  )
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, x=toX, y=toY))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def clickPosition(self, toX=0, toY=0,  description='unknown'):
		"""
		Click on position x and y
		
		@param toY: position y (in pixel)
		@type toY: integer
		
		@param toX: position x (in pixel)
		@type toX: integer
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_CLICK_POSITION
		actionId = self.getActionId()
		code = [ "try:" ]
		code.append( '\tclick(Location(%s,%s))' % (toX, toY )  )
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, x=toX, y=toY))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def doubleClickPosition(self, toX=0, toY=0,  description='unknown'):
		"""
		Double click on position x and y
		
		@param toY: position y (in pixel)
		@type toY: integer
		
		@param toX: position x (in pixel)
		@type toX: integer
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_DOUBLE_CLICK_POSITION
		actionId = self.getActionId()
		code = [ "try:" ]
		code.append( '\tdoubleClick(Location(%s,%s))' % (toX, toY )  )
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')	
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, x=toX, y=toY))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def mouseMovePosition(self, toX=0, toY=0,  description='unknown'):
		"""
		Move on position x and y
		
		@param toY: position y (in pixel)
		@type toY: integer
		
		@param toX: position x (in pixel)
		@type toX: integer
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_MOVE_POSITION
		actionId = self.getActionId()
		code = [ "try:" ]
		code.append( '\thover(Location(%s,%s))' % (toX, toY )  )
		code.append( 'except Exception, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'action-id': actionId }
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, x=toX, y=toY))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def dragDropImage(self, img, description='unknown', toY=0, toX=0, similar=0.70, mainImg=None):
		"""
		Drag and drop the image passed as argument, search the image on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find in first
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param toY: drop image to the top or bottom (in pixel)
		@type toY: integer
		
		@param toX: drop image to the left or right (in pixel)
		@type toX: integer
		
		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_DRAGDROP_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()

		code = [ "try:" ]
		
		if mainImg is not None:
			code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
			code.append( '\tfromImg = mainRegion.find(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			code.append( '\tdragDrop(fromImg, Location(fromImg.x + %s, fromImg.y + %s))' % (toX, toY )  )
		else:
			code.append( '\tfromImg = find(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			code.append( '\tdragDrop(fromImg, Location(fromImg.x + %s, fromImg.y + %s))' % (toX, toY )  )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description,
													img=img, length=str(len(img)), mainImg=mainImg, x=toX, y=toY))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	@doc_public
	def hoverImage(self, img, description='unknown', similar=0.70, mainImg=None):
		"""
		Perform a mouse hover on the image passed as argument, search the image on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find in first
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_HOVER_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()

		code = [ "try:" ]
		if mainImg is not None:
			code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
			code.append( '\tmainRegion.hover(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			code.append( '\thover(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
		
	@doc_public
	def clickImage(self, img, description='unknown', similar=0.70, mainImg=None, findAll=False):
		"""
		Perform a mouse click on the image passed as argument, search the image on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find in first
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@param findAll: find all image and click on it
		@type findAll: boolean	
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_CLICK_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		if mainImg is not None:
			if findAll:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\telements = mainRegion.findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.click(Pattern("%s.png").similar(%s))' % (imgName, similar ) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if findAll:
				code.append( '\telements = findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.click(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\tclick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)' )
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName			
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId

	@doc_public
	def doubleClickImage(self, img, description='unknown', similar=0.70, mainImg=None, findAll=False):
		"""
		Perform a mouse click on the image passed as argument, search the image on all screen

		@param img: image to find
		@type img: image	

		@param mainImg: main image to find in first
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	
	
		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param findAll: find all image and double click on it
		@type findAll: boolean	
		
		@return: action id
		@rtype: string	
		"""
		action =  ACTION_DOUBLE_CLICK_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		if mainImg is not None:
			if findAll:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\telements = mainRegion.findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.doubleClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.doubleClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if findAll:
				code.append( '\telements = findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.doubleClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\tdoubleClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)' )
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, 
												img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId

	@doc_public
	def rightClickImage(self, img, description='unknown', similar=0.70, mainImg=None, findAll=False):
		"""
		Perform a mouse right click on the image passed as argument, search the image on all screen

		@param img: image to find
		@type img: image		

		@param mainImg: main image to find in first
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	
		
		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param findAll: find all image and right click on it
		@type findAll: boolean	
		
		@return: action id
		@rtype: string
		"""
		action =  ACTION_RIGHT_CLICK_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		if mainImg is not None:
			if findAll:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\telements = mainRegion.findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.rightClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
				code.append( '\tmainRegion.rightClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		else:
			if findAll:
				code.append( '\telements = findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
				code.append( '\tfor el in elements:' )
				code.append( '\t\tel.rightClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			else:
				code.append( '\trightClick(Pattern("%s.png").similar(%s))' % (imgName, similar) )
		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		code.append( '\tsys.exit(1)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description, 
												img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId

	@doc_public
	def countImage(self,  img, description='unknown', similar=0.70, mainImg=None):
		"""
		Count the image passed as argument and returns the number of occurences
		
		@param img: image to find
		@type img: image	

		@param mainImg: main image to find in first
		@type mainImg: image/None	
		
		@param description: image name (default='unknown')
		@type description: string	

		@param similar: similar scale (default=0.70)
		@type similar: float

		@return: action id
		@rtype: string	
		"""
		action =  ACTION_COUNT_IMAGE
		actionId = self.getActionId()
		
		#generate rando name
		imgName = "%s" % uuid.uuid4()
		mainImgName =  "%s" % uuid.uuid4()
		
		code = [ "try:" ]
		code.append( '\tHOME_PATH = "__PATH__"' )
		code.append( '\tcount = 0' )
		if mainImg is not None:
			code.append( '\tmainRegion = find(Pattern("%s.png").similar(%s))' % (mainImgName, similar) )
			code.append( '\telements = mainRegion.findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			code.append( '\tfor el in elements:' )
			code.append( '\t\tcount +=1')
		else:
			code.append( '\telements = findAll(Pattern("%s.png").similar(%s))' % (imgName, similar) )
			code.append( '\tfor el in elements:' )
			code.append( '\t\tcount +=1' )

		code.append( 'except FindFailed, e:')
		code.append( '\tf = open("%s\\\\debug.log" % HOME_PATH, "w")')
		code.append( '\tf.write( "debug: %s" % e)' )
		code.append( '\tf.close()')
		
		code.append( 'f = open("%s\\\\text.dat" % HOME_PATH, "w")')
		code.append( 'f.write( "%s" % count )' )
		code.append( 'f.close()')
		code.append( 'sys.exit(2)')
		
		data = {'action': action, 'code': "\n".join(code), 'img': img, 'img-name': imgName, 'action-id': actionId }
		if mainImg is not None:
			data['main-img'] = mainImg
			data['main-img-name'] = mainImgName
			
		self.sendNotifyToAgent(data=data)
	
		# log event
		tpl = self.encapsule(layer_gui=templates.gui(action=action, actionId=actionId, description=description,
													img=img, length=str(len(img)), mainImg=mainImg))
		self.logSentEvent( shortEvt = action, tplEvt = tpl )
		
		return actionId
	def agentIsReady(self, timeout=1.0):
		"""
		Waits to receive "agent ready" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		tpl = TestTemplatesLib.TemplateMessage()
		layer = TestTemplatesLib.TemplateLayer('AGENT')
		layer.addKey("ready", True)
		layer.addKey(name='name', data=self.cfg['agent']['name'] )
		layer.addKey(name='type', data=self.cfg['agent']['type'] )
		tpl.addLayer(layer= layer)
		evt = self.received( expected = tpl, timeout = timeout )
		return evt
	@doc_public
	def hasReceivedScreenshot(self, timeout=10.0, actionId=None):
		"""
		Wait to receive "screenshot" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=10s)
		@type timeout: float		

		@param actionId: action id
		@type actionId: string/none
		
		@return: an event matching with the template ornone otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_gui=templates.gui(action=ACTION_SCREENSHOT, actionId=actionId))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def hasReceivedText(self, timeout=10.0, actionId=None):
		"""
		Wait to receive "text" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=10s)
		@type timeout: float		

		@param actionId: action id
		@type actionId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_gui=templates.gui(action=ACTION_GET_TEXT, actionId=actionId))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
	@doc_public
	def hasReceivedCount(self, timeout=10.0, actionId=None):
		"""
		Wait to receive "count" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=10s)
		@type timeout: float		

		@param actionId: action id
		@type actionId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_gui=templates.gui(action=ACTION_COUNT_IMAGE, actionId=actionId))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
	@doc_public
	def isActionAccepted(self, timeout=10.0, actionName=None, actionId=None):
		"""
		Wait to receive "action accepted" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=10s)
		@type timeout: float		

		@param actionName:  name action
		@type actionName: string/none

		@param actionId: action id
		@type actionId: string/none
		
		@return: an event matching with the template or none otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_gui=templates.gui(action=actionName, actionId=actionId, result=ACTION_OK ))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
	@doc_public
	def doWaitImage(self, image, region=None,  similar=0.70, timeout=10.0):
		"""
		Wait the image passed as argument to appear on the screen

		@param image: image to find
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.waitImage(img=image, description='unknown', similar=similar, mainImg=region, timeout=timeout)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_WAIT_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True		
	@doc_public
	def doWaitClickImage(self, image, region=None,  similar=0.70, timeout=10.0, onAll=False):
		"""
		Wait the image passed as argument to appear on the screen and click on it

		@param image: image to find and click on it
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param onAll: find all image and click on it
		@type onAll: boolean	
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.waitClickImage(img=image, description='unknown', similar=similar, mainImg=region, timeout=timeout)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_WAIT_CLICK_IMAGE, actionId=actionId)
		if actionRet is  None:
			return False
		else:
			return True
	@doc_public
	def doFindImage(self, image, region=None,  similar=0.70, timeout=10.0):
		"""
		Find the image passed as argument on the screen

		@param image: image to find
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.findImage(img=image, description='unknown', similar=similar, mainImg=region)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_FIND_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True		
			
	@doc_public
	def doFindClickImage(self, image, region=None,  similar=0.70, timeout=10.0, onAll=False):
		"""
		Find the image passed as argument on the screen and click on it

		@param image: image to find and click on it
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param onAll: find all image and click on it
		@type onAll: boolean	
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.findClickImage(img=image, description='unknown', similar=similar, mainImg=region)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_FIND_CLICK_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True

	@doc_public
	def doClickImage(self, image, region=None,  similar=0.70, onAll=False, timeout=10.0):
		"""
		Do a click on the image passed as argument

		@param image: image to find and click on it
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@param onAll: find all image and click on it
		@type onAll: boolean	
		
		@param timeout: time max to wait to receive click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.clickImage(img=image, description='unknown', similar=similar, mainImg=region, findAll=onAll)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_CLICK_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True
	@doc_public
	def doDoubleClickImage(self, image, region=None,  similar=0.70, onAll=False, timeout=10.0):
		"""
		Do a double click on the image passed as argument

		@param image: image to find and click on it
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@param onAll: find all image and click on it
		@type onAll: boolean	
		
		@param timeout: time max to wait to receive double click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.doubleClickImage(img=image, description='unknown', similar=similar, mainImg=region, findAll=onAll)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_DOUBLE_CLICK_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True
	@doc_public
	def doRightClickImage(self, image, region=None,  similar=0.70, onAll=False, timeout=10.0):
		"""
		Do a right click on the image passed as argument

		@param image: image to find and click on it
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@param onAll: find all image and click on it
		@type onAll: boolean	
		
		@param timeout: time max to wait to receive right click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.rightClickImage(img=image, description='unknown', similar=similar, mainImg=region, findAll=onAll)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_RIGHT_CLICK_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True			
	@doc_public
	def doClickWord(self, word, locX=0, locY=0, locW=0, locH=0, timeout=10.0):
		"""
		Do a click on the word passed as argument
		Search the word on the rectangle provided or on all screen

		@param word: word to find and click on it
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param timeout: time max to wait to receive click word event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.clickWord(word=word, locX=locX, locY=locY, locW=locW, locH=locH)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_CLICK_WORD, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True		
	@doc_public
	def doDoubleClickWord(self, word, locX=0, locY=0, locW=0, locH=0, timeout=10.0):
		"""
		Do a double click on the word passed as argument
		Search the word on the rectangle provided or on all screen

		@param word: word to find and click on it
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param timeout: time max to wait to receive click word event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.doubleClickWord(word=word, locX=locX, locY=locY, locW=locW, locH=locH)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_DOUBLE_CLICK_WORD, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True		
	@doc_public
	def doRightClickWord(self, word, locX=0, locY=0, locW=0, locH=0, timeout=10.0):
		"""
		Do a double click on the word passed as argument
		Search the word on the rectangle provided or on all screen

		@param word: word to find and click on it
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.rightClickWord(word=word, locX=locX, locY=locY, locW=locW, locH=locH)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_RIGHT_CLICK_WORD, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True		
	@doc_public
	def doWaitWord(self,  word, locX=0, locY=0, locW=0, locH=0, timeout=10.0):
		"""
		Wait the word passed as argument to appear on the screen
		Search the word on the rectangle provided or on all screen

		@param word: word to find and click on it
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.waitWord(word=word, locX=locX, locY=locY, locW=locW, locH=locH, description='unknown',  timeout=timeout)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_WAIT_WORD, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True		
	@doc_public
	def doWaitClickWord(self, word, locX=0, locY=0, locW=0, locH=0, timeout=10.0):
		"""
		Wait the word passed as argument to appear on the screen and click on it
		Search the word on the rectangle provided or on all screen

		@param word: word to find and click on it
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@param timeout: time max to wait to receive find image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.waitClickWord(word=word, locX=locX, locY=locY, locW=locW, locH=locH, timeout=timeout)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_WAIT_CLICK_WORD, actionId=actionId)
		if actionRet is  None:
			return False
		else:
			return True
	@doc_public
	def doTakeScreenshot(self, timeout=10.0):
		"""
		Take a screenshot of the screen

		@param timeout: time max to wait to receive screenshot event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.takeScreenshot()
		actionRet = self.hasReceivedScreenshot(timeout=timeout, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True					
	@doc_public
	def doTypeText(self, text='', keys=[], keysModifiers=[], image=None, similar=0.70, timeout=10.0):
		"""
		Type the text on the image passed as argument

		@param text: text to type
		@type text: string	
		
		@param image: image to find
		@type image: image/none	

		@param timeout: time max to wait to receive type text event in second (default=10s)
		@type timeout: float		

		@param similar: similar scale (default=0.70)
		@type similar: float
	
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.typeText(text=text, keys=keys, keysModifiers=keysModifiers, img=image, description='unknown', similar=similar)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_TYPE_TEXT, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True			
	@doc_public
	def doTypeShorcut(self, key=None, modifier=None, special=None, other=None, timeout=10.0):
		"""
		Type shortcut with keyboard
		CTRL +ALT+DELETE cannot be typed simulated, only on the real keyboard.

		@param key: SutAdapters.GUI.MOD_KEY_ALT | SutAdapters.GUI.MOD_KEY_CMD | SutAdapters.GUI.MOD_KEY_CTRL | SutAdapters.GUI.MOD_KEY_META | SutAdapters.GUI.MOD_KEY_SHIFT | SutAdapters.GUI.MOD_KEY_WIN
		@type key: strconstant/none			
	
		@param modifier: SutAdapters.GUI.MOD_KEY_ALT | SutAdapters.GUI.MOD_KEY_CMD | SutAdapters.GUI.MOD_KEY_CTRL | SutAdapters.GUI.MOD_KEY_META | SutAdapters.GUI.MOD_KEY_SHIFT | SutAdapters.GUI.MOD_KEY_WIN
		@type modifier: strconstant/none						

		@param special: SutAdapters.GUI.KEY_ENTER | SutAdapters.GUI.KEY_TAB | SutAdapters.GUI.KEY_ESC | SutAdapters.GUI.KEY_BACKSPACE | SutAdapters.GUI.KEY_DELETE | SutAdapters.GUI.KEY_INSERT | SutAdapters.GUI.KEY_SPACE | SutAdapters.GUI.KEY_HOME | SutAdapters.GUI.KEY_END | SutAdapters.GUI.KEY_LEFT | SutAdapters.GUI.KEY_RIGHT | SutAdapters.GUI.KEY_DOWN | SutAdapters.GUI.KEY_UP | SutAdapters.GUI.KEY_PAGE_DOWN | SutAdapters.GUI.KEY_UP | SutAdapters.GUI.KEY_F1 | SutAdapters.GUI.KEY_F2 | SutAdapters.GUI.KEY_F3 | SutAdapters.GUI.KEY_F4 | SutAdapters.GUI.KEY_F5 | SutAdapters.GUI.KEY_F6 | SutAdapters.GUI.KEY_F7 | SutAdapters.GUI.KEY_F8 | SutAdapters.GUI.KEY_F9 | SutAdapters.GUI.KEY_F10 | SutAdapters.GUI.KEY_F11 | SutAdapters.GUI.KEY_F12 | SutAdapters.GUI.KEY_F13 | SutAdapters.GUI.KEY_F14 | SutAdapters.GUI.KEY_F15 | SutAdapters.GUI.KEY_PRINTSCREEN | SutAdapters.GUI.KEY_PAUSE | SutAdapters.GUI.KEY_CAPS_LOCK | SutAdapters.GUI.KEY_SCROLL_LOCK | SutAdapters.GUI.KEY_NUM_LOCK | SutAdapters.GUI.KEY_NUM0 | SutAdapters.GUI.KEY_NUM1 | SutAdapters.GUI.KEY_NUM2 | SutAdapters.GUI.KEY_NUM3 | SutAdapters.GUI.KEY_NUM4 | SutAdapters.GUI.KEY_NUM5 | SutAdapters.GUI.KEY_NUM6 | SutAdapters.GUI.KEY_NUM7 | SutAdapters.GUI.KEY_NUM8 | SutAdapters.GUI.KEY_NUM9 | SutAdapters.GUI.KEY_SEPARATOR | SutAdapters.GUI.KEY_ADD | SutAdapters.GUI.KEY_MINUS | SutAdapters.GUI.KEY_MULTIPLY | SutAdapters.GUI.KEY_DIVIDE
		@type special: strconstant/none	
		
		@param other: all others keys
		@type other: string/none		

		@param timeout: time max to wait to receive type text event in second (default=10s)
		@type timeout: float		

		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.typeShorcut(key=key, modifier=modifier, special=special, other=other)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_TYPE_SHORTCUT, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True			
	@doc_public
	def doHoverImage(self, image, region=None,  similar=0.70, timeout=10.0):
		"""
		Do a hover on the image passed as argument

		@param image: image to find
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: time max to wait to receive click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.hoverImage(img=image, description='unknown', similar=similar, mainImg=region)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_HOVER_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True
	@doc_public
	def doCountImage(self, image, region=None,  similar=0.70, timeout=10.0):
		"""
		Count the image passed as argument and returns the number of occurences

		@param image: image to find
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: time max to wait to receive click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.countImage(img=image, description='unknown', similar=similar, mainImg=region)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_COUNT_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return actionRet.get('GUI', 'text-result')
	@doc_public
	def doCountWord(self, word, locX=0, locY=0, locW=0, locH=0, timeout=10.0):
		"""
		Count the word passed as argument and returns the number of occurences

		@param word: word to find and click on it
		@type word: string	

		@param locX: X location (default=0)
		@type locX: integer

		@param locY: Y location (default=0)
		@type locY: integer

		@param locW: width of the rectangle (default=0)
		@type locW: integer

		@param locH: height of the rectangle (default=0)
		@type locH: integer
		
		@param timeout: time max to wait to receive click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.countWord(word=word, locX=locX, locY=locY, locW=locW, locH=locH, description='unknown')
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_COUNT_WORD, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return actionRet.get('GUI', 'text-result')
	@doc_public
	def doGetClipboard(self, timeout=10.0):
		"""
		Return the clipboard content
		
		@param timeout: time max to wait to receive click image event in second (default=10s)
		@type timeout: float		
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.getTextClipboard(description='unknown')
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_GET_CLIPBOARD, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return actionRet.get('GUI', 'text-result')
	@doc_public
	def doDragDropImage(self, image, region=None,  toY=0, toX=0, similar=0.70, timeout=10.0):
		"""
		Do a drag and drop off the image passed as argument

		@param image: image to find
		@type image: image	

		@param region: region to find
		@type region: image/none	

		@param similar: similar scale (default=0.70)
		@type similar: float
		
		@param timeout: time max to wait to receive click image event in second (default=10s)
		@type timeout: float		
		
		@param toY: drop image to the top or bottom (in pixel)
		@type toY: integer
		
		@param toX: drop image to the left or right (in pixel)
		@type toX: integer
		
		@return: True if click is OK, false otherwise
		@rtype: boolean	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		actionId = self.dragDropImage(img=image, description='unknown', toY=toY, toX=toX, 
																								similar=similar, mainImg=region)
		actionRet = self.isActionAccepted(timeout=timeout, actionName=ACTION_DRAGDROP_IMAGE, actionId=actionId)
		if actionRet is None:
			return False
		else:
			return True