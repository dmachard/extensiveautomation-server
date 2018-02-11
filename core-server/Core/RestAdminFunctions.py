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

from pycnic.core import Handler
from pycnic.errors import HTTP_401, HTTP_400, HTTP_500, HTTP_403, HTTP_404

import os
import wrapt
import hashlib

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
    import StatsManager
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
    from . import StatsManager

import Libs.FileModels.TestSuite as TestSuite
import Libs.FileModels.TestUnit as TestUnit
import Libs.FileModels.TestPlan as TestPlan
import Libs.FileModels.TestAbstract as TestAbstract
import Libs.FileModels.TestConfig as TestConfig
 
class EmptyValue(Exception): pass

@wrapt.decorator
def _to_yaml(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for yaml generator
    """
    return wrapped(*args, **kwargs)

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
  
"""
Tasks handlers
"""       
class TasksKillAll(Handler):
    """
    /rest/tasks/kill/all
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - tasks
        summary: Kill all running tasks, only with admin level
        description: ''
        operationId: tasksKillAll
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
                  "cmd": "/tasks/kill/all"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        # kill all tasks
        success = TaskManager.instance().killAllTasks()

        return { "cmd": self.request.path, "message": "tasks successfully killed" }
     
class TasksCancelAll(Handler):
    """
    /rest/tasks/cancel/all
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - tasks
        summary: Cancel all waiting tasks, only with admin level
        description: ''
        operationId: tasksCancelAll
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
            description: Tasks successfully cancelled
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "tasks successfully cancelled",
                  "cmd": "/tasks/cancel/all"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        # kill all tasks
        success = TaskManager.instance().cancelAllTasks()

        return { "cmd": self.request.path, "message": "tasks successfully cancelled" }
           
class TasksHistoryClear(Handler):
    """
    /rest/tasks/history/clear
    """ 
    @_to_yaml
    def get(self):
        """
        tags:
          - tasks
        summary: Reset history tasks, only with admin level
        description: ''
        operationId: tasksHistoryClear
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
            description: History tasks successfully reseted
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
                  "cmd": "/tasks/history/clear"
                }
          '401':
            description: Access denied 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        success = TaskManager.instance().clearHistory()
        if not success:
            raise HTTP_500("unable to clear the history")
        return { "cmd": self.request.path, "message": "tasks successfully reseted" }

"""
Adapters handler
"""    
class AdaptersCheckSyntaxAll(Handler):
    """
    /rest/adapters/syntax/all
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - adapters
        summary: check syntax for all adapters
        description: ''
        operationId: adaptersSyntaxAll
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
        responses:
          '200':
            description: syntax is good
            schema :
              properties:
                cmd:
                  type: string
                syntax-status:
                  type: boolean
                syntax-error:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/syntax/all", 
                  "syntax-status": True,
                  "syntax-error": ""
                }
        """
        user_profile = _get_user(self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success, details = RepoAdapters.instance().checkGlobalSyntax()
        
        return { "cmd": self.request.path, "syntax-status": success, "syntax-error": details }
      
class AdaptersStatistics(Handler):
    """
    /rest/adapters/statistics
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - adapters
        summary: get adapters statistics files
        description: ''
        operationId: adaptersStatistics
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
        responses:
          '200':
            description: adapters statistics
            schema :
              properties:
                cmd:
                  type: string
                statistics:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/statistics", 
                  "statistics": "...."
                }
        """
        user_profile = _get_user(self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        _, _, _, statistics = RepoAdapters.instance().getTree()
        
        return { "cmd": self.request.path, "statistics": statistics }
   
class AdaptersFileUnlockAll(Handler):
    """
    /rest/adapters/file/unlock/all
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - adapters
        summary: unlock all adapters
        description: ''
        operationId: adaptersFileUnlockAll
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
        responses:
          '200':
            description: adapters unlocked
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/unlock/all", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoAdapters.instance().cleanupLocks( )
        if not success:
            raise HTTP_500("Unable to unlock all adapters")
            
        return { "cmd": self.request.path, "message": "unlocked" }
        
class AdaptersBackup(Handler):
    """
    /rest/adapters/backup
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: Make a backup of all adapters
        description: ''
        operationId: adaptersBackup
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
                backup-name:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/backup", 
                  "message": "created"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            backupName = self.request.data.get("backup-name")
            if backupName is None: raise EmptyValue("Please specify a backupName")            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoAdapters.instance().createBackup(backupName=backupName)  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to create backup")
            
        return { "cmd": self.request.path, "message": "created" }

class AdaptersBackupDownload(Handler):
    """
    /rest/adapters/backup/download
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - adapters
        summary: Download backup file
        description: ''
        operationId: adaptersBackupDownload
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
                backup-name:
                  type: string
                dest-name:
                  type: string 
        responses:
          '200':
            description: backup file
            schema :
              properties:
                cmd:
                  type: string
                backup:
                  type: string
                  description: backup file in base64
                dest-name:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/rest/adapters/backup/download", 
                  "backup": "....",
                  "dest-name": "..."
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            destName = self.request.data.get("dest-name")
            backupName = self.request.data.get("backup-name")
            if backupName is None: raise EmptyValue("Please specify a backup name")
            if destName is None: raise EmptyValue("Please specify a dest name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, _, _, _, backupb64, _ = RepoAdapters.instance().getBackup(pathFile=backupName, 
                                                                           project='')
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to download backup adapter")
            
        return { "cmd": self.request.path, 
                 "backup": backupb64, 
                 "dest-name": destName }

class AdaptersBackupListing(Handler):
    """
    /rest/adapters/backup/listing
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - adapters
        summary: return the list of all backups
        description: ''
        operationId: adaptersBackupListing
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                backups:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/backup/listing", 
                  "backups": "..."
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        backups =  RepoAdapters.instance().getBackups()  

        return { "cmd": self.request.path, "backups": backups }
        
class AdaptersBackupRemoveAll(Handler):
    """
    /rest/adapters/backup/remove/all
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - adapters
        summary: remove all backups from adapters
        description: ''
        operationId: adaptersBackupRemoveAll
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/adapters/remove/all", 
                  "message": "deleted"
                }
          '401':
            description: access denied, unauthorized
          '500':
            description: server error
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
          
        success = RepoAdapters.instance().deleteBackups()  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to delete all backups adapters")
            
        return { "cmd": self.request.path, "message": "deleted" } 

class AdaptersReset(Handler):
    """
    /rest/adapters/reset
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - adapters
        summary: reset adapters
        description: ''
        operationId: adaptersReset
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
        responses:
          '200':
            description: adapters reseted
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/reset", 
                  "message": "reseted"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoAdapters.instance().uninstall()
        if not success:
            raise HTTP_500("Unable to reset adapters")
            
        return { "cmd": self.request.path, "message": "reseted" }
        
class AdaptersDirectoryRemoveAll(Handler):
    """
    /rest/adapters/directory/remove/all
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - adapters
        summary: remove all directories in the adapters storage 
        description: ''
        operationId: adaptersDirectoryRemoveAll
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
              required: [ directory-path  ]
              properties:
                directory-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/directory/remove/all", 
                  "message": "all directories successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoAdapters.instance().delDirAll(folderPath)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Removing directory denied")
  
        return { "cmd": self.request.path, "message": "all directories successfully removed" }
        
"""
Libraries handler
"""  
class LibrariesCheckSyntaxAll(Handler):
    """
    /rest/libraries/syntax/all
    """   
    @_to_yaml   
    def get(self):
        """
        tags:
          - libraries
        summary: check syntax for all libraries
        description: ''
        operationId: librariesSyntaxAll
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
        responses:
          '200':
            description: syntax is good
            schema :
              properties:
                cmd:
                  type: string
                syntax-status:
                  type: boolean
                syntax-error:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/syntax/all", 
                  "syntax-status": True,
                  "syntax-error": ""
                }
        """
        user_profile = _get_user(self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success, details = RepoLibraries.instance().checkGlobalSyntax()
        
        return { "cmd": self.request.path, "syntax-status": success, "syntax-error": details }

class LibrariesDirectoryRemoveAll(Handler):
    """
    /rest/libraries/directory/remove/all
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - libraries
        summary: remove all directories in the libraries storage 
        description: ''
        operationId: librariesDirectoryRemoveAll
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
              required: [ directory-path  ]
              properties:
                directory-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/directory/remove/all", 
                  "message": "all directories successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )

        success = RepoLibraries.instance().delDirAll(folderPath)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Removing directory denied")
            
        return { "cmd": self.request.path, "message": "all directories successfully removed" }

class LibrariesBackup(Handler):
    """
    /rest/libraries/backup
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - libraries
        summary: Make a backup of all libraries
        description: ''
        operationId: librariesBackup
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
                backup-name:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/backup", 
                  "message": "created"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            backupName = self.request.data.get("backup-name")
            if backupName is None: 
                raise EmptyValue("Please specify a backupName")            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoLibraries.instance().createBackup(backupName=backupName)  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to create backup")
            
        return { "cmd": self.request.path, "message": "created" }
         
class LibrariesBackupDownload(Handler):
    """
    /rest/libraries/backup/download
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - libraries
        summary: Download backup file
        description: ''
        operationId: librariesBackupDownload
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
                backup-name:
                  type: string
                dest-name:
                  type: string 
        responses:
          '200':
            description: backup file
            schema :
              properties:
                cmd:
                  type: string
                backup:
                  type: string
                  description: backup file in base64
                dest-name:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/rest/libraries/backup/download", 
                  "backup": "....",
                  "dest-name": "..."
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            destName = self.request.data.get("dest-name")
            backupName = self.request.data.get("backup-name")
            if backupName is None: raise EmptyValue("Please specify a backup name")
            if destName is None: raise EmptyValue("Please specify a dest name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, _, _, _, backupb64, _ = RepoLibraries.instance().getBackup(pathFile=backupName, 
                                                                            project='')
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to download backup library")
            
        return { "cmd": self.request.path, 
                 "backup": backupb64, 
                 "dest-name": destName }

class LibrariesBackupListing(Handler):
    """
    /rest/libraries/backup/listing
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: return the list of all backups
        description: ''
        operationId: librariesBackupListing
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                backups:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/backup/listing", 
                  "backups": "..."
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        backups =  RepoLibraries.instance().getBackups()  

        return { "cmd": self.request.path, "backups": backups }
        
class LibrariesBackupRemoveAll(Handler):
    """
    /rest/libraries/backup/remove/all
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: remove all backups from libraries
        description: ''
        operationId: librariesBackupRemoveAll
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/libraries/remove/all", 
                  "message": "deleted"
                }
          '401':
            description: access denied, unauthorized
          '500':
            description: server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoLibraries.instance().deleteBackups()  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to delete all backups libraries")
            
        return { "cmd": self.request.path, "message": "deleted" } 
        
