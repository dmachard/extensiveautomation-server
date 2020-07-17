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

import sys
import base64
import binascii
import json

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__DESCRIPTION__ = """The library provides some functions to access to the properties of the test."""
__HELPER__ = []


class TestPropertiesException(Exception):
    pass


class SelfIP(object):
    def __init__(self, ip):
        """
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
    """
    if sys.version_info > (3,):
        return description['value']
    else:
        return description['value'].encode("utf-8")


def decodeListShared(parameter, sharedParameters=[]):
    """
    Decode the shared parameter
    """
    if sys.version_info > (3,):
        parametersList = [(i.rstrip().lstrip())
                          for i in parameter['value'].split(',')]
    else:
        parametersList = [(i.rstrip().lstrip()).encode("utf-8")
                          for i in parameter['value'].split(',')]
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
            raise TestPropertiesException(
                "ERR_PRO_016: list of global parameters project not authorized")

        # find the main key
        mainKeyFounded = None
        for p in projectData:
            if key.upper() == p['name'].upper():
                mainKeyFounded = p
                break
        if mainKeyFounded is None:
            raise TestPropertiesException(
                "ERR_PRO_017: list of global parameters not available: %s" %
                key)
        else:
            retList.append(mainKeyFounded['value'])

    return retList


def readListShared(parameter, sharedParameters=[]):
    """
    """
    if sys.version_info > (3,):
        parametersList = [(i.rstrip().lstrip()) for i in parameter.split(',')]
    else:
        parametersList = [(i.rstrip().lstrip()).encode("utf-8")
                          for i in parameter.split(',')]
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
                retList.append("<br /> - %s" % mainKeyFounded['value'])

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
                if isinstance(mainKeyFounded['value'], str) or isinstance(
                        mainKeyFounded['value'], unicode):
                    if sys.version_info > (3,):
                        sharedValue = mainKeyFounded['value']
                    else:
                        sharedValue = mainKeyFounded['value'].encode("utf-8")
                else:
                    sharedValue = mainKeyFounded['value']

            # find the second key
            else:
                secondKeyFounded = None
                try:
                    #  mainKeyFounded = {'name': 'TEST', 'value': {u'active': False, u'ip': u'test'}}
                    for k, v in mainKeyFounded['value'].items():
                        if secondKey.upper() == k.upper():
                            secondKeyFounded = v
                            break
                except Exception:
                    pass
                if secondKeyFounded is not None:
                    if isinstance(secondKeyFounded, str) or isinstance(
                            secondKeyFounded, unicode):
                        if sys.version_info > (3,):
                            sharedValue = secondKeyFounded
                        else:
                            sharedValue = secondKeyFounded.encode("utf-8")
                    else:
                        sharedValue = secondKeyFounded

    return sharedValue


def decodeShared(parameter, sharedParameters=[],
                 projectName=None, separator=">", exception=True):
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
        params = parameter['value'].split(":")
        if len(params) == 4:
            prjId, prjName, mainKey, secondKey = parameter['value'].split(":")
            for prj in sharedParameters:
                if int(prj['project_id']) == int(prjId):
                    projectData = prj['test_environment']
                    break
        else:
            if len(params) == 2:
                prjName = params[0]
                mainKey = params[1]
                secondKey = ""
                
            if len(params) == 3:
                prjName = params[0]
                mainKey = params[1]
                secondKey = params[2]
                
            for prj in sharedParameters:
                if prj['project_name'] == prjName:
                    projectData = prj['test_environment']
                    break
                
    if projectData is None:
        if exception:
            raise TestPropertiesException(
                "ERR_PRO_016: global parameter project not authorized: %s (Id=%s)" %
                (prjName, prjId))
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
                raise TestPropertiesException(
                    "ERR_PRO_017: global parameter not available: %s" %
                    mainKey)
            else:
                return ''
        else:
            # not second key
            if not len(secondKey):
                if isinstance(mainKeyFounded['value'], str) or isinstance(
                        mainKeyFounded['value'], unicode):
                    if sys.version_info > (3,):
                        return mainKeyFounded['value']
                    else:
                        return mainKeyFounded['value'].encode("utf-8")
                else:
                    return mainKeyFounded['value']

            # find the second key
            else:
                secondKeyFounded = None
                try:
                    #  mainKeyFounded = {'name': 'TEST', 'value': {u'active': False, u'ip': u'test'}}
                    for k, v in mainKeyFounded['value'].items():
                        if secondKey.upper() == k.upper():
                            secondKeyFounded = v
                            break
                except Exception:
                    pass
                if secondKeyFounded is None:
                    if exception:
                        raise TestPropertiesException(
                            "ERR_PRO_018: shared parameter not available: %s>%s" %
                            (mainKey, secondKey))
                    else:
                        return ''
                else:
                    if isinstance(secondKeyFounded, str) or isinstance(
                            secondKeyFounded, unicode):
                        if sys.version_info > (3,):
                            return secondKeyFounded
                        else:
                            return secondKeyFounded.encode("utf-8")
                    else:
                        return secondKeyFounded


