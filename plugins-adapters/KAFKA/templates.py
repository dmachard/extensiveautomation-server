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
import json
# Template Layer file
CONSUMER="consumer"
PRODUCER="producer"

CONNECT = "connect"
CONSUME = "consum"
POSITION='position'
POLL="poll"
SEEK='seek'
ASSIGN='assign'
ASSIGNMENT='assignment'
SEEK_TO_BEGINNING="seek_to_beginning"
SEEK_TO_END="seek_to_end"
DISCONNECT="close" 
PARTITIONS_FOR="partitions_for"
HIGHWATER="highwater"
END_OFFSET="end_offset"
SUBSCRIBE="subscribe"
SUBSCRIPTION="subscription"
UNSUBSCRIBE="unsubscribe"
TOPICS="topics"
OFFSETS_FOR_TIMES="offsets_for_times"
PARTITIONS_FOR_TOPIC="partitions_for_topic"

def kafka_connect(api=None,bootstrap_servers=None, more=None, **kargs):
	"""
	Construct a kafka template Layer
	"""
	if api is CONSUMER: 
		layer_kafka= TestTemplatesLib.TemplateLayer(name='KAFKA_CONSUMER')
	else:
		layer_kafka = TestTemplatesLib.TemplateLayer(name='KAFKA_PRODUCER')
	
	if bootstrap_servers is not None: 
		layer_kafka.addKey(name='bootstrap_servers', data="%s" % bootstrap_servers )

	if more is not None:
		layer_kafka.addMore(more=more)
	if kargs is not None:
		for key,value in kargs.iteritems():
				if value is not None:
					layer_kafka.addKey(name=key, data="{0}".format(value))
	return layer_kafka
	

def kafka_ops(method=None, more=None, **kargs):
	"""
	Construct a kafka operation template Layer
	"""
	tpl = TestTemplatesLib.TemplateLayer(name=method.upper())
	if more is not None:
		tpl.addMore(more=more)
	if method is CONSUME:
		tpl = consumed_record(tpl=tpl,msg=kargs.pop('msg'))
	else:
		if kargs is not None:
			for key,value in kargs.iteritems():
				if value is not None:
					tpl.addKey(name=key, data="{0}".format(value))		
	return tpl 	

def response_err(method=None,msg=None, **kargs):
	"""
		Construct a kafka error template Layer
	"""
	tpl = kafka_ops(method=method)
	if msg is not None:
		tpl.addRaw( "%s" % msg)
	if kargs is not None:
		for key,value in kargs.iteritems():
			if value is not None:
				tpl.addKey(name=key, data="{0}".format(value))
	return tpl
