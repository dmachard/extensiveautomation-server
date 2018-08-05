#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive automation project
# Copyright (c) 2010-2018 Denis Machard
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
#
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensiveautomation.org
# -------------------------------------------------------------------

"""
Main module 
"""

# name of the main developer
__AUTHOR__ = 'Denis Machard'
# email of the main developer
__EMAIL__ = 'd.machard@gmail.com'
# list of contributors
__CONTRIBUTORS__ = [ "" ]
# list of contributors
__TESTERS__ = [ "" ]
# project start in year
__BEGIN__="2016"
# year of the latest build
__END__="2017"
# date and time of the buid
__BUILDTIME__="27/05/2017 10:21:09"
# debug mode
DEBUGMODE=False


from Core import CorePlugin
from Core import Settings
from Core.Libs import Logger

import sys
import sip
import json
import os

# adding missing folders
if not os.path.exists( "%s/Core/Logs/" % Settings.getDirExec() ):
    os.mkdir( "%s/Core/Logs" % Settings.getDirExec() )
    
try:
    from PyQt4.QtGui import (QApplication)
except ImportError:
    from PyQt5.QtWidgets import (QApplication)
    
CONFIG_JSON = None
with open( "%s/config.json" % (Settings.getDirExec()) ) as f:
    CONFIG_RAW = f.read()
CONFIG_JSON = json.loads(CONFIG_RAW)

if CONFIG_JSON is None:
    sys.exit(-1)
        
class MyPlugin(CorePlugin.GenericPlugin):
    """
    """
    def __init__(self, pluginName='undefined', pluginType='agent'):
        """
        """
        super(MyPlugin, self).__init__()
        
    def onStartingPlugin(self):
        """
        """
        self.logWarning("Starting dummy agent")
        
    def onPluginStarted(self):
        """
        """
        self.logWarning("Dummy agent started")
        
    def onAgentNotify(self, client, tid, request): 
        """
        Function to overwrite
        """
        Logger.instance().info("notify received")
        self.logWarning(msg="notify received: %s" % request['data'])
        self.sendData(request=request, data={'a': '\x00é'})
        self.sendError(request=request, data="error sent")
        
    def onAgentReset(self, client, tid, request): 
        """
        Function to overwrite
        """
        Logger.instance().info("reset received")
        if 'data' in request:
            self.logWarning(msg="reset called: %s" % request['data'])
        else:
            self.logWarning(msg="reset called")
            
    def onAgentInit(self, client, tid, request): 
        """
        Function to overwrite
        """
        Logger.instance().info("init received")
        self.logWarning(msg="init called: %s" % request['data'])
        self.sendNotify(request=request, data="notify sent")
        
    def onAgentAlive(self, client, tid, request): 
        """
        Function to overwrite
        """
        Logger.instance().info("alive received")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # initiliaze settings application, read settings from the ini file
    Settings.initialize()
    
    # initialize logger
    logPathFile = "%s/%s" % ( Settings.getDirExec(), Settings.instance().readValue( key ='Trace/file' ) )
    level = Settings.instance().readValue( key ='Trace/level' )
    size = Settings.instance().readValue( key ='Trace/max-size-file' )
    nbFiles = int( Settings.instance().readValue( key ='Trace/nb-backup-max' ) )
    Logger.initialize( logPathFile=logPathFile, level=level, size=size, nbFiles=nbFiles, noSettings=True )
    
    # init the plugin
    # MyPlugin = CorePlugin.GenericPlugin(
    Plugin = MyPlugin(
                        pluginName=CONFIG_JSON["plugin"]["name"], 
                        pluginType=CONFIG_JSON["plugin"]["type"]
                    )
    
    sys.exit(app.exec_())