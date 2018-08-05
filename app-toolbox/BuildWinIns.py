#!/usr/bin/python3
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
Module to construct the portable version with pyinstaller
"""

import os
import sys
import platform

from Libs import Settings

Settings.initialize()

os.rename( 
            "%s/dist/ExtensiveAutomationToolbox/" % Settings.getDirExec(), 
            "%s/dist/%s_%s_%s_Portable" % (Settings.getDirExec(), 
                                           Settings.get( section = 'Common', key='acronym' ), 
                                           Settings.getVersion(), 
                                           platform.architecture()[0]) 
        )

Settings.finalize()