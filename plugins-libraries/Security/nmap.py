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

__NAME__="""NMAP"""

NMAP_BIN = "/usr/bin/nmap"

class Nmap(TestLibrary.Library):
	@doc_public	
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Implementation of the nmap library
		
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
	def execute(self, cmd):
		"""
		Execute the nmap command

		@param cmd: nmap argument
		@type cmd: string
		
		@return: nmap result or none
		@rtype: string/none
		"""
		run = "%s %s" % (NMAP_BIN, cmd)
		self.debug(run)
		ps = subprocess.Popen(run,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		out, err = ps.communicate()
		if out is None:
			self.error("unable to run nmap command: %s" % err)
		return out