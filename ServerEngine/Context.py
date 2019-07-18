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

import time
import sys
import threading
import os
import zlib
import base64
import copy
import subprocess
from datetime import timedelta

import hashlib
import json

import platform
import base64
import uuid

try:
    import DbManager
    import UsersManager
    import ProjectsManager
    import Common
except ImportError:  # python3 support
    from . import DbManager
    from . import UsersManager
    from . import ProjectsManager
    from . import Common

from Libs import Settings, Logger
from ServerInterfaces import EventServerInterface as ESI
from ServerRepositories import (RepoTests)


# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class UserContext(Logger.ClassLogger):
    """
    """

    def __init__(self, login):
        """
        Class to construct a user context
        """
        self.trace('Preparing user context Login=%s' % login)
        self.login = login
        self.default_prj = ProjectsManager.instance().getDefaultProjectForUser(user=login)
        self.projects = ProjectsManager.instance().getProjects(user=login)
        self.trace('User context constructed Login=%s' % login)

    def __str__(self):
        """
        """
        return self.login

    def __repr__(self):
        """
        """
        return self.login

    def getDefault(self):
        """
        Return default project according to the user
        """
        return self.default_prj

    def getProjects(self, b64=False):
        """
        Return all projects 
        """
        return self.projects


class SessionExpireHandler(threading.Thread, Logger.ClassLogger):
    """
    """

    def __init__(self):
        """
        """
        threading.Thread.__init__(self)

        self.event = threading.Event()
        self.mutex = threading.RLock()
        self.running = True

        self.lease = int(Settings.get(
            'Users_Session', 'max-expiry-age'))  # in seconds

        self.expire = int(Settings.get(
            'Users_Session', 'timeout-cleanup'))  # in seconds

    def run(self):
        """
        """
        while self.running:
            self.event.wait(self.expire)
            if self.running:
                self.mutex.acquire()

                # inspect sessions to delete
                sessions = []
                self.trace("Num sessions before: %s" %
                           len(instance().getSessions()))
                for (session, user) in instance().getSessions().items():
                    t = time.time()
                    max_age = user['last_activity'] + self.lease
                    if t > max_age:
                        self.trace("Delete session=%s time=%s max-age=%s" %
                                   (session, t, max_age))
                        sessions.append(session)

                # delete sessions
                for sess in sessions:
                    del instance().getSessions()[sess]

                # sessions.clear(), on with python > 3.3
                del sessions[:]

                self.trace("Num sessions after: %s" %
                           len(instance().getSessions()))

                self.mutex.release()

    def stop(self):
        """
        """
        self.mutex.acquire()
        self.running = False
        self.event.set()
        self.mutex.release()


