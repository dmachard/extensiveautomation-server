#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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
try:
    import cStringIO
except ImportError: # support python 3
    import io as cStringIO
import time

import os

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
    backtrace = cStringIO.StringIO()
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
