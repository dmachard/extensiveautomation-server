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

import time
import sys
import threading
import base64
import copy
import hashlib
import platform
import uuid
import json
import urllib

try:
    LDAP_INSTALLED = True
    import ldap3
except ImportError:
    LDAP_INSTALLED = False

from ea.serverengine import DbManager
from ea.serverengine import UsersManager
from ea.serverengine import VariablesManager
from ea.serverengine import ProjectsManager
from ea.libs import Settings, Logger
from ea.serverinterfaces import EventServerInterface as ESI
from ea.serverrepositories import (RepoTests)

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class UserContext(Logger.ClassLogger):
    """
    User context
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
    Handler to expiration of the session
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
    Global context for server
    """
    CODE_ERROR = 500
    CODE_DISABLED = 405
    CODE_NOT_FOUND = 404
    CODE_LOCKED = 421
    CODE_ALREADY_EXISTS = 420
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

        # read config from database
        self.cfg_db = {}
        self.readConfigDb()

        # {'address' : client, 'profile': ....,
        # 'connected-at': time.time()  }
        self.usersConnected = {}

        self.userSessions = {}
        self.handlerSesssions = SessionExpireHandler()
        self.startSessionHandler()

    def readConfigDb(self):
        """
        """
        self.trace("Loading config from database in memory")

        sql = """SELECT * FROM `config`"""
        success, res = DbManager.instance().querySQL(query=sql,
                                                     columnName=True)
        if not success:
            raise Exception("unable to read config from database")

        # populate cfg variable
        for line in res:
            self.cfg_db[line["opt"]] = line["value"]

        del res

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

    def apiBasicAuthorization(self, authorization):
        """
        Check authorization for rest api
        New version in v17
        """
        if authorization.startswith("Basic "):
            try:
                encoded = authorization.split("Basic ")[1].strip()

                if sys.version_info < (3,):
                    decoded = base64.b64decode(encoded)
                else:
                    decoded = base64.b64decode(encoded.encode())
                    decoded = decoded.decode()
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
        if login not in cache_users:
            self.trace("Login=%s account not found" % login)
            return (self.CODE_NOT_FOUND, expires)

        user_profile = cache_users[login]

        # account disable ?
        if not user_profile['active']:
            self.trace("%s account not active" % login)
            return (self.CODE_DISABLED, expires)

        # 2 methods to authenticate the user
        # make a hash of the password and look inside the server
        # or communicate with a remote ldap authenticator

        if Settings.getInt('Users_Session',
                           'ldap-authbind') and LDAP_INSTALLED:
            auth_success = self.doLdapAuth(login, password)
            if not auth_success:
                self.trace("ldap auth failed for %s account" % login)
                return (self.CODE_FAILED, expires)

        elif Settings.getInt('Users_Session', 'ldap-authbind') and not LDAP_INSTALLED:
            self.error("python ldap3 library is not installed on your system")
            return (self.CODE_FAILED, expires)

        else:
            # check password, create a sha1 hash with salt: sha1(salt +
            # sha1(password))
            sha0 = hashlib.sha1()
            sha0.update(password.encode('utf8'))

            sha1 = hashlib.sha1()
            _pwd = "%s%s" % (self.cfg_db["auth-salt"], sha0.hexdigest())
            sha1.update(_pwd.encode('utf8'))

            sha3 = hashlib.sha1()
            _pwd2 = "%s%s" % (self.cfg_db["auth-salt"],
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

    def doLdapAuth(self, login, password):
        """
        perform bind ldap authentication
        with multiple ldaps server and ssl mode
        """
        auth_success = False

        # get ldap settings
        ldap_host_list = json.loads(Settings.get('Users_Session', 'ldap-host'))
        ldap_dn_list = json.loads(Settings.get('Users_Session', 'ldap-dn'))

        # define ldap server(s)
        servers_list = []
        for host in ldap_host_list:
            use_ssl = False
            ldap_port = 386
            # parse the url to extract scheme host and port
            url_parsed = urllib.parse.urlparse(host)

            if url_parsed.scheme == "ldaps":
                use_ssl = True
                ldap_port = 636

            if ":" in url_parsed.netloc:
                ldap_host, ldap_port = url_parsed.netloc.split(":")
            else:
                ldap_host = url_parsed.netloc

            server = ldap3.Server(ldap_host,
                                  port=int(ldap_port),
                                  use_ssl=use_ssl)
            servers_list.append(server)

        last_auth_err = ""
        for bind_dn in ldap_dn_list:
            c = ldap3.Connection(servers_list,
                                 user=bind_dn % login,
                                 password=password)

            # perform the Bind operation
            auth_success = c.bind()
            last_auth_err = c.result
            if auth_success:
                break

        if not auth_success:
            self.trace(last_auth_err)

        return auth_success

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
            levels.append("Administrator")
        if userProfile['monitor']:
            levels.append("Monitor")
        if userProfile['tester']:
            levels.append("Tester")
        return levels

    def registerUser(self, user):
        """
        Adds new user, new connection

        @param user: user description
        @type user: dict
        """
        connStart = time.time()
        connId = self.getUniqueId()

        # user = {'address' : client, <user>:{},  'profile': <user profile>}
        self.usersConnected[user['profile']['login']] = user
        self.usersConnected[user['profile']
                            ['login']]['connected-at'] = connStart
        self.usersConnected[user['profile']['login']]['connection-id'] = connId

        self.info("User Registered: ConnID=%s Addr=%s Login=%s" % (
            connId,
            user['address'],
            user['profile']['login'])
        )

        # update db
        UsersManager.instance().setOnlineStatus(login=user['profile']['login'],
                                                online=True)

        return True

    def unregisterChannelUser(self, login):
        """
        Force channel disconnection
        """
        self.info("Unregister user Login=%s" % login)
        UsersManager.instance().setOnlineStatus(login=login, online=False)
        if login not in self.usersConnected:
            self.trace("User=%s to unregister not found" % login)
            return self.CODE_NOT_FOUND

        user_profile = self.usersConnected[login]

        # close the network link with the client if exists
        if user_profile['address'] in ESI.instance().clients:
            ESI.instance().stopClient(client=user_profile['address'])
        else:
            self.usersConnected.pop(login)

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
        """
        if login not in self.usersConnected:
            self.trace('User=%s connected with channel? no' % str(login))
            return None

        # return the user profile
        return self.usersConnected[login]

    def getInformations(self, user):
        """
        Returns settings on the server for the client
        """
        self.trace('construct servers information')
        ret = []

        # get project and default one according to the user
        if isinstance(user, UserContext):
            user_projects = user.getProjects()
            user_def_project = user.getDefault()
        else:
            user_projects = ProjectsManager.instance().getProjects(user=user)
            user_def_project = ProjectsManager.instance().getDefaultProjectForUser(user=user)

        # append informations in the list to return
        ret.append({'version': Settings.getVersion()})
        ret.append({'python': platform.python_version()})
        ret.append({'test-environment': self.getTestEnvironment(user=user)})
        ret.append({'projects': user_projects})
        ret.append({'default-project': user_def_project})

        return ret

    def getRn(self, pathRn):
        """
        Returns the contains of the file releasenotes.txt
        """
        with open('%s/releasenotes.txt' % pathRn, 'r') as f:
            return f.read()

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
            vars_list = VariablesManager.instance().cacheVars()

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
            data = (
                'context-server',
                ("update",
                 self.getInformations(
                     user=user_login)))
            ESI.instance().notify(body=data, toUser=user_login)
        return True


CTX = None


def instance():
    """
    Returns the singleton
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
