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
Codecs = sys.modules['SutLibraries.%s.Codecs' % TestLibraryLib.getVersion()]

import random

__NAME__="""RFC2617"""

# RFC2617: Basic and Digest Access Authentication
class Basic(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Basic Access Authentication
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
		self.base64 = Codecs.BASE64(parent=parent, debug=debug)
		
	@doc_public
	def decode(self, challenge):
		"""
		Decode the challenge present in the authentization header
		Authorization: Basic username="bob"

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
	def compute(self, username, password):
		"""
		Compute the challenge response according  to the rfc2617
		
		@param username: username of the user
		@type username: string
		
		@param password: password of the user
		@type password: string
		
		@return: base64 hash
		@rtype: tuple
		"""
		userpass = "%s:%s" % (username, password)
		return self.base64.encode(data=userpass)

	@doc_public
	def encode(self, response):
		"""
		Contructs a basic authorization header line
		
		@param response: A md5 string of username:password
		@type response: string
		
		@return: authorization
		@rtype: string
		"""
		return "Basic %s" % response