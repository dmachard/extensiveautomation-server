#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterSOCKS = sys.modules['SutAdapters.%s.SOCKS' % TestAdapterLib.getVersion()]

try:
	import codec
	import templates
except ImportError: # python3 support
	from . import codec
	from . import templates
	
__NAME__="""TELNET"""

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, bindIp = '', bindPort=0, destIp='127.0.0.1', destPort=23, destHost='',
									socketTimeout=10.0, socketFamily=AdapterIP.IPv4,  doEcho=True, name=None,
									proxyType=AdapterTCP.PROXY_SOCKS4, proxyUserID='xtc', proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False,
									debug=False, logEventSent=True, logEventReceived=True, parentName=None
									, agentSupport=False, agent=None, shared=False, saveContent=False):
		"""
		This class enable to use TELNET (rfc854) as client only,
		lower network layer (IP, Ethernet) are not controlable.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer

		@param destIp: destination ip
		@type destIp: string

		@param destPort: destination port
		@type destPort: integer

		@param destHost: destination host (automatic dns resolution)
		@type destHost: string

		@param proxyType: SutAdapters.TCP.PROXY_SOCKS4 | SutAdapters.TCP.PROXY_SOCKS5 (default=PROXY_SOCKS4)
		@type proxyType: strconstant
		
		@param proxyUserID: user id with socks (default=xtc)
		@type proxyUserID: string
		
		@param proxyIp: proxy ip
		@type proxyIp: string

		@param proxyPort: proxy port
		@type proxyPort: integer

		@param proxyHost: proxy host (automatic dns resolution)
		@type proxyHost: string
		
		@param proxyEnabled: True to support proxy (default=False)
		@type proxyEnabled: boolean
		
		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: intconstant

		@param socketTimeout: timeout to connect in second (default=1s)
		@type socketTimeout: float

		@param doEcho: send do echo command on True
		@type doEcho: boolean

		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		
		@param saveContent: save content in the private storage (default=False)
		@type saveContent:	boolean
		"""
		if not isinstance(bindPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "bindPort argument is not a integer (%s)" % type(bindPort) )
		if not isinstance(destPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "destPort argument is not a integer (%s)" % type(destPort) )
		if not isinstance(proxyPort, int):
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "proxyPort argument is not a integer (%s)" % type(proxyPort) )
			
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, realname=name, shared=shared,
																									debug=debug, agentSupport=agentSupport, agent=agent,
																									caller=TestAdapterLib.caller(),
																									agentType=AGENT_TYPE_EXPECTED)
		if parentName is not None:
			TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__)  )
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		# prepare tcp adapter
		self.tcp = AdapterTCP.Client(parent=parent, bindIp = bindIp, bindPort=bindPort, 
																		destinationIp=destIp, destinationPort=destPort,  destinationHost=destHost, 
																		socketTimeout=socketTimeout, socketFamily=socketFamily, inactivityTimeout=0, 
																		proxyType=proxyType, proxyUserID=proxyUserID, proxyIp=proxyIp, proxyPort=proxyPort,
																		proxyHost=proxyHost, proxyEnabled=proxyEnabled,
																		separatorDisabled=True, sslSupport=False, name=name,
																		debug=debug, logEventSent=False, logEventReceived=False, shared=shared,
																		parentName=__NAME__, agentSupport=agentSupport, agent=agent)
		# callback tcp
		self.tcp.handleIncomingData = self.onIncomingData	
		self.tcp.handleNoMoreData = self.onNoMoreData

		# telnet options
		self.cfg = {}	
		# proxy
		self.cfg['proxy-enabled'] = proxyEnabled
		# option to sent
		self.cfg['do-echo'] = doEcho
		# ip layer
		self.cfg['telnet-source-ip'] = bindIp
		self.cfg['telnet-source-port'] = int(bindPort)
		self.cfg['telnet-destination-ip'] = destIp
		self.cfg['telnet-destination-port'] = int(destPort)
		# options 
		self.cfg['telnet-remote-opts'] = []
		self.cfg['telnet-save-content'] = saveContent
		# agent
		self.cfg['agent-support'] = agentSupport
		if self.cfg['agent-support'] :
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']

		self.doEchoSent = False
		self.buf = ''
		
		# init the telnet encoder/decoder 
		self.telnetCodec = codec.Codec(parent=self)
		
		if self.cfg['telnet-save-content']: self.warning("TELNET AdapterID=%s" % self.getAdapterId() )

	def __negotiateOptions(self, opts):
		"""
		Negotiate options
		"""
		opts_rsp = []
		for opt_req, opt_cmd in opts:
			# do echo
			if opt_req == codec.WILL and opt_cmd == codec.ECHO:
				if not self.doEchoSent:
					opts_rsp.append( (codec.DO, codec.ECHO )  )
					self.doEchoSent = True

			# dont echo
			elif opt_req == codec.DONT and opt_cmd == codec.ECHO:
				opts_rsp.append( (codec.WONT,opt_cmd )  )
				
			# do echo 
			elif opt_req == codec.DO and opt_cmd == codec.ECHO:
				opts_rsp.append( (codec.WILL,opt_cmd )  )
				
			# wont 
			elif opt_req == codec.DO:
				opts_rsp.append( (codec.WONT,opt_cmd )  )
			
		# refuse all options
		if len(opts_rsp):
			self.sendOptions(opts=opts_rsp)

		if not self.doEchoSent:
			self.doEchoSent = True
			self.sendOptions(opts=[ (codec.DO, codec.ECHO) ] )
	def onReset(self):
		"""
		Reset
		"""
		self.tcp.onReset()
	@doc_public
	def connection(self, timeout=1.0):
		"""
		Tcp connection and wait the connection event until the end of the timeout
		Proxy supported.
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: connection result
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = True
		self.connect()
		if self.isConnected(timeout=timeout) is None:
			ret = False
		if self.cfg['proxy-enabled']:
			if self.tcp.isAcceptedProxy(timeout=timeout) is None:
				ret = False
		return ret
		
	@doc_public
	def disconnection(self, timeout=1.0):
		"""
		Tcp disconnection and wait the disconnection event until the end of the timeout
		
		@param timeout: time to wait response in second (default=1s)
		@type timeout: float
		
		@return: disconnection result
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = True
		self.disconnect()
		if self.isDisconnected(timeout=timeout) is None:
			ret = False
		if self.cfg['proxy-enabled']:
			if self.tcp.isAcceptedProxy(timeout=timeout) is None:
				ret = False			
		return ret
	@doc_public
	def connect(self):
		"""
		Start the TCP connection
		"""
		self.tcp.connect()
	
	@doc_public
	def disconnect(self):
		"""
		Close the TCP connection
		"""
		self.tcp.disconnect()
	
	@doc_public
	def isAcceptedProxy(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None):
		"""
		Wait accepted proxy event until the end of the timeout
		
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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.tcp.isAcceptedProxy(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
											sourcePort=sourcePort, destinationPort=destinationPort)
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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.tcp.isConnected(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
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
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.tcp.isDisconnected(timeout=timeout, byServer=byServer, versionIp=versionIp, 
						sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
						
	def sendOptions(self, opts):
		"""
		opts = list of tuple of integer
		"""
		nb_cmd = 0
		tpl_cmds = TestTemplatesLib.TemplateLayer(name='')
		for i in xrange(len(opts)):
			cmd, opt = opts[i]
			cmds_str = ''
			if cmd in codec.TELNET_COMMANDS:
				cmds_str = '%s' % codec.TELNET_COMMANDS[cmd]
			else:
				self.warning("telnet command not supported: %s" % cmd)
			if opt in codec.TELNET_OPTIONS:
				cmds_str += ' %s' % codec.TELNET_OPTIONS[opt]
			else:
				self.warning("telnet option not supported: %s" % opt)
				cmd_str += ' Unsupported'
			tpl_cmds.addKey(name="%s" % nb_cmd, data=cmds_str)
			nb_cmd += 1
			
		tpl = templates.telnet(cmds=tpl_cmds)
		self.sendData(tpl=tpl)
		
	def sendSubOption(self, optName, subopts):
		"""
		subopts = list of tuple
		"""
		nb_cmd = 0
		
		optNameFinal = ''
		if optName in codec.TELNET_OPTIONS:
			optNameFinal = codec.TELNET_OPTIONS[optName]
		

		tpl_sub = TestTemplatesLib.TemplateLayer(name='')
		for (optDescr,optValue) in subopts:
			tpl_sub.addKey(name=optDescr, data=optValue)

		tpl_subs = TestTemplatesLib.TemplateLayer(name='')	
		tpl_subs.addKey( optNameFinal,tpl_sub )
		
		tpl = templates.telnet(subs=tpl_subs)
		self.sendData(tpl=tpl)

	def onIncomingData(self, data, lower=None):
		"""
		"""
		try:
			self.debug('data received (bytes %d), decoding attempt...' % len(data))
			if self.cfg['telnet-save-content'] : self.appendDataInStorage(destname="telnet_data.txt", data=data)
			self.debug( data )
			self.buf += data
			
			tpl, summary, cmds, moredata = self.telnetCodec.decode(data=self.buf)
			if len(moredata):
				self.debug( 'need more telnet data...' ) # for commands
			else:
				self.buf = ''
				
				tpl.addRaw(data)
				lower.addLayer(layer=tpl)
					
				# log event 	
				if self.logEventReceived:	
					lower.addRaw(raw=data)		
					self.logRecvEvent( shortEvt = summary, tplEvt = lower )	
				# handle data
				self.handleIncomingData( data, lower=lower )
				
				if len(cmds):
					self.__negotiateOptions(opts=cmds)
					self.cfg['telnet-remote-opts'].extend(cmds)		
		except Exception as e:
			self.error('Error while waiting for telnet data: %s' % str(e))
			
	def onNoMoreData(self, lower):
		"""
		"""
		self.debug( 'not impletemented' )	

	def handleIncomingData(self, data, lower=None):
		"""
		Function to overwrite
		Called on incoming data
		
		@param data: tcp data received
		@type data: string
		
		@param lower: template tcp data received
		@type lower: templatemessage
		"""
		pass
		
	def handleNoMoreData(self, lower):
		"""
		Function to reimplement
		
		@param lower:
		@type lower:
		 """
		pass
		
	@doc_public
	def sendData(self, tpl, dataRaw=None, optionsRaw=None):
		"""
		Send telnet data

		@param tpl: telnet
		@type tpl: templatelayer

		@param dataRaw: telnet data (default=None)
		@type dataRaw: string/none
		
		@param optionsRaw: telnet options (default=None)
		@type optionsRaw: string/none

		@return: telnet layer encapsulate in ip
		@rtype: templatemessage		
		"""
		if not self.tcp.connected:
			#raise Exception( 'tcp not connected' )
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(),  "tcp not connected" )
				
		try:
			if dataRaw is not None or optionsRaw is not None:
				tpl = templates.telnet(data=dataRaw, cmds=optionsRaw)
			# encode template
			try:
				(encodedData, summary) = self.telnetCodec.encode(telnet_tpl=tpl)
			except Exception as e:
				raise Exception("Cannot encode Telnet message: %s" % str(e))	
					
			try:
				lower = self.tcp.sendData( data=encodedData )
			except Exception as e:
				raise Exception("telnet failed: %s" % str(e))	
			
			# add sip layer to the lower layer
			tpl.addRaw( encodedData )
			lower.addLayer( tpl )
			
			# Log event
			if self.logEventSent:
				self.logSentEvent( shortEvt = summary, tplEvt = lower ) 
		except Exception as e:
			raise Exception('Unable to send telnet data: %s' % str(e))
			
		return lower	
		
	@doc_public
	def hasReceivedData(self, timeout=1.0, dataExpected=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param dataExpected: data expected (default=None)
		@type dataExpected:	string/operators/none			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		layer_ip = AdapterIP.ip() 		
		layer_tcp = AdapterTCP.tcp()
		
		tpl = TestTemplatesLib.TemplateMessage()

		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_tcp)
		
		if self.tcp.cfg['proxy-enabled']:
			layer_sock = AdapterSOCKS.socks(more=AdapterSOCKS.received())
			tpl.addLayer(layer=layer_sock)
				
		layer_telnet = templates.telnet()
		if dataExpected is not None:
			layer_telnet.addKey( name='data', data=dataExpected )
		tpl.addLayer(layer=layer_telnet)
		evt = self.received( expected = tpl, timeout = timeout )
		return evt