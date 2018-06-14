#!/bin/sh

set -e 

#----------
# Stop XTC
#---------
xtctl stop;sleep 2


#---------------
# Start process
#---------------

# Start mariadb
/bin/bash -c "/usr/bin/mysqld_safe --skip-grant-tables &";sleep 5

# Start httpd
rm -f /run/httpd/httpd.pid;/bin/bash -c "/usr/sbin/apachectl -D BACKGROUND"; sleep 5

# Start XTC
xtctl start;sleep 2

#----------------------------
# Keep process in background
#----------------------------
exec "$@" && tail -f /dev/null

