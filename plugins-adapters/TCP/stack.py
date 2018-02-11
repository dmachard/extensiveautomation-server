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

import codec
import sniffer as SnifferTCP
import templates

import random

__NAME__ = """TCP STACK"""

CONNECTION_PASSIVE    = "passive" 
CONNECTION_ACTIVE     = "active"

STATE_CLOSED           = "CLOSED"
STATE_LISTEN           = "LISTEN"
STATE_SYN_SENT         = "SYN-SENT"
STATE_ESTABLISHED      = "ESTABLISHED"
STATE_SYN_RECEIVED     = "SYN-RECEIVED"
STATE_FIN_WAIT_1       = "FIN-WAIT-1"
STATE_FIN_WAIT_2       = "FIN-WAIT-2"
STATE_CLOSE_WAIT       = "CLOSE-WAIT"
STATE_CLOSING          = "CLOSING"
STATE_LAST_ACK         = "LAST-ACK"
STATE_TIME_WAIT        = "TIME-WAIT"

# 3.9.  Event Processing
# The events are the user calls, OPEN, SEND, RECEIVE, CLOSE, ABORT, and STATUS
# Events that occur:
#      User Calls: OPEN, SEND, RECEIVE, CLOSE, ABORT, STATUS
#      Arriving Segments: SEGMENT ARRIVES
#      Timeouts: USER TIMEOUT, RETRANSMISSION TIMEOUT, TIME-WAIT TIMEOUT

AGENT_TYPE_EXPECTED='socket'

class Stack(TestAdapterLib.Adapter):
	def __init__ (self, parent,  bindInterface, debug=False, name=None,
										logEventSent=True, logEventReceived=True, agentSupport=False, agent=None, shared=False ):
		"""
		@param parent: testcase 
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		# check agent
		if agentSupport and agent is None:
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent cannot be undefined!" )
			
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		
		# init adapter
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name,
																		shared=shared, agentSupport=agentSupport, agent=agent)
		self.parent = parent
		self.debugMode = debug
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.agentSupport = agentSupport
		self.agent = agent
		
		self.cfg = {}
		self.cfg['bind-eth'] = bindInterface
		self.cfg['agent-support'] = agentSupport
		if agentSupport:
			self.cfg['agent-name'] = agent['name']
		
		self.__tcbMngr = TcbManager(parent=self)
		self.__checkConfig()
		
	def __checkConfig(self):
		"""
		private function
		"""
		self.debug("config: %s" % self.cfg)

	def tcbs(self):
		"""
		"""
		return self.__tcbMngr
		
	def onReset(self):
		"""
		Reset
		"""
		for tcb in self.__tcbMngr.getAll():
			tcb.sniffer().stopListening()
			
	def OPEN(self, localPort, remotePort=None, mode=CONNECTION_PASSIVE, precedence=0, timeout=1.0):
		"""
		passive = wait incoming connection
		active = make outgoing connection
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# create TCB
		tcb = TransmissionControlBlock( parent=self, testcase=self.parent, debug=self.debugMode,
																	  connType=mode, localPort=localPort, remotePort=remotePort,
																	  precedence=precedence, agentSupport=self.agentSupport, agent=self.agent )
		# check if not already exist
		if self.__tcbMngr.searchBy( localname=tcb.localName() ):
			raise Exception( 'connection already exists' )
		self.__tcbMngr.add( tcb=tcb )
		
		# start to sniff
		tcb.sniffer().startListening( eth=self.cfg['bind-eth'], srcIp=tcb.localIp() )
		if not tcb.sniffer().isSniffing( timeout=timeout):
			raise Exception( 'not listening' )	
			
		if mode == CONNECTION_PASSIVE:
			# enter LISTEN state
			tcb.setListenState()
		elif mode == CONNECTION_ACTIVE:
			if remotePort is None:
				raise Exception( 'foreign socket unspecified' )
			else:
				tcb.sendInitialSYN()
				# enter SYN-SENT state
				tcb.setSynSentState()
		else:
			raise Exception( 'mode %s not supported' % mode )	
			
		return tcb.getId()
		
	def SEND(self, connId):
		"""
		"""
		try:
			tcb = self.__tcpMngr.getBy( id=connId )
		except Exception as e: 
			self.error('connection %s does not exist' % connId)
		else:
			pass

	def CLOSE(self, connId):
		"""
		
		"""
		try:
			tcb = self.__tcbMngr.getBy( id=connId )
		except Exception as e: 
			self.error('connection %s does not exist' % connId)
		else:
			# go to the closed state
			if tcb.isPassive() and tcb.getState() in [ STATE_LISTEN ]:
				# enter CLOSED state and delete TCB
				tcb.setClosedState()
				tcb.onDelete()
			else:
				# go to the closed state
				if tcb.getState() in [ STATE_LISTEN ]:
					# enter CLOSED state and delete TCB
					tcb.setClosedState()
					tcb.onDelete()
				elif tcb.getState() in [ STATE_SYN_SENT ]:
					tcb.onDelete()
				elif tcb.getState() in [ STATE_SYN_RECEIVED ]:
					tcb.sendFIN()
					tcb.setFinWait1State()
				elif tcb.getState() in [ STATE_ESTABLISHED ]:
					tcb.sendFIN()
					tcb.setFinWait1State()
				elif tcb.getState() in [ STATE_CLOSE_WAIT ]:
					tcb.sendFIN()
					tcb.setClosedState()
				else:
					self.error( 'close: not yet implemented in this state' )	
					
	def ABORT(self):
		"""
		"""
		try:
			tcb = self.__tcbMngr.getBy( id=connId )
		except Exception as e: 
			self.error('connection %s does not exist' % connId)
		else:
			if tcb.getState() in [ STATE_LISTEN ]:
				# enter CLOSED state and delete TCB
				tcb.setClosedState()
				tcb.onDelete()
			elif tcb.getState() in [ STATE_SYN_SENT ]:
				# enter CLOSED state and delete TCB
				tcb.setClosedState()
				tcb.onDelete()
			elif tcb.getState() in [ STATE_CLOSE_WAIT ]:	
				tcb.sendRST()
				tcb.setClosedState(seq=tcb.SND_NXT, ack=tcb.SND_UNA)
				tcb.onDelete()
			elif tcb.getState() in [ STATE_TIME_WAIT ]:
				# enter CLOSED state and delete TCB
				tcb.setClosedState()
				tcb.onDelete()
			else:
				self.error( 'abort: not yet implemented in this state' )	
					
	def STATUS(self, connId):
		"""
		"""
		try:
			tcb = self.__tcpMngr.getBy( id=connId )
		except Exception as e: 
			self.error('connection %s does not exist' % connId)
		else:
			return tcb.getStatus()

class TcbManager(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.__tcp =  {}
		self.__id = 0
	
	def getAll(self):
		"""
		"""	
		return self.__tcp.values()
		
	def add(self, tcb):
		"""
		"""
		self.__id += 1
		tcb.setId(id=self.__id)
		self.__tcp[tcb.getId()] = tcb
		
	def getBy(self, id):
		"""
		"""
		return self.__tcp[id]
		
	def delete(self, id):
		"""
		"""
		del self.__tcp[id]
		
	def searchBy(self, localname):
		"""
		"""
		found=False
		for tcb in self.__tcp.values():
				if tcb.localName() == localname:
					found = True
					break
		return found
		
#
# 3.2.  Terminology
#                              +---------+ ---------\      active OPEN  
#                              |  CLOSED |            \    -----------  
#                              +---------+<---------\   \   create TCB  
#                                |     ^              \   \  snd SYN    
#                   passive OPEN |     |   CLOSE        \   \           
#                   ------------ |     | ----------       \   \         
#                    create TCB  |     | delete TCB         \   \       
#                                V     |                      \   \     
#                              +---------+            CLOSE    |    \   
#                              |  LISTEN |          ---------- |     |  
#                              +---------+          delete TCB |     |  
#                   rcv SYN      |     |     SEND              |     |  
#                  -----------   |     |    -------            |     V  
# +---------+      snd SYN,ACK  /       \   snd SYN          +---------+
# |         |<-----------------           ------------------>|         |
# |   SYN   |                    rcv SYN                     |   SYN   |
# |   RCVD  |<-----------------------------------------------|   SENT  |
# |         |                    snd ACK                     |         |
# |         |------------------           -------------------|         |
# +---------+   rcv ACK of SYN  \       /  rcv SYN,ACK       +---------+
#   |           --------------   |     |   -----------                  
#   |                  x         |     |     snd ACK                    
#   |                            V     V                                
#   |  CLOSE                   +---------+                              
#   | -------                  |  ESTAB  |                              
#   | snd FIN                  +---------+                              
#   |                   CLOSE    |     |    rcv FIN                     
#   V                  -------   |     |    -------                     
# +---------+          snd FIN  /       \   snd ACK          +---------+
# |  FIN    |<-----------------           ------------------>|  CLOSE  |
# | WAIT-1  |------------------                              |   WAIT  |
# +---------+          rcv FIN  \                            +---------+
#   | rcv ACK of FIN   -------   |                            CLOSE  |  
#   | --------------   snd ACK   |                           ------- |  
#   V        x                   V                           snd FIN V  
# +---------+                  +---------+                   +---------+
# |FINWAIT-2|                  | CLOSING |                   | LAST-ACK|
# +---------+                  +---------+                   +---------+
#   |                rcv ACK of FIN |                 rcv ACK of FIN |  
#   |  rcv FIN       -------------- |    Timeout=2MSL -------------- |  
#   |  -------              x       V    ------------        x       V  
#    \ snd ACK                 +---------+delete TCB         +---------+
#     ------------------------>|TIME WAIT|------------------>| CLOSED  |
#                              +---------+                   +---------+
#
class TransmissionControlBlock(object):
	def __init__(self, parent, testcase, debug, connType, localPort, remotePort=None,
										windowSize=8000, urgentPointer=0, precedence=0, ipVersion=4, agentSupport=False, agent=None	):
		"""
		transmission control block (TCB) to hold connection state information
		"""
		self.parent = parent
		self.testcase = testcase
		
		# sockets
		self.conn_type = connType
		self.local_socket = localPort # tuple ip, port
		self.foreign_socket = remotePort # tuple ip, port
		
		# Send Sequence Variables
		self.SND_UNA = 0 # send unacknowledged
		self.SND_NXT = None # send next
		self.SND_WND = windowSize # send window
		self.SND_UP  = urgentPointer # send urgent pointer
		self.SND_WL1 = None # segment sequence number used for last window update
		self.SND_WL2 = None # segment acknowledgment number used for last window update
		self.ISS     = None # initial send sequence number

		#	Receive Sequence Variables
		self.RCV_NXT = None # receive next
		self.RCV_WND = None # receive window
		self.RCV_UP  = None # receive urgent pointer
		self.IRS     = None # initial receive sequence number
		
		self.PRC = precedence
		self.ipVersion = ipVersion
		
		self.__id = None
		self.__tcpSniffer = SnifferTCP.Sniffer(parent=testcase, debug=False, logEventSent=True, logEventReceived=True,
																		ipVersion=ipVersion, port2sniff=self.localPort(), separatorIn='0x00', separatorOut='0x00', 
																		separatorDisabled=True, inactivityTimeout=0.0, parentName=__NAME__
																		, agentSupport=agentSupport, agent=agent)
		self.__tcpSniffer.handleIncomingData = self.onReceiving
		self.__tcpState = TestAdapterLib.State(parent=parent, name='CONNECTION_STATE', initial=STATE_CLOSED)
	
		self.__timer2MSL = TestAdapterLib.Timer(parent=parent, duration=2, name='Timer 2 MSL', callback=self.__on2MSLTimeout)
		self.__timerwait = TestAdapterLib.Timer(parent=parent, duration=2, name='Timer wait', callback=self.__onWaitTimeout)
																			
	def localIp(self):
		"""
		"""
		return str(self.local_socket[0])
		
	def localPort(self):
		"""
		"""
		return int(self.local_socket[1])

	def remoteIp(self):
		"""
		"""
		return str(self.foreign_socket[0])
		
	def remotePort(self):
		"""
		"""
		return int(self.foreign_socket[1])
		
	def debug(self, txt):
		"""
		"""
		self.parent.debug("[CONN %s][%s]: %s" % ( self.getId(), self.getState(), txt) )
		
	def warning(self, txt):
		"""
		"""
		self.parent.warning("[CONN %s][%s]: %s" % ( self.getId(), self.getState(),txt) )
		
	def error(self, txt):
		"""
		"""
		self.parent.error("[CONN %s][%s]: %s" % ( self.getId(), self.getState(),txt) )
		
	def getId(self):
		"""
		"""
		return self.__id
	def setId(self, id):
		"""
		"""
		self.__id = id
	def getStatus(self):
		"""
		"""
		pass
	def getState(self):
		"""
		"""
		return self.__tcpState.get()
		
	def setState(self, state):
		"""
		"""
		self.__tcpState.set(state)

	def sniffer(self):
		"""
		"""
		return self.__tcpSniffer
	def setClosedState(self):
		"""
		CLOSED - represents no connection state at all.
		"""
		# Initial state CLOSED is fictional because it represents the state when there is no TCB,
		# and therefore, no connection.
		self.setState(state=STATE_CLOSED)
		
	def setClosingState(self):
		"""
		CLOSING - represents waiting for a connection termination request acknowledgment from the remote TCP.
		"""
		self.setState(state=STATE_CLOSING)		
		
	def setListenState(self):
		"""
		LISTEN - represents waiting for a connection request from any remote TCP and port.
		"""
		self.setState(state=STATE_LISTEN)		
	
	def setSynSentState(self):
		"""
		SYN-SENT - represents waiting for a matching connection request after having sent a connection request.
		"""
		self.setState(state=STATE_SYN_SENT)		

	def setEstablishedState(self):
		"""
		ESTABLISHED - represents an open connection, data received can be delivered to the user.  
		The normal state for the data transfer phase of the connection.
		"""
		self.setState(state=STATE_ESTABLISHED)		

	def setSynReceivedState(self):
		"""
		SYN-RECEIVED - represents waiting for a confirming connection request acknowledgment after having 
		both received and sent a connection request
		"""
		self.setState(state=STATE_SYN_RECEIVED)		
		
	def setCloseWaitState(self):
		"""
		CLOSE-WAIT - represents waiting for a connection termination request from the local user.
		"""
		self.setState(state=STATE_CLOSE_WAIT)		

	def setTimeWaitState(self):
		"""
		TIME-WAIT - represents waiting for enough time to pass to be sure
		the remote TCP received the acknowledgment of its connection termination request.
		"""
		self.setState(state=STATE_TIME_WAIT)

	def setFinWait1State(self):
		"""
		FIN-WAIT-1 - represents waiting for a connection termination request from the remote TCP,
		or an acknowledgment of the connection termination request previously sent.
		"""
		self.setState(state=STATE_FIN_WAIT_1)
		
	def setFinWait2State(self):
		"""
		FIN-WAIT-2 - represents waiting for a connection termination request from the remote TCP.
		"""
		self.setState(state=STATE_FIN_WAIT_2)
	
	def setLastAckState(self):
		"""
		LAST-ACK - represents waiting for an acknowledgment of the connection termination request 
		previously sent to the remote TCP (which includes an acknowledgment 
		of its connection termination request).
		"""
		self.setState(state=STATE_LAST_ACK)
		
	def localName(self):
		"""
		"""
		# the localname is defined by the <local socket, foreign socket> pair.
		return ( self.local_socket, self.foreign_socket )	
	
	def getMode(self):
		"""
		"""
		return self.conn_type
	
	def isPassive(self):
		"""
		"""
		if self.conn_type == CONNECTION_PASSIVE:
			return True
		else:
			return False

	def isActive(self):
		"""
		"""
		if self.conn_type == CONNECTION_ACTIVE:
			return True
		else:
			return False
	def sendInitialSYN(self):
		"""
		"""
		# An initial send sequence number (ISS) is selected
		self.ISS = random.randrange(0, 4294967295) # 32 bits

		# send A SYN segment of the form <SEQ=ISS><CTL=SYN>.
		self.sniffer().SYN( destPort=self.remotePort(), srcPort=self.localPort(), destIp=self.remoteIp(), destMac=None,
											  seqNum=self.ISS, ackNum=self.SND_UNA, tcpWin=self.SND_WND, urgPtr=self.SND_UP, checksum=None,
											  options=None, optSegMax=None, optWinScale=None, optSackPermitted=None, optSack=None)
		
		# Set SND.UNA to ISS, SND.NXT to ISS+1
		self.SND_UNA = self.ISS 
		self.SND_NXT = self.ISS + 1
	
	def sendRST(self, seq, ack):
		"""
		"""
		# send a RST
		self.sniffer().RST( destPort=self.remotePort(), srcPort=self.localPort(), destIp=self.remoteIp(), destMac=None, 
														seqNum=seq, ackNum=ack, tcpWin=self.SND_WND, urgPtr=self.SND_UP,
														checksum=None, options=None)
												
	def sendRST_ACK(self, seq, ack):
		"""
		"""
		# send a RST + ACK
		self.sniffer().RST_ACK( destPort=self.remotePort(), srcPort=self.localPort(), destIp=self.remoteIp(), destMac=None, 
														seqNum=seq, ackNum=ack, tcpWin=self.SND_WND, urgPtr=self.SND_UP,
														checksum=None, options=None)
	def sendACK(self, seq, ack):
		"""
		"""
		# send a ACK
		self.sniffer().ACK( destPort=self.remotePort(), srcPort=self.localPort(), destIp=self.remoteIp(), destMac=None, 
												seqNum=seq, ackNum=ack, tcpWin=self.SND_WND, urgPtr=self.SND_UP,
												checksum=None, options=None)

	def sendFIN(self):
		"""
		"""
		# send a FIN
		self.sniffer().FIN( destPort=self.remotePort(), srcPort=self.localPort(), destIp=self.remoteIp(), destMac=None, 
												seqNum=self.SND_NXT, ackNum=self.RCV_NXT, tcpWin=self.SND_WND, urgPtr=self.SND_UP,
												checksum=None, options=None)


	def sendSYN_ACK(self, seq, ack):
		"""
		"""
		# send a SYN + ACK
		self.sniffer().SYN_ACK( destPort=self.remotePort(), srcPort=self.localPort(), destIp=self.remoteIp(), destMac=None,
											  seqNum=seq, ackNum=ack, tcpWin=self.SND_WND, urgPtr=self.SND_UP, checksum=None,
											  options=None, optSegMax=None, optWinScale=None, optSackPermitted=None, optSack=None)

	def onDelete(self, timeout=1.0):
		"""
		"""
		self.sniffer().stopListening()
		if not self.sniffer().isStopped( timeout=timeout):
			self.warning( 'unable to stop properly' )	
			
		self.parent.tcbs().delete( id=self.getId() )
		
	def __on2MSLTimeout(self):
		"""
		"""
		pass
		
	def __onWaitTimeout(self):
		"""
		"""
		pass
		
	def onReceiving(self, data, lower, fromAddr, toAddr):
		"""
		SEGMENT ARRIVES
		"""
		# extract some important tcp info
		ctrl_bits = lower.get('TCP', 'control-bits')
		ack = lower.getInt('TCP', 'acknowledgment-number')
		seq = lower.getInt('TCP', 'sequence-number')
		win = lower.get('TCP', 'window').getInt('integer')
		data_len = lower.get('TCP', 'data').getInt('length')
		# tos
		if self.ipVersion == 4:
			tos = lower.get('IP4', 'type-service')
		if self.ipVersion == 6:
			tos = lower.get('IP6', 'type-service')
		prc = int( tos.get('precedence').getName() )
		
		# dispatch the packet	
		if self.getState() in [ STATE_CLOSED ]:
			self.onClosedState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq)
		elif self.getState() in [ STATE_LISTEN ]:
			self.onListenState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_SYN_SENT ]:
			self.onSynSentState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_SYN_RECEIVED ]:
			self.onSynReceivedState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)	
		elif self.getState() in [ STATE_CLOSE_WAIT ]:
			self.onCloseWaitState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_TIME_WAIT ]:
			self.onTimeWaitState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_ESTABLISHED ]:
			self.onEstablishedState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_LAST_ACK ]:
			self.onLastAckState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_FIN_WAIT_1 ]:
			self.onFinWait1State(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)			
		elif self.getState() in [ STATE_FIN_WAIT_2 ]:
			self.onFinWait2State(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		elif self.getState() in [ STATE_CLOSING ]:
			self.onClosingState(fromaddr=fromAddr, segment=lower, ctrl_bits=ctrl_bits, seg_ack=ack, seg_seq=seq, seg_win=win, seg_prc=prc, seg_len=data_len)
		else:
			self.error( 'unknown state %s' % self.getState() )
			
	def onClosedState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		all data in the incoming segment is discarded
		"""
		if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
			self.debug( 'An incoming segment containing a RST is discarded.' )
		else:
			#  An incoming segment not containing a RST causes a RST to be sent in response.
			if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
				self.sendRST_ACK( seq=0, ack=seg_seq + seg_len )
			else:
				self.sendRST( seq=seg_seq, ack=self.SND_UNA )
				
	def onListenState(self, fromaddr,segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		self.foreign_socket = fromaddr
		# first check for an RST
		if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
			self.debug('An incoming RST should be ignored')
			return
			
		# second check for an ACK
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			# The RST should be formatted as follows: <SEQ=SEG.ACK><CTL=RST>
			self.sendRST(seq=seg_ack, ack=self.SND_UNA)
			return
		
		# third check for a SYN
		if seg_prc <= self.PRC:
			self.debug( 'prc ok, continue')
		
		# An initial send sequence number (ISS) is selected
		self.ISS = random.randrange(0, 4294967295) # 32 bits
		
		self.RCV_NXT  = seg_seq + 1
		self.IRS = seg_seq
	
		# sent of the form: <SEQ=ISS><ACK=RCV.NXT><CTL=SYN,ACK>
		self.sendSYN_ACK( seq=self.ISS, ack=self.RCV_NXT )		
		
		self.SND_NXT = self.ISS+1 
		self.SND_UNA = self.ISS
		
		# The connection state should be changed to SYN-RECEIVED.
		self.setSynReceivedState()
			
		# fourth other text or control
		# todo, not yet implemented

	def onSynSentState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		syn_received = False
		ack_received = False
		rst_received = False
		ack_acceptable = False
		# first check the ACK bit
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			ack_received = True
			# send a reset, unless the RST bit is set
			if seg_ack <= self.ISS or seg_ack > self.SND_NXT:
				if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
					self.warning( 'ack not acceptable, reset segment dropped' )
					return
				self.warning( 'ack not acceptable, reset and discard the segment' )
				self.sendRST(seq=seg_ack, ack=self.SND_UNA)
				return
			
			if self.SND_UNA <= seg_ack and seg_ack <= self.SND_NXT:
				self.debug( 'ack acceptable, continue' )
				ack_acceptable = True
				
		# second check the RST bit
		if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
			rst_received = True
			if ack_acceptable:
				# signal the user "error: connection reset"
				tpl = templates.connection_reset()
				self.logRecvEvent( shortEvt = 'connection reset', tplEvt = tpl ) 
		
				# enter CLOSED state and delete TCB
				self.setClosedState()
				self.onDelete()
				return
			else:
				self.warning( 'no ack, segment dropped' )	
				return

		# third check the security and precedence
		# todo, not yet implemented
		
		# fourth check the SYN bit
		# This step should be reached only if the ACK is ok, or there is  no ACK, and it the segment did not contain a RST.
		if ack_acceptable or  ( not ack_received and not rst_received ):
			if codec.CTRL_BITS_SYN in ctrl_bits.get('string'):
				syn_received = True
				self.RCV_NXT = seg_seq + 1
				self.IRS = seg_seq
				
				# SND.UNA should be advanced to equal SEG.ACK (if there  is an ACK)
				if ack_received:
					self.SND_UNA = seg_ack
				
				# SYN has been ACKed, change the connection state to ESTABLISHED
				# form an ACK segment <SEQ=SND.NXT><ACK=RCV.NXT><CTL=ACK> and send it
				if self.SND_UNA > self.ISS:
					self.setEstablishedState()
					self.sendACK( seq=self.SND_NXT, ack=self.RCV_NXT )
					return
				#  Otherwise enter SYN-RECEIVED, form a SYN,ACK segment <SEQ=ISS><ACK=RCV.NXT><CTL=SYN,ACK> and send it
				else:
					self.setSynReceivedState()
					self.sendSYN_ACK( seq=self.ISS, ack=self.RCV_NXT )
					return
					
		# fifth, if neither of the SYN or RST bits is set then drop the segment and return.
		if not syn_received or not rst_received:
			self.warning( 'segment dropped' )
	
	# other states
	def onSynReceivedState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# second check the RST bit
		if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
			if self.isPassive():
				self.setListenState()
				return
				
				# signal the user "connection refused"
				tpl = templates.connection_refused()
				self.logRecvEvent( shortEvt = 'connection refused', tplEvt = tpl ) 
				
				# enter CLOSED state and delete TCB
				self.setClosedState()
				self.onDelete()
		
		# third check security and precedence
		# todo, not yet implemented
		
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return
		
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			if self.SND_UNA <= seg_ack and  seg_ack <= self.SND_NXT:
				self.setEstablishedState()
				
	def onCloseWaitState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# second check the RST bit
		if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
			# signal the user "connection rest"
			tpl = templates.connection_reset()
			self.logRecvEvent( shortEvt = 'connection reset', tplEvt = tpl ) 
			
			# enter CLOSED state and delete TCB
			self.setClosedState()
			self.onDelete()
		
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return

		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			if self.SND_UNA < seg_ack and seg_ack <= self.SND_NXT:
				self.SND_UNA = seg_ack
		
			if seg_ack < self.SND_UNA:
				self.warning('this ACK is a duplicate, it can be ignored') 	
			
			if seg_ack > self.SND_NXT:
				self.warning('this ACK acks something not yet sent, drop the segment')
				self.sendACK( seq=self.SND_NXT, ack=self.RCV_NXT )
				return
			
			# the send window should be  updated. 
			if self.SND_UNA < seg_ack and seg_ack <= self.SND_NXT:
				if self.SND_WL1 < seg_seq or ( self.SND_WL1 == seg_seq and self.SND_WL2 <= seg_ack):
					self.SND_WND = seg_win
					self.SND_WL1 = seg_seq
					self.SND_WL2 = seg_ack
		
		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.debug('Remain in the CLOSE-WAIT state.')		
			
	def onTimeWaitState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# second check the RST bit
		if codec.CTRL_BITS_RST in ctrl_bits.get('string'):
			# enter CLOSED state and delete TCB
			self.setClosedState()
			self.onDelete()
		
		# fourth, check the SYN bit
		# todo, not yet implemented
		
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return
		
		# The only thing that can arrive in this state is a retransmission of the remote FIN.
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.sendACK( seq=self.SND_NXT, ack=self.RCV_NXT )
#			self.__timer2MSL.restart()
		
		# sixth, check the URG bit,
		# todo, not yet implemented
		
		# seventh, process the segment text
		# todo, not yet implemented
		
		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.debug('Remain in the TIME-WAIT state.')
#			self.__timer2MSL.restart()
			
	def onClosingState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return
		
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string') and  codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.setTimeWaitState()
		else:
			self.warning( 'ignore the segment' )
		
		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.debug('Remain in the CLOSING state.')
			
	def onFinWait1State(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return

		if codec.CTRL_BITS_ACK in ctrl_bits.get('string') and codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.setFinWait2State()
			self.onFinWait2State(fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len)
			return

		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.sendACK( seq=self.SND_NXT, ack=self.RCV_NXT )
			self.setClosingState()
				
	def onFinWait2State(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return
			
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.sendACK( seq=seg_ack, ack=seg_seq+1 )
			
		# sixth, check the URG bit,
		# todo, not yet implemented
		
		# seventh, process the segment text
		# todo, not yet implemented
		
		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.setTimeWaitState()
#			self.__timerwait.start()
#			self.__timer2MSL.stop()
				
	def onLastAckState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return
		
		# The only thing that can arrive in this state is an acknowledgment of our FIN
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			# enter CLOSED state and delete TCB
			self.setClosedState()
			self.onDelete()
		
		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.debug('Remain in the LAST-ACK state.')
			
	def onEstablishedState(self, fromaddr, segment, ctrl_bits, seg_ack, seg_seq, seg_win, seg_prc, seg_len):
		"""
		"""
		# third check security and precedence
		# todo, not yet implemented
		
		# fifth check the ACK field
		if not codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			self.warning('ACK bit is off drop the segment')
			return
	
		if codec.CTRL_BITS_ACK in ctrl_bits.get('string'):
			if self.SND_UNA < seg_ack and seg_ack <= self.SND_NXT:
				self.SND_UNA = seg_ack
		
			if seg_ack < self.SND_UNA:
				self.warning('this ACK is a duplicate, it can be ignored') 	
			
			if seg_ack > self.SND_NXT:
				self.warning('this ACK acks something not yet sent, drop the segment')
				self.sendACK( seq=self.SND_NXT, ack=self.RCV_NXT )
				return
			
			# the send window should be  updated. 
			if self.SND_UNA < seg_ack and seg_ack <= self.SND_NXT:
				if self.SND_WL1 < seg_seq or ( self.SND_WL1 == seg_seq and self.SND_WL2 <= seg_ack):
					self.SND_WND = seg_win
					self.SND_WL1 = seg_seq
					self.SND_WL2 = seg_ack
					
		# eighth, check the FIN bit
		if codec.CTRL_BITS_FIN in ctrl_bits.get('string'):
			self.setCloseWaitState()
		
		if codec.CTRL_BITS_PSH in ctrl_bits.get('string'):
			self.sendACK( seq=self.SND_NXT, ack=seg_ack+1 )