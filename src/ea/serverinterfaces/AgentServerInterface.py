#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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

import threading
import sys

from ea.serverinterfaces import EventServerInterface as ESI
from ea.libs.NetLayerLib import ServerAgent as NetLayerLib
from ea.libs.NetLayerLib import Messages as Messages
from ea.libs.NetLayerLib import ClientAgent as ClientAgent
from ea.libs import Settings, Logger


class AgentServerInterface(Logger.ClassLogger, NetLayerLib.ServerAgent):
    def __init__(self, listeningAddress, agentName='ASI', sslSupport=False,
                 wsSupport=False, tsi=None, context=None):
        """
        Construct Agent Server Interface

        @param listeningAddress:
        @type listeningAddress:

        @param agentName:
        @type agentName: string
        """
        NetLayerLib.ServerAgent.__init__(self, listeningAddress=listeningAddress,
                                         agentName=agentName,
                                         keepAliveInterval=Settings.getInt(
                                             'Network', 'keepalive-interval'),
                                         inactivityTimeout=Settings.getInt(
                                             'Network', 'inactivity-timeout'),
                                         responseTimeout=Settings.getInt(
                                             'Network', 'response-timeout'),
                                         selectTimeout=Settings.get(
                                             'Network', 'select-timeout'),
                                         sslSupport=sslSupport,
                                         wsSupport=wsSupport,
                                         certFile='%s/%s' % (Settings.getDirExec(),
                                                             Settings.get('Agent_Channel', 'channel-ssl-cert')),
                                         keyFile='%s/%s' % (Settings.getDirExec(),
                                                            Settings.get('Agent_Channel', 'channel-ssl-key')),
                                         pickleVer=Settings.getInt(
                                             'Network', 'pickle-version')
                                         )
        self.tsi = tsi
        self.context = context

        self.__mutex = threading.RLock()
        self.__mutexNotif = threading.RLock()
        self.agentsRegistered = {}
        self.agentsPublicIp = {}

    def onWsHanshakeSuccess(self, clientId, publicIp):
        """
        Called on ws handshake successful
        """
        self.trace("ws hanshake success: %s" % str(clientId))
        # save public ip
        self.agentsPublicIp[clientId] = publicIp

    def getAgent(self, aname):
        """
        Search and return a specific agent by the name

        @type  pname:
        @param pname:

        @return:
        @rtype:
        """
        self.trace("search and get agent=%s" % aname)
        ret = None
        if aname in self.agentsRegistered:
            return self.agentsRegistered[aname]
        return ret

    def getAgents(self):
        """
        Returns all registered agents

        @return:
        @rtype: list
        """
        self.trace("get agents")
        ret = []
        for k, c in self.agentsRegistered.items():
            tpl = {'id': k}
            tpl.update(c)
            ret.append(tpl)
        return ret

    def notifyAgent(self, client, tid, data):
        """
        Notify agent
        """
        try:
            agentName = data['destination-agent']
            agent = self.getAgent(aname=agentName)
            if agent is None:
                data['event'] = 'agent-system-error'
                self.tsi.notify(client=client, data=data)
            else:
                NetLayerLib.ServerAgent.notify(
                    self, client=agent['address'], data=data)
        except Exception as e:
            self.error("unable to notify agent: %s" % str(e))

    def onConnection(self, client):
        """
        Called on connection

        @param client:
        @type client:
        """
        self.trace("New connection from %s" % str(client.client_address))
        NetLayerLib.ServerAgent.onConnection(self, client)

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
            # handle register request
            if request['cmd'] == Messages.RSQ_CMD:
                body = request['body']
                if 'cmd' in body:
                    if body['cmd'] == Messages.CMD_HELLO:
                        self.trace('ASI <-- CMD HELLO: %s' % tid)
                        self.onRegistration(client, tid, request)
                    else:
                        self.error('cmd unknown %s' % body['cmd'])
                        rsp = {'cmd': body['cmd'], 'res': Messages.CMD_ERROR}
                        NetLayerLib.ServerAgent.failed(
                            self, client, tid, body=rsp)
                else:
                    self.error('cmd is missing')

            # handle notify
            elif request['cmd'] == Messages.RSQ_NOTIFY:
                self.trace(
                    "notify %s received from agent of size: %s" %
                    (tid, len(
                        request['body'])))
                self.onNotify(client, tid, request=request['body'])

            # unknown errors
            else:
                self.error('request unknown %s' % request['cmd'])
        except Exception as e:
            self.error("unable to handle incoming request: %s" % e)

    def onNotify(self, client, tid, request):
        """
        Called on notify
        """
        self.__mutexNotif.acquire()
        try:
            self.tsi.notify(client=request["from-src"], data=request)
        except Exception as e:
            self.error('unable to handle notify: %s' % str(e))
        self.__mutexNotif.release()

    def onRegistration(self, client, tid, request):
        """
        Called on the registration of a new agents

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        self.trace("on registration")
        self.__mutex.acquire()
        doNotify = False

        if sys.version_info > (3,):
            request['userid'] = request['userid'].decode("utf8")

        if request['userid'] in self.agentsRegistered:
            self.info('duplicate agents registration: %s' % request['userid'])
            NetLayerLib.ServerAgent.failed(self, client, tid)
        else:
            if not ('type' in request['body']):
                self.error('type missing in request: %s' % request['body'])
                NetLayerLib.ServerAgent.failed(self, client, tid)
            else:
                if request['body']['type'] != ClientAgent.TYPE_AGENT_AGENT:
                    self.error(
                        'agent type refused: %s' %
                        request['body']['type'])
                    NetLayerLib.ServerAgent.forbidden(self, client, tid)
                else:
                    tpl = {'address': client,
                           'version': request['body']['version'],
                           'description': request['body']['description']['details'],
                           'auto-startup': request['body']['description']['default'],
                           'type': request['body']['name'],
                           'start-at': request['body']['start-at'],
                           'publicip': self.agentsPublicIp[client]
                           }

                    self.agentsRegistered[request['userid']] = tpl
                    NetLayerLib.ServerAgent.ok(self, client, tid)
                    self.info(
                        'Remote agent registered: Name="%s"' %
                        request['userid'])
                    doNotify = True

        if doNotify:
            # Notify all connected users
            notif = ('agents', ('add', self.getAgents()))
            ESI.instance().notifyByUserTypes(body=notif,
                                             admin=True,
                                             monitor=False,
                                             tester=True)
        self.__mutex.release()

    def onDisconnection(self, client):
        """
        Reimplemented from ServerAgent

        @type  client:
        @param client:
        """
        self.trace("on disconnection")
        NetLayerLib.ServerAgent.onDisconnection(self, client)
        clientRegistered = self.agentsRegistered.items()
        for k, c in clientRegistered:
            if c['address'] == client.client_address:
                self.agentsRegistered.pop(k)
                self.agentsPublicIp.pop(c['address'])

                self.info('Agent unregistered: Name="%s"' % k)
                notif = ('agents', ('del', self.getAgents()))
                ESI.instance().notifyByUserTypes(body=notif,
                                                 admin=True,
                                                 monitor=False,
                                                 tester=True)
                break

    def trace(self, txt):
        """
        Trace message
        """
        if Settings.instance() is not None:
            if Settings.get('Trace', 'debug-level') == 'VERBOSE':
                Logger.ClassLogger.trace(self, txt=txt)


ASI = None


def instance():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return ASI


def initialize(listeningAddress, sslSupport, wsSupport, tsi, context):
    """
    Instance creation

    @param listeningAddress:
    @type listeningAddress:
    """
    global ASI
    ASI = AgentServerInterface(listeningAddress=listeningAddress,
                               sslSupport=sslSupport, wsSupport=wsSupport,
                               tsi=tsi, context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global ASI
    if ASI:
        ASI.stopSA()
        ASI = None
