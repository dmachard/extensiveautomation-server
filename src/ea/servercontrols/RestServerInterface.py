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

from pycnic.core import WSGI

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler

import threading
import logging
import sys
import wrapt

from ea.libs import Logger
from ea.servercontrols import RestTesterFunctions
from ea.servercontrols import RestAdminFunctions
from ea.servercontrols import RestCommonFunctions
from ea.servercontrols import RestRessources


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
Logger
"""


class WSGIRequestHandlerLogging(WSGIRequestHandler, Logger.ClassLogger):
    """
    """

    def log_message(self, format, *args):
        """
        """
        try:
            self.trace("%s %s %s" % args)
        except BaseException:
            print(args)


if sys.version_info > (3,):
    _my_logger = None
else:
    _my_logger = logging.Logger("LOG")
    _my_logger.setLevel(logging.INFO)
    _hnd = logging.StreamHandler(sys.stdout)
    _my_logger.addHandler(_hnd)

"""
Webservices routing
"""


class _WebServices(WSGI):
    # This allows * on all Handlers
    headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "*"),
        ("Access-Control-Allow-Headers",
         "X-Requested-With, Content-Type, Origin, Authorization, Accept, Client-Security-Token, Accept-Encoding")
    ]

    logger = _my_logger
    # debug = True
    routes = [
        # new in v22
        ('/v1/files/(.*)', RestRessources.FilesHandler()),
        ('/v1/jobs', RestRessources.JobsHandler()),
        ('/v1/executions', RestRessources.ExecutionsHandler()),
        
        # session
        ('/session/login', RestCommonFunctions.SessionLogin()),
        ('/session/logout', RestCommonFunctions.SessionLogout()),
        ('/session/refresh', RestCommonFunctions.SessionRefresh()),
        ('/session/context', RestCommonFunctions.SessionContext()),
        ('/session/context/notify', RestCommonFunctions.SessionContextNotify()),
        ('/session/context/all', RestCommonFunctions.SessionContextAll()),

        # agents
        ('/agents/running', RestTesterFunctions.AgentsRunning()),
        ('/agents/disconnect', RestTesterFunctions.AgentsDisconnect()),

        # tasks
        
        ('/tasks/schedule', RestCommonFunctions.TasksSchedule()),
        ('/tasks/remove', RestCommonFunctions.TasksRemove()),
        ('/tasks/listing', RestCommonFunctions.TasksListing()),
        ('/tasks/running', RestCommonFunctions.TasksRunning()),
        ('/tasks/waiting', RestCommonFunctions.TasksWaiting()),
        ('/tasks/history', RestCommonFunctions.TasksHistory()),
        ('/tasks/history/all', RestCommonFunctions.TasksHistoryAll()),
        ('/tasks/cancel', RestCommonFunctions.TasksCancel()),
        ('/tasks/cancel/selective', RestCommonFunctions.TasksCancelSelective()),
        ('/tasks/cancel/all', RestAdminFunctions.TasksCancelAll()),
        ('/tasks/history/clear', RestAdminFunctions.TasksHistoryClear()),
        ('/tasks/replay', RestCommonFunctions.TasksReplay()),
        ('/tasks/verdict', RestCommonFunctions.TasksVerdict()),
        ('/tasks/review', RestCommonFunctions.TasksReview()),
        ('/tasks/design', RestCommonFunctions.TasksDesign()),
        ('/tasks/comment', RestCommonFunctions.TasksComment()),
        ('/tasks/kill', RestCommonFunctions.TasksKill()),
        ('/tasks/kill/all', RestAdminFunctions.TasksKillAll()),
        ('/tasks/kill/selective', RestCommonFunctions.TasksKillSelective()),
        ('/tasks/reschedule', RestCommonFunctions.TasksReschedule()),

        # public storage
        ('/public/listing/basic', RestTesterFunctions.PublicListing()),
        ('/public/directory/add', RestTesterFunctions.PublicDirectoryAdd()),
        ('/public/directory/remove', RestTesterFunctions.PublicDirectoryRemove()),
        ('/public/directory/rename', RestTesterFunctions.PublicDirectoryRename()),
        ('/public/file/download', RestTesterFunctions.PublicDownload()),
        ('/public/file/import', RestTesterFunctions.PublicImport()),
        ('/public/file/remove', RestTesterFunctions.PublicRemove()),
        ('/public/file/rename', RestTesterFunctions.PublicRename()),

        # tests
        ('/tests/schedule', RestTesterFunctions.TestsSchedule()),
        ('/tests/schedule/tpg', RestTesterFunctions.TestsScheduleTpg()),
        ('/tests/schedule/group', RestTesterFunctions.TestsScheduleGroup()),
        ('/tests/listing/basic', RestTesterFunctions.TestsBasicListing()),
        ('/tests/listing/dict', RestTesterFunctions.TestsDictListing()),
        ('/tests/listing', RestTesterFunctions.TestsListing()),
        ('/tests/directory/add', RestTesterFunctions.TestsDirectoryAdd()),
        ('/tests/directory/remove', RestTesterFunctions.TestsDirectoryRemove()),
        ('/tests/directory/remove/all', RestAdminFunctions.TestsDirectoryRemoveAll()),
        ('/tests/directory/rename', RestTesterFunctions.TestsDirectoryRename()),
        ('/tests/directory/duplicate', RestTesterFunctions.TestsDirectoryDuplicate()),
        ('/tests/directory/move', RestTesterFunctions.TestsDirectoryMove()),
        ('/tests/file/download', RestTesterFunctions.TestsFileDownload()),
        ('/tests/file/open', RestTesterFunctions.TestsFileOpen()),
        ('/tests/file/upload', RestTesterFunctions.TestsFileUpload()),
        ('/tests/file/remove', RestTesterFunctions.TestsFileRemove()),
        ('/tests/file/rename', RestTesterFunctions.TestsFileRename()),
        ('/tests/file/duplicate', RestTesterFunctions.TestsFileDuplicate()),
        ('/tests/file/move', RestTesterFunctions.TestsFileMove()),
        ('/tests/file/unlock', RestTesterFunctions.TestsFileUnlock()),
        ('/tests/check/syntax', RestTesterFunctions.TestsCheckSyntax()),
        ('/tests/check/syntax/tpg', RestTesterFunctions.TestsCheckSyntaxTpg()),
        ('/tests/create/design', RestTesterFunctions.TestsCreateDesign()),
        ('/tests/create/design/tpg', RestTesterFunctions.TestsCreateDesignTpg()),
        ('/tests/find/file-usage', RestTesterFunctions.TestsFindFileUsage()),

        # variables
        ('/variables/listing', RestTesterFunctions.VariablesListing()),
        ('/variables/add', RestTesterFunctions.VariablesAdd()),
        ('/variables/update', RestTesterFunctions.VariablesUpdate()),
        ('/variables/remove', RestTesterFunctions.VariablesRemove()),
        ('/variables/duplicate', RestTesterFunctions.VariablesDuplicate()),
        ('/variables/reset', RestAdminFunctions.VariablesReset()),
        ('/variables/search/by/name', RestTesterFunctions.VariablesSearchByName()),
        ('/variables/search/by/id', RestTesterFunctions.VariablesSearchById()),

        # tests results storage
        ('/results/listing/files', RestTesterFunctions.ResultsListingFiles()),
        ('/results/listing/basic', RestTesterFunctions.ResultsListingBasic()),
        ('/results/listing/by/id/datetime', RestTesterFunctions.ResultsListingFilter()),
        ('/results/reset', RestAdminFunctions.ResultsReset()),
        ('/results/remove/by/id', RestTesterFunctions.ResultsRemoveById()),
        ('/results/remove/by/date', RestTesterFunctions.ResultsRemoveByDate()),
        ('/results/follow', RestTesterFunctions.ResultsFollow()),
        ('/results/details', RestTesterFunctions.ResultsDetails()),
        ('/results/status', RestTesterFunctions.ResultsStatus()),
        ('/results/verdict', RestTesterFunctions.ResultsVerdict()),
        ('/results/report/verdicts', RestTesterFunctions.ResultsReportVerdicts()),
        ('/results/report/reviews', RestTesterFunctions.ResultsReportReviews()),
        ('/results/report/designs', RestTesterFunctions.ResultsReportDesigns()),
        ('/results/report/comments', RestTesterFunctions.ResultsReportComments()),
        ('/results/report/events', RestTesterFunctions.ResultsReportEvents()),
        ('/results/reports', RestTesterFunctions.ResultsReports()),
        ('/results/upload/file', RestTesterFunctions.ResultsUploadFile()),
        ('/results/download/image', RestTesterFunctions.ResultsDownloadImage()),
        ('/results/download/result', RestTesterFunctions.ResultsDownloadResult()),
        ('/results/download/uncomplete',
         RestTesterFunctions.ResultsDownloadResultUncomplete()),
        ('/results/comment/add', RestTesterFunctions.ResultsCommentAdd()),
        ('/results/comments/remove', RestTesterFunctions.ResultsCommentsRemove()),

        # adapters
        ('/adapters/adapter/add', RestTesterFunctions.AdaptersAdapterAdd()),
        ('/adapters/listing', RestTesterFunctions.AdaptersListing()),
        ('/adapters/file/move', RestTesterFunctions.AdaptersFileMove()),
        ('/adapters/file/unlock', RestTesterFunctions.AdaptersFileUnlock()),
        ('/adapters/file/rename', RestTesterFunctions.AdaptersFileRename()),
        ('/adapters/file/duplicate', RestTesterFunctions.AdaptersFileDuplicate()),
        ('/adapters/file/remove', RestTesterFunctions.AdaptersFileRemove()),
        ('/adapters/file/upload', RestTesterFunctions.AdaptersFileUpload()),
        ('/adapters/file/download', RestTesterFunctions.AdaptersFileDownload()),
        ('/adapters/file/open', RestTesterFunctions.AdaptersFileOpen()),
        ('/adapters/directory/move', RestTesterFunctions.AdaptersDirectoryMove()),
        ('/adapters/directory/rename', RestTesterFunctions.AdaptersDirectoryRename()),
        ('/adapters/directory/duplicate',
         RestTesterFunctions.AdaptersDirectoryDuplicate()),
        ('/adapters/directory/remove', RestTesterFunctions.AdaptersDirectoryRemove()),
        ('/adapters/directory/remove/all',
         RestAdminFunctions.AdaptersDirectoryRemoveAll()),
        ('/adapters/directory/add', RestTesterFunctions.AdaptersDirectoryAdd()),
        ('/adapters/check/syntax', RestTesterFunctions.AdaptersCheckSyntax()),

        # system
        ('/system/status', RestCommonFunctions.SystemStatus()),
        ('/system/about', RestCommonFunctions.SystemAbout()),

        # administration
        ('/administration/configuration/listing',
         RestAdminFunctions.AdminConfigListing()),
        ('/administration/configuration/reload',
         RestAdminFunctions.AdminConfigReload()),
        ('/administration/users/profile', RestAdminFunctions.AdminUsersProfile()),
        ('/administration/users/listing', RestAdminFunctions.AdminUsersListing()),
        ('/administration/users/add', RestAdminFunctions.AdminUsersAdd()),
        ('/administration/users/remove', RestAdminFunctions.AdminUsersRemove()),
        ('/administration/users/channel/disconnect',
         RestAdminFunctions.AdminUsersChannelDisconnect()),
        ('/administration/users/update', RestCommonFunctions.AdminUsersUpdate()),
        ('/administration/users/status', RestAdminFunctions.AdminUsersStatus()),
        ('/administration/users/duplicate',
         RestAdminFunctions.AdminUsersDuplicate()),
        ('/administration/users/password/reset',
         RestAdminFunctions.AdminUsersPasswordReset()),
        ('/administration/users/password/update',
         RestCommonFunctions.AdminUsersPasswordUpdate()),
        ('/administration/users/search', RestAdminFunctions.AdminUsersSearch()),
        ('/administration/projects/listing',
         RestAdminFunctions.AdminProjectsListing()),
        ('/administration/projects/add', RestAdminFunctions.AdminProjectsAdd()),
        ('/administration/projects/remove',
         RestAdminFunctions.AdminProjectsRemove()),
        ('/administration/projects/rename',
         RestAdminFunctions.AdminProjectsRename()),
        ('/administration/projects/search/by/name',
         RestCommonFunctions.AdminProjectsSearchByName()),
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

        self.httpd = make_server(host=listeningAddress[0],
                                 port=listeningAddress[1],
                                 app=_WebServices,
                                 handler_class=WSGIRequestHandlerLogging
                                 )

    def run(self):
        """
        Run xml rpc server
        """
        self.trace("REST server started")
        try:
            while not self._stopEvent.isSet():
                self.httpd.serve_forever()
        except Exception as e:
            self.error("Exception in REST server thread: " + str(e))
        self.trace("REST server stopped")

    def stop(self):
        """
        Stop the xml rpc server
        """
        self._stopEvent.set()
        self.httpd.shutdown()
        self.join()


_RSI = None  # singleton


def instance():
    """
    Returns the singleton of the rest server

    @return:
    @rtype:
    """
    return _RSI


def initialize(listeningAddress):
    """
    Rest server instance creation

    @param listeningAddress: listing on ip and port
    @type listeningAddress: tuple
    """
    global _RSI
    _RSI = _RestServerInterface(listeningAddress=listeningAddress)


def finalize():
    """
    Destruction of the singleton
    """
    global _RSI
    if _RSI:
        _RSI.stop()
        _RSI = None
