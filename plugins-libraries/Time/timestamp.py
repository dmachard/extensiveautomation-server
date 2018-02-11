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

import time
from datetime import datetime, date
from time import mktime

# python 2.4 support
if hasattr(datetime, 'strptime'):
	strptime = datetime.strptime
else:
	strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))
		
__NAME__="""Timestamp"""

class Timestamp(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		This library returns seconds since epoch (UTC).

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
	def generate (self, fromDate=None, dateFormat="%d/%m/%Y %H:%M:%S", deltaTime=0) :
		"""
		Get seconds since epoch (UTC).

		@param fromDate: date and time (default=None)
		@type fromDate: none/string
		
		@param dateFormat: date time format representation (default=%d/%m/%Y %H:%M:%S)
		@type dateFormat: string
		
		@param deltaTime: return a timestamp representing delta seconds from now (default=0)
		@type deltaTime: integer
		
		@return: seconds
		@rtype: integer
		"""
		if fromDate is not None:
			dt = strptime(fromDate, "%d/%m/%Y %H:%M:%S")
			return int( mktime( dt.timetuple()) )
		else:
			return int(time.time()+deltaTime)
	@doc_public
	def toHuman(self, timestamp, dateFormat="%Y-%m-%d %H:%M:%S"):
		"""
		Return a timestamp to a readable human view
		
		@param dateFormat: date time format representation (default=%d/%m/%Y %H:%M:%S)
		@type dateFormat: string
		
		@param timestamp: timestamp
		@type timestamp: integer
		
		@return: timestamp readable for human
		@rtype: string
		"""
		pass
		humanTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
		return humanTime
	@doc_public
	def now(self, timeFormat="%H:%M:%S"):
		"""
		Return the current time
		
		@param timeFormat: time format representation (default=%H:%M:%S)
		@type timeFormat: string
		
		@return: the current time with desired format
		@rtype: string
		"""
		return datetime.now().strftime(timeFormat)