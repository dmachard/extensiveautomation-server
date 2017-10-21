#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

#       +----+-----+-------+------+----------+----------+
#        |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
#        +----+-----+-------+------+----------+----------+
#        | 1  |  1  | X'00' |  1   | Variable |    2     |
#        +----+-----+-------+------+----------+----------+

import struct
import templates

# VN = Version
# CD = Command
# DSTPORT = Destination port
# DSTIP = Destination IP
# USERID = User ID

VN = 5
CD_CONNECT = 1
CD_BIND = 2
CD_UDP = 3

class Codec(object):
	def __init__(self, parent, testcase, debug):
		"""
		https://www.ietf.org/rfc/rfc1928.txt
		
		@param parent:
		@type parent:		
		"""
		self.warning = parent.warning
		self.debug = parent.debug
		self.error = parent.error
		self.info = parent.info
	
	def encodenego(self, socks_tpl):
		"""
		"""
		self.debug( 'encode sock nego' )
		
		summary = 'negociation'
		
		vn = socks_tpl.get('version')
		methods = socks_tpl.get('methods')
		nmethods = socks_tpl.get('number-methods')
	
		args = []
		args.append( int(vn) )
		args.append( int(nmethods) )
		args.append( int(methods) )
		
		req = [ struct.pack('BBB', *args ) ]
		return ( ''.join( req ), summary )
		
	def decodenego(self, sock):
		"""
	
		"""
		self.debug( 'decode sock nego rsp' )
		tpl = None
		summary = 'response'	
		try:
			sock_rsp = struct.unpack('!2B', sock)

			# extract version
			V = str(sock_rsp[0])

			#		'00' NO AUTHENTICATION REQUIRED
			#		'01' GSSAPI
			#		'02' USERNAME/PASSWORD
			#		'03' to X'7F' IANA ASSIGNED
			#		'80' to X'FE' RESERVED FOR PRIVATE METHODS
			#		'FF' NO ACCEPTABLE METHODS	
			METHOD = 'unknown'
			if sock_rsp[1] == 0:
				METHOD = 'no authentication required'
			
			if sock_rsp[1] == 1:
				METHOD = 'gssapi'

			if sock_rsp[1] == 2:
				METHOD = 'username/password'

			if sock_rsp[1] == 255:
				METHOD = 'no acceptable methods'
			
			summary = METHOD	
			tpl = templates.socks(version=V, 
														methods=str(sock_rsp[1]),
														methods_str=METHOD,
														more=templates.received()
														)
		except Exception as e:
			self.error('unable to decode sock5 nego response: %s' % e)
		return (tpl, summary)
		
	def encode(self, socks_tpl):
		"""
		"""
		self.debug( 'encode sock' )
		summary = 'connect'
		
		vn = socks_tpl.get('version')
		cd = socks_tpl.get('command')
		if cd == 'connect':
			cd = CD_CONNECT
		if cd == 'bind':
			cd = CD_BIND
		if cd == 'udp':
			cd = CD_UDP
		dstport = socks_tpl.get('remote-port')
		dstip = socks_tpl.get('remote-ip')
		rsv = socks_tpl.get('reserved')
		atype = socks_tpl.get('remote-type')
		self.debug( 'template read' )
		
		args = []
		args.append( int(vn) )
		args.append( int(cd) )
		args.append( int(rsv) )
		args.append( int(atype) )

		req = [ struct.pack('BBBB', *args ) ]
		
		ipstr = TestValidatorsLib.IPv4Address(separator='.').toList(ip=dstip)
		req.append( struct.pack('4B', *ipstr) )
		
		req.append( struct.pack('>H', int(dstport) ) )

		return ( ''.join( req ), summary )
		
	def decode(self, sock):
		"""
		Support ipv4 only for now
		"""
		self.debug( 'decode sock rsp' )
		tpl = None
		summary = 'response'	
		try:
			sock_rsp = struct.unpack('!4B4BH', sock)

			if sock_rsp[1] == 0:
				summary = 'succeeded'

			tpl = templates.socks(version=str(sock_rsp[0]), 
														result=str(sock_rsp[1]), 
														reserved=str(sock_rsp[2]),
														remoteType=str(sock_rsp[3]),
														remotePort=str(sock_rsp[8]), 
														remoteAddress='.'.join(map(str,sock_rsp[4:8])),
														more=templates.received()
														)
		except Exception as e:
			self.error('unable to decode sock5 response: %s' % e)
		return (tpl, summary)