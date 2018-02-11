#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestLibraryLib as TestLibraryLib

Generic = None
TestLibraryLib.setVersion("v810")

__RN__ = """Date: 11/02/2018
What's new
	1. (medium) Nmap libraries moved to adapters
Issues fixed
	1. none
"""

__DESCRIPTION__ = """Libraries for your SUT adapters and tests.

%s
""" % __RN__

import Media
import Codecs
import Ciphers
import Hashing
import Security
import Security as Authentication # kept for backward compatibility
import Time
import Identifiers
import Dummy
import Units
import Compression
import Date

__HELPER__ =	[ ]
__HELPER__.append("Media")
__HELPER__.append("Codecs")
__HELPER__.append("Ciphers")
__HELPER__.append("Hashing")
__HELPER__.append("Security")
__HELPER__.append("Time")
__HELPER__.append("Identifiers")
__HELPER__.append("Dummy")
__HELPER__.append("Units")
__HELPER__.append("Compression")
__HELPER__.append("Date")