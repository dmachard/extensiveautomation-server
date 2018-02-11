#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

"""
Database agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import sys
import threading
import socket
import time
import io

try:
    xrange
except NameError: # support python3
    xrange = range

MYSQL_CONNECTOR_READY=True
try:
    import pymysql 
except ImportError:
    try:
        import MySQLdb as pymysql # trying on linux ?
    except ImportError:    
        MYSQL_CONNECTOR_READY=False
        
POSTGRESQL_CONNECTOR_READY=True
try:
    import psycopg2 
except ImportError:
    POSTGRESQL_CONNECTOR_READY=False
    
MSSQL_CONNECTOR_READY=True
try:
    import _mssql
    import pymssql 
except ImportError:
    MSSQL_CONNECTOR_READY=False
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = ""
__TYPE__="""database"""
__RESUME__="""This agent enables to make sql queries. MySQL, PostgreSQL and Microsoft SQL are supported.
Can be used on Linux or Windows."""

__DESCRIPTION__="""This agent enables to make sql queries. MySQL, PostgreSQL and Microsoft SQL are supported.
Can be used on Linux or Windows.

Events messages:
    Agent->Server
        * Error( msg )
        * Data( ... ) - not used
        * Notify( content, cmd, file )

    Server->Agent
        * Init( ... ) - not used
        * Notify( cmd, path, ip, port, user, password )
        * Reset( ... ) - not used

