#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
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

import getopt
import sys
import os
import urllib
import shutil


import suds
from suds.client import Client
from suds.cache import NoCache

TPL_INIT = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2015 Denis Machard
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

%s

__DESCRIPTION__ = "%s"

__HELPER__ = [ %s ]
"""

TPL_LIB = """#!/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2015
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

AdapterSOAP = sys.modules['SutAdapters.%%s.SOAP' %% TestAdapter.getVersion()]
AdapterIP = sys.modules['SutAdapters.%%s.IP' %% TestAdapter.getVersion()]
AdapterTCP = sys.modules['SutAdapters.%%s.TCP' %% TestAdapter.getVersion()]
AdapterSSL = sys.modules['SutAdapters.%%s.SSL' %% TestAdapter.getVersion()]
AdapterHTTP = sys.modules['SutAdapters.%%s.HTTP' %% TestAdapter.getVersion()]

__NAME__=\"\"\"%s\"\"\"

class %s(TestAdapter.Adapter):
	def __init__(self, parent, name=None, debug=False, shared=False, agentSupport=False, agent=None, 
				sslSupport=%s, bindIp='', bindPort=0, destinationIp='%s', destinationPort=%s,
				xmlns0='%s', httpAuthentication=False, httpLogin='', httpPassword='',
				xmlns1='http://schemas.xmlsoap.org/soap/envelope/',
				xmlns2='http://www.w3.org/2003/05/soap-envelope', 
				xmlns3='http://www.w3.org/2001/XMLSchema-instance', xmlns7='', xmlns8='',
				xmlns4='http://www.w3.org/2001/XMLSchema', xmlns5='http://www.w3.org/XML/1998/namespace', xmlns6='', destUri='%s',
				proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False, proxyType=AdapterTCP.PROXY_HTTP):
		\"\"\"
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
		\"\"\"
		TestAdapter.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name)
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.cfg = {}
		self.cfg['local-wsdl'] = '%%s/%%s/%%s' %% (TestAdapter.getMainPath(), TestAdapter.getVersion(), '%s')
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
			self.LIB_SUDS = Client("file://%%s" %% self.cfg['local-wsdl'], nosend=True, cache=NoCache())
		except Exception as e:
			raise Exception("Unable to load the wsdl file: %%s" %% e)
		self.__checkConfig()

	def __checkConfig(self):	
		\"\"\"
		Private function
		\"\"\"
		self.debug(self.cfg)	
	
	def onReset(self):
		\"\"\"
		Called automatically on reset adapter
		\"\"\"
		pass

	def connect(self):
		\"\"\"
		Connect the remote api
		\"\"\"
		self.ADP_SOAP.connect()

	def addSoapHeaders(self, soapheaders):
		\"\"\"
		The soap headers to be included in the soap message. 

		@param soapheaders: soap header to include
		@type soapheaders: soapheaders
		\"\"\"
		self.LIB_SUDS.set_options(soapheaders=soapheaders)

	def addWsse(self, username, password, nonce=False, create=False):
		\"\"\"
		Add WS-Security

		@param username: username
		@type username: string

		@param password: password
		@type password: string

		@param nonce: add nonce element (default=False)
		@type nonce: boolean

		@param create: add create element (default=False)
		@type create: boolean
		\"\"\"
		security = Security()
		token = UsernameToken(username, password)
		if nonce: token.setnonce()
		if create: token.setcreated()
		security.tokens.append(token)
		self.LIB_SUDS.set_options(wsse=security)

	def disconnect(self):
		\"\"\"
		Disconnect from the remote api
		\"\"\"
		self.ADP_SOAP.disconnect()

	def isConnected(self, timeout=1.0):
		\"\"\"
		is connected to the soap service

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float

		@return: event if connected
		@rtype:	template	
		\"\"\"
		return self.ADP_SOAP.isConnected(timeout=timeout)

	def isDisconnected(self, timeout=1.0):
		\"\"\"
		is disconnected from the soap service

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float

		@return: event if disconnected
		@rtype:	template	
		\"\"\"
		return self.ADP_SOAP.isDisconnected(timeout=timeout)

	def hasReceivedResponse(self, expected, timeout=1.0):
		\"\"\"
		Wait a generic response until the end of the timeout.
		
		@param expected: response template
		@type expected: templatemessage

		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		\"\"\"
		evt = self.ADP_SOAP.received( expected = expected, timeout = timeout )
		if evt is None:
			return None
		return evt

	def hasReceivedSoapResponse(self, httpCode="200", httpPhrase="OK", timeout=1.0):
		\"\"\"
		Wait soap response until the end of the timeout.
		
		@param httpCode: http code (default=200)
		@type httpCode: string
		
		@param httpPhrase: http phrase (default=OK)
		@type httpPhrase: string
		
		@param timeout: time to wait in seconds (default=1s)
		@type timeout: float
	
		@return: http response
		@rtype:	template	
		\"\"\"
		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer( AdapterIP.ip( more=AdapterIP.received() ) )
		tpl.addLayer( AdapterTCP.tcp(more=AdapterTCP.received()) )
		if self.ADP_SOAP.http().tcp.cfg['ssl-support']:
			tpl.addLayer( AdapterSSL.ssl(more=AdapterSSL.received()) )
		headers = {'content-type': TestOperators.Contains(needle='xml', AND=True, OR=False) }
		tpl.addLayer( AdapterHTTP.response( version="HTTP/1.1", code=httpCode, phrase=httpPhrase, headers=headers ) )
		tpl.addLayer( AdapterSOAP.body() )
		
		return self.hasReceivedResponse(expected=tpl, timeout=timeout)
