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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestLibraryLib as TestLibrary
import sys

def term():
	"""
	Construct a template for term
	"""
	tpl = TestTemplates.TemplateLayer('TERM')
	return tpl

def term_open(ip=None, port=None, login=None):
    """
    Construct a template for a term event
    """
    tpl = term()
    tpl.addKey(name='event', data="open")
    if ip is not None:
        tpl.addKey(name='ip', data=ip)
    if port is not None:
        tpl.addKey(name='port', data=port)
    if login is not None:
        tpl.addKey(name='login', data=login)
    return tpl

def term_opened(data=None):
	"""
	Construct a template for a term event
	"""
	tpl = term()
	tpl.addKey(name='event', data="opened")
	if data is not None:
		tpl.addKey(name='data', data=data)
	
	return tpl
def term_open_failed(data=None):
	"""
	Construct a template for a term event
	"""
	tpl = term()
	tpl.addKey(name='event', data="open-failed")
	if data is not None:
		tpl.addKey(name='data', data=data)
	
	return tpl
def term_close():
	"""
	Construct a template for a term event
	"""
	tpl = term()
	tpl.addKey(name='event', data="close")

	return tpl
	
def term_closed():
	"""
	Construct a template for a term event
	"""
	tpl = term()
	tpl.addKey(name='event', data="closed")

	return tpl
	
def term_data(data=None):
	"""
	Construct a template for a term event
	"""
	tpl = term()
	tpl.addKey(name='event', data="text")
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl
