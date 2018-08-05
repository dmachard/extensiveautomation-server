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
import sys

# Two operations are defined: CONNECT and BIND.
#		+----+----+----+----+----+----+----+----+----+----+....+----+
#		| VN | CD | DSTPORT |      DSTIP        | USERID       |NULL|
#		+----+----+----+----+----+----+----+----+----+----+....+----+
# # of bytes:	   1    1      2              4           variable       1

import struct

try:
	import templates
except ImportError: # python3 support
	from . import templates
	
# VN = Version
# CD = Command
# DSTPORT = Destination port
# DSTIP = Destination IP
# USERID = User ID

VN = 4
CD_CONNECT = 1
CD_BIND = 2

class Codec(object):
	def __init__(self, parent, testcase, debug):
		"""
		http://www.openssh.com/txt/socks4.protocol
		
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.error = parent.error
		self.info = parent.info
		
	def encode(self, socks_tpl):
		"""
		"""
		self.debug( 'encode sock' )
		
		summary = 'connect'
		
		vn = socks_tpl.get('version')
		cd = socks_tpl.get('command')
		if cd == 'connect':
			cd = CD_CONNECT
		dstport = socks_tpl.get('remote-port')
		dstip = socks_tpl.get('remote-ip')
		userid = socks_tpl.get('user-id')
		self.debug( 'template read' )
		
		args = []
		args.append( int(vn) )
		args.append( int(cd) )

		req = [ struct.pack('BB', *args ) ]
		req.append( struct.pack('>H', int(dstport) ) )
		ipstr = TestValidatorsLib.IPv4Address(separator='.').toList(ip=dstip)

		req.append( struct.pack('4B', *ipstr) )
		req.append( userid )
		req.append( '\x00' )

		return ( ''.join( req ), summary )
		
	def decode(self, sock):
		"""
		"""
		self.debug( 'decode sock rsp: %s' % sock )
		tpl = None
		summary = 'response'		
		try:
			sock_rsp = struct.unpack('!2BH4B', sock)
			
			# CD is the result code with one of the following values:
			CD = str(sock_rsp[1])

			#		90: request granted
			#		91: request rejected or failed
			#		92: request rejected becasue SOCKS server cannot connect to
			#		    identd on the client
			#		93: request rejected because the client program and identd
			#		    report different user-ids.
			if sock_rsp[1] == 90:
				summary = 'granted'
			if sock_rsp[1] == 91:
				summary = 'rejected'
			
			# VN is the version of the reply code and should be 0
			VN = str(sock_rsp[0])
			
			tpl = templates.socks(version=VN, 
														result=CD, 
														remotePort=str(sock_rsp[2]), 
														remoteAddress='.'.join(map(str,sock_rsp[3:])),
														more=templates.received()
														)
		except Exception as e:
			self.error('unable to decode sock4 response: %s' % e)
		return (tpl, summary)