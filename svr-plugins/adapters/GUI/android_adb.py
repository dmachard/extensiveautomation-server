#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import threading
import json

try:
	import templates
except ImportError: # python3 support
	from . import templates

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

__NAME__="""ADB"""


ADB_ACTION_OK = "OK"
ADB_ACTION_FAILED = "FAILED"

AGENT_EVENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='adb'

ADB_ACTION = "adb"
ADB_WAKEUP_ACTION = "wakeUp"
ADB_SLEEP_ACTION = "sleep"
ADB_OPENNOTIFICATION_ACTION = "openNotification"
ADB_OPENQUICKSETTINGS_ACTION = "openQuickSettings"
ADB_DEVICEINFO_ACTION = "deviceInfo"
ADB_CLICK_ACTION = "click"
ADB_SWIPE_ACTION = "swipe"
ADB_DRAG_ACTION = "drag"
ADB_FREEZEROTATION_ACTION = "freezeRotation"
ADB_PRESSKEY_ACTION = "pressKey"
ADB_PRESSKEYCODE_ACTION = "pressKeyCode"
ADB_UNLOCK_ACTION = "unlock"
# todo, clear cache ?
# todo, kill app

JSON_CLICK_ACTION="click"
JSON_EXIST_ACTION="exist"
JSON_LONGCLICK_ACTION="longClick"
JSON_CLEARTEXT_ACTION = "clearTextField"
JSON_GETTEXT_ACTION = "getText"
JSON_SETTEXT_ACTION = "setText"
JSON_NOTIFICATION_ACTION = "openNotification"
JSON_SETTINGS_ACTION = "openQuickSettings"
JSON_WAITELEMENT_ACTION = "waitForExists"
JSON_SCREENSHOT_ACTION = "takeScreenshot"
JSON_DRAG_ACTION = "drag"
JSON_SWIPE_ACTION = "swipe"
JSON_DRAGELEMENT_ACTION = "dragTo"
JSON_FREEZEROTATION_ACTION = "freezeRotation"
JSON_SETORIENTATION_ACTION = "setOrientation"


ADB_KEY_HOME = "home"
ADB_KEY_BACK = "back"
ADB_KEY_LET = "left"
ADB_KEY_RIGHT = "right"
ADB_KEY_UP = "up"
ADB_KEY_DOWN = "down"
ADB_KEY_CENTER = "center"
ADB_KEY_MENU = "menu"
ADB_KEY_SEARCH = "search"
ADB_KEY_ENTER = "enter"
ADB_KEY_DELETE = "delete"
ADB_KEY_DEL = "del"
ADB_KEY_RECENT = "recent"
ADB_KEY_VOLUMEUP = "volume_up"
ADB_KEY_VOLUMEDOWN = "volume_down"
ADB_KEY_VOLUMEMUTE = "volume_mute"
ADB_KEY_CAMERA = "camera"
ADB_KEY_POWER = "power"

ADB_KEYCODE_NUM_LOCK = 143
ADB_KEYCODE_APP_SWITCH = 187
ADB_KEYCODE_BACK = 4
ADB_KEYCODE_BACKSLASH  = 73
ADB_KEYCODE_BRIGHTNESS_DOWN = 220
ADB_KEYCODE_BRIGHTNESS_UP = 221
ADB_KEYCODE_CLEAR = 28
ADB_KEYCODE_COMMA = 55
ADB_KEYCODE_ENTER  = 66
ADB_KEYCODE_ESCAPE  = 111
ADB_KEYCODE_SPACE  = 62
ADB_KEYCODE_STAR = 17

def U(x):
    if sys.version_info.major == 2:
        return x.decode('utf-8') if type(x) is str else x
    elif sys.version_info.major == 3:
        return x
        
