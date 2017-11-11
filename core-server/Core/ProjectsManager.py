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

try:
    import MySQLdb
except ImportError: # python3 support
    import pymysql as MySQLdb
import os
import base64
import zlib
import shutil
try:
    # python 2.4 support
    import simplejson as json
except ImportError:
    import json

try:
    import DbManager
    # import Context
except ImportError: # python3 support
    from . import DbManager
    # from . import Context

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
        
        # Initialize the repository
        self.info( 'Deploying default common project...' )
        self.createDefaultCommon()

        # new in v17
        self.addReservedFolders()
        # end of new
        
    def encodeData(self, data):
        """
        Encode data
        """
        ret = ''
        try:
            tasks_json = json.dumps(data)
        except Exception as e:
            self.error( "Unable to encode in json: %s" % str(e) )
        else:
            try: 
                tasks_zipped = zlib.compress(tasks_json)
            except Exception as e:
                self.error( "Unable to compress: %s" % str(e) )
            else:
                try: 
                    ret = base64.b64encode(tasks_zipped)
                except Exception as e:
                    self.error( "Unable to encode in base 64: %s" % str(e) )
        return ret

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
        self.trace("terminated")
            
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
        # get user id 
        prjs = []
        sql = 'SELECT r.project_id, p.name FROM `%s-users` u,`%s-relations-projects` r, `%s-projects` p ' % (
                                                                                    Settings.get( 'MySql', 'table-prefix'), 
                                                                                    Settings.get( 'MySql', 'table-prefix'), 
                                                                                    Settings.get( 'MySql', 'table-prefix')
                                                                                 )
        sql += 'WHERE u.login="%s" and u.id=r.user_id AND r.project_id=p.id ;' % ( user )
        ret, rows = DbManager.instance().querySQL( query=sql, columnName=True )
        if not ret:
            self.error( 'unable to get project from db for the user %s: %s' % (user, str(ret)) )
        else:
            self.trace( "List of projects for user %s: %s" % (user,rows) )
            prjs = rows
        if b64:
            return self.encodeData(data=prjs)
        else:
            return prjs
            
    def checkProjectsAuthorization(self, user, projectId):
        """
        Check if the project id provided is authorized for the user
        """
        ret = False
        sql = 'SELECT r.project_id, p.name FROM `%s-users` u,`%s-relations-projects` r, `%s-projects` p ' % (
                                                                                        Settings.get( 'MySql', 'table-prefix'),
                                                                                        Settings.get( 'MySql', 'table-prefix'),
                                                                                        Settings.get( 'MySql', 'table-prefix')
                                                                                     )
        sql += 'WHERE u.login="%s" and u.id=r.user_id AND r.project_id=p.id ;' % (  user )
        retDb, rows = DbManager.instance().querySQL( query=sql, columnName=True )
        if not retDb:
            self.error( 'unable to get project from db for the user %s: %s' % (user, str(retDb)) )
        else:
            projectAuthorized = False
            for prj in rows:
                if "%s" % prj["project_id"] == "%s" % projectId:
                    projectAuthorized = True
            self.trace( '[Login=%s] [ProjectID=%s] authorized projects list: %s' % (user, projectId, rows) )
            ret = projectAuthorized
        return ret
        
    def checkProjectsAuthorizationV2(self, user, projectId):
        """
        Check if the project id provided is authorized for the user
        """
        ret = False
        rows = []
        sql = 'SELECT r.project_id, p.name FROM `%s-users` u,`%s-relations-projects` r, `%s-projects` p  WHERE u.login="%s" and u.id=r.user_id AND r.project_id=p.id ;' % (
            Settings.get( 'MySql', 'table-prefix'), Settings.get( 'MySql', 'table-prefix'), Settings.get( 'MySql', 'table-prefix'),  user )
        retDb, rows = DbManager.instance().querySQL( query=sql, columnName=True )
        if not retDb:
            self.error( 'unable to get project from db for the user %s: %s' % (user, str(retDb)) )
        else:
            projectAuthorized = False
            for prj in rows:
                if "%s" % prj["project_id"] == "%s" % projectId:
                    projectAuthorized = True
            self.trace( '[Login=%s] [ProjectID=%s] authorized projects list: %s' % (user, projectId, rows) )
            ret = projectAuthorized

        return (ret,rows)
        
    def getDefaultProjectForUser(self, user):
        """
        Get default project of the user passed as argument
        """
        self.trace( 'get default project for the user %s from db' % user)
        pid = 1 # default project
        sql = "SELECT defaultproject FROM `%s` WHERE login='%s'" % (self.table_name_user, user )
        ret, rows = DbManager.instance().querySQL( query=sql, columnName=True)
        if not ret:
            self.error( 'unable to get the default project for the user %s from db: %s' % ( user, str(ret) ) )
        else:
            if rows:
                pid = rows[0]['defaultproject']
            else:
                self.error( 'no default project returned for user' )
        return pid

    def getProjectID(self, name):
        """
        Return project id according to the name passed as argument
        """
        self.trace( 'Get project id by name "%s" from db' % name)
        pid = 0 # default project
        sql = "SELECT id FROM `%s` WHERE name='%s'" % (self.table_name, name )
        ret, rows = DbManager.instance().querySQL( query=sql, columnName=True)
        if not ret:
            self.error( 'unable to get the project id for the name %s from db: %s' % ( name, str(ret) ) )
        else:
            if rows:
                pid = rows[0]['id']
            else:
                self.error( 'no project id returned for name=%s' % name )
        return pid
        
    def getProjectName(self, prjId):
        """
        Return project name according to the id passed as argument
        """
        self.trace( 'Get project name by id "%s" from db' % prjId)
        prjName = 'Common' # default project
        
        if int(prjId) == 0: return prjName
        
        sql = "SELECT name FROM `%s` WHERE id=%s" % (self.table_name, prjId )
        ret, rows = DbManager.instance().querySQL( query=sql, columnName=True)
        if not ret:
            self.error( 'unable to get the project name for id %s from db: %s' % ( prjId, str(ret) ) )
        else:
            if rows:
                prjName = rows[0]['name']
            else:
                self.error( 'no project name returned for id=%s' % prjId )
        return prjName

    def addProject(self, prjId):
        """
        Add project
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
        Delete project
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
        
        return (self.context.CODE_OK, "%s" % int(lastRowId) )
        
    def updateProjectFromDB(self, projectName, projectId):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
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
            
        return (self.context.CODE_OK, "" )
        
    def delProjectFromDB(self, projectId):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
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
            return (self.context.CODE_ERROR, "unable to remove project because this project is linked with %s users" % dbRows["nbrelation"] )
        
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
            
        return (self.context.CODE_OK, "" )
        
    def getProjectsFromDB(self):
        """
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all projects
        sql = """SELECT * FROM `%s-projects`""" % ( prefix)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read project's table" )
            return (self.context.CODE_ERROR, "unable to read project's table")

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