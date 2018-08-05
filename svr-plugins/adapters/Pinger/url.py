#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import httplib2
import threading

__NAME__="""PINGER URL"""

class UrlAgent(threading.Thread):
	def __init__(self, parent, url, method, credentials, https, timeout):
		"""
		"""
		threading.Thread.__init__(self)
		self.parent = parent
		self.http = httplib2.Http(timeout=timeout)
		self.url = url
		self.method = method
		self.rspCodeReceived = None
		self.rspBodyReceived = None
		self.credentials = credentials
		self.https = https
		self.uri = None
		self.setLogin()
		self.setUri()

	def setUri(self):
		"""
		"""
		if self.https:
			self.uri = 'https://%s' % self.url
		else:
			self.uri = 'http://%s' % self.url

	def setLogin(self):
		"""
		"""
		login, password = self.credentials
		if login is not None and password is not None:
			self.http.add_credentials(login, password)

	def run(self):
		"""
		"""
		try:
			self.trace( "%s %s" % (self.method, self.uri) )
			resp, content = self.http.request(self.uri, self.method)
			self.rspCodeReceived = str(resp['status'])
			self.rspBodyReceived = content
		except Exception as e:
			self.error( str(e) )

	def trace(self, msg):
		"""
		"""
		if self.parent.debug:
			self.parent.trace( "[%s] %s" % ( self.__class__.__name__, msg) )

	def error(self, msg):
		"""
		"""
#		self.parent.error( "%s" % msg )
		if self.parent.debug:
			self.parent.trace( "[%s][ERROR] %s" % ( self.__class__.__name__, msg) )

