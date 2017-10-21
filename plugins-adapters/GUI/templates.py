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

# templates for gui client
def gui(more=None, action=None, actionId=None, description=None, result=None, text=None, length=None,
							img=None, mainImg=None, mainLength=None, countResult=None, textResult=None, value=None, parameters=None,
							x=None, y=None, steps=None, repeat=None, out=None, state=None):
	"""
	Construct a template for a gui event
	"""
	tpl = TestTemplatesLib.TemplateLayer('GUI')

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
		
	if state is not None:
		tpl.addKey(name='state', data=state )
		
	if out is not None:
		tpl.addKey(name='out', data=out )
		
	if x is not None:
		tpl.addKey(name='x', data=x )
		
	if y is not None:
		tpl.addKey(name='y', data=y )
		
	if steps is not None:
		tpl.addKey(name='steps', data=steps )
		
	if repeat is not None:
		tpl.addKey(name='repeat', data=repeat )
		
	if action is not None:
		tpl.addKey(name='action', data=action )

	if actionId is not None:
		tpl.addKey(name='action-id', data=actionId )
		
	if description is not None:
		tpl.addKey(name='description', data=description )

	if text is not None:
		tpl.addKey(name='txt', data=text )
		
	if result is not None:
		tpl.addKey(name='result', data=result )

	if countResult is not None:
		tpl.addKey(name='count-result', data=countResult )
	
	if textResult is not None:
		tpl.addKey(name='text-result', data=textResult )
		
	if length is not None:
		tpl.addKey(name='length', data=length )

	if img is not None:
		tpl.addKey(name='img', data=img )

	if mainImg is not None:
		tpl.addKey(name='main-img', data=mainImg )

	if mainLength is not None:
		tpl.addKey(name='main-length', data=mainLength )

	if value is not None:
		tpl.addKey(name='value', data=value )

	if parameters is not None:
		tpl.addKey(name='parameters', data=parameters )
	return tpl