#!/usr/bin/env python
# -*- coding=utf-8 -*-

# ------------------------------------------------------------------
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

#AdapterIP = sys.modules['SutAdapters.%s.IP' % TestAdapter.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapter.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapter.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapter.getVersion()]
AdapterHTTP = sys.modules['SutAdapters.%s.HTTP' % TestAdapter.getVersion()]

LibraryCodecs = sys.modules['SutLibraries.%s.Codecs' % TestLibrary.getVersion()]

import templates

__NAME__="""REST"""

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, name=None, bindIp='', bindPort=0, destinationIp='127.0.0.1', destinationPort=80, debug=False,
												logEventSent=True, logEventReceived=True, 
												httpAgent='ExtensiveTesting',  httpVersion='HTTP/1.1', httpConnection='close',
												sslSupport=False,  sslVersion=AdapterSSL.SSLv23, checkCert=AdapterSSL.CHECK_CERT_NO, caCerts=None, checkHost=False,
												hostCn=None, 	agentSupport=False, agent=None, 	shared=False,
												proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False, proxyType=AdapterTCP.PROXY_HTTP,
												certfile=None, keyfile=None	):
		"""
		This class enables to send and receive REST data

		@param bindIp: bind ip (default='')
		@type bindIp: string
		
		@param bindPort: bind port (default=0)
		@type bindPort: integer
		
		@param destinationIp: destination ip (default=127.0.0.1)
		@type destinationIp: string
		
		@param destinationPort: destination port (default=80)
		@type destinationPort: integer

		@param httpAgent: http agent (default value=ExtensiveTesting)
		@type httpAgent: string
		
		@param httpConnection: SutAdapters.HTTP.CONN_CLOSE (default) | SutAdapters.HTTP.CONN_KEEPALIVE | None
		@type httpConnection: strconstant
		
		@param httpVersion: SutAdapters.HTTP.VERSION_10 | SutAdapters.HTTP.VERSION_11 (default)
		@type httpVersion: strconstant
		
		@param sslSupport: ssl support (default=False)
		@type sslSupport: boolean

		@param checkCert: SutAdapters.SSL.CHECK_CERT_NO (default) | SutAdapters.SSL.CHECK_CERT_OPTIONAL | SutAdapters.SSL.CHECK_CERT_REQUIRED
		@type checkCert: strconstant
		
		@param caCerts: path to the certificate authority (default=None)
		@type caCerts: string/none
		
		@param checkHost: validate the common name field (default=False)
		@type checkHost: boolean
		
		@param hostCn: common name to check (default=None)
		@type hostCn: string/none
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated, socket type expected
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean

		@param proxyType: SutAdapters.TCP.PROXY_HTTP (default) | SutAdapters.TCP.PROXY_SOCKS4 | SutAdapters.TCP.PROXY_SOCKS5 
		@type proxyType: strconstant
		
		@param proxyIp: proxy ip
		@type proxyIp: string

		@param proxyPort: proxy port
		@type proxyPort: integer

		@param proxyHost: proxy host (automatic dns resolution)
		@type proxyHost: string
		
		@param proxyEnabled: True to support proxy (default=False)
		@type proxyEnabled: boolean	

		@param certfile: path to the cert file (default=None)
		@type certfile: string/none

		@param keyfile: path to the key file (default=None)
		@type keyfile: string/none
		"""
		# check agent
		if agentSupport and agent is None:
			raise TestAdapter.ValueException(TestAdapter.caller(), "Agent cannot be undefined!" )
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapter.ValueException(TestAdapter.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapter.ValueException(TestAdapter.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )

		# init adapter
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, 
																	realname=name, agentSupport=agentSupport, agent=agent)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived

		self.ADP_HTTP = AdapterHTTP.Client(
																	parent=parent, bindIp=bindIp, bindPort=bindPort, destinationIp=destinationIp, destinationPort=destinationPort,
																	proxyIp=proxyIp, proxyPort=proxyPort, proxyHost=proxyHost, proxyEnabled=proxyEnabled, proxyType=proxyType,
																	destinationHost='', socketTimeout=300.0, socketFamily=4, saveContent=False,
																	httpVersion=httpVersion, httpAgent=httpAgent, httpConnection=httpConnection,
																	httpChunckedData=False, sslSupport=sslSupport, sslVersion=sslVersion, checkCert=checkCert, 
																	caCerts=caCerts, checkHost=checkHost, hostCn=hostCn, debug=debug,
																	logEventSent=False, logEventReceived=False, agentSupport=agentSupport,
																	agent=agent, shared=shared, name=name, keyfile=keyfile, certfile=certfile
										)
		self.ADP_HTTP.handleIncomingResponse = self.handleIncomingResponse	

		self.LIB_JSON = LibraryCodecs.JSON(parent=parent, name=name, debug=debug, ignoreErrors=True)
		
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		
		self.cfg = {}
		self.cfg['http-agent'] = httpAgent
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.__checkConfig()

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
		
	def decodeList(self, data, firstCall=False):
		"""
		Private function
		"""
		name=''
		if firstCall: name='REST'
		list_layer = TestTemplates.TemplateLayer(name=name)
		for i in xrange(len(data)):
			layer_data2 = None
			if isinstance(data[i], dict):
				if len(data[i]):
					layer_data2 = self.decodeDict(data=data[i])
			elif isinstance(data[i], list):
				if len(data[i]):
					layer_data2 = self.decodeList(data=data[i])
			else:
				if isinstance(data[i], int):
					data[i] = str(data[i])
				if isinstance(data[i], float):
					data[i] = str(data[i])
				if len(data[i]):
					layer_data2 = data[i]
			if layer_data2 is not None:
				list_layer.addKey(name=str(i), data=layer_data2)
		return 	list_layer
	
	def decodeDict(self, data, firstCall=False):
		"""
		Private function
		"""
		name=''
		if firstCall: name='REST'
		layerRest = TestTemplates.TemplateLayer(name=name)
		for k,v in data.items():
			if isinstance(v, dict):
				if k.startswith('@') and not len(v):
					pass
				else:
					layer_data = self.decodeDict(data=v)
					layerRest.addKey(name=k, data=layer_data)
			elif isinstance(v, list):
				list_layer = self.decodeList(data=v)
				if list_layer.getLenItems():
					layerRest.addKey(name=k, data=list_layer)
			else:
				if v is None: v = 'null'
				layerRest.addKey(name=k, data="%s" % v)
		return layerRest
		
	def handleIncomingResponse(self, data, lower):
		"""
		Called on incoming response
		"""
		try:
			# extract body
			http_body = lower.get('HTTP', 'body')

			# encode template
			try:
				new_json= self.LIB_JSON.decode(json_str=http_body)
			except Exception as e:
				self.debug( 'decode body as json error: %s' % str(e) )
			else:
				try:
					if isinstance(new_json, list):
						layerRest = self.decodeList(data=new_json, firstCall=True )
					elif isinstance(new_json, dict):
						layerRest = self.decodeDict(data=new_json, firstCall=True )
					else:
						raise Exception('unsupported json type on response: %s' % type(new_json) )
					layerRest.addRaw(http_body)
				except Exception as e:
					self.debug( 'encode json to template error: %s' % str(e) )
					if self.logEventReceived:
						lower.addRaw( data )
						self.logRecvEvent( shortEvt = data, tplEvt = lower ) # log event 		
				else:
					lower.addLayer(layer=layerRest)
					
					if self.logEventReceived:
						lower.addRaw( data )
						self.logRecvEvent( shortEvt = 'REST response', tplEvt = lower ) # log event 		
		except Exception as e:
			self.error( 'internal error on incoming message: %s' % str(e) )
		
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		self.ADP_HTTP.onReset()
		
	@doc_public
	def connect(self):
		"""
		Start the TCP connection
		"""
		self.ADP_HTTP.connect()
	
	@doc_public
	def disconnect(self):
		"""
		Close the TCP connection
		"""
		self.ADP_HTTP.disconnect()
	
	@doc_public
	def isConnected(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isConnected(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
											sourcePort=sourcePort, destinationPort=destinationPort)

	@doc_public
	def isDisconnected(self, timeout=1.0, byServer=False, versionIp=None, sourceIp=None, destinationIp=None, 
										sourcePort=None, destinationPort=None):
		"""
		Wait to receive "disconnected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@param byServer: indicate if the disconnection is initiated by the server
		@type byServer: boolean		

		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isDisconnected(timeout=timeout, byServer=byServer, versionIp=versionIp, 
						sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
	
	@doc_public
	def sendRestRaw(self, http, json='', timeout=1.0):
		"""
		Send REST and HTTP data as raw 
		
		@param http: http part to send
		@type http: string
		
		@param json: json part to send
		@type json: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		"""
		# connect ?
		if not self.ADP_HTTP.tcp().connected:
			if not self.ADP_HTTP.connection(timeout=timeout):
				return
				
		try:
			# encode template
			try:
				if len(json):
					str_json= self.LIB_JSON.encode(json_obj=json)
					if isinstance(json, list):
						layerRest = self.decodeList(data=json, firstCall=True )
					elif isinstance(json, dict):
						layerRest = self.decodeDict(data=json, firstCall=True )
					else:
						raise Exception('unsupported json type: %s' % type(json) )
					layerRest.addRaw(str_json)
				else:
					str_json=''
			except Exception as e:
				raise Exception("Cannot encode REST request: %s" % str(e))	
			
			# Send request	
			try:
				req_tpl = self.ADP_HTTP.constructTemplateRequest(rawHttp=http+json)
				lower = self.ADP_HTTP.sendRequest(tpl=req_tpl)
			except Exception as e:
				raise Exception("http failed: %s" % str(e))	
			
			if len(json):
				lower.addLayer( layerRest )

			# Log event
			if self.logEventSent:
				lower.addRaw(raw=http+json)
				self.logSentEvent( shortEvt = 'REST request', tplEvt = lower ) 
		except Exception as e:
			self.error( 'unable to send rest raw: %s' % str(e) )
			
	@doc_public
	def sendRest(self, uri, host, json='', method='POST',  httpHeaders = {}, body=None, timeout=1.0):
		"""
		Send REST data, http headers can be added
		
		@param uri: uri
		@type uri: string
		
		@param host: host
		@type host: string
		
		@param method: POST | GET | PUT | DELETE (default=POST)
		@type method: string
		
		@param json: json
		@type json: string
		
		@param httpHeaders: http headers to add
		@type httpHeaders: dict
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		"""
		# connect ?
		if not self.ADP_HTTP.tcp().connected:
			if not self.ADP_HTTP.connection(timeout=timeout):
				return

		try:
			# encode template
			try:
				if len(json):
					str_json= self.LIB_JSON.encode(json_obj=json)
					if isinstance(json, list):
						layerRest = self.decodeList(data=json, firstCall=True )
					elif isinstance(json, dict):
						layerRest = self.decodeDict(data=json, firstCall=True )
					else:
						raise Exception('unsupported json type: %s' % type(json) )
					layerRest.addRaw(str_json)
				else:
					if body is not None:
						str_json = body
					else:
						str_json = ''
			except Exception as e:
				raise Exception("Cannot encode REST request: %s" % str(e))	
			
			# Send request	
			try:
				hdrs = { "Host": host , "User-Agent": self.cfg['http-agent'] , "Content-Length": str(len(str_json)) }
				if len(json):
					hdrs.update( {"Content-Type": "application/json; charset=utf-8" } )
				hdrs.update(httpHeaders)
				req_tpl = AdapterHTTP.request(method=method, uri=uri, version="HTTP/1.1", headers=hdrs, body=str_json)
				lower = self.ADP_HTTP.sendRequest(tpl=req_tpl)
			except Exception as e:
				raise Exception("http failed: %s" % str(e))	
			
			if len(json):
				lower.addLayer( layerRest )
			
			# Log event
			if self.logEventSent:
				lower.addRaw(raw=lower.getLayer("HTTP").getRaw() )
				self.logSentEvent( shortEvt = 'REST request', tplEvt = lower ) 
		except Exception as e:
			self.error( 'unable to send rest: %s' % str(e) )
			
	@doc_public
	def hasReceivedResponse(self, expected, timeout=1.0):
		"""
		Wait to receive "generic response" until the end of the timeout.
		
		@param expected: response template
		@type expected: templatemessage

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	
	@doc_public
	def hasReceivedRestResponse(self, httpCode="200", httpPhrase="OK", httpVersion='HTTP/1.1', timeout=1.0, httpHeaders={}, httpBody=None):
		"""
		Wait to receive "rest response" until the end of the timeout.
		
		@param httpCode: http code (default=200)
		@type httpCode: string
		
		@param httpPhrase: http phrase (default=OK)
		@type httpPhrase: string
		
		@param httpVersion: http version (default=HTTP/1.1)
		@type httpVersion: string
		
		@param httpHeaders: expected http headers
		@type httpHeaders: dict
		
		@param httpBody: expected body (default=None)
		@type httpBody: string/none
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float

		@return: http response
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = TestTemplates.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )		
		if self.ADP_HTTP.tcp().cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		headers = {'content-type': TestOperators.Contains(needle='application/json', AND=True, OR=False) }
		headers.update(httpHeaders)
		tpl.addLayer( AdapterHTTP.response( version=httpVersion, code=httpCode, phrase=httpPhrase, headers=headers, body=httpBody) )
		tpl.addLayer( templates.response() )
		
		return self.hasReceivedResponse(expected=tpl, timeout=timeout)