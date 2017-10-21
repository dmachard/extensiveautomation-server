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

import shutil
import subprocess
import urllib

class GitRepository(object):
    """
    """
    def __init__(self, local, remote, username='', password='', email='', bin="/usr/bin/git"):
        """
        """
        self.bin_git = bin
        self.local_repo_path = local
        self.remote_url = remote
        self.repo_username = username
        self.repo_password = password
        self.user_email = email
        
        self.__executeCommand(command=["config", "user.email", "\"%s\"" % self.user_email ])
        self.__executeCommand(command=["config", "user.name", "\"%s\"" % self.repo_username ])
        
    def __executeCommand(self, command):
        """
        """
        command.insert(0, self.bin_git)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.local_repo_path)
        (output, errors) = p.communicate()
        return output, errors
        
    def __prepareAuthUrl(self):
        """
        """
        url_split = self.remote_url.split("://", 1)
        
        urlencoded_username = ''
        urlencoded_password = ''
        if len(self.repo_username):
            urlencoded_username = urllib.quote(self.repo_username.strip(), safe='')
        if len(self.repo_password):
            urlencoded_password = urllib.quote(self.repo_password.strip(), safe='')
            
        auth = [url_split[0]]
        auth.append( "://" )
        if len(urlencoded_username): 
            auth.append( urlencoded_username )
            if not len(urlencoded_password):
                auth.append( "@" )
        if len(urlencoded_password):       
            auth.append( ":" )    
            auth.append( urlencoded_password )
            auth.append( "@" )
        auth.append(url_split[1])    
        return "".join(auth)

    def remove(self):
        """
        """
        shutil.rmtree(self.local_repo_path)

    def clone(self):
        """
        """
        return self.__executeCommand(["clone", self.__prepareAuthUrl(), self.local_repo_path])
        
    def add(self):
        """
        """
        return self.__executeCommand(["add", "--all",  "."])
        
    def commit(self, msg):
        """
        """
        return self.__executeCommand(["commit", "-m %s" % msg])
   
    def push(self):
        """
        """
        return self.__executeCommand(["push", self.__prepareAuthUrl()])
        
class Git(TestInteropLib.InteropPlugin):
    """
    Git plugin
    """
    @doc_public
    def __init__(self, parent, local, remote, username='', password='', email='admin@extensivetesting.org'):
        """
        Git interop
        Sample on /Samples/Tests_Interop/04_Git

        @param parent: testcase parent
        @type parent: testcase

        @param local: local repository
        @type local: string

        @param remote: remote git http url
        @type remote: string

        @param username: username (default=)
        @type username: string

        @param password: password (default=)
        @type password: string

        @param email: user email (default=admin@extensivetesting.org)
        @type email: string        
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        self.repoDir = local
        self.remoteUrl = remote
        self.repoUsername = username
        self.repoPassword = password
        
        self.repo = GitRepository(local=self.repoDir, remote=self.remoteUrl, 
                                username=self.repoUsername, password=self.repoPassword,
                                email=email, bin="/usr/bin/git")
    @doc_public
    def remove(self):
        """
        Remove the local repository 

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        # log message
        content = {'local-repo': self.repoDir, 'cmd': 'remove' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="remove", details=tpl )
        
        try:
            self.repo.remove()

            # response
            content = { 'cmd': 'remove' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="done", details=tpl )
            
            ret = True
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "remove" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="remove exception", details=tpl )
        
        return ret
    @doc_public    
    def add(self, commitMsg):
        """
        Add and commit the files to the remote git repository 

        @param commitMsg: commit message
        @type commitMsg: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        # log message
        content = {'remote-url': self.remoteUrl, 'locate-path': self.repoDir, 'cmd': 'add',
                   'login': self.repoUsername }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="add", details=tpl )
        
        try:
            msg = []
            o,r = self.repo.add()
            if "fatal" in r: raise Exception(r)
            msg.append(o)
            
            o,r = self.repo.commit(commitMsg)
            if "fatal" in r: raise Exception(r)
            msg.append(o)
            
            # response
            content = { 'cmd': 'add', 'details': "\n".join(msg) }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="done", details=tpl )
            
            ret = True
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "add" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="add exception", details=tpl )
        
        return ret
    @doc_public    
    def push(self):
        """
        Push the changes to the remote git repository 

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        # log message
        content = {'remote-url': self.remoteUrl, 'locate-path': self.repoDir, 'cmd': 'push',
                   'login': self.repoUsername }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="push", details=tpl )
        
        try:
            o,r = self.repo.push()
            if "fatal" in r: raise Exception(r)

            # response
            content = { 'cmd': 'push', 'details': o }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="done", details=tpl )
            
            ret = True
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "push" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="push exception", details=tpl )
        
        return ret
    @doc_public    
    def clone(self):
        """
        Clone the remote git repository 

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        
        # log message
        content = {'remote-url': self.remoteUrl, 'locate-path': self.repoDir, 'cmd': 'cloning',
                   'login': self.repoUsername }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="cloning", details=tpl )
        
        try:
            o,r = self.repo.clone()
            if "fatal" in r: raise Exception(r)
            
            # response
            content = { 'cmd': 'cloning', 'details': o }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="done", details=tpl )
            
            ret = True
        except Exception as e:
            content = { "response-code": "unknown", "response-more": "%s" % e, "cmd": "cloning" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="cloning exception", details=tpl )
        
        return ret