Targetted operating system: Windows and Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, 
                        defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Database( controllerIp, controllerPort, toolName, toolDesc, 
                        defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    
class DbContext(object):
    """
    Database context class
    """
    def __init__(self):
        """
        Constructor
        """
        self.DB_PTR = None
        self.connected = False
        
    def onReset(self):
        """
        Called to reset the context
        """
        try:
            if self.DB_PTR is not None: self.DB_PTR.close()
        except Exception as e:
            pass
            
        self.connected = False
        
        
class Database(GenericTool.Tool):
    """
    Database agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Database agent constructor

        @param controllerIp: controller ip/host
        @type controllerIp: string

        @param controllerPort: controller port
        @type controllerPort: integer

        @param toolName: agent name
        @type toolName: string

        @param toolDesc: agent description
        @type toolDesc: string

        @param defaultTool: True if the agent is started by the server, False otherwise
        @type defaultTool: boolean
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, 
                    defaultTool, supportProxy=supportProxy, proxyIp=proxyIp, 
                    proxyPort=proxyPort, sslSupport=sslSupport)        
        self.__type__ = __TYPE__

    
    def checkPrerequisites(self):
        """
        Check the prerequisistes (database module installed)
        """
        if not MYSQL_CONNECTOR_READY:
            self.onToolLogErrorCalled("MySQL connector is missing!")
            raise Exception("MySQL connector is missing!")
        if not POSTGRESQL_CONNECTOR_READY:
            self.onToolLogErrorCalled("PostgreSQL connector is missing!")
            raise Exception("PostgreSQL connector is missing!")

        if not MSSQL_CONNECTOR_READY:
           self.onToolLogErrorCalled("MsSQL connector is missing!")
           raise Exception("MsSQL connector is missing!")
        
    def getType(self):
        """
        Returns agent type

        @return: agent type
        @rtype: string
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
        In this function, you can stop your program
        """
        pass
            
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        self.onToolLogWarningCalled("Starting database agent")
        self.onToolLogWarningCalled("Database agent started")
        self.onPluginStarted()
    
    def pluginStarting(self):
        """
        Function to reimplement
        """
        pass
        
    def onPluginStarted(self):
        """
        Function to reimplement
        """
        pass
        
    def pluginStopped(self):
        """
        Function to reimplement
        """
        pass

    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass
        
    def onToolLogWarningCalled(self, msg):
        """
        Logs warning on main application

        @param msg: warning message
        @type msg: string
        """
        pass

    def onToolLogErrorCalled(self, msg):
        """
        Logs error on main application

        @param msg: error message
        @type msg: string
        """
        pass

    def onToolLogSuccessCalled(self, msg):
        """
        Logs success on main application

        @param msg: error message
        @type msg: string
        """
        pass
    
    def onAgentAlive(self, client, tid, request):
        """
        Called on keepalive received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass
        
    def onAgentInit(self, client, tid, request):
        """
        Called on init received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass

    def onAgentReset(self, client, tid, request):
        """
        Called on reset received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass
        
    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        On reset test context event
        """
        self.onToolLogWarningCalled( "<< Resetting Context TestID=%s AdapterId=%s" % (scriptId, adapterId) )
        self.trace("Resetting TestUuid=%s ScriptId=%s AdapterId=%s" % (testUuid, scriptId, adapterId) )

        currentTest = self.context()[testUuid][adapterId]
        if currentTest.ctx() is not None:
            currentTest.ctx().onReset()
            
        # cleanup test context
        self.cleanupTestContext(testUuid, scriptId, adapterId)
        
    def execAction(self, request):
        """
        Execute action
        """
        currentTest = self.context()[request['uuid']][request['source-adapter']]
        
        self.onToolLogWarningCalled( "<< Starting SQL=%s TestId=%s AdapterId=%s" % (request['data']['cmd'],
                                                                                    request['script_id'], 
                                                                                    request['source-adapter']) )
        try:
            cmd = request['data']['cmd']
            data = request['data']
            
            # connect
            if cmd == 'Connect':
                try:
                    if data['dbtype'] == 'mysql':
                        currentTest.ctx().DB_PTR = pymysql.connect( host = data['host'],  user = data['user'], 
                                                                    passwd = data['password'], 
                                                                    port=data['port'], connect_timeout=int(data['timeout']), 
                                                                    db = data['db-name'] )
                        self.onToolLogSuccessCalled( "<< MySQL connector initialized" )
                    elif data['dbtype'] == 'mssql':
                        self.onToolLogErrorCalled("MsSQL connector not yet supported!")
                        raise Exception("MsSQL not yet supported")
                    elif data['dbtype'] == 'postgresql':
                        sslMode = 'disable'
                        if data['ssl-support']: sslMode = 'require'
                        currentTest.ctx().DB_PTR = psycopg2.connect( host = data['host'],  user = data['user'], 
                                                                    password = data['password'], 
                                                                    port=data['port'], database = data['db-name'], 
                                                                    sslmode=sslMode,
                                                                    connect_timeout=int(data['timeout'])      )
                        self.onToolLogSuccessCalled( "<< PosgreSQL connector initialized" )
                    else:
                        raise Exception('database not yet supported: %s' % data['dbtype'] )
                except psycopg2.Error as err:
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (0, str(err)) } )
                except pymssql.Error as err:
                    code, msg = err.args
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (code, msg) } )
                except pymysql.Error as err:
                    code, msg = err.args
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (code, msg) } )
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "generic-err-msg": str(e)} )
                else:
                    currentTest.ctx().connected = True
                    self.sendNotify(request, data={ 'cmd': cmd, 'host': data['host'], 'port': data['port'], 
                                                    'user': data['user'], 'password': data['password']  } )
                        
            # disconnect
            elif cmd == 'Disconnect':
                if not currentTest.ctx().connected: raise Exception('db not connected')
            
                try:
                    currentTest.ctx().DB_PTR.close()
                except psycopg2.Error as err:
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (0, str(err)) } )
                except pymssql.Error as err:
                    code, msg = err.args
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (code, msg) } )
                except pymysql.Error as err:
                    code, msg = err.args
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (code, msg) } )
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "generic-err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'host': data['host'], 'port': data['port'], 
                                                    'user': data['user'], 'password': data['password']  } )
            
            # query
            elif cmd == 'Query':
                if not currentTest.ctx().connected: raise Exception('db not connected')

                try:
                    cursor = currentTest.ctx().DB_PTR.cursor()
                    cursor.execute ( data['query'] )

                    i = 0
                    self.sendNotify(request, data={ 'cmd': 'Executed', 'host': data['host'], 
                                                    'port': data['port'], 'user': data['user'],
                                                    'password': data['password'],  
                                                    'nb-changed': str(cursor.rowcount) } )
                    
                    try:
                        row = cursor.fetchone()
                        while row:
                            i += 1
                            # as dict
                            fields = map(lambda x:x[0], cursor.description)
                            ret = dict(zip(fields,row))
                            
                            # each value as str
                            ret_str = {}
                            if 'query-name' in data: ret_str['query-name'] = data['query-name']
                            for k,v in ret.items(): ret_str[k] = str(v)

                            # log response event
                            self.sendNotify(request, data={ 'cmd': cmd, 'host': data['host'], 
                                                            'port': data['port'], 'user': data['user'], 
                                                            'password': data['password'],  'row': ret_str, 
                                                            'row-index': i, 'row-max': cursor.rowcount} )
                            
                            row = cursor.fetchone()
                    except psycopg2.ProgrammingError as e:
                        pass # no more to read 
                    # except MySQLdb.Error as e:
                        # pass # no more to read 
                    except pymysql.Error as e:
                        pass # no more to read 
                        
                    # close the cursor and commit
                    cursor.close ()
                    currentTest.ctx().DB_PTR.commit ()
                except psycopg2.Error as err:
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (0, str(err)) } )
                except pymssql.Error as err:
                    code, msg = err.args
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (code, msg) } )
                except pymysql.Error as e:
                    code, msg = err.args
                    self.sendError( request , data={"cmd": cmd , "database-err-msg": (code, msg) } )
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "generic-err-msg": str(e)} )
                else:
                    # log response event
                    self.sendNotify(request, data={ 'cmd': 'Terminated', 'host': data['host'], 'port': data['port'], 
                                                    'user': data['user'], 'password': data['password'],
                                                    'nb-row': i } )

            else:
                raise Exception('cmd not supported: %s' % cmd )
                
        except Exception as e:
            self.error( 'unable to run sql query: %s' % str(e) )
            self.sendError( request , data="unable to run sql query")

        self.onToolLogWarningCalled( "<< Terminating SQL=%s TestId=%s AdapterId=%s" % ( request['data']['cmd'],
                                                                                        request['script_id'], 
                                                                                        request['source-adapter']) )

    def onAgentNotify(self, client, tid, request):
        """
        Called on notify received from test server and dispatch it
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        self.__mutex__.acquire()
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                ctx_test = self.context()[request['uuid']][request['source-adapter']]
                if ctx_test.ctx() is None: 
                    ctx_test.ctx_plugin = DbContext()
                ctx_test.putItem( lambda: self.execAction(request) )
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()