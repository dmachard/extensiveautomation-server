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
from TestExecutorLib.TestExecutorLib import doc_public

import sys

try:
	import templates
except ImportError: # python3 support
	from . import templates

# SSL support 
try:
    import ssl
except ImportError as x:
    print("error: %s" % x)

__NAME__="""SSL"""

#CERT_NONE - no certificates from the other side are required (or will
#be looked at if provided)
#CERT_OPTIONAL - certificates are not required, but if provided will be
#validated, and if validation fails, the connection will
#also fail
#CERT_REQUIRED - certificates are required, and will be validated, and
#if validation fails, the connection will also fail

CHECK_CERT_NO = 'No'
CHECK_CERT_OPTIONAL = 'Optional'
CHECK_CERT_REQUIRED = 'Required'

#client / server 	SSLv2 	SSLv3 	SSLv23 	TLSv1
#SSLv2 	yes 	no 	yes 	no
#SSLv3 	no 	yes 	yes 	no
#SSLv23 	yes 	no 	yes 	no
#TLSv1 	no 	no 	yes 	yes

SSLv2 = "SSLv2" 
SSLv23 = "SSLv23" 
SSLv3 = "SSLv3"
TLSv1 = "TLSv1"
TLSv11 = "TLSv11"
TLSv12 = "TLSv12"

class HandshakeFailed(Exception):
	pass
class HostnameFailed(Exception):
	pass

