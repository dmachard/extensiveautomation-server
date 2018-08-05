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

import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import sys
Hashing = sys.modules['SutLibraries.%s.Hashing' % TestLibrary.getVersion()]
Codecs = sys.modules['SutLibraries.%s.Codecs' % TestLibrary.getVersion()]

import time
import urllib

__NAME__="""OAUTH"""

class Oauth(TestLibrary.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Oauth authentication 1.0a

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
		self.hmac1 = Hashing.HMAC_SHA1(parent=parent, debug=debug)
		self.base64 = Codecs.BASE64(parent=parent, debug=debug)
	@doc_public
	def compute(self, parameters, url, method, tokenSecret, consumerSecret):
		"""
		Compute the signature

		@param parameters: request parameters
		@type parameters: list of tuple

		@param url: request url
		@type url: string
		
		@param method: request method
		@type method: strinig
		
		@param tokenSecret: token secret
		@type tokenSecret: string
		
		@param consumerSecret: consumer secret
		@type consumerSecret: string
		
		@return: signature base string
		@rtype: string
		"""
		#  9.1.1 Normalize Request Parameters
		norm_req_list = []
		# The parameters are normalized into a single string as follows: 
		for param in sorted(parameters, key=lambda tup: tup[0]):
			key, value = param
			# The oauth_signature parameter MUST be excluded.
			if key == 'oauth_signature':
				pass
			norm_req_list.append( '='.join(param) )
		norm_req = '&'.join(norm_req_list)
		norm_req = urllib.quote_plus(norm_req)
		
		# 9.1.2.  Construct Request URL
		norm_url = url.lower().split('?')[0]
		norm_url = urllib.quote_plus(norm_url)
		
		# 9.1.3.  Concatenate Request Elements
		req_els_list = []
		req_els_list.append( method.upper() )
		req_els_list.append( norm_url )
		req_els_list.append( norm_req )
		# Signature base string
		sig_base_str = '&'.join(req_els_list)

		# Consumer Secret and Token Secret
		key = "%s&%s" % (consumerSecret,tokenSecret)
		self.hmac1 .setKey(key=key)
		
		sig = self.hmac1.compute(data=sig_base_str, hexdigit=False)
		sig_base64 = self.base64.encode(data=sig)
		
		return  urllib.quote_plus(sig_base64)
	@doc_public	
	def decode(self, challenge):
		"""
		Decode the challenge present in the www-authenticate header

		@param challenge: 'www-authenticate' field value
		@type challenge: string
		
		@return: challenge parsed
		@rtype: dict
		"""
		ch = {}
		
		# extract authentication scheme
		values = challenge.split(' ', 1)
		if len(values) != 2:
			raise Exception('malformed authentication scheme: %s' % values )
		
		ch['auth-scheme'] = values[0].strip() # remove spaces	
		
		# continue to parse the request
		chal = values[1].strip()# remove uneeded spaces
		for k_v in chal.split(','):
			kv = k_v.split('=', 1)
			if len(kv) != 2:
				raise Exception('malformed authentication request: %s' % k_v )
			ch[kv[0].strip()] = kv[1].strip()
			
		return ch
	@doc_public	
	def encode(self, nonce, callback, method, timestamp, consumerkey, signature, version):
		"""
		Contructs an oauth authorization header line

		@param nonce: nonce
		@type nonce: string
		
		@param callback: callback url
		@type callback: string
		
		@param method: method http
		@type method: string
		
		@param timestamp:  timestamp
		@type timestamp: string
		
		@param consumerkey: consumer key
		@type consumerkey: string
		
		@param signature: signature
		@type signature: string
		
		@param version: oauth version
		@type version: string
		
		@return: authorization
		@rtype: string
		"""
		oauth_response = [ 'oauth_nonce="%s"' % nonce ]
		oauth_response.append( 'oauth_callback="%s"' % callback )
		oauth_response.append( 'oauth_signature_method="%s"' % method )
		oauth_response.append( 'oauth_timestamp="%s"' % timestamp )
		oauth_response.append( 'oauth_consumer_key="%s"' % consumerkey )
		oauth_response.append( 'oauth_signature="%s"' % signature )
		oauth_response.append( 'oauth_version="%s"' % version )
		
		oauth = "OAuth %s" % ', '.join(oauth_response)
		return oauth