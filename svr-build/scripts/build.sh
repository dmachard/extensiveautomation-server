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
#         USAGE:  ./build.sh
#
#   DESCRIPTION:  Package the product
#
#       OPTIONS:  ---
#        AUTHOR:  Denis Machard
#====================================================================

PKG_NAME="ExtensiveAutomation"
PRODUCT_SVC_NAME="$(echo $PKG_NAME | sed 's/.*/\L&/')"
APP_PATH="$(pwd)/../"
APP_SRC_PATH="$(pwd)/../$PKG_NAME/"
LOG_FILE="$APP_PATH/logs/install.log"

echo "========================================"
echo "=      Build the $PKG_NAME product     ="
echo "=           Denis Machard              ="
echo "=      www.extensiveautomation.org     ="
echo "========================================"


PKG_VERSION=$(cat $APP_SRC_PATH/VERSION)

TMP_BACKUP=/tmp/backuptestserver/

echo "Creating package $PKG_VERSION"
echo "with source $APP_SRC_PATH"

# clean code
find $APP_SRC_PATH/. -name "*.pyo" -exec rm -rf {} \;
find $APP_SRC_PATH/. -name "*.pyc" -exec rm -rf {} \;

echo "- prepare tmp"
rm -rf $TMP_BACKUP
mkdir $TMP_BACKUP

echo "- backup config to $TMP_BACKUP"
cp -rf $APP_SRC_PATH/settings.ini $TMP_BACKUP/settings.ini

echo "- add default config"
perl -i -pe "s/^ip=.*/ip=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^ip-wsu=.*/ip-wsu=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^ip-esi=.*/ip-esi=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^ip-tsi=.*/ip-tsi=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^ip-psi=.*/ip-psi=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^ip-asi=.*/ip-asi=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^fqdn=.*/fqdn=127.0.0.1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^level=.*/level=INFO/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^test-debug=.*/test-debug=0/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^statistics=.*/statistics=1/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^insert-test-statistics=.*/insert-test-statistics=0/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^#!\/usr\/bin\/python.*/#!\/usr\/bin\/python -O/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^mode-demo=.*/mode-demo=0/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^test-environment-encrypted=.*/test-environment-encrypted=0/g" $APP_SRC_PATH/settings.ini
perl -i -pe "s/^cleanup-test-design=.*/cleanup-test-design=1/g" $APP_SRC_PATH/settings.ini
dos2unix $APP_SRC_PATH/settings.ini  1>> "$LOG_FILE" 2>&1

echo "- add web default config"
perl -i -pe "s/LWF_DB_HOST.*/LWF_DB_HOST='127.0.0.2';/g" $APP_SRC_PATH/Web/include/config.php
perl -i -pe "s/LWF_DB_USER.*/LWF_DB_USER='root';/g" $APP_SRC_PATH/Web/include/config.php
perl -i -pe "s/LWF_DB_PWD.*/LWF_DB_PWD='';/g" $APP_SRC_PATH/Web/include/config.php
dos2unix $APP_SRC_PATH/Web/include/config.php  1>> "$LOG_FILE" 2>&1

echo "- add install default value"
perl -i -pe "s/^FQDN=.*/FQDN=127.0.0.1/g" $APP_PATH/scripts/default.cfg
perl -i -pe "s/^MYSQL_IP=.*/MYSQL_IP=127.0.0.1/g" $APP_PATH/scripts/default.cfg
perl -i -pe "s/^EXTERNAL_IP=.*/EXTERNAL_IP=127.0.0.1/g" $APP_PATH/scripts/default.cfg
perl -i -pe "s/^MYSQL_USER=.*/MYSQL_USER=root/g" $APP_PATH/scripts/default.cfg
perl -i -pe "s/^MYSQL_PWD=.*/MYSQL_PWD=/g" $APP_PATH/scripts/default.cfg
dos2unix $APP_PATH/scripts/default.cfg  1>> "$LOG_FILE" 2>&1

echo "- remove code report and analysis"
rm -rf $APP_SRC_PATH/Scripts/code_analysis/

echo "- remove toolbox"
rm -rf $APP_SRC_PATH/Toolbox/

echo "- move sutadapters to tmp"
cp -rf $APP_SRC_PATH/SutAdapters/ $TMP_BACKUP
rm -rf $APP_SRC_PATH/SutAdapters/*

echo "- move sutlibraries to tmp"
cp -rf $APP_SRC_PATH/SutLibraries/ $TMP_BACKUP
rm -rf $APP_SRC_PATH/SutLibraries/*

echo "- remove pid and httpd conf"
rm -rf $APP_SRC_PATH/Var/Run/*.pid
rm -rf $APP_SRC_PATH/Var/Run/httpd.conf

echo "- clean logs"
rm -rf $APP_PATH/logs/*
touch $APP_PATH/logs/install.log
touch $APP_PATH/logs/install_yum.log
touch $APP_PATH/logs/install_pip.log
rm -rf $APP_SRC_PATH/Var/Logs/*
touch $APP_SRC_PATH/Var/Logs/output.log
touch $APP_SRC_PATH/Var/Logs/tests.out

echo "- clean documentation cache"
rm -rf $APP_SRC_PATH/Var/Tmp/*

echo "- clean tests result"
rm -rf $APP_SRC_PATH/Var/TestsResult/*

echo "- clean tests"
rm -rf $APP_SRC_PATH/Var/Tests/*

echo "- clean public storage"
rm -rf $APP_SRC_PATH/Var/Public/*

echo "- clean backups"
rm -rf $APP_SRC_PATH/Var/Backups/Tasks/*
rm -rf $APP_SRC_PATH/Var/Backups/Adapters/*
rm -rf $APP_SRC_PATH/Var/Backups/Libraries/*
rm -rf $APP_SRC_PATH/Var/Backups/Archives/*
rm -rf $APP_SRC_PATH/Var/Backups/Tests/*
rm -rf $APP_SRC_PATH/Var/Backups/Tables/*

echo "- remove symbolic link"
rm -rf $APP_SRC_PATH/Packages/Client/linux2/*
rm -rf $APP_SRC_PATH/Packages/Client/win32/*
rm -rf $APP_SRC_PATH/Packages/Agents/linux2/*
rm -rf $APP_SRC_PATH/Packages/Agents/win32/*

rm -rf $APP_SRC_PATH/Packages/Client/win64/*
rm -rf $APP_SRC_PATH/Packages/Agents/win64/*


echo "- chmod on scripts"
chmod +x $APP_PATH/*.sh
dos2unix $APP_PATH/*.sh  1>> "$LOG_FILE" 2>&1

chmod +x $APP_PATH/scripts/*.sh
dos2unix $APP_PATH/scripts/*.sh  1>> "$LOG_FILE" 2>&1

chmod +x $APP_SRC_PATH/Scripts/*.py
dos2unix $APP_SRC_PATH/Scripts/*.py 1>> "$LOG_FILE" 2>&1

chmod +x $APP_SRC_PATH/Scripts/*.sh
dos2unix $APP_SRC_PATH/Scripts/*.sh 1>> "$LOG_FILE" 2>&1

echo "- generate doc api"
$APP_SRC_PATH/Scripts/yaml-restapi-docs.sh $APP_SRC_PATH

echo "- create pkg"
tar -czvf /tmp/$PKG_NAME-$PKG_VERSION.tar.gz ../../$PKG_NAME-$PKG_VERSION/
echo "=> Result tar.gz file is located in /tmp"
