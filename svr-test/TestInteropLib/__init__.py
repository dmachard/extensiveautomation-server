#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

import sys

try:
    from Jira import Jira
    from QualityCenter import QualityCenter
    from Git import Git
    from ExtensiveAutomation import ExtensiveAutomation
    from VSphere import VSphere
    from Nexus import Nexus
    from Email import Email
    from Chef import Chef
    if sys.version_info >= (2,7): from Jenkins import Jenkins
except ImportError: # python3 support
    from TestInteropLib.Jira import Jira
    from TestInteropLib.QualityCenter import QualityCenter
    from TestInteropLib.Git import Git
    from TestInteropLib.ExtensiveAutomation import ExtensiveAutomation
    from TestInteropLib.Nexus import Nexus
    from TestInteropLib.Email import Email
    from TestInteropLib.Jenkins import Jenkins
    from TestInteropLib.Chef import Chef
        
__DESCRIPTION__ = """The library enable to interact with others testing tools."""