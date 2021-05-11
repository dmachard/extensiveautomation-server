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
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
