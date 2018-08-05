#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive automation project
# Copyright (c) 2010-2018 Denis Machard
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
#
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensiveautomation.org
# -------------------------------------------------------------------

from Core import ConfigureExe
from Core import BuildWin
from Core import Settings
from Core.Libs import Logger

import json

# read the config
CONFIG = None
with open( "%s/config.json" % (Settings.getDirExec()) ) as f:
    CONFIG_RAW = f.read()
CONFIG = json.loads(CONFIG_RAW)

# start the compilation
ConfigureExe.run()
BuildWin.run(pluginName=CONFIG["plugin"]["name"], pluginVersion=CONFIG["plugin"]["version"])