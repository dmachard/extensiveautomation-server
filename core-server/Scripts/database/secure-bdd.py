#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import sys
sys.path.insert(0, '../' )

import MySQLdb
from  Libs import Settings

Settings.initialize(path="../../")

prefix_table = Settings.get( 'MySql', 'table-prefix')
aes_pwd = Settings.get( 'MySql', 'test-environment-password')

user = sys.argv[1]
pwd = sys.argv[2]

user_dump = sys.argv[3]
pwd_dump = sys.argv[4]

def querySQL ( query, db = Settings.get( 'MySql', 'db') ):
    """
    @param query: sql query
    @type query: string
    """
    try:
        conn = MySQLdb.connect ( host = Settings.get( 'MySql', 'ip') ,
                                 user = Settings.get( 'MySql', 'user'),
                                 passwd = Settings.get( 'MySql', 'pwd'),
                                 db = db,
                                 unix_socket=Settings.get( 'MySql', 'sock') )

        cursor = conn.cursor ()
        cursor.execute ( query )
        rows = cursor.fetchall()

        cursor.close ()

        conn.commit ()
        conn.close ()
        ret = rows
    except MySQLdb.Error, e:
        print("[querySQL] %s" % str(e))
        sys.exit(1)
    return ret
    
print("Encrypt test environment value in '%s-test-environment'" % prefix_table)
rows = querySQL( query = """SELECT * FROM `%s-test-environment`;"""% prefix_table)

for line in rows:
    id_, name_, value_, prj_ = line
    sql = "UPDATE `%s-test-environment` SET value=AES_ENCRYPT('%s', '%s') WHERE id=%s;" % (
                prefix_table,
                value_,
                aes_pwd,
                id_
            )
    querySQL( query = sql )

print("Create new user for database")
querySQL( query = "CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (user, Settings.get( 'MySql', 'ip'), pwd) )
querySQL( query = "GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE, SHOW VIEW ON %s.* TO '%s'@'%s';" % (
                                                        Settings.get( 'MySql', 'db'), 
                                                        user, 
                                                        Settings.get( 'MySql', 'ip')
                                                        ) )
querySQL( query = "CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (user_dump, Settings.get( 'MySql', 'ip'), pwd_dump) )
querySQL( query = "GRANT SELECT, LOCK TABLES ON *.* TO '%s'@'%s';" % (user_dump, Settings.get( 'MySql', 'ip')) )
querySQL( query = "FLUSH privileges ;" )

Settings.finalize()

sys.exit(0)