class Selector(dict):

    """The class is to build parameters for UiSelector passed to Android device.
    """
    __fields = {
        "text": (0x01, None),  # MASK_TEXT,
        "textContains": (0x02, None),  # MASK_TEXTCONTAINS,
        "textMatches": (0x04, None),  # MASK_TEXTMATCHES,
        "textStartsWith": (0x08, None),  # MASK_TEXTSTARTSWITH,
        "className": (0x10, None),  # MASK_CLASSNAME
        "classNameMatches": (0x20, None),  # MASK_CLASSNAMEMATCHES
        "description": (0x40, None),  # MASK_DESCRIPTION
        "descriptionContains": (0x80, None),  # MASK_DESCRIPTIONCONTAINS
        "descriptionMatches": (0x0100, None),  # MASK_DESCRIPTIONMATCHES
        "descriptionStartsWith": (0x0200, None),  # MASK_DESCRIPTIONSTARTSWITH
        "checkable": (0x0400, False),  # MASK_CHECKABLE
        "checked": (0x0800, False),  # MASK_CHECKED
        "clickable": (0x1000, False),  # MASK_CLICKABLE
        "longClickable": (0x2000, False),  # MASK_LONGCLICKABLE,
        "scrollable": (0x4000, False),  # MASK_SCROLLABLE,
        "enabled": (0x8000, False),  # MASK_ENABLED,
        "focusable": (0x010000, False),  # MASK_FOCUSABLE,
        "focused": (0x020000, False),  # MASK_FOCUSED,
        "selected": (0x040000, False),  # MASK_SELECTED,
        "packageName": (0x080000, None),  # MASK_PACKAGENAME,
        "packageNameMatches": (0x100000, None),  # MASK_PACKAGENAMEMATCHES,
        "resourceId": (0x200000, None),  # MASK_RESOURCEID,
        "resourceIdMatches": (0x400000, None),  # MASK_RESOURCEIDMATCHES,
        "index": (0x800000, 0),  # MASK_INDEX,
        "instance": (0x01000000, 0)  # MASK_INSTANCE,
    }
    __mask, __childOrSibling, __childOrSiblingSelector = "mask", "childOrSibling", "childOrSiblingSelector"

    def __init__(self, **kwargs):
        super(Selector, self).__setitem__(self.__mask, 0)
        super(Selector, self).__setitem__(self.__childOrSibling, [])
        super(Selector, self).__setitem__(self.__childOrSiblingSelector, [])
        for k in kwargs:
            self[k] = kwargs[k]

    def __setitem__(self, k, v):
        if k in self.__fields:
          if v is not None:
            super(Selector, self).__setitem__(U(k), U(v))
            super(Selector, self).__setitem__(self.__mask, self[self.__mask] | self.__fields[k][0])
        else:
            raise ReferenceError("%s is not allowed." % k)

    def __delitem__(self, k):
        if k in self.__fields:
            super(Selector, self).__delitem__(k)
            super(Selector, self).__setitem__(self.__mask, self[self.__mask] & ~self.__fields[k][0])

    def clone(self):
        kwargs = dict((k, self[k]) for k in self
                      if k not in [self.__mask, self.__childOrSibling, self.__childOrSiblingSelector])
        selector = Selector(**kwargs)
        for v in self[self.__childOrSibling]:
            selector[self.__childOrSibling].append(v)
        for s in self[self.__childOrSiblingSelector]:
            selector[self.__childOrSiblingSelector].append(s.clone())
        return selector

    def child(self, **kwargs):
        self[self.__childOrSibling].append("child")
        self[self.__childOrSiblingSelector].append(Selector(**kwargs))
        return self

    def sibling(self, **kwargs):
        self[self.__childOrSibling].append("sibling")
        self[self.__childOrSiblingSelector].append(Selector(**kwargs))
        return self

    child_selector, from_parent = child, sibling
 
