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

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
import sys

ALL     = -1

# Protocol: 
# This field indicates the next level protocol used in the data
# portion of the internet datagram.  The values for various protocols
# are specified in "Assigned Numbers" [9].
# http://www.ietf.org/rfc/rfc790.txt

ICMP    = 1
IGMP    = 2
TCP     = 6
UDP     = 17
RDP     = 27
ICMPV6  = 58
VRRP    = 112
SCTP    = 132
OSPF    = 89
L2TP    = 115

# ASSIGNED INTERNET PROTOCOL NUMBERS
PRO_TYPE_MAP = {}
PRO_TYPE_MAP[ICMP]    = "ICMP4" # Internet Control Message Protocol
PRO_TYPE_MAP[TCP]     = "TCP" # Transmission Control Protocol
PRO_TYPE_MAP[UDP]     = "UDP" # User Datagram
#PRO_TYPE_MAP[IGMP]    = "IGMP" # Internet Group Management Protocol
#PRO_TYPE_MAP[RDP]     = "RDP" # Reliable Datagram Protocol
#PRO_TYPE_MAP[ICMPV6]  = "ICMP6" # ICMP for IPv6
#PRO_TYPE_MAP[VRRP]    = "VRRP" # Virtual Router Redundancy Protocol
#PRO_TYPE_MAP[SCTP]    = "SCTP" # Stream Control Transmission Protocol
#PRO_TYPE_MAP[OSPF]    = "OSPF" # Open Shortest Path First
#PRO_TYPE_MAP[L2TP]    = "L2TP" # Layer Two Tunneling Protocol Version 3