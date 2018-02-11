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

from TestExecutorLib.TestExecutorLib import doc_public

from sample import *
import math

class Waves(Sample):
	@doc_public
	def __init__(self, rate, parent, name=None, debug=False, amplitude=100, bits=SIGNED_16BITS):
		"""
		Waves generator

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
	def sine(self, f, duration ):
		"""
		Return a sine wave

		@param f: frequency
		@type f: integer	
		
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
			vsin = math.sin(t*f*2*math.pi) # sin(2*pi*f*t)
			A = scale * ( self.amplitude / 100)
			s = A * vsin
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def square(self, f, duration ):
		"""
		Return a square wave

		@param f: frequency
		@type f: integer	
		
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
			v = int(t*f*2)%2 * 2-1  # int(2*t*f)%2*2-1
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def triange(self, f, duration ):
		"""
		Return a triange wave

		@param f: frequency
		@type f: integer	
		
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
			v = 1-2*abs(1-2*f*t%2)  # 1-2*abs(1-2*f*t%2)
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def sweep(self, duration ):
		"""
		Return a sweep wave 

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
			v = math.sin( math.pi*300*t**2 )  # sin(pi*300*t^2)
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def ping(self, f, duration ):
		"""
		Return a ping wave

		@param f: frequency
		@type f: integer	
		
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
			v = math.sin(2*math.pi*t*f)*math.exp(-t*4)  # sin(2*pi*t*f)*exp(-t*4)
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def overload(self, f, duration ):
		"""
		Return an overloaded wave

		@param f: frequency
		@type f: integer	
		
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
			v = math.sin(1000*t + math.sin(300*t*t)*5)  # sin(1000*t+sin(300*t*t)*5)
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def modulation(self, f, duration, x=2, y=4 ):
		"""
		Return a frequency modulated wave

		@param f: frequency
		@type f: integer	
		
		@param duration: duration in milliseconds
		@type duration: integer	

		@param y: at y percent
		@type y: float

		@param x: x Hz
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
			v = math.sin( 2*math.pi*f*t + f*math.sin(2*math.pi*t*x)*(float(y)/100)/x )  # sin(2*pi*f*t+f*sin(2*pi*t*x)*(y/100)/x)
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def sonar(self, f, duration ):
		"""
		Return a sonar wave

		@param f: frequency
		@type f: integer	
		
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
			v = math.sin(2*math.pi*t*2000)*math.exp(-t*3)*(math.sin(2*math.pi*3*t)+math.sin(2*math.pi*23*t))/2  # sin(2*pi*t*2000)*exp(-t*3)*(sin(2*pi*3*t)+sin(2*pi*23*t))/2
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret
	@doc_public
	def deep(self, f, duration ):
		"""
		Return a deep wave

		@param f: frequency
		@type f: integer	
		
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
			v = math.sin(2*math.pi*2*t*(1+(1+math.sin(2*math.pi*t*50))/4))*math.exp(-t*0.6) # sin(2*pi*2*t*(1+(1+sin(2*pi*t*50))/4))*exp(-t*.6)
			A = scale * ( self.amplitude / 100)
			s = A * v
			if scale == 0xFFFF or scale == 0xFF:
				s = (s + scale) / 2
			ret.append( int(s) )
		return ret