#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

def arp(hrd=None, pro=None, hln=None, pln=None, op=None, 
        sha=None, spa=None, tha=None, tpa=None, opString=None):
	"""
	"""
	tpl_arp = TestTemplatesLib.TemplateLayer('ARP')
	
	if hrd is not None:
		tpl_arp.addKey(name='hardware-type', data=hrd )
	
	if pro is not None:
		tpl_arp.addKey(name='protocol-type', data=pro )
	
	if hln is not None:
		tpl_arp.addKey(name='hardware-len', data=hln )
	
	if pln is not None:
		tpl_arp.addKey(name='protocol-len', data=pln )
	
	if op is not None:
		tpl_op = TestTemplatesLib.TemplateLayer(name=op)
		if opString is not None:
			tpl_op.addKey(name='string', data=opString )
		tpl_arp.addKey(name='op-code', data=tpl_op )
	
	if sha is not None:
		tpl_arp.addKey(name='sender-mac', data=sha )
	
	if spa is not None:
		tpl_arp.addKey(name='sender-ip', data=spa )
	
	if tha is not None:
		tpl_arp.addKey(name='target-mac', data=tha )
	
	if tpa is not None:
		tpl_arp.addKey(name='target-ip', data=tpa )
		
	return tpl_arp