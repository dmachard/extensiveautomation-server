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
Api client interface
"""
import sys
import json

try:
    from PyQt4.QtGui import (QDialog)
    from PyQt4.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)
except ImportError:
    from PyQt5.QtWidgets import (QDialog)
    from PyQt5.QtCore import (QObject, pyqtSignal, QTimer, QFile, QIODevice)

from Libs import QtHelper, Logger
import ServerExplorer
import Settings

HTTP_POST   =   "POST"
HTTP_GET    =   "GET"

CMD_LOGIN           =   "/session/login"
CMD_LOGOUT          =   "/session/logout"
CMD_REFRESH         =   "/session/refresh"

CMD_ADD_COMMENT     =   ""
CMD_READ_COMMENTS   =   ""
CMD_DEL_COMMENTS    =   ""

CMD_EXPORT_REPORT   =   ""
CMD_EXPORT_DESIGN   =   ""
CMD_EXPORT_VERDICT  =   ""

CMD_REFRESH_REPO    =   ""
CMD_EMPTY_REPO      =   ""

CMD_LOAD_TR         =   ""
CMD_ZIP_TR          =   ""
CMD_GET_TR          =   ""
CMD_GET_TR_REPORTS  =   "/results/reports"
CMD_GET_TR_IMAGE    =   ""
CMD_DELETE_TR       =   ""


# REPOSITORY TYPE
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
    GetTestReports = pyqtSignal(dict)
    def __init__(self, parent):
        """
        Constructor
        """
        QObject.__init__(self, parent)
        self.__sessionId = None
        self.__expires = 0
        
        self.refreshTimer = QTimer()
        self.refreshTimer.timeout.connect(self.refresh)
        
    def makeRequest(self, uri, request, _json={}):
        """
        Make rest request
        """
        self.trace('REST function called %s' % uri)
        try:
            body = ''
            if len(_json): body = json.dumps(_json)
        except Exception as e:
            self.CriticalMsg.emit( "Bad json encode: %s" % e)
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
        ServerExplorer.instance().rest().unsetWsCookie()
        ServerExplorer.instance().stopWorking()
        self.CloseConnection.emit()
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
            elif response['cmd'] == CMD_GET_TR_REPORTS:
                self.onGetTestReports(details=response)
            else:
                self.onGenericError(err=self.tr("Bad cmd provided on response: %s" % response["cmd"]), 
                                    title=self.tr("Bad message") )
    
    # handle rest requests
    @calling_rest
    def login(self, login, password):  
        """
        Login
        """
        # reset
        self.__sessionId = None
        self.__expires = 0
        self.refreshTimer.stop()
        ServerExplorer.instance().rest().unsetWsCookie()
        
        # password is a sha1
        _json = { 'login': login, 'password': password }
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
    def deleteTestResult(self, trPath,  projectId=0):
        """
        Delete test result
        """
        pass
        
    @calling_rest
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
        pass
        
    @calling_rest
    def readCommentsArchive(self, archiveFile):
        """
        Read comments from archive

        @param archiveFile:
        @type archiveFile:
        """
        pass
        
    @calling_rest
    def delCommentsArchive(self, archiveFile):
        """
        Delete comments on archives

        @param archiveFile:
        @type archiveFile:
        """
        pass
        
    @calling_rest
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
        pass
        
    @calling_rest
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
        pass
        
    @calling_rest
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
        pass
        
    @calling_rest
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
        pass
        
    @calling_rest
    def loadTestCache (self, mainPath, subPath, project=1):
        """
        Load test cache

        @param mainPath:
        @type mainPath:

        @param subPath:
        @type subPath:
        """
        pass
        
    @calling_rest
    def createZipArchives (self, mainPathToZip, subPathToZip, projectId=1):
        """
        Create zip archives

        @param mainPathToZip:
        @type mainPathToZip:

        @param subPathToZip:
        @type subPathToZip:
        """
        pass
        
    @calling_rest
    def downloadResultLogsV2(self, trPath, trName, projectId=1, andSave=False, destFile=''):
        """
        Download test result v2
        """
        pass
        
    @calling_rest
    def emptyRepo(self, repo=REPO_TESTS, project=0):
        """
        Empty repository

        @param repo:
        @type repo:

        @param project:
        @type project:
        """
        pass
        
    @calling_rest        
    def getTestReports(self, testId, replayId=0, projectId=0):
        """
        Get test basic report
        """
        _json = { 'project-id': int(projectId), 'test-id': testId, 'replay-id': replayId }
        self.makeRequest( uri=CMD_GET_TR_REPORTS, request=HTTP_POST, _json=_json )

    @calling_rest
    def getImagePreview(self, trPath, imageName, projectId=0):
        """
        Get image privew
        """
        pass
        
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
        pass
        
    def onLogin(self, details):
        """
        On authentication successfull
        """
        self.trace("on success authentication: %s" % details)
        
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
        
    def onGetTestReports(self, details):
        """
        """
        self.trace("on get reports")
        self.GetTestReports.emit( details )
        
RCI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return RCI

def initialize (parent):
    """
    Initialize the class

    @param parent:
    @type: parent:

    @param clientVersion:
    @type: clientVersion:
    """
    global RCI
    RCI = RestClientInterface(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global RCI
    if RCI:
        RCI.refreshTimer.stop()
        del RCI
        RCI = None