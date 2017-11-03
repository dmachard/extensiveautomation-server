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

"""
FTP agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import sys
import threading
import socket
import time
import re
import os

from ftplib import FTP
try:
    if sys.version_info < (2,7, ):
        from Libs.ftplib import FTP_TLS # python 2.6 support
    else:
        from ftplib import FTP_TLS

    FTPS_SUPPORT = True
except ImportError:
    FTPS_SUPPORT = False
    
import io

try:
    xrange
except NameError: # support python3
    xrange = range
    

    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = ""
__TYPE__="""ftp"""
__RESUME__="""This agent enables to retrieve file through ftp with tls support
Can be used on Linux or Windows."""

__DESCRIPTION__="""This agent enables to retrieve file through ftp.
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
    return Ftp( controllerIp, controllerPort, toolName, toolDesc, 
                        defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    
class FtpContext(object):
    """
    FTP context object
    """
    def __init__(self):
        """
        Constructor
        """
        self.FTP_LIB = None
        self.useTls = False
        self.connected = False
        self.logged = False
        
    def onReset(self):
        """
        On reset 
        """
        try:
            if self.FTP_LIB is not None: self.FTP_LIB.close()
        except Exception as e:
            pass
        self.useTls = False
        self.connected = False
        self.logged = False
        
class Ftp(GenericTool.Tool):
    """
    FTP agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        File agent constructor

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

        self.FTP_LIB = None
        self.useTls = False
        self.__connected = False
        self.__logged = False
        self.nbGetFile = 0
        self.__mutexActionId__ = threading.RLock()
        
    def getId(self):
        """
        Return the ID
        """
        self.__mutexActionId__.acquire()
        self.nbGetFile += 1
        ret = self.nbGetFile
        self.__mutexActionId__.release()
        return ret

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
        self.onToolLogWarningCalled("Starting ftp agent")
        self.onToolLogWarningCalled("Ftp agent started")
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
        self.onToolLogWarningCalled( "<< Resetting Context TestId=%s AdapterId=%s" % (scriptId, adapterId) )
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

        self.onToolLogWarningCalled( "<< Starting Command=%s TestId=%s AdapterId=%s" % (request['data']['cmd'],
                                                                                        request['script_id'], 
                                                                                        request['source-adapter']) )
        try:
            cmd = request['data']['cmd']
            data = request['data']
            
            # connect
            if cmd == 'Connect':
                # init 
                if data['tls-support']:
                    currentTest.ctx().useTls = True
                    if FTPS_SUPPORT:
                        currentTest.ctx().FTP_LIB = FTP_TLS()
                    else:
                        raise Exception('tls not supported')
                    self.onToolLogSuccessCalled( "<< FTP(S) connector initialized" )
                else:
                    currentTest.ctx().FTP_LIB = FTP()
                    self.onToolLogSuccessCalled( "<< FTP connector initialized" )
                    
                # passive mode of not ?
                currentTest.ctx().FTP_LIB.set_pasv(data['passive'])
                
                # connect
                try:
                    connected = currentTest.ctx().FTP_LIB.connect(host=data['dest-ip'] , port=data['dest-port'] )
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    currentTest.ctx().connected = True
                    self.sendNotify(request, data={ 'cmd': cmd } )

            # disconnect
            elif cmd == 'Disconnect':
                if not currentTest.ctx().connected: raise Exception('not connected')
                currentTest.ctx().connected = False
                try:
                    currentTest.ctx().FTP_LIB.quit()
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd } )
                    
            # login
            elif cmd == 'Login':
                if not currentTest.ctx().connected: raise Exception('not connected')
                try:
                    logged = currentTest.ctx().FTP_LIB.login(user=data['user'] , passwd=data['password'] )
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    currentTest.ctx().logged = True
                    self.sendNotify(request, data={ 'cmd': cmd } )

                    # get the welcome message if exists
                    welcome = currentTest.ctx().FTP_LIB.getwelcome()
                    if len(welcome): self.sendNotify(request, data={ 'cmd': "Welcome", 'msg': welcome } )

                    # init protected transfer for ssl
                    if currentTest.ctx().useTls:
                        currentTest.ctx().FTP_LIB.prot_p()
                        self.sendNotify(request, data={ 'cmd': "Secure"} )

            # size of file
            elif cmd == 'Size File':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.size(data['filename'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # delete file
            elif cmd == 'Delete File':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.delete(data['filename'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # rename file
            elif cmd == 'Rename File':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.rename(data['current-filename'], data['new-filename'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # rename folder
            elif cmd == 'Rename Folder':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.rename(data['current-path'], data['new-path'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # add folder
            elif cmd == 'Add Folder':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.mkd(data['path'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # delete folder
            elif cmd == 'Delete Folder':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.rmd(data['path'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # goto folder
            elif cmd == 'Goto Folder':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    rsp = currentTest.ctx().FTP_LIB.cwd(data['path'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
            
            # listing folder
            elif cmd == 'Listing Folder':
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    ret = []
                    if not data['extended']:
                        if 'path' in data: 
                            ret.extend(	currentTest.ctx().FTP_LIB.nlst(data['path']) )
                        else:
                            ret.extend(	currentTest.ctx().FTP_LIB.nlst() )
                    else:
                        def append_data(line):
                            """
                            Append data
                            """
                            ret.append( line )
                        if 'path' in data: 
                            currentTest.ctx().FTP_LIB.dir(data['path'], append_data)
                        else:
                            currentTest.ctx().FTP_LIB.dir(append_data)
                            
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "\n".join(ret) } )
                    
            # get file
            elif cmd == 'Get File':
                if not currentTest.ctx().logged: raise Exception('not logged')
                
                internalID = self.getId()
                
                read_data = []
                def handle_binary(more_data):
                    """
                    Handle binary data
                    """
                    read_data.append(more_data)
                    
                toPrivate = False
                if 'to-private' in data: toPrivate = data['to-private']

                try:
                    rsp = currentTest.ctx().FTP_LIB.retrbinary("RETR %s" % data['filename'], callback=handle_binary)
                    read_data = b"".join(read_data)
                    
                    if toPrivate:
                        self.onToolLogWarningCalled( "<< Uploading file...")
                        self.addCallIdTmpDir("%s" % internalID )
                        
                        # extract just the filename
                        f_name = data['filename'].rsplit("/", 1)
                        if len(f_name) == 1: 
                            f_name = f_name[0]
                        else:
                            f_name = f_name[1]

                        # save the file in the temp area
                        destFile = "%s/%s/%s" % (self.getTemp(), internalID, f_name)
                        f = open(destFile, "wb")
                        f.write(read_data)
                        f.close()
                        
                        # zip the file and upload them
                        ret, pathZip, filenameZip = self.createZip(callId=internalID, zipReplayId=request['test-replay-id'],
                                                                            zipPrefix="agent") 
                        if not ret:
                            self.error('unable to create zip file')
                            try:
                                os.remove(destFile)
                            except Exception as e:
                                pass
                        else:
                            self.uploadZip(callId=internalID, fileName=filenameZip, pathZip=pathZip, 
                                           resultPath=request['result-path'])
                                            
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    if toPrivate:
                        self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp, 'content': "%s" % len(read_data) } )
                    else:
                        self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp, 'content': read_data } )
                    
            # put file
            elif cmd == 'Put File': 
                if not currentTest.ctx().logged: raise Exception('not logged')
                try:
                    if 'raw-content' in data:
                        myfile = io.BytesIO( bytes(data['raw-content'], 'utf8') )
                    if 'from-filename' in data:
                        myfile = open(data['from-filename'], 'rb')

                    rsp = currentTest.ctx().FTP_LIB.storbinary(u'STOR %s' % data['to-filename'], myfile)                        
                    myfile.close()
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp} )
            
            # wait file
            elif cmd == 'Wait File':
                if not currentTest.ctx().logged: raise Exception('not logged')

                ret = False
                timeoutEvent = False
                startTime = time.time()
                try:
                    true_filename=''
                    list_files = []
                    def append_data(line):
                        """
                        Append data
                        """
                        list_files.append( line )
                    while (not timeoutEvent):
                        if (time.time() - startTime) >= data['timeout']:
                            timeoutEvent = True
                        if not timeoutEvent:
                            # list path
                            list_files = []
                            currentTest.ctx().FTP_LIB.dir(data['path'], append_data)
                            for f in list_files:
                                # inspect only folders
                                if not f.startswith('d'): # only file  'drwxr-xr-x 2 0 0 4096 Nov 12 16:51 toto'
                                    # extract filename
                                    #['-rw-r--r--', '1', '501', '501', '49', 'Jan', '20', '18:03', 'xxxxx.xml']
                                    tmp_filename = f.split()
                                    f_name = f.split(' '.join(tmp_filename[4:8]))[1].strip()
                                    
                                    # math ?
                                    if re.match( data['filename'], f_name):
                                        true_filename=f_name
                                        ret = True
                                        timeoutEvent=True

                        if not timeoutEvent: time.sleep(data['watch-every'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': ret, 'path':data['path'], 
                                                    'filename': true_filename   } )

            # wait folder
            elif cmd == 'Wait Folder':
                if not currentTest.ctx().logged: raise Exception('not logged')
                
                ret = False
                timeoutEvent = False
                startTime = time.time()
                try:
                    true_folder=''
                    list_files = []
                    def append_data(line):
                        """
                        Append data
                        """
                        list_files.append( line )
                    while (not timeoutEvent):
                        if (time.time() - startTime) >= data['timeout']:
                            timeoutEvent = True
                        if not timeoutEvent:
                            # list path
                            list_files = []
                            currentTest.ctx().FTP_LIB.dir(data['path'], append_data)
                            for f in list_files:
                                if f.startswith('d'): # only file  'drwxr-xr-x 2 0 0 4096 Nov 12 16:51 toto'
                                    # extract filename
                                    #['-rw-r--r--', '1', '501', '501', '49', 'Jan', '20', '18:03', 'xxxxx.xml']
                                    tmp_filename = f.split()
                                    f_name = f.split(' '.join(tmp_filename[4:8]))[1].strip()
                                    
                                    #if data['folder'] in f:
                                    if re.match( data['folder'], f_name):
                                        true_folder = f_name
                                        ret = True
                                        timeoutEvent=True

                        if not timeoutEvent: time.sleep(data['watch-every'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': ret, 'path':data['path'], 'foldername': true_folder } )
 
            elif cmd == 'Get Folder':
                pass
 
            elif cmd == 'Put Folder':
                pass
                
            # command
            elif cmd == 'Command':
                if not currentTest.ctx().logged: raise Exception('not logged')
                
                try:
                    rsp = currentTest.ctx().FTP_LIB.sendcmd(data['cmd'])
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            # curent path
            elif cmd == 'Current Path':
                if not currentTest.ctx().logged: raise Exception('not logged')
                
                try:
                    rsp = currentTest.ctx().FTP_LIB.pwd()
                except Exception as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                else:
                    self.sendNotify(request, data={ 'cmd': cmd, 'result': "%s" % rsp } )
                    
            else:
                raise Exception('cmd not supported: %s' % cmd )

        except Exception as e:
            self.error( 'unable to run ftp command: %s' % str(e) )
            self.sendError( request , data="unable to run ftp command")

        self.onToolLogWarningCalled( "<< Terminated Command=%s TestId=%s AdapterId=%s" % (request['data']['cmd'],
                                                                                          request['script-id'], 
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
                    ctx_test.ctx_plugin = FtpContext()
                ctx_test.putItem( lambda: self.execAction(request) )
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()