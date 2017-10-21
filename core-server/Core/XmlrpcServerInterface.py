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

from twisted.web import xmlrpc, server
from twisted.internet import reactor
from twisted.internet import ssl
import threading
import os
import zlib
import base64
import time

try:
    # python 2.4 support
    import simplejson as json
except ImportError:
    import json

import Context
import RepoManager
import TaskManager
import StatsManager
import RepoTests
import RepoArchives
import HelperManager
import ProbesManager
import AgentsManager
import ToolboxManager
import RepoAdapters
import RepoLibraries
import ProjectsManager
import XmlrpcServerRights
import TestModel

from Libs import Settings, Logger

import Libs.FileModels.TestSuite as TestSuite
import Libs.FileModels.TestUnit as TestUnit
import Libs.FileModels.TestPlan as TestPlan
import Libs.FileModels.TestAbstract as TestAbstract

def authentication(func):
    """
    Decorator to log xmlrpc call
    """
    def wrapper(*args, **kwargs):
        """
        """
        # init the wrapper
        t = time.time()
        responseCode = Context.CODE_OK
        funcname = func.__name__
        # extract login, password and from gui arg
        try:
            login = args[1]
            password = args[2]
            fromGui = args[4]
        except Exception as e:
            Logger.ClassLogger().error( err="WSI - bad args on authentication: %s" % str(args) )
            return ( 'authenticateClient', Context.CODE_ERROR, {} )

        rightsExpected = XmlrpcServerRights.instance().XMLRPC_RIGHTS[funcname]
        Logger.ClassLogger().info(txt="WSI - calling %s [Login=%s]" % (funcname, login ) )
        
        # authentication
        rCode, rights = Context.instance().checkAuthorization( 
                                                                login = login, 
                                                                password = password, 
                                                                rightsExpected = rightsExpected, 
                                                                fromGui=fromGui 
                                                            )
        if rCode is not Context.CODE_OK:
            return ( 'authenticateClient', Context.CODE_OK, (rCode, False, 0, False) )
        
        # authentication successful so continue, passing users rights according to the function called
        kwargs['rights'] = rights
        res = {}
        try:
            responseCode, res = func(*args, **kwargs)
        except Exception as e:
            Logger.ClassLogger().fatal( err="%s exception during call: %s" % (funcname, e) )
            responseCode = Context.CODE_ERROR
            
        # endding the function
        Logger.ClassLogger().trace(txt="WSI - ending %s [Login=%s] [Runtime=%s]" % (funcname, login, (time.time()-t)) )
        return (funcname.split('xmlrpc_')[1],responseCode,res)
    return wrapper

def unauthenticated(func):
    """
    Decorator to log xmlrpc call without authentication
    """
    def wrapper(*args, **kwargs):
        """
        """
        # init the wrapper
        t = time.time()
        responseCode = Context.CODE_OK
        funcname = func.__name__

        rightsExpected = XmlrpcServerRights.instance().XMLRPC_RIGHTS[funcname]
        Logger.ClassLogger().info(txt="WSI - calling %s" % (funcname ) )

        
        # authentication successful so continue, passing users rights according to the function called
        res = {}
        try:
            responseCode, res = func(*args, **kwargs)
        except Exception as e:
            Logger.ClassLogger().fatal( err="%s exception during call: %s" % (funcname, e) )
            responseCode = Context.CODE_ERROR
            
        # endding the function
        Logger.ClassLogger().trace(txt="WSI - ending %s [Runtime=%s]" % (funcname, (time.time()-t)) )
        return (funcname.split('xmlrpc_')[1],responseCode,res)
    return wrapper

