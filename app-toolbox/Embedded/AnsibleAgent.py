#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2018 Denis Barleben and Denys Bortovets
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
import json

import Core.GenericTool as GenericTool

# Ansible API
import sys
if sys.platform in ['linux', 'linux2']:
    from collections import namedtuple
    from ansible.parsing.dataloader import DataLoader
    from ansible.vars.manager import VariableManager
    from ansible.inventory.manager import InventoryManager
    from ansible.playbook.play import Play
    from ansible.executor.task_queue_manager import TaskQueueManager
    from ansible.plugins.callback.json import CallbackModule
    from ansible import constants as C


__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False
__APP_PATH__ = ""
__TYPE__ = """ansible"""
__RESUME__ = """This agent provides Ansible client functionality Can be used on Linux"""

__DESCRIPTION__ = """This agent enables to execute ansible playbooks on localhost and remotes machines"""


def initialize(controllerIp, controllerPort, toolName, toolDesc, defaultTool,
               supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Ansible(controllerIp, controllerPort, toolName, toolDesc, defaultTool,
                   supportProxy, proxyIp, proxyPort, sslSupport)


class Ansible(GenericTool.Tool):

    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool,
                 supportProxy=0, proxyIp=None, proxyPort=None, sslSupport=True):

        """
        Asible agent constructor
        :param controllerIp:
        :param controllerPort:
        :param toolName:
        :param toolDesc:
        :param defaultTool:
        :param supportProxy:
        :param proxyIp:
        :param proxyPort:
        :param sslSupport:
        """

        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName,
                                  toolDesc, defaultTool, supportProxy=supportProxy,
                                  proxyIp=proxyIp, proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__

        if sys.platform not in ['linux', 'linux2']:
            raise EnvironmentError("Only for Linux")

    def execAnsibleAction(self, request):
        """
        Execute action
        """

        params = request['data']['parameters']

        options_dict = params['options']

        Options = namedtuple('Options', options_dict.keys())

        options = Options(**options_dict)

        # initialize needed objects
        loader = DataLoader()

        play_source = loader.load(params['playbook'])

        passwords = dict(params.get('passwords', {}))

        # Instantiate our ResultCallback for handling results as they come in
        results_callback = CallbackModule()

        # create inventory and pass to var manager
        inventory = InventoryManager(loader=loader, sources=params.get('hosts'))
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        for c_name, c_value in params['constants'].items():
            C.set_constant(c_name, c_value)

        summary = {}

        try:
            for play_item in play_source:

                play = Play().load(play_item, variable_manager=variable_manager, loader=loader)

                # actually run it
                tqm = None
                try:
                    tqm = TaskQueueManager(
                        inventory=inventory,
                        variable_manager=variable_manager,
                        loader=loader,
                        options=options,
                        passwords=passwords,
                        stdout_callback=results_callback
                    )
                    tqm.run(play)
                finally:
                    if tqm is not None:
                        tqm.cleanup()

                hosts = sorted(tqm._stats.processed.keys())

                for h in hosts:
                    s = tqm._stats.summarize(h)

                    if s['unreachable'] > 0 or s['failures'] > 0:
                        raise AnsiblesCommandExecution

                    summary[h] = s

            self.sendNotify(request, data={'result': json.dumps(summary), 'get': request['data']['get']})
        except AnsiblesCommandExecution:
            self.sendError(request, data={'error': 'Wrong ansible response', 'get': request['data']['get']})
            self.sendNotify(request, data={'result': json.dumps({'error': results_callback.results}, sort_keys=True,
                                                                indent=4),
                                           'get': request['data']['get']})

    def onAgentNotify(self, client, tid, request):
        """
        Received a notify from server and dispatch it to the good socket
        """
        self.__mutex__.acquire()
        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                ctx_test = self.context()[request['uuid']][request['source-adapter']]
                ctx_test.putItem( lambda: self.execAnsibleAction(request))
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'],
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()

    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass

    def onToolLogWarningCalled(self, msg):
        """
        Function to reimplement
        """
        pass

    def onToolLogErrorCalled(self, msg):
        """
        Function to reimplement
        """
        pass

    def onToolLogSuccessCalled(self, msg):
        """
        Logs success on main application

        @param msg: error message
        @type msg: string
        """
        pass

    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        self.onToolLogWarningCalled("Starting socket agent")
        self.onToolLogWarningCalled("Socket agent started")
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

    def getType(self):
        """
        Return agent type
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all sockets, all threads
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
        Initialize a new socket the agent
        """
        pass

    def onAgentReset(self, client, tid, request):
        """
        On agent reset event
        """
        pass


class AnsiblesCommandExecution(Exception):
    pass
