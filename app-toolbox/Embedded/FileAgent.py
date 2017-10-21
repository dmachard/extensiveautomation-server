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

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue
import Libs.LogWatcher as LogWatcher

import sys
import threading
import os
import hashlib
import time
import shutil
import datetime
import difflib
import filecmp
import copy

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
__TYPE__="""file"""
__RESUME__="""This agent deal with disk files and directories on system.
Can be used on Linux or Windows."""
__DESCRIPTION__="""This agent deal with disk files and directories on system.
Can be used on Linux or Windows.

Events messages:
    Agent->Server
        * Error( msg )
        * Data( ... ) - not used
        * Notify( content, cmd, file )

    Server->Agent
        * Init( ... ) - not used
        * Notify( cmd, path )
        * Reset( ... ) - not used

Targetted operating system: Windows and Linux"""

def get_size_path(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)

    return total_size   # in megabytes
    
def initialize (controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return File( controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    
class FollowThread(threading.Thread):
    def __init__(self, parent, request):
        """
        Individual sikuli thread
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.parent = parent
        self.request = request 
        self.following = False
        self.logfile = None
        self.filter = None
        self.watcher = None
        if len(self.request['data']['filter']):
            self.filter = self.request['data']['filter']

    def error(self, msg):
        """
        Trace to log file
        """
        self.parent.error(msg)
        
    def trace(self, msg):
        """
        Trace to log file
        """
        self.parent.trace(msg)

    def startFollow(self, path, extensions):
        """
        """
        self.following = True	
        self.trace("To inspect Path=%s" % path)
        self.watcher =  LogWatcher.LogWatcher(path, self.callback, parent=self, extensions=extensions)
        return self.following
		
    def callback(self, filename, lines):
        """
        """
        for line in lines:
            if self.filter is not None:

                if sys.version_info > (3,):
                    line = unicode(line, 'utf8') # to support python3 
                    if self.filter in line:
                        self.sendNotify(content={'filename': filename, 'content': line} )
                else:
                    if self.filter in line:
                        self.sendNotify(content={'filename': filename, 'content': line} )
            else:
                self.sendNotify(content={'filename': filename, 'content': line})
                
    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )
        
    def sendNotify(self, content):
        """
        Send error to the server
        """
        req =  self.request
        req['data']['cmd'] = 'Log File'
        req['event'] = "agent-notify"
        req['data']['log'] = content
        self.parent.notify( data=req )
        
    def log(self, content):
        """
        """
        self.sendFollow(content)
        
    def sendFollow(self, content):
        """
        Send error to the server
        """
        req =  self.request
        req['data']['cmd'] = 'Event File'
        req['event'] = "agent-notify"
        req['data'] = content
        self.parent.notify( data=req )
        
    def run(self):
        """
        On run function
        """
        try:
            while not self.stopEvent.isSet():
                if self.following:
                    self.watcher.loop(blocking=False)
                    time.sleep(0.1)
        except Exception as e:
            self.sendError("generic exception on thread: %s" % e)

    def stop(self):
        """
        Stop the thread
        """
        self.watcher.close()
        self.following = False
        self.stopEvent.set()

class File(GenericTool.Tool):
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                            supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        File agent

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
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                                    supportProxy=supportProxy, proxyIp=proxyIp, proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__

        # self.testsContext = {}
        self.followThreads = {}
       
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
        try:
            # reset all threads
            for fileId, followThread in self.followThreads.items():
                followThread.stop()
                followThread.join()
        except Exception as e:
            self.error("unable to cleanup properly: %s" % e)
            
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        self.onToolLogWarningCalled("Starting file agent")
        self.onToolLogWarningCalled("File agent started")
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

    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        """
        self.onToolLogWarningCalled( "<< Resetting ScriptId=%s AdapterId=%s" % (scriptId, adapterId) )
        self.trace("Resetting follow threads ScriptId=%s - AdapterId=%s" % (scriptId, adapterId) )
        
        threadDetected = False
        for testId, followThread in self.followThreads.items():
            if testId.startswith( "%s_%s" % (scriptId, adapterId) ):
                threadDetected = True
                break

        if threadDetected:
            fThread = self.followThreads.pop(testId)
            fThread.stop()
            fThread.join()
            del fThread
            
        
        self.trace("reset test terminated")
        self.onToolLogWarningCalled( "<< Reset terminated"  )
        
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
        
    def execAction(self, request):
        """
        Execute action
        """
        self.onToolLogWarningCalled( "<< Command [%s] called" % request['data']['cmd'] )
        try:
            # get file
            if request['data']['cmd'] == 'Get File':
                self.trace("read the file: %s" % str(request['data']['path']) )
                
                # read the file and close it
                filePath = os.path.normpath(request['data']['path'])
                
                if sys.version_info > (3,):
                    fd = open(filePath, 'rb') 
                else:
                    fd = open(request['data']['path'], 'r')
                read_data = fd.read()
                fd.close()

                self.trace("length of the file read: %s" % len(read_data) )
                
                # send the result
                self.sendNotify(request, data={'content': read_data, 
                                                'cmd': request['data']['cmd'], 
                                                'request-id': request['data']['request-id'],
                                                'file':request['data']['path']} )
                                                
            elif request['data']['cmd'] == 'Exists File':
                self.trace("check if the file exists: %s" % request['data']['path'] )
                existsFile =  os.path.exists(request['data']['path'] )
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': existsFile} )
                                                
            elif request['data']['cmd'] == 'Size Of File':
                self.trace("get the size of the file: %s" % request['data']['path'] )
                existsFile = True
                try:
                    fileSize =  os.path.getsize(request['data']['path'] )
                except Exception as e:
                    self.error("unable to get the size of the file: %s" % e )
                    existsFile = False
                    fileSize = 0
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': existsFile,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'size': fileSize} )

            elif request['data']['cmd'] == 'Size Of Directory':
                self.trace("get the size of the folder: %s" % request['data']['path'] )
                existsFolder = True
                try:
                    folderSize =  get_size_path(request['data']['path'] )
                except Exception as e:
                    self.error("unable to get the size of the file: %s" % e )
                    v = False
                    fileSize = 0
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': existsFolder,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'size': folderSize} )
                                                
            elif request['data']['cmd'] == 'Copy File':
                self.trace("copy file %s to %s" % (request['data']['path'], request['data']['path-dst']) )
                fileCopied = True
                try:
                    shutil.copyfile(request['data']['path'], request['data']['path-dst'])
                except Exception as e:
                    self.error("unable to get copy the file: %s" % e )
                    fileCopied = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': fileCopied,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'],
                                                'path-dst':request['data']['path-dst'],
                                                } )
                                                
            elif request['data']['cmd'] == 'Copy Directory':
                self.trace("copy folder %s to %s" % (request['data']['path'], request['data']['path-dst']) )
                dirCopied = True
                try:
                    shutil.copytree(request['data']['path'], request['data']['path-dst'])
                except Exception as e:
                    self.error("unable to get copy the dir: %s" % e )
                    dirCopied = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': dirCopied,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'],
                                                'path-dst':request['data']['path-dst'],
                                                } )
                                                
            elif request['data']['cmd'] == 'Move File':
                self.trace("move file %s to %s" % (request['data']['path'], request['data']['path-dst']) )
                fileMoved = True
                try:
                    shutil.move(request['data']['path'], request['data']['path-dst'])
                except Exception as e:
                    self.error("unable to get move the file: %s" % e )
                    fileMoved = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': fileMoved,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'],
                                                'path-dst':request['data']['path-dst'],
                                                } )
                                                
            elif request['data']['cmd'] == 'Move Directory':
                self.trace("move directory %s to %s" % (request['data']['path'], request['data']['path-dst']) )
                dirMoved = True
                try:
                    shutil.move(request['data']['path'], request['data']['path-dst'])
                except Exception as e:
                    self.error("unable to get move the dir: %s" % e )
                    dirMoved = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': dirMoved,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'],
                                                'path-dst':request['data']['path-dst'],
                                                } )
                                                
            elif request['data']['cmd'] == 'Modification Date Of File':
                self.trace("get modification date of the file: %s" % request['data']['path'] )
                fileExists = True
                try:
                    t = os.path.getmtime(request['data']['path'])
                    fileDate = datetime.datetime.fromtimestamp(t)
                except Exception as e:
                    self.error("unable to delete file: %s" % e)
                    fileExists = False
                    fileDate =  ""
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': fileExists,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'modification-date': str(fileDate) } )
                                                
            elif request['data']['cmd'] == 'List Files':
                self.trace("get list of files in : %s" % request['data']['path'] )
                dirExists = True
                listFiles = []
                try:
                    for dirpath, dirnames, filenames in os.walk(request['data']['path'] ):
                        for f in filenames:
                            listFiles.append( f )
                except Exception as e:
                    self.error("unable to delete file: %s" % e)
                    dirExists = False

                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'result': dirExists,
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'],
                                                'list-files': "\n".join(listFiles) } )
                                                
            elif request['data']['cmd'] == 'Delete File':
                self.trace("delete the file: %s" % request['data']['path'] )
                fileDeleted = True
                try:
                    os.remove( request['data']['path'] )
                except Exception as e:
                    self.error("unable to delete file: %s" % e)
                    fileDeleted = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': fileDeleted} )
                                                
            elif request['data']['cmd'] == 'Delete Directory':
                self.trace("delete the directory: %s" % request['data']['path'] )
                dirDeleted = True
                try:
                    shutil.rmtree( request['data']['path'] )
                except Exception as e:
                    self.error("unable to delete folder: %s" % e)
                    dirDeleted = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': dirDeleted} )
                                                
            elif request['data']['cmd'] == 'Exists Directory':
                self.trace("check if the directory exists: %s" % request['data']['path'] )
                existsDir =  os.path.exists(request['data']['path'] )
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': existsDir} )
                                                
            elif request['data']['cmd'] == 'Is File':
                self.trace("check if file: %s" % request['data']['path'] )
                isFile =  os.path.isfile(request['data']['path'] )
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': isFile} )
                                                           
            elif request['data']['cmd'] == 'Is Directory':
                self.trace("check if folder: %s" % request['data']['path'] )
                isFolder =  os.path.isdir(request['data']['path'] )
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': isFolder} )
                                         
            elif request['data']['cmd'] == 'Is Link':
                self.trace("check if link: %s" % request['data']['path'] )
                isLink =  os.path.islink(request['data']['path'] )
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'], 'result': isLink} )

            elif request['data']['cmd'] == 'Checksum File':
                self.trace("checksum of the file: %s" % str(request['data']['path']) )
                checksumFile = hashlib.md5(open(request['data']['path'], 'rb').read()).hexdigest()
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'path':request['data']['path'],
                                                'request-id': request['data']['request-id'],
                                                'checksum': checksumFile, 'checksum-type': 'md5' } )
            
            elif request['data']['cmd'] == 'Wait For File':
                self.trace("wait for file: %s" % str(request['data']['path']) )
                timeout = False
                timeout = False
                startTime = time.time()
                while (not timeout):
                    time.sleep(0.25)
                    if (time.time() - startTime) >= int(request['data']['timeout']):
                        timeout = True
                    if not timeout:
                        fileExists =  os.path.exists(request['data']['path'])
                        if fileExists:
                            # send the result
                            self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                            'path':request['data']['path'], 
                                                            'result': fileExists,
                                                            'request-id': request['data']['request-id'] } )
                            break
                    else:
                            self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                            'path':request['data']['path'], 
                                                            'request-id': request['data']['request-id'],
                                                            'result': False} )
                                                            
            elif request['data']['cmd'] == 'Wait For Directory':
                self.trace("wait for directory: %s" % request['data']['path'] )
                timeout = False
                startTime = time.time()
                while (not timeout):
                    time.sleep(0.25)
                    if (time.time() - startTime) >= int(request['data']['timeout']):
                        timeout = True
                    if not timeout:
                        folderExists =  os.path.exists(request['data']['path'])
                        if folderExists:
                            # send the result
                            self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                            'path':request['data']['path'], 
                                                            'result': folderExists,
                                                            'request-id': request['data']['request-id'] } )
                            break
                    else:
                            self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                            'path':request['data']['path'], 
                                                            'request-id': request['data']['request-id'],
                                                            'result': False} )
            
            elif request['data']['cmd'] == 'Start Follow File':
                
                
                follow_id = "%s_%s_%s" % (request['script_id'], request['source-adapter'], request['data']['request-id'] )
                self.trace( "Starting follow ScriptId=%s AdapterId=%s" % (request['script_id'], request['source-adapter']) )
                
                if follow_id not in self.followThreads:

                    req_saved = copy.deepcopy(request)
                    newthread = FollowThread(parent=self, request=request  )
                    newthread.startFollow(path=req_saved['data']['path'], extensions=req_saved['data']['extensions'])
                    newthread.start()
                    
                    self.followThreads[ follow_id ] = newthread
                
					 
                    # send the result
                    self.sendNotify(req_saved, data={ 'cmd': req_saved['data']['cmd'],
                                                    'request-id': req_saved['data']['request-id'],
                                                    'extensions': req_saved['data']['extensions'],
                                                    'path': req_saved['data']['path'],
                                                    'result': True  } )
                else:
                 
                    # send the result
                    self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                    'request-id': request['data']['request-id'],
                                                    'extensions': req_saved['data']['extensions'],
                                                    'path': request['data']['path'],
                                                    'result': False  } )
                                                
                                                
            elif request['data']['cmd'] == 'Stop Follow File':

                follow_id = "%s_%s_%s" % (request['script_id'], request['source-adapter'], request['data']['follow-id'] )
                self.trace("stopping follow ScriptId=%s AdapterId=%s" % (request['script_id'], request['source-adapter']) )
                if follow_id in self.followThreads:
                    self.followThreads[ follow_id ].stop()
                    self.followThreads[ follow_id ].join()
                    
                    self.trace("follow id=%s - thread stopped" % follow_id)
                    
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'result': True } )
                self.trace("follow id=%s - notify sent" % follow_id)

            elif request['data']['cmd'] == 'Compare Files':
                self.trace("compare file %s with %s" % (request['data']['path'], request['data']['path-dst']) )
                filesExists = True
                htmlResult = ''
                try:
                    fromlines = open(request['data']['path'], 'U').readlines()
                    tolines = open(request['data']['path-dst'], 'U').readlines()
                    htmlResult = difflib.HtmlDiff().make_file(fromlines, tolines)
                    compareResult = filecmp.cmp(request['data']['path'], request['data']['path-dst'])
                except Exception as e:
                    self.error("unable to compare file: %s" % e )
                    filesExists = False
                    compareResult = False
                # send the result
                self.sendNotify(request, data={ 'cmd': request['data']['cmd'],
                                                'request-id': request['data']['request-id'],
                                                'path':request['data']['path'],
                                                'path-dst':request['data']['path-dst'],
                                                'result': filesExists,
                                                'result-compare': compareResult,
                                                'result-html': htmlResult} )
            # unknown command
            else:
                raise Exception('cmd not supported: %s' % request['data']['cmd'] )
        except Exception as e:
            self.error( 'request received: %s' % request )
            self.error( 'unable to run command: %s' % str(e) )
            self.sendError( request , data="unable to run command")

        self.onToolLogWarningCalled( "<< Command terminated"  )

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
                a = self.context()[request['uuid']][request['source-adapter']]
                a.putItem( lambda: self.execAction(request) )
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()