#!/usr/bin/env python
# -*- coding=utf-8 -*-

# ------------------------------------------------------------------
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
import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import subprocess
import time
import uuid
import os

try:
	import curl_templates
except ImportError: # python3 support
	from . import curl_templates


from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

__NAME__="""CURL_HTTP"""

AGENT_EVENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='curl'

CURL_BIN = "/usr/local/bin/curl"

class Curl(TestAdapterLib.Adapter):
	@doc_public	
	def __init__(self, parent, name=None, debug=False, shared=False, agentSupport=False, 
											agent=None, logEventSent=True, logEventReceived=True):
		"""
		Curl wrapper

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
		"""
		TestAdapterLib.Adapter.__init__(self, 
																								name = __NAME__, 
																								parent = parent, 
																								debug=debug, 
																								realname=name,
																								agentSupport=agentSupport, 
																								agent=agent, 
																								shared=shared,
																								caller=TestAdapterLib.caller(),
																								agentType=AGENT_TYPE_EXPECTED)
		self.parent = parent
		
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		if agent is not None:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = agentSupport
		
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, 
																																			duration=20, 
																																			name="keepalive-agent", 
																																			callback=self.aliveAgent,
																																			logEvent=False, 
																																			enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		if agent is not None:
			if self.cfg['agent-support']:
				self.prepareAgent(data={'shared': shared})
				if self.agentIsReady(timeout=30) is None: 
					raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
				self.TIMER_ALIVE_AGT.start()
			
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], 
																																											self.cfg['agent']['type']) ) 

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
		
		elif data["cmd"] == "send-http":
			if data["response-type"] == "http-request":
				
				req_out = data["headers"] .splitlines()
				
				tpl_req = TestTemplates.TemplateMessage()
				layer_curl = TestTemplates.TemplateLayer('CURL_HTTP')
				layer_curl.addKey(name='headers', data= data["headers"] )
				tpl_req.addLayer( layer_curl )
				
				if "body" in data:
					layer_curl.addKey(name='body', data=  data["body"])	
					req_out.append(  "" )
					req_out.append( data["body"] )  
				
				tpl_req.addRaw("\n".join(req_out)  )
				if self.logEventSent: self.logSentEvent( shortEvt = req_out[0], tplEvt = tpl_req ) 
				
			elif data["response-type"] == "http-response":
				
				rsp_in = data["headers"] .splitlines()
				
				rsp_decoded = rsp_in[0].split(" ", 2)
				rsp_code = rsp_decoded[1]
				rsp_version = rsp_decoded[0]
				rsp_phrase =  rsp_decoded[2]
				
				# log event 
				tpl_rsp = TestTemplates.TemplateMessage()
				layer_curl = TestTemplates.TemplateLayer('CURL_HTTP_RESPONSE')
				layer_curl.addKey(name='code', data= rsp_code)
				layer_curl.addKey(name='phrase', data= rsp_phrase)
				layer_curl.addKey(name='version', data= rsp_version)
				layer_curl.addKey(name='headers', data= "\n".join(rsp_in[1:]) )
				if "body"  in data:
					layer_curl.addKey(name='body', data=  data["body"])	
					rsp_in.append(  "" )
					rsp_in.append( data["body"] )
		
				tpl_rsp.addLayer( layer_curl )
				tpl_rsp.addRaw("\n".join(rsp_in)  )
				if self.logEventReceived: self.logRecvEvent( shortEvt = rsp_in[0], tplEvt = tpl_rsp ) 
					
			elif data["response-type"] == "http-info":
				conn_info = data["debug"] .splitlines()
				
				tpl_info = TestTemplates.TemplateMessage()
				layer_curl = TestTemplates.TemplateLayer('CURL_HTTP_INFO')
				layer_curl.addKey(name='perf', data= conn_info[-1] )
				layer_curl.addKey(name='debug', data= "\n".join(conn_info[:-1]) )
				tpl_info.addLayer( layer_curl )
				tpl_info.addRaw("\n".join(conn_info)  )
				if self.logEventReceived: self.logRecvEvent( shortEvt = "conn info", tplEvt = tpl_info ) 
				
			else:
				self.warning("unknown response type received %s" % data["response-type"] )
		else:
			self.warning("unknown command received")
			
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
		self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), 
																								agentName=self.cfg['agent-name'], 
																								agentData=data)
	
	def prepareAgent(self, data):
		"""
		prepare agent
		"""
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), 
																								agentName=self.cfg['agent-name'], 
																								agentData=data)
	
	def initAgent(self, data):
		"""
		Init agent
		"""
		self.parent.sendInitToAgent(adapterId=self.getAdapterId(), 
																						agentName=self.cfg['agent-name'], 
																						agentData=data)

	def resetAgent(self):
		"""
		Reset agent
		"""
		self.parent.sendResetToAgent(adapterId=self.getAdapterId(), 
																								agentName=self.cfg['agent-name'], 
																								agentData='')

	def aliveAgent(self):
		"""
		Keep alive agent
		"""
		self.parent.sendAliveToAgent(adapterId=self.getAdapterId(), 
																							agentName=self.cfg['agent-name'], 
																							agentData='')
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
		

	@doc_public	
	def sendHttp(self, host, method=None,  headers=None, body=None, more=None, 
												proxy_host=None, timeout_connect=10, timeout_max=10):
		"""
		Make a HTTP request
		"""
		if self.cfg['agent-support']:
				remote_cfg = {'cmd': 'send-http', 
															'host': host,
															'timeout-connect': timeout_connect,
															'timeout-max': timeout_max}
				if method is not None:
					remote_cfg["method"] = method
				if headers is not None:
					remote_cfg["headers"] = headers
				if body is not None:
					remote_cfg["body"] = body
				if proxy_host is not None:
					remote_cfg["proxy-host"] = proxy_host
				if more is not None:
					remote_cfg["more"] = more
				self.sendNotifyToAgent(data=remote_cfg)
		else:
			infile = "/tmp/req_%s" % uuid.uuid4()
			outfile = "/tmp/rsp_%s" % uuid.uuid4()
			
			curl_cmd = '%s -v %s -s ' % (CURL_BIN, host)
			curl_cmd += ' --user-agent ExtensiveAutomation'
			
			if method is not None:
				curl_cmd += " -X %s" % method
			if headers is not None:
				for hdr in headers.splitlines():
					curl_cmd += ' -H "%s"' % hdr
			if proxy_host is not None:
				curl_cmd += ' -x %s' % proxy_host
				
			if more is not None:
				curl_cmd += " %s" % (more)
				
			curl_cmd += ' -w '
			curl_cmd += '"\n%{time_connect},%{time_total},%{speed_download},'
			curl_cmd += '%{time_appconnect}, %{time_namelookup},'
			curl_cmd += '%{http_code},%{size_download},'
			curl_cmd += '%{url_effective},%{remote_ip}\n"'
	
			curl_cmd+= '	--connect-timeout %s --max-time %s ' % ( timeout_connect, timeout_max)
			curl_cmd += ' -o "%s"' % outfile
			
			if body is not None:
				with open(infile, "wb") as f:
					f.write(body)
				curl_cmd += ' --data-binary "@%s"'  % infile
				
			self.debug(curl_cmd)
			
			try:
				ps = subprocess.Popen(curl_cmd, shell=True, 
																					stdout=subprocess.PIPE, 
																					stderr=subprocess.STDOUT,
																					bufsize=0)
		
				conn_info = []
				req_out = []
				rsp_in = []
				
				self.trace("curl - command executed")
				while True:
					line = ps.stdout.readline()
					line = line.decode('latin-1').encode("utf-8") 
					if line != '':
						if line.startswith("*"):
							conn_info.append(line[1:].strip())
						elif line.startswith("> "):
							req_out.append(line[2:].strip())
						elif line.startswith("< "):
							if not len(rsp_in):
								
								# log event 
								tpl_req = TestTemplates.TemplateMessage()
								layer_curl = TestTemplates.TemplateLayer('CURL_HTTP')
								layer_curl.addKey(name='headers', data= "\n".join(req_out) )
								if body is not None:
									layer_curl.addKey(name='body', data=  body)						
								tpl_req.addLayer( layer_curl )
								if body is not None: req_out.append(body)
								tpl_req.addRaw("\n".join(req_out)  )
								if self.logEventSent: self.logSentEvent( shortEvt = req_out[0], tplEvt = tpl_req ) 
	
							rsp_in.append(line[2:].strip())	
						elif line.startswith("{"):
							continue
						elif line.startswith("}"):
							continue
						else:
							conn_info.append(line.strip())
					else:
						break
						
				# read the response 
				self.trace("curl - reading the response")
				rsp_body=None
				if len(rsp_in):
					rsp_decoded = rsp_in[0].split(" ", 2)
					rsp_code = rsp_decoded[1]
					rsp_version = rsp_decoded[0]
					rsp_phrase =  rsp_decoded[2]
				
					self.trace("curl - log response")
					with open(outfile) as f:
						rsp_body = f.read()
	
					# log event 
					tpl_rsp = TestTemplates.TemplateMessage()
					layer_curl = TestTemplates.TemplateLayer('CURL_HTTP_RESPONSE')
					layer_curl.addKey(name='code', data= rsp_code)
					layer_curl.addKey(name='phrase', data= rsp_phrase)
					layer_curl.addKey(name='version', data= rsp_version)
					layer_curl.addKey(name='headers', data= "\n".join(rsp_in[1:]) )
					if rsp_body is not None:
						layer_curl.addKey(name='body', data=  rsp_body)						
					tpl_rsp.addLayer( layer_curl )
					if rsp_body is not None: rsp_in.append(rsp_body)
					tpl_rsp.addRaw("\n".join(rsp_in)  )
					if self.logEventReceived: self.logRecvEvent( shortEvt = rsp_in[0], tplEvt = tpl_rsp ) 
	
	
				# log event 
				self.trace("curl - log http info")
				tpl_info = TestTemplates.TemplateMessage()
				layer_curl = TestTemplates.TemplateLayer('CURL_HTTP_INFO')
				layer_curl.addKey(name='perf', data= conn_info[-1] )
				layer_curl.addKey(name='debug', data= "\n".join(conn_info[:-1]) )
				tpl_info.addLayer( layer_curl )
				tpl_info.addRaw("\n".join(conn_info)  )
				if self.logEventReceived: self.logRecvEvent( shortEvt = "conn info", tplEvt = tpl_info ) 
					
			except Exception as e:
				self.error("exception - %s" % e)
				
			try:
				os.remove(infile)
			except:
				pass
			try:
				os.remove(outfile)
			except:
				pass

	@doc_public	
	def hasReceivedHttpResponse(self, httpCode=None, httpPhrase=None, httpVersion=None, 
																									httpHeaders=None, httpBody=None, timeout=1.0):
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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)

		tpl_expected = TestTemplates.TemplateMessage()
		layer_curl = curl_templates.response(version=httpVersion, 
																												code=httpCode, 
																												phrase=httpPhrase, 
																												headers=httpHeaders, 
																												body=httpBody)
		tpl_expected.addLayer( layer_curl )
		
		evt = self.received( expected = tpl_expected, timeout = timeout )
		if evt is None:
			return None
		return evt