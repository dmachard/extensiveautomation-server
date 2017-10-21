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

from datetime import date
import calendar

__NAME__="""Today"""

class Today(TestLibrary.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Return the current day, month or year as string or digits

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
	def getDayName(self, lang="en", abbreviated=False):
		"""
		Return the current day with the name
		en/fr languages are supported
		
		@param lang: language en/fr (default=en)
		@type lang: string
		
		@param abbreviated: abbreviated mode (default=False)
		@type abbreviated: boolean
		
		@return: day name
		@rtype: string
		"""
		fr_map = { "Monday": "Lundi", "Tuesday": "Mardi", "Wesnesday": "Mercredi",  "Thursday": "Jeudi",
											"Friday": "Vendredi", "Saturday": "Samedi",  "Sunday": "Dimanche"}
		fr_map_abbr = { "Mon": "Lun", "Tue": "Mar", "Wes": "Mer",  "Thu": "Jeu", "Fri": "Ven", "Sat": "Sam",  "Sun": "Dim"}
										
		if lang == "en" and not abbreviated:
			return calendar.day_name[date.today().weekday()]
		elif lang == "fr" and not abbreviated:
			return fr_map[calendar.day_name[date.today().weekday()]]
		elif lang == "en" and abbreviated:
			return calendar.day_abbr[date.today().weekday()]
		elif lang == "fr" and abbreviated:
			return fr_map_abbr[calendar.day_abbr[date.today().weekday()]]
		else:
			raise Exception("lang %s not supported" % lang)
			
	@doc_public
	def getDayNumber(self, nb=2):
		"""
		Return the day as number
		
		@param nb: size of the number (default=2)
		@type nb: integer
		
		@return: day
		@rtype: string
		"""
		return str(date.today().day).zfill(nb)
		
	@doc_public
	def getMonthName(self, lang="en", abbreviated=False):
		"""
		Return the current month as word
		en/fr languages are supported
		
		@param lang: language en/fr (default=en)
		@type lang: string
		
		@param abbreviated: abbreviated mode (default=False)
		@type abbreviated: boolean
		
		@return: month name
		@rtype: string
		"""
		fr_map= { 1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 7: "Juillet",
												8: "Août", 9: "Septembre", 10:"Octobre", 11: "Novembre", 12: "Décembre" }
		en_map = { 1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
												8: "August", 9: "September", 10: "October", 11: "November", 12: "December" }
												
		fr_map_abbr= { 1: "Janv", 2: "Févr", 3: "Mars", 4: "Avr", 5: "Mai", 6: "Juin", 7: "Juill",
												8: "Août", 9: "Sept", 10:"Oct", 11: "Nov", 12: "Déc" }
		en_map_abbr = { 1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul",
												8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec" }

		if lang == "en" and not abbreviated:
			return en_map[date.today().month]
		elif lang == "fr" and not abbreviated:
			return fr_map[date.today().month]
		elif lang == "en" and abbreviated:
			return en_map_abbr[date.today().month]
		elif lang == "fr" and abbreviated:
			return fr_map_abbr[date.today().month]
		else:
			raise Exception("lang %s not supported" % lang)
			
	@doc_public
	def getMonthNumber(self, nb=2):
		"""
		Return the current month as number
		
		@param nb: size of the number (default=2)
		@type nb: integer
		
		@return: month
		@rtype: string
		"""
		return str(date.today().month).zfill(nb)
	@doc_public	
	def getYearNumber(self):
		"""
		Return the current year as number

		@return: year
		@rtype: string
		"""
		return str(date.today().year)
		
	@doc_public
	def getWeekNumber(self, nb=2):
		"""
		Return the current week number
		
		@param nb: size of the number (default=2)
		@type nb: integer
		
		@return: week number
		@rtype: string
		"""
		year, week, weekday  = date.today().isocalendar()
		return str(week).zfill(nb)