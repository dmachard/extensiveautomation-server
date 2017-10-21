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

#====================================================================
#
#         USAGE:  ./secure.sh
#
#   DESCRIPTION:  Secure the product
#                 Improvement based on recommendations provided by
#                 Blaise Cador and more
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
APP_SRC_PATH="$(pwd)/$APP_NAME/"
if [ ! -f "$APP_SRC_PATH"/VERSION ]; then
    echo "Package version not detected, goodbye."
    exit 1
fi
PRODUCT_VERSION="$(cat $APP_SRC_PATH/VERSION)"
PRODUCT_SVC_NAME="$(echo $APP_NAME | sed 's/.*/\L&/')"

echo "================================================"
echo "=  - Secure of the $APP_NAME product -  ="
echo "=              Denis Machard                   ="
echo "=          www.extensivetesting.org            ="
echo "================================================"

# import default config
source $APP_PATH/default.cfg
PRODUCT_SVC_CTRL=$ADMIN_SVC_CTL

exit_on_error()
{
    rm -rf "$APP_PATH"/default.cfg.tmp 1>> "$LOG_FILE" 2>&1
    exit 1
}

PERL_BIN="/usr/bin/perl"

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

# check if the product is installed
if [ ! -f "$INSTALL"/current/VERSION ]; then
	echo "No $APP_NAME product detected!"
	echo "Bye bye"
	exit 1
fi

read -p "Are you sure to secure the product? (yes or no) " yn 
case $yn in 
	[Yy]* ) ;; 
	[Nn]* ) echo "Ok, goodbye."; exit 1;; 
	* ) echo "Please answer yes or no. ";exit 1;; 
esac 

#######################################
#
# Stopping all services
#
#######################################
echo -n "* Stopping the $APP_NAME server"
if [ "$OS_RELEASE" == "7" ]; then
	systemctl stop $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to stop the server, perhaps the server is not running" >> $LOG_FILE
        exit_on_error
	fi
else
	service $PRODUCT_SVC_NAME stop 1>> $LOG_FILE 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to stop the server, perhaps the server is not running" >> $LOG_FILE
        exit_on_error
	fi
fi
echo_success; echo

echo -n "* Stopping $HTTPD_SERVICE_NAME"
if [ "$OS_RELEASE" == "7" ]; then
	systemctl stop $HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to stop $HTTPD_SERVICE_NAME" >> "$LOG_FILE"
		exit_on_error
	fi
else
	service $HTTPD_SERVICE_NAME stop 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to stop $HTTPD_SERVICE_NAME" >> "$LOG_FILE"
		exit_on_error
	fi
	# kill httpd, just to be sure
	kill -9 `ps -ef | grep "$HTTPD_SERVICE_NAME" | grep -v grep | awk '{print $2}'` 1>> $LOG_FILE 2>&1
fi
echo_success; echo


#######################################
#
# System changes
#
#######################################

# system config
echo -n "* Creating $ADMIN_GROUP group"
groupadd $ADMIN_GROUP 1>> "$LOG_FILE" 2>&1
echo_success; echo

echo -n "* Creating $ADMIN_USER user"
userdel -r $PRODUCT_SVC_NAME 1>> "$LOG_FILE" 2>&1
useradd $ADMIN_USER -g $ADMIN_GROUP 1>> "$LOG_FILE" 2>&1
echo_success; echo

# change owner
echo -n "* Change files owner and group on $INSTALL"
chown -R $ADMIN_USER:$ADMIN_GROUP "$INSTALL"
echo_success; echo

# Remove the service
echo -n "* Update starting boot files"
if [ "$OS_RELEASE" == "7" ]; then
	$PERL_BIN -p -i -e  "s/^User=.*/User=$ADMIN_USER/g;" $SYSTEMD/$PRODUCT_SVC_NAME.service
	$PERL_BIN -p -i -e  "s/^Group=.*/Group=$ADMIN_GROUP/g;" $SYSTEMD/$PRODUCT_SVC_NAME.service
    systemctl daemon-reload 1>> "$LOG_FILE" 2>&1 
else
	$PERL_BIN -p -i -e  "s/^UserExec=.*/UserExec=\"$ADMIN_USER\"/g;" $INITD/$PRODUCT_SVC_NAME
fi
echo_success; echo

