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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

try:
	import templates
except ImportError: # python3 support
	from . import templates

import socket

__NAME__="""DNS"""

class Client(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, debug=False, name=None, verbose=True,
											logEventSent=True, logEventReceived=True, shared=False):
		"""
		This class enable to use the protocol DNS as client.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, 
																									shared=shared, realname=name,
																									showEvts=verbose, showSentEvts=verbose, 
																									showRecvEvts=verbose)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.cfg = {}
	
	def encapsule(self, layer):
		"""
		"""
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer( layer=layer )
		return tpl
		
	def resolveHost(self, host):
		"""
		Make a resolution of the host passed as argument
		
		@param host: host to resolv
		@type host: string
		
		@return: associated ip to the host
		@rtype: string
		"""
		dstIp = ''
		self.debug('dns resolve host...')
		if self.logEventSent: 
			layer_dns = self.encapsule( layer=templates.dns( more=templates.resolv(hostname=host) ) )
			self.logSentEvent( shortEvt = 'resolution', tplEvt = layer_dns )
				
		try:
			dstIp = socket.gethostbyname( host )
			self.debug('hostname %s resolv to %s' % (host, dstIp) )
			if self.logEventReceived: 
				layer_dns = self.encapsule( layer=templates.dns( more=templates.resolv_success(hostname=host, destinationIp=dstIp) ) )
				self.logRecvEvent( shortEvt = 'resolution success', tplEvt = layer_dns )

		except Exception as e:
			if self.logEventReceived: 
				layer_dns = self.encapsule( layer=templates.dns( more=templates.resolv_failed(hostname=host, error=str(e) ) ) )
				self.logRecvEvent( shortEvt = 'resolution failed', tplEvt = layer_dns )
		return dstIp

	@doc_public
	def isResolutionSuccess(self, timeout=1.0):
		"""
		Waits to receive "resolution success" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		expected = templates.dns(more=templates.resolv_success())
		evt = self.received( expected = expected, timeout = timeout )
		return evt
		
	@doc_public
	def isResolutionFailed(self, timeout=1.0):
		"""
		Waits to receive "resolution failed" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		expected = templates.dns(more=templates.resolv_failed())
		evt = self.received( expected = expected, timeout = timeout )
		return evt