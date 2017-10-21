#!/bin/sh

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

#====================================================================
#
#         USAGE:  ./install.sh
#
#   DESCRIPTION:  Install the product
#
#       OPTIONS:  ---
#        AUTHOR:  Denis Machard
#====================================================================

. /etc/rc.d/init.d/functions

# first check for root user
if [ ! $UID -eq 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

APP_NAME="ExtensiveTesting"
APP_PATH="$(pwd)"
LOG_FILE="$APP_PATH/install.log"
PKG_PATH="$APP_PATH/PKG/"
APP_SRC_PATH="$(pwd)/$APP_NAME/"
if [ ! -f "$APP_SRC_PATH"/VERSION ]; then
    echo "Package version not detected, goodbye."
    exit 1
fi
PRODUCT_VERSION="$(cat "$APP_SRC_PATH"/VERSION)"
PRODUCT_SVC_NAME="$(echo $APP_NAME | sed 's/.*/\L&/')"
PRODUCT_SVC_CTRL="xtctl"

read -p "Are you sure to install the product? (yes or no) " yn 
case $yn in 
	[Yy]* ) ;; 
	[Nn]* ) echo "Ok, goodbye."; exit 1;; 
	* ) echo "Please answer yes or no. ";exit 1;; 
esac 

# install the product without ask anything
$APP_PATH/custom.sh install
