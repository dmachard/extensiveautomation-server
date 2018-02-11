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
import TestExecutorLib.TestTemplatesLib as TestTemplates
from TestExecutorLib.TestExecutorLib import doc_public

import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import io
import time
import stat
import re
import os

import templates

AdapterSSH = sys.modules['SutAdapters.%s.SSH' % TestAdapter.getVersion()]

LISTING_FOLDER = "Listing Folder"
DELETE_FOLDER = "Delete Folder"
ADD_FOLDER = "Add Folder"
RENAME_FOLDER = "Rename Folder"

RENAME_FILE = "Rename File"
DELETE_FILE = "Delete File"

PUT_FILE = "Put File"
GET_FILE = "Get File"

WAIT_FILE = "Wait File"
WAIT_FOLDER = "Wait Folder"

PUT_FOLDER="Put Folder"
GET_FOLDER="Get Folder"

__NAME__="""SFTP"""

class Client(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, destIp= '127.0.0.1',  destPort=22,  bindIp='', bindPort=0,
													login='admin', password='admin',	privateKey=None, privateKeyPath=None, name=None, 
													debug=False, shared=False, agent=None, agentSupport=False, verbose=True):
		"""
		SFTP adapter based on SSH.
		Authentication by login/password or key are supported
		
		@param parent: parent testcase
		@type parent: testcase
		
		@param destIp: destination ip of the scp server
		@type destIp: string
		
		@param destPort: destination port of the scp server (default=22)
		@type destPort: integer
		
		@param bindIp: bind on specific ip, bind on all by default
		@type bindIp: string
		
		@param bindPort: bind on specific port, bind on all port by default
		@type bindPort: integer
		
		@param login: username to connect on it
		@type login: string
		
		@param password: password to connect on it
		@type password: string
		
		@param privateKey: string private key to use to authenticate, push your public key on the remote server
		@type privateKey: string/none
		
		@param privateKeyPath: path to the private key to use to authenticate, push your public key on the remote server
		@type privateKeyPath: string/none
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param agent: agent to use, ssh type expected
		@type agent: string/none
		
		@param agentSupport: agent support (default=False)
		@type agentSupport:	boolean
		"""
		if not isinstance(bindPort, int):
			raise TestAdapter.ValueException(TestAdapter.caller(), "bindPort argument is not a integer (%s)" % type(bindPort) )
		if not isinstance(destPort, int):
			raise TestAdapter.ValueException(TestAdapter.caller(), "destPort argument is not a integer (%s)" % type(destPort) )

		# init adapter
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared,
																								showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		
		self.parent = parent
		
		self.__connected = False
		self.__logged = False
		
		self.ADP_SSH = AdapterSSH.Client(parent=parent, login=login, password=password, privateKey=privateKey,  privateKeyPath=privateKeyPath,
																											bindIp=bindIp, bindPort=bindPort,  destIp=destIp, destPort=destPort, 
																											destHost='', socketTimeout=10.0, socketFamily=4, name=name, debug=debug,
																											logEventSent=True, logEventReceived=True, parentName=__NAME__, shared=shared,
																											sftpSupport=True, agent=agent,  agentSupport=agentSupport, verbose=verbose
																										)
		self.cfg = {}
		
		self.cfg['dst-ip'] = destIp
		self.cfg['dst-port'] = destPort
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		
		self.cfg['user'] = login
		self.cfg['password'] = password

		
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			
		self.__logged = False
	
		self.__checkConfig()
		
		# wrap function
		self.ADP_SSH.onSftpOpened = self.onSftpOpened
		self.ADP_SSH.onSftpEvent = self.onSftpEvent
		
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)

	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		self.ADP_SSH.onReset()

	def ssh(self):
		"""
		Return ssh level
		"""
		return self.ADP_SSH
	
	def onSftpEvent(self, event):
		"""
		"""
		if 'sftp-event' in event:
			
			if event['sftp-event'] == 'response-error' :
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=event['err']), cmd=event['cmd'] )
				tpl.addRaw( event['err'] )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				
			if event['sftp-event'] == 'folder-listing':
				tpl = self.encapsule( sftp_event=templates.response(rsp=event['rsp'] ), cmd=LISTING_FOLDER )
				tpl.addRaw( event['rsp'] )
				self.logRecvEvent( shortEvt = "folder listing", tplEvt = tpl )
				
			if event['sftp-event'] == 'folder-added':
				tpl = self.encapsule( sftp_event=templates.response(), cmd=ADD_FOLDER )
				self.logRecvEvent( shortEvt = "folder added", tplEvt = tpl )

			if event['sftp-event'] == 'file-renamed':
				tpl = self.encapsule( sftp_event=templates.response(), cmd=RENAME_FILE  )
				self.logRecvEvent( shortEvt = "file renamed", tplEvt = tpl )
				
			if event['sftp-event'] == 'file-deleted':
				tpl = self.encapsule( sftp_event=templates.response(), cmd=DELETE_FILE  )
				self.logRecvEvent( shortEvt = "file deleted", tplEvt = tpl )
				
			if event['sftp-event'] == 'folder-renamed':
				tpl = self.encapsule( sftp_event=templates.response() , cmd=RENAME_FOLDER )
				self.logRecvEvent( shortEvt = "folder renamed", tplEvt = tpl )
				
			if event['sftp-event'] == 'folder-deleted':
				tpl = self.encapsule( sftp_event=templates.response(), cmd=DELETE_FOLDER )
				self.logRecvEvent( shortEvt = "folder deleted", tplEvt = tpl )

			if event['sftp-event'] == 'file-downloaded':
				tpl = self.encapsule( sftp_event=templates.response(content=event['content']), cmd=GET_FILE )
				tpl.addRaw( event['content'] )
				self.logRecvEvent( shortEvt = "file downloaded", tplEvt = tpl )
				
			if event['sftp-event'] == 'file-uploaded':
				tpl = self.encapsule( sftp_event=templates.response(rsp=event['rsp']), cmd=PUT_FILE )
				tpl.addRaw( event['rsp'] )
				self.logRecvEvent( shortEvt = "file uploaded", tplEvt = tpl )
				
			if event['sftp-event'] == 'folder-downloaded':
				tpl = self.encapsule( sftp_event=templates.response(content=event['content']), cmd=GET_FOLDER )
				tpl.addRaw( event['content'] )
				self.logRecvEvent( shortEvt = "folder downloaded", tplEvt = tpl )
				
			if event['sftp-event'] == 'folder-uploaded':
				tpl = self.encapsule( sftp_event=templates.response(rsp=event['rsp']), cmd=PUT_FOLDER )
				tpl.addRaw( event['rsp'] )
				self.logRecvEvent( shortEvt = "folder uploaded", tplEvt = tpl )
				
			if event['sftp-event'] == 'wait-file':
				tpl = self.encapsule( sftp_event=templates.wait_file(path=event['path'], filename=event['filename'], result=event['result']), cmd=WAIT_FILE )
				self.logRecvEvent( shortEvt = "wait file", tplEvt = tpl )
				
			if event['sftp-event'] == 'wait-folder':
				tpl = self.encapsule( sftp_event=templates.wait_folder(path=event['path'], folder=event['folder'], result=event['result']), cmd=WAIT_FOLDER )
				self.logRecvEvent( shortEvt = "wait folder", tplEvt = tpl )
				
	def onSftpOpened(self):
		"""
		Reimplemented from ssh adapter
		"""
		self.__logged = True

	def onSftpFailed(self):
		"""
		Reimplemented from ssh adapter
		"""
		self.__logged = False
		
	def encapsule(self, sftp_event, cmd=None):
		"""
		"""
		# sftp 
		layer_sftp = templates.sftp(cmd=cmd)
		layer_sftp.addMore(more=sftp_event)
		
		# prepare template
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			
		tpl = TestTemplates.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=layer_sftp)
		return tpl
		
	@doc_public
	def connect(self):
		"""
		Connect to the SCP server
		Login is performed in automatic
		"""
		self.ADP_SSH.connect()
		
	@doc_public
	def disconnect(self):
		"""
		Disconnect from the SCP server
		"""
		self.ADP_SSH.disconnect()
		
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
		
		tpl = self.encapsule( sftp_event=templates.rename(fromFilename=currentFilename, toFilename=newFilename), cmd=RENAME_FILE )
		tpl.addRaw( currentFilename )
		self.logSentEvent( shortEvt = "rename file", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  RENAME_FILE, 'current-filename': currentFilename, 'new-filename': newFilename }
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				self.ssh().channel().rename(currentFilename, newFilename)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=RENAME_FILE  )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(), cmd=RENAME_FILE  )
				self.logRecvEvent( shortEvt = "file renamed", tplEvt = tpl )
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
			
		tpl = self.encapsule( sftp_event=templates.delete(filename=filename), cmd=DELETE_FILE )
		tpl.addRaw( filename )
		self.logSentEvent( shortEvt = "delete file", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  DELETE_FILE, 'filename': filename }
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				self.ssh().channel().remove(filename)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=DELETE_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(), cmd=DELETE_FILE )
				self.logRecvEvent( shortEvt = "file deleted", tplEvt = tpl )


	@doc_public
	def addFolder(self, path, mode=511):
		"""
		Add a folder
		
		@param path: path folder
		@type path: string
		
		@param mode: folder mode in octal (default=511 (0777))
		@type mode: integer
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( sftp_event=templates.add(path=path, mode="%s" % mode), cmd=ADD_FOLDER )
		tpl.addRaw( path )
		self.logSentEvent( shortEvt = "add", tplEvt = tpl )

		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  ADD_FOLDER, 'path': path, 'mode':  mode }
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				self.ssh().channel().mkdir(path, mode)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=ADD_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(), cmd=ADD_FOLDER )
				self.logRecvEvent( shortEvt = "folder added", tplEvt = tpl )
				
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
		
		tpl = self.encapsule( sftp_event=templates.delete(path=path), cmd=DELETE_FOLDER )
		tpl.addRaw( path )
		self.logSentEvent( shortEvt = "delete folder", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  DELETE_FOLDER, 'path': path }
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				self.ssh().channel().rmdir(path)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=DELETE_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(), cmd=DELETE_FOLDER )
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
		
		tpl = self.encapsule( sftp_event=templates.rename(fromPath=currentPath, toPath=newPath), cmd=RENAME_FOLDER )
		tpl.addRaw( currentPath )
		self.logSentEvent( shortEvt = "rename folder", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  RENAME_FOLDER, 'current-path': currentPath, 'new-path': newPath  }
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				self.ssh().channel().rename(currentPath, newPath)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=RENAME_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response() , cmd=RENAME_FOLDER )
				self.logRecvEvent( shortEvt = "folder renamed", tplEvt = tpl )
				
	@doc_public
	def listingFolder(self, path, extended=False):
		"""
		Listing the folder.
		
		@param path: current path folder
		@type path: string

		@param extended: extended mode (default=False)
		@type extended: boolean
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( sftp_event=templates.listing(path=path), cmd=LISTING_FOLDER )
		if path is not None: tpl.addRaw( path )
		self.logSentEvent( shortEvt = "listing", tplEvt = tpl )

		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  LISTING_FOLDER, 'path': path, 'extended': extended}
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				if extended:
					ret = []
					ret_tmp = self.ssh().channel().listdir_attr(path=path)
					for attr in ret_tmp:
						ret.append( str(attr) )
				else:
					ret = self.ssh().channel().listdir(path=path)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=LISTING_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(rsp='\n'.join(ret) ), cmd=LISTING_FOLDER )
				tpl.addRaw( '\n'.join(ret) )
				self.logRecvEvent( shortEvt = "folder listing", tplEvt = tpl )

	@doc_public
	def getFile(self,  filename, toPrivate=False):
		"""
		Get file content 
	
		@param filename: file name 
		@type filename: string				
		
		@param toPrivate: save the file in the private area on True (default=False)
		@type toPrivate: boolean			
		"""
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl = self.encapsule( sftp_event=templates.get(filename=filename), cmd=GET_FILE )
		tpl.addRaw( filename )
		self.logSentEvent( shortEvt = "get file", tplEvt = tpl )
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  GET_FILE, 'filename': filename}
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				myfile = io.BytesIO()
				self.ssh().channel().getfo(filename, myfile)
				read_data = myfile.getvalue() 
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=GET_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				if toPrivate:
					head, tail = os.path.split(filename)
					self.privateSaveFile(destname=tail, data=read_data)
					
				# log event
				tpl = self.encapsule( sftp_event=templates.response(content=read_data), cmd=GET_FILE )
				tpl.addRaw( read_data )
				self.logRecvEvent( shortEvt = "file downloaded", tplEvt = tpl )
				
	@doc_public
	def putFile(self, toFilename, fromFilename=None, rawContent=None):
		"""
		Put file  in binary transfer mode.
		
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
			tpl = self.encapsule( sftp_event=templates.put(fromPath=fromFilename, toPath=toFilename), cmd=PUT_FILE )
			tpl.addRaw( fromFilename )
		if rawContent is not None:
			tpl = self.encapsule( sftp_event=templates.put(content=rawContent, toPath=toFilename) , cmd=PUT_FILE )
			tpl.addRaw( rawContent )
		self.logSentEvent( shortEvt = "put file", tplEvt = tpl )
	
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  PUT_FILE, 'to-filename': toFilename, }
			if fromFilename is not None:
				agent_cmd[ 'from-filename'] = fromFilename
			else:
				agent_cmd[ 'from-filename'] = ''
			if rawContent is not None:
				agent_cmd[ 'raw-content'] = rawContent
			else:
				agent_cmd[ 'raw-content'] = ''
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				if rawContent is not None:
					myfile = io.BytesIO( rawContent )
					
				if fromFilename is not None:
					myfile = open(fromFilename, 'rb')
				
				rsp = self.ssh().channel().putfo(myfile, toFilename)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=PUT_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(rsp=str(rsp)), cmd=PUT_FILE )
				tpl.addRaw( str(rsp) )
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
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = False
		if not self.__logged:
			self.warning( "not logged" )
			return

		tpl = self.encapsule( sftp_event=templates.wait_file(path=path, filename=filename), cmd=WAIT_FILE )
		if path is not None: tpl.addRaw( path )
		self.logSentEvent( shortEvt = "wait for file (%s sec.)" % timeout, tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  WAIT_FILE, 'path': path, 'filename': filename, 'timeout': timeout, 'watch-every': watchEvery}
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			timeoutEvent = False
			startTime = time.time()
			try:
				true_filename = ''
				while (not timeoutEvent):
					if (time.time() - startTime) >= timeout:
						timeoutEvent = True
					if not timeoutEvent:
						# list path
						ret_tmp = self.ssh().channel().listdir_attr(path=path)
						for f in ret_tmp:
							if not stat.S_ISDIR(f.st_mode):
								if re.match( filename, f.filename):
									true_filename =  f.filename
									ret = True
									timeoutEvent=True
					if not timeoutEvent: time.sleep(watchEvery)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=WAIT_FILE )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.wait_file(path=path, filename=true_filename, result=ret), cmd=WAIT_FILE )
				self.logRecvEvent( shortEvt = "wait file", tplEvt = tpl )

	@doc_public
	def waitForFolder(self, path, folder, timeout=1.0, watchEvery=0.5):
		"""
		Wait for folder, regexp supported on folder name
		
		@param path: current path folder
		@type path: string
		
		@param folder: folder to look up
		@type folder: string		

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float				
	
		@param watchEvery: watch folder every xx seconds (default=0.5s)
		@type watchEvery: float				
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = False
		if not self.__logged:
			self.warning( "not logged" )
			return False

		tpl = self.encapsule( sftp_event=templates.wait_folder(path=path, folder=folder), cmd=WAIT_FOLDER)
		if path is not None: tpl.addRaw( path )
		self.logSentEvent( shortEvt = "wait for folder (%s sec.)" % timeout, tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  WAIT_FOLDER, 'path': path, 'folder': folder, 'timeout': timeout, 'watch-every': watchEvery}
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			timeoutEvent = False
			startTime = time.time()
			try:
				true_folder=''
				while (not timeoutEvent):
					if (time.time() - startTime) >= timeout:
						timeoutEvent = True
					if not timeoutEvent:
						# list path
						ret_tmp = self.ssh().channel().listdir_attr(path=path)
						for f in ret_tmp:
							if stat.S_ISDIR(f.st_mode):
								if re.match( folder, f.filename):
									true_folder = f.filename
									ret = True
									timeoutEvent=True
					if not timeoutEvent: time.sleep(watchEvery)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=WAIT_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.wait_folder(path=path, folder=true_folder, result=ret), cmd=WAIT_FOLDER )
				self.logRecvEvent( shortEvt = "wait folder", tplEvt = tpl )

	@doc_public
	def isConnected(self,timeout=1.0):
		"""
		Wait to receive "Connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_SSH.isConnected(timeout=timeout)
	@doc_public
	def isLogged(self,timeout=1.0):
		"""
		Wait to receive "logged" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_SSH.isChannelOpened(timeout=timeout)
		
	@doc_public
	def isDisconnected(self,timeout=1.0):
		"""
		Wait to receive "disconnected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )

		return self.ADP_SSH.isDisconnected(timeout=timeout)
	@doc_public
	def isFileRenamed(self, timeout=1.0):
		"""
		Wait to receive "renamed file" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
	
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=RENAME_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt

	@doc_public
	def isFileDeleted(self, timeout=1.0):
		"""
		Wait to receive "deleted file" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=DELETE_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasUploadedFile(self, timeout=1.0):
		"""
		Wait to receive "uploaded file" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=PUT_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasDownloadedFile(self, timeout=1.0):
		"""
		Wait to receive "downloaded" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=GET_FILE )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def isFolderDeleted(self, timeout=1.0):
		"""
		Wait to receive "deleted folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=DELETE_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt

	@doc_public
	def isFolderRenamed(self, timeout=1.0):
		"""
		Wait to receive "folder renamed" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=RENAME_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def isFolderAdded(self, timeout=1.0):
		"""
		Wait to receive "added folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=ADD_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
		
	@doc_public
	def hasFolderListing(self, timeout=1.0):
		"""
		Wait to receive "listing folder" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response(), cmd=LISTING_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasDetectedFile(self, path=None,  filename=None, timeout=1.0):
		"""
		Wait to receive "detected file" event
		
		@param path: path of the file
		@type path: string/none	
		
		@param filename: filename detected
		@type filename: string/none	
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.wait_file(path=path, filename=filename, result=True), cmd=WAIT_FILE)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasDetectedFolder(self, path=None, folder=None, timeout=1.0):
		"""
		Wait to receive "detected" folder event
		
		@param path: path of the folder
		@type path: string/none	
		
		@param folder: folder detected
		@type folder: string/none	
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.wait_folder(path=path, folder=folder, result=True), cmd=WAIT_FOLDER)
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasReceivedResponse(self, timeout=1.0):
		"""
		Wait to receive "response" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response() )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def hasReceivedError(self, timeout=1.0):
		"""
		Wait to receive "error response" event
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if not self.__logged:
			self.warning( "not logged" )
			return
		
		tpl_expected = self.encapsule( sftp_event=templates.response_error() )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
	@doc_public
	def doConnect(self, timeout=1.0):
		"""
		Do connect with authentification

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: True is successfully connected, false otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		ret = True
		self.connect()
		if self.isConnected(timeout=timeout) is None:
			ret = False
		if self.isLogged(timeout=timeout) is None:
			ret = False
		return ret
	@doc_public
	def doDisconnect(self, timeout=1.0):
		"""
		Do disconnect

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: True is successfully disconnected, false otherwise
		@rtype: boolean	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		self.disconnect()
		if self.isDisconnected(timeout=timeout) is None:
			ret = False
		return ret
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
		
		tpl = self.encapsule( sftp_event=templates.get_folder(fromPath=fromPath, toPath=toPath, overwrite=overwrite), cmd=GET_FOLDER )
		tpl.addRaw( fromPath )
		self.logSentEvent( shortEvt = "get folder", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  GET_FOLDER, 'from-path': fromPath, 'overwrite':  overwrite}
			if toPath is not None:
				agent_cmd[ 'to-path'] = toPath
			else:
				agent_cmd[ 'to-path'] = ''
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				rsp = 0 # nb files detected
				rsp = self.__getFolder(fromPath=fromPath, toPath=toPath, overwrite=overwrite)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=GET_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(rsp=str(rsp)), cmd=GET_FOLDER )
				tpl.addRaw( str(rsp) )
				self.logRecvEvent( shortEvt = "folder downloaded", tplEvt = tpl )
				
	def __getFolder(self, fromPath, toPath=None, overwrite=False):
		"""
		recursive get folder
		"""
		nb_file = 0
		ret_tmp = self.ssh().channel().listdir_attr(path=fromPath)
		for f in ret_tmp:
			# handle folder
			if stat.S_ISDIR(f.st_mode):
				# add the remote folder in the local side
				try:
					if toPath is None:
						destFolder = "%s/%s" % (self.getDataStoragePath(), f.filename)
					else:
						destFolder = "%s/%s" % (toPath, f.filename)
					os.mkdir( destFolder, 0755 )
				except OSError as e:
					if e.errno == errno.EEXIST and not overwrite:
						raise Exception("os error folder: %s" % e)
				# recursive call
				nb_file += self.__getFolder(fromPath="%s/%s/" % (fromPath,f.filename), toPath=destFolder, overwrite=overwrite)
			
			# handle files
			else:
				nb_file += 1
				
				myfile = io.BytesIO()
				self.ssh().channel().getfo( "%s/%s" % (fromPath,f.filename) , myfile)
				read_data = myfile.getvalue() 
				
				# download the remote file to the local side
				try:
					if toPath is None:
						destFile = "%s/%s" % (self.getDataStoragePath(),f.filename)
					else:
						destFile = "%s/%s" % (toPath,f.filename)

					f = open(destFile, "wb")
					f.write(read_data)
					f.close()
				except OSError as e:
					if e.errno == errno.EEXIST and not overwrite:
						raise Exception("os error file: %s" % e)
				del read_data
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
		
		tpl_expected = self.encapsule( sftp_event=templates.response(rsp=nbFiles), cmd=GET_FOLDER )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
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
		
		tpl = self.encapsule( sftp_event=templates.put_folder(fromPath=fromPath, toPath=toPath, overwrite=overwrite), cmd=PUT_FOLDER )
		tpl.addRaw( fromPath )
		self.logSentEvent( shortEvt = "put folder", tplEvt = tpl )
		
		if self.cfg['agent-support']:
			agent_cmd = {'cmd':  PUT_FOLDER, 'from-path': fromPath, 'overwrite':  overwrite}
			if toPath is not None:
				agent_cmd[ 'to-path'] = toPath
			else:
				agent_cmd[ 'to-path'] = ''
			self.ssh().notifyAgent(cfg=agent_cmd)
		else:
			try:
				rsp = 0 # nb files uploaded
				rsp = self.__putFolder(fromPath=fromPath, toPath=toPath, overwrite=overwrite)
			except Exception as e:
				tpl = self.encapsule( sftp_event=templates.response_error(rsp=str(e)), cmd=PUT_FOLDER )
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				tpl = self.encapsule( sftp_event=templates.response(rsp=str(rsp)), cmd=PUT_FOLDER )
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
					rsp = self.ssh().channel().putfo(myfile, "%s/%s" % (toPath, item) )
				except Exception as e:
					if not overwrite: raise e
				else:
					nb_file += 1
			elif os.path.isdir(itempath):
				# create folder in remote side
				destFolder = "%s/%s" % (toPath, item)
				try:
					self.ssh().channel().mkdir(destFolder , 511)
				except Exception as e:
					if not overwrite: raise e
				# recursive call in this folder
				nb_file += self.__putFolder(fromPath=itempath, toPath=destFolder, overwrite=overwrite)
		return nb_file
		
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
		
		tpl_expected = self.encapsule( sftp_event=templates.response(rsp=nbFiles), cmd=PUT_FOLDER )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		return evt
