#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import sys
sys.path.insert(0, '../' )

try:
    import MySQLdb
except ImportError: # python3 support
    import pymysql as MySQLdb

from  Libs import Settings

Settings.initialize(path="../../")

def querySQL ( query, db = '' ):
    """
    @param query: sql query
    @type query: string
    """
    try:
        conn = MySQLdb.connect (  host = Settings.get( 'MySql', 'ip') ,
                                 user = Settings.get( 'MySql', 'user'),
                                 passwd = Settings.get( 'MySql', 'pwd'),
                                 db = Settings.get( 'MySql', 'db'),
                                 unix_socket=Settings.get( 'MySql', 'sock') )
        #
        cursor = conn.cursor ()
        cursor.execute ( query )
        cursor.close ()
        #
        conn.commit ()
        conn.close ()
        ret = True
    except MySQLdb.Error, e:
        print("[querySQL] %s" % str(e))
        sys.exit(1)

# Drop the database tas
print("Drop the database %s" % Settings.get( 'MySql', 'db'))
querySQL( query = """
DROP DATABASE `%s`;
""" % Settings.get( 'MySql', 'db') )

Settings.finalize()

sys.exit(0)