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
import time
import Queue

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapter.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapter.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapter.getVersion()]
AdapterSOCKS = sys.modules['SutAdapters.%s.SOCKS' % TestAdapter.getVersion()]

import codec
import copy
import templates

__NAME__="""HTTP_SERVER"""

AGENT_EVENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='socket'

class ClientObj(object):
	def __init__(self, parent, address):
			"""
			"""
			self.parent = parent
			self.address = address
			self.id = None
			
			self.buf = ''
			# init the HTTP encoder/decoder 
			self.httpCodec = codec.Codec( parent=self, 
																									octetStreamSupport=self.parent.cfg['http_octet_stream_support'],
																									manStreamSupport=self.parent.cfg['http_man_stream_support'],
																									truncateBody=self.parent.cfg['http_truncate_body'],
																									strictMode=self.parent.cfg['http_strict_mode'],
																									websocketMode=self.parent.cfg['http_websocket_mode'] 
																								)

	def codec(self):
		"""
		"""
		return self.httpCodec
		
	def error(self, msg):
		"""
		"""
		self.parent.error("[Client=%s]\n\n%s" % (self.address, msg) )
	def debug(self, msg):
		"""
		"""
		self.parent.debug("[Client=%s]\n\n%s" % (self.address, msg) )
	def warning(self, msg):
		"""
		"""
		self.parent.warning("[Client=%s]\n\n%s" % (self.address, msg) )
	def info(self, msg):
		"""
		"""
		self.parent.info("[Client=%s]\n\n%s" % (self.address, msg) )
		
	def onIncomingData(self, data, lower):
		"""
		"""
		if self.parent.cfg['http_websocket_mode'] :
			self.onWebsocketIncomingData(data, lower)
		else:
			try:
				# put in the buffer the data received
				self.buf += data
				self.debug('data received (bytes %d), decoding attempt...' % len(self.buf))
				self.debug( data )
				
				# try to decode it, the request can be not complete
				(ret, decodedMessageTpl, summary, left) = self.httpCodec.decode(rsp=self.buf, request=True)
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
					
				else:
					self.debug( 'unknown decoding error: %s' % str(ret) )
					self.warning(self.buf)
					raise Exception('bad response received')
					
			except Exception as e:
				self.error('Error on http incoming data: %s' % str(e))		

	def onNoMoreData(self, lower):
		"""
		"""
		if self.parent.cfg['http_websocket_mode']:
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
		self.id = lower.get("TCP", "client-id")
		
		responseRaw = self.buf
		if self.parent.logEventReceived:
			lower.addRaw(raw=responseRaw) # add the raw request to the template
			
			# log event 		
			self.parent.logRecvEvent( shortEvt = summary, tplEvt = lower ) 
			self.parent.registerEvent(event=lower)
			
		# reset the buffer
		self.buf = ''	
		
