#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

__NAME__="""RSA"""

from Crypto.PublicKey import RSA  as crypto_rsa
from Crypto import Random

class RSA(TestLibrary.Library):
	@doc_public	
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		RSA library

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
	@doc_public
	def generate(self, keysize=2048):
		"""
		Generate an RSA keypair with an exponent of 65537 in PEM format
		
		@param keysize: key size (default=2048)
		@type keysize:	integer
		
		@return: return private key and public key
		@rtype: tuple	
		"""
		random_generator = Random.new().read
		new_key = crypto_rsa.generate(keysize, random_generator)
		
		public_key = new_key.publickey().exportKey("PEM") 
		private_key = new_key.exportKey("PEM") 
		return (private_key, public_key)