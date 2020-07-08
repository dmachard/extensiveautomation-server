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

import json

from ea.serverengine import (DbManager)
from ea.libs import Logger

def uniqid():
    """
    Return a unique id
    """
    from time import time
    return hex(int(time() * 10000000))[2:]
      
class VariablesManager(Logger.ClassLogger):
    """
    Variables manager class
    """

    def __init__(self, context):
        """
        Class User Manager
        """
        self.context = context
        self.tb_variables = 'test-environment'
        self.__cache_vars = []
        self.loadCacheVars()


    def loadCacheVars(self):
        """
        load all projects in cache
        """
        self.trace("Updating variables memory cache from database")

        code, vars_list = self.getVariablesFromDB()
        if code == self.context.CODE_ERROR:
            raise Exception("Unable to get variables from database")

        self.__cache_vars = vars_list
        self.trace("Variables cache Size=%s" % len(self.__cache_vars))

    def cacheVars(self):
        """
        Return accessor for the cache
        """
        return self.__cache_vars

    def getVariablesFromDB(self, projectId=None):
        """
        Get test variables from database
        """
        sql_args = ()

        # get all users
        sql = """SELECT id, name, project_id"""
        sql += """, value"""
        sql += """ FROM `%s`""" % (self.tb_variables)
        if projectId is not None:
            projectId = str(projectId)
            sql += """ WHERE project_id=?"""
            sql_args += (projectId,)
        sql += """ ORDER BY name"""
        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        args=sql_args)
        if not success:
            self.error("unable to read test environment table")
            return (self.context.CODE_ERROR,
                    "unable to test environment table")

        # new in v17 convert as json the result
        for d in dbRows:
            try:
                d['value'] = json.loads(d['value'])
            except Exception:
                d['value'] = "Bad JSON"
        # end of new

        return (self.context.CODE_OK, dbRows)

    def getVariableFromDB(self, projectId, variableName=None, variableId=None):
        """
        Get a specific variable from database
        """
        # init some shortcut
        projectId = str(projectId)
        sql_args = ()

        # get all users
        sql = """SELECT id, name, project_id"""
        sql += """, value"""
        sql += """ FROM `%s`""" % (self.tb_variables)
        sql += """ WHERE project_id=?"""
        sql_args += (projectId,)
        if variableName is not None:
            sql += """ AND name LIKE ?"""
            sql_args += ("%%%s%%" % variableName,)
        if variableId is not None:
            variableId = str(variableId)
            sql += """ AND id=?"""
            sql_args += (variableId,)
        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        args=sql_args)
        if not success:
            self.error("unable to search test environment table")
            return (self.context.CODE_ERROR,
                    "unable to search variable in test environment table")

        # new in v17 convert as json the result
        for d in dbRows:
            try:
                d['value'] = json.loads(d['value'])
            except Exception:
                d['value'] = "Bad JSON"
        # end of new
        return (self.context.CODE_OK, dbRows)

    def addVariableInDB(self, projectId, variableName, variableValue):
        """
        Add a variable in the database
        """
        # init some shortcut
        projectId = str(projectId)

        if ":" in variableName:
            return (self.context.CODE_ERROR, "bad variable name provided")

        # check if the name is not already used
        sql = """SELECT * FROM `%s` WHERE name=?""" % (self.tb_variables)
        sql += """ AND project_id=?"""
        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        arg1=variableName.upper(),
                                                        arg2=projectId)
        if not success:
            self.error("unable to get variable by name")
            return (self.context.CODE_ERROR, "unable to get variable by name")
        if len(dbRows):
            return (self.context.CODE_ALREADY_EXISTS,
                    "this variable (%s) already exists" % variableName)

        # good json ?
        try:
            json.loads(variableValue)
        except Exception:
            return (self.context.CODE_ERROR, "bad json value provided")

        # this name is free then create project
        sql = """INSERT INTO `%s`(`name`, `value`, `project_id`)""" % self.tb_variables
        sql += """VALUES(?, ?, ?)"""
        success, lastRowId = DbManager.instance().querySQL(query=sql,
                                                           insertData=True,
                                                           arg1=variableName.upper(),
                                                           arg2=variableValue,
                                                           arg3=projectId)
        if not success:
            self.error("unable to insert variable")
            return (self.context.CODE_ERROR, "unable to insert variable")

        # new in v19, refresh the cache
        self.loadCacheVars()

        # refresh the context of all connected users
        self.context.refreshTestEnvironment()

        return (self.context.CODE_OK, "%s" % int(lastRowId))

    def duplicateVariableInDB(self, variableId, projectId=None):
        """
        Duplicate a variable in database
        """
        # init some shortcut
        variableId = str(variableId)
        sql_args = ()

        # find variable by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_variables)
        sql_args += (variableId,)
        if projectId is not None:
            projectId = str(projectId)
            sql += """ AND project_id=?"""
            sql_args += (projectId,)

        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        args=sql_args)
        if not success:
            self.error("unable to read variable id")
            return (self.context.CODE_ERROR, "unable to read variable id")
        if not len(dbRows):
            return (self.context.CODE_NOT_FOUND,
                    "this variable id does not exist")
        variable = dbRows[0]

        # duplicate variable
        newVarName = "%s-COPY#%s" % (variable['name'], uniqid())

        return self.addVariableInDB(projectId=variable["project_id"],
                                    variableName=newVarName,
                                    variableValue=variable["value"])

    def updateVariableInDB(self, variableId, variableName=None,
                           variableValue=None, projectId=None):
        """
        Update the value of a variable in a database
        """
        # init some shortcut
        variableId = str(variableId)

        # find variable by id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_variables)
        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        arg1=variableId)
        if not success:
            self.error("unable to read variable id")
            return (self.context.CODE_ERROR, "unable to read variable id")
        if not len(dbRows):
            return (self.context.CODE_NOT_FOUND,
                    "this variable id does not exist")

        sql_values = []
        sql_args = ()
        if variableName is not None:
            sql_values.append("""name=?""")
            sql_args += (variableName.upper(),)
        if variableValue is not None:
            # good json ?
            try:
                json.loads(variableValue)
            except Exception:
                return (self.context.CODE_ERROR, "bad json value provided")

            sql_values.append("""value=?""")
            sql_args += (variableValue,)
        if projectId is not None:
            projectId = str(projectId)
            sql_values.append("""project_id=?""")
            sql_args += (projectId,)

        # update
        if len(sql_values):
            sql_args += (variableId,)
            sql = """UPDATE `%s` SET %s WHERE id=?""" % (
                self.tb_variables, ','.join(sql_values))
            success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
            if not success:
                self.error("unable to update variable")
                return (self.context.CODE_ERROR, "unable to update variable")

        # new in v19, refresh the cache
        self.loadCacheVars()

        # refresh the context of all connected users
        self.context.refreshTestEnvironment()

        return (self.context.CODE_OK, "")

    def delVariableInDB(self, variableId, projectId=None):
        """
        Delete a variable in database
        """
        # init some shortcut
        variableId = str(variableId)
        sql_args = ()

        # check if the name is not already used
        sql = """SELECT * FROM `%s` WHERE id=?""" % (self.tb_variables)
        sql_args += (variableId,)
        if projectId is not None:
            projectId = str(projectId)
            sql += """ AND project_id=?"""
            sql_args += (projectId,)

        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        args=sql_args)
        if not success:
            self.error("unable to get variable by id")
            return (self.context.CODE_ERROR, "unable to get variable by id")
        if not len(dbRows):
            return (self.context.CODE_NOT_FOUND,
                    "variable id provided does not exist")

        # delete from db
        sql_args = ()
        sql = """DELETE FROM `%s` WHERE  id=?""" % (self.tb_variables)
        sql_args += (variableId,)
        if projectId is not None:
            projectId = str(projectId)
            sql += """ AND project_id=?"""
            sql_args += (projectId,)

        success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
        if not success:
            self.error("unable to remove variable by id")
            return (self.context.CODE_ERROR, "unable to remove variable by id")

        # new in v19, refresh the cache
        self.loadCacheVars()

        # refresh the context of all connected users
        self.context.refreshTestEnvironment()

        return (self.context.CODE_OK, "")

    def delVariablesInDB(self, projectId):
        """
        Delete all variables in database
        """
        # init some shortcut
        projectId = str(projectId)
        sql_args = ()

        # delete from db
        sql = """DELETE FROM `%s` WHERE  project_id=?""" % (self.tb_variables)
        sql_args += (projectId,)
        success, _ = DbManager.instance().querySQL(query=sql, args=sql_args)
        if not success:
            self.error("unable to reset variables")
            return (self.context.CODE_ERROR, "unable to reset variables")

        # new in v19, refresh the cache
        self.loadCacheVars()

        # refresh the context of all connected users
        self.context.refreshTestEnvironment()

        return (self.context.CODE_OK, "")

VarsMng = None


def instance():
    """
    Returns the singleton
    """
    return VarsMng


def initialize(context):
    """
    Instance creation
    """
    global VarsMng
    VarsMng = VariablesManager(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global VarsMng
    if VarsMng:
        VarsMng = None
