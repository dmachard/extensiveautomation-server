#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
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

import wrapt
import sys
import copy
import re

@wrapt.decorator
def doc_public(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for documentation
    """
    return wrapped(*args, **kwargs)
    
import base64
import xlrd
import binascii
import json

__DESCRIPTION__ = """The library provides some functions to access to the properties of the test."""


class TestPropertiesException(Exception): pass

class Others(object):
    """
    """
    @doc_public
    def excel(self, data, worksheet, row=None, column=None ):
        """
        Read excel file

        @param data: excel data
        @type data: string
        
        @param worksheet: worksheet name
        @type worksheet: string
        
        @param row: row id
        @type row: integer/none
        
        @param column: column id
        @type column: integer/none
        
        @return: content
        @rtype: string/none
        """
        pass
    @doc_public
    def shared(self, project, name, subname=''):
        """
        Get one specific shared parameter by name passed as argument.

        @param project: project name
        @type project: string

        @param name: parameter name
        @type name: string

        @param subname: sub parameter name
        @type subname: string
            
        @return: parameter value
        @rtype: string, int, boolean, boolean and more
        """
        pass

class Agents(object):
    @doc_public
    def running(self, name):
        """
        Return agent according to the name passed as argument.

        @param name: agent name
        @type name: string

        @return: agent value
        @rtype: agent
        """
        pass
    @doc_public
    def agent(self, name):
        """
        Get one specific agent by name passed as argument.

        @param name: agent name
        @type name: string

        @return: agent value
        @rtype: agent
        """
        pass
    @doc_public
    def agents(self):
        """
        Returns all agents.

        @return: agents
        @rtype: list
        """
        pass

class Inputs(object):
    """
    """
    @doc_public
    def input(self, name):
        """
        Get one specific test input parameter by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int, boolean and more
        """
        pass
    @doc_public
    def setInput(name, value):
        """
        Set the value of one specific test input parameter by name passed as argument.
        Overwrite the test properties

        @param name: parameter name
        @type name: string

        @param value: parameter value
        @type name: undefined
        """
        pass
    @doc_public    
    def inputs(self):
        """
        Returns all inputs parameters.

        @return: parameters
        @rtype: list
        """
        return instance().getParameters()
    
class Outputs(object):
    """
    """  
    @doc_public
    def output(self, name):
        """
        Get one specific test output parameter by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int, boolean and more
        """
        pass
    @doc_public
    def setOutput(self, name, value):
        """
        Set the value of one specific test output parameter by name passed as argument.
        Overwrite the test properties
        
        @param name: parameter name
        @type name: string

        @param value: parameter value
        @type name: undefined
        """
        pass
    @doc_public
    def outputs(self):
        """
        Returns all outputs parameters.

        @return: parameters
        @rtype: list
        """
        pass

class Design(object):
    """
    """
    @doc_public
    def descriptions(self):
        """
        Returns all descriptions parameters.

        @return: descriptions as list
        @rtype: list
        """
        pass
    @doc_public    
    def description(self, name):
        """
        Get one specific test description by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int
        """
        pass

class SelfIP(object):
    def __init__(self, ip):
        """
        @param ip:
        @type ip: string
        """
        self.ip = ip

    def getIP(self):
        """
        Return ip
        """
        return self.ip.split(' (')[0]

class SelfMAC(object):
    def __init__(self, mac):
        """
        @param mac:
        @type mac: string
        """
        self.mac = mac

    def getMAC(self):
        """
        Return mac
        """
        return self.mac.split(' (')[0]

def decodeDescription(description):
    """
    Decode description

    @param agent: agent name
    @type agent: string
    """
    return description['value'].encode("utf-8")

def decodeAgent(agent):
    """
    Decode agent

    @param agent: agent name
    @type agent: string
    """
    agt = {}
    agt['name'] =  agent['value'].encode("utf-8")
    agt['type'] =  agent['type'].encode("utf-8")
    return agt

def decodeListShared(parameter, sharedParameters=[]):
    """
    Decode the shared parameter
    """
    parametersList = [ (i.rstrip().lstrip()).encode("utf-8") for i in parameter['value'].split(',') ]
    retList = []
    for param in parametersList:
        prjId, key = param.split(":", 1)
        # checking if project is authorized ?
        projectData = None
        for prj in sharedParameters:
            if int(prj['project_id']) == int(prjId):
                projectData = prj['test_environment']
                break
        if projectData is None:
            raise TestPropertiesException("ERR_PRO_016: list of global parameters project not authorized" )
            
        # find the main key
        mainKeyFounded = None
        for p in projectData:
            if key.upper() == p['name'].upper():
                mainKeyFounded = p
                break
        if mainKeyFounded is None:
            raise TestPropertiesException("ERR_PRO_017: list of global parameters not available: %s" % key )
        else:
            retList.append(mainKeyFounded['value'])
        
    return retList
   
def decodeExcel(data, worksheet, row=None, column=None):
    """
    Decode excel file
    """
    content = None
    
    # old file format
    try:
        wb = xlrd.open_workbook(file_contents=data)
    except Exception as e:
        raise TestPropertiesException('ERR_PRO_023: excel data not supported')

    # read sheet
    try:
        ws = wb.sheet_by_name(worksheet)
    except Exception as e:
        wb.release_resources()
        raise TestPropertiesException('ERR_PRO_024: worksheet %s does not exists on excel file' % worksheet)
    
    # read cell 
    if row is not None and column is not None:
        col = ws.col_values( int(column) )
        content = col[ int(row) ]
        
    # read column
    elif row is None and column is not None:
        content = ws.col_values( int(column) )
        
    # read row
    elif row is not None and column is None:
        content = ws.row_values( int(row) )
        
    # other case
    else:
        wb.release_resources()
        raise TestPropertiesException('ERR_PRO_025: column or row ID are missing')
    
    wb.release_resources()
    
    return content   

def readListShared(parameter, sharedParameters=[]):
    """
    """
    parametersList = [ (i.rstrip().lstrip()).encode("utf-8") for i in parameter.split(',') ]
    retList = []
    for param in parametersList:
        prjId, key = param.split(":", 1)
        
        # checking if project is authorized ?
        projectData = None
        for prj in sharedParameters:
            if int(prj['project_id']) == int(prjId):
                projectData = prj['test_environment']
                break
                
        if projectData is not None:
            # find the main key
            mainKeyFounded = None
            for p in projectData:
                if key.upper() == p['name'].upper():
                    mainKeyFounded = p
                    break
            if mainKeyFounded is not None:
                retList.append( "<br /> - %s" % mainKeyFounded['value'])
        
    return "\n".join(retList)
    
def readShared(parameter, sharedParameters=[]):
    """
    """
    projectData = None
    prjId, prjName, mainKey, secondKey = parameter.split(":")
    for prj in sharedParameters:
        if int(prj['project_id']) == int(prjId):
            projectData = prj['test_environment']
            break
    
    sharedValue = ''
    if projectData is not None:
        mainKeyFounded = None
        for param in projectData:
            if mainKey.upper() == param['name'].upper():
                mainKeyFounded = param
                break
                
        if mainKeyFounded is not None:
            # not second key
            if not len(secondKey):
                if isinstance(mainKeyFounded['value'], str) or isinstance(mainKeyFounded['value'], unicode):
                    sharedValue = mainKeyFounded['value'].encode("utf-8")
                else:
                    sharedValue = mainKeyFounded['value']

            # find the second key
            else:
                secondKeyFounded = None
                try:
                    #  mainKeyFounded = {'name': 'TEST', 'value': {u'active': False, u'ip': u'test'}}
                    for k,v in mainKeyFounded['value'].items():
                        if secondKey.upper() == k.upper():
                            secondKeyFounded = v
                            break
                except Exception as e:
                    pass
                if secondKeyFounded is not None:
                    if isinstance(secondKeyFounded, str) or isinstance(secondKeyFounded, unicode):
                        sharedValue = secondKeyFounded.encode("utf-8")
                    else:
                        sharedValue =  secondKeyFounded
    
    return sharedValue

def decodeShared(parameter, sharedParameters=[], projectName=None, separator=">", exception=True):
    """
    Decode the shared parameter
    """
    # search the project
    projectData = None
    if projectName is not None:
        prjId, prjName, mainKey, secondKey = parameter.split(":")
        for prj in sharedParameters:
            if prj['project_name'] == projectName:
                projectData = prj['test_environment']
                break
    else:
        prjId, prjName, mainKey, secondKey = parameter['value'].split(":")
        for prj in sharedParameters:
            print( "<> %s" % prj )
            if int(prj['project_id']) == int(prjId):
                projectData = prj['test_environment']
                break

    if projectData is None:
        if exception:
            raise TestPropertiesException("ERR_PRO_016: global parameter project not authorized: %s (Id=%s)" % (prjName, prjId) )
        else:
            return '' 
    else:
        # find the main key
        mainKeyFounded = None
        for param in projectData:
            if mainKey.upper() == param['name'].upper():
                mainKeyFounded = param
                break
        if mainKeyFounded is None:
            if exception:
                raise TestPropertiesException("ERR_PRO_017: global parameter not available: %s" % mainKey )
            else:
                return ''
        else:
            # not second key
            if not len(secondKey):
                if isinstance(mainKeyFounded['value'], str) or isinstance(mainKeyFounded['value'], unicode):
                    return mainKeyFounded['value'].encode("utf-8")
                else:
                    return mainKeyFounded['value']

            # find the second key
            else:
                secondKeyFounded = None
                try:
                    #  mainKeyFounded = {'name': 'TEST', 'value': {u'active': False, u'ip': u'test'}}
                    for k,v in mainKeyFounded['value'].items():
                        if secondKey.upper() == k.upper():
                            secondKeyFounded = v
                            break
                except Exception as e:
                    pass
                if secondKeyFounded is None:
                    if exception:
                        raise TestPropertiesException("ERR_PRO_018: shared parameter not available: %s>%s" % (mainKey,secondKey) )
                    else:
                        return ''
                else:
                    if isinstance(secondKeyFounded, str) or isinstance(secondKeyFounded, unicode):
                        return secondKeyFounded.encode("utf-8")
                    else:
                        return secondKeyFounded

def decodeParameter(parameter, sharedParameters=[]):
    """
    Decode parameter

    @param parameter: parameter name
    @type parameter: string

    @param sharedParameters: 
    @type sharedParameters: list
    """
    if parameter['type'] == "none":
        return None

    elif parameter['type'] == "python":
        return parameter['value']
        
    elif parameter['type'] in [ "shared", "global" ]:
        return decodeShared(parameter=parameter, sharedParameters=sharedParameters)

    elif parameter['type'] in [ "list-shared", "list-global" ]:
        if len(parameter['value']):
            return decodeListShared(parameter=parameter, sharedParameters=sharedParameters)
        else:
            return []
            
    elif parameter['type'] == "json":
        custom_tmp = custom_json(parameter['value'].encode("utf-8"))
        j = {}
        try:
            j = json.loads(custom_tmp)
        except Exception as e:
            raise TestPropertiesException( 'ERR_PRO_001: invalid json provided: %s' % str(e) )
        return j
        
    elif parameter['type'] == "custom":
        return custom_text(parameter['value'].encode("utf-8"))
        
    elif parameter['type'] == "text":
        return custom_text(parameter['value'].encode("utf-8"))
        
    # elif parameter['type'] == "json":
        # j = {}
        # try:
            # j = json.loads(parameter['value'].encode("utf-8"))
        # except Exception as e:
            # raise TestPropertiesException( 'ERR_PRO_001: invalid json provided: %s' % str(e) )
        # return j
        
    elif parameter['type'] == "alias":
        return parameter['value'].encode("utf-8")

    elif parameter['type'] == "str":
        return parameter['value'].encode("utf-8")
        
    # elif parameter['type'] == "text":
        # return parameter['value'].encode("utf-8")

    elif parameter['type'] == "cache":
        return cache(parameter['value'].encode("utf-8"))
        
    elif parameter['type'] == "hex":
        if len(parameter['value']) % 2: 
            parameter['value'] = parameter['value'].zfill(len(parameter['value'])+1)
        return binascii.unhexlify(parameter['value'])
        
    elif parameter['type'] == "pwd":
        return parameter['value'].encode("utf-8")

    elif parameter['type'] == "int":
        try:
            return int(parameter['value'])
        except ValueError as e:
            raise TestPropertiesException( 'ERR_PRO_001: bad int value in input (%s=%s)' % (parameter['name'],parameter['value']) )
            
    elif parameter['type'] == "float":
        try:
            parameter['value'] = parameter['value'].replace(",", ".")
            return float(parameter['value'])
        except ValueError as e:
            raise TestPropertiesException( 'ERR_PRO_002: bad float value in input (%s=%s)' % (parameter['name'],parameter['value']) )
            
    elif parameter['type'] == "list":
        if len(parameter['value']):
            return [ (i.rstrip().lstrip()).encode("utf-8") for i in parameter['value'].split(',') ]
        else:
            return []

    elif parameter['type'] == "bool":
        return eval(parameter['value'])

    elif parameter['type'] == "date":
        return str( parameter['value'] )

    elif parameter['type'] == "time":
        return str( parameter['value'] )

    elif parameter['type'] == "date-time":
        return str( parameter['value'] )

    elif parameter['type'] == "self-ip":
        return SelfIP(ip=parameter['value']).getIP()

    elif parameter['type'] == "self-eth":
        return parameter['value']

    elif parameter['type'] == "self-mac":
        return SelfMAC(mac=parameter['value']).getMAC()

    elif parameter['type'] == "dataset":
        return parameter['value']

    elif parameter['type'] == "remote-image":
        return parameter['value']

    elif parameter['type'] == "local-image":
        return base64.b64decode(parameter['value']) 
        
    elif parameter['type'] == "local-file":
        try:
            fName, fSize, fData = parameter['value'].split(":", 2)
            return base64.b64decode(fData) 
        except Exception as e:
            return ""
        
    elif parameter['type'] == "snapshot-image":
        return base64.b64decode(parameter['value']) 

    else:
        raise TestPropertiesException( 'ERR_PRO_001: parameter type unknown: %s' % str(parameter['type']) )

def decodeValue(parameter, value):
    """
    Decode the value
    """
    if parameter['type'] == "none":
        return None

    elif parameter['type'] in [ "shared", "global" ]:
        if isinstance(value, dict): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "alias":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "str":
        if isinstance(value, str) or isinstance(value, unicode): return value.decode("utf-8")
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "text":
        if isinstance(value, str) or isinstance(value, unicode): return value.decode("utf-8")
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "custom":
        if isinstance(value, str) or isinstance(value, unicode): return value.decode("utf-8")
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "cache":
        if isinstance(value, str) or isinstance(value, unicode): return value.decode("utf-8")
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "pwd":
        if isinstance(value, str) or isinstance(value, unicode): return value.decode("utf-8")
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "int":
        if isinstance(value, int): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "float":
        if isinstance(value, float): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "list":
        if isinstance(value, list): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "bool":
        if isinstance(value, bool): return "%s" % value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "date":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "time":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "date-time":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "self-ip":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "self-eth":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "self-mac":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "dataset":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "remote-image":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    elif parameter['type'] == "local-image":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "local-file":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )
        
    elif parameter['type'] == "snapshot-image":
        if isinstance(value, str) or isinstance(value, unicode): return value
        raise TestPropertiesException( 'ERR_PRO_XXX: bad value: %s' % value )

    else:
        raise TestPropertiesException( 'ERR_PRO_001: parameter type unknown: %s' % str(parameter['type']) )
    
class Properties:
    def __init__(self, parameters, descriptions, parametersOut, 
                 agents, parametersShared, 
                 runningAgents=[], runningProbes=[]):
        """
        """
        self.__parameters = parameters
        self.__parametersOut = parametersOut
        self.__descriptions = descriptions
        self.__agents = agents
        self.__parametersShared = parametersShared
        
        # new in v10.1
        self.__running_agents = runningAgents
        self.__running_probes = runningProbes
        
    def initAtRunTime(self, cache=None):
        """
        new in v19
        """
        try:
            if cache is not None:
                for p in self.__parameters:
                    if p["scope"] == "cache" and cache.get(name=p["name"]) is None:
                        tmp_v = decodeParameter(p, sharedParameters=self.__parametersShared)
                        cache.set(name=p["name"], data=tmp_v)
                        if p["type"] == "json" and isinstance(tmp_v, dict):
                            for k,v in tmp_v.items():
                                cache.set(name="%s_%s" % (p["name"], k), data=v)
                            
                for p in self.__parametersOut:
                    if p["scope"] == "cache" and cache.get(name=name_upper) is None:
                        tmp_v = decodeParameter(p, sharedParameters=self.__parametersShared)
                        cache.set(name=p["name"], data=tmp_v)
                        if p["type"] == "json" and isinstance(tmp_v, dict):
                            for k,v in tmp_v.items():
                                cache.set(name="%s_%s" % (p["name"], k), data=v)
                            
        except Exception as e:
            raise TestPropertiesException( 'ERR_PRO_100: bad json parameter provided - %s' % e )

    def readShared(self, shared):
        """
        @return: parameter value
        @rtype: string, list, int
        """
        return readShared(parameter=shared , 
                          sharedParameters=self.__parametersShared)
        
    def readListShared(self, shared):
        """
        @return: parameter value
        @rtype: string, list, int
        """
        return readListShared(parameter=shared , 
                              sharedParameters=self.__parametersShared)
        
    def getRunningAgents(self):
        """
        Return running agents
        """
        return self.__running_agents
        
    def getRunningProbes(self):
        """
        Return running probes
        """
        return self.__running_probes
        
    def getAgents(self):
        """
        Return agents
        """
        return self.__agents
        
    def getAgents(self):
        """
        Return agents
        """
        return self.__agents

    def getParameters(self):
        """
        Return parameters
        """
        return self.__parameters

    def getParametersOut(self):
        """
        Return out parameters
        """
        return self.__parametersOut

    def getParametersShared(self):
        """
        Return shared parameters
        """
        return self.__parametersShared

    def getDescriptions(self):
        """
        Return description
        """
        return self.__descriptions
        
class Descriptions:
    def __init__(self):
        """
        This class enables to get parameters defined in the test.
        """
        self.__descriptions = instance().getDescriptions()

    def get(self, name):
        """
        Get one specific test config by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int
        """
        if name.lower() == 'comments':
            return ''

        try:
            for descr in self.__descriptions:
                if descr['key'] == name.lower():
                    if sys.version_info > (3,):
                        return descr['value']
                    else:
                        return descr['value'].encode("utf-8")
        except Exception:
            return ''
        raise TestPropertiesException('ERR_PRO_002: Description key "%s" not available' % name)

class Parameters:
    def __init__(self):
        """
        This class enables to get parameters defined in the test.
        """
        self.__parameters = instance().getParameters()
        self.__parametersOut = instance().getParametersOut()
        self.__parametersShared = instance().getParametersShared()
        self.__agents = instance().getAgents()
        # new in v10.1
        self.__running_agents = instance().getRunningAgents()
        self.__running_probes = instance().getRunningProbes()
        # new in v16
        self.__descriptions = instance().getDescriptions()
     
    def excel(self, data, worksheet, row=None, column=None):
        """
        """
        return decodeExcel(data, worksheet, row=row, column=column)
        
    def running(self, name):
        """
        Return running agents according to the name passed as argument
        """
        agentAvailable = None
        for agt in self.__running_agents:
            if agt['id'] == name:
                agentAvailable = { 'type': agt['type'].lower(), 'name': name}
        if agentAvailable is not None:
            return agentAvailable
        else:
            raise TestPropertiesException( 'ERR_PRO_022: agent=%s is not running!' % name )
        
    def agents(self):
        """
        Return agents
        """
        return self.__agents
    
    def inputs(self):
        """
        Return inputs
        """
        return self.__parameters
    
    def outputs(self):
        """
        Return outputs
        """
        return self.__parametersOut
    
    def descriptions(self):
        """
        Return descriptions
        """
        return self.__descriptions

    def agent(self, name):
        """
        Get one specific test config by name passed as argument.

        @param name: agent name
        @type name: string

        @return: agent value
        @rtype: agent
        """
        for agt in self.__agents:
            if agt['name'] == name:
                if agt['type'] == 'alias':
                    if agt['value'] == name:
                        raise TestPropertiesException('ERR_PRO_005: Invalid agent alias "%s"' % agt['value'])
                    return self.agent(name=agt['value'])
                else:
                    return decodeAgent(agent=agt)
        raise TestPropertiesException('ERR_PRO_003: Agent "%s" from test config not available' % name)

    def input_type(self, name):
        """
        Return the type of a input parameter
        
        @return: parameter type
        @rtype: string
        """
        for pr in self.__parameters:
            if pr['name'] == name:
                return pr['type']
                
    def output_type(self, name):
        """
        Return the type of a input parameter
        
        @return: parameter type
        @rtype: string
        """
        for pr in self.__parametersOut:
            if pr['name'] == name:
                return pr['type']
                
    def input(self, name):
        """
        Get one specific test config by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int
        """
        for pr in self.__parameters:
            if pr['name'] == name:
                if pr['type'] == 'alias':
                    if pr['value'] == name:
                        raise TestPropertiesException('ERR_PRO_005: Invalid input alias "%s"' % pr['value'])
                    return self.input(name=pr['value'])
                else:
                    return decodeParameter(parameter=pr, sharedParameters=self.__parametersShared)
        raise TestPropertiesException('ERR_PRO_004: Input parameter "%s" not available' % name)

    def output(self, name):
        """
        Get one specific test config by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int
        """
        for pr in self.__parametersOut:
            if pr['name'] == name:
                if pr['type'] == 'alias':
                    if pr['value'] == name:
                        raise TestPropertiesException('ERR_PRO_007: Invalid output alias "%s"' % pr['value'])
                    return self.output(name=pr['value'])
                else:
                    return decodeParameter(parameter=pr, sharedParameters=self.__parametersShared)
        raise TestPropertiesException('ERR_PRO_006: Output parameter "%s" not available' % name)

    def setInput(self, name, value):
        """
        Set input value
        """
        paramFounded = False
        for pr in self.__parameters:
            if pr['name'] == name:
                paramFounded = True
                pr['value'] = decodeValue(parameter=pr,value=value)
                break
        if not paramFounded:
            raise TestPropertiesException('ERR_PRO_020: Input parameter "%s" not available' % name)
            
    def setOutput(self, name, value):
        """
        Set output value
        """
        paramFounded = False
        for pr in self.__parametersOut:
            if pr['name'] == name:
                paramFounded = True
                pr['value'] = decodeValue(parameter=pr,value=value)
                break
        if not paramFounded:
            raise TestPropertiesException('ERR_PRO_019: Output parameter "%s" not available' % name)

    def shared(self, project, name, subname=''):
        """
        Get one specific test config by name passed as argument.
        
        @param project: project name
        @type project: string
        
        @param name: parameter name
        @type name: string
        
        @param subname: sub parameter name
        @type subname: string
        
        @return: parameter value
        @rtype: string, list, int
        """
        return decodeShared(parameter="::%s:%s" % (name,subname) , 
                            sharedParameters=self.__parametersShared, 
                            projectName=project)

    def data(self):
        """
        """
        ret = []
        for d in self.__parameters:
            if d['name'].startswith('DATA_'):
                ret.append( d )
        return ret
        
    def sut(self):
        """
        """
        ret = []
        for d in self.__parameters:
            if d['name'].startswith('SUT_'):
                ret.append( d )
        return ret

    def dataOut(self):
        """
        """
        ret = []
        for d in self.__parametersOut:
            if d['name'].startswith('DATA_'):
                ret.append( d )
        return ret
        
    def sutOut(self):
        """
        """
        ret = []
        for d in self.__parametersOut:
            if d['name'].startswith('SUT_'):
                ret.append( d )
        return ret
        
class NotFound(object): pass

class TestPlanParameters(object):
    def __init__(self):
        """
        """
        self.__parameters = {}
        self.__parametersOut = {}
        self.__agents = {}
        self.__descriptions = {}
        self.__parametersShared = []
        # new in v10.1
        self.__running_agents = []
        self.__running_probes = []
        # new in v19
        self.__cache = None
     
    def excel(self, data, worksheet, row=None, column=None):
        """
        """
        return decodeExcel(data, worksheet, row=row, column=column)
        
    def initAtRunTime(self, cache=None):
        """
        new in v19
        """
        self.__cache = cache
        
    def updateAtRunTime(self, param_id, params_all):
        """
        """
        try:
            if self.__cache is not None:
                for p in params_all[param_id]:
                    if p["scope"] == "cache" and self.__cache.get(name=p["name"]) is None:
                        tmp_v = decodeParameter(p, sharedParameters=self.__parametersShared)
                        self.__cache.set(name=p["name"], data=tmp_v)
                        if p["type"] == "json" and isinstance(tmp_v, dict):
                            for k,v in tmp_v.items():
                                self.__cache.set(name="%s_%s" % (p["name"], k), data=v)            
        except Exception as e:
            raise TestPropertiesException( 'ERR_PRO_100: bad json parameter provided - %s' % e )

    def getAgents(self):
        """
        Return agents
        """
        return self.__agents

    def getDescriptions(self):
        """
        Return descriptions
        """
        return self.__descriptions

    def getParameters(self):
        """
        Return parameters in
        """
        return self.__parameters

    def getParametersOut(self):
        """
        Return parameters out
        """
        return self.__parametersOut

    def addDescriptions(self, descriptionsId, descriptions):
        """
        Add descriptions

        @param descriptionsId: 
        @type descriptionsId: 

        @param descriptions: 
        @type descriptions: 
        """
        self.__descriptions[descriptionsId] = descriptions

    def addRunningAgents(self, agents):
        """
        Add running agents 
        
        @param agents: 
        @type agents: 
        """
        self.__running_agents = agents

    def addRunningProbes(self, probes):
        """
        Add running probes 
        
        @param probes: 
        @type probes: 
        """
        self.__running_probes = probes
        
    def addAgents(self, agentsId, agents):
        """
        Add agents 

        @param agentsId: 
        @type agentsId: 

        @param agents: 
        @type agents: 
        """
        self.__agents[agentsId] = agents

    def addParameters(self, parametersId, parameters):
        """
        Add parameters

        @param parametersId: 
        @type parametersId: 

        @param parameters: 
        @type parameters: 
        """
        self.__parameters[parametersId] = parameters
        
        self.updateAtRunTime(param_id=parametersId, params_all=self.__parameters)

    def addParametersOut(self, parametersId, parameters):
        """
        Add parameter out

        @param parametersId: 
        @type parametersId: 

        @param parameters: 
        @type parameters: 
        """
        self.__parametersOut[parametersId] = parameters
        
        self.updateAtRunTime(param_id=parametersId, params_all=self.__parametersOut)

    def addParametersShared(self, parameters):
        """
        Add parameter shared

        @param parameters: 
        @type parameters: 
        """
        self.__parametersShared = parameters

    def running(self, name):    
        """
        Return agent according to the name passed as argument
        """
        agentAvailable = None
        for agt in self.__running_agents:
            if agt['id'] == name:
                agentAvailable = { 'type': agt['type'].lower(), 'name': name}
        if agentAvailable is not None:
            return agentAvailable
        else:
            raise TestPropertiesException( 'ERR_PRO_022: agent=%s is not running!' % name )
        
    def agents(self, tpId, tsId):
        """
        Agents
        """
        for agtId, agtVal in self.__agents.items():
            if agtId == tsId:
                return agtVal

    def inputs(self, tpId, tsId):
        """
        Inputs
        """
        for prId, prVal in self.__parameters.items():
            if prId == tsId:
                return prVal
    
    def outputs(self, tpId, tsId):
        """
        Outputs
        """
        for prId, prVal in self.__parametersOut.items():
            if prId == tsId:
                return prVal
    
    def descriptions(self, tpId, tsId):
        """
        Outputs
        """
        for descrId, descrVal in self.__descriptions.items():
            if descrId == tsId:
                return descrVal
                
    def description(self, name, tpId, tsId):
        """
        Return description

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 

        @param tsId: 
        @type tsId: 
        """
        if name.lower() == 'comments':
            return ''
        for descrId, descrVal in self.__descriptions.items():
            if descrId == tsId:
                for descr in descrVal:
                    if descr['key'] == name.lower():
                        return descr['value'].encode("utf-8")
        raise TestPropertiesException('ERR_PRO_008: Description "%s" not available' % name)

    def agent(self, name, tpId, tsId):
        """
        Return agent

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 

        @param tsId: 
        @type tsId: 
        """
        for agtId, agtVal in self.__agents.items():
            if agtId == tsId:
                for agt in agtVal:
                    if agt['name'] == name:
                        # overwrite the parameter if present in main parameter
                        ret = self.getAgentFromMain(name, tpId)
                        if ret is not None:
                            return ret
                        else:
                            if agt['type'] == 'alias':
                                if agt['value'] == name:
                                    raise TestPropertiesException('ERR_PRO_011: Invalid agent alias "%s"' % agt['value'])
                                return self.agent(name=agt['value'],tpId=tpId, tsId=tsId)
                            else:
                                return decodeAgent(agent=agt)
        raise TestPropertiesException('ERR_PRO_009: Agent "%s" from test config not available' % name)

    def parameter(self, name, tpId, tsId):
        """
        Return parameter

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 

        @param tsId: 
        @type tsId: 
        """
        for prId, prVal in self.__parameters.items():
            if prId == tsId:
                for pr in prVal:
                    if pr['name'] == name :
                        # overwrite the parameter if present in main parameter except for alias
                        if pr['type'] != "alias":
                            ret = self.getParamFromMain(name, tpId, paramType=pr['type'])
                        else:
                            ret = NotFound()
                        if not isinstance(ret, NotFound):
                            return ret
                        else:
                            if pr['type'] == 'alias':
                                if pr['value'] == name:
                                    raise TestPropertiesException('ERR_PRO_011: Invalid input alias "%s"' % pr['value'])
                                return self.parameter(name=pr['value'],tpId=tpId, tsId=tsId)
                            else:
                                return decodeParameter(parameter=pr, sharedParameters=self.__parametersShared)
        raise TestPropertiesException('ERR_PRO_010: Input parameter "%s" not available' % name)

    def parameterOut(self, name, tpId, tsId):
        """
        Return parameter out

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 

        @param tsId: 
        @type tsId: 
        """
        for prId, prVal in self.__parametersOut.items():
            if prId == tsId:
                for pr in prVal:
                    if pr['name'] == name:
                        # overwrite the parameter if present in main parameter
                        if pr['type'] != "alias":
                            ret = self.getParamOutFromMain(name, tpId, paramType=pr['type'])
                        else:
                            ret = NotFound()
                        if not isinstance(ret, NotFound):
                            return ret
                        else:
                            if pr['type'] == 'alias':
                                if pr['value'] == name:
                                    raise TestPropertiesException('ERR_PRO_013: Invalid output alias "%s"' % pr['value'])
                                return self.parameterOut(name=pr['value'],tpId=tpId, tsId=tsId)
                            else:
                                return decodeParameter(parameter=pr, sharedParameters=self.__parametersShared)

        raise TestPropertiesException('ERR_PRO_012: Output parameter "%s" not available' % name)
    
    def setParameter(self, name, value, tpId, tsId):
        """
        Return parameter

        @param name: 
        @type name: 
        
        @param value: 
        @type value: 
        
        @param tpId: 
        @type tpId: 

        @param tsId: 
        @type tsId: 
        """
        paramFounded = False
        for prId, prVal in self.__parameters.items():
            if prId == tsId:
                for pr in prVal:
                    if pr['name'] == name:
                        paramFounded = True
                        pr['value'] = decodeValue(parameter=pr,value=value)
                        break
        if not paramFounded:
            raise TestPropertiesException('ERR_PRO_022: Input parameter "%s" not available' % name)
        
    def setParameterOut(self, name, value, tpId, tsId):
        """
        Set parameter out

        @param name: 
        @type name: 
        
        @param value: 
        @type value: 
        
        @param tpId: 
        @type tpId: 

        @param tsId: 
        @type tsId: 
        """
        paramFounded = False
        for prId, prVal in self.__parametersOut.items():
            if prId == tsId:
                for pr in prVal:
                    if pr['name'] == name:
                        paramFounded = True
                        pr['value'] = decodeValue(parameter=pr,value=value)
                        break
        if not paramFounded:
            raise TestPropertiesException('ERR_PRO_021: Output parameter "%s" not available' % name)
        
    def readShared(self, shared):
        """
        @return: parameter value
        @rtype: string, list, int
        """
        return readShared(parameter=shared , sharedParameters=self.__parametersShared)
        
    def readListShared(self, shared):
        """
        @return: parameter value
        @rtype: string, list, int
        """
        return readListShared(parameter=shared , sharedParameters=self.__parametersShared)
        
    def shared(self, project, name, subname=''):
        """
        Get one specific test config by name passed as argument.

        @param name: parameter name
        @type name: string

        @return: parameter value
        @rtype: string, list, int
        """
        return decodeShared(parameter="::%s:%s" % (name,subname) , 
                            sharedParameters=self.__parametersShared, 
                            projectName=project)

    def getDescrFromMain(self, name, tpId):
        """
        Return description from main

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 
        """
        for pr in self.__descriptions[ tpId ]:
            if pr['key'] == name:
                return decodeDescription(description=pr)
        return None

    def getParamFromMain(self, name, tpId, paramType):
        """
        Return parameter from main

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 
        """
        for pr in self.__parameters[ tpId ]:
            if pr['name'] == name:
                if pr['type'] == 'alias':
                    if pr['value'] == name:
                        raise TestPropertiesException('ERR_PRO_014: Invalid main input alias "%s"' % pr['value'])
                    return self.getParamFromMain(name=pr['value'], tpId=tpId, paramType=paramType)
                else:
                    return decodeParameter(parameter=pr, sharedParameters=self.__parametersShared)
        return NotFound()

    def getParamOutFromMain(self, name, tpId, paramType):
        """
        Return out parameter from main

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 
        """
        for pr in self.__parametersOut[ tpId ]:
            if pr['name'] == name:
                if pr['type'] == 'alias':
                    if pr['value'] == name:
                        raise TestPropertiesException('ERR_PRO_015: Invalid main output alias "%s"' % pr['value'])
                    return self.getParamOutFromMain(name=pr['value'], tpId=tpId, paramType=paramType)
                else:
                    return decodeParameter(parameter=pr, sharedParameters=self.__parametersShared)
        return NotFound()

    def getSutFromMain(self, parametersId):
        """
        """
        ret = []
        for d in self.__parameters[ parametersId ]:
            if d['name'].startswith('SUT_'):
                ret.append( d )
        return ret
        
    def getDataFromMain(self, parametersId):
        """
        """
        ret = []
        for d in self.__parameters[ parametersId ]:
            if d['name'].startswith('DATA_'):
                ret.append( d )
        return ret
    
    def getSutOutFromMain(self, parametersId):
        """
        """
        ret = []
        for d in self.__parametersOut[ parametersId ]:
            if d['name'].startswith('SUT_'):
                ret.append( d )
        return ret
        
    def getDataOutFromMain(self, parametersId):
        """
        """
        ret = []
        for d in self.__parametersOut[ parametersId ]:
            if d['name'].startswith('DATA_'):
                ret.append( d )
        return ret
    
    def sut(self, tpId, tsId):
        """
        """
        # extract all parameters according to the tpid and tsid
        tsParameters = self.__parameters[tsId]

        newParams = []
        for d in tsParameters:
            toUpdate = False
            for m in self.__parameters[tpId]:
                if m['name'] == d['name']:
                    toUpdate = True
                    break
            if not toUpdate:
                newParams.append( d )
                    
        ret = []
        for d in newParams: 
            if d['name'].startswith('SUT_'):
                ret.append( d )
                
        del newParams
        return ret
        
    def data(self, tpId, tsId):
        """
        """
        # extract all parameters according to the tpid and tsid
        tsParameters = self.__parameters[tsId]
        
        newParams = []
        for d in tsParameters:
            toUpdate = False
            for m in self.__parameters[tpId]:
                if m['name'] == d['name']:
                    toUpdate = True
                    break
            if not toUpdate:
                newParams.append( d )
                
        ret = []
        for d in newParams:
            if d['name'].startswith('DATA_'):
                ret.append( d )
                
        del newParams
        return ret
    
    def sutOut(self, tpId, tsId):
        """
        """
        # extract all parameters according to the tpid and tsid
        tsParameters = self.__parametersOut[tsId]

        newParams = []
        for d in tsParameters:
            toUpdate = False
            for m in self.__parametersOut[tpId]:
                if m['name'] == d['name']:
                    toUpdate = True
                    break
            if not toUpdate:
                newParams.append( d )
                    
        ret = []
        for d in newParams: 
            if d['name'].startswith('SUT_'):
                ret.append( d )
                
        del newParams
        return ret
        
    def dataOut(self, tpId, tsId):
        """
        """
        # extract all parameters according to the tpid and tsid
        tsParameters = self.__parametersOut[tsId]
        
        newParams = []
        for d in tsParameters:
            toUpdate = False
            for m in self.__parametersOut[tpId]:
                if m['name'] == d['name']:
                    toUpdate = True
                    break
            if not toUpdate:
                newParams.append( d )
                
        ret = []
        for d in newParams:
            if d['name'].startswith('DATA_'):
                ret.append( d )
                
        del newParams
        return ret
    
    def getAgentFromMain(self, name, tpId):
        """
        Return agent from main

        @param name: 
        @type name: 

        @param tpId: 
        @type tpId: 
        """
        for agt in self.__agents[ tpId ]:
            if agt['name'] == name:
                if agt['type'] == 'alias':
                    if agt['value'] == name:
                        raise TestPropertiesException('ERR_PRO_015: Invalid main agent alias "%s"' % agt['value'])
                    return self.getAgentFromMain(name=agt['value'], tpId=tpId)
                else:
                    return decodeAgent(agent=agt)
        return None

TPL = None
custom_text = None
custom_json = None
cache = None

def instance():
    """
    Return the instance

    @return:
    @rtype:
    """
    if TPL:
        return TPL

def initialize(parameters=None, descriptions=None, 
               parametersOut=None, agents=None, 
               parametersShared=None, runningAgents=[], 
               runningProbes=[]):
    """
    Initialize the module

    @param parameters:
    @type parameters:

    @param descriptions:
    @type descriptions:
    
    @param parametersOut:
    @type parametersOut:
    
    @param agents:
    @type agents:
    
    @param parametersShared:
    @type parametersShared:
    """
    global TPL
    if parameters is None:
        TPL = TestPlanParameters()
    else:
        TPL = Properties(   parameters=parameters, descriptions=descriptions, 
                            parametersOut=parametersOut,
                            agents=agents, parametersShared=parametersShared, 
                            runningAgents=runningAgents, runningProbes=runningProbes)

def finalize():
    """
    Finalize the module
    """
    global TPL
    if TPL:
        TPL = None