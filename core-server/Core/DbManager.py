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

import MySQLdb
import time
import inspect

from Libs import Settings, Logger


def caller():
    """
    Function to find out which function is the caller of the current function. 

    @return: caller function name
    @rtype: string
    """
    callback = inspect.getouterframes(inspect.currentframe())
    ret = [ "%s" % str(callback[2][1:4]) ]
    ret.append( "%s" % str(callback[3][1:4]) )
    return  ">>".join(ret)
    
class DbManager(Logger.ClassLogger):    
    def __init__(self):
        """
        Class Db Manager
        Mysql is only supported 
        """
        self.dbVersion = None
        self.conn = None

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="DBM - %s" % (txt) )

    def querySQL ( self, query, insertData=False, columnName=False, debugCaller=False):
        """
        Make a SQL query, a new connection made each time.

        @param query: sql query
        @type query: string

        @return: response from table
        @rtype: tuple
        """
        ret = False
        rows = None
        try:
            conn = MySQLdb.connect ( host = Settings.get( 'MySql', 'ip') ,
                                     user = Settings.get( 'MySql', 'user'),
                                     passwd = Settings.get( 'MySql', 'pwd'),
                                     db = Settings.get( 'MySql', 'db'),
                                     unix_socket=Settings.get( 'MySql', 'sock') )
            
            cursor = conn.cursor()
            if debugCaller:
                self.trace( "SQL QUERY: %s - %s" % (caller(), query) )
            else:
                self.trace( "SQL QUERY: %s" % (query) )
                
            cursor.execute ( query )
            if insertData:
                rows = cursor.lastrowid
            else:
                if columnName:
                    fields = map(lambda x:x[0], cursor.description)
                    rows = [dict(zip(fields,row))   for row in cursor.fetchall()]
                else:
                    rows = cursor.fetchall()
            cursor.close ()
            
            conn.commit ()
            conn.close ()
            ret = True
        except MySQLdb.Error, e:
            self.error( "unable to execute sql query: %s" % e ) 
        return ret, rows
    
    def connectTo(self, host, user, passwd, db):
        """
        Should be nice but not yet implemented
        """
        pass

    def disconnectFrom(self):
        """
        Should be nice but not yet implemented
        """
        pass

    def isUp(self):
        """
        Try to connect to the database
        Detect the version of the mysql server
        """
        
        timeoutVal = Settings.getInt('Boot','timeout-sql-server')
        
        timeout = False
        go = False
        startTime = time.time()
        while (not go) and (not timeout):
            # timeout elapsed ?
            if (time.time() - startTime) >= timeoutVal:
                timeout = True
            else:   
                try:
                    self.trace( "try to connect to the database" ) 
                    conn = MySQLdb.connect ( host = Settings.get( 'MySql', 'ip') ,
                                             user = Settings.get( 'MySql', 'user'),
                                             passwd = Settings.get( 'MySql', 'pwd'),
                                             db = Settings.get( 'MySql', 'db'),
                                             unix_socket=Settings.get( 'MySql', 'sock') )
                    go = True
                    self.trace( "connection successful" ) 
                except MySQLdb.Error as e:
                    Logger.debug( "connect to the database failed: %s" % str(e) )
                    Logger.debug( "retry in %s second" % Settings.get( 'MySql', 'retry-connect') )
                    time.sleep( int(Settings.get( 'MySql', 'retry-connect')) )

                
        
        if timeout:
            raise Exception("db manager not ready: timeout" )
    
        if go:
            self.trace( "retrieve mysql version" ) 
            cursor = conn.cursor()
            cursor.execute ( "SELECT VERSION()" )
            row = cursor.fetchone ()
            cursor.close ()
            conn.close ()
            self.dbVersion = row[0]
            self.trace( self.dbVersion  )
    
    def getVersion(self):
        """
        Return the mysql version
        """
        return "MySQL/%s" % self.dbVersion

DBM = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return DBM

def initialize ():
    """
    Instance creation
    """
    global DBM
    DBM = DbManager()
    #DBM.connectTo()
    #DBM.detectVersion()


def finalize ():
    """
    Destruction of the singleton
    """
    global DBM
    if DBM:
        #DBM.disconnectFrom()
        DBM = None