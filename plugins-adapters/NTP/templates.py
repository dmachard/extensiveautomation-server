#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestLibraryLib as TestLibrary
import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

def ntp(more=None):
	"""
	Construct a template for a NTP packet
	"""
	tpl = TestTemplates.TemplateLayer('NTP')

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
		
	return tpl

def msg(leap=None, version=None, mode=None, stratum=None, poll=None, precision=None,
									rootDelay=None, rootDispersion=None, refId=None, refTimestamp=None,
									origTimestamp=None, recvTimestamp=None, txTimestamp=None, destTimestamp=None,
									offset=None, delay=None, leapMsg=None, modeMsg=None, stratumMsg=None, refIdMsg=None):
	"""
	"""
	tpl = ntp()
	
	if offset is not None:
		tpl.addKey(name='offset', data="%s" % offset )
		
	if delay is not None:
		tpl.addKey(name='delay', data="%s" % delay )
		
	if leap is not None:
		tpl.addKey(name='leap', data="%s" % leap )
	if leapMsg is not None:
		tpl.addKey(name='leap-text', data="%s" % leapMsg )
		
	if version is not None:
		tpl.addKey(name='version', data="%s" % version )
		
	if mode is not None:
		tpl.addKey(name='mode', data="%s" % mode )
	if modeMsg is not None:
		tpl.addKey(name='mode-text', data="%s" % modeMsg )
		
	if stratum is not None:
		tpl.addKey(name='stratum', data="%s" % stratum )
	if stratumMsg is not None:
		tpl.addKey(name='stratum-text', data="%s" % stratumMsg )

	if poll is not None:
		tpl.addKey(name='poll', data="%s" % poll )
		
	if precision is not None:
		tpl.addKey(name='precision', data="%s" % precision )
		
	if rootDelay is not None:
		tpl.addKey(name='root-delay', data="%s" % rootDelay )
		
	if rootDispersion is not None:
		tpl.addKey(name='root-dispersion', data="%s" % rootDispersion )
		
	if refId is not None:
		tpl.addKey(name='ref-id', data="%s" % refId )
	if refIdMsg is not None:
		tpl.addKey(name='ref-id-text', data="%s" % refIdMsg )
		
	if refTimestamp is not None:
		tpl.addKey(name='ref-timestamp', data="%s" % refTimestamp )
		
	if origTimestamp is not None:
		tpl.addKey(name='orig-timestamp', data="%s" % origTimestamp )
		
	if recvTimestamp is not None:
		tpl.addKey(name='recv-timestamp', data="%s" % recvTimestamp )
		
	if txTimestamp is not None:
		tpl.addKey(name='tx-timestamp', data="%s" % txTimestamp )
		
	if destTimestamp is not None:
		tpl.addKey(name='dest-timestamp', data="%s" % destTimestamp )
		
	return tpl
