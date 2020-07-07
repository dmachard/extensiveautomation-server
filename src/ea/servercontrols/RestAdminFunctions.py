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

from pycnic.core import Handler
from pycnic.errors import HTTP_401, HTTP_400, HTTP_500, HTTP_403, HTTP_404

import os
import wrapt

from ea.libs import Settings
from ea.serverengine import (Context,
                             ProjectsManager,
                             TaskManager,
                             UsersManager,
                             VariablesManager
                             )
from ea.serverrepositories import (RepoAdapters,
                                   RepoTests,
                                   RepoArchives)
from ea.servercontrols import CliFunctions


class EmptyValue(Exception):
    pass


class HandlerCORS(Handler):
    def options(self):
        return {}


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
            userP = Context.instance().apiBasicAuthorization(authorization=authorization)
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


class TasksKillAll(HandlerCORS):
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
          '403':
            description: Access refused
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        # kill all tasks
        TaskManager.instance().killAllTasks()

        return {"cmd": self.request.path,
                "message": "tasks successfully killed"}


class TasksCancelAll(HandlerCORS):
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
          '403':
            description: Access refused
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        # kill all tasks
        TaskManager.instance().cancelAllTasks()

        return {"cmd": self.request.path,
                "message": "tasks successfully cancelled"}


class TasksHistoryClear(HandlerCORS):
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
          '403':
            description: Access refused
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        success = TaskManager.instance().clearHistory()
        if not success:
            raise HTTP_500("unable to clear the history")
        return {"cmd": self.request.path,
                "message": "tasks successfully reseted"}


class AdaptersDirectoryRemoveAll(HandlerCORS):
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
          '403':
            description: Access refused
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            folderPath = self.request.data.get("directory-path")
            if folderPath is None:
                raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath)

        success = RepoAdapters.instance().delDirAll(folderPath)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Removing directory denied")

        return {"cmd": self.request.path,
                "message": "all directories successfully removed"}


"""
Administration handlers
"""


class AdminConfigListing(HandlerCORS):
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
        responses:
          '200':
            description:
            schema :
              properties:
                cmd:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/configurationg/listing"
               }
          '403':
            description: Access refused
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        config = {}
        for section in Settings.instance().sections():
            for (name, value) in Settings.instance().items(section):
                config["%s-%s" % (section.lower(), name.lower())] = value

        return {"cmd": self.request.path, "configuration": config}


class AdminConfigReload(HandlerCORS):
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
        responses:
          '200':
            description:
            schema :
              properties:
                cmd:
                  type: string
                status:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/configuration/reload",
                  "status": "reloaded"
               }
          '403':
            description: Access refused
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        CliFunctions.instance().reload()

        return {"cmd": self.request.path, "status": "reloaded"}


class AdminProjectsListing(HandlerCORS):
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

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        success, details = ProjectsManager.instance().getProjectsFromDB()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return {"cmd": self.request.path, "projects": details}


class AdminProjectsAdd(HandlerCORS):
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

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectName = self.request.data.get("project-name")
            if projectName is None:
                raise HTTP_400("Please specify a project name")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, details = ProjectsManager.instance(
        ).addProjectToDB(projectName=projectName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALREADY_EXISTS:
            raise HTTP_403(details)

        return {"cmd": self.request.path,
                "message": "project successfully added", "project-id": details}


class AdminProjectsRename(HandlerCORS):
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
              required: [ project-name, project-id ]
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

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None:
                raise HTTP_400("Please specify a project id")

            projectName = self.request.data.get("project-name")
            if projectName is None:
                raise HTTP_400("Please specify a project name")
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
        if success == Context.instance().CODE_ALREADY_EXISTS:
            raise HTTP_403(details)

        return {"cmd": self.request.path,
                "message": "project successfully updated"}


class AdminProjectsRemove(HandlerCORS):
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

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None:
                raise HTTP_400("Please specify a project id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        if projectId == 1:
            raise HTTP_403("Remove this project is not authorized")

        success, details = ProjectsManager.instance().delProjectFromDB(projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return {"cmd": self.request.path,
                "message": "project successfully removed"}


class AdminUsersProfile(HandlerCORS):
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
              required: [ user-id ]
              properties:
                user-id:
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
                  "cmd": "/administration/users/profile"
               }
          '403':
            description: Access refused
          '404':
            description: User not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            userId = self.request.data.get("user-id")
            if userId is None:
                raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        if int(userId) != int(
                user_profile["id"]) and not user_profile['administrator']:
            raise HTTP_403("Access refused")
        else:
            success, details = UsersManager.instance().getUserProfile(userId=userId)
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500(details)

        return {"cmd": self.request.path, "user": details}


class AdminUsersListing(HandlerCORS):
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
                  "cmd": "/administration/users/listing"
               }
          '403':
            description: Access refused
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        success, details_users = UsersManager.instance().getUsersFromDB()
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details_users)

        code, details_relations = UsersManager.instance().getRelationsFromDB()
        if code == Context.instance().CODE_ERROR:
            raise HTTP_500(details_relations)

        try:
            for user in details_users:
                # cleanup result
                # all these keys will be remove in future
                if user["tester"]:
                    user["level"] = "tester"
                if user["monitor"]:
                    user["level"] = "monitor"
                if user["administrator"]:
                    user["level"] = "administrator"
                del user["tester"]
                del user["monitor"]
                del user["administrator"]

                # add projects relations in user profile
                user_projects = []
                for relation in details_relations:
                    if relation['user_id'] == user['id']:
                        user_projects.append(relation['project_id'])
                user['projects'] = user_projects
        except Exception as e:
            raise HTTP_500("error to read user list: %s" % e)

        return {"cmd": self.request.path, "users": details_users}


