#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import TestInteropLib
from TestInteropLib import doc_public

import requests
import json
import xml.etree.ElementTree as ET

class QualityCenter(TestInteropLib.InteropPlugin):
    """
    Quality Center plugin
    """
    @doc_public
    def __init__(self, parent, qcurl, username, password, domain, project, proxies={}, verifySsl=False):
        """
        HP ALM interop
        Support HP ALM from version 11.5 and more
        Sample on /Samples/Tests_Interop/02_HP_QC
        
        @param parent: testcase parent
        @type parent: testcase
        
        @param qcurl: hp alm url api
        @type qcurl: string
        
        @param username: qc login
        @type username: string
        
        @param password: qc password
        @type password: string
        
        @param domain: qc domain
        @type domain: string
        
        @param project: qc project
        @type project: string
        
        @param proxies: proxies to use {'http': '', 'https': ''}
        @type proxies: dict
        
        @param verifySsl: check ssl server cert (default=False)
        @type verifySsl: boolean
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        self.__qcurl = qcurl
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.__project = project
        self.__proxies = proxies
        self.__certCheck = verifySsl
        
        self.LWSSO_COOKIE_KEY = None
    @doc_public
    def signin(self):
        """
        Signin to QC

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        url = "%s/authentication-point/authenticate" % self.__qcurl
        
        # prepare template
        content = {'qc-url': url, 'cmd': 'sigin', "username":"%s" % self.__username, 
                    "domain": "%s" % self.__domain, "project": "%s" % self.__project }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="sigin", details=tpl )
        
        # make request
        try:
            r = requests.get(url,auth=(self.__username,self.__password), 
                                proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'signin' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="sigin error", details=tpl )
                
            # extract the cookie    
            else:
                cookies = r.headers["set-cookie"]
                self.LWSSO_COOKIE_KEY = cookies.split("LWSSO_COOKIE_KEY=")[1].split(";", 1)[0]
                
                content = {'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY, 'cmd': 'sign' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="logged", details=tpl )
                
                ret = True
        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "signin" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="signin exception", details=tpl )

        return ret
    @doc_public
    def signout(self):
        """
        Sigout from QC

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        # signin
        if self.LWSSO_COOKIE_KEY is None:
            return ret
            
        url = "%s/authentication-point/logout" % self.__qcurl

        # prepare template
        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY, 
                     'qc-url': url ,   'cmd': 'sigout' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="sigout", details=tpl )
        
        # make request
        try:
            r = requests.get(
                                url, 
                                proxies=self.__proxies, 
                                cookies={'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY},
                                verify=self.__certCheck
                            )
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'sigout' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="sigout error", details=tpl )
            else:
                content = {'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY, 'cmd': 'signout' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="log out", details=tpl )
                
                ret = True
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "signout" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="signout exception", details=tpl )
            
        return ret
    @doc_public        
    def createIssue(self, defectName, defectDescription, defectStatus, defectPriority, defectSeverity,
                        creationTime, detectedBy, cycleId, user01='', user02='', user03='', user04=''):
        """
        Create issue and return the associated Id
        
        @param defectName: defect name 
        @type defectName: string
        
        @param defectDescription: defect description
        @type defectDescription: string
        
        @param defectStatus: defect status
        @type defectStatus: string
        
        @param defectPriority: defect priority
        @type defectPriority: string
        
        @param defectSeverity: defect severity
        @type defectSeverity: string
        
        @param creationTime: creation time of the defect
        @type creationTime: string
        
        @param detectedBy: name of the author of the detection
        @type detectedBy: string
        
        @param cycleId: cycle id of attached to the defect
        @type cycleId: integer
        
        @param user01: additional user1 parameter
        @type user01: string
        
        @param user02: additional user2 parameter
        @type user02: string
        
        @param user03: additional user3 parameter
        @type user03: string
        
        @param user04: additional user4 parameter
        @type user04: string

        @return: defect id on success, None otherwise
        @rtype: boolean/none
        """
        ret = None
        
        # signin
        if self.LWSSO_COOKIE_KEY is None:
            return ret
            
        url = "%s/rest/domains/%s/projects/%s/defects" % (self.__qcurl, self.__domain, self.__project)
        
        # prepare template
        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY, 
                    'qc-url': url ,   'cmd': 'create-issue',
                    'defect-name': "%s" % defectName, 'detected-by': "%s" % detectedBy, 'cycle-id': "%s" % cycleId, 
                    'defect-status': "%s" % defectStatus, 'defect-priority': "%s" % defectPriority, 'defect-severity': "%s" % defectSeverity,
                    'creation-time': "%s" % creationTime, 'defect-description': "%s" % defectDescription }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="create issue", details=tpl )
        
        # create entity
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"defect\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"detected-by\"><Value>%s</Value></Field>" % detectedBy )
        data.append( "<Field Name=\"severity\"><Value>%s</Value></Field>" % defectSeverity )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % defectName )
        data.append( "<Field Name=\"priority\"><Value>%s</Value></Field>" % defectPriority )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % defectStatus )
        if len(user01): data.append( "<Field Name=\"user-01\"><Value>%s</Value></Field>" % user01 )
        if len(user02): data.append( "<Field Name=\"user-02\"><Value>%s</Value></Field>" % user02 )
        if len(user03): data.append( "<Field Name=\"user-03\"><Value>%s</Value></Field>" % user03 )
        if len(user04): data.append( "<Field Name=\"user-04\"><Value>%s</Value></Field>" % user04 )
        data.append( "<Field Name=\"creation-time\"><Value>%s</Value></Field>" % creationTime )
        data.append( "<Field Name=\"detected-in-rcyc\"><Value>%s</Value></Field>" % cycleId )
        data.append( "<Field Name=\"description\"><Value>%s</Value></Field>" % defectDescription )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
  
        try:
            r = requests.post(
                                url, 
                                cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY} ,
                                headers = {'Content-Type': 'application/xml;charset=utf-8'},
                                data="\n".join(data).encode("utf8"),
                                proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 201:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 
                            'cmd': 'create-issue' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="create issue error", details=tpl )
            else:
                # extract the defect id
                response = ET.fromstring( r.text.encode("utf8") )
                folderId = response.find("./Fields/Field[@Name='id']/Value")
                ret = int(folderId.text)

                content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY, 
                            'defect-id': "%s" % ret, 'cmd': 'create-issue' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="issue created", details=tpl )
                
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "create-issue" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="create issue exception", details=tpl )

        return ret
