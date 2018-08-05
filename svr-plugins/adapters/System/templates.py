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

def windows(get=None, event=None, cmd=None):
	"""
	Construct a template
	"""
	tpl = TestTemplatesLib.TemplateLayer('WINDOWS')

	if get is not None:
		tpl.addKey(name='get', data=get )

	if event is not None:
		tpl.addKey(name='event', data=event )

	if cmd is not None:
		tpl.addKey(name='cmd', data=cmd )
		
	return tpl

def linux(get=None, event=None):
	"""
	Construct a template
	"""
	tpl = TestTemplatesLib.TemplateLayer('LINUX')

	if get is not None:
		tpl.addKey(name='get', data=get )

	if event is not None:
		tpl.addKey(name='event', data=event )

	return tpl

def file(cmd=None, event=None, file=None, fileDst=None, content=None, contentLength=None, filename=None, path=None, result=None,
							checksum=None, checksumType=None, timeout=None, requestId=None, size=None, sizeHuman=None, pathDst=None, 
								modificationDate=None, listFiles=None, resultHtml=None, resultCompare=None):
	"""
	Construct a template
	"""
	tpl = TestTemplatesLib.TemplateLayer('FILE')

	if modificationDate is not None:
		tpl.addKey(name='modification-date', data=modificationDate )
		
	if cmd is not None:
		tpl.addKey(name='cmd', data=cmd )
		
	if requestId is not None:
		tpl.addKey(name='request-id', data=requestId )
		
	if listFiles is not None:
		tpl.addKey(name='list-files', data=listFiles )
		
	if timeout is not None:
		tpl.addKey(name='timeout', data=timeout )
		
	if checksumType is not None:
		tpl.addKey(name='checksum-type', data=checksumType )

	if checksum is not None:
		tpl.addKey(name='checksum', data=checksum )
		
	if resultCompare is not None:
		tpl.addKey(name='result-compare', data=resultCompare )
		
	if resultHtml is not None:
		tpl.addKey(name='result-html', data=resultHtml )

	if result is not None:
		tpl.addKey(name='result', data=result )

	if size is not None:
		tpl.addKey(name='size', data=size )

	if sizeHuman is not None:
		tpl.addKey(name='size-human', data=sizeHuman )
		
	if file is not None:
		tpl.addKey(name='file', data=file )
		
	if fileDst is not None:
		tpl.addKey(name='file-dest', data=fileDst )
		
	if filename is not None:
		tpl.addKey(name='filename', data=filename )

	if pathDst is not None:
		tpl.addKey(name='path-dest', data=pathDst )

	if path is not None:
		tpl.addKey(name='path', data=path )
		
	if event is not None:
		tpl.addKey(name='event', data=event )

	if content is not None:
		tpl.addKey(name='content', data=content )

	if contentLength is not None:
		tpl.addKey(name='content-length', data=str(contentLength) )
		
	return tpl