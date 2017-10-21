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
import sys

import templates
import struct

import TestExecutorLib.TestTemplatesLib as TestTemplatesLib

SE                  = 240    #End of subnegotiation parameters.
NOP                 = 241    #No operation.
DataMark           = 242    #The data stream portion of a Synch. This should always be accompanied by a TCP Urgent notification.
Break               = 243    #NVT character BRK.
InterruptProcess   = 244    #The function IP.
AbortOutput        = 245    #The function AO.
AreYouThere       = 246    #The function AYT.
EraseCharacter     = 247    #The function EC.
EraseLine          = 248    #The function EL.
GoAhead            = 249    #The GA signal.
SB                  = 250    #Indicates that what follows is subnegotiation of the indicated option.
WILL                = 251    #Indicates the desire to begin performing, or confirmation that you are now performing, the indicated option.
WONT                = 252    #Indicates the refusal to perform, or continue performing, the  indicated option.
DO                  = 253    #Indicates the request that the other party perform, or  confirmation that you are expecting the other party to perform, the indicated option.
DONT                = 254    #Indicates the demand that the other party stop performing, or confirmation that you are no longer expecting the other party to perform, the indicated option.
IAC                 = 255    #Interpret as Command Data Byte 255.

TELNET_COMMANDS = {
	SE : 'SE',
	NOP : 'NOP',
	DataMark : 'DataMark',
	Break : 'Break',
	InterruptProcess : 'InterruptProcess',
	AbortOutput : 'AbortOutput',
	AreYouThere : 'AreYouThere',
	EraseCharacter : 'EraseCharacter',
	EraseLine : 'EraseLine',
	GoAhead : 'GoAhead',
	SB : 'SB',
	WILL : 'WILL',
	WONT : 'WONT',
	DO : 'DO',
	DONT : 'DONT',
	IAC : 'IAC'
}

BIN = 0 	#Binary Transmission
ECHO = 1 	#Echo
RECON = 2 	#Reconnection
SUPP = 3 	#Suppress Go Ahead
APSN = 4 	#Approx Message Size Negotiation
STATUS = 5 	#Status
TIMING = 6 	#Timing Mark
RCTE = 7 	#Remote Controlled Trans and Echo
OLW = 8 	#Output Line Width
OPS = 9 	#Output Page Size
OCRD = 10 	#Output Carriage-Return Disposition
OHTS = 11 	#Output Horizontal Tab Stops
OHTD = 12 	#Output Horizontal Tab Disposition
OFD = 13 	#Output Formfeed Disposition
OVT = 14 	#Output Vertical Tabstops
OVTD = 15 	#Output Vertical Tab Disposition
OLD = 16 	#Output Linefeed Disposition
EASCII = 17 	#Extended ASCII
LOGOUT = 18 	#Logout
ByeMacro = 19 	#Byte Macro
DET = 20 	#Data Entry Terminal
SUPDUP = 21 	#SUPDUP
SUPDUPOutput = 22 	#SUPDUP Output
SL = 23 	#Send Location
TermType = 24 	#Terminal Type
EOR = 25 	#End of Record
TUI = 26 	#TACACS User Identification
OM = 27 	#Output Marking
TLN = 28 	#Terminal Location Number
T3270R = 29 	#Telnet 3270 Regime
X3D = 30 	#X.3 PAD
NAWS = 31 	#Negotiate About Window Size
TS = 32 	#Terminal Speed
RFC = 33 	#Remote Flow Control
Linemode = 22 # 	Linemode
XDL = 35 	#X Display Location
EOL = 255 	#Extended-Options-List
NewEnv = 39

TELNET_OPTIONS = {
	TS: 'Terminal Speed',
	NewEnv: 'New Environment Option',
	BIN : 'Binary Transmission',
	ECHO : 'Echo',
	RECON : 'Reconnection',
	SUPP : 'Suppress Go Ahead',
	APSN : 'Approx Message Size Negotiation',
	STATUS : 'Status',
	TIMING : 'Timing Mark',
	RCTE : 'Remote Controlled Trans and Echo',
	OLW : 'Output Line Width',
	OPS : 'Output Page Size',
	OCRD : 'Output Carriage-Return Disposition',
	OHTS : 'Output Horizontal Tab Stops',
	OHTD : 'Output Horizontal Tab Disposition',
	OFD : 'Output Formfeed Disposition',
	OVT : 'Output Vertical Tabstops',
	OVTD : 'Output Vertical Tab Disposition',
	OLD : 'Output Linefeed Disposition',
	EASCII : 'Extended ASCII',
	LOGOUT : 'Logout',
	ByeMacro : 'Byte Macro',
	DET : 'Data Entry Terminal',
	SUPDUP : 'SUPDUP',
	SUPDUPOutput : 'SUPDUP Output',
	SL : 'Send Location',
	TermType : 'Terminal Type',
	EOR : 'End of Record',
	TUI : 'TACACS User Identification',
	OM : 'Output Marking',
	TLN : 'Terminal Location Number',
	T3270R : 'Telnet 3270 Regime',
	X3D : 'X.3 PAD',
	NAWS : 'Negotiate About Window Size',
	RFC : 'Remote Flow Control',
	Linemode : 'Linemode',
	XDL : 'X Display Location',
	EOL : 'Extended-Options-List',
}

