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

import templates

import struct
import array

PROTOCOL_TCP                     = 6
ALL                              = -1 # all ports
TCP_LEN                          = 20 # header length in bytes
POS_CHECKSUM                     = 6 # index position in the list header
OFFSET_CHECKSUM_WITH_SPEUDO_HDR  = 14

CTRL_BITS_NS                     = 'NS'
CTRL_BITS_CWR                    = 'CWR'
CTRL_BITS_ECN                    = 'ECN'
CTRL_BITS_URG                    = 'URG'
CTRL_BITS_ACK                    = 'ACK'
CTRL_BITS_PSH                    = 'PSH'
CTRL_BITS_RST                    = 'RST'
CTRL_BITS_SYN                    = 'SYN'
CTRL_BITS_FIN                    = 'FIN'

#http://tools.ietf.org/html/rfc793
#http://tools.ietf.org/html/rfc3540
#http://tools.ietf.org/html/rfc3168
#http://tools.ietf.org/html/rfc2018 TCP Selective Acknowledgment Options
#http://tools.ietf.org/html/rfc1323 WSOPT - Window Scale

# TCP Header Format, fix part without option                               
#    0                   1                   2                   3   
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |          Source Port          |       Destination Port        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                        Sequence Number                        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Acknowledgment Number                      |
#   +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
#   |  Data |           |U|A|P|R|S|F|                               |
#   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
#   |       |           |G|K|H|T|N|N|                               |
#   +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
#   |           Checksum            |         Urgent Pointer        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

#(from left to right):
#URG:  Urgent Pointer field significant
#ACK:  Acknowledgment field significant
#PSH:  Push Function
#RST:  Reset the connection
#SYN:  Synchronize sequence numbers
#FIN:  No more data from sender

#NS:   The Nonce Sum 
#CWR:  Congestion Window Reduced
#ECN:  ECN-nonce

# tcp kind options values
OPTION_END_LIST            = 0 # rfc793
OPTION_NO_OPERATION        = 1 # rfc793
OPTION_MAX_SEGMENT_SIZE    = 2 # rfc793
OPTION_WINDOW_SCALE        = 3 # rfc1323 
OPTION_SACK_PERMITTED      = 4 # rfc2018
OPTION_SACK                = 5 # rfc2018
OPTION_ECHO                = 6 # rfc1072
OPTION_REPLY               = 7 # rfc1072
OPTION_TIMESTAMP           = 8 # rfc1323
# TODO RFC1693, RFC6247, RFC4782, RFC5482, RFC5925, RFC4727, RFC1146

