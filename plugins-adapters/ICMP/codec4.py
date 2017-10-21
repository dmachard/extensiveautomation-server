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
import sys

LibraryHashing = sys.modules['SutLibraries.%s.Hashing' % TestLibraryLib.getVersion()]

import templates

import struct
import array
import datetime

# http://www.iana.org/assignments/icmp-parameters

# Redirect Code
CODE_NETWORK         = 0
CODE_HOST            = 1
CODE_TOS_NETWORK     = 2
CODE_TOS_HOST        = 3 

CODES_REDIRECT = {}
CODES_REDIRECT[CODE_NETWORK]      = "Redirect datagrams for the Network"
CODES_REDIRECT[CODE_HOST]         = "Redirect datagrams for the Host"
CODES_REDIRECT[CODE_TOS_NETWORK]  = "Redirect datagrams for the Type of Service and Network"
CODES_REDIRECT[CODE_TOS_HOST]     = "Redirect datagrams for the Type of Service and Host"

# Time exceeded Code
CODE_TTL    = 0
CODE_FRAG   = 1

CODES_TIME_EXCEEDED = {}
CODES_TIME_EXCEEDED[CODE_TTL]       = "Time to live exceeded in transit"
CODES_TIME_EXCEEDED[CODE_FRAG]      = "Fragment reassembly time exceeded"

# Destination Unreachable Message
CODE_NET_UNREACH             = 0
CODE_HOST_UNREACH            = 1
CODE_PROTOCOL_UNREACH        = 2
CODE_PORT_UNREACH            = 3
CODE_FRAG_NEEDED             = 4
CODE_SRC_ROUTE_FAILED        = 5

CODES_UNREACHABLE = {}
CODES_UNREACHABLE[CODE_NET_UNREACH]        = "Net unreachable"
CODES_UNREACHABLE[CODE_HOST_UNREACH]       = "Host unreachable"
CODES_UNREACHABLE[CODE_PROTOCOL_UNREACH]   = "Protocol unreachable"
CODES_UNREACHABLE[CODE_PORT_UNREACH]       = "Port unreachable"
CODES_UNREACHABLE[CODE_FRAG_NEEDED]        = "Fragmentation needed and DF set"
CODES_UNREACHABLE[CODE_SRC_ROUTE_FAILED]   = "Source route failed"

# Query/Error Messages 
DESTINATION_UNREACHABLE = 3
SOURCE_QUENCH           = 4 
REDIRECT                = 5 
ECHO                    = 8 
ECHO_REPLY              = 0 
TIME_EXCEEDED           = 11
PARAMETER_PROBLEM       = 12
TIMESTAMP               = 13 
TIMESTAMP_REPLY         = 14
INFORMATION             = 15      
INFORMATION_REPLY       = 16  
MASK                    = 17
MASK_REPLY              = 18 

MESSAGES = {}
MESSAGES[DESTINATION_UNREACHABLE]  = "Destination unreachable"
MESSAGES[SOURCE_QUENCH]            = "Quench"
MESSAGES[REDIRECT]                 = "Redirect"
MESSAGES[ECHO]                     = "Echo request"
MESSAGES[ECHO_REPLY]               = "Echo reply"
MESSAGES[TIME_EXCEEDED]            = "Time Exceeded"
MESSAGES[PARAMETER_PROBLEM]        = "Parameter problem"
MESSAGES[TIMESTAMP]                = "Timestamp request"
MESSAGES[TIMESTAMP_REPLY]          = "Timestamp reply"
MESSAGES[INFORMATION]              = "Information request" #No Longer Used
MESSAGES[INFORMATION_REPLY]        = "Information reply" #No Longer Used
MESSAGES[MASK]                     = "Mask request"
MESSAGES[MASK_REPLY]               = "Mask reply"

# ICMP Message
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |     Code      |          Checksum             |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
			
