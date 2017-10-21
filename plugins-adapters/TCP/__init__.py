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

from client import *
from server import *
from codec import *
from templates import *
from sniffer import *
from stack import *

__DESCRIPTION__ = """This adapter enables to send/receive data trought TCP transport protocol, SSL support.

The Transmission Control Protocol (TCP) provides reliable, ordered delivery of a stream of octets to the application level between hosts over an Internet Protocol (IP) network.

More informations in the RFC793, RFC3540, RFC1323, RFC2018 and RFC3168."""