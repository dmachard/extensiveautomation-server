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
Repositories manager module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QFrame, QTabWidget, QIcon, QLabel, QFont, QVBoxLayout)
    from PyQt4.QtCore import (QRect)
except ImportError:
    from PyQt5.QtGui import (QIcon, QFont)
    from PyQt5.QtWidgets import (QWidget, QFrame, QTabWidget, QLabel, QVBoxLayout)
    from PyQt5.QtCore import (QRect)
    
from Libs import QtHelper, Logger

try:
    import LocalRepository
    import RemoteTests
    import RemoteAdapters
    import RemoteLibraries
except ImportError: # support python3
    from . import LocalRepository
    from . import RemoteTests
    from . import RemoteAdapters
    from . import RemoteLibraries
    
import Settings
import UserClientInterface as UCI

import os.path
import base64
import json
import zlib

TAB_LOCAL_POS       =   0
TAB_REMOTE_POS      =   1
TAB_ADAPTER_POS     =   0
TAB_LIBRARY_POS     =   1

MAIN_TAB_TEST       = 0
MAIN_TAB_DEV        = 1

class WRepositories(QWidget, Logger.ClassLogger):
    """
    Repositories widget
    """
    def __init__(self, parent=None):
        """
        Constructs WRepositories widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        
        self.localRepoPath = Settings.instance().readValue( key = 'Repositories/local-repo' )
        self.localRepository = None
        self.localSaveOpen = None
        self.remoteRepository = None
        self.adaptersRemoteRepository = None
        
        self.createWidgets()
        self.createConnections()
        self.onResetRemote()

    def localRepoIsPresent(self):
        """
        The local repository is configured ?
        """
        if self.localRepoPath != "Undefined":
            if not os.path.exists(self.localRepoPath):
                self.localConfigured = "Undefined"
                self.testsTab.setTabEnabled( TAB_LOCAL_POS, False )
            else:
                self.localConfigured = self.localRepoPath
                self.testsTab.setTabEnabled( TAB_LOCAL_POS, True )
        else:
            self.localConfigured = self.localRepoPath
            self.testsTab.setTabEnabled( TAB_LOCAL_POS, False )

    def createWidgets(self):
        """
        Create qt widgets

        QTabWidget:
          ________  ________
         /        \/        \___________
        |                               |
        |                               |
        |                               |
        |_______________________________|
        """
        self.line = QFrame()
        self.line.setGeometry(QRect(110, 221, 51, 20))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
  
        self.testsTab = QTabWidget()
        self.testsTab.setTabPosition(QTabWidget.North)
        self.testsTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border

        # local repo
        self.localConfigured = self.localRepoPath
        self.localRepository = LocalRepository.Repository( parent = self )
        self.localRepository.deactive()
        self.localRepoIsPresent()

        self.localSaveOpen = LocalRepository.SaveOpenToRepoDialog(parent = self)
       
        # remote repo
        self.remoteRepository = RemoteTests.Repository( parent = self, projectSupport=True )
        if not UCI.instance().isAuthenticated():
            self.remoteRepository.setNotConnected() 
            self.remoteRepository.setEnabled( False ) 

        # adapters remote repo
        self.adaptersRemoteRepository = RemoteAdapters.Repository( parent = self )
        if not UCI.instance().isAuthenticated():
            self.adaptersRemoteRepository.setNotConnected() 
            self.adaptersRemoteRepository.setEnabled( False ) 

        # libraries adapters remote repo
        self.librariesRemoteRepository = RemoteLibraries.Repository( parent = self )
        if not UCI.instance().isAuthenticated():
            self.librariesRemoteRepository.setNotConnected() 
            self.librariesRemoteRepository.setEnabled( False ) 

        self.testsTab.addTab(self.localRepository, QIcon(":/repository-tests.png"), self.tr("Local Tests") )
        self.testsTab.addTab( self.remoteRepository, QIcon(":/repository-tests.png"), self.tr("Remote Tests") )
        self.testsTab.setTabEnabled( TAB_LOCAL_POS, False )
        self.testsTab.setTabEnabled( TAB_REMOTE_POS, False )

        self.connectorsTab = QTabWidget()
        self.connectorsTab.setTabPosition(QTabWidget.North)
        self.connectorsTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border

        self.connectorsTab.addTab(self.adaptersRemoteRepository, QIcon(":/repository-adapters.png"), self.tr("Adapters") )
        self.connectorsTab.addTab(self.librariesRemoteRepository, QIcon(":/repository-libraries.png"), self.tr("Libraries") )
        self.connectorsTab.setTabEnabled( TAB_ADAPTER_POS, False )
        self.connectorsTab.setTabEnabled( TAB_LIBRARY_POS, False )

        self.title = QLabel(self.tr("Repositories"))
        font = QFont()
        font.setBold(True)
        self.title.setFont(font)

        self.labelHelp = QLabel(self.tr("Drag and drop your selected file in the workspace to open it."))
        self.labelHelp.setEnabled(False)
        font = QFont()
        font.setItalic(True)
        self.labelHelp.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget( self.title )
        layout.addWidget( self.labelHelp )

        self.mainTab = QTabWidget()
        self.mainTab.setEnabled(False)
        self.mainTab.setTabPosition(QTabWidget.North)
        self.mainTab.setMinimumWidth( 300 )

        self.mainTab.addTab(self.testsTab, QIcon(":/test-description.png"), "Tests Listing")
        self.mainTab.addTab(self.connectorsTab, QIcon(":/adapters.png"), "Modules Listing")

        layout.addWidget( self.mainTab )
        layout.addWidget( self.line )

        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # set the default tab  
        defaultTab = Settings.instance().readValue( key = 'Repositories/default-repo-test' )
        if int(defaultTab) == TAB_LOCAL_POS or int(defaultTab) == TAB_REMOTE_POS:
            self.mainTab.setCurrentIndex(MAIN_TAB_TEST)  
            self.testsTab.setCurrentIndex(int(defaultTab))   
        else:
            self.mainTab.setCurrentIndex(MAIN_TAB_DEV)  
            self.connectorsTab.setCurrentIndex(int(defaultTab)-2)   
    
    def hideWidgetsHeader(self):
        """
        """
        self.line.hide()
        self.title.hide()
        self.labelHelp.hide()
        
    def showWidgetsHeader(self):
        """
        """
        self.line.show()
        self.title.show()
        self.labelHelp.show()
        
    def createConnections(self):
        """
        Create qt connections
        """
        pass

    def initLocalRepo(self):
        """
        Initialize the local repository
        """
        if self.localConfigured != "Undefined":
            self.localRepository.active()

    def cleanLocalRepo(self):
        """
        Cleanup the local repository
        """
        self.localRepository.deactive()

    def local (self):
        """
        Returns the local repository widget

        @return: LocalRepository.Repository
        @rtype: QWidget
        """
        return self.localRepository
    
    def localDialogSave(self):
        """
        Return the save/open dialog
        """
        return self.localSaveOpen

    def remote (self):
        """
        Returns the remote repository widget

        @return: RemoteRepository.Repository
        @rtype: QWidget
        """
        return self.remoteRepository
    
    def remoteAdapter (self):
        """
        Returns the remote repository widget

        @return: RemoteRepository.Repository
        @rtype: QWidget
        """
        return self.adaptersRemoteRepository

    def remoteLibrary (self):
        """
        Returns the remote repository widget

        @return: RemoteRepository.Repository
        @rtype: QWidget
        """
        return self.librariesRemoteRepository

    def decodeData(self, b64data):
        """
        Decode data
        """
        data_json = ''
        try:
            data_decoded = base64.b64decode(b64data)
        except Exception as e:
            self.error( 'unable to decode from base64 structure: %s' % str(e) )
        else:
            try:
                data_uncompressed = zlib.decompress(data_decoded)
            except Exception as e:
                self.error( 'unable to decompress: %s' % str(e) )
            else:
                try:
                    if sys.version_info > (3,):
                        data_json = json.loads( data_uncompressed.decode('utf-8') )
                    else:
                        data_json = json.loads( data_uncompressed )
                except Exception as e:
                    self.error( 'unable to decode from json structure: %s' % str(e) )
        return data_json

    # functions for remote repository
    def onLoadRemote(self, data):
        """
        Called on load remote actions
        """
        self.mainTab.setEnabled(True)
        self.labelHelp.setEnabled(True)
        if UCI.RIGHTS_TESTER in UCI.instance().userRights:
            self.remoteRepository.setConnected() 
            self.remoteRepository.setEnabled(True)
            self.localRepository.setEnabled(True)
            
            self.testsTab.setTabEnabled( TAB_REMOTE_POS, True )
            if self.localConfigured != "Undefined":
                self.testsTab.setTabEnabled( TAB_LOCAL_POS, True )
            else:
                self.testsTab.setTabEnabled( TAB_LOCAL_POS, False )
            self.connectorsTab.setTabEnabled( TAB_LIBRARY_POS, False )
            self.connectorsTab.setTabEnabled( TAB_ADAPTER_POS, False )
 
            defaultTab = Settings.instance().readValue( key = 'Repositories/default-repo-test' )
            if int(defaultTab) == TAB_LOCAL_POS or int(defaultTab) == TAB_REMOTE_POS:
                self.mainTab.setCurrentIndex(MAIN_TAB_TEST)  
                self.testsTab.setCurrentIndex(int(defaultTab))   
            else:
                self.mainTab.setCurrentIndex(MAIN_TAB_DEV)  
                self.connectorsTab.setCurrentIndex(int(defaultTab)-2)   
            
            self.remoteRepository.defaultActions()
            self.remoteRepository.initialize(listing= self.decodeData(data['repo'])  )
            self.remoteRepository.initializeProjects( projects=self.decodeData(data['projects']), defaultProject=data['default-project'] )
        
        if UCI.RIGHTS_DEVELOPER in UCI.instance().userRights:
            self.connectorsTab.setTabEnabled( TAB_ADAPTER_POS, True )
            self.connectorsTab.setTabEnabled( TAB_LIBRARY_POS, True )

            if UCI.RIGHTS_TESTER in UCI.instance().userRights: # exception if the developer if also a tester
                defaultTab = Settings.instance().readValue( key = 'Repositories/default-repo-test' )
                if int(defaultTab) == TAB_LOCAL_POS or int(defaultTab) == TAB_REMOTE_POS:
                    self.mainTab.setCurrentIndex(MAIN_TAB_TEST)  
                    self.testsTab.setCurrentIndex(int(defaultTab))   
                else:
                    self.mainTab.setCurrentIndex(MAIN_TAB_DEV)  
                    self.connectorsTab.setCurrentIndex(int(defaultTab)-2)   
            else:
                defaultTab = Settings.instance().readValue( key = 'Repositories/default-repo-dev' )
                if int(defaultTab) == TAB_LOCAL_POS or int(defaultTab) == TAB_REMOTE_POS:
                    self.mainTab.setCurrentIndex(MAIN_TAB_TEST)  
                    self.testsTab.setCurrentIndex(int(defaultTab))   
                else:
                    self.mainTab.setCurrentIndex(MAIN_TAB_DEV)  
                    self.connectorsTab.setCurrentIndex(int(defaultTab)-2)   
                    
            self.adaptersRemoteRepository.setConnected() 
            self.adaptersRemoteRepository.setEnabled(True)
            self.adaptersRemoteRepository.defaultActions()
            self.adaptersRemoteRepository.initialize(listing=self.decodeData(data['repo-adp']) )

            self.librariesRemoteRepository.setConnected() 
            self.librariesRemoteRepository.setEnabled(True)
            self.librariesRemoteRepository.defaultActions()
            self.librariesRemoteRepository.initialize( listing=self.decodeData(data['repo-lib-adp']) )

        if UCI.RIGHTS_ADMIN in UCI.instance().userRights:
            self.remoteRepository.setConnected() 
            self.remoteRepository.setEnabled(True)
            self.localRepository.setEnabled(True)

            self.testsTab.setTabEnabled( TAB_REMOTE_POS, True )
            if self.localConfigured != "Undefined":
                self.testsTab.setTabEnabled( TAB_LOCAL_POS, True )
            else:
                self.testsTab.setTabEnabled( TAB_LOCAL_POS, False )
            self.connectorsTab.setTabEnabled( TAB_ADAPTER_POS, True )
            self.connectorsTab.setTabEnabled( TAB_LIBRARY_POS, True )
  
            defaultTab = Settings.instance().readValue( key = 'Repositories/default-repo-test' )
            if int(defaultTab) == TAB_LOCAL_POS or int(defaultTab) == TAB_REMOTE_POS:
                self.mainTab.setCurrentIndex(MAIN_TAB_TEST)  
                self.testsTab.setCurrentIndex(int(defaultTab))   
            else:
                self.mainTab.setCurrentIndex(MAIN_TAB_DEV)  
                self.connectorsTab.setCurrentIndex(int(defaultTab)-2)   
                    
            self.remoteRepository.defaultActions()
            if self.remoteRepository.initializeProjects( projects= self.decodeData(data['projects']), defaultProject=data['default-project']  ) :
                self.remoteRepository.initialize(listing= self.decodeData(data['repo']))

            self.adaptersRemoteRepository.setConnected() 
            self.adaptersRemoteRepository.setEnabled(True)
            self.adaptersRemoteRepository.defaultActions()
            self.adaptersRemoteRepository.initialize(listing=self.decodeData(data['repo-adp']) )

            self.librariesRemoteRepository.setConnected() 
            self.librariesRemoteRepository.setEnabled(True)
            self.librariesRemoteRepository.defaultActions()
            self.librariesRemoteRepository.initialize( listing=self.decodeData(data['repo-lib-adp']) )

    def onResetRemote(self):
        """
        Called on reset remote actions
        """
        self.mainTab.setEnabled(False)
        self.labelHelp.setEnabled(False)
        
        self.remoteRepository.setNotConnected() 
        self.remoteRepository.wrepository.clear()
        self.remoteRepository.setEnabled(False)
        self.localRepository.setEnabled( False ) 
        self.localRepository.defaultActions()
        
        self.adaptersRemoteRepository.setNotConnected() 
        self.adaptersRemoteRepository.wrepository.clear()
        self.adaptersRemoteRepository.setEnabled(False)
        
        self.librariesRemoteRepository.setNotConnected() 
        self.librariesRemoteRepository.wrepository.clear()
        self.librariesRemoteRepository.setEnabled(False)

        self.testsTab.setTabEnabled( TAB_REMOTE_POS, False )
        self.connectorsTab.setTabEnabled( TAB_ADAPTER_POS, False )
        self.testsTab.setTabEnabled( TAB_LOCAL_POS, False )
        self.connectorsTab.setTabEnabled( TAB_LIBRARY_POS, False )
  
        defaultTab = Settings.instance().readValue( key = 'Repositories/default-repo-test' )
        if int(defaultTab) == TAB_LOCAL_POS or int(defaultTab) == TAB_REMOTE_POS:
            self.mainTab.setCurrentIndex(MAIN_TAB_TEST)  
            self.testsTab.setCurrentIndex(int(defaultTab))   
        else:
            self.mainTab.setCurrentIndex(MAIN_TAB_DEV)  
            self.connectorsTab.setCurrentIndex(int(defaultTab)-2)   
            
    def onRefreshRemote(self, repoType, data, saveAsOnly, projectid):
        """
        Dispatch received datas to the tests repo or adapters repo
        """
        if repoType == UCI.REPO_TESTS:
            self.remoteRepository.defaultActions()
            if saveAsOnly:
                self.remoteRepository.initializeSaveAs(listing=self.decodeData(data), reloadItems=True )
            else:
                # update default project
                projectName = self.remoteRepository.getProjectName(projectid)
                self.remoteRepository.setDefaultProject(projectName=projectName)
                # reconstruct
                self.remoteRepository.initialize(listing=self.decodeData(data) )
        elif repoType == UCI.REPO_ADAPTERS:
            self.adaptersRemoteRepository.defaultActions()
            self.adaptersRemoteRepository.initialize(listing=self.decodeData(data) )
        elif repoType == UCI.REPO_LIBRARIES:
            self.librariesRemoteRepository.defaultActions()
            self.librariesRemoteRepository.initialize(listing=self.decodeData(data) )
        else:
            self.error( 'repo type unknown: %s' % repoType )

WR = None # Singleton
def instance ():
    """
    Returns Singleton
    """
    return WR

def initialize (parent):
    """
    Initialize WRepositories widget
    """
    global WR
    WR = WRepositories(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global WR
    if WR:
        WR = None