class WebServicesUsers(xmlrpc.XMLRPC, Logger.ClassLogger):
    """
    Web service functions are prefixed with xmlrpc_
    All WS function returns always a tuple of three values
        - function name (str)
        - response code (int)
        - response data (dict, str)
        
    Responses codes can be equals to:
        CODE_ERROR = 500
        CODE_DISABLED = 405
        CODE_NOT_FOUND = 404
        CODE_ALREADY_EXISTS = 420
        CODE_ALREADY_CONNECTED = 416
        CODE_FORBIDDEN = 403
        CODE_FAILED = 400
        CODE_OK = 200
    """
    def trace(self, txt):
        """
        Trace message, internal function
        """
        Logger.ClassLogger.trace(self, txt="WSI - %s" % txt)

    @unauthenticated
    def xmlrpc_authenticateClient ( self, data={}, fromGui=False, cltIp='', cltPort=0, userLogin='', userPwd='', version='', os='', portable=False):
        """
        Authenticate the client, check the login and the password
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'channel-id': tuple, 'login': str, 'password': str, 'ver': str, 'os': str }
        @type data: dict
        
        @param cltIp: client ip
        @type cltIp: string
        
        @param cltPort: client port (default=0)
        @type cltPort: integer

        @param userLogin: user login
        @type userLogin: string

        @param userPwd: user password (sha1)
        @type userPwd: string
        
        @param version: client version, expected format A.B.C
        @type version: string
        
        @param os: client os
        @type os: string
        
        @param portable: portable client (default=False)
        @type portable: boolean
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'channel-id': (cltIp, cltPort), 'login': userLogin, 'password': userPwd,
                                   'ver': version, 'os': os, 'portable': portable }
        if 'portable' not in data: data['portable'] = False # just for backward compatibility
        
        self.info('Authenticate client: Login=%s Password=%s ChannelID=%s' % ( data['login'], data['password'], str(data['channel-id']) ) )

        client = ( data['channel-id'][0], data['channel-id'][1] ) # ip, port
        rsp = Context.instance().isAuthorized( client = client, login = data['login'], 
                                                password = data['password'], fromGui=fromGui )

        clientToUpdate = Context.instance().checkClientUpdate(currentVersion= data['ver'], 
                                                systemOs = data['os'], portable=data['portable'] )
        rsp = rsp + ( clientToUpdate, )
        return (code,rsp)
    
    @authentication
    def xmlrpc_checkUpdateAuto (self, login, password, data={}, fromGui=False, version='', os='', portable=False, rights=[]):
        """
        Check if an update of the client is needed for automatic mode. The user need to provide the current version and operating system.
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string
        
        @param password: sha1 of the password 
        @type password: string
        
        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'ver': str, 'os': str }
        @type data: dict
        
        @param version: client version, expected format A.B.C
        @type version: string
        
        @param os: client os
        @type os: string
        
        @param portable: portable client (default=False)
        @type portable: boolean
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        
        if not len(data): data = {'ver': version, 'os': os, 'portable': portable }
        if 'portable' not in data: data['portable'] = False # for backward compatibility
        
        rsp = Context.instance().checkClientUpdate(currentVersion= data['ver'], systemOs = data['os'], 
                                                    portable=data['portable'])
        return (code,rsp)

    @authentication
    def xmlrpc_checkUpdate (self, login, password, data={}, fromGui=False, version='', os='', portable=False, rights=[]):
        """
        Check if an update of the client is needed for automatic mode. The user need to provide the current version and operating system.
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'ver': str, 'os': str }
        @type data: dict
        
        @param version: client version, expected format A.B.C
        @type version: string
        
        @param os: client os
        @type os: string
        
        @param portable: portable client (default=False)
        @type portable: boolean
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        if not len(data): data = {'ver': version, 'os': os, 'portable': portable }
        if 'portable' not in data: data['portable'] = False # for backward compatibility
        
        rsp = Context.instance().checkClientUpdate(currentVersion= data['ver'], systemOs = data['os'],
                                                    portable=data['portable'])
        return (code,rsp)

    @authentication
    def xmlrpc_replayTest (self, login, password, data={}, fromGui=False, testid=0, rights=[]):
        """
        Replay a test if existing in the task manager
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'tid': int }
        @type data: dict
        
        @param testid: test id (default=0)
        @type testid: integer
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        if not len(data): data = {'tid': testid }
        rsp = TaskManager.instance().replayTask( tid = data['tid'] )
        return (code,rsp)

    @authentication
    def xmlrpc_addDevTime (self, login, password, data={}, fromGui=False, projectId=0, userId=0, duration=0, 
                                isTs=False, isTp=False, isTu=False, isTg=False, isTa=False, rights=[]):
        """
        Replay a test if existing in the task manager
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'prj-id': int, 'user-id': int, 'duration': int, 'is-ts': bool, 'is-tp': bool, 'is-tu': bool, 'is-tg': bool, 'is-ta': bool }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'prj-id': projectId, 'user-id': userId, 'duration': duration,
                                  'is-ts': isTs, 'is-ta': isTa, 'is-tg': isTg, 'is-tp': isTp, 'is-tu': isTu}
        
        # test not save; change the project id to the default
        prjId = int(data['prj-id'])
        if prjId == 0: prjId = ProjectsManager.instance().getDefaultProjectForUser(user=login)
        
        # checking authorization    
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=prjId)
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            rsp = StatsManager.instance().addWritingDuration(   
                                                                fromUser=data['user-id'], prjId=prjId,
                                                                writingDuration=data['duration'], isTs=data['is-ts'],
                                                                isTp=data['is-tp'], isTu=data['is-tu'], isTg=data['is-tg'],
                                                                isTa=data['is-ta']
                                                            )
        return (code,rsp)

    @authentication
    def xmlrpc_checkDesignTest (self, login, password, data, fromGui=False, rights=[]):
        """
        Check the syntax of a test
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: json compressed {'testglobal': list, 'testplan': list, 'testunit': list, 'testabstract': list, 'properties': dict, 'src': str, 'str2': str, 'testname': str, 'testpath': str, 'background': bool, 'test-id': int, 'user': str}
        @type data: binary

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        try:
            self.trace('decompressing data')
            decompressed_data = zlib.decompress(data.data)
        except Exception as e:
            self.error( "unable to decompress: %s" % e)
        else:
            try:
                data_ = json.loads( decompressed_data )
            except Exception as e:
                self.error( "unable to decode json: %s" % e)
            else:
                # try:
                if 'testglobal' in data_:   
                    rslt, alltests = RepoTests.instance().addtf2tg( data_=data_['testglobal'] )
                    if rslt is not None:
                        return rslt
                    testData = { 'testglobal': alltests, 'properties': data_['properties'] }
                elif 'testplan' in data_:
                    rslt = RepoTests.instance().addtf2tp( data_=data_['testplan'] )
                    if rslt is not None:
                        return rslt
                    testData = { 'testplan': data_['testplan'], 'properties': data_['properties'] }
                else:
                    if 'testunit' in data_:
                        testData = { 'testunit': True, 'src-test': data_['src'], 'src-exec': '', 'properties': data_['properties'] }
                    elif 'testabstract' in data_:
                        testData = { 'testabstract': True, 'src-test': data_['src'], 'src-exec': '', 'properties': data_['properties'] }
                    else:
                        testData = { 'src-test': data_['src'], 'src-exec': data_['src2'], 'properties': data_['properties'] }
                
                task = TaskManager.getObjectTask(   testData=testData, testName=data_['testname'], 
                                                    testPath=data_['testpath'] ,  testUser=data_['user'], 
                                                    testId=data_['test-id'], testBackground=data_['background'],
                                                    projectId=data_['prj-id']
                                                )
                rsp['result'] = task.parseTestDesign()
                del task
        return (code,rsp)
    
    @authentication
    def xmlrpc_checkSyntaxTest (self, login, password, data, fromGui=False, rights=[]):
        """
        Check the syntax of a test
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: json compressed {'testglobal': list, 'testplan': list, 'testunit': list, 'testabstract': list, 'properties': dict, 'src': str, 'str2': str, 'testname': str, 'testpath': str, 'background': bool, 'test-id': int, 'user': str}
        @type data: binary

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        ret = {}
        msg_ = ""
        try:
            self.trace('decompressing data')
            decompressed_data = zlib.decompress(data.data)
        except Exception as e:
            self.error( "unable to decompress: %s" % e)
        else:
            try:
                data_ = json.loads( decompressed_data )
            except Exception as e:
                self.error( "unable to decode json: %s" % e)
            else:
                # try:
                if 'testglobal' in data_:   
                    rslt, alltests = RepoTests.instance().addtf2tg( data_=data_['testglobal'] )
                    if rslt is not None:
                        return rslt
                    testData = { 'testglobal': alltests, 'properties': data_['properties'] }
                elif 'testplan' in data_:       
                    rslt = RepoTests.instance().addtf2tp( data_=data_['testplan'] )
                    if rslt is not None:
                        return rslt
                    testData = { 'testplan': data_['testplan'], 'properties': data_['properties'] }
                else:
                    if 'testunit' in data_: 
                        testData = { 'testunit':True, 'src-test': data_['src'], 'src-exec': '', 'properties': data_['properties'] }
                    elif 'testabstract' in data_: 
                        testData = { 'testabstract':True, 'src-test': data_['src'], 'src-exec': '', 'properties': data_['properties'] }
                    else:
                        testData = { 'src-test': data_['src'], 'src-exec': data_['src2'], 'properties': data_['properties'] }
                
                task = TaskManager.getObjectTask(   testData=testData, testName=data_['testname'], 
                                                    testPath=data_['testpath'] ,  testUser=data_['user'], 
                                                    testId=data_['test-id'], testBackground=data_['background']
                                                )
                ret, msg_ = task.parseTest()        
                del task

        rsp =  (ret , msg_ )
        return (code,rsp)
    
    @authentication
    def xmlrpc_checkSyntaxAdapter (self, login, password, data={}, fromGui=False, path='', ext='', filename='', content='', rights=[]):
        """
        Check the syntax of one adapter
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'path': str, 'extension': str, 'filename': str, 'content': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'path': path, 'extension': ext, 'filename': filename, 'content': content}
        
        pathFile = data['path']
        extFile = data['extension']
        nameFile = data['filename']
        contentFile = str(data['content'])
        ret, ret_msg = RepoAdapters.instance().checkSyntax(content=contentFile)
        
        # set the result
        rsp['ret'] = ret
        rsp['syntax-error'] = ret_msg

        return (code,rsp)
    
    @authentication
    def xmlrpc_checkSyntaxAdapters (self, login, password, data={}, fromGui=False, rights=[]):
        """
        Check global syntax of all adapters
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        ret, ret_msg = RepoAdapters.instance().checkGlobalSyntax()
        rsp['ret'] = ret
        rsp['syntax-error'] = ret_msg

        return (code,rsp)
    
    @authentication
    def xmlrpc_checkSyntaxLibrary (self, login, password, data={}, fromGui=False, path='', ext='', filename='', content='', rights=[]):
        """
        Check the syntax of one library
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'path': str, 'extension': str, 'filename': str, 'content': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'path': path, 'extension': ext, 'filename': filename, 'content': content}
        
        pathFile = data['path']
        extFile = data['extension']
        nameFile = data['filename']
        contentFile = str(data['content'])
        ret, ret_msg = RepoLibraries.instance().checkSyntax(content=contentFile)
        
        rsp['ret'] = ret
        rsp['syntax-error'] = ret_msg

        return (code,rsp)
    
    @authentication
    def xmlrpc_checkSyntaxLibraries (self, login, password, data={}, fromGui=False, rights=[]):
        """
        Check global syntax of all libraries
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        ret, ret_msg = RepoLibraries.instance().checkGlobalSyntax()
        rsp['ret'] = ret
        rsp['syntax-error'] = ret_msg

        return (code,rsp)
    
    @authentication
    def xmlrpc_scheduleTests(self, login, password, data={}, fromGui=False, simultaneous=False, later=False, runAt=(0,0,0,0,0,0), tests=[], rights=[]):
        """
        Schedule several tests on the task manager
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'simultaneous': bool, 'later': later, 'run-at': (0,0,0,0,0,0), 'tests': [ prjname:test, ... ] }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'simultaneous': simultaneous, 'later': later, 'run-at': runAt, 'tests': tests }
        
        runSimultaneous = False
        if 'simultaneous' in data: runSimultaneous = data['simultaneous']
        runLater = data['later']
        runAt = data['run-at']
        testsRun = []
        for t in data['tests']:
            try:
                prjName, absPath = t.split(':', 1)
            except Exception as e:
                self.error("unable to extract project name: %s" % str(e) )
                code = Context.CODE_FAILED
            else:
                prjID = ProjectsManager.instance().getProjectID(name=prjName)
                testPath, testExtension = absPath.rsplit('.', 1)
                if len(testPath.rsplit('/', 1)) > 1:
                    testName = testPath.rsplit('/', 1)[1]
                else:
                    testName = testPath.rsplit('/', 1)[0]

                if testExtension == 'tsx':
                    doc = TestSuite.DataModel()
                    res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjID, testPath, testExtension) )
                    if not res:
                        self.error('unable to read test suite:%s' % testExtension)
                        code = Context.CODE_FAILED
                    else:
                        testData = { 'src-test': doc.testdef, 'src-exec': doc.testexec, 'properties': doc.properties['properties'] }
                        testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 'test-name': testName,
                                            'test-path': testPath, 'test-data': testData } )

                elif testExtension == 'tux':
                    doc = TestUnit.DataModel()
                    res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjID, testPath, testExtension) )
                    if not res:
                        self.error('unable to schedule test unit:%s' % testExtension)
                        code = Context.CODE_FAILED
                    else:
                        testData = { 'testunit': True, 'src-test': doc.testdef, 'src-exec': '', 'properties': doc.properties['properties'] }
                        testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 'test-name': testName,
                                            'test-path': testPath, 'test-data': testData } )
                
                elif testExtension == 'tax':
                    doc = TestAbstract.DataModel()
                    res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjID, testPath, testExtension) )
                    if not res:
                        self.error('unable to schedule test abstract:%s' % testExtension)
                        code = Context.CODE_FAILED
                    else:
                        testData = { 'testabstract': True, 'src-test': doc.testdef, 'src-exec': '', 'properties': doc.properties['properties'] }
                        testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 'test-name': testName,
                                            'test-path': testPath, 'test-data': testData } )
                                            
                elif testExtension == 'tpx':
                    doc = TestPlan.DataModel()
                    res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjID, testPath, testExtension) )
                    if not res:
                        self.error('unable to schedule test plan:%s' % testExtension)
                        code = Context.CODE_FAILED
                    else:
                        rslt = RepoTests.instance().addtf2tp( data_= doc.getSorted() )
                        if rslt is not None:
                            self.error('unable to run several test in test plan')
                            code = Context.CODE_FAILED
                        else:
                            testData = { 'testplan': doc.getSorted(),  'properties': doc.properties['properties'] }
                            testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 'test-name': testName, 
                                                'test-path': testPath, 'test-data': testData } )

                elif testExtension == 'tgx':
                    doc = TestPlan.DataModel()
                    res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjID, testPath, testExtension) )
                    if not res:
                         self.error('unable to schedule test plan:%s' % testExtension)
                         code = Context.CODE_FAILED
                    else:
                        self.trace('reading the test global to run several tests')
                        rslt, alltests = RepoTests.instance().addtf2tg( data_= doc.getSorted() )
                        self.trace('reading test global finished to run several tests')
                        if rslt is not None:
                            self.error('unable to run several test in test global')
                            code = Context.CODE_FAILED
                        else:
                            testData = { 'testglobal': alltests, 'properties': doc.properties['properties'] }
                            testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 'test-name': testName,
                                                'test-path': testPath, 'test-data': testData } )
                else:
                    self.error('test not supported: %s' % testExtension )
                    code = Context.CODE_FAILED

        if len(testsRun):
            ret = TaskManager.instance().addTasks(userName=login, tests=testsRun, runAt=runAt,
                                                    queueAt=runLater, simultaneous=runSimultaneous )
            rsp['ret'] = ret

        return (code,rsp)
    
    @authentication
    def xmlrpc_scheduleTest (self, login, password, data, fromGui=False, returnPath=False, projectId=0, projectName='', testName='', testPath='', testExtension='', userId=0, userName='', 
                                    testId=0, inBackground=False, runType=0, runAt=(0,0,0,0,0,0), runNb=0, noContent=False, 
                                    testProperties={}, testSrc='', testSrcExec='', testGlobal=[], testPlan=[], testUnit=[], testAbstract=[],
                                    withoutProbes=False, debugActivated=False, withoutNotif=False, 
                                    noKeepTr=False, fromTime=(0,0,0,0,0,0), toTime=(0,0,0,0,0,0), stepByStep=False, withBreakpoint=False, rights=[]):
        """
        Schedule a test on the task manager
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: json compressed in base64 {'prj-id': int, 'prj-name': str, 'nocontent': bool, 'testname': str, 'testpath': str, 'testextension': str, 'runType': int, 'runAt': tuple, 'runNb': int, 'withoutProbes': bool, 'debugActivated': bool, 'withoutNotif': bool, 'noKeepTr': bool, 'fromTime': tuple, 'toTime': tuple, 'breakpoint':bool, 'step-by-step': bool }
        @type data: binary

        @return: ws function name, response code, response data=(task-id , test-id, test-name, is-background, is-recursive, is-postponed, is-successive)
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        ret_ = rsp
        try:
            self.trace('schedule test - decompressing data...')
            decompressed_data = zlib.decompress(data.data)
        except Exception as e:
            self.error( "unable to decompress: %s" % e)
            code = Context.CODE_FAILED
        else:
            try:
                data_ = json.loads( decompressed_data )
            except Exception as e:
                self.error( "unable to decode json: %s" % e)
                code = Context.CODE_FAILED
            else:
                recursive = False
                postponed = False
                successive = False
                tsnotfound = False

                # extract project info
                prjId = data_['prj-id']
                prjName = data_['prj-name']
                if prjId == 0 and len(prjName): prjId = ProjectsManager.instance().getProjectID(name=prjName)  
                self.trace('schedule test in project (name=%s, id=%s) ...' % (prjName, prjId) )
               
                # checking project authorization ? if the test is not saved; change the project id to the default
                __prjId = int(prjId)
                if __prjId == 0: __prjId = ProjectsManager.instance().getDefaultProjectForUser(user=login)
                projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=int(__prjId))
                self.trace( "project is authorized ? %s" % projectAuthorized)
                if not projectAuthorized:
                    code = Context.CODE_FORBIDDEN
                    return (code,ret_)
                    
                # no test content
                if 'nocontent' in data_:
                    self.trace( 'cli: schedule the following test - %s/%s.%s' % (prjId, data_['testpath'], data_['testextension']) )
                    if data_['testextension'] == 'tsx':
                        doc = TestSuite.DataModel()
                        res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjId, data_['testpath'], data_['testextension']) )
                        if not res:
                            raise Exception('unable to schedule test suite:%s' % data_['testextension'])
                        else:
                            testData = { 'src-test': doc.testdef, 'src-exec': doc.testexec, 'properties': doc.properties['properties'] }
    
                    elif data_['testextension'] == 'tux':
                        doc = TestUnit.DataModel()
                        res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjId, data_['testpath'], data_['testextension']) )
                        if not res:
                            raise Exception('unable to schedule test unit:%s' % data_['testextension'])
                        else:
                            testData = { 'testunit': True, 'src-test': doc.testdef, 'src-exec': '', 'properties': doc.properties['properties'] }
                    
                    elif data_['testextension'] == 'tax':
                        doc = TestAbstract.DataModel()
                        res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjId, data_['testpath'], data_['testextension']) )
                        if not res:
                            raise Exception('unable to schedule test abstract:%s' % data_['testextension'])
                        else:
                            testData = { 'testabstract': True, 'src-test': doc.testdef, 'src-exec': '', 'properties': doc.properties['properties'] }

                    elif data_['testextension'] == 'tpx':
                        doc = TestPlan.DataModel()
                        res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjId, data_['testpath'], data_['testextension']) )
                        if not res:
                            raise Exception('unable to schedule test plan:%s' % data_['testextension'])
                        else:
                            rslt = RepoTests.instance().addtf2tp( data_= doc.getSorted() )
                            if rslt is not None:
                                return rslt
                            testData = { 'testplan': doc.getSorted(),  'properties': doc.properties['properties'] }
                    
                    elif data_['testextension'] == 'tgx':
                        doc = TestPlan.DataModel()
                        res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjId, data_['testpath'], data_['testextension']) )
                        if not res:
                            raise Exception('unable to schedule test plan:%s' % data_['testextension'])
                        else:
                            self.trace('reading the test global')
                            rslt, alltests = RepoTests.instance().addtf2tg( data_= doc.getSorted() )
                            self.trace('reading test global finished')
                            if rslt is not None:
                                return rslt
                            testData = { 'testglobal': alltests, 'properties': doc.properties['properties'] }
                    else:
                        raise Exception('test extension not supported: %s' % data_['testextension'])

                # content passed as argument
                else:
                    if 'testglobal' in data_:
                        rslt, alltests = RepoTests.instance().addtf2tg( data_=data_['testglobal'] )
                        if rslt is not None:
                            return rslt
                        testData = { 'testglobal': alltests, 'properties': data_['properties'] }

                    elif 'testplan' in data_:
                        rslt = RepoTests.instance().addtf2tp( data_=data_['testplan'] )
                        if rslt is not None:
                            return rslt
                        testData = { 'testplan': data_['testplan'], 'properties': data_['properties'] }
                    
                    else:
                        if 'testunit' in data_:
                            testData = { 'testunit': True, 'src-test': data_['src'], 'src-exec': '', 'properties': data_['properties'] }
                        elif 'testabstract' in data_:
                            testData = { 'testabstract': True, 'src-test': data_['src'], 'src-exec': '', 'properties': data_['properties'] }
                        else:
                            testData = { 'src-test': data_['src'], 'src-exec': data_['src2'], 'properties': data_['properties'] }
                
                #run a test not save; change the project id to the default
                if prjId == 0: prjId = ProjectsManager.instance().getDefaultProjectForUser(user=login)
                
                # register the test
                channelId = False
                if 'channel-id' in data_: channelId = data_['channel-id']
                task = TaskManager.instance().registerTask( 
                                                testData=testData, testName=data_['testname'], testPath=data_['testpath'], testUserId=data_['user-id'],
                                                testUser=data_['user'], testId=data_['test-id'], testBackground=data_['background'],
                                                runAt=data_['runAt'], runType=data_['runType'], runNb=data_['runNb'], withoutProbes=data_['withoutProbes'],
                                                debugActivated=data_['debugActivated'], withoutNotif=data_['withoutNotif'], noKeepTr=data_['noKeepTr'],
                                                testProjectId=prjId, runFrom=data_['fromTime'], runTo=data_['toTime'], stepByStep=data_['step-by-step'], 
                                                breakpoint=data_['breakpoint'], channelId=channelId
                                            )
                taskPath = ""   
                if task.lastError is None:
                    ret = task.getId()
                    taskPath = task.getTestPath(withDate=True)
                    if task.isRecursive():
                        recursive = True
                    if task.isPostponed():
                        postponed = True
                    if task.isSuccessive():
                        successive = True
                else:
                    ret = task.lastError
                    if ret.startswith('No more space left on'):
                        code = Context.CODE_FORBIDDEN

                if returnPath:
                    ret_ = (ret,taskPath)
                else:
                    ret_ =  (ret, data_['test-id'], data_['testname'], data_['background'], recursive, postponed, successive )

        return (code,ret_)
    
    @authentication
    def xmlrpc_rescheduleTest (self, login, password, data={}, fromGui=False, taskId=0, runType=0, runEnabled=False, runAt=(0,0,0,0,0,0), 
                                    runNb=0, withoutProbes=False, debugActivated=False, withoutNotif=False, 
                                    noKeepTr=False, fromTime=(0,0,0,0,0,0), toTime=(0,0,0,0,0,0), rights=[]):
        """
        Reschedule a test if existing in the task manager
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'taskId': int, 'runType': int, 'runEnabled': bool, 'runAt': tuple, 'runNb': int, 'withoutProbes': bool, 'debugActivated': bool, 'withoutNotif': bool, 'noKeepTr': bool, 'fromTime': tuple, 'toTime': tuple }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'taskId': taskId, 'runType': runType, 'runEnabled': runEnabled, 'runAt': runAt, 
                                    'runNb': runNb, 'withoutProbes': withoutProbes, 'debugActivated': debugActivated, 'withoutNotif': withoutNotif, 
                                    'noKeepTr': noKeepTr, 'fromTime': fromTime, 'toTime': toTime }
        
        rsp = TaskManager.instance().updateTask( taskId = data['taskId'], schedType=data['runType'], schedEnabled=data['runEnabled'],
                                                    shedAt=data['runAt'], schedNb=data['runNb'], withoutProbes=data['withoutProbes'],
                                                    debugActivated=data['debugActivated'], withoutNotif=data['withoutNotif'],
                                                    noKeepTr=data['noKeepTr'], schedFrom=data['fromTime'], schedTo=data['toTime'] )
        if rsp is None:
            rsp = False
            code = Context.CODE_NOT_FOUND

        return (code,rsp)
    
    @authentication
    def xmlrpc_loadTestCache(self, login, password, data={}, fromGui=False, mainPath='', subPath='', projectId=0, rights=[]):
        """
        Load test from cache
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'main-path': str, 'sub-path': str, 'project-id': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False };

        if not len(data): data = {'main-path': mainPath, 'sub-path': subPath, 'project-id': projectId}
        
        trPath = data['main-path']
        trSubPath = data['sub-path']
        projectId = data['project-id']
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['project-id'])
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            # extract the testname from the test folder
            timeArch, milliArch, testName, testUser = trSubPath.split(".")
            testName = base64.b64decode(testName)

            rsp['ret'] =  RepoArchives.instance().createTrTmp(mainPath=trPath, subPath=trSubPath, testName=testName,
                                    projectId=projectId)
                                    
        return (code,rsp)
    
    @authentication
    def xmlrpc_unauthenticateClient(self, login, password, data={}, fromGui=False, userLogin='', rights=[]):
        """
        Disconnect client
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string
        
        @param data: example {'login': str}
        @type data: dict

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param userLogin: user login
        @type userLogin: boolean
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        if not len(data): data = {'login': userLogin}
        rsp = Context.instance().unregisterUserFromXmlrpc( login=data['login'] )
        return (code,rsp)

    @authentication
    def xmlrpc_getServerUsage(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Return server usage
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp['usage'] = Context.instance().getUsage(b64=True)
        return (code,rsp)
    
    @authentication
    def xmlrpc_getServerInformations(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Return server information
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp['informations'] = Context.instance().getInformations(user=login, b64=True)
        return (code,rsp)
    
    @authentication
    def xmlrpc_getReleaseNotes(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Return release notes
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        rsp['rn'] = Context.instance().getRn(pathRn=Settings.getDirExec(), b64=True) 
        rsp['rnAdp'] = RepoAdapters.instance().getRn(b64=True)
        rsp['rnLib'] = RepoLibraries.instance().getRn(b64=True)
        rsp['rnToolbox'] = ToolboxManager.instance().getRn(b64=True)
        rsp['rnProbes'] = '' # for backward compatibility
        rsp['rnAgents'] = '' # for backward compatibility

        return (code,rsp)
    
    @authentication
    def xmlrpc_getAdvancedInformations (self, login, password, data={}, fromGui=False, rights=[]):
        """
        Constructs the context of the server, informations to return depend of the type of user
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """ 
        code = Context.CODE_OK; rsp={};

        # new in v12, create a context for the user, avoid to make several sql req in database
        USER_CTX = Context.UserContext(login=login)

        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights :
            rsp['probes'] = ProbesManager.instance().getRunning(b64=True)
            rsp['probes-installed'] = ProbesManager.instance().getInstalled(b64=True)
            rsp['probes-stats'] = ProbesManager.instance().getStats(b64=True)
            rsp['probes-default'] = ProbesManager.instance().getDefaultProbes(b64=True)

            rsp['agents'] = AgentsManager.instance().getRunning(b64=True)
            rsp['agents-installed'] = AgentsManager.instance().getInstalled(b64=True)
            rsp['agents-stats'] = AgentsManager.instance().getStats(b64=True)
            rsp['agents-default'] = AgentsManager.instance().getDefaultAgents(b64=True)
            
        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights \
            or Settings.get('Server', 'level-leader') in rights:
            rsp['projects'] = USER_CTX.getProjects(b64=True)
            rsp['default-project'] = USER_CTX.getDefault()

        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights \
            or Settings.get('Server', 'level-leader') in rights:
            nb_archs, nb_archs_f, archs, stats_archs = RepoArchives.instance().getTree(b64=True,  project=USER_CTX.getDefault())
            rsp['archives'] =  archs
            if Settings.get('Server', 'level-admin') in rights : 
                rsp['stats-repo-archives'] = stats_archs

            rsp['tasks-running'] = TaskManager.instance().getRunning(b64=True, user=USER_CTX)
            rsp['tasks-waiting'] = TaskManager.instance().getWaiting(b64=True, user=USER_CTX)
            rsp['tasks-history'] = TaskManager.instance().getHistory(b64=True, user=USER_CTX)
            rsp['tasks-enqueued'] = TaskManager.instance().getEnqueued(b64=True)

            nb_tests, nb_tests_f, tests, stats_tests = RepoTests.instance().getTree(b64=True, project=USER_CTX.getDefault() )
            rsp['repo'] = tests
            if Settings.get('Server', 'level-admin') in rights :
                rsp['stats-repo-tests'] = stats_tests
                
        if Settings.get('Server', 'level-leader') in rights or Settings.get('Server', 'level-admin') in rights \
            or Settings.get('Server', 'level-tester') in rights or Settings.get('Server', 'level-developer') in rights :
            rsp['help'] = HelperManager.instance().getHelps()

        if Settings.get('Server', 'level-leader') in rights or Settings.get('Server', 'level-admin') in rights \
            or Settings.get('Server', 'level-tester') in rights or Settings.get('Server', 'level-developer') in rights :
            rsp['stats'] = StatsManager.instance().getStats()
        
        if Settings.get('Server', 'level-admin') in rights :
            rsp['stats-server'] = Context.instance().getStats(b64=True)
            rsp['backups-repo-tests'] = RepoTests.instance().getBackups(b64=True)
            rsp['backups-repo-adapters'] = RepoAdapters.instance().getBackups(b64=True)
            rsp['backups-repo-libraries'] = RepoLibraries.instance().getBackups(b64=True)
            rsp['backups-repo-archives'] = RepoArchives.instance().getBackups(b64=True)

        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights :
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                nb_adps, nb_adps_f, adps, stats_adps = RepoAdapters.instance().getTree(b64=True)
                rsp['repo-adp'] = adps
                if Settings.get('Server', 'level-admin') in rights :
                    rsp['stats-repo-adapters'] = stats_adps
            else: # development not authorized
                rsp['repo-adp'] = []
                rsp['stats-repo-adapters'] = {}
                
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                nb_libs, nb_libs_f, libs, stats_libs = RepoLibraries.instance().getTree(b64=True)
                rsp['repo-lib-adp'] = libs
                if Settings.get('Server', 'level-admin') in rights :
                    rsp['stats-repo-libraries'] = stats_libs
                
            else: # development not authorized
                rsp['repo-lib-adp'] = []
                rsp['stats-repo-libraries'] = {}

        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights \
                        or Settings.get('Server', 'level-developer')  :
            rsp['rn'] = Context.instance().getRn(pathRn=Settings.getDirExec(), b64=True) 
            rsp['rnAdp'] = RepoAdapters.instance().getRn(b64=True)
            rsp['rnLibAdp'] = RepoLibraries.instance().getRn(b64=True)
            rsp['rnToolbox'] = ToolboxManager.instance().getRn(b64=True)
            rsp['rnProbes'] = ''; rsp['rnAgents'] = ''; # for backward compatibility
            rsp['informations'] = Context.instance().getInformations(user=USER_CTX, b64=True)

        del USER_CTX

        return (code,rsp)
    
    @authentication
    def xmlrpc_cancelTask (self, login, password, data={}, fromGui=False, taskId=0, taskIds=[], rights=[]):
        """
        Cancel a specific task on the task manager or all
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'taskid': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'taskid': taskId, 'taskids': taskIds, 'cancelall': False}
        
        if 'cancelall' in data:
            if data['cancelall']:
                self.trace('new cancelling all tasks' )
                rsp = TaskManager.instance().cancelAllTasks()
        elif 'taskids' in data:
            self.trace("tasks to cancel: %s" % data['taskids'])
            for taskId in data['taskids']:
                self.trace('cancelling the task %s' % str(taskId) )
                TaskManager.instance().cancelTask( taskId = taskId )
            rsp = True
        elif 'taskid' in data:
            taskId = data['taskid']
            self.trace('cancelling the task %s' % str(taskId) )
            tsk_cancelled = TaskManager.instance().cancelTask( taskId = taskId )
            if tsk_cancelled is None:
                code = Context.CODE_NOT_FOUND
            else:
                rsp = tsk_cancelled
        else:
            self.trace('cancelling all tasks' )
            rsp = TaskManager.instance().cancelAllTasks()

        return (code,rsp)
        
    @authentication
    def xmlrpc_cancelAllTasks (self, login, password, data={}, fromGui=False, rights=[]):
        """
        Cancel all tasks
        Granted levels: ADMIN

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'taskid': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = TaskManager.instance().cancelAllTasks()
        return (code,rsp)
            
    @authentication
    def xmlrpc_killTask (self, login, password, data={}, fromGui=False, taskId=0, taskIds=[], rights=[]):
        """
        Kill a specific task on the task manager or all
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'taskid': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'taskid': taskId, 'taskids': taskIds, 'killall': False}
        
        if 'killall' in data:
            if data['killall']:
                self.trace('new killing all tasks' )
                rsp = TaskManager.instance().killAllTasks()
        elif 'taskids' in data:
            self.trace("tasks to kill: %s" % data['taskids'])
            taskKilled = []
            for taskId in data['taskids']:
                self.trace('killing the task %s' % str(taskId) )
                tsk_killed = TaskManager.instance().killTask( taskId = taskId )
                if tsk_killed is not None:
                    taskKilled.append(tsk_killed)
            rsp = taskKilled
        elif 'taskid' in data:
            taskId = data['taskid']
            self.trace('killing the task %s' % str(taskId) )
            tsk_killed = TaskManager.instance().killTask( taskId = taskId )
            if tsk_killed is None:
                code = Context.CODE_NOT_FOUND
            else:
                rsp = tsk_killed
        else:
            self.trace('killing all tasks' )
            rsp = TaskManager.instance().killAllTasks()

        return (code,rsp)
            
    @authentication
    def xmlrpc_killAllTasks (self, login, password, data={}, fromGui=False, rights=[]):
        """
        Kill all tasks
        Granted levels: ADMIN

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'taskid': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = TaskManager.instance().killAllTasks()
        return (code,rsp)
            
    @authentication
    def xmlrpc_refreshHelper (self, login, password, data={}, fromGui=False, rights=[]):
        """
        Refresh Helper
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp['help'] = HelperManager.instance().getHelps()
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshRepo(self, login, password, data={}, fromGui=False, projectId=0, repoDst=0, saveasOnly=False, partialRefresh=False, forRuns=False, rights=[]):
        """
        Get all files
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string
        
        @param data: example { 'projectid' int, 'repo-dst': int, 'saveas-only': bool, 'partial': bool, 'for-runs': bool }
        @type data: dict
        
        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param projectId: id of the project to refresh (default=0)
        @type projectId: integer
        
        @param repoDst: id of the repository (default=0) Tests=0, Adapters=1, Archives=4, Libraries=5
        @type repoDst: integer
        
        @param saveasOnly: optional argument (default=False)
        @type saveasOnly: boolean
        
        @param partialRefresh: optional argument (default=False)
        @type partialRefresh: boolean
        
        @param forRuns: optional argument (default=False)
        @type forRuns: boolean
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'projectid': projectId, 'repo-dst': repoDst, 'saveas-only': saveasOnly, 
                                    'partial': partialRefresh, 'for-runs': forRuns }
        
        repoType = data['repo-dst']
        refreshSaveAsOnly = data['saveas-only']
        refreshForRuns = data['for-runs']
        
        # for retro compatibility, new in v12
        if 'partial' not in data: data['partial'] = True
        
        rsp['repo-dst'] = repoType
        rsp['saveas-only'] = refreshSaveAsOnly
        rsp['for-runs'] = refreshForRuns
        rsp['projectid'] = data['projectid']
        self.trace('Refresh Repo=%s ProjectId=%s Partial=%s' % (repoType, data['projectid'], data['partial']) )
        
        # repo tests
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights \
            or Settings.get('Server', 'level-tester') in rights or Settings.get('Server', 'level-system') in rights  ):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                nb_tests, nb_tests_f, tests, stats_tests = RepoTests.instance().getTree(b64=True, project=data['projectid'])
                rsp['ret'] = tests
        
        # adapters
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights \
            or Settings.get('Server', 'level-developer') in rights or Settings.get('Server', 'level-system') in rights ):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                nb_adps, nb_adps_f, adps, stats_adps = RepoAdapters.instance().getTree(b64=True)
                rsp['ret'] = adps
            else:
                code = Context.CODE_FORBIDDEN
        
        # libraries
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights \
            or Settings.get('Server', 'level-developer') in rights or Settings.get('Server', 'level-system') in rights ):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                nb_libs, nb_libs_f, libs, stats_libs = RepoLibraries.instance().getTree(b64=True)
                rsp['ret'] = libs
            else:
                code = Context.CODE_FORBIDDEN
                
        # libraries
        elif repoType == RepoArchives.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights \
            or Settings.get('Server', 'level-tester') in rights or Settings.get('Server', 'level-developer') in rights \
            or Settings.get('Server', 'level-system') in rights or Settings.get('Server', 'level-leader') in rights  ):
            
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                nb_archs, nb_archs_f, archs, stats_archs = RepoArchives.instance().getTree(b64=True, fullTree=not data['partial'], project=data['projectid'])
                rsp['ret'] = archs

        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE and repoType != RepoLibraries.REPO_TYPE:
                raise Exception('repo type unknown %s type=%s' % (repoType, type(repoType)) )
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_openFileRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, forceOpen=False, readOnly=False, rights=[]):
        """
        Open file  and return content
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoDst, 'projectid': projectId, 'force-open': forceOpen, 'read-only': readOnly }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        # BEGIN NEW in v12
        if 'force-open' not in data: data['force-open'] = False 
        if 'read-only' not in data: data['read-only'] = False
        # END OF NEW
        self.trace('repo dest %s' % str(repoType) )
        
        pathFile = data['path']
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):
            projectAuthorized, projectsList = ProjectsManager.instance().checkProjectsAuthorizationV2(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                ret = RepoTests.instance().getFile(pathFile=pathFile, project=data['projectid'], login=login,
                                                   forceOpen=data['force-open'], readOnly=data['read-only'], 
                                                   projectsList=projectsList)
                rsp['ret'] = ret
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                ret = RepoAdapters.instance().getFile(pathFile=pathFile, login=login, forceOpen=data['force-open'],
                                                        readOnly=data['read-only'])
                rsp['ret'] = ret
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                ret = RepoLibraries.instance().getFile(pathFile=pathFile, login=login, forceOpen=data['force-open'],
                                                        readOnly=data['read-only'])
                rsp['ret'] = ret
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_getFileRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFile='', 
                                    forDest=0, actionId=0, testId=0, rights=[]):
        """
        Get file 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int, 'path': str, 'for-dest': int, 'action-id': int, 'test-id': int}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'repo-dst': repoDst, 'projectid': projectId, 'path': pathFile, 
                                    'for-dest': forDest, 'action-id': actionId, 'test-id': testId}
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )
        pathFile = data['path']
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                forDest = data['for-dest']
                actionId = data['action-id']
                testId = data['test-id']
                ret = RepoTests.instance().getFile(pathFile=pathFile, project=data['projectid'], addLock=False)
                if isinstance( ret, list):
                    ret.append(forDest)
                    ret.append(actionId)
                    ret.append(testId)
                rsp['ret'] = ret
        else:
            if repoType != RepoTests.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code, rsp)
    
    @authentication
    def xmlrpc_importFileRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFile='', 
                                    extFile='', nameFile='', contentFile='', rights=[], makeDirs=False):
        """
        Import file 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example  { 'repo-dst': int, 'projectid': int, 'path': str, 'extension': str, 'filename': str, 'content': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'repo-dst': repoDst, 'projectid': projectId, 'path': pathFile, 
                                    'extension': extFile, 'filename': nameFile, 'content': contentFile,
                                    'make-dirs': makeDirs}
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )
        
        pathFile = data['path']
        extFile = data['extension']
        nameFile = data['filename']
        makeDirs = data['make-dirs']
        contentFile = str(data['content'])

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights ):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret']  = RepoTests.instance().importFile(pathFile=pathFile, nameFile=nameFile, 
                                                            extFile=extFile,contentFile=contentFile, 
                                                            project=data['projectid'], makeDirs=makeDirs )
                                                            
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
            
    @authentication
    def xmlrpc_unlockFileRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFile='', 
                                    extFile='', nameFile='', rights=[]):
        """
        Put file 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'path': str, 'extension': str, 'filename': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoDst, 'projectid': projectId, 'path': pathFile, 
                                    'extension': extFile, 'filename': nameFile}
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )
        
        pathFile = data['path']
        extFile = data['extension']
        nameFile = data['filename']

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights ):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized: code = Context.CODE_FORBIDDEN
            else:
                rsp['ret']  = RepoTests.instance().unlockFile( pathFile=pathFile, nameFile=nameFile, 
                                                                     extFile=extFile, project=data['projectid'], login=login)
                                                                     
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights ):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().unlockFile(pathFile=pathFile, nameFile=nameFile, extFile=extFile, login=login)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights ):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().unlockFile(pathFile=pathFile, nameFile=nameFile, extFile=extFile, login=login)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            code = Context.CODE_FORBIDDEN

        return (code,rsp)
            
    @authentication
    def xmlrpc_putFileRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFile='', 
                                    extFile='', nameFile='', contentFile='', updateFile=False, rights=[]):
        """
        Put file in repositories tests or adapters or libraries
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'path': str, 'extension': str, 'filename': str, 'content': str, 'update': bool }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoDst, 'projectid': projectId, 'path': pathFile, 
                                    'extension': extFile, 'filename': nameFile, 'content': contentFile, 'update': updateFile }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )
        
        pathFile = data['path']
        extFile = data['extension']
        nameFile = data['filename'].replace("'", "") # no more authorized ' in folder name
        contentFile = str(data['content'])
        updateFile = data['update']

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights ):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret']  = RepoTests.instance().putFile(pathFile=pathFile, nameFile=nameFile, extFile=extFile,contentFile=contentFile,
                                                        updateFile=updateFile, project=data['projectid'], closeAfter=data['close'], login=login )
                                                        
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights ):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().putFile(pathFile=pathFile, nameFile=nameFile, extFile=extFile,contentFile=contentFile,
                                                                    updateFile=updateFile, closeAfter=data['close'], login=login )
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights ):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().putFile(pathFile=pathFile, nameFile=nameFile, extFile=extFile,contentFile=contentFile,
                                            updateFile=updateFile, closeAfter=data['close'], login=login )
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_addDirRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFolder='', folderName='', rights=[]):
        """
        Add folder
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'path': str, 'name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'repo-dst': repoDst, 'projectid': projectId, 'path': pathFolder, 'name': folderName }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        pathFolder = data['path']
        folderName = data['name'].replace("'", "") # no more authorized ' in folder name
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().addDir(pathFolder, folderName, project=data['projectid'])
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().addDir(pathFolder, folderName)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().addDir(pathFolder, folderName)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_delDirRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFolder='', rights=[]):
        """
        Delete folder
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int, 'path': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoDst, 'projectid': projectId, 'path': pathFolder }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        pathFolder = data['path']
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().delDir(pathFolder, project=data['projectid'])
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().delDir(pathFolder)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().delDir(pathFolder)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_delDirAllRepo(self, login, password, data={}, fromGui=False, repoDst=0, projectId=0, pathFolder='', rights=[]):
        """
        Delete folders and all sub folders
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int, 'path': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'repo-dst': repoDst, 'projectid': projectId, 'path': pathFolder }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        pathFolder = data['path']
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().delDirAll(pathFolder, project=data['projectid'])
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().delDirAll(pathFolder)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().delDirAll(pathFolder)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_renameDirRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, mainPath='', oldPath='', newPath='', rights=[]):
        """
        Rename folder
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'main-path': str, 'old-path': str, 'new-path': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'repo-dst': repoType, 'projectid': projectId, 'main-path': mainPath, 'old-path': oldPath, 'new-path': newPath }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        mainPath = data['main-path']
        oldPath = data['old-path']
        newPath = data['new-path'].replace("'", "") # no more authorized ' in folder name
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):      
            projectAuthorized, prjsList = ProjectsManager.instance().checkProjectsAuthorizationV2(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().renameDir(mainPath, oldPath,newPath, project=data['projectid'], projectsList=prjsList, renamedBy=login)
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().renameDir(mainPath, oldPath,newPath)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().renameDir(mainPath, oldPath,newPath)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_duplicateDirRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, mainPath='', oldPath='', newPath='', 
                                      newProjectId=0, newMainPath='', rights=[]):
        """
        Duplicate folder
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int, 'main-path': str, 'old-path': str, 'new-path': str, 'new-projectid': int, 'new-main-path': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoType, 'projectid': projectId, 'main-path': mainPath, 'old-path': oldPath, 
                                'new-path': newPath, 'new-projectid': newProjectId, 'new-main-path': newMainPath}
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        mainPath = data['main-path']
        oldPath = data['old-path']
        newPath = data['new-path'].replace("'", "") # no more authorized ' in folder name
        newProjectId = data['new-projectid']
        newMainPath = data['new-main-path'].replace("'", "") # no more authorized ' in folder name

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):  
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().duplicateDir(mainPath, oldPath,newPath, newMainPath=newMainPath,
                                                                project=data['projectid'], newProject=newProjectId)
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().duplicateDir(mainPath, oldPath,newPath, newMainPath=newMainPath)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().duplicateDir(mainPath, oldPath,newPath, newMainPath=newMainPath)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_delFileRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, pathFile='', rights=[]):
        """
        Delete file
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int,'path-file': str  }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoType, 'projectid': projectId,'path-file':pathFile  }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        pathFile = data['path-file']    
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):  
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().delFile(pathFile, project=data['projectid'], supportSnapshot=True)
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().delFile(pathFile)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().delFile(pathFile)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_renameFileRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, mainPath='', oldFilename='',
                                    newFilename='', extFilename='', rights=[]):
        """
        Rename file
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'main-path': str, 'old-filename': str, 'new-filename': str, 'extension': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'repo-dst': repoType, 'projectid': projectId, 'main-path': mainPath, 
                                'old-filename': oldFilename, 'new-filename': newFilename, 'extension': extFilename}
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        mainPath = data['main-path']
        oldFilename = data['old-filename']
        newFilename = data['new-filename'].replace("'", "") # no more authorized ' in folder name
        extFilename = data['extension']
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):  
            projectAuthorized, prjsList = ProjectsManager.instance().checkProjectsAuthorizationV2(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoTests.instance().renameFile(mainPath, oldFilename, newFilename, extFilename, 
                                                             project=data['projectid'], supportSnapshot=True, 
                                                             projectsList=prjsList, renamedBy=login)
                
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().renameFile(mainPath, oldFilename, newFilename, extFilename)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().renameFile(mainPath, oldFilename, newFilename, extFilename)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_duplicateFileRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, mainPath='', 
                                        oldFilename='', newFilename='', extFilename='', newProjectId=0, newMainPath='', rights=[]):
        """
        Duplicate file 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int,'projectid': int, 'main-path': str,'old-filename': str, 'new-filename': str, 'extension': str,  'new-projectid': int, 'new-main-path': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'repo-dst': repoType,'projectid': projectId, 'main-path': mainPath, 
                                    'old-filename': oldFilename, 'new-filename': newFilename,
                                   'extension': extFilename,  'new-projectid': newProjectId, 'new-main-path': newMainPath }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )
        
        mainPath = data['main-path']
        oldFilename = data['old-filename']
        newFilename = data['new-filename'].replace("'", "") # no more authorized ' in folder name
        extFilename = data['extension']
        newProjectId = data['new-projectid']
        newMainPath = data['new-main-path']

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):  
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "source project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['new-projectid'])
                self.trace( "source project is authorized ? %s" % projectAuthorized)
                if not projectAuthorized:
                    code = Context.CODE_FORBIDDEN
                else:
                    rsp['ret'] = RepoTests.instance().duplicateFile(mainPath, oldFilename, newFilename, extFilename,
                                                                  project=data['projectid'], newProject=newProjectId, newMainPath=newMainPath)
                                                                  
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().duplicateFile(mainPath, oldFilename, newFilename, extFilename, newMainPath=newMainPath)
            else:
                code = Context.CODE_FORBIDDEN
                
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().duplicateFile(mainPath, oldFilename, newFilename, extFilename, newMainPath=newMainPath)
            else:
                code = Context.CODE_FORBIDDEN
                
        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_resetTestsStats(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Reset tests statistics on database
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = StatsManager.instance().resetStats()
        if not rsp: responseCode = Context.CODE_FAILED
        return (code,rsp)
    
    @authentication
    def xmlrpc_emptyRepo(self, login, password, data={}, fromGui=False, projectId=0, repoType=0, rights=[]):
        """
        Removes all archives on the archives repository
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'repo-dst': repoType, 'projectid': projectId}
        
        # extract the destination repository
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )

        # tests repository
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights ):
            rsp['ret'] = RepoTests.instance().emptyRepo(projectId='')
            if not rsp['ret']:
                code = Context.CODE_FAILED
        
        # adapters repository
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights ) :
            rsp['ret'] = RepoAdapters.instance().uninstall()
            if rsp['ret'] != Context.CODE_OK:
                code = Context.CODE_FAILED

        # libraries adapters repository
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights ) :
            rsp['ret'] = RepoLibraries.instance().uninstall()
            if rsp['ret'] != Context.CODE_OK:
                code = Context.CODE_FAILED

        # archives repository
        elif repoType == RepoArchives.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights ) :
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                rsp['ret'] = RepoArchives.instance().resetArchives(projectId=data['projectid'])
                if rsp['ret'] != Context.CODE_OK:
                    code = Context.CODE_FAILED
        else:
            raise Exception('repo type unknown %s' % repoType)

        return (code,rsp)
    
    @authentication
    def xmlrpc_zipRepoArchives(self, login, password, data={}, fromGui=False, projectId=0, mainPath='', subPath='', rights=[]):
        """
        Create a zip file on the archive repository
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'project-id': int, 'main-path-to-zip': str, 'sub-path-to-zip': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'project-id': projectId, 'main-path-to-zip': mainPath, 'sub-path-to-zip': subPath}
        
        mainPathToZip = data['main-path-to-zip']
        subPathToZip = data['sub-path-to-zip']
        projectId = data['project-id']
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['project-id'])
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            rsp = RepoArchives.instance().createZip(mainPathToZip, subPathToZip, projectId=projectId)
            if rsp != Context.CODE_OK:
                code = Context.CODE_FAILED

        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshStatsRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, rights=[]):
        """
        Get statistics from repository
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'repo-dst': int, 'projectid': int, 'partial': bool }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'repo-dst': repoType, 'projectid': projectId, 'partial': True}
        
        # extract the destination repository
        repoType = data['repo-dst']
        projectId = data['projectid']
        rsp['repo-dst'] = repoType
        # for retro compatibility, new in v11.3
        if 'partial' not in data: data['partial'] = True
        
        if int(projectId) == 0: projectId = ""
        self.trace('Refresh Statistics Repo=%s ProjectId=%s Partial=%s' % (repoType, projectId, data['partial']) )

        # tests repository
        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-system') in rights ):
            nb_tests, nb_tests_f, tests, stats_tests = RepoTests.instance().getTree(b64=True,  project=projectId )
            del tests; del nb_tests_f; del nb_tests;
            rsp['stats-repo-tests'] = stats_tests              
            rsp['backups-repo-tests'] = RepoTests.instance().getBackups(b64=True)
            if len(rsp['stats-repo-tests']) == 0:
                code = Context.CODE_FAILED
        
        # adapters repository
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-system') in rights) :
            nb_adps, nb_adps_f, adps, stats_adps = RepoAdapters.instance().getTree(b64=True)
            del adps; del nb_adps_f; del nb_adps;
            rsp['stats-repo-adapters'] = stats_adps
            rsp['backups-repo-adapters'] = RepoAdapters.instance().getBackups(b64=True)
            if len(rsp['stats-repo-adapters']) == 0:
                code = Context.CODE_FAILED

        # libraries adapters repository
        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-system') in rights ) :
            nb_libs, nb_libs_f, libs, stats_libs = RepoLibraries.instance().getTree(b64=True)
            del libs; del nb_libs_f; del nb_libs;
            rsp['stats-repo-libraries'] = stats_libs
            rsp['backups-repo-libraries'] = RepoLibraries.instance().getBackups(b64=True)
            if len(rsp['stats-repo-libraries']) == 0:
                code = Context.CODE_FAILED

        # archives repository
        elif repoType == RepoArchives.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or \
                Settings.get('Server', 'level-tester') in rights or Settings.get('Server', 'level-system') in rights):
            nb_archs, nb_archs_f, archs, stats_archs = RepoArchives.instance().getTree(b64=True, fullTree=not data['partial'], project=projectId)
            del archs; del nb_archs_f; del nb_archs;
            rsp['stats-repo-archives'] = stats_archs
            if  Settings.get('Server', 'level-admin') in rights:
                rsp['backups-repo-archives'] = RepoArchives.instance().getBackups(b64=True)

        else:
            raise Exception('repo type unknown %s' % repoType)
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshContextServer(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Get context of the server
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = Context.instance().getInformations(user=login, b64=True)
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshStatsServer(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Get statistics of the server
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = Context.instance().getStats(b64=True)
        if len(rsp) == 0: code = Context.CODE_FAILED
        return (code,rsp)
    
    @authentication
    def xmlrpc_stopAgent (self, login, password, data={}, fromGui=False, agentName='', rights=[]):
        """
        Stop the agent gived as argument
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'name': agentName }
        rsp = AgentsManager.instance().stopAgent( aname = data['name'] )
        if not rsp: code = Context.CODE_NOT_FOUND
        return (code,rsp)
    
    @authentication
    def xmlrpc_startAgent(self, login, password, data={}, fromGui=False, agentType='', agentName='', agentDescr='', makeDefault=False, rights=[]):
        """
        Start a agent 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example  { 'make-default': bool, 'type': str, 'name': str, 'description': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'make-default': makeDefault, 'type': agentType, 'name': agentName, 'description': agentDescr}
        
        if not Settings.getInt( 'WebServices', 'local-agents-enabled' ):
            code = Context.CODE_DISABLED
        else:
            # add default probe 
            agentDefault = True
            if data['make-default']:
                agentAdded = AgentsManager.instance().addDefaultAgent( aType = data['type'], aName = data['name'], 
                                                    aDescr = data['description'])
                if agentAdded  == Context.CODE_ERROR:
                    return ( 'addAgent', Context.CODE_ERROR, agentAdded )

            # start the probe
            rsp = AgentsManager.instance().startAgent( atype = data['type'], aname = data['name'], adescr = data['description'],
                                                    adefault=agentDefault )
            if rsp == -1:
                code = Context.CODE_FAILED
            else:
                code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshRunningAgents(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Get all running agents
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = AgentsManager.instance().getRunning(b64=True)
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshDefaultAgents(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Get all default agents
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not Settings.getInt( 'WebServices', 'local-agents-enabled' ):
            code = Context.CODE_DISABLED
        else:
            rsp = AgentsManager.instance().getDefaultAgents(b64=True)

        return (code,rsp)
    
    @authentication
    def xmlrpc_addAgent (self, login, password, data={}, fromGui=False, agentType='', agentName='', agentDescr='', rights=[]):
        """
        Add an agent 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'type': str, 'name': str, 'description': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'type': agentType, 'name': agentName, 'description': agentDescr}
        
        if not Settings.getInt( 'WebServices', 'local-agents-enabled' ):
            code = Context.CODE_DISABLED
        else:
            rsp = AgentsManager.instance().addDefaultAgent( aType = data['type'], aName = data['name'],aDescr = data['description'])
            if rsp  == Context.CODE_ERROR:
                code = ret
            else:
                code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_delAgent (self, login, password, data={}, fromGui=False, agentName='', rights=[]):
        """
        Delete an agent 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'name': agentName }
        
        if not Settings.getInt( 'WebServices', 'local-agents-enabled' ):
            code = Context.CODE_DISABLED
        else:
            rsp = AgentsManager.instance().delDefaultAgent( aName = data['name'] )
            if rsp  == Context.CODE_ERROR:
                code = rsp
            else:
                code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_stopProbe (self, login, password, data={}, fromGui=False, probeName='', rights=[]):
        """
        Stop the probe gived as argument
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        if not len(data): data = { 'name': probeName }
        rsp = ProbesManager.instance().stopProbe( pname = data['name'] )
        if not rsp:
            code = Context.CODE_NOT_FOUND
        return (code,rsp)
    
    @authentication
    def xmlrpc_startProbe (self, login, password, data={}, fromGui=False, probeType='', probeName='', probeDescr='', rights=[]):
        """
        Start a probe 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'type': str, 'name': str, 'description': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'type': probeType, 'name': probeName, 'description': probeDescr}
        
        if not Settings.getInt( 'WebServices', 'local-probes-enabled' ):
            code = Context.CODE_DISABLED
        else:
            # add default probe 
            prDefault = True
            if data['make-default']:
                prAdded = ProbesManager.instance().addDefaultProbe( pType = data['type'], pName = data['name'], 
                                                                    pDescr = data['description'])
                if prAdded  == Context.CODE_ERROR:
                    return ( 'addProbe', Context.CODE_ERROR, prAdded )

            # start the probe
            rsp = ProbesManager.instance().startProbe( ptype = data['type'], pname = data['name'], pdescr = data['description'],
                                                       pdefault=prDefault )
            if rsp == -1:
                code = Context.CODE_FAILED
            else:
                code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshRunningProbes(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Get all running probes
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = ProbesManager.instance().getRunning(b64=True)
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshDefaultProbes(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Get all default probes
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not Settings.getInt( 'WebServices', 'local-probes-enabled' ):
            code = Context.CODE_DISABLED
        else:
            rsp = ProbesManager.instance().getDefaultProbes(b64=True)

        return (code,rsp)
    
    @authentication
    def xmlrpc_addProject (self, login, password, data={}, fromGui=False, projectId=0, rights=[]):
        """
        Add a project
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'project-id': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'project-id': projectId }
        rsp = ProjectsManager.instance().addProject( prjId = data['project-id'])
        code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_delProject (self, login, password, data={}, fromGui=False, projectId=0, rights=[]):
        """
        Delete a project
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'project-id': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'project-id': projectId }
        rsp = ProjectsManager.instance().delProject( prjId = data['project-id'])
        code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_addProbe (self, login, password, data={}, fromGui=False, probeType='', probeName='', probeDescr='', rights=[]):
        """
        Add a probe 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'type': str, 'name': str, 'description': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'type': probeType, 'name': probeName, 'description': probeDescr}
        
        if not Settings.getInt( 'WebServices', 'local-probes-enabled' ):
            code = Context.CODE_DISABLED
        else:
            rsp = ProbesManager.instance().addDefaultProbe( pType = data['type'], pName = data['name'], pDescr = data['description'])
            if rsp  == Context.CODE_ERROR:
                code = rsp
            else:
                code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_delProbe (self, login, password, data={}, fromGui=False, probeName='', rights=[]):
        """
        Delete a probe 
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'name': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = {'name': probeName}
        
        if not Settings.getInt( 'WebServices', 'local-probes-enabled' ):
            code = Context.CODE_DISABLED
        else:
            rsp = ProbesManager.instance().delDefaultProbe( pName = data['name'] )
            if rsp  == Context.CODE_ERROR:
                code = rsp
            else:
                code = Context.CODE_OK

        return (code,rsp)
    
    @authentication
    def xmlrpc_genCacheHelp(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Generate the cache for the documentation
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        subRet, details = HelperManager.instance().generateHelps()
        if not subRet:
            code = Context.CODE_FAILED
        rsp['result'] = subRet
        rsp['details'] = details

        return (code,rsp)
    
    @authentication
    def xmlrpc_delTasksHistory(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Delete all tasks from history (from database)
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        TaskManager.instance().clearHistory()
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshTasks(self, login, password, data={}, fromGui=False, taskType=0, fullRefresh=False, rights=[]):
        """
        Refresh tasks running, waiting or history
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'task-type': int, 'full': bool}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'task-type': taskType, 'full': fullRefresh}
        
        taskType = data['task-type']
        rsp['task-type'] = taskType
        self.trace('task type %s' % str(taskType) )
        if taskType == TaskManager.TASKS_RUNNING:
            rsp['tasks-running'] = TaskManager.instance().getRunning(b64=True, user=login)
        elif taskType == TaskManager.TASKS_WAITING:
            rsp['tasks-waiting'] = TaskManager.instance().getWaiting(b64=True, user=login)
        elif taskType == TaskManager.TASKS_HISTORY:
            rsp['tasks-history'] = TaskManager.instance().getHistory(Full=data['full'], b64=True, user=login)
        else:
            raise Exception('task type unknown %s' % taskType)
        rsp['ret'] = True

        return (code,rsp)
    
    @authentication
    def xmlrpc_addCommentArchive(self, login, password, data={}, fromGui=False, archivePath='', archivePost='', archiveTimestamp='', 
                                        testId=0, rights=[]):
        """
        Add comment in the archive gived as argument
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'file': str, 'post': str, 'timestamp': str, 'testid': int}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = {'file': archivePath, 'post': archivePost, 'timestamp': archiveTimestamp, 'testid': testId}
        
        archivePath = data['file']
        archivePost = data['post']
        archiveTimestamp = data['timestamp']
        testId = data['testid']
        rsp['display-posts'] = True
        if testId > 0:
            task = TaskManager.instance().getTask( taskId = testId )
            if task is None:
                raise Exception( 'task %s not found' % testId )
            archivePath = task.getFileResultPath()
            rsp['display-posts'] = False
        rsp['ret'] = RepoArchives.instance().addComment( archiveUser=login, archivePath=archivePath, archivePost=archivePost, 
                                                                archiveTimestamp=archiveTimestamp )

        return (code,rsp)
    
    @authentication
    def xmlrpc_loadCommentsArchive(self, login, password, data={}, fromGui=False, archivePath='', rights=[]):
        """
        Load comment from the archive gived as argument
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'file': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'file': archivePath }
        archivePath = data['file']
        rsp['ret'] =  RepoArchives.instance().getComments(archivePath=archivePath)

        return (code,rsp)
    
    @authentication
    def xmlrpc_delCommentsArchive(self, login, password, data={}, fromGui=False, archivePath='', rights=[]):
        """
        Delete all comments in the archive gived as argument
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'file': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'file': archivePath }
        archivePath = data['file']
        rsp['ret'] =  RepoArchives.instance().delComments(archivePath=archivePath)

        return (code,rsp)
    
    @authentication
    def xmlrpc_backupRepo(self, login, password, data={}, fromGui=False, repoType=0, rights=[]):
        """
        Backup repository tests/adapters
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'repo-dst': repoType }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )
        backupName = data['backup-name']

        if repoType == RepoTests.REPO_TYPE:
            rsp['ret'] =  RepoTests.instance().createBackup(backupName=backupName)

        elif repoType == RepoAdapters.REPO_TYPE:
            rsp['ret'] =  RepoAdapters.instance().createBackup(backupName=backupName)

        elif repoType == RepoLibraries.REPO_TYPE:
            rsp['ret'] =  RepoLibraries.instance().createBackup(backupName=backupName)

        elif repoType == RepoArchives.REPO_TYPE:
            rsp['ret'] =  RepoArchives.instance().createBackup(backupName=backupName)
        else:
            raise Exception('repo type unknown %s' % repoType)

        return (code,rsp)
    
    @authentication
    def xmlrpc_deleteBackupsRepo(self, login, password, data={}, fromGui=False, repoType=0, rights=[]):
        """
        Delete all backups from repository tests/adapters
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'repo-dst': repoType }
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        self.trace('repo dest %s' % str(repoType) )

        if repoType == RepoTests.REPO_TYPE:
            rsp['ret'] = RepoTests.instance().deleteBackups()

        elif repoType == RepoAdapters.REPO_TYPE:
            rsp['ret'] = RepoAdapters.instance().deleteBackups()

        elif repoType == RepoLibraries.REPO_TYPE:
            rsp['ret'] = RepoLibraries.instance().deleteBackups()

        elif repoType == RepoArchives.REPO_TYPE:
            rsp['ret'] = RepoArchives.instance().deleteBackups()
        else:
            raise Exception('repo type unknown %s' % repoType)

        return (code,rsp)
    
    @authentication
    def xmlrpc_addLibraryRepo(self, login, password, data={}, fromGui=False, pathFolder='', libraryName='', mainLibraries='', rights=[]):
        """
        Add library
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'path': str, 'name': str, 'main-libraries': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};
        
        if not len(data): data = {'path': pathFolder, 'name': libraryName, 'main-libraries': mainLibraries}
        
        pathFolder = data['path']
        libraryName = data['name']
        mainLibraries = data['main-libraries']
        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights:
            rsp['ret'] = RepoLibraries.instance().addLibrary(pathFolder, libraryName, mainLibraries)
        else:
            code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_addAdapterRepo(self, login, password, data={}, fromGui=False, pathFolder='', adapterName='', mainAdapters='', rights=[]):
        """
        Add adapter
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'path': str, 'name': str, 'main-adapters': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'path': pathFolder, 'name': adapterName, 'main-adapters': mainAdapters}
        
        pathFolder = data['path']
        adapterName = data['name']
        mainAdapters = data['main-adapters']
        if Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights:
            rsp['ret'] = RepoAdapters.instance().addAdapter(pathFolder, adapterName, mainAdapters)
        else:
            code = Context.CODE_FORBIDDEN

        return (code,rsp)
            
    @authentication
    def xmlrpc_setGenericAdapter(self, login, password, data={}, fromGui=False, packageName='', rights=[]):
        """
        Set generic adapter
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'package-name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'package-name': packageName }
        packageName = data['package-name']
        rsp['ret'] = RepoAdapters.instance().setGeneric(packageName)

        return (code,rsp)
    
    @authentication
    def xmlrpc_setGenericLibrary(self, login, password, data={}, fromGui=False, packageName='', rights=[]):
        """
        Set generic library
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'package-name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'package-name': packageName }
        packageName = data['package-name']
        rsp['ret'] = RepoLibraries.instance().setGeneric(packageName)

        return (code,rsp)
            
    @authentication
    def xmlrpc_setDefaultAdapterV2(self, login, password, data={}, fromGui=False, packageName='', rights=[]):
        """
        Set default adapter
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'package-name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'package-name': packageName }
        packageName = data['package-name']
        rsp['ret'] = RepoAdapters.instance().setDefaultV2(packageName)

        return (code,rsp)
    
    @authentication
    def xmlrpc_setDefaultLibraryV2(self, login, password, data={}, fromGui=False, packageName='', rights=[]):
        """
        Set default library
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'package-name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'package-name': packageName }
        packageName = data['package-name']
        rsp['ret'] = RepoLibraries.instance().setDefaultV2(packageName)

        return (code,rsp)
    
    @authentication
    def xmlrpc_moveDirRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, mainPath='', folderName='',
                                    newPath='', newProjectId=0, rights=[]):
        """
        Move dir
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'main-path': str, 'folder-name': str, 'new-path': str, 'new-projectid': int}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'repo-dst': repoType, 'projectid': projectId, 'main-path': mainPath, 
                                    'folder-name': folderName, 'new-path': newPath, 'new-projectid': newProjectId}
        
        repoType = data['repo-dst']
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )

        mainPath = data['main-path']
        folderName = data['folder-name']
        newPath = data['new-path']
        newProjectId = data['new-projectid']

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):  
            projectAuthorized, prjsList = ProjectsManager.instance().checkProjectsAuthorizationV2(user=login, projectId=data['projectid'])
            self.trace( "source project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['new-projectid'])
                self.trace( "destination project is authorized ? %s" % projectAuthorized)
                if not projectAuthorized:
                    code = Context.CODE_FORBIDDEN
                else:
                    rsp['ret'] = RepoTests.instance().moveDir(mainPath, folderName, newPath, project=data['projectid'], 
                                                                newProject=newProjectId, projectsList=prjsList, renamedBy=login )

        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                rsp['ret'] = RepoAdapters.instance().moveDir(mainPath, folderName, newPath )
            else:
                code = Context.CODE_FORBIDDEN

        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                rsp['ret'] = RepoLibraries.instance().moveDir(mainPath, folderName, newPath )
            else:
                code = Context.CODE_FORBIDDEN


        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_moveFileRepo(self, login, password, data={}, fromGui=False, repoType=0, projectId=0, mainPath='', 
                                    fileName='', newPath='', extFilename='', newProjectId=0, rights=[]):
        """
        Move file
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'repo-dst': int, 'projectid': int, 'main-path': str, 'filename': str, 'new-path': str, 'extension': str, 'new-projectid': int}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        if not len(data): data = { 'repo-dst': repoType, 'projectid': projectId, 'main-path': mainPath,
                                    'filename': fileName, 'new-path': newPath, 'extension': extFilename, 
                                    'new-projectid': newProjectId}
        
        repoType = data['repo-dst']
        
        rsp['repo-dst'] = repoType
        rsp['projectid'] = data['projectid']
        self.trace('repo dest %s' % str(repoType) )

        mainPath = data['main-path']
        fileName = data['filename']
        newPath = data['new-path']
        extFilename = data['extension']
        newProjectId = data['new-projectid']

        if repoType == RepoTests.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-tester') in rights):  
            projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
            self.trace( "source project is authorized ? %s" % projectAuthorized)
            if not projectAuthorized:
                code = Context.CODE_FORBIDDEN
            else:
                projectAuthorized, prjsList = ProjectsManager.instance().checkProjectsAuthorizationV2(user=login, projectId=data['new-projectid'])
                self.trace( "destination project is authorized ? %s" % projectAuthorized)
                if not projectAuthorized:
                    code = Context.CODE_FORBIDDEN
                else:
                    ret = RepoTests.instance().moveFile(mainPath, fileName, extFilename, newPath, project=data['projectid'], 
                                                        newProject=newProjectId, supportSnapshot=True,
                                                        projectsList=prjsList, renamedBy=login)
                    if ret == Context.CODE_ERROR: raise Exception('unable to move the file repo test')
                    else:
                        rsp['ret'] = ret
        elif repoType == RepoAdapters.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-adapters' ):
                ret = RepoAdapters.instance().moveFile(mainPath, fileName, extFilename, newPath )
                if ret == Context.CODE_ERROR: raise Exception('unable to move the file repo adapter')
                else:
                    rsp['ret'] = ret
            else:
                code = Context.CODE_FORBIDDEN

        elif repoType == RepoLibraries.REPO_TYPE and ( Settings.get('Server', 'level-admin') in rights or Settings.get('Server', 'level-developer') in rights):
            if Settings.getInt( 'WebServices', 'remote-dev-libraries' ):
                ret = RepoLibraries.instance().moveFile(mainPath, fileName, extFilename, newPath )
                if ret == Context.CODE_ERROR: raise Exception('unable to move the file repo lib')
                else:
                    rsp['ret'] = ret
            else:
                code = Context.CODE_FORBIDDEN


        else:
            if repoType != RepoTests.REPO_TYPE and repoType != RepoAdapters.REPO_TYPE:
                raise Exception('repo type unknown %s' % repoType)
            else:
                code = Context.CODE_FORBIDDEN

        return (code,rsp)
    
    @authentication
    def xmlrpc_exportTestVerdict(self, login, password, data={}, fromGui=False, projectId=0, testId=0, archivePath='', 
                                        archiveName='', rights=[]):
        """
        Export test result to csv
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'project-id': int, 'testid': int, 'testpath': str, 'testfilename': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        # try:
        if not len(data): data = { 'project-id': projectId, 'testid': testId, 'testpath': archivePath, 'testfilename': archiveName}
        
        prjId = data['project-id']
        # test not name, project = 0
        if prjId == 0: prjId = ProjectsManager.instance().getDefaultProjectForUser(user=login)
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=prjId)
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            testId = data['testid']
            rsp['verdict'] = ''
            if testId > 0:
                task = TaskManager.instance().getTask( taskId = testId )
                if task is None:
                    code = Context.CODE_NOT_FOUND
                    self.info( 'task %s not found' % testId )
                else:
                    rsp['verdict'] = task.getTestVerdict()
                    rsp['verdict-xml'] = task.getTestVerdict(returnXml=True)
            if 'testpath' in data:
                code, verdict = RepoArchives.instance().getTestVerdict(archivePath=data['testpath'], 
                                                    archiveName=data['testfilename'], projectId=prjId)
                rsp['verdict'] = verdict
                code, verdictXml = RepoArchives.instance().getTestVerdict(archivePath=data['testpath'],
                                                    archiveName=data['testfilename'], returnXml=True, projectId=prjId)
                rsp['verdict-xml'] = verdictXml

        return (code,rsp)
    
    @authentication
    def xmlrpc_exportTestReport(self, login, password, data={}, fromGui=False, projectId=0, testId=0, archivePath='', 
                                        archiveName='', rights=[]):
        """
        Export test result report
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'project-id': int, 'testid': int, 'testpath': str, 'testfilename': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"ret": False};

        # try:
        if not len(data): data = { 'project-id': projectId, 'testid': testId, 'testpath': archivePath, 'testfilename': archiveName}
        
        prjId = data['project-id']
        # test not name, project = 0
        if prjId == 0: prjId = ProjectsManager.instance().getDefaultProjectForUser(user=login)
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=prjId)
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            testId = data['testid']
            rsp['report'] = ''
            if testId > 0:
                task = TaskManager.instance().getTask( taskId = testId )
                if task is None:
                    code = Context.CODE_NOT_FOUND
                    self.info( 'task %s not found' % testId )
                else:
                    rsp['report'] = task.getTestReport()
                    rsp['report-xml'] =  task.getTestReport(returnXml=True)
            if 'testpath' in data:
                code, reports = RepoArchives.instance().getTestReport(archivePath=data['testpath'],
                                                            archiveName=data['testfilename'], projectId=prjId)
                rsp['report'] = reports
                code, reportsXml = RepoArchives.instance().getTestReport(archivePath=data['testpath'],
                                                            archiveName=data['testfilename'], returnXml=True, projectId=prjId)
                rsp['report-xml'] = reportsXml

        return (code,rsp)
        
    @authentication
    def xmlrpc_prepareAssistant(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Prepare assistant
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"result": False};

        if Context.instance().generateAdapters():
            if Context.instance().generateLibraries():
                if Context.instance().generateSamples():
                    subRet, details = HelperManager.instance().generateHelps()
                    rsp['result'] = subRet
                    rsp['details'] = details

        return (code,rsp)
        
    @authentication
    def xmlrpc_generateAdapterFromWSDL(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Generate adapter from WSDL file
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"result": False};

        rsp['result'] = RepoAdapters.instance().generateFromWSDL(
                                                    wsdlUrl=data['wsdl-url'],
                                                    wsdlFile=data['wsdl-file'].data,
                                                    pkg=data['pkg'],
                                                    overwrite=data['overwrite']
                                                )

        return (code,rsp)
            
    @authentication
    def xmlrpc_setDefaultVersionForTests(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Set the default version of adapter and libraries for all tests
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={"result": False};
        rsp['result'] = RepoTests.instance().setTestsWithDefault()
        return (code,rsp)
    
    @authentication
    def xmlrpc_genAllPackages(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Generate all packages
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        rsp = Context.instance().generateAdapters()
        if not rsp:
            code = Context.CODE_ERROR
        else:
            rsp = Context.instance().generateLibraries()
            if not rsp:
                code = Context.CODE_ERROR
            else:
                rsp = Context.instance().generateSamples()
                if not rsp:
                    code = Context.CODE_ERROR

        return (code,rsp)
    
    @authentication
    def xmlrpc_genAdapters(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Generate adapters
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = Context.instance().generateAdapters()
        if not rsp: code = Context.CODE_ERROR
        return (code,rsp)
    
    @authentication
    def xmlrpc_genLibraries(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Generate libraries
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = Context.instance().generateLibraries()
        if not rsp: code = Context.CODE_ERROR
        return (code,rsp)
    
    @authentication
    def xmlrpc_genSamples(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Generate samples
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM

        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = Context.instance().generateSamples()
        if not rsp: code = Context.CODE_ERROR
        return (code,rsp)
    
    @authentication
    def xmlrpc_refreshTestEnvironment(self, login, password, data={}, fromGui=False, rights=[]):
        """
        Refresh test environment
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};
        rsp = Context.instance().refreshTestEnvironment()
        return (code,rsp)
    
    @authentication
    def xmlrpc_exportTestDesign(self, login, password, data={}, fromGui=False, testId=0, projectId=0, archivePath='', 
                                        archiveName='', rights=[]):
        """
        Export test result design
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'project-id': int, 'testid': int, 'testpath': str, 'testfilename': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False };

        if not len(data): data = { 'project-id': projectId, 'testid': testId, 'testpath': archivePath, 'testfilename': archiveName }
        
        prjId = data['project-id']
        # test not name, project = 0 so change it to the default
        if prjId == 0: prjId = ProjectsManager.instance().getDefaultProjectForUser(user=login)
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=prjId)
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            testId = data['testid']
            rsp['design'] = ''
            if testId > 0:
                task = TaskManager.instance().getTask( taskId = testId )
                if task is None:
                    code = Context.CODE_NOT_FOUND
                    self.info( 'task %s not found' % testId )
                else:
                    rsp['design'] = task.getTestDesign()
                    rsp['design-xml'] = task.getTestDesign(returnXml=True)
            if 'testpath' in data:
                code, reports = RepoArchives.instance().getTestDesign(archivePath=data['testpath'], 
                                                                        archiveName=data['testfilename'], projectId=prjId)
                rsp['design'] = reports
                code, reportsXml = RepoArchives.instance().getTestDesign(archivePath=data['testpath'], 
                                                                        archiveName=data['testfilename'],
                                                                        returnXml=True, projectId=prjId)
                rsp['design-xml'] = reportsXml

        return (code,rsp)
    
    @authentication
    def xmlrpc_disconnectAgent(self, login, password, data={}, fromGui=False, agentName='', rights=[]):
        """
        Disconnect Agent
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'name': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ };
        if not len(data): data = { 'name': agentName}
        rsp = AgentsManager.instance().disconnectAgent( name=data['name'] )
        return (code,rsp)
    
    @authentication
    def xmlrpc_cleanupLockFilesRepo(self, login, password, data={}, fromGui=False, tests=False, adapters=False, libraries=False, rights=[]):
        """
        Cleanup lock files
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'cleanup-tests': bool, 'cleanup-adapters': bool, 'cleanup-libraries': bool }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ };

        if not len(data): data = {'cleanup-tests': tests, 'cleanup-adapters': adapters, 'cleanup-libraries': libraries }
        
        if data['cleanup-tests'] and data['cleanup-adapters'] and data['cleanup-libraries']:
            rsp = RepoTests.instance().cleanupLocks( )
            rsp &= RepoAdapters.instance().cleanupLocks( )
            rsp &= RepoLibraries.instance().cleanupLocks( )
        elif data['cleanup-tests']:
            rsp = RepoTests.instance().cleanupLocks( )
        elif data['cleanup-adapters']:
            rsp = RepoAdapters.instance().cleanupLocks( )
        elif data['cleanup-libraries']:
            rsp = RepoLibraries.instance().cleanupLocks( )
        else:
            raise Exception("bad parameters")

        return (code,rsp)
        
    @authentication
    def xmlrpc_createSnapshotTest(self, login, password, data={}, fromGui=False, projectId=0, snapshotTimestamp='', snapshotName='', 
                                        testPath='', rights=[]):
        """
        Create snapshot
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'test-prjid': int, 'snapshot-name': str, 'snapshot-timestamp': str, 'test-path': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'test-prjid': projectId, 'snapshot-name': snapshotName, 
                                    'snapshot-timestamp': snapshotTimestamp, 'test-path': testPath}
        
        rsp['projectid'] = data['test-prjid']
        rsp['ret'] =  RepoTests.instance().addSnapshot(snapshotName=data['snapshot-name'], 
                                                snapshotTimestamp=data['snapshot-timestamp'],
                                                testPath=data['test-path'], testPrjId=data['test-prjid'] )

        return (code,rsp)
            
    @authentication
    def xmlrpc_deleteSnapshotTest(self, login, password, data={}, fromGui=False, projectId=0, snapshotPath='', snapshotName='', rights=[]):
        """
        Delete snapshot
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'test-prjid': int, 'snapshot-path': str, 'snapshot-name': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'test-prjid': projectId, 'snapshot-path': snapshotPath, 'snapshot-name': snapshotName}
        
        rsp['projectid'] = data['test-prjid']
        rsp['ret'] =  RepoTests.instance().deleteSnapshot( 
                                                                snapshotPath=data['snapshot-path'],
                                                                snapshotName=data['snapshot-name'],
                                                                snapshotPrjId=data['test-prjid']
                                                            )

        return (code,rsp)
            
    @authentication
    def xmlrpc_restoreSnapshotTest(self, login, password, data={}, fromGui=False, projectId=0, snapshotPath='', snapshotName='', rights=[]):
        """
        Restore snapshot
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'test-prjid': int, 'snapshot-path': str, 'snapshot-name': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'test-prjid': projectId, 'snapshot-path': snapshotPath, 'snapshot-name': snapshotName}
        
        rsp['projectid'] = data['test-prjid']
        rsp['ret'] =  RepoTests.instance().restoreSnapshot( 
                                                                snapshotPath=data['snapshot-path'],
                                                                snapshotName=data['snapshot-name'],
                                                                snapshotPrjId=data['test-prjid']
                                                            )

        return (code,rsp)
            
    @authentication
    def xmlrpc_deleteAllSnapshotsTest(self, login, password, data={}, fromGui=False, projectId=0, testPath='', testName='', testExt='', rights=[]):
        """
        Delete all snapshots
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example  {'test-prjid': int, 'test-path': str, 'test-name': str, 'test-ext': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = {'test-prjid': projectId, 'test-path': testPath, 'test-name': testName, 'test-ext': testExt}
        
        rsp['projectid'] = data['test-prjid']
        rsp['ret'] =  RepoTests.instance().deleteAllSnapshots( testPath=data['test-path'], 
                                                                    testPrjId=data['test-prjid'],
                                                                    testName=data['test-name'],
                                                                    testExt=data['test-ext']
                                                                    )

        return (code,rsp)
            
    @authentication
    def xmlrpc_disconnectProbe(self, login, password, data={}, fromGui=False, probeName='', rights=[]):
        """
        Disconnect Probe
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'name': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };
        if not len(data): data = {'name': probeName}
        rsp = ProbesManager.instance().disconnectProbe( name=data['name'] )
        return (code,rsp)
            
    @authentication
    def xmlrpc_downloadTestResult(self, login, password, data={}, fromGui=False, projectId=0, trPath='', trName='', toFile='', andSave=False, rights=[]):
        """
        Download test result
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'projectid': int, 'tr-path': str, 'tr-name': str, 'to-file': str, 'and-save': bool }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'projectid': projectId, 'tr-path': trPath, 'tr-name': trName,
                                    'to-file': toFile, 'and-save': andSave }
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            projectId = data['projectid']
            trPath = data['tr-path']
            trName = data['tr-name']
            
            pathFile = "%s/%s" % (trPath, trName)
            ret = RepoArchives.instance().getFile(pathFile=pathFile, project=projectId, addLock=False)
            rsp['ret'] = ret
            # variable for save mode 
            rsp['and-save'] =  data['and-save']
            rsp['to-file'] =  data['to-file']

        return (code,rsp)
            
    @authentication
    def xmlrpc_downloadBackup(self, login, password, data={}, fromGui=False, repoType=0, backupFilename='', toFile='', rights=[]):
        """
        Download backup
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'from-repo': int, 'backup-filename': str, 'to-file': str }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'from-repo': repoType, 'backup-filename': backupFilename, 'to-file': toFile }
        
        repoType = data['from-repo']
        pathFile = data['backup-filename']
        projectId = ''
        if repoType == RepoArchives.REPO_TYPE:
            ret = RepoArchives.instance().getBackup(pathFile=pathFile, project=projectId)
            rsp['ret'] = ret
            rsp['to-file'] =  data['to-file']
        elif repoType == RepoTests.REPO_TYPE:
            ret = RepoTests.instance().getBackup(pathFile=pathFile, project=projectId)
            rsp['ret'] = ret
            rsp['to-file'] =  data['to-file']
        elif repoType == RepoAdapters.REPO_TYPE:
            ret = RepoAdapters.instance().getBackup(pathFile=pathFile, project=projectId)
            rsp['ret'] = ret
            rsp['to-file'] =  data['to-file']
        elif repoType == RepoLibraries.REPO_TYPE:
            ret = RepoLibraries.instance().getBackup(pathFile=pathFile, project=projectId)
            rsp['ret'] = ret
            rsp['to-file'] =  data['to-file']
        else:
            raise Exception('repo type unknown %s' % repoType)

        return (code,rsp)
            
    @authentication
    def xmlrpc_downloadClient(self, login, password, data={}, fromGui=False, os='', packageName='', rights=[]):
        """
        Download client
        Granted levels: ADMIN, TESTER, DEVELOPER, LEADER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example { 'os': str, 'package-name': str}
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={ 'ret': False  };

        if not len(data): data = { 'os': os, 'package-name': packageName}
        
        # read arg
        systemOs = data['os']
        packageName = data['package-name']
        
        # new in v17, force to download the 64_bit architecture
        if systemOs == "win32":
            systemOs = "win64"
        # end of new
        
        # construct the full path of the client to download
        clientPackagePath = '%s%s/%s/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                                systemOs, packageName )
        self.trace( "client path: %s" % clientPackagePath )
        
        # read the file
        f = open( clientPackagePath, 'rb')
        data_read = f.read()
        f.close()
        rsp['ret']  = [ Context.CODE_OK, base64.b64encode(data_read) ]
        rsp['package-name'] = packageName

        return (code,rsp)
    
    @unauthenticated
    def xmlrpc_uploadLogs(self, login, password, data={}, fromGui=False, logPath='', logName='', logData='', rights=[]):
        """
        Upload logs, only zip, png, jpg and mp4 files are authorized!

        @param login: login name expected (anonymous)
        @type login: string

        @param password: pasword expected (anonymous)
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param data: example {'filename': str, 'result-path': str, 'file-data': binary }
        @type data: dict

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={'ret': False};

        if login != "anonymous" and password != "anonymous":
            self.error("authentication failed: anonymous login expected")
            return ( Context.CODE_FORBIDDEN, rsp)

        if not len(data): data = {'filename': logName, 'result-path': logPath, 'file-data': logData }
        
        # we can upload only zip file
        if not data['filename'].endswith(".zip") and not data['filename'].endswith(".png") and not data['filename'].endswith(".jpg") \
            and not data['filename'].endswith(".mp4") :
            self.error("unable to upload log, bad file extension: %s" % data['filename'])
            return ( Context.CODE_FORBIDDEN, rsp)
            
        # checking if testresult path exist!
        archiveRepo='%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        if os.path.exists( "%s/%s" % (archiveRepo, data['result-path']) ):
            ret = RepoArchives.instance().createResultLog(testsPath=archiveRepo , 
                                                        logPath=data['result-path'],
                                                        logName=data['filename'], logData=data['file-data'].data )
            rsp['ret'] = ret
        else:
            raise Exception("result path does not exist")

        return (code,rsp)
            
    @authentication
    def xmlrpc_shiftLocalTime(self, login, password, shift, fromGui=False, rights=[]):
        """
        Shift local time for test
        Granted levels: ADMIN, TESTER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string
        
        @param shift: shift time
        @type shift: integer

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={'ret': False};

        if not isintance(shift, int): raise Exception("integer expected: %s" % type(shift))
        
        f = open("%s/%s/timeshift" % ( Settings.getDirExec(), Settings.get('Paths', 'templates')), "w")
        f.write("%s" % shift)
        f.close()

        return (code,rsp)
    
    @authentication
    def xmlrpc_getImagePreview(self, login, password, data={}, fromGui=False, trPath='', imageName='', projectId=0, rights=[]):
        """
        Get image preview
        Granted levels: ADMIN, TESTER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param trPath: test path name to get
        @type trPath: string
        
        @param trName: test result name to get
        @type trName: string
        
        @param projectId: id of the project to refresh (default=0)
        @type projectId: integer
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={  'ret': False };

        if not len(data): data = { 'projectid': projectId, 'tr-path': trPath, 'image-name': trName }
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            projectId = data['projectid']
            trPath = data['tr-path']
            imageName = data['image-name']
            
            pathFile = "%s/%s" % (trPath, imageName)
            ret = RepoArchives.instance().getFile(pathFile=pathFile, project=projectId, addLock=False)
            rsp['ret'] = ret

        return (code,rsp)
            
    @authentication
    def xmlrpc_getTestPreview(self, login, password,  data={}, fromGui=False, trPath='', trName='', projectId=0, rights=[]):
        """
        Get test preview (reports and comments)
        Granted levels: ADMIN, TESTER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param trPath: test path name to get
        @type trPath: string
        
        @param trName: test result name to get
        @type trName: string
        
        @param projectId: id of the project to refresh (default=0)
        @type projectId: integer

        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'projectid': projectId, 'tr-path': trPath, 'tr-name': trName }
        
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            projectId = data['projectid']
            trPath = data['tr-path']
            trName = data['tr-name']
            
            self.trace("get test preview arguments trPath=%s trName=%s" %(trPath, trName) )
            pathFile = "%s/%s/%s" % (projectId, trPath, trName)
            rsp['comments'] =  RepoArchives.instance().getComments(archivePath=pathFile)

            # filename without extension, example : "Noname1_0_PASS_0.trx
            logFileName =  trName.rsplit('.', 1)[0]
            # and without nb comment and result
            logFileName =  logFileName.rsplit('_', 2)[0]
            
            code, reports = RepoArchives.instance().getTestReport(archivePath=trPath, archiveName=logFileName, 
                                                                  projectId=projectId)
            rsp['reports'] = reports
            code, reports = RepoArchives.instance().getBasicTestReport(archivePath=trPath, archiveName=logFileName, 
                                                                    projectId=projectId)
            rsp['basic-reports'] = reports
            
            code, verdicts = RepoArchives.instance().getTestVerdict(archivePath=trPath, archiveName=logFileName, 
                                                                    projectId=projectId)
            rsp['verdicts'] = verdicts
            code, verdicts = RepoArchives.instance().getTestVerdict(archivePath=trPath, archiveName=logFileName, 
                                                                    projectId=projectId, returnXml=True)
            rsp['xml-verdicts'] = verdicts
            
        return (code,rsp)
            
    @authentication
    def xmlrpc_deleteTestResult(self, login, password,  data={}, fromGui=False, trPath='', projectId=0, rights=[]):
        """
        Delete test result
        Granted levels: ADMIN, TESTER, SYSTEM
        
        @param login: login name
        @type login: string

        @param password: sha1 of the password 
        @type password: string

        @param fromGui: call from gui (default=False)
        @type fromGui: boolean
        
        @param trPath: test result path
        @type trPath: string
        
        @param projectId: id of the project to refresh (default=0)
        @type projectId: integer
        
        @return: ws function name, response code, response data
        @rtype: tuple 
        """
        code = Context.CODE_OK; rsp={};

        if not len(data): data = { 'projectid': projectId, 'tr-path': trPath }
    
        projectId = data['projectid']
        trPath = data['tr-path']

        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=login, projectId=data['projectid'])
        self.trace( "project is authorized ? %s" % projectAuthorized)
        if not projectAuthorized:
            code = Context.CODE_FORBIDDEN
        else:
            rsp['ret'] = RepoArchives.instance().delDirAll(trPath, project=data['projectid'])
            rsp['projectid'] = projectId

        return (code,rsp)
        
