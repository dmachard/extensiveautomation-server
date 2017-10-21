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

# integer value expected or UNLIMITED to disable the license
LICENCE='{ "users": { "administrator": "UNLIMITED",  "leader": "UNLIMITED", "developer": "UNLIMITED", "tester": "UNLIMITED"  }, "agents": { "default": "UNLIMITED",  "instance": "UNLIMITED" }, "probes": { "default": "UNLIMITED",  "instance": "UNLIMITED" }, "projects": {"instance": "UNLIMITED"} }'

APP_NAME="product"

# read the key and iv
SALT=`awk -F"=" '/^salt=/{print $2}' $APP_NAME.key`
KEY=`awk -F"=" '/^key=/{print $2}' $APP_NAME.key`
IV=`awk -F"=" '/^iv =/{print $2}' $APP_NAME.key`

echo $LICENCE | openssl aes-256-cbc -salt -K $KEY -iv $IV  -e -out $APP_NAME.lic
