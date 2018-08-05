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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
import sys

import struct

SutLibraries = sys.modules['SutLibraries.%s' % TestLibraryLib.getVersion()]


__NAME__="""PAYLOADS"""

DEFAULT = 256*'\x01'

class DefaultPayloads(TestAdapterLib.Adapter):
	def __init__(self, parent, debug=False, codec=SutLibraries.Codecs.A_G711U, rate=8000):
		"""
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug)
		self.__testcase = parent
		self.__debugmode = debug
		self.rate = rate
		self.codec = codec

	def testcase(self):
		"""
		"""
		return self.__testcase
		
	def debugmode(self):
		"""
		"""
		return self.__debugmode
		
	def setCodec(self, codec):
		"""
		"""
		self.codec = codec

	def setRate(self, rate):
		"""
		"""
		self.rate = rate

	def getWhiteNoise(self, duration=500):
		"""
		"""
		self.debug( 'prepare write noise' )
		try:
			# generate samples
			noises = SutLibraries.Media.Noise(parent=self.testcase(), rate=self.rate)
			sample = noises.white(duration=duration)
		except Exception as e:
			self.error( str(e) )
		# encode and return it
		return self.encode(sample=sample)
		
	def getSine(self, frequency=1000, duration=500):
		"""
		"""
		self.debug( 'prepare wave sine' )
		try:
			# generate samples
			waves = SutLibraries.Media.Waves(parent=self.testcase(), rate=self.rate)
			sample = waves.sine(f=frequency, duration=duration)
		except Exception as e:
			self.error( str(e) )
			
		# encode and return it
		return self.encode(sample=sample)
	
	def getSilence(self):
		"""
		"""
		self.debug( 'prepare silence' )
		sample = [0]
		
		# encode and return it
		return self.encode(sample=sample)
		
	def encode(self, sample):
		"""
		"""
		self.debug( 'encode sample' )
		# encode and return it
		ret = []
		try:
			g711a = SutLibraries.Codecs.G711A(parent=self.testcase())
			g711u = SutLibraries.Codecs.G711U(parent=self.testcase())
			for fr in sample:
				if self.codec == SutLibraries.Codecs.A_G711A:
					encoded = g711a.encode(pcm_val=fr)
				elif self.codec == SutLibraries.Codecs.A_G711U:
					encoded = g711u.encode(pcm_val=fr)
				else:
					raise Exception('codec not supported: %s' % self.codec)
				ret.append( struct.pack('B',encoded) )
		except Exception as e:
			self.error( str(e) )
		return ''.join(ret)