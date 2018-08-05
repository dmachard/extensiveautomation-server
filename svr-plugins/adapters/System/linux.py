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

try:
	import StringIO
except ImportError: # python3 support
	import io as StringIO

import csv
import os 

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

try:
	import templates
except ImportError: # python3 support
	from . import templates

__NAME__="""LINUX"""

GET_OS='Os'
GET_HOSTNAME='Hostname'
GET_PROCESSES='Processes'
GET_UPTIME='Uptime'
GET_CPU_LOAD='Cpu Load'
GET_CPU_INFO='Cpu Info'
GET_DISKS='Disks'
GET_SYS_INFO='System Info'
GET_MEM_USAGE='Mem Usage'
GET_KERNEL='Kernel'

EXEC_CMD='Command'

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='command'

class Linux(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, agent, name=None, debug=False, shared=False, logEventSent=True, logEventReceived=True):
		"""
		Linux adapter
		Works with an agent only

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param agent: agent to use
		@type agent: string

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug,
																									realname=name, agentSupport=True, 
																									agent=agent, shared=shared,
																									caller=TestAdapterLib.caller(),
																									agentType=AGENT_TYPE_EXPECTED)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.parent = parent
		self.cfg = {}
		self.cfg['agent'] = agent
		self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = True
		
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		self.prepareAgent(data={'shared': shared})
		if self.agentIsReady(timeout=30) is None:
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
#			raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
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
			try:
				raw = data['result']
				
				tplLin = templates.linux(event='response')
				tplLin.addRaw(raw)			
	
				if data['get'] == EXEC_CMD:
					Rsp = EXEC_CMD
					tplLin.addKey(name='get', data=Rsp)
					tplLin.addKey(name='result', data=raw)
	
				if data['get'] == GET_HOSTNAME:
					Rsp = GET_HOSTNAME
					tplLin.addKey(name='get', data=Rsp)
					tplLin.addKey(name='hostname', data=raw.splitlines()[0] )
	
				if data['get'] == GET_OS:
					Rsp = GET_OS
					tplLin.addKey(name='get', data=Rsp)
					tplLin.addKey(name='os', data=raw)
	
				if data['get'] == GET_KERNEL:
					Rsp = GET_KERNEL
					tplLin.addKey(name='get', data=Rsp)
					tplLin.addKey(name='kernel', data=raw)
					
				if data['get'] == GET_CPU_INFO:
					Rsp = GET_CPU_INFO
					tplLin.addKey(name='get', data=Rsp)
					cpus = self.decodeCpuInfo(cpus=raw)
					tplLin.addKey(name='cpu-count', data=str(len(cpus)) )
					for cpu, details in cpus.items():
						tplCpu = TestTemplatesLib.TemplateLayer(name='')
						for k,v in details.items():
							tplCpu.addKey(name=k, data=v)
						tplLin.addKey(name=cpu, data=tplCpu)
		
				if data['get'] == GET_MEM_USAGE:
					Rsp = GET_MEM_USAGE
					tplLin.addKey(name='get', data=Rsp)
					mem = self.decodeMemUsage(mem=raw)
					for k,v in mem.items():
						tplLin.addKey(name=k, data=v)
					
				if self.logEventReceived:		
					tpl = self.encapsule(linux_event=tplLin)
					tpl.addRaw(raw)
					self.logRecvEvent( shortEvt = "%s Response" % Rsp, tplEvt = tpl )					
			except Exception as e:
				self.error( 'unable to read response: %s' % str(e) )
				
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
		Waits to receive agent ready event until the end of the timeout
		
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
	def decodeMemUsage(self, mem):
		"""
		Decode raw string
		"""
		ret = { }
		for line in mem.splitlines():
			tmp_ = line.split(':')
			if tmp_[0] == 'MemTotal':
				while tmp_[1].startswith(' '):
					tmp_[1] = tmp_[1][1:]
				ret['total-physical'] = tmp_[1]
			if tmp_[0] == 'MemFree':
				while tmp_[1].startswith(' '):
					tmp_[1] = tmp_[1][1:]
				ret['free-physical'] = tmp_[1]	
			if tmp_[0] == 'SwapTotal':
				while tmp_[1].startswith(' '):
					tmp_[1] = tmp_[1][1:]
				ret['total-virtual'] = tmp_[1]
			if tmp_[0] == 'SwapFree':
				while tmp_[1].startswith(' '):
					tmp_[1] = tmp_[1][1:]
				ret['free-virtual'] = tmp_[1]			
		return ret
		
	def decodeCpuInfo(self, cpus):
		"""
		Decode raw string
		"""
		ret = { }
		for line in cpus.splitlines():				
				tmp_ = line.split(':')
				if tmp_[0].startswith('processor'):
					while tmp_[1].startswith(' '):
						tmp_[1] = tmp_[1][1:]
					cpu_id = 'cpu%s' % tmp_[1]
					ret[cpu_id] = {}
				elif tmp_[0].startswith('model name'):
					while tmp_[1].startswith(' '):
						tmp_[1] = tmp_[1][1:]
					ret[cpu_id]['model-name'] = tmp_[1]
				elif tmp_[0].startswith('cpu MHz'):
					while tmp_[1].startswith(' '):
						tmp_[1] = tmp_[1][1:]
					ret[cpu_id]['cpu-mhz'] = tmp_[1]
				elif tmp_[0].startswith('cache size'):
					while tmp_[1].startswith(' '):
						tmp_[1] = tmp_[1][1:]
					ret[cpu_id]['cache-size'] = tmp_[1]
		return ret
		
	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( 'Error received from agent: %s' % data )
		
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.debug( 'Data received from agent: %s' % data )
		
	def sendNotifyToAgent(self, data):
		"""
		"""
		self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	def encapsule(self, linux_event):
		"""
		"""
		layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
		layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
		layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=linux_event)
		return tpl
	@doc_public
	def hasReceivedResponse(self, timeout=1.0):
		"""
		Waits to receive "response" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		layer_linux=templates.linux(event='response') 
		evt = self.received( expected = self.encapsule(linux_event=layer_linux), timeout = timeout )
		return evt
		
	@doc_public
	def getHostname(self):
		"""
		Requests the host to get the hostname
		"""
		cmd = { 'cmd': "uname -n",
						'get': GET_HOSTNAME		}
		if self.logEventSent:
			layer_linux=templates.linux(get=GET_HOSTNAME, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_HOSTNAME, tplEvt = self.encapsule(linux_event=layer_linux) ) 
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def getCpuInfo(self):
		"""
		Requests the host to get the cpu info
		"""
		cmd = { 'cmd': "cat /proc/cpuinfo",
						'get': GET_CPU_INFO		}
		if self.logEventSent:
			layer_linux=templates.linux(get=GET_CPU_INFO, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_CPU_INFO, tplEvt = self.encapsule(linux_event=layer_linux) ) 
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def getMemUsage(self):
		"""
		Requests the host to get the memory usage
		"""
		__cmd__ = "cat /proc/meminfo"
		cmd = { 'cmd': __cmd__,
						'get': GET_MEM_USAGE	}
		if self.logEventSent:
			layer_linux=templates.linux(get=GET_MEM_USAGE, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_MEM_USAGE, tplEvt = self.encapsule(linux_event=layer_linux) ) 		
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def getOs(self):
		"""
		Requests the host to get the version of the operating system
		"""
		cmd = { 'cmd': "",
						'get': GET_OS	}
		if self.logEventSent:
			layer_linux=templates.linux(get=GET_OS, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_OS, tplEvt = self.encapsule(linux_event=layer_linux) ) 		
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def getKernel(self):
		"""
		Requests the host to get the version of the kernel
		"""
		cmd = { 'cmd': "uname -mrs",
						'get': GET_KERNEL	}
		if self.logEventSent:
			layer_linux=templates.linux(get=GET_KERNEL, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_KERNEL, tplEvt = self.encapsule(linux_event=layer_linux) ) 		
		self.sendNotifyToAgent(data=cmd)
	
	@doc_public
	def execCommand(self, cmd):
		"""
		Execute the command passed on argument
	
		@param cmd: command to execute
		@type cmd: string		
		"""
		cmd = { 'cmd': cmd,
						'get': EXEC_CMD	}
		if self.logEventSent:
			layer_linux=templates.linux(get=EXEC_CMD, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % EXEC_CMD, tplEvt = self.encapsule(linux_event=layer_linux) ) 		
		self.sendNotifyToAgent(data=cmd)		
		
	@doc_public
	def doGetHostname(self, timeout=1.0):
		"""
		Get the hostname and wait the reponse until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.getHostname()
		return self.hasReceivedResponse(timeout=timeout)
	@doc_public
	def doGetCpuInfo(self, timeout=1.0):
		"""
		Get the cpu info and wait the reponse until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.getCpuInfo()
		return self.hasReceivedResponse(timeout=timeout)
	@doc_public
	def doGetMemUsage(self, timeout=1.0):
		"""
		Get the memory usage and wait the reponse until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.getMemUsage()
		return self.hasReceivedResponse(timeout=timeout)
	@doc_public
	def doGetOs(self, timeout=1.0):
		"""
		Get the version of the operating system and wait the reponse until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.getOs()
		return self.hasReceivedResponse(timeout=timeout)
	@doc_public
	def doGetKernel(self, timeout=1.0):
		"""
		Get the version of the kernel and wait the reponse until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.getOs()
		return self.hasReceivedResponse(timeout=timeout)
	@doc_public
	def doCommand(self, cmd, timeout=1.0):
		"""
		Execute the command passed on argument and wait the reponse until the end of the timeout
		
		@param cmd: command to execute
		@type cmd: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		self.execCommand(cmd=cmd)
		return self.hasReceivedResponse(timeout=timeout)