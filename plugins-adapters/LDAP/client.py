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

import templates
import ldap
import ldap.modlist as modlist

__NAME__="""LDAP"""

AGENT_EVENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='ldap'

class Client(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, ip, dn, password, port=389, sslSupport=False,
											name=None, debug=False, shared=False, 
											agentSupport=False, agent=None):
		"""
		LDAP Client 

		@param parent: parent testcase
		@type parent: testcase
		
		@param ip: ip destination
		@type ip: string
		
		@param dn: distinguished name
		@type dn: string
		
		@param password: password
		@type password: string
		
		@param port: port (default=389)
		@type port: integer
		
		@param sslSupport: ssl support (default=False)
		@type sslSupport: integer
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param agentSupport: agent support (default=False)
		@type agentSupport: boolean
		
		@param agent: agent to use (default=None)
		@type agent: string/none
		"""
		# check the agent
		if agentSupport and agent is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent cannot be undefined!" )
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapter.ValueException(TestAdapter.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name,
																							agentSupport=agentSupport, agent=agent, shared=shared)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		if agent is not None:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = agentSupport
		
		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		if agent is not None:
			if self.cfg['agent-support']:
				self.prepareAgent(data={'shared': shared})
				if self.agentIsReady(timeout=30) is None: raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
				self.TIMER_ALIVE_AGT.start()

		self.cfg["ip"] = ip
		self.cfg["port"] = port
		self.cfg["dn"] = dn
		self.cfg["password"] = password
		self.cfg["ssl-support"] = sslSupport

		self.con = None
		self.__connected = False
		
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
		if self.cfg['agent-support'] :
			# stop timer
			self.TIMER_ALIVE_AGT.stop()
			# cleanup remote agent
			self.resetAgent()

	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if data['cmd'] == AGENT_EVENT_INITIALIZED:
			tpl = TestTemplates.TemplateMessage()
			layer = TestTemplates.TemplateLayer('AGENT')
			layer.addKey("ready", True)
			tpl.addLayer(layer= layer)
			self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )	

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

	def encapsule(self, ldap_event):
		"""
		"""
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
		
		tpl = TestTemplates.TemplateMessage()
		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		tpl.addLayer(layer=ldap_event)
		return tpl
		
	@doc_public
	def connect(self):
		"""
		LDAP connection
		"""
		# log connect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_connect(dn=self.cfg['dn']) )
		self.logSentEvent( shortEvt = "connection", tplEvt = self.encapsule(ldap_event=tpl) )
		
		try:
			if self.cfg["ssl-support"]:
				self.con = ldap.initialize('ldaps://%s:%s'%(self.cfg['ip'],self.cfg['port']))
			else:
				self.con = ldap.initialize('ldap://%s:%s'%(self.cfg['ip'],self.cfg['port']))
			self.con.bind_s(self.cfg['dn'], self.cfg['password'])
			
			self.__connected = True
		except ldap.INVALID_CREDENTIALS as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap connect - authentication error", tplEvt = self.encapsule(ldap_event=tpl) )
		except ldap.LDAPError as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap connect - error", tplEvt = self.encapsule(ldap_event=tpl) )
		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap connect - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		
		else:
			# log connected event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_connected() )
			self.logRecvEvent( shortEvt = "connected", tplEvt = self.encapsule(ldap_event=tpl) )

	@doc_public
	def disconnect(self):
		"""
		LDAP disconnection
		"""
		if not self.__connected: return
		
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_disconnect() )
		self.logSentEvent( shortEvt = "disconnection", tplEvt = self.encapsule(ldap_event=tpl) )
	
		try:
			self.con.unbind()
			
			self.__connected = False
		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap disconnect - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			# log disconnected event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_disconnected() )
			self.logRecvEvent( shortEvt = "disconnected", tplEvt = self.encapsule(ldap_event=tpl) )
			
	@doc_public
	def add(self, baseDn, record=[]):
		"""
		LDAP add query
		
		@param baseDn: baseDN for search
		@type baseDn: string
		
		@param record: record to add 
		@type record: list
		"""
		if not self.__connected: return
		
		r_tpl= TestTemplates.Template(parent=None)
		r_layer= r_tpl.prepareLayer(name="", data=record)
			
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_add(bdn=baseDn, record=r_layer) )
		self.logSentEvent( shortEvt = "add", tplEvt = self.encapsule(ldap_event=tpl) )
		
		try:
			
			self.con.add_s(baseDn,record)
			
		except ldap.ALREADY_EXISTS as e:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % str(e) ) )
			self.logRecvEvent( shortEvt = "ldap add - entry already exits", tplEvt = self.encapsule(ldap_event=tpl) )
		except Exception as e:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % str(e) ) )
			self.logRecvEvent( shortEvt = "ldap add - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_response() )
			self.logRecvEvent( shortEvt = "add success", tplEvt = self.encapsule(ldap_event=tpl) )

	@doc_public
	def search(self, baseDn, filter="(objectClass=*)", attrs = []):
		"""
		LDAP search query
		
		@param baseDn: baseDN for search
		@type baseDn: string
		
		@param filter: default (objectClass=*) 
		@type filter: string
		
		@param attrs: attributes 
		@type attrs: list
		"""
		if not self.__connected: return
		
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_search(bdn=baseDn, filter=filter) )
		self.logSentEvent( shortEvt = "search", tplEvt = self.encapsule(ldap_event=tpl) )
		
		try:
			res = self.con.search_s(baseDn, ldap.SCOPE_SUBTREE, filter,attrs)
		except ldap.NO_SUCH_OBJECT:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap search - no such object", tplEvt = self.encapsule(ldap_event=tpl) )
		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap search - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			# log connected event
			r_tpl= TestTemplates.Template(parent=None)
			r_layer= r_tpl.prepareLayer(name="", data=res)
			
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_response(results=r_layer) )
			self.logRecvEvent( shortEvt = "results (%s)" % len(res), tplEvt = self.encapsule(ldap_event=tpl) )

	@doc_public
	def updateAttribute(self, baseDn, attrName, value):
		"""
		Update attribute
		
		@param baseDn: baseDn
		@type baseDn: string
		
		@param attrName: attrName 
		@type attrName: string
		
		@param value: value to manipulate
		@type value: string
		"""
		if not self.__connected: return
		
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_update_attribute(bdn=baseDn, 
																																																																				attr=attrName, 
																																																																				value=value) )
		self.logSentEvent( shortEvt = "update attribute", tplEvt = self.encapsule(ldap_event=tpl) )
		
		try:
			mod_attrs = [(ldap.MOD_REPLACE, attrName, value)]
			result = self.con.modify_s(baseDn, mod_attrs)

		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "update attribute - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_response() )
			self.logRecvEvent( shortEvt = "update attribute success", tplEvt = self.encapsule(ldap_event=tpl) )
	@doc_public
	def addAttribute(self, baseDn, attrName, value):
		"""
		Add attribute
		
		@param baseDn: baseDn
		@type baseDn: string
		
		@param attrName: attrName 
		@type attrName: string
		
		@param value: value to manipulate
		@type value: string
		"""
		if not self.__connected: return
		
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_add_attribute(bdn=baseDn, 
																																																																				attr=attrName, 
																																																																				value=value) )
		self.logSentEvent( shortEvt = "add attribute", tplEvt = self.encapsule(ldap_event=tpl) )
		
		try:
			mod_attrs = [(ldap.MOD_ADD, attrName, value)]
			result = self.con.modify_s(baseDn, mod_attrs)

		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "add attribute - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_response() )
			self.logRecvEvent( shortEvt = "add attribute success", tplEvt = self.encapsule(ldap_event=tpl) )
	@doc_public
	def deleteAttribute(self, baseDn, attrName, value):
		"""
		Delete attribute
		
		@param baseDn: baseDn
		@type baseDn: string
		
		@param attrName: attrName 
		@type attrName: string
		
		@param value: value to manipulate
		@type value: string
		"""
		if not self.__connected: return
		
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_delete_attribute(bdn=baseDn, 
																																																																				attr=attrName,
																																																																				value=value) )
		self.logSentEvent( shortEvt = "delete attribute", tplEvt = self.encapsule(ldap_event=tpl) )
		
		try:
			mod_attrs = [(ldap.MOD_DELETE, attrName, value)]
			result = self.con.modify_s(baseDn, mod_attrs)

		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap delete attribute - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_response() )
			self.logRecvEvent( shortEvt = "delete attribute success", tplEvt = self.encapsule(ldap_event=tpl) )
			
	@doc_public
	def delete(self, baseDn):
		"""
		Delete entry
		
		@param baseDn: baseDn
		@type baseDn: string
		"""
		if not self.__connected: return
		
		# log disconnect event
		tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_delete() )
		self.logSentEvent( shortEvt = "delete", tplEvt = self.encapsule(ldap_event=tpl) )
	
		try:
			result = self.con.delete(baseDn)
		except Exception as e:
			# log error event
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'],  more=templates.ldap_error(details="%s" % e) )
			self.logRecvEvent( shortEvt = "ldap delete - generic error", tplEvt = self.encapsule(ldap_event=tpl) )
		else:
			tpl = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_response() )
			self.logRecvEvent( shortEvt = "deleted", tplEvt = self.encapsule(ldap_event=tpl) )

	@doc_public
	def hasReceivedResponse(self, timeout=1.0):
		"""
		Wait ldap response event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template

		layer_ldap = templates.ldap()
		layer_ldap.addMore(more=templates.ldap_response())
		
		expected = TestTemplates.TemplateMessage()
		expected.addLayer(layer=layer_ldap)

		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

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
		
		expected = templates.ldap( ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_connected() )
		evt = self.received( expected = self.encapsule(ldap_event=expected), timeout = timeout )
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
		
		expected = templates.ldap(ip=self.cfg['ip'], port=self.cfg['port'], more=templates.ldap_disconnected() )
		evt = self.received( expected = self.encapsule(ldap_event=expected), timeout = timeout )
		return evt