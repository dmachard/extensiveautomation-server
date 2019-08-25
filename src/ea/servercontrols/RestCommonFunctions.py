#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
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

import wrapt
import platform

from ea.libs import Settings
from ea.serverengine import (Context,
                             ProjectsManager,
                             TaskManager,
                             AgentsManager,
                             UsersManager,
                             HelperManager )
from ea.serverrepositories import ( RepoAdapters,
                                    RepoTests,
                                    RepoArchives )

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

class HandlerCORS(Handler):
    def options(self):
        return {}

"""
Session handlers
"""
class SessionLogin(HandlerCORS):
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
        operationId: sessionLogin
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
                channel-id:
                  type: string
                client-version:
                  type: string
                client-platform:
                  type: boolean
                client-portable:
                  type: string
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
            if login is None: raise EmptyValue("Please specify login")
            if password is None: raise EmptyValue("Please specify password")

            channelId = self.request.data.get("channel-id")
            clientVersion = self.request.data.get("client-version")
            clientPlatform = self.request.data.get("client-platform")
            clientPortable = self.request.data.get("client-portable")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # check user access
        (userSession, expires) = Context.instance().apiAuthorization(login=login,
                                                                     password=password)

        if userSession == Context.instance().CODE_NOT_FOUND:
            raise HTTP_401("Invalid credential!")

        if userSession == Context.instance().CODE_DISABLED:
            raise HTTP_401("Account disabled!")

        if userSession == Context.instance().CODE_FORBIDDEN:
            raise HTTP_401("Access not authorized!")

        if userSession == Context.instance().CODE_FAILED:
            raise HTTP_401("Invalid credential!")

        lease = Settings.get('Users_Session', 'max-expiry-age') #in seconds
        userProfile = Context.instance().getSessions()[userSession]

        self.response.set_cookie(key="session_id", value=userSession,
                                 expires='', path='/', domain="")

        # get levels
        levels = Context.instance().getLevels(userProfile=userProfile)

        if channelId is not None:
            if not isinstance(channelId, list):
                raise HTTP_400("Bad channel-id provided in request, list expected")
            if len(channelId) != 2:
                raise HTTP_400("Bad len channel-id provided in request, list of 2 elements expected")

            channelId = tuple(channelId)
            user = { 'address' : channelId, 'profile': userProfile }
            registered = Context.instance().registerUser(user=user)

        _rsp = {
                    "cmd": self.request.path,
                    "message":"Logged in",
                    "session_id": userSession,
                    "expires": int(lease),
                    "user_id": userProfile['id'],
                    "levels": levels,
                    "project_id":  userProfile['defaultproject'],
                    "api_login": userProfile['login'],
                    "api_secret": userProfile['apikey_secret'],
                   # "email": userProfile['email'],
                   # "projects": userProfile['projects']
                }

        _rsp["client-available"] = False
        _rsp["version"] = ''
        _rsp["name"] = ''

        return _rsp

class SessionLogout(HandlerCORS):
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
        operationId: sessionLogout
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

class SessionRefresh(HandlerCORS):
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
        operationId: sessionRefresh
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

class SessionContext(HandlerCORS):
    """
    /rest/session/context
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - session
        summary: Context session
        description: ''
        operationId: sessionContext
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
                  "context": "xxxxxxxxxxxx",
                  "cmd": "/session/context"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        context = Context.instance().getInformations(user=user_profile['login'])

        return { "cmd": self.request.path, "context": context }

class SessionContextNotify(HandlerCORS):
    """
    /rest/session/context/notify
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - session
        summary: Notify all users with context
        description: ''
        operationId: sessionContextNotify
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
                  "message": "success",
                  "cmd": "/session/context/notify"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        Context.instance().refreshTestEnvironment()

        return { "cmd": self.request.path, "message": "success" }

