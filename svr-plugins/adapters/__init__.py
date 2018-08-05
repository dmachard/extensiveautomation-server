#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib

Generic = None
Default = None
TestAdapterLib.setVersion("base_v1300")
TestLibraryLib.setVersion("base_v900")

__RN__ = """Date: 29/07/2018
What's new
	1. (major) split between base and extra adapters
	2. (minor) terminal: added the possibility of not logging sent messages from terminal adapter (pull request #7)
	3. (minor) ssl/tcp/http server: the certificate and key files can now be added from parameters (pull request #7)
	4. (minor) ssl/tcp/http: new ciphers client side argument 
	5. (medium) telnet: support new options 36 to 39
	6. (medium) New ansible adapter with agent mode support (pull request #8)
	7. (medium) New kafka adapter with agent mode support too (pull request #15)
	8. (major) Generic Curl adapter moved to System folder
	9. (major) important update of the curl http adapter
	10. (medium) all adapters updated to use the new way to check agent and timeout argument
Issues fixed
	1. (minor) fix bad option code in telnet
"""

__DESCRIPTION__ = """This library contains all adapters available to test your SUT (System Under Test).

%s
""" % __RN__

try:
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
	import Ansible
	import Kafka
except ImportError: # python3 support
	from . import IPLITE
	from . import Ethernet
	from . import ARP
	from . import IP
	from . import ICMP
	from . import DNS
	from . import UDP
	from . import SSL
	from . import SOCKS
	from . import TCP
	from . import HTTP
	from . import RTP
	from . import SSH
	from . import Telnet
	from . import Pinger
	from . import SOAP
	from . import GUI
	from . import System
	from . import WebSocket
	from . import SNMP
	from . import REST
	from . import FTP
	from . import SIP
	from . import Cisco
	from . import SMS
	from . import SFTP
	from . import Database
	from . import NTP
	from . import LDAP
	from . import Ansible
	from . import Kafka
	
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
__HELPER__.append("Ansible")
__HELPER__.append("Kafka")