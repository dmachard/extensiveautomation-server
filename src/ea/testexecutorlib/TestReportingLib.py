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

from ea.testexecutorlib import TestExecutorLib

__DESCRIPTION__ = """The library enable to create test reporting in realtime."""
__HELPER__ = [
    ('TestCases', ['__init__'])
]


class TestCases(object):
    def __init__(self):
        """
        Get all testcases as an iterator.
        Iterate on each testcase to get the verdict.
        """
        self.i = -1

    def __str__(self):
        """
        """
        tcs = TestExecutorLib.getTsMgr().testcases()
        return "TestCases(nb=%s)" % len(tcs)

    def __iter__(self):
        """
        """
        return iter(TestExecutorLib.getTsMgr().testcases())
