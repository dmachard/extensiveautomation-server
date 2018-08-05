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

try:
	import common
except ImportError: # support python 3
	from . import common

import shlex
import subprocess

__NAME__="""OPENSSL"""

OPENSSL_BIN = "/usr/bin/openssl"

class OpenSSL(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Implementation of the openssl library
		
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
	@doc_public	
	def execute(self, cmd):
		"""
		Execute the openssl command

		@param cmd: openssl argument
		@type cmd: string
		
		@return: openssl result or none
		@rtype: string/none
		"""
		run = "%s %s" % (OPENSSL_BIN, cmd)
		self.debug(run)
		ps = subprocess.Popen(run,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		out, err = ps.communicate()
		if out is None:
			self.error("unable to run openssl command: %s" % err)
		return out
	@doc_public
	def digest(self, digest, data, hmac=None, binary=False):
		"""
		Digests data
		
		@param digest:  cipher to use
		@type digest: string
		
		@param data: data to digest
		@type data: string
		
		@param hmac: hmac key (default=None)
		@type hmac: string/none
		
		@param binary:  result as binary (default=False)
		@type binary: boolean
		
		@return: digest of the payload or none on error
		@rtype: string/none
		"""
		# save data in tmp file
		infile = "/tmp/data.in"
		with open(infile, "wb") as f:
			f.write(data)
		
		# digest
		cmd = [ 'dgst -%s' % digest ]
		if hmac is not None:
			cmd.append( "-hmac %s" % hmac )
		if binary:
			cmd.append( "-binary" )
		cmd.append("/tmp/data.in")
		
		# execute the openssl command
		digested = self.execute( cmd=" ".join(cmd) )
		
		if not binary:
			try:
				hash = digested.split("=", 1)[1].strip()
			except Exception as e:
				self.error("%s" % digested)
				hash = None
		else:
			hash = digested
		return hash
	@doc_public
	def encrypt(self, cipher, data, key=None, iv=None, salt=None, password=None, base64=False, nopad=False, zlib=False):
		"""
		Encrypt data
		
		@param cipher:  cipher to use
		@type cipher: string
		
		@param data: data to encrypt
		@type data: string
		
		@param key:  the actual key to use
		@type key: string/none
		
		@param iv: the actual IV to use
		@type iv: string/none
		
		@param salt: use salt (randomly generated)
		@type salt: string/none

		@param password: the password source
		@type password: string/none
		
		@param base64: the data is base64 encoded after encryption or before (default=False)
		@type base64: boolean
		
		@param nopad: disable standard block padding (default=False)
		@type nopad: boolean
		
		@param zlib:  zlib before encryption or after decryption (default=False)
		@type zlib: boolean
		
		@return: encrypted payload or none on error
		@rtype: string/none
		"""
		# save data in tmp file
		infile = "/tmp/data.in"
		with open(infile, "wb") as f:
			f.write(data)
		
		# encrypt
		cmd = [ 'enc -%s' % cipher ]
		cmd.append(	'-e' )
		if key is not None:
			cmd.append( "-K %s" % key )
		if iv is not None:
			cmd.append( "-iv %s" % iv )
		if salt is not None:
			cmd.append( "-S %s" % salt )
		if base64:
			cmd.append( "-A -a" )
		if zlib:
			cmd.append( "-z" )
		if nopad:
			cmd.append( "-nopad" )
		if password is not None:
			cmd.append( "-pass %s" % password )
		cmd.append( 	'-in %s' % infile )

		return self.execute( cmd=" ".join(cmd) )
	@doc_public
	def decrypt(self, cipher, data, key=None, iv=None, salt=None, password=None, base64=False, nopad=False, zlib=False):
		"""
		Decrypt data
		
		@param cipher:  cipher to use
		@type cipher: string
		
		@param data: data to encrypt
		@type data: string
		
		@param key:  the actual key to use
		@type key: string/none
		
		@param iv: the actual IV to use
		@type iv: string/none
		
		@param salt: use salt (randomly generated)
		@type salt: string/none

		@param password: the password source
		@type password: string/none
		
		@param base64: the data is base64 encoded after encryption or before (default=False)
		@type base64: boolean
		
		@param nopad: disable standard block padding (default=False)
		@type nopad: boolean
		
		@param zlib:  zlib before encryption or after decryption (default=False)
		@type zlib: boolean
		
		@return: decrypted payload or none on error
		@rtype: string/none
		"""
		# save data in tmp file
		infile = "/tmp/data.in"
		with open(infile, "wb") as f:
			f.write(data)
			
		cmd = [ 'enc -%s' % cipher ]
		cmd.append(	'-d' )
		if key is not None:
			cmd.append( "-K %s" % key )
		if iv is not None:
			cmd.append( "-iv %s" % iv )
		if salt is not None:
			cmd.append( "-S %s" % salt )
		if base64:
			cmd.append( "-A -a" )
		if zlib:
			cmd.append( "-z" )
		if nopad:
			cmd.append( "-nopad" )
		if password is not None:
			cmd.append( "-pass %s" % password )
			
		cmd.append( 	'-in %s' % infile )

		decrypted = self.execute( cmd=" ".join(cmd) )
		if "bad decrypt" in decrypted:
			return None
		return decrypted