class SessionContextAll(HandlerCORS):
    """
    /rest/session/context/all
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - session
        summary: get full context
        description: ''
        operationId: sessionContextAll
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
                  "context": "xxxxxxxxxxxx",
                  "cmd": "/session/context"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        USER_CTX = Context.UserContext(login=user_profile["login"])

        rsp = { "cmd": self.request.path }

        rsp['agents-running'] = AgentsManager.instance().getRunning()

        rsp['projects'] = USER_CTX.getProjects()
        rsp['default-project'] = USER_CTX.getDefault()

        _, _, archs, stats_archs = RepoArchives.instance().getTree(project=USER_CTX.getDefault())
        rsp['archives'] =  archs
        rsp['stats-repo-archives'] = stats_archs

        rsp['tasks-running'] = TaskManager.instance().getRunning(user=USER_CTX)
        rsp['tasks-waiting'] = TaskManager.instance().getWaiting(user=USER_CTX)
        rsp['tasks-history'] = TaskManager.instance().getHistory(user=USER_CTX)
        rsp['tasks-enqueued'] = TaskManager.instance().getEnqueued()

        _, _, tests, stats_tests = RepoTests.instance().getTree(project=USER_CTX.getDefault() )
        rsp['repo'] = tests
        rsp['stats-repo-tests'] = stats_tests

        rsp['help'] = HelperManager.instance().getHelps()
        rsp['stats'] = {} # StatsManager.instance().getStats()

        rsp['stats-server'] = {} # Context.instance().getStats()
        rsp['backups-repo-tests'] = []
        rsp['backups-repo-adapters'] = []
        rsp['backups-repo-libraries'] = []
        rsp['backups-repo-archives'] = []

        _, _, adps, stats_adps = RepoAdapters.instance().getTree()
        rsp['repo-adp'] = adps
        rsp['stats-repo-adapters'] = stats_adps

        # _, _, libs, stats_libs = RepoLibraries.instance().getTree()
        rsp['repo-lib-adp'] = [] #libs
        rsp['stats-repo-libraries'] = {} #stats_libs

        rsp['core'] = Context.instance().getRn(pathRn=Settings.getDirExec())
        rsp['adapters'] = ''
        rsp['libraries'] = ''
        rsp['toolbox'] = ''
        rsp['informations'] = Context.instance().getInformations(user=USER_CTX)

        del USER_CTX

        return rsp

"""
Administration handlers
"""
class AdminProjectsSearchByName(HandlerCORS):
    """
    /rest/administration/projects/search/by/name
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - admin
        summary: Search a project by name
        description: ''
        operationId: adminProjectsSearchByName
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
                project:
                  type: object
            examples:
              application/json: |
                {
                  "cmd": "/administration/projects/search/by/name",
                  "project: {}
                }
          '400':
            description: Bad request provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            projectName = self.request.data.get("project-name")
            if projectName is None: raise EmptyValue("Please specify the name of the project")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        success, details = ProjectsManager.instance().getProjectFromDB(projectName=projectName)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)
        if len(details) == 0:
            raise HTTP_500("no project found")

        return { "cmd": self.request.path, "project": details[0] }

class AdminUsersPasswordUpdate(HandlerCORS):
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
              required: [ user-id, current-password, new-password ]
              properties:
                user-id:
                  type: integer
                current-password:
                  type: string
                new-password:
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
                  "cmd": "/administration/users/password/update",
                  "message: "password successfully updated"
                }
          '400':
            description: Bad request provided
          '404':
            description: User not found
          '403':
            description: Bad current password provided
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            userId = self.request.data.get("user-id")
            if userId is None : raise HTTP_400("Please specify a user id")

            currentPwd = self.request.data.get("current-password")
            if currentPwd is None : raise HTTP_400("Please specify the current password")

            newPwd = self.request.data.get("new-password")
            if newPwd is None : raise HTTP_400("Please specify the new password")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(userId, int):
            raise HTTP_400("Bad user id provided in request, int expected")

        if not user_profile['administrator']:
                if userId != user_profile['id']:
                        raise HTTP_403("Not authorized to change password")

        # update
        success, details = UsersManager.instance().updatePwdUserInDB(userId=userId,
                                                                     newPwd=newPwd,
                                                                     curPwd=currentPwd)
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403(details)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "password successfully updated" }

