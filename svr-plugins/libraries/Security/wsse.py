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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys
Hashing = sys.modules['SutLibraries.%s.Hashing' % TestLibraryLib.getVersion()]
Codecs = sys.modules['SutLibraries.%s.Codecs' % TestLibraryLib.getVersion()]

import time
import random

__NAME__="""WSSE"""

class Wsse(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Wsse Authentication

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
		self.sha = Hashing.SHA1(parent=parent, debug=debug)
		self.base64 = Codecs.BASE64(parent=parent, debug=debug)

	@doc_public
	def compute(self, password):
		"""
		Compute the challenge response

		@param password: password of the user
		@type password: string

		@return: passworddigest, cnonce, created
		@rtype: tuple
		"""
		iso_now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
		
		# construct cnonce
		cnonce = "%s:%s" % (time.ctime(), ["0123456789"[random.randrange(0, 9)] for i in range(20)])
		cnonce = self.md5.compute(data=cnonce)
		cnonce = dig[:16]
		
		# construct password
		pwd_digest = self.sha.compute( "%s%s%s" % (cnonce, iso_now, password) )
		pwd_digest = self.base64.encode(pwd_digest)
		
		return (pwd_digest, cnonce, iso_now)
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
	def encode(self, xwsse=False, username=None, password=None, nonce=None, created=None ):
		"""
		Contructs an authorization or X-WSSE headers

		@param xwsse: return xwsse header
		@type xwsse: boolean
		
		@param username: username of the user (default=None)
		@type username: string/none
		
		@param password: password of the user (default=None)
		@type password: string/none

		@param nonce: nonce
		@type nonce: string/none

		@param created: creation date and time
		@type created: string/none

		@return: authorization/x-wsse
		@rtype: string
		"""
		if not xwsse:
			return 'WSSE profile="UsernameToken"'
		else:
			wsse_rsp = [ 'UsernameToken Username="%s"' % username ]
			wsse_rsp.append( 'PasswordDigest="%s"' % password )
			wsse_rsp.append( 'Nonce="%s"' % nonce )
			wsse_rsp.append( 'Created="%s"' % created )
		
			return ', '.join(wsse_rsp)