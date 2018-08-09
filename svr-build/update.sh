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

#====================================================================
#
#         USAGE:  ./update.sh
#
#   DESCRIPTION:  Update the product
#
#       OPTIONS:  ---
#        AUTHOR:  Denis Machard
#====================================================================


. /etc/rc.d/init.d/functions

usage(){
	echo "Usage: $0"
	echo "Example: ./update.sh"
	exit 1
}

# first check for root user
if [ ! $UID -eq 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

# init somes variables
PREVIOUS_APP_NAME="ExtensiveTesting"
PREVIOUS_PRODUCT_SVC_NAME="$(echo $PREVIOUS_APP_NAME | sed 's/.*/\L&/')"

APP_NAME="ExtensiveAutomation"
APP_PATH="$(pwd)"
LOG_FILE="$APP_PATH/logs/install.log"
UPDATE_PATH="$APP_PATH/scripts/"
APP_SRC_PATH="$(pwd)/$APP_NAME/"
if [ ! -f "$APP_SRC_PATH"/VERSION ]; then
    echo "Package version not detected, goodbye."
    exit 1
fi
PRODUCT_VERSION="$(cat "$APP_SRC_PATH"/VERSION)"
PRODUCT_SVC_NAME="$(echo $APP_NAME | sed 's/.*/\L&/')"

echo "============================================================="
echo "=       - Update of the $APP_NAME product -       ="
echo "=              Denis Machard                                ="
echo "=          www.extensiveautomation.org                      ="
echo "============================================================="

# import default config
source $APP_PATH/scripts/default.cfg
PREVIOUS_PRODUCT_SVC_CTRL=$ADMIN_SVC_CTL

exit_on_error()
{
    rm -rf "$APP_PATH"/scripts/default.cfg.tmp 1>> "$LOG_FILE" 2>&1
    exit 1
}


echo "===> Update called" >> "$LOG_FILE"


# Get system name: redhat or centos and release version
echo -n "* Detecting the operating system"
OS_NAME=$(cat /etc/redhat-release | awk {'print $1}' | awk '{print tolower($0)}' )
OS_RELEASE=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release))
# the sed is here to extract the first character of the string
OS_RELEASE=$( echo $OS_RELEASE | sed -r 's/(.)[^.]*\.?/\L\1/g' )

if [[ $OS_RELEASE == 7* ]]; then
    OS_RELEASE=7
fi

if [ "$OS_NAME" != "red" -a "$OS_NAME" != "centos" -a "$OS_RELEASE" -lt 6 ]; then
	echo_failure; echo
	echo "OS unknown: $OS_NAME$OS_RELEASE" >> "$LOG_FILE"
	exit_on_error
else
    echo -n " ($OS_NAME $OS_RELEASE)"
fi
echo_success; echo

echo -n "* Detecting the system architecture"
OS_ARCH=$(uname -m)

if [ "$OS_ARCH" != "x86_64" ]; then
	echo_failure; echo
	echo "OS arch not supported: $OS_ARCH" >> "$LOG_FILE"
	exit_on_error
else
	echo -n " ($OS_ARCH)"
fi
echo_success; echo

# prepare
if [ ! -f "$INSTALL"/current/VERSION ]; then
	echo "No $APP_NAME product detected!"
	echo "Bye bye"
	exit 1
fi

PREVIOUS_VERSION="$(cat "$INSTALL"/current/VERSION)"
if [[ "$PREVIOUS_VERSION" == "" ]]; then
	echo "No $APP_NAME product detected!"
	echo "Nothing to do, refer to the installation"
	echo "Bye bye"
	exit 1
fi

PREVIOUS_PATH="$INSTALL/$PREVIOUS_APP_NAME-$PREVIOUS_VERSION"
PREVIOUS_DB_NAME=$(sed -n 's/^db=*\([^ ]*.*\)/\1/p' < $INSTALL/current/settings.ini)
if [[ "$PREVIOUS_DB_NAME" == "" ]]; then
	echo "No current database detected!"
	echo "Nothing to do, refer to the installation"
	echo "Bye bye"
	exit 1
fi
echo "Current product version $PREVIOUS_VERSION"
echo "Current database name $PREVIOUS_DB_NAME"
echo "New product version: $PRODUCT_VERSION"
echo "New database name: $DATABASE_NAME"

if [[ "$PREVIOUS_VERSION" == "$PRODUCT_VERSION" ]]; then
	echo "$APP_NAME product is up-to-date!"
	echo "Bye bye"
	exit 1
fi

read -p "Are you sure to update the product? (yes or no) " yn 
case $yn in 
	[Yy]* ) ;; 
	[Nn]* ) echo "Ok, goodbye."; exit 1;; 
	* ) echo "Please answer yes or no. ";exit 1;; 
esac 

