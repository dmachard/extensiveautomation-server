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

import struct
import templates

OP_REQUEST	= "0x0001"
OP_REPLY		= "0x0002"

HARDWARE_TYPE = "0x0001"
HARDWARE_LEN  = "0x06"
PROTOCOL_LEN  = "0x04"


class Codec(object):
	def __init__(self, parent):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.info = parent.info
	
	def getOp(self, op):
		"""
		"""
		if op == OP_REQUEST: 
			op_str = 'request'
		elif op == OP_REPLY: 
			op_str = 'reply'
		else:
			op_str = 'unknown'
		return op_str
		
	def encode(self, arp_tpl):
		"""
		"""
		# extract values from the template
		hrd = arp_tpl.get('hardware-type')
		pro = arp_tpl.get('protocol-type')
		hln = arp_tpl.get('hardware-len')
		pln = arp_tpl.get('protocol-len')
		op = arp_tpl.get('op-code')
		if isinstance(op, TestTemplatesLib.TemplateLayer):
			op = op.getName()
		sha = arp_tpl.get('sender-mac')
		spa = arp_tpl.get('sender-ip')
		tha = arp_tpl.get('target-mac')
		tpa = arp_tpl.get('target-ip')
		
		# add human values
		op_str = self.getOp(op=op)
		arp_tpl.get('op-code').addKey('string', op_str)	
			
		# pack fixed part
		args = [ int(hrd, 16) ]
		args.append( int(pro, 16) )
		hln = int(hln, 16)
		args.append( hln )
		pln = int(pln, 16)
		args.append( pln )
		args.append( int(op, 16) )
		arp = [ struct.pack('!HHBBH', *args ) ]
		
		if not len(sha):
			raise Exception( "encode: sha is empty" )
			
		# pack variable part
		args_next = TestValidatorsLib.MacAddress(separator=':').toList(mac=sha)
		
		args_next.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=spa) )
		args_next.extend( TestValidatorsLib.MacAddress(separator=':').toList(mac=tha) )
		args_next.extend( TestValidatorsLib.IPv4Address(separator='.').toList(ip=tpa) )
		arp.append( struct.pack( '!%sB%sB%sB%sB' % (hln, pln, hln, pln) , *args_next ) )

	
		# Encode OK, finally prepare the summary
		if op == OP_REQUEST:
			summary = 'Who has %s? Tell %s' % (tpa, spa)
		elif op == OP_REPLY:
			summary = '%s is at %s' % (spa, sha)
		else:
			summary = 'unknown op %s' % op
		

		return ''.join(arp), summary
			
	def decode(self, arp):
		"""
		"""
		# fixed header, H + H + B + B + H = 8
		arp_len_fixed = 8
		arp_header = struct.unpack('!HHBBH', arp[:arp_len_fixed])

		## 16.bit Hardware address space 
		arp_hrd = arp_header[0]
		
		## 16.bit Protocol address space
		arp_pro = arp_header[1]

		## 8.bit byte length of each hardware address
		arp_hln = arp_header[2]

		## 8.bit byte length of each protocol address
		arp_pln = arp_header[3]

		## 16.bit opcode
		arp_op = arp_header[4]

		## extract addresses, variable part
		addrs_len = 2*int(arp_hln) + 2*int(arp_pln)
		arp_addresses = struct.unpack( '!%sB%sB%sB%sB' %(int(arp_hln), int(arp_pln), int(arp_hln), int(arp_pln)),
																		arp[arp_len_fixed:arp_len_fixed+addrs_len ] )
		data_upper = arp[ arp_len_fixed+addrs_len :]

		## Hardware address of sender
		arp_sha = arp_addresses[ 0:int(arp_hln) ]

		## Protocol address of sender
		arp_spa = arp_addresses[ int(arp_hln): int(arp_hln) + int(arp_pln) ]

		## Hardware address of target
		arp_tha = arp_addresses[ int(arp_hln) + int(arp_pln): 2 * int(arp_hln) + int(arp_pln) ]
	
		## Protocol address of target
		arp_tpa = arp_addresses[ 2 * int(arp_hln) + int(arp_pln):2 * int(arp_hln) + 2*int(arp_pln)]

		# convert values
		arp_hrd = "0x%0.4X" % arp_hrd
		arp_pro = "0x%0.4X" % arp_pro
		arp_hln = "0x%0.2X" % arp_hln
		arp_pln = "0x%0.2X" % arp_pln
		arp_op = "0x%0.4X" % arp_op
		arp_sha = ':'.join( [ "%0.2X" % ch for ch in arp_sha ] )
		arp_spa = '.'.join( [ str(d) for d in arp_spa ] )
		arp_tha = ':'.join( [ "%0.2X" % ch for ch in arp_tha ] )
		arp_tpa = '.'.join( [ str(d) for d in arp_tpa ] )
		
		# add human values
		op_str = self.getOp(op=arp_op)
			
		# Decode OK, create template 
		arp_tpl = templates.arp(hrd=arp_hrd, pro=arp_pro, hln=arp_hln, pln=arp_pln, op=arp_op, 
													sha=arp_sha, spa=arp_spa, tha=arp_tha, tpa=arp_tpa, opString=op_str)
		
		# add padding if exist
		if len(data_upper):
			arp_tpl.addKey('padding', data_upper )
			arp_tpl.addKey('padding-length', len(data_upper) )
		
		# add the raw data  to the layer
		arp_tpl.addRaw(arp)
		
		# finally prepare the summary
		if arp_op == OP_REQUEST:
			summary = 'Who has %s? Tell %s' % (arp_tpa, arp_spa)
		elif arp_op == OP_REPLY:
			summary = '%s is at %s' % (arp_spa, arp_sha)
		else:
			summary = 'unknown op %s' % arp_op
			
		return arp_tpl, summary