def decodeParameter(parameter, sharedParameters=[]):
    """
    Decode parameter
    """
    if parameter['type'] == "none":
        return None

    elif parameter['type'] == "python":
        return parameter['value']

    elif parameter['type'] in ["shared", "global"]:
        return decodeShared(parameter=parameter,
                            sharedParameters=sharedParameters)

    elif parameter['type'] in ["list-shared", "list-global"]:
        if len(parameter['value']):
            return decodeListShared(
                parameter=parameter, sharedParameters=sharedParameters)
        else:
            return []

    elif parameter['type'] == "json":
        if custom_json is None:
            raise Exception('ERR_PRO_100: json parameter not ready')
        if sys.version_info > (3,):
            custom_tmp = custom_json(parameter['value'])
        else:
            custom_tmp = custom_json(parameter['value'].encode("utf-8"))
        j = {}
        try:
            j = json.loads(custom_tmp)
        except Exception as e:
            raise TestPropertiesException(
                'ERR_PRO_001: invalid json provided: %s' %
                str(e))
        return j

    elif parameter['type'] == "custom":
        if sys.version_info > (3,):
            return custom_text(parameter['value'])
        else:
            return custom_text(parameter['value'].encode("utf-8"))

    elif parameter['type'] == "text":
        if sys.version_info > (3,):
            return custom_text(parameter['value'])
        else:
            return custom_text(parameter['value'].encode("utf-8"))

    elif parameter['type'] == "alias":
        if sys.version_info > (3,):
            return parameter['value']
        else:
            return parameter['value'].encode("utf-8")

    elif parameter['type'] == "str":
        if sys.version_info > (3,):
            return parameter['value']
        else:
            return parameter['value'].encode("utf-8")

    elif parameter['type'] == "cache":
        if sys.version_info > (3,):
            return cache(parameter['value'])
        else:
            return cache(parameter['value'].encode("utf-8"))

    elif parameter['type'] == "hex":
        if len(parameter['value']) % 2:
            parameter['value'] = parameter['value'].zfill(
                len(parameter['value']) + 1)
        return binascii.unhexlify(parameter['value'])

    elif parameter['type'] == "pwd":
        if sys.version_info > (3,):
            return parameter['value']
        else:
            return parameter['value'].encode("utf-8")

    elif parameter['type'] == "int":
        try:
            return int(parameter['value'])
        except ValueError:
            raise TestPropertiesException(
                'ERR_PRO_001: bad int value in input (%s=%s)' %
                (parameter['name'], parameter['value']))

    elif parameter['type'] == "float":
        try:
            parameter['value'] = parameter['value'].replace(",", ".")
            return float(parameter['value'])
        except ValueError:
            raise TestPropertiesException(
                'ERR_PRO_002: bad float value in input (%s=%s)' %
                (parameter['name'], parameter['value']))

    elif parameter['type'] == "list":
        if len(parameter['value']):
            if sys.version_info > (3,):
                return [(i.rstrip().lstrip())
                        for i in parameter['value'].split(',')]
            else:
                return [(i.rstrip().lstrip()).encode("utf-8")
                        for i in parameter['value'].split(',')]
        else:
            return []

    elif parameter['type'] == "bool":
        return eval(parameter['value'])

    elif parameter['type'] == "date":
        return str(parameter['value'])

    elif parameter['type'] == "time":
        return str(parameter['value'])

    elif parameter['type'] == "date-time":
        return str(parameter['value'])

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
            _, _, fData = parameter['value'].split(":", 2)
            return base64.b64decode(fData)
        except Exception:
            return ""

    elif parameter['type'] == "snapshot-image":
        return base64.b64decode(parameter['value'])

    else:
        raise TestPropertiesException(
            'ERR_PRO_001: parameter type unknown: %s' % str(
                parameter['type']))


