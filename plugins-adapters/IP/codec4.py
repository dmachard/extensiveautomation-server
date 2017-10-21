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
import sys

LibraryHashing = sys.modules['SutLibraries.%s.Hashing' % TestLibraryLib.getVersion()]

import struct
import array

import templates
import common

# ip header size
IPV4_LEN = 20 # 20 bytes


# Type of Service
#
#      Bits 0-2:  Precedence.
#      Bit    3:  0 = Normal Delay,      1 = Low Delay.
#      Bits   4:  0 = Normal Throughput, 1 = High Throughput.
#      Bits   5:  0 = Normal Relibility, 1 = High Relibility.
#      Bit  6-7:  Reserved for Future Use.
#
NORMAL = 'normal'
LOW    = 'low'
HIGH   = 'high'
#         0     1     2     3     4     5     6     7
#      +-----+-----+-----+-----+-----+-----+-----+-----+
#      |                 |     |     |     |     |     |
#      |   PRECEDENCE    |  D  |  T  |  R  |  0  |  0  |
#      |                 |     |     |     |     |     |
#      +-----+-----+-----+-----+-----+-----+-----+-----+
#
#        Precedence
#
#          111 - Network Control
#          110 - Internetwork Control
#          101 - CRITIC/ECP
#          100 - Flash Override
#          011 - Flash
#          010 - Immediate
#          001 - Priority
#          000 - Routine
ROUTINE                          = 0
PRIORITY                         = 1
IMMEDIATE                        = 2
FLASH                            = 3
FLASH_OVERRIDE                   = 4
ECP                              = 5
INTERNETWORK_CONTROL             = 6
NETWORK_CONTROL                  = 7

PRECEDENCE = {}
PRECEDENCE[ROUTINE]              = "routine"
PRECEDENCE[PRIORITY]             = "priority"
PRECEDENCE[IMMEDIATE]            = "immediate"
PRECEDENCE[FLASH]                = "flash"
PRECEDENCE[FLASH_OVERRIDE]       = "flash override"
PRECEDENCE[ECP]                  = "critic/ecp"
PRECEDENCE[INTERNETWORK_CONTROL] = "internetwork control"
PRECEDENCE[NETWORK_CONTROL]      = "network control"

#  IPv4 Flags:  3 bits
#      Bit 0: reserved, must be zero
#      Bit 1: (DF) 0 = May Fragment,  1 = Don't Fragment.
#      Bit 2: (MF) 0 = Last Fragment, 1 = More Fragments.
#
#          0   1   2
#        +---+---+---+
#        |   | D | M |
#        | 0 | F | F |
#        +---+---+---+

DF    =  "don't fragment"
MF    =  "more fragments"

#  A summary of the contents of the internet header follows:
# 
#    0                   1                   2                   3   
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |Version|  IHL  |Type of Service|          Total Length         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |         Identification        |Flags|      Fragment Offset    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |  Time to Live |    Protocol   |         Header Checksum       |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                       Source Address                          |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Destination Address                        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Options                    |    Padding    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#

