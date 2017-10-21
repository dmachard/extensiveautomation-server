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

if [ $# -eq 0 ]; then
    INSTALL_PATH=..
else
    INSTALL_PATH=$1
fi 

cd $INSTALL_PATH
CURRENT_PATH="$(pwd)"
PRODUCT_NAME="extensivetesting"

rm -rf $CURRENT_PATH/Docs/api 1>> /dev/null 2>&1

epydoc --html  $CURRENT_PATH/Core/XmlrpcServerInterface.py -o $CURRENT_PATH/Docs/api -v --parse-only 1>> /dev/null 2>&1

rm -rf $CURRENT_PATH/Docs/api-rest 1>> /dev/null 2>&1
mkdir $CURRENT_PATH/Docs/api-rest 1>> /dev/null 2>&1
mkdir $CURRENT_PATH/Docs/api-rest/previous 1>> /dev/null 2>&1

epydoc --html  $CURRENT_PATH/Core/RestServerInterface.py -o $CURRENT_PATH/Docs/api-rest/previous -v --parse-only --no-private > /dev/null

cd $CURRENT_PATH/Scripts/
python ./decode-api.py  1>> /dev/null 2>&1

java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/api-rest/$PRODUCT_NAME.yaml -l html2 -o $CURRENT_PATH/Docs/api-rest/ -t $CURRENT_PATH/Scripts/htmlDocs2/ 1>> /dev/null 2>&1
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/api-rest/$PRODUCT_NAME.yaml -l swagger -o $CURRENT_PATH/Docs/api-rest/  1>> /dev/null 2>&1
mv $CURRENT_PATH/Docs/api-rest/swagger.json $CURRENT_PATH/Docs/api-rest/$PRODUCT_NAME.json 1>> /dev/null 2>&1


if [ ! -f $CURRENT_PATH/Docs/api-rest/index.html ]; then
    echo "Doc generation failed - index.html not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/api-rest/$PRODUCT_NAME.json ]; then
    echo "Doc generation failed - swagger json not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/api-rest/$PRODUCT_NAME.yaml ]; then
    echo "Doc generation failed - swagger yaml not found!"
fi

