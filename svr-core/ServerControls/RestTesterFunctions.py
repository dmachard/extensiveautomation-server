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
import json
import wrapt

from Libs import Settings, Logger

from ServerEngine import (Context, ProjectsManager,  
                          TaskManager, AgentsManager, ProbesManager,
                          ToolboxManager,
                          UsersManager, HelperManager, 
                          StatsManager )
from ServerRepositories import ( RepoAdapters, RepoLibraries, RepoTests,
                                 RepoPublic, RepoArchives )

import Libs.FileModels.TestSuite as TestSuite
import Libs.FileModels.TestUnit as TestUnit
import Libs.FileModels.TestPlan as TestPlan
import Libs.FileModels.TestAbstract as TestAbstract
   
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

def _check_project_permissions(user_login, project_id):
    """
    Look up project
    """
    try:
        project_id = int(project_id)
    except:
        raise HTTP_400("Bad project id (Id=%s) provided in request, int expected" % str(project_id) )

    # get the project id according to the name and checking permissions
    project_authorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_login, 
                                                                               projectId=project_id)
    if not project_authorized:
        raise HTTP_403('Permission denied to this project')

"""
Adapters handler
"""
class AdaptersAdapterAddByWsdlFile(Handler):
    """
    /rest/adapters/adapter/add/by/wsdl/file
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: Add adapter from wsdl file
        description: ''
        operationId: adaptersAdapterAddByWsdlFile
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
                wsdl-file:
                  type: string
                package-name:
                  type: string
                adapter-overwrite:
                  type: boolean
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
                  "cmd": "/adapters/adapter/add/by/wsdl/file", 
                  "message": "adapter added"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            wsdlFile = self.request.data.get("wsdl-file")
            if wsdlFile is None: raise EmptyValue("Please specify a wsdl file")   

            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify a package name") 

            adapterOverwrite = self.request.data.get("overwrite-adapter")
            if adapterOverwrite is None: raise EmptyValue("Please specify a adapter overwrite") 
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = RepoAdapters.instance().generateFromWSDL(
                                                    wsdlUrl='',
                                                    wsdlFile=wsdlFile,
                                                    pkg=packageName,
                                                    overwrite=adapterOverwrite
                                                )
        
        if not success:
            raise HTTP_500("Unable to generate adapter from wsdl file")
            
        return { "cmd": self.request.path, "message": "adapter added" }
        
class AdaptersAdapterAddByWsdlUrl(Handler):
    """
    /rest/adapters/adapter/add/by/wsdl/url
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: Add adapter from wsdl url
        description: ''
        operationId: adaptersAdapterAddByWsdlUrl
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
                wsdl-url:
                  type: string
                package-name:
                  type: string
                adapter-overwrite:
                  type: boolean
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
                  "cmd": "/adapters/adapter/add/by/wsdl/url", 
                  "message": "adapter added"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            wsdlUrl = self.request.data.get("wsdl-url")
            if wsdlUrl is None: raise EmptyValue("Please specify a wsdl url")   

            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify a package name") 

            adapterOverwrite = self.request.data.get("adapter-overwrite")
            if adapterOverwrite is None: raise EmptyValue("Please specify a adapter overwrite") 
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = RepoAdapters.instance().generateFromWSDL(
                                                    wsdlUrl=wsdlUrl,
                                                    wsdlFile='',
                                                    pkg=packageName,
                                                    overwrite=adapterOverwrite
                                                )
        
        if not success:
            raise HTTP_500("Unable to generate adapter from wsdl url")
            
        return { "cmd": self.request.path, "message": "adapter added" }
        
class AdaptersAdapterAdd(Handler):
    """
    /rest/adapters/adapter/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: Add a new adapter
        description: ''
        operationId: adaptersAdapterAdd
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
                package-name:
                  type: string
                adapter-name:
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
                  "cmd": "/adapters/adapter/add", 
                  "message": "adapter added"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify a package name")   

            adapterName = self.request.data.get("adapter-name")
            if adapterName is None: raise EmptyValue("Please specify a adapter name")            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = RepoAdapters.instance().addAdapter(  pathFolder=packageName, 
                                                       adapterName=adapterName, 
                                                       mainAdapters=False)
        
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to add adapter")
            
        return { "cmd": self.request.path, "message": "adapter added" }
        
class AdaptersPackageAdd(Handler):
    """
    /rest/adapters/package/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: Add a new package of adapters
        description: ''
        operationId: adaptersPackageAdd
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
                package-name:
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
                  "cmd": "/libraries/package/add", 
                  "message": "package added"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify a package name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = RepoAdapters.instance().addAdapter(  pathFolder="", 
                                                       adapterName=packageName, 
                                                       mainAdapters=True  )
        
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to add package of adapters")
            
        return { "cmd": self.request.path, "message": "package added" }

class AdaptersPackageDefault(Handler):
    """
    /rest/adapters/package/default
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: set adapters package as default
        description: ''
        operationId: adaptersPackageDefault
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
              required: [ package-name ]
              properties:
                package-name:
                  type: string
        responses:
          '200':
            description: adapters vXXXX is default
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/package/default", 
                  "message": "success"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify the package name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoAdapters.instance().setDefaultV2(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as default the package %s" % packageName )

        return { "cmd": self.request.path, "message": "success" }

class AdaptersPackageGeneric(Handler):
    """
    /rest/adapters/package/generic
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - adapters
        summary: set adapters package as generic
        description: ''
        operationId: adaptersPackageGeneric
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
              required: [ package-name ]
              properties:
                package-name:
                  type: string
        responses:
          '200':
            description: adapters vXXXX is generic
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/package/generic", 
                  "message": "success"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify the package name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoAdapters.instance().setGeneric(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as generic the package %s" % packageName )
                
        return { "cmd": self.request.path, "message": "success" }

class AdaptersCheckSyntax(Handler):
    """
    /rest/adapters/check/syntax
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - adapters
        summary: check the syntax of a adapter
        description: ''
        operationId: adaptersCheckSyntax
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
              required: [ file-content ]
              properties:
                file-content:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                success:
                  type: boolean
                syntax-error:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/check/syntax", 
                  "file-content": "...."
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
            fileContent = self.request.data.get("file-content")
            if fileContent is None: raise EmptyValue("Please specify a file content")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        success, syntaxerror = RepoAdapters.instance().checkSyntax(content=fileContent)

        return { "cmd": self.request.path, "success": success, "syntax-error": syntaxerror }

class AdaptersBuild(Handler):
    """
    /rest/adapters/build
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - adapters
        summary: build adapters
        description: ''
        operationId: adaptersBuild
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
            description: adapters packaged
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/build", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        success = Context.instance().generateAdapters()
        if not success:
            raise HTTP_500("Unable to package adapters")
            
        return { "cmd": self.request.path, "message": "packaged" }

class AdaptersListing(Handler):
    """
    /rest/adapters/listing
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - adapters
        summary: Get the listing of all adapters.
        description: ''
        operationId: adaptersListing
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
            description: adapters listing
            schema :
              properties:
                cmd:
                  type: string
                adapters-listing:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/listing", 
                  "adapters-listing": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        _, _, listing, _ = RepoAdapters.instance().getTree()

        return { "cmd": self.request.path, "adapters-listing": listing }
        
class AdaptersFileMove(Handler):
    """
    /rest/adapters/file/move
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - adapters
        summary: Move file
        description: ''
        operationId: adaptersFileMove
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ file-name, file-path, file-extension  ]
                  properties:
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ file-path ]
                  properties:
                    file-path:
                      type: string
        responses:
          '200':
            description: move response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/move", 
                  "message": "file successfully moved"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source filename")
            
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source file path")
            
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            
            newFilePath = self.request.data.get("destination")["file-path"]
            if newFilePath is None: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

            
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )

        success = RepoAdapters.instance().moveFile( 
                                                        mainPath=filePath, 
                                                        fileName=fileName, 
                                                        extFilename=fileExt, 
                                                        newPath=newFilePath
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Move file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file successfully moved" }
        
class AdaptersDirectoryMove(Handler):
    """
    /rest/adapters/directory/move
    """   
    @_to_yaml   
    def post(self):
        """
        tags:
          - adapters
        summary: Move directory
        description: ''
        operationId: adaptersDirectoryMove
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ directory-name, directory-path  ]
                  properties:
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ directory-path ]
                  properties:
                    directory-path:
                      type: string
        responses:
          '200':
            description: move response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/directory/move", 
                  "message": "directory successfully moved"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        # checking json request on post
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")

            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if newFolderPath is None: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        if "%s/%s" % (folderPath, folderName) == newFolderPath:
            raise HTTP_403( "Destination same as origin" )
            
        # all ok, do the duplication
        success = RepoAdapters.instance().moveDir(
                                                    mainPath=folderPath, 
                                                    folderName=folderName, 
                                                    newPath=newFolderPath
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to move directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully moved"}

class AdaptersFileRename(Handler):
    """
    /rest/adapters/file/rename
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - adapters
        summary: Rename file in the adapters storage 
        description: ''
        operationId: adaptersFileRename
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, file-name, file-path, file-extension  ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ project-id, file-name ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/rename", 
                  "message": "file successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoAdapters.instance().renameFile( 
                                                    mainPath=filePath, 
                                                    oldFilename=fileName, 
                                                    newFilename=newFileName, 
                                                    extFilename=fileExt
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Rename file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully renamed",
                 "file-path": filePath,
                 "file-name": fileName,
                 "file-extension": fileExt,
                 "new-file-name": newFileName        }
        
