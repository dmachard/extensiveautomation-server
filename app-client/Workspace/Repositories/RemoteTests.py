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
Remote tests module
"""

import sys
import base64
import time

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QTreeWidgetItem, QMessageBox)
except ImportError:
    from PyQt5.QtWidgets import (QTreeWidgetItem, QMessageBox)
    
from Libs import QtHelper, Logger

try:
    import RemoteRepository
except ImportError: # support python3
    from . import RemoteRepository

try:
    xrange
except NameError: # support python3
    xrange = range

import UserClientInterface as UCI
import RestClientInterface as RCI


class Repository(RemoteRepository.Repository):
    """
    Repository
    """
    def __init__(self, parent, projectSupport=False):
        """
        Repoistory constructor
        """
        RemoteRepository.Repository.__init__(self, parent, projectSupport=projectSupport)
 
        self.pluginsStarted = []
        
    def __treeFolder(self, item):
        """
        Reccursive tree folder
        """
        listing = []
        
        if item.childCount():
            for i in xrange(item.childCount()):
                childItem = item.child(i)
                if childItem.type() == QTreeWidgetItem.UserType+0: # file
                    listing.append( childItem.getPath(withFileName = True, withFolderName=False) )
                if childItem.type() == QTreeWidgetItem.UserType+1: # folder
                    pathFolder = childItem.getPath(withFileName = False, withFolderName=True)
                    listing.extend( self.__treeFolder(childItem) )
                    
        return listing
            
    def pluginDataAccessor(self):
        """
        Send data to plugin
        """
        listing = []
        
        if self.itemCurrent is not None:
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
                listing.append( self.itemCurrent.getPath(withFileName = True, withFolderName=False) )
                
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+10 : #root
                listing.extend( self.__treeFolder(self.itemCurrent) )
                
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+1: # folder
                pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=True)
                listing.extend( self.__treeFolder(self.itemCurrent) )
                
        return { "files-tree": listing }
        
    def addPlugin(self, pluginAct):
        """
        Add plugin
        """
        self.pluginsStarted.append( pluginAct )
        
    def moreCreateActions(self):
        """
        More creation qt actions
        """
        self.createSamplesAction = QtHelper.createAction(self, "&Generate samples", self.generateSamples, 
                                                         icon = None, 
                                                         tip = 'Generate samples' )
        self.setTestsDefaultAction = QtHelper.createAction(self, "&Set default versions", self.setDefaultVersionForAllTests, 
                                                           icon = None, 
                                                           tip = 'Set default version adapters and libraries for all tests' )

    def moreDefaultActions(self):
        """
        Reimplemented from RemoteRepository
        """
        self.createSamplesAction.setEnabled(False)
    
    def onMorePopupMenu(self, itemType):
        """
        Reimplemented from RemoteRepository
        """
        if itemType == QTreeWidgetItem.UserType+10 : # root
            self.menu.addSeparator()
            self.menu.addAction( self.createSamplesAction )
            self.menu.addAction( self.setTestsDefaultAction )

        self.menu.addSeparator()
        for plug in self.pluginsStarted:
            self.menu.addAction( plug )
            
    def onPluginImport(self, dataJson):
        """
        On data from plugin
        """
        if "files" not in dataJson:
            QMessageBox.warning(self, "Remote tests" , "bad json import, files key is missing!")
            
        # get current project
        project = self.getCurrentProject()
        projectId = self.getProjectId(project=str(project))

        for el in dataJson['files']:
            if 'file-path' in el and 'content-file' in el:
                try:
                    contentFile = base64.b64decode(el['content-file'])
                except Exception as e:
                    QMessageBox.warning(self, "Remote tests" , "bad file content!")
                else:
                    try:
                        if not el['file-path'].startswith("/"):
                            el['file-path'] = "/%s" % el['file-path']
                            
                        tmp__, extensionFile = el['file-path'].rsplit(".", 1)
                        pathFile, nameFile = tmp__.rsplit('/', 1)

                        RCI.instance().uploadTestFile(filePath=pathFile, fileName=nameFile, 
                                                      fileExtension=extensionFile, 
                                                      fileContent=contentFile, projectId=projectId, 
                                                      updateMode=False, closeTabAfter=False)
                    except Exception as e:
                        QMessageBox.warning(self, "Remote tests" , "bad file path!")
                    
    def setDefaultVersionForAllTests(self):
        """
        Set the default version for all tests
        """
        reply = QMessageBox.question(self, self.tr("Set default adapters and libraries version"), 
                                     self.tr("Are you sure to set the default adapters and libraries version for all tests?"),
                                     QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            RCI.instance().setAllTestsAsDefault()
            
    def generateSamples(self):
        """
        Generate samples
        """
        reply = QMessageBox.question(self, self.tr("Generate samples"), self.tr("Are you sure to re-generate samples?"),
                                     QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            RCI.instance().buildSamples()
            
    def moveRemoteFile(self, currentName, currentPath, currentExtension, newPath, project=0, newProject=0):
        """
        Reimplemented from RemoteRepository
        Move file
        """
        RCI.instance().moveFileTests(filePath=currentPath, fileName=currentName, fileExt=currentExtension, 
                                     fileProject=project, newPath=newPath, newProject=newProject)
        
    def moveRemoteFolder(self, currentName, currentPath, newPath, project=0, newProject=0):
        """
        Reimplemented from RemoteRepository
        Move folder
        """
        RCI.instance().moveFolderTests(folderPath=currentPath, folderName=currentName, folderProject=project, 
                                       newPath=newPath, newProject=newProject)
        
    def initialize(self, listing):
        """
        Initialize the repository
        """
        self.createSamplesAction.setEnabled(False)

        if UCI.RIGHTS_ADMIN in RCI.instance().userRights:
            self.createSamplesAction.setEnabled(True)

        # if UCI.RIGHTS_DEVELOPER in RCI.instance().userRights:
            # self.createSamplesAction.setEnabled(True)

        RemoteRepository.Repository.initialize(self, listing)

    def openRemoteFile (self, pathFile, project=0):
        """
        Reimplemented from RemoteRepository
        Open the file

        @param pathFile: 
        @type pathFile:
        """
        RCI.instance().openFileTests(projectId=int(project), filePath=pathFile)
    
    def deleteAllFolders (self, pathFolder, project=0):
        """
        Reimplemented from RemoteRepository
        Delete all folders

        @param pathFolder: 
        @type pathFolder:
        """
        RCI.instance().removeFoldersTests(projectId=project,
                                          folderPath=pathFolder)
        
    def deleteFile (self, pathFile, project=0):
        """
        Reimplemented from RemoteRepository
        Delete file

        @param pathFile: 
        @type pathFile:
        """
        RCI.instance().removeFileTests(filePath=pathFile, 
                                       fileProject=project)
        
    def deleteFolder (self, pathFolder, project=0):
        """
        Reimplemented from RemoteRepository
        Delete folder

        @param pathFolder: 
        @type pathFolder:
        """
        RCI.instance().removeFolderTests(projectId=project, 
                                         folderPath=pathFolder)
        
    def addFolder (self, pathFolder, folderName, project=0):
        """
        Reimplemented from RemoteRepository
        Add folder

        @param pathFolder: 
        @type pathFolder:

        @param folderName: 
        @type folderName:
        """
        RCI.instance().addFolderTests(projectId=project, 
                                      folderPath=pathFolder,
                                      folderName = folderName)

    def refresh(self, project=0, saveAsOnly=False):
        """
        Reimplemented from RemoteRepository
        Refresh
        """
        if not project:
            projectname = self.getCurrentProject()
            project = self.getProjectId(project=str(projectname))

        RCI.instance().listingTests(projectId=project, 
                                    forSaveAs=saveAsOnly, 
                                    forRuns=False)
    # dbr13 udpdate_location for rename>>>
    def renameFile (self, mainPath, oldFileName, newFileName, extFile, project=0, update_location=False):
        """
        Reimplemented from RemoteRepository
        Rename file

        @param mainPath: 
        @type mainPath:

        @param oldFileName: 
        @type oldFileName:

        @param newFileName: 
        @type newFileName:

        @param extFile: 
        @type extFile:

        @param update_location:
        @type update_location:
        """
        RCI.instance().renameFileTests(filePath=mainPath,
                                       fileName=oldFileName,
                                       fileExt=extFile,
                                       fileProject=project,
                                       newName=newFileName,
                                       update_location=update_location)
                                             
    def renameFolder (self, mainPath, oldFolderName, newFolderName, project=0):
        """
        Reimplemented from RemoteRepository
        Rename folder

        @param mainPath: 
        @type mainPath:

        @param oldFolderName: 
        @type oldFolderName:

        @param newFolderName: 
        @type newFolderName:
        """
        RCI.instance().renameFolderTests(projectId=project, 
                                         folderPath=mainPath, 
                                         folderName = oldFolderName, 
                                         newName=newFolderName)
        
    def duplicateFile (self, mainPath, oldFileName, newFileName, extFile, project=0, newProject=0, newPath=''):
        """
        Reimplemented from RemoteRepository
        Duplicate file

        @param mainPath: 
        @type mainPath:

        @param oldFileName: 
        @type oldFileName:

        @param newFileName: 
        @type newFileName:

        @param extFile: 
        @type extFile:
        """
        RCI.instance().duplicateFileTests( filePath=mainPath,
                                           fileName=oldFileName, 
                                           fileExt=extFile, 
                                           fileProject=project,
                                           newPath=newPath, 
                                           newName=newFileName,
                                           newProject=newProject)
        
    def duplicateFolder (self, mainPath, oldFolderName, newFolderName, project=0, newProject=0, newPath=''):
        """
        Reimplemented from RemoteRepository
        Duplicate folder

        @param mainPath: 
        @type mainPath:

        @param oldFolderName: 
        @type oldFolderName:

        @param newFolderName: 
        @type newFolderName:
        """
        RCI.instance().duplicateFolderTests( folderProject=project,
                                             folderPath=mainPath, 
                                             folderName = oldFolderName, 
                                             newPath=newPath,
                                             newName=newFolderName,
                                             newProject=newProject)