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
import time
import base64

try:
    xrange
except NameError:  # support python3
    xrange = range

from ea.testexecutorlib import TestOperatorsLib
from ea.testexecutorlib import TestLoggerXml as TLX
from ea.testexecutorlib import TestSettings

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__DESCRIPTION__ = """This library enable to create template messages."""

__HELPER__ = [
    ('Template', ['__init__', 'compare', 'getRaw',
                              'getValue', 'prepareLayer']),
    ('TemplateLayer', ['__init__', 'addRaw', 'getRaw', 'getName',
                                   'updateName', 'getLenItems', 'getItems',
                                   'getValues', 'getKeys', 'getInt', 'get',
                                   'addKey', 'updateKey', 'removeKey', 'addMore']),
    ('TemplateMessage', ['__init__', 'addRaw', 'getRaw',
                                     'getInt', 'get',
                                     'addLayer', 'getLayer'])
]

VERSION_PAYLOAD = 1

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

TYPES_OP = [
    str,
    unicode,
    int,
    TestOperatorsLib.Any,
    TestOperatorsLib.Startswith,
    TestOperatorsLib.NotStartswith,
    TestOperatorsLib.Endswith,
    TestOperatorsLib.NotEndswith,
    TestOperatorsLib.Contains,
    TestOperatorsLib.NotContains,
    TestOperatorsLib.GreaterThan,
    TestOperatorsLib.LowerThan,
    TestOperatorsLib.RegEx,
    TestOperatorsLib.NotRegEx,
    TestOperatorsLib.NotGreaterThan,
    TestOperatorsLib.NotLowerThan
]


class TestTemplatesException(Exception):
    pass


