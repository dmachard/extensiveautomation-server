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

import MySQLdb
import templates
import datetime

__NAME__="""MYSQL"""

MYSQL_PORT=3306

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='database'

class FakePtr(object):
	def close(self): pass

class MySQL(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, host='127.0.0.1', user='', password='', port=MYSQL_PORT, name=None, verbose=True,
												debug=False, shared=False, agent=None, agentSupport=False, logEventSent=True, logEventReceived=True):
		"""
		Adapter to connect on MSSQL database

		@param host: host address
		@type host: string
		
		@param user: user
		@type user: string
		
		@param password: password
		@type password: string
		
		@param port: destination port (default=SutAdapters.Database.MYSQL_PORT)
		@type port: intconstant
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean

		@param agent: agent to use
		@type agent: string/none
		
		@param agentSupport: agent support (default=False)
		@type agentSupport:	boolean
		"""
		# check agent
		if agentSupport and agent is None: 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent cannot be undefined!" )	
			
		# check the agent
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
				
		if not isinstance(port, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "port argument is not a integer (%s)" % type(port) )

		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, realname=name,
																											showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose)
		
		self.parent = parent
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.cfg = {}
		self.cfg['host']=host
		self.cfg['user']=user
		self.cfg['password']=password
		self.cfg['port']=port

		self.connected = False
		
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			self.cfg['agent-type'] = agent['type']
			
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
																																
		self.__checkConfig()
		
		self.connPtr = None
		
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
		try:
			if self.connPtr is not None: self.connPtr.close()
		except Exception as e:
			pass
		if self.cfg['agent-support']:
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
			
			elif data['cmd'] == 'Connect':
				self.connPtr  = FakePtr()
				tpl = templates.db( host=data['host'], port=data['port'], user=data['user'], password=data['password'], 
																more=templates.connected() )
				self.logRecvEvent( shortEvt = "connected", tplEvt = self.encapsule(db_event=tpl) )
			
			elif data['cmd'] == 'Disconnect':
				tpl = templates.db(host=data['host'], port=data['port'], user=data['user'], 
															password=data['password'], more=templates.disconnected() )
				self.logRecvEvent( shortEvt = "disconnected", tplEvt = self.encapsule(db_event=tpl) )
				self.connPtr = None
				
			elif data['cmd'] == 'Query':
				tpl = templates.db( host=data['host'], port=data['port'], user=data['user'],  password=data['password'], 
																		more=templates.response(row=data['row'], rowIndex=data['row-index'], rowMax=data['row-max']) )
				if self.logEventReceived:
					self.logRecvEvent( shortEvt = "row", tplEvt = self.encapsule(db_event=tpl) )
	
				self.handleIncomingRow(lower=self.encapsule(db_event=tpl))

			elif data['cmd'] == 'Executed':
				tpl = templates.db( host=data['host'], port=data['port'], user=data['user'],  password=data['password'], 
																	 more=templates.executed(nbChanged=data['nb-changed'])  )
				self.logRecvEvent( shortEvt = "executed", tplEvt = self.encapsule(db_event=tpl) )
				
			elif data['cmd'] == 'Terminated':
					tpl = templates.db( host=data['host'], port=data['port'], user=data['user'],  password=data['password'],
																		 more=templates.terminated(nbRow=['nb-rows'])  )
					self.logRecvEvent( shortEvt = "terminated", tplEvt = self.encapsule(db_event=tpl) )
				
			else:
				self.error("unknown command received: %s" % data["cmd"])
		else:
			self.error("no cmd detected %s" % data)

	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['cmd'] in [ 'Disconnect', 'Connect', 'Query', 'Terminated', 'Executed' ]:
			if 'database-err-msg' in data:
				self.onError( data['database-err-msg'] )
			if 'generic-err-msg'  in data:
				self.error( "%s" % data['generic-err-msg'] )
		else:
			self.error("database event unknown on error: %s" % data['cmd'] )	
			
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
	def prepareAgent(self, data):
		"""
		prepare agent
		"""
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
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
	def encapsule(self, db_event):
		"""
		"""
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplatesLib.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=db_event)
		return tpl
	def onGenericError(self, err):
		"""
		"""
		pass
		
	def onError(self, err):
		"""
		"""
		code, msg = err
		# log received event
		tpl = self.encapsule(db_event=templates.db(more=templates.error(code=code, msg=msg) ))
		tpl.addRaw(msg)
		self.logRecvEvent( shortEvt = "error", tplEvt = tpl )
		
	@doc_public
	def connect(self, dbName, timeout=5):
		"""
		Connect to the database
		
		@param dbName: database name
		@type dbName: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: integer		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.debug('connect to the db')
		
		# log connect event
		tpl = templates.db( host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], password=self.cfg['password'], more=templates.connect(db=dbName) )
		self.logSentEvent( shortEvt = "connect", tplEvt = self.encapsule(db_event=tpl) )
		
		# connect
		if self.cfg['agent-support']:
			remote_cfg = { 'cmd': 'Connect', 'db-name': dbName , 'dbtype': 'mysql', 'user': self.cfg['user'],
															'password':self.cfg['password'],  'host':  self.cfg['host'], 'port': self.cfg['port'],
															'timeout': int(timeout) }
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.connPtr = MySQLdb.connect( host = self.cfg['host'],  user = self.cfg['user'], passwd = self.cfg['password'], 
																				port=self.cfg['port'], connect_timeout=int(timeout), db = dbName )
			except MySQLdb.Error as e:
				self.onError( e )
			except Exception as e:
				self.error( "unable to connect, generic error: %s" % str(e) )
			else:
				# log connected event
				tpl = templates.db( host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], password=self.cfg['password'], 
																more=templates.connected() )
				self.logRecvEvent( shortEvt = "connected", tplEvt = self.encapsule(db_event=tpl) )

	@doc_public
	def disconnect(self):
		"""
		Disconnect from the database
		"""
		if self.connPtr is None:
			self.warning('connect first to the database')
		else:
			self.debug('disconnect from the db')
			
			# log disconnect event
			tpl = templates.db( host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], 
														password=self.cfg['password'], more=templates.disconnect() )
			self.logSentEvent( shortEvt = "disconnect", tplEvt = self.encapsule(db_event=tpl) )
			
			if self.cfg['agent-support']:
				remote_cfg = { 'cmd': 'Disconnect', 'user': self.cfg['user'],
															'password':self.cfg['password'],  'host':  self.cfg['host'], 'port': self.cfg['port'] }
				self.sendNotifyToAgent(data=remote_cfg)
			else:
				try:
					self.connPtr.close()
				except MySQLdb.Error as e:
					self.onError( e )
				except Exception as e:
					self.error( str(e) )
				else:
					# log disconnected event
					tpl = templates.db(host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], 
															password=self.cfg['password'], more=templates.disconnected() )
					self.logRecvEvent( shortEvt = "disconnected", tplEvt = self.encapsule(db_event=tpl) )
					self.connPtr = None
		
	@doc_public
	def doQuery(self, query, timeout=1.0, dbName=''):
		"""
		Do query

		@param query: sql query
		@type query: string			

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@param dbName: database name
		@type dbName: string		
		
		@return: result of the query, none otherwise
		@rtype: none/event				
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = None
		
		# do connect ?
		internalConnect = False
		if self.connPtr is None:
			internalConnect = True
			self.connect(dbName=dbName, timeout=timeout)
			if self.isConnected(timeout=timeout) is None:
				ret = None
		
		self.query(query=query)
		ret = self.hasReceivedRow(timeout=timeout) 
		
		# do disconnect
		if internalConnect:
			self.disconnect()
			if self.isDisconnected(timeout=timeout) is None:
				ret = None
		return ret

	@doc_public
	def doConnect(self, dbName, timeout=1.0):
		"""
		Do connect

		@param dbName: database name
		@type dbName: string		
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: True is successfully connected, false otherwise
		@rtype: boolean		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		self.connect(dbName=dbName, timeout=timeout)
		if self.isConnected(timeout=timeout) is None:
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
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		self.disconnect()
		if self.isDisconnected(timeout=timeout) is None:
			ret = False
		return ret
		
	@doc_public
	def query(self, query, queryName=None):
		"""
		Query the database
		
		@param query: sql query
		@type query: string			
		
		@param queryName: query identifier
		@type queryName: string/none	
		"""
		if self.connPtr is None:
			self.warning('connect first to the database')
		else:
			self.debug('query db')
			# log query event
			tpl = templates.db(host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], password=self.cfg['password'], more=templates.query(query=query) )
			self.logSentEvent( shortEvt = "query", tplEvt = self.encapsule(db_event=tpl) )
			
			if self.cfg['agent-support']:
				remote_cfg = { 'cmd': 'Query', 'query':  query, 'user': self.cfg['user'],
															'password':self.cfg['password'],  'host':  self.cfg['host'], 'port': self.cfg['port'] }
				if queryName is not None:
					remote_cfg['query-name'] = queryName
				self.sendNotifyToAgent(data=remote_cfg)
			else:
				try:
					cursor = self.connPtr.cursor()
					cursor.execute ( query )
	
					i = 0
					# log response event
					tpl = templates.db( host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], password=self.cfg['password'], 
																		 more=templates.executed(nbChanged=str(cursor.rowcount))  )
					self.logRecvEvent( shortEvt = "executed", tplEvt = self.encapsule(db_event=tpl) )
					
					try:
						row =cursor.fetchone()
						while row:
							i += 1
							self.debug( row )
							# as dict
							fields = map(lambda x:x[0], cursor.description)
							ret = dict(zip(fields,row))
							
							# each value as str
							ret_str = {}
							if queryName is not None:
								ret_str['query-name'] = queryName
							for k,v in ret.items():
								ret_str[k] = str(v)
		
							# log response event
							tpl = templates.db( host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], 
																	password=self.cfg['password'], more=templates.response(row=ret_str, rowIndex=i, rowMax=cursor.rowcount) )
							if self.logEventReceived:
								self.logRecvEvent( shortEvt = "row", tplEvt = self.encapsule(db_event=tpl) )
		
							self.handleIncomingRow(lower=self.encapsule(db_event=tpl))
							
							row = cursor.fetchone()
					except MySQLdb.Error as e:
						pass # no more to read 
						
					# log response event
					tpl = templates.db( host=self.cfg['host'], port=self.cfg['port'], user=self.cfg['user'], password=self.cfg['password'], 
																		 more=templates.terminated(nbRow=i)  )
					self.logRecvEvent( shortEvt = "terminated", tplEvt = self.encapsule(db_event=tpl) )
					
					
					# close the cursor and commit
					cursor.close ()
					self.connPtr.commit ()
				except MySQLdb.Error as e:
					self.onError( e )
				except Exception as e:
					self.error( str(e) )
				else:
					pass
	def handleIncomingRow(self, lower):
		"""
		Function to reimplement
		"""
		pass	
	@doc_public
	def isConnected(self, timeout=1.0):
		"""
		Waits to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.db( host=self.cfg['host'], port=self.cfg['port'], more=templates.connected() )
		evt = self.received( expected = self.encapsule(db_event=expected), timeout = timeout )
		return evt
	
	@doc_public
	def isExecuted(self, timeout=1.0, status=None, nbChanged=None):
		"""
		Waits to receive "executed" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@param status: status message
		@type status: string/none			
		
		@param nbChanged: number of row modified
		@type nbChanged: string/none			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.db(host=self.cfg['host'], port=self.cfg['port'], more=templates.executed(status=status, nbChanged=nbChanged) )
		evt = self.received( expected = self.encapsule(db_event=expected), timeout = timeout )
		return evt
	@doc_public
	def isTerminated(self, timeout=1.0, nbRow=None):
		"""
		Waits to receive "terminated" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@param nbRow: number of row received
		@type nbRow: string/none			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.db(host=self.cfg['host'], port=self.cfg['port'], more=templates.terminated(nbRow=nbRow) )
		evt = self.received( expected = self.encapsule(db_event=expected), timeout = timeout )
		return evt
	@doc_public
	def isDisconnected(self, timeout=1.0):
		"""
		Waits to receive "disconnected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.db(host=self.cfg['host'], port=self.cfg['port'], more=templates.disconnected() )
		evt = self.received( expected = self.encapsule(db_event=expected), timeout = timeout )
		return evt
	
	@doc_public
	def hasReceivedRow(self, timeout=1.0, row=None, rowIndex=None, rowMax=None):
		"""
		Waits to receive "response" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.db(host=self.cfg['host'], port=self.cfg['port'], more=templates.response(row=row, rowIndex=None, rowMax=None) )
		evt = self.received( expected = self.encapsule(db_event=expected), timeout = timeout )
		return evt
