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
from TestExecutorLib.TestExecutorLib import doc_public

import sys

import templates

import tempfile
# SSL support 
try:
    import ssl
except ImportError, x:
    print("error: %s" % x)

__NAME__="""SSL"""

SSLv2 = "SSLv2" 
SSLv23 = "SSLv23" 
SSLv3 = "SSLv3"
TLSv1 = "TLSv1"
TLSv11 = "TLSv11"
TLSv12 = "TLSv12"

CHECK_CERT_NO = 'No'
CHECK_CERT_OPTIONAL = 'Optional'
CHECK_CERT_REQUIRED = 'Required'

INTERNAL_CERT = """-----BEGIN CERTIFICATE-----
MIIC4TCCAkoCCQChbBI7Qc3YnDANBgkqhkiG9w0BAQUFADCBtDELMAkGA1UEBhMC
RlIxETAPBgNVBAgTCENhbHZhZG9zMQ0wCwYDVQQHEwRDYWVuMRowGAYDVQQKExFF
eHRlbnNpdmUgVGVzdGluZzEaMBgGA1UECxMRRXh0ZW5zaXZlIHRlc3RpbmcxHjAc
BgNVBAMTFWV4dGVuc2l2ZSB0ZXN0IGNlbnRlcjErMCkGCSqGSIb3DQEJARYcY29u
dGFjdEBleHRlbnNpdmV0ZXN0aW5nLm9yZzAeFw0xNDA2MjExMTA2MDZaFw0xNjA2
MjAxMTA2MDZaMIG0MQswCQYDVQQGEwJGUjERMA8GA1UECBMIQ2FsdmFkb3MxDTAL
BgNVBAcTBENhZW4xGjAYBgNVBAoTEUV4dGVuc2l2ZSBUZXN0aW5nMRowGAYDVQQL
ExFFeHRlbnNpdmUgdGVzdGluZzEeMBwGA1UEAxMVZXh0ZW5zaXZlIHRlc3QgY2Vu
dGVyMSswKQYJKoZIhvcNAQkBFhxjb250YWN0QGV4dGVuc2l2ZXRlc3Rpbmcub3Jn
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDKQ7xupVsm0o9Na235hTVYwLFy
PqEkqVLRpc87VyoNi1+DDNdegO2X6U08Ic+RPDyUxazfPJH6YL/43jdzDPa4o+4D
KQ1L4tcoM8JGB0dnEhkj68+AoQNKCyGqlKns0wgZr+VqlupW6rX8hJjBNOqWw1WX
JCgaNbxdJjS/ajSoEQIDAQABMA0GCSqGSIb3DQEBBQUAA4GBAIuu3AAIg12xXmw5
m2OI2ZwSrWPqXWwm7h0/uV2mAf9kTopw/T8fJGAAKbswI2LZ4yLwWTALfBJBidNl
S8efYnLYUqyUqoZfQZLlvY05fLmuF3eDS2AZUbSbUmOTm+dOQpB677ytk+1235fZ
WHlMLduUSPNThcAq//mZX95Q1IXa
-----END CERTIFICATE-----"""

