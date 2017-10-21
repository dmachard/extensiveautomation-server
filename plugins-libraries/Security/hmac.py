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

import sys
Hashing = sys.modules['SutLibraries.%s.Hashing' % TestLibraryLib.getVersion()]
#Codecs = sys.modules['SutLibraries.%s.Codecs' % TestLibraryLib.getVersion()]

import random


__NAME__="""HMAC"""

class Hmac(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Hmac Digest Access Authentication

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
		self.md5 = Hashing.MD5(parent=parent, debug=debug)
		self.sha1 = Hashing.SHA1(parent=parent, debug=debug)
		
		self.hmac_md5 = Hashing.HMAC_MD5(parent=parent, debug=debug)
		self.hmac_sha1 = Hashing.HMAC_SHA1(parent=parent, debug=debug)
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
	def compute(self, username, password, realm, method, uri, snonce, headers, salt, algo, pwalgo ):
		"""
		Compute the challenge response

		@param username: username of the user
		@type username: string
		
		@param password: password of the user
		@type password: string
	
		@param realm: realm of the challenge.
		@type realm: string
		
		@param method: method of the initial request (for instance: REGISTER)
		@type method: string
		
		@param uri: uri of the initial request (including an eventually 'sip:')
		@type uri: string
		
		@param snonce: server nonce
		@type snonce: string

		@param salt: salt
		@type salt: string

		@param algo: algorithm to use
		@type algo: string

		@param pwalgo: algorithm to use
		@type pwalgo: string
		
		@param headers: headers list
		@type headers: dict

		@return: req_digest, cnonce
		@rtype: tuple
		"""
		keylist = "".join(["%s " % k for k in headers.keys()])
		headers_val = "".join([headers[k] for k in headers.keys()])
		
		created = time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())

		# key
		if algo not in ['HMAC-SHA-1', 'HMAC-MD5']:
			if pwalgo == 'HMAC-MD5':
				key = "".join([username, ':', self.md5.compute(''.join([password, salt])).lower(), ':', realm])
			else:
				key = "".join([username, ':', self.sha1.compute(''.join([password, salt])).lower(), ':', realm])
		else:
			raise Exception( 'algorithm unknown: %s' % algo )

		if pwalgo not in ['SHA-1', 'MD5']:
			if pwalgo == 'MD5':
				key = self.md5.compute(key).lower()
			else:
				key = self.sha1.compute(key).lower()
		else:
			raise Exception( 'pw-algorithm unknown: %s' % algo )

		self.hmac_md5.setKey(key=key)
		self.hmac_sha1.setKey(key=key)
		
		# construct cnonce
		cnonce = "%s:%s" % (time.ctime(), ["0123456789"[random.randrange(0, 9)] for i in range(20)])
		cnonce = self.md5.compute(data=cnonce)
		cnonce = dig[:16]
		
		req_digest = "%s:%s:%s:%s:%s" % (method, uri, cnonce, snonce, headers_val)
		if pwalgo == 'HMAC-MD5':
			req_digest  = self.hmac_md5.compute(key, req_digest).lower()
		else:
			req_digest  = self.hmac_sha1.compute(key, req_digest).lower()
			
		return (req_digest, cnonce)
		
	@doc_public
	def encode(self, username, realm, snonce, cnonce, uri, created, response, headers):
		"""
		Contructs a hmacdigest authorization header line

		@param username: username of the user
		@type username: string

		@param realm: realm of the challenge.
		@type realm: string

		@param snonce: server nonce
		@type snonce: string

		@param cnonce: client nonce
		@type cnonce: string

		@param uri: uri of the initial request
		@type uri: string

		@param created: creation date and time
		@type created: string

		@param response: A string of 32 hex digits computed with the function compute
		@type response: string

		@param headers: headers list
		@type headers: dict
		
		@return: authorization
		@rtype: string
		"""
		# mandatory directives
		hmacdigest_rsp = [ 'username="%s"' % username ]
		hmacdigest_rsp.append( 'realm="%s"' % realm )
		hmacdigest_rsp.append( 'snonce="%s"' % snonce )
		hmacdigest_rsp.append( 'cnonce="%s"' % cnonce )
		hmacdigest_rsp.append( 'uri="%s"' % uri )

		hmacdigest_rsp.append( 'created="%s"' % created )
		hmacdigest_rsp.append( 'response="%s"' % response )
		hmacdigest_rsp.append( 'headers="%s"' % headers )

		credentials = "HMACDigest %s" % ', '.join(hmacdigest_rsp)
		return credentials