class CodecV4(object):
	def __init__(self, parent, testcase, debug):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.info = parent.info
		
		self.checksum = LibraryHashing.Checksum(parent=testcase, debug=debug)
		self.srcIp = None
		
	def setSrcIp(self, ip):
		"""
		"""
		self.srcIp = ip

	def encode(self, ip_tpl):
		"""
		"""
		# extract values from the template
		ver = ip_tpl.get('version')
		ihl = ip_tpl.get('header-length')
		
		tos = ip_tpl.get('type-service')
		if isinstance(tos, TestTemplatesLib.TemplateLayer):
			tos = tos.getName()
			
		tl = ip_tpl.get('total-length')
		id = ip_tpl.get('identification')
		
		flg = ip_tpl.get('flags')
		if isinstance(flg, TestTemplatesLib.TemplateLayer):
			flg = flg.getName()
			
		frg = ip_tpl.get('fragment-offset')
		ttl = ip_tpl.get('time-to-live')
		
		pro = ip_tpl.get('protocol')
		if isinstance(pro, TestTemplatesLib.TemplateLayer):
			pro = pro.getName()
			
		sum = ip_tpl.get('checksum')
		if isinstance(sum, TestTemplatesLib.TemplateLayer):
			sum = sum.getName()
			
		src = ip_tpl.get('source-ip')
		if isinstance(src, TestTemplatesLib.TemplateLayer):
			src = src.getName()
			
		dst = ip_tpl.get('destination-ip')
		if isinstance(dst, TestTemplatesLib.TemplateLayer):
			dst = dst.getName()
			
		data = ip_tpl.get('data')
		if isinstance(data, TestTemplatesLib.TemplateLayer):
			data = data.getName()
			
		self.debug( 'template read' )
		
		# add human values
		pro_string = None
		if common.PRO_TYPE_MAP.has_key( int(pro) ):
			pro_string = common.PRO_TYPE_MAP[ int(pro) ]
			if pro_string is not None:
				ip_tpl.get('protocol').addKey('string', pro_string)
		
		self.debug( 'human values added to the template' )
		
		# pack fixed part
		if ihl is None:
			ip_tpl.addKey('header-length', '5')
			ihl = 5
		args = [ int(ihl) | int(ver) << 4 ]
		if tos is not None:
			args.append( int(tos) )
		else:
			ip_tpl.addKey('type-service', '0')
			args.append( 0 )
		
		# total length: compute the good value or not 
		if tl is not None:
			args.append( int(tl) )
		else:
			tl = (ihl + 0xF) + len(data) 
			ip_tpl.addKey('total-length', str(tl) )
			args.append( int(tl) )
		
		if id is None:
			ip_tpl.addKey('identification', '0x0000')
			args.append( 0 )
		else:
			if isinstance( id, str):
				args.append( int(id, 16) )
			else:
				args.append( int(id) )
		
		if flg is None:
			ip_tpl.addKey('flags', '0x00')
			flg = 0
		else:
			if isinstance( flg, str):
				flg = int(flg, 16)
			else:
				flg = int(flg) 
				
		if frg is None:
			ip_tpl.addKey('fragment-offset', '0')
			frg = 0
		args.append( int(frg) | int(flg) << 13 )
		
		args.append( int(ttl) )
		args.append( int(pro) )
	
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
				
		args.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=src) )
		args.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=dst) )
			
		fmt = '!2B3H2BH4B4B'
		hdr_ip = struct.pack(fmt, *args )
		sum_computed = self.checksum.compute ( data=hdr_ip, checksum_offset=5)
		if sum2add:
			tpl_sum = TestTemplatesLib.TemplateLayer(name="0x%0.4X" % sum_computed )
			tpl_sum.addKey(name='integer', data=str(sum_computed) )
			tpl_sum.addKey(name='status', data='correct' )
			ip_tpl.addKey('checksum', tpl_sum )
			
			# repack a second time
			args[7] = sum_computed
			datagram = [ struct.pack(fmt, *args ) ]
		else:
			sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
			if sum_int == sum_computed:
				sum_status = 'correct'
				
			ip_tpl.get('checksum').addKey(name='status', data=sum_status )
			datagram = [ hdr_ip ]
		
		self.debug( 'ip header pack ok' )
		
		# add upper data
		datagram.append( data )
				
		# Encode OK, finally prepare the summary
		summary = 'To %s from %s' % (dst, src)
			
		return ''.join(datagram), summary
		
	def decode(self, ip):
		"""
		"""	
		# Extract the fixed header = 20 octets
		# B + B + H  = 4
		# H + H = 4
		# B + B + H = 4
		# I + I = 8 
		ip_header = struct.unpack('!2B3H2BH4B4B', ip[:IPV4_LEN])
		
		## Version:  4 bits
		ip_ver = ( ip_header[0] >> 4 )
		
		## IHL:  4 bits Internet Header Length is the length of the internet header in 32 bit words
		ip_ihl = ( ip_header[0] & 15 )
		
		## Type of Service:  8 bits
		ip_tos = ip_header[1]
		# Precedence.  An independent measure of the importance of this datagram.
		precedence = ip_tos >> 5
		# Delay.  Prompt delivery is important for datagrams with this indication.
		ip_d = (ip_tos & 16) and 1 or 0
		#	Throughput.  High data rate is important for datagrams with this indication.
		ip_t = (ip_tos & 8) and 1 or 0
		# Reliability.  A higher level of effort to ensure delivery is important for datagrams with this indication.
		ip_r = (ip_tos & 4) and 1 or 0
		
		## Total Length:  16 bits
		ip_tl = ip_header[2]
		
		## Identification:  16 bits
		ip_id = ip_header[3]
		
		## Flags:  3 bits
		ip_flg = ( ip_header[4] >> 13 )
		
		## Fragment Offset:  13 bits
		ip_frg = ( ip_header[4] & 0x1FFF )
		
		## Time to Live:  8 bits
		ip_ttl = ip_header[5]
		
		## Protocol:  8 bits
		ip_pro = ip_header[6]
		
		## Header Checksum:  16 bits
		ip_sum = ip_header[7]
		
		## Source Address:  32 bits
		ip_src = ip_header[8:12]

		## Destination Address:  32 bits
		ip_dst = ip_header[12:16]
		
		## extract variable part: options 
		## not yet implemented
		
		## extract data
		data_upper = ip[ (ip_ihl*32)/8: ]
		
		self.debug( 'ip header unpack ok' )
		
		# Add human values
		# upper protocol name
		pro_string = None
		if common.PRO_TYPE_MAP.has_key( ip_pro ):
			pro_string = common.PRO_TYPE_MAP[ ip_pro ]
		
		# flags
		flgs_str = None
		if ip_flg == 2:
			flgs_str = DF
		if ip_flg == 1:
			flgs_str = MF
		
		# tos
		if ip_d: ip_d_str = LOW
		else: ip_d_str = NORMAL
		
		if ip_t: ip_t_str = HIGH
		else: ip_t_str = NORMAL
		
		if ip_r: ip_r_str = HIGH
		else: ip_r_str = NORMAL
		
		precedence_str = PRECEDENCE[precedence]
			
		# checksum is correct ?	
		sum_computed = self.checksum.compute ( data=ip[:IPV4_LEN], checksum_offset=5)
		sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
		if ip_sum == sum_computed:
			sum_status = 'correct'
		
		self.debug( 'ip checksum computed' )
		
		# convert values
		ip_id = "0x%0.4X" % ip_id
		ip_flg = "0x%0.2X" % ip_flg
		ip_sum_hex = "0x%0.4X" % ip_sum
		ip_src = '.'.join( [ str(d) for d in ip_src ] )
		ip_src_hex = None
