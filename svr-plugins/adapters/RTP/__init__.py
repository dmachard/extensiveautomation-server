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

try:
	from client import *
except ImportError: # python3 support
	from .client import *
	
__DESCRIPTION__ = """This adapter enables to send/receive rtp.

The real-time transport protocol (RTP) provides end-to-end network transport functions suitable for applications transmitting real-time data, such as audio, video or more.

More informations in the RFC 1889."""

__HELPER__ =	[
				( "Client", [ "__init__", "startSending", "stopSending", "setCodec", "sendPacket", "configure",
													"onSending", "onReceiving", "onInactivity", "hasStartedReceiving", "hasStoppedReceiving" ] ),
]