class AdaptersDirectoryRename(Handler):
    """
    /rest/adapters/directory/rename
    """   
    @_to_yaml   
    def post(self):
        """
        tags:
          - adapters
        summary: Rename directory in the adapters storage 
        description: ''
        operationId: adaptersDirectoryRename
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, directory-name, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ project-id, directory-name ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/directory/rename", 
                  "message": "directory successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
		
        if user_profile['leader']: raise HTTP_403("Access refused")

        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoAdapters.instance().renameDir(mainPath=folderPath, oldPath=folderName, 
                                                    newPath=newFolderName)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to rename directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully renamed",
                 "directory-name": folderName, "directory-path": folderPath, 
                 "new-directory-name": newFolderName}

class AdaptersFileDuplicate(Handler):
    """
    /rest/adapters/file/duplicate
    """   
    @_to_yaml    
    def post(self):
        """
        tags:
          - adapters
        summary: Duplicate file in the adapters storage 
        description: ''
        operationId: adaptersFileDuplicate
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, file-name, file-path, file-extension  ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ project-id, file-name ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/rename", 
                  "message": "file successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
            newFilePath = self.request.data.get("destination")["file-path"]
            if newFilePath is None: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoAdapters.instance().duplicateFile( 
                                                        mainPath=filePath,
                                                        oldFilename=fileName,
                                                        newFilename=newFileName,
                                                        extFilename=fileExt,
                                                        newMainPath=newFilePath
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Duplicate file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully duplicated" }
        
class AdaptersDirectoryDuplicate(Handler):
    """
    /rest/adapters/directory/duplicate
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - adapters
        summary: Duplicate directory in the adapters storage 
        description: ''
        operationId: adaptersDirectoryDuplicate
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ directory-name, directory-path  ]
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
                    directory-path:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/directory/rename", 
                  "message": "directory successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        # checking json request on post
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if newFolderPath is None: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        # all ok, do the duplication
        success = RepoAdapters.instance().duplicateDir(
                                                    mainPath=folderPath, 
                                                    oldPath=folderName, 
                                                    newPath=newFolderName,
                                                    newMainPath=newFolderPath
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to duplicate directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully duplicated" }

class AdaptersFileRemove(Handler):
    """
    /rest/adapters/file/remove
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - adapters
        summary: remove file in the adapters storage 
        description: ''
        operationId: adaptersFileRemove
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
              required: [ file-path  ]
              properties:
                file-path:
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
                  "cmd": "/adapters/file/remove", 
                  "message": "file successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            filePath = self.request.data.get("file-path")
            if not filePath: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoAdapters.instance().delFile( pathFile=filePath )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove file")
        if success == Context.instance().CODE_FAILED:
            raise HTTP_403("Remove file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file successfully removed" }

class AdaptersFileUnlock(Handler):
    """
    /rest/adapters/file/unlock
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - adapters
        summary: unlock file in the adapters storage 
        description: ''
        operationId: adaptersFileUnlock
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
              required: [ file-path, file-name, file-extension  ]
              properties:
                file-path:
                  type: string
                file-name:
                  type: string
                file-extension:
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
                  "cmd": "/adapters/file/unlock", 
                  "message": "file successfully unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a source filepath")
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a source file filename")
            fileExt = self.request.data.get("file-extension")
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success  = RepoAdapters.instance().unlockFile(pathFile=filePath, 
                                                   nameFile=fileName, 
                                                   extFile=fileExt,
                                                   login=user_profile["login"])
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to unlock adapter file")
            
        return { "cmd": self.request.path, "message": "file successfully unlocked" }

class AdaptersDirectoryRemove(Handler):
    """
    /rest/adapters/directory/remove
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - adapters
        summary: remove directory in the adapters storage 
        description: ''
        operationId: adaptersDirectoryRemove
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
                recursive:
                  type: boolean
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
                  "cmd": "/adapters/directory/remove", 
                  "message": "directory successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )

        success = RepoAdapters.instance().delDir(folderPath)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Cannot remove directory")
            
        return { "cmd": self.request.path, "message": "directory successfully removed" }

class AdaptersDirectoryAdd(Handler):
    """
    /rest/adapters/directory/add
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - adapters
        summary: Add directory in the adapters storage 
        description: ''
        operationId: adaptersDirectoryAdd
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
              required: [ directory-name, directory-path ]
              properties:
                directory-name:
                  type: string
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
                  "cmd": "/adapters/directory/add", 
                  "message": "directory successfully added"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            folderName = self.request.data.get("directory-name")
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoAdapters.instance().addDir(pathFolder=folderPath, folderName=folderName)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add directory")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully added" }

class AdaptersFileUpload(Handler):
    """
    /rest/adapters/file/upload
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - adapters
        summary: Upload file the test storage 
        description: ''
        operationId: adaptersFileUpload
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
              required: [ project-id, file-path, file-name, file-extension, file-content ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
                file-name:
                  type: string
                file-extension:
                  type: string
                file-content:
                  type: string
                overwrite:
                  type: boolean
                close-after:
                  type: boolean
                add-folders:
                  type: boolean
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                code:
                  type: integer
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/upload", 
                  "code": 200
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a file name")
            fileExt = self.request.data.get("file-extension")
            if fileExt is None: raise EmptyValue("Please specify a file extension")
            fileContent = self.request.data.get("file-content")
            if fileContent is None: raise EmptyValue("Please specify a file content")
            
            _overwrite = self.request.data.get("overwrite", False)
            _closeafter = self.request.data.get("close-after", False)
            _addfolders = self.request.data.get("add-folders", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # overwrite = False
        # if _overwrite is not None:
            # overwrite = _overwrite
            
        # closeAfter = False
        # if _closeafter is not None:
            # closeAfter = _closeafter
            
        # addFolders = False
        # if _addfolders is not None:
            # addFolders = _addfolders
            
        putFileReturn = RepoAdapters.instance().uploadFile( pathFile=filePath, 
                                                            nameFile=fileName, 
                                                            extFile=fileExt, 
                                                            contentFile=fileContent, 
                                                            login=user_profile['login'], 
                                                            project='', 
                                                            overwriteFile=_overwrite,
                                                            createFolders=_addfolders,
                                                            lockMode=True, 
                                                            binaryMode=True,
                                                            closeAfter=_closeafter )
        success, pathFile, nameFile, extFile, _, overwriteFile, closeAfter, isLocked, lockedBy = putFileReturn

        return { "cmd": self.request.path, 
                 "code": success,
                 "file-path": pathFile,
                 "file-name": nameFile,
                 "file-extension": extFile,
                 "overwrite":  overwriteFile,
                 "close-after": closeAfter,
                 "locked": isLocked,
                 "locked-by": lockedBy }

class AdaptersFileDownload(Handler):
    """
    /rest/adapters/file/download
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - adapters
        summary: download file from the test storage 
        description: ''
        operationId: adaptersFileDownload
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                file-content:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/download", 
                  "file-content": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a  project id")
            
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success, _, _, _, content, _, _ = RepoTests.instance().getFile(pathFile=filePath, 
                                                                       binaryMode=True, 
                                                                       project=projectId, 
                                                                       addLock=False)  
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to download file")

        return { "cmd": self.request.path, "file-content": content }
        
class AdaptersFileOpen(Handler):
    """
    /rest/adapters/file/open
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - adapters
        summary: open and lock file from the test storage 
        description: ''
        operationId: adaptersFileOpen
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                file-content:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/adapters/file/open", 
                  "file-content": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
            
            _ignoreLock = self.request.data.get("ignore-lock", False)
            _readOnly = self.request.data.get("read-only", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # ignoreLock = False
        # if _ignoreLock is not None:
            # ignoreLock = _ignoreLock
        
        # readOnly = False
        # if _readOnly is not None:
            # _readOnly = readOnly
           
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )

        resultGetFile = RepoAdapters.instance().getFile(pathFile=filePath, 
                                                        login=user_profile['login'],
                                                        forceOpen=_ignoreLock, 
                                                        readOnly=_readOnly)  
        success, path_file, name_file, ext_file, project, data_base64, locked, locked_by = resultGetFile 
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to open adapter file")

        return { "cmd": self.request.path, 
                 "file-content": data_base64,
                 "file-path": path_file,
                 "file-name": name_file,
                 "file-extension": ext_file,
                 "locked": locked,
                 "locked-by": locked_by,
                 "project-id": project }
        
"""
Libraries handler
"""
class LibrariesLibraryAdd(Handler):
    """
    /rest/libraries/library/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - libraries
        summary: Add a new library
        description: ''
        operationId: librariesLibraryAdd
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
                package-name:
                  type: string
                library-name:
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
                  "cmd": "/libraries/library/add", 
                  "message": "library added"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify a package name")   

            libraryName = self.request.data.get("library-name")
            if libraryName is None: raise EmptyValue("Please specify a library name")            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = RepoLibraries.instance().addLibrary(  pathFolder=packageName, 
                                                        libraryName=libraryName, 
                                                        mainLibraries=False)
        
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to add library")
            
        return { "cmd": self.request.path, "message": "library added" }
        
class LibrariesPackageAdd(Handler):
    """
    /rest/libraries/package/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - libraries
        summary: Add a new package of libraries
        description: ''
        operationId: librariesPackageAdd
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
                package-name:
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
                  "cmd": "/libraries/package/add", 
                  "message": "package added"
                }
          '400':
            description: Bad request provided
          '401':
            description: unauthorized
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if packageName is None: raise EmptyValue("Please specify a package name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = RepoLibraries.instance().addLibrary(  pathFolder="", 
                                                        libraryName=packageName, 
                                                        mainLibraries=True  )
        
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to add package of libraries")
            
        return { "cmd": self.request.path, "message": "package added" }

class LibrariesPackageDefault(Handler):
    """
    /rest/libraries/package/default
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - libraries
        summary: set libraries package as default
        description: ''
        operationId: librariesPackageDefault
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
              required: [ package-name ]
              properties:
                package-name:
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
                  "cmd": "/libraries/package/default", 
                  "message": "success"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if not packageName: raise EmptyValue("Please specify the package name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoLibraries.instance().setDefaultV2(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as default the package %s" % packageName )

        return { "cmd": self.request.path, "message": "success"  }

class LibrariesPackageGeneric(Handler):
    """
    /rest/libraries/package/generic
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - libraries
        summary: set libraries package as generic
        description: ''
        operationId: librariesPackageGeneric
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
              required: [ package-name ]
              properties:
                package-name:
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
                  "cmd": "/libraries/package/generic", 
                  "message": "success"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error 
        """
        user_profile = _get_user(self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            packageName = self.request.data.get("package-name")
            if not packageName: raise EmptyValue("Please specify the package name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success =  RepoLibraries.instance().setGeneric(packageName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to set as generic the package %s" % packageName )
                
        return { "cmd": self.request.path, "message": "success"  }

class LibrariesCheckSyntax(Handler):
    """
    /rest/libraries/check/syntax
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - libraries
        summary: check the syntax of a library
        description: ''
        operationId: librariesCheckSyntax
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
              required: [ file-content ]
              properties:
                file-content:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                success:
                  type: boolean
                syntax-error:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/check/syntax", 
                  success:
                    type: boolean
                  syntax-error:
                    type: string
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
            fileContent = self.request.data.get("file-content")
            if fileContent is None: raise EmptyValue("Please specify a file content")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, syntaxerror = RepoLibraries.instance().checkSyntax(content=fileContent)

        return { "cmd": self.request.path, "success": success, "syntax-error": syntaxerror }

class LibrariesBuild(Handler):
    """
    /rest/libraries/build
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: build libraries
        description: ''
        operationId: librariesBuild
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
            description: libraries packaged
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/build", 
                  "message": "unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        success = Context.instance().generateLibraries()
        if not success:
            raise HTTP_500("Unable to package libraries")
            
        return { "cmd": self.request.path, "message": "packaged" }

class LibrariesListing(Handler):
    """
    /rest/libraries/listing
    """   
    @_to_yaml
    def get(self):
        """
        tags:
          - libraries
        summary: Get the listing of all libraries.
        description: ''
        operationId: librariesListing
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
            description: libraries listing
            schema :
              properties:
                cmd:
                  type: string
                libraries-listing:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/listing", 
                  "libraries-listing": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        _, _, listing, _ = RepoLibraries.instance().getTree()

        return { "cmd": self.request.path, "libraries-listing": listing }
        
class LibrariesFileMove(Handler):
    """
    /rest/libraries/file/move
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - libraries
        summary: Move file
        description: ''
        operationId: librariesFileMove
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ file-name, file-path, file-extension  ]
                  properties:
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ file-path ]
                  properties:
                    file-path:
                      type: string
        responses:
          '200':
            description: move response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/file/move", 
                  "message": "file successfully moved"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source filename")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFilePath = self.request.data.get("destination")["file-path"]
            if newFilePath is None: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoLibraries.instance().moveFile( 
                                                        mainPath=filePath, 
                                                        fileName=fileName, 
                                                        extFilename=fileExt, 
                                                        newPath=newFilePath
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Move file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file successfully moved" }
        
class LibrariesDirectoryMove(Handler):
    """
    /rest/libraries/directory/move
    """   
    @_to_yaml   
    def post(self):
        """
        tags:
          - libraries
        summary: Move directory
        description: ''
        operationId: librariesDirectoryMove
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ directory-name, directory-path  ]
                  properties:
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ directory-path ]
                  properties:
                    directory-path:
                      type: string
        responses:
          '200':
            description: move response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/directory/move", 
                  "message": "directory successfully moved"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        # checking json request on post
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")

            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if newFolderPath is None: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        if "%s/%s" % (folderPath, folderName) == newFolderPath:
            raise HTTP_403( "Destination same as origin" )
            
        # all ok, do the duplication
        success = RepoLibraries.instance().moveDir(
                                                    mainPath=folderPath, 
                                                    folderName=folderName, 
                                                    newPath=newFolderPath
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to move directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully moved"}

class LibrariesFileRename(Handler):
    """
    /rest/libraries/file/rename
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - libraries
        summary: Rename file in the libraries storage 
        description: ''
        operationId: librariesFileRename
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, file-name, file-path, file-extension  ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ project-id, file-name ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/file/rename", 
                  "message": "file successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoLibraries.instance().renameFile( 
                                                    mainPath=filePath, 
                                                    oldFilename=fileName, 
                                                    newFilename=newFileName, 
                                                    extFilename=fileExt
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Rename file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully renamed",
                 "file-path": filePath,
                 "file-name": fileName,
                 "file-extension": fileExt,
                 "new-file-name": newFileName}
        
class LibrariesDirectoryRename(Handler):
    """
    /rest/libraries/directory/rename
    """   
    @_to_yaml   
    def post(self):
        """
        tags:
          - libraries
        summary: Rename directory in the libraries storage 
        description: ''
        operationId: librariesDirectoryRename
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, directory-name, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ project-id, directory-name ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/directory/rename", 
                  "message": "directory successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoLibraries.instance().renameDir(mainPath=folderPath, oldPath=folderName, 
                                                    newPath=newFolderName)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to rename directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully renamed",
                 "directory-name": folderName, "directory-path": folderPath, 
                 "new-directory-name": newFolderName}

class LibrariesFileDuplicate(Handler):
    """
    /rest/libraries/file/duplicate
    """   
    @_to_yaml    
    def post(self):
        """
        tags:
          - libraries
        summary: Duplicate file in the libraries storage 
        description: ''
        operationId: librariesFileDuplicate
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ file-name, file-path, file-extension  ]
                  properties:
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ file-name ]
                  properties:
                    file-name:
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
                  "cmd": "/libraries/file/duplicate", 
                  "message": "file successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
            newFilePath = self.request.data.get("destination")["file-path"]
            if newFilePath is None: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoLibraries.instance().duplicateFile( 
                                                        mainPath=filePath,
                                                        oldFilename=fileName,
                                                        newFilename=newFileName,
                                                        extFilename=fileExt,
                                                        newMainPath=newFilePath
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Duplicate file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully duplicated" }
        
class LibrariesDirectoryDuplicate(Handler):
    """
    /rest/libraries/directory/duplicate
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - libraries
        summary: Duplicate directory in the libraries storage 
        description: ''
        operationId: librariesDirectoryDuplicate
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ directory-name, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ directory-name, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/directory/rename", 
                  "message": "directory successfully renamed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        # checking json request on post
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if newFolderPath is None: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        # all ok, do the duplication
        success = RepoLibraries.instance().duplicateDir(
                                                    mainPath=folderPath, 
                                                    oldPath=folderName, 
                                                    newPath=newFolderName,
                                                    newMainPath=newFolderPath
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to duplicate directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully duplicated" }

class LibrariesFileRemove(Handler):
    """
    /rest/libraries/file/remove
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - libraries
        summary: remove file in the libraries storage 
        description: ''
        operationId: librariesFileRemove
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
              required: [ file-path  ]
              properties:
                file-path:
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
                  "cmd": "/libraries/file/remove", 
                  "message": "file successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoLibraries.instance().delFile( pathFile=filePath )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove file")
        if success == Context.instance().CODE_FAILED:
            raise HTTP_403("Remove file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file successfully removed" }
        
class LibrariesFileUnlock(Handler):
    """
    /rest/libraries/file/unlock
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - libraries
        summary: unlock file in the libraries storage 
        description: ''
        operationId: librariesFileUnlock
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
              required: [ file-path, file-name, file-extension  ]
              properties:
                file-path:
                  type: string
                file-name:
                  type: string
                file-extension:
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
                  "cmd": "/libraries/file/unlock", 
                  "message": "file successfully unlocked"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a source filepath")
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a source file filename")
            fileExt = self.request.data.get("file-extension")
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success  = RepoLibraries.instance().unlockFile(pathFile=filePath, 
                                                       nameFile=fileName, 
                                                       extFile=fileExt,
                                                       login=user_profile["login"])
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to unlock library file")
            
        return { "cmd": self.request.path, "message": "file successfully unlocked" }

class LibrariesDirectoryRemove(Handler):
    """
    /rest/libraries/directory/remove
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - libraries
        summary: remove directory in the libraries storage 
        description: ''
        operationId: librariesDirectoryRemove
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
                  "cmd": "/libraries/directory/remove", 
                  "message": "directory successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )

        success = RepoLibraries.instance().delDir(folderPath)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Cannot remove directory")
                
        return { "cmd": self.request.path, "message": "directory successfully removed" }

class LibrariesDirectoryAdd(Handler):
    """
    /rest/libraries/directory/add
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - libraries
        summary: Add directory in the libraries storage 
        description: ''
        operationId: librariesDirectoryAdd
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
              required: [ directory-name, directory-path ]
              properties:
                directory-name:
                  type: string
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
                  "cmd": "/libraries/directory/add", 
                  "message": "directory successfully added"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            folderName = self.request.data.get("directory-name")
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoLibraries.instance().addDir(pathFolder=folderPath, folderName=folderName)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add directory")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully added" }

class LibrariesFileUpload(Handler):
    """
    /rest/libraries/file/upload
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - libraries
        summary: Upload file the test storage 
        description: ''
        operationId: librariesFileUpload
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
              required: [ project-id, file-path, file-name, file-extension, file-content ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
                file-name:
                  type: string
                file-extension:
                  type: string
                file-content:
                  type: string
                overwrite:
                  type: boolean
                close-after:
                  type: boolean
                add-folders:
                  type: boolean
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                code:
                  type: integer
            examples:
              application/json: |
                {
                  "cmd": "/libraries/file/upload", 
                  "code": 200
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a file name")
            fileExt = self.request.data.get("file-extension")
            if fileExt is None: raise EmptyValue("Please specify a file extension")
            fileContent = self.request.data.get("file-content")
            if fileContent is None: raise EmptyValue("Please specify a file content")
            
            _overwrite = self.request.data.get("overwrite", False)
            _closeafter = self.request.data.get("close-after", False)
            _addfolders = self.request.data.get("add-folders", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # overwrite = False
        # if _overwrite is not None:
            # overwrite = _overwrite
            
        # closeAfter = False
        # if _closeafter is not None:
            # closeAfter = _closeafter
            
        # addFolders = False
        # if _addfolders is not None:
            # addFolders = _addfolders
            
        putFileReturn = RepoLibraries.instance().uploadFile( pathFile=filePath, 
                                                             nameFile=fileName, 
                                                             extFile=fileExt, 
                                                             contentFile=fileContent, 
                                                             login=user_profile['login'], 
                                                             project='', 
                                                             overwriteFile=_overwrite,
                                                             createFolders=_addfolders,
                                                             lockMode=True, 
                                                             binaryMode=True,
                                                             closeAfter=_closeafter )
        success, pathFile, nameFile, extFile, _, overwriteFile, closeAfter, isLocked, lockedBy = putFileReturn

        return { "cmd": self.request.path, 
                 "code": success,
                 "file-path": pathFile,
                 "file-name": nameFile,
                 "file-extension": extFile,
                 "overwrite":  overwriteFile,
                 "close-after": closeAfter,
                 "locked": isLocked,
                 "locked-by": lockedBy }

class LibrariesFileDownload(Handler):
    """
    /rest/libraries/file/download
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - libraries
        summary: download file from the test storage 
        description: ''
        operationId: librariesFileDownload
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                file-content:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/file/download", 
                  "file-content": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a  project id")
            
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success, _, _, _, content, _, _ = RepoTests.instance().getFile(pathFile=filePath, 
                                                                       binaryMode=True, 
                                                                       project=projectId, 
                                                                       addLock=False)  
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to download file")

        return { "cmd": self.request.path, "file-content": content }
        
class LibrariesFileOpen(Handler):
    """
    /rest/libraries/file/open
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - libraries
        summary: open and lock file from the test storage 
        description: ''
        operationId: librariesFileOpen
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                file-content:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/libraries/file/open", 
                  "file-content": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
            
            _ignoreLock = self.request.data.get("ignore-lock", False)
            _readOnly = self.request.data.get("read-only", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # ignoreLock = False
        # if _ignoreLock is not None:
            # ignoreLock = _ignoreLock
        
        # readOnly = False
        # if _readOnly is not None:
            # _readOnly = readOnly
            
        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )

        resultGetFile = RepoLibraries.instance().getFile(pathFile=filePath,  
                                                        login=user_profile['login'],
                                                        forceOpen=_ignoreLock,
                                                        readOnly=_readOnly)
        success, path_file, name_file, ext_file, project, data_base64, locked, locked_by = resultGetFile
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to open library file")

        return { "cmd": self.request.path, 
                 "file-content": data_base64,
                 "file-path": path_file,
                 "file-name": name_file,
                 "file-extension": ext_file,
                 "locked": locked,
                 "locked-by": locked_by,
                 "project-id": project }

"""
Agents handlers
"""
class AgentsRunning(Handler):
    """
    /rest/agents/running
    """
    @_to_yaml   
    def get(self):
        """
        tags:
          - agents
        summary: Get all running agents
        description: ''
        operationId: agentsRunning
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
            description: running agents
            schema :
              properties:
                cmd:
                  type: string
                agents-running:
                  type: array
                  items:
                    type: string
            examples:
              application/json: |
                {
                  "cmd": "/agents/running", 
                  "agents-running": ...
                } 
        """
        user_profile = _get_user(request=self.request)
        
        running = AgentsManager.instance().getRunning()
        return { "cmd": self.request.path, "agents": running }
        
class AgentsDefault(Handler):
    """
    /rest/agents/default
    """
    @_to_yaml   
    def get(self):
        """
        tags:
          - agents
        summary: Get all default agents
        description: ''
        operationId: agentsDefault
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
            description: default agents
            schema :
              properties:
                cmd:
                  type: string
                agents:
                  type: array
                  items:
                    type: string
            examples:
              application/json: |
                {
                  "cmd": "/agents/default", 
                  "agents": ...
                } 
        """
        user_profile = _get_user(request=self.request)
        
        default = AgentsManager.instance().getDefaultAgents()
        return { "cmd": self.request.path, "agents": default }
       
class AgentsDisconnect(Handler):
    """
    /rest/agents/disconnect
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - agents
        summary: Disconnect a agent by the name
        description: ''
        operationId: agentsDisconnect
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
              required: [ agent-name ]
              properties:
                agent-name:
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
                  "cmd": "/agents/disconnect", 
                  "message: "agent successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Agent not found
        """
        user_profile = _get_user(request=self.request)
  
        try:
            agentName = self.request.data.get("agent-name")
            if agentName is None : raise HTTP_400("Please specify a agent name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = AgentsManager.instance().disconnectAgent(name=agentName)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("agent not found")
            
        return { "cmd": self.request.path, "message": "agent successfully disconnected" }
        
class AgentsConnect(Handler):
    """
    /rest/agents/connect
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - agents
        summary: connect a agent
        description: ''
        operationId: agentsConnect
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
              required: [ agent-name, agent-type, agent-description, agent-boot ]
              properties:
                agent-name:
                  type: string
                agent-type:
                  type: string
                agent-description:
                  type: string
                agent-boot:
                  type: boolean
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
                  "cmd": "/agents/connect", 
                  "message: "agent successfully connected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Agent not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
 
        try:
            agentName = self.request.data.get("agent-name")
            agentType = self.request.data.get("agent-type")
            agentDescription = self.request.data.get("agent-description")
            agentBoot = self.request.data.get("agent-boot")
            
            if agentName is None: raise HTTP_400("Please specify a agent name")
            if agentType is None: raise HTTP_400("Please specify a agent type")
            if agentDescription  is None: raise HTTP_400("Please specify a agent description")
            if agentBoot is None: raise HTTP_400("Please specify a agent boot")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if agentBoot:
            success = AgentsManager.instance().addDefaultAgent( aType = agentType, 
                                                                aName = agentName, 
                                                                aDescr = agentDescription)
            if success != Context.instance().CODE_OK:
                raise HTTP_500("unable to add agent before to connect it")
                
        # start the agent
        success = AgentsManager.instance().startAgent(  atype = agentType, aname = agentName, 
                                                        adescr = agentDescription,
                                                        adefault=False )
        if success != 0:
            raise HTTP_500("unable to start the agent")
            
        return { "cmd": self.request.path, "message": "agent successfully connected" }

