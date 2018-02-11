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

def sftp(cmd=None):
	"""
	Construct a template
	"""
	tpl = TestTemplatesLib.TemplateLayer('SFTP')
	
	if cmd is not None:
		tpl.addKey(name='cmd', data=cmd )

	return tpl

def add(path=None, mode=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	if mode is not None:
		tpl['mode'] = mode
	return tpl	
	
def delete(filename=None, path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'delete' }
	if filename is not None:
		tpl['filename'] = filename
	if path is not None:
		tpl['path'] = path
	return tpl	
	
def put(fromPath=None, toPath=None, content=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if fromPath is not None:
		tpl['from-path'] = fromPath
	if toPath is not None:
		tpl['to-path'] = toPath
	if content is not None:
		tpl['content'] = content
	return tpl	
	
def get(filename=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if filename is not None:
		tpl['filename'] = filename
	return tpl	
	
def rename(fromPath=None, toPath=None, fromFilename=None, toFilename=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if fromPath is not None:
		tpl['from-path'] = fromPath
	if toPath is not None:
		tpl['to-path'] = toPath
	if fromFilename is not None:
		tpl['from-filename'] = fromFilename
	if toFilename is not None:
		tpl['to-filename'] = toFilename
	return tpl	
	
def goto(path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	return tpl	
	
def listing(path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	return tpl	
	
def wait_file(path=None, filename=None, result=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	if filename is not None:
		tpl['filename'] = filename
	if result is not None:
		tpl['result'] = result
	return tpl	
	
def wait_folder(path=None, folder=None, result=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'sftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	if folder is not None:
		tpl['folder'] = folder
	if result is not None:
		tpl['result'] = result
	return tpl	
	
def response(rsp=None, content=None):
	"""
	Construct a template for FTP logged
	"""
	tpl = { 'sftp-event': 'response' }
	if rsp is not None:
		tpl['result'] = rsp
	if content is not None:
		tpl['content'] = content
	return tpl	
	
def response_error(rsp=None):
	"""
	Construct a template for FTP logged
	"""
	tpl = { 'sftp-event': 'response-error' }
	if rsp is not None:
		tpl['rsp'] = rsp
	return tpl	
	
def get_folder(fromPath=None, toPath=None, overwrite=None):
	"""
	Construct a template for  put folder
	"""
	tpl = { 'sftp-event': 'request' }
	if fromPath is not None:
		tpl['from-path'] = fromPath
	if toPath is not None:
		tpl['to-path'] = toPath
	if overwrite is not None:
		tpl['overwrite'] = overwrite
	return tpl	
	
def put_folder(fromPath=None, toPath=None, overwrite=None):
	"""
	Construct a template for  put folder
	"""
	tpl = { 'sftp-event': 'request' }
	if fromPath is not None:
		tpl['from-path'] = fromPath
	if toPath is not None:
		tpl['to-path'] = toPath
	if overwrite is not None:
		tpl['overwrite'] = overwrite
	return tpl	
	