class AdminUsersAdd(HandlerCORS):
    """
    /rest/administration/users/add
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - admin
        summary: Add a new user in the server
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
              required: [ login, password, email, level, lang, style, notifications, default, projects ]
              properties:
                login:
                  type: string
                password:
                  type: string
                email:
                  type: string
                level:
                  type: string
                  description: administrator or monitor or tester
                lang:
                  type: string
                  description: en or fr
                style:
                  type: string
                  description: default
                notifications:
                  type: string
                  description: "false;false;false;false;false;false;false;"
                default:
                  type: integer
                  description: default project id
                projects:
                  type: array
                  description: list of project id
                  items:
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
                  "cmd": "/administration/users/add",
                  "message: "user successfully added"
               }
          '400':
            description: Bad request provided
          '404':
            description: User not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            login = self.request.data.get("login")
            if not login:
                raise EmptyValue("Please specify a login")

            password = self.request.data.get("password")
            if password is None:
                raise EmptyValue("Please specify a password")

            email = self.request.data.get("email")
            if email is None:
                raise EmptyValue("Please specify a email")

            level = self.request.data.get("level")
            if level is None:
                raise EmptyValue("Please specify a level")

            defaultPrj = self.request.data.get("default")
            if defaultPrj is None:
                raise EmptyValue("Please specify a default project")

            listPrjs = self.request.data.get("projects")
            if listPrjs is None:
                raise EmptyValue("Please specify a list of authorized project")

            lang = self.request.data.get("lang")
            if lang is None:
                raise EmptyValue("Please specify a lang")

            style = self.request.data.get("style")
            if style is None:
                raise EmptyValue("Please specify a style")

            notifications = self.request.data.get("notifications")
            if notifications is None:
                raise EmptyValue("Please specify a notifications")

        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, details = UsersManager.instance().addUserToDB(
            level=level,
            login=login,
            password=password,
            email=email,
            lang=lang,
            style=style,
            notifications=notifications,
            defaultPrj=defaultPrj,
            listPrjs=listPrjs
        )
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ALREADY_EXISTS:
            raise HTTP_500(details)

        return {"cmd": self.request.path,
                "message": "user successfully added", "user-id": details}


class AdminUsersRemove(HandlerCORS):
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
              required: [ user-id ]
              properties:
                user-id:
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
                  "cmd": "/administration/users/remove",
                  "message: "user successfully removed"
               }
          '400':
            description: Bad request provided
          '403':
            description: Not authorized
          '404':
            description: User not found
          '500':
            description: Unable to remove the user
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            userId = self.request.data.get("user-id")
            if userId is None:
                raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(userId, int):
            raise HTTP_400("Bad user id provided in request, int expected")

        # him self deletion deny
        if int(userId) == int(user_profile["id"]):
            raise HTTP_403("deletion not authorized")

        success, details = UsersManager.instance().delUserInDB(userId=userId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return {"cmd": self.request.path,
                "message": "user successfully removed"}


class AdminUsersStatus(HandlerCORS):
    """
    /rest/administration/users/status
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - admin
        summary: Set the status of the user (enabled or not)
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
              required: [ user-id, enabled ]
              properties:
                user-id:
                  type: integer
                enabled:
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
                  "cmd": "/administration/users/status",
                  "message: "probe successfully disconnected"
               }
          '400':
            description: Bad request provided
          '404':
            description: User not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            userId = self.request.data.get("user-id")
            if userId is None:
                raise HTTP_400("Please specify a user id")

            enabled = self.request.data.get("enabled")
            if enabled is None:
                raise HTTP_400(
                    "Please specify status of the user, enabled parameter")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(userId, int):
            raise HTTP_400("Bad user id provided in request, int expected")
        if not isinstance(enabled, int):
            raise HTTP_400(
                "Bad enabled parameter provided in request, int expected")

        # update
        success, details = UsersManager.instance().updateStatusUserInDB(userId=userId,
                                                                        status=enabled)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        if enabled:
            return {"cmd": self.request.path,
                    "message": "user successfully enabled"}
        else:
            return {"cmd": self.request.path,
                    "message": "user successfully disabled"}


