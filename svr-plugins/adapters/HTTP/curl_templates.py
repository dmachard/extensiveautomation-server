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

def curl_http(more=None):
	"""
	Construct a template for a HTTP packet
	"""
	tpl = TestTemplatesLib.TemplateLayer('CURL_HTTP')

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
		
	return tpl

def response(version=None, code=None, phrase=None, headers=None, body=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('CURL_HTTP_RESPONSE')
	
	if phrase is not None:
		tpl.addKey(name='phrase', data=phrase)
	if code is not None:
		tpl.addKey(name='code', data=code)
	if version is not None:
		tpl.addKey(name='version', data=version)	

	if headers is not None:
		tpl.addKey(name='headers', data=headers )
	if body is not None:
		tpl.addKey(name='body', data=body)
	return tpl