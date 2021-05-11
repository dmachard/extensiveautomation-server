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

from ea.serverrepositories import RepoManager
from ea.libs import Settings, Logger


class RepoPublic(RepoManager.RepoManager, Logger.ClassLogger):
    def __init__(self):
        """
        Repository manager for public test files
        """
        RepoManager.RepoManager.__init__(self, pathRepo='%s%s' % (Settings.getDirExec(),
                                                                  Settings.get('Paths', 'public')),
                                         extensionsSupported=[])


RepoPublicMng = None


def instance():
    """
    Returns the singleton
    """
    return RepoPublicMng


def initialize():
    """
    Instance creation
    """
    global RepoPublicMng
    RepoPublicMng = RepoPublic()


def finalize():
    """
    Destruction of the singleton
    """
    global RepoPublicMng
    if RepoPublicMng:
        RepoPublicMng = None
