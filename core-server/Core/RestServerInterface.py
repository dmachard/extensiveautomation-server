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
from functools import wraps
from pycnic.core import WSGI, Handler
from pycnic.errors import HTTP_401, HTTP_400, HTTP_500, HTTP_403, HTTP_404

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler

import multiprocessing

import threading
import logging
import sys
import os
import platform
import json
import wrapt

from Libs import Settings, Logger

try:
    import Context
    import ProjectsManager
    import RepoTests
    import RepoPublic
    import RepoArchives
    import TaskManager
    import AgentsManager
    import ProbesManager
    import RepoAdapters
    import RepoLibraries
    import ToolboxManager
    import UsersManager
    import CliFunctions
    import HelperManager
except ImportError: # python3 support
    from . import Context
    from . import ProjectsManager
    from . import RepoTests
    from . import RepoPublic
    from . import RepoArchives
    from . import TaskManager
    from . import AgentsManager
    from . import ProbesManager
    from . import RepoAdapters
    from . import RepoLibraries
    from . import ToolboxManager
    from . import UsersManager
    from . import CliFunctions
    from . import HelperManager
    
try:
    import hashlib
    sha1_constructor = hashlib.sha1
except ImportError as e: # support python 2.4
    import sha
    sha1_constructor = sha.new
    
import Libs.FileModels.TestSuite as TestSuite
import Libs.FileModels.TestUnit as TestUnit
import Libs.FileModels.TestPlan as TestPlan
import Libs.FileModels.TestAbstract as TestAbstract
import Libs.FileModels.TestConfig as TestConfig

class EmptyValue(Exception): pass

def _get_user(request):
    """
    Lookup a user session or return None if one doesn't exist
    """
    sess_id = request.cookies.get("session_id")
    if sess_id is None:
        # new in v17, checking authorization header
        authorization = request.get_header(name="Authorization", default=None)
        if authorization is not None:
            userP = Context.instance().apiAuthorizationV2(authorization=authorization)
            if userP is None:
                raise HTTP_401("Invalid credentials")
            else:
                return userP
        else:
            raise HTTP_401("Authorization header not detected")
        # end of new
    else:
        if sess_id in Context.instance().getSessions():
            return Context.instance().getSessions()[sess_id]
        else:
            raise HTTP_401("Invalid session")

@wrapt.decorator
def _to_yaml(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for yaml generator
    """
    return wrapped(*args, **kwargs)
    
@wrapt.decorator
def _to_yaml_defs(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for yaml generator
    """
    return wrapped(*args, **kwargs)
    
@wrapt.decorator
def _to_yaml_tags(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for yaml generator
    """
    return wrapped(*args, **kwargs)
    
"""
Swagger object definitions
"""
class SwaggerDefinitions(object):
    """
    """
    #@_to_yaml_defs
    def ResponseGeneric(self):
        """
        type: object
        properties:
          cmd:
            type: string
          message:
            type: string
        """
        pass
    
"""
Swagger tags
"""
class SwaggerTags(object):
    """
    """
    @_to_yaml_tags
    def session(self):
        """
        Everything about your session
        """
        pass
    @_to_yaml_tags
    def variables(self):
        """
        Everything to manage projects variables
        """
        pass
    @_to_yaml_tags
    def tests(self):
        """
        Everything to manage your tests
        """
        pass
    @_to_yaml_tags
    def tasks(self):
        """
        Everything to manage your tasks
        """
        pass
    @_to_yaml_tags
    def public(self):
        """
        Everything to manage your tasks
        """
        pass 
    @_to_yaml_tags
    def results(self):
        """
        Everything to manage your test results
        """
        pass 
    @_to_yaml_tags
    def reports(self):
        """
        Everything to get your test reports
        """
        pass  
"""
Sessions handlers
"""
class SessionLogin(Handler):
    """
    /rest/session/login
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - session
        summary: Authenticate client
        description: ''
        operationId: loginSession
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required: [login,password]
              properties:
                login:
                  type: string
                password:
                  type: string
                  description: sha1 password
        responses:
          '200':
            description: Logged in
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                expires:
                  type: integer
                user_id:
                  type: integer
                session_id:
                  type: string
                project_id:
                  type: integer
            examples:
              application/json: |
                {
                  "expires": 86400, 
                  "user_id": 2, 
                  "cmd": "/session/login", 
                  "session_id": "NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M", 
                  "message": "Logged in", 
                  "project_id": 1
                }
            headers:
              Set-Cookie:
                type: string
                description: |
                  session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M;expires=Wed, 10-May-2017 06:32:57 GMT; path=/ 
          '401':
            description: Invalid login | Account disabled | Access not authorized | Invalid  password
          '400':
            description: Bad request provided
        """
        try:
            login = self.request.data.get("login")
            password = self.request.data.get("password")
            
            if not login or not password:
                raise EmptyValue("Please specify login and password")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # check user access 
        (userSession, expires) = Context.instance().apiAuthorization(login=login, password=password)
        
        if userSession == Context.instance().CODE_NOT_FOUND:
            raise HTTP_401("Invalid login")

        if userSession == Context.instance().CODE_DISABLED:
            raise HTTP_401("Account disabled")

        if userSession == Context.instance().CODE_FORBIDDEN:
            raise HTTP_401("Access not authorized")

        if userSession == Context.instance().CODE_FAILED:
            raise HTTP_401("Invalid  password")

        lease = Settings.get('Users_Session', 'max-expiry-age') #in seconds
        userProfile = Context.instance().getSessions()[userSession]
        
        self.response.set_cookie(key="session_id", value=userSession, expires=expires, path='/', domain="") 
        return { "cmd": self.request.path, "message":"Logged in", "session_id": userSession, "expires": int(lease), 
                "user_id": userProfile['id'], "project_id":  userProfile['defaultproject'] }
        
class SessionLogout(Handler):
    """
    /rest/session/logout
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - session
        summary: Logout client
        description: ''
        operationId: logoutSession
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: Logged out | Not logged in
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "logged out",
                  "cmd": "/session/logout"
                }
            headers:
              Set-Cookie:
                type: string
                description: |
                  session_id=DELETED;expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/ 
        """
        sess_id = self.request.cookies.get("session_id")
        
        if sess_id in Context.instance().getSessions():
            del Context.instance().getSessions()[sess_id]
            self.response.delete_cookie("session_id")
            return {  "cmd": self.request.path, "message":"logged out" } 

        return { "cmd": self.request.path, "message":"Not logged in" }
        
class SessionRefresh(Handler):
    """
    /rest/session/refresh
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - session
        summary: Refresh session
        description: ''
        operationId: refreshSession
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: Session refreshed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "session refreshed",
                  "cmd": "/session/refresh"
                }
            headers:
              Set-Cookie:
                type: string
                description: |
                  session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M;expires=Wed, 10-May-2017 06:32:57 GMT; path=/ 
          '401':
            description: Access denied
        """
        sess_user = _get_user(request=self.request)
        sess_id = self.request.cookies.get("session_id")
        
        expires = Context.instance().updateSession(sessionId=sess_id)
        self.response.set_cookie(key="session_id", value=sess_id, expires=expires, path='/', domain="") 
        return { "cmd": self.request.path, "message":"session refreshed" }

"""
Tasks handlers
"""
class TasksRunning(Handler):
    """
    /rest/tasks/running
    """   
    def get(self):
        """
        tags:
          - tasks
        summary: Get all running tasks
        description: ''
        operationId: runningTasks
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: Running tasks
            schema :
              properties:
                cmd:
                  type: string
                tasks-running:
                  type: array
            examples:
              application/json: |
                {
                  "tasks-running": [],
                  "cmd": "/tasks/running"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)
        
        USER_CTX = Context.UserContext(login=user_profile['login'])
        
        running = TaskManager.instance().getRunning(b64=False, user=USER_CTX)
        return { "cmd": self.request.path, "tasks-running": running }
        
class TasksWaiting(Handler):
    """
    /rest/tasks/waiting
    """   
    def get(self):
        """
        tags:
          - tasks
        summary: Get all waiting tasks
        description: ''
        operationId: waitingTasks
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: Waiting tasks
            schema :
              properties:
                cmd:
                  type: string
                tasks-waiting:
                  type: array
            examples:
              application/json: |
                {
                  "tasks-waiting": [],
                  "cmd": "/tasks/waiting"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        USER_CTX = Context.UserContext(login=user_profile['login'])
        
        waiting = TaskManager.instance().getWaiting(b64=False, user=USER_CTX)
        return { "cmd": self.request.path, "tasks-waiting": waiting }
        
class TasksHistory(Handler):
    """
    /rest/tasks/history
    """   
    def get(self):
        """
        tags:
          - tasks
        summary: Get all history tasks
        description: ''
        operationId: historyTasks
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: History tasks
            schema :
              properties:
                cmd:
                  type: string
                tasks-history:
                  type: array
            examples:
              application/json: |
                {
                  "tasks-history": [],
                  "cmd": "/tasks/history"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        USER_CTX = Context.UserContext(login=user_profile['login'])
        
        history = TaskManager.instance().getHistory(b64=False, user=USER_CTX)
        return { "cmd": self.request.path, "tasks-history": history }
 
class TasksCancel(Handler):
    """
    /rest/tasks/cancel
    """   
    def post(self):
        """
        tags:
          - tasks
        summary: Cancel all waiting tasks or one specific task according to the id
        description: ''
        operationId: cancelTasks
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ task-id ]
              properties:
                task-id:
                  type: integer
                  description: task id to cancel
        responses:
          '200':
            description: Tasks successfully canceled
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "tasks successfully canceled",
                  "cmd": "/tasks/cancel"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            taskId = self.request.data.get("task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input
        if taskId is not None:
            if not isinstance(taskId, int):
                raise HTTP_400("Bad task id provided in request, int expected")
        
        if taskId is None:
            success = TaskManager.instance().cancelAllTasks()
        else:
            success = TaskManager.instance().cancelTask(taskId=taskId)
            if success is None:
                raise HTTP_500( "task not found" )

        return { "cmd": self.request.path, "message": "tasks successfully canceled" }
        
class TasksKill(Handler):
    """
    /rest/tasks/kill
    """   
    def post(self):
        """
        tags:
          - tasks
        summary: Kill all running tasks or one specific task according to the id
        description: ''
        operationId: killTasks
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ task-id ]
              properties:
                task-id:
                  type: integer
                  description: task id to kill
        responses:
          '200':
            description: Tasks successfully killed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "tasks successfully killed",
                  "cmd": "/tasks/kill"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            taskId = self.request.data.get("task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input
        if taskId is not None:
            if not isinstance(taskId, int):
                raise HTTP_400("Bad task id provided in request, int expected")
        
        if taskId is None:
            success = TaskManager.instance().killAllTasks()
        else:
            success = TaskManager.instance().killTask(taskId=taskId)
            if success is None:
                raise HTTP_500( "task not found" )

        return { "cmd": self.request.path, "message": "tasks successfully killed" }
        
class TasksReset(Handler):
    """
    /rest/tasks/reset
    """   
    def get(self):
        """
        tags:
          - tasks
        summary: Reset history tasks
        description: ''
        operationId: resetTasks
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: Tasks successfully reseted
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "tasks successfully reseted",
                  "cmd": "/tasks/reset"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)

        success, details = TaskManager.instance().resetHistoryInDb()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        return { "cmd": self.request.path, "message": "tasks successfully reseted" }
    
"""
Public storage handlers
"""
class PublicListing(Handler):
    """
    /rest/public/listing
    """   
    def get(self):
        """
        tags:
          - public_storage
        summary: Get the listing of all files and folders in the public area
        description: ''
        operationId: listingPublic
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
        responses:
          '200':
            description: Listing file in public area
            schema :
              properties:
                cmd:
                  type: string
                public-listing:
                  type: array
            examples:
              application/json: |
                {
                  "public-listing": [],
                  "cmd": "/public/listing"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)

        listing = RepoPublic.instance().getBasicListing()  
        
        return { "cmd": self.request.path, "public-listing": listing }

class PublicDirectoryAdd(Handler):
    """
    /rest/public/directory/add
    """   
    def post(self):
        """
        tags:
          - public_storage
        summary: Add directory in the public storage
        description: ''
        operationId: addFolderPublic
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ directory-path, directory-name ]
              properties:
                directory-path:
                  type: string
                directory-name:
                  type: string
        responses:
          '200':
            description: Directory successfully added
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "directory successfully added",
                  "cmd": "/public/directory/add"
                }
          '401':
            description: Access denied 
          '400':
            description: Bad request
          '403':
            description: Directory already exists
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            folderName = self.request.data.get("directory-name")
            if not folderName: raise EmptyValue("Please specify a source folder name")
            
            folderPath = self.request.data.get("directory-path")
            if not folderPath: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoPublic.instance().addDir(pathFolder=folderPath, folderName=folderName)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add directory")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully added" } 
        
class PublicDirectoryRename(Handler):
    """
    /rest/public/directory/rename
    """   
    def post(self):
        """
        tags:
          - public_storage
        summary: Rename directory name in the public storage
        description: ''
        operationId: renameFolderPublic
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ directory-path, directory-name ]
                  properties:
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ directory-name ]
                  properties:
                    directory-name:
                      type: string
        responses:
          '200':
            description: Directory successfully renamed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "directory successfully renamed",
                  "cmd": "/public/directory/rename"
                }
          '401':
            description: Access denied 
          '400':
            description: Bad request
          '403':
            description: Directory already exists
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
       
        try:
            folderName = self.request.data.get("source")["directory-name"]
            if not folderName: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if not folderPath: raise EmptyValue("Please specify a source folder path")
            
            newFolderName = self.request.data.get("destination")["directory-name"]
            if not newFolderName: raise EmptyValue("Please specify a destination folder name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoTests.instance().renameDir(mainPath=folderPath, oldPath=folderName, 
                                                newPath=newFolderName)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to rename directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully renamed" }

