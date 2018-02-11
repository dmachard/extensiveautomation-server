#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

import templates

DECODING_OK_CONTINUE = 3
DECODING_NOTHING_TODO = 2
DECODING_NEED_MORE_DATA = 1
DECODING_OK = 0

class Codec(object):
	def __init__(self, parent, truncateBody=False, strictMode=False, websocketMode=False,
												octetStreamSupport=False, manStreamSupport=False):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info
		self.sep = '\r\n'
		self.truncateBody = truncateBody
		self.strictMode = strictMode
		self.websocketMode = websocketMode
		self.octetStreamSupport = octetStreamSupport
		self.manStreamSupport = manStreamSupport

	def encode(self, http, request=True):
		"""
		Try to encode a payload to an octetstring.
		"""

		# first line encoding		
		ret = []
		
		if request:
			head_req = http.get('request')
			method = head_req.get('method')
			uri = head_req.get('uri')
			ver = head_req.get('version')
			
			summary = u'%s %s %s' % (method, uri, ver)
			ret.append( summary )
		else:
			head_rsp = http.get('response')
			version = head_rsp.get('version')
			code = head_rsp.get('code')
			phrase = head_rsp.get('phrase')
			
			summary = u'%s %s %s' % (version, code, phrase)
			ret.append( summary )
			
		# headers encoding
		headers = http.get('headers')
		contentType = None
		for key, val in headers.getItems():
			if val is None:
				continue
			# values are encoded as iso8859-1.
			if isinstance(val, TestTemplatesLib.TemplateLayer):	
				l = val.getItems()
				l.sort()
				for k, v in l:
					ret.append( '%s: %s' % ( key, v.encode('iso8859-1') )   )
			else:
				ret.append( '%s: %s' % ( key, val.encode('iso8859-1') )  )
			if key.lower() == 'content-type':
				contentType = val

		# body encoding
		body = http.get('body')
		if contentType is not None:
			# normalize content type
			ct = contentType.lower()
			if "charset=" in ct:
				charset = ct.split("charset=")[1]
				charset = charset.split(";", 1)[0].strip()
				charset = charset.replace("-", "")
				self.debug( "charset encoding for body: %s" % charset)
				body = body.encode(charset)

		# adding carrier return
		ret.append( u'')

		# adding body if needed
		if body:
			ret.append(body)
		else:
			ret.append( u'')

		# concatenation
		retStr = []
		for l in ret:
			if isinstance(l, unicode):
				if l.lower().startswith("content-length"):
					 # recompute len body because of the encodage
					retStr.append( "content-length: %s" % len(body) )
				else:
					retStr.append( l.encode() )
			else:
				retStr.append(l)
				
		msg = self.sep.join(retStr)

		return ( msg, summary)
	
	def decode(self, rsp, nomoredata=False, request=False):
		"""
		Try to decode some data to a valid payload.
		"""
		if len(rsp) == 0 and nomoredata:
			return (DECODING_NOTHING_TODO, None, None, None)

		# strict mode for the separator between headers and body ?
		if '\r\n\r\n' not in rsp:
			if not self.strictMode:
				if '\n\r\n' in rsp:
					rsp = rsp.replace('\n\r\n', '\r\n\r\n' )
				
		bod = ''
		# split all headers
		hdrs = rsp.split(self.sep)

		# parse response code and phrase
		rspDecoded = hdrs[0].split(" ", 2)
		if len(rspDecoded) != 3:
			if request:
				self.debug('malformed http code request: %s' % rsp)
			else:
				self.debug('malformed http code response: %s' % rsp)
			return (DECODING_NEED_MORE_DATA, None, None, None)
		if request:
			httpMethod = rspDecoded[0]
			httpUri = rspDecoded[1]
			httpVersion = rspDecoded[2]
			summary = "%s %s %s" % (httpMethod, httpUri, httpVersion)
		else:
			httpVersion = rspDecoded[0]
			httpCode = rspDecoded[1]
			httpPhrase = (rspDecoded[2].decode("ISO8859-1")).encode("utf-8")
			summary = "%s %s %s" % (httpVersion, httpCode, httpPhrase)
	
		# parse hdrs to list
		http_body_detected = False
		content_type_hdr = None
		content_length_hdr = None
		transfer_encoding_hdr = None

		hdrs_dict = {}
		i = 1
		for hdr in hdrs[1:]: 
			i += 1
			h = hdr.strip() # remove spaces before and after
			if not hdr:
				http_body_detected = True
				break # reached body and its empty line
				
			fv = hdr.split(':', 1)
			if len(fv) != 2:
				raise Exception('invalid http headers: %s' % fv )
			# rfc 2616: Field names are case-insensitive
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

		if not http_body_detected:
			self.debug("body not detected")
			return (DECODING_NEED_MORE_DATA, None, None, None)
		

		# transfer-encoding header is present ?
		if transfer_encoding_hdr is not None:
			self.debug( "transfer encoding header detected (%s)" % str(transfer_encoding_hdr) )
			if transfer_encoding_hdr == 'chunked':
				try:
					if not hdrs[i].strip():
						self.debug("wait for the chunk size in a next payload" )
						return (DECODING_NEED_MORE_DATA, None, None, None) # Let's wait for the chunk size in a next payload

					chunkSize = int(hdrs[i].strip(), 16)
					self.debug("chunk size detected: %s" % chunkSize )
					remainingPayload = '\r\n'.join(hdrs[i+1:])

					# consuming chunk with thr exactly chunkSize characters then followed by an empty line or possibly another chunksize
					while chunkSize != 0:
						chunk = remainingPayload[:chunkSize]
						if len(chunk) < chunkSize:
							self.debug("current chunk (%s) lower than chunk size expected (%s), need more data" % ( len(chunk), chunkSize) )
							return (DECODING_NEED_MORE_DATA, None, None, None)
						bod += chunk

						remainingPayload = remainingPayload[chunkSize:]

						lines = remainingPayload.split('\r\n')  # ['', '0', '', '']
						if lines[0]:
							# should be an empty line... 
							raise Exception("No chunk boundary at the end of the chunk. Invalid data.")
						if not lines[1]:
							self.debug("No next chunk size yet" )
							return (DECODING_NEED_MORE_DATA, None, None, None) # No next chunk size yet
						else:
							chunkSize = int(lines[1].strip(), 16)
							self.debug("next chunk size detected: %s" % chunkSize )
						
						# fix issue, final chunk size received but crlf is missing
						if len(lines) <= 2:
							self.debug("next chunk size received but crlf is missing, waiting more data" )
							return (DECODING_NEED_MORE_DATA, None, None, None) # final chunk size received but crlf is missing
						# end of fix
						
						remainingPayload = '\r\n'.join(lines[2:])
				except IndexError:
					return (DECODING_NEED_MORE_DATA, None, None, None)
			else:
				raise Exception("not yet supported")
		
		# content-length header is present ?
		else:
			bod  ="\r\n".join(hdrs[i:])
			if content_length_hdr is not None:
				self.debug( "content-length header detected (%s)" % str(content_length_hdr) )
				cl = int(content_length_hdr)
				bl = len(bod)
				
				truncate_body = False
				if self.truncateBody:
					bod = '%s ...stream truncated....' % bod[:100]
					truncate_body = True

				if not ( truncate_body ):	
					if bl < cl:
						return (DECODING_NEED_MORE_DATA, None, None, None)
					elif bl > cl:
						# Truncate the body
						bod = bod[:cl]
			else:
				self.debug( "no transfer encoding header or content-length header" )
				
				if request:
					if http_body_detected and len(bod) == 0: 
						nomoredata = True

				# if the status code is 100 or 200 OK from a proxy, discard the first response and read the next one instead. 
				if len(hdrs) == 3 and len(bod) == 0:
					if len(hdrs[0]) and not len(hdrs[1]) and not len(hdrs[2]):
						self.debug('message with one line only detected, discard and read the next one')
						bod = ''
						nomoredata = True

				if self.websocketMode:
					self.debug( "websocket mode activated on codec" )
					if http_body_detected and len(bod) == 0: 
						nomoredata = True
				
				if not request:
					if http_body_detected and len(bod) == 0 and httpCode == "204": 
						self.debug('204 no content detected')
						bod = ''
						nomoredata = True
						
				# No chunk, no content-length, no body separator detected
				# wait until the end of the connection
				if not nomoredata:
					return (DECODING_NEED_MORE_DATA, None, None, None)

		# content-type header is present ?
		if content_type_hdr is not None:
			self.debug( "content type header detected (%s)" % str(content_type_hdr) )
			content_type = content_type_hdr.split(";", 1)[0] # split the type of data
			# update summary with content type
			summary = "%s (%s)" % (summary, content_type)
			
			# decode the body with the charset defined in the header content-type and re-encode to utf8
			if content_type == "text/html" or content_type == "text/plain" :
				if len(bod)> 0: # fix error in adapter 2.1.0, decode body only if the length > 0
					content_type_charset = content_type_hdr.split("charset=")
					if len(content_type_charset)==1:
						self.debug("Codec: charset is missing, decode body with iso-8859-1")
						content_type_charset = "iso-8859-1" 
					else:
						content_type_charset = content_type_hdr.split("charset=")[1].split(";", 1)[0]
					try:
						bod_decoded = bod.decode(content_type_charset)
						bod = bod_decoded.encode("utf-8")
					except Exception as e:
						self.warning('Codec: unable to decode body with charset: %s' % content_type_charset)

		# create template
		if request:
			ret = templates.request(method=httpMethod, uri=httpUri, version=httpVersion, headers=hdrs_dict, body=bod) 
		else:
			if not len(hdrs_dict):
				hdrs_dict = None
			if not len(bod):
				bod=None
			ret = templates.response(version=httpVersion, code=httpCode, phrase=httpPhrase, headers=hdrs_dict, body=bod) 
		if not request:
			if httpCode == "100":
				left_data = "\r\n".join(hdrs[i:])
				ret.addRaw(hdrs[0])
				return (DECODING_OK_CONTINUE, ret, summary, left_data ) 
		return (DECODING_OK, ret, summary, None)
