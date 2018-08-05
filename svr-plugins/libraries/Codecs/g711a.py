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

__NAME__="""G711A"""

A_G711A = 8

def val_seg (val):
	"""
	"""
	r = 1
	
	val >>= 8
	if (val & 0xf0):
		val >>= 4
		r += 4
	if (val & 0x0c):
		val >>= 2
		r += 2
	if (val & 0x02):
		r += 1
	return r
	
class G711A(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		A-Law audio encoder and decoder.
		
		The A-law data format is specified by the CCITT Recommendation G.711. This specification is the telephony standard used in
		Europe. It is a non-linear (logarithmic) compression/decompression format that
		dedicates more digitization codes to lower amplitude analog signals with the sacrifice
		of precision on higher amplitude signals.
		
		The format of an 8-bit A-law encoded value is XYYYZZZZ, where X is the sign bit,
		YYY is the (3-bit) segment number, and ZZZZ is the (4-bit) position within the segment
		
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
	def encode (self, pcm_val):
		"""
		Convert a 16-bit linear PCM value to 8-bit A-law

		@param pcm_val: signed 16 bit linear
		@type pcm_val: integer

		@return: unsigned 8 bit alaw
		@rtype: integer
		"""
		if (pcm_val >= 0):
			mask = 0xD5
		else:
			mask = 0x55
			pcm_val = -pcm_val
			if (pcm_val > 0x7fff):
				pcm_val = 0x7fff

		if (pcm_val < 256):
			aval = pcm_val >> 4
		else:
			seg = val_seg (pcm_val)
			aval = (seg << 4) | ((pcm_val >> (seg + 3)) & 0x0f)
		return aval ^ mask
	@doc_public	
	def decode (self, a_val):
		"""
		Convert an A-law value to 16-bit linear PCM
	
		@param a_val: unsigned 8 bit alaw 
		@type a_val: integer

		@return: signed 16 bit linear
		@rtype: integer
		"""
		a_val ^= 0x55
		t = a_val & 0x7f
		if (t < 16):
			 t = (t << 4) + 8
		else:
			seg = (t >> 4) & 0x07
			t = ((t & 0x0f) << 4) + 0x108
			t <<= seg - 1
		
		return (a_val & 0x80) and t or -t