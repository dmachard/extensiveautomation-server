#!/bin/bash

# -------------------------------------------------------------------
# Copyright (c) 2018 Denys Bortovets
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

VERSION=18.0.0

echo "Build App Client for Mac"
python3 ../../BuildMacApp.py py2app


echo "Create dmg package"
hdiutil create ExtensiveTestingClient.dmg -srcfolder ./dist/ExtensiveTestingClient_$VERSION.app