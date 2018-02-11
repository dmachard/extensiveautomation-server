#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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
Test unit module
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

import Libs.PyXmlDict.Xml2Dict as PyXmlDict
import Libs.PyXmlDict.Dict2Xml as PyDictXml
try:
    from . import GenericModel # python3 support
except ImportError:   
    try:
        import GenericModel
    except ImportError as e:# import for server side
        import Libs.FileModels.GenericModel as GenericModel

import datetime
import time
import copy
import re

r = re.compile( u"[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\xFF\u0100-\uD7FF\uE000-\uFDCF\uFDE0-\uFFFD]")
def removeInvalidXML(string):
    """
    Remove invalid XML
    """
    def replacer(m):
        """
        return empty string
        """
        return ""
    return re.sub(r,replacer,string)

DEFAULT_INPUTS = [ {'type': 'bool', 'name': 'DEBUG', 'description': '', 'value' : 'False', 'color': '' }, 
                    {'type': 'float', 'name': 'TIMEOUT', 'description': '', 'value' : '1.0', 'color': '' },
                    {'type': 'bool', 'name': 'VERBOSE', 'description': '', 'value' : 'True', 'color': '' }  ]
DEFAULT_OUTPUTS = [ {'type': 'float', 'name': 'TIMEOUT', 'description': '', 'value' : '1.0', 'color': '' } ]
DEFAULT_AGENTS = [ { 'name': 'AGENT', 'description': '', 'value' : 'agent-dummy01', 'type': 'dummy' } ]

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
    Data model for test abstract
    """
    def __init__ (self, userName='unknown', testDef='', defLibrary='', defAdapter='', timeout="10.0", inputs=[], outputs=[]):
        """
        This class describes the model of one script document, and provides a xml <=> python encoder
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
                    <agents>
                        <agent>
                            <name>...</name>
                            <type>...</type>
                            <description>...</description>
                            <value>...</value>
                        </agent>
                    </agents>
                </properties>
                <testdefinition>...</testdefinition>
            </file>
        """
        GenericModel.GenericModel.__init__(self)

        today = datetime.datetime.today()
        self.dateToday = today.strftime("%d/%m/%Y %H:%M:%S")  
        self.currentUser = userName
        self.defLibrary = defLibrary
        self.defAdapter = defAdapter
        self.timeout = timeout # new in v17
        
        # init xml encoder
        self.codecX2D = PyXmlDict.Xml2Dict( )
        self.codecD2X = PyDictXml.Dict2Xml( coding = None )
        
        # files properties
        self.properties = { 'properties': {
                                    'descriptions': {
                                        'description': [ 
                                                { 'key': 'author', 'value': self.currentUser },
                                                { 'key': 'creation date', 'value':  self.dateToday },
                                                { 'key': 'summary', 'value': 'Just a basic sample.' },
                                                { 'key': 'prerequisites', 'value': 'None.' },
                                                { 'key': 'comments', 'value': { 'comments': { 'comment': [] } } },
                                                { 'key': 'libraries', 'value': self.defLibrary },
                                                { 'key': 'adapters', 'value': self.defAdapter },
                                                { 'key': 'state', 'value': 'Writing' },
                                                { 'key': 'name', 'value': 'TESTCASE' },
                                                { 'key': 'requirement', 'value': 'REQ_01' },
                                                ] },
                                    'probes': {
                                        'probe': [  { 'active': 'False', 'args': '', 'name': 'probe01', 'type': 'default'} ]
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
            if p["name"] == "TIMEOUT": p["value"] = self.timeout           
        for p in self.properties["properties"]["outputs-parameters"]["parameter"]:
            if p["name"] == "TIMEOUT": p["value"] = self.timeout
            
        if len(inputs):
            self.properties["properties"]["inputs-parameters"]["parameter"] = inputs
        if len(outputs):
            self.properties["properties"]["outputs-parameters"]["parameter"] = outputs
        # end of new
        
        
        self.steps = { 'steps': { 'step': [] } }
        self.adapters = { 'adapters': { 'adapter': [] } }
        self.libraries = { 'libraries': { 'library': [] } }
        self.actions = { 'actions': { 'action': [] } }
        self.aborted = { 'aborted': { 'abort': [] } }

        # file contents
        self.testdef = testDef
        
        # dev duration
        self.testdev = time.time()

    def setSteps(self, steps):
        """
        Set steps
        """
        self.steps['steps']['step'] = steps

    def setAdapters(self, adapters):
        """
        Set adapters
        """
        self.adapters['adapters']['adapter'] = adapters

    def setLibraries(self, libraries):
        """
        Set libraries
        """
        self.adapters['libraries']['library'] = libraries

    def setActions(self, actions):
        """
        Set actions
        """
        self.actions['actions']['action'] = actions

    def setAborted(self, aborted):
        """
        Set aborted
        """
        self.aborted['aborted']['abort'] = aborted

    def toXml (self):
        """
        Python data to xml
        
        @return: 
        @rtype:
        """
        try:
            self.fixPyXML( data = self.properties['properties']['inputs-parameters'], key = 'parameter' )
            self.fixPyXML( data = self.properties['properties']['outputs-parameters'], key = 'parameter' )
            self.fixPyXML( data = self.properties['properties']['probes'], key = 'probe' )
            self.fixPyXML( data = self.properties['properties']['agents'], key = 'agent' )
            
            xmlDataList = [ '<?xml version="1.0" encoding="utf-8" ?>' ]
            xmlDataList.append('<file>')
            if sys.version_info > (3,): # python3 support
                xmlDataList.append( bytes2str(self.codecD2X.parseDict( dico = self.properties )) )
            else:
                xmlDataList.append( self.codecD2X.parseDict( dico = self.properties ) )

            # fix dict
            if '@step' in  self.steps['steps']:
                if len(self.steps['steps']['@step']) != len(self.steps['steps']['step']):
                    stp = []
                    for p in self.steps['steps']['step']:
                        stp.append( {} )
                    self.steps['steps']['@step'] = stp

            # print("here3")
            if '@adapter' in  self.adapters['adapters']:
                if len(self.adapters['adapters']['@adapter']) != len(self.adapters['adapters']['adapter']):
                    adp = []
                    for p in self.adapters['adapters']['adapter']:
                        adp.append( {} )
                    self.adapters['adapters']['@adapter'] = adp

            if '@library' in  self.libraries['libraries']:
                if len(self.libraries['libraries']['@library']) != len(self.libraries['libraries']['library']):
                    lib = []
                    for p in self.libraries['libraries']['library']:
                        lib.append( {} )
                    self.libraries['libraries']['@library'] = lib

            if '@action' in  self.actions['actions']:
                if len(self.actions['actions']['@action']) != len(self.actions['actions']['action']):
                    act = []
                    for p in self.actions['actions']['action']:
                        act.append( {} )
                    self.actions['actions']['@action'] = act

            if '@abort' in  self.aborted['aborted']:
                if len(self.aborted['aborted']['@abort']) != len(self.aborted['aborted']['abort']):
                    abrt = []
                    for p in self.aborted['aborted']['abort']:
                        abrt.append( {} )
                    self.aborted['aborted']['@abort'] = abrt

            # convert dict/list to xml
            if sys.version_info > (3,): # python3 support
                xmlDataList.append('<teststeps>%s</teststeps>' % bytes2str(self.codecD2X.parseDict( dico = self.steps )) )
                xmlDataList.append('<testadapters>%s</testadapters>' % bytes2str(self.codecD2X.parseDict( dico = self.adapters )) )
                xmlDataList.append('<testlibraries>%s</testlibraries>' % bytes2str(self.codecD2X.parseDict( dico = self.libraries )) )
                xmlDataList.append('<testactions>%s</testactions>' % bytes2str(self.codecD2X.parseDict( dico = self.actions )) )
                xmlDataList.append('<testaborted>%s</testaborted>' % bytes2str(self.codecD2X.parseDict( dico = self.aborted )) )
            else:
                xmlDataList.append('<teststeps>%s</teststeps>' % self.codecD2X.parseDict( dico = self.steps ) )
                xmlDataList.append('<testadapters>%s</testadapters>' % self.codecD2X.parseDict( dico = self.adapters ) )
                xmlDataList.append('<testlibraries>%s</testlibraries>' % self.codecD2X.parseDict( dico = self.libraries ) )
                xmlDataList.append('<testactions>%s</testactions>' % self.codecD2X.parseDict( dico = self.actions ) )
                xmlDataList.append('<testaborted>%s</testaborted>' % self.codecD2X.parseDict( dico = self.aborted ) )

            xmlDataList.append('<testdefinition><![CDATA[%s]]></testdefinition>' % unicode(self.testdef) )
            xmlDataList.append('<testdevelopment>%s</testdevelopment>' % unicode(self.testdev) )
            xmlDataList.append('</file>')

            ret = '\n'.join(xmlDataList)

            # remove all invalid xml data
            ret = removeInvalidXML(ret)
        except Exception as e:
            self.error( "TestAbstract > To Xml %s" % str(e) ) 
            ret = None

        return ret

    def fixStringtoUTF8(self):
        """
        Fix encodage not pretty....
        """
        pass
        
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
                
            if isinstance( descr['value'], dict):
                pass
            else:
                descr['value'] = descr['value'].decode("utf-8")

    def setTestDef(self, testDef):
        """
        Set the test definition
        """
        self.testdef = testDef

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
            ret = self.codecX2D.parseXml( xml = decompressedData )
        except Exception as e:
            self.error( "TestAbstract > Parse Xml %s" % str(e) )
        else:
            try:
                if sys.version_info > (3,):  # python3 support
                   # Extract test definition and test execution
                    self.testdef = ret['file']['testdefinition']
                    self.testdev = ret['file']['testdevelopment']
                else:
                    # Extract test definition and test execution
                    self.testdef = ret['file']['testdefinition'].decode("utf-8")
                    self.testdev = ret['file']['testdevelopment'].decode("utf-8")

                # Tests def
                self.steps = ret['file']['teststeps']
                self.adapters = ret['file']['testadapters']
                self.libraries = ret['file']['testlibraries']
                self.actions = ret['file']['testactions']
                self.aborted = ret['file']['testaborted']

                # Extract all properties
                properties = ret['file']['properties']
                
            except Exception as e:
                self.error( "TestAbstract > extract properties, test definition and execution: %s" % str(e) )
            else:
                try:
                    # NEW in 13.0.0
                    if 'descriptions' in properties:
                        foundRequirement = False
                        for kv in properties['descriptions']['description']:
                            if kv['key'] == 'requirement': foundRequirement = True
                        if not foundRequirement:
                            properties['descriptions']['description'].append( {'key': 'requirement', 'value': 'REQ_01'} )
                             
                    # END OF NEW
                except Exception as e:
                    self.error( "TestAbstract > fix backward compatibility %s" % str(e) )
                else:
                    try:
                        # old fix
                        if type(properties['probes']) == str or type(properties['probes']) == bytes:# python3 support
                            properties['probes'] = { 'probe':[], '@probe':[] }

                        if type(properties['inputs-parameters']) == str or type(properties['inputs-parameters']) == bytes:# python3 support
                            properties['inputs-parameters'] = { 'parameter':[], '@parameter':[] }

                        if type(properties['outputs-parameters']) == str or type(properties['outputs-parameters']) == bytes:# python3 support
                            properties['outputs-parameters'] = { 'parameter':[], '@parameter':[] }

                        if type(properties['agents']) == str or type(properties['agents']) == bytes:# python3 support
                            properties['agents'] = { 'agent':[], '@agent':[] }

                        self.fixXML( data = properties['probes'], key = 'probe' )
                        if '@probe' in properties['probes']:
                            self.fixXML( data = properties['probes'], key = '@probe' )

                        self.fixXML( data = properties['agents'], key = 'agent' )
                        if '@agent' in properties['agents']:
                            self.fixXML( data = properties['agents'], key = '@agent' )

                        self.fixXML( data = properties['inputs-parameters'], key = 'parameter' )
                        if '@parameter' in properties['inputs-parameters']:
                            self.fixXML( data = properties['inputs-parameters'], key = '@parameter' )

                        self.fixXML( data = properties['outputs-parameters'], key = 'parameter' )
                        if '@parameter' in properties['outputs-parameters']:
                            self.fixXML( data = properties['outputs-parameters'], key = '@parameter' )

                        self.fixXML( data = properties['descriptions'], key = 'description' )
                        if '@description' in properties['descriptions']:
                            self.fixXML( data = properties['descriptions'], key = '@description' )

                        ##### fix xml steps #####
                        if type(self.steps['steps']) == str or type(self.steps['steps']) == bytes:# python3 support
                            self.steps['steps'] = { 'step':[], '@step':[] }
                        self.fixXML( data = self.steps['steps'], key = 'step' )

                        if type(self.steps['steps']['step']) == str or type(self.steps['steps']['step']) == bytes:# python3 support
                            self.steps['steps'] = { 'step':[], '@step':[] }
                        for act in self.steps['steps']['step']:
                            if 'data' in act:
                                if type(act['data']) == str or type(act['data']) == bytes:# python3 support
                                    act['data'] = { 'obj':[], '@obj':[] }

                                if 'obj' not in act['data']:
                                    act['data']['obj'] = []
                                    act['data']['@obj'] = []
                                self.fixXML( data = act['data'], key = 'obj' )

                        ##### fix xml adapters #####
                        if type(self.adapters['adapters']) == str or type(self.adapters['adapters']) == bytes:# python3 support
                            self.adapters['adapters'] = { 'adapter':[], '@adapter':[] }
                        self.fixXML( data = self.adapters['adapters'], key = 'adapter' )

                        if type(self.adapters['adapters']['adapter']) == str or type(self.adapters['adapters']['adapter']) == bytes:# python3 support
                            self.adapters['adapters'] = { 'adapter':[], '@adapter':[] }
                        for act in self.adapters['adapters']['adapter']:
                            if 'data' in act:
                                if type(act['data']) == str or type(act['data']) == bytes:# python3 support
                                    act['data'] = { 'obj':[], '@obj':[] }
                                
                                if 'obj' not in act['data']:
                                    act['data']['obj'] = []
                                    act['data']['@obj'] = []
                                self.fixXML( data = act['data'], key = 'obj' )

                        ##### fix xml libraries #####
                        if type(self.libraries['libraries']) == str or type(self.libraries['libraries']) == bytes: # python3 support
                            self.libraries['libraries'] = { 'library':[], '@library':[] }
                        self.fixXML( data = self.libraries['libraries'], key = 'library' )

                        if type(self.libraries['libraries']['library']) == str or  type(self.libraries['libraries']['library']) == bytes: # python3 support
                            self.libraries['libraries'] = { 'library':[], '@library':[] }
                        for act in self.libraries['libraries']['library']:
                            if 'data' in act:
                                if type(act['data']) == str or type(act['data']) == bytes: # python3 support
                                    act['data'] = { 'obj':[], '@obj':[] }
                                
                                if 'obj' not in act['data']:
                                    act['data']['obj'] = []
                                    act['data']['@obj'] = []
                                self.fixXML( data = act['data'], key = 'obj' )

                        ##### fix xml actions #####
                        if type(self.actions['actions']) == str or type(self.actions['actions']) == bytes: # python3 support
                            self.actions['actions'] = { 'action':[], '@action':[] }
                        self.fixXML( data = self.actions['actions'], key = 'action' )

                        if type(self.actions['actions']['action']) == str or  type(self.actions['actions']['action']) == bytes: # python3 support
                            self.actions['actions'] = { 'action':[], '@action':[] }

                        for act in self.actions['actions']['action']:
                            if 'data' in act['item-data']:
                                if type(act['item-data']['data']) == str or type(act['item-data']['data']) == bytes : # python3 support
                                    act['item-data']['data'] = { 'obj':[], '@obj':[] }
                                if 'obj' not in act['item-data']['data']:
                                    act['item-data']['data']['obj'] = []
                                    act['item-data']['data']['@obj'] = []
                                self.fixXML( data = act['item-data']['data'], key = 'obj' )

                        if sys.version_info < (3,):  # python3 support 
                            for act in self.actions['actions']['action']:
                                if 'data' in act['item-data']:
                                    for par in act['item-data']['data']['obj']:
                                        if par['selected-type'] in ['string', 'label']:
                                            par['value'] = par['value'].decode('utf8')

                        ##### fix xml aborted #####
                        if type(self.aborted['aborted']) == str or type(self.aborted['aborted']) == bytes: # python3 support
                            self.aborted['aborted'] = { 'abort':[], '@abort':[] }
                        self.fixXML( data = self.aborted['aborted'], key = 'abort' )

                        if type(self.aborted['aborted']['abort']) == str or type(self.aborted['aborted']['abort']) == bytes: # python3 support
                            self.aborted['aborted'] = { 'abort':[], '@abort':[] }
                        for act in self.aborted['aborted']['abort']:
                            if 'data' in act:
                                if type(act['data']) == str or type(act['data']) == bytes: # python3 support
                                    act['data'] = { 'obj':[], '@obj':[] }

                                if 'obj' not in act['data']:
                                    act['data']['obj'] = []
                                    act['data']['@obj'] = []
                                self.fixXML( data = act['data'], key = 'obj' )

                    except Exception as e:
                        self.error( "TestAbstract >  fix xml: %s" % str(e) )
                    else:
                        try:
                            self.properties = { 'properties':  properties}
                            if sys.version_info < (3,): # python3 support
                                self.fixDescriptionstoUTF8()
                                self.fixParameterstoUTF8()
                        except Exception as e:
                            self.error( "TestAbstract >  fix utf8 %s" % str(e) )
                        else:
                            decodedStatus = True
        return decodedStatus