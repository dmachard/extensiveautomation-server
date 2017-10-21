#!/bin/bash

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

LIB_NAME=Toolbox
PKG_NAME=ExtensiveTestingToolbox
dos2unix ../$LIB_NAME/VERSION
PKG_VERSION=`cat ../Toolbox/VERSION`

echo "- clean pyo, pyc, git"
find ../$LIB_NAME/. -name "*.pyo" -exec rm -rf {} \;
find ../$LIB_NAME/. -name "*.pyc" -exec rm -rf {} \;
find ../$LIB_NAME/. -type d -name __pycache__ -not -path "./.*" -delete
rm -rf ../$LIB_NAME/.git/  > /dev/null
rm -rf ../$LIB_NAME/.gitignore  > /dev/null
rm -rf ../$LIB_NAME/Bin/.git/  > /dev/null
rm -rf ../$LIB_NAME/Bin/.gitignore  > /dev/null

echo "- add default config"
perl -i -pe "s/^level=.*/level=INFO/g" ../$LIB_NAME/settings.ini
dos2unix  ../$LIB_NAME/toolagent
dos2unix  ../$LIB_NAME/toolprobe
chmod +x ../$LIB_NAME/toolagent
chmod +x ../$LIB_NAME/toolprobe
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/toolrunner.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/testrunner.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/uninstallactiontrack.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/updateinstallation.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/wargenerator.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/soapui.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/securitytestrunner.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/mockservicerunner.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/loadtestrunner.sh
chmod +x ../$LIB_NAME/Bin/SoapUI/bin/installationcomplete.sh

echo "- clean build"
rm -rf ../$LIB_NAME/Scripts/build > /dev/null
rm -rf ../$LIB_NAME/__build__ > /dev/null

echo "- clean logs"
rm -rf ../$LIB_NAME/Logs/*  > /dev/null

echo "- clean tmp"
rm -rf ../$LIB_NAME/Tmp/*  > /dev/null

echo "- create pkg"
tar -czvf ../Packages/$LIB_NAME/linux2/$PKG_NAME\_$PKG_VERSION\_Setup.tar.gz ../$LIB_NAME/
