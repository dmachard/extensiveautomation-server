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

import Dict2Xml
import Xml2Dict

if __name__ == '__main__':
    """
    """
    codecX2D = Xml2Dict.Xml2Dict()
    codecD2X = Dict2Xml.Dict2Xml(coding=None)
    # TEST 1
    xml = """<Family>
<Member Name="Abe" DOB="3/31/42" />
<Member Name="Betty" DOB="2/4/49" />
<Member Name="Edith" Father="Abe" Mother="Betty" DOB="8/30/80" />
<Member Name="Janet" Father="Frank" Mother="Edith" DOB="1/17/03" />
</Family>"""
    print("========== BEGIN TEST 1 ============")
    print("BEGIN WITH: \n%s" % xml)
    retX2D = codecX2D.parseXml(xml=xml)
    print("\nCONVERT TO \n%s" % retX2D)
    retD2X = codecD2X.parseDict(dico=retX2D)
    print("\nRECONVERT TO \n%s" % retD2X)
    print("========== END TEST 1 ============")

    # TEST 2
    xml = """<Request>
<RequestID>1</RequestID>
</Request>"""
    print("========== BEGIN TEST 2 ============")
    print("BEGIN WITH: \n%s" % xml)
    retX2D = codecX2D.parseXml(xml=xml)
    print("\nCONVERT TO \n%s" % retX2D)
    retD2X = codecD2X.parseDict(dico=retX2D)
    print("\nRECONVERT TO \n%s" % retD2X)
    print("========== END TEST 2 ============")

    # TEST 3
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<test>
    <items>
        <item id="1">
            <RequestID>1</RequestID>
            <Result>OK</Result>
        </item>
        <item id="2">
            <RequestID>3</RequestID>
            <Result>KO</Result>
        </item>
        <item id="3">
            <RequestID>65</RequestID>
            <Result>KO</Result>
        </item>
        <item>
            <RequestID>43</RequestID>
            <Result>KO</Result>
        </item>
    </items>
</test>"""
    print("========== BEGIN TEST 3 ============")
    print("BEGIN WITH: \n%s" % xml)
    retX2D = codecX2D.parseXml(xml=xml)
    print("\nCONVERT TO \n%s" % retX2D)
    retD2X = codecD2X.parseDict(dico=retX2D)
    print("\nRECONVERT TO \n%s" % retD2X)
    print("========== END TEST 3 ============")

    # TEST 4
    xml = """<Response>
      <items>
         <item >
            <Request>GET</Request>
            <Result>OK</Result>
         </item>
         <item id="1">
            <Request>GET</Request>
            <Result>KO</Result>
         </item>
      </items>
    </Response>"""
    print("========== BEGIN TEST 4 ============")
    print("BEGIN WITH: \n%s" % xml)
    retX2D = codecX2D.parseXml(xml=xml)
    print("\nCONVERT TO \n%s" % retX2D)
    retD2X = codecD2X.parseDict(dico=retX2D)
    print("\nRECONVERT TO \n%s" % retD2X)
    print("========== END TEST 4 ============")
