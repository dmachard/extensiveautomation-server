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

def dns(more=None):
	"""
	Construct a template for a dns packet
	"""
	tpl = TestTemplatesLib.TemplateLayer(name='DNS')

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
	return tpl
	

def resolv(hostname=None):
	"""
	Construct a template for dns resolution
	"""
	tpl = { 'dns-event': 'resolving'}
	
	if hostname is not None:
		tpl['hostname'] = hostname
		
	return tpl	

def resolv_success(hostname=None, destinationIp=None):
	"""
	Construct a template for dns resolution wih success
	"""
	tpl = { 'dns-event': 'resolution-success' }
	
	if hostname is not None:
		tpl['hostname'] = hostname
		
	if destinationIp is not None:
		tpl['destination-ip'] = destinationIp
		
	return tpl	
	
def resolv_failed(hostname=None, error=None):
	"""
	Construct a template for dns resolution failed
	"""
	tpl = { 'dns-event': 'resolution-failed' }
	
	if hostname is not None:
		tpl['hostname'] = hostname
	
	if error is not None:
		tpl['error'] = error
		
	return tpl	
