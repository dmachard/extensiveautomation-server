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

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapterLib.getVersion()]
AdapterHTTP = sys.modules['SutAdapters.%s.HTTP' % TestAdapterLib.getVersion()]

LibraryAuth = sys.modules['SutLibraries.%s.Security' % TestLibraryLib.getVersion()]

import templates

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

__NAME__="""SOAP"""

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, name=None, bindIp='', bindPort=0, destinationIp='127.0.0.1', destinationPort=80, 
									debug=False, logEventSent=True, logEventReceived=True,
									xmlns0='http://schemas.xmlsoap.org/soap/envelope/', xmlns1='', xmlns2='', xmlns3='', xmlns4='',
									xmlns5='',  xmlns6='',  xmlns7='',  xmlns8='', 
									httpAgent='ExtensiveTesting', httpVersion='HTTP/1.1', httpConnection='close',
									agentSupport=False, agent=None, shared=False, httpAuthentication=False,
									proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False, proxyType=AdapterTCP.PROXY_HTTP, verbose=True,
									sslSupport=False, sslVersion=AdapterSSL.SSLv23, checkCert=AdapterSSL.CHECK_CERT_NO, caCerts=None, checkHost=False,
									hostCn=None, certfile=None, keyfile=None ):
		"""
		This class enables to send and receive SOAP data

		@param bindIp: bind ip (default='')
		@type bindIp: string
		
		@param bindPort: bind port (default=0)
		@type bindPort: integer
		
		@param destinationIp: destination ip (default=127.0.0.1)
		@type destinationIp: string
		
		@param destinationPort: destination port (default=80)
		@type destinationPort: integer
		
		@param xmlns0: xml namespace
		@type xmlns0: string
		
		@param xmlns1: xml namespace 
		@type xmlns1: string
		
		@param xmlns2: xml namespace
		@type xmlns2: string
		
		@param xmlns3: xml namespace
		@type xmlns3: string
		
		@param xmlns4: xml namespace
		@type xmlns4: string
		
		@param xmlns5: xml namespace
		@type xmlns5: string
		
		@param xmlns6: xml namespace
		@type xmlns6: string
		
		@param xmlns7: xml namespace
		@type xmlns7: string
		
		@param xmlns8: xml namespace
		@type xmlns8: string

		@param supportAuthentication: support digest authentication (default=False)
		@type supportAuthentication: boolean

		@param httpAgent: http agent (default value=ExtensiveTesting)
		@type httpAgent: string
		
		@param httpConnection: SutAdapters.HTTP.CONN_CLOSE (default) | SutAdapters.HTTP.CONN_KEEPALIVE | None
		@type httpConnection: strconstant
		
		@param httpVersion: SutAdapters.HTTP.VERSION_10 | SutAdapters.HTTP.VERSION_11 (default)
		@type httpVersion: strconstant
		
		@param sslSupport: ssl support (default=False)
		@type sslSupport: boolean

		@param sslVersion: SutAdapters.SSL.SSLv2 | SutAdapters.SSL.SSLv23 (default) | SutAdapters.SSL.SSLv3 | SutAdapters.SSL.TLSv1 | SutAdapters.SSL.TLSv11  | SutAdapters.SSL.TLSv12 
		@type sslVersion: strconstant

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

		@param agent: agent to use when this mode is activated
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
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent cannot be undefined!" )
			
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
				
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, 
																	realname=name, agentSupport=agentSupport, agent=agent, showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.ADP_HTTP = AdapterHTTP.Client(
																	parent=parent, bindIp=bindIp, bindPort=bindPort, destinationIp=destinationIp, destinationPort=destinationPort,
																	proxyIp=proxyIp, proxyPort=proxyPort, proxyHost=proxyHost, proxyEnabled=proxyEnabled, proxyType=proxyType,
																	destinationHost='', socketTimeout=300.0, socketFamily=4, saveContent=False,
																	httpVersion=httpVersion, httpAgent=httpAgent, httpConnection=httpConnection,
																	httpChunckedData=False, sslSupport=sslSupport, sslVersion=sslVersion, checkCert=checkCert, debug=debug,
																	caCerts=caCerts, checkHost=checkHost, hostCn=hostCn,
																	logEventSent=False, logEventReceived=False, agentSupport=agentSupport,
																	agent=agent, shared=shared, name=name, verbose=verbose, keyfile=keyfile, certfile=certfile
										)
		self.ADP_HTTP.handleIncomingResponse = self.handleIncomingResponse	
		
		self.codecX2D = Xml2Dict.Xml2Dict(coding='utf8')
		self.codecD2X = Dict2Xml.Dict2Xml(coding = 'utf8')
		
		self.cfg = {}
		self.cfg['xmlns0'] = xmlns0
		self.cfg['xmlns1'] = xmlns1
		self.cfg['xmlns2'] = xmlns2
		self.cfg['xmlns3'] = xmlns3
		self.cfg['xmlns4'] = xmlns4
		self.cfg['xmlns5'] = xmlns5
		self.cfg['xmlns6'] = xmlns6
		self.cfg['xmlns7'] = xmlns7
		self.cfg['xmlns8'] = xmlns8
		self.cfg['http-agent'] = httpAgent
		self.cfg['agent-support'] = agentSupport
		self.cfg['http_support_authentication'] = httpAuthentication
		self.cfg['http_digest_timeout'] = 10.0
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		
		# digest library
		self.rfc2617 = LibraryAuth.Digest(parent=parent, debug=debug)
		
		self.__checkConfig()

	def http(self):
		"""
		Return http adapter
		"""
		return self.ADP_HTTP

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	

	def decodeList(self, data):
		"""
		"""
		list_layer = TestTemplatesLib.TemplateLayer(name='')
		for i in xrange(len(data)):
			layer_data2 = None
			if isinstance(data[i], dict):
				if len(data[i]):
					layer_data2 = self.decodeSoap(data=data[i])
			elif isinstance(data[i], list):
				if len(data[i]):
					layer_data2 = self.decodeList(data=data[i])
			else:
				if len(data[i]):
					layer_data2 = data[i]
			if layer_data2 is not None:
				list_layer.addKey(name=str(i), data=layer_data2)
		return 	list_layer
	
	def decodeSoap(self, data, firstCall=False):
		"""
		"""
		name=''
		if firstCall: name='SOAP'
		layerSoap = TestTemplatesLib.TemplateLayer(name=name)
		for k,v in data.items():
			if isinstance(v, dict):
				if k.startswith('@') and not len(v):
					pass
				else:
					layer_data = self.decodeSoap(data=v)
					layerSoap.addKey(name=k, data=layer_data)
			elif isinstance(v, list):
				list_layer = self.decodeList(data=v)
				if list_layer.getLenItems():
					layerSoap.addKey(name=k, data=list_layer)
			else:
				layerSoap.addKey(name=k, data=v)
		return layerSoap
		
	def handleIncomingResponse(self, data, lower):
		"""
		"""
		try:
			# extract body
			http_body = lower.get('HTTP', 'body')
			
			# encode template
			try:
				new_xml = self.__removeNamespace(soapXml=http_body)
				layerSoap = self.decodeSoap(data=eval(new_xml), firstCall=True )
				layerSoap.addRaw(http_body)
			except Exception as e:
				self.debug( 'decode soap body error: %s' % str(e) )
				if self.logEventReceived:
					lower.addRaw( data )
					self.logRecvEvent( shortEvt = data, tplEvt = lower ) # log event 		
			else:
				lower.addLayer(layer=layerSoap)
				
				if self.logEventReceived:
					lower.addRaw( data )
					self.logRecvEvent( shortEvt = 'SOAP response', tplEvt = lower ) # log event 		
		except Exception as e:
			self.error( 'internal error on incoming message: %s' % str(e) )
	
	def onIncomingResponse(self, summary, lower):
		"""
		"""
		pass
		
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
		Wait connected event until the end of the timeout
		
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
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isConnected(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
											sourcePort=sourcePort, destinationPort=destinationPort)

	@doc_public
	def isDisconnected(self, timeout=1.0, byServer=False, versionIp=None, sourceIp=None, destinationIp=None, 
										sourcePort=None, destinationPort=None):
		"""
		Wait disconnected event until the end of the timeout
		
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
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isDisconnected(timeout=timeout, byServer=byServer, versionIp=versionIp, 
						sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
						
	def __removeNamespace(self, soapXml):
		"""
		"""
		decoded = self.codecX2D.parseXml( soapXml.strip() )

		new_xml_ns =  unicode(decoded)
		if len(self.cfg['xmlns0']):
			new_xml_ns= unicode(decoded).replace('{%s}' % self.cfg['xmlns0'], '')
		if len(self.cfg['xmlns1']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns1'], '')
		if len(self.cfg['xmlns2']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns2'], '')
		if len(self.cfg['xmlns3']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns3'], '')
		if len(self.cfg['xmlns4']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns4'], '')
		if len(self.cfg['xmlns5']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns5'], '')
		if len(self.cfg['xmlns6']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns6'], '')
		if len(self.cfg['xmlns7']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns7'], '')
		if len(self.cfg['xmlns8']):
			new_xml_ns = unicode(new_xml_ns).replace('{%s}' % self.cfg['xmlns8'], '')
		return new_xml_ns
	
	@doc_public
	def sendSoapRaw(self, http, soap):
		"""
		Send SOAP and HTTP data as raw 
		
		@param http: http part to send
		@type http: string
		
		@param soap: soap part to send
		@type soap: string
		"""
		try:
			# encode template
			try:
				new_xml = self.__removeNamespace(soapXml=soap)
			except Exception as e:
				raise Exception("Cannot remove namespace: %s" % str(e))	
			try:
				layerSoap = self.decodeSoap(data=eval(new_xml), firstCall=True )
				layerSoap.addRaw(soap)
			except Exception as e:
				raise Exception("Cannot encode SOAP request: %s" % str(e))	
			
			# Send request	
			try:
				req_tpl = self.ADP_HTTP.constructTemplateRequest(rawHttp=http+soap)
				lower = self.ADP_HTTP.sendRequest(tpl=req_tpl)
			except Exception as e:
				raise Exception("http failed: %s" % str(e))	
			
			lower.addLayer( layerSoap )

			# Log event
			if self.logEventSent:
				lower.addRaw(raw=http+soap)
				self.logSentEvent( shortEvt = 'SOAP request', tplEvt = lower ) 
		except Exception as e:
			self.error( 'unable to send soap raw: %s' % str(e) )
			

	@doc_public
	def sendSoap(self, uri, host, soap, httpHeaders = {}, method='POST', login='', password='', httpVersion="HTTP/1.1"):
		"""
		Send SOAP data with a HTTP request, http headers can be added
		
		@param uri: uri
		@type uri: string
		
		@param host: host
		@type host: string
		
		@param soap: soap
		@type soap: string
		
		@param httpHeaders: http headers to add
		@type httpHeaders: dict

		@param method: http method (default=POST)
		@type method: string
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		"""
		try:
			# encode template
			try:
				new_xml = self.__removeNamespace(soapXml=soap)
			except Exception as e:
				raise Exception("Cannot remove namespace: %s" % str(e))	
			try:
				layerSoap = self.decodeSoap(data=eval(new_xml), firstCall=True )
				layerSoap.addRaw(soap)
			except Exception as e:
				raise Exception("Cannot encode SOAP request: %s" % str(e))	
			
			# Send request	
			try:
				hdrs = { "Host": host , "User-Agent": self.cfg['http-agent'] ,  
									"Content-Length": str(len(soap)), "Content-Type": "text/xml; charset=utf-8" }
				hdrs.update(httpHeaders)
				req_tpl = AdapterHTTP.request(method=method, uri=uri, version=httpVersion, headers=hdrs, body=soap)
				lower = self.ADP_HTTP.sendRequest(tpl=req_tpl)

			except Exception as e:
				raise Exception("http failed: %s" % str(e))	
			
			lower.addLayer( layerSoap )
			lower.addRaw( lower.get('HTTP').getRaw()  )
			
			# Log event
			if self.logEventSent:
				lower.addRaw(raw=lower.getRaw())
				self.logSentEvent( shortEvt = 'SOAP request', tplEvt = lower ) 
				
			# support authentification	
			if self.cfg['http_support_authentication'] :
				rsp = self.hasReceivedHttpResponse(httpCode="401", httpPhrase=None, 
															headers={ 'www-authenticate': TestOperatorsLib.Any()}, timeout=self.cfg['http_digest_timeout'])
				if rsp is not None:
					# extract authentication
					self.debug('authentication to do, extract www-authen header')
					http_hdrs = rsp.get('HTTP', 'headers')
					www_hdr = http_hdrs.get('www-authenticate')
		
					# respond to the challenge
					challenge = self.rfc2617.decode(challenge=www_hdr)
					rsp, cnonce, nc = self.rfc2617.compute( username=login, password=password, realm=challenge['realm'],
																									nonce=challenge['nonce'], 	method=method, uri=uri , qop=challenge['qop'],
																									algo=challenge['algorithm'], body=None )
					challengeRsp = self.rfc2617.encode( username=login, realm=challenge['realm'], nonce=challenge['nonce'],
																							uri=uri, response=rsp, cnonce=cnonce, nc=nc,
																							qop=challenge['qop'], algo=challenge['algorithm'])
					
					hdrs.update( {'authorization': challengeRsp} )	
					try:
						req_tpl = AdapterHTTP.request(method=method, uri=uri, version=httpVersion, headers=hdrs, body=soap)
						lower = self.ADP_HTTP.sendRequest(tpl=req_tpl)
					except Exception as e:
						raise Exception("http digest failed: %s" % str(e))	
					
					lower.addLayer( layerSoap )
					lower.addRaw( lower.get('HTTP').getRaw()  )
					
					# Log event
					if self.logEventSent:
						lower.addRaw(raw=lower.getRaw())
						self.logSentEvent( shortEvt = 'SOAP request', tplEvt = lower ) 
						
				
		except Exception as e:
			self.error( 'unable to send soap: %s' % str(e) )
			
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
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	
	@doc_public
	def hasReceivedSoapResponse(self, httpCode="200", httpPhrase="OK", timeout=1.0):
		"""
		Wait to receive "soap response" until the end of the timeout.
		
		@param httpCode: http code (default=200)
		@type httpCode: string
		
		@param httpPhrase: http phrase (default=OK)
		@type httpPhrase: string
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.ADP_HTTP.tcp().cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		headers = {'content-type': TestOperatorsLib.Contains(needle='xml', AND=True, OR=False) }
		tpl.addLayer( AdapterHTTP.response( version="HTTP/1.1", code=httpCode, phrase=httpPhrase, headers=headers ) )
		tpl.addLayer( templates.body() )
		
		return self.hasReceivedResponse(expected=tpl, timeout=timeout)
	@doc_public
	def hasReceivedHttpResponse(self, httpCode="200", httpPhrase="OK", headers=None, timeout=1.0):
		"""
		Wait to receive "http response" until the end of the timeout.
		
		@param httpCode: http code (default=200)
		@type httpCode: string
		
		@param httpPhrase: http phrase (default=OK)
		@type httpPhrase: string
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.ADP_HTTP.tcp().cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl.addLayer( AdapterHTTP.response( version="HTTP/1.1", code=httpCode, phrase=httpPhrase, headers=headers ) )
		
		return self.hasReceivedResponse(expected=tpl, timeout=timeout)