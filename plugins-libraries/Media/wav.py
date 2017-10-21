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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

__NAME__="""WAV"""

import math
import struct

# Format types
WAVE_FORMAT_PCM		= 0x0001
WAVE_FORMAT_PCMA	= 0x0006
WAVE_FORMAT_PCMU	= 0x0007

# Channel types
CHANNELS_MONO		= 0x0001
CHANNELS_STEREO		= 0x0002

# Precision
WAV_UNSIGNED_8BITS		= 8
WAV_SIGNED_16BITS		= 16

class WavContainer(TestLibraryLib.Library):
	@doc_public
	def __init__(self,  parent, name=None, debug=False, format=WAVE_FORMAT_PCM, 
												channels=CHANNELS_MONO, rate=44100, bits=WAV_SIGNED_16BITS, samples=[], shared=False):
		"""
		Wav file container
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param format: SutLibraries.Media.WAVE_FORMAT_PCM (default) | SutLibraries.Media.WAVE_FORMAT_PCMA | SutLibraries.Media.WAVE_FORMAT_PCMU
		@type format:	integer	

		@param channels: SutLibraries.Media.CHANNELS_MONO | SutLibraries.Media.CHANNELS_STEREO
		@type channels: integer		

		@param rate: rate in Hz (default=44100)
		@type rate:	integer	
		
		@param bits: SutLibraries.Media.WAV_UNSIGNED_8BITS | SutLibraries.Media.WAV_SIGNED_16BITS
		@type bits:	integer

		@param samples:
		@type samples: list
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		# wave format
		self.FileID = "RIFF"
		self.FileSize = 0
		self.Format = "WAVE"

		# audio description
		self.FmtID = "fmt "
		self.FmtSize = 16
		self.AudioFormat = format
		self.NumChannels = channels
		self.SampleRate = rate
		self.ByteRate = 0
		self.BlockAlign = 0
		self.BitsPerSample = bits

		# datas
		self.DataID = "data"
		self.DataSize = 0
		self.Data = samples

	def setFileSize(self):
		"""
		"""
		self.FileSize = 4 + (8 + self.FmtSize) + (8 + self.DataSize)

	def setByteRate(self):
		"""
		"""
		self.ByteRate = self.SampleRate * self.NumChannels * self.BitsPerSample/8
	
	def setBlockAlign(self):
		"""
		"""
		self.BlockAlign = self.NumChannels * self.BitsPerSample/8
	
	def setDataSize(self):
		"""
		"""
		self.DataSize = len(self.Data) * self.NumChannels * self.BitsPerSample/8

	def getHeader(self):
		"""
		"""
		self.setDataSize()
		self.setFileSize()
		self.setByteRate()
		self.setBlockAlign()
		wavHeader = [ struct.pack( '>4s', self.FileID ) ]
		wavHeader.append( struct.pack( '<i', self.FileSize ) )
		wavHeader.append( struct.pack( '>4s4s', self.Format, self.FmtID ) )
		wavHeader.append( struct.pack( '<ihhiihh', self.FmtSize, self.AudioFormat, self.NumChannels, self.SampleRate,
							self.ByteRate, self.BlockAlign, self.BitsPerSample ) )
		wavHeader.append( struct.pack( '>4s', self.DataID ) )
		wavHeader.append( struct.pack( '<i', self.DataSize ) )
		return ''.join(wavHeader)

	@doc_public
	def setDataRaw(self, dataRaw):
		"""
		Set raw data
		
		@param dataRaw: raw data
		@type dataRaw: string				
		"""
		self.Data = dataRaw

	def getData(self):
		"""
		"""
		if isinstance(self.Data, list):
			return ''.join(self.Data)
		else:
			return self.Data
	@doc_public
	def getRaw(self):
		"""
		Returns raw data
		
		@return: raw data
		@rtype: string
		"""
		wav = [ self.getHeader(), self.getData() ] 
		return ''.join(wav)
		
	def write(self, filename):
		"""
		@param filename:
		@type filename:			
		"""
		wav = [ self.getHeader(), self.getData() ] 
		f = open( "%s.wav" % filename, 'wb')
		f.write( ''.join(wav)  )
		f.close()
