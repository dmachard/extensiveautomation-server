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

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

LibraryUnits= sys.modules['SutLibraries.%s.Units' % TestLibrary.getVersion()]

import templates

__NAME__="""FILE"""

GET_FILE = "Get File"
IS_FILE = "Is File"
IS_DIRECTORY = "Is Directory"
IS_LINK = "Is Link"
CHECKSUM_FILE = "Checksum File"
WAIT_FILE = "Wait For File"
WAIT_DIRECTORY = "Wait For Directory"
EXISTS_FILE = "Exists File"
EXISTS_DIRECTORY = "Exists Directory"
DELETE_FILE = "Delete File"
DELETE_DIRECTORY = "Delete Directory"
MODIFICATION_DATE_OF_FILE = "Modification Date Of File"
SIZE_OF_FILE = "Size Of File"
SIZE_OF_DIRECTORY = "Size Of Directory"
MOVE_FILE = "Move File"
MOVE_DIRECTORY = "Move Directory"
COPY_FILE = "Copy File"
COPY_DIRECTORY = "Copy Directory"
LIST_FILES = "List Files"
COMPARE_FILES = "Compare Files"

START_FOLLOW_FILE = "Start Follow File"
STOP_FOLLOW_FILE = "Stop Follow File"
LOG_FILE = "Log File"
WATCHING_FILE = "Watching"
UNWATCHING_FILE = "Unwatching"

AGENT_INITIALIZED = "AGENT_INITIALIZED"

AGENT_TYPE_EXPECTED='file'

