#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
