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

import base64
from Crypto import Random
import Crypto.Cipher.AES as AESCRYPTO

__NAME__="""AES"""

class AES(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, hexKey=None, strKey=None, debug=False, shared=False):
		"""
		Implementation of the cipher AES
		
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
		self.BLOCK_SIZE = 32
		self.PADDING = '{'
		self.key = []

		# set the key
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
			
		# encrypt str
		if strData is not None: 
			raw = strData
		
		if hexData is not None: 
			data_int = common.decodeHex(hexData, 2)
			data_str = []
			for d in data_int: data_str.append( chr(d) )
			raw = ''.join(data_str)

		raw = self.pad(raw)
		iv = Random.new().read(AESCRYPTO.block_size)
		cipher = AESCRYPTO.new( self.getKey(strKey=True), AESCRYPTO.MODE_CBC, iv )	
		cipher_ret = base64.b64encode(iv + cipher.encrypt(raw))
			
		# convert to int
		ret_int =  []
		for c in cipher_ret: ret_int.append( ord(c) )
		
		# convert to hex or not ?
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
		if not len(self.key):
			raise Exception('No key defined')
		
		if strData is None and hexData is None:
			raise Exception('No data defined')

		# encrypt
		if strData is not None: 
			enc = data_str
			
		if hexData is not None: 
			data_int = common.decodeHex(hexData, 2)
			data_str = []
			for d in data_int: data_str.append( chr(d) )
			enc = ''.join(data_str)
		
		enc = base64.b64decode(enc)
		iv = enc[:AESCRYPTO.block_size]
		cipher = AESCRYPTO.new(self.getKey(strKey=True), AESCRYPTO.MODE_CBC, iv)
		cipher_ret = self.unpad(cipher.decrypt(enc[AESCRYPTO.block_size:]))
		
		return cipher_ret
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

	def pad(self, s):
		"""
		Pad
		"""
		return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)

	def unpad(self, s):
		"""
		Unpad
		"""
		return s[:-ord(s[len(s)-1:])]