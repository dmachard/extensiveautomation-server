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

__DESCRIPTION__ = """The library enable to handle repositories."""
__HELPER__ = [
                ('Paths', ['tests', 'adapters'])
             ]
             
__testspath = ''
__adpspath = ''

def setTestsPath(path):
    """
    Set tests path
    """
    global __testspath
    __testspath = path

def setAdpsPath(path):
    """
    Set tests path
    """
    global __adpspath
    __adpspath = path

def getTestsPath():
    """
    Return tests path

    @return: path
    @rtype: string
    """
    global __testspath
    return __testspath
    
def getAdaptersPath():
    """
    Return adapters path

    @return: path
    @rtype: string
    """
    global __adpspath
    return __adpspath

class Paths(object):
    """
    """
    
    def tests(self):
        """
        Return tests path

        @return: path
        @rtype: string
        """
        global __testspath
        return __testspath
        
    def adapters(self):
        """
        Return adapters path

        @return: path
        @rtype: string
        """
        global __adpspath
        return __adpspath