class Template(object):

    def __init__(self, parent=None):
        """
        Generic template accessor

        @param parent: the parent testcase
        @type parent: testcase
        """
        self.__testcase = parent

    def compare(self, template, expected):
        """
        Compare templates

        @param template: template message or layer
        @type template: templatemessage/templatelayer

        @param expected: template message or layer
        @type expected: templatemessage/templatelayer

        @return: result of the comparaison
        @rtype: boolean
        """
        msg = template
        tpl = expected

        # read template message
        if isinstance(msg, TemplateLayer):
            msg = TemplateMessage()
            msg.addLayer(template)
        elif isinstance(msg, TemplateMessage):
            pass
        else:
            raise Exception("bad template message: %s" % type(msg))

        # read template expected
        if isinstance(tpl, TemplateLayer):
            tpl = TemplateMessage()
            tpl.addLayer(expected)
        elif isinstance(tpl, TemplateMessage):
            pass
        else:
            raise Exception("bad expected message: %s" % type(tpl))

        # compare templates
        ret, details = comparePayload(
            payload=msg.get(), tpl=tpl.get(), debug=False)

        if ret:
            if self.__testcase is not None:
                componentName = "TEMPLATE [matched]"
                TLX.instance().log_match_stopped(fromComponent=componentName,
                                                 dataMsg=(msg.get(), details),
                                                 tcid=self.__testcase.getId(),
                                                 font='italic',
                                                 index=0,
                                                 fromlevel=LEVEL_TE,
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__testcase.getTestInfo())
        else:
            if self.__testcase is not None:
                componentName = "TEMPLATE [mismatched]"
                TLX.instance().log_match_info(fromComponent=componentName,
                                              dataMsg=(msg.get(), details),
                                              tcid=self.__testcase.getId(),
                                              font='italic',
                                              index=0,
                                              fromlevel=LEVEL_TE,
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())

        return ret

    def getRaw(self, template):
        """
        Return raw message from template

        @param template: template message or layer
        @type template: templatemessage/templatelayer

        @return: raw message
        @rtype: string
        """
        if not isinstance(template, TemplateLayer) and not isinstance(
                template, TemplateMessage):
            raise TestTemplatesException('ERR_TPL_017: template layer message '
                                         'or layer expected, not %s' % type(template))
        return template.getRaw()

    def getValue(self, template, layerName, layerKey,
                 subLayerKey=None, caseSensitive=True):
        """
        Return value according to the layer name and key passed as argument

        @param template: template message or layer
        @type template: templatemessage/templatelayer

        @param layerName: key name
        @type layerName: string

        @param layerKey: key name
        @type layerKey: string

        @param subLayerKey: sub key name
        @type subLayerKey: string/none

        @param caseSensitive: the key is case sensitive is True
        @type caseSensitive: boolean

        @return: layer value as string or template layer
        @rtype: string/templatelayer/none
        """
        if not isinstance(template, TemplateLayer) and not isinstance(
                template, TemplateMessage):
            raise TestTemplatesException('ERR_TPL_017: template layer message '
                                         'or layer expected, not %s' % type(template))

        ret = None
        if isinstance(template, TemplateLayer):
            if template.getName() == layerName:
                ret = template.get(key=layerKey, caseSensitive=caseSensitive)
            else:
                raise TestTemplatesException('ERR_TPL_018: template layer '
                                             'name unknown: %s' % layerName)

        if isinstance(template, TemplateMessage):
            templateLayer = template.getLayer(layerName)
            if templateLayer is None:
                raise TestTemplatesException('ERR_TPL_018: template layer '
                                             'name unknown: %s' % layerName)
            else:
                if templateLayer.getName() == layerName:
                    retTmp = templateLayer.get(
                        key=layerKey, caseSensitive=caseSensitive)
                    if subLayerKey is not None:
                        ret = retTmp.get(
                            key=subLayerKey, caseSensitive=caseSensitive)
                    else:
                        ret = retTmp
                else:
                    raise TestTemplatesException('ERR_TPL_018: template layer '
                                                 'name unknown: %s' % layerName)

        return ret

    def __decodeList(self, data, firstCall=False, name=''):
        """
        Private function
        """
        list_layer = TemplateLayer(name=name)
        for i in xrange(len(data)):
            layer_data2 = None
            if isinstance(data[i], dict):
                if len(data[i]):
                    layer_data2 = self.__decodeDict(data=data[i])
            elif isinstance(data[i], list):
                if len(data[i]):
                    layer_data2 = self.__decodeList(data=data[i])
            elif isinstance(data[i], tuple):
                if len(data[i]) == 2:
                    layer_data2 = self.__decodeDict(
                        data={data[i][0]: data[i][1]})
                else:
                    layer_data2 = "%s" % str(data[i])
            else:
                if isinstance(data[i], int):
                    data[i] = str(data[i])
                if isinstance(data[i], float):
                    data[i] = str(data[i])
                if len(data[i]):
                    layer_data2 = data[i]
            if layer_data2 is not None:
                list_layer.addKey(name=str(i), data=layer_data2)
        return list_layer

    def __decodeDict(self, data, firstCall=False, name=''):
        """
        Private function
        """
        layerRest = TemplateLayer(name=name)
        for k, v in data.items():
            if isinstance(v, dict):
                if k.startswith('@') and not len(v):
                    pass
                else:
                    layer_data = self.__decodeDict(data=v)
                    layerRest.addKey(name=k, data=layer_data)
            elif isinstance(v, list):
                list_layer = self.__decodeList(data=v)
                if list_layer.getLenItems():
                    layerRest.addKey(name=k, data=list_layer)
            else:
                if v is None:
                    v = 'null'
                layerRest.addKey(name=k, data="%s" % v)
        return layerRest

    def prepareLayer(self, name, data):
        """
        Prepare the template layer according to the data

        @param name: layer name
        @type name: string

        @param data: layer data
        @type data: dict/list

        @return: the template layer
        @rtype: templatelayer
        """
        if isinstance(data, list):
            layerRest = self.__decodeList(data=data, firstCall=True, name=name)
        elif isinstance(data, dict):
            layerRest = self.__decodeDict(data=data, firstCall=True, name=name)
        else:
            raise TestTemplatesException("ERR_TPL_019: bad data "
                                         "on prepare: %s" % type(data))
        layerRest.addAsPy(data)
        return layerRest


class TemplateLayer(object):

    def __init__(self, name):
        """
        A template layer is a tuple with the name of the layer and the associated value.

        @param name: layer name
        @type name: string/integer
        """
        if sys.version_info > (3,):
            if isinstance(name, bytes):
                name = base64.encodebytes(name).decode("utf8")

        type_matched = False
        for op_type in TYPES_OP:
            if isinstance(name, op_type):
                type_matched = True
                break

        if not type_matched:
            raise TestTemplatesException('ERR_TPL_001: string expected '
                                         'on key name for the template layer '
                                         'with error: %s' % type(name))

        self.__datapy__ = {}
        self.__data__ = {}
        self.__name__ = name
        self.__tpl__ = (self.__name__, self.__data__)

    def __repr__(self):
        """
        """
        if len(self.__name__) > 0:
            return "%s(%s)" % (self.__class__.__name__, self.__name__)
        else:
            return self.__class__.__name__

    def __str__(self):
        """
        """
        if len(self.__name__) > 0:
            return "%s(%s)" % (self.__class__.__name__, self.__name__)
        else:
            return self.__class__.__name__

    def addAsPy(self, obj):
        """
        """
        self.__datapy__ = obj

    def getSize(self):
        """
        """
        s = 1
        for k, v in self.__data__.items():
            if isinstance(v, TemplateLayer):
                s += v.getSize()
            else:
                s += 1
        return s

    def getAsPy(self):
        """
        """
        if len(self.__datapy__):
            return self.__datapy__
        else:
            tmp = {}
            for k, v in self.__data__.items():
                if isinstance(v, TemplateLayer):
                    tmp[k] = v.get()
                else:
                    tmp[k] = v
            return tmp

    def addRaw(self, raw):
        """
        Add the raw layer

        @param raw: raw template layer
        @type raw: string
        """
        self.__data__['%%raw-layer%%'] = raw

    def getRaw(self):
        """
        Return the template layer as raw

        @return: raw message
        @rtype: string
        """
        if '%%raw-layer%%' in self.__data__:
            return self.__data__['%%raw-layer%%']
        else:
            return ''

    def getName(self):
        """
        Returns the name of the layer

        @return: layer name
        @rtype: string
        """
        return self.__name__

    def updateName(self, name):
        """
        Update the name of the layer

        @param name: name of the layer
        @type name: string
        """
        self.__name__ = name

    def getLenItems(self):
        """
        Return the length data

        @return: layer data length
        @rtype: integer
        """
        return len(self.__data__)

    def getItems(self):
        """
        Returns items as list [ (key, value), ... ]

        @return: layer data
        @rtype: list
        """
        return self.__data__.items()

    def getValues(self):
        """
        Returns layer values only

        @return: layer values
        @rtype: list
        """
        return self.__data__.values()

    def getKeys(self):
        """
        Returns layer key only

        @return: layer keys
        @rtype: list
        """
        return self.__data__.keys()

    def getInt(self, key=None, caseSensitive=True):
        """
        Identical to the function get
        But force to return the value as integer

        @param key: key name
        @type key: string/none

        @param caseSensitive: the key is case sensitive is True
        @type caseSensitive: boolean

        @return: value associated to the key
        @rtype: integer/none/tuple
        """
        ret = self.get(key=key, caseSensitive=caseSensitive)
        if ret is None:
            return ret
        if isinstance(ret, tuple):
            return ret
        return int(ret)

    def get(self, key=None, caseSensitive=True):
        """
        Get the value of the key passed as argument.
        Returns None if the key is not found.
        If no arguments are passed, then this function returns the template message as a tuple of (string, dict)

        @param key: key name
        @type key: string/none

        @param caseSensitive: the key is case sensitive is True
        @type caseSensitive: boolean

        @return: value associated to the key
        @rtype: string/none/tuple
        """
        if key is None:
            tmp = {}
            for k, v in self.__data__.items():
                if isinstance(v, TemplateLayer):
                    tmp[k] = v.get()
                else:
                    tmp[k] = v
            self.__tpl__ = (self.__name__, tmp)
            return self.__tpl__
        else:
            if caseSensitive:
                data = None
                if key in self.__data__:
                    data = self.__data__[key]
                return data
            else:
                data = None
                for k, v in self.getItems():
                    if k.lower() == key.lower():
                        data = v
                        break
                return data

    def addKey(self, name, data):
        """
        Add the key (name, data) to the layer

        @param name: key name
        @type name: string/integer

        @param data: key value
        @type data: string/integer/templatelayer
        """
        if sys.version_info > (3,):
            if isinstance(name, bytes):
                name = base64.encodebytes(name).decode("utf8")
            if isinstance(data, bytes):
                data = base64.encodebytes(data).decode("utf8")

        type_matched = False
        for op_type in TYPES_OP:
            if isinstance(name, op_type):
                type_matched = True
                break
        if not type_matched:
            raise TestTemplatesException('ERR_TPL_002 string expected '
                                         'on key name: %s' % type(name))

        type_matched = False
        for op_type in TYPES_OP:
            if isinstance(data, op_type):
                type_matched = True
                break
        if isinstance(data, TemplateLayer):
            type_matched = True

        if not type_matched:
            raise TestTemplatesException('ERR_TPL_003 string or templatelayer '
                                         'expected on value: %s' % type(data))
        self.__data__[name] = data

    def updateKey(self, name, data):
        """
        Update the key (name, data) to the layer

        @param name: key name
        @type name: string

        @param data: key value
        @type data: string/templatelayer
        """
        if name in self.__data__:
            self.__data__[name] = data

    def removeKey(self, name):
        """
        Remove the key name from the layer

        @param name: key name
        @type name: string
        """
        try:
            del self.__data[name]
        except Exception:
            pass

    def addMore(self, more):
        """
        Add more

        @param more: key, name data
        @type more: dict
        """
        self.__data__.update(more)


class TemplateMessage(object):

    def __init__(self):
        """
        Template Message
        This is a list of TemplateLayer
        """
        self.__version__ = VERSION_PAYLOAD
        self.__tpl__ = []
        self.__raw__ = ''
        self.__time__ = time.time()

    def __repr__(self):
        """
        """
        descr = []
        for l in self.__tpl__:
            descr.append(l.getName())
        if len(descr) > 0:
            return "%s(%s)" % (self.__class__.__name__, "|".join(descr))
        else:
            return self.__class__.__name__

    def __str__(self):
        """
        """
        descr = []
        for l in self.__tpl__:
            descr.append(l.getName())
        if len(descr) > 0:
            return "%s(%s)" % (self.__class__.__name__, "|".join(descr))
        else:
            return self.__class__.__name__

    def type(self):
        """
        """
        return '%%payload-v%s%%' % str(self.__version__)

    def addRaw(self, raw):
        """
        Add the raw message

        @param raw: raw template message
        @type raw: string
        """
        self.__raw__ = raw

    def getRaw(self):
        """
        Return the template message as raw

        @return: raw message
        @rtype: string
        """
        return self.__raw__

    def getEvent(self):
        """
        """
        tpl = self.get()

        # add header
        rawData = b""
        if len(self.__raw__):
            if sys.version_info > (3,):
                if not isinstance(self.__raw__, bytes):
                    rawData = base64.b64encode(bytes(self.__raw__, "utf8"))
                else:
                    rawData = base64.b64encode(self.__raw__)
            else:
                try:
                    rawData = base64.b64encode(self.__raw__)
                except UnicodeEncodeError:
                    rawData = base64.b64encode(self.__raw__.encode('utf8'))

        tpl.append((self.type(), {'len': len(self.__raw__),
                                  'raw': rawData,
                                  'time': self.__time__}))

        return tpl

    def getInt(self, name=None, key=None, keyCaseSensitive=True):
        """
        Identical to the function get
        But force to return the value as integer

        @param name: layer name
        @type name: string/none

        @param key: key name
        @type key: string/none

        @param keyCaseSensitive: the key is case sensitive is True
        @type keyCaseSensitive: boolean

        @return: value associated to the key
        @rtype: integer/none/templatelayer
        """
        ret = self.get(name=name, key=key, keyCaseSensitive=keyCaseSensitive)
        if ret is None:
            return ret
        if isinstance(ret, TemplateLayer):
            return ret
        return int(ret)

    def get(self, name=None, key=None, keyCaseSensitive=True):
        """
        Get the value of the key and the layer <name>
        If no arguments are passed, then this function
        returns the template message as a list of tuple.
        Returns None if the key and the <name> are not found.

        @param name: layer name
        @type name: string/none

        @param key: key name
        @type key: string/none

        @param keyCaseSensitive: the key is case sensitive is True
        @type keyCaseSensitive: boolean

        @return: value associated to the key
        @rtype: string/list/none/templatelayer
        """
        if name is not None:
            data = None
            for l in self.__tpl__:
                if l.getName() == name:
                    data = l
                    if key is not None:
                        data = l.get(key=key,
                                     caseSensitive=keyCaseSensitive)
                    break
            return data
        else:
            rlt = []
            for l in self.__tpl__:
                rlt.append(l.get())
            return rlt

    def set(self, tpl):
        """
        """
        self.__tpl__ = tpl

    def addLayer(self, layer):
        """
        Add a layer to the template message

        @param layer: layer
        @type layer: templatelayer
        """
        if not isinstance(layer, TemplateLayer):
            raise TestTemplatesException('ERR_TPL_004: add layer assertion '
                                         'failed, templatelayer is need')
        self.__tpl__.append(layer)

    def getLayer(self, name):
        """
        Get a layer from the template message by the name

        @param name: layer name
        @type name: string

        @return: templatelayer
        @rtype: none/templatelayer
        """
        ret = None
        for layer in self.__tpl__:
            if layer.getName() == name:
                ret = layer
        return ret

    def removeLayer(self, layer):
        """
        Remove layer
        """
        try:
            self.__tpl__.remove(layer)
        except Exception:
            raise TestTemplatesException("ERR_TPL_005: remove layer "
                                         "failed: layer unknown")

    def getSize(self):
        """
        return the size of the template
        """
        s = 0
        for l in self.__tpl__:
            s += l.getSize()
        return s


def tpl2str(expected):
    """
    replace compare object by unicode val

    @param tplValue:
    @type tplValue:
    """
    ret_pl = []
    for itm in expected:
        k, v = itm
        tmp_key = k
        tmp_val = v

        # replace the key first
        if is_ops(k=k):
            tmp_key = unicode(v)

        # then replace the value
        if is_ops(k=v):
            tmp_val = unicode(v)

        # recursive call if list
        if isinstance(v, dict):
            tmp_val = tpl2str(expected=v.items())
            tmp_val = dict(tmp_val)

        # recursive call if tuple
        if isinstance(v, tuple):
            tmp_val = tpl2str(expected=[v])
            tmp_val = tmp_val[0]

        ret_pl.append((tmp_key, tmp_val))
    return ret_pl


def comparePayload(payload, tpl, debug):
    """
    @param tplValue:
    @type tplValue:

    @param tplValue:
    @type tplValue:

    @param tplValue:
    @type tplValue:
    """
    if TestSettings.get('Trace', 'level') == 'DEBUG':
        TLX.instance().trace("compare template received: %s" % payload)
        TLX.instance().trace("compare template expected: %s" % tpl)

    # List expected, raise an expection if it is
    # not the case, can happens only on unitary test
    if not isinstance(payload, list):
        TLX.instance().error("ERR_TPL_006: compare: list expected "
                             "but %s passed on template received" % type(payload))
        payload = []
    if not isinstance(tpl, list):
        TLX.instance().error("ERR_TPL_007: compare: list expected "
                             "but %s passed on template expected" % type(tpl))
        tpl = []

    match = True
    ret_tpl = []
    for i in xrange(len(tpl)):
        # Somes checks before to start the comparaison;
        # tuple expected with just (key, value)
        if not isinstance(tpl[i], tuple):
            TLX.instance().error("ERR_TPL_008: compare: tuple expected "
                                 "but %s passed on template expected" % type(tpl[i]))
            tpl[i] = ('', {})

        # Extract key, value from the payload and
        # the template with index i
        tplKey, tplValue = tpl[i]

        # if the length of the payload if lower than
        # the template than ignore the rest
        if i >= len(payload):
            match = False
            tpl_key, tp_dict = ignoreValues(
                tplValue=(tplKey, tplValue), color='$r')
        else:
            # Somes checks before to start the comparaison;
            # tuple expected with just (key, value)
            if not isinstance(payload[i], tuple):
                TLX.instance().error("ERR_TPL_009: compare: tuple expected "
                                     "but %s passed on template received" % type(payload[i]))
                payload[i] = ('', {})

            # Extract key, value from the payload
            # and the template with index i
            plKey, plValue = payload[i]

            # A dict is expected on the value
            if not isinstance(tplValue, dict):
                TLX.instance().error("ERR_TPL_010: compare: dict expected "
                                     "but %s passed on template expected" % type(tplValue))
                tplValue = {}
            if not isinstance(plValue, dict):
                TLX.instance().error("ERR_TPL_011: compare: dict expected "
                                     "but %s passed on template received" % type(plValue))
                plValue = {}

            if not match:
                # Ignore all next values to compare
                tpl_key, tp_dict = ignoreValues(tplValue=(tplKey, tplValue))
            else:
                # Reconstruct template expected for the key of the tuple
                tpl_r, tpl_key = check_key_tuple(plKey=plKey,
                                                 tplKey=tplKey,
                                                 toStr=True)
                if not tpl_r:
                    match = tpl_r

                # Reconstruct the rest and compute
                # the final result of the comparaison
                tp_dict = {}
                for d in tplValue.items():
                    k, v = d
                    if not match:
                        # Ignore all next values to compare
                        tmp_tp_key = ignoreValues(tplValue=k)
                        tmp_tp_value = ignoreValues(tplValue=v)
                        tp_dict[tmp_tp_key] = tmp_tp_value
                    else:
                        # check the dict key
                        if is_ops(k=k):
                            f, f2, t, i = check_all_ops_dict_key(pl=plValue,
                                                                 keyTpl=k,
                                                                 toStr=True)
                            tmp_tp_key = t
                            pl_index = i
                            if not f:
                                tmp_tp_key = k.toStr(clr='$r')
                                match = False
                            if not f2:
                                tmp_tp_key = k.toStr(clr='$r')
                                match = False

                            # check the dict value
                            if match:
                                sub_match, sub_ret_tpl = check_dict_value(tpl_value=v,
                                                                          pl_value=plValue[pl_index],
                                                                          debug=debug)
                                if not sub_match:
                                    match = False
                                tmp_tp_value = sub_ret_tpl
                            else:
                                tmp_tp_value = ignoreValues(tplValue=v)

                        elif k in plValue:
                            tmp_tp_key = '$g%s' % k
                            # check the dict value
                            sub_match, sub_ret_tpl = check_dict_value(tpl_value=v,
                                                                      pl_value=plValue[k],
                                                                      debug=debug)
                            if not sub_match:
                                match = False
                            tmp_tp_value = sub_ret_tpl
                        else:

                            tmp_tp_key = '$r%s' % k
                            match = False
                            tmp_tp_value = ignoreValues(tplValue=v)

                        tp_dict[tmp_tp_key] = tmp_tp_value

        ret_tpl.append((tpl_key, tp_dict))
    if TestSettings.get('Trace', 'level') == 'DEBUG':
        TLX.instance().trace("compare result: %s" % match)
        TLX.instance().trace("compare result: %s" % ret_tpl)
    return match, ret_tpl


