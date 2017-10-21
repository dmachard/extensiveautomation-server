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

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapterLib.getVersion()]
AdapterHTTP = sys.modules['SutAdapters.%s.HTTP' % TestAdapterLib.getVersion()]

import codec
try:
    import hashlib
    sha1_constructor = hashlib.sha1
except ImportError, e: # support python 2.4
    import sha
    sha1_constructor = sha.new
import base64

import templates

__NAME__="""WEBSOCKET"""

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, bindIp='', bindPort=0, destinationIp='127.0.0.1', 
								proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False,
									destinationPort=80, destinationHost='', name=None, debug=False,
									sslSupport=False, sslVersion=AdapterSSL.SSLv23, agentSupport=False, agent=None, shared=False,
									logEventSent=True, logEventReceived=True):
		"""
		Adapter for the websocket protocol according to the rfc 6455
		Ssl and proxy support

		@param parent: parent testcase
		@type parent: testcase

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
		
		@param proxyIp: proxy ip
		@type proxyIp: string

		@param proxyPort: proxy port
		@type proxyPort: integer

		@param proxyHost: proxy host (automatic dns resolution)
		@type proxyHost: string
		
		@param proxyEnabled: True to support proxy (default=False)
		@type proxyEnabled: boolean	
		
		@param sslSupport: activate SSL channel (default=False)
		@type sslSupport: boolean
		
		@param sslVersion: SutAdapters.SSL.SSLv2 | SutAdapters.SSL.SSLv23 (default) | SutAdapters.SSL.SSLv3 | SutAdapters.SSL.TLSv1 | SutAdapters.SSL.TLSv11  | SutAdapters.SSL.TLSv12 
		@type sslVersion: strconstant
		
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.wsKey = None
		self.wsHanshakeSuccess = False
		self.wsMaxPayloadSize = codec.WEBSOCKET_MAX_BASIC_DATA1024
		self.buf = ''
		
		self.cfg = {}
		self.cfg['dest-ip'] = destinationIp
		self.cfg['dest-port'] = destinationPort
		self.cfg['ssl-support'] = sslSupport
		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		
		self.__checkConfig()
		
		self.ADP_HTTP = AdapterHTTP.Client(parent=parent, bindIp=bindIp, bindPort=bindPort, name=name, destinationIp=destinationIp, 
																					destinationPort=destinationPort, destinationHost=destinationHost, 
																					proxyIp=proxyIp, proxyPort=proxyPort,  proxyHost=proxyHost, proxyEnabled=proxyEnabled, 
																					socketTimeout=300.0, socketFamily=4, websocketMode=True,
																					saveContent=False, httpVersion='HTTP/1.1', httpAgent='ExtensiveTesting', 
																					httpConnection='close', httpChunckedData=False, sslSupport=sslSupport, 
																					sslVersion=sslVersion, checkCert='No', debug=debug, logEventSent=False, 
																					logEventReceived=False, truncateBody=False,
																					agentSupport=agentSupport, agent=agent, shared=shared, strictMode=False)
		self.ADP_HTTP.handleIncomingResponse = self.handleIncomingHttpResponse
		self.ADP_HTTP.onWebsocketIncomingData = self.onWebsocketIncomingData
		
		self.wsCodec =  codec.Codec( parent=self )
		
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	

	@doc_public
	def connect(self):
		"""
		Connect tcp
		"""
		self.buf = ''
		self.ADP_HTTP.connect()
	@doc_public
	def disconnect(self):
		"""
		Disconnect tcp
		"""
		self.buf = ''
		self.ADP_HTTP.disconnect()
	
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		self.disconnect()
	
	@doc_public
	def isAcceptedProxy(self, timeout=1.0, codeExpected="200", phraseExpected="Connection established", versionExpected=None):
		"""
		Wait response from proxy until the end of the timeout.
			
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float

		@param versionExpected: http version expected
		@type versionExpected: string/operator/none

		@param codeExpected: http status code expected
		@type codeExpected: string/operator/none

		@param phraseExpected: http phrase code expected
		@type phraseExpected: string/operators/none
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isAcceptedProxy(timeout=timeout, codeExpected=codeExpected, phraseExpected=phraseExpected, 
																														versionExpected=versionExpected)
		
	@doc_public
	def handshake(self, resource, origin):
		"""
		Do hanshake
		"""
		self.wsHanshakeSuccess = False
		self.wsKey = self.wsCodec.createSecWsKey()
		
		req = [ "GET %s HTTP/1.1" % resource ]
		req.append("Upgrade: websocket")
		req.append("Connection: keep-alive, upgrade")
		req.append("Host: %s" % self.cfg['dest-ip'])
		req.append("Origin: http://%s" % origin )
		req.append("Sec-WebSocket-Key: %s" % self.wsKey )
		req.append("Sec-WebSocket-Version: %s" % codec.WEBSOCKET_VERSION)
		req.append("")

		
		req_tpl = self.ADP_HTTP.constructTemplateRequest(rawHttp=req)
		lower_tpl = self.ADP_HTTP.sendRequest(tpl=req_tpl)
		if self.logEventSent:
			tpl =templates.ws(more=templates.handshake())
			lower_tpl.addLayer( tpl )
			self.logSentEvent( shortEvt = 'Handshake', tplEvt = lower_tpl ) 
	
	def handleIncomingHttpResponse(self, data, lower):
		"""
		On http response
		"""
		http_rsp = lower.get('HTTP', 'response')
		http_hdrs = lower.get('HTTP', 'headers')
		http_code = http_rsp.get('code')
		
		if str(http_code) != '101':
			if self.logEventReceived:
				tpl = templates.ws(more=templates.handshake_error(details="bad http response: %s" % http_code))
				lower.addLayer( tpl )
				self.logRecvEvent( shortEvt = 'Handshake Error', tplEvt = lower ) 
			else:
				self.error( 'hanshake failed bad http response: %s' % http_code )
		else:
			# decode specific ws headers
			hdrUpgrade = False
			hdrConnection = False
			wsAccept = False
			try:
				for k, v in http_hdrs.getItems():
					if k.lower().strip() == 'upgrade' and v.lower().strip() == 'websocket':
						hdrUpgrade = True
					if k.lower().strip() == 'connection' and v.lower().strip() == 'upgrade':
						hdrConnection = True    
					if k.lower().strip() == 'sec-websocket-accept':
						v = v.lower().strip()
						# rfc6455 1.3. Opening Handshake
						value = (self.wsKey + codec.GUID).encode('utf-8')
						sha1 = sha1_constructor()
						sha1.update(value)
						hashed = base64.encodestring(sha1.digest()).strip().lower()
						if hashed == v:
							wsAccept = True
						else:
							if self.logEventReceived:
								tpl = templates.ws(more=templates.handshake_error(details="key incorrect computed=%s received=%s key=%s" % (hashed,v, self.wsKey)))
								lower.addLayer( tpl )
								self.logRecvEvent( shortEvt = 'Handshake Error', tplEvt = lower ) 
							else:
								self.error('web socket key incorrect computed=%s received=%s key=%s' % (hashed,v, self.wsKey)  )
			except Exception as e:
				self.error( 'unable to check websocket headers: %s' % e )  
			else:
				if hdrUpgrade and hdrConnection and wsAccept:
					self.wsHanshakeSuccess = True
					if self.logEventReceived:
						tpl = templates.ws(more=templates.handshake_ok())
						lower.addLayer( tpl )
						self.logRecvEvent( shortEvt = 'Handshake OK', tplEvt = lower ) 
					else:
						self.info( 'handshake ok' )
					self.ADP_HTTP.activeWebsocket()
				else:
					if self.logEventReceived:
						tpl = templates.ws(more=templates.handshake_error())
						lower.addLayer( tpl )
						self.logRecvEvent( shortEvt = 'Handshake Error', tplEvt = lower ) 
					else:
						self.error( 'hanshake failed' )
				
	def onWebsocketIncomingData(self, data, lower):
		"""
		On incoming data
		"""
		self.buf += data
		(data, left, needmore, ws_tpl) = self.wsCodec.decodeWsData(buffer=self.buf)
		self.buf = left
		if not needmore:
			if ws_tpl is not None:
				if self.logEventReceived:
					lower.addLayer( ws_tpl )
					summary = codec.WEBSOCKET_OPCODE_UNKNOWN_STR
					ws_opcode = ws_tpl.getInt('opcode')
					if ws_opcode == codec.WEBSOCKET_OPCODE_TEXT:
						summary = codec.WEBSOCKET_OPCODE_TEXT_STR
					if ws_opcode == codec.WEBSOCKET_OPCODE_BINARY:
						summary = codec.WEBSOCKET_OPCODE_BINARY_STR
					if ws_opcode == codec.WEBSOCKET_OPCODE_PING:
						summary = codec.WEBSOCKET_OPCODE_PING_STR
					if ws_opcode == codec.WEBSOCKET_OPCODE_PONG:
						summary = codec.WEBSOCKET_OPCODE_PONG_STR					
					if ws_opcode == codec.WEBSOCKET_OPCODE_CLOSE:
						summary = codec.WEBSOCKET_OPCODE_CLOSE_STR			
					self.logRecvEvent( shortEvt = summary, tplEvt = lower ) 
				else:
					self.info( 'data received' )		
			# more data in buffer ?
			if len(self.buf) >= 2:
				self.onWebsocketIncomingData(data='', lower=lower)

	@doc_public
	def sendRaw(self, opcode=0, fin=1, mask=0, rsv1=0, rsv2=0, rsv3=0, data=''):
		"""
		Send raw data
		"""
		if not self.wsHanshakeSuccess:
			return
			
		ws_tpl = templates.ws(fin=fin, mask=mask, rsv1=rsv1, rsv2=rsv2, rsv3=rsv3, opcode=opcode, 
													data=data, data_length=len(data), more=templates.sent() )
		wsdata = self.wsCodec.encodeWsData(tpl=ws_tpl)
		
		# Send websocket data
		try:
			lower = self.ADP_HTTP.tcp().sendData( data=wsdata )
		except Exception as e:
			#raise Exception("send request: tcp failed: %s" % str(e))	
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "send request: tcp failed: %s" % str(e) )
		
		lower.addLayer( ws_tpl )
		
		# Log event
		if self.logEventSent:
			lower.addRaw(raw=wsdata)
			self.logSentEvent( shortEvt = codec.WEBSOCKET_OPCODE_TEXT_STR, tplEvt = lower ) 
	@doc_public
	def sendText(self, text):
		"""
		Send text
		
		@param text: text to send
		@type tet: string
		"""
		if not self.wsHanshakeSuccess:
			return
			
		# make chunk
		chunks=[text[x:x+self.wsMaxPayloadSize] for x in xrange(0, len(text), self.wsMaxPayloadSize)]
		
		# encode data in the websocket packet and enqueue it
		for chunk in chunks:
			ws_tpl = templates.ws(fin=1, mask=0, rsv1=0, rsv2=0, rsv3=0, opcode=codec.WEBSOCKET_OPCODE_TEXT, 
														data=chunk, data_length=len(chunk), more=templates.sent() )
			wsdata = self.wsCodec.encodeWsData(tpl=ws_tpl)
			
			# Send websocket data
			try:
				lower = self.ADP_HTTP.tcp().sendData( data=wsdata )
			except Exception as e:
				#raise Exception("send request: tcp failed: %s" % str(e))	
				raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "send request: tcp failed: %s" % str(e) )
			
			lower.addLayer( ws_tpl )
			
			# Log event
			if self.logEventSent:
				lower.addRaw(raw=wsdata)
				self.logSentEvent( shortEvt = codec.WEBSOCKET_OPCODE_TEXT_STR, tplEvt = lower ) 

	@doc_public
	def sendBinary(self, data):
		"""
		Send binary data
		
		@param data: data to send
		@type data: string
		"""
		if not self.wsHanshakeSuccess:
			return
			
		# make chunk
		chunks=[data[x:x+self.wsMaxPayloadSize] for x in xrange(0, len(data), self.wsMaxPayloadSize)]
		
		# encode data in the websocket packet and enqueue it
		for chunk in chunks:
			ws_tpl = templates.ws(fin=1, mask=0, rsv1=0, rsv2=0, rsv3=0, opcode=codec.WEBSOCKET_OPCODE_BINARY, 
														data=chunk, data_length=len(chunk), more=templates.sent() )
			wsdata = self.wsCodec.encodeWsData(tpl=ws_tpl)
			
			# Send websocket data
			try:
				lower = self.ADP_HTTP.tcp().sendData( data=wsdata )
			except Exception as e:
				#raise Exception("send request: tcp failed: %s" % str(e))	
				raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "send request: tcp failed: %s" % str(e) )
			
			lower.addLayer( ws_tpl )
			
			# Log event
			if self.logEventSent:
				lower.addRaw(raw=wsdata)
				self.logSentEvent( shortEvt = codec.WEBSOCKET_OPCODE_BINARY_STR, tplEvt = lower ) 
	@doc_public
	def sendPing(self, data=None):
		"""
		Send ping
		
		@param data: data included on the ping (default=None)
		@type data: string
		"""
		if data is None:
			dataLength = 0
		else:
			dataLength = len(data)
			
		ws_tpl = templates.ws(fin=1, mask=0, rsv1=0, rsv2=0, rsv3=0, opcode=codec.WEBSOCKET_OPCODE_PING, 
														data=data, data_length=dataLength, more=templates.sent() )
		wsdata = self.wsCodec.encodeWsData(tpl=ws_tpl)
	
		# Send websocket data
		try:
			lower = self.ADP_HTTP.tcp().sendData( data=wsdata )
		except Exception as e:
			#raise Exception("send request: tcp failed: %s" % str(e))	
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "send request: tcp failed: %s" % str(e) )
		
		lower.addLayer( ws_tpl )
		
		# Log event
		if self.logEventSent:
			lower.addRaw(raw=wsdata)
			self.logSentEvent( shortEvt = codec.WEBSOCKET_OPCODE_PING_STR, tplEvt = lower ) 

	@doc_public
	def sendClose(self, data=None):
		"""
		Send close 
		
		@param data: data included on the clise operation (default=None)
		@type data: string
		"""
		if data is None:
			dataLength = 0
		else:
			dataLength = len(data)
			
		ws_tpl = templates.ws(fin=1, mask=0, rsv1=0, rsv2=0, rsv3=0, opcode=codec.WEBSOCKET_OPCODE_CLOSE, 
														data=data, data_length=dataLength, more=templates.sent() )
		wsdata = self.wsCodec.encodeWsData(tpl=ws_tpl)
	
		# Send websocket data
		try:
			lower = self.ADP_HTTP.tcp().sendData( data=wsdata )
		except Exception as e:
			#raise Exception("send request: tcp failed: %s" % str(e))	
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "send request: tcp failed: %s" % str(e) )
		
		lower.addLayer( ws_tpl )
		
		# Log event
		if self.logEventSent:
			lower.addRaw(raw=wsdata)
			self.logSentEvent( shortEvt = codec.WEBSOCKET_OPCODE_CLOSE_STR, tplEvt = lower ) 
	@doc_public
	def sendPong(self, data=None):
		"""
		Send pong 
		
		@param data: data included on the pong (default=None)
		@type data: string
		"""
		if data is None:
			dataLength = 0
		else:
			dataLength = len(data)
			
		ws_tpl = templates.ws(fin=1, mask=0, rsv1=0, rsv2=0, rsv3=0, opcode=codec.WEBSOCKET_OPCODE_PONG, 
														data=data, data_length=dataLength, more=templates.sent() )
		wsdata = self.wsCodec.encodeWsData(tpl=ws_tpl)
	
		# Send websocket data
		try:
			lower = self.ADP_HTTP.tcp().sendData( data=wsdata )
		except Exception as e:
			#raise Exception("send request: tcp failed: %s" % str(e))	
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "send request: tcp failed: %s" % str(e) )
		
		lower.addLayer( ws_tpl )
		
		# Log event
		if self.logEventSent:
			lower.addRaw(raw=wsdata)
			self.logSentEvent( shortEvt = codec.WEBSOCKET_OPCODE_PONG_STR, tplEvt = lower ) 
		
	@doc_public
	def isHandshakeSuccessful(self, timeout=1.0):
		"""
		Wait to receive "handshake successful" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['ssl-support']:
			tpl_rsp.addLayer(  AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer(  AdapterHTTP.response() )
		tpl_rsp.addLayer( templates.ws(more=templates.handshake_ok()) )
		return self.received(expected=tpl_rsp, timeout=timeout)
		
	@doc_public
	def isConnected(self, timeout=1.0):
		"""
		Wait to receive "connected" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isConnected(timeout=timeout)

	@doc_public
	def isDisconnected(self, timeout=1.0):
		"""
		Wait to receive "disconnected" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_HTTP.isDisconnected(timeout=timeout)
		
	@doc_public
	def hasReceivedData(self, timeout=1.0, opcode=None):
		"""
		Waits to receive "data" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@param opcode: operation code (default=None)
		@type opcode: integer
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['ssl-support']:
			tpl_rsp.addLayer(  AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer( templates.ws(opcode=opcode, more=templates.received()) )
		return self.received(expected=tpl_rsp, timeout=timeout)

	@doc_public
	def hasReceivedText(self, timeout=1.0):
		"""
		Waits to receive "text" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['ssl-support']:
			tpl_rsp.addLayer(  AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer( templates.ws(opcode=codec.WEBSOCKET_OPCODE_TEXT, more=templates.received()) )
		return self.received(expected=tpl_rsp, timeout=timeout)

	@doc_public
	def hasReceivedBinary(self, timeout=1.0):
		"""
		Waits to receive "binary" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['ssl-support']:
			tpl_rsp.addLayer(  AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer( templates.ws(opcode=codec.WEBSOCKET_OPCODE_BINARY, more=templates.received()) )
		return self.received(expected=tpl_rsp, timeout=timeout)

	@doc_public
	def hasReceivedPong(self, timeout=1.0):
		"""
		Waits to receive "pong" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['ssl-support']:
			tpl_rsp.addLayer(  AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer( templates.ws(opcode=codec.WEBSOCKET_OPCODE_PONG, more=templates.received()) )
		return self.received(expected=tpl_rsp, timeout=timeout)

	@doc_public
	def hasReceivedPing(self, timeout=1.0):
		"""
		Waits to receive "ping" event until the end of the timeout.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl_rsp = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl_rsp.addLayer( layer_agent )
			
		tpl_rsp.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl_rsp.addLayer(  AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.cfg['ssl-support']:
			tpl_rsp.addLayer(  AdapterSSL.ssl(more=AdapterSSL.received()) )
		tpl_rsp.addLayer( templates.ws(opcode=codec.WEBSOCKET_OPCODE_PING, more=templates.received()) )
		return self.received(expected=tpl_rsp, timeout=timeout)