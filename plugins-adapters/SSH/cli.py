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

import templates_cli as templates

from Libs import pexpect

__NAME__="""CLI"""

class Cli(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, host, username, password, name=None, port=22, timeout=10.0, prompt="~]#", 
										debug=False, shared=False ):
		"""
		This class enables to connect to a remote host through ssh with an expected prompt
		
		@param parent: define parent (testcase)
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param host: destination host
		@type host: string

		@param username: ssh login
		@type username: string
		
		@param password: ssh password
		@type password: string

		@param port: destination port
		@type port: integer

		@param timeout: time max to wait to receive something (prompt)
		@type timeout: float

		@param prompt: prompt of connection, escape the prompt with special characters (regex supported)
		@type prompt: string	
		
		@param debug: True to activate the debug mode
		@type debug: boolean		

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, realname=name)
		
		self.host = host
		self.username = username
		self.password = password
		self.timeout = timeout
		self.port = port

		self.child = None
		self.connected = False
		self.PROMPT = prompt
		
		self.__checkConfig()
		
	def __checkConfig(self):
		"""
		"""
		try:
			self.port = int(self.port)
		except Exception as e:
			raise TestAdapterLib.AdapterException(TestAdapterLib.caller(), "config ssh: wrong destination port type: %s" % str(self.port) )


	@doc_public
	def login(self):
		"""
		Login to the server
		"""
		# log event
		tpl = templates.ssh(host=self.host, port=self.port,  more=templates.login(username=self.username,password=self.password) )
		self.logSentEvent( shortEvt = "login", tplEvt = tpl )
		
		SSH_NEWKEY = r'Are you sure you want to continue connecting'
		SSH_KEYCHANGED = r'REMOTE HOST IDENTIFICATION HAS CHANGED'
	
		# connect 
		cmdSSH = 'ssh -l %s %s -p %s -o "UserKnownHostsFile /dev/null"' % (self.username, self.host, self.port )
		self.debug( cmdSSH )
		self.child = pexpect.spawn(cmdSSH, timeout=self.timeout)
		r = self.child.expect([pexpect.TIMEOUT, SSH_NEWKEY, '[Pp]assword: ', SSH_KEYCHANGED, pexpect.EOF])
		
		if r == 0:  # Timeout
			self.debug( self.child.before )
			self.onPasswordPromptNotDetected()
		
		elif r == 1: # accept public key.
			# public key stored in the 'known_hosts' cache.
			self.debug( 'public key prompt detected' )
			
			# send yes to accept
			self.child.sendline('yes')
			r = self.child.expect([pexpect.TIMEOUT, '[Pp]assword: '])
			
			if r == 0:  # Timeout
				self.debug( self.child.before )
				self.onPasswordPromptNotDetected()
			
			elif r == 1: # ok
				self.debug( self.child.before )
				self.__type_pass()
			
			else: # unknown error
				self.debug( self.child.before )
				self.error( 'login: sub unknown error' )
		
		elif r == 2: 
			self.debug( self.child.before )
			self.__type_pass()

		elif r == 3:
			self.debug( 'rsa finger has changed detected' )
			self.debug( self.child.before )
			
			# log event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.error(self.child.before) )
			self.logRecvEvent( shortEvt = "connection error: rsa fingerprint has changed", tplEvt = tpl )
			
			# cleanup
			self.cleanProcess()
			
		elif r == 4:
			# ssh: connect to host 227.0.0.2 port 22: Network is unreachable
			# ssh: connect to host 127.0.0.1 port 34: Connection refused
			self.debug( self.child.before )
			errstr =  self.child.before.split(':')[2].strip()

			# log event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.error(errstr.lower()) )
			self.logRecvEvent( shortEvt = "connection error", tplEvt = tpl )
			
			# cleanup
			self.cleanProcess()
		else:
			self.error( 'login: unknown error' )

	def __type_pass(self):
		"""
		"""
		SSH_DENIED = '[Pp]ermission denied, please try again'
		
		self.debug( 'password prompt detected' )
		# send password 
		self.child.sendline(self.password)
		r = self.child.expect([pexpect.TIMEOUT, SSH_DENIED, self.PROMPT])
		
		if r == 0:  # Timeout
			self.debug( self.child.before )
			self.onPromptNotDetected()
		
		elif r == 1:# denied
			self.debug( 'permission denied detected' )
			self.debug( self.child.before )
			
			# log event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.login_failed() )
			self.logRecvEvent( shortEvt = "login failed", tplEvt = tpl )
			
			# cleanup
			self.cleanProcess()
		elif r == 2: # ok 
			self.debug( 'prompt %s detected' % self.PROMPT)
			self.debug( self.child.before )
			self.connected = True

			# log event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.connected() )
			self.logRecvEvent( shortEvt = "connected", tplEvt = tpl )

		else:
			self.error( 'prompt: unknown error' )		
			
	def sendData(self, data, dataExpected=''):
		"""
		Send data over SSH

		@param data: data to send over ssh
		@type data: string
		
		@param dataExpected: expected data on response
		@type dataExpected: string
		"""
		if not self.connected:
			self.debug( 'not connected' )
			return
		
		# log event
		tpl = templates.ssh(host=self.host, port=self.port, more=templates.data_sent(data=data) )
		self.logSentEvent( shortEvt = "data", tplEvt = tpl )
		
		# send command line
		self.child.send(data)
		if len(dataExpected):
			r = self.child.expect([pexpect.TIMEOUT, dataExpected])
		else:
			r = self.child.expect([pexpect.TIMEOUT, self.PROMPT])
		
		if r == 0:  # Timeout
			self.debug( self.child.before )
			self.onPromptNotDetected()
		
		elif r == 1: # ok, expected condition
			# split cmd 
			data_received = "%s%s%s" % ( self.child.after, self.child.before, self.child.after )
			
			# log received event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.data_received(data=data_received) )
			self.logRecvEvent( shortEvt = "data", tplEvt = tpl )
		
		else:
			self.error( 'send data: unknown error' )
			
	@doc_public
	def logout(self):
		"""
		Disconnect from the server
		"""
		if self.connected:
			# log event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.logout() )
			self.logSentEvent( shortEvt = "logout", tplEvt = tpl )
			self.connected = False
			
			# optional step, just to be clean
			self.child.sendline('exit')
			
			# log event
			tpl = templates.ssh(host=self.host, port=self.port, more=templates.disconnected() )
			self.logRecvEvent( shortEvt = "disconnected", tplEvt = tpl )
			
		# cleanup
		self.cleanProcess()
	
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		self.cleanProcess()
		
	def cleanProcess(self):
		"""
		"""
		if self.child != None:
			self.child.terminate()
			self.child.close()
	
	def onPromptNotDetected(self):
		"""
		"""
		self.debug( 'prompt %s not detected' % self.PROMPT )
		
		# log event
		errstr = 'prompt not detected'
		tpl = templates.ssh(host=self.host, port=self.port, more=templates.error(errstr) )
		self.logRecvEvent( shortEvt = "prompt error", tplEvt = tpl )
		
		# cleanup
		self.cleanProcess()
	
	
	def onPasswordPromptNotDetected(self):
		"""
		"""
		self.debug( 'password prompt not detected' )
		
		# log event		
		errstr = 'password prompt not detected'
		tpl = templates.ssh(host=self.host, port=self.port, more=templates.error(errstr) )
		self.logRecvEvent( shortEvt = "password prompt error", tplEvt = tpl )
			
		# cleanup
		self.cleanProcess()
	
	@doc_public
	def hasReceivedData(self, timeout=1.0, data=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param data: data expected
		@type data:	string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.ssh(host=self.host, port=self.port, more=templates.data_received(data) )
		evt = self.received( expected = expected, timeout = timeout )
		return evt
	
	@doc_public
	def isConnected(self, timeout=1.0):
		"""
		Waits to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.ssh(host=self.host, port=self.port, more=templates.connected() )
		evt = self.received( expected = expected, timeout = timeout )
		return evt
	
	@doc_public
	def isDisconnected(self, timeout=1.0):
		"""
		Waits to receive "disconnected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.ssh(host=self.host, port=self.port, more=templates.disconnected() )
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def isLoginFailed(self, timeout=1.0):
		"""
		Waits to receive "login failed" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.ssh(host=self.host, port=self.port, more=templates.login_failed() )
		evt = self.received( expected = expected, timeout = timeout )
		return evt

	@doc_public
	def isError(self, timeout=1.0, errReason=None):
		"""
		Waits to receive "error" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@param data: error reason expected
		@type data:	string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.ssh(host=self.host, port=self.port, more=templates.error(errReason) )
		evt = self.received( expected = expected, timeout = timeout )
		return evt