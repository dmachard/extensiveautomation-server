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

"""
Settings
"""

try:
    import ConfigParser
except ImportError: # python 3 support
    import configparser as ConfigParser
import sys
import os
import time

arg = sys.argv[0]
pathname = os.path.dirname(arg)
DIR_EXEC = os.path.abspath(pathname)


def getDirExec ():
    """
    @return:
    @rtype:
    """
    return DIR_EXEC

def getVersion ():
    """
    @return:
    @rtype:
    """
    ver = 'undefined'
    try:
        f = open( '%s/VERSION' % getDirExec() )
        ver = f.read()
        f.close()
    except Exception as e:
        print( "[getVersion] Unable to read version: " + str(e) )
    return ver.strip()

def cfgFileIsPresent(path="./", cfgname='settings.ini' ):
    """
    New in 1.2.0, to fix issue 9

    @return: 
    @rtype: boolean
    """
    ret = False
    pathCfg = '%s/%s/%s' % (getDirExec(),path, cfgname)
    if os.path.isfile( pathCfg ):
        ret = True
    return ret


SETTINGS = None # singleton

def getInt (section, key):
    """
    Return integer
    """
    val = SETTINGS.get(section, key)
    return int(val)

def getBool (section, key):
    """
    Return bool
    """
    val = SETTINGS.getboolean(section, key)
    return val

def get (section, key):
    """
    Return value
    """
    val = SETTINGS.get(section, key)
    return val

def getItems (section):
    """
    Return all items in section
    """
    val = SETTINGS.items(section)
    return val

def set (section, key, value):
    """
    Set a value
    """
    val = SETTINGS.set(section, key, value)
    return val

def addSection (section):
    """
    Add a section
    """
    SETTINGS.add_section(section)
    
def removeSection (section):
    """
    Remove a section
    """
    SETTINGS.remove_section(section)
    
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return SETTINGS

def save(path="./", cfgname='settings.ini'):
    """
    Save settings
    """
    global SETTINGS
    if sys.version_info > (3,):
        configfile = open( '%s/%s/%s' % (getDirExec(),path, cfgname) , 'wt')
    else:
        configfile = open( '%s/%s/%s' % (getDirExec(),path, cfgname) , 'wb')
    SETTINGS.write(configfile)
        
def initialize (path="./", cfgname='settings.ini'):
    """
    Instance creation
    """
    global SETTINGS
    SETTINGS = ConfigParser.ConfigParser()
    if cfgFileIsPresent(path,cfgname):
        SETTINGS.read( '%s/%s/%s' % (getDirExec(),path, cfgname) )
    else:
        sys.stdout.write( "config file %s doesn't exist\n" % cfgname )

def finalize ():
    """
    Destruction of the singleton
    """
    global SETTINGS
    if SETTINGS:
        SETTINGS = None
