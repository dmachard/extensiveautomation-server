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

def ftp(cmd=None, event=None, ip=None, port=None, user=None, password=None, file=None, 
									content=None, contentLength=None):
	"""
	Construct a template
	"""
	tpl = TestTemplatesLib.TemplateLayer('FTP')

	if event is not None:
		tpl.addKey(name='event', data=event )

	if cmd is not None:
		tpl.addKey(name='cmd', data=cmd )

	if ip is not None:
		tpl.addKey(name='ip', data=ip )

	if port is not None:
		tpl.addKey(name='port', data=port )

	if user is not None:
		tpl.addKey(name='user', data=user )

	if password is not None:
		tpl.addKey(name='password', data=password )
		
	if file is not None:
		tpl.addKey(name='file', data=file )

	if content is not None:
		tpl.addKey(name='content', data=content )

	if contentLength is not None:
		tpl.addKey(name='content-length', data=str(contentLength) )

	return tpl
	
def connection(ip=None, port=None, tls=None):
	"""
	Construct a template for FTP connection
	"""
	tpl = { 'ftp-event': 'connection' }
	if ip is not None:
		tpl['destination-ip'] = ip
	if port is not None:
		tpl['destination-port'] = port
	if tls is not None:
		tpl['tls-support'] = tls
	return tpl	
	
def secure():
	"""
	Construct a template for FTP connection
	"""
	tpl = { 'ftp-event': 'secure' }
	return tpl	
	
def connected():
	"""
	Construct a template for FTP connection
	"""
	tpl = { 'ftp-event': 'connected' }
	return tpl	
	
def disconnection():
	"""
	Construct a template for FTP connection
	"""
	tpl = { 'ftp-event': 'disconnection' }
	return tpl	
	
def disconnected():
	"""
	Construct a template for FTP disconnection
	"""
	tpl = { 'ftp-event': 'disconnected' }
	return tpl	
	
	
def login(user=None, password=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if user is not None:
		tpl['user'] = user
	if password is not None:
		tpl['password'] = password
	return tpl	
	
def logged():
	"""
	Construct a template for FTP logged
	"""
	tpl = { 'ftp-event': 'logged' }
	return tpl	
	
def command(cmd=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if cmd is not None:
		tpl['cmd'] = cmd
	return tpl	
	
def add(path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	return tpl	
	
def delete(filename=None, path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'delete' }
	if filename is not None:
		tpl['filename'] = filename
	if path is not None:
		tpl['path'] = path
	return tpl	
def wait_folder(folder=None, path=None, result=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'wait-folder' }
	if folder is not None:
		tpl['folder'] = folder
	if path is not None:
		tpl['path'] = path
	if result is not None:
		tpl['result'] = result
	return tpl	
def wait_file(filename=None, path=None, result=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'wait-file' }
	if filename is not None:
		tpl['filename'] = filename
	if path is not None:
		tpl['path'] = path
	if result is not None:
		tpl['result'] = result
	return tpl	
def size(filename=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if filename is not None:
		tpl['filename'] = filename
	return tpl	
	
def rename(fromPath=None, toPath=None, fromFilename=None, toFilename=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if fromPath is not None:
		tpl['from-path'] = fromPath
	if toPath is not None:
		tpl['to-path'] = toPath
	if fromFilename is not None:
		tpl['from-filename'] = fromFilename
	if toFilename is not None:
		tpl['to-filename'] = toFilename
	return tpl	
	
def listing(path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	return tpl	

def current():
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	return tpl	
	
def goto(path=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
	if path is not None:
		tpl['path'] = path
	return tpl	
	
def put(fromPath=None, toPath=None, content=None):
	"""
	Construct a template for FTP logging
	"""
	tpl = { 'ftp-event': 'request' }
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
	tpl = { 'ftp-event': 'request' }
	if filename is not None:
		tpl['filename'] = filename
	return tpl	
	
def response(rsp=None, content=None):
	"""
	Construct a template for FTP logged
	"""
	tpl = { 'ftp-event': 'response' }
	if rsp is not None:
		tpl['result'] = rsp
	if content is not None:
		tpl['content'] = content
	return tpl	
	
def response_error(rsp=None):
	"""
	Construct a template for FTP logged
	"""
	tpl = { 'ftp-event': 'response-error' }
	if rsp is not None:
		tpl['rsp'] = rsp
	return tpl	
	
def welcome(msg=None):
	"""
	Construct a template for FTP logged
	"""
	tpl = { 'ftp-event': 'welcome' }
	if msg is not None:
		tpl['msg'] = msg
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