#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestLibraryLib as TestLibraryLib

Generic = None
TestLibraryLib.setVersion("v800")

__RN__ = """Date: 04/06/2017
What's new
	1. (medium) Json: new functions to support jsonpath
	2. (medium) New date section with today library
	3. (minor) Time: new function to get the current time
	4. (medium) Xml: new functions to support xpath in full mode
	5. (minor) Json: new function to return JSON data to human-readable form
	6. (minor) Xml codec: new function to return XML data to human-readable form
	7. (major) Support new decorator function for documentation
	8. (major) Package Authentication renamed to Security
	9. (medium) New library to manage certificate
	10. (major) New wrapper to the nmap command
	11. (minor) Xml/Json: new function to valid the format
	12. (minor) Base64 decoder: add missing padding in decode function
	13. (medium) New RSA library to generate private and public key
	14. (medium) New JWT library to encode or decode a token
Issues fixed
	1. None
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