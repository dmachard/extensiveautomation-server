#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

LibraryHashing = sys.modules['SutLibraries.%s.Hashing' % TestLibraryLib.getVersion()]

import templates

import struct
import array

PROTOCOL_UDP                                     = 17
ALL                                                       = -1 # all ports
UDP_LEN                                               = 8 # header length in bytes
OFFSET_CHECKSUM                                 = 3 # index position in header
OFFSET_CHECKSUM_WITH_SPEUDO_HDR  = 9

# Packet format
#	0      7 8     15 16    23 24    31
#	+--------+--------+--------+--------+
#	|     Source      |   Destination   |
#	|      Port       |      Port       |
#	+--------+--------+--------+--------+
#	|                 |                 |
#	|     Length      |    Checksum     |
#	+--------+--------+--------+--------+
#	|
#	|          data octets ...
#	+---------------- ...

class Codec(object):
	def __init__(self, parent, testcase, debug, srcPort):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.info = parent.info
		self.srcPort = srcPort
		self.pad_byte = '0x00'
		self.checksum = LibraryHashing.Checksum(parent=testcase, debug=debug)

	def speudoHeader(self, ipSrc, ipDst, udpLength):
		"""
		xx bit pseudo header conceptually
		0      7 8     15 16    23 24    31 
		+--------+--------+--------+--------+
		|          source address           |
		+--------+--------+--------+--------+
		|        destination address        |
		+--------+--------+--------+--------+
		|  zero  |protocol|   UDP length    |
		+--------+--------+--------+--------+		
		"""
		try:
			args = TestValidatorsLib.IPv4Address(separator='.').toList(ip=ipSrc)
			args.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=ipDst) )
			args.append( 0 )
			args.append( PROTOCOL_UDP )
			args.append( udpLength )
			speudo_hdr = struct.pack('!4B4B2BH', *args )
			return speudo_hdr
		except Exception as e:
			raise Exception( 'speudo header: %s' % str(e) )
			
	def encode(self, udp_tpl, ipSrc, ipDst):
		"""
		"""
		args = []
		src_port = udp_tpl.get('source-port')
		if isinstance(src_port, TestTemplatesLib.TemplateLayer):
			src_port = src_port.getName()
		src_port = int(src_port)
		args.append( src_port )

		dst_port = udp_tpl.get('destination-port')
		if isinstance(dst_port, TestTemplatesLib.TemplateLayer):
			dst_port = dst_port.getName()
		dst_port = int(dst_port)
		args.append( dst_port )
		
		sum = udp_tpl.get('checksum')
		if isinstance(sum, TestTemplatesLib.TemplateLayer):
			sum = sum.getName()
			
		data = udp_tpl.get('data')
		if isinstance(data, TestTemplatesLib.TemplateLayer):
			data = data.getName()
		if data is None:
			data = ''
		
		total_length = udp_tpl.get('total-length')
		if total_length is None:
			total_length = UDP_LEN + len(data)
			udp_tpl.addKey(name='total-length', data=str(total_length) )	
		else:
			total_length = int(total_length)
		args.append( total_length )
		
		# checksum: compute the good value or not 
		sum2add = False
		if sum is not None:
			if isinstance( id, str):
				args.append( int(sum, 16) )
				sum_int = int(sum, 16)
			else:
				args.append( int(sum) )	
				sum_int = int(sum)				
		else:
			sum2add = True
			args.append( 0 )
			
		# pack udp header
		fmt = "!4H"
		udp_hdr = struct.pack(fmt, *args )
		speudo_hdr = self.speudoHeader(ipSrc=ipSrc, ipDst=ipDst, udpLength=total_length )
		sum_computed = self.checksum.compute (data=''.join( [speudo_hdr, udp_hdr, data] ), checksum_offset=OFFSET_CHECKSUM_WITH_SPEUDO_HDR )
		if sum2add:
			tpl_sum = TestTemplatesLib.TemplateLayer(name="0x%0.4X" % sum_computed )
			tpl_sum.addKey(name='integer', data=str(sum_computed) )
			tpl_sum.addKey(name='status', data='correct' )
			udp_tpl.addKey('checksum', tpl_sum )
			
			# repack a second time
			args[OFFSET_CHECKSUM] = sum_computed
			udp = [ struct.pack(fmt, *args ) ]
		else:
			sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
			if sum_int == sum_computed:
				sum_status = 'correct'
			
			udp_tpl.get('checksum').addKey(name='status', data=sum_status )
			udp = [ udp_hdr ]
		self.debug( 'udp header pack ok' )
		
		# add upper data
		udp.append( data )

		# Encode OK, finally prepare the summary
		summary = 'Port=%s>%s, Len=%s' % (src_port, dst_port, len(data) )
		self.debug( 'udp data pack ok' )
		
		return  ''.join(udp) , summary

	def decode(self, udp, ipSrc, ipDst):
		"""
		"""
		udp_hdr = struct.unpack('!4H', udp[:UDP_LEN])
		
		## source:  2 bytes
		src_port = udp_hdr[0]
		
		## destination:  2 bytes
		dst_port = udp_hdr[1]
		
		## length:  2 bytes
		lgth = udp_hdr[2]
		
		## checksum:  2 bytes
		udp_sum = udp_hdr[3]
		udp_sum_hex = "0x%0.4X" % udp_sum
		
		## extract data
		data_upper = udp[UDP_LEN:]
		
		# checksum is correct ?	optional for udp
		#		An all zero  transmitted checksum  value means that the transmitter  generated  no checksum  (for
		#		debugging or for higher level protocols that don't care).
		if udp_sum != 0:
			speudo_hdr = self.speudoHeader(ipSrc=ipSrc, ipDst=ipDst, udpLength=lgth)
	
			sum_computed = self.checksum.compute( data= ''.join( [speudo_hdr, udp] ), checksum_offset=OFFSET_CHECKSUM_WITH_SPEUDO_HDR  )
			sum_status = 'incorrect, should be 0x%0.4X' % sum_computed

			if udp_sum == sum_computed:
				sum_status = 'correct'
			self.debug( 'udp checksum computed' )
		else:
			sum_status = "don't care"
			
		# Decode OK, create template 
		udp_tpl = templates.udp(source=str(src_port), destination=str(dst_port), length=str(lgth),
														sum=udp_sum_hex, sum_status=sum_status, sum_int=str(udp_sum),
														data=data_upper, data_size=len(data_upper) )
		# add the raw data  to the layer
		udp_tpl.addRaw(udp[:UDP_LEN])

		# set summary
		summary = 'Port=%s>%s, Len=%s' % (src_port, dst_port, len(data_upper))
		#		if dst_port == self.srcPort:
		#			summary = 'Port=%s<%s, Len=%s' % (dst_port, src_port, len(data_upper))

		return udp_tpl, summary, data_upper