class Client(TestAdapterLib.Adapter):
	def __init__ (self, parent, sslVersion=SSLv23, checkCert=CHECK_CERT_NO, debug=False, name=None,
											logEventSent=True, logEventReceived=True, shared=False, caCerts=None, checkHost=False, 
											host=None, verbose=True, certfile=None,keyfile=None, clientCiphers=None):
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																									debug=debug, shared=shared, 
																									realname=name, showEvts=verbose, 
																									showSentEvts=verbose, showRecvEvts=verbose	)
		self.parent = parent
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		
		self.cfg = {}
		# ssl options
		self.cfg['ssl-version'] = sslVersion
		self.cfg['check-cert'] = checkCert
		self.cfg['ca-certs'] = caCerts
		self.cfg['check-host'] = checkHost
		self.cfg['host'] = host
		self.cfg['keyfile'] = keyfile
		self.cfg['certfile'] = certfile
		self.cfg['ciphers'] = clientCiphers
		
		self.sslCipher = ''
		self.sslVersion = ''
		self.sslBits = ''
		
		self.__checkConfig()

	def __checkConfig(self):
		"""
		"""
		self.debug("config: %s" % self.cfg)

	def encapsule(self, tpl, ssl_event):
		"""
		"""
		# prepare layers
		layer_ssl = templates.ssl(version=self.sslVersion)
		layer_ssl.addMore(more=ssl_event)
		
		# add layer to tpl
		tpl.addLayer(layer=layer_ssl)

		return tpl
		
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
				raise Exception('ssl init - version unknown: %s' % str(self.cfg['ssl-version']) )	
			
			# set cehck certificate option
			if self.cfg['check-cert'] == CHECK_CERT_NO:
				check = ssl.CERT_NONE
			elif self.cfg['check-cert'] == CHECK_CERT_OPTIONAL:
				check = ssl.CERT_OPTIONAL
			elif self.cfg['check-cert'] == CHECK_CERT_REQUIRED:
				check = ssl.CERT_REQUIRED				
			else:
				raise Exception('check certificate unknown: %s' % str(self.cfg['check-cert']) )
				
			self.sslVersion = self.cfg['ssl-version']
			if check == ssl.CERT_REQUIRED	and self.cfg['ca-certs'] is None:
				raise Exception("certificate required from the other side of the connection - no CA certificates")
				
			if sock is not None:
				# to support py2.6
				if sys.version_info >= (2,7):
					# disable sni feature
					_host = self.cfg['host']
					if not self.cfg['check-host']:
						_host = None
					# end
					sock = ssl.SSLSocket(
																							sock=sock, 
																							ca_certs=self.cfg['ca-certs'],
																							cert_reqs=check,
																							ssl_version=ver,
																							server_hostname=_host ,
																							keyfile=self.cfg['keyfile'],
																							certfile=self.cfg['certfile'],
																							ciphers=self.cfg['ciphers']
																			)
				else:
					sock = ssl.SSLSocket(
																							sock=sock, 
																							ca_certs=self.cfg['ca-certs'],
																							cert_reqs=check,
																							ssl_version=ver,
																							keyfile=self.cfg['keyfile'],
																							certfile=self.cfg['certfile']
																			)
		except Exception as e:
			raise Exception('SSL init failed: %s' % str(e))	
		return sock
	
	def finalizeSocketSsl(self, sock):
		"""
		"""
		self.debug( 'finalize ssl' )
		if sock is not None:
			sock.unwrap()
		
	def getPEMcert(self, DERcert):
		"""
		"""
		return ssl.DER_cert_to_PEM_cert(DERcert)
	
	def getSslError(self, err):
		"""
		enum py_ssl_error {
			/* these mirror ssl.h */
			PY_SSL_ERROR_NONE,                 
			PY_SSL_ERROR_SSL,                   
			PY_SSL_ERROR_WANT_READ,             
			PY_SSL_ERROR_WANT_WRITE,            
			PY_SSL_ERROR_WANT_X509_LOOKUP,      
			PY_SSL_ERROR_SYSCALL,     /* look at error stack/return value/errno */
			PY_SSL_ERROR_ZERO_RETURN,           
			PY_SSL_ERROR_WANT_CONNECT,
			/* start of non ssl.h errorcodes */ 
			PY_SSL_ERROR_EOF,         /* special case of SSL_ERROR_SYSCALL */
			PY_SSL_ERROR_INVALID_ERROR_CODE
		};		
		"""
		errMsg = ""
		try:
			sslError = err.split('SSL routines:')[1].split(':')[1]
			errMsg = sslError[:-2]
		except Exception as e:
			errMsg = str(err)
		return errMsg
		
	def logHandshake(self, tpl_s):
		"""
		"""
		self.sslVersion = self.cfg['ssl-version']
		
		# log sent event
		tpl = self.encapsule( tpl=tpl_s, ssl_event=templates.do_handshake(check_certificate=self.cfg['check-cert']) )
		self.logSentEvent( shortEvt = "handshake", tplEvt = tpl )
		
	def logHandshakeAccepted(self, tpl_r, cipher, version, bits, certpem ):
		"""
		"""
		self.sslCipher = cipher
		self.sslVersion = version
		self.sslBits = bits
		# log sent event
		tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_accepted(cipher=cipher,version=version,bits=bits, certPEM=certpem) )
		self.logRecvEvent( shortEvt = "handshake accepted", tplEvt = tpl )

	def logHandshakeFailed(self, tpl_r, err):
		"""
		"""
		# log sent event
		tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_failed(error=err) )
		self.logRecvEvent( shortEvt = "handshake failed", tplEvt = tpl )	
		
	def doSslHandshake(self, sock, tpl_s, tpl_r):
		"""
		Perform the SSL setup handshake.
		"""
		try:
			# log sent event
			self.logHandshake(tpl_s=tpl_s)
			self.debug( 'starting handshake ')
			
			# do handshake ssl
			sock.do_handshake()
			
			self.debug( 'handshake done')
			# extract ssl informations
			self.sslCipher, self.sslVersion, self.sslBits = sock.cipher()
			dercert = sock.getpeercert(True)

			# decode the certificate					 
			cert_svr_layer = TestTemplatesLib.TemplateLayer(name="")
			for k, v in sock.getpeercert().items():
				
				if isinstance(v, tuple):
					if k == "subject":
						cert_subject_layer = TestTemplatesLib.TemplateLayer(name="")
						for c in list(v):
							sk, sv = c[0]
							cert_subject_layer.addKey(name="%s" % str(sk), data ="%s" % str(sv) )
						cert_svr_layer.addKey(name="subject", data=cert_subject_layer)
				else:
					cert_svr_layer.addKey( name="%s" % k, data="%s" % str(v) )

			if self.cfg['check-host']:
				sub = cert_svr_layer.get("subject")
				if sub is not None:
					cn = sub.get("commonName")
					if cn is None: raise Exception('common name missing in peer certificate')
					if cn !=self.cfg['host']: raise HostnameFailed('Host name %s doesnt match certificate host %s' % (self.cfg['host'], cn) )
					
			if dercert is not None:
				certPEM = self.getPEMcert( dercert )
			else:
				certPEM = ''
			
			# log received event
			tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_accepted(cipher=self.sslCipher,version=self.sslVersion,
																bits=self.sslBits, certPEM=certPEM, cert=cert_svr_layer) )
			self.logRecvEvent( shortEvt = "handshake accepted", tplEvt = tpl )
		except ssl.SSLError as x:
			# log received event
			tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_failed(error=self.getSslError(str(x)) ) )
			self.logRecvEvent( shortEvt = "handshake failed", tplEvt = tpl )	
			
			# raise failure to parent
			raise HandshakeFailed()
		except HostnameFailed as x:
			# log received event
			tpl = self.encapsule( tpl=tpl_r, ssl_event=templates.handshake_failed(error=self.getSslError(str(x)) ) )
			self.logRecvEvent( shortEvt = "handshake failed", tplEvt = tpl )	
			
			# raise failure to parent
			raise HandshakeFailed()
		
	def onIncomingDecodedData(self, data, tpl):
		"""
		"""
		# log received event
		tpl = self.encapsule( tpl=tpl, ssl_event=templates.received(data=data) )
		if self.logEventReceived:
			tpl.addRaw(raw=data)
			self.logRecvEvent( shortEvt = "data", tplEvt = tpl )
		return 	tpl
	
	def sendData(self, decodedData, tpl):
		"""
		"""
		# log sent event
		if self.logEventSent:
			tpl = self.encapsule( tpl=tpl, ssl_event=templates.sent(data=decodedData) )
		else:
			tpl = self.encapsule( tpl=tpl, ssl_event=templates.sent() )
		
		if self.logEventSent:
			tpl.addRaw(raw=decodedData)
			self.logSentEvent( shortEvt = "data", tplEvt = tpl )
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
		
	def isConnected(self, tpl, timeout, sslVersion=None, sslCipher=None):
		"""
		@param timeout:
		@type timeout: 		
		"""
		# construct the expected template
		tpl_ssl = templates.handshake_accepted(version=sslVersion, cipher=sslCipher)
		expected = self.getExpectedTemplate( mainTpl=tpl, tpl=tpl_ssl)
		
		# try to match the template
		evt = self.received( expected = expected, timeout = timeout )
		return evt
		
	def hasReceivedData(self, tpl, timeout, data=None, sslVersion=None, sslCipher=None):
		"""
		"""
		# construct the expected template
		tpl_ssl = templates.received(data=data)
		expected = self.getExpectedTemplate( mainTpl=tpl, tpl=tpl_ssl )
		
		# try to match the template
		evt = self.received( expected = expected, timeout = timeout )
		return evt