class Codec(object):
	def __init__(self, parent, testcase, debug, srcPort):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.error = parent.error
		self.info = parent.info
		
		self.srcPort = srcPort
		self.checksum = LibraryHashing.Checksum(parent=testcase, debug=debug)
		self.dflt_seqnum = '0x0000'
		self.dflt_acknum = '0x0000'
		self.dflt_ctrlbits = '0x000'
		self.dflt_urgptr = '0x0000'
		self.dflt_win = '0x0000'
		
	def speudoHeader(self, ipSrc, ipDst, tcpLength):
		"""
		96 bit pseudo header conceptually
		
		The TCP Length is the TCP header length plus the data length in
		octets (this is not an explicitly transmitted quantity, but is
		computed), and it does not count the 12 octets of the pseudo header.
			
		+--------+--------+--------+--------+
		|           Source Address          |
		+--------+--------+--------+--------+
		|         Destination Address       |
		+--------+--------+--------+--------+
		|  zero  |  PTCL  |    TCP Length   |
		+--------+--------+--------+--------+
		"""
		try:
			args = TestValidatorsLib.IPv4Address(separator='.').toList(ip=ipSrc)
			args.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=ipDst) )
			args.append( 0 )
			args.append( PROTOCOL_TCP )
			args.append( tcpLength )
			speudo_hdr = struct.pack('!4B4B2BH', *args )
			return speudo_hdr
		except Exception as e:
			raise Exception( 'speudo header: %s' % str(e) )
			
	def encode(self, tcp_tpl, ipSrc, ipDst):
		"""
		"""
		args = []
		src_port = tcp_tpl.get('source-port')
		if isinstance(src_port, TestTemplatesLib.TemplateLayer):
			src_port = src_port.getName()
		src_port = int(src_port)
		args.append( src_port )

		dst_port = tcp_tpl.get('destination-port')
		if isinstance(dst_port, TestTemplatesLib.TemplateLayer):
			dst_port = dst_port.getName()
		dst_port = int(dst_port)
		args.append( dst_port )
		
		seq_num = tcp_tpl.get('sequence-number')
		if isinstance(seq_num, TestTemplatesLib.TemplateLayer):
			seq_num = seq_num.getName()
		if seq_num is None:
			tcp_tpl.addKey(name='sequence-number', data=str(self.dflt_seqnum) )	
			seq_num = self.dflt_seqnum
		if isinstance( seq_num, str):
			seq_num = int(seq_num, 16) 
		else:	
			seq_num = int(seq_num)
		args.append( seq_num )
	
		ack_num = tcp_tpl.get('acknowledgment-number')
		if isinstance(ack_num, TestTemplatesLib.TemplateLayer):
			ack_num = ack_num.getName()
		if ack_num is None:
			tcp_tpl.addKey(name='acknowledgment-number', data=str(self.dflt_acknum) )	
			ack_num = self.dflt_acknum
		if isinstance( ack_num, str):
			ack_num = int(ack_num, 16) 
		else:	
			ack_num = int(ack_num)
		ack_num = int(ack_num)
		args.append( ack_num )
			
		hdr_length = tcp_tpl.get('data-offset')
		if isinstance(hdr_length, TestTemplatesLib.TemplateLayer):
			hdr_length = hdr_length.getName()
		if hdr_length is None:
			hdr_length = TCP_LEN * 8 / 32
			tcp_tpl.addKey(name='data-offset', data=str(hdr_length) )	
		else:
			hdr_length = int(hdr_length)

		control_bits = tcp_tpl.get('control-bits')
		if isinstance(control_bits, TestTemplatesLib.TemplateLayer):
			control_bits = control_bits.getName()
		if control_bits is None:
			tpl_control = TestTemplatesLib.TemplateLayer(name=str(self.dflt_ctrlbits) )
			tcp_tpl.addKey(name='control-bits', data=tpl_control )	
			control_bits = int(self.dflt_ctrlbits, 16) 
		else:
			if isinstance( control_bits, str):
				control_bits = int(control_bits, 16) 
			else:
				control_bits = int(control_bits)
	
		ctrl_bits_lst = []
		if (control_bits & 256) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_NS )
		if (control_bits & 256) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_CWR )
		if (control_bits & 64) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_ECN )
		if (control_bits & 32) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_URG )
		if (control_bits & 16) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_ACK )
		if (control_bits & 8) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_PSH )
		if (control_bits & 4) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_RST )
		if (control_bits & 2) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_SYN )
		if (control_bits & 1) and 1 or 0: ctrl_bits_lst.append( CTRL_BITS_FIN )
		ctrl_bits_lst.reverse()
		if not len(ctrl_bits_lst): ctrl_bits_lst.append('No Flags')
		tcp_tpl.get('control-bits').addKey('string', ', '.join(ctrl_bits_lst) )
		
		args.append(( hdr_length << 12 ) + control_bits )
		
		win = tcp_tpl.get('window')
		if isinstance(win, TestTemplatesLib.TemplateLayer):
			win = win.getName()
		if win is None:
			tcp_tpl.addKey(name='window', data=str(self.dflt_win) )	
			win = int(self.dflt_win, 16) 
		else:
			if isinstance( win, str):
				win = int(win, 16) 
			else:
				win = int(win)
		args.append( win )
		
		sum = tcp_tpl.get('checksum')
		if isinstance(sum, TestTemplatesLib.TemplateLayer):
			sum = sum.getName()

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
			
		urg_ptr= tcp_tpl.get('urgent-pointer')
		if isinstance(urg_ptr, TestTemplatesLib.TemplateLayer):
			urg_ptr = urg_ptr.getName()
		if urg_ptr is None:
			tcp_tpl.addKey(name='urgent-pointer', data=str(self.dflt_urgptr) )	
			urg_ptr = int(self.dflt_urgptr, 16) 
		else:
			if isinstance( urg_ptr, str):
				urg_ptr = int(urg_ptr, 16) 
			else:
				urg_ptr = int(urg_ptr)
		args.append( urg_ptr )

		# add options
		tcp_opts = tcp_tpl.get('options')
		if isinstance(tcp_opts, TestTemplatesLib.TemplateLayer):
			# extract raw options data
			tcp_opts = tcp_opts.getName()
			# extract the sub template
			tpl_opt = tcp_tpl.get('options')
			
			# encode options
			opt_max_seg = tpl_opt.get('maximun-segment-size')
			if opt_max_seg is not None:
				opt_args = [OPTION_MAX_SEGMENT_SIZE, 4, int(opt_max_seg) ]
				tcp_opts = struct.pack('!2BH', *opt_args)
			opt_win_scale = tpl_opt.get('window-scale')
			if opt_win_scale is not None:
				opt_args = [OPTION_WINDOW_SCALE, 3, int(opt_win_scale) ]
				tcp_opts += struct.pack('!3B', *opt_args)
			opt_sack_perm = tpl_opt.get('sack-permitted')
			if opt_sack_perm is not None:
				opt_args = [OPTION_SACK_PERMITTED, 2]
				tcp_opts += struct.pack('!2B', *opt_args)
			opt_sack = tpl_opt.get('sack')
			if opt_sack is not None:
				opt_args = [OPTION_SACK, len(opt_sack)]
				tcp_opts += ''.join( [ struct.pack('!2B', *opt_args), opt_sack ] ) 	
				
			# add padding
			if len(tcp_opts) % 4 != 0:
				pad = '\x00' * (4 - len(tcp_opts) % 4 )
				tcp_opts += pad
				tpl_opt.addKey(name='padding', data=pad )
			
			# add options length just for description, update the data offset and finally
			# update the data options
			tpl_opt.addKey(name='length', data=len(tcp_opts) )	
			tpl_opt.updateName(name=tcp_opts)
			hdr_length += ( len(tcp_opts) * 8 ) /32
			
			# overwrite the data offset value with the real value
			tcp_tpl.updateKey(name='data-offset', data=hdr_length )
			args[4] = ( hdr_length << 12 ) + control_bits
		if tcp_opts is None:
			tcp_opts = ''

		# get upper data from the template
		data = tcp_tpl.get('data')
		if isinstance(data, TestTemplatesLib.TemplateLayer):
			data = data.getName()
		if data is None:
			data = ''
		
		# pack tcp header
		fmt = "!2H2I4H"
		tcp_hdr = struct.pack(fmt, *args )
		speudo_hdr = self.speudoHeader(ipSrc=ipSrc, ipDst=ipDst, tcpLength=len(tcp_hdr) + len(tcp_opts) + len(data) )
		sum_computed = self.checksum.compute (data=''.join( [speudo_hdr, tcp_hdr, tcp_opts, data] ), checksum_offset=OFFSET_CHECKSUM_WITH_SPEUDO_HDR )

		if sum2add:
			tpl_sum = TestTemplatesLib.TemplateLayer(name="0x%0.4X" % sum_computed )
			tpl_sum.addKey(name='integer', data=str(sum_computed) )
			tpl_sum.addKey(name='status', data='correct' )
			tcp_tpl.addKey('checksum', tpl_sum )

			# repack a second time
			args[POS_CHECKSUM] = sum_computed
			tcp = [ struct.pack(fmt, *args ), tcp_opts ]

		else:
			sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
			if sum_int == sum_computed:
				sum_status = 'correct'
			
			tcp_tpl.get('checksum').addKey(name='status', data=sum_status )
			tcp = [ tcp_hdr, tcp_opts ]
		self.debug( 'tcp header pack ok' )
		
		# add upper data
		tcp.append( data )

		# Encode OK, finally prepare the summary
		summary = '[%s] Port=%s>%s, Seq=%s, Ack=%s, Win=%s, Len=%s' % (', '.join(ctrl_bits_lst), src_port, dst_port, seq_num, ack_num, win, len(data) )
		self.debug( 'tcp data pack ok' )
		
		return  ''.join(tcp) , summary
		
	def decode(self, tcp, ipSrc, ipDst):
		"""
		"""
		tcp_hdr = struct.unpack('!2H2I4H', tcp[:TCP_LEN])
		
		## Source Port:  16 bits: The source port number.
		src_port = tcp_hdr[0]
		
		## Destination Port:  16 bits: The destination port number.
		dst_port = tcp_hdr[1]
		
		##  Sequence Number:  32 bits
		seq_num = tcp_hdr[2]
		
		##  Acknowledgment Number:  32 bits
		ack_num = tcp_hdr[3]
		
		## Data Offset:  4 bits
		data_offset = (tcp_hdr[4] >> 12) 
	
		## Reserved:  6 bits
		reserved = 0
		
		## Control Bits:  6 bits
		ctrl_bits_lst = []
		
		ns = (tcp_hdr[4] & 256) and 1 or 0
		if ns: ctrl_bits_lst.append( CTRL_BITS_NS )
		cwr = (tcp_hdr[4] & 128) and 1 or 0
		if cwr: ctrl_bits_lst.append( CTRL_BITS_CWR )
		ece = (tcp_hdr[4] & 64) and 1 or 0
		if ece: ctrl_bits_lst.append( CTRL_BITS_ECN )
		urg = (tcp_hdr[4] & 32) and 1 or 0
		if urg: ctrl_bits_lst.append( CTRL_BITS_URG )
		ack = (tcp_hdr[4] & 16) and 1 or 0
		if ack: ctrl_bits_lst.append( CTRL_BITS_ACK )
		psh = (tcp_hdr[4] & 8) and 1 or 0
		if psh: ctrl_bits_lst.append( CTRL_BITS_PSH )
		rst = (tcp_hdr[4] & 4) and 1 or 0
		if rst: ctrl_bits_lst.append( CTRL_BITS_RST )
		syn = (tcp_hdr[4] & 2) and 1 or 0
		if syn: ctrl_bits_lst.append( CTRL_BITS_SYN )
		fin = (tcp_hdr[4] & 1) and 1 or 0
		if fin: ctrl_bits_lst.append( CTRL_BITS_FIN )
		ctrl_bits_lst.reverse()
		if not len(ctrl_bits_lst): ctrl_bits_lst.append('No Flags')
		
		ctrl_bits = tcp_hdr[4] & 255
		ctrl_bits_hex = "0x%0.3X" % ctrl_bits
		
		##  Window:  16 bits
		window = tcp_hdr[5]
		window_hex = "0x%0.4X" % window
		
		## Checksum:  16 bits
		tcp_sum = tcp_hdr[6]
		tcp_sum_hex = "0x%0.4X" % tcp_sum
		
		## Urgent Pointer:  16 bits
		urgent_ptr = tcp_hdr[7]
		urgent_ptr_hex = "0x%0.4X" % urgent_ptr
		
		self.debug( 'tcp fixed header part extracted' )
		
		# the variable part, extract option part
		options = None; options_size = None; opt_max_seg = None;
		opt_pad = None; opt_nop = 0; opt_end = None; opt_win_scale=None
		opt_ts=None; opt_sack_permitted=None; opt_sack=None; opt_echo=None; opt_reply=None
		if data_offset*32/8 == TCP_LEN:
			self.debug( 'no tcp options' )	
		else:
			try:
				options = tcp[TCP_LEN:data_offset*32/8]
				options_size = len(options) 
				nextbytes = array.array('B', options)
				while len(nextbytes) > 0:
					if nextbytes[0] == OPTION_END_LIST:
						opt_end = ''
						opt_pad = nextbytes[1:].tostring()
						break
					# The TCP No Operation option is used to pad the option list.
					elif nextbytes[0] == OPTION_NO_OPERATION: 
						opt_nop += 1
						nextbytes = nextbytes[1:]
					elif nextbytes[0] == OPTION_MAX_SEGMENT_SIZE:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_max_seg = (opt[0] << 8 )+ opt[1]
						nextbytes = nextbytes[opt_len:]
					elif nextbytes[0] == OPTION_WINDOW_SCALE:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_win_scale = opt[0]
						nextbytes = nextbytes[opt_len:]
					elif nextbytes[0] == OPTION_TIMESTAMP:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_tsval = (opt[0] << 56) + (opt[1] << 48) + (opt[2] << 40)  + (opt[3] << 32)
						opt_tsecr = (opt[4] << 24) + (opt[5] << 16) + (opt[6] << 8)  + opt[7]
						opt_ts = TestTemplatesLib.TemplateLayer(name='timestamp' )
						opt_ts.addKey(name='value', data=str(opt_tsval) )
						opt_ts.addKey(name='echo-reply', data=str(opt_tsecr) )		
						nextbytes = nextbytes[opt_len:]
					elif nextbytes[0] == OPTION_SACK_PERMITTED:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_sack_permitted = 'supported'
						nextbytes = nextbytes[opt_len:]
					elif nextbytes[0] == OPTION_SACK:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_sack = opt.tostring()
						nextbytes = nextbytes[opt_len:]
					elif nextbytes[0] == OPTION_ECHO:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_echo = (opt[0] << 24) + (opt[1] << 16) + (opt[2] << 8)  + opt[3]
						nextbytes = nextbytes[opt_len:]
					elif nextbytes[0] ==OPTION_REPLY:
						opt_len = nextbytes[1]
						opt = nextbytes[2: opt_len]
						opt_reply = (opt[0] << 24) + (opt[1] << 16) + (opt[2] << 8)  + opt[3]
						nextbytes = nextbytes[opt_len:]
					else:
						opt_pad = nextbytes.tostring()
						break	
			except Exception as e:
				self.error( 'unable to extract tcp options: %s' % str(e) )
			if not opt_nop: opt_nop = None
			
		## extract data
		data_upper = tcp[data_offset*32/8:]
		
		# checksum is correct 
		if tcp_sum != 0:
			speudo_hdr = self.speudoHeader(ipSrc=ipSrc, ipDst=ipDst, tcpLength=len(tcp))
			sum_computed = self.checksum.compute( data= ''.join( [speudo_hdr, tcp] ), checksum_offset=OFFSET_CHECKSUM_WITH_SPEUDO_HDR  )
			sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
			if tcp_sum == sum_computed:
				sum_status = 'correct'
			self.debug( 'tcp checksum computed' )
		else:
			sum_status = "don't care"
			
		# Decode OK, create template 
		tcp_tpl = templates.tcp( source=str(src_port), destination=str(dst_port),sum_int=str(tcp_sum), sum=tcp_sum_hex,
														 seq_num=str(seq_num), ack_num=str(ack_num), sum_status=sum_status,
														data=data_upper, data_size=len(data_upper), window=window_hex, window_int=str(window),
														urgent=urgent_ptr_hex, urgent_int=str(urgent_ptr), data_offset=str(data_offset),
														control_bits=ctrl_bits_hex, control_bits_str=', '.join(ctrl_bits_lst),
														options=options, options_size=options_size, opt_max_seg=opt_max_seg, opt_pad=opt_pad,
														opt_nop=opt_nop, opt_end=opt_end, opt_win_scale=opt_win_scale, 
														opt_ts=opt_ts, opt_sack_permitted=opt_sack_permitted, opt_sack=opt_sack)
		# add the raw data  to the layer
		tcp_tpl.addRaw(tcp[:data_offset*32/8])
		
		# set summary 
		summary = "[%s] Port=%s<%s, Seq=%s, Ack=%s, Win=%s, Len=%s" % ( ', '.join(ctrl_bits_lst), dst_port, src_port,
																					seq_num, ack_num, window, len(data_upper)  )
		
		return tcp_tpl, summary, data_upper