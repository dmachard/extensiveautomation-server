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


def db(type=None, host=None, port=None, user=None, password=None, more=None):
	"""
	Construct a DB template
	"""
#	tpl = TestTemplatesLib.TemplateMessage()
	
	layer_mysql = TestTemplatesLib.TemplateLayer(name='DB')
	
	# add keys
	if type is not None:
		layer_mysql.addKey(name='type', data=type )
	if host is not None:
		layer_mysql.addKey(name='host', data=host )
	if port is not None:
		layer_mysql.addKey(name='port', data=port )
	if user is not None:
		layer_mysql.addKey(name='user', data=user )
	if password is not None:
		layer_mysql.addKey(name='password', data=password )
		
	# add additional keys
	if more is not None:
		layer_mysql.addMore(more=more)
	
#	tpl.addLayer(layer=layer_mysql)
#	return tpl
	return layer_mysql

def connected():
	"""
	"""
	tpl = { 'db-event': 'connected'}
	return tpl
	
def disconnected():
	"""
	"""
	tpl = { 'db-event': 'disconnected'}
	return tpl
	
def connect(db=None):
	"""
	"""
	tpl = { 'db-event': 'connect'}
	if db is not None:
		tpl['database'] = db
	return tpl

def query(query=None):
	"""
	"""
	tpl = { 'db-event': 'query'}
	if query is not None:
		tpl['query'] = query
	return tpl
	
def executed(status=None, nbChanged=None):
	"""
	"""
	tpl = { 'db-event': 'executed'}
	if nbChanged is not None:
		tpl['number-changed'] = nbChanged
	if status is not None:
		tpl['status'] = status
	return tpl
def terminated(nbRow=None):
	"""
	"""
	tpl = { 'db-event': 'terminated'}
	if nbRow is not None:
		tpl['number-row'] = nbRow
	return tpl
def response(row=None, rowIndex=None, rowMax=None, status=None, nbChanged=None, queryName=None):
	"""
	"""
	tpl = { 'db-event': 'response'}
	if nbChanged is not None:
		tpl['number-changed'] = nbChanged
	if rowIndex is not None:
		tpl['row-index'] = rowIndex
	if status is not None:
		tpl['status'] = status
	if rowMax is not None:
		tpl['row-max'] = rowMax
	if queryName is not None:
		tpl['query-name'] = queryName
	if row is not None:
		layer_rsp = TestTemplatesLib.TemplateLayer(name='')
		layer_rsp.addMore( more=row.items() )
		tpl['row'] = layer_rsp
	return tpl
	
def disconnect():
	"""
	"""
	tpl = { 'db-event': 'disconnect'}
	return tpl
	
def error(code=None, msg=None):
	"""
	"""
	tpl = { 'db-event': 'error'}
	if code is not None:
		tpl['error-code'] = code
	if msg is not None:
		tpl['error-msg'] = msg
	return tpl