%s

%s
"""


def prepare_wsdl(wsdlUrl, pkgVersion):
    """
    Prepare the wsdl
    Download-it if necessary
    """
    print("0. Preparing WSDL (%s)" % wsdlUrl)
    wsdlFile = "%s/../%s/wsdl.txt" % (Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ))
    
    if wsdlUrl.startswith("http://") or wsdlUrl.startswith("https://"):
        print("1. Downloading WSDL (%s)" % wsdlUrl)
        
        try:
            urllib.urlretrieve (wsdlUrl, wsdlFile)
        except Exception as e:
            print("ERROR: unable to download wsdl: %s" % e )
            sys.exit(1)
    else:
        try:
            shutil.copy(
                            wsdlUrl, 
                            wsdlFile
                        )
        except Exception as e:
            print("ERROR: unable to copy wsdl file: %s" % e )
            sys.exit(1)
            
    return  wsdlFile

def parse_portlocation(portlocation, https=False):
    """
    Parse the port location to extract the host and uri
    """
    # default returns values
    host = portlocation
    uri = ''
    
    # starts with value for the port location
    starts_with = "http://"
    if https: starts_with = "https://"
    
    # extract the host and uri
    tmpport = portlocation.split(starts_with, 1)
    if len(tmpport) == 2:
        tmpret = tmpport[1].split('/', 1)
        if len(tmpret) == 2: 
            host, uri = tmpret

    return (host, uri)
    
def read_wsdl(wsdlFile):
    """
    Read wsdl
    """
    # construct the client with wsdl
    print("1. Reading WSDL")
    try:
        client = Client("file://%s" % wsdlFile, nosend=False, cache=NoCache())
        sdList = client.sd # all service definition
    except Exception as e:
        print("ERROR: unable to read wsdl: %s" % e)
        sys.exit(1)
    else:
        adaptersName = []
        complexList = {}
        for sd in sdList:
            adps = {}
            adps['name'] = sd.service.name
            adps['namespaces'] = sd.prefixes
            adps['adapters'] = []

            for p in sd.ports:
                adp = {}
                portLocation = p[0].location

                adp['ssl'] = False
                if portLocation.startswith("https://"):  adp['ssl'] = True
                
                host, uri = parse_portlocation(portlocation=portLocation, https=adp['ssl'])
                adp['host'] = host
                adp['uri'] = '/%s' % uri
                
                adp['host-port'] = 80
                if adp['ssl']: adp['host-port'] = 443
                destPort = adp['host'].split(':')
                if len(destPort) == 2: adp['host-port'] = destPort[1]

                __adpname = p[0].name
                adp['name'] = __adpname.replace("-", "")
                adp['methods'] = []

                for m in p[1]:
                    method = {}
                    method['name'] = m[0]
                    method['args'] = []

                    for a in m[1]:
                        arg = {}
                        argType =  a[1].resolve().name
                        
                        # simple type arg (string, bool, int, double, long)
                        if argType in ["string", "boolean", "int", "double", "long", "base64Binary", 
                                        "dateTime", "nonNegativeInteger" ]:
                            if a[1].required(): arg['expected'] = 'required'
                            else: arg['expected'] = 'optional'

                            arg['name'] = a[0]
                            if argType == "double": arg['type'] = "float"
                            else: arg['type'] = argType
                        else:
                        
                            # advanced arg ? (restriction, .... )
                            if a[1].restriction():
                                values = a[1].rawchildren[0].content()
                                vType = values[1].resolve().ref[0]

                                l = []
                                for v in values:
                                    if v.resolve().name is not None:
                                        l.append(v.resolve().name)

                                if vType in ["string", "boolean", "int", "double", "long", "base64Binary", 
                                                "dateTime", "nonNegativeInteger" ]:
                                    arg['name'] = a[0]
                                    arg['type'] = vType
                                    if vType == "double": arg['type'] = "float"
                                    else:arg['type'] = vType
                                    
                                    arg['value'] = l

                                    if a[1].required(): arg['expected'] = 'required'
                                    else: arg['expected'] = 'optional'
                                else:
                                    print('arg - restriction - not yet implemented: %s' % vType)
                                    
                            elif a[1].sequence():   
                                print('arg - sequence - not yet implemented: %s' % vType)
                            elif a[1].xslist():   
                                print('arg - xslist - not yet implemented: %s' % vType)
                            elif a[1].choice():   
                                print('arg - choice - not yet implemented: %s' % vType)
                            elif a[1].all():   
                                print('arg - all - not yet implemented: %s' % vType)
                            elif a[1].any():   
                                print('arg - any - not yet implemented: %s' % vType)
                            elif a[1].builtin():   
                                print('arg - builtin - not yet implemented: %s' % vType)
                            elif a[1].enum():   
                                print('arg - enum - not yet implemented: %s' % vType)
                            elif a[1].extension():   
                                print('arg - extension - not yet implemented: %s' % vType)
                            elif a[1].restriction():   
                                print('arg - restriction - not yet implemented: %s' % vType) 
                            elif a[1].isattr():   
                                print('arg - isattr - not yet implemented: %s' % vType)  
                            elif a[1].mixed():   
                                print('arg - mixed - not yet implemented: %s' % vType)   

                            else:
                            
                                # complex arg ?
                                complex = get_type(sd=sd, type_name=argType)
                                if not len(complex):
                                    print('complex arg not yet implemented: %s' % argType)
                                else:
                                    arg['name'] = a[0]
                                    arg['type'] = argType
                                    if a[1].required(): arg['expected'] = 'required'
                                    else: arg['expected'] = 'optional'
                                    
                                    if complex['name'] not in complexList:
                                        if 'args' in complex:
                                            complexList[complex['name']] = complex['args']
                                        
                                    for carg in complex['args']:
                                        if carg['type'] not in ['string', 'boolean', 'int', 'double', 'long', "base64Binary",
                                                                    "dateTime", "nonNegativeInteger" ]:
                                            complex2 = get_type(sd=sd, type_name=carg['type'])
                                            if not len(complex2):
                                                print('complex-2 arg not yet implemented: %s' % carg['type'])
                                            else:
                                                if complex2['name'] not in complexList:
                                                    if 'args' in complex2:
                                                        complexList[complex2['name']] = complex2['args']
                                                    
                        if len(arg):
                            method['args'].append( arg )
                            
                    adp['methods'].append( method )
                print("\tnb methods detected: %s" % len(adp['methods']) )  
                print("\tnb complex type detected: %s" % len(complexList) )  
                adps['adapters'].append( adp )
                
            adaptersName.append( adps )
        
        return (adaptersName, complexList)
        
def get_type(sd, type_name):
    """
    get type from xsd
    """
    ret = {}
    
    for t in sd.types:
        typeName = t[1].resolve().name
        if type_name == typeName:
            # [<Sequence:0x2f4dd10 />]
            ret['name'] = typeName
            values = t[1].rawchildren[0].content()
            for v in values:
                if v.sequence():
                    ret['args'] = []
                    for s in v.rawchildren:
                        # <Element:0x28665d0 name="recurrenceId" type="(u'string', u'http://www.w3.org/2001/XMLSchema')" />
                        if isinstance(s, suds.xsd.sxbasic.Any):
                            continue
                        subret = { 'name':s.name }
                        subret['type'] = s.type[0]
                        subret['min'] = s.min
                        subret['max'] = s.max
                        ret['args'].append( subret)
                else:
                    pass
    return ret
    
# def getDateValue(self, _strValue, _strFormat, _oDefaultValue):
    # if _strValue is None or _strValue == "None":
        # oReturnValue = _oDefaultValue
    # else:
        # oReturnValue = DateTime(datetime.datetime.strptime(_strValue, _strFormat))
    # return oReturnValue
        
# def get_type(sd, type_name):
    # """
    # """
    # for t in sd.types:
        # typeName = t[1].resolve().name
        # print(typeName)
        # if type_name == typeName:
            # test = client.factory.create(t[1].resolve().name)
            # print(type_name)
            # print( test.__keylist__ )
    
