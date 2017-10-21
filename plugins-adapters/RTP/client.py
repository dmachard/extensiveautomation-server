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

SutLibraries = sys.modules['SutLibraries.%s' % TestLibraryLib.getVersion()]
MediaTools = sys.modules['SutLibraries.%s.Media' % TestLibraryLib.getVersion()]

import codec
import templates
import streamer 
import defaultpayloads

import os
import threading
import time
import random

# RFC 1889 - RTP: A Transport Protocol for Real-Time Applications

__NAME__="""RTP"""

SOUND_SINE_1K = 0
SOUND_WHITE_NOISE = 1
SOUND_SILENCE = 2

AGENT_TYPE_EXPECTED='socket'

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, debug=False, name=None,
						bindIp = '0.0.0.0', bindPort=0, destinationIp='', destinationHost='', destinationPort=0,
						socketFamily=AdapterIP.IPv4, logHighLevelEvents=True, logLowLevelEvents=False,
						recordRcvSound=False, recordSndSound=False, payloadType=SutLibraries.Codecs.A_G711U, defaultSound=SOUND_SINE_1K,
						rtpVersion=2, initialSeqNumber=None, ssrcValue=None, inactivityTimeout=2.0, sessionId=None,
						agentSupport=False, agent=None, shared=False):
		"""
		Raw RTP client. This class inherit from the UDP adapter.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param bindIp: bind on ip
		@type bindIp:	string
		
		@param bindPort: bind on port
		@type bindPort:	integer
		
		@param destinationIp: destination ip
		@type destinationIp: string
		
		@param destinationPort: destination port
		@type destinationPort: integer
		
		@param destinationHost: destination host
		@type destinationHost: string
		
		@param logHighLevelEvents: log high level events (default=True)
		@type logHighLevelEvents: boolean
		
		@param logLowLevelEvents: log low level events (default=False)
		@type logLowLevelEvents: boolean
		
		@param recordRcvSound: bufferize the sound received and save the RTP flow in a rtp file. If the codec is supported then the flow is saved in a wave file.
		@type recordRcvSound:	boolean
		
		@param recordSndSound: bufferize the sound sent and save the RTP flow in a rtp file. If the codec is supported then the flow is saved in a wave file.
		@type recordSndSound:	boolean
		
		@param payloadType: SutLibraries.Codecs.A_G711U (default) | SutLibraries.Codecs.A_G711A
		@type payloadType: intconstant		
		
		@param defaultSound: SutAdapters.RTP.SOUND_SINE_1K (default) | SutAdapters.RTP.SOUND_WHITE_NOISE | SutAdapters.RTP.SOUND_SILENCE
		@type defaultSound: intconstant
		
		@param rtpVersion: rtp version (default=2)
		@type rtpVersion:	integer
		
		@param initialSeqNumber: initial sequence number
		@type initialSeqNumber:	integer/none
		
		@param ssrcValue: ssrc
		@type ssrcValue: integer/none

		@param socketFamily: socket family
		@type socketFamily:	string
		
		@param sessionId: session identifier for high level events
		@type sessionId:	string/none
		
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared,
																	realname=name, agentSupport=agentSupport, agent=agent)
		self.logHighLevelEvents = logHighLevelEvents
		self.logLowLevelEvents = logLowLevelEvents	
		self.__testcase = parent
		self.__debugmode = debug
		
		# init udp layer
		self.udp = AdapterUDP.Client(parent=parent, debug=debug, name=name, 
											bindIp = bindIp, bindPort=bindPort, 
											destinationIp=destinationIp, destinationPort=destinationPort,  destinationHost=destinationHost, 
											socketFamily=socketFamily, separatorDisabled=True, inactivityTimeout=inactivityTimeout,
											logEventSent=False, logEventReceived=False, parentName=__NAME__, agentSupport=agentSupport,
											agent=agent, shared=shared)
		
		# callback udp
		self.udp.handleIncomingData = self.onIncomingData
		self.udp.preStopListening = self.stopSending
		self.udp.onInactivity = self.onInactivity
		# inherent udp functions
		self.startListening = self.udp.startListening
		self.sendData = self.udp.sendData
		self.isStopped = self.udp.isStopped
		self.isListening = self.udp.isListening
		self.hasReceivedData = self.udp.hasReceivedData
		self.setDestination = self.udp.setDestination
		self.setSource = self.udp.setSource
		
		# rtp options
		self.cfg = {}
		self.cfg['version-rtp'] = rtpVersion
		self.cfg['record-rcv-rtp'] = recordRcvSound
		self.cfg['record-snd-rtp'] = recordSndSound
		self.cfg['payload-type'] = payloadType
		self.cfg['default-sound'] = defaultSound
		self.cfg['framing-interval'] = float(0)
		self.cfg['initial-seq'] = initialSeqNumber	
		self.cfg['ssrc-chosen'] = ssrcValue
		self.cfg['session-id'] = sessionId
		# agent
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent-name'] = agent['name']
		
		# init the RTP encoder/decoder 
		self.rtpCodec = codec.Codec(parent=self)
		self.bufIn = ''
		self.bufOut = ''
		self.buf_AudioET = None # audio encoding type
		
		# sending thread init
		self.rtpStreamer = streamer.Streamer()
		self.defaultPayloads = defaultpayloads.DefaultPayloads(parent=parent, debug=debug)
		self.sendingThread = SendingThread(parent=self)
		self.sendingThread.start()
		
		# high events
		self.last_pkt_sent = None
		self.last_pkt_recv = None
		
		# check config
		self.__checkConfig()

	def testcase(self):
		"""
		"""
		return self.__testcase
		
	def debugmode(self):
		"""
		"""
		return self.__debugmode
		
	def __checkConfig(self):
		"""
		"""	
		# Set the initial value for the sequence number
		self.__setInitialSeq()
		# Set the initial value for the ssrc
		self.__setSsrc()
		# Set the default sound to play
		self.__setDefaultDataToStream()
		if self.cfg['agent-support'] :
			self.warning('Agent mode activated') 
			
	def __setSsrc(self):
		"""
		"""
		try:
			maxssrc = 0xFFFFFFFF
			if self.cfg['ssrc-chosen'] is None:
				# This identifier is chosen randomly
				self.cfg['ssrc-chosen'] = random.randint(0, maxssrc) 	
			else:
				self.cfg['ssrc-chosen'] = int( self.cfg['ssrc-chosen'] )
				if self.cfg['ssrc-chosen'] > maxseq:
					raise Exception( 'ssrc greater than 0xFFFFFFFF: %s' % self.cfg['ssrc-chosen'] )
					
			self.sendingThread.setInitialSsrc(ssrc=self.cfg['ssrc-chosen'])
		except Exception as e:
			self.error( 'failed to initialize the ssrc: %s' % str(e) )
			self.cfg['ssrc-chosen'] = 0
			
	def __setInitialSeq(self):
		"""
		"""
		try:
			maxseq = 0xFFFF
			if self.cfg['initial-seq'] is None:
				# The initial value of the sequence number is random
				self.cfg['initial-seq'] = random.randint(0, maxseq) 	
			else:
				self.cfg['initial-seq'] = int( self.cfg['initial-seq'] )
				if self.cfg['initial-seq'] > maxseq:
					self.cfg['initial-seq'] = self.cfg['initial-seq'] % 2**16
			
			self.sendingThread.setInitialSeq(seq=self.cfg['initial-seq'])
		except Exception as e:
			self.error( 'failed to initialize the sequence number: %s' % str(e) )
			self.cfg['initial-seq'] = 0
	
	def __setDefaultDataToStream(self):
		"""
		"""
		self.debug( 'set default data to stream' )
		try:
			if self.cfg['payload-type'] == SutLibraries.Codecs.A_G711U:
				self.defaultPayloads.setCodec( codec=self.cfg['payload-type'] )
			elif self.cfg['payload-type'] == SutLibraries.Codecs.A_G711A:
				self.defaultPayloads.setCodec( codec=self.cfg['payload-type'] )
			else:
				raise Exception( 'payload type not supported: %s' % self.cfg['payload-type'] )
			
			self.defaultPayloads.setRate( rate=codec.PAYLOAD_TYPE_MAP[self.cfg['payload-type']].getRate() )
			self.cfg['framing-interval'] = codec.PAYLOAD_TYPE_MAP[self.cfg['payload-type']].getFraming()
			self.cfg['framing-interval'] = float(self.cfg['framing-interval'])
			
			self.debug( 'init the streamer' )
			# init the streamer
			if self.cfg['default-sound'] == SOUND_SINE_1K:
				payload = self.defaultPayloads.getSine()
			elif self.cfg['default-sound'] == SOUND_WHITE_NOISE:
				payload = self.defaultPayloads.getWhiteNoise()
			elif self.cfg['default-sound'] == SOUND_SILENCE:
				payload = self.defaultPayloads.getSilence()
			else:
				raise Exception( 'default sound not supported: %s' % self.cfg['default-sound'])
			self.rtpStreamer.setVals( raw_vals=payload )
			
			self.debug( 'init the sending thread' )
			# num samples per packets
			numsamples = codec.PAYLOAD_TYPE_MAP[self.cfg['payload-type']].getSize()
			self.rtpStreamer.setSize( pl_size= numsamples)
			self.sendingThread.setNumSamplesPerPacket(num=numsamples)
			
			self.debug( 'data to stream prepared' )
		except Exception as e:
			self.onReset()
			raise Exception( 'failed to init default stream: %s' % str(e) )	
	def __recordSndSound(self):
		"""
		Record the RTP flow in a rtp file. If the codec is supported then the flow is saved in a wave file.
		
		Codecs supported: PCMA (G711A), PCMU (G771U)
		"""
		try:
			if not self.cfg['record-snd-rtp']:
				return
			
			if len(self.bufOut) == 0 :
				return
				
			if not codec.PAYLOAD_TYPE_MAP.has_key(self.cfg['payload-type']):
				self.warning( 'payload type unknown: %s' % self.cfg['payload-type'] )
				# save rtp in raw file
				et = 'UNKNOWN'
				self.saveDataInStorage( destname='snd_audio%s.rtp' % et, data=self.bufOut )
			else:
				# get payload type
				oPt = codec.PAYLOAD_TYPE_MAP[self.cfg['payload-type']]
	
				# save rtp in raw file
				self.saveDataInStorage( destname='snd_audio%s.rtp' % oPt.en, data=self.bufOut )
				
				if oPt.en == 'PCMU':
					formatWav = MediaTools.WAVE_FORMAT_PCMU
				if oPt.en == 'PCMA':
					formatWav = MediaTools.WAVE_FORMAT_PCMA
				w = MediaTools.WavContainer(parent=self.testcase(), rate=oPt.cr, format=formatWav, channels=oPt.c, bits=MediaTools.WAV_UNSIGNED_8BITS)
				w.setDataRaw(dataRaw=self.bufOut)
				
				# save rtp in wav file
				self.saveDataInStorage( destname='snd_audio%s.wav' % oPt.en, data=w.getRaw() )
				
			# reset buffer
			self.bufOut = ''
		except Exception as e:
			self.error( 'record rcv sound error: %s' % str(e) )		
	def __recordRcvSound(self):
		"""
		Record the RTP flow in a rtp file. If the codec is supported then the flow is saved in a wave file.
		
		Codecs supported: PCMA (G711A), PCMU (G771U)
		"""
		try:
			if not self.cfg['record-rcv-rtp']:
				return
			
			if len(self.bufIn) == 0 :
				return
				
			if not codec.PAYLOAD_TYPE_MAP.has_key(self.buf_AudioET):
				self.warning( 'payload type unknown: %s' % self.buf_AudioET)
				# save rtp in raw file
				et = 'UNKNOWN'
				self.saveDataInStorage( destname='rcv_audio%s.rtp' % et, data=self.bufIn )
			else:
				# get payload type
				oPt = codec.PAYLOAD_TYPE_MAP[self.buf_AudioET]
	
				# save rtp in raw file
				self.saveDataInStorage( destname='rcv_audio%s.rtp' % oPt.en, data=self.bufIn )
				
				if oPt.en == 'PCMU':
					formatWav = MediaTools.WAVE_FORMAT_PCMU
				if oPt.en == 'PCMA':
					formatWav = MediaTools.WAVE_FORMAT_PCMA
				w = MediaTools.WavContainer(parent=self.testcase(), rate=oPt.cr, format=formatWav, channels=oPt.c, bits=MediaTools.WAV_UNSIGNED_8BITS)
				w.setDataRaw(dataRaw=self.bufIn)
				
				# save rtp in wav file
				self.saveDataInStorage( destname='rcv_audio%s.wav' % oPt.en, data=w.getRaw() )
				
			# reset buffer
			self.bufIn = ''
		except Exception as e:
			self.error( 'record rcv sound error: %s' % str(e) )
			
	@doc_public
	def configure(self, recordRcvSound=None, recordSndSound=None, defaultSound=None, payloadType=None):
		"""
		Configure settings
		
		@param recordRcvSound: bufferize the sound received and save the RTP flow in a rtp file. If the codec is supported then the flow is saved in a wave file.
		@type recordRcvSound:	boolean/none
		
		@param recordSndSound: bufferize the sound sent and save the RTP flow in a rtp file. If the codec is supported then the flow is saved in a wave file.
		@type recordSndSound:	boolean/none
		
		@param defaultSound: SutAdapters.RTP.SOUND_SINE_1K | SutAdapters.RTP.SOUND_WHITE_NOISE | SutAdapters.RTP.SOUND_SILENCE
		@type defaultSound: intconstant/none
		
		@param payloadType: SutLibraries.Codecs.A_G711U (default payload type) | SutLibraries.Codecs.A_G711A
		@type payloadType: intconstant
		"""
		self.debug( 'reconfigure' )
		if recordRcvSound is not None:
			self.cfg['record-rcv-rtp'] = recordRcvSound
		
		if recordRcvSound is not None:
			self.cfg['record-snd-rtp'] = recordSndSound
		
		rebuildData = False
		if defaultSound is not None:
			self.cfg['default-sound'] = defaultSound
			rebuildData = True
		
		if payloadType is not None:
			self.cfg['payload-type'] = payloadType
			rebuildData = True
		
		if rebuildData:
			self.__setDefaultDataToStream()
			
	def onReset(self):
		"""
		"""
		if self.sendingThread:
			self.sendingThread.stop()
		self.stopListening()
		
	@doc_public
	def setCodec(self, payloadType):
		"""
		Set the codec to use 
		
		@param payloadType: rtp payload type
		@type payloadType: integer/string
		"""
		self.cfg['payload-type'] = int(payloadType)
		# Set the default sound to play
		self.__setDefaultDataToStream()

	def setDataToStream(self, raw_data, pl_type, pl_size, fr_interval):
		"""
		Set the data to stream
		
		@param raw_data:
		@type raw_data:
		
		@param pl_type:
		@type pl_type:
		
		@param pl_size:
		@type pl_size:
		
		@param fr_interval:
		@type fr_interval:
		"""
		try:
			self.cfg['payload-type'] = pl_type
			self.cfg['framing-interval'] = float(fr_interval)
			self.rtpStreamer.setVals(raw_vals=raw_data)
			self.rtpStreamer.setSize(pl_size=psize)
		except Exception as e:
			self.error( 'failed to set data to stream: %s' % str(e) )
			
	def onIncomingData(self, data, lower):
			"""
			"""
			try:
				# decode data
				self.debug('data received (bytes %d), decoding attempt...' % len(data))
				(rtp_tpl, o_rtp, summary) = self.rtpCodec.decode(rtp=data)
				
				# payload to buffer
				if self.cfg['record-rcv-rtp']:
					# save payload type with the first packet
					if self.buf_AudioET is None:
						self.buf_AudioET = o_rtp.pt
					# bufferize
					self.bufIn = ''.join([self.bufIn, o_rtp.pl])

				if self.logLowLevelEvents:
					# add rtp layer 
					lower.addLayer(layer=rtp_tpl)
					self.logRecvEvent( shortEvt = summary, tplEvt = lower ) 	
				else:
					self.onReceiving(lower=lower, pkt=o_rtp)

			except Exception as e:
				self.error('Error while waiting for rtp packet: %s' % str(e))		

	@doc_public
	def sendPacket(self, tpl, to=None):
		"""
		Send RTP packet over network
		
		@param tpl: rtp template packet
		@type tpl: template
		
		@param to: destination ip/port
		@type to: none/tuple
		
		@return: template message
		@rtype: template
		"""
		try:
			# encode template
			try:
				(encodedPkt, summary, oPkt) = self.rtpCodec.encode(rtp_tpl=tpl)
			except Exception as e:
				raise Exception("Cannot encode rtp packet: %s" % str(e))
			
			# Send packet
			try:
				lower = self.udp.sendData( data=encodedPkt, to=to )
			except Exception as e:
				raise Exception("udp failed: %s" % str(e))	
			
			# Bufferize	
			if self.cfg['record-snd-rtp']:
				self.bufOut = ''.join([self.bufOut, oPkt.pl])
					
			# Log event
			if self.logLowLevelEvents:
				# add rtp layer to the lower layer
				lower.addLayer( tpl )
				lower.addRaw(raw=encodedPkt)
				self.logSentEvent( shortEvt = summary, tplEvt = lower ) 
			else:
				self.onSending(lower=lower, pkt=oPkt)

		except Exception as e:
			raise Exception('Unable to send rtp packet: %s' % str(e))
		return lower		
		
	@doc_public
	def startSending(self):
		"""
		Start sending rtp.
		"""
		self.debug( 'start sending rtp' )
		if self.sendingThread:
			self.sendingThread.setSending()
			
	def onSending(self, lower, pkt):
		"""
		Function to reimplement
		
		@param lower: template message
		@type lower: template
		
		@param en: encoding name
		@type en: string
		"""
		self.debug( 'starts sending' )
		# Log event packet sent only if different of the previous
		if self.last_pkt_sent is None:
			self.last_pkt_sent = pkt
			if self.logHighLevelEvents:
				ssrc, en, mt = self.getSummaryPacket(pkt=self.last_pkt_sent)
				lower.addLayer( layer=templates.starts_sending(en=en, ssrc=ssrc, mt=mt, sessid=self.cfg['session-id']) )
				self.logSentEvent( shortEvt = "starts sending", tplEvt = lower )
		else:
			previouspkt = self.getSummaryPacket(pkt=self.last_pkt_sent)
			lastpkt = self.getSummaryPacket(pkt=self.last_pkt_sent)
			if previouspkt != lastpkt:
				self.last_pkt_sent = lastpkt
				if self.logHighLevelEvents:
					ssrc, en, mt = lastpkt
					lower.addLayer( layer=templates.starts_sending(en=en, ssrc=ssrc, mt=mt, sessid=self.cfg['session-id']) )
					self.logSentEvent( shortEvt = "starts sending", tplEvt = lower )
	
	def getSummaryPacket(self, pkt):
		"""
		"""
		en = 'Unknown'
		mt = 'Unknown'
		ssrc = str(pkt.ssrc)
		if codec.PAYLOAD_TYPE_MAP.has_key(pkt.pt):
			en = codec.PAYLOAD_TYPE_MAP[pkt.pt].getName()
			mt = codec.PAYLOAD_TYPE_MAP[pkt.pt].getMediaType()	
		return 	ssrc, en, mt
		
	def onReceiving(self, lower, pkt):
		"""
		Function to reimplement
		
		@param lower: template message
		@type lower: template
		
		@param en: encoding name
		@type en: string
		"""
		self.debug( 'starts receiving' )
		# Log event packet received only if different of the previous
		if self.last_pkt_recv is None:
			self.last_pkt_recv = pkt
			if self.logHighLevelEvents:
				ssrc, en, mt = self.getSummaryPacket(pkt=self.last_pkt_recv)
				lower.addLayer( layer=templates.starts_receiving(en=en, ssrc=ssrc, mt=mt, sessid=self.cfg['session-id']) )
				self.logRecvEvent( shortEvt = "starts receiving", tplEvt = lower )
		else:
			previouspkt = self.getSummaryPacket(pkt=self.last_pkt_recv)
			lastpkt = self.getSummaryPacket(pkt=self.last_pkt_recv)
			if previouspkt != lastpkt:
				self.last_pkt_recv = lastpkt
				if self.logHighLevelEvents:
					ssrc, en, mt = lastpkt
					lower.addLayer( layer=templates.starts_receiving(en=en, ssrc=ssrc, mt=mt, sessid=self.cfg['session-id']) )
					self.logRecvEvent( shortEvt = "starts receiving", tplEvt = lower )	

	def onInactivity(self, lower):
		"""
		Function to reimplement
		
		@param lower: template message
		@type lower: template
		"""
		if self.last_pkt_recv is not None:
			ssrc, en, mt = self.getSummaryPacket(pkt=self.last_pkt_recv)
			self.last_pkt_recv = None
			if self.logHighLevelEvents:
				lower.addLayer( layer=templates.stops_receiving(en=en, ssrc=ssrc, mt=mt, sessid=self.cfg['session-id']) )
				self.logRecvEvent( shortEvt = "stops receiving", tplEvt = lower )
	
	@doc_public
	def stopSending(self):
		"""
		Stop sending rtp.
		"""
		self.debug( 'stop sending rtp' )
		if self.sendingThread:
			if self.sendingThread.isSending():
				self.sendingThread.unsetSending()
			self.sendingThread.stop()
			lower = self.udp.encapsule( ip_event=AdapterIP.sent(), udp_event=AdapterUDP.sent() )
			self.onStopSending(lower=lower)
	
	def onStopSending(self, lower):
		"""
		"""
		if self.last_pkt_sent is not None:
			ssrc, en, mt = self.getSummaryPacket(pkt=self.last_pkt_sent)
			self.last_pkt_sent = None
			if self.logHighLevelEvents:
				lower.addLayer( layer=templates.stops_sending(en=en, ssrc=ssrc, mt=mt, sessid=self.cfg['session-id']) )
				self.logSentEvent( shortEvt = "stops sending", tplEvt = lower )

	@doc_public
	def stopListening(self):
		"""
		"""
		self.stopSending()
		self.udp.stopListening()
		# save rtp in file 
		self.__recordSndSound()
		self.__recordRcvSound()

	def getExpectedTemplate(self, layer_rtp, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		"""
		layer_ip = AdapterIP.ip( source=sourceIp, destination=destinationIp, version=versionIp ) 		
		layer_udp = AdapterUDP.udp(source=sourcePort, destination=destinationPort)
		
		# prepare template
		tpl_msg = TestTemplatesLib.TemplateMessage()
		tpl_msg.addLayer(layer=layer_ip)
		tpl_msg.addLayer(layer=layer_udp)
		tpl_msg.addLayer(layer=layer_rtp)
		return tpl_msg
		
	@doc_public
	def hasStartedReceiving(self, timeout=1.0, ssrc=None, codec=None, type=None, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None, sessionid=None):
		"""
		Wait to receive "starts receiving" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default value=1s)
		@type timeout: float		
		
		@param ssrc: ssrc
		@type ssrc: string/operators/none	
		
		@param codec: codec 
		@type codec: string/operators/none	
		
		@param type: media type 
		@type type: string/operators/none
		
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
		
		@param sessionid: session id for hight level
		@type sessionid: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		layer_rtp = templates.starts_receiving(en=codec, ssrc=ssrc, mt=type, sessid=sessionid)
		expected = self.getExpectedTemplate(layer_rtp=layer_rtp, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
					sourcePort=sourcePort, destinationPort=destinationPort)

		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def hasStoppedReceiving(self, timeout=1.0, ssrc=None, codec=None, type=None, versionIp=None, sourceIp=None, destinationIp=None, 
											sourcePort=None, destinationPort=None, sessionid=None):
		"""
		Wait to receive "stops receving" event event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default value=1s)
		@type timeout: float		
		
		@param ssrc: ssrc
		@type ssrc: string/operators/none	
		
		@param codec: codec 
		@type codec: string/operators/none
		
		@param type: payload type 
		@type type: string/operators/none
		
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
		
		@param sessionid: session id for hight level
		@type sessionid: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		layer_rtp = templates.stops_receiving(en=codec, ssrc=ssrc, mt=type, sessid=sessionid)
		expected = self.getExpectedTemplate(layer_rtp=layer_rtp, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
					sourcePort=sourcePort, destinationPort=destinationPort)

		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
