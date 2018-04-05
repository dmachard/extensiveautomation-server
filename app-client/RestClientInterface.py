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

"""
Api client interface
"""
import sys
import json
import base64
import subprocess
import copy

try:
    from PyQt4.QtGui import (QDialog)
    from PyQt4.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)
except ImportError:
    from PyQt5.QtWidgets import (QDialog)
    from PyQt5.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)

from Libs import QtHelper, Logger
import ServerExplorer
import Settings
import TestResults

import Workspace.FileModels.TestData as FileModelTestData
import Workspace.FileModels.TestSuite as FileModelTestSuite
import Workspace.FileModels.TestUnit as FileModelTestUnit
import Workspace.FileModels.TestAbstract as FileModelTestAbstract
import Workspace.FileModels.TestPlan as FileModelTestPlan

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
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

CODE_ERROR                  = 500
CODE_DISABLED               = 405
CODE_ALLREADY_EXISTS        = 420
CODE_NOT_FOUND              = 404
CODE_LOCKED                 = 421
CODE_ALLREADY_CONNECTED     = 416
CODE_FORBIDDEN              = 403
CODE_FAILED                 = 400
CODE_OK                     = 200

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
                    
RIGHTS_ADMIN                =   "Administrator"
RIGHTS_DEVELOPER            =   "Developer"
RIGHTS_LEADER               =   "Leader"
RIGHTS_TESTER               =   "Tester"

RIGHTS_USER_LIST            =  [ 
                                    RIGHTS_ADMIN, 
                                    RIGHTS_LEADER,
                                    RIGHTS_TESTER,
                                    RIGHTS_DEVELOPER
                                ]


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

# type of http request
HTTP_POST   =   "POST"
HTTP_GET    =   "GET"

# all rest uri called
CMD_LOGIN                       =   "/session/login"
CMD_LOGOUT                      =   "/session/logout"
CMD_REFRESH                     =   "/session/refresh"
CMD_CONTEXT                     =   "/session/context"
CMD_CONTEXT_ALL                 =   "/session/context/all"

CMD_AGENTS_RUNNING              =   "/agents/running"
CMD_AGENTS_DEFAULT              =   "/agents/default"
CMD_AGENTS_DISCONNECT           =   "/agents/disconnect"
CMD_AGENTS_CONNECT              =   "/agents/connect"
CMD_AGENTS_ADD                  =   "/agents/add"
CMD_AGENTS_REMOVE               =   "/agents/remove"

CMD_PROBES_RUNNING              =   "/probes/running"
CMD_PROBES_DEFAULT              =   "/probes/default"
CMD_PROBES_DISCONNECT           =   "/probes/disconnect"
CMD_PROBES_CONNECT              =   "/probes/connect"
CMD_PROBES_ADD                  =   "/probes/add"
CMD_PROBES_REMOVE               =   "/probes/remove"

CMD_TESTS_UNLOCK_ALL            =   "/tests/file/unlock/all"
CMD_TESTS_BUILD                 =   "/tests/build/samples"
CMD_TESTS_BACKUP                =   "/tests/backup"
CMD_TESTS_BACKUP_REMOVE_ALL     =   "/tests/backup/remove/all"
CMD_TESTS_BACKUP_DOWNLOAD       =   "/tests/backup/download"
CMD_TESTS_RESET                 =   "/tests/reset"
CMD_TESTS_CHECK_SYNTAX          =   "/tests/check/syntax"
CMD_TESTS_CHECK_SYNTAX_TPG      =   "/tests/check/syntax/tpg"
CMD_TESTS_CREATE_DESIGN         =   "/tests/create/design"
CMD_TESTS_CREATE_DESIGN_TPG     =   "/tests/create/design/tpg"
CMD_TESTS_STATISTICS            =   "/tests/statistics"
CMD_TESTS_FILE_MOVE             =   "/tests/file/move"
CMD_TESTS_FOLDER_MOVE           =   "/tests/directory/move"
CMD_TESTS_LISTING               =   "/tests/listing"
CMD_TESTS_FILE_RENAME           =   "/tests/file/rename"
CMD_TESTS_FOLDER_RENAME         =   "/tests/directory/rename"
CMD_TESTS_FILE_DUPLICATE        =   "/tests/file/duplicate"
CMD_TESTS_FOLDER_DUPLICATE      =   "/tests/directory/duplicate"
CMD_TESTS_FILE_REMOVE           =   "/tests/file/remove"
CMD_TESTS_FOLDER_REMOVE         =   "/tests/directory/remove"
CMD_TESTS_FOLDER_REMOVE_ALL     =   "/tests/directory/remove/all"
CMD_TESTS_FOLDER_ADD            =   "/tests/directory/add"
CMD_TESTS_SNAPSHOT_ADD          =   "/tests/snapshot/add"
CMD_TESTS_SNAPSHOT_REMOVE       =   "/tests/snapshot/remove"
CMD_TESTS_SNAPSHOT_REMOVE_ALL   =   "/tests/snapshot/remove/all"
CMD_TESTS_SNAPSHOT_RESTORE      =   "/tests/snapshot/restore"
CMD_TESTS_FILE_UNLOCK           =   "/tests/file/unlock"
CMD_TESTS_FILE_OPEN             =   "/tests/file/open"
CMD_TESTS_FILE_UPLOAD           =   "/tests/file/upload"
CMD_TESTS_DEFAULT_VERSION       =   "/tests/default/all"
CMD_TESTS_SCHEDULE              =   "/tests/schedule"
CMD_TESTS_SCHEDULE_TPG          =   "/tests/schedule/tpg"
CMD_TESTS_SCHEDULE_GROUP        =   "/tests/schedule/group"

CMD_LIBRARIES_UNLOCK_ALL        =   "/libraries/file/unlock/all"
CMD_LIBRARIES_BUILD             =   "/libraries/build"
CMD_LIBRARIES_SYNTAX_ALL        =   "/libraries/check/syntax/all"
CMD_LIBRARIES_SYNTAX            =   "/libraries/check/syntax"
CMD_LIBRARIES_PACKAGE_ADD       =   "/libraries/package/add"
CMD_LIBRARIES_LIB_ADD           =   "/libraries/library/add"
CMD_LIBRARIES_DEFAULT           =   "/libraries/package/default"
CMD_LIBRARIES_GENERIC           =   "/libraries/package/generic"
CMD_LIBRARIES_BACKUP            =   "/libraries/backup"
CMD_LIBRARIES_BACKUP_REMOVE_ALL =   "/libraries/backup/remove/all"
CMD_LIBRARIES_BACKUP_DOWNLOAD   =   "/libraries/backup/download"
CMD_LIBRARIES_RESET             =   "/libraries/reset"
CMD_LIBRARIES_STATISTICS        =   "/libraries/statistics"
CMD_LIBRARIES_LISTING           =   "/libraries/listing"
CMD_LIBRARIES_FILE_MOVE         =   "/libraries/file/move"
CMD_LIBRARIES_FOLDER_MOVE       =   "/libraries/directory/move"
CMD_LIBRARIES_FILE_RENAME       =   "/libraries/file/rename"
CMD_LIBRARIES_FOLDER_RENAME     =   "/libraries/directory/rename"
CMD_LIBRARIES_FILE_DUPLICATE    =   "/libraries/file/duplicate"
CMD_LIBRARIES_FOLDER_DUPLICATE  =   "/libraries/directory/duplicate"
CMD_LIBRARIES_FILE_REMOVE       =   "/libraries/file/remove"
CMD_LIBRARIES_FOLDER_REMOVE     =   "/libraries/directory/remove"
CMD_LIBRARIES_FOLDER_REMOVE_ALL =   "/libraries/directory/remove/all"
CMD_LIBRARIES_FOLDER_ADD        =   "/libraries/directory/add"
CMD_LIBRARIES_FILE_UNLOCK       =   "/libraries/file/unlock"
CMD_LIBRARIES_FILE_OPEN         =   "/libraries/file/open"
CMD_LIBRARIES_FILE_UPLOAD       =   "/libraries/file/upload"

CMD_ADAPTERS_UNLOCK_ALL         =   "/adapters/file/unlock/all"
CMD_ADAPTERS_BUILD              =   "/adapters/build"
CMD_ADAPTERS_SYNTAX_ALL         =   "/adapters/check/syntax/all"
CMD_ADAPTERS_SYNTAX             =   "/adapters/check/syntax"
CMD_ADAPTERS_PACKAGE_ADD        =   "/adapters/package/add"
CMD_ADAPTERS_ADP_ADD            =   "/adapters/adapter/add"
CMD_ADAPTERS_ADP_ADD_WSDL_URL   =   "/adapters/adapter/add/by/wsdl/url"
CMD_ADAPTERS_ADP_ADD_WSDL_FILE  =   "/adapters/adapter/add/by/wsdl/file"
CMD_ADAPTERS_DEFAULT            =   "/adapters/package/default"
CMD_ADAPTERS_GENERIC            =   "/adapters/package/generic"
CMD_ADAPTERS_BACKUP             =   "/adapters/backup"
CMD_ADAPTERS_BACKUP_REMOVE_ALL  =   "/adapters/backup/remove/all"
CMD_ADAPTERS_BACKUP_DOWNLOAD    =   "/adapters/backup/download"
CMD_ADAPTERS_RESET              =   "/adapters/reset"
CMD_ADAPTERS_STATISTICS         =   "/adapters/statistics"
CMD_ADAPTERS_LISTING            =   "/adapters/listing"
CMD_ADAPTERS_FILE_MOVE          =   "/adapters/file/move"
CMD_ADAPTERS_FOLDER_MOVE        =   "/adapters/directory/move"
CMD_ADAPTERS_FILE_RENAME        =   "/adapters/file/rename"
CMD_ADAPTERS_FOLDER_RENAME      =   "/adapters/directory/rename"
CMD_ADAPTERS_FILE_DUPLICATE     =   "/adapters/file/duplicate"
CMD_ADAPTERS_FOLDER_DUPLICATE   =   "/adapters/directory/duplicate"
CMD_ADAPTERS_FILE_REMOVE        =   "/adapters/file/remove"
CMD_ADAPTERS_FOLDER_REMOVE      =   "/adapters/directory/remove"
CMD_ADAPTERS_FOLDER_REMOVE_ALL  =   "/adapters/directory/remove/all"
CMD_ADAPTERS_FOLDER_ADD         =   "/adapters/directory/add"
CMD_ADAPTERS_FILE_UNLOCK        =   "/adapters/file/unlock"
CMD_ADAPTERS_FILE_OPEN          =   "/adapters/file/open"
CMD_ADAPTERS_FILE_UPLOAD        =   "/adapters/file/upload"

CMD_DOCS_BUILD                  =   "/documentations/build"
CMD_DOCS_CACHE                  =   "/documentations/cache"

CMD_CLIENTS_AVAILABLE           =   "/clients/available"
CMD_CLIENTS_DOWNLOAD            =   "/clients/download"

CMD_SYSTEM_USAGES               =   "/system/usages"

CMD_METRICS_RESET               =   "/metrics/tests/reset"
CMD_METRICS_WRITING_DURATION    =   "/metrics/tests/duration/writing"

CMD_TASKS_REPLAY                =   "/tasks/replay"
CMD_TASKS_VERDICT               =   "/tasks/verdict"
CMD_TASKS_DESIGN                =   "/tasks/design"
CMD_TASKS_REVIEW                =   "/tasks/review"
CMD_TASKS_COMMENT               =   "/tasks/comment"
CMD_TASKS_KILL                  =   "/tasks/kill"
CMD_TASKS_KILL_ALL              =   "/tasks/kill/all"
CMD_TASKS_KILL_SELECTIVE        =   "/tasks/kill/selective"
CMD_TASKS_CANCEL                =   "/tasks/cancel"
CMD_TASKS_CANCEL_ALL            =   "/tasks/cancel/all"
CMD_TASKS_CANCEL_SELECTIVE      =   "/tasks/cancel/selective"
CMD_TASKS_WAITING               =   "/tasks/waiting"
CMD_TASKS_RUNNING               =   "/tasks/running"
CMD_TASKS_HISTORY               =   "/tasks/history"
CMD_TASKS_HISTORY_ALL           =   "/tasks/history/all"
CMD_TASKS_HISTORY_CLEAR         =   "/tasks/history/clear"
CMD_TASKS_SCHEDULE              =   "/tasks/reschedule"

CMD_TR_GET_DESIGNS              =   "/results/report/designs"
CMD_TR_GET_REVIEWS              =   "/results/report/reviews"
CMD_TR_GET_VERDICTS             =   "/results/report/verdicts"
CMD_TR_DEL_COMMENTS             =   "/results/comments/remove"
CMD_TR_ADD_COMMENT              =   "/results/comment/add"
CMD_TR_ZIP                      =   "/results/compress/zip"
CMD_TR_DOWNLOAD                 =   "/results/download/result"
CMD_TR_UNCOMPLETE               =   "/results/download/uncomplete"
CMD_TR_LISTING                  =   "/results/listing/files"
CMD_TR_GET_REPORTS              =   "/results/reports"
CMD_TR_GET_IMAGE                =   "/results/download/image"
CMD_TR_REMOVE                   =   "/results/reset"
CMD_TR_DELETE                   =   "/results/remove/by/id"
CMD_TR_DELETE_BY_DATE           =   "/results/remove/by/date"
CMD_TR_BACKUP                   =   "/results/backup"
CMD_TR_BACKUP_REMOVE_ALL        =   "/results/backup/remove/all"
CMD_TR_BACKUP_DOWNLOAD          =   "/results/backup/download"
CMD_TR_STATISTICS               =   "/results/statistics"

def calling_rest(func):
    """
    Decorator for rest call
    """
    def wrapper(*args, **kwargs):
        """
        just a wrapper
        """
        funcname = func.__name__
        parent = args[0]
        try:
            parent.trace("calling rest %s" % funcname)
            func(*args, **kwargs)
            parent.trace("ending rest %s, waiting response" % funcname)
        except Exception as e:
            parent.onGenericError( title="Request error (%s)" % funcname, err=str(e) )
    return wrapper
    
