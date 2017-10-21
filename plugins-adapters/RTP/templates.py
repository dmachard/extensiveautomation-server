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

def rtp(pl=None, m=None, pt=None, seq=None, ts=None, ssrc=None, v=None, p=None, x=None,  cc=None, csrc=None, ext=None, pad=None,
					pl_length=None, more=None):
	"""
	Construct a template for a RTP packet
	"""
	tpl = TestTemplatesLib.TemplateLayer('RTP')

	if v is not None:
		tpl.addKey(name='version', data=v )

	if p is not None:
		tpl.addKey(name='padding', data=p )

	if pad is not None:
		tpl.addKey(name='padding-data', data=pad)
		
	if x is not None:
		tpl.addKey(name='extension', data=x )

	if cc is not None:
		tpl.addKey(name='csrc-count', data=cc )

	if m is not None:
		tpl.addKey(name='marker', data=m )

	if pt is not None:
		tpl.addKey(name='payload-type', data=pt )

	if pl is not None:
		tpl.addKey(name='payload-data', data=pl )

	if pl_length is not None:
		tpl.addKey(name='payload-length', data=pl_length )
		
	if seq is not None:
		tpl.addKey(name='sequence-number', data=seq )

	if ts is not None:
		tpl.addKey(name='timestamp', data=ts )

	if ssrc is not None:
		tpl.addKey(name='ssrc', data=ssrc )

	if csrc is not None:
		tpl.addKey(name='csrc', data=csrc)

	if ext is not None:
		tpl.addKey(name='header-extension', data=ext)
	
	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
		
	return tpl

def starts_sending(en=None, ssrc=None, mt=None, sessid=None):
	"""
	Construct a template for RTP sending
	"""
	tpl = rtp(ssrc=ssrc)
	tpl.addKey(name='rtp-event', data='starts-sending')
	
	if en is not None:
		tpl.addKey(name='codec', data=en)

	if mt is not None:
		tpl.addKey(name='type', data=mt)
	if sessid is not None:
		tpl.addKey(name='session-id', data=sessid	)
	return tpl	

def stops_sending(en=None, ssrc=None, mt=None, sessid=None):
	"""
	Construct a template for RTP sending
	"""
	tpl = rtp(ssrc=ssrc)
	tpl.addKey(name='rtp-event', data='stops-sending')
	
	if en is not None:
		tpl.addKey(name='codec', data=en)
	
	if mt is not None:
		tpl.addKey(name='type', data=mt)
		
	if sessid is not None:
		tpl.addKey(name='session-id', data= sessid	)
		
	return tpl	
	
def starts_receiving(en=None, ssrc=None, mt=None, sessid=None):
	"""
	Construct a template for RTP receiving
	"""
	tpl = rtp(ssrc=ssrc)
	tpl.addKey(name='rtp-event', data='starts-receiving')
	
	if en is not None:
		tpl.addKey(name='codec', data=en)
	
	if mt is not None:
		tpl.addKey(name='type', data=mt)
		
	if sessid is not None:
		tpl.addKey(name='session-id', data= sessid)
		
	return tpl	

def stops_receiving(en=None, ssrc=None, mt=None, sessid=None):
	"""
	Construct a template for RTP receiving
	"""
	tpl = rtp(ssrc=ssrc)
	tpl.addKey(name='rtp-event', data='stops-receiving')
	
	if en is not None:
		tpl.addKey(name='codec', data=en)
		
	if mt is not None:
		tpl.addKey(name='type', data=mt)
		
	if sessid is not None:
		tpl.addKey(name='session-id', data= sessid)
		
	return tpl	