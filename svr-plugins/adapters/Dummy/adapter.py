#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

import sys

# import the test framework
import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

# Example to import adapter or library from the generic branch
AdapterHTTP = sys.modules['SutAdapters.%s.HTTP' % TestAdapterLib.getVersionGeneric()]
LibraryCodecs =  sys.modules['SutLibraries.%s.Codecs' % TestLibraryLib.getVersionGeneric()]

# Name of the adapter
__NAME__="""DUMMY"""

# Adapter example inherent from adapter library
class Adapter(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, debug=False, name=None, shared=False, showEvts=True, showSentEvts=True, showRecvEvts=True):
		"""
		My dummy adapter.
		Mon adaptateur factice et avancée.

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared,
																									showEvts=showEvts, showSentEvts=showSentEvts, showRecvEvts=showRecvEvts )
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		self.__checkConfig()
		
		# try to init generic library and adapter
		self.XML = LibraryCodecs.XML(parent=parent, debug=False, coding='UTF-8', name=None, shared=False)

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
	
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		pass

	@doc_public
	def helloWorld(self, msg="hello world"):
		"""
		Dummy function
		
		@param msg:  message (default=hello world)
		@type msg:	string
		"""
		if not isinstance(msg, str):
			msg_err =  "msg argument is not a string (%s)" % type(msg) 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), msg_err)
		
		# log a message during the execution
		self.info( msg )
		
		# prepare a template
		tpl = TestTemplatesLib.TemplateMessage()
		layer = TestTemplatesLib.TemplateLayer('EXAMPLE')
		layer.addKey("hello", "world")
		tpl.addLayer(layer= layer)
			
		self.logSentEvent(shortEvt=msg, tplEvt=tpl )
		
		self.logRecvEvent(shortEvt=msg, tplEvt=tpl )