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
from TestExecutorLib.TestExecutorLib import doc_public

import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

if sys.version_info < (2,7, ): # add python ftp tls support for py2.6
	import Libs.ftplib as ftplib
else:
	import ftplib

import io
import time
import re
import os

try:
	import templates
except ImportError: # python3 support
	from . import templates

__NAME__="""FTP"""

SECURE = "Secure"
WELCOME = "Welcome"
CONNECT = "Connect"
DISCONNECT = "Disconnect"
LOGIN = "Login"
COMMAND = "Command"
GET_FILE = "Get File"
PUT_FILE = "Put File"
SIZE_FILE = "Size File"
RENAME_FILE = "Rename File"
DELETE_FILE = "Delete File"
GOTO_FOLDER = "Goto Folder"
ADD_FOLDER = "Add Folder"
DELETE_FOLDER = "Delete Folder"
RENAME_FOLDER = "Rename Folder"
LISTING_FOLDER = "Listing Folder"
CURRENT_PATH = "Current Path"

WAIT_FILE = "Wait File"
WAIT_FOLDER = "Wait Folder"

PUT_FOLDER="Put Folder"
GET_FOLDER="Get Folder"

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='ftp'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, destinationIp= '127.0.0.1',  destinationPort=21, 
													user='anonymous', password='anonymous@',
													agent=None, name=None, tlsSupport=False, 
													debug=False, shared=False, agentSupport=False):
		"""
		Ftp adapter with TLS support
		
		@param parent: parent testcase
		@type parent: testcase
		
		@param destinationIp: destination ip of the ftp
		@type destinationIp: string
		
		@param destinationPort: destination port of the ftp
		@type destinationPort: integer
		
		@param user: username to connect on it
		@type user: string
		
		@param password: password to connect on it
		@type password: string
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param agent: agent to use
		@type agent: string/none
		
		@param agentSupport: agent support (default=False)
		@type agentSupport:	boolean
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param tlsSupport: tls support (default=False)
		@type tlsSupport:	boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		if not isinstance(destinationPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "destinationPort argument is not a integer (%s)" % type(destinationPort) )

		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																										debug=debug, realname=name, 
																										agentSupport=agentSupport, agent=agent, shared=shared,
																										caller=TestAdapterLib.caller(),
																										agentType=AGENT_TYPE_EXPECTED)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		
		self.parent = parent
		if tlsSupport:
			self.FTP_LIB = ftplib.FTP_TLS()
		else:
			self.FTP_LIB = ftplib.FTP()
		if debug:
			self.FTP_LIB.set_debuglevel(2)
		
		self.__connected = False
		self.__logged = False
		
		self.cfg = {}
		
		self.cfg['tls-support'] = tlsSupport
		
		self.cfg['dst-ip'] = destinationIp
		self.cfg['dst-port'] = destinationPort
		
		self.cfg['user'] = user
		self.cfg['password'] = password
		
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		if agentSupport:
			self.prepareAgent(data={'shared': shared})
			if self.agentIsReady(timeout=30) is None: 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent %s is not ready" % self.cfg['agent-name'] )
			self.TIMER_ALIVE_AGT.start()
			
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
		
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		if not self.cfg['agent-support'] :
			try:
				self.FTP_LIB.close()
			except Exception as e:
				pass
		else:
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
		elif data['cmd'] == CONNECT:
			self.__connected = True
			tpl = self.encapsule( ftp_event=templates.connected(), cmd=CONNECT )
			self.logRecvEvent( shortEvt = "connected", tplEvt = tpl )
			
		elif data['cmd'] == DISCONNECT:
			self.__connected = False
			self.__logged = False
			tpl = self.encapsule( ftp_event=templates.disconnected(), cmd=DISCONNECT )
			self.logRecvEvent( shortEvt = "disconnected", tplEvt = tpl )
			
		elif data['cmd'] == LOGIN:
			self.__logged = True 
			tpl = self.encapsule( ftp_event=templates.logged(), cmd=LOGIN )
			self.logRecvEvent( shortEvt = "logged", tplEvt = tpl )
			
		elif data['cmd'] == WELCOME:
			tpl = self.encapsule( ftp_event=templates.welcome(msg=data['msg']) )
			tpl.addRaw( data['msg'] )
			self.logRecvEvent( shortEvt = "welcome message", tplEvt = tpl )
			
		elif data['cmd'] == SECURE:
			tpl = self.encapsule( ftp_event=templates.secure() )
			self.logRecvEvent( shortEvt = "data secured", tplEvt = tpl )
			
		elif data['cmd'] == GET_FILE:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result'], content=data['content'] ), cmd=GET_FILE )
			tpl.addRaw( data['content'] )
			self.logRecvEvent( shortEvt = "file downloaded", tplEvt = tpl )
			
		elif data['cmd'] == CURRENT_PATH:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=CURRENT_PATH )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "current", tplEvt = tpl )
			
		elif data['cmd'] == PUT_FILE:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=PUT_FILE )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "file uploaded", tplEvt = tpl )

		elif data['cmd'] == SIZE_FILE:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=SIZE_FILE )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "file size returned", tplEvt = tpl )
			
		elif data['cmd'] == DELETE_FILE:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=DELETE_FILE )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "file deleted", tplEvt = tpl )
			
		elif data['cmd'] == RENAME_FILE:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=RENAME_FILE  )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "file renamed", tplEvt = tpl )
			
		elif data['cmd'] == ADD_FOLDER:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=ADD_FOLDER )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "added", tplEvt = tpl )
			
		elif data['cmd'] == RENAME_FOLDER:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result'] ) , cmd=RENAME_FOLDER )
			tpl.addRaw( data['result']  )
			self.logRecvEvent( shortEvt = "folder renamed", tplEvt = tpl )
			
		elif data['cmd'] == DELETE_FOLDER:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=DELETE_FOLDER )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "folder deleted", tplEvt = tpl )
			
		elif data['cmd'] == GOTO_FOLDER:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=GOTO_FOLDER )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "changed", tplEvt = tpl )
			
		elif data['cmd'] == LISTING_FOLDER:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result'] ), cmd=LISTING_FOLDER )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "folder listing", tplEvt = tpl )
			
		elif data['cmd'] == COMMAND:
			tpl = self.encapsule( ftp_event=templates.response(rsp=data['result']), cmd=COMMAND )
			tpl.addRaw( data['result'] )
			self.logRecvEvent( shortEvt = "response", tplEvt = tpl )
		elif data['cmd'] == WAIT_FILE:
			tpl = self.encapsule( ftp_event=templates.wait_file(path=data['path'], filename=data['filename'],
																		result=data['result']), cmd=WAIT_FILE )
			self.logRecvEvent( shortEvt = "wait file", tplEvt = tpl )
		elif data['cmd'] == WAIT_FOLDER:
			tpl = self.encapsule( ftp_event=templates.wait_folder(path=data['path'], folder=data['foldername'], 
																							result=data['result']), cmd=WAIT_FOLDER )
			self.logRecvEvent( shortEvt = "wait folder", tplEvt = tpl )
		else:
			self.error("unknown command received: %s" % data["cmd"])

	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if "cmd" in data:
			if data['cmd'] in [ CONNECT, DISCONNECT, LOGIN, GET_FILE, PUT_FILE,
																	RENAME_FILE, DELETE_FILE, ADD_FOLDER, DELETE_FOLDER,
																	GOTO_FOLDER, LISTING_FOLDER, RENAME_FOLDER,
																	COMMAND, SIZE_FILE, SECURE, WELCOME, CURRENT_PATH,
																	WAIT_FILE, WAIT_FOLDER	]:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=data['err-msg']), cmd=data['cmd'] )
				tpl.addRaw( data['err-msg'] )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				
			else:
				self.error("unknown command received: %s" % data["cmd"])
				
		else:
			self.error( 'Generic error: %s' % data )
		
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
		
	def encapsule(self, ftp_event, cmd=None):
		"""
		"""
		# ftp 
		layer_ftp = templates.ftp(cmd=cmd)
		layer_ftp.addMore(more=ftp_event)
		
		# prepare template
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplates.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_ftp)
		return tpl
		
	@doc_public
	def connect(self, passiveMode=True):
		"""
		Connect to ftp
		
		@param passiveMode: passive mode (nat traversal) (default=True)
		@type passiveMode:	boolean
		"""
		tpl = self.encapsule( ftp_event=templates.connection(ip=self.cfg['dst-ip'], port="%s" % self.cfg['dst-port'], 
																																								tls= "%s" % self.cfg['tls-support']), cmd=CONNECT )
		self.logSentEvent( shortEvt = "connection", tplEvt = tpl )

		if self.cfg['agent-support'] :
			cmd = { 'cmd':  CONNECT,  'passive': passiveMode,  'tls-support':  self.cfg['tls-support'] ,
									'dest-ip': self.cfg['dst-ip'] , 'dest-port': self.cfg['dst-port']}
			self.sendNotifyToAgent(data=cmd)		
		else:
			self.FTP_LIB.set_pasv(passiveMode)
			try:
				connected = self.FTP_LIB.connect(host=self.cfg['dst-ip'] , port=self.cfg['dst-port'] )
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=CONNECT )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				self.__connected = True
				
				tpl = self.encapsule( ftp_event=templates.connected(), cmd=CONNECT )
				self.logRecvEvent( shortEvt = "connected", tplEvt = tpl )
			
	@doc_public
	def disconnect(self):
		"""
		Disconnect from ftp
		"""
		if not self.__connected:
			self.warning( "not connected" )
			return
			
		self.__connected = False
		self.__logged = False
		
		tpl = self.encapsule( ftp_event=templates.disconnection(), cmd=DISCONNECT )
		self.logSentEvent( shortEvt = "disconnection", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  DISCONNECT }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				self.FTP_LIB.quit()
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=DISCONNECT )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.disconnected(), cmd=DISCONNECT )
				self.logRecvEvent( shortEvt = "disconnected", tplEvt = tpl )
		
	@doc_public
	def login(self):
		"""
		Login to ftp
		"""
		if not self.__connected:
			self.warning( "not connected" )
			return
			
		tpl = self.encapsule( ftp_event=templates.login(user=self.cfg['user'] , password=self.cfg['password'] ), cmd=LOGIN )
		self.logSentEvent( shortEvt = "login", tplEvt = tpl )

		# try to login
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  LOGIN, 'user': self.cfg['user'] , 'password': self.cfg['password'] }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				logged = self.FTP_LIB.login(user=self.cfg['user'] , passwd=self.cfg['password'] )
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=LOGIN )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				self.__logged = True 
				
				tpl = self.encapsule( ftp_event=templates.logged(), cmd=LOGIN )
				self.logRecvEvent( shortEvt = "logged", tplEvt = tpl )
		
			# get the welcome message if exists
			welcome = self.FTP_LIB.getwelcome()
			if len(welcome):
				tpl = self.encapsule( ftp_event=templates.welcome(msg=welcome) )
				tpl.addRaw( welcome )
				self.logRecvEvent( shortEvt = "welcome message", tplEvt = tpl )

			# init protected transfer for ssl
			if self.cfg['tls-support']:
				self.FTP_LIB.prot_p()
				tpl = self.encapsule( ftp_event=templates.secure() )
				self.logRecvEvent( shortEvt = "data secured", tplEvt = tpl )
				
	@doc_public
	def sizeOfFile(self, filename):
		"""
		Get the size of the file
		
		@param filename:  the name of the file to get the size
		@type filename: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
			
		tpl = self.encapsule( ftp_event=templates.size(filename=filename), cmd=SIZE_FILE )
		tpl.addRaw( filename )
		self.logSentEvent( shortEvt = "size file", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  SIZE_FILE, 'filename': filename }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.size(filename)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=SIZE_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp="%s" % rsp), cmd=SIZE_FILE )
				tpl.addRaw( "%s" % rsp )
				self.logRecvEvent( shortEvt = "file size returned", tplEvt = tpl )
				
	@doc_public
	def deleteFile(self, filename):
		"""
		Delete a file
		
		@param filename:  the name of the file to delete
		@type filename: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
			
		tpl = self.encapsule( ftp_event=templates.delete(filename=filename), cmd=DELETE_FILE )
		tpl.addRaw( filename )
		self.logSentEvent( shortEvt = "delete file", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  DELETE_FILE, 'filename': filename }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.delete(filename)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=DELETE_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=DELETE_FILE )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "file deleted", tplEvt = tpl )
	@doc_public
	def renameFile(self, currentFilename, newFilename):
		"""
		Rename a file
		
		@param currentFilename: current filename
		@type currentFilename: string
		
		@param newFilename: new filename
		@type newFilename: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.rename(fromFilename=currentFilename, toFilename=newFilename), cmd=RENAME_FILE )
		tpl.addRaw( currentFilename )
		self.logSentEvent( shortEvt = "rename file", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  RENAME_FILE, 'current-filename': currentFilename, 'new-filename': newFilename}
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.rename(currentFilename, newFilename)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=RENAME_FILE  )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=RENAME_FILE  )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "file renamed", tplEvt = tpl )
	@doc_public
	def gotoFolder(self, path):
		"""
		Goto the folder
		
		@param path: path folder
		@type path: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.goto(path=path), cmd=GOTO_FOLDER  )
		tpl.addRaw( path )
		self.logSentEvent( shortEvt = "goto", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  GOTO_FOLDER, 'path': path }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.cwd(path)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=GOTO_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=GOTO_FOLDER )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "changed", tplEvt = tpl )
			
	@doc_public
	def addFolder(self, path):
		"""
		Add a folder
		
		@param path: path folder
		@type path: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.add(path=path), cmd=ADD_FOLDER )
		tpl.addRaw( path )
		self.logSentEvent( shortEvt = "add", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  ADD_FOLDER, 'path': path }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.mkd(path)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=ADD_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=ADD_FOLDER )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "added", tplEvt = tpl )
	@doc_public
	def currentPath(self):
		"""
		Get the current path
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.current(), cmd=CURRENT_PATH )
		self.logSentEvent( shortEvt = "current path", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  CURRENT_PATH }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.pwd()
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=CURRENT_PATH )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=CURRENT_PATH )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "current", tplEvt = tpl )
	@doc_public
	def deleteFolder(self, path):
		"""
		Delete a folder
		
		@param path: path folder
		@type path: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.delete(path=path), cmd=DELETE_FOLDER )
		tpl.addRaw( path )
		self.logSentEvent( shortEvt = "delete folder", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  DELETE_FOLDER, 'path': path }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.rmd(path)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=DELETE_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=DELETE_FOLDER )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "folder deleted", tplEvt = tpl )
				
	@doc_public
	def renameFolder(self, currentPath, newPath):
		"""
		Rename a folder
		
		@param currentPath: current path folder
		@type currentPath: string
		
		@param newPath: new path folder
		@type newPath: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.rename(fromPath=currentPath, toPath=newPath), cmd=RENAME_FOLDER )
		tpl.addRaw( currentPath )
		self.logSentEvent( shortEvt = "rename folder", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  RENAME_FOLDER, 'current-path': currentPath, 'new-path': newPath  }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.rename(currentPath, newPath)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=RENAME_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp) , cmd=RENAME_FOLDER )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "folder renamed", tplEvt = tpl )
			
	@doc_public
	def listingFolder(self, path=None, extended=False):
		"""
		Listing the folder
		The current folder is the path is None
		
		@param path: current path folder
		@type path: string/none
		
		@param extended: extended mode (default=False)
		@type extended: boolean
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.listing(path=path), cmd=LISTING_FOLDER )
		if path is not None:
			tpl.addRaw( path )
		self.logSentEvent( shortEvt = "listing", tplEvt = tpl )

		if self.cfg['agent-support'] :
			cmd = { 'cmd':  LISTING_FOLDER, 'extended': extended  }
			if path is not None:
				cmd['path'] = path
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				ret = []
				if not extended:
					if path is not None:
						ret.extend(	self.FTP_LIB.nlst(path) )
					else:
						ret.extend(	self.FTP_LIB.nlst() )
				else:
					def append_data(line):
						ret.append( line )
					if path is None:
						self.FTP_LIB.dir(append_data)
					else:
						self.FTP_LIB.dir(path, append_data)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=LISTING_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp='\n'.join(ret) ), cmd=LISTING_FOLDER )
				tpl.addRaw( '\n'.join(ret) )
				self.logRecvEvent( shortEvt = "folder listing", tplEvt = tpl )
			

	@doc_public
	def command(self, cmd):
		"""
		Send a simple command string to the server and return the response string.
		
		@param cmd: ftp command to execute
		@type cmd: string
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.command(cmd=cmd), cmd=COMMAND )
		tpl.addRaw( cmd )
		self.logSentEvent( shortEvt = "command", tplEvt = tpl )

		if self.cfg['agent-support'] :
			cmd = { 'cmd':  COMMAND, 'cmd': cmd  }
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				rsp = self.FTP_LIB.sendcmd(cmd)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=COMMAND )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=COMMAND )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "response", tplEvt = tpl )
			
	@doc_public
	def getFile(self,  filename, toPrivate=False):
		"""
		Get file content 
		Retrieve the file in binary transfer mode
	
		@param filename: path of the file
		@type filename: string				
		
		@param toPrivate: save the file in the private area on True (default=False)
		@type toPrivate: boolean			
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.get(filename=filename), cmd=GET_FILE )
		tpl.addRaw( filename )
		self.logSentEvent( shortEvt = "get file", tplEvt = tpl )
		
		if self.cfg['agent-support'] :
			cmd = { 'cmd':  GET_FILE,  'filename': filename }
			self.sendNotifyToAgent(data=cmd)		
		else:
					read_data = []
					def handle_binary(more_data):
						read_data.append(more_data)

					try:
						resp = self.FTP_LIB.retrbinary("RETR %s" % filename, callback=handle_binary)
						read_data = b"".join(read_data)
					except Exception as e:
						tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=GET_FILE )
						tpl.addRaw( str(e) )
						self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
					else:
						if toPrivate:
							head, tail = os.path.split(filename)
							self.privateSaveFile(destname=tail, data=read_data)
							
						# log event
						tpl = self.encapsule( ftp_event=templates.response(rsp=resp, content=read_data), cmd=GET_FILE )
						tpl.addRaw( read_data )
						self.logRecvEvent( shortEvt = "file downloaded", tplEvt = tpl )
			
			
	@doc_public
	def putFile(self, toFilename, fromFilename=None, rawContent=None):
		"""
		Put file  in binary transfer mode.
		Read the file and upload to the file destination
		
		@param toFilename: path of the destination file
		@type toFilename: string			
		
		@param fromFilename: the file to upload
		@type fromFilename: string/None		
		
		@param rawContent: raw content to upload
		@type rawContent: string/None			
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		if fromFilename is None and rawContent is None:
			raise Exception("please to choose a type of upload")
		
		if fromFilename is not None:
			tpl = self.encapsule( ftp_event=templates.put(fromPath=fromFilename, toPath=toFilename), cmd=PUT_FILE )
			tpl.addRaw( fromFilename )
		if rawContent is not None:
			tpl = self.encapsule( ftp_event=templates.put(content=rawContent, toPath=toFilename) , cmd=PUT_FILE )
			tpl.addRaw( rawContent )
		self.logSentEvent( shortEvt = "put file", tplEvt = tpl )

		if self.cfg['agent-support'] :
			cmd = { 'cmd':  PUT_FILE,  'to-filename': toFilename }
			if fromFilename is not None:
				cmd['from-filename'] = fromFilename
			if rawContent is not None:
				cmd['raw-content'] = rawContent
			self.sendNotifyToAgent(data=cmd)		
		else:
			try:
				if rawContent is not None:
					myfile = io.BytesIO( rawContent )
				if fromFilename is not None:
					myfile = open(fromFilename, 'rb')
				rsp = self.FTP_LIB.storbinary('STOR %s' % toFilename, myfile)
				myfile.close()
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=PUT_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=rsp), cmd=PUT_FILE )
				tpl.addRaw( rsp )
				self.logRecvEvent( shortEvt = "file uploaded", tplEvt = tpl )

	@doc_public
	def waitForFile(self, path, filename, timeout=1.0, watchEvery=0.5):
		"""
		Wait for file, regexp supported on filename
	
		@param path: current path for file
		@type path: string
		
		@param filename: filename to lookup
		@type filename: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@param watchEvery: watch folder every xx seconds (default=0.5s)
		@type watchEvery: float		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = False
		if not self.__logged:
			self.warning( "not logged" )
			return
		tpl = self.encapsule( ftp_event=templates.wait_file(path=path, filename=filename), cmd=WAIT_FILE )
		if path is not None: tpl.addRaw( path )
		self.logSentEvent( shortEvt = "wait for file (%s sec.)" % timeout, tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  WAIT_FILE, 'path': path, 'filename': filename, 'timeout': timeout, 'watch-every': watchEvery}
			self.sendNotifyToAgent(data=agent_cmd)
		else:
			timeoutEvent = False
			startTime = time.time()
			try:
				true_filename=''
				list_files = []
				def append_data(line):
					list_files.append( line )
				while (not timeoutEvent):
					if (time.time() - startTime) >= timeout:
						timeoutEvent = True
					if not timeoutEvent:
						# list path
						list_files = []
						self.FTP_LIB.dir(path, append_data)
						for f in list_files:
							if not f.startswith('d'): # only file  'drwxr-xr-x 2 0 0 4096 Nov 12 16:51 toto'
								# extract filename
								#['-rw-r--r--', '1', '501', '501', '49', 'Jan', '20', '18:03', 'xxxxx.xml']
								tmp_filename = f.split()
								f_name = f.split(' '.join(tmp_filename[4:8]))[1].strip()

								if re.match( filename, f_name):
									true_filename = f_name
									ret = True
									timeoutEvent=True
					if not timeoutEvent: time.sleep(watchEvery)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=WAIT_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.wait_file(path=path, filename=true_filename, result=ret), cmd=WAIT_FILE )
				self.logRecvEvent( shortEvt = "wait file", tplEvt = tpl )
				
	@doc_public
	def waitForFolder(self, path, folder, timeout=1.0, watchEvery=0.5):
		"""
		Wait for folder, regexp supported on folder name
	
		@param path: current path for file
		@type path: string
		
		@param folder: folder to lookup
		@type folder: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param watchEvery: watch folder every xx seconds (default=0.5s)
		@type watchEvery: float				
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = False
		if not self.__logged:
			self.warning( "not logged" )
			return
		tpl = self.encapsule( ftp_event=templates.wait_folder(path=path, folder=folder), cmd=WAIT_FOLDER )
		if path is not None: tpl.addRaw( path )
		self.logSentEvent( shortEvt = "wait for folder (%s sec.)" % timeout, tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  WAIT_FOLDER, 'path': path, 'folder': folder, 'timeout': timeout, 'watch-every': watchEvery}
			self.sendNotifyToAgent(data=agent_cmd)
		else:
			true_folder=''
			timeoutEvent = False
			startTime = time.time()
			try:
				list_files = []
				def append_data(line):
					list_files.append( line )
				while (not timeoutEvent):
					if (time.time() - startTime) >= timeout:
						timeoutEvent = True
					if not timeoutEvent:
						# list path
						list_files = []
						self.FTP_LIB.dir(path, append_data)
						for f in list_files:
							if f.startswith('d'): # only file  'drwxr-xr-x 2 0 0 4096 Nov 12 16:51 toto'
								# extract filename
								#['-rw-r--r--', '1', '501', '501', '49', 'Jan', '20', '18:03', 'xxxxx.xml']
								tmp_filename = f.split()
								f_name = f.split(' '.join(tmp_filename[4:8]))[1].strip()

								if re.match( folder, f_name):
									true_folder = f_name
									ret = True
									timeoutEvent=True
					if not timeoutEvent: time.sleep(watchEvery)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=WAIT_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.wait_folder(path=path, folder=true_folder, result=ret), cmd=WAIT_FOLDER )
				self.logRecvEvent( shortEvt = "wait folder", tplEvt = tpl )
				
	@doc_public
	def isConnected(self, timeout=1.0):
		"""
		Waits to receive "is connected" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		tpl_expected = self.encapsule( ftp_event=templates.connected(), cmd=CONNECT)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def isLogged(self, timeout=1.0):
		"""
		Waits to receive "is logged" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		tpl_expected = self.encapsule( ftp_event=templates.logged(), cmd=LOGIN )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def isDataSecured(self, timeout=1.0):
		"""
		Waits to receive "welcome response" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		tpl_expected = self.encapsule( ftp_event=templates.secure() )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def isDisconnected(self, timeout=1.0):
		"""
		Waits to receive "is disconnected" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		tpl_expected = self.encapsule( ftp_event=templates.disconnected(), cmd=DISCONNECT )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def isFileRenamed(self, timeout=1.0):
		"""
		Waits to receive "renamed file" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=RENAME_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt

	@doc_public
	def isFileDeleted(self, timeout=1.0):
		"""
		Waits to receive "deleted file" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=DELETE_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasUploadedFile(self, timeout=1.0):
		"""
		Waits to receive "uploaded file" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=PUT_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasDownloadedFile(self, timeout=1.0):
		"""
		Waits to receive "downloaded" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=GET_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def isFolderDeleted(self, timeout=1.0):
		"""
		Waits to receive "deleted folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=DELETE_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def isFolderChanged(self, timeout=1.0):
		"""
		Waits to receive "changed folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=GOTO_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt

	@doc_public
	def isFolderRenamed(self, timeout=1.0):
		"""
		Waits to receive "folder renamed" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=RENAME_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def isFolderAdded(self, timeout=1.0):
		"""
		Waits to receive "added folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=ADD_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasFolderListing(self, timeout=1.0):
		"""
		Waits to receive "listing folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=LISTING_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	
	@doc_public
	def hasFileSize(self, timeout=1.0):
		"""
		Waits to receive "file size" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=SIZE_FILE)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasCurrentPath(self, timeout=1.0):
		"""
		Waits to receive "current path" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(), cmd=CURRENT_PATH)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasReceivedResponse(self, timeout=1.0):
		"""
		Waits to receive "response" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response() )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasReceivedError(self, timeout=1.0):
		"""
		Waits to receive "error response" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response_error() )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasReceivedWelcome(self, timeout=1.0):
		"""
		Waits to receive "welcome response" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.welcome() )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasDetectedFile(self, path=None,  filename=None, timeout=1.0):
		"""
		Waits to receive "detected file" event
		
		@param path: path of the file
		@type path: string/none	
		
		@param filename: filename detected
		@type filename: string/none	
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.wait_file(path=path, filename=filename, result=True), cmd=WAIT_FILE)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasDetectedFolder(self, path=None, folder=None, timeout=1.0):
		"""
		Waits to receive "detected folder" event
		
		@param path: path of the folder
		@type path: string/none	
		
		@param folder: folder detected
		@type folder: string/none	
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.wait_folder(path=path, folder=folder, result=True), cmd=WAIT_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def getFolder(self, fromPath, toPath=None, overwrite=False):
		"""
		Get folder content with recursive mode
		
		@param fromPath: remote path to download
		@type fromPath: string
		
		@param toPath: local destination, if none then the content is downloaded to the private area
		@type toPath: string/none
		
		@param overwrite: overwrite file/folder if already exists in local side
		@type overwrite: boolean
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.get_folder(fromPath=fromPath, toPath=toPath, overwrite=overwrite), cmd=GET_FOLDER )
		tpl.addRaw( fromPath )
		self.logSentEvent( shortEvt = "get folder", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  GET_FOLDER, 'from-path': fromPath, 'overwrite':  overwrite}
			if toPath is not None:
				agent_cmd[ 'to-path'] = toPath
			else:
				agent_cmd[ 'to-path'] = ''
			self.sendNotifyToAgent(data=agent_cmd)		
		else:
			try:
				rsp = 0 # nb files detected
				rsp = self.__getFolder(fromPath=fromPath, toPath=toPath, overwrite=overwrite)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=GET_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=str(rsp)), cmd=GET_FOLDER )
				tpl.addRaw( str(rsp) )
				self.logRecvEvent( shortEvt = "folder downloaded", tplEvt = tpl )
				
	def __getFolder(self, fromPath, toPath=None, overwrite=False):
		"""
		recursive get folder
		"""
		nb_file = 0
		
		list_files = []
		def append_data(line):
			list_files.append( line )

		def handle_binary(more_data):
			read_data.append(more_data)
			
		self.FTP_LIB.dir(fromPath, append_data)
		for f in list_files:
			# extract folder name
			tmp_filename = f.split()
			f_name = f.split(' '.join(tmp_filename[4:8]))[1].strip()
			
			if f.startswith('d'): # only file  'drwxr-xr-x 2 0 0 4096 Nov 12 16:51 toto'
	
				# add the remote folder in the local side
				try:
					if toPath is None:
						destFolder = "%s/%s" % (self.getDataStoragePath(), f_name)
					else:
						destFolder = "%s/%s" % (toPath, f_name)
					os.mkdir( destFolder, 0o755 )
				except OSError as e:
					if e.errno == errno.EEXIST and not overwrite:
						raise Exception("os error folder: %s" % e)
				# recursive call
				nb_file += self.__getFolder(fromPath="%s/%s/" % (fromPath,f_name), toPath=destFolder, overwrite=overwrite)
			
			else:
				nb_file += 1
				
				read_data = []
				resp = self.FTP_LIB.retrbinary("RETR %s/%s" % (fromPath,f_name) , callback=handle_binary)
				read_data = b"".join(read_data)
				
				# download the remote file to the local side
				try:
					if toPath is None:
						destFile = "%s/%s" % (self.getDataStoragePath(),f_name)
					else:
						destFile = "%s/%s" % (toPath,f_name)

					f = open(destFile, "wb")
					f.write(read_data)
					f.close()
				except OSError as e:
					if e.errno == errno.EEXIST and not overwrite:
						raise Exception("os error file: %s" % e)
				
		return nb_file
	@doc_public
	def putFolder(self, fromPath, toPath, overwrite=False):
		"""
		Put folder content with recursive mode
		
		@param fromPath: local path to upload
		@type fromPath: string
		
		@param toPath: remote destination
		@type toPath: string
		
		@param overwrite: overwrite file/folder if already exists in remote side
		@type overwrite: boolean
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( ftp_event=templates.put_folder(fromPath=fromPath, toPath=toPath, overwrite=overwrite), cmd=PUT_FOLDER )
		tpl.addRaw( fromPath )
		self.logSentEvent( shortEvt = "put folder", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  PUT_FOLDER, 'from-path': fromPath, 'overwrite':  overwrite}
			if toPath is not None:
				agent_cmd[ 'to-path'] = toPath
			else:
				agent_cmd[ 'to-path'] = ''
			self.sendNotifyToAgent(data=agent_cmd)		
		else:
			try:
				rsp = 0 # nb files uploaded
				rsp = self.__putFolder(fromPath=fromPath, toPath=toPath, overwrite=overwrite)
			except Exception as e:
				tpl = self.encapsule( ftp_event=templates.response_error(rsp=str(e)), cmd=PUT_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( ftp_event=templates.response(rsp=str(rsp)), cmd=PUT_FOLDER )
				tpl.addRaw( str(rsp) )
				self.logRecvEvent( shortEvt = "folder uploaded", tplEvt = tpl )
				
	def __putFolder(self, fromPath, toPath, overwrite=False):
		"""
		recursive put folder
		"""
		nb_file = 0
		for item in os.listdir(fromPath):
			itempath = os.path.join(fromPath, item)
			if os.path.isfile(itempath):
				# upload the local file to the remote
				try:
					myfile = open(itempath, 'rb')
					rsp = self.FTP_LIB.storbinary('STOR %s/%s' % (toPath, item) , myfile)
					myfile.close()
				except Exception as e:
					if not overwrite: raise e
				else:
					nb_file += 1
			elif os.path.isdir(itempath):
				# create folder in remote side
				destFolder = "%s/%s" % (toPath, item)
				try:
					rsp = self.FTP_LIB.mkd(destFolder)
				except Exception as e:
					if not overwrite: raise e
				# recursive call in this folder
				nb_file += self.__putFolder(fromPath=itempath, toPath=destFolder, overwrite=overwrite)
		return nb_file
		
	@doc_public
	def hasDownloadedFolder(self, timeout=1.0, nbFiles=None):
		"""
		Waiting downloaded event for folder
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param nbFiles: number of file succesfully downloaded
		@type nbFiles: none/int	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(rsp=nbFiles), cmd=GET_FOLDER )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasUploadedFolder(self, timeout=1.0, nbFiles=None):
		"""
		Waiting uploaded event for folder
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@param nbFiles: number of file succesfully uploaded
		@type nbFiles: none/int	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( ftp_event=templates.response(rsp=nbFiles), cmd=PUT_FOLDER )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt