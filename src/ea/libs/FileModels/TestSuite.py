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
Test suite module
"""

from ea.libs.FileModels import GenericModel
from ea.libs.PyXmlDict import Dict2Xml as PyDictXml
from ea.libs.PyXmlDict import Xml2Dict as PyXmlDict
import sys
import datetime
import time
import copy
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


DEFAULT_INPUTS = [{'type': 'bool', 'name': 'DEBUG', 'description': '',
                   'value': 'False', 'color': '', 'scope': 'local'},
                  {'type': 'float', 'name': 'TIMEOUT', 'description': '',
                   'value': '1.0', 'color': '', 'scope': 'local'},
                  {'type': 'bool', 'name': 'VERBOSE', 'description': '',
                   'value': 'True', 'color': '', 'scope': 'local'}]
DEFAULT_OUTPUTS = [{'type': 'float', 'name': 'TIMEOUT', 'description': '',
                    'value': '1.0', 'color': '', 'scope': 'local'}]
DEFAULT_AGENTS = [{'name': 'AGENT', 'description': '',
                   'value': 'agent-dummy01', 'type': 'dummy'}]


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
    Data model for test suite
    """

    def __init__(self, userName='unknown', testDef='', testExec='',
                 defLibrary='', defAdapter='', timeout="10.0", inputs=[], outputs=[]):
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
                        <description>
                            <key>prerequisites</key>
                            <value>...</value>
                        </description>
                        <description>
                            <key>comments</key>
                            <value>
                                <comments>
                                    <comment>
                                        <author>author</author>
                                        <datetime>...</datetime>
                                        <post>...</post>
                                    </comment>
                                    ....
                                </comments>
                            </value>
                        </description>
                    </descriptions>
                    <inputs-parameters>
                        <parameter>
                            <name>...</name>
                            <type>...</type>
                            <description>...</description>
                            <value>...</value>
                        </parameter>
                    </inputs-parameters>
                    <outputs-parameters>
                        <parameter>
                            <name>...</name>
                            <type>...</type>
                            <description>...</description>
                            <value>...</value>
                        </parameter>
                    </outputs-parameters>
                    <probes>
                        <probe>
                            <active>...</active>
                            <args>...</args>
                            <name>...</name>
                            <type>...</type>
                        </probe>
                    </probes>
                </properties>
                <testdefinition>...</testdefinition>
                <testexecution>...</testexecution>
            </file>
        """
        GenericModel.GenericModel.__init__(self)

        today = datetime.datetime.today()
        self.dateToday = today.strftime("%d/%m/%Y %H:%M:%S")
        self.currentUser = userName
        self.defLibrary = defLibrary
        self.defAdapter = defAdapter

        # new in v17
        self.timeout = timeout
        self.inputs = inputs
        self.outputs = outputs
        # end of new

        # init xml encoder
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
                    {'key': 'prerequisites',
                     'value': 'None.'},
                    {'key': 'comments', 'value': {'comments': {'comment': []}}},
                    {'key': 'libraries',
                     'value': self.defLibrary},
                    {'key': 'adapters',
                     'value': self.defAdapter},
                    {'key': 'state', 'value': 'Writing'},
                    {'key': 'requirement',
                     'value': 'REQ_01'},
                ]},
            'probes': {
                'probe': [{'active': 'False', 'args': '', 'name': 'probe01', 'type': 'default'}]
            },
            'inputs-parameters': {
                'parameter': copy.deepcopy(DEFAULT_INPUTS)
            },
            'outputs-parameters': {
                'parameter': copy.deepcopy(DEFAULT_OUTPUTS)
            },
            'agents': {
                'agent': copy.deepcopy(DEFAULT_AGENTS)
            },
        }
        }

        # new in v17
        for p in self.properties["properties"]["inputs-parameters"]["parameter"]:
            if p["name"] == "TIMEOUT":
                p["value"] = self.timeout
        for p in self.properties["properties"]["outputs-parameters"]["parameter"]:
            if p["name"] == "TIMEOUT":
                p["value"] = self.timeout

        if len(self.inputs):
            self.properties["properties"]["inputs-parameters"]["parameter"] = self.inputs
        if len(self.outputs):
            self.properties["properties"]["outputs-parameters"]["parameter"] = self.outputs
        # end of new

        # file contents
        self.testdef = testDef
        self.testexec = testExec

        # dev duration
        self.testdev = time.time()

    def toXml(self):
        """
        Python data to xml

        @return:
        @rtype:
        """
        try:
            # !!!!!!!!!!!!!!!!!!!!!!!!!!
            self.fixPyXML(
                data=self.properties['properties']['inputs-parameters'],
                key='parameter')
            self.fixPyXML(
                data=self.properties['properties']['outputs-parameters'],
                key='parameter')
            self.fixPyXML(
                data=self.properties['properties']['probes'],
                key='probe')
            self.fixPyXML(
                data=self.properties['properties']['agents'],
                key='agent')
            # !!!!!!!!!!!!!!!!!!!!!!!!!!
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
                '<testdefinition><![CDATA[%s]]></testdefinition>' %
                unicode(
                    self.testdef))
            xmlDataList.append(
                '<testexecution><![CDATA[%s]]></testexecution>' %
                unicode(
                    self.testexec))
            xmlDataList.append(
                '<testdevelopment>%s</testdevelopment>' %
                unicode(
                    self.testdev))
            xmlDataList.append('</file>')

            ret = '\n'.join(xmlDataList)

            # remove all invalid xml data
            ret = removeInvalidXML(ret)

        except Exception as e:
            self.error("TestSuite > To Xml %s" % str(e))
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

        for param in self.properties['properties']['outputs-parameters']['parameter']:
            param['value'] = param['value'].decode("utf-8")
            param['description'] = param['description'].decode("utf-8")
            param['name'] = param['name'].decode("utf-8")

        for agent in self.properties['properties']['agents']['agent']:
            agent['value'] = agent['value'].decode("utf-8")
            agent['description'] = agent['description'].decode("utf-8")
            agent['name'] = agent['name'].decode("utf-8")

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

    def setTestDef(self, testDef):
        """
        Set the test definition
        """
        self.testdef = testDef

    def setTestExec(self, testExec):
        """
        Set the test execution
        """
        self.testexec = testExec

    def onLoad(self, decompressedData):
        """
        Called on load data model
        """
        # reset properties
        self.properties = {}
        self.testdef = ""
        self.testexec = ""
        decodedStatus = False

        # decode content
        try:
            # Extract xml from the file data
            ret = self.codecX2D.parseXml(xml=decompressedData)
        except Exception as e:
            self.error("TestSuite > Parse Xml %s" % str(e))
        else:
            try:
                if sys.version_info > (3,):  # python3 support
                    # Extract test definition and test execution
                    self.testdef = ret['file']['testdefinition']
                    self.testexec = ret['file']['testexecution']

                    # BEGIN NEW in 5.1.0 :
                    if 'testdevelopment'not in ret['file']:
                        self.testdev = time.time()
                    else:
                        self.testdev = ret['file']['testdevelopment']
                    # END NEW in 5.1.0
                else:
                    # Extract test definition and test execution
                    self.testdef = ret['file']['testdefinition'].decode(
                        "utf-8")
                    self.testexec = ret['file']['testexecution'].decode(
                        "utf-8")

                    # BEGIN NEW in 5.1.0 :
                    if 'testdevelopment'not in ret['file']:
                        self.testdev = time.time()
                    else:
                        self.testdev = ret['file']['testdevelopment'].decode(
                            "utf-8")
                    # END NEW in 5.1.0

                # Extract all properties
                properties = ret['file']['properties']
            except Exception as e:
                self.error(
                    "TestSuite > extract properties, test definition and execution %s" %
                    str(e))
            else:
                try:
                    # BEGIN NEW in 2.0.0 : description and can be missing model
                    # file, to keep the compatibility
                    if 'descriptions'not in properties:
                        properties['descriptions'] = {'description': [{'key': 'author', 'value': ''},
                                                                      {'key': 'date', 'value': ''},
                                                                      {'key': 'summary', 'value': ''},
                                                                      {'key': 'prerequisites', 'value': ''},
                                                                      {'key': 'requirement', 'value': ''}]}

                    # BEGIN NEW in 13.0.0
                    if 'descriptions' in properties:
                        foundLibraries = False
                        foundAdapters = False
                        creationDate = None
                        foundState = False
                        foundPrerequis = False
                        foundComments = False
                        foundRequirement = False
                        for kv in properties['descriptions']['description']:
                            if kv['key'] == 'libraries':
                                foundLibraries = True
                            if kv['key'] == 'adapters':
                                foundAdapters = True
                            if kv['key'] == 'date':
                                creationDate = kv['value']
                            if kv['key'] == 'comments':
                                foundComments = True
                            if kv['key'] == 'state':
                                foundState = True
                            if kv['key'] == 'prerequisites':
                                foundPrerequis = True
                            if kv['key'] == 'requirement':
                                foundRequirement = True

                        if not foundLibraries:
                            properties['descriptions']['description'].append(
                                {'key': 'libraries', 'value': self.defLibrary})
                        if not foundAdapters:
                            properties['descriptions']['description'].append(
                                {'key': 'adapters', 'value': self.defAdapter})
                        if not foundState:
                            properties['descriptions']['description'].append(
                                {'key': 'state', 'value': 'Writing'})
                        if not foundComments:
                            properties['descriptions']['description'].append(
                                {'key': 'comments', 'value': {'comments': {'comment': []}}})
                        if not foundPrerequis:
                            properties['descriptions']['description'].append(
                                {'key': 'prerequisites', 'value': ''})
                        if not foundRequirement:
                            properties['descriptions']['description'].append(
                                {'key': 'requirement', 'value': 'REQ_01'})

                        if creationDate is not None:
                            properties['descriptions']['description'].insert(
                                1, {'key': 'creation date', 'value': creationDate})
                    # END NEW in 13.0.0

                    # BEGIN NEW in 5.1.0 : output-parameters  can be missing in
                    # the model file, to keep the compatibility
                    if 'outputs-parameters' not in properties:
                        properties['outputs-parameters'] = {
                            'parameter': copy.deepcopy(DEFAULT_OUTPUTS)}
                    # END NEW in 5.1.0

                    # BEGIN NEW in 5.1.0 : replace parameters by
                    # intput-parameters in the model file, to keep the
                    # compatibility
                    if 'inputs-parameters' not in properties:
                        properties['inputs-parameters'] = properties['parameters']
                        properties.pop('parameters')
                    # END NEW in 5.1.0

                    # BEGIN NEW in 6.0.0 : agents  can be missing in the model
                    # file, to keep the compatibility
                    if 'agents' not in properties:
                        properties['agents'] = {
                            'agent': copy.deepcopy(DEFAULT_AGENTS)}
                    # END NEW in 6.0.0

                    # bug fix in 10.1
                    if properties['agents'] == '' or properties['agents'] == b'':  # python3 support
                        properties['agents'] = {'agent': [], '@agent': []}

                    # BEGIN NEW in 9.0.0 :
                    if isinstance(properties['agents']['agent'], dict):
                        properties['agents']['agent'] = [
                            properties['agents']['agent']]

                    for agt in properties['agents']['agent']:
                        if 'type' not in agt:
                            agt.update({'type': ''})
                    # END NEW in 9.0.0
                except Exception as e:
                    self.error(
                        "TestSuite > fix backward compatibility: %s" %
                        str(e))
                else:
                    try:
                        if isinstance(properties['probes'], str) or isinstance(
                                properties['probes'], bytes):  # python3 support
                            properties['probes'] = {'probe': [], '@probe': []}

                        if isinstance(properties['inputs-parameters'], str) or isinstance(
                                properties['inputs-parameters'], bytes):  # python3 support
                            properties['inputs-parameters'] = {
                                'parameter': [], '@parameter': []}

                        if isinstance(properties['outputs-parameters'], str) or isinstance(
                                properties['outputs-parameters'], bytes):  # python3 support
                            properties['outputs-parameters'] = {
                                'parameter': [], '@parameter': []}

                        if isinstance(properties['agents'], str) or isinstance(
                                properties['agents'], bytes):  # python3 support
                            properties['agents'] = {'agent': [], '@agent': []}

                        self.fixXML(data=properties['probes'], key='probe')
                        if '@probe' in properties['probes']:
                            self.fixXML(
                                data=properties['probes'], key='@probe')

                        self.fixXML(data=properties['agents'], key='agent')
                        if '@agent' in properties['agents']:
                            self.fixXML(
                                data=properties['agents'], key='@agent')

                        self.fixXML(
                            data=properties['inputs-parameters'],
                            key='parameter')
                        if '@parameter' in properties['inputs-parameters']:
                            self.fixXML(
                                data=properties['inputs-parameters'],
                                key='@parameter')

                        self.fixXML(
                            data=properties['outputs-parameters'],
                            key='parameter')
                        if '@parameter' in properties['outputs-parameters']:
                            self.fixXML(
                                data=properties['outputs-parameters'],
                                key='@parameter')

                        self.fixXML(
                            data=properties['descriptions'],
                            key='description')
                        if '@description' in properties['descriptions']:
                            self.fixXML(
                                data=properties['descriptions'],
                                key='@description')

                        # BEGIN NEW in 19.0.0 : add missing scope parameters
                        for p in properties['inputs-parameters']['parameter']:
                            if "scope" not in p:
                                p["scope"] = "local"
                                p["@scope"] = {}
                        for p in properties['outputs-parameters']['parameter']:
                            if "scope" not in p:
                                p["scope"] = "local"
                                p["@scope"] = {}
                        # END OF NEW
                    except Exception as e:
                        self.error("TestSuite >  fix xml %s" % str(e))
                    else:
                        try:
                            self.properties = {'properties': properties}
                            if sys.version_info < (3,):  # python3 support
                                self.fixDescriptionstoUTF8()
                                self.fixParameterstoUTF8()
                        except Exception as e:
                            self.error("TestSuite >  fix utf8 %s" % str(e))
                        else:
                            decodedStatus = True
        return decodedStatus
