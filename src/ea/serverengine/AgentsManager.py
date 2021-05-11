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

from ea.libs import Logger
from ea.serverinterfaces import AgentServerInterface as ASI

from ea.serverengine import DbManager

class AgentsManager(Logger.ClassLogger):
    def __init__(self, context):
        """
        Construct Probes Manager
        """
        self.context = context
        
        self.tb_agents = 'agents'
        # load agents token in cache, new in v23
        self.cache = {}
        self.load_cache()

    def load_cache(self):
        """load cache"""
        self.cache = {}
        
        sql = """SELECT * FROM `%s`""" % (self.tb_agents)
        success, rows = DbManager.instance().querySQL(query=sql,
                                                      columnName=True)
        if not success:
            raise Exception("unable to init agents caching")
        
        for r in rows:
            self.cache[r["token"]] = r
            
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


def initialize(*args, **kwargs):
    """
    Instance creation
    """
    global AM
    AM = AgentsManager(*args, **kwargs)


def finalize():
    """
    Destruction of the singleton
    """
    global AM
    if AM:
        AM = None
