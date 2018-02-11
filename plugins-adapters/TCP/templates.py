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

def tcp(source=None, destination=None, more=None,  sum=None, sum_status=None, sum_int=None,seq_num=None,  ack_num=None, 
				data=None, data_size=None, window=None, window_int=None, urgent=None, urgent_int=None,
				data_offset=None, control_bits=None, control_bits_str=None,
				options=None, options_size=None, opt_max_seg=None, opt_pad=None, opt_nop=None, opt_end=None, opt_win_scale=None,
				opt_ts=None, opt_sack_permitted=None, opt_sack=None, opt_echo=None, opt_reply=None):
	"""
	Construct a template for a tcp packet
	"""
	tpl = TestTemplatesLib.TemplateLayer(name='TCP')
	
	# add keys
	if source is not None:
		tpl.addKey(name='source-port', data=str(source) )
	if destination is not None:
		tpl.addKey(name='destination-port', data=str(destination) )

	if sum is not None:
		tpl_sum = TestTemplatesLib.TemplateLayer(name=sum)
		if sum_status is not None:
			tpl_sum.addKey(name='status', data=sum_status )
		if sum_int is not None:
			tpl_sum.addKey(name='integer', data=sum_int )
		tpl.addKey(name='checksum', data=tpl_sum )
	
	if seq_num is not None:
		tpl.addKey(name='sequence-number', data=seq_num )

	if ack_num is not None:
		tpl.addKey(name='acknowledgment-number', data=ack_num )

	if window is not None:
		tpl_window = TestTemplatesLib.TemplateLayer(name=window)
		if window_int is not None:
			tpl_window.addKey(name='integer', data=window_int )
		tpl.addKey(name='window', data=tpl_window )
	
	if data_offset is not None:
		tpl_offset = TestTemplatesLib.TemplateLayer(name=data_offset)
		tpl.addKey(name='data-offset', data=tpl_offset )
	
	if urgent is not None:
		tpl_urgent = TestTemplatesLib.TemplateLayer(name=urgent)
		if urgent_int is not None:
			tpl_urgent.addKey(name='integer', data=urgent_int )
		tpl.addKey(name='urgent-pointer', data=tpl_urgent )
	
	if control_bits is not None:
		tpl_control = TestTemplatesLib.TemplateLayer(name=control_bits)
		if control_bits_str is not None:
			tpl_control.addKey(name='string', data=control_bits_str )
		tpl.addKey(name='control-bits', data=tpl_control )
	
	if options is not None:
		tpl_opts = TestTemplatesLib.TemplateLayer(name=options)
		if options_size is not None:
			tpl_opts.addKey(name='length', data=options_size ) 
		if opt_nop is not None:
			tpl_opts.addKey(name='no-operation', data=opt_nop ) 
		if opt_end is not None:
			tpl_opts.addKey(name='end-of-option-list', data=opt_end ) 
		if opt_win_scale is not None:
			tpl_opts.addKey(name='window-scale', data=opt_win_scale ) 
		if opt_max_seg is not None:
			tpl_opts.addKey(name='maximun-segment-size', data=opt_max_seg ) 
		if opt_pad is not None:
			tpl_opts.addKey(name='padding', data=opt_pad ) 
		if opt_pad is not None:
			tpl_opts.addKey(name='padding', data=opt_pad ) 
		if opt_sack_permitted is not None:
			tpl_opts.addKey(name='sack-permitted', data=opt_sack_permitted ) 
		if opt_sack is not None:
			tpl_opts.addKey(name='sack', data=opt_sack ) 
		if opt_echo is not None:
			tpl_opts.addKey(name='echo', data=opt_echo ) 
		if opt_reply is not None:
			tpl_opts.addKey(name='reply', data=opt_reply ) 
		tpl.addKey(name='options', data=tpl_opts )
		
	# set data upper
	if data is not None:
		tpl_data = TestTemplatesLib.TemplateLayer(name=data)
		if data_size is not None:
			tpl_data.addKey(name='length', data=data_size )
		tpl.addKey(name='data', data=tpl_data )

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
	
	return tpl
	
