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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import struct
import array

__NAME__="""SUM"""

class Checksum(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Computing checksum: 16 bit one's complement of the one's complement sum of all 16 bit words
		Used with ICMPv4, IPv4, TCP and UDP. Checksum size is of 2 octets.
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.pad_byte = '0x00'
	@doc_public
	def compute (self, data, checksum_offset=0, hexdigit=False):
		"""
		Returns the checksum  of the data passed as argument
		The pad is not transmitted as part of the segment.  
		While computing the checksum, the checksum field its elf is replaced with zeros
		
		@param data: data 
		@type data: string
		
		@param checksum_offset:  checksum offset in data
		@type checksum_offset: integer
		
		@param hexdigit: hexa representation (default=False) 
		@type hexdigit: boolean
		
		@return: checksum
		@rtype: integer/string
		"""
		sum = 0
		# add pad 
		if len(data) % 2 != 0:
				data = ''.join( [data, struct.pack('!B', int(self.pad_byte, 16 )) ] )
		# 32 bits words
		words = array.array('h', data)
		# the checksum field must to be initialized to zeros before checksum calculation
		words[checksum_offset] = 0
		try:
			for word in words:
				sum = sum + (word & 0xffff)
			hi = sum >> 16
			lo = sum & 0xffff
			sum = hi + lo
			sum = sum + (sum >> 16)
			sum = (~sum) & 0xffff # return ones complement 
			sum = sum >> 8 | ((sum & 0xff) << 8)  # Swap bytes
		except Exception as e:
			self.error( 'compute checksum: %s' % str(e) )
		else:
			if hexdigit:
				sum = "%0.4x" % sum
		return sum