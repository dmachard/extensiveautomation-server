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
import sys

def socks(version=None, more=None, result=None, remotePort=None, remoteAddress=None, type=None,
					nmethods=None, methods=None, reserved=None, remoteType=None,
					remoteType_str=None, methods_str=None):
	"""
	Construct a template for a ssl packet
	"""
	tpl = TestTemplatesLib.TemplateLayer(name='TUNNEL')
	
	if version is not None:
		tpl.addKey(name='version', data=version )
		
	if result is not None:
		tpl.addKey(name='result', data=result )
		
	if remotePort is not None:
		tpl.addKey(name='remote-port', data=remotePort )
		
	if remoteAddress is not None:
		tpl.addKey(name='remote-address', data=remoteAddress )
	
	if remoteType_str is not None:
		tpl.addKey(name='remote-type-string', data=remoteType_str )

	if remoteType is not None:
		tpl.addKey(name='remote-type', data=remoteType )
		
	if type is not None:
		tpl.addKey(name='tunnel-type', data=type )
		
	if nmethods is not None:
		tpl.addKey(name='number-methods', data=nmethods )

	if methods is not None:
		tpl.addKey(name='methods', data=methods)

	if methods_str is not None:
		tpl.addKey(name='methods-string', data=methods_str )
		
	if reserved is not None:
		tpl.addKey(name='reserved', data=reserved )
		
	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
	return tpl

def connect(userId=None, destPort=None, destIp=None, destType=None):
	"""
	Construct a template for connect
	"""
	tpl = { 'command': 'connect' }
	
	if userId is not None:
		tpl['user-id'] = userId
	
	if destPort is not None:
		tpl['remote-port'] = destPort
	
	if destIp is not None:
		tpl['remote-ip'] = destIp

	if destType is not None:
		tpl['remote-type'] = destType
		
		
	return tpl	

def sent():
	"""
	"""
	tpl = {'tunnel-event': 'sent'}
	return tpl
	
def received():
	"""
	"""
	tpl = {'tunnel-event': 'received'}
	return tpl