class AdminUsersUpdate(HandlerCORS):
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
              required: [ user-id ]
              properties:
                user-id:
                  type: integer
                login:
                  type: string
                password:
                  type: string
                email:
                  type: string
                level:
                  type: string
                lang:
                  type: string
                style:
                  type: string
                notifications:
                  type: string
                default:
                  type: integer
                projects:
                  type: array
                  items:
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
                  "cmd": "/administration/users/update",
                  "message: "user successfully updated"
                }
          '400':
            description: Bad request provided
          '404':
            description: User not found
          '500':
            description: Server error
        """
        user_profile = _get_user(request=self.request)

        try:
            userId = self.request.data.get("user-id")
            if userId is None : raise HTTP_400("Please specify a user id")

            login = self.request.data.get("login")
            email = self.request.data.get("email")
            level = self.request.data.get("level")
            lang = self.request.data.get("lang")
            style = self.request.data.get("style")
            notifications = self.request.data.get("notifications")
            default = self.request.data.get("default")
            projects = self.request.data.get("projects", [])
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(userId, int):
            raise HTTP_400("Bad user id provided in request, int expected")

        if user_profile['administrator']:
            def_valid = False
            if default is not None:
                for prj in projects:
                    if int(prj)  == int(default):
                        def_valid = True
                if not def_valid:
                    raise HTTP_403("Access denied to this project as default")

            success, details = UsersManager.instance().updateUserInDB(userId=userId,
                                                                  email=email,
                                                                  login=login,
                                                                  level=level,
                                                                  lang=lang,
                                                                  style=style,
                                                                  notifications=notifications,
                                                                  default=default,
                                                                  projects=projects)
        else:
            if userId != user_profile['id']:
                raise HTTP_403("Not authorized to change notifications for other user")
            success, details = UsersManager.instance().updateUserInDB(userId=userId,
                                                                      notifications=notifications)

        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404(details)
        if success == Context.instance().CODE_ALREADY_EXISTS:
            raise HTTP_500(details)
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500(details)

        return { "cmd": self.request.path, "message": "user successfully updated" }

class SystemAbout(HandlerCORS):
    """
    /rest/system/about
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - system
        summary: get system about
        description: ''
        operationId: systemAbout
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
                about:
                  type: object
                  properties:
                    changelogs:
                      type: object
                      properties:
                        core:
                          type: string
                    version:
                      type: object
                      properties:
                        core:
                          type: string
                        python:
                          type: string
                    networking:
                      type: string
            examples:
              application/json: |
                {
                  "about": { 'rn': '...', 'core': '...', 'version': '...'},
                  "cmd": "/system/about"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        about = {}

        rn = {}
        rn['core'] = Context.instance().getRn(pathRn=Settings.getDirExec())

        versions = {}
        versions["core"] = Settings.getVersion()
        versions["python"] = platform.python_version()

        about["changelogs"] = rn
        about["version"] = versions

        return { "cmd": self.request.path, "about": about }

class SystemStatus(HandlerCORS):
    """
    /rest/system/status
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - system
        summary: get system status
        description: ''
        operationId: systemStatus
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
                status:
                  type: string
            examples:
              application/json: |
                {
                  "status": 'OK',
                  "cmd": "/system/status"
                }
          '401':
            description: Access denied
        """
        return { "cmd": self.request.path, "status": "OK" }

"""
Tasks handlers
"""
class TasksRunning(HandlerCORS):
    """
    /rest/tasks/running
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - tasks
        summary: Get all my running tasks or all with admin level
        description: ''
        operationId: tasksRunning
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
                  items:
                    type: integer
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

        _userCtx = Context.UserContext(login=user_profile['login'])
        if user_profile['administrator']: _userCtx = None

        running = TaskManager.instance().getRunning(user=_userCtx)
        return { "cmd": self.request.path, "tasks-running": running }

class TasksWaiting(HandlerCORS):
    """
    /rest/tasks/waiting
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - tasks
        summary: Get all my waiting tasks or all with admin level
        description: ''
        operationId: tasksWaiting
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
                  items:
                    type: string
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

        _userCtx = Context.UserContext(login=user_profile['login'])
        if user_profile['administrator']: _userCtx = None

        waiting = TaskManager.instance().getWaiting(user=_userCtx)
        return { "cmd": self.request.path, "tasks-waiting": waiting }

class TasksHistory(HandlerCORS):
    """
    /rest/tasks/history
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - tasks
        summary: Get my partial history tasks or all with admin level
        description: ''
        operationId: tasksHistory
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
                  items:
                    type: string
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

        _userCtx = Context.UserContext(login=user_profile['login'])
        if user_profile['administrator']: _userCtx = None

        history = TaskManager.instance().getHistory(user=_userCtx)
        return { "cmd": self.request.path, "tasks-history": history }

class TasksHistoryAll(HandlerCORS):
    """
    /rest/tasks/history/all
    """
    @_to_yaml
    def get(self):
        """
        tags:
          - tasks
        summary: Get all my history tasks or all with admin level
        description: ''
        operationId: tasksHistoryAll
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
                  items:
                    type: string
            examples:
              application/json: |
                {
                  "tasks-history": [],
                  "cmd": "/tasks/history/all"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        _userCtx = Context.UserContext(login=user_profile['login'])
        if user_profile['administrator']: _userCtx = None

        history = TaskManager.instance().getHistory(Full=True, user=_userCtx)
        return { "cmd": self.request.path, "tasks-history": history }

class TasksCancel(HandlerCORS):
    """
    /rest/tasks/cancel
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: Cancel one specific task according to the id
        description: ''
        operationId: tasksCancel
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
            description: Task successfully cancelled
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task successfully cancelled",
                  "cmd": "/tasks/cancel"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        # kill all task
        success = TaskManager.instance().cancelTask(taskId=taskId, userName=_userName)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("unable to kill the task")

        return { "cmd": self.request.path, "message": "task successfully cancelled", 'task-id': taskId }

class TasksCancelSelective(HandlerCORS):
    """
    /rest/tasks/cancel/selective
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: Cancel one or more tasks according to the id
        description: ''
        operationId: tasksCancelSelective
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
              required: [ tasks-id ]
              properties:
                tasks-id:
                  type: array
                  description: list of tasks id to cancel
                  items:
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
                  "cmd": "/tasks/cancel/selective"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            tasksId = self.request.data.get("tasks-id")
            if tasksId is None: raise EmptyValue("Please specify tasks-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(tasksId, list):
            raise HTTP_400("Bad tasks id provided in request, list expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        # cancel selective tasks
        for taskId in tasksId:
            success = TaskManager.instance().cancelTask(taskId=taskId, userName=_userName)
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_404("task id not found")
            if success == Context.instance().CODE_FORBIDDEN:
                raise HTTP_403("access denied to this task")
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500("unable to cancel the task")

        return { "cmd": self.request.path, "message": "tasks successfully cancelled" }

class TasksKill(HandlerCORS):
    """
    /rest/tasks/kill
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: Kill one specific task according to the id
        description: ''
        operationId: tasksKill
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
            description: Task successfully killed
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task successfully killed",
                  "cmd": "/tasks/kill"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        # kill all task
        success = TaskManager.instance().killTask(taskId=taskId, userName=_userName)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("unable to kill the task")

        return { "cmd": self.request.path, "message": "task successfully killed", 'task-id': taskId }

class TasksKillSelective(HandlerCORS):
    """
    /rest/tasks/kill/selective
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: Kill one or more tasks according to the id
        description: ''
        operationId: tasksKillSelective
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
              required: [ tasks-id ]
              properties:
                tasks-id:
                  type: array
                  description: list of tasks id to kill
                  items:
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
                  "cmd": "/tasks/kill/selective"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            tasksId = self.request.data.get("tasks-id")
            if tasksId is None: raise EmptyValue("Please specify tasks-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(tasksId, list):
            raise HTTP_400("Bad tasks id provided in request, list expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        # kill selective tasks
        for taskId in tasksId:
            success = TaskManager.instance().killTask(taskId=taskId, userName=_userName)
            if success == Context.instance().CODE_NOT_FOUND:
                raise HTTP_404("task id not found")
            if success == Context.instance().CODE_FORBIDDEN:
                raise HTTP_403("access denied to this task")
            if success == Context.instance().CODE_ERROR:
                raise HTTP_500("unable to kill the task")

        return { "cmd": self.request.path, "message": "tasks successfully killed" }

class TasksReschedule(HandlerCORS):
    """
    /rest/tasks/reschedule
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: Reschedule a test
        description: ''
        operationId: tasksReschedule
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
              required: [ task-id, task-enabled, schedule-at, schedule-repeat, probes-enabled, debug-enabled, notifications-enabled, logs-enabled, from-time, to-time  ]
              properties:
                task-id:
                  type: integer
                  description: task id to reschedule
                schedule-id:
                  type: integer
                schedule-type:
                  type: string
                  description: daily | hourly | weekly | every | at | in | now
                task-enabled:
                  type: boolean
                schedule-at:
                  type: array
                  description: [ Y,M,D,H,M,S ]
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
                  description: [ Y,M,D,H,M,S ]
                  items:
                    type: integer
                to-time:
                  type: array
                  description: [ Y,M,D,H,M,S ]
                  items:
                    type: integer
        responses:
          '200':
            description: task successfully rescheduled
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task successfully rescheduled",
                  "cmd": "/tasks/reschedule"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            scheduleType = self.request.data.get("schedule-type")
            scheduleId = self.request.data.get("schedule-id")
            taskEnabled = self.request.data.get("task-enabled")
            scheduleAt = self.request.data.get("schedule-at")
            scheduleRepeat = self.request.data.get("schedule-repeat")
            probesEnabled = self.request.data.get("probes-enabled")
            notificationsEnabled = self.request.data.get("notifications-enabled")
            logsEnabled = self.request.data.get("logs-enabled")
            debugEnabled = self.request.data.get("debug-enabled")
            fromTime = self.request.data.get("from-time")
            toTime = self.request.data.get("to-time")

            if taskId is None: raise EmptyValue("Please specify task-id")
            if taskEnabled is None: raise EmptyValue("Please specify task-boolean")

            if scheduleType is None and scheduleId is None : raise EmptyValue("Please specify schedule-type or schedule-id")
            if scheduleAt is None: raise EmptyValue("Please specify schedule-at")
            if scheduleRepeat is None: raise EmptyValue("Please specify schedule-repeat")

            if probesEnabled is None: raise EmptyValue("Please specify probes-enabled")
            if notificationsEnabled is None: raise EmptyValue("Please specify notifications-enabled")
            if logsEnabled is None: raise EmptyValue("Please specify logs-enabled")
            if debugEnabled is None: raise EmptyValue("Please specify debug-enabled")

            if fromTime is None: raise EmptyValue("Please specify from-time")
            if toTime is None: raise EmptyValue("Please specify to-time")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task-id provided in request, int expected")
        if not isinstance(taskEnabled, bool):
            raise HTTP_400("Bad task-enabled provided in request, boolean expected")
        if not isinstance(scheduleRepeat, int):
            raise HTTP_400("Bad schedule-repeat provided in request, int expected")
        if not isinstance(probesEnabled, bool):
            raise HTTP_400("Bad probes-enabled provided in request, boolean expected")
        if not isinstance(notificationsEnabled, bool):
            raise HTTP_400("Bad notifications-enabled provided in request, boolean expected")
        if not isinstance(logsEnabled, bool):
            raise HTTP_400("Bad logs-enabled provided in request, boolean expected")
        if not isinstance(debugEnabled, bool):
            raise HTTP_400("Bad debug-enabled provided in request, boolean expected")
        if len(scheduleAt) != 6:
            raise HTTP_400("Bad schedule-at provided in request, array of size 6 expected")
        if len(fromTime) != 6:
            raise HTTP_400("Bad from-time provided in request, array of size 6 expected")
        if len(toTime) != 6:
            raise HTTP_400("Bad to-time provided in request, array of size 6 expected")

        if scheduleType is not None:
            if scheduleType not in TaskManager.SCHEDULE_TYPES:
                raise HTTP_400("Bad schedule-type provided in request, string expected daily | hourly | weekly | every | at | in | now ")

        if scheduleId is None:
            scheduleId = TaskManager.SCHEDULE_TYPES[scheduleType]

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        success = TaskManager.instance().updateTask( taskId = taskId, schedType=scheduleId, schedEnabled=taskEnabled,
                                                    shedAt=scheduleAt, schedNb=scheduleRepeat, withoutProbes=probesEnabled,
                                                    debugActivated=debugEnabled, withoutNotif=notificationsEnabled,
                                                    noKeepTr=logsEnabled, schedFrom=fromTime, schedTo=toTime,
                                                    userName=_userName)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("unable to reschedule the task")

        return { "cmd": self.request.path, "message": "task successfully rescheduled" }

class TasksVerdict(HandlerCORS):
    """
    /rest/tasks/verdict
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: get the verdict as report of my task
        description: ''
        operationId: tasksVerdict
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
        responses:
          '200':
            description: task replayed with success
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task replayed with success",
                  "cmd": "/tasks/verdict"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        task = TaskManager.instance().getTaskBy( taskId = taskId, userName=_userName )
        if task == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if task == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")

        verdict = task.getTestVerdict()
        xmlVerdict = task.getTestVerdict(returnXml=True)

        return { "cmd": self.request.path, "verdict": verdict, "xml-verdict": xmlVerdict }

class TasksReview(HandlerCORS):
    """
    /rest/tasks/review
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: get the review as report of my test
        description: ''
        operationId: tasksReview
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
        responses:
          '200':
            description: task replayed with success
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task replayed with success",
                  "cmd": "/tasks/review"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        task = TaskManager.instance().getTaskBy( taskId = taskId, userName=_userName )
        if task == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if task == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")

        review = task.getTestReport()
        xmlReview = task.getTestReport(returnXml=True)

        return { "cmd": self.request.path, "review": review, "xml-review": xmlReview }

class TasksDesign(HandlerCORS):
    """
    /rest/tasks/design
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: get the design as report of my task
        description: ''
        operationId: tasksDesign
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
        responses:
          '200':
            description: task replayed with success
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task replayed with success",
                  "cmd": "/tasks/replay"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        task = TaskManager.instance().getTaskBy( taskId = taskId, userName=_userName )
        if task == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if task == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")

        design = task.getTestDesign()
        xmlDesign = task.getTestDesign(returnXml=True)

        return { "cmd": self.request.path, "design": design, "xml-design": xmlDesign }

class TasksComment(HandlerCORS):
    """
    /rest/tasks/comment
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: add a comment to the task
        description: ''
        operationId: tasksComment
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
              required: [ task-id, comment, timestamp ]
              properties:
                task-id:
                  type: integer
                comment:
                  type: string
                timestamp:
                  type: string
        responses:
          '200':
            description: task replayed with success
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "comment added with success",
                  "cmd": "/tasks/comment"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            comment = self.request.data.get("comment")
            timestamp = self.request.data.get("timestamp")

            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        task = TaskManager.instance().getTaskBy( taskId = taskId, userName=_userName )
        if task == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if task == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")

        archivePath = task.getFileResultPath()
        success, _, _, _ = RepoArchives.instance().addComment(  archiveUser=user_profile['login'],
                                                                archivePath=archivePath,
                                                                archivePost=comment,
                                                                archiveTimestamp=timestamp )
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to add comment")

        return { "cmd": self.request.path, "message": "comment added with success" }

class TasksReplay(HandlerCORS):
    """
    /rest/tasks/replay
    """
    @_to_yaml
    def post(self):
        """
        tags:
          - tasks
        summary: replay my task
        description: ''
        operationId: tastkReplay
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
        responses:
          '200':
            description: task replayed with success
            schema :
              properties:
                cmd:
                  type: string
                message:
                  type: string
            examples:
              application/json: |
                {
                  "message": "task replayed with success",
                  "cmd": "/tasks/replay"
                }
          '401':
            description: Access denied
        """
        user_profile = _get_user(request=self.request)

        try:
            taskId = self.request.data.get("task-id")
            if taskId is None: raise EmptyValue("Please specify task-id")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        # checking input
        if not isinstance(taskId, int):
            raise HTTP_400("Bad task id provided in request, int expected")

        _userName = user_profile['login']
        if user_profile['administrator']: _userName = None

        success = TaskManager.instance().replayTask( tid = taskId, userName=_userName)
        if success == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404("task id not found")
        if success == Context.instance().CODE_FORBIDDEN:
            raise HTTP_403("access denied to this task")
        if success == Context.instance().CODE_ERROR:
            raise HTTP_500("unable to replay the task")

        return { "cmd": self.request.path, "message": "task replayed with success" }
