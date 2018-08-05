#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import zlib

__NAME__="""CRC32"""

class CRC32(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, initialCrc=0xFFFF, shared=False):
		"""
		This library implements CRC-32 (Cyclic Redundancy Check) algorithm .
		(see ISO 3309)
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param initialCrc: initial crc (default=0xFFFF) 
		@type initialCrc: integer
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.initialCrc = initialCrc
	@doc_public
	def compute (self, data, hexdigit=False):
		"""
		Compute CRC-32, the 32-bit (4 octets) checksum of data, starting with an initial crc.
		
		@param data: data 
		@type data: string
		
		@param hexdigit: return hexadecimal representation (default=False) 
		@type hexdigit: boolean
		
		@return: md5 digest
		@rtype: string/string
		"""
		crc = zlib.crc32(data, self.initialCrc)
		if hexdigit:
			crc = "%08x" % crc
		return crc