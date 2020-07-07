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
Test data module
"""

from ea.libs.FileModels import GenericModel
from ea.libs.PyXmlDict import Dict2Xml as PyDictXml
from ea.libs.PyXmlDict import Xml2Dict as PyXmlDict
import sys
import datetime
import re

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


r = re.compile(
    u"[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\xFF\u0100-\uD7FF\uE000-\uFDCF\uFDE0-\uFFFD]")


def removeInvalidXML(string):
    """
    Remove invalid XML
    """
    def replacer(m):
        """
        return empty string
        """
        return ""
    return re.sub(r, replacer, string)


DEFAULT_MODE = 'Raw'


def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val


class DataModel(GenericModel.GenericModel):
    """
    Data model for test data
    """

    def __init__(self, userName='unknown', testData=''):
        """
        This class describes the model of one script document,
        and provides a xml <=> python encoder
        The following xml :
        <?xml version="1.0" encoding="utf-8" ?>
            <file>
                <properties">
                    <descriptions>
                        <description>
                            <key>author</key>
                            <value>...</value>
                        </description>
                        <description>
                            <key>creation date</key>
                            <value>...</value>
                        </description>
                        <description>
                            <key>summary</key>
                            <value>...</value>
                        </description>
                    </descriptions>
                    <parameters>
                        <parameter>
                            <name>...</name>
                            <type>...</type>
                            <description>...</description>
                            <value>...</value>
                        </parameter>
                    </parameters>
                </properties>
                <testdata>...</testdata>
            </file>
        """
        GenericModel.GenericModel.__init__(self)

        today = datetime.datetime.today()
        self.dateToday = today.strftime("%d/%m/%Y %H:%M:%S")
        self.currentUser = userName

        # init xml codec
        self.codecX2D = PyXmlDict.Xml2Dict()
        self.codecD2X = PyDictXml.Dict2Xml(coding=None)

        # files properties
        self.properties = {'properties': {
            'descriptions': {
                'description': [
                    {'key': 'author', 'value': self.currentUser},
                    {'key': 'creation date', 'value': self.dateToday},
                    {'key': 'summary',
                     'value': 'Just a basic sample.'},
                    {'key': 'data mode',
                     'value': DEFAULT_MODE}
                ]
            },
            'inputs-parameters': {
                'parameter': [{'type': 'str', 'name': 'PARAM1',
                               'description': '', 'value': 'Sample',
                               'color': '', 'scope': 'local'}]
            }
        }
        }

        self.testdata = testData

    def toXml(self):
        """
        Python data to xml

        @return:
        @rtype:
        """
        try:
            self.fixPyXML(
                data=self.properties['properties']['inputs-parameters'],
                key='parameter')

            xmlDataList = ['<?xml version="1.0" encoding="utf-8" ?>']
            xmlDataList.append('<file>')
            if sys.version_info > (3,):  # python3 support
                xmlDataList.append(
                    bytes2str(
                        self.codecD2X.parseDict(
                            dico=self.properties)))
            else:
                xmlDataList.append(
                    self.codecD2X.parseDict(
                        dico=self.properties))
            xmlDataList.append(
                '<testdata><![CDATA[%s]]></testdata>' %
                unicode(
                    self.testdata))
            xmlDataList.append('</file>')
            ret = '\n'.join(xmlDataList)

            # remove all invalid xml data
            ret = removeInvalidXML(ret)
        except Exception as e:
            self.error("TestData > To Xml %s" % str(e))
            ret = None
        return ret

    def fixParameterstoUTF8(self):
        """
        Fix encodage not pretty....
        """
        for param in self.properties['properties']['inputs-parameters']['parameter']:
            param['value'] = param['value'].decode("utf-8")
            param['description'] = param['description'].decode("utf-8")
            param['name'] = param['name'].decode("utf-8")

    def fixDescriptionstoUTF8(self):
        """
        Fix encodage not pretty....
        """
        for descr in self.properties['properties']['descriptions']['description']:
            descr['key'] = descr['key'].decode("utf-8")

            if isinstance(descr['value'], dict):
                pass
            else:
                descr['value'] = descr['value'].decode("utf-8")

    def setTestData(self, testData):
        """
        Set test data
        """
        self.testdata = testData

    def onLoad(self, decompressedData):
        """
        Called on data model loading
        """
        # reset properties
        self.testdata = ""
        decodedStatus = False

        # decode content
        try:
            # Extract xml from the file data
            ret = self.codecX2D.parseXml(xml=decompressedData)
        except Exception as e:
            self.error("TestData > Parse Xml %s" % str(e))
        else:
            try:
                if sys.version_info > (3,):  # python3 support
                    # Extract test definition and test execution
                    self.testdata = ret['file']['testdata']
                else:
                    # Extract test definition and test execution
                    self.testdata = ret['file']['testdata'].decode("utf-8")

                # Extract all properties
                if 'properties' not in ret['file']:  # new in 5.0.0
                    ret['file']['properties'] = self.properties['properties']

                properties = ret['file']['properties']
            except Exception as e:
                self.error(
                    "TestData > extract properties, testdata %s" %
                    str(e))
            else:
                try:
                    # BEGIN NEW in 5.1.0
                    if 'descriptions' in properties:
                        creationDate = None
                        creationDateIndex = None
                        i = -1
                        for kv in properties['descriptions']['description']:
                            i += 1
                            if kv['key'] == 'date':
                                creationDate = kv['value']
                                creationDateIndex = i
                        if creationDate is not None:
                            properties['descriptions']['description'].pop(
                                creationDateIndex)
                            properties['descriptions']['description'].append(
                                {'key': 'creation date', 'value': creationDate})
                    # END NEW in 5.1.0

                    # BEGIN NEW in 8.0.0
                    if 'descriptions' in properties:
                        dataMode = False
                        for kv in properties['descriptions']['description']:
                            if kv['key'] == 'data mode':
                                dataMode = True
                        if not dataMode:
                            properties['descriptions']['description'].append(
                                {'key': 'data mode', 'value': DEFAULT_MODE})
                    # END NEW in 8.0.0

                except Exception as e:
                    self.error(
                        "TestData > fix backward compatibility %s" %
                        str(e))
                else:
                    try:
                        # BEGIN NEW in 5.1.0 : replace parameters by
                        # intput-parameters in the model file, to keep the
                        # compatibility
                        if 'inputs-parameters' not in properties:
                            properties['inputs-parameters'] = properties['parameters']
                            properties.pop('parameters')
                        # END NEW in 5.1.0

                        self.fixXML(
                            data=properties['inputs-parameters'],
                            key='parameter')
                        if '@parameter' in properties['inputs-parameters']:
                            self.fixXML(
                                data=properties['inputs-parameters'],
                                key='@parameter')

                        self.fixXML(
                            data=properties['descriptions'],
                            key='description')
                        if '@description' in properties['descriptions']:
                            self.fixXML(
                                data=properties['descriptions'],
                                key='@description')

                    except Exception as e:
                        self.error("TestData >  fix xml %s" % str(e))
                    else:
                        try:
                            self.properties = {'properties': properties}
                            if sys.version_info < (3,):  # python3 support
                                self.fixDescriptionstoUTF8()
                                self.fixParameterstoUTF8()
                        except Exception as e:
                            self.error("TestData >  fix utf8 %s" % str(e))
                        else:
                            decodedStatus = True
        return decodedStatus
