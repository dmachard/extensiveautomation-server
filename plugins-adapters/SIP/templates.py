#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# templates for sip client
def sip(more=None):
	"""
	Construct a template for a SIP packet
	"""
	tpl = TestTemplatesLib.TemplateLayer('SIP')

	# add additional keys
	if more is not None:
		tpl.addMore(more=more)
		
	return tpl

def request(method=None, uri=None, version=None, headers=None, body=None):
	"""
	Returns a template for SIP request
	
	@param method: 
	@type method: 
	
	@param uri: 
	@type uri: 
	
	@param version: 
	@type version: 
	
	@param headers: 
	@type headers: 
	
	@param body: 
	@type body: 
	
	@return: sip request
	@rtype: templatelayer
	"""
	tpl = sip()
	tpl.addKey(name='request', data=request_head(method=method,uri=uri,version=version) )
	if headers is not None:
		tpl.addKey(name='headers', data=sip_headers(headers=headers) )
	if body is not None:
		if len(body) > 1:
			tpl.addKey(name='body', data=body)
	return tpl

def status(version=None, code=None, phrase=None, headers=None, body=None):
	"""
	Returns a template for SIP status response

	@param version: 
	@type version: 
	
	@param code: 
	@type code: 
	
	@param phrase: 
	@type phrase: 
	
	@param headers: 
	@type headers: 
	
	@param body: 
	@type body: 
	
	@return: sip response
	@rtype: templatelayer
	"""
	tpl = sip()
	tpl.addKey(name='status', data=status_head(version=version,code=code,phrase=phrase) )
	if headers is not None:
		tpl.addKey(name='headers', data=sip_headers(headers=headers) )
	if body is not None:
		if len(body) > 1:
			tpl.addKey(name='body', data=body)
	return tpl

def request_head(method=None, uri=None, version=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	if method is not None:
		tpl.addKey(name='method', data=method)
	if uri is not None:
		tpl.addKey(name='uri', data=uri)
	if version is not None:
		tpl.addKey(name='version', data=version)	
	return tpl

def status_head(version=None, code=None, phrase=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	if version is not None:
		tpl.addKey(name='version', data=version)
	if code is not None:
		tpl.addKey(name='code', data=code)
	if phrase is not None:
		tpl.addKey(name='phrase', data=phrase)	
	return tpl
	
def sip_headers(headers=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	# add additional keys
	if headers is not None:
		tpl.addMore(more=headers)
	return tpl

# templates for sip phone
def sip_phone(more=None):
	"""
	Construct a template for a SIP PHONE event
	"""
	tpl = TestTemplatesLib.TemplateMessage()
	
	layer_sipphone = TestTemplatesLib.TemplateLayer('SIP-PHONE')

	# add additional keys
	if more is not None:
		layer_sipphone.addMore(more=more)
	tpl.addLayer(layer=layer_sipphone)	
	return tpl

def registration(expire=None, login=None, password=None):
	tpl = { 'phone-event': 'registering' }
	if expire is not None:
		tpl['expire'] = expire
	if login is not None:
		tpl['login'] = login
	if password is not None:
		tpl['password'] = password
	return sip_phone(more=tpl)
	
def unregistration():
	tpl = { 'phone-event': 'unregistering' }
	return sip_phone(more=tpl)
	
def registered(expire=None):
	tpl = { 'phone-event': 'registered' }
	if expire is not None:
		tpl['expire'] = expire
	return sip_phone(more=tpl)

def unregistered():
	tpl = { 'phone-event': 'unregistered' }
	return sip_phone(more=tpl)

def registration_timeout():
	tpl = { 'phone-event': 'registration-timeout' }
	return sip_phone(more=tpl)

def outgoingcall(sessid=None):
	tpl = { 'phone-event': 'outgoing-call' }
	if sessid is not None:
		tpl['session-id'] = sessid
	return sip_phone(more=tpl)
def incomingcall(sessid=None, cli=None, display=None, diversion=None, assertedidentity=None):
	tpl = { 'phone-event': 'incoming-call' }
	if sessid is not None:
		tpl['session-id'] = sessid
	if cli is not None:
		tpl['cli'] = cli
	if display is not None:
		tpl['display'] = display
	if diversion is not None:
		tpl['diversion'] = diversion
	if assertedidentity is not None:
		tpl['asserted-identity'] = assertedidentity
	return sip_phone(more=tpl)
def hangupcall(sessid=None):
	tpl = { 'phone-event': 'hangup-call' }
	if sessid is not None:
		tpl['session-id'] = sessid
	return sip_phone(more=tpl)
def ringing(sessid=None):
	tpl = { 'phone-event': 'ringing' }
	if sessid is not None:
		tpl['session-id'] = sessid
	return sip_phone(more=tpl)
def ringback_tone(sessid=None):
	tpl = { 'phone-event': 'ringback-tone' }
	if sessid is not None:
		tpl['session-id'] = sessid
	return sip_phone(more=tpl)
def unexpected_response(sessid=None, state=None, code=None, phrase=None):
	tpl = { 'phone-event': 'unexpected-response' }
	if sessid is not None:
		tpl['session-id'] = sessid
	if state is not None:
		tpl['state'] = state
	if code is not None:
		tpl['code-received'] = code
	if phrase is not None:
		tpl['phrase-received'] = phrase	
	return sip_phone(more=tpl)


def call_connected(sessid=None):
	tpl = { 'phone-event': 'call-connected' }
	if sessid is not None:
		tpl['session-id'] = sessid
	return sip_phone(more=tpl)
def call_connection_timeout(sessid=None):
	tpl = { 'phone-event': 'call-connected-timeout' }
	if sessid is not None:
		tpl['session-id'] = sessid
	return sip_phone(more=tpl)
def call_disconnected(sessid=None, reason=None, by=None):
	tpl = { 'phone-event': 'call-disconnected' }
	if sessid is not None:
		tpl['session-id'] = sessid
	if reason is not None:
		tpl['reason'] = reason
	if by is not None:
		tpl['disconnected-by'] = by
	return sip_phone(more=tpl)
def call_cancelled(sessid=None, by=None):
	tpl = { 'phone-event': 'call-cancelled' }
	if sessid is not None:
		tpl['session-id'] = sessid
	if by is not None:
		tpl['cancelled-by'] = by
	return sip_phone(more=tpl)
def call_rejected(sessid=None, reason=None):
	tpl = { 'phone-event': 'call-rejected' }
	if sessid is not None:
		tpl['session-id'] = sessid
	if reason is not None:
		tpl['reason'] = reason
	return sip_phone(more=tpl)