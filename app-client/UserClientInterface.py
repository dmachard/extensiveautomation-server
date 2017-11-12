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

"""
User client interface
"""

# import standard modules
import sys
import time
import base64
import zlib
try:
    import xmlrpclib
except ImportError: # support python3
    import xmlrpc.client as xmlrpclib
import hashlib
import copy
import os
import urllib
import json
from threading import Thread
import subprocess

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QDialog)
    from PyQt4.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)
except ImportError:
    from PyQt5.QtWidgets import (QDialog)
    from PyQt5.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)

from Libs import PyBlowFish, QtHelper, Logger
import Libs.NetLayerLib.ClientAgent as NetLayerLib
import Libs.NetLayerLib.Messages as Messages

import TestResults
import Settings
import ServerExplorer

import Workspace.FileModels.TestData as FileModelTestData
import Workspace.FileModels.TestSuite as FileModelTestSuite
import Workspace.FileModels.TestUnit as FileModelTestUnit
import Workspace.FileModels.TestAbstract as FileModelTestAbstract
import Workspace.FileModels.TestPlan as FileModelTestPlan

import Workspace as WWorkspace
import RestClientInterface as RCI

EXT_TESTUNIT = "tux"
EXT_TESTSUITE = "tsx"
EXT_TESTPLAN = "tpx"
EXT_TESTGLOBAL = "tgx"
EXT_TESTABSTRACT = "tax"

TESTPLAN_REPO_FROM_OTHER                = 'other'
TESTPLAN_REPO_FROM_LOCAL                = 'local'
TESTPLAN_REPO_FROM_REMOTE               = 'remote'
TESTPLAN_REPO_FROM_HDD                  = 'hdd'
TESTPLAN_REPO_FROM_LOCAL_REPO_OLD       = 'local repository'

############## NETWORK ERROR ##############
# errors on channel tcp

# - Connection refused: [Errno 10061] No connection could be made because the target machine actively refused it
# - Resolved hostname failed: [Errno 11004] getaddrinfo failed
# - Network problem server to slow to respond
# - Connection timeout

TIMEOUT_CONNECT_XMLRPC      = 10.0

############## RESPONSE CODE ##############

CODE_ERROR                  = 500
CODE_DISABLED               = 405
CODE_ALLREADY_EXISTS        = 420
CODE_NOT_FOUND              = 404
CODE_LOCKED                 = 421
CODE_ALLREADY_CONNECTED     = 416
CODE_FORBIDDEN              = 403
CODE_FAILED                 = 400
CODE_OK                     = 200

DOWNLOAD_CLIENT             = 0
DOWNLOAD_LOGS               = 1
DOWNLOAD_LOGS_LOCAL         = 2
DOWNLOAD_BACKUP             = 3

############## XML RPC  FUNCTIONS ##############
AUTHENTICATE_CLIENT         =   "authenticateClient"

GET_ADVANCED_INFO           =   "getAdvancedInformations"
CHECK_UPDATE                =   "checkUpdate"
CHECK_UPDATE_AUTO           =   "checkUpdateAuto"

SCHEDULE_TESTS              =   "scheduleTests"
SCHEDULE_TEST               =   "scheduleTest"
RESCHEDULE_TEST             =   "rescheduleTest"
REPLAY_TEST                 =   "replayTest"

CHECK_DESIGN_TEST           =   "checkDesignTest"
CHECK_SYNTAX_TEST           =   "checkSyntaxTest"
CHECK_SYNTAX_ADAPTER        =   "checkSyntaxAdapter"
CHECK_SYNTAX_ADAPTERS       =   "checkSyntaxAdapters"
CHECK_SYNTAX_LIBRARY        =   "checkSyntaxLibrary"
CHECK_SYNTAX_LIBRARIES      =   "checkSyntaxLibraries"
ADD_DEV_TIME_TEST           =   "addDevTime"

CANCEL_ALL_TASKS            =   "cancelAllTasks"
CANCEL_TASK                 =   "cancelTask"
KILL_TASK                   =   "killTask"
KILL_ALL_TASKS              =   "killAllTasks"

REFRESH_REPO                =   "refreshRepo"
GET_FILE_REPO               =   "getFileRepo"
PUT_FILE_REPO               =   "putFileRepo"
IMPORT_FILE_REPO            =   "importFileRepo"
MOVE_FILE_REPO              =   "moveFileRepo"
MOVE_FOLDER_REPO            =   "moveDirRepo"
OPEN_FILE_REPO              =   "openFileRepo"
UNLOCK_FILE_REPO            =   "unlockFileRepo"
CLEANUP_LOCK_FILES_REPO     =   "cleanupLockFilesRepo"

CREATE_SNAPSHOT_TEST        =   "createSnapshotTest"
DELETE_ALL_SNAPSHOTS_TEST   =   "deleteAllSnapshotsTest"
RESTORE_SNAPSHOT_TEST       =   "restoreSnapshotTest"
DELETE_SNAPSHOT_TEST        =   "deleteSnapshotTest"

ADD_DIR_REPO                =   "addDirRepo"
RENAME_DIR_REPO             =   "renameDirRepo"
DEL_DIR_REPO                =   "delDirRepo"
DEL_DIR_ALL_REPO            =   "delDirAllRepo"
DUPLICATE_DIR_REPO          =   "duplicateDirRepo"

RENAME_FILE_REPO            =   "renameFileRepo"
DEL_FILE_REPO               =   "delFileRepo"
DUPLICATE_FILE_REPO         =   "duplicateFileRepo"

ADD_LIBRARY_REPO            =   "addLibraryRepo"
ADD_ADAPTER_REPO            =   "addAdapterRepo"
REFRESH_HELPER              =   "refreshHelper"
SET_DEFAULT_ADP             =   "setDefaultAdapterV2"
SET_DEFAULT_LIB             =   "setDefaultLibraryV2"
SET_DEFAULT_TESTS_VERSION   =   "setDefaultVersionForTests"
SET_GENERIC_ADP             =   "setGenericAdapter"
SET_GENERIC_LIB             =   "setGenericLibrary"


LOAD_TEST_CACHE             =   "loadTestCache"
RESET_TESTS_STATS           =   "resetTestsStats"

EMPTY_REPO                  =   "emptyRepo"
REFRESH_STATS_REPO          =   "refreshStatsRepo"
DELETE_BACKUPS_REPO         =   "deleteBackupsRepo"
BACKUP_REPO                 =   "backupRepo"

ZIP_REPO_ARCHIVES           =   "zipRepoArchives"
ADD_COMMENT_ARCHIVE         =   "addCommentArchive"
LOAD_COMMENTS_ARCHIVE       =   "loadCommentsArchive"
DEL_COMMENTS_ARCHIVE        =   "delCommentsArchive"

EXPORT_TESTRESULT_VERDICT   =   "exportTestVerdict"
EXPORT_TESTRESULT_REPORT    =   "exportTestReport"
EXPORT_TESTRESULT_DESIGN    =   "exportTestDesign"

STOP_PROBE                  =   "stopProbe"
START_PROBE                 =   "startProbe"
ADD_PROBE                   =   "addProbe"
DEL_PROBE                   =   "delProbe"
REFRESH_RUNNING_PROBES      =   "refreshRunningProbes"
REFRESH_DEFAULT_PROBES      =   "refreshDefaultProbes"

STOP_AGENT                  =   "stopAgent"
START_AGENT                 =   "startAgent"
ADD_AGENT                   =   "addAgent"
DEL_AGENT                   =   "delAgent"
REFRESH_RUNNING_AGENTS      =   "refreshRunningAgents"
REFRESH_DEFAULT_AGENTS      =   "refreshDefaultAgents"

GEN_CACHE_HELP              =   "genCacheHelp"
GEN_ADAPTERS                =   "genAdapters"
GEN_LIBRARIES               =   "genLibraries"
GEN_SAMPLES                 =   "genSamples"
GEN_ALL                     =   "genAllPackages"
PREPARE_ASSISTANT           =   "prepareAssistant"
GENERATE_ADAPTER_WSDL       =   "generateAdapterFromWSDL"

REFRESH_STATS_SERVER        =   "refreshStatsServer"
REFRESH_CONTEXT_SERVER      =   "refreshContextServer"

DEL_TASKS_HISTORY           =   "delTasksHistory"
REFRESH_TASKS               =   "refreshTasks"

DOWNLOAD_TESTRESULT         =   "downloadTestResult"
DOWNLOAD_BACKUP             =   "downloadBackup"
DOWNLOAD_CLIENT             =   "downloadClient"

# GET_TEST_PREVIEW            =   "getTestPreview"
GET_IMAGE_PREVIEW           =   "getImagePreview"
DELETE_TEST_RESULT          =   "deleteTestResult"

############## USERS TYPE ##############
RIGHTS_ADMIN                =   "Administrator"
RIGHTS_USER                 =   "Tester"
RIGHTS_DEVELOPER            =   "Developer"
RIGHTS_MANAGER              =   "Leader"
RIGHTS_LEADER               =   RIGHTS_MANAGER
RIGHTS_TESTER               =   RIGHTS_USER

RIGHTS_USER_LIST            =  [ 
                                    RIGHTS_ADMIN, 
                                    RIGHTS_LEADER,
                                    RIGHTS_TESTER,
                                    RIGHTS_DEVELOPER
                                ]

############## SCHEDULATION TYPE ##############
SCHED_NOW                   =   -1      # one run 
SCHED_AT                    =   0       # run postponed
SCHED_IN                    =   1       # run postponed
SCHED_EVERY_SEC             =   2
SCHED_EVERY_MIN             =   3
SCHED_HOURLY                =   4
SCHED_DAILY                 =   5
SCHED_EVERY_X               =   6
SCHED_WEEKLY                =   7
SCHED_NOW_MORE              =   8

SCHED_QUEUE                 =   9      # run enqueued
SCHED_QUEUE_AT              =   10     # run enqueued at


SCHED_DAYS_DICT =   {
                        0           :   'monday',
                        1           :   'tuesday',
                        2           :   'wednesday',
                        3           :   'thursday',
                        4           :   'friday',
                        5           :   'saturday',
                        6           :   'sunday',
                    }

############## TASKS TYPE ##############
TASKS_RUNNING                       =   0
TASKS_WAITING                       =   1
TASKS_HISTORY                       =   2

############## REPOSITORY TYPE ##############
REPO_TESTS                          =   0
REPO_ADAPTERS                       =   1
REPO_TESTS_LOCAL                    =   2
REPO_UNDEFINED                      =   3
REPO_ARCHIVES                       =   4
REPO_LIBRARIES                      =   5

REPO_TYPES_DICT =   {
                        REPO_TESTS          :   'remote-tests',
                        REPO_ADAPTERS       :   'remote-adapters',
                        REPO_TESTS_LOCAL    :   'local-tests',
                        REPO_UNDEFINED      :   'undefined',
                        REPO_ARCHIVES       :   'archives',
                        REPO_LIBRARIES      :   'remote-libraries'
                    }

############## PROBES RESULT START ##############

PROBE_REG_OK                    =   0
PROBE_REG_FAILED                =   1
PROBE_REG_TIMEOUT               =   2
PROBE_REG_REFUSED               =   3
PROBE_REG_HOSTNAME_FAILED       =   4
PROBE_REG_CONN_REFUSED          =   5
PROBE_TYPE_UNKNOWN              =   -2

AGENT_REG_OK                    =   0
AGENT_REG_FAILED                =   1
AGENT_REG_TIMEOUT               =   2
AGENT_REG_REFUSED               =   3
AGENT_REG_HOSTNAME_FAILED       =   4
AGENT_REG_CONN_REFUSED          =   5
AGENT_TYPE_UNKNOWN              =   -2

ACTION_MERGE_PARAMS     = 7
ACTION_UPDATE_PATH      = 6
ACTION_IMPORT_OUTPUTS   = 5
ACTION_IMPORT_INPUTS    = 4
ACTION_RELOAD_PARAMS    = 3
ACTION_INSERT_AFTER     = 2
ACTION_INSERT_BELOW     = 1
ACTION_ADD              = 0

FOR_DEST_TP             = 1
FOR_DEST_TG             = 2
FOR_DEST_TS             = 3
FOR_DEST_TU             = 4
FOR_DEST_ALL            = 10


def bytes2str(val):
    """
    bytes 2 str conversion, only for python3
    """
    if isinstance(val, bytes):
        return str(val, "utf8")
    else:
        return val
        
def calling_xmlrpc(func):
    """
    Decorator for xmlrpc call
    """
    def wrapper(*args, **kwargs):
        """
        just a wrapper
        """
        funcname = func.__name__
        parent = args[0]
        try:
            parent.trace("calling xmlrpc %s" % funcname)
            func(*args, **kwargs)
            parent.trace("ending xmlrpc %s, waiting response" % funcname)
        except Exception as e:
            parent.onError( title=funcname, err=str(e) )
    return wrapper

