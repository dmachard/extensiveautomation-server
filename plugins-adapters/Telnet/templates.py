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

# templates for telnet client
def telnet(more=None, cmds=None, data=None, subs=None):
	"""
	Construct a template for a telnet packet
	"""
	tpl = TestTemplatesLib.TemplateLayer('TELNET')

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
	
	if cmds is not None:
		tpl.addKey(name='commands', data=cmds )

	if subs is not None:
		tpl.addKey(name='suboptions', data=subs )

	if data is not None:
		tpl.addKey(name='data', data=data )

	return tpl

def dataIncoming(cmds=None, data=None):
	tpl =  telnet(cmds=cmds, data=data)
	tpl.addKey(name='payload', data='incoming' )
	return tpl
	
def dataOutgoing(data=None):
	tpl =  telnet(data=data)
	tpl.addKey(name='payload', data='outgoing' )
	return tpl