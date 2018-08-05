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
	from checksum import Checksum
	from hash_md5 import MD5
	from hash_sha1 import SHA1
	from hash_sha256 import SHA256
	from hash_sha512 import SHA512
	from crc32 import CRC32
	from hmac_md5 import HMAC_MD5
	from hmac_sha1 import HMAC_SHA1
	from hmac_sha256 import HMAC_SHA256
except ImportError: # support python 3
	from .checksum import Checksum
	from .hash_md5 import MD5
	from .hash_sha1 import SHA1
	from .hash_sha256 import SHA256
	from .hash_sha512 import SHA512
	from .crc32 import CRC32
	from .hmac_md5 import HMAC_MD5
	from .hmac_sha1 import HMAC_SHA1
	from .hmac_sha256 import HMAC_SHA256
	
__DESCRIPTION__ = "Hashing algorithms"