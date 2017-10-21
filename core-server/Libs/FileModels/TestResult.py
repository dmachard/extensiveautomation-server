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
Test result module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
from Libs import Logger
import Libs.PyXmlDict.Xml2Dict as PyXmlDict
import Libs.PyXmlDict.Dict2Xml as PyDictXml

import zlib
import datetime
import base64
import re

r = re.compile( u"[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\xFF\u0100-\uD7FF\uE000-\uFDCF\uFDE0-\uFFFD]")
def removeInvalidXML(string):
  def replacer(m):
    return ""
  return re.sub(r,replacer,string)
  
def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val

def keyequals( key, search ):
    """
    key is equals
    """
    ret = False
    if isinstance(key, bytes):
        if str(key, 'utf8') == search:
            ret = True  
    else:
        if key == search:
            ret = True 
    return ret
    
class DataModel(Logger.ClassLogger):
    """
    Data model for test result
    """
    def __init__ (self, testResult='', testHeader=''):
        """
        This class describes the model of the test result document, and provides a xml <=> python encoder
        The following xml :
        <?xml version="1.0" encoding="utf-8" ?>
            <file>
                <properties">
                    <comments>
                        <comment>
                            <author>author</author>
                            <datetime>...</datetime>
                            <post>...</post>
                        </comment>
                        ....
                    </comments>
                </properties>
                <testheader>...</testheader>
                <testresult>...</testresult>
            </file>
        """
        today = datetime.date.today()
        #
        self.codecX2D = PyXmlDict.Xml2Dict( )
        self.codecD2X = PyDictXml.Dict2Xml( coding = None )
        #
        self.properties = { 'properties': { 'comments': { 'comment': [] } } }
        self.testresult = testResult
        self.testheader = testHeader
        
    def addComment(self, user_name, user_post, post_timestamp):
        """
        Add one comment
        """
        try:
            comments = self.properties['properties']['comments']
            tpl = {'author': user_name, 'datetime': str(post_timestamp), 'post': user_post}
            if isinstance(comments, dict):
                if isinstance( comments['comment'], list):
                    comments['comment'].append( tpl )
                else:
                    comments['comment'] = [ comments['comment'], tpl ]                  
            else:
                comments = {'comment': [tpl] }
        except Exception as e:
            self.error( "[addComment] %s" % str(e) )
            return None
        return comments

    def delComments(self):
        """
        Delete all comments
        """
        self.properties['properties']['comments'] = { 'comment': [] } 
        
    def toXml (self):
        """
        Python data to xml
        
        @return: 
        @rtype:
        """
        try:
            xmlDataList = [ '<?xml version="1.0" encoding="utf-8" ?>' ]
            xmlDataList.append('<file>')
            if sys.version_info > (3,): # python3 support
                xmlDataList.append( str(self.codecD2X.parseDict( dico = self.properties )) )
            else:
                xmlDataList.append( self.codecD2X.parseDict( dico = self.properties ) )
                
            tr = zlib.compress(self.testresult)
            xmlDataList.append('<testresult><![CDATA[%s]]></testresult>' % base64.b64encode(tr) )
            
            hdr = zlib.compress(self.testheader)
            xmlDataList.append('<testheader><![CDATA[%s]]></testheader>' % base64.b64encode(hdr) )
            
            xmlDataList.append('</file>')
            ret = '\n'.join(xmlDataList)
            
            # remove all invalid xml data
            ret = removeInvalidXML(ret)
        except Exception as e:
            self.error( "TestResult > To Xml %s" % str(e) ) 
            ret = None
        return ret

    def load (self, absPath = None, rawData = None):
        """ 
        Load data model from a file or from arguments

        @param absPath: 
        @type absPath:

        @param rawData: 
        @type rawData:
        """
        self.properties = {}
        self.testresult = ''
        
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
            self.error( "uncompress testresult error: %s" % e )
            return False
        try:
            if sys.version_info > (3,): # python3 support
                ret = self.codecX2D.parseXml( xml = bytes2str(decompressed_data), huge_tree=True  )
            else:
                ret = self.codecX2D.parseXml( xml = decompressed_data, huge_tree=True  )

            del decompressed_data
            del read_data
            
            if sys.version_info > (3,): # python3 support
                tr_decoded = base64.b64decode( bytes(ret['file']['testresult'], 'utf8') ) 
            else:
                tr_decoded = base64.b64decode( ret['file']['testresult'] ) 
            
            tr_decompressed = zlib.decompress(tr_decoded)
            if sys.version_info > (3,): # python3 support
                self.testresult = bytes2str(tr_decompressed)
            else:
                self.testresult = tr_decompressed
                
            del tr_decoded
            
            # new in v11.2
            if 'testheader' not in ret['file']: # for backward compatibility
                ret['file']['testheader'] = ''
            else:
                if sys.version_info > (3,): # python3 support
                    hdr_decoded = base64.b64decode( bytes(ret['file']['testheader'], 'utf8') ) 
                else:
                    hdr_decoded = base64.b64decode( ret['file']['testheader'] ) 
                
                hdr_decompressed = zlib.decompress(hdr_decoded)
                if sys.version_info > (3,): # python3 support
                    self.testheader = bytes2str(hdr_decompressed)
                else:
                    self.testheader = hdr_decompressed
            # end of new
            
            properties = ret['file']['properties']
            self.properties = { 'properties':  properties}
        except Exception as e:
            self.error( "[parse] %s" % str(e) )
            return False
        return True