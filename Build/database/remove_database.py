#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
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

import os
import sys
sys.path.insert(0, '../../' )

from  Libs import Settings

Settings.initialize(path="../../")


db_name = "%s/../../%s/%s" % ( Settings.getDirExec(),
                               Settings.get( 'Paths', 'var' ),
                               Settings.get( 'Database', 'db' ))

try:
    os.remove(db_name)
except Exception as e:
    print("unable to remove database: %s" % e)
    
Settings.finalize()
sys.exit(0)