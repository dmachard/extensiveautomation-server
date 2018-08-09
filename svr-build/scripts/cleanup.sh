#!/bin/bash

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

#====================================================================
#
#         USAGE:  ./cleanup.sh
#
#   DESCRIPTION:  Remove all compilated files and dynamic folders
#
#       OPTIONS:  ---
#        AUTHOR:  Denis Machard
#====================================================================

PKG_NAME="ExtensiveAutomation"
APP_PATH="$(pwd)/../"
APP_SRC_PATH="$(pwd)/$PKG_NAME/"

echo "=============================================="
echo "=      - Cleanup the $PKG_NAME product -     ="
echo "=            Denis Machard                   ="
echo "=       www.extensiveautomation.org          ="
echo "=============================================="

rm -rf $APP_SRC_PATH/Libs/NetLayerLib/
rm -rf $APP_SRC_PATH/Libs/PyXmlDict/
rm -rf $APP_SRC_PATH/Libs/Scheduler.py
rm -rf $APP_SRC_PATH/Libs/FileModels/
rm -rf $APP_SRC_PATH/Libs/Logger.py
rm -rf $APP_SRC_PATH/SutAdapters/*
rm -rf $APP_SRC_PATH/SutLibraries/*
rm -rf $APP_SRC_PATH/Var/Backups/Tasks/*
rm -rf $APP_SRC_PATH/Var/Run/*
rm -rf $APP_SRC_PATH/Var/Logs/*
rm -rf $APP_SRC_PATH/Var/TestsResult/*
rm -rf $APP_SRC_PATH/Var/Backups/Adapters/*
rm -rf $APP_SRC_PATH/Var/Backups/Libraries/*
rm -rf $APP_SRC_PATH/Var/Backups/Archives/*
rm -rf $APP_SRC_PATH/Var/Backups/Tests/*
rm -rf $APP_SRC_PATH/Var/Tmp/*
rm -rf $APP_SRC_PATH/Probes/
rm -rf $APP_SRC_PATH/Packages/Client/win32/*
rm -rf $APP_SRC_PATH/Packages/Client/linux2/*
rm -rf $APP_SRC_PATH/Packages/Probes/win32/*
rm -rf $APP_SRC_PATH/Packages/Probes/linux2/*
rm -rf $APP_SRC_PATH/Packages/Agents/win32/*
rm -rf $APP_SRC_PATH/Packages/Agents/linux2/*
rm -rf $APP_SRC_PATH/Agents/
rm -rf $APP_SRC_PATH/Scripts/code_analysis/

find $APP_SRC_PATH/. -name "*.pyo" -exec rm -rf {} \;
find $APP_SRC_PATH/. -name "*.pyc" -exec rm -rf {} \;