class SendingThread(threading.Thread):
	def __init__(self, parent):
		"""
		"""
		threading.Thread.__init__(self)
		self.parent = parent
		self.sending = False
		self.stopEvent = threading.Event()
		# rtp params
		self.initialSeq = 0
		self.numSamplesPerPacket = 0
		# counters
		self.seq = 0
		self.ts = 0
		self.ssrc = 0

	def setInitialSeq(self, seq):
		"""
		"""
		self.initialSeq = 0
		self.seq = seq

	def setInitialSsrc(self, ssrc):
		"""
		"""
		self.ssrc = ssrc

	def setNumSamplesPerPacket(self, num):
		"""
		"""
		self.numSamplesPerPacket = num
		self.ts  = num
		
	def setSending (self):
		"""
		"""
		self.sending = True

	def unsetSending(self):
		"""
		"""
		self.sending = False
		self.seq = self.initialSeq
		self.ts = 0
		self.ssrc = 0

	def isSending(self):
		"""
		"""
		return self.sending
		
	def stop(self):
		"""
		"""
		self.parent.debug('cleanup sending thread')
		self.stopEvent.set()
		self.join()
		
	def run(self):
		while not self.stopEvent.isSet():
			try:
				if self.sending:
					PAYLOAD = self.parent.rtpStreamer.getNext()
					# prepare the rtp template
					rtp_tpl = templates.rtp( 
																		v=str(self.parent.cfg['version-rtp']),
																		m=str(0),
																		x=str(0),
																		seq=str(self.seq),
																		ts=str(self.ts),
																		ssrc=str(self.ssrc),
																		p=str(0),
																		cc=str(0),
																		pt=str(self.parent.cfg['payload-type']),
																		pl=PAYLOAD,
																		pl_length=str(len(PAYLOAD))
																	)
					self.parent.sendPacket(tpl=rtp_tpl)
					
					# increment the sequence number
					self.seq +=1
					if self.seq > 0xFFFF:
						self.seq  = self.seq  % 2**16
					
					# increment the timestamp
					self.ts += self.numSamplesPerPacket
					if self.ts > 0xFFFFFFFF:
						self.ts  = self.ts  % 2**32
						
					# interval between rtp packets
					time.sleep( self.parent.cfg['framing-interval'] / 1000 )
				else:
					time.sleep(0.01)
			except Exception as e:
				self.parent.error( 'sending rtp error: %s' % str(e) )