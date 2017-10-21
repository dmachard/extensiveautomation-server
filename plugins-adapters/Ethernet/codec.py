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

import struct

import templates
from oui import OUI

ALL     = "ALL"

IPv4    = "0x0800"
IPv6    = "0x86DD"
ARP     = "0x0806"
RARP    = "0x8035"
DOT1Q   = "0x8100"
SNMP    = "0x814C"

# http://standards.ieee.org/develop/regauth/ethertype/eth.txt
ETHER_TYPE_MAP = {}
ETHER_TYPE_MAP[IPv4]   = "IPv4" # Internet Protocol, Version 4
ETHER_TYPE_MAP[IPv6]   = "IPv6" # Internet Protocol, Version 6
ETHER_TYPE_MAP[ARP]    = "ARP" # Address Resolution Protocol
ETHER_TYPE_MAP[RARP]   = "RARP" # Reverse Address Resolution Protocol
ETHER_TYPE_MAP[DOT1Q]  = "802.1Q"  # VLAN-tagged frame
ETHER_TYPE_MAP[SNMP]   = "SNMP" # Simple Network Management Protocol

def conv_mac (mac):
	"""
	00:00:00:00:00:00 -> [ 0, 0, 0, 0, 0, 0 ]
	"""
	return [ int(x, 16) for x in mac.split(':') ]
	
class Codec(object):
	def __init__(self, parent, macResolution):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.info = parent.info
		
		self.mac_resolution = macResolution
		
	def encode(self, frame_tpl):
		"""
		"""
		hdrs_len = 14
		
		ether_layer = frame_tpl.get('ETHERNET-II')
		data = ether_layer.get('data')

		if isinstance(data, TestTemplatesLib.TemplateLayer):
			data = data.getName()
			ether_layer.get('data').addKey('length', str(len(data)) )
				
		src = ether_layer.get('mac-source')
		if isinstance(src, TestTemplatesLib.TemplateLayer):
			src = src.getName()
			
		dst = ether_layer.get('mac-destination')
		if isinstance(dst, TestTemplatesLib.TemplateLayer):
			dst = dst.getName()
			
		upper = ether_layer.get('protocol-upper')
		if isinstance(upper, TestTemplatesLib.TemplateLayer):
			upper = upper.getName()
		
		# set upper protocol name
		protocolUpper = None
		if ETHER_TYPE_MAP.has_key( upper ):
			protocolUpper = ETHER_TYPE_MAP[ upper ]
		if protocolUpper is not None:
			ether_layer.get('protocol-upper').addKey('string', protocolUpper)
		
		# set vendors
		vendorSrc = None
		vendorDst = None
		if self.mac_resolution:
			if OUI.has_key(dst):
				vendorDst = OUI[dst].title()
			if OUI.has_key(src):
				vendorSrc = OUI[src].title()
			if vendorSrc is not None:
				ether_layer.get('mac-source').addKey('vendor', vendorSrc)
			if vendorDst is not None:
				ether_layer.get('mac-destination').addKey('vendor', vendorDst)
			
		args = conv_mac(dst)
		args.extend( conv_mac(src) )
		args.append( int(upper, 16) )

		frame = [ struct.pack('!6B6BH', *args ) ]
		frame.append( data )
			
		# Encode OK
		frame_hex = ''.join(frame)
		return frame_hex, frame_hex[:hdrs_len]
			
	def decode(self, frame):
		"""
		"""
		# Unpack the first fourteen octets which are present in every ethernet frame
		hdrs_len = 14
		# B = 1 octet
		# H = 2 octets
		# 6*B + 6*B + H = 12
		ether_header = struct.unpack('!6B6BH', frame[:hdrs_len])
		data_upper = frame[hdrs_len:]

		## Destination Address. 6 bytes.
		## The address(es) are specified for a unicast, multicast (subgroup), or broadcast (an entire group).
		dst_mac = ether_header[0:6]
		dst_mac_str = ':'.join( [ "%0.2X" % ch for ch in dst_mac ] )
		key_dst = ':'.join( [ "%0.2X" % ch for ch in dst_mac[0:3] ] )
		
		## Source Address. 6 bytes.
		## The address is for a unicast (single computer or device).
		src_mac = ether_header[6:12]
		src_mac_str = ':'.join( [ "%0.2X" % ch for ch in src_mac ] )
		key_src = ':'.join( [ "%0.2X" % ch for ch in src_mac[0:3] ] )
		
		## EtherType. 16 bits. 
		## Which upper layer protocol will utilized the Ethernet frame.
		ethertype = ether_header[12:][0]
		ethertype = "0x%0.4X" % ethertype
		protocolUpper = None
		if ETHER_TYPE_MAP.has_key( ethertype ):
			protocolUpper = ETHER_TYPE_MAP[ ethertype]
		
		# set vendors
		vendorSrc = None
		vendorDst = None
		if self.mac_resolution:
			if OUI.has_key(key_dst):
				vendorDst = OUI[key_dst].title()
			if OUI.has_key(key_src):
				vendorSrc = OUI[key_src].title()
		
		# Decode OK, create template 
		ether_tpl = templates.ethernet(destAddr=dst_mac_str, srcAddr=src_mac_str, etherType=ethertype, 
																vendorDst=vendorDst, vendorSrc=vendorSrc, protocolUpper=protocolUpper,
																data=data_upper, size_data=len(data_upper)	)
																
		# add the raw data without upper data
		ether_tpl.addRaw(frame[:hdrs_len])
		
		return data_upper, ether_tpl