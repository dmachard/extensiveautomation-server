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

import json
from jsonpath_ng.ext import parse
 
__NAME__="""JSON"""

class JSON(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, ignoreErrors=False, shared=False):
		"""
		JSON Decoder/Encoder
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param ignoreErrors: ignore errors (default=False)
		@type ignoreErrors: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.ignoreErrors = ignoreErrors
	@doc_public
	def encode(self, json_obj):
		"""
		Encode a json object to the  string json representation

		@param json_obj: json object
		@type json_obj: json object

		@return: json value
		@rtype: string
		"""
		ret=None
		try:
			ret = json.dumps(json_obj)
		except Exception as e:
			if not self.ignoreErrors :
				self.error('library - unable to encode: %s' % str(e) )
		return ret
	@doc_public
	def decode(self, json_str):
		"""
		Decode a string json to a object json
	
		@param json_str: xml raw
		@type json_str: string

		@return: value
		@rtype: json object/none
		"""
		ret=None
		try:
			ret = json.loads(json_str)
		except Exception as e:
			if not self.ignoreErrors :
				self.error('library - unable to decode: %s' % str(e) )
		return ret
	@doc_public
	def getValue(self, jpath, json_obj):
		"""
		Get the value according to the jsonpath provided
		
		@param jpath: json path
		@type jpath: string
	
		@param json_obj: json
		@type json_obj: json object
		
		@return: the value on match, None otherwise
		@rtype: object/none
		"""
		try:
			json_values = [match.value for match in parse(jpath).find(json_obj)]
			if len(json_values) >= 1: 
				return json_values[0]
		except Exception as e:
			self.error('library - unable to get json value: %s' % str(e) )
		return None
	@doc_public
	def getValues(self, jpath, json_obj):
		"""
		Get all values according to the jsonpath provided
		
		@param jpath: json path
		@type jpath: string
	
		@param json_obj: json
		@type json_obj: json object
		
		@return: all values on match, empty list otherwise
		@rtype: list
		"""
		try:
			return [match.value for match in parse(jpath).find(json_obj)]
		except Exception as e:
			self.error('library - bad jsonpath (%s) provided ? more details:\n\n %s' % (jpath, str(e)) )
		return []
	@doc_public
	def toHuman(self, json_obj):
		"""
		Return JSON data to human-readable form
	
		@param json_obj: json
		@type json_obj: json object
		
		@return: json with indentation
		@rtype: string
		"""
		json_pretty = json.dumps(json_obj, sort_keys = False, indent = 4) 
		return json_pretty
	@doc_public
	def isValid(self, json_str):
		"""
		JSON is valid ?
	
		@param json_str: xml raw
		@type json_str: string

		@return: True on valid, false otherwise
		@rtype: boolean
		"""
		try:
			ret = json.loads(json_str)
			del ret
			return True
		except Exception as e:
			return False