def construct_adapter(adaptersName, complexList, wsdlFile, overwrite=False):
    """
    Construct the adapter
    """
    # create the adapter
    if len(adaptersName):
        print("2. Adding adapter")
        # checking pkg version
        repoAdps = '%s/../%s/%s/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'adapters' ), pkgVersion )
        if not os.path.exists( repoAdps ):
            print("ERROR: packages %s does not exists" % pkgVersion)
            sys.exit(2)

        for adps in adaptersName:
            # create the main dir
            if not overwrite:
                if os.path.exists( "%s/%s" % (repoAdps, adps['name']) ):
                    print("ERROR: package %s already exists" % adps['name'])
                    sys.exit(3)
            try:
                os.mkdir( "%s/%s" % (repoAdps, adps['name']) )
            except Exception as e:
                if not overwrite:
                    print("ERROR: unable to create folder - %s" % e)
                    sys.exit(3)
                    
            # move the wsdl file
            shutil.move(
                        wsdlFile, 
                        "%s/%s/wsdl.txt" % (repoAdps, adps['name'])
                        )
            
            # create all other lib
            s = []
            s2 = []
            for adp in adps['adapters']:
                s.append( "from %s import *" % adp['name'].lower() )

                # list complex type
                t = []
                t2 = []
                for kt, vt in complexList.items():
                    t2.append( "\"type_%s\"" % kt )
                    at = []
                    atdoc = []
                    ta = []
                    for targ in vt:
                        if targ['type'] == "long":
                            ta.append( "\t\tif %s is not None: obj.%s = long(%s)" % (targ['name'], targ['name'], targ['name']) )
                        else:
                            ta.append( "\t\tif %s is not None: obj.%s = %s" % (targ['name'], targ['name'], targ['name']) )
                            
                        at.append( "%s=None" % targ['name'] )
                        targ_descr = targ['type']
                        if targ['max'] == 'unbounded':  targ_descr = "list of %s" % targ_descr
                        atdoc.append("""
		@param %s: %s
		@type %s: %s/none""" % (targ['name'], targ['name'], targ['name'], targ_descr ) )
                    ta.append( "\t\treturn obj" )
                    t.append( """
	def type_%s(self, %s ):
		\"\"\"
		Get %s complex type
%s

		@return: complex type
		@rtype:	object
		\"\"\"
		obj = self.LIB_SUDS.factory.create(%s)
%s""" % (
                                                        kt,
                                                        ', '.join(at),
                                                        kt,
                                                        '\n'.join(atdoc),
                                                        kt,
                                                        '\n'.join(ta)
                                                    ) 
                    )
                    
                # list methods
                m = []
                m2 = []
                for mt in adp['methods']:
                    m2.append( "\"%s\"" % mt['name'] )
                    
                    a = [] # mandatory args
                    a2 = []
                    o = [] # optional args
                    o2 = []
                    adoc = []
                    for arg in mt['args']:
                        if arg['expected'] == 'required':
                            a.append( "%s" % arg['name'] )
                            if arg['type'] == "long":
                                a2.append( "%s=long(%s)" % (arg['name'],arg['name']) )
                            else:
                                a2.append( "%s=%s" % (arg['name'],arg['name']) )
                        else:
                            o.append( "%s=None" % arg['name'] )
                            if arg['type'] == "long":
                                o2.append( """
			if %s is not None: kargs['%s'] = long(%s)""" % (arg['name'], arg['name'], arg['name']) )
                            else:
                                o2.append( """
			if %s is not None: kargs['%s'] = %s""" % (arg['name'], arg['name'], arg['name']) )
                            
                        pdescr = arg['name']
                        if 'value' in arg: pdescr = "%s" % '|'.join(arg['value'])
                        tdescr = arg['type']
                        if arg['expected'] == 'optional': tdescr = '%s/none' % arg['type']
                        
                        adoc.append("""
		@param %s: %s
		@type %s: %s""" % (arg['name'], pdescr, arg['name'], tdescr ) )
        
                    o.append(" httpHeaders={}")
                    
                    fargs = ', '.join(a2)
                    if len(a2): fargs += ', '
                    m.append( """
	def %s(self, %s ):
		\"\"\"
		%s function
%s

		@param httpHeaders: http headers to add
		@type httpHeaders: dict
		\"\"\"
		try:
			kargs = {}
			%s
			ret = self.LIB_SUDS.service.%s(%s **kargs)
			env = ret.envelope
		except Exception as e:
			raise Exception("unable to prepare soap request: %%s" %% e)
		self.ADP_SOAP.sendSoap(uri=self.cfg['uri'], host=self.cfg['host'], soap=env, httpHeaders=httpHeaders, login=self.cfg['http-login'], password=self.cfg['http-password'])""" % (
                                                                        mt['name'], ', '.join(a+o), 
                                                                        mt['name'],
                                                                        '\n'.join(adoc),
                                                                        ''.join(o2),
                                                                        mt['name'], fargs
                                                                       )
                                                                 )
            
                s2.append( "(\"%s\", [ \"__init__\", \"connect\", \"disconnect\", \"addSoapHeaders\", \"addWsse\", \
                \"isConnected\", \"isDisconnected\", \"hasReceivedSoapResponse\", %s, %s ])," % (adp['name'], ','.join(m2), ','.join(t2) ) )
                
                ns=''
                if len(adps['namespaces']):
                    ns_name, ns_value = adps['namespaces'][0]
                    ns = ns_value
                    
                # create lib file
                f = open( "%s/%s/%s.py" % (repoAdps, adps['name'], adp['name'].lower() ) , 'wb')
                f.write( TPL_LIB % (
                                    adp['name'].upper(), 
                                    adp['name'], 
                                    adp['ssl'],
                                    adp['host'],
                                    adp['host-port'],
                                    ns,
                                    adp['uri'],
                                    "/%s/wsdl.txt" % adps['name'] ,
                                    '\n\t'.join(m),
                                    '\n\t'.join(t) )
                      )
                f.close()
                        
            # create __init__ file
            f = open( "%s/%s/__init__.py" % (repoAdps, adps['name']) , 'wb')
            f.write( TPL_INIT % ('\n'.join(s), 'Adapters generated automatically from WSDL.', '\n'.join(s2))  )
            f.close()

