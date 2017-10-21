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

def generic_error():
	"""
	Construct a template for socket generic error
	"""
	tpl = {'ethernet-event': 'generic-error'}
	return tpl	
	
def starting(interface=None):
	"""
	Construct a template for  starting
	"""
	tpl = { 'ethernet-event': 'starting' }
	if interface is not None:
		tpl['interface'] = interface
	return tpl
	
def sniffing(macSrc=None, interface=None):
	"""
	Construct a template for sniffing
	"""
	tpl = { 'ethernet-event': 'sniffing' }
	if macSrc is not None:
		tpl['mac-source'] = macSrc
	if interface is not None:
		tpl['interface'] = interface
	return tpl

def sniffing_failed(err=None, interface=None):
	"""
	Construct a template for sniffing failed
	"""
	tpl = { 'ethernet-event': 'sniffing-failed' }
	if interface is not None:
		tpl['interface'] = interface
	if err is not None:
		tpl['error'] = err
	return tpl
	
def stopping(interface=None):
	"""
	Construct a template for Ethernet stopping
	"""
	tpl = { 'ethernet-event': 'stopping' }
	if interface is not None:
		tpl['interface'] = interface
	return tpl

def stopped(interface=None):
	"""
	Construct a template for Ethenert stopped
	"""
	tpl = { 'ethernet-event': 'stopped' }
	if interface is not None:
		tpl['interface'] = interface
	return tpl

def stopping_failed(interface=None):
	"""
	Construct a template for stopping failed
	"""
	tpl = { 'ethernet-event': 'stopping-failed' }
	if interface is not None:
		tpl['interface'] = interface
	return tpl

def ethernet(destAddr=None, srcAddr=None, etherType=None, data=None, size_data=None, vendorDst=None, vendorSrc=None,
					protocolUpper=None, more=None, padding=None):
	"""
	Construct a template for a Ethernet packet
	"""
	tpl_ether = TestTemplatesLib.TemplateLayer('ETHERNET-II')

	if destAddr is not None:
		tpl_dst = TestTemplatesLib.TemplateLayer(name=destAddr)
		if vendorDst is not None:
			tpl_dst.addKey(name='vendor', data=vendorDst )
		tpl_ether.addKey(name='mac-destination', data=tpl_dst )
	
	if srcAddr is not None:
		tpl_src = TestTemplatesLib.TemplateLayer(name=srcAddr)
		if vendorSrc is not None:
			tpl_src.addKey(name='vendor', data=vendorSrc )
		tpl_ether.addKey(name='mac-source', data=tpl_src )
		
	if etherType is not None:
		tpl_typ = TestTemplatesLib.TemplateLayer(name=etherType)
		if protocolUpper is not None:
			tpl_typ.addKey(name='string', data=protocolUpper )
		tpl_ether.addKey(name='protocol-upper', data=tpl_typ )
			
	if data is not None:
		tpl_data = TestTemplatesLib.TemplateLayer(name=data)
		if size_data is not None:
			tpl_data.addKey(name='length', data=str(size_data) )
		tpl_ether.addKey(name='data', data=tpl_data )		
	
	if padding is not None:
		tpl_padding = TestTemplatesLib.TemplateLayer(name=padding)
		tpl_padding.addKey(name='length', data=len(padding) )
		tpl_ether.addKey(name='padding', data=tpl_padding )		
		
	# add additional keys
	if more is not None:
		tpl_ether.addMore(more=more)
		
	return tpl_ether