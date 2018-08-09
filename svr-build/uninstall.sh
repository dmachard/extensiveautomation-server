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
#         USAGE:  ./uninstall.sh
#
#   DESCRIPTION:  Uninstall the product
#
#       OPTIONS:  ---
#        AUTHOR:  Denis Machard
#====================================================================

. /etc/rc.d/init.d/functions


usage(){
	echo "Usage: $0 [force]"
	exit 1
}

# first check for root user
if [ ! $UID -eq 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

# check if the force option is provided on argument
if [ $# -eq 0 ]; then
	FORCE_UNINSTALL=0
else
	FORCE_UNINSTALL=1
fi 

APP_NAME="ExtensiveAutomation"
APP_PATH="$(pwd)"
PKG_PATH="$APP_PATH/PKG/"
LOG_FILE="$APP_PATH/logs/install.log"
APP_SRC_PATH="$(pwd)/$APP_NAME/"
if [ ! -f "$APP_SRC_PATH"/VERSION ]; then
    echo "Package version not detected, goodbye."
    exit 1
fi
PRODUCT_VERSION="$(cat $APP_SRC_PATH/VERSION)"
PRODUCT_SVC_NAME="$(echo $APP_NAME | sed 's/.*/\L&/')"

echo "================================================================="
echo "=         - Uninstall of the $APP_NAME product -      ="
echo "=                 Denis Machard                                 ="
echo "=            www.extensiveautomation.org                        ="
echo "================================================================="

source $APP_PATH/scripts/default.cfg
INSTALL_PATH="$INSTALL"
PRODUCT_SVC_CTRL=$ADMIN_SVC_CTL

# Get system name: redhat or centos and release version
echo -n "* Detecting the operating system"
OS_NAME=$(cat /etc/redhat-release | awk {'print $1}' | awk '{print tolower($0)}' )
OS_RELEASE=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release))
# the sed is here to extract the first character of the string
OS_RELEASE=$( echo $OS_RELEASE | sed -r 's/(.)[^.]*\.?/\L\1/g' )

if [[ $OS_RELEASE == 7* ]]; then
    OS_RELEASE=7
fi

if [ "$OS_NAME" != "red" -a "$OS_NAME" != "centos" -a "$OS_RELEASE" -lt 6  ]; then
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
# Stopping all services
#
#######################################
echo -n "* Stopping server"
systemctl stop $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Unable to stop the server, perhaps the server is not installed" >> $LOG_FILE
    if [ "$FORCE_UNINSTALL" == 0 ]; then
        echo_failure; echo
        exit 1
    fi
fi

/usr/sbin/"$PRODUCT_SVC_CTRL" stop 1>> $LOG_FILE 2>&1

echo_success; echo

echo -n "* Stopping $HTTPD_SERVICE_NAME"
systemctl stop $HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo_failure; echo
    echo "Unable to stop $HTTPD_SERVICE_NAME" >> "$LOG_FILE"
    exit_on_error
fi

echo_success; echo

#######################################
#
# Uninstallation
#
#######################################

# Remove the bdd
echo -n "* Removing database"
cd "$INSTALL_PATH"/current/Scripts/ 1>> $LOG_FILE 2>&1
python ./database/del-bdd.py 1>> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
	echo_failure; echo
	echo "Unable to delete the database" >> $LOG_FILE
	if [ "$FORCE_UNINSTALL" == 0 ]; then
		exit 1
	fi
else
	echo_success; echo
fi

# Remove the source
echo -n "* Removing source"
rm -rf $INSTALL/$APP_NAME-$PRODUCT_VERSION 1>> $LOG_FILE 2>&1
rm -f $INSTALL/current 1>> $LOG_FILE 2>&1
echo_success; echo


echo -n "* Removing cron scripts"
rm -f $CRON_WEEKLY/$PRODUCT_SVC_NAME-backups 1>> $LOG_FILE 2>&1
rm -f $CRON_DAILY/$PRODUCT_SVC_NAME-tables 1>> $LOG_FILE 2>&1
echo_success; echo

# Remove the service
echo -n "* Removing service"
systemctl disable $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
rm -rf $SYSTEMD/$PRODUCT_SVC_NAME.service 1>> $LOG_FILE 2>&1
rm -rf /usr/sbin/"$PRODUCT_SVC_NAME"ctl 1>> $LOG_FILE 2>&1

# remove workaround
cp -rf $SYSTEMD/$HTTPD_SERVICE_NAME.service.backup $SYSTEMD/$HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
systemctl daemon-reload 1>> "$LOG_FILE" 2>&1 
echo_success; echo

if [ "$CONFIG_IPTABLES" = "Yes" ]; then
	echo -n "* Restoring iptables"
	systemctl stop $IPTABLE_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1

	cp -rf $IPTABLE_CONF/iptables.backup $IPTABLE_CONF/iptables
	systemctl restart $IPTABLE_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to unconfigure $IPTABLE_CONF/iptables" >> $LOG_FILE
        if [ "$FORCE_UNINSTALL" == 0 ]; then
            exit 1
        fi
    fi
	echo_success; echo
fi

if [ "$CONFIG_PHP" = "Yes" ]; then
	echo -n "* Restoring php"
	mv -f $PHP_CONF.backup $PHP_CONF 1>> $LOG_FILE 2>&1
	echo_success; echo
fi

if [ "$CONFIG_APACHE" = "Yes" ]; then
	if [ "$SELINUX_CONFIG" = "Yes" ]; then
		echo -n "* Restoring selinux httpd_enable_homedirs"
		setsebool -P httpd_enable_homedirs 0 1>> $LOG_FILE 2>&1
		semanage port -d -t http_port_t -p tcp 8082 1>> $LOG_FILE 2>&1
		if [ $? -ne 0 ]; then
			echo_failure; echo
			echo "Unable to unconfigure selinux" >> $LOG_FILE
			if [ "$FORCE_UNINSTALL" == 0 ]; then
				exit 1
			fi
		else
			echo_success; echo
		fi
		echo -n "* Restoring selinux httpd_can_network_connect_db"
		setsebool -P httpd_can_network_connect_db 0 1>> $LOG_FILE 2>&1
		if [ $? -ne 0 ]; then
			echo_failure; echo
			echo "Unable to unconfigure selinux connect db" >> $LOG_FILE
			if [ "$FORCE_UNINSTALL" == 0 ]; then
				exit 1
			fi
		else
			echo_success; echo
		fi
	fi

	echo -n "* Removing httpd configuration"
	mv -f $HTTPD_CONF/httpd.conf.backup $HTTPD_CONF/httpd.conf 1>> $LOG_FILE 2>&1
	mv -f $HTTPD_VS_CONF/ssl.conf.backup $HTTPD_VS_CONF/ssl.conf 1>> $LOG_FILE 2>&1
	rm -rf $HTTPD_VS_CONF/$PRODUCT_SVC_NAME.conf >> $LOG_FILE 2>&1
	echo_success; echo

	echo -n "* Restarting $HTTPD_SERVICE_NAME"
	systemctl start $HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to start $HTTPD_SERVICE_NAME" >> $LOG_FILE
        if [ "$FORCE_UNINSTALL" == 0 ]; then
            exit 1
        fi
    else
        echo_success; echo
    fi
fi

echo "================================================================="
echo "- Uninstallation completed successfully!"
echo "================================================================="