INTERNAL_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDKQ7xupVsm0o9Na235hTVYwLFyPqEkqVLRpc87VyoNi1+DDNde
gO2X6U08Ic+RPDyUxazfPJH6YL/43jdzDPa4o+4DKQ1L4tcoM8JGB0dnEhkj68+A
oQNKCyGqlKns0wgZr+VqlupW6rX8hJjBNOqWw1WXJCgaNbxdJjS/ajSoEQIDAQAB
AoGAD0VV8LSjUScMkrfNsc0Q3gaOXyXDXNU734A5SS2niyY+q9JIYGYzigifQC79
UOXPXRwflSspilHLrKp6XUFZTy0U/Dfyoh7/ZG0nQDj8HLNYnPC/XQZ+W4HQFBWB
1+6vGJjqzeskQKfmEUPpoHX37CQSjNNEYwUwMixmD6+3bQECQQDjqk+0Ra85wHXY
spCWLv5QuQd7hZaJxX5nm8qfjeRM4uKY8LfkB9aTG5ecZQ2nRWjWdko1Hd6xagXc
8ehEoXoJAkEA43Ag4rsWeJVhnbd508tV82PSR4DfO7JpvdPMNwcOf5K66uftX17j
4ODnmTQYkSTChG3YHl6M+X9IWtcDjK7fyQJAFBQtO2T580n6GsaE4fn7C/uFoWtC
v5vfbhvbXv8Qp4dLHNn+HepjDk5crLps3dfNSzzbhpu/zD3hjn73UTY8oQJAP+Zo
BuvDg3uM4pADFYNikbBxCw/lKFOXK/NOxAMiiqtCAu/InGv/oFXwG/YsFNN8J1Lp
TpcICq09OfCBGcykKQJAC/rWo+ppYbDFs5f5NhR9/41gvXy2G56FLBpLswYBLlds
ydAE8Ki+hYqdM+Hd8M8kAeRt1HKIj9RUt5635HgIjg==
-----END RSA PRIVATE KEY-----"""

class HandshakeFailed(Exception):
	pass
	
class Server(TestAdapterLib.Adapter):
	def __init__ (self, parent, sslVersion=TLSv1, checkCert=CHECK_CERT_NO, debug=False, name=None,
											logEventSent=True, logEventReceived=True, shared=False):
		"""
		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param sslSupport: True to activate debug mode
		@type sslSupport: boolean

		@param debug: to activate debug mode
		@type debug: boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, shared=shared, realname=name)
		self.parent = parent
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.cfg = {}
		# ssl options
		self.cfg['ssl-version'] = sslVersion
		self.cfg['check-cert'] = checkCert
		self.cfg['cert'] = INTERNAL_CERT
		self.cfg['cert-file'] = "/tmp/cert.file"
		self.cfg['key'] = INTERNAL_KEY
		self.cfg['key-file'] = "/tmp/key.file"
		
		self.sslCipher = ''
		self.sslVersion = ''
		self.sslBits = ''

		try:
			f = open("/tmp/cert.file", 'w')
			f.write(self.cfg['cert'])
			f.close()
		except Exception as e:
			self.error( 'unable to write cert file: %s' % e)
			
		try:
			f = open("/tmp/key.file", 'w')
			f.write(self.cfg['key'])
			f.close()
		except Exception as e:
			self.error( 'unable to write temp key file: %s' % e)
			
		self.__checkConfig()

	def __checkConfig(self):
		"""
		"""
		self.debug("config: %s" % self.cfg)

	def encapsule(self, tpl, ssl_event):
		"""
		"""
		# prepare layers
		layer_ssl = templates.ssl(version=self.cfg['ssl-version'])
		layer_ssl.addMore(more=ssl_event)
		
		# add layer to tpl
		tpl.addLayer(layer=layer_ssl)

		return tpl

	def getPEMcert(self, DERcert):
		"""
		"""
		return ssl.DER_cert_to_PEM_cert(DERcert)

		
	def logDoHandshake(self, tpl_s, msg):
		"""
		"""
		# log sent event
		tpl = self.encapsule( tpl=tpl_s, ssl_event=templates.do_handshake(self.cfg['check-cert']) )
		self.logSentEvent( shortEvt = msg, tplEvt = tpl )

	def logHandshakeAccepted(self, tpl_r, msg ):
		"""
		"""
		# log sent event
		tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_accepted() )
		self.logRecvEvent( shortEvt = msg, tplEvt = tpl )

	def logHandshakeFailed(self, tpl_r, err, msg):
		"""
		"""
		# log sent event
		tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_failed(error=err) )
		self.logRecvEvent( shortEvt = msg, tplEvt = tpl )	
		
	def initSocketSsl(self, sock):
		"""
		"""
		try:
			# set ssl version
			self.debug( 'initialize ssl' )
			if  self.cfg['ssl-version'] == SSLv2:
				ver = ssl.PROTOCOL_SSLv2
			elif self.cfg['ssl-version'] == SSLv23:
				ver = ssl.PROTOCOL_SSLv23
			elif self.cfg['ssl-version'] == SSLv3:
				ver = ssl.PROTOCOL_SSLv3
			elif self.cfg['ssl-version'] == TLSv1:
				ver = ssl.PROTOCOL_TLSv1		
			elif self.cfg['ssl-version'] == TLSv11:
				ver = ssl.PROTOCOL_TLSv1_1 
			elif self.cfg['ssl-version'] == TLSv12:
				ver = ssl.PROTOCOL_TLSv1_2
			else:
				raise Exception('ssl version unknown: %s' % str(self.cfg['ssl-version']) )	
			
			if sock is not None:
				sock = ssl.wrap_socket(sock, server_side=True,  certfile = self.cfg['cert-file'],
																keyfile = self.cfg['key-file'],  ssl_version = ver)
				
				self.sslCipher, self.sslVersion, self.sslBits = sock.cipher()
				
				dercert = sock.getpeercert(True)
				if dercert is not None:
					certPEM = self.getPEMcert( dercert )
				else:
					certPEM = ''
		except Exception as e:
			raise Exception('SSL Server init failed: %s' % str(e))	
		return sock
	
	def finalizeSocketSsl(self, sock):
		"""
		"""
		self.debug( 'finalize ssl' )
		if sock is not None:
			sock.unwrap()

	def onIncomingDecodedData(self, data, tpl, msg):
		"""
		"""
		# log received event
		tpl = self.encapsule( tpl=tpl, ssl_event=templates.received(data=data) )
		if self.logEventReceived:
			tpl.addRaw(raw=data)
			self.logRecvEvent( shortEvt = msg,  tplEvt = tpl )
		return 	tpl
		
	def sendData(self, decodedData, tpl, msg):
		"""
		"""
		# log sent event
		if self.logEventSent:
			tpl = self.encapsule( tpl=tpl, ssl_event=templates.sent(data=decodedData) )
		else:
			tpl = self.encapsule( tpl=tpl, ssl_event=templates.sent() )
		
		if self.logEventSent:
			tpl.addRaw(raw=decodedData)
			self.logSentEvent( shortEvt = msg, tplEvt = tpl )
		return tpl

	def getExpectedTemplate(self, mainTpl, tpl):
		"""
		"""
		# prepare layers
		layer_ssl = templates.ssl()
		layer_ssl.addMore(more=tpl)

		# prepare template
		mainTpl.addLayer(layer=layer_ssl)
		return mainTpl
		
	def hasReceivedData(self, tpl, timeout, data=None, sslVersion=None, sslCipher=None):
		"""
		"""
		# construct the expected template
		tpl_ssl = templates.received(data=data)
		expected = self.getExpectedTemplate( mainTpl=tpl, tpl=tpl_ssl )
		
		# try to match the template
		evt = self.received( expected = expected, timeout = timeout )
		return evt