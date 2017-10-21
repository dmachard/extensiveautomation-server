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

import traceback
import StringIO
import time

import copy
import os
import tarfile

# def _extractall(self, path=".", members=None ):
    # """
    # Python 2.4 support, Fallback extractall method for TarFile
    # """
    # directories = []

    # if members is None:
        # members = self

    # for tarinfo in members:
        # if tarinfo.isdir():
            # Extract directories with a safe mode.
            # directories.append(tarinfo)
            # tarinfo = copy.copy(tarinfo)
            # tarinfo.mode = 0700
        # self.extract(tarinfo, path)

    # Reverse sort directories.
    # directories.sort(lambda a, b: cmp(a.name, b.name))
    # directories.reverse()

    # Set correct owner, mtime and filemode on directories.
    # for tarinfo in directories:
        # dirpath = os.path.join(path, tarinfo.name)
        # try:
            # self.chown(tarinfo, dirpath)
            # self.utime(tarinfo, dirpath)
            # self.chmod(tarinfo, dirpath)
        # except tarfile.ExtractError, e:
            # if self.errorlevel > 1:
                # raise
            # else:
                # self._dbg(1, "tarfile: %s" % e)

def indent(code, nbTab = 1):
    """
    Add tabulation for each lines

    @param nbTab:
    @type nbTab: int

    @return:
    @rtype: string
    """
    indentChar = '\t'*nbTab
    ret = []
    for line in code.splitlines() :
        ret.append("%s%s" % (indentChar, line) )
    return '\n'.join(ret)

def getBackTrace():
    """
    Returns the current backtrace.

    @return:
    @rtype:
    """
    backtrace = StringIO.StringIO()
    traceback.print_exc(None, backtrace)
    ret = backtrace.getvalue()
    backtrace.close()
    return ret

def getTimeStamp ():
    """
    Returns current timestamp (yyyy-MM-dd HH-mm-ss.SSS)

    @return:
    @rtype:
    """
    ret = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time()) ) \
                         + ".%3.3d" % int((time.time() * 1000) % 1000 )
    return ret
