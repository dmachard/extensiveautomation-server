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
