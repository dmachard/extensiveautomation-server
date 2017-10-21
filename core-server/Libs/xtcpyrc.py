#!/usr/bin/env python
#-*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2014-2017 Jean-Vianney OBLIN (jv.oblin@gmail.com)
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
#
# Updated v2: Denis Machard
# -------------------------------------------------------------------

import os
import hashlib
import json
import xmlrpclib
import zlib

CODE_ERROR = 500
CODE_DISABLED = 405
CODE_NOT_FOUND = 404
CODE_ALREADY_EXISTS = 420
CODE_ALREADY_CONNECTED = 416
CODE_FORBIDDEN = 403
CODE_FAILED = 400
CODE_OK = 200

class SrvConnector:
    """
    This class allows to create the object to manage remotely xtc
    """
    def __init__(self, server, login, password, port=443, https=True, path="/xmlrpc/"):
        """
        Constructor for SrvConnector

        @param server: IP or FQDN
        @type server: string

        @param login: your login
        @type login: string

        @param password: your password
        @type password: string

        @param port: tcp port to connect on server. Default is 443.
        @type port: int

        @param https: default value is True for ssl usage. Otherwise set False
        @type https: boolean

        @param path: path on xtc server
        @type path: string
        """
        try:
            if server and login:
                self.login = login
                if https:
                    proto = "https://"
                else:
                    proto = "http://"
                self.server_url = proto + server + ":" + str(port) + path
                self.srv = xmlrpclib.ServerProxy(self.server_url)
                self.hash_pass = hashlib.sha1(password).hexdigest()
            else:
                raise ValueError("Server and Login can't be empty")
        except xmlrpclib.ProtocolError as err:
            print("A protocol error occurred")
            print("URL: %s" % err.url)
            print("HTTP/HTTPS headers: %s" % err.headers)
            print("Error code: %d" % err.errcode)
            print("Error message: %s" % err.errmsg)


    def scheduleTest(self, testsList ):
        """
        Allows to start remotely one test or more on XTC
        Example: testsList = [ "Common:/Samples/Tests_Unit/01_Initial_test.tux" ]

        @param testsList: list of test to run
        @type testsList: list

        @rtype : a string 
        @return: SUCCESS if it works, otherwise an error message
        """
        ret = "UNKNOWN"
        try:
            if not isinstance( testsList, list):
                raise ValueError("list of test expected")

            if not len(testsList):
                raise ValueError("list can no be empty")

            fromGui = xmlrpclib.Boolean(False)

            if len(testsList) > 1:
                xml_rpc_data = {
                        'tests': testsList, 
                        'later': False, 
                        'run-at': (0,0,0,0,0,0)
                }
                response = self.srv.scheduleTests( self.login, self.hash_pass, xml_rpc_data, fromGui )
            else:
                prjName, testFull = testsList[0].split(":", 1)
                tmpTest, testExt = testFull.rsplit(".", 1)
                testPath, testName = tmpTest.rsplit("/", 1)
                
                data = {
                        'nocontent': True,
                        'testextension': testExt,
                        'prj-id': 0,
                        'prj-name': prjName,
                        'testpath':"%s/%s" % (testPath,testName),
                        'testname': testName,
                        'user-id': 8,
                        'user': self.login,
                        'test-id': 0,
                        'background': True,
                        'runAt': (0, 0, 0, 0, 0, 0),
                        'runType': 1,
                        'runNb': 1,
                        'withoutProbes': False,
                        'debugActivated': False,
                        'withoutNotif': False,
                        'noKeepTr': False,
                        'fromTime': (0, 0, 0, 0, 0, 0),
                        'toTime': (0, 0, 0, 0, 0, 0),
                        'breakpoint': False, 
                        'step-by-step': False
                    }

                jsoned = json.dumps(data)
                commpressed = zlib.compress(jsoned)
                xml_rpc_data = xmlrpclib.Binary(commpressed)

                response = self.srv.scheduleTest( self.login, self.hash_pass, xml_rpc_data, fromGui )

            methode, responseCode, responseData = response

            """ For scheduleTest, authenticateClient method is returned if an authentication error occurs"""
            if methode == "authenticateClient":
                #authenticationCode, other = responseData
                authenticationCode, userRights, userId, updateClient = responseData
                if authenticationCode == CODE_ERROR:
                    raise Exception("%i Authentication Error" % CODE_ERROR)
                elif authenticationCode == CODE_DISABLED:
                    raise Exception("%i User disabled" % CODE_DISABLED)
                elif authenticationCode == CODE_NOT_FOUND:
                    raise Exception("%i User not found" % CODE_NOT_FOUND)
                elif authenticationCode == CODE_ALREADY_CONNECTED:
                    raise Exception("%i Alreay Connected" % CODE_ALREADY_CONNECTED)
                elif authenticationCode == CODE_FORBIDDEN:
                    raise Exception("%i Access not authorized" % CODE_FORBIDDEN)
                elif authenticationCode == CODE_FAILED:
                    raise Exception("%i Failed" % CODE_FAILED)
                else:
                    raise Exception("Unknwon authentication error")
            
            elif methode == "scheduleTests":
                if responseCode == CODE_OK:
                    ret = "SUCCESS"
                elif responseCode == CODE_ERROR:
                    ret = "FAILED"
            
            elif methode == "scheduleTest":
                if responseCode == CODE_OK:
                    ret = "SUCCESS"
                elif responseCode == CODE_ERROR:
                    ret = "FAILED"
            else:
                raise Exception("Unknown xmlrpc method")
        
        except xmlrpclib.Fault as err:
            errorMsg = "XMLRPCLIB Fault : %d %s" % (err.faultCode, err.faultString)
            ret = errorMsg
        except Exception as err:
            ret = err
        return ret