class LibrariesFileUnlockAll(Handler):
    """
    /rest/libraries/file/unlock/all
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: unlock all libraries
        description: ''
        operationId: librariesFileUnlockAll
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
        responses:
          '200':
            description: libraries unlocked
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/file/unlock/all", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoLibraries.instance().cleanupLocks( )
        if not success:
            raise HTTP_500("Unable to unlock all libraries")
            
        return { "cmd": self.request.path, "message": "unlocked" }
        
class LibrariesStatistics(Handler):
    """
    /rest/libraries/statistics
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: get libraries statistics files
        description: ''
        operationId: librariesStatistics
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
        responses:
          '200':
            description: libraries statistics
            schema :
              properties:
                cmd:
                  type: string
                statistics:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/statistics", 
                  "statistics": "...."
                }
        """
        user_profile = _get_user(self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        _, _, _, statistics = RepoLibraries.instance().getTree()
        
        return { "cmd": self.request.path, "statistics": statistics }
        
class LibrariesReset(Handler):
    """
    /rest/libraries/reset
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: reset libraries
        description: ''
        operationId: librariesReset
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
        responses:
          '200':
            description: libraries reseted
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/reset", 
                  "message": "reseted"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoLibraries.instance().uninstall()
        if not success:
            raise HTTP_500("Unable to reset libraries")
            
        return { "cmd": self.request.path, "message": "reseted" }
  
"""
Administration handlers
"""
class AdminConfigListing(Handler):
    """
    /rest/administration/configurationg/listing
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - admin
        summary: Get all configuration
        description: ''
        operationId: adminConfigurationgListing
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        config = {}
        for section in Settings.instance().sections():
            for (name,value) in Settings.instance().items(section):
                config["%s-%s" % ( section.lower(), name.lower() )] = value
                
        return { "cmd": self.request.path, "configuration": config }  

class AdminConfigReload(Handler):
    """
    /rest/administration/configuration/reload
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - admin
        summary: Reload the configuration
        description: ''
        operationId: adminConfigurationReload
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        CliFunctions.instance().reload()

        return { "cmd": self.request.path, "status": "reloaded" }  
        
