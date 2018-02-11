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

def pinger(destination=None, more=None, type=None):
	"""
	Construct a template for a pinger event
	"""
	tpl = TestTemplatesLib.TemplateMessage()
	
	layer_pinger = TestTemplatesLib.TemplateLayer(name='PINGER')
	if destination is not None:
		layer_pinger.addKey(name='destination', data=destination )
	
	if type is not None:
		layer_pinger.addMore(more=type)
		
	# add additional keys
	if more is not None:
		layer_pinger.addMore(more=more)
		
	tpl.addLayer(layer=layer_pinger)
	return tpl

def icmp():
	"""
	Construct a template
	"""
	tpl = { 'ping-type': 'icmp' }
	return tpl	

def url(code=None, body=None):
	"""
	Construct a template
	"""
	tpl = { 'ping-type': 'url' }
	if code is not None:
		tpl['code'] = code
	if body is not None:
		tpl['body'] = body		
	return tpl

def tcp(destination):
	"""
	Construct a template
	"""
	tpl = { 'ping-type': 'tcp', 'on-port': destination  }
	return tpl
	
def ping():
	"""
	Construct a template
	"""
	tpl = { 'ping-event': 'ping' }
	return tpl	

def alive():
	"""
	Construct a template
	"""
	tpl = { 'ping-event': 'alive' }
	return tpl	

def no_response():
	"""
	Construct a template
	"""
	tpl = { 'ping-event': 'no-response' }
	return tpl	