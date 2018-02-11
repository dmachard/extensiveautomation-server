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

keypad =   [ 
				['1','2','3','A'],
				['4','5','6','B'],
				['7','8','9','C'],
				['*','0','#','D']
			]
F1 = [ 697, 770, 852, 941 ]
F2 = [ 1209, 1336, 1477, 1633 ]

def pressKey(symbol):
	"""
	@return: f1 and f2
	@rtype:	tuple 	
	"""
	f1 = 0 # low frequency
	f2 = 0 # high frequency
	for i in xrange(len(keypad)):
		for j in xrange(len(keypad[i])):
			if keypad[i][j] == symbol:
				f1 = F1[j]
				f2 = F2[j]
	return f1, f2

def tone(f1, f2, duration, rate, volume=100):
	"""
	@param f1: low frequency in Hz
	@type f1:	integer	

	@param f2: high frequency in Hz
	@type f2:	integer	
	
	@return: 16-bit linear, signed: -32768...+32767
	@rtype:	list of integer
	"""
	# scale 16-bit linear, signed: -32768...+32767
	scale = 0x7FFF #16-bit unsigned short
	ret = []
	T = 1.0/rate
	N = rate*duration//1000 # number of samples
	for n in xrange(N):
		t = n*T
		v = (math.sin(t*f1*2*math.pi)+math.sin(t*f2*2*math.pi))/2
		s = scale * float(volume) / 100 *  v
		ret.append( int(s) )
	return ret

# Countries
UE = 0
US = 1
UK = 2

# Special Information Tones
SIT_RO = 0 # Reorder: Incomplete digits, internal office or feature failure
SIT_RO2 = 1 # Reorder: Call failure, no wink or partial digits received
SIT_VC = 2 # Vacant Code: Unassigned
SIT_NC = 3 # No Circuit: All circuits busy
SIT_NC2 = 4 # No Circuit: All circuits busy
SIT_IC = 5 # Intercept: Number changed or disconnected
SIT_IO = 6 # Ineffective/Other: General misdialing, coin deposit required or other failure
SIT_FU = 7 # Future Use: Reserved for future use.

