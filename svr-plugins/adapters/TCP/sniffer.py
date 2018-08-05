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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

AdapterEthernet = sys.modules['SutAdapters.%s.Ethernet' % TestAdapterLib.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IP' % TestAdapterLib.getVersion()]

try:
	import client
	import codec
	import templates
except ImportError: # python3 support
	from . import client
	from . import codec
	from . import templates

import struct
import time

AGENT_TYPE_EXPECTED='socket'

class Sniffer(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, debug=False, logEventSent=True, logEventReceived=True, name=None,
								ipVersion=AdapterIP.IPv4, port2sniff=codec.ALL, parentName=None, inactivityTimeout=0.0,
								separatorIn='0x00', separatorOut='0x00', separatorDisabled=True, agentSupport=False, 
								agent=None, shared=False):
		"""
		This class enables to send/receive TCP data.
		The lower layer is based on the IP adapter.
		Support data separator for upper application, tcp options supported.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		
		@param separatorIn: data separator (default=0x00)
		@type separatorIn: string
		
		@param port2sniff: udp port to sniff
		@type port2sniff: integer

		@param separatorOut: data separator (default=0x00)
		@type separatorOut: string

		@param separatorDisabled: disable the separator feature, if this feature is enabled then data are buffered until the detection of the separator (default=False)
		@type separatorDisabled: boolean
		
		@param inactivityTimeout: feature disabled by default (value=0.0)
		@type inactivityTimeout: float

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = client.__NAME__, parent = parent, 
																									debug=debug, realname=name,
																									shared=shared, agentSupport=agentSupport, agent=agent,
																									caller=TestAdapterLib.caller(),
																									agentType=AGENT_TYPE_EXPECTED)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		# tcp codec
		self.tcpCodec = codec.Codec(parent=self, testcase=parent, debug=debug, srcPort=port2sniff)
		
		# ip layer
		self.ip = AdapterIP.SnifferV4(parent=parent, debug=debug, protocol2sniff=AdapterIP.TCP,
																	logEventSent=False, logEventReceived=False,
																	parentName=client.__NAME__, agentSupport=agentSupport, 
																	agent=agent, shared=shared)
		if parentName is not None:
			self.ip.setname(name="%s>%s" % (parentName,client.__NAME__))
		self.ip.onReceiving = self.onDecodeData
		
		self.cfg = {}
		self.cfg['port-to-sniff'] = port2sniff
		self.cfg['ip-version'] = ipVersion
		self.cfg['sep-in'] = separatorIn
		self.cfg['sep-out'] = separatorOut
		self.cfg['sep-disabled'] = separatorDisabled
		self.cfg['inactivity-timeout'] = inactivityTimeout
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']		
		self.__checkConfig()
		
		self.buf = {}

	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)

	def setPort2Sniff(self, port):
		"""
		Define the local port to sniff
		
		@param port: port to sniff
		@type port: integer
		"""
		self.cfg['port-to-sniff']= port
		
	def encapsule(self, layer):
		"""
		"""
		# prepare template
		tpl = TestTemplatesLib.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer(layer=layer)
		return tpl
		
	def onReset(self):
		"""
		Reset
		"""
		self.stopListening()

	def onDecodeData(self, data, lower=None):
		"""
		"""
		try:
			# extract source and destination IP
			src_ip = lower.get('IP4', 'source-ip')
			if isinstance(src_ip, TestTemplatesLib.TemplateLayer):
				src_ip = src_ip.getName()
			dst_ip = lower.get('IP4', 'destination-ip')
			if isinstance(dst_ip, TestTemplatesLib.TemplateLayer):
				dst_ip = dst_ip.getName()
		except Exception as e:
			self.error( "ip level info extraction failed: %s" % str(e) )
		else:
			self.debug ( 'ip level info extracted' )
		
		# try to decode the udp payload
		try:
			tcp_tpl, summary, data_upper = self.tcpCodec.decode(tcp=data, ipSrc=src_ip, ipDst=dst_ip)
			if isinstance(tcp_tpl.get('destination-port'), TestTemplatesLib.TemplateLayer):
				dst_port = tcp_tpl.get('destination-port').getName()
			else:
				dst_port = tcp_tpl.get('destination-port')
			if isinstance(tcp_tpl.get('source-port'), TestTemplatesLib.TemplateLayer):
				src_port = tcp_tpl.get('source-port').getName()
			else:
				src_port = tcp_tpl.get('source-port')
			fromAddr = ( src_ip, int(src_port) )
			toAddr = ( dst_ip, int(dst_port) )
		except Exception as e:
			self.error( "Cannot decode the tcp payload: %s" % str(e) )	
		
		# decode OK, we continue
		else:
			self.debug ( 'decode OK, we continue' )
			try:
				lower.addLayer( tcp_tpl )
			except Exception as e:
				self.error( "add layer failed: %s" % str(e) )
			else:
				self.debug ( 'upper layer added' )
			
			try:
				# log this event
				if self.cfg['port-to-sniff']== codec.ALL:
					if self.logEventReceived: 
						self.logRecvEvent( shortEvt = summary, tplEvt = lower )
					try:
						self.onReceiving(data=data_upper, lower=lower, fromAddr=fromAddr, toAddr=toAddr)
					except Exception as e:
						self.error( "on receiving all tcp: %s" % str(e) )
				else:
					if self.cfg['port-to-sniff']== int(dst_port):
						if self.logEventReceived: 
							self.logRecvEvent( shortEvt = summary, tplEvt = lower )
						try:
							self.onReceiving(data=data_upper, lower=lower, fromAddr=fromAddr, toAddr=toAddr)
						except Exception as e:
							self.error( "on receiving tcp: %s" % str(e) )
					else:
						self.debug( 'discarding packet, not for me' )
			except Exception as e:
				self.error( "on logging event tcp: %s" % str(e) )
		
	def onReceiving(self, data, fromAddr, toAddr, lower):
		"""
		Function to overwrite
		Called on incoming data

		@param data: data received
		@type data: string
		
		@param lower: template data received
		@type lower: templatemessage
		"""
		# extract transport info
		self.lastActivity = time.time()
		srcIp, srcPort = fromAddr
		dstIp, dstPort = toAddr
		
		# the separator feature is disabled, to nothing
		if self.cfg['sep-disabled']:
			try:
				self.handleIncomingData(data=data, lower=lower, fromAddr=fromAddr, toAddr=toAddr)
			except Exception as e:
				self.error( "on handle incoming tcp data, upper layer problem: %s" % str(e) )
		else:
			# bufferize data
			if self.buf.has_key(fromAddr):
				self.buf[fromAddr] = ''.join([self.buf[fromAddr], data])
			else:
				self.buf[fromAddr] = data
			
			# split data with the separator
			datas = self.buf[fromAddr].split(self.cfg['sep-in'])
			for d in datas[:-1]:
				tcp_data = d + self.cfg['sep-in']
				tcp_data_size = len(tcp_data)
				
				# construct high template and log it
				tpl = TestTemplatesLib.TemplateMessage()
				tpl.addLayer( layer=AdapterIP.ip( source=srcIp, destination=dstIp, more=AdapterIP.received(), version=self.cfg['ip-version'] ) )
				if self.logEventReceived: 
					tcp_layer = templates.tcp(source=srcPort, destination=dstPort, more=templates.received(data=tcp_data, data_length=str(tcp_data_size) ) )
				else:
					tcp_layer = templates.tcp(source=srcPort, destination=dstPort, more=templates.received(data_length=str(tcp_data_size) ) )
				tpl.addLayer( layer=tcp_layer )
				
				if self.logEventReceived: 
					tpl.addRaw(raw=tcp_data)
					self.logRecvEvent( shortEvt = 'data reassembled', tplEvt = tpl )
				
				# handle data
				self.handleIncomingData( tcp_data, lower=tpl, fromAddr=fromAddr, toAddr=toAddr)
			self.buf[fromAddr] = datas[-1]

	def handleIncomingData(self, data, lower, fromAddr, toAddr):
		"""
		Function to reimplement
		Called on incoming packet

		@param data: udp data received
		@type data: string
		
		@param lower: template udp data received
		@type lower: templatemessage
		"""
		pass	

	def onRun(self):
		"""
		"""
		if self.cfg['inactivity-timeout']:
			if time.time() - self.lastActivity > self.cfg['inactivity-timeout']:
				self.onInactivityTimeout()
				
	@doc_public
	def onInactivityTimeout(self):
		"""
		"""
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer( layer=AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( layer=templates.udp( more=templates.received() ) )
		self.onInactivity(lower=tpl)

	def onInactivity(self, lower):
		"""
		Function to reimplement
		"""
		pass
	
	def addSeparator(self, data):
		"""
		Add the separator to the end of the data, if the feature is enabled	
		"""
		if self.cfg['sep-disabled']:
			return data
		else:
			return  ''.join( [ data, struct.pack('!B', int( self.cfg['sep-out'], 16 ) ) ] )

	@doc_public
	def sendPacket(self, destIp=None, destPort=0, srcPort=0, seqNum='0x000', ackNum='0x0000', ctrlBits='0x000', 
										checksum=None, headerSize=None, tcpWin='0x0000', urgPtr='0x0000', data=None, destMac=None,
										options=None, optSegMax=None, optWinScale=None, optSackPermitted=None, optSack=None):
		"""
		Send TCP packet.
		
		@param data: tcp data to send
		@type data: none/string
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string/integer
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string/integer
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param headerSize: tcp header length in 32 bit words, auto computed if not provided
		@type headerSize: none/integer
		
		@param ctrlBits: control bits (default=0x000)
		@type ctrlBits: none/string
		
		@param win: tcp window (default=0x0000)
		@type win: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param options: raw tcp options 
		@type options: none/string
		
		@param optSegMax: tcp option, maximum segment size
		@type optSegMax: none/integer
		
		@param optWinScale: tcp option, window scale
		@type optWinScale: none/integer
		
		@param optSackPermitted: tcp option, sack permitted
		@type optSackPermitted: none/string
		
		@param optSack: tcp option, sack
		@type optSack: none/string
		"""
		try:
			if self.cfg['port-to-sniff']== codec.ALL:
				src_port = int(srcPort)
			else:
				src_port = int(self.cfg['port-to-sniff'])
			
			# add the separator 
			data = self.addSeparator(	data=data )
			# prepare tcp options
			if optSegMax is not None: options=''
			if optWinScale is not None: options=''
			if optSackPermitted is not None: options=''
			if optSack is not None: options=''
			
			# prepare the template
			layer_tcp = templates.tcp(source=srcPort, destination=destPort, seq_num=seqNum,  ack_num=ackNum,
																data=data, control_bits=ctrlBits, sum=checksum, urgent=urgPtr, window=tcpWin,
																data_offset=headerSize, options=options, opt_max_seg=optSegMax, opt_win_scale=optWinScale,
																opt_sack_permitted=optSackPermitted, opt_sack=optSack)
		except Exception as e:
			raise Exception('Cannot prepare tcp template: %s' % str(e))
		else:	
			# encode the template tcp		
			try:
				tcp_pkt, summary = self.tcpCodec.encode(tcp_tpl=layer_tcp, ipSrc=self.ip.getSourceIP(), ipDst=destIp)
			except Exception as e:
				raise Exception("Cannot encode tcp packet: %s" % str(e))		
			else:
				# Send packet	
				try:
					lower = self.ip.sendDatagram(dstMac=destMac, dstIp=destIp, data=tcp_pkt, protocol=AdapterIP.TCP)
				except Exception as e:
					raise Exception("Unable to send tcp data: %s" % str(e))	
				else:
					lower.addLayer( layer_tcp )
					if self.logEventSent:
						layer_tcp.addRaw(raw=tcp_pkt)
					else:
						layer_tcp.addRaw(raw=tcp_pkt[:codec.TCP_LEN])
					if self.logEventSent:
						self.logSentEvent( shortEvt = summary, tplEvt = lower ) 
						
	@doc_public
	def SYN(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None, optSegMax=None, optWinScale=None, optSackPermitted=None, optSack=None):
		"""
		Send a synchronize sequence numbers (SYN) packet.
		Checksum autocomputed.

		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		
		@param optSegMax: tcp option, maximum segment size
		@type optSegMax: none/integer
		
		@param optWinScale: tcp option, window scale
		@type optWinScale: none/integer
		
		@param optSackPermitted: tcp option, sack permitted
		@type optSackPermitted: none/string
		
		@param optSack: tcp option, sack
		@type optSack: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x002',
											options=options, optSegMax=optSegMax, optWinScale=optWinScale, optSackPermitted=optSackPermitted,
											optSack=optSack)

	@doc_public
	def SYN_ACK(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None, optSegMax=None, optWinScale=None, optSackPermitted=None, optSack=None):
		"""
		Send a synchronize sequence numbers (SYN) and an acknowledgment field significant (ACK) packet.
		Checksum autocomputed.

		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		
		@param optSegMax: tcp option, maximum segment size
		@type optSegMax: none/integer
		
		@param optWinScale: tcp option, window scale
		@type optWinScale: none/integer
		
		@param optSackPermitted: tcp option, sack permitted
		@type optSackPermitted: none/string
		
		@param optSack: tcp option, sack
		@type optSack: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x012',
											options=options, optSegMax=optSegMax, optWinScale=optWinScale, optSackPermitted=optSackPermitted,
											optSack=optSack)
											
	@doc_public
	def ACK(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send an acknowledgment field significant (ACK) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x010',
											options=options)
	
	@doc_public
	def RST(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send a reset the connection (RST) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x004', options=options)

	@doc_public
	def RST_ACK(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send a reset the connection (RST) and an acknowledgment field significant (ACK) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x014', options=options)
											
	@doc_public
	def FIN(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send a no more data from sender (FIN) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x001', options=options)
											

	@doc_public
	def FIN_ACK(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send a no more data from sender (FIN) and an acknowledgment field significant (ACK) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x011', options=options)
											
	@doc_public
	def PSH(self, data, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send a push Function (PSH) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x008',
											data=data, options=options)
		
	@doc_public
	def PSH_ACK(self, data, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send a push Function (PSH) and an acknowledgment field significant (ACK) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x018', 
											data=data, options=options)


	@doc_public
	def URG(self, destPort=0, srcPort=0, destIp=None, destMac=None, 
							seqNum='0x000', ackNum='0x0000', tcpWin='0x0000', urgPtr='0x0000',
							checksum=None, options=None):
		"""
		Send an urgent Pointer field significant (URG) packet.
		Checksum autocomputed.
		
		@param destPort: destination port
		@type destPort: integer
		
		@param srcPort: source port
		@type srcPort: integer
		
		@param destIp: destination ip address
		@type destIp: none/integer
		
		@param destMac: destination mac address
		@type destMac: none/integer
		
		@param seqNum: sequence number (default=0x0000)
		@type seqNum: string
		
		@param ackNum: acknowledge number (default=0x0000)
		@type ackNum: string
		
		@param tcpWin: tcp window (default=0x0000)
		@type tcpWin: string
		
		@param urgPtr: urgent pointer (default=0x0000)
		@type urgPtr: string
		
		@param checksum: checksum, auto computed if not provided 
		@type checksum: integer
		
		@param options: raw tcp options 
		@type options: none/string
		"""
		self.sendPacket(destPort=destPort, srcPort=srcPort, destIp=destIp, destMac=destMac,
											seqNum=seqNum, ackNum=ackNum, tcpWin=tcpWin, urgPtr=urgPtr, ctrlBits='0x020', options=options)
											
	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		# stop thread
		self.unsetRunning()
		
		self.ip.stopListening()
		
	
	@doc_public
	def startListening(self, eth, srcIp, srcMac=None ):
		"""
		Start listening
		
		@param eth: network interface identifier
		@type eth: string
		
		@param srcIp: source ip
		@type srcIp: string
		
		@param srcMac: source mac address
		@type srcMac: none/string
		"""
		self.ip.startListening(eth=eth, srcIp=srcIp, srcMac=srcMac)
		# start thread
		self.lastActivity = time.time()
		self.setRunning()
		
	@doc_public
	def isSniffing(self, timeout=1.0):
		"""
		Wait to receive "sniffing" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.ip.isSniffing(timeout=timeout)
		
	@doc_public
	def isStopped(self, timeout=1.0):
		"""
		Wait to receive "stopped" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.ip.isStopped(timeout=timeout)
		
	@doc_public
	def hasReceivedPacket(self, timeout=1.0, dstIp=None, srcIp=None, srcPort=None, dstPort=None, data=None, 
												controlBits=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float
		
		@param dstIp: destination ip
		@type dstIp: none/string/operators
		
		@param srcIp: source ip
		@type srcIp: none/string/operators
		
		@param srcPort: source port
		@type srcPort: none/integer/operators

		@param dstPort: destination port
		@type dstPort: none/integer/operators
		
		@param data: upper data
		@type data: none/string/operators
		
		@param controlBits: control bits
		@type controlBits: none/string/operators

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# prepare the expected template
		ether_tpl = AdapterEthernet.ethernet()
		expected = self.encapsule(layer=ether_tpl)
		
		ip_tpl = AdapterIP.ip(source=srcIp, destination=dstIp)
		expected.addLayer(ip_tpl)
		
		tcp_tpl = templates.tcp(source=srcPort, destination=dstPort, control_bits=controlBits)
		expected.addLayer(tcp_tpl)
		# wait 
		evt = self.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt