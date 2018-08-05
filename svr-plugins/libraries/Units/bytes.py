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

__NAME__="""Bytes"""

class Bytes(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Bytes converter

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
	def toHuman(self, bytes):
		"""
		Converts and returns a readable value of the bytes passed as argument
		
		@param bytes: bytes values to convert
		@type bytes: integer
		
		@return: readable value
		@rtype: string		
		"""
		if not isinstance(bytes, int): raise Exception( 'bad type on argument, integer expected' )
		symbols = ('KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
		prefix = {}
		for i, s in enumerate(symbols):
			prefix[s] = 1 << (i+1)*10
		for s in reversed(symbols):
			if bytes >= prefix[s]:
				value = float(bytes) / prefix[s]
				return '%.1f %s' % (value, s)
		return "%s Bytes" % bytes