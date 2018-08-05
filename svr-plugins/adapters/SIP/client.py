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

# RFC3261: SIP: Session Initiation Protocol

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

AdapterEthernet = sys.modules['SutAdapters.%s.Ethernet' % TestAdapterLib.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]
AdapterUDP = sys.modules['SutAdapters.%s.UDP' % TestAdapterLib.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapterLib.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapterLib.getVersion()]

LibrarySDP = sys.modules['SutLibraries.%s.Media' % TestLibraryLib.getVersion()]

try:
	import codec
	import templates
except ImportError: # python3 support
	from . import codec
	from . import templates

import random
import copy

__NAME__="""SIP"""

AGENT_TYPE_EXPECTED='socket'

VERSION_20 = 'SIP/2.0'

# Some functions for help
def QUO_URI(X, start_quote='<', end_quote='>'):
	"""
	Returns the quoted-string X with the surrounding < and >
	
	@param X: X
	@type X: string
	
	@param start_quote: default value = <
	@type start_quote: string
	
	@param end_quote: default value = >
	@type end_quote: string
	
	@return: X with quotes
	@rtype: string
	"""
	return '%s%s%s' % (start_quote, X,end_quote)
	
def UNQ_URI(X, start_quote='<', end_quote='>'):
	"""
	Returns the quoted-string X without the surrounding < and >.

	@param X: X
	@type X: string
	
	@param start_quote: default value = <
	@type start_quote: string
	
	@param end_quote: default value = >
	@type end_quote: string
	
	@return: X without quotes
	@rtype: string
	"""
	if X.startswith('<') and X.endswith('>'):
		return X[1:-1]
	else:
		return X
		
def RAND(length = 30, choice = 'azertyuiopqsdfghjklmwxcvbn0123456789'):
	"""
	Generate a random string according characters contained in choice which a length of 'length'
	
	@param length: length of the generated id
	@type length: integer
	
	@param choice: a string of all possible characters in the generated id.
	@type choice: string
	
	@return: the generated id
	@rtype: string
	"""
	rand_str = ''
	for i in range(int(length)):
		rand_str += random.choice(choice)
	return rand_str
	
def CALLID():
	"""
	Generate a random call-id number. The domain name is not added in the result.
	
	@return: the generated call-id
	@rtype: string
	"""	
	return RAND(choice = '0123456789ABCDEF')
	
def BRANCH():
	"""
	Generate a random branch of via header. The fixed party of the branch is not added here.
	
	@return: the branch number
	@rtype: string
	"""	
	return RAND(length = 30,choice = '0123456789')

def TAG():
	"""
	Generate a random tag.
	
	@return: the tag number
	@rtype: string
	"""		
	return RAND(30)
	
