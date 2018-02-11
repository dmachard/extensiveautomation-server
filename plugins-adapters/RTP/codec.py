#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
import sys

import binascii
import struct

import templates


A = "audio"
V = "video"
AV = "audiovideo"

class PT(object):
	def __init__(self, mt, pt, en, cr, c=None, fi=None):
		"""
		@param mt: media type
		@type mt:		

		@param pt: payload type
		@type pt:		

		@param en: encoding name
		@type en:		

		@param cr: clock rate (Hz)
		@type cr:		

		@param c: channels
		@type c:	

		@param fr: default framing interval in ms
		@type fr:	
		"""
		self.mt = mt # media type
		self.pt = pt # payload type
		self.en = en # encoding name
		self.cr = cr # clock rate
		self.c = c # channels
		self.fi = fi # default framing interval

	def getMediaType(self):
		"""
		"""
		return self.mt
		
	def getName(self):
		"""
		"""
		return self.en
		
	def getSize(self):
		"""
		"""
		return self.fi* 8
	
	def getFraming(self):
		"""
		"""
		return self.fi
	
	def getRate(self):
		"""
		"""
		return self.cr
		
# for audio encodings
PT_PCMU	= PT(mt=A, pt=0, en='PCMU', cr=8000, c=1, fi=20)
PT_PCMA	= PT(mt=A, pt=8, en='PCMA', cr=8000, c=1, fi=20)
PT_G722	= PT(mt=A, pt=9, en='G722', cr=8000, c=1)
PT_G723	= PT(mt=A, pt=4, en='G723', cr=8000, c=1, fi=30)
PT_G728	= PT(mt=A, pt=15, en='G728', cr=8000, c=1)
PT_G729	= PT(mt=A, pt=18, en='G729', cr=8000, c=1, fi=20)

# for video encodings
PT_H261	= PT(mt=V, pt=31, en='H261', cr=90000)
PT_H263	= PT(mt=V, pt=34, en='H263', cr=90000)

# Payload type map
PAYLOAD_TYPE_MAP = {}
PAYLOAD_TYPE_MAP[PT_PCMU.pt] = PT_PCMU # G711U
PAYLOAD_TYPE_MAP[PT_PCMA.pt] = PT_PCMA # G711A
PAYLOAD_TYPE_MAP[PT_G723.pt] = PT_G723
PAYLOAD_TYPE_MAP[PT_G722.pt] = PT_G722
PAYLOAD_TYPE_MAP[PT_G728.pt] = PT_G728
PAYLOAD_TYPE_MAP[PT_G729.pt] = PT_G729
PAYLOAD_TYPE_MAP[PT_H261.pt] = PT_H261
PAYLOAD_TYPE_MAP[PT_H263.pt] = PT_H263

# RFC 1889 - RTP: A Transport Protocol for Real-Time Applications

#      The RTP header has the following format:
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |V=2|P|X|  CC   |M|     PT      |       sequence number         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                           timestamp                           |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |           synchronization source (SSRC) identifier            |
#   +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
#   |            contributing source (CSRC) identifiers             |
#   |                             ....                              |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

RTP_VERSION = 2
class RTPPacket(object):
	def __init__(self, pl,  pt, seq, ts, ssrc, v=RTP_VERSION, p=0, x=0, m=0, cc=0, csrc=None, ext=None, pad=None ):
		"""
		@param pl: payload data
		@type pl:		

		@param pt: payload type
		@type pt:		

		@param seq: sequence number, 2 octets
		@type seq:		

		@param ts: timestamp
		@type ts:		
		
		@param ssrc:
		@type ssrc:		

		@param v: protocol version
		@type v:		
		
		@param p: padding
		@type p:		
		
		@param x: extension
		@type x:		
		
		@param m: marker
		@type m:		
		
		@param cc: CSRC count
		@type cc:		
		
		@param csrc:
		@type csrc:		

		@param ext:
		@type ext:		
		
		@param pad: padding data
		@type pad:
		"""
		self.v = int(v)
		self.p = int(p)
		self.x = int(x)
		self.cc = int(cc)
		self.m = int(m)
		self.pt = int(pt)
		self.seq = int(seq)
		self.ts = int(ts)
		self.ssrc = int(ssrc)
		self.csrc = csrc
		self.ext = ext
		self.pl = pl
		self.pad = pad
		
	def decodePT(self):
		"""
		"""
		if PAYLOAD_TYPE_MAP.has_key(self.pt):
			return PAYLOAD_TYPE_MAP[self.pt].en #  return encoding name
		else:
			return 'Unknown'
			
