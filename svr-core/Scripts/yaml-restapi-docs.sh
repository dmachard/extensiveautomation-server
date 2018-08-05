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

if [ $# -eq 0 ]; then
    INSTALL_PATH=..
else
    INSTALL_PATH=$1
fi 

cd $INSTALL_PATH
CURRENT_PATH="$(pwd)"
PRODUCT_NAME="extensiveautomation"

rm -rf $CURRENT_PATH/Docs/tester-api-rest 1>> /dev/null 2>&1
rm -rf $CURRENT_PATH/Docs/admin-api-rest 1>> /dev/null 2>&1
rm -rf $CURRENT_PATH/Docs/common-api-rest 1>> /dev/null 2>&1

mkdir $CURRENT_PATH/Docs/tester-api-rest 1>> /dev/null 2>&1
mkdir $CURRENT_PATH/Docs/admin-api-rest 1>> /dev/null 2>&1
mkdir $CURRENT_PATH/Docs/common-api-rest 1>> /dev/null 2>&1

cd $CURRENT_PATH/Scripts/
python ./yaml-restapi-prepare.py  1>> /dev/null 2>&1

# tester functions
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/tester-api-rest/$PRODUCT_NAME.yaml -l html2 -o $CURRENT_PATH/Docs/tester-api-rest/ -t $CURRENT_PATH/Scripts/htmlDocs2/
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/tester-api-rest/$PRODUCT_NAME.yaml -l swagger -o $CURRENT_PATH/Docs/tester-api-rest/
mv $CURRENT_PATH/Docs/tester-api-rest/swagger.json $CURRENT_PATH/Docs/tester-api-rest/$PRODUCT_NAME.json 1>> /dev/null 2>&1


if [ ! -f $CURRENT_PATH/Docs/tester-api-rest/index.html ]; then
    echo "Tester doc generation failed - index.html not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/tester-api-rest/$PRODUCT_NAME.json ]; then
    echo "Tester doc generation failed - swagger json not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/tester-api-rest/$PRODUCT_NAME.yaml ]; then
    echo "Tester doc generation failed - swagger yaml not found!"
fi

# admin functions
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/admin-api-rest/$PRODUCT_NAME.yaml -l html2 -o $CURRENT_PATH/Docs/admin-api-rest/ -t $CURRENT_PATH/Scripts/htmlDocs2/
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/admin-api-rest/$PRODUCT_NAME.yaml -l swagger -o $CURRENT_PATH/Docs/admin-api-rest/
mv $CURRENT_PATH/Docs/admin-api-rest/swagger.json $CURRENT_PATH/Docs/admin-api-rest/$PRODUCT_NAME.json 1>> /dev/null 2>&1


if [ ! -f $CURRENT_PATH/Docs/admin-api-rest/index.html ]; then
    echo "Admin doc generation failed - index.html not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/admin-api-rest/$PRODUCT_NAME.json ]; then
    echo "Admin doc generation failed - swagger json not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/admin-api-rest/$PRODUCT_NAME.yaml ]; then
    echo "Admin doc generation failed - swagger yaml not found!"
fi

# common functions
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/common-api-rest/$PRODUCT_NAME.yaml -l html2 -o $CURRENT_PATH/Docs/common-api-rest/ -t $CURRENT_PATH/Scripts/htmlDocs2/
java -jar $CURRENT_PATH/Scripts/swagger-codegen-cli-2.2.2.jar generate -i $CURRENT_PATH/Docs/common-api-rest/$PRODUCT_NAME.yaml -l swagger -o $CURRENT_PATH/Docs/common-api-rest/
mv $CURRENT_PATH/Docs/common-api-rest/swagger.json $CURRENT_PATH/Docs/common-api-rest/$PRODUCT_NAME.json 1>> /dev/null 2>&1


if [ ! -f $CURRENT_PATH/Docs/common-api-rest/index.html ]; then
    echo "Common doc generation failed - index.html not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/common-api-rest/$PRODUCT_NAME.json ]; then
    echo "Common doc generation failed - swagger json not found!"
fi

if [ ! -f $CURRENT_PATH/Docs/common-api-rest/$PRODUCT_NAME.yaml ]; then
    echo "Common doc generation failed - swagger yaml not found!"
fi
