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

import os
import base64
import parser
import sys

from ea.serverrepositories import RepoManager
from ea.libs import (Settings, Logger)

MAIN_DESCR = "This library contains all adapters available to test your SUT (System Under Test)."

MAIN_INIT = """%s

__DESCRIPTION__ = "%s"

__HELPER__ = [%s]

__all__ = [%s]
"""


ADP_INIT = """%s

__DESCRIPTION__ = "%s"
"""

# REGEXP_VERSION = r"^v[0-9]{3,}\Z"


class RepoAdapters(RepoManager.RepoManager, Logger.ClassLogger):
    """
    Repo adapters manager
    """

    def __init__(self, context):
        """
        Construct Adpaters Manager
        """
        RepoManager.RepoManager.__init__(self,
                                         pathRepo='%s/%s/' % (Settings.getDirExec(),
                                                              Settings.get('Paths', 'packages-sutadapters')),
                                         extensionsSupported=[RepoManager.PY_EXT,
                                                              RepoManager.TXT_EXT],
                                         context=context)

        self.context = context

        # update main init file
        self.updateMainInit()

    def getInstalled(self, withQuotes=False, asList=False):
        """
        Return all installed adapters
        """
        installed = []
        for f in os.listdir(self.testsPath):
            if f == "__pycache__":
                continue

            if os.path.isdir("%s/%s" % (self.testsPath, f)):
                if withQuotes:
                    installed.append('"%s"' % f)
                else:
                    installed.append(f)
        installed.sort()
        self.trace("Sut adapters installed: %s" % ', '.join(installed))
        if asList:
            return installed
        return ','.join(installed)

    def addPyInitFile(self, pathFile, descr="", helper="",
                      allmodules="", adps=False, mainInit=False):
        """
        Add the default __init__ file of the repository
        """
        HEADER = ''
        tpl_path = "%s/%s/adapter_header.tpl" % (Settings.getDirExec(),
                                                 Settings.get('Paths', 'templates'))
        try:
            fd = open(tpl_path, "r")
            HEADER = fd.read()
            fd.close()
        except Exception as e:
            self.error('unable to read template adapter header: %s' % str(e))

        try:
            if mainInit:
                default_init = MAIN_INIT % (HEADER, descr, helper, allmodules)
            else:
                default_init = ADP_INIT % (HEADER, descr)

            f = open('%s/__init__.py' % pathFile, 'w')
            f.write(default_init)
            f.close()
        except Exception as e:
            self.error(e)
            return False
        return True

    def getTree(self):
        """
        Get tree folders
        """
        return self.getListingFilesV2(path=self.testsPath,
                                      folderIgnored=["deps", "samples"])

    def updateMainInit(self):
        """
        Update the main init file
        """
        allmodules = self.getInstalled(withQuotes=True)
        ret = self.addPyInitFile(pathFile=self.testsPath, descr=MAIN_DESCR,
                                 allmodules=allmodules, mainInit=True)
        return ret

    def addAdapter(self, pathFolder, adapterName, mainAdapters=False):
        """
        Add adapter
        """
        ret = self.addDir(pathFolder, adapterName)
        if ret != self.context.CODE_OK:
            return ret

        if mainAdapters:
            # update main init file
            ret = self.updateMainInit()
            if not ret:
                return self.context.CODE_ERROR

        ret = self.addPyInitFile(pathFile="%s/%s/%s/" % (self.testsPath, pathFolder, adapterName),
                                 adps=mainAdapters)
        if not ret:
            return self.context.CODE_ERROR
        else:
            return self.context.CODE_OK

    def checkSyntax(self, content):
        """
        Check the syntax of the content passed as argument
        """
        try:
            if sys.version_info < (3,):
                content_decoded = base64.b64decode(content)
            else:
                content_decoded = base64.b64decode(content.encode())
                content_decoded = content_decoded.decode()

            parser.suite(content_decoded).compile()
        except SyntaxError as e:
            # syntax_msg = str(e)
            return False, str(e)

        return True, ''


RA = None


def instance():
    """
    Returns the singleton
    """
    return RA


def initialize(*args, **kwargs):
    """
    Instance creation
    """
    global RA
    RA = RepoAdapters(*args, **kwargs)


def finalize():
    """
    Destruction of the singleton
    """
    global RA
    if RA:
        RA = None