class XmlrpcServerInterface(Logger.ClassLogger, threading.Thread):
    def __init__(self, listeningAddress, https=False):
        """
        Constructor 

        @param listeningAddress:
        @type listeningAddress: tuple
        """
        threading.Thread.__init__(self)
        self._stopEvent = threading.Event()
        self.ws = WebServicesUsers()
        if https:
            crt = '%s/%s' % (Settings.getDirExec(),Settings.get('WebServices', 'ssl-cert'))
            key = '%s/%s' % (Settings.getDirExec(),Settings.get('WebServices', 'ssl-key'))
            try:
                ssl_context = ssl.DefaultOpenSSLContextFactory(key, crt)
            except ImportError, e:
                self.error("unable to initialize ssl context: %s" % str(e) )
                self.stop()
            else:
                reactor.listenSSL(  port = listeningAddress[1], factory= server.Site(self.ws), contextFactory=ssl_context, interface=listeningAddress[0])
        else:
            reactor.listenTCP( port = listeningAddress[1], factory= server.Site(self.ws), interface = listeningAddress[0] )

    def run(self):
        """
        Run xml rpc server
        """
        self.trace("XML-RPC server started")
        try:
            while not self._stopEvent.isSet():
                # The default reactor, by default, will install signal handlers
                # to catch events like Ctrl-C, SIGTERM, and so on. However, 
                # you can't install signal handlers from non-main threads in Python,
                # which means that reactor.run() will cause an error.
                # Pass the installSignalHandlers=0 keyword argument to reactor.run 
                # to work around this. 
                reactor.run(installSignalHandlers=0)
        except Exception as e:
            self.error("Exception in XMLRPC server thread: " + str(e))
        reactor.stop()
        self.trace("XML-RPC server stopped")

    def stop(self):
        """
        Stop the xml rpc server
        """
        self._stopEvent.set()
        self.join()


XSI = None # singleton
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return XSI

def initialize (listeningAddress, https):
    """
    Instance creation

    @param listeningAddress:
    @type listeningAddress:
    """
    global XSI
    XSI = XmlrpcServerInterface( listeningAddress = listeningAddress, https=https)

def finalize ():
    """
    Destruction of the singleton
    """
    global XSI
    if XSI:
        XSI = None
