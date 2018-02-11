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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import base64 

__NAME__="""BASE64"""

class BASE64(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		JSON Decoder/Encoder
		
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
		
	@doc_public
	def encode(self, data, urlsafe=False):
		"""
		Encode a string in base 64

		@param data: string in clear
		@type data: string
	
		@param urlsafe: url safe (default=False)
		@type urlsafe: boolean
		
		@return: string encoded
		@rtype: string
		"""
		if urlsafe:
			return base64.urlsafe_b64encode( data )
		else:
			return base64.b64encode( data )
		
	@doc_public
	def decode(self, data, urlsafe=False, padding=False):
		"""
		Decode a string encoded in base 64
	
		@param data: string encoded
		@type data: string
	
		@param urlsafe: url safe (default=False)
		@type urlsafe: boolean
	
		@param padding: adding missing padding. (default=False)
		@type padding: boolean
		
		@return: string in clear
		@rtype: string
		"""
		if padding:
			_data = data + b'=' * (-len(data) % 4)
		else:
			_data = data
		if urlsafe:
			return base64.urlsafe_b64decode(_data)
		else:
			return base64.b64decode( _data )
		