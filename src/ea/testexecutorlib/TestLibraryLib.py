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

import re
import inspect

from ea.testexecutorlib import TestLoggerXml as TLX
from ea.testexecutorlib import TestSettings

__DESCRIPTION__ = """The library provides some important functionalities to create library."""

__HELPER__ = [
    ('Library', ['__init__', 'testcase'])
]


def caller():
    """
    Function to find out which function is the caller of the current function.

    @return: caller function name
    @rtype: string
    """
    return inspect.getouterframes(inspect.currentframe())[1][1:4]


def getMainPath():
    """
    Return path where adapter are installed

    @return: test result path
    @rtype: string
    """
    return TestSettings.get('Paths', 'sut-adapters')


class LibraryException(Exception):
    """
    """

    def __init__(self, orig, msg):
        """
        """
        self.orig = orig
        self.msg = msg

    def __str__(self):
        """
        """
        # sut adapters path normalized, remove double // or more
        sut = re.sub("/{2,}", "/", getMainPath())

        f = self.orig[0].split(sut)[1]
        ret = "Library.%s > %s" % (self.orig[2], self.msg)
        ret += '\nFile: %s' % f
        ret += '\nLine error: %s' % self.orig[1]
        return ret


class ValueException(Exception):
    """
    """

    def __init__(self, orig, msg):
        """
        """
        self.orig = orig
        self.msg = msg

    def __str__(self):
        """
        """
        # sut adapters path normalized, remove double // or more
        sut = re.sub("/{2,}", "/", getMainPath())

        f = self.orig[0].split(sut)[1]
        ret = "Library.%s > %s" % (self.orig[2], self.msg)
        ret += '\nFile: %s' % f
        ret += '\nLine error: %s' % self.orig[1]
        return ret


LEVEL_LIBRARY = 'LIBRARY'
LEVEL_USER = 'USER'