# Dial tones object
class DialTones(Sample):
	@doc_public
	def __init__(self, parent, name=None, debug=False, rate=8000, volume=100):
		"""
		Dial tones generator
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param rate: rate in Hz (default=8000)
		@type rate:	integer

		@param volume: volume in percent (default=100)
		@type volume: integer
		"""
		Sample.__init__(self, parent=parent, debug=debug, rate=rate, amplitude=volume, bits=SIGNED_16BITS, name=name)
	@doc_public
	def setRate(self, rate):
		"""
		Set the rate in Hz
		
		@param rate: rate in Hz
		@type rate:	integer		
		"""
		Sample.setRate(self, rate=rate)
	@doc_public
	def setVolume(self, volume):
		"""
		Set the volume in percent
		
		@param volume: volume in percent
		@type volume: integer		
		"""
		Sample.setAmplitude(self, amplitude=volume)
	@doc_public
	def specialInformationTone(self, code=SIT_RO):
		"""
		Returns a special information tone, this signal consisting of three rising tones indicating a call has failed

		SIT_RO: Reorder: incomplete digits, internal office or feature failure
		SIT_RO2: Reorder: call failure, no wink or partial digits received
		SIT_VC: Vacant Code: unassigned
		SIT_NC: No Circuit: all circuits busy
		SIT_NC2: No Circuit: all circuits busy
		SIT_IC: Intercept: number changed or disconnected
		SIT_IO: Ineffective/Other: general misdialing, coin deposit required or other failure
		SIT_FU: Future Use: reserved for future use.
		
		@param code: SutLibraries.Media.SIT_RO (default) | SutLibraries.Media.SIT_RO2 | SutLibraries.Media.SIT_VC | SutLibraries.Media.SIT_NC | SutLibraries.Media.SIT_NC2 | SutLibraries.Media.SIT_IC | SutLibraries.Media.SIT_IO | SutLibraries.Media.SIT_FU
		@type code:	integer
		
		@return: signed 16 bit PCM values sample 
		@rtype: list of integer	
		"""
		# initialize frequencies and durations
		seg1_fl = 913.8
		seg1_fh = 985.2
		
		seg2_fl = 1370.6
		seg2_fh = 1428.5
		
		seg3_fl = 1776.7
		seg3_fh = 0
		
		seg_short = 276
		seg_long = 380
		
		silence = tone(f1=0, f2=0, duration=30, rate=self.rate, volume=self.amplitude)
		
		if code==SIT_RO: # short, long, long 	low, high, low
			sample = tone(f1=seg1_fl, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fh, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
		elif code==SIT_RO2: # short, long, long 	high, low, low
			sample = tone(f1=seg1_fh, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
		elif code==SIT_VC: # long, short, long 	high, low, low
			sample = tone(f1=seg1_fh, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fl, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
		elif code==SIT_NC: # long, long, long 	high, high, low
			sample = tone(f1=seg1_fh, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fh, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )		
		elif code==SIT_NC2: # long, long, long 	low, low, low
			sample = tone(f1=seg1_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )				
		elif code==SIT_IC: # short, short, long 	low, low, low
			sample = tone(f1=seg1_fl, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fl, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )	
		elif code==SIT_IO: # long, short, long 	low, high, low
			sample = tone(f1=seg1_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fh, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )	
		elif code==SIT_FU: # 	short, short, long 	high, high, low
			sample = tone(f1=seg1_fh, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude)
			sample.extend( silence )
			sample.extend( tone(f1=seg2_fh, f2=0, duration=seg_short, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )
			sample.extend( tone(f1=seg3_fl, f2=0, duration=seg_long, rate=self.rate, volume=self.amplitude) )
			sample.extend( silence )				
		else:
			raise Exception( 'code %s not supported' % code )
		return sample
	@doc_public
	def busyTone(self, country=UE):
		"""
		Returns a busy tone signal with just one ON/OFF sample
		
		In North America (US), a busy tone is defined as having frequency components of 480 and 620 Hz at a cadence of 0.5 sec ON and 0.5 sec OFF.
		
		In the United Kingdom (UK) , busy tone consists of a single 400 Hz tone with a cadence of 0.375 sec ON and 0.375 sec OFF.
		
		Most European (UE) countries use a single precise frequency of 425 Hz with a cadence of 0.5 sec ON and 0.5 sec OFF.
		
		@param country: SutLibraries.Media.UE (default) | SutLibraries.Media.US | SutLibraries.Media.UK
		@type country:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer		
		"""
		if country == UE :
			fl = 425; fh = 0;
			on = 500; off = 500;
		elif country == US:
			fl = 480; fh = 620;
			on = 500; off = 500;
		elif country == UK:
			fl = 400; fh = 0;
			on = 325; off = 325;
		else:
			raise Exception( 'country %s not supported' % country )
		
		sample = tone(f1=fl, f2=fh, duration=on, rate=self.rate, volume=self.amplitude)
		sample.extend( tone(f1=0, f2=0, duration=off, rate=self.rate, volume=self.amplitude) )
		return sample
	@doc_public
	def ringbackTone(self, country=UE):
		"""
		Returns a ringback tone signal with just one ON/OFF sample, except for UK it is a double ON/OFF
		
		In North America (US), a ringback tone is defined as having frequency components of 440 and 480 Hz at a cadence of 2 sec ON and 4 sec OFF.
		
		Most European (UE) countries use a single precise frequency of 425 Hz with a cadence at a cadence of 1 sec ON and 4 sec OFF.
		
		In the United Kingdom (UK), a ringback tone is defined as having frequency components of 440 and 450 Hz 
		at a cadence of 0.4 sec ON and 0.2 sec OFF and 0.4 sec ON and 2 sec OFF.
		
		@param country: SutLibraries.Media.UE (default) | SutLibraries.Media.US | SutLibraries.Media.UK
		@type country:	integer
		
		@return: signed 16 bit PCM values sample 
		@rtype: list of integer			
		"""
		if country == UE :
			fl = 425; fh = 0;
			on = 1000; off = 4000;
		elif country == US:
			fl = 440; fh = 480;
			on = 2000; off = 4000;
		elif country == UK:
			fl = 400; fh = 450;
			on = 400; off = 200; off2 = 2000;
		else:
			raise Exception( 'country %s not supported' % country )
		
		sample = tone(f1=fl, f2=fh, duration=on, rate=self.rate, volume=self.amplitude)
		sample.extend( tone(f1=0, f2=0, duration=off, rate=self.rate, volume=self.amplitude) )
		if country == UK:
			sample.extend( tone(f1=fl, f2=fh, duration=on, rate=self.rate, volume=self.amplitude) )
			sample.extend( tone(f1=0, f2=0, duration=off2, rate=self.rate, volume=self.amplitude) )			
		return sample
	@doc_public
	def dialTone(self, country=UE):
		"""
		Returns a continuous dial tone signal of one second.
		
		In North America (US) and in the United Kingdom (UK), a dial tone is defined as having frequency components of 350 and 440 Hz.
		Most European (UE) countries use a single precise frequency of 425 Hz.
		
		@param country: UE (default) | US | UK
		@type country:	integer
		
		@return: signed 16 bit PCM values sample 
		@rtype: list of integer			
		"""
		if country == UE :
			fl = 425; fh = 0;
		elif country == US:
			fl = 350; fh = 440;
		elif country == UK:
			fl = 350; fh = 440;
		else:
			raise Exception( 'country %s not supported' % country )
		
		sample = tone(f1=fl, f2=fh, duration=1000, rate=self.rate, volume=self.amplitude)
		return sample
	@doc_public
	def pressKeys(self, symbols, duration=500):
		"""
		Returns a signal representing each pressed keys
		
		@param symbols: example '9876543'
		@type symbols:	string		

		@param duration: duration in milleseconds per symbol (default=500)
		@type duration:	integer
		
		@return: signed 16 bit PCM values sample 
		@rtype: list of integer		
		"""
		if not isinstance(symbols, str):
			raise Exception('bad type')
		sample = []
		for s in symbols:
			fl, fh = pressKey(symbol=s)
			sample.extend( tone(f1=fl, f2=fh, duration=duration, rate=self.rate, volume=self.amplitude) )
		return sample
	@doc_public
	def press0(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <0>
		This tone is defined as having frequency components of 941 and 1336 Hz 
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer
		
		@return: signed 16 bit PCM values sample 
		@rtype: list of integer		
		"""
		f1, f2 = pressKey(symbol='0')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press1(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <1>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer		

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='1')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press2(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <2>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer		

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer		
		"""
		f1, f2 = pressKey(symbol='2')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press3(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <3>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='3')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press4(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <4>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='4')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press5(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <5>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='5')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press6(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <6>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='6')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press7(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <7>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='7')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press8(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <8>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='8')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def press9(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <9>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='9')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def pressA(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key A
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='A')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def pressB(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key B
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer	

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='B')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def pressC(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key C
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='C')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def pressD(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key D
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer
	
		@return: signed 16 bit PCM values sample 
		@rtype: list of integer	
		"""
		f1, f2 = pressKey(symbol='D')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def pressStar(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <*>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='*')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)
	@doc_public
	def pressPound(self, duration=500):
		"""
		Returns a continuous tone signal representing the pressing on the key <#>
		
		@param duration: duration in milleseconds (default=500)
		@type duration:	integer

		@return: signed 16 bit PCM values sample 
		@rtype: list of integer
		"""
		f1, f2 = pressKey(symbol='#')
		return tone(f1=f1, f2=f2, duration=duration, rate=self.rate, volume=self.amplitude)