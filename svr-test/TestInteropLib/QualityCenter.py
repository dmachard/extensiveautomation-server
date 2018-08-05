#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
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

try:
    import TestInteropLib
    from TestInteropLib import doc_public
except ImportError: # python3 support
    from . import TestInteropLib
    from TestInteropLib.TestInteropLib import doc_public
    
import requests
import json
import xml.etree.ElementTree as ET
import os
import time
import cgi

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
        self.QC_SESSION = None
        self.XSRF_TOKEN = None
        
    @doc_public
    def signin(self):
        """
        Signin to QC

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        urlAuth = "%s/authentication-point/authenticate" % self.__qcurl
        urlSession = "%s/rest/site-session" % self.__qcurl

        # prepare template
        content = {'qc-url': urlAuth, 'cmd': 'sigin', "username":"%s" % self.__username,
                    "domain": "%s" % self.__domain, "project": "%s" % self.__project }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="sigin", details=tpl )

        # make request
        try:
            r = requests.get(urlAuth,auth=(self.__username,self.__password),
                                proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'signin' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="sigin error", details=tpl )

            # extract the cookie
            else:
                cookies = r.headers["set-cookie"]
                self.LWSSO_COOKIE_KEY = cookies.split("LWSSO_COOKIE_KEY=")[1].split(";", 1)[0]


                r = requests.post(urlSession,
                                cookies={'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY},
                                proxies=self.__proxies, verify=self.__certCheck)
                if r.status_code != 201:
                        content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'signin' }
                        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                        self.logResponse(msg="sigin session error", details=tpl )
                else:
                        cookies = r.headers["set-cookie"]
                        self.QC_SESSION = cookies.split("QCSession=")[1].split(";", 1)[0]
                        self.XSRF_TOKEN = cookies.split("XSRF-TOKEN=")[1].split(";", 1)[0]

                        content = {'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                                'QC_SESSION': "%s" % self.QC_SESSION,
                                'XSRF_TOKEN': "%s" % self.XSRF_TOKEN,
                                'cmd': 'sign' }
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

    def __splitpath(self, path):
        """
        """
        # cleanup path
        path = path.replace("//", "/")
        if path.startswith("/"): path = path[1:]
        if path.endswith("/"): path = path[:-1]
        
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts
    
    def __gethtml(self, text):
        """
        """
        ret = []
        ret.append( "<html>" )
        ret.append( "<body>" )
        ret.append( "%s" % text.replace("\n", "<br />") )
        ret.append( "</body>" )
        ret.append( "</html>" )
        
        val = "".join(ret)
        val = cgi.escape(val)
        return val
        
    def __findInXml(self, root, name, pid):
        """
        """
        ret = None
        for child in root:
            folderName = child.find("./Fields/Field[@Name='name']/Value")
            folderId = child.find("./Fields/Field[@Name='id']/Value")
            parentId = child.find("./Fields/Field[@Name='parent-id']/Value")

            if folderName is not None:
                if folderName.text == name and parentId.text == str(pid):
                    ret = { 'name': folderName.text, 
                            'id': folderId.text, 
                            'parent-id': parentId.text }
                    break
        return ret
        
    def __findXmlByName(self, root, name):
        """
        """
        ret = None
        for child in root:
            folderName = child.find("./Fields/Field[@Name='name']/Value")
            folderId = child.find("./Fields/Field[@Name='id']/Value")
            testId = child.find("./Fields/Field[@Name='test-id']/Value")
            
            if folderName is not None:
                if folderName.text == name:
                    ret = { 'name': folderName.text, 
                            'id': folderId.text,
                            'test-id': testId.text}
                    break
        return ret
        
    def __findFolderTestLab(self, folderName="Root", parentId=-1):
        """
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:
            return ret
        
        url = "%s/rest/domains/%s/projects/%s/test-set-folders?query={parent-id[%s]}" % (self.__qcurl,  
                                                                                         self.__domain, 
                                                                                         self.__project,
                                                                                         parentId)

        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                    'qc-url': url ,   'cmd': 'find-folder-testlab',
                    'parent-id': "%s" % parentId, 
                    'folder-name': "%s" % folderName }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="testlab: find folder (%s)" % folderName, details=tpl )
        
        try:
            r = requests.get( url,
                              cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY,
                                        'QCSession': self.QC_SESSION },
                              proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 
                           'response-more': "%s" % r.text,
                           'cmd': 'find-folder-testlab' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="find folder testlab error", details=tpl )
            else:
                response = ET.fromstring(r.text.encode("utf8"))
                ret = self.__findInXml(root=response, name=folderName, pid=parentId)
                if ret is None:
                    content = {'response-code': "%s" % r.status_code, 
                               'response-more': "%s" % r.text,
                               'cmd': 'find-folder-testlab' }
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testlab: folder not found", details=tpl )
                else:   

                    content = { 'cmd': 'find-folder-testlab' }
                    content.update(ret)
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testlab: folder found" , details=tpl )

                    
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "find-folder-testlab" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="find folder testlab exception", details=tpl )

        return ret
           
    @doc_public
    def searchTestSetByName(self, testsetPath, testsetName):
        """
        Search test set in the testlab
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:
            return ret
        
        safeFolders = self.__splitpath(path=testsetPath)
                    
        rootFolder = self.__findFolderTestLab(folderName="Root", parentId=-1)
        if rootFolder is None:
            return ret
            
        # search all folders
        parentId = rootFolder["id"]
        parentFound = False
        for folder in safeFolders:
            parentFolder = self.__findFolderTestLab(folderName=folder, parentId=parentId)
            if parentFolder is None:
                break
            else:
                parentId = parentFolder["id"]
                parentFound = True
        
        if not parentFound:
            return ret
            
        # search testset
        url = "%s/rest/domains/%s/projects/%s/test-sets?query={parent-id[%s]}" % (self.__qcurl,  
                                                                                         self.__domain, 
                                                                                         self.__project,
                                                                                         parentId)

        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                    'qc-url': url ,   'cmd': 'create-issue',
                    'parent-id': "%s" % parentId, 
                    'testset-name': "%s" % testsetName }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="testlab: search testset (%s)" % testsetName, details=tpl )
        
        try:
            r = requests.get( url,
                              cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY,
                                        'QCSession': self.QC_SESSION },
                              proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 
                           'response-more': "%s" % r.text,
                           'cmd': 'search-testset-testlab' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="search testset testlab error", details=tpl )
            else:
                response = ET.fromstring(r.text.encode("utf8"))
                ret = self.__findInXml(root=response, name=testsetName, pid=parentId)
                if ret is None:
                    content = {'response-code': "%s" % r.status_code, 
                               'response-more': "%s" % r.text,
                               'cmd': 'search-testset-testlab' }
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testset in testlab not found", details=tpl )
                else:  
                    content = { 'cmd': 'search-testset-testlab' }
                    content.update(ret)
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testlab: testset found", details=tpl )
                    
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e,
                        "cmd": "search-testset-testlab" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="search testset testlab exception", details=tpl )

        return ret
     
    @doc_public
    def searchTestInstanceByName(self, instanceName, testsetId):
        """
        Search the test instance by name and testset id
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:  return ret
        
        # search testset
        url = "%s/rest/domains/%s/projects/%s/test-instances?query={contains-test-set.id[%s]}" % (self.__qcurl,  
                                                                                     self.__domain, 
                                                                                     self.__project,
                                                                                     testsetId)

        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                    'qc-url': url ,   'cmd': 'create-issue',
                    'testset-id': "%s" % testsetId, 
                    'instance-name': "%s" % instanceName }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="testlab: search test instance (%s)" % instanceName, details=tpl )
        
        try:
            r = requests.get( url,
                              cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY,
                                        'QCSession': self.QC_SESSION },
                              proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 
                           'response-more': "%s" % r.text,
                           'cmd': 'search-testinstance-testlab' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="search test instance testlab error", details=tpl )
            else:
                response = ET.fromstring(r.text.encode("utf8"))
                ret = self.__findXmlByName(root=response, name=instanceName)
                if ret is None:
                    content = {'response-code': "%s" % r.status_code, 
                               'response-more': "%s" % r.text,
                               'cmd': 'search-testinstance-testlab' }
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testinstance in testlab not found", details=tpl )
                else:  
                    content = { 'cmd': 'search-testinstance-testlab' }
                    content.update(ret)
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testlab: test instance found", details=tpl )
                    
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e,
                        "cmd": "search-testinstance-testlab" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="search test instance testlab exception", details=tpl )

        return ret 

    @doc_public
    def stopTestById(self, runId, testStatus):
        """
        Stop test according to the run id provided
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:  return ret
        
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % testStatus )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        
        url = "%s/rest/domains/%s/projects/%s/runs/%s" % (self.__qcurl,  
                                                     self.__domain, 
                                                     self.__project,
                                                     runId)
                                                     
        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                    'qc-url': url ,   'cmd': 'stop-test',
                    'run-id': "%s" % runId }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="testlab: stop test", details=tpl )
        
        try:
            r = requests.put( url,
                              cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY,
                                        'QCSession': self.QC_SESSION },
                              headers = {'Content-Type': 'application/xml;charset=utf-8'},
                              data="\n".join(data).encode("utf8"),
                              proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 
                           'response-more': "%s" % r.text,
                           'cmd': 'stop-test' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="stop test error", details=tpl )
            else:
                ret = True
                
                content = { 'cmd': 'stop-test' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="testlab: test stopped", details=tpl )
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e,
                        "cmd": "stop-test" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="stop test exception", details=tpl )
        return ret
        
    @doc_public
    def runStepById(self, stepId, runId, stepStatus, stepActual):
        """
        Run step according the run and step id provided
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:  return ret
        
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run-step\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % stepStatus )
        data.append( "<Field Name=\"actual\"><Value>%s</Value></Field>" %  self.__gethtml(stepActual) )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )

        url = "%s/rest/domains/%s/projects/%s/runs/%s/run-steps/%s" % (self.__qcurl,  
                                                     self.__domain, 
                                                     self.__project,
                                                     runId,
                                                     stepId)

        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                    'qc-url': url ,   'cmd': 'run-step',
                    'step-id': "%s" % stepId, 
                    'run-id': "%s" % runId }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="testlab: run step", details=tpl )
        
        try:
            r = requests.put( url,
                              cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY,
                                        'QCSession': self.QC_SESSION },
                              headers = {'Content-Type': 'application/xml;charset=utf-8'},
                              data="\n".join(data).encode("utf8"),
                              proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 
                           'response-more': "%s" % r.text,
                           'cmd': 'run-step' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="run step error", details=tpl )
            else:
                ret = True
                
                content = { 'cmd': 'run-step' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="testlab: step runned", details=tpl )
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e,
                        "cmd": "run-step" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="run step exception", details=tpl )
        return ret
 
    @doc_public
    def runTestByName(self, testsetPath, testsetName, instanceName, testStatus, testActual, 
                      subtypeId="hp.qc.run.MANUAL", runName=""):
        """
        Run test by name
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:  return ret
        
        testset = self.searchTestSetByName(testsetPath=testsetPath, testsetName=testsetName)
        if testset is None: return ret

        testinstance = self.searchTestInstanceByName(instanceName=instanceName, testsetId=testset['id'])
        if testinstance is None: return ret
        
        runinstance = self.startTestById(testsetId=testset['id'], instanceId=testinstance['id'],
                                         testId=testinstance['test-id'], testStatus=testStatus, 
                                         subtypeId=subtypeId, runName=runName)
        if runinstance is None: return ret 

        for stp in runinstance["steps"]:
            self.runStepById(stepId=stp["id"], runId=runinstance["run-id"], 
                             stepStatus=testStatus, 
                             stepActual=testActual)
            
        self.stopTestById(runId=runinstance["run-id"], testStatus=testStatus)
        
        return True
        
    @doc_public
    def startTestByName(self, testsetPath, testsetName, instanceName, testStatus="Not Completed", 
                              subtypeId="hp.qc.run.MANUAL", runName=""):
        """
        Search the test instance by name and testset id
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:  return ret

        testset = self.searchTestSetByName(testsetPath=testsetPath, testsetName=testsetName)
        if testset is None: return ret

        testinstance = self.searchTestInstanceByName(instanceName=instanceName, testsetId=testset['id'])
        if testinstance is None: return ret
        
        ret = self.startTestById(testsetId=testset['id'], instanceId=testinstance['id'],
                                         testId=testinstance['test-id'], testStatus=testStatus, 
                                         subtypeId=subtypeId, runName=runName)
        return ret
        
    @doc_public
    def startTestById(self, testsetId, instanceId, testId, testStatus="Not Completed", 
                            subtypeId="hp.qc.run.MANUAL", runName=""):
        """
        Search the test instance by name and testset id
        """
        ret = None
        
        if self.LWSSO_COOKIE_KEY is None:  return ret
        
        if len(runName):
            _runName = runName
        else:
            _runName = "ExtensiveTesting_%s" % time.strftime('%d-%m-%y %H:%M',time.localtime())

        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"subtype-id\"><Value>%s</Value></Field>" % subtypeId )
        data.append( "<Field Name=\"testcycl-id\"><Value>%s</Value></Field>" % instanceId )
        data.append( "<Field Name=\"cycle-id\"><Value>%s</Value></Field>" % testsetId )
        data.append( "<Field Name=\"test-id\"><Value>%s</Value></Field>" % testId )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % testStatus )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % _runName )
        data.append( "<Field Name=\"owner\"><Value>%s</Value></Field>" % self.__username )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        
        # search testset
        url = "%s/rest/domains/%s/projects/%s/runs" % (self.__qcurl,  
                                                     self.__domain, 
                                                     self.__project)

        content = { 'LWSSO_COOKIE_KEY': "%s" % self.LWSSO_COOKIE_KEY,
                    'qc-url': url ,   'cmd': 'start-test',
                    'testset-id': "%s" % testsetId, 
                    'instance-id': "%s" % instanceId,
                    'test-id': "%s" % testId }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="testlab: start test", details=tpl )
        
        try:
            r = requests.post( url,
                              cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY,
                                        'QCSession': self.QC_SESSION },
                              headers = {'Content-Type': 'application/xml;charset=utf-8'},
                              data="\n".join(data).encode("utf8"),
                              proxies=self.__proxies, verify=self.__certCheck)
            if r.status_code != 201:
                content = {'response-code': "%s" % r.status_code, 
                           'response-more': "%s" % r.text,
                           'cmd': 'start-test' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="start test error", details=tpl )
            else:
                response = ET.fromstring( r.text.encode("utf8") )
                runId = response.find("./Fields/Field[@Name='id']/Value").text

                r = requests.get("%s/%s/run-steps" % (url, runId),
                                cookies={ 'LWSSO_COOKIE_KEY': self.LWSSO_COOKIE_KEY, 
                                          'QCSession': self.QC_SESSION } ,
                                proxies=self.__proxies, verify=self.__certCheck)
                if r.status_code != 200:
                    content = {'response-code': "%s" % r.status_code, 
                               'response-more': "%s" % r.text,
                               'cmd': 'start-test' }
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="start test get steps error", details=tpl )
                else:
                    response = ET.fromstring( r.text.encode("utf8") )
                    steps = []
                    for child in response:
                        step = {}
                        
                        stepId = child.find("./Fields/Field[@Name='id']/Value")
                        if stepId is not None:
                            stepName = child.find("./Fields/Field[@Name='name']/Value")
                            stepDescr = child.find("./Fields/Field[@Name='description']/Value")
                            stepExpected = child.find("./Fields/Field[@Name='expected']/Value")
                            step['id'] = stepId.text
                            step['name'] = stepName.text
                            step['description'] = stepDescr.text
                            step['expected'] = stepExpected.text
                        
                            steps.append( step )
                     
                    ret =  { 'run-id': runId, 'steps': steps }
                    content = { 'cmd': 'start-test' }
                    content.update(ret)
                    
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="testlab: test started", details=tpl )

        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e,
                        "cmd": "start-test" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="start test exception", details=tpl )
        return ret