#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import templates

import re
import time
import codecs
import binascii

class Codec(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info
		self.stats = {}
		
	def encode(self, ssh_cmd):
		"""
		"""
		evt = ssh_cmd.get('event')
		data = ssh_cmd.get('data')
		return evt.title(), data
		
	def decode(self, data, prompt=r'\[.*@.* .+\][#\$]', delimiter = ""):
		"""
		"""
		messages_decoded = []
		left = data
		while re.search(prompt, left) is not None:
			prompt_found = 	re.findall(prompt, left)[0]
			junk, left = re.split(prompt, left, maxsplit=1)
			messages_decoded.append(junk + prompt_found)
			time.sleep(0.1)
		if len(delimiter)>0:
			while re.search(re.escape(delimiter), left) is not None:
				junk, left = re.split(re.escape(delimiter), left, maxsplit=1)
				messages_decoded.append(junk + delimiter)
				time.sleep(0.1)
		
		# Management of screen refresh signal generating commands like TOP
		# Detect the refresh SIGNAL 1b5b4a1b5b481b5b6d0f
		if "\x1b\x5b\x4a\x1b\x5b\x48\x1b\x5b\x6d\x0f" in left:
			self.info("before top-like messages split")
			junk, left = left.split("\x1b\x5b\x4a\x1b\x5b\x48\x1b\x5b\x6d\x0f",1)
			self.info("after top-like messages split")
			messages_decoded.append(junk + "\x1b\x5b\x4a\x1b\x5b\x48\x1b\x5b\x6d\x0f")
			self.info("updater after top-like messages split")

		#Management of the su command as there is no prompt in that case
		if re.search("su.*\n.assword:", left) is not None:
			self.info("before su-like messages split")
			junk, left = re.split(":", left, maxsplit=1)
			self.info("after su-like messages split")
			messages_decoded.append(junk + ":")
			self.info("update after su-like messages split")

		return 	messages_decoded, left
		

