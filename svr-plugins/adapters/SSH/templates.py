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
	layer_ssh = TestTemplatesLib.TemplateLayer(name='SSH')
	
	# add keys
	if host is not None:
		layer_ssh.addKey(name='destination-host', data=host )
	if port is not None:
		layer_ssh.addKey(name='destination-port', data=port )
		
	# add additional keys
	if more is not None:
		layer_ssh.addMore(more=more)
	
	return layer_ssh

def open_channel():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'open-channel' }
	return tpl	
	
def open_channel_ok():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'channel-opened' }
	return tpl	
	
def open_channel_failed():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'open-channel-failed' }
	return tpl	
	
def authentication():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'authentication' }
	return tpl	

def authentication_ok():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'authentication-ok' }
	return tpl	
	
def authentication_failed(err=None):
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'authentication-failed' }
	if err is not None:
		tpl['error'] = err
	return tpl	
	
def negotiation():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'negotiation' }
	return tpl	

def negotiation_ok():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'negotiation-ok' }
	return tpl	
	
def negotiation_failed(err=None):
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'negotiation-failed' }
	if err is not None:
		tpl['error'] = err
	return tpl	
	
def connection():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'connection' }
	return tpl	
	
def connected():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'connected' }
	return tpl	
	
def disconnection():
	"""
	Construct a template for SSH connection
	"""
	tpl = { 'ssh-event': 'disconnection' }
	return tpl	
	
def disconnected():
	"""
	Construct a template for SSH disconnection
	"""
	tpl = { 'ssh-event': 'disconnected' }
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

def disconnected_by_server():
	"""
	Construct a template for SSH disconnection
	"""
	tpl = { 'ssh-event': 'disconnected-by-server' }
	return tpl	

def generic_error():
	"""
	Construct a template for SSH generic error
	"""
	tpl = {'ssh-event': 'generic-error'}
	return tpl	
	
def connection_refused():
	"""
	Construct a template for SSH connection refused
	"""
	tpl = { 'ssh-event': 'connection-refused' }
	return tpl	
	
def connection_reset():
	"""
	Construct a template for SSH connection reset
	"""
	tpl = { 'ssh-event': 'connection-reset' }
	return tpl	

def connection_refused():
	"""
	Construct a template for SSH on connection refused
	"""
	tpl = { 'ssh-event': 'connection-refused' }
	return tpl

def connection_timeout():
	"""
	Construct a template for SSH on connection timeout
	"""
	tpl = { 'ssh-event': 'connection-timeout' }
	return tpl

def connection_failed(errno=None, errstr=None):
	"""
	Construct a template for SSH on connection failed
	"""
	tpl = { 'ssh-event': 'connection-failed' }
	if errno is not None:
		tpl['error-no'] = errno
	if errstr is not None:
		tpl['error-str'] = errstr
	return tpl

def data_sent(data=None):
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'data-sent'}
	if data is not None:
		tpl['data'] = data
	return tpl

def data_received(data=None):
	"""
	Construct a template
	"""
	tpl = { 'ssh-event': 'data-received'}
	if data is not None:
		tpl['data'] = data
	return tpl