#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

__NAME__="""SOCKS"""

import codec4
import codec5
import templates

PROXY_SOCKS4 = 'socks4'
PROXY_SOCKS5 = 'socks5'

class Client(TestAdapterLib.Adapter):
	def __init__(self, parent, name=None, debug=False, proxyType=PROXY_SOCKS4, verbose=True):
		"""
		Socks adapter (Socket Secure) version 4 and 5 (rfc1928)
		https://www.ietf.org/rfc/rfc1928.txt
		http://tools.ietf.org/html/rfc1929
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, showEvts=verbose, showSentEvts=verbose, showRecvEvts=verbose)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		self.cfg['proxy-type'] = proxyType
		self.__checkConfig()
		
		self.sockCodec4 = codec4.Codec(parent=self, testcase=parent, debug=debug)
		self.sockCodec5 = codec5.Codec(parent=self, testcase=parent, debug=debug)

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)	
	
	def codec(self):
		"""
		Return the codec
		"""
		if self.cfg['proxy-type'] == PROXY_SOCKS4:
			return self.sockCodec4
		elif self.cfg['proxy-type'] == PROXY_SOCKS5:
			return self.sockCodec5
		else:
			return self.sockCodec4
			
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		pass
	
	def prepareNego(self):
		"""
		Negociation with socks version 5
		only user/password supported 
		"""
		if self.cfg['proxy-type'] != PROXY_SOCKS5:
			return
		# support user/password authen
		tpl = templates.socks(version=5, nmethods=1, methods=0)
		req, summary = self.sockCodec5.encodenego(socks_tpl=tpl)			
		return (tpl,req, summary)
		
	def prepareConnect(self, userId=None, destinationPort=None, destinationIp=None, destinationType=None, reserved=None):
		"""
		Connect request
		"""
		if self.cfg['proxy-type'] == PROXY_SOCKS4:
			tpl = templates.socks(version=4, more=templates.connect(userId=userId, destIp=destinationIp, destPort=destinationPort))
			req, summary = self.sockCodec4.encode(socks_tpl=tpl)
		
		if self.cfg['proxy-type'] == PROXY_SOCKS5:
			tpl = templates.socks(version=5, reserved=reserved,  more=templates.connect(destIp=destinationIp, destPort=destinationPort, destType=destinationType))
			req, summary = self.sockCodec5.encode(socks_tpl=tpl)			
		
		return (tpl,req, summary)