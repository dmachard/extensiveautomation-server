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

AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapterLib.getVersion()]

import threading
import socket
import select
import time

import templates

__NAME__="""UDP"""

class Server(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, bindIp = '', bindPort=0, 
								socketFamily=AdapterIP.IPv4, name=None,
								separatorIn='\\x00', separatorOut='\\x00', separatorDisabled=False,
								debug=False, logEventSent=True, logEventReceived=True,
								parentName=None, shared=False
						):
		"""
		This class enable to use the protocol UDP as server only.
		Lower network layer (IP, Ethernet) are not controlable.
		Support data separator for upper application and inactivity detection.
		
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer

		@param socketFamily: SutAdapters.IP.IPv4 (default) | SutAdapters.IP.IPv6 
		@type socketFamily: integer
		
		@param separatorIn: data separator (default=\\x00)
		@type separatorIn: string

		@param separatorOut: data separator (default=\\x00)
		@type separatorOut: string

		@param separatorDisabled: disable the separator feature, if this feature is enabled then data are buffered until the detection of the separator (default=False)
		@type separatorDisabled: boolean
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, realname=name)
		if parentName is not None:
			TestAdapterLib.Adapter.setName(self, name="%s>%s" % (parentName,__NAME__) )
		self.__mutex__ = threading.RLock()
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived		
		self.parent = parent
		self.sourceIp = bindIp
		self.sourcePort = bindPort
		self.islistening = False
		self.clients = {}
		
		self.cfg = {}
		# transport options
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		# socket options
		self.cfg['sock-family'] =  int(socketFamily)
		# data separators 
		self.cfg['sep-in'] = separatorIn
		self.cfg['sep-out'] = separatorOut
		self.cfg['sep-disabled'] = separatorDisabled
		self.__checkConfig()
		
		self.clientId = 0
		self.idMutex = threading.RLock()
	def getId(self):
		"""
		"""
		self.idMutex.acquire()
		self.clientId += 1
		ret = self.clientId
		self.idMutex.release()
		return ret				
	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)
	
	def __setSource(self):
		"""
		"""
		srcIp, srcPort = self.socket.getsockname() # ('127.0.0.1', 52318)
		self.sourceIp = srcIp
		self.sourcePort = srcPort		
		
	def setSource(self, bindIp, bindPort):
		"""
		Set the source ip/port
		
		@param bindIp: bind on ip (source ip)
		@type bindIp: string

		@param bindPort: bind on port (source port)
		@type bindPort: integer
		"""
		self.cfg['bind-ip'] = bindIp
		self.cfg['bind-port'] = bindPort
		
	def encapsule(self, ip_event, udp_event, src_ip=None, src_port=None):
		"""
		"""
		# prepare layers
		src = self.sourceIp
		srcP = self.sourcePort
		dst = ''
		dstP = ''
		if src_ip is not None:
			src = src_ip
			dst = self.sourceIp
		if src_port is not None:
			srcP = src_port
			dstP = self.sourcePort
		layer_ip = AdapterIP.ip( source=src, destination=dst, version=self.cfg['sock-family'], more=ip_event ) 
		layer_udp = templates.udp(source=srcP, destination=dstP)
		layer_udp.addMore(more=udp_event)
		
		# prepare template
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_udp)
		return tpl

	@doc_public
	def stopListening(self):
		"""
		Stop listening
		"""
		self.__mutex__.acquire()
		if self.islistening:
			self.debug( 'stopping to listen' )
			# log event
			self.islistening = False
			tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.stopping() )
			self.logSentEvent( shortEvt = "stopping", tplEvt = tpl )		
			
			#	clean socket	
			self.cleanSocket()
			
			# dispatch
			self.onStopListening()
		self.__mutex__.release()
		
	def cleanSocket(self):
		"""
		"""
		self.debug( 'clean the socket' )
		self.unsetRunning()
		# clean the socket
		if self.socket is not None:
			self.socket.close()
			self.islistening = False

	@doc_public
	def startListening(self):
		"""
		Start listening
		"""
		if self.islistening:
			self.debug( 'already listening' )
			return 
			
		# Start the tcp connection
		self.debug( 'starting to listen' )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.starting() )
		self.logSentEvent( shortEvt = "starting", tplEvt = tpl )		
		self.__mutex__.acquire()
		try:
			# set the socket version
			if self.cfg['sock-family'] == AdapterIP.IPv4:
				sockType = TestAdapterLib.INIT_DGRAM_SOCKET
			elif  self.cfg['sock-family'] == AdapterIP.IPv6:
				sockType = TestAdapterLib.INIT6_DGRAM_SOCKET
			else:
				raise Exception('socket family unknown: %s' % str(self.cfg['socket-family']) )	
			
			# Create the socket
			self.socket = TestAdapterLib.getSocket(sockType=sockType)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.debug( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
			self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
			
			# listening successful
			self.__setSource()	
			
			# dispatch 
			self.lastActivity = time.time()
			self.islistening = True
			self.onStartListening()
			
			# start thread
			self.setRunning()
		except socket.error, e:
			self.onStartListeningFailed(e)
		except Exception as e:
			self.error( "start listen error: %s" % str(e) )
			self.stopListening()
		self.__mutex__.release()
		
	def onRun(self):
		"""
		"""
		self.__mutex__.acquire()
		try:
			if self.socket is not None:  
				if self.islistening:
						r, w, e = select.select([ self.socket ], [], [], 0.01)
						for s in r:
							if s is not None:
								(data, addr) = s.recvfrom(65535)
								self.debug( 'incoming data from %s' % str(addr) )
								if self.cfg['sep-disabled']:
									if addr in self.clients:
										self.onClientIncomingData(clientAddress=addr, data=data)
									else:
										self.clients[addr] = { 'buffer': data, 'id': self.getId() }
										self.onClientIncomingData(clientAddress=addr, data=data)
								else:
									if addr in self.clients:
										self.clients[addr]['buffer'] = ''.join([self.clients[addr]['buffer'], data])
									else:
										self.clients[addr] = { 'buffer': data, 'id': self.getId() }
									self.onClientIncomingData(clientAddress=addr)		
		except socket.error, e:
			self.onSocketError(e)					
		except Exception as e:
			self.error( "on run %s" % str(e) )
		self.__mutex__.release()

	@doc_public
	def sendData(self, clientId, data):
		"""
		Send data over the udp protocol

		@param clientId: client id number
		@type clientId: integer/string
		
		@param data: data to send over udp
		@type data: string		

		@return: udp layer encapsulate in ip
		@rtype: templatemessage
		"""
		try:
			#self.debug( "data to sent (bytes %s) to %s"  % (len(data), to) )
			if not self.islistening:
				self.debug( "not listening" )
				return

			# find the client 
			destAddr = None
			for clientAddress, client in self.clients.items():
				if client['id'] == int(clientId):
					destAddr = clientAddress
					break
			
			if destAddr is None:
				self.error( "client id %s does not exist!" % clientId )
				return
			
			# add the separator to the end of the data, if the feature is enabled	
			if self.cfg['sep-disabled']:
				pdu = data
			else:
				pdu =  data + self.cfg['sep-out']

			# log event
			pdu_size = len(pdu)
			if self.logEventSent:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.sent(data=pdu, data_length=str(pdu_size), id=clientId) )
			else:
				tpl = self.encapsule( ip_event=AdapterIP.sent(), udp_event=templates.sent( data_length=str(pdu_size), id=clientId ) )
			if self.logEventSent:
				tpl.addRaw(raw=pdu)
				self.logSentEvent( shortEvt = "client #%s data" % clientId, tplEvt = tpl )
				
			# send the packet
			self.socket.sendto(pdu, destAddr)
			self.debug( "data sent (bytes %s) for client %s"  % (len(pdu), str(destAddr)) )
			return tpl
		except Exception as e:
			self.error('Unable to send data: %s to client %s' % (str(e), clientId) )
			
	@doc_public
	def onClientIncomingData(self, clientAddress, data=None):
		"""
		"""

		try:
			ip, port = clientAddress
			id = self.clients[clientAddress]['id']
			# separator feature is disabled
			if data is not None: 
				# log event
				data_size = len(data)
				if self.logEventReceived:
					tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received(data=data, data_length=str(data_size), id=id), src_ip=ip, src_port=port )
				else:
					tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received(data_length=str(data_size), id=id), src_ip=ip, src_port=port )
				if self.logEventReceived:
					tpl.addRaw(raw=data)
					self.logRecvEvent( shortEvt = "client #%s data" % self.clients[clientAddress]['id'], tplEvt = tpl )
				
				# handle data
				self.handleIncomingData( clientAddress=clientAddress, data=data, lower=tpl )
			# separator feature is enabled, split the buffer by the separator
			else: 
				datas = self.clients[clientAddress]['buffer'].split(self.cfg['sep-in'])
				for data in datas[:-1]:
					pdu = data+self.cfg['sep-in']
					# log event
					pdu_size = len(data)
					if self.logEventReceived:
						tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received( data=pdu, data_length=str(pdu_size), id=id ), src_ip=ip, src_port=port )
					else:
						tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.received( data_length=str(pdu_size), id=id ), src_ip=ip, src_port=port )
					if self.logEventReceived:
						tpl.addRaw(raw=pdu)
						self.logRecvEvent( shortEvt = "client #%s data reassembled" % id, tplEvt = tpl )
					# handle data
					self.handleIncomingData( clientAddress=clientAddress, data=pdu, lower=tpl)
				self.clients[clientAddress]['buffer'] = datas[-1]
		except Exception as e:
			self.error( str(e) )

	def handleIncomingData(self, clientAddress, data, lower=None):
		"""
		Function to reimplement
		Called on incoming packet

		@param data: udp data received
		@type data: string
		
		@param lower: template udp data received
		@type lower: templatemessage
		"""
		pass
		
	def onStartListening(self):
		"""
		"""
		self.debug( 'on start listening called' )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.listening() )
		self.logRecvEvent( shortEvt = "listening", tplEvt = tpl )
		
	def onStopListening(self):
		"""
		"""
		self.debug( 'on stop listening called' )	
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.stopped() )
		self.logRecvEvent( shortEvt = "stopped", tplEvt = tpl )
		
	def onSocketError(self, e):
		"""
		"""
		self.error( "generic error: %s" % str(e) )
		
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.generic_error() )
		self.logRecvEvent( shortEvt = "error", tplEvt = tpl )
		
		# clean the socket
		self.cleanSocket()

	def onReset(self):
		"""
		Reset
		"""
		self.stopListening()
		
	def onStartListeningFailed(self, e):
		"""
		"""
		self.debug( e )
		# log event
		tpl = self.encapsule( ip_event=AdapterIP.received(), udp_event=templates.listening_failed() )
		self.logRecvEvent( shortEvt = "listening failed", tplEvt = tpl )

	def getExpectedTemplate(self, tpl, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
		"""
		Return an expected template with ip and udp layers
		"""
		# prepare layers
		defaultVer = self.cfg['sock-family']
		if versionIp is not None:
			defaultVer = versionIp
		layer_ip = AdapterIP.ip( source=sourceIp, destination=destinationIp, version=defaultVer ) 		
		layer_udp = templates.udp(source=sourcePort, destination=destinationPort)
		layer_udp.addMore(more=tpl)
		
		# prepare template
		tpl = TestTemplatesLib.TemplateMessage()
		tpl.addLayer(layer=layer_ip)
		tpl.addLayer(layer=layer_udp)
		return tpl
		
	@doc_public
	def isListening(self, timeout=1.0):
		"""
		Wait to receive "listening" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.listening()
		expected = self.getExpectedTemplate(tpl=tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def isListeningFailed(self, timeout=1.0):
		"""
		Wait to receive "listening failed" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.listening_failed()
		expected = self.getExpectedTemplate(tpl=tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt
		
	@doc_public
	def isStopped(self, timeout=1.0):
		"""
		Wait to receive "stopped" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		

		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.stopped()
		expected = self.getExpectedTemplate(tpl=tpl)
		
		# try to match the template 
		evt = self.received( expected=expected, timeout=timeout )
		return evt

	@doc_public
	def hasClientData(self, timeout=1.0, clientId=None, data=None, versionIp=None, sourceIp=None, destinationIp=None, 
													sourcePort=None, destinationPort=None):
		"""
		Waits to receive "data" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	

		@param data: data expected
		@type data:	string/operators	
	
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
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		tpl = templates.received(data=data, id=clientId)
		expected = self.getExpectedTemplate(tpl=tpl, versionIp=versionIp, sourceIp=sourceIp, destinationIp=destinationIp, 
																				sourcePort=sourcePort, destinationPort=destinationPort)
		
		# try to match the template 			
		evt = self.received( expected = expected, timeout = timeout )
		return evt