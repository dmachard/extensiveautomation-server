#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

import getopt
import sys
import base64

from binascii import hexlify
import os

import MySQLdb

sys.path.insert(0, '../' )
from  Libs import Settings
Settings.initialize(path="../")

prefix_table = Settings.get( 'MySql', 'table-prefix')

def querySQL ( query, db = Settings.get( 'MySql', 'db') ):
    """
    Query database 
    """
    try:

        conn = MySQLdb.connect ( 
                                 host = Settings.get( 'MySql', 'ip') ,
                                 user = Settings.get( 'MySql', 'user'),
                                 passwd = Settings.get( 'MySql', 'pwd'),
                                 db = db,
                                 unix_socket=Settings.get( 'MySql', 'sock')
                               )

        cursor = conn.cursor ()
        cursor.execute ( query )
        cursor.close ()
        
        conn.commit ()
        conn.close ()

    except MySQLdb.Error, e:
        print( "[querySQL] %s" % str(e) )
        sys.exit(1)


def generate(login, size=20):
    """
    Generate secret api
    """
    apikey_id = login
    apikey_secret = hexlify(os.urandom(size))

    # insert in database
    prefix_table = Settings.get( 'MySql', 'table-prefix')
    querySQL( query = "UPDATE `%s-users` SET apikey_id=\"%s\", apikey_secret=\"%s\" WHERE login=\"%s\"" % (prefix_table,login, apikey_secret,login) )

    return (apikey_id, apikey_secret)


def help():
    """
    Display help
    """
    print("./generate-apikey --user=<username>")

    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt( sys.argv[1:], "h", [ "user=" ] )
    except getopt.error, msg:
        print(msg)
        help()
        sys.exit(2)
    if len(opts) == 0:
        help()
        sys.exit(0)

    userName = None
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit(0)
        elif o in ["--user"]:  
            userName = a

    if userName is not None :
        apikey_id,apikey_secret = generate(login=userName)
        print("API Key ID: %s" % apikey_id)
        print("API Key Secret: %s" % apikey_secret)

        apikey = base64.b64encode( "%s:%s" % (apikey_id, apikey_secret) )
        print("API Key: %s" % apikey)
        sys.exit(0)
    else:
        help()
        sys.exit(0)