def help():
    """
    Display help
    """
    print("./generate-wsdl-adapter --wsdl=<file> --pkg=<version>")
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", [ "wsdl=","pkg=","pathlib=", "overwrite"])
    except getopt.error, msg:
        print(msg)
        help()
        sys.exit(2)
    if len(opts) == 0:
        help()
        sys.exit(0)

    pkgVersion = None
    wsdlFile = None
    pathLib = None
    overwrite=False
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit(0)
        elif o in ["--wsdl"]:  
            wsdlFile = a
        elif o in ["--pkg"]:
            pkgVersion = a
        elif o in ["--pathlib"]:
            pathLib = a
        elif o in ["--overwrite"]:
            overwrite = True
            
    if pkgVersion is not None and wsdlFile is not None:

        if pathLib is not None:
            sys.path.insert(0, pathLib )
        else:
            sys.path.insert(0, '../' )
        from  Libs import Settings
        
        Settings.initialize(path="../")
        
        # download the wsdl
        wsdlFile = prepare_wsdl(wsdlFile, pkgVersion)
        
        # read the wsdl
        adapters, complexList = read_wsdl(wsdlFile=wsdlFile)
        
        # constructs library
        construct_adapter(adaptersName=adapters, complexList=complexList, wsdlFile=wsdlFile, overwrite=overwrite)
        
        Settings.finalize()
        sys.exit(0)
    else:
        help()
        sys.exit(0)