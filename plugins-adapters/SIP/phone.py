#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
AdapterUDP = sys.modules['SutAdapters.%s.UDP' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterRTP = sys.modules['SutAdapters.%s.RTP' % TestAdapterLib.getVersion()]

LibraryAuth = sys.modules['SutLibraries.%s.Security' % TestLibraryLib.getVersion()]
LibraryCodecs = sys.modules['SutLibraries.%s.Codecs' % TestLibraryLib.getVersion()]
LibrarySDP = sys.modules['SutLibraries.%s.Media' % TestLibraryLib.getVersion()]


import client as SIP
import templates

__NAME__                         = """SIP PHONE"""

TRANSACTION_STATE_IDLE           = "idle"
TRANSACTION_STATE_TRYING         = "trying"
TRANSACTION_STATE_PROCEEDING     = "proceeding"
TRANSACTION_STATE_CALLING        = "calling"
TRANSACTION_STATE_COMPLETED      = "completed"
TRANSACTION_STATE_CONFIRMED      = "confirmed"
TRANSACTION_STATE_TERMINATED     = "terminated"

AGENT_TYPE_EXPECTED='socket'

class Phone(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, name=None, debug=False, sipSrc=('',0), sipDest=('127.0.0.1', 5060), rtpSrc=('',0),
									prefTransport=AdapterUDP.PROTOCOL_UDP, enableRtp=True, enableTcp=True, enableUdp=True,
									agentSupport=False, agent=None, shared=False):
		"""
		Sip phone simulator. Tries to be RFC compliant. TCP/UDP transport support.
		
		@param parent: testcase 
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param sipSrc: default source ip/port for sip
		@type sipSrc: tuple
		
		@param sipDest: default destination ip/port for sip
		@type sipDest: tuple
		
		@param rtpSrc: default source ip/port for rtp
		@type rtpSrc: string
		
		@param prefTransport: SutAdapters.TCP.PROTOCOL_TCP | SutAdapters.UDP.PROTOCOL_UDP (default)
		@type prefTransport: intconstant
		
		@param enableRtp: activate rtp (default=True)
		@type enableRtp: boolean
		
		@param enableTcp: activate tcp (default=True)
		@type enableTcp: boolean
		
		@param enableUdp: activate udp (default=True)
		@type enableUdp: boolean
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/none

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# check agent
		if agentSupport and agent is None:
			raise Exception('Agent cannot be undefined!')	
		
		if agentSupport:
			if not isinstance(agent, dict):
				raise Exception('Bad value passed on agent!')						
			if not len(agent['name']):
				raise Exception('Agent name cannot be empty!')	
			if unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED):
				raise Exception('Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED)) )	
		
		
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, 
														realname=name, agentSupport=agentSupport, agent=agent)
		if not isinstance(sipSrc, tuple):
			raise Exception('bad type on sip src argument, tuple expected (ip,port)')
		if not isinstance(sipDest, tuple):
				raise Exception('bad type on sip dest argument, tuple expected (ip,port)')
		if not isinstance(rtpSrc, tuple):
				raise Exception('bad type on rtp src argument, tuple expected (ip,port)')
		(bindIp, bindPort) = sipSrc
		(destIp, destPort) = sipDest
		(bindRtpIp, bindRtpPort) = rtpSrc
		self.__testcase = parent
		self.__debugmode = debug
		# sip adapters 
		self.sip_udp =  SIP.Client(parent=parent, bindIp=bindIp, bindPort=bindPort, destIp=destIp, destPort=destPort, proxyHost='', 
																	socketTimeout=10.0, socketFamily=AdapterIP.IPv4, transport=AdapterUDP.PROTOCOL_UDP,
																	sipVersion='SIP/2.0', sipAgent='ExtensiveTesting', sipMaxForwards=70,
																	sipRport=True, sipInitialCseq=0, sipPuid='undefined',
																	sipDomain='', sipDisplayName='', sslSupport=False, sslVersion='TLSv1',
																	checkCert='No', debug=debug, logEventSent=True, logEventReceived=True, 
																	agentSupport=agentSupport, agent=agent, shared=shared, name=name)
		self.sip_tcp =  SIP.Client(parent=parent, bindIp=bindIp, bindPort=bindPort, destIp=destIp, destPort=destPort, proxyHost='', 
																	socketTimeout=10.0, socketFamily=AdapterIP.IPv4, transport=AdapterTCP.PROTOCOL_TCP,
																	sipVersion='SIP/2.0', sipAgent='XTC', sipMaxForwards=70,
																	sipRport=True, sipInitialCseq=0, sipPuid='undefined',
																	sipDomain='', sipDisplayName='', sslSupport=False, sslVersion='TLSv1',
																	checkCert='No', debug=debug, logEventSent=True, logEventReceived=True, 
																	agentSupport=agentSupport, agent=agent, shared=shared, name=name)
		# callback udp and tcp
		self.sip_udp.onIncomingMessage = self.onIncomingMessage	
		self.sip_tcp.onIncomingMessage = self.onIncomingMessage	
		
		# digest library
		self.rfc2617 = LibraryAuth.Digest(parent=parent, debug=debug)
				
		self.cfg = {}	
		# shared mode for adapter
		self.cfg['shared'] = shared
		self.cfg['adapter-name'] = name
		# agent support
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent-name'] = agent['name']		
		self.cfg['agent'] = agent
		# ip level settings
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		self.cfg['bind-rtp-ip'] = bindRtpIp
		self.cfg['bind-rtp-port'] = bindRtpPort
		self.cfg['dest-ip'] = destIp
		self.cfg['dest-port'] = destPort
		# transport
		self.cfg['pref-transport'] = prefTransport
		self.cfg['enable-rtp'] = enableRtp
		self.cfg['enable-udp'] = enableUdp
		self.cfg['enable-tcp'] = enableTcp
		# registration settings
		self.cfg['register-interval'] = 300
		self.cfg['auto-registration-refresh'] = True
		# account settings
		self.cfg['puid'] = 'undefined'
		self.cfg['domain'] = ''
		self.cfg['display-name'] = '' 
		self.cfg['login'] = 'anonymous'
		self.cfg['password'] = ''
		# 
		self.cfg['auto-answer'] = False
		self.cfg['dnd'] = False
		# timers values
		self.cfg['T1'] = 500 # RTT Estimate (default value: 500ms)
		self.cfg['T2'] = 4000 # The default value of T2 is 4s
		self.cfg['T4'] = 5000 # Maximum duration a message will remain in the network
		self.cfg['timer-A'] = self.cfg['T1'] # INVITE request retransmit interval, for UDP only
		self.cfg['timer-B'] = self.cfg['T1'] * 64 # INVITE transaction timeout timer 64*T1 => 32s
		self.cfg['timer-D'] = 32000 # Wait time for response retransmits, UDP only, 32s for UDP, 0s for TCP/SCTP
		self.cfg['timer-E'] = self.cfg['T1'] # non-INVITE request retransmit interval, UDP only
		self.cfg['timer-F'] = self.cfg['T1'] * 64 # non-INVITE transaction timeout timer 64*T1 => 32s
		self.cfg['timer-G'] = self.cfg['T1'] # INVITE response retransmit interval, UDP only
		self.cfg['timer-H'] = self.cfg['T1'] * 64 # Wait time for ACK receipt
		self.cfg['timer-I'] = self.cfg['T4'] # Wait time for ACK retransmits, T4 for UDP, 0s for TCP/SCTP
		self.cfg['timer-J'] = self.cfg['T1'] * 64 # non-INVITE request retransmit interval, 64*T1 for UDP, 0s for TCP/SCTP
		self.cfg['timer-K'] = self.cfg['T4'] # Wait time for response retransmits, T4 for UDP, 0s for TCP/SCTP

		self.started = False
		
		# check the config
		self.__checkConfig()
		
		# manager
		self.clientTransactions = ClientTransactions(phone=self)
		self.serverTransactions = ServerTransactions(phone=self)
		self.registerManager = Registration(phone=self)
		self.sessionsManager = Sessions(phone=self)
		
	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)	
			
	def testcase(self):
		"""
		"""
		return self.__testcase
		
	def debugmode(self):
		"""
		"""
		return self.__debugmode
		
	def configure(self, registerInterval=None, puid=None, domain=None, displayName=None, login=None, password=None,
											autoAnswer=None, dnd=None, T1=None, T2=None, T4=None, timerA=None, timerB=None, timerF=None,
											timerE=None, timerG=None, timerH=None, timerI=None, timerK=None, timerD=None, timerJ=None):
		"""
		Configure settings of the phone.
		
		@param regInterval: setting the expiration interval for the registration (default=300s)
		@type regInterval: integer/none
		
		@param puid: puid name
		@type puid: string/none
		
		@param domain: domain name
		@type domain: string/none
		
		@param displayName: local display name
		@type displayName: string/none
		
		@param login: account login (default=anonymous)
		@type login: string/none
		
		@param password: account password
		@type password: string/none
		
		@param autoAnswer: auto answer activation
		@type autoAnswer: boolean/none
		
		@param dnd: do not disturb activation
		@type dnd: boolean/none
		
		@param T1: timer T1 (default=500ms)
		@type T1: float/none
		
		@param T2: timer T2 (default=4s)
		@type T2: float/none
		
		@param T4: timer T2 (default=5s)
		@type T4: float/none
		
		@param timerA: timer A (default=T1)
		@type timerA: float/none
		
		@param timerB: timer B (default=T1*64)
		@type timerB: float/none
		
		@param timerD: timer D (default=32s)
		@type timerD: float/none
		
		@param timerE: timer E (default=T1)
		@type timerE: float/none
		
		@param timerF: timer F (default=T1*64)
		@type timerF: float/none
		
		@param timerG: timer G (default=T1)
		@type timerG: float/none
		
		@param timerH: timer H (default=T1*64)
		@type timerH: float/none
		
		@param timerI: timer I (default=T4)
		@type timerI: float/none
		
		@param timerJ: timer J (default=T1*64)
		@type timerJ: float/none
		
		@param timerK: timer K (default=T4)
		@type timerK: float/none
		"""
		if registerInterval is not None:
			self.cfg['register-interval'] = int(registerInterval)
		
		if puid is not None:
			self.cfg['puid'] = puid
			self.sip_udp.configure(puid=puid)
			self.sip_tcp.configure(puid=puid)
			
		if domain is not None:
			self.cfg['domain'] = domain
			self.sip_udp.configure(domain=domain)
			self.sip_tcp.configure(domain=domain)
			
		if displayName is not None:
			self.cfg['display-name'] = displayName
			self.sip_udp.configure(displayName=displayName)
			self.sip_tcp.configure(displayName=displayName)
			
		if login is not None:
			self.cfg['login'] = login
			
		if password is not None:
			self.cfg['password'] = password
		
		if autoAnswer is not None:
			self.cfg['auto-answer'] = autoAnswer
			
		if dnd is not None:
			self.cfg['dnd'] = dnd
			
		if T1 is not None:
			self.cfg['T1'] = T1
			
		if T2 is not None:
			self.cfg['T2'] = T2
			
		if T4 is not None:
			self.cfg['T4'] = T4
			
		if timerA is not None:
			self.cfg['timer-A'] = timerA
			
		if timerB is not None:
			self.cfg['timer-B'] = timerB
		
		if timerF is not None:
			self.cfg['timer-F'] = timerF
		
		if timerE is not None:
			self.cfg['timer-E'] = timerE
		
		if timerG is not None:
			self.cfg['timer-G'] = timerG
		
		if timerH is not None:
			self.cfg['timer-H'] = timerH
		
		if timerI is not None:
			self.cfg['timer-I'] = timerI
		
		if timerK is not None:
			self.cfg['timer-K'] = timerK
			
		if timerD is not None:
			self.cfg['timer-D'] = timerD
			
		if timerJ is not None:
			self.cfg['timer-J'] = timerJ
			
	def onIncomingMessage(self, summary, lower):
		"""
		Inspect the message
		"""
		try:
			sip_layer = lower.get('SIP')
			if sip_layer is None:
				self.debug( lower.get() )
				self.error( 'incorrect sip message received' )
			else:
				if sip_layer.get('request') is not None:
					self.onIncomingRequest(request=lower)
				elif sip_layer.get('status') is not None:
					self.onIncomingResponse( response=lower )
				else:
					self.debug( lower.get() )
					self.error( 'incorrect sip message received' )
		except Exception as e:
			self.error( 'internal error on incoming message: %s' % str(e) )
			
	def onIncomingRequest(self, request):
		"""
		Inspect the request and dispatch it
		"""
		try:
			self.debug( 'request received' )
			sip_layer = request.get('SIP')
			sip_hdrs = sip_layer.get('headers')
			sip_request = sip_layer.get('request')
			request_uri = sip_request.get('uri')
			request_method = sip_request.get('method')
			request_version = sip_request.get('version')
			
			valid_request = True
			
			if sip_hdrs is None:
				self.error( 'incorrect sip request received: not sip headers detected' )
				valid_request = False
			if request_uri is None:
				self.error( 'incorrect sip request received: not sip uri detected' )
				valid_request = False	
			if request_method is None:
				self.error( 'incorrect sip request received: not sip method detected' )
				request_method = 'invalid request'
				valid_request = False	
			if request_version is None:
				self.error( 'incorrect sip request received: not sip version detected on %s' % request_method )
				valid_request = False	
			
			# extract mandatory headers:  To, From, CSeq, Call-ID, Max-Forwards, Via
			from_hdr = sip_hdrs.get('from')
			to_hdr = sip_hdrs.get('to')
			cseq_hdr = sip_hdrs.get('cseq')
			callid_hdr = sip_hdrs.get('call-id')
			via_hdr = sip_hdrs.get('via')
			maxforwards_hdr = sip_hdrs.get('max-forwards')
			if from_hdr is None:
				self.error( 'incorrect sip request received: from header is missing on %s' % request_method )
				valid_request = False
			if to_hdr is None:
				self.error( 'incorrect sip request received: to header is missing on %s' % request_method )
				valid_request = False
			if cseq_hdr is None:
				self.error( 'incorrect sip request received: cseq is missing on %s' % request_method )
				valid_request = False
			else:
				try:
					cseq_number, cseq_method = cseq_hdr.split(' ')
				except Exception as e:
					self.error( 'malformed cseq received: %s on %s' % (cseq_hdr, request_method) )
					valid_request = False
			if callid_hdr is None:
				self.error( 'incorrect sip request received: call id is missing on %s' % request_method  )
				valid_request = False
			if via_hdr is None:
				self.error( 'incorrect sip request received: via header is missing on %s' % request_method  )
				valid_request = False
			
			if maxforwards_hdr is None:
				self.warning( 'incorrect sip request received: max forwards header is missing on %s' % request_method )
				valid_request = False
				
			if not valid_request: 
				self.debug( 'invalid request %s received, discard it' % request_method )	
				self.debug( sip_layer.get() )
			else:
				self.debug( 'request is valid' )	
				
			if valid_request:
				did = TransactionDialogID( phone=self )
				did.set(callid=callid_hdr, fromhdr=to_hdr)
				self.debug( 'dialog id received: %s' % did.get() )
				
				tid = TransactionDialogID( phone=self )
				tid.set( cseq=cseq_hdr, callid=callid_hdr, tohdr=to_hdr, fromhdr=from_hdr)
				self.debug( 'transaction id received: %s' % tid.get() )
				
				# search in server transation
				transaction = self.transactions(client=False).find(tid=tid)
				del tid
				if transaction is not None:
					transaction.onIncomingRequest(sip_request=request, sip_headers=sip_hdrs, sip_method=request_method)
				else:	
					# search in session ?
					sess = self.sessionsManager.find(did=did)
					del did
					if sess is None:
						to_hdr = sip_hdrs.get('to')
						if request_method == 'INVITE' and not (';tag=' in to_hdr): # new incoming call
							sessid, sess = self.sessionsManager.add()
							sess.startingIncomingDialog( sip_request=request, sip_headers=sip_hdrs, sip_method=request_method )
						else:
							self.debug( 'unknown dialog request %s received' % request_method )		
							# send 481 Transaction Does Not Exist response 
							tmp_transaction = self.transactions(client=False).add(method=request_method)
							rsp_tpl = self.sip().Status( code='481', phrase='Call/Transaction Does Not Exist', fromHeader=sip_hdrs.get('from'), toHeader=sip_hdrs.get('to'),
																				callId=sip_hdrs.get('call-id'), via=sip_hdrs.get('via'), cseq=sip_hdrs.get('cseq'), send=False)
							tmp_transaction.onIncomingRequest(sip_request=request, sip_headers=sip_hdrs, sip_method=request_method)
							tmp_transaction.sendFinalResponse(sip_response=rsp_tpl)
					else:
						sess.dialog().dispatchRequest( sip_request=request, sip_headers=sip_hdrs, sip_method=request_method )
		except Exception as e:
			self.error( 'internal error on incoming request: %s' % str(e) )
			
	def onIncomingResponse(self, response):
		"""
		Inspect the response and dispatch it
		"""
		try:
			self.debug( 'response received' )
			sip_layer = response.get('SIP')
			sip_hdrs = sip_layer.get('headers')
			sip_status = sip_layer.get('status')
			status_code = sip_status.get('code')
			status_phrase = sip_status.get('phrase')
			status_version = sip_status.get('version')
			
			valid_response = True
			
			if sip_hdrs is None:
				self.error( 'incorrect sip response received: not sip headers detected' )
				valid_response = False
			if status_code is None:
				self.error( 'incorrect sip response received: not sip code detected' )
				valid_response = False	
			if status_phrase is None:
				self.error( 'incorrect sip response received: not sip phrase detected' )
				valid_response = False	
			if status_version is None:
				self.error( 'incorrect sip response received: not sip version detected' )
				valid_response = False	
				
			# extract mandatory headers:  To, From, CSeq, Call-ID, via
			from_hdr = sip_hdrs.get('from')
			to_hdr = sip_hdrs.get('to')
			cseq_hdr = sip_hdrs.get('cseq')
			callid_hdr = sip_hdrs.get('call-id')
			via_hdr = sip_hdrs.get('via')
			if from_hdr is None:
				self.error( 'incorrect sip response received: from header is missing' )
				valid_response = False
			if to_hdr is None:
				self.error( 'incorrect sip response received: to header is missing' )
				valid_response = False
			if cseq_hdr is None:
				self.error( 'incorrect sip response received: cseq is missing' )
				valid_response = False
			else:
				try:
					cseq_number, cseq_method = cseq_hdr.split(' ')
				except Exception as e:
					self.error( 'malformed cseq received: %s' % cseq_hdr )
					valid_response = False
			if callid_hdr is None:
				self.error( 'incorrect sip response received: call id is missing' )
				valid_response = False
			if via_hdr is None:
				self.error( 'incorrect sip response received: via header is missing' )
				valid_response = False
	
				
			if not valid_response:
				self.debug( sip_layer.get() )
			else:
				self.debug( 'response is valid' )	
				
			# dispatch the response if valid
			if valid_response:
				self.debug( 'extract topvia' )	
				# extract topvia and contruct transaction id 
				if isinstance(via_hdr, TestTemplatesLib.TemplateLayer):
					vias = via_hdr.getItems()
					vias.sort()
					k, topvia = vias [0] 
				else:
					topvia = via_hdr
				tid = TransactionDialogID( phone=self )
				tid.set(via=topvia, cseq=cseq_hdr)
				
				self.debug( 'transaction id received: %s' % tid.get() )
				
				transaction = self.transactions().find(tid=tid)
				del tid
				if transaction is None:
					self.warning( 'unknown transaction response %s received' % status_code )
				else:
					# 17.1.3 Matching Responses to Client Transactions
					transaction.dispatchResponse(response=response)
		except Exception as e:
			self.error( 'internal error on incoming response: %s' % str(e) )	
			
	def onReset(self):
		"""
		"""
		self.sip_udp.onReset()
		self.sip_tcp.onReset()
		
	def transactions(self, client=True):
		"""
		"""
		if client:
			return self.clientTransactions
		else:
			return self.serverTransactions
		
	def transport(self):
		"""
		"""
		return self.cfg['pref-transport']
		
	def sip(self):
		"""
		"""
		if self.cfg['pref-transport'] == AdapterTCP.PROTOCOL_TCP:
			return self.sip_tcp
		if self.cfg['pref-transport'] == AdapterUDP.PROTOCOL_UDP:	
			return self.sip_udp
	def getRegistrationState(self):
		"""
		"""
		return self.registerManager.getState()
	def getUri(self):
		"""
		"""
		return "%s@%s" % (self.cfg['puid'], self.cfg['domain'])
		
	def getNewCallId(self):
		"""
		"""
		# todo: add domain
		return SIP.CALLID()
	@doc_public
	def plug(self, timeout=1.0):
		"""
		Starts the phone.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: plug result
		@rtype:	boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if self.started:
			self.debug('already plugged')
			return
	
		plugged = True
		if self.cfg['enable-udp']:
			sip_udp_listening = self.sip_udp.initialize(timeout=timeout)
			if sip_udp_listening is None:
				self.error('Initialize SIP UDP failed')
				plugged = False
		
		if self.cfg['enable-tcp']:
			sip_tcp_listening = self.sip_tcp.initialize(timeout=timeout)
			if sip_tcp_listening is None:
				self.error('Initialize SIP TCP failed')
				plugged = False

		self.started = plugged
		return plugged
	
	@doc_public
	def unplug(self, timeout=1.0, cleanup=True):
		"""
		Stops the phone.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: unplug result
		@rtype:	boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		self.started = False
		
		unplugged = True
		
		if cleanup:
			self.sessionsManager.reset()
			if self.getRegistrationState()== 'registered':
				self.unregister()
				if not self.isUnregistered(timeout=timeout):
					self.error('SIP unregistration failed')
					unplugged = False
			
			self.transactions(client=False).reset()
			self.transactions(client=True).reset()
			
		if self.cfg['enable-udp']:
			sip_udp = self.sip_udp.finalize( timeout=timeout )		
			if sip_udp is None:
				self.error('Finalize SIP UDP failed')
				unplugged = False
		
		if self.cfg['enable-tcp']:
			sip_tcp = self.sip_tcp.finalize( timeout=timeout )		
			if sip_tcp is None:
				self.error('Finalize SIP TCP failed')
				unplugged = False
		
		return unplugged
			
	@doc_public
	def register(self, headers={}):
		"""
		Register the phone with a proxy (automatic refresh).
		
		@param headers: additional headers or overwrites existing in the REGISTER request
		@type headers: dict
		"""
		if not self.started:
			self.debug('not plugged')
			return
			
		if self.registerManager.getState() != 'not-registered':
			self.warning('already registered or in progress')
		else:
			tpl = templates.registration(expire=self.cfg['register-interval'], login=self.cfg['login'], password=self.cfg['password']) 
			self.logSentEvent( shortEvt = 'registration', tplEvt = tpl ) 
			self.registerManager.sendRegister(state='registering', expire=self.cfg['register-interval'], headers=headers)
	
	@doc_public
	def unregister(self, headers={}):
		"""
		Unregister the phone.
		
		@param headers: additional headers or overwrites existing in the REGISTER request
		@type headers: dict
		"""
		if not self.started:
			self.debug('not plugged')
			return
			
		if self.registerManager.getState() == 'not-registered':
			pass
		elif self.registerManager.getState() == 'registering' or self.registerManager.getState() == 'refreshing':	
			self.warning('already unregistered or in progress')
		else:
			self.logSentEvent( shortEvt = 'unregistration', tplEvt = templates.unregistration() ) 
			self.registerManager.sendRegister(state='unregistering', expire=0, headers=headers)
			
	@doc_public
	def placeCall(self, uri, recordCall=False, playSound=AdapterRTP.SOUND_SINE_1K, codecSound=LibraryCodecs.A_G711U, headers={}):
		"""
		Place a new call.
		
		@param uri: uri to call
		@type uri: string
		
		@param recordCall: record the call (default=False)
		@type recordCall: boolean
		
		@param playSound: SutAdapters.RTP.SOUND_SINE_1K (default) | SutAdapters.RTP.SOUND_WHITE_NOISE | SutAdapters.RTP.SOUND_SILENCE
		@type playSound: integer
		
		@param codecSound: prefered codec to use: SutLibraries.Codecs.A_G711U (default) | SutLibraries.Codecs.A_G711A
		@type codecSound: integer	
		
		@param headers: additional headers or overwrites existing in the INVITE request
		@type headers: dict
		
		@return: session identifier
		@rtype:	integer
		"""
		if isinstance(uri, Phone):
			destAddr = uri.getUri()
		else:
			destAddr = uri
		sessid, sess = self.sessionsManager.add()
		# create the call
		sess.startingOutgoingDialog(destAddr=destAddr, recordSesssion=recordCall, playSound=playSound, codecSound=codecSound, headers=headers)
		# return session session-id
		return sessid
			
	@doc_public
	def hangupCall(self, sessionid, headers={}):
		"""
		Hangup the call.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param headers: additional headers or overwrites existing in the BYE or CANCEL request
		@type headers: dict
		"""
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'hangup: session id %s not found' % sessionid )
		else:
			if sess.getSipState() == 'connected':
				sess.stoppingDialog(headers=headers)
			elif sess.getSipState() in [ 'waiting-provisional-response', 'waiting-success-response' ]:
				sess.cancellingDialog(headers=headers)
			else:
				self.debug( 'hangup is not yet supported in the state %s' % sess.getSipState() )
	@doc_public
	def answerCall(self, sessionid, recordCall=False, playSound=AdapterRTP.SOUND_SINE_1K, headers={}):
		"""
		Answer to the call.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param playSound: SutAdapters.RTP.SOUND_SINE_1K (default) | SutAdapters.RTP.SOUND_WHITE_NOISE | SutAdapters.RTP.SOUND_SILENCE
		@type playSound: integer

		@param recordCall: record the call
		@type recordCall: boolean
		
		@param headers: additional headers or overwrites existing in 200OK
		@type headers: dict
		"""
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'answer: session id %s not found' % sessionid )
		else:
			if sess.getSipState() == 'ringing':
				sess.acceptingDialog(recordSesssion=recordCall, playSound=playSound, headers=headers )
			else:
				self.debug( 'answer is not yet supported in the state %s' % sess.getSipState() )
				
	@doc_public
	def rejectCall(self, sessionid, code='603', phrase='Decline', headers={}):
		"""
		Reject to the call.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param code: response code (default=603)
		@type code: string/operators/none	
		
		@param phrase: response phrase (default=Decline)
		@type phrase: string/operators/none	
		
		@param headers: additional headers or overwrites existing in 300-699 reponse
		@type headers: dict
		"""
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'reject: session id %s not found' % sessionid )
		else:
			if sess.getSipState() == 'ringing':
				sess.rejectingDialog(code=code, phrase=phrase, headers=headers)
			else:
				self.debug( 'reject is not yet supported in the state %s' % sess.getSipState() )
				
	@doc_public
	def isRegistered(self, timeout=1.0, interval=None):
		"""
		Wait registered event until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param interval: expire value
		@type interval: string/operators/none	
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.registered(expire=interval)
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	
	@doc_public
	def isUnregistered(self, timeout=1.0):
		"""
		Wait unregistered event until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.unregistered()
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	
	@doc_public
	def isRinging(self, timeout=1.0):
		"""
		Wait ringing event until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: session identifier
		@rtype:	integer/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.ringing()
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		else:
			layer_phone = evt.get('SIP-PHONE')
			return layer_phone.get('session-id')
	@doc_public
	def hasReceivedCall(self, timeout=1.0, cli=None, display=None, diversion=None, assertedIdentity=None):
		"""
		Wait incoming call event until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param cli: call line identifier
		@type cli: string/operators/none	
		
		@param display: display name
		@type display: string/operators/none	
		
		@param diversion: diversion
		@type diversion: string/operators/none	
		
		@param assertedIdentity: asserted identity
		@type assertedIdentity: string/operators/none	
		
		@return: session identifier
		@rtype:	integer/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.incomingcall(cli=cli, display=display, diversion=diversion, assertedidentity=assertedIdentity)	
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		else:
			layer_phone = evt.get('SIP-PHONE')
			return layer_phone.get('session-id')

	@doc_public
	def isReceivingAudio(self, sessionid, timeout=1.0, codec=None):
		"""
		Wait receiving audio event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param codec: audio codec expected
		@type codec: string/operators/none	
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'isreceivingaudio: session id %s not found' % sessionid )
			return None
		else:
			return sess.isReceivingAudio(timeout=timeout, codec=codec)
			
	@doc_public
	def isNoLongerReceivingAudio(self, sessionid, timeout=1.0, codec=None):
		"""
		Wait stop receiving audio event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param codec: audio codec expected
		@type codec: string/operators/none	
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'isnolongerreceivingaudio: session id %s not found' % sessionid )
			return None
		else:
			return sess.isNoLongerReceivingAudio(timeout=timeout, codec=codec)
		
	@doc_public
	def ringbackToneReceived(self, sessionid, timeout=1.0):
		"""
		Wait ringbacktone event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'ringbacktonereceived: session id %s not found' % sessionid )
			return None
		else:
			expected = templates.ringback_tone(sessid=sessionid)	
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				return None
			return evt
		
	@doc_public
	def hasReceivedError(self, timeout=1.0, sessionid=None, code=None, phrase=None):
		"""
		Wait unexpected response event until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param sessionid: session identifier
		@type sessionid: integer/operators/none
		
		@param code: response code (default=603)
		@type code: string/operators/none	
		
		@param phrase: response phrase (default=Decline)
		@type phrase: string/operators/none	
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.unexpected_response(sessid=sessionid, code=code, phrase=phrase)	
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt

	@doc_public
	def isConnected(self, sessionid, timeout=1.0 ):
		"""
		Wait connected event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'isconnected: session id %s not found' % sessionid )
			return None
		else:
			expected = templates.call_connected(sessid=sessionid)
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				return None
			return evt
	
	@doc_public
	def isDisconnected(self, sessionid, timeout=1.0, reason=None, originator=None):
		"""
		Wait disconnected event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param reason: disconnection reason
		@type reason: string/operators/none	
		
		@param originator: originator of the disconnection
		@type originator: string/operators/none	
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'isdisconnected: session id %s not found' % sessionid )
			return None
		else:
			expected = templates.call_disconnected(sessid=sessionid, reason=reason, by=originator)
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				return None
			return evt
			
	@doc_public
	def isCancelled(self, sessionid, timeout=1.0 ):
		"""
		Wait cancelled event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'iscancelled: session id %s not found' % sessionid )
			return None
		else:
			expected = templates.call_cancelled(sessid=sessionid)
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				return None
			return evt
	@doc_public
	def isRejected(self, sessionid, timeout=1.0 ):
		"""
		Wait rejected event until the end of the timeout.
		
		@param sessionid: session identifier
		@type sessionid: integer
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@return: sip phone event
		@rtype:	templatemessage/none
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		sess = self.sessionsManager.get(id=sessionid)
		if sess is None:
			self.error( 'isrejected: session id %s not found' % sessionid )
			return None
		else:
			expected = templates.call_rejected(sessid=sessionid)
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				return None
			return evt
# Internal Logger
class CommonLogger(object):
	def __init__(self, phone, name):
		"""
		"""
		self.__phone = phone
		self.__loggername = name
		# wrappers
		self.sip = self.__phone.sip
		
	def phone(self):
		"""
		"""
		return self.__phone	
		
	def debug(self, msg):
		"""
		"""
		full_msg = '%s: %s' % ( self.__loggername, msg )
		self.phone().debug(full_msg)
		
	def info(self, info):
		"""
		"""
		full_info = '%s: %s' % ( self.__loggername, info )
		self.phone().info(full_info)
		
	def error(self, err):
		"""
		"""
		full_err = '%s: %s' % ( self.__loggername, err )
		self.phone().error(full_err)	
		
	def warning(self, warm):
		"""
		"""
		full_warm = '%s: %s' % ( self.__loggername, warm )
		self.phone().warning(full_warm)		

#	Handle Transactions
class ClientTransactions(CommonLogger):
	def __init__(self, phone):
		"""
		"""
		CommonLogger.__init__(self, phone=phone, name='CLIENT_TRANSACTIONS')
		self.__tids = []
		self.__id = 0

	def add(self, method):
		"""
		"""
		self.debug( 'adding transaction')
		self.__id += 1
		if method == 'INVITE':
			transaction = InviteClientTransaction(phone=self.phone(), requestName=method, tid=self.__id )
		else:	
			transaction = NonInviteClientTransaction(phone=self.phone(), requestName=method, tid=self.__id )
			
		self.__tids.append( transaction )
		return transaction
		
	def remove(self, transaction):
		"""
		"""
		self.debug( 'removing transaction %s' % transaction.tid() )
		try:
			self.__tids.remove(transaction)
		except Exception as e:
			self.error('transaction not found')
		self.debug( 'transaction removed %s'  % transaction.tid())
		
	def find(self, tid):
		"""
		"""
		ret = None
		for transaction in self.__tids:
			if transaction.recognizeTransaction(tid):
				ret = transaction
				break
		return ret
	def reset(self):
		"""
		"""
		for tr in self.__tids:
			tr.resetTransaction()
class ServerTransactions(CommonLogger):
	def __init__(self, phone):
		"""
		"""
		CommonLogger.__init__(self, phone=phone, name='SERVER_TRANSACTIONS')
		self.__tids = []
		self.__id = 0
		
	def add(self, method):
		"""
		"""
		self.debug( 'adding transaction')
		self.__id += 1
		if method == 'INVITE':
			transaction = InviteServerTransaction(phone=self.phone(), requestName=method, tid=self.__id )
		else:	
			transaction = NonInviteServerTransaction(phone=self.phone(), requestName=method, tid=self.__id )
			
		self.__tids.append( transaction )
		return transaction
	def remove(self, transaction):
		"""
		"""
		self.debug( 'removing transaction %s' % transaction.tid() )
		try:
			self.__tids.remove(transaction)
		except Exception as e:
			self.error('transaction not found')
		self.debug( 'transaction removed %s'  % transaction.tid())
	def find(self, tid):
		"""
		"""
		ret = None
		for transaction in self.__tids:
			if transaction.recognizeTransaction(tid):
				ret = transaction
				break
		return ret
	def reset(self):
		"""
		"""
		for tr in self.__tids:
			tr.resetTransaction()
class Transaction(CommonLogger):
	def __init__(self, phone, name, id):
		"""
		Transaction Logger
		"""
		CommonLogger.__init__(self, phone=phone, name=name)
		self.__phone = phone
		self.__tid = id
		self.__requestName = name.upper()
	def tid(self):
		"""
		"""
		return self.__tid	

	def phone(self):
		"""
		"""
		return self.__phone	
		
	def debug(self, msg):
		"""
		"""
		full_msg = '%s (tid %s): %s' % ( self.__requestName, self.__tid, msg )
		self.__phone.debug(full_msg)
		
	def info(self, info):
		"""
		"""
		full_info = '%s (tid %s): %s' % ( self.__requestName, self.__tid, info )
		self.__phone.info(full_info)	
	def error(self, err):
		"""
		"""
		full_err = '%s (tid %s): %s' % ( self.__requestName, self.__tid, err )
		self.__phone.error(full_err)	
		
	def warning(self, warm):
		"""
		"""
		full_warm = '%s (tid %s): %s' % ( self.__requestName, self.__tid, warm )
		self.__phone.warning(full_warm)
	
class TransactionDialogID(CommonLogger):
	def __init__(self, phone):
		"""
		Internal ID
		"""
		CommonLogger.__init__(self, phone=phone, name='TID')
		self.__id = []	# cseq number, cseq method, branch from top via, tag to, tag from, callid
		self.__size = 0
	def getBranchInVia(self, viaHeader):
		"""
		"""
		try:
			if ';branch=' in viaHeader:
				tmp = viaHeader.split(';branch=')
				return tmp[1].split(';')[0]
			else:
				return ''	
		except Exception as e:
			self.error('unable to extract the branch: %s' % str(e) )
			return None
		
	def getTagInFrom(self, fromHeader):
		"""
		"""
		try:
			if ';tag=' in fromHeader:
				tmp = fromHeader.split(';tag=')
				return tmp[1].split(';')[0]
			else:
				return ''
		except Exception as e:
			self.error('unable to extract the tag in from: %s' % str(e) )
			return None
			
	def getTagInTo(self, toHeader):
		"""
		"""
		try:
			if ';tag=' in toHeader:
				tmp = toHeader.split(';tag=')
				return tmp[1].split(';')[0]
			else:
				return ''
		except Exception as e:
			self.error('unable to extract the tag in to: %s' % str(e) )
			return None
			
	def set(self, via='', cseq='', tohdr='', fromhdr='', callid=''):
		"""
		"""
		try:
			self.__id = []
			if ' ' in cseq:
				cseq_num, cseq_meth = cseq.split(' ')
				if cseq_meth == 'ACK':
					cseq_meth = 'INVITE'
			else:
				cseq_num = ''
				cseq_meth = ''
			self.__id.append( cseq_num )
			self.__id.append( cseq_meth )
			if len(cseq):
				self.__size += 2
			
			branch = self.getBranchInVia(via)
			if branch is None:
				branch = ''
			self.__id.append( branch )
			if len(branch):
				self.__size += 1
			
			tagto = self.getTagInTo(tohdr)
			if tagto is None:
				tagto = ''
			self.__id.append( tagto )
			if len(tagto):
				self.__size += 1
			
			tagfrom = self.getTagInFrom(fromhdr) 
			if tagfrom is None:
				tagfrom = ''
			self.__id.append( tagfrom )
			if len(tagfrom):
				self.__size += 1
				
			self.__id.append( callid )
			if len(callid):
				self.__size += 1
		except Exception as e:
			self.error('unable to set tid: %s' % str(e) )
			
	def getSize(self):
		"""
		"""
		return self.__size
		
	def get(self):
		"""
		"""
		return self.__id
		
#17.2.1 INVITE Server Transaction
class InviteServerTransaction(Transaction):
	def __init__(self, phone, requestName, tid):
		"""
		"""
		Transaction.__init__(self, phone=phone, name=requestName, id=tid)
		self.__tid_sip = TransactionDialogID(phone=phone) # unique transaction identifier
		# state
		self.__transactionState = TestAdapterLib.State(parent=phone, name='SERVER_TRANSACTION', initial=TRANSACTION_STATE_IDLE)
		# timers 
		self.__timerG_value = phone.cfg['timer-G']
		self.__timerG = TestAdapterLib.Timer(parent=phone, duration=float(self.__timerG_value) / 1000,
																			name='Timer G: INVITE response retransmit interval', callback=self.__onFiredTimerG)
		self.__timerH = TestAdapterLib.Timer(parent=phone, duration=float(phone.cfg['timer-H']) / 1000,
																			name='Timer H: Wait time for ACK receipt', callback=self.__onFiredTimerH)
		self.__timerI = TestAdapterLib.Timer(parent=phone, duration=float(phone.cfg['timer-I']) / 1000,
																			name='Timer I: Wait time for ACK retransmits', callback=self.__setTerminatedState)
		# variables
		self.req = None
		self.final_rsp  = None # last final response sent
		self.prov_rsp  = None  # last provisional response sent
	def resetTransaction(self):
		"""
		"""
		self.__setState(state='idle')
		# reset timers
		self.__timerG.stop()
		elf.__timerH.stop()
		elf.__timerI.stop()
	def __getState(self):
		"""
		"""
		return self.__transactionState.get()
		
	def __setState(self, state):
		"""
		"""
		self.__transactionState.set(state)
		
	def __setProceedingState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_PROCEEDING)
	
	def __setCompletedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_COMPLETED)
		self.__timerH.start()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerG.start()
			
	def __setConfirmedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_CONFIRMED)		
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerG.stop()
			self.__timerI.setDuration(duration=float(self.phone().cfg['timer-I']) / 1000)
			self.__timerI.start()
		else:
			self.__timerI.setDuration(duration=float(0))
			self.__timerI.start()
		
	def __setTerminatedState(self):		
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_TERMINATED)
		self.phone().transactions(client=False).remove(self)
		
	def __onFiredTimerG(self):
		"""
		Timer G fired
		"""
		if self.__getState() in [ 'completed' ]:
			# retransmission 
			self.__sendResponse(sip_response=self.final_rsp)
			# reset timer G and rearm
			# exponentially increasing interval
			self.__timerG_value *= 2
			timerE = min( self.__timerG_value, self.phone().cfg['T2'] )
			self.__timerG.setDuration( float(timerG) / 1000 )
			self.__timerG.start()
			
	def __onFiredTimerH(self):
		"""
		Timer H fired, it implies that the ACK was never received
		"""
		if self.__getState() in [ 'completed' ]:		
			self.__setTerminatedState()
			self.onTransactionTimeout()
			
	def onTransactionTimeout(self):
		"""
		success response to resend
		"""
		pass

	def __savetid(self, cseq, callid, fromhdr, tohdr):
		"""
		"""
		self.debug( 'save transaction id' )
		self.__tid_sip.set(cseq=cseq, callid=callid, fromhdr=fromhdr, tohdr=tohdr)
		self.debug( "sip id: %s" % self.__tid_sip.get() )	
		
	def updatetid(self, cseq, callid, fromhdr, tohdr):
		"""
		"""
		self.debug( 'update transaction id' )
		self.__savetid( cseq=cseq, callid=callid,tohdr=tohdr, fromhdr=fromhdr	)

	def recognizeTransaction(self, tid):
		"""
		Check if the request is for me
		"""
		try:
			# verify
			recognized = True
			nb = 0

			a, b, c, d, e, f =  tid.get()
			la, lb, lc, ld, le, lf = 	self.__tid_sip.get()
				
			if len(a):
				nb += 1
				if a != la: recognized=False
			if len(b): 
				nb += 1
				if b != lb: recognized=False		
			if len(c): 
				nb += 1
				if c != lc: recognized=False	
			if len(d): 
				nb += 1
				if d != ld: recognized=False	
			if len(e): 
				nb += 1
				if e != le: recognized=False	
			if len(f): 
				nb += 1
				if f != lf: recognized=False	
			
			if nb != tid.getSize():
				recognized=False
			
			self.debug( 'Matching Server Transaction %s: %s' % (self.__tid_sip.get(), recognized) )	
		except Exception as e:
			self.error( 'internal error on recognize invite server transaction: %s' % str(e) )
		return recognized
	def getRequest(self):
		"""
		"""
		sip_layer = self.req.get('SIP')
		sip_headers = sip_layer.get('headers')
		return sip_layer, sip_headers 
		
	def onIncomingRequest(self, sip_request, sip_headers, sip_method):
		"""
		"""
		if sip_method == 'INVITE':
			if self.__getState() in [ 'idle' ]:
				# initialize the transaction with the request
				self.req = sip_request
				self.__savetid( cseq=sip_headers.get('cseq'), callid=sip_headers.get('call-id'), 
															tohdr=sip_headers.get('to'), fromhdr=sip_headers.get('from')	)
				self.__setProceedingState()
			elif self.__getState() in [ 'proceeding' ]:
				self.onRetransmissionDetected(sip_method)
				# retransmission of the most recently sent provisional response
				if self.prov_rsp is not None:
					self.__sendResponse( sip_response=self.prov_rsp )
			else:
				self.debug( '%s received in state %s' % (sip_method, self.__getState()) )
		elif sip_method == 'ACK':
			if self.__getState() in [ 'completed' ]:
				self.__setConfirmedState()
				self.onAck(sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method)
			elif self.__getState() in [ 'confirmed' ]:
				# absorb any additional ACK messages
				self.onRetransmissionDetected(sip_method)
			else:
				self.debug( '%s received in state %s' % (sip_method, self.__getState()) )
		else:
			self.error('incorrect method %s for a server transaction' % sip_method)
			
	def onRetransmissionDetected(self, sip_method):
		"""
		"""
		self.warning( '%s retransmission detected' % sip_method)
			
	def onAck(self, sip_request, sip_headers, sip_method):
		"""
		"""
		pass
	def __sendResponse(self, sip_response):
		"""
		"""
		# send response
		self.sip().sendMessage(tpl=sip_response)	
	
	def sendFinalResponse(self, sip_response):
		"""
		Send a final response (status codes 300 to 699)
		"""
		if self.__getState() in [ 'proceeding' ]:		
			self.final_rsp = sip_response
			self.__sendResponse( sip_response=sip_response )
			self.__setCompletedState()
			
			
	def sendSuccessResponse(self, sip_response):
		"""
		Send a final response (status codes 2xx)
		"""
		if self.__getState() in [ 'proceeding' ]:		
			self.final_rsp = sip_response
			self.__sendResponse( sip_response=sip_response )
			self.__setCompletedState()
			
			
	def sendProvisionalResponse(self, sip_response):
		"""
		Send a provisional response (status codes 101-199)
		"""
		if self.__getState() in [ 'proceeding' ]:
			self.prov_rsp = sip_response
			self.__sendResponse( sip_response=sip_response )
		
#17.2.2 Non-INVITE Server Transaction
class NonInviteServerTransaction(Transaction):
	def __init__(self, phone, requestName, tid):
		"""
		"""
		Transaction.__init__(self, phone=phone, name=requestName, id=tid)
		self.__tid_sip = TransactionDialogID(phone=phone) # unique transaction identifier
		# state
		self.__transactionState = TestAdapterLib.State(parent=phone, name='SERVER_TRANSACTION', initial=TRANSACTION_STATE_IDLE)
		# timers 
		self.__timerJ_value = phone.cfg['timer-J']
		self.__timerJ = TestAdapterLib.Timer(parent=phone, duration=float(self.__timerJ_value) / 1000,
																			name='Timer J: non-INVITE request retransmit interval, 64*T1 for UDP, 0s for TCP/SCTP',
																			callback=self.__setTerminatedState)
		# variables
		self.req = None
		self.final_rsp  = None # last final response sent
		self.prov_rsp  = None  # last provisional response sent
	def resetTransaction(self):
		"""
		"""
		self.__setState(state='idle')
		# reset timers
		self.__timerJ.stop()
	
	def __getState(self):
		"""
		"""
		return self.__transactionState.get()
		
	def __setState(self, state):
		"""
		"""
		self.__transactionState.set(state)
	def __setTryingState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_TRYING)
		
	def __setProceedingState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_PROCEEDING)
		
	def __setCompletedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_COMPLETED)
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerJ.setDuration(duration=float(self.__timerJ_value) / 1000)
			self.__timerJ.start()
		else:
			self.__timerJ.setDuration(duration=float(0))
			self.__timerJ.start()	
			
	def __setTerminatedState(self):		
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_TERMINATED)
		self.phone().transactions(client=False).remove(self)
		
	def __savetid(self, cseq, callid, fromhdr, tohdr):
		"""
		"""
		self.__tid_sip.set(cseq=cseq, callid=callid, fromhdr=fromhdr, tohdr=tohdr)
		self.debug( "sip id: %s" % self.__tid_sip.get() )	
	def recognizeTransaction(self, tid):
		"""
		Check if the request is for me
		"""
		try:
			# verify
			recognized = True
			nb = 0
			a, b, c, d, e, f =  tid.get()
			la, lb, lc, ld, le, lf = 	self.__tid_sip.get()
			
			if len(a):
				nb += 1
				if a != la: recognized=False
			if len(b): 
				nb += 1
				if b != lb: recognized=False		
			if len(c): 
				nb += 1
				if c != lc: recognized=False	
			if len(d): 
				nb += 1
				if d != ld: recognized=False	
			if len(e): 
				nb += 1
				if e != le: recognized=False	
			if len(f): 
				nb += 1
				if f != lf: recognized=False	
			
			if nb != tid.getSize():
				recognized=False
			
			self.debug( 'Matching Server Transaction %s: %s' % (self.__tid_sip.get(), recognized) )	
		except Exception as e:
			self.error( 'internal error on recognize non invite server transaction: %s' % str(e) )
		return recognized
	def getRequest(self):
		"""
		"""
		sip_layer = self.req.get('SIP')
		sip_headers = sip_layer.get('headers')
		return sip_layer, sip_headers 
	def onIncomingRequest(self, sip_request, sip_headers, sip_method):
		"""
		"""
		if self.__getState() in [ 'idle' ]:
			# initialize the transaction with the request
			self.req = sip_request
			self.__savetid( cseq=sip_headers.get('cseq'), callid=sip_headers.get('call-id'), 
														tohdr=sip_headers.get('to'), fromhdr=sip_headers.get('from')	)
			self.__setTryingState()
		elif self.__getState() in [ 'trying' ]:
			# Once in the "Trying" state, any further request retransmissions are discarded.
			self.onRetransmissionDetected()
		elif self.__getState() in [ 'proceeding' ]:
			self.onRetransmissionDetected()
			# retransmission of the most recently sent provisional response
			self.__sendResponse( sip_response=self.prov_rsp )
		elif self.__getState() in [ 'completed' ]:
			self.onRetransmissionDetected()
			# retransmission of the final response
			self.__sendResponse( sip_response=self.final_rsp )
		else:
			self.error( 'should not happened')
			
	def onRetransmissionDetected(self):
		"""
		"""
		self.warning( 'retransmission detected, request discarded' )						

	def sendProvisionalResponse(self, sip_response):
		"""
		"""
		if self.__getState() in [ 'trying' ]:
			self.prov_rsp = sip_response
			self.__setProceedingState()
			self.__sendResponse( sip_response=sip_response )
			
	def sendSuccessResponse(self, sip_response):
		"""
		Send a final response (status codes 2xx)
		"""
		self.sendFinalResponse(sip_response=sip_response)
		
	def sendFinalResponse(self, sip_response):
		"""
		Send a final response (status codes 300 to 699)
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:		
			self.final_rsp = sip_response
			self.__setCompletedState()
			self.__sendResponse( sip_response=sip_response )
			
	def __sendResponse(self, sip_response):
		"""
		"""
		# send response
		self.sip().sendMessage(tpl=sip_response)
		
