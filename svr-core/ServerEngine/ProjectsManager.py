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

try:
    import MySQLdb
except ImportError: # python3 support
    import pymysql as MySQLdb
import os
import base64
import zlib
import shutil
import json

try:
    import DbManager
    import Common
    import UsersManager
except ImportError: # python3 support
    from . import DbManager
    from . import Common
    from . import UsersManager

from Libs import Settings, Logger

DEFAULT_PRJ_ID = "1"

class ProjectsManager(Logger.ClassLogger):  
    """
    """
    def __init__(self, context):
        """
        Class Projects Manager
        """
        self.table_name = '%s-projects' % Settings.get( 'MySql', 'table-prefix')
        self.table_name_user = '%s-users' % Settings.get( 'MySql', 'table-prefix')
        self.repoTests ='%s/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tests' ) )
        self.context = context
        
        # load projects in cache, new in v19
        self.__cache = []
        self.loadCache()
        
        # Initialize the repository
        self.info( 'Deploying default common project and reserved folders...' )
        self.createDefaultCommon()
        self.addReservedFolders()

    def loadCache(self):
        """
        load all projects in cache
        """
        self.trace("Updating memory cache with projects from database")
        
        code, projects_list = self.getProjectsFromDB()
        if code == self.context.CODE_ERROR:
            raise Exception("Unable to get projects from database")
            
        self.__cache = projects_list
        self.trace("Projects cache Size=%s" % len(self.__cache) )
        
    def cache(self):
        """
        Return accessor for the cache
        """
        return self.__cache
        
    def addReservedFolders(self):
        """
        Add reserved folders (recycle and sandbox)
        """
        self.trace("adding reserved folders")
        code, prjsList = self.getProjectsFromDB()
        if code != self.context.CODE_OK:
            return
        
        for prj in prjsList:
            try:
                os.mkdir( "%s/%s/@Recycle" % (self.repoTests, prj["id"]) )
                os.mkdir( "%s/%s/@Sandbox" % (self.repoTests, prj["id"]) )
            except Exception as e:
                pass
            
    def createDefaultCommon(self):
        """
        Create default common project
        """
        self.trace( 'creating the default common project' )
        res = os.path.exists( "%s/%s" % (self.repoTests,DEFAULT_PRJ_ID) )
        if res:
            self.trace( 'default project already exist' )
        else:
            try:
                os.mkdir( "%s/%s" % (self.repoTests, DEFAULT_PRJ_ID) )
            except Exception as e:
                self.error( "unable to create the default project: %s" % str(e) )
    
    def getProjects(self, user, b64=True):
        """
        Return projects
        """
        # search the user in the cache
        if user not in UsersManager.instance().cache():
            self.error( 'Get project for Login=%s not found in cache' % (user) )
            return False
            
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
            self.error( 'Check project access for Login=%s not found in cache' % (user) )
            return False
        
        # check if the provided project id is authorized for the user
        granted = False
        user_profile = UsersManager.instance().cache()[user]
        for p in user_profile['projects']:
            if int(p) == int(projectId):
                granted = True
                break
        
        # return the final result
        self.trace( 'Check project access for Login=%s and ProjectID=%s Result=%s' % (user, projectId, str(granted)) )
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
                
        if not found: self.error( 'no default project returned for User=%s' % user)
        self.trace( 'Get default project for User=%s Result=%s' % (user, pid) )
        return pid

    def getProjectID(self, name):
        """
        Return project id according to the name passed as argument
        """
        pid = 0 # default project
        found = False
        
        for p in self.cache():
            if p["name"] == name:
                pid = p["id"]
                found = True
                break
                
        if not found: self.error( 'no project id returned with name=%s' % name )
        self.trace( 'Get project ID with Name=%s Result=%s ' % (name, pid) )
        return pid
        
    def getProjectName(self, prjId):
        """
        Return project name according to the id passed as argument
        """
        prjName = 'Common' # default project
        found = False
        
        for p in self.cache():
            if int(p["id"]) == int(prjId):
                prjName = p["name"]
                found = True
                break
                
        if not found: self.error( 'no project name returned with id=%s' % prjId )
        self.trace( 'Get project name with Id=%s Result=%s' % (prjId, prjName) )
        return prjName

    def addProject(self, prjId):
        """
        Add project folder
        """
        self.trace( 'creating the project %s' % prjId )
        ret = False
        try:
            res = os.path.exists( "%s/%s" % (self.repoTests,prjId) )
            if res:
                self.trace( 'project %s already exist' % prjId )
                ret = False
            else:
                try:
                    os.mkdir( "%s/%s" % (self.repoTests, prjId) )
                    
                    # create some reserved folders
                    os.mkdir( "%s/%s/@Recycle" % (self.repoTests, prjId) )
                    os.mkdir( "%s/%s/@Sandbox" % (self.repoTests, prjId) )
                    
                except Exception as e:
                    self.error( "unable to create the project %s: %s" % (prjId,str(e)) )
                    ret = False
                else:
                    ret = True
        except Exception as e:
            self.error("add project error: %s" % str(e) )
        return ret

    def delProject(self, prjId):
        """
        Delete project folder
        """
        self.trace( 'deleting the project %s' % prjId )
        ret = False
        try:
            res = os.path.exists( "%s/%s" % (self.repoTests,prjId) )
            if not res:
                self.trace( 'project %s does not exist' % prjId )
                ret = False
            else:
                shutil.rmtree( "%s/%s" % (self.repoTests,prjId) )
                ret = True
        except OSError as e:
            self.trace( e )
            ret = False
        except Exception as e:
            self.error( "del project error: %s" % str(e) )
            ret = False
        return ret

    def addProjectToDB(self, projectName):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # check if the name of the project already exists
        sql = """SELECT * FROM `%s-projects` WHERE  name='%s'""" % ( prefix, escape(projectName) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to read project's table" )
            return (self.context.CODE_ERROR, "unable to read project's table")
        if len(dbRows): return (self.context.CODE_ALLREADY_EXISTS, "this name already exists")
            
        # insert in db
        sql = """INSERT INTO `%s-projects`(`name`, `active` ) VALUES('%s', '1')""" % (prefix, escape(projectName))
        dbRet, lastRowId = DbManager.instance().querySQL( query = sql, insertData=True  )
        if not dbRet: 
            self.error("unable to insert project")
            return (self.context.CODE_ERROR, "unable to insert project")

        # create the folder according to the id of the project
        added = self.addProject(prjId=int(lastRowId) )
        if not added: 
            self.error("unable to add project")
            # todo, cancel the previous insert
            return (self.context.CODE_ERROR, "unable to add project")
        
        # refresh the cache, new in v19
        self.loadCache()
        
        return (self.context.CODE_OK, "%s" % int(lastRowId) )
        
    def updateProjectFromDB(self, projectName, projectId):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        projectId = str(projectId)
        
        # not possible to delete default project common
        if int(projectId) == 1:
            self.error("delete the default project not authorized")
            return (self.context.CODE_ERROR, "delete the default project not authorized")
        
        # find the project id
        sql = """SELECT * FROM `%s-projects` WHERE  id='%s'""" % ( prefix, escape(projectId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to read project id" )
            return (self.context.CODE_ERROR, "unable to read project id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this project id does not exist")
        
        # check if the name of the project already exists
        sql = """SELECT * FROM `%s-projects` WHERE  name='%s'""" % ( prefix, escape(projectName) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to read project's table" )
            return (self.context.CODE_ERROR, "unable to read project's table")
        if len(dbRows): return (self.context.CODE_ALLREADY_EXISTS, "this name already exists")
        
        # update in db
        sql = """UPDATE `%s-projects` SET name='%s' WHERE id='%s'""" % ( prefix, escape(projectName), escape(projectId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to update project by id" )
            return (self.context.CODE_ERROR, "unable to update project by id")
        
        # refresh the cache, new in v19
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def delProjectFromDB(self, projectId):
        """
        Delete a project from DB and disk
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        projectId = str(projectId)
        
        # not possible to delete default project common
        if int(projectId) == 1:
            self.error("delete the default project not authorized")
            return (self.context.CODE_ERROR, "delete the default project not authorized")
        
        # find the project id
        sql = """SELECT * FROM `%s-projects` WHERE  id='%s'""" % ( prefix, escape(projectId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to read project id" )
            return (self.context.CODE_ERROR, "unable to read project id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this project id does not exist")
            
        # checking relations projects`
        sql = """SELECT COUNT(*) as nbrelation FROM `%s-relations-projects` WHERE  project_id='%s'""" % ( prefix, escape(projectId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read project relations" )
            return (self.context.CODE_ERROR, "unable to read project relations")
        if dbRows[0]["nbrelation"]:
            msg = "unable to remove project because this project is linked with %s user(s)" % dbRows[0]["nbrelation"]
            return (self.context.CODE_ERROR, msg )
        
        # delete from db
        sql = """DELETE FROM `%s-projects` WHERE  id='%s'""" % ( prefix, escape(projectId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to remove project by id" )
            return (self.context.CODE_ERROR, "unable to remove project by id")

        # delete the folder according to the id of the project
        deleted = self.delProject(prjId=int(projectId) )
        if not deleted: 
            self.error("unable to delete project")
            # todo, cancel the previous delete
            return (self.context.CODE_ERROR, "unable to delete project")

        # refresh the cache, new in v19
        self.loadCache()
        
        return (self.context.CODE_OK, "" )
        
    def getProjectsFromDB(self):
        """
        Delete all projects
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all projects
        sql = """SELECT * FROM `%s-projects`""" % ( prefix)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read project's table" )
            return (self.context.CODE_ERROR, [])

        return (self.context.CODE_OK, dbRows )
        
    def getProjectFromDB(self, projectName=None, projectId=None):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all projects
        sql = """SELECT * FROM `%s-projects`""" % ( prefix)
        sql += """ WHERE """
        if projectName is not None:
            sql += """name LIKE '%%%s%%'""" % escape(projectName)
        if projectId is not None:
            sql += """ id='%s'""" % escape( "%s" % projectId)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to search project table" )
            return (self.context.CODE_ERROR, "unable to search project table")

        return (self.context.CODE_OK, dbRows )
    
    def getStatisticsFromDb(self):
        """
        """
        prefix = Settings.get( 'MySql', 'table-prefix')

        sql = """SELECT COUNT(*) AS total_projects FROM `%s-projects`""" % (prefix)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to get statitics  for projects" )
            return (self.context.CODE_ERROR, "unable to get statitics  for projects")

        return (self.context.CODE_OK, dbRows[0] )
        
    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="PJM - %s" % txt)

PM = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class ProjectsManager
    @rtype: Context
    """
    return PM

def initialize (context):
    """
    Instance creation
    """
    global PM
    PM = ProjectsManager(context=context)

def finalize ():
    """
    Destruction of the singleton
    """
    global PM
    if PM:
        PM = None