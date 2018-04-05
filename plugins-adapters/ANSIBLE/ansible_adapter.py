# !/usr/bin/env python
# -*- coding=utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2017-2018 Denys Bortovets and Denis Barleben
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

import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
from TestExecutorLib.TestExecutorLib import doc_public

import templates
import yaml

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml


class AnsibleAdapter(TestAdapterLib.Adapter):
    __NAME__ = """ANSIBLE"""
    AGENT_INITIALIZED = "AGENT_INITIALIZED"
    AGENT_TYPE_EXPECTED = 'ansible'

    @doc_public
    def __init__(self, parent, host_group, agent, ssh_user=None, ssh_pass=None,
                 name=None, debug=False, shared=False, constants=None,
                 options=None, host_fqdns="None", host_py='python',
                 agentSupport=True, logEventReceived=True, timeout=10.0):
        """
          My adapter

          @param parent: parent testcase
          @type parent: testcase

          @param name: adapter name used with from origin/to destination (default=None)
          @type name: string/none

          @param debug: active debug mode (default=False)
          @type debug:	boolean

          @param shared: shared adapter (default=False)
          @type shared:	boolean

          @param agentSupport: agent support (default=False)
          @type agentSupport: boolean

          @param agent: agent to use (default=None)
          @type agent: string/none

          @param logEventReceived: default = True
          @type logEventReceived: boolean

          @param ssh_user: ssh user name
          @type ssh_user: string/dict/None

          @param ssh_pass: ssh user password
          @type ssh_pass: string/dict/None

          @param host_group: group for task
          @type host_group: string

          @param options: default ﻿{
                                     "connection": "local",
                                     "module_path": "~/",
                                     "forks": 100,
                                     "become": "yes",
                                     "become_method": "sudo",
                                     "become_user": "root",
                                     "check": false,
                                     "diff": false
                                   }
          @type options: dict/None

          @param constants:
          @type constants: dict/None

          @param host_fqdns: For hosts machines dict or string as json where keys should be ansible_host. For localhost playbook just "None"
          @type host_fqdns: dict/String

          @param host_py: path to python interpreter default for Linux python for Freebsd ﻿/usr/local/bin/python2
          @type host_py: string

          """
        # check the agent
        if agentSupport and agent is None:
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent cannot be undefined!")
        if agentSupport:
            if not isinstance(agent, dict):
                raise TestAdapterLib.ValueException(TestAdapterLib.caller(),
                                                    "agent argument is not a dict (%s)" % type(agent))
            if not len(agent['name']):
                raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty")
            if unicode(agent['type']) != unicode(self.AGENT_TYPE_EXPECTED):
                raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (
                    agent['type'], unicode(self.AGENT_TYPE_EXPECTED)))

        TestAdapterLib.Adapter.__init__(self, name=self.__NAME__, parent=parent, debug=debug, realname=name,
                                        agentSupport=agentSupport, agent=agent, shared=shared)
        self.parent = parent
        self.codecX2D = Xml2Dict.Xml2Dict()
        self.codecD2X = Dict2Xml.Dict2Xml(coding=None)
        self.logEventReceived = logEventReceived
        self.cfg = {}

        self.cfg['agent-support'] = True
        self.cfg['agent'] = agent
        self.cfg['agent-name'] = agent['name']

        # Ansible parameters
        self.host_group = host_group
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass

        self.host_fqdns = host_fqdns if isinstance(host_fqdns, dict) else yaml.load(host_fqdns)
        self.host_py = host_py
        self.constants = constants if constants else {"HOST_KEY_CHECKING": False}
        self.options = options if options else {"connection": "local",
                                                "module_path": "~/",
                                                "forks": 100,
                                                "become": "yes",
                                                "become_method": "sudo",
                                                "become_user": "root",
                                                "check": False,
                                                "diff": False}

        # initialize the agent with no data

        self.prepareAgent(data={'shared': shared})
        if self.agentIsReady(timeout=timeout) is None:
            raise TestAdapterLib.ValueException(TestAdapterLib.caller(),
                                                "Agent %s is not ready" % self.cfg['agent-name'])

        self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent",
                                                    callback=self.aliveAgent,
                                                    logEvent=False, enabled=True)

        self.cfg['agent']['type'] = 'ansible'

        self.configs = {}
        self.services = {}

        self.TIMER_ALIVE_AGT.start()

    @property
    def host_tasks(self):
        """
        prepares dictionary for continue working with yaml
        """
        host_tasks = []
        for host in self.host_fqdns:
            task = {
                'name': 'Add host %s' % host,
                'local_action': {
                    'module': 'add_host',
                    'hostname': host,
                    'ansible_connection': 'ssh',
                    'ansible_user': self.ssh_user[host] if isinstance(self.ssh_user, dict) else self.ssh_user,
                    'ansible_host': self.host_fqdns[host],
                    'ansible_ssh_pass': self.ssh_pass[host] if isinstance(self.ssh_pass, dict) else self.ssh_pass,
                    'ansible_python_interpreter': self.host_py,
                    'group': self.host_group

                }
            }
            host_tasks.append(task)

        return host_tasks

    def create_playbook(self, play):
        """
        This method prepares playbook for ansible
        ﻿---
        - hosts: localhost
          gather_facts: no
          tasks:
            self.host_tasks

        - hosts: self.host_group
          become: yes
          gather_facts: no
          tasks:
            play

        :return yaml string
        """
        loaded_play = yaml.load(play)
        if isinstance(loaded_play, list):
            play = loaded_play
        elif isinstance(loaded_play, dict):
            play = [loaded_play]
        else:
            raise ValueError('play has to be dict or list after loading from yaml')

        if self.host_group not in ['localhost', '127.0.0.1']:
            playbook_template = [
                {
                    'hosts': 'localhost',
                    'gather_facts': False,
                    'tasks': self.host_tasks
                },
                {
                    'hosts': self.host_group,
                    'become': True,
                    'gather_facts': False,
                    'tasks': play
                }
            ]
        else:
            playbook_template = [
                {
                    'hosts': 'localhost',
                    'gather_facts': False,
                    'tasks': play
                }
            ]

        playbook = yaml.dump(playbook_template, default_flow_style=False)
        self.info('playbook:\n%s' % playbook, raw=True)
        return playbook

    @doc_public
    def doAnsibleCmd(self, options=None, constants=None, play=None, passwords={}):
        """

        @param options:
        @type options: dict

        @param constants:
        @type constants: dict

        @param play:
        @type play: string/custom

        @param passwords:
        @type passwords: dict
        :return:
        """

        options = self.options if not options else self.options.update(options)
        constants = self.constants.update(constants) if constants else self.constants

        playbook = self.create_playbook(play=play)

        return self.execRequest(apiMethod='ansible_cmd',
                                parameters={'options': options, 'constants': constants,
                                            'playbook': playbook, 'passwords': passwords},
                                agentType='ansible')

    def __checkConfig(self):
        """
          Private function
          """
        self.debug("config: %s" % self.cfg)
        if self.cfg['agent-support']:
            self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']))

    def onReset(self):
        """
        Called automaticly on reset adapter
        """
        # stop timer
        self.TIMER_ALIVE_AGT.stop()

        # cleanup remote agent
        self.resetAgent()

    def receivedNotifyFromAgent(self, data):
        if 'cmd' in data:
            if data['cmd'] == self.AGENT_INITIALIZED:
                tpl = TestTemplatesLib.TemplateMessage()
                layer = TestTemplatesLib.TemplateLayer('AGENT')
                layer.addKey("ready", True)
                layer.addKey(name='name', data=self.cfg['agent']['name'])
                layer.addKey(name='type', data=self.cfg['agent']['type'])
                tpl.addLayer(layer=layer)
                self.logRecvEvent(shortEvt="Agent Is Ready", tplEvt=tpl)
        else:
            try:
                raw = data['result']
                self.debug(str(raw))
                if self.logEventReceived:
                    tplAnsible = TestTemplatesLib.TemplateLayer(name=self.__NAME__)
                    tplAnsible.addRaw(raw)
                    tplAnsible.addKey(name='event', data='response')
                    tplAnsible.addKey(name='get', data=data['get'])

                    if isinstance(raw, dict):
                        tplResult = TestTemplatesLib.TemplateLayer(name='result')
                        tplResult.addMore(raw)
                        tplResult.addRaw(raw)
                        tplAnsible.addKey(name='result', data=tplResult)
                    else:
                        tplAnsible.addKey(name='result', data=str(raw))

                    tpl = self.encapsule(kate_event=tplAnsible)
                    tpl.addRaw(str(raw))
                    self.logRecvEvent(shortEvt="%s Response" % data['get'], tplEvt=tpl)
            except Exception as e:
                self.error('unable to read response: %s. Data: %s' % (str(e), raw))

    def receivedErrorFromAgent(self, data):
        """
        Function to reimplement
        """
        self.error('Error received from agent: %s' % data)

    def receivedDataFromAgent(self, data):
        """
        Function to reimplement
        """
        self.info('Data received from agent: %s' % data)

    def prepareAgent(self, data):
        """
        Prepare agent
        """
        self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)

    def initAgent(self, data):
        """
        Init agent
        """
        self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)

    def resetAgent(self):
        """
        Reset agent
        """
        self.parent.sendResetToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData='')

    def aliveAgent(self):
        """
        Keep alive agent
        """
        self.parent.sendAliveToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData='')
        self.TIMER_ALIVE_AGT.restart()

    def sendInitToAgent(self, data):
        """
        """
        self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)

    def sendNotifyToAgent(self, data, agentType=None):
        """
        """
        self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data,
                                      agentType=agentType)

    def sendResetToAgent(self, data):
        """
        """
        self.parent.sendResetToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)

    def agentIsReady(self, timeout=1.0):
        """
        Waits to receive "agent ready" event until the end of the timeout

        @param timeout: time max to wait to receive event in second (default=1s)
        @type timeout: float

        @return: an event matching with the template or None otherwise
        @rtype: templatemessage
        """
        tpl = TestTemplatesLib.TemplateMessage()
        layer = TestTemplatesLib.TemplateLayer('AGENT')
        layer.addKey("ready", True)
        layer.addKey(name='name', data=self.cfg['agent']['name'])
        layer.addKey(name='type', data=self.cfg['agent']['type'])
        tpl.addLayer(layer=layer)
        evt = self.received(expected=tpl, timeout=timeout)
        return evt

    def encapsule(self, kate_event):
        """
        """
        layer_agent = TestTemplatesLib.TemplateLayer('AGENT')
        layer_agent.addKey(name='name', data=self.cfg['agent']['name'])
        layer_agent.addKey(name='type', data=self.cfg['agent']['type'])

        tpl = TestTemplatesLib.TemplateMessage()
        tpl.addLayer(layer=layer_agent)
        tpl.addLayer(layer=kate_event)
        return tpl

    def execRequest(self, apiMethod, parameters={}, waitForResponse=True, timeout=60.0, agentType=None):
        """
        General method for executing requests on kate agents
        """
        cmd = {'cmd': apiMethod, 'get': apiMethod, 'timeout': timeout}
        if parameters:
            cmd['parameters'] = parameters

        self.sendNotifyToAgent(data=cmd, agentType=agentType)

        if waitForResponse:
            layer_ansible = templates.ansibleAgent(layerName=self.__NAME__, event='response')
            evt = self.received(expected=self.encapsule(kate_event=layer_ansible), timeout=timeout)
            return evt.getLayer(self.__NAME__).getRaw()

        return
