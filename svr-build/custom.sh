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
#         USAGE:  ./custom.sh
#
#   DESCRIPTION:  Custom installation of the product
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

# check if this script is called with silent 
# used with update mode
if [ $# -eq 0 ]; then
	SILENT="custom"
else
	SILENT=$1
fi 

# minimum space left to install the product, 1GB
MIN_SPACE_LEFT=1048576

APP_NAME="ExtensiveAutomation"
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

if [ "$SILENT" == "custom" -o "$SILENT" == "install" ]; then
	echo "=================================================================="
	echo "=       - Installation of the $APP_NAME product -      ="
	echo "=                           Denis Machard                        ="
	echo "=                      www.extensiveautomation.org               ="
	echo "=================================================================="
fi

# bin
PYBIN="/usr/bin/python"
UNZIP_BIN="/usr/bin/unzip"
YUM_BIN="/usr/bin/yum"
TAR_BIN="/usr/bin/tar"
PERL_BIN="/usr/bin/perl"
CAT_BIN="/usr/bin/cat"
PWD_BIN="/usr/bin/pwd"
LS_BIN="/usr/bin/ls"

# python extensions modified
SELENIUM_ZIP="selenium-3.13.0-extensivetesting"
SELENIUM="selenium-3.13.0"
PYCRYPTO_ZIP="pycryptodome-3.4.5-extensivetesting"
PYCRYPTO="pycryptodome-3.4.5"
PYCNIC_ZIP="pycnic-0.1.1-extensivetesting"
PYCNIC="pycnic-0.1.1"

# embedded python extensions
HTTPLIB2="httplib2-0.11.3"
UUIDLIB="uuid-1.30"
PYASN="pyasn1-0.4.2"
PYSMI="pysmi-0.2.2"
PLY="ply-3.11"
PYCRYPTODOMEX="pycryptodomex-3.5.1"
PYSNMP="pysnmp-4.4.4"
PYMSSQL="pymssql-2.1.3"
FREETDS="freetds-0.91"
ECDSA="ecdsa-0.13"
PIL="Imaging-1.1.7"
APPDIRS="appdirs-1.4.3"
SETUPTOOLS="setuptools-40.0.0"
SUDS="suds-jurko-0.6"
SUDS_ZIP="suds-jurko-0.6-extensivetesting"
CERTIFI="certifi-2018.1.18"
CHARTED="chardet-3.0.4"
REQUESTS="requests-2.18.4"
NTLM="python-ntlm-1.1.0"
KERBEROS="kerberos-1.3.0"
POSTGRESQL="psycopg2-2.7.4"
POSTGRESQL8="psycopg2-2.6.1"
XLRD="xlrd-1.1.0"
XLWT="xlwt-1.3.0"
OPENXL="openpyxl-2.5.2"
ETXMLFILE="et_xmlfile-1.0.1"
JDCAL="jdcal-1.3"
SETUPTOOLS_GIT="setuptools-git-1.2"
SCANDIR="scandir-1.7"
PBR="pbr-4.0.1"
PYTZ="pytz-2018.3"
PYJENKINS="jenkinsapi-0.3.6"
GITDB2="gitdb2-2.0.3"
PYGIT="GitPython-2.1.9"
SMMAP2="smmap2-2.0.3"
XML2DICT="xmltodict-0.11.0"
ISODATE="isodate-0.6.0"
PYWINRM="pywinrm-0.3.0"
PYTEST="pytest-runner-4.2"
SETUPTOOLS_SCM="setuptools_scm-1.17.0"
PYTE="pyte-0.8.0"
WCWIDTH="wcwidth-0.1.7"
PYSPHERE="pysphere-0.1.9"
SIX="six-1.11.0"
PYCHEF="PyChef-0.3.0"
IDNA="idna-2.6"
ENUM34="enum34-1.1.6"
IPADDRESS="ipaddress-1.0.19"
PYCPARSER="pycparser-2.18"
CFFI="cffi-1.11.5"
PYPARSING="pyparsing-2.2.0"
ORDEREDDICT="ordereddict-1.1"
NTLM_AUTH="ntlm-auth-1.1.0"
REQUESTS_NTLM="requests_ntlm-1.1.0"
PY_NTLM3="python-ntlm3-1.0.2"
ASN1CRYPTO="asn1crypto-0.24.0"
PACKAGING="packaging-17.1"
CRYPTOGRAPHY="cryptography-2.3"
PYNACL="PyNaCl-1.2.1"
BCRYPT="bcrypt-3.1.4"
PARAMIKO="paramiko-2.4.1"
JSONPATH="jsonpath-ng-1.4.3"
WRAPT="wrapt-1.10.11"
PYAML="pyaml-17.12.1"
MARKUP="MarkupSafe-1.0"
JINGA="Jinja2-2.10"
ANSIBLE="ansible-2.5.0"
URLLIB3="urllib3-1.22"
PYKAFKA="kafka-python-1.4.2"
PYSNAPPY="python-snappy-0.5.2"

# websocket module for apache, only for centos 5/6
MOD_WSTUNNEL="mod_proxy_wstunnel.so"

CURL="curl-7.60.0"

usage(){
	echo "Usage: $0 filename"
	exit 1
}

exit_on_error()
{
    rm -rf "$APP_PATH"/default.cfg.tmp 1>> "$LOG_FILE" 2>&1
    exit 1
}

# add some protections before to start installation
if [ ! -d "$PKG_PATH" ]; then
        echo 'PKG folder is missing!'
        exit_on_error
fi
if [ ! -d "$APP_SRC_PATH" ]; then
        echo 'Source folder is missing!'
        exit_on_error
fi

echo "===> Installation called" >> "$LOG_FILE"

# Get system name: redhat or centos and release version
echo -n "* Detecting the operating system"
OS_NAME=$(cat /etc/redhat-release | awk {'print $1}' | awk '{print tolower($0)}' )
OS_RELEASE=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release))
# the sed is here to extract the first character of the string
OS_RELEASE=$( echo $OS_RELEASE | sed -r 's/(.)[^.]*\.?/\L\1/g' )

if [[ $OS_RELEASE == 7* ]]; then
    OS_RELEASE=7
fi

if [ "$OS_NAME" != "red" -a "$OS_NAME" != "centos" -a "$OS_RELEASE" -lt 5 ]; then
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


if [ "$OS_RELEASE" != "7" ]; then
    TAR_BIN="/bin/tar"
    CAT_BIN="/bin/cat"
    PWD_BIN="/bin/pwd"
    LS_BIN="/bin/ls"
fi

