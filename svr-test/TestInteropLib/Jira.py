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

class Jira(TestInteropLib.InteropPlugin):
    """
    Jira plugin
    """
    @doc_public
    def __init__(self, parent, url, login, password, project, verifySsl=False, apiVersion="2", proxies={} ):
        """
        Jira interop
        Implementation based on documentation https://docs.atlassian.com/jira/REST
        Sample on /Samples/Tests_Interop/01_Jira
        
        @param parent: testcase parent
        @type parent: testcase
        
        @param url: jira url api
        @type url: string
        
        @param login: login for jira api
        @type login: string
        
        @param password: password for jira api
        @type passord: string     
        
        @param project: project
        @type project: string    
        
        @param verifySsl: check ssl server cert (default=False)
        @type verifySsl: boolean

        @param apiVersion: api version (default=2)
        @type apiVersion: string
        
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
        self.__currentApi = apiVersion
        self.__project = project
        self.__context = None
        self.__proxies = proxies
    @doc_public    
    def context(self):
        """
        Return the context
        """
        return self.__context
    @doc_public    
    def issueTypes(self, name):
        """
        Return issue type ID according to the name
        
        @param name: issue type name
        @type name: string   

        @return: issue type id
        @rtype: string
        """
        issueId = ''
        for issueType in self.__context['issue-types']:
            if issueType['name'] == name:
                issueId = issueType['id']
        return issueId

    def __loadContext(self, projectId):
        """
        Load context
        """
        headers = {'cookie': 'JSESSIONID=%s' % self.__jsessionid}
        
        uri = 'rest/api/%s/project/%s/components' % (self.__currentApi,projectId)
        r = requests.get( "%s/%s" % (self.__url, uri),headers=headers, verify=self.__certCheck, proxies=self.__proxies)
        if r.status_code == 200: self.__context['components'] = json.loads(r.text)

        uri = 'rest/api/%s/project/%s/versions' % (self.__currentApi,projectId)
        r = requests.get( "%s/%s" % (self.__url, uri),headers=headers, verify=self.__certCheck, proxies=self.__proxies)
        if r.status_code == 200: self.__context['versions'] = json.loads(r.text)

        uri = 'rest/api/%s/project/%s/statuses' % (self.__currentApi,projectId)
        r = requests.get( "%s/%s" % (self.__url, uri),headers=headers, verify=self.__certCheck, proxies=self.__proxies)
        if r.status_code == 200: self.__context['statuses'] = json.loads(r.text)
        
        uri = 'rest/api/%s/issuetype' % (self.__currentApi)
        r = requests.get( "%s/%s" % (self.__url, uri),headers=headers, verify=self.__certCheck, proxies=self.__proxies)
        if r.status_code == 200: self.__context['issue-types'] = json.loads(r.text)
    @doc_public
    def signin(self):
        """
        Login to jira

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        uri = 'rest/auth/1/session'
        payload = { "username": self.__login, "password": self.__password }
        headers = {'content-type': 'application/json'}        
        url = "%s/%s" % (self.__url, uri)

        # log message
        content = {'jira-url': url, 'username':"%s" % self.__login, 'cmd': 'signin' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="sigin", details=tpl )
        
        try:
            r = requests.post( url, data=json.dumps(payload), proxies=self.__proxies,
                                headers=headers, verify=self.__certCheck)
            if r.status_code != 200:  # log message
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'signin' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="signin error", details=tpl )
                
            else:
                # decode json body
                rsp = json.loads(r.text)
                self.__jsessionid = rsp['session']['value']

                ret = True
                
                # intialize the user context
                uri = 'rest/api/%s/project' % self.__currentApi
                headers = {'cookie': 'JSESSIONID=%s' % self.__jsessionid}
                r = requests.get( "%s/%s" % (self.__url, uri),headers=headers, 
                                    proxies=self.__proxies, verify=self.__certCheck)
                if r.status_code != 200:  raise Exception("unable to get projects list")
                
                for prj in json.loads(r.text):
                    if prj['key'] == self.__project: 
                        self.__context = {'project': prj } 
                        break
                
                if self.__context is None: 
                    ret = False
                else:
                    self.__loadContext(projectId=self.__context['project']['id'])

                    # log message
                    content = {'jsessionid': self.__jsessionid, 'cmd': 'signin' }
                    content.update(self.__context)
                    tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                    self.logResponse(msg="logged", details=tpl )

        except Exception as e:  # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "signin" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="signin exception", details=tpl )

        return ret
    @doc_public    
    def signout(self):
        """
        Logout from jira

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if self.__jsessionid is None: 
            return ret
            
        uri = 'rest/auth/1/session'
        headers = {'cookie': 'JSESSIONID=%s' % self.__jsessionid}
        url = "%s/%s" % (self.__url, uri)

        # log message
        content = {'jira-url': url, 'cmd': 'sigout', 'jsessionid': self.__jsessionid }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="sigout", details=tpl )
        
        try:
            r = requests.delete( url,headers=headers, verify=self.__certCheck, proxies=self.__proxies)
            if r.status_code != 204: 
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'sigout' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="sigout error", details=tpl )
            else:
                # log message
                content = {'jsessionid': self.__jsessionid, 'cmd': 'signout' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="log out", details=tpl )
                
                ret = True
                
        except Exception as e: # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "sigout" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="sigout exception", details=tpl )
            
        return ret
    @doc_public
    def createIssue(self, summary, description, issueTypeId, assignee):
        """
        Create issue      
        
        @param summary: issue summary
        @type summary: string
        
        @param description: issue description
        @type description: string
        
        @param issueTypeId: issue type id
        @type issueTypeId: string
        
        @param assignee: issue assigned to
        @type assignee: string
        
        @return: issue key/id on success, None otherwise
        @rtype: dict/none
        """
        ret = None
        if self.__jsessionid is None: 
            return ret
            
        uri = 'rest/api/%s/issue' % self.__currentApi
        headers = {'cookie': 'JSESSIONID=%s' % self.__jsessionid, 'content-type': 'application/json'}

        url = "%s/%s" % (self.__url, uri)
        
        data = {
            "fields": {
                "project": {
                    "id": "%s" % self.context()['project']['id']
                },
                "summary": summary,
                "issuetype": {
                    "id": "%s" % issueTypeId
                },
                "assignee": {
                    "name": "%s" % assignee
                }
            }
        }

        # log message
        content = {'jsessionid': self.__jsessionid, 'jira-url': url , 'cmd': 'create-issue' }
        content.update(data)
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="create issue", details=tpl )
        
        try:
            r = requests.post( url,headers=headers,  verify=self.__certCheck, 
                                proxies=self.__proxies, data=json.dumps(data) )
            if r.status_code != 201: 
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'create-issue' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="create issue error", details=tpl )
            else:
                ret = json.loads(r.text)

                # log message
                content = {'jsessionid': self.__jsessionid, 'cmd': 'create-issue' }
                content.update(ret)
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="issue created", details=tpl )
                
        except Exception as e:
            # log message
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "create-issue" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="create issue exception", details=tpl )

        return ret