class AgentsAdd(Handler):
    """
    /rest/agents/add
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - agents
        summary: add a agent
        description: ''
        operationId: agentsAdd
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
              required: [ agent-name, agent-type, agent-description ]
              properties:
                agent-name:
                  type: string
                agent-type:
                  type: string
                agent-description:
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
                  "cmd": "/agents/add", 
                  "message: "agent successfully added"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
            
        try:
            agentName = self.request.data.get("agent-name")
            agentType = self.request.data.get("agent-type")
            agentDescription = self.request.data.get("agent-description")

            if agentName is None: raise HTTP_400("Please specify a agent name")
            if agentType is None: raise HTTP_400("Please specify a agent type")
            if agentDescription  is None: raise HTTP_400("Please specify a agent description")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = AgentsManager.instance().addDefaultAgent( 
                                                            aType = agentType, 
                                                            aName = agentName,
                                                            aDescr = agentDescription
                                                          )
        if success != Context.instance().CODE_OK:
            raise HTTP_500("unable to add default agent")

        return { "cmd": self.request.path, "message": "agent successfully add" } 

class AgentsRemove(Handler):
    """
    /rest/agents/remove
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - agents
        summary: remove a agent
        description: ''
        operationId: agentsRemove
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
              required: [ agent-name ]
              properties:
                agent-name:
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
                  "cmd": "/agents/remove", 
                  "message: "agent successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
   
        try:
            agentName = self.request.data.get("agent-name")
            if not agentName : raise HTTP_400("Please specify a agent name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = AgentsManager.instance().delDefaultAgent( aName = agentName )
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to remove default agent")
            
        return { "cmd": self.request.path, "message": "agent successfully removed" } 

"""
Probes handlers
"""
class ProbesRunning(Handler):
    """
    /rest/probes/running
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - probes
        summary: Get all running probes
        description: ''
        operationId: probesRunning
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
            description: running probes
            schema :
              properties:
                cmd:
                  type: string
                probes:
                  type: array
                  items:
                    type: string
            examples:
              application/json: |
                {
                  "cmd": "/probes/running", 
                  "probes": ...
                }
        """
        user_profile = _get_user(request=self.request)
        
        running = ProbesManager.instance().getRunning()
        return { "cmd": self.request.path, "probes": running }
        
class ProbesDefault(Handler):
    """
    /rest/probes/default
    """
    @_to_yaml    
    def get(self):
        """
        tags:
          - probes
        summary: Get all default probes
        description: ''
        operationId: probesDefault
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
            description: default probes
            schema :
              properties:
                cmd:
                  type: string
                probes:
                  type: array
                  items:
                    type: string
            examples:
              application/json: |
                {
                  "cmd": "/probes/default", 
                  "probes": ...
                }
        """
        user_profile = _get_user(request=self.request)
        
        default = ProbesManager.instance().getDefaultProbes()
        return { "cmd": self.request.path, "probes": default }
        
class ProbesDisconnect(Handler):
    """
    /rest/probes/disconnect
    """
    @_to_yaml     
    def post(self):
        """
        tags:
          - probes
        summary: Disconnect a probe by the name
        description: ''
        operationId: probesDisconnect
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
              required: [ probe-name ]
              properties:
                probe-name:
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
                  "cmd": "/probes/disconnect", 
                  "message: "probe successfully disconnected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
        """
        user_profile = _get_user(request=self.request)
   
        try:
            probeName = self.request.data.get("probe-name")
            if probeName is None: raise HTTP_400("Please specify a probe name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = ProbesManager.instance().disconnectProbe(name=probeName)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("probe not found")
            
        return { "cmd": self.request.path, "message": "probe successfully disconnected" }
        
class ProbesConnect(Handler):
    """
    /rest/probes/connect
    """
    @_to_yaml   
    def post(self):
        """
        tags:
          - probes
        summary: connect a probe
        description: ''
        operationId: probesConnect
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
              required: [ probe-name, probe-type, probe-description, probe-boot ]
              properties:
                probe-name:
                  type: string
                probe-type:
                  type: string
                probe-description:
                  type: string
                probe-boot:
                  type: boolean
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
                  "cmd": "/probes/connect", 
                  "message: "probe successfully connected"
                }
          '400':
            description: Bad request provided
          '404':
            description: Probe not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
 
        try:
            probeName = self.request.data.get("probe-name")
            probeType = self.request.data.get("probe-type")
            probeDescription = self.request.data.get("probe-description")
            probeBoot = self.request.data.get("probe-boot")
            
            if probeName is None: raise HTTP_400("Please specify a probe name")
            if probeType is None: raise HTTP_400("Please specify a probe type")
            if probeDescription  is None: raise HTTP_400("Please specify a probe description")
            if probeBoot is None: raise HTTP_400("Please specify a probe boot")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if probeBoot:
            success = ProbesManager.instance().addDefaultProbe( pType = probeType, 
                                                                pName = probeName, 
                                                                pDescr = probeDescription)
            if success != Context.instance().CODE_OK:
                raise HTTP_500("unable to add probe before to connect it")
                
        # start the probe
        success = ProbesManager.instance().startProbe(  ptype = probeType, pname = probeName, 
                                                        pdescr = probeDescription,
                                                        pdefault=False )
        if success != 0:
            raise HTTP_500("unable to start the probe")
            
        return { "cmd": self.request.path, "message": "probe successfully connected" }

class ProbesAdd(Handler):
    """
    /rest/probes/add
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - probes
        summary: add a probe
        description: ''
        operationId: probesAdd
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
              required: [ probe-name, probe-type, probe-description ]
              properties:
                probe-name:
                  type: string
                probe-type:
                  type: string
                probe-description:
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
                  "cmd": "/probes/add", 
                  "message: "probe successfully added"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
 
        try:
            probeName = self.request.data.get("probe-name")
            probeType = self.request.data.get("probe-type")
            probeDescription = self.request.data.get("probe-description")

            if probeName is None: raise HTTP_400("Please specify a probe name")
            if probeType is None: raise HTTP_400("Please specify a probe type")
            if probeDescription  is None: raise HTTP_400("Please specify a probe description")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = ProbesManager.instance().addDefaultProbe( pType = probeType, 
                                                            pName = probeName, 
                                                            pDescr = probeDescription)
        if success != Context.instance().CODE_OK:
            raise HTTP_500("unable to add default probe")
            
        return { "cmd": self.request.path, "message": "probe successfully added" } 
         
class ProbesRemove(Handler):
    """
    /rest/probes/remove
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - probes
        summary: remove a probe
        description: ''
        operationId: probesRemove
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
              required: [ probe-name ]
              properties:
                probe-name:
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
                  "cmd": "/probes/remove", 
                  "message: "probe successfully removed"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
  
        try:
            probeName = self.request.data.get("probe-name")
            if not probeName : raise HTTP_400("Please specify a probe name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success = ProbesManager.instance().delDefaultProbe( pName = probeName )
        if success != Context.instance().CODE_OK:
            raise HTTP_500("unable to remove default probe")
            
        return { "cmd": self.request.path, "message": "probe successfully removed" } 

    
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
          - public
        summary: Get the listing of all files and folders in the public area
        description: ''
        operationId: publicListing
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
                  items:
                    type: string
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
          - public
        summary: Add directory in the public storage
        description: ''
        operationId: publicDirectoryAdd
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
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
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
          - public
        summary: Rename directory name in the public storage
        description: ''
        operationId: publicDirectoryRename
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
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
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
          - public
        summary: Remove directory in the public storage and their contents recursively
        description: ''
        operationId: publicDirectoryRemove
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
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            _recursive = self.request.data.get("recursive", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # if _recursive is None:
            # recursive = False
        # else:
            # recursive = _recursive

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        if _recursive:
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
          - public
        summary: Import file to the public storage. Provide the file in base64 format
        description: ''
        operationId: publicFileImport
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
            if not filePath and not fileContent:
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
    /rest/public/file/remove
    """  
    def post(self):
        """
        tags:
          - public
        summary: Import file to the public storage. Provide the file in base64 format
        description: ''
        operationId: publicFileRemove
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
            if filePath is None:raise EmptyValue("Please specify a project name and file path")
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
    /rest/public/file/rename
    """ 
    def post(self):
        """
        tags:
          - public
        summary: Import file to the public storage. Provide the file in base64 format
        description: ''
        operationId: publicFileRename
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
            fileName = self.request.data.get("source")["file-path"]
            if fileName is None: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-name"]
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
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
    /rest/public/file/download
    """   
    def post(self):
        """
        tags:
          - public
        summary: Import file to the public storage. Provide the file in base64 format
        description: ''
        operationId: publicFileDownload
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
            if filePath is None: raise EmptyValue("Please specify a project name and file path")
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
Tests handlers
"""
class TestsBasicListing(Handler):
    """
    /rest/tests/basic/listing
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Get the listing of all tests in basic mode.
        description: ''
        operationId: testsBasicListing
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
            schema :
              properties:
                cmd:
                  type: string
                listing:
                  type: array
                  items:
                    type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/basic/listing", 
                  "listing": ["/Snippets/UI/03_OpenBrowser.tux", "/Snippets/UI/05_MaximizeBrowser.tux"],
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
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        listing = RepoTests.instance().getBasicListing(projectId=projectId)  
        
        return { "cmd": self.request.path, "listing": listing, "project-id": projectId }

class TestsScheduleGroup(Handler):
    """
    /rest/tests/schedule/group
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Schedule a group of tests
        description: ''
        operationId: testsScheduleGroup
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
              required: [ tests, postpone-at, parallel-mode, postpone-mode]
              properties:
                tests:
                  type: array
                  items:
                    type: string
                postpone-at:
                  type: array
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                parallel-mode:
                  type: boolean
                postpone-mode:
                  type: boolean
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
                  "cmd": "/tests/schedule/group", 
                  "message": "success"
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
            postponeAt = self.request.data.get("postpone-at")
            if postponeAt is None: raise EmptyValue("Please specify a postpone at")
            
            postponeMode = self.request.data.get("postpone-mode")
            if postponeMode is None: raise EmptyValue("Please specify a postpone mode")
            
            tests = self.request.data.get("tests")
            if tests is None: raise EmptyValue("Please specify tests")
            
            parallel = self.request.data.get("parallel-mode")
            if parallel is None: raise EmptyValue("Please specify parallel-mode")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        if len(postponeAt) != 6:
            raise HTTP_400("Bad schedule-at provided in request, array of size 6 expected")
            
        testsRun = []
        for t in tests:
            try:
                prjName, absPath = t.split(':', 1)
            except Exception as e:
                raise HTTP_500("Unable to extract project name: %s" % str(e))

            prjID = ProjectsManager.instance().getProjectID(name=prjName)
            testPath, testExtension = absPath.rsplit('.', 1)
            if len(testPath.rsplit('/', 1)) > 1:
                testName = testPath.rsplit('/', 1)[1]
            else:
                testName = testPath.rsplit('/', 1)[0]

            if testExtension == 'tsx':
                doc = TestSuite.DataModel()
                res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, prjID, 
                                                           testPath, testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test suite: %s' % testPath)

                testData = { 'test-definition': doc.testdef, 
                             'test-execution': doc.testexec, 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
                testsRun.append( {  'prj-id': prjID, 
                                    'test-extension': testExtension, 
                                    'test-name': testName,
                                    'test-path': testPath, 'test-data': testData } )

            elif testExtension == 'tux':
                doc = TestUnit.DataModel()
                res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           prjID, testPath, testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test unit: %s' % testPath)

                testData = { 'test-definition': doc.testdef, 
                             'test-execution': '', 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
                testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension,
                                    'test-name': testName,
                                    'test-path': testPath, 'test-data': testData } )
            
            elif testExtension == 'tax':
                doc = TestAbstract.DataModel()
                res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           prjID, testPath, testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test abstract: %s' % testPath)

                testData = { 'test-definition': doc.testdef, 
                             'test-execution': '', 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
                testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 
                                    'test-name': testName,
                                    'test-path': testPath, 'test-data': testData } )
                                        
            elif testExtension == 'tpx':
                doc = TestPlan.DataModel()
                res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           prjID, testPath, testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test plan: %s' % testPath)

                tests = doc.getSorted()
                success, error_msg = RepoTests.instance().addtf2tp( data_=tests )
                if success != Context.instance().CODE_OK:
                    raise HTTP_500('Unable to prepare test plan: %s' % error_msg )

                testData = { 'test-execution': doc.getSorted(), 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
                testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 
                                    'test-name': testName, 
                                    'test-path': testPath, 'test-data': testData } )

            elif testExtension == 'tgx':
                doc = TestPlan.DataModel()
                res = doc.load( absPath = "%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           prjID, testPath, testExtension) )
                if not res:
                     raise HTTP_500('Unable to read test global: %s' % testPath)

                alltests = doc.getSorted()
                success, error_msg, alltests = RepoTests.instance().addtf2tg( data_= alltests )
                if success != Context.instance().CODE_OK:
                    raise HTTP_500('Unable to prepare test global: %s' % error_msg)

                testData = { 'test-execution': alltests, 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
                testsRun.append( {  'prj-id': prjID, 'test-extension': testExtension, 
                                    'test-name': testName,
                                    'test-path': testPath, 'test-data': testData } )
            
            else:
                raise HTTP_500('test extension not supported: %s' % testExtension)

        if len(testsRun):
            success = TaskManager.instance().addTasks(userName=user_profile['login'], 
                                                      tests=testsRun, 
                                                      runAt=postponeAt,
                                                      queueAt=postponeMode, 
                                                      simultaneous=parallel )
            if not success:
                raise HTTP_500('Unable to run the group of tests')
        else:
            raise HTTP_500('No tests provided')
            
        return { "cmd": self.request.path, "message": "success" }
          
class TestsSchedule(Handler):
    """
    /rest/tests/schedule
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Schedule a test unit/suite or abstract
        description: ''
        operationId: testsSchedule
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
              required: [ project-id, test-extension, test-path, test-name]
              properties:
                project-id:
                  type: integer
                test-definition:
                  type: string
                test-execution:
                  type: string 
                test-properties:
                  type: object 
                test-extension:
                  type: string 
                test-path:
                  type: string 
                test-name:
                  type: string
                schedule-id:
                  type: integer
                  description: '0 => now, 1 => at, 2 => in'
                schedule-at:
                  type: array
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                schedule-repeat:
                  type: integer
                probes-enabled:
                  type: boolean 
                debug-enabled:
                  type: boolean 
                notifications-enabled:
                  type: boolean 
                logs-enabled:
                  type: boolean 
                from-time:
                  type: array
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                to-time:
                  type: array 
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                tab-id:
                  type: integer
                step-mode:
                  type: boolean 
                breakpoint-mode:
                  type: boolean 
                background-mode:
                  type: boolean
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
                test-libraries:
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
        responses:
          '200':
            description: tests listing
            schema :
              properties:
                cmd:
                  type: string
                test-id:
                  type: string
                task-id:
                  type: string
                tab-id:
                  type: string
                test-name:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/schedule",
                  "message": ""
                  "test-id": "",
                  "task-id": "",
                  "tab-id": ""
                  "test-name": ""
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
            if projectId is None: raise EmptyValue("Please specify a project id")

            testDefinition = self.request.data.get("test-definition")
            if testDefinition is None: testDefinition = ""
            
            testExecution = self.request.data.get("test-execution")
            if testExecution is None: testExecution = ""
            
            testProperties = self.request.data.get("test-properties")
            if testProperties is None: testProperties = {}
            
            testExtension = self.request.data.get("test-extension")
            if testExtension is None: raise EmptyValue("Please specify a test extension")
            
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            
            scheduleId = self.request.data.get("schedule-id")
            if scheduleId is None : scheduleId = 0
            
            _scheduleAt = self.request.data.get("schedule-at")  
            _scheduleRepeat = self.request.data.get("schedule-repeat", 0)
            _tabId = self.request.data.get("tab-id")
            _backgroundMode = self.request.data.get("background-mode")
            _stepMode = self.request.data.get("step-mode")
            _breakpointMode = self.request.data.get("breakpoint-mode")
            _probesEnabled = self.request.data.get("probes-enabled")
            _notificationsEnabled = self.request.data.get("notifications-enabled")
            _logsEnabled = self.request.data.get("logs-enabled")
            _debugEnabled = self.request.data.get("debug-enabled")
            _fromTime = self.request.data.get("from-time")
            _toTime = self.request.data.get("to-time")
            
            _sutAdapters = self.request.data.get("test-adapters")
            _sutLibraries = self.request.data.get("test-libraries")
            _testInputs = self.request.data.get("test-inputs")
            _testOutputs = self.request.data.get("test-outputs")
            _testAgents = self.request.data.get("test-agents")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
        if not isinstance(scheduleId, int):
            raise HTTP_400("Bad schedule id provided in request, int expected")

        if _testInputs is not None:
            if not isinstance(_testInputs, list): 
                raise HTTP_400("Bad test inputs provided in request, list expected")
            for inp in _testInputs:
                if not isinstance(inp, dict):     
                    raise HTTP_400("Bad test inputs provided in request, list of dict expected")
                if not ( "name" in inp and "type" in inp and "value" in inp ):
                    raise HTTP_400("Bad test format inputs provided in request")
                    
        if _testOutputs is not None:
            if not isinstance(_testOutputs, list): 
                raise HTTP_400("Bad test outputs provided in request, list expected")
            for out in _testOutputs:
                if not isinstance(out, dict):     
                    raise HTTP_400("Bad test outputs provided in request, list of dict expected")
                if not ( "name" in out and "type" in out and "value" in out ):
                    raise HTTP_400("Bad test format outputs provided in request")
                    
        if _testAgents is not None:
            if not isinstance(_testAgents, list): 
                raise HTTP_400("Bad test agents provided in request, list expected")
            for agt in _testAgents:
                if not isinstance(agt, dict):     
                    raise HTTP_400("Bad test agents provided in request, list of dict expected")
                if not ( "name" in agt and "type" in agt and "value" in agt ):
                    raise HTTP_400("Bad test format agents provided in request")

        if _sutAdapters is not None:
            if not isinstance(_sutAdapters, str): 
                raise HTTP_400("Bad sut adapter provided in request, str expected")
        
        if _sutLibraries is not None:
            if not isinstance(_sutLibraries, str): 
                raise HTTP_400("Bad sut library provided in request, str expected")
                
        # find if the user is connected on the channel too
        channelId=False
        channel = Context.instance().getUser(user_profile["login"])
        if channel is not None: channelId = list(channel['address'])
            
        #run a test not save; change the project id to the default
        if projectId == 0: 
            projectId = ProjectsManager.instance().getDefaultProjectForUser(user=user_profile['login'])
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # no test content provided
        if not len(testDefinition) and not len(testExecution) and not len(testProperties): 
            if testExtension == 'tsx':
                doc = TestSuite.DataModel()
                res = doc.load( absPath = "%s/%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           projectId, 
                                                           testPath, 
                                                           testName,
                                                           testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test suite: %s' % testPath)

                testData = { 'test-definition': doc.testdef, 
                             'test-execution': doc.testexec, 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension 
                             }

            elif testExtension == 'tux':
                doc = TestUnit.DataModel()
                res = doc.load( absPath = "%s/%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           projectId, 
                                                           testPath,  
                                                           testName,
                                                           testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test unit: %s' % testPath)
                    
                testData = { 'test-definition': doc.testdef, 
                             'test-properties': '', 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension  }
            
            elif testExtension == 'tax':
                doc = TestAbstract.DataModel()
                res = doc.load( absPath = "%s/%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           projectId, 
                                                           testPath,  
                                                           testName,
                                                           testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test abstract: %s' % testPath)
                    
                testData = { 'test-definition': doc.testdef, 
                             'test-execution': '', 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension  }
            else:
                raise HTTP_403('Test extension not supported: %s' % testExtension)
        
        else:
            if testExtension == 'tsx':
                testData = { 'test-definition': testDefinition, 
                             'test-execution': testExecution, 
                             'test-properties': testProperties,
                             'test-extension': testExtension  }
                
            elif testExtension == 'tux':
                testData = { 'test-definition': testDefinition, 
                             'test-execution': '', 
                             'test-properties': testProperties,
                             'test-extension': testExtension  }  
                
            elif testExtension == 'tax':
                testData = { 'test-definition': testDefinition, 
                             'test-execution': '', 
                             'test-properties': testProperties,
                             'test-extension': testExtension  }  
                             
            else:
                raise HTTP_403('Test extension not supported: %s' % testExtension)
                
        tabId = 0
        backgroundMode = True
        stepMode = False
        breakpointMode = False
        notificationsEnabled = False
        logsEnabled = True
        debugEnabled = False
        probesEnabled = False
        fromTime = (0,0,0,0,0,0)
        toTime = (0,0,0,0,0,0)
        message = "success"
        # scheduleRepeat = 0
        scheduleAt = (0,0,0,0,0,0)
        
        # if _scheduleRepeat is not None: scheduleRepeat = _scheduleRepeat
        if _tabId is not None: tabId = _tabId
        if _backgroundMode is not None: backgroundMode=_backgroundMode
        if _stepMode is not None: stepMode=_stepMode
        if _breakpointMode is not None: breakpointMode=_breakpointMode
        if _notificationsEnabled is not None: notificationsEnabled=_notificationsEnabled
        if _logsEnabled is not None: logsEnabled=_logsEnabled
        if _debugEnabled is not None: debugEnabled=_debugEnabled
        if _probesEnabled is not None: probesEnabled=_probesEnabled
        if _fromTime is not None: fromTime=_fromTime
        if _toTime is not None: toTime=_toTime
        if _scheduleAt is not None: scheduleAt=_scheduleAt
        
        # personalize test description ?
        if _sutAdapters is not None:
            for origDescr in testData["test-properties"]["description"]:
                if origDescr["key"] == "adapters":
                    origDescr["value"] = _sutAdapters
                    
        if _sutLibraries is not None:
            for origDescr in testData["test-properties"]["description"]:
                if origDescr["key"] == "libraries":
                    origDescr["value"] = _sutLibraries

        if _testInputs is not None:
            for newInp in _testInputs:
                if "scope" not in newInp: newInp["scope"] = "local"
                for origInp in testData["test-properties"]['inputs-parameters']['parameter']:
                    if "scope" not in origInp: origInp["scope"] = "local"
                    
                    # if the param exist on the original test than overwrite them
                    if newInp["name"] == origInp["name"]:
                        origInp["value"] = newInp["value"]
                        origInp["type"] = newInp["type"]
                        origInp["scope"] = newInp["scope"]
                        
        if _testOutputs is not None:
            for newOut in _testOutputs:
                if "scope" not in newOut: newOut["scope"] = "local"
                for origOut in testData["test-properties"]['outputs-parameters']['parameter']:
                    if "scope" not in origOut: origOut["scope"] = "local"
                    
                    # if the param exist on the original test than overwrite them
                    if newOut["name"] == origOut["name"]:
                        origOut["value"] = newOut["value"]
                        origOut["type"] = newOut["type"]
                        origOut["scope"] = newOut["scope"]
                        
        if _testAgents is not None:
            for newAgt in _testAgents:
                for origAgt in testData["test-properties"]["agents"]["agent"]:
                    # if the param exist on the original test than overwrite them
                    if newAgt["name"] == origAgt["name"]:
                        origAgt["value"] = newAgt["value"]
                        origAgt["type"] = newAgt["type"]
        
        if not testPath.endswith(testName):
            _testPath = "%s/%s" % (testPath, testName)
            _testPath = os.path.normpath(_testPath)
        else:
            _testPath = testPath
            
        task = TaskManager.instance().registerTask( 
                                                testData=testData, 
                                                testName=testName, 
                                                testPath=_testPath, 
                                                testUserId=user_profile['id'],
                                                testUser=user_profile['login'],
                                                testId=tabId, 
                                                testBackground=backgroundMode,
                                                runAt=scheduleAt, 
                                                runType=scheduleId, 
                                                runNb=_scheduleRepeat, 
                                                withoutProbes=probesEnabled,
                                                debugActivated=debugEnabled, 
                                                withoutNotif=notificationsEnabled, 
                                                noKeepTr=not logsEnabled,
                                                testProjectId=projectId, 
                                                runFrom=fromTime, 
                                                runTo=toTime, 
                                                stepByStep=stepMode, 
                                                breakpoint=breakpointMode, 
                                                channelId=channelId
                                            )
  
        if task.lastError is not None:
            raise HTTP_500('ERROR: %s' % task.lastError)
  
        if task.isRecursive(): message = "recursive"
        if task.isRecursive() and backgroundMode: message = "recursive-background"
        if task.isPostponed(): message = "postponed"
        if task.isPostponed() and backgroundMode: message = "postponed-background"
        if task.isSuccessive(): message = "successive"
        if task.isSuccessive() and backgroundMode: message = "successive-background"
        if not task.isSuccessive() and not task.isPostponed() and not task.isRecursive() and backgroundMode:
            message = "background"
        
        return { "cmd": self.request.path, 
                 "message": message,
                 "task-id": task.getId(),
                 "test-id": task.getTestID(),
                 "tab-id": tabId,
                 "test-name": testName
               }
               
class TestsScheduleTpg(Handler):
    """
    /rest/tests/schedule/tpg
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Schedule a testplan or test global
        description: ''
        operationId: testsScheduleTpg
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
              required: [ project-id, test-extension, test-path, test-name]
              properties:
                project-id:
                  type: integer
                test-execution:
                  type: string 
                test-properties:
                  type: object 
                test-extension:
                  type: string 
                test-path:
                  type: string 
                test-name:
                  type: string
                schedule-id:
                  type: integer
                  description: '0 => now, 1 => at, 2 => in'
                schedule-at:
                  type: array
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                schedule-repeat:
                  type: integer
                probes-enabled:
                  type: boolean 
                debug-enabled:
                  type: boolean 
                notifications-enabled:
                  type: boolean 
                logs-enabled:
                  type: boolean 
                from-time:
                  type: array
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                to-time:
                  type: array 
                  description: '[ Y,M,D,H,M,S ]'
                  items:
                    type: integer
                tab-id:
                  type: integer
                step-mode:
                  type: boolean 
                breakpoint-mode:
                  type: boolean 
                background-mode:
                  type: boolean
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
                test-libraries:
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
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                test-id:
                  type: string
                task-id:
                  type: string
                tab-id:
                  type: string
                test-name:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/schedule/tpg"
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
            if projectId is None: raise EmptyValue("Please specify a project id")

            testExecution = self.request.data.get("test-execution")
            if testExecution is None: testExecution = ""
            
            testProperties = self.request.data.get("test-properties")
            if testProperties is None: testProperties = {}
            
            testExtension = self.request.data.get("test-extension")
            if testExtension is None: raise EmptyValue("Please specify a test extension")
            
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            
            scheduleId = self.request.data.get("schedule-id")
            if scheduleId is None : scheduleId = 0
            
            _scheduleAt = self.request.data.get("schedule-at")
            _scheduleRepeat = self.request.data.get("schedule-repeat", 0)
            _tabId = self.request.data.get("tab-id")
            _backgroundMode = self.request.data.get("background-mode")
            _stepMode = self.request.data.get("step-mode")
            _breakpointMode = self.request.data.get("breakpoint-mode")
            _probesEnabled = self.request.data.get("probes-enabled")
            _notificationsEnabled = self.request.data.get("notifications-enabled")
            _logsEnabled = self.request.data.get("logs-enabled")
            _debugEnabled = self.request.data.get("debug-enabled")
            _fromTime = self.request.data.get("from-time")
            _toTime = self.request.data.get("to-time")
            
            _sutAdapters = self.request.data.get("test-adapters")
            _sutLibraries = self.request.data.get("test-libraries")
            _testInputs = self.request.data.get("test-inputs")
            _testOutputs = self.request.data.get("test-outputs")
            _testAgents = self.request.data.get("test-agents")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # checking input    
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")
        if not isinstance(scheduleId, int):
            raise HTTP_400("Bad schedule id provided in request, int expected")

        if _testInputs is not None:
            if not isinstance(_testInputs, list): 
                raise HTTP_400("Bad test inputs provided in request, list expected")
            for inp in _testInputs:
                if not isinstance(inp, dict):     
                    raise HTTP_400("Bad test inputs provided in request, list of dict expected")
                if not ( "name" in inp and "type" in inp and "value" in inp ):
                    raise HTTP_400("Bad test format inputs provided in request")
                    
        if _testOutputs is not None:
            if not isinstance(_testOutputs, list): 
                raise HTTP_400("Bad test outputs provided in request, list expected")
            for out in _testOutputs:
                if not isinstance(out, dict):     
                    raise HTTP_400("Bad test outputs provided in request, list of dict expected")
                if not ( "name" in out and "type" in out and "value" in out ):
                    raise HTTP_400("Bad test format outputs provided in request")
                    
        if _testAgents is not None:
            if not isinstance(_testAgents, list): 
                raise HTTP_400("Bad test agents provided in request, list expected")
            for agt in _testAgents:
                if not isinstance(agt, dict):     
                    raise HTTP_400("Bad test agents provided in request, list of dict expected")
                if not ( "name" in agt and "type" in agt and "value" in agt ):
                    raise HTTP_400("Bad test format agents provided in request")

        if _sutAdapters is not None:
            if not isinstance(_sutAdapters, str): 
                raise HTTP_400("Bad sut adapter provided in request, str expected")
        
        if _sutLibraries is not None:
            if not isinstance(_sutLibraries, str): 
                raise HTTP_400("Bad sut library provided in request, str expected")
                
        # find if the user is connected on the channel too
        channelId=False
        channel = Context.instance().getUser(user_profile["login"])
        if channel is not None: channelId = list(channel['address'])
            
        #run a test not save; change the project id to the default
        if projectId == 0: 
            projectId = ProjectsManager.instance().getDefaultProjectForUser(user=user_profile['login'])
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # no test content provided
        if not len(testExecution) and not len(testProperties): 
            if testExtension == 'tpx':
                doc = TestPlan.DataModel()
                res = doc.load( absPath = "%s/%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           projectId, 
                                                           testPath,  
                                                           testName,
                                                           testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test plan: %s' % testPath)
                    
                tests = doc.getSorted()
                success, error_msg = RepoTests.instance().addtf2tp( data_=tests )
                if success != Context.instance().CODE_OK:
                    raise HTTP_500('Unable to prepare test plan: %s' % error_msg )

                testData = { 'test-execution': tests,  
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
            
            elif testExtension == 'tgx':
                doc = TestPlan.DataModel()
                res = doc.load( absPath = "%s/%s/%s/%s.%s" % (RepoTests.instance().testsPath, 
                                                           projectId, 
                                                           testPath,  
                                                           testName,
                                                           testExtension) )
                if not res:
                    raise HTTP_500('Unable to read test global: %s' % testPath)
                    
                alltests = doc.getSorted()
                success, error_msg, alltests = RepoTests.instance().addtf2tg( data_= alltests )
                if success != Context.instance().CODE_OK:
                    raise HTTP_500('Unable to prepare test global: %s' % error_msg)
                
                testData = { 'test-execution': alltests, 
                             'test-properties': doc.properties['properties'],
                             'test-extension': testExtension }
            else:
                raise HTTP_403('Test extension not supported: %s' % testExtension)
        
        else:
            if testExtension == 'tpx':
                success, error_msg = RepoTests.instance().addtf2tp( data_=testExecution )
                if success != Context.instance().CODE_OK:
                    raise HTTP_500('Unable to prepare test plan: %s' % error_msg )

                testData = { 'test-definition': '',
                             'test-execution': testExecution, 
                             'test-properties': testProperties,
                             'test-extension': testExtension  }

            elif testExtension == 'tgx':
                success, error_msg, testExecution = RepoTests.instance().addtf2tg( data_=testExecution )
                if success != Context.instance().CODE_OK:
                    raise HTTP_500('Unable to prepare test global: %s' % error_msg )
                
                testData = { 'test-definition': '', 
                             'test-execution': testExecution, 
                             'test-properties': testProperties,
                             'test-extension': testExtension } 
                             
            else:
                raise HTTP_403('Test extension not supported: %s' % testExtension)
                
        tabId = 0
        backgroundMode = True
        stepMode = False
        breakpointMode = False
        notificationsEnabled = False
        logsEnabled = True
        debugEnabled = False
        probesEnabled = False
        fromTime = (0,0,0,0,0,0)
        toTime = (0,0,0,0,0,0)
        scheduleAt = (0,0,0,0,0,0)
        message = "success" 
        # scheduleRepeat = 0

        # if _scheduleRepeat is not None: scheduleRepeat = _scheduleRepeat
        if _tabId is not None: tabId = _tabId
        if _backgroundMode is not None: backgroundMode=_backgroundMode
        if _stepMode is not None: stepMode=_stepMode
        if _breakpointMode is not None: breakpointMode=_breakpointMode
        if _notificationsEnabled is not None: notificationsEnabled=_notificationsEnabled
        if _logsEnabled is not None: logsEnabled=_logsEnabled
        if _debugEnabled is not None: debugEnabled=_debugEnabled
        if _probesEnabled is not None: probesEnabled=_probesEnabled
        if _fromTime is not None: fromTime=_fromTime
        if _toTime is not None: toTime=_toTime
        if _scheduleAt is not None: scheduleAt=_scheduleAt
        
        # personalize test description ?
        if _sutAdapters is not None:
            for origDescr in testData["test-properties"]["description"]:
                if origDescr["key"] == "adapters":
                    origDescr["value"] = _sutAdapters
                    
        if _sutLibraries is not None:
            for origDescr in testData["test-properties"]["description"]:
                if origDescr["key"] == "libraries":
                    origDescr["value"] = _sutLibraries

        if _testInputs is not None:
            for newInp in _testInputs:
                for origInp in testData["test-properties"]['inputs-parameters']['parameter']:
                    # if the param exist on the original test than overwrite them
                    if newInp["name"] == origInp["name"]:
                        origInp["value"] = newInp["value"]
                        origInp["type"] = newInp["type"]
                        origInp["scope"] = newInp["scope"]
                        
        if _testOutputs is not None:
            for newOut in _testOutputs:
                for origOut in testData["test-properties"]['outputs-parameters']['parameter']:
                    # if the param exist on the original test than overwrite them
                    if newOut["name"] == origOut["name"]:
                        origOut["value"] = newOut["value"]
                        origOut["type"] = newOut["type"]
                        origOut["scope"] = newOut["scope"]
                        
        if _testAgents is not None:
            for newAgt in _testAgents:
                for origAgt in testData["test-properties"]["agents"]["agent"]:
                    # if the param exist on the original test than overwrite them
                    if newAgt["name"] == origAgt["name"]:
                        origAgt["value"] = newAgt["value"]
                        origAgt["type"] = newAgt["type"]
        
        if not testPath.endswith(testName):            
            _testPath = "%s/%s" % (testPath, testName)
            _testPath = os.path.normpath(_testPath)
        else:
            _testPath = testPath
            
        task = TaskManager.instance().registerTask( 
                                                testData=testData, 
                                                testName=testName, 
                                                testPath=_testPath, 
                                                testUserId=user_profile['id'],
                                                testUser=user_profile['login'],
                                                testId=tabId, 
                                                testBackground=backgroundMode,
                                                runAt=scheduleAt, 
                                                runType=scheduleId, 
                                                runNb=_scheduleRepeat, 
                                                withoutProbes=probesEnabled,
                                                debugActivated=debugEnabled, 
                                                withoutNotif=notificationsEnabled, 
                                                noKeepTr=not logsEnabled,
                                                testProjectId=projectId, 
                                                runFrom=fromTime, 
                                                runTo=toTime, 
                                                stepByStep=stepMode, 
                                                breakpoint=breakpointMode, 
                                                channelId=channelId
                                            )
  
        if task.lastError is not None:
            raise HTTP_500('Unable to run the test: %s' % task.lastError)
  
        if task.isRecursive(): message = "recursive"
        if task.isRecursive() and backgroundMode: message = "recursive-background"
        if task.isPostponed(): message = "postponed"
        if task.isPostponed() and backgroundMode: message = "postponed-background"
        if task.isSuccessive(): message = "successive"
        if task.isSuccessive() and backgroundMode: message = "successive-background"
        if not task.isSuccessive() and not task.isPostponed() and not task.isRecursive() and backgroundMode:
            message = "background"
        
        return { "cmd": self.request.path, 
                 "message": message,
                 "task-id": task.getId(),
                 "test-id": task.getTestID(),
                 "tab-id": tabId,
                 "test-name": testName
               }
               
class TestsListing(Handler):
    """
    /rest/tests/listing
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Get the listing of all tests.
        description: ''
        operationId: testsListing
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
                for-saveas:
                  type: boolean
                for-runs:
                  type: boolean
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                listing:
                  type: array
                  items:
                    type: string
                project-id:
                  type: integer
            examples:
              application/json: |
                {
                  "cmd": "/tests/listing", 
                  "listing": [],
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
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            _forsaveas = self.request.data.get("for-saveas", False)
            _forruns = self.request.data.get("for-runs", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        _, _, listing, _ = RepoTests.instance().getTree(project=projectId)

        return { "cmd": self.request.path, "listing": listing, "project-id": projectId, 
                 "for-saveas": _forsaveas, "for-runs": _forruns }

class TestsCheckSyntax(Handler):
    """
    /rest/tests/check/syntax
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: check the syntax of a test (unit, abstract and suite)
        description: ''
        operationId: testsCheckSyntax
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
              required: [ test-definition, test-execution, test-properties, test-name, test-path, test-extension ]
              properties:
                test-definition:
                  type: string
                test-execution:
                  type: string
                test-properties:
                  type: string
                test-name:
                  type: string
                test-path:
                  type: string
                test-extension:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                status:
                  type: boolean
                error-msg:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/check/syntax/string", 
                  "status": True,
                  "error-msg": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            testDefinition = self.request.data.get("test-definition")
            if testDefinition is None: raise EmptyValue("Please specify a test definition")
            
            testExecution = self.request.data.get("test-execution")
            if testExecution is None: raise EmptyValue("Please specify a test execution")
            
            testProperties = self.request.data.get("test-properties")
            if testProperties is None: raise EmptyValue("Please specify a test properties")
            
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            
            testExtension = self.request.data.get("test-extension")
            if testExtension is None: raise EmptyValue("Please specify a test extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if testExtension not in [ "tax", "tux", "tsx" ]:
            raise HTTP_400("Bad test extension provided (%s)" % testExtension)
            
        task = TaskManager.getObjectTask(   
                                            testData=self.request.data, testName=testName, 
                                            testPath=testPath,  testUser=user_profile["login"], 
                                            testId=0, testBackground=False ,
                                            statsmgr=StatsManager.instance(),
                                            context=Context
                                        )
        status, error_msg = task.parseTest()        
        del task

        return { "cmd": self.request.path, "status": status, "error": error_msg }
        
class TestsCheckSyntaxTpg(Handler):
    """
    /rest/tests/check/syntax/tpg
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: check the syntax of a test (plan and global)
        description: ''
        operationId: testsCheckSyntaxTpg
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
              required: [ test-execution, test-properties, test-name, test-path, test-extension ]
              properties:
                test-execution:
                  type: array
                  items:
                    type: string
                test-properties:
                  type: string
                test-name:
                  type: string
                test-path:
                  type: string
                test-extension:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                status:
                  type: boolean
                error-msg:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/check/syntax/tpg", 
                  "status": True,
                  "error-msg": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            testExecution = self.request.data.get("test-execution")
            if testExecution is None: raise EmptyValue("Please specify a test execution")
            
            testProperties = self.request.data.get("test-properties")
            if testProperties is None: raise EmptyValue("Please specify a test properties")
            
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            
            testExtension = self.request.data.get("test-extension")
            if testExtension is None: raise EmptyValue("Please specify a test extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if testExtension not in [ "tgx", "tpx" ]:
            raise HTTP_400("Bad test extension provided (%s)" % testExtension)
            
        if testExtension == "tgx":
            success, error_msg, all_tests = RepoTests.instance().addtf2tg( data_= testExecution )
            if success != Context.instance().CODE_OK:
                return { "cmd": self.request.path, "status": False, "error": error_msg }
            testData = { 'test-definition': '', 
                         'test-execution': all_tests, 
                         'test-properties': testProperties,
                         'test-extension': testExtension }
                         
        if testExtension == "tpx":       
            success, error_msg = RepoTests.instance().addtf2tp( data_=testExecution  )
            if success != Context.instance().CODE_OK:
                return { "cmd": self.request.path, "status": False, "error": error_msg }
                
            testData = { 'test-definition': '',
                         'test-execution': testExecution, 
                         'test-properties': testProperties,
                         'test-extension': testExtension  }

        task = TaskManager.getObjectTask(   
                                            testData=testData, 
                                            testName=testName, 
                                            testPath=testPath,  
                                            testUser=user_profile["login"], 
                                            testId=0, 
                                            testBackground=False ,
                                            statsmgr=StatsManager.instance(),
                                            context=Context
                                        )
        status, error_msg = task.parseTest()        
        del task

        return { "cmd": self.request.path, "status": status, "error": error_msg }
    
class TestsCreateDesign(Handler):
    """
    /rest/tests/create/design
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: create the design of a test (unit, abstract and suite)
        description: ''
        operationId: testsCreateDesign
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
              required: [ project-id, test-definition, test-execution, test-properties, test-name, test-path, test-extension ]
              properties:
                project-id:
                  type: integer
                test-definition:
                  type: string
                test-execution:
                  type: string
                test-properties:
                  type: string
                test-name:
                  type: string
                test-path:
                  type: string
                test-extension:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                status:
                  type: boolean
                error-msg:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/check/design", 
                  "status": True,
                  "error-msg": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            testDefinition = self.request.data.get("test-definition")
            if testDefinition is None: raise EmptyValue("Please specify a test definition")
            testExecution = self.request.data.get("test-execution")
            if testExecution is None: raise EmptyValue("Please specify a test execution")
            testProperties = self.request.data.get("test-properties")
            if testProperties is None: raise EmptyValue("Please specify a test properties")
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            testExtension = self.request.data.get("test-extension")
            if testExtension is None: raise EmptyValue("Please specify a test extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if testExtension not in [ "tax", "tux", "tsx" ]:
            raise HTTP_400("Bad test extension provided (%s)" % testExtension)
            
        task = TaskManager.getObjectTask(   
                                            testData=self.request.data, testName=testName, 
                                            testPath=testPath,  testUser=user_profile["login"], 
                                            testId=0, testBackground=False ,
                                            projectId=projectId,
                                            statsmgr=StatsManager.instance(),
                                            context=Context
                                        )
        parsed = task.parseTestDesign()        
        del task

        return { "cmd": self.request.path, 
                 "error": parsed["error"], 
                 "error-msg": parsed["error-details"],
                 "design": parsed["design"],
                 "xml-design": parsed["design-xml"],
                 }

class TestsCreateDesignTpg(Handler):
    """
    /rest/tests/create/design/tpg
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: create the design of a test (plan and global)
        description: ''
        operationId: testsCreateDesignTpg
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
              required: [ project-id, test-execution, test-properties, test-name, test-path, test-extension ]
              properties:
                project-id:
                  type: integer
                test-execution:
                  type: array
                  items:
                    type: string
                test-properties:
                  type: string
                test-name:
                  type: string
                test-path:
                  type: string
                test-extension:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                status:
                  type: boolean
                error-msg:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/check/design/tpg", 
                  "status": True,
                  "error-msg": "...."
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            testExecution = self.request.data.get("test-execution")
            if testExecution is None: raise EmptyValue("Please specify a test execution")
            testProperties = self.request.data.get("test-properties")
            if testProperties is None: raise EmptyValue("Please specify a test properties")
            testName = self.request.data.get("test-name")
            if testName is None: raise EmptyValue("Please specify a test name")
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            testExtension = self.request.data.get("test-extension")
            if testExtension is None: raise EmptyValue("Please specify a test extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if testExtension not in [ "tgx", "tpx" ]:
            raise HTTP_400("Bad test extension provided (%s)" % testExtension)
            
        if testExtension == "tgx":  
            success, error_msg, self.request.data["test-execution"] = RepoTests.instance().addtf2tg( 
                                data_=self.request.data["test-execution"]
                              )
            if success != Context.instance().CODE_OK:
                return { "cmd": self.request.path, "status": False, "error-msg": error_msg }
                
        if testExtension == "tpx":       
            success, error_msg = RepoTests.instance().addtf2tp( 
                                data_=self.request.data["test-execution"]
                             )
            if success != Context.instance().CODE_OK:
                return { "cmd": self.request.path, "status": False, "error-msg": error_msg }
 
        task = TaskManager.getObjectTask(   
                                            testData=self.request.data, testName=testName, 
                                            testPath=testPath,  testUser=user_profile["login"], 
                                            testId=0, testBackground=False ,
                                            projectId=projectId,
                                            statsmgr=StatsManager.instance(),
                                            context=Context
                                        )
        parsed = task.parseTestDesign()        
        del task

        return { "cmd": self.request.path, 
                 "error": parsed["error"], 
                 "error-msg": parsed["error-details"],
                 "design": parsed["design"],
                 "xml-design": parsed["design-xml"],
                 }

class TestsFileDownload(Handler):
    """
    /rest/tests/file/download
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: download file from the test storage 
        description: ''
        operationId: testsFileDownload
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                file-content:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/download", 
                  "file-content": "...."
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
            if projectId is None: raise EmptyValue("Please specify a  project id")
            
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success, _, _, _, content, _, _ = RepoTests.instance().getFile(pathFile=filePath, 
                                                                       binaryMode=True, 
                                                                       project=projectId, 
                                                                       addLock=False)  
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to download file")

        return { "cmd": self.request.path, "file-content": content }
        
class TestsFileOpen(Handler):
    """
    /rest/tests/file/open
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: open and lock file from the test storage 
        description: ''
        operationId: testsFileOpen
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
                ignore-lock:
                  type: boolean
                read-only:
                  type: boolean
                custom-param:
                  type: integer
                destination-id:
                  type: integer
                action-id:
                  type: integer
                extra:
                  type: object
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                file-content:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/open", 
                  "file-content": "...."
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
            if projectId is None: raise EmptyValue("Please specify a  project id")
            
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
            
            _ignoreLock = self.request.data.get("ignore-lock", False)
            _readOnly = self.request.data.get("read-only", False)
            
            _customParam = self.request.data.get("custom-param")
            _actId = self.request.data.get("action-id")
            _destId = self.request.data.get("destination-id")

            # new in v19, news extras parameters used only by the qt client
            # these parameters are introduced by the pull request from dbr13 contribution user.
       
            # update location is true when the test location in testplan/testglobal is updated
            # the old test location is also provided to search it in other files and update it
            extra_update_location = self.request.data.get('extra', {}).get('update_location', False)
            
            # the old test location from testplan/testglobal 
            # these parameters are used when the update_location is True
            extra_filename = self.request.data.get('extra', {}).get('file_name', '')
            extra_ext = self.request.data.get('extra', {}).get('file_ext', '')
            extra_projectid = self.request.data.get('extra', {}).get('project_id', 0)
            extra_path = self.request.data.get('extra', {}).get('file_path', '')
            
            # referer to the origin file (testplan or testglobal) which ask to open the file
            # the path and the project id if the file is provided
            # the refresh referer indicates or not if the referer file must be updated or not
            extra_file_referer_path = self.request.data.get('extra', {}).get('file_referer_path', '')
            extra_file_referer_projectid = self.request.data.get('extra', {}).get('file_referer_projectid', 0)
            extra_file_referer_refresh = self.request.data.get('extra', {}).get('file_referer_refresh', False)
            
            # provide a specific sub test id in a testplan or testglobal
            # this parameter is used from find test usage function
            extra_subtest_id = self.request.data.get('extra', {}).get('subtest_id', '')
            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        addLock = True
        if _destId is not None and _actId is not None:
            addLock = False
            _ignoreLock = False
            _readOnly = False
            
        resultGetFile = RepoTests.instance().getFile(pathFile=filePath, 
                                                    project=projectId, 
                                                    login=user_profile['login'],
                                                    forceOpen=_ignoreLock, 
                                                    readOnly=_readOnly,
                                                    addLock=addLock)  
        success, path_file, name_file, ext_file, project, data_base64, locked, locked_by = resultGetFile
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to open test file")
            
        rsp_rest = { "cmd": self.request.path, 
                     "file-content": data_base64,
                     "file-path": path_file,
                     "file-name": name_file,
                     "file-extension": ext_file,
                     "locked": locked,
                     "locked-by": locked_by,
                     "project-id": project,
                     "custom-param": _customParam,
                     "action-id": _actId,
                     "destination-id": _destId,
                     "referer-refresh": extra_file_referer_refresh,
                     "subtest-id": str(extra_subtest_id) }
                     
        # dbr13 >>> when we set checkbox in the Update->Location
        if extra_update_location:
            file_path = path_file or '/'
            update_files_list = RepoTests.instance().updateLinkedScriptPath(project=extra_projectid,
                                                                            mainPath=extra_path,
                                                                            oldFilename=extra_filename,
                                                                            extFilename=extra_ext,
                                                                            
                                                                            newProject=projectId,
                                                                            newPath=file_path,
                                                                            newFilename=name_file,
                                                                            newExt=ext_file,
                                                                            
                                                                            user_login=user_profile['login'],
                                                                            file_referer_path=extra_file_referer_path,
                                                                            file_referer_projectid=extra_file_referer_projectid
                                                                           )
        # dbr13 <<<

        return rsp_rest

class TestsFileUpload(Handler):
    """
    /rest/tests/file/upload
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - tests
        summary: Upload file the test storage 
        description: ''
        operationId: testsFileUpload
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
              required: [ project-id, file-path, file-name, file-extension, file-content ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
                file-name:
                  type: string
                file-extension:
                  type: string
                file-content:
                  type: string
                overwrite:
                  type: boolean
                close-after:
                  type: boolean
                add-folders:
                  type: boolean
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                code:
                  type: integer
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/upload", 
                  "code": 200
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a file path")
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a file name")
            fileExt = self.request.data.get("file-extension")
            if fileExt is None: raise EmptyValue("Please specify a file extension")
            fileContent = self.request.data.get("file-content")
            if fileContent is None: raise EmptyValue("Please specify a file content")
            
            _overwrite = self.request.data.get("overwrite", False)
            _closeafter = self.request.data.get("close-after", False)
            _addfolders = self.request.data.get("add-folders", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        putFileReturn = RepoTests.instance().uploadFile( pathFile=filePath, 
                                                         nameFile=fileName, 
                                                         extFile=fileExt, 
                                                         contentFile=fileContent, 
                                                         login=user_profile['login'], 
                                                         project=projectId, 
                                                         overwriteFile=_overwrite,
                                                         createFolders=_addfolders,
                                                         lockMode=True, 
                                                         binaryMode=True,
                                                         closeAfter=_closeafter )
        success, pathFile, nameFile, extFile, project, overwriteFile, closeAfter, isLocked, lockedBy = putFileReturn

        return { "cmd": self.request.path, 
                 "code": success,
                 "file-path": pathFile,
                 "file-name": nameFile,
                 "file-extension": extFile,
                 "project-id":  project,
                 "overwrite":  overwriteFile,
                 "close-after": closeAfter,
                 "locked": isLocked,
                 "locked-by": lockedBy }

class TestsFileRemove(Handler):
    """
    /rest/tests/file/remove
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - tests
        summary: remove file in the test storage 
        description: ''
        operationId: testsFileRemove
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
              required: [ project-id, file-path  ]
              properties:
                project-id:
                  type: integer
                file-path:
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
                  "cmd": "/tests/file/remove", 
                  "message": "file successfully removed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            filePath = self.request.data.get("file-path")
            if not filePath: raise EmptyValue("Please specify a file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoTests.instance().delFile( pathFile=filePath, project=projectId, supportSnapshot=False)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove file")
        if success == Context.instance().CODE_FAILED:
            raise HTTP_403("Remove file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully removed", 
                 "project-id": projectId }
                 
class TestsFileUnlock(Handler):
    """
    /rest/tests/file/unlock
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - tests
        summary: unlock file in the test storage 
        description: ''
        operationId: testsFileUnlock
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
              required: [ project-id, file-path, file-name, file-extension  ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
                file-name:
                  type: string
                file-extension:
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
                  "cmd": "/tests/file/unlock", 
                  "message": "file successfully unlocked"
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
            if projectId is None: raise EmptyValue("Please specify a project id")
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a source file filename")
            fileExt = self.request.data.get("file-extension")
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success  = RepoTests.instance().unlockFile(pathFile=filePath, 
                                                   nameFile=fileName, 
                                                   extFile=fileExt, 
                                                   project=projectId, 
                                                   login=user_profile["login"])
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to unlock test file")

        return { "cmd": self.request.path, "message": "file sucessfully unlocked", 
                 "project-id": projectId }

# dbr13 >>>
class TestsFindFileUsage(Handler):
    """
    /tests/find/file-usage
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary:  Finding script usages included in test plans and globals
        description: ''
        operationId: testsFindFileUsage
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
              required: [ project-id, file-path ]
              properties:
                project-id:
                  type: integer
                file-path:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                folder-content:
                  type: dict
            examples:
              application/json: |
                {
                  "cmd": "/tests/find/file-usage",
                  "folder-content": {}
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
            if projectId is None: raise EmptyValue("Please specify a project id")
            filePath = self.request.data.get("file-path")
            if filePath is None: raise EmptyValue("Please specify a source filepath")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        response = RepoTests.instance().getTestFileUsage(file_path=filePath,
                                                         project_id=projectId,
                                                         user_login=user_profile['login'])
        return {
            'cmd': self.request.path,
            'response': response,
            "usage-file-path": filePath,
            "usage-project-id": projectId
        }
        
class TestsUpdateAdapterLibrary(Handler):
    """
    tests/update/adapter-library
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: Update Adapters/Libraries for multiple test entities
        description: ''
        operationId: testsUpdateAdapterLibrary
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
              required: [ project-id, folder-path, adapter-version, library-version ]
              properties:
                project-id:
                  type: integer
                folder-path:
                  type: string
                adapter-version:
                  type: string
                library-version:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                folder-content:
                  type: dict
            examples:
              application/json: |
                {
                  "cmd": "/tests/update/adapter-library",
                  "folder-content": {}
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        if user_profile['leader']: raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            folderPath = self.request.data.get("folder-path")
            if folderPath is None: raise EmptyValue("Please specify a source filepath")
            adapterVersion = self.request.data.get('adapter-version')
            libraryVersion = self.request.data.get('library-version')
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath)

        status, result = RepoTests.instance().updateAdaptersLibrariesVForTestEnteties(folder_path=folderPath,
                                                                                      adapter_version=adapterVersion,
                                                                                      library_version=libraryVersion,
                                                                                      project_id=projectId,
                                                                                      user_login=user_profile['login'])
        return {
            'cmd': self.request.path,
            'status': status,
            'result': result,
            'adapter_version': adapterVersion,
            'library_version': libraryVersion,
            'path_folder': folderPath
        }
        
# dbr13 <<<
                 
class TestsFileRename(Handler):
    """
    /rest/tests/file/rename
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - tests
        summary: Rename file in the test storage 
        description: ''
        operationId: testsFileRename
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, file-name, file-path, file-extension  ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ file-name ]
                  properties:
                    file-name:
                      type: string
                upload_location:
                  required: [upload_location]
                  properties:
                    upload_location: boolean
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/rename", 
                  "message": "file successfully renamed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify source")
            projectId = self.request.data.get("source")["project-id"]
            if projectId is None: raise EmptyValue("Please specify a project id")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source filepath")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source file filename")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify destination")
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
            
            # dbr13 >>>
            update_location = self.request.data.get("update_location", False)
            # dbr13 <<<
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        
        success = RepoTests.instance().renameFile( 
                                                    mainPath=filePath, 
                                                    oldFilename=fileName, 
                                                    newFilename=newFileName, 
                                                    extFilename=fileExt,
                                                    project=projectId, 
                                                    supportSnapshot=False
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Rename file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")


        # dbr13 >>>
        # When we set checkbox in the rename
        if update_location:
            update_files_list = RepoTests.instance().updateLinkedScriptPath(
                                                                            project=projectId,
                                                                            mainPath=filePath,
                                                                            oldFilename=fileName,
                                                                            extFilename=fileExt,
                                                                            
                                                                            newProject=projectId,
                                                                            newPath=filePath,
                                                                            newFilename=newFileName,
                                                                            newExt=fileExt,
                                                                            
                                                                            user_login=user_profile['login'])

        # dbr13 >>>
        # I think we need add some info into return but I haven't thought about it yet =)
        
        return { "cmd": self.request.path, "message": "file sucessfully renamed", 
                 "project-id": projectId,
                 "file-path": filePath,
                 "file-name": fileName,
                 "file-extension": fileExt,
                 "new-file-name": newFileName}
        
class TestsFileDuplicate(Handler):
    """
    /rest/tests/file/duplicate
    """   
    @_to_yaml    
    def post(self):
        """
        tags:
          - tests
        summary: Duplicate file in the test storage 
        description: ''
        operationId: testsFileDuplicate
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, file-name, file-path, file-extension  ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ project-id, file-path, file-name ]
                  properties:
                    project-id:
                      type: integer
                    file-path:
                      type: string
                    file-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/rename", 
                  "message": "file successfully renamed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify source")
            projectId = self.request.data.get("source")["project-id"]
            if projectId is None: raise EmptyValue("Please specify a source projcet-id")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source filename")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify destination")
            newProjectId = self.request.data.get("destination")["project-id"]
            if newProjectId is None: raise EmptyValue("Please specify a project id")
            newFileName = self.request.data.get("destination")["file-name"]
            if newFileName is None: raise EmptyValue("Please specify a destination file name")
            newFilePath = self.request.data.get("destination")["file-path"]
            if newFilePath is None: raise EmptyValue("Please specify a destination file path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)
        _check_project_permissions(user_login=user_profile['login'], project_id=newProjectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoTests.instance().duplicateFile( 
                                                        mainPath=filePath,
                                                        oldFilename=fileName,
                                                        newFilename=newFileName,
                                                        extFilename=fileExt,
                                                        project=projectId,
                                                        newProject=newProjectId,
                                                        newMainPath=newFilePath
                                                    )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Duplicate file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        return { "cmd": self.request.path, "message": "file sucessfully duplicated", 
                 "project-id": projectId }
        
class TestsFileMove(Handler):
    """
    /rest/tests/file/move
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: Move file in the test storage 
        description: ''
        operationId: testsFileMove
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, file-name, file-path, file-extension  ]
                  properties:
                    project-id:
                      type: integer
                    file-name:
                      type: string
                    file-path:
                      type: string
                    file-extension:
                      type: string
                destination:
                  type: object
                  required: [ project-id, file-path ]
                  properties:
                    project-id:
                      type: integer
                    file-path:
                      type: string
                upload_location:
                  required: [upload_location]
                  properties:
                    upload_location: boolean
        responses:
          '200':
            description: move response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/file/move", 
                  "message": "file successfully moved"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify source")
            projectId = self.request.data.get("source")["project-id"]
            if projectId is None: raise EmptyValue("Please specify a project name or a project id")
            filePath = self.request.data.get("source")["file-path"]
            if filePath is None: raise EmptyValue("Please specify a source filename")
            fileName = self.request.data.get("source")["file-name"]
            if fileName is None: raise EmptyValue("Please specify a source file path")
            fileExt = self.request.data.get("source")["file-extension"]
            if fileExt is None: raise EmptyValue("Please specify a source file extension")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify destination")
            newProjectId = self.request.data.get("destination")["project-id"]
            if newProjectId is None: raise EmptyValue("Please specify a new project id")
            newFilePath = self.request.data.get("destination")["file-path"]
            if newFilePath is None: raise EmptyValue("Please specify a destination file path")
            
            update_location = self.request.data.get("update_location", False)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)
        _check_project_permissions(user_login=user_profile['login'], project_id=newProjectId)

        # avoid directory traversal
        filePath = os.path.normpath("/" + filePath )
        newFilePath = os.path.normpath("/" + newFilePath )
        
        success = RepoTests.instance().moveFile( 
                                                mainPath=filePath, 
                                                fileName=fileName, 
                                                extFilename=fileExt, 
                                                newPath=newFilePath, 
                                                project=projectId, 
                                                newProject=newProjectId,
                                                supportSnapshot=True
                                                )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move file")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Move file denied")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("File does not exists")
            
        if update_location:
            update_files_list = RepoTests.instance().updateLinkedScriptPath(project=projectId,
                                                                            mainPath=filePath,
                                                                            oldFilename=fileName,
                                                                            extFilename=fileExt,
                                                                            
                                                                            newProject=newProjectId,
                                                                            newPath=newFilePath,
                                                                            newFilename=fileName,
                                                                            newExt=fileExt,
                                                                            
                                                                            user_login=user_profile['login'],
                                                                            )
                                                                            
        return { "cmd": self.request.path, "message": "file successfully moved", 
                 "project-id": projectId  }
      
class TestsDirectoryAdd(Handler):
    """
    /rest/tests/directory/add
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - tests
        summary: Add directory in the test storage 
        description: ''
        operationId: testsDirectoryAdd
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
              required: [ project-id, directory-name, directory-path ]
              properties:
                project-id:
                  type: integer
                directory-name:
                  type: string
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
                  "cmd": "/tests/directory/add", 
                  "message": "directory successfully added"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            folderName = self.request.data.get("directory-name")
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoTests.instance().addDir(pathFolder=folderPath, folderName=folderName, project=projectId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add directory")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully added", 
                 "project-id": projectId }
        
class TestsDirectoryRename(Handler):
    """
    /rest/tests/directory/rename
    """   
    @_to_yaml   
    def post(self):
        """
        tags:
          - tests
        summary: Rename directory in the test storage 
        description: ''
        operationId: testsDirectoryRename
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, directory-name, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ project-id, directory-name ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/directory/rename", 
                  "message": "directory successfully renamed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)
		
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify source")
            projectId = self.request.data.get("source")["project-id"]
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify destination")
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        
        success = RepoTests.instance().renameDir(mainPath=folderPath, oldPath=folderName, 
                                                 newPath=newFolderName, project=projectId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to rename directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to rename directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully renamed", 
                 "project-id": projectId, "directory-name": folderName, 
                 "directory-path": folderPath, "new-directory-name": newFolderName  }
        
class TestsDirectoryDuplicate(Handler):
    """
    /rest/tests/directory/duplicate
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - tests
        summary: Duplicate directory in the test storage 
        description: ''
        operationId: testsDirectoryDuplicate
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, directory-name, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ project-id, file-name ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
        responses:
          '200':
            description: rename response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/directory/rename", 
                  "message": "directory successfully renamed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        # checking json request on post
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            
            projectId = self.request.data.get("source")["project-id"]
            if projectId is None: raise EmptyValue("Please specify a project id")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
            
            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            
            newProjectId = self.request.data.get("destination")["project-id"]
            if newProjectId is None: raise EmptyValue("Please specify a project id")
            newFolderName = self.request.data.get("destination")["directory-name"]
            if newFolderName is None: raise EmptyValue("Please specify a destination folder name")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if newFolderPath is None: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)
        _check_project_permissions(user_login=user_profile['login'], project_id=newProjectId)

        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        # all ok, do the duplication
        success = RepoTests.instance().duplicateDir(
                                                    mainPath=folderPath, oldPath=folderName, 
                                                    newPath=newFolderName, project=projectId, 
                                                    newProject=newProjectId, 
                                                    newMainPath=newFolderPath
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to duplicate directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to duplicate directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully duplicated",
                 "project-id": projectId }
        
class TestsDirectoryMove(Handler):
    """
    /rest/tests/directory/move
    """   
    @_to_yaml   
    def post(self):
        """
        tags:
          - tests
        summary: Move directory in the test storage 
        description: ''
        operationId: testsDirectoryMove
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
              required: [ source, destination ]
              properties:
                source:
                  type: object
                  required: [ project-id, directory-name, directory-path  ]
                  properties:
                    project-id:
                      type: integer
                    directory-name:
                      type: string
                    directory-path:
                      type: string
                destination:
                  type: object
                  required: [ project-id, directory-path ]
                  properties:
                    project-id:
                      type: integer
                    directory-path:
                      type: string
        responses:
          '200':
            description: move response
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/tests/directory/move", 
                  "message": "directory successfully moved"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        # get the user profile
        user_profile = _get_user(request=self.request)
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        # checking json request on post
        try:
            source = self.request.data.get("source")
            if source is None: raise EmptyValue("Please specify a source")
            projectId = self.request.data.get("source")["project-id"]
            if projectId is None: raise EmptyValue("Please specify a project id")
            folderName = self.request.data.get("source")["directory-name"]
            if folderName is None: raise EmptyValue("Please specify a source folder name")
            folderPath = self.request.data.get("source")["directory-path"]
            if folderPath is None: raise EmptyValue("Please specify a source folder path")

            destination = self.request.data.get("destination")
            if destination is None: raise EmptyValue("Please specify a destination")
            newProjectId = self.request.data.get("destination")["project-id"]
            if newProjectId is None: raise EmptyValue("Please specify a project id")
            newFolderPath = self.request.data.get("destination")["directory-path"]
            if newFolderPath is None: raise EmptyValue("Please specify a destination folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)
        _check_project_permissions(user_login=user_profile['login'], project_id=newProjectId)

        # some security check to avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )
        newFolderPath = os.path.normpath("/" + newFolderPath )
        
        if "%s/%s" % (folderPath, folderName) == newFolderPath:
            raise HTTP_403( "Destination same as origin" )
        
        # all ok, do the duplication
        success = RepoTests.instance().moveDir(
                                                    mainPath=folderPath, 
                                                    folderName=folderName, 
                                                    newPath=newFolderPath, 
                                                    project=projectId, 
                                                    newProject=newProjectId
                                                )  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to move directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to move directory: source directory not found")
        if success == Context.instance().CODE_ALLREADY_EXISTS:
            raise HTTP_403("Directory already exists")
            
        return { "cmd": self.request.path, "message": "directory successfully moved", 
                 "project-id": projectId }
        
class TestsDirectoryRemove(Handler):
    """
    /rest/tests/directory/remove
    """   
    @_to_yaml 
    def post(self):
        """
        tags:
          - tests
        summary: remove directory in the test storage 
        description: ''
        operationId: testsDirectoryRemove
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
                  "cmd": "/tests/directory/remove", 
                  "message": "directory successfully removed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            folderPath = self.request.data.get("directory-path")
            if folderPath is None: raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath )

        success = RepoTests.instance().delDir(folderPath, projectId)  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Cannot remove directory")
                
        return { "cmd": self.request.path, "message": "directory successfully removed",
                 "project-id": projectId }

class TestsSnapshotAdd(Handler):
    """
    /rest/tests/snapshot/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: add a snapshot
        description: ''
        operationId: testsSnapshotAdd
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
              required: [ project-id, test-path, snapshot-name, snapshot-timestamp ]
              properties:
                project-id:
                  type: integer
                test-path:
                  type: string
                snapshot-name:
                  type: string
                snapshot-timestamp:
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
                  "cmd": "/rest/tests/snapshot/add", 
                  "message": "snapshot successfully added"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            testPath = self.request.data.get("test-path")
            if testPath is None: raise EmptyValue("Please specify a test path")
            
            snapshotName = self.request.data.get("snapshot-name")
            if snapshotName is None: raise EmptyValue("Please specify a snapshot name")
            snapshotTimestamp = self.request.data.get("snapshot-timestamp")
            if snapshotTimestamp is None: raise EmptyValue("Please specify a snapshot timestamp")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success = RepoTests.instance().addSnapshot( snapshotName=snapshotName, 
                                                    snapshotTimestamp=snapshotTimestamp,
                                                    testPath=testPath, 
                                                    testPrjId=projectId )
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to find the test provided")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to add the snapshot")
            
        return { "cmd": self.request.path, "message": "snapshot successfully added",
                 "project-id": projectId}
        
class TestsSnapshotRemove(Handler):
    """
    /rest/tests/snapshot/remove
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: remove a snapshot
        description: ''
        operationId: testsSnapshotRemove
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
              required: [ project-id, snapshot-name, snapshot-path ]
              properties:
                project-id:
                  type: integer
                snapshot-name:
                  type: string
                snapshot-path:
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
                  "cmd": "/rest/tests/snapshot/remove", 
                  "message": "snapshot removed"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            snapshotName = self.request.data.get("snapshot-name")
            if snapshotName is None: raise EmptyValue("Please specify a snapshot name")
            snapshotPath = self.request.data.get("snapshot-path")
            if snapshotPath is None: raise EmptyValue("Please specify a snapshot path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success = RepoTests.instance().deleteSnapshot( 
                                                        snapshotPath=snapshotPath,
                                                        snapshotName=snapshotName,
                                                        snapshotPrjId=projectId
                                                        )
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to find the snapshot provided")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove the snapshot")
            
        return { "cmd": self.request.path, "message": "snapshot removed", "project-id": projectId }

class TestsSnapshotRestore(Handler):
    """
    /rest/tests/snapshot/restore
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tests
        summary: restore snapshot
        description: ''
        operationId: testsSnapshotRestore
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
              required: [ project-id, snapshot-name, snapshot-path ]
              properties:
                project-id:
                  type: integer
                snapshot-name:
                  type: string
                snapshot-path:
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
                  "cmd": "/rest/tests/snapshot/restore", 
                  "message": "snapshot restored"
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            snapshotName = self.request.data.get("snapshot-name")
            if snapshotName is None: raise EmptyValue("Please specify a snapshot name")
            snapshotPath = self.request.data.get("snapshot-path")
            if snapshotPath is None: raise EmptyValue("Please specify a snapshot path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success =  RepoTests.instance().restoreSnapshot( 
                                                            snapshotPath=snapshotPath,
                                                            snapshotName=snapshotName,
                                                            snapshotPrjId=projectId
                                                        )
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to find the snapshot provided")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to restore the snapshot")
            
        return { "cmd": self.request.path, "message": "snapshot restored", "project-id": projectId }
 
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
        operationId: variablesAdd
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
              required: [ project-id, variable-name,variable-value]
              properties:
                variable-name:
                  type: string
                variable-value:
                  type: string
                  description: in json format
                project-id:
                  type: integer
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
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

            variableName = self.request.data.get("variable-name")
            if variableName is None: raise EmptyValue("Please specify the name of the variable")
            
            variableJson = self.request.data.get("variable-value")
            if variableJson is None: raise EmptyValue("Please specify the value of the variable")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)
   
        # dumps the json
        try:
            variableValue = json.dumps(variableJson)
        except Exception :
            raise HTTP_400("Bad json provided in value")

        success, details = RepoTests.instance().addVariableInDB(projectId=projectId, 
                                                                variableName=variableName,
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
        operationId: variablesDuplicate
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
              required: [project-id, variable-id]
              properties:
                variable-id:
                  type: string
                project-id:
                  type: integer
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
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

            variableId = self.request.data.get("variable-id")
            if variableId is None: raise EmptyValue("Please specify a variable id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success, details = RepoTests.instance().duplicateVariableInDB(variableId=variableId, 
                                                                      projectId=projectId)
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
        operationId: variablesUpdate
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
              required: [project-id, variable-id]
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
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            variableId = self.request.data.get("variable-id")
            if variableId is None: raise HTTP_400("Please specify a variable id")

            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

            variableName = self.request.data.get("variable-name")
            variableJson = self.request.data.get("variable-value")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)
  
        # dumps the json
        try:
            variableValue = json.dumps(variableJson)
        except Exception :
            raise HTTP_400("Bad json provided in value")

        success, details = RepoTests.instance().updateVariableInDB(variableId=variableId, 
                                                                   variableName=variableName, 
                                                                   variableValue=variableValue, 
                                                                   projectId=projectId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "variable successfully updated" }
        
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
        operationId: variablesRemove
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
              required: [project-id, variable-id]
              properties:
                variable-id:
                  type: string
                project-id:
                  type: integer
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
        
        if user_profile['leader']: raise HTTP_403("Access refused")
        
        try:
            variableId = self.request.data.get("variable-id")
            if variableId is None : raise HTTP_400("Please specify a variable id")
            
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success, details = RepoTests.instance().delVariableInDB(variableId=variableId, projectId=projectId)
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
        operationId: variablesListing
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
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success, details = RepoTests.instance().getVariablesFromDB(projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        
        # new in v17 convert as json the result 
        # for d in details:
            # d['value'] = json.loads( d['value'] )        
        # end of new
        
        return { "cmd": self.request.path, "message": "listing result", "variables": details }

class VariablesSearchByName(Handler):
    """
    /rest/variables/search/by/name
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Search a variable according to the name or id
        description: ''
        operationId: variablesSearchByName
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
              required: [project-id, variable-name]
              properties:
                project-id:
                  type: integer
                variable-name:
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
                  "cmd": "/variables/search/by/name"
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
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            variableName = self.request.data.get("variable-name")
            if variableName is None: raise EmptyValue("Please specify the name of the variable")
            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success, details = RepoTests.instance().getVariableFromDB(projectId=projectId, 
                                                                  variableName=variableName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_404("Variable not found")

        
        # if len(details) == 1:
            # new in v17, convert as json the value
            # details[0]['value'] = json.loads( details[0]['value'] )
            # end of new
            # return { "cmd": self.request.path, "variable": details[0] }
        # else:
            # new in v17 convert value as json
            # for d in details:
                # d['value'] = json.loads( d['value'] )
            # end of new
            
        return { "cmd": self.request.path, "message": "search result", "variables": details }

class VariablesSearchById(Handler):
    """
    /rest/variables/search/by/id
    """   
    @_to_yaml
    def post(self):
        """
        tags:
          - variables
        summary: Search a variable according to the name or id
        description: ''
        operationId: variablesSearchById
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
              required: [project-id, variable-id]
              properties:
                project-id:
                  type: integer
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
                  "cmd": "/variables/search/by/id"
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
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            variableId = self.request.data.get("variable-id")
            if variableId is None: raise EmptyValue("Please specify the id of the variable")
            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success, details = RepoTests.instance().getVariableFromDB(projectId=projectId,
                                                                  variableId=variableId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_404("Variable not found")

        
        # if len(details) == 1:
            # new in v17, convert as json the value
            # details[0]['value'] = json.loads( details[0]['value'] )
            # end of new
            # return { "cmd": self.request.path, "variable": details[0] }
        # else:
            # new in v17 convert value as json
            # for d in details:
                # d['value'] = json.loads( d['value'] )
            # end of new
            
        return { "cmd": self.request.path, "message": "search result", "variables": details }

"""
Tests Results handlers
"""
class ResultsUploadFile(Handler):
    """
    /rest/results/upload/file
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Upload a file in the test result
        description: ''
        operationId: resultsUploadFile
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: body
            in: body
            required: true
            schema:
              required: [ result-path, file-name, file-content ]
              properties:
                result-path:
                  type: string
                file-name:
                  type: string
                file-content:
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
                  "cmd": "/results/upload/file", 
                  "message": "success"
                }
          '400':
            description: Bad request provided
          '403':
            description: Extension file refused
          '404':
            description: Test result not found
          '500':
            description: Server error 
        """
        try:
            resultPath = self.request.data.get("result-path")
            if resultPath is None: raise EmptyValue("Please specify a result path")
            
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a file name")
            
            fileContent = self.request.data.get("file-content")
            if fileContent is None: raise EmptyValue("Please specify a file content")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        # we can upload only zip file
        if not fileName.endswith(".zip") and not fileName.endswith(".png") \
                and not fileName.endswith(".jpg") and not fileName.endswith(".mp4") :
            raise HTTP_403('Extension file not authorized')
            
        archiveRepo='%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        if not os.path.exists( "%s/%s" % (archiveRepo, resultPath )):
            raise HTTP_404('test result path not found')
        
        success = RepoArchives.instance().createResultLog(testsPath=archiveRepo , 
                                                          logPath=resultPath,
                                                          logName=fileName, 
                                                          logData=fileContent )
        if not success:
            raise HTTP_500("Unable to upload file in testresult")
            
        return { "cmd": self.request.path, 'message': 'success' }
       
class ResultsCompressZip(Handler):
    """
    /rest/results/compress/zip
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Compress test result in one zip file
        description: ''
        operationId: resultsCompressZip
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
        responses:
          '200':
            description: all tests results zipped
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
                  "cmd": "/results/compress/zip", 
                  "message": "....",
                  "project-id": 22
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
            if projectId is None: raise EmptyValue("Please specify a project id")

            testId = self.request.data.get("test-id")
            if testId is None: raise EmptyValue("Please specify a project id and test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId, 
                                                                  returnProject=False)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        success = RepoArchives.instance().createZip(trPath=testPath, projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500('Unable to create zip file')
            
        return { "cmd": self.request.path, 'project-id': projectId, "message": "zip created" }
                 
class ResultsListingFiles(Handler):
    """
    /rest/results/listing/files
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Get the listing of all tests results
        description: ''
        operationId: resultsListingFiles
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
                partial-list:
                  type: boolean
                project-id:
                  type: integer
        responses:
          '200':
            description: all test results with details
            schema :
              properties:
                cmd:
                  type: string
                listing:
                  type: list
                  description: listing all test results
                  items:
                    type: object
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/listing/files", 
                  "listing": [...],
                  "nb-folders": 2,
                  "nb-files":  2,
                  "statistics": {...}
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
            if projectId is None: raise EmptyValue("Please specify a project id")

            _partial = self.request.data.get("partial-list", True)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        nb_archs, nb_archs_f, archs, stats_archs = RepoArchives.instance().getTree(fullTree=not _partial, 
                                                                                   project=projectId)       
        return { "cmd": self.request.path, 
                 "listing": archs, 
                 "nb-folders": nb_archs, 
                 "nb-files": nb_archs_f, 
                 "statistics": stats_archs, 
                 'project-id': projectId }

class ResultsListingIdByDateTime(Handler):
    """
    /rest/results/listing/id/by/datetime
    """
    @_to_yaml    
    def post(self):
        """
        tags:
          - results
        summary: Get the listing id of all tests results. Support date and time filtering.
        description: ''
        operationId: resultsListingIdByDatetime
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
                date:
                  type: string
                  description: filter results by date "YYYY-MM-DD", returns only results greater than the date provided
                time:
                  type: string
                  description: filter results by time "HH:MM:SS", returns only results greater than the time provided
        responses:
          '200':
            description: all tests results with id
            schema :
              properties:
                cmd:
                  type: string
                listing:
                  type: array
                  items:
                    type: object
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/listing/id/by/datetime", 
                  "listing":  [...]
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
            if projectId is None: raise EmptyValue("Please specify a project id")

            dateFilter = self.request.data.get("date", None)
            timeFilter = self.request.data.get("time", None)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        listing = RepoArchives.instance().getBasicListing(projectId=projectId, 
                                                        dateFilter=dateFilter, 
                                                        timeFilter=timeFilter)  
        
        return { "cmd": self.request.path, 
                 "listing": listing, 
                 'project-id': projectId }

class ResultsDownloadResult(Handler):
    """
    /rest/results/download/result
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Get result file in test result
        description: ''
        operationId: resultsDownloadResult
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
              required: [ test-id, project-id, file-name ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                file-name:
                  type: string
                save-as:
                  type: boolean
                  description: parameter only used in windows client
                save-as-name:
                  type: string
                  description: parameter only used in windows client
        responses:
          '200':
            description: image
            schema :
              properties:
                cmd:
                  type: string
                result:
                  type: string
                  description: in base64
                result-name:
                  type: string
                project-id:
                  type: string
                save-as:
                    type: boolean
                save-as-name:
                    type: string
                    description: in base64
            examples:
              application/json: |
                {
                  "cmd": "/results/download/result", 
                  "result": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "result-name": "....",
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "save-as": False,
                  "save-as-dest: ""
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result by id not found
          '500':
            description: Server error 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            fileName = self.request.data.get("file-name")
            if fileName is None: raise EmptyValue("Please specify a file name")

            testId = self.request.data.get("test-id")
            if testId is None: raise EmptyValue("Please specify a project id and test id")
            
            _saveAs = self.request.data.get("save-as", False)
            _saveAsDest = self.request.data.get("save-as-name", '')
            
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, 
                                                                  testId=testId, returnProject=False)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result by id not found')

        trxPath = "%s/%s" % (testPath, fileName)
        success, _, nameFile, extFile, _, b64result, _, _ = RepoArchives.instance().getFile( pathFile=trxPath, 
                                                                                          project=projectId, 
                                                                                          addLock=False)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Result file not found")
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to get file, check log in server side")
            
        return { "cmd": self.request.path, 'test-id': testId, 'project-id': projectId, 
                 'result': b64result, 'result-name': nameFile, "result-extension": extFile,
                 'save-as': _saveAs, 'save-as-name': _saveAsDest }
                 
class ResultsDownloadResultUncomplete(Handler):
    """
    /rest/results/download/uncomplete
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Get result events event if the test is not yet terminated
        description: ''
        operationId: resultsDownloadUncomplete
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
        responses:
          '200':
            description: image
            schema :
              properties:
                cmd:
                  type: string
                result:
                  type: string
                  description: in base64
                result-name:
                  type: string
                project-id:
                  type: string
                save-as:
                    type: boolean
                save-as-name:
                    type: string
                    description: in base64
            examples:
              application/json: |
                {
                  "cmd": "/results/download/uncomplete", 
                  "result": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "result-name": "....",
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "save-as": False,
                  "save-as-dest: ""
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result by id not found
          '500':
            description: Server error 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

            testId = self.request.data.get("test-id")
            if testId is None: raise EmptyValue("Please specify a test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # extract the real test path according the test id
        success, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result by id not found')

        success, trName = RepoArchives.instance().createTrTmp(trPath=testPath)
        if success != Context.instance().CODE_OK:
            raise HTTP_500('Unable to get partial test result')
            
        testPath = testPath.split("/", 1)[1]
        trxPath = "%s/%s" % (testPath, trName)
        success, _, nameFile, extFile, _, b64result, _, _ = RepoArchives.instance().getFile( pathFile=trxPath, 
                                                                                          project=projectId, 
                                                                                          addLock=False)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Result file not found")
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to get file, check log in server side")
            
        return { "cmd": self.request.path, 'test-id': testId, 'project-id': projectId, 
                 'result': b64result, 'result-name': nameFile, "result-extension": extFile }
                 
class ResultsDownloadImage(Handler):
    """
    /rest/results/download/image
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Get image (png or jpg) from test result
        description: ''
        operationId: resultsDownloadImage
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
              required: [ test-id, project-id, image-name ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                image-name:
                  type: string
        responses:
          '200':
            description: image
            schema :
              properties:
                cmd:
                  type: string
                image:
                  type: string
                  description: in base64
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/download/image", 
                  "image": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
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
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            imageName = self.request.data.get("image-name")
            if imageName is None: raise EmptyValue("Please specify a image name")
			
            testId = self.request.data.get("test-id")
            if testId is None: raise EmptyValue("Please specify a project id and test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, 
                                                                  testId=testId, returnProject=False)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('test not found')

        imagePath = "%s/%s" % (testPath, imageName)
        success, _, _, _, _, b64img, _, _ = RepoArchives.instance().getFile(pathFile=imagePath, 
                                                                         project=projectId, 
                                                                         addLock=False)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("Image not found")
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to get file, check logs in server side")
            
        return { "cmd": self.request.path, 'test-id': testId, 'project-id': projectId, 'image': b64img }

class ResultsRemoveById(Handler):
    """
    /rest/results/remove/by/id
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Remove a test result according to the test id provided
        description: ''
        operationId: resultsRemoveById
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: remove result
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                  description: message
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/remove", 
                  "message": "xxxx",
                  "project-id": 25
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
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            testId = self.request.data.get("test-id")
            if testId is None: raise HTTP_400("Please specify a test id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('test not found')
            
        success = RepoArchives.instance().delDirAll(pathFolder=testPath, project='')  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove test result")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove test result (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Cannot remove test result")
            
        return { "cmd": self.request.path, "message": "test result successfully removed", 
                 'project-id': projectId }

class ResultsRemoveByDate(Handler):
    """
    /rest/results/remove/by/date
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Remove all tests results according to the date provided
        description: ''
        operationId: resultsRemoveByDate
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
              required: [ date, project-id ]
              properties:
                date:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: remove result
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
                  description: message
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/remove/by/date", 
                  "message": "xxxxxxx",
                  "project-id": 25
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
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            byDate = self.request.data.get("date")
            if byDate is None: raise HTTP_400("Please specify a date")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
                    
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success = RepoArchives.instance().delDirAll(pathFolder="%s/%s/" % (projectId, byDate), project='')  
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove all tests results")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove all tests results (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Cannot remove all tests results")
            
        return { "cmd": self.request.path, "message": "all tests results successfully removed", 
                 'project-id': projectId }

class ResultsFollow(Handler):
    """
    /rest/results/follow
    """   
    @_to_yaml  
    def post(self):
        """
        tags:
          - results
        summary: Follow the result of one or several tests
        description: ''
        operationId: resultsFollow
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
              required: [ test-ids, project-id ]
              properties:
                test-ids:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            schema :
              properties:
                cmd:
                  type: string
                results:
                  type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/follow", 
                  "project-id": 25
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
            testIds = self.request.data.get("test-ids")
            if testIds is None: raise HTTP_400("Please specify a project id and a list of test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
          
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        results = []
        for testId in testIds:
            result = { "id": testId }
            founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
            if founded == Context.instance().CODE_NOT_FOUND: raise HTTP_404('test not found')

            state = RepoArchives.instance().getTrState(trPath=testPath)
            verdict = RepoArchives.instance().getTrResult(trPath=testPath)
            progress = RepoArchives.instance().getTrProgress(trPath=testPath)
            result["result"] = { "state": state, "verdict": verdict, "progress": progress['percent'] }

            description = RepoArchives.instance().getTrDescription(trPath=testPath)
            result.update(description)
            
            results.append(result)
        return { "cmd": self.request.path, "results": results, 'project-id': projectId}
    
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
        operationId: resultsStatus
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
              required: [ test-id, project-id ]
              properties:
                test-id:
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
            if testId is None: raise HTTP_400("Please specify a list of test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
            
        state = RepoArchives.instance().getTrState(trPath=testPath)
        progress = RepoArchives.instance().getTrProgress(trPath=testPath)
        return { "cmd": self.request.path, 'test-id': testId, 'test-status': state, 
                 'test-progress': progress['percent'] }
    
class ResultsVerdict(Handler):
    """
    /rest/results/verdict
    """
    @_to_yaml      
    def post(self):
        """
        tags:
          - results
        summary: Get the end result of the test (undefined, pass, fail).
        description: ''
        operationId: resultsVerdict
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: string
        responses:
          '200':
            description: tests end result
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
            if testId is None: raise HTTP_400("Please specify a list of test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
            
        verdict = RepoArchives.instance().getTrEndResult(trPath=testPath)
        return { "cmd": self.request.path, 'test-id': testId, 'test-verdict': verdict }

class ResultsReportReviews(Handler):
    """
    /rest/results/report/reviews
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get all report reviews
        description: ''
        operationId: resultsReportReviews
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string
        responses:
          '200':
            description: all test reports
            schema :
              properties:
                cmd:
                  type: string
                test-report:
                  type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/report/reviews", 
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "basic-review": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "review": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV...."
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
            if testId is None: raise HTTP_400("Please specify a test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
                
            _replayId = self.request.data.get("replay-id", 0)    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        ret = { "cmd": self.request.path, 'test-id': testId }
        
        # reviews
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="tbrp")
        if success == Context.instance().CODE_OK:
            ret["basic-review"] = report
 
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="trp")
        if success == Context.instance().CODE_OK:
            ret["review"] = report
 
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId, 
                                                                         trExt="trpx")
        if success == Context.instance().CODE_OK:
            ret["xml-review"] = report

        return ret

class ResultsReportVerdicts(Handler):
    """
    /rest/results/report/verdicts
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get all report verdicts.
        description: ''
        operationId: resultsReportVerdicts
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string
        responses:
          '200':
            description: all test reports
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
                  "cmd": "/results/reports", 
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "verdict": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "xml-verdict": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV...."
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
            if testId is None: raise HTTP_400("Please specify a test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
                
            _replayId = self.request.data.get("replay-id", 0)    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        ret = { "cmd": self.request.path, 'test-id': testId }
        
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="trv")
        if success == Context.instance().CODE_OK:
            ret["verdict"] = report
        else:
            self.error("Error to get csv verdict report from test result")
            
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="tvrx")
        if success == Context.instance().CODE_OK:
            ret["xml-verdict"] = report
        else:
            self.error("Error to get csv verdict report from test result")

        return ret

class ResultsReportDesigns(Handler):
    """
    /rest/results/report/designs
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get all report designs
        description: ''
        operationId: resultsReportDesigns
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string
        responses:
          '200':
            description: all test reports
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
                  "cmd": "/results/reports", 
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "design": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "xml-design": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV...."
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
            if testId is None: raise HTTP_400("Please specify a test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
                
            _replayId = self.request.data.get("replay-id", 0)    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        ret = { "cmd": self.request.path, 'test-id': testId }

        # designs
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId, 
                                                                         trExt="trd")
        if success == Context.instance().CODE_OK:
            ret["design"] = report
        else:
            self.error("Error to get xml report from test result")
            
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId, 
                                                                         trExt="tdsx")
        if success == Context.instance().CODE_OK:
            ret["xml-design"] = report
        else:
            self.error("Error to get xml report from test result")

        return ret

class ResultsReportComments(Handler):
    """
    /rest/results/report/comments
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get all comments in one report
        description: ''
        operationId: resultsReportComments
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string
        responses:
          '200':
            description: all test reports
            schema :
              properties:
                cmd:
                  type: string
                comments:
                  type: string
                  description: in base64 and gzipped
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/reports", 
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "comments": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
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
            if testId is None: raise HTTP_400("Please specify a test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
                
            _replayId = self.request.data.get("replay-id", 0)    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        ret = { "cmd": self.request.path, 'test-id': testId }
        
        # comments
        success, report = RepoArchives.instance().getTrComments(trPath=testPath, replayId=_replayId)
        if success == Context.instance().CODE_OK:
            ret["comments"] = report
        else:
            self.error("Error to get comments from test result")
         
        return ret

class ResultsReportEvents(Handler):
    """
    /rest/results/report/events
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get a report of events occured during the test
        description: ''
        operationId: resultsReportEvents
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string
        responses:
          '200':
            description: all test reports
            schema :
              properties:
                cmd:
                  type: string
                events:
                  type: string
                  description: in base64 and gzipped
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/reports", 
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "events": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV...."
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
            if testId is None: raise HTTP_400("Please specify a test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
                
            _replayId = self.request.data.get("replay-id", 0)    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        ret = { "cmd": self.request.path, 'test-id': testId }

        # events
        success, report = RepoArchives.instance().getTrResume(trPath=testPath, replayId=_replayId)
        if success == Context.instance().CODE_OK:
            ret["events"] = report
        else:
            self.error("Error to get events from test result")
            
        return ret
        
class ResultsReports(Handler):
    """
    /rest/results/reports
    """
    @_to_yaml  
    def post(self):
        """
        tags:
          - reports
        summary: Get all reports of one test (advanced and basic in all formats).
        description: ''
        operationId: resultsReports
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string
        responses:
          '200':
            description: all test reports
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
                  "cmd": "/results/reports", 
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "basic-review": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "review": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "verdict": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "xml-verdict": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "design": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "xml-design": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "comments": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "events": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV...."
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
            if testId is None: raise HTTP_400("Please specify a test id")
                
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
                
            _replayId = self.request.data.get("replay-id", 0)    
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')
        
        ret = { "cmd": self.request.path, 'test-id': testId }
        
        # reviews
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="tbrp")
        if success == Context.instance().CODE_OK:
            ret["basic-review"] = report

        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="trp")
        if success == Context.instance().CODE_OK:
            ret["review"] = report

        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId, 
                                                                         trExt="trpx")
        if success == Context.instance().CODE_OK:
            ret["xml-review"] = report

        # verdicts
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="trv")
        if success == Context.instance().CODE_OK:
            ret["verdict"] = report

        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId,
                                                                         trExt="tvrx")
        if success == Context.instance().CODE_OK:
            ret["xml-verdict"] = report

        # designs
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId, 
                                                                         trExt="trd")
        if success == Context.instance().CODE_OK:
            ret["design"] = report
  
        success, report = RepoArchives.instance().getTrReportByExtension(trPath=testPath, 
                                                                         replayId=_replayId, 
                                                                         trExt="tdsx")
        if success == Context.instance().CODE_OK:
            ret["xml-design"] = report

        # comments
        success, report = RepoArchives.instance().getTrComments(trPath=testPath, replayId=_replayId)
        if success == Context.instance().CODE_OK:
            ret["comments"] = report

        # events
        success, report = RepoArchives.instance().getTrResume(trPath=testPath, replayId=_replayId)
        if success == Context.instance().CODE_OK:
            ret["events"] = report
 
        return ret

class ResultsCommentAdd(Handler):
    """
    /rest/results/comment/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Add a comment in a test result
        description: ''
        operationId: resultsCommentAdd
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
              required: [ test-id, comment, timestamp, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string 
                comment:
                  type: string
                timstamp:
                  type: string
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                result:
                  type: string
                  description: in base64
                result-name:
                  type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/download/result", 
                  "result": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "result-name": "....",
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "save-as": False,
                  "save-as-dest: ""
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result by id not found
          '500':
            description: Server error 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            comment = self.request.data.get("comment")
            timestamp = self.request.data.get("timestamp")
            if projectId is None: raise EmptyValue("Please specify a project id")
            if comment is None: raise EmptyValue("Please specify the comment to add")
            if timestamp is None: raise EmptyValue("Please specify a timestamp")

            testId = self.request.data.get("test-id")
            if testId is None: raise EmptyValue("Please specify a project id and test id")

            _replayId = self.request.data.get("replay-id", 0)  
            _returnAll = self.request.data.get("return-all", True)  
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result by id not found')

        founded, trName = RepoArchives.instance().getTrName(trPath=testPath, replayId=_replayId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('trx not found')

        success, _,_, comments = RepoArchives.instance().addComment( archiveUser=user_profile['login'], 
                                                             archivePath="%s/%s" % (testPath,trName), 
                                                             archivePost=comment, 
                                                             archiveTimestamp=timestamp )
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to add comment")
        
        rsp = { "cmd": self.request.path, 'test-id': testId, 'project-id': projectId }
        if _returnAll:
            rsp["comments"] = comments
        else:
            rsp["comments"] = []
        return rsp

class ResultsCommentsRemove(Handler):
    """
    /rest/results/comment/remove/all
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - results
        summary: Remove all comments in test result
        description: ''
        operationId: resultsCommentsRemoveAll
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
              required: [ test-id, project-id ]
              properties:
                test-id:
                  type: string
                project-id:
                  type: integer
                replay-id:
                  type: string 
        responses:
          '200':
            description: 
            schema :
              properties:
                cmd:
                  type: string
                result:
                  type: string
                  description: in base64
                result-name:
                  type: string
                project-id:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/results/download/result", 
                  "result": "eJztfHnPq9iZ5/+R+ju8qqiVbjkV....",
                  "result-name": "....",
                  "test-id": "7dcc4836-e989-49eb-89b7-5ec1351d2ced",
                  "save-as": False,
                  "save-as-dest: ""
                }
          '400':
            description: Bad request provided
          '403':
            description: Access denied to this project
          '404':
            description: Test result by id not found
          '500':
            description: Server error 
        """
        user_profile = _get_user(request=self.request)
        
        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")

            testId = self.request.data.get("test-id")
            if testId is None: raise EmptyValue("Please specify a project id and test id")

            _replayId = self.request.data.get("replay-id", 0)  

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
        
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        # extract the real test path according the test id
        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId, testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result by id not found')

        founded, trName = RepoArchives.instance().getTrName(trPath=testPath, replayId=_replayId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('trx not found')

        success, _ = RepoArchives.instance().delComments( archivePath="%s/%s" % (testPath,trName) )
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to delete all comments")
            
        return  { "cmd": self.request.path, 
                  'test-id': testId, 
                  'project-id': projectId, 
                  "message": "all comments deleted" }

"""
Metrics handlers
"""
class MetricsTestsWritingDuration(Handler):
    """
    /rest/metrics/tests/duration/writing
    """
    @_to_yaml      
    def post(self):
        """
        tags:
          - metrics
        summary: add the duration of developpement for a test
        description: ''
        operationId: metricsTestsDurationWriting
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
              required: [ project-id, duration, is-ta, is-tu, is-ts, is-tp, is-tg ]
              properties:
                project-id:
                  type: integer
                duration:
                  type: integer
                is-ta:
                  type: boolean
                is-tu:
                  type: boolean
                is-ts:
                  type: boolean    
                is-tp:
                  type: boolean      
                is-tg:
                  type: boolean                        
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
                  "cmd": "/metrics/tests/duration/writing", 
                  "message": "duration added"
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None: raise EmptyValue("Please specify a project id")
            
            duration = self.request.data.get("duration")
            if duration is None: raise EmptyValue("Please specify a duration")
            
            isTs = self.request.data.get("is-ts")
            if isTs is None: raise EmptyValue("Please specify a source is ts")
            
            isTu = self.request.data.get("is-tu")
            if isTu is None: raise EmptyValue("Please specify a source is tu")
            
            isTa = self.request.data.get("is-ta")
            if isTa is None: raise EmptyValue("Please specify a source is ta")
            
            isTp = self.request.data.get("is-tp")
            if isTp is None: raise EmptyValue("Please specify a source is tp")
            
            isTg = self.request.data.get("is-tg")
            if isTg is None: raise EmptyValue("Please specify a source is tg")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)
            
        _check_project_permissions(user_login=user_profile['login'], project_id=projectId)

        success = StatsManager.instance().addWritingDuration(   
                                                                fromUser=user_profile['id'], 
                                                                prjId=projectId,
                                                                writingDuration=duration, 
                                                                isTs=isTs,
                                                                isTp=isTp, 
                                                                isTu=isTu, 
                                                                isTg=isTg,
                                                                isTa=isTa
                                                            )
        if not success:
            raise HTTP_500("unable to save duration in table")
            
        return { "cmd": self.request.path, 'message': 'duration added' }
