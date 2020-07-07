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
