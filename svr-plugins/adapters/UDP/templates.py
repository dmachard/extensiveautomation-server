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

def udp(source=None, destination=None, more=None, sum=None, sum_status=None, sum_int=None,
				length=None, data=None, data_size=None):
	"""
	Construct a template for a udp packet
	"""
	tpl = TestTemplatesLib.TemplateLayer(name='UDP')
	
	# add keys
	if source is not None:
		tpl_src = TestTemplatesLib.TemplateLayer(name=source )
		tpl.addKey(name='source-port', data=tpl_src )
	if destination is not None:
		tpl_dst = TestTemplatesLib.TemplateLayer(name=destination )
		tpl.addKey(name='destination-port', data=tpl_dst )
	
	if length is not None:
		tpl.addKey(name='total-length', data=length )	
		
	if sum is not None:
		tpl_sum = TestTemplatesLib.TemplateLayer(name=sum)
		if sum_status is not None:
			tpl_sum.addKey(name='status', data=sum_status )
		if sum_int is not None:
			tpl_sum.addKey(name='integer', data=sum_int )
		tpl.addKey(name='checksum', data=tpl_sum )
		
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
	Construct a template for UDP outgoing data
	"""
	tpl = { 'udp-event': 'sent' }
	if data is not None:
		tpl['udp-data'] = data

	if data_length is not None:
		tpl['udp-data-length'] = data_length

	if id is not None:
		tpl['client-id'] = str(id)	
	return tpl	

def received(data=None, data_length=None, id=None):
	"""
	Construct a template for UDP incoming data
	"""
	tpl = { 'udp-event': 'received' }
	if data is not None:
		tpl['udp-data'] = data
	
	if data_length is not None:
		tpl['udp-data-length'] = data_length

	if id is not None:
		tpl['client-id'] = str(id)	
	return tpl

def starting():
	"""
	Construct a template for UDP starting
	"""
	tpl = { 'udp-event': 'starting' }
	return tpl
	
def listening():
	"""
	Construct a template for UDP listening
	"""
	tpl = { 'udp-event': 'listening' }
	return tpl

def listening_failed():
	"""
	Construct a template for UDP listening failed
	"""
	tpl = { 'udp-event': 'listening-failed' }
	return tpl
	
def stopping():
	"""
	Construct a template for UDP stopping
	"""
	tpl = { 'udp-event': 'stopping' }
	return tpl

def stopped():
	"""
	Construct a template for UDP stopped
	"""
	tpl = { 'udp-event': 'stopped' }
	return tpl

def stopping_failed():
	"""
	Construct a template for UDP stopping failed
	"""
	tpl = { 'udp-event': 'stopping-failed' }
	return tpl

def icmp_error(error=None, details=None):
	"""
	Construct a template for UDP icmp error
	"""
	tpl = {'udp-event': 'icmp-error' }
	
	if error is not None:
		tpl['type-error'] = error
	
	if details is not None:
		tpl['details-error'] = details
	return tpl	
	
def generic_error():
	"""
	Construct a template for UDP generic error
	"""
	tpl = {'udp-event': 'generic-error'}
	return tpl	