# update the default cfg according to the previous app
PREVIOUS_EXT_IP=$(sed -n 's/^ip-ext=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
if [[ "$PREVIOUS_EXT_IP" == "" ]]; then
	PREVIOUS_EXT_IP="0.0.0.0"
fi
PREVIOUS_MYSQL_IP=$(sed -n 's/^ip=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_MYSQL_LOGIN=$(sed -n 's/^user=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_MYSQL_PWD=$(sed -n 's/^pwd=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_MYSQL_SOCK=$(sed -n 's/^sock=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_FQDN=$(sed -n 's/^fqdn=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_DEMO_MODE=$(sed -n 's/^mode-demo=\(.*\)/\1/p' < $INSTALL/current/settings.ini)


PREVIOUS_DEFAULT_ADP=$(sed -n 's/^current-adapters=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_DEFAULT_LIB=$(sed -n 's/^current-libraries=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_GENERIC_ADP=$(sed -n 's/^generic-adapters=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_GENERIC_LIB=$(sed -n 's/^generic-libraries=\(.*\)/\1/p' < $INSTALL/current/settings.ini)

PREVIOUS_INSERT_DB=$(sed -n 's/^insert-test-statistics=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_READ_DB=$(sed -n 's/^read-test-statistics=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
PREVIOUS_ENCRYPT_ENV_DB=$(sed -n 's/^test-environment-encrypted=\(.*\)/\1/p' < $INSTALL/current/settings.ini)


perl -i -pe "s/DOWNLOAD_MISSING_PACKAGES=.*/DOWNLOAD_MISSING_PACKAGES=Yes/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/FQDN=.*/FQDN=$PREVIOUS_FQDN/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/EXTERNAL_IP=.*/EXTERNAL_IP=$PREVIOUS_EXT_IP/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/MYSQL_IP=.*/MYSQL_IP=$PREVIOUS_MYSQL_IP/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/MYSQL_USER=.*/MYSQL_USER=$PREVIOUS_MYSQL_LOGIN/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/MYSQL_PWD=.*/MYSQL_PWD=$PREVIOUS_MYSQL_PWD/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/MYSQL_SOCK=.*/MYSQL_SOCK=$(echo "$PREVIOUS_MYSQL_SOCK" | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/MODE_DEMO=.*/MODE_DEMO=$PREVIOUS_DEMO_MODE/g" "$APP_PATH"/scripts/default.cfg

perl -i -pe "s/DATABASE_INSERT_TEST_STATISTICS=.*/DATABASE_INSERT_TEST_STATISTICS=$PREVIOUS_INSERT_DB/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/DATABASE_READ_TEST_STATISTICS=.*/DATABASE_READ_TEST_STATISTICS=$PREVIOUS_READ_DB/g" "$APP_PATH"/scripts/default.cfg
perl -i -pe "s/DATABASE_ENCRYPT_TEST_ENV=.*/DATABASE_ENCRYPT_TEST_ENV=$PREVIOUS_ENCRYPT_ENV_DB/g" "$APP_PATH"/scripts/default.cfg

if [ "${PREVIOUS_DEFAULT_ADP}" != "" ]; then
    perl -i -pe "s/CURRENT_ADAPTERS=.*/CURRENT_ADAPTERS=$PREVIOUS_DEFAULT_ADP/g" "$APP_PATH"/scripts/default.cfg
fi
if [ "${PREVIOUS_DEFAULT_LIB}" != "" ]; then
    perl -i -pe "s/CURRENT_LIBRARIES=.*/CURRENT_LIBRARIES=$PREVIOUS_DEFAULT_LIB/g" "$APP_PATH"/scripts/default.cfg
fi
if [ "${PREVIOUS_GENERIC_ADP}" != "" ]; then
    perl -i -pe "s/GENERIC_ADAPTERS=.*/GENERIC_ADAPTERS=$PREVIOUS_GENERIC_ADP/g" "$APP_PATH"/scripts/default.cfg
fi
if [ "${PREVIOUS_GENERIC_LIB}" != "" ]; then
    perl -i -pe "s/GENERIC_LIBRARIES=.*/GENERIC_LIBRARIES=$PREVIOUS_GENERIC_LIB/g" "$APP_PATH"/scripts/default.cfg
fi


# reload config
source $APP_PATH/scripts/default.cfg

# Stop the product server
echo -n "* Stopping the current version $PREVIOUS_VERSION"
/usr/sbin/"$PREVIOUS_PRODUCT_SVC_CTRL" stop 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo_failure; echo
    echo "Unable to stop the server, perhaps the server is not installed" >> $LOG_FILE
    exit_on_error
fi
echo_success; echo

# remove previous symbolic link, usefull when the product name changed
rm -rf $HTTPD_VS_CONF/$PREVIOUS_PRODUCT_SVC_NAME.conf 1>> "$LOG_FILE" 2>&1
rm -rf $SYSTEMD/$PREVIOUS_PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1


$APP_PATH/custom.sh update
if [ $? -ne 0 ]; then
    exit_on_error
fi

#######################################
#
# Stop the product server
#
#######################################
systemctl stop $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo_failure; echo
    echo "Unable to stop the server, perhaps the server is not installed" >> $LOG_FILE
    exit_on_error
fi

/usr/sbin/"$ADMIN_SVC_CTL" stop 1>> $LOG_FILE 2>&1


#######################################
#
# Production migration
#
#######################################

# copy all previous sut adapters
echo -n "* Restoring SUT adapters from $PREVIOUS_VERSION to $PRODUCT_VERSION"
for f in $INSTALL/current/SutAdapters/*
do
    if [ -d "$f" ]; then
	perl -i -pe 's/__DEFAULT__ = True/__DEFAULT__ = False/' /$f/__init__.py
    fi
done
cp -rf $PREVIOUS_PATH/SutAdapters/* $INSTALL/current/SutAdapters/ 1>> "$LOG_FILE" 2>&1
echo_success; echo

# copy all previous sut libraries
echo -n "* Restoring SUT libraries from $PREVIOUS_VERSION to $PRODUCT_VERSION"
for f in $INSTALL/current/SutLibraries/*
do
    if [ -d "$f" ]; then
	perl -i -pe 's/__DEFAULT__ = True/__DEFAULT__ = False/' /$f/__init__.py
    fi
done
cp -rf $PREVIOUS_PATH/SutLibraries/* $INSTALL/current/SutLibraries/ 1>> "$LOG_FILE" 2>&1
echo_success; echo

# Database migration
echo -n "* Restoring database from $PREVIOUS_VERSION to $PRODUCT_VERSION"
mysqldump -h $MYSQL_IP -u $MYSQL_USER --password="$MYSQL_PWD" --add-drop-table --op $PREVIOUS_DB_NAME > /tmp/backup-dbb-$APP_NAME-$PREVIOUS_VERSION.sql
mysql -h $MYSQL_IP -u $MYSQL_USER --password="$MYSQL_PWD" $DATABASE_NAME < /tmp/backup-dbb-$APP_NAME-$PREVIOUS_VERSION.sql 1>> "$LOG_FILE" 2>&1
echo_success; echo

# Database model update
echo -n "* Updating database model to $PRODUCT_VERSION"
rm -rf "$UPDATE_PATH"/update.sql.tmp 1>> "$LOG_FILE" 2>&1
cp -rf "$UPDATE_PATH"/update.sql "$UPDATE_PATH"/update.sql.tmp 1>> "$LOG_FILE" 2>&1
perl -i -pe "s/<TABLE_PREFIX>/$DATABASE_TABLE_PREFIX/g" "$UPDATE_PATH"/update.sql.tmp
mysql -h $MYSQL_IP -u $MYSQL_USER --password="$MYSQL_PWD" $DATABASE_NAME < $UPDATE_PATH/update.sql.tmp 1>> "$LOG_FILE" 2>&1
rm -rf "$UPDATE_PATH"/update.sql.tmp 1>> "$LOG_FILE" 2>&1
echo_success; echo

# Tests migration
echo -n "* Restoring tests from $PREVIOUS_VERSION to $PRODUCT_VERSION"
cp -uR $PREVIOUS_PATH/Var/Tests/* $INSTALL/current/Var/Tests/ 1>> "$LOG_FILE" 2>&1
echo_success; echo

# Tasks migration
echo -n "* Restoring tasks from $PREVIOUS_VERSION to $PRODUCT_VERSION"
cp -rf $PREVIOUS_PATH/Var/Backups/Tasks/* $INSTALL/current/Var/Backups/Tasks/ 1>> "$LOG_FILE" 2>&1
echo_success; echo

# Public data migration
echo -n "* Restoring public data from $PREVIOUS_VERSION to $PRODUCT_VERSION"
cp -uR $PREVIOUS_PATH/Var/Public/* $INSTALL/current/Var/Public/ 1>> "$LOG_FILE" 2>&1
echo_success; echo

#######################################
#
# Restarting services
#
#######################################
echo -n "* Restarting $HTTPD_SERVICE_NAME"
systemctl restart $HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo_failure; echo
    echo "Unable to restart $HTTPD_SERVICE_NAME" >> "$LOG_FILE"
    exit_on_error
fi
echo_success; echo
    
echo -n "* Starting the new version $PRODUCT_VERSION"
systemctl start $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo_failure; echo
    echo "Unable to start the server" >> "$LOG_FILE"
    exit_on_error
fi
echo_success; echo

echo "========================================================================="
echo "- Update completed successfully!"
echo "- Continue and go to the web interface (https://$PREVIOUS_EXT_IP/web/index.php)"
echo "========================================================================="
