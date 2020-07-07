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
Test plan module
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

try:
    xrange
except NameError:  # support python3
    xrange = range


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

IF_OK = "0"
IF_KO = "1"


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
    Data model for test plan
    """

    def __init__(self, userName='unknown', defLibrary='', defAdapter='',
                 isGlobal=False, timeout="10.0", inputs=[], outputs=[]):
        """
        Data model for test plan

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
                        </probe>
                    </probes>
                </properties>
                <testplan id="0">
                    <testfile>
                        <id>1</id>
                        <parent>0</parent>
                        <file>/../../..</file>
                        <enable>2|0</enable>
                        <type>local</type>
                        <extension>tsx|tux</extension>
                        <description></description>
                        <alias>....</<alias>
                        <properties">
                            <parameters>
                                <parameter>
                                    <name>...</name>
                                    <type>...</type>
                                    <description>...</description>
                                    <value>...</value>
                                </parameter>
                            </parameters>
                            <probes>
                                <probe>
                                    <active>...</active>
                                    <args>...</args>
                                    <name>...</name>
                                </probe>
                            </probes>
                        </properties>
                    </testfile>
                    <testfile>
                        ...
                    </testfile>
                </testplan>
            </file>
        """
        GenericModel.GenericModel.__init__(self)
        today = datetime.datetime.today()
        self.dateToday = today.strftime("%d/%m/%Y %H:%M:%S")
        self.currentUser = userName
        self.defLibrary = defLibrary
        self.defAdapter = defAdapter
        self.isGlobal = isGlobal

        # new in v17
        self.timeout = timeout
        self.inputs = inputs
        self.outputs = outputs
        # end of new

        self.testName = 'Scenario'
        if self.isGlobal:
            self.testName = 'Global Scenario'

        # init xml encoder
        self.codecX2D = PyXmlDict.Xml2Dict()
        self.codecD2X = PyDictXml.Dict2Xml(coding=None)

        # file content and properties
        self.testplan = {}
        self.properties = {}

        # dev duration
        self.testdev = time.time()

        self.reset()

    def reset(self):
        """
        Reset the data model
        """
        self.testplan = {
            'testplan': {
                'testfile': [],
                '@testfile': []},
            '@testplan': {
                'id': '0'}}
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
                    {'key': 'name', 'value': self.testName},
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

        self.testdev = time.time()

    def getName(self):
        """
        Returns the name from description
        """
        keyValue = ''
        for p in self.properties['properties']['descriptions']['description']:
            if p['key'] == 'name':
                keyValue = p['value']
        return keyValue

    def getProperties(self, id):
        """
        Returns properties for a specific test suite

        @param id:
        @type id:
        """
        testSuites = self.testplan['testplan']['testfile']
        for ts in testSuites:
            if ts['id'] == id:
                return ts['properties']

    def getNbChild(self, parent, all):
        """
        Return the number of child
        """
        nb = 0
        for t in all:
            if int(t['parent']) == int(parent):
                nb += 1
                nb += self.getNbChild(parent=t['id'], all=all)
        return nb

    def fixOrphan(self):
        """
        Fix orphan test
        """
        orphansDetected = []
        for i in xrange(len(self.testplan['testplan']['testfile'])):
            parentId = self.testplan['testplan']['testfile'][i]['parent']

            # find if the parent id exists on the test listing
            if int(parentId) != 0:
                parentTest = self.findTest(testId=parentId)
                if parentTest is None:
                    orphansDetected.append(i)

        # remove the
        orphansDetected.reverse()
        for orphanIndex in orphansDetected:
            orphan = self.testplan['testplan']['testfile'].pop(orphanIndex)
            del orphan

    def findTest(self, testId):
        """
        Find a test
        """
        test = None
        for t in self.testplan['testplan']['testfile']:
            if int(t["id"]) == int(testId):
                test = t
        return test

    def getSorted(self):
        """
        Returns data model sorted
        """
        # to avoid bad behaviour, remove orphan test (the parent does not
        # exist)
        self.fixOrphan()

        ret = []

        # log the initial order
        idOrder = []
        for t in self.testplan['testplan']['testfile']:
            idOrder.append({'id': t['parent'], 'parent': t['id']})
        self.trace('testplan/testglobal - internal id order: %s' % idOrder)

        for t in self.testplan['testplan']['testfile']:
            if int(t['parent']) == 0:
                ret.append(t)
            else:
                i = None
                # find the parent
                for i in xrange(len(ret)):
                    if ret[i]['id'] == t['parent']:
                        break

                if i is None:
                    ret.append(t)
                else:
                    nbChild = self.getNbChild(parent=t['parent'], all=ret)
                    ret.insert(i + nbChild + 1, t)

        # log the final order
        newOrder = []
        for t in ret:
            newOrder.append({'id': t['id'], 'parent': t['parent']})
        self.trace('testplan/testglobal - new id order: %s' % newOrder)

        return ret

    def getTestFile(self, id):
        """
        Returns a specific testsuite

        @param id:
        @type id:
        """
        testSuites = self.testplan['testplan']['testfile']
        for ts in testSuites:
            if ts['id'] == id:
                return ts

    def delTestFile(self, itemId):
        """
        Delete a specific test suite

        @param itemId:
        @type itemId:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites.pop(i)
                break

    def updateTestFile(self, itemId, testName,
                       testExtension, testDescriptions):
        """
        Update the path of the test file
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == str(itemId):
                testSuites[i]['file'] = testName
                testSuites[i]['extension'] = testExtension
                testSuites[i]['properties']['descriptions']['description'] = testDescriptions

    def updateTestFileOnly(self, itemId, testName):
        """
        Update the path of the test file
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == str(itemId):
                testSuites[i]['file'] = testName

    def updateTestFileParent(self, itemId, parentId):
        """
        Update the parent test file
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites[i]['parent'] = parentId

    def updateTestFileParentCondition(self, itemId, parentCondition):
        """
        Update the parent test file
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites[i]['parent-condition'] = parentCondition

    def mergeTestFileProperties(self, itemId, properties):
        """
        Merge properties of a specific test suite

        @param itemId:
        @type itemId:

        @param properties:
        @type properties:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == str(itemId):

                # merge inputs
                toAdd = []
                for inputDict in properties['inputs-parameters']['parameter']:
                    newInput = self.__submerge(paramName=inputDict['name'],
                                               parameters=testSuites[i]['properties']['inputs-parameters']['parameter'])
                    if not newInput:
                        toAdd.append(inputDict)
                for newParam in toAdd:
                    testSuites[i]['properties']['inputs-parameters']['parameter'].append(
                        newParam)
                properties['inputs-parameters']['parameter'] = testSuites[i]['properties']['inputs-parameters']['parameter']

                # merge outputs
                toAdd = []
                for inputDict in properties['outputs-parameters']['parameter']:
                    newInput = self.__submerge(paramName=inputDict['name'],
                                               parameters=testSuites[i]['properties']['outputs-parameters']['parameter'])
                    if not newInput:
                        toAdd.append(inputDict)
                for newParam in toAdd:
                    testSuites[i]['properties']['outputs-parameters']['parameter'].append(
                        newParam)
                properties['outputs-parameters']['parameter'] = testSuites[i]['properties']['outputs-parameters']['parameter']

    def __submerge(self, paramName, parameters):
        """
        Recursive function to merge
        """
        paramFound = False
        for inputDict in parameters:
            if inputDict['name'] == paramName:
                paramFound = True
                break
        return paramFound

    def cleartTestParameters(self, itemId):
        """
        Clear test parameters
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == str(itemId):
                inputs = testSuites[i]['properties']['inputs-parameters']['parameter']
                inputs.clear()
                outputs = testSuites[i]['properties']['outputs-parameters']['parameter']
                outputs.clear()
                return testSuites[i]['properties']
        return {}

    def cleartAllTestParameters(self):
        """
        Clear all test parameters
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            inputs = testSuites[i]['properties']['inputs-parameters']['parameter']
            inputs.clear()
            outputs = testSuites[i]['properties']['outputs-parameters']['parameter']
            outputs.clear()
        prop = {
            'descriptions': {'description': []},
            'probes': {'probe': []},
            'inputs-parameters': {'parameter': []},
            'outputs-parameters': {'parameter': []},
            'agents': {'agent': []},
        }
        return prop

    def updateTestFileProperties(self, itemId, properties):
        """
        Update properties of a specific test suite

        @param itemId:
        @type itemId:

        @param properties:
        @type properties:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == str(itemId):
                testSuites[i]['properties'] = properties

    def updateTestFileDescr(self, itemId, descr):
        """
        Update the description of a specific test suite

        @param itemId:
        @type itemId:

        @param descr:
        @type descr:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites[i]['description'] = unicode(descr)

    def updateTestFileAlias(self, itemId, alias):
        """
        Update the alias of a specific test suite

        @param itemId:
        @type itemId:

        @param descr:
        @type descr:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites[i]['alias'] = unicode(alias)

    def updateTestFileEnable(self, itemId, enableStatus):
        """
        Update the enable field of a specific test suite

        @param itemId:
        @type itemId:

        @param descr:
        @type descr:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites[i]['enable'] = str(enableStatus)

    def updateTestFileColor(self, itemId, colorValue):
        """
        Update the enable field of a specific test suite

        @param itemId:
        @type itemId:

        @param descr:
        @type descr:
        """
        testSuites = self.testplan['testplan']['testfile']
        for i in xrange(len(testSuites)):
            if testSuites[i]['id'] == itemId:
                testSuites[i]['color'] = str(colorValue)

    def insertBeforeTestFile(self, fileName, type, itemId, parentId, currentId, properties,
                             descr='', enabled=2, extension='tsx', color="", alias="",
                             parentCondition=IF_OK, control=""):
        """
        Insert test before

        @param fileName:
        @type fileName:

        @param type:
        @type type:

        @param itemId:
        @type itemId:

        @param parentId:
        @type parentId:

        @param properties:
        @type properties:

        @param descr:
        @type descr:

        @param enabled: 2=enabled / 0=disabled
        @type enabled: integer
        """
        properties.update({'file': fileName, 'enable': str(enabled),
                           'extension': extension, 'type': type, 'id': itemId,
                           'parent': parentId, 'description': descr, 'color': color,
                           'alias': alias, 'parent-condition': parentCondition, 'control': control})
        root = self.testplan['testplan']
        tsf = root['testfile']

        # find current index
        for i in xrange(len(tsf)):
            if tsf[i]['id'] == currentId:
                root['testfile'].insert(i, properties)
                break

    def insertAfterTestFile(self, fileName, type, itemId, parentId, currentId, properties,
                            descr='', enabled=2, extension='tsx', color="", alias="",
                            parentCondition=IF_OK, control=""):
        """
        Insert test after

        @param fileName:
        @type fileName:

        @param type:
        @type type:

        @param itemId:
        @type itemId:

        @param parentId:
        @type parentId:

        @param properties:
        @type properties:

        @param descr:
        @type descr:

        @param enabled: 2=enabled / 0=disabled
        @type enabled: integer
        """
        properties.update({'file': fileName, 'enable': str(enabled), 'extension': extension,
                           'type': type, 'id': itemId, 'parent': parentId, 'description': descr,
                           'color': color, 'alias': alias,
                           'parent-condition': parentCondition, 'control': control})
        root = self.testplan['testplan']
        tsf = root['testfile']

        # find current index
        for i in xrange(len(tsf)):
            if tsf[i]['id'] == currentId:
                root['testfile'].insert(i + 1, properties)
                break

    def addTestFile(self, fileName, type, itemId, parentId, properties, descr='',
                    enabled=2, extension='tsx', color="", alias="", parentCondition=IF_OK,
                    control=""):
        """
        Add test suite

        @param fileName:
        @type fileName:

        @param type:
        @type type:

        @param itemId:
        @type itemId:

        @param parentId:
        @type parentId:

        @param properties:
        @type properties:

        @param descr:
        @type descr:

        @param enabled: 2=enabled / 0=disabled
        @type enabled: integer
        """
        properties.update({'file': fileName, 'enable': str(enabled), 'extension': extension,
                           'type': type, 'id': itemId, 'parent': parentId, 'description': descr,
                           'color': color, 'alias': alias, 'parent-condition': parentCondition,
                           'control': control})
        root = self.testplan['testplan']
        if 'testfile' not in root:
            root['testfile'] = [properties]
        else:
            if not isinstance(root['testfile'], list):
                root['testfile'] = [root['testfile']]
            root['testfile'].append(properties)

    def toXml(self):
        """
        Return XML representation of the test plan
        """
        # to avoid bad errors, remove orphan test
        self.fixOrphan()

        try:
            # !!!!!!!!!!!!!!!!!!!!!!!!!!
            self.fixPyXML(data=self.testplan['testplan'], key='testfile')
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

            # BEGIN NEW in 2.0.0
            self.fixPyXML(
                data=self.properties['properties']['descriptions'],
                key='description')
            # END NEW in 2.0.0
            for ts in self.testplan['testplan']['testfile']:
                if sys.version_info < (3,):  # python3 support
                    # issue Issue 258:
                    if isinstance(ts['description'], str):
                        ts['description'] = ts['description'].decode('utf8')
                    # issue Issue 258:
                self.fixPyXML(
                    data=ts['properties']['descriptions'],
                    key='description')
                self.fixPyXML(
                    data=ts['properties']['inputs-parameters'],
                    key='parameter')
                self.fixPyXML(
                    data=ts['properties']['outputs-parameters'],
                    key='parameter')
                self.fixPyXML(data=ts['properties']['probes'], key='probe')
                self.fixPyXML(data=ts['properties']['agents'], key='agent')

            # !!!!!!!!!!!!!!!!!!!!!!!!!!
            xmlDataList = ['<?xml version="1.0" encoding="utf-8" ?>']
            xmlDataList.append('<file>')
            if sys.version_info > (3,):  # python3 support
                xmlDataList.append(
                    bytes2str(
                        self.codecD2X.parseDict(
                            dico=self.properties)))
                xmlDataList.append(
                    bytes2str(
                        self.codecD2X.parseDict(
                            dico=self.testplan)))
            else:
                xmlDataList.append(
                    self.codecD2X.parseDict(
                        dico=self.properties))
                xmlDataList.append(self.codecD2X.parseDict(dico=self.testplan))
            xmlDataList.append(
                '<testdevelopment>%s</testdevelopment>' %
                unicode(
                    self.testdev))
            xmlDataList.append('</file>')

            ret = '\n'.join(xmlDataList)

            # remove all invalid xml data
            ret = removeInvalidXML(ret)

        except Exception as e:
            self.error("TestPlan > To Xml %s" % str(e))
            ret = None

        return ret

    def fixParameterstoUTF8(self, val):
        """
        Fix encodage not pretty....

        @param val:
        @type val:
        """
        for param in val:
            param['value'] = param['value'].decode("utf-8")
            param['description'] = param['description'].decode("utf-8")
            param['name'] = param['name'].decode("utf-8")

    def fixDescriptionstoUTF8(self, val):
        """
        Fix encodage not pretty....

        @param val:
        @type val:
        """
        for descr in val:
            descr['key'] = descr['key'].decode("utf-8")

            if isinstance(descr['value'], dict):
                pass
            else:
                descr['value'] = descr['value'].decode("utf-8")

    def onLoad(self, decompressedData):
        """
        Called on data model loading
        """
        # reset properties
        self.properties = {}
        self.testplan = {}
        decodedStatus = False

        # decode content
        try:
            # Extract xml from the file data
            ret = self.codecX2D.parseXml(xml=decompressedData)
        except Exception as e:
            self.error("TestPlan > Parse Xml %s" % str(e))
        else:
            try:
                testplan = ret['file']['testplan']
                properties = ret['file']['properties']

                if sys.version_info > (3,):  # python3 support
                    if isinstance(testplan, bytes):
                        testplan = ''

                # BEGIN NEW in 5.2.0
                if 'testsuite' in testplan:
                    testplan['testfile'] = testplan['testsuite']
                    testplan.pop('testsuite')

                if '@testsuite' in testplan:
                    testplan['@testfile'] = testplan['@testsuite']
                    testplan.pop('@testsuite')
                # END NEW

                # BEGIN NEW in 5.1.0 :
                if 'testdevelopment' not in ret['file']:
                    self.testdev = time.time()
                else:
                    if sys.version_info > (3,):  # python3 support
                        self.testdev = ret['file']['testdevelopment']
                    else:
                        self.testdev = ret['file']['testdevelopment'].decode(
                            "utf-8")
                # END NEW in 5.1.0

            except Exception as e:
                self.error(
                    "TestPlan > extract properties, testplan %s" %
                    str(e))
            else:
                try:
                    # BEGIN NEW in 2.0.0: description and can be missing model
                    # file
                    tpl_def = {'description': [{'key': 'author', 'value': ''}, {'key': 'date', 'value': ''},
                                               {'key': 'summary', 'value': ''}, {'key': 'prerequisites', 'value': ''}]}
                    if 'descriptions' not in properties:
                        properties['descriptions'] = tpl_def

                    if not len(testplan):
                        testplan = {'testfile': [], '@testfile': []}

                    if isinstance(testplan['testfile'], dict):
                        testplan['testfile'] = [testplan['testfile']]

                    for i in xrange(len(testplan['testfile'])):
                        if 'descriptions' not in testplan['testfile'][i]['properties']:
                            testplan['testfile'][i]['properties']['descriptions'] = tpl_def
                    # END NEW in 2.0.0

                    # NEW in 13.0.0
                    if 'descriptions' in properties:
                        foundPrerequis = False
                        foundRequirement = False
                        foundComments = False
                        foundLibraries = False
                        foundAdapters = False
                        foundState = False
                        creationDate = None
                        foundTestname = False
                        for kv in properties['descriptions']['description']:
                            if kv['key'] == 'prerequisites':
                                foundPrerequis = True
                            if kv['key'] == 'requirement':
                                foundRequirement = True
                            if kv['key'] == 'comments':
                                foundComments = True
                            if kv['key'] == 'libraries':
                                foundLibraries = True
                            if kv['key'] == 'adapters':
                                foundAdapters = True
                            if kv['key'] == 'date':
                                creationDate = kv['value']
                            if kv['key'] == 'state':
                                foundState = True
                            if kv['key'] == 'name':
                                foundTestname = True

                        if not foundPrerequis:
                            properties['descriptions']['description'].append(
                                {'key': 'prerequisites', 'value': ''})
                        if not foundRequirement:
                            properties['descriptions']['description'].append(
                                {'key': 'requirement', 'value': 'REQ_01'})
                        if not foundComments:
                            properties['descriptions']['description'].append(
                                {'key': 'comments', 'value': {'comments': {'comment': []}}})

                        if not foundLibraries:
                            properties['descriptions']['description'].append(
                                {'key': 'libraries', 'value': self.defLibrary})
                        if not foundAdapters:
                            properties['descriptions']['description'].append(
                                {'key': 'adapters', 'value': self.defAdapter})
                        if not foundState:
                            properties['descriptions']['description'].append(
                                {'key': 'state', 'value': 'Writing'})
                        if creationDate is not None:
                            properties['descriptions']['description'].insert(
                                1, {'key': 'creation date', 'value': creationDate})
                        if not foundTestname:
                            properties['descriptions']['description'].append(
                                {'key': 'name', 'value': self.testName})

                    # END NEW in 13.0.0

                    # to keep the compatibility
                    if 'outputs-parameters' not in properties:
                        properties['outputs-parameters'] = {
                            'parameter': copy.deepcopy(DEFAULT_OUTPUTS)}

                    if 'inputs-parameters' not in properties:
                        properties['inputs-parameters'] = properties['parameters']
                        properties.pop('parameters')

                    if 'agents' not in properties:
                        properties['agents'] = {
                            'agent': copy.deepcopy(DEFAULT_AGENTS)}

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
                        "TestPlan > fix backward compatibility: %s" %
                        str(e))
                else:
                    try:
                        if isinstance(testplan, str) or isinstance(
                                testplan, bytes):  # python3 support
                            testplan = {'testfile': [], '@testfile': []}

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

                        # BEGIN NEW in 2.0.0
                        self.fixXML(
                            data=properties['descriptions'],
                            key='description')
                        if '@description' in properties['descriptions']:
                            self.fixXML(
                                data=properties['descriptions'],
                                key='@description')
                        # END NEW in 2.0.0

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

                        self.fixXML(data=testplan, key='testfile')
                        self.fixXML(data=testplan, key='@testfile')

                        for ts in testplan['testfile']:

                            if 'extension' in ts:
                                if ts['extension'] == 'tux':
                                    foundTestname = False
                                    foundRequirement = False
                                    for kv in ts['properties']['descriptions']['description']:
                                        if kv['key'] == 'name':
                                            foundTestname = True
                                        if kv['key'] == 'requirement':
                                            foundRequirement = True
                                    if not foundTestname:
                                        ts['properties']['descriptions']['description'].append(
                                            {'key': 'name', 'value': 'TESTCASE'})
                                    if not foundRequirement:
                                        ts['properties']['descriptions']['description'].append(
                                            {'key': 'requirement', 'value': 'REQ_01'})

                            if 'alias' not in ts:
                                ts['alias'] = ''
                            if 'color' not in ts:
                                ts['color'] = ''

                            # BEGIN NEW in 6.0.0 : output-parameters  can be
                            # missing in the model file, to keep the
                            # compatibility
                            if 'agents'not in ts['properties']:
                                ts['properties']['agents'] = {
                                    'agent': copy.deepcopy(DEFAULT_AGENTS)}
                            # END NEW in 6.0.0

                            # bug fix in 10.1
                            if ts['properties']['agents'] == '':
                                ts['properties']['agents'] = {
                                    'agent': [], '@agent': []}

                            # BEGIN NEW in 9.0.0 :
                            if isinstance(ts['properties']
                                          ['agents']['agent'], dict):
                                ts['properties']['agents']['agent'] = [
                                    ts['properties']['agents']['agent']]
                            for agt in ts['properties']['agents']['agent']:
                                if 'type' not in agt:
                                    agt.update({'type': ''})
                            # END NEW in 9.0.0

                            # BEGIN NEW in 5.1.0 : output-parameters  can be
                            # missing in the model file, to keep the
                            # compatibility
                            if 'outputs-parameters'not in ts['properties']:
                                ts['properties']['outputs-parameters'] = {
                                    'parameter': copy.deepcopy(DEFAULT_OUTPUTS)}
                            # END NEW in 5.1.0
                            # BEGIN NEW in 5.1.0 replace parameters by
                            # intput-parameters in the model file, to keep the
                            # compatibility
                            if 'inputs-parameters'not in ts['properties']:
                                ts['properties']['inputs-parameters'] = ts['properties']['parameters']
                                ts['properties'].pop('parameters')
                            # END NEW in 5.1.0

                            # NEW in 17.0.0
                            if 'parent-condition'not in ts:
                                ts['parent-condition'] = IF_OK
                            if 'control'not in ts:
                                ts['control'] = ""
                            # END OF NEW

                            if isinstance(ts['properties']['probes'], str) or isinstance(
                                    ts['properties']['probes'], bytes):  # python3 support
                                ts['properties']['probes'] = {
                                    'probe': [], '@probe': []}

                            if isinstance(ts['properties']['inputs-parameters'], str) or isinstance(
                                    ts['properties']['inputs-parameters'], bytes):  # python3 support
                                ts['properties']['inputs-parameters'] = {
                                    'parameter': [], '@parameter': []}

                            if isinstance(ts['properties']['outputs-parameters'], str) or isinstance(
                                    ts['properties']['outputs-parameters'], bytes):  # python3 support
                                ts['properties']['outputs-parameters'] = {
                                    'parameter': [], '@parameter': []}

                            if isinstance(ts['properties']['agents'], str) or isinstance(
                                    ts['properties']['agents'], bytes):  # python3 support
                                ts['properties']['agents'] = {
                                    'agent': [], '@agent': []}

                            self.fixXML(
                                data=ts['properties']['probes'], key='probe')
                            if '@probe' in ts['properties']['probes']:
                                self.fixXML(
                                    data=ts['properties']['probes'], key='@probe')

                            self.fixXML(
                                data=ts['properties']['agents'], key='agent')
                            if '@agent' in ts['properties']['agents']:
                                self.fixXML(
                                    data=ts['properties']['agents'], key='@agent')

                            self.fixXML(
                                data=ts['properties']['inputs-parameters'],
                                key='parameter')
                            if '@parameter' in ts['properties']['inputs-parameters']:
                                self.fixXML(
                                    data=ts['properties']['inputs-parameters'], key='@parameter')

                            self.fixXML(
                                data=ts['properties']['outputs-parameters'],
                                key='parameter')
                            if '@parameter' in ts['properties']['outputs-parameters']:
                                self.fixXML(
                                    data=ts['properties']['outputs-parameters'], key='@parameter')

                            # BEGIN NEW in 19.0.0 : add missing scope
                            # parameters
                            for p in ts['properties']['inputs-parameters']['parameter']:
                                if "scope" not in p:
                                    p["scope"] = "local"
                                    p["@scope"] = {}
                            for p in ts['properties']['outputs-parameters']['parameter']:
                                if "scope" not in p:
                                    p["scope"] = "local"
                                    p["@scope"] = {}
                            # END OF NEW

                            if sys.version_info < (3,):  # python3 support
                                self.fixParameterstoUTF8(
                                    val=ts['properties']['inputs-parameters']['parameter'])
                                self.fixParameterstoUTF8(
                                    val=ts['properties']['outputs-parameters']['parameter'])
                                self.fixParameterstoUTF8(
                                    val=ts['properties']['agents']['agent'])
                                self.fixDescriptionstoUTF8(
                                    val=ts['properties']['descriptions']['description'])

                        self.properties = {'properties': properties}
                        if sys.version_info < (3,):  # python3 support
                            self.fixParameterstoUTF8(
                                val=self.properties['properties']['inputs-parameters']['parameter'])
                            self.fixParameterstoUTF8(
                                val=self.properties['properties']['outputs-parameters']['parameter'])
                            self.fixParameterstoUTF8(
                                val=self.properties['properties']['agents']['agent'])
                            self.fixDescriptionstoUTF8(
                                val=self.properties['properties']['descriptions']['description'])
                        self.testplan = {
                            'testplan': testplan,
                            '@testplan': {
                                'id': '0'}}

                    except Exception as e:
                        self.error("TestPlan > fix xml and utf8 %s" % str(e))
                    else:
                        decodedStatus = True
        return decodedStatus


#    testDatas = [
#                (
#                    [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '19', '24', '25', '26', '31', '33' ], # good value
#                    [
#                        {'id':'1', 'parent': '0'},
#                        {'id':'2', 'parent': '0'},
#                        {'id':'3', 'parent': '0'},
#                        {'id':'4', 'parent': '3'},
#                        {'id':'5', 'parent': '3'},
#                        {'id':'6', 'parent': '3'},
#                        {'id':'19', 'parent': '3'},
#                        {'id':'31', 'parent': '3'},
#                        {'id':'33', 'parent': '3'},
#                        {'id':'7', 'parent': '6'},
#                        {'id':'8', 'parent': '6'},
#                        {'id':'9', 'parent': '6'},
#                        {'id':'24', 'parent': '19'},
#                        {'id':'25', 'parent': '19'},
#                        {'id':'26', 'parent': '19'},
#                    ]
#                ),
#                (
#                    [ '47', '48', '49', '50', '51', '52', '53', '54', '55', '65', '58', '59', '60', '61', '66', '62', '63' ], # good value
#                    [
#                        {'id':'47', 'parent': '0'},
#                        {'id':'48', 'parent': '0'},
#                        {'id':'49', 'parent': '0'},
#                        {'id':'50', 'parent': '49'},
#                        {'id':'51', 'parent': '49'},
#                        {'id':'52', 'parent': '49'},
#                        {'id':'65', 'parent': '49'},
#                        {'id':'53', 'parent': '52'},
#                        {'id':'54', 'parent': '52'},
#                        {'id':'55', 'parent': '52'},
#                        {'id':'58', 'parent': '49'},
#                        {'id':'66', 'parent': '49'},
#                        {'id':'59', 'parent': '58'},
#                        {'id':'60', 'parent': '58'},
#                        {'id':'61', 'parent': '58'},
#                        {'id':'62', 'parent': '49'},
#                        {'id':'63', 'parent': '49'},
#                    ]
#                ),
#                (
#                    [ '47', '48', '49', '50', '51', '52', '53', '54', '55', '65', '67', '68', '58', '59', '60', '61', '66', '62', '63' ], # good value
#                    [
#                        {'id':'47', 'parent':'0' },
#                        {'id':'48', 'parent':'0' },
#                        {'id':'49', 'parent':'0' },
#                        {'id':'50', 'parent':'49' },
#                        {'id':'51', 'parent':'49' },
#                        {'id':'52', 'parent':'49' },
#                        {'id':'65', 'parent':'49' },
#                        {'id':'53', 'parent':'52' },
#                        {'id':'54', 'parent':'52' },
#                        {'id':'55', 'parent':'52' },
#                        {'id':'58', 'parent':'49' },
#                        {'id':'66', 'parent':'49' },
#                        {'id':'59', 'parent':'58' },
#                        {'id':'60', 'parent':'58' },
#                        {'id':'61', 'parent':'58' },
#                        {'id':'62', 'parent':'49' },
#                        {'id':'63', 'parent':'49' },
#                        {'id':'67', 'parent':'65' },
#                        {'id':'68', 'parent':'65' }
#                    ]
#                ),
#                (
#                    [ '1', '2', '3', '4', '5', '10', '11', '12', '13', '15', '16', '17', '18', '19', '20' ], # good value
#                    [
#                        {'id': '1', 'parent': '0'},
#                        {'id': '2', 'parent': '0'},
#                        {'id': '3', 'parent': '0'},
#                        {'id': '4', 'parent': '3'},
#                        {'id': '5', 'parent': '3'},
#                        {'id': '10', 'parent': '3'},
#                        {'id': '11', 'parent': '10'},
#                        {'id': '12', 'parent': '10'},
#                        {'id': '13', 'parent': '10'},
#                        {'id': '15', 'parent': '3'},
#                        {'id': '16', 'parent': '15'},
#                        {'id': '17', 'parent': '15'},
#                        {'id': '18', 'parent': '15'},
#                        {'id': '19', 'parent': '3'},
#                        {'id': '20', 'parent': '3'}
#                    ]
#                ),
#                ]
