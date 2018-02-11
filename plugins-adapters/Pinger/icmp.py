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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys

import templates

import subprocess
import threading
import os

__NAME__="""PINGER ICMP"""

class PingAgent(threading.Thread):
	def __init__(self, parent, host, nbPing):
		"""
		"""
		threading.Thread.__init__(self)
		self.parent = parent
		self.nbIcmpRequest = nbPing
		self.host = host
		self.isup = False
		self.binPing = "/bin/ping"

	def run(self):
		"""
		"""
		if not os.path.exists( self.binPing ):
				raise Exception('ping binary is not installed')
		ret = subprocess.call("%s -c %s %s" % (self.binPing, self.nbIcmpRequest, self.host),
				shell=True,  stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
		if ret == 0:
			self.isup = True

class HostICMP(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, name=None, nbPing=2, debug=False, shared=False):
		"""
		This class enable to check the status of a network element. Requests ICMP are used to do that, a node is up if an echo reply a received.

		@param parent: define parent (testcase or component)
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param nbPing: number of icmp request to check the status. The default value is 2 requests
		@type nbPing: integer

		@param debug: True to activate the debug mode (default=False)
		@type debug: boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, realname=name)
		self.nbPing = nbPing
		self.debug=debug

	@doc_public
	def doIsUp(self, host, timeout=1.0):
		"""
		Do a test on the host to check if alive

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float		

		@return: True for UP, False otherwise
		@rtype: boolean		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = False
		evt = self.isUp(host=host, timeout=timeout)
		if evt is not None:
			ret = True
		return ret
		
	@doc_public
	def doIsDown(self, host, timeout=1.0):
		"""
		Do a test on the host to check if down

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float		

		@return: True for down, False otherwise
		@rtype: boolean		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = False
		evt = self.isDown(host=host, timeout=timeout)
		if evt is not None:
			ret = True
		return ret
		
	@doc_public
	def isUp(self, host, timeout=1.0):
		"""
		Check if the host passed as argument is up. This check takes approximately 10 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: alive event
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates.pinger(destination=host, more=templates.ping(), type=templates.icmp() )
		self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
	
		pa = PingAgent(self, host, self.nbPing)
		pa.start()
		# synchronization
		pa.join()
		ret= pa.isup
		if not ret:
			tpl = templates.pinger(destination=host, more=templates.no_response(), type=templates.icmp() )
			self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
		else:
			tpl = templates.pinger(destination=host, more=templates.alive(), type=templates.icmp() )
			self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )

		expected = templates.pinger(destination=host, more=templates.alive(), type=templates.icmp() )
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def isDown(self, host, timeout=1.0):
		"""
		Check if the host passed as argument is down. This check takes approximately 10 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: no response event
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates.pinger(destination=host, more=templates.ping(), type=templates.icmp() )
		self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
		
		pa = PingAgent(self, host, self.nbPing)
		pa.start()
		# synchronization
		pa.join()
		ret= pa.isup
		if ret:
			tpl = templates.pinger(destination=host, more=templates.alive(), type=templates.icmp() )
			self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
		else:
			tpl = templates.pinger(destination=host, more=templates.no_response(), type=templates.icmp() )
			self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )

		expected = templates.pinger(destination=host, more=templates.no_response(), type=templates.icmp() )
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def doAreUp(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are up. This check takes approximately 10 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: True if all hosts are up.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.areUp(hosts=hosts, timeout=timeout)
		

	@doc_public
	def doAreDown(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are down. This check takes approximately 10 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: True if all hosts are up.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.areDown(hosts=hosts, timeout=timeout)
		
	@doc_public
	def areUp(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are up. This check takes approximately 10 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: True if all hosts are up, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		th = []
		# parallelize
		for i in xrange(len(hosts)):
			tpl = templates.pinger(destination=hosts[i], more=templates.ping(), type=templates.icmp() )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )

			pa = PingAgent(self, hosts[i], self.nbPing)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if not pa.isup:
				tpl = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.icmp() )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
			else:
				tpl = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.icmp() )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			
			expected = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.icmp() )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False
		return ret


	@doc_public
	def areDown(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are down. This check takes approximately 10 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: True if all hosts are down, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		th = []
		# parallelize
		for i in xrange(len(hosts)):
			tpl = templates.pinger(destination=hosts[i], more=templates.ping(), type=templates.icmp() )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
			
			pa = PingAgent(self, hosts[i], self.nbPing)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if pa.isup:
				tpl = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.icmp() )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			else:
				tpl = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.icmp() )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
			
			expected = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.icmp() )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False
		return ret