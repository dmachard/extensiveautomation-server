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
import TestExecutorLib.TestAdapterLib as TestAdapter
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import threading

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

try:
	import templates_soapui as templates
except ImportError: # python3 support
	from . import templates_soapui as templates

__NAME__="""SOAPUI"""

SOAPUI_RUN_TESTCASE = "Starting SoapUI TestCase"
SOAPUI_TESTCASE_STARTED = "TestCase Started"
SOAPUI_TESTCASE_STOPPED = "TestCase Stopped"
SOAPUI_STEP_STARTED = "Step Started"
SOAPUI_STEP_STOPPED = "Step Stopped"

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='soapui'


class SoapUI(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent,  agent, name=None, debug=False, shared=False):
		"""
		SoapUI adapter

		@param parent: parent testcase
		@type parent: testcase
		
		@param agent: agent to use
		@type agent: string
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, 
																							debug=debug, realname=name,
																							agentSupport=True, agent=agent, 
																							caller=TestAdapter.caller(),
																							agentType=AGENT_TYPE_EXPECTED)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		
		self.curStepName = ''
		self.stepId = 0
		self.currentStep = None
		
		self.threads_list = []
		
		self.cfg = {}
		self.cfg['agent'] = agent
		self.cfg['agent-support'] = True
		self.cfg['agent-name'] = agent['name']
		
		self.cfg['soapui-options'] = [ "-r", "-I" ]
		#  -a         Turns on exporting of all results
		# -r         Prints a small summary report
		# -j         Sets the output to include JUnit XML reports
		# -I         Do not stop if error occurs, ignore them
		
		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		self.initAgent(data={})
		if self.agentIsReady(timeout=10) is None:
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
		# join all threads
		for thread in self.threads_list:
			thread.join()
		# stop timer
		self.TIMER_ALIVE_AGT.stop()
		
		# cleanup remote agent
		self.resetAgent()
	def encapsule(self, layer_soapui):
		"""
		Encapsule layer in template message
		"""
		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer(layer=layer_soapui)
		return tpl
		
	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		line = data['msg']
		self.debug(line)

		# start of the run
		if 'Running TestCase' in line:
			tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_TESTCASE_STARTED))
			self.logRecvEvent( shortEvt = SOAPUI_TESTCASE_STARTED, tplEvt = tpl )
		
		# end of the run
		if 'TestCaseRunner Summary' in line:
			tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_TESTCASE_STOPPED))
			self.logRecvEvent( shortEvt = SOAPUI_TESTCASE_STOPPED, tplEvt = tpl )
		
		# send request
		if 'Sending request: ' in line:
			self.warning( "%s" % line.split("Sending request: ")[1].strip() )
		
		# receive request
		if 'Receiving response:' in line:
			self.warning( "%s" % line.split("Receiving response:")[1].strip()  )

		# create step
		if ' running step ' in line:
			self.stepId += 1
			self.curStepName = line.split(' running step ')[1].strip()[1:-1] 
			
			# log event
			tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_STEP_STARTED, stepId= "%s" % self.stepId))
			self.logRecvEvent( shortEvt = "%s [Id=#%s]" % (SOAPUI_STEP_STARTED, self.stepId), tplEvt = tpl )

			# starting thread to check response
#			thread = threading.Thread(target = self.isStepStopped, args=(self.cfg['step-timeout'] , "%s" % self.stepId)  )
#			self.threads_list.append( thread)
#			thread.start()

			# create step in testcase
			self.currentStep = self.testcase().addStep(expected=self.curStepName, description=self.curStepName, summary=self.curStepName)
			self.currentStep.start()

		# error on assertion
		if '[different]' in line:
			# log event
#			tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_STEP_STOPPED, stepId= "%s" % self.stepId))
#			self.logRecvEvent( shortEvt = "%s [Id=#%s]" % (SOAPUI_STEP_STOPPED, self.stepId) , tplEvt = tpl )
			
			# set the step to failed
			self.currentStep.setFailed(actual=line.split('[different]')[1].strip() )
			
		#step passed
		if 'has status VALID' in line:
			tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_STEP_STOPPED, stepId= "%s" % self.stepId))
			self.logRecvEvent( shortEvt = "%s [Id=#%s]" % (SOAPUI_STEP_STOPPED, self.stepId) , tplEvt = tpl )
			
			msgOk = line.split( 'INFO  [SoapUITestCaseRunner] ' )[1] 
			self.currentStep.setPassed(actual=msgOk)
		
		# assert error detected
		if "ASSERTION FAILED ->" in line:
			tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_STEP_STOPPED, stepId= "%s" % self.stepId))
			self.logRecvEvent( shortEvt = "%s [Id=#%s]" % (SOAPUI_STEP_STOPPED, self.stepId) , tplEvt = tpl )
			
			# set the step to failed
			self.currentStep.setFailed(actual=line.split('ASSERTION FAILED ->')[1].strip() )

		# unable to load xml file
		if "java.lang.Exception: Failed to load SoapUI project file [" in line:
			lineTmp = line.split("Failed to load SoapUI project file [")[1].split("]", 1)[0]
			self.error("Failed to load SoapUI project file: %s" % lineTmp)

		# bad testcase name
		if " java.lang.Exception: TestCase with name [" in line:
			lineTmp = line.split("TestCase with name [")[1].split("]", 1)[0]
			self.error("Bad testcase name: %s" % lineTmp)

		# bad testsuite name
		if " java.lang.Exception: TestSuite with name [" in line:
			lineTmp = line.split("TestSuite with name [")[1].split("]", 1)[0]
			self.error("Bad testsuite name: %s" % lineTmp)

		# connect error
		if 'HttpHostConnectException' in line:
			if self.currentStep is not None:
				self.currentStep.setFailed("connection to host refused")
			else:
				self.error("connection to host refused")

		# just to be sure, if an error is not catched
		if "finished with status [FAILED] in" in line:
			self.testcase().setFailed()


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
		pass
	
	def sendNotifyToAgent(self, data):
		"""
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
	@doc_public
	def isStepStopped(self, timeout=20.0, stepId=None):
		"""
		"""
		TestAdapter.check_timeout(caller=TestAdapter.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_STEP_STOPPED, stepId=stepId))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isTestcaseStarted(self, timeout=20.0):
		"""
		Wait to receive "testcase started" event until the end of the timeout
		The timeout is the max time to start soapui
		
		@param timeout: max time to start the run of the testcase in second (default=20s)
		@type timeout: float		
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapter.check_timeout(caller=TestAdapter.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_TESTCASE_STARTED))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isTestcaseStopped(self, timeout=60.0):
		"""
		Wait to receive "testcase stopped" event until the end of the timeout
		The timeout is the max time to run all steps inside the testcase of soapui
		
		@param timeout: max time to run all steps of the testcase in second (default=60s)
		@type timeout: float		

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapter.check_timeout(caller=TestAdapter.caller(), timeout=timeout)
		
		# construct the expected template
		expected = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_TESTCASE_STOPPED))
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def runTest(self, projectPath, projectFile, testsuiteName, testcaseName, endpoint='', projectProperties={}):
		"""
		Run a testcase
		
		@param projectPath: project path
		@type projectPath: string		

		@param projectFile: xml file
		@type projectFile: string		

		@param testsuiteName: testsuite name
		@type testsuiteName: string	

		@param testcaseName: testcase name
		@type testcaseName: string	
		
		@param endpoint: endpoint used (default='')
		@type endpoint: string	
		
		@param projectProperties: project properties
		@type projectProperties: dict	
		"""
		if len(endpoint):
			self.cfg['soapui-options'].append("-e %s" % endpoint)
		if len(projectProperties):
			for k,v in projectProperties.items():
				self.cfg['soapui-options'].append("-P%s=%s" % (k, v) )
		agentData = { 'project-path': projectPath,  'project-file': projectFile,  'testsuite-name':  testsuiteName, 
													'testcase-name':  testcaseName, 'options': self.cfg['soapui-options']  }
		
		# send command to agent
		self.debug( "request: %s" % agentData)
		self.sendNotifyToAgent(data=agentData)
		
		# log event
		tpl = self.encapsule(layer_soapui=templates.soapui(action=SOAPUI_RUN_TESTCASE, projectPath=projectPath, projectFile=projectFile,
																																					testsuiteName=testsuiteName, testcaseName=testcaseName))
		self.logSentEvent( shortEvt = "%s [%s -> %s]" % (SOAPUI_RUN_TESTCASE, testsuiteName, testcaseName) , tplEvt = tpl )
		
	@doc_public
	def doRunTest(self, projectPath, projectFile, testsuiteName, testcaseName, endpoint='', projectProperties={}, 
																timeoutStart=20.0, timeoutStop=60.0):
		"""
		Run a testcase as complete
		
		@param projectPath: project path
		@type projectPath: string		

		@param projectFile: xml file
		@type projectFile: string		

		@param testsuiteName: testsuite name
		@type testsuiteName: string	

		@param testcaseName: testcase name
		@type testcaseName: string	
		
		@param endpoint: endpoint used (default='')
		@type endpoint: string	
		
		@param projectProperties: project properties
		@type projectProperties: dict	
		
		@param timeoutStart: max time to start the run of the testcase in second (default=60s)
		@type timeoutStart: float		

		@param timeoutStop: max time to run all steps in the testcase in second (default=60s)
		@type timeoutStop: float		
		
		@return: True if the testcase is complete, False otherwise.
		@rtype: boolean
		"""
		ret = True
		self.runTest(projectPath=projectPath, projectFile=projectFile, testsuiteName=testsuiteName, testcaseName=testcaseName,
											endpoint=endpoint, projectProperties=projectProperties)
		
		if self.isTestcaseStarted(timeout=timeoutStart) is None:
			ret = False
		
		else:
			
			if self.isTestcaseStopped(timeout=timeoutStop) is None:
				ret = False
				
		return ret
			