#17.1.1 INVITE Client Transaction
class InviteClientTransaction(Transaction):
	def __init__(self, phone, requestName, tid):
		"""
		"""
		Transaction.__init__(self, phone=phone, name=requestName, id=tid)
		self.__tid_sip = TransactionDialogID(phone=phone) # unique transaction identifier
		# state
		self.__transactionState = TestAdapterLib.State(parent=phone, name='CLIENT_TRANSACTION', initial=TRANSACTION_STATE_IDLE)
		# timers 
		self.__timerB = TestAdapterLib.Timer(parent=phone, duration=float(phone.cfg['timer-B']) / 1000,
																			name='Timer B: INVITE transaction timeout timer', callback=self.__onTransactionTimeout)
		self.__timerA_value = phone.cfg['timer-A']
		self.__timerA = TestAdapterLib.Timer(parent=phone, duration=float(self.__timerA_value) / 1000,
																			name='Timer A: INVITE request retransmit interval, for UDP only', callback=self.__onRetransmissionTimeout)
		self.__timerD = TestAdapterLib.Timer(parent=phone, duration=float(phone.cfg['timer-D']) / 1000,
																			name='Timer D: Wait time for response retransmits, 32s for UDP, 0s for TCP/SCTP', callback=self.__setTerminatedState)
		# variables
		self.req  = None # contains the last request sent

	def __getState(self):
		"""
		"""
		return self.__transactionState.get()
		
	def __setState(self, state):
		"""
		"""
		self.__transactionState.set(state)
		
	def __setCompletedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_COMPLETED)
		self.__timerB.stop()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerA.stop()
			self.__timerD.setDuration(duration=float(self.phone().cfg['timer-D']) / 1000)
			self.__timerD.start()
		else:
			self.__timerD.setDuration(duration=float(0))
			self.__timerD.start()
			
	def __setProceedingState(self):
		"""
		"""
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerA.stop()
		self.__setState(state=TRANSACTION_STATE_PROCEEDING)
		
	def __setTerminatedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_TERMINATED)
		self.phone().transactions().remove(self)
	
	def __setCallingState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_CALLING)

	def saveTransactionId(self, via, cseq, callid, fromhdr):
		"""
		"""
		self.__tid_sip.set(via=via, cseq=cseq, callid=callid, fromhdr=fromhdr)
		self.debug( "sip id: %s" % self.__tid_sip.get() )

	def resetTransaction(self):
		"""
		"""
		self.__setState(state='idle')
		# reset timers
		self.__timerB.stop()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerA.stop()
			self.__timerD.stop()

	def recognizeTransaction(self, tid):
		"""
		Check if the response is for me
		"""
		try:
			# verify
			recognized = True
			nb = 0
			a, b, c, d, e, f =  tid.get()
			la, lb, lc, ld, le, lf = 	self.__tid_sip.get()
			
			if len(a):
				nb += 1
				if a != la: recognized=False
			if len(b): 
				nb += 1
				if b != lb: recognized=False		
			if len(c): 
				nb += 1
				if c != lc: recognized=False	
			if len(d): 
				nb += 1
				if d != ld: recognized=False	
			if len(e): 
				nb += 1
				if e != le: recognized=False	
			if len(f): 
				nb += 1
				if f != lf: recognized=False	
			
			if nb != tid.getSize():
				recognized=False
				
			self.debug( 'Matching Client Transaction %s: %s' % (self.__tid_sip.get(), recognized) )	
		except Exception as e:
			self.error( 'internal error on recognize invite client transaction: %s' % str(e) )
		return recognized
		
	def dispatchResponse(self, response):
		"""
		Valid response, dispatch it
		"""
		sip_layer = response.get('SIP')
		sip_status = sip_layer.get('status')
		status_code = sip_status.get('code')
		status_phrase = sip_status.get('phrase')
		sip_hdrs = sip_layer.get('headers')

		if status_code.startswith('1') :
			self.__onResponse1xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('2') :
			self.__onResponse2xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('3') :
			self.__onResponse3xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('4') :
			self.__onResponse4xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('5') :
			self.__onResponse5xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('6') :
			self.__onResponse6xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		else:
			self.debug( response )
			self.error( 'status code received unknown: %s %s' %  (status_code, status_phrase) )
				
	def sendRequest(self, sip_request):
		"""
		"""
		# extract top via and save transactin id
		sip_headers = sip_request.get('headers')
		via = sip_headers.get('via')
		if isinstance(via, TestTemplatesLib.TemplateLayer):
			vias = via.getItems()
			vias.sort()
			k, topvia = vias [0] 
		else:
			topvia = via
		self.saveTransactionId( via=topvia, cseq=sip_headers.get('cseq'), callid=sip_headers.get('call-id'),
														fromhdr=sip_headers.get('from')	)

		# send request
		self.__sendRequest(sip_request=sip_request)
		
		# start timers
		self.__timerB.start()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerA.setDuration( float(self.__timerA_value) / 1000 )
			self.__timerA.start()
			
		# set state
		self.__setCallingState()
		
	def __sendRequest(self, sip_request):
		"""
		"""
		# send request
		self.req = sip_request
		self.sip().sendMessage(tpl=sip_request)
					
	def __onTransactionTimeout(self):
		"""
		Timer B fired
		"""
		if self.__getState() in [ 'calling', 'proceeding' ]:
			self.__timerA.stop()
			self.__setTerminatedState()
			self.onTransactionTimeout()

	def __onRetransmissionTimeout(self):
		"""
		Timer A fired
		"""
		if self.__getState() in [ 'calling' ]:
			# retransmission 
			self.__sendRequest(sip_request=self.req)
			# reset timer A and rearm
			self.__timerA_value *= 2
			self.__timerA.setDuration( float(timerA) / 1000 )
			self.__timerA.start()
		
	def __onResponse1xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'calling' ]:
			self.__setProceedingState()
		if self.__getState() in [ 'calling', 'proceeding' ]:
			self.onResponse1xx(sip_response, sip_headers, sip_code, sip_phrase)

	def __onResponse2xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'calling', 'proceeding' ]:
			if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
				self.__timerA.stop()
			self.__timerB.stop()
			self.__setTerminatedState()
			self.onResponse2xx(sip_response, sip_headers, sip_code, sip_phrase)
			
	def __onResponse3xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'calling', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse3xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse4xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'calling', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse4xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse5xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'calling', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse5xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse6xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'calling', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse6xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	
	def onRetranmissionDetected(self):
		"""
		"""
		self.warning( 'final response retransmission detected, response discarded' )	
		
	def onTransactionTimeout(self):
		"""
		"""
		pass
		
	def onResponse1xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('1xx not yet implemented')

	def onResponse2xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('2xx not yet implemented')
				
	def onResponse3xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('3xx not yet implemented')

	def onResponse4xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('4xx not yet implemented')
		
	def onResponse5xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('5xx not yet implemented')

	def onResponse6xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('6xx not yet implemented')
