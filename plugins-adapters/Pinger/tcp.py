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
from TestExecutorLib.TestExecutorLib import doc_public

import sys

import templates

import threading
import subprocess
import os

__NAME__="""PINGER TCP"""

class TcpPingAgent(threading.Thread):
	def __init__(self, parent, host, destPort, nbSyn):
		"""
		"""
		threading.Thread.__init__(self)
		self.parent = parent
		self.nbSyn = nbSyn
		self.destPort = destPort
		self.host = host
		self.isup = False
		self.binHping = "/usr/sbin/hping3"

	def run(self):
		"""
		"""
		_cmd = "%s -S -c %s -p %s %s --tcpexitcode" % (self.binHping, self.nbSyn, self.destPort, self.host)
		ret = subprocess.call(_cmd,	shell=True,  stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
		self.trace( "exit code received: %s" % str(ret) )
		if ret == 18:
			self.isup = True
	
	def trace(self, msg):
		"""
		"""
		if self.parent.debug:
			self.parent.trace( "[%s] %s" % ( self.__class__.__name__, msg) )


class HostTCP(TestAdapterLib.Adapter):
	@doc_public
	def __init__(self, parent, name=None, nbSyn=2, destPort=80, debug=False, shared=False):
		"""
		This class enable to check the status of a network element with transport TCP level.
		SYN requests are used to do that, if the host reply with SYN/ACK in response to SYN then the service is up otherwise down. 

		@param parent: define parent (testcase or component)
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param nbSyn: number of SYN request to send. The default value is 2 requests
		@type nbSyn: integer

		@param destPort: destination TCP port. The default value is 80 (http)
		@type destPort: integer		

		@param debug: True to activate the debug mode (default=False)
		@type debug: boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, realname=name)
		self.nbSyn = nbSyn
		self.destPort = destPort
		self.debug=debug
		self.binHping = "/usr/sbin/hping3"
		if not os.path.exists( self.binHping ):
			raise Exception('hping3 binary is not installed')
			
	@doc_public
	def doIsUp(self, host, timeout=1.0):
		"""
		Check if the host passed as argument is up. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default value=1s)
		@type timeout: float
		
		@return: True is the host is UP, False otherwise
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
	def isUp(self, host, timeout=1.0):
		"""
		Check if the host passed as argument is up. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default value=1s)
		@type timeout: float
		
		@return: alive event
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates.pinger(destination=host, more=templates.ping(), type=templates.tcp(destination=self.destPort) )
		self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
			
		pa = TcpPingAgent(self, host, self.destPort, self.nbSyn)
		pa.start()
		# synchronization
		pa.join()
		ret= pa.isup
		if not ret:
			tpl = templates.pinger(destination=host, more=templates.no_response(), type=templates.tcp(destination=self.destPort) )
			self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
		else:
			tpl = templates.pinger(destination=host, more=templates.alive(), type=templates.tcp(destination=self.destPort) )
			self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )	

		expected = templates.pinger(destination=host, more=templates.alive(), type=templates.tcp(destination=self.destPort) )
		evt = self.received( expected = expected, timeout = timeout )
		return evt
		

	@doc_public
	def doIsDown(self, host, timeout=1.0):
		"""
		Check if the host passed as argument is down. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: True if the host is down, False otherwise
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) )  or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		ret = False
		evt = self.isDown(host=host, timeout=timeout)
		if evt is not None:
			ret = True
		return ret
		
	@doc_public
	def isDown(self, host, timeout=1.0):
		"""
		Check if the host passed as argument is down. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: no response event
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = templates.pinger(destination=host, more=templates.ping(), type=templates.tcp(destination=self.destPort) )
		self.logSentEvent( shortEvt = "ping", tplEvt = tpl )
	
		pa = TcpPingAgent(self, host, self.destPort, self.nbSyn)
		pa.start()
		# synchronization
		pa.join()
		ret= pa.isup
		if ret:
			tpl = templates.pinger(destination=host, more=templates.alive(), type=templates.tcp(destination=self.destPort) )
			self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
		else:
			tpl = templates.pinger(destination=host, more=templates.no_response(), type=templates.tcp(destination=self.destPort) )
			self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
		
		expected = templates.pinger(destination=host, more=templates.no_response(), type=templates.tcp(destination=self.destPort) )
		evt = self.received( expected = expected, timeout = timeout )
		return evt
		
	@doc_public
	def doAreUp(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are up. This check takes approximately 3 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all hosts are up.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.areUp(hosts=hosts, timeout=timeout)
		
	@doc_public
	def areUp(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are up. This check takes approximately 3 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all hosts are up.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		th = []
		# parallelize
		for i in xrange(len(hosts)):
			tpl = templates.pinger(destination=hosts[i], more=templates.ping(), type=templates.tcp(destination=self.destPort) )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )

			pa = TcpPingAgent(self, hosts[i], self.destPort, self.nbSyn)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if not pa.isup:
				tpl = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.tcp(destination=self.destPort) )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
				ret = False
			else:
				tpl = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.tcp(destination=self.destPort) )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			
			expected = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.tcp(destination=self.destPort) )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False

		return ret


	@doc_public
	def doAreDown(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are down. This check takes approximately 3 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all hosts are down.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.areDown(hosts=hosts, timeout=timeout)
		
	@doc_public
	def areDown(self, hosts, timeout=1.0):
		"""
		Check if all hosts passed as argument are down. This check takes approximately 3 sec.

		@param hosts: list of IPv4 or hostname
		@type hosts: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all hosts are down.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		th = []
		# parallelize
		for i in xrange(len(hosts)):
			tpl = templates.pinger(destination=hosts[i], more=templates.ping(), type=templates.tcp(destination=self.destPort) )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )

			pa = TcpPingAgent(self, hosts[i], self.destPort, self.nbSyn)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if pa.isup:
				tpl = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.tcp(destination=self.destPort) )
				self.logRecvEvent( shortEvt = "aive", tplEvt = tpl )
				ret = False
			else:
				tpl = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.tcp(destination=self.destPort) )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
			
			expected = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.tcp(destination=self.destPort) )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False	
				
		return ret

	@doc_public
	def doPortsAreUp(self, host, ports, timeout=1.0):
		"""
		Check if all ports passed as argument are up for one specific host. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param ports: list of port
		@type ports: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all ports are up.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.portsAreUp(host=host, ports=ports, timeout=timeout)
		
	@doc_public
	def portsAreUp(self, host, ports, timeout=1.0):
		"""
		Check if all ports passed as argument are up for one specific host. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param ports: list of port
		@type ports: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all ports are up.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		th = []
		# parallelize
		for tcpPort in ports:
			tpl = templates.pinger(destination=host, more=templates.ping(), type=templates.tcp(destination=tcpPort) )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )

			pa = TcpPingAgent(self, host, tcpPort, self.nbSyn)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if not pa.isup:
				ret = False
				tpl = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.tcp(destination=pa.destPort) )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
			else:
				tpl = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.tcp(destination=pa.destPort) )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			
			expected = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.tcp(destination=pa.destPort) )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False				
		return ret


	@doc_public
	def doPortsAreDown(self, host, ports, timeout=1.0):
		"""
		Check if all ports passed as argument are down for one specific host. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param ports: list of port
		@type ports: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all ports are down.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.portsAreDown(host, ports=ports, timeout=timeout)
		
	@doc_public
	def portsAreDown(self, host, ports, timeout=1.0):
		"""
		Check if all ports passed as argument are down for one specific host. This check takes approximately 3 sec.

		@param host: IPv4 or hostname
		@type host: string

		@param ports: list of port
		@type ports: list

		@param timeout: time to wait in second (default=1s)
		@type timeout: float
		
		@return: global status, True if all ports are down.
		@rtype: boolean
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		th = []
		# parallelize
		for tcpPort in ports:
			tpl = templates.pinger(destination=host, more=templates.ping(), type=templates.tcp(destination=tcpPort) )
			self.logSentEvent( shortEvt = "ping", tplEvt = tpl )

			pa = TcpPingAgent(self, host, tcpPort, self.nbSyn)
			pa.start()
			th.append(pa)
		# synchronize
		for pa in th:
			pa.join()
		# compute final result
		ret = True
		for pa in th:
			if pa.isup:
				ret = False
				tpl = templates.pinger(destination=pa.host, more=templates.alive(), type=templates.tcp(destination=pa.destPort) )
				self.logRecvEvent( shortEvt = "alive", tplEvt = tpl )
			else:
				tpl = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.tcp(destination=pa.destPort) )
				self.logRecvEvent( shortEvt = "no response", tplEvt = tpl )
			
			expected = templates.pinger(destination=pa.host, more=templates.no_response(), type=templates.tcp(destination=pa.destPort) )
			evt = self.received( expected = expected, timeout = timeout )
			if evt is None:
				ret = False	
		return ret