class File(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, agent, name=None, debug=False, shared=False):
		"""
		File adapter
		Works with an agent only

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
		# check the agent
		if not isinstance(agent, dict) : 
			raise TestAdapter.ValueException(TestAdapter.caller(), "agent argument is not a dict (%s)" % type(agent) )
		if not len(agent['name']): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "agent name cannot be empty" )
		if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
			raise TestAdapter.ValueException(TestAdapter.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		# init adapter
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, 
																							agentSupport=True, agent=agent, shared=shared)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		
		self.unitLib = LibraryUnits.Bytes(parent=parent, name=None, debug=debug)
		
		self.parent = parent
		self.reqId = 0
		self.cfg = {}
		self.cfg['agent'] = agent
		self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = True

		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
			
		# initialize the agent with no data
		self.prepareAgent(data={'shared': shared})
		if self.agentIsReady(timeout=30) is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
#			raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
		self.TIMER_ALIVE_AGT.start()
		
	def getRedId(self):
			"""
			Return a new req id
			"""
			self.reqId += 1
			return self.reqId

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
		# stop timer
		self.TIMER_ALIVE_AGT.stop()
		
		# cleanup remote agent
		self.resetAgent()

	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['cmd'] == AGENT_INITIALIZED:
			tpl = TestTemplates.TemplateMessage()
			layer = TestTemplates.TemplateLayer('AGENT')
			layer.addKey("ready", True)
			layer.addKey(name='name', data=self.cfg['agent']['name'] )
			layer.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer(layer= layer)
			self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )	
			
		if data['cmd'] == COMPARE_FILES:
			layer_file=templates.file( 
																											cmd=COMPARE_FILES, 
																											path = data['path'],
																											pathDst = data['path-dst'],
																											result=data['result'], 
																											resultHtml=data['result-html'], 
																											resultCompare=data['result-compare'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % COMPARE_FILES, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == LIST_FILES:
			layer_file=templates.file( 
																											cmd=LIST_FILES, 
																											path = data['path'],
																											listFiles = data['list-files'],
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % LIST_FILES, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == MODIFICATION_DATE_OF_FILE:
			layer_file=templates.file( 
																											cmd=MODIFICATION_DATE_OF_FILE, 
																											path = data['path'],
																											modificationDate = data['modification-date'],
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % MODIFICATION_DATE_OF_FILE, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == COPY_FILE:
			layer_file=templates.file( 
																											cmd=COPY_FILE, 
																											path = data['path'],
																											pathDst = data['path-dst'],
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % COPY_FILE, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == COPY_DIRECTORY:
			layer_file=templates.file( 
																											cmd=COPY_DIRECTORY, 
																											path = data['path'],
																											pathDst = data['path-dst'],
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % COPY_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == MOVE_FILE:
			layer_file=templates.file( 
																											cmd=MOVE_FILE, 
																											path = data['path'],
																											pathDst = data['path-dst'],
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % MOVE_FILE, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == MOVE_DIRECTORY:
			layer_file=templates.file( 
																											cmd=MOVE_DIRECTORY, 
																											path = data['path'],
																											pathDst = data['path-dst'],
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % MOVE_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == SIZE_OF_FILE:
			layer_file=templates.file( 
																											cmd=SIZE_OF_FILE,  size=data['size'], 
																											path = data['path'],
																											result=data['result'], 
																											event='response' ,
																											sizeHuman = self.unitLib.toHuman(bytes=int(data['size'])),
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % SIZE_OF_FILE, tplEvt = self.encapsule(file_event=layer_file) )	

		if data['cmd'] == SIZE_OF_DIRECTORY:
			layer_file=templates.file( 
																											cmd=SIZE_OF_DIRECTORY,  size=data['size'], 
																											path = data['path'],
																											result=data['result'], 
																											event='response' ,
																											sizeHuman = self.unitLib.toHuman(bytes=int(data['size'])),
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % SIZE_OF_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == DELETE_FILE:
			layer_file=templates.file( 
																											cmd=DELETE_FILE,  result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % DELETE_FILE, tplEvt = self.encapsule(file_event=layer_file) )	

		if data['cmd'] == DELETE_DIRECTORY:
			layer_file=templates.file( 
																											cmd=DELETE_DIRECTORY,  result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % DELETE_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == GET_FILE:
			layer_file=templates.file( 
																											cmd=GET_FILE,  file=data['file'], 
																											event='response' , 
																											content=data['content'] , 
																											contentLength=len(data['content'] ),
																											requestId = data['request-id']
																										) 
#			layer_file.addRaw(data['content'])
			self.logRecvEvent( shortEvt = "%s Response" % GET_FILE, tplEvt = self.encapsule(file_event=layer_file, raw=data['content']) )	

		if data['cmd'] == IS_LINK:
			layer_file=templates.file( 
																											cmd=IS_LINK,  result=data['result'], 
																											path = data['path'],
																											event='response',
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % IS_LINK, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == EXISTS_FILE:
			layer_file=templates.file( 
																											cmd=EXISTS_FILE,  result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % EXISTS_FILE, tplEvt = self.encapsule(file_event=layer_file) )	

		if data['cmd'] == EXISTS_DIRECTORY:
			layer_file=templates.file( 
																											cmd=EXISTS_DIRECTORY,  result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % EXISTS_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == IS_FILE:
			layer_file=templates.file( 
																											cmd=IS_FILE,  result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % IS_FILE, tplEvt = self.encapsule(file_event=layer_file) )	

		if data['cmd'] == IS_DIRECTORY:
			layer_file=templates.file( 
																											cmd=IS_DIRECTORY,  result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % IS_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
			
		if data['cmd'] == CHECKSUM_FILE:
			layer_file=templates.file( 
																											cmd=CHECKSUM_FILE,  
																											checksum=data['checksum'] , 
																											checksumType=data['checksum-type'] , 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % CHECKSUM_FILE, tplEvt = self.encapsule(file_event=layer_file) )	

		if data['cmd'] == WAIT_FILE:
			layer_file=templates.file( 
																											cmd=WAIT_FILE,  
																											result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % WAIT_FILE, tplEvt = self.encapsule(file_event=layer_file) )	

		if data['cmd'] == WAIT_DIRECTORY:
			layer_file=templates.file( 
																											cmd=WAIT_DIRECTORY,  
																											result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % WAIT_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) )	
		if data['cmd'] == START_FOLLOW_FILE:
			layer_file=templates.file( 
																											cmd=START_FOLLOW_FILE,  
																											result=data['result'], 
																											path = data['path'],
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % START_FOLLOW_FILE, tplEvt = self.encapsule(file_event=layer_file) )	
		if data['cmd'] == STOP_FOLLOW_FILE:
			layer_file=templates.file( 
																											cmd=STOP_FOLLOW_FILE,  
																											result=data['result'], 
																											event='response' ,
																											requestId = data['request-id']
																										) 
			self.logRecvEvent( shortEvt = "%s Response" % STOP_FOLLOW_FILE, tplEvt = self.encapsule(file_event=layer_file) )	
		if data['cmd'] == LOG_FILE:
			layer_file=templates.file( 
																											cmd=LOG_FILE,  
																											content=data['log']['content'], 
																											file = data['log']['filename'], 
																											event='response' ,
																										) 
#			layer_file.addRaw( data['log']['content'] )
			self.logRecvEvent( shortEvt = "%s Event" % LOG_FILE, tplEvt = self.encapsule(file_event=layer_file, raw=data['log']['content']) )	
		if data['cmd'] == WATCHING_FILE:
			layer_file=templates.file( 
																											cmd=WATCHING_FILE,  
																											file = data['filename'], 
																											event='response' ,
																										) 
#			layer_file.addRaw( data['filename'] )
			self.logRecvEvent( shortEvt = "%s" % WATCHING_FILE, tplEvt = self.encapsule(file_event=layer_file, raw=data['filename'] ) )	
		if data['cmd'] == UNWATCHING_FILE:
			layer_file=templates.file( 
																											cmd=UNWATCHING_FILE,  
																											file = data['filename'], 
																											event='response' ,
																										) 
#			layer_file.addRaw( data['filename'] )
			self.logRecvEvent( shortEvt = "%s" % UNWATCHING_FILE, tplEvt = self.encapsule(file_event=layer_file, raw=data['filename']) )	
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
		
	def encapsule(self, file_event, raw=''):
		"""
		"""
		layer_agent= TestTemplates.TemplateLayer('AGENT')
		layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
		layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=file_event)
		
		tpl.addRaw( raw )
		
		return tpl
		
	@doc_public
	def sizeOfFile(self, file):
		"""
		Get the size of the file
	
		@param file: path of the file
		@type file: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(file):
			self.error("no file passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  SIZE_OF_FILE, 'path': file, 'request-id': 	requestId }
		layer_file=templates.file(cmd=SIZE_OF_FILE,  file=file, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % SIZE_OF_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId

	@doc_public
	def sizeOfDirectory(self, path):
		"""
		Get the size of the directory
	
		@param path: path of the directory
		@type path: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  SIZE_OF_DIRECTORY, 'path': path, 'request-id': 	requestId }
		layer_file=templates.file(cmd=SIZE_OF_DIRECTORY,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % SIZE_OF_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def listFiles(self, path):
		"""
		List all files in the directory
	
		@param path: path of the directory
		@type path: string	
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  LIST_FILES, 'path': path, 'request-id': 	requestId }
		layer_file=templates.file(cmd=LIST_FILES,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % LIST_FILES, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def deleteFile(self, file):
		"""
		Delete a file
	
		@param file: path of the file
		@type file: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(file):
			self.error("no file passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  DELETE_FILE, 'path': file, 'request-id': 	requestId }
		layer_file=templates.file(cmd=DELETE_FILE,  file=file, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % DELETE_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId

	@doc_public
	def deleteDirectory(self, path):
		"""
		Delete a directory
	
		@param path: path of the directory
		@type path: string	
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  DELETE_DIRECTORY, 'path': path, 'request-id': 	requestId }
		layer_file=templates.file(cmd=DELETE_DIRECTORY,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % DELETE_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def getFile(self, file):
		"""
		Get file content 
	
		@param file: path of the file
		@type file: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(file):
			self.error("no file passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  GET_FILE, 'path': file, 'request-id': 	requestId }
		layer_file=templates.file(cmd=GET_FILE,  file=file, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % GET_FILE, tplEvt = self.encapsule(file_event=layer_file) )		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def modificationDateOfFile(self, file):
		"""
		Get the modification date of the file
	
		@param file: path of the file
		@type file: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(file):
			self.error("no file passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  MODIFICATION_DATE_OF_FILE, 'path': file, 'request-id': 	requestId }
		layer_file=templates.file(cmd=MODIFICATION_DATE_OF_FILE,  file=file, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % MODIFICATION_DATE_OF_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def copyFile(self, fileSrc, fileDst):
		"""
		Copy the file
	
		@param fileSrc: path of the source file
		@type fileSrc: string		
		
		@param fileDst: path of the destination file
		@type fileDst: string	
		
		@return: request id
		@rtype: integer	
		"""
		if not len(fileSrc):
			self.error("no file passed as argument")
			return
		if not len(fileDst):
			self.error("no file dest passed as argument")
			return
			
		requestId = self.getRedId()
		cmd = { 'cmd':  COPY_FILE, 'path': fileSrc, 'path-dst': fileDst, 'request-id': 	requestId }
		layer_file=templates.file(cmd=COPY_FILE,  file=fileSrc, fileDst=fileDst, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % COPY_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId

	@doc_public
	def moveFile(self, fileSrc, fileDst):
		"""
		Move the file 
	
		@param fileSrc: path of the source file
		@type fileSrc: string		
		
		@param fileDst: path of the destination file
		@type fileDst: string
		
		@return: request id
		@rtype: integer	
		"""
		if not len(fileSrc):
			self.error("no file passed as argument")
			return
		if not len(fileDst):
			self.error("no file dest passed as argument")
			return
			
		requestId = self.getRedId()
		cmd = { 'cmd':  MOVE_FILE, 'path': fileSrc, 'path-dst': fileDst, 'request-id': 	requestId }
		layer_file=templates.file(cmd=MOVE_FILE,  file=fileSrc, fileDst=fileDst, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % MOVE_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId

	@doc_public
	def compareFiles(self, fileSrc, fileDst):
		"""
		Compare two text files
	
		@param fileSrc: path of the source file
		@type fileSrc: string		
		
		@param fileDst: path of the destination file
		@type fileDst: string
		
		@return: request id
		@rtype: integer	
		"""
		if not len(fileSrc):
			self.error("no file passed as argument")
			return
		if not len(fileDst):
			self.error("no file dest passed as argument")
			return
			
		requestId = self.getRedId()
		cmd = { 'cmd':  COMPARE_FILES, 'path': fileSrc, 'path-dst': fileDst, 'request-id': 	requestId }
		layer_file=templates.file(cmd=COMPARE_FILES,  file=fileSrc, fileDst=fileDst, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % COMPARE_FILES, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def moveDirectory(self, pathSrc, pathDst):
		"""
		Move the directory 
	
		@param pathSrc: path of the source file
		@type pathSrc: string		
		
		@param pathDst: path of the destination file
		@type pathDst: string	
		
		@return: request id
		@rtype: integer	
		"""
		if not len(pathSrc):
			self.error("no path passed as argument")
			return
		if not len(pathDst):
			self.error("no path dest passed as argument")
			return
			
		requestId = self.getRedId()
		cmd = { 'cmd':  MOVE_DIRECTORY, 'path': pathSrc, 'path-dst': pathDst, 'request-id': 	requestId }
		layer_file=templates.file(cmd=MOVE_DIRECTORY,  path=pathSrc, pathDst=pathDst, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % MOVE_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId

	@doc_public
	def copyDirectory(self, pathSrc, pathDst):
		"""
		Copy the directory 
	
		@param pathSrc: path of the source file
		@type pathSrc: string		
		
		@param pathDst: path of the destination file
		@type pathDst: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(pathSrc):
			self.error("no path passed as argument")
			return
		if not len(pathDst):
			self.error("no path dest passed as argument")
			return
			
		requestId = self.getRedId()
		cmd = { 'cmd':  COPY_DIRECTORY, 'path': pathSrc, 'path-dst': pathDst, 'request-id': 	requestId }
		layer_file=templates.file(cmd=COPY_DIRECTORY,  path=pathSrc, pathDst=pathDst, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % COPY_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def isFile(self, path):
		"""
		Check if path is an existing regular file
	
		@param path: path of the file
		@type path: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()	
		cmd = { 'cmd':  IS_FILE, 'path': path, 'request-id': requestId	}
		layer_file=templates.file(cmd=IS_FILE,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % IS_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def isDirectory(self, path):
		"""
		Check if the path in argument is a folder
	
		@param path: path of the file
		@type path: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no file passed as argument")
			return
			
		requestId = self.getRedId()	
		cmd = { 'cmd':  IS_DIRECTORY, 'path': path, 'request-id': requestId	}
		
		layer_file=templates.file(cmd=IS_DIRECTORY,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % IS_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def isLink(self, path):
		"""
		Check if the path in argument is a link
	
		@param path: path of the link
		@type path: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  IS_LINK, 'path': path, 'request-id': requestId	}
		
		layer_file=templates.file(cmd=IS_LINK,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % IS_LINK, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		
		
		return requestId

	@doc_public
	def existsFile(self, path):
		"""
		Check if the path exists
	
		@param path: path of the file
		@type path: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  EXISTS_FILE, 'path': path, 'request-id': requestId	}
		
		layer_file=templates.file(cmd=EXISTS_FILE,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % EXISTS_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		
		
		return requestId

	@doc_public
	def existsDirectory(self, path):
		"""
		Check if the path folder exists
	
		@param path: path of the folder
		@type path: string		
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  EXISTS_DIRECTORY, 'path': path, 'request-id': requestId	}
		
		layer_file=templates.file(cmd=EXISTS_DIRECTORY,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % EXISTS_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		
		
		return requestId
		
	@doc_public
	def waitForFile(self, path, timeout=10):
		"""
		Wait for file
	
		@param path: path of the file
		@type path: string		
		
		@param timeout: time max to wait file (default=10s)
		@type timeout: float	
		
		@return: request id
		@rtype: integer	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  WAIT_FILE, 'path': path, 'timeout': timeout, 
								'request-id': requestId	}
		
		layer_file=templates.file(cmd=WAIT_FILE,  path=path, event='request', 
											timeout=str(timeout), requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % WAIT_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def waitForDirectory(self, path, timeout=10):
		"""
		Wait for directory
	
		@param path: path of the file
		@type path: string		
		
		@param timeout: time max to wait file (default=10s)
		@type timeout: float	
		
		@return: request id
		@rtype: integer	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not len(path):
			self.error("no path passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  WAIT_DIRECTORY, 'path': path, 
									'timeout': timeout, 'request-id': requestId	}
									
		layer_file=templates.file(cmd=WAIT_DIRECTORY,  path=path, event='request',
											timeout=str(timeout), requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % WAIT_DIRECTORY, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def checksumFile(self, file, md5=True):
		"""
		Compute the checksum of the file passed in argument
	
		@param file: path of the link
		@type file: string		
		
		@param md5: make a md5  (defaiult=True)
		@type md5: boolean		
		
		@return: request id
		@rtype: integer		
		"""
		if not len(file):
			self.error("no file passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  CHECKSUM_FILE, 'path': file,  
								'checksum-type': md5, 'request-id': requestId	}
								
		layer_file=templates.file(cmd=CHECKSUM_FILE,  file=file, 
											event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % CHECKSUM_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def startFollowFile(self, path, filter, extensions=["log"]):
		"""
		Start to follow a text file
		
		@param path: path of the file
		@type path: string	
		
		@param filter: text filter
		@type filter: string	
		
		@param extensions:  list of file extensions to follow
		@type extensions: list	
		
		@return: request id
		@rtype: integer	
		"""
		if not len(path):
			self.error("no path passed as argument")
			return
		if not len(filter):
			self.error("no filter passed as argument")
			return
		
		requestId = self.getRedId()
		cmd = { 'cmd':  START_FOLLOW_FILE,  'path': path, 'extensions': extensions, 'request-id': requestId	}
		if filter is not None:
			cmd['filter'] = filter
		else:
			cmd['filter'] = ''

		layer_file=templates.file(cmd=START_FOLLOW_FILE,  path=path, event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % START_FOLLOW_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def stopFollowFile(self, followId):
		"""
		Stop to follow a text file
		
		@param followId: follow id 
		@type followId: integer	
		"""	
		requestId = self.getRedId()
		cmd = { 'cmd':  STOP_FOLLOW_FILE, 'follow-id': followId, 'request-id': requestId	}

		layer_file=templates.file(cmd=STOP_FOLLOW_FILE,   event='request', requestId=requestId) 
		self.logSentEvent( shortEvt = "%s Request" % STOP_FOLLOW_FILE, tplEvt = self.encapsule(file_event=layer_file) ) 		
		self.sendNotifyToAgent(data=cmd)		

		return requestId
		
	@doc_public
	def hasStartedFollowing(self, timeout=1.0):
		"""
		Waits to receive "started following" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', result=True, cmd=START_FOLLOW_FILE) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
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
	def hasStoppedFollowing(self, timeout=1.0):
		"""
		Waits to receive "stopped following" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', result=True, cmd=STOP_FOLLOW_FILE) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
		
	@doc_public
	def hasReceivedLogFile(self, timeout=1.0, content=None):
		"""
		Waits to receive "log file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param content: expected content
		@type content: string/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', content=content, cmd=LOG_FILE) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedFile(self, timeout=1.0, requestId=None, content=None):
		"""
		Waits to receive "get file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param content: expected content
		@type content: string/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', content=content, cmd=GET_FILE, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedModificationDateFile(self, timeout=1.0, requestId=None, modificationDate=None):
		"""
		Waits to receive "modification date for file" event until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param requestId: request id (default=None)
		@type requestId: integer/none	

		@param modificationDate: modification date
		@type modificationDate: string/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', modificationDate=modificationDate, 
																						cmd=MODIFICATION_DATE_OF_FILE, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedListFiles(self, timeout=1.0, requestId=None, listFiles=None):
		"""
		Waits to receive "list of files" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	

		@param listFiles: expected list of files
		@type listFiles: string/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', listFiles=listFiles, 
																						cmd=LIST_FILES, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedSizeFile(self, timeout=1.0, requestId=None, size=None, fileExists=True):
		"""
		Waits to receive "size file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param size: expected content
		@type size: string/none	

		@param fileExists: expected result, True if file, False otherwise (default=True)
		@type fileExists: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', size=size, cmd=SIZE_OF_FILE, result=fileExists,  requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt

	@doc_public
	def hasReceivedSizeDirectory(self, timeout=1.0, requestId=None, size=None, folderExists=True):
		"""
		Waits to receive "size directory" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param size: expected content
		@type size: string/none	
		
		@param folderExists: expected result, True if file, False otherwise (default=True)
		@type folderExists: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', size=size, cmd=SIZE_OF_DIRECTORY,
										result=folderExists,  requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedIsLink(self, timeout=1.0, requestId=None,  isLink=True):
		"""
		Waits to receive "link" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param isLink: expected result, True if file, False otherwise (default=True)
		@type isLink: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=IS_LINK, result=isLink, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedIsFile(self, timeout=1.0, requestId=None, isFile=True):
		"""
		Waits to receive "file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param isFile: expected result, True if file, False otherwise (default=True)
		@type isFile: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=IS_FILE, result=isFile, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedIsDirectory(self, timeout=1.0, requestId=None, isFolder=True):
		"""
		Waits to receive "directory" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param isFolder: expected result, True if folder, False otherwise (default=True)
		@type isFolder: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=IS_DIRECTORY, result=isFolder, requestId=requestId ) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedWaitFile(self, timeout=1.0, requestId=None, fileExists=True):
		"""
		Waits to receive "file exists" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param fileExists: expected result, True if exists, False otherwise (default=True)
		@type fileExists: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=WAIT_FILE, result=fileExists, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedWaitDirectory(self, timeout=1.0, requestId=None, directoryExists=True):
		"""
		Waits to receive "folder exists" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param directoryExists: expected result, True if exists, False otherwise (default=True)
		@type directoryExists: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=WAIT_DIRECTORY, result=directoryExists, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedCompareFiles(self, timeout=1.0, requestId=None, identical=True):
		"""
		Waits to receive "compare files" text event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param identical: expected result, True if identical, False otherwise (default=True)
		@type identical: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=COMPARE_FILES, resultCompare=identical, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedExistsFile(self, timeout=1.0, requestId=None, fileExists=True):
		"""
		Waits to receive "file exists" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param fileExists: expected result, True if exists, False otherwise (default=True)
		@type fileExists: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=EXISTS_FILE, result=fileExists, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedExistsDirectory(self, timeout=1.0, requestId=None, directoryExists=True):
		"""
		Waits to receive "folder exists" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param directoryExists: expected result, True if exists, False otherwise (default=True)
		@type directoryExists: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=EXISTS_DIRECTORY, result=directoryExists, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt

	@doc_public
	def hasReceivedDeleteFile(self, timeout=1.0, requestId=None, fileDeleted=True):
		"""
		Waits to receive "delete file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param fileDeleted: expected result, True if exists, False otherwise (default=True)
		@type fileDeleted: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=DELETE_FILE, result=fileDeleted, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt

	@doc_public
	def hasReceivedDeleteDirectory(self, timeout=1.0, requestId=None, directoryDeleted=True):
		"""
		Waits to receive "delete directory" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param directoryDeleted: expected result, True if exists, False otherwise (default=True)
		@type directoryDeleted: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=DELETE_DIRECTORY, result=directoryDeleted, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		

	@doc_public
	def hasReceivedCopyDirectory(self, timeout=1.0, requestId=None, directoryCopied=True):
		"""
		Waits to receive "copy directory" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param directoryCopied: expected result, True if exists, False otherwise (default=True)
		@type directoryCopied: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=COPY_DIRECTORY, result=directoryCopied, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedCopyFile(self, timeout=1.0, requestId=None, fileCopied=True):
		"""
		Waits to receive "delete directory" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param fileCopied: expected result, True if exists, False otherwise (default=True)
		@type fileCopied: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=COPY_FILE, result=fileCopied, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt

	@doc_public
	def hasReceivedMoveFile(self, timeout=1.0, requestId=None, fileMoved=True):
		"""
		Waits to receive "move file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param fileMoved: expected result, True if exists, False otherwise (default=True)
		@type fileMoved: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=MOVE_FILE, result=fileMoved, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt

	@doc_public
	def hasReceivedMoveDirectory(self, timeout=1.0, requestId=None, directoryMoved=True):
		"""
		Waits to receive "move directory" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param directoryMoved: expected result, True if exists, False otherwise (default=True)
		@type directoryMoved: boolean
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=MOVE_DIRECTORY, result=directoryMoved, requestId=requestId) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def hasReceivedChecksumFile(self, timeout=1.0, requestId=None, checksum=None, checksumType=None):
		"""
		Waits to receive "checksum md5 file" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param requestId: request id (default=None)
		@type requestId: integer/none	
		
		@param checksum: expected checksum
		@type checksum: string/none	

		@param checksumType: expected checksum type
		@type checksumType: string/none
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		layer_file=templates.file(event='response', cmd=CHECKSUM_FILE, checksum=checksum, 
																											checksumType=checksumType, requestId=requestId ) 
		evt = self.received( expected = self.encapsule(file_event=layer_file), timeout = timeout )
		return evt
		
	@doc_public
	def doGetContent(self, file, timeout=1.0):
		"""
		Return content of the file passed as argument
		
		@param file: path of the file to get
		@type file: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: content file or False on error
		@rtype: string/boolean		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		reqId = self.getFile(file=file)
		evt = self.hasReceivedFile(timeout=timeout, requestId=reqId)
		if evt is not None:
			return evt.getRaw()
		return False
		
	@doc_public
	def doFindString(self, file, stringExpected, timeout=1.0):
		"""
		Search the expected string on the file content
		
		@param file: path of the file to get
		@type file: string		
		
		@param stringExpected: string expected in file
		@type stringExpected: string/operators
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: True on match, False otherwise
		@rtype: boolean		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		reqId = self.getFile(file=file)
		evt = self.hasReceivedFile(timeout=timeout, content=stringExpected, requestId=reqId)
		if evt is not None:
			return True
		return False