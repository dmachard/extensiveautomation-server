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

import sys
import os
try:
    import ConfigParser
except ImportError:  # python3 support
    import configparser as ConfigParser

# extract the main path of the package
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
new_dir_path = os.sep.join(dir_path.split(os.sep)[:-1])

DIR_EXEC = os.path.normpath("%s/" % new_dir_path)


def getDirExec():
    """
    @return:
    @rtype:
    """
    return DIR_EXEC


def getVersion(path="./"):
    """
    @return:
    @rtype:
    """
    ver = 'undefined'
    try:
        vpath = '%s/%s/VERSION' % (getDirExec(), path)
        f = open(vpath)
        ver = f.read()
        f.close()
    except Exception as e:
        print("[getVersion] Unable to read version: " + str(e))
    return ver.strip()


def cfgFileIsPresent(path="./", cfgname='settings.ini'):
    """
    New in 1.2.0, to fix issue 9

    @return:
    @rtype: boolean
    """
    ret = False
    if os.path.isfile('%s/%s/%s' % (getDirExec(), path, cfgname)):
        ret = True
    return ret


SETTINGS = None  # singleton


def getInt(section, key):
    """
    """
    val = SETTINGS.get(section, key)
    return int(val)


def getBool(section, key):
    """
    """
    val = SETTINGS.getboolean(section, key)
    return val


def get(section, key):
    """
    """
    val = SETTINGS.get(section, key)
    return val


def set(section, key, value, path="./", cfgname='settings.ini'):
    """
    Set value and write to file
    Be careful, comments are removed with this function
    """
    SETTINGS.set(section, key, value)
    completePath = '%s/%s/%s' % (getDirExec(), path, cfgname)
    with open(completePath, 'w') as f:
        SETTINGS.write(f)


def instance():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return SETTINGS


def initialize(path="./", cfgname='settings.ini'):
    """
    Instance creation
    """
    global SETTINGS
    SETTINGS = ConfigParser.ConfigParser()
    completePath = '%s/%s/%s' % (getDirExec(), path, cfgname)

    if cfgFileIsPresent(path, cfgname):
        SETTINGS.read(completePath)
    else:
        sys.stdout.write("config file %s doesn't exist\n" % completePath)


def finalize():
    """
    Destruction of the singleton
    """
    global SETTINGS
    if SETTINGS:
        SETTINGS = None