# 17.1.2 Non-INVITE Client Transaction	
class NonInviteClientTransaction(Transaction):
	def __init__(self, phone, requestName, tid):
		"""
		"""
		Transaction.__init__(self, phone=phone, name=requestName, id=tid)
		self.__tid_sip = TransactionDialogID(phone=phone) # unique transaction identifier
		# state
		self.__transactionState = TestAdapterLib.State(parent=phone, name='CLIENT_TRANSACTION', initial=TRANSACTION_STATE_IDLE)
		# timers 
		self.__timerF = TestAdapterLib.Timer(parent=phone, duration=float(phone.cfg['timer-F']) / 1000,
																			name='Timer F: non-INVITE transaction timeout timer', callback=self.__onTransactionTimeout)
		self.__timerE_value = phone.cfg['timer-E']
		self.__timerE = TestAdapterLib.Timer(parent=phone, duration=float(self.__timerE_value) / 1000,
																			name='Timer E: non-INVITE request retransmit interval, UDP only', callback=self.__onRetransmissionTimeout)
		self.__timerK = TestAdapterLib.Timer(parent=phone, duration=float(phone.cfg['timer-K']) / 1000,
																			name='Timer K: Wait time for response retransmits, T4 for UDP, 0s for TCP/SCTP', callback=self.__setTerminatedState)													


		# variables
		self.req  = None # contains the last request sent
		
	def __getState(self):
		"""
		"""
		return self.__transactionState.get()
		
	def __setState(self, state):
		"""
		"""
		self.__transactionState.set(state)
		
	def __setCompletedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_COMPLETED)
		self.__timerF.stop()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerE.stop()
			self.__timerK.setDuration(duration=float(self.phone().cfg['timer-K']) / 1000)
			self.__timerK.start()
		else:
			self.__timerK.setDuration(duration=float(0))
			self.__timerK.start()
			
	def __setProceedingState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_PROCEEDING)
		
	def __setTerminatedState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_TERMINATED)
		self.phone().transactions().remove(self)
	
	def __setTryingState(self):
		"""
		"""
		self.__setState(state=TRANSACTION_STATE_TRYING)
		
	def saveTransactionId(self, via, cseq, callid, fromhdr):
		"""
		"""
		self.__tid_sip.set(via=via, cseq=cseq, callid=callid, fromhdr=fromhdr)
		self.debug( "sip id: %s" % self.__tid_sip.get() )

	def resetTransaction(self):
		"""
		"""
		self.__setState(state='idle')
		# reset timers
		self.__timerF.stop()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerE.stop()
			self.__timerK.stop()
			
	def recognizeTransaction(self, tid):
		"""
		Check if the response is for me
		"""
		try:
			# verify
			recognized = True
			nb = 0
			a, b, c, d, e, f =  tid.get()
			la, lb, lc, ld, le, lf = 	self.__tid_sip.get()
			
			if len(a):
				nb += 1
				if a != la: recognized=False
			if len(b): 
				nb += 1
				if b != lb: recognized=False		
			if len(c): 
				nb += 1
				if c != lc: recognized=False	
			if len(d): 
				nb += 1
				if d != ld: recognized=False	
			if len(e): 
				nb += 1
				if e != le: recognized=False	
			if len(f): 
				nb += 1
				if f != lf: recognized=False	
			
			if nb != tid.getSize():
				recognized=False
			
			self.debug( 'Matching Client Transaction %s: %s' % (self.__tid_sip.get(), recognized) )	
		except Exception as e:
			self.error( 'internal error on recognize non invite client transaction: %s' % str(e) )
		return recognized
		
	def dispatchResponse(self, response):
		"""
		Valid response, dispatch it
		"""
		sip_layer = response.get('SIP')
		sip_status = sip_layer.get('status')
		status_code = sip_status.get('code')
		status_phrase = sip_status.get('phrase')
		sip_hdrs = sip_layer.get('headers')

		if status_code.startswith('1') :
			self.__onResponse1xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('2') :
			self.__onResponse2xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('3') :
			self.__onResponse3xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('4') :
			self.__onResponse4xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('5') :
			self.__onResponse5xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		elif status_code.startswith('6') :
			self.__onResponse6xx(sip_response=response, sip_headers=sip_hdrs, sip_code=status_code, sip_phrase=status_phrase)
		else:
			self.debug( response )
			self.error( 'status code received unknown: %s %s' %  (status_code, status_phrase) )
				
	def sendRequest(self, sip_request):
		"""
		"""
		# extract top via and save transactin id
		sip_headers = sip_request.get('headers')
		via = sip_headers.get('via')
		if isinstance(via, TestTemplatesLib.TemplateLayer):
			vias = via.getItems()
			vias.sort()
			k, topvia = vias [0] 
		else:
			topvia = via
		self.saveTransactionId( via=topvia, cseq=sip_headers.get('cseq'), callid=sip_headers.get('call-id'),
														fromhdr=sip_headers.get('from')	)

		# send request
		self.__sendRequest(sip_request=sip_request)
		
		# start timers
		self.__timerF.start()
		if self.phone().transport() == AdapterUDP.PROTOCOL_UDP:
			self.__timerE.setDuration( float(self.__timerE_value) / 1000 )
			self.__timerE.start()
			
		# set state
		self.__setTryingState()
		
	def __sendRequest(self, sip_request):
		"""
		"""
		# send request
		self.req = sip_request
		self.sip().sendMessage(tpl=sip_request)
					
	def __onTransactionTimeout(self):
		"""
		Timer F fired
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:
			self.__timerE.stop()
			self.__setTerminatedState()
			self.onTransactionTimeout()

	def __onRetransmissionTimeout(self):
		"""
		Timer E fired
		"""
		if self.__getState() in [ 'trying' ]:
			# retransmission 
			self.__sendRequest(sip_request=self.req)
			# reset timer E and rearm
			# exponentially increasing interval
			self.__timerE_value *= 2
			timerE = min( self.__timerE_value, self.phone().cfg['T2'] )
			self.__timerE.setDuration( float(timerE) / 1000 )
			self.__timerE.start()
		elif self.__getState() in [ 'proceeding' ]:
			# retransmission 
			self.__sendRequest(sip_request=self.req)
			# reset timer to T2
			self.__timerE.setDuration( self.phone().cfg['T2'] )
			self.__timerE.start()
			

		
	def __onResponse1xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'trying' ]:
			self.__setProceedingState()
			self.onResponse1xx(sip_response, sip_headers, sip_code, sip_phrase)

	def __onResponse2xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse2xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse3xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse3xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse4xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse4xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse5xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse5xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def __onResponse6xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		if self.__getState() in [ 'trying', 'proceeding' ]:
			self.__setCompletedState()
			self.onResponse6xx(sip_response, sip_headers, sip_code, sip_phrase)
		elif self.__getState() in [ 'completed' ]:
			self.onRetranmissionDetected()
			
	def onRetranmissionDetected(self):
		"""
		"""
		self.warning( 'final response retransmission detected, response discarded' )
		
	def onTransactionTimeout(self):
		"""
		"""
		pass
		
	def onResponse1xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('1xx not yet implemented')

	def onResponse2xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('2xx not yet implemented')
				
	def onResponse3xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('3xx not yet implemented')

	def onResponse4xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('4xx not yet implemented')
		
	def onResponse5xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('5xx not yet implemented')

	def onResponse6xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		self.warning('6xx not yet implemented')
		
# Sessions Manager
CALL_IN=0
CALL_OUT=1
class Sessions(CommonLogger):
	def __init__(self, phone):
		"""
		"""
		CommonLogger.__init__(self, phone=phone, name='SESSIONS')
		self.__sessions =  {}
		self.__id = 0
		
	def add(self):
		"""
		""" 
		self.__id += 1
		self.debug( 'adding session: %s' % self.__id )
		sess = Session(phone=self.phone(), id=self.__id )
		self.__sessions[self.__id] = 	sess
		return ( self.__id, sess )
		
	def get(self, id):
		"""
		"""
		if self.__sessions.has_key(id):
			return self.__sessions[id]
		else:
			return None
			
	def reset(self):
		"""
		"""
		for sessid, sess in self.__sessions.items():
			sess.reset()
			
	def find(self, did):
		"""
		"""
		ret = None
		for sessid, sess in self.__sessions.items():
			if sess.recognizeDialog(did):
				ret = sess
				break
		return ret
#		
# Session = Dialog + offer/answer exchange
# Dialog = Created by an INVITE and terminated by a BYE
class Session(CommonLogger):
	def __init__(self, phone, id):
		"""
		Transaction user for session
		"""
		CommonLogger.__init__(self, phone=phone, name='SESSION')
		# call state
		self.sessState = TestAdapterLib.State(parent=phone, name='%s_SESSION' % __NAME__, initial='idle')
		
		# dialog manager
		self.__dialog = Dialog(phone=phone, session=self)	
		self.__dialogId = TransactionDialogID(phone=phone)
		# initialize variables
		self.__origreq = None
		
		self.__id = id
		self.__timeout = 5.0
		self.__audioport_src = 0
		self.__sdp_offer = None
		self.__sdp_answer = None
		self.__calldirection = None
		# initialize sdp and rtp adapters
		self.__sdp = LibrarySDP.SDP(parent=phone.testcase(), debug=phone.debugmode(),
									unicastAddress=phone.cfg['bind-rtp-ip'], connectionAddress=phone.cfg['bind-rtp-ip'] )	


		if phone.cfg['enable-rtp']:
			self.__rtp = AdapterRTP.Client( parent=phone.testcase(), debug=phone.debugmode(), bindIp=phone.cfg['bind-rtp-ip'], 
																bindPort=phone.cfg['bind-rtp-port'],  recordRcvSound=False, recordSndSound=False, 
																defaultSound=AdapterRTP.SOUND_SINE_1K	,
																logLowLevelEvents=False, payloadType=LibraryCodecs.A_G711U, sessionId=self.__id,
																agentSupport=phone.cfg['agent-support'], agent=phone.cfg['agent'], 
																shared=phone.cfg['shared'], name=phone.cfg['adapter-name']	) 
	def saveDialogId(self, callid, fromhdr):
		"""
		"""
		self.__dialogId.set(callid=callid, fromhdr=fromhdr)
		self.debug( "dialog id: %s" % self.__dialogId.get() )
	def updateDialogId(self, callid, tohdr):
		"""
		"""
		self.__dialogId.set(callid=callid, fromhdr=tohdr)
		self.debug( "dialog id updated: %s" % self.__dialogId.get() )
		
	def calldirection(self):
		"""
		"""
		return self.__calldirection
		
	def recognizeDialog(self, did):
		"""
		Check if the response is for me
		"""
		# verify
		recognized = True
		nb = 0
		a, b, c, d, e, f =  did.get()
		la, lb, lc, ld, le, lf = 	self.__dialogId.get()
		
		if len(a):
			nb += 1
			if a != la: recognized=False
		if len(b): 
			nb += 1
			if b != lb: recognized=False		
		if len(c): 
			nb += 1
			if c != lc: recognized=False	
		if len(d): 
			nb += 1
			if d != ld: recognized=False	
		if len(e): 
			nb += 1
			if e != le: recognized=False	
		if len(f): 
			nb += 1
			if f != lf: recognized=False	
		
		if nb != did.getSize():
			recognized=False
		
		self.debug( 'Matching Dialog %s: %s' % (self.__dialogId.get(), recognized) )	
		return recognized
		
	def sessid(self):
		"""
		"""
		return self.__id
		
	def dialog(self):
		"""
		"""
		return self.__dialog

		
	def reset(self):
		"""
		"""
		self.__calldirection = None
		self.setState( 'idle' )
		# reset dialog
		self.__dialog.reset()
		# cleanup rtp
		if self.phone().cfg['enable-rtp']:
			self.rtp().stopListening()		
			rtp_stopped = self.rtp().isStopped( timeout=self.__timeout )
			if not rtp_stopped:
				self.error('finalize RTP failed')
			self.rtp().onReset()
			
	def getSipState(self):
		"""
		"""
		return self.dialog().getState()
		
	def setSipState(self, state):
		"""
		"""
		self.dialog().setState(state=state)
		
	def getState(self):
		"""
		"""
		return self.sessState.get()
		
	def setState(self, state):
		"""
		"""
		self.sessState.set(state)	
		
	def saveOrigRequest(self, request):
		"""
		"""
		try:
			self.__origreq = request
			sip_req = self.__origreq.get('headers')
			# 
			self.saveDialogId( callid=sip_req.get('call-id') , fromhdr=sip_req.get('from') )
		except Exception as e:
			self.error( 'internal error save original request: %s' % str(e) )	
			
	def getOrigRequest(self):
		"""
		"""
		return self.__origreq
		
	def rtp(self):
		"""
		"""
		return self.__rtp
		
	def sdp(self):
		"""
		"""
		return self.__sdp
		
	def getSdpOffer(self):
		"""
		"""
		self.__sdp_offer = self.sdp().getOffer( audioPort=self.__audioport_src )
		return self.__sdp_offer

	def getSdpAnswer(self):
		"""
		"""
		return self.sdp().getAnswer(audioPort=self.__audioport_src)
		
	def negotiatesCodec(self, sdp):
		"""
		"""
		negotiated = False
		try:
			codec, ipRtpDest, portRtpDest = self.sdp().negotiatesCodec( sdp=sdp )
			self.debug( 'codec choosed: %s' % codec )
			self.debug( 'rtp ip destination: %s' % ipRtpDest )
			self.debug( 'rtp port destination: %s' % portRtpDest )
			if codec is not None:
				negotiated = True
				self.rtp().setCodec(payloadType=codec)
				self.rtp().setDestination(destinationIp=ipRtpDest, destinationPort=portRtpDest)
		except Exception as e:
			self.error( 'internal error negotiates codec: %s' % str(e) )	
		return negotiated
		
	def startingIncomingDialog(self, sip_request, sip_headers, sip_method):
		"""
		"""
		try:
			self.setState('incoming-call')
			self.__calldirection = CALL_IN 
			
			# extract call origin information
			from_hdr = sip_headers.get('from')
			diversion_hdr = sip_headers.get('diversion')
			identity_hdr = sip_headers.get('p-asserted-identity')
			# "bob" <sip:bob-xtc@sip2sip.info>;tag=bebf9489d69a4bbfba50bdfa79ba4a76
			ci=None; display=None;
			try:
				cli = from_hdr.split('>')[0].split('<')[1].split(':')[1]
				display = from_hdr.split('"')[1]
			except Exception as e:
				self.error( 'unable to extract caller info: %s' % str(e) )
			
			# log event
			tpl = templates.incomingcall(sessid= self.sessid(), cli=cli, display=display, 
																		diversion=diversion_hdr, assertedidentity=identity_hdr) 
			self.phone().logRecvEvent( shortEvt = 'incoming call', tplEvt = tpl )
			
			# save invite and initialize the dialog
			self.saveOrigRequest( request=sip_request.get('SIP'))
			
			# initialize rtp
			audioPort = 0
			if self.phone().cfg['enable-rtp']:
				self.rtp().startListening()
				rtp_listening = self.rtp().isListening( timeout=self.__timeout )
				if not rtp_listening:
					self.error('Initialize RTP failed')
				else:
					udp_layer = rtp_listening.get('UDP')
					self.__audioport_src = udp_layer.get('source-port')
					if isinstance(self.__audioport_src, TestTemplatesLib.TemplateLayer):
						self.__audioport_src = self.__audioport_src.getName()
						
					# start dialog with rtp
					self.dialog().dispatchRequest( sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method )
			else:
				# start dialog without rtp
				self.dialog().dispatchRequest( sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method )
		except Exception as e:
			self.error( 'internal error incoming dialog: %s' % str(e) )	
			
	def startingOutgoingDialog(self, destAddr, recordSesssion, playSound, codecSound, headers):
		"""
		"""
		try:
			self.setState('outgoing-call')
			self.__calldirection = CALL_OUT 
			# log event
			tpl = templates.outgoingcall(sessid= self.sessid() ) 
			self.phone().logSentEvent( shortEvt = 'outgoing call', tplEvt = tpl )
			
			# update sdp with the prefered codecs, reorder the list
			self.sdp().reorderCodecs(preferedCodec=codecSound)
			
			# initialize rtp
			audioPort = 0
			if self.phone().cfg['enable-rtp']:
				# configure rtp
				self.rtp().configure(recordRcvSound=recordSesssion, recordSndSound=recordSesssion)
				self.rtp().configure(defaultSound=playSound, payloadType=codecSound)
				
				self.rtp().startListening()
				rtp_listening = self.rtp().isListening( timeout=self.__timeout )
				if not rtp_listening:
					self.error('Initialize RTP failed')
				else:
					udp_layer = rtp_listening.get('UDP')
					self.__audioport_src = udp_layer.get('source-port')
					if isinstance(self.__audioport_src, TestTemplatesLib.TemplateLayer):
						self.__audioport_src = self.__audioport_src.getName()
						
					# start dialog with rtp
					self.dialog().sendInvite( requestUri=destAddr, headers=headers )
			else:
				# start dialog without rtp
				self.dialog().sendInvite( requestUri=destAddr, headers=headers )
		except Exception as e:
			self.error( 'internal error outgoing dialog: %s' % str(e) )	
			
	def outgoingDialogConfirmed(self):
		"""
		"""
		try:
			self.setState('call-confirmed')	
			if self.phone().cfg['enable-rtp']:
				self.rtp().startSending()
		except Exception as e:
			self.error( 'internal error dialog confirmed: %s' % str(e) )	
	def incomingDialogConfirmed(self):
		"""
		"""
		try:
			self.setState('call-confirmed')	
			if self.phone().cfg['enable-rtp']:
				self.rtp().startSending()
		except Exception as e:
			self.error( 'internal error dialog confirmed: %s' % str(e) )			
	def acceptingDialog(self, recordSesssion=None, playSound=None, headers={}):
		"""
		"""
		self.setState('accepting-incoming-call')
		
		# record the session
		if self.phone().cfg['enable-rtp']:
			self.rtp().configure(recordRcvSound=recordSesssion, recordSndSound=recordSesssion)
			self.rtp().configure(defaultSound=playSound)
			
		sdpAnswer = self.getSdpAnswer()
		tagto = self.sip().getLocalTag()
		# extract record route from original
		origreq = self.getOrigRequest()
		sip_headers = origreq.get('headers')
		recordroute_hdr = sip_headers.get('record-route')
		more_headers = {}
		if recordroute_hdr is not None: 
			more_headers = {'record-route':recordroute_hdr }
		
		# add additionals headers
		more_headers.update( headers )	
		self.dialog().sendSuccessResponse(sip_code='200', sip_phrase='OK', 
																			tagto=tagto, sdp=sdpAnswer, headers=more_headers)
	def rejectingDialog(self, code, phrase, headers={}):
		"""
		"""
		self.setState('rejecting-incoming-call')
		tagto = self.sip().getLocalTag()
		# extract record route from original
		origreq = self.getOrigRequest()
		sip_headers = origreq.get('headers')
		recordroute_hdr = sip_headers.get('record-route')
		more_headers = {}
		if recordroute_hdr is not None: 
			more_headers = {'record-route':recordroute_hdr }
		# add additionals headers
		more_headers.update( headers )				
		self.dialog().sendFinalResponse(sip_code=code, sip_phrase=phrase, tagto=tagto, headers=more_headers)	
		
	def stoppingDialog(self, headers):
		"""
		Stopping dialog, initiated by the local party
		"""
		try:
			if self.dialog().getState() == 'idle':
				self.debug( 'nothing todo: call is in idle state')
				return
	
			self.setState('outgoing-end')
			
			# log event
			tpl = templates.hangupcall(sessid= self.sessid() ) 
			self.phone().logSentEvent( shortEvt = 'hang-up', tplEvt = tpl )
		
			# stop media
			if self.phone().cfg['enable-rtp']:
				self.rtp().stopSending()		
	
			self.dialog().sendBye(headers=headers)
		except Exception as e:
			self.error( 'internal error stopping dialog: %s' % str(e) )	
			
	def cancellingDialog(self, headers):
		"""
		"""
		try:
			if self.dialog().getState() == 'idle':
				self.debug( 'nothing todo: call is in idle state')
				return
			self.setState('outgoing-cancel')
			
			# log event
			tpl = templates.hangupcall(sessid= self.sessid() ) 
			self.phone().logSentEvent( shortEvt = 'hang-up', tplEvt = tpl )
	
			# stop media
			if self.phone().cfg['enable-rtp']:
				self.rtp().stopSending()		
	
			self.dialog().sendCancel(headers=headers)
		except Exception as e:
			self.error( 'internal error cancelling dialog: %s' % str(e) )	
			
	def dialogStopped(self):
		"""
		Dialog stopped by other party
		"""
		try:
			self.setState('incoming-end')
			
			# stop media
			if self.phone().cfg['enable-rtp']:
				self.rtp().stopSending()	
		except Exception as e:
			self.error( 'internal error dialog stopped: %s' % str(e) )	

	def isReceivingAudio(self, timeout=1.0, codec=None):
		"""
		"""
		return self.rtp().hasStartedReceiving(timeout=timeout, type='audio', sessionid=self.sessid(), codec=codec )
	
	def isNoLongerReceivingAudio(self, timeout=1.0, codec=None):
		"""
		"""
		return self.rtp().hasStoppedReceiving(timeout=timeout, type='audio', sessionid=self.sessid(), codec=codec )
		
#		
# >> INVITE state machine
#
#             ----->  idle
#             |        |           ---------------------------------------
#             |        | invite   |                                       |
#             |        | sent     |                                       |                 
#             |        v          v                                       | invite
# unexpected  |<--- waiting-100-trying  -----------> |                    | resent
#  response   |        |                             |                    |
#  received   |        | 100 received                |                    |
#             |        |                             |                    |
#             |        v                             |   2xx              |
#             |<--- waiting-provisional-response---->| received           |
#             |        |                             |                    | 
#             |        | 1xx received                |                    | 
#             |        |                       	     |                    |
#             |        v                       	    ---    407            |             
#             |<--- waiting-success-response ------/ | \--------->  challenging-invite
#             |        |                       	     |    received
#             |        | 2xx received                |
#             |        |                             |
#             |        v                             |
#             |<--- connected  <---------------------|
#
# >> BYE state machine
# 
#                  connected
#	                     |
#                      | bye sent  
#                      |                     
#                      v
#    idle <------- waiting-100-trying-bye ---------->|
#             ^        |                        	   |
#             |        | 100 received                |
# unexpected  |        |                        	   |
#  response   |        v                       	     |   2xx 
#  received   |<--- waiting-success-response-bye     | received
#             |        |                       	     |    
#             |        | 2xx received                |
#             |        |                             |
#             |        v                             |
#             |<--- disconnected  <------------------|
#
#
# >> CANCEL state machine
#
#             waiting-provisional-response/
#               waiting-success-response
#	                           |
#                            | cancel sent 
#                            |           _____
#                            |          |     |       
#                            v          v     |
#            ---- waiting-cancel-response     | 2xx received
#            |               |      |         |
#            |               |      |_________|
#            | 	             |
# unexpected | 	             | 487 received
#  response  | 	             | 
#  received  | 	             v
#            |            cancelled
#            |               |
#            |               |
#            |               |
#            |               v
#            |------------> idle

class Dialog(CommonLogger):
	def __init__(self, phone, session):
		"""
		Transaction User for dialog
		"""
		CommonLogger.__init__(self, phone=phone, name='DIALOG')
		self.__session = session
		self.__dialogState = TestAdapterLib.State(parent=phone, name='%s_DIALOG' % __NAME__, initial='idle')
		self.__callid = phone.getNewCallId()
		# initialize vars
		self.challengeRsp = None
		self.uriCalled = None
		self.more_headers = {}
	def callid(self):
		"""
		"""
		return self.__callid
	def session(self):
		"""
		"""
		return self.__session
		
	def reset(self):
		"""
		"""
		self.setState( 'idle' )
		self.session().setState('idle')
		self.challengeRsp = None
		self.uriCalled = None
		self.more_headers = {}

	def getState(self):
		"""
		"""
		return self.__dialogState.get()
		
	def setState(self, state):
		"""
		"""
		self.__dialogState.set(state)	
		
	def onTransactionTimeout(self):
		"""
		Timer F fired
		"""
		try:
			if self.getState() in [ 'waiting-100-trying', 'waiting-ringback-tone', 'ringback-tone' ]:
				self.reset()
				self.phone().logRecvEvent( shortEvt = 'call connection timeout', tplEvt = templates.call_connection_timeout(sessid=self.sessions().sessid() ) ) 
			elif self.getState() in [ 'ringing' ]:
				self.reset()
				self.phone().logRecvEvent( shortEvt = 'call connection timeout', tplEvt = templates.call_connection_timeout(sessid=self.sessions().sessid() ) ) 
		except Exception as e:
			self.error( 'internal error transaction timeout: %s' % str(e) )
			
	def sendInvite(self, requestUri, headers={}):
		"""
		Send an initial invite request
		"""
		try:
			# memorize additional headers and uri to call
			self.more_headers = headers
			self.uriCalled = requestUri
			# add more: challenge, sdp, additionals headers etc ...
			if self.challengeRsp is not None:
				headers.update( self.challengeRsp )
			sdpOffer = self.session().getSdpOffer()
			# prepare invite and construct an internal id associated to this request
			req_tpl = self.sip().INVITE(callId=self.callid(), requestUri=requestUri, sdp=sdpOffer, send=False, headers=headers)
			self.session().saveOrigRequest(request = req_tpl)
			# create a new transaction with wrappers
			transaction = self.phone().transactions().add(method='INVITE')
			transaction.onTransactionTimeout = self.onTransactionTimeout
			transaction.onResponse1xx = self.onResponse1xx
			transaction.onResponse2xx = self.onResponse2xx
			transaction.onResponse3xx = self.onResponse3xx
			transaction.onResponse4xx = self.onResponse4xx
			transaction.onResponse5xx = self.onResponse5xx
			transaction.onResponse6xx = self.onResponse6xx
			# send the request
			transaction.sendRequest(sip_request=req_tpl)
			# set sip state, and save uri called
			self.setState('waiting-100-trying')
		except Exception as e:
			self.error( 'internal error send invite request: %s' % str(e) )
			
	def sendCancel(self, headers={}):
		"""
		"""
		try:
			# get values from the initial invite
			initial_req = self.session().getOrigRequest()
			sip_headers = initial_req.get('headers')
			sip_request = initial_req.get('request')
			cseq_initial = sip_headers.get('cseq').split(' ')[0]
			via_initial = sip_headers.get('via')
			toHeader = sip_headers.get('to')
			fromHeader = sip_headers.get('from')
			requestUri = sip_request.get('uri')
			# prepare cancel
			req_tpl = self.sip().CANCEL( requestUri=requestUri, cseq=cseq_initial, via=via_initial, callId=self.callid(),
																fromHeader=fromHeader, toHeader=toHeader, send=False, headers=headers)
			# create a new transaction with wrappers
			transaction = self.phone().transactions().add(method='CANCEL')
			transaction.onTransactionTimeout = self.onTransactionTimeout
			transaction.onResponse1xx = self.onResponse1xx
			transaction.onResponse2xx = self.onResponse2xx
			transaction.onResponse3xx = self.onResponse3xx
			transaction.onResponse4xx = self.onResponse4xx
			transaction.onResponse5xx = self.onResponse5xx
			transaction.onResponse6xx = self.onResponse6xx
			# send the request
			transaction.sendRequest(sip_request=req_tpl)
			# set sip state
			self.setState('waiting-cancel-response')	
		except Exception as e:
			self.error( 'internal error request send cancel: %s' % str(e) )
			
	def sendBye(self, headers={}):
		"""
		"""
		try:
			# prepare bye and construct an internal id associated to this request
			req_tpl = self.sip().BYE( callId=self.callid(), send=False, headers=headers)
			# create a new transaction with wrappers
			transaction = self.phone().transactions().add(method='BYE')
			transaction.onTransactionTimeout = self.onTransactionTimeout
			transaction.onResponse1xx = self.onResponse1xx
			transaction.onResponse2xx = self.onResponse2xx
			transaction.onResponse3xx = self.onResponse3xx
			transaction.onResponse4xx = self.onResponse4xx
			transaction.onResponse5xx = self.onResponse5xx
			transaction.onResponse6xx = self.onResponse6xx
			# send the request
			transaction.sendRequest(sip_request=req_tpl)
			# set sip state
			self.setState('waiting-100-trying-bye')	
		except Exception as e:
			self.error( 'internal error send bye request: %s' % str(e) )
			
	def sendAck(self, to=None):
		"""
		"""
		try:
			# get values from the initial invite
			initial_req = self.session().getOrigRequest()
			sip_headers = initial_req.get('headers')
			sip_request = initial_req.get('request')
			cseq_initial = sip_headers.get('cseq').split(' ')[0]
			via_initial = sip_headers.get('via')
			sip_body= initial_req.get('body')
			
			# 17.1.1.3 Construction of the ACK Request
			# The ACK MUST contain a single Via header field, and this MUST be equal to the top 
			# Via header field of the original request. 
			if isinstance( via_initial, TestTemplatesLib.TemplateLayer ):
				viaHeader = via_initial.get('0')
			else:
				viaHeader = via_initial
	
			if to is not None:
				fromHeader = sip_headers.get('from')
				requestUri = sip_request.get('uri')
			else:
				requestUri = None
				fromHeader = None
			
			# prepare ack
			req_tpl = self.sip().ACK( requestUri=requestUri, cseq=cseq_initial, via=viaHeader, callId=self.callid(),
																fromHeader=fromHeader, toHeader=to, send=False)
			# send ack
			self.sip().sendMessage(tpl=req_tpl)
			
			# recall with an invite authenticated 
			if self.getState() in [ 'challenging-invite' ]:
				self.sendInvite( requestUri= self.uriCalled, headers=self.more_headers )
		except Exception as e:
			self.error( 'internal error send ack request: %s' % str(e) )
			
	def dispatchRequest(self, sip_request, sip_headers, sip_method):
		"""
		"""
		try:
			transaction = self.phone().transactions(client=False).add(method=sip_method)
			transaction.onIncomingRequest(sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method)
			if sip_method in self.sip().cfg['sip-allow']:
				if sip_method == 'BYE':
					self.onByeReceived( transaction=transaction, sip_request=sip_request,
															sip_headers=sip_headers, sip_method=sip_method)
				elif sip_method == 'INVITE':
					transaction.onTransactionTimeout = self.onTransactionTimeout
					transaction.onAck = self.onAckReceived
					self.onInviteReceived( transaction=transaction, sip_request=sip_request,
																	sip_headers=sip_headers, sip_method=sip_method)			
				elif sip_method == 'CANCEL':
					self.onCancelReceived( transaction=transaction, sip_request=sip_request, 
																sip_headers=sip_headers, sip_method=sip_method)	
				else:
					self.debug( 'The method %s not yet implemented in this dialog' % sip_method )
					self.sendFinalResponse(transaction=transaction, sip_code='501', sip_phrase='Not Implemented')
			else:
				self.debug( 'The method %s is not supported in this dialog' % sip_method)
				self.sendFinalResponse(transaction=transaction, sip_code='501', sip_phrase='Not Implemented')
		except Exception as e:
			self.error( 'internal error request dispatcher: %s' % str(e) )
	
	def sendProvisionalResponse(self, sip_code, sip_phrase, transaction=None, tagto=None, headers={}):
		"""
		"""
		try:
			# find original transaction if none
			__transaction__ = None
			if transaction is None:
				orig = self.session().getOrigRequest()
				sip_req = orig.get('headers')
				tid = TransactionDialogID( phone=self )
				tid.set( cseq=sip_req.get('cseq'), callid=sip_req.get('call-id'), tohdr=sip_req.get('to'), fromhdr=sip_req.get('from'),)
				origtransaction = self.phone().transactions(client=False).find(tid=tid)
				del tid
				if origtransaction is None:
					self.debug( 'original invite transaction not found' )
				else:
					__transaction__ = origtransaction
			else:
				__transaction__ = transaction
			
			# prepare response and send it
			if __transaction__ is not None:
				sip_request, sip_headers = __transaction__.getRequest()
				to_hdr = sip_headers.get('to')
				if tagto is not None:
					totag_hdr = '%s;tag=%s' % (to_hdr,tagto)
				else:
					totag_hdr = to_hdr
				rsp_tpl = self.sip().Status(code=sip_code, phrase=sip_phrase,
																		fromHeader=sip_headers.get('from'), toHeader=totag_hdr,
																		callId=sip_headers.get('call-id'), via=sip_headers.get('via'), 
																		cseq=sip_headers.get('cseq'), send=False, headers=headers)
				__transaction__.sendProvisionalResponse(sip_response=rsp_tpl)
		except Exception as e:
			self.error( 'internal error send prov response: %s' % str(e) )
			
	def sendFinalResponse(self, sip_code, sip_phrase, transaction=None, tagto=None, headers={}):
		"""
		"""
		try:
			# find original transaction if none
			__transaction__ = None
			if transaction is None:
				orig = self.session().getOrigRequest()
				sip_req = orig.get('headers')
				tid = TransactionDialogID( phone=self )
				tid.set( cseq=sip_req.get('cseq'), callid=sip_req.get('call-id'), tohdr=sip_req.get('to'), fromhdr=sip_req.get('from'),)
				origtransaction = self.phone().transactions(client=False).find(tid=tid)
				del tid
				if origtransaction is None:
					self.debug( 'original invite transaction not found' )
				else:
					__transaction__ = origtransaction
				self.setState('waiting-invite-final-ack')
			else:
				__transaction__ = transaction
				
			# prepare response and send it
			if __transaction__ is not None:
				sip_request, sip_headers = __transaction__.getRequest()
				to_hdr = sip_headers.get('to')
				if tagto is not None:
					totag_hdr = '%s;tag=%s' % (to_hdr,tagto)
				else:
					totag_hdr = to_hdr
				rsp_tpl = self.sip().Status(code=sip_code, phrase=sip_phrase,
																		fromHeader=sip_headers.get('from'), toHeader=totag_hdr,
																		callId=sip_headers.get('call-id'), via=sip_headers.get('via'), 
																		cseq=sip_headers.get('cseq'), send=False, headers=headers)
				__transaction__.sendFinalResponse(sip_response=rsp_tpl)
		except Exception as e:
			self.error( 'internal error send final response: %s' % str(e) )
	
	def sendSuccessResponse(self, sip_code, sip_phrase, transaction=None, tagto=None, sdp=None, headers={}):
		"""
		"""
		try:
			# find original transaction if none
			__transaction__ = None
			if transaction is None:
				orig = self.session().getOrigRequest()
				sip_req = orig.get('headers')
				tid = TransactionDialogID( phone=self )
				tid.set( cseq=sip_req.get('cseq'), callid=sip_req.get('call-id'), tohdr=sip_req.get('to'), fromhdr=sip_req.get('from'),)
				origtransaction = self.phone().transactions(client=False).find(tid=tid)
				del tid
				if origtransaction is None:
					self.debug( 'original invite transaction not found' )
				else:
					__transaction__ = origtransaction
				self.setState('waiting-invite-success-ack')
			else:
				__transaction__ = transaction
			
			# prepare response and send it
			if __transaction__ is not None:	
				sip_request, sip_headers = __transaction__.getRequest()
				to_hdr = sip_headers.get('to')
				if tagto is not None:
					totag_hdr = '%s;tag=%s' % (to_hdr,tagto)
				else:
					totag_hdr = to_hdr
				rsp_tpl = self.sip().Status(code=sip_code, phrase=sip_phrase,
																		fromHeader=sip_headers.get('from'), toHeader=totag_hdr,
																		callId=sip_headers.get('call-id'), via=sip_headers.get('via'), 
																		cseq=sip_headers.get('cseq'), sdp=sdp, send=False, headers=headers)
				__transaction__.sendSuccessResponse(sip_response=rsp_tpl)
		except Exception as e:
			self.error( 'internal error send success response: %s' % str(e) )
			
	def onAckReceived(self, sip_request, sip_headers, sip_method):
		"""
		"""
		try:
			if self.getState() in [ 'waiting-invite-success-ack' ]:
				self.session().incomingDialogConfirmed()
				self.setState('connected')
				
				# log event
				tpl = templates.call_connected(sessid=self.session().sessid())
				self.phone().logRecvEvent( shortEvt = 'call connected', tplEvt = tpl ) 
			elif self.getState() in [ 'waiting-invite-final-ack' ]:
				# log event
				tpl = templates.call_rejected(sessid=self.session().sessid())
				self.phone().logRecvEvent( shortEvt = 'call rejected', tplEvt = tpl ) 
				
				# reset 
				self.reset()
			elif self.getState() in [ 'waiting-cancel-ack' ]:
				# log event
				tpl = templates.call_cancelled(sessid=self.session().sessid())
				self.phone().logRecvEvent( shortEvt = 'call cancelled', tplEvt = tpl ) 
				
				self.setState('cancelled')
				
				# reset 
				self.reset()
			else:
				self.warning( 'unexpected ack received in state %s' % self.getState() )
		except Exception as e:
			self.error( 'internal error on received ack: %s' % str(e) )	
			
	def onCancelReceived(self, transaction, sip_request, sip_headers, sip_method):
		"""
		"""
		try:
			if self.getState() in [ 'ringing' ]:
				# send success response to cancel transaction
				self.sendSuccessResponse(transaction=transaction, sip_code='200', sip_phrase='OK')
				
				# send 487 for the invite transaction
				self.sendFinalResponse(sip_code='487', sip_phrase='Terminated')
					
				self.setState( 'waiting-cancel-ack' )
			else:
				self.onUnexpectedRequest( transaction=transaction, state=self.getState(), sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method  )
		except Exception as e:
			self.error( 'internal error on received cancel: %s' % str(e) )	
			
	def onByeReceived(self, transaction, sip_request, sip_headers, sip_method):
		"""
		"""
		try:
			if self.getState() in [ 'connected' ]:
				# stop session
				self.session().dialogStopped()
				
				more_headers = {}
				recordroute_hdr = sip_headers.get('record-route')
				contact_hdr = sip_headers.get('contact') 
				if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
				if recordroute_hdr is not None:  
					self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
					more_headers.update( {'record-route':recordroute_hdr } )
				
				# send success response 
				self.sendSuccessResponse(transaction=transaction, sip_code='200', sip_phrase='OK', headers=more_headers)		
				
				# log event
				reason = sip_headers.get('reason')
				if self.session().calldirection() == CALL_OUT:
					disconnected_by = 'callee'
				elif self.session().calldirection() == CALL_IN:
					disconnected_by = 'caller'
				else:
					disconnected_by = None
				tpl = templates.call_disconnected(sessid=self.session().sessid(), reason=reason, by=disconnected_by)
				self.phone().logRecvEvent( shortEvt = 'call ended', tplEvt = tpl ) 
				
				# reset 
				self.reset()
			else:
				self.onUnexpectedRequest( transaction=transaction, state=self.getState(), sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method  )
		except Exception as e:
			self.error( 'internal error on received bye: %s' % str(e) )	
			
	def onInviteReceived(self, transaction, sip_request, sip_headers, sip_method):
		"""
		"""
		try:
			if self.getState() in [ 'idle' ]:
				from_hdr = sip_headers.get('from')
				to_hdr = sip_headers.get('to')
				recordroute_hdr = sip_headers.get('record-route')
				contact_hdr = sip_headers.get('contact') 
				contenttype_hdr = sip_headers.get('content-type') 
				more_headers = {}
				
				# set remote target, routes,  local tag ad remote uri
				if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
				if recordroute_hdr is not None: 
					self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
					more_headers.update( {'record-route':recordroute_hdr } )
				self.sip().setLocalTag()
				self.sip().setRemoteUri(fromhdr=from_hdr) 
				self.sip().setRemoteTag(fromhdr=from_hdr) 
				# add tag in to
				tagto = self.sip().getLocalTag()
				tagto_hdr = "%s;tag=%s" % (sip_headers.get('to'), tagto)
				# update dialog and transaction id, not very nice ...
				self.session().updateDialogId(callid=sip_headers.get('call-id'), tohdr=tagto_hdr)
				transaction.updatetid(cseq=sip_headers.get('cseq'), callid=sip_headers.get('call-id'), 
														fromhdr=sip_headers.get('from'), tohdr=tagto_hdr  ) 
				
				# send provisional response
				self.sendProvisionalResponse(transaction=transaction, sip_code='100', sip_phrase='Trying', headers=more_headers)	

				# decode sdp 
				if contenttype_hdr is None:
					self.debug( 'no content type detected' )
					self.sendFinalResponse(transaction=transaction, sip_code='501', sip_phrase='Not Implemented',
																	tagto=tagto, headers=more_headers)
				else:
					if contenttype_hdr != 'application/sdp':
						self.debug( 'no sdp detected' )
						self.sendFinalResponse(transaction=transaction, sip_code='501', sip_phrase='Not Implemented',
																		tagto=tagto, headers=more_headers)
					else:
						self.session().sdp().setRemoteOffer( sdp=sip_request.get('SDP') )
						negotiated = self.session().negotiatesCodec( sdp=sip_request.get('SDP') )
						# negociation failed => send 606 Not Acceptable
						if not negotiated:
							self.debug( 'codec negotiation failed' )
							self.sendFinalResponse(transaction=transaction, sip_code='606', sip_phrase='Not Acceptable', 
																			tagto=tagto, headers=more_headers)
						else:
							# do not disturb activated ?
							if self.phone().cfg['dnd']:
								self.debug( 'dnd activated' )
								self.session().rejectingDialog(code='486', phrase='Busy Here')
							# auto answer activated ?
							elif self.phone().cfg['auto-answer']:
								self.debug( 'auto answer activated' )
								self.session().acceptingDialog()
							else:
								# send provisional response
								self.sendProvisionalResponse(transaction=transaction, sip_code='180', sip_phrase='Ringing',
																							tagto=tagto, headers=more_headers)	
								
								# log event
								self.setState('ringing')
								tpl = templates.ringing(sessid=self.session().sessid())
								self.phone().logRecvEvent( shortEvt = 'ringing', tplEvt = tpl ) 
				
			elif self.getState() in [ 'connected' ]:
				self.sendFinalResponse(transaction=transaction, sip_code='501', sip_phrase='Not Implemented')
			else:
				self.onUnexpectedRequest( transaction=transaction, state=self.getState(), sip_request=sip_request, sip_headers=sip_headers, sip_method=sip_method )
		except Exception as e:
			self.error( 'internal error on received invite: %s' % str(e) )
			
	def onUnexpectedRequest(self, transaction, state, sip_request, sip_method, sip_headers):
		"""
		"""
		try:
			self.debug('dialog, unexpected request %s received in state: %s' % (sip_method, state) )
			self.sendFinalResponse(transaction=transaction, sip_code='500', sip_phrase='Server Internal Error')
		except Exception as e:
			self.error( 'internal error unexpected request: %s' % str(e) )
		
	def onUnexpectedResponse(self, state, sip_code, sip_phrase):
		"""
		"""
		try:
			self.debug('unexpected response %s received in state: %s' % (sip_code, state) )
			
			# unexpected response for invite
			if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 
															'waiting-success-response', 'challenging-invite' ]:
				# log event
				tpl = templates.unexpected_response(sessid=self.session().sessid(), code=sip_code, phrase=sip_phrase)
				self.phone().logRecvEvent( shortEvt = 'calling error', tplEvt = tpl ) 
	
			# unexpected response for bye
			elif self.getState() in [ 'waiting-100-trying-bye', 'waiting-success-response-bye' ]:
				# log event
				tpl = templates.unexpected_response(sessid=self.session().sessid(), code=sip_code, phrase=sip_phrase)
				self.phone().logRecvEvent( shortEvt = 'hang-up error', tplEvt = tpl ) 
				
			self.reset()
		except Exception as e:
			self.error( 'internal error unexpected response: %s' % str(e) )
		
	def onResponse1xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""	
		try:
			# handle response for invite
			if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 'waiting-success-response' ]:
				if sip_code == '100':
					self.onTryingResponse(sip_response, sip_headers, sip_code, sip_phrase)
				else:
					self.onProvisionalResponse(sip_response, sip_headers, sip_code, sip_phrase)
			
			# handle response for bye 
			elif self.getState() in [ 'waiting-100-trying-bye' ]:
				if sip_code == '100':
					self.onTryingResponse(sip_response, sip_headers, sip_code, sip_phrase)
				else:
					self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 1xx : %s' % str(e) )
			
	def onTryingResponse(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response' ]:
				self.setState('waiting-provisional-response')
			elif self.getState() in [ 'waiting-100-trying-bye' ]:
				self.setState('waiting-bye-response')
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on trying response : %s' % str(e) )			
			
	def onProvisionalResponse(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in [ 'waiting-provisional-response', 'waiting-100-trying', 'waiting-success-response' ]:
				to_hdr = sip_headers.get('to')
				recordroute_hdr = sip_headers.get('record-route')
				contact_hdr = sip_headers.get('contact') 
	
				# set remote tag, remote target, and routes
				self.sip().decodeHeader_To( to_hdr )
				if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
				if recordroute_hdr is not None: self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
				
				# set ringback tone state
				if sip_code == '180': # Ringing
					self.setState('waiting-success-response')
					# log event
					tpl = templates.ringback_tone(sessid=self.session().sessid())
					self.phone().logRecvEvent( shortEvt = 'ringback tone', tplEvt = tpl ) 
				else:
					self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on prov response : %s' % str(e) )
			
	def onResponse2xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 'waiting-success-response' ]:
				self.challengeRsp = None 
				to_hdr = sip_headers.get('to')
				recordroute_hdr = sip_headers.get('record-route')
				contact_hdr = sip_headers.get('contact') 
				contenttype_hdr = sip_headers.get('content-type') 
				
				# set remote tag, remote target, and routes
				self.sip().decodeHeader_To( to_hdr )
				if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
				if recordroute_hdr is not None: self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
				
				# sdp 
				if contenttype_hdr is not None:
					if contenttype_hdr == 'application/sdp':
						self.session().sdp().setRemoteAnswer( sdp=sip_response.get('SDP') )
						negotiated = self.session().negotiatesCodec( sdp=sip_response.get('SDP') )				
						# negociation failed => ack + bye
						if not negotiated:
							self.sendAck()
							self.sendBye()
						# Negociation success => ack
						else:
							self.sendAck()
								
							self.session().outgoingDialogConfirmed()
							self.setState('connected')
							
							# log event
							tpl = templates.call_connected(sessid=self.session().sessid())
							self.phone().logRecvEvent( shortEvt = 'call connected', tplEvt = tpl ) 
			elif self.getState() in [ 'waiting-100-trying-bye', 'waiting-success-response-bye' ]:
				# log event
				if self.session().calldirection() == CALL_OUT:
					disconnected_by = 'caller'
				elif self.session().calldirection() == CALL_IN:
					disconnected_by = 'callee'
				else:
					disconnected_by = None
				tpl = templates.call_disconnected(sessid=self.session().sessid(), by=disconnected_by)
				self.phone().logRecvEvent( shortEvt = 'call ended', tplEvt = tpl ) 
				
				self.setState('disconnected')
				
				# reset 
				self.reset()
			elif self.getState() in [ 'waiting-cancel-response' ]:
				self.debug( 'cancel accepted' )
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 2xx : %s' % str(e) )
			
	def onResponse3xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 'waiting-success-response' ]:
					to_hdr = sip_headers.get('to')
					
					recordroute_hdr = sip_headers.get('record-route')
					contact_hdr = sip_headers.get('contact') 
					if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
					if recordroute_hdr is not None: self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
				
					#self.sendAck( to=to_hdr )
					self.sendAck(  )
					
			self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 3xx : %s' % str(e) )
			
	def onResponse4xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 'waiting-success-response' ]:
				to_hdr = sip_headers.get('to')
				
				recordroute_hdr = sip_headers.get('record-route')
				contact_hdr = sip_headers.get('contact') 
				if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
				if recordroute_hdr is not None: self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
				
				if sip_code == '407': # Proxy Authentication Required
					if self.challengeRsp is not None: # authentication failed 
						# clear challenge rsp and send ack 
						self.challengeRsp = None 
						#self.sendAck( to=to_hdr )
						self.sendAck(  )
						self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )	
					else: # first tentative
						auth = sip_headers.get('proxy-authenticate')
						if auth is None:
							self.error( 'no proxy-authenticate header' )
						else:
							challenge = self.phone().rfc2617.decode(challenge=auth)
							rsp, cnonce, nc = self.phone().rfc2617.compute( username=self.phone().cfg['login'], password=self.phone().cfg['password'], 
																					realm=challenge['realm'], nonce=challenge['nonce'],
																					method='INVITE', uri=self.sip().getRemoteUri() , qop=None, algo=None, body=None )
							challengeRsp = self.phone().rfc2617.encode( username=self.phone().cfg['login'], realm=challenge['realm'], 
																						nonce=challenge['nonce'], uri=self.sip().getRemoteUri(), 
																						response=rsp, cnonce=cnonce, nc=nc)
							self.challengeRsp = {"proxy-authorization": challengeRsp} 
							self.setState('challenging-invite')
							self.sendAck( to=to_hdr )
				else:
					# clear challenge rsp send ack 
					self.challengeRsp = None 
					#self.sendAck( to=to_hdr )
					self.sendAck(  )
					self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )			
			elif self.getState() in [ 'waiting-cancel-response' ]:
				if sip_code == '487': # Request Terminated
					# ack response
					self.sendAck()
					
					# log event
					tpl = templates.call_cancelled(sessid=self.session().sessid())
					self.phone().logRecvEvent( shortEvt = 'call cancelled', tplEvt = tpl ) 
					
					self.setState('cancelled')	
					
					# reset 
					self.reset()
				else:
					self.onUnexpectedResponse(self.getState(), sip_code, sip_phrase)
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 4xx : %s' % str(e) )	
			
	def onResponse5xx(self, sip_response, sip_headers, sip_code, sip_phrase):
			"""
			"""
			try:
				if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 'waiting-success-response' ]:
					to_hdr = sip_headers.get('to')
					
					recordroute_hdr = sip_headers.get('record-route')
					contact_hdr = sip_headers.get('contact') 
					if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
					if recordroute_hdr is not None: self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
				
					self.sendAck(  )
					#self.sendAck( to=to_hdr )
					
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
			except Exception as e:
				self.error( 'internal error on 5xx : %s' % str(e) )
				
	def onResponse6xx(self, sip_response, sip_headers, sip_code, sip_phrase):
			"""
			"""
			try:
				if self.getState() in [ 'waiting-100-trying', 'waiting-provisional-response', 'waiting-success-response' ]:
					to_hdr = sip_headers.get('to')

					recordroute_hdr = sip_headers.get('record-route')
					contact_hdr = sip_headers.get('contact') 
					if contact_hdr is not None: self.sip().decodeHeader_Contact( contact_hdr )
					if recordroute_hdr is not None: self.sip().decodeHeader_RecordRoute( recordroute_hdr ) 
				
					self.sendAck( )
					#self.sendAck( to=to_hdr )
				
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
			except Exception as e:
				self.error( 'internal error on 6xx : %s' % str(e) )			
#
# REGISTER State machine
#
#             ---------->  not-registered
#            |                  |
#            |                  | [un]register sent
#            |                  |    _____________________________________
#            |                  |   |                                     |
#            |                  v   v                                     |
#            |<----------- registering                                    |
#            |                  |                                         |
# unexpected |                  | 401 received                            | refresh
#  response  |                  |                                         | registration
#  received  |                  v                                         | at 90% of expire
#            |<--------- challenging-[un]register ( [un]register resent)  |
#            |                  |                                         |
#            |                  | 200 received                            |
#            |                  |                                         |
#            |                  v                                         |
#            |<----------  registered ------------------------------------|                                                                                  
#
class Registration(CommonLogger):
	def __init__(self, phone):
		"""
		Transaction User (TU) for registration
		"""
		CommonLogger.__init__(self, phone=phone, name='REGISTRATION')
		
		# initialize state
		self.regState = TestAdapterLib.State(parent=phone, name='%s_REGISTER' % __NAME__, initial='not-registered')
		
		# initialize timers
		self.timerRefresh = TestAdapterLib.Timer(parent=phone, duration=phone.cfg['register-interval'], 
																			name='Timer Refresh: registration interval timer at 90% of the expire value',
																			callback=self.onRegistrationExpired)
		# initialize vars
		self.more_headers = {}
		
	def reset(self):
		"""
		"""
		self.setState('not-registered')
		self.more_headers = {}
		
	def getState(self):
		"""
		"""
		return self.regState.get()
		
	def setState(self, state):
		"""
		"""
		self.regState.set(state)
		
	def setExpire(self, expire):
		"""
		"""
		try:
			self.phone().cfg['register-interval'] = expire
			newExpire = int(int(expire)*90/100) # refresh registration at 90% 
			self.timerRefresh.setDuration(newExpire)
		except Exception as e:
			self.error( 'internal error set expire value: %s' % str(e) )
			
	def sendRegister(self, state, expire, headers={}):
		"""
		Send the initial register request
		"""
		
		try:
			# memorize additional headers
			self.more_headers = headers
			# set state
			self.setState(state)
			# generate a random callid 
			# prepare register and construct an internal id associated to this request
			callId = self.phone().getNewCallId()
			req_tpl = self.sip().REGISTER(callId=callId, expires=expire, send=False, headers=headers)
			# create a new transaction with wrappers
			transaction = self.phone().transactions().add(method='REGISTER')
			transaction.onTransactionTimeout = self.onTransactionTimeout
			transaction.onResponse1xx = self.onResponse1xx
			transaction.onResponse2xx = self.onResponse2xx
			transaction.onResponse3xx = self.onResponse3xx
			transaction.onResponse4xx = self.onResponse4xx
			transaction.onResponse5xx = self.onResponse5xx
			transaction.onResponse6xx = self.onResponse6xx
			# send the request
			
			transaction.sendRequest(sip_request=req_tpl)
		except Exception as e:
			self.error( 'internal error on send register request: %s' % str(e) )
			
	def onTransactionTimeout(self):
		"""
		Timer F fired
		"""
		try:
			self.reset()
			self.phone().logRecvEvent( shortEvt = 'registration timeout', tplEvt = templates.registration_timeout() ) 
		except Exception as e:
			self.error( 'internal error on transaction timeout: %s' % str(e) )
			
	def onRegistrationExpired(self):
		"""
		Timer Refresh fired
		"""
		try:
			# log event
			tpl = templates.registration(expire=self.phone().cfg['register-interval'])
			self.phone().logSentEvent( shortEvt = 'registration', tplEvt = tpl ) 
			# refresh registration
			self.sendRegister(state='registering', expire=self.phone().cfg['register-interval'], headers=self.more_headers )
		except Exception as e:
			self.error( 'internal error on reg expired: %s' % str(e) )
			
	def onUnexpectedResponse(self, state, sip_code, sip_phrase):
		"""
		"""
		try:
			self.debug('unexpected response %s received in state: %s' % (sip_code, state) )
			
			# log event
			tpl = templates.unexpected_response(state=state, code=sip_code, phrase=sip_phrase)
			self.phone().logSentEvent( shortEvt = 'registration error', tplEvt = tpl ) 
			
			self.reset()
		except Exception as e:
			self.error( 'internal error on unexpected response: %s' % str(e) )
			
	def onResponse1xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 1xx: %s' % str(e) )
			
	def onResponse2xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in [ 'challenging-register' ]:
				# handle response
				if sip_code == '200': # OK
					# extract expire in response
					expire_hdr = sip_headers.get('expires')
					contact_hdr = sip_headers.get('contact')
					if expire_hdr is not None:
						self.setExpire(expire=expire)
					else:
						if contact_hdr is not None:
							first_contact = contact_hdr.split(',')[0]
							if len(first_contact.split(';expires=')) == 2:
								self.setExpire( expire=first_contact.split(';expires=')[1].split(';')[0] )
								
					# start refresh timer
					if self.phone().cfg['auto-registration-refresh']:
						self.timerRefresh.start()
					
					# set final state and log event
					self.setState('registered')
					tpl = templates.registered(expire=self.phone().cfg['register-interval'])
					self.phone().logRecvEvent( shortEvt = 'registered', tplEvt = tpl )
				else:
					self.onUnexpectedResponse(self.getState(), sip_code, sip_phrase)
			elif self.getState() in [ 'challenging-unregister' ]:
				# handle response
				if sip_code == '200':
					self.reset()
					self.phone().logRecvEvent( shortEvt = 'unregistered', tplEvt = templates.unregistered() ) 
				else:
					self.onUnexpectedResponse(self.getState(), sip_code, sip_phrase)
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 2xx: %s' % str(e) )
			
	def onResponse3xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 3xx: %s' % str(e) )
			
	def onResponse4xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			if self.getState() in ['registering', 'unregistering' ]:
				# handle response
				if sip_code == '401': # Unauthorized
					auth = sip_headers.get('www-authenticate')
					if auth is None:
						self.error( 'no www-authenticate header' )
					else:
						challenge = self.phone().rfc2617.decode(challenge=auth)
						rsp, cnonce, nc = self.phone().rfc2617.compute( username=self.phone().cfg['login'], password=self.phone().cfg['password'], 
																				realm=challenge['realm'], nonce=challenge['nonce'],
																				method='REGISTER', uri=self.sip().getRemoteUri() , qop=None, algo=None, body=None )
						challengeRsp = self.phone().rfc2617.encode( username=self.phone().cfg['login'], realm=challenge['realm'], 
																					nonce=challenge['nonce'], uri=self.sip().getRemoteUri(), 
																					response=rsp, cnonce=cnonce, nc=nc)
						if self.getState() in [ 'registering' ]:
							expireValue = self.phone().cfg['register-interval']
							state = 'challenging-register'
						if self.getState() in [ 'unregistering' ]:
							expireValue = 0
							state = 'challenging-unregister'
						hdr = {"authorization": challengeRsp}
						hdr.update( self.more_headers )
						self.sendRegister(state=state, expire=expireValue, headers=hdr )
				elif sip_code == '423': # Interval Too Brief
					min_expire = sip_headers.get('min-expires')
					if min_expire is None:
						self.error( '423 received, but min-expires header is missing' )
					else:
						self.setExpire( expire=min_expire )
						self.sendRegister(state='registering', expire=min_expire)
				else:
					self.onUnexpectedResponse(self.getState(), sip_code, sip_phrase)
			elif self.getState() in ['challenging-register', 'challenging-unregister' ]: # authentication failed
				self.onUnexpectedResponse(self.getState(), sip_code, sip_phrase)
			else:
				self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 4xx: %s' % str(e) )	
			
	def onResponse5xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 5xx: %s' % str(e) )
			
	def onResponse6xx(self, sip_response, sip_headers, sip_code, sip_phrase):
		"""
		"""
		try:
			self.onUnexpectedResponse( self.getState(), sip_code, sip_phrase )
		except Exception as e:
			self.error( 'internal error on 6xx: %s' % str(e) )