#!/bin/bash

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

if [ $# -eq 0 ]; then
    INSTALL_PATH=.
else
    INSTALL_PATH=$1
fi 

cd $INSTALL_PATH

PKG_NAME=SutLibraries

find ../SutLibraries/. -name "*.pyo" -exec rm -rf {} \;
find ../SutLibraries/. -name "*.pyc" -exec rm -rf {} \;
find ../SutLibraries/. -name "*.lock" -exec rm -rf {} \;

NB_LIB=$(find ../SutLibraries/* -maxdepth 1 -type d | wc -l)
if [ $NB_LIB -eq 0 ]; then
    exit 0
fi

for dir in ../SutLibraries/*/
do
    dir=${dir%*/}
    echo "- create pkg ${dir##*/}"
    tar -czvf ../Packages/SutLibraries/$PKG_NAME-${dir##*/}.tar.gz ../SutLibraries/${dir##*/}/
done