def decodeValue(parameter, value):
    """
    Decode the value
    """
    if parameter['type'] == "none":
        return None

    elif parameter['type'] in ["shared", "global"]:
        if isinstance(value, dict):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "alias":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "str":
        if isinstance(value, str) or isinstance(value, unicode):
            if sys.version_info < (3,):
                return value.decode("utf-8")
            else:
                return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "text":
        if isinstance(value, str) or isinstance(value, unicode):
            if sys.version_info < (3,):
                return value.decode("utf-8")
            else:
                return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "custom":
        if isinstance(value, str) or isinstance(value, unicode):
            if sys.version_info < (3,):
                return value.decode("utf-8")
            else:
                return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "cache":
        if isinstance(value, str) or isinstance(value, unicode):
            if sys.version_info < (3,):
                return value.decode("utf-8")
            else:
                return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "pwd":
        if isinstance(value, str) or isinstance(value, unicode):
            if sys.version_info < (3,):
                return value.decode("utf-8")
            else:
                return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "int":
        if isinstance(value, int):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "float":
        if isinstance(value, float):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "list":
        if isinstance(value, list):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "bool":
        if isinstance(value, bool):
            return "%s" % value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "date":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "time":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "date-time":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "self-ip":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "self-eth":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "self-mac":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "dataset":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "remote-image":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "local-image":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "local-file":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    elif parameter['type'] == "snapshot-image":
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TestPropertiesException('ERR_PRO_XXX: bad value: %s' % value)

    else:
        raise TestPropertiesException(
            'ERR_PRO_001: parameter type unknown: %s' % str(
                parameter['type']))


class Properties:
    def __init__(self, parameters,
                 descriptions,
                 parametersShared,
                 runningAgents=[],
                 ):
        """
        """
        self.__parameters = parameters
        self.__descriptions = descriptions
        self.__parametersShared = parametersShared
        self.__running_agents = runningAgents

    def initAtRunTime(self, cache=None):
        """
        new in v19
        """
        try:
            if cache is not None:
                for p in self.__parameters:
                    if p["scope"] == "cache" and cache.get(
                            name=p["name"]) is None:
                        tmp_v = decodeParameter(
                            p, sharedParameters=self.__parametersShared)
                        cache.set(name=p["name"], data=tmp_v)
                        if p["type"] == "json" and isinstance(tmp_v, dict):
                            for k, v in tmp_v.items():
                                cache.set(
                                    name="%s_%s" %
                                    (p["name"], k), data=v)
        except Exception as e:
            raise TestPropertiesException(
                'ERR_PRO_100: bad json provided - %s ' % (e))

    def readShared(self, shared):
        """
        @return: parameter value
        @rtype: string, list, int
        """
        return readShared(parameter=shared,
                          sharedParameters=self.__parametersShared)

    def readListShared(self, shared):
        """
        """
        return readListShared(parameter=shared,
                              sharedParameters=self.__parametersShared)

    def getRunningAgents(self):
        """
        Return running agents
        """
        return self.__running_agents

    def getParameters(self):
        """
        Return parameters
        """
        return self.__parameters

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
        raise TestPropertiesException(
            'ERR_PRO_002: Description key "%s" not available' %
            name)


