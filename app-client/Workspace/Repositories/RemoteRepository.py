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

"""
Remote repository module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    xrange
except NameError: # support python3
    xrange = range
    
USE_PYQT5 = False
try:
    from PyQt4.QtGui import (QDialog, QPushButton, QLabel, QFont, QComboBox, QVBoxLayout, QHBoxLayout, 
                            QTreeWidget, QFrame, QHeaderView, QAbstractItemView, QLineEdit, QMessageBox, 
                            QTreeWidgetItem, QDialogButtonBox, QDrag, QTreeView, QFormLayout, QStyle, 
                            QPixmap, QWidget, QIcon, QMenu, QToolBar, QInputDialog, QCheckBox,
                            QDesktopWidget)
    from PyQt4.QtCore import (pyqtSignal, Qt, QRect, QMimeData, QSize, QObject, QEvent)
except ImportError:
    from PyQt5.QtGui import (QFont, QDrag, QPixmap, QIcon)
    from PyQt5.QtWidgets import (QDialog, QPushButton, QLabel, QComboBox, QVBoxLayout,
                                QHBoxLayout, QTreeWidget, QFrame, QHeaderView, QAbstractItemView, 
                                QLineEdit, QMessageBox, QTreeWidgetItem, QDialogButtonBox, QCheckBox,
                                QTreeView, QFormLayout, QStyle, QWidget, QMenu, QToolBar, 
                                QInputDialog, QDesktopWidget)
    from PyQt5.QtCore import (pyqtSignal, Qt, QRect, QMimeData, QSize, QObject, QEvent)
    USE_PYQT5 = True
    
from Libs import QtHelper, Logger
import Settings

import os
import operator  
import pickle
import time

import UserClientInterface as UCI
import RestClientInterface as RCI

import TestResults

import Workspace.TestUnit as TestUnit
import Workspace.TestPlan as TestPlan
import Workspace.TestConfig as TestConfig
import Workspace.TestSuite as TestSuite
import Workspace.TestData as TestData
import Workspace.TestAdapter as TestAdapter
import Workspace.TestTxt as TestTxt
import Workspace.TestPng as TestPng
import Workspace.TestAbstract as TestAbstract

import Workspace.DocumentViewer as DocumentViewer

EXTENSION_TAX = TestAbstract.TYPE
EXTENSION_TUX = TestUnit.TYPE
EXTENSION_TPX = TestPlan.TYPE
EXTENSION_TGX = TestPlan.TYPE_GLOBAL

EXTENSION_TCX = TestConfig.TYPE
EXTENSION_TSX = TestSuite.TYPE
EXTENSION_TDX = TestData.TYPE

EXTENSION_TXT = TestTxt.TYPE
EXTENSION_PY  = TestAdapter.TYPE
EXTENSION_PNG  = TestPng.TYPE
EXTENSION_SNAP  = "snapshot"

class NotReimplemented(Exception):
    """
    Not reimplemented exception
    """
    pass

class SaveOpenToRepoDialog(QDialog, Logger.ClassLogger):
    """
    Save/Open/Move dialog 
    """
    RefreshRepository = pyqtSignal(str)
    def __init__(self, parent, multipleSelection=False):
        """
        Constructor

        @param parent:
        @type parent:
        """
        super(SaveOpenToRepoDialog, self).__init__(parent)
        
        self.owner = parent

        self.filenameLineEdit = None
        self.selectedFilename = None
        self.selectedFilenames = []
        self.modeRepoSave = False # save or select file
        self.modeRepoMove = False
        
        # move 
        self.modeMoveFile = False
        self.modeMoveFolder = False
        self.modeSaveFile = False
        self.modeGetFile = False
        self.typeToHide = [ ]

        self.typeFile = [ EXTENSION_TSX ]
        self.multipleSelection = multipleSelection
        self.projectReady = False
         
        # create the widget
        self.createWidgets()
        self.createConnections()

    def initProjects(self, projects=[], defaultProject=1):
        """
        Initialize projects
        """
        self.projectReady = False
        self.projectCombobox.clear()
        self.projectCombobox.setEnabled(True)
        
        # insert data
        pname = ''
        for p in projects:
            self.projectCombobox.addItem ( p['name']  )
            if defaultProject == p['project_id']:
                pname = p['name']
        
        for i in xrange(self.projectCombobox.count()):
            item_text = self.projectCombobox.itemText(i)
            if str(pname) == str(item_text):
                self.projectCombobox.setCurrentIndex(i)

    def setDefaultProject(self, project):
        """
        Set the default project on combo
        """
        for i in xrange(self.projectCombobox.count()):
            item_text = self.projectCombobox.itemText(i)
            if str(project) == str(item_text):
                self.projectCombobox.setCurrentIndex(i)
        self.projectReady = True

    def createWidgets(self):
        """
        Create qt widgets
        """
        self.setFixedWidth(450)
        self.setFixedHeight(500)

        self.setWindowTitle(self.tr('Save in the remote repository as ...'))
        self.acceptButton = QPushButton(self.tr("Save"))
        self.warningLabel = QLabel('')
        font = QFont()
        font.setItalic(True)
        self.warningLabel.setFont(font)
        self.projectLabel = QLabel(self.tr('Project:'))

        self.projectCombobox = QComboBox(self)
        self.projectCombobox.setEnabled(False)

        layout = QVBoxLayout()
        
        layoutProject = QHBoxLayout()

        layoutProject.addWidget( self.projectLabel )
        layoutProject.addWidget( self.projectCombobox )

        layoutProject.addWidget( self.warningLabel )
        
        layoutProject.setContentsMargins(0, 0, 0, 0)
        layoutProject.setSpacing(10)
        layoutProject.setAlignment(Qt.AlignLeft)

        layout.addLayout(layoutProject)

        self.wrepository = QTreeWidget()
        self.wrepository.setFrameShape(QFrame.NoFrame)
        if USE_PYQT5:
            self.wrepository.header().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.wrepository.header().setResizeMode(QHeaderView.Stretch)
        self.wrepository.setHeaderHidden(True)
        self.wrepository.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wrepository.setIndentation(10)
        if self.multipleSelection:
            self.wrepository.setSelectionMode(QAbstractItemView.ExtendedSelection)

        layout.addWidget( self.wrepository )

        fileLayout = QHBoxLayout()
        self.filenameLabel = QLabel(self.tr('File name:'))
        fileLayout.addWidget( self.filenameLabel )
        self.filenameLineEdit = QLineEdit()
        fileLayout.addWidget( self.filenameLineEdit )
        layout.addLayout(fileLayout)
        
        # dbr13 >> Checkbox for Update --> Location
        text_update = self.tr('Search and update this new test location in all\ntestplan or testglobal?')
        text_refresh = self.tr('Update all occurences in this current test with\n this new test location?')
        self.update_location_in_tests = QCheckBox(text_update)
        self.referer_refresh_in_tests = QCheckBox(text_refresh)
        # dbr13 <<
        
        optLayout = QVBoxLayout()
        optLayout.addWidget(self.referer_refresh_in_tests)
        optLayout.addWidget(self.update_location_in_tests)

        # Buttons
        self.cancelButton = QPushButton(self.tr("Cancel"))
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addLayout(optLayout)
        buttonLayout.addWidget(self.acceptButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)

    def createConnections (self):
        """
        Create qt connections
        """
        self.wrepository.itemDoubleClicked.connect(self.accept)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.projectCombobox.currentIndexChanged.connect(self.onProjectChanged)

    def onProjectChanged(self, projectId):
        """
        Called when the project changed on the combo box
        """
        if self.projectReady:
            item_text = self.projectCombobox.itemText(projectId)
            self.RefreshRepository.emit(item_text)
        
    def iterateTree(self, item, hideTsx, hideTpx, hideTcx, hideTdx, 
                    hideTxt, hidePy, hideTux, hidePng, hideTgx, hideTax):
        """
        Iterate tree
        """
        child_count = item.childCount()
        for i in range(child_count):
            subitem = item.child(i)
            subchild_count = subitem.childCount()
            if subchild_count > 0:
                self.iterateTree(item=subitem, hideTsx=hideTsx, 
                                 hideTpx=hideTpx, hideTcx=hideTcx, 
                                 hideTdx=hideTdx, hideTxt=hideTxt,
                                 hidePy=hidePy, hideTux=hideTux, 
                                 hidePng=hidePng, hideTgx=hideTgx, 
                                 hideTax=hideTax)
            else:
                if hideTux and subitem.getExtension() == EXTENSION_TUX:
                    subitem.setHidden (True)
                elif hideTax and subitem.getExtension() == EXTENSION_TAX:
                    subitem.setHidden (True)
                elif hideTpx and subitem.getExtension() == EXTENSION_TPX:
                    subitem.setHidden (True)
                elif hideTgx and subitem.getExtension() == EXTENSION_TGX:
                    subitem.setHidden (True)
                elif hideTcx and subitem.getExtension() == EXTENSION_TCX:
                    subitem.setHidden (True)
                elif hideTsx and  subitem.getExtension() == EXTENSION_TSX:
                    subitem.setHidden (True)
                elif hideTdx and  subitem.getExtension() == EXTENSION_TDX:
                    subitem.setHidden (True)
                elif hideTxt and  subitem.getExtension() == EXTENSION_TXT:
                    subitem.setHidden (True)
                elif hidePy and  subitem.getExtension() == EXTENSION_PY:
                    subitem.setHidden (True)
                elif hidePng and  subitem.getExtension() == EXTENSION_PNG:
                    subitem.setHidden (True)
                else:
                    subitem.setHidden(False)

    def hideItems(self, hideTsx=False, hideTpx=False, hideTcx=False, hideTdx=False, hideTxt=False, 
                    hidePy=False, hideTux=False, hidePng=False, hideTgx=False, hideTax=False):
        """
        Hide items
        """
        root = self.wrepository.invisibleRootItem()
        self.iterateTree(item=root, hideTsx=hideTsx, hideTpx=hideTpx, 
                         hideTcx=hideTcx, hideTdx=hideTdx, 
                         hideTxt=hideTxt, hidePy=hidePy,
                         hideTux=hideTux, hidePng=hidePng, 
                         hideTgx=hideTgx, hideTax=hideTax)

    def accept(self):
        """
        Called on accept button
        """
        self.selectedFilenames = []
        wItems = self.wrepository.selectedItems()
        if len(wItems):
            if self.multipleSelection:
                wItemsSelected = wItems
            else:
                wItemSelected = wItems[0]
        else:
            # select the root item
            wItemSelected = self.wrepository.topLevelItem(0)

        if self.modeRepoMove:
            self.selectedFilename =  wItemSelected.getPath( withFolderName = True, withFileName = False )
            QDialog.accept(self)
        else:
            if self.modeRepoSave:
                filename = unicode(self.filenameLineEdit.text())
                if not filename:
                    return

                if '>' in filename or '<' in filename:
                    QMessageBox.warning(self, self.tr("Save") , 
                                        self.tr("Invalid filename (\/:?<>*|\").") )
                    return
                if '?' in filename or ':' in filename:
                    QMessageBox.warning(self, self.tr("Save") , 
                                        self.tr("Invalid filename (\/:?<>*|\").") )
                    return
                if '|' in filename or '*' in filename:
                    QMessageBox.warning(self, self.tr("Save") , 
                                        self.tr("Invalid filename (\/:?<>*|\").") )
                    return
                if '"' in filename or '\\' in filename or '/' in filename:
                    QMessageBox.warning(self, self.tr("Save") , 
                                        self.tr("Invalid filename (\/:?<>*|\").") )
                    return

            if self.modeRepoSave:
                fName = self.filenameLineEdit.text()
                
                # remove uneeded space, fix in v16
                fName = fName.strip()
                
                self.selectedFilename =  "%s/%s" % (    
                                                    wItemSelected.getPath( withFolderName = True, withFileName = False ), 
                                                    fName
                                                    )
                if len(self.selectedFilename):

                    QDialog.accept(self)
            else:
                if self.multipleSelection:
                    for itm in wItemsSelected:
                        selectedFilename = itm.getPath( withFolderName = False, withFileName = True )
                        if EXTENSION_TSX in self.typeFile and selectedFilename.endswith(EXTENSION_TSX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TAX in self.typeFile and selectedFilename.endswith(EXTENSION_TAX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TPX in self.typeFile and selectedFilename.endswith(EXTENSION_TPX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TGX in self.typeFile and selectedFilename.endswith(EXTENSION_TGX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TUX in self.typeFile and selectedFilename.endswith(EXTENSION_TUX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TCX in self.typeFile and selectedFilename.endswith(EXTENSION_TCX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TDX in self.typeFile and selectedFilename.endswith(EXTENSION_TDX):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_TXT in self.typeFile and selectedFilename.endswith(EXTENSION_TXT):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_PY in self.typeFile and selectedFilename.endswith(EXTENSION_PY):
                            self.selectedFilenames.append(selectedFilename)
                        elif EXTENSION_PNG in self.typeFile and selectedFilename.endswith(EXTENSION_PNG):
                            self.selectedFilenames.append(selectedFilename)
                        else:
                            pass
                    if len(self.selectedFilenames):
                        QDialog.accept(self)  
                else:
                    selectedFilename = wItemSelected.getPath( withFolderName = False, withFileName = True )
                    if EXTENSION_TSX in self.typeFile and selectedFilename.endswith(EXTENSION_TSX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TAX in self.typeFile and selectedFilename.endswith(EXTENSION_TAX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TPX in self.typeFile and selectedFilename.endswith(EXTENSION_TPX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TGX in self.typeFile and selectedFilename.endswith(EXTENSION_TGX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TUX in self.typeFile and selectedFilename.endswith(EXTENSION_TUX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TCX in self.typeFile and selectedFilename.endswith(EXTENSION_TCX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TDX in self.typeFile and selectedFilename.endswith(EXTENSION_TDX):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_TXT in self.typeFile and selectedFilename.endswith(EXTENSION_TXT):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_PY in self.typeFile and selectedFilename.endswith(EXTENSION_PY):
                        self.selectedFilename = selectedFilename
                    elif EXTENSION_PNG in self.typeFile and selectedFilename.endswith(EXTENSION_PNG):
                        self.selectedFilename = selectedFilename
                    else:
                        pass
                    if len(self.selectedFilename):
                        QDialog.accept(self)  
                
    def reloadItems(self, hideType=[]):
        """
        Reload items after the change of project
        """
        if self.modeMoveFile:
            self.hideItems(hideTsx=True, hideTpx=True, hideTcx=True, hideTdx=True, 
                            hideTux=True, hideTgx=True, hidePng=True, hideTax=True)
        
        if self.modeMoveFolder:
            self.hideItems( hideTsx=True, hideTpx=True, hideTcx=True, hideTdx=True, 
                            hideTxt=True, hidePy=True, hideTux=True, 
                            hidePng=True, hideTgx=True, hideTax=True)

        if self.modeSaveFile:
            self.hideItems(hideTsx=True, hideTpx=True, hideTcx=True, hideTdx=True, hideTxt=True, 
                            hidePy=True, hideTux=True, hidePng=True, hideTgx=True, hideTax=True)

        if self.modeGetFile:
            hideTax = True
            hideTux = True
            hideTcx = True
            hideTsx = True
            hideTpx = True
            hideTgx = True
            hideTdx = True
            hideTxt = True
            hidePy = True
            hidePng = True
            if EXTENSION_TAX in self.typeToHide: hideTax = False
            if EXTENSION_TUX in self.typeToHide: hideTux = False
            if EXTENSION_TSX in self.typeToHide: hideTsx = False
            if EXTENSION_TPX in self.typeToHide: hideTpx = False
            if EXTENSION_TGX in self.typeToHide: hideTgx = False
            if EXTENSION_TCX in self.typeToHide: hideTcx = False
            if EXTENSION_TDX in self.typeToHide: hideTdx = False
            if EXTENSION_TXT in self.typeToHide: hideTxt = False
            if EXTENSION_PY in self.typeToHide: hidePy = False
            if EXTENSION_PNG in self.typeToHide: hidePng = False
            
            self.hideItems(hideTsx=hideTsx, hideTpx=hideTpx, 
                           hideTcx=hideTcx, hideTdx=hideTdx, 
                           hideTxt=hideTxt, hidePy=hidePy, 
                           hideTux=hideTux, hidePng=hidePng, 
                           hideTgx=hideTgx, hideTax=hideTax)

    def getProjectSelection(self):
        """
        Returh the current project
        """
        return self.projectCombobox.currentText()

    def getSelection(self, withRepoName=False, withProject=False):
        """
        Returns selection

        @return:
        @rtype:
        """
        if self.multipleSelection:
            if withProject:
                selectFiles = []
                for f in self.selectedFilenames:
                    selectFiles.append( "%s:/%s" % (self.projectCombobox.currentText(), f) )
                return selectFiles
            else:
                return self.selectedFilenames
        else:
            if withProject:
                if withRepoName:
                    return "remote-tests(%s):/%s" % (self.projectCombobox.currentText(), self.selectedFilename)
                else:
                    return "%s:/%s" % (self.projectCombobox.currentText(), self.selectedFilename)
            else:
                if withRepoName:
                    return "remote-tests:/%s" % self.selectedFilename
                else:
                    return self.selectedFilename
            return self.selectedFilename

    def updateCurrentPath (self, dirValue):
        """
        Update the current path

        @param dirValue:
        @type dirValue:
        """
        self.selectedFilename = dirValue

    def setMoveFile(self, project='', update_path=False):
        """
        Set as move file

        @param filename:
        @type filename:
        """
        self.hideItems(hideTsx=True, hideTpx=True, hideTcx=True, 
                       hideTdx=True, hideTux=True, 
                       hideTgx=True, hidePng=True, hideTax=True)

        self.setDefaultProject(project=project)
        
        self.multipleSelection = False
        self.warningLabel.setText('')
        self.modeRepoMove = True
        self.modeRepoSave = False

        # new move action in 8.0.0
        self.modeMoveFile = True
        self.modeMoveFolder = False
        self.modeSaveFile = False
        self.modeGetFile = False

        self.setWindowTitle(self.tr('Move file to...'))
        self.acceptButton.setText(self.tr("Select"))
        self.filenameLabel.hide()
        self.filenameLineEdit.hide()
        
        self.update_location_in_tests.setChecked(False)
        self.referer_refresh_in_tests.setChecked(False)
        if update_path:
            self.update_location_in_tests.show()
            self.referer_refresh_in_tests.show()
        else:
            self.update_location_in_tests.hide()
            self.referer_refresh_in_tests.hide()
            
    def setMoveFolder(self, project='', update_path=False):
        """
        Set as move folder

        @param filename:
        @type filename:
        """
        self.hideItems( hideTsx=True, hideTpx=True, 
                        hideTcx=True, hideTdx=True, 
                        hideTxt=True, hidePy=True, 
                        hideTux=True, hidePng=True, 
                        hideTgx=True, hideTax=True)

        self.setDefaultProject(project=project)

        self.multipleSelection = False
        self.warningLabel.setText('')
        self.modeRepoMove = True
        self.modeRepoSave = False

        # new move action in 8.0.0
        self.modeMoveFile = False
        self.modeMoveFolder = True
        self.modeSaveFile = False
        self.modeGetFile = False

        self.setWindowTitle(self.tr('Move folder to...'))
        self.acceptButton.setText(self.tr("Select"))
        self.filenameLabel.hide()
        self.filenameLineEdit.hide()
        
        self.update_location_in_tests.setChecked(False)
        self.referer_refresh_in_tests.setChecked(False)
        if update_path:
            self.update_location_in_tests.show()
            self.referer_refresh_in_tests.show()
        else:
            self.update_location_in_tests.hide()
            self.referer_refresh_in_tests.hide()
            
    def setFilename(self, filename, project=''):
        """
        Set the filename

        @param filename:
        @type filename:
        """
        self.hideItems(hideTsx=True, hideTpx=True, 
                       hideTcx=True, hideTdx=True, 
                       hideTxt=True, hidePy=True, 
                        hideTux=True, hidePng=True, 
                        hideTgx=True, hideTax=True)

        self.setDefaultProject(project=project)

        self.multipleSelection = False
        self.warningLabel.setText('')
        self.modeRepoSave = True
        self.modeRepoMove = False

        # new move action in 8.0.0
        self.modeMoveFile = False
        self.modeMoveFolder = False
        self.modeSaveFile = True
        self.modeGetFile = False

        self.setWindowTitle(self.tr('Save to remote repository as ...'))
        self.acceptButton.setText(self.tr("Save"))
        
        # dbr13 >>
        self.update_location_in_tests.setChecked(False)
        self.update_location_in_tests.hide()
        self.referer_refresh_in_tests.setChecked(False)
        self.referer_refresh_in_tests.hide()
        # dbr13 <<
        self.filenameLabel.show()
        self.filenameLineEdit.show()
        self.filenameLineEdit.setText(filename)

    def getUpdateLocationStatus(self):
        """
        """
        return self.update_location_in_tests.isChecked()

    def getRefererRefreshStatus(self):
        """
        """
        return self.referer_refresh_in_tests.isChecked()

    def setImportFilename(self, filename, project='', update_path=False):
        """
        Set import filename

        @param filename:
        @type filename:
        """
        self.hideItems(hideTsx=True, hideTpx=True, 
                       hideTcx=True, hideTdx=True, 
                       hideTxt=True, hidePy=True, 
                       hideTux=True, hidePng=True, 
                       hideTgx=True, hideTax=True)
        self.setDefaultProject(project=project)

        self.multipleSelection = False
        self.warningLabel.setText('')
        self.modeRepoSave = True
        self.modeRepoMove = False

        # new move action in 8.0.0
        self.modeMoveFile = False
        self.modeMoveFolder = False
        self.modeSaveFile = True
        self.modeGetFile = False

        self.setWindowTitle(self.tr('Import to remote repository as ...'))
        self.acceptButton.setText(self.tr("Import"))
        self.filenameLabel.show()
        self.filenameLineEdit.show()
        self.filenameLineEdit.setText(filename)

        self.update_location_in_tests.setChecked(False)
        self.referer_refresh_in_tests.setChecked(False)
        if update_path:
            self.update_location_in_tests.show()
            self.referer_refresh_in_tests.show()
        else:
            self.update_location_in_tests.hide()
            self.referer_refresh_in_tests.hide()

    def getFilename(self, type= EXTENSION_TSX, multipleSelection=False, 
                    project='', update_path=False):
        """
        Returns filename

        @param type:
        @type type:
        """
        if len(project):
            self.setDefaultProject(project=project)
        else:
            self.setDefaultProject(project=self.getProjectSelection())
            prjId = self.owner.getProjectId(project=self.getProjectSelection())
            self.onProjectChanged(projectId=prjId)
            
        self.multipleSelection = multipleSelection
        if multipleSelection:
            self.warningLabel.setText(self.tr('(Multiple selection in tree can be done.)'))
            self.wrepository.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else:
            self.warningLabel.setText('')

        hideTax = True
        hideTux = True
        hideTcx = True
        hideTsx = True
        hideTpx = True
        hideTgx = True
        hideTdx = True
        hideTxt = True
        hidePy = True
        hidePng = True
        if not isinstance(type, list):
            type = [ type ]
        self.typeToHide = type
        if EXTENSION_TAX in type: hideTax = False
        if EXTENSION_TUX in type: hideTux = False
        if EXTENSION_TSX in type: hideTsx = False
        if EXTENSION_TPX in type: hideTpx = False
        if EXTENSION_TGX in type: hideTgx = False
        if EXTENSION_TCX in type: hideTcx = False
        if EXTENSION_TDX in type: hideTdx = False
        if EXTENSION_TXT in type: hideTxt = False
        if EXTENSION_PY in type: hidePy = False
        if EXTENSION_PNG in type: hidePng = False

        self.hideItems(hideTsx=hideTsx, hideTpx=hideTpx, 
                       hideTcx=hideTcx, hideTdx=hideTdx, 
                       hideTxt=hideTxt, hidePy=hidePy, 
                       hideTux=hideTux, hidePng=hidePng, 
                       hideTgx=hideTgx, hideTax=hideTax)

        self.modeRepoSave = False
        self.modeRepoMove = False

        # new move action in 8.0.0
        self.modeMoveFile = False
        self.modeMoveFolder = False
        self.modeSaveFile = False
        self.modeGetFile = True

        self.typeFile=type
        self.setWindowTitle(self.tr('Open from remote repository ...'))
        self.acceptButton.setText(self.tr("Open"))
        
        # dbr13>>>
        self.update_location_in_tests.setChecked(False)
        self.referer_refresh_in_tests.setChecked(False)
        if update_path:
            self.update_location_in_tests.show()
            self.referer_refresh_in_tests.show()
        else:
            self.update_location_in_tests.hide()
            self.referer_refresh_in_tests.hide()
        # dbr13 <<<
        
        self.filenameLabel.hide()
        self.filenameLineEdit.hide()

class Item(QTreeWidgetItem, Logger.ClassLogger):
    """
    Item tree widget item
    """
    def __init__( self, repo, txt, parent = None, 
                    type = QTreeWidgetItem.UserType+1, isRoot = False, isFolder=False,
                    propertiesFile=None, projectId=None, projectName=None, 
                    snapRealname=None, snapMode=False, icon=None, 
                    virtualTxt=None, reserved=False):
        """
        Item constructor

        @param repo: 
        @type repo:

        @param txt: 
        @type txt:

        @param parent: 
        @type parent:

        @param type:  10=root, 1=folder, 0=file
        @type type:

        @param isRoot: 
        @type isRoot:
        """
        QTreeWidgetItem.__init__(self, parent, type)
        
        self.repo = repo
        self.folderName = str(txt)
        self.isFolder = isFolder
        
        self.reserved = reserved
        
        self.fileName = None
        self.fileExtension = None
        self.projectId=projectId
        self.projectName=projectName

        self.propertiesFile = propertiesFile
        self.isRoot = isRoot

        self.setIcon(0, self.repo.folderIcon)
        if virtualTxt is None:
            self.setText(0, txt)
            self.setToolTip(0, txt)
        else:
            self.setText(0, virtualTxt)
            self.setToolTip(0, virtualTxt)
            
        self.snapRealname = snapRealname
        self.snapMode = snapMode

        if isRoot:  # root of the repository
            self.setExpanded(True)
            self.setIcon(0, self.repo.rootIcon)
        
        if icon is not None:
            self.setIcon(0, icon)
            
        if type == QTreeWidgetItem.UserType+0: # file
            # issue 8 fix begin
            tmp =  txt.rsplit('.', 1)
            if len(tmp) == 2:
                self.fileName = tmp[0]
                self.fileExtension = tmp[1]
            else:
                raise Exception("file type unknown")

            # issue 8 fix end 
            if self.fileExtension.lower() == EXTENSION_TUX:
                self.setIcon(0, self.repo.testUnitIcon)
            elif self.fileExtension.lower() == EXTENSION_TAX:
                self.setIcon(0, self.repo.testAbstractIcon)
            elif self.fileExtension.lower() == EXTENSION_TSX:
                self.setIcon(0, self.repo.testSuiteIcon)
            elif self.fileExtension.lower() == EXTENSION_TPX:
                self.setIcon(0, self.repo.testPlanIcon)
            elif self.fileExtension.lower() == EXTENSION_TGX:
                self.setIcon(0, self.repo.testGlobalIcon)
            elif self.fileExtension.lower() == EXTENSION_TCX:
                self.setIcon(0, self.repo.testConfigIcon)
            elif self.fileExtension.lower() == EXTENSION_TDX:
                self.setIcon(0, self.repo.testDataIcon)
            elif self.fileExtension.lower() == EXTENSION_PY and self.repo.getRepoType() == UCI.REPO_ADAPTERS :
                self.setIcon(0, self.repo.adapterIcon)
            elif self.fileExtension.lower() == EXTENSION_PY and self.repo.getRepoType() == UCI.REPO_LIBRARIES :
                self.setIcon(0, self.repo.libraryIcon)
            elif self.fileExtension.lower() == EXTENSION_TXT:
                self.setIcon(0, self.repo.txtIcon)
            elif self.fileExtension.lower() == EXTENSION_PNG:
                self.setIcon(0, self.repo.pngIcon)

            else:
                raise Exception("[item] file extension unknown: %s" % self.fileExtension)
            
            self.setText(0, self.fileName)
        
        if type == QTreeWidgetItem.UserType+100: # file snapshot
            # issue 8 fix begin
            tmp =  txt.rsplit('.', 1)
            if len(tmp) == 2:
                self.fileName = tmp[0]
                self.fileExtension = tmp[1]
            else:
                raise Exception("file type unknown")
            self.setIcon(0, self.repo.snapIcon)
            self.setText(0, self.fileName)
            
    def getExtension(self):
        """
        Returns extension
        """
        return str(self.fileExtension)

    def getPath(self, withFileName = True, withFolderName = False):
        """
        Returns path

        @param withFileName: 
        @type withFileName: 

        @param withFolderName: 
        @type withFolderName:
        """
        p = self.parent()
        
        # in snap mode, the first parent is the file, 
        # so we get the second parent (a folder)
        if self.snapMode: p = p.parent()
            
        if withFolderName:
            path = [ self.folderName ]
        else: 
            path = [ ]
        
        if withFileName:
            path.append( "%s.%s" % ( self.fileName, self.fileExtension) )
        
        while p != None:
            path.append( str(p.folderName) )
            p = p.parent()
        
        # remove root dir
        path = path[:-1]
        

        path.reverse()
        return '/'.join(path)

class DuplicateDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Duplicate dialog
    """
    def __init__(self, currentName, folder, parent=None, projects=[], 
                    defaultProject=1, repoType=0, currentPath=''):
        """
        Dialog to duplicate file or folder

        @param currentName: 
        @type currentName: 

        @param folder: 
        @type folder:

        @param parent: 
        @type parent:   
        """
        super(DuplicateDialog, self).__init__(parent)
        self.dataCurrent = currentName
        self.currentPath = currentPath
        self.isFolder = folder
        self.repoType = repoType
        self.createDialog()
        self.createConnections()

        self.initProjects(projects=projects, defaultProject=defaultProject)
        
        # new in v12, auto select of the new text 
        self.newnameEdit.setFocus()
        self.newnameEdit.selectAll()
        
    def initProjects(self, projects=[], defaultProject=1):
        """
        Initialize projects
        """
        self.projectCombobox.clear()
        if self.repoType  == UCI.REPO_TESTS:
            self.projectCombobox.setEnabled(True)
        else:
            self.projectCombobox.setEnabled(False)

        # insert data
        pname = ''
        for p in projects:
            self.projectCombobox.addItem ( p['name']  )
            if defaultProject == p['project_id']:
                pname = p['name']
        
        for i in xrange(self.projectCombobox.count()):
            item_text = self.projectCombobox.itemText(i)
            if pname == item_text:
                self.projectCombobox.setCurrentIndex(i)

    def createDialog (self):
        """
        Create qt dialog
        """
        self.currentLabel = QLabel(self.tr("Current name:") )
        self.currentEdit = QLineEdit()
        self.currentEdit.setText(self.dataCurrent)
        self.currentEdit.setReadOnly(True)
        self.currentEdit.setStyleSheet("QLineEdit { background-color : #F0F0F0; }");

        self.currentPathLabel = QLabel(self.tr("Current path:") )
        self.currentPathEdit = QLineEdit()
        self.currentPathEdit.setText(self.currentPath)
        self.currentPathEdit.setReadOnly(True)
        self.currentPathEdit.setStyleSheet("QLineEdit { background-color : #F0F0F0; }");
        
        self.newLabel = QLabel(self.tr("Destination name:") )
        self.newnameEdit = QLineEdit()
        self.newnameEdit.setText(self.dataCurrent)
        
        self.newPathLabel = QLabel(self.tr("Destination path:") )
        self.newPathEdit = QLineEdit()
        self.newPathEdit.setText(self.currentPath)
        
        self.projectLabel = QLabel(self.tr("Destination project:") )
        self.projectCombobox = QComboBox(self)
        self.projectCombobox.setEnabled(False)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        separator = QFrame()
        separator.setGeometry(QRect(110, 221, 51, 20))
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.currentLabel)
        mainLayout.addWidget(self.currentEdit)
        
        mainLayout.addWidget(self.currentPathLabel)
        mainLayout.addWidget(self.currentPathEdit)
        
        mainLayout.addWidget(separator)
        
        mainLayout.addWidget(self.newLabel)
        mainLayout.addWidget(self.newnameEdit)
        
        mainLayout.addWidget(self.newPathLabel)
        mainLayout.addWidget(self.newPathEdit)
        
        mainLayout.addWidget(self.projectLabel)
        mainLayout.addWidget(self.projectCombobox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        if self.isFolder:
            self.setWindowTitle(self.tr("Duplicate folder"))
        else:
            self.setWindowTitle(self.tr("Duplicate file"))
        
        self.resize(600, 100)

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.acceptName)
        self.buttonBox.rejected.connect(self.reject)

    def acceptName(self):
        """
        Accept name
        """
        filename = self.newnameEdit.text()

        if not len(filename):
            QMessageBox.warning(self, self.tr("Rename") , self.tr("New value cannot be empty!") )
            return

        if '>' in filename or '<' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        if '?' in filename or ':' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        if '|' in filename or '*' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        if '"' in filename or '\\' in filename or '/' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        self.accept()

    def getNewPath(self):
        """
        Return the new path
        """
        path = self.newPathEdit.text()
        return str(path)
        
    def getDuplicateName(self):
        """
        Return the duplicate name
        """
        return self.newnameEdit.text()

    def getProjectSelected(self):
        """
        Return the selection project
        """
        project = self.projectCombobox.currentText()
        return str(project)


