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

def ws(fin=None, mask=None, opcode=None, data=None, rsv1=None, rsv2=None, rsv3=None, data_length=None, more=None):
	"""
	Construct a template for a WS packet
	"""
	tpl = TestTemplatesLib.TemplateLayer('WEBSOCKET')

	if fin is not None:
		tpl.addKey(name='fin', data=str(fin))
	
	if opcode is not None:
		tpl.addKey(name='opcode', data=str(opcode))
		
	if mask is not None:
		tpl.addKey(name='mask', data=str(mask))

	if rsv1 is not None:
		tpl.addKey(name='rsv1', data=str(rsv1))
	
	if rsv2 is not None:
		tpl.addKey(name='rsv2', data=str(rsv2))
	
	if rsv3 is not None:
		tpl.addKey(name='rsv3', data=str(rsv3))

	if data is not None:
		tpl.addKey(name='data', data=data)
	
	if data_length is not None:
		tpl.addKey(name='data-length', data=str(data_length))
		
	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
		
	return tpl

def handshake():
	"""
	handshake event
	"""
	tpl = { 'ws-event': 'handshake' }
	return tpl	

def handshake_ok():
	"""
	handshake event
	"""
	tpl = { 'ws-event': 'handshake-success' }
	return tpl	

def handshake_error(details=None):
	"""
	handshake event
	"""
	tpl = { 'ws-event': 'handshake-error' }
	if details is not None:
		tpl.addKey(name='details', data=details)
	return tpl	

def sent():
	"""
	sent event
	"""
	tpl = { 'ws-event': 'sent' }
	return tpl	
	
def received():
	"""
	received event
	"""
	tpl = { 'ws-event': 'received' }
	return tpl	