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
import copy

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapterLib.getVersion()]
AdapterSOCKS = sys.modules['SutAdapters.%s.SOCKS' % TestAdapterLib.getVersion()]

LibraryAuth = sys.modules['SutLibraries.%s.Security' % TestLibraryLib.getVersion()]

import codec
import templates

__NAME__="""HTTP"""

VERSION_10 = 'HTTP/1.0'
VERSION_11 = 'HTTP/1.1'

CONN_CLOSE = "close"
CONN_KEEPALIVE = "keepalive"

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent,  destinationIp= '127.0.0.1', 
								bindIp = '0.0.0.0', bindPort=0, name=None,
								destinationPort=80,  destinationHost='', 
								proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False, proxyType=AdapterTCP.PROXY_HTTP,
								socketTimeout=300.0, socketFamily=AdapterIP.IPv4, saveContent=False, supportAuthentication=False,
								httpVersion=VERSION_11, httpAgent='ExtensiveTesting', httpConnection=CONN_CLOSE, httpChunckedData=False,
								sslSupport=False, sslVersion=AdapterSSL.SSLv23, checkCert=AdapterSSL.CHECK_CERT_NO, caCerts=None, checkHost=False,
								debug=False, logEventSent=True, logEventReceived=True, websocketMode=False,  hostCn=None,
								truncateBody=False, agentSupport=False, agent=None, shared=False, strictMode=False,
								octetStreamSupport=True, manStreamSupport=True, verbose=True, keyfile=None,certfile=None):
		"""
		This class enables to send/receive HTTP requests and response
		SSL and proxy (socks4, 5 and http) support.
		Chunked or content-length data support.
		Basic, digest authentication support.
		This class inherit from the TCP adapter.
		
		@param parent: testcase 
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param bindIp: source ip (default='')
		@type bindIp: string

		@param bindPort: source port (default=0)
		@type bindPort: integer

		@param destinationIp: destination ip
		@type destinationIp: string

		@param destinationPort: destination port (default: port 80)
		@type destinationPort: integer

		@param destinationHost: destination host (dns resolution)
		@type destinationHost: string
		
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
		
		@param websocketMode: websocket mode (default=False)
		@type websocketMode: boolean
		
		@param supportAuthentication: support http authentication (basic, digest) (default=False)
		@type supportAuthentication: boolean
		
		@param socketTimeout: connection timeout in second (default=300s)
		@type socketTimeout: float

		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: intconstant

		@param httpVersion: SutAdapters.HTTP.VERSION_10 | SutAdapters.HTTP.VERSION_11 (default)
		@type httpVersion: strconstant

		@param httpAgent: user agent (default=ExtensiveTesting)
		@type httpAgent: string

		@param httpConnection: SutAdapters.HTTP.CONN_CLOSE (default) | SutAdapters.HTTP.CONN_KEEPALIVE | None
		@type httpConnection: strconstant

		@param httpChunckedData: cut the body in chunk and add automatically the transfer encoding header (default=False)
		@type httpChunckedData: boolean
	
		@param saveContent: save content in a file
		@type saveContent: boolean
		
		@param sslSupport: activate SSL channel (default=False)
		@type sslSupport: boolean

		@param sslVersion: SutAdapters.SSL.SSLv2 | SutAdapters.SSL.SSLv23 (default)  | SutAdapters.SSL.SSLv3 | SutAdapters.SSL.TLSv1 | SutAdapters.SSL.TLSv11  | SutAdapters.SSL.TLSv12 
		@type sslVersion: strconstant

		@param checkCert: SutAdapters.SSL.CHECK_CERT_NO (default) | SutAdapters.SSL.CHECK_CERT_OPTIONAL | SutAdapters.SSL.CHECK_CERT_REQUIRED
		@type checkCert: strconstant
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param truncateBody: truncate the body content (default=True)
		@type truncateBody: boolean
		
		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated, socket expected
		@type agent: string/none

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param caCerts: path to the certificate authority (default=None)
		@type caCerts: string/none
		
		@param checkHost: validate the common name field (default=False)
		@type checkHost: boolean
		
		@param hostCn: common name to check (default=None)
		@type hostCn: string/none
		
		@param manStreamSupport: man stream support on content type header (default=True)
		 @type manStreamSupport: boolean
		
		@param octetStreamSupport: octet stream support on content type header (default=True)
		@type octetStreamSupport: boolean

		@param certfile: path to the cert file (default=None)
		@type certfile: string/none

		@param keyfile: path to the key file (default=None)
		@type keyfile: string/none
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
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
		
		if not isinstance(bindPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "bindPort argument is not a integer (%s)" % type(bindPort) )
		if not isinstance(destinationPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "destinationPort argument is not a integer (%s)" % type(destinationPort) )
		if not isinstance(proxyPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "proxyPort argument is not a integer (%s)" % type(proxyPort) )

		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, 
																										realname=name, agentSupport=agentSupport, agent=agent, showEvts=verbose,
																										showSentEvts=verbose, showRecvEvts=verbose)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived

		# init tcp layer

		self.ADP_TCP = AdapterTCP.Client(parent=parent, bindIp = bindIp, bindPort=bindPort, 
																		destinationIp=destinationIp, destinationPort=destinationPort,  destinationHost=destinationHost, 
																		proxyIp=proxyIp, proxyPort=proxyPort, proxyHost=proxyHost, proxyEnabled=proxyEnabled, proxyType=proxyType,
																		socketTimeout=socketTimeout, socketFamily=socketFamily, inactivityTimeout=0, 
																		separatorDisabled=True, name=name, caCerts=caCerts, checkHost=checkHost, hostCn=hostCn,
																		sslSupport=sslSupport, sslVersion=sslVersion, checkCert=checkCert,
																		debug=debug, logEventSent=False, logEventReceived=False, parentName=__NAME__,
																		agentSupport=agentSupport, agent=agent, shared=shared, verbose=verbose,
																		keyfile=keyfile, certfile=certfile)
		# callback tcp
		self.ADP_TCP.handleIncomingData = self.onIncomingData	
		self.ADP_TCP.handleNoMoreData = self.onNoMoreData
		self.ADP_TCP.onHttpProxyInitialization = self.onHttpProxyInitialization
		# inherent functions
#		self.isConnectedSsl = self.ADP_TCP.isConnectedSsl
		self.hasReceivedData = self.ADP_TCP.hasReceivedData
		self.sendData = self.ADP_TCP.sendData

		self.websocketSupport = False
		
		# http options
		self.cfg = {}	
		self.cfg['http_version'] = httpVersion
		self.cfg['http_agent'] = httpAgent
		self.cfg['http_connection'] = httpConnection # close | keep-alive | None
		self.cfg['http_chuncked_data'] =  httpChunckedData # boolean
		self.cfg['http_save_content'] = saveContent
		self.cfg['http_truncate_body'] = truncateBody
		self.cfg['http_strict_mode'] = strictMode
		self.cfg['http_support_authentication'] = supportAuthentication
		self.cfg['http_websocket_mode'] = websocketMode
		self.cfg['http_octet_stream_support'] = octetStreamSupport
		self.cfg['http_man_stream_support'] = manStreamSupport

		# proxy options
		self.cfg['proxy-enabled'] = proxyEnabled
		self.cfg['proxy-type'] = proxyType

		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.__checkConfig()
		
		# digest library
		self.authDigest = LibraryAuth.Digest(parent=parent, debug=debug)
		self.authBasic= LibraryAuth.Basic(parent=parent, debug=debug)
		
		# init the HTTP encoder/decoder 
		self.httpCodec = codec.Codec( parent=self, 
																								octetStreamSupport=self.cfg['http_octet_stream_support'],
																								manStreamSupport=self.cfg['http_man_stream_support'],
																								truncateBody=self.cfg['http_truncate_body'],
																								strictMode=self.cfg['http_strict_mode'],
																								websocketMode=self.cfg['http_websocket_mode'] 
																							)
		self.buf = ''
		self.file_id = 0
		self.waitingProxy = False

	def __checkConfig(self):
		"""
		"""
		self.debug("config: %s" % self.cfg)
		if self.cfg['http_save_content']: self.warning("HTTP AdapterID=%s" % self.getAdapterId() )
		
	def tcp(self):
		"""
		Return tcp layer
		"""
		return self.ADP_TCP
		
	def activeWebsocket(self):
		"""
		Active Websocket
		"""
		self.websocketSupport = True

	def encapsule(self, lower_event, layer_http):
		"""
		"""
		# add layer to tpl
		lower_event.addLayer(layer=layer_http)
		return lower_event
	
	def onReset(self):
		"""
		Reset
		"""
		# flush the buffer
		self.buf = ''
		self.waitingProxy = False
		self.file_id = 0
		# tcp disconnect
		self.disconnect()

	@doc_public
	def connect(self):
		"""
		Start the TCP connection
		"""
		# flush the buffer
		self.buf = ''
		# tcp connect
		self.ADP_TCP.connect()
	
	@doc_public
	def disconnect(self):
		"""
		Close the TCP connection
		"""
		# flush the buffer
		self.buf = ''
		# tcp disconnect
		self.ADP_TCP.disconnect()

	@doc_public
	def constructTemplateRequest(self, rawHttp):
		"""
		Construct a template request from the raw http passed on argument
		
		@param rawHttp: http request
		@type rawHttp: string/list
		
		@return: the http template layer
		@rtype: templatelayer or none on error
		"""
		decodedMessageTpl = None
		try:
			if isinstance( rawHttp, list):
				rawHttp = '\r\n'.join(rawHttp)
			else:
				rawHttp = rawHttp.replace('\t', '')
				rawHttp = rawHttp.splitlines()
				rawHttp = '\r\n'.join(rawHttp)
			(ret, decodedMessageTpl, summary, left) = self.httpCodec.decode(rsp=rawHttp, nomoredata=True, request=True)
		except Exception as e:
			self.error('error while constructing the template request: %s' % str(e))		
		return decodedMessageTpl
			
	@doc_public
	def constructTemplateResponse(self, rawHttp):
		"""
		Construct a template response from the raw http passed on argument
		
		@param rawHttp: http response
		@type rawHttp: string/list
		
		@return: the http template layer
		@rtype: templatelayer
		"""
		try:
			if isinstance( rawHttp, list):
				rawHttp = '\r\n'.join(rawHttp)
			else:
				rawHttp = rawHttp.replace('\t', '')
				rawHttp = rawHttp.splitlines()
				rawHttp = '\r\n'.join(rawHttp)
			(ret, decodedMessageTpl, summary, left) = self.httpCodec.decode(rsp=rawHttp, nomoredata=True, request=False)
		except Exception as e:
			self.error('error while constructing the template response: %s' % str(e))		
		return decodedMessageTpl		
			
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
		
		return self.ADP_TCP.isConnected(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
											sourcePort=sourcePort, destinationPort=destinationPort)
	@doc_public
	def isConnectedSsl(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None, sslVersion=None, sslCipher=None):
		"""
		Wait connected ssl event until the end of the timeout
		
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
		@type destinationPort: string/operators	

		@param sslVersion: ssl version expected
		@type sslVersion: string/operators/none
		
		@param sslCipher: ssl cipher expected
		@type sslCipher: string/operators/none
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_TCP.isConnectedSsl(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
											sourcePort=sourcePort, destinationPort=destinationPort, sslVersion=sslVersion, sslCipher=sslCipher)
											
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
		
		return self.ADP_TCP.isDisconnected(timeout=timeout, byServer=byServer, versionIp=versionIp, 
						sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)

	def onHttpProxyInitialization(self):
			"""
			"""
			self.waitingProxy = True
			
			# prepare the CONNECT request
			dst = self.ADP_TCP.cfg['dst-ip']
			if len(self.ADP_TCP.cfg['dst-host']):
				dst = self.ADP_TCP.cfg['dst-host']
			rawHttp = [ "CONNECT %s:%s %s" % (dst, self.ADP_TCP.cfg['dst-port'], self.cfg['http_version']) ]
			rawHttp.append( "User-Agent: %s" % self.cfg['http_agent'] )
			rawHttp.append( "Proxy-Connection: Keep-Alive" )
			rawHttp.append( "Content-Length: 0" )
			rawHttp.append( "Host: %s" % dst )
			rawHttp.append( "Pragma: no-cache" )
			rawHttp.append("")
			self.trace("Proxy request")
			self.debug( "%s" % "\r\n".join(rawHttp) )
			
			# send it
			req_tpl = self.constructTemplateRequest(rawHttp=rawHttp)
			lower = self.sendRequest(tpl=req_tpl)
			
			# log event
			self.logSentEvent( shortEvt = "proxy connection", tplEvt = lower )
			
	def onHttpProxyResponse(self, summary, lower):
		"""
		On http proxy established
		"""
		self.debug( "proxy response" )
		self.waitingProxy = False
		rsp_code = lower.get('HTTP', 'response')
		if rsp_code.get('code') == '200':
			self.debug( "proxy established" )
			
			self.logRecvEvent( shortEvt = "proxy established", tplEvt = lower )
			self.ADP_TCP.proxyInitialized()
			
			if self.ADP_TCP.cfg['ssl-support']:
				self.debug( "proxy starting ssl because enabled" )
				self.ADP_TCP.startSsl()
		elif rsp_code.get('code') == '407':  # proxy-authorization
			self.warning('proxy authentication not yet supported')
		else:	
			self.logRecvEvent( shortEvt = "proxy error", tplEvt = lower )
			
	@doc_public
	def isAcceptedProxy(self, codeExpected="200", phraseExpected="Connection established", versionExpected=None, timeout=1.0 ):
		"""
		Wait response from proxy until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
	
		# prepare expected response template 
		tpl_rsp = TestTemplatesLib.TemplateMessage()
	
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.ADP_TCP.cfg['ssl-support']:
			tpl_rsp.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )		
		if rsp is not None:
			self.ADP_TCP.proxyInitialized()
		return rsp
		
	def onIncomingData(self, data, lower):
		"""
		"""
		if self.websocketSupport:
			self.onWebsocketIncomingData(data, lower)
		else:
			try:
				self.buf += data
				self.debug('data received (bytes %d), decoding attempt...' % len(self.buf))
				self.debug( data )
				(ret, decodedMessageTpl, summary, left) = self.httpCodec.decode(rsp=self.buf)
				if ret == codec.DECODING_OK_CONTINUE:
					self.debug('decoding ok but several message received on the same message..')
					lowerCopy = copy.deepcopy( lower )
					# log event
					lower.addLayer(layer=decodedMessageTpl)
					self.buf = decodedMessageTpl.getRaw()
					self.onIncomingResponse(summary=summary, lower=lower)
					self.debug('decoding ok continue...')
					
					# update buffer
					if left:
						self.onIncomingData( data=left, lower=lowerCopy)
					del lowerCopy
				elif ret == codec.DECODING_NEED_MORE_DATA:
					self.debug('need more data, waiting for additional...')
					self.debug( data )
				elif ret == codec.DECODING_OK:
					self.debug('decoding ok...')
					# log event
					decodedMessageTpl.addRaw(self.buf)
					lower.addLayer(layer=decodedMessageTpl)
					self.onIncomingResponse(summary=summary, lower=lower)
				else:  # should not be happen
					self.debug( 'unknown decoding error: %s' % str(ret) )
					self.warning(self.buf)
					raise Exception('bad response received')
			except Exception as e:
				self.error('Error on http incoming data: %s' % str(e))		
		
	def onNoMoreData(self, lower):
		"""
		"""
		if self.websocketSupport:
			self.onWebsocketIncomingData(data='', lower=lower)
		else:		
			try:
				(ret, decodedMessageTpl, summary, left) = self.httpCodec.decode(rsp=self.buf, nomoredata = True)
				if ret == codec.DECODING_OK_CONTINUE:
					lowerCopy = copy.deepcopy( lower )
					# log event
					lower.addLayer(layer=decodedMessageTpl)
					self.buf = decodedMessageTpl.getRaw()
					self.onIncomingResponse(summary=summary, lower=lower)
					self.debug('decoding ok continue...')
					
					# update buffer
					if left:
						self.onIncomingData( data=left, lower=lowerCopy)
					
					del lowerCopy
				elif ret == codec.DECODING_NOTHING_TODO:
					pass
				elif ret == codec.DECODING_OK:
					self.debug('decoding ok...')
					# log event
					lower.addLayer(layer=decodedMessageTpl)
					self.onIncomingResponse(summary=summary, lower=lower)
				else:  # should not be happen
					self.warning( self.buf)
					self.debug( 'unknown decoding error: %s' % str(ret) )
					raise Exception('bad data received' )
			except Exception as e:
				self.error('Error on http incoming more data: %s' % str(e))	

	def onWebsocketIncomingData(self, data, lower):
		"""
		Function to overwrite, called on incoming websocket data.

		@param data: http response
		@type data: string

		@param lower: template http response received
		@type lower: templatemessage/none
		"""
		pass
		
	def onIncomingResponse(self, summary, lower):
		"""
		Called when the reponse is decoded successfully
		"""
		responseRaw = self.buf
		if self.logEventReceived:
			lower.addRaw(raw=responseRaw) # add the raw request to the template
			self.logRecvEvent( shortEvt = summary, tplEvt = lower ) # log event 		
		# reset the buffer
		self.buf = ''	
		
		if self.waitingProxy:
			self.onHttpProxyResponse(summary=summary, lower=lower)
		else:	
			self.handleIncomingResponse(data=responseRaw,lower=lower)
		
			# save data ?
			if self.cfg['http_save_content']:
				http_layer = lower.get('HTTP')
				http_headers = http_layer.get('headers')
				http_body = http_layer.get('body')
				contenttype_hdr = http_headers.get('content-type')
				contentdisp_hdr = http_headers.get('content-disposition')
				if contenttype_hdr is not None:
					self.__saveData(type=contenttype_hdr, filename=contentdisp_hdr, data=http_body )
		
	def __saveData(self, type, data, filename=None):
		"""
		"""
		self.debug( 'save data called' )
		self.file_id += 1
		# default name and extension file
		file_name = 'file%s' % self.file_id
		# Content-Type: text/html;charset=UTF-8
		extfile = type.split(';')[0].split('/')[1]
		fullname = '%s.%s' % (file_name, extfile)
		self.debug( 'save with the filename and path: %s' % fullname )
		
		# filename gived ?
		if filename is not None:
			file_name = filename.split('filename=')[1]
			if file_name.startswith('"') and file_name.endsswith('"'):
				file_name = file_name[1:-1]
			fullname = file_name
			
		# save data in the storage
		if data is not None:
			if len(data) > 0:
				self.debug( 'save data in storage called' )
				self.saveDataInStorage( destname=fullname, data=data )
		
	def handleIncomingResponse(self, data, lower=None):
		"""
		Function to overwrite, called on incoming http response.

		@param data: http response
		@type data: string

		@param lower: template http response received
		@type lower: templatemessage/none
		"""
		pass
		
	@doc_public
	def sendRequest(self, tpl):
		"""
		Send a request

		@param tpl: http request
		@type tpl: templatelayer

		@return: lower template
		@rtype:	template	
		"""
		try:
			# check if connected 
			if not self.ADP_TCP.connected:
				raise Exception( 'not connected' )

			# check if tpl is not none
			if tpl is  None:
				raise Exception( 'tpl empty' )

			# encode template
			try:
				(encodedMessage, summary) = self.httpCodec.encode(http=tpl)
			except Exception as e:
				raise Exception("codec error: %s" % str(e))	

			# Send request
			try:
				lower = self.ADP_TCP.sendData( data=encodedMessage )
			except Exception as e:
				raise Exception("tcp failed: %s" % str(e))	

			tpl.addRaw( encodedMessage )
			lower.addLayer( tpl )

			# Log event
			if self.logEventSent:
				lower.addRaw(raw=encodedMessage)
				self.logSentEvent( shortEvt = summary, tplEvt = lower ) 

		except Exception as e:
			raise Exception('unable to send request: %s' % str(e))
		return lower

	@doc_public
	def hasReceivedResponse(self, expected, timeout=1.0):
		"""
		Wait to receive "response" until the end of the timeout.
		
		@param expected: response template
		@type expected: templatemessage/templatelayer

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response or none otherwise
		@rtype:	templatemessage/templatelayer/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if expected is None:
			raise Exception( 'has received response: expected template cannot be empty' )
		tpl_expected = expected
		if isinstance( expected, TestTemplatesLib.TemplateLayer ):
			tpl_expected = TestTemplatesLib.TemplateMessage()
		
			if self.cfg['agent-support']:
				layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
				layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
				layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
				tpl_expected.addLayer( layer_agent )
				
			tpl_expected.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
			tpl_expected.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )
			if self.ADP_TCP.cfg['proxy-enabled']:
				tpl_expected.addLayer( AdapterSOCKS.socks(more=AdapterSOCKS.received()) )
			if self.ADP_TCP.cfg['ssl-support']:
				tpl_expected.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
			tpl_expected.addLayer( expected )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		if evt is None:
			return None
		return evt

	def addContentLength(self, hdrs, lenBod, overwrite_cl=False):
		"""
		"""
		self.debug( 'add content length automatically' )
		contentLengthPresent = False
		for h in hdrs.items():
			k,v = h
			if k.lower() == "content-length":
				self.warning( 'content-length already present with the value: %s, different of %s' % (v,lenBod) )
				contentLengthPresent = True
		if not contentLengthPresent:
			if lenBod > 0:
				hdrs[ u'Content-Length'] = '%s' % unicode(lenBod)
		if overwrite_cl:
			self.debug( 'write the good value for the content-length' )
			if lenBod > 0:
				hdrs[ u'Content-Length'] = '%s' % unicode(lenBod)

	def addTransferEncoding(self, hdrs, lenBod):
		"""
		"""
		transferEncodingPresent = False
		for h in hdrs.items():
			k,v = h
			if k.lower() == "transfer-encoding":
				if v.lowert() == "chunked":
					transferEncodingPresent = True
		if not transferEncodingPresent:
			if lenBod > 0:
				hdrs[ u'Transfer-Encoding'] = u'chunked'

	def chunkData(self, bod):
		"""
		Chunks a body in one piece.
		"""
		return "%s\r\n%s\r\n0\r\n" % (len(bod), bod)
	
	@doc_public
	def makeAuthentication(self, uri, login, password, method, headers={}, timeout=1.0, body=None):
		"""
		Make authentication function (basic, digest)
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# prepare expected response template 
		tpl_rsp401 = self.getTemplateResponse()
		tpl_rsp401.addLayer( templates.response( code='401', phrase=None, headers={ 'www-authenticate': TestOperatorsLib.Any()}) )
		
		rsp = self.hasReceivedResponse(expected=tpl_rsp401, timeout=timeout )
		if rsp is not None:
			# disconnect previous 	
			if self.cfg['http_connection'] == CONN_CLOSE:
				isDisconnected = self.isDisconnected(timeout=timeout,byServer=True)
				if isDisconnected is None:
					self.error( 'unable to disconnect' )
					return

			# extract authentication
			self.debug('authentication to do, extract www-authen header')
			http_hdrs = rsp.get('HTTP', 'headers')
			www_hdr = http_hdrs.get('www-authenticate')

			# respond to the challenge
			challenge = self.authDigest.decode(challenge=www_hdr)
			self.debug( challenge )
			
			# make digest ?
			schemeComputed = False
			if challenge['auth-scheme'].lower() == 'digest':
				rsp, cnonce, nc = self.authDigest.compute( username=login, password=password, realm=challenge['realm'],
																								nonce=challenge['nonce'], 	method=method, uri=uri , qop=challenge['qop'],
																								algo=challenge['algorithm'], body=None )
				challengeRsp = self.authDigest.encode( username=login, realm=challenge['realm'], nonce=challenge['nonce'],
																						uri=uri, response=rsp, cnonce=cnonce, nc=nc,
																						qop=challenge['qop'], algo=challenge['algorithm'])
				schemeComputed = True

			elif challenge['auth-scheme'].lower() == 'basic':
				rsp = self.authBasic.compute( username=login, password=password )
				challengeRsp = self.authBasic.encode(response=rsp)
				schemeComputed = True
				
			# authentication not supported
			else:
				self.error('authentication scheme not yet supported: %s' % challenge['auth-schem'] )

			if schemeComputed:
				headers.update( {'authorization': challengeRsp} )	
				tpl = templates.request(method=method, uri=uri, version=self.cfg['http_version'], headers=headers, body=body)
				if self.cfg['http_connection'] == CONN_CLOSE:
					# tcp connect
					if not self.connection(timeout=timeout):
						return
				self.sendRequest(tpl=tpl)
			
	def getTemplateResponse(self):
		"""
		Internal function
		"""
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['proxy-enabled']:
			tpl_rsp.addLayer( AdapterSOCKS.socks(more=AdapterSOCKS.received()) )
		if self.ADP_TCP.cfg['ssl-support']:
			tpl_rsp.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		return tpl_rsp
		
	def getDefaultHeaders(self):
		"""
		Internal function
		"""
		__hdrs = { u'User-Agent': u'%s' % self.cfg['http_agent'] }
		if self.cfg['http_connection'] == CONN_CLOSE:
			__hdrs[u'Connection'] = u'Close'
		if self.cfg[u'http_connection'] == CONN_KEEPALIVE:
			__hdrs[u'Connection'] = u'Keep-Alive'
		return __hdrs
	@doc_public
	def sendHttp(self, uri, host, method="GET", headers={}, body=None, timeout=1.0):
		"""
		Send a GET request and wait response until the end of the timeout.
		
		@param uri: URI
		@type uri: string
		
		@param host: host to contact
		@type host: string
		
		@param method: http method (default=GET)
		@type method: string

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the request
		@type body: string/none
		"""
		__hdrs = { u'Host': u'%s' % host }
		
		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		 
		
		if body is not None :
			lenBod = len(body)
			if lenBod > 0:				
				self.addContentLength(__hdrs, lenBod)
				
		# prepare request template and send it
		tpl = templates.request(method=method, uri=uri, version=self.cfg['http_version'], headers=__hdrs, body=body)

		# start tcp connection
		if not self.connection(timeout=timeout):
			return
		
		self.sendRequest(tpl=tpl)
	@doc_public
	def hasReceivedHttpResponse(self, httpCode="200", httpPhrase="OK", httpVersion='HTTP/1.1', timeout=1.0, httpHeaders={}, httpBody=None):
		"""
		Wait to receive "http response" until the end of the timeout.

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
		@rtype:	   template	  
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ):
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )

		tpl = TestTemplatesLib.TemplateMessage()
		   
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )

		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )		 
		if self.tcp().cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		headers = { }
		headers.update(httpHeaders)
		tpl.addLayer( templates.response( version=httpVersion, code=httpCode, phrase=httpPhrase, headers=headers, body=httpBody) )
		
		return self.hasReceivedResponse(expected=tpl, timeout=timeout)

	@doc_public
	def connection(self, timeout=1.0):
		"""
		Tcp connection and wait connected event until the end of the timeout 
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: connection result
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		if not self.ADP_TCP.connected:
			# connect tcp
			self.connect()
			if self.isConnected(timeout=timeout) is None:
				return False

			# connect proxy if active
			if self.cfg['proxy-enabled']:
				if self.cfg['proxy-type'] == AdapterTCP.PROXY_HTTP:
					if self.isAcceptedProxy(timeout=timeout) is None:
						ret = False
				else:
					if self.ADP_TCP.isAcceptedProxy(timeout=timeout) is None:
						ret = False
		return ret

	@doc_public
	def disconnection(self, timeout=1.0):
		"""
		Tcp disconnection and wait disconnected event until the end of the timeout 
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: disconnection result
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = True
		if self.ADP_TCP.connected:
			self.disconnect()
			isDisconnected = self.isDisconnected(timeout=timeout)
			if isDisconnected is None:
				ret = False
		return ret
				
	@doc_public
	def OPTIONS(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None):
		"""
		Send a OPTIONS request and wait response until the end of the timeout.

		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }

		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="OPTIONS", uri=uri, version=self.cfg['http_version'], headers=__hdrs)
		
		# tcp connect
		if not self.connection(timeout=timeout):
			return 

		self.sendRequest(tpl=tpl)

		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="OPTIONS", headers=__hdrs, timeout=timeout)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=None) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp
		
		
	@doc_public
	def DELETE(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None):
		"""
		Send a DELETE request and wait response until the end of the timeout.

		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }

		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="DELETE", uri=uri, version=self.cfg['http_version'], headers=__hdrs)
		
		# start connection
		if not self.connection(timeout=timeout):
			return

		self.sendRequest(tpl=tpl)

		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="DELETE", headers=__hdrs, timeout=timeout)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=None) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp
		
	@doc_public
	def HEAD(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None):
		"""
		Send a HEAD request and wait response until the end of the timeout.
		No body in response is expected with this type of request
	
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }

		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="HEAD", uri=uri, version=self.cfg['http_version'], headers=__hdrs)
		
		# start tcp connection
		if not self.connection(timeout=timeout):
			return
		
		self.sendRequest(tpl=tpl)

		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="HEAD", headers=__hdrs, timeout=timeout)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=None) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp

	@doc_public
	def GET(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None):
		"""
		Send a GET request and wait response until the end of the timeout.
	
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: body expected
		@type bodyExpected: string/operators/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }

		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="GET", uri=uri, version=self.cfg['http_version'], headers=__hdrs)
		
		# start tcp connection
		if not self.connection(timeout=timeout):
			return

		self.sendRequest(tpl=tpl)

		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="GET", headers=__hdrs, timeout=timeout)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=bodyExpected) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp

	@doc_public
	def PUT(self, uri, host, timeout=1.0, headers={}, body=None, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None,
									overwriteCl=False):
		"""
		Send a PUT request and wait response until the end of the timeout.
		The content-length is automatically computed if not provided and body not present (unless a transfer-encoding was set explicitly to chunked).
		
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the GET request
		@type body: string/none

		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: http headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: http body expected
		@type bodyExpected: string/operators/none
		
		@param overwriteCl: overwrite content-length header with the good value
		@type overwriteCl: boolean
		
		@return: http response or none if no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }

		if body is not None :
			lenBod = len(body)
			if lenBod > 0:
				if self.cfg['http_chuncked_data']:
					self.addTransferEncoding(headers, lenBod)
					bod = self.chunkData(bod=body)
				else:
					self.addContentLength(headers, lenBod, overwriteCl)
		
		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="PUT", uri=uri, version=self.cfg['http_version'], headers=__hdrs, body=body )

		# start tcp connection
		if not self.connection(timeout=timeout):
			return	
					
		self.sendRequest(tpl=tpl)
		
		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="PUT", headers=__hdrs, timeout=timeout)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=bodyExpected) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp

	@doc_public
	def POST(self, uri, host, timeout=1.0, headers={}, body=None, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None,
									overwriteCl=False):
		"""
		Send a POST request and wait response until the end of the timeout.
		The content-length is automatically computed if not provided and body not present (unless a transfer-encoding was set explicitly to chunked).
		
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the GET request
		@type body: string/none

		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: http headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: http body expected
		@type bodyExpected: string/operators/none
		
		@param overwriteCl: overwrite content-length header with the good value
		@type overwriteCl: boolean
		
		@return: http response or none if no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }
		
		if body is not None :
			lenBod = len(body)
			if lenBod > 0:
				if self.cfg['http_chuncked_data']:
					self.addTransferEncoding(headers, lenBod)
					bod = self.chunkData(bod=body)
				else:
					self.addContentLength(headers, lenBod, overwriteCl)

		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="POST", uri=uri, version=self.cfg['http_version'], headers=__hdrs, body=body )

		# start tcp connection
		if not self.connection(timeout=timeout):
			return

		self.sendRequest(tpl=tpl)

		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="POST", headers=__hdrs, timeout=timeout, body=body)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=bodyExpected) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp

	@doc_public
	def TRACE(self, uri, host, timeout=1.0, headers={}, body=None, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None,
									overwriteCl=False):
		"""
		Send a TRACE request and wait response until the end of the timeout.
		The content-length is automatically computed if not provided and body not present (unless a transfer-encoding was set explicitly to chunked).
		
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the GET request
		@type body: string/none

		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: http headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: http body expected
		@type bodyExpected: string/operators/none
		
		@param overwriteCl: overwrite content-length header with the good value
		@type overwriteCl: boolean
		
		@return: http response or none if no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		__hdrs = { u'Host': u'%s' % host }

		if body is not None :
			lenBod = len(body)
			if lenBod > 0:
				if self.cfg['http_chuncked_data']:
					self.addTransferEncoding(headers, lenBod)
					bod = self.chunkData(bod=body)
				else:
					self.addContentLength(headers, lenBod, overwriteCl)
		
		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		

		# prepare request template and send it
		tpl = templates.request(method="TRACE", uri=uri, version=self.cfg['http_version'], headers=__hdrs, body=body )

		# start tcp connection
		if not self.connection(timeout=timeout):
			return
			
		self.sendRequest(tpl=tpl)
		
		# digest authentication support
		if self.cfg['http_support_authentication']:
			self.makeAuthentication(uri=uri, login=login, password=password, method="TRACE", headers=__hdrs, timeout=timeout)

		# prepare expected response template 
		tpl_rsp = self.getTemplateResponse()
		tpl_rsp.addLayer( templates.response( version=versionExpected, code=codeExpected, phrase=phraseExpected, headers=headersExpected, body=bodyExpected) )
		# and wait for response
		rsp = self.hasReceivedResponse(expected=tpl_rsp, timeout=timeout )
		
		# close the connection ?
		if self.cfg['http_connection'] == CONN_CLOSE:
			self.disconnect()
		return rsp

	@doc_public
	def doGET(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None):
		"""
		Send a GET request and wait response until the end of the timeout.
	
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: body expected
		@type bodyExpected: string/operators/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.GET(uri=uri, host=host, timeout=timeout, headers=headers, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected, bodyExpected=bodyExpected)
	@doc_public
	def doPOST(self, uri, host, timeout=1.0, headers={}, body=None, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None,
									overwriteCl=False):
		"""
		Send a POST request and wait response until the end of the timeout.
		The content-length is automatically computed if not provided and body not present (unless a transfer-encoding was set explicitly to chunked).
		
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the GET request
		@type body: string/none

		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: http headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: http body expected
		@type bodyExpected: string/operators/none
		
		@param overwriteCl: overwrite content-length header with the good value
		@type overwriteCl: boolean
		
		@return: http response or none if no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.POST(uri=uri, host=host, timeout=timeout, headers=headers, body=body, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected, bodyExpected=bodyExpected,
									overwriteCl=overwriteCl)
	@doc_public
	def doPUT(self, uri, host, timeout=1.0, headers={}, body=None, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None,
									overwriteCl=False):
		"""
		Send a PUT request and wait response until the end of the timeout.
		The content-length is automatically computed if not provided and body not present (unless a transfer-encoding was set explicitly to chunked).
		
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the GET request
		@type body: string/none

		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: http headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: http body expected
		@type bodyExpected: string/operators/none
		
		@param overwriteCl: overwrite content-length header with the good value
		@type overwriteCl: boolean
		
		@return: http response or none if no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.PUT(uri=uri, host=host, timeout=timeout, headers=headers, body=body, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected, 
									overwriteCl=overwriteCl)
	@doc_public
	def doTRACE(self, uri, host, timeout=1.0, headers={}, body=None, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None, bodyExpected=None,
									overwriteCl=False):
		"""
		Send a TRACE request and wait response until the end of the timeout.
		The content-length is automatically computed if not provided and body not present (unless a transfer-encoding was set explicitly to chunked).
		
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the GET request
		@type body: string/none

		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: http headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none

		@param bodyExpected: http body expected
		@type bodyExpected: string/operators/none
		
		@param overwriteCl: overwrite content-length header with the good value
		@type overwriteCl: boolean
		
		@return: http response or none if no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.TRACE(uri=uri, host=host, timeout=timeout, headers=headers, body=body, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected, bodyExpected=bodyExpected,
									overwriteCl=overwriteCl)		
	@doc_public
	def doHEAD(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None):
		"""
		Send a HEAD request and wait response until the end of the timeout.
		No body in response is expected with this type of request
	
		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.HEAD(uri=uri, host=host, timeout=timeout, headers=headers, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected)		
	@doc_public
	def doDELETE(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None):
		"""
		Send a DELETE request and wait response until the end of the timeout.

		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.DELETE(uri=uri, host=host, timeout=timeout, headers=headers, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected)
			
	@doc_public
	def doOPTIONS(self, uri, host, timeout=1.0, headers={}, login='', password='', versionExpected=None, codeExpected=None, phraseExpected=None, headersExpected=None):
		"""
		Send a OPTIONS request and wait response until the end of the timeout.

		@param uri: URI
		@type uri: string

		@param host: host to contact
		@type host: string

		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict
		
		@param login: login used on digest authentication (default='')
		@type login: string
		
		@param password: password used on digest authentication (default='')
		@type password: string
		
		@param versionExpected: http version expected
		@type versionExpected: string/operators/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operators/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none

		@param headersExpected: headers expected {key:value, ...}
		@type headersExpected: dictadvanced/none
		
		@return: http response or none is no match
		@rtype: templatemessage/none	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.OPTIONS( uri=uri, host=host, timeout=timeout, headers=headers, login=login, password=password, versionExpected=versionExpected, codeExpected=codeExpected, phraseExpected=phraseExpected, headersExpected=headersExpected)