class AdminClientsDeploy(Handler):
    """
    /rest/administration/clients/deploy
    """
    @_to_yaml     
    def get(self):
        """
        tags:
          - admin
        summary: Deploy clients
        description: ''
        operationId: adminClientsDeploy
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        CliFunctions.instance().deployclients()
        CliFunctions.instance().deployclients(portable=True)
        
        return { "cmd": self.request.path, "status": "deployed" }  

class AdminProjectsListing(Handler):
    """
    /rest/administration/projects/listing
    """
    @_to_yaml   
    def get(self):
        """
        tags:
          - admin
        summary: Get all projects
        description: ''
        operationId: adminProjectsListing
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                projects:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/projects/listing", 
                  "projects: "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        success, details = ProjectsManager.instance().getProjectsFromDB()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "projects": details }
        
class AdminProjectsStatistics(Handler):
    """
    /rest/administration/projects/statistics
    """
    @_to_yaml   
    def get(self):
        """
        tags:
          - admin
        summary: Get statistics on projects
        description: ''
        operationId: adminProjectsStatistics
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/projects/statistics", 
                  "projects-statistics: "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        success, details = ProjectsManager.instance().getStatisticsFromDb()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "projects-statistics": details }
        
class AdminProjectsAdd(Handler):
    """
    /rest/administration/projects/add
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - admin
        summary: Add a project
        description: ''
        operationId: adminProjectsAdd
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
              required: [ project-name ]
              properties:
                project-name:
                  type: string
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/projects/add", 
                  "message: "project successfully added"
                }
          '400':
            description: Bad request provided
          '403':
            description: Project name already used
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        try:
            projectName = self.request.data.get("project-name")
            if projectName is None : raise HTTP_400("Please specify a project name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        success, details = ProjectsManager.instance().addProjectToDB(projectName=projectName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403(details)

        return { "cmd": self.request.path, "message": "project successfully added", "project-id": details }

class AdminProjectsRename(Handler):
    """
    /rest/administration/projects/rename
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - admin
        summary: Rename a project
        description: ''
        operationId: adminProjectsRename
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
              required: [ project-name, project-ic ]
              properties:
                project-id:
                  type: integer
                project-name:
                  type: string
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/projects/rename", 
                  "message: "project successfully renamed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Name already exist or rename not authorized
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise HTTP_400("Please specify a project id")
            
            projectName = self.request.data.get("project-name")
            if projectName is None: raise HTTP_400("Please specify a project name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        success, details = ProjectsManager.instance().updateProjectFromDB(projectName=projectName, 
                                                                          projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403(details)
            
        return { "cmd": self.request.path, "message": "project successfully updated" }

class AdminProjectsRemove(Handler):
    """
    /rest/administration/projects/remove
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - admin
        summary: Remove a project
        description: ''
        operationId: adminProjectsRemove
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
              required: [ project-id ]
              properties:
                project-id:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/projects/remove", 
                  "message: "project successfully removed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Deletion not authorized
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise HTTP_400("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
        
        if projectId == 1: raise HTTP_403("Remove this project is not authorized")
        
        success, details = ProjectsManager.instance().delProjectFromDB(projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "project successfully removed" } 

class AdminUsersProfile(Handler):
    """
    /rest/administration/users/profile
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - admin
        summary: Get the profile of a user
        description: ''
        operationId: adminUsersProfile
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
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
    /rest/administration/users/listing
    """
    @_to_yaml   
    def get(self):
        """
        tags:
          - admin
        summary: Get all users
        description: ''
        operationId: adminUsersListing
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
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
    /rest/administration/users/statistics
    """
    @_to_yaml 
    def get(self):
        """
        tags:
          - admin
        summary: Users statistics
        description: ''
        operationId: adminUsersStatistics
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        success, details = UsersManager.instance().getStatisticsFromDb()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
            
        return { "cmd": self.request.path, "users-statistics": details }
        
class AdminUsersAdd(Handler):
    """
    /rest/administration/users/add
    """
    @_to_yaml 
    def post(self):
        """
        tags:
          - admin
        summary: Add a user
        description: ''
        operationId: adminUsersAdd
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
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
    /rest/administration/users/update
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - admin
        summary: Update the profile of a user
        description: ''
        operationId: adminUsersUpdate
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
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
    /rest/administration/users/remove
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - admin
        summary: Remove a user
        description: ''
        operationId: adminUsersRemove
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
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
    /rest/administration/users/status
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - admin
        summary: Status of the user
        description: ''
        operationId: adminUsersStatus
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
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
        
class AdminUsersChannelDisconnect(Handler):
    """
    /rest/administration/users/channel/disconnect
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - admin
        summary: Force channel disconnection for a user
        description: ''
        operationId: adminUsersChannelDisconnect
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
              required: [ login ]
              properties:
                login:
                  type: string
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/users/channel/disconnect", 
                  "message: "user successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: User not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
        try:
            userLogin = self.request.data.get("login")
            if userLogin is None: raise HTTP_400("Please specify a login")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = Context.instance().unregisterChannelUser(login=userLogin)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("user not found")
            
        return { "cmd": self.request.path, "message": "user successfully disconnected" } 
  
class AdminUsersDuplicate(Handler):
    """
    /rest/administration/users/duplicate
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - admin
        summary: Duplicate user
        description: ''
        operationId: adminUsersDuplicate
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
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
    /rest/administration/users/password/reset
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - admin
        summary: Reset the password of a user
        description: ''
        operationId: adminUsersPasswordReset
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
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
    /rest/administration/users/password/update
    """
    @_to_yaml 
    def post(self):
        """
        tags:
          - admin
        summary: Update user password
        description: ''
        operationId: adminUsersPasswordUpdate
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
            
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
        sha1 = hashlib.sha1()
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
    /rest/administration/users/search
    """
    @_to_yaml 
    def post(self):
        """
        tags:
          - admin
        summary: Search user according to the id
        description: ''
        operationId: adminUsersSearch
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
           
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

class AdminTimeShift(Handler):
    """
    /rest/administration/time/shift
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - admin
        summary: Shift the local time
        description: ''
        operationId: adminTimeShift
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
              required: [ shift ]
              properties:
                shift:
                  type: integer
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
           
        try:
            shift = self.request.data.get("shift")
            if shift is None: raise EmptyValue("Please specify the shift value")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        f = open("%s/%s/timeshift" % ( Settings.getDirExec(), 
                                       Settings.get('Paths', 'templates')), "w")
        f.write("%s" % shift)
        f.close()
        
        return { "cmd": self.request.path, "users": details }

"""
Metrics handlers
"""      
class MetricsTestsReset(Handler):
    """
    /rest/metrics/tests/reset
    """
    @_to_yaml      
    def get(self):
        """
        tags:
          - metrics
        summary: Reset tests statistics
        description: ''
        operationId: metricsTestsReset
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
        responses:
          '200':
            description: statistics reseted
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/metrics/reset", 
                  "message": "tests statistics reseted"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = StatsManager.instance().resetStats()
        if not success:
            raise HTTP_500("Unable to reset statistics for tests")
            
        return { "cmd": self.request.path, 'message': 'tests statistics reseted' }
        
"""
Tests handlers
"""
class TestsBuild(Handler):
    """
    /rest/tests/build/samples
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - tests
        summary: build tests samples
        description: ''
        operationId: testsBuildSamples
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
        responses:
          '200':
            description: tests packaged
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/build/samples", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = Context.instance().generateSamples()
        if not success:
            raise HTTP_500("Unable to package tests samples")
            
        return { "cmd": self.request.path, "message": "packaged" } 

class TestsFileUnlockAll(Handler):
    """
    /rest/tests/file/unlock/all
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - tests
        summary: unlock tests
        description: ''
        operationId: testsFileUnlockAll
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
        responses:
          '200':
            description: tests unlocked
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/unlock/all", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoTests.instance().cleanupLocks( )
        if not success:
            raise HTTP_500("Unable to unlock all tests")
            
        return { "cmd": self.request.path, "message": "unlocked" }
   
class TestsFileDefaultAll(Handler):
    """
    /rest/tests/file/default/all
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - tests
        summary: set all tests with the default adapters and libraries version
        description: ''
        operationId: testsFileDefaultAll
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/unlock/all", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoTests.instance().setTestsWithDefault()
        if not success:
            raise HTTP_500("Unable to set default version of adapters and libraries for all tests")
            
        return { "cmd": self.request.path, "message": "default version configured" }
               
class TestsStatistics(Handler):
    """
    /rest/tests/statistics
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: get tests statistics files
        description: ''
        operationId: testsStatistics
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
              required: [ project-id ]
              properties:
                project-id:
                  type: string
        responses:
          '200':
            description: tests statistics
            schema :
              properties:
                cmd:
                  type: string
                statistics:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/statistics", 
                  "statistics": "...."
                }
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
  
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        if projectId == 0: projectId=''
        
        _, _, _, statistics = RepoTests.instance().getTree(project=projectId)
        
        return { "cmd": self.request.path, 
                 "statistics": statistics, 
                 "project-id": projectId }

class TestsDirectoryRemoveAll(Handler):
    """
    /rest/tests/directory/remove/all
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: remove all directories in the test storage 
        description: ''
        operationId: testsDirectoryRemoveAll
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
              required: [ project-id, directory-path  ]
              properties:
                project-id:
                  type: integer
                directory-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/directory/remove/all", 
                  "message": "all directories successfully removed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )

        success = RepoTests.instance().delDirAll(folderPath, projectId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Removing directory denied")

        return { "cmd": self.request.path, "message": "all directories successfully removed",
                 "project-id": projectId }

class TestsBackup(Handler):
    """
    /rest/tests/backup
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Make a backup of all tests
        description: ''
        operationId: testsBackup
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
                backup-name:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/backup", 
                  "message": "created"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            backupName = self.request.data.get("backup-name")
            if backupName is None: 
                raise EmptyValue("Please specify a backupName")            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoTests.instance().createBackup(backupName=backupName)  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to create backup")
            
        return { "cmd": self.request.path, "message": "created" }
        
class TestsBackupDownload(Handler):
    """
    /rest/tests/backup/download
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Download backup file
        description: ''
        operationId: testsBackupDownload
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
                backup-name:
                  type: string
                dest-name:
                  type: string
        responses:
          '200':
            description: backup file
            schema :
              properties:
                cmd:
                  type: string
                backup:
                  type: string
                  description: backup file in base64
                dest-name:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/rest/tests/backup/download", 
                  "backup": "....",
                  "dest-name": "..."
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            destName = self.request.data.get("dest-name")
            backupName = self.request.data.get("backup-name")
            if backupName is None: raise EmptyValue("Please specify a backup name")
            if destName is None: raise EmptyValue("Please specify a dest name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, _, _, _, backupb64, _ = RepoTests.instance().getBackup(pathFile=backupName, 
                                                                        project='')
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to download backup test")
            
        return { "cmd": self.request.path, 
                 "backup": backupb64, 
                 "dest-name": destName }

class TestsBackupListing(Handler):
    """
    /rest/tests/backup/listing
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - tests
        summary: return the list of all backups
        description: ''
        operationId: testsBackupListing
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                backups:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/backup/listing", 
                  "backups": "..."
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        backups =  RepoTests.instance().getBackups()  

        return { "cmd": self.request.path, "backups": backups }
        
class TestsBackupRemoveAll(Handler):
    """
    /rest/tests/backup/remove/all
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - tests
        summary: remove all backups from tests
        description: ''
        operationId: testsBackupRemoveAll
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/tests/backup/remove/all", 
                  "message": "deleted"
                }
          '401':
            description: access denied, unauthorized
          '500':
            description: server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoTests.instance().deleteBackups()  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to delete all backups tests")
            
        return { "cmd": self.request.path, "message": "deleted" }

class TestsReset(Handler):
    """
    /rest/tests/reset
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - tests
        summary: reset tests
        description: ''
        operationId: testsReset
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
        responses:
          '200':
            description: tests uninstalled
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/reset", 
                  "message": "reseted"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoTests.instance().emptyRepo(projectId='')
        if not success:
            raise HTTP_500("Unable to reset tests")
            
        return { "cmd": self.request.path, "message": "reseted" }
        
class TestsSnapshotRemoveAll(Handler):
    """
    /rest/tests/snapshot/remove/all
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: remove all snapshots according to the test provided
        description: ''
        operationId: testsSnapshotRemoveAll
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
              required: [ project-id, test-path, test-name, test-extension ]
              properties:
                project-id:
                  type: integer
                test-path:
                  type: string
                test-name:
                  type: string
                test-extension:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/rest/tests/snapshot/remove/all", 
                  "message": "all snapshots removed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            testExt = self.request.data.get("test-extension")
            if testExt is None: raise EmptyValue("Please specify a test extension")
       
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], 
                                                                                  projectId=projectId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success =  RepoTests.instance().deleteAllSnapshots( testPath=testPath, 
                                                            testPrjId=projectId,
                                                            testName=testName,
                                                            testExt=testExt
                                                            )
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to find the test provided")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to delete all snapshots")
            
        return { "cmd": self.request.path, "message": "all snapshots deleted", "project-id": projectId }

"""
Variables handlers
"""
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
        operationId: variablesReset
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
              required: [project-id]
              properties:
                project-id:
                  type: integer
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
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], 
                                                                                  projectId=projectId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
            
        success, details = RepoTests.instance().delVariablesInDB(projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "variables successfully reseted" }

"""
Tests Results handlers
"""
class ResultsReset(Handler):
    """
    /rest/results/reset
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Remove all the tests results according to the project provided
        description: ''
        operationId: resultsReset
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
              required: [ project-id ]
              properties:
                project-id:
                  type: integer
        responses:
          '200':
            description: image
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/reset", 
                  "message": "xxxxxxxx"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error 
        """
        user_profile = _get_user(request=self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
                    
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
                
        # get the project id according to the name and checking authorization
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], 
                                                                                  projectId=projectId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        success = RepoArchives.instance().resetArchives(projectId=projectId)  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to reset test results")
            
        return { "cmd": self.request.path, "message": "results successfully reseted", 
                 'project-id': projectId }
        
class ResultsBackup(Handler):
    """
    /rest/results/backup
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Make a backup of all tests results
        description: ''
        operationId: resultsBackup
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
              required: [ backup-name ]
              properties:
                backup-name:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/backup", 
                  "message": "created"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            backupName = self.request.data.get("backup-name")
            if backupName is None: raise EmptyValue("Please specify a backup-name")            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoArchives.instance().createBackup(backupName=backupName)  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to create backup")
            
        return { "cmd": self.request.path, "message": "created" }

class ResultsBackupListing(Handler):
    """
    /rest/results/backup/listing
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - results
        summary: return the list of all backups
        description: ''
        operationId: resultsBackupListing
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                backups:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/backup/listing", 
                  "backups": "..."
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        backups =  RepoArchives.instance().getBackups()  

        return { "cmd": self.request.path, "backups": backups }
     
class ResultsBackupDownload(Handler):
    """
    /rest/results/backup/download
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - results
        summary: Download backup file
        description: ''
        operationId: resultsBackupDownload
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
              required: [ backup-name, dest-name ]
              properties:
                backup-name:
                  type: string
                dest-name:
                  type: string
        responses:
          '200':
            description: backup file
            schema :
              properties:
                cmd:
                  type: string
                backup:
                  type: string
                  description: backup file in base64
                dest-name:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/rest/results/backup/download", 
                  "backup": "....",
                  "dest-name": "..."
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        try:
            destName = self.request.data.get("dest-name")
            backupName = self.request.data.get("backup-name")
            if backupName is None: raise EmptyValue("Please specify a backup name")
            if destName is None: raise EmptyValue("Please specify a dest name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, _, _, _, backupb64, _ = RepoArchives.instance().getBackup(pathFile=backupName, 
                                                                           project='')
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to download backup result")
            
        return { "cmd": self.request.path, 
                 "backup": backupb64, 
                 "dest-name": destName }
        
class ResultsBackupRemoveAll(Handler):
    """
    /rest/results/backup/remove/all
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - results
        summary: remove all backups from test results
        description: ''
        operationId: resultsBackupRemoveAll
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/results/remove/all", 
                  "message": "deleted"
                }
          '401':
            description: access denied, unauthorized
          '500':
            description: server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']: raise HTTP_403("Access refused")
        
        success = RepoArchives.instance().deleteBackups()  
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to delete all backups results")
            
        return { "cmd": self.request.path, "message": "deleted" } 

class ResultsStatistics(Handler):
    """
    /rest/results/statistics
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: get results statistics files
        description: ''
        operationId: resultsStatistics
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
              required: [ project-id ]
              properties:
                project-id:
                  type: string
        responses:
          '200':
            description: results statistics
            schema :
              properties:
                cmd:
                  type: string
                statistics:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/statistics", 
                  "statistics": "...."
                }
        """
        user_profile = _get_user(self.request)
        
        if not user_profile['administrator']: raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
            
        # get the project id according to the name and checking authorization
        projectAuthorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_profile['login'], 
                                                                                  projectId=projectId)
        if not projectAuthorized:
            raise HTTP_403('Access denied to this project')
        
        _, _, _, statistics = RepoArchives.instance().getTree()
        
        return { "cmd": self.request.path, "statistics": statistics }  
        