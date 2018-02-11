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

from binascii import hexlify
import os

try:
    import MySQLdb
except ImportError: # python3 support
    import pymysql as MySQLdb
import time
import hashlib

try:
    import DbManager
    import Common
except ImportError: # python3 support
    from . import DbManager
    from . import  Common
    
from Libs import Settings, Logger

def uniqid():
    """
    Return a unique id
    """
    from time import time
    return hex(int(time()*10000000))[2:]
    
class UsersManager(Logger.ClassLogger): 
    """
    Users manager class
    """
    def __init__(self, context):
        """
        Class User Manager
        """
        self.context=context
        self.table_name = '%s-users' % Settings.get( 'MySql', 'table-prefix')
        self.table_name_stats = '%s-users-stats' % Settings.get( 'MySql', 'table-prefix')

    def getNbUserOfType(self, userType):
        """
        Returns the number of admins present in database

        @param userType: user type (RIGHTS_ADMIN/RIGHTS_USER/RIGHTS_TESTER/RIGHTS_MANAGER)
        @type userType: string

        @return: nb user of the user type passed as argument
        @rtype: int
        """
        nb = 0
        ok, nb_entries = DbManager.instance().querySQL( query="""SELECT count(*) FROM `%s` WHERE %s='1'""" % (self.table_name,userType) )
        if ok:
            nb = int( nb_entries[0][0] )
        return nb

    def getNbAdmin(self):
        """
        Returns the number of admins present in database

        @return: nb admins
        @rtype: int
        """
        self.trace( 'get nb admin from db' )
        return self.getNbUserOfType(userType=Settings.get( 'Server', 'level-admin'))

    def getNbTester(self):
        """
        Returns the number of testers present in database

        @return: nb testers
        @rtype: int
        """
        self.trace( 'get nb tester from db' )
        return self.getNbUserOfType(userType=Settings.get( 'Server', 'level-tester'))

    # def getNbDeveloper(self):
        # """
        # Returns the number of developers present in database

        # @return: nb developers
        # @rtype: int
        # """
        # self.trace( 'get nb developer from db' )
        # return self.getNbUserOfType(userType=Settings.get( 'Server', 'level-developer'))

    # def getNbMonitor(self):
        # """
        # Returns the number of leaders present in database

        # @return: nb managers
        # @rtype: int
        # """
        # self.trace( 'get nb managers from db' )
        # return self.getNbUserOfType(userType=Settings.get( 'Server', 'level-leader'))

    def getNbOfUsers(self):
        """
        Returns the total number of users present in database
        """
        self.trace( 'get nb users from db' )
        nb = 0
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.table_name )
        if not ok:
            self.error( 'unable to count the number of user from db: %s' % str(ok) )
        else:
            nb = int( nb_entries[0][0] )
        return nb

    def getUser(self, login):
        """
        Return user according the login passed as argument
        """
        self.trace( 'get user from db' )
        ret, rows = DbManager.instance().querySQL( query = """SELECT * FROM `%s` WHERE login='%s'""" % (self.table_name,login), columnName=True )
        if not ret:
            self.error( 'unable to select user from db: %s' % str(ret) )
            return None
        elif len(rows) > 1:
            self.error( 'several users founded: %s' % str(ret) )
            return None
        else:
            return rows[0]

    def getUsers(self):
        """
        Returns users with colomn name
        """
        self.trace( 'get users from db' )
        sql = """SELECT * FROM `%s`""" % self.table_name
        ret, rows = DbManager.instance().querySQL( query = sql, columnName=True)
        if not ret:
            self.error( 'unable to select users from db: %s' % str(ret) )
            return None
        return rows

    def getUsersByLogin (self):
        """
        Returns a dict of all users present in the database
        reindex by the login

        @return: all users from the database
        @rtype: dict
        """
        self.trace( 'get users as dict' )
        users = {}

        usersdb = self.getUsers()
        if usersdb is not None:
            # reindex user by login
            for row in usersdb:
                users[row['login']] = row
        return users

    def setOnlineStatus(self, login, online):
        """
        Set the online status of a specific user
        """
        self.trace( 'set online status %s' % login )
        ret, rows = DbManager.instance().querySQL( query = "UPDATE `%s` SET online=%s WHERE login='%s'" % ( self.table_name, online, login) )
        if not ret:
            self.error("unable to update db online user field for user %s to %s" % (login, online) )

    def addStats(self, user, connId, startTime, duration):
        """
        Add statistics of a specific user
        """
        self.trace( 'add user stats %s' % user )
        strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(startTime))
        ret, rows = DbManager.instance().querySQL(  query = "INSERT INTO `%s` (user, connection, date, duration) VALUES ('%s',%s,'%s',%s)" 
                            % (self.table_name_stats, user, int(connId), strDate, int(duration)  ) )
        if not ret:
            self.error("unable to add user stats in db")
    
    def addUserToDB(self, login, password, email):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # find user by name
        sql = """SELECT * FROM `%s-users` WHERE login='%s'""" % ( prefix, escape(login) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user by name" )
            return (self.context.CODE_ERROR, "unable to read user by name")
        if len(dbRows): return (self.context.CODE_ALREADY_EXISTS, "this user name already exists")
        
        # create user in db
        lang = "en"
        style = "default"
        notifications = "false;false;false;false;false;false;false;"
        defaultPrj = 1
        projects = [1]
        #  password, create a sha1 hash with salt: sha1( salt + sha1(password) )
        sha1 = hashlib.sha1()
        sha1.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), password )  )

        apikey_secret = hexlify(os.urandom(20))
        sql = """INSERT INTO `%s-users`(`login`, `password`, `administrator`, """  % prefix
        sql += """`leader`, `tester`, `developer`, `system`, `email`, `lang`, """
        sql += """`style`, `active`, `default`, `online`, `notifications`, """
        sql += """`defaultproject`, `cli`, `gui`, `web`, `apikey_id`, `apikey_secret`)"""
        sql += """ VALUES('%s', '%s', '0', """ % (escape(login), escape(sha1.hexdigest()))
        sql += """'0', '1', '0', '0', '%s', '%s',""" % ( escape(email), escape(lang) )
        sql += """'%s', '1', '0', '0', '%s', """ % (escape(style), escape(notifications))
        sql += """'%s', '1', '1', '1', '%s', '%s')""" % (defaultPrj, escape(login), apikey_secret )
        dbRet, lastRowId = DbManager.instance().querySQL( query = sql, insertData=True  )
        if not dbRet: 
            self.error("unable to insert user")
            return (self.context.CODE_ERROR, "unable to insert user")
        
        # adding relations-projects`
        sql = """INSERT INTO `%s-relations-projects`(`user_id`, `project_id`) VALUES""" % prefix
        sql_values = []
        for prj in projects:
            sql_values.append( """('%s', '%s')""" % (lastRowId, prj) )
        
        sql += ', '.join(sql_values)
        dbRet, _ = DbManager.instance().querySQL( query = sql, insertData=True  )
        if not dbRet: 
            self.error("unable to insert relations")
            return (self.context.CODE_ERROR, "unable to insert relations")
                
        return (self.context.CODE_OK, "%s" % int(lastRowId) )
        
    def delUserInDB(self, userId):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # not possible to delete default usrs
        if int(userId) <= 4:
            self.error("delete default users not authorized")
            return (self.context.CODE_ERROR, "delete default users not authorized")
            
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user id" )
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")
        
        # disconnect user before deletion
        # todo
        
        # delete from db
        sql = """DELETE FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to remove user by id" )
            return (self.context.CODE_ERROR, "unable to remove user by id")
            
        # delete relations from db
        sql = """DELETE FROM `%s-relations-projects` WHERE  user_id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to remove user relation" )
            return (self.context.CODE_ERROR, "unable to remove user relation")
            
        return (self.context.CODE_OK, "" )
        
    def updateUserInDB(self, userId, email=None):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user id" )
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")
        
        sql_values = []
        if email is not None:
            sql_values.append( """email='%s'""" % escape(email))
            
        # update
        if len(sql_values):
            sql = """UPDATE `%s-users` SET %s WHERE id='%s'""" % (prefix, ','.join(sql_values) , userId)
            dbRet, _ = DbManager.instance().querySQL( query = sql )
            if not dbRet: 
                self.error("unable to update user")
                return (self.context.CODE_ERROR, "unable to update user")
            
        return (self.context.CODE_OK, "" )
        
    def duplicateUserInDB(self, userId):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user id" )
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")
        user = dbRows[0]
        
        # duplicate user
        newLogin = "%s-COPY#%s" % (user['login'], uniqid())
        sha1 = hashlib.sha1()
        sha1.update( '' )
        emptypwd = sha1.hexdigest()
        
        return self.addUserToDB(login=newLogin, password=emptypwd, email=user['email'])
        
    def updateStatusUserInDB(self, userId, status):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user id" )
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")
        
        # update
        sql = """UPDATE `%s-users` SET active='%s' WHERE id='%s'""" % (prefix, int(status), userId)
        dbRet, _ = DbManager.instance().querySQL( query = sql )
        if not dbRet: 
            self.error("unable to change the status of the user")
            return (self.context.CODE_ERROR, "unable to change the status of the user")
            
        return (self.context.CODE_OK, "" )
        
    def resetPwdUserInDB(self, userId):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user id" )
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")
        
        # disconnect user before 
        # todo
        
        # update password
        emptypwd = hashlib.sha1()
        emptypwd.update( '' )
        sha1 = hashlib.sha1()
        sha1.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), emptypwd.hexdigest() )  )
        
        sql = """UPDATE `%s-users` SET password='%s' WHERE id='%s'""" % (prefix, sha1.hexdigest(), userId)
        dbRet, _ = DbManager.instance().querySQL( query = sql )
        if not dbRet: 
            self.error("unable to reset pwd")
            return (self.context.CODE_ERROR, "unable to reset pwd")
            
        return (self.context.CODE_OK, "" )
        
    def updatePwdUserInDB(self, userId, newPwd):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user id" )
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")

        # disconnect user before 
        # todo
        
        # update password
        sha1 = hashlib.sha1()
        sha1.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), newPwd )  )
        
        sql = """UPDATE `%s-users` SET password='%s' WHERE id='%s'""" % (prefix, sha1.hexdigest(), userId)
        dbRet, _ = DbManager.instance().querySQL( query = sql )
        if not dbRet: 
            self.error("unable to update pwd")
            return (self.context.CODE_ERROR, "unable to update pwd")
            
        return (self.context.CODE_OK, "" )
        
    def getUsersFromDB(self):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all users
        sql = """SELECT * FROM `%s-users`""" % ( prefix)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read user's table" )
            return (self.context.CODE_ERROR, "unable to read user's table")

        return (self.context.CODE_OK, dbRows )
        
    def getUserFromDB(self, userId=None, userLogin=None):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # get all users
        sql = """SELECT * FROM `%s-users`""" % ( prefix)
        sql += """ WHERE """
        if userId is not None: sql += """id='%s'""" % escape( "%s" % userId )
        if userLogin is not None: sql += """login LIKE '%%%s%%'""" % escape( "%s" % userLogin)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to search user table" )
            return (self.context.CODE_ERROR, "unable to search user table")

        return (self.context.CODE_OK, dbRows[0] )
    
    def getStatisticsFromDb(self):
        """
        """
        prefix = Settings.get( 'MySql', 'table-prefix')
        
        sql1 = """SELECT COUNT(*) from `%s-users`""" % (prefix)
        sql = """SELECT COUNT(*) AS total_connections, (%s) AS total_users FROM `%s-users-stats`""" % ( sql1, prefix)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to get statitics  for users" )
            return (self.context.CODE_ERROR, "unable to get statitics  for users")

        return (self.context.CODE_OK, dbRows[0] )
        
    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="USM - %s" % txt)


UM = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class users manager
    @rtype: UsersManager
    """
    return UM

def initialize (context):
    """
    Instance creation
    """
    global UM
    UM = UsersManager(context=context)

def finalize ():
    """
    Destruction of the singleton
    """
    global UM
    if UM:
        UM = None