# search because it is mandatory during the installation
echo -n "* Detecting mandatory commands"
[ -f "$PERL_BIN" ] || { echo_failure; echo; echo "perl is missing" >> "$LOG_FILE"; exit_on_error ;}
[ -f "$PYBIN" ] || { echo_failure; echo; echo "python is missing" >> "$LOG_FILE"; exit_on_error ;}
[ -f "$YUM_BIN" ] || { echo_failure; echo; echo "yum command is missing" >> "$LOG_FILE"; exit_on_error ;}
[ -f "$CAT_BIN" ] || { echo_failure; echo; echo "cat command is missing" >> "$LOG_FILE"; exit_on_error ;}
[ -f "$PWD_BIN" ] || { echo_failure; echo; echo "pwd command is missing" >> "$LOG_FILE"; exit_on_error ;}
[ -f "$LS_BIN" ] || { echo_failure; echo; echo "ls command is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo

# logging version in log file
cat /etc/redhat-release 1>> "$LOG_FILE" 2>&1
$PYBIN --version 1>> "$LOG_FILE" 2>&1

rm -rf "$APP_PATH"/$HTTPLIB2/ 1>> "$LOG_FILE" 2>&1
rm -rf "$APP_PATH"/default.cfg.tmp 1>> "$LOG_FILE" 2>&1
cp -rf "$APP_PATH"/default.cfg "$APP_PATH"/default.cfg.tmp 1>> "$LOG_FILE" 2>&1
$PERL_BIN -pi -e "s/^INSTALL=(.+)$/INSTALL=\"\1\"/g" "$APP_PATH"/default.cfg.tmp
source "$APP_PATH"/default.cfg.tmp
PRODUCT_SVC_CTRL=$ADMIN_SVC_CTL

echo -n "* Detecting primary network address"
if [ "$SILENT" == "update" ]; then
    echo -n " ($EXTERNAL_IP)"
else
    PRIMARY_IP=$(ip addr show | grep -E '^\s*inet' | grep -m1 global | awk '{ print $2 }' | sed 's|/.*||')
    if [ "$PRIMARY_IP" == "" ]; then
        echo_failure; echo
        echo "No primary ip detected" >> "$LOG_FILE"
        exit_on_error
    else
        echo -n " ($PRIMARY_IP)"
    fi
fi
echo_success; echo

if echo "$INSTALL" | egrep -q "[[:space:]]" ; then
        echo 'Whitespace on install path not supported'
        exit_on_error
fi

if [ "$SILENT" == "custom" ]; then
	echo -n "* Download automatically all missing packages? [$DOWNLOAD_MISSING_PACKAGES]"
	read reply
	DL_MISSING_PKGS="${reply}"
	if [ -z "$reply" ]; then
		DL_MISSING_PKGS=$DOWNLOAD_MISSING_PACKAGES
	fi
	$PERL_BIN -i -pe "s/DOWNLOAD_MISSING_PACKAGES=.*/DOWNLOAD_MISSING_PACKAGES=$(echo $DL_MISSING_PKGS | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg

	echo -n "* Install automatically all embedded packages? [$INSTALL_EMBEDDED_PACKAGES]"
	read reply
	INSTALL_EMBEDDED_PKGS="${reply}"
	if [ -z "$reply" ]; then
		INSTALL_EMBEDDED_PKGS=$INSTALL_EMBEDDED_PACKAGES
	fi
	$PERL_BIN -i -pe "s/INSTALL_EMBEDDED_PACKAGES=.*/INSTALL_EMBEDDED_PACKAGES=$(echo $INSTALL_EMBEDDED_PKGS | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg

	echo -n "* In which directory do you want to install the $APP_NAME product? [$INSTALL]"
	read reply
	INSTALL_PATH="${reply}"
	if [ -z "$reply" ]; then
		INSTALL_PATH="$INSTALL"
	fi
	$PERL_BIN -i -pe "s/INSTALL=.*/INSTALL=$(echo "$INSTALL_PATH" | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg

	echo -n "* What is the directory that contains the init scripts? [$INITD]"
	read reply
	INITD_PATH="${reply}"
	if [ -z "$reply" ]; then
		INITD_PATH=$INITD
	fi
	$PERL_BIN -i -pe "s/INITD=.*/INITD=$(echo $INITD_PATH | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg

	echo -n "* What is the external ip of your server? [$PRIMARY_IP]"
	read reply
	EXT_IP="${reply}"
	if [ -z "$reply" ]; then
		EXT_IP=$PRIMARY_IP
	fi
	$PERL_BIN -i -pe "s/EXTERNAL_IP=.*/EXTERNAL_IP=$EXT_IP/g" "$APP_PATH"/default.cfg

	echo -n "* What is the FQDN associated to the external ip of your server? [$PRIMARY_IP]"
	read reply
	EXT_FQDN="${reply}"
	if [ -z "$reply" ]; then
		EXT_FQDN=$PRIMARY_IP
	fi
	$PERL_BIN -i -pe "s/FQDN=.*/FQDN=$EXT_FQDN/g" "$APP_PATH"/default.cfg

	echo -n "* What is the database name? [$DATABASE_NAME]"
	read reply
	DB_NAME="${reply}"
	if [ -z "$reply" ]; then
		DB_NAME=$DATABASE_NAME
	fi
	$PERL_BIN -i -pe "s/DATABASE_NAME=.*/DATABASE_NAME=$DB_NAME/g" "$APP_PATH"/default.cfg

	echo -n "* What is the table prefix? [$DATABASE_TABLE_PREFIX]"
	read reply
	TABLE_PREFIX="${reply}"
	if [ -z "$reply" ]; then
		TABLE_PREFIX=$DATABASE_TABLE_PREFIX
	fi
	$PERL_BIN -i -pe "s/DATABASE_TABLE_PREFIX=.*/DATABASE_TABLE_PREFIX=$TABLE_PREFIX/g" "$APP_PATH"/default.cfg

	echo -n "* What is the ip of your mysql/mariadb server? [$MYSQL_IP]"
	read reply
	SQL_IP="${reply}"
	if [ -z "$reply" ]; then
		SQL_IP=$MYSQL_IP
	fi
	$PERL_BIN -i -pe "s/MYSQL_IP=.*/MYSQL_IP=$SQL_IP/g" "$APP_PATH"/default.cfg

	echo -n "* What is the login to connect to your mysql/mariadb server? [$MYSQL_USER]"
	read reply
	SQL_USER="${reply}"
	if [ -z "$reply" ]; then
		SQL_USER=$MYSQL_USER
	fi
	$PERL_BIN -i -pe "s/MYSQL_USER=.*/MYSQL_USER=$SQL_USER/g" "$APP_PATH"/default.cfg

	echo -n "* What is the password of previous user to connect to your mysql/mariadb server? [$MYSQL_PWD]"
	read reply
	SQL_PWD="${reply}"
	if [ -z "$reply" ]; then
		SQL_PWD=$MYSQL_PWD
	fi
	$PERL_BIN -i -pe "s/MYSQL_PWD=.*/MYSQL_PWD=$SQL_PWD/g" "$APP_PATH"/default.cfg

	echo -n "* What is the sock file of your mysql/mariadb server? [$MYSQL_SOCK]"
	read reply
	SQL_SOCK="${reply}"
	if [ -z "$reply" ]; then
		SQL_SOCK=$MYSQL_SOCK
	fi
	$PERL_BIN -i -pe "s/MYSQL_SOCK=.*/MYSQL_SOCK=$(echo $SQL_SOCK| sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg

	echo -n "* Do you want to configure iptables automatically? [$CONFIG_IPTABLES]"
	read reply
	FW_CONFIG="${reply}"
	if [ -z "$reply" ]; then
		FW_CONFIG=$CONFIG_IPTABLES
	fi
	$PERL_BIN -i -pe "s/CONFIG_IPTABLES=.*/CONFIG_IPTABLES=$FW_CONFIG/g" "$APP_PATH"/default.cfg

	echo -n "* Do you want to configure php automatically? [$CONFIG_PHP]"
	read reply
	PHP_CONFIG="${reply}"
	if [ -z "$reply" ]; then
		PHP_CONFIG=$CONFIG_PHP
	fi
	$PERL_BIN -i -pe "s/CONFIG_PHP=.*/CONFIG_PHP=$PHP_CONFIG/g" "$APP_PATH"/default.cfg

	if [ "$PHP_CONFIG" = "Yes" ]; then
		echo -n "* Where is your php conf file? [$PHP_CONF]"
		read reply
		PHP_PATH="${reply}"
		if [ -z "$reply" ]; then
			PHP_PATH=$PHP_CONF
		fi
		$PERL_BIN -i -pe "s/PHP_CONF=.*/PHP_CONF=$(echo $PHP_PATH | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg
	fi

	echo -n "* Do you want to configure apache automatically? [$CONFIG_APACHE]"
	read reply
	WEB_CONFIG="${reply}"
	if [ -z "$reply" ]; then
		WEB_CONFIG=$CONFIG_APACHE
	fi
	$PERL_BIN -i -pe "s/CONFIG_APACHE=.*/CONFIG_APACHE=$WEB_CONFIG/g" "$APP_PATH"/default.cfg

	if [ "$WEB_CONFIG" = "Yes" ]; then
		echo -n "* What is the directory that contains the httpd conf file? [$HTTPD_CONF]"
		read reply
		HTTPD_PATH="${reply}"
		if [ -z "$reply" ]; then
			HTTPD_PATH=$HTTPD_CONF
		fi
		$PERL_BIN -i -pe "s/HTTPD_CONF=.*/HTTPD_CONF=$(echo $HTTPD_PATH | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg

		echo -n "* What is the directory that contains the httpd virtual host conf files? [$HTTPD_VS_CONF]"
		read reply
		HTTPD_VS_CONF_PATH="${reply}"
		if [ -z "$reply" ]; then
			HTTPD_VS_CONF_PATH=$HTTPD_VS_CONF
		fi
		$PERL_BIN -i -pe "s/HTTPD_VS_CONF=.*/HTTPD_VS_CONF=$(echo $HTTPD_VS_CONF_PATH | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$APP_PATH"/default.cfg
	fi

	echo -n "* Do you want to configure selinux automatically? [$CONFIG_SELINUX]"
	read reply
	SELINUX_CONFIG="${reply}"
	if [ -z "$reply" ]; then
		SELINUX_CONFIG=$CONFIG_SELINUX
	fi
	$PERL_BIN -i -pe "s/CONFIG_SELINUX=.*/CONFIG_SELINUX=$SELINUX_CONFIG/g" "$APP_PATH"/default.cfg

	echo -n "* What is the path of the openssl binary? [$OPENSSL]"
	read reply
	SSL_BIN="${reply}"
	if [ -z "$reply" ]; then
		SSL_BIN=$OPENSSL
	fi
	$PERL_BIN -i -pe "s/OPENSSL=.*/OPENSSL=$(echo $SSL_BIN | sed -e 's/[]\/()$*.^|[]/\\&/g' )/g" "$APP_PATH"/default.cfg
else
	DL_MISSING_PKGS=$DOWNLOAD_MISSING_PACKAGES
    INSTALL_EMBEDDED_PKGS=$INSTALL_EMBEDDED_PACKAGES
	INSTALL_PATH="$INSTALL"
	INITD_PATH=$INITD
	EXT_IP=$EXTERNAL_IP
	EXT_FQDN=$FQDN
	DB_NAME=$DATABASE_NAME
	TABLE_PREFIX=$DATABASE_TABLE_PREFIX
	SQL_IP=$MYSQL_IP
	SQL_USER=$MYSQL_USER
	SQL_PWD=$MYSQL_PWD
	SQL_SOCK=$MYSQL_SOCK
	FW_CONFIG=$CONFIG_IPTABLES
	PHP_CONFIG=$CONFIG_PHP
	PHP_PATH=$PHP_CONF
	WEB_CONFIG=$CONFIG_APACHE
	HTTPD_PATH=$HTTPD_CONF
	HTTPD_VS_CONF_PATH=$HTTPD_VS_CONF
	SELINUX_CONFIG=$CONFIG_SELINUX
	SSL_BIN=$OPENSSL
    if [ "$SILENT" == "install" ]; then
        EXT_IP=$PRIMARY_IP
        EXT_FQDN=$PRIMARY_IP
    fi
fi

echo "===> default cfg" >> "$LOG_FILE"
$CAT_BIN "$APP_PATH"/default.cfg.tmp >> "$LOG_FILE"

# prepare
if [ "$SILENT" == "custom" -o  "$SILENT" == "install" ]; then
	if [ -f "$INSTALL_PATH"/current/VERSION ]; then
		echo "A $APP_NAME server already exists on this server!"
		echo "Bye bye"
		exit 1
	fi
fi

if [ "$DL_MISSING_PKGS" = "Yes" ]; then
    echo -ne "* Adding network tools                \r" 
	$YUM_BIN -y install vim net-snmp-utils unzip zip gmp wget curl ntp nmap bind-utils 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages httpd and more with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
	echo -ne "* Adding openssl                \r" 
	$YUM_BIN -y install postfix dos2unix openssl openssl-devel tcpdump mlocate  1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages basics with yum" >> "$LOG_FILE"
        exit_on_error
    fi
        
    echo -ne "* Adding mariadb                \r" 
	if [ "$OS_RELEASE" == "7" ]; then
		$YUM_BIN -y install mariadb-server mariadb mariadb-devel 1>> "$LOG_FILE" 2>&1
	else
		$YUM_BIN -y install mysql-server mysql 1>> "$LOG_FILE" 2>&1
	fi
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages mysql with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
    echo -ne "* Adding httpd                \r" 
	$YUM_BIN -y install httpd mod_ssl php php-mysql php-gd php-pear  1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages httpd and more with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
	echo -ne "* Adding python                \r"
	$YUM_BIN -y install python-lxml MySQL-python policycoreutils-python python-setuptools python-ldap PyYAML 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages python and more with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
	echo -ne "* Adding gcc                \r"
	$YUM_BIN -y install gcc python-devel Cython gcc-c++ 1>> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages gcc and more with yum" >> "$LOG_FILE"
        exit_on_error
    fi

	echo -ne "* Adding java                \r"
	$YUM_BIN -y install java git libffi-devel >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages java and more with yum" >> "$LOG_FILE"
        exit_on_error
    fi

	echo -ne "* Adding images                \r"
	$YUM_BIN -y install libpng-devel libjpeg-devel zlib-devel freetype-devel lcms-devel tk-devel tkinter >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download lib png with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
	echo -ne "* Adding postgresql                \r"
	$YUM_BIN -y install postgresql postgresql-libs postgresql-devel >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download postgresql with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
	echo -ne "* Adding snappy                \r"
	$YUM_BIN -y install snappy-devel >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo_failure; echo
        echo "Unable to download packages libsnappy-devel with yum" >> "$LOG_FILE"
        exit_on_error
    fi
    
	# chkconfig
	if [ "$OS_RELEASE" == "7" ]; then
		chmod g-wx,o-wx ~/.python-eggs 1>> "$LOG_FILE" 2>&1
		systemctl enable $HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
		systemctl enable $MARIADB_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
	else
		chkconfig $HTTPD_SERVICE_NAME on 345 1>> "$LOG_FILE" 2>&1
		chkconfig $MYSQL_SERVICE_NAME on 345 1>> "$LOG_FILE" 2>&1
	fi

	echo_success; echo
fi

# search because it is mandatory during the installation
echo -n "* Detecting system commands"
[ -f "$UNZIP_BIN" ] || { echo_failure; echo; echo "unzip command is missing" >> "$LOG_FILE"; exit_on_error ;}
[ -f "$TAR_BIN" ] || { echo_failure; echo; echo "tar command is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo


if [ "$INSTALL_EMBEDDED_PKGS" = "Yes" ]; then

    echo -ne "* Installing six                 \r"
    $TAR_BIN xvf $PKG_PATH/$SIX.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$SIX/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SIX/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing appdirs                 \r"
    $TAR_BIN xvf $PKG_PATH/$APPDIRS.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$APPDIRS/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$APPDIRS/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pyparsing                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYPARSING.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYPARSING/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYPARSING/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing packaging                 \r"
    $TAR_BIN xvf $PKG_PATH/$PACKAGING.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PACKAGING/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PACKAGING/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing setuptools                 \r"
    cd $APP_PATH
    $UNZIP_BIN $PKG_PATH/$SETUPTOOLS.zip  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$SETUPTOOLS/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SETUPTOOLS/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing httplib2                 \r"
	$TAR_BIN xvf $PKG_PATH/$HTTPLIB2.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$HTTPLIB2/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
    cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$HTTPLIB2/ 1>> "$LOG_FILE" 2>&1
	
	echo -ne "* Installing uuid                 \r"
	$TAR_BIN xvf $PKG_PATH/$UUIDLIB.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$UUIDLIB/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$UUIDLIB/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing pycrypto                 \r"
    cd $APP_PATH
	$UNZIP_BIN $PKG_PATH/$PYCRYPTO_ZIP.zip  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYCRYPTO/
	$PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYCRYPTO/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing pyasn                 \r"
    rm -rf /usr/lib/python2.6/site-packages/pyasn1* 1>> "$LOG_FILE" 2>&1
    rm -rf /usr/lib/python2.7/site-packages/pyasn1* 1>> "$LOG_FILE" 2>&1
	$TAR_BIN xvf $PKG_PATH/$PYASN.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PYASN/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYASN/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing ply                 \r"
	$TAR_BIN xvf $PKG_PATH/$PLY.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PLY/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PLY/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing pysmi                 \r"
	$TAR_BIN xvf $PKG_PATH/$PYSMI.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PYSMI/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYSMI/ 1>> "$LOG_FILE" 2>&1

	echo -ne "* Installing pycryptodomex                 \r"
	$TAR_BIN xvf $PKG_PATH/$PYCRYPTODOMEX.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PYCRYPTODOMEX/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYCRYPTODOMEX/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing pysnmp                 \r"
	$TAR_BIN xvf $PKG_PATH/$PYSNMP.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PYSNMP/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYSNMP/ 1>> "$LOG_FILE" 2>&1

	echo -ne "* Installing freetds                 \r"
	$TAR_BIN xvf $PKG_PATH/$FREETDS.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$FREETDS/
	./configure --enable-msdblib 1>> "$LOG_FILE" 2>&1
	make 1>> "$LOG_FILE" 2>&1
	make install 1>> "$LOG_FILE" 2>&1
    cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$FREETDS/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing setuptools_git                 \r"
	$TAR_BIN xvf $PKG_PATH/$SETUPTOOLS_GIT.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$SETUPTOOLS_GIT/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SETUPTOOLS_GIT/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing pymssql                 \r"
	$TAR_BIN xvf $PKG_PATH/$PYMSSQL.tar.gz  1>> "$LOG_FILE" 2>&1
        cd $APP_PATH/$PYMSSQL/
	$PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	ln -s /usr/local/lib/libsybdb.so.5 /usr/lib/libsybdb.so.5  1>> "$LOG_FILE" 2>&1
	ldconfig 1>> "$LOG_FILE" 2>&1
    cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYMSSQL/ 1>> "$LOG_FILE" 2>&1

	echo -ne "* Installing ecdsa                 \r"
	$TAR_BIN xvf $PKG_PATH/$ECDSA.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ECDSA/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ECDSA/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pil                 \r"
	$TAR_BIN xvf $PKG_PATH/$PIL.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PIL/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PIL/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing selenium                 \r"
    cd $APP_PATH
    $UNZIP_BIN $PKG_PATH/$SELENIUM_ZIP.zip  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$SELENIUM/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SELENIUM/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing suds                 \r"
    cd $APP_PATH
    $UNZIP_BIN $PKG_PATH/$SUDS_ZIP.zip  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$SUDS/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SUDS/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing certifi                 \r"
    $TAR_BIN xvf $PKG_PATH/$CERTIFI.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$CERTIFI/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$CERTIFI/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing certifi                 \r"
    $TAR_BIN xvf $PKG_PATH/$CHARTED.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$CHARTED/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$CHARTED/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing requests                 \r"
    $TAR_BIN xvf $PKG_PATH/$REQUESTS.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$REQUESTS/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$REQUESTS/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing ntlm                 \r"
    $TAR_BIN xvf $PKG_PATH/$NTLM.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$NTLM/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$NTLM/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing kerberos                 \r"
    $TAR_BIN xvf $PKG_PATH/$KERBEROS.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$KERBEROS/
	$PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$KERBEROS/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing postgresql                 \r"
    if [ "$OS_RELEASE" == "7" ]; then
        $TAR_BIN xvf $PKG_PATH/$POSTGRESQL.tar.gz  1>> "$LOG_FILE" 2>&1
        cd $APP_PATH/$POSTGRESQL/
        $PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
        $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
        cd .. 1>> "$LOG_FILE" 2>&1
        rm -rf $APP_PATH/$POSTGRESQL/ 1>> "$LOG_FILE" 2>&1
    else
        $TAR_BIN xvf $PKG_PATH/$POSTGRESQL8.tar.gz  1>> "$LOG_FILE" 2>&1
        cd $APP_PATH/$POSTGRESQL8/
        $PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
        $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
        cd .. 1>> "$LOG_FILE" 2>&1
        rm -rf $APP_PATH/$POSTGRESQL8/ 1>> "$LOG_FILE" 2>&1
    fi
    
    echo -ne "* Installing xlrd                 \r"
    $TAR_BIN xvf $PKG_PATH/$XLRD.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$XLRD/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$XLRD/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing etxmlfile                 \r"
    $TAR_BIN xvf $PKG_PATH/$ETXMLFILE.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ETXMLFILE/
	$PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ETXMLFILE/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing jdcal                 \r"
    $TAR_BIN xvf $PKG_PATH/$JDCAL.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$JDCAL/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$JDCAL/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing openxl                 \r"
    $TAR_BIN xvf $PKG_PATH/$OPENXL.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$OPENXL/
	$PYBIN setup.py build 1>> "$LOG_FILE" 2>&1
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$OPENXL/ 1>> "$LOG_FILE" 2>&1

	echo -ne "* Installing libpqxx                 \r"
	if [ "$OS_RELEASE" != "7" ]; then
		rpm -ivh $PKG_PATH/libpqxx-4.0.1-2.el6.x86_64.rpm 1>> "$LOG_FILE" 2>&1
		rpm -ivh $PKG_PATH/libpqxx-devel-4.0.1-2.el6.x86_64.rpm 1>> "$LOG_FILE" 2>&1
	else
		rpm -ivh $PKG_PATH/libpqxx-4.0.1-1.el7.x86_64.rpm 1>> "$LOG_FILE" 2>&1
		rpm -ivh $PKG_PATH/libpqxx-devel-4.0.1-1.el7.x86_64.rpm 1>> "$LOG_FILE" 2>&1
	fi
    
    echo -ne "* Installing scandir                 \r"
    $TAR_BIN xvf $PKG_PATH/$SCANDIR.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$SCANDIR/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SCANDIR/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pycnic                 \r"
    cd $APP_PATH
    $UNZIP_BIN $PKG_PATH/$PYCNIC_ZIP.zip 1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYCNIC/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYCNIC/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing xlwt                 \r"
    $TAR_BIN xvf $PKG_PATH/$XLWT.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$XLWT/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$XLWT/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing isodate                 \r"
    $TAR_BIN xvf $PKG_PATH/$ISODATE.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ISODATE/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ISODATE/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing xml2dict                 \r"
    $TAR_BIN xvf $PKG_PATH/$XML2DICT.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$XML2DICT/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$XML2DICT/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing setuptools_scm                 \r"
    $TAR_BIN xvf $PKG_PATH/$SETUPTOOLS_SCM.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$SETUPTOOLS_SCM/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SETUPTOOLS_SCM/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pytest                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYTEST.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYTEST/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYTEST/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing wcwidth                 \r"
    $TAR_BIN xvf $PKG_PATH/$WCWIDTH.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$WCWIDTH/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$WCWIDTH/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pyte                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYTE.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYTE/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYTE/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pysphere                 \r"
    cd $APP_PATH
    $UNZIP_BIN $PKG_PATH/$PYSPHERE.zip  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PYSPHERE/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYSPHERE/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing pychef                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYCHEF.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYCHEF/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYCHEF/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing idna                 \r"
    $TAR_BIN xvf $PKG_PATH/$IDNA.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$IDNA/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$IDNA/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing enum34                 \r"
    $TAR_BIN xvf $PKG_PATH/$ENUM34.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ENUM34/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ENUM34/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing ipaddress                 \r"
    $TAR_BIN xvf $PKG_PATH/$IPADDRESS.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$IPADDRESS/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$IPADDRESS/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pycparser                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYCPARSER.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYCPARSER/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYCPARSER/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing cffi                 \r"
    $TAR_BIN xvf $PKG_PATH/$CFFI.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$CFFI/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$CFFI/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing ordereddict                 \r"
    $TAR_BIN xvf $PKG_PATH/$ORDEREDDICT.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ORDEREDDICT/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ORDEREDDICT/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing ntlm_auth                 \r"
    cd $APP_PATH
    $TAR_BIN xvf $PKG_PATH/$NTLM_AUTH.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$NTLM_AUTH/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$NTLM_AUTH/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing requests_ntlm                 \r"
    $TAR_BIN xvf $PKG_PATH/$REQUESTS_NTLM.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$REQUESTS_NTLM/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$REQUESTS_NTLM/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing py_ntlm3                 \r"
    $TAR_BIN xvf $PKG_PATH/$PY_NTLM3.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PY_NTLM3/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PY_NTLM3/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing pywinrm                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYWINRM.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYWINRM/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYWINRM/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing asn1crypto                 \r"
    $TAR_BIN xvf $PKG_PATH/$ASN1CRYPTO.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ASN1CRYPTO/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ASN1CRYPTO/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing cryptography                 \r"
    $TAR_BIN xvf $PKG_PATH/$CRYPTOGRAPHY.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$CRYPTOGRAPHY/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$CRYPTOGRAPHY/ 1>> "$LOG_FILE" 2>&1

	echo -ne "* Installing pynacl                 \r"
	$TAR_BIN xvf $PKG_PATH/$PYNACL.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYNACL/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYNACL/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing bcrypt                 \r"
	$TAR_BIN xvf $PKG_PATH/$BCRYPT.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$BCRYPT/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$BCRYPT/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing paramiko                 \r"
	$TAR_BIN xvf $PKG_PATH/$PARAMIKO.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PARAMIKO/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PARAMIKO/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing jsonpath_ng                 \r"
	$TAR_BIN xvf $PKG_PATH/$JSONPATH.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$JSONPATH/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$JSONPATH/ 1>> "$LOG_FILE" 2>&1
    
	echo -ne "* Installing wrapt                 \r"
	$TAR_BIN xvf $PKG_PATH/$WRAPT.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$WRAPT/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$WRAPT/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing pbr                \r"
    $TAR_BIN xvf $PKG_PATH/$PBR.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PBR/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PBR/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pytz                \r"
    $TAR_BIN xvf $PKG_PATH/$PYTZ.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYTZ/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYTZ/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing pyjenkins                \r"
    $TAR_BIN xvf $PKG_PATH/$PYJENKINS.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYJENKINS/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYJENKINS/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing smmap                \r"
    $TAR_BIN xvf $PKG_PATH/$SMMAP2.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$SMMAP2/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$SMMAP2/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing gitdb                \r"
    $TAR_BIN xvf $PKG_PATH/$GITDB2.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$GITDB2/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$GITDB2/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing pygit                \r"
    $TAR_BIN xvf $PKG_PATH/$PYGIT.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$PYGIT/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$PYGIT/ 1>> "$LOG_FILE" 2>&1
   
    echo -ne "* Installing markupsafe             \r"
    $TAR_BIN xvf $PKG_PATH/$MARKUP.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$MARKUP/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$MARKUP/ 1>> "$LOG_FILE" 2>&1
   
    echo -ne "* Installing jinga             \r"
    $TAR_BIN xvf $PKG_PATH/$JINGA.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$JINGA/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$JINGA/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing ansible                \r"
    $TAR_BIN xvf $PKG_PATH/$ANSIBLE.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$ANSIBLE/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$ANSIBLE/ 1>> "$LOG_FILE" 2>&1
    
    echo -ne "* Installing urllib3                \r"
    $TAR_BIN xvf $PKG_PATH/$URLLIB3.tar.gz  1>> "$LOG_FILE" 2>&1
	cd $APP_PATH/$URLLIB3/
	$PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
	cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$URLLIB3/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing python-snappy                \r"
    $TAR_BIN xvf $PKG_PATH/$PYSNAPPY.tar.gz  1>> "$LOG_FILE" 2>&1
        cd $APP_PATH/$PYSNAPPY/
        $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
        cd .. 1>> "$LOG_FILE" 2>&1
        rm -rf $APP_PATH/$PYSNAPPY/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing kafka-python                \r"
    $TAR_BIN xvf $PKG_PATH/$PYKAFKA.tar.gz  1>> "$LOG_FILE" 2>&1
        cd $APP_PATH/$PYKAFKA/
        $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
        cd .. 1>> "$LOG_FILE" 2>&1
        rm -rf $APP_PATH/$PYKAFKA/ 1>> "$LOG_FILE" 2>&1

    echo -ne "* Installing pyaml                 \r"
    $TAR_BIN xvf $PKG_PATH/$PYAML.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$PYAML/
    $PYBIN setup.py install 1>> "$LOG_FILE" 2>&1
    cd .. 1>> "$LOG_FILE" 2>&1
    rm -rf $APP_PATH/$PYAML/ 1>> "$LOG_FILE" 2>&1

	echo -ne "* Installing curl                  \r"
	$TAR_BIN xvf $PKG_PATH/$CURL.tar.gz  1>> "$LOG_FILE" 2>&1
    cd $APP_PATH/$CURL/
	./configure 1>> "$LOG_FILE" 2>&1
	make 1>> "$LOG_FILE" 2>&1
	make install 1>> "$LOG_FILE" 2>&1
    cd .. 1>> "$LOG_FILE" 2>&1
	rm -rf $APP_PATH/$CURL/ 1>> "$LOG_FILE" 2>&1

	echo_success; echo
fi

echo -n "* Detecting Apache"
[ -f "$HTTPD" ] || { echo_failure; echo; echo "$HTTPD_SERVICE_NAME is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo

echo -n "* Detecting MySQL/MariaDB"
[ -f "$MYSQLD" ] || { echo_failure; echo; echo "$MYSQL_SERVICE_NAME is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo

echo -n "* Detecting Postfix"
[ -f "$POSTFIX" ] || { echo_failure; echo; echo "$POSTFIX_SERVICE_NAME is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo

echo -n "* Detecting Openssl"
[ -f "$OPENSSL" ] || { echo_failure; echo; echo "openssl is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo

echo -n "* Detecting Php"
[ -f "$PHP_CONF" ] || { echo_failure; echo; echo "php is missing" >> "$LOG_FILE"; exit_on_error ;}
echo_success; echo

# copy source
echo -n "* Preparing destination"
if [ "$SILENT" == "custom" -o "$SILENT" == "install" ]; then
	rm -rf "$INSTALL_PATH"/$APP_NAME 1>> "$LOG_FILE" 2>&1
	rm -rf "$INSTALL_PATH"/$APP_NAME-$PRODUCT_VERSION 1>> "$LOG_FILE" 2>&1
fi
mkdir -p "$INSTALL_PATH" 1>> "$LOG_FILE" 2>&1
echo_success; echo

# checking space before install
echo -n "* Checking space left on $INSTALL_PATH"
FREE_SPACE="$(df -P $INSTALL_PATH | tail -1 | awk '{print $4}')"
if [[ $FREE_SPACE -lt $MIN_SPACE_LEFT ]]; then
    echo_failure; echo
    echo "Less than 1GB free space left, $FREE_SPACE bytes"
    exit_on_error
fi
echo_success; echo

echo -n "* Copying source files"
cp -rf "$APP_SRC_PATH"/ "$INSTALL_PATH"/ 1>> "$LOG_FILE" 2>&1
mv -f "$INSTALL_PATH"/$APP_NAME "$INSTALL_PATH"/$APP_NAME-$PRODUCT_VERSION 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
	echo_failure; echo
	echo "Unable to copy sources" >> "$LOG_FILE"
	exit_on_error
fi
rm -f "$INSTALL_PATH"/current 1>> "$LOG_FILE" 2>&1
ln -s "$INSTALL_PATH"/$APP_NAME-$PRODUCT_VERSION "$INSTALL_PATH"/current 1>> "$LOG_FILE" 2>&1
echo_success; echo

# Install the product as service
echo -n "* Adding startup service"
if [ "$OS_RELEASE" == "7" ]; then
	# update the path, espace the path with sed and the db name 
	cp -rf "$INSTALL_PATH"/current/Scripts/svr.$OS_NAME$OS_RELEASE $SYSTEMD/$PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
	$PERL_BIN -p -i -e  "s/^PIDFile=.*/PIDFile=$(echo "$INSTALL_PATH" | sed -e 's/[]\/()$*.^|[]/\\&/g')\/current\/Var\/Run\/$PRODUCT_SVC_NAME.pid/g;" $SYSTEMD/$PRODUCT_SVC_NAME.service

	$PERL_BIN -p -i -e  "s/^APP_PATH=.*/APP_PATH=$(echo "$INSTALL_PATH" | sed -e 's/[]\/()$*.^|[]/\\&/g')/g;"  "$INSTALL_PATH"/current/Scripts/ctl.$OS_NAME$OS_RELEASE
	$PERL_BIN -p -i -e  "s/^DB_NAME=.*/DB_NAME=$DB_NAME/g;" "$INSTALL_PATH"/current/Scripts/ctl.$OS_NAME$OS_RELEASE
    rm -f /usr/sbin/"$PRODUCT_SVC_CTRL" 1>> "$LOG_FILE" 2>&1
	ln -s "$INSTALL_PATH"/current/Scripts/ctl.$OS_NAME$OS_RELEASE /usr/sbin/"$PRODUCT_SVC_CTRL" 1>> "$LOG_FILE" 2>&1

	systemctl enable $PRODUCT_SVC_NAME.service 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to activate as a service" >> "$LOG_FILE"
		exit_on_error
	fi
else
	# update the path, espace the path with sed and the db name 
	# and make a symoblic link on init.d
	$PERL_BIN -p -i -e  "s/^APP_PATH=.*/APP_PATH=$(echo "$INSTALL_PATH" | sed -e 's/[]\/()$*.^|[]/\\&/g')/g;"  "$INSTALL_PATH"/current/Scripts/svr.$OS_NAME$OS_RELEASE
	$PERL_BIN -p -i -e  "s/^DB_NAME=.*/DB_NAME=$DB_NAME/g;" "$INSTALL_PATH"/current/Scripts/svr.$OS_NAME$OS_RELEASE

    rm -f $INITD_PATH/$PRODUCT_SVC_NAME 1>> "$LOG_FILE" 2>&1
	ln -s "$INSTALL_PATH"/current/Scripts/svr.$OS_NAME$OS_RELEASE $INITD_PATH/$PRODUCT_SVC_NAME 1>> "$LOG_FILE" 2>&1
    rm -f /usr/sbin/"$PRODUCT_SVC_CTRL" 1>> "$LOG_FILE" 2>&1
	ln -s "$INSTALL_PATH"/current/Scripts/svr.$OS_NAME$OS_RELEASE /usr/sbin/"$PRODUCT_SVC_CTRL" 1>> "$LOG_FILE" 2>&1

	# activate the service
	chkconfig $PRODUCT_SVC_NAME on 345 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to activate as a service" >> "$LOG_FILE"
		exit_on_error
	fi
fi
echo_success; echo

echo -n "* Adding cron scripts"

$PERL_BIN -p -i -e  "s/^INSTALL_PATH=.*/INSTALL_PATH=$(echo "$INSTALL_PATH" | sed -e 's/[]\/()$*.^|[]/\\&/g')/g;"  "$INSTALL_PATH"/current/Scripts/cron/cron.backup-tables
rm -f $CRON_DAILY/$PRODUCT_SVC_NAME-tables 1>> "$LOG_FILE" 2>&1
ln -s "$INSTALL_PATH"/current/Scripts/cron/cron.backup-tables $CRON_DAILY/$PRODUCT_SVC_NAME-tables 1>> "$LOG_FILE" 2>&1
    
if [ "$CLEANUP_BACKUPS" = "Yes" ]; then
	$PERL_BIN -p -i -e  "s/^INSTALL_PATH=.*/INSTALL_PATH=$(echo "$INSTALL_PATH" | sed -e 's/[]\/()$*.^|[]/\\&/g')/g;"  "$INSTALL_PATH"/current/Scripts/cron/cron.cleanup-backups
	$PERL_BIN -p -i -e  "s/^OLDER_THAN=.*/OLDER_THAN=$BACKUPS_OLDER_THAN/g;"  "$INSTALL_PATH"/current/Scripts/cron/cron.cleanup-backups
    
    rm -f $CRON_WEEKLY/$PRODUCT_SVC_NAME-backups 1>> "$LOG_FILE" 2>&1
    ln -s "$INSTALL_PATH"/current/Scripts/cron/cron.cleanup-backups $CRON_WEEKLY/$PRODUCT_SVC_NAME-backups 1>> "$LOG_FILE" 2>&1
fi
echo_success; echo
    
# Updating the config file
echo -n "* Updating configuration files"
$PERL_BIN -i -pe "s/^ip=.*/ip=$SQL_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^user=.*/user=$SQL_USER/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^pwd=.*/pwd=$SQL_PWD/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^sock=.*/sock=$(echo $SQL_SOCK | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^fqdn=.*/fqdn=$EXT_FQDN/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^db=.*/db=$DB_NAME/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^table-prefix=.*/table-prefix=$TABLE_PREFIX/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^ip-ext=.*/ip-ext=$EXT_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^ip-wsu=.*/ip-wsu=$LOCALHOST_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^ip-esi=.*/ip-esi=$LOCALHOST_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^ip-tsi=.*/ip-tsi=$LOCALHOST_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^ip-psi=.*/ip-psi=$LOCALHOST_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^ip-asi=.*/ip-asi=$LOCALHOST_IP/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^mode-demo=.*/mode-demo=$MODE_DEMO/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^current-adapters=.*/current-adapters=$CURRENT_ADAPTERS/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^current-libraries=.*/current-libraries=$CURRENT_LIBRARIES/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^generic-adapters=.*/generic-adapters=$GENERIC_ADAPTERS/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^generic-libraries=.*/generic-libraries=$GENERIC_LIBRARIES/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^tar=.*/tar=$(echo $TAR_BIN | sed -e 's/[]\/()$*.^|[]/\\&/g')/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^insert-test-statistics=.*/insert-test-statistics=$DATABASE_INSERT_TEST_STATISTICS/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^read-test-statistics=.*/read-test-statistics=$DATABASE_READ_TEST_STATISTICS/g" "$INSTALL_PATH"/current/settings.ini
$PERL_BIN -i -pe "s/^test-environment-encrypted=.*/test-environment-encrypted=$DATABASE_ENCRYPT_TEST_ENV/g" "$INSTALL_PATH"/current/settings.ini
dos2unix "$INSTALL_PATH"/current/settings.ini 1>> "$LOG_FILE" 2>&1

$PERL_BIN -i -pe "s/LWF_DB_HOST.*/LWF_DB_HOST='$SQL_IP';/g" "$INSTALL_PATH"/current/Web/include/config.php
$PERL_BIN -i -pe "s/LWF_DB_USER.*/LWF_DB_USER='$SQL_USER';/g" "$INSTALL_PATH"/current/Web/include/config.php
$PERL_BIN -i -pe "s/LWF_DB_PWD.*/LWF_DB_PWD='$SQL_PWD';/g" "$INSTALL_PATH"/current/Web/include/config.php
$PERL_BIN -i -pe "s/__LWF_DB_NAME.*/__LWF_DB_NAME='$DB_NAME';/g" "$INSTALL_PATH"/current/Web/include/config.php
$PERL_BIN -i -pe "s/__LWF_DB_PREFIX.*/__LWF_DB_PREFIX='$TABLE_PREFIX';/g" "$INSTALL_PATH"/current/Web/include/config.php
dos2unix "$INSTALL_PATH"/current/Web/include/config.php 1>> "$LOG_FILE" 2>&1

# workaround, disable PrivateTmp feature for apache on centos7 only
# authorize to upload file from apache
if [ "$OS_RELEASE" == "7" ]; then
    cp -rf $SYSTEMD/$HTTPD_SERVICE_NAME.service $SYSTEMD/$HTTPD_SERVICE_NAME.service.backup 1>> "$LOG_FILE" 2>&1
    $PERL_BIN -i -pe "s/PrivateTmp=true/PrivateTmp=false/g" $SYSTEMD/$HTTPD_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
    systemctl daemon-reload 1>> "$LOG_FILE" 2>&1 
fi
 
echo_success; echo

# echo -n "* Creating $PRODUCT_SVC_NAME user"
# useradd $PRODUCT_SVC_NAME 1>> "$LOG_FILE" 2>&1
# echo_success; echo

# set folders rights
echo -n "* Updating folders rights"
chown -R $HTTP_USER:$HTTP_USER "$INSTALL_PATH"/current/Var/Tests/
chown -R $HTTP_USER:$HTTP_USER "$INSTALL_PATH"/current/Web/
chown -R $HTTP_USER:$HTTP_USER "$INSTALL_PATH"/current/Scripts/
chown -R $HTTP_USER:$HTTP_USER "$INSTALL_PATH"/current/Docs/
chown -R $HTTP_USER:$HTTP_USER "$INSTALL_PATH"/current/Packages/

# 755 only on folder for apache
chmod 755 "$INSTALL_PATH"/current/Scripts/
find "$INSTALL_PATH"/current/Web/ -type d -exec chmod 755 "{}" \;
find "$INSTALL_PATH"/current/Docs/ -type d -exec chmod 755 "{}" \;
find "$INSTALL_PATH"/current/Packages/ -type d -exec chmod 755 "{}" \;

echo_success; echo

if [ "$FW_CONFIG" = "Yes" ]; then
	if [ "$OS_RELEASE" == "7" ]; then
		systemctl enable $IPTABLE_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
	else
		chkconfig $IPTABLE_SERVICE_NAME on 345 1>> "$LOG_FILE" 2>&1
	fi

	echo -n "* Updating iptables"
	cp -rf $IPTABLE_CONF/iptables $IPTABLE_CONF/iptables.backup 1>> "$LOG_FILE" 2>&1
	chmod +x "$APP_SRC_PATH"/Scripts/iptables.rules
	"$APP_SRC_PATH"/Scripts/iptables.rules 1>> "$LOG_FILE" 2>&1
	if [ $? -ne 0 ]; then
		echo_failure; echo
		echo "Unable to configure iptables" >> "$LOG_FILE"
		exit_on_error
	fi
	echo_success; echo
fi

if [ "$PHP_CONFIG" = "Yes" ]; then
	echo -n "* Updating php configuration"
	cp -rf $PHP_PATH $PHP_PATH.backup 1>> "$LOG_FILE" 2>&1
	$PERL_BIN -i -pe "s/post_max_size.*/post_max_size = $PHP_MAX_SIZE/g" $PHP_PATH
	$PERL_BIN -i -pe "s/upload_max_filesize.*/upload_max_filesize = $PHP_MAX_SIZE/g" $PHP_PATH
	echo_success; echo
fi

if [ "$WEB_CONFIG" = "Yes" ]; then
	if [ "$SELINUX_CONFIG" = "Yes" ]; then
		echo -n "* Detecting selinux"
		selinuxenabled
		if [ $? -ne 0 ]; then
			$PERL_BIN -i -pe "s/SELINUX=disabled/SELINUX=enforcing/g" $SELINUX_CONF 1>> "$LOG_FILE" 2>&1
		fi
		echo_success; echo
		echo -n "* Updating selinux"
		setsebool -P httpd_enable_homedirs 1 1>> "$LOG_FILE" 2>&1
		semanage port -a -t http_port_t -p tcp 8082 1>> "$LOG_FILE" 2>&1
		if [ $? -ne 0 ]; then
			echo_failure; echo
			echo "Unable to configure selinux" >> "$LOG_FILE"
			exit_on_error
		fi
		setsebool -P httpd_can_network_connect_db 1 1>> "$LOG_FILE" 2>&1
		if [ $? -ne 0 ]; then
			echo_failure; echo
			echo "Unable to configure selinux connect db" >> "$LOG_FILE"
			exit_on_error
		fi
		echo_success; echo
	else
		setenforce 0 1>> "$LOG_FILE" 2>&1
		$PERL_BIN -i -pe "s/SELINUX=enforcing/SELINUX=disabled/g" $SELINUX_CONF 1>> "$LOG_FILE" 2>&1
	fi

	echo -n "* Updating $HTTPD_SERVICE_NAME configuration"
	cp -rf $HTTPD_PATH/httpd.conf $HTTPD_PATH/httpd.conf.backup 1>> "$LOG_FILE" 2>&1
	$PERL_BIN -i -pe "s/Listen 80.*/Listen $EXTERNAL_WEB_PORT\n/g" $HTTPD_PATH/httpd.conf 1>> "$LOG_FILE" 2>&1
	# $PERL_BIN -i -pe "s/ServerSignature.*/ServerSignature Off/g" $HTTPD_PATH/httpd.conf 1>> "$LOG_FILE" 2>&1

	cp -rf $HTTPD_VS_CONF_PATH/ssl.conf $HTTPD_VS_CONF_PATH/ssl.conf.backup 1>> "$LOG_FILE" 2>&1
	$PERL_BIN -i -pe "s/Listen 443.*/Listen $EXTERNAL_WEB_PORT_SSL\n/g" $HTTPD_VS_CONF_PATH/ssl.conf 1>> "$LOG_FILE" 2>&1
	echo_success; echo

	if [ "$OS_RELEASE" != "7" ]; then
		echo -n "* Adding wstunnel module"
		cp -rf "$PKG_PATH"/mod_proxy_wstunnel.so /etc/httpd/modules/
		echo_success; echo
	fi

	echo -n "* Adding virtual host"
	cp -rf "$APP_SRC_PATH"/Scripts/httpd.conf "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_IP>/$EXT_IP/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_IP_LOCAL>/$LOCALHOST_IP/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_WEB_PORT>/$INTERNAL_WEB_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_RP_PORT_SSL>/$EXTERNAL_WEB_PORT_SSL/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_RP_PORT>/$EXTERNAL_WEB_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_RPC_PORT>/$INTERNAL_RPC_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_REST_PORT>/$INTERNAL_REST_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_DATA_CLIENT_PORT>/$INTERNAL_DATA_CLIENT_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_DATA_AGENT_PORT>/$INTERNAL_DATA_AGENT_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_DATA_PROBE_PORT>/$INTERNAL_DATA_PROBE_PORT/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_FQDN>/$EXT_FQDN/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_USERNAME>/$PRODUCT_SVC_NAME/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	$PERL_BIN -i -pe "s/<KEY_INSTALL>/$(echo $INSTALL_PATH/current/ | sed -e 's/[]\/()$*.^|[]/\\&/g' )/g" "$INSTALL_PATH"/current/Var/Run/httpd.conf
	dos2unix "$INSTALL_PATH"/current/Var/Run/httpd.conf 1>> "$LOG_FILE" 2>&1

	rm -f $HTTPD_VS_CONF_PATH/$PRODUCT_SVC_NAME.conf 1>> $LOG_FILE 2>&1
	ln -s "$INSTALL_PATH"/current/Var/Run/httpd.conf $HTTPD_VS_CONF_PATH/$PRODUCT_SVC_NAME.conf
	echo_success; echo
fi

#######################################
#
# Restart all services
#
#######################################

if [ "$SILENT" == "custom" -o  "$SILENT" == "install" ]; then
    if [ "$WEB_CONFIG" = "Yes" -o "$PHP_CONFIG" = "Yes" ] ; then
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
    fi

    if [ "$FW_CONFIG" = "Yes" ]; then
        echo -n "* Restarting firewall"
        if [ "$OS_RELEASE" == "7" ]; then
            systemctl restart firewalld.service 1>> "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                echo_failure; echo
                echo "Unable to restart firewalld" >> "$LOG_FILE"
                exit_on_error
            fi
        else
            service $IPTABLE_SERVICE_NAME restart 1>> "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                echo_failure; echo
                echo "Unable to restart $IPTABLE_SERVICE_NAME" >> "$LOG_FILE"
                exit_on_error
            fi
        fi
        echo_success; echo
    else
        if [ "$OS_RELEASE" == "7" ]; then
            systemctl stop firewalld.service 1>> "$LOG_FILE" 2>&1
            systemctl disable firewalld.service 1>> "$LOG_FILE" 2>&1
            systemctl stop $IPTABLE_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
            systemctl disable $IPTABLE_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
        else
            service $IPTABLE_SERVICE_NAME stop 1>> "$LOG_FILE" 2>&1
            chkconfig $IPTABLE_SERVICE_NAME off 1>> "$LOG_FILE" 2>&1
        fi
    fi

    echo -n "* Restarting postfix"
    if [ "$OS_RELEASE" == "7" ]; then
        systemctl restart $POSTFIX_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo_failure; echo
            echo "Unable to restart $POSTFIX_SERVICE_NAME" >> "$LOG_FILE"
            exit_on_error
        fi
    else
        service $POSTFIX_SERVICE_NAME restart 1>> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo_failure; echo
            echo "Unable to restart $POSTFIX_SERVICE_NAME" >> "$LOG_FILE"
            exit_on_error
        fi
    fi
    echo_success; echo
    
    echo -n "* Restarting MySQL/MariaDB"
    if [ "$OS_RELEASE" == "7" ]; then
        systemctl restart $MARIADB_SERVICE_NAME.service 1>> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo_failure; echo
            echo "Unable to restart $MARIADB_SERVICE_NAME" >> "$LOG_FILE"
            exit_on_error
        fi
    else
        service $MYSQL_SERVICE_NAME restart 1>> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo_failure; echo
            echo "Unable to restart $MYSQL_SERVICE_NAME" >> "$LOG_FILE"
            exit_on_error
        fi
    fi
    echo_success; echo
fi

echo -n "* Adding the $APP_NAME database"
cd "$INSTALL_PATH"/current/Scripts/
$PWD_BIN 1>> "$LOG_FILE" 2>&1
$LS_BIN 1>> "$LOG_FILE" 2>&1
$LS_BIN ../Libs/ 1>> "$LOG_FILE" 2>&1
python ./database/add-bdd.py 1>> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
	echo_failure; echo
	echo "Unable to create the database" >> "$LOG_FILE"
	exit_on_error
fi
echo_success; echo

if [ "$SILENT" == "custom" -o  "$SILENT" == "install" ]; then
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
fi

rm -rf "$APP_PATH"/default.cfg.tmp 1>> "$LOG_FILE" 2>&1

if [ "$SILENT" == "custom" -o  "$SILENT" == "install" ]; then
        echo "========================================================================="
        echo "- Installation completed successfully!"
        echo "- Continue and go to the web interface (https://$EXT_IP/web/index.php)"
        echo "========================================================================="
fi

exit 0