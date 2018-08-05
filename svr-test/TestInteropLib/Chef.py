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
    
import chef


class Chef(TestInteropLib.InteropPlugin):
    """
    Chef plugin
    Sample on /Samples/Tests_Interop/09_Chef
    """
    @doc_public
    def __init__(self, parent, url, login, key, port=4000, verifySsl=False):
        """
        Chef interop,
        Documentation http://pychef.readthedocs.io
        
        @param parent: testcase parent
        @type parent: testcase
        
        @param url: jenkins url
        @type url: string
        
        @param port: jenkins port (default=8080)
        @type port: integer
        
        @param login: login for api
        @type login: string
        
        @param key: password for api
        @type key: string    
        
        @param verifySsl: check ssl server cert (default=False)
        @type verifySsl: boolean
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        
        self.__url = url
        self.__login = login
        self.__key = key
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
        Authenticate to chef server

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False

        # log message
        content = {'chef-url': self.__url, 
                   'chef-port': self.__port, 
                   'login':"%s" % self.__login, 
                   'cmd': 'authenticate' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="authenticate", details=tpl )
        
        try:
            self.__server = chef.ChefAPI(url="%s:%s" % (self.__url, self.__port), 
                                         key=self.__key, 
                                         client=self.__login,
                                         headers={}, 
                                         ssl_verify=self.__certCheck)

            content = {'cmd': 'authenticated' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="authenticated", details=tpl )
            
            ret = True
        except Exception as e:  # log message
            content = { "chef-error": "%s" % e, "cmd": "authenticate" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="authenticate error", details=tpl )

        return ret