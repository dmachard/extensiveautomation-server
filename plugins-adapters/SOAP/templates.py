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

def soap():
	"""
	Construct a SOAP template
	"""
	layer_soap = TestTemplatesLib.TemplateLayer(name='SOAP')
	return layer_soap
	
	
def envelope():
	"""
	Construct a SOAP template
	"""
	layer_soap = soap()
	layer_env = TestTemplatesLib.TemplateLayer(name='')
	layer_soap.addKey('Envelope', layer_env)
	return layer_soap
	

def body():
	"""
	Construct a SOAP template
	"""
	layer_soap = soap()
	layer_env = TestTemplatesLib.TemplateLayer(name='')
	layer_soap.addKey('Envelope', layer_env)
	layer_bod = TestTemplatesLib.TemplateLayer(name='')
	layer_env.addKey('Body', layer_bod)
	return layer_soap