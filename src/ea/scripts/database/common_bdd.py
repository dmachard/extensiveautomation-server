#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
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

import os
import sqlite3
import sys
sys.path.insert(0, '../../../' )

from ea.libs import Settings

# initialize settings module to read the settings.ini file
Settings.initialize(path="./")

# prepare the path of the database
db_name = "%s/%s/%s" % ( Settings.getDirExec(),
                         Settings.get( 'Paths', 'var' ),
                         Settings.get( 'Database', 'db' ))

def delete_db():
    """
    """
    print("Removing current database...")
    try:
        os.remove(db_name)
    except Exception:
        pass
  
def querySQL ( query ):
    """
    detect dabatase type
    only 2 type supported (mysql and sqlite)
    
    @param query: sql query
    @type query: string
    """
    # connect to the db
    conn = sqlite3.connect(db_name)
    
    c = conn.cursor()
    
    # execute the sql query
    print(query)
    print()
    c.execute(query)
    
    # retrieve the last id
    lastrowid = c.lastrowid

    c.close ()
    
    conn.commit()
    conn.close()
    
    return lastrowid