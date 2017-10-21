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

from TestExecutorLib.TestExecutorLib import doc_public

from sample import *
import random

class Noise(Sample):
	@doc_public
	def __init__(self, rate, parent, name=None, debug=False, amplitude=100, bits=SIGNED_16BITS):
		"""
		Noise generator

		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param rate: rate in Hz
		@type rate:	integer		

		@param amplitude: amplitude in percent (default=100)
		@type amplitude: integer	

		@param bits: SutLibraries.Media.SIGNED_16BITS (default) | SutLibraries.Media.SIGNED_8BITS | SutLibraries.Media.UNSIGNED_16BITS | SutLibraries.Media.UNSIGNED_8BITS
		@type bits: string		
		"""
		Sample.__init__(self, parent=parent, debug=debug, rate=rate, amplitude=amplitude, bits=bits, name=name)
	@doc_public
	def setRate(self, rate):
		"""
		Set the rate in Hz
		
		@param rate: rate in Hz
		@type rate:	integer		
		"""
		Sample.setRate(self, rate=rate)
	@doc_public
	def setAmplitude(self, amplitude):
		"""
		Set the amplitude of the noise in percent
		
		@param amplitude: amplitude in percent
		@type amplitude: integer		
		"""
		Sample.setAmplitude(self, amplitude=amplitude)	
	@doc_public
	def setBits(self, bits):
		"""
		Set the number of bits by sample
		
		@param bits: SutLibraries.Media.SIGNED_16BITS | SutLibraries.Media.SIGNED_8BITS | SutLibraries.Media.UNSIGNED_16BITS | SutLibraries.Media.UNSIGNED_8BITS
		@type bits: string			
		"""
		Sample.setBits(self, bits=bits)
	@doc_public
	def silence(self, duration):
		"""
		Returns a silence sample
		
		@param duration: duration in milliseconds
		@type duration: integer		
		
		@return: values sample 
		@rtype: list of integer
		"""		
		ret = []
		T = 1.0/self.rate
		N = self.rate*duration//1000 # number of samples
		for n in xrange(N):
			ret.append( 0 )
		return ret
	@doc_public
	def white(self, duration):
		"""
		Returns a white noise sample
		
		@param duration: duration in milliseconds
		@type duration: integer		
		
		@return: values sample 
		@rtype: list of integer
		"""
		scale = maxv(numbits=self.bits) 
		
		ret = []
		T = 1.0/self.rate
		N = self.rate*duration//1000 # number of samples
		for n in xrange(N):
			t = n*T
			# Generates a uniform random number between 0 and 2
			v = 1 - random.uniform(0,2) # 1 - rand(2)
			A = scale*(self.amplitude/100)
			s = A*v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def vinyl(self, duration, x=0.25, y=0.02, f=10 ):
		"""
		Returns a vinyl noise sample
		
		@param duration: duration in milliseconds
		@type duration: integer	
	
		@param f: frequency (default=10)
		@type f: integer	
		
		@param y: hiss (default=0.02)
		@type y: float

		@param x: pop (default=0.25)
		@type x: float
		
		@return: values sample 
		@rtype: list of integer
		"""
		scale = maxv(numbits=self.bits)
	
		ret = []
		T = 1.0/self.rate
		N = self.rate*duration//1000 # number of samples
		for n in xrange(N):
			t = n*T
			v = random.uniform(0,x) * (random.uniform(0, 1/T/f) < 1 and 1 or 0) # (rand(x)*(rand(1/T/f)<1))+(rand(y)-y/2)
			v += ( random.uniform(0,y) - y/2 )
			A = scale*(self.amplitude/100)
			s = A*v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret