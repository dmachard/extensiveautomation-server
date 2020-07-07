#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

try:
    xrange
except NameError:  # support python3
    xrange = range

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import cElementTree as ET


class Dict2Xml(object):
    def __init__(self, coding='UTF-8'):
        """
        Convert python dict to xml string

        @param coding: coding type (UTF-8, ISO, etc ...)
        @type coding: string
        """
        # encodage type
        # if coding = None, then the tag <?xml not added
        self.coding = coding
        # var to save the root node
        self.et = None

    def __parse(self, dico, parent=None, appnd=False):
        """
        Construct XML in function of the argument dico
        This function is called recursively

        @param dico: python dictionnary
        @type dico: dict

        @param parent: element
        @type parent: ET

        @param appnd: True when dico is a element of a list, False otherwise
        @type appnd: boolean
        """
        # saves attributes only if the node is of type list
        if appnd:
            attribList = {}
            for k, v in dico.items():
                if k.startswith('@'):
                    attribList = v
                    del dico[k]
        #
        for k, v in dico.items():
            donothing = False
            # check if the key is a node or if it is a key that contains
            # attributes
            attri = {}
            itrAttrib = False
            if ('@' == k[:1]) and isinstance(v, dict):
                k = k[1:]
                attri.update(v)
                itrAttrib = True
            elif ('@' == k[:1]) and isinstance(v, list):
                donothing = True
            if donothing:
                continue

            # element creation
            el = ET.Element(k)

            # add attributes to nodes, except for the root
            # on the second iter, the var parent is always different
            # of None
            if parent is not None:
                if appnd:  # list handler
                    el = ET.SubElement(parent, k, attribList)
                else:
                    _el = parent.find(k)
                    if _el is None:
                        el = ET.SubElement(parent, k, attri)
                    else:
                        el = _el
                        el.attrib.update(attri)

            # save the root node
            # this condition is true only on the first iter of the loop for
            if self.et is None:
                self.et = el

            # add attributes just for the root node
            # this condition is true only on the first iter of the loop for
            if parent is None:
                if self.et.tag == k:
                    self.et.attrib.update(attri)

            # continue to handle the variable v
            if isinstance(v, dict):
                # condition true only if the iteration if not for an
                # attributes
                if not itrAttrib:
                    # recursive call
                    if parent is None:
                        self.__parse(v, self.et)
                    else:
                        self.__parse(v, el)
            elif isinstance(v, list):
                # temp var to save the length of the var v
                tmp = []
                for idx in xrange(len(v)):
                    tmp.append({})
                #
                if '@%s' % k in dico:
                    for idx in xrange(len(dico['@%s' % k])):
                        tmp[idx].update(dico['@%s' % k][idx])
                # others iterations
                if parent is not None:
                    parent.remove(el)
                    for idx in xrange(len(v)):
                        tpl = {k: v[idx]}
                        if tmp[idx] != {}:
                            tpl.update({'@%s' % k: tmp[idx]})
                        self.__parse(tpl, parent, appnd=True)
            else:
                el.text = v

    def parseDict(self, dico):
        """
        Converts Python Dict to XML

        @param dico: dict message
        @type dico: dict

        @return: XML message
        @rtype: string
        """
        self.__parse(dico)
        ret = ET.tostring(self.et, self.coding)
        self.et = None
        return ret