class Parameters:
    def __init__(self):
        """
        This class enables to get parameters defined in the test.
        """
        self.__parameters = instance().getParameters()
        self.__parametersShared = instance().getParametersShared()
        self.__running_agents = instance().getRunningAgents()
        self.__descriptions = instance().getDescriptions()

    def running(self, name):
        """
        Return running agents according to the name passed as argument
        """
        agentAvailable = None
        for agt in self.__running_agents:
            if agt['id'] == name:
                agentAvailable = {'type': agt['type'].lower(), 'name': name}
        if agentAvailable is not None:
            return agentAvailable
        else:
            raise TestPropertiesException(
                'ERR_PRO_022: agent=%s is not running!' % name)

    def inputs(self):
        """
        Return inputs
        """
        return self.__parameters

    def descriptions(self):
        """
        Return descriptions
        """
        return self.__descriptions

    def input_type(self, name):
        """
        Return the type of a input parameter
        """
        for pr in self.__parameters:
            if pr['name'] == name:
                return pr['type']

    def input(self, name):
        """
        Get one specific test config by name passed as argument.
        """
        for pr in self.__parameters:
            if pr['name'] == name:
                if pr['type'] == 'alias':
                    if pr['value'] == name:
                        raise TestPropertiesException(
                            'ERR_PRO_005: Invalid input alias "%s"' % pr['value'])
                    return self.input(name=pr['value'])
                else:
                    return decodeParameter(
                        parameter=pr, sharedParameters=self.__parametersShared)
        raise TestPropertiesException(
            'ERR_PRO_004: Input parameter "%s" not available' %
            name)

    def setInput(self, name, value):
        """
        Set input value
        """
        paramFounded = False
        for pr in self.__parameters:
            if pr['name'] == name:
                paramFounded = True
                pr['value'] = decodeValue(parameter=pr, value=value)
                break
        if not paramFounded:
            raise TestPropertiesException(
                'ERR_PRO_020: Input parameter "%s" not available' %
                name)

    def shared(self, project, name, subname=''):
        """
        Get one specific test config by name passed as argument.
        """
        return decodeShared(parameter="::%s:%s" % (name, subname),
                            sharedParameters=self.__parametersShared,
                            projectName=project)

    def data(self):
        """
        """
        ret = []
        for d in self.__parameters:
            if d['name'].startswith('DATA_'):
                ret.append(d)
        return ret

    def sut(self):
        """
        """
        ret = []
        for d in self.__parameters:
            if d['name'].startswith('SUT_'):
                ret.append(d)
        return ret


class NotFound(object):
    pass


