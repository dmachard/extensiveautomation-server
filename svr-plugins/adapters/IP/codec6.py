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

import sys
import struct

try:
	import common
except ImportError: # python3 support
	from . import common

# http://www.ietf.org/rfc/rfc2460.txt

# ip header size
IPV6_LEN = 40 # 40 bytes

#IPv6 Header Format
#
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |Version| Traffic Class |           Flow Label                  |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |         Payload Length        |  Next Header  |   Hop Limit   |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                                                               |
#   +                                                               +
#   |                                                               |
#   +                         Source Address                        +
#   |                                                               |
#   +                                                               +
#   |                                                               |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                                                               |
#   +                                                               +
#   |                                                               |
#   +                      Destination Address                      +
#   |                                                               |
#   +                                                               +
#   |                                                               |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class CodecV6(object):
	def __init__(self, parent):
		"""
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.info = parent.info
		
	def encode(self, ip_tpl):
		"""
		"""
		pass
		
	def decode(self, ip):
		"""
		"""	
		# Extract the fixed header = 40 octets
		# 2 * H = 4
		# H + B + B = 4
		# 8 * H + 8 * H = 32
		ip_header = struct.unpack('!2HH2B8H8H', ip[:IPV6_LEN])
		
		## Payload Length: 16-bit unsigned integer. Length of the IPv6 payload, i.e., 
		## the rest of the packet following this IPv6 header, in octets.
		pl = ip_header[2]

		## Next Header: 8-bit selector.  Identifies the type of header immediately following the IPv6 header. 
		## Uses the same values as the IPv4 Protocol field [RFC-1700 et seq.].
		nh = ip_header[3]
		
		## Hop Limit 8-bit unsigned integer.  Decremented by 1 by each node that forwards the packet. 
		## The packet is discarded if Hop Limit is decremented to zero.
		hl = ip_header[4]
		
		## Source Address:  128-bit address of the originator of the packet
		src = ip_header[5:12]

		## Destination Address:  128-bit address of the intended recipient of the
		dst = ip_header[13:20]
		