#		ip_src_hex = ''.join( [ "0x%0.2X" % int(d) for d in ip_src ] )
		ip_dst = '.'.join( [ str(d) for d in ip_dst ] )
#		ip_dst_hex = ''.join( [ "0x%0.2X" % int(d) for d in ip_dst ] )
		ip_dst_hex = None
		
		# Decode OK, create template 
		ip_tpl = templates.ip( source=ip_src, source_hex=ip_src_hex, destination=ip_dst, destination_hex=ip_dst_hex,
													version=str(ip_ver), ihl=ip_ihl, 
													tos=ip_tos, p=precedence, p_str=precedence_str, d=ip_d, d_str=ip_d_str,
													t=ip_t, t_str=ip_t_str, r=ip_r, r_str=ip_r_str, tl=ip_tl, 
													id=ip_id, flg=ip_flg, flg_str=flgs_str, frg=ip_frg, ttl=ip_ttl, pro=ip_pro, pro_str=pro_string,
													sum=ip_sum_hex, sum_status=sum_status, sum_int=str(ip_sum) ,
													data=data_upper, data_size=len(data_upper) )
		# add the raw data  to the layer
		ip_tpl.addRaw(ip[:IPV4_LEN])
		
		self.debug( 'template created' )
		
		# set summary
		summary = 'To %s from %s' % (ip_dst, ip_src)
		if ip_dst == self.srcIp:
			summary = 'From %s to %s' % (ip_src, ip_dst)
			
		return ip_tpl, summary, data_upper