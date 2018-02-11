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

import PIL.Image as ImagePIL
from StringIO import StringIO

__NAME__="""IMAGE"""

class Image(TestLibraryLib.Library):
	@doc_public
	def __init__(self,  parent, name=None, debug=False, shared=False):
		"""
		Library to manipulate image
		Based on PIL library
		
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
	def mainColor(self, imgData):
		"""
		Return the main color of the image passed as argument
		
		@param imgData: image data  
		@type imgData: string
		
		@return: rgb color
		@rtype: tuple
		"""
		most_present = None
		try:
			im = ImagePIL.open(StringIO(imgData))
		except Exception as e:
			self.error('unable to read image: %s' % e)
		else:
			colors = im.getcolors(256)
			max_occurence, most_present = 0, 0
			try:
				for c in colors:
					if c[0] > max_occurence:
						(max_occurence, most_present) = c
			except TypeError:
				self.warning("Too many colors in the image")
		return most_present