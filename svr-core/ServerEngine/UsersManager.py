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

        # load projects in cache, new in v19
        self.__cache = {}
        self.loadCache()

    def loadCache(self):
        """
        load all projects in cache
        """
        self.trace("Updating users memory cache from database")

        code, users_list = self.getUsersFromDB()
        if code == self.context.CODE_ERROR:
            raise Exception("Unable to get users from database")
            
        code, relations_list = self.getRelationsFromDB()
        if code == self.context.CODE_ERROR:
            raise Exception("Unable to get relations from database")

        # save users in the cache and order by login before
        users_dict = {}
        for row_user in users_list:
        
            # get all linked projects to the user
            projects = []
            for row_relation in relations_list:
                if row_relation['user_id'] == row_user['id']:
                    projects.append( row_relation['project_id'] )     
            row_user['projects'] = projects
            
            # store in the dict
            users_dict[row_user['login']] = row_user
            
        # delete the list of users and save the dict in the cache  
        del users_list
        self.__cache = users_dict
        self.trace("Users cache Size=%s" % len(self.__cache) )
        
    def cache(self):
        """
        Return accessor for the cache
        """
        return self.__cache

    def setOnlineStatus(self, login, online):
        """
        Set the online status of a specific user
        """
        self.trace( 'Set online status User=%s' % login )
        
        sql = "UPDATE `%s` SET online=%s WHERE login='%s'" % ( self.table_name, online, login)
        ret, rows = DbManager.instance().querySQL( query =sql  )
        if not ret:
            self.error("unable to update db online user field for user %s to %s" % (login, online) )

        # new in v19, refresh the users cache
        self.loadCache()
        
    def addStats(self, user, connId, startTime, duration):
        """
        Add statistics of a specific user
        """
        self.trace( 'Add stats for User=%s' % user )
        
        strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(startTime))
        sql = "INSERT INTO `%s` (user, connection, date, duration) VALUES ('%s',%s,'%s',%s)" \
                            % (self.table_name_stats, user, int(connId), strDate, int(duration)  )
        ret, rows = DbManager.instance().querySQL(  query =sql  )
        if not ret:
            self.error("unable to add user stats in db")
    
    def addUserToDB(self, level, login, password, email, lang, 
                    style, notifications, defaultPrj, listPrjs):
        """
        Add a new user in database
        """
        self.trace( 'Add user in database Login=%s' % login )
        
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

        # access level
        if level == "admin":
            admin=1
        elif level == "monitor":
            monitor=1
        else:
            tester=1
        
        #  password, create a sha1 hash with salt: sha1( salt + sha1(password) )
        sha1_pwd = hashlib.sha1()
        sha1_pwd.update( password.encode("utf8") ) 
        
        sha1 = hashlib.sha1()
        sha1.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), sha1_pwd.hexdigest() )  )

        # create random apikey
        apikey_secret = hexlify(os.urandom(20))
        
        # prepare the sql query
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
        for prj in listPrjs:
            sql_values.append( """('%s', '%s')""" % (lastRowId, prj) )
        
        sql += ', '.join(sql_values)
        dbRet, _ = DbManager.instance().querySQL( query = sql, insertData=True  )
        if not dbRet: 
            self.error("unable to insert relations")
            return (self.context.CODE_ERROR, "unable to insert relations")
                
        # new in v19, refresh the cache
        self.loadCache()
        
        return (self.context.CODE_OK, "%s" % int(lastRowId) )
        
    def delUserInDB(self, userId):
        """
        Delete a user from database
        """
        self.trace( 'Delete user from database Id=%s' % userId )
        
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
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
            
        # new in v19, refresh the cache
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def updateUserInDB(self, userId, email=None, login=None, lang=None, 
                       style=None, notifications=None, default=None, 
                       projects=[], level=None):
        """
        """
        self.trace( 'Update user in database Id=%s' % userId )
        
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # search  user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to search user by id" )
            return (self.context.CODE_ERROR, "unable to read user id")

        sql_values = []
        if login is not None:
            # check if this new login if available ?
            sql = """SELECT * FROM `%s-users` WHERE  login='%s' AND id != '%s'""" % ( prefix, escape(login), escape(userId) )
            dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
            if not dbRet: 
                self.error( "unable to search user login" )
                return (self.context.CODE_ERROR, "unable to read user id")
            if len(dbRows): 
                return (self.context.CODE_ALLREADY_EXISTS, "This login already exist")
            else:
                sql_values.append( """login='%s'""" % escape(login))
        if email is not None:
            sql_values.append( """email='%s'""" % escape(email))
        if lang is not None:
            sql_values.append( """lang='%s'""" % escape(lang))
        if style is not None:
            sql_values.append( """style='%s'""" % escape(style))
        if notifications is not None:
            sql_values.append( """notifications='%s'""" % escape(notifications))
        if default is not None:
            default = str(default)
            sql_values.append( """defaultproject='%s'""" % escape(default))
            
        # access level
        # the level can not modified for default users (system, admin, monitor and tester)
        if level is not None and int(userId) > 4:
            if level == "admin":  
                sql_values.append( """administrator='1'""")
                sql_values.append( """leader='0'""")
                sql_values.append( """tester='0'""")
                sql_values.append( """developer='0'""")
            elif level == "monitor":
                sql_values.append( """administrator='0'""")
                sql_values.append( """leader='1'""")
                sql_values.append( """tester='0'""")
                sql_values.append( """developer='0'""")
            else:
                sql_values.append( """administrator='0'""")
                sql_values.append( """leader='0'""")
                sql_values.append( """tester='1'""")
                sql_values.append( """developer='1'""")

        # update
        if len(sql_values):
            sql = """UPDATE `%s-users` SET %s WHERE id='%s'""" % (prefix, ','.join(sql_values) , userId)
            dbRet, _ = DbManager.instance().querySQL( query = sql )
            if not dbRet: 
                self.error("unable to update user")
                return (self.context.CODE_ERROR, "unable to update user")
            
        if len(projects):
            # delete relation to update it
            sql = """DELETE FROM `%s-relations-projects` WHERE user_id='%s'""" % (prefix, escape(userId))
            dbRet, _ = DbManager.instance().querySQL( query = sql  )
            if not dbRet: 
                self.error("unable to delete relations")
                return (self.context.CODE_ERROR, "unable to delete relations")
            
            # adding relations-projects`
            sql = """INSERT INTO `%s-relations-projects`(`user_id`, `project_id`) VALUES""" % prefix
            sql_values = []
            for prj in projects:
                sql_values.append( """('%s', '%s')""" % (userId, prj) )
            
            sql += ', '.join(sql_values)
            dbRet, _ = DbManager.instance().querySQL( query = sql, insertData=True  )
            if not dbRet: 
                self.error("unable to insert relations")
                return (self.context.CODE_ERROR, "unable to insert relations")
        
        # new in v19, refresh the cache
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def duplicateUserInDB(self, userId):
        """
        Duplicate a user in database
        """
        self.trace( 'Duplicate user from database Id=%s' % userId )
        
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
        level = "tester"
        if user['administrator']:
            level = "admin"
        if user['leader']:
            level = "monitor"
        if user['tester']:
            level = "level"
        return self.addUserToDB(login=newLogin, 
                                password='', 
                                email=user['email'],
                                level=level, 
                                lang=user['lang'], 
                                style=user['style'], 
                                notifications=user['notifications'], 
                                defaultPrj=user['default'], 
                                listPrjs=[user['default']])
        
    def updateStatusUserInDB(self, userId, status):
        """
        Enable or disable a user in database
        """
        self.trace( 'Enable/disable user in database Id=%s' % userId )
        
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
        
        # new in v19, refresh the cache
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def resetPwdUserInDB(self, userId):
        """
        Reset a password in database
        """
        self.trace( 'Reset user`\'s password in database Id=%s' % userId )
        
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
            
        # new in v19, refresh the cache
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def updatePwdUserInDB(self, userId, newPwd, curPwd):
        """
        Update password's user in database
        """
        self.trace( 'Update user\'s password in database Id=%s' % userId )
        
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        userId = str(userId)
        
        # find user by id
        sql = """SELECT * FROM `%s-users` WHERE  id='%s'""" % ( prefix, escape(userId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to find user id" )
            return (self.context.CODE_ERROR, "unable to find user id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this user id does not exist")

        self.trace( "/!\ %s" % dbRows )
        
        # current password
        sha1_cur = hashlib.sha1()
        sha1_cur.update( curPwd.encode("utf8") ) 
        
        sha1_cur2 = hashlib.sha1()
        sha1_cur2.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), sha1_cur.hexdigest()  )  )
        
        if sha1_cur2.hexdigest() != dbRows[0]['password']:
            return (self.context.CODE_FORBIDDEN, "Bad current password provided")
            
        # update password
        sha1_new = hashlib.sha1()
        sha1_new.update( newPwd.encode("utf8") ) 
        
        sha1_new2 = hashlib.sha1()
        sha1_new2.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), sha1_new.hexdigest()  )  )

        sql = """UPDATE `%s-users` SET password='%s' WHERE id='%s'""" % (prefix, sha1_new2.hexdigest(), userId)
        dbRet, _ = DbManager.instance().querySQL( query = sql )
        if not dbRet: 
            self.error("unable to update pwd")
            return (self.context.CODE_ERROR, "unable to update pwd")
            
        # new in v19, refresh the cache
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def getUsersFromDB(self):
        """
        Get all users from database
        """
        self.trace( 'Get all users from database')
        
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

    def getRelationsFromDB(self):
        """
        Get all relations from database
        """
        self.trace( 'Get all relations from database')
        
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all users
        sql = """SELECT * FROM `%s-relations-projects`""" % ( prefix)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read relation's table" )
            return (self.context.CODE_ERROR, "unable to read relation's table")

        return (self.context.CODE_OK, dbRows )
        
    def getUserFromDB(self, userId=None, userLogin=None):
        """
        Get user from database according to the id or login name
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
            self.error( "unable to find user" )
            return (self.context.CODE_ERROR, "unable to find user")

        return (self.context.CODE_OK, dbRows[0] )
    
    def getStatisticsFromDb(self):
        """
        Get statistics users from database
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