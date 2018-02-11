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

__NAME__="""SAMPLE"""

UNSIGNED_8BITS		= "u8" # 8-bit linear, unsigned: 0...255
UNSIGNED_16BITS		= "u16" #  16-bit linear, unsigned: 0...65535
SIGNED_8BITS		= "s8" # 8-bit linear, signed: -128...127
SIGNED_16BITS		= "s16" #  16-bit linear, signed: -32768...+32767

def maxv(numbits):
	scale = 0
	if numbits == SIGNED_16BITS:  scale = 0x7FFF
	elif numbits == SIGNED_8BITS:  scale = 0x7F
	elif numbits == UNSIGNED_16BITS:  scale = 0xFFFF
	elif numbits == UNSIGNED_8BITS:  scale = 0xFF
	else: raise Exception('numbits not supported: %s' % samplePrecision)
	return scale

# T: period
# f: frequency 
# A: amplitude

class Sample(TestLibraryLib.Library):
	def __init__(self, rate, parent, name=None, debug=False, amplitude=100, bits=SIGNED_16BITS, shared=False):
		"""
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
		self.rate = rate
		self.amplitude = float(amplitude)
		self.bits = bits

	def setRate(self, rate):
		"""
		"""
		self.rate = rate
		
	def setAmplitude(self, amplitude):
		"""
		"""
		self.amplitude = amplitude
		
	def setBits(self, bits):
		"""
		"""
		self.bits = bits