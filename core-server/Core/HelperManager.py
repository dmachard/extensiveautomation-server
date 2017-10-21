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

from Libs import Settings, Logger

import subprocess
import shlex
import base64
import zlib
import os

SUTADAPTERS_INSTALLED = True
SUTLIBADAPTERS_INSTALLED = True

class HelperManager(Logger.ClassLogger):
    def __init__ (self):
        """
        Documentation is generated with the start of the server in save in a file
        """
        if Settings.getInt('Boot','cache-documentations'):
            self.generateHelps()

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="HMG - %s" % txt)

    def generateHelps(self):
        """
        Generate the cache of the documentation

        @return:
        @rtype:
        """
        self.trace("Generating help cache..." )
        ret = False
        details = ''
        try:

            # args: path /tas, path /var/tmp/, sut installed
            __cmd__ = "%s %s/Core/DocBuild.py %s %s %s False %s False" % ( 
                                                Settings.get( 'Bin', 'python' ), Settings.getDirExec(), Settings.getDirExec(),
                                                "%s/%s" % (Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ) ), 
                                                SUTADAPTERS_INSTALLED, SUTLIBADAPTERS_INSTALLED
                                    )
            self.trace( __cmd__ )
            __cmd_args__ = shlex.split(__cmd__)
            p = subprocess.Popen( __cmd_args__, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            out, err = p.communicate()
            if out:
                self.trace( "Helper (out): %s" % out )
            if err:
                self.error( "Helper (err): %s" % err )
            if p.returncode == 1:
                self.error('Unable to generate help cache')
                details = err
            else:
                self.info('Documentation cache successfully generated')
                ret = True
        except Exception as e:
            self.error( e )
        return ( ret, details )
            
    def getHelps(self):
        """
        Returns the documentation cache

        @return:
        @rtype:
        """
        self.trace("Helper manager - get helps" )
        ret = ''
        try:
            complete_path = '%s/%s/documentations.dat' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ))
            if os.path.exists( complete_path ):
                fd = open( complete_path , "r")
                data = fd.read()
                fd.close()
                ret = base64.b64encode( zlib.compress(data) )
            else:
                self.error( 'documentation cache does not exist' ) 
        except Exception as e:
            self.error( "unable to get helps: %s" % e )
        return ret

HM = None # singleton
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return HM

def initialize ():
    """
    Instance creation
    """
    global HM
    HM = HelperManager()

def finalize ():
    """
    Destruction of the singleton
    """
    global HM
    if HM:
        HM = None