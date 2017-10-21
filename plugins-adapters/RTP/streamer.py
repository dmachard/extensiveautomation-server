#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
import sys

class Streamer(object):
	def __init__(self, raw_vals=[], pl_size=0):
		"""
		"""
		self.current_cur = 0
		self.raw_vals = raw_vals
		self.pl_size = pl_size
		self.initData()

	def setVals(self, raw_vals):
		"""
		"""
		self.raw_vals = raw_vals
		self.initData()
		
	def setSize(self, pl_size):
		"""
		"""
		self.pl_size = pl_size
		self.initData()
		
	def initData(self):
		"""
		"""
		if len(self.raw_vals) <= self.pl_size:
			self.raw_vals = self.raw_vals * (self.pl_size+1)

	def getNext(self):
		"""
		"""
		start_cur = self.current_cur
		end_cur = start_cur +  self.pl_size
		if end_cur > len(self.raw_vals): 
			end_cur = end_cur % len(self.raw_vals)
			pl = '%s%s' % ( self.raw_vals[start_cur:], self.raw_vals[:end_cur] )
		else:
			pl = self.raw_vals[start_cur:end_cur]
		self.current_cur = end_cur

		return pl