def ignoreValues(tplValue, color='$y'):
    """
    """
    if isinstance(tplValue, tuple):
        k, v = tplValue
        if is_ops(k=k):
            kIgnored = k.toStr(clr=color)
        else:
            kIgnored = '%s%s' % (color, k)
        vIgnored = {}
        for d in v.items():
            k2, v2 = d
            if is_ops(k=k2):
                k2Ignored = k2.toStr(clr=color)
            else:
                k2Ignored = '%s%s' % (color, k2)
            if isinstance(v2, tuple):
                v2Ignored = ignoreValues(tplValue=v2, color=color)
            elif is_ops(k=v2):
                v2Ignored = v2.toStr(clr=color)
            else:
                v2Ignored = '%s%s' % (color, v2)
            vIgnored[k2Ignored] = v2Ignored
        valueIgnored = (kIgnored, vIgnored)
    elif is_ops(k=tplValue):
        valueIgnored = tplValue.toStr(clr=color)
    else:
        valueIgnored = '%s%s' % (color, tplValue)
    return valueIgnored


def check_all_ops_dict_key(pl, keyTpl, toStr=False):
    """
    """
    tmp_tp_key = keyTpl
    found = False
    found2 = True
    pl_index = None
    for d2 in pl.items():
        k2, v2 = d2
        try:
            a, b = check_ops(pl=k2, tp=keyTpl, toStr=toStr)
            if a:
                tmp_tp_key = b
                pl_index = k2
                found = True
                break
        except Exception:
            try:
                found = True
                a, b = check_ops_not(pl=k2, tp=keyTpl, toStr=toStr)
                if found2:
                    tmp_tp_key = b
                    pl_index = k2
                    found2 = a
                if not a:
                    tmp_tp_key = b
                    break
            except Exception as e:
                TLX.instance().error("ERR_TPL_012: template incorrect: "
                                     "dict key unknown: %s" % e)
                raise TestTemplatesException("ERR_TPL_012: template incorrect: "
                                             "dict key unknown: %s" % e)
    return found, found2, tmp_tp_key, pl_index


