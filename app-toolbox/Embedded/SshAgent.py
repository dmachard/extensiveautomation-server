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
Ssh agent
"""

import Core.GenericTool as GenericTool
import Libs.Settings as Settings

import sys
import threading
import socket
import os
import errno
import select
import io
import time
import stat
import re

try:
    xrange
except NameError: # support python3
    xrange = range
    

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
EXT_SSH_LIB_INSTALLED=True
try:
	import paramiko
except ImportError as e:
    EXT_SSH_LIB_INSTALLED=False

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = ""
__TYPE__="""ssh"""
__RESUME__="""SSH and SFTP agent for windows and linux platform."""

__DESCRIPTION__="""SSH and SFTP agent for windows and linux platform.

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


IPv4    = 4
IPv6    = 6

INIT6_STREAM_SOCKET     = 6     # AF_INET6, SOCK_STREAM, 0 (or IPPROTO_TCP), TCP over IPv6
INIT_STREAM_SOCKET      = 9     # AF_INET, SOCK_STREAM, 0 (or IPPROTO_TCP), TCP over IPv4

LISTING_FOLDER = "Listing Folder"
DELETE_FOLDER = "Delete Folder"
ADD_FOLDER = "Add Folder"
RENAME_FOLDER = "Rename Folder"

RENAME_FILE = "Rename File"
DELETE_FILE = "Delete File"

PUT_FILE = "Put File"
GET_FILE = "Get File"

WAIT_FILE = "Wait File"
WAIT_FOLDER = "Wait Folder"

GET_FOLDER = "GET FOLDER"
PUT_FOLDER = "PUT FOLDER"

def getSocket(sockType):
    """
    Get socket 

    @return: socket
    @rtype: socket
    """
    if sockType == INIT6_STREAM_SOCKET: # TCP over IPv6
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    elif sockType == INIT_STREAM_SOCKET: #  TCP over IPv4
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    else:
        sock = None
    return sock

    