echo -n "* Secure database"
TEST_ENV_ENCRYPTED=$(sed -n 's/.*test-environment-encrypted=\(.*\)/\1/p' < $INSTALL/current/settings.ini)
if [ "$TEST_ENV_ENCRYPTED" == "0" ]; then
    cd "$INSTALL"/current/Scripts/
    python ./database/secure-bdd.py "$ADMIN_DB" "$PWD_DB" "$ADMIN_DUMP" "$PWD_DUMP" 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to encrypt test environement in the database" >> "$LOG_FILE"
        exit_on_error
    fi
    $PERL_BIN -i -pe "s/^test-environment-encrypted=.*/test-environment-encrypted=1/g" "$INSTALL"/current/settings.ini
    $PERL_BIN -i -pe "s/^user=.*/user=$ADMIN_DB/g" "$INSTALL"/current/settings.ini
    $PERL_BIN -i -pe "s/^pwd=.*/pwd=$PWD_DB/g" "$INSTALL"/current/settings.ini
    $PERL_BIN -i -pe "s/^user-dump=.*/user-dump=$ADMIN_DUMP/g" "$INSTALL"/current/settings.ini
    $PERL_BIN -i -pe "s/^pwd-dump=.*/pwd-dump=$PWD_DUMP/g" "$INSTALL"/current/settings.ini
    
    $PERL_BIN -i -pe "s/__LWF_DB_USER=.*/\$\_\_LWF\_DB\_USER='$ADMIN_DB';/g" "$INSTALL"/current/Web/include/config.php
    $PERL_BIN -i -pe "s/__LWF_DB_PWD=.*/\$\_\_LWF\_DB\_PWD='$PWD_DB';/g" "$INSTALL"/current/Web/include/config.php
fi
echo_success; echo

# secure httpd config
echo -n "* Secure apache configuration"

CURRENT_EXTERNAL_IP=$(sed -n 's/.*ip-ext=\(.*\)/\1/p' < $INSTALL/current/settings.ini)

cp -rf "$APP_SRC_PATH"/Scripts/httpd-sslonly.conf "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_IP>/$CURRENT_EXTERNAL_IP/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_IP_LOCAL>/$LOCALHOST_IP/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_WEB_PORT>/$INTERNAL_WEB_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_RP_PORT_SSL>/$EXTERNAL_WEB_PORT_SSL/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_RP_PORT>/$EXTERNAL_WEB_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_RPC_PORT>/$INTERNAL_RPC_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_REST_PORT>/$INTERNAL_REST_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_DATA_CLIENT_PORT>/$INTERNAL_DATA_CLIENT_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_DATA_AGENT_PORT>/$INTERNAL_DATA_AGENT_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_DATA_PROBE_PORT>/$INTERNAL_DATA_PROBE_PORT/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_FQDN>/$FQDN/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_USERNAME>/$PRODUCT_SVC_NAME/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/<KEY_INSTALL>/$(echo $INSTALL/current/ | sed -e 's/[]\/()$*.^|[]/\\&/g' )/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/ServerSignature.*/ServerSignature Off/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
$PERL_BIN -i -pe "s/ServerTokens.*/ServerTokens Prod/g" "$INSTALL"/current/Var/Run/httpd-sslonly.conf
dos2unix "$INSTALL"/current/Var/Run/httpd-sslonly.conf 1>> "$LOG_FILE" 2>&1

rm -f $HTTPD_VS_CONF/$PRODUCT_SVC_NAME.conf 1>> $LOG_FILE 2>&1
ln -s "$INSTALL"/current/Var/Run/httpd-sslonly.conf $HTTPD_VS_CONF/$PRODUCT_SVC_NAME.conf
echo_success; echo

echo -n "* Secure php configuration"
cp -rf $PHP_PATH $PHP_PATH.backup 1>> "$LOG_FILE" 2>&1
$PERL_BIN -i -pe "s/expose_php.*/expose_php = Off/g" $PHP_PATH
echo_success; echo

#######################################
#
# Restarting all services
#
#######################################
echo -n "* Restarting $HTTPD_SERVICE_NAME"
if [ "$OS_RELEASE" == "7" ]; then
    systemctl restart $HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to restart $HTTPD_SERVICE_NAME" >> "$LOG_FILE"
        exit_on_error
    fi
else
    service $HTTPD_SERVICE_NAME restart 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to restart $HTTPD_SERVICE_NAME" >> "$LOG_FILE"
        exit_on_error
    fi
fi
echo_success; echo

echo -n "* Starting $APP_NAME $PRODUCT_VERSION"
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