class Codec(object):
	def __init__(self, parent, testcase, debug):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.info = parent.info
		
		self.checksum = LibraryHashing.Checksum(parent=testcase, debug=debug)
		self.data = 'ABCDFEFGHIJKLMNOPQPRSTUVWXYZ'
		# The internet header plus the first 64 bits of the original datagram's data.
		self.dataError = '\xFF' * 20 + '\xFF' * 8
		
	def timestamp2human(self, val):
		"""
		@param val:
		@type val:

		@return: time
		@rtype: str
		"""
		sec, milli = divmod(val, 1000)
		min, sec = divmod(sec, 60)
		hour, min = divmod(min, 60)
		#
		milli = str(milli)
		sec = str(sec)
		min = str(min)
		hour = str(hour)
		#
		if len(min) == 1: min = "0%s" % min
		if len(sec) == 1: sec = "0%s" % sec
		return "%s:%s:%s.%s" %(hour, min, sec, milli)
			
	def encode(self, icmp_tpl):
		"""
		"""	
		## encode the common part between query and error messages
		icmp_type = icmp_tpl.get('type')
		if isinstance(icmp_type, TestTemplatesLib.TemplateLayer):
			icmp_type = icmp_type.getName()
		args = [ icmp_type ]
		
		# add human values
		type_string = None
		if MESSAGES.has_key( int(icmp_type) ):
			type_string = MESSAGES[ int(icmp_type) ]
			if type_string is not None:
				icmp_tpl.get('type').addKey('string', type_string)
				
				
		icmp_code = icmp_tpl.get('code')
		if isinstance(icmp_code, TestTemplatesLib.TemplateLayer):
			icmp_code = icmp_code.getName()
		args.append( int(icmp_code) )
		
		icmp_sum = icmp_tpl.get('checksum')
		if isinstance(icmp_sum, TestTemplatesLib.TemplateLayer):
			icmp_sum = icmp_sum.getName()

		sum2add = False
		if icmp_sum is not None:
			if isinstance( icmp_sum, str):
				args.append( int(icmp_sum, 16) )
				sum_int = int(icmp_sum, 16)
			else:
				args.append( int(icmp_sum) )
				sum_int = int(icmp_sum)
		else:
			sum2add = True
			args.append( 0 )

		## pack icmp header
		fmt_common = '!2BH'
		icmp_common = struct.pack(fmt_common, *args )

		icmp_data = ''
		icmp_msg = '' # error or query
		args2 = []
		
		## Query Messages
		if int(icmp_type) in [ ECHO, INFORMATION, TIMESTAMP, MASK ]:
			## extract common part for query 
			icmp_id = icmp_tpl.get('identifier')
			if isinstance(icmp_id, TestTemplatesLib.TemplateLayer):
				icmp_id = icmp_id.getName()
			icmp_seq = icmp_tpl.get('sequence-number')
			if isinstance(icmp_seq, TestTemplatesLib.TemplateLayer):
				icmp_seq = icmp_seq.getName()
			
			if icmp_id is not None:
				if isinstance( icmp_id, str):
					args2 = [ int(icmp_id, 16) ]
				else:
					args2 = [ int(icmp_id) ]
			else:
				icmp_tpl.addKey('identifier', '0x0000' )
				args2 = [ 0 ]
			
			if icmp_seq is not None:
				if isinstance( icmp_seq, str):
					args2.append( int(icmp_seq, 16) )
				else:
					args2.append( int(icmp_seq) )
			else:
				icmp_tpl.addKey('sequence-number', '0x0000' )
				args2.append( 0 )
			
			
			if int(icmp_type) in [ ECHO, INFORMATION ]:
				fmt_query = '2H'
				
			if int(icmp_type) == TIMESTAMP:
				# extract data from tpl
				tp_orig = icmp_tpl.get('originate-timestamp')
				if isinstance(tp_orig, TestTemplatesLib.TemplateLayer):
					tp_orig = tp_orig.getName()

				tp_rx = icmp_tpl.get('receive-timestamp')
				if isinstance(tp_rx, TestTemplatesLib.TemplateLayer):
					tp_rx = tp_rx.getName()
				
				tp_tx = icmp_tpl.get('transmit-timestamp')
				if isinstance(tp_tx, TestTemplatesLib.TemplateLayer):
					tp_tx = tp_tx.getName()

				# The Originate Timestamp is the time the sender last touched the
				# message before sending it, the Receive Timestamp is the time the
				# echoer first touched it on receipt, and the Transmit Timestamp is
				# the time the echoer last touched the message on sending it.
				# The timestamp is 32 bits of milliseconds since midnight UT
				if tp_orig is not None:
					if isinstance( tp_orig, str):
						args2.append( int(tp_orig,16) )
					else:
						args2.append( int(tp_orig) )
				else:
					midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
					now = datetime.datetime.now()
					orig = now - midnight
					orig = orig.seconds * 1000

					tpl_orig = TestTemplatesLib.TemplateLayer(name=str(orig) )
					tpl_orig.addKey(name='time', data=self.timestamp2human(orig) )
					icmp_tpl.addKey('originate-timestamp', tpl_orig )
					args2.append( orig )
					
				if tp_rx is not None:
					if isinstance( tp_rx, str):
						args2.append( int(tp_rx,16) )
					else:
						args2.append( int(tp_rx) )
				else:
					tpl_rx = TestTemplatesLib.TemplateLayer(name='0' )
					tpl_rx.addKey(name='time', data=self.timestamp2human(0) )
					icmp_tpl.addKey('receive-timestamp', tpl_rx )
					args2.append( 0 )
				
				if tp_tx is not None:
					if isinstance( tp_tx, str):
						args2.append( int(tp_tx,16) )
					else:
						args2.append( int(tp_tx) )
				else:
					tpl_tx = TestTemplatesLib.TemplateLayer(name='0' )
					tpl_tx.addKey(name='time', data=self.timestamp2human(0) )
					icmp_tpl.addKey('transmit-timestamp', tpl_tx )
					args2.append( 0 )
					
				fmt_query = '2H3I'
				
			if int(icmp_type) == MASK:
				
				mask = icmp_tpl.get('mask')
				if isinstance(mask, TestTemplatesLib.TemplateLayer):
					mask = mask.getName()
				
				if mask is not None:
					args2.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=mask) )
				else:
					mask = '0.0.0.0'
					icmp_tpl.addKey('mask', mask )
					args2.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=mask) )
					
				fmt_query = '2H4B'
			
			# pack icmp query and save the global fmt
			fmt = '%s%s' % (fmt_common, fmt_query)
			icmp_query = struct.pack( '!%s' % fmt_query, *args2 )

			icmp_msg  = icmp_query
		else:
			fmt = fmt_common

		## Errors Messages
		if int(icmp_type) in [ REDIRECT, SOURCE_QUENCH, PARAMETER_PROBLEM, TIME_EXCEEDED, DESTINATION_UNREACHABLE]:
			if int(icmp_type) == REDIRECT:
				fmt_error = '4B'
				
				redirect_gw= icmp_tpl.get('gateway')
				if isinstance(redirect_gw, TestTemplatesLib.TemplateLayer):
					redirect_gw = redirect_gw.getName()
					
				if redirect_gw is None:
					redirect_gw = '0.0.0.0'
					tpl_gw = TestTemplatesLib.TemplateLayer(name=str(redirect_gw) )
					icmp_tpl.addKey('gateway', tpl_gw )
					
				args2.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=redirect_gw) )
			
			if int(icmp_type) in [ SOURCE_QUENCH, TIME_EXCEEDED, DESTINATION_UNREACHABLE]:
				fmt_error = 'I'	
				
				unused = icmp_tpl.get('unused')
				if isinstance(unused, TestTemplatesLib.TemplateLayer):
					unused = unused.getName()
					
				if unused is None:
					tpl_unused = TestTemplatesLib.TemplateLayer(name="0x00000000" )
					icmp_tpl.addKey('unused', tpl_unused )	
					args2.append(0)
				else:
					if isinstance( unused, str):
						args2.append(  int(unused, 16) )
					else:
						args2.append( int(unused) )
						
			if int(icmp_type) == PARAMETER_PROBLEM:
				fmt_error = 'I'

				pointer = icmp_tpl.get('pointer')
				if isinstance(pointer, TestTemplatesLib.TemplateLayer):
					pointer = pointer.getName()
					
				unused = icmp_tpl.get('unused')
				if isinstance(unused, TestTemplatesLib.TemplateLayer):
					unused = unused.getName()
				
				if pointer is None:	
					pointer = 0
					tpl_pointer = TestTemplatesLib.TemplateLayer(name="0" )
					icmp_tpl.addKey('pointer', tpl_pointer )
				else:
					if isinstance( pointer, str):
						pointer = int(pointer, 16)
					else:
						pointer = int(pointer)
					
				if unused is None:	
					unused = 0
					tpl_unused = TestTemplatesLib.TemplateLayer(name="0x000000" )
					icmp_tpl.addKey('unused', tpl_unused )
				else:
					if isinstance( unused, str):
						unused = int(unused, 16)
					else:
						unused = int(unused)

				args2.append( unused | pointer << 24 )

			# pack icmp query and save the global fmt
			fmt = '%s%s' % (fmt_common, fmt_error)
			icmp_query = struct.pack( '!%s' % fmt_error, *args2 )
			icmp_msg  = icmp_query

			
		## add data ?
		if int(icmp_type) in [ INFORMATION, MASK, TIMESTAMP ]:
			icmp_data = ''
		else:
			icmp_data = icmp_tpl.get('data')
			if icmp_data is None:
				icmp_data = self.data
				if int(icmp_type) in [ REDIRECT, SOURCE_QUENCH, PARAMETER_PROBLEM, TIME_EXCEEDED, DESTINATION_UNREACHABLE]:
					icmp_data = self.dataError
				tpl_data = TestTemplatesLib.TemplateLayer(name=icmp_data)
				tpl_data.addKey(name='length', data=str(len(icmp_data)) )
				icmp_tpl.addKey('data', tpl_data )

		## concatenate the final request
		icmp = '%s%s%s' % (icmp_common, icmp_msg, icmp_data)

		## prepare summary
		if MESSAGES.has_key( int(icmp_type) ):
			summary = MESSAGES[ int(icmp_type) ].title()
		else:
			summary = 'unknown icmp code: %s' %(icmp_code)
		
		## compute checksum ?
		sum_computed = self.checksum.compute ( data=''.join(icmp), checksum_offset=1 )
		args[2] = sum_computed
		if sum2add:
			tpl_sum = TestTemplatesLib.TemplateLayer(name="0x%0.4X" % sum_computed )
			tpl_sum.addKey(name='integer', data=str(sum_computed) )
			tpl_sum.addKey(name='status', data='correct' )
			icmp_tpl.addKey('checksum', tpl_sum )
			
			new_args = args
			new_args.extend( args2 )
			icmp_recomputed = struct.pack( fmt, *new_args )
			icmp = '%s%s' % (icmp_recomputed, icmp_data)
		else:
			sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
			if sum_int == sum_computed:
				sum_status = 'correct'
				
			icmp_tpl.get('checksum').addKey(name='status', data=sum_status )
		
		## return icmp data with a summary
		return ''.join(icmp), summary
		
	def decode(self, icmp):
		"""
		"""
		## Extract the fixed header = 4 octets 
		## between error and query messages
		icmp_len = 4
		icmp_hdr = struct.unpack('!2BH', icmp[:icmp_len])

		## Extract ICMP Fields
		## Type
		icmp_type = icmp_hdr[0]
		type_string = None
		if MESSAGES.has_key( int(icmp_type) ):
			type_string = MESSAGES[ int(icmp_type) ].lower()
			summary = type_string.title()
			
		## Code
		icmp_code = icmp_hdr[1]

		## Checksum
		icmp_chksum = icmp_hdr[2]
		icmp_chksum_hex = "0x%0.4X" % icmp_chksum
		
		next_data = icmp[icmp_len:]

		# checksum is correct ?	
		sum_computed = self.checksum.compute ( data=icmp, checksum_offset=1)
		sum_status = 'incorrect, should be 0x%0.4X' % sum_computed
		if icmp_chksum == sum_computed:
			sum_status = 'correct'
		
		self.debug( 'ip checksum computed' )
		
		## Decode OK, create template 
		icmp_tpl = templates.icmp(tp=str(icmp_type), tp_str=str(type_string), code=str(icmp_code),
															sum=str(icmp_chksum_hex), sum_int =str(icmp_chksum), sum_status=sum_status )
		## add the raw data  to the layer
		icmp_tpl.addRaw(icmp)

		## encode query
		if int(icmp_type) in [  ECHO , ECHO_REPLY,  INFORMATION, INFORMATION_REPLY, 
														TIMESTAMP, TIMESTAMP_REPLY, MASK, MASK_REPLY	]:
			## start with the common part
			#    0                   1                   2                   3
			#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
			#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
			#   |           Identifier          |        Sequence Number        |
			#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
			
			query_len = 4
			icmp_query = struct.unpack('!HH', next_data[:query_len])
			
			## Identifier: If code = 0, an identifier to aid in matching echos and replies, may be zero
			echo_id = icmp_query[0]
			tpl_id = TestTemplatesLib.TemplateLayer(name="0x%0.4X" % echo_id )
			tpl_id.addKey(name='integer', data=str(echo_id) )
			icmp_tpl.addKey('identifier', tpl_id )
			
			## Sequence Number: If code = 0, a sequence number to aid in matching echos and replies, may be zero.
			echo_seq = icmp_query[1]
			tpl_seq = TestTemplatesLib.TemplateLayer(name="0x%0.4X" % echo_seq )
			tpl_seq.addKey(name='integer', data=str(echo_seq) )
			icmp_tpl.addKey('sequence-number', tpl_seq )

			## Echo or Echo Reply Message	
			if int(icmp_type) in [ ECHO , ECHO_REPLY ]:
				#    0                   1                   2                   3
				#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+				
				#   |     Data ...
				#   +-+-+-+-+-								
				echo_data = next_data[query_len:]
				tpl_data = TestTemplatesLib.TemplateLayer(name=echo_data)
				tpl_data.addKey(name='length', data=str(len(echo_data)) )
				icmp_tpl.addKey('data', tpl_data )

			## Timestamp or Timestamp Reply Message
			if int(icmp_type) in [ TIMESTAMP, TIMESTAMP_REPLY ]:
				#    0                   1                   2                   3
				#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+				
				#   |     Originate Timestamp                                       |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |     Receive Timestamp                                         |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |     Transmit Timestamp                                        |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				timestamp_len = 12
				icmp_timestamp = struct.unpack('!3I', next_data[query_len:query_len+timestamp_len])
				data_upper = next_data[query_len+timestamp_len:]
				
				orig = icmp_timestamp[0]
				tpl_orig = TestTemplatesLib.TemplateLayer(name=str(orig) )
				tpl_orig.addKey(name='time', data=self.timestamp2human(orig) )
				tpl_orig.addKey(name='hex', data="0x%0.6X" % orig )
				icmp_tpl.addKey('originate-timestamp', tpl_orig )
				
				rx = icmp_timestamp[1]
				tpl_rx = TestTemplatesLib.TemplateLayer(name=str(rx) )
				tpl_rx.addKey(name='time', data=self.timestamp2human(rx) )
				tpl_rx.addKey(name='hex', data="0x%0.6X" % rx )
				icmp_tpl.addKey('receive-timestamp', tpl_rx )
				
				tx = icmp_timestamp[2]
				tpl_tx = TestTemplatesLib.TemplateLayer(name=str(tx) )
				tpl_tx.addKey(name='time', data=self.timestamp2human(tx) )
				tpl_tx.addKey(name='hex', data="0x%0.6X" % tx )
				icmp_tpl.addKey('transmit-timestamp', tpl_tx )
				
				# add padding if exist
				if len(data_upper):
					icmp_tpl.addKey('padding', data_upper )
					icmp_tpl.addKey('padding-length', len(data_upper) )
			## Address Mask Request or Address Mask Reply	
			if int(icmp_type) in [ MASK, MASK_REPLY ]:	
				#       0                   1                   2                   3
				#       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#      |                        Address Mask                           |
				#      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+		
				
				mask_len = 4
				icmp_mask = struct.unpack('!4B', next_data[query_len:query_len+mask_len])
				data_upper = next_data[query_len+mask_len:]
				
				## Address Mask: A 32-bit mask
				mask = icmp_mask[0:5]
				mask_addr = '.'.join( [ str(d) for d in mask ] )
				tpl_mask = TestTemplatesLib.TemplateLayer(name=str(mask_addr) )
				icmp_tpl.addKey('mask', tpl_mask )
				
				# add padding if exist
				if len(data_upper):
					icmp_tpl.addKey('padding', data_upper )
					icmp_tpl.addKey('padding-length', len(data_upper) )
		elif int(icmp_type) in [ REDIRECT, SOURCE_QUENCH, PARAMETER_PROBLEM, TIME_EXCEEDED, DESTINATION_UNREACHABLE ]:
			## Redirect	Message
			if int(icmp_type) == REDIRECT:	