# dbr13 >>>

class FindTestFileUsageWTree(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Display files tree using current test file
    """
    def __init__(self, result_list, file_path, file_projectid, parent=None):
        """
        @param response: onFindTestFileUsage
        @type response: dict

        @param parent:
        @type parent
        """
        super(FindTestFileUsageWTree, self).__init__(parent)
        self.usage_list = result_list
        self.usage_file_path = file_path
        self.usage_pr_id = file_projectid
        
        self.createWidgets()
        self.createConnections()
        self.createTree()

    def center(self):
        """
        Center the dialog
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createWidgets(self):
        """
        create dialog
        """
        self.test_usage_tree = QTreeWidget(self)
        self.test_usage_tree.move(25, 25)
        self.test_usage_tree.setHeaderHidden(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.test_usage_tree)

        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Find Usage Tree"))
        # self.resize(1280, 720)
        # self.setWindowIcon(QIcon(":/find-usage@1x.png"))

        self.resize(700, 700)
        
    def createConnections(self):
        """
        Create connections
        """
        self.test_usage_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self):
        """
        """
        item = self.test_usage_tree.currentItem()
        if item.type == 'usage_line':
            RCI.instance().openFileTests(projectId=int(item.project_id), 
                                         filePath=item.path, 
                                         extra={'subtest_id': "%s" % item.id})

    def createTree(self):
        """
        This is not what I want.
        """
        for usage in self.usage_list:
            if usage['content']:
                
                # create the project item
                item_pr = QTreeWidgetItem([usage['name']])
                item_pr.path = None
                item_pr.project_id = usage['project_id']
                item_pr.prject_name = usage['name']
                item_pr.type = 'project'
                item_pr.setIcon(0, QIcon(":/folders.png"))

                # create the result
                for file in usage['content']:
                    item_file = QTreeWidgetItem([file['file_path']])
                    item_file.path = file['file_path']
                    item_file.type = 'file'
                    item_file.ext = item_file.path.rsplit('.')[-1]
                    item_file.setIcon(0, QIcon(":/%s48.png" % item_file.ext))
                    item_pr.addChild(item_file)
                    if usage['content']:
                        for line_id in file['lines_id']:
                            item_line_id = QTreeWidgetItem(['%s: %s' % (line_id, self.usage_file_path)])
                            item_line_id.path = item_file.path
                            item_line_id.project_id = item_pr.project_id
                            item_line_id.type = 'usage_line'
                            item_line_id.id = line_id
                            item_line_id.ext = self.usage_file_path.rsplit('.')[-1]
                            item_line_id.setIcon(0, QIcon(":/%s48.png" % item_line_id.ext))
                            item_file.addChild(item_line_id)

                self.test_usage_tree.addTopLevelItem(item_pr)
                item_pr.setExpanded(True)
                
class UpdateAdapterLibraryDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Update used Adapter and Library in the test file
    """
    def __init__(self, parent=None):
        """
        Dialog to update used Adapter or Library in the test file

        @param parent:
        @type parent
        """
        super(UpdateAdapterLibraryDialog, self).__init__(parent)
        self.createDialog()
        self.createConnections()

    def createDialog(self):
        """
        create dialog
        """

        self.adapter = QLabel(self.tr('Update Adapter: '))
        self.update_adapter_combobox = QComboBox(self)
        self.update_adapter_combobox.clear()
        self.update_adapter_combobox.addItem('None')
        serverSutAdps = Settings.instance().serverContext['adapters']
        self.update_adapter_combobox.addItems(serverSutAdps.split(','))


        self.library = QLabel(self.tr('Update Library: '))
        self.update_library_combobox = QComboBox(self)
        self.update_library_combobox.clear()
        self.update_library_combobox.addItem('None')
        serverSutLibs = Settings.instance().serverContext['libraries']
        self.update_library_combobox.addItems(serverSutLibs.split(','))

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet("""QDialogButtonBox { 
                    dialogbuttonbox-buttons-have-icons: 1;
                    dialog-ok-icon: url(:/ok.png);
                    dialog-cancel-icon: url(:/ko.png);
                }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.adapter)
        mainLayout.addWidget(self.update_adapter_combobox)
        mainLayout.addWidget(self.library)
        mainLayout.addWidget(self.update_library_combobox)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Update Adapter/Library"))

    def createConnections(self):
        """
        Create connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
# dbr13 <<<

class RenameDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Rename dialog
    """
    def __init__(self, currentName, folder, parent=None, show_update_location=False):
        """
        Dialog to rename file or folder

        @param currentName: 
        @type currentName: 

        @param folder: 
        @type folder:

        @param parent: 
        @type parent: 
        """
        super(RenameDialog, self).__init__(parent)
        self.dataCurrent = currentName
        self.isFolder = folder
        self.show_update_location = show_update_location
        
        self.createDialog()
        self.createConnections()
        
        # new in v12, auto select of the new text 
        self.newnameEdit.setFocus()
        self.newnameEdit.selectAll()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.currentLabel = QLabel(self.tr("Current name:") )
        self.currentEdit = QLineEdit(self)
        self.currentEdit.setText(self.dataCurrent)
        self.currentEdit.setReadOnly(True)
        self.currentEdit.setStyleSheet("QLineEdit { background-color : #F0F0F0; }");

        self.newLabel = QLabel(self.tr("New name:") )
        self.newnameEdit = QLineEdit(self)
        self.newnameEdit.setText(self.dataCurrent)

        self.nameUppercase = QCheckBox(self.tr("Change the new name in uppercase"))
        
        # dbr13 >>
        self.update_location = QCheckBox(self.tr('Search and update test location in all testplan or testglobal?'))
        # dbr13 <<
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.currentLabel)
        mainLayout.addWidget(self.currentEdit)
        mainLayout.addWidget(self.newLabel)
        mainLayout.addWidget(self.newnameEdit)
        mainLayout.addWidget(self.nameUppercase)
        # dbr13 >>>
        mainLayout.addWidget(self.update_location)
        # dbr13 <<<
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        if self.show_update_location:
            self.update_location.show()
        else:
            self.update_location.hide()
            
        if self.isFolder:
            self.setWindowTitle(self.tr("Rename folder"))
            # dbr13 currently it doesn't work with folders
            self.update_location.hide()
        else:
            self.setWindowTitle(self.tr("Rename file"))
            
        self.resize(600, 100)

    def createConnections (self):
        """
        Create qt connections
        """
        self.nameUppercase.stateChanged.connect(self.onUppercaseChanged)
        self.buttonBox.accepted.connect(self.acceptName)
        self.buttonBox.rejected.connect(self.reject)

    def onUppercaseChanged(self, state):
        """
        on uppercase changed
        """
        if state == 2:
            filename = self.newnameEdit.text()
            filename = filename.upper()
            self.newnameEdit.setText(filename)
            
    def acceptName(self):
        """
        Called on accept
        """
        filename = self.newnameEdit.text()

        if not len(filename):
            QMessageBox.warning(self, self.tr("Rename") , self.tr("New value cannot be empty!") )
            return

        if '>' in filename or '<' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        if '?' in filename or ':' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        if '|' in filename or '*' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        if '"' in filename or '\\' in filename or '/' in filename:
            QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name (\/:?<>*|\").") )
            return
        self.accept()

    def getNewName(self):
        """
        Returns the new name
        """
        return self.newnameEdit.text()

    def getUpdateLocationStatus(self):
        """
        """
        return self.update_location.isChecked()
        
