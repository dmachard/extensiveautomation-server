#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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
from binascii import hexlify
import os
import hashlib

from ea.serverengine import DbManager
from ea.libs import Logger


def uniqid():
    """
    Return a unique id
    """
    from time import time
    return hex(int(time() * 10000000))[2:]


class UsersManager(Logger.ClassLogger):
    """
    Users manager class
    """

    def __init__(self, context):
        """
        Class User Manager
        """
        self.context = context
        self.tb_users = 'users'

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
                    projects.append(row_relation['project_id'])
            row_user['projects'] = projects

            # store in the dict
            users_dict[row_user['login']] = row_user

        # delete the list of users and save the dict in the cache
        del users_list
        self.__cache = users_dict
        self.trace("Users cache Size=%s" % len(self.__cache))

    def cache(self):
        """
        Return accessor for the cache
        """
        return self.__cache

    def setOnlineStatus(self, login, online):
        """
        Set the online status of a specific user
        """
        self.trace('Set online status User=%s' % login)

        sql_args = ()
        sql = "UPDATE `%s` SET online=? WHERE login=?" % (self.tb_users)
        sql_args += (int(online),)
        sql_args += (login,)
        success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
        if not success:
            self.error(
                "unable to update online status user=%s value=%s" %
                (login, online))

        # new in v19, refresh the users cache
        self.loadCache()

    def addUserToDB(self, level, login, password, email, lang,
                    style, notifications, defaultPrj, listPrjs):
        """
        Add a new user in database
        """
        self.trace('Add user in database Login=%s' % login)

        # find user by name
        sql = """SELECT * FROM `%s` WHERE login=?""" % (self.tb_users)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     arg1=login)
        if not success:
            self.error("unable to read user by name")
            return (self.context.CODE_ERROR, "unable to read user by name")
        if len(res):
            return (self.context.CODE_ALREADY_EXISTS,
                    "this user name (%s) already exists" % login)

        self.trace(level)
        admin = 0
        monitor = 0
        tester = 0
        # access level
        if level == "administrator":
            admin = 1
        elif level == "monitor":
            monitor = 1
        else:
            tester = 1
        self.trace("%s %s %s" % (admin, monitor, tester))

        #  password, create a sha1 hash with salt: sha1(salt + sha1(password))
        sha1_pwd = hashlib.sha1()
        sha1_pwd.update(password.encode("utf8"))

        sha1 = hashlib.sha1()
        pwd_salt = "%s%s" % (self.context.cfg_db["auth-salt"],
                             sha1_pwd.hexdigest())
        if sys.version_info < (3,):
            sha1.update(pwd_salt)
        else:
            sha1.update(pwd_salt.encode('utf-8'))

        # create random apikey
        apikey_secret = hexlify(os.urandom(20))
        if sys.version_info > (3,):
            apikey_secret = apikey_secret.decode("utf8")

        # prepare the sql query
        sql = """INSERT INTO `%s`(`login`, `password`, `administrator`, """ % self.tb_users
        sql += """`monitor`, `tester`, `email`, `lang`, """
        sql += """`style`, `active`, `online`, `notifications`, """
        sql += """`defaultproject`, `apikey_id`, `apikey_secret`)"""
        sql += """ VALUES(?, ?, ?, """
        sql += """?, ?, ?, ?,"""
        sql += """?, '1', '0', ?, """
        sql += """?, ?, ?)"""
        success, lastRowId = DbManager.instance().querySQL(query=sql,
                                                           insertData=True,
                                                           arg1=login,
                                                           arg2=sha1.hexdigest(),
                                                           arg3=admin,
                                                           arg4=monitor,
                                                           arg5=tester,
                                                           arg6=email,
                                                           arg7=lang,
                                                           arg8=style,
                                                           arg9=notifications,
                                                           arg10=defaultPrj,
                                                           arg11=login,
                                                           arg12=apikey_secret)
        if not success:
            self.error("unable to insert user")
            return (self.context.CODE_ERROR, "unable to insert user")

        # adding relations-projects`
        sql_args = ()
        sql = """INSERT INTO `relations-projects`(`user_id`, `project_id`) VALUES"""
        sql_values = []
        try:
            for prj in listPrjs:
                prj = int(prj)
                sql_values.append("""(?, ?)""")
                sql_args += (lastRowId, prj,)
        except Exception:
            return (self.context.CODE_ERROR, "bad project list provided")

        sql += ', '.join(sql_values)
        success, _ = DbManager.instance().querySQL(query=sql,
                                                   insertData=True,
                                                   args=sql_args)
        if not success:
            self.error("unable to insert relations")
            return (self.context.CODE_ERROR, "unable to insert relations")

        # new in v19, refresh the cache
        self.loadCache()

        return (self.context.CODE_OK, "%s" % int(lastRowId))

    def delUserInDB(self, userId):
        """
        Delete a user from database
        """
        self.trace('Delete user from database Id=%s' % userId)

        # init some shortcut
        userId = str(userId)

        # find user by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_users)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     arg1=userId)
        if not success:
            self.error("unable to read user id")
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(res):
            return (self.context.CODE_NOT_FOUND, "this user id does not exist")

        # delete from db
        sql = """DELETE FROM `%s` WHERE  id=?""" % (self.tb_users)
        success, res = DbManager.instance().querySQL(query=sql, arg1=userId)
        if not success:
            self.error("unable to remove user by id")
            return (self.context.CODE_ERROR, "unable to remove user by id")

        # delete relations from db
        sql = """DELETE FROM `relations-projects` WHERE  user_id=?"""
        success, res = DbManager.instance().querySQL(query=sql, arg1=userId)
        if not success:
            self.error("unable to remove user relation")
            return (self.context.CODE_ERROR, "unable to remove user relation")

        # new in v19, refresh the cache
        self.loadCache()

        return (self.context.CODE_OK, "")

    def updateUserInDB(self, userId, email=None, login=None, lang=None,
                       style=None, notifications=None, default=None,
                       projects=[], level=None):
        """
        """
        self.trace('Update user in database Id=%s' % userId)

        # init some shortcut
        userId = str(userId)

        # search  user by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_users)
        success, _ = DbManager.instance().querySQL(query=sql,
                                                   columnName=True,
                                                   arg1=userId)
        if not success:
            self.error("unable to search user by id")
            return (self.context.CODE_ERROR, "unable to read user id")

        sql_values = []
        sql_args = ()
        if login is not None:
            # check if this new login if available ?
            sql = """SELECT * FROM `%s` WHERE  login=? AND id != ?""" % (
                self.tb_users)
            success, res = DbManager.instance().querySQL(query=sql,
                                                         columnName=True,
                                                         arg1=login,
                                                         arg2=userId)
            if not success:
                self.error("unable to search user login")
                return (self.context.CODE_ERROR, "unable to read user id")
            if len(res):
                return (self.context.CODE_ALREADY_EXISTS,
                        "This login already exist")
            else:
                sql_values.append("""login=?""")
                sql_args += (login,)
        if email is not None:
            sql_values.append("""email=?""")
            sql_args += (email,)
        if lang is not None:
            sql_values.append("""lang=?""")
            sql_args += (lang,)
        if style is not None:
            sql_values.append("""style=?""")
            sql_args += (style,)
        if notifications is not None:
            sql_values.append("""notifications=?""")
            sql_args += (notifications,)
        if default is not None:
            default = str(default)
            sql_values.append("""defaultproject=?""")
            sql_args += (default,)

        # access level
        if level is not None:
            if level == "administrator":
                sql_values.append("""administrator='1'""")
                sql_values.append("""monitor='0'""")
                sql_values.append("""tester='0'""")
            elif level == "monitor":
                sql_values.append("""administrator='0'""")
                sql_values.append("""monitor='1'""")
                sql_values.append("""tester='0'""")
            else:
                sql_values.append("""administrator='0'""")
                sql_values.append("""monitor='0'""")
                sql_values.append("""tester='1'""")

        # update
        if len(sql_values):
            sql_args += (userId,)
            sql = """UPDATE `%s` SET %s WHERE id=?""" % (
                self.tb_users, ','.join(sql_values))
            success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
            if not success:
                self.error("unable to update user")
                return (self.context.CODE_ERROR, "unable to update user")

        if len(projects):
            # delete relation to update it
            sql = """DELETE FROM `relations-projects` WHERE user_id=?"""
            success, _ = DbManager.instance().querySQL(query=sql, arg1=userId)
            if not success:
                self.error("unable to delete relations")
                return (self.context.CODE_ERROR, "unable to delete relations")

            # adding relations-projects`
            sql = """INSERT INTO `relations-projects`(`user_id`, `project_id`) VALUES"""
            sql_values = []
            sql_args = ()
            for prj in projects:
                prj = int(prj)
                sql_values.append("""(?, ?)""")
                sql_args += (userId, prj,)

            sql += ', '.join(sql_values)
            success, _ = DbManager.instance().querySQL(query=sql,
                                                       insertData=True,
                                                       args=sql_args)
            if not success:
                self.error("unable to insert relations")
                return (self.context.CODE_ERROR, "unable to insert relations")

        # new in v19, refresh the cache
        self.loadCache()

        return (self.context.CODE_OK, "")

    def duplicateUserInDB(self, userId):
        """
        Duplicate a user in database
        """
        self.trace('Duplicate user from database Id=%s' % userId)

        # init some shortcut
        userId = str(userId)

        # find user by id
        sql_args = ()
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_users)
        sql_args += (userId,)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     args=sql_args)
        if not success:
            self.error("unable to read user id")
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(res):
            return (self.context.CODE_NOT_FOUND, "this user id does not exist")
        user = res[0]

        # duplicate user
        newLogin = "%s-COPY#%s" % (user['login'], uniqid())
        level = "tester"
        if user['administrator']:
            level = "administrator"
        if user['monitor']:
            level = "monitor"
        if user['tester']:
            level = "tester"
        return self.addUserToDB(login=newLogin,
                                password='',
                                email=user['email'],
                                level=level,
                                lang=user['lang'],
                                style=user['style'],
                                notifications=user['notifications'],
                                defaultPrj=user['defaultproject'],
                                listPrjs=[user['defaultproject']])

    def updateStatusUserInDB(self, userId, status):
        """
        Enable or disable a user in database
        """
        self.trace('Enable/disable user in database Id=%s' % userId)
        sql_args = ()

        # init some shortcut
        userId = str(userId)

        # find user by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_users)
        sql_args += (userId,)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     args=sql_args)
        if not success:
            self.error("unable to read user id")
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(res):
            return (self.context.CODE_NOT_FOUND, "this user id does not exist")

        # update
        sql_args = ()
        sql = """UPDATE `%s` SET active=? WHERE id=?""" % (self.tb_users)
        sql_args += (int(status),)
        sql_args += (userId,)
        success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
        if not success:
            self.error("unable to change the status of the user")
            return (self.context.CODE_ERROR,
                    "unable to change the status of the user")

        # new in v19, refresh the cache
        self.loadCache()

        return (self.context.CODE_OK, "")

    def resetPwdUserInDB(self, userId):
        """
        Reset a password in database
        """
        self.trace('Reset user`\'s password in database Id=%s' % userId)
        sql_args = ()

        # init some shortcut
        userId = str(userId)

        # find user by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_users)
        sql_args += (userId,)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     args=sql_args)
        if not success:
            self.error("unable to read user id")
            return (self.context.CODE_ERROR, "unable to read user id")
        if not len(res):
            return (self.context.CODE_NOT_FOUND, "this user id does not exist")

        # disconnect user before
        # todo

        # update password
        emptypwd = hashlib.sha1()
        emptypwd.update(''.encode("utf8"))
        sha1 = hashlib.sha1()
        pwd_salt = "%s%s" % (self.context.cfg_db["auth-salt"],
                             emptypwd.hexdigest())
        if sys.version_info < (3,):
            sha1.update(pwd_salt)
        else:
            sha1.update(pwd_salt.encode('utf-8'))

        sql_args = ()
        sql = """UPDATE `%s` SET password=? WHERE id=?""" % (self.tb_users)
        sql_args += (sha1.hexdigest(),)
        sql_args += (userId,)
        success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
        if not success:
            self.error("unable to reset pwd")
            return (self.context.CODE_ERROR, "unable to reset pwd")

        # new in v19, refresh the cache
        self.loadCache()

        return (self.context.CODE_OK, "")

    def updatePwdUserInDB(self, userId, newPwd, curPwd):
        """
        Update password's user in database
        """
        self.trace('Update user\'s password in database Id=%s' % userId)

        sql_args = ()

        # init some shortcut
        userId = str(userId)

        # find user by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_users)
        sql_args += (userId,)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     args=sql_args)
        if not success:
            self.error("unable to find user id")
            return (self.context.CODE_ERROR, "unable to find user id")
        if not len(res):
            return (self.context.CODE_NOT_FOUND, "this user id does not exist")

        # current password
        sha1_cur = hashlib.sha1()
        sha1_cur.update(curPwd.encode("utf8"))

        sha1_cur2 = hashlib.sha1()
        pwd1_salt2 = "%s%s" % (self.context.cfg_db["auth-salt"],
                               sha1_cur.hexdigest())
        if sys.version_info < (3,):
            sha1_cur2.update(pwd1_salt2)
        else:
            sha1_cur2.update(pwd1_salt2.encode('utf-8'))

        if sha1_cur2.hexdigest() != res[0]['password']:
            return (self.context.CODE_FORBIDDEN,
                    "Bad current password provided")

        # update password
        sha1_new = hashlib.sha1()
        sha1_new.update(newPwd.encode("utf8"))

        sha1_new2 = hashlib.sha1()
        pwd_salt2 = "%s%s" % (self.context.cfg_db["auth-salt"],
                              sha1_new.hexdigest())
        if sys.version_info < (3,):
            sha1_new2.update(pwd_salt2)
        else:
            sha1_new2.update(pwd_salt2.encode('utf-8'))

        sql_args = ()
        sql = """UPDATE `%s` SET password=? WHERE id=?""" % (self.tb_users)
        sql_args += (sha1_new2.hexdigest(),)
        sql_args += (userId,)
        success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
        if not success:
            self.error("unable to update pwd")
            return (self.context.CODE_ERROR, "unable to update pwd")

        # new in v19, refresh the cache
        self.loadCache()

        return (self.context.CODE_OK, "")

    def getUsersFromDB(self):
        """
        Get all users from database
        Returns all users, except the first one (system)
        """
        self.trace('Get all users from database')

        # get all users
        sql = """SELECT * FROM `%s`""" % (self.tb_users)
        success, res = DbManager.instance().querySQL(query=sql, columnName=True)
        if not success:
            self.error("unable to read user's table")
            return (self.context.CODE_ERROR, "unable to read user's table")

        return (self.context.CODE_OK, res)

    def getRelationsFromDB(self):
        """
        Get all relations from database
        """
        self.trace('Get all relations from database')

        # get all users
        sql = """SELECT * FROM `relations-projects`"""
        success, res = DbManager.instance().querySQL(query=sql, columnName=True)
        if not success:
            self.error("unable to read relation's table")
            return (self.context.CODE_ERROR, "unable to read relation's table")

        return (self.context.CODE_OK, res)

    def getUserFromDB(self, userId=None, userLogin=None):
        """
        Get user from database according to the id or login name
        """
        sql_args = ()

        # init some shortcut
        userId = str(userId)

        # get all users
        sql = """SELECT * FROM `%s`""" % (self.tb_users)
        sql += """ WHERE """
        if userId is not None:
            sql += """id=?"""
            sql_args += (userId,)
        if userLogin is not None:
            sql += """login LIKE ?"""
            sql_args += ("%%%s%%" % userLogin,)
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True,
                                                     args=sql_args)
        if not success:
            self.error("unable to find user")
            return (self.context.CODE_ERROR, "unable to find user")

        return (self.context.CODE_OK, res[0])

    def getUserProfile(self, userId):
        """
        """
        new_profile = {}

        success, user_profile = self.getUserFromDB(userId=userId)
        if success != self.context.CODE_OK:
            return (self.context.CODE_ERROR, {})

        # add level to profile
        if user_profile["administrator"]:
            new_profile["level"] = "Administrator"
        if user_profile["monitor"]:
            new_profile["level"] = "Monitor"
        if user_profile["tester"]:
            new_profile["level"] = "Tester"

        # add some general infos
        new_profile["api_login"] = user_profile["login"]
        new_profile["email"] = user_profile["email"]
        new_profile["api_secret"] = user_profile["apikey_secret"]

        # projects
        sql = """SELECT * FROM `relations-projects` WHERE user_id=?"""
        sql_args = (userId,)
        success, relations_list = DbManager.instance().querySQL(query=sql,
                                                                columnName=True,
                                                                args=sql_args)
        if not success:
            self.error("unable to read relation's table")
            return (self.context.CODE_ERROR, {})

        sql = """SELECT * FROM `projects` WHERE id=?"""
        sql_args = (relations_list[0]["project_id"],)
        for row_relation in relations_list[1:]:
            sql += """ OR id=?"""
            sql_args += (row_relation['project_id'],)

        success, projects_list = DbManager.instance().querySQL(query=sql,
                                                               columnName=True,
                                                               args=sql_args)

        if not success:
            self.error("unable to read projects according to the user")

            return (self.context.CODE_ERROR, {})

        new_profile["projects"] = projects_list

        # default project
        sql = """SELECT * FROM `projects` WHERE id=?"""
        sql_args = (user_profile["defaultproject"],)
        success, def_project = DbManager.instance().querySQL(query=sql,
                                                             columnName=True,
                                                             args=sql_args)

        if not success:
            self.error("unable to read default project according to the user")
        new_profile["default_project"] = def_project[0]

        return (self.context.CODE_OK, new_profile)


UM = None


def instance():
    """
    Returns the singleton
    """
    return UM


def initialize(context):
    """
    Instance creation
    """
    global UM
    UM = UsersManager(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global UM
    if UM:
        UM = None
