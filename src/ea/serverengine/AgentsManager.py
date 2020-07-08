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

from ea.libs import Logger
from ea.serverinterfaces import AgentServerInterface as ASI


class AgentsManager(Logger.ClassLogger):
    def __init__(self, context):
        """
        Construct Probes Manager
        """
        self.context = context

    def getRunning(self, b64=False):
        """
        Returns all registered agent
        """
        self.trace("get running agents")
        ret = ASI.instance().getAgents()
        return ret

    def disconnectAgent(self, name):
        """
        Disconnect agent
        """
        self.info("Disconnect agent Name=%s" % name)
        if name not in ASI.instance().agentsRegistered:
            self.trace("disconnect agent, agent %s not found" % name)
            return self.context.CODE_NOT_FOUND

        agentProfile = ASI.instance().agentsRegistered[name]
        ASI.instance().stopClient(client=agentProfile['address'])
        return self.context.CODE_OK


AM = None


def instance():
    """
    Returns the singleton
    """
    return AM


def initialize(context):
    """
    Instance creation
    """
    global AM
    AM = AgentsManager(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global AM
    if AM:
        AM = None
