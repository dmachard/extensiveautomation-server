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
    import StatsManager
    import ProjectsManager
    import Common
except ImportError: # python3 support
    from . import DbManager
    from . import UsersManager
    from . import StatsManager
    from . import ProjectsManager
    from . import Common
    
from Libs import Settings, Logger
from ServerInterfaces import EventServerInterface as ESI
from ServerRepositories import ( RepoAdapters, RepoLibraries, RepoTests )


# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

def getstatusoutput(cmd):
    """
    Return (exitcode, output) of executing cmd in a shell.
    """
    try:
        data = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        exitcode = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data

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
        
        self.lease = int(Settings.get('Users_Session', 'max-expiry-age')) #in seconds
        
        self.expire = int(Settings.get('Users_Session', 'timeout-cleanup')) #in seconds
 
    def run(self):
        """
        """
        while self.running: 
            self.event.wait(self.expire)
            if self.running:
                self.mutex.acquire()
                
                # inspect sessions to delete
                sessions = []
                self.trace("Num sessions before: %s" % len(instance().getSessions()) )
                for (session, user) in instance().getSessions().items():
                    t = time.time()
                    max_age = user['last_activity'] + self.lease
                    if  t > max_age:
                        self.trace("Delete session=%s time=%s max-age=%s"  % (session, t, max_age) )
                        sessions.append(session)
                
                # delete sessions
                for sess in sessions:
                    del instance().getSessions()[sess]
                
                # sessions.clear(), on with python > 3.3
                del sessions[:]
                
                self.trace("Num sessions after: %s" % len(instance().getSessions()) )
                
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
    CODE_ERROR                = 500
    CODE_DISABLED             = 405
    CODE_NOT_FOUND            = 404
    CODE_LOCKED               = 421
    CODE_ALLREADY_EXISTS      = 420 # error in the name, should be remove in the future
    CODE_ALREADY_EXISTS       = 420
    CODE_ALLREADY_CONNECTED   = 416 # error in the name, should be remove in the future
    CODE_ALREADY_CONNECTED    = 416
    CODE_FORBIDDEN            = 403
    CODE_FAILED               = 400
    CODE_OK                   = 200

    LANG_EN                   = 0
    LANG_FR                   = 1
    def __init__(self):
        """
        Construct context server
        """
        self.__mutex__ = threading.RLock()
        self.table_name = '%s-config' % Settings.get( 'MySql', 'table-prefix')
        self.conn_id = 0

        self.opts = {} # dynamic configuration
        self.usersConnected = {} # {    'address' : client, 'profile': ...., 'connected-at': time.time()   }
        
        self.startedAt = None
        self.mysqlVersion = None
        self.apacheVersion = None
        self.phpVersion = None
        self.networkInterfaces = None
        self.networkRoutes = None
        
        # new in v12.2
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
        
    def setPhpVersion(self):
        """
        Set apache version
        """
        try:
            phpVersion = subprocess.check_output( 'php -v', stderr=subprocess.STDOUT, shell=True )
            phpVersion = phpVersion.strip()
            
            if sys.version_info > (3,):
                phpVersion = phpVersion.decode('utf8')
                
            self.trace("php version: %s" % phpVersion)
            
            lines = phpVersion.splitlines()
            self.phpVersion = (lines[0].split(' ')[1]).strip()
        except Exception as e:
            self.error( 'unable to set php version: %s' % str(e) )
            self.phpVersion  = "Unknown"

    def setApacheVersion(self):
        """
        Set apache version
        """
        try:
            versionHttpd = subprocess.check_output( 'httpd -v', stderr=subprocess.STDOUT, shell=True )
            versionHttpd = versionHttpd.strip()
            if sys.version_info > (3,):
                versionHttpd = versionHttpd.decode('utf8')
                
            self.trace("httpd version: %s" % versionHttpd)
            
            lines = versionHttpd.splitlines()
            self.apacheVersion = (lines[0].split(': ')[1]).strip()
        except Exception as e:
            self.error( 'unable to set apache version: %s' % str(e) )
            self.apacheVersion  = "Unknown"

    def getUsage(self, b64=False):
        """
        Return usage
        """
        ret=  {}
        try:
            ret['disk-usage'] = self.diskUsage(p= Settings.getDirExec() )
            ret['disk-usage-logs'] = self.getSize(folder= "%s/%s" % (   Settings.getDirExec(), 
                                                                        Settings.get( 'Paths', 'logs')) )
            ret['disk-usage-tmp'] = self.getSize(folder="%s/%s" % ( Settings.getDirExec(), 
                                                                    Settings.get( 'Paths', 'tmp')) )
            ret['disk-usage-testresults'] = self.getSize(folder="%s/%s" % (Settings.getDirExec(), 
                                                                            Settings.get( 'Paths', 'testsresults')) )
            ret['disk-usage-adapters'] = self.getSize(folder="%s/%s" % (Settings.getDirExec(), 
                                                                        Settings.get( 'Paths', 'adapters')) )
            ret['disk-usage-libraries'] = self.getSize(folder="%s/%s" % (Settings.getDirExec(), 
                                                                         Settings.get( 'Paths', 'libraries')) )
            ret['disk-usage-backups'] = self.getSize(folder="%s/%s" % ( Settings.getDirExec(), 
                                                                        Settings.get( 'Paths', 'backups')) )
            ret['disk-usage-tests'] = self.getSize(folder="%s/%s" % ( Settings.getDirExec(), 
                                                                      Settings.get( 'Paths', 'tests')) )
        except Exception as e:
            self.error( "unable to get server usage: %s"  % e )
        return ret

    def diskUsage(self, p):
        """
        Return the disk usage of a specific directory

        @type  p:
        @param p: string

        @return:  total/used/free
        @rtype: tuple
        """
        st = os.statvfs(p)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        return (total, used, free)

    def getUniqueId(self):
        """
        Return a unique id
        """
        self.__mutex__.acquire()
        self.conn_id += 1
        ret = self.conn_id
        self.__mutex__.release()
        return ret

    def generateAdapters(self):
        """
        Generate all tar.gz (adapters, libraries)
        """
        ret = False
        self.trace('Generating all packages adapters...')
        try:
            DEVNULL = open(os.devnull, 'w')
            sys.stdout.write( "Generate all adapters packages...\n")
            __cmd__ = "%s/Scripts/generate-adapters.sh %s/Scripts/" % (Settings.getDirExec(), 
                                                                        Settings.getDirExec())
            subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
            ret = True
        except Exception as e:
            self.error("unable to generate adapters: %s" % e)
        return ret

    def generateLibraries(self):
        """
        Generate all tar.gz (adapters, libraries)
        """
        ret = False
        self.trace('Generating all packages libraries...')
        try:
            DEVNULL = open(os.devnull, 'w')
            sys.stdout.write( "Generate all libraries packages...\n")
            __cmd__ = "%s/Scripts/generate-libraries.sh %s/Scripts/" % (Settings.getDirExec(), 
                                                                        Settings.getDirExec())
            subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
            ret = True
        except Exception as e:
            self.error("unable to generate libraries: %s" % e)
        return ret

    def generateSamples(self):
        """
        Generate all tar.gz (samples)
        """
        ret = False
        self.trace('Generating samples...')
        try:
            DEVNULL = open(os.devnull, 'w')
            sys.stdout.write( "Generate samples packages...\n") 
            __cmd__ = "%s/Scripts/generate-samples.sh %s/Scripts/" % (Settings.getDirExec(), 
                                                                      Settings.getDirExec())
            subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)
            ret = True
        except Exception as e:
            self.error("unable to generate sample: %s" % e)
        return ret

    def dynamicCfg(self, opt):
        """
        Return  dynamic config

        @param opt: option key
        @type opt: string

        @return: option value
        @rtype: string
        """
        ret = None
        try:
            ret = self.opts[opt]
        except Exception as e:
            self.error( 'unable to get opt %s in the dynamic config' % opt )
        return ret

    def synchronizeDynamicCfg(self):
        """
        Synchronize the dynamic config (dbb) with the file settings (tas.ini)
        """
        self.trace('Synchronize dynamic config')
        
        # cleanup the database config
        ret, rows = DbManager.instance().querySQL( query = """DELETE FROM `%s`""" % self.table_name)
        if not ret:
            raise Exception( 'unable to cleanup in db config' )

        ret, rows = DbManager.instance().querySQL( 
                        query = """INSERT INTO `%s` (opt, value) VALUES ('%s', '%s')""" % ( self.table_name, 
                                                                                            "paths-main" , 
                                                                                            Settings.getDirExec() ) 
                    )
        if not ret:
            raise Exception( "unable to insert main-path in db config" )

        
        ret, rows = DbManager.instance().querySQL( 
                        query = """INSERT INTO `%s` (opt, value) VALUES ('%s', '%s')""" % ( self.table_name, 
                                                                                            "server-version" , 
                                                                                            Settings.getVersion() ) 
                    )
        if not ret:
            raise Exception( "unable to insert version in db config" )

        # parse the ini file and store key and value in the db
        for section in Settings.instance().sections():
            for (name,value) in Settings.instance().items(section):
                ret, rows = DbManager.instance().querySQL(
                        query = """INSERT INTO `%s` (opt, value) VALUES ('%s', '%s')""" % (
                                self.table_name,
                                "%s-%s" % ( section.lower(), name.lower()),
                                value ) 
                        )
                if not ret:
                    raise Exception("unable to insert in db config: %s: %s %s" % (section, name, value) )
        self.trace('Dynamic config synchronized')
        self.loadDynamicCfg()

    def loadDynamicCfg(self):
        """
        Load the dynamic config from database
        """
        self.trace('Load dynamic config')
        opts = {}

        ret, rows = DbManager.instance().querySQL( query = """SELECT * FROM `%s`""" % self.table_name)
        if not ret:
            self.error( 'unable to load config from db' )
        else:
            for row in rows:
                # `id`, `opt`, `value`
                id_, opt_, value_ = row
                opts[opt_] =  value_
        
        self.opts = opts
        self.trace('Dynamic config loaded')

    def getNbUsersConnected(self):
        """
        Returns the number of users connected

        @return: nb users connected
        @rtype: int
        """
        return len(self.usersConnected)

    def getStats(self, b64=False):
        """
        Constructs some statistics on tas server
            - Space disk
            - Lines in database by table 

        @return: server statistics
        @rtype: dict
        """
        ret=  {}
        nbLinesTableUsers = 0
        try:
            ret['disk-usage'] = self.diskUsage(p= Settings.getDirExec() )
            ret['disk-usage-logs'] = self.getSize(folder= "%s/%s" % (Settings.getDirExec(), 
                                                                     Settings.get( 'Paths', 'logs')) )
            ret['disk-usage-tmp'] = self.getSize(folder="%s/%s" % ( Settings.getDirExec(), 
                                                                    Settings.get( 'Paths', 'tmp')) )
            ret['disk-usage-testresults'] = self.getSize(folder="%s/%s" % ( Settings.getDirExec(), 
                                                                            Settings.get( 'Paths', 'testsresults')) )
            ret['disk-usage-adapters'] = self.getSize(folder="%s/%s" % (Settings.getDirExec(), 
                                                                        Settings.get( 'Paths', 'adapters')) )
            ret['disk-usage-libraries'] = self.getSize(folder="%s/%s" % (Settings.getDirExec(), 
                                                                         Settings.get( 'Paths', 'libraries')) )
            ret['disk-usage-backups'] = self.getSize(folder="%s/%s" % ( Settings.getDirExec(), 
                                                                        Settings.get( 'Paths', 'backups')) )
            ret['disk-usage-tests'] = self.getSize(folder="%s/%s" % (Settings.getDirExec(), 
                                                                     Settings.get( 'Paths', 'tests')) )


            # nbLinesTableUsers = UsersManager.instance().getNbOfUsers()
            ret['nb-line-table-users'] = len(UsersManager.instance().cache())
            # self.trace( "Nb [usr=%s]" % nbLinesTableUsers)
            
            nbTests = StatsManager.instance().getNbTests()
            self.trace( "Nb tests executed [sc=%s], [tg=%s], [tp=%s], [ts=%s], [tu=%s], [ta=%s], [tc=%s]" % (
                                                    int(nbTests[0]['nbsc']),
                                                    int(nbTests[0]['nbtg']),
                                                    int(nbTests[0]['nbtp']),
                                                    int(nbTests[0]['nbts']),
                                                    int(nbTests[0]['nbtu']),
                                                    int(nbTests[0]['nbta']),
                                                    int(nbTests[0]['nbtc'])
                                                )
                      )

            ret['nb-line-table-scriptsstats'] = int(nbTests[0]['nbsc'])
            ret['nb-line-table-testplansstats'] = int(nbTests[0]['nbtp'])
            ret['nb-line-table-testsuitesstats'] = int(nbTests[0]['nbts'])
            ret['nb-line-table-testunitsstats'] = int(nbTests[0]['nbtu'])
            ret['nb-line-table-testabstractsstats'] = int(nbTests[0]['nbta'])
            ret['nb-line-table-testglobalsstats'] = int(nbTests[0]['nbtg'])
            ret['nb-line-table-testcasesstats'] = int(nbTests[0]['nbtc'])

            ret['nb-line-total'] =  nbLinesTableUsers + int(nbTests[0]['nbsc']) + int(nbTests[0]['nbtc']) \
                                    + int(nbTests[0]['nbts']) + int(nbTests[0]['nbtp']) + int(nbTests[0]['nbtu']) \
                                    + int(nbTests[0]['nbtg']) + int(nbTests[0]['nbta'])
        except Exception as e:
            self.error( "unable get statistics server: %s"  % e )

        return ret

    def getSize(self, folder):
        """
        Get the size of a specific folder in bytes

        @param folder: 
        @type folder: string

        @return: folder size
        @rtype: int
        """
        total_size = 0
        try:
            total_size = os.path.getsize(folder)
            for item in os.listdir(folder):
                itempath = os.path.join(folder, item)
                if os.path.isfile(itempath):
                    total_size += os.path.getsize(itempath)
                elif os.path.isdir(itempath):
                    total_size += self.getSize(itempath)
        except Exception as e:
            self.error( e )
        return total_size

    def setStartTime(self):
        """
        Save the start time of the server on boot
        """
        self.startedAt = self.formatTimestamp( timestamp=time.time() )

    def setMysqlVersion(self):
        """
        Save the mysql version on boot
        """
        self.mysqlVersion = DbManager.instance().getVersion()
    
    def formatTimestamp (self, timestamp):
        """
        Returns human-readable time

        @param timestamp: 
        @type timestamp:

        @return: timestamp readable
        @rtype: string
        """
        ret = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(timestamp) ) \
            + ".%3.3d  " % int(( timestamp * 1000) % 1000)
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
        session_id = base64.b64encode( uuid_val )[:45] 
        if sys.version_info > (3,):
            return session_id.decode('utf8')
        else:
            return session_id
         
    def apiAuthorizationV2(self, authorization):
        """
        Check authorization for rest api
        New version in v17
        """
        if authorization.startswith("Basic "):
            try:
                encoded = authorization.split("Basic ")[1].strip()

                decoded = base64.b64decode(encoded)
                apikey_id, apikey_secret = decoded.rsplit(":", 1)

                usersDb = UsersManager.instance().cache()
                userOk = None
                for user, profile in usersDb.items():
                    if profile["apikey_id"] == apikey_id and profile["apikey_secret"] == apikey_secret:
                        userOk = profile
                        break
                return userOk
                    
            except Exception as e:
                self.error( "unable to decode authorization: %s" % e )
            return None
        return None
       
    def apiAuthorization(self, login, password):
        """
        Check authorization for rest api
        """
        self.trace('Rest authorization called for Login=%s' % (login) )
        expires = ''
        
        # check if this login exists on the database
        usersDb = UsersManager.instance().cache()
        if not login in usersDb:
            self.trace( "Login=%s account not found" % login )
            return (self.CODE_NOT_FOUND, expires)
        
        user_profile = usersDb[login]
        
        # account disable ?
        if not user_profile['active']: 
            self.trace( "%s account not active" % login )
            return (self.CODE_DISABLED, expires)

        # check password, create a sha1 hash with salt: sha1( salt + sha1(password) )
        sha1 = hashlib.sha1()
        _pwd = "%s%s" % ( Settings.get( 'Misc', 'salt'), password )
        sha1.update( _pwd.encode('utf8')  )
        if user_profile['password'] != sha1.hexdigest():
            self.trace( "incorrect password for %s account" % login )
            return (self.CODE_FAILED, expires)
            
        session_id = self.generateSessionid()
        user_profile['last_activity'] = time.time()
        
        lease = int(Settings.get('Users_Session', 'max-expiry-age')) #in seconds
        end = time.gmtime( user_profile['last_activity'] + lease)
        expires = time.strftime("%a, %d-%b-%Y %T GMT", end)
                
        self.userSessions.update( {session_id: user_profile } )
        
        self.trace('Rest authorized for Login=%s SessionId=%s Expires=%s' % (login, session_id, expires))
        return (session_id, expires)    
    
    def updateSession(self, sessionId):
        """
        """
        if sessionId in self.userSessions:
            self.userSessions[sessionId]['last_activity'] = time.time()
        
            lease = int(Settings.get('Users_Session', 'max-expiry-age')) #in seconds
            end = time.gmtime( self.userSessions[sessionId]['last_activity'] + lease)
            expires = time.strftime("%a, %d-%b-%Y %T GMT", end) 
            return  expires
        return ''

    def getLevels(self, userProfile):
        """
        Return levels
        """
        levels = []
        if userProfile['administrator']: 
            levels.append( Settings.get('Server', 'level-admin') )
        if userProfile['leader']: 
            levels.append( Settings.get('Server', 'level-monitor') )
        if userProfile['tester']: 
            levels.append( Settings.get('Server', 'level-tester') )
        return levels

    def registerUser (self, user):
        """
        Adds new user, new connection

        @param user: user description
        @type user: dict
        """ 
        connStart = time.time()
        connId =  self.getUniqueId()
        # user = { 'address' : client, <user>:{},  'profile': <user profile> }
        self.usersConnected[ user['profile']['login'] ] = user
        self.usersConnected[ user['profile']['login'] ]['connected-at'] = connStart
        self.usersConnected[ user['profile']['login'] ]['connection-id'] = connId
        self.info( "User Registered: ConnectionID=%s PrivateAddress=%s Login=%s" % ( connId, 
                                                                                    user['address'], 
                                                                                    user['profile']['login'] ) )

        # update db
        UsersManager.instance().setOnlineStatus(login=user['profile']['login'], online=True)
        UsersManager.instance().addStats(user=user['profile']['login'], 
                                         connId=connId, 
                                         startTime=connStart, 
                                         duration=0)
    
        return True

    def unregisterChannelUser(self, login):
        """
        Force channel disconnection
        """
        self.info( "Unregister user Login=%s" % login )
        UsersManager.instance().setOnlineStatus(login=login, online=False)
        if not login in self.usersConnected:
            self.trace( "unregister user from api, user %s not found" % login )
            return self.CODE_NOT_FOUND
        else:
            userProfile = self.usersConnected[login]
            
            # close the network link with the client if exists
            if userProfile['address'] in ESI.instance().clients:
                ESI.instance().stopClient(client=userProfile['address'] )
            else:
                user_removed = self.usersConnected.pop(login)
                del user_removed
                
        return self.CODE_OK

    def unregisterUser (self, user):
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
            self.trace( 'client %s not connected' % str(user) )
        else:
            user_removed = self.usersConnected.pop(userLogin)
            self.info( "Conn id %s: User (%s,  %s) unregistered" % ( user_removed['connection-id'], 
                                                                     user_removed['address'], 
                                                                     userLogin ) )

            # update db
            UsersManager.instance().setOnlineStatus(login=userLogin, online=False)
            UsersManager.instance().addStats(   user=userLogin, connId=user_removed['connection-id'],
                                                startTime=user_removed['connected-at'],
                                                duration=time.time()-user_removed['connected-at'] )

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
            self.trace( 'User Login=%s connected with channel? no' % str(login) )
            return found
        else:
            found = self.usersConnected[login]
            # self.trace( 'User Login=%s connected with channel? yes' % str(login) )
        return found

    def getInformations(self, user=None, b64=False):
        """
        Returns settings on the server for the client

        @return: server settings
        @rtype: list
        """
        self.trace( 'construct servers information' )
        ret = []
        # platform
        try:
            ret.append( {'version': Settings.getVersion() } )
            ret.append( {'python': platform.python_version() } )
            ret.append( {'start-at': "%s" % self.startedAt } )
            ret.append( {'database': "%s" % self.mysqlVersion } )
            ret.append( {'server-web': " %s" % self.apacheVersion } )
            ret.append( {'php': " %s" % self.phpVersion } )
            if self.networkInterfaces is not None:
                ret.append( {'network': self.networkInterfaces } )
            if self.networkRoutes is not None:
                ret.append( {'routes': self.networkRoutes } )
            ret.append( {'server-date': self.getServerDateTime() } )
            ret.append( {'default-library': "%s" % RepoLibraries.instance().getDefault() } ) # dynamic value
            ret.append( {'libraries': "%s" % RepoLibraries.instance().getInstalled() } )
            ret.append( {'default-adapter': "%s" % RepoAdapters.instance().getDefault() } ) # dynamic value
            ret.append( {'adapters': "%s" % RepoAdapters.instance().getInstalled() } )

            if user is not None:
                ret.append( {'test-environment': self.getTestEnvironment(user=user) } )
                
                if isinstance(user, UserContext):
                    ret.append( {'projects': user.getProjects()  } )
                    ret.append( {'default-project': user.getDefault()  } )
                else:
                    ret.append( {'projects': ProjectsManager.instance().getProjects(user=user)  } )
                    ret.append( {'default-project': ProjectsManager.instance().getDefaultProjectForUser(user=user)  } )

            for section in Settings.instance().sections():
                for (name,value) in Settings.instance().items(section):
                    ret.append( { "%s-%s" % ( section.lower(), name.lower() ): value} )

        except Exception as e:
            self.error( 'unable to construct servers settings: %s' % str(e) )

        return  ret

    def getUptime(self):
        """
        """
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(timedelta(seconds = uptime_seconds))
        return uptime_string
        
    def getServerDateTime(self):
        """
        Returns server time and date

        @return: server date
        @rtype: string
        """
        dt = subprocess.check_output( "%s --rfc-3339=seconds" % Settings.get('Bin', 'date'), 
                                        stderr=subprocess.STDOUT, shell=True )
        dt = dt.strip()
        if sys.version_info > (3,):
            dt = dt.decode('utf8')
        self.trace( 'Date Server: %s' % dt )
        return dt

    def getRn (self, pathRn, b64=False):
        """
        Returns the contains of the file releasenotes.txt

        @param pathRn: 
        @type pathRn:

        @return: release notes
        @rtype: string
        """
        self.trace( 'opening the release note' )
        rn_ret = ''
        try:
            f = open( '%s/releasenotes.txt' % pathRn  )
            rn_ret = f.read()
            f.close()
        except Exception as e:
            self.error( "Unable to read release notes: %s" % str(e) )

        return rn_ret

    def listRoutes(self):
        """
        Discovers all routes on server

        204.62.14.0/24 dev eth0  proto kernel  scope link  src 204.62.14.177
        169.254.0.0/16 dev eth1  scope link
        10.0.0.0/8 dev eth1  proto kernel  scope link  src 10.9.1.132
        default via 204.62.14.1 dev eth0
        """
        iproute = subprocess.check_output(  Settings.get('Bin', 'iproute'), 
                                            stderr=subprocess.STDOUT, shell=True )
        iproute = iproute.strip()
        if sys.version_info > (3,):
            iproute = iproute.decode('utf8')
        self.trace( 'iproute: %s' % iproute )
        
        # save all eths
        self.networkRoutes = iproute

    def listEthsNew(self):
        """
        Discovers all network interfaces of the server
        New function because ifconfig is deprecated

        [ current]# ip addr
        1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue
            link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
            inet 127.0.0.1/8 scope host lo
        2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast qlen 1000
            link/ether 52:54:00:2a:d0:49 brd ff:ff:ff:ff:ff:ff
            inet 204.62.14.177/24 brd 204.62.14.255 scope global eth0
        3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast qlen 1000
            link/ether 52:54:00:17:18:79 brd ff:ff:ff:ff:ff:ff
            inet 10.9.1.132/8 brd 10.255.255.255 scope global eth1
        """
        eths = []

        ipaddr = subprocess.check_output( Settings.get('Bin', 'ipaddr'), 
                                          stderr=subprocess.STDOUT, shell=True )
        ipaddr = ipaddr.strip()
        if sys.version_info > (3,):
            ipaddr = ipaddr.decode('utf8')
        self.trace( 'ipaddr: %s' % ipaddr )
        
        try:
            eth_tmp = {}
            for line in ipaddr.splitlines():
                if 'link/ether' in line:
                    line_tmp = line.strip().split(' ') # link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
                    eth_tmp.update( {'mac': line_tmp[1] } )
                if 'inet ' in line:
                    line_tmp = line.strip().split(' ') # inet 204.62.14.177/24 brd 204.62.14.255 scope global eth0
                    eth_tmp.update( {'name': line_tmp[-1:][0] } )
                    eth_tmp.update( {'ip': line_tmp[1].split('/')[0] } )
                    if 'brd ' in line:
                        eth_tmp.update( {'broadcast': line_tmp[3] } )
                    else:
                        eth_tmp.update( {'broadcast': '255.0.0.0' } )
                    eth_tmp.update( {'mask': "/%s" % line_tmp[1].split('/')[1] } )
                    eths.append( eth_tmp )
                    eth_tmp = {}
        except Exception as e:
            self.error( 'unable to read network interfaces: %s' % e )
        
        # adding this network
        eths.append( { 'name': 'all', 'ip':'0.0.0.0', 'mask': '255.0.0.0' } )

        # save all eths
        self.networkInterfaces = eths

    def listEths(self):
        """
        Discovers all network interfaces of the server

        @return: list of eth
        @rtype: list
        """
        eths = []

        ifconfig = subprocess.check_output( Settings.get('Bin', 'ifconfig'),
                                            stderr=subprocess.STDOUT, shell=True )
        if sys.version_info > (3,):
            ifconfig = ifconfig.decode('utf8')
        self.trace( 'ifconfig: %s' % ifconfig )
        
        for eth in ifconfig.split('\n\n'):
            if currentLang == LANG_EN:
                ret = self.parseEth_En(ethRaw=eth)
                if ret is not None:
                    eths.append( ret )
            if currentLang == LANG_FR:
                ret = self.parseEth_Fr(ethRaw=eth)
                if ret is not None:
                    eths.append( ret )
                    
        # adding this network
        eths.append( { 'name': 'all', 'ip':'0.0.0.0', 'mask': '255.0.0.0' } )

        # save all eths
        self.networkInterfaces = eths
    
    def detectLanguage(self):
        """
        Detect the language
        """
        lang = subprocess.check_output( Settings.get('Bin', 'locale'), 
                                        stderr=subprocess.STDOUT, shell=True )
        if sys.version_info > (3,):
            lang = lang.decode('utf8')
        self.trace( 'lang: %s' % lang )
        
        lines = lang.splitlines()
        if lines[0].startswith('LANG=fr_FR'):
            return LANG_FR
        elif lines[0].startswith('LANG=en_US'):
            return LANG_EN
        else:
            return None

    def parseEth_Fr(self, ethRaw):
        """
        Parse a specific interface and returns a dict

        eth0      Link encap:Ethernet  HWaddr 08:00:27:DC:EF:FF 
                  inet adr:192.168.1.66  Bcast:192.168.1.255  Masque:255.255.255.0
                  adr inet6: fe80::a00:27ff:fedc:efff/64 Scope:Lien
                  UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
                  RX packets:60894 errors:0 dropped:0 overruns:0 frame:0
                  TX packets:16378 errors:0 dropped:0 overruns:0 carrier:0
                  collisions:0 lg file transmission:1000
                  RX bytes:19247197 (18.3 MiB)  TX bytes:12191975 (11.6 MiB)

        lo        Link encap:Boucle locale 
                  inet adr:127.0.0.1  Masque:255.0.0.0
                  adr inet6: ::1/128 Scope:Hôte
                  UP LOOPBACK RUNNING  MTU:16436  Metric:1
                  RX packets:11963 errors:0 dropped:0 overruns:0 frame:0
                  TX packets:11963 errors:0 dropped:0 overruns:0 carrier:0
                  collisions:0 lg file transmission:0
                  RX bytes:1151531 (1.0 MiB)  TX bytes:1151531 (1.0 MiB)

        @return: eth description
        @rtype: dict
        """
        eth = {}
        try:
            lines = ethRaw.splitlines()

            # extract eth name and mac address
            # 'eth0      Link encap:Ethernet  HWaddr 52:54:00:2A:D0:49  ' 
            # 'lo        Link encap:Boucle locale'
            if 'HWaddr' in lines[0]:
                ethname = lines[0].split('Link encap:Ethernet  HWaddr')
                eth['name'] = ethname[0].strip() # remove spaces
                eth['mac'] = ethname[1].strip() # remove spaces
            else:
                ethname = lines[0].split('Link encap:Boucle locale')
                eth['name'] = ethname[0].strip() # remove spaces

            # extract ips
            # => '          inet addr:204.62.14.177  Bcast:204.62.14.255  Mask:255.255.255.0'
            # or '          inet addr:127.0.0.1  Mask:255.0.0.0'
            # or '          inet adr:192.168.1.66  Bcast:192.168.1.255  Masque:255.255.255.0'
            if 'Bcast:' in lines[1]:
                ethip =  lines[1].split('inet adr:')[1].split('Bcast:')[0]
                eth['ip'] = ethip.strip() # remove spaces
                
                ethbroadcast =  lines[1].split('Bcast:')[1].split('Masque:')[0]
                eth['broadcast'] = ethbroadcast.strip() # remove spaces
            else:
                ethip =  lines[1].split('inet adr:')[1].split('Masque:')[0]
                eth['ip'] = ethip.strip() # remove spaces

            ethmask =  lines[1].split('Masque:')[1]
            eth['mask'] = ethmask.strip() # remove spaces
        except Exception as e:
            self.error( "unable to parse eth fr: %s" % e )
            return None
        return eth

    def parseEth_En(self, ethRaw):
        """
        Parse a specific interface and returns a dict

        eth1      Link encap:Ethernet  HWaddr 52:54:00:17:18:79
                  inet addr:10.9.1.132  Bcast:10.255.255.255  Mask:255.0.0.0
                  UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
                  RX packets:300155 errors:0 dropped:0 overruns:0 frame:0
                  TX packets:6 errors:0 dropped:0 overruns:0 carrier:0
                  collisions:0 txqueuelen:1000
                  RX bytes:33043119 (31.5 MiB)  TX bytes:252 (252.0 b)

        lo        Link encap:Local Loopback
                  inet addr:127.0.0.1  Mask:255.0.0.0
                  UP LOOPBACK RUNNING  MTU:16436  Metric:1
                  RX packets:2771998 errors:0 dropped:0 overruns:0 frame:0
                  TX packets:2771998 errors:0 dropped:0 overruns:0 carrier:0
                  collisions:0 txqueuelen:0
                  RX bytes:390592795 (372.4 MiB)  TX bytes:390592795 (372.4 MiB)

        @return: eth description
        @rtype: dict
        """
        eth = {}
        try:
            lines = ethRaw.splitlines()

            # extract eth name and mac address
            # 'eth0      Link encap:Ethernet  HWaddr 52:54:00:2A:D0:49  '
            # 'lo        Link encap:Local Loopback'
            # 'lo        Link encap:Boucle locale'
            if 'HWaddr' in lines[0]:
                ethname = lines[0].split('Link encap:Ethernet  HWaddr')
                eth['name'] = ethname[0].strip() # remove spaces
                eth['mac'] = ethname[1].strip() # remove spaces
            else:
                ethname = lines[0].split('Link encap:Local Loopback')
                eth['name'] = ethname[0].strip() # remove spaces

            # extract ips
            # => '          inet addr:204.62.14.177  Bcast:204.62.14.255  Mask:255.255.255.0'
            # or '          inet addr:127.0.0.1  Mask:255.0.0.0'
            # or '          inet adr:192.168.1.66  Bcast:192.168.1.255  Masque:255.255.255.0'
            if 'Bcast:' in lines[1]:
                ethip =  lines[1].split('inet addr:')[1].split('Bcast:')[0]
                eth['ip'] = ethip.strip() # remove spaces
                
                ethbroadcast =  lines[1].split('Bcast:')[1].split('Mask:')[0]
                eth['broadcast'] = ethbroadcast.strip() # remove spaces
            else:
                ethip =  lines[1].split('inet addr:')[1].split('Mask:')[0]
                eth['ip'] = ethip.strip() # remove spaces

            ethmask =  lines[1].split('Mask:')[1]
            eth['mask'] = ethmask.strip() # remove spaces
        except Exception as e:
            self.error( "unable to parse eth en" % e )
            return None
        return eth
        
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
                    env_filtered.append( {'name': var['name'], 'value': var['value'] } )
            
            testEnvironment.append( { 'project_id': prj['project_id'], 
                                      'project_name': prj['name'], 
                                      'test_environment': env_filtered } 
                                  )
           
        return testEnvironment

    def refreshTestEnvironment(self):
        """
        Refresh test environment
        And notify all connected user
        """
        for user_login, user_profile in self.usersConnected.items():
            if user_profile['profile']['administrator'] or user_profile['profile']['tester'] or \
                user_profile[cur_user]['profile']['developer'] :
                data = ( 'context-server', ( "update", self.getInformations(user=user_login) ) )
                ESI.instance().notify(body=data, toUser=user_login)
        return True
    
    def checkClientUpdate(self, currentVersion, systemOs, silenceMode=False, portable=False):
        """
        Check if an update of the client is needed

        @param currentVersion: current version of the client
        @type currentVersion: string

        @param systemOs: system os of the client
        @type systemOs: string
        
        @param silenceMode: silence mode 
        @type silenceMode: boolean
        
        @param portable:
        @type portable: boolean
        """
        self.trace('Check update client requested client Version=%s OS=%s Portable=%s' % (currentVersion, 
                                                                                          systemOs, 
                                                                                          portable) )
        available = self.CODE_NOT_FOUND
        
        # avoid exception during version check, provide default values
        if not len(currentVersion): currentVersion = '0.0.0'
        if not len(systemOs): systemOs = 'win32'  
        
        if "beta" in currentVersion:
            currentVersion = currentVersion.replace("beta", "")
        
        if "alpha" in currentVersion:
            currentVersion = currentVersion.replace("alpha", "")
            
        # new in v17, win32 is deprecated
        if systemOs == "win32": 
            systemOs = "win64"
            self.trace("Rewrite system os win32 by win64")
        # end of new
        
        if systemOs.startswith( "linux" ) : systemOs = "linux2"
        
        clientPackagePath = '%s%s/%s/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), systemOs )
        pkgs = os.listdir( clientPackagePath )
        latestPkg = (0,0,0)
        latestPkgStr = ''
        latestPkgName = ''
        try:
            # discovers the latest client
            for pkg in pkgs:
                # ignore symlink
                if os.path.islink( "%s/%s" % (clientPackagePath,pkg )): continue
                
                # Expected files, ignore other: 
                #  * ExtensiveTestingClient_11.0.0_Setup.exe
                #  * ExtensiveTestingClient_11.2.0_Portable.zip
				# ExtensiveTestingClient_16.0.0_32bit_Portable.zip
                pkg_split = pkg.split("_")
                if len(pkg_split) != 4:  continue
                else:
                    (n, v, h, t) = pkg_split
                    
                # Ignore all portable files or exe
                if portable:
                    if t.lower() != 'portable.zip':
                        continue
                else:
                    if t.lower() != 'setup.exe':
                        continue
                    
                # compare the version
                ver = v.split(".")
                if tuple(map( int, ver )) > latestPkg:
                    latestPkg = tuple(map( int, ver ))
                    latestPkgName = pkg

            self.trace( 'latest client in server: %s' % str(latestPkg) )
            # check the latest version with the version passed on argument
            if latestPkg > tuple(map(int, currentVersion.split("."))):
                available = self.CODE_OK
                latestPkgStr = ".".join( map(str,latestPkg) )
        except Exception as e:
            self.error("unable to check client update: %s" % str(e) )
            available = self.CODE_ERROR
            
        # returns the result
        self.trace('check update client returned with result %s' % available )
        return (available, latestPkgStr, latestPkgName)
        
    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="CTX - %s" % txt)

CTX = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return CTX

def initialize ():
    """
    Instance creation
    """
    global CTX
    CTX = Context()

def finalize ():
    """
    Destruction of the singleton
    """
    global CTX
    if CTX:
        CTX.stopSessionHandler()
        CTX = None