class Adb(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, agent, name=None, debug=False, verbose=True, shared=False):
		"""
		Android automator throught ADB (Android debug bridge)

		@param parent: parent testcase
		@type parent: testcase
		
		@param agent: agent to use, adb type expected
		@type agent: string
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																										debug=debug, realname=name,
																										agentSupport=True, agent=agent, shared=shared,
																										showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose,
																										caller=TestAdapterLib.caller(),
																										agentType=AGENT_TYPE_EXPECTED)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		self.cfg['agent'] = agent
		self.cfg['agent-name'] = agent['name']

		self.cmdId = 0
		self.__mutexCmdId__ = threading.RLock()

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
			if data['cmd'] == AGENT_EVENT_INITIALIZED:
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
				commandResult =  data['command-result']
				commandValue =  data['command-value']
				
				result = ADB_ACTION_OK
				if commandResult: 
					result = ADB_ACTION_FAILED
				
				if isinstance(data['command-value'], dict):
					if "result" in data['command-value']:
						commandValue =  data['command-value']['result']
					
					if "error" in data['command-value']:
						commandValue =  data['command-value']['error']
						if isinstance(commandValue, dict):
							error_tpl = TestTemplates.TemplateLayer(name='')
							for k, v in commandValue.items():
								error_tpl.addKey("%s" % k, "%s" % v)
							commandValue = error_tpl
			
						result = ADB_ACTION_FAILED
				
				
				if commandName == ADB_DEVICEINFO_ACTION:
					deviceInfo = TestTemplates.TemplateLayer(name='')
					
					for k in commandValue.keys():
						deviceInfo.addKey(k, commandValue[k])
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=result, value=deviceInfo) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, result), tplEvt = tpl )
					
				elif commandName == JSON_EXIST_ACTION:
					if not commandValue:  result = ADB_ACTION_FAILED
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=result, value=commandValue) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, result), tplEvt = tpl )
					
				elif commandName == JSON_WAITELEMENT_ACTION:
					if not commandValue:  result = ADB_ACTION_FAILED
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=result, value=commandValue) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, result), tplEvt = tpl )
					
				else:
					tpl = self.encapsule(layer_gui=templates.gui(action=commandName, actionId=commandId, result=result, value=commandValue) )
					self.logRecvEvent( shortEvt = "%s [result=%s]" % (commandName, result), tplEvt = tpl )
					
			except Exception as e:
				self.error('received notify: %s' % e)
				
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
		
	def prepareAgent(self, data):
		"""
		prepare agent
		"""
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	def agentIsReady(self, timeout=1.0):
		"""
		Waits to receive ved agent ready event until the end of the timeout
		
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
		
	def getCommandId(self):
		"""
		"""
		self.__mutexCmdId__.acquire()
		self.cmdId += 1
		ret = self.cmdId
		self.__mutexCmdId__.release()
		return ret
		
	def getTimeout(self, timeout=None):
		"""
		"""
		threshold = 90 # reduce to 90% of the interval
		if timeout is None:
			return timeout
		else:
			return ((timeout*threshold) / 100 ) * 1000
	def command_json(self, cmd, params=[]):
		"""
		"""
		# prepare agent request
		cmdId = self.getCommandId()
		agentData = { 'command-id': cmdId, 'command-name':  cmd, "command-params": json.dumps(params) }

		# send command to agent
		self.debug( "request: %s" % agentData)
		self.sendNotifyToAgent(data=agentData)

		# log event
		layerParams = TestTemplates.TemplateLayer(name='')
		i = 1
		for v in params:
			layerParams.addKey("arg%s" % i, "%s" % v)
			i += 1
		
		tpl = self.encapsule(layer_gui=templates.gui(action=cmd, actionId=cmdId, parameters=layerParams))
		self.logSentEvent( shortEvt = cmd, tplEvt = tpl )
		
		return cmdId
		
	@doc_public
	def command_adb(self, params, adb='adb'):
		"""
		"""
		# prepare agent request
		cmdId = self.getCommandId()
		agentData = { 'command-id': cmdId, 'command-name':  ADB_ACTION,  'sub-command':  adb, "command-params": params}

		# send command to agent
		self.debug( "request: %s" % agentData)
		self.sendNotifyToAgent(data=agentData)

		# log event
		layerParams = TestTemplates.TemplateLayer(name=params)

		tpl = self.encapsule(layer_gui=templates.gui(action=adb, actionId=cmdId, parameters=layerParams))
		self.logSentEvent( shortEvt = "adb %s" % adb, tplEvt = tpl )
		
		return cmdId
		
	@doc_public
	def shell(self, command):
		"""
		Shell adb command
		
		@param command: command to execute
		@type command: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="shell %s" % command, adb="shell")
	
	@doc_public
	def resetApplication(self, packageName):
		"""
		Reset application according to the package name 
		Stop the app process and clear out all the stored data for that app
		
		@param packageName: package name to clean up
		@type packageName: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.shell(command="pm clear %s" % packageName)
	
	@doc_public
	def stopApplication(self, packageName):
		"""
		Stop application according to the package name

		@param packageName: package name to clean up
		@type packageName: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.shell(command="am force-stop %s" % packageName)
		
	@doc_public
	def input(self, command):
		"""
		Input adb command 
		
		@param command: command to execute
		@type command: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="shell input %s" % command, adb="input")
		
	@doc_public
	def root(self):
		"""
		Input adb command 
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="root", adb="root")

	@doc_public
	def devices(self):
		"""
		Get all connected devices
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="devices", adb="devices")
		

	@doc_public
	def unlock(self):
		"""
		Unlock the device
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="shell input keyevent 82", adb="unlock")
	@doc_public
	def lock(self):
		"""
		Lock the device, go to sleep before
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="shell input keyevent 82", adb="lock")

	@doc_public
	def reboot(self):
		"""
		Reboot the device
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="reboot", adb="reboot")
	
	@doc_public
	def recovery(self):
		"""
		Reboots the device into the recovery program
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="reboot recovery", adb="recovery")
	
	@doc_public
	def bootloader(self):
		"""
		Reboots the device into the bootloader
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="reboot bootloader", adb="bootloader")

	@doc_public
	def getLogs(self):
		"""
		Get device logs
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="logcat -d", adb="get logs")
		
	@doc_public
	def clearLogs(self):
		"""
		Clear device logs
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="logcat -c", adb="clear logs")
		
	@doc_public
	def install(self, apk):
		"""
		Install apk 
		
		@param apk: apk to install
		@type apk: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="install %s" % apk, adb="install")
		
	@doc_public
	def uninstall(self, apk):
		"""
		Uninstall apk 
		
		@param apk: apk to install
		@type apk: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="uninstall %s" % apk, adb="uninstall")
		
		
	@doc_public	
	def push(self, fromPath, toPath):
		"""
		Upload file to the device
		
		@param fromPath: path file to push
		@type fromPath: string
		
		@param toPath: to the path on the device
		@type toPath: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="push \"%s\" %s" % (fromPath,toPath), adb="push")
		
	@doc_public
	def pull(self, fromPath, toPath):
		"""
		Pull file from the device
		
		@param fromPath: path file to pull
		@type fromPath: string
		
		@param toPath: to the path on the server
		@type toPath: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_adb(params="pull \"%s\" %s" % (fromPath,toPath), adb="pull")
	@doc_public
	def wakeUp(self):
		"""
		Wake up the device
		"""
		return self.command_json(cmd=ADB_WAKEUP_ACTION)	
	@doc_public
	def sleep(self):
		"""
		Go to sleep
		"""
		return self.command_json(cmd=ADB_SLEEP_ACTION)	
	@doc_public	
	def deviceInfo(self):
		"""
		Get device info
		"""
		return self.command_json(cmd=ADB_DEVICEINFO_ACTION)	
	@doc_public
	def typeShortcut(self, shortcut):
		"""
		Type shortcut on device (home, power, etc...)
		
		@param shortcut: SutAdapters.GUI.ADB_KEY_HOME | SutAdapters.GUI.ADB_KEY_BACK | SutAdapters.GUI.ADB_KEY_LET | SutAdapters.GUI.ADB_KEY_RIGHT | SutAdapters.GUI.ADB_KEY_UP | SutAdapters.GUI.ADB_KEY_DOWN | SutAdapters.GUI.ADB_KEY_CENTER | SutAdapters.GUI.ADB_KEY_MENU | SutAdapters.GUI.ADB_KEY_SEARCH | SutAdapters.GUI.ADB_KEY_ENTER | SutAdapters.GUI.ADB_KEY_DELETE | SutAdapters.GUI.ADB_KEY_DEL | SutAdapters.GUI.ADB_KEY_RECENT | SutAdapters.GUI.ADB_KEY_VOLUMEUP | SutAdapters.GUI.ADB_KEY_VOLUMEDOWN | SutAdapters.GUI.ADB_KEY_VOLUMEMUTE | SutAdapters.GUI.ADB_KEY_CAMERA | SutAdapters.GUI.ADB_KEY_POWER
		@type shortcut: strconstant
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd='pressKey', params=[shortcut])
	@doc_public
	def typeKeyCode(self, code):
		"""
		Type key code on device
		
		@param code: key code
		@type code: integer
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd='pressKeyCode', params=[code])
	@doc_public
	def openNotification(self):
		"""
		Open notification
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_NOTIFICATION_ACTION, params=[])
	@doc_public
	def openQuickSettings(self):
		"""
		Open quick settings
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_SETTINGS_ACTION, params=[])
	@doc_public
	def clickPosition(self, x, y):
		"""
		Click on position x and y
		
		@param x: x coordinate
		@type x: integer
		
		@param y: y coordinate
		@type y: integer
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_CLICK_ACTION, params=[x,y])
	@doc_public
	def dragPosition(self, startX, startY, endX, endY):
		"""
		Drag from startX/startY to endX/endY
		
		@param startX: from x coordinate
		@type startX: integer
		
		@param startY: from y coordinate
		@type startY: integer
		
		@param endX: to x coordinate
		@type endX: integer
		
		@param endY: to y coordinate
		@type endY: integer
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_DRAG_ACTION, params=[ startX, startY, endX, endY, 40])
	@doc_public
	def freezeRotation(self):
		"""
		Freeze the rotation

		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_FREEZEROTATION_ACTION, params=[ True ])
	@doc_public
	def unfreezeRotation(self):
		"""
		Unfreeze the rotation

		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_FREEZEROTATION_ACTION, params=[ False ])
	@doc_public
	def setOrientation(self):
		"""
		Set orientation

		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_SETORIENTATION_ACTION, params=[ False ])
	@doc_public
	def dragElement(self, endX, endY, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Drag element to endX/endY

		@param endX: to x coordinate
		@type endX: integer
		
		@param endY: to y coordinate
		@type endY: integer
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none

		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_DRAGELEMENT_ACTION, params=[ Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith), endX, endY, 40])
	@doc_public
	def swipePosition(self, startX, startY, endX, endY):
		"""
		Swipe from startX/startY to endX/endY
		
		@param startX: from x coordinate
		@type startX: integer
		
		@param startY: from y coordinate
		@type startY: integer
		
		@param endX: to x coordinate
		@type endX: integer
		
		@param endY: to y coordinate
		@type endY: integer
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_SWIPE_ACTION, params=[ startX, startY, endX, endY, 100])
	@doc_public
	def waitElement(self, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None, timeout=10.0):
		"""
		Wait element during the timeout passed as argument
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none

		@param timeout: timeout value (threshold to 90% )
		@type timeout: float/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_WAITELEMENT_ACTION, params=[Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith), self.getTimeout(timeout=timeout)])
	@doc_public
	def clickElement(self, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Click on element
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_CLICK_ACTION, params=[Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith) ])
	@doc_public
	def longClickElement(self, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Long click on element
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_LONGCLICK_ACTION, params=[Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith) ])
	@doc_public
	def existElement(self, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Element exists on device
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_EXIST_ACTION, params=[Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith) ])
	@doc_public
	def clearTextElement(self, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Clear text element on device
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_CLEARTEXT_ACTION, params=[Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith) ])
	@doc_public
	def typeTextElement(self, newText, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Type text on element
		
		@param newText: text to type
		@type newText: string
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_SETTEXT_ACTION, params=[ Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith) , newText])
	@doc_public
	def getTextElement(self, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Get text on element
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@return: internal command id
		@rtype: string
		"""
		return self.command_json(cmd=JSON_GETTEXT_ACTION, params=[Selector(text=text, textContains=textContains, textStartsWith=textStartsWith, className=className,
																																									resourceId=resourceId, packageName=packageName, description=description, descriptionContains=descriptionContains, 
																																									descriptionStartsWith=descriptionStartsWith) ])
	@doc_public
	def typeText(self, text):
		"""
		Type text on device
		
		@param text: text to type
		@type text: string
		
		@return: internal command id
		@rtype: string
		"""
		return self.input(command='text %s' % text)
		
	@doc_public
	def isActionAccepted(self, timeout=10.0, actionName=None, actionId=None):
		"""
		Waits to receive "action accepted" event until the end of the timeout
		
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
		expected = self.encapsule(layer_gui=templates.gui(action=actionName, actionId=actionId, result=ADB_ACTION_OK ))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
	@doc_public
	def doWakeupUnlock(self, timeout=10.0):
		"""
		Do wake up and unlock the device
		
		@param timeout: time max to wake up and unlock in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.wakeUp()
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			cmdId = self.unlock()
			if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
				ret = False
			else:
				ret = True
		return ret
	@doc_public
	def doWakeUp(self, timeout=10.0):
		"""
		Do wake up
		
		@param timeout: time max to wake up in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.wakeUp()
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			ret = True
		return ret
	@doc_public
	def doUnlock(self, timeout=10.0):
		"""
		Do unlock the device
		
		@param timeout: time max to wake up and unlock in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.unlock()
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			ret = True
		return ret
	@doc_public
	def doSleepLock(self, timeout=10.0):
		"""
		Do sleep and lock the device
		
		@param timeout: time max to sleep and lock in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.sleep()
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			cmdId2 = self.command_adb(params="shell input keyevent 82", adb='lock')
			if self.isActionAccepted(timeout=timeout, actionId=cmdId2) is None:
				ret = False
			else:
				ret = True
		return ret
	@doc_public
	def doSleep(self, timeout=10.0):
		"""
		Do sleep the device
		
		@param timeout: time max to wake up and unlock in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.sleep()
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			ret = True
		return ret
	@doc_public
	def doReboot(self, timeout=10.0):
		"""
		Do reboot the device
		
		@param timeout: time max to wake up and unlock in second (default=30s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.reboot()
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			ret = True
		return ret
	@doc_public
	def doWaitClickElement(self, timeout=10.0, text=None, textContains=None, textStartsWith=None, description=None, descriptionContains=None, descriptionStartsWith=None,
																	className=None, resourceId=None, packageName=None):
		"""
		Do wait and click on ui element
		
		@param text: text ui element
		@type text: string/none
		
		@param textContains: text contains
		@type textContains: string/none
		
		@param textStartsWith: text starts with
		@type textStartsWith: string/none
		
		@param description: description
		@type description: string/none
		
		@param descriptionContains: the description contains
		@type descriptionContains: string/none
		
		@param descriptionStartsWith: the description startswith
		@type descriptionStartsWith: string/none
		
		@param className: class name
		@type className: string/none
		
		@param resourceId: resource id
		@type resourceId: string/none
		
		@param packageName: package name
		@type packageName: string/none
		
		@param timeout: time max to wait and click event in seconds (default=10s)
		@type timeout: float		
		
		@return: True on action OK, False otherwise
		@rtype: boolean	
		"""
		ret = True
		cmdId = self.waitElement(text=text, textContains=textContains, textStartsWith=textStartsWith, description=description,
																		descriptionContains=descriptionContains, descriptionStartsWith=descriptionStartsWith,
																	className=className, resourceId=resourceId, packageName=packageName, timeout=timeout)
		if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
			ret = False
		else:
			cmdId = self.clickElement(text=text, textContains=textContains, textStartsWith=textStartsWith, description=description, 
																descriptionContains=descriptionContains, descriptionStartsWith=descriptionStartsWith,
																	className=className, resourceId=resourceId, packageName=packageName)
			if self.isActionAccepted(timeout=timeout, actionId=cmdId) is None:
				ret = False
			else:
				ret = True
		return ret