class UserClientInterface(QObject, Logger.ClassLogger, NetLayerLib.ClientAgent):
    """
    User client interface
    """
    ResetStatistics = pyqtSignal()  
    CriticalMsg = pyqtSignal(str, str)  
    WarningMsg = pyqtSignal(str, str)  
    InformationMsg = pyqtSignal(str, str)  
    Disconnected = pyqtSignal()  
    Connected = pyqtSignal(dict)  
    Notify = pyqtSignal(tuple)  
    Interact = pyqtSignal(int, str, float, int, str) 
    Pause = pyqtSignal(int, str, str, float, int) 
    BreakPoint = pyqtSignal(int, int, float) 
    AddTestTab = pyqtSignal(TestResults.TestResult.WTestResult) 
    TestRescheduled = pyqtSignal(int) 
    TestKilled = pyqtSignal(int) 
    TestsKilled = pyqtSignal(list) # new in v12.1
    ArrowCursor = pyqtSignal() 
    BusyCursor = pyqtSignal()
    TestCancelled = pyqtSignal(int)
    RefreshRepo = pyqtSignal(int, str, bool, bool, int)
    GetFileRepo = pyqtSignal(int, str, str, str, str, int, int, int, int) 
    OpenFileRepo = pyqtSignal(int, str, str, str, str, int, list) 
    PutFileRepo = pyqtSignal(tuple)
    PutFileErrRepo = pyqtSignal(tuple)
    ImportFileRepo = pyqtSignal(tuple)
    ImportFileErrRepo = pyqtSignal(tuple)
    AddDirRepo = pyqtSignal()
    DelFileRepo = pyqtSignal()
    DelDirRepo = pyqtSignal()
    DelDirAllRepo = pyqtSignal()
    RenameDirRepo = pyqtSignal(tuple)
    MoveFileRepo = pyqtSignal()
    DuplicateDirRepo = pyqtSignal()
    RenameFileRepo = pyqtSignal(tuple)
    DuplicateFileRepo = pyqtSignal()
    OpenTestResult = pyqtSignal(tuple)
    RefreshTasksWaiting = pyqtSignal(dict)
    RefreshTasksRunning = pyqtSignal(dict)
    RefreshTasksHistory = pyqtSignal(dict)
    MoveFolderRepo = pyqtSignal()
    RefreshHelper = pyqtSignal(dict)
    AddAdapterRepo = pyqtSignal()
    AddLibraryRepo = pyqtSignal()
    CommentsArchiveDeleted = pyqtSignal(str)
    CommentsArchiveLoaded = pyqtSignal(str, list)
    CommentArchiveAdded = pyqtSignal(str, str, list, bool)
    TestresultReportLoaded = pyqtSignal(str, str)
    TestresultVerdictLoaded = pyqtSignal(str, str)
    TestresultDesignLoaded = pyqtSignal(str, str)
    RefreshDefaultAgents = pyqtSignal(str)
    RefreshRunningAgents = pyqtSignal(str)
    RefreshDefaultProbes = pyqtSignal(str)
    RefreshRunningProbes = pyqtSignal(str)
    RefreshStatsServer = pyqtSignal(str)
    RefreshContextServer = pyqtSignal(str)
    RefreshStatsRepoArchives = pyqtSignal(dict)
    RefreshStatsRepoLibraries = pyqtSignal(dict)
    RefreshStatsRepoAdapters = pyqtSignal(dict)
    RefreshStatsRepo = pyqtSignal(dict)
    GetImagePreview = pyqtSignal(str)
    # GetTestPreview = pyqtSignal(dict)
    WebCall = pyqtSignal(object)
    def __init__(self, parent = None, clientVersion=None):
        """
        Qt Class User Client Interface
        Signals:
         * Connected
         * Disconnected
         * Notify
         * RefreshRepo
         * refreshStatsRepo
         * getFileRepo
         * addDirRepo
         * testKilled
         * testCancelled

        @param parent: 
        @type parent:
        """
        QObject.__init__(self, parent)
        NetLayerLib.ClientAgent.__init__(self, typeAgent = NetLayerLib.TYPE_AGENT_USER,
                            keepAliveInterval=int(Settings.instance().readValue( key = 'Network/keepalive-interval' )), 
                            inactivityTimeout=int(Settings.instance().readValue( key = 'Network/inactivity-timeout' )),
                            timeoutTcpConnect=int(Settings.instance().readValue( key = 'Network/tcp-connect-timeout' )),
                            responseTimeout=int(Settings.instance().readValue( key = 'Network/response-timeout' )),
                            selectTimeout=float(Settings.instance().readValue( key = 'Network/select-timeout' )),
                            sslSupport=QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' )),
                            wsSupport=QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' )),
                            pickleVer=int(Settings.instance().readValue( key = 'Network/pickle-version' )),
                            tcpKeepAlive=QtHelper.str2bool(Settings.instance().readValue( key = 'Network/tcp-keepalive' )), 
                            tcpKeepIdle=int(Settings.instance().readValue( key = 'Network/tcp-keepidle' )),
                            tcpKeepCnt=int(Settings.instance().readValue( key = 'Network/tcp-keepcnt' )), 
                            tcpKeepIntvl=int(Settings.instance().readValue( key = 'Network/tcp-keepintvl' ))
                        )
        self.parent = parent
        self.password = ""
        self.login = ""
        self.channelId = None
        self.clientVersion = clientVersion
        self.appName = Settings.instance().readValue( key = 'Common/name' )
        self.address = ""
        self.addressResolved = ""
        self.portWs = 0
        
        self.addressProxyHttp = ""
        self.addressProxyHttpResolved = ""
        self.proxyActivated = False

        self.portData = Settings.instance().readValue( key = 'Server/port-data' )
        self.authenticated = False
        self.userRights = []
        self.userId = 0
        self.loaderDialog = QtHelper.MessageBoxDialog(dialogName = self.tr("Loading"))

        self.updateClientDialog = QtHelper.MessageBoxDialog(dialogName = '')
        self.updateClientDialog.Download.connect(self.updateClient)

        self.parent.DataProgress.connect(self.updateDataReadProgress)
        
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.getClientUpdateAuto)
        
    def application(self):
        """
        return main application instance
        """
        return self.parent

    def updateClient(self, pkgName):
        """
        Download the client to update it
        """
        self.updateClientDialog.done(0)
        self.downloadClientV2(packageName="%s" % pkgName) 

    def getLogin(self):
        """
        Returns login
        """
        return self.login

    def updateDataReadProgress (self, bytesRead, totalBytes):
        """
        Called to update progress bar

        @param bytesRead: 
        @type bytesRead:

        @param totalBytes: 
        @type totalBytes:
        """
        self.loaderDialog.updateDataReadProgress(bytesRead, totalBytes) 

    def getScheme(self):
        """
        Return scheme
        """
        if eval( Settings.instance().readValue( key = 'Server/api-ssl' ) ):
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def getHttpPort(self):
        """
        Return http port
        """
        httpPort = Settings.instance().readValue( key = 'Server/port-api' )
        return httpPort
    
    def getHttpAddress(self):
        """
        Return http address
        """
        addr =  Settings.instance().readValue( key = 'Server/last-addr' )
        if ":" in addr:
            return addr.split(":")[0]
        else:
            return addr
            
    def setCtx(self, address, login, password, supportProxy, addressProxyHttp, portProxyHttp):
        """
        Sets login and password given by the user
        Password is encoded to md5

        @param address: 
        @type address:

        @param port: 
        @type port:

        @param login: 
        @type login:
        
        @param password: 
        @type password:
        """
        if supportProxy:
            self.proxyActivated = True
        else:
            self.proxyActivated = False
            
        NetLayerLib.ClientAgent.unsetProxy(self)
        ServerExplorer.instance().wWebService.unsetWsProxy()

        self.address = address
        self.addressProxyHttp = addressProxyHttp
        self.portProxyHttp = portProxyHttp

        self.login = login
        self.password = hashlib.sha1( password.encode('utf8') ).hexdigest()
        # resolve server address

        # read port from settings, can be changed from preferences
        self.portWs = int( Settings.instance().readValue( key = 'Server/port-api' ) )
        self.portData = int( Settings.instance().readValue( key = 'Server/port-data' ) )
        
        resolved = NetLayerLib.ClientAgent.setServerAddress(self, ip = address, port = int(self.portData) )
        if resolved is None:
            ret = resolved
        else:
            dst_ip, dst_port = resolved
            self.addressResolved = dst_ip

            # set the agent name
            NetLayerLib.ClientAgent.setAgentName( self, self.login ) 

            scheme = "http"
            if Settings.instance().readValue( key = 'Server/api-ssl' ) == "True" :
                scheme = "https"
            
            # do not resolve ip in this case
            if self.proxyActivated and len(addressProxyHttp) and portProxyHttp:
                dst_ip = address
                
            ServerExplorer.instance().configureServer( address= dst_ip, port = self.portWs,
                                                        scheme=scheme, hostname=self.address )

            # resolve proxy if activated 
            if self.proxyActivated and len(addressProxyHttp) and portProxyHttp:
                resolvedProxyHttp = NetLayerLib.ClientAgent.setProxyAddress(self, ip = addressProxyHttp, port = int(portProxyHttp) )
                if resolvedProxyHttp is None:
                    ret = resolvedProxyHttp
                else:
                    dst_ip, dst_port = resolvedProxyHttp
                    self.addressProxyHttpResolved = dst_ip
                
                # set proxy on ws http
                ServerExplorer.instance().configureProxy(ip=self.addressProxyHttpResolved, port=portProxyHttp)
            ret = True
        return ret

    def connectChannel(self):
        """
        Connect channel
        """
        self.startConnection()

    def isAuthenticated (self):
        """
        Is authenticated ?

        @return:
        @rtype:
        """
        return self.authenticated

    def onResolveHostnameFailed(self, err):
        """
        On resolve hostname failed

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        if 'Errno 11004' in err:
            msgErr = 'Server address resolution failed'
        else:
            msgErr = err
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection") , "%s:\n%s" % (self.tr("Error occured"),msgErr) )

    def onResolveHostnameProxyFailed(self, err):
        """
        On resolve proxy hostname failed

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        if 'Errno 11004' in str(err):
            msgErr = 'Proxy address resolution failed'
        else:
            msgErr = err
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection Proxy") , "%s:\n%s" % (self.tr("Error occured"),msgErr) )
    
    def onConnectionRefused(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        if 'Errno 10061' in err:
            msgErr = 'The connection has been refused by the server'
        else:
            msgErr = err
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection") , "%s:\n%s" % (self.tr("Error occured"),msgErr) )

    def onConnectionTimeout(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection") , "%s %s.\n%s\n\n%s" % ( self.tr('Connection'), err,  self.tr("Please retry!"),
                                                                            self.tr("If the problem persists contact your administrator.") )
                            )

    def onWsHanshakeError(self, err):
        """
        Called on websocket error
        """
        self.updateTimer.stop()
        
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection") , "%s %s.\n%s\n\n%s" % ( self.tr('Connection'), err,  self.tr("Please retry!"),
                                                                            self.tr("If the problem persists contact your administrator.") )
                            )

    def onProxyConnectionRefused(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        if 'Errno 10061' in err:
            msgErr = 'Proxy: the connection has been refused by the server'
        else:
            msgErr = err
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection Proxy") , str(msgErr) )

    def onProxyConnectionError(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        ServerExplorer.instance().stopWorking()
        self.closeConnection()
        ServerExplorer.instance().enableConnect()
        WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection Proxy") , str(err) )

    def onProxyConnectionTimeout(self, err):
        """
        Called when the connection to the channel of data is refused 

        @param err: message
        @type err: string
        """
        self.updateTimer.stop()
        
        if ServerExplorer.instance() is not None:
            ServerExplorer.instance().stopWorking()
            ServerExplorer.instance().enableConnect()
            WWorkspace.WDocumentViewer.instance().updateConnectLink(connected=False)
        self.emitCriticalMsg( self.tr("Connection Proxy") , "%s %s.\n%s\n\n%s" % ( self.tr("Connection Proxy"), err, self.tr("Please retry!"),
                                                                self.tr("If the problem persists contact your administrator.") )
                             )

    def onProxyConnection(self):
        """
        On proxy connection
        """
        self.updateTimer.stop()
        
        self.trace('Proxy initialization...')
        try:
            self.sendProxyHttpRequest()
        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Connection Proxy") , str(e) )

    def onConnection(self):
        """
        On connection
        """
        try:
            websocketSupport = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' ))
            websocketSsl = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' ))
            if websocketSupport:
                self.trace('Websocket initialization...')
                wspath = Settings.instance().readValue( key = 'Server/websocket-path' )
                if websocketSsl:
                    wspath = Settings.instance().readValue( key = 'Server/websocket-secure-path' )
                self.handshakeWebSocket(resource=wspath, hostport=self.address)
        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Channel handshake") , str(e) )

    def onProxyConnectionSuccess(self):
        """
        On proxy connection with success
        """
        try:
            websocketSupport = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-websocket' ))
            websocketSsl = QtHelper.str2bool(Settings.instance().readValue( key = 'Server/data-ssl' ))
            if websocketSupport:
                self.trace('Websocket initialization through proxy...')
                wspath = Settings.instance().readValue( key = 'Server/websocket-path' )
                if websocketSsl:
                    wspath = Settings.instance().readValue( key = 'Server/websocket-secure-path' )
                self.handshakeWebSocket(resource=wspath, hostport=self.address)
        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Channel handshake through proxy") , str(e) )

    def onFirstNotify(self):
        """
        On first notify received from server
        """
        self.trace('API Authentication...')
        try:
            xml_data = { 'channel-id':  self.channelId, 'login': self.login, 'password':self.password }
            xml_data.update( self.__getCurrentVersion() )

            self.trace('[XMLRPC] xmlrpc function called')
            self.__callXmlrpc( xmlrpcFunc=AUTHENTICATE_CLIENT, xmlrpcData=xml_data )

        except Exception as e:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Connection") , str(e) )
            
    def emitCriticalMsg(self, title, err):
        """
        Emit a critical message
        """
        self.CriticalMsg.emit(title, err)  
    
    def emitWarningMsg(self, title, err):
        """
        Emit a warning message
        """
        self.WarningMsg.emit(title, err)  
    
    def emitInformationMsg(self,title, err):
        """
        Emit a infomational message
        """
        self.InformationMsg.emit(title, err)  

    def onDisconnection(self, byServer=False, inactivityServer=False):
        """
        Reimplemented from ClientDataChannel
        Emit "Disconnected" on disconnection
        """
        self.trace('on disconnection byserver=%s inactivitserver=%s...' %(byServer, inactivityServer) )
        self.updateTimer.stop()
        self.authenticated = False
                    
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/rest-support' ) ):
            if not byServer:
                RCI.instance().logout()

        if inactivityServer:
            if ServerExplorer.instance() is not None: ServerExplorer.instance().stopWorking()

            self.channelId = None
            self.userRights = []
            self.userId = 0

            self.Disconnected.emit() 
            
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageWarningTray(msg="%s\n%s" % (self.tr("Inactivity detected, connection closed"), 
                                                                            self.tr("Please to reconnect!")))
            else:  
                self.emitCriticalMsg( self.tr("Connection") , "%s\n%s" % (self.tr("Inactivity detected, connection closed"), 
                                                                            self.tr("Please to reconnect!")) )

            
        else:
            if self.isConnected():  self.trace('Disconnection...')
            self.channelId = None
            self.userRights = []
            self.userId = 0
            NetLayerLib.ClientAgent.onDisconnection(self)
            if ServerExplorer.instance() is not None: ServerExplorer.instance().stopWorking()
            
            self.Disconnected.emit() 
            
            if byServer:
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageWarningTray(msg=self.tr("Disconnected by the server.\nPlease to reconnect"))
                else: 
                    self.emitWarningMsg(title=self.tr("Connection"), err=self.tr("Disconnected by the server.\nPlease to reconnect"))
        
    def onRequest (self, client, tid, request):
        """
        Reimplemented from ClientAgent
        Emit "Notify" when NOTIFY message is received

        @param event: 
        @type event:
        """
        if request['cmd'] == Messages.RSQ_NOTIFY:
            if  request['body'][0] == 'reg':
                if self.channelId is None:
                    self.channelId = request['body'][1]['channel-id']
                    self.onFirstNotify()
                else:
                    self.channelId = request['body'][1]['channel-id']
            else:
                self.Notify.emit( request['body'] )
        elif request['cmd'] == Messages.RSQ_CMD:
            if 'cmd' in request['body']:
                if request['body']['cmd'] == Messages.CMD_INTERACT:
				
                    if 'ask' in request['body']:
					
                        # new in v12.2
                        defaultValue = ''
                        if 'default' in request['body']:
                            defaultValue = request['body']['default']
                        # end of new
                        self.Interact.emit( tid, request['body']['ask'], request['body']['timeout'], 
											int(request['body']['test-id']), defaultValue )
											
                    if 'pause' in request['body']:
                        self.Pause.emit( tid, request['body']['step-id'], request['body']['step-summary'],
                                           request['body']['timeout'], int(request['body']['test-id']) )
                    if 'breakpoint' in request['body']:
                        self.BreakPoint.emit( tid, int(request['body']['test-id']), request['body']['timeout'] )
                else:
                    NetLayerLib.ClientAgent.forbidden(self, tid=tid, body='' )
            else:
                NetLayerLib.ClientAgent.forbidden(self, tid=tid, body='' )
        else:
            self.trace('%s received ' % request['cmd'])
    
    def onResponse(self, value):
        """
        XmlRPC callback

        @param value: 
        @type value: 
        """
        self.ArrowCursor.emit()
        try:
            self.trace('[XMLRPC] Response received')
            requestName, responseCode, responseData = value
            # general server error ?
            if responseCode == CODE_ERROR: 
                self.closeConnection()
                ServerExplorer.instance().stopWorking()
                self.emitCriticalMsg( self.tr("Error") , "%s\n%s" %  (self.tr("Server error!"), 
                                        self.tr("If the problem persists contact your administrator.")) )
            else:
                if requestName == AUTHENTICATE_CLIENT:
                    self.onAuthenticate( data = responseData )
                elif requestName == GET_ADVANCED_INFO:
                    self.Connected.emit( responseData )
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'Update/enable' ) ):
                        self.updateTimer.start( int(Settings.instance().readValue( key = 'Update/retry' )) )
                elif requestName == SCHEDULE_TEST:
                    self.onScheduleTest(responseCode, responseData)
                elif requestName == SCHEDULE_TESTS:
                    self.onScheduleTests(responseCode, responseData)
                elif requestName ==  RESCHEDULE_TEST:
                    self.onRescheduleTest(responseCode, responseData)
                elif requestName == CHECK_SYNTAX_TEST:
                    self.onCheckSyntaxTest(responseCode, responseData)
                elif requestName == CHECK_DESIGN_TEST:
                    self.onCheckDesignTest(responseCode, responseData)
                elif requestName == REPLAY_TEST:    
                    self.onReplayTest(responseCode, responseData)
                elif requestName == CHECK_UPDATE:   
                    self.onCheckUpdate(responseCode, responseData)
                elif requestName == CHECK_UPDATE_AUTO:   
                    self.onCheckUpdateAuto(responseCode, responseData)
                elif requestName ==  KILL_TASK:
                    self.onKillTask(responseCode, responseData)
                elif requestName ==  KILL_ALL_TASKS:
                    self.onKillAllTasks(responseCode, responseData)
                elif requestName ==  CANCEL_TASK:
                    self.onCancelTask(responseCode, responseData)
                elif requestName ==  CANCEL_ALL_TASKS:
                    self.onCancelAllTasks(responseCode, responseData)
                elif requestName ==  REFRESH_REPO:
                    self.onRefreshRepo(responseCode, responseData)
                elif requestName ==  GET_FILE_REPO:
                    self.onGetFileRepo(responseCode, responseData)
                elif requestName ==  OPEN_FILE_REPO:
                    self.onOpenFileRepo(responseCode, responseData)
                elif requestName ==  PUT_FILE_REPO:
                    self.onPutFileRepo(responseCode, responseData)
                elif requestName ==  UNLOCK_FILE_REPO:
                    self.onUnlockFileRepo(responseCode, responseData)
                elif requestName ==  CLEANUP_LOCK_FILES_REPO:
                    self.onCleanupLockFilesRepo(responseCode, responseData)
                elif requestName ==  IMPORT_FILE_REPO:
                    self.onImportFileRepo(responseCode, responseData)
                elif requestName ==  ADD_DIR_REPO:
                    self.onAddDirRepo(responseCode, responseData)
                elif requestName ==  DEL_DIR_REPO:
                    self.onDelDirRepo(responseCode, responseData)
                elif requestName ==  DEL_DIR_ALL_REPO:
                    self.onDelDirAllRepo(responseCode, responseData)
                elif requestName ==  DEL_FILE_REPO:
                    self.onDelFileRepo(responseCode, responseData)
                elif requestName ==  RENAME_DIR_REPO:
                    self.onRenameDirRepo(responseCode, responseData)
                elif requestName ==  DUPLICATE_DIR_REPO:
                    self.onDuplicateDirRepo(responseCode, responseData)
                elif requestName ==  RENAME_FILE_REPO:
                    self.onRenameFileRepo(responseCode, responseData)
                elif requestName ==  CREATE_SNAPSHOT_TEST:
                    self.onCreateSnapshotTest(responseCode, responseData)
                elif requestName ==  DELETE_SNAPSHOT_TEST:
                    self.onDeleteSnapshotTest(responseCode, responseData) 
                elif requestName ==  RESTORE_SNAPSHOT_TEST:
                    self.onRestoreSnapshotTest(responseCode, responseData) 
                elif requestName ==  DELETE_ALL_SNAPSHOTS_TEST:
                    self.onDeleteAllSnapshotsTest(responseCode, responseData) 
                elif requestName ==  DUPLICATE_FILE_REPO:
                    self.onDuplicateFileRepo(responseCode, responseData)
                elif requestName ==  RESET_TESTS_STATS:
                    self.onResetTestsStats(responseCode, responseData)
                elif requestName ==  EMPTY_REPO:
                    self.onEmptyRepo(responseCode, responseData)
                elif requestName ==  ZIP_REPO_ARCHIVES:
                    self.onZipRepoArchives(responseCode, responseData)
                elif requestName ==  REFRESH_STATS_REPO:
                    self.onRefreshStatsRepo(responseCode, responseData)
                elif requestName ==  REFRESH_CONTEXT_SERVER:
                    self.onRefreshContextServer(responseCode, responseData)
                elif requestName ==  REFRESH_STATS_SERVER:
                    self.onRefreshStatsServer(responseCode, responseData)
                elif requestName ==  DEL_PROBE:
                    self.onDelProbe(responseCode,responseData)
                elif requestName ==  ADD_PROBE:
                    self.onAddProbe(responseCode, responseData)
                elif requestName ==  STOP_PROBE:
                    self.onStopProbe(responseCode, responseData)
                elif requestName ==  START_PROBE:
                    self.onStartProbe(responseCode, responseData)
                elif requestName ==  DEL_AGENT:
                    self.onDelAgent(responseCode,responseData)
                elif requestName ==  ADD_AGENT:
                    self.onAddAgent(responseCode, responseData)
                elif requestName ==  STOP_AGENT:
                    self.onStopAgent(responseCode, responseData)
                elif requestName ==  START_AGENT:
                    self.onStartAgent(responseCode, responseData)
                elif requestName ==  GEN_CACHE_HELP:
                    self.onGenCacheHelp(responseCode, responseData)
                elif requestName ==  DEL_TASKS_HISTORY:
                    self.onDelTasksHistory(responseCode, responseData)
                elif requestName ==  REFRESH_RUNNING_PROBES:
                    self.onRefreshRunningProbes(responseCode, responseData)
                elif requestName ==  REFRESH_DEFAULT_PROBES:
                    self.onRefreshDefaultProbes(responseCode, responseData)
                elif requestName ==  REFRESH_RUNNING_AGENTS:
                    self.onRefreshRunningAgents(responseCode, responseData)
                elif requestName ==  REFRESH_DEFAULT_AGENTS:
                    self.onRefreshDefaultAgents(responseCode, responseData)
                elif requestName ==  EXPORT_TESTRESULT_VERDICT:
                    self.onExportTestResultVerdict(responseCode, responseData)
                elif requestName ==  EXPORT_TESTRESULT_REPORT:
                    self.onExportTestResultReport(responseCode, responseData)
                elif requestName ==  EXPORT_TESTRESULT_DESIGN:
                    self.onExportTestResultDesign(responseCode, responseData)
                elif requestName ==  ADD_DEV_TIME_TEST:
                    self.onAddDevTimeTest(responseCode, responseData)
                elif requestName ==  ADD_COMMENT_ARCHIVE:
                    self.onAddCommentArchive(responseCode, responseData)
                elif requestName ==  LOAD_COMMENTS_ARCHIVE:
                    self.onLoadCommentsArchive(responseCode, responseData)
                elif requestName ==  DEL_COMMENTS_ARCHIVE:
                    self.onDelCommentsArchive(responseCode, responseData)
                elif requestName ==  BACKUP_REPO:
                    self.onBackupRepo(responseCode, responseData)
                elif requestName ==  DELETE_BACKUPS_REPO:
                    self.onDeleteBackupsRepo(responseCode, responseData)
                elif requestName ==  ADD_LIBRARY_REPO:
                    self.onAddLibraryRepo(responseCode, responseData)
                elif requestName ==  ADD_ADAPTER_REPO:
                    self.onAddAdapterRepo(responseCode, responseData)
                elif requestName ==  REFRESH_HELPER:
                    self.onRefreshHelper(responseCode, responseData)
                elif requestName == CHECK_SYNTAX_ADAPTER or requestName == CHECK_SYNTAX_LIBRARY:
                    self.onCheckSyntax(responseCode, responseData)
                elif requestName == CHECK_SYNTAX_ADAPTERS or requestName == CHECK_SYNTAX_LIBRARIES:
                    self.onCheckSyntaxes(responseCode, responseData)
                elif requestName ==  MOVE_FILE_REPO:
                    self.onMoveFileRepo(responseCode, responseData)
                elif requestName ==  MOVE_FOLDER_REPO:
                    self.onMoveFolderRepo(responseCode, responseData)
                elif requestName ==  REFRESH_TASKS:
                    self.onRefreshTasks(responseCode, responseData)
                elif requestName ==  LOAD_TEST_CACHE:
                    self.onLoadTestCache(responseCode, responseData)
                elif requestName ==  SET_DEFAULT_ADP:
                    self.onSetDefaultAdapter(responseCode, responseData)
                elif requestName ==  SET_DEFAULT_LIB:
                    self.onSetDefaultLibrary(responseCode, responseData)
                elif requestName ==  SET_GENERIC_ADP:
                    self.onSetGenericAdapter(responseCode, responseData)
                elif requestName ==  SET_GENERIC_LIB:
                    self.onSetGenericLibrary(responseCode, responseData)
                elif requestName ==  GEN_ADAPTERS:
                    self.onGenerateAdapters(responseCode, responseData)
                elif requestName ==  GEN_LIBRARIES:
                    self.onGenerateLibraries(responseCode, responseData)
                elif requestName ==  GEN_SAMPLES:
                    self.onGenerateSamples(responseCode, responseData)
                elif requestName ==  GEN_ALL:
                    self.onGenerateAll(responseCode, responseData)
                elif requestName ==  DOWNLOAD_TESTRESULT:
                    self.onDownloadTestResult(responseCode, responseData)
                elif requestName ==  DOWNLOAD_BACKUP:
                    self.onDownloadBackup(responseCode, responseData) 
                elif requestName ==  PREPARE_ASSISTANT:
                    self.onPrepareAssistant(responseCode, responseData) 
                elif requestName ==  GENERATE_ADAPTER_WSDL:
                    self.onAdapterWsdl(responseCode, responseData) 
                elif requestName ==  DOWNLOAD_CLIENT:
                    self.onDownloadClient(responseCode, responseData) 
                elif requestName ==  SET_DEFAULT_TESTS_VERSION:
                    self.onSetDefaultTestsVersion(responseCode, responseData) 
                # elif requestName ==  GET_TEST_PREVIEW:
                    # self.onGetTestPreview(responseCode, responseData) 
                elif requestName ==  GET_IMAGE_PREVIEW:
                    self.onGetImagePreview(responseCode, responseData) 
                elif requestName ==  DELETE_TEST_RESULT:
                    self.onDeleteTestResult(responseCode, responseData) 
                else:
                    raise Exception("Request name %s unknown" % requestName)
        except Exception as e:
            self.error( str(e) )
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Error"),  str(e) )
            
    def onDeleteTestResult(self, responseCode, responseData):
        """
        On delete test result

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK: 
            self.refreshRepo(repo=REPO_ARCHIVES, partialRefresh=True, project=responseData['projectid'] )
        else:
            raise Exception("On delete test result: responseCode %s unknown" % responseCode)
            
    # def onGetTestPreview(self, responseCode, responseData):
        # """
        # On set default tests

        # @param responseCode: 
        # @type responseCode:

        # @param responseData: 
        # @type responseData:
        # """
        # if responseCode == CODE_OK: 
            # self.GetTestPreview.emit( responseData )
        # elif responseCode == CODE_FORBIDDEN:
            # self.emitCriticalMsg( self.tr("Authorization on get test preview") , 
                                    # self.tr("You are not authorized to do that!") )
        # elif responseCode == CODE_NOT_FOUND:
            # self.GetTestPreview.emit( {} )
        # else:
            # raise Exception("On get test preview: responseCode %s unknown" % responseCode)
            
    def onGetImagePreview(self, responseCode, responseData):
        """
        On set default tests

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """    
        if responseCode == CODE_OK: 
            subRspCode, pathFile, nameFile, extFile, dataFile, project, is_locked = responseData['ret']

            if subRspCode == CODE_OK:
                # decode data file
                self.GetImagePreview.emit( dataFile )

            elif subRspCode ==  CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Get image preview") , self.tr("Image not found!") )
            elif subRspCode ==  CODE_ERROR:
                self.emitCriticalMsg( self.tr("Get image preview") , "%s\n%s" % (self.tr("Unable to get image preview!"),
                                        self.tr("If the problem persists contact your administrator.")) )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization on get image preview") , 
                                    self.tr("You are not authorized to do that!") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
        
    def onSetDefaultTestsVersion(self, responseCode, responseData):
        """
        On set default tests

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """       
        if responseCode == CODE_OK: 
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageTray(msg="All tests are updated!")
            else:
                self.emitInformationMsg( title=self.tr("Set default version"), err= self.tr("All tests are updated!" ) )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
        
    def onDownloadBackup(self, responseCode, responseData):
        """
        On download backup
        

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """       
        if responseCode == CODE_OK: 
            subRspCode, pathFile, nameFile, extFile, dataFile, project = responseData['ret']

            if subRspCode == CODE_OK:
                # decode data file
                content = base64.b64decode(dataFile)
                fileName = responseData['to-file']

                # fix in v12.1 to support special character on destination file
                if sys.version_info > (3,): # python 3 support, return xmlrpc binary type
                    fileName = base64.b64decode(fileName.data)
                    fileName = fileName.decode("utf8")
                else:
                    fileName = base64.b64decode(fileName)
                    fileName = fileName.decode("utf8")
                # end of fix
                    
                # writing file
                f = open( fileName, 'wb')
                f.write( content )
                f.close()
                
                # remove unneeded data
                del content
                del dataFile
                
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Download terminated!")
                else:
                    self.emitInformationMsg( title=self.tr("Download Backup"), err= self.tr("Download terminated!" ) )
                                       
            elif subRspCode ==  CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Download Backup") , self.tr("Backup not found!") )
            elif subRspCode ==  CODE_ERROR:
                self.emitCriticalMsg( self.tr("Download Backup") , "%s\n%s" % (self.tr("Unable to open backup!"),
                                        self.tr("If the problem persists contact your administrator.")) )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization on download backup") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
        
    def onDownloadClient(self, responseCode, responseData):
        """
        On download client
        

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """       
        if responseCode == CODE_OK: 
            subRspCode, dataFile = responseData['ret']

            if subRspCode == CODE_OK:
                # decode data file
                content = base64.b64decode(dataFile)
                fileName = "%s//Update//%s" % (QtHelper.dirExec(), responseData['package-name'] )
                 
                # writing file
                f = open( fileName, 'wb')
                f.write( content )
                f.close()
                
                # remove unneeded data
                del content
                del dataFile
                
                settingsBackup = "%s//Update//backup_settings.ini" % QtHelper.dirExec()
                #remove client settings
                backupFile = QFile( settingsBackup )
                backupFile.remove()

                #copy current settings
                currentSettingsFile = QFile("%s//Files//settings.ini" % QtHelper.dirExec() )
                ret = currentSettingsFile.copy(settingsBackup)
                if not ret:  self.error( 'update: unable to copy settings files' )

                #inform user
                self.emitInformationMsg( 
                                            title=self.tr("Download"), 
                                            err= self.tr("Download finished\nGo in the Start Menu /%s/Update/ and  execute the package." % self.appName ) 
                                       )
                                       
                # open the update folder, new in v16
                if sys.platform == "win32":
                    updatePath =  '"%s\\Update\\"' % QtHelper.dirExec()
                    subprocess.call ('explorer.exe %s' % updatePath, shell=True)
                # end of new
                
                self.parent.close()
                


            elif subRspCode ==  CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Download Client") , self.tr("Client not found!") )
            elif subRspCode ==  CODE_ERROR:
                self.emitCriticalMsg( self.tr("Download Client") , "%s\n%s" % (self.tr("Unable to open client!"),
                                        self.tr("If the problem persists contact your administrator.")) )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization on download client") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
        
    def onDownloadTestResult(self, responseCode, responseData):
        """
        On download test result
        

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """       
        if responseCode == CODE_OK: 
            subRspCode, pathFile, nameFile, extFile, dataFile, project, is_locked = responseData['ret']

            if subRspCode == CODE_OK:
                # decode data file
                content = base64.b64decode(dataFile)

                # save or open ?
                # the path of the destination file depend of the mode save/open
                saveFile = responseData['and-save']
                if saveFile: 
                    fileName = responseData['to-file']
                    # fix in v12.1 to support special character on destination file
                    if sys.version_info > (3,): # python 3 support, return xmlrpc binary type
                        fileName = base64.b64decode(fileName.data)
                        fileName = fileName.decode("utf8")
                    else:
                        fileName = base64.b64decode(fileName)
                        fileName = fileName.decode("utf8")
                    # end of fix
                else:
                    fileName = "%s//ResultLogs//%s.%s" % (QtHelper.dirExec(), nameFile, extFile)

                # writing file
                f = open( fileName, 'wb')
                f.write( content )
                f.close()
                
                # remove unneeded data
                del content
                del dataFile
                
                # emit qt signal only to open test result
                if not saveFile: 
                    self.OpenTestResult.emit( (fileName, nameFile) )
                else:
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                        self.application().showMessageTray(msg="Download terminated!")
                    else:                    
                        self.emitInformationMsg( title=self.tr("Download Test Result"), err= self.tr("Download terminated!" ) )
                       
                
            elif subRspCode ==  CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Download Test Result") , self.tr("Test Result not found!") )
            elif subRspCode ==  CODE_ERROR:
                self.emitCriticalMsg( self.tr("Download Test Result") , "%s\n%s" % (self.tr("Unable to open test result!"),
                                        self.tr("If the problem persists contact your administrator.")) )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization on download test result") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
    
    def onCreateSnapshotTest(self, responseCode, responseData):
        """
        On create snapshot
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.refreshRepo(repo=REPO_TESTS, showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitWarningMsg( self.tr("Create snapshot") , self.tr("Test not found") )
            else:
                self.emitCriticalMsg( self.tr("Create snapshot") , self.tr("Unable to create snapshot") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Create snapshot: responseCode %s unknown" % responseCode)
        
    def onRestoreSnapshotTest(self, responseCode, responseData):
        """
        On restore snapshot
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.refreshRepo(repo=REPO_TESTS, showPopup=False, project=responseData['projectid'])
                self.emitInformationMsg( self.tr("Restore snapshot") , self.tr("Snapshot restored") )
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Restore snapshot") , self.tr("Snapshot not found") )
            else:
                self.emitCriticalMsg( self.tr("Restore snapshot") , self.tr("Unable to restore snapshot") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Restore snapshot: responseCode %s unknown" % responseCode)
        
    def onDeleteSnapshotTest(self, responseCode, responseData):
        """
        On delete snapshot
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.refreshRepo(repo=REPO_TESTS, showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Delete snapshot") , self.tr("Snapshot not found") )
            else:
                self.emitCriticalMsg( self.tr("Delete snapshot") , self.tr("Unable to delete snapshot") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Delete snapshot: responseCode %s unknown" % responseCode)
        
    def onDeleteAllSnapshotsTest(self, responseCode, responseData):
        """
        On delete snapshot
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.refreshRepo(repo=REPO_TESTS, showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Delete all snapshots") , self.tr("Test not found") )
            else:
                self.emitCriticalMsg( self.tr("Delete all snapshots") , self.tr("Unable to delete all snapshots") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Delete all snapshots: responseCode %s unknown" % responseCode)
        
    def onSetDefaultAdapter(self, responseCode, responseData):
        """
        On set default adapter
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.emitInformationMsg( self.tr("Set the default package of adapters") ,
                                                    self.tr("Package adapters configured successfully as default!") )
                self.refreshContextServer()
            else:
                self.emitCriticalMsg( self.tr("Set the default package of adapters") , self.tr("Unable to set the package of adapters as default!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Set the default package of adapters"), self.tr("Unable to set the default package of adapters.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
        
    def onSetGenericAdapter(self, responseCode, responseData):
        """
        On set generic adapter
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.emitInformationMsg( self.tr("Set the generic package of adapters") ,
                                                    self.tr("Package adapters configured successfully as generic!") )
                self.refreshContextServer()
            else:
                self.emitCriticalMsg( self.tr("Set the generic package of adapters") , 
                    self.tr("Unable to set the package of adapters as generic!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Set the generic package of adapters"),
                self.tr("Unable to set the generic package of adapters.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
        
    def onSetGenericLibrary(self, responseCode, responseData):
        """
        On set generic library
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.emitInformationMsg( self.tr("Set the generic library of adapters") ,
                                                    self.tr("Package libraries configured successfully as generic!") )
                self.refreshContextServer()
            else:
                self.emitCriticalMsg( self.tr("Set the generic package of libraries") ,
                    self.tr("Unable to set the package of libraries as generic!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Set the generic package of libraries"), 
                self.tr("Unable to set the generic package of libraries.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
            
    def onAdapterWsdl(self, responseCode, responseData):
        """
        On adapter wsdl
        """
        if responseCode == CODE_OK:
            if responseData['result']:
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Adapter generated successfully!")
                else:
                    self.emitInformationMsg( self.tr("Adapter generator") , 
                                            self.tr("Adapter generated successfully!") )
            else:
                self.emitCriticalMsg( self.tr("Adapter generator"), self.tr("Unable to generate adapter from wsdl file") )
        else:
            raise Exception("Adapter WSDL - responseCode %s unknown" % responseCode)
            
    def onPrepareAssistant(self, responseCode, responseData):
        """
        On prepare assistant
        """
        if responseCode == CODE_OK:
            if responseData['result']:
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Assistant successfully prepared!")
                else:
                    self.emitInformationMsg( self.tr("Prepare assistant") , 
                                            self.tr("Assistant successfully prepared!") )
                self.reloadHelper()
            else:
                self.emitCriticalMsg( self.tr("Prepare assistant"), 
                                            self.tr("Unable to prepare assistant.\n%s." %responseData['details']) )
        else:
            raise Exception("Prepare assistant - responseCode %s unknown" % responseCode)
            
    def onGenerateAll(self, responseCode, responseData):
        """
        On generate all
        """
        if responseCode == CODE_OK:
            if responseData:
                self.emitInformationMsg( self.tr("Generate all") , self.tr("Generation all done!") )
            else:
                self.emitCriticalMsg( self.tr("Generate all"), self.tr("Unable to generate all packages!.") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Generate all"), self.tr("Unable to generate all packages.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onGenerateSamples(self, responseCode, responseData):
        """
        On generate samples
        """
        if responseCode == CODE_OK:
            if responseData:
                self.emitInformationMsg( self.tr("Generate samples") , self.tr("Samples generation done!") )
            else:
                self.emitCriticalMsg( self.tr("Generate samples"), self.tr("Unable to generate samples!.") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Generate samples"), self.tr("Unable to generate samples.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onGenerateAdapters(self, responseCode, responseData):
        """
        On generate adapters
        """
        if responseCode == CODE_OK:
            if responseData:
                self.emitInformationMsg( self.tr("Generate all adapters") , self.tr("Adapters generation done!") )
            else:
                self.emitCriticalMsg( self.tr("Generate adapters"), self.tr("Unable to generate all adapters!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Generate adapters"), self.tr("Error to generate all adapters.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onGenerateLibraries(self, responseCode, responseData):
        """
        On generate libraries
        """
        if responseCode == CODE_OK:
            if responseData:
                self.emitInformationMsg( self.tr("Generate all libraries") , self.tr("Libraries generation done!") )
            else:
                self.emitCriticalMsg( self.tr("Generate libraries"), self.tr("Unable to generate all libraries!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Generate libraries"), self.tr("Error to generate all libraries.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onSetDefaultLibrary(self, responseCode, responseData):
        """
        On set default library
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.emitInformationMsg( self.tr("Set the default package of libraries") , self.tr("Package libraries configured succesfully as default!") )
                self.refreshContextServer()
            else:
                self.emitCriticalMsg( self.tr("Set the default package of libraries") , self.tr("Error to set the package of libraries as default!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Set the default package of libraries"), self.tr("Error to set the default package of libraries.\nIf the problem persists contact your administrator.") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onAuthenticate (self, data):
        """
        Called on authenticate

        @param data: 
        @type data: 
        """
        self.trace('entering in function')
        updateClient = False

        responseCode, userRights, userId, updateClient = data

        if responseCode == CODE_ERROR:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Server Error"), "%s\n\n%s\n%s" %  ( self.tr("Server Error!"), 
                                                                                self.tr("Please to retry after."),
                                                                                self.tr("If the problem persists contact your administrator.") ) )
            
        elif responseCode == CODE_NOT_FOUND:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( self.tr("Authentication"), "%s\n\n%s\n%s" %  ( self.tr("Authentication failed!"), 
                                                                                self.tr("Please to retry after, this user is unknown."),
                                                                                self.tr("If the problem persists contact your administrator.") ) )
        elif responseCode == CODE_DISABLED:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitWarningMsg(self.tr("Authentication") , "%s\n\n%s" % (self.tr("Authentication failed!"),self.tr("This user is disabled!")) )
        elif responseCode == CODE_ALLREADY_CONNECTED:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitWarningMsg( self.tr("Authentication") , "%s\n\n%s\n%s\n%s" % (self.tr("Authentication failed!"), self.tr("This user is already connected, one instance is allowed."),
                                                                                self.tr("Please to disconnect the other connection."), self.tr("If the problem persists contact your administrator.") ) )
        elif responseCode == CODE_FORBIDDEN:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitWarningMsg( self.tr("Authentication") , "%s\n\n%s\n%s" % (self.tr("Authentication failed!"), self.tr("This password is incorrect, please to retry after with the good one."), 
                                                                                self.tr("If the problem persists contact your administrator.") ) )
        elif responseCode == CODE_FAILED:
            self.closeConnection()
            ServerExplorer.instance().stopWorking()
            self.emitWarningMsg( self.tr("Authentication") , "%s\n\n%s" % (self.tr("Authentication failed!"), self.tr("Your rights are not high enough!") ) )
        elif responseCode == CODE_OK:
            if not isinstance(userId, int):
                raise Exception( "Bad User ID received: %s type=%s" % (userId, type(userId)) )
            
            if updateClient:
                
                # format of the updateClient variable: ['2.1.0', 'XXX_2.1.0_Setup.exe']
                
                # new in v10.1
                majorVersion = False
                typeVersion = "minor"
                
                # convert current version to tuple
                currentMajor, currentMinor, currentFix =  self.clientVersion.split(".")
                currentVersion = (int(currentMajor), int(currentMinor), int(currentFix)) 
                # convert new version to tuple
                newMajor, newMinor, newFix =  updateClient[0].split(".")
                newVersion = (int(newMajor), int(newMinor), int(newFix))
                # and compare it
                if int(newMajor) >  int(currentMajor):
                    majorVersion = True
                    typeVersion = "major"
                # end of new
                
                msg_ = "%s" % self.tr("A newer %s version of this client is available." % typeVersion)
                if majorVersion:
                    msg_ += "\nYou must click on download button and install the update."
                else:
                    msg_ += "\nYou may click on download button and install the update."
                msg_ += "\n\nVersion %s" % updateClient[0]
                self.updateClientDialog.setDownload( title = self.tr("Update available"), txt = msg_, 
                                                    url = updateClient[1], cancelButton=not majorVersion )
                if self.updateClientDialog.exec_() != QDialog.Accepted:
                    self.authenticated = True
                    self.userRights = userRights # list of rights
                    self.userId = userId
                    
                    if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/rest-support' ) ):
                        RCI.instance().login(  login=self.login, password=self.password  )
                    else:
                        self.trace('[XMLRPC] Retrieve server informations...')
                        self.__callXmlrpc( xmlrpcFunc=GET_ADVANCED_INFO, xmlrpcData={} )
            else:
                self.authenticated = True
                self.userRights = userRights # list of rights
                self.userId = userId
                    
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/rest-support' ) ):
                    RCI.instance().login(  login=self.login, password=self.password  )
                else:
                    self.trace('[XMLRPC] Retrieve server informations...')
                    self.__callXmlrpc( xmlrpcFunc=GET_ADVANCED_INFO, xmlrpcData={} )
        else:
            raise Exception( "Authentication: response code %s not supported" % str(responseCode))

    def onRestAuthenticated(self):
        """
        Load advanced informations
        After rest authentication
        """
        self.trace('[XMLRPC] Retrieve server informations...')
        # ServerExplorer.instance().wWebService.startWorking()
        self.__callXmlrpc( xmlrpcFunc=GET_ADVANCED_INFO, xmlrpcData={} )

    def onScheduleTests(self, responseCode, responseData):
        """
        Called on schedule test, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Grouped execution error") ,  "Unable to schedule tests run" )
        else:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageTray(msg="Group of test(s) enqueued to run.")
            else:
                self.emitInformationMsg( self.tr("Tests Execution") , self.tr("Group of test(s) enqueued to run.") )            

    def onScheduleTest(self, responseCode, responseData):
        """
        Called on schedule test, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( self.tr("Prepare Error") , "%s: %s %s %s" % ( self.tr("Preparation"), self.tr("Test"), responseData, self.tr("not found.") ) )
        elif responseCode == CODE_FORBIDDEN:
            taskId, testId, testName, background, recursive, postponed, successive = responseData
            self.emitCriticalMsg( self.tr("Execute error") ,  "Unable to execute the test: %s" % taskId )
        else:
            taskId, testId, testName, background, recursive, postponed, successive = responseData
            self.trace(responseData)
            if isinstance(taskId, int):
                if recursive or postponed or background or successive:
                    TestResults.instance().delWidgetTest( testId = testId )
                    if successive:  
                        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                            self.application().showMessageTray(msg="Your test is running several time in background.")
                        else:
                            self.emitInformationMsg( self.tr("Test Execution") , self.tr("Your test is running several time in background.") )
                    else:
                        if recursive and background:
                            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                                self.application().showMessageTray(msg="Recursive test execution scheduled!")
                            else:
                                self.emitInformationMsg( self.tr("Test Execution") , self.tr('Recursive test execution scheduled!') )
                        elif postponed and background:
                            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                                self.application().showMessageTray(msg="Test execution postponed!")
                            else:
                                self.emitInformationMsg( self.tr("Test Execution") , self.tr('Test execution postponed!') )
                        elif background:  
                            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                                self.application().showMessageTray(msg="Your test is running in background.")
                            else:
                                self.emitInformationMsg( self.tr("Test Execution") , self.tr("Your test is running in background.") )
                        else:
                            self.error( 'unknown run' )
                else:
                    wTest = TestResults.instance().getWidgetTest( testId = testId )
                    wTest.name = '[%s] %s' % (taskId, testName)
                    wTest.TID = taskId
                    if wTest is not None:
                        self.AddTestTab.emit( wTest )
            elif taskId.startswith('Unable to'):
                msg = self.tr("An error exists in this test. Fix-it and retry!")
                msg += "\n%s" % taskId
                self.emitCriticalMsg( self.tr("Test Execution") , msg )

    def onRescheduleTest(self, responseCode, responseData):
        """
        Called on reschedule test, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageWarningTray(msg="Test(s) rescheduled!")
            else:
                self.emitInformationMsg( self.tr("Re-schedule test execution") , self.tr("Test execution rescheduled!") )
            self.TestRescheduled.emit(responseData)
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( self.tr("Re-schedule test execution") , self.tr("This test does not exist!") )
        else:
            raise Exception("responseCode %s unknown" % responseData)

    def onCheckDesignTest(self, responseCode, responseData):
        """
        Called on check design on test, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Test Design", "Unable to prepare the design:\nTest %s not found!" % responseData )
        else:
            self.onExportTestResultDesign(responseCode, responseData['result'])

    def onCheckSyntaxTest(self, responseCode, responseData):
        """
        Called on check syntax on test, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Test Design", "Unable to check the syntax:\nTest %s not found!" % responseData )
        else:
            statusSyntax, errorSyntax = responseData
            if statusSyntax:
                self.emitInformationMsg( self.tr("Check syntax") , "%s\n%s" % ( self.tr("Well done!"), self.tr("No syntax error detected in your test.") ) )
            else:
                msg = self.tr("An error exists on this test.")
                msg += "\n%s" % errorSyntax
                self.emitWarningMsg( self.tr("Check syntax") , msg )

    def onReplayTest(self, responseCode, responseData):
        """
        Called on replay test, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseData == False:
            self.emitCriticalMsg( self.tr("Replay") , self.tr("This test does not exist") )

    def onCheckUpdateAuto(self, responseCode, responseData):
        """
        Called on check client update auto, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseData:
            self.updateTimer.stop()
            msg_ = "%s: %s" % ( "Update available", responseData[0] )
            self.updateClientDialog.setDownload( title = self.tr("Update available"), txt = msg_, url = responseData[1] )
            if self.updateClientDialog.exec_() != QDialog.Accepted:
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Update/enable' ) ):
                    self.updateTimer.start( int(Settings.instance().readValue( key = 'Update/retry' )) )
            
    def onCheckUpdate(self, responseCode, responseData):
        """
        Called on check client update, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseData == False:
            self.emitInformationMsg( self.tr("Check for update") , self.tr("No update available") )
        else:
            msg_ = "%s: %s" % ( "Update available", responseData[0] )
            self.updateClientDialog.setDownload( title = self.tr("Update available"), txt = msg_, url = responseData[1] )
            self.updateClientDialog.exec_()

    def onKillTask(self, responseCode, responseData):
        """
        Called on kill task, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageWarningTray(msg="Test(s) killed!")
            else:
                self.emitWarningMsg( self.tr("Kill test") , self.tr("The test is stopped!") )
            if isinstance(responseData, list): # new in v12.1
                self.TestsKilled.emit( responseData )
            else: # end of new
                self.TestKilled.emit( responseData )
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( self.tr("Kill test") , self.tr("This test does not exist!") )
        else:
            raise Exception("responseCode %s unknown" % responseData)

    def onKillAllTasks(self, responseCode, responseData):
        """
        Called on kill all tasks, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.emitWarningMsg( self.tr("Kill all tests") , self.tr("All tests are killed!") )
        else:
            raise Exception("responseCode %s unknown" % responseData)

    def onCancelTask(self, responseCode, responseData):
        """
        Called on cancel task, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageWarningTray(msg="Test(s) cancelled!")
            else:
                self.emitWarningMsg( self.tr("Cancel test") , "The test is cancelled!" )
            self.TestCancelled.emit(responseData)
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( self.tr("Cancel test") , self.tr("This test does not exist!") )
        else:
            raise Exception("responseCode %s unknown" % responseData)

    def onCancelAllTasks(self, responseCode, responseData):
        """
        Called on cancel all tasks, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.emitWarningMsg( self.tr("Cancel all tests") , self.tr("All tests are cancelled!") )
        else:
            raise Exception("responseCode %s unknown" % responseData)

    def onRefreshRepo(self, responseCode, responseData):
        """
        Called on refresh respository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshRepo.emit(responseData['repo-dst'], responseData['ret'], responseData['saveas-only'], responseData['for-runs'], responseData['projectid'])
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Refresh repository") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onOpenFileRepo(self, responseCode, responseData):
        """
        Called on open file from repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK: 
            if responseData['repo-dst'] == REPO_TESTS:
                subRspCode, pathFile, nameFile, extFile, dataFile, project, isLocked = responseData['ret']
            elif responseData['repo-dst'] == REPO_ADAPTERS or responseData['repo-dst'] == REPO_LIBRARIES:
                subRspCode, pathFile, nameFile, extFile, dataFile, project, isLocked  = responseData['ret']
            else:
                raise Exception("repo type %s unknown" % responseData['repo-dst'])

            if subRspCode == CODE_OK:
                self.OpenFileRepo.emit(responseData['repo-dst'], str(pathFile), str(nameFile), str(extFile), dataFile, project, isLocked)
            elif subRspCode ==  CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Open file") , self.tr("File not found!") )
            elif subRspCode == CODE_LOCKED:    
                self.OpenFileRepo.emit(responseData['repo-dst'], str(pathFile), str(nameFile), str(extFile), dataFile, project, isLocked)
            elif subRspCode ==  CODE_ERROR:
                self.emitCriticalMsg( self.tr("Open file") , "%s\n%s" % (self.tr("Unable to open file!"),
                                        self.tr("If the problem persists contact your administrator.")) )
            elif subRspCode ==  CODE_FORBIDDEN:
                self.emitCriticalMsg( self.tr("Open file") , "%s" % self.tr("Unable to open file!\nPermission denied!") )   
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)

        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Open file") , self.tr("Adapters not installed!") )
            
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
            
        else:
            raise Exception("responseCode %s unknown" % responseCode)

    def onGetFileRepo(self, responseCode, responseData):
        """
        Called on get file from repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK: 
            if responseData['repo-dst'] == REPO_TESTS:
                subRspCode, pathFile, nameFile, extFile, dataFile, project, isLocked, forDest, actionId, testId = responseData['ret']
            else:
                raise Exception("repo type %s unknown" % responseData['repo-dst'])
            if subRspCode == CODE_OK:
                self.GetFileRepo.emit(responseData['repo-dst'], str(pathFile), str(nameFile), str(extFile), dataFile,
                                      project, forDest, actionId,  testId)
            elif subRspCode ==  CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Get file") , self.tr("File not found!") )
            elif subRspCode ==  CODE_ERROR:
                self.emitCriticalMsg( self.tr("Get file") , "%s\n%s" % (self.tr("Unable to open file!"),
                                        self.tr("If the problem persists contact your administrator.")) )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization on get file") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("responseCode %s unknown" % responseCode)
            
    def onCleanupLockFilesRepo(self, responseCode, responseData):
        """
        Called on cleanup lock files in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.emitWarningMsg( self.tr("Unlock all files") , self.tr("All files unlocked") )
        else:
            raise Exception("Cleanup lock file: responseCode %s unknown" % responseCode)

    def onUnlockFileRepo(self, responseCode, responseData):
        """
        Called on unlock file in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            pass
        else:
            self.error("Unlock file: responseCode %s unknown" % responseCode)

    def onPutFileRepo(self, responseCode, responseData):
        """
        Called on put file in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode, pathFile, nameFile, extFile, fileAlreadyExists, project, closeAfter, lockedBy = responseData['ret']

            if subRspCode  == CODE_OK:
                self.PutFileRepo.emit( (responseData['repo-dst'], str(pathFile), str(nameFile), 
                                            str(extFile), fileAlreadyExists, project, closeAfter) )
                if not fileAlreadyExists:
                    self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=project)
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Save file" , "This filename already exist!" )
                self.PutFileErrRepo.emit(  (responseData['repo-dst'], str(pathFile), str(nameFile), 
                                            str(extFile), fileAlreadyExists, project, closeAfter ) )
            elif subRspCode == CODE_LOCKED:  
                if sys.version_info > (3,): # python3 support
                    self.emitCriticalMsg( "File locked" , "This file is locked by the user %s\nUnable to save the file!" %  bytes2str(base64.b64decode(lockedBy)) )
                else:
                    self.emitCriticalMsg( "File locked" , "This file is locked by the user %s\nUnable to save the file!" %  base64.b64decode(lockedBy) )
            else:
                self.emitCriticalMsg( self.tr("Save file") , "%s\n%s" % (self.tr("Unable to save!"),
                                            self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Save file") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Put file: responseCode %s unknown" % responseCode)

    def onImportFileRepo(self, responseCode, responseData):
        """
        Called on import file in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode, pathFile, nameFile, extFile, project = responseData['ret']
            if subRspCode  == CODE_OK:
                self.ImportFileRepo.emit( (responseData['repo-dst'], str(pathFile), str(nameFile), str(extFile), project ) )
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=project)
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( self.tr("Import file") , "This filename already exist!" )
                self.ImportFileErrRepo.emit( (responseData['repo-dst'], str(pathFile), str(nameFile), str(extFile), project ) )
            else:
                self.emitCriticalMsg( self.tr("Import file") , "%s\n%s" % (self.tr("Unable to import!"), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization"), self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Importe file: responseCode %s unknown" % responseCode)

    def onAddDirRepo(self, responseCode, responseData):
        """
        Called on add folder in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.AddDirRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( self.tr("Add directory") , self.tr("This directory name already exist!") )
            else:
                self.emitCriticalMsg( self.tr("Add directory") , "%s\n%s" % (self.tr("Unable to add the folder!"), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Add folder") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Add dir: responseCode %s unknown" % responseCode)

    def onDelDirRepo(self, responseCode, responseData):
        """
        Called on delete folder in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.DelDirRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Delete directory") , self.tr("This directory does not exist!") )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( self.tr("Delete directory") , self.tr("The directory is not empty!") )
            else:
                self.emitCriticalMsg( self.tr("Delete directory") , "%s\n%s" % ( self.tr("Unable to delete the directory!"), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Delete directory") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Del dir: responseCode %s unknown" % responseData)

    def onDelDirAllRepo(self, responseCode, responseData):
        """
        Called on delete all folders in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.DelDirAllRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Delete all directories and files") , self.tr("This directory does not exist!") )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( self.tr("Delete all directories and files") , self.tr("All deletion forbidden!") )
            else:
                self.emitCriticalMsg( self.tr("Delete all directories and files") , "%s\n%s" % (self.tr("All deletion failed."), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Delete all directories and files") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Del all dir: responseCode %s unknown" % responseCode)
    
    def onDelFileRepo(self, responseCode, responseData):
        """
        Called on delete file in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.DelFileRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Delete file") , self.tr("This file does not exist!") )
            elif subRspCode == CODE_FAILED:
                self.emitCriticalMsg( self.tr("Delete file") , "%s\n%s" % (self.tr("Deletion failed!"), self.tr("If the problem persists contact your administrator.")) )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( self.tr("Delete file") , self.tr("Deletion forbidden!") )
            else:
                self.emitCriticalMsg( self.tr("Delete file") , "%s\n%s" % (self.tr("Deletion failed!"), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Delete file") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Del file: responseCode %s unknown" % responseData)

    def onRenameDirRepo(self, responseCode, responseData):
        """
        Called on rename folder in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode, mainPath, oldPath, newPath, project  = responseData['ret']
            if subRspCode == CODE_OK:
                self.RenameDirRepo.emit((responseData['repo-dst'], str(mainPath), str(oldPath), str(newPath), responseData['projectid']))
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Rename directory") , self.tr("This directory does not exist!") )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( self.tr("Rename directory") , self.tr("This directory name already exist!") )
            else:
                self.emitCriticalMsg( self.tr("Rename directory") ,"%s\n%s" % (self.tr("Unable to rename!"), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Rename directory") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Rename dir: responseCode %s unknown" % responseCode)

    def onDuplicateDirRepo(self, responseCode, responseData):
        """
        Called on duplicate folder in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.DuplicateDirRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Duplicate directory") , self.tr("This directory does not exist!") )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( self.tr("Duplicate directory") , self.tr("This directory name already exist!") )
            else:
                self.emitCriticalMsg( self.tr("Duplicate directory") ,"%s\n%s" % (self.tr("Duplication failed!"), self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Duplicate directory") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization"), self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Duplicate dir: responseCode %s unknown" % responseCode)

    def onRenameFileRepo(self, responseCode, responseData):
        """
        Called on rename file in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode, mainPath, oldFilename, newFilename, extFilename, project = responseData['ret']
            if subRspCode == CODE_OK:
                self.RenameFileRepo.emit((responseData['repo-dst'], str(mainPath), str(oldFilename), str(newFilename),
                                          extFilename, responseData['projectid'] ))
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Rename file") , self.tr("This file does not exist!") )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( self.tr("Rename file") , self.tr("This file name already exist!") )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( self.tr("Rename file") , self.tr("This file can not be renamed! Permission Denied") )
            else:
                self.emitCriticalMsg( self.tr("Rename file") , "%s\n%s" % (self.tr("Rename failed!"),
                                    self.tr("If the problem persists contact your administrator.")) )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Rename file") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Rename file: responseCode %s unknown" % responseCode)

    def onDuplicateFileRepo(self, responseCode, responseData):
        """
        Called on duplicate file in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.DuplicateFileRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=responseData['projectid'])
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( self.tr("Duplicate file") , self.tr("This file does not exist!") )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( self.tr("Duplicate file") , self.tr("This file name already exist!") )
            else:
                self.emitCriticalMsg( self.tr("Duplicate file") , self.tr("Duplication failed!") )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitCriticalMsg( self.tr("Duplicate file") , self.tr("Adapters not installed!") )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( self.tr("Authorization") , self.tr("You are not authorized to do that!") )
        else:
            raise Exception("Duplicate file: responseCode %s unknown" % responseCode)

    def onResetTestsStats(self, responseCode, responseData):
        """
        Called on reset statistics tests, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.ResetStatistics.emit()
                self.application().showMessageWarningTray(msg="Statistics are reseted!")
            else:
                self.emitInformationMsg( self.tr("Reset statistics") , self.tr("Statistics are reseted!") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Reset statistics") , "%s\n%s" % (self.tr("Unable to reset statistics!"), self.tr("If the problem persists contact your administrator.")) )
        else:
            raise Exception("Reset tests stats: responseData %s unknown" % responseCode)

    def onEmptyRepo(self, responseCode, responseData):
        """
        Called on repository empty, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        repoType = responseData['repo-dst']
        if responseCode == CODE_OK:
            if repoType == REPO_ADAPTERS:
                self.emitInformationMsg( self.tr("Uninstall adapters") , self.tr("Uninstallation successfull!") )
            elif repoType == REPO_LIBRARIES:
                self.emitInformationMsg( self.tr("Uninstall libraries") , self.tr("Uninstallation successfull!") )
            else:
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="The repository is now empty!")
                else:
                    self.emitInformationMsg( self.tr("Empty remote repository") , self.tr("The repository is now empty!") )
        elif responseCode == CODE_FAILED:
            if repoType == REPO_ADAPTERS:
                self.emitCriticalMsg( self.tr("Uninstall adapters") , "%s\ns%s" % (self.tr("Uninstallation failed!"), self.tr("If the problem persists contact your administrator.")) )
            if repoType == REPO_LIBRARIES:
                self.emitCriticalMsg( self.tr("Uninstall libraries") , "%s\n%s" % (self.tr("Uninstallation failed!"), self.tr("If the problem persists contact your administrator.")) )
            else:
                self.emitCriticalMsg( self.tr("Empty remote repository") , "%s\n%s" % ( self.tr("Unable to empty the repository!"), self.tr("If the problem persists contact your administrator.")) )
        else:
            raise Exception("Empty repo: responseCode %s unknown" % responseCode)

    def onZipRepoArchives(self, responseCode, responseData):
        """
        Called on create zip on repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            if subRspCode == CODE_OK:
                self.emitInformationMsg( self.tr("Zip test results") , self.tr("Test results zipped!") )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( self.tr("Zip test results"), self.tr("Unable to write zip on storage: no space left, permission denied or other") )
            else:
                self.emitCriticalMsg( self.tr("Zip test results") , self.tr("Unable to zip test results") )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Zip test results") , "%s\n%s" % ("Error to zip test results.", self.tr("If the problem persists contact your administrator.")) )
        else:
            raise Exception("Zip repo: responseCode %s unknown" % responseCode)

    def onRefreshStatsRepo(self, responseCode, responseData):
        """
        Called on refresh statistics from repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        repoType = responseData['repo-dst']
        if responseCode == CODE_OK:
            #self.loaderDialog.done(0)
            if repoType == REPO_TESTS:
                self.RefreshStatsRepo.emit(responseData)
            elif repoType == REPO_ADAPTERS:
                self.RefreshStatsRepoAdapters.emit(responseData)
            elif repoType == REPO_LIBRARIES:
                self.RefreshStatsRepoLibraries.emit(responseData)
            elif repoType == REPO_ARCHIVES:
                self.RefreshStatsRepoArchives.emit(responseData)
            else:
                self.error( 'repo type unknown: %s' % str(repoType) )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Refresh statistics") , "%s\n%s" % (self.tr("Unable to refresh statistics!"), self.tr("If the problem persists contact your administrator.")) )
        else:
            raise Exception("refresh stats: responseCode %s unknown" % responseCode)

    def onRefreshContextServer(self, responseCode, responseData):
        """
        Called on refresh context server, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshContextServer.emit(responseData)
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( self.tr("Refresh server context") , "%s\n%s" % (self.tr("Unable to refresh context!"), self.tr("If the problem persists contact your administrator.")) )
        else:
            raise Exception("refresh context: responseCode %s unknown" % responseCode)

    def onRefreshStatsServer(self, responseCode, responseData):
        """
        Called on refresh statistic server, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshStatsServer.emit(responseData)
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh server statistics" , "Error to refresh stats.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("refresh stats: responseCode %s unknown" % responseCode)

    def onDelAgent(self, responseCode, responseData):
        """
        Called on delete agent, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            if subRspCode == CODE_OK:
                self.emitInformationMsg( "Delete default agent" , "Default agent deleted!" )
            elif responseCode == CODE_FAILED:
                self.emitCriticalMsg( "Delete default agent" , "Failed to delete the default agent!" )
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( "Add default agent" , "This agent does not exists!" )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Delete agent" , "Agent module disabled on server side." )
        else:
            raise Exception("Del agent: responseCode %s unknown" % responseCode)

    def onAddAgent(self, responseCode, responseData):
        """
        Called on add agent, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            if subRspCode == CODE_OK:
                self.emitInformationMsg( "Add default agent" , "Default agent added!" )
            elif subRspCode == CODE_FAILED:
                self.emitCriticalMsg( "Add default agent" , "Failed to add the default agent!" )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( "Add default agent" , "Number of default agent is reached!\nPlease to update your licence if you want more default agents!" )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Add default agent" , "This agent already exists!" )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_DISABLED:
            self.emitWarningMsg( "Add agent" , "Agent module disabled on server side." )
        else:
            raise Exception("add agent: responseCode %s unknown" % responseCode)

    def onStartAgent(self, responseCode, responseData):
        """
        Called on start agent, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            titleMsg = 'Starting default agent'
            if subRspCode == AGENT_REG_OK:
                self.emitInformationMsg( titleMsg , "Agent started!" )
            elif subRspCode == AGENT_REG_FAILED:
                self.emitCriticalMsg( titleMsg , "Start failed: agent name already used!" )
            elif subRspCode == AGENT_REG_TIMEOUT:
                self.emitCriticalMsg( titleMsg , "Connection timeout!\nPlease retry!\nIf the problem persists contact your administrator." )
            elif subRspCode == AGENT_REG_REFUSED:
                self.emitCriticalMsg( titleMsg , "Number of registrations is reached!\nPlease to update your licence if you want more registration!" )
            elif subRspCode == AGENT_REG_CONN_REFUSED:
                self.emitCriticalMsg( titleMsg , "Server refuses the connection!" )
            elif subRspCode == AGENT_REG_HOSTNAME_FAILED:
                self.emitCriticalMsg( titleMsg , "Incorrect controler IP" )
            elif subRspCode == AGENT_TYPE_UNKNOWN:
                self.emitCriticalMsg( titleMsg , "Agent type not found!" )
            else:
                raise Exception("Unknown error occurred (%s)" % subRspCode)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Start agent", "Agent module disabled on server side." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Start agent", "Server error to start agent.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("start agent: responseCode %s unknown" % responseCode)   

    def onStopAgent(self, responseCode, responseData):
        """
        Called on stop agent, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.emitInformationMsg( "Stop agent" , "Agent stopped!" )
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Stop agent" , "Agent module disabled on server side." )
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Stop agent" , "This agent does not exist!" )
        else:
            raise Exception("stop agent: responseCode %s unknown" % responseCode)

    def onDelProbe(self, responseCode, responseData):
        """
        Called on delete probe, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            if subRspCode == CODE_OK:
                self.emitInformationMsg( "Delete default probe" , "Default probe deleted!" )
            elif responseCode == CODE_FAILED:
                self.emitCriticalMsg( "Delete default probe" , "Failed to delete the default probe!" )
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( "Add default probe" , "This probe does not exists!" )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Delete probe" , "Probe module disabled on server side." )
        else:
            raise Exception("del probe: responseCode %s unknown" % responseCode)

    def onAddProbe(self, responseCode, responseData):
        """
        Called on add probe, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            if subRspCode == CODE_OK:
                self.emitInformationMsg( "Add default probe" , "Default probe added!" )
            elif subRspCode == CODE_FAILED:
                self.emitCriticalMsg( "Add default probe" , "Failed to add the default probe!" )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( "Add default probe" , "Number of default probe is reached!\nPlease to update your licence if you want more default probes!" )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Add default probe" , "This probe already exists!" )
            else:
                raise Exception("sub responseCode %s unknown" % subRspCode)
        elif responseCode == CODE_DISABLED:
            self.emitWarningMsg( "Add probe" , "Probe module disabled on server side." )
        else:
            raise Exception("add probe: responseCode %s unknown" % responseCode)

    def onStartProbe(self, responseCode, responseData):
        """
        Called on start probe, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData
            titleMsg = 'Starting default probe'
            if subRspCode == PROBE_REG_OK:
                self.emitInformationMsg( titleMsg , "Probe started!" )
            elif subRspCode == PROBE_REG_FAILED:
                self.emitCriticalMsg( titleMsg , "Start failed: probe name already used!" )
            elif subRspCode == PROBE_REG_TIMEOUT:
                self.emitCriticalMsg( titleMsg , "Connection timeout!\nPlease retry!\nIf the problem persists contact your administrator." )
            elif subRspCode == PROBE_REG_REFUSED:
                self.emitCriticalMsg( titleMsg , "Number of registrations is reached!\nPlease to update your licence if you want more registration!" )
            elif subRspCode == PROBE_REG_CONN_REFUSED:
                self.emitCriticalMsg( titleMsg , "Server refuses the connection!" )
            elif subRspCode == PROBE_REG_HOSTNAME_FAILED:
                self.emitCriticalMsg( titleMsg , "Incorrect controler IP" )
            elif subRspCode == PROBE_TYPE_UNKNOWN:
                self.emitCriticalMsg( titleMsg , "Probe type not found!" )
            else:
                raise Exception("Unknown error occurred (%s)" % subRspCode)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Start probe", "Probe module disabled on server side." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Start probe", "Server error to start probe.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("start probe: responseCode %s unknown" % responseCode)   

    def onStopProbe(self, responseCode, responseData):
        """
        Called on stop probe, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.emitInformationMsg( "Stop probe" , "Probe stopped!" )
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Stop probe" , "Probe module disabled on server side." )
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Stop probe" , "This probe does not exist!" )
        else:
            raise Exception("stop probe: responseCode %s unknown" % responseCode)

    def onGenCacheHelp(self, responseCode, responseData):
        """
        Called on generate cache on help, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.emitInformationMsg( "Generate help cache", "Generation done!\n\nPlease to reload the documentation!\n(Right click on the helper tree)" )
        elif responseCode == CODE_FAILED:
            details =  "Unable to generate cache.\n\nFix the following error: %s" % responseData['details']
            details += "\nIf the problem persists contact your administrator." 
            self.emitCriticalMsg( "Generate help cache", details)
        else:
            raise Exception("generate cache help: responseCode %s unknown" % responseCode)

    def onDelTasksHistory(self, responseCode, responseData):
        """
        Called on delete task from history, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            pass
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Clear tasks history", "Error to clear tasks history.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("del tasks history: responseCode %s unknown" % responseCode)

    def onRefreshRunningProbes(self, responseCode, responseData):
        """
        Called on refresh running probes, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshRunningProbes.emit(responseData)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Refresh running probes", "Probe module disabled on server side." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh running probes", "Error to refresh running probes.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("refresh running probes: responseCode %s unknown" % responseCode)

    def onRefreshDefaultProbes(self, responseCode, responseData):
        """
        Called on refresh default probes, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshDefaultProbes.emit(responseData)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Refresh default probes", "Probe module disabled on server side." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh default probes", "Error to refresh default probes.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("refresh default probes: responseCode %s unknown" % responseCode)

    def onRefreshRunningAgents(self, responseCode, responseData):
        """
        Called on refresh running agents, response,

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshRunningAgents.emit(responseData)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Refresh running agents", "Agent module disabled on server side." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh running agents", "Error to refresh running agents.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("refresh running agents: responseCode %s unknown" % responseCode)

    def onRefreshDefaultAgents(self, responseCode, responseData):
        """
        Called on refresh default agents, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshDefaultAgents.emit(responseData)
        elif responseCode == CODE_DISABLED:
            self.emitInformationMsg( "Refresh default agents", "AGENT module disabled on server side." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh default agents", "Error to refresh default agents.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("refresh default agents: responseCode %s unknown" % responseCode)

    def onExportTestResultDesign(self, responseCode, responseData):
        """
        Called on export design from testresult, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            if "error" in responseData:
                if responseData["error"] == True:
                    if responseData["error-details"] == "Syntax":
                        self.emitCriticalMsg( "Test Design", "Unable to prepare the design of the test!\nSyntax error detected in this test!" )
                    else:
                        self.emitCriticalMsg( "Test Design", "Unable to prepare the design!" )
                else:
                    self.TestresultDesignLoaded.emit(responseData['design'], responseData['design-xml'])
            else:
                self.TestresultDesignLoaded.emit(responseData['design'], responseData['design-xml'])
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Test Design", "Not test result found!" )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Test Design", "Error to get the design.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Export test result: Design responseCode %s unknown" % responseData)

    def onExportTestResultVerdict(self, responseCode, responseData):
        """
        Called on export verdict from testresult, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.TestresultVerdictLoaded.emit(responseData['verdict'], responseData['verdict-xml'])
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Test Verdict", "Not test result found!" )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Test Verdict", "Error to get the verdict.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Export test Verdict responseCode %s unknown" % responseData)

    def onExportTestResultReport(self, responseCode, responseData):
        """
        Called on export report from testresult, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.TestresultReportLoaded.emit(responseData['report'], responseData['report-xml'])
        elif responseCode == CODE_NOT_FOUND:
            self.emitCriticalMsg( "Test Report", "Not test result found!" )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Test Report", "Unable to get the report.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Export test Report responseCode %s unknown" % responseData)

    def onAddDevTimeTest(self, responseCode, responseData):
        """
        Called on add development time, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            pass
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Test development duration", "Error to save the development duration.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Add dev time: responseCode %s unknown" % responseData)

    def onAddCommentArchive(self, responseCode, responseData):
        """
        Called on add comment in archive, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode, oldArchivesPath, newArchivesPath, archivesComments = responseData['ret']
            if subRspCode == CODE_OK:
                self.CommentArchiveAdded.emit( str(oldArchivesPath), str(newArchivesPath), archivesComments, responseData['display-posts'])
            else:
                self.emitCriticalMsg( "Add comment", "Unable to add comment.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Add comment: responseCode %s unknown" % responseData)

    def onLoadCommentsArchive(self, responseCode, responseData):
        """
        Called on load coments from archive, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode, archivesPath, archivesComments = responseData['ret']
            if subRspCode == CODE_OK:
                self.CommentsArchiveLoaded.emit(str(archivesPath), archivesComments)
            else:
                self.emitCriticalMsg( "Load comments", "Unable to load comments.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Load comments: responseCode %s unknown" % responseData)

    def onDelCommentsArchive(self, responseCode, responseData):
        """
        Called on delete comments on archive, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode, archivesPath = responseData['ret']
            if subRspCode == CODE_OK:
                self.CommentsArchiveDeleted.emit(str(archivesPath))
            else:
                self.emitCriticalMsg( "Delete comments", "Unable to delete comments.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Del comments: responseCode %s unknown" % responseData)

    def onBackupRepo(self, responseCode, responseData):
        """
        Called on backup in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.emitInformationMsg( "Backup", "Backup created with success!" )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( "Backup", "Unable to write backup on storage: no space left, permission denied or other.\nIf the problem persists contact your administrator." )
            else:
                self.emitCriticalMsg( "Backup", "Unable to create the backup.\nIf the problem persists contact your administrator." )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Backup", "Unable to create the backup.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Backups repo: responseCode %s unknown" % responseCode)

    def onDeleteBackupsRepo(self, responseCode, responseData):
        """
        Called on delete backups on repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.emitInformationMsg( "Delete backups", "All backups deleted with success!" )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( "Delete backups", "Unable to delete backups on storage: no space left, permission denied or other.\nIf the problem persists contact your administrator." )
            else:
                self.emitCriticalMsg( "Delete backups", "Unable to delete all backups.\nIf the problem persists contact your administrator." )
                # self.loaderDialog.setTxt( title = "Delete backups", txt = "Error to delete all backups", error=True )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Delete backups", "Unable to delete backups.\nIf the problem persists contact your administrator." )
            # self.loaderDialog.setTxt( title = "Delete backups", txt = "Unable to delete backups", error=True )
        else:
            raise Exception("Delete backups: responseCode %s unknown" % responseCode)

    def onAddLibraryRepo(self, responseCode, responseData):
        """
        Called on add library in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.AddLibraryRepo.emit()
                self.refreshRepo(repo=REPO_LIBRARIES, showPopup=False)
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Add library", "This library name already exist!" )
            else:
                self.emitCriticalMsg( "Add library", "Creation failed.\nIf the problem persists contact your administrator." )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( "Authorization", "You are not authorized to do that!" )
        else:
            raise Exception("Add library: responseCode %s unknown" % responseCode)

    def onAddAdapterRepo(self, responseCode, responseData):
        """
        Called on add adapter in repository, response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            subRspCode = responseData['ret']
            if subRspCode == CODE_OK:
                self.AddAdapterRepo.emit()
                self.refreshRepo(repo=REPO_ADAPTERS, showPopup=False)
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Add adapter", "This adapter name already exist!" )
            else:
                self.emitCriticalMsg( "Add adapter", "Creation failed.\nIf the problem persists contact your administrator." )
        elif responseCode == CODE_FORBIDDEN:
            self.emitCriticalMsg( "Authorization", "You are not authorized to do that!" )
        else:
            raise Exception("Add adapter: responseCode %s unknown" % responseCode)

    def onRefreshHelper(self, responseCode, responseData):
        """
        Called on refresh helper response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            self.RefreshHelper.emit(responseData)
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh helper", "Unable to refresh documentations" )
        else:
            raise Exception("refresh helper: responseCode %s unknown" % responseData)

    def onCheckSyntax(self, responseCode, responseData):
        """
        Called on check syntax response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            statusSyntax = responseData['ret']
            errorSyntax = responseData['syntax-error']
            if statusSyntax:
                self.emitInformationMsg( self.tr("Check syntax"), "%s\n%s" % ( self.tr("Well done!"), "No syntax error detected.") )
            else:
                msg = "An error exists on this file."
                msg += "\n%s" % errorSyntax
                self.emitCriticalMsg( self.tr("Check syntax"), msg )
        else:
            raise Exception("check syntax: responseCode %s unknown" % responseData)

    def onCheckSyntaxes(self, responseCode, responseData):
        """
        Called on check syntaxes response

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            statusSyntax = responseData['ret']
            errorSyntax = responseData['syntax-error']
            if statusSyntax:
                self.emitInformationMsg( self.tr("Check syntax"), "%s\n%s" % (self.tr("Well done!"), "No syntax error detected.") )
            else:
                self.emitCriticalMsg( self.tr("Check syntax"), str(errorSyntax) )
        else:
            raise Exception("check syntaxes: responseCode %s unknown" % responseData)

    def onMoveFileRepo(self, responseCode, responseData):
        """
        Called on move file on repository

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode, mainPath, fileName, newPath, extFilename, project = responseData['ret']
            if subRspCode == CODE_OK:
                self.MoveFileRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=project)
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( "Move file", "This file does not exist!" )
            elif subRspCode == CODE_FAILED:
                self.emitCriticalMsg( "Move file", "Move failed.\nIf the problem persists contact your administrator." )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( "Move file", "Move forbidden." )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Move file", "Move not authorized, identical testname detected." )
            else:
                self.emitCriticalMsg( "Move file", "Move failed.\nIf the problem persists contact your administrator." )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitWarningMsg( "Move file", "Adapters not installed!" )
        elif responseCode == CODE_FORBIDDEN:
            self.emitWarningMsg( "Authorization", "You are not authorized to do that!" )
        else:
            raise Exception("Move files: responseCode %s unknown" % responseData)

    def onMoveFolderRepo(self, responseCode, responseData):
        """
        Called on move folder on repository

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            repoType = responseData['repo-dst']
            subRspCode, mainPath, folderName, newPath, project = responseData['ret']
            if subRspCode == CODE_OK:
                self.MoveFolderRepo.emit()
                self.refreshRepo(repo=responseData['repo-dst'], showPopup=False, project=project)
            elif subRspCode == CODE_NOT_FOUND:
                self.emitCriticalMsg( "Move folder", "The folder to move does not exist!" )
            elif subRspCode == CODE_FAILED:
                self.emitCriticalMsg( "Move folder", "Move failed.\nIf the problem persists contact your administrator." )
            elif subRspCode == CODE_FORBIDDEN:
                self.emitCriticalMsg( "Move folder", "Move forbidden." )
            elif subRspCode == CODE_ALLREADY_EXISTS:
                self.emitCriticalMsg( "Move folder", "Move not authorized, identical destination folder detected." )
            else:
                self.emitCriticalMsg( "Move folder", "Move failed.\nIf the problem persists contact your administrator." )
        elif responseCode == CODE_NOT_FOUND and responseData['repo-dst']==REPO_ADAPTERS:
            self.emitWarningMsg( "Move folder", "Adapters not installed!" )
        elif responseCode == CODE_FORBIDDEN:
            self.emitWarningMsg( "Authorization", "You are not authorized to do that!" )
        else:
            raise Exception("Moves folder: responseCode %s unknown" % responseData)

    def onRefreshTasks(self, responseCode, responseData):
        """
        Called on refresh tasks

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        taskType = responseData['task-type']
        if responseCode == CODE_OK:
            if taskType == TASKS_WAITING:
                self.RefreshTasksWaiting.emit(responseData)
            elif taskType == TASKS_RUNNING:
                self.RefreshTasksRunning.emit(responseData)
            elif taskType == TASKS_HISTORY:
                self.RefreshTasksHistory.emit(responseData)
            else:
                self.error( 'task type unknown: %s' % str(taskType) )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Refresh tasks", "Error to refresh tasks.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Refresh tasks: responseCode %s unknown" % responseCode)

    def onLoadTestCache(self, responseCode, responseData):
        """
        Called on load test cache

        @param responseCode: 
        @type responseCode:

        @param responseData: 
        @type responseData:
        """
        if responseCode == CODE_OK:
            dataRsp = responseData['ret']
            if len(dataRsp) == 0:
                self.emitCriticalMsg( "Load partial test", "Error to load a partial test!\nIf the problem persists contact your administrator." )
            else:
                #{'sub-path': '17:31:36.874162.Tm9uYW1lMQ==.admin', 'main-path': '2012-07-21', 'filename': 'Noname1_tmp.trx'}
                self.downloadResultLogsV2(  trPath='%s/%s/' % (dataRsp['main-path'], dataRsp['sub-path']), 
                                            trName = dataRsp['filename'], projectId=dataRsp['project-id'] )
        elif responseCode == CODE_FAILED:
            self.emitCriticalMsg( "Load partial test", "Server error to load a partial test.\nIf the problem persists contact your administrator." )
        else:
            raise Exception("Load tests cache: responseCode %s unknown" % responseCode)

    def onError(self, err, title="Error"):
        """
        Called on xml rpc error

        @param err: 
        @type err:

        @param title: 
        @type title:
        """
        self.error( "%s: %s" % (title,err) )
        self.closeConnection()
        ServerExplorer.instance().stopWorking()
        self.emitCriticalMsg( title,  err )

    def __callXmlrpc(self, xmlrpcFunc, xmlrpcData={}, showPopup=True):
        """
        Private function
        XML rpc call

        @param xmlrpcFunc: 
        @type xmlrpcFunc:

        @param xmlrpcData: 
        @type xmlrpcData:

        @param showPopup: 
        @type showPopup:
        """
        self.BusyCursor.emit()
        fromGui = True
        if xmlrpcFunc==AUTHENTICATE_CLIENT:
            call_string = xmlrpclib.dumps( (xmlrpcData,fromGui), xmlrpcFunc )
        else:
            call_string = xmlrpclib.dumps( (self.login, self.password, xmlrpcData, fromGui ), xmlrpcFunc )

        self.trace('XMLRPC request sent: %s' % call_string)
        self.WebCall.emit( call_string )
    
    def __getCurrentVersion(self):
        """
        Private function
        Returns current version

        @return:
        @rtype: dict
        """
        data = { 
                    'ver': self.clientVersion, 
                    'os': sys.platform, 
                    'portable': QtHelper.str2bool(Settings.instance().readValue( key = 'Common/portable')) 
               }
        return data

    def getClientUpdateAuto (self):
        """
        Check client update 
        """
        if not self.isAuthenticated(): 
            self.Disconnected.emit() 
            return

        self.trace('[XMLRPC] Check client update auto...')
        try:
            xmlrpcData = self.__getCurrentVersion()
            self.__callXmlrpc( xmlrpcFunc=CHECK_UPDATE_AUTO, xmlrpcData=xmlrpcData )
        except Exception as e:
            self.onError( title='get update auto', err=str(e) )

    def getClientUpdate (self, silence=False):
        """
        Check client update 
        """
        self.trace('[XMLRPC] Check client update...')
        try:
            xmlrpcData = self.__getCurrentVersion()
            xmlrpcData['silence'] = silence 
            self.__callXmlrpc( xmlrpcFunc=CHECK_UPDATE, xmlrpcData=xmlrpcData )
        except Exception as e:
            self.onError( title='get update', err=str(e) )

    def replayTest (self, testId):
        """
        Replay a test

        @param testId: 
        @type testId:
        """
        self.trace('[XMLRPC] Replay test...')
        try:
            self.trace('[XMLRPC] calling xmlrpc function')
            xmlrpcData = {'tid': testId}
            self.__callXmlrpc( xmlrpcFunc=REPLAY_TEST, xmlrpcData=xmlrpcData )
        except Exception as e:
            self.onError( title='replay test', err=str(e) )

    def __readTestPlan(self, testplan):
        """
        Private function
        Read local testplan

        @param testplan: 
        @type testplan:

        @return:
        @rtype:
        """
        ret = []
        return ret

    def prepareTest (self, wdocument=None, testId=0, background = False, runAt = (0,0,0,0,0,0), runType=0, runNb=-1, withoutProbes=False, 
                            debugActivated=False, withoutNotif=False, noKeepTr=False, prjId=0, testFileExtension=None, testFilePath=None,
                            testFileName=None, fromTime=(0,0,0,0,0,0), toTime=(0,0,0,0,0,0), prjName='', stepByStep=False, breakpoint=False,
                            channelId=False):
        """
        Prepare test

        @param testId: 
        @type testId:

        @param background: 
        @type background: boolean

        @param runAt: 
        @type runAt: tuple of integer

        @param runType: 
        @type runType: Integer

        @param runNb: 
        @type runNb:

        @param withoutProbes: 
        @type withoutProbes:

        @param debugActivated: 
        @type debugActivated:

        @param withoutNotif: 
        @type withoutNotif:

        @param noKeepTr: 
        @type noKeepTr:

        @param prjId: 
        @type prjId:

        @param testFileExtension: 
        @type testFileExtension:

        @param testFilePath: 
        @type testFilePath:

        @param testFileName: 
        @type testFileName:
        
        @return:
        @rtype:
        """
        dat = None
        try:
            data__ =  { 'user': self.login, 'user-id': self.userId, 'prj-id': prjId, 'test-id': testId, 'background': background, 
                        'runAt': runAt, 'runType': runType, 'runNb': runNb, 'withoutProbes': withoutProbes, 
                        'debugActivated': debugActivated, 'withoutNotif': withoutNotif, 'noKeepTr': noKeepTr,
                        'fromTime': fromTime, 'toTime': toTime, 'prj-name': prjName, 
                        'step-by-step': stepByStep, 'breakpoint': breakpoint, 'channel-id': channelId }

            if wdocument is None:
                self.trace('[prepareTest] no content, prepare test, type %s' % testFileExtension)
                data__.update( { 'nocontent': True, 'testname': testFileName, 'testpath': testFilePath, 'testextension': testFileExtension } )
            else:
                self.trace('[prepareTest] prepare test, type %s' % wdocument.extension)
                properties = copy.deepcopy( wdocument.dataModel.properties['properties'] )
                testfileName = wdocument.getShortName( withAsterisk = False, withLocalTag=False)
                testPath = ""
                if wdocument.isRemote:
                    testPath = wdocument.getPath(withExtension = False, withLocalTag=False)

                if wdocument.extension == EXT_TESTSUITE:
                    # load datasets
                    self.__loadDataset(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadDataset(parameters=properties['outputs-parameters']['parameter'])

                    # load images
                    self.__loadImage(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadImage(parameters=properties['outputs-parameters']['parameter'])

                    # prepare content
                    srcEditor = unicode( wdocument.srcEditor.text() )
                    execEditor = unicode( wdocument.execEditor.text() )
                    data__.update( { 'src': srcEditor, 'src2': execEditor, 'properties': properties, 'testname': testfileName,
                                    'testpath': testPath } )

                elif wdocument.extension == EXT_TESTABSTRACT:
                    # load datasets
                    self.__loadDataset(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadDataset(parameters=properties['outputs-parameters']['parameter'])

                    # load images
                    self.__loadImage(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadImage(parameters=properties['outputs-parameters']['parameter'])

                    # prepare content
                    #wdocument.constructTestDef2()
                    #return
                    srcEditor = unicode( wdocument.constructTestDef() )
                    data__.update( { 'testabstract': True, 'src': srcEditor, 'src2': '', 'properties': properties,
                                    'testname': testfileName, 'testpath': testPath } )

                elif wdocument.extension == EXT_TESTUNIT:
                    # load datasets
                    self.__loadDataset(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadDataset(parameters=properties['outputs-parameters']['parameter'])

                    # load images
                    self.__loadImage(parameters=properties['inputs-parameters']['parameter'])
                    self.__loadImage(parameters=properties['outputs-parameters']['parameter'])

                    # prepare content
                    srcEditor = unicode( wdocument.srcEditor.text() )
                    data__.update( { 'testunit': True, 'src': srcEditor, 'src2': '', 'properties': properties,
                                'testname': testfileName, 'testpath': testPath } )

                elif wdocument.extension == EXT_TESTGLOBAL:
                    testglobal =  copy.deepcopy( wdocument.getDataModelSorted() )
                    self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
                    alltests = []
                    all_id = [] 
                    for ts in testglobal:   
                        all_id.append(ts['id'])
                        if ts['type'] == TESTPLAN_REPO_FROM_LOCAL or ts['type'] == TESTPLAN_REPO_FROM_LOCAL_REPO_OLD:
                            if self.localConfigured != "Undefined":
                                absPath = '%s/%s' % ( self.localConfigured, ts['file'] )
                            else:
                                raise Exception("local repository not configured")
                        elif ts['type'] == TESTPLAN_REPO_FROM_OTHER or ts['type'] == TESTPLAN_REPO_FROM_HDD:
                            absPath = ts['file'] 
                        elif ts['type'] == TESTPLAN_REPO_FROM_REMOTE:
                            pass
                        else:
                            raise Exception("test type from unknown: %s" % ts['type'])
                        
                        # load dataset
                        self.__loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'])

                        # load image
                        self.__loadImage(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadImage(parameters=ts['properties']['outputs-parameters']['parameter'])

                        if ts['type'] != TESTPLAN_REPO_FROM_REMOTE:
            
                            if not os.path.exists( absPath ):
                                raise Exception("the following test file is missing: %s " % absPath)
                            
                            if absPath.endswith(EXT_TESTSUITE):
                                doc = FileModelTestSuite.DataModel()
                            elif absPath.endswith(EXT_TESTUNIT):
                                doc = FileModelTestUnit.DataModel()
                            elif absPath.endswith(EXT_TESTABSTRACT):
                                doc = FileModelTestAbstract.DataModel()
                            elif absPath.endswith(EXT_TESTPLAN):
                                doc = FileModelTestPlan.DataModel()
                            else:
                                raise Exception("the following test extension file is incorrect: %s " % absPath)

                            res = doc.load( absPath = absPath )
                            if res:
                                try:
                                    tmp = str(ts['file']).rsplit("/", 1)
                                    if len(tmp) ==1:
                                        filenameTs = tmp[0].rsplit(".", 1)[0]
                                    else:
                                        filenameTs = tmp[1].rsplit(".", 1)[0]
                                except Exception as e:
                                    self.error( 'fail to parse filename: %s' % e)
                                    raise Exception('fail to parse filename')                                
                                # Update current test suite parameters with testplan parameter
                                self.__updateParameter( currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                                            newParam=ts['properties']['inputs-parameters']['parameter'] )
                                self.__updateParameter( currentParam=doc.properties['properties']['outputs-parameters']['parameter'],
                                                            newParam=ts['properties']['outputs-parameters']['parameter'] )

                                ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']
                                ts['properties']['outputs-parameters'] = doc.properties['properties']['outputs-parameters']

                                if absPath.endswith(EXT_TESTSUITE):
                                    ts.update( { 'src': doc.testdef, 'src2': doc.testexec, 'path': filenameTs } )
                                    alltests.append( ts )
                                elif absPath.endswith(EXT_TESTUNIT):
                                    ts.update( { 'src': doc.testdef, 'path': filenameTs } ) 
                                    alltests.append( ts )
                                elif absPath.endswith(EXT_TESTABSTRACT):
                                    ts.update( { 'src': doc.testdef, 'path': filenameTs } ) 
                                    alltests.append( ts )
                                elif absPath.endswith(EXT_TESTPLAN):
                                    pass #todo
                        else:
                            alltests.append( ts )
                    data__.update( { 'testglobal': alltests, 'properties': properties, 'testname': testfileName, 'testpath': testPath } )
                    self.trace('TestGlobal, tests id order: %s' % all_id)

                elif wdocument.extension == EXT_TESTPLAN:
                    testplan =  copy.deepcopy( wdocument.getDataModelSorted() )                    
                    self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
                    all_id = [] 
                    for ts in testplan: 
                        all_id.append(ts['id'])
                        if ts['type'] == TESTPLAN_REPO_FROM_LOCAL or ts['type'] == TESTPLAN_REPO_FROM_LOCAL_REPO_OLD:
                            if self.localConfigured != "Undefined":
                                absPath = '%s/%s' % ( self.localConfigured, ts['file'] )
                            else:
                                raise Exception("local repository not configured")
                        elif ts['type'] == TESTPLAN_REPO_FROM_OTHER or ts['type'] == TESTPLAN_REPO_FROM_HDD:
                            absPath = ts['file'] 
                        elif ts['type'] == TESTPLAN_REPO_FROM_REMOTE:
                            pass
                        else:
                            raise Exception("test type from unknown: %s" % ts['type'])
                        
                        # load dataset
                        self.__loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'])

                        # load image
                        self.__loadImage(parameters=ts['properties']['inputs-parameters']['parameter'])
                        self.__loadImage(parameters=ts['properties']['outputs-parameters']['parameter'])

                        if ts['type'] != TESTPLAN_REPO_FROM_REMOTE:
            
                            if not os.path.exists( absPath ):
                                raise Exception("the following test file is missing: %s " % absPath)
                            
                            if absPath.endswith(EXT_TESTSUITE):
                                doc = FileModelTestSuite.DataModel()
                            elif absPath.endswith(EXT_TESTABSTRACT):
                                doc = FileModelTestAbstract.DataModel()
                            else:
                                doc = FileModelTestUnit.DataModel()
                            res = doc.load( absPath = absPath )
                            if res:
                                tmp = str(ts['file']).rsplit("/", 1)
                                filenameTs = tmp[1].rsplit(".", 1)[0]
                                
                                # Update current test suite parameters with testplan parameter
                                self.__updateParameter( currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                                            newParam=ts['properties']['inputs-parameters']['parameter'] )
                                self.__updateParameter( currentParam=doc.properties['properties']['outputs-parameters']['parameter'],
                                                            newParam=ts['properties']['outputs-parameters']['parameter'] )

                                ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']
                                ts['properties']['outputs-parameters'] = doc.properties['properties']['outputs-parameters']

                                ts.update( { 'src': doc.testdef, 'src2': doc.testexec, 'path': filenameTs } )
            
                    data__.update( { 'testplan': testplan, 'properties': properties, 'testname': testfileName, 'testpath': testPath } )
                    self.trace('TestPlan, tests id order: %s' % all_id)

            # compress
            self.trace('[XMLRPC] Check syntax test, test constructed')

            try:
                json_data = json.dumps(data__)
            except Exception as e:
                self.error('unable to encode with to json: %s' % e)
            else:
                try:
                    if sys.version_info > (3,):
                        compressed = zlib.compress( bytes(json_data, 'utf8') )
                    else:
                        compressed = zlib.compress( json_data )
                except Exception as e:
                    self.error('unable to compress with zip: %s' % e)
                else:
                    dat = xmlrpclib.Binary( compressed )
                    self.trace('[XMLRPC] test compressed')
        except Exception as e:
            self.error( e )
            ServerExplorer.instance().stopWorking()
            self.emitCriticalMsg( "Prepare Error",  "Prepare test: %s" % str(e) )
        return dat

    def __loadImage(self, parameters):
        """
        Private function
        Load image

        @param parameters: 
        @type parameters:
        """
        self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
        for pr in parameters:
            if pr['type'] == 'image':
                if pr['value'].startswith('undefined:/'):
                    fileName = pr['value'].split('undefined:/')[1]
                    if not os.path.exists( fileName ):
                        raise Exception("the following image file is missing: %s " % fileName)

                    file = QFile(fileName)
                    if not file.open(QIODevice.ReadOnly):
                        raise Exception("error opening image file %s" % fileName )
                    else:
                        imageData= file.readAll()
                        pr['value'] = "undefined:/%s" % base64.b64encode(imageData)
                elif pr['value'].startswith('local-tests:/'):
                    fileName = pr['value'].split('local-tests:/')[1]

                    if not os.path.exists( fileName ):
                        raise Exception("the following image file is missing: %s " % fileName)
                    
                    file = QFile(fileName)
                    if not file.open(QIODevice.ReadOnly):
                        raise Exception("error opening image file %s" % fileName )
                    else:
                        imageData= file.readAll()
                        pr['value'] = "local-tests:/%s" % base64.b64encode(imageData)
                else:
                    pass

    def __loadDataset(self, parameters):
        """
        Private function
        Load dataset

        @param parameters: 
        @type parameters:
        """
        self.localConfigured = Settings.instance().readValue( key = 'Common/local-repo' )
        for pr in parameters:
            if pr['type'] == 'dataset':
                if pr['value'].startswith('undefined:/'):
                    fileName = pr['value'].split('undefined:/')[1]
                    if not os.path.exists( fileName ):
                        raise Exception("the following test data file is missing: %s " % fileName)

                    doc = FileModelTestData.DataModel()
                    res = doc.load( absPath = fileName )
                    pr['value'] = "undefined:/%s" % doc.getRaw()
                elif pr['value'].startswith('local-tests:/'):
                    fileName = pr['value'].split('local-tests:/')[1]

                    if not os.path.exists( fileName ):
                        raise Exception("the following test data file is missing: %s " % fileName)
                    
                    doc = FileModelTestData.DataModel()
                    res = doc.load( absPath = fileName )
                    pr['value'] = "local-tests:/%s" % doc.getRaw()
                else:
                    pass

    def __updateParameter(self, currentParam, newParam):
        """
        Private function
        Update current test suite parameters with testplan parameter

        @param currentParam: 
        @type currentParam:

        @param newParam: 
        @type newParam:
        """
        for i in xrange(len(currentParam)):
            for np in newParam:
                if np['name'] == currentParam[i]['name']:
                    currentParam[i] = np
            
    @calling_xmlrpc
    def checkSyntaxAdapter (self, wdocument):
        """
        Check syntax of one adapter

        @param wdocument: 
        @type wdocument:
        """
        content_encoded = wdocument.getraw_encoded()
        if wdocument.path is None:
            wdocpath = ''
        else:
            wdocpath = wdocument.path
        xmlrpcData = { 'path': wdocpath, 'filename': wdocument.filename , 'extension': wdocument.extension, 'content': content_encoded, }
        self.__callXmlrpc( xmlrpcFunc=CHECK_SYNTAX_ADAPTER, xmlrpcData=xmlrpcData ) 

    @calling_xmlrpc
    def checkSyntaxAdapters (self):
        """
        Check syntax of all adapters
        """
        self.__callXmlrpc( xmlrpcFunc=CHECK_SYNTAX_ADAPTERS )   

    @calling_xmlrpc
    def checkSyntaxLibrary (self, wdocument):
        """
        Check syntax of one library

        @param wdocument: 
        @type wdocument:
        """
        content_encoded = wdocument.getraw_encoded()
        if wdocument.path is None: 
            wdocpath = ''
        else: 
            wdocpath = wdocument.path
        xmlrpcData = { 'path': wdocpath, 'filename': wdocument.filename , 'extension': wdocument.extension, 'content': content_encoded, }
        self.__callXmlrpc( xmlrpcFunc=CHECK_SYNTAX_LIBRARY, xmlrpcData=xmlrpcData ) 

    @calling_xmlrpc
    def checkSyntaxLibraries (self):
        """
        Check syntax of all libraries
        """
        self.__callXmlrpc( xmlrpcFunc=CHECK_SYNTAX_LIBRARIES )  

    @calling_xmlrpc
    def checkSyntaxTest (self, wdocument, testId, background = False, runAt = (0,0,0,0,0,0), runType=0, runNb=-1, 
                                withoutProbes=False, debugActivated=False,
                                withoutNotif=False, noKeepTr=False, prjId=0):
        """
        Send Test to the server
        
        @param wdocument: 
        @type wdocument:

        @param testId: 
        @type testId:

        @param background: 
        @type background: boolean

        @param runAt: 
        @type runAt: tuple of integer

        @param runType: 
        @type runType: Integer

        @param runNb: 
        @type runNb:

        @param withoutProbes: 
        @type withoutProbes:

        @param debugActivated: 
        @type debugActivated:

        @param withoutNotif: 
        @type withoutNotif:

        @param noKeepTr: 
        @type noKeepTr:

        @param prjId: 
        @type prjId:
        """
        xmlrpcData = self.prepareTest(wdocument, testId, background, runAt, runType, runNb, withoutProbes, 
                                        debugActivated, withoutNotif, noKeepTr, prjId)
        if xmlrpcData is not None:
            self.trace('[XMLRPC] calling xmlrpc function')
            self.__callXmlrpc( xmlrpcFunc=CHECK_SYNTAX_TEST, xmlrpcData=xmlrpcData )            

    @calling_xmlrpc
    def checkDesignTest (self, wdocument=None, prjId=0, prjName=''):
        """
        Send Test to the server
        
        @param wdocument: 
        @type wdocument:

        @param prjId: 
        @type prjId:
        """     
        xmlrpcData = self.prepareTest( wdocument=wdocument,  prjId=prjId, prjName=prjName )
        if xmlrpcData is not None:
            self.__callXmlrpc( xmlrpcFunc=CHECK_DESIGN_TEST, xmlrpcData=xmlrpcData )    

    @calling_xmlrpc
    def scheduleTests(self, tests, later=False, runAt=(0,0,0,0,0,0), runSimultaneous=False):
        """
        Schedule several tests
        """      
        xmlrpcData = { 'tests': tests, 'later': later, 'run-at': runAt, 'simultaneous': runSimultaneous}
        self.__callXmlrpc( xmlrpcFunc=SCHEDULE_TESTS, xmlrpcData=xmlrpcData )    

    @calling_xmlrpc
    def scheduleTest (self, wdocument=None, testId=0, background = False, runAt = (0,0,0,0,0,0), runType=0, runNb=-1, withoutProbes=False, 
                            debugActivated=False, withoutNotif=False, noKeepTr=False, prjId=0, testFileExtension=None, testFilePath=None, testFileName=None,
                            fromTime=(0,0,0,0,0,0), toTime=(0,0,0,0,0,0), stepByStep=False, breakpoint=False, channelId=False ):
        """
        Send Test to the server
        
        @param wdocument: 
        @type wdocument:

        @param testId: 
        @type testId:

        @param background: 
        @type background: boolean

        @param runAt: 
        @type runAt: tuple of integer

        @param runType: 
        @type runType: Integer

        @param runNb: 
        @type runNb:

        @param withoutProbes: 
        @type withoutProbes:

        @param debugActivated: 
        @type debugActivated:

        @param withoutNotif: 
        @type withoutNotif:

        @param noKeepTr: 
        @type noKeepTr:

        @param prjId: 
        @type prjId:

        @param testFileExtension: 
        @type testFileExtension:

        @param testFilePath: 
        @type testFilePath:

        @param testFileName: 
        @type testFileName:
        """       
        xmlrpcData = self.prepareTest(wdocument, testId, background, runAt, runType, runNb, withoutProbes, debugActivated, withoutNotif, noKeepTr, 
                                            prjId=prjId, testFileExtension=testFileExtension, testFilePath=testFilePath, testFileName=testFileName,
                                        fromTime=fromTime, toTime=toTime, stepByStep=stepByStep, breakpoint=breakpoint, channelId=channelId)
        if xmlrpcData is not None:
            if wdocument is not None:
                path = wdocument.getShortName( withAsterisk = False )
                TestResults.instance().newTest( name = "[] %s" % path, projectId=prjId )
            else:
                TestResults.instance().newTest( name = "[] %s" % testFileName, projectId=prjId )
            self.trace('[XMLRPC] calling xmlrpc function')
            self.__callXmlrpc( xmlrpcFunc=SCHEDULE_TEST, xmlrpcData=xmlrpcData )    

    @calling_xmlrpc
    def rescheduleTest (self, taskId, runAt = (0,0,0,0,0,0), runType=0, runNb=-1, withoutProbes=False, 
                            runEnabled=True, debugActivated=False, withoutNotif=False,
                            noKeepTr=False, fromTime=(0,0,0,0,0,0), toTime=(0,0,0,0,0,0) ):
        """
        Rescheduler test and inform the server

        @param taskId: 
        @type taskId:

        @param runAt: 
        @type runAt: tuple of integer

        @param runType: 
        @type runType: Integer

        @param runNb: 
        @type runNb:

        @param withoutProbes: 
        @type withoutProbes:

        @param runEnabled: 
        @type runEnabled:

        @param debugActivated: 
        @type debugActivated:

        @param withoutNotif: 
        @type withoutNotif:

        @param noKeepTr: 
        @type noKeepTr:
        """      
        self.trace('[XMLRPC] calling xmlrpc function')
        xmlrpcData = { 'taskId': taskId, 'runAt': runAt, 'runType': runType, 'runNb': runNb, 'runEnabled': runEnabled,
                        'withoutProbes': withoutProbes, 'debugActivated': debugActivated, 'withoutNotif': withoutNotif,
                        'noKeepTr': noKeepTr, 'fromTime': fromTime, 'toTime': toTime }
        self.__callXmlrpc( xmlrpcFunc=RESCHEDULE_TEST, xmlrpcData=xmlrpcData )  
            
    @calling_xmlrpc
    def addDevTime (self, duration, prjId, isTp=False, isTs=False, isTu=False, isTg=False, isTa=False):
        """
        Add development time

        @param duration:
        @type duration:

        @param prjId:
        @type prjId:

        @param isTp:
        @type isTp:

        @param isTs:
        @type isTs:

        @param isTu:
        @type isTu:
        """      
        self.trace('[XMLRPC] calling xmlrpc function')
        xmlrpcData = { 'duration': duration, 'prj-id': prjId, 'user-id': self.userId, 'is-tp': isTp, 'is-ts': isTs,
                        'is-tu': isTu, 'is-tg': isTg, 'is-ta': isTa }
        self.__callXmlrpc( xmlrpcFunc=ADD_DEV_TIME_TEST, xmlrpcData=xmlrpcData )    

    @calling_xmlrpc
    def killTask (self, taskId, taskIds=[]):
        """
        Kill task

        @param taskId: task to kill 
        @type taskId:
        """
        xmlrpcData = { 'taskid': taskId, 'taskids': taskIds  }
        self.__callXmlrpc( xmlrpcFunc=KILL_TASK, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def killAllTasks (self):
        """
        Kill all tasks
        """
        xmlrpcData = { 'killall': True }
        self.__callXmlrpc( xmlrpcFunc=KILL_ALL_TASKS, xmlrpcData=xmlrpcData) 

    @calling_xmlrpc
    def cancelTask (self, taskId, taskIds=[]):
        """
        Cancel task

        @param taskId: task to cancel 
        @type taskId:
        """
        xmlrpcData = { 'taskid': taskId, 'taskids': taskIds }
        self.__callXmlrpc( xmlrpcFunc=CANCEL_TASK, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def cancelAllTasks (self):
        """
        Cancel all tasks
        """
        xmlrpcData = { 'cancelall': True }
        self.__callXmlrpc( xmlrpcFunc=CANCEL_ALL_TASKS, xmlrpcData=xmlrpcData  )
            
    @calling_xmlrpc
    def refreshRepo (self, repo=REPO_TESTS, showPopup=True, project=0, saveAsOnly=False, forRuns=False, partialRefresh=False):
        """
        Refresh repository

        @param showPopup:
        @type showPopup: boolean

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        if repo == REPO_TESTS and project == 0:
            self.trace('no refresh to do for test because project is equal to zero.')
            return
        xmlrpcData = { 'repo-dst': repo , 'projectid': project, 'saveas-only': saveAsOnly, 'for-runs': forRuns, 'partial': partialRefresh }
        self.__callXmlrpc( xmlrpcFunc=REFRESH_REPO, xmlrpcData=xmlrpcData, showPopup=showPopup )

    @calling_xmlrpc
    def setDefaultAdapter(self, packageAdapter):
        """
        Set default adapter
        """
        xmlrpcData = { 'package-name': packageAdapter }
        self.__callXmlrpc( xmlrpcFunc=SET_DEFAULT_ADP, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def setDefaultLibrary(self, packageLibrary):
        """
        Set default library
        """
        xmlrpcData = { 'package-name': packageLibrary }
        self.__callXmlrpc( xmlrpcFunc=SET_DEFAULT_LIB, xmlrpcData=xmlrpcData)

    @calling_xmlrpc
    def setGenericAdapter(self, packageAdapter):
        """
        Set generic adapter
        """
        xmlrpcData = { 'package-name': packageAdapter }
        self.__callXmlrpc( xmlrpcFunc=SET_GENERIC_ADP, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def setGenericLibrary(self, packageLibrary):
        """
        Set generic library
        """
        xmlrpcData = { 'package-name': packageLibrary }
        self.__callXmlrpc( xmlrpcFunc=SET_GENERIC_LIB, xmlrpcData=xmlrpcData)
    
    @calling_xmlrpc    
    def openFileRepo (self, pathFile, repo=REPO_TESTS,  project=0, forceOpen=False, readOnly=False):
        """
        Get file from repository

        @param pathFile:
        @type pathFile:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 
                        'path': pathFile, 'repo-dst': repo, 'projectid': project,
                       'force-open': forceOpen, 'read-only': readOnly
                     }
        self.__callXmlrpc( xmlrpcFunc=OPEN_FILE_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def getFileRepo (self, pathFile, forDest=0, actionId=0, testId=0, project=0, repo=REPO_TESTS):
        """
        Get file from repository

        ACTION_MERGE_PARAMS     = 7
        ACTION_UPDATE_PATH      = 6
        ACTION_IMPORT_OUTPUTS   = 5
        ACTION_IMPORT_INPUTS    = 4
        ACTION_RELOAD_PARAMS    = 3
        ACTION_INSERT_AFTER     = 2
        ACTION_INSERT_BELOW     = 1
        ACTION_ADD              = 0

        FOR_DEST_TP             = 1
        FOR_DEST_TG             = 2
        FOR_DEST_TS             = 3
        FOR_DEST_TU             = 4
        FOR_DEST_ALL            = 10

        @param pathFile:
        @type pathFile:

        @param forTp:
        @type forTp: boolean

        @param forTs:
        @type forTs: boolean

        @param tpId:
        @type tpId:

        @param repo:
        @type repo:

        @param tsInputs:
        @type tsInputs:

        @param project:
        @type project:

        @param forTpInsert:
        @type forTpInsert:

        @param forTg:
        @type forTg:

        @param forTgInsert:
        @type forTgInsert:
        """
        xmlrpcData = { 
                        'path': pathFile, 'for-dest': forDest, 'action-id': actionId, 'test-id': testId,
                        'projectid': project, 'repo-dst': repo
                     }
        self.__callXmlrpc( xmlrpcFunc=GET_FILE_REPO, xmlrpcData=xmlrpcData )
    
    @calling_xmlrpc
    def importFileRepo (self, contentFile, extensionFile, nameFile, pathFile, repo=REPO_TESTS, project=0, makeDirs=False):
        """
        Import file on repository

        @param contentFile:
        @type contentFile:

        @param extensionFile:
        @type extensionFile:

        @param nameFile:
        @type nameFile:

        @param pathFile:
        @type pathFile:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        content_encoded = base64.b64encode(contentFile)
        xmlrpcData = { 'path': pathFile, 'filename': nameFile, 'extension': extensionFile,
                        'content': content_encoded,  'repo-dst': repo, 'projectid': project,
                        'make-dirs': makeDirs }
        self.__callXmlrpc( xmlrpcFunc=IMPORT_FILE_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def unlockFileRepo(self, document, repo=REPO_TESTS, project=0):
        """
        Unlock file
        """
        # nothing to unlock if the repo is undefined
        if repo == REPO_UNDEFINED: return
        
        xmlrpcData = { 'path': document.path, 'filename': document.filename , 'extension': document.extension,
                        'repo-dst': repo, 'projectid': project}
        self.__callXmlrpc( xmlrpcFunc=UNLOCK_FILE_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def putFileRepo (self, document, updateFile=False, repo=REPO_TESTS, project=0, closeTabAfter=False):
        """
        Put file on repository

        @param document:
        @type document:

        @param updateFile:
        @type updateFile: boolean

        @param repo:
        @type repo:

        @param project:
        @type project:

        @param closeTabAfter:
        @type closeTabAfter:
        """
        content_encoded = document.getraw_encoded()
        xmlrpcData = { 'path': document.path, 'filename': document.filename , 'extension': document.extension,
                        'content': content_encoded, 'update': updateFile, 'repo-dst': repo,
                        'projectid': project, 'close': closeTabAfter }
        self.__callXmlrpc( xmlrpcFunc=PUT_FILE_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def addDirRepo (self, pathFolder, folderName, repo=REPO_TESTS, project=0):
        """
        Add folder on repository

        @param pathFolder:
        @type pathFolder:

        @param folderName:
        @type folderName:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'path': str(pathFolder), 'name': str(folderName), 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=ADD_DIR_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def delDirRepo (self, pathFolder, repo=REPO_TESTS, project=0):
        """
        Delete folder on repository

        @param pathFolder:
        @type pathFolder:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'path': str(pathFolder), 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=DEL_DIR_REPO, xmlrpcData=xmlrpcData ) 

    @calling_xmlrpc
    def delDirAllRepo (self, pathFolder, repo=REPO_TESTS, project=0):
        """
        Delete all folders on repository

        @param pathFolder:
        @type pathFolder:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'path': str(pathFolder), 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=DEL_DIR_ALL_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def renameDirRepo (self, mainPath, oldFolder, newFolder, repo=REPO_TESTS, project=0):
        """
        Rename folder on repository

        @param mainPath:
        @type mainPath:

        @param oldFolder:
        @type oldFolder:

        @param newFolder:
        @type newFolder:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'main-path': str(mainPath),'old-path': str(oldFolder), 'new-path': str(newFolder), 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=RENAME_DIR_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def duplicateDirRepo (self, mainPath, oldFolderName, newFolderName, repo=REPO_TESTS, project=0, newProject=0, newPath=''):
        """
        Duplicate folder on repository

        @param mainPath:
        @type mainPath:

        @param oldFolder:
        @type oldFolder:

        @param newFolder:
        @type newFolder:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'main-path': str(mainPath),'old-path': str(oldFolderName), 'new-path': str(newFolderName),
                        'repo-dst': repo, 'projectid': project, 'new-projectid': newProject, 'new-main-path': newPath }
        self.__callXmlrpc( xmlrpcFunc=DUPLICATE_DIR_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def delFileRepo (self, pathFile, repo=REPO_TESTS, project=0):
        """
        Delete file on repository

        @param pathFile:
        @type pathFile:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'path-file': str(pathFile), 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=DEL_FILE_REPO, xmlrpcData=xmlrpcData )    

    @calling_xmlrpc
    def renameFileRepo (self, mainPath, oldFileName, newFileName, extFile, repo=REPO_TESTS, project=0):
        """
        Rename file on repository

        @param mainPath:
        @type mainPath:

        @param oldFileName:
        @type oldFileName:

        @param newFileName:
        @type newFileName:

        @param extFile:
        @type extFile:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = {  'main-path': str(mainPath),'old-filename': str(oldFileName), 'new-filename': str(newFileName),
                    'extension': str(extFile), 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=RENAME_FILE_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def duplicateFileRepo (self, mainPath, oldFileName, newFileName, extFile, repo=REPO_TESTS, project=0, newProject=0, newPath=''):
        """
        Duplicate file on repository

        @param mainPath:
        @type mainPath:

        @param oldFileName:
        @type oldFileName:

        @param newFileName:
        @type newFileName:

        @param extFile:
        @type extFile:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = {  'main-path': str(mainPath),'old-filename': str(oldFileName), 'new-filename': str(newFileName),
                    'extension': str(extFile), 'repo-dst': repo, 'projectid': project, 'new-projectid': newProject, 'new-main-path': newPath }
        self.__callXmlrpc( xmlrpcFunc=DUPLICATE_FILE_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def resetTestsStatistics(self):
        """
        Reset tests statistics
        """
        self.__callXmlrpc( xmlrpcFunc=RESET_TESTS_STATS )

    @calling_xmlrpc
    def emptyRepo(self, repo=REPO_TESTS, project=0):
        """
        Empty repository

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = { 'repo-dst': repo, 'projectid': project }
        self.__callXmlrpc( xmlrpcFunc=EMPTY_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def refreshRepoStats(self, repo=REPO_TESTS, partialRefresh=True, projectId=0):
        """
        Refresh statistics for the repository

        @param repo:
        @type repo:

        @param partialRefresh:
        @type partialRefresh:

        @param projectId:
        @type projectId:
        """
        xmlrpcData = { 'repo-dst': repo, 'partial': partialRefresh , 'projectid':projectId }
        self.__callXmlrpc( xmlrpcFunc=REFRESH_STATS_REPO, xmlrpcData=xmlrpcData )
        
    @calling_xmlrpc
    def refreshStatsServer(self):
        """
        Refresh stats server
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_STATS_SERVER )

    @calling_xmlrpc
    def refreshContextServer(self):
        """
        Refresh stats server
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_CONTEXT_SERVER )

    @calling_xmlrpc
    def createZipArchives (self, mainPathToZip, subPathToZip, projectId=1):
        """
        Create zip archives

        @param mainPathToZip:
        @type mainPathToZip:

        @param subPathToZip:
        @type subPathToZip:
        """
        xmlrpcData = { 'main-path-to-zip': str(mainPathToZip), 'sub-path-to-zip': str(subPathToZip) , 'project-id': projectId }
        self.__callXmlrpc( xmlrpcFunc=ZIP_REPO_ARCHIVES, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def stopAgent (self, agentName):
        """
        Stop agent

        @param agentName:
        @type agentName:
        """
        xmlrpcData = { 'name': agentName }
        self.__callXmlrpc( xmlrpcFunc=STOP_AGENT, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def startAgent (self, agentType, agentName, agentDescription, agentAutoStart):
        """
        Start agent

        @param agentType:
        @type agentType:

        @param agentName:
        @type agentName:

        @param agentDescription:
        @type agentDescription:

        @param agentAutoStart:
        @type agentAutoStart:
        """
        xmlrpcData = { 'name': agentName, 'type': agentType, 'description': agentDescription, 'make-default': agentAutoStart }
        self.__callXmlrpc( xmlrpcFunc=START_AGENT, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def addAgent (self,agentType, agentName, agentDescription):
        """
        Add default agent

        @param agentType:
        @type agentType:

        @param agentName:
        @type agentName:

        @param agentDescription:
        @type agentDescription:

        @param agentAutoStart:
        @type agentAutoStart:
        """
        xmlrpcData = { 'name': agentName, 'type': agentType, 'description': agentDescription }
        self.__callXmlrpc( xmlrpcFunc=ADD_AGENT, xmlrpcData=xmlrpcData )
            
    @calling_xmlrpc
    def delAgent (self, agentName):
        """
        Delete default agent 

        @param agentName:
        @type agentName:
        """
        xmlrpcData = { 'name': agentName }
        self.__callXmlrpc( xmlrpcFunc=DEL_AGENT, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def refreshRunningAgents(self):
        """
        Refresh running agents list 
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_RUNNING_AGENTS )

    @calling_xmlrpc
    def refreshDefaultAgents(self):
        """
        Refresh default agents list 
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_DEFAULT_AGENTS )
            
    @calling_xmlrpc
    def stopProbe (self, probeName):
        """
        Stop probe

        @param probeName:
        @type probeName:
        """
        xmlrpcData = { 'name': probeName }
        self.__callXmlrpc( xmlrpcFunc=STOP_PROBE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def startProbe (self, probeType, probeName, probeDescription, probeAutoStart):
        """
        Start probe

        @param probeType:
        @type probeType:

        @param probeName:
        @type probeName:

        @param probeDescription:
        @type probeDescription:

        @param probeAutoStart:
        @type probeAutoStart:
        """
        xmlrpcData = { 'name': probeName, 'type': probeType, 'description': probeDescription, 'make-default': probeAutoStart }
        self.__callXmlrpc( xmlrpcFunc=START_PROBE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def addProbe (self, probeType, probeName, probeDescription):
        """
        Add default probe

        @param probeType:
        @type probeType:

        @param probeName:
        @type probeName:

        @param probeDescription:
        @type probeDescription:
        """
        xmlrpcData = { 'name': probeName, 'type': probeType, 'description': probeDescription }
        self.__callXmlrpc( xmlrpcFunc=ADD_PROBE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def delProbe (self, probeName):
        """
        Delete default probe 

        @param probeName:
        @type probeName:
        """
        xmlrpcData = { 'name': probeName }
        self.__callXmlrpc( xmlrpcFunc=DEL_PROBE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def refreshRunningProbes(self):
        """
        Refresh running probes list 
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_RUNNING_PROBES )

    @calling_xmlrpc
    def refreshDefaultProbes(self):
        """
        Refresh default probes list 
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_DEFAULT_PROBES )

    @calling_xmlrpc
    def genCacheHelp(self):
        """
        Empty archives
        """
        self.__callXmlrpc( xmlrpcFunc=GEN_CACHE_HELP )

    @calling_xmlrpc
    def prepareAssistant(self):
        """
        Prepare assistant
        """
        self.__callXmlrpc( xmlrpcFunc=PREPARE_ASSISTANT )

    @calling_xmlrpc
    def clearTasksHistory(self):
        """
        Clear tasks history
        """
        self.__callXmlrpc( xmlrpcFunc=DEL_TASKS_HISTORY )

    @calling_xmlrpc
    def addCommentArchive(self, archiveFile, archivePost, postTimestamp, testId=0):
        """
        Add comment on archive

        @param archiveFile:
        @type archiveFile:

        @param archivePost:
        @type archivePost:

        @param postTimestamp:
        @type postTimestamp:

        @param testId:
        @type testId:
        """
        xmlrpcData = { 'file': archiveFile, 'post': archivePost, 'timestamp': postTimestamp,
                        'testid': testId }
        self.__callXmlrpc( xmlrpcFunc=ADD_COMMENT_ARCHIVE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def exportTestDesign(self, testId=0, testPath=None, testFileName=None, projectId=1):
        """
        Export test design

        @param testId:
        @type testId:

        @param testPath:
        @type testPath:

        @param testFileName:
        @type testFileName:
        """
        xmlrpcData = { 'testid': testId, 'project-id': projectId }
        if testPath is not None:
            xmlrpcData['testpath'] = testPath
        if testFileName is not None:
            xmlrpcData['testfilename'] = testFileName
        self.__callXmlrpc( xmlrpcFunc=EXPORT_TESTRESULT_DESIGN, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def exportTestVerdict(self, testId=0, testPath=None, testFileName=None, projectId=1):
        """
        Export test verdict

        @param testId:
        @type testId:

        @param testPath:
        @type testPath:

        @param testFileName:
        @type testFileName:
        """
        xmlrpcData = { 'testid': testId , 'project-id': projectId }
        if testPath is not None:
            xmlrpcData['testpath'] = testPath
        if testFileName is not None:
            xmlrpcData['testfilename'] = testFileName
        self.__callXmlrpc( xmlrpcFunc=EXPORT_TESTRESULT_VERDICT, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def exportTestReport(self, testId=0, testPath=None, testFileName=None, projectId=1):
        """
        Export test report

        @param testId:
        @type testId:

        @param testPath:
        @type testPath:

        @param testFileName:
        @type testFileName:
        """
        xmlrpcData = { 'testid': testId , 'project-id': projectId }
        if testPath is not None:
            xmlrpcData['testpath'] = testPath
        if testFileName is not None:
            xmlrpcData['testfilename'] = testFileName
        self.__callXmlrpc( xmlrpcFunc=EXPORT_TESTRESULT_REPORT, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def readCommentsArchive(self, archiveFile):
        """
        Read comments from archive

        @param archiveFile:
        @type archiveFile:
        """
        xmlrpcData = { 'file': archiveFile }
        self.__callXmlrpc( xmlrpcFunc=LOAD_COMMENTS_ARCHIVE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def delCommentsArchive(self, archiveFile):
        """
        Delete comments on archives

        @param archiveFile:
        @type archiveFile:
        """
        xmlrpcData = { 'file': archiveFile }
        self.__callXmlrpc( xmlrpcFunc=DEL_COMMENTS_ARCHIVE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def backupRepo(self, backupName, repo=REPO_TESTS):
        """
        Backup repository

        @param backupName:
        @type backupName:

        @param repo:
        @type repo:
        """
        xmlrpcData = { 'backup-name': backupName, 'repo-dst': repo}
        self.__callXmlrpc( xmlrpcFunc=BACKUP_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def deleteBackupsRepo(self, repo=REPO_TESTS):
        """
        Delete backups on repository

        @param repo:
        @type repo:
        """
        xmlrpcData = { 'repo-dst': repo }
        self.__callXmlrpc( xmlrpcFunc=DELETE_BACKUPS_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def refreshRunningTasks(self):
        """
        Refresh running tasks
        """
        xmlrpcData = { 'task-type': TASKS_RUNNING }
        self.__callXmlrpc( xmlrpcFunc=REFRESH_TASKS, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def refreshWaitingTasks(self):
        """
        Refresh waiting tasks
        """
        xmlrpcData = { 'task-type': TASKS_WAITING }
        self.__callXmlrpc( xmlrpcFunc=REFRESH_TASKS, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def refreshHistoryTasks(self, Full=True):
        """
        Refresh history tasks

        @param Full:
        @type Full:
        """
        xmlrpcData = { 'task-type': TASKS_HISTORY }
        xmlrpcData['full'] = Full
        self.__callXmlrpc( xmlrpcFunc=REFRESH_TASKS, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def addAdapterRepo(self, pathFolder, adapterName, mainAdapters=False):
        """
        Add a new adapter in the repository

        @param pathFolder:
        @type pathFolder:

        @param adapterName:
        @type adapterName:

        @param mainAdapters:
        @type mainAdapters:
        """
        xmlrpcData = { 'path': str(pathFolder), 'name': str(adapterName), 'main-adapters': mainAdapters }
        self.__callXmlrpc( xmlrpcFunc=ADD_ADAPTER_REPO, xmlrpcData=xmlrpcData )
            
    @calling_xmlrpc
    def addLibraryRepo(self, pathFolder, libraryName, mainLibraries=False):
        """
        Add a new library in the repository

        @param pathFolder:
        @type pathFolder:

        @param libraryName:
        @type libraryName:

        @param mainLibraries:
        @type mainLibraries:
        """
        xmlrpcData = { 'path': str(pathFolder), 'name': str(libraryName), 'main-libraries': mainLibraries}
        self.__callXmlrpc( xmlrpcFunc=ADD_LIBRARY_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def reloadHelper(self):
        """
        Refresh helper
        """
        self.__callXmlrpc( xmlrpcFunc=REFRESH_HELPER )

    @calling_xmlrpc
    def moveFileRepo (self, mainPath, FileName, extFile, newPath, repo=REPO_TESTS, project=0, newProject=0):
        """
        Move file on repository

        @param mainPath:
        @type mainPath:

        @param FileName:
        @type FileName:

        @param extFile:
        @type extFile:

        @param newPath:
        @type newPath:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = {  'main-path': str(mainPath),'filename': str(FileName), 'new-path': str(newPath),
                    'extension': str(extFile), 'repo-dst': repo, 'projectid': project, 'new-projectid': newProject}
        self.__callXmlrpc( xmlrpcFunc=MOVE_FILE_REPO, xmlrpcData=xmlrpcData )
    
    @calling_xmlrpc
    def moveFolderRepo (self, mainPath, FolderName, newPath, repo=REPO_TESTS, project=0, newProject=0):
        """
        Move folder on repository

        @param mainPath:
        @type mainPath:

        @param FileName:
        @type FileName:

        @param extFile:
        @type extFile:

        @param newPath:
        @type newPath:

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        xmlrpcData = {  'main-path': str(mainPath),'folder-name': str(FolderName), 'new-path': str(newPath),
                             'repo-dst': repo, 'projectid': project, 'new-projectid': newProject }
        self.__callXmlrpc( xmlrpcFunc=MOVE_FOLDER_REPO, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def loadTestCache (self, mainPath, subPath, project=1):
        """
        Load test cache

        @param mainPath:
        @type mainPath:

        @param subPath:
        @type subPath:
        """
        xmlrpcData = { 'main-path': str(mainPath), 'sub-path': str(subPath), 'project-id': project  }
        self.__callXmlrpc( xmlrpcFunc=LOAD_TEST_CACHE, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def generateLibraries(self):
        """
        Generate packages
        """
        self.__callXmlrpc( xmlrpcFunc=GEN_LIBRARIES )

    @calling_xmlrpc
    def generateAdapters(self):
        """
        Generate packages
        """
        self.__callXmlrpc( xmlrpcFunc=GEN_ADAPTERS )

    @calling_xmlrpc
    def generateSamples(self):
        """
        Generate samples
        """
        self.__callXmlrpc( xmlrpcFunc=GEN_SAMPLES)

    @calling_xmlrpc
    def generateAll(self):
        """
        Generate all
        """
        self.__callXmlrpc( xmlrpcFunc=GEN_ALL)
    
    @calling_xmlrpc
    def cleanupLockFiles(self, tests=True, adapters=False, libraries=False):
        """
        Generate packages
        """
        xmlrpcData = { 'cleanup-tests': tests, 'cleanup-adapters': adapters, 'cleanup-libraries': libraries}
        self.__callXmlrpc( xmlrpcFunc=CLEANUP_LOCK_FILES_REPO, xmlrpcData=xmlrpcData )
    
    @calling_xmlrpc
    def restoreSnapshot(self, snapshotName, snapshotPath, projectId):
        """
        Restore snapshot
        """
        xmlrpcData = {
                        'snapshot-name': snapshotName,
                        'snapshot-path': snapshotPath,
                        'test-prjid': projectId
                    }
        self.__callXmlrpc( xmlrpcFunc=RESTORE_SNAPSHOT_TEST, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def deleteSnapshot(self, snapshotName, snapshotPath, projectId):
        """
        Delete snapshot
        """
        xmlrpcData = {
                        'snapshot-name': snapshotName,
                        'snapshot-path': snapshotPath,
                        'test-prjid': projectId
                    }
        self.__callXmlrpc( xmlrpcFunc=DELETE_SNAPSHOT_TEST, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def deleteAllSnapshots(self, path, filename, extension, projectId):
        """
        Generate packages
        """
        xmlrpcData = {
                        'test-path': path,
                        'test-name': filename,
                        'test-ext': extension,
                        'test-prjid': projectId
                    }
        self.__callXmlrpc( xmlrpcFunc=DELETE_ALL_SNAPSHOTS_TEST, xmlrpcData=xmlrpcData )
    
    @calling_xmlrpc
    def createSnapshot(self, path, filename, extension, projectId, snapshotName, snapshotTimestamp):
        """
        Generate packages
        """
        xmlrpcData = {
                        'snapshot-name': snapshotName,
                        'snapshot-timestamp': snapshotTimestamp,
                        'test-path': path,
                        'test-name': filename,
                        'test-ext': extension,
                        'test-prjid': projectId
                    }
        self.__callXmlrpc( xmlrpcFunc=CREATE_SNAPSHOT_TEST, xmlrpcData=xmlrpcData )
            
    @calling_xmlrpc
    def downloadResultLogsV2(self, trPath, trName, projectId=1, andSave=False, destFile=''):
        """
        Download test result v2
        """
        if sys.version_info > (3,): # python 3 support
            encodedDest = base64.b64encode(bytes(destFile, "utf8") )
        else:
            encodedDest = base64.b64encode( destFile.encode("utf8")  )
        xmlrpcData = { 'projectid': projectId, 'tr-path':trPath, 'tr-name': trName,
                        'and-save': andSave, 'to-file': encodedDest }
        self.__callXmlrpc( xmlrpcFunc=DOWNLOAD_TESTRESULT, xmlrpcData=xmlrpcData )
    
    @calling_xmlrpc
    def downloadBackupV2(self, fromRepo, backupFileName, destFileName):
        """
        Download backup v2
        """
        if sys.version_info > (3,): # python 3 support
            encodedDest = base64.b64encode(bytes(destFileName, "utf8") )
        else:
            encodedDest = base64.b64encode( destFileName.encode("utf8")  )
        xmlrpcData = { 'from-repo': fromRepo, 'backup-filename':backupFileName, 'to-file': encodedDest}
        self.__callXmlrpc( xmlrpcFunc=DOWNLOAD_BACKUP, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def downloadClientV2(self, packageName):
        """
        Download client v2
        """
        xmlrpcData = { 'package-name': packageName, 'os': sys.platform }
        self.__callXmlrpc( xmlrpcFunc=DOWNLOAD_CLIENT, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def generateAdapterFromWSDL(self, wsdlUrl, wsdlFile, pkg, overwrite=False):
        """
        Download client v2
        """
        xmlrpcData = { 'wsdl-url': wsdlUrl, 'wsdl-file': xmlrpclib.Binary(wsdlFile), 'pkg': pkg,
                        'overwrite': overwrite}
        self.__callXmlrpc( xmlrpcFunc=GENERATE_ADAPTER_WSDL, xmlrpcData=xmlrpcData )
    
    @calling_xmlrpc
    def setTestsWithDefaultVersion(self):
        """
        Set all tests with default version for adapters and libraries
        """
        self.__callXmlrpc( xmlrpcFunc=SET_DEFAULT_TESTS_VERSION )
    
    @calling_xmlrpc
    def getImagePreview(self, trPath, imageName, projectId=0):
        """
        Get image privew
        """
        xmlrpcData = { 'projectid': projectId, 'tr-path':trPath, 'image-name': imageName }
        self.__callXmlrpc( xmlrpcFunc=GET_IMAGE_PREVIEW, xmlrpcData=xmlrpcData )

    # @calling_xmlrpc        
    # def getTestPreview(self, trPath, trName, projectId=0):
        # """
        # Get test privew
        # """
        # xmlrpcData = { 'projectid': projectId, 'tr-path':trPath, 'tr-name': trName }
        # self.__callXmlrpc( xmlrpcFunc=GET_TEST_PREVIEW, xmlrpcData=xmlrpcData )

    @calling_xmlrpc
    def deleteTestResult(self, trPath,  projectId=0):
        """
        Delete test result
        """
        xmlrpcData = { 'projectid': projectId, 'tr-path':trPath}
        self.__callXmlrpc( xmlrpcFunc=DELETE_TEST_RESULT, xmlrpcData=xmlrpcData )

UCI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return UCI

def initialize (parent, clientVersion):
    """
    Initialize the class UserClientInterface

    @param parent:
    @type: parent:

    @param clientVersion:
    @type: clientVersion:
    """
    global UCI
    UCI = UserClientInterface(parent, clientVersion)

def finalize ():
    """
    Destroy Singleton
    """
    global UCI
    if UCI:
        del UCI
        UCI = None