#				0                   1                   2                   3
#				 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#				+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#				|                 Gateway Internet Address                      |
#				+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#				|      Internet Header + 64 bits of Original Data Datagram      |
#				+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				icmp_redirect = struct.unpack('!4B', next_data[:4])
				
				gw = icmp_redirect[0]
				gw_addr = '.'.join( [ str(d) for d in gw ] )
				tpl_gw_addr = TestTemplatesLib.TemplateLayer(name=str(gw_addr) )
				icmp_tpl.addKey('gateway', tpl_gw_addr )
				
				redirect_data = next_data[4:]
				tpl_data = TestTemplatesLib.TemplateLayer(name=redirect_data)
				tpl_data.addKey(name='length', data=str(len(redirect_data)) )
				icmp_tpl.addKey('data', tpl_data )
			
				if CODES_REDIRECT.has_key( icmp_code ):
					code_tpl = icmp_tpl.get('code')
					code_tpl.addKey('string', CODES_REDIRECT[ icmp_code ].lower() )
					
			## Source Quench Message
			if int(icmp_type) == SOURCE_QUENCH:
				#    0                   1                   2                   3
				#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |                             unused                            |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |      Internet Header + 64 bits of Original Data Datagram      |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+				
				icmp_quench = struct.unpack('!I', next_data[:4])
				
				unused = icmp_quench[0]
				tpl_unused = TestTemplatesLib.TemplateLayer(name=str(unused) )
				icmp_tpl.addKey('unused', tpl_unused )
				
				quench_data = next_data[4:]
				tpl_data = TestTemplatesLib.TemplateLayer(name=quench_data)
				tpl_data.addKey(name='length', data=str(len(quench_data)) )
				icmp_tpl.addKey('data', tpl_data )

			## Parameter Problem Message
			if int(icmp_type) == PARAMETER_PROBLEM:
				#    0                   1                   2                   3
				#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |    Pointer    |                   unused                      |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |      Internet Header + 64 bits of Original Data Datagram      |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+	
				icmp_param = struct.unpack('!I', next_data[:4])		
				
				pointer = (icmp_param[0] >> 24) 
				tpl_pointer = TestTemplatesLib.TemplateLayer(name=str(pointer) )
				icmp_tpl.addKey('pointer', tpl_pointer )
				
				unused = (icmp_param[0] & 0xFFFFFF) 
				tpl_unused = TestTemplatesLib.TemplateLayer(name=str(unused) )
				icmp_tpl.addKey('unused', tpl_unused )
				
				problem_data = next_data[4:]
				tpl_data = TestTemplatesLib.TemplateLayer(name=problem_data)
				tpl_data.addKey(name='length', data=str(len(problem_data)) )
				icmp_tpl.addKey('data', tpl_data )

			## Time Exceeded Message
			if int(icmp_type) == TIME_EXCEEDED:
				#    0                   1                   2                   3
				#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |                             unused                            |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |      Internet Header + 64 bits of Original Data Datagram      |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+				
				icmp_exceeded = struct.unpack('!I', next_data[:4])
				
				unused = icmp_exceeded[0]
				tpl_unused = TestTemplatesLib.TemplateLayer(name=str(unused) )
				icmp_tpl.addKey('unused', tpl_unused )
				
				exceeded_data = next_data[4:]
				tpl_data = TestTemplatesLib.TemplateLayer(name=exceeded_data)
				tpl_data.addKey(name='length', data=str(len(exceeded_data)) )
				icmp_tpl.addKey('data', tpl_data )

				if CODES_TIME_EXCEEDED.has_key( icmp_code ):
					code_tpl = icmp_tpl.get('code')
					code_tpl.addKey('string', CODES_TIME_EXCEEDED[ icmp_code ].lower() )
					
			## Destination Unreachable Message
			if int(icmp_type) == DESTINATION_UNREACHABLE:
				#    0                   1                   2                   3
				#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |                             unused                            |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
				#   |      Internet Header + 64 bits of Original Data Datagram      |
				#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+		
				icmp_unreach = struct.unpack('!I', next_data[:4])
				
				unused = icmp_unreach[0]
				tpl_unused = TestTemplatesLib.TemplateLayer(name=str(unused) )
				icmp_tpl.addKey('unused', tpl_unused )
				
				unreach_data = next_data[4:]
				tpl_data = TestTemplatesLib.TemplateLayer(name=unreach_data)
				tpl_data.addKey(name='length', data=str(len(unreach_data)) )
				icmp_tpl.addKey('data', tpl_data )
				
				if CODES_UNREACHABLE.has_key( icmp_code ):
					code_tpl = icmp_tpl.get('code')
					code_tpl.addKey('string', CODES_UNREACHABLE[ icmp_code ].lower() )
				
		else:
			# set summary
			summary = 'Unknown icmp message'
			
			echo_data = next_data[icmp_len:]
			tpl_data = TestTemplatesLib.TemplateLayer(name=echo_data)
			tpl_data.addKey(name='length', data=str(len(echo_data)) )
			icmp_tpl.addKey('data', tpl_data )

		return icmp_tpl, summary