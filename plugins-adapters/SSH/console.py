#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestTemplatesLib as TestTemplates
from TestExecutorLib.TestExecutorLib import doc_public

import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import io
import time
import stat

import copy

import codec_ssh
import templates
import client

client = sys.modules['SutAdapters.%s.SSH' % TestAdapter.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IP' % TestAdapter.getVersion()]

__NAME__="""SSH_Console"""

class Console(TestAdapter.Adapter):
	@doc_public
	def __init__(self, parent,  destIp, destPort=22, bindIp = '0.0.0.0', bindPort=0,  destHost='', prompt ='~]#',
									login='admin', password='admin', privateKey=None, verbose=True,
									socketTimeout=10.0, socketFamily=AdapterIP.IPv4,  name=None, tcpKeepAlive=False, tcpKeepAliveInterval=30.0,
									debug=False, logEventSent=True, logEventReceived=True, parentName=None, shared=False, sftpSupport=False,
									agent=None, agentSupport=False, loopFrequence = 1):
		"""
		Adapter based on SSH.
		Send command for given period
		Automatic connect and disconnection if not done before
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param login: ssh login (default=admin)
		@type login: string
		
		@param privateKey: string private key to use to authenticate, push your public key on the remote server
		@type privateKey: string
		
		@param verbose: False to disable verbose mode (default=True)
		@type verbose: boolean
		
		@param password: ssh password (default=admin)
		@type password: string
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer

		@param destIp: destination ip
		@type destIp: string

		@param destPort: destination port
		@type destPort: integer

		@param destHost: destination host (automatic dns resolution)
		@type destHost: string

		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: intconstant

		@param socketTimeout: timeout to connect in second (default=1s)
		@type socketTimeout: float

		@param tcpKeepAlive: turn on tcp keep-alive (defaut=False)
		@type tcpKeepAlive: boolean

		@param tcpKeepAliveInterval: tcp keep-alive interval (default=30s)
		@type tcpKeepAliveInterval: float

		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean

		@param agent: agent to use
		@type agent: string/none
		
		@param agentSupport: agent support (default=False)
		@type agentSupport:	boolean
		
		@param loopFrequence: interval of time for a command to be sent again when using sendCommandLoop (default=1)
		@type loopFrequence:	integer
		"""
		# init adapter
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		
		self.parent = parent
		
		self.__connected = False
		self.__logged = False
		name_ssh ="ssh_"
		if name is None:
			name_ssh = None
		else:
			name_ssh ="ssh_"+name
		self.ADP_SSH = client.Client(parent=parent, login=login, password=password, privateKey=privateKey,
																							bindIp=bindIp, bindPort=bindPort,  destIp=destIp, destPort=destPort, 
																				destHost=destHost, socketTimeout=socketTimeout, socketFamily=socketFamily, name=name_ssh, debug=debug,
																				logEventSent=True, logEventReceived=logEventReceived, parentName=__NAME__, shared=shared,
																				sftpSupport=sftpSupport, agent=agent,  agentSupport=agentSupport, verbose = verbose
																				)
		self.buf = ''
		self.prompt=prompt
		self.codec = codec_ssh.Codec(parent=self)
		self.cfg = {}
		
		self.cfg['dst-ip'] = destIp
		self.cfg['dst-port'] = destPort
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		
		self.cfg['user'] = login
		self.cfg['password'] = password

		
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
			
		self.__logged = False
	
		self.__checkConfig()
		
		self.TIMER_LOGS = TestAdapter.Timer(parent=self, duration=loopFrequence, name="send-commands", callback=self.redoCommand, logEvent=False, enabled=True)
		self.command = ''
		self.delimiter = "password:"
		# wrap function
		self.ADP_SSH.handleIncomingData = self.handleIncomingData
		
	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug("config: %s" % self.cfg)

	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		self.ADP_SSH.onReset()

	def ssh(self):
		"""
		Return ssh level
		"""
		return self.ADP_SSH

	@doc_public
	def doConnect(self, timeout=1.0, prompt='~]#'):
		"""
		Do connect with authentification

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@param prompt: ssh prompt (default=~]#)
		@type prompt: string
		
		@return: True is successfully connected, false otherwise
		@rtype: boolean	
		"""
		return self.ADP_SSH.doConnect(timeout=timeout,prompt=prompt)
	@doc_public
	def doDisconnect(self, timeout=1.0):
		"""
		Do disconnect

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			

		@return: True is successfully connected, false otherwise
		@rtype: boolean	
		"""
		return self.ADP_SSH.doDisconnect(timeout=timeout)

	@doc_public
	def connect(self):
		"""
		Connect to the SSH server
		Login is performed in automatic
		"""
		self.ADP_SSH.connect()
		
	@doc_public
	def disconnect(self):
		"""
		Disconnect from the SCP server
		"""
		self.ADP_SSH.disconnect()

	@doc_public
	def isNegotiated(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Wait received is negotiated event until the end of the timeout
	
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@param versionIp: version ip expected
		@type versionIp: string/operators/none	
	
		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		return self.ADP_SSH.isNegotiated(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)

	@doc_public
	def isAuthenticated(self, timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Wait received is authenticated event until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@param versionIp: version ip expected
		@type versionIp: string/operators/none	

		@param sourceIp: source ip expected
		@type sourceIp:	string/operators/none	
		
		@param destinationIp: destination ip expected
		@type destinationIp: string/operators/none	
		
		@param sourcePort: source port expected
		@type sourcePort:	string/operators/none
		
		@param destinationPort: destination port expected
		@type destinationPort: string/operators/none	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		return self.ADP_SSH.isAuthenticated(timeout=timeout, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)

	def getExpectedTemplate(self, tpl, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Return an expected template with ip and tcp layers
		"""
		return self.ADP_SSH.getExpectedTemplate(tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, sourcePort=sourcePort, destinationPort=destinationPort)
		
	@doc_public
	def hasReceivedData(self, timeout=1.0, dataExpected=None, delimiter = ""):
		"""
		Wait received data event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param dataExpected: data expected (default=None)
		@type dataExpected:	string/operators/None			
		
		@param delimiter: expected string (default="") => This parameter must be used in case no prompt is expected yet, and the shell is currently waiting
		@type delimiter:	string/operators/None			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage/none
		"""
		self.delimiter = delimiter
		# construct the expected template
		tpl = templates.data_received(data=dataExpected)
		expected = self.getExpectedTemplate(tpl=tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		self.delimiter = ""
		return evt
		
			
	def encapsule(self, ip_event, ssh_event):
		"""
		"""
		return self.ADP_SSH.encapsule(ip_event=ip_event, ssh_event=ssh_event)
	
	@doc_public
	def doSendCommandLoop(self, command, prompt='~]#'):
		"""
		Send a command multiple times until the method stopSendingCommand is called.
	
		@param command: ssh command
		@type command: string
		
		@param prompt: ssh prompt (default=~]#)
		@type prompt: string	
		
		@return: command response as string or None otherwise
		@rtype: string/none		
		"""
		ret = None
		internalConnect = False

		self.command = command	
		cmd = "%s\n" % self.command
		try:
			self.ssh().sendData( dataRaw=cmd )
			self.TIMER_LOGS.start()

			if internalConnect:
				# disconnect phase
				self.disconnect()
				if self.isDisconnected(timeout=timeout) is None:
					return None
			return ret
		except Exception as e:
			self.error( "Error doing command loop: %s" % str(e) )
	
	@doc_public
	def redoCommand(self):
		"""
		Send a command each time the timer calls this function
		"""
		ret = None

#		# send command
		cmd = "%s\n" % self.command
		try:
			self.ssh().sendData( dataRaw=cmd )
			self.TIMER_LOGS.restart()
			
		except Exception as e:
			self.error( "Error doing command loop: %s" % str(e) )

	@doc_public
	def stopSendingCommand(self):
		"""
		Stop the command loop
		"""
		self.TIMER_LOGS.stop()
				
	@doc_public
	def sendData(self, dataRaw=None):
		"""
		Send ssh data

		@param tpl: ssh template data (default=None)
		@type tpl: templatelayer/none
		
		@param dataRaw: ssh data (default=None)
		@type dataRaw: string/none
	
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage	
		"""
		
		self.ADP_SSH.sendData(dataRaw=dataRaw +"\n")
		
	@doc_public
	def isConnected(self,timeout=1.0):
		"""
		Wait Connected event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		return self.ADP_SSH.isConnected(timeout=timeout)
	@doc_public
	def isChannelOpened(self,timeout=1.0):
		"""
		Wait logged event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		return self.ADP_SSH.isChannelOpened(timeout=timeout)
	
	@doc_public
	def automaticPasswordUpdate(self, timeout=1.0, currentPassword="", newPassword="", currentRootPassword="", newRootPassword="", login=""):
		self.info("detecting request for password change")
		data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["WARNING","current","password"], AND=True, OR=False) , delimiter = "password:")
		if data is not None:
			self.info("entering current password")
			self.delimiter = "password:"
			self.sendData( dataRaw="%s\n" % currentPassword)
		else:
			return
		data = self.hasReceivedData(timeout=timeout, dataExpected=TestOperators.Contains(needle=["New","password" ], AND=True, OR=False) , delimiter = "password:")
		if data is not None:
			self.info("entering new password")
			self.delimiter = "password:"
			self.sendData( dataRaw="%s\n" % newPassword)
		else:
			return
		data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["new","password" ] , AND=True, OR=False), delimiter = "password:")
		if data is not None:
			self.sendData( dataRaw="%s\n" % newPassword)
			self.cfg['password'] = newPassword
			self.cfg['private-key'] = None
			self.ADP_SSH.cfg['password'] = newPassword
			self.ADP_SSH.cfg['private-key'] = None
		else:
			return
		data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["passwd: all authentication tokens updated successfully." ] , AND=True, OR=False), delimiter = "passwd: all authentication tokens updated successfully.")
		if data is not None:
			self.disconnect()
			time.sleep(1)
			self.connect()

		else:
			return
			
		#-------Changing Root Password------------------------
		if self.isChannelOpened(timeout=60):
			self.info("detecting request for root password change")
			self.sendData( dataRaw="%s\n" % "su")
			data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["Password"], AND=True, OR=False) , delimiter = "Password:")
			if data is not None:
				self.sendData( dataRaw="%s\n" % currentRootPassword)
			else:
				return
			data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["current","password"], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering current password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % currentRootPassword)
			else:
				return
			data = self.hasReceivedData(timeout=timeout, dataExpected=TestOperators.Contains(needle=["ew","password" ], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering new password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % newRootPassword)
			else:
				return
			
			
			#-------Put old Root Password again------------------------
			self.sendData( dataRaw="%s\n" % "su")
			data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["password"], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering current password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % newRootPassword)
			else:
				return
			
			self.sendData( dataRaw="%s\n" % "passwd")
			data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["password"], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering current password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % currentRootPassword)
			else:
				return
			data = self.hasReceivedData(timeout=timeout, dataExpected=TestOperators.Contains(needle=["ew","password" ], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering new password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % currentRootPassword)
			else:
				return
				
				
				
			#-------Put old osadmin Password again------------------------
			self.sendData( dataRaw="passwd %s\n"%login)
			data = self.hasReceivedData( timeout=timeout, dataExpected=TestOperators.Contains(needle=["password"], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering current password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % currentPassword)
			else:
				return
			data = self.hasReceivedData(timeout=timeout, dataExpected=TestOperators.Contains(needle=["ew","password" ], AND=True, OR=False) , delimiter = "password:")
			if data is not None:
				self.info("entering new password")
				self.delimiter = "password:"
				self.sendData( dataRaw="%s\n" % currentPassword)
			else:
				return
			self.sendData( dataRaw="%s\n" % "exit")

	@doc_public
	def isDisconnected(self,timeout=1.0, byServer=False, versionIp=None, sourceIp=None, destinationIp=None, 
										sourcePort=None, destinationPort=None):
		"""
		Wait disconnected event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float			
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage
		"""
		return self.ADP_SSH.isDisconnected(timeout=timeout, byServer=byServer, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
										sourcePort=sourcePort, destinationPort=destinationPort)
	def getAllReceivedData(self):
			"""
			Get All data received by the SSH Agent.
			"""
			buffer = self.buf
			self.buf = ""
			return buffer
						
	def handleIncomingData(self, data, lower=None):
		"""
		Called on incoming data
		
		@param data: tcp data received
		@type data: string
		
		@param lower: template tcp data received
		@type lower: templatemessage
		"""
		if lower is not None:
			layer_app = lower.get('SSH')
			app_data = layer_app.get('data')
			self.buf += app_data
		try:
			self.privateAppendFile(destname="ssh_dump", data=data)
			decoded_msgs, left = self.codec.decode(data=self.buf, delimiter = self.delimiter)
			self.buf = left
			for d in decoded_msgs:
				summary = d.replace("\r","")
				new_tpl = self.encapsule(ip_event=AdapterIP.received(), ssh_event=templates.data_received(data=summary))
				new_tpl.addRaw(summary)
				self.logRecvEvent( shortEvt = "ssh", tplEvt = new_tpl ) 

		except Exception as e:
			self.error('Error while waiting on incoming data: %s' % str(e))
			self.info("buffer = " + self.buf)
			
	def handleNoMoreData(self, lower):
		"""
		Function to reimplement
		
		@param lower:
		@type lower:
		 """
		self.alldatareceived = True
		pass
	@doc_public
	def doSendCommand(self, command, timeout=1.0, dataExpected=None, delimiter=""):
		"""
		Send ssh data

		@param tpl: ssh template data (default=None)
		@type tpl: templatelayer/none
		
		@param command: ssh data to send (default=None)
		@type command: string
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param dataExpected: data expected (default=None)
		@type dataExpected:	string/operators/None			
		
		@param delimiter: expected string (default="") => This parameter must be used in case no prompt is expected yet, and the shell is currently waiting
		@type delimiter:	string		
	
		@return: data from ssh output gathered after the command
		@rtype: templatemessage	
		"""
		self.sendData(command)
		if dataExpected is None:
			dataExpected = TestOperators.Contains(needle=command, AND=False, OR=True)
		
		rsp = self.hasReceivedData(timeout, dataExpected, delimiter)
		return rsp
	
	def onSSHEvent(self, event):
			pass