class PublicDirectoryRemove(Handler):
    """
    /rest/public/directory/remove
    """   
    def post(self):
        """
        tags:
          - public_storage
        summary: Remove directory in the public storage and their contents recursively
        description: ''
        operationId: removeFolderPublic
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ source ]
              properties:
                source:
                  type: object
                  required: [ directory-path ]
                  properties:
                    directory-path:
                      type: string
                recursive:
                  type: boolean
        responses:
          '200':
            description: Directory successfully removed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "directory successfully removed",
                  "cmd": "/public/directory/remove"
                }
          '401':
            description: Access denied 
          '400':
            description: Bad request
          '403':
            description: Cannot remove directory | Removing directory denied
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            folderPath = self.request.data.get("source")["directory-path"]
            if not folderPath: raise EmptyValue("Please specify a source folder path")
            _recursive = self.request.data.get("recursive")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if _recursive is None:
            recursive = False
        else:
            recursive = _recursive

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        if recursive:
            success = RepoTests.instance().delDirAll(folderPath)  
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500("Unable to remove directory")
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_500("Unable to remove directory (missing)")
            if success == Context.instance().CODE_FORBIDDEN:
                raise HTTP_403("Removing directory denied")
        else:
            success = RepoTests.instance().delDir(folderPath)  
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500("Unable to remove directory")
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_500("Unable to remove directory (missing)")
            if success == Context.instance().CODE_FORBIDDEN:
                raise HTTP_403("Cannot remove directory")
                
        return { "cmd": self.request.path, "message": "directory successfully removed" }

class PublicImport(Handler):
    """
    /rest/public/file/import
    """
    def post(self):
        """
        tags:
          - public_storage
        summary: Import file to the public storage. Provide the file in base64 format
        description: ''
        operationId: importFilePublic
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ file-path, file-content ]
              properties:
                file-path:
                  type: string
                file-content:
                  type: string
                  string: in base64 format
        responses:
          '200':
            description: File sucessfully imported
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "file sucessfully imported",
                  "cmd": "/public/file/import"
                }
          '401':
            description: Access denied 
          '400':
            description: Bad request
          '403':
            description: File already exists
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            filePath = self.request.data.get("file-path")
            fileContent = self.request.data.get("file-content")
            if not projectName and not filePath and not fileContent:
                raise EmptyValue("Please specify a project name, file content and path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        _filePath, fileExtension = filePath.rsplit(".", 1)
        _filePath = _filePath.rsplit("/", 1)
        if len(_filePath) == 2:
            filePath = _filePath[0]
            fileName =  _filePath[1]
        else:
            filePath = "/"
            fileName =  _filePath[0]
            
        success, _, _, _, _ = RepoTests.instance().importFile( pathFile=filePath, nameFile=fileName, extFile=fileExtension,
                                                               contentFile=fileContent, binaryMode=True)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("File already exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully imported" }

class PublicRemove(Handler):
    """
    Remove file from the public storage
    """   
    def post(self):
        """
        Remove file from the public storage
        Send POST request (uri /rest/public/file/remove) with the following body JSON 
        { "file-path": "/" }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            filePath = self.request.data.get("file-path")
            if not projectName and not filePath:
                raise EmptyValue("Please specify a project name and file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoTests.instance().delFile( pathFile=filePath, supportSnapshot=False)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove file")
        if success == Context.instance().CODE_FAILED:
            raise HTTP_403("Remove file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully removed" }

class PublicRename(Handler):
    """
    Rename file in the public storage
    """
    def post(self):
        """
        Rename file in the public storage
        Send POST request (uri /rest/public/file/rename) with the following body JSON 
            { 
                "source":      {"file-path": "/", "file-name": "test", "file-extension": "tsx"  },
                "destination":  { "file-name": "test" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            fileName = self.request.data.get("source")["file-path"]
            if not fileName: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-name"]
            if not filePath: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if not fileExt: raise EmptyValue("Please specify a source file extension")
            
            newFileName = self.request.data.get("destination")["file-name"]
            if not newFileName: raise EmptyValue("Please specify a destination file name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoTests.instance().renameFile( 
                                                    mainPath=filePath, 
                                                    oldFilename=fileName, 
                                                    newFilename=newFileName, 
                                                    extFilename=fileExt,
                                                    supportSnapshot=False
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Rename file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully renamed" }

class PublicDownload(Handler):
    """
    Download file from the public storage
    """   
    def post(self):
        """
        Download file from the public storage in base64 format
        Send POST request (uri /rest/public/file/download) with the following body JSON { "file-path": "/" }
        Cookie session_id is mandatory.

        @return: file content encoding in base64
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            filePath = self.request.data.get("file-path")
            if not projectName and not filePath:
                raise EmptyValue("Please specify a project name and file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success, _, _, _, content, _, _ = RepoTests.instance().getFile(pathFile=filePath, binaryMode=True, addLock=False)  
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to download file")

        return { "cmd": self.request.path, "file-content": content }

"""
Adapters handler
"""     
class AdaptersStatistics(Handler):
    """
    Get the adapters statistics 
    """   
    # @_requires_login()
    def get(self):
        """
        Get the adapters statistics  (uri /rest/adapters/statistics).
        Cookie session_id is mandatory.
        
        @return: statistics or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")

        _, _, _, statistics = RepoAdapters.instance().getTree(b64=True)
        
        return { "cmd": self.request.path, "adapters-statistics": statistics }

class AdaptersSetDefault(Handler):
    """
    Configure adapters as default
    """   
    # @_requires_login()
    def post(self):
        """
        Configure adapters as default or generic
        Send POST request (uri /rest/adapters/configure) with the following body JSON { "adapters": "v1000" }
        Cookie session_id is mandatory.

        @return: success message or error
        @rtype: dict 
        """
        # user_profile = _get_user(self.request)
        
        try:
            adapters = self.request.data.get("adapters")
            if not adapters: raise EmptyValue("Please specify the adapters")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoAdapters.instance().setDefaultV2(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as default the package %s" % adapters )

        return { "cmd": self.request.path, "status": success }

class AdaptersSetGeneric(Handler):
    """
    Configure adapters as generic
    """   
    # @_requires_login()
    def post(self):
        """
        Configure adapters as default or generic
        Send POST request (uri /rest/adapters/configure)  with the following body JSON { "adapters": "v1000" }
        Cookie session_id is mandatory.

        @return: success message or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)
        
        try:
            adapters = self.request.data.get("adapters")
            if not adapters: raise EmptyValue("Please specify the adapters")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoAdapters.instance().setGeneric(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as generic the package %s" % adapters )
                
        return { "cmd": self.request.path, "status": success }
        
class AdaptersCheckSyntax(Handler):
    """
    Check the syntax of the adapters
    """   
    # @_requires_login()
    def get(self):
        """
        Check the syntax of the adapters  (uri /rest/adapters/check/syntax).
        Cookie session_id is mandatory.
        
        @return: success message or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)

        success, details = RepoAdapters.instance().checkGlobalSyntax()
        
        return { "cmd": self.request.path, "syntax-status": success, "syntax-error": details }

"""
Libraries handler
"""     
class LibrariesStatistics(Handler):
    """
    Get the libraries statistics 
    """   
    # @_requires_login()
    def get(self):
        """
        Get the libraries statistics  (uri /rest/libraries/statistics).
        Cookie session_id is mandatory.
        
        @return: statistics or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")

        _, _, _, statistics = RepoLibraries.instance().getTree(b64=True)
        
        return { "cmd": self.request.path, "libraries-statistics": statistics }

class LibrariesSetDefault(Handler):
    """
    Configure libraries as default
    """   
    # @_requires_login()
    def post(self):
        """
        Configure libraries as default or generic
        Send POST request (uri /rest/libraries/configure)  with the following body JSON { "libraries": "v1000" }
        Cookie session_id is mandatory.

        @return: success message or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)
        
        try:
            libraries = self.request.data.get("libraries")
            if not libraries: raise EmptyValue("Please specify the libraries")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoLibraries.instance().setDefaultV2(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as default the package %s" % libraries )

        return { "cmd": self.request.path, "status": success }

class LibrariesSetGeneric(Handler):
    """
    Configure libraries as default or generic
    """   
    # @_requires_login()
    def post(self):
        """
        Configure libraries as default or generic
        Send POST request (uri /rest/libraries/configure)  with the following body JSON { "libraries": "v1000" }
        Cookie session_id is mandatory.

        @return: success message or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)
        
        try:
            libraries = self.request.data.get("libraries")
            if not libraries: raise EmptyValue("Please specify the libraries")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoLibraries.instance().setGeneric(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as generic the package %s" % libraries )
                
        return { "cmd": self.request.path,  "status": success }
        
class LibrariesCheckSyntax(Handler):
    """
    Check the syntax of the libraries
    """   
    # @_requires_login()
    def get(self):
        """
        Check the syntax of the libraries  (uri /rest/libraries/check/syntax).
        Cookie session_id is mandatory.
        
        @return: success message or error
        @rtype: dict 
        """
        user_profile = _get_user(self.request)

        success, details = RepoLibraries.instance().checkGlobalSyntax()
        
        return { "cmd": self.request.path, "syntax-status": success, "syntax-error": details }
 
"""
Documentations handler
"""     
class DocumentationsListing(Handler):
    """
    Get the documentations
    """   
    # @_requires_login()
    def get(self):
        """
        Get the documentations  (uri /rest/documentations/listing).
        Cookie session_id is mandatory.
        
        @return: documentations
        @rtype: dict 
        """
        user_profile = _get_user(self.request)

        docs = {}
        docs["online"] = HelperManager.instance().getHelps()
        
        return { "cmd": self.request.path, "documentations": docs }
        
class DocumentationsBuild(Handler):
    """
    Build the cache for the documentations
    """   
    # @_requires_login()
    def get(self):
        """
        Build the cache for the documentations (uri /rest/documentations/build).
        Cookie session_id is mandatory.
        
        @return: documentations
        @rtype: dict 
        """
        user_profile = _get_user(self.request)

        success, details = HelperManager.instance().generateHelps()
        if not success:
            raise HTTP_500("Unable to build the documentations")
        return { "cmd": self.request.path, "build": "success" }
        
"""
Tests handlers
"""
class TestsRun(Handler):
    """
    /rest/tests/run
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Run one test according to the project name and the path, name and extension of the test. 
        description: ''
        operationId: runTest
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ test-path ]
              properties:
                test-path:
                  type: string
                project-name:
                  type: string
                project-id:
                  type: string
                test-inputs:
                  type: array
                  description: Test inputs parameters can be used to overwrite the original test parameters
                  items:
                    type: object
                    required: [ name, value, type ]
                    properties:
                      name:
                        type: string
                      type:
                        type: string
                      value:
                        type: string
                test-outputs:
                  type: array
                  description: Test outputs parameters can be used to overwrite the original test parameters
                  items:
                    type: object
                    required: [ name, value, type ]
                    properties:
                      name:
                        type: string
                      type:
                        type: string
                      value:
                        type: string
                test-adapters:
                  type: string
                  description: adapters options can be used to select the adapters or libraries
                test-librairies:
                  type: string
                  description: libraries options can be used to select the adapters or libraries
                test-agents:
                  type: array
                  description: agents parameters can be used to overwrite the original test
                  items:
                    type: object
                    required: [ name, value, type ]
                    properties:
                      name:
                        type: string
                      type:
                        type: string
                      value:
                        type: string
                number-occurences:
                  type: integer
                  description: Specify the number of occurences to execute your test several times in successive mode
                schedule:
                  description: Schedule your run    
                  type: object
                  required: [ at, type ]
                  properties:
                    at:
                      type: array
                      description: (year, month, day,hours,minutes,seconds)
                    type:
                      type: string
                      description: weekly/daily/hourly/every/min/at/in
                testcfg-inputs:
                  description: Test config file can be used to provide test parameters
                  type: object
                  required: [ project-name, testcfg-path ]
                  properties:
                    project-name:
                      type: string
                    testcfg-path:
                      type: string
                testcfg-outputs:
                  description: Test config file can be used to provide test parameters
                  type: object
                  required: [ project-name, testcfg-path ]
                  properties:
                    project-name:
                      type: string
                    testcfg-path:
                      type: string
        responses:
          '200':
            description: test executed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                test-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/run", 
                  "message": "test executed"
                  "test-id": "bd0df6b4-10df-4a57-a970-8d693ddb4cfa"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project | Test extension not accepted
          '404':
            description: Test does not exists in repository
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            testPath = self.request.data.get("test-path")
            testInputs = self.request.data.get("test-inputs")
            testOutputs = self.request.data.get("test-outputs")
            sutAdapters = self.request.data.get("test-adapters")
            sutLibraries = self.request.data.get("test-libraries")
            testAgents = self.request.data.get("test-agents")

            numberRuns = self.request.data.get("number-occurences")
            schedule = self.request.data.get("schedule")
            
            testcfgInputs = self.request.data.get("testcfg-inputs")
            testcfgOutputs = self.request.data.get("testcfg-outputs")
            
            if not testPath: raise EmptyValue("Please specify a project name and test path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # check if the file exists
        if not os.path.isfile( "%s/%s/%s" % (RepoTests.instance().testsPath, prjId, testPath) ):
            raise HTTP_404('Test does not exists in repository')
        
        # extract test name and test extension
        testExtension = testPath.rsplit(".", 1)[1]
        testName = "/%s" % testPath
        testName = testName.rsplit("/", 1)[1].rsplit(".", 1)[0]
        
        # checking schedule
        runNb = -1; runType=-1;
        runAt = (0,0,0,0,0,0)
        if numberRuns is not None:
            if not isinstance(numberRuns, int):
                raise HTTP_400("Bad number runs in request, integer expected")
            if numberRuns < 1:
                raise HTTP_400("Bad number runs in request, must be greater to 1")
            if numberRuns > 1:
                runNb = numberRuns; runType = 8; # successive mode 
        if schedule is not None:
            if not isinstance(schedule, dict):
                raise HTTP_400("Bad schedule in request, dict expected")
            if "at" not in schedule:
                raise HTTP_400("At is missing in request")
            if "type" not in schedule:
                raise HTTP_400("Type is missing in request")
            if schedule["type"] in [ "weekly", "daily", "hourly", "every", "min", "at", "in" ]:
                raise HTTP_400("Bad type value in request")
            if not isinstance(schedule["at"], tuple):
                raise HTTP_400("Bad at type in request, tuple expected")
            if len(schedule["at"]) != 6:
                raise HTTP_400("Bad at tuple in request, tuple of 6 integers expected")
            
            if schedule["type"] == "weekly": runType = 7
            if schedule["type"] == "daily": runType = 5
            if schedule["type"] == "hourly": runType = 4
            if schedule["type"] == "every": runType = 6
            if schedule["type"] == "min": runType = 3
            if schedule["type"] == "at": runType = 0
            if schedule["type"] == "in": runType = 1
            
            runAt = schedule["at"]
            
        # checking test inputs, adapters and libraries type
        if testInputs is not None:
            if not isinstance(testInputs, list): 
                raise HTTP_400("Bad test inputs provided in request, list expected")
            for inp in testInputs:
                if not isinstance(inp, dict):     
                    raise HTTP_400("Bad test inputs provided in request, list of dict expected")
                if not ( "name" in inp and "type" in inp and "value" in inp ):
                    raise HTTP_400("Bad test format inputs provided in request")
                    
        if testOutputs is not None:
            if not isinstance(testOutputs, list): 
                raise HTTP_400("Bad test outputs provided in request, list expected")
            for out in testOutputs:
                if not isinstance(out, dict):     
                    raise HTTP_400("Bad test outputs provided in request, list of dict expected")
                if not ( "name" in out and "type" in out and "value" in out ):
                    raise HTTP_400("Bad test format outputs provided in request")
                    
        if testAgents is not None:
            if not isinstance(testAgents, list): 
                raise HTTP_400("Bad test agents provided in request, list expected")
            for agt in testAgents:
                if not isinstance(agt, dict):     
                    raise HTTP_400("Bad test agents provided in request, list of dict expected")
                if not ( "name" in agt and "type" in agt and "value" in agt ):
                    raise HTTP_400("Bad test format agents provided in request")

        if sutAdapters is not None:
            if not isinstance(sutAdapters, str): 
                raise HTTP_400("Bad sut adapter provided in request, str expected")
        
        if sutLibraries is not None:
            if not isinstance(sutLibraries, str): 
                raise HTTP_400("Bad sut library provided in request, str expected")
              
        if testcfgInputs is not None:
            if not isinstance(testcfgInputs, dict): 
                raise HTTP_400("Bad test config inputs provided in request, dict expected")
            if not ( "project-name" in testcfgInputs and "testcfg-path" in testcfgInputs ) :
                raise HTTP_400("Bad test config inputs provided in request, dict expected with project name and path")
            
            if not testcfgInputs["testcfg-path"].endswith(".tcx"):
                raise HTTP_400('Tcx file required for test config inputs')
                
            # get the project id according to the name and checking authorization
            projectcfgId = ProjectsManager.instance().getProjectID(name=testcfgInputs["project-name"])   
            projectcfgAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=projectcfgId)
            if not projectcfgAuthorized:
                raise HTTP_403('Access denied to this project for config')
           
            # read the file
            cfgInputs = TestConfig.DataModel()
            resInputs = cfgInputs.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, projectcfgId, testcfgInputs["testcfg-path"]) )
            if not resInputs: 
                raise HTTP_500('unable to read test config for inputs')
                
        if testcfgOutputs is not None:
            if not isinstance(testcfgOutputs, dict): 
                raise HTTP_400("Bad test config outputs provided in request, dict expected")
            if not ( "project-name" in testcfgOutputs and "testcfg-path" in testcfgOutputs ) :
                raise HTTP_400("Bad test config outputs provided in request, dict expected with project name and path")
           
            if not testcfgOutputs["testcfg-path"].endswith(".tcx"):
                raise HTTP_400('Tcx file required for test config outputs')
                
            # get the project id according to the name and checking authorization
            projectcfgId = ProjectsManager.instance().getProjectID(name=testcfgOutputs["project-name"])   
            projectcfgAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=projectcfgId)
            if not projectcfgAuthorized:
                raise HTTP_403('Access denied to this project for config')
                
            cfgOutputs = TestConfig.DataModel()
            resOutputs = cfgOutputs.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, projectcfgId, testcfgOutputs["testcfg-path"]) )
            if not resOutputs: 
                raise HTTP_500('unable to read test config for outputs')
                
        # read the test file from test repository
        if testExtension == 'tsx':
            doc = TestSuite.DataModel()
            res = doc.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, prjId, testPath) )
            if not res: 
                raise HTTP_500('unable to read test suite')
            
            testData = { 'src-test': doc.testdef, 'src-exec': doc.testexec, 'properties': doc.properties['properties'] }
  
        elif testExtension == 'tux':
            doc = TestUnit.DataModel()
            res = doc.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, prjId, testPath) )
            if not res: 
                raise HTTP_500('unable to read test unit')
                
            testData = { 'testunit': True, 'src-test': doc.testdef, 'src-exec': '', 'properties': doc.properties['properties'] }
                
        elif testExtension == 'tax':
            doc = TestAbstract.DataModel()
            res = doc.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, prjId, testPath) )
            if not res: 
                raise HTTP_500('unable to read test abstract')
            
            testData = { 'testabstract': True, 'src-test': doc.testdef, 'src-exec': '', 'properties': doc.properties['properties'] }
                            
        elif testExtension == 'tpx':
            doc = TestPlan.DataModel()
            res = doc.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, prjId, testPath) )
            if not res: 
                raise HTTP_500('unable to read test plan')

            rslt = RepoTests.instance().addtf2tp( data_= doc.getSorted() )
            if rslt is not None:
                _, err = rslt
                raise HTTP_404('test not found: %s' % err)
            testData = { 'testplan': doc.getSorted(),  'properties': doc.properties['properties'] }
                            
        elif testExtension == 'tgx':
            doc = TestPlan.DataModel()
            res = doc.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, prjId, testPath) )
            if not res: raise HTTP_500('unable to read test plan')

            rslt, alltests = RepoTests.instance().addtf2tg( data_= doc.getSorted() )
            if rslt is not None:
                _, err = rslt
                raise HTTP_404('test not found: %s' % err)
            testData = { 'testglobal': alltests, 'properties': doc.properties['properties'] }
                
        else:
            raise HTTP_403('test extension not accepted: %s' % testExtension )
        
        # personalize test inputs and outputs ?
        if testInputs is not None:
            for newInp in testInputs:
                for origInp in testData["properties"]['inputs-parameters']['parameter']:
                    # if the param exist on the original test than overwrite them
                    if newInp["name"] == origInp["name"]:
                        origInp["value"] = newInp["value"]
                        origInp["type"] = newInp["type"]
        
        if testOutputs is not None:
            for newOut in testOutputs:
                for origOut in testData["properties"]['outputs-parameters']['parameter']:
                    # if the param exist on the original test than overwrite them
                    if newOut["name"] == origOut["name"]:
                        origOut["value"] = newOut["value"]
                        origOut["type"] = newOut["type"]
        
        if testAgents is not None:
            for newAgt in testAgents:
                for origAgt in testData["properties"]["agents"]["agent"]:
                    # if the param exist on the original test than overwrite them
                    if newAgt["name"] == origAgt["name"]:
                        origAgt["value"] = newAgt["value"]
                        origAgt["type"] = newAgt["type"]
              
        if testcfgInputs is not None:
            testData["properties"]['inputs-parameters']['parameter'] = cfgInputs.properties['properties']['parameters']['parameter']
              
        if testcfgOutputs is not None:
            testData["properties"]['outputs-parameters']['parameter'] = cfgOutputs.properties['properties']['parameters']['parameter']
            
        # personalize test description ?
        if sutAdapters is not None:
            for origDescr in testData["properties"]["description"]:
                if origDescr["key"] == "adapters":
                    origDescr["value"] = sutAdapters
                    
        if sutLibraries is not None:
            for origDescr in testData["properties"]["description"]:
                if origDescr["key"] == "libraries":
                    origDescr["value"] = sutLibraries
                    

        # register the test in the task manager
        # extract the extension from test path
        task = TaskManager.instance().registerTask(
                                                    testData=testData, testName=testName, testPath=testPath.rsplit(".", 1)[0], 
                                                    testUser=user_profile['login'], testId=0, testUserId=user_profile['id'],
                                                    testBackground=True, runAt=runAt, runType=runType, runNb=runNb, 
                                                    testProjectId=prjId
                                                  )
        if task.lastError is None:
            # taskID = task.generateTestID()
            taskID = task.getTestID()
            if not taskID: raise HTTP_500('unable to generate test id')
                
        else:
            raise HTTP_500('unable to run test: %s' % task.lastError )
            
        return { "cmd": self.request.path, "message": "test executed", "test-id": taskID }
  
