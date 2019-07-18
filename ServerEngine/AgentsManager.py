#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
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

import base64
import zlib
import json 
import os
import signal
import shlex
import subprocess
import sys
import time
import shutil
import tarfile

try:
    import ConfigParser
except ImportError: # python3 support
    import configparser as ConfigParser

try:
    import Common
except ImportError: # python3 support
    from . import  Common
    
from Libs import Settings, Logger
from ServerInterfaces import AgentServerInterface as ASI

class AgentsManager(Logger.ClassLogger):    
    def __init__(self, context):
        """
        Construct Probes Manager
        """
        self.context = context
        self.configsFile = None
        self.__pids__ = {}

    def getRunning (self, b64=False):
        """
        Returns all registered agent

        @return: all registered agent
        @rtype: list
        """
        self.trace("get running agents" )
        ret = ASI.instance().getAgents()
        return ret

    def disconnectAgent(self, name):
        """
        Disconnect agent
        """
        self.info( "Disconnect agent Name=%s" % name )
        if not name in ASI.instance().agentsRegistered:
            self.trace( "disconnect agent, agent %s not found" % name )
            return self.context.CODE_NOT_FOUND
        else:
            agentProfile =  ASI.instance().agentsRegistered[name]
            ASI.instance().stopClient(client=agentProfile['address'] )
        return self.context.CODE_OK

    def stopAgent(self, aname):
        """
        Stop the agent gived in argument

        @type  aname:
        @param aname:

        @return: 
        @rtype: 
        """
        self.trace( "stop agent %s" % aname )
        ret = False
        try:
            client = ASI.instance().getAgent( aname=aname )
            if client is None:
                self.trace( "agent %s not found" % aname )
                ret = False
            else:
                self.trace( "agent %s found" % aname )
                ASI.instance().stopClient( client = client['address'] )
                ret = True
        except Exception as e:
            self.error( "unable to stop agent: %s" % e )
        return ret

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="ATM - %s" % txt)

AM = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return AM

def initialize (context):
    """
    Instance creation
    """
    global AM
    AM = AgentsManager(context=context)

def finalize ():
    """
    Destruction of the singleton
    """
    global AM
    if AM:
        AM = None