# SIP Client
class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, name=None,
								bindIp = '', bindPort=0, destIp='127.0.0.1', destPort=5060,  proxyHost='', 
								socketTimeout=10.0, socketFamily=AdapterIP.IPv4, transport=AdapterTCP.PROTOCOL_TCP,
								sipVersion=VERSION_20, sipAgent='ExtensiveTesting', sipMaxForwards=70, sipRport=True, sipInitialCseq=0,
								sipPuid='undefined', sipDomain='', sipDisplayName='',
								sslSupport=False, sslVersion=AdapterSSL.TLSv1, checkCert=AdapterSSL.CHECK_CERT_NO, 
								debug=False, logEventSent=True, logEventReceived=True, sniffer=False, bindEth="eth0",
								agentSupport=False, agent=None, shared=False):
		"""
		This class enables to send/receive SIP requests and responses, SSL support.
		This class inherit from the TCP and UDP adapters.
		
		@param parent: testcase 
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param bindIp: source ip
		@type bindIp: string

		@param bindPort: source port
		@type bindPort: integer

		@param destIp: destination proxy ip
		@type destIp: string

		@param destPort: destination proxy port (default: port 5060)
		@type destPort: integer

		@param proxyHost: destination proxy host (dns resolution)
		@type proxyHost: string
		
		@param bindEth: network interface to use with the sniffer mode (default=eth0)
		@type bindEth: string
		
		@param sniffer: activate the sniffer mode, control network layers (default=False)
		@type sniffer: boolean
		
		@param socketTimeout: connection timeout in second (default=300s)
		@type socketTimeout: float

		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: intconstant

		@param transport: SutAdapters.TCP.PROTOCOL_TCP (default) | SutAdapters.UDP.PROTOCOL_UDP
		@type transport: intconstant
		
		@param sipPuid: puid
		@type sipPuid: string
		
		@param sipDomain: domain name
		@type sipDomain: string
		
		@param sipDisplayName: local display name
		@type sipDisplayName: string
		
		@param sipVersion: SutAdapters.SIP.VERSION_20
		@type sipVersion: strconstant

		@param sipAgent: user agent (default=ExtensiveTesting)
		@type sipAgent: string
		
		@param sipMaxForwards: default value=70
		@type sipMaxForwards: integer

		@param sipRport: Allows a client to request that the server send the response back to the source IP address and port where the request came from. (default=True)
		@type sipRport: boolean
		
		@param sipInitialCseq: initial cseq value (default=0)
		@type sipInitialCseq: integer
		
		@param sslSupport: activate SSL channel (default=False)
		@type sslSupport: boolean

		@param sslVersion: SutAdapters.SSL.SSLv2 | SutAdapters.SSL.SSLv23 | SutAdapters.SSL.SSLv3 | SutAdapters.SSL.TLSv1 (default)
		@type sslVersion: strconstant

		@param checkCert: SutAdapters.SSL.CHECK_CERT_NO (default) | SutAdapters.SSL.CHECK_CERT_OPTIONAL | SutAdapters.SSL.CHECK_CERT_REQUIRED
		@type checkCert: strconstant
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																										debug=debug, shared=shared,
																										realname=name, 
																										agentSupport=agentSupport, agent=agent,
																										caller=TestAdapterLib.caller(),
																										agentType=AGENT_TYPE_EXPECTED)
		self.transport = transport
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.modeSniffer = sniffer
		self.ready = False

		# init tcp or udp layer
		if self.transport == AdapterTCP.PROTOCOL_TCP:
			self.tcp = AdapterTCP.Client(parent=parent, bindIp = bindIp, bindPort=bindPort, 
																			destinationIp=destIp, destinationPort=destPort,  destinationHost=proxyHost, 
																			socketTimeout=socketTimeout, socketFamily=socketFamily, inactivityTimeout=0, 
																			separatorDisabled=True, name=name,
																			sslSupport=sslSupport, sslVersion=sslVersion, checkCert=checkCert,
																			debug=debug, logEventSent=False, logEventReceived=False,
																			parentName=__NAME__, agentSupport=agentSupport, agent=agent, shared=shared)
			# callback tcp
			self.tcp.handleIncomingData = self.onIncomingData	
			self.tcp.handleNoMoreData = self.onNoMoreData
			# inherent tcp functions
			self.connect = self.tcp.connect
			self.isConnected = self.tcp.isConnected
			self.isConnectedSsl = self.tcp.isConnectedSsl
			self.disconnect = self.tcp.disconnect
			self.isDisconnected = self.tcp.isDisconnected
			self.hasReceivedData = self.tcp.hasReceivedData
			self.sendData = self.tcp.sendData
		elif self.transport == AdapterUDP.PROTOCOL_UDP:
			self.udp = AdapterUDP.Client(parent=parent, bindIp = bindIp, bindPort=bindPort, 
																			destinationIp=destIp, destinationPort=destPort,  destinationHost=proxyHost, 
																			socketFamily=socketFamily, separatorDisabled=True, 
																			debug=debug, logEventSent=False, logEventReceived=False,
																			parentName=__NAME__, agentSupport=agentSupport, agent=agent,
																			shared=shared, name=name )
			if self.modeSniffer:
				self.udp = AdapterUDP.Sniffer(parent=parent, debug=debug, logEventSent=False, logEventReceived=False, 
																				ipVersion=4, port2sniff=bindPort, separatorIn='0x00', separatorOut='0x00',
																				separatorDisabled=True, inactivityTimeout=0.0,  parentName=__NAME__,
																				agentSupport=agentSupport, agent=agent, shared=shared, name=name )
			# callback udp
			self.udp.handleIncomingData = self.onIncomingData
			# inherent udp functions
			self.startListening = self.udp.startListening
			self.stopListening = self.udp.stopListening
			self.sendData = self.udp.sendData
			self.isStopped = self.udp.isStopped
			if self.modeSniffer:
				self.isSniffing = self.udp.isSniffing
			else:
				self.isListening = self.udp.isListening
			self.hasReceivedData = self.udp.hasReceivedData
		else:
			raise Exception( 'transport type not supported: %s' % self.preferredTransport )
		
		# sip options
		self.cfg = {}	
		# to sniff
		self.cfg['bind-eth'] = bindEth
		# ip layer
		self.cfg['sip-source-ip'] = bindIp
		self.cfg['sip-source-port'] = int(bindPort)
		self.cfg['sip-destination-ip'] = destIp
		self.cfg['sip-destination-port'] = int(destPort)
		
		# sip params
		self.cfg['sip-version'] = sipVersion
		self.cfg['sip-agent'] = sipAgent
		self.cfg['sip-max-forwards'] = sipMaxForwards
		self.cfg['sip-rport'] = sipRport
		self.cfg['sip-initial-cseq'] = sipInitialCseq
		self.cfg['sip-allow'] = [ 'SUBSCRIBE', 'NOTIFY', 'PRACK', 'INVITE', 'ACK', 'BYE', 'CANCEL', 'UPDATE', 'MESSAGE', 'REFER' ]
		self.cfg['sip-domain'] = sipDomain
		self.cfg['sip-puid'] = sipPuid
		self.cfg['sip-display-name'] = sipDisplayName

		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent-name'] = agent['name']
		
		self.localCseq = 0
		self.localTag = None
		self.remoteTag = None
		self.localBranch = None
		self.localUri = None
		self.remoteUri = None
		self.routeSet = None
		self.remoteTarget = None
		
		self.__checkConfig()
		
		# init the SDP encoder
		self.sdpCodec = LibrarySDP.SDP(parent=parent, debug=debug)
		
		# init the SIP encoder/decoder 
		self.sipCodec = codec.Codec(parent=self)
		self.buf = ''

	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)
		try:
			self.localCseq = int(self.cfg['sip-initial-cseq'])
		except Exception as e:
			raise Exception('unable to init local cseq: %s' % str(e) )
	
	def __getLayer4Name(self):
		"""
		private function
		returns the transport protocol name
		"""
		if self.transport == AdapterTCP.PROTOCOL_TCP:
			return 'TCP'
		if self.transport == AdapterUDP.PROTOCOL_UDP:
			return 'UDP'

	def __request(self, fromHeader, toHeader, callId, via, cseq):
		"""
		private function
		"""
		hdrs = {
				"via": via,
				"from": fromHeader,
				"to": toHeader,
				"user-agent": self.cfg['sip-agent'],
				"call-id": callId,
				"max-forwards": str(self.cfg['sip-max-forwards']),
				"cseq": cseq,
				"allow": ', '.join(self.cfg['sip-allow'])
		}
		return hdrs 

	def __response(self, fromHeader, toHeader, callId, via, cseq):
		"""
		private function
		"""
		hdrs = {
				"via": via,
				"from": fromHeader,
				"to": toHeader,
				"call-id": callId,
				"user-agent": self.cfg['sip-agent'],
				"cseq": cseq,
				"allow": ', '.join(self.cfg['sip-allow'])
		}
		return hdrs 
		
	def __updateHdrs(self, currentHeaders, newHeaders):
		"""
		"""
		for key, value in newHeaders.items():
			key = key.lower()
			currentHeaders.update( {key:value} )

	def __addDisplayName(self, uri):
		"""
		"""
		if len(self.cfg['sip-display-name']):
			return '"%s" %s' % (self.cfg['sip-display-name'], uri)
		else:
			return uri
	def __incrementeCseq(self):
		"""
		"""
		self.localCseq += 1
		return self.localCseq
	def __setLocalTag(self):
		"""
		"""
		self.localTag = TAG() 
		
	def __setLocalBranch(self):
		"""
		"""
		self.localBranch = 'z9hG4bK%s' % BRANCH()
		
	def __setLocalUri(self):
		"""
		"""
		if len(self.cfg['sip-domain']):
			self.localUri = 'sip:%s@%s' % ( self.cfg['sip-puid'], self.cfg['sip-domain'] )	
		else:
			self.localUri = self.cfg['sip-puid']

	def __setRemoteUri(self, uri=None):
		"""
		"""
		if uri is None:
			self.remoteUri = 'sip:%s' % self.cfg['sip-domain']
		else:
			if '@' in uri:
				self.remoteUri = 'sip:%s' % uri
			else:
				self.remoteUri = 'sip:%s@%s' % (uri, self.cfg['sip-domain'])

		
	def __setRouteSet(self, routes):
		"""
		"""
		self.routeSet = routes
	
	def __setRemoteTarget(self, uri):
		"""
		"""
		self.remoteTarget = uri
		

	@doc_public
	def configure(self, puid=None, domain=None, displayName=None):
		"""
		Configure settings
		
		@param puid: puid name
		@type puid: string/none
		
		@param domain: domain name
		@type domain: string/none
		
		@param displayName: local display name
		@type displayName: string/none
		"""
		if puid is not None:
			self.cfg['sip-puid'] = puid
		if domain is not None:
			self.cfg['sip-domain'] = domain
		if displayName is not None:
			self.cfg['sip-display-name'] = displayName
			
	@doc_public
	def setSource(self, bindIp, bindPort):
		"""
		Set the source ip/port
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer
		"""
		if self.transport == AdapterTCP.PROTOCOL_TCP:
			self.tcp.setSource(bindIp=bindIp, bindPort=bindPort)
		if self.transport == AdapterUDP.PROTOCOL_UDP:
			self.udp.setSource(bindIp=bindIp, bindPort=bindPort)
	
	@doc_public
	def setDestination(self, destIp, destPort):
		"""
		Set the destination ip/port
		
		@param destIp: destination ip
		@type destIp: string

		@param destPort: destination port
		@type destPort: integer	
		"""
		if self.transport == AdapterTCP.PROTOCOL_TCP:
			self.tcp.setDestination(destinationIp=destIp, destinationPort=destPort)
		if self.transport == AdapterUDP.PROTOCOL_UDP:
			self.udp.setDestination(destinationIp=destIp, destinationPort=destPort)
			
	@doc_public
	def setLocalTag(self):
		"""
		Set the local tag
		"""
		self.__setLocalTag()
		
	@doc_public
	def setRemoteTag(self, fromhdr):
		"""
		Set the remote tag
		
		@param fromhdr: from header
		@type fromhdr: string	
		"""
		try:
			if ';tag=' in fromhdr:
				self.remoteTag = fromhdr.split(';tag=')[1].split(';')[0]
		except Exception as e:
			self.error( 'unable to extract tag in from: %s' % str(e) )	
			
	@doc_public
	def setRemoteUri(self, fromhdr):
		"""
		Set the remote uri
		
		@param fromhdr: from header
		@type fromhdr: string	
		"""
		try:
			sipuri = fromhdr.split('<')[1].split('>')[0]
			if sipuri.startswith( 'sip:' ):
				sipuri = sipuri[4:]
			self.__setRemoteUri(uri=sipuri)
		except Exception as e:
			self.error( 'unable to set remote uri: %s'  % str(e))	
		
	@doc_public
	def getRoutesAndRequestUri(self):
		"""
		"""
		if self.routeSet == None:
			requestUri = self.remoteTarget
			routes = None
		elif self.routeSet != None:
			if 'lr' in self.routeSet.get('0'):
				requestUri = self.remoteTarget
				routes = self.routeSet	
			else:
				requestUri = self.routeSet.get('0')
				# remove route one 
				self.routeSet.removeKey('0')
				self.routeSet.addKey(name="%s" % self.routeSet.getLenItems(), data=self.remoteTarget)
		return routes, requestUri	
		
	@doc_public
	def getRemoteUri(self):
		"""
		Returns the remote uri
		
		@return: remote uri
		@rtype:	string	
		"""
		return self.remoteUri
		
	@doc_public
	def getLocalTag(self):
		"""
		Returns the local tag
		
		@return: local tag
		@rtype:	string
		"""
		return self.localTag
		
	@doc_public
	def getLocalUri(self):
		"""
		Returns the local uri
		
		@return: local uri
		@rtype:	string	
		"""
		return self.localUri		
		
	@doc_public
	def getLocalCseq(self):
		"""
		Returns the local cseq
		
		@return: local cseq
		@rtype:	integer	
		"""
		return self.localCseq
	
	@doc_public
	def getLocalBranch(self):
		"""
		Returns the local branch
		
		@return: local branch
		@rtype:	string	
		"""
		return self.localBranch
		
	@doc_public
	def getSrcIP(self):
		"""
		Returns the source IP
		
		@return: source ip
		@rtype:	string	
		"""
		return self.cfg['sip-source-ip']
		
	@doc_public
	def getSrcPort(self):
		"""
		Returns the source port
		
		@return: source port
		@rtype:	integer	
		"""
		return self.cfg['sip-source-port']
		
	
	@doc_public
	def getFromHeader(self):
		"""
		Returns from header
		
		@return: from header
		@rtype:	string	
		"""
		if self.localUri is not None:
			if self.localTag is not None:
				f = '<' + self.localUri + '>;tag=' + self.localTag
			else:
				f = '<' + self.localUri + '>'
		else:
			f = '<undefined>'
		f = self.__addDisplayName(uri=f)
		return f
		
	@doc_public
	def getToHeader(self):
		"""
		Returns to header
		
		@return: to header
		@rtype:	string	
		"""
		if self.remoteUri is not None:
			if self.remoteTag is not None:
				to = '<' + self.remoteUri + '>;tag=' + self.remoteTag 
			else:
				to = '<' + self.remoteUri + '>'
		else:
			if self.localUri is not None:
				to = '<' + self.localUri + '>'
				to = self.__addDisplayName(uri=to)
			else:
				to = '<undefined>'
		return to
		
	def onReset(self):
		"""
		Reset
		"""
		if self.transport == AdapterTCP.PROTOCOL_TCP:
			self.disconnect()
		if self.transport == AdapterUDP.PROTOCOL_UDP:
			self.stopListening()
	
	def onIncomingData(self, data, lower):
		"""
		"""
		try:
			self.buf += data
			self.debug('data received (bytes %d), decoding attempt...' % len(self.buf))
			self.debug( data )
			(ret, decodedMessageTpl, summary, left) = self.sipCodec.decode(sip=self.buf)
			if ret == codec.DECODING_OK_CONTINUE:
				self.debug('decoding ok but several message received on the same message..')

				lowerCopy = copy.deepcopy( lower )
				# log event
				lower.addLayer(layer=decodedMessageTpl)
				self.buf = decodedMessageTpl.getRaw()
				self.onIncomingMessage(summary=summary, lower=lower)
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
				
				# add sip layer 
				decodedMessageTpl.addRaw(self.buf)
				lower.addLayer(layer=decodedMessageTpl)
				
				# decode sdp layer ? add it if detected
				sip_headers = decodedMessageTpl.get('headers')
				sip_body = decodedMessageTpl.get('body')
				sip_ct = sip_headers.get('content-type', caseSensitive=False)
				if sip_ct is not None:
					if sip_ct.lower() == "application/sdp":
						try:
							sdp_layer = self.sdpCodec.decode(sdp=sip_body)
							sdp_layer.addRaw( sip_body )
							lower.addLayer(sdp_layer)
						except Exception as e:
							raise Exception("sdp decode failed: %s" % str(e))	
				
				# log event 	
				if self.logEventReceived:
					if not self.modeSniffer:
						lower.addRaw(raw=self.buf) # add the raw message to the template						
					self.logRecvEvent( shortEvt = summary, tplEvt = lower )	
					
				# reset the buffer
				self.buf = ''	
		
				self.onIncomingMessage(summary=summary, lower=lower)
			else:  # should not be happen
				raise Exception('unknown decoding error')
		except Exception as e:
			self.error('Error while waiting for sip message: %s' % str(e))		

	def onIncomingMessage(self, summary, lower):
		"""
		Function to reimplement
		
		@param summary: message summary
		@type summary: string
		
		@param lower: sip request or status
		@type lower: templatemessage
		"""
		pass
		
	def onNoMoreData(self, lower):
		"""
		"""
		self.debug( 'not impletemented' )	

	def constructSipTemplate(self, rawSip):
		"""
		Construct a template request from the sip message passed on argument
		
		@param rawSip: sip
		@type rawSip: string		
		
		@return: the sip template layer
		@rtype: templatelayer
		"""
		try:
			rawSip = rawHttp.replace('\t', '')
			rawSip = rawSip.splitlines()
			rawSip = '\r\n'.join(rawSip)
			(ret, decodedMessageTpl, summary) = self.sipCodec.decode(sip=rawSip, nomoredata=True)
		except Exception as e:
			self.error('Error while constructing the template : %s' % str(e))		
		return decodedMessageTpl
	
			
	@doc_public
	def sendMessage(self, tpl):
		"""
		Send a sip message: request or status

		@param tpl: sip request or status
		@type tpl: templatelayer
		"""
		try:
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				# check the transport connection
				if not self.tcp.connected:
					raise Exception( 'transport tcp is not connected' )
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				# check the transport connection
				if not self.modeSniffer:
					if not self.udp.islistening:
						raise Exception( 'transport udp is not listening ' )
					
			# encode template
			try:
				(encodedMessage, summary) = self.sipCodec.encode(sip_tpl=tpl)
			except Exception as e:
				raise Exception("Cannot encode SIP message: %s" % str(e))	
			
			# Send message
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				try:
					lower = self.tcp.sendData( data=encodedMessage )
				except Exception as e:
					raise Exception("tcp failed: %s" % str(e))	
			
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				try:
					if self.modeSniffer:
						lower = self.udp.sendData( data=str(encodedMessage),
																				destIp=self.cfg['sip-destination-ip'], 
																				destPort=self.cfg['sip-destination-port']
																		)
					else:
						lower = self.udp.sendData( data=encodedMessage )
				except Exception as e:
					raise Exception("udp failed: %s" % str(e))	
					
			# add sip layer to the lower layer
			tpl.addRaw( encodedMessage )
			lower.addLayer( tpl )
			
			# decode sdp layer ? add it if detected
			sip_headers = tpl.get('headers')
			sip_body = tpl.get('body')
			sip_ct = sip_headers.get('content-type', caseSensitive=False)
			if sip_ct is not None:
				if sip_ct.lower() == "application/sdp":
					try:
						sdp_layer = self.sdpCodec.decode(sdp=sip_body)	
						sdp_layer.addRaw( sip_body )	
						lower.addLayer(sdp_layer)
					except Exception as e:
						raise Exception("sdp decode failed: %s" % str(e))	
			
			# Log event
			if self.logEventSent:
				if not self.modeSniffer:
					lower.addRaw(raw=encodedMessage)
				self.logSentEvent( shortEvt = summary, tplEvt = lower ) 
		except Exception as e:
			raise Exception('Unable to send SIP message: %s' % str(e))
		return lower

	@doc_public
	def hasReceivedMessage(self, expected, timeout=1.0):
		"""
		Wait response until the end of the timeout.
		
		@param expected: response template
		@type expected: templatemessage

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt
	
	@doc_public
	def hasReceivedResponse(self, timeout=1.0, sipCode="200", sipPhrase='OK', sipVersion='SIP/2.0', callId=None,
														tagFrom=None, tagTo=None, cseq=None, branchVia=None, expectedHeaders=None, body=None,
														versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Wait sip response until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param sipCode: sip code (default=200)
		@type sipCode: string/operators/none	
		
		@param sipPhrase: sip phrase (default=OK)
		@type sipPhrase: string/operators/none	
		
		@param sipVersion: sip version (default=SIP/2.0)
		@type sipVersion: string/operators/none	
		
		@param callId: 
		@type callId: string/operators/none	
		
		@param tagFrom: 
		@type tagFrom: string/operators/none	
		
		@param tagTo: 
		@type tagTo: string/operators/none	
		
		@param cseq: 
		@type cseq: string/operators/none	
		
		@param branchVia: 
		@type branchVia: string/operators/none	
		
		@param expectedHeaders: 
		@type expectedHeaders: string/operators/none	
		
		@param body: 
		@type body: string/operators/none
		
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
		
		@return: sip status response
		@rtype:	template	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# prepare expected template
		tpl = TestTemplatesLib.TemplateMessage()
		
		if self.modeSniffer:
			if AdapterEthernet is None: raise Exception('Ethernet Adapter not activated')
			ether_tpl = AdapterEthernet.ethernet()
			tpl.addLayer(ether_tpl)
			
			ip_tpl = AdapterIP.ip(source=sourceIp, destination=destinationIp)
			tpl.addLayer(ip_tpl)
			
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				pass
				
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				udp_tpl = AdapterUDP.udp(source=sourcePort, destination=destinationPort)
				tpl.addLayer(udp_tpl)
		else:
			
			# ip layer
			tpl.addLayer( AdapterIP.ip( source=sourceIp, destination=destinationIp, version=versionIp, more=AdapterIP.received() ) )
			# transport layer (tcp or udp)
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				tpl.addLayer(  AdapterTCP.tcp(source=sourcePort, destination=destinationPort, more=AdapterTCP.received()) )
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				tpl.addLayer(  AdapterUDP.udp(source=sourcePort, destination=destinationPort, more=AdapterUDP.received()) )
		
		# sip layer
		__hdrs = {}
		if callId is not None:
			__hdrs['call-id'] = callId
		if cseq is not None:
			__hdrs['cseq'] = cseq
		if branchVia is not None:
			__hdrs['via'] = TestOperatorsLib.Contains(needle=';branch=%s' % branchVia)
		if tagFrom is not None:
			__hdrs['from'] = TestOperatorsLib.Contains(needle=';tag=%s' % tagFrom)
		if tagTo is not None:
			__hdrs['to'] = TestOperatorsLib.Contains(needle=';tag=%s' % tagTo)
		if expectedHeaders is not None:
			__hdrs.update(expectedHeaders)
		tpl.addLayer( templates.status( version=sipVersion, code=sipCode, phrase=sipPhrase, headers=__hdrs, body=body) )
		
		# try to match
		return self.hasReceivedMessage(expected=tpl, timeout=timeout)
	@doc_public
	def hasReceivedRequest(self, timeout=1.0, sipMethod='INVITE', sipUri='sip:undefined', sipVersion='SIP/2.0', callId=None,
														tagFrom=None, tagTo=None, cseq=None, branchVia=None, expectedHeaders=None, body=None,
														versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Wait sip response until the end of the timeout.
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
		
		@param sipMethod: sip code (default=INVITE)
		@type sipMethod: string/operators/none	
		
		@param sipUri: sip phrase (default=sip:undefined)
		@type sipUri: string/operators/none	
		
		@param sipVersion: sip version (default=SIP/2.0)
		@type sipVersion: string/operators/none	

		@param callId: 
		@type callId: string/operators/none	
		
		@param tagFrom: 
		@type tagFrom: string/operators/none	
		
		@param tagTo: 
		@type tagTo: string/operators/none	
		
		@param cseq: 
		@type cseq: string/operators/none	
		
		@param branchVia: 
		@type branchVia: string/operators/none	
		
		@param expectedHeaders: 
		@type expectedHeaders: string/operators/none	
		
		@param body: 
		@type body: string/operators/none
		
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
		
		@return: sip request
		@rtype:	template	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# prepare expected template
		tpl = TestTemplatesLib.TemplateMessage()
		
		if self.modeSniffer:
			ether_tpl = AdapterEthernet.ethernet()
			tpl.addLayer(ether_tpl)
			
			ip_tpl = AdapterIP.ip(source=sourceIp, destination=destinationIp)
			tpl.addLayer(ip_tpl)
			
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				pass
				
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				udp_tpl = AdapterUDP.udp(source=sourcePort, destination=destinationPort)
				tpl.addLayer(udp_tpl)
		else:
			
			# ip layer
			tpl.addLayer( AdapterIP.ip( source=sourceIp, destination=destinationIp, version=versionIp, more=AdapterIP.received() ) )
			# transport layer (tcp or udp)
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				tpl.addLayer(  AdapterTCP.tcp(source=sourcePort, destination=destinationPort, more=AdapterTCP.received()) )
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				tpl.addLayer(  AdapterUDP.udp(source=sourcePort, destination=destinationPort, more=AdapterUDP.received()) )
			
		# sip layer
		__hdrs = {}
		if callId is not None:
			__hdrs['call-id'] = callId
		if cseq is not None:
			__hdrs['cseq'] = cseq
		if branchVia is not None:
			__hdrs['via'] = TestOperatorsLib.Contains(needle=';branch=%s' % branchVia)
		if tagFrom is not None:
			__hdrs['from'] = TestOperatorsLib.Contains(needle=';tag=%s' % tagFrom)
		if tagTo is not None:
			__hdrs['to'] = TestOperatorsLib.Contains(needle=';tag=%s' % tagTo)
		if expectedHeaders is not None:
			__hdrs.update(expectedHeaders)
		tpl.addLayer( templates.request( version=sipVersion, methord=sipMethod, uri=sipUri, headers=__hdrs, body=body) )
		
		# try to match
		return self.hasReceivedMessage(expected=tpl, timeout=timeout)		
	
	def decodeHeader_To(self, to):
		"""
		"""
		try:
			if ';tag=' in to:
				self.remoteTag = to.split(';tag=')[1].split(';')[0]
		except Exception as e:
			self.error( 'unable to extract tag in to')	
	def decodeHeader_RecordRoute(self, recordRoute, reverseRoute=True):
		"""
		"""
		if isinstance(recordRoute, TestTemplatesLib.TemplateLayer):
			recordRoutes = recordRoute.getItems()
			recordRoutes.sort()
		else:
			recordRoutes = recordRoute.split(',')
			
		if reverseRoute:
			recordRoutes.reverse()
			
		routes  = TestTemplatesLib.TemplateLayer('')
		for r in recordRoutes:
			if isinstance( r, tuple):
				k, v = r
			else:
				v = r
			routes.addKey(name="%s" % routes.getLenItems(), data=v)

		self.__setRouteSet(routes=routes)
		return routes
		
	def decodeHeader_Contact(self, contact):
		"""
		"""
		contact_unq = UNQ_URI( contact )
		self.__setRemoteTarget(uri=contact_unq)
		return contact_unq
		
	def initialize(self, timeout=1.0):
		"""
		Initialize. Connect to the SUT on tcp transport or just listen for udp
		
		@param timeout: time max to wait to receive event in second (default value=1s)
		@type timeout: float
	
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		try:
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				self.connect()	
				isConnected = self.isConnected( timeout=timeout )
				if isConnected is None:
					return None
				else:
					self.cfg['sip-source-ip'] =  isConnected.get('IP4', 'destination-ip').getName() 
					dst_port = isConnected.get('TCP', 'destination-port')
					if isinstance(dst_port, TestTemplatesLib.TemplateLayer):
						dst_port = dst_port.getName()
					self.cfg['sip-source-port'] =  dst_port
					self.onReady()
					return isConnected
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				# start the sniffer adapter
				if self.modeSniffer:
					self.startListening(eth=self.cfg['bind-eth'], srcIp=self.cfg['sip-source-ip'])	
					isSniffing = self.isSniffing( timeout=timeout )
					if isSniffing is None:
						return None
					else:
						self.onReady()
						return isSniffing
				else:
					# start the client adapter
					self.startListening()	
					isListening = self.isListening( timeout=timeout )
					if isListening is None:
						return None
					else:
						self.cfg['sip-source-ip'] =  isListening.get('IP4', 'source-ip').getName() 
						src_port = isListening.get('UDP', 'source-port')
						if isinstance(src_port, TestTemplatesLib.TemplateLayer):
							src_port = src_port.getName()
						self.cfg['sip-source-port'] =  src_port
						self.onReady()
						return isListening
		except Exception as e:
			self.error( 'unable to initialize: %s' % str(e) )
			
	def finalize(self, timeout=1.0):
		"""
		Finalize. Disconnect from the SUT or stop listening on udp.
		
		@param timeout: time max to wait to receive event in second (default value=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		try:
			self.ready = False
			if self.transport == AdapterTCP.PROTOCOL_TCP:
				self.disconnect()	
				isDisconnected = self.isDisconnected( timeout=timeout )
				return isDisconnected
			if self.transport == AdapterUDP.PROTOCOL_UDP:
				self.stopListening()	
				isStopped = self.isStopped( timeout=timeout )		
				return isStopped
		except Exception as e:
			self.error( 'unable to finalize: %s' % str(e) )
	
	def onReady(self):
		"""
		"""
		self.debug( "ready" )
		self.ready = True

	def getContact(self):
		"""
		"""
		contact = '<sip:%s@%s:%s>' % ( self.cfg['sip-puid'], 
																		self.cfg['sip-source-ip'], self.cfg['sip-source-port'] )
		return contact

	def getVia(self, branch):
		"""
		"""
		via = [ '%s/%s ' % (self.cfg['sip-version'], self.__getLayer4Name()) ]
		via.append( '%s:%s' % (self.cfg['sip-source-ip'], self.cfg['sip-source-port']) )
		if self.cfg['sip-rport']:
			via.append( ';rport' )
		
		via.append( ';branch=%s' % branch )
		return ''.join(via)

	@doc_public
	def CANCEL(self, callId, cseq, requestUri=None, toHeader=None, fromHeader=None, via=None, headers={}, send=True ):
		"""
		Send CANCEL to the SUT 

		@param callId: call id
		@type callId: string
		
		@param requestUri: request uri
		@type requestUri: string/none
		
		@param via: via header
		@type via: string/none
		
		@param toHeader: header to
		@type toHeader: string/none
		
		@param fromHeader: header from
		@type fromHeader: string/none
		
		@param headers: additional headers
		@type headers: dict
		
		@param send: send request (default=True)
		@type send: boolean
		
		@return: template message
		@rtype: templatemessage
		"""
		# not ready then exit
		if not self.ready:
			self.debug( 'initialize the sip adapter in first')
			return
		
		# init 
		body = None
		if via is None: self.__setLocalBranch()
			
		# prepare headers
		cseq = "%s CANCEL" % cseq
		if via is None: via = self.getVia(branch=self.localBranch)
		if fromHeader is None: fromHeader = self.getFromHeader()
		if toHeader is None: toHeader = self.getToHeader()
		if requestUri is None:
			routes, requestUri = self.getRoutesAndRequestUri()	
		else:
			routes = None
		hdrs = self.__request( fromHeader=fromHeader, toHeader=toHeader, callId=callId, via=via, cseq=cseq )
		
		# add headers specific to the CANCEL
		hdrs['content-length'] =  '0'
		hdrs['contact'] = self.getContact()
		
		# add additional headers and overwrite others
		try:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders=headers)
		except Exception as e:
			self.error( 'unable to update headers: %s' % str(e) )
		
		# add routes 
		if routes is not None:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders={"route": routes})
		
		if requestUri is None:
			self.debug( 'ack: request uri is none' )
			return None
			
		# create template and send it
		req_tpl = templates.request(method='CANCEL', uri=requestUri, version=self.cfg['sip-version'], headers=hdrs, body=body)
		if send:
			return self.sendMessage(tpl=req_tpl)
		else:
			return req_tpl
			
	@doc_public
	def ACK(self, callId, cseq, requestUri=None, toHeader=None, fromHeader=None, via=None, headers={}, sdp=None, send=True ):
		"""
		Send ACK to the SUT 

		@param callId: call id
		@type callId: string
		
		@param requestUri: request uri
		@type requestUri: string/none
		
		@param via: via header
		@type via: string/none
		
		@param toHeader: header to
		@type toHeader: string/none
		
		@param fromHeader: header from
		@type fromHeader: string/none
		
		@param headers: additional headers
		@type headers: dict
		
		@param sdp: sdp offer
		@type sdp: string/none
		
		@param send: send request (default=True)
		@type send: boolean
		
		@return: template message
		@rtype: templatemessage
		"""
		# not ready then exit
		if not self.ready:
			self.debug( 'initialize the sip adapter in first')
			return
		
		# init 
		body = None
		if via is None: self.__setLocalBranch()
			
		# prepare headers
		cseq = "%s ACK" % cseq
		if via is None: via = self.getVia(branch=self.localBranch)
		if fromHeader is None: fromHeader = self.getFromHeader()
		if toHeader is None: toHeader = self.getToHeader()
		if requestUri is None:
			routes, requestUri = self.getRoutesAndRequestUri()	
		else:
			routes = None
		hdrs = self.__request( fromHeader=fromHeader, toHeader=toHeader, callId=callId, via=via, cseq=cseq )
		
		# add headers specific to the ACK
		if sdp is not None:
			hdrs['content-type'] = 'application/sdp'
			hdrs['content-length'] = str(len(sdp))
			body = sdp
		else:
			hdrs['content-length'] =  '0'
		hdrs['contact'] = self.getContact()
		
		# add additional headers and overwrite others
		try:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders=headers)
		except Exception as e:
			self.error( 'unable to update headers: %s' % str(e) )
		
		# add routes 
		if routes is not None:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders={"route": routes})
		
		if requestUri is None:
			self.debug( 'ack: request uri is none' )
			return None
			
		# create template and send it
		req_tpl = templates.request(method='ACK', uri=requestUri, version=self.cfg['sip-version'], headers=hdrs, body=body)
		if send:
			return self.sendMessage(tpl=req_tpl)
		else:
			return req_tpl
	@doc_public
	def BYE(self, callId, requestUri=None, headers={}, send=True ):
		"""
		Send BYE to the SUT 
		
		@param requestUri: request uri
		@type requestUri: string/none
		
		@param callId: call id
		@type callId: string
		
		@param headers: additional headers
		@type headers: dict
		
		@param send: send request (default=True)
		@type send: boolean
		
		@return: template message
		@rtype: templatemessage
		"""
		# not ready then exit
		if not self.ready:
			self.debug( 'initialize the sip adapter in first')
			return
		
		# init
		self.__incrementeCseq()
		self.__setLocalBranch()
		
		# prepare headers
		cseq = "%s BYE" % self.localCseq
		fromHeader = self.getFromHeader()
		toHeader = self.getToHeader()
		via = self.getVia(branch=self.localBranch)
		if requestUri is None:
			routes, requestUri = self.getRoutesAndRequestUri()	
		else:
			routes = None
		hdrs = self.__request( fromHeader=fromHeader, toHeader=toHeader, callId=callId, via=via, cseq=cseq )
		
		# add headers specific to the BYE
		hdrs['content-length'] =  '0'
		hdrs['contact'] = self.getContact()
		
		# add additional headers and overwrite others
		try:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders=headers)
		except Exception as e:
			self.error( 'unable to update headers: %s' % str(e) )
		
		# add routes 
		if routes is not None:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders={"route": routes})
		
		if requestUri is None:
			self.debug( 'bye: request uri is none' )
			return None
			
		# create template and send it
		req_tpl = templates.request(method='BYE', uri=requestUri, version=self.cfg['sip-version'], headers=hdrs, body=None)
		if send:
			return self.sendMessage(tpl=req_tpl)
		else:
			return req_tpl
		
	@doc_public
	def INVITE(self, requestUri, callId, headers={}, sdp=None, send=True ):
		"""
		Send INVITE to the SUT 
		
		@param requestUri: request uri
		@type requestUri: string
		
		@param callId: call id
		@type callId: string
		
		@param headers: additional headers
		@type headers: dict
		
		@param sdp: sdp offer
		@type sdp: string/none
		
		@param send: send request (default=True)
		@type send: boolean
		
		@return: template message
		@rtype: templatemessage
		"""
		# not ready then exit
		if not self.ready:
			self.debug( 'initialize the sip adapter in first')
			return
		
		# init
		self.__setLocalBranch()
		self.__setLocalTag()
		self.__incrementeCseq()
		self.__setLocalUri()
		self.__setRemoteUri(uri=requestUri)
