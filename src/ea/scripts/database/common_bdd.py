#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

import os
import sqlite3

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
new_dir_path = os.sep.join(dir_path.split(os.sep)[:-2])

DIR_EXEC = os.path.normpath("%s/" % new_dir_path)

# prepare the path of the database
db_name = "%s/var/data.db" % (DIR_EXEC)


def delete_db():
    """
    """
    print("Removing current database...")
    try:
        os.remove(db_name)
    except Exception:
        pass


def querySQL(query):
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

    c.close()

    conn.commit()
    conn.close()

    return lastrowid
