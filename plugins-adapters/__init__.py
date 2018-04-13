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

import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib

Generic = None
TestAdapterLib.setVersion("v1200")
TestLibraryLib.setVersion("v810")

__RN__ = """Date: 11/02/2018
What's new
	1. (minor) New curl wrapper in HTTP adapter
	2. (minor) New dig wrapper in DNS adapter
	3. (minor) New nmap wrapper in System adapters
	4. (minor) System: add cp850 decoding for windows cmd response
	5. (major) Selenium: no more check platform parameter to support selenium server 3.9.0
	6. (major) Selenium: support w3c browser like firefox 58
	7. (minor) New ncat wrapper in System adapters
	8. (minor) New openssl wrapper in System adapters
Issues fixed
	1. none
"""

__DESCRIPTION__ = """This library contains all adapters available to test your SUT (System Under Test).

%s
""" % __RN__

import IPLITE
import Ethernet
import ARP
import IP
import ICMP
import DNS
import UDP
import SSL
import SOCKS
import TCP
import HTTP
import RTP
import SSH
import Telnet
import Pinger
import SOAP
import GUI
import Dummy
import System
import WebSocket
import SNMP
import REST
import FTP
import SIP
import Cisco
import SMS
import SFTP
import Database
import NTP
import LDAP
import KAFKA
import ANSIBLE

__HELPER__ =	[ ]
__HELPER__.append("Ethernet")
__HELPER__.append("ARP")
__HELPER__.append("IP") 
__HELPER__.append("ICMP")
__HELPER__.append("DNS") 
__HELPER__.append("UDP") 
__HELPER__.append("TCP") 
__HELPER__.append("HTTP") 
__HELPER__.append("RTP") 
__HELPER__.append("SSH") 
__HELPER__.append("Telnet")
__HELPER__.append("Pinger") 
__HELPER__.append("SOAP") 
__HELPER__.append("GUI") 
__HELPER__.append("Dummy") 
__HELPER__.append("System") 
__HELPER__.append("WebSocket") 
__HELPER__.append("SNMP") 
__HELPER__.append("REST") 
__HELPER__.append("FTP")
__HELPER__.append("SIP") 
__HELPER__.append("Cisco") 
__HELPER__.append("SMS") 
__HELPER__.append("SFTP") 
__HELPER__.append("Database") 
__HELPER__.append("NTP") 
__HELPER__.append("LDAP")
__HELPER__.append("KAFKA")
__HELPER__.append("ANSIBLE")