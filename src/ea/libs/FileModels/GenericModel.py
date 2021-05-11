#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

"""
Generic model
"""
from ea.libs import Logger
import sys
import zlib
import base64

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError:  # support python3
    xrange = range


class GenericModel(Logger.ClassLogger):
    """
    Data model for generic test
    """

    def __init__(self, level=6, compressed=False):
        """
        Generic model
        """
        self.level = level
        self.compressed = compressed

    def toXml(self):
        """
        Returns to xml
        """
        raise Exception('To reimplement')

    def fixXML(self, data, key):
        """
        Fix xml

        @param data:
        @type data:

        @param key:
        @type key:
        """
        if isinstance(data[key], dict):
            data[key] = [data[key]]

    def fixPyXML(self, data, key):
        """
        Fix xml

        @param data:
        @type data:

        @param key:
        @type key:
        """
        if '@%s' % key in data:
            nb = len(data[key])
            tpl = []
            for i in xrange(nb):
                tpl.append({})
            data['@%s' % key] = tpl

    def write(self, absPath):
        """
        Write the file on the disc

        @param absPath:
        @type absPath:
        """
        ret = False
        try:
            xmlraw = self.toXml()
            if xmlraw is None:
                raise Exception("bad xml")
            else:
                f = open(absPath, 'wb')
                raw = unicode(xmlraw).encode('utf-8')
                if self.compressed:
                    f.write(zlib.compress(raw, self.level))
                else:
                    f.write(raw)
                f.close()
                ret = True
        except Exception as e:
            self.error(e)
        return ret

    def getRaw(self):
        """
        Return the content file zipped and encoded in the base64
        """
        encoded = None
        try:
            xmlraw = self.toXml()
            if xmlraw is None:
                raise Exception("bad xml")
            raw = unicode(xmlraw).encode('utf-8')

            # compress and encode in base64 before to return it
            if self.compressed:
                compressed = zlib.compress(raw, self.compress)
                encoded = base64.b64encode(compressed)
            else:
                encoded = base64.b64encode(raw)

            if sys.version_info > (3,):
                encoded = encoded.decode("utf-8")
        except Exception as e:
            self.error(e)
        return encoded

    def load(self, absPath=None, rawData=None):
        """
        Load xml content from a file or raw data

        @param absPath:
        @type absPath:

        @param rawData:
        @type rawData:
        """
        if absPath is None and rawData is None:
            self.error('absPath and rawData are equal to None')
            return False

        read_data = rawData

        if rawData is None:
            try:
                f = open(absPath, 'rb')
                read_data = f.read()
                f.close()
            except Exception as e:
                self.error("open file: %s" % e)
                return False

        # to be backward compatible, try to decompress the file
        try:
            decompressed_data = zlib.decompress(read_data)
        except Exception:
            # return the file as plain text
            return self.onLoad(decompressedData=read_data)
        else:
            return self.onLoad(decompressedData=decompressed_data)

    def onLoad(self, decompressedData):
        """
        Called on data model loading
        """
        raise Exception('To reimplement')
