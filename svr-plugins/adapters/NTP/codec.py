#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestLibraryLib as TestLibrary
import sys
import struct

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

try:
	import templates
except ImportError: # python3 support
	from . import templates

import time
import datetime

#system epoch
SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])

#NTP epoch
NTP_EPOCH = datetime.date(1900, 1, 1)

#delta between system and NTP time
NTP_DELTA = (SYSTEM_EPOCH - NTP_EPOCH).days * 24 * 3600

#leap indicator table
LEAP_TABLE = {
    0: "no warning",
    1: "last minute of the day has 61 seconds",
    2: "last minute of the day has 59 seconds",
    3: "unknown (clock unsynchronized)",
}

MODE_TABLE = {
    0: "reserved",
    1: "symmetric active",
    2: "symmetric passive",
    3: "client",
    4: "server",
    5: "broadcast",
    6: "reserved for NTP control messages",
    7: "reserved for private use",
}

STRATUM_TABLE = {
    0: "unspecified or invalid",
    1: "primary reference (%s)",
}

REF_ID_TABLE = {
    "GOES":  "Geostationary Orbit Environment Satellite",
    "GPS\0": "Global Position System",
    "GAL\0": "Galileo Positioning System",
    "PPS\0": "Generic pulse-per-second",
    "IRIG":  "Inter-Range Instrumentation Group",
    "WWVB":  "LF Radio WWVB Ft. Collins, CO 60 kHz",
    "DCF\0": "LF Radio DCF77 Mainflingen, DE 77.5 kHz",
    "HBG\0": "LF Radio HBG Prangins, HB 75 kHz",
    "MSF\0": "LF Radio MSF Anthorn, UK 60 kHz",
    "JJY\0": "LF Radio JJY Fukushima, JP 40 kHz, Saga, JP 60 kHz",
    "LORC":  "MF Radio LORAN C station, 100 kHz",
    "TDF\0": "MF Radio Allouis, FR 162 kHz",
    "CHU\0": "HF Radio CHU Ottawa, Ontario",
    "WWV\0": "HF Radio WWV Ft. Collins, CO",
    "WWVH":  "HF Radio WWVH Kauai, HI",
    "NIST":  "NIST telephone modem",
    "ACTS":  "NIST telephone modem",
    "USNO":  "USNO telephone modem",
    "PTB\0": "European telephone modem",
    "LOCL":  "uncalibrated local clock",
    "CESM":  "calibrated Cesium clock",
    "RBDM":  "calibrated Rubidium clock",
    "OMEG":  "OMEGA radionavigation system",
    "DCN\0": "DCN routing protocol",
    "TSP\0": "TSP time protocol",
    "DTS\0": "Digital Time Service",
    "ATOM":  "Atomic clock (calibrated)",
    "VLF\0": "VLF radio (OMEGA,, etc.)",
    "1PPS":  "External 1 PPS input",
    "FREE":  "(Internal clock)",
    "INIT":  "(Initialization)",
    "\0\0\0\0":   "NULL",
}

