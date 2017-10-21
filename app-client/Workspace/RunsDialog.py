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
Runs module
"""
import sys

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

USE_PYQT5 = False    
try:
    from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QComboBox, QTreeWidget, QFrame, 
                            QHeaderView, QListWidget, QPushButton, QCheckBox, QRadioButton, 
                            QDateTimeEdit, QTreeWidgetItem, QListWidgetItem, QIcon)
    from PyQt4.QtCore import (pyqtSignal, Qt, QDateTime)
except ImportError:
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QComboBox, QTreeWidget, QFrame, 
                                QHeaderView, QListWidget, QPushButton, QCheckBox, QRadioButton, 
                                QDateTimeEdit, QTreeWidgetItem, QListWidgetItem)
    from PyQt5.QtCore import (pyqtSignal, Qt, QDateTime)
    USE_PYQT5 = True    
    
from Libs import QtHelper, Logger
import UserClientInterface as UCI

class RunsDialog(QtHelper.EnhancedQDialog):
    """
    Runs several dialog
    """
    RefreshRepository = pyqtSignal(str)
    def __init__(self, dialogName, parent = None, iRepo=None, lRepo=None, rRepo=None):
        """
        Constructor
        """
        QtHelper.EnhancedQDialog.__init__(self, parent)

        self.name = self.tr("Prepare a group of runs")
        self.projectReady = False
        self.iRepo = iRepo
        self.lRepo = lRepo
        self.rRepo = rRepo

        self.createDialog()
        self.createConnections()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( self.name )

        mainLayout = QHBoxLayout()
        layoutTests = QHBoxLayout()
        layoutRepoTest = QVBoxLayout()

        self.prjCombo = QComboBox(self)
        self.prjCombo.setEnabled(False)

        self.repoTests = QTreeWidget(self)
        self.repoTests.setFrameShape(QFrame.NoFrame)
        if USE_PYQT5:
            self.repoTests.header().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.repoTests.header().setResizeMode(QHeaderView.Stretch)
        self.repoTests.setHeaderHidden(True)
        self.repoTests.setContextMenuPolicy(Qt.CustomContextMenu)
        self.repoTests.setIndentation(10)

        layoutRepoTest.addWidget(self.prjCombo)
        layoutRepoTest.addWidget(self.repoTests)

        self.testsList = QListWidget(self)

        layoutTests.addLayout( layoutRepoTest )
        layoutTests.addWidget( self.testsList )
        mainLayout.addLayout( layoutTests )

        buttonLayout = QVBoxLayout()

        self.okButton = QPushButton(self.tr("Execute All"), self)
        self.okButton.setEnabled(False)
        self.cancelButton = QPushButton(self.tr("Cancel"), self)
        self.upButton = QPushButton(self.tr("UP"), self)
        self.upButton.setEnabled(False)
        self.downButton = QPushButton(self.tr("DOWN"), self)
        self.downButton.setEnabled(False)
        self.clearButton = QPushButton(self.tr("Remove All"), self)
        self.delButton = QPushButton(self.tr("Remove"), self)
        self.delButton.setEnabled(False)

        self.runSimultaneous = QCheckBox(self.tr("Simultaneous Run"))
        
        self.schedImmed = QRadioButton(self.tr("Run Immediately"))
        self.schedImmed.setChecked(True)
        self.schedAt = QRadioButton(self.tr("Run At:"))
        self.schedAtDateTimeEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.schedAtDateTimeEdit.setEnabled(False)

        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.runSimultaneous)
        buttonLayout.addWidget(self.schedImmed)
        buttonLayout.addWidget(self.schedAt)
        buttonLayout.addWidget(self.schedAtDateTimeEdit)

        
        buttonLayout.addWidget( self.upButton )
        buttonLayout.addWidget( self.downButton )
        buttonLayout.addWidget( self.delButton )
        buttonLayout.addWidget( self.clearButton )

        buttonLayout.addWidget(self.cancelButton)

        mainLayout.addLayout(buttonLayout)

        self.setMinimumHeight(400)
        self.setMinimumWidth(750)
        self.setLayout(mainLayout)

    def initProjects(self, projects=[], defaultProject=1):
        """
        Initialize projects
        """
        # init date and time
        self.schedAtDateTimeEdit.setDateTime(QDateTime.currentDateTime()) 

        self.projectReady = False

        self.repoTests.clear()
        self.prjCombo.clear()
        self.testsList.clear()

        self.prjCombo.setEnabled(True)
        
        # insert data
        pname = ''
        for p in projects:
            self.prjCombo.addItem ( p['name']  )
            if defaultProject == p['project_id']:
                pname = p['name']
        
        for i in xrange(self.prjCombo.count()):
            item_text = self.prjCombo.itemText(i)
            if str(pname) == str(item_text):
                self.prjCombo.setCurrentIndex(i)

        self.projectReady = True
        self.RefreshRepository.emit(pname)

    def initializeTests(self, listing):
        """
        Initialize tests
        """
        self.repoTests.clear()
        #self.testRoot = Repositories.RemoteRepository.Item(repo = Repositories.instance().remote(), parent = self.repoTests, txt = "Root", 
        self.testRoot = self.rRepo.Item(repo = self.iRepo.remote(), parent = self.repoTests, txt = "Root", 
                                                            type = QTreeWidgetItem.UserType+10, isRoot = True )
        self.testRoot.setSelected(True)
        self.createRepository(listing=listing, parent=self.testRoot,fileincluded=True)
        self.repoTests.sortItems(0, Qt.AscendingOrder)

        self.hideItems(hideTsx=False, hideTpx=False, hideTcx=True, hideTdx=True, hideTxt=True, hidePy=True,
                                hideTux=False, hidePng=True, hideTgx=False, hideTax=False)

    def createRepository(self, listing, parent, fileincluded=True):
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
                    #item = Repositories.RemoteRepository.Item(repo = Repositories.instance().remote(), parent = parent, txt = dct["name"], propertiesFile=dct )
                    item = self.rRepo.Item(repo = self.iRepo.remote(), parent = parent, txt = dct["name"], propertiesFile=dct )
                    self.createRepository(  dct["content"] , item, fileincluded )
                else:
                    if fileincluded:
                        if dct["type"] == "file":
                            #pname = Repositories.instance().remote().getProjectName(dct["project"])
                            pname = self.iRepo.remote().getProjectName(dct["project"])
                            # {'modification': 1342259500, 'type': 'file', 'name': '__init__.py', 'size': '562 }
                            #item = Repositories.RemoteRepository.Item(repo = Repositories.instance().remote(), parent = parent, txt = dct["name"] ,
                            item = self.rRepo.Item(repo = self.iRepo.remote(), parent = parent, txt = dct["name"] ,
                                                        propertiesFile=dct, type = QTreeWidgetItem.UserType+0, projectId=dct["project"], projectName=pname )

        except Exception as e:
            self.error( "unable to create tree for runs: %s" % e )

    def onProjectChanged(self, projectItem):
        """
        Called when the project changed on the combo box
        """
        if self.projectReady:
            item_text = self.prjCombo.itemText(projectItem)
            self.RefreshRepository.emit(item_text)

    def createConnections (self):
        """
        create qt connections
         * ok
         * cancel
        """
        self.prjCombo.currentIndexChanged.connect(self.onProjectChanged)
        self.okButton.clicked.connect( self.acceptClicked )
        self.cancelButton.clicked.connect( self.reject )
        self.upButton.clicked.connect(self.upTest)
        self.downButton.clicked.connect(self.downTest)
        self.clearButton.clicked.connect(self.clearList)
        self.delButton.clicked.connect(self.delTest)

        self.testsList.itemClicked.connect(self.onItemSelected)
        self.testsList.itemSelectionChanged.connect(self.onItemSelectionChanged)

        self.schedAt.toggled.connect(self.onSchedAtActivated)

        self.repoTests.itemDoubleClicked.connect( self.onTestDoucleClicked )

    def onSchedAtActivated(self, toggled):
        """
        On sched at button activated
        """
        if toggled:
            self.schedAtDateTimeEdit.setEnabled(True)
        else:
            self.schedAtDateTimeEdit.setEnabled(False)

    def onItemSelectionChanged(self):
        """
        Called on item selection changed
        """
        self.onItemSelected(itm=None)

    def onItemSelected(self, itm):
        """
        Call on item selected
        """
        selectedItems = self.testsList.selectedItems()
        if len(selectedItems):
            self.delButton.setEnabled(True)
            self.upButton.setEnabled(True)
            self.downButton.setEnabled(True)
        else:
            self.delButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.downButton.setEnabled(False)

        #if not len(self.testsList.count()):
        if not self.testsList.count():
            self.okButton.setEnabled(False)

    def upTest(self):
        """
        Up test
        """
        currentRow = self.testsList.currentRow()
        currentItem = self.testsList.takeItem(currentRow)
        self.testsList.insertItem(currentRow - 1, currentItem)

    def downTest(self):
        """
        Down test
        """
        currentRow = self.testsList.currentRow()
        currentItem = self.testsList.takeItem(currentRow)
        self.testsList.insertItem(currentRow + 1, currentItem)


    def delTest(self):
        """
        Del test
        """
        currentRow = self.testsList.currentRow()
        currentItem = self.testsList.takeItem(currentRow)

    def clearList(self):
        """
        Clear test
        """
        self.testsList.clear()
        self.delButton.setEnabled(False)
        self.upButton.setEnabled(False)
        self.downButton.setEnabled(False)

        self.okButton.setEnabled(False)

    def iterateTree(self, item, hideTsx, hideTpx, hideTcx, hideTdx, hideTxt, hidePy, hideTux, hidePng, hideTgx, hideTax):
        """
        Iterate tree
        """
        child_count = item.childCount()
        for i in range(child_count):
            subitem = item.child(i)
            subchild_count = subitem.childCount()
            if subchild_count > 0:
                self.iterateTree(item=subitem, hideTsx=hideTsx, hideTpx=hideTpx, hideTcx=hideTcx, hideTdx=hideTdx, hideTxt=hideTxt,
                                    hidePy=hidePy, hideTux=hideTux, hidePng=hidePng, hideTgx=hideTgx, hideTax=hideTax)
            else:
                #if hideTux and subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TUX:
                if hideTux and subitem.getExtension() == self.rRepo.EXTENSION_TUX:
                    subitem.setHidden (True)
                #elif hideTpx and subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TPX:
                elif hideTpx and subitem.getExtension() == self.rRepo.EXTENSION_TPX:
                    subitem.setHidden (True)
                #elif hideTgx and subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TGX:
                elif hideTgx and subitem.getExtension() == self.rRepo.EXTENSION_TGX:
                    subitem.setHidden (True)
                #elif hideTcx and subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TCX:
                elif hideTcx and subitem.getExtension() == self.rRepo.EXTENSION_TCX:
                    subitem.setHidden (True)
                #elif hideTsx and  subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TSX:
                elif hideTsx and  subitem.getExtension() == self.rRepo.EXTENSION_TSX:
                    subitem.setHidden (True)
                #elif hideTdx and  subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TDX:
                elif hideTdx and  subitem.getExtension() == self.rRepo.EXTENSION_TDX:
                    subitem.setHidden (True)
                #elif hideTxt and  subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_TXT:
                elif hideTxt and  subitem.getExtension() == self.rRepo.EXTENSION_TXT:
                    subitem.setHidden (True)
                #elif hidePy and  subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_PY:
                elif hidePy and  subitem.getExtension() == self.rRepo.EXTENSION_PY:
                    subitem.setHidden (True)
                #elif hidePng and  subitem.getExtension() == Repositories.RemoteRepository.EXTENSION_PNG:
                elif hidePng and  subitem.getExtension() == self.rRepo.EXTENSION_PNG:
                    subitem.setHidden (True)
                elif hideTax and  subitem.getExtension() == self.rRepo.EXTENSION_TAx:
                    subitem.setHidden (True)
                else:
                    subitem.setHidden(False)

    def hideItems(self, hideTsx=False, hideTpx=False, hideTcx=False, hideTdx=False, hideTxt=False, hidePy=False, 
                        hideTux=False, hidePng=False, hideTgx=False, hideTax=False):
        """
        Hide items
        """
        root = self.repoTests.invisibleRootItem()
        self.iterateTree(item=root, hideTsx=hideTsx, hideTpx=hideTpx, hideTcx=hideTcx, hideTdx=hideTdx, hideTxt=hideTxt, hidePy=hidePy,
                            hideTux=hideTux, hidePng=hidePng, hideTgx=hideTgx, hideTax=hideTax)

    def onTestDoucleClicked(self, testItem):
        """
        On tests double clicked
        """
        if testItem.type() != QTreeWidgetItem.UserType+0:
            return

        self.okButton.setEnabled(True)

        currentProject = self.prjCombo.currentText()

        testName = "%s:%s" % (str(currentProject),testItem.getPath(withFileName = True))
        testItem = QListWidgetItem(testName )

        #if testName.endswith(Repositories.RemoteRepository.EXTENSION_TUX):
        if testName.endswith(self.rRepo.EXTENSION_TUX):
            testItem.setIcon(QIcon(":/tux.png"))
        #if testName.endswith(Repositories.RemoteRepository.EXTENSION_TSX):
        if testName.endswith(self.rRepo.EXTENSION_TSX):
            testItem.setIcon(QIcon(":/tsx.png"))
        #if testName.endswith(Repositories.RemoteRepository.EXTENSION_TPX):
        if testName.endswith(self.rRepo.EXTENSION_TPX):
            testItem.setIcon(QIcon(":/tpx.png"))
        #if testName.endswith(Repositories.RemoteRepository.EXTENSION_TGX):
        if testName.endswith(self.rRepo.EXTENSION_TGX):
            testItem.setIcon(QIcon(":/tgx.png"))
        #if testName.endswith(Repositories.RemoteRepository.EXTENSION_TAX):
        if testName.endswith(self.rRepo.EXTENSION_TAX):
            testItem.setIcon(QIcon(":/tax.png"))
            
        self.testsList.addItem( testItem )

    def acceptClicked (self):
        """
        Called on accept button
        """
        self.accept()
    
    def getTests(self):
        """
        Returns all tests in the list
        """
        tests = []
        for i in xrange(self.testsList.count()):
            testItem = self.testsList.item(i)
            tests.append( str(testItem.text()) )

        runSimultaneous = False
        if self.runSimultaneous.isChecked(): runSimultaneous = True
        
        if self.schedImmed.isChecked():
            runAt = (0,0,0,0,0,0)
            return (tests, False, runAt, runSimultaneous)
        else:
            pydt = self.schedAtDateTimeEdit.dateTime().toPyDateTime()
            runAt = (pydt.year, pydt.month, pydt.day, pydt.hour, pydt.minute, pydt.second)
            return (tests, True, runAt, runSimultaneous)