#		self.__setRemoteTarget(uri=requestUri)
		body = None
		
		# prepare headers
		cseq = "%s INVITE" % self.localCseq
		fromHeader = self.getFromHeader()
		toHeader = self.getToHeader()
		via = self.getVia(branch=self.localBranch)
		hdrs = self.__request( fromHeader=fromHeader, toHeader=toHeader, callId=callId, via=via, cseq=cseq )
		
		# add headers specific to the INVITE
		if sdp is not None:
			hdrs['content-type'] = 'application/sdp'
			hdrs['content-length'] = str(len(sdp))
			body = sdp
		else:
			hdrs['content-length'] =  '0'
		hdrs['contact'] = self.getContact()
		
		# add additional headers and overwrite others
		try:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders=headers)
		except Exception as e:
			self.error( 'unable to update headers: %s' % str(e) )
		
		# create template and send it
		req_tpl = templates.request(method='INVITE', uri=self.getRemoteUri(), version=self.cfg['sip-version'], headers=hdrs, body=body)
		if send:
			return self.sendMessage(tpl=req_tpl)
		else:
			return req_tpl
	@doc_public
	def REGISTER(self, callId, expires=300, headers={}, send=True ):
		"""
		Send REGISTER to the SUT 
		
		@param callId: call id
		@type callId: string
		
		@param expires: registration interval
		@type expires: integer
		
		@param headers: additional headers
		@type headers: dict
		
		@param send: send request (default=True)
		@type send: boolean
		
		@return: template message
		@rtype: templatemessage
		"""
		# not ready then exit
		if not self.ready:
			self.debug( 'initialize the sip adapter in first')
			return
		
		# init
		self.remoteUri = None
		self.remoteTag = None
		self.__setLocalBranch()
		self.__setLocalTag()
		self.__incrementeCseq()
		self.__setLocalUri()
		self.__setRemoteUri()
		
		# prepare headers
		cseq = "%s REGISTER" % self.localCseq
		fromHeader = self.getFromHeader()
		toHeader = '<%s>' % self.localUri
		via = self.getVia(branch=self.localBranch)
		hdrs = self.__request( fromHeader=fromHeader, toHeader=toHeader, callId=callId, via=via, cseq=cseq )
		
		# add headers specific to the REGISTER
		hdrs['expires'] = str(expires)
		hdrs['contact'] = self.getContact()
		hdrs['content-length'] =  '0'

		# add additional headers and overwrite others
		try:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders=headers)
		except Exception as e:
			self.error( 'unable to update headers: %s' % str(e) )
			
		# create template and send it
		req_tpl = templates.request(method='REGISTER', uri=self.getRemoteUri(), version=self.cfg['sip-version'], headers=hdrs, body=None)
		if send:
			return self.sendMessage(tpl=req_tpl)
		else:
			return req_tpl
	@doc_public
	def Status(self, code, phrase, fromHeader, toHeader, callId, via, cseq, sdp=None, headers={}, send=True ):
		"""
		Send status response to the SUT 
		
		@param code: response code
		@type code: string
		
		@param phrase: response phrase
		@type phrase: string
		
		@param toHeader: header to
		@type toHeader: string
		
		@param fromHeader: header from
		@type fromHeader: string
		
		@param callId: call id
		@type callId: string

		@param via: via header
		@type via: string
		
		@param cseq: cseq header
		@type cseq: string
		
		@param sdp: sdp offer/answer
		@type sdp: string/none
		
		@param headers: additional headers
		@type headers: dict
		
		@param send: send response (default=True)
		@type send: boolean
		
		@return:  template message
		@rtype: templatemessage
		"""
		# not ready then exit
		if not self.ready:
			self.debug( 'initialize the sip adapter in first')
			return
		
		body = None
		hdrs = self.__response( fromHeader=fromHeader, toHeader=toHeader, callId=callId, via=via, cseq=cseq )
		
		if sdp is not None:
			hdrs['content-type'] = 'application/sdp'
			hdrs['content-length'] = str(len(sdp))
			body = sdp
		else:
			hdrs['content-length'] =  '0'
		hdrs['contact'] = self.getContact()
		
		# add additional headers and overwrite others
		try:
			self.__updateHdrs(currentHeaders=hdrs, newHeaders=headers)
		except Exception as e:
			self.error( 'unable to update headers: %s' % str(e) )
		
		# create template and send it
		req_tpl = templates.status(code=code, phrase=phrase, version=self.cfg['sip-version'], headers=hdrs, body=body)
		if send:
			return self.sendMessage(tpl=req_tpl)
		else:
			return req_tpl