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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

try:
	import templates_catalyst
except ImportError: # python3 support
	from . import templates_catalyst

DECODING_NOTHING_TODO = 2
DECODING_NEED_MORE_DATA = 1
DECODING_OK = 0

import re

class Codec(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info
		self.stats = {}
		
	def encode(self, catalyst_cmd):
		"""
		"""
		evt = catalyst_cmd.get('event')
		data = catalyst_cmd.get('data')
		return evt.title(), data
		
	def decode(self, data):
		"""
		"""
		messages_decoded = []
		left = data
		self.debug(data)
		
		if re.search(r'.*Login invalid.*', left, re.MULTILINE):
			self.debug('Bad login username or password detected')
			junk, left = left.split("Login invalid")
			messages_decoded.append( ('Login invalid', templates_catalyst.catalyst_bad_login()) )
			
		if re.search(r'.*Bad secrets.*', left, re.MULTILINE):
			self.debug('Bad secret detected')
			junk, left = left.split("Enable invalid")
			messages_decoded.append( ('Enable invalid', templates_catalyst.catalyst_bad_secret()) )
			
		if re.search(r'.*Username: .*', left, re.MULTILINE):
			self.debug('Username prompt detected')
			junk, left = left.split("Username: ")
			messages_decoded.append( ('Username ?', templates_catalyst.catalyst_prompt_username()) )

		if re.search(r'.*Password: .*', left, re.MULTILINE):
			self.debug('Password prompt detected')
			junk, left = left.split("Password: ")
			messages_decoded.append( ('Password ?', templates_catalyst.catalyst_prompt_password()) )

		if re.search(r'.*%s.*' % self.parent.prompt, left, re.MULTILINE):
			self.debug('Prompt detected')
			junk, left = left.split("%s" % self.parent.prompt)
			messages_decoded.append( ('Response', templates_catalyst.catalyst_prompt(data=junk)) )
			
		if re.search(r'.*%s.*' % self.parent.promptEnable, left, re.MULTILINE):
			self.debug('Prompt enable detected')
			junk, left = left.split("%s" % self.parent.promptEnable)
			messages_decoded.append( ('Response', templates_catalyst.catalyst_prompt_enable(data=junk)) )

		if re.search(r'.*--More--.*', left, re.MULTILINE):
			self.debug('more detected')
			junk, left = left.split("--More--")
			messages_decoded.append( ('Response', templates_catalyst.catalyst_more(data=junk)) )
			
		return 	messages_decoded, left
		