class SockTcpThread(threading.Thread):
    """
    Tcp socket thread
    """
    def __init__(self, parent, request, sshlib):
        """
        Individual socket
        """
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.__mutex__ = threading.RLock()
        self.__mutexActionId__ = threading.RLock()
        self.parent = parent
        self.request = request 
        self.socket = None
        self.sshTranport = None
        self.sshChannel = None
        self.cfg = request['data']
        self.connected = False   
        self.channelOpened = False
        self.sshlib = sshlib
        self.nbGetFile = 0
        self.__checkConfig()
        
    def getId(self):
        """
        Return ID
        """
        self.__mutexActionId__.acquire()
        self.nbGetFile += 1
        ret = self.nbGetFile
        self.__mutexActionId__.release()
        return ret

    def trace(self, txt):
        """
        Trace
        """
        self.parent.trace( str(txt) )
        
    def onReset(self):
        """
        Stop on reset
        """
        self.stop()
        
    def error(self, err):
        """
        Log error
        """
        self.parent.error( str(err) )
        
    def __checkConfig(self):
        """
        private function
        """
        # log all configuration parameters
        self.trace(  "cfg: %s"  %  self.cfg )

    def sendError(self, data):
        """
        Send error to the server
        """
        self.error( "send error: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-error"
        req['data'] = data
        self.parent.notify( data=req )

    def sendNotify(self, data):
        """
        Send notify to the server
        """
        self.trace( "send notify: %s"  % str(data) )
        req =  self.request
        req['event'] = "agent-notify"
        req['data'] = data
        self.parent.notify( data=req )
    
    def sendData(self, data):
        """
        Send data to the server
        """
        self.trace( "send data: %s"  % len(data) )
        req =  self.request
        req['event'] = "agent-data"
        req['data'] = data
        self.parent.notify( data=req )

    def __negotiation(self):
        """
        Sub function to start the negotiation
        """
        self.sshTranport = self.sshlib.Transport(self.socket)
        try:
            self.sshTranport.start_client()
        except Exception as e:	
            self.sendNotify(data={'ssh-event': 'negotiation-failed', 'err': '%s' % e } )
        
        # nego ok
        else:
            self.sendNotify(data={'ssh-event': 'negotiation-ok' } )
            
    def __authentication(self, login, password, privateKey):
        """
        Sub function to start the negotiation
        """
        try:
            if len(privateKey):
                key = self.sshTranport.get_remote_server_key()
                
                # read first line of the private key to detect the type
                key_head=privateKey.splitlines()[0]
                if 'DSA' in key_head:
                    keytype=paramiko.DSSKey
                elif 'RSA' in key_head:
                    keytype=paramiko.RSAKey
                else:
                    raise Exception("Invalid key type: %s" % key_head)
                
                # construct the key
                keyfile = io.StringIO( unicode(privateKey) )
                pkey=keytype.from_private_key(keyfile)
                
                # try to make the authen
                self.sshTranport.auth_publickey(login, pkey)
            else:
                self.sshTranport.auth_password(login, password)
        except Exception as e:
            self.sendNotify(data={'ssh-event': 'authentication-failed', 'err': '%s' % e } )
        
        # authen ok 
        else:
            self.sendNotify(data={'ssh-event': 'authentication-ok' } )
    
    def __opensession(self, sftpSupport, vterm='vt100', width=300, height=300):
        """
        Internal function
        Open a ssh channel
        """
        try:
            if sftpSupport:
                self.sshChannel = self.sshTranport.open_sftp_client()
            else:
                self.sshChannel = self.sshTranport.open_session()
                self.sshChannel.get_pty(term=vterm, width=width, height=height)
                self.sshChannel.invoke_shell()
                self.sshChannel.settimeout(0.0)
        except Exception as e:
            if sftpSupport:
                self.sendNotify(data={'ssh-event': 'sftp-opening-failed', 'err': '%s' % e } )
            else:
                self.sendNotify(data={'ssh-event': 'channel-opening-failed', 'err': '%s' % e } )

        # channel opened 
        else:
            if sftpSupport:
                self.sendNotify(data={'ssh-event': 'sftp-opened' } )
            else:
                self.channelOpened = True
                self.sendNotify(data={'ssh-event': 'channel-opened' } )
    
    def __listingfolder(self, path, extended):
        """
        Internal function
        Make a listing of the folder provided
        """
        try:
            if extended:
                ret = []
                ret_tmp = self.sshChannel.listdir_attr(path=path)
                for attr in ret_tmp:
                    ret.append( str(attr) )
            else:
                ret = self.sshChannel.listdir(path=path)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': LISTING_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'folder-listing', 'cmd': LISTING_FOLDER, 'rsp': '\n'.join(ret) } )
    
    def __addfolder(self, path, mode):
        """
        Internal function
        Add a folder in the ssh channel
        """
        try:
            self.sshChannel.mkdir(path, mode)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': ADD_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'folder-added', 'cmd': ADD_FOLDER } )
    
    def __renamefolder(self, currentPath, newPath):
        """
        Internal function
        Rename a folder
        """
        try:
            self.sshChannel.rename(currentPath, newPath)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': RENAME_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'folder-renamed', 'cmd': RENAME_FOLDER } )

    def __deleteFile(self, filename):
        """
        Internal function
        Delete a file
        """
        try:
            self.sshChannel.remove(filename)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': DELETE_FILE, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'file-deleted', 'cmd': DELETE_FILE } )
        
    def __renameFile(self, currentFilename, newFilename):
        """
        Internal function
        Rename a file
        """
        try:
            self.sshChannel.rename(currentFilename, newFilename)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': RENAME_FILE, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'file-renamed', 'cmd': RENAME_FILE } )
        
    def __deleteFolder(self, path):
        """
        Internal function
        Delete a folder
        """
        try:
            self.sshChannel.rmdir(path)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': DELETE_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'folder-deleted', 'cmd': DELETE_FOLDER } )
                
    def __getFile(self, filename, toPrivate=False):
        """
        Internal function
        Get a file
        """
        internalID = self.getId()

        try:
            myfile = io.BytesIO()
            self.sshChannel.getfo(filename, myfile)
            read_data = myfile.getvalue() 
            
            if toPrivate:
                self.parent.onToolLogWarningCalled( "<< Uploading file...")
                self.parent.addCallIdTmpDir("%s" % internalID )
                
                # extract just the filename
                f_name = filename.rsplit("/", 1)
                if len(f_name) == 1: 
                    f_name = f_name[0]
                else:
                    f_name = f_name[1]

                # save the file in the temp area
                destFile = "%s/%s/%s" % (self.parent.getTemp(), internalID, f_name)
                f = open(destFile, "wb")
                f.write(read_data)
                f.close()
                
                # zip the file and upload them
                ret, pathZip, filenameZip = self.parent.createZip(callId=internalID, zipReplayId=self.request['test-replay-id'],
                                                                    zipPrefix="agent") 
                if not ret:
                    self.parent.error('unable to create zip file')
                    try:
                        os.remove(destFile)
                    except Exception as e:
                        pass
                else:
                    self.parent.uploadZip(callId=internalID, fileName=filenameZip, pathZip=pathZip, 
                                            resultPath=self.request['result-path'])
                    
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': GET_FILE, 'err': "%s" % e } )
        else:
            if toPrivate:
                self.sendNotify(data={'sftp-event': 'file-downloaded', 'cmd': GET_FILE, 'content': "%s" % len(read_data) } )
            else:
                self.sendNotify(data={'sftp-event': 'file-downloaded', 'cmd': GET_FILE, 'content': read_data} )
        
    def __putFile(self, toFilename, fromFilename, rawContent):
        """
        Internal function
        Upload a file in the remote side
        """
        try:
            if len(rawContent):
                if sys.version_info > (3,):
                    myfile = io.BytesIO( bytes(rawContent, 'utf8') )
                else:
                    myfile = io.BytesIO( rawContent )
                    
            if len(fromFilename):
                myfile = open(fromFilename, 'rb')
            
            rsp = self.sshChannel.putfo(myfile, toFilename)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': PUT_FILE, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'file-uploaded', 'cmd': PUT_FILE, 'rsp': str(rsp) } )
    
    def __waitFile(self, path, filename, timeout, watchEvery=0.1):
        """
        Internal function
        Wait a file to appear in the remote side
        """
        timeoutEvent = False
        ret = False
        startTime = time.time()
        try:
            true_filename=''
            while (not timeoutEvent):
                if (time.time() - startTime) >= timeout:
                    timeoutEvent = True
                if not timeoutEvent:
                    # list path
                    ret_tmp = self.sshChannel.listdir_attr(path=path)
                    for f in ret_tmp:
                        if not stat.S_ISDIR(f.st_mode):
                            if re.match( filename, f.filename):
                            #if filename in f.filename:
                                true_filename = f.filename
                                ret = True
                                timeoutEvent=True
                if not timeoutEvent: time.sleep(watchEvery)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': WAIT_FILE, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'wait-file', 'cmd': WAIT_FILE, 'result': ret, 'filename': true_filename, 'path': path } )

    def __waitFolder(self, path, folder, timeout, watchEvery=0.1):
        """
        Internal function
        Wait a folder to appear in the remote side
        """
        timeoutEvent = False
        ret = False
        startTime = time.time()
        try:
            true_folder=''
            while (not timeoutEvent):
                if (time.time() - startTime) >= timeout:
                    timeoutEvent = True
                if not timeoutEvent:
                    # list path
                    ret_tmp = self.sshChannel.listdir_attr(path=path)
                    for f in ret_tmp:
                        if stat.S_ISDIR(f.st_mode):
                            #if folder in f.filename:
                            if re.match( folder, f.filename):
                                true_folder = f.filename
                                ret = True
                                timeoutEvent=True
                if not timeoutEvent: time.sleep(watchEvery)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': WAIT_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'wait-folder', 'cmd': WAIT_FOLDER, 'result': ret, 'folder': true_folder, 'path': path } )
      
    def __putFolder(self, fromPath, toPath, overwrite=False):
        """
        Internal function
        Upload a folder in the remote side
        """
        try:
            rsp = 0 # nb files uploaded
            rsp = self.__putFolderSub(fromPath=fromPath, toPath=toPath, overwrite=overwrite)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': PUT_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'folder-uploaded', 'cmd': PUT_FOLDER, 'rsp': str(rsp) } )
            
    def __putFolderSub(self, fromPath, toPath, overwrite=False):
        """
        Internal function
        Upload a sub folders
        """
        nb_file = 0
        for item in os.listdir(fromPath):
            itempath = os.path.join(fromPath, item)
            if os.path.isfile(itempath):
                # upload the local file to the remote
                try:
                    myfile = open(itempath, 'rb')
                    rsp = self.sshChannel.putfo(myfile, "%s/%s" % (toPath, item) )
                except Exception as e:
                    if not overwrite: raise e
                else:
                    nb_file += 1
            elif os.path.isdir(itempath):
                # create folder in remote side
                destFolder = "%s/%s" % (toPath, item)
                try:
                    self.sshChannel.mkdir(destFolder , 511)
                except Exception as e:
                    if not overwrite: raise e
                # recursive call in this folder
                nb_file += self.__putFolderSub(fromPath=itempath, toPath=destFolder, overwrite=overwrite)
        return nb_file
        
    def __getFolder(self, fromPath, toPath, overwrite=False):
        """
        Internal function
        Download a folder
        """
        try:
            rsp = 0 # nb files detected
            rsp = self.__getFolderSub(fromPath=fromPath, toPath=toPath, overwrite=overwrite)
        except Exception as e:
            self.sendNotify(data={'sftp-event': 'response-error', 'cmd': GET_FOLDER, 'err': "%s" % e } )
        else:
            self.sendNotify(data={'sftp-event': 'folder-downloaded', 'cmd': GET_FOLDER, 'rsp': str(rsp) } )

    def __getFolderSub(self, fromPath, toPath, overwrite=False):
        """
        Internal function
        Download all sub folders
        """
        nb_file = 0
        ret_tmp = self.sshChannel.listdir_attr(path=fromPath)
        for f in ret_tmp:
            # handle folder
            if stat.S_ISDIR(f.st_mode):
                # add the remote folder in the local side
                try:
                    destFolder = "%s/%s" % (toPath, f.filename)
                    os.mkdir( destFolder, 755 )
                except OSError as e:
                    if e.errno == errno.EEXIST and not overwrite:
                        self.sendNotify(data={'sftp-event': 'response-error', 'cmd': GET_FOLDER, 
                                                'err': "os error folder: %s" % e} )
                        break
                # recursive call
                nb_file += self.__getFolderSub(fromPath="%s/%s/" % (fromPath,f.filename), 
                                                toPath=destFolder, overwrite=overwrite)
            
            # handle files
            else:
                nb_file += 1
                
                myfile = io.BytesIO()
                self.sshChannel.getfo( "%s/%s" % (fromPath,f.filename) , myfile)
                read_data = myfile.getvalue() 
                
                # download the remote file to the local side
                try:
                    destFile = "%s/%s" % (toPath,f.filename)

                    f = open(destFile, "wb")
                    f.write(read_data)
                    f.close()
                except OSError as e:
                    if e.errno == errno.EEXIST and not overwrite:
                        self.sendNotify(data={'sftp-event': 'response-error', 'cmd': GET_FOLDER, 
                                            'err': "os error file: %s" % e} )
                        break
                del read_data
        return nb_file
        
    def __senddata(self, data):
        """
        Internal function
        Send data
        """
        try:
            self.sshChannel.send(data)
        except Exception as e:
            self.sendError( data= { 'ssh-event': "send-data-error", 'more': "%s" % str(e) } )
            
    def onNotify(self, client, tid, request):
        """
        Called from remote peer to send data to the socket
        """
        cmd = request['data']
        
        # ssh
        if cmd['cmd'] == 'negotiation':
            t = threading.Thread(target=self.__negotiation)
            t.start()
        
        elif cmd['cmd'] == 'authentication':
            t = threading.Thread(target=self.__authentication, kwargs={'login':cmd['login'], 
                                    'password': cmd['password'], 'privateKey': cmd['private-key'] } )
            t.start()

        elif cmd['cmd'] == 'open-session':
            termType='vt100'; termWidth=300; termHeight=300;
            if "terminal-type" in cmd:  termType=cmd['terminal-type']
            if "terminal-width" in cmd: termWidth=cmd['terminal-width']
            if "terminal-height" in cmd: termHeight=cmd['terminal-height']

            t = threading.Thread(target=self.__opensession, kwargs={'sftpSupport':cmd['sftp-support'], 
                                                                    'vterm': cmd['terminal-type'],
                                                                    'width': cmd['terminal-width'], 
                                                                    'height': cmd['terminal-height'] } )
            t.start()
            
        elif cmd['cmd'] == 'send-data':
            self.__senddata(data=cmd['data'])
        
        # sftp command
        elif cmd['cmd'] == LISTING_FOLDER:
            t = threading.Thread(target=self.__listingfolder, kwargs={ 'path':cmd['path'], 
                                                                       'extended': cmd['extended']} )
            t.start()

        elif cmd['cmd'] == ADD_FOLDER:
            t = threading.Thread(target=self.__addfolder, kwargs={ 'path':cmd['path'], 
                                                                   'mode': cmd['mode']} )
            t.start()

        elif cmd['cmd'] == RENAME_FOLDER:
            t = threading.Thread(target=self.__renamefolder, kwargs={ 'currentPath':cmd['current-path'], 
                                                                      'newPath':cmd['new-path']} )
            t.start()

        elif cmd['cmd'] == RENAME_FILE:
            t = threading.Thread(target=self.__renameFile, kwargs={ 'currentFilename':cmd['current-filename'],
                                                                    'newFilename':cmd['new-filename']} )
            t.start()

        elif cmd['cmd'] == DELETE_FILE:
            t = threading.Thread(target=self.__deleteFile, kwargs={ 'filename':cmd['filename']} )
            t.start()

        elif cmd['cmd'] == DELETE_FOLDER:
            t = threading.Thread(target=self.__deleteFolder, kwargs={ 'path':cmd['path']} )
            t.start()

        elif cmd['cmd'] == PUT_FILE:
            t = threading.Thread(target=self.__putFile, kwargs={ 'toFilename':cmd['to-filename'], 
                                                                 'fromFilename':cmd['from-filename'], 
                                                                 'rawContent':cmd['raw-content']} )
            t.start()

        elif cmd['cmd'] == GET_FILE:
            toPrivate = False
            if 'to-private' in cmd: toPrivate = cmd['to-private']
            t = threading.Thread(target=self.__getFile, kwargs={ 'filename':cmd['filename'], 
                                                                 'toPrivate': toPrivate } )
            t.start()

        elif cmd['cmd'] == WAIT_FILE:
            t = threading.Thread(target=self.__waitFile, kwargs={ 'path':cmd['path'], 
                                                                  'filename':cmd['filename'], 
                                                                  'timeout':cmd['timeout'], 
                                                                  'watchEvery': cmd['watch-every']})
            t.start()

        elif cmd['cmd'] == WAIT_FOLDER:
            t = threading.Thread(target=self.__waitFolder, kwargs={ 'path':cmd['path'], 
                                                                    'folder':cmd['folder'], 
                                                                    'timeout':cmd['timeout'], 
                                                                    'watchEvery': cmd['watch-every']})
            t.start()
            
        elif cmd['cmd'] == GET_FOLDER:
            t = threading.Thread( target=self.__getFolder, kwargs={ 'fromPath':cmd['from-path'], 
                                                                    'toPath':cmd['to-path'], 
                                                                    'overwrite':cmd['overwrite']} )
            t.start()
            
        elif cmd['cmd'] == PUT_FOLDER:
            t = threading.Thread( target=self.__putFolder, kwargs={ 'fromPath':cmd['from-path'], 
                                                                    'toPath':cmd['to-path'], 
                                                                    'overwrite':cmd['overwrite']} )
            t.start()
            
        else:
            self.error("cmd not yet implemented: %s" % cmd['cmd'])

    def createTcpSocket(self):
        """
        Create a tcp socket and start the connection
        """
        try:
            self.trace( 'init connect' )
            # set the socket version
            if self.cfg['sock-family'] == IPv4:
                sockType = INIT_STREAM_SOCKET
            elif  self.cfg['sock-family'] == IPv6:
                sockType = INIT6_STREAM_SOCKET
            else:
                self.sendError( { 'ssh-event':'socket-family-unknown', 
                                    'more': '%s' % str(self.cfg['socket-family'])} )
                self.stop()
                
            # Create the socket
            self.trace( 'get socket connect' )
            self.socket = getSocket(sockType)
            self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            if self.cfg['tcp-keepalive'] and sys.platform != "win32":
                # active tcp keep alive
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # seconds before sending keepalive probes
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.cfg['tcp-keepalive-interval'] ) 
                # interval in seconds between keepalive probes
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.cfg['tcp-keepalive-interval']) 
                # failed keepalive probes before declaring the other end dead
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5) 

            self.trace( 'set sock timeout' )
            self.socket.settimeout( self.cfg['sock-timeout'] )
            self.trace( 'bind socket on %s:%s' % (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.socket.bind( (self.cfg['bind-ip'], self.cfg['bind-port']) )
            self.__setSource()  

            # Connect the socket
            self.trace( 'ssh connect' )
            self.socket.connect( (self.cfg['dst-ip'], self.cfg['dst-port']) )

            # Connection successful
            self.connected = True
            self.onConnection()      

        except socket.timeout as e:
            self.onConnectionTimeout(e)
        except socket.error as e:
            if sys.version_info > (3,):
                errno = e.errno
                strerror = os.strerror(errno)
                self.onConnectionFailed(errno=errno, errstr=strerror)
            else:
                (errno, errstr) = e
                if errno == 111:
                    self.onConnectionRefused()
                else:
                    self.onConnectionFailed(errno=errno, errstr=errstr)
                
        # new with python3
        except ConnectionAbortedError as e:
            self.onDisconnectionByPeer(msg=e)
        except ConnectionRefusedError as e:
            self.onConnectionRefused()
        except ConnectionResetError as e:
            self.onDisconnectionByPeer(msg=e)
        # end of new
                
        except Exception as e:
            self.sendError( data= { 'ssh-event': "connect-error", 'more': "%s" % str(e) } )
            self.stop()

    def __setSource(self):
        """
        Set the source ip and port
        """
        srcIp, srcPort = self.socket.getsockname()
        self.sendNotify(data={'ssh-event': 'initialized', 'src-ip': srcIp, 'src-port': srcPort} )

    def onConnection(self):
        """
        On connection tcp
        """
        self.sendNotify(data={'ssh-event': 'connected' } )
    
    def onConnectionRefused(self):
        """
        On connection refused
        """
        self.sendNotify(data={'ssh-event': 'connection-refused' } )
        self.stop()

    def onConnectionFailed(self, errno, errstr):
        """
        On connection failed
        """
        self.sendNotify(data={'ssh-event': 'connection-failed', 'err-no': errno, 'err-str': errstr} )
        self.stop()

    def onConnectionTimeout(self, e):
        """
        On connection timeout
        """
        self.sendNotify(data={'ssh-event': 'connection-timeout', 'more': str(e) } )
        self.stop()

    def onDisconnectionByPeer(self, msg):
        """
        On disconnection by peer
        """
        self.sendNotify(data={'ssh-event': 'disconnected-by-peer', 'more': str(msg)} )
        self.stop()

    def onSocketError(self, e):
        """
        On tcp socket error
        """
        self.sendError( data={ 'ssh-event': "socket-error", "more": "%s" % str(e) } )
        self.stop()
        
    def run(self):
        """
        On run function
        """
        while not self.stopEvent.isSet():
            time.sleep(0.05)
            self.__mutex__.acquire()
            try:
                if self.connected:
                    if self.channelOpened:
                        r, w, e = select.select([self.sshChannel], [], [self.sshChannel], 0.01)
                        if self.sshChannel in e:
                            raise EOFError("raw socket select error")
                        elif self.sshChannel in r:
                            data = self.sshChannel.recv(2048)
                            self.trace('data received (bytes %d)...' % len(data))
                            self.sendData(data=data)
            except EOFError as e:
                self.onDisconnectionByPeer(e)
            except socket.error as e:
                self.onSocketError(e)
            except Exception as e:
                self.sendError( data={ 'socket-raw-event': "on-run", "more": "%s" % str(e) } )
            self.__mutex__.release()
        self.cleanSocket()
    
    def closeSocket(self):
        """
        Close the socket
        """
        self.cleanSocket()
        self.sendNotify(data={'ssh-event': 'closed' } )

    def cleanSocket(self):
        """
        Clean the socket
        """
        if self.socket is not None: 
            self.socket.close()
        self.channelOpened = False
        self.connected = False
        
    def stop(self):
        """
        Stop the thread
        """
        self.trace('set stop event')
        self.stopEvent.set()
        
def initialize (controllerIp, controllerPort, toolName, toolDesc, 
                        defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Ssh( controllerIp, controllerPort, toolName, toolDesc, 
                        defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    

class Ssh(GenericTool.Tool):
    """
    Ssh agent class
    """
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Ssh agent

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
        if EXT_SSH_LIB_INSTALLED: 
            paramiko.util.log_to_file( "%s/%s/sshlog_%s.txt" % (Settings.getDirExec(), 
                                                                Settings.get( 'Paths', 'logs' ), 
                                                                toolName) )

    def checkPrerequisites(self):
        """
        Check prerequisites before to execute the agent
        """
        if not EXT_SSH_LIB_INSTALLED: 
            self.onToolLogErrorCalled("SSH library is not installed")
            raise Exception("paramiko ssh librarie not installed on system")
        
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
        self.onToolLogWarningCalled("Starting ssh agent")
        self.onToolLogWarningCalled("Ssh agent started")
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
        To reimplement
        Called on reset
        """
        pass

    def execAction(self, client, tid, request):
        """
        Execute action
        """
        currentTest = self.context()[request['uuid']][request['source-adapter']]
        
        self.onToolLogWarningCalled( "<< Starting SSH=%s TestId=%s AdapterId=%s" % (request['data']['cmd'], 
                                                                                    request['script_id'], 
                                                                                    request['source-adapter']) )
        try:
            cmd = request['data']['cmd']
            if cmd == 'connect':
                currentTest.ctx().createTcpSocket()
                if not currentTest.ctx().is_alive():
                    currentTest.ctx().start()
            elif cmd == 'disconnect':
                currentTest.ctx().closeSocket()
            else:
                currentTest.ctx().onNotify(client, tid, request)
        except Exception as e:
            self.error( 'unable to run ssh action: %s' % str(e) )
            self.sendError( request , data="unable to run ssh action")
        self.onToolLogWarningCalled( "<< Terminating SSH=%s TestId=%s AdapterId=%s" % ( request['data']['cmd'], 
                                                                                        request['script_id'], 
                                                                                        request['source-adapter']) )

    def onResetTestContext(self, testUuid, scriptId, adapterId):
        """
        Called on reset of the test context
        """
        self.onToolLogWarningCalled( "<< Resetting Context TestID=%s AdapterId=%s" % (scriptId, adapterId) )
        self.trace("Resetting TestUuid=%s ScriptId=%s AdapterId=%s" % (testUuid, scriptId, adapterId) )

        currentTest = self.context()[testUuid][adapterId]
        if currentTest.ctx() is not None:
            try:
                self.trace('closing socket and stopping thread')
                currentTest.ctx().closeSocket()
                currentTest.ctx().stop()
                currentTest.ctx().join()
                self.trace('ssh sock thread stopped')
            except Exception as e:
                self.error( "unable to reset ssh sock thread: %s" % e)
                
        # cleanup test context
        self.cleanupTestContext(testUuid, scriptId, adapterId)
         
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
                    ctx_test.ctx_plugin = SockTcpThread(parent=self, request=request, sshlib=paramiko)
                ctx_test.putItem( lambda: self.execAction(client, tid, request) )
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()