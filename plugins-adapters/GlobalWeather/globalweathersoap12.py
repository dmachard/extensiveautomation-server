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
import base64

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

from suds.client import Client
from suds.cache import NoCache
from suds.sax.date import DateTime
from suds.wsse import Security
from suds.wsse import UsernameToken

AdapterSOAP = sys.modules['SutAdapters.%s.SOAP' % TestAdapter.getVersion()]
#AdapterIP = sys.modules['SutAdapters.%s.IP' % TestAdapter.getVersion()]
AdapterIP = sys.modules['SutAdapters.%s.IPLITE' % TestAdapter.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%s.TCP' % TestAdapter.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%s.SSL' % TestAdapter.getVersion()]
AdapterHTTP = sys.modules['SutAdapters.%s.HTTP' % TestAdapter.getVersion()]

__NAME__="""GLOBALWEATHERSOAP12"""

class GlobalWeatherSoap12(TestAdapter.Adapter):
	def __init__(self, parent, name=None, debug=False, shared=False, agentSupport=False, agent=None, 
				sslSupport=False, bindIp='', bindPort=0, destinationIp='www.webservicex.net', destinationPort=80,
				xmlns0='', httpAuthentication=False, httpLogin='', httpPassword='',
				xmlns1='http://schemas.xmlsoap.org/soap/envelope/',
				xmlns2='http://www.w3.org/2003/05/soap-envelope', 
				xmlns3='http://www.w3.org/2001/XMLSchema-instance', xmlns7='', xmlns8='',
				xmlns4='http://www.w3.org/2001/XMLSchema', xmlns5='http://www.w3.org/XML/1998/namespace', xmlns6='', destUri='/globalweather.asmx',
				proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False, proxyType=AdapterTCP.PROXY_HTTP):
		"""
		Adapter generated automatically from wsdl

		@param parent: parent testcase
		@type parent: testcase

		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean

		@param bindIp: bind ip (default='')
		@type bindIp: string

		@param bindPort: bind port (default=0)
		@type bindPort: integer

		@param destinationIp: destination ip (default=127.0.0.1)
		@type destinationIp: string

		@param destinationPort: destination port (default=80)
		@type destinationPort: integer

		@param xmlns0: xml namespace
		@type xmlns0: string

		@param xmlns1: xml namespace (default=http://schemas.xmlsoap.org/soap/envelope/)
		@type xmlns1: string
		
		@param xmlns2: xml namespace (defaut=http://www.w3.org/2003/05/soap-envelope)
		@type xmlns2: string
		
		@param xmlns3: xml namespace (default=http://www.w3.org/2001/XMLSchema-instance)
		@type xmlns3: string

		@param xmlns4: xml namespace (default=http://www.w3.org/2001/XMLSchema)
		@type xmlns4: string

		@param xmlns5: xml namespace (default=)
		@type xmlns5: string

		@param xmlns6: xml namespace (default=)
		@type xmlns6: string

		@param xmlns7: xml namespace (default=)
		@type xmlns7: string

		@param xmlns8: xml namespace (default=)
		@type xmlns8: string

		@param sslSupport: ssl support (default=False)
		@type sslSupport: boolean

		@param destUri: destination uri
		@type destUri: string

		@param proxyType: SutAdapters.TCP.PROXY_HTTP (default) | SutAdapters.TCP.PROXY_SOCKS4 | SutAdapters.TCP.PROXY_SOCKS5 
		@type proxyType: strconstant

		@param proxyIp: proxy ip
		@type proxyIp: string

		@param proxyPort: proxy port
		@type proxyPort: integer

		@param proxyHost: proxy host (automatic dns resolution)
		@type proxyHost: string

		@param proxyEnabled: True to support proxy (default=False)
		@type proxyEnabled: boolean	

		@param httpAuthentication: support http digest authentication (default=False)
		@type httpAuthentication: boolean

		@param httpLogin: login used on http digest authentication (default='')
		@type httpLogin: string
		
		@param httpPassword: password used on http digest authentication (default='')
		@type httpPassword: string

		@param agentSupport: agent support to use a remote socket (default=False)
		@type agentSupport: boolean

		@param agent: agent to use when this mode is activated
		@type agent: string/None
		"""
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		self.cfg['local-wsdl'] = '%s/%s/%s' % (TestAdapter.getMainPath(), TestAdapter.getVersion(), '/GlobalWeather/wsdl.txt')
		self.cfg['host'] = destinationIp
		self.cfg['uri'] = destUri
		self.cfg['http-login'] = httpLogin
		self.cfg['http-password'] = httpPassword
		self.ADP_SOAP = AdapterSOAP.Client(parent=parent, name=name, bindIp=bindIp, bindPort=bindPort, destinationIp=destinationIp,
										destinationPort=destinationPort, debug=debug, logEventSent=True, logEventReceived=True,
										xmlns0=xmlns0, xmlns1=xmlns1, xmlns2=xmlns2, xmlns7=xmlns7, xmlns8=xmlns8,
										xmlns3=xmlns3, xmlns4=xmlns4, xmlns5=xmlns5, xmlns6=xmlns6, httpAgent='ExtensiveTesting', 
										sslSupport=sslSupport, agentSupport=agentSupport, httpAuthentication=httpAuthentication,
										proxyIp=proxyIp, proxyPort=proxyPort, proxyHost=proxyHost, proxyEnabled=proxyEnabled, proxyType=proxyType,
										agent=agent, shared=shared)
		try:
			self.LIB_SUDS = Client("file://%s" % self.cfg['local-wsdl'], nosend=True, cache=NoCache())
		except Exception as e:
			raise Exception("Unable to load the wsdl file: %s" % e)
		self.__checkConfig()

	def __checkConfig(self):	
		"""
		Private function
		"""
		self.debug(self.cfg)	
	
	def onReset(self):
		"""
		Called automatically on reset adapter
		"""
		pass

	def connect(self):
		"""
		Connect the remote api
		"""
		self.ADP_SOAP.connect()

	def addSoapHeaders(self, soapheaders):
		"""
		The soap headers to be included in the soap message. 

		@param soapheaders: soap header to include
		@type soapheaders: soapheaders
		"""
		self.LIB_SUDS.set_options(soapheaders=soapheaders)

	def addWsse(self, username, password, nonce=False, create=False):
		"""
		Add WS-Security

		@param username: username
		@type username: string

		@param password: password
		@type password: string

		@param nonce: add nonce element (default=False)
		@type nonce: boolean

		@param create: add create element (default=False)
		@type create: boolean
		"""
		security = Security()
		token = UsernameToken(username, password)
		if nonce: token.setnonce()
		if create: token.setcreated()
		security.tokens.append(token)
		self.LIB_SUDS.set_options(wsse=security)

	def disconnect(self):
		"""
		Disconnect from the remote api
		"""
		self.ADP_SOAP.disconnect()

	def isConnected(self, timeout=1.0):
		"""
		is connected to the soap service

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float

		@return: event if connected
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_SOAP.isConnected(timeout=timeout)

	def isDisconnected(self, timeout=1.0):
		"""
		is disconnected from the soap service

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float

		@return: event if disconnected
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		return self.ADP_SOAP.isDisconnected(timeout=timeout)

	def hasReceivedResponse(self, expected, timeout=1.0):
		"""
		Wait a generic response until the end of the timeout.
		
		@param expected: response template
		@type expected: templatemessage

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		evt = self.ADP_SOAP.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt

	def hasReceivedSoapResponse(self, httpCode="200", httpPhrase="OK", timeout=1.0):
		"""
		Wait soap response until the end of the timeout.
		
		@param httpCode: http code (default=200)
		@type httpCode: string
		
		@param httpPhrase: http phrase (default=OK)
		@type httpPhrase: string
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapter.ValueException(TestAdapter.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		tpl = TestTemplates.TemplateMessage()
		
		if self.cfg['agent-support']:
			layer_agent= TestTemplates.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )
			tpl.addLayer( layer_agent )
			
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.ADP_SOAP.http().tcp.cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		headers = {'content-type': TestOperators.Contains(needle='xml', AND=True, OR=False) }
		tpl.addLayer( AdapterHTTP.response( version="HTTP/1.1", code=httpCode, phrase=httpPhrase, headers=headers ) )
		tpl.addLayer( AdapterSOAP.body() )
		
		return self.hasReceivedResponse(expected=tpl, timeout=timeout)

	def GetCitiesByCountry(self, CountryName=None,  httpHeaders={} ):
		"""
		GetCitiesByCountry function

		@param CountryName: CountryName
		@type CountryName: string/none

		@param httpHeaders: http headers to add
		@type httpHeaders: dict
		"""
		try:
			kargs = {}
			
			if CountryName is not None: kargs['CountryName'] = CountryName
			ret = self.LIB_SUDS.service.GetCitiesByCountry( **kargs)
			env = ret.envelope
		except Exception as e:
			raise Exception("unable to prepare soap request: %s" % e)
		self.ADP_SOAP.sendSoap(uri=self.cfg['uri'], host=self.cfg['host'], soap=env, httpHeaders=httpHeaders, login=self.cfg['http-login'], password=self.cfg['http-password'])
	
	def GetWeather(self, CityName=None, CountryName=None,  httpHeaders={} ):
		"""
		GetWeather function

		@param CityName: CityName
		@type CityName: string/none

		@param CountryName: CountryName
		@type CountryName: string/none

		@param httpHeaders: http headers to add
		@type httpHeaders: dict
		"""
		try:
			kargs = {}
			
			if CityName is not None: kargs['CityName'] = CityName
			if CountryName is not None: kargs['CountryName'] = CountryName
			ret = self.LIB_SUDS.service.GetWeather( **kargs)
			env = ret.envelope
		except Exception as e:
			raise Exception("unable to prepare soap request: %s" % e)
		self.ADP_SOAP.sendSoap(uri=self.cfg['uri'], host=self.cfg['host'], soap=env, httpHeaders=httpHeaders, login=self.cfg['http-login'], password=self.cfg['http-password'])


