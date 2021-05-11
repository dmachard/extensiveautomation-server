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

import base64
import zlib
import os

from ea.libs import Settings, Logger


class HelperManager(Logger.ClassLogger):
    def getHelps(self):
        """
        Returns the documentation cache
        """
        self.trace("get helps")
        ret = ''
        try:
            complete_path = '%s/%s/documentations.dat' % (Settings.getDirExec(),
                                                          Settings.get('Paths', 'var'))
            if os.path.exists(complete_path):
                fd = open(complete_path, "rb")
                data = fd.read()
                fd.close()

                ret = base64.b64encode(zlib.compress(data))
            else:
                self.error('documentation cache does not exist')
        except Exception as e:
            self.error("unable to get helps: %s" % e)
        return ret.decode('utf8')


HM = None  # singleton


def instance():
    """
    Returns the singleton
    """
    return HM


def initialize():
    """
    Instance creation
    """
    global HM
    HM = HelperManager()


def finalize():
    """
    Destruction of the singleton
    """
    global HM
    if HM:
        HM = None