class URL(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, name=None, responseCode=200, method='GET', 
											responseBody=None, login=None, password=None,
											https=False, timeout=2, debug=False, shared=False ):
		"""
		This class enable to check the status of an URL with the HTTP response code returned by the remote host

		@param parent: define parent
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param responseCode: expected http response code from the remote (default=200)
		@type responseCode: integer

		@param responseBody: string expected in the body (default=None)
		@type responseBody: string/operators
		
		@param method: http method to use (GET, POST, etc..) (default=GET)
		@type method: string

		@param login: login for the digest authentication
		@type login: string/none

		@param password: password for the digest authentication
		@type password: string/none

		@param https: True to activate ssl support (default=False)
		@type https: boolean

		@param timeout: timeout in second to connect to the remote server (default value 2 seconds)
		@type timeout: integer

		@param debug: True to activate the debug mode (default=False)
		@type debug: boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, shared=shared, debug=debug, realname=name)
		self.responseCode = int(responseCode)
		self.responseBody = responseBody
		self.timeout = timeout
		self.method = method
		self.https=https
		self.credentials = (login,password)
		self.debug=debug

	@doc_public
	def doIsUp(self, url, timeout=1.0, codeExpected=None, bodyExpected=None):
		"""
		Check if the url passed as argument is up

		@param url: url without http(s)://
		@type url: string

		@param timeout: time to wait in second (default value=1s)
		@type timeout: float
		
		@param codeExpected: expected http response code from the remote (default=None)
		@type codeExpected: string/operators/none

		@param bodyExpected: string expected in the body (default=None)
		@type bodyExpected: string/operators/none
		
		@return:  True is UP, False otherwise
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = False
		evt = self.isUp(url=url, timeout=timeout, codeExpected=codeExpected, bodyExpected=bodyExpected)
		if evt is not None:
			ret = True
		return ret
		
	@doc_public
	def isUp(self, url, timeout=1.0, codeExpected=None, bodyExpected=None):
		"""
		Check if the url passed as argument is up

		@param url: url without http(s)://
		@type url: string

		@param timeout: time to wait in second (default value=1s)
		@type timeout: float
		
		@param codeExpected: expected http response code from the remote (default=None)
		@type codeExpected: string/operators/none

		@param bodyExpected: string expected in the body (default=None)
		@type bodyExpected: string/operators/none
		
		@return: alive event
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		responseCode = self.responseCode
		responseBody = self.responseBody
		if codeExpected is not None:
			responseCode = int(codeExpected)
		if bodyExpected is not None:
			responseBody = bodyExpected
		
		tpl = templates.pinger(destination=url, more=templates.ping(), type=templates.url() )
		self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
		
		pa = UrlAgent(self, url, self.method, self.credentials, self.https, self.timeout )
		pa.start()
		# synchronization
		pa.join()
		
		if pa.rspCodeReceived is not None:
			tpl = templates.pinger(destination=url, more=templates.alive(), type=templates.url(code=pa.rspCodeReceived,body=pa.rspBodyReceived) )
			self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
		else:
			tpl = templates.pinger(destination=url, more=templates.no_response(), type=templates.url() )
			self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )		
			
		expected = templates.pinger(destination=url, more=templates.alive(), type=templates.url(code=str(responseCode),body=responseBody) )
		evt = self.received( expected = expected, timeout = timeout )
		return evt


	@doc_public
	def doIsDown(self, url, timeout=1.0):
		"""
		Check if the url passed as argument is down

		@param url: url without http(s)://
		@type url: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: True is the url is down, False otherwise
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		ret = False
		evt = self.isDown(url=url, timeout=timeout)
		if evt is not None:
			ret = True
		return ret
		
	@doc_public
	def isDown(self, url, timeout=1.0):
		"""
		Check if the url passed as argument is down

		@param url: url without http(s)://
		@type url: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: no response event
		@rtype: templatemessage
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		tpl = templates.pinger(destination=url, more=templates.ping(), type=templates.url() )
		self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
		
		pa = UrlAgent(self, url, self.method, self.credentials, self.https, self.timeout)
		pa.start()
		# synchronization
		pa.join()

		if pa.rspCodeReceived is not None:
			tpl = templates.pinger(destination=url, more=templates.alive(), type=templates.url(code=pa.rspCodeReceived,body=pa.rspBodyReceived) )
			self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
		else:
			tpl = templates.pinger(destination=url, more=templates.no_response(), type=templates.url() )
			self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )			

		expected = templates.pinger(destination=url, more=templates.no_response(), type=templates.url() )
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def doAreUp(self, urls, timeout=1.0):
		"""
		Check if the list of urls passed as argument are all up

		@param urls: list of url without http(s)://
		@type urls: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all urls are up.
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.areUp(urls=urls, timeout=timeout)
		
	@doc_public
	def areUp(self, urls, timeout=1.0):
		"""
		Check if the list of urls passed as argument are all up

		@param urls: list of url without http(s)://
		@type urls: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all urls are up.
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		th = []
		# parallelize
		for i in xrange(len(urls)):
			tpl = templates.pinger(destination=urls[i], more=templates.ping(), type=templates.url() )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
			
			pa = UrlAgent(self, urls[i], self.method, self.credentials, self.https, self.timeout)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if pa.rspCodeReceived is not None:
				tpl = templates.pinger(destination=pa.url, more=templates.alive(), type=templates.url(code=pa.rspCodeReceived,body=pa.rspBodyReceived) )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			else:
				tpl = templates.pinger(destination=pa.url, more=templates.no_response(), type=templates.url() )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )		
			
			expected = templates.pinger(destination=pa.url, more=templates.alive(), type=templates.url() )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False
		
		return ret
		
	@doc_public
	def doAreDown(self, urls, timeout=1.0):
		"""
		Check if the list of urls passed as argument are all down

		@param urls: list of url without http(s)://
		@type urls: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all urls are down.
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		return self.areDown(urls=urls, timeout=timeout)
		
	@doc_public
	def areDown(self, urls, timeout=1.0):
		"""
		Check if the list of urls passed as argument are all down

		@param urls: list of url without http(s)://
		@type urls: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all urls are down.
		@rtype: boolean
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		th = []
		# parallelize
		for i in xrange(len(urls)):
			tpl = templates.pinger(destination=urls[i], more=templates.ping(), type=templates.url() )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
			
			pa = UrlAgent(self, urls[i], self.method, self.credentials, self.https, self.timeout )
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if pa.rspCodeReceived is not None:
				tpl = templates.pinger(destination=pa.url, more=templates.alive(), type=templates.url(code=pa.rspCodeReceived,body=pa.rspBodyReceived) )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			else:
				tpl = templates.pinger(destination=pa.url, more=templates.no_response(), type=templates.url() )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )	
			
			expected = templates.pinger(destination=pa.url, more=templates.no_response(), type=templates.url() )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False
		return ret

