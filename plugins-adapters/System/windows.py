#!/usr/bin/env python
# -*- coding=utf-8 -*-

# ------------------------------------------------------------------
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

import StringIO
import csv
import os 

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import templates

__NAME__="""WINDOWS"""

GET_OS='Os'
GET_HOSTNAME='Hostname'
GET_PROCESSES='Processes'
GET_UPTIME='Uptime'
GET_CPU_LOAD='Cpu Load'
GET_DISKS='Disks'
GET_SYS_INFO='System Info'
GET_MEM_USAGE='Mem Usage'

EXEC_CMD='Command'

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='command'

class Windows(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, agent, name=None, node='127.0.0.1', user='', password='', debug=False, 
								shared=False, logEventSent=True, logEventReceived=True, nodes=[] ):
		"""
		Windows adapter, based on the tool wmic
		Works with an agent only

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param agent: agent to use
		@type agent: string

		@param node: host to contact (default=127.0.0.1)
		@type node: string
		
		@param user: username (default='')
		@type user: string

		@param password: password (default='')
		@type password: string
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# check the agent
		if not isinstance(agent, dict) : 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
		if not len(agent['name']): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
		if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug,
																		realname=name, agentSupport=True, agent=agent, shared=shared)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.parent = parent
		self.cfg = {}
		self.cfg['agent'] = agent
		self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = True
		self.cfg['node'] = node
		# todo add authen  /user:"xxxx /password:"xxxx"
		self.cfg['user'] = node
		self.cfg['password'] = node
		# nodes: call server machine at once
		# /node:"server-01","server-02","server-03"
		
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
		self.debug( data )
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
				raw = data['result'].replace('\r\r\n', '\n')
				self.debug( raw )
				f = StringIO.StringIO(raw)
	
				# todo, handle error
				#			ERROR 1 =>			
				#				Node - 127.0.0.1
				#				ERROR:
				#				Description = Invalid query
				#				
				#				Node,
				
				#			ERROR 2 =>		
				#			192.168.1.253 cpu get name
				#			Node - 192.168.1.253
				#			ERROR:
				#			Description = The RPC server is unavailable.
				
				#			ERROR 3 =>	
				#			192.168.0.253 cpu get name
				#			Node - 192.168.0.253
				#			ERROR:
				#			Description = Access is denied.
				
				#			ERROR 4 =>	
				#			Invalid GET Expression.
							
				# raw format
				if data['get'] == EXEC_CMD:
					if self.logEventReceived:		
						tplWin = TestTemplatesLib.TemplateLayer(name='WINDOWS')
						tplWin.addRaw(raw)
						tplWin.addKey(name='event', data='response')
						tplWin.addKey(name='get', data=EXEC_CMD)
						tplWin.addKey(name='result', data=raw)
						tpl = self.encapsule(win_event=tplWin)
						tpl.addRaw(raw)
						self.logRecvEvent( shortEvt = "%s Response" % EXEC_CMD, tplEvt = tpl )	
						return
						
				if data['get'] == GET_SYS_INFO:
					if self.logEventReceived:		
						tplWin = TestTemplatesLib.TemplateLayer(name='WINDOWS')
						tplWin.addRaw(raw)
						tplWin.addKey(name='event', data='response')
						tplWin.addKey(name='get', data=GET_SYS_INFO)
						tplWin.addKey(name='info', data=raw)
						tpl = self.encapsule(win_event=tplWin)
						tpl.addRaw(raw)
						self.logRecvEvent( shortEvt = "%s Response" % GET_SYS_INFO, tplEvt = tpl )	
						return
				
				if data['get'] == GET_MEM_USAGE:
					tplWin = TestTemplatesLib.TemplateLayer(name='WINDOWS')
					tplWin.addRaw(raw)
					tplWin.addKey(name='event', data='response')
					tplWin.addKey(name='get', data=GET_MEM_USAGE)
					
					totalMemPhysical = 0
					freeMemPhysical = 0
					totalVirtual = 0
					freeVirtual = 0
					if "Node,TotalPhysicalMemory\n127.0.0.1," in raw:
						totalMemPhysical = raw.split('Node,TotalPhysicalMemory\n127.0.0.1,')[1].split('\n')[0]
					if "Node,FreePhysicalMemory\n127.0.0.1," in raw:
						freeMemPhysical = raw.split('Node,FreePhysicalMemory\n127.0.0.1,')[1].split('\n')[0]
					inUseMemPhysical = (int(totalMemPhysical)/1000) - int(freeMemPhysical)
					if "Node,TotalVirtualMemorySize\n127.0.0.1," in raw:
						totalVirtual = raw.split('Node,TotalVirtualMemorySize\n127.0.0.1,')[1].split('\n')[0]
					if "Node,FreeVirtualMemory\n127.0.0.1," in raw:
						freeVirtual = raw.split('Node,FreeVirtualMemory\n127.0.0.1,')[1].split('\n')[0]
					inUseVirtual = int(totalVirtual) - int(freeVirtual)
					
					tplWin.addKey(name='total-physical', data=totalMemPhysical )
					tplWin.addKey(name='free-physical', data=freeMemPhysical )
					tplWin.addKey(name='in-use-physical', data=str(inUseMemPhysical) )
					tplWin.addKey(name='total-virtual', data=totalVirtual )
					tplWin.addKey(name='free-virtual', data=freeVirtual )
					tplWin.addKey(name='in-use-virtual', data=str(inUseVirtual) )
					
					tpl = self.encapsule(win_event=tplWin)
					tpl.addRaw(raw)
					self.logRecvEvent( shortEvt = "%s Response" % GET_MEM_USAGE, tplEvt = tpl )	
					return
					
				# csv format in response
				fieldnames =('Node')
				Rsp = ''
				if data['get'] == GET_OS:
					Rsp = GET_OS
					fieldnames = ('node', 'build-number', 'caption' )
	
				if data['get'] == GET_HOSTNAME:
					Rsp = GET_HOSTNAME
					fieldnames = ('node', 'hostname' )

				if data['get'] == GET_PROCESSES:
					Rsp = GET_PROCESSES
					fieldnames = ('node', 'caption', 'process-id', 'thread-count' )
	
				if data['get'] == GET_UPTIME:
					Rsp = GET_UPTIME
					fieldnames = ('node', 'last-boot-uptime' )
		
				if data['get'] == GET_CPU_LOAD:
					Rsp = GET_CPU_LOAD
					fieldnames = ('node', 'device-id', 'load-percentage' )
	
				if data['get'] == GET_DISKS:
					Rsp = GET_DISKS
					fieldnames = ('node', 'description', 'device-id', 'file-system', 'free-space', 'size-total' )
					
					
				reader = csv.DictReader( f, delimiter=',', fieldnames = fieldnames )
				headers = reader.next() # remove header

				tplWin = TestTemplatesLib.TemplateLayer(name='WINDOWS')
				tplWin.addRaw(raw)
				tplItems = TestTemplatesLib.TemplateLayer(name='')
				tplWin.addKey(name='event', data='response')
				tplWin.addKey(name='items', data=tplItems)
				tplWin.addKey(name='get', data=Rsp)

				i = 0
				nbThreads = 0
				for row in reader:
					subtpl = TestTemplatesLib.TemplateLayer(name='')
					for k,v in row.items():
						if k is not None:
							subtpl.addKey(name=k, data="%s" % v)
						
						# count nb thread just for the get processes action
						if data['get'] == GET_PROCESSES:
							if k == 'thread-count':
								try:
									nbThreads += int(v)
								except Exception as e:
									pass
					tplItems.addKey(name="item %s" % str(i), data=subtpl)
					i += 1

				if data['get'] == GET_PROCESSES:
					tplWin.addKey(name="count-processes", data=str(i) )
					tplWin.addKey(name="count-threads", data=str(nbThreads) )

				if self.logEventReceived:		
					tpl = self.encapsule(win_event=tplWin)
					tpl.addRaw(raw)
					self.logRecvEvent( shortEvt = "%s Response" % Rsp, tplEvt = tpl )	
					
			except Exception as e:
				self.error( 'unable to read response: %s' % str(e), raw=True )
		
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
		
	def agentIsReady(self, timeout=30.0):
		"""
		Wait received "agent ready" event until the end of the timeout
		
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

	def encapsule(self, win_event):
		"""
		"""
		layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
		layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
		layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=win_event)
		return tpl
		
	@doc_public
	def hasReceivedResponse(self, timeout=60.0):
		"""
		Waits to receive "response" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=60s+10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_win=templates.windows(event='response') 
		evt = self.received( expected = self.encapsule(win_event=layer_win), timeout = self.__computeTimeout(timeout) )
		return evt
		
	@doc_public
	def getHostname(self, timeout=60.0):
		"""
		Requests the host to get the hostname

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "wmic /node:\"%s\" computersystem get Username /format:csv" % self.cfg['node'],
									'get': GET_HOSTNAME, 'timeout': timeout		}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_HOSTNAME, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_HOSTNAME, tplEvt = self.encapsule(win_event=layer_win) ) 
		self.sendNotifyToAgent(data=cmd)
		
	@doc_public
	def getOs(self, timeout=60.0):
		"""
		Requests the host to get the version of the operating system

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "wmic /node:\"%s\" os get buildnumber,caption /format:csv" % self.cfg['node'],
						'get': GET_OS, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_OS, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_OS, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)
	
	@doc_public
	def getProcesses(self, timeout=60.0):
		"""
		Requests the host to get a list of all processes 

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "wmic /node:\"%s\" process get Processid,Caption,threadcount /format:csv" % self.cfg['node'],
						'get': GET_PROCESSES, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_PROCESSES, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_PROCESSES, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def getUptime(self, timeout=60.0):
		"""
		Requests the host to get the uptime

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "wmic /node:\"%s\" os get lastbootuptime /format:csv" % self.cfg['node'],
						'get': GET_UPTIME, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_UPTIME, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_UPTIME, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def getCpuLoad(self, timeout=60.0):
		"""
		Requests the host to get the cpu load

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "wmic /node:\"%s\"  cpu get DeviceID, loadpercentage /format:csv" % self.cfg['node'],
						'get': GET_CPU_LOAD, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_CPU_LOAD, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_CPU_LOAD, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)


	@doc_public
	def getMemUsage(self, timeout=60.0):
		"""
		Requests the host to get the memory usage

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		__cmd__ = "wmic /node:%s ComputerSystem get TotalPhysicalMemory /format:csv" % self.cfg['node']
		__cmd__ += " && wmic /node:\"%s\" OS get FreePhysicalMemory /format:csv" % self.cfg['node']
		__cmd__ += " && wmic /node:\"%s\" OS get TotalVirtualMemorySize /format:csv" % self.cfg['node']
		__cmd__ += " && wmic /node:\"%s\" OS get FreeVirtualMemory/format:csv" % self.cfg['node']
		cmd = { 'cmd': __cmd__, 'get': GET_MEM_USAGE, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_MEM_USAGE, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_MEM_USAGE, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)
		

	@doc_public
	def getDisks(self, timeout=60.0):
		"""
		Requests the host to get a list of all disks 

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "wmic /node:\"%s\" logicaldisk get Description, DeviceID, FileSystem, FreeSpace, Size /format:csv" % self.cfg['node'],
						'get': GET_DISKS, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_DISKS, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_DISKS, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)
	
	@doc_public
	def getSystemInfo(self, timeout=60.0):
		"""
		Requests the host to get the complete system information

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd = { 'cmd': "systeminfo /S %s /FO CSV" % self.cfg['node'] ,
						'get': GET_SYS_INFO, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=GET_SYS_INFO, event='request') 
			self.logSentEvent( shortEvt = "%s Request" % GET_SYS_INFO, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd)

	@doc_public
	def execCommand(self, cmd, timeout=60.0):
		"""
		Execute the command passed on argument
	
		@param cmd: command to execute
		@type cmd: string		

		@param timeout: max time to run command (default=60s)
		@type timeout: float	
		"""
		cmd_ = { 'cmd': cmd, 'get': EXEC_CMD, 'timeout': timeout	}
		if self.logEventSent:
			layer_win=templates.windows(get=EXEC_CMD, event='request', cmd=cmd) 
			self.logSentEvent( shortEvt = "%s Request" % EXEC_CMD, tplEvt = self.encapsule(win_event=layer_win) ) 		
		self.sendNotifyToAgent(data=cmd_)		
	
	def __computeTimeout(self, timeout):
		"""
		"""
		p = 10
		t = ( timeout * p ) / 100 + timeout
		return t 
	@doc_public
	def doCommand(self, cmd, timeout=60.0):
		"""
		Execute the command passed on argument and wait reponse until the end of the timeout
	
		@param cmd: command to execute
		@type cmd: string		
		
		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.execCommand(cmd=cmd, timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetSystemInfo(self, timeout=60.0):
		"""
		Get the complete system information and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getSystemInfo(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetDisks(self, timeout=60.0):
		"""
		Get the list of all disks  and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getDisks(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetMemUsage(self, timeout=60.0):
		"""
		Get the memory usage and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getMemUsage(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetCpuLoad(self, timeout=60.0):
		"""
		Get the cpu load and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getCpuLoad(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetUptime(self, timeout=60.0):
		"""
		Get the uptime and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getUptime(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetProcesses(self, timeout=60.0):
		"""
		Get the list of all processes  and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getProcesses(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetOs(self, timeout=60.0):
		"""
		Get the version of the operating system and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getOs(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )
	@doc_public
	def doGetHostname(self, timeout=60.0):
		"""
		Get the hostname and wait reponse until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=60s + 10%)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.getHostname(timeout=timeout)
		return self.hasReceivedResponse(timeout=self.__computeTimeout(timeout) )