class Codec(object):
	def __init__(self, parent):
		"""
		@param parent:
		@type parent:		
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info
	def encode(self, rtp_tpl):
		"""
		Encode object RTP to a network RTP packet.

		@param rtp_tpl: rtp template
		@type rtp_tpl: layer message
		"""
		try:
			rtp_packet = []
			
			PAYLOAD = rtp_tpl.get('payload-data')
			M = rtp_tpl.get('marker')
			PT = rtp_tpl.get('payload-type')
			SEQ = rtp_tpl.get('sequence-number')
			TS = rtp_tpl.get('timestamp')
			SSRC = rtp_tpl.get('ssrc')
			V = rtp_tpl.get('version')
			P = rtp_tpl.get('padding')
			X =  rtp_tpl.get('extension')
			CC = rtp_tpl.get('csrc-count')
			CSRC = rtp_tpl.get('csrc')
			EXT = rtp_tpl.get('header-extension')
			PAD = rtp_tpl.get('padding-data')
		
			oRtp = RTPPacket(pl=PAYLOAD, m=M, pt=PT, seq=SEQ, ts=TS, ssrc=SSRC, v=V, p=P, x=X,  cc=CC, csrc=CSRC, ext=EXT, pad=PAD)
			summary = 'PT=%s, Seq=%s, Time=%s' % ( oRtp.decodePT(), oRtp.seq, oRtp.ts )
			
			# Pack the first twelve octets
			# 2*B + H + 2*I = 12
			firstbyte = oRtp.cc | oRtp.x << 4 | oRtp.p << 5 | oRtp.v << 6 
			secondbyte = oRtp.pt | oRtp.m << 7
			fixed_hdr = struct.pack('!2BH2I', firstbyte, secondbyte, oRtp.seq, oRtp.ts, oRtp.ssrc )
			rtp_packet.append( fixed_hdr )
			
			# Pack csrc list
			if oRtp.csrc is not None:
				if len(oRtp.csrc) > 0:
					for csrc in oRtp.csrc:
						rtp_packet.append( struct.pack( '!I', csrc ) )
		
			# Pack header extension
			if oRtp.ext is not None:
				rtp_packet.append( struct.pack('!2H', 0, len(oRtp.ext)/4 ) )
				rtp_packet.append( oRtp.ext )

			# Pack payload data
			rtp_packet.append( oRtp.pl )


			# Pack padding
			if oRtp.pad is not None:
				rtp_packet.append( oRtp.pad )
				rtp_packet.append( struct.pack('!B', len(oRtp.pad) ) )

			# Encode OK
			return ( ''.join(rtp_packet), summary, oRtp)
		except Exception as e:
			raise Exception('failed to encode: %s' % e) 

	def decode(self, rtp):
		"""
		Decode a network RTP packet.

		@param rtp:
		@type rtp:	
		"""
		try:
			# Unpack the first twelve octets which are present in every RTP packet
			hdrs_len = 12
			# B = 1 octet
			# H = 2 octets
			# I = 4 octets
			# 2*B + H + 2*I = 12
			fixed_header= struct.unpack('!2BH2I', rtp[:hdrs_len])
			remaining = rtp[hdrs_len:]

			## Extract fields of the fixed header
			## Version (V): 2 bits
			V = (fixed_header[0] >> 6) 

			## Padding (P): 1 bit
			P = (fixed_header[0] & 32) and 1 or 0

			## Extension (X): 1 bit
			X = (fixed_header[0] & 16) and 1 or 0

			## CSRC count (CC): 4 bits
			CC = (fixed_header[0] & 15)

			## Marker (M): 1 bit
			M = (fixed_header[1] & 128) and 1 or 0

			## Payload type (PT): 7 bits
			PT = (fixed_header[1] & 127)

			## Sequence number: 16 bits
			SEQ = fixed_header[2]

			## Timestamp: 32 bits
			TS = fixed_header[3]

			## SSRC: 32 bits
			SSRC = fixed_header[4]

			## CSRC list: 0 to 15 items, 32 bits each
			csrc_len = 4*CC
			CSRC = struct.unpack( '!%sI' % CC, remaining[:csrc_len] )
			CSRC = list(CSRC)
			remaining = remaining[csrc_len:]

			## If the extension bit (X) is set, the fixed header is followed by exactly one header extension
			EXT = None
			if X:
				# Unpack the first four octets 
				hdrext_len = 4
				header_ext = struct.unpack('!2H', remaining[:hdrext_len])
	
				# Extract length
				data_length = header_ext[1]
				EXT = remaining[hdrext_len:data_length*4]
				remaining = remaining[ hdrext_len + data_length*4:]

			## If the padding bit is set, the packet contains one or more additional padding octets at the end
			## which are not part of the  payload. The last octet of the padding contains a count of how
			## many padding octets should be ignored
			PAD = None
			if P:
				# Unpack the last octet
				cpad = struct.unpack('!B', remaining[-1])[0]
				if cpad:
					PAD = remaining[-cpad:]
					remaining = remaining[:-cpad]
			
			## Payload data
			PAYLOAD = remaining

			# Decode OK
			oRtp = RTPPacket(pl=PAYLOAD, m=M, pt=PT, seq=SEQ, ts=TS, ssrc=SSRC, v=V, p=P, x=X,  cc=CC, csrc=CSRC, ext=EXT, pad=PAD)
			rtp_tpl = templates.rtp(pl=PAYLOAD, m=str(M), pt=str(PT), seq=str(SEQ), ts=str(TS), ssrc=str(SSRC),
																	v=str(V), p=str(P), x=str(X), csrc=None, cc=str(CC), ext=EXT, pad=PAD,
																pl_length=len(PAYLOAD)	)
			summary = 'PT=%s, Seq=%s, Time=%s' % ( oRtp.decodePT(), oRtp.seq, oRtp.ts )
			return rtp_tpl, oRtp, summary
		except Exception as e:
			raise Exception('failed to decode:%s' % e) 