def check_all_ops_dict_value(pl, valueTpl, toStr=False):
    """
    """
    tmp_tp_value = valueTpl
    found = False
    found2 = True
    try:
        a, b = check_ops(pl=pl, tp=valueTpl, toStr=toStr)
        if a:
            tmp_tp_value = b
            found = True
    except Exception:
        try:
            found = True
            a, b = check_ops_not(pl=pl, tp=valueTpl, toStr=toStr)
            if found2:
                tmp_tp_value = b
                found2 = a
            if not a:
                tmp_tp_value = b
        except Exception as e:
            TLX.instance().error("ERR_TPL_013: template incorrect: "
                                 "dict value unknown: %s" % e)
            raise TestTemplatesException("ERR_TPL_013: template incorrect: "
                                         "dict value unknown: %s" % e)
    return found, found2, tmp_tp_value


def check_dict_value(tpl_value, pl_value, debug):
    """
    """
    sub_match = False
    sub_ret_tpl = {}
    if isinstance(tpl_value, tuple):
        recur_match, recur_tpl = comparePayload(payload=[pl_value],
                                                tpl=[tpl_value],
                                                debug=debug)
        sub_match = recur_match
        sub_ret_tpl = recur_tpl[0]
    elif is_ops(k=tpl_value):
        f, f2, t = check_all_ops_dict_value(pl=pl_value,
                                            valueTpl=tpl_value,
                                            toStr=True)
        sub_ret_tpl = t
        sub_match = f
        sub_match = f2
        if not f:
            sub_ret_tpl = tpl_value.toStr(clr='$r')
            sub_match = False
        if not f2:
            sub_ret_tpl = tpl_value.toStr(clr='$r')
            sub_match = False
    else:
        if tpl_value == pl_value:
            sub_match = True
            sub_ret_tpl = '$g%s' % tpl_value
        else:
            sub_ret_tpl = '$r%s' % tpl_value
    return sub_match, sub_ret_tpl


def is_ops(k):
    """
    """
    type_matched = False
    for op_type in TYPES_OP[3:]:
        if isinstance(k, op_type):
            type_matched = True
            break

    if type_matched:
        return True
    else:
        return False


def check_key_tuple(plKey, tplKey, toStr=False):
    """
    """
    try:
        pl_r, pl_key = check_ops(pl=plKey, tp=tplKey, toStr=toStr)
    except Exception:
        try:
            pl_r, pl_key = check_ops_not(pl=plKey, tp=tplKey, toStr=toStr)
        except Exception as e:
            TLX.instance().error("ERR_TPL_014: value unknown received "
                                 "%s (%s) cmp with " % (
                                     str(plKey), type(plKey)),
                                 "tpl %s (%s)\n%s" % (str(tplKey), type(tplKey), e))
            raise TestTemplatesException("ERR_TPL_014: value unknown "
                                         "received %s (%s) cmp with " % (
                                             str(plKey), type(plKey)),
                                         "tpl %s (%s)\n%s" % (str(tplKey), type(tplKey), e))
    return pl_r, pl_key


def check_ops(pl, tp, clrOk='$g', clrKo='$r', toStr=False):
    """
    """
    match = True

    if isinstance(tp, TestOperatorsLib.Any):  # cmp any
        toDisplay = pl
        if toStr:
            toDisplay = tp.toStr()
        tmp_key = "%s%s" % (clrOk, toDisplay)

    elif isinstance(tp, TestOperatorsLib.RegEx) \
            or isinstance(tp, TestOperatorsLib.Startswith) \
            or isinstance(tp, TestOperatorsLib.Endswith) \
            or isinstance(tp, TestOperatorsLib.Contains):
        try:
            r = tp.seekIn(haystack=pl)
        except Exception:
            return False, ''
        toDisplay = pl
        if toStr:
            toDisplay = tp.toStr()
        if r:
            tmp_key = '%s%s' % (clrOk, toDisplay)
        else:
            tmp_key = '%s%s' % (clrKo, toDisplay)
            match = False

    elif isinstance(tp, TestOperatorsLib.GreaterThan) \
            or isinstance(tp, TestOperatorsLib.NotGreaterThan) \
            or isinstance(tp, TestOperatorsLib.LowerThan) \
            or isinstance(tp, TestOperatorsLib.NotLowerThan):
        try:
            r = tp.comp(y=pl)
        except Exception:
            return False, ''
        toDisplay = pl
        if toStr:
            toDisplay = tp.toStr()
        if r:
            tmp_key = '%s%s' % (clrOk, toDisplay)
        else:
            tmp_key = '%s%s' % (clrKo, toDisplay)
            match = False

    # strict compare
    elif isinstance(tp, str) or isinstance(tp, unicode) or isinstance(tp, int):
        toDisplay = pl
        if toStr:
            toDisplay = tp
        if tp != pl:
            tmp_key = '%s%s' % (clrKo, toDisplay)
            match = False
        else:
            tmp_key = '%s%s' % (clrOk, toDisplay)

    else:
        raise TestTemplatesException("ERR_TPL_015: cmp, key type "
                                     "unknown: %s (%s)" % (str(tp), type(tp)))
    return match, tmp_key


