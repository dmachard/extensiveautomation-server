#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

"""
Module to handle settings
"""

try:
    from PyQt4.QtCore import (QSettings)
except ImportError:
    from PyQt5.QtCore import (QSettings)
    
import sys
import os

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
from .Libs import QtHelper, Logger
   
arg = sys.argv[0]
pathname = os.path.dirname(arg)
DIR_EXEC = os.path.abspath(pathname)

def getDirExec():
    """
    Dummy function
    """
    return DIR_EXEC

class Settings(object):
    """
    Settings accessor
    """
    def __init__(self, parent = None):
        """
        Settings of the application

        @param parent:
        @type parent:
        """
        self.dirExec = QtHelper.dirExec()
        
        # global settings
        self.settingsFileName = "settings.ini"
        self.fileName = "%s/Core/Files/%s" % ( self.dirExec, self.settingsFileName )
        # print(self.fileName)
        self.settings = QSettings( self.fileName,  QSettings.IniFormat    )

        self.appName = self.readValue( key = 'Common/Name' )

    def syncValues(self):
        """
        Synchronize value
        """
        self.settings.sync()

    def readValue (self, key, rType = 'str'):
        """
        Read value

        @param key:
        @type key:

        @param rType: expected values in str, qstr an qlist
        @type rType: string

        @return:
        @rtype: str
        """
        ret = self.settings.value(key)
        if ret is None:
            return ''
        if rType == 'str':
            if isinstance(ret, str): # python3 support
                return ret
            return str(ret.toString())
        elif rType == 'int':
            if isinstance(ret, str): # python3 support
                return int(ret)
            return int(ret.toString())
        elif rType == 'qstr':
            if sys.version_info > (3,):  # python3 support
                return ret
            return ret.toString()
        elif rType == 'qlist':
            if sys.version_info > (3,):  # python3 support
                return ret
            return ret.toStringList()
        else:
            return ret

    def setValue(self, key, value):
        """
        Set value

        @param key:
        @type key:

        @param value:
        @type value:
        """
        self.settings.setValue( key, value)
        self.settings.sync()
        
    def removeValue(self, key):
        """
        Remove value
        """
        self.settings.remove(key)
        
ST = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return ST

def initialize (parent = None):
    """
    Initialize the class Settings

    @param parent:
    @type: parent:
    """
    global ST
    ST = Settings(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global ST
    if ST:
        ST = None