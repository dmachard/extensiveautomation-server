#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

import threading

from ea.libs.NetLayerLib import ServerAgent as NetLayerLib
from ea.libs import Logger, Settings
from ea.serverengine import (ProjectsManager)


class EventServerInterface(Logger.ClassLogger, NetLayerLib.ServerAgent):
    def __init__(self, listeningAddress, agentName='ESI',
                 sslSupport=False, wsSupport=False, context=None):
        """Event server interface"""
        NetLayerLib.ServerAgent.__init__(self, listeningAddress=listeningAddress, agentName=agentName,
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
                                                             Settings.get('Client_Channel', 'channel-ssl-cert')),
                                         keyFile='%s/%s' % (Settings.getDirExec(),
                                                            Settings.get('Client_Channel', 'channel-ssl-key')),
                                         pickleVer=Settings.getInt(
                                             'Network', 'pickle-version')
                                         )
        self.__mutex__ = threading.RLock()
        self.context = context

    def onWsHanshakeSuccess(self, clientId, publicIp):
        """Called on ws handshake successful"""
        self.trace(
            "WS handshake successful for privateip=%s publicip=%s" %
            (str(clientId), publicIp))

        client = self.clients[clientId]
        self.trace('ws sending notify to channel id: %s' %
                   str(client.client_address))
        body = ('reg', {'channel-id': client.client_address,
                        'session-id': '', 'public-ip': publicIp})
        NetLayerLib.ServerAgent.notify(
            self, client=client.client_address, data=body)

    def onConnection(self, client):
        """Called on connection"""
        self.trace("New connection Client=%s" % str(client.client_address))

        NetLayerLib.ServerAgent.onConnection(self, client)
        if not self.wsSupport:
            self.trace('sending notify to channel id: %s' %
                       str(client.client_address))
            body = (
                'reg', {
                    'channel-id': client.client_address, 'session-id': ''})
            NetLayerLib.ServerAgent.notify(
                self, client=client.client_address, data=body)

    def onDisconnection(self, client):
        """Called on disconnection"""
        self.trace("Disconnection Client=%s" % str(client.client_address))

        NetLayerLib.ServerAgent.onDisconnection(self, client)
        self.__mutex__.acquire()
        if self.context is not None:
            self.context.unregisterUser(user=client.client_address)
        self.__mutex__.release()

    def notify(self, body, toUser=None, toAddress=None):
        """Notify a specific connected user"""
        if toAddress is not None:
            self.trace('Sending notify Client=%s' % toAddress)
            NetLayerLib.ServerAgent.notify(
                self, client=tuple(toAddress), data=body)
            return

        if toUser is not None:
            from_user = toUser
        else:
            from_user = body[1]['from']

        self.trace('Sending notify User=%s' % from_user)
        connected = self.context.getUsersConnectedCopy()
        if from_user in connected:
            NetLayerLib.ServerAgent.notify(self,
                                           client=connected[from_user]['address'],
                                           data=body)
        del connected

    def interact(self, body, timeout=0.0):
        """Command a specific connected user"""
        to_user = body['from']
        self.trace('Sending command User=%s' % to_user)

        # search user
        destUser = None
        rsp = None
        connected = self.context.getUsersConnectedCopy()
        if to_user in connected:
            destUser = connected[to_user]

        if destUser is None:
            self.trace('user not found: %s' % to_user)
        else:
            rsp = NetLayerLib.ServerAgent.cmd(self, client=destUser['address'], data=body,
                                              timeout=timeout)
        # cleanup
        del connected
        return rsp

    def notifyAll(self, body):
        """Notify all connected users"""
        self.trace('Sending notify to all users')

        connected = self.context.getUsersConnectedCopy()
        for cur_user in connected:
            NetLayerLib.ServerAgent.notify(self,
                                           client=connected[cur_user]['address'],
                                           data=body)
        del connected

    def notifyByUserAndProject(
            self, body, admin=False, monitor=False, tester=False, projectId=1):
        """
        """
        self.trace('Sending notify to admin=%s, monitor=%s, tester=%s' % (admin,
                                                                          monitor,
                                                                          tester))
        connected = self.context.getUsersConnectedCopy()
        for cur_user in connected:
            # An user can have multiple right so this variable is here to avoid
            # multiple notify
            toNotify = False

            # Check the type of user to notify
            if admin and connected[cur_user]['profile']['administrator']:
                toNotify = True
            if monitor and connected[cur_user]['profile']['monitor']:
                toNotify = True
            if tester and connected[cur_user]['profile']['tester']:
                toNotify = True

            # Finaly notify the user of not
            if toNotify:
                projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=cur_user,
                                                                                          projectId=projectId)
                self.trace("project is authorized ? %s" % projectAuthorized)
                if projectAuthorized:
                    NetLayerLib.ServerAgent.notify(self,
                                                   client=connected[cur_user]['address'],
                                                   data=body)
        del connected

    def notifyByUserTypes(self, body, admin=False,
                          monitor=False, tester=False):
        """Notify users by type"""
        self.trace('Sending notify to admin=%s, monitor=%s, tester=%s' % (admin,
                                                                          monitor,
                                                                          tester))

        connected = self.context.getUsersConnectedCopy()
        for cur_user in connected:
            # An user can have multiple right so this variable is here to avoid
            # multiple notify
            toNotify = False

            # Check the type of user to notify
            if admin and connected[cur_user]['profile']['administrator']:
                toNotify = True
            if monitor and connected[cur_user]['profile']['monitor']:
                toNotify = True
            if tester and connected[cur_user]['profile']['tester']:
                toNotify = True

            # Finaly notify the user of not
            if toNotify:
                NetLayerLib.ServerAgent.notify(self, client=connected[cur_user]['address'],
                                               data=body)
        del connected

    def notifyAllAdmins(self, body):
        """Notify all admin users"""
        self.notifyByUserTypes(body=body, admin=True)

    def notifyAllMonitors(self, body):
        """Notify all admin managers"""
        self.notifyByUserTypes(body=body, monitor=True)

    def notifyAllTesters(self, body):
        """Notify all admin testers"""
        self.notifyByUserTypes(body=body, tester=True)

    def trace(self, txt):
        """Trace message"""
        if Settings.instance() is not None:
            if Settings.get('Trace', 'debug-level') == 'VERBOSE':
                Logger.ClassLogger.trace(self, txt=txt)


ESI = None  # singleton


def instance():
    """Returns the singleton"""
    return ESI


def initialize(*args, **kwargs):
    """Instance creation"""
    global ESI
    ESI = EventServerInterface(*args, **kwargs)


def finalize():
    """Destruction of the singleton"""
    global ESI
    if ESI:
        ESI.stopSA()
        ESI = None
