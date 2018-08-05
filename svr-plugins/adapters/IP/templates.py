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

def ip(   source=None, source_hex=None, destination=None, destination_hex=None,
        version=None, ihl=None, 
        tos=None, p=None, p_str=None, d=None, d_str=None, t=None, t_str=None, r=None, r_str=None,
        tl=None, id=None, 
        flg=None, flg_str=None, frg=None, ttl=None,
        pro=None, sum=None, sum_status=None, sum_int=None,
        data=None, data_size=None, more=None, pro_str=None):
	"""
	Construct a template for a ipv4 packet
	"""	
	tpl = TestTemplatesLib.TemplateLayer(name='IP4')
	
	# add keys
	if version is not None:
		tpl.addKey(name='version', data=version)
	if source is not None:
		tpl_src = TestTemplatesLib.TemplateLayer(name=source )
		if source_hex is not None:
			tpl_src.addKey(name='hex', data=source_hex )
		tpl.addKey(name='source-ip', data=tpl_src )
	if destination is not None:
		tpl_dst = TestTemplatesLib.TemplateLayer(name=destination )
		if destination_hex is not None:
			tpl_dst.addKey(name='hex', data=destination_hex )
		tpl.addKey(name='destination-ip', data=tpl_dst )
	
	# v4 fields
	if ihl is not None:
		tpl.addKey(name='header-length', data=ihl )
		
	if tos is not None:
		tpl_tos = TestTemplatesLib.TemplateLayer(name=str(tos) )
		if p is not None:
			tpl_p = TestTemplatesLib.TemplateLayer(name=str(p) )
			if p_str is not None:
				tpl_p.addKey(name='string', data=p_str )
			tpl_tos.addKey(name='precedence', data=tpl_p )
		if d is not None:
			tpl_d = TestTemplatesLib.TemplateLayer(name=str(d) )
			if d_str is not None:
				tpl_d.addKey(name='string', data=d_str )
			tpl_tos.addKey(name='delay', data=tpl_d )
		if t is not None:
			tpl_t = TestTemplatesLib.TemplateLayer(name=str(t) )
			if t_str is not None:
				tpl_t.addKey(name='string', data=t_str )
			tpl_tos.addKey(name='throughput', data=tpl_t )
		if r is not None:
			tpl_r = TestTemplatesLib.TemplateLayer(name=str(r) )
			if r_str is not None:
				tpl_r.addKey(name='string', data=r_str )
			tpl_tos.addKey(name='relibility', data=tpl_r )
		tpl.addKey(name='type-service', data=tpl_tos )	
		
	if tl is not None:
		tpl.addKey(name='total-length', data=tl )	
	if id is not None:
		tpl.addKey(name='identification', data=id )	
		
	if flg is not None:
		tpl_flg = TestTemplatesLib.TemplateLayer(name=flg )
		if flg_str is not None:
			tpl_flg.addKey(name='string', data=flg_str )
		tpl.addKey(name='flags', data=tpl_flg )	
		
	if frg is not None:
		tpl.addKey(name='fragment-offset', data=frg )	
	if ttl is not None:
		tpl.addKey(name='time-to-live', data=ttl )	
		
	if pro is not None:
		tpl_pro = TestTemplatesLib.TemplateLayer(name=str(pro) )
		if pro_str is not None:
			tpl_pro.addKey(name='string', data=pro_str )
		tpl.addKey(name='protocol', data=tpl_pro )

	if sum is not None:
		tpl_sum = TestTemplatesLib.TemplateLayer(name=sum)
		if sum_status is not None:
			tpl_sum.addKey(name='status', data=sum_status )
		if sum_int is not None:
			tpl_sum.addKey(name='integer', data=sum_int )
		tpl.addKey(name='checksum', data=tpl_sum )
		
	# set data upper
	if data is not None:
		tpl_data = TestTemplatesLib.TemplateLayer(name=data)
		if data_size is not None:
			tpl_data.addKey(name='length', data=data_size )
		tpl.addKey(name='data', data=tpl_data )
		
	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
	return tpl

def sent(data=None):
	"""
	Construct a template for IP outgoing packet
	"""
	tpl = { 'ip-event': 'sent' }
	if data is not None:
		tpl['ip-data'] = data
	return tpl	

def received(data=None):
	"""
	Construct a template for IP incoming packet
	"""
	tpl = { 'ip-event': 'received' }
	if data is not None:
		tpl['ip-data'] = data	
	return tpl
