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
Module to construct messages
"""

try:
    import cPickle
except ImportError:  # support python 3
    import pickle as cPickle
import zlib
import base64
import sys
import json

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

HEAD_SEP = b" "
BODY_SEP = b"\n"

RSQ_CMD = b"RSQ"
RSQ_NOTIFY = b"NOTIFY"

RSP_CODE_OK = (b"200", b"OK")
RSP_CODE_FORBIDDEN = (b"403", b"FORBIDDEN")
RSP_CODE_FAILED = (b"400", b"FAILED")
RSP_CODE_ERROR = (b"500", b"ERROR")

CMD_ERROR = -1
CMD_HELLO = 0
CMD_GET_PROBE = 1
CMD_START_PROBE = 2
CMD_STOP_PROBE = 3
CMD_NEW_FILE = 4
CMD_INTERACT = 5
CMD_START_AGENT = 6
CMD_STOP_AGENT = 7


def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val


def bytes_to_unicode(ob):
    """
    Byte to unicode with exception...
    Only for py3, will be removed on future version...
    """
    t = type(ob)
    if t in (list, tuple):
        try:
            l_ = [str(i, 'utf-8') if isinstance(i, bytes) else i for i in ob]
        except UnicodeDecodeError:
            l_ = [i for i in ob]  # keep as bytes
        l_ = [bytes_to_unicode(i) if type(i) in (
            list, tuple, dict) else i for i in l_]
        ro = tuple(l_) if t is tuple else l_
    elif t is dict:
        byte_keys = [i for i in ob if isinstance(i, bytes)]
        for bk in byte_keys:
            v = ob[bk]
            del(ob[bk])
            try:
                ob[str(bk, 'utf-8')] = v
            except UnicodeDecodeError:
                ob[bk] = v  # keep as bytes
        for k in ob:
            if isinstance(ob[k], bytes):
                try:
                    ob[k] = str(ob[k], 'utf-8')
                except UnicodeDecodeError:
                    ob[k] = ob[k]  # keep as bytes
            elif type(ob[k]) in (list, tuple, dict):
                ob[k] = bytes_to_unicode(ob[k])
        ro = ob
    else:
        ro = ob
    return ro


class Messages(object):
    """
    Codec for messages
    """

    def __init__(self, userId=None, useJson=False, pickleVer=2):
        """
        Constructor

        @param userId: user identifier (default=None)
        @type userId: string

        @param useJson: use json instead of pickle (default=False)
        @type useJson: boolean

        @param pickleVer: pickle version used (default=2) backward compatibility with python2
        @type pickleVer: integer
        """
        self.__userId = userId
        self.__useJson = useJson
        self.__pickleProtocol = pickleVer

    def setUserId(self, userId):
        """
        Set the userid

        @param userId: user identifier
        @type userId: string
        """
        self.__userId = userId

    def encode(self, op, tid, desc, body=None):
        """
        Encode a message (response or request

        @param op: operator
        @type op:

        @param tid: transaction id
        @type tid:

        @param desc: description
        @type desc:

        @param body: content of the message
        @type body:

        @return: the message encoded
        @rtype: string
        """
        # encode a response ?
        if op.isdigit():
            # example: 200 OK, 403 FORBIDDEN, etc...
            if op not in [RSP_CODE_OK[0], RSP_CODE_FORBIDDEN[0],
                          RSP_CODE_FAILED[0], RSP_CODE_ERROR[0]]:
                raise Exception('unknown response code: %s' % op)
            if desc not in [RSP_CODE_OK[1], RSP_CODE_FORBIDDEN[1],
                            RSP_CODE_FAILED[1], RSP_CODE_ERROR[1]]:
                raise Exception('unknown response phrase: %s' % desc)

        # encode a request: cmd or notify
        else:
            if op not in [RSQ_CMD, RSQ_NOTIFY]:
                raise Exception('unknown request: %s' % op)

        # prepare the head of the message
        if sys.version_info > (3,):  # python 3 support
            if not isinstance(desc, bytes):
                desc = bytes(desc, 'utf8')
            ret = [HEAD_SEP.join([op, bytes(str(tid), 'utf8'), desc])]
        else:
            ret = [HEAD_SEP.join([op, str(tid), desc])]

        # adding the body as json or pickled(default)
        # also zipped and encoded in base64
        if body:
            if not self.__useJson:
                pickled = cPickle.dumps(body, protocol=self.__pickleProtocol)
                bod = zlib.compress(pickled)
                ret.append(base64.encodestring(bod))
            else:
                json_data = json.dumps(body, ensure_ascii=False)
                compressed = zlib.compress(json_data)
                ret.append(base64.encodestring(compressed))
        else:
            rslt = ret

        # join all and return the message
        rslt = BODY_SEP.join(ret)

        return rslt

    def decode(self, msgraw):
        """
        Decode a message: request or response

        @param msgraw:
        @type msgraw:

        @return: request or response
        @rtype: typle
        """
        # split the body
        msg = msgraw.split(BODY_SEP, 1)
        # no body in the message
        if len(msg) == 1:
            head = msg[0].split(HEAD_SEP)
            body = b''

        # header with body
        elif len(msg) == 2:
            # extract the header of the message
            head = msg[0].split(HEAD_SEP)

            # extract the body
            # the body is encoded in the base 64 and zipped
            if sys.version_info > (3,):  # support python3
                decoded = base64.b64decode(msg[1])
            else:
                decoded = base64.decodestring(msg[1])  # deprecated function
            decompressed_data = zlib.decompress(decoded)
            if not self.__useJson:
                if sys.version_info > (3,):  # support python3
                    body = cPickle.loads(decompressed_data, encoding="bytes")
                    # convert bytes to unicode with exceptions, workaround
                    body = bytes_to_unicode(body)
                else:
                    body = cPickle.loads(decompressed_data)
            else:
                body = json.loads(decompressed_data, encoding="ISO-8859-1")
        else:
            raise Exception('invalid message')

        # the final message is a dictionary with the following keys
        #  - tid key = transaction id
        #  - body key = content of the message
        # if response
        #  - code key
        #  - phrase key
        # if request
        #  - cmd key
        #  - userid key
        # finally return a tuple (response,...) or (request, ...)
        ret = {}
        ret['tid'] = int(head[1])
        ret['body'] = body
        if head[0].isdigit():
            ret['code'] = head[0]
            if ret['code'] not in [RSP_CODE_OK[0], RSP_CODE_FORBIDDEN[0],
                                   RSP_CODE_FAILED[0], RSP_CODE_ERROR[0]]:
                raise Exception('unknown response code: %s' % ret['code'])

            ret['phrase'] = head[2]
            if ret['phrase'] not in [RSP_CODE_OK[1], RSP_CODE_FORBIDDEN[1],
                                     RSP_CODE_FAILED[1], RSP_CODE_ERROR[1]]:
                raise Exception('unknown response phrase: %s' % ret['phrase'])
            return ('response', ret)
        else:

            ret['cmd'] = head[0]
            if ret['cmd'] not in [RSQ_CMD, RSQ_NOTIFY]:
                raise Exception('unknown request: %s' % ret['cmd'])
            ret['userid'] = head[2]
            return ('request', ret)

    def ok(self, tid, body=None):
        """
        Encode a ok message

        @param tid: transaction id
        @type tid:

        @param body:
        @type body:

        @return: one ok message encoded
        @rtype: string
        """
        ret = self.encode(
            op=RSP_CODE_OK[0],
            tid=tid,
            desc=RSP_CODE_OK[1],
            body=body)
        return ret

    def forbidden(self, tid, body=None):
        """
        Encode a forbidden message

        @param tid: transaction id
        @type tid:

        @param body:
        @type body:

        @return: one forbidden message encoded
        @rtype: string
        """
        ret = self.encode(
            op=RSP_CODE_FORBIDDEN[0],
            tid=tid,
            desc=RSP_CODE_FORBIDDEN[1],
            body=body)
        return ret

    def failed(self, tid, body=None):
        """
        Encode a failed message

        @param tid: transaction id
        @type tid:

        @param body:
        @type body:

        @return: one failed message encoded
        @rtype: string
        """
        ret = self.encode(
            op=RSP_CODE_FAILED[0],
            tid=tid,
            desc=RSP_CODE_FAILED[1],
            body=body)
        return ret

    def error(self, tid, body=None):
        """
        Encode an error message

        @param tid: transaction id
        @type tid:

        @param body:
        @type body:

        @return: one error message encoded
        @rtype: string
        """
        ret = self.encode(
            op=RSP_CODE_ERROR[0],
            tid=tid,
            desc=RSP_CODE_ERROR[1],
            body=body)
        return ret

    def cmd(self, tid, body):
        """
        Encode a command

        @param tid: transaction id
        @type tid:

        @param body:
        @type body:

        @return: one cmd message encoded
        @rtype: string
        """
        ret = self.encode(op=RSQ_CMD, tid=tid, desc=self.__userId, body=body)
        return ret

    def notify(self, tid, body):
        """
        Encode a notify

        @param tid: transaction id
        @type tid:

        @param body:
        @type body:

        @return: one notify message encoded
        @rtype: string
        """
        ret = self.encode(
            op=RSQ_NOTIFY,
            tid=tid,
            desc=self.__userId,
            body=body)
        return ret
