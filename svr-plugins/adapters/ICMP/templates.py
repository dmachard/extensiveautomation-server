#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

def icmp(tp=None, tp_str=None, code=None, code_str=None, sum=None, sum_status=None, sum_int=None,
        id=None, id_int=None, seq_num=None, seq_num_int=None, data=None, data_size=None, 
        mask=None, time_orig=None, time_rx=None, time_tx=None,
        gw_addr=None, unused=None, pointer=None):
	"""
	Construct a template for a icmp packet
	"""	
	tpl = TestTemplatesLib.TemplateLayer(name='ICMP4')

	if pointer is not None:
		tpl_pointer = TestTemplatesLib.TemplateLayer(name=str(pointer) )
		tpl.addKey(name='pointer', data=tpl_pointer )
		
	if unused is not None:
		tpl_unused = TestTemplatesLib.TemplateLayer(name=str(unused) )
		tpl.addKey(name='unused', data=tpl_unused )
		
	if gw_addr is not None:
		tpl_gw = TestTemplatesLib.TemplateLayer(name=str(gw_addr) )
		tpl.addKey(name='gateway', data=tpl_gw )
		
	if mask is not None:
		tpl_mask = TestTemplatesLib.TemplateLayer(name=str(mask) )
		tpl.addKey(name='mask', data=tpl_mask )

	if time_orig is not None:
		tpl_orig = TestTemplatesLib.TemplateLayer(name=time_orig )
		tpl.addKey(name='originate-timestamp', data=tpl_orig )

	if time_rx is not None:
		tpl_rx = TestTemplatesLib.TemplateLayer(name=time_rx )
		tpl.addKey(name='receive-timestamp', data=tpl_rx )

	if time_tx is not None:
		tpl_tx = TestTemplatesLib.TemplateLayer(name=time_tx )
		tpl.addKey(name='transmit-timestamp', data=tpl_tx )
		
	if id is not None:
		tpl_id = TestTemplatesLib.TemplateLayer(name=id)
		if id_int is not None:
			tpl_id.addKey(name='integer', data=id_int )
		tpl.addKey(name='identifier', data=tpl_id )
	
	if seq_num is not None:
		tpl_seq = TestTemplatesLib.TemplateLayer(name=seq_num)
		if seq_num_int is not None:
			tpl_seq.addKey(name='integer', data=seq_num_int )
		tpl.addKey(name='sequence-number', data=tpl_seq )

	if tp is not None:
		tpl_type = TestTemplatesLib.TemplateLayer(name=tp)
		if tp_str is not None:
			tpl_type.addKey(name='string', data=tp_str )
		tpl.addKey(name='type', data=tpl_type )
		
	if code is not None:
		tpl_code = TestTemplatesLib.TemplateLayer(name=code)
		if code_str is not None:
			tpl_code.addKey(name='string', data=code_str )
		tpl.addKey(name='code', data=tpl_code )
		
	if sum is not None:
		tpl_sum = TestTemplatesLib.TemplateLayer(name=sum)
		if sum_int is not None:
			tpl_sum.addKey(name='integer', data=sum_int )
		if sum_status is not None:
			tpl_sum.addKey(name='status', data=sum_status )
		tpl.addKey(name='checksum', data=tpl_sum )
	
	if data is not None:
		tpl_data = TestTemplatesLib.TemplateLayer(name=data)
		if data_size is not None:
			tpl_data.addKey(name='length', data=data_size )
		tpl.addKey(name='data', data=tpl_data )
		
	return tpl