def sent(data=None, data_length=None, id=None):
	"""
	Construct a template for TCP outgoing data
	"""
	tpl = { 'tcp-event': 'sent' }
	if data is not None:
		tpl['tcp-data'] = data
	
	if data_length is not None:
		tpl['tcp-data-length'] = data_length
		
	if id is not None:
		tpl['client-id'] = str(id)	
	return tpl	

def connection_closing():
	"""
	Construct a template for TCP connection closing
	"""
	tpl = { 'tcp-event': 'connection-closing' }
	return tpl	
	
	
def connection_refused():
	"""
	Construct a template for TCP connection refused
	"""
	tpl = { 'tcp-event': 'connection-refused' }
	return tpl	
	
def connection_reset():
	"""
	Construct a template for TCP connection reset
	"""
	tpl = { 'tcp-event': 'connection-reset' }
	return tpl	
	
def received(data=None, data_length=None, id=None):
	"""
	Construct a template for TCP incoming data
	"""
	tpl = { 'tcp-event': 'received' }
	if data is not None:
		tpl['tcp-data'] = data	
	
	if data_length is not None:
		tpl['tcp-data-length'] = data_length
	
	if id is not None:
		tpl['client-id'] = str(id)	
	return tpl
	
def connection():
	"""
	Construct a template for TCP connection
	"""
	tpl = { 'tcp-event': 'connection' }
	return tpl	
	
def connected():
	"""
	Construct a template for TCP connection
	"""
	tpl = { 'tcp-event': 'connected' }
	return tpl	
	
def disconnection():
	"""
	Construct a template for TCP connection
	"""
	tpl = { 'tcp-event': 'disconnection' }
	return tpl	
	
def disconnected():
	"""
	Construct a template for TCP disconnection
	"""
	tpl = { 'tcp-event': 'disconnected' }
	return tpl	
	
def disconnected_by_server():
	"""
	Construct a template for TCP disconnection
	"""
	tpl = { 'tcp-event': 'disconnected-by-server' }
	return tpl	

def generic_error():
	"""
	Construct a template for TCP generic error
	"""
	tpl = {'tcp-event': 'generic-error'}
	return tpl	

def connection_refused():
	"""
	Construct a template for TCP on connection refused
	"""
	tpl = { 'tcp-event': 'connection-refused' }
	return tpl

def connection_timeout():
	"""
	Construct a template for TCP on connection timeout
	"""
	tpl = { 'tcp-event': 'connection-timeout' }
	return tpl

def connection_failed(errno=None, errstr=None):
	"""
	Construct a template for TCP on connection failed
	"""
	tpl = { 'tcp-event': 'connection-failed' }
	if errno is not None:
		tpl['error-no'] = errno
	if errstr is not None:
		tpl['error-str'] = errstr
	return tpl

def dns_resolution_failed():
	"""
	Construct a template for dns resolution failed
	"""
	tpl = { 'tcp-event': 'dns-resolution-failed' }
	return tpl

def start_listening():
	"""
	Construct a template for TCP listening
	"""
	tpl = { 'tcp-event': 'start-listening' }
	return tpl	

def stop_listening():
	"""
	Construct a template for TCP listening
	"""
	tpl = { 'tcp-event': 'stop-listening' }
	return tpl	

def is_listening():
	"""
	Construct a template for TCP listening
	"""
	tpl = { 'tcp-event': 'is-listening' }
	return tpl	

def is_stopped():
	"""
	Construct a template for TCP listening
	"""
	tpl = { 'tcp-event': 'is-stopped' }
	return tpl	
	
def listening_failed(errno=None, errstr=None):
	"""
	Construct a template for TCP on connection failed
	"""
	tpl = { 'tcp-event': 'listening-failed' }
	if errno is not None:
		tpl['error-no'] = errno
	if errstr is not None:
		tpl['error-str'] = errstr
	return tpl
	
def client_connected(id=None):
	"""
	Construct a template for TCP new connection
	"""
	tpl = { 'tcp-event': 'client-connected' }
	if id is not None:
		tpl['client-id'] = str(id)
	return tpl	

def client_disconnected(id=None):
	"""
	Construct a template for TCP new connection
	"""
	tpl = { 'tcp-event': 'client-disconnected' }
	if id is not None:
		tpl['client-id'] = str(id)	
	return tpl	