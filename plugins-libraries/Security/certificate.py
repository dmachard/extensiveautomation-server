#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

import subprocess
import re

__NAME__="""CERTIFICATE"""

OPENSSL_BIN = "/usr/bin/openssl"

class Certificate(TestLibrary.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Certificate decoder	

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
	def decode(self, certPath=None, cert=None):
		"""
		"""
		ret = None
		
		cert_str = self.toHuman( certPath=certPath, cert=cert)
		if cert_str is None: 
			return ret
	
		cert_dict = {}
		validity_notbefore = re.search('Not Before( )*:( )*(.*)', cert_str)
		if validity_notbefore is not None:
			cert_dict["valid-from"] = validity_notbefore.group(3)
			
		validity_notafter = re.search('Not After( )*:( )*(.*)', cert_str)
		if validity_notafter is not None:
			cert_dict["valid-to"] = validity_notafter.group(3)

		subject_cn = re.search('Subject:.*CN=(.*)', cert_str)
		if subject_cn is not None:
			cert_dict["common-name"] = subject_cn.group(1)

		subject_o = re.search('Subject:.*O=(.*),', cert_str)
		if subject_o is not None:
			cert_dict["organization"] = subject_o.group(1)
		
		return cert_dict
		
	@doc_public
	def toHuman(self, certPath=None, cert=None):
		"""
		Return certificate to a readable human view
		
		@param cert: certificate pem to read (default=None)
		@type cert: string/none

		@param certPath: path to the certificate to read (default=None)
		@type certPath: string/none
		
		@return: certificate in readable human form
		@rtype: string/none
		"""
		if certPath is None and cert is None:
			raise Exception("no certificate provided")
		
		if cert is not None:
			# save cert in tmp file
			infile = "/tmp/cert.in"
			with open(infile, "wb") as f:
				f.write(cert)
		else:
			infile = certPath
		
		
		out = None
		
		run = "%s x509 -text -noout -in %s" % (OPENSSL_BIN, infile)
		self.debug(run)
		ps = subprocess.Popen(run,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		out, err = ps.communicate()
		if out is None:
			self.error("unable to run openssl command: %s" % err)

		return out
		
	def isValid(self):
		"""
		todo
		"""
		pass