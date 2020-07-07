#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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
Websocket module support
"""

import sys
import uuid
import base64
import struct
import threading
import hashlib

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

WEBSOCKET_VERSION = 13

WEBSOCKET_OPCODE_TEXT = 1
WEBSOCKET_OPCODE_BINARY = 2
WEBSOCKET_OPCODE_PING = 9
WEBSOCKET_OPCODE_PONG = 10

WEBSOCKET_MAX_BASIC_DATA = 125
WEBSOCKET_MAX_BASIC_DATA1024 = 1024
WEBSOCKET_EXT_DATA = 65535

# Websocket payload
#  0                   1                   2                   3
#      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#     +-+-+-+-+-------+-+-------------+-------------------------------+
#     |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
#     |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
#     |N|V|V|V|       |S|             |   (if payload len==126/127)   |
#     | |1|2|3|       |K|             |                               |
#     +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
#     |     Extended payload length continued, if payload len == 127  |
#     + - - - - - - - - - - - - - - - +-------------------------------+
#     |                               |Masking-key, if MASK set to 1  |
#     +-------------------------------+-------------------------------+
#     | Masking-key (continued)       |          Payload Data         |
#     +-------------------------------- - - - - - - - - - - - - - - - +
#     :                     Payload Data continued ...                :
#     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
#     |                     Payload Data continued ...                |
#     +---------------------------------------------------------------+

# Globally Unique Identifier
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketCodec(object):
    """
    Websocket codec
    """

    def __init__(self, parent, debug=False):
        """
        RFC 6455, minimal support

        @param parent: parent decoder
        @type parent: instance

        @param debug: codec debug
        @type debug: boolean
        """
        self.parent = parent
        self.__mutex__ = threading.RLock()
        self.pingId = 0
        self.pingMutex = threading.RLock()
        self.debug = debug

    def getNewPingId(self):
        """
        Returns ID for ping requet
        """
        self.pingMutex.acquire()
        self.pingId += 1
        ret = self.pingId
        self.pingMutex.release()
        return ret

    def createSecWsKey(self):
        """
        Create sec-websocket-key
        """
        encoded = ''
        try:
            uid = uuid.uuid4()
            encoded = base64.encodestring(uid.bytes).decode('utf-8').strip()
        except Exception as e:
            self.parent.error('unable to create sec key: %s' % e)
        return encoded

    def createSecWsAccept(self, key):
        """
        Create sec-websocket-accept value

        @param key: ws key
        @type key: string
        """
        if sys.version_info > (3,):
            value = key + bytes(GUID, 'utf8')
        else:
            value = (key + GUID).encode('utf-8')

        sha1 = hashlib.sha1()
        sha1.update(value)
        encoded = base64.encodestring(sha1.digest())
        encoded = encoded.strip().lower()
        return encoded

    def getHeaderForwardedFor(self, request):
        """
        Return x-forwarded-for header
        """
        xforwardedfor = None
        for hdr in request.splitlines()[1:]:
            k, v = hdr.split(b':', 1)
            if k.lower().strip() == b'x-forwarded-for':
                xforwardedfor = v.lower().strip()
                break
        return xforwardedfor

    def checkingWsReqHeaders(self, request):
        """
        Checking headers on request

        @param request: http request
        @type request: string
        """
        hdrUpgrade = False
        hdrConnection = False
        wsKey = False
        key = None
        wsVersion = False
        try:
            for hdr in request.splitlines()[1:]:
                k, v = hdr.split(b':', 1)
                if k.lower().strip() == b'upgrade' and v.lower().strip() == b'websocket':
                    hdrUpgrade = True
                if k.lower().strip() == b'connection' and b'upgrade' in v.lower().strip():
                    hdrConnection = True
                if k.lower().strip() == b'sec-websocket-key':
                    wsKey = True
                    key = v.strip()
                    keyLength = len(base64.b64decode(key))
                    if keyLength != 16:
                        self.parent.error('bad key length: %s' % keyLength)
                        wsKey = False
                if k.lower().strip() == b'sec-websocket-version':
                    version = "%s" % WEBSOCKET_VERSION
                    if sys.version_info > (3,):
                        version = bytes(version, "utf8")

                    if v.lower().strip() == version:
                        wsVersion = True

        except Exception as e:
            self.parent.error('unable to check req headers: %s' % e)
        return ((hdrUpgrade and hdrConnection and wsKey and wsVersion), key)

    def checkingWsHeaders(self, response, key):
        """
        Checking headers

        @param response: http response
        @type response: string

        @param key: ws key
        @type key: string
        """
        hdrUpgrade = False
        hdrConnection = False
        wsAccept = False
        try:
            for hdr in response.splitlines()[1:]:
                k, v = hdr.split(b':', 1)
                if k.lower().strip() == b'upgrade' and v.lower().strip() == b'websocket':
                    hdrUpgrade = True
                if k.lower().strip() == b'connection' and v.lower().strip() == b'upgrade':
                    hdrConnection = True
                if k.lower().strip() == b'sec-websocket-accept':
                    v = v.lower().strip()
                    # rfc6455 1.3. Opening Handshake
                    value = (key + GUID).encode('utf-8')
                    sha1 = hashlib.sha1()
                    sha1.update(value)
                    hashed = base64.encodestring(sha1.digest()).strip().lower()
                    if hashed == v:
                        wsAccept = True
                    else:
                        if self.debug:
                            self.parent.error(
                                'web socket key incorrect computed=%s received=%s key=%s' %
                                (hashed, v, key))
        except Exception as e:
            self.parent.error('unable to check headers: %s' % e)
        return hdrUpgrade and hdrConnection and wsAccept

    def decodeWsData(self, buffer):
        """
        Decode ws message

        @param buffer: buffer
        @type buffer: string
        """
        payload = ''
        opcode = None
        left = ''
        needMore = False
        try:
            try:
                hdrs_len = 2
                # B = 1 octet
                # H = 2 octets
                # I = 4 octets
                fixed_hdr = struct.unpack('!2B', buffer[:hdrs_len])
                # remaining = buffer[hdrs_len:]
            except struct.error:
                left = buffer  # need more data
                needMore = True
            else:

                fin = fixed_hdr[0] >> 7 & 1
                rsv1 = fixed_hdr[0] >> 6 & 1
                rsv2 = fixed_hdr[0] >> 5 & 1
                rsv3 = fixed_hdr[0] >> 4 & 1
                opcode = fixed_hdr[0] & 0xf

                has_mask = fixed_hdr[1] >> 7 & 1
                length = fixed_hdr[1] & 0x7f
                if self.debug:
                    self.parent.trace(
                        "ws header: %s, %s, %s, %s, %s, %s, %s" %
                        (fin, rsv1, rsv2, rsv3, opcode, has_mask, length))

                if length == 126:
                    try:
                        hdrs_extended_len = 2
                        # size = buffer[hdrs_len:hdrs_len + hdrs_extended_len]
                        ext_lenght_hdr = struct.unpack(
                            '!H', buffer[hdrs_len:hdrs_len + hdrs_extended_len])
                    except struct.error:
                        left = buffer  # need more data
                        needMore = True
                    else:
                        length_ext = ext_lenght_hdr[0]
                        if self.debug:
                            self.parent.trace(
                                "ws lenght extended: %s" % length_ext)
                        if fin:
                            if len(buffer) < hdrs_len + \
                                    hdrs_extended_len + length_ext:
                                if self.debug:
                                    self.parent.trace(
                                        "data extended, need more data (%s/%s)" %
                                        (len(buffer), length_ext))
                                left = buffer  # need more data
                                needMore = True
                            else:
                                payload = buffer[hdrs_len +
                                                 hdrs_extended_len:hdrs_len +
                                                 hdrs_extended_len +
                                                 length_ext]
                                left = buffer[hdrs_len +
                                              hdrs_extended_len + length_ext:]
                        else:
                            left = buffer  # need more data
                            needMore = True
                else:
                    if fin:
                        if len(buffer) < hdrs_len + length:
                            if self.debug:
                                self.parent.trace(
                                    "data, need more data (%s/%s)" %
                                    (len(buffer), length))
                            left = buffer  # need mode data
                            needMore = True
                        else:
                            payload = buffer[hdrs_len:hdrs_len + length]
                            left = buffer[hdrs_len + length:]
                    else:
                        left = buffer  # need mode data
                        needMore = True
        except Exception as e:
            self.parent.error('unable to decode ws data: %s' % e)
        return (payload, opcode, left, needMore)

    def encodeWsData(self, data, opcode):
        """
        Encode ws message

        @param data: data
        @type data: string

        @param opcode: opcode
        @type opcode: integer
        """
        ws_packet = []
        try:
            fin = 1
            rsv1 = 0
            rsv2 = 0
            rsv3 = 0
            opcode = opcode
            mask = 0
            length = len(data)

            byte1 = opcode | rsv3 << 4 | rsv2 << 5 | rsv1 << 6 | fin << 7
            byte2 = length | mask << 7

            if len(data) <= 125:
                fmt = '!2B'
                fixed_hdr = struct.pack(fmt, byte1, byte2)
            elif len(data) > 125 and len(data) <= 65535:
                fmt = '!2BH'
                byte2 = 126 | mask << 7
                bytesnext = len(data)
                fixed_hdr = struct.pack(fmt, byte1, byte2, bytesnext)
            else:
                pass

            ws_packet.append(fixed_hdr)
            ws_packet.append(data)
        except Exception as e:
            self.parent.error('unable to encode ws data: %s' % e)
        return b''.join(ws_packet)

    def encodeBinary(self, data):
        """
        Encode a binary message

        @param data: data in binary
        @type data: string
        """
        return self.encodeWsData(data=data, opcode=WEBSOCKET_OPCODE_BINARY)

    def encodeText(self, data):
        """
        Encode a text message

        @param data: data to encode
        @type data: string
        """
        return self.encodeWsData(data=data, opcode=WEBSOCKET_OPCODE_TEXT)

    def encodePing(self):
        """
        Encode a ping message
        """
        data = "%s" % self.getNewPingId()
        if sys.version_info[0] == 3:  # python 3 support
            return (self.encodeWsData(data=bytes(data, 'UTF-8'),
                                      opcode=WEBSOCKET_OPCODE_PING),
                    bytes(data, 'UTF-8'))
        else:
            return (self.encodeWsData(
                data=data, opcode=WEBSOCKET_OPCODE_PING), data)

    def encodePong(self, data=b'abcdef'):
        """
        Encode a pong message

        @param data: data to encode in pong response
        @type data: string
        """
        return self.encodeWsData(data=data, opcode=WEBSOCKET_OPCODE_PONG)
