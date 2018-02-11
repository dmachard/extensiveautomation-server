#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import zlib

__NAME__="""GZIP"""

class GZIP(TestLibrary.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Gzip library

		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibrary.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
	@doc_public
	def compress(self, data, level=6):
		"""
		Compress the data passed as argument
		
		@param data:  data to compress
		@type data: string

		@return: compressed data
		@rtype: string
		"""
		compressed =  zlib.compress(data, level)
		return compressed
	@doc_public
	def uncompress(self, data):
		"""
		Uncompress the data passed as argument
		
		@param data: data to decompress
		@type data: string
		
		@return: uncompressed data
		@rtype: string
		"""
		decompressed =  zlib.decompress(data)
		return decompressed