class Library(object):
    """
    Library
    """

    def __init__(self, parent, name, realname=None, debug=False, showEvts=True,
                 showSentEvts=True, showRecvEvts=True, shared=False):
        """
        All libraries must inherent from this class

        @param parent: the parent testcase
        @type parent: testcase

        @param name: library name
        @type name: string

        @param debug: True to activate debug mode, default value=False
        @type debug: boolean

        @param shared: True to activate shared mode, default value=False
        @type shared: boolean
        """
        self.realname__ = realname
        self.__testcase = parent
        self.testcaseId = parent.getId()
        self.name__ = name.upper()

    def getFromLevel(self):
        """
        Return the from level
        """
        if self.realname__ is None:
            self.realname__ = "%s" % (LEVEL_LIBRARY)
        return self.realname__.upper()

    def testcase(self):
        """
        Accessor to the testcase
        """
        return self.__testcase

    def debug(self, txt, raw=True):
        """
        Display an debug message

        @param txt: debug message
        @type txt: string
        """
        self.trace("[%s] %s" % (self.__class__.__name__, txt), raw=raw)

    def error(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an error message
        Nothing is displayed if txt=None

        @param txt: error message
        @type txt: string

        @param bold: text is rendered as bold
        @type bold: boolean

        @param italic: text is rendered as italic
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """

        if not isinstance(bold, bool):
            raise Exception(
                "adp>error: bad value for the argument: bold=%s (%s)" %
                (bold, type(bold)))
        if not isinstance(italic, bool):
            raise Exception(
                "adp>error: bad value for the argument: italic=%s (%s)" %
                (italic, type(italic)))
        if not isinstance(multiline, bool):
            raise Exception(
                "adp>error: bad value for the argument: multiline=%s (%s)" %
                (multiline, type(multiline)))
        if not isinstance(raw, bool):
            raise Exception(
                "adp>error: bad value for the argument: raw=%s (%s)" %
                (raw, type(raw)))

        typeMsg = ''
        if raw:
            typeMsg = 'raw'

        try:
            TLX.instance().log_testcase_error(message=txt,
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_error(message=txt.encode('utf8'),
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())

    def warning(self, txt, bold=False, italic=False,
                multiline=False, raw=False):
        """
        Display an debug message
        Nothing is displayed if txt=None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """

        if not isinstance(bold, bool):
            raise Exception(
                "adp>warning: bad value for the argument: bold=%s (%s)" %
                (bold, type(bold)))
        if not isinstance(italic, bool):
            raise Exception(
                "adp>warning: bad value for the argument: italic=%s (%s)" %
                (italic, type(italic)))
        if not isinstance(multiline, bool):
            raise Exception(
                "adp>warning: bad value for the argument: multiline=%s (%s)" %
                (multiline, type(multiline)))
        if not isinstance(raw, bool):
            raise Exception(
                "adp>warning: bad value for the argument: raw=%s (%s)" %
                (raw, type(raw)))

        typeMsg = ''
        if raw:
            typeMsg = 'raw'
        try:
            TLX.instance().log_testcase_warning(message=txt,
                                                component=self.name__,
                                                tcid=self.testcaseId,
                                                bold=bold,
                                                italic=italic,
                                                multiline=multiline,
                                                typeMsg=typeMsg,
                                                fromlevel=self.getFromLevel(),
                                                tolevel=LEVEL_USER,
                                                testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_warning(message=txt.encode('utf8'),
                                                component=self.name__,
                                                tcid=self.testcaseId,
                                                bold=bold,
                                                italic=italic,
                                                multiline=multiline,
                                                typeMsg=typeMsg,
                                                fromlevel=self.getFromLevel(),
                                                tolevel=LEVEL_USER,
                                                testInfo=self.__testcase.getTestInfo())

    def info(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an info message
        Nothing is displayed if txt=None

        @param txt: info message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """

        if not isinstance(bold, bool):
            raise Exception(
                "adp>info: bad value for the argument: bold=%s (%s)" %
                (bold, type(bold)))
        if not isinstance(italic, bool):
            raise Exception(
                "adp>info: bad value for the argument: italic=%s (%s)" %
                (italic, type(italic)))
        if not isinstance(multiline, bool):
            raise Exception(
                "adp>info: bad value for the argument: multiline=%s (%s)" %
                (multiline, type(multiline)))
        if not isinstance(raw, bool):
            raise Exception(
                "adp>info: bad value for the argument: raw=%s (%s)" %
                (raw, type(raw)))

        typeMsg = ''
        if raw:
            typeMsg = 'raw'

        try:
            TLX.instance().log_testcase_info(message=txt,
                                             component=self.name__,
                                             tcid=self.testcaseId,
                                             bold=bold,
                                             italic=italic,
                                             multiline=multiline,
                                             typeMsg=typeMsg,
                                             fromlevel=self.getFromLevel(),
                                             tolevel=LEVEL_USER,
                                             testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_info(message=txt.encode('utf8'),
                                             component=self.name__,
                                             tcid=self.testcaseId,
                                             bold=bold, italic=italic,
                                             multiline=multiline,
                                             typeMsg=typeMsg,
                                             fromlevel=self.getFromLevel(),
                                             tolevel=LEVEL_USER,
                                             testInfo=self.__testcase.getTestInfo())

    def trace(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Trace message
        Nothing is displayed if txt=None

        @param txt: trace message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """

        if not isinstance(bold, bool):
            raise Exception(
                "adp>trace: bad value for the argument: bold=%s (%s)" %
                (bold, type(bold)))
        if not isinstance(italic, bool):
            raise Exception(
                "adp>trace: bad value for the argument: italic=%s (%s)" %
                (italic, type(italic)))
        if not isinstance(multiline, bool):
            raise Exception(
                "adp>trace: bad value for the argument: multiline=%s (%s)" %
                (multiline, type(multiline)))
        if not isinstance(raw, bool):
            raise Exception(
                "adp>trace: bad value for the argument: raw=%s (%s)" %
                (raw, type(raw)))

        typeMsg = ''
        if raw:
            typeMsg = 'raw'
        try:
            TLX.instance().log_testcase_trace(message=txt,
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_trace(message=txt.encode('utf8'),
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())
