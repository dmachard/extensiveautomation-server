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
import common

__NAME__="""RC4"""

class RC4(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, hexKey=None, strKey=None, debug=False, shared=False):
		"""
		Implementation of the cipher RC4 (also known as ARC4 or ARCFOUR)
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param strKey: string key
		@type strKey: string/none
		
		@param hexKey: hexadecimal key
		@type hexKey: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.rounds = 256
		self.state = []
		self.keyStream = []
		self.key = [] # integer representation
		if hexKey is not None:
			self.setKey(hexKey=hexKey)
		if strKey is not None:
			self.setKey(strKey=strKey)
	@doc_public		
	def encrypt (self, strData=None, hexData=None, hexdigit=False):
		"""
		Encrypt the string data or hexa data string and return an encrypted string
		
		@param strData: data in clear
		@type strData: string/none

		@param hexData: data in clear with hexa representation (example: bbaa01ffef)
		@type hexData: string/none
		
		@param hexdigit: return hexadecimal representation (default=False) 
		@type hexdigit: boolean
		
		@return: encrypted data
		@rtype: string
		"""
		if not len(self.key):
			raise Exception('No key defined')
		
		if strData is None and hexData is None:
			raise Exception('No data defined')
			
		# initialize
		self.ksa()
		self.pgra()

		# convert data to a list of int
		data_int =  []
		if strData is not None: 
			for c in strData: data_int.append( ord(c) )
		if hexData is not None:
			data_int = common.decodeHex(hexData, 2)
			
		# xor	
		ret_int = []
		for a in xrange(len(data_int)): 
			ret_int.append( data_int[a]^self.keyStream[a] )
		
		ret = []
		if hexdigit:
			for d in ret_int: ret.append( "%02x" % d )
		else:
			for d in ret_int: ret.append( chr(d) )
		
		ret_str = ''.join(ret)	
		return ret_str
	@doc_public		
	def decrypt(self, strData=None, hexData=None):
		"""
		Decrypt the string data or hexa data string
		
		@param strData: data encrypted
		@type strData: string/none

		@param hexData: data in clear with hexa representation (example: bbaa01ffef)
		@type hexData: string/none

		@return: decrypted data
		@rtype: string
		"""
		if strData is None and hexData is None:
			raise Exception('No data defined')
		return self.encrypt(strData=strData, hexData=hexData)
	@doc_public
	def getKey(self, strKey=True, hexKey=False):
		"""
		Returns the key as string or hexadecimal representation
		
		@param strKey: string key
		@type strKey: boolean
		
		@param hexKey: hexadecimal key
		@type hexKey: boolean
		
		@return: key
		@rtype: string
		"""
		key = []
		if hexKey:
			for c in self.key: key.append( "%02x" % c )
		if strKey:
			for c in self.key: key.append(chr(c))
		return ''.join(key)
	@doc_public
	def setKey(self, hexKey=None, strKey=None):
		"""
		Set the key string or hexadecimal representation passed in argument
		
		@param strKey: string key
		@type strKey: string/none
		
		@param hexKey: hexadecimal key
		@type hexKey: string/none
		"""
		if strKey is not None:
			for c in strKey:
				self.key.append( ord(c) )
		elif hexKey is not None:
			self.key = common.decodeHex(hexKey, 2)
		else:
			raise Exception('No key defined')
			
	def ksa(self):
		"""
		The key-scheduling algorithm
		"""
		for i in xrange(0, self.rounds): self.state.append(i)
	
		j = 0
		for i in xrange(0, self.rounds):
			j = (j + self.state[i] + self.key[i % len(self.key)]) % self.rounds
			tmp_state = self.state[i]
			self.state[i] = self.state[j] 
			self.state[j] = tmp_state
	
	def pgra(self):
		"""
		The pseudo-random generation algorithm
		"""
		i = 0; j = 0;
		for x in xrange(self.rounds):
			i = (i+1) % self.rounds
			j = (j + self.state[i]) % self.rounds
			tmp_state = self.state[i]
			self.state[i] = self.state[j]
			self.state[j] = tmp_state
			self.keyStream.append( self.state[ (self.state[i] + self.state[j]) % self.rounds ] )