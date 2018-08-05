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
Local repository module
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
    from PyQt4.QtGui import (QDialog, QLabel, QFont, QPushButton, QVBoxLayout, QAbstractItemView, 
                            QHBoxLayout, QLineEdit, QTreeWidgetItem, QMessageBox, QTreeWidget, QDrag, 
                            QWidget, QIcon, QStyle, QMenu, QToolBar, QFrame, QHeaderView, QInputDialog,
                            QKeySequence)
    from PyQt4.QtCore import (QMimeData, Qt, pyqtSignal, QSize)
except ImportError:
    from PyQt5.QtGui import (QFont, QDrag, QIcon, QKeySequence)
    from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QAbstractItemView, 
                                QHBoxLayout, QLineEdit, QTreeWidgetItem, QMessageBox, QTreeWidget, 
                                QWidget, QStyle, QMenu, QToolBar, QFrame, QHeaderView, QInputDialog)
    from PyQt5.QtCore import (QMimeData, Qt, pyqtSignal, QSize)
    USE_PYQT5 = True
    
from Libs import QtHelper, Logger
import Settings
import UserClientInterface as UCI
import RestClientInterface as RCI

import Workspace.TestPlan as TestPlan
import Workspace.TestConfig as TestConfig
import Workspace.TestSuite as TestSuite
import Workspace.TestData as TestData
import Workspace.TestAdapter as TestAdapter
import Workspace.TestTxt as TestTxt
import Workspace.TestUnit as TestUnit
import Workspace.TestPng as TestPng
import Workspace.TestAbstract as TestAbstract

import os
try:
    import pickle
except ImportError: # support python3
    import cPickle as pickle
    
EXTENSION_TPX = TestPlan.TYPE
EXTENSION_TGX = TestPlan.TYPE_GLOBAL
EXTENSION_TCX = TestConfig.TYPE
EXTENSION_TSX = TestSuite.TYPE
EXTENSION_TDX = TestData.TYPE
EXTENSION_TUX = TestUnit.TYPE
EXTENSION_TAX = TestAbstract.TYPE

EXTENSION_TXT = TestTxt.TYPE
EXTENSION_PY  = TestAdapter.TYPE
EXTENSION_PNG  = TestPng.TYPE

SUPPORTED_EXTENSIONS = [EXTENSION_TSX, EXTENSION_TPX, EXTENSION_TGX, EXTENSION_TCX, 
                        EXTENSION_TDX, EXTENSION_TUX, EXTENSION_PNG, EXTENSION_TAX]

MODE_SAVE = 0
MODE_OPEN = 1

class SaveOpenToRepoDialog(QDialog, Logger.ClassLogger):
    """
    Save/open dialog for repositories
    """
    def __init__(self, parent, filename='', type = MODE_SAVE, typeFile = [ EXTENSION_TSX ], 
                 multipleSelection=False):
        """
        Save/open dialog

        @param parent:
        @type parent:

        @param filename:
        @type filename:

        @param type: MODE_SAVE, MODE_OPEN
        @type type: Integer

        @param typeFile: EXTENSION_TSX, etc ...
        @type typeFile: Integer
        """
        super(SaveOpenToRepoDialog, self).__init__(parent)

        self.typeMode = type # mode save or open 
        self.typeFile = typeFile
        self.widgetRepo = None
        self.filenameLineEdit = None
        self.selectedFilename = None
        self.selectedFilenames = []
        self.multipleSelection = multipleSelection
        
        self.createWidgets(filename)
        self.createConnections()

    def createWidgets(self, filename):
        """
        Create qt widgets

        @param filename:
        @type filename:
        """
        self.setFixedWidth(450)
        self.setFixedHeight(500)

        self.warningLabel = QLabel('')
        font = QFont()
        font.setItalic(True)
        self.warningLabel.setFont(font)

        if self.typeMode == MODE_SAVE:
            self.selectedFilenames = []
            self.setWindowTitle('Save to local repository as ...')
            self.acceptButton = QPushButton("Save")
            self.warningLabel.setText('')
            withFile = False
        elif self.typeMode == MODE_OPEN:
            self.acceptButton = QPushButton("Open")
            self.setWindowTitle('Open from repository')
            withFile = True
            if self.multipleSelection:
                self.warningLabel.setText('Multiple selection files available.')
            else:
                self.warningLabel.setText('')

        else:
            raise Exception( 'local repo mode not supported: %s' % self.typeMode)

        layout = QVBoxLayout()
        self.widgetRepo = Repository( parent= self, withFile = withFile ) 
        self.widgetRepo.active()

        self.repo = self.widgetRepo.wrepository
        layout.addWidget( self.widgetRepo )
        
        if self.typeMode == MODE_OPEN:
            if self.multipleSelection:
                self.repo.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # save mode
        if self.typeMode == MODE_SAVE:
            fileLayout = QHBoxLayout()
            fileLayout.addWidget(QLabel('File name:'))
            self.filenameLineEdit = QLineEdit(filename)
            fileLayout.addWidget( self.filenameLineEdit )
            layout.addLayout(fileLayout)
        
        # Buttons
        self.cancelButton = QPushButton("Cancel")
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.acceptButton)
        buttonLayout.addWidget(self.cancelButton)

        layout.addWidget( self.warningLabel )

        layout.addLayout(buttonLayout)
        
        # set the layout
        self.setLayout(layout)

    def refresh(self):
        """
        Refresh
        """
        self.widgetRepo.deactive()
        self.widgetRepo.active()

    def setOpen(self):
        """
        Set as open mode
        """
        self.filenameLineEdit.setText( "")
        self.setWindowTitle('Open from repository')
        self.acceptButton.setText( "Open" )
        if self.multipleSelection:
            self.warningLabel.setText('Multiple selection files available.')
        else:
            self.warningLabel.setText('')

    def setFilename(self, filename):
        """
        Set current filename
        """
        self.filenameLineEdit.setText( filename)
        self.setWindowTitle('Save to local repository as ...')
        self.acceptButton.setText( "Save" )
        self.warningLabel.setText('')

    def setImportFilename(self, filename):
        """
        Set to import file
        """
        self.warningLabel.setText('')
        self.setWindowTitle('Import to local repository as ...')
        self.acceptButton.setText( "Import" )
        self.filenameLineEdit.setText( filename)

    def iterateTree(self, item, hideTsx, hideTpx, hideTcx, hideTdx, hideTux, hidePng, hideTgx, hideTax):
        """
        Iterate on the tree to hide items or not
        """
        child_count = item.childCount()
        for i in range(child_count):
            subitem = item.child(i)
            subchild_count = subitem.childCount()
            if subchild_count > 0:
                self.iterateTree(item=subitem, hideTsx=hideTsx, hideTpx=hideTpx, hideTcx=hideTcx, hideTdx=hideTdx,
                                    hideTux=hideTux, hidePng=hidePng, hideTgx=hideTgx, hideTax=hideTax)
            else:
                if hideTpx and subitem.getExtension() == EXTENSION_TPX:
                    subitem.setHidden (True)
                elif hideTgx and subitem.getExtension() == EXTENSION_TGX:
                    subitem.setHidden (True)
                elif hideTcx and subitem.getExtension() == EXTENSION_TCX:
                    subitem.setHidden (True)
                elif hideTux and  subitem.getExtension() == EXTENSION_TUX:
                    subitem.setHidden (True)
                elif hideTsx and  subitem.getExtension() == EXTENSION_TSX:
                    subitem.setHidden (True)
                elif hideTdx and  subitem.getExtension() == EXTENSION_TDX:
                    subitem.setHidden (True)
                elif hidePng and  subitem.getExtension() == EXTENSION_PNG:
                    subitem.setHidden (True)
                elif hideTax and  subitem.getExtension() == EXTENSION_TAX:
                    subitem.setHidden (True)
                else:
                    subitem.setHidden(False)

    def hideItems(self, hideTsx=False, hideTpx=False, hideTcx=False, hideTdx=False, 
                    hideTux=False, hidePng=False, hideTgx=False, hideTax=False):
        """
        Hide items
        """
        root = self.repo.invisibleRootItem()
        self.iterateTree(item=root, hideTsx=hideTsx, hideTpx=hideTpx, hideTcx=hideTcx, hideTdx=hideTdx, 
                                hideTux=hideTux, hidePng=hidePng, hideTgx=hideTgx, hideTax=hideTax)

    def hideFiles(self, hideTsx=False, hideTpx=False, hideTcx=False, hideTdx=False, 
                    hideTux=False, hidePng=False, hideTgx=False, hideTax=False):
        """
        Hide files
        """
        self.hideItems(hideTsx=hideTsx, hideTpx=hideTpx, hideTcx=hideTcx, hideTdx=hideTdx, hideTux=hideTux,
                        hidePng=hidePng, hideTgx=hideTgx, hideTax=hideTax)

    def createConnections (self):
        """
        Create qt connections
        """
        self.repo.itemDoubleClicked.connect(self.accept)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def accept(self):
        """
        Called on accept button
        """
        self.selectedFilenames = []
        # save mode
        if self.typeMode == MODE_SAVE:
            filename = unicode(self.filenameLineEdit.text())
            if not filename:
                return

        wItems = self.repo.selectedItems()
        if len(wItems):
            if self.multipleSelection:
                wItemsSelected = wItems
            else:
                wItemsSelected = wItems[0]
        else:
            # select the root item
            wItemsSelected = self.repo.topLevelItem(0)

        if wItemsSelected is None:
            return

        if self.typeMode == MODE_SAVE:
            self.selectedFilename =  "%s/%s" % (    wItemsSelected.getPath( withFolderName = True, withFileName = False ),
                                        self.filenameLineEdit.text(),
                                    )
            QDialog.accept(self)
        elif self.typeMode == MODE_OPEN:
            if self.multipleSelection:
                for itm in wItemsSelected:
                    selectedFilename = itm.getPath( withFolderName = False, withFileName = True )
                    if EXTENSION_TSX in self.typeFile and selectedFilename.endswith(EXTENSION_TSX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_TPX in self.typeFile and selectedFilename.endswith(EXTENSION_TPX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_TGX in self.typeFile and selectedFilename.endswith(EXTENSION_TGX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_TCX in self.typeFile and selectedFilename.endswith(EXTENSION_TCX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_TDX in self.typeFile and selectedFilename.endswith(EXTENSION_TDX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_TUX in self.typeFile and selectedFilename.endswith(EXTENSION_TUX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_TAX in self.typeFile and selectedFilename.endswith(EXTENSION_TAX):
                        self.selectedFilenames.append(selectedFilename)
                    elif EXTENSION_PNG in self.typeFile and selectedFilename.endswith(EXTENSION_PNG):
                        self.selectedFilenames.append(selectedFilename)
                    else:
                        pass

                if len(self.selectedFilenames):
                    QDialog.accept(self)  
            else:
                selectedFilename = wItemsSelected.getPath( withFolderName = False, withFileName = True )
                if EXTENSION_TSX in self.typeFile and selectedFilename.endswith(EXTENSION_TSX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_TPX in self.typeFile and selectedFilename.endswith(EXTENSION_TPX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_TGX in self.typeFile and selectedFilename.endswith(EXTENSION_TGX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_TCX in self.typeFile and selectedFilename.endswith(EXTENSION_TCX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_TDX in self.typeFile and selectedFilename.endswith(EXTENSION_TDX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_TUX in self.typeFile and selectedFilename.endswith(EXTENSION_TUX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_TAX in self.typeFile and selectedFilename.endswith(EXTENSION_TAX):
                    self.selectedFilename = selectedFilename
                elif EXTENSION_PNG in self.typeFile and selectedFilename.endswith(EXTENSION_PNG):
                    self.selectedFilename = selectedFilename
                else:
                    pass
                if self.selectedFilename is not None:
                    if len(self.selectedFilename):
                        QDialog.accept(self)
        else:
            raise Exception( 'local repo mode not supported: %s' % self.typeMode)

    def getSelection(self, withRepoName=False):
        """
        Returns selection

        @return:
        @rtype:
        """
        if self.multipleSelection:
            return self.selectedFilenames
        else:
            if withRepoName:
                return "local-tests:/%s" % self.selectedFilename
            return self.selectedFilename

    def updateCurrentPath (self, dirValue):
        """
        Update the current path

        @param dirValue:
        @type dirValue:
        """
        self.selectedFilename = dirValue

class Item(QTreeWidgetItem, Logger.ClassLogger):
    """
    Item widget
    """
    def __init__( self, repo, txt, parent = None,
                        type = QTreeWidgetItem.UserType+1, isRoot = False, itemTxt=None):
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
        """
        QTreeWidgetItem.__init__(self, parent, type)

        self.repo = repo
        self.folderName = str(txt)

        self.fileName = None
        self.fileExtension = None

        self.setIcon(0, self.repo.folderIcon)
        if isRoot:
            self.setText(0, itemTxt)
        else:
            self.setText(0, txt)
        if isRoot:  # root of the repository
            self.setExpanded(True)
            self.setIcon(0, self.repo.rootIcon)
        if type == QTreeWidgetItem.UserType+0: # file
            # issue 8 fix begin
            tmp =  txt.rsplit('.', 1)
            if len(tmp) == 2:
                self.fileName = tmp[0]
                self.fileExtension = tmp[1]
            else:
                raise Exception("file type unknown")
            # issue 8 fix end 
            if self.fileExtension.lower() == EXTENSION_TSX:
                self.setIcon(0, self.repo.testSuiteIcon)
            elif self.fileExtension.lower() == EXTENSION_TPX:
                self.setIcon(0, self.repo.testPlanIcon)
            elif self.fileExtension.lower() == EXTENSION_TGX:
                self.setIcon(0, self.repo.testGlobalIcon)
            elif self.fileExtension.lower() == EXTENSION_TCX:
                self.setIcon(0, self.repo.testConfigIcon)
            elif self.fileExtension.lower() == EXTENSION_TDX:
                self.setIcon(0, self.repo.testDataIcon)
            elif self.fileExtension.lower() == EXTENSION_TUX:
                self.setIcon(0, self.repo.testUnitIcon)
            elif self.fileExtension.lower() == EXTENSION_TAX:
                self.setIcon(0, self.repo.testAbstractIcon)
            elif self.fileExtension.lower() == EXTENSION_PNG:
                self.setIcon(0, self.repo.pngIcon)
            else:
                raise Exception("file extension unknown: %s" % self.fileExtension)

            self.setText(0, self.fileName)

    def getExtension(self):
        """
        Return extension
        """
        return str(self.fileExtension)

    def renameDir (self, oldName, newName):
        """
        Rename the folder

        @param oldName: 
        @type oldName:

        @param newName: 
        @type newName:
        """
        try:
            absPath = self.getPath(withFileName = False, withFolderName = False)
            newName = str(newName)
            pathOld =  absPath + '/' + oldName
            pathNew = absPath + '/' + newName 
            self.trace( pathOld )
            self.trace( pathNew )
            os.rename( pathOld, pathNew )
            self.folderName = newName
        except Exception as e:
            self.setText(0, oldName)
            self.error( "unable to rename folder: %s" % e )

    def renameFile (self, oldName, newName):
        """
        Rename the file

        @param oldName: 
        @type oldName:

        @param newName: 
        @type newName:
        """
        try:
            absPath = self.getPath(withFileName = False, withFolderName = False)
            newName = str(newName)
            pathOld = absPath + '/' + oldName + '.' + self.fileExtension
            pathNew = absPath + '/' + newName + '.' + self.fileExtension
            self.trace( pathOld )
            self.trace( pathNew )
            os.rename( pathOld, pathNew)
            self.fileName = newName
        except Exception as e:
            self.setText(0, oldName)
            self.error( "unable to rename file: %s" % e )

    def createSubDirectory (self, folderName):
        """
        Create a sub folder

        @param folderName: 
        @type folderName:
        """
        try:
            absPath = self.getPath(withFolderName = True, withFileName = False)
            res = os.path.exists(absPath + '/' + str(folderName ))
            if res:
                QMessageBox.information(self.repo,  "Creation", "This directory already exists")
            else:
                os.mkdir( absPath + '/' + str(folderName) )
                newItem = Item( repo = self.repo,  parent = self, txt = folderName)
                self.addChild( newItem )
                self.setExpanded(True)
                self.setSelected(False)

        except Exception as e:
            self.error( "unable to create sub folder: %s" % e )
    
    def getPath(self, withFileName = True, withFolderName = False):
        """
        Returns the path
        """
        p = self.parent()

        if withFolderName:
            path = [ self.folderName ]
        else: 
            path = [ ]

        if withFileName:
            path.append( "%s.%s" % ( self.fileName, self.fileExtension) )

        while p != None:
            path.append( str(p.folderName) )
            p = p.parent()

        path.reverse()
        return '/'.join(path)
    
    def rmDir (self):
        """
        Deletes folders
        """
        try:
            absPath = self.getPath(withFolderName = True, withFileName = False)
            nb_dirs = len(os.listdir(absPath))
            if nb_dirs > 0:
                QMessageBox.information(self.repo,  "Delete", "The directory is not empty")
            else:
                reply = QMessageBox.question( self.repo, "Delete", "Are you sure ?", 
                                                    QMessageBox.Yes | QMessageBox.No )
                if reply == QMessageBox.Yes:
                    
                    os.rmdir(absPath)
                    self.parent().removeChild(self)
        except Exception as e:
            self.error( "unable to delete folder: %s" % e )

    def rmFile (self):
        """
        Deletes file
        """
        try:
            reply = QMessageBox.question( self.repo, "Delete", "Are you sure ?",
                                                QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                absPath = self.getPath( withFolderName = False, withFileName = True )
                os.remove(absPath)
                self.parent().removeChild(self)
        except Exception as e:
            self.error( "unable to delete file: %s" % e )

class TreeWidgetRepository(QTreeWidget):
    """
    Tree widget
    """
    def __init__(self, parent):
        """
        Treewidget constructor
        """
        QTreeWidget.__init__(self, parent)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
    def startDrag(self, dropAction):
        """
        Start drag
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
            pathFile = self.itemCurrent.getPath(withFileName = False)
            if len(pathFile) > 1 :
                meta = {}
                meta['repotype'] = UCI.REPO_TESTS_LOCAL
                meta['pathfile'] = pathFile
                meta['filename'] = self.itemCurrent.fileName
                meta['ext'] = self.itemCurrent.fileExtension

                # create mime data object
                mime = QMimeData()
                mime.setData('application/x-%s-repo-openfile' % Settings.instance().readValue( key = 'Common/acronym' ).lower() , pickle.dumps(meta) )
                # start drag 
                drag = QDrag(self)
                drag.setMimeData(mime)    
                
                drag.exec_(Qt.CopyAction)

class Repository(QWidget, Logger.ClassLogger):
    """
    Repository widget
    """
    OpenFile = pyqtSignal(str, str, str, bool, object, int)
    def __init__(self, parent = None,  withFile = True):
        """
        Repository widget

        @param parent: 
        @type parent:

        @param withFile: 
        @type withFile:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.withFile = withFile
        self.itemCurrent = None

        self.wrepository = None
        
        style = self.parent.style()
        self.folderIcon = QIcon()
        self.rootIcon = QIcon()
        self.folderIcon.addPixmap( style.standardPixmap(QStyle.SP_DirClosedIcon), QIcon.Normal, QIcon.Off)
        self.folderIcon.addPixmap( style.standardPixmap(QStyle.SP_DirOpenIcon), QIcon.Normal, QIcon.On)
        self.rootIcon.addPixmap( style.standardPixmap(QStyle.SP_DriveHDIcon) )
        self.testSuiteIcon = QIcon(":/%s.png" % EXTENSION_TSX)
        self.testPlanIcon = QIcon(":/%s.png" % EXTENSION_TPX)
        self.testGlobalIcon = QIcon(":/%s.png" % EXTENSION_TGX)
        self.testConfigIcon = QIcon(":/%s.png" % EXTENSION_TCX)
        self.testDataIcon = QIcon(":/%s.png" % EXTENSION_TDX )
        self.testUnitIcon = QIcon(":/%s.png" % EXTENSION_TUX )
        self.testAbstractIcon = QIcon(":/%s.png" % EXTENSION_TAX )
        self.pngIcon = QIcon(":/%s.png" % EXTENSION_PNG )


        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.createToolbarLocal()

        self.itemEdited = None
    
    def initRepo(self):
        """
        Initialize the repository
        """
        if RCI.instance().isAuthenticated():
            testcasesRoot = Item(repo = self, parent = self.wrepository, 
                                 txt = "%s" % Settings.instance().readValue( key = 'Repositories/local-repo' ), 
                                 type = QTreeWidgetItem.UserType+10, 
                                 isRoot = True, itemTxt="Root" )
            testcasesRoot.setSelected(True)
            self.createRepository("%s" % Settings.instance().readValue( key = 'Repositories/local-repo' ), parent = testcasesRoot )

    def active(self):
        """
        Active the repository
        """
        self.wrepository.clear()
        self.wrepository.setEnabled(True)
        self.initRepo()

    def deactive(self):
        """
        Disable the repository
        """
        self.wrepository.setEnabled(False)
        self.wrepository.clear()

    def keyPressEvent(self, event):
        """
        Called on key press
        Reimplement from widget
        """
        if event.key() == Qt.Key_Delete:
            self.deleteItem()       
        return QWidget.keyPressEvent(self, event)

    def createActions (self):
        """
        Create qt actions
        """
        self.refreshAction = QtHelper.createAction(self, "&Refresh", self.refreshAll, icon = QIcon(":/refresh.png"), 
                                                    tip = 'Refresh local repository content' )
        self.addDirAction = QtHelper.createAction(self, "&Add", self.createItem, icon = QIcon(":/folder_add.png"), 
                                                    tip = 'Create new folder' )
        self.delFileAction = QtHelper.createAction(self, "&Delete File", self.deleteItem, 
                                                    icon = QIcon(":/delete_file.png"), shortcut=QKeySequence.Delete, 
                                                    tip = 'Delete file' )
        self.delDirAction = QtHelper.createAction(self, "&Delete Folder", self.deleteItem, 
                                                    icon = QIcon(":/folder_delete.png"), shortcut=QKeySequence.Delete, 
                                                    tip = 'Delete folder' )
        self.renameAction = QtHelper.createAction(self, "&Rename", self.renameItem, icon = QIcon(":/rename.png"), 
                                                    tip = 'Rename' )

        self.expandSubtreeAction = QtHelper.createAction(self, "&Expand folder...", self.expandSubFolder, icon = None, 
                                                    tip = 'Expand folder' )
        self.expandAllAction = QtHelper.createAction(self, "&Expand All", self.expandAllFolders, icon = None, 
                                                    tip = 'Expand all folders' )
        self.collapseAllAction  = QtHelper.createAction(self, "&Collapse All", self.collapseAllFolders, icon = None, 
                                                    tip = 'Collapse all folder' )

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
        Expand the sub folder
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

    def defaultActions(self):
        """
        Set the default actions values
        """
        self.refreshAction.setEnabled(False)
        self.addDirAction.setEnabled(False)
        self.delFileAction.setEnabled(False)
        self.delDirAction.setEnabled(False)
        self.renameAction.setEnabled(False)
        self.expandSubtreeAction.setEnabled(False)
        self.expandAllAction.setEnabled(False)
        self.collapseAllAction.setEnabled(False)

    def onPopupMenu(self, pos):
        """
        Called on popup right menu

        @param pos: 
        @type pos:
        """
        item = self.wrepository.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.itemCurrent = item
            self.wrepository.itemCurrent = item
            if item.type() == QTreeWidgetItem.UserType+0: # file
                self.menu.addAction( self.delFileAction )
                self.menu.addSeparator()
                self.menu.addAction( self.renameAction )
            elif item.type() == QTreeWidgetItem.UserType+1: # dir
                self.menu.addAction( self.expandSubtreeAction )
                self.menu.addSeparator()
                self.menu.addAction( self.addDirAction )
                self.menu.addSeparator()
                self.menu.addAction( self.delDirAction )
                self.menu.addSeparator()
                self.menu.addAction( self.renameAction )
            if item.type() == QTreeWidgetItem.UserType+10 :
                self.menu.addAction( self.refreshAction )
                self.menu.addSeparator()
                self.menu.addAction( self.expandAllAction )
                self.menu.addAction( self.collapseAllAction )
                self.menu.addSeparator()
                self.menu.addAction( self.addDirAction )
            self.menu.popup(self.mapToGlobal(pos))

    def createConnections (self):
        """
        Create qc connections
        """
        self.wrepository.itemDoubleClicked.connect(self.openFile)
        self.wrepository.itemChanged.connect(self.onItemChanged)
        self.wrepository.currentItemChanged.connect(self.onCurrentItemChanged)
        self.wrepository.customContextMenuRequested.connect(self.onPopupMenu)

    def createWidgets (self):
        """
        Create qt widgets
        """
        self.dockToolbarLocal = QToolBar(self)
        self.dockToolbarLocal.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border
        

        self.wrepository = TreeWidgetRepository(parent=self)
        self.wrepository.setFrameShape(QFrame.NoFrame)
        if USE_PYQT5:
            self.wrepository.header().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.wrepository.header().setResizeMode(QHeaderView.Stretch)
        self.wrepository.setHeaderHidden(True)
        self.wrepository.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wrepository.setIndentation(10)

        layout = QVBoxLayout()
        layout.addWidget(self.wrepository)
        layout.addWidget(self.dockToolbarLocal)

        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def createToolbarLocal(self):
        """
        Toolbar creation
            
        ||--|||
        ||  |||
        ||--|||
        """
        self.dockToolbarLocal.setObjectName("Local Repository toolbar")
        self.dockToolbarLocal.addAction(self.refreshAction)
        self.dockToolbarLocal.addSeparator()
        self.dockToolbarLocal.addAction(self.addDirAction)
        self.dockToolbarLocal.addAction(self.delDirAction)
        self.dockToolbarLocal.addAction(self.delFileAction)
        self.dockToolbarLocal.addSeparator()
        self.dockToolbarLocal.addAction(self.renameAction)
        self.dockToolbarLocal.setIconSize(QSize(16, 16))

    def createRepository(self, path, parent):
        """
        Create repository

        @param path: 
        @type path:

        @param parent: 
        @type parent:
        """
        self.refreshAction.setEnabled(True)
        try:
            for d in  os.listdir(path):
                if not os.path.isfile(path + '/' + d):
                    # is directory
                    item = Item(repo = self, parent = parent, txt = d )
                    self.createRepository( path + '/' + d, item )
                else:
                    if self.withFile:
                        if d.lower().endswith( tuple(SUPPORTED_EXTENSIONS) ):
                            # is file
                            item = Item(repo = self, parent = parent, 
                                        txt = d, 
                                        type = QTreeWidgetItem.UserType+0 )
        except Exception as e:
            self.error( e )
    
    def openFile (self, witem, col):
        """
        Open file

        @param witem: 
        @type witem:

        @param col: 
        @type col:
        """
        if witem.type() == QTreeWidgetItem.UserType+0 :
            path = witem.getPath(withFileName = False)
            self.OpenFile.emit(path, witem.fileName, witem.fileExtension, False, None, UCI.REPO_TESTS_LOCAL)
            
    def deleteItem (self):
        """
        Delete item
        """
        if self.itemCurrent.type() == QTreeWidgetItem.UserType+0:
            self.itemCurrent.rmFile()
        elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1:
            self.itemCurrent.rmDir()
        else:
            self.error( "should not be happened" )

    def createItem (self):
        """
        Create item
        """
        if self.itemCurrent is not None:
            txt, ok = QInputDialog.getText(self, "Create", "Enter name:", QLineEdit.Normal)
            if ok and txt:
                self.itemCurrent.createSubDirectory(folderName = txt)
                self.itemCurrent.setSelected(False)

    def refreshAll (self):
        """
        Refresh all
        """
        self.wrepository.clear()
        testcasesRoot = Item(repo = self, parent = self.wrepository, 
                             txt = "%s" % Settings.instance().readValue( key = 'Repositories/local-repo' ),
                             type = QTreeWidgetItem.UserType+10, isRoot = True, itemTxt="Root"  )
        testcasesRoot.setSelected(True)
        if "%s" % Settings.instance().readValue( key = 'Repositories/local-repo' ) == 'Undefined':
            self.wrepository.setEnabled(False)
            self.refreshAction.setEnabled(False)
        else:
            self.createRepository("%s" % Settings.instance().readValue( key = 'Repositories/local-repo' ), parent = testcasesRoot )
        self.defaultActions()
        self.refreshAction.setEnabled(True)

    def renameItem(self):
        """
        Rename item
        """
        self.itemCurrent.setFlags(  Qt.ItemIsEditable | Qt.ItemIsEnabled )
        self.wrepository.editItem(self.itemCurrent, 0) 
        self.itemEdited = ( self.itemCurrent,  self.itemCurrent.text(0) )
        self.itemCurrent.setFlags( Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def onCurrentItemChanged (self, witem1, witem2):
        """
        Called when the current item changed

        @param witem1: 
        @type witem1:

        @param witem2: 
        @type witem2:
        """
        self.itemEdited = None
        self.itemCurrent = witem1
        self.wrepository.itemCurrent = witem1
        if self.itemCurrent is not None:
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # file
                self.addDirAction.setEnabled(False)
                self.delFileAction.setEnabled(True)
                self.delDirAction.setEnabled(False)
                self.renameAction.setEnabled(True)
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
            elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1: # dir
                self.addDirAction.setEnabled(True)
                self.delFileAction.setEnabled(False)
                self.delDirAction.setEnabled(True)
                self.renameAction.setEnabled(True)
                self.expandSubtreeAction.setEnabled(True)
                self.expandAllAction.setEnabled(False)
                self.collapseAllAction.setEnabled(False)
            elif self.itemCurrent.type() == QTreeWidgetItem.UserType+10 : #root
                self.addDirAction.setEnabled(True)
                self.delFileAction.setEnabled(False)
                self.delDirAction.setEnabled(False)
                self.renameAction.setEnabled(False)
                self.expandSubtreeAction.setEnabled(False)
                self.expandAllAction.setEnabled(True)
                self.collapseAllAction.setEnabled(True)
            else:
                pass

    def onItemChanged (self, witem, col):
        """
        Called when item changed

        @param witem: 
        @type witem:

        @param col: 
        @type col:
        """
        if self.itemEdited != None: 
            if witem.text(0) != self.itemEdited[1]:
                if self.itemCurrent.type() == QTreeWidgetItem.UserType+0:
                    witem.renameFile (oldName = self.itemEdited[1], newName =  witem.text(0) )
                elif self.itemCurrent.type() == QTreeWidgetItem.UserType+1:
                    witem.renameDir (oldName = self.itemEdited[1], newName =  witem.text(0) )
                else:
                    self.error( "should not be happened" )
                self.itemEdited = None
