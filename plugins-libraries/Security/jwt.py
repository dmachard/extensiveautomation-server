#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

__NAME__="""JWT"""

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import HMAC, SHA512, SHA384, SHA256

import sys
Codecs = sys.modules['SutLibraries.%s.Codecs' % TestLibrary.getVersion()]

class JWT(TestLibrary.Library):
	@doc_public	
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		JWT library	
		Supported signatures:
		HS256 	HMAC using SHA-256 hash algorithm
		HS384 	HMAC using SHA-384 hash algorithm
		HS512 	HMAC using SHA-512 hash algorithm
		RS256 	RSA using SHA-256 hash algorithm
		RS384 	RSA using SHA-384 hash algorithm
		RS512 	RSA using SHA-512 hash algorithm

		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibrary.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.alg_supported = {
							"HS256":  SHA256,
							"HS384":  SHA384,
							"HS512":  SHA512,
							
							"RS256":  SHA256,
							"RS384":  SHA384,
							"RS512":  SHA512
				}
		self.LIB_BASE64 = Codecs.BASE64(parent=parent , name=None, debug=False, shared=False)
		self.LIB_JSON = Codecs.JSON(parent=parent, name=None, debug=False, ignoreErrors=False, shared=False)
	@doc_public	
	def encode(self, payload, alg="RS256", key=None):
		"""
		Encode the provided payload and return a valid token

		@param payload: payload in dict format
		@type payload: dict
		
		@param alg: algorithm to use for signature (default=RS256)
		@type alg: string

		@param key: key to use for signature (default=None)
		@type key: none/string
		
		@return: encoded token
		@rtype: string
		"""
		header = {'typ': 'JWT', 'alg': alg}
		
		# encode 
		header_encoded = self.LIB_BASE64.encode(self.LIB_JSON.encode(header).encode('utf-8'), urlsafe=True)
		payload_encoded = self.LIB_BASE64.encode(self.LIB_JSON.encode(payload).encode('utf-8'), urlsafe=True)
		segments = [ header_encoded, payload_encoded ]

		signing= b'.'.join(segments)
		if key is None: raise ValueError("key is required")

		if alg in [ "RS256", "RS384", "RS512"]:
			signature = self.rsa_sign(message=signing, key=key, hash=alg)
		elif alg in [ "HS256", "HS384", "HS512"]:
			signature = self.hmac_sign(message=signing, key=key, hash=alg)
		else:
			raise ValueError("alg not supported %s" % alg)
			
		segments.append( self.LIB_BASE64.encode(signature, urlsafe=True))
		
		return b'.'.join(segments)
	@doc_public	
	def decode(self, token, verify=False, key=None):
		"""
		Decode the provided token and check the signature 

		@param token: jwt token to decode
		@type token: string
		
		@param verify: verify the signature (default=False)
		@type verify: boolean

		@param key: key to check the signature (default=None)
		@type key: none/string
		
		@return: (header, payload, isvalid)
		@rtype: tuple of [str,str,bool]
		"""
		# check format
		if token.count(b'.') != 2: raise ValueError("Wrong number of segments in token")
		encoded_header, encoded_payload, signature = token.split(b'.')

		# decode each parts of the token
		signature  = self.LIB_BASE64.decode(data=signature, urlsafe=True, padding=True)
		
		decoded_header  = self.LIB_BASE64.decode(data=encoded_header, urlsafe=True, padding=True)
		header =  self.LIB_JSON.decode(decoded_header.decode('utf-8'))
		if 'alg' not in  header: raise ValueError("The \"alg\" header parameter is REQUIRED.")
		
		decoded_payload = self.LIB_BASE64.decode(data=encoded_payload, urlsafe=True, padding=True)
		payload = self.LIB_JSON.decode(decoded_payload.decode('utf-8'))
		
		# check signature
		if verify and key is None: raise ValueError("Public key is required")
		
		if verify:
			signed_section = encoded_header + b'.' + encoded_payload
			if header["alg"] in [ "RS256", "RS384", "RS512"]:
				sign_valid = self.rsa_sign_verify(message=signed_section, signature=signature, 
																												key=key, hash=header["alg"])
			elif header["alg"] in [ "HS256", "HS384", "HS512"]:
				sign_valid = self.hmac_sign_verify(message=signed_section, signature=signature, 
																												key=key, hash=header["alg"])
			else:
				raise ValueError("alg not supported %s" % header["alg"])
		else:
			sign_valid = None
			
		return (header, payload, sign_valid)
				
	def hmac_sign(self, message, key, hash):
		"""
		"""
		signer = HMAC.new(key=key, digestmod=self.alg_supported[hash])
		signer.update(message)
		return signer.digest()
	def hmac_sign_verify(self, message, signature, key, hash):
		"""
		"""
		computed_sign = self.hmac_sign(message, key, hash)
		return True if computed_sign == signature else False
		
	def rsa_sign_verify(self, message, signature, key, hash):
		"""
		key=public key
		"""
		try:
			pub_key = RSA.importKey(key)
		except Exception as e:
			raise ValueError("Invalid public key - %s" % e)
				
		signer = PKCS1_v1_5.new(pub_key)
		
		if hash not in self.alg_supported:
			raise ValueError("unsupported hash %s" % hash)
			
		digest = self.alg_supported[hash].new()
		digest.update(message)
		
		return signer.verify(digest, signature)
	def rsa_sign(self, message, key, hash):
		
		try:
			priv_key = RSA.importKey(key)
		except Exception as e:
			raise ValueError("Invalid private key - %s" % e)

		signer = PKCS1_v1_5.new(priv_key)
		
		if hash not in self.alg_supported:
			raise ValueError("unsupported hash %s" % hash)
			
		digest = self.alg_supported[hash].new()
		digest.update(message)
		return signer.sign(digest)