class Context(Logger.ClassLogger):
    """
    """
    CODE_ERROR = 500
    CODE_DISABLED = 405
    CODE_NOT_FOUND = 404
    CODE_LOCKED = 421
    CODE_ALLREADY_EXISTS = 420  # error in the name, should be remove in the future
    CODE_ALREADY_EXISTS = 420
    CODE_ALLREADY_CONNECTED = 416  # error in the name, should be remove in the future
    CODE_ALREADY_CONNECTED = 416
    CODE_FORBIDDEN = 403
    CODE_FAILED = 400
    CODE_OK = 200

    def __init__(self):
        """
        Construct context server
        """
        self.__mutex__ = threading.RLock()
        self.conn_id = 0

        # {    'address' : client, 'profile': ...., 'connected-at': time.time()   }
        self.usersConnected = {}

        self.startedAt = self.formatTimestamp(timestamp=time.time())

        self.userSessions = {}
        self.handlerSesssions = SessionExpireHandler()
        self.startSessionHandler()

    def startSessionHandler(self):
        """
        """
        self.handlerSesssions.start()

    def stopSessionHandler(self):
        """
        """
        self.handlerSesssions.stop()
        self.handlerSesssions.join()

    def getSessions(self):
        """
        Return all actives users sessions
        """
        return self.userSessions

    def getUniqueId(self):
        """
        Return a unique id
        """
        self.__mutex__.acquire()
        self.conn_id += 1
        ret = self.conn_id
        self.__mutex__.release()
        return ret

    def getNbUsersConnected(self):
        """
        Returns the number of users connected

        @return: nb users connected
        @rtype: int
        """
        return len(self.usersConnected)

    def formatTimestamp(self, timestamp):
        """
        Returns human-readable time

        @param timestamp: 
        @type timestamp:

        @return: timestamp readable
        @rtype: string
        """
        ret = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) \
            + ".%3.3d  " % int((timestamp * 1000) % 1000)
        return ret

    def getUsersConnectedCopy(self):
        """
        Return a copy
        """
        return copy.deepcopy(self.usersConnected)

    def generateSessionid(self):
        """
        Returns a random, 45-character session ID.
        Example: "NzY4YzFmNDdhMTM1NDg3Y2FkZmZkMWJmYjYzNjBjM2Y5O"

        @return: 45-character session ID
        @rtype: string
        """
        uuid_val = (uuid.uuid4().hex + uuid.uuid4().hex).encode('utf-8')
        session_id = base64.b64encode(uuid_val)[:45]
        if sys.version_info > (3,):
            return session_id.decode('utf8')
        else:
            return session_id

    def apiUserIdentification(self, userLogin):
        """
        """
        usersDb = UsersManager.instance().cache()
        userProfile = None
        for _, profile in usersDb.items():
            if profile["login"].lower() == userLogin.lower():
                userProfile = profile
                break
        return userProfile

    def apiBasicAuthorization(self, authorization):
        """
        Check authorization for rest api
        New version in v17
        """
        if authorization.startswith("Basic "):
            try:
                encoded = authorization.split("Basic ")[1].strip()

                decoded = base64.b64decode(encoded)
                self.trace("Basic Auth decoded: %s" % decoded)
                apikey_id, apikey_secret = decoded.rsplit(":", 1)

                usersDb = UsersManager.instance().cache()
                userOk = None
                for _, profile in usersDb.items():
                    if profile["apikey_id"] == apikey_id and profile["apikey_secret"] == apikey_secret:
                        userOk = profile
                        break
                return userOk

            except Exception as e:
                self.error("unable to decode authorization: %s" % e)
            return None
        return None

    def apiAuthorization(self, login, password):
        """
        Check authorization for rest api
        """
        self.trace('Rest authorization called for Login=%s' % (login))
        expires = ''

        # check if this login exists on the database
        cache_users = UsersManager.instance().cache()
        if not login in cache_users:
            self.trace("Login=%s account not found" % login)
            return (self.CODE_NOT_FOUND, expires)

        user_profile = cache_users[login]

        # account disable ?
        if not user_profile['active']:
            self.trace("%s account not active" % login)
            return (self.CODE_DISABLED, expires)

        # check password, create a sha1 hash with salt: sha1( salt + sha1(password) )
        sha0 = hashlib.sha1()
        sha0.update(password.encode('utf8'))

        sha1 = hashlib.sha1()
        _pwd = "%s%s" % (Settings.get('Misc', 'salt'), sha0.hexdigest())
        sha1.update(_pwd.encode('utf8'))

        sha3 = hashlib.sha1()
        _pwd2 = "%s%s" % (Settings.get('Misc', 'salt'),
                          password.encode('utf8'))
        sha3.update(_pwd2.encode('utf8'))

        pwd_matched = False
        if user_profile['password'] == sha1.hexdigest():
            pwd_matched = True
        # keep this mode only for backward compatibility
        if user_profile['password'] == sha3.hexdigest():
            pwd_matched = True

        if not pwd_matched:
            self.trace("incorrect password for %s account" % login)
            return (self.CODE_FAILED, expires)

        session_id = self.generateSessionid()
        user_profile['last_activity'] = time.time()

        lease = int(Settings.get('Users_Session',
                                 'max-expiry-age'))  # in seconds
        end = time.gmtime(user_profile['last_activity'] + lease)
        expires = time.strftime("%a, %d-%b-%Y %T GMT", end)

        self.userSessions.update({session_id: user_profile})

        self.trace('Rest authorized for Login=%s SessionId=%s Expires=%s' %
                   (login, session_id, expires))
        return (session_id, expires)

    def updateSession(self, sessionId):
        """
        """
        if sessionId in self.userSessions:
            self.userSessions[sessionId]['last_activity'] = time.time()

            lease = int(Settings.get('Users_Session',
                                     'max-expiry-age'))  # in seconds
            end = time.gmtime(
                self.userSessions[sessionId]['last_activity'] + lease)
            expires = time.strftime("%a, %d-%b-%Y %T GMT", end)
            return expires
        return ''

    def getLevels(self, userProfile):
        """
        Return levels
        """
        levels = []
        if userProfile['administrator']:
            levels.append( "Administrator" )
        if userProfile['leader']:
            levels.append( "Monitor" )
        if userProfile['tester']:
            levels.append( "Tester" )
        return levels

    def registerUser(self, user):
        """
        Adds new user, new connection

        @param user: user description
        @type user: dict
        """
        connStart = time.time()
        connId = self.getUniqueId()
        # user = { 'address' : client, <user>:{},  'profile': <user profile> }
        self.usersConnected[user['profile']['login']] = user
        self.usersConnected[user['profile']
                            ['login']]['connected-at'] = connStart
        self.usersConnected[user['profile']['login']]['connection-id'] = connId
        self.info("User Registered: ConnectionID=%s PrivateAddress=%s Login=%s" % (connId,
                                                                                   user['address'],
                                                                                   user['profile']['login']))

        # update db
        UsersManager.instance().setOnlineStatus(
            login=user['profile']['login'], online=True)

        return True

    def unregisterChannelUser(self, login):
        """
        Force channel disconnection
        """
        self.info("Unregister user Login=%s" % login)
        UsersManager.instance().setOnlineStatus(login=login, online=False)
        if not login in self.usersConnected:
            self.trace("unregister user from api, user %s not found" % login)
            return self.CODE_NOT_FOUND
        else:
            userProfile = self.usersConnected[login]

            # close the network link with the client if exists
            if userProfile['address'] in ESI.instance().clients:
                ESI.instance().stopClient(client=userProfile['address'])
            else:
                user_removed = self.usersConnected.pop(login)
                del user_removed

        return self.CODE_OK

    def unregisterUser(self, user):
        """
        Deletes user, disconnection

        @param user: channel-id (ip, port)
        @type user: tuple
        """
        userLogin = None
        for cur_user in self.usersConnected:
            if self.usersConnected[cur_user]['address'] == user:
                userLogin = self.usersConnected[cur_user]['profile']['login']
                break
        if userLogin is None:
            self.trace('client %s not connected' % str(user))
        else:
            user_removed = self.usersConnected.pop(userLogin)
            self.info("Conn id %s: User (%s,  %s) unregistered" % (user_removed['connection-id'],
                                                                   user_removed['address'],
                                                                   userLogin))

            # update db
            UsersManager.instance().setOnlineStatus(login=userLogin, online=False)

    def getUser(self, login):
        """
        Search the user in the connected user list by the name and return it
        Return None if the user is not found

        @param user: channel-id (ip, port)
        @type user: tuple

        @return: user information
        @rtype: dict
        """
        found = None
        if not login in self.usersConnected:
            self.trace('User Login=%s connected with channel? no' % str(login))
            return found
        else:
            found = self.usersConnected[login]
        return found

    def getInformations(self, user=None, b64=False):
        """
        Returns settings on the server for the client

        @return: server settings
        @rtype: list
        """
        self.trace('construct servers information')
        ret = []
        # platform
        try:
            ret.append({'version': Settings.getVersion()})
            ret.append({'python': platform.python_version()})
            ret.append({'start-at': "%s" % self.startedAt})

            if user is not None:
                ret.append(
                    {'test-environment': self.getTestEnvironment(user=user)})

                if isinstance(user, UserContext):
                    ret.append({'projects': user.getProjects()})
                    ret.append({'default-project': user.getDefault()})
                else:
                    ret.append(
                        {'projects': ProjectsManager.instance().getProjects(user=user)})
                    ret.append(
                        {'default-project': ProjectsManager.instance().getDefaultProjectForUser(user=user)})

            for section in Settings.instance().sections():
                for (name, value) in Settings.instance().items(section):
                    ret.append(
                        {"%s-%s" % (section.lower(), name.lower()): value})

        except Exception as e:
            self.error('unable to construct servers settings: %s' % str(e))

        return ret

    def getRn(self, pathRn, b64=False):
        """
        Returns the contains of the file releasenotes.txt

        @param pathRn: 
        @type pathRn:

        @return: release notes
        @rtype: string
        """
        self.trace('opening the release note')
        rn_ret = ''
        try:
            f = open('%s/releasenotes.txt' % pathRn)
            rn_ret = f.read()
            f.close()
        except Exception as e:
            self.error("Unable to read release notes: %s" % str(e))

        return rn_ret

    def getTestEnvironment(self, user, b64=False):
        """
        Return the test environment according to the user
        """
        self.trace("Return test variables for User=%s" % user)

        if isinstance(user, UserContext):
            projects = user.getProjects()
        else:
            projects = ProjectsManager.instance().getProjects(user=user)

        testEnvironment = []
        for prj in projects:
            vars_list = RepoTests.instance().cacheVars()

            env_filtered = []
            for var in vars_list:
                if int(var['project_id']) == int(prj['project_id']):
                    env_filtered.append(
                        {'name': var['name'], 'value': var['value']})

            testEnvironment.append({'project_id': prj['project_id'],
                                    'project_name': prj['name'],
                                    'test_environment': env_filtered}
                                   )

        return testEnvironment

    def refreshTestEnvironment(self):
        """
        Refresh test environment
        And notify all connected user
        """
        for user_login, user_profile in self.usersConnected.items():
            if user_profile['profile']['administrator'] or user_profile['profile']['tester'] or \
                    user_profile['profile']['developer']:
                data = ('context-server', ("update", self.getInformations(user=user_login)))
                ESI.instance().notify(body=data, toUser=user_login)
        return True

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="CTX - %s" % txt)


CTX = None


def instance():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return CTX


def initialize():
    """
    Instance creation
    """
    global CTX
    CTX = Context()


def finalize():
    """
    Destruction of the singleton
    """
    global CTX
    if CTX:
        CTX.stopSessionHandler()
        CTX = None