class TestsListing(Handler):
    """
    /rest/tests/basic/listing
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Get the listing of all tests.
        description: ''
        operationId: listingTests
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              properties:
                project-name:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: tests listing
            schema :
              properties:
                cmd:
                  type: string
                tests-listing:
                  type: array
                  items:
                    type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/basic/listing", 
                  "tests-listing": ["/Snippets/UI/03_OpenBrowser.tux", "/Snippets/UI/05_MaximizeBrowser.tux"],
                  "project-id": 1
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        listing = RepoTests.instance().getBasicListing(projectId=prjId)  
        
        return { "cmd": self.request.path, "tests-listing": listing, "project-id": prjId }
        
class TestsStatistics(Handler):
    """
    Get the tests statistics 
    """   
    def post(self):
        """
        Get the tests statistics 
        Send POST request (uri /rest/tests/statistics) with the following body JSON 
        { [ "project-id": <integer>] [, "project-name": <string>] }
        Cookie session_id is mandatory.

        @return: tests listing or error
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        _, _, _, statistics = RepoTests.instance().getTree(b64=True,  project=prjId )
        
        return { "cmd": self.request.path, "tests-statistics": statistics, "project-id": prjId }
        
class TestsDownload(Handler):
    """
    Download file from the test storage
    """   
    def post(self):
        """
        Download file from the test storage in base64 format
        Send POST request (uri /rest/tests/file/download) with the following body JSON 
        { [ "project-id": <integer>] [, "project-name": <string>] , "file-path": "/" }
        Cookie session_id is mandatory.

        @return: file content encoding in base64
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            filePath = self.request.data.get("file-path")
            if not filePath: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success, _, _, _, content, _, _ = RepoTests.instance().getFile(pathFile=filePath, binaryMode=True, project=prjId, addLock=False)  
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to download file")

        return { "cmd": self.request.path, "file-content": content }

class TestsImport(Handler):
    """
    Import file to the test storage
    """   
    def post(self):
        """
        Import file to the test storage. Provide the file in base64 format
        Send POST request (uri /rest/tests/file/import) with the following body JSON 
        { [ "project-id": <integer>] [, "project-name": <string>] , "file-path": "/", "file-content": "...." }
        Cookie session_id is mandatory.

        @return: success message or error
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            filePath = self.request.data.get("file-path")
            fileContent = self.request.data.get("file-content")
            if not filePath and not fileContent: raise EmptyValue("Please specify a file content and path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        _filePath, fileExtension = filePath.rsplit(".", 1)
        _filePath = _filePath.rsplit("/", 1)
        if len(_filePath) == 2:
            filePath = _filePath[0]
            fileName =  _filePath[1]
        else:
            filePath = "/"
            fileName =  _filePath[0]
            
        success, _, _, _, _ = RepoTests.instance().importFile( pathFile=filePath, nameFile=fileName, extFile=fileExtension,
                                                                                contentFile=fileContent, binaryMode=True, project=prjId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("File already exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully imported" }

class TestsRemove(Handler):
    """
    Remove file from the test storage
    """   
    def post(self):
        """
        Remove file from the test storage
        Send POST request (uri /rest/tests/file/remove) with the following body JSON 
        { [ "project-id": <integer>] [, "project-name": <string>] , "file-path": "/" }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            filePath = self.request.data.get("file-path")
            if not filePath: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoTests.instance().delFile( pathFile=filePath, project=prjId, supportSnapshot=False)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove file")
        if success == Context.instance().CODE_FAILED:
            raise HTTP_403("Remove file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully removed" }
        
class TestsRename(Handler):
    """
    Rename file in the test storage
    """   
    def post(self):
        """
        Rename file in the test storage
        Send POST request (uri /rest/tests/file/rename) with the following body JSON 
            { 
                "source":      { [ "project-id": <integer>] [, "project-name": <string>], "file-path": "/", 
                                    "file-name": "test", "file-extension": "tsx"  },
                "destination":  { "file-name": "test" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        projectId = None
        projectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            fileName = self.request.data.get("source")["file-path"]
            if not fileName: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-name"]
            if not filePath: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if not fileExt: raise EmptyValue("Please specify a source file extension")
            
            newFileName = self.request.data.get("destination")["file-name"]
            if not newFileName: raise EmptyValue("Please specify a destination file name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoTests.instance().renameFile( 
                                                    mainPath=filePath, 
                                                    oldFilename=fileName, 
                                                    newFilename=newFileName, 
                                                    extFilename=fileExt,
                                                    project=prjId, 
                                                    supportSnapshot=False
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Rename file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully renamed" }
        
class TestsDuplicate(Handler):
    """
    Duplicate file in the test storage
    """   
    def post(self):
        """
        Duplicate file in the test storage 
        Send POST request (uri /rest/tests/file/duplicate) with the following body JSON 
            { 
                "source":      { [ "project-id": <integer>] [, "project-name": <string>], "file-path": "/", 
                                    "file-name": "test", "file-extension": "tsx"  },
                "destination":  { [ "project-id": <integer>] [, "project-name": <string>], "file-path": "/", "file-name": "test" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        projectId = None
        projectName = None
        newProjectId = None
        newProjectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            fileName = self.request.data.get("source")["file-path"]
            if not fileName: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-name"]
            if not filePath: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if not fileExt: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if "project-id" in destination: newProjectId = destination["project-id"]
            if "project-name" in destination: newProjectName = destination["project-name"]
            if not newProjectId and not newProjectName: raise EmptyValue("Please specify a project name or a project id")
            
            newFileName = self.request.data.get("destination")["file-name"]
            if not newFileName: raise EmptyValue("Please specify a destination file name")
            newFilePath = self.request.data.get("destination")["file-path"]
            if not newFilePath: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
        # checking input    
        if newProjectId is not None:
            if not isinstance(newProjectId, int):
                raise HTTP_400("Bad new project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # get the project id according to the name and checking authorization
        newPrjId = projectId
        if newProjectName: newPrjId = ProjectsManager.instance().getProjectID(name=newProjectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=newPrjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoTests.instance().duplicateFile( 
                                                        mainPath=filePath,
                                                        oldFilename=fileName,
                                                        newFilename=newFileName,
                                                        extFilename=fileExt,
                                                        project=prjId,
                                                        newProject=newPrjId,
                                                        newMainPath=newFilePath
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Duplicate file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully duplicated" }
        
class TestsMove(Handler):
    """
    Move file from the test storage
    """   
    def post(self):
        """
        Move file in the test storage 
        Send POST request (uri /rest/tests/file/move) with the following body JSON 
            { 
                "source":      { [ "project-id": <integer>] [, "project-name": <string>], "file-path": "/", 
                                    "file-name": "test", "file-extension": "tsx"  },
                "destination":  { [ "project-id": <integer>] [, "project-name": <string>], "file-path": "/" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
		
        projectId = None
        projectName = None
        newProjectId = None
        newProjectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            fileName = self.request.data.get("source")["file-path"]
            if not fileName: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-name"]
            if not filePath: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if not fileExt: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if "project-id" in destination: newProjectId = destination["project-id"]
            if "project-name" in destination: newProjectName = destination["project-name"]
            if not newProjectId and not newProjectName: raise EmptyValue("Please specify a project name or a project id")
            
            newFilePath = self.request.data.get("destination")["file-path"]
            if not newFilePath: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
        # checking input    
        if newProjectId is not None:
            if not isinstance(newProjectId, int):
                raise HTTP_400("Bad new project id provided in request, int expected")

        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # get the project id according to the name and checking authorization
        newPrjId = projectId
        if newProjectName: newPrjId = ProjectsManager.instance().getProjectID(name=newProjectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=newPrjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoTests.instance().moveFile( 
                                                        mainPath=filePath, 
                                                        fileName=fileName, 
                                                        extFilename=fileExt, 
                                                        newPath=newFilePath, 
                                                        project=prjId, 
                                                        newProject=newPrjId
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Move file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully moved" }

class TestsInstance(Handler):
    """
    Find tests in instance in all test plans or test globals
    """   
    def post(self):
        """
        Find tests in instance in all test plans or test globals
        Send POST request (uri /rest/tests/file/instance) with the following body JSON 
        { [ "project-id": <integer>] [, "project-name": <string>] , "file-path": "/" }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            filePath = self.request.data.get("file-path")
            if  not filePath: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: 
            prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        else:
            projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success, tests = RepoTests.instance().findInstance( filePath=filePath, projectName=projectName, projectId=prjId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to find tests instance")

        return { "cmd": self.request.path, "tests-instance": tests }
        
class TestsDirectoryAdd(Handler):
    """
    Add directory in test storage
    """   
    def post(self):
        """
        Add directory in test storage
        Send POST request (uri /rest/tests/directory/add) with the following body JSON 
            { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/", "directory-name": "test" }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            folderName = self.request.data.get("directory-name")
            if not folderName: raise EmptyValue("Please specify a source folder name")
            
            folderPath = self.request.data.get("directory-path")
            if not folderPath: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoTests.instance().addDir(pathFolder=folderPath, folderName=folderName, project=prjId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add directory")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully added" }
        
class TestsDirectoryRename(Handler):
    """
    Rename directory name in test storage
    """   
    def post(self):
        """
        Rename directory name in test storage
        Send POST request (uri /rest/tests/directory/rename) with the following body JSON 
            { 
                "source":      { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/", "directory-name": "test" },
                "destination":  { "directory-name": "test" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
		
        projectId = None
        projectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            folderName = self.request.data.get("source")["directory-name"]
            if not folderName: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if not folderPath: raise EmptyValue("Please specify a source folder path")
            
            newFolderName = self.request.data.get("destination")["directory-name"]
            if not newFolderName: raise EmptyValue("Please specify a destination folder name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoTests.instance().renameDir(mainPath=folderPath, oldPath=folderName, 
                                                newPath=newFolderName, project=prjId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to rename directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully renamed" }
        
class TestsDirectoryDuplicate(Handler):
    """
    Duplicate directory in test storage
    """   
    def post(self):
        """
        Duplicate directory in test storage
        Send POST request (uri /rest/tests/directory/duplicate) with the following body JSON 
            { 
                "source":      { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/", "directory-name": "test" },
                "destination":  { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/", "directory-name": "test" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        
        # checking json request on post
        projectId = None
        projectName = None
        newProjectId = None
        newProjectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            folderName = self.request.data.get("source")["directory-name"]
            if not folderName: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if not folderPath: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if "project-id" in destination: newProjectId = destination["project-id"]
            if "project-name" in destination: newProjectName = destination["project-name"]
            if not newProjectId and not newProjectName: raise EmptyValue("Please specify a project name or a project id")
            
            newFolderName = self.request.data.get("destination")["directory-name"]
            if not newFolderName: raise EmptyValue("Please specify a destination folder name")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if not newFolderPath: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
        # checking input    
        if newProjectId is not None:
            if not isinstance(newProjectId, int):
                raise HTTP_400("Bad new project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # get the project id according to the name and checking authorization
        newPrjId = projectId
        if newProjectName: newPrjId = ProjectsManager.instance().getProjectID(name=newProjectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=newPrjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        # all ok, do the duplication
        success = RepoTests.instance().duplicateDir(
                                                    mainPath=folderPath, oldPath=folderName, 
                                                    newPath=newFolderName, project=prjId, 
                                                    newProject=newPrjId, 
                                                    newMainPath=newFolderPath
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to duplicate directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully duplicated" }
        
class TestsDirectoryMove(Handler):
    """
    Move directory in test storage
    """   
    def post(self):
        """
        Move directory in test storage
        Send POST request (uri /rest/tests/directory/move) with the following body JSON 
            { 
                "source":      { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/", "directory-name": "test" },
                "destination":  { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/" }
            }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        
        # checking json request on post
        projectId = None
        projectName = None
        newProjectId = None
        newProjectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            folderName = self.request.data.get("source")["directory-name"]
            if not folderName: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if not folderPath: raise EmptyValue("Please specify a source folder path")

            destination = self.request.data.get("destination")
            if "project-id" in destination: newProjectId = destination["project-id"]
            if "project-name" in destination: newProjectName = destination["project-name"]
            if not newProjectId and not newProjectName: raise EmptyValue("Please specify a project name or a project id")
            
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if not newFolderPath: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
        # checking input    
        if newProjectId is not None:
            if not isinstance(newProjectId, int):
                raise HTTP_400("Bad new project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # get the project id according to the name and checking authorization
        newPrjId = projectId
        if newProjectName: newPrjId = ProjectsManager.instance().getProjectID(name=newProjectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=newPrjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        # all ok, do the duplication
        success = RepoTests.instance().moveDir(
                                                    mainPath=projectName, 
                                                    folderName=folderName, 
                                                    newPath=newFolderPath, 
                                                    project=prjId, 
                                                    newProject=newPrjId
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to move directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully moved" }
        
class TestsDirectoryRemove(Handler):
    """
    Remove directory in test storage and their contents recursively
    """   
    def post(self):
        """
        Remove directory in test storage and their contents recursively
        Send POST request (uri /rest/tests/directory/remove) with the following body JSON 
        { 
            "source":      { [ "project-id": <integer>] [, "project-name": <string>], "directory-path": "/test"},
            "recursive": True
        }
        Parameter "recursive" is optional in json body.
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
		
        projectId = None
        projectName = None
        try:
            source = self.request.data.get("source")
            if "project-id" in source: projectId = source["project-id"]
            if "project-name" in source: projectName = source["project-name"]
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            folderPath = self.request.data.get("source")["directory-path"]
            if not folderPath: raise EmptyValue("Please specify a source folder path")
            _recursive = self.request.data.get("recursive")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        if _recursive is None:
            recursive = False
        else:
            recursive = _recursive

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        if recursive:
            success = RepoTests.instance().delDirAll(folderPath, prjId)  
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500("Unable to remove directory")
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_500("Unable to remove directory (missing)")
            if success == Context.instance().CODE_FORBIDDEN:
                raise HTTP_403("Removing directory denied")
        else:
            success = RepoTests.instance().delDir(folderPath, prjId)  
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500("Unable to remove directory")
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_500("Unable to remove directory (missing)")
            if success == Context.instance().CODE_FORBIDDEN:
                raise HTTP_403("Cannot remove directory")
                
        return { "cmd": self.request.path, "message": "directory successfully removed" }

"""
Variables handlers
"""
class VariablesAdd(Handler):
    """
    /rest/variables/add/
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Add test variable in project, variables can be accessible from test
        description: ''
        operationId: addVariable
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [variable-name,variable-value]
              properties:
                variable-name:
                  type: string
                variable-value:
                  type: string
                  description: in json format
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: variable successfully added
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                variable-id:
                  type: string
            examples:
              application/json: |
                {
                  "message": "variable successfully added",
                  "cmd": "/variables/add",
                  "variable-id": "95"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project | Variable already exists
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            variableName = self.request.data.get("variable-name")
            if not variableName: raise EmptyValue("Please specify the name of the variable")
            
            variableJson = self.request.data.get("variable-value")
            if not variableJson: raise EmptyValue("Please specify the value of the variable")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # dumps the json
        try:
            variableValue = json.dumps(variableJson)
        except Exception :
            raise HTTP_400("Bad json provided in value")
         
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().addVariableInDB(projectId=prjId, variableName=variableName,
                                                                variableValue=variableValue)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALREADY_EXISTS:
            raise HTTP_403(details)
            
        return { "cmd": self.request.path, "message": "variable successfully added", "variable-id": details }
        
class VariablesDuplicate(Handler):
    """
    /rest/variables/duplicate
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Duplicate test variable in project
        description: ''
        operationId: duplicateVariable
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [variable-id]
              properties:
                variable-id:
                  type: string
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: variable successfully duplicated
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                variable-id:
                  type: string
            examples:
              application/json: |
                {
                  "message": "variable successfully duplicated",
                  "cmd": "/variables/duplicate",
                  "variable-id": "95"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project
          '404':
            description: Variable not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            variableId = self.request.data.get("variable-id")
            if not variableId: raise EmptyValue("Please specify a variable id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().duplicateVariableInDB(variableId=variableId, projectId=prjId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "variable successfully duplicated", "variable-id": details }
        
class VariablesUpdate(Handler):
    """
    /rest/variables/update
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Update test variable in project
        description: ''
        operationId: updateVariable
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [variable-id]
              properties:
                variable-id:
                  type: string
                variable-name:
                  type: string
                variable-value:
                  type: string
                  description: with json format
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: variable successfully updated
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "variable successfully updated",
                  "cmd": "/variables/update"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project
          '404':
            description: Variable not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            variableId = self.request.data.get("variable-id")
            if not variableId : raise HTTP_400("Please specify a variable id")

            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            variableName = self.request.data.get("variable-name")
            variableJson = self.request.data.get("variable-value")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # dumps the json
        try:
            variableValue = json.dumps(variableJson)
        except Exception :
            raise HTTP_400("Bad json provided in value")
        
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)  
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().updateVariableInDB(variableId=variableId, variableName=variableName, 
                                                                    variableValue=variableValue, projectId=prjId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "variable successfully updated" }
        
class VariablesReset(Handler):
    """
    /rest/variables/reset
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Reset all test variables according to the project
        description: ''
        operationId: resetVariables
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              properties:
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: variables successfully reseted
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "variables successfully reseted",
                  "cmd": "/variables/reset"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)  
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().delVariablesInDB(projectId=prjId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "variables successfully reseted" }
        
class VariablesRemove(Handler):
    """
    /rest/variables/remove
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Remove test variable in project
        description: ''
        operationId: removeVariable
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [variable-id]
              properties:
                variable-id:
                  type: string
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: variable successfully removed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "variable successfully removed",
                  "cmd": "/variables/remove"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project
          '404':
            description: Variable not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            variableId = self.request.data.get("variable-id")
            if not variableId : raise HTTP_400("Please specify a variable id")
            
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)  
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().delVariableInDB(variableId=variableId, projectId=prjId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "variable successfully removed" }
        
class VariablesListing(Handler):
    """
    /rest/variables/listing
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Get a listing of all test variables according to the project id or name
        description: ''
        operationId: listingVariables
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              properties:
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: variables listing
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                variables:
                  type: array
                  description: variables list in json format
                  items:
                    type: object
                    required: [ project-id, id, name, value ]
                    properties:
                      project-id:
                        type: integer
                      id:
                        type: integer
                      name:
                        type: string
                      value:
                        type: string
            examples:
              application/json: |
                {
                  "variables": [ 
                                 { 
                                  "project_id": 1, 
                                  "id": 1, 
                                  "value": false, 
                                  "name": "DEBUG"
                                 } 
                              ],
                  "cmd": "/variables/listing"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)  
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            

        success, details = RepoTests.instance().getVariablesFromDB(projectId=prjId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        
        # new in v17 convert as json the result 
        for d in details:
            d['value'] = json.loads( d['value'] )        
        # end of new
        
        return { "cmd": self.request.path, "message": "listing result", "variables": details }

class VariablesSearch(Handler):
    """
    /rest/variables/search
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Search a variable according to the name or id
        description: ''
        operationId: searchVariable
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              properties:
                project-id:
                  type: integer
                project-name:
                  type: string
                variable-name:
                  type: string
                variable-id:
                  type: string
        responses:
          '200':
            description: search result
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                variable:
                  description: variable in json format in only one match
                  type: object
                  required: [ project-id, id, name, value ]
                  properties:
                    project-id:
                      type: integer
                    id:
                      type: integer
                    name:
                      type: string
                    value:
                      type: string
                variables:
                  type: array
                  description: variables list in json format on several occurences
                  items:
                    type: object
                    required: [ project-id, id, name, value ]
                    properties:
                      project-id:
                        type: integer
                      id:
                        type: integer
                      name:
                        type: string
                      value:
                        type: string
            examples:
              application/json: |
                {
                  "variable": {
                                "project_id": 1, 
                                "id": 95, 
                                "value": "1.0", 
                                "name": "VAR_AUTO"
                              },
                  "cmd": "/variables/search"
                }
          '400':
            description: Bad request provided | Bad project id provided | Bad json provided in value
          '403':
            description: Access denied to this project
          '404':
            description: Variable not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            variableName = self.request.data.get("variable-name")
            variableId = self.request.data.get("variable-id")
            
            if variableName is None and variableId is None: raise EmptyValue("Please specify the name/id of the variable")
            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)  
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().getVariableFromDB(projectId=prjId, variableName=variableName, variableId=variableId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_404("Variable not found")

        
        if len(details) == 1:
            # new in v17, convert as json the value
            details[0]['value'] = json.loads( details[0]['value'] )
            # end of new
            return { "cmd": self.request.path, "variable": details[0] }
        else:
            # new in v17 convert value as json
            for d in details:
                d['value'] = json.loads( d['value'] )
            # end of new
            
            return { "cmd": self.request.path, "message": "search result", "variables": details }
            
"""
Tests Results handlers
"""   
class ResultsListing(Handler):
    """
    Get the listing of all tests results. Support filtering by date and running time.
    Use this function to get the testid.
    """   
    def post(self):
        """
        Get the listing of all tests results with testid. 
        Send POST request (uri /rest/results/listing) with the following body JSON 
        { ["project-id": <integer>] [, "project-name": <string>] }
        Cookie session_id is mandatory.

        Optionals parameters:
        
        > Filter results by date, returns only results greater than the date provided
            "date": "YYYY-MM-DD"
            
        > Filter results by time, returns only results greater than the time provided
            "time": "HH:MM:SS" 
            
        @return: testsresults listing
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            dateFilter = self.request.data.get("date")
            timeFilter = self.request.data.get("time")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        listing = RepoArchives.instance().getBasicListing(projectId=prjId, 
                                                        dateFilter=dateFilter, 
                                                        timeFilter=timeFilter)  
        
        return { "cmd": self.request.path, "testsresults-listing": listing, 'project-id': prjId }
        
class ResultsDownloadResume(Handler):
    """
    Download the resume of the test result
    """    
    def post(self):
        """
        Download the resume of the test result
        Send POST request (uri /rest/results/events/resume) with the following body JSON 
        { ["project-id": <integer>] [, "project-name": <string>] , "test-id":"xxxxx" }
        Cookie session_id is mandatory.

        @return: test resume
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            testId = self.request.data.get("test-id")
            if not testId: raise EmptyValue("Please specify a test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('test not found')
            
        success, resume = RepoArchives.instance().getTrResume(trPath=testPath)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Test resume not found")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to prepare test resume")
            
        return { "cmd": self.request.path, 'test-id': testId, 'project-id': prjId, 'test-resume': resume }

class ResultsDownloadEvents(Handler):
    """
    Download all events of the test result
    """    
    def post(self):
        """
        Download all events of the test result
        Send POST request (uri /rest/results/events/download) with the following body JSON 
        { ["project-id": <integer>] [, "project-name": <string>], "test-id":"xxxxx" }
        Cookie session_id is mandatory.

        @return: test report
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            testId = self.request.data.get("test-id")
            if not testId: raise EmptyValue("Please specify a test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('test not found')
            
        success, events = RepoArchives.instance().getTrEvents(trPath=testPath)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Test events not found")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to download test events")
            
        return { "cmd": self.request.path, 'test-id': testId, 'project-id': prjId, 'test-events': events }

class ResultsDownloadLogs(Handler):
    """
    Download logs of the test result
    """    
    def post(self):
        """
        Download logs of the test result
        Send POST request (uri /rest/results/logs/download) with the following body JSON 
        { ["project-id": <integer>] [, "project-name": <string>], "test-id":"xxxxx" }
        Cookie session_id is mandatory.

        @return: test report
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            testId = self.request.data.get("test-id")
            if not testId: raise EmptyValue("Please specify a project id and test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('test not found')
            
        success, logs = RepoArchives.instance().getTrLogs(trPath=testPath)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Test logs not found")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to download test logs")
            
        return { "cmd": self.request.path, 'test-id': testId, 'project-id': prjId, 'test-logs': logs }

class ResultsReset(Handler):
    """
    Remove all test results
    """   
    def post(self):
        """
        Remove all test results
        Send POST request (uri /rest/results/reset) with the following body JSON 
        { ["project-id": <integer>] [, "project-name": <string>] }
        Cookie session_id is mandatory.

        @return: testsresults listing
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
                    
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        success = RepoArchives.instance().emptyRepo(projectId=prjId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to reset test results")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Reset results forbidden")
            
        return { "cmd": self.request.path, "message": "results successfully reseted", 'project-id': prjId }
        
class ResultsRemove(Handler):
    """
    Remove test result
    """   
    def post(self):
        """
        Remove test result
        Send POST request (uri /rest/results/remove) with the following body JSON 
        { ["project-id": <integer>] [, "project-name": <string>] , "test-id":"xxxxx" }
        Cookie session_id is mandatory.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
            
            testId = self.request.data.get("test-id")
            if not testId: raise HTTP_400("Please specify a test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
                    
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('test not found')
            
        success = RepoArchives.instance().delDirAll(pathFolder=testPath, project='')  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove test result")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove test result (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Cannot remove test result")
            
        return { "cmd": self.request.path, "message": "test result successfully removed", 'project-id': prjId }

class ResultsFollow(Handler):
    """
    Follow the result of one or severals results
    """    
    def post(self):
        """
        Follow the result of one or severals results
        Send POST request (uri /rest/results/follow) with the following body JSON 
        { "test-ids": ["xxxxx"] [, "project-id": <integer>] [, "project-name": <string>] }
        Cookie session_id is mandatory.
        
        @return: test status
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            testIds = self.request.data.get("test-ids")
            if not testIds: raise HTTP_400("Please specify a project id and a list of test id")
                
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        results = []
        for testId in testIds:
            result = { "id": testId }
            founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
            if founded == Context.instance().CODE_NOT_FOUND: raise HTTP_404('test not found')

            state = RepoArchives.instance().getTrState(trPath=testPath)
            verdict = RepoArchives.instance().getTrResult(trPath=testPath)
            progress = RepoArchives.instance().getTrProgress(trPath=testPath)
            result["result"] = { "state": state, "verdict": verdict, "progress": progress['percent'] }

            description = RepoArchives.instance().getTrDescription(trPath=testPath)
            result.update(description)
            
            results.append(result)
        return { "cmd": self.request.path, "results": results, 'project-id': prjId}
    
class ResultsStatus(Handler):
    """
    /rest/results/status
    """   
    @_to_yaml    
    def post(self):
        """
        tags:
          - results
        summary: Get the status of the test (not-running, running, complete).
        description: ''
        operationId: statusResult
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ test-id ]
              properties:
                test-id:
                  type: string
                project-name:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: result status of a test
            schema :
              properties:
                cmd:
                  type: string
                test-status:
                  type: string
                  description: running/not-running/complete
                test-progress:
                  type: integer
                  description: progress in percent
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/status", 
                  "test-status": "running", 
                  "test-id": "af0b2587-459e-42eb-a4da-e3e6fa227719",
                  "test-progress": 25
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            testId = self.request.data.get("test-id")
            if not testId: raise HTTP_400("Please specify a list of test id")
                
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
            
        state = RepoArchives.instance().getTrState(trPath=testPath)
        progress = RepoArchives.instance().getTrProgress(trPath=testPath)
        return { "cmd": self.request.path, 'test-id': testId, 'test-status': state, 'test-progress': progress['percent'] }
    
class ResultsVerdict(Handler):
    """
    /rest/results/verdict
    """
    @_to_yaml      
    def post(self):
        """
        tags:
          - results
        summary: Get the result of the test (undefined, pass, fail).
        description: ''
        operationId: verdictResult
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ test-id ]
              properties:
                test-id:
                  type: string
                project-name:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: tests verdict
            schema :
              properties:
                cmd:
                  type: string
                test-verdict:
                  type: string
                  description: undefined, pass, fail
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/verdict", 
                  "test-verdict": "undefined",
                  "test-id": "af0b2587-459e-42eb-a4da-e3e6fa227719"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            testId = self.request.data.get("test-id")
            if not testId: raise HTTP_400("Please specify a list of test id")
                
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
            
        verdict = RepoArchives.instance().getTrResult(trPath=testPath)
        return { "cmd": self.request.path, 'test-id': testId, 'test-verdict': verdict }
        
class ResultsBasicHtmlReport(Handler):
    """
    /rest/results/report/basic/html
    """
    def post(self):
        """
        tags:
          - reports
        summary: Get the basic report of the test (html format).
        description: ''
        operationId: basicHtmlReport
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ test-id ]
              properties:
                test-id:
                  type: string
                project-name:
                  type: string
                project-id:
                  type: string
                replay-id:
                  type: string
        responses:
          '200':
            description: basic test report
            schema :
              properties:
                cmd:
                  type: string
                test-report:
                  type: string
                  description: in base64 and gzipped
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/report/basic/html", 
                   "test-report": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                   "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result not found
          '500':
            description: Server error 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            testId = self.request.data.get("test-id")
            if not testId: raise HTTP_400("Please specify a list of test id")
                
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: 
                raise EmptyValue("Please specify a project name or a project id")
                
            replayId = self.request.data.get("replay-id")    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], 
                                                                                  projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
            
        success, report = RepoArchives.instance().getTrBasicReport(trPath=testPath, replayId=replayId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Basic test report not found")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to download basic html report")
            
        return { "cmd": self.request.path, 'test-id': testId, 'test-report': report }

class ResultsHtmlReport(Handler):
    """
    /rest/results/report/html
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get the full or basic report of the test (html format).
        description: ''
        operationId: htmlReport
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ test-id ]
              properties:
                test-id:
                  type: string
                project-name:
                  type: string
                project-id:
                  type: string
                basic:
                  type: boolean
        responses:
          '200':
            description: full html test report
            schema :
              properties:
                cmd:
                  type: string
                test-report:
                  type: string
                  description: in base64 and gzipped
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/report/html", 
                   "test-report": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                   "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            testId = self.request.data.get("test-id")
            if not testId: raise HTTP_400("Please specify a list of test id")
                
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

            _basic = self.request.data.get("basic")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        if _basic is None:
            basicReport = False
        else:
            basicReport = _basic
            
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
           
        if basicReport:
            success, report = RepoArchives.instance().getTrBasicReport(trPath=testPath)
        else:
            success, report = RepoArchives.instance().getTrReport(trPath=testPath)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Test events not found")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to download html report")
            
        return { "cmd": self.request.path, 'test-id': testId, 'test-report': report }

class ResultsCsvReport(Handler):
    """
    /rest/results/report/csv
    """
    @_to_yaml      
    def post(self):
        """
        tags:
          - reports
        summary: Get the report of the test (csv format).
        description: ''
        operationId: csvReport
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: Cookie
            in: header
            description: session_id=NjQyOTVmOWNlMDgyNGQ2MjlkNzAzNDdjNTQ3ODU5MmU5M 
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              required: [ test-id ]
              properties:
                test-id:
                  type: string
                project-name:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: full csv test report
            schema :
              properties:
                cmd:
                  type: string
                test-report:
                  type: string
                  description: in base64 and gzipped
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/report/csv", 
                   "test-report": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                   "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        try:
            testId = self.request.data.get("test-id")
            if not testId: raise HTTP_400("Please specify a list of test id") 
                
            projectId = self.request.data.get("project-id")
            projectName = self.request.data.get("project-name")
            if not projectId and not projectName: raise EmptyValue("Please specify a project name or a project id")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if projectId is not None:
            if not isinstance(projectId, int):
                raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        prjId = projectId
        if projectName: prjId = ProjectsManager.instance().getProjectID(name=projectName)   
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], projectId=prjId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=prjId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
            
        success, report = RepoArchives.instance().getTrReportCsv(trPath=testPath)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Test events not found")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to download csv report")
            
        return { "cmd": self.request.path, 'test-id': testId, 'test-report': report }

"""
Metriscs handlers
"""
class MetricsScriptsStatistics(Handler):
    """
    Get statistics for scripts
    """   
    def post(self):
        """
        Get statistics for scripts
        Send POST request (uri /rest/metrics/scripts/statistics) with the following body JSON 
        { "user-id": <integer>}
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
            
"""
Agents handlers
"""
class AgentsRunning(Handler):
    """
    Get all running agents
    """   
    def get(self):
        """
        Get all running agents
        Send GET request (uri /rest/agents/running)
        Cookie session_id is mandatory.

        @return: list of running agents
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        running = AgentsManager.instance().getRunning()
        return { "cmd": self.request.path, "agents-running": running }
        
class AgentsDisconnect(Handler):
    """
    Disconnect a agent by the name
    """   
    def post(self):
        """
        Disconnect a agent by the name
        Send POST request (uri /rest/agents/disconnect) with the following body JSON 
        { "agent-name"}
        Cookie session_id is mandatory. 
        
        Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            agentName = self.request.data.get("agent-name")
            if not agentName : raise HTTP_400("Please specify a agent name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = AgentsManager.instance().disconnectAgent(name=agentName)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("agent not found")
            
        return { "cmd": self.request.path, "message": "agent successfully disconnected" } 
  
"""
Probes handlers
"""
class ProbesRunning(Handler):
    """
    Get all running probes
    """   
    def get(self):
        """
        Get all running probes
        Send GET request (uri /rest/probes/running)
        Cookie session_id is mandatory.

        @return: list of running probes
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        running = ProbesManager.instance().getRunning()
        return { "cmd": self.request.path, "probes-running": running }
        
class ProbesDisconnect(Handler):
    """
    Disconnect a probe
    """   
    def post(self):
        """
        Disconnect a probe
        Send POST request (uri /rest/probes/disconnect) with the following body JSON 
        { "probe-name": <string> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            probeName = self.request.data.get("probe-name")
            if not probeName : raise HTTP_400("Please specify a probe name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = ProbesManager.instance().disconnectProbe(name=probeName)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("probe not found")
            
        return { "cmd": self.request.path, "message": "probe successfully disconnected" } 
  
"""
Release notes handlers
"""
class AboutChangesCore(Handler):
    """
    Get the release notes of the product
    """   
    def get(self):
        """
        Get the release notes of the product
        Send GET request (uri /rest/releasenotes/core)
        Cookie session_id is mandatory.

        @return: release notes
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        rn = Context.instance().getRn(pathRn=Settings.getDirExec(), b64=False) 
        return { "cmd": self.request.path, "releasenotes-core": rn }
        
class AboutChangesAdapters(Handler):
    """
    Get the release notes of the adapters
    """   
    def get(self):
        """
        Get the release notes of the adapters
        Send GET request (uri /rest/releasenotes/adapters)
        Cookie session_id is mandatory.

        @return: release notes
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        rn = RepoAdapters.instance().getRn(b64=False)
        return { "cmd": self.request.path, "releasenotes-adapters": rn }
        
class AboutChangesLibraries(Handler):
    """
    Get the release notes of the libraries
    """   
    def get(self):
        """
        Get the release notes of the libraries
        Send GET request (uri /rest/releasenotes/libraries)
        Cookie session_id is mandatory.

        @return: release notes
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        rn = RepoLibraries.instance().getRn(b64=False)
        return { "cmd": self.request.path, "releasenotes-libraries": rn }
        
class AboutChangesToolbox(Handler):
    """
    Get the release notes of the toolbox
    """   
    def get(self):
        """
        Get the release notes of the toolbox
        Send GET request (uri /rest/releasenotes/toolbox)
        Cookie session_id is mandatory.

        @return: release notes
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        rn = ToolboxManager.instance().getRn(b64=False)
        return { "cmd": self.request.path, "releasenotes-toolbox": rn }

"""
System handlers
"""
class SystemVersions(Handler):
    """
    Get information about versions
    """   
    def get(self):
        """
        Get information about versions
        Send GET request (uri /rest/system/versions)
        Cookie session_id is mandatory.

        @return: version of python, php, etc..
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        versions = {}
        versions["core"] = Settings.getVersion()
        versions["python"] = platform.python_version()
        versions["php"] = Context.instance().phpVersion
        versions["database"] = Context.instance().mysqlVersion
        versions["web"] = Context.instance().apacheVersion
        
        return { "cmd": self.request.path, "versions": versions }
        
class SystemNetworking(Handler):
    """
    Get information about the network
    """   
    def get(self):
        """
        Get information about the network
        Send GET request (uri /rest/system/networking)
        Cookie session_id is mandatory.

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        networking = Context.instance().networkInterfaces
        return { "cmd": self.request.path, "networking": networking }
        
class SystemStatus(Handler):
    """
    Get information about the status of the server
    """   
    def get(self):
        """
        Get information about the status of the server
        Send GET request (uri /rest/system/status)
        Cookie session_id is mandatory.

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        status = {}
        status["start-at"] = Context.instance().startedAt
        status["current-date"] = Context.instance().getServerDateTime()
        status["uptime"] = Context.instance().getUptime()
        
        return { "cmd": self.request.path, "status": status }

class SystemUsages(Handler):
    """
    Get usages of the server
    """   
    def get(self):
        """
        Get usages of the server
        Send GET request (uri /rest/system/usages)
        Cookie session_id is mandatory.

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
        
        usages = {}
        usages["disk"] = Context.instance().getUsage()
        
        return { "cmd": self.request.path, "usages": usages }


"""
Administration handlers
"""
class AdminConfigListing(Handler):
    """
    Get listing of the configuration
    """   
    def get(self):
        """
        Get listing of the configuration
        Send GET request (uri /rest/administration/configuration/listing)
        Cookie session_id is mandatory. only available for administrator

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        config = {}
        for section in Settings.instance().sections():
            for (name,value) in Settings.instance().items(section):
                config["%s-%s" % ( section.lower(), name.lower() )] = value
                
        return { "cmd": self.request.path, "configuration": config }  

class AdminConfigReload(Handler):
    """
    Reload the configuration of the server
    """   
    def get(self):
        """
        Reload the configuration of the server
        Send GET request (uri /rest/administration/configuration/reload)
        Cookie session_id is mandatory. only available for administrator

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
        
        CliFunctions.instance().reload()

        return { "cmd": self.request.path, "status": "reloaded" }  
        
class AdminClientsDeploy(Handler):
    """
    Deploy clients
    """   
    def get(self):
        """
        Deploy clients
        Send GET request (uri /rest/administration/clients/deploy)
        Cookie session_id is mandatory. only available for administrator

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
        
        CliFunctions.instance().deployclients()
        CliFunctions.instance().deployclients(portable=True)
        
        return { "cmd": self.request.path, "status": "deployed" }  

class AdminToolsDeploy(Handler):
    """
    Deploy toolboxes
    """   
    def get(self):
        """
        Deploy toolboxes
        Send GET request (uri /rest/administration/tools/deploy)
        Cookie session_id is mandatory. only available for administrator

        @return: version
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
        
        CliFunctions.instance().deploytools()
        CliFunctions.instance().deploytools(portable=True)
        
        return { "cmd": self.request.path, "status": "deployed" }  

class AdminProjectsListing(Handler):
    """
    Listing projects
    """   
    def get(self):
        """
        List all projects with get request (uri /rest/projects/listing)
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']:
            raise HTTP_401("Access refused")
            
        success, details = ProjectsManager.instance().getProjectsFromDB()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "projects": details }
        
class AdminProjectsStatistics(Handler):
    """
    Get projects statistics
    """   
    def get(self):
        """
        Get projects statistics with GET request (uri /rest/projects/statistics).
        Cookie session_id is mandatory.
        
        @return: statistics or error
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        success, details = ProjectsManager.instance().getStatisticsFromDb()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "projects-statistics": details }
        
class AdminProjectsAdd(Handler):
    """
    Add project
    """   
    def post(self):
        """
        Add project
        Send POST request (uri /rest/projects/add) with the following body JSON 
        { "project-name": <string> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            projectName = self.request.data.get("project-name")
            if not projectName : raise HTTP_400("Please specify a project name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        success, details = ProjectsManager.instance().addProjectToDB(projectName=projectName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_400(details)
            
        return { "cmd": self.request.path, "message": "project successfully added", "project-id": details }

class AdminProjectsRename(Handler):
    """
    Rename project
    """   
    def post(self):
        """
        Rename
        Update project 
        Send POST request (uri /rest/projects/rename) with the following body JSON 
        { "project-id": <integer>, "project-name": <string> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']:
            raise HTTP_401("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if not projectId : raise HTTP_400("Please specify a project id")
            
            projectName = self.request.data.get("project-name")
            if not projectName : raise HTTP_400("Please specify a project name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, details = ProjectsManager.instance().updateProjectFromDB(projectName=projectName, projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_400(details)
            
        return { "cmd": self.request.path, "message": "project successfully updated" }

class AdminProjectsRemove(Handler):
    """
    Remove project
    """   
    def post(self):
        """
        Remove project
        Send POST request (uri /rest/projects/remove) with the following body JSON 
        { "project-id": <integer> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            projectId = self.request.data.get("project-id")
            if not projectId : raise HTTP_400("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, details = ProjectsManager.instance().delProjectFromDB(projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "project successfully removed" } 
        
class AdminProjectsSearch(Handler):
    """
    Search a project according to the name or id
    """   
    def post(self):
        """
        Search a project according to the name or id
        Send POST request (uri /rest/projects/search) with the following body JSON 
        { ["project-name": <string>], ["project-id": <integer>] }
        
        @return: user(s) found
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
        
        try:
            projectName = self.request.data.get("project-name")
            projectId = self.request.data.get("project-id")
            
            if projectName is None and projectId is None: raise EmptyValue("Please specify the name/id of the project")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, details = ProjectsManager.instance().getProjectFromDB(projectName=projectName, projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_500("no project found")
        
        if len(details) == 1:
            return { "cmd": self.request.path, "project": details[0] }
        else:
            return { "cmd": self.request.path, "projects": details }

class AdminUsersProfile(Handler):
    """
    Get user profile
    """   
    def post(self):
        """
        Remove user
        Send POST request (uri /rest/users/profile) with the following body JSON 
        { "user-id": <integer> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)

        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if int(userId) != int(user_profile["id"]) and not user_profile['administrator']:
            raise HTTP_401("Access refused")
        else:
            success, details = UsersManager.instance().getUserFromDB(userId=userId)
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_404(details)
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500(details)
                
        return { "cmd": self.request.path, "user": details } 

class AdminUsersListing(Handler):
    """
    Get all users
    """   
    def get(self):
        """
        Get all users with GET request (uri /rest/users/listing).
        Cookie session_id is mandatory.
        
        @return: list of users or error
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']:
            raise HTTP_401("Access refused")
            
        success, details = UsersManager.instance().getUsersFromDB()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "users": details }
        
class AdminUsersStatistics(Handler):
    """
    Get users statistics
    """   
    def get(self):
        """
        Get users statistics with GET request (uri /rest/users/statistics).
        Cookie session_id is mandatory.
        
        @return: statistics or error
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        success, details = UsersManager.instance().getStatisticsFromDb()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "users-statistics": details }
        
class AdminUsersAdd(Handler):
    """
    Add project
    """   
    def post(self):
        """
        Add users
        Send POST request (uri /rest/users/add) with the following body JSON 
        { "login": <string>, "password": <sha1>, "email": <string> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message with user id
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            login = self.request.data.get("login")
            if not login: raise EmptyValue("Please specify a login")
            
            password = self.request.data.get("password")
            if not password: raise EmptyValue("Please specify a password")
            
            email = self.request.data.get("email")
            if not email: raise EmptyValue("Please specify a email")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        success, details = UsersManager.instance().addUserToDB(login=login, password=password, email=email)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALREADY_EXISTS:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "user successfully added", "user-id": details }

class AdminUsersUpdate(Handler):
    """
    Update user
    """   
    def post(self):
        """
        Update user 
        Send POST request (uri /rest/users/update) with the following body JSON 
        { "user-id": <integer>, ["email": <string>] }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']:
            raise HTTP_401("Access refused")

        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")

            email = self.request.data.get("email")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, details = UsersManager.instance().updateUserInDB(userId=userId, email=email)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "user successfully updated" }

class AdminUsersRemove(Handler):
    """
    Remove user
    """   
    def post(self):
        """
        Remove user
        Send POST request (uri /rest/users/remove) with the following body JSON 
        { "user-id": <integer> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # him self deletion deny
        if int(userId) == int(user_profile["id"]):
            raise HTTP_403("deletion not authorized")
            
        success, details = UsersManager.instance().delUserInDB(userId=userId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "user successfully removed" } 

class AdminUsersStatus(Handler):
    """
    Enable or disable a user account
    """   
    def post(self):
        """
        Enable or disable a user account
        Send POST request (uri /rest/users/status) with the following body JSON 
        { "user-id": <integer>, "enabled": True }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")
            
            enabled = self.request.data.get("enabled")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # update 
        success, details = UsersManager.instance().updateStatusUserInDB(userId=userId, status=enabled)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        
        if enabled:
            return { "cmd": self.request.path, "message": "user successfully enabled" }
        else:
            return { "cmd": self.request.path, "message": "user successfully disabled" } 
        
class AdminUsersDisconnect(Handler):
    """
    Disconnect a user
    """   
    def post(self):
        """
        Disconnect a user 
        Send POST request (uri /rest/users/disconnect) with the following body JSON 
        { "login": <string> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            userLogin = self.request.data.get("login")
            if not userLogin : raise HTTP_400("Please specify a login")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = Context.instance().unregisterUserFromXmlrpc(login=userLogin)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("user not found")
            
        return { "cmd": self.request.path, "message": "user successfully disconnected" } 
  
class AdminUsersDuplicate(Handler):
    """
    Duplicate user
    """   
    def post(self):
        """
        Duplicate user
        Send POST request (uri /rest/users/duplicate) with the following body JSON 
        { "user-id": <integer> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, details = UsersManager.instance().duplicateUserInDB(userId=userId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "user successfully duplicated", "user-id": details  } 

class AdminUsersPasswordReset(Handler):
    """
    Reset the password of a user 
    """   
    def post(self):
        """
        Reset the password of a user 
        Send POST request (uri /rest/users/password/reset) with the following body JSON 
        { "user-id": <integer> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, details = UsersManager.instance().resetPwdUserInDB(userId=userId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "password successfully reseted" } 
        
class AdminUsersPasswordUpdate(Handler):
    """
    Update the password of a user 
    """   
    def post(self):
        """
        Update the password of a user 
        Send POST request (uri /rest/users/password/update) with the following body JSON 
        { "user-id": <integer>, "current-password": <sha1>, "new-password": <sha1> }
        Cookie session_id is mandatory. Available only for administrator.

        @return: success message
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
            
        try:
            userId = self.request.data.get("user-id")
            if not userId : raise HTTP_400("Please specify a user id")
            
            currentPwd = self.request.data.get("current-password")
            if not currentPwd : raise HTTP_400("Please specify the current password")
            
            newPwd = self.request.data.get("new-password")
            if not newPwd : raise HTTP_400("Please specify the new password")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        # check current password
        sha1 = sha1_constructor()
        sha1.update( "%s%s" % ( Settings.get( 'Misc', 'salt'), currentPwd )  )
        if sha1.hexdigest() != user_profile['password']:
            raise HTTP_403("bad current password provided")
        
        # update 
        success, details = UsersManager.instance().updatePwdUserInDB(userId=userId, newPwd=newPwd)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "message": "password successfully updated" } 

class AdminUsersSearch(Handler):
    """
    Search a user according to the name or id
    """   
    def post(self):
        """
        Search a user according to the name or id
        Send POST request (uri /rest/users/search) with the following body JSON 
        { ["user-login": <string>], ["user-id": <integer>] }
        
        @return: user(s) found
        @rtype: dict 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_401("Access refused")
           
        try:
            userLogin = self.request.data.get("user-login")
            userId = self.request.data.get("user-id")
            
            if userLogin is None and userId is None: raise EmptyValue("Please specify the name/id of the user")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, details = UsersManager.instance().getUserFromDB(userId=userId, userLogin=userLogin)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_500("no user found")
        
        if len(details) == 1:
            return { "cmd": self.request.path, "user": details[0] }
        else:
            return { "cmd": self.request.path, "users": details }
          
"""
Logger
"""
class _NoLoggingWSGIRequestHandler(WSGIRequestHandler, Logger.ClassLogger):
    """
    """
    def log_message(self, format, *args):
        """
        """
        self.trace( "RSI - %s %s %s" % args )
        
_my_logger = logging.Logger(__name__)
_my_logger.setLevel(logging.DEBUG)
_hnd = logging.StreamHandler(sys.stdout)
_my_logger.addHandler(_hnd)

"""
Webservices routing
"""
class _WebServices(WSGI):
    logger = _my_logger
    debug = False
    routes = [
        # session
        ('/session/login',                              SessionLogin()),
        ('/session/logout',                             SessionLogout()),
        ('/session/refresh',                            SessionRefresh()),
        
        # agents
        ('/agents/running',                             AgentsRunning()),
        ('/agents/disconnect',                          AgentsDisconnect()),
        
        # probes
        ('/probes/running',                             ProbesRunning()),
        ('/probes/disconnect',                          ProbesDisconnect()),
        
        # tasks
        ('/tasks/running',                              TasksRunning()),
        ('/tasks/waiting',                              TasksWaiting()),
        ('/tasks/history',                              TasksHistory()),
        ('/tasks/cancel',                               TasksCancel()),
        ('/tasks/reset',                                TasksReset()),
        # ('/tasks/update',                               TasksUpdate()),
        # ('/tasks/statistics', TasksUpdate()),
        
        # public storage
        ('/public/basic/listing',                       PublicListing()),
        ('/public/directory/add',                       PublicDirectoryAdd()),
        ('/public/directory/remove',                    PublicDirectoryRemove()),
        ('/public/directory/rename',                    PublicDirectoryRename()),
        ('/public/file/download',                       PublicDownload()),
        ('/public/file/import',                         PublicImport()),
        ('/public/file/remove',                         PublicRemove()),
        ('/public/file/rename',                         PublicRename()),
        
        # tests
        ('/tests/run',                                  TestsRun()),
        ('/tests/basic/listing',                        TestsListing()),
        ('/tests/statistics',                           TestsStatistics()),
        # ('/tests/statistics/reset',                     TestsStatistics()),
        ('/tests/directory/add',                        TestsDirectoryAdd()),
        ('/tests/directory/remove',                     TestsDirectoryRemove()),
        ('/tests/directory/rename',                     TestsDirectoryRename()),
        ('/tests/directory/duplicate',                  TestsDirectoryDuplicate()),
        ('/tests/directory/move',                       TestsDirectoryMove()),
        ('/tests/file/download',                        TestsDownload()),
        ('/tests/file/import',                          TestsImport()),
        ('/tests/file/remove',                          TestsRemove()),
        ('/tests/file/rename',                          TestsRename()),
        ('/tests/file/duplicate',                       TestsDuplicate()),
        ('/tests/file/move',                            TestsMove()),
        ('/tests/file/instance',                        TestsInstance()),
        # /tests/directory/statistics
        # /tests/file/statistics
        # /tests/file/unlock
        # /tests/file/update/project
        # /tests/file/update/adapters/version
        # /tests/file/update/libraries/version
        # /tests/snapshot/add
        # /tests/snapshot/remove
        # /tests/check

        # variables
        ('/variables/listing',                          VariablesListing()),
        ('/variables/add',                              VariablesAdd()),
        ('/variables/update',                           VariablesUpdate()),
        ('/variables/remove',                           VariablesRemove()),
        ('/variables/duplicate',                        VariablesDuplicate()),
        ('/variables/reset',                            VariablesReset()),
        ('/variables/search',                           VariablesSearch()),
        # /variables/export
        # /variables/import
        
        # tests results storage
        ('/results/reset',                              ResultsReset()),
        ('/results/listing',                            ResultsListing()),
        ('/results/remove',                             ResultsRemove()),
        ('/results/follow',                             ResultsFollow()),
        ('/results/status',                             ResultsStatus()),
        ('/results/verdict',                            ResultsVerdict()),
        ('/results/report/basic/html',                  ResultsBasicHtmlReport()),
        ('/results/report/html',                        ResultsHtmlReport()),
        ('/results/report/csv',                         ResultsCsvReport()),
        ('/results/events/download',                    ResultsDownloadEvents()),
        ('/results/events/resume',                      ResultsDownloadResume()),
        ('/results/logs/download',                      ResultsDownloadLogs()),
        
        # metrics for test 
        # /metrics/scripts/statistics 
        # /metrics/testsglobal/statistics 
        # /metrics/testsplan/statistics 
        # /metrics/testssuite/statistics 
        # /metrics/testsunit/statistics 
        # /metrics/testsabstract/statistics 
        # /metrics/testscase/statistics 
        # /metrics/reset
        
        # adapters
        ( '/adapters/statistics',                       AdaptersStatistics()),
        ( '/adapters/check/syntax',                     AdaptersCheckSyntax()),
        ( '/adapters/set/default',                      AdaptersSetDefault()),
        ( '/adapters/set/generic',                      AdaptersSetGeneric()),
        
        # libraries
        ( '/libraries/statistics',                      LibrariesStatistics()),
        ( '/libraries/check/syntax',                    LibrariesCheckSyntax()),
        ( '/libraries/set/default',                     LibrariesSetDefault()),
        ( '/libraries/set/generic',                     LibrariesSetGeneric()),
       
        # documentation
        ( '/documentations/listing',                    DocumentationsListing()),
        ( '/documentations/build',                      DocumentationsBuild()),
        
        # system
        ( '/system/versions',                           SystemVersions()),
        ( '/system/networking',                         SystemNetworking()),
        ( '/system/status',                             SystemStatus()),
        ( '/system/usages',                             SystemUsages()),
        
        # administration
        ( '/administration/configuration/listing',      AdminConfigListing()),
        ( '/administration/configuration/reload',       AdminConfigReload()),
        ( '/administration/clients/deploy',             AdminClientsDeploy()),
        ( '/administration/tools/deploy',               AdminToolsDeploy()),
        ( '/administration/users/profile',              AdminUsersProfile()),
        ( '/administration/users/listing',              AdminUsersListing()),
        ( '/administration/users/add',                  AdminUsersAdd()),
        ( '/administration/users/remove',               AdminUsersRemove()),
        ( '/administration/users/disconnect',           AdminUsersDisconnect()),
        ( '/administration/users/update',               AdminUsersUpdate()),
        ( '/administration/users/status',               AdminUsersStatus()),
        ( '/administration/users/duplicate',            AdminUsersDuplicate()),
        ( '/administration/users/password/reset',       AdminUsersPasswordReset()),
        ( '/administration/users/password/update',      AdminUsersPasswordUpdate()),
        ( '/administration/users/search',               AdminUsersSearch()),
        ( '/administration/users/statistics',           AdminUsersStatistics()),
        ( '/administration/projects/listing',           AdminProjectsListing()),
        ( '/administration/projects/add',               AdminProjectsAdd()),
        ( '/administration/projects/remove',            AdminProjectsRemove()),
        ( '/administration/projects/rename',            AdminProjectsRename()),
        ( '/administration/projects/search',            AdminProjectsSearch()),
        ( '/administration/projects/statistics',        AdminProjectsStatistics()),
        # /administration/logs/export
        # /administration/trace/level
        
        # client
        # /clients/available
        
        # toolbox
        # /tools/available
        
        # plugins
        # /plugins/available
        
        # about
        ('/about/changes/core',                         AboutChangesCore()),
        ('/about/changes/adapters',                     AboutChangesAdapters()),
        ('/about/changes/libraries',                    AboutChangesLibraries()),
        ('/about/changes/toolbox',                      AboutChangesToolbox()),
    ]

class _RestServerInterface(Logger.ClassLogger, threading.Thread):
    def __init__(self, listeningAddress):
        """
        Constructor 

        @param listeningAddress:
        @type listeningAddress: tuple
        """
        threading.Thread.__init__(self)
        self._stopEvent = threading.Event()

        self.httpd = make_server( host=listeningAddress[0], port=listeningAddress[1], 
                                    app=_WebServices, handler_class=_NoLoggingWSGIRequestHandler )

    def run(self):
        """
        Run xml rpc server
        """
        self.trace("REST server started")
        try:
            while not self._stopEvent.isSet():
                self.httpd.handle_request()
        except Exception as e:
            self.error("Exception in REST server thread: " + str(e))
        self.trace("REST server stopped")

    def stop(self):
        """
        Stop the xml rpc server
        """
        self._stopEvent.set()
        self.join()
        
_RSI = None # singleton
def instance ():
    """
    Returns the singleton of the rest server

    @return:
    @rtype:
    """
    return _RSI

def initialize (listeningAddress):
    """
    Rest server instance creation

    @param listeningAddress: listing on ip and port
    @type listeningAddress: tuple
    """
    global _RSI
    _RSI = _RestServerInterface( listeningAddress = listeningAddress)

def finalize ():
    """
    Destruction of the singleton
    """
    global _RSI
    if _RSI:
        _RSI = None