class TreeWidgetRepository(QTreeWidget):
    """
    Tree widget repository
    """
    def __init__(self, parent, repoType):
        """
        Treewidget constructor

        @param parent: 
        @type parent:

        @param repoType: 
        @type repoType:
        """
        QTreeWidget.__init__(self, parent)
        self.repoType = repoType
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.mine_flag = Settings.instance().readValue( key = 'Common/acronym' ).lower()
        
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setExpandsOnDoubleClick(False)

    def startDrag(self, dropAction):
        """
        Start drag

        @param dropAction: 
        @type dropAction:
        """
        if self.itemCurrent is not None:
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
                pathFile = self.itemCurrent.getPath(withFileName = True)
                if len(pathFile) > 1 :
                    meta = {}
                    meta['repotype'] = self.repoType
                    meta['pathfile'] = pathFile
                    meta['ext'] = self.itemCurrent.fileExtension
                    meta['projectid'] = int(self.itemCurrent.projectId)
                    meta['filename'] = self.itemCurrent.fileName
                    meta['path'] = self.itemCurrent.getPath(withFileName = False, withFolderName = False)

                    # create mime data object
                    mine_data = 'application/x-%s-repo-openfile' % self.mine_flag
                    mime = QMimeData()
                    mime.setData(mine_data, pickle.dumps(meta) )
                    # start drag 
                    drag = QDrag(self)
                    drag.setMimeData(mime) 
                    
                    drag.exec_(Qt.CopyAction)

    def dragEnterEvent(self, event):
        """
        Drag enter

        @param event: 
        @type event:
        """
        mine_data = 'application/x-%s-repo-openfile' % self.mine_flag
        if event.mimeData().hasFormat(mine_data):
            event.accept()
        else:
            QTreeWidget.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        """
        Drag move

        @param event: 
        @type event:
        """
        mine_data = "application/x-%s-repo-openfile" % self.mine_flag
        if event.mimeData().hasFormat(mine_data):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            QTreeWidget.dragMoveEvent(self, event)

    def dropEvent(self, event):
        """
        On drop event

        @param event: 
        @type event:
        """
        if event.source() == self:
            QAbstractItemView.dropEvent(self, event)

    def dropMimeData(self, parent, row, data, action):
        """
        On drop mime data

        @param parent: 
        @type parent:

        @param row: 
        @type row:

        @param data: 
        @type data:

        @param action: 
        @type action:
        """
        if parent is None:
            return False
        if parent.type() == QTreeWidgetItem.UserType+0: # file
            return False
        else:
            newPath = parent.getPath(withFileName = False, withFolderName = True)
            meta_data = data.data("application/x-%s-repo-openfile" %  self.mine_flag )
            data = pickle.loads(meta_data)
            if self.parent().projectSupport:
                project = self.parent().getCurrentProject()
                projectid = self.parent().getProjectId(project=str(project))
                self.parent().moveRemoteFile(currentName=data['filename'], 
                                             currentPath=data['path'],
                                             currentExtension=data['ext'], 
                                             newPath=newPath,
                                             project=projectid, 
                                             newProject=projectid)
            else:
                self.parent().moveRemoteFile(currentName=data['filename'], 
                                             currentPath=data['path'],
                                             currentExtension=data['ext'], 
                                             newPath=newPath)
            return False

    def mousePressEvent(self, event):
        """
        On mouse press
        """
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)

class PropertiesDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Properties dialog
    """
    def __init__(self, parent, item, repoType):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(PropertiesDialog, self).__init__(parent)
        self.parent = parent
        self.item = item
        self.repoType = repoType
        self.createDialog()
        self.createConnections()
        self.setDatas()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.labelName = QLabel()
        self.labelName.setTextInteractionFlags( Qt.TextSelectableByMouse  | Qt.TextSelectableByKeyboard )
        self.labelIcon = QLabel()
        self.labelProject = QLabel()
        layoutName = QFormLayout()
        
        layoutName.addRow(  QLabel(self.tr("File:")) , self.labelName)
        layoutName.addRow(  QLabel(self.tr("Icon:")) , self.labelIcon )
        layoutName.addRow(  QLabel(self.tr("Project:")) , self.labelProject)

        sep1 = QFrame()
        sep1.setGeometry(QRect(110, 221, 51, 20))
        sep1.setFrameShape(QFrame.HLine)
        sep1.setFrameShadow(QFrame.Sunken)

        self.labelSize = QLabel()
        self.labelLocation = QLabel()
        self.labelLocation.setTextInteractionFlags( Qt.TextSelectableByMouse  | Qt.TextSelectableByKeyboard )
        self.labelType = QLabel()
        self.layoutSize = QFormLayout()
        self.layoutSize.addRow( QLabel(self.tr("Type:")), self.labelType )
        self.layoutSize.addRow( QLabel(self.tr("Location:")), self.labelLocation )
        self.layoutSize.addRow( QLabel(self.tr("Size:")), self.labelSize  )
        
        sep2 = QFrame()
        sep2.setGeometry(QRect(110, 221, 51, 20))
        sep2.setFrameShape(QFrame.HLine)
        sep2.setFrameShadow(QFrame.Sunken)

        self.labelModif = QLabel()

        layoutDate = QFormLayout()
        layoutDate.addRow( QLabel(self.tr("Modified:")), self.labelModif )

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layoutName)
        mainLayout.addWidget(sep1)
        mainLayout.addLayout(self.layoutSize)
        mainLayout.addWidget(sep2)
        mainLayout.addLayout(layoutDate)

        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        self.resize(300, 200)
        self.setWindowTitle(self.tr("Repository > File Properties") )

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)

    def setDatas(self):
        """
        Set datas
        """
        if self.item is None:
            return
        
        if 'type' in self.item.propertiesFile:
            if self.item.propertiesFile['type'] == "folder":
                self.setWindowTitle( self.tr("Repository > Folder Properties") )
                
                txtContains = "%s Files, %s Folders" % (self.item.propertiesFile['nb-files'],
                                                        self.item.propertiesFile['nb-folders'])
                self.layoutSize.addRow( QLabel("Contains:"), QLabel( txtContains ) )
                style = self.parent.style()

                folder_icon = QIcon( QIcon(":/folder_base.png")  )
                self.labelIcon.setPixmap( folder_icon.pixmap(QSize(16, 16)) )
                
                self.labelName.setText( self.item.folderName )
                self.labelType.setText('Folder')
                self.labelLocation.setText( "/%s" % self.item.getPath(withFileName = False) ) 


        if 'size' in self.item.propertiesFile:
            self.labelSize.setText(  QtHelper.bytes2human( int(self.item.propertiesFile['size']) )  )
        
        if 'modification' in self.item.propertiesFile:
            local_time = time.localtime( self.item.propertiesFile['modification'] )
            text_time = time.strftime( "%Y-%m-%d %H:%M:%S", local_time )
            self.labelModif.setText( text_time  )

        if self.item.fileName is not None:
            self.labelName.setText( self.item.fileName )
            self.labelLocation.setText( "/%s" % self.item.getPath(withFileName = False) ) 
        
        if self.item.fileExtension is not None:
            if self.item.fileExtension == EXTENSION_TUX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TUX ) )
                self.labelType.setText(self.tr('Test Unit Xml'))
            elif self.item.fileExtension == EXTENSION_TAX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TAX ) )
                self.labelType.setText(self.tr('Test Abstract Xml'))
            elif self.item.fileExtension == EXTENSION_TSX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TSX ) )
                self.labelType.setText(self.tr('Test Suite Xml'))
            elif self.item.fileExtension == EXTENSION_TPX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TPX ) )
                self.labelType.setText(self.tr('Test Plan Xml'))
            elif self.item.fileExtension == EXTENSION_TGX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TGX ) )
                self.labelType.setText(self.tr('Test Global Xml'))
            elif self.item.fileExtension == EXTENSION_TCX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TCX) )
                self.labelType.setText(self.tr('Test Config Xml'))
            elif self.item.fileExtension == EXTENSION_TDX:
                self.labelIcon.setPixmap(QPixmap(":/%s.png" % EXTENSION_TDX) )
                self.labelType.setText(self.tr('Test Data Xml'))
            elif self.item.fileExtension == EXTENSION_PY and self.repoType==UCI.REPO_ADAPTERS:
                self.labelIcon.setPixmap(QPixmap(":/file-adp2.png"))
                self.labelType.setText(self.tr('Adapter'))
            elif self.item.fileExtension == EXTENSION_PY and self.repoType==UCI.REPO_LIBRARIES:
                self.labelIcon.setPixmap(QPixmap(":/file-lib-adp.png"))
                self.labelType.setText(self.tr('Library'))
            elif self.item.fileExtension == EXTENSION_TXT:
                self.labelIcon.setPixmap(QPixmap(":/file-txt.png"))
                self.labelType.setText(self.tr('Text'))
            elif self.item.fileExtension == EXTENSION_PNG:
                self.labelIcon.setPixmap(QPixmap(":/png.png"))
                self.labelType.setText(self.tr('Image Png'))
            else:
                self.labelType.setText(self.tr('Unknown'))

class EventFilterComboBox(QObject):
    """
    Event filter for combobox project list
    Disable wheel mouse to prevent some bad behaviour
    """
    def eventFilter(self, filteredObj, event):
        """
        On event filter
        """
        if event.type() == QEvent.Wheel:
            event.ignore()
            return True
        else:
            return QObject.eventFilter(self, filteredObj, event)
        
class Repository(QWidget, Logger.ClassLogger):
    """
    Repository widget
    """
    def __init__(self, parent = None,  withFile = True, repoType=0, projectSupport=False):
        """
        Repository class 

        @param parent: 
        @type parent:

        @param withFile: 
        @type withFile:

        @param repoType: 
        @type repoType:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.withFile = withFile
        self.repoType = repoType
        self.projectSupport = projectSupport
        self.projectClicked = False
        self.initializeCalled = False
        self.projects = []
        self.treeIndexes = []

        self.repositoryPath = Settings.instance().readValue( key = 'Repositories/local-repo' )
        self.wrepository = None
        
        style = self.parent.style()
        self.folderIcon = QIcon( QIcon(":/folder_base.png")  )
        self.rootIcon = QIcon()
        self.rootIcon.addPixmap( style.standardPixmap(QStyle.SP_DriveNetIcon) )
        self.testAbstractIcon = QIcon(":/%s.png" % EXTENSION_TAX)
        self.testUnitIcon = QIcon(":/%s.png" % EXTENSION_TUX)
        self.testSuiteIcon = QIcon(":/%s.png" % EXTENSION_TSX)
        self.testPlanIcon = QIcon(":/%s.png" % EXTENSION_TPX)
        self.testGlobalIcon = QIcon(":/%s.png" % EXTENSION_TGX)
        self.testConfigIcon = QIcon(":/%s.png" % EXTENSION_TCX)
        self.testDataIcon = QIcon(":/%s.png" % EXTENSION_TDX)
        self.pngIcon = QIcon(":/%s.png" % EXTENSION_PNG)
        self.adapterIcon = QIcon(":/file-adp2.png")
        self.libraryIcon = QIcon(":/file-lib-adp.png")
        self.txtIcon = QIcon(":/file-txt.png")
        self.snapIcon = QIcon(":/snapshot.png")
        self.projectInitialized = False

        # new in v17
        self.trashIcon = QIcon(":/trash.png")
        self.sandboxIcon = QIcon(":/folder_add.png")
        self.reservedItems = []
        # end of new
        
        self.createWidgets()
        self.__createConnections()
        self.__createActions()

        self.createToolbarRemote()

    def createToolbarRemote(self):
        """
        Toolbar creation
            
        ||--|||
        ||  |||
        ||--|||
        """
        self.dockToolbarRemote.setObjectName("Remote Repository toolbar")
        self.dockToolbarRemote.addAction(self.refreshRemoteAction)
        self.dockToolbarRemote.addSeparator()
        self.dockToolbarRemote.addAction(self.runAction)
        self.dockToolbarRemote.addSeparator()
        self.dockToolbarRemote.addAction(self.addDirAction)
        self.dockToolbarRemote.addAction(self.delDirAction)
        self.dockToolbarRemote.addAction(self.delAllDirAction)
        self.dockToolbarRemote.addAction(self.deleteFileAction)
        self.dockToolbarRemote.addSeparator()
        self.dockToolbarRemote.addAction(self.renameAction)
        self.dockToolbarRemote.addAction(self.duplicateDirAction)
        self.dockToolbarRemote.addAction(self.duplicateFileAction)
        self.dockToolbarRemote.addSeparator()
        self.dockToolbarRemote.addAction(self.moveFileAction)
        self.dockToolbarRemote.addAction(self.moveFolderAction)
        self.dockToolbarRemote.addSeparator()
        # dbr13 >>>
        self.dockToolbarRemote.addAction(self.updateAdapterLibraryAction)
        self.dockToolbarRemote.addAction(self.findUsageAction)
        self.dockToolbarRemote.addSeparator()
        # dbr13 <<<
        self.dockToolbarRemote.setIconSize(QSize(16, 16))

    def itemEventExpandedCollapsed(self, item):
        """
        On item event expanded or collapsed
        """
        if self.initializeCalled:
            return
        self.treeIndexes = []
        for i in xrange( self.wrepository.topLevelItemCount() ):
            itm = self.wrepository.topLevelItem( i )
            if itm.isExpanded():
                subRet = self.__itemEventExpandedCollapsed(itm)
                self.treeIndexes.append( (i,subRet) )

    def __itemEventExpandedCollapsed(self, itm):
        """
        Sub function of item event expanded or collapsed
        """
        subRet = []
        for j in xrange(itm.childCount()):
            child = itm.child(j)
            if child.isExpanded():
                if child.childCount():
                    subRet.append( (j, self.__itemEventExpandedCollapsed(itm=child) ) )
                else:
                    subRet.append( (j,[]) )
        return subRet
 
    def expandAuto(self):
        """
        Expand auto
        """
        for  v in self.treeIndexes:
            i, subIdx = v
            itm = self.wrepository.topLevelItem( i)
            if itm is not None:
                itm.setExpanded(True)
                if len(subIdx):
                    self.__expandAuto(itm=itm, indexes=subIdx)
   
    def __expandAuto(self, itm, indexes):
        """
        Sub function of expand auto
        """
        for j in indexes:
            i, subIdx = j
            child = itm.child(i)
            if child is not None:
                child.setExpanded(True)
                if len(subIdx):
                    self.__expandAuto(itm=child,indexes=subIdx)
                    
    def getRepoType(self):
        """
        Returns the type of the repository
        """
        return self.repoType

    def keyPressEvent(self, event):
        """
        Called on key press

        @param event: 
        @type event:
        """ 
        return QWidget.keyPressEvent(self, event)

    def __createActions (self):
        """
        Create qt actions
        Private function

        Actions defined:
         * open
         * save as
        """
        # remote actions
        self.refreshRemoteAction = QtHelper.createAction(self, 
                                                self.tr("&Refresh"), 
                                                self.__refreshAll, 
                                                icon = QIcon(":/refresh.png"), 
                                                tip = self.tr('Refresh remote repository content') )
        self.addDirAction = QtHelper.createAction(self, self.tr("&Add Folder"), 
                                                self.__createItem, 
                                                icon = QIcon(":/folder_add.png"), 
                                                tip = self.tr('Create new folder') )
        self.delDirAction = QtHelper.createAction(self, self.tr("&Delete"), 
                                                self.__deleteItem, 
                                                shortcut = "Ctrl+Alt+D", 
                                                icon = QIcon(":/folder_delete.png"), 
                                                tip = self.tr('Add the selected directory') )
        self.delAllDirAction = QtHelper.createAction(self, self.tr("&Delete All"), 
                                                self.__deleteAllItem, 
                                                shortcut = "Ctrl+Alt+A", 
                                                icon = QIcon(":/folder_delete_all.png"), 
                                                tip = self.tr('Delete all folder and contents') )
        self.renameAction = QtHelper.createAction(self, self.tr("&Rename"), 
                                                self.__renameItem, 
                                                shortcut = "Ctrl+Alt+R",
                                                icon = QIcon(":/rename.png"), 
                                                tip = self.tr('Rename') )
        # dbr13 >>>
        self.updateAdapterLibraryAction = QtHelper.createAction(self, self.tr("&Update Adapter/Library"),
                                                                self.__update_adapter_library,
                                                                icon=QIcon(":/update-adapter.png"),
                                                                tip=self.tr('Update Adapters/Library'))
        self.findUsageAction = QtHelper.createAction(self, self.tr("&Find Usage..."),
                                                     self.__find_usage,
                                                     icon=QIcon(":/find-usage@1x.png"),
                                                     tip=self.tr('Find test file usage'))
        # dbr13 <<<
        
        self.duplicateDirAction = QtHelper.createAction(self, 
                                                self.tr("&Duplicate Folder"), 
                                                self.__duplicateItem, 
                                                icon = QIcon(":/duplicate_folder.png"), 
                                                tip = self.tr('Duplicate folder') )
        self.duplicateFileAction = QtHelper.createAction(self, 
                                                self.tr("&Duplicate File"), 
                                                self.__duplicateItem, 
                                                icon = QIcon(":/filenew2.png"), 
                                                tip = self.tr('Duplicate file') )
        self.deleteFileAction = QtHelper.createAction(self, 
                                                self.tr("&Delete File"), 
                                                self.__deleteItem, 
                                                shortcut = "Ctrl+Alt+D", 
                                                icon = QIcon(":/delete_file.png"), 
                                                tip = self.tr('Delete File') )
        self.moveFileAction = QtHelper.createAction(self, 
                                                self.tr("&Move File"), 
                                                self.__moveItem, 
                                                icon = QIcon(":/move_file.png"), 
                                                tip = self.tr('Move the selected file') )
        self.moveFolderAction = QtHelper.createAction(self, 
                                                self.tr("&Move Folder"), 
                                                self.__moveItem, 
                                                icon = QIcon(":/move_folder.png"), 
                                                tip = self.tr('Move the selected folder') )
        self.openFileAction = QtHelper.createAction(self, 
                                                self.tr("&Open File"), 
                                                self.__openItem, 
                                                icon = None, 
                                                tip = self.tr('Open the selected file') )
        self.openPropertiesAction = QtHelper.createAction(self, 
                                                self.tr("&Properties"), 
                                                self.__openProperties, 
                                                icon = None, 
                                                tip = self.tr('Open properties') )
        self.snapshotAction = QtHelper.createAction(self, 
                                                self.tr("&Snapshot"), 
                                                self.__addSnapshot, 
                                                icon = QIcon(":/snapshot.png"), 
                                                tip = self.tr('Snapshot manager') )
        self.snapshotAddAction = QtHelper.createAction(self, 
                                                self.tr("&Create..."), 
                                                self.__addSnapshot, 
                                                icon = None, 
                                                tip = self.tr('Add snapshot') )
        self.snapshotRestoreAction = QtHelper.createAction(self, 
                                                self.tr("&Restore..."), 
                                                self.__restoreSnapshot, 
                                                icon = None, 
                                                tip = self.tr('Restore snapshot') )
        self.snapshotDeleteAction = QtHelper.createAction(self, 
                                                self.tr("&Delete..."), 
                                                self.__deleteSnapshot, 
                                                icon = None, 
                                                tip = self.tr('Delete snapshot') )
        self.snapshotDeleteAllAction = QtHelper.createAction(self, 
                                                self.tr("&Delete All"), 
                                                self.__delAllSnapshots, 
                                                icon = None, 
                                                tip = self.tr('Delete All') )
        menu1 = QMenu(self)
        menu1.addAction( self.snapshotAddAction )
        menu1.addAction( self.snapshotDeleteAllAction )
        self.snapshotAction.setMenu(menu1) 
        
        self.saveAsFileAction = QtHelper.createAction(self, 
                                                self.tr("&Save As"), 
                                                self.__saveasItem, 
                                                icon = None, 
                                                tip = self.tr('Save the file as') )
        self.runAction = QtHelper.createAction(self, 
                                                self.tr("&Execute"), 
                                                self.__runItem, 
                                                shortcut = "Ctrl+Alt+E", 
                                                icon = QIcon(":/test-play.png"), 
                                                tip = self.tr('Execute the test') )
        self.expandSubtreeAction = QtHelper.createAction(self, 
                                                self.tr("&Expand folder..."), 
                                                self.expandSubFolder, 
                                                icon = None, 
                                                tip = self.tr('Expand folder') )
        self.expandAllAction = QtHelper.createAction(self, 
                                                self.tr("&Expand All"), 
                                                self.expandAllFolders, 
                                                icon = None, 
                                                tip = self.tr('Expand all folders') )
        self.collapseAllAction  = QtHelper.createAction(self, 
                                                self.tr("&Collapse All"), 
                                                self.collapseAllFolders, 
                                                icon = None, 
                                                tip = self.tr('Collapse all folder') )

        self.moreCreateActions()
        self.defaultActions()

    def expandAllFolders(self):
        """
        Expand all folders
        """
        self.wrepository.expandAll()

    def collapseAllFolders(self):
        """
        Collapse all folders
        """
        self.wrepository.collapseAll()

    def expandSubFolder(self):
        """
        Expand sub folder
        """
        currentItem = self.wrepository.currentItem()
        if currentItem is not None:
            self.expandItem(itm=currentItem)

    def expandItem(self, itm):
        """
        Expand item
        """
        itm.setExpanded(True)
        if itm.childCount() > 0:
            for i in xrange( itm.childCount() ):
                itm.child(i).setExpanded(True)
                if itm.child(i).childCount() > 0:
                    self.expandItem(itm=itm.child(i))

    def moreCreateActions(self):
        """
        Called after create actions function
        You should override this method
        """
        pass

    def defaultActions(self):
        """
        Set default actions
        """
        self.saveAsFileAction.setEnabled(False)
        self.refreshRemoteAction.setEnabled(False)
        self.addDirAction.setEnabled(False)
        self.deleteFileAction.setEnabled(False)
        self.delDirAction.setEnabled(False)
        self.duplicateFileAction.setEnabled(False)
        self.duplicateDirAction.setEnabled(False)
        self.renameAction.setEnabled(False)
        self.delAllDirAction.setEnabled(False)
        self.moveFileAction.setEnabled(False)
        self.moveFolderAction.setEnabled(False)
        self.openFileAction.setEnabled(False)
        self.openPropertiesAction.setEnabled(False)
        self.snapshotAction.setEnabled(False)
        self.expandSubtreeAction.setEnabled(False)
        self.expandAllAction.setEnabled(False)
        self.collapseAllAction.setEnabled(False)
        self.runAction.setEnabled(False)

        # dbr13 >>>
        self.updateAdapterLibraryAction.setEnabled(False)
        self.findUsageAction.setEnabled(False)
        # dbr13 <<<
        
        self.moreDefaultActions()
    
    def moreDefaultActions(self):
        """
        Called after default actions function
        You should override this method
        """
        pass

    def onPopupMenu(self, pos):
        """
        Called on popup menu displayed by user

        @param pos: 
        @type pos:
        """
        item = self.wrepository.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.itemCurrent = item
            self.wrepository.itemCurrent = item
            if item.type() == QTreeWidgetItem.UserType+0: # file
                self.menu.addAction( self.openFileAction )
                self.menu.addSeparator()
                self.menu.addAction( self.deleteFileAction )
                self.menu.addSeparator()
                self.menu.addAction( self.renameAction )
                self.menu.addAction( self.duplicateFileAction )
                self.menu.addAction( self.moveFileAction )
                self.menu.addSeparator()
                self.menu.addAction( self.runAction )
                self.menu.addSeparator()
                self.menu.addAction( self.openPropertiesAction )
                self.menu.addSeparator()
                self.menu.addAction( self.snapshotAction )
                # dbr13 >>>
                self.menu.addSeparator()
                self.menu.addAction(self.findUsageAction)
                # dbr13 <<<
                
            if item.type() == QTreeWidgetItem.UserType+100: # file snapshot
                self.menu.addAction( self.snapshotDeleteAction )
                self.menu.addAction( self.snapshotRestoreAction )
                
            if item.type() == QTreeWidgetItem.UserType+1: # folder
                self.menu.addAction( self.expandSubtreeAction )
                self.menu.addSeparator()
                self.menu.addAction( self.addDirAction )
                self.menu.addSeparator()
                self.menu.addAction( self.delDirAction )
                self.menu.addAction( self.delAllDirAction ) # only for admin
                self.menu.addSeparator()
                self.menu.addAction( self.renameAction )
                self.menu.addAction( self.duplicateDirAction )
                self.menu.addAction( self.moveFolderAction )
                self.menu.addSeparator()
                self.menu.addAction( self.openPropertiesAction )
                # dbr13 >>>
                self.menu.addAction(self.updateAdapterLibraryAction)
                self.menu.addSeparator()
                # dnr13 <<<
                
            if item.type() == QTreeWidgetItem.UserType+10 : # root
                self.menu.addAction( self.refreshRemoteAction )
                self.menu.addSeparator()
                self.menu.addAction( self.expandAllAction )
                self.menu.addAction( self.collapseAllAction )
                self.menu.addSeparator()
                self.menu.addAction( self.addDirAction )
                
                
            if item.type() == QTreeWidgetItem.UserType+101: # folder reserved
                self.menu.addAction( self.expandSubtreeAction )
                self.menu.addSeparator()
                self.menu.addAction( self.addDirAction )
                self.menu.addSeparator()
                self.menu.addAction( self.openPropertiesAction )
                
            self.menu.popup(self.mapToGlobal(pos))
            self.onMorePopupMenu( item.type() )
    
    def onMorePopupMenu(self, itemType):
        """
        Called after on popup menu
        You should override this method

        @param itemType: 
        @type itemType: 
        """
        pass

    def __createConnections (self):
        """
        Create connections
        """
        self.wrepository.itemDoubleClicked.connect(self.__openRemoteFile)
        self.wrepository.customContextMenuRequested.connect(self.onPopupMenu)
        self.wrepository.currentItemChanged.connect(self.onCurrentItemChanged)
        self.wrepository.itemExpanded.connect(self.itemEventExpandedCollapsed)
        self.wrepository.itemCollapsed.connect(self.itemEventExpandedCollapsed)

        self.projectCombobox.currentIndexChanged.connect(self.onProjectChanged)
        self.projectCombobox.highlighted.connect(self.onProjectHighlighted)

        self.saveAs.RefreshRepository.connect(self.onSaveAsProjectChanged)

    def onSaveAsProjectChanged(self, projectName):
        """
        Called when the project changed on the save as windows
        """
        self.refresh(project=self.getProjectId(project=projectName), saveAsOnly=True )

    def createWidgets (self):
        """
        Create widgets
        """
        self.dockToolbarRemote = QToolBar(self)
        self.dockToolbarRemote.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border

        self.eventFilter = EventFilterComboBox()
        
        self.projectLabel = QLabel(self.tr("Project: "))
        self.projectCombobox = QComboBox(self)
        self.projectCombobox.setEnabled(True)
        self.projectCombobox.installEventFilter(self.eventFilter)

        self.wrepository = TreeWidgetRepository(parent=self, repoType=self.repoType)
        self.wrepository.setFrameShape(QFrame.NoFrame)
        if USE_PYQT5:
            self.wrepository.header().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.wrepository.header().setResizeMode(QHeaderView.Stretch)
        self.wrepository.setHeaderHidden(True)
        self.wrepository.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wrepository.setIndentation(10)
        self.wrepository.hide()
        self.wrepository.setMinimumHeight(150)


        self.saveAs = SaveOpenToRepoDialog(self)
        
        self.labelNotConnected = QLabel(self.tr("   Not connected"))
        font = QFont()
        font.setItalic(True)
        self.labelNotConnected.setFont(font)
        self.labelNotConnected.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.labelNotConnected)
        if self.projectSupport:
            layout.addWidget(self.projectCombobox )
        layout.addWidget(self.wrepository)
        layout.addWidget(self.dockToolbarRemote)

        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    
    def setNotConnected(self):
        """
        Called on disconnection
        """
        self.defaultActions()
        self.labelNotConnected.show()
        self.projectCombobox.hide()
        self.wrepository.hide()
        self.projects = []
        self.projectInitialized = False

    def setConnected(self):
        """
        Called on connection
        """ 
        self.labelNotConnected.hide()
        if self.projectSupport:
            self.projectCombobox.show()
        self.wrepository.show()

    def getCurrentProject(self):
        """
        Returns the current project
        """
        return self.projectCombobox.currentText()

    def getProjectId(self, project):
        """
        Returns the project id according to the project passed as argument
        """
        pid = 0
        for p in self.projects:
            if p['name'] == project:
                pid = p['project_id']
                break
        if pid == 0:
            self.error( 'project not found: %s' % project )
            
            # added in v18
            # Force to return the default project common (1)
            pid = 1
            # end of add
            
        return pid

    def getProjectName(self, project):
        """
        Returns project name according to the project passed as argument
        """
        pname = ""
        for p in self.projects:
            if p['project_id'] == project:
                pname = p['name']
                break
        return pname

    def onProjectHighlighted(self):
        """
        Called on project highlighted
        """
        if self.projectInitialized:
            self.projectClicked = True

    def onProjectChanged(self, comboIndex):
        """
        Called on project changed
        """
        projectName = self.projectCombobox.itemText(comboIndex)

        if self.projectClicked and self.projectInitialized:
            self.refresh(project=self.getProjectId(project=str(projectName)) )
            self.projectClicked = False
    
    def initializeProjects(self,  projects=[], defaultProject=1):
        """
        Create the root item and load all subs items

        @param listing: 
        @type listing: list
        """
        # [{u'project_id': 1, u'name': u'Common'}]
        self.projects = projects
        self.projectCombobox.clear()
        
        # insert data
        pname = ''
        
        # sort project list by  name 
        projects = sorted(projects, key=lambda k: k['name'])
        i = 0
        for p in projects:
            if p["name"].lower() == "common":
                break
            i += 1

        common = projects.pop(i)    
        projects.insert(0, common)

        self.projects = projects
        
        for p in projects:
            self.projectCombobox.addItem ( p['name']  )
            if defaultProject == p['project_id']:
                pname = p['name']
        self.projectCombobox.insertSeparator(1)
        
        for i in xrange(self.projectCombobox.count()):
            item_text = self.projectCombobox.itemText(i)
            if str(pname) == str(item_text):
                self.projectCombobox.setCurrentIndex(i)
        
        self.saveAs.initProjects(projects=projects, defaultProject=defaultProject)

        self.projectInitialized = True
        return True

    def setDefaultProject(self, projectName):
        """
        Set the default project
        """
        for i in xrange(self.projectCombobox.count()):
            item_text = self.projectCombobox.itemText(i)
            if projectName == str(item_text):
                self.projectCombobox.setCurrentIndex(i)

    def initialize(self, listing):
        """
        Create the root item and load all subs items

        @param listing: 
        @type listing: list
        """
        self.initializeCalled = True
        self.refreshRemoteAction.setEnabled(True)
        self.wrepository.clear()

        self.testcasesRoot = Item(repo = self, 
                                  parent = self.wrepository, 
                                  txt = "Root",  
                                  type = QTreeWidgetItem.UserType+10, 
                                  isRoot = True )
        self.testcasesRoot.setSelected(True)
        self.createRepository(listing=listing, parent=self.testcasesRoot, firstCalled=True)
        self.wrepository.sortItems(0, Qt.AscendingOrder)
        self.expandAuto()

        self.initializeSaveAs(listing=listing)

        self.initializeCalled = False
    
    def initializeSaveAs(self, listing, reloadItems=False):
        """
        Create the root item for the save as
        """
        self.saveAs.wrepository.clear()
        self.testcasesRoot2 = Item(repo = self, 
                                   parent = self.saveAs.wrepository, 
                                   txt = "Root",  
                                   type = QTreeWidgetItem.UserType+10, 
                                   isRoot = True )
        self.testcasesRoot2.setSelected(True)
        self.createRepository(listing=listing, 
                              parent=self.testcasesRoot2,
                              fileincluded=True, 
                              firstCalled=True)
        self.saveAs.wrepository.sortItems(0, Qt.AscendingOrder)

        if reloadItems:
            self.saveAs.reloadItems()

    def createRepository(self, listing, parent, fileincluded=True, firstCalled=False):
        """
        Create repository

        @param listing: 
        @type listing: list

        @param parent: 
        @type parent:

        @param fileincluded: 
        @type fileincluded: boolean
        """
        try:
            for dct in  listing:
                if dct["type"] == "folder":
                    folderIcon = None
                    virtualTxt = None
                    reserved = False
                    if firstCalled and dct["name"] == "@Recycle":
                        folderIcon = self.trashIcon
                        reserved = True
                        virtualTxt = " %s" % dct["name"][1:]
                    if firstCalled and dct["name"] == "@Sandbox":
                        folderIcon = self.sandboxIcon   
                        reserved = True     
                        virtualTxt = " %s" % dct["name"][1:]

                    # {'nb-folders': '0', 'name': 'SSL', 'nb-files': '3', 'content': [{'modification':
                    # 1342259500, 'type': 'file', 'name': '__init__.py', 'size': '378'}, {'modificati
                    # on': 1342259500, 'type': 'file', 'name': 'templates.py', 'size': '1795'}, {'modi
                    # fication': 1342259500, 'type': 'file', 'name': 'client.py', 'size': '7096'}], 'm
                    # odification': 1342465145, 'type': 'folder', 'size': '32549'}
                    if reserved:
                        item = Item(repo = self, 
                                    type = QTreeWidgetItem.UserType+101, 
                                    parent = parent, 
                                    txt = dct["name"], 
                                    propertiesFile=dct, 
                                    isFolder=True, 
                                    icon=folderIcon, 
                                    virtualTxt=virtualTxt, 
                                    reserved=reserved )
                    else:
                        item = Item(repo = self, 
                                    parent = parent, 
                                    txt = dct["name"], 
                                    propertiesFile=dct, 
                                    isFolder=True, 
                                    icon=folderIcon, 
                                    virtualTxt=virtualTxt, 
                                    reserved=reserved )

                    self.createRepository(  dct["content"] , item, fileincluded )
                else:
                    if fileincluded:
                        if dct["type"] == "file":
                            pname = self.getProjectName(dct["project"])
                            # {'modification': 1342259500, 'type': 'file', 'name': '__init__.py', 'size': '562 }
                            item = Item(repo = self, 
                                        parent = parent, 
                                        txt = dct["name"] , 
                                        propertiesFile=dct,
                                        type = QTreeWidgetItem.UserType+0, 
                                        projectId=dct["project"], 
                                        projectName=pname )
                            
                            # adding snapshots
                            if 'snapshots' in dct:
                                if len(dct['snapshots']):
                                    for snap in dct['snapshots']:
                                        # extract snap name 
                                        itemSnap = Item(repo = self, 
                                                        parent = item, 
                                                        txt = snap['name'] , 
                                                        propertiesFile=dct,
                                                        type = QTreeWidgetItem.UserType+100, 
                                                        projectId=dct["project"], 
                                                        projectName=pname, 
                                                        snapRealname=snap['realname'], 
                                                        snapMode=True )

        except Exception as e:
            self.error( "unable to create tree: %s" % e )

    def __runItem(self):
        """
        Run item
        Private function
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
            pathFile = self.itemCurrent.getPath(withFileName = False)
            projectId = 0
            if self.projectSupport:
                project = self.getCurrentProject()
                projectId = self.getProjectId(project=str(project))

            testId = TestResults.instance().getTestId()
            
            _json = DocumentViewer.instance().prepareTest( wdocument=None, 
                                                           tabId=testId, 
                                                           background = False, 
                                                           runAt = (0,0,0,0,0,0), 
                                                           runType=UCI.SCHED_NOW, 
                                                           runNb=-1, 
                                                           withoutProbes=False, 
                                                           debugActivated=False, 
                                                           withoutNotif=False, 
                                                           keepTr=True, 
                                                           prjId=projectId, 
                                                           testFileExtension=self.itemCurrent.fileExtension, 
                                                           testFilePath=pathFile, 
                                                           testFileName=self.itemCurrent.fileName, 
                                                           fromTime=(0,0,0,0,0,0), 
                                                           toTime=(0,0,0,0,0,0), 
                                                           prjName='', 
                                                           stepByStep=False, 
                                                           breakpoint=False,
                                                           channelId=False, 
                                                           basicMode=False  )
                                                           
            if self.itemCurrent.fileExtension in [ RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT, RCI.EXT_TESTUNIT]:
                RCI.instance().scheduleTest(req=_json, wdocument=None)
                
            elif self.itemCurrent.fileExtension in [ RCI.EXT_TESTPLAN, RCI.EXT_TESTGLOBAL]:
                RCI.instance().scheduleTestTpg(req=_json, wdocument=None)
                
            else:
                pass
            
    def __saveasItem(self):
        """
        Save item as 
        Private function
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
            pass
        
    def __delAllSnapshots(self):
        """
        Delete all snapshots
        """
        if self.itemCurrent is None:
            return
            
        reply = QMessageBox.question(self, self.tr("Delete all snapshots"), self.tr("Are you sure?"),
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes: 
            RCI.instance().removeAllSnapshotTests(projectId=int(self.itemCurrent.projectId), 
                                                  testPath=self.itemCurrent.getPath(), 
                                                  testName=self.itemCurrent.fileName, 
                                                  testExtension=self.itemCurrent.fileExtension)
            
    def __deleteSnapshot(self):
        """
        Delete snapshot
        """
        if self.itemCurrent is None:
            return
            
        reply = QMessageBox.question(self, self.tr("Delete snapshot"), self.tr("Are you sure?"),
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes: 
            RCI.instance().removeSnapshotTests(projectId=int(self.itemCurrent.projectId), 
                                               snapshotPath=self.itemCurrent.getPath(withFileName=False), 
                                               snapshotName=self.itemCurrent.snapRealname)
            
    def __restoreSnapshot(self):
        """
        Restore snapshot
        """
        if self.itemCurrent is None:
            return
        reply = QMessageBox.question(self, self.tr("Restore snapshot"), self.tr("Are you sure?"),
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes: 
            RCI.instance().restoreSnapshotTests(projectId=int(self.itemCurrent.projectId), 
                                                snapshotPath=self.itemCurrent.getPath(withFileName=False), 
                                                snapshotName=self.itemCurrent.snapRealname)
            
    def __addSnapshot(self):
        """
        Add snapshot
        """
        if self.itemCurrent is None:
            return
            
        txt, ok = QInputDialog.getText(self, "Create snapshot", "Enter snapshot name:",
                                       QLineEdit.Normal, self.itemCurrent.fileName)
        if ok and txt:
            try:
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    txt.encode("ascii") 

                RCI.instance().addSnapshotTests(projectId=int(self.itemCurrent.projectId), 
                                                testPath=self.itemCurrent.getPath(), 
                                                snapshotName=txt, 
                                                snapshotTimestamp="%s" % time.time())
            except UnicodeEncodeError as e:
                self.error(e)
                QMessageBox.warning(self, "Create snapshot" , 
                                    "Bad snapshot name!\nPerhaps one day, but not today, sorry for this limitation.")
 
    def __openProperties(self):
        """
        Open properties
        Private function
        """
        if self.itemCurrent is None:
            return
        propertiesDialog = PropertiesDialog(parent=self, 
                                            item=self.itemCurrent, 
                                            repoType=self.repoType)
        if propertiesDialog.exec_() == QDialog.Accepted:
            pass

    def __openItem(self):
        """
        Open item
        Private function
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
            pathFile = self.itemCurrent.getPath(withFileName = True)
            if self.projectSupport:
                project = self.getCurrentProject()
                self.openRemoteFile(pathFile=pathFile, project=self.getProjectId(project=str(project)))
            else:
                self.openRemoteFile(pathFile=pathFile)

    def __moveItem(self):
        """
        Move item
        Private function
        """
        project= self.getCurrentProject()
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
            currentName = self.itemCurrent.fileName
            pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=False)
            if self.repoType == UCI.REPO_TESTS:
                self.parent.remote().saveAs.setMoveFile(project=project, update_path=True)
                dialog = self.parent.remote().saveAs
            elif self.repoType == UCI.REPO_ADAPTERS:
                self.parent.remoteAdapter().saveAs.setMoveFile()
                dialog = self.parent.remoteAdapter().saveAs
            elif self.repoType == UCI.REPO_LIBRARIES:
                self.parent.remoteLibrary().saveAs.setMoveFile()
                dialog = self.parent.remoteLibrary().saveAs
            else:
                self.error( 'move item file: should not be happened')
            
            if dialog.exec_() == QDialog.Accepted:
                newPath = dialog.getSelection()
                newProject = dialog.getProjectSelection()
                
                update_location = dialog.getUpdateLocationStatus()
                
                if self.projectSupport:
                    project = self.getCurrentProject()
                    projectid = self.getProjectId(project=str(project))
                    if len(str(newProject)):
                        newprojectid = self.getProjectId(project=str(newProject))
                    else:
                        newprojectid = projectid
                    self.moveRemoteFile(    currentName=currentName, 
                                            currentPath=pathFolder, 
                                            currentExtension=self.itemCurrent.fileExtension,
                                            newPath=newPath, 
                                            project=projectid, 
                                            newProject=newprojectid,
                                            update_location = update_location
                                        )
                else:
                    self.moveRemoteFile(currentName=currentName, 
                                        currentPath=pathFolder, 
                                        currentExtension=self.itemCurrent.fileExtension, 
                                        newPath=newPath)
        elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1: # folder
            currentName = self.itemCurrent.folderName
            pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=False)
            if self.repoType == UCI.REPO_TESTS:
                self.parent.remote().saveAs.setMoveFolder(project=project)
                dialog = self.parent.remote().saveAs
            elif self.repoType == UCI.REPO_ADAPTERS:
                self.parent.remoteAdapter().saveAs.setMoveFolder()
                dialog = self.parent.remoteAdapter().saveAs
            elif self.repoType == UCI.REPO_LIBRARIES:
                self.parent.remoteLibrary().saveAs.setMoveFolder()
                dialog = self.parent.remoteLibrary().saveAs
            else:
                self.error( 'move item folder: should not be happened')
            
            if dialog.exec_() == QDialog.Accepted:
                newPath = dialog.getSelection()
                newProject = dialog.getProjectSelection()
                if self.projectSupport:
                    project = self.getCurrentProject()
                    projectid = self.getProjectId(project=str(project))
                    if len(str(newProject)):
                        newprojectid = self.getProjectId(project=str(newProject))
                    else:
                        newprojectid = projectid
                    self.moveRemoteFolder(  currentName=currentName, 
                                            currentPath=pathFolder,
                                            newPath=newPath,
                                            project=projectid, 
                                            newProject=newprojectid )
                else:
                    self.moveRemoteFolder(currentName=currentName, 
                                          currentPath=pathFolder, 
                                          newPath=newPath)

    def moveRemoteFile(self, currentName, currentPath, currentExtension, newPath, 
                       project=0, newProject=0, update_location=False):
        """
        Move remote file

        @param currentName: 
        @type currentName:  

        @param currentPath: 
        @type currentPath:  

        @param currentExtension: 
        @type currentExtension: 

        @param newPath: 
        @type newPath:  
        """
        raise NotReimplemented("moveRemoteFile")

    def moveRemoteFolder(self, currentName, currentPath, newPath, project=0, newProject=0):
        """
        Move remote folder

        @param currentName: 
        @type currentName:  

        @param currentPath: 
        @type currentPath:  

        @param currentExtension: 
        @type currentExtension: 

        @param newPath: 
        @type newPath:  
        """
        raise NotReimplemented("moveRemoteFolder")

    def __openRemoteFile(self, witem, col):
        """
        Open remote file
        Private function

        @param witem: 
        @type witem:

        @param col: 
        @type col:
        """
        if witem.type() == QTreeWidgetItem.UserType+0 :
            pathFile = witem.getPath(withFileName = True)
            if self.projectSupport:
                project = self.getCurrentProject()
                projectid = self.getProjectId(project=str(project))
                self.openRemoteFile(pathFile=pathFile, project=projectid)
            else:
                self.openRemoteFile(pathFile=pathFile)

    def openRemoteFile(self, pathFile, project=0):
        """
        Open remote file
        You should override this method

        @param pathFile: 
        @type pathFile: 
        """
        raise NotReimplemented("openRemoteFile")

    def __deleteAllItem (self):
        """
        Delete all item
        Private function
        Recursive Delete
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+1:
            reply = QMessageBox.question(self, self.tr("Delete all directories and files"), self.tr("Are you sure ?"),
                        QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=True)
                if self.projectSupport:
                    project = self.getCurrentProject()
                    projectid = self.getProjectId(project=str(project))
                    self.deleteAllFolders(pathFolder=pathFolder, project=projectid)
                else:
                    self.deleteAllFolders(pathFolder=pathFolder)
        else:
            self.error( "should not be happened" )

    def deleteAllItem (self, pathFolder, project=0):
        """
        Delete all item
        You should override this method

        @param pathFolder: 
        @type pathFolder:
        """
        raise NotReimplemented("deleteAllItem")

    def __deleteItem (self):
        """
        Delete item
        Private function
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0:
            reply = QMessageBox.question(self, self.tr("Delete file"), self.tr("Are you sure ?"),
                        QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                pathFile = self.itemCurrent.getPath(withFileName= True, withFolderName=False)
                if self.projectSupport:
                    project = self.getCurrentProject()
                    projectid = self.getProjectId(project=str(project))
                    self.deleteFile(pathFile=pathFile, project=projectid)
                else:
                    self.deleteFile(pathFile=pathFile)
                    
        elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1:
            reply = QMessageBox.question(self, self.tr("Delete folder"), self.tr("Are you sure ?"),
                    QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=True)
                if self.projectSupport:
                    project = self.getCurrentProject()
                    projectid = self.getProjectId(project=str(project))
                    self.deleteFolder(pathFolder=pathFolder, project=projectid)
                else:
                    self.deleteFolder(pathFolder=pathFolder)
        else:
            self.error( "should not be happened" )

    def deleteFile (self, pathFile, project=0):
        """
        Delete file
        You should override this method

        @param pathFile: 
        @type pathFile:
        """
        raise NotReimplemented("deleteFile")

    def deleteFolder (self, pathFolder, project=0):
        """
        Delete Folder
        You should override this method

        @param pathFolder: 
        @type pathFolder:
        """
        raise NotReimplemented("deleteFolder")

    def __createItem (self):
        """
        Create item
        Private function
        """
        txt, ok = QInputDialog.getText(self, self.tr("Create"), self.tr("Enter name:"), QLineEdit.Normal)
        if ok and txt:
            try:
                txt = str(txt)
                
                # remove uneeded space in v16
                txt = txt.strip()
                
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    txt.encode("ascii") 
            except UnicodeEncodeError as e:
                QMessageBox.warning(self, self.tr("Add") , self.tr("Invalid name.") )
            else:
                if "'" in txt:
                    QMessageBox.warning(self, self.tr("Add") , self.tr("Invalid name.") )
                else:
                    pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=True)
                    if self.projectSupport:
                        project = self.getCurrentProject()
                        projectid = self.getProjectId(project=str(project))
                        self.addFolder(pathFolder=pathFolder, folderName = txt, project=projectid)
                    else:
                        self.addFolder(pathFolder=pathFolder, folderName = txt)
    
    def addFolder (self, pathFolder, folderName, project=0):
        """
        Add Folder
        You should override this method

        @param pathFolder: 
        @type pathFolder:

        @param folderName: 
        @type folderName:
        """
        raise NotReimplemented("addFolder")

    def __refreshAll (self):
        """
        Refresh all tree
        Private function
        """
        self.defaultActions()
        self.refresh()
        
    def refresh(self, project=0, saveAsOnly=False):
        """
        Refresh tree
        You should override this method
        """
        raise NotReimplemented("refresh")
        
    # dbr13 >>>
    def __update_adapter_library(self):
        """
        Update Adapters/Libraries version for multiple test entities
        """

        project = self.getCurrentProject()
        project_id = self.getProjectId(project)
        path_folder = self.itemCurrent.getPath(withFileName=False, withFolderName=True)
        updateAdpLibDialog = UpdateAdapterLibraryDialog()
        if updateAdpLibDialog.exec_() == QDialog.Accepted:
            adapter_version = updateAdpLibDialog.update_adapter_combobox.currentText()
            library_version = updateAdpLibDialog.update_library_combobox.currentText()
            if adapter_version != 'None' or library_version != 'None':
                RCI.instance().updateAdapterLibraryVForTestEntities(projectId=project_id,
                                                                    pathFolder=path_folder,
                                                                    adapterVersion=adapter_version,
                                                                    libraryVersion=library_version)
    def __find_usage(self):
        """
        Find file usage
        """
        project = self.getCurrentProject()
        project_id = self.getProjectId(project)
        path_file = self.itemCurrent.getPath(withFileName=True, 
                                             withFolderName=False)
        self.find_usage(project_id=project_id, 
                        file_path=path_file)

    def find_usage(self, project_id, file_path):
        """

        @param project_id:
        @type project_id

        @param file_path:
        @type file_path
        """
        raise NotReimplemented("find_usage")

    def initFindTestFileUsageWTree(self, result_list, file_path, file_projectid):
        """
        Init Find Usage Treewidget
        :param response:
        :return:
        """
        usage_tree = FindTestFileUsageWTree(result_list=result_list, 
                                            file_path=file_path, 
                                            file_projectid=file_projectid)
        return usage_tree                                                         
    # dbr13 <<<


    def __renameItem(self):
        """
        Rename item
        Private function
        """
        currentName = ''
        folder=False
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0:
            currentName = self.itemCurrent.fileName
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+1:
            currentName = self.itemCurrent.folderName
            folder=True

        if self.repoType in [ UCI.REPO_ADAPTERS, UCI.REPO_LIBRARIES ]:
            show_update_location = False
        else:
            show_update_location = True
            
        renameDialog = RenameDialog( currentName = str(currentName), 
                                     folder=folder,
                                     show_update_location = show_update_location)
        if renameDialog.exec_() == QDialog.Accepted:
            # dbr13 >>> for rename
            update_location = renameDialog.getUpdateLocationStatus()
            # dbr13 <<<
            
            txt = renameDialog.getNewName()
            try:
                txt = str(txt)
                
                # remove uneeded space in v16
                txt = txt.strip()
                
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    txt.encode("ascii") 
            except UnicodeEncodeError as e:
                QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name.") )
            else:
                if "'" in txt or txt.startswith("."):
                    QMessageBox.warning(self, self.tr("Rename") , self.tr("Invalid name.") )
                else:
                
                    if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: #rename file
                        pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=False)
                        if self.projectSupport:
                            project = self.getCurrentProject()
                            projectid = self.getProjectId(project=str(project))
                            self.renameFile(mainPath=pathFolder, 
                                            oldFileName=self.itemCurrent.fileName, 
                                            newFileName=txt, 
                                            extFile=self.itemCurrent.fileExtension, 
                                            project=projectid, 
                                            update_location=update_location)
                        else:
                            self.renameFile(mainPath=pathFolder, 
                                            oldFileName=self.itemCurrent.fileName, 
                                            newFileName=txt, 
                                            extFile=self.itemCurrent.fileExtension)
                                            
                    elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1: # rename folder
                        pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=False)
                        if self.projectSupport:
                            project = self.getCurrentProject()
                            projectid = self.getProjectId(project=str(project))
                            self.renameFolder(mainPath=pathFolder, 
                                              oldFolderName=self.itemCurrent.folderName, 
                                              newFolderName= txt, 
                                              project=projectid)
                        else:
                            self.renameFolder(mainPath=pathFolder, 
                                              oldFolderName=self.itemCurrent.folderName, 
                                              newFolderName= txt)
                    else:
                        self.error( "should not be happened" )

    def renameFile (self, mainPath, oldFileName, newFileName, extFile, 
                     project=0, update_location=False):
        """
        Rename file
        You should override this method

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
        raise NotReimplemented("renameFile")

    def renameFolder (self, mainPath, oldFolderName, newFolderName, project=0):
        """
        Rename folder
        You should override this method

        @param mainPath: 
        @type mainPath:

        @param oldFolderName: 
        @type oldFolderName:

        @param newFolderName: 
        @type newFolderName:
        """
        raise NotReimplemented("renameFolder")

    def __duplicateItem(self):
        """
        Duplicate item
        Private function
        """
        currentName = ''
        folder=False
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0:
            currentName = self.itemCurrent.fileName
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+1:
            currentName = self.itemCurrent.folderName
            folder=True

        pathFolder = self.itemCurrent.getPath(withFileName = False, 
                                              withFolderName=False)
        
        if self.projectSupport:
            project = self.getCurrentProject()
            projectid = self.getProjectId(project=str(project))
        else:
            projectid = 0
            
        duplicateDialog = DuplicateDialog( currentName = str(currentName), 
                                           folder=folder, 
                                           repoType=self.repoType,
                                           projects=self.projects, 
                                           defaultProject=projectid, 
                                           currentPath=pathFolder )
        if duplicateDialog.exec_() == QDialog.Accepted:
            txt = duplicateDialog.getDuplicateName()
            newProjectName = duplicateDialog.getProjectSelected()
            newPath = duplicateDialog.getNewPath()
            try:
                txt = str(txt)
                
                # remove uneeded space in v16
                txt = txt.strip()
                
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    txt.encode("ascii") 
            except UnicodeEncodeError as e:
                QMessageBox.warning(self, self.tr("Duplicate") , self.tr("Invalid name.") )
            else:
                if "'" in txt:
                    QMessageBox.warning(self, self.tr("Duplicate") , self.tr("Invalid name.") )
                else:
                    try:
                        newPath = str(newPath)
                        
                        # workaround to detect special characters, same limitation as with python2 because of the server
                        # this limitation will be removed when the server side will be ported to python3
                        if sys.version_info > (3,): # python3 support only 
                            newPath.encode("ascii") 
                    except UnicodeEncodeError as e:
                        QMessageBox.warning(self, self.tr("Duplicate") , self.tr("Invalid path.") )
                    else:
                        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # duplicate file
                            pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=False)
                            if self.projectSupport:
                                project = self.getCurrentProject()
                                projectid = self.getProjectId(project=str(project))
                                if len(str(newProjectName)):
                                    newprojectid = self.getProjectId(project=str(newProjectName))
                                else:
                                    newprojectid = projectid
                                self.duplicateFile(mainPath=pathFolder, 
                                                   oldFileName=self.itemCurrent.fileName, 
                                                   newFileName= txt, 
                                                   extFile=self.itemCurrent.fileExtension, 
                                                   project=projectid, newProject=newprojectid, 
                                                   newPath=newPath)
                            else:
                                self.duplicateFile(mainPath=pathFolder, 
                                                   oldFileName=self.itemCurrent.fileName, 
                                                   newFileName= txt, 
                                                   extFile=self.itemCurrent.fileExtension, 
                                                   newPath=newPath)
                        elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1: # not yet impletemented
                            pathFolder = self.itemCurrent.getPath(withFileName = False, withFolderName=False)
                            if self.projectSupport:
                                project = self.getCurrentProject()
                                projectid = self.getProjectId(project=str(project))
                                if len(str(newProjectName)):
                                    newprojectid = self.getProjectId(project=str(newProjectName))
                                else:
                                    newprojectid = projectid
                                self.duplicateFolder(mainPath=pathFolder, 
                                                     oldFolderName=self.itemCurrent.folderName, 
                                                     newFolderName= txt,
                                                     project=projectid, 
                                                     newProject=newprojectid, 
                                                     newPath=newPath)
                            else:
                                self.duplicateFolder(mainPath=pathFolder, 
                                                     oldFolderName=self.itemCurrent.folderName, 
                                                     newFolderName= txt,
                                                     newPath=newPath)
                        else:
                            self.error( "should not be happened" )

    def duplicateFile (self, mainPath, oldFileName, newFileName, 
                        extFile, project=0, newProject=0, newPath=''):
        """
        Duplicate file
        You should override this method

        @param mainPath: 
        @type mainPath:

        @param oldFileName: 
        @type oldFileName:

        @param newFileName: 
        @type newFileName:

        @param extFile: 
        @type extFile:
        """
        raise NotReimplemented("duplicateFile")

    def duplicateFolder (self, mainPath, oldFolderName, newFolderName, 
                            project=0, newProject=0, newPath=''):
        """
        Duplicate folder
        You should override this method

        @param mainPath: 
        @type mainPath:

        @param oldFolderName: 
        @type oldFolderName:

        @param newFolderName: 
        @type newFolderName:
        """
        raise NotReimplemented("duplicateFolder")

    def onCurrentItemChanged (self, witem1, witem2):
        """
        Called on current item changed

        @param witem1: 
        @type witem1:

        @param witem2: 
        @type witem2:
        """
        if witem1 is not None:
            self.itemCurrent = witem1
            self.wrepository.itemCurrent = witem1
            
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
                self.addDirAction.setEnabled(False)
                self.delDirAction.setEnabled(False)
                self.delAllDirAction.setEnabled(False)
                self.renameAction.setEnabled(True)
                self.duplicateDirAction.setEnabled(False)
                self.duplicateFileAction.setEnabled(True)
                self.deleteFileAction.setEnabled(True)
                self.moveFileAction.setEnabled(True)
                self.moveFolderAction.setEnabled(False)
                self.openFileAction.setEnabled(True)
                self.openPropertiesAction.setEnabled(True)
                
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                if self.itemCurrent.fileExtension.lower() in [ EXTENSION_TUX, EXTENSION_TAX, 
                                                               EXTENSION_TPX, EXTENSION_TSX, 
                                                               EXTENSION_TGX ]:
                    self.runAction.setEnabled(True)
                else:
                    self.runAction.setEnabled(False)
                    
                if self.itemCurrent.fileExtension.lower() in [ EXTENSION_TUX, EXTENSION_TAX, 
                                                               EXTENSION_TPX, EXTENSION_TSX,
                                                               EXTENSION_TGX, EXTENSION_TDX, 
                                                               EXTENSION_TCX ]:
                    self.snapshotAction.setEnabled(True)
                else:
                    self.snapshotAction.setEnabled(False)
                    
                # dbr13 >>>
                self.updateAdapterLibraryAction.setEnabled(False)
                
                if self.itemCurrent.fileExtension.lower() in [ EXTENSION_TUX, EXTENSION_TAX, 
                                                               EXTENSION_TPX, EXTENSION_TSX]:
                    self.findUsageAction.setEnabled(True)
                else:
                    self.findUsageAction.setEnabled(False)
                    
                # dbr13 <<<
                
            elif self.itemCurrent.type() == QTreeWidgetItem.UserType+100: # file snapshot
                self.addDirAction.setEnabled(False)
                self.delDirAction.setEnabled(False)
                self.delAllDirAction.setEnabled(False)
                self.renameAction.setEnabled(False)
                self.duplicateDirAction.setEnabled(False)
                self.duplicateFileAction.setEnabled(False)
                self.deleteFileAction.setEnabled(False)
                self.moveFileAction.setEnabled(False)
                self.moveFolderAction.setEnabled(False)
                self.openFileAction.setEnabled(False)
                self.openPropertiesAction.setEnabled(False)
                self.snapshotAction.setEnabled(False)
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.runAction.setEnabled(False)
                
                # dbr13 >>>
                self.updateAdapterLibraryAction.setEnabled(False)
                # dbr13 <<<
                
            elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1: # folder
                self.addDirAction.setEnabled(True)
                self.delDirAction.setEnabled(True)
                if UCI.RIGHTS_ADMIN in RCI.instance().userRights :
                    self.delAllDirAction.setEnabled(True)
                else:
                    self.delAllDirAction.setEnabled(False)
                self.renameAction.setEnabled(True)
                self.duplicateDirAction.setEnabled(True)
                self.duplicateFileAction.setEnabled(False)
                self.deleteFileAction.setEnabled(False)
                self.moveFileAction.setEnabled(False)
                self.moveFolderAction.setEnabled(True)
                self.openFileAction.setEnabled(False)
                self.openPropertiesAction.setEnabled(True)
                self.snapshotAction.setEnabled(False)
                self.expandSubtreeAction.setEnabled(True)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.runAction.setEnabled(False)
                
                # dbr13 >>>
                self.updateAdapterLibraryAction.setEnabled(True)
                # dbr13 <<<
                
            elif self.itemCurrent.type() == QTreeWidgetItem.UserType+10 : #root
                self.addDirAction.setEnabled(True)
                self.delDirAction.setEnabled(False)
                self.delAllDirAction.setEnabled(False)
                self.renameAction.setEnabled(False)
                self.duplicateDirAction.setEnabled(False)
                self.duplicateFileAction.setEnabled(False)
                self.deleteFileAction.setEnabled(False)
                self.moveFileAction.setEnabled(False)
                self.moveFolderAction.setEnabled(False)
                self.openFileAction.setEnabled(False)
                self.openPropertiesAction.setEnabled(False)
                self.snapshotAction.setEnabled(False)
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(True)
                self.collapseAllAction.setEnabled(True)
                self.runAction.setEnabled(False)
                
                # dbr13 >>>
                self.updateAdapterLibraryAction.setEnabled(False)
                # dbr13 <<<
                
            elif self.itemCurrent.type() == QTreeWidgetItem.UserType+101: # reserved (trash, sandbox)
                self.addDirAction.setEnabled(True)
                self.delDirAction.setEnabled(False)
                self.delAllDirAction.setEnabled(False)
                self.renameAction.setEnabled(False)
                self.duplicateDirAction.setEnabled(False)
                self.duplicateFileAction.setEnabled(False)
                self.deleteFileAction.setEnabled(False)
                self.moveFileAction.setEnabled(False)
                self.moveFolderAction.setEnabled(False)
                self.openFileAction.setEnabled(False)
                self.openPropertiesAction.setEnabled(True)
                self.snapshotAction.setEnabled(False)
                self.expandSubtreeAction.setEnabled(True)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.runAction.setEnabled(False)
                
                # dbr13 >>>
                self.updateAdapterLibraryAction.setEnabled(False)
                # dbr13 <<<
            else:
                self.addDirAction.setEnabled(False)
                self.delDirAction.setEnabled(False)
                self.delAllDirAction.setEnabled(False)
                self.renameAction.setEnabled(False)
                self.duplicateDirAction.setEnabled(False)
                self.duplicateFileAction.setEnabled(False)
                self.deleteFileAction.setEnabled(False)
                self.moveFileAction.setEnabled(False)
                self.moveFolderAction.setEnabled(False)
                self.openFileAction.setEnabled(False)
                self.openPropertiesAction.setEnabled(False)
                self.snapshotAction.setEnabled(False)
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
                self.runAction.setEnabled(False)

                # dbr13 >>>
                self.updateAdapterLibraryAction.setEnabled(False)
                # dbr13 <<<
                
            self.onMoreCurrentItemChanged( self.itemCurrent.type() )

    def onMoreCurrentItemChanged (self, itemType):
        """
        Called after the function on current item changed
        You should override this method

        @param itemType: 
        @type itemType: 
        """
        pass