class RestClientInterface(QObject, Logger.ClassLogger):
    """
    Rest client interface
    """
    CloseConnection = pyqtSignal()
    CriticalMsg = pyqtSignal(str, str)  
    WarningMsg = pyqtSignal(str, str)  
    InformationMsg = pyqtSignal(str, str)  
    WebCall = pyqtSignal(str, str, str)
    IdleCursor = pyqtSignal() 
    BusyCursor = pyqtSignal()
    Authenticated = pyqtSignal()
    # new in v18
    GetTrReports = pyqtSignal(dict)
    GetTrImage = pyqtSignal(str)
    RefreshResults = pyqtSignal(list)
    OpenTestResult = pyqtSignal(tuple)
    CommentTrAdded = pyqtSignal(list)
    CommentsTrDeleted = pyqtSignal()
    GetTrReviews = pyqtSignal(str, str)
    GetTrDesigns = pyqtSignal(str, str)
    GetTrVerdicts = pyqtSignal(str, str)
    ResetStatistics = pyqtSignal()
    RefreshContext = pyqtSignal(list)
    RefreshUsages = pyqtSignal(dict)
    TasksWaiting = pyqtSignal(list)
    TasksRunning = pyqtSignal(list)
    TasksHistory = pyqtSignal(list)
    TasksHistoryCleared = pyqtSignal()
    TestRescheduled = pyqtSignal()
    TestCancelled = pyqtSignal()
    TestKilled = pyqtSignal(int)
    TestsKilled = pyqtSignal()
    RefreshRunningProbes = pyqtSignal(list)
    RefreshRunningAgents = pyqtSignal(list)
    RefreshHelper = pyqtSignal(dict)
    RefreshStatsResults = pyqtSignal(dict)
    RefreshStatsLibraries = pyqtSignal(dict)
    RefreshStatsAdapters = pyqtSignal(dict)
    RefreshStatsTests = pyqtSignal(dict)
    RefreshDefaultAgents = pyqtSignal(list)
    RefreshDefaultProbes = pyqtSignal(list)
    Connected = pyqtSignal(dict)
    RefreshTestsRepo = pyqtSignal(list, int, bool, bool)
    RefreshAdaptersRepo = pyqtSignal(list)
    RefreshLibrariesRepo = pyqtSignal(list)
    FolderTestsRenamed = pyqtSignal(int, str, str, str)
    FolderAdaptersRenamed = pyqtSignal(str, str, str)
    FolderLibrariesRenamed = pyqtSignal(str, str, str)
    FileTestsRenamed = pyqtSignal(int, str, str, str, str)
    FileAdaptersRenamed = pyqtSignal(str, str, str, str)
    FileLibrariesRenamed = pyqtSignal(str, str, str, str)
    OpenTestFile = pyqtSignal(str, str, str, str, int, bool, str)
    OpenAdapterFile = pyqtSignal(str, str, str, str, bool, str)
    OpenLibraryFile = pyqtSignal(str, str, str, str, bool, str)
    FileTestsUploaded = pyqtSignal(str, str, str, int, bool, bool)
    FileAdaptersUploaded = pyqtSignal(str, str, str, bool, bool)
    FileLibrariesUploaded = pyqtSignal(str, str, str, bool, bool)
    FileTestsUploadError = pyqtSignal(str, str, str, int, bool, bool)
    FileAdaptersUploadError = pyqtSignal(str, str, str, bool, bool)
    FileLibrariesUploadError = pyqtSignal(str, str, str, bool, bool)
    GetFileRepo = pyqtSignal(str, str, str, str, int, int, int, int)
    AddTestTab = pyqtSignal(object)
    def __init__(self, parent, clientVersion):
        """
        Constructor
        """
        QObject.__init__(self, parent)
        
        self.__parent = parent
        self.__sessionId = None
        self.__expires = 0
        self.__login = ""

        self.clientVersion = clientVersion
        self.authenticated = False
        self.userRights = []
        self.userId = 0

        self.refreshTimer = QTimer()
        self.refreshTimer.timeout.connect(self.refresh)

        self.updateDialog = QtHelper.MessageBoxDialog(dialogName = '')
        self.updateDialog.Download.connect(self.onUpdateClientClicked)

        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.checkClientUpdateAuto)

    def isAuthenticated (self):
        """
        Is authenticated ?

        @return:
        @rtype:
        """
        return self.authenticated
        
    def application(self):
        """
        return main application instance
        """
        return self.__parent

    def makeRequest(self, uri, request, _json={}):
        """
        Make rest request
        """
        self.trace('REST function called %s' % uri)
        try:
            body = ''
            if len(_json): body = json.dumps(_json)
        except Exception as e:
            self.CriticalMsg.emit( "Critical Error", "Bad json encode: %s" % e)
        else:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/rest-support' ) ):
                self.WebCall.emit(uri, request, body)
            else:
                self.WarningMsg.emit( self.tr("The REST API interface disabled") )
            
    def onGenericError(self, err, title="Rest Error"):
        """
        Called on rest generic error

        @param err: 
        @type err:

        @param title: 
        @type title:
        """
        self.error( "%s: %s" % (title,err) )
        ServerExplorer.instance().stopWorking()
        
        self.CriticalMsg.emit( title, err)
            
    def onAuthenticationFailed(self, err, title="Error"):
        """
        Called on rest authentication error

        @param err: 
        @type err:

        @param title: 
        @type title:
        """
        self.error( "%s: %s" % (title,err) )
        ServerExplorer.instance().stopWorking()
        self.CloseConnection.emit()
        
        auth_error = "%s\n\n%s\n%s" % ( 
                                        self.tr(err), 
                                        self.tr("Please to retry with valid credentials"),
                                        self.tr("If the problem persists contact your administrator.")
                                      )
        self.WarningMsg.emit( title, auth_error)
        
    def onGenericResponse(self, response):
        """
        Rest callback

        @param value: 
        @type value: 
        """
        self.IdleCursor.emit()
        
        # some important checks before to read the response
        if 'cmd' not in response:
            self.onGenericError(err=self.tr("Bad json response, cmd is missing: %s" % response), 
                                title=self.tr("Bad message") )
        else:
            if response['cmd'] == CMD_LOGIN:
                self.onLogin(details=response)
            elif response['cmd'] == CMD_LOGOUT:
                self.onLogout(details=response)
            elif response['cmd'] == CMD_REFRESH:
                self.onRefresh(details=response)
            elif response['cmd'] == CMD_CONTEXT:
                self.onSessionContext(details=response)
            elif response['cmd'] == CMD_CONTEXT_ALL:
                self.onSessionContextAll(details=response)
                  
            elif response['cmd'] == CMD_TR_GET_REPORTS:
                self.onGetTrReports(details=response)
            elif response['cmd'] == CMD_TR_GET_IMAGE:
                self.onGetTrImage(details=response)
            elif response['cmd'] in [ CMD_TR_DELETE, CMD_TR_DELETE_BY_DATE ]:
                self.onGetTrRemoved(details=response)
            elif response['cmd'] == CMD_TR_LISTING:
                self.onGetTrListing(details=response)
            elif response['cmd'] == CMD_TR_REMOVE:
                self.onGetTrReseted(details=response)
            elif response['cmd'] == CMD_TR_DOWNLOAD:
                self.onGetTrDownloaded(details=response)
            elif response['cmd'] == CMD_TR_UNCOMPLETE:
                self.onGetTrUncomplete(details=response) 
            elif response['cmd'] == CMD_TR_ZIP:
                self.onGetTrZipped(details=response)
            elif response['cmd'] == CMD_TR_ADD_COMMENT:
                self.onCommentAdded(details=response)
            elif response['cmd'] == CMD_TR_DEL_COMMENTS:
                self.onCommentsDeleted(details=response)
            elif response['cmd'] == CMD_TR_GET_VERDICTS:
                self.onGetTrVerdicts(details=response)
            elif response['cmd'] == CMD_TR_GET_DESIGNS:
                self.onGetTrDesigns(details=response)
            elif response['cmd'] == CMD_TR_GET_REVIEWS:
                self.onGetTrReviews(details=response)
            elif response['cmd'] == CMD_TR_BACKUP:
                self.onBackupResults(details=response)  
            elif response['cmd'] == CMD_TR_BACKUP_REMOVE_ALL:
                self.onRemoveBackupsResults(details=response)  
            elif response['cmd'] == CMD_TR_BACKUP_DOWNLOAD:
                self.onDownloadBackupResults(details=response) 
            elif response['cmd'] == CMD_TR_STATISTICS:
                self.onStatisticsResults(details=response) 
                 
            elif response['cmd'] == CMD_METRICS_RESET:
                self.onMetricsReset(details=response)
            elif response['cmd'] == CMD_METRICS_WRITING_DURATION:
                self.onMetricsTestsDurationWriting(details=response)
                
            elif response['cmd'] == CMD_SYSTEM_USAGES:
                self.onSystemUsages(details=response)
                
            elif response['cmd'] == CMD_CLIENTS_AVAILABLE:
                self.onClientAvailable(details=response)
            elif response['cmd'] == CMD_CLIENTS_DOWNLOAD:
                self.onClientDownload(details=response)

            elif response['cmd'] == CMD_DOCS_BUILD:
                self.onBuildDocumentations(details=response)
            elif response['cmd'] == CMD_DOCS_CACHE:
                self.onCacheDocumentations(details=response)

            elif response['cmd'] == CMD_TESTS_UNLOCK_ALL:
                self.onUnlockTests(details=response)  
            elif response['cmd'] == CMD_TESTS_BUILD:
                self.onBuildTestsSamples(details=response)  
            elif response['cmd'] == CMD_TESTS_BACKUP:
                self.onBackupTests(details=response)  
            elif response['cmd'] == CMD_TESTS_BACKUP_REMOVE_ALL:
                self.onRemoveBackupsTests(details=response)  
            elif response['cmd'] == CMD_TESTS_BACKUP_DOWNLOAD:
                self.onDownloadBackupTests(details=response) 
            elif response['cmd'] == CMD_TESTS_RESET:
                self.onResetTests(details=response) 
            elif response['cmd'] == CMD_TESTS_STATISTICS:
                self.onStatisticsTests(details=response) 
            elif response['cmd'] == CMD_TESTS_FILE_MOVE:
                self.onTestsFileMoved(details=response) 
            elif response['cmd'] == CMD_TESTS_FOLDER_MOVE:
                self.onTestsFolderMoved(details=response) 
            elif response['cmd'] == CMD_TESTS_LISTING:
                self.onTestsListing(details=response) 
            elif response['cmd'] == CMD_TESTS_FILE_RENAME:
                self.onTestsFileRenamed(details=response) 
            elif response['cmd'] == CMD_TESTS_FOLDER_RENAME:
                self.onTestsFolderRenamed(details=response)
            elif response['cmd'] == CMD_TESTS_FILE_DUPLICATE:
                self.onTestsFileDuplicated(details=response) 
            elif response['cmd'] == CMD_TESTS_FOLDER_DUPLICATE:
                self.onTestsFolderDuplicated(details=response)
            elif response['cmd'] == CMD_TESTS_FILE_REMOVE:
                self.onTestsFileRemoved(details=response) 
            elif response['cmd'] == CMD_TESTS_FOLDER_REMOVE:
                self.onTestsFolderRemoved(details=response)
            elif response['cmd'] == CMD_TESTS_FOLDER_REMOVE_ALL:
                self.onTestsFoldersRemoved(details=response)
            elif response['cmd'] == CMD_TESTS_FOLDER_ADD:
                self.onTestsFolderAdded(details=response)
            elif response['cmd'] == CMD_TESTS_SNAPSHOT_ADD:
                self.onTestsSnapshotAdded(details=response)
            elif response['cmd'] == CMD_TESTS_SNAPSHOT_RESTORE:
                self.onTestsSnapshotRestored(details=response)
            elif response['cmd'] == CMD_TESTS_SNAPSHOT_REMOVE:
                self.onTestsSnapshotRemoved(details=response)
            elif response['cmd'] == CMD_TESTS_SNAPSHOT_REMOVE_ALL:
                self.onTestsSnapshotRemovedAll(details=response)
            elif response['cmd'] == CMD_TESTS_FILE_OPEN:
                self.onTestsFileOpened(details=response)       
            elif response['cmd'] == CMD_TESTS_FILE_UPLOAD:
                self.onTestsFileUploaded(details=response)    
            elif response['cmd'] == CMD_TESTS_FILE_UNLOCK:
                self.onTestsFileUnlocked(details=response) 
            elif response['cmd'] == CMD_TESTS_DEFAULT_VERSION:
                self.onTestsDefaultAll(details=response) 
            elif response['cmd'] == CMD_TESTS_CHECK_SYNTAX:
                self.onTestsCheckSyntax(details=response) 
            elif response['cmd'] == CMD_TESTS_CHECK_SYNTAX_TPG:
                self.onTestsCheckSyntax(details=response)
            elif response['cmd'] == CMD_TESTS_CREATE_DESIGN:
                self.onTestsCreateDesign(details=response) 
            elif response['cmd'] == CMD_TESTS_CREATE_DESIGN_TPG:
                self.onTestsCreateDesign(details=response)
            elif response['cmd'] == CMD_TESTS_SCHEDULE_GROUP:
                self.onTestsScheduled(details=response)
            elif response['cmd'] == CMD_TESTS_SCHEDULE:
                self.onTestScheduled(details=response) 
            elif response['cmd'] == CMD_TESTS_SCHEDULE_TPG:
                self.onTestScheduled(details=response) 
                
            elif response['cmd'] == CMD_TASKS_WAITING:
                self.onWaitingTasks(details=response) 
            elif response['cmd'] == CMD_TASKS_RUNNING:
                self.onRunningTasks(details=response) 
            elif response['cmd'] == CMD_TASKS_HISTORY:
                self.onHistoryTasks(details=response) 
            elif response['cmd'] == CMD_TASKS_HISTORY_ALL:
                self.onHistoryTasksAll(details=response) 
            elif response['cmd'] == CMD_TASKS_HISTORY_CLEAR:
                self.onClearHistory(details=response) 
            elif response['cmd'] == CMD_TASKS_SCHEDULE:
                self.onTaskReschedule(details=response)
            elif response['cmd'] == CMD_TASKS_REPLAY:
                self.onTasksReplayed(details=response)
            elif response['cmd'] == CMD_TASKS_DESIGN:
                self.onTasksDesign(details=response)
            elif response['cmd'] == CMD_TASKS_VERDICT:
                self.onTasksVerdict(details=response)
            elif response['cmd'] == CMD_TASKS_REVIEW:
                self.onTasksReview(details=response)
            elif response['cmd'] == CMD_TASKS_COMMENT:
                self.onTasksComment(details=response)
            elif response['cmd'] == CMD_TASKS_KILL:
                self.onTasksKill(details=response)
            elif response['cmd'] == CMD_TASKS_KILL_ALL:
                self.onTasksKillAll(details=response)
            elif response['cmd'] == CMD_TASKS_KILL_SELECTIVE:
                self.onTasksKillSelective(details=response)
            elif response['cmd'] == CMD_TASKS_CANCEL:
                self.onTasksCancel(details=response)
            elif response['cmd'] == CMD_TASKS_CANCEL_ALL:
                self.onTasksCancelAll(details=response)
            elif response['cmd'] == CMD_TASKS_CANCEL_SELECTIVE:
                self.onTasksCancelSelective(details=response)
                
            elif response['cmd'] == CMD_AGENTS_RUNNING:
                self.onAgentsRunning(details=response)
            elif response['cmd'] == CMD_AGENTS_DEFAULT:
                self.onAgentsDefault(details=response)
            elif response['cmd'] == CMD_AGENTS_DISCONNECT:
                self.onAgentsDisconnect(details=response)
            elif response['cmd'] == CMD_AGENTS_CONNECT:
                self.onAgentsConnect(details=response)
            elif response['cmd'] == CMD_AGENTS_ADD:
                self.onAgentsAdd(details=response)
            elif response['cmd'] == CMD_AGENTS_REMOVE:
                self.onAgentsRemove(details=response)
                
            elif response['cmd'] == CMD_PROBES_RUNNING:
                self.onProbesRunning(details=response)
            elif response['cmd'] == CMD_PROBES_DEFAULT:
                self.onProbesDefault(details=response)
            elif response['cmd'] == CMD_PROBES_DISCONNECT:
                self.onProbesDisconnect(details=response)
            elif response['cmd'] == CMD_PROBES_CONNECT:
                self.onProbesConnect(details=response)
            elif response['cmd'] == CMD_PROBES_ADD:
                self.onProbesAdd(details=response)
            elif response['cmd'] == CMD_PROBES_REMOVE:
                self.onProbesRemove(details=response)
            
            elif response['cmd'] == CMD_LIBRARIES_UNLOCK_ALL:
                self.onUnlockLibraries(details=response)
            elif response['cmd'] == CMD_LIBRARIES_SYNTAX_ALL:
                self.onSyntaxAllLibraries(details=response)
            elif response['cmd'] == CMD_LIBRARIES_SYNTAX:
                self.onSyntaxLibrary(details=response)
            elif response['cmd'] == CMD_LIBRARIES_BUILD:
                self.onBuildLibraries(details=response)
            elif response['cmd'] == CMD_LIBRARIES_DEFAULT:
                self.onDefaultLibraries(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_GENERIC:
                self.onGenericLibraries(details=response)
            elif response['cmd'] == CMD_LIBRARIES_BACKUP:
                self.onBackupLibraries(details=response)  
            elif response['cmd'] == CMD_LIBRARIES_BACKUP_REMOVE_ALL:
                self.onRemoveBackupsAdapters(details=response)  
            elif response['cmd'] == CMD_LIBRARIES_BACKUP_DOWNLOAD:
                self.onDownloadBackupLibraries(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_RESET:
                self.onResetLibraries(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_STATISTICS:
                self.onStatisticsLibraries(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_LISTING:
                self.onLibrariesListing(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FILE_MOVE:
                self.onLibrariesFileMoved(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FOLDER_MOVE:
                self.onLibrariesFolderMoved(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FILE_RENAME:
                self.onLibrariesFileRenamed(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FOLDER_RENAME:
                self.onLibrariesFolderRenamed(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FILE_DUPLICATE:
                self.onLibrariesFileDuplicated(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FOLDER_DUPLICATE:
                self.onLibrariesFolderDuplicated(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FILE_REMOVE:
                self.onLibrariesFileRemoved(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FOLDER_REMOVE:
                self.onLibrariesFolderRemoved(details=response)
            elif response['cmd'] == CMD_LIBRARIES_FOLDER_REMOVE_ALL:
                self.onLibrariesFoldersRemoved(details=response)
            elif response['cmd'] == CMD_LIBRARIES_FOLDER_ADD:
                self.onLibrariesFolderAdded(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FILE_OPEN:
                self.onLibrariesFileOpened(details=response)       
            elif response['cmd'] == CMD_LIBRARIES_FILE_UPLOAD:
                self.onLibrariesFileUploaded(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_FILE_UNLOCK:
                self.onLibrariesFileUnlocked(details=response) 
            elif response['cmd'] == CMD_LIBRARIES_PACKAGE_ADD:
                self.onLibrariesPackageAdded(details=response)
            elif response['cmd'] == CMD_LIBRARIES_LIB_ADD:
                self.onLibrariesLibraryAdded(details=response)
                
            elif response['cmd'] == CMD_ADAPTERS_UNLOCK_ALL:
                self.onUnlockAdapters(details=response)
            elif response['cmd'] == CMD_ADAPTERS_SYNTAX_ALL:
                self.onSyntaxAllAdapters(details=response)
            elif response['cmd'] == CMD_ADAPTERS_SYNTAX:
                self.onSyntaxAdapter(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_BUILD:
                self.onBuildAdapters(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_DEFAULT:
                self.onDefaultAdapters(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_GENERIC:
                self.onGenericAdapters(details=response)
            elif response['cmd'] == CMD_ADAPTERS_BACKUP:
                self.onBackupAdapters(details=response)  
            elif response['cmd'] == CMD_ADAPTERS_BACKUP_REMOVE_ALL:
                self.onRemoveBackupsAdapters(details=response)  
            elif response['cmd'] == CMD_ADAPTERS_BACKUP_DOWNLOAD:
                self.onDownloadBackupAdapters(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_RESET:
                self.onResetAdapters(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_STATISTICS:
                self.onStatisticsAdapters(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_LISTING:
                self.onAdaptersListing(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FILE_MOVE:
                self.onAdaptersFileMoved(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FOLDER_MOVE:
                self.onAdaptersFolderMoved(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FILE_DUPLICATE:
                self.onAdaptersFileDuplicated(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FOLDER_DUPLICATE:
                self.onAdaptersFolderDuplicated(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FILE_REMOVE:
                self.onAdaptersFileRemoved(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FOLDER_REMOVE:
                self.onAdaptersFolderRemoved(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FOLDER_REMOVE_ALL:
                self.onAdaptersFoldersRemoved(details=response)
            elif response['cmd'] == CMD_ADAPTERS_FOLDER_ADD:
                self.onAdaptersFolderAdded(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FOLDER_RENAME:
                self.onAdaptersFolderRenamed(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FILE_RENAME:
                self.onAdaptersFileRenamed(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FILE_OPEN:
                self.onAdaptersFileOpened(details=response)       
            elif response['cmd'] == CMD_ADAPTERS_FILE_UPLOAD:
                self.onAdaptersFileUploaded(details=response) 
            elif response['cmd'] == CMD_ADAPTERS_FILE_UNLOCK:
                self.onAdaptersFileUnlocked(details=response)
            elif response['cmd'] == CMD_ADAPTERS_PACKAGE_ADD:
                self.onAdaptersPackageAdded(details=response)
            elif response['cmd'] == CMD_ADAPTERS_ADP_ADD:
                self.onAdaptersAdapterAdded(details=response)
            elif response['cmd'] == CMD_ADAPTERS_ADP_ADD_WSDL_URL:
                self.onAdaptersAdapterWsdlUrlAdded(details=response)
            elif response['cmd'] == CMD_ADAPTERS_ADP_ADD_WSDL_FILE:
                self.onAdaptersAdapterWsdlFileAdded(details=response)
    
            else:
                self.onGenericError(err=self.tr("Bad cmd provided on response: %s" % response["cmd"]), 
                                    title=self.tr("Bad message") )
    
    def onUpdateClientClicked(self, clientName):
        """
        """
        self.updateDialog.done(0)
        
        # rest call to download the client
        self.downloadClient(clientName="%s" % clientName) 
        
    def checkClientUpdateAuto(self):
        """
        """
        self.checkClientUpdate(recheck=True)
        
    # handle rest requests
    @calling_rest
    def login(self, login, password, channelId):  
        """
        Login
        """
        # reset
        self.__login = login
        self.__sessionId = None
        self.__expires = 0
        self.refreshTimer.stop()
        ServerExplorer.instance().rest().unsetWsCookie()
        
        # password is a sha1
        _json = { 'login': login, 'password': password, 'channel-id': channelId }
        _json.update( self.application().getCurrentVersion() )
        self.makeRequest( uri=CMD_LOGIN, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def logout(self):  
        """
        Logout
        """
        self.refreshTimer.stop()
        if self.__sessionId is not None:
            self.makeRequest( uri=CMD_LOGOUT, request=HTTP_GET )
    
    @calling_rest
    def refresh(self):  
        """
        Refresh
        """
        self.makeRequest( uri=CMD_REFRESH, request=HTTP_GET )
    
    @calling_rest
    def deleteTestResult(self, testId,  projectId=0):
        """
        Delete test result
        """
        _json = { 'project-id': int(projectId), 'test-id': testId }
        self.makeRequest( uri=CMD_TR_DELETE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def waitingTasks(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TASKS_WAITING, request=HTTP_GET, _json={} )
    
    @calling_rest
    def runningTasks(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TASKS_RUNNING, request=HTTP_GET, _json={} )
    
    @calling_rest
    def historyTasks(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TASKS_HISTORY, request=HTTP_GET, _json={} )
    
    @calling_rest
    def historyTasksAll(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TASKS_HISTORY_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def clearHistory(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TASKS_HISTORY_CLEAR, request=HTTP_GET, _json={} )
    
    @calling_rest
    def cacheDocs(self):
        """
        Get the cache of the documentations
        """
        self.makeRequest( uri=CMD_DOCS_CACHE, request=HTTP_GET, _json={} ) 
    
    @calling_rest
    def backupTests(self, backupName):
        """
        Get the cache of the documentations
        """
        _json = { 'backup-name': backupName }
        self.makeRequest( uri=CMD_TESTS_BACKUP, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def backupResults(self, backupName):
        """
        Get the cache of the documentations
        """
        _json = { 'backup-name': backupName }
        self.makeRequest( uri=CMD_TR_BACKUP, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def backupAdapters(self, backupName):
        """
        Get the cache of the documentations
        """
        _json = { 'backup-name': backupName }
        self.makeRequest( uri=CMD_ADAPTERS_BACKUP, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def backupLibraries(self, backupName):
        """
        Get the cache of the documentations
        """
        _json = { 'backup-name': backupName }
        self.makeRequest( uri=CMD_LIBRARIES_BACKUP, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def removeBackupsTests(self):
        """
        Remove backups
        """
        self.makeRequest( uri=CMD_TESTS_BACKUP_REMOVE_ALL, request=HTTP_GET, _json={} ) 
    
    @calling_rest
    def removeBackupsAdapters(self):
        """
        Remove backups
        """
        self.makeRequest( uri=CMD_ADAPTERS_BACKUP_REMOVE_ALL, request=HTTP_GET, _json={} ) 
    
    @calling_rest
    def removeBackupsLibraries(self):
        """
        Remove backups
        """
        self.makeRequest( uri=CMD_LIBRARIES_BACKUP_REMOVE_ALL, request=HTTP_GET, _json={} ) 
    
    @calling_rest
    def removeBackupsResults(self):
        """
        Remove backups
        """
        self.makeRequest( uri=CMD_TR_BACKUP_REMOVE_ALL, request=HTTP_GET, _json={} ) 
    
    @calling_rest
    def downloadBackupsResults(self, backupName, destName):
        """
        Remove backups
        """
        _json = { 'backup-name': backupName, 'dest-name': destName }
        self.makeRequest( uri=CMD_TR_BACKUP_DOWNLOAD, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def downloadBackupsTests(self, backupName, destName):
        """
        Remove backups
        """
        _json = { 'backup-name': backupName, 'dest-name': destName }
        self.makeRequest( uri=CMD_TESTS_BACKUP_DOWNLOAD, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def downloadBackupsAdapters(self, backupName, destName):
        """
        Remove backups
        """
        _json = { 'backup-name': backupName, 'dest-name': destName }
        self.makeRequest( uri=CMD_ADAPTERS_BACKUP_DOWNLOAD, request=HTTP_POST, _json=_json ) 
    
    @calling_rest
    def downloadBackupsLibraries(self, backupName, destName):
        """
        Remove backups
        """
        _json = { 'backup-name': backupName, 'dest-name': destName }
        self.makeRequest( uri=CMD_LIBRARIES_BACKUP_DOWNLOAD, request=HTTP_POST, _json=_json ) 
        
    @calling_rest
    def rescheduleTask(self, taskId, taskEnabled, scheduleType, scheduleAt, scheduleRepeat, 
                    probesEnabled, notificationsEnabled, debugEnabled, logsEnabled, 
                    fromTime, toTime ):
        """
        Delete test result
        """
        _json = { 'task-id': int(taskId), 'schedule-id': int(scheduleType), "schedule-repeat": int(scheduleRepeat),
                  'task-enabled': taskEnabled, 'schedule-at': scheduleAt, 'probes-enabled': probesEnabled, 
                  'notifications-enabled': notificationsEnabled, 'debug-enabled': debugEnabled, 'logs-enabled': logsEnabled,
                  'from-time': fromTime, 'to-time': toTime }
        self.makeRequest( uri=CMD_TASKS_SCHEDULE, request=HTTP_POST, _json=_json)
     
    @calling_rest
    def replayTask(self, taskId):
        """
        Delete test result
        """
        _json = { 'task-id': int(taskId) }
        self.makeRequest( uri=CMD_TASKS_REPLAY, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def killTask(self, taskId):
        """
        kill
        """
        _json = { 'task-id': int(taskId) }
        self.makeRequest( uri=CMD_TASKS_KILL, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def killTasks(self, taskIds):
        """
        kill
        """
        _json = { 'tasks-id': taskIds }
        self.makeRequest( uri=CMD_TASKS_KILL_SELECTIVE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def killTasksAll(self):
        """
        kill
        """
        self.makeRequest( uri=CMD_TASKS_KILL_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def cancelTask(self, taskId):
        """
        cancel
        """
        _json = { 'task-id': int(taskId) }
        self.makeRequest( uri=CMD_TASKS_CANCEL, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def cancelTasks(self, taskIds):
        """
        cancel
        """
        _json = { 'tasks-id': taskIds }
        self.makeRequest( uri=CMD_TASKS_CANCEL_SELECTIVE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def cancelTasksAll(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_TASKS_CANCEL_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def runningAgents(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_AGENTS_RUNNING, request=HTTP_GET, _json={} )
    
    @calling_rest
    def runningProbes(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_PROBES_RUNNING, request=HTTP_GET, _json={} )
    
    @calling_rest
    def defaultAgents(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_AGENTS_DEFAULT, request=HTTP_GET, _json={} )
    
    @calling_rest
    def defaultProbes(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_PROBES_DEFAULT, request=HTTP_GET, _json={} )
    
    @calling_rest
    def resetAdapters(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_ADAPTERS_RESET, request=HTTP_GET, _json={} )
    
    @calling_rest
    def resetLibraries(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_LIBRARIES_RESET, request=HTTP_GET, _json={} )
    
    @calling_rest
    def resetTests(self):
        """
        cancel
        """
        self.makeRequest( uri=CMD_TESTS_RESET, request=HTTP_GET, _json={} )
    
    @calling_rest
    def taskVerdict(self, taskId):
        """
        Delete test result
        """
        _json = { 'task-id': int(taskId) }
        self.makeRequest( uri=CMD_TASKS_VERDICT, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def taskReview(self, taskId):
        """
        Delete test result
        """
        _json = { 'task-id': int(taskId) }
        self.makeRequest( uri=CMD_TASKS_REVIEW, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def taskDesign(self, taskId):
        """
        Delete test result
        """
        _json = { 'task-id': int(taskId) }
        self.makeRequest( uri=CMD_TASKS_DESIGN, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def taskComment(self, taskId, comment, timestamp):
        """
        Add comment on archive

        @param testId:
        @type testId:

        @param archivePost:
        @type archivePost:

        @param postTimestamp:
        @type postTimestamp:

        @param testId:
        @type testId:
        """
        _json = { 'task-id': taskId, "comment": comment, "timestamp": timestamp }
        self.makeRequest( uri=CMD_TASKS_COMMENT, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def unlockTests(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TESTS_UNLOCK_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def unlockAdapters(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_ADAPTERS_UNLOCK_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def unlockLibraries(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_LIBRARIES_UNLOCK_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def unlockTestFile(self, filePath, fileName, fileExtension, projectId):
        """
        Delete test result
        """
        _json = { "file-path": filePath, "file-name": fileName, 
                  "file-extension": fileExtension, "project-id": projectId }
        self.makeRequest( uri=CMD_TESTS_FILE_UNLOCK, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def unlockAdapterFile(self, filePath, fileName, fileExtension):
        """
        Delete test result
        """
        _json = { "file-path": filePath, "file-name": fileName, 
                  "file-extension": fileExtension }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_UNLOCK, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def unlockLibraryFile(self, filePath, fileName, fileExtension):
        """
        Delete test result
        """
        _json = { "file-path": filePath, "file-name": fileName, 
                  "file-extension": fileExtension }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_UNLOCK, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def uploadTestFile(self, filePath, fileName, fileExtension, fileContent, projectId, 
                       updateMode, closeTabAfter):
        """
        Delete test result
        """
        _json = { "file-path": filePath, "file-name": fileName, 
                  "file-extension": fileExtension, "file-content": fileContent,
                  "project-id": projectId, "overwrite": updateMode,
                  "close-after": closeTabAfter }
        self.makeRequest( uri=CMD_TESTS_FILE_UPLOAD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def uploadAdapterFile(self, filePath, fileName, fileExtension, fileContent, 
                          updateMode, closeTabAfter):
        """
        Delete test result
        """
        _json = { "file-path": filePath, "file-name": fileName, "file-content": fileContent,
                  "file-extension": fileExtension, "overwrite": updateMode,
                  "close-after": closeTabAfter }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_UPLOAD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def uploadLibraryFile(self, filePath, fileName, fileExtension, fileContent, 
                          updateMode, closeTabAfter):
        """
        Delete test result
        """
        _json = { "file-path": filePath, "file-name": fileName, "file-content": fileContent,
                  "file-extension": fileExtension, "overwrite": updateMode,
                  "close-after": closeTabAfter }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_UPLOAD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def buildDocumentations(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_DOCS_BUILD, request=HTTP_GET, _json={} )
    
    @calling_rest
    def buildAdapters(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_ADAPTERS_BUILD, request=HTTP_GET, _json={} )
    
    @calling_rest
    def buildLibraries(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_LIBRARIES_BUILD, request=HTTP_GET, _json={} )
    
    @calling_rest
    def buildSamples(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_TESTS_BUILD, request=HTTP_GET, _json={} )
    
    @calling_rest
    def resetTestsMetrics(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_METRICS_RESET, request=HTTP_GET, _json={} )
    
    @calling_rest
    def durationTestsWritingMetrics(self, duration, projectId, isTp=False, isTs=False, 
                                          isTu=False, isTg=False, isTa=False):
        """
        Delete test result
        """
        _json = { "project-id": int(projectId), "duration": duration, "is-ta": isTa,
                    "is-tu": isTu, "is-ts": isTs, "is-tp": isTp, "is-tg": isTg }
        self.makeRequest( uri=CMD_METRICS_WRITING_DURATION, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def sessionContext(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_CONTEXT, request=HTTP_GET, _json={} )
    
    @calling_rest
    def systemUsages(self):
        """
        Delete test result
        """
        self.makeRequest( uri=CMD_SYSTEM_USAGES, request=HTTP_GET, _json={} )
    
    @calling_rest
    def checkSyntaxAdapters(self):
        """
        check syntax
        """
        self.makeRequest( uri=CMD_ADAPTERS_SYNTAX_ALL, request=HTTP_GET, _json={} )
    
    @calling_rest
    def checkSyntaxLibraries(self):
        """
        check syntax
        """
        self.makeRequest( uri=CMD_LIBRARIES_SYNTAX_ALL, request=HTTP_GET, _json={} )
        
    @calling_rest
    def checkSyntaxAdapter(self, fileContent):
        """
        check syntax
        """
        _json = { "file-content": fileContent }
        self.makeRequest( uri=CMD_ADAPTERS_SYNTAX, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def checkSyntaxLibrary(self, fileContent):
        """
        check syntax
        """
        _json = { "file-content": fileContent }
        self.makeRequest( uri=CMD_LIBRARIES_SYNTAX, request=HTTP_POST, _json=_json )
 
    @calling_rest
    def addPackageAdapters(self, packageName):
        """
        check syntax
        """
        _json = { "package-name": packageName }
        self.makeRequest( uri=CMD_ADAPTERS_PACKAGE_ADD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def addPackageLibraries(self, packageName):
        """
        check syntax
        """
        _json = { "package-name": packageName }
        self.makeRequest( uri=CMD_LIBRARIES_PACKAGE_ADD, request=HTTP_POST, _json=_json )

    @calling_rest
    def addPackageAdapter(self, packageName, adapterName):
        """
        check syntax
        """
        _json = { "package-name": packageName, "adapter-name": adapterName }
        self.makeRequest( uri=CMD_ADAPTERS_ADP_ADD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def addPackageLibrary(self, packageName, libraryName):
        """
        check syntax
        """
        _json = { "package-name": packageName, "library-name": libraryName }
        self.makeRequest( uri=CMD_LIBRARIES_LIB_ADD, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def addAdapterByWsdlUrl(self, packageName, overwriteAdapter, wsdlUrl):
        """
        check syntax
        """
        _json = { "package-name": packageName, "overwrite-adapter": overwriteAdapter,
                  "wsdl-url": wsdlUrl}
        self.makeRequest( uri=CMD_ADAPTERS_ADP_ADD_WSDL_URL, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def addAdapterByWsdlFile(self, packageName, overwriteAdapter, wsdlFile):
        """
        check syntax
        """
        _json = { "package-name": packageName, "overwrite-adapter": overwriteAdapter,
                  "wsdl-file": wsdlFile}
        self.makeRequest( uri=CMD_ADAPTERS_ADP_ADD_WSDL_FILE, request=HTTP_POST, _json=_json )
  
    @calling_rest
    def setAllTestsAsDefault(self):
        """
        check syntax
        """
        self.makeRequest( uri=CMD_TESTS_DEFAULT_VERSION, request=HTTP_GET, _json=_json )
        
    @calling_rest
    def setDefaultAdapter(self, packageName):
        """
        Delete test result
        """
        _json = { 'package-name': packageName }
        self.makeRequest( uri=CMD_ADAPTERS_DEFAULT, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def setGenericAdapter(self, packageName):
        """
        Delete test result
        """
        _json = { 'package-name': packageName }
        self.makeRequest( uri=CMD_ADAPTERS_GENERIC, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def setDefaultLibrary(self, packageName):
        """
        Delete test result
        """
        _json = { 'package-name': packageName }
        self.makeRequest( uri=CMD_LIBRARIES_DEFAULT, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def setGenericLibrary(self, packageName):
        """
        Delete test result
        """
        _json = { 'package-name': packageName }
        self.makeRequest( uri=CMD_LIBRARIES_GENERIC, request=HTTP_POST, _json=_json )
            
    @calling_rest
    def deleteTestResultByDate(self, date,  projectId=0):
        """
        Delete test result
        """
        _json = { 'project-id': int(projectId), 'date': date }
        self.makeRequest( uri=CMD_TR_DELETE_BY_DATE, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def addCommentTr(self, testId, replayId, comment, timestamp, projectId=0, returnAll=True):
        """
        Add comment on archive

        @param testId:
        @type testId:

        @param archivePost:
        @type archivePost:

        @param postTimestamp:
        @type postTimestamp:

        @param testId:
        @type testId:
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, "replay-id": replayId,
                  "comment": comment, "timestamp": timestamp, "return-all": returnAll }
        self.makeRequest( uri=CMD_TR_ADD_COMMENT, request=HTTP_POST, _json=_json )

    @calling_rest
    def delCommentsTr(self, testId, replayId, projectId=0):
        """
        Delete comments on archives

        @param archiveFile:
        @type archiveFile:
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, "replay-id": replayId}
        self.makeRequest( uri=CMD_TR_DEL_COMMENTS, request=HTTP_POST, _json=_json )
 
    @calling_rest
    def refreshTr(self, projectId=0, partialRefresh=False):
        """
        Refresh results

        @param project:
        @type project:
        """
        _json = { 'project-id': int(projectId), 'partial-list': partialRefresh}
        self.makeRequest( uri=CMD_TR_LISTING, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def createTrZip (self, testId, projectId=1):
        """
        Create zip archives

        @param mainPathToZip:
        @type mainPathToZip:

        @param subPathToZip:
        @type subPathToZip:
        """
        _json = { 'project-id': int(projectId), 'test-id': testId }
        self.makeRequest( uri=CMD_TR_ZIP, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def getUncompleteTr (self, testId, projectId=1):
        """
        Get uncomplete test result (not yet terminated)

        @param mainPathToZip:
        @type mainPathToZip:

        @param subPathToZip:
        @type subPathToZip:
        """
        _json = { 'project-id': int(projectId), 'test-id': testId }
        self.makeRequest( uri=CMD_TR_UNCOMPLETE, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def downloadResult(self, fileName, testId, projectId=0, saveAs=False, saveAsName=''):
        """
        Download test result v2
        """
        if sys.version_info > (3,): # python 3 support
            encodedDest = base64.b64encode(bytes(saveAsName, "utf8") )
            encodedDest= encodedDest.decode("utf-8")
        else:
            encodedDest = base64.b64encode( saveAsName.encode("utf8")  )

        _json = { 'project-id': int(projectId), 'file-name': fileName, 'test-id': testId, 
                  'save-as': saveAs , 'save-as-name': encodedDest }
        self.makeRequest( uri=CMD_TR_DOWNLOAD, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def resetTr(self, projectId=0):
        """
        Empty repository

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        _json = { 'project-id': int(projectId) }
        self.makeRequest( uri=CMD_TR_REMOVE, request=HTTP_POST, _json=_json )
        
    @calling_rest        
    def getTrReports(self, testId, replayId=0, projectId=0):
        """
        Get test basic report
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, 'replay-id': replayId }
        self.makeRequest( uri=CMD_TR_GET_REPORTS, request=HTTP_POST, _json=_json )
        
    @calling_rest        
    def getTrReviews(self, testId, replayId=0, projectId=0):
        """
        Get test basic report
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, 'replay-id': replayId }
        self.makeRequest( uri=CMD_TR_GET_REVIEWS, request=HTTP_POST, _json=_json )
        
    @calling_rest        
    def getTrDesigns(self, testId, replayId=0, projectId=0):
        """
        Get test basic report
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, 'replay-id': replayId }
        self.makeRequest( uri=CMD_TR_GET_DESIGNS, request=HTTP_POST, _json=_json )
        
    @calling_rest        
    def getTrVerdicts(self, testId, replayId=0, projectId=0):
        """
        Get test basic report
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, 'replay-id': replayId }
        self.makeRequest( uri=CMD_TR_GET_VERDICTS, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def getTrImage(self, testId, imageName, projectId=0):
        """
        Get image privew
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, 'image-name': imageName }
        self.makeRequest( uri=CMD_TR_GET_IMAGE, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def statisticsTests(self, projectId=0):
        """
        Get image privew
        """
        _json = { 'project-id': int(projectId) }
        self.makeRequest( uri=CMD_TESTS_STATISTICS, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def statisticsAdapters(self):
        """
        Get image privew
        """
        self.makeRequest( uri=CMD_ADAPTERS_STATISTICS, request=HTTP_GET, _json={} )
        
    @calling_rest
    def statisticsLibraries(self):
        """
        Get image privew
        """
        self.makeRequest( uri=CMD_LIBRARIES_STATISTICS, request=HTTP_GET, _json={} )
        
    @calling_rest
    def statisticsResults(self, projectId=0):
        """
        Get image privew
        """
        _json = { 'project-id': int(projectId) }
        self.makeRequest( uri=CMD_TR_STATISTICS, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def disconnectAgent(self, agentName):
        """
        Get image privew
        """
        _json = { 'agent-name': agentName }
        self.makeRequest( uri=CMD_AGENTS_DISCONNECT, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def disconnectProbe(self, probeName):
        """
        Get image privew
        """
        _json = { 'probe-name': probeName }
        self.makeRequest( uri=CMD_PROBES_DISCONNECT, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def addAgent(self, agentName, agentType, agentDescription):
        """
        Add agent
        """
        _json = { 'agent-name': agentName, 'agent-type': agentType,
                  'agent-description': agentDescription}
        self.makeRequest( uri=CMD_AGENTS_ADD, request=HTTP_POST, _json=_json )
       
    @calling_rest
    def addProbe(self, probeName, probeType, probeDescription):
        """
        Add probe
        """
        _json = { 'probe-name': probeName, 'probe-type': probeType,
                  'probe-description': probeDescription}
        self.makeRequest( uri=CMD_PROBES_ADD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def removeAgent(self, agentName):
        """
        Add agent
        """
        _json = { 'agent-name': agentName}
        self.makeRequest( uri=CMD_AGENTS_REMOVE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def removeProbe(self, probeName):
        """
        Add probe
        """
        _json = { 'probe-name': probeName}
        self.makeRequest( uri=CMD_PROBES_REMOVE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def connectAgent(self, agentName, agentType, agentDescription, agentBoot):
        """
        Add agent
        """
        _json = { 'agent-name': agentName, 'agent-type': agentType,
                  'agent-description': agentDescription, 'agent-boot': agentBoot}
        self.makeRequest( uri=CMD_AGENTS_CONNECT, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def connectProbe(self, probeName, probeType, probeDescription, probeBoot):
        """
        Add probe
        """
        _json = { 'probe-name': probeName, 'probe-type': probeType,
                  'probe-description': probeDescription, 'probe-boot': probeBoot}
        self.makeRequest( uri=CMD_PROBES_CONNECT, request=HTTP_POST, _json=_json )
 
    @calling_rest
    def checkClientUpdate(self, recheck=False):
        """
        Add probe
        """
        _json = self.application().getCurrentVersion()
        _json['recheck'] = recheck
        self.makeRequest( uri=CMD_CLIENTS_AVAILABLE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def downloadClient(self, clientName):
        """
        Add probe
        """
        _json = { 'client-name': clientName, 'client-platform': sys.platform }
        self.makeRequest( uri=CMD_CLIENTS_DOWNLOAD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def getContextAll(self):
        """
        Add probe
        """
        self.makeRequest( uri=CMD_CONTEXT_ALL, request=HTTP_GET, _json={} )

    @calling_rest
    def moveFileAdapters(self, filePath, fileName, fileExt, newPath):
        """
        Add probe
        """
        _json = { 
                    "source": { "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "file-path": newPath }
                }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_MOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def moveFileTests(self, filePath, fileName, fileExt, fileProject, newPath, newProject):
        """
        Add probe
        """
        _json = { 
                    "source": { "project-id": int(fileProject),
                                "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "project-id": int(newProject),
                                     "file-path": newPath }
                }
        self.makeRequest( uri=CMD_TESTS_FILE_MOVE, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def moveFileLibraries(self, filePath, fileName, fileExt, newPath):
        """
        Add probe
        """
        _json = { 
                    "source": {  "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "file-path": newPath }
                }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_MOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def renameFileAdapters(self, filePath, fileName, fileExt, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "file-name": newName }
                }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_RENAME, request=HTTP_POST, _json=_json )

    @calling_rest
    def renameFileTests(self, filePath, fileName, fileExt, fileProject, newName, update_location=False):
        """
        Add probe
        """
        _json = { 
                    "source": {"project-id": int(fileProject),
                               "file-path": filePath,
                               "file-name": fileName,
                               "file-extension": fileExt},
                    "destination": {"file-name": newName},
                    "update_location": update_location
                }
        self.makeRequest( uri=CMD_TESTS_FILE_RENAME, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def renameFileLibraries(self, filePath, fileName, fileExt, newName):
        """
        Add probe
        """
        _json = { 
                    "source": {  "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "file-name": newName }
                }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_RENAME, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def duplicateFileAdapters(self, filePath, fileName, fileExt, newPath, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "file-path": newPath,
                                     "file-name": newName }
                }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_DUPLICATE, request=HTTP_POST, _json=_json )

    @calling_rest
    def duplicateFileTests(self, filePath, fileName, fileExt, fileProject, newPath, newName, newProject):
        """
        Add probe
        """
        _json = { 
                    "source": { "project-id": int(fileProject),
                                "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "project-id": int(newProject),
                                     "file-path": newPath,
                                     "file-name": newName
                                     }
                }
        self.makeRequest( uri=CMD_TESTS_FILE_DUPLICATE, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def duplicateFileLibraries(self, filePath, fileName, fileExt, newPath, newName):
        """
        Add probe
        """
        _json = { 
                    "source": {  "file-path": filePath,
                                "file-name": fileName,
                                "file-extension": fileExt },
                    "destination": { "file-path": newPath,
                                     "file-name": newName }
                }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_DUPLICATE, request=HTTP_POST, _json=_json )
         
    @calling_rest
    def removeFileAdapters(self, filePath):
        """
        Add probe
        """
        _json = { "file-path": filePath }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_REMOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFileTests(self, filePath, fileProject):
        """
        Add probe
        """
        _json = { "project-id": int(fileProject), "file-path": filePath}
        self.makeRequest( uri=CMD_TESTS_FILE_REMOVE, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def removeFileLibraries(self, filePath):
        """
        Add probe
        """
        _json = { "file-path": filePath }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_REMOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def moveFolderAdapters(self, folderPath, folderName, newPath):
        """
        Add probe
        """
        _json = { 
                    "source": { "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-path": newPath }
                }
        self.makeRequest( uri=CMD_ADAPTERS_FOLDER_MOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def moveFolderLibraries(self, folderPath, folderName, newPath):
        """
        Add probe
        """
        _json = { 
                    "source": { "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-path": newPath }
                }
        self.makeRequest( uri=CMD_LIBRARIES_FOLDER_MOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def moveFolderTests(self, folderPath, folderName, folderProject, newPath, newProject):
        """
        Add probe
        """
        _json = { 
                    "source": { "project-id": int(folderProject),
                                "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "project-id": int(newProject),
                                     "directory-path": newPath }
                }
        self.makeRequest( uri=CMD_TESTS_FOLDER_MOVE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def addSnapshotTests(self, projectId, testPath, snapshotName, snapshotTimestamp):
        """
        add snapshot
        """
        _json = { "project-id": projectId, "test-path": testPath,
                  "snapshot-name": snapshotName, "snapshot-timestamp": snapshotTimestamp }
        self.makeRequest( uri=CMD_TESTS_SNAPSHOT_ADD, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def scheduleTests(self, tests, postponeMode, postponeAt, parallelMode):
        """
        """
        _json = { "tests": tests, "postpone-mode": postponeMode,
                  "postpone-at": postponeAt, "parallel-mode": parallelMode}
        self.makeRequest( uri=CMD_TESTS_SCHEDULE_GROUP, request=HTTP_POST, _json=_json )
        
    @calling_rest
    def scheduleTest(self, req, wdocument=None):
        """
        """
        if wdocument is not None:
            path = wdocument.getShortName( withAsterisk = False )
            TestResults.instance().newTest( name = "[] %s" % path, projectId=req["project-id"] )
        else:
            TestResults.instance().newTest( name = "[] %s" % req["test-name"], projectId=req["project-id"] )
                
        self.makeRequest( uri=CMD_TESTS_SCHEDULE, request=HTTP_POST, _json=req )
        
    @calling_rest
    def scheduleTestTpg(self, req, wdocument=None):
        """
        """
        if wdocument is not None:
            path = wdocument.getShortName( withAsterisk = False )
            TestResults.instance().newTest( name = "[] %s" % path, projectId=req["project-id"] )
        else:
            TestResults.instance().newTest( name = "[] %s" % req["test-name"], projectId=req["project-id"] )
                
        self.makeRequest( uri=CMD_TESTS_SCHEDULE_TPG, request=HTTP_POST, _json=req )

    @calling_rest
    def restoreSnapshotTests(self, projectId, snapshotPath, snapshotName):
        """
        restore snapshot
        """
        _json = { "project-id": projectId, "snapshot-path": snapshotPath,
                  "snapshot-name": snapshotName}
        self.makeRequest( uri=CMD_TESTS_SNAPSHOT_RESTORE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def removeSnapshotTests(self, projectId, snapshotPath, snapshotName):
        """
        restore snapshot
        """
        _json = { "project-id": projectId, "snapshot-path": snapshotPath,
                  "snapshot-name": snapshotName}
        self.makeRequest( uri=CMD_TESTS_SNAPSHOT_REMOVE, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def removeAllSnapshotTests(self, projectId, testPath, testName, testExtension):
        """
        restore snapshot
        """
        _json = { "project-id": projectId, "test-path": testPath, "test-name": testName,
                  "test-extension": testExtension }
        self.makeRequest( uri=CMD_TESTS_SNAPSHOT_REMOVE_ALL, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def openFileTests(self, projectId, filePath, ignoreLock=False, readOnly=False, 
                      customParam=None, actionId=None, destinationId=None, extra={}):
        # dbr13 extra for updating location
        """
        add snapshot
        """
        _json = {"project-id": projectId, "file-path": filePath,
                 "ignore-lock": ignoreLock, "read-only": readOnly,
                 "extra": extra}
        if customParam is not None:
            _json["custom-param"] = customParam
        if actionId is not None:
            _json["action-id"] = actionId
        if destinationId is not None:
            _json["destination-id"] = destinationId
              
        self.makeRequest( uri=CMD_TESTS_FILE_OPEN, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def openFileAdapters(self, filePath, ignoreLock=False, readOnly=False):
        """
        add snapshot
        """
        _json = { "file-path": filePath, "ignore-lock": ignoreLock, "read-only": readOnly }
        self.makeRequest( uri=CMD_ADAPTERS_FILE_OPEN, request=HTTP_POST, _json=_json )
    
    @calling_rest
    def openFileLibraries(self, filePath, ignoreLock=False, readOnly=False):
        """
        add snapshot
        """
        _json = { "file-path": filePath, "ignore-lock": ignoreLock, "read-only": readOnly }
        self.makeRequest( uri=CMD_LIBRARIES_FILE_OPEN, request=HTTP_POST, _json=_json )
     
    @calling_rest
    def addFolderLibraries(self, folderPath, folderName):
        """
        Add probe
        """
        _json = { "directory-path": folderPath,"directory-name": folderName }
        self.makeRequest( uri=CMD_LIBRARIES_FOLDER_ADD, request=HTTP_POST, _json=_json )

    @calling_rest
    def addFolderAdapters(self, folderPath, folderName):
        """
        Add probe
        """
        _json = { "directory-path": folderPath,"directory-name": folderName}
        self.makeRequest( uri=CMD_ADAPTERS_FOLDER_ADD, request=HTTP_POST, _json=_json )

    @calling_rest
    def addFolderTests(self, projectId, folderPath, folderName):
        """
        Add probe
        """
        _json = { "project-id": int(projectId), "directory-path": folderPath, 
                  "directory-name": folderName }
        self.makeRequest( uri=CMD_TESTS_FOLDER_ADD, request=HTTP_POST, _json=_json )

    @calling_rest
    def renameFolderLibraries(self, folderPath, folderName, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-name": newName }
                }
        self.makeRequest( uri=CMD_LIBRARIES_FOLDER_RENAME, request=HTTP_POST, _json=_json )

    @calling_rest
    def renameFolderAdapters(self, folderPath, folderName, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-name": newName }
                }
        self.makeRequest( uri=CMD_ADAPTERS_FOLDER_RENAME, request=HTTP_POST, _json=_json )

    @calling_rest
    def renameFolderTests(self, projectId, folderPath, folderName, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "project-id": projectId, 
                                "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-name": newName }
                }
        self.makeRequest( uri=CMD_TESTS_FOLDER_RENAME, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFolderLibraries(self, folderPath):
        """
        Add probe
        """
        _json = { "directory-path": folderPath}
        self.makeRequest( uri=CMD_LIBRARIES_FOLDER_REMOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFolderAdapters(self, folderPath):
        """
        Add probe
        """
        _json = { "directory-path": folderPath }
        self.makeRequest( uri=CMD_ADAPTERS_FOLDER_REMOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFolderTests(self, projectId, folderPath):
        """
        Add probe
        """
        _json = { "project-id": projectId, "directory-path": folderPath }
        self.makeRequest( uri=CMD_TESTS_FOLDER_REMOVE, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFoldersLibraries(self, folderPath):
        """
        Add probe
        """
        _json = { "directory-path": folderPath}
        self.makeRequest( uri=CMD_LIBRARIES_FOLDER_REMOVE_ALL, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFoldersAdapters(self, folderPath):
        """
        Add probe
        """
        _json = { "directory-path": folderPath }
        self.makeRequest( uri=CMD_ADAPTERS_FOLDER_REMOVE_ALL, request=HTTP_POST, _json=_json )

    @calling_rest
    def removeFoldersTests(self, projectId, folderPath):
        """
        Add probe
        """
        _json = { "project-id": projectId, "directory-path": folderPath }
        self.makeRequest( uri=CMD_TESTS_FOLDER_REMOVE_ALL, request=HTTP_POST, _json=_json )

    @calling_rest
    def duplicateFolderTests(self, folderPath, folderName, folderProject, newPath, newName, newProject):
        """
        Add probe
        """
        _json = { 
                    "source": { "project-id": int(folderProject),
                                "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "project-id": int(newProject),
                                     "directory-path": newPath,
                                     "directory-name": newName}
                }
        self.makeRequest( uri=CMD_TESTS_FOLDER_DUPLICATE, request=HTTP_POST, _json=_json )

    @calling_rest
    def duplicateFolderAdapters(self, folderPath, folderName, newPath, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-path": newPath,
                                     "directory-name": newName }
                }
        self.makeRequest( uri=CMD_ADAPTERS_FOLDER_DUPLICATE, request=HTTP_POST, _json=_json )

    @calling_rest
    def duplicateFolderLibraries(self, folderPath, folderName, newPath, newName):
        """
        Add probe
        """
        _json = { 
                    "source": { "directory-path": folderPath,
                                "directory-name": folderName  },
                    "destination": { "directory-path": newPath,
                                     "directory-name": newName }
                }
        self.makeRequest( uri=CMD_LIBRARIES_FOLDER_DUPLICATE, request=HTTP_POST, _json=_json )

    @calling_rest
    def listingTests(self, projectId, forSaveAs=False, forRuns=False):
        """
        Add probe
        """
        _json = { "project-id": int(projectId), 'for-saveas': forSaveAs, 'for-runs': forRuns}
        self.makeRequest( uri=CMD_TESTS_LISTING, request=HTTP_POST, _json=_json )

    @calling_rest
    def listingAdapters(self):
        """
        Add probe
        """
        self.makeRequest( uri=CMD_ADAPTERS_LISTING, request=HTTP_GET, _json={} )

    @calling_rest
    def listingLibraries(self):
        """
        Add probe
        """
        self.makeRequest( uri=CMD_LIBRARIES_LISTING, request=HTTP_GET, _json={} )
        
    @calling_rest
    def checkTestSyntax(self, req):
        """
        """
        self.makeRequest( uri=CMD_TESTS_CHECK_SYNTAX, request=HTTP_POST, _json=req )
        
    @calling_rest
    def checkTestSyntaxTpg(self, req):
        """
        """
        self.makeRequest( uri=CMD_TESTS_CHECK_SYNTAX_TPG, request=HTTP_POST, _json=req )
        
    @calling_rest
    def createTestDesign(self, req):
        """
        """
        self.makeRequest( uri=CMD_TESTS_CREATE_DESIGN, request=HTTP_POST, _json=req )
        
    @calling_rest
    def createTestDesignTpg(self, req):
        """
        """
        self.makeRequest( uri=CMD_TESTS_CREATE_DESIGN_TPG, request=HTTP_POST, _json=req )   

    # handle rest responses
    def onRefresh(self, details):
        """
        On refresh
        """
        self.trace("rest session refreshed")
        
    def onLogout(self, details):
        """
        On logout
        """
        self.authenticated = False
        
    def onLogin(self, details):
        """
        On authentication successfull
        """
        self.trace("on success authentication: %s" % details)
        
        self.authenticated = True
        self.userRights = details["levels"]
        self.userId = details["user_id"]
        
        # save jsessionid and start expires timer
        self.__sessionId = details['session_id']
        self.__expires = details['expires']
        ServerExplorer.instance().rest().setWsCookie(cook="session_id=%s" % self.__sessionId)
        
        # start timer
        percentRefresh = int(Settings.instance().readValue( key = 'Network/refresh-session' ))
        interval = int( int(self.__expires) * percentRefresh / 100 )
        self.refreshTimer.start( interval * 1000 )
        
        # emit success signal
        self.Authenticated.emit()

        if details['client-available']:
            majorVersion = False
            typeVersion = "minor"
            
            # convert current version to tuple
            currentMajor, currentMinor, currentFix =  self.clientVersion.split(".")
            currentVersion = (int(currentMajor), int(currentMinor), int(currentFix)) 
            
            # convert new version to tuple
            newMajor, newMinor, newFix =  details["version"].split(".")
            newVersion = (int(newMajor), int(newMinor), int(newFix))
            
            # and compare it
            if int(newMajor) >  int(currentMajor):
                majorVersion = True
                typeVersion = "major"
                
            msg_ = "%s" % self.tr("A newer %s version of this client is available." % typeVersion)
            if majorVersion:
                msg_ += "\nYou must click on download button and install the update."
            else:
                msg_ += "\nYou may click on download button and install the update."
            msg_ += "\n\nVersion %s" % details["version"]
            self.updateDialog.setDownload( title = self.tr("Update available"), txt = msg_, 
                                                url = details['name'], cancelButton=not majorVersion )
            if self.updateDialog.exec_() != QDialog.Accepted:
                self.getContextAll()
                
        else:
            self.getContextAll()
        
    def onGetTrReports(self, details):
        """
        """
        self.trace("on get reports")
        self.GetTrReports.emit( details )
        
    def onGetTrReviews(self, details):
        """
        """
        self.trace("on get reviews")
        self.GetTrReviews.emit(details["review"], details["xml-review"])        
        
    def onGetTrDesigns(self, details):
        """
        """
        self.trace("on get designs")
        self.GetTrDesigns.emit(details["design"], details["xml-design"])
        
    def onGetTrVerdicts(self, details):
        """
        """
        self.trace("on get verdicts")
        self.GetTrVerdicts.emit(details["verdict"], details["xml-verdict"])        
        
    def onGetTrImage(self, details):
        """
        """
        self.trace("on get image")
        self.GetTrImage.emit( details['image'] )
        
    def onGetTrRemoved(self, details):
        """
        """
        self.trace("on test result removed")
        self.refreshTr(partialRefresh=True, projectId=details['project-id'] )
    
    def onGetTrListing(self, details):
        """
        """
        self.trace("on test result listing")
        self.RefreshResults.emit(details["listing"])
    
    def onGetTrReseted(self, details):
        """
        """
        self.trace("on test result reseted")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="The repository is now empty!")
        else:
            self.InformationMsg.emit( self.tr("Empty remote repository") , self.tr("The repository is now empty!") )
    
        self.refreshTr(projectId=details['project-id'], partialRefresh=True)
        
    def onGetTrDownloaded(self, details):
        """
        """
        self.trace("on download test result")
        content = base64.b64decode(details["result"])

        if details["save-as"]:
            fileName = base64.b64decode(details['save-as-name'])
            fileName = fileName.decode("utf8")
        else:
            fileName = "%s//ResultLogs//%s.%s" % (QtHelper.dirExec(), 
                                                  details["result-name"],
                                                  details["result-extension"])

        # writing file
        f = open( fileName, 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        if not details["save-as"]:
            self.OpenTestResult.emit( (fileName, details["result-name"]) )
        else:
            if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                self.application().showMessageTray(msg="Download terminated!")
            else:                    
                self.InformationMsg.emit( title=self.tr("Download Test Result"), 
                                          err= self.tr("Download terminated!" ) )
                       
    def onGetTrZipped(self, details):
        """
        """
        self.trace("on test result zipped")
        
        self.InformationMsg.emit( self.tr("Zip test results") , self.tr("Test results zipped!") )
    
    def onGetTrUncomplete(self, details):
        """
        """
        self.trace("on download partial test result")
        
        content = base64.b64decode(details["result"])
        fileName = "%s//ResultLogs//%s.%s" % (QtHelper.dirExec(), 
                                              details["result-name"],
                                              details["result-extension"])


        # writing file
        f = open( fileName, 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        self.OpenTestResult.emit( (fileName, details["result-name"]) )

    def onCommentAdded(self, details):
        """
        """
        self.trace("on comment added")
        self.CommentTrAdded.emit( details["comments"] )
        
    def onCommentsDeleted(self, details):
        """
        """
        self.trace("on comments deleted")
        self.CommentsTrDeleted.emit()
        
    def onTasksReplayed(self, details):
        """
        """
        self.trace("on tasks replayed")

    def onTasksDesign(self, details):
        """
        """
        self.trace("on tasks design")
        self.GetTrDesigns.emit(details["design"], details["xml-design"]) 
        
    def onTasksVerdict(self, details):
        """
        """
        self.trace("on tasks verdict")
        self.GetTrVerdicts.emit(details["verdict"], details["xml-verdict"])
        
    def onTasksReview(self, details):
        """
        """
        self.trace("on tasks review")
        self.GetTrReviews.emit(details["review"], details["xml-review"])        
        
    def onTasksComment(self, details):
        """
        """
        self.trace("on tasks comment")
        self.InformationMsg.emit( self.tr("Task comment") , self.tr("Comment added!") )
        
    def onTasksKill(self, details):
        """
        """
        self.trace("on task killed")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="Test(s) killed!")
        else:
            self.WarningMsg.emit( self.tr("Kill test") , self.tr("The test is stopped!") )
        
        self.TestKilled.emit(details['task-id'])
        
    def onTasksKillAll(self, details):
        """
        """
        self.trace("on task killed")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="All test(s) killed!")
        else:
            self.WarningMsg.emit( self.tr("Kill tests") , self.tr("All tests are stopped!") )
        
        self.TestsKilled.emit()
        
    def onTasksKillSelective(self, details):
        """
        """
        self.trace("on task killed")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="All test(s) killed!")
        else:
            self.WarningMsg.emit( self.tr("Kill tests") , self.tr("All tests are stopped!") )
        
        self.TestsKilled.emit()
        
    def onTasksCancel(self, details):
        """
        """
        self.trace("on task cancelled")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="Test(s) cancelled!")
        else:
            self.WarningMsg.emit( self.tr("Kill test") , self.tr("The test is cancelled!") )
        
        self.TestCancelled.emit()
        
    def onTasksCancelAll(self, details):
        """
        """
        self.trace("on task cancelled")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="All test(s) cancelled!")
        else:
            self.WarningMsg.emit( self.tr("Kill tests") , self.tr("All tests are cancelled!") )
        
    def onTasksCancelSelective(self, details):
        """
        """
        self.trace("on task cancelled")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="All test(s) cancelled!")
        else:
            self.WarningMsg.emit( self.tr("Kill tests") , self.tr("All tests are cancelled!") )
    
    def onMetricsReset(self, details):
        """
        """
        self.trace("on tests metrics reseted")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.ResetStatistics.emit()
            self.application().showMessageWarningTray(msg="Statistics are reseted!")
        else:
            self.InformationMsg.emit( self.tr("Reset statistics") , self.tr("Statistics are reseted!") )
        
    def onMetricsTestsDurationWriting(self, details):
        """
        """
        self.trace("on tests metrics duration writing added")
        
    def onSessionContext(self, details):
        """
        """
        self.trace("on session context")
        
        self.RefreshContext.emit(details["context"])
    
    def onSystemUsages(self, details):
        """
        """
        self.trace("on system usages")

        self.RefreshUsages.emit(details["usages"])
        
    def onBuildDocumentations(self, details):
        """
        """
        self.trace("on build documentations")
        
        if details["build"]:
            details = "Generation done!"
            self.InformationMsg.emit( "Generate documentations", details )
            
            self.cacheDocs()
        else:
            details =  "Unable to generate cache.\n\nFix the following error: %s" % details['details']
            details += "\nIf the problem persists contact your administrator." 
            self.CriticalMsg.emit( "Generate documentations", details)
        
    def onCacheDocumentations(self, details):
        """
        """
        self.trace("on build documentations")
        
        self.RefreshHelper.emit(details["cache"])
        
    def onUnlockTests(self, details):
        """
        """
        self.trace("on unlock tests")
        self.WarningMsg.emit( self.tr("Unlock all files") , self.tr("All tests unlocked") )
        
    def onUnlockAdapters(self, details):
        """
        """
        self.trace("on unlock adapters")
        self.WarningMsg.emit( self.tr("Unlock all files") , self.tr("All adapters unlocked") )
        
    def onUnlockLibraries(self, details):
        """
        """
        self.trace("on unlock libraries")
        self.WarningMsg.emit( self.tr("Unlock all files") , self.tr("All libraries unlocked") )
        
    def onBuildTestsSamples(self, details):
        """
        """
        self.trace("on build tests samples")
        self.InformationMsg.emit( self.tr("Generate tests samples") , self.tr("Build done!") )
        
    def onBuildAdapters(self, details):
        """
        """
        self.trace("on build adapters")
        self.InformationMsg.emit( self.tr("Generate adapters") , self.tr("Build done!") )
        
    def onBuildLibraries(self, details):
        """
        """
        self.trace("on build libraries")
        self.InformationMsg.emit( self.tr("Generate libraries") , self.tr("Build done!") )
        
    def onRunningTasks(self, details):
        """
        """
        self.trace("on running tasks")
        self.TasksRunning.emit( details["tasks-running"] )
        
    def onWaitingTasks(self, details):
        """
        """
        self.trace("on waiting tasks")
        self.TasksWaiting.emit( details["tasks-waiting"] )
        
    def onHistoryTasks(self, details):
        """
        """
        self.trace("on history tasks")
        self.TasksHistory.emit( details["tasks-history"] )
        
    def onHistoryTasksAll(self, details):
        """
        """
        self.trace("on history all tasks")
        self.TasksHistory.emit( details["tasks-history"] )
        
    def onClearHistory(self, details):
        """
        """
        self.trace("on history cleared")
        self.TasksHistoryCleared.emit()
        
    def onTaskReschedule(self, details):
        """
        """
        self.trace("on task schedule")
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageWarningTray(msg="Test(s) rescheduled!")
        else:
            self.InformationMsg.emit( self.tr("Re-schedule test execution") , self.tr("Test execution rescheduled!") )
    
        self.TestRescheduled.emit()
       
    def onProbesRunning(self, details):
        """
        """
        self.trace("on probes running")
        self.RefreshRunningProbes.emit(details['probes'])
        
    def onAgentsRunning(self, details):
        """
        """
        self.trace("on agents running")
        self.RefreshRunningAgents.emit(details['agents'])
       
    def onProbesDefault(self, details):
        """
        """
        self.trace("on probes default")
        self.RefreshDefaultProbes.emit(details['probes'])
        
    def onAgentsDefault(self, details):
        """
        """
        self.trace("on agents default")
        self.RefreshDefaultAgents.emit(details['agents'])
        
    def onSyntaxAllAdapters(self, details):
        """
        """
        self.trace("on syntax adapters")
        if details['syntax-status']:
            self.InformationMsg.emit( self.tr("Check syntax"), 
                                      "%s\n%s" % (self.tr("Well done!"), "No syntax error detected.") )
        else:
            self.CriticalMsg.emit( self.tr("Check syntax"), details['syntax-error'] )
        
    def onSyntaxAllLibraries(self, details):
        """
        """
        self.trace("on syntax libraries")
        if details['syntax-status']:
            self.InformationMsg.emit( self.tr("Check syntax"), 
                                      "%s\n%s" % (self.tr("Well done!"), "No syntax error detected.") )
        else:
            self.CriticalMsg.emit( self.tr("Check syntax"), details['syntax-error'] )
    
    def onSyntaxAdapter(self, details):
        """
        """
        if details["success"]:
            self.InformationMsg.emit( self.tr("Check syntax"), 
                                      "%s\n%s" % ( self.tr("Well done!"), "No syntax error detected.") )
        else:
            msg = "An error exists on this file."
            msg += "\n%s" % details["syntax-error"]
            self.CriticalMsg.emit( self.tr("Check syntax"), msg )
        
    def onSyntaxLibrary(self, details):
        """
        """
        if details["success"]:
            self.InformationMsg.emit( self.tr("Check syntax"), 
                                      "%s\n%s" % ( self.tr("Well done!"), "No syntax error detected.") )
        else:
            msg = "An error exists on this file."
            msg += "\n%s" % details["syntax-error"]
            self.CriticalMsg.emit( self.tr("Check syntax"), msg )
            
    def onGenericAdapters(self, details):
        """
        """
        self.trace("on generic adapters")
        self.InformationMsg.emit( self.tr("Set the generic package of adapters") ,
                                  self.tr("Package adapters configured successfully as generic!") )
        self.sessionContext()
                
    def onGenericLibraries(self, details):
        """
        """
        self.trace("on generic libraries")
        self.InformationMsg.emit( self.tr("Set the generic library of adapters") ,
                                  self.tr("Package libraries configured successfully as generic!") )
        self.sessionContext()
        
    def onDefaultAdapters(self, details):
        """
        """
        self.trace("on default adapters")
        self.InformationMsg.emit( self.tr("Set the default package of adapters") ,
                                  self.tr("Package adapters configured successfully as default!") )
        self.sessionContext()
        
    def onDefaultLibraries(self, details):
        """
        """
        self.trace("on default libraries")
        self.InformationMsg.emit( self.tr("Set the default package of libraries") , 
                                  self.tr("Package libraries configured succesfully as default!") )
        self.sessionContext()
        
    def onBackupTests(self, details):   
        """
        """
        self.trace("on backup tests")
        self.InformationMsg.emit( "Backup", "Backup created with success!" )
        
    def onBackupResults(self, details):   
        """
        """
        self.trace("on backup results")
        self.InformationMsg.emit( "Backup", "Backup created with success!" )
        
    def onBackupAdapters(self, details):   
        """
        """
        self.trace("on backup adapters")
        self.InformationMsg.emit( "Backup", "Backup created with success!" )
        
    def onBackupLibraries(self, details):   
        """
        """
        self.trace("on backup libraries")
        self.InformationMsg.emit( "Backup", "Backup created with success!" )
        
    def onRemoveBackupsResults(self, details):
        """
        """
        self.trace("on remove all backups results")
        self.InformationMsg.emit( "Delete backups", "All backups deleted with success!" )
        
    def onRemoveBackupsTests(self, details):
        """
        """
        self.trace("on remove all backups tests")
        self.InformationMsg.emit( "Delete backups", "All backups deleted with success!" )
        
    def onRemoveBackupsAdapters(self, details):
        """
        """
        self.trace("on remove all backups adapters")
        self.InformationMsg.emit( "Delete backups", "All backups deleted with success!" )
        
    def onRemoveBackupsLibraries(self, details):
        """
        """
        self.trace("on remove all backups libraries") 
        self.InformationMsg.emit( "Delete backups", "All backups deleted with success!" )
    
    def onDownloadBackupResults(self, details):
        """
        """
        self.trace("on download backup from results") 
        
        # decode data file
        content = base64.b64decode(details['backup'])

        # writing file
        f = open( details['dest-name'], 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Download terminated!")
        else:
            self.InformationMsg.emit( title=self.tr("Download Backup"), 
                                      err= self.tr("Download terminated!" ) )
    
    def onDownloadBackupTests(self, details):
        """
        """
        self.trace("on download backup from tests") 
        
        # decode data file
        content = base64.b64decode(details['backup'])

        # writing file
        f = open( details['dest-name'], 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Download terminated!")
        else:
            self.InformationMsg.emit( title=self.tr("Download Backup"), 
                                      err= self.tr("Download terminated!" ) )
    
    def onDownloadBackupAdapters(self, details):
        """
        """
        self.trace("on download backup from adapters") 
        
        # decode data file
        content = base64.b64decode(details['backup'])

        # writing file
        f = open( details['dest-name'], 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Download terminated!")
        else:
            self.InformationMsg.emit( title=self.tr("Download Backup"), 
                                      err= self.tr("Download terminated!" ) )
    
    def onDownloadBackupLibraries(self, details):
        """
        """
        self.trace("on download backup from libraries") 
        
        # decode data file
        content = base64.b64decode(details['backup'])

        # writing file
        f = open( details['dest-name'], 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Download terminated!")
        else:
            self.InformationMsg.emit( title=self.tr("Download Backup"), 
                                      err= self.tr("Download terminated!" ) )
         
    def onResetTests(self, details):
        """
        """
        self.trace("on reset tests") 
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="The tests repository is now empty!")
        else:
            self.InformationMsg.emit( self.tr("Empty remote tests repository") , 
                                      self.tr("The tests repository is now empty!") )
            
    def onResetAdapters(self, details):
        """
        """
        self.trace("on reset adapters") 
        self.InformationMsg.emit( self.tr("Uninstall adapters") , self.tr("Uninstallation successfull!") )
        
    def onResetLibraries(self, details):
        """
        """
        self.trace("on reset libraries") 
        self.InformationMsg.emit( self.tr("Uninstall libraries") , 
                                  self.tr("Uninstallation successfull!") )
        
    def onStatisticsResults(self, details):
        """
        """
        self.trace("on statistics results")
        self.RefreshStatsResults.emit(details['statistics'])
        
    def onStatisticsAdapters(self, details):
        """
        """
        self.trace("on statistics adapters")
        self.RefreshStatsAdapters.emit(details['statistics'])
        
    def onStatisticsLibraries(self, details):
        """
        """
        self.trace("on statistics libraries")
        self.RefreshStatsLibraries.emit(details['statistics'])
        
    def onStatisticsTests(self, details):
        """
        """
        self.trace("on statistics tests")
        self.RefreshStatsTests.emit(details['statistics'])
       
    def onAgentsDisconnect(self, details):
        """
        """
        self.trace("on agents disconnect")
        self.InformationMsg.emit( "Stop agent" , "Agent stopped!" )
        
    def onProbesDisconnect(self, details):
        """
        """
        self.trace("on probes disconnect")
        self.InformationMsg.emit( "Stop probe" , "Probe stopped!" )
       
    def onAgentsConnect(self, details):
        """
        """
        self.trace("on agents connect")
        self.InformationMsg.emit( 'Starting agent' , "Agent started!" )
        
    def onProbesConnect(self, details):
        """
        """
        self.trace("on probes connect")
        self.InformationMsg.emit( 'Starting probe' , "Probes started!" )
       
    def onAgentsAdd(self, details):
        """
        """
        self.trace("on agents add")
        self.InformationMsg.emit( "Add default agent" , "Default agent added!" )
        
    def onProbesAdd(self, details):
        """
        """
        self.trace("on probes add")
        self.InformationMsg.emit( "Add default probe" , "Default probe added!" )
       
    def onAgentsRemove(self, details):
        """
        """
        self.trace("on agents remove")
        self.InformationMsg.emit( "Delete default agent" , "Default agent deleted!" )
        
    def onProbesRemove(self, details):
        """
        """
        self.trace("on probes add")
        self.InformationMsg.emit( "Delete default probe" , "Default probe deleted!" )
        
    def onClientAvailable(self, details):
        """
        """
        self.trace("on client available")
        
        if not details["client-available"]:
            if details["recheck"]:
                self.updateTimer.stop()
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Update/enable' ) ):
                    self.updateTimer.start( int(Settings.instance().readValue( key = 'Update/retry' )) )
            else:
                self.InformationMsg.emit( self.tr("Check for update") , self.tr("No update available") )
        else:
            # a new client is available
            majorVersion = False
            typeVersion = "minor"
            
            # convert current version to tuple
            currentMajor, currentMinor, currentFix =  self.clientVersion.split(".")
            currentVersion = (int(currentMajor), int(currentMinor), int(currentFix)) 
            
            # convert new version to tuple
            newMajor, newMinor, newFix =  details["version"].split(".")
            newVersion = (int(newMajor), int(newMinor), int(newFix))
            
            # and compare it
            if int(newMajor) >  int(currentMajor):
                majorVersion = True
                typeVersion = "major"
                
            msg_ = "%s" % self.tr("A newer %s version of this client is available." % typeVersion)
            if majorVersion:
                msg_ += "\nYou must click on download button and install the update."
            else:
                msg_ += "\nYou may click on download button and install the update."
            msg_ += "\n\nVersion %s" % details["version"]
            

            self.updateDialog.setDownload( title = self.tr("Update available"), 
                                           txt = msg_, 
                                           url = details['name'] )
            self.updateDialog.exec_()

    def onClientDownload(self, details):
        """
        """
        self.trace("on client downloaded")
  
        # decode data file
        content = base64.b64decode( details["client-binary" ] )
        fileName = "%s//Update//%s" % (QtHelper.dirExec(), details["client-name" ] )
         
        # writing file
        f = open( fileName, 'wb')
        f.write( content )
        f.close()
        
        # remove unneeded data
        del content

        settingsBackup = "%s//Update//backup_settings.ini" % QtHelper.dirExec()
        #remove client settings
        backupFile = QFile( settingsBackup )
        backupFile.remove()

        #copy current settings
        currentSettingsFile = QFile("%s//Files//settings.ini" % QtHelper.dirExec() )
        ret = currentSettingsFile.copy(settingsBackup)
        if not ret:  self.error( 'update: unable to copy settings files' )

        #inform user
        msg = "Download finished\n"
        msg += "Go in the Start Menu /%s" % Settings.instance().readValue( key = 'Common/name' )
        msg += "/Update/ and  execute the package." 
        self.InformationMsg.emit( self.tr("Download"), self.tr( msg )  )
                               
        # open the update folder
        if sys.platform == "win32":
            updatePath =  '"%s\\Update\\"' % QtHelper.dirExec()
            subprocess.call ('explorer.exe %s' % updatePath, shell=True)

        self.application().close()

    def onSessionContextAll(self, details):
        """
        """
        self.trace("on session context all")
  
        self.Connected.emit( details )
        
    def onTestsFileMoved(self, details):
        """
        """
        self.trace("on test file moved")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFolderMoved(self, details):
        """
        """
        self.trace("on test folder moved")
   
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFileRenamed(self, details):
        """
        """
        self.trace("on test file renamed")

        self.FileTestsRenamed.emit( details["project-id"], 
                                    details["file-path"], 
                                    details["file-name"],
                                    details["file-extension"],
                                    details["new-file-name"] )
                                    
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFolderRenamed(self, details):
        """
        """
        self.trace("on test folder renamed")
        
        self.FolderTestsRenamed.emit(details["project-id"], 
                                     details["directory-path"],
                                     details["directory-name"], 
                                     details["new-directory-name"] )
                                         
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFileDuplicated(self, details):
        """
        """
        self.trace("on test file duplicated")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFolderDuplicated(self, details):
        """
        """
        self.trace("on test folder duplicated")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFileRemoved(self, details):
        """
        """
        self.trace("on test file removed")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFolderRemoved(self, details):
        """
        """
        self.trace("on test folder removed")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFoldersRemoved(self, details):
        """
        """
        self.trace("on test folders removed")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFolderAdded(self, details):
        """
        """
        self.trace("on test folder added")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsListing(self, details):
        """
        """
        self.trace("on tests listing")

        self.RefreshTestsRepo.emit(details["listing"], 
                                   details["project-id"],
                                   details["for-saveas"],
                                   details["for-runs"])
        
    def onAdaptersListing(self, details):
        """
        """
        self.trace("on adapters listing")
        
        self.RefreshAdaptersRepo.emit(details["adapters-listing"])
        
    def onLibrariesListing(self, details):
        """
        """
        self.trace("on libraries listing")
        
        self.RefreshLibrariesRepo.emit(details["libraries-listing"])
        
    def onAdaptersFileMoved(self, details):
        """
        """
        self.trace("on adapter file moved")
        
        self.listingAdapters()
        
    def onAdaptersFolderMoved(self, details):
        """
        """
        self.trace("on adapter folder moved")
   
        self.listingAdapters()
        
    def onAdaptersFileRenamed(self, details):
        """
        """
        self.trace("on adapter file renamed")

        self.FileAdaptersRenamed.emit(details["file-path"], 
                                      details["file-name"],
                                      details["file-extension"],
                                      details["new-file-name"] )
        self.listingAdapters()
        
    def onAdaptersFolderRenamed(self, details):
        """
        """
        self.trace("on adapter folder renamed")
        
        self.FolderAdaptersRenamed.emit( details["directory-name"], 
                                         details["directory-path"],
                                         details["new-directory-name"] )
                                         
        self.listingAdapters()
        
    def onAdaptersFileDuplicated(self, details):
        """
        """
        self.trace("on adapter file duplicated")
        
        self.listingAdapters()
        
    def onAdaptersFolderDuplicated(self, details):
        """
        """
        self.trace("on adapter folder duplicated")
        
        self.listingAdapters()
        
    def onAdaptersFileRemoved(self, details):
        """
        """
        self.trace("on adapter file removed")
        
        self.listingAdapters()
        
    def onAdaptersFolderRemoved(self, details):
        """
        """
        self.trace("on adapter folder removed")

        self.listingAdapters()

    def onAdaptersFoldersRemoved(self, details):
        """
        """
        self.trace("on adapter folders removed")

        self.listingAdapters()
        
    def onAdaptersFolderAdded(self, details):
        """
        """
        self.trace("on adapter folder added")
        
        self.listingAdapters()
        
    def onLibrariesFileMoved(self, details):
        """
        """
        self.trace("on library file moved")
        
        self.listingLibraries()
        
    def onLibrariesFolderMoved(self, details):
        """
        """
        self.trace("on library folder moved")
   
        self.listingLibraries()
        
    def onLibrariesFileRenamed(self, details):
        """
        """
        self.trace("on library file renamed")

        self.FileLibrariesRenamed.emit( details["file-path"], 
                                        details["file-name"],
                                        details["file-extension"],
                                        details["new-file-name"] )
                                         
        self.listingLibraries()
        
    def onLibrariesFolderRenamed(self, details):
        """
        """
        self.trace("on library folder renamed")
        
        self.FolderLibrariesRenamed.emit(details["directory-name"], 
                                         details["directory-path"],
                                         details["new-directory-name"] )
        
        self.listingLibraries()
        
    def onLibrariesFileDuplicated(self, details):
        """
        """
        self.trace("on library file duplicated")
        
        self.listingLibraries()
        
    def onLibrariesFolderDuplicated(self, details):
        """
        """
        self.trace("on library folder duplicated")
        
        self.listingLibraries()
        
    def onLibrariesFileRemoved(self, details):
        """
        """
        self.trace("on library file removed")
        
        self.listingLibraries()
        
    def onLibrariesFolderRemoved(self, details):
        """
        """
        self.trace("on library folder removed")

        self.listingLibraries()

    def onLibrariesFoldersRemoved(self, details):
        """
        """
        self.trace("on library folders removed")

        self.listingLibraries()
          
    def onLibrariesFolderAdded(self, details):
        """
        """
        self.trace("on library folder added")
        
        self.listingLibraries()
        
    def onTestsSnapshotAdded(self, details):
        """
        """
        self.trace("on snapshot added")
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsSnapshotRestored(self, details):
        """
        """
        self.trace("on snapshot added")
        
        self.listingTests(projectId=details["project-id"])
        self.InformationMsg.emit( self.tr("Restore snapshot") , self.tr("Snapshot restored") )
        
    def onTestsSnapshotRemoved(self, details):
        """
        """
        self.trace("on snapshot removed") 
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsSnapshotRemovedAll(self, details):
        """
        """
        self.trace("on snapshot removed all") 
        
        self.listingTests(projectId=details["project-id"])
        
    def onTestsFileOpened(self, details):
        """
        """
        self.trace("on tests file opened") 
        if details["destination-id"] is not None and details["action-id"] is not None:
            self.GetFileRepo.emit( details["file-path"], 
                                   details["file-name"], 
                                   details["file-extension"], 
                                   details["file-content"],
                                   details["project-id"], 
                                   details["destination-id"], 
                                   details["action-id"],
                                   details["custom-param"] )
        else:
            self.OpenTestFile.emit( details["file-path"],
                                    details["file-name"],
                                    details["file-extension"],
                                    details["file-content"],
                                    details["project-id"],
                                    details["locked"],
                                    details["locked-by"] )
        
    def onTestsFileUploaded(self, details):
        """
        """
        self.trace("on tests file uploaded")
        
        lockedBy = base64.b64decode(details["locked-by"])
        if sys.version_info > (3,): # python3 support
            lockedBy = lockedBy.decode("utf8")
            
        if details["code"] == CODE_OK:
            if details["locked"] and lockedBy != self.__login:
                msg = "This file is locked by the user %s\nUnable to save the file!" %  lockedBy
                self.WarningMsg.emit( "File locked" , msg  )
            else:
                self.FileTestsUploaded.emit( details["file-path"],
                                             details["file-name"], 
                                             details["file-extension"],
                                             details["project-id"],
                                             details["overwrite"],
                                             details["close-after"] )
                if not details["overwrite"]:
                    self.listingTests(projectId=details["project-id"])
        elif details["code"] == CODE_ALLREADY_EXISTS:  
            self.WarningMsg.emit( "Save file" , "This filename already exist!" )
            
            self.FileTestsUploadError.emit( details["file-path"],
                                             details["file-name"], 
                                             details["file-extension"],
                                             details["project-id"],
                                             details["overwrite"],
                                             details["close-after"] )
        else:
            self.CriticalMsg.emit( "Save file" , 
                                   "Unable to save the file.\nError Num=%s" % details["code"])
            
            self.FileTestsUploadError.emit( details["file-path"],
                                             details["file-name"], 
                                             details["file-extension"],
                                             details["project-id"],
                                             details["overwrite"],
                                             details["close-after"] )
                                             
    def onAdaptersFileOpened(self, details):
        """
        """
        self.trace("on adapters file opened") 
        
        self.OpenAdapterFile.emit(  details["file-path"],
                                    details["file-name"],
                                    details["file-extension"],
                                    details["file-content"],
                                    details["locked"],
                                    details["locked-by"])
                                
    def onAdaptersFileUploaded(self, details):
        """
        """
        self.trace("on adapters file uploaded") 
        
        lockedBy = base64.b64decode(details["locked-by"])
        if sys.version_info > (3,): # python3 support
            lockedBy = lockedBy.decode("utf8")
            
        if details["code"] == CODE_OK:
            if details["locked"] and lockedBy != self.__login:
                msg = "This file is locked by the user %s\nUnable to save the file!" %  lockedBy
                self.WarningMsg.emit( "File locked" , msg  )
            else:
                self.FileAdaptersUploaded.emit( details["file-path"],
                                                details["file-name"], 
                                                details["file-extension"],
                                                details["overwrite"],
                                                details["close-after"] )
                if not details["overwrite"]:
                    self.listingAdapters()
        elif details["code"] == CODE_ALLREADY_EXISTS:  
            self.WarningMsg.emit( "Save file" , "This filename already exist!" )
            
            self.FileAdaptersUploadError.emit( details["file-path"],
                                                details["file-name"], 
                                                details["file-extension"],
                                                details["overwrite"],
                                                details["close-after"] )
        else:
            self.CriticalMsg.emit( "Save file" , "Unable to save the file.\nError Num=%s" % details["code"])
            
            self.FileAdaptersUploadError.emit( details["file-path"],
                                                details["file-name"], 
                                                details["file-extension"],
                                                details["overwrite"],
                                                details["close-after"] )
            
    def onLibrariesFileOpened(self, details):
        """
        """
        self.trace("on libraries file opened") 
        
        self.OpenLibraryFile.emit(  details["file-path"],
                                    details["file-name"],
                                    details["file-extension"],
                                    details["file-content"],
                                    details["locked"],
                                    details["locked-by"])
                                    
    def onLibrariesFileUploaded(self, details):
        """
        """
        self.trace("on libraries file uploaded") 
        
        lockedBy = base64.b64decode(details["locked-by"])
        if sys.version_info > (3,): # python3 support
            lockedBy = lockedBy.decode("utf8")
            
        if details["code"] == CODE_OK:
            if details["locked"] and lockedBy != self.__login:
                msg = "This file is locked by the user %s\nUnable to save the file!" %  lockedBy
                self.WarningMsg.emit( "File locked" , msg  )
            else:
                self.FileLibrariesUploaded.emit(details["file-path"],
                                                details["file-name"], 
                                                details["file-extension"],
                                                details["overwrite"],
                                                details["close-after"])
            
                if not details["overwrite"]:
                    self.listingLibraries()
        elif details["code"] == CODE_ALLREADY_EXISTS:  
            self.WarningMsg.emit( "Save file" , "This filename already exist!" )
            self.FileLibrariesUploadError.emit(details["file-path"],
                                                details["file-name"], 
                                                details["file-extension"],
                                                details["overwrite"],
                                                details["close-after"])
        else:
            self.CriticalMsg.emit( "Save file" , "Unable to save the file.\nError Num=%s" % details["code"])
            
            self.FileLibrariesUploadError.emit(details["file-path"],
                                                details["file-name"], 
                                                details["file-extension"],
                                                details["overwrite"],
                                                details["close-after"])
            
    def onAdaptersFileUnlocked(self, details):
        """
        """
        self.trace("on adapters file unlocked") 
        
    def onLibrariesFileUnlocked(self, details):
        """
        """
        self.trace("on libraries file unlocked") 
        
    def onTestsFileUnlocked(self, details):
        """
        """
        self.trace("on tests file unlocked") 
        
    def onAdaptersPackageAdded(self, details):
        """
        """
        self.trace("on adapters package added") 
        
        self.listingAdapters()
        
    def onLibrariesPackageAdded(self, details):
        """
        """
        self.trace("on libraries package added") 
        
        self.listingLibraries()
        
    def onLibrariesLibraryAdded(self, details):
        """
        """
        self.trace("on library added") 
        
        self.listingLibraries()
        
    def onAdaptersAdapterAdded(self, details):
        """
        """
        self.trace("on adapter added") 
        
        self.listingAdapters()
        
    def onAdaptersAdapterWsdlUrlAdded(self, details):
        """
        """
        self.trace("on adapter added from wsdl url")
        
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Adapter generated successfully!")
        else:
            self.InformationMsg.emit( self.tr("Adapter generator") , 
                                      self.tr("Adapter generated successfully!") )
                                    
        self.listingAdapters()   
        
    def onAdaptersAdapterWsdlFileAdded(self, details):
        """
        """
        self.trace("on adapter added from wsdl file") 
        
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Adapter generated successfully!")
        else:
            self.InformationMsg.emit( self.tr("Adapter generator") , 
                                      self.tr("Adapter generated successfully!") )
                                      
        self.listingAdapters()
        
    def onTestsDefaultAll(self, details):
        """
        """
        self.trace("on default all tests") 
        
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="All tests are updated!")
        else:
            self.InformationMsg.emit( self.tr("Set default version"), 
                                      self.tr("All tests are updated!" ) )
          
    def onTestsCheckSyntax(self, details):
        """
        """
        self.trace("on check test syntax")
        
        if details["status"]:
            self.InformationMsg.emit( self.tr("Check syntax") , 
                                      "%s\n%s" % ( self.tr("Well done!"), 
                                                   self.tr("No syntax error detected in your test.") ) )
        else:
            msg = self.tr("An error exists on this test.")
            msg += "\n%s" % details["error-msg"]
            self.WarningMsg.emit( self.tr("Check syntax") , msg )
            
    def onTestsCreateDesign(self, details):
        """
        """
        self.trace("on create test design")
        
        if details["error"]:
            if details["error-msg"] == "Syntax":
                msg = "Unable to prepare the design of the test!\n"
                msg += "Syntax error detected in this test!"
                self.WarningMsg.emit( "Test Design", msg )
            else:
                self.WarningMsg.emit( "Test Design", 
                                      "Unable to prepare the design!" )
        else:
            self.GetTrDesigns.emit(details["design"], details["xml-design"])
            
    def onTestsScheduled(self, details):
        """
        """
        self.trace("on tests scheduled")
        
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
            self.application().showMessageTray(msg="Group of test(s) enqueued to run.")
        else:
            self.InformationMsg.emit( self.tr("Tests Execution") , 
                                      self.tr("Group of test(s) enqueued to run.") )
            
    def onTestScheduled(self, details):
        """
        """
        self.trace("on test scheduled")

        if details["message"] in [ "background", "recursive-background", 
                                   "postponed-background", "successive-background" ]:
            TestResults.instance().delWidgetTest( testId = details["tab-id"] )
            if details["message"] == "successive-background":  
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Your test is running several time in background.")
                else:
                    self.InformationMsg.emit( self.tr("Test Execution") ,
                                              self.tr("Your test is running several time in background.") )
                                              
            elif details["message"] == "recursive-background":
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Recursive test execution scheduled!")
                else:
                    self.InformationMsg.emit( self.tr("Test Execution") , 
                                              self.tr('Recursive test execution scheduled!') )
                                              
            elif details["message"] == "postponed-background":
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Test execution postponed!")
                else:
                    self.InformationMsg.emit( self.tr("Test Execution") , 
                                              self.tr('Test execution postponed!') )
                                              
            elif details["message"] == "background":
                if QtHelper.str2bool( Settings.instance().readValue( key = 'Common/systray-notifications' ) ):
                    self.application().showMessageTray(msg="Your test is running in background.")
                else:
                    self.InformationMsg.emit( self.tr("Test Execution") , 
                                              self.tr("Your test is running in background.") )
                                              
        else:
            wTest = TestResults.instance().getWidgetTest( testId = details["tab-id"] )
            wTest.name = '[%s] %s' % (details["task-id"], details["test-name"])
            wTest.TID = details["task-id"]
            if wTest is not None:
                self.AddTestTab.emit( wTest )
                        
RCI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return RCI

def initialize (parent, clientVersion):
    """
    Initialize the class

    @param parent:
    @type: parent:

    @param clientVersion:
    @type: clientVersion:
    """
    global RCI
    RCI = RestClientInterface(parent, clientVersion)

def finalize ():
    """
    Destroy Singleton
    """
    global RCI
    if RCI:
        RCI.refreshTimer.stop()
        del RCI
        RCI = None