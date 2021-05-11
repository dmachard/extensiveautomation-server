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

import sqlite3
import inspect

from ea.libs import Settings, Logger


def caller():
    """
    Function to find out which function is the caller of the current function.

    @return: caller function name
    @rtype: string
    """
    callback = inspect.getouterframes(inspect.currentframe())
    ret = ["%s" % str(callback[2][1:4])]
    ret.append("%s" % str(callback[3][1:4]))
    return ">>".join(ret)


class DbManager(Logger.ClassLogger):
    def querySQL(self, query, insertData=False, columnName=False,
                 debugCaller=False, args=(),
                 arg1=None, arg2=None, arg3=None,
                 arg4=None, arg5=None, arg6=None,
                 arg7=None, arg8=None, arg9=None,
                 arg10=None, arg11=None, arg12=None):
        """
        """
        ret = False
        rows = None

        db_name = "%s/%s/%s" % (Settings.getDirExec(),
                                Settings.get('Paths', 'var'),
                                Settings.get('Database', 'db'))

        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            if Settings.get('Trace', 'debug-level') == 'VERBOSE':
                if debugCaller:
                    self.trace("SQL QUERY: %s - %s" % (caller(), query))
                else:
                    self.trace("SQL QUERY: %s" % (query))

            sql_args = args
            if arg1 is not None:
                sql_args += (arg1,)
            if arg2 is not None:
                sql_args += (arg2,)
            if arg3 is not None:
                sql_args += (arg3,)
            if arg4 is not None:
                sql_args += (arg4,)
            if arg5 is not None:
                sql_args += (arg5,)
            if arg6 is not None:
                sql_args += (arg6,)
            if arg7 is not None:
                sql_args += (arg7,)
            if arg8 is not None:
                sql_args += (arg8,)
            if arg9 is not None:
                sql_args += (arg9,)
            if arg10 is not None:
                sql_args += (arg10,)
            if arg11 is not None:
                sql_args += (arg11,)
            if arg12 is not None:
                sql_args += (arg12,)
            cursor.execute(query, sql_args)

            if insertData:
                rows = cursor.lastrowid
            else:
                if columnName:
                    rows = []
                    for row in cursor.fetchall():
                        fields = map(lambda x: x[0], cursor.description)
                        rows.append(dict(zip(fields, row)))
                else:
                    rows = cursor.fetchall()
            cursor.close()

            conn.commit()
            conn.close()

            ret = True
        except Exception as e:
            self.error("unable to execute sqlite3 query: %s" % e)

        return ret, rows

    def isUp(self):
        """
        Try to connect to the database
        Detect the version of the mysql server
        """
        db_name = "%s/%s/%s" % (Settings.getDirExec(),
                                Settings.get('Paths', 'var'),
                                Settings.get('Database', 'db'))
        sqlite3.connect(db_name)
        self.trace("database connection successful")


DBM = None


def instance():
    """
    Returns the singleton
    """
    return DBM


def initialize():
    """
    Instance creation
    """
    global DBM
    DBM = DbManager()


def finalize():
    """
    Destruction of the singleton
    """
    global DBM
    if DBM:
        DBM = None
