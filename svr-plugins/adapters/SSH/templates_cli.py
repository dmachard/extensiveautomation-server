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

def ssh(host=None, port=None, more=None):
	"""
	Construct a SSH template
	"""
	tpl = TestTemplatesLib.TemplateMessage()
	
	layer_ssh = TestTemplatesLib.TemplateLayer(name='SSH')
	
	# add keys
	if host is not None:
		layer_ssh.addKey(name='destination-host', data=host )
	if port is not None:
		layer_ssh.addKey(name='destination-port', data=port )
		
	# add additional keys
	if more is not None:
		layer_ssh.addMore(more=more)
	
	tpl.addLayer(layer=layer_ssh)
	return tpl

def login(username, password):
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'login', 'username':username , 'password':password }
	return tpl

def login_failed():
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'login-failed' }
	return tpl

def connected():
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'connected' }
	return tpl

def disconnected():
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'disconnected' }
	return tpl
	
def error(errstr):
	"""
	"""
	tpl = { 'ssh-event': 'error'}
	if errstr is not None:
		tpl['error-str'] = errstr
	return tpl
	
def logout():
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'logout'}
	return tpl
		
def data_sent(data):
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'data-sent'}
	if data is not None:
		tpl['data'] = data
	return tpl

def data_received(data):
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'data-received'}
	if data is not None:
		tpl['data'] = data
	return tpl