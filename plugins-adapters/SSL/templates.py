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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
import sys

def ssl(version=None, more=None):
	"""
	Construct a template for a ssl packet
	"""
	tpl = TestTemplatesLib.TemplateLayer(name='SSL')
	
	if version is not None:
		tpl.addKey(name='version', data=version )
		
	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
	return tpl
	
def do_handshake(check_certificate):
	"""
	Construct a template for ssl handshake
	"""
	tpl = { 'ssl-event': 'handshake','check-certificate': check_certificate }
	return tpl	

def handshake_accepted(cipher=None,version=None,bits=None, certPEM=None, cert=None):
	"""
	Construct a template for ssl handshake completed
	"""
	tpl = { 'ssl-event': 'handshake-accepted' }
	if cipher is not None:
		tpl['cipher'] = cipher
	if version is not None:
		tpl['version'] = version		
	if bits is not None:
		tpl['bits'] = bits	
	if certPEM is not None:
		serverCertif = ( certPEM, {}  )	
		tpl['server-certificate-PEM'] = serverCertif			
	if cert is not None:
		tpl['server-certificate-decoded'] = cert			
	return tpl	

def handshake_failed(error):
	"""
	Construct a template for ssl handshake completed
	"""
	tpl = { 'ssl-event': 'handshake-failed', 'ssl-error': error }
	return tpl	

def sent(data=None):
	"""
	Construct a template for ssl outgoing data
	"""
	tpl = { 'ssl-event': 'sent' }
	if data is not None:
		tpl['ssl-data-decoded'] = data
	return tpl

def received(data=None):
	"""
	Construct a template for ssl incoming data
	"""
	tpl = { 'ssl-event': 'received' }
	if data is not None:
		tpl['ssl-data-decoded'] = data	
	return tpl