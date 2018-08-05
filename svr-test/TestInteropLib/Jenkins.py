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
    
from jenkinsapi.jenkins import Jenkins

class Jenkins(TestInteropLib.InteropPlugin):
    """
    Jenkins plugin
    Sample on /Samples/Tests_Interop/06_Jenkins
    """
    @doc_public
    def __init__(self, parent, url, login, password, port=8080, verifySsl=False):
        """
        Jenkins interop
        
        @param parent: testcase parent
        @type parent: testcase
        
        @param url: jenkins url
        @type url: string
        
        @param port: jenkins port (default=8080)
        @type port: integer
        
        @param login: login for api
        @type login: string
        
        @param password: password for api
        @type passord: string    
        
        @param verifySsl: check ssl server cert (default=False)
        @type verifySsl: boolean
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        
        self.__url = url
        self.__login = login
        self.__password = password
        self.__port = port
        self.__certCheck = verifySsl
        self.__server = None
    @doc_public
    def server(self):
        """
        Return the server instance
        """
        return self.__server
    @doc_public    
    def authenticate(self):
        """
        Authenticate to jenkins server

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False

        # log message
        content = {'jenkins-url': self.__url, 'jenkins-port': self.__port, 'login':"%s" % self.__login, 'cmd': 'authenticate' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="authenticate", details=tpl )
        
        try:
            self.__server = Jenkins( "%s:%s" % (self.__url, self.__port), username=self.__login, 
                                    password=self.__password, ssl_verify=self.__certCheck)

            content = {'jenkins-version': self.__server.version, 'cmd': 'authenticated' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="authenticated", details=tpl )
            
            ret = True
        except Exception as e:  # log message
            content = { "jenkins-error": "%s" % e, "cmd": "authenticate" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="authenticate error", details=tpl )

        return ret
    @doc_public
    def disableJob(self, jobName):
        """
        Disable job according to the name passed in argument
        
        @param jobName: job name to disable
        @type jobName: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False 

        # log message
        content = {'jenkins-url': self.__url, 'jenkins-port': self.__port, 'cmd': 'disable-job', 'job-name': jobName }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="disable job", details=tpl )
        
        try:
            if not self.__server.has_job(jobName):
                raise Exception("Job %s not found" % jobName)
            
            job_instance = self.__server.get_job(jobName)
            job_instance.disable()
            
            content = { 'cmd': 'disable-job' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="job disabled", details=tpl )
            
            ret = True
        except Exception as e:  # log message
            content = { "jenkins-error": "%s" % e, "cmd": "disable-job" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="disable job error", details=tpl )

        return ret
    @doc_public
    def enableJob(self, jobName):
        """
        Enable job according to the name passed in argument
        
        @param jobName: job name to enable
        @type jobName: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False 

        # log message
        content = {'jenkins-url': self.__url, 'jenkins-port': self.__port, 'cmd': 'enable-job', 'job-name': jobName }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="enable job", details=tpl )
        
        try:
            if not self.__server.has_job(jobName):
                raise Exception("Job %s not found" % jobName)
            
            job_instance = self.__server.get_job(jobName)
            job_instance.enable()
            
            content = { 'cmd': 'enable-job' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="job enabled", details=tpl )
            
            ret = True
        except Exception as e:  # log message
            content = { "jenkins-error": "%s" % e, "cmd": "enable-job" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="enable job error", details=tpl )

        return ret
    @doc_public        
    def runningJob(self, jobName):
        """
        Check if the job according to the name passed in argument is running
        
        @param jobName: job name to check if running
        @type jobName: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False 

        # log message
        content = {'jenkins-url': self.__url, 'jenkins-port': self.__port, 'cmd': 'running-job', 'job-name': jobName }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="running job", details=tpl )
        
        try:
            if not self.__server.has_job(jobName):
                raise Exception("Job %s not found" % jobName)
            
            job_instance = self.__server.get_job(jobName)
            if job_instance.is_running():
                ret = True
                content = { 'cmd': 'running-job' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="job is running", details=tpl )
            else:
                content = { 'cmd': 'running-job' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="job not running", details=tpl )
        except Exception as e:  # log message
            content = { "jenkins-error": "%s" % e, "cmd": "running-job" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="running job error", details=tpl )

        return ret
    @doc_public    
    def buildJob(self, jobName, jobParams={}):
        """
        Build the job according to the name passed in argument
        
        @param jobName: job name to check if running
        @type jobName: string
        
        @param jobParams: job parameters
        @type jobParams: dict
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False 

        # log message
        content = {'jenkins-url': self.__url, 'jenkins-port': self.__port, 'cmd': 'build-job', 
                    'job-name': jobName, 'job-parameters': "%s" % jobParams  }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="running job", details=tpl )
        
        try:
            if not self.__server.has_job(jobName):
                raise Exception("Job %s not found" % jobName)

            self.__server.build_job(jobName, jobParams)

            content = { 'cmd': 'build-job' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="job builed", details=tpl )
            
            ret = True
        except Exception as e:  # log message
            content = { "jenkins-error": "%s" % e, "cmd": "build-job" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="build job error", details=tpl )

        return ret
    @doc_public    
    def runJob(self, jobName, jobParams={}):
        """
        Run the job according to the name passed in argument and wait until the build is finished
        
        @param jobName: job name to check if running
        @type jobName: string
        
        @param jobParams: job parameters
        @type jobParams: dict
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False 

        # log message
        content = {'jenkins-url': self.__url, 'jenkins-port': self.__port, 'cmd': 'run-job', 
                    'job-name': jobName, 'job-parameters': "%s" % jobParams }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="run job", details=tpl )
        
        try:
            if not self.__server.has_job(jobName):
                raise Exception("Job %s not found" % jobName)

            job_instance = self.__server.get_job(jobName)
            qi = job_instance.invoke(build_params=jobParams)
            
            if qi.is_queued() or qi.is_running():
                qi.block_until_complete()

            content = { 'cmd': 'run-job' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="job builed", details=tpl )
            
            build = qi.get_build()
            ret = build.is_good()
        except Exception as e:  # log message
            content = { "jenkins-error": "%s" % e, "cmd": "run-job" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="run job error", details=tpl )

        return ret