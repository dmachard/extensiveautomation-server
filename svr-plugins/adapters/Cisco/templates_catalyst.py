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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

def catalyst():
	"""
	Construct a template for catalyst
	"""
	tpl = TestTemplates.TemplateLayer('CATALYST')
	return tpl

def catalyst_prompt(data=None):
	"""
	Construct a template for a  prompt event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='prompt')
	if data is not None:
		tpl.addKey(name='data', data=data)
	return tpl

def catalyst_prompt_enable(data=None):
	"""
	Construct a template for a  prompt event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='prompt enable')
	if data is not None:
		tpl.addKey(name='data', data=data)
	return tpl

def catalyst_more(data=None):
	"""
	Construct a template for a  prompt event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='more')
	if data is not None:
		tpl.addKey(name='data', data=data)
	return tpl
def catalyst_prompt_password():
	"""
	Construct a template for a  password prompt event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='prompt password')
	return tpl

def catalyst_prompt_username():
	"""
	Construct a template for a  username prompt event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='prompt username')
	return tpl

def catalyst_bad_login():
	"""
	Construct a template for a  bad username  event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='bad login')
	return tpl

def catalyst_bad_secret():
	"""
	Construct a template for a  bad username  event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='bad secret')
	return tpl

def catalyst_username(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='username')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl

def catalyst_password(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='password')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl

def catalyst_cmd(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='cmd')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl

def catalyst_config(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='config')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl

def catalyst_enable(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='enable')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl

def catalyst_exit(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='exit')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl

def catalyst_writemem(data=None):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='event', data='write mem')
	if data is not None:
		tpl.addKey(name='data', data=data)

	return tpl
	
def catalyst_data(data):
	"""
	Construct a template for a catalyst event
	"""
	tpl = catalyst()
	tpl.addKey(name='data', data=data)

	return tpl