class Codec(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.error = self.parent.error
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info	
		
	def encode(self, telnet_tpl):
		"""
		todo: impleted cmd
		"""
		summary = 'Data out ...'
		data = telnet_tpl.get('data')
		cmds = telnet_tpl.get('commands')
		subopts = telnet_tpl.get('suboptions')

		if data is None:
			data = ''
			
		# encode commands
		if cmds is not None:
			summary = 'Commands out ...'
			
			try:
				commands = []
				for command in cmds.getValues():
					cmd, opt = command.split(' ', 1)
					# convert string command to integer value
					finalCmd = 0
					for key, value in TELNET_COMMANDS.items():
						if cmd == value:
							finalCmd = key
							break
					# convert string options to integer value
					finalOtps = 0
					for key, value in TELNET_OPTIONS.items():
						if opt == value:
							finalOtps = key
							break			
					# final pack			
					commands.append( struct.pack('!BBB', IAC, finalCmd, finalOtps ) )
			except Exception as e:
				self.error( 'unable to pack options: %s' % e)
			else:	
				data = ''.join(commands)
		
		# encode commands options
		if subopts is not None:
			summary = 'Suboptions out ...'
			
			try:
				suboptions = []
				for subopt in subopts.getKeys():
					# pack begin
					suboptions.append( struct.pack('!BB', IAC, SB ) )
					
					# convert string command to integer value
					finalSubOpt = 0
					for key, value in TELNET_OPTIONS.items():
						if subopt == value:
							finalSubOpt = key
							break
					
					# pack command
					suboptions.append( struct.pack('!B', finalSubOpt ) )
					
					# encode sub value 
					sub_tpl = subopts.get(subopt)	
					for subopt in sub_tpl.getValues():
						if finalSubOpt == TermType:
							suboptions.append( struct.pack('!%ss' % len(subopt), subopt ) )
						else:
							suboptions.append( struct.pack('!H', subopt ) )
					
					# pack end
					suboptions.append( struct.pack('!BB',IAC, SE ) )
			except Exception as e:
				self.error( 'unable to pack subopts: %s' % e)
			else:
				data = ''.join(suboptions)
			
		return data, summary
		
	def decode(self, data):
		"""
		"""
		# create template
		#  The commands dealing with option negotiation are three byte sequences
		summary = 'Data in...'
		left_data = ''
		moredata = ''
		len_cmd = 3
		nb_cmd = 0
		tplCmd = TestTemplatesLib.TemplateLayer('')
		cmdList = []


		# FF FB 03 FF FD 03 FF FB 01
		cmdCountLen = 2
		for i in xrange(0,len(data)):
			# command  ?
			isCmd  = struct.unpack('!B', data[i])
			if isCmd[0] == IAC:
				cmdCountLen = 0				
				summary= 'Commands in...'
				cmds_str = ''
				
				if ( len(data[i:i+len_cmd]) % len_cmd ) != 0:
					left_data += data[i:] # insufficient data received
					moredata =  left_data
				else:				
					sep, cmd, code_opt = struct.unpack('!BBB', data[i:i+len_cmd])
					if cmd in TELNET_COMMANDS:
						cmds_str = '%s' % (TELNET_COMMANDS[cmd])
					if code_opt in TELNET_OPTIONS:
						cmds_str += ' %s' % (TELNET_OPTIONS[code_opt])
					cmdList.append( (cmd, code_opt) )
					tplCmd.addKey(name="%s" % nb_cmd, data=cmds_str)
					
					# incremente number of cmd detected
					nb_cmd += 1
					
					# if a data mark is detected, we can stop to decode commands
					if cmd == DataMark:
						left_data = data[i+len_cmd-1:]
						break					
			else:
				if cmdCountLen <= 1:
					cmdCountLen += 1
				else:
					left_data += data[i]
					
#		left_data = data[len_cmd*nb_cmd:]
		if not nb_cmd:
			tplCmd = None
			
		tpl = templates.dataIncoming(cmds=tplCmd, data=left_data) 
		return (tpl, summary, cmdList, moredata)