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
import time

from ea.libs.NetLayerLib import ServerAgent as NetLayerLib
from ea.libs.NetLayerLib import Messages as Messages
from ea.libs.NetLayerLib import FifoCallBack as FifoCallBack
from ea.serverinterfaces import EventServerInterface as ESI
from ea.serverinterfaces import AgentServerInterface as ASI
from ea.libs import Logger, Settings


class TestServerInterface(Logger.ClassLogger, NetLayerLib.ServerAgent):
    def __init__(self, listeningAddress, agentName='TSI', context=None):
        """
        Constructs TCP Server Inferface

        @param listeningAddress:
        @type listeningAddress:
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
                                         pickleVer=Settings.getInt(
                                             'Network', 'pickle-version')
                                         )
        self.context = context

        self.__mutex__ = threading.RLock()
        self.__fifoThread = None

        self.tests = {}  # {'task-id': Boolean} # test register,  with background running or not
        self.testsConnected = {}  # all tests connected

    def startFifo(self):
        """
        Start the fifo
        """
        self.__fifoThread = FifoCallBack.FifoCallbackThread()
        self.__fifoThread.start()
        self.trace("TSI: fifo started.")

    def stopFifo(self):
        """
        Stop the fifo
        """
        self.__fifoThread.stop()
        self.__fifoThread.join()
        self.trace("TSI: fifo stopped.")

    def registerTest(self, id, background):
        """
        Register the test on the server

        @param id:
        @type id:

        @param background:
        @type background: boolean
        """
        try:
            self.tests[str(id)] = bool(background)
            self.trace(
                'Test=%s registered, running in Background=%s' %
                (id, background))
        except Exception as e:
            self.error(err=e)
            return False
        return True

    def onConnection(self, client):
        """
        Called on connection of the test

        @param client:
        @type client:
        """
        NetLayerLib.ServerAgent.onConnection(self, client)
        self.testsConnected[client.client_address] = {'connected-at': time.time(),
                                                      'probes': [], 'agents': []}
        self.trace('test is starting: %s' % str(client.client_address))

    def onDisconnection(self, client):
        """
        Called on disconnection of test

        @param client:
        @type client:
        """
        NetLayerLib.ServerAgent.onDisconnection(self, client)
        self.trace('test is endding: %s' % str(client.client_address))

    def resetRunningAgent(self, client):
        """
        Reset all running agents used by the client passed as argument

        @param client:
        @type client:
        """
        self.trace('Trying to cleanup active agents')
        for p in client['agents']:
            # we can reset only agent in ready state (ready message received)
            if 'agent-name' in p:
                agent = ASI.instance().getAgent(aname=p['agent-name'])
                if agent is not None:
                    self.trace('Reset Agent=%s for Script=%s and Adapter=%s' % (p['agent-name'],
                                                                                p['script-id'],
                                                                                p['source-adapter']))
                    data = {'event': 'agent-reset', 'script_id': p['script-id'],
                            'source-adapter': p['source-adapter'], 'uuid': p['uuid']}
                    ASI.instance().notify(client=agent['address'], data=data)

    def onRequest(self, client, tid, request):
        """
        Reimplemented from ServerAgent
        Called on incoming request

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        self.__mutex__.acquire()
        try:
            _body_ = request['body']

            if client not in self.testsConnected:
                self.__mutex__.release()
                return

            self.testsConnected[client]['task-id'] = _body_['task-id']

            # handle notify and save some statistics on the database
            if request['cmd'] == Messages.RSQ_NOTIFY:
                try:
                    if _body_['event'] in ['agent-data', 'agent-notify', 'agent-init',
                                           'agent-reset', 'agent-alive', 'agent-ready']:

                        if _body_['event'] == 'agent-ready':
                            self.testsConnected[client]['agents'].append(
                                {
                                    'agent-name': _body_['destination-agent'],
                                    'script-id': _body_['script_id'],
                                    'uuid': _body_['uuid'],
                                    'source-adapter': _body_['source-adapter']
                                }
                            )

                        ASI.instance().notifyAgent(client, tid, data=_body_)
                except Exception as e:
                    self.error('unable to handle notify for agent: %s' % e)

                if _body_['event'] == 'testcase-stopped':
                    # reset agents
                    self.resetRunningAgent(client=self.testsConnected[client])

                if _body_['task-id'] in self.tests:
                    if not self.tests[_body_['task-id']]:
                        # check connected time of the associated user and  test
                        # if connected-at of the user > connected-at of the test
                        # then not necessary to send events
                        userFounded = self.context.getUser(
                            login=_body_['from'])
                        if userFounded is not None:
                            if client not in self.testsConnected:
                                self.error(
                                    'unknown test from %s' % str(client))
                            else:
                                if userFounded['connected-at'] < self.testsConnected[client]['connected-at']:
                                    if _body_['channel-id']:
                                        ESI.instance().notify(body=('event', _body_),
                                                              toAddress=_body_['channel-id'])
                                    else:
                                        ESI.instance().notify(body=('event', _body_))
                else:
                    self.error('test unknown: %s' % _body_['task-id'])

                if _body_['event'] == 'script-stopped':
                    # reset agents
                    self.resetRunningAgent(client=self.testsConnected[client])

                    if _body_['task-id'] in self.tests:
                        self.tests.pop(_body_['task-id'])
                    else:
                        self.error('task-id unknown: %s' % _body_['task-id'])
                    if client in self.testsConnected:
                        self.testsConnected.pop(client)
                    else:
                        self.error('test unknown: %s' % str(client))

            # handle requests
            elif request['cmd'] == Messages.RSQ_CMD:
                self.trace("cmd received: %s" % _body_['cmd'])
                if 'cmd' in _body_:
                    # handle interact command
                    if _body_['cmd'] == Messages.CMD_INTERACT:
                        self.trace('interact called')
                        if _body_['task-id'] in self.tests:
                            if not self.tests[_body_['task-id']]:
                                # check connected time of the associated user and  test
                                # if connected-at of the user > connected-at of
                                # the test then not necessary to send events
                                userFounded = self.context.getUser(
                                    login=_body_['from'])
                                if userFounded is not None:
                                    if client not in self.testsConnected:
                                        self.error(
                                            'unknown test from %s' %
                                            str(client))
                                    else:
                                        if userFounded['connected-at'] < self.testsConnected[client]['connected-at']:
                                            self.__fifoThread.putItem(lambda: self.onInteract(client, tid,
                                                                                              bodyReq=_body_,
                                                                                              timeout=_body_['timeout']))
                        else:
                            self.error('test unknown: %s' % _body_['task-id'])

                    else:
                        self.error('cmd unknown %s' % _body_['cmd'])
                        rsp = {'cmd': _body_['cmd'], 'res': Messages.CMD_ERROR}
                        NetLayerLib.ServerAgent.failed(
                            self, client, tid, body=rsp)
                else:
                    self.error('cmd is missing')

            # handle other request
            else:
                self.trace('%s received ' % request['cmd'])
        except Exception as e:
            self.error("unable to handle incoming request: %s" % e)
        self.__mutex__.release()

    def onInteract(self, client, tid, bodyReq, timeout=0.0):
        """
        Called on interact
        """
        inter = Interact(client, tid, bodyReq, timeout=timeout)
        testThread = threading.Thread(target=lambda: inter.run())
        testThread.start()

    def trace(self, txt):
        """
        Trace message
        """
        if Settings.instance() is not None:
            if Settings.get('Trace', 'debug-level') == 'VERBOSE':
                Logger.ClassLogger.trace(self, txt=txt)


class Interact(object):
    def __init__(self, client, tid, bodyReq, timeout=0.0):
        """
        Interact object, not blocking
        """
        self.client = client
        self.tid = tid
        self.bodyReq = bodyReq
        self.timeout = timeout

    def run(self):
        """
        On run
        """
        rsp = ESI.instance().interact(body=self.bodyReq, timeout=self.timeout)

        _data_ = {'cmd': Messages.CMD_INTERACT}
        if rsp is None:
            _data_['rsp'] = None
        else:
            _data_['rsp'] = rsp['body']

        instance().ok(self.client, self.tid, body=_data_)


TSI = None


def instance():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return TSI


def initialize(listeningAddress, context):
    """
    Instance creation

    @param listeningAddress:
    @type listeningAddress:
    """
    global TSI
    TSI = TestServerInterface(listeningAddress=listeningAddress,
                              context=context)
    TSI.startFifo()


def finalize():
    """
    Destruction of the singleton
    """
    global TSI
    if TSI:
        TSI.stopFifo()
        TSI.stopSA()
        TSI = None
