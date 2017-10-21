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

import Libs.NetLayerLib.ServerAgent as NetLayerLib
import Libs.NetLayerLib.Messages as Messages
import Libs.NetLayerLib.ClientAgent as ClientAgent
import EventServerInterface as ESI
import RepoArchives
import Context

from Libs import Settings, Logger

import threading
import shutil
import os

class ProbeServerInterface(Logger.ClassLogger, NetLayerLib.ServerAgent):
    def __init__ (self, listeningAddress, agentName = 'PSI', sslSupport=False, wsSupport=False):
        """
        Construct Probe Server Interface

        @param listeningAddress:
        @type listeningAddress:

        @param agentName:
        @type agentName: string
        """
        NetLayerLib.ServerAgent.__init__(self, listeningAddress = listeningAddress, agentName = agentName,
                                            keepAliveInterval= Settings.getInt('Network', 'keepalive-interval' ), 
                                            inactivityTimeout=Settings.getInt( 'Network', 'inactivity-timeout' ),
                                            responseTimeout=Settings.getInt( 'Network', 'response-timeout' ),
                                            selectTimeout=Settings.get( 'Network', 'select-timeout' ),
                                            sslSupport=sslSupport,
                                            wsSupport=wsSupport,
                                            certFile='%s/%s' % (Settings.getDirExec(),Settings.get( 'Probe_Channel', 'channel-ssl-cert' )), 
                                            keyFile='%s/%s' % (Settings.getDirExec(),Settings.get( 'Probe_Channel', 'channel-ssl-key' )),
                                            pickleVer=Settings.getInt( 'Network', 'pickle-version' )
                                        )
        self.__mutex = threading.RLock()
        self.probesRegistered = {}
        self.probesPublicIp = {}

    def onWsHanshakeSuccess(self, clientId, publicIp):
        """
        Called on ws handshake successful
        """
        self.trace("ws hanshake success: %s" % str(clientId) )
        # save public ip
        self.probesPublicIp[clientId] = publicIp

    def getProbe(self, pname):
        """
        Search and return a specific probe by the name

        @type  pname:
        @param pname:

        @return:
        @rtype:
        """
        self.trace(" get probe" )
        ret = None
        if pname in self.probesRegistered:
            return self.probesRegistered[pname]
        return ret

    def getProbes (self):
        """
        Returns all registered probes

        @return:
        @rtype: list
        """
        self.trace("get probes" )
        ret = []
        for k, c in self.probesRegistered.items():
            tpl = { 'id': k }
            tpl.update(c)
            ret.append( tpl )
        return ret

    def findProbe (self, cmd):
        """
        Find the probe 

        @param cmd:
        @type cmd:

        @return:
        @rtype: boolean
        """
        self.trace(" find the probe" )
        probeId = cmd['name']
        for k, c in self.probesRegistered.items():
            if probeId == k:
                return True
        return False

    def startProbe ( self, cmd):
        """
        Start the probe 

        @param cmd:
        @type cmd:

        @return:
        @rtype: boolean
        """
        self.trace(" start the probe" )
        ret = None
        try:
            probeId = cmd['name']
            tpl = { 'cmd': Messages.CMD_START_PROBE, 'opts': cmd }
            ret = NetLayerLib.ServerAgent.cmd(self, client = self.probesRegistered[probeId]['address'],
                                                    data = tpl )
            if ret is not None:
                ret = ret['body']
        except Exception as e:
            self.error( "unable to start probe %s" % e )
        return ret

    def onConnection (self, client):
        """
        Called on connection

        @param client:
        @type client:
        """
        self.trace("New connection from %s" % str(client.client_address) )
        NetLayerLib.ServerAgent.onConnection( self, client )

    def stopProbe ( self, cmd):
        """
        Stop the probe

        @param cmd:
        @type cmd:

        @return:
        @rtype: boolean
        """
        self.trace(" stop the probe" )
        ret = None
        try:
            probeId = cmd['name']
            tpl = { 'cmd': Messages.CMD_STOP_PROBE, 'opts': cmd  }
            ret = NetLayerLib.ServerAgent.cmd(self, client = self.probesRegistered[probeId]['address'],
                                                    data = tpl, timeout=10 )
            if ret is not None:
                ret = ret['body']
        except Exception as e:
            self.error( "unable to stop probe: %s" % e )
        return ret

    def onRequest(self, client, tid, request):
        """
        Reimplemented from ServerAgent

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        try:
            if request['cmd'] == Messages.RSQ_CMD:
            ############################################################
                body = request['body']
                if 'cmd' in body:
                    if body['cmd'] == Messages.CMD_HELLO:
                        self.trace( '<-- CMD HELLO: %s' % tid )
                        self.probeRegistration(client, tid, request)
                    else:
                        self.error( 'cmd unknown %s' % body['cmd'])
                        rsp = {'cmd': body['cmd'], 'res': Messages.CMD_ERROR }
                        NetLayerLib.ServerAgent.failed(self, client, tid, body = rsp )
                else:
                    self.error( 'cmd is missing')
            ############################################################
            elif request['cmd'] == Messages.RSQ_NOTIFY:
                self.trace( '<-- NOTIFY: %s' % tid )
                self.moveNewFile( data=request['body'] )
            ############################################################
            else:
                self.error( 'request unknown %s' % request['cmd'])
        except Exception as e:
            self.error( "unable to handle incoming request: %s" % e )

    def moveNewFile (self, data):
        """
        Move the file from the temp unix to the test result storage
        Deprecated function thanks to the migration to python3 on probe side
        
        @type  data:
        @param data:
        """
        self.trace(" moving file" )
        try:
            testResult = data['result-path']
            fileName = data['filename']
            self.trace( 'move %s to %s' % ( fileName, testResult ) )
            # move file 
            testsResultPath = '%s%s' % (    Settings.getDirExec(),Settings.get( 'Paths', 'testsresults' ) )
            
            shutil.copyfile(    src = '/tmp/%s' % fileName,
                                dst = '%s/%s/%s' % (testsResultPath, testResult, fileName)
                            )
        except Exception as e:
            self.error( "unable to move the new file: %s" % e )
        else:
            try:
                # now notify all connected users
                size_ = os.path.getsize( '%s/%s/%s' % (testsResultPath, testResult, fileName) )
                if testResult.startswith('/'):
                    testResult = testResult[1:]
                tmp = testResult.split('/', 1)
                projectId = tmp[0]
                tmp = tmp[1].split('/', 1)
                mainPathTozip= tmp[0]
                subPathTozip = tmp[1]
                if Settings.getInt( 'Notifications', 'archives'):
                    m = [   {   "type": "folder", "name": mainPathTozip, "project": "%s" % projectId,
                                "content": [ {  "type": "folder", "name": subPathTozip, "project": "%s" % projectId,
                                "content": [ { "project": "%s" % projectId, "type": "file", "name": fileName, 'size': str(size_) } ]} ] }  ]
                    notif = {}
                    notif['archive'] = m 
                    notif['stats-repo-archives'] = {    'nb-zip':1, 'nb-trx':0, 'nb-tot': 1,
                                                    'mb-used': RepoArchives.instance().getSizeRepo(folder=RepoArchives.instance().testsPath),
                                                    'mb-free': RepoArchives.instance().freeSpace(p=RepoArchives.instance().testsPath) }
                    data = ( 'archive', ( None, notif) )    
                    #ESI.instance().notifyByUserTypes(body = data, admin=True, leader=False, tester=True, developer=False)
                    ESI.instance().notifyByUserAndProject(body = data, admin=True, leader=False, tester=True, developer=False, projectId="%s" % projectId)
        
            except Exception as e:
                self.error( "unable to notify users for this new file: %s" % e )
        
        # clean temp dir
        try:
            os.remove( '/tmp/%s' % fileName )
        except Exception as e:
            pass

    def probeRegistration (self, client, tid, request):
        """
        Called on the registration of a new probes

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        self.trace(" on registration" )
        self.__mutex.acquire()
        doNotify=False
        if len(self.probesRegistered) >= Context.instance().getLicence()[ 'probes' ] [ 'instance' ]:
            self.info('license probes reached')
            NetLayerLib.ServerAgent.forbidden(self, client, tid)
        elif request['userid'] in  self.probesRegistered:
            self.info('duplicate probe registration: %s' % request['userid'] )
            NetLayerLib.ServerAgent.failed(self, client, tid)
        else:
            if not ('type' in request['body']):
                self.error('type missing in request: %s' % request['body'] )
                NetLayerLib.ServerAgent.failed(self, client, tid)
            else:
                if request['body']['type'] != ClientAgent.TYPE_AGENT_PROBE:
                    self.error('probe type refused: %s' % request['body']['type'])
                    NetLayerLib.ServerAgent.forbidden(self, client, tid)
                else:
                    tpl = { 'address' : client,
                            'version': request['body']['version'],
                            'description': request['body']['description']['details'],
                            'auto-startup': request['body']['description']['default'],
                            'type': request['body']['name'],
                            'start-at': request['body']['start-at'],
                            'publicip': self.probesPublicIp[client]
                            }
                    if not Settings.getInt( 'WebServices', 'remote-probes-enabled' ):
                        if not tpl['auto-startup']:
                            self.info('remote probes registration not authorized')
                            NetLayerLib.ServerAgent.forbidden(self, client, tid)
                        else:
                            self.probesRegistered[request['userid']] = tpl
                            NetLayerLib.ServerAgent.ok(self, client, tid)
                            self.trace( 'Local probe registered: Name="%s"' % request['userid'] )
                            doNotify = True
                    else:
                        self.probesRegistered[request['userid']] = tpl
                        NetLayerLib.ServerAgent.ok(self, client, tid)
                        self.info( 'Remote probe registered: Name="%s"' % request['userid'] )
                        doNotify = True
        if doNotify:
            # Notify all connected users
            notif = ( 'probes', ( 'add', self.getProbes() ) )
            ESI.instance().notifyByUserTypes(body = notif, admin=True, leader=False, tester=True, developer=False)
        self.__mutex.release()

    def onDisconnection (self, client):
        """
        Reimplemented from ServerAgent

        @type  client:
        @param client:
        """
        self.trace(" on disconnection" )
        NetLayerLib.ServerAgent.onDisconnection(self, client)
        clientRegistered = self.probesRegistered.items()
        for k, c in clientRegistered:
            if c['address'] == client.client_address:
                ret = self.probesRegistered.pop(k)
                publicip = self.probesPublicIp.pop(c['address'])
                del publicip
                self.info( 'Probe unregistered: Name="%s"' % k )
                notif = ( 'probes', ( 'del', self.getProbes() ) )
                ESI.instance().notifyByUserTypes(body = notif, admin=True, leader=False, tester=True, developer=False)
                del ret
                break

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="PSI - %s" % txt)

#############
PSI = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return PSI

def initialize (listeningAddress, sslSupport, wsSupport):
    """
    Instance creation

    @param listeningAddress:
    @type listeningAddress:
    """
    global PSI
    PSI = ProbeServerInterface( listeningAddress = listeningAddress, sslSupport=sslSupport, wsSupport=wsSupport)

def finalize ():
    """
    Destruction of the singleton
    """
    global PSI
    if PSI:
        PSI = None