class Codec(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info
		self.stats = {}

	def toFrac(self, timestamp, n=32):
		"""
		Return the fractional part of a timestamp.
		
		@param bindIp: NTP timestamp
		@type bindIp: string
		
		@param bindIp: number of bits of the fractional part
		@type bindIp: int
		"""
		return int(abs(timestamp - int(timestamp)) * 2**n)
		
	def toTime(self, integ, frac, n=32):
		"""
		Return a timestamp from an integral and fractional part.
		
		@param bindIp: integral part
		@type bindIp: string

		@param bindIp: fractional part
		@type bindIp: string

		@param bindIp: number of bits of the fractional part
		@type bindIp: integer
		"""
		return integ + float(frac)/2**n
		
	def toNtpTime(self, timestamp):
		"""
		Convert a system time to a NTP time.
		
		@param timestamp: timestamp in system time
		@type timestamp: string

		"""
		return timestamp + NTP_DELTA
		
	def toSystemTime(self, timestamp):
		"""
		Convert a NTP time to system time.
			
		@param timestamp: timestamp in NTP time
		@type timestamp: string
		"""
		return timestamp - NTP_DELTA

	def encode(self, leap, version, mode, stratum, poll, precision, root_delay, root_dispersion, ref_id, 
											ref_timestamp, orig_timestamp,  recv_timestamp, tx_timestamp):
		"""
		"""
		tx_timestamp = self.toNtpTime( tx_timestamp )
		try:
			packed = struct.pack("!B B B b 11I", (leap << 6 | version << 3 | mode),
																		stratum, poll, precision,
																		int(root_delay) << 16 | self.toFrac(root_delay, 16),
																		int(root_dispersion) << 16 | self.toFrac(root_dispersion, 16),
																		ref_id, int(ref_timestamp), self.toFrac(ref_timestamp),
																		int(orig_timestamp), self.toFrac(orig_timestamp),
																		int(recv_timestamp), self.toFrac(recv_timestamp),
																		int(tx_timestamp), self.toFrac(tx_timestamp))
		except struct.error:
			raise NTPException("Encode error: Invalid NTP packet fields.")
			
		
		tpl = templates.msg(leap=leap, version=version, mode=mode, stratum=stratum, poll=poll, precision=precision,
																		rootDelay=root_delay, rootDispersion=root_dispersion, refId=ref_id, refTimestamp=ref_timestamp,
																		origTimestamp=orig_timestamp, recvTimestamp=recv_timestamp, txTimestamp=tx_timestamp) 
		tpl.addRaw(packed)
		return (packed, tpl)
				
	def decode(self, pkt, dest_timestamp):
		"""
		"""
		dest_timestamp = self.toNtpTime( dest_timestamp )
		try:
			unpacked = struct.unpack("!B B B b 11I", pkt[0:struct.calcsize("!B B B b 11I")])
		except struct.error:
			raise NTPException("Decode error: Invalid NTP packet.")
		else:
			leap = unpacked[0] >> 6 & 0x3
			version = unpacked[0] >> 3 & 0x7
			mode = unpacked[0] & 0x7
			stratum = unpacked[1]
			poll = unpacked[2]
			precision = unpacked[3]
			root_delay = float(unpacked[4])/2**16
			root_dispersion = float(unpacked[5])/2**16
			ref_id = unpacked[6]
			ref_timestamp = self.toTime(unpacked[7], unpacked[8])
			orig_timestamp = self.toTime(unpacked[9], unpacked[10])
			recv_timestamp = self.toTime(unpacked[11], unpacked[12])
			tx_timestamp = self.toTime(unpacked[13], unpacked[14])
			
			# prepare ntp stats
			offset = ((recv_timestamp - orig_timestamp) + (tx_timestamp - dest_timestamp))/2
			delay = ((dest_timestamp - orig_timestamp) - (tx_timestamp - recv_timestamp))

			ref_timestamp = self.toSystemTime(ref_timestamp)
			orig_timestamp = self.toSystemTime(orig_timestamp)
			recv_timestamp = self.toSystemTime(recv_timestamp)
			tx_timestamp = self.toSystemTime(tx_timestamp)
			dest_timestamp = self.toSystemTime(dest_timestamp)
			
			# decode leap indicator
			if leap in LEAP_TABLE:
				leapMsg = LEAP_TABLE[leap]
			else:
				leapMsg = "Invalid leap indicator."
				
			# decode mode to text
			if mode in MODE_TABLE:
				modeMsg = MODE_TABLE[leap]
			else:
				modeMsg = "Invalid mode."
		
			#decode statum
			if stratum in STRATUM_TABLE:
				stratumMsg = STRATUM_TABLE[stratum] % (stratum)
			elif 1 < stratum < 16:
				stratumMsg = "secondary reference (%s)" % (stratum)
			elif stratum == 16:
				stratumMsg = "unsynchronized (%s)" % (stratum)
			else:
				stratumMsg = "Invalid stratum or reserved."
				
			# decode ref id
			fields = (ref_id >> 24 & 0xff, ref_id >> 16 & 0xff, ref_id >> 8 & 0xff, ref_id & 0xff)
			if 0 <= stratum <= 1:
				text = '%c%c%c%c' % fields
				if text in REF_ID_TABLE:
					refIdMsg = REF_ID_TABLE[text]
				else:
					refIdMsg = "Unidentified reference source '%s'" % (text)
			elif 2 <= stratum < 255:
				refIdMsg = '%d.%d.%d.%d' % fields
			else:
				refIdMsg = "Invalid stratum."
				
			# construct the tpl
			tpl = templates.msg(leap=leap, version=version, mode=mode, stratum=stratum, poll=poll, precision=precision,
																				rootDelay=root_delay, rootDispersion=root_dispersion, refId=ref_id, refTimestamp=ref_timestamp,
																				origTimestamp=orig_timestamp, recvTimestamp=recv_timestamp, txTimestamp=tx_timestamp,
																				destTimestamp=dest_timestamp, offset=offset, delay=delay,
																				leapMsg=leapMsg, modeMsg=modeMsg, stratumMsg=stratumMsg, refIdMsg=refIdMsg) 
			tpl.addRaw(pkt)
			return tpl
			