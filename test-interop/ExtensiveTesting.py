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
import hashlib

class ExtensiveTesting(TestInteropLib.InteropPlugin):
    """
    ExtensiveTesting plugin
    """
    @doc_public
    def __init__(self, parent, url, login, password, verifySsl=False, proxies={} ):
        """
        ExtensiveTesting interop
        
        @param parent: testcase parent
        @type parent: testcase
        
        @param url: jira url api
        @type url: string
        
        @param login: login for api
        @type login: string
        
        @param password: password for api
        @type passord: string     

        @param verifySsl: check ssl server cert (default=False)
        @type verifySsl: boolean
        
        @param proxies: proxies to use {'http': '', 'https': ''}
        @type proxies: dict
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        
        self.__url = url
        if url.endswith("/"): self.__url = url[:-1]
        self.__login = login
        self.__password = password
        self.__jsessionid = None
        self.__certCheck = verifySsl
        self.__proxies = proxies
        self.__certCheck = verifySsl
    @doc_public
    def login(self):
        """
        Login to extensivetesting

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        uri = 'rest/session/login'
        
        hash =  hashlib.sha1()
        hash.update(self.__password)
        
        payload = { "login": self.__login, "password": hash.hexdigest()  }
        headers = {'content-type': 'application/json'}        
        url = "%s/%s" % (self.__url, uri)

        # log message
        content = {'extensivetesting-url': url, 'username':"%s" % self.__login, 'cmd': 'login' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="login", details=tpl )
        
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200:  # log message
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'login' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="login error", details=tpl )
                
            else:
                # decode json body
                rsp = json.loads(r.text)
                self.__jsessionid = rsp['session_id']

                ret = True

                # log message
                content = {'jsessionid': self.__jsessionid, 'cmd': 'login' }
                content.update(rsp)
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="logged", details=tpl )

        except Exception as e:  # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "login" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="login exception", details=tpl )

        return ret
    @doc_public    
    def logout(self):
        """
        Logout from extensivetesting
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if self.__jsessionid is None: 
            return ret
            
        uri = 'rest/session/logout'
        headers = {'cookie': 'JSESSIONID=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)

        # log message
        content = {'extensivetesting-url': url, 'cmd': 'logout', 'jsessionid': self.__jsessionid }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="logout", details=tpl )
        
        try:
            r = requests.get( url,headers=headers, verify=self.__certCheck, proxies=self.__proxies)
            if r.status_code != 200: 
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'logout' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="logout error", details=tpl )
            else:
                # log message
                content = { 'cmd': 'logout' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="logout", details=tpl )
                
                ret = True
                
        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "logout" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="logout exception", details=tpl )
            
        return ret
    @doc_public
    def addVariable(self, variableName, variableValue, projectName="Common"):
        """
        Add a variable
        
        @param variableName: variable name
        @type variableName: string     

        @param variableValue: json as string
        @type variableValue: string 
        
        @param projectName: project to look in (default=Common)
        @type projectName: string     
        
        @return: variable id
        @rtype: string
        """
        ret = None
        if self.__jsessionid is None:
            return ret
           
        uri = 'rest/variables/add'
        payload = { "project-name": projectName, "variable-name": variableName, "variable-value": variableValue }
        headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)
       
        # log message
        content = {'extensivetesting-url': url, 'cmd': 'add-variable', 'jsessionid': self.__jsessionid,
                   'project-name': projectName, "variable-name": variableName  }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="add variable", details=tpl )
       
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'add-variable' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="add variable error", details=tpl )
            else:
                # decode json body
                rsp = json.loads(r.text)

                # log message
                content = { 'cmd': 'add-variable' }
                content.update(rsp)

                ret = rsp["variable-id"]

                tpl = self.template(name=self.__class__.__name__.upper(), content=content)
                self.logResponse(msg="result", details=tpl  )

        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "add-variable" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="add variable exception", details=tpl )
           
        return ret
    @doc_public
    def searchVariable(self, variableName, projectName="Common"):
        """
        Search a variable according to the name and the project name to look-in
        
        @param variableName: variable name to search
        @type variableName: string     

        @param projectName: project to look in (default=Common)
        @type projectName: string     
        
        @return: json on match, None otherwise
        @rtype: json/none
        """
        ret = None
        if self.__jsessionid is None:
            return ret
           
        uri = 'rest/variables/search'
        payload = { "project-name": projectName, "variable-name": variableName }
        headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)
       
        # log message
        content = {'extensivetesting-url': url, 'cmd': 'search-variable', 'jsessionid': self.__jsessionid,
                   'project-name': projectName, "variable-name": variableName  }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="search variable", details=tpl )
       
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'search-variable' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="search variable error", details=tpl )
            else:
                # decode json body
                rsp = json.loads(r.text)

                # log message
                content = { 'cmd': 'search-variable' }
                content.update(rsp)

                if "variables" in rsp:
                    ret = rsp["variables"]
                else:
                    ret = rsp["variable"]

                tpl = self.template(name=self.__class__.__name__.upper(), content=content)
                self.logResponse(msg="result", details=tpl  )

        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "search-variable" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="search variable exception", details=tpl )
           
        return ret
    @doc_public   
    def updateVariable(self, variableId, variableValue):
        """
        Update the value of a variable according to the id provided
        Make a search to get the ID of the variable to update
        
        @param variableId: variable id
        @type variableId: string     

        @param variableValue: json as string
        @type variableValue: string 
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if self.__jsessionid is None:
            return ret
           
        uri = 'rest/variables/update'
        payload = { "variable-id": variableId, "variable-value": variableValue }
        headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)
       
        # log message
        content = {'extensivetesting-url': url, 'cmd': 'update-variable', 'jsessionid': self.__jsessionid,
                   'variable-value': variableValue, "variable-id": variableId  }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="update variable", details=tpl )
       
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'update-variable' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="update variable error", details=tpl )
            else:
                # decode json body
                rsp = json.loads(r.text)

                # log message
                content = { 'cmd': 'update-variable' }
                content.update(rsp)

                if "message" in rsp:
                        if rsp["message"] == "variable successfully update":
                                ret = True

                tpl = self.template(name=self.__class__.__name__.upper(), content=content)
                self.logResponse(msg="result", details=tpl  )

        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "update-variable" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="update variable exception", details=tpl )
           
        return ret
    @doc_public    
    def runTest(self, testPath, projectName, testInputs=[], testAgents=[]):
        """
        Run a test
        
        @param testPath: test path (example: Basics/00_Wait.tux)
        @type testPath: string     
        
        @param projectName: project (example: Common)
        @type projectName: string    
        
        @param testInputs: list of inputs (example: [ {'name': 'DURATION', 'type': 'int' , 'value':  '5'} ] )
        @type testInputs: list    
        
        @param testAgents: list of agents
        @type testAgents: list
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if self.__jsessionid is None: 
            return ret
            
        uri = 'rest/tests/run'
        payload = { "test-path": testPath, "project-name": projectName, 
                    'test-inputs': testInputs, 'test-agents': testAgents  }
        headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)

        # log message
        content = {'extensivetesting-url': url, 'cmd': 'run-test', 'jsessionid': self.__jsessionid,
                    'test-path': testPath, 'project-name': projectName, 'test-inputs': testInputs,
                    'test-agents': testAgents }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="test run", details=tpl )
        
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200: 
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'run-test' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="test run error", details=tpl )
            else:
                # decode json body
                rsp = json.loads(r.text)

                # log message
                content = { 'cmd': 'run-test' }
                content.update(rsp)
                
                ret = content["test-id"]
                tpl = self.template(name=self.__class__.__name__.upper(), content=content)
                self.logResponse(msg="executed", details=tpl  )

        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "run-test" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="test run exception", details=tpl )
            
        return ret
    @doc_public 
    def testStatus(self, testIds=[], logEvents=True):
        """
        """
        ret = False
        if self.__jsessionid is None: 
            return ret
            
        uri = 'rest/results/follow'
        payload = { "test-ids":  testIds}
        headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)

        # log message
        if logEvents:
            content = {'extensivetesting-url': url, 'cmd': 'get-test-result', 'jsessionid': self.__jsessionid,
                        "test-ids":  testIds }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logRequest(msg="get test(s) result(s)", details=tpl )
        
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200: 
                if logEvents:
                    content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'get-test-result' }
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="test result error", details=tpl )
            else:
                # decode json body
                rsp = json.loads(r.text)
                
                # log message
                content = { 'cmd': 'get-result' }
                content.update(rsp)
                
                ret = rsp
                if logEvents:
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content)
                    self.logResponse(msg="test(s) result(s)", details=tpl  )

        except Exception as e: # log message
            if logEvents:
                content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "get-test-result" }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="test result exception", details=tpl )
                
        return ret
     