def check_ops_not(pl, tp, clrOk='$g', clrKo='$r', toStr=False):
    """
    """
    match = True

    # cmp not startswith
    if isinstance(tp, TestOperatorsLib.NotStartswith) \
            or isinstance(tp, TestOperatorsLib.NotRegEx) \
            or isinstance(tp, TestOperatorsLib.NotEndswith) \
            or isinstance(tp, TestOperatorsLib.NotContains):
        try:
            r = tp.seekIn(haystack=pl)
        except Exception:
            return False, ''
        toDisplay = pl
        if toStr:
            toDisplay = tp.toStr()
        if r:
            tmp_key = '%s%s' % (clrOk, toDisplay)
        else:
            tmp_key = '%s%s' % (clrKo, toDisplay)
            match = False
    else:
        TLX.instance().error("ERR_TPL_016: cmp tpl - not expected "
                             "key type unknown: %s (%s)" % (str(tp), type(tp)))
        raise TestTemplatesException("ERR_TPL_016: cmp tpl - not expected "
                                     "key type unknown: %s (%s)" % (str(tp), type(tp)))
    return match, tmp_key


# unit test
# pl = [
    # ('IP', {'source-ip': '127.0.0.1',
    # 'destination-ip': '127.0.0.1'}),
    # ('TCP', {'source-port': '60246',
    # 'destination-port': '80',
    # 'tcp-event':'connected'}),
    # ('HTTP', {'request': ('GET /.../ HTTP 1.1', {'method': 'GET',
    # 'version': 'HTTP 1.1'})}),
    # ('APP', {'raw': 'xxxxxxxxx'})
    # ]

# tpl = [
    # (TestOperatorsLib.Any(), {'source': '127.0.0.1',
    # 'destination-ip': TestOperatorsLib.Startswith('127')}),
    # (TestOperatorsLib.NotContains('TCP2'),  {}),
    # (TestOperatorsLib.Endswith('P'), {'request': ('GET /.../ HTTP 1.1', {})})
    # ]

# tpl = [
    # (TestOperatorsLib.Any(), {TestOperatorsLib.NotContains('source-ip'): '127.0.0.1',
    # TestOperatorsLib.Endswith('source-ip'): '127.0.0.1'}),
    # ]

# tpl = [
    # (TestOperatorsLib.Any(), {TestOperatorsLib.LowerThan(2): ''}),
    # ]

# tpl = [
    # (TestOperatorsLib.Any(), {TestOperatorsLib.NotContains('s2urce'): TestOperatorsLib.Any(),
    # TestOperatorsLib.Endswith('source-ip'): '127.0.0.1'}),
    # (TestOperatorsLib.Contains('TCP'), {'tcp-event': TestOperatorsLib.Startswith('conn'),
    # TestOperatorsLib.Contains('source'): '60246',
    # 'destination-port': TestOperatorsLib.GreaterThan('70')}),
    # ('HTTP', {TestOperatorsLib.Contains('request'): (TestOperatorsLib.Endswith('HTTP 1.1'),
    # {'version': TestOperatorsLib.Contains('1.1')})}),
    # (TestOperatorsLib.Endswith('P'), {TestOperatorsLib.Contains('raw'): 'xxxxxxxxx'})
    # ]

# issue 313
# pl =   [
    # ('IP', {'test': ('a', '')}),
    # ]

# tpl =  [
    # ('IP', {'test': ('a', {'b': 'c'})})
    # ]
# r, t = comparePayload(payload=pl, tpl=tpl, debug=None)
# print("result: %s" % r)
# print("template: %s" % t)