class Server(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False, agentSupport=False, agent=None,
														 bindIp = '', bindPort=0,  sslSupport=False,  strictMode=False, octetStreamSupport=True, 
														 manStreamSupport=True, websocketMode=False, truncateBody=False,
														  logEventSent=True, logEventReceived=True, checkCert=AdapterSSL.CHECK_CERT_NO, certfile="/tmp/cert.file",keyfile="/tmp/key.file"):
		"""
		HTTP server, based on TCP server adapter.
		
		@param parent: parent testcase
		@type parent: testcase

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
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer

		@param sslSupport: activate SSL channel (default=False)
		@type sslSupport: boolean
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
		
#		self.TIMER_ALIVE_AGT = TestAdapter.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
#																																logEvent=False, enabled=True)
																																
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.cfg['http_truncate_body'] = truncateBody
		self.cfg['http_strict_mode'] = strictMode
		self.cfg['http_websocket_mode'] = websocketMode
		self.cfg['http_octet_stream_support'] = octetStreamSupport
		self.cfg['http_man_stream_support'] = manStreamSupport
		
		self.clients = {}
		self.eventsExpected = []
		self.eventsQueue = Queue.Queue(0)
		
		self.ADP_TCP = AdapterTCP.Server(parent=parent, bindIp = bindIp, bindPort=bindPort, separatorDisabled=True, 
																													logEventSent=False, logEventReceived=False, agent=agent, shared=shared,
																													agentSupport=agentSupport, sslSupport=sslSupport, checkCert=checkCert, certfile=certfile,keyfile=keyfile)
		self.ADP_TCP.onClientIncomingData = self.onClientIncomingData	
		self.ADP_TCP.onClientNoMoreData = self.onClientNoMoreData
		
		self.__checkConfig()
		
		# initialize the agent with no data

	def registerEvent(self, event):
		"""
		"""
		self.eventsQueue.put(event)
		
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
#		if self.cfg['agent-support'] :
			# stop timer
#			self.TIMER_ALIVE_AGT.stop()
			# cleanup remote agent
#			self.resetAgent()
#		self.stopRunning()
		

	# specific functions
	@doc_public
	def activateAutoAnswer(self, eventsExpected=[]):
		"""
		Activate the auto answer mode
		Provide the requests expected and the associate responses
		"""
		evtsTpl = []
		for (req,rsp) in eventsExpected:

			tplReq = self.getTemplateRequest(httpMethod=req["method"], httpUri=req["uri"], httpVersion=req["version"],  
																											httpHeaders=req["headers"], httpBody=req["body"])
			tplRsp = self.getTemplateResponse(code=rsp["code"], phrase=rsp["phrase"], version=rsp["version"], 
																											headers=rsp["headers"], body=rsp["body"])
			answer = { "count": 0, "request":  tplReq, "response": tplRsp}
			evtsTpl.append(answer)
			
		self.eventsExpected = evtsTpl
		self.warning("auto answer mode activated")
		self.setRunning()
	@doc_public
	def stopAutoAnswer(self):
		"""
		Stop the auto answer mode
		"""
		self.unsetRunning()
		self.eventsExpected = []
		
	def onRun(self):
		"""
		"""
		try:
			if not self.eventsQueue.empty():
				evt = self.eventsQueue.get(False)
				clientId =  evt.get("TCP", "client-id")
				comparator= TestTemplates.Template(parent=None)
				
				matches = []
				for answer in self.eventsExpected:
					ret = comparator.compare(template=evt, expected=answer["request"])
					if ret:
						answer["count"] += 1
						matches.append( answer )

				# get only one matche
				if len(matches):
					greaterEvent = matches[0]
					maxSize = matches[0]["request"].getSize() 
					for m in matches:
						if m["request"].getSize() > maxSize:
							greaterEvent = m
							maxSize = m["request"].getSize()

					self.sendResponse(clientId=clientId,tpl=greaterEvent["response"])
				
		except Exception as e:
			self.error("%s" % e)

	@doc_public
	def startListening(self):
		"""
		Start to listen
		"""
		self.ADP_TCP.startListening()
		
	@doc_public
	def stopListening(self):
		"""
		Stop to listen
		"""
		self.ADP_TCP.stopListening()
		
	@doc_public
	def isListening(self, timeout=10.0):
		"""
		Wait to receive "listening" until the end of the timeout.

		@param timeout: time to wait in seconds (default=10s)
		@type timeout: float
	
		@return: stopped event or none
		@rtype:	templatemessage/templatelayer/none	
		"""
		return self.ADP_TCP.isListening(timeout=timeout)
		
	@doc_public
	def isStopped(self, timeout=10.0):
		"""
		Wait to receive "stopped" until the end of the timeout.

		@param timeout: time to wait in seconds (default=10s)
		@type timeout: float
	
		@return: stopped event or none
		@rtype:	templatemessage/templatelayer/none	
		"""
		return self.ADP_TCP.isStopped(timeout=timeout)
		
	def onClientIncomingData(self, clientAddress, data, lower=None):
		"""
		"""
		if clientAddress not in self.clients:
			clt = ClientObj(parent=self, address=clientAddress)
			self.clients[clientAddress] = clt
			
			# handle incoming data
			clt.onIncomingData(data=data, lower=lower)
			
		else:
			clt = self.clients[clientAddress]
			clt.onIncomingData(data=data, lower=lower)
			
	def onClientNoMoreData(self, clientAddress, lower):
		"""
		"""
		clt = self.clients[clientAddress]
		clt.onNoMoreData(lower=lower)

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

	@doc_public
	def sendResponse(self, clientId, tpl):
		"""
		Send a response

		@param clientId: client id
		@type clientId: tuple
		
		@param tpl: http response
		@type tpl: templatelayer

		@return: lower template
		@rtype:	template	
		"""
		try:
			# check if tpl is not none
			if tpl is  None:	raise Exception( 'tpl empty' )

			# find the client 
			cltObj = None
			for cltAddr, cltObj in self.clients.items():
				if cltObj.id == clientId:
					cltObj = cltObj
					break
					
			if cltObj is None:
				raise Exception( 'client %s not found' % clientId )
				
			# encode template
			try:
				(encodedMessage, summary) = cltObj.codec().encode(http=tpl, request=False)
			except Exception as e:
				raise Exception("codec error: %s" % str(e))	

			# Send request
			try:
				lower = self.ADP_TCP.sendData( clientId=clientId, data=encodedMessage )
			except Exception as e:
				raise Exception("tcp failed: %s" % str(e))	

			tpl.addRaw( encodedMessage )
			lower.addLayer( tpl )

			# Log event
			if self.logEventSent:
				lower.addRaw(raw=encodedMessage)
				self.logSentEvent( shortEvt = summary, tplEvt = lower ) 

		except Exception as e:
			raise Exception('unable to send response: %s' % str(e))
		return lower
	def getDefaultHeaders(self):
		"""
		Internal function
		"""
		return {}
		
	@doc_public
	def sendHttp(self, clientId, code="200", phrase="OK", version="HTTP/1.1", headers={}, body=None, overwriteCl=False):
		"""
		Send a response.
		
		@param clientId: client id
		@type clientId: integer
		
		@param code: code  (default=200)
		@type code: string
		
		@param phrase: phrase  (default=OK)
		@type phrase: string
		
		@param version: http version (default=HTTP/1.1)
		@type version: string

		@param headers: additional headers to add {key:value, ...}
		@type headers: dict

		@param body: http content of the response
		@type body: string/none
		"""
		__hdrs = {  }
		
		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		 
		
		if body is not None :
			lenBod = len(body)
			if lenBod > 0: 	self.addContentLength(__hdrs, lenBod, overwriteCl)
					
		# prepare response template and send it
		tpl = templates.response(version=version, code=code, phrase=phrase, headers=__hdrs, body=body)

		self.sendResponse(clientId=clientId, tpl=tpl)
	@doc_public
	def hasReceivedRequest(self, expected, timeout=1.0):
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
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if expected is None:
			raise Exception( 'has received response: expected template cannot be empty' )
		tpl_expected = expected
		if isinstance( expected, TestTemplates.TemplateLayer ):
			tpl_expected = TestTemplates.TemplateMessage()
		
			if self.cfg['agent-support']:
				layer_agent= TestTemplates.TemplateLayer('AGENT')
				layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
				layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
				tpl_expected.addLayer( layer_agent )
				
			tpl_expected.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
			tpl_expected.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )

			if self.ADP_TCP.cfg['ssl-support']:
				tpl_expected.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
			tpl_expected.addLayer( expected )
		evt = self.received( expected = tpl_expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	@doc_public
	def hasReceivedHttpRequest(self, httpMethod="GET", httpUri="/", httpVersion='HTTP/1.1', timeout=1.0, 
																											httpHeaders={}, httpBody=None):
		"""
		Wait to receive "http request" until the end of the timeout.

		@param httpMethod: http method (default=GET)
		@type httpMethod: string

		@param httpUri: http phrase (default=OK)
		@type httpUri: string

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

		tpl = TestTemplates.TemplateMessage()
		   
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )

		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )		 
		if self.ADP_TCP.cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		headers = { }
		headers.update(httpHeaders)
		tpl.addLayer( templates.request( method=httpMethod, uri=httpUri, version=httpVersion, headers=headers, body=httpBody) )
		
		return self.hasReceivedRequest(expected=tpl, timeout=timeout)
	@doc_public
	def getTemplateResponse(self, code="200", phrase="OK", version="HTTP/1.1", headers={}, body=None, overwriteCl=False):
		"""
		"""
		__hdrs = {  }
		
		# add additional headers
		__hdrs.update(self.getDefaultHeaders())
		__hdrs.update(headers)		 
		
		if body is not None :
			lenBod = len(body)
			if lenBod > 0: 	self.addContentLength(__hdrs, lenBod, overwriteCl)
					
		# prepare response template and send it
		tpl = templates.response(version=version, code=code, phrase=phrase, headers=__hdrs, body=body)
		return tpl
		
	@doc_public
	def getTemplateRequest(self, httpMethod="GET", httpUri="/", httpVersion='HTTP/1.1',  httpHeaders={}, httpBody=None):
		"""
		"""
		tpl = TestTemplates.TemplateMessage()
		   
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )

		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )		 
		if self.ADP_TCP.cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
			
		headers = { }
		headers.update(httpHeaders)
		tpl.addLayer( templates.request( method=httpMethod, uri=httpUri, version=httpVersion, headers=headers, body=httpBody) )
		
		return tpl
	
	@doc_public
	def waitRequests(self, count=1, timeout=1.0):
		"""
		Wait to received requests according to the counter provided
		Use this function when the auto answer mode is activated
		
		@param count: number to expected requests (default=1)
		@type count: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: True if all requests are received
		@rtype:	 boolean	  
		"""
		ret = False
		timeoutBool = False
		startTime = time.time()
		while (not ret) and (not timeoutBool):
			time.sleep(0.01)
			if (time.time() - startTime) >= timeout:
				timeoutBool = True
			subRet = True
			for answer in self.eventsExpected:
				if answer["count"] < count:
					subRet &= False
			if subRet:  ret = True
		return ret