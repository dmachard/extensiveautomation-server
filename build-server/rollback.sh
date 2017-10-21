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
#         USAGE:  ./roolback.sh
#
#   DESCRIPTION:  Rollback the product
#
#       OPTIONS:  ---
#        AUTHOR:  Denis Machard
#====================================================================


. /etc/rc.d/init.d/functions

usage(){
	echo "Usage: $0 [previous-version]"
	echo "Example: ./rollback.sh 6.1.0"
	exit 1
}

# if no argument passed then exit
[ $# -eq 0 ] && { usage; }

# first check for root user
if [ ! $UID -eq 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

# init somes variables
PREVIOUS_APP_NAME="ExtensiveTesting"
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


echo "=================================================="
echo "=  - Rollback of the $APP_NAME product -  ="
echo "=                 Denis Machard                  ="
echo "=            www.extensivetesting.org            ="
echo "=================================================="


# import default config
source $APP_PATH/default.cfg

PREVIOUS_PATH="$INSTALL/$PREVIOUS_APP_NAME-$1"

exit_on_error()
{
    rm -rf "$APP_PATH"/default.cfg.tmp 1>> "$LOG_FILE" 2>&1
    exit 1
}

# Get system name: redhat or centos and release version
echo -n "* Detecting the operating system"
OS_NAME=$(cat /etc/redhat-release | awk {'print $1}' | awk '{print tolower($0)}' )
OS_RELEASE=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release))
# the sed is here to extract the first character of the string
OS_RELEASE=$( echo $OS_RELEASE | sed -r 's/(.)[^.]*\.?/\L\1/g' )

if [[ $OS_RELEASE == 7* ]]; then
    OS_RELEASE=7
fi

if [ "$OS_NAME" != "red" -a "$OS_NAME" != "centos" ]; then
	echo_failure; echo
	echo "OS unknown: $OS_NAME$OS_RELEASE" >> "$LOG_FILE"
	exit_on_error
fi
echo_success; echo

echo -n "* Detecting the system architecture"
OS_ARCH=$(uname -m)

if [ "$OS_ARCH" != "x86_64" ]; then
	echo_failure; echo
	echo "OS arch not supported: $OS_ARCH" >> "$LOG_FILE"
	exit_on_error
fi
echo_success; echo

#######################################
#
# Stop the product server
#
#######################################
echo -n "* Stopping the $APP_NAME server"
if [ "$OS_RELEASE" == "7" ]; then
	systemctl stop $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to stop the server, perhaps the server is not installed" >> $LOG_FILE
		exit_on_error
	fi
else
	service $PRODUCT_SVC_NAME stop 1>> $LOG_FILE 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to stop the server, perhaps the server is not installed" >> $LOG_FILE
		exit_on_error
	fi
fi
echo_success; echo

#######################################
#
# Rollback actions
#
#######################################

# removing symbolic link
echo -n "* Rollbacking to $PREVIOUS_APP_NAME-$1"
rm -rf $INSTALL/current 1>> "$LOG_FILE" 2>&1
ln -s $PREVIOUS_PATH $INSTALL/current
echo_success; echo


#######################################
#
# Restart server
#
#######################################
echo -n "* Restarting the $PREVIOUS_APP_NAME server"
if [ "$OS_RELEASE" == "7" ]; then
	systemctl start $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to start the server" >> "$LOG_FILE"
		exit_on_error
	fi
else
	service $PRODUCT_SVC_NAME start 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to start the server" >> "$LOG_FILE"
		exit_on_error
	fi
fi
echo_success; echo

echo "========================================================================="
echo "- Rollback terminated!"
echo "========================================================================="