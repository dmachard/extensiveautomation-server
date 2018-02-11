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

def ldap(ip=None, port=None, more=None):
	"""
	Construct a LDAP template
	"""
	layer_ldap = TestTemplatesLib.TemplateLayer(name='LDAP')
	if ip is not None: 
		layer_ldap.addKey(name='ip', data="%s" % ip )
	if port is not None: 
		layer_ldap.addKey(name='port', data="%s" % port )

	if more is not None:
		layer_ldap.addMore(more=more)
	return layer_ldap
	
def ldap_connect(dn=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "connection"}
	if dn is not None: 
		tpl['dn'] = "%s" % dn
		
	return tpl
	
def ldap_connected():
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "connected"}
	return tpl
	
def ldap_error(details=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "error"}
	if details is not None: 
		tpl['details'] = details
		
	return tpl
	
def ldap_disconnect(dn=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "disconnection"}
	if dn is not None: 
		tpl['dn'] = "%s" % dn
		
	return tpl
	
def ldap_disconnected():
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "disconnected"}
	return tpl
	
def ldap_search(bdn=None, filter=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "search-query"}
	if bdn is not None: 
		tpl['base-dn'] = "%s" % bdn
	if filter is not None: 
		tpl['filter'] = "%s" % filter
		
	return tpl
	
def ldap_delete():
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "delete"}
	return tpl
	
def ldap_deleted():
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "deleted"}
	return tpl

def ldap_add(bdn=None, record=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "add-query"}
	if bdn is not None: 
		tpl['base-dn'] = "%s" % bdn
	if record is not None: 
		tpl['record'] =  record
		
	return tpl
	
def ldap_update_attribute(bdn=None, attr=None, value=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "add-attribute"}
	if bdn is not None: 
		tpl['base-dn'] = "%s" % bdn
	if attr is not None: 
		tpl['attr'] =  "%s" % attr
	if value is not None: 
		tpl['value'] =   "%s" % value
	return tpl
	
def ldap_add_attribute(bdn=None, attr=None, value=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "add-attribute"}
	if bdn is not None: 
		tpl['base-dn'] = "%s" % bdn
	if attr is not None: 
		tpl['attr'] =  "%s" % attr
	if value is not None: 
		tpl['value'] =   "%s" % value
	return tpl
	
def ldap_delete_attribute(bdn=None, attr=None, value=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "delete-attribute"}
	if bdn is not None: 
		tpl['base-dn'] = "%s" % bdn
	if attr is not None: 
		tpl['attr'] =  "%s" % attr
	if value is not None: 
		tpl['value'] =   "%s" % value
	return tpl
	
def ldap_response(results=None):
	"""
	Construct a template
	"""
	tpl = { "ldap-event": "response"}
	if results is not None: 
		tpl['results'] =  results
	return tpl