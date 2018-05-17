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

from pycnic.core import WSGI
from pycnic.errors import HTTP_401, HTTP_400, HTTP_500, HTTP_403, HTTP_404

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler

import threading
import logging
import sys
import wrapt

from Libs import Settings, Logger

try:
    import RestTesterFunctions
    import RestAdminFunctions
    import RestCommonFunctions
except ImportError: # python3 support
    from . import RestTesterFunctions
    from . import RestAdminFunctions
    from . import RestCommonFunctions

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
Logger
"""
class _NoLoggingWSGIRequestHandler(WSGIRequestHandler, Logger.ClassLogger):
    """
    """
    def log_message(self, format, *args):
        """
        """
        self.trace( "RSI - %s %s %s" % args )

if sys.version_info > (3,):
    _my_logger = None
else:
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
        ('/session/login',                              RestCommonFunctions.SessionLogin()),
        ('/session/logout',                             RestCommonFunctions.SessionLogout()),
        ('/session/refresh',                            RestCommonFunctions.SessionRefresh()),
        ('/session/context',                            RestCommonFunctions.SessionContext()),
        ('/session/context/notify',                     RestCommonFunctions.SessionContextNotify()),
        ('/session/context/all',                        RestCommonFunctions.SessionContextAll()),
        
        # agents
        ('/agents/running',                             RestTesterFunctions.AgentsRunning()),
        ('/agents/default',                             RestTesterFunctions.AgentsDefault()),
        ('/agents/disconnect',                          RestTesterFunctions.AgentsDisconnect()),
        ('/agents/connect',                             RestTesterFunctions.AgentsConnect()),
        ('/agents/add',                                 RestTesterFunctions.AgentsAdd()),
        ('/agents/remove',                              RestTesterFunctions.AgentsRemove()),
        
        # probes
        ('/probes/running',                             RestTesterFunctions.ProbesRunning()),
        ('/probes/default',                             RestTesterFunctions.ProbesDefault()),
        ('/probes/disconnect',                          RestTesterFunctions.ProbesDisconnect()),
        ('/probes/connect',                             RestTesterFunctions.ProbesConnect()),
        ('/probes/add',                                 RestTesterFunctions.ProbesAdd()),
        ('/probes/remove',                              RestTesterFunctions.ProbesRemove()),
        
        # tasks
        ('/tasks/running',                              RestCommonFunctions.TasksRunning()),
        ('/tasks/waiting',                              RestCommonFunctions.TasksWaiting()),
        ('/tasks/history',                              RestCommonFunctions.TasksHistory()),
        ('/tasks/history/all',                          RestCommonFunctions.TasksHistoryAll()),
        ('/tasks/cancel',                               RestCommonFunctions.TasksCancel()),
        ('/tasks/cancel/selective',                     RestCommonFunctions.TasksCancelSelective()),
        ('/tasks/cancel/all',                           RestAdminFunctions.TasksCancelAll()),
        ('/tasks/history/clear',                        RestAdminFunctions.TasksHistoryClear()),
        ('/tasks/replay',                               RestCommonFunctions.TasksReplay()),
        ('/tasks/verdict',                              RestCommonFunctions.TasksVerdict()),
        ('/tasks/review',                               RestCommonFunctions.TasksReview()),
        ('/tasks/design',                               RestCommonFunctions.TasksDesign()),
        ('/tasks/comment',                              RestCommonFunctions.TasksComment()),
        ('/tasks/kill',                                 RestCommonFunctions.TasksKill()),
        ('/tasks/kill/all',                             RestAdminFunctions.TasksKillAll()),
        ('/tasks/kill/selective',                       RestCommonFunctions.TasksKillSelective()),
        ('/tasks/reschedule',                           RestCommonFunctions.TasksReschedule()),
        
        # public storage
        ('/public/basic/listing',                       RestTesterFunctions.PublicListing()),
        ('/public/directory/add',                       RestTesterFunctions.PublicDirectoryAdd()),
        ('/public/directory/remove',                    RestTesterFunctions.PublicDirectoryRemove()),
        ('/public/directory/rename',                    RestTesterFunctions.PublicDirectoryRename()),
        ('/public/file/download',                       RestTesterFunctions.PublicDownload()),
        ('/public/file/import',                         RestTesterFunctions.PublicImport()),
        ('/public/file/remove',                         RestTesterFunctions.PublicRemove()),
        ('/public/file/rename',                         RestTesterFunctions.PublicRename()),
        
        # tests
        ('/tests/schedule',                             RestTesterFunctions.TestsSchedule()),
        ('/tests/schedule/tpg',                         RestTesterFunctions.TestsScheduleTpg()),
        ('/tests/schedule/group',                       RestTesterFunctions.TestsScheduleGroup()),
        ('/tests/basic/listing',                        RestTesterFunctions.TestsBasicListing()),
        ('/tests/listing',                              RestTesterFunctions.TestsListing()),
        ('/tests/statistics',                           RestAdminFunctions.TestsStatistics()),
        ('/tests/directory/add',                        RestTesterFunctions.TestsDirectoryAdd()),
        ('/tests/directory/remove',                     RestTesterFunctions.TestsDirectoryRemove()),
        ('/tests/directory/remove/all',                 RestAdminFunctions.TestsDirectoryRemoveAll()),
        ('/tests/directory/rename',                     RestTesterFunctions.TestsDirectoryRename()),
        ('/tests/directory/duplicate',                  RestTesterFunctions.TestsDirectoryDuplicate()),
        ('/tests/directory/move',                       RestTesterFunctions.TestsDirectoryMove()),
        ('/tests/file/download',                        RestTesterFunctions.TestsFileDownload()),
        ('/tests/file/open',                            RestTesterFunctions.TestsFileOpen()),
        ('/tests/file/upload',                          RestTesterFunctions.TestsFileUpload()),
        ('/tests/file/remove',                          RestTesterFunctions.TestsFileRemove()),
        ('/tests/file/rename',                          RestTesterFunctions.TestsFileRename()),
        ('/tests/file/duplicate',                       RestTesterFunctions.TestsFileDuplicate()),
        ('/tests/file/move',                            RestTesterFunctions.TestsFileMove()),
        ('/tests/file/default/all',                     RestAdminFunctions.TestsFileDefaultAll()),
        ('/tests/file/unlock/all',                      RestAdminFunctions.TestsFileUnlockAll()),
        ('/tests/file/unlock',                          RestTesterFunctions.TestsFileUnlock()),
        ('/tests/build/samples',                        RestAdminFunctions.TestsBuild()),
        ('/tests/backup',                               RestAdminFunctions.TestsBackup()),
        ('/tests/backup/listing',                       RestAdminFunctions.TestsBackupListing()),
        ('/tests/backup/download',                      RestAdminFunctions.TestsBackupDownload()),
        ('/tests/backup/remove/all',                    RestAdminFunctions.TestsBackupRemoveAll()),
        ('/tests/reset',                                RestAdminFunctions.TestsReset()),
        ('/tests/snapshot/add',                         RestTesterFunctions.TestsSnapshotAdd()),
        ('/tests/snapshot/restore',                     RestTesterFunctions.TestsSnapshotRestore()),
        ('/tests/snapshot/remove',                      RestTesterFunctions.TestsSnapshotRemove()),
        ('/tests/snapshot/remove/all',                  RestAdminFunctions.TestsSnapshotRemoveAll()),
        ('/tests/check/syntax',                         RestTesterFunctions.TestsCheckSyntax()),
        ('/tests/check/syntax/tpg',                     RestTesterFunctions.TestsCheckSyntaxTpg()),
        ('/tests/create/design',                        RestTesterFunctions.TestsCreateDesign()),
        ('/tests/create/design/tpg',                    RestTesterFunctions.TestsCreateDesignTpg()),

        # dbr13 >>>
        ('/tests/update/adapter-library',               RestTesterFunctions.TestsUpdateAdapterLibrary()),
        ('/tests/find/file-usage',                      RestTesterFunctions.TestsFindFileUsage()),
        # dbr13 <<<
        # variables
        ('/variables/listing',                          RestTesterFunctions.VariablesListing()),
        ('/variables/add',                              RestTesterFunctions.VariablesAdd()),
        ('/variables/update',                           RestTesterFunctions.VariablesUpdate()),
        ('/variables/remove',                           RestTesterFunctions.VariablesRemove()),
        ('/variables/duplicate',                        RestTesterFunctions.VariablesDuplicate()),
        ('/variables/reset',                            RestAdminFunctions.VariablesReset()),
        ('/variables/search/by/name',                   RestTesterFunctions.VariablesSearchByName()),
        ('/variables/search/by/id',                     RestTesterFunctions.VariablesSearchById()),

        # tests results storage
        ('/results/listing/files',                      RestTesterFunctions.ResultsListingFiles()),
        ('/results/listing/id/by/datetime',             RestTesterFunctions.ResultsListingIdByDateTime()),
        ('/results/reset',                              RestAdminFunctions.ResultsReset()),
        ('/results/remove/by/id',                       RestTesterFunctions.ResultsRemoveById()),
        ('/results/remove/by/date',                     RestTesterFunctions.ResultsRemoveByDate()),
        ('/results/follow',                             RestTesterFunctions.ResultsFollow()),
        ('/results/status',                             RestTesterFunctions.ResultsStatus()),
        ('/results/verdict',                            RestTesterFunctions.ResultsVerdict()),
        ('/results/report/verdicts',                    RestTesterFunctions.ResultsReportVerdicts()),
        ('/results/report/reviews',                     RestTesterFunctions.ResultsReportReviews()),
        ('/results/report/designs',                     RestTesterFunctions.ResultsReportDesigns()),
        ('/results/report/comments',                    RestTesterFunctions.ResultsReportComments()),
        ('/results/report/events',                      RestTesterFunctions.ResultsReportEvents()),
        ('/results/reports',                            RestTesterFunctions.ResultsReports()),
        ('/results/compress/zip',                       RestTesterFunctions.ResultsCompressZip()),
        ('/results/upload/file',                        RestTesterFunctions.ResultsUploadFile()),
        ('/results/download/image',                     RestTesterFunctions.ResultsDownloadImage()),
        ('/results/download/result',                    RestTesterFunctions.ResultsDownloadResult()),
        ('/results/download/uncomplete',                RestTesterFunctions.ResultsDownloadResultUncomplete()),
        ('/results/comment/add',                        RestTesterFunctions.ResultsCommentAdd()),
        ('/results/comments/remove',                    RestTesterFunctions.ResultsCommentsRemove()),
        ('/results/backup',                             RestAdminFunctions.ResultsBackup()),
        ('/results/backup/listing',                     RestAdminFunctions.ResultsBackupListing()),
        ('/results/backup/download',                    RestAdminFunctions.ResultsBackupDownload()),
        ('/results/backup/remove/all',                  RestAdminFunctions.ResultsBackupRemoveAll()),
        ('/results/statistics',                         RestAdminFunctions.ResultsStatistics()),
        
        # metrics for test 
        ('/metrics/tests/reset',                        RestAdminFunctions.MetricsTestsReset()),
        ('/metrics/tests/duration/writing',             RestTesterFunctions.MetricsTestsWritingDuration()),
        
        # adapters
        ( '/adapters/statistics',                       RestAdminFunctions.AdaptersStatistics()),
        ( '/adapters/check/syntax/all',                 RestAdminFunctions.AdaptersCheckSyntaxAll()),
        ( '/adapters/check/syntax',                     RestTesterFunctions.AdaptersCheckSyntax()),
        ( '/adapters/adapter/add',                      RestTesterFunctions.AdaptersAdapterAdd()),
        ( '/adapters/package/add',                      RestTesterFunctions.AdaptersPackageAdd()),
        ( '/adapters/adapter/add/by/wsdl/url',          RestTesterFunctions.AdaptersAdapterAddByWsdlUrl()),
        ( '/adapters/adapter/add/by/wsdl/file',         RestTesterFunctions.AdaptersAdapterAddByWsdlFile()),
        ( '/adapters/package/default',                  RestTesterFunctions.AdaptersPackageDefault()),
        ( '/adapters/package/generic',                  RestTesterFunctions.AdaptersPackageGeneric()),
        ( '/adapters/build',                            RestTesterFunctions.AdaptersBuild()),
        ( '/adapters/backup',                           RestAdminFunctions.AdaptersBackup()),
        ( '/adapters/backup/listing',                   RestAdminFunctions.AdaptersBackupListing()),
        ( '/adapters/backup/download',                  RestAdminFunctions.AdaptersBackupDownload()),
        ( '/adapters/backup/remove/all',                RestAdminFunctions.AdaptersBackupRemoveAll()),
        ( '/adapters/reset',                            RestAdminFunctions.AdaptersReset()),
        ( '/adapters/listing',                          RestTesterFunctions.AdaptersListing()),
        ( '/adapters/file/move',                        RestTesterFunctions.AdaptersFileMove()),
        ( '/adapters/file/unlock/all',                  RestAdminFunctions.AdaptersFileUnlockAll()),
        ( '/adapters/file/unlock',                      RestTesterFunctions.AdaptersFileUnlock()),
        ( '/adapters/file/rename',                      RestTesterFunctions.AdaptersFileRename()),
        ( '/adapters/file/duplicate',                   RestTesterFunctions.AdaptersFileDuplicate()),
        ( '/adapters/file/remove',                      RestTesterFunctions.AdaptersFileRemove()),
        ( '/adapters/file/upload',                      RestTesterFunctions.AdaptersFileUpload()),
        ( '/adapters/file/download',                    RestTesterFunctions.AdaptersFileDownload()),
        ( '/adapters/file/open',                        RestTesterFunctions.AdaptersFileOpen()),
        ( '/adapters/directory/move',                   RestTesterFunctions.AdaptersDirectoryMove()),
        ( '/adapters/directory/rename',                 RestTesterFunctions.AdaptersDirectoryRename()),
        ( '/adapters/directory/duplicate',              RestTesterFunctions.AdaptersDirectoryDuplicate()),
        ( '/adapters/directory/remove',                 RestTesterFunctions.AdaptersDirectoryRemove()),
        ( '/adapters/directory/remove/all',             RestAdminFunctions.AdaptersDirectoryRemoveAll()),
        ( '/adapters/directory/add',                    RestTesterFunctions.AdaptersDirectoryAdd()),
        
        # libraries
        ( '/libraries/statistics',                      RestAdminFunctions.LibrariesStatistics()),
        ( '/libraries/check/syntax/all',                RestAdminFunctions.LibrariesCheckSyntaxAll()),
        ( '/libraries/check/syntax',                    RestTesterFunctions.LibrariesCheckSyntax()),
        ( '/libraries/library/add',                     RestTesterFunctions.LibrariesLibraryAdd()),
        ( '/libraries/package/add',                     RestTesterFunctions.LibrariesPackageAdd()),
        ( '/libraries/package/default',                 RestTesterFunctions.LibrariesPackageDefault()),
        ( '/libraries/package/generic',                 RestTesterFunctions.LibrariesPackageGeneric()),
        ( '/libraries/build',                           RestTesterFunctions.LibrariesBuild()),
        ( '/libraries/backup',                          RestAdminFunctions.LibrariesBackup()),
        ( '/libraries/backup/listing',                  RestAdminFunctions.LibrariesBackupListing()),
        ( '/libraries/backup/download',                 RestAdminFunctions.LibrariesBackupDownload()),
        ( '/libraries/backup/remove/all',               RestAdminFunctions.LibrariesBackupRemoveAll()),
        ( '/libraries/reset',                           RestAdminFunctions.LibrariesReset()),
        ( '/libraries/listing',                         RestTesterFunctions.LibrariesListing()),
        ( '/libraries/file/move',                       RestTesterFunctions.LibrariesFileMove()),
        ( '/libraries/file/unlock/all',                 RestAdminFunctions.LibrariesFileUnlockAll()),
        ( '/libraries/file/unlock',                     RestTesterFunctions.LibrariesFileUnlock()),
        ( '/libraries/file/rename',                     RestTesterFunctions.LibrariesFileRename()),
        ( '/libraries/file/duplicate',                  RestTesterFunctions.LibrariesFileDuplicate()),
        ( '/libraries/file/remove',                     RestTesterFunctions.LibrariesFileRemove()),
        ( '/libraries/file/upload',                     RestTesterFunctions.LibrariesFileUpload()),
        ( '/libraries/file/download',                   RestTesterFunctions.LibrariesFileDownload()),
        ( '/libraries/file/open',                       RestTesterFunctions.LibrariesFileOpen()),
        ( '/libraries/directory/move',                  RestTesterFunctions.LibrariesDirectoryMove()),
        ( '/libraries/directory/rename',                RestTesterFunctions.LibrariesDirectoryRename()),
        ( '/libraries/directory/duplicate',             RestTesterFunctions.LibrariesDirectoryDuplicate()),
        ( '/libraries/directory/remove',                RestTesterFunctions.LibrariesDirectoryRemove()),
        ( '/libraries/directory/remove/all',            RestAdminFunctions.LibrariesDirectoryRemoveAll()),
        ( '/libraries/directory/add',                   RestTesterFunctions.LibrariesDirectoryAdd()),
        
        # documentation
        ( '/documentations/cache',                      RestCommonFunctions.DocumentationsCache()),
        ( '/documentations/build',                      RestCommonFunctions.DocumentationsBuild()),
        
        # system
        ( '/system/status',                             RestCommonFunctions.SystemStatus()),
        ( '/system/usages',                             RestCommonFunctions.SystemUsages()),
        ( '/system/about',                              RestCommonFunctions.SystemAbout()),

        # administration
        ( '/administration/configuration/listing',      RestAdminFunctions.AdminConfigListing()),
        ( '/administration/configuration/reload',       RestAdminFunctions.AdminConfigReload()),
        ( '/administration/clients/deploy',             RestAdminFunctions.AdminClientsDeploy()),
        ( '/administration/users/profile',              RestAdminFunctions.AdminUsersProfile()),
        ( '/administration/users/listing',              RestAdminFunctions.AdminUsersListing()),
        ( '/administration/users/add',                  RestAdminFunctions.AdminUsersAdd()),
        ( '/administration/users/remove',               RestAdminFunctions.AdminUsersRemove()),
        ( '/administration/users/channel/disconnect',   RestAdminFunctions.AdminUsersChannelDisconnect()),
        ( '/administration/users/update',               RestAdminFunctions.AdminUsersUpdate()),
        ( '/administration/users/status',               RestAdminFunctions.AdminUsersStatus()),
        ( '/administration/users/duplicate',            RestAdminFunctions.AdminUsersDuplicate()),
        ( '/administration/users/password/reset',       RestAdminFunctions.AdminUsersPasswordReset()),
        ( '/administration/users/password/update',      RestAdminFunctions.AdminUsersPasswordUpdate()),
        ( '/administration/users/search',               RestAdminFunctions.AdminUsersSearch()),
        ( '/administration/users/statistics',           RestAdminFunctions.AdminUsersStatistics()),
        ( '/administration/projects/listing',           RestAdminFunctions.AdminProjectsListing()),
        ( '/administration/projects/add',               RestAdminFunctions.AdminProjectsAdd()),
        ( '/administration/projects/remove',            RestAdminFunctions.AdminProjectsRemove()),
        ( '/administration/projects/rename',            RestAdminFunctions.AdminProjectsRename()),
        ( '/administration/projects/search/by/name',    RestCommonFunctions.AdminProjectsSearchByName()),
        ( '/administration/projects/statistics',        RestAdminFunctions.AdminProjectsStatistics()),
        ( '/administration/time/shift',                 RestAdminFunctions.AdminTimeShift()),
        
        # client
        ( '/clients/available',                         RestCommonFunctions.ClientsAvailable()),
        ( '/clients/download',                          RestCommonFunctions.ClientsDownload())
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

        self.httpd = make_server( host=listeningAddress[0], 
                                  port=listeningAddress[1], 
                                  app=_WebServices, 
                                  handler_class=_NoLoggingWSGIRequestHandler )

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
