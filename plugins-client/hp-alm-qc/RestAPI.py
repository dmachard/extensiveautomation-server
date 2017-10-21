#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2017 Denis Machard
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
#
# Gfi Informatique, Inc., hereby disclaims all copyright interest in the
# extensive testing project written by Denis Machard
# 
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

try:
    from PyQt4.QtCore import ( QObject, pyqtSignal )         
except ImportError:
    from PyQt5.QtCore import ( QObject, pyqtSignal )    

from Core import Settings

import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import os
import html
import time
from xml.sax.saxutils import escape

class RestHpAlmClient(QObject):
    """
    Rest HP ALM client
    """
    Error = pyqtSignal(object)
    ConnectionOk = pyqtSignal()
    
    TestsExported = pyqtSignal(list, dict)
    ResultsExported = pyqtSignal(list, dict)
    LogAuthStatus = pyqtSignal(str)
    LogTestsStatus = pyqtSignal(str)
    LogResultsStatus = pyqtSignal(str)
    
    def __init__(self, parent, core, proxies={}):
        """
        """
        QObject.__init__(self, parent)
        self.__core = core
        
        self.WsProxies = proxies
        
        self.WsLwssoCookie = None
        self.WsQcSession = None
        self.WsXsrfToken = None
        
        self.loadConfig()

    def loadConfig(self):
        """
        """
        self.WsUsername = self.core().settings().cfg()["credentials"]["login"]
        self.WsPassword = self.core().settings().cfg()["credentials"]["password"]
        self.WsCheckSsl = self.core().settings().cfg()["qc-server"]["check-ssl"]
        self.WsDomain = self.core().settings().cfg()["qc-server"]["domain"]
        self.WsProject = self.core().settings().cfg()["qc-server"]["project"]
        self.WsUrl = self.core().settings().cfg()["qc-server"]["url"]
        if self.WsUrl.endswith("/"): self.WsUrl = self.WsUrl[:-1]

    def core(self):
        """
        """
        return self.__core

    def __findTestset(self, root, name, pid):
        """
        """
        ret = None
        # i = 0
        for child in root:
            tsName = child.find("./Fields/Field[@Name='name']/Value")
            tsId = child.find("./Fields/Field[@Name='id']/Value")
            parentId = child.find("./Fields/Field[@Name='parent-id']/Value")

            if tsName.text == name and parentId.text == pid:
                ret = { 'name': tsName.text, 'id': tsId.text, 
                        'parent-id': parentId.text }
                break
            # i += 1
            
        return ret
    
    def __findFolder(self, root, name, pid):
        """
        """
        ret = None
        # i = 0
        for child in root:
            folderName = child.find("./Fields/Field[@Name='name']/Value")
            folderId = child.find("./Fields/Field[@Name='id']/Value")
            parentId = child.find("./Fields/Field[@Name='parent-id']/Value")

            if folderName is not None:
                if folderName.text == name and parentId.text == pid:
                    ret = { 'name': folderName.text, 'id': folderId.text, 
                            'parent-id': parentId.text }
                    break
            # i += 1
            
        return ret
        
    def __findTest(self, xml, name, pid):
        """
        """
        ret = None
        # i = 0
        for child in xml:
            testName = child.find("./Fields/Field[@Name='name']/Value")
            testId = child.find("./Fields/Field[@Name='id']/Value")
            parentId = child.find("./Fields/Field[@Name='parent-id']/Value")

            if testName is not None:
                if testName.text == name and parentId.text == pid:
                    ret = { 'name': testName.text, 'id': testId.text, 
                            'parent-id': parentId.text }
                    break
            # i += 1
            
        return ret
        
    def __findSteps(self, xml):
        """
        """
        steps = []
        for child in xml:
            stepId = child.find("./Fields/Field[@Name='id']/Value")
            if stepId is not None:
                steps.append( stepId.text )
        return steps
        
    def __findTestset(self, xml, name, pid):
        """
        """
        ret = None
        # i = 0
        for child in xml:
            testName = child.find("./Fields/Field[@Name='name']/Value")
            testId = child.find("./Fields/Field[@Name='id']/Value")
            parentId = child.find("./Fields/Field[@Name='parent-id']/Value")

            if testName is not None:
                if testName.text == name and parentId.text == pid:
                    ret = { 'name': testName.text, 'id': testId.text, 
                            'parent-id': parentId.text }
                    break

        return ret

    def __findTestsetins(self, xml, name, pid):
        """
        """
        ret = None
        # i = 0
        for child in xml:
            testinsName = child.find("./Fields/Field[@Name='name']/Value")
            testinsId = child.find("./Fields/Field[@Name='id']/Value")
            parentTestId = child.find("./Fields/Field[@Name='test-id']/Value")

            if testinsName is not None:
                if testinsName.text == name and parentTestId.text == pid:
                    ret = { 'name': testinsName.text, 'id': testinsId.text, 
                            'parent-id': parentTestId.text }
                    break
            # i += 1
            
        return ret
        
    def __splitall(self, path):
        """
        """
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
        val = html.escape(val)
        return val

    def RestFindTestFolder(self, logger, folderName, parentId):
        """
        """
        logger("Finding folder %s in testplan" % folderName )
        r = requests.get("%s/rest/domains/%s/projects/%s/test-folders?query={parent-id[%s]}" % 
                            (self.WsUrl, self.WsDomain, self.WsProject, parentId), 
                            cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                            proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception( "Unable to retrieve folders from testplan: %s - %s" % (r.status_code, r.text) )

        foldersXML = ET.fromstring(r.text.encode("utf8"))
        folder = self.__findFolder(root=foldersXML, name=folderName, pid=parentId)
        return folder

    def RestFindTestsetFolder(self, logger, folderName, parentId):
        """
        """
        logger("Finding folder %s in testlab" % folderName )
        r = requests.get("%s/rest/domains/%s/projects/%s/test-set-folders?query={parent-id[%s]}" % 
                            (self.WsUrl, self.WsDomain, self.WsProject, parentId), 
                            cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                            proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception( "Unable to retrieve folders from testlab: %s - %s" % (r.status_code, r.text) )

        foldersXML = ET.fromstring(r.text.encode("utf8"))
        folder = self.__findFolder(root=foldersXML, name=folderName, pid=parentId)
        return folder
        
    def RestAddTestFolder(self, logger, folderName, parentId):
        """
        """
        logger("Creating folder %s" % folderName )
        
        ret = None
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"test-folder\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"parent-id\"><Value>%s</Value></Field>" % parentId )
        data.append( "<Field Name=\"description\"><Value></Value></Field>" )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % folderName )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        r = requests.post("%s/rest/domains/%s/projects/%s/test-folders" % (self.WsUrl, self.WsDomain, self.WsProject), 
                                cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                                headers = {'Content-Type': 'application/xml;charset=utf-8'},
                                data="\n".join(data).encode("utf8"),
                                proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception( "Unable to create folder in testplan: %s - %s" % (r.status_code, errTitle) )

        response = ET.fromstring( r.text.encode("utf8") )
        folderId = response.find("./Fields/Field[@Name='id']/Value")
        ret = folderId.text
        return ret
        
    def RestAddTestsetFolder(self, logger, folderName, parentId):
        """
        """
        logger("Creating folder %s" % folderName )
        
        ret = None
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"test-set-folder\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"parent-id\"><Value>%s</Value></Field>" % parentId )
        data.append( "<Field Name=\"description\"><Value></Value></Field>" )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % folderName )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        r = requests.post("%s/rest/domains/%s/projects/%s/test-set-folders" % (self.WsUrl, self.WsDomain, self.WsProject), 
                                cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                                headers = {'Content-Type': 'application/xml;charset=utf-8'},
                                data="\n".join(data).encode("utf8"),
                                proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception( "Unable to create folder in testlab: %s - %s" % (r.status_code, errTitle) )

        response = ET.fromstring( r.text.encode("utf8") )
        folderId = response.find("./Fields/Field[@Name='id']/Value")
        ret = folderId.text
        return ret
        
    def RestDeleteTest(self, logger, testId, testName=None):
        """
        """
        logger("Deleting test (%s) in test plan..."  % testName)
        r = requests.delete("%s/rest/domains/%s/projects/%s/tests/%s" % (self.WsUrl, self.WsDomain, self.WsProject, testId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception("Unable to delete test in testplan - %s - %s" % (r.status_code, errTitle ) )
        return True

    def RestFindTest(self, logger, testName, parentId):
        """
        """
        logger("Finding test (%s) in test plan..."  % testName)
        r = requests.get("%s/rest/domains/%s/projects/%s/tests?query={parent-Id[%s]}" % (self.WsUrl, self.WsDomain, self.WsProject, parentId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to get tests from testplan - %s - %s" % (r.status_code, r.text ) )
        
        oXml = ET.fromstring(r.text.encode("utf8"))
        oTest = self.__findTest(xml=oXml, name=testName, pid=parentId)
        if oTest is None: 
            raise Exception( "Unable to find the test (%s) in test plan" % testName )
            
        return oTest
            
    def RestCreateTest(self, logger, testName, parentId, testDescription, Test_Type='MANUAL', User_01='', User_02='',
                    User_03='', User_04='', User_05='', User_06='', User_07='', User_08='', User_09='',
                    User_10='', User_11='', User_12='', User_13='', User_14='', User_15='', User_16='',
                    User_17='', User_18='', User_19='', User_20='', User_21='', User_22='', User_23='',
                    User_24='', Overwrite_Tests=False, Add_Folders=False):
        """
        """
        logger("Creating test (%s) in test plan" % testName )
        
        ret = None
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"test\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"subtype-id\"><Value>%s</Value></Field>" % Test_Type )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % testName )
        data.append( "<Field Name=\"parent-id\"><Value>%s</Value></Field>" % parentId )
        data.append( "<Field Name=\"steps\"><Value>0</Value></Field>" )
        data.append( "<Field Name=\"description\"><Value>%s</Value></Field>"  % testDescription )
        if User_01: data.append( "<Field Name=\"user-01\"><Value>%s</Value></Field>" % User_01 )
        if User_02: data.append( "<Field Name=\"user-02\"><Value>%s</Value></Field>" % User_02 )
        if User_03: data.append( "<Field Name=\"user-03\"><Value>%s</Value></Field>" % User_03 )
        if User_04: data.append( "<Field Name=\"user-04\"><Value>%s</Value></Field>" % User_04 )
        if User_05: data.append( "<Field Name=\"user-05\"><Value>%s</Value></Field>" % User_05 ) 
        if User_06: data.append( "<Field Name=\"user-06\"><Value>%s</Value></Field>" % User_06 )
        if User_07: data.append( "<Field Name=\"user-07\"><Value>%s</Value></Field>" % User_07 )
        if User_08: data.append( "<Field Name=\"user-08\"><Value>%s</Value></Field>" % User_08 )
        if User_09: data.append( "<Field Name=\"user-09\"><Value>%s</Value></Field>" % User_09 )
        if User_10: data.append( "<Field Name=\"user-10\"><Value>%s</Value></Field>" % User_10 )
        if User_11: data.append( "<Field Name=\"user-11\"><Value>%s</Value></Field>" % User_11 )
        if User_12: data.append( "<Field Name=\"user-12\"><Value>%s</Value></Field>" % User_12 )
        if User_13: data.append( "<Field Name=\"user-13\"><Value>%s</Value></Field>" % User_13 )
        if User_14: data.append( "<Field Name=\"user-14\"><Value>%s</Value></Field>" % User_14 )
        if User_15: data.append( "<Field Name=\"user-15\"><Value>%s</Value></Field>" % User_15 )
        if User_16: data.append( "<Field Name=\"user-16\"><Value>%s</Value></Field>" % User_16 )
        if User_17: data.append( "<Field Name=\"user-17\"><Value>%s</Value></Field>" % User_17 )
        if User_18: data.append( "<Field Name=\"user-18\"><Value>%s</Value></Field>" % User_18 )
        if User_19: data.append( "<Field Name=\"user-19\"><Value>%s</Value></Field>" % User_19 )
        if User_20: data.append( "<Field Name=\"user-20\"><Value>%s</Value></Field>" % User_20 )
        if User_21: data.append( "<Field Name=\"user-21\"><Value>%s</Value></Field>" % User_21 )
        if User_22: data.append( "<Field Name=\"user-22\"><Value>%s</Value></Field>" % User_22 )
        if User_23: data.append( "<Field Name=\"user-23\"><Value>%s</Value></Field>" % User_23 )
        if User_24: data.append( "<Field Name=\"user-24\"><Value>%s</Value></Field>" % User_24 )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        r = requests.post("%s/rest/domains/%s/projects/%s/tests" % (self.WsUrl, self.WsDomain, self.WsProject), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)

        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            if "duplicate test" in errTitle.lower() and Overwrite_Tests:
                # overwrite option is activated then we search the current test 
                oTest = self.RestFindTest(logger=logger, testName=testName, parentId=parentId)
                
                # then delete the test
                self.RestDeleteTest(logger=logger, testId=oTest["id"], testName=testName)
                
                # finally recreate the new one
                return self.RestCreateTest(logger=logger, testName=testName, parentId=parentId, 
                                            testDescription=testDescription, Test_Type=Test_Type, User_01=User_01,
                                            User_02=User_02, User_03=User_03, User_04=User_04, User_05=User_05, 
                                            User_06=User_06, User_07=User_07, User_08=User_08, User_09=User_09,
                                            User_10=User_10, User_11=User_11, User_12=User_12, User_13=User_13, 
                                            User_14=User_14, User_15=User_15, User_16=User_16, User_17=User_17, 
                                            User_18=User_18, User_19=User_19, User_20=User_20, User_21=User_21, 
                                            User_22=User_22, User_23=User_23, User_24=User_24, 
                                            Overwrite_Tests=Overwrite_Tests, Add_Folders=Add_Folders)
            else:
                raise Exception("Unable to add test in testplan - %s - %s" % (r.status_code, errTitle ) )

        response = ET.fromstring( r.text.encode("utf8") )
        testId = response.find("./Fields/Field[@Name='id']/Value")
        ret = testId.text
        return ret

    def RestCreateStep(self, logger, testId, stepName, stepDescription, stepExpected):
        """
        """
        logger("Creating step (%s) for test (%s)" % (stepName, testId) )
        
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"design-step\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"parent-id\"><Value>%s</Value></Field>" % testId )
        
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % stepName )
        data.append( "<Field Name=\"description\"><Value>%s</Value></Field>" % self.__gethtml(stepDescription) )
        data.append( "<Field Name=\"expected\"><Value>%s</Value></Field>" % self.__gethtml(stepExpected) )
        
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        
        r = requests.post("%s/rest/domains/%s/projects/%s/design-steps" % (self.WsUrl, self.WsDomain, self.WsProject), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception( "Unable to create step: %s - %s" % (r.status_code, errTitle) )
        return True
        
    def RestCreateTestset(self, logger, testsetName, parentId, testsetComment="testset generated automatically", 
                                subtypeId="hp.qc.test-set.default"):
        """
        """
        logger("Creating testset (%s) in test plan" % testsetName )
        
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"test-set\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"parent-id\"><Value>%s</Value></Field>" % parentId )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % testsetName )
        data.append( "<Field Name=\"subtype-id\"><Value>%s</Value></Field>" % subtypeId )
        data.append( "<Field Name=\"comment\"><Value>%s</Value></Field>" % self.__gethtml(testsetComment) )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        
        r = requests.post("%s/rest/domains/%s/projects/%s/test-sets" % (self.WsUrl, self.WsDomain, self.WsProject), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception("Unable to add testset in testlab - %s - %s" % (r.status_code, errTitle ) )

        response = ET.fromstring( r.text.encode("utf8") )
        testsetId = response.find("./Fields/Field[@Name='id']/Value")
        ret = testsetId.text
        return ret
    
    def RestFindTestset(self, logger, testsetName, parentId):
        """
        """
        logger("Finding testset (%s) in test lab..."  % testsetName)
        
        r = requests.get("%s/rest/domains/%s/projects/%s/test-sets?query={parent-Id[%s]}" % (self.WsUrl, self.WsDomain, self.WsProject, parentId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to get testsets frmo testlab - %s - %s" % (r.status_code, r.text ) )
        
        oXml = ET.fromstring(r.text.encode("utf8"))
        oTestset = self.__findTestset(xml=oXml, name=testsetName, pid=parentId)
        if oTestset is None: 
            raise Exception( "Unable to find the testset (%s) in test lab" % testsetName )
            
        return oTestset
        
    def RestFindTestInstance(self, logger, testinsName, parentId):
        """
        """
        logger("Finding test instance (%s) in test lab..."  % testinsName)
        
        r = requests.get("%s/rest/domains/%s/projects/%s/test-instances?query={test-id[%s]}" % (self.WsUrl, self.WsDomain, self.WsProject, parentId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to get test instances from testlab - %s - %s" % (r.status_code, r.text ) )
        
        oXml = ET.fromstring(r.text.encode("utf8"))
        oTestins = self.__findTestsetins(xml=oXml, name=testinsName, pid=parentId)
        if oTestins is None: 
            raise Exception( "Unable to find the test instance (%s) in test lab" % testinsName )
            
        return oTestins
        
    def RestCreateTestInstance(self, logger, testId, testsetId, subtypeId="hp.qc.test-instance.MANUAL"):
        """
        """       
        logger("Creating testinstance for testset" )

        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"test-instance\">" )
        data.append( "<Fields>" )
        # hp.qc.test-instance.external-test
        data.append( "<Field Name=\"subtype-id\"><Value>%s</Value></Field>" % subtypeId )
        # Testset Id of the testset that contains the test instance
        data.append( "<Field Name=\"cycle-id\"><Value>%s</Value></Field>" % testsetId )
        # The test Id of the test instance
        data.append( "<Field Name=\"test-id\"><Value>%s</Value></Field>" % testId )

        data.append( "</Fields>" ) 
        data.append( "</Entity>" )

        r = requests.post("%s/rest/domains/%s/projects/%s/test-instances" % (self.WsUrl, self.WsDomain, self.WsProject), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception( "Unable to add test instance: %s - %s" % (r.status_code, errTitle) )


        response = ET.fromstring( r.text.encode("utf8") )
        testinsId = response.find("./Fields/Field[@Name='id']/Value")
        ret = testinsId.text

        return ret
        
    def RestCreateRun(self, logger, testinsId, testsetId, testId, testStatus, runName, ownerName, subtypeId="hp.qc.run.MANUAL"):
        """
        """
        logger("Creating run" )

        # if runName is None
        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"subtype-id\"><Value>%s</Value></Field>" % subtypeId )
        data.append( "<Field Name=\"testcycl-id\"><Value>%s</Value></Field>" % testinsId )
        data.append( "<Field Name=\"cycle-id\"><Value>%s</Value></Field>" % testsetId )
        data.append( "<Field Name=\"test-id\"><Value>%s</Value></Field>" % testId )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % testStatus )
        data.append( "<Field Name=\"name\"><Value>%s</Value></Field>" % runName )
        data.append( "<Field Name=\"owner\"><Value>%s</Value></Field>" % ownerName )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )
        
        r = requests.post("%s/rest/domains/%s/projects/%s/runs" % (self.WsUrl, self.WsDomain, self.WsProject), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            errTitle = r.text.split("<title>")[1].split("</title>", 1)[0]
            errTitle = html.unescape(errTitle)
            raise Exception( "Unable to add run: %s - %s" % (r.status_code, errTitle) )

        response = ET.fromstring( r.text.encode("utf8") )
        runId = response.find("./Fields/Field[@Name='id']/Value")
        ret = runId.text
        return ret

    def RestGetTestInstanceSteps(self, logger, runId):
        """
        """
        logger("Get steps from test instance" )
        
        r = requests.get("%s/rest/domains/%s/projects/%s/runs/%s/run-steps" % (self.WsUrl, self.WsDomain, self.WsProject, runId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to get steps according to the test instances - %s - %s" % (r.status_code, r.text ) )

        oXml = ET.fromstring(r.text.encode("utf8"))
        steps = self.__findSteps(xml=oXml)
        return steps
    
    def RestUpdateRun(self, logger, runId, runStatus):
        """
        """
        logger("Updating run" )

        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % runStatus )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )

        r = requests.put("%s/rest/domains/%s/projects/%s/runs/%s" % (self.WsUrl, self.WsDomain, self.WsProject, runId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to update run - %s - %s" % (r.status_code, r.text ) )
        return True

    def RestUpdateRunStep(self, logger, stepId, runId, stepStatus, stepActual):
        """
        """
        logger("Running steps" )

        data = [ "<?xml version=\"1.0\" encoding=\"utf-8\"?>" ]
        data.append( "<Entity Type=\"run-step\">" )
        data.append( "<Fields>" )
        data.append( "<Field Name=\"status\"><Value>%s</Value></Field>" % stepStatus )
        data.append( "<Field Name=\"actual\"><Value>%s</Value></Field>" %  self.__gethtml(stepActual) )
        data.append( "</Fields>" ) 
        data.append( "</Entity>" )

        r = requests.put("%s/rest/domains/%s/projects/%s/runs/%s/run-steps/%s" % (self.WsUrl, self.WsDomain, self.WsProject, runId, stepId), 
                        cookies={ 'LWSSO_COOKIE_KEY': self.WsLwssoCookie, 'QCSession': self.WsQcSession } ,
                        headers = {'Content-Type': 'application/xml;charset=utf-8'},
                        data="\n".join(data).encode("utf8"),
                        proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception("Unable to update run step - %s - %s" % (r.status_code, r.text ) )
        return True
        
    def RestAuthenticate(self, logger):
        """
        """
        self.WsLwssoCookie = None
        self.WsQcSession = None
        self.WsXsrfToken = None
        
        almAuth = "<alm-authentication><user>%s</user><password>%s</password></alm-authentication>""" % (self.WsUsername, escape(self.WsPassword))
        logger("Connection to the REST API..." )
        r = requests.post("%s/authentication-point/alm-authenticate" % self.WsUrl,
                            headers = {'Content-Type': 'application/xml;charset=utf-8'},
                            data = almAuth.encode("utf8"),
                            proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 200:
            raise Exception('Unable to connect to the rest api: %s - %s' % (r.status_code, r.text) )

        cookies = r.headers["set-cookie"]
        self.WsLwssoCookie = cookies.split("LWSSO_COOKIE_KEY=")[1].split(";", 1)[0]
        
        
        logger("Creating session..." )
        r = requests.post("%s/rest/site-session" % self.WsUrl,
                            cookies={'LWSSO_COOKIE_KEY': self.WsLwssoCookie},
                            proxies=self.WsProxies, verify=self.WsCheckSsl)
        if r.status_code != 201:
            raise Exception('Unable to create the session to the rest api: %s - %s' % (r.status_code, r.text) )
        logger("Session ready" )
        
        cookies = r.headers["set-cookie"]
        self.WsQcSession = cookies.split("QCSession=")[1].split(";", 1)[0]
        self.WsXsrfToken = cookies.split("XSRF-TOKEN=")[1].split(";", 1)[0]
        
        logger("Successfully connected" )
        
    def RestLogout(self, logger):
        """
        """
        logger("Disconnection from the REST API..." )
        r = requests.get("%s/authentication-point/logout" % self.WsUrl, 
                            proxies=self.WsProxies, verify=self.WsCheckSsl,
                            cookies={'LWSSO_COOKIE_KEY': self.WsLwssoCookie} )
        if r.status_code != 200:
            raise Exception('Unable to disconnect from the rest api: %s - %s' % (r.status_code, r.text) )
        logger("Disconnected" )

    def testConnection(self, config={}):
        """
        """
        try:
            # connect
            self.RestAuthenticate(logger=self.logAuthStatus)

            # disconnect
            self.RestLogout(logger=self.logAuthStatus)
            
            self.ConnectionOk.emit()
        except Exception as e:
            self.logAuthStatus("Error on HP connection" )
            self.Error.emit( "%s" % e )
            
    def addTestsInTestPlan(self, testcases, config={}):    
        """
        """
        try:
            self.RestAuthenticate(logger=self.logTestsStatus)

            # export one testcase
            for tc in testcases:
                rootFolder = self.RestFindTestFolder(logger=self.logTestsStatus, folderName="Subject", parentId="0")
                if rootFolder is None: 
                    raise Exception( "Unable to detect the root folder in test plan" )
                
                # clean up the path
                testpath="%s/%s" % ( tc['testpath'], tc['testname'] )
                testpath = testpath.replace("//", "/")
                if testpath.startswith("/"): testpath = testpath[1:]
                if testpath.endswith("/"): testpath = testpath[:-1]
                if not len(testpath): folders = []
                else: folders = self.__splitall(testpath)

                # iterate on all folders
                ret = None
                parentId = rootFolder["id"]
                for d in folders:
                    ret = self.RestFindTestFolder(logger=self.logTestsStatus, folderName=d, parentId=parentId)
                    if ret is None and not config["Add_Folders"]:
                        raise Exception( 'Folder (%s) is missing in test plan' % d )
                    elif ret is None and config["Add_Folders"]:
                        parentId = self.RestAddTestFolder(logger=self.logTestsStatus, folderName=d, parentId=parentId)
                    else:
                        parentId = ret["id"]

                # create the test
                if parentId is None:
                    raise Exception('Folder parent id is missing ?')

                funcParams = { 'logger': self.logTestsStatus, 'testName': tc['testcase'], 'parentId': parentId, 
                                'testDescription': tc['purpose'] }
                funcParams.update(config)
                testId = self.RestCreateTest(**funcParams)

                # create steps
                i = 1
                for stp in tc["steps"]:                
                    self.RestCreateStep(logger=self.logTestsStatus, testId=testId, 
                                        stepName="Step%s" % i, stepDescription=stp["action"], 
                                        stepExpected=stp["expected"])
                    i += 1
                                    
            # disconnect
            self.RestLogout(logger=self.logTestsStatus)
            
            self.TestsExported.emit(testcases, config)
        except Exception as e:
            if self.WsLwssoCookie is not None: self.RestLogout(logger=self.logTestsStatus)
                
            self.logTestsStatus("Error on test(s) export" )
            self.Error.emit( "%s" % e )

    def addResultsInTestLab(self, testcases, config={}):
        """
        """
        try:
            # connect
            self.RestAuthenticate(logger=self.logResultsStatus)

            rootFolder = self.RestFindTestsetFolder(logger=self.logResultsStatus, folderName="Root", parentId="-1")
            if rootFolder is None: 
                raise Exception( "Unable to detect the root folder in test lab" )

            rootTpFolder = self.RestFindTestFolder(logger=self.logResultsStatus, folderName="Subject", parentId="0")
            if rootTpFolder is None: 
                raise Exception( "Unable to detect the root folder in test plan" )
                
            # clean up the path
            testsetpath = config["TestSet_Path"].replace("//", "/")
            if testsetpath.startswith("/"): testsetpath = testsetpath[1:]
            if testsetpath.endswith("/"): testsetpath = testsetpath[:-1]
            if not len(testsetpath): folders = []
            else: folders = self.__splitall(testsetpath)

            # iterate on all folders
            ret = None
            parentId = rootFolder["id"]
            for d in folders:
                ret = self.RestFindTestsetFolder(logger=self.logResultsStatus, folderName=d, parentId=parentId)
                if ret is None and not config["Add_Folders"]:
                    raise Exception( 'Folder (%s) is missing in test lab' % d )
                elif ret is None and config["Add_Folders"]:
                    parentId = self.RestAddTestsetFolder(logger=self.logResultsStatus, folderName=d, parentId=parentId)
                else:
                    parentId = ret["id"]
                
            if config["Add_TestSet"]:
                testsetId = self.RestCreateTestset(logger=self.logResultsStatus, testsetName=config["TestSet_Name"], parentId=parentId,
                                                    subtypeId=config["TestSet_TypeId"])
            else:
                oTestset = self.RestFindTestset(logger=self.logResultsStatus, testsetName=config["TestSet_Name"], parentId=parentId)
                testsetId = oTestset["id"]

            for tc in testcases:
                # clean the testpath
                testpath= "%s/" % tc['testpath']
                testpath = testpath.replace("//", "/")
                if testpath.startswith("/"): testpath = testpath[1:]
                if testpath.endswith("/"): testpath = testpath[:-1]
                if not len(testpath): folders = []
                else: folders = self.__splitall(testpath)

                # iterate on all folders
                ret = None
                parentIdTp = rootTpFolder["id"]
                for d in folders:
                    ret = self.RestFindTestFolder(logger=self.logResultsStatus, folderName=d, parentId=parentIdTp)
                    if ret is None :
                        raise Exception( 'Folder (%s) is missing in test plan' % d )
                    else:
                        parentIdTp = ret["id"]
                if parentIdTp is None:
                    raise Exception('Folder parent id is missing ?')

                # finally search the test in testplan ?
                oTest = self.RestFindTest(logger=self.logResultsStatus, testName=tc['testname'], parentId=parentIdTp)
                
                if config["Add_TestInstance"]:
                    # add the test instance in testset
                    testinsId = self.RestCreateTestInstance(logger=self.logResultsStatus, testId=oTest["id"], testsetId=testsetId,
                                                            subtypeId=config["TestInstance_TypeId"])
                else:
                    oTestins = self.RestFindTestInstance(logger=self.logResultsStatus, testinsName=tc["name"], parentId=oTest["id"])
                    testinsId = oTestins["id"]

                # create a run with the state not completed
                runName = "%s_%s" % (Settings.instance().readValue( key = 'Common/name' ), time.strftime('%d-%m-%y %H:%M',time.localtime()) )
                ownerName = self.core().settings().cfg()["credentials"]["login"]
                runId = self.RestCreateRun(logger=self.logResultsStatus, testinsId=testinsId, runName=runName, 
                                            ownerName=ownerName, testsetId=testsetId, testId=oTest["id"], 
                                            testStatus="Not Completed", subtypeId=config["TestRun_TypeId"] )
                    
                # create a run for all steps
                steps = self.RestGetTestInstanceSteps(logger=self.logResultsStatus, runId=runId)

                if "steps" in tc:
                    i = 0
                    for stpId in steps:
                        try:
                            stp = tc["steps"][i]
                        except Exception as e:
                            raise Exception("step %s is missing" % i )
                        else:
                            self.RestUpdateRunStep(logger=self.logResultsStatus, stepId=stpId, runId=runId, 
                                                    stepStatus=stp["result"], stepActual=stp["actual"] )
                            i += 1
                else:
                    for stpId in steps:
                        self.RestUpdateRunStep(logger=self.logResultsStatus, stepId=stpId, runId=runId, 
                                                stepStatus=tc["result"], stepActual="")

                # complete the run
                self.RestUpdateRun(logger=self.logResultsStatus, runId=runId, runStatus=tc["result"])

            # disconnect
            self.RestLogout(logger=self.logResultsStatus)
            
            self.ResultsExported.emit(testcases, config)
        except Exception as e:
            if self.WsLwssoCookie is not None: self.RestLogout(logger=self.logResultsStatus)
                
            self.logResultsStatus("Error on result(s) export" )
            self.Error.emit( "%s" % e )
            
    def logAuthStatus(self, status):
        """
        """
        self.LogAuthStatus.emit( "Status: %s" % status )
        
    def logTestsStatus(self, status):
        """
        """
        self.LogTestsStatus.emit( "Status: %s" % status )
        
    def logResultsStatus(self, status):
        """
        """
        self.LogResultsStatus.emit( "Status: %s" % status )