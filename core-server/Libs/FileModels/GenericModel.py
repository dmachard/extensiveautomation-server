#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
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

"""
Generic model
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range
    
from Libs import Logger

import zlib
import base64
  
class GenericModel(Logger.ClassLogger):
    """
    Data model for generic test
    """
    def __init__ (self, compress=6):
        """
        Generic model
        """
        self.compress = compress

    def toXml(self):
        """
        Returns to xml
        """
        raise Exception('To reimplement')

    def fixXML (self, data, key):
        """
        Fix xml

        @param data: 
        @type data:

        @param key: 
        @type key:
        """
        if isinstance( data[key], dict):
            data[key] = [ data[key] ]

    def fixPyXML(self, data, key):
        """
        Fix xml

        @param data: 
        @type data:

        @param key: 
        @type key:
        """
        if '@%s' % key  in data:
            nb = len(data[key])
            tpl = []
            for i in xrange(nb):
                tpl.append( {} )
            data[ '@%s' % key ] = tpl

    def write(self, absPath ):
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
                raw =  unicode( xmlraw ).encode('utf-8') 
                f.write( zlib.compress( raw, self.compress ) )
                f.close()
                ret = True
        except Exception as e:
            self.error( e )
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
            raw = unicode( xmlraw ).encode('utf-8')
            compressed = zlib.compress( raw, self.compress ) 
            encoded = base64.b64encode( compressed )
        except Exception as e:
            self.error( e )
        return encoded
    
    def load (self, absPath = None, rawData = None):
        """ 
        Load xml content from a file or raw data

        @param absPath: 
        @type absPath:

        @param rawData: 
        @type rawData:
        """
        if absPath is None and rawData is None:
            self.error( 'absPath and rawData are equal to None' )
            return False

        if rawData is None:
            try:
                f = open(absPath, 'rb')
                read_data = f.read()
                f.close()
            except Exception as e:
                self.error( e )
                return False
        else:
            read_data = rawData
        try:
            decompressed_data = zlib.decompress(read_data)
        except Exception as e:
            self.error( e )
            return False
        else:
            return self.onLoad(decompressedData=decompressed_data)

    def onLoad(self, decompressedData):
        """
        Called on data model loading
        """
        raise Exception('To reimplement')