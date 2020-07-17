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

import os
import shutil
from ea.serverengine import DbManager
from ea.serverengine import UsersManager
from ea.libs import Settings, Logger

DEFAULT_PRJ_ID = "1"


class ProjectsManager(Logger.ClassLogger):
    """
    """

    def __init__(self, context):
        """
        Class Projects Manager
        """
        self.tb_projects = 'projects'

        self.repoTests = '%s/%s' % (Settings.getDirExec(),
                                    Settings.get('Paths', 'tests'))
        self.context = context

        # load projects in cache, new in v19
        self.__cache = []
        self.loadCache()

        # Initialize the repository
        self.info('Deploying folders projects and reserved folders...')

        self.createDirProjects()
        # self.addReservedFolders()

    def loadCache(self):
        """
        load all projects in cache
        """
        self.trace("Updating memory cache with projects from database")

        code, projects_list = self.getProjectsFromDB()
        if code == self.context.CODE_ERROR:
            raise Exception("Unable to get projects from database")

        self.__cache = projects_list
        self.trace("Projects cache Size=%s" % len(self.__cache))

    def cache(self):
        """
        Return accessor for the cache
        """
        return self.__cache

    # def addReservedFolders(self):
        # """
        # Add reserved folders (recycle and sandbox)
        # """
        # self.trace("adding reserved folders")

        # code, prjsList = self.getProjectsFromDB()
        # if code != self.context.CODE_OK:
            # return

        # for prj in prjsList:
            # try:
                # os.mkdir("%s/%s/@Recycle" % (self.repoTests, prj["id"]))
                # os.mkdir("%s/%s/@Sandbox" % (self.repoTests, prj["id"]))
            # except Exception:
                # pass

    def createDirProjects(self):
        """
        """
        self.trace("creating projects folders if missing")

        code, projects_list = self.getProjectsFromDB()
        if code != self.context.CODE_OK:
            return

        for prj in projects_list:
            if not os.path.exists("%s/%s" % (self.repoTests, prj["id"])):
                os.mkdir("%s/%s" % (self.repoTests, prj["id"]))

    def getProjects(self, user):
        """
        Return projects
        """
        # search the user in the cache
        if user not in UsersManager.instance().cache():
            self.error('Get project for Login=%s not found in cache' % (user))
            return False

        # exception added for administrator
        # an administrator can see all projects
        if UsersManager.instance().cache()[user]['administrator']:
            projects_list = []
            for p in self.cache():
                projects_dict = {}
                projects_dict['project_id'] = int(p['id'])
                projects_dict['name'] = p['name']
                projects_list.append(projects_dict)
        else:
            user_projects = UsersManager.instance().cache()[user]['projects']
            
            projects_list = []
            for p in user_projects:
                projects_dict = {}
                projects_dict['project_id'] = int(p)
                projects_dict['name'] = self.getProjectName(prjId=int(p))
                projects_list.append(projects_dict)

        return projects_list

    def checkProjectsAuthorization(self, user, projectId):
        """
        Check if the project id provided is authorized for the user
        """
        # search the user in the cache
        if user not in UsersManager.instance().cache():
            self.error(
                'Check project access for Login=%s not found in cache' %
                (user))
            return False

        # check if the provided project id is authorized for the user
        granted = False
        user_profile = UsersManager.instance().cache()[user]
        
        # new exception for administrator 
        # project is granted to all projects
        if user_profile['administrator']:
            granted=True
        else:
            for p in user_profile['projects']:
                if int(p) == int(projectId):
                    granted = True
                    break

        # return the final result
        self.trace('Check project access for Login=%s and ProjectID=%s Result=%s' % (user,
                                                                                     projectId,
                                                                                     str(granted)
                                                                                     )
                   )
        return granted

    def getDefaultProjectForUser(self, user):
        """
        Get default project of the user passed as argument
        """
        pid = 1
        found = False

        for u, profile in UsersManager.instance().cache().items():
            if u == user:
                pid = profile['defaultproject']
                found = True
                break

        if not found:
            self.error('no default project returned for User=%s' % user)
        self.trace('Get default project for User=%s Result=%s' % (user, pid))
        return pid

    def getProjectID(self, name):
        """
        Return project id according to the name passed as argument
        """
        pid = 0  # default project
        found = False

        for p in self.cache():
            if p["name"] == name:
                pid = p["id"]
                found = True
                break

        if not found:
            self.error('no project id returned with name=%s' % name)
        self.trace('Get project ID with Name=%s Result=%s ' % (name, pid))
        return pid

    def getProjectName(self, prjId):
        """
        Return project name according to the id passed as argument
        """
        prjName = 'Common'  # default project
        found = False

        for p in self.cache():
            if int(p["id"]) == int(prjId):
                prjName = p["name"]
                found = True
                break

        if not found:
            self.error('no project name returned with id=%s' % prjId)
        self.trace('Get project name with Id=%s Result=%s' % (prjId, prjName))
        return prjName

    def addProject(self, prjId):
        """
        Add project folder
        """
        self.trace('creating the project %s' % prjId)
        ret = False
        try:
            res = os.path.exists("%s/%s" % (self.repoTests, prjId))
            if res:
                self.trace('project %s already exist' % prjId)
                ret = False
            else:
                try:
                    os.mkdir("%s/%s" % (self.repoTests, prjId))

                    # create some reserved folders
                    os.mkdir("%s/%s/@Recycle" % (self.repoTests, prjId))
                    os.mkdir("%s/%s/@Sandbox" % (self.repoTests, prjId))

                except Exception as e:
                    self.error(
                        "unable to create the project %s: %s" %
                        (prjId, str(e)))
                    ret = False
                else:
                    ret = True
        except Exception as e:
            self.error("add project error: %s" % str(e))
        return ret

    def delProject(self, prjId):
        """
        Delete project folder
        """
        self.trace('deleting the project %s' % prjId)
        ret = False
        try:
            res = os.path.exists("%s/%s" % (self.repoTests, prjId))
            if not res:
                self.trace('project %s does not exist' % prjId)
                ret = False
            else:
                shutil.rmtree("%s/%s" % (self.repoTests, prjId))
                ret = True
        except OSError as e:
            self.trace(e)
            ret = False
        except Exception as e:
            self.error("del project error: %s" % str(e))
            ret = False
        return ret

    def addProjectToDB(self, projectName):
        """
        """
        if not len(projectName):
            self.error("project name is empty")
            return (self.context.CODE_ERROR, "project name is empty")

        # check if the name of the project already exists
        sql = """SELECT * FROM `%s` WHERE  name=?""" % (self.tb_projects)
        success, dbRows = DbManager.instance().querySQL(query=sql, arg1=projectName)
        if not success:
            self.error("unable to read project's table")
            return (self.context.CODE_ERROR, "unable to read project's table")
        if len(dbRows):
            return (self.context.CODE_ALREADY_EXISTS,
                    "this name (%s) already exists" % projectName)

        # insert in db
        sql = """INSERT INTO `%s`(`name`, `active`) VALUES(?, '1')""" % (
            self.tb_projects)
        success, lastRowId = DbManager.instance().querySQL(query=sql,
                                                           insertData=True,
                                                           arg1=projectName)
        if not success:
            self.error("unable to insert project")
            return (self.context.CODE_ERROR, "unable to insert project")

        # create the folder according to the id of the project
        added = self.addProject(prjId=int(lastRowId))
        if not added:
            self.error("unable to add project")
            # todo, cancel the previous insert
            return (self.context.CODE_ERROR, "unable to add project")

        # refresh the cache, new in v19
        self.loadCache()

        return (self.context.CODE_OK, "%s" % int(lastRowId))

    def updateProjectFromDB(self, projectName, projectId):
        """
        """
        # init some shortcut
        projectId = str(projectId)

        # not possible to delete default project common
        if int(projectId) == 1:
            self.error("update the default project not authorized")
            return (self.context.CODE_ERROR,
                    "update the default project is not authorized")

        if not len(projectName):
            self.error("project name is empty")
            return (self.context.CODE_ERROR, "the project name is empty")

        # find the project id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_projects)
        success, dbRows = DbManager.instance().querySQL(query=sql, arg1=projectId)
        if not success:
            self.error("unable to read project id")
            return (self.context.CODE_ERROR, "unable to read project id")
        if not len(dbRows):
            return (self.context.CODE_NOT_FOUND,
                    "this project id does not exist")

        # check if the name of the project already exists
        sql = """SELECT * FROM `%s` WHERE  name=?""" % (self.tb_projects)
        success, dbRows = DbManager.instance().querySQL(query=sql, arg1=projectName)
        if not success:
            self.error("unable to read project's table")
            return (self.context.CODE_ERROR, "unable to read project's table")
        if len(dbRows):
            return (self.context.CODE_ALREADY_EXISTS,
                    "this name already exists")

        # update in db
        sql = """UPDATE `%s` SET name=? WHERE id=?""" % (self.tb_projects)
        success, _ = DbManager.instance().querySQL(query=sql,
                                                   arg1=projectName,
                                                   arg2=projectId)
        if not success:
            self.error("unable to update project by id")
            return (self.context.CODE_ERROR, "unable to update project by id")

        # refresh the cache, new in v19
        self.loadCache()

        return (self.context.CODE_OK, "")

    def delProjectFromDB(self, projectId):
        """
        Delete a project from DB and disk
        """
        # init some shortcut
        projectId = str(projectId)

        # not possible to delete default project common
        if int(projectId) == 1:
            self.error("delete the default project not authorized")
            return (self.context.CODE_ERROR,
                    "delete the default project not authorized")

        # find the project id
        sql = """SELECT * FROM `%s` WHERE  id=?""" % (self.tb_projects)
        success, dbRows = DbManager.instance().querySQL(query=sql, arg1=projectId)
        if not success:
            self.error("unable to read project id")
            return (self.context.CODE_ERROR, "unable to read project id")
        if not len(dbRows):
            return (self.context.CODE_NOT_FOUND,
                    "this project id does not exist")

        # checking relations projects`
        sql = """SELECT COUNT(*) as nbrelation FROM `relations-projects` WHERE  project_id=?"""
        success, dbRows = DbManager.instance().querySQL(
            query=sql, columnName=True, arg1=projectId)
        if not success:
            self.error("unable to read project relations")
            return (self.context.CODE_ERROR,
                    "unable to read project relations")
        if dbRows[0]["nbrelation"]:
            msg = "unable to remove project because linked to user(s)=%s" % dbRows[
                0]["nbrelation"]
            return (self.context.CODE_ERROR, msg)

        # delete from db
        sql = """DELETE FROM `%s` WHERE  id=?""" % (self.tb_projects)
        success, _ = DbManager.instance().querySQL(query=sql, arg1=projectId)
        if not success:
            self.error("unable to remove project by id")
            return (self.context.CODE_ERROR, "unable to remove project by id")

        # delete the folder according to the id of the project
        deleted = self.delProject(prjId=int(projectId))
        if not deleted:
            self.error("unable to delete project")
            # todo, cancel the previous delete
            return (self.context.CODE_ERROR, "unable to delete project")

        # refresh the cache, new in v19
        self.loadCache()

        return (self.context.CODE_OK, "")

    def getProjectsFromDB(self):
        """
        Delete all projects
        """
        # get all projects
        sql = """SELECT * FROM `%s`""" % (self.tb_projects)
        success, dbRows = DbManager.instance().querySQL(query=sql, columnName=True)
        if not success:
            self.error("unable to read project's table")
            return (self.context.CODE_ERROR, [])

        return (self.context.CODE_OK, dbRows)

    def getProjectFromDB(self, projectName=None, projectId=None):
        """
        """
        sql_args = ()

        # get all projects
        sql = """SELECT * FROM `%s`""" % (self.tb_projects)
        sql += """ WHERE """
        if projectName is not None:
            sql += """name LIKE ?"""
            sql_args += ("%%%s%%" % projectName,)
        if projectId is not None:
            sql += """ id=?"""
            sql_args += (projectId,)
        success, dbRows = DbManager.instance().querySQL(query=sql,
                                                        columnName=True,
                                                        args=sql_args)
        if not success:
            self.error("unable to search project table")
            return (self.context.CODE_ERROR, "unable to search project table")

        return (self.context.CODE_OK, dbRows)


PM = None


def instance():
    """
    Returns the singleton
    """
    return PM


def initialize(context):
    """
    Instance creation
    """
    global PM
    PM = ProjectsManager(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global PM
    if PM:
        PM = None
