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

__NAME__="""G771U"""

A_G711U = 0

BIAS		= 0x84 # define the add-in bias for 16 bit samples
CLIP		= 32635

EXP_LUT_ENC = [ 
		0, 0, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3,
		4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
		5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
		5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
		6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
		6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
		6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
		6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
		7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7
]

EXP_LUT_DEC = [ 
	0, 132, 396, 924, 
	1980, 4092, 8316, 16764
]

class G711U(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		U-Law audio encoder and decoder.

		The u-law data format is specified by the CCITT Recommendation G.711.
		This specification is the telephony standard used in the
		United States and Japan. It is a non-linear (logarithmic) compression/decompression format
		that dedicates more digitization codes to lower amplitude analogue signals with the
		sacrifice of precision on higher amplitude signals.
		
		The format of an 8-bit u-law encoded value is XYYYZZZZ, where X is the sign bit, YYY is
		the (3-bit) segment number, and ZZZZ is the (4-bit) position within the segment.
		
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
	def encode(self, pcm_val, zero_trap=False):
		"""
		Convert a 16-bit linear PCM value to 8 bit U-law

		@param pcm_val: signed 16 bit linear
		@type pcm_val: integer

		@param zero_trap: turn on the trap as per the MIL-STD
		@type zero_trap: boolean
		
		@return: unsigned 8 bit ulaw
		@rtype: integer
		"""
		# set aside the sign
		sign = (pcm_val >> 8) & 0x80 
		if sign != 0:
			pcm_val = -pcm_val # get magnitude
		
		# sample can be zero because we can overflow in the inversion,
		# checking against the unsigned version solves this
		if pcm_val > CLIP:
			pcm_val = CLIP  # clip the magnitude
		
		# convert from 16 bit linear to ulaw
		pcm_val = pcm_val + BIAS
		exponent = EXP_LUT_ENC[(pcm_val >> 7) & 0xFF]
		mantissa = (pcm_val >> (exponent + 3)) & 0x0F
		ulawbyte = sign | (exponent << 4) | mantissa
		
		# xor to invert
		ulawbyte ^= 0xFF
		
		# optional CCITT trap
		if zero_trap:
			if (ulawbyte == 0):
				ulawbyte = 0x02;         
		
		return ulawbyte
	@doc_public
	def decode(self, u_val):
		"""
		Convert an U-law value to 16-bit linear PCM
		
		@param u_val: unsigned 8 bit ulaw
		@type u_val: integer	

		@return: signed 16 bit linear
		@rtype: integer
		"""
		u_val ^= 0xFF
		sign = (u_val & 0x80)
		exponent = (u_val >> 4) & 0x07
		mantissa = u_val & 0x0F
		linear = EXP_LUT_DEC[exponent] + (mantissa << (exponent + 3))
		
		if sign != 0:
			linear = -linear
		return linear