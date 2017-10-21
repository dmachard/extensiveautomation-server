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

import templates

DECODING_OK_CONTINUE = 3
DECODING_NOTHING_TODO = 2
DECODING_NEED_MORE_DATA = 1
DECODING_OK = 0

class Codec(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info	
	
	def encode(self, sip_tpl):
		"""
		"""
		# detect the type of template: request or response ?
		if sip_tpl.get('request') is not None:
			return self.encode_req(sip_req=sip_tpl)
		elif sip_tpl.get('status') is not None:
			return self.encode_rsp(sip_rsp=sip_tpl)
		else:
			raise Exception('invalid sip template')
			
	def encode_req(self, sip_req):
		"""
		Try to encode a payload sip request to an octetstring.
		"""
		# first line encoding		
		ret = []
		head_req = sip_req.get('request')
		method = head_req.get('method')
		uri = head_req.get('uri')
		ver = head_req.get('version')
		
		summary = '%s %s %s' % (method, uri, ver)
		ret.append( '%s %s %s' % (method, uri, ver) )
		
		headers_req = sip_req.get('headers')
		content_type = headers_req.get('Content-Type', caseSensitive=False)
		if content_type is not None:
			summary += ' (%s)' % 	content_type
		

		# headers encoding
		for key, val in headers_req.getItems():
			if val is None:
				continue
			if isinstance(val, TestTemplatesLib.TemplateLayer):
				l = val.getItems()
				l.sort()
				for k,v in l:
					ret.append( '%s: %s' % ( key, v ) )
			else:		
				ret.append( '%s: %s' % ( key, val ) )
		
		# body encoding
		body_req = sip_req.get('body')
			
		# adding carrier return
		ret.append('')

		# adding body if needed
		if body_req:
			ret.append(body_req)
		else:
			ret.append('')

		# concatenation
		return ( '\r\n'.join(ret), summary)
		
	def encode_rsp(self, sip_rsp):
		"""
		Try to encode a payload sip response to an octetstring.
		"""
		# first line encoding		
		ret = []
		head_rsp = sip_rsp.get('status')
		code = head_rsp.get('code')
		phrase = head_rsp.get('phrase')
		version = head_rsp.get('version')
		
		summary = '%s %s' % (code,phrase)
		ret.append( '%s %s %s' % (version, code,phrase) )
		
		headers_req = sip_rsp.get('headers')
		content_type = headers_req.get('Content-Type', caseSensitive=False)
		if content_type is not None:
			summary += ' (%s)' % 	content_type

		# headers encoding
		for key, val in headers_req.getItems():
			if val is None:
				continue
			if isinstance(val, TestTemplatesLib.TemplateLayer):
				l = val.getItems()
				l.sort()
				for k, v in l:
					ret.append( '%s: %s' % ( key, v ) )
			else:
				ret.append( '%s: %s' % ( key, val ) )
		
		# body encoding
		body_rsp = sip_rsp.get('body')
			
		# adding carrier return
		ret.append('')

		# adding body if needed
		if body_rsp:
			ret.append(body_rsp)
		else:
			ret.append('')

		# concatenation
		return ( '\r\n'.join(ret), summary)
	
	def decode(self, sip, nomoredata=False):
		"""
		"""
		headline = sip.splitlines()[0]
		if headline.startswith('SIP/'):
			return self.decode_rsp(rsp=sip, nomoredata=nomoredata)
		else:
			return self.decode_req(req=sip, nomoredata=nomoredata)	
			
	def decode_req(self, req, nomoredata=False):
		"""
		Try to decode some data to a valid payload.
		"""
		if len(req) == 0 and nomoredata:
			return (DECODING_NOTHING_TODO, None, None, None)
			
		bod = ''
		# split all headers
		hdrs = req.split('\r\n')
		
		# parse response code and phrase
		reqDecoded = hdrs[0].split(" ", 2)
		if len(reqDecoded) != 3:
			raise Exception('malformed sip request: %s' % req)
		sipMethod = reqDecoded[0]
		sipUri = reqDecoded[1]
		sipVersion = reqDecoded[2]
		summary = "%s %s" % (sipMethod, sipUri)
	
		# parse hdrs to list
		sip_body_detected = False
		content_type_hdr = None
		content_length_hdr = None
		transfer_encoding_hdr = None

		hdrs_dict = {}
		i = 1
		for hdr in hdrs[1:]: 
			i += 1
			hv = hdr.strip() # remove spaces before and after
			if not hdr:
				sip_body_detected = True
				break # reached body and its empty line
			
			fv = hdr.split(':', 1)
			if len(fv) != 2:
				raise Exception('invalid sip headers in response')
			# rfc3261: field names are always case-insensitive.
			f = fv[0].lower().strip() # extract field and remove spaces
			v = fv[1].strip() # extract value and remove spaces
			
			if f == "content-type": content_type_hdr = v
			if f == "content-length": content_length_hdr = v
			if f == "transfer-encoding": transfer_encoding_hdr = v
			
			if hdrs_dict.has_key(f):
				if isinstance( hdrs_dict[f], TestTemplatesLib.TemplateLayer):
					tpl.addKey(name="%s" % tpl.getLenItems(), data=v )
				else:
					tpl = TestTemplatesLib.TemplateLayer('')
					tpl.addKey(name="%s" % tpl.getLenItems(), data=hdrs_dict[f])
					tpl.addKey(name="%s" % tpl.getLenItems(), data=v )
					hdrs_dict[f] = tpl
			else:
				hdrs_dict[f] = v
		
		if not sip_body_detected:
			return (DECODING_NEED_MORE_DATA, None, None, None)
			
		# transfer-encoding header is present ?
		if transfer_encoding_hdr is not None:
			self.debug( "transfer encoding header detected (%s)" % str(transfer_encoding_hdr) )
		
		# content-length header is present ?
		else:
			bod  ="\r\n".join(hdrs[i:])
			if content_length_hdr is not None:
				self.debug( "content-length header detected (%s)" % str(content_length_hdr) )
				cl = int(content_length_hdr)
				bl = len(bod)
				if bl < cl:
					return (DECODING_NEED_MORE_DATA, None, None, None)
				elif bl > cl:
					# Truncate the body
					bod = bod[:cl]
			else:
				self.debug( "no transfer encoding header or content-length header" )

				# no content-length: wait until the end of the connection
				if not nomoredata:
					return (DECODING_NEED_MORE_DATA, None, None, None)

		# content-type header is present ?
		if content_type_hdr is not None:
			content_type = content_type_hdr.split(";", 1)[0] # split the type of data
			# update summary with content type
			summary = "%s (%s)" % (summary, content_type)
			
			# decode the body with the charset defined in the header content-type and re-encode to utf8
			if content_type == "text/html" or content_type == "text/plain" :
				if len(bod)> 0:
					content_type_charset = content_type_hdr.split("charset=")
					if len(content_type_charset)==1:
						raise Exception("charset is mssing")
					else:
						content_type_charset = content_type_hdr.split("charset=")[1].split(";", 1)[0]
					try:
						bod_decoded = bod.decode(content_type_charset)
						bod = bod_decoded.encode("utf-8")
					except Exception as e:
						self.warning('Codec: decode body failed with charset: %s' % content_type_charset)

		# create template
		ret = templates.request(version=sipVersion, method=sipMethod, uri=sipUri, headers=hdrs_dict, body=bod) 
		left_data = "\r\n".join(hdrs[i:])
		if len(bod) == 0 and len(left_data)> 0:
			return (DECODING_OK_CONTINUE, ret, summary, left_data )
		else:		
			return (DECODING_OK, ret, summary, None)
		
	def decode_rsp(self, rsp, nomoredata=False):
		"""
		Try to decode some data to a valid payload.
		"""
		if len(rsp) == 0 and nomoredata:
			return (DECODING_NOTHING_TODO, None, None, None)
			
		bod = ''
		# split all headers
		hdrs = rsp.split('\r\n')
		
		# parse response code and phrase
		rspDecoded = hdrs[0].split(" ", 2)
		if len(rspDecoded) != 3:
			raise Exception('malformed sip response: %s' % rsp)
		sipVersion = rspDecoded[0]
		sipCode = rspDecoded[1]
		sipPhrase = rspDecoded[2]
		summary = "%s %s" % (sipCode, sipPhrase)
	
		# parse hdrs to list
		sip_body_detected = False
		content_type_hdr = None
		content_length_hdr = None
		transfer_encoding_hdr = None

		hdrs_dict = {}
		i = 1
		for hdr in hdrs[1:]: 
			i += 1
			h = hdr.strip() # remove spaces before and after
			if not hdr:
				sip_body_detected = True
				break # reached body and its empty line
			
			fv = hdr.split(':', 1)
			if len(fv) != 2:
				raise Exception('invalid sip headers in response')
			f = fv[0].lower().strip() # extract field and remove spaces
			v = fv[1].strip() # extract value and remove spaces
			
			if f == "content-type": content_type_hdr = v
			if f == "content-length": content_length_hdr = v
			if f == "transfer-encoding": transfer_encoding_hdr = v
			
			if hdrs_dict.has_key(f):
				if isinstance( hdrs_dict[f], TestTemplatesLib.TemplateLayer):
					tpl.addKey(name="%s" % tpl.getLenItems(), data=v )
				else:
					tpl = TestTemplatesLib.TemplateLayer('')
					tpl.addKey(name="%s" % tpl.getLenItems(), data=hdrs_dict[f])
					tpl.addKey(name="%s" % tpl.getLenItems(), data=v )
					hdrs_dict[f] = tpl
			else:
				hdrs_dict[f] = v
		
		if not sip_body_detected:
			return (DECODING_NEED_MORE_DATA, None, None, None)
			
		# transfer-encoding header is present ?
		if transfer_encoding_hdr is not None:
			self.debug( "transfer encoding header detected (%s)" % str(transfer_encoding_hdr) )
		
		# content-length header is present ?
		else:
			bod  ="\r\n".join(hdrs[i:])
			if content_length_hdr is not None:
				self.debug( "content-length header detected (%s)" % str(content_length_hdr) )
				cl = int(content_length_hdr)
				bl = len(bod)
				if bl < cl:
					return (DECODING_NEED_MORE_DATA, None, None, None)
				elif bl > cl:
					# Truncate the body
					bod = bod[:cl]
			else:
				self.debug( "no transfer encoding header or content-length header" )

				# no content-length: wait until the end of the connection
				if not nomoredata:
					return (DECODING_NEED_MORE_DATA, None, None, None)

		# content-type header is present ?
		if content_type_hdr is not None:
			content_type = content_type_hdr.split(";", 1)[0] # split the type of data
			# update summary with content type
			summary = "%s (%s)" % (summary, content_type)
			
			# decode the body with the charset defined in the header content-type and re-encode to utf8
			if content_type == "text/html" or content_type == "text/plain" :
				if len(bod)> 0:
					content_type_charset = content_type_hdr.split("charset=")
					if len(content_type_charset)==1:
						raise Exception("charset is mssing")
					else:
						content_type_charset = content_type_hdr.split("charset=")[1].split(";", 1)[0]
					try:
						bod_decoded = bod.decode(content_type_charset)
						bod = bod_decoded.encode("utf-8")
					except Exception as e:
						self.warning('Codec: decode body failed with charset: %s' % content_type_charset)

		# create template
		ret = templates.status(version=sipVersion, code=sipCode, phrase=sipPhrase, headers=hdrs_dict, body=bod) 
		left_data = "\r\n".join(hdrs[i:])
		if len(bod) == 0 and len(left_data)> 0:
			return (DECODING_OK_CONTINUE, ret, summary, left_data )
		else:		
			return (DECODING_OK, ret, summary, None)