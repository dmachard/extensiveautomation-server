#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

def snmp(version=None, community=None, agentAddr=None, enterprise=None, genericTrap=None, 
							specificTrap=None, uptime=None, varbinds=None, 
							requestId=None, errorStatus=None, errorIndex=None):
	"""
	Construct a template for a WS packet
	"""
	tpl = TestTemplatesLib.TemplateLayer('SNMP')

	if version is not None:
		tpl.addKey(name='version', data=version)

	if community is not None:
		tpl.addKey(name='community', data=community)
		
	if agentAddr is not None:
		tpl.addKey(name='agent-address', data=agentAddr)
	
	if enterprise is not None:
		tpl.addKey(name='enterprise', data=enterprise)
	
	if genericTrap is not None:
		tpl.addKey(name='generic-trap', data=genericTrap)
	
	if specificTrap is not None:
		tpl.addKey(name='specific-trap', data=specificTrap)
	
	if uptime is not None:
		tpl.addKey(name='uptime', data=uptime)
	
	if varbinds is not None:
		tpl.addKey(name='variable-bindings', data=varbinds)

	# trap v2c
	if requestId is not None:
		tpl.addKey(name='request-id', data=requestId)
		
	if errorStatus is not None:
		tpl.addKey(name='error-status', data=errorStatus)
	
	if errorIndex is not None:
		tpl.addKey(name='error-index', data=errorIndex)
		
	return tpl
