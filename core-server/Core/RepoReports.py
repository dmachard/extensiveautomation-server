#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
# This file is part of the extensive testing project
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

from Libs import Settings, Logger

import RepoManager

REPO_TYPE = 5

class RepoReports(RepoManager.RepoManager, Logger.ClassLogger):
    def __init__(self):
        """
        Repository manager log reports files
        """
        RepoManager.RepoManager.__init__(self,
            pathRepo='%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'reports' ) ),
                extensionsSupported = [ RepoManager.TEST_RESULT_EXT, RepoManager.TXT_EXT, 
                                        RepoManager.CAP_EXT, RepoManager.ZIP_EXT,
                                        RepoManager.PNG_EXT ] )
                                        
###############################
RepoReportsMng = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return RepoReportsMng

def initialize ():
    """
    Instance creation
    """
    global RepoReportsMng
    RepoReportsMng = RepoReports()

def finalize ():
    """
    Destruction of the singleton
    """
    global RepoReportsMng
    if RepoReportsMng:
        RepoReportsMng = None