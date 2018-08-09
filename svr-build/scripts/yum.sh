#!/bin/sh

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

. /etc/rc.d/init.d/functions

# first check for root user
if [ ! $UID -eq 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

APP_PATH="$(pwd)"
LOG_FILE="$APP_PATH/logs/install_yum.log"

YUM_BIN="/usr/bin/yum"

for pkg in $(cat "$APP_PATH/local_rpms/requirements.txt")
do
    echo -ne "\r\033[K* Adding $pkg"
    yum -y install $(echo $pkg | tr '\n' ' ' | tr '\r' ' ')  >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to install package $pkg" >> "$LOG_FILE"
        exit 1
    fi
done 
echo_success; echo