class TestPlanParameters(object):
    def __init__(self):
        """
        """
        self.__parameters = {}
        self.__descriptions = {}
        self.__parametersShared = []
        self.__running_agents = []
        self.__cache = None

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
                    if p["scope"] == "cache" and self.__cache.get(
                            name=p["name"]) is None:
                        tmp_v = decodeParameter(
                            p, sharedParameters=self.__parametersShared)
                        self.__cache.set(name=p["name"], data=tmp_v)
                        if p["type"] == "json" and isinstance(tmp_v, dict):
                            for k, v in tmp_v.items():
                                self.__cache.set(
                                    name="%s_%s" %
                                    (p["name"], k), data=v)
        except Exception as e:
            raise TestPropertiesException(
                'ERR_PRO_100: bad json parameter provided - %s' % e)

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

    def addDescriptions(self, descriptionsId, descriptions):
        """
        Add descriptions
        """
        self.__descriptions[descriptionsId] = descriptions

    def addRunningAgents(self, agents):
        """
        Add running agents
        """
        self.__running_agents = agents

    def addParameters(self, parametersId, parameters):
        """
        Add parameters
        """
        self.__parameters[parametersId] = parameters

        self.updateAtRunTime(
            param_id=parametersId,
            params_all=self.__parameters)

    def addParametersShared(self, parameters):
        """
        Add parameter shared
        """
        self.__parametersShared = parameters

    def running(self, name):
        """
        Return agent according to the name passed as argument
        """
        agentAvailable = None
        for agt in self.__running_agents:
            if agt['id'] == name:
                agentAvailable = {'type': agt['type'].lower(), 'name': name}
        if agentAvailable is not None:
            return agentAvailable
        else:
            raise TestPropertiesException(
                'ERR_PRO_022: agent=%s is not running!' % name)

    def inputs(self, tpId, tsId):
        """
        Inputs
        """
        for prId, prVal in self.__parameters.items():
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
        """
        if name.lower() == 'comments':
            return ''
        for descrId, descrVal in self.__descriptions.items():
            if descrId == tsId:
                for descr in descrVal:
                    if descr['key'] == name.lower():
                        if sys.version_info > (3,):
                            return descr['value']
                        else:
                            return descr['value'].encode("utf-8")
        raise TestPropertiesException(
            'ERR_PRO_008: Description "%s" not available' %
            name)

    def parameter(self, name, tpId, tsId):
        """
        Return parameter
        """
        for prId, prVal in self.__parameters.items():
            if prId == tsId:
                for pr in prVal:
                    if pr['name'] == name:
                        # overwrite the parameter if present in main parameter
                        # except for alias
                        if pr['type'] != "alias":
                            ret = self.getParamFromMain(
                                name, tpId, paramType=pr['type'])
                        else:
                            ret = NotFound()
                        if not isinstance(ret, NotFound):
                            return ret
                        else:
                            if pr['type'] == 'alias':
                                if pr['value'] == name:
                                    raise TestPropertiesException(
                                        'ERR_PRO_011: Invalid input alias "%s"' % pr['value'])
                                return self.parameter(
                                    name=pr['value'], tpId=tpId, tsId=tsId)
                            else:
                                return decodeParameter(
                                    parameter=pr, sharedParameters=self.__parametersShared)
        raise TestPropertiesException(
            'ERR_PRO_010: Input parameter "%s" not available' %
            name)

    def setParameter(self, name, value, tpId, tsId):
        """
        Return parameter
        """
        paramFounded = False
        for prId, prVal in self.__parameters.items():
            if prId == tsId:
                for pr in prVal:
                    if pr['name'] == name:
                        paramFounded = True
                        pr['value'] = decodeValue(parameter=pr, value=value)
                        break
        if not paramFounded:
            raise TestPropertiesException(
                'ERR_PRO_022: Input parameter "%s" not available' %
                name)

    def readShared(self, shared):
        """
        """
        return readShared(parameter=shared,
                          sharedParameters=self.__parametersShared)

    def readListShared(self, shared):
        """
        """
        return readListShared(
            parameter=shared, sharedParameters=self.__parametersShared)

    def shared(self, project, name, subname=''):
        """
        Get one specific test config by name passed as argument.
        """
        return decodeShared(parameter="::%s:%s" % (name, subname),
                            sharedParameters=self.__parametersShared,
                            projectName=project)

    def getDescrFromMain(self, name, tpId):
        """
        Return description from main
        """
        for pr in self.__descriptions[tpId]:
            if pr['key'] == name:
                return decodeDescription(description=pr)
        return None

    def getParamFromMain(self, name, tpId, paramType):
        """
        Return parameter from main
        """
        for pr in self.__parameters[tpId]:
            if pr['name'] == name:
                if pr['type'] == 'alias':
                    if pr['value'] == name:
                        raise TestPropertiesException(
                            'ERR_PRO_014: Invalid main input alias "%s"' % pr['value'])
                    return self.getParamFromMain(
                        name=pr['value'], tpId=tpId, paramType=paramType)
                else:
                    return decodeParameter(
                        parameter=pr, sharedParameters=self.__parametersShared)
        return NotFound()

    def getSutFromMain(self, parametersId):
        """
        """
        ret = []
        for d in self.__parameters[parametersId]:
            if d['name'].startswith('SUT_'):
                ret.append(d)
        return ret

    def getDataFromMain(self, parametersId):
        """
        """
        ret = []
        for d in self.__parameters[parametersId]:
            if d['name'].startswith('DATA_'):
                ret.append(d)
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
                newParams.append(d)

        ret = []
        for d in newParams:
            if d['name'].startswith('SUT_'):
                ret.append(d)

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
                newParams.append(d)

        ret = []
        for d in newParams:
            if d['name'].startswith('DATA_'):
                ret.append(d)

        del newParams
        return ret


TPL = None
custom_text = None
custom_json = None
cache = None


def instance():
    """
    Return the instance
    """
    if TPL:
        return TPL


def initialize(parameters=None,
               descriptions=None,
               parametersOut=None,
               # agents=None,
               parametersShared=None,
               runningAgents=[],
               runningProbes=[]):
    """
    Initialize the module
    """
    global TPL
    if parameters is None:
        TPL = TestPlanParameters()
    else:
        TPL = Properties(parameters=parameters,
                         descriptions=descriptions,
                         parametersShared=parametersShared,
                         runningAgents=runningAgents
                         )


def finalize():
    """
    Finalize the module
    """
    global TPL
    if TPL:
        TPL = None
