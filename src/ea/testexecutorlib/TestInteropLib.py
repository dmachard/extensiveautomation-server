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

from ea.testexecutorlib import TestLoggerXml as TLX
from ea.testexecutorlib import TestTemplatesLib
from ea.testexecutorlib import TestExecutorLib as TestExecutor


class InteropException(Exception):
    pass


FROM_LEVEL = "INTEROP"


class InteropPlugin(object):
    def __init__(self, parent):
        """
        """
        self.tcparent = parent

        if not isinstance(parent, TestExecutor.TestCase):
            raise InteropException(
                "ERR_INT_001: testcase expected (%s)" %
                type(parent))

    def logRequest(self, msg, details, raw=""):
        """
        """
        tpl = TestTemplatesLib.TemplateMessage()
        tpl.addLayer(details)
        tpl.addRaw(raw)
        try:
            TLX.instance().log_snd(msg,
                                   tpl.getEvent(),
                                   tpl.type(),
                                   TestExecutor.TC, self.tcparent.getId(),
                                   fromlevel=FROM_LEVEL,
                                   tolevel=self.__class__.__name__.upper(),
                                   testInfo=self.tcparent.getTestInfo())
        except Exception as e:
            raise InteropException('ERR_INT_002: error on request: %s' % e)

    def logResponse(self, msg, details, raw=""):
        """
        """
        tpl = TestTemplatesLib.TemplateMessage()
        tpl.addLayer(details)
        tpl.addRaw(raw)
        try:
            TLX.instance().log_rcv(msg,
                                   tpl.getEvent(),
                                   tpl.type(),
                                   TestExecutor.TC,
                                   self.tcparent.getId(),
                                   fromlevel=self.__class__.__name__.upper(),
                                   tolevel=FROM_LEVEL,
                                   testInfo=self.tcparent.getTestInfo())
        except Exception as e:
            raise InteropException('ERR_INT_003: error on response: %s' % e)

    def template(self, name, content):
        """
        """
        tplGenerator = TestTemplatesLib.Template()
        tpl = tplGenerator.prepareLayer(name=name, data=content)
        return tpl
