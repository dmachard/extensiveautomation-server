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

import sys
Hashing = sys.modules['SutLibraries.%s.Hashing' % TestLibraryLib.getVersion()]

import random

# Some functions for help
def unq(X):
	"""
	Returns the quoted-string X without the surrounding quotes.

	@param X: X
	@type X: string
	
	@return: X without quotes
	@rtype: string
	"""
	if X.startswith('"') and X.endswith('"'):
		return X[1:-1]
	else:
		return X
	
def RAND(length = 30, choice = 'azertyuiopqsdfghjklmwxcvbn0123456789'):
	"""
	Generate a random string according characters contained in choice which a length of 'length'
	
	@param length: length of the generated id
	@type length: integer
	
	@param choice: a string of all possible characters in the generated id.
	@type choice: string
	
	@return: the generated id
	@rtype: string
	"""
	rand_str = ''
	for i in range(int(length)):
		rand_str += random.choice(choice)
	return rand_str

__NAME__="""RFC2617"""

# RFC2617: Basic and Digest Access Authentication
class Digest(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Digest Access Authentication
		Used with HTTP and SIP
		
		More informations in the RFC 2617
		
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

	def H(self, data):
		"""
		Compute the md5 of data
		
		@param data: data
		@type data: string
		
		@return: MD5 of data
		@rtype: string
		"""	
		return self.md5.compute(data=data)
		
	@doc_public
	def decode(self, challenge):
		"""
		Decode the challenge present in the www-authenticate header
		WWW-Authenticate: Digest realm="protected", nonce="DPwj+vr8BAA=56ff77658e6f9faeb6b722468ba161fcb12d6309",
											algorithm=MD5, qop="auth"

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
	def compute(self, username, password, realm, nonce, method, uri, qop=None, algo=None, body=None):
		"""
		Compute the challenge response according  to the rfc2617

		@param username: username of the user
		@type username: string
		
		@param password: password of the user
		@type password: string
		
		@param realm: realm of the challenge.
		@type realm: string
		
		@param nonce: server nonce
		@type nonce: string
		
		@param method: method of the initial request (for instance: REGISTER)
		@type method: string
		
		@param uri: uri of the initial request (including an eventually 'sip:')
		@type uri: string
		
		@param qop: quality of protection.
		@type qop: string/None
		
		@param algo: algorithm to use
		@type algo: string/None
		
		@param body: the body of the response, if exists
		@type body: string/None
		
		@return: response, cnonce, nonce-count
		@rtype: tuple
		"""
		# generate random client cnonce
		cnonce = RAND(8)
		nc = "00000001"
		
		if algo is not None:
			algo = unq(algo)
			
		# compute A1 §3.2.2.2 A1
		if algo is None: #If this is not present it is assumed to be "MD5".
			A1 = "%s:%s:%s" % ( unq(username), unq(realm), password )
		elif algo.upper() == "MD5": 
			A1 = "%s:%s:%s" % ( unq(username), unq(realm), password )
			
		# compute A1 md5sess 
		elif algo == "MD5-sess":
			# creates a 'session key' for the authentication
			A1 = "%s:%s:%s" % ( self.H( "%s:%s:%s" % ( unq(username), unq(realm), password ) ), unq(nonce), unq(cnonce) )
		
		# should not be happen
		else:
			raise Exception( 'algorithm unknown: %s' % algo )
		
		# compute A2 AuthInt §3.2.2.3 A2
		if qop is not None:
			qop = unq(qop)
		if qop is None:
			A2 = "%s:%s" % (method, uri)
		elif qop == "auth":
			A2 = "%s:%s" % (method, uri)			
		elif qop == "auth-int" :
			if body is None: body = ''
			A2 = "%s:%s:%s" ( method, uri, self.H(body) )

		# should not be happen
		else:
			raise Exception( 'qop unknown: %s' % qop )

		# compute request digest §3.2.2.1 Request-Digest
		r_digest = [ self.H(A1) ]
		if qop == "auth" or qop == "auth-int":
			r_digest.append( unq(nonce) )
			r_digest.append( nc )
			r_digest.append( unq(cnonce) )
			r_digest.append( unq(qop) )
		else:
			r_digest.append( unq(nonce) )
		r_digest.append( self.H(A2) )
		
		return ( self.H ( ':'.join(r_digest) ), cnonce, nc )

	@doc_public
	def encode(self, username, realm, nonce, uri, response, cnonce, nc, qop=None, algo=None, opaque=None):
		"""
		Contructs a digest authorization header line
		Authorization: Digest username="bob", realm="biloxi.com",
		              nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
		              uri="sip:bob@biloxi.com", qop=auth, nc=00000001, cnonce="0a4f113b",
		              response="6629fae49393a05397450978507c4ef1",
		              opaque="5ccc069c403ebaf9f0171e9517f40e41"		

		@param username: username of the user
		@type username: string
		
		@param realm: realm of the challenge.
		@type realm: string
		
		@param nonce: server nonce
		@type nonce: string
		
		@param uri: uri of the initial request
		@type uri: string
		
		@param response: A string of 32 hex digits computed with the function compute
		@type response: string

		@param cnonce: client nonce
		@type cnonce: string
		
		@param nc: nonce count
		@type nc: string
		
		@param qop: quality of protection
		@type qop: string/None
		
		@param algo: algorithm
		@type algo: string/None
		
		@param opaque: A string of data, specified by the server, which should be returned by the client unchanged
		@type opaque: string/None
		
		@return: authorization
		@rtype: string
		"""
		# mandatory directives
		digest_response = [ 'username="%s"' % unq(username) ]
		digest_response.append( 'realm="%s"' % unq(realm) )
		digest_response.append( 'response="%s"' % unq(response) )
		digest_response.append( 'nonce="%s"' % unq(nonce) )
		digest_response.append( 'uri="%s"' % unq(uri) )

		# optional directives
		if qop is not None:
			digest_response.append( 'qop="%s"' % unq(qop) )
			digest_response.append( 'cnonce="%s"' % unq(cnonce) )
			digest_response.append( 'nc=%s' % unq(nc) )
		if algo is not None:
			digest_response.append( 'algorithm="%s"' % unq(algo) )
		if opaque is not None:
			digest_response.append( 'opaque="%s"' % unq(opaque) )
			
		credentials = "Digest %s" % ', '.join(digest_response)
		return credentials