class AdminUsersChannelDisconnect(HandlerCORS):
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

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            userLogin = self.request.data.get("login")
            if userLogin is None:
                raise HTTP_400("Please specify a login")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        disconnected = Context.instance().unregisterChannelUser(login=userLogin)
        if disconnected == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("user not found")

        return {"cmd": self.request.path,
                "message": "user successfully disconnected"}


class AdminUsersDuplicate(HandlerCORS):
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
              required: [ user-id ]
              properties:
                user-id:
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
                  "cmd": "/administration/users/duplicate",
                  "message: "user successfully duplicated"
               }
          '400':
            description: Bad request provided
          '404':
            description: User not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            userId = self.request.data.get("user-id")
            if userId is None:
                raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(userId, int):
            raise HTTP_400("Bad user id provided in request, int expected")

        success, details = UsersManager.instance().duplicateUserInDB(userId=userId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return {"cmd": self.request.path,
                "message": "user successfully duplicated", "user-id": details}


class AdminUsersPasswordReset(HandlerCORS):
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
              required: [ user-id ]
              properties:
                user-id:
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
                  "cmd": "/administration/users/password/reset",
                  "message: "password successfully reseted"
               }
          '400':
            description: Bad request provided
          '404':
            description: User not found
          '500':
            description: Unable to reset the password
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            userId = self.request.data.get("user-id")
            if userId is None:
                raise HTTP_400("Please specify a user id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(userId, int):
            raise HTTP_400("Bad user id provided in request, int expected")

        success, details = UsersManager.instance().resetPwdUserInDB(userId=userId)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return {"cmd": self.request.path,
                "message": "password successfully reseted"}


class AdminUsersSearch(HandlerCORS):
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
              properties:
                user-id:
                  type: integer
                login:
                  type: string
        responses:
          '200':
            description:
            schema :
              properties:
                cmd:
                  type: string
            examples:
              application/json: |
                {
                  "cmd": "/administration/users/search"
               }
          '400':
            description: Bad request provided
          '403':
            description: Access refused
          '404':
            description: User not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            userLogin = self.request.data.get("login")
            userId = self.request.data.get("user-id")

            if userLogin is None and userId is None:
                raise EmptyValue("Please specify the name or id of the user")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, details = UsersManager.instance().getUserFromDB(
            userId=userId, userLogin=userLogin)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_404("no user found")

        if len(details) == 1:
            return {"cmd": self.request.path, "user": details[0]}
        else:
            return {"cmd": self.request.path, "users": details}


class TestsDirectoryRemoveAll(HandlerCORS):
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
            description: Access refused
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None:
                raise EmptyValue("Please specify a project id")

            folderPath = self.request.data.get("directory-path")
            if folderPath is None:
                raise EmptyValue("Please specify a source folder path")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(projectId, int):
            raise HTTP_400("Bad project id provided in request, int expected")

        # avoid directory traversal
        folderPath = os.path.normpath("/" + folderPath)

        success = RepoTests.instance().delDirAll(folderPath, projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to remove directory")
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to remove directory (missing)")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("Removing directory denied")

        return {"cmd": self.request.path, "message": "all directories successfully removed",
                "project-id": projectId}


class TestsSnapshotRemoveAll(HandlerCORS):
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
            description: Access refused
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None:
                raise EmptyValue("Please specify a project id")

            testPath = self.request.data.get("test-path")
            if testPath is None:
                raise EmptyValue("Please specify a test path")
            testName = self.request.data.get("test-name")
            if testName is None:
                raise EmptyValue("Please specify a test name")
            testExt = self.request.data.get("test-extension")
            if testExt is None:
                raise EmptyValue("Please specify a test extension")

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

        success = RepoTests.instance().deleteAllSnapshots(testPath=testPath,
                                                          testPrjId=projectId,
                                                          testName=testName,
                                                          testExt=testExt
                                                          )
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_500("Unable to find the test provided")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("Unable to delete all snapshots")

        return {"cmd": self.request.path,
                "message": "all snapshots deleted", "project-id": projectId}


"""
Variables handlers
"""


class VariablesReset(HandlerCORS):
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
            description: Access refused
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None:
                raise EmptyValue("Please specify a project id")
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

        success, details = VariablesManager.instance().delVariablesInDB(projectId=projectId)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return {"cmd": self.request.path,
                "message": "variables successfully reseted"}


"""
Tests Results handlers
"""


class ResultsReset(HandlerCORS):
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

        if not user_profile['administrator']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.data.get("project-id")
            if projectId is None:
                raise EmptyValue("Please specify a project id")
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

        return {"cmd": self.request.path, "message": "results successfully reseted",
                'project-id': projectId}
