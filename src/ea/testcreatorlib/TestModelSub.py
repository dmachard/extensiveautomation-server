#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

import sys

from ea.testcreatorlib import TestModelCommon

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


def createSubTest(dataTest,
                  descriptions,
                  trPath,
                  isTestUnit=True,
                  isTestPlan=False,
                  isTestGlobal=False):
    """
    """
    srcTest = dataTest['test-definition']

    # te construction
    te = []

    # import python libraries
    te.append(TestModelCommon.IMPORT_PY_LIBS)
    te.append("import re\n")

    # import static arguments
    te.append(TestModelCommon.getStaticArgs())

    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

    if isTestPlan or isTestGlobal:
        te.append("""
ParametersHandler = TestProperties.instance()

try:
    def shared(project, name, subname=''):
        return ParametersHandler.shared(project=project,
                                        name=name,
                                        subname=subname)
    def input(name):
        return ParametersHandler.parameter(name=name,
                                           tpId=TLX.instance().mainScriptId,
                                           tsId=TLX.instance().scriptId)
    def setInput(name, value):
        return ParametersHandler.setParameter(name=name,
                                              value=value,
                                              tpId=TLX.instance().mainScriptId,
                                              tsId=TLX.instance().scriptId)
    def running(name):
        return ParametersHandler.running(name=name)

    get = parameter = input # backward compatibility
    def inputs():
        return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId,
                                        tsId=TLX.instance().scriptId)
    def descriptions():
        return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId,
                                              tsId=TLX.instance().scriptId)

    def description(name):
        return ParametersHandler.description(name=name,
                                             tpId=TLX.instance().mainScriptId,
                                             tsId=TLX.instance().scriptId)
""")
    else:
        te.append("""
try:
    def shared(project, name, subname=''):
        return TestProperties.Parameters().shared(project=project,
                                                  name=name,
                                                  subname=subname)
    def input(name):
        return TestProperties.Parameters().input(name=name)
    def setInput(name, value):
        return TestProperties.Parameters().setInput(name=name, value=value)
    def running(name):
        return TestProperties.Parameters().running(name=name)
    def inputs():
        return TestProperties.Parameters().inputs()
    def descriptions():
        return TestProperties.Parameters().descriptions()

    get = parameter = input # backward compatibility

    def description(name):
        return TestProperties.Descriptions().get(name=name)

""")

    te.append("""
    try:
        from ea.sutadapters import *
        from ea import sutadapters as SutAdapters
        SutLibraries = SutAdapters
        TestInteroperability = SutAdapters
    except Exception as e:
        raise Exception('SUT adapters import error (more details)\\n\\n%s' % str(e))
""")

    if isTestUnit:
        te.append("""
    # !! test injection
    class TESTCASE(TestCase):
""")
    else:
        te.append("""
    # !! test injection
""")
    if isTestUnit:
        te.append(TestModelCommon.indent(srcTest, nbTab=2))
    else:
        te.append(TestModelCommon.indent(srcTest, nbTab=1))

    te.append("""
except Exception as e:
    raise Exception(e)
""")
    return unicode(''.join(te)).encode('utf-8')
