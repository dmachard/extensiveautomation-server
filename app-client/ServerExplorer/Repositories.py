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
Plugin repositories
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range

try:
    from PyQt4.QtGui import (QWidget, QGroupBox, QLabel, QFormLayout, QHBoxLayout, QTreeWidgetItem, 
                            QIcon, QBrush, QTreeWidget, QToolBar, QVBoxLayout, QGridLayout, QComboBox, 
                            QMenu, QFileDialog, QMessageBox, QInputDialog, QColor, QLineEdit, QTabWidget, QFrame)
    from PyQt4.QtCore import (Qt, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon, QBrush, QColor)
    from PyQt5.QtWidgets import (QWidget, QGroupBox, QLabel, QFormLayout, QHBoxLayout, QLineEdit,
                                QTreeWidgetItem, QTreeWidget, QToolBar, QVBoxLayout, QGridLayout, 
                                QComboBox, QMenu, QFileDialog, QMessageBox, QInputDialog, QTabWidget, QFrame)
    from PyQt5.QtCore import (Qt, QSize)
    
import UserClientInterface as UCI
import RestClientInterface as RCI
from Libs import QtHelper, Logger

COL_NAME        =   0
COL_DATE        =   1
COL_SIZE        =   2


try:
    xrange
except NameError: # support python3
    xrange = range

class FileStats(QWidget):
    def __init__(self, parent, boxName='undefined'):
        """
        """
        QWidget.__init__(self, parent)
        self.boxName = boxName
        self.createWidgets()
    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.fileBox = QGroupBox("%s (Size)" % self.boxName)
        self.minSizeLabel = QLabel("0")
        self.maxSizeLabel = QLabel("0")
        self.avgSizeLabel = QLabel("0")
        self.nbFilesLabel = QLabel("0")
        
        fileLayout = QFormLayout()
        fileLayout.addRow(QLabel("Min"), self.minSizeLabel )
        fileLayout.addRow(QLabel("Max"), self.maxSizeLabel )
        fileLayout.addRow(QLabel("Avg"), self.avgSizeLabel )
        fileLayout.addRow(QLabel("TOTAL"), self.nbFilesLabel )
        self.fileBox.setLayout(fileLayout)
        
        layoutFinal = QHBoxLayout()
        layoutFinal.addWidget(self.fileBox)
        self.setLayout(layoutFinal)
    def resetStats(self):
        """
        """
        self.minSizeLabel.setText( "0" )
        self.maxSizeLabel.setText( "0" )
        self.avgSizeLabel.setText( "0" )
        self.nbFilesLabel.setText( "0" )
    def loadStats(self, data):
        """
        """
        self.minSizeLabel.setText( "%s" % QtHelper.bytes2human( data['min'] )  )
        self.maxSizeLabel.setText( "%s" % QtHelper.bytes2human( data['max'] )  )
        self.avgSizeLabel.setText( "%s" % QtHelper.bytes2human( int(data['total'] / data['nb']  )) )
        self.nbFilesLabel.setText( "%s Files" % data['nb'] )

class DiskStats(QWidget):
    def __init__(self, parent, boxName='Disk Usage'):
        """
        """
        QWidget.__init__(self, parent)
        self.boxName=boxName
        self.createWidgets()
    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.diskUsageBox = QGroupBox(self.boxName)
        self.nbDiskUsedLabel = QLabel("0")
        self.nbDiskFreeLabel = QLabel("0")
        self.nbDiskTotalLabel = QLabel("0")
        
        layout2 = QFormLayout()
        layout2.addRow(QLabel("Total"), self.nbDiskTotalLabel )
        layout2.addRow(QLabel("Used"), self.nbDiskUsedLabel )
        layout2.addRow(QLabel("Free"), self.nbDiskFreeLabel )
        self.diskUsageBox.setLayout(layout2)
        
        layoutFinal = QHBoxLayout()
        layoutFinal.addWidget(self.diskUsageBox)
        self.setLayout(layoutFinal) 
    def resetStats(self):
        """
        """
        self.nbDiskUsedLabel.setText( "0" )
        self.nbDiskFreeLabel.setText( "0" )
        self.nbDiskTotalLabel.setText( "0" )    
    def loadStats(self, data):
        """
        """
        self.nbDiskUsedLabel.setText( "%s" % QtHelper.bytes2human( int(data['used']) )  )
        self.nbDiskFreeLabel.setText( "%s" % QtHelper.bytes2human( int(data['free']) )  )
        self.nbDiskTotalLabel.setText( "%s" % QtHelper.bytes2human( int(data['total']) )  )

class RepoStats(QWidget):
    def __init__(self, parent, boxName='Repository Usage'):
        """
        """
        QWidget.__init__(self, parent)
        self.boxName=boxName
        self.createWidgets()
    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.diskUsageBox = QGroupBox(self.boxName)
        self.nbDiskFilesUsedLabel = QLabel("0")
        self.nbDiskTotalFilesLabel = QLabel("0")
        
        layout2 = QFormLayout()
        layout2.addRow(QLabel("Used"), self.nbDiskFilesUsedLabel )
        layout2.addRow(QLabel("TOTAL"), self.nbDiskTotalFilesLabel )
        self.diskUsageBox.setLayout(layout2)
        
        layoutFinal = QHBoxLayout()
        layoutFinal.addWidget(self.diskUsageBox)
        self.setLayout(layoutFinal)
    def resetStats(self):
        """
        """
        self.nbDiskFilesUsedLabel.setText( "0" )
        self.nbDiskTotalFilesLabel.setText( "0" )
    def loadStats(self, totalUsed=0, totalFiles=0):
        """
        """
        self.nbDiskFilesUsedLabel.setText( "%s" % QtHelper.bytes2human(totalUsed) )
        self.nbDiskTotalFilesLabel.setText( "%s Files" % totalFiles )
        
class BackupItem(QTreeWidgetItem, Logger.ClassLogger):
    """
    Treewidget item for backup
    """
    def __init__(self, parent, backupData, backupName, backupDate, backupSize, type = QTreeWidgetItem.UserType+0, newBackup=False ):
        """
        Constructs BackupItem widget item

        @param parent: 
        @type parent:

        @param backupData: 
        @type backupData:

        @param backupName: 
        @type backupName:

        @param backupDate: 
        @type backupDate:

        @param backupSize: 
        @type backupSize:

        @param type: 
        @type type:

        @param newBackup: 
        @type newBackup: boolean
        """
        QTreeWidgetItem.__init__(self, parent, type)
        self.parent = parent
        self.itemData = backupData # real archive name on the server
        if newBackup:
            self.setIcon(COL_NAME, QIcon(":/file-zip-new.png") )
            self.setColor()
        else:
            self.setIcon(COL_NAME, QIcon(":/file-zip.png") )
        self.setText(COL_NAME, backupName )
        self.setText(COL_SIZE, QtHelper.bytes2human( int(backupSize) ) )
        self.parseDate( backupDate=backupDate )

    def parseDate(self, backupDate):
        """
        Parse the date of the backup

        @param backupDate: 
        @type backupDate:
        """
        d,t = backupDate.split('_')
        t = t.split('.')[0]
        t = t.replace('-', ':')
        self.setText(COL_DATE, "%s %s" % (d,t) )

    def setColor(self):
        """
        Change the color of new item
        """
        for i in xrange(3):
            self.setForeground( i, QBrush( QColor( Qt.blue ) ) )

class BackupTree(QTreeWidget):
    def __init__(self, parent):
        """
        """
        QTreeWidget.__init__(self, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        labels = [ self.tr("Backup Name"), self.tr("Date Creation"), self.tr("Size on disk") ]
        self.setHeaderLabels(labels)
        self.setColumnWidth(COL_NAME, 240)
        self.setColumnWidth(COL_DATE, 150 )
        
class WRepositoriesSvr(QWidget, Logger.ClassLogger):
    """
    Widget for repositories server
    """
    def __init__(self, parent = None):
        """
        Constructs WStatistics widget 

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Repositories")
        
        self.itemBackupCurrent = None
        self.projects = []
        # self.statsData = { 'trx': [], 'zip': [] }
        
        self.createWidgets()
        self.createActions()
        self.createConnections()
        self.createToolbar()
        self.deactivate()
    
    def createConnections (self):
        """
        QtWidgets connections
        """
        self.backup.customContextMenuRequested.connect(self.onPopupMenu)
        self.backupAdps.customContextMenuRequested.connect(self.onPopupMenuAdapters)
        self.backupLibAdps.customContextMenuRequested.connect(self.onPopupMenuLibraries)

        self.backup.currentItemChanged.connect(self.currentItemChanged)
        self.backupAdps.currentItemChanged.connect(self.currentItemChangedAdapters)
        self.backupLibAdps.currentItemChanged.connect(self.currentItemChangedLibraries)

        self.backup.itemDoubleClicked.connect(self.onDoubleClicked)
        self.backupAdps.itemDoubleClicked.connect(self.onDoubleClickedAdapters)
        self.backupLibAdps.itemDoubleClicked.connect(self.onDoubleClickedLibraries)

        self.backupArchives.customContextMenuRequested.connect(self.onPopupMenuBackupArchives)
        self.backupArchives.currentItemChanged.connect(self.currentItemChangedBackupArchives)
        self.backupArchives.itemDoubleClicked.connect(self.onBackupArchivesDoubleClicked)
        
    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbarAdapters = QToolBar(self)
        self.dockToolbarLibraries = QToolBar(self)

        # left widgets definition
        self.testsRepoBox = QGroupBox("Tests Repository")
        testsLayout =  QVBoxLayout()

        self.diskUsageBox = DiskStats(parent=self, boxName='Disk Usage')
        self.numberFilesBox = RepoStats(parent=self, boxName='Repository Usage')
        self.taFileBox = FileStats(parent=self, boxName='TestAbstract File')
        self.tuFileBox = FileStats(parent=self, boxName='TestUnit File')
        self.tpFileBox = FileStats(parent=self, boxName='TestPlan File')
        self.tsFileBox = FileStats(parent=self, boxName='TestSuite File')
        self.tcFileBox = FileStats(parent=self, boxName='TestConfig File')
        self.tdFileBox = FileStats(parent=self, boxName='TestData File')
        self.pngFileBox = FileStats(parent=self, boxName='Image File')
        self.tgxFileBox = FileStats(parent=self, boxName='TestGlobal File')

        self.statsTestBox = QFrame(self)
        layoutGrid = QGridLayout()
        layoutGrid.addWidget(self.tsFileBox, 0, 0)
        layoutGrid.addWidget(self.tuFileBox, 0, 1)
        layoutGrid.addWidget(self.taFileBox, 0, 2)
        layoutGrid.addWidget(self.tgxFileBox, 0, 3)
        
        layoutGrid.addWidget(self.tpFileBox, 1, 0)
        layoutGrid.addWidget(self.tcFileBox, 1, 1)
        layoutGrid.addWidget(self.tdFileBox, 1, 2)
        layoutGrid.addWidget(self.pngFileBox, 1, 3)
        
        layoutGrid.addWidget(self.numberFilesBox, 2, 0)
        layoutGrid.addWidget(self.diskUsageBox, 2, 1)
        
        self.statsTestBox.setLayout( layoutGrid )

        self.backup = BackupTree(self)

        self.statsTestsTab = QTabWidget()
        self.statsTestsTab.addTab( self.statsTestBox, "Statistics" )
        self.statsTestsTab.addTab( self.backup, "Backups" )
        
        self.prjTestsComboBox = QComboBox(self) 
        self.prjTestsComboBox.setMaximumWidth(250)
        subLayout = QHBoxLayout()
        subLayout.addWidget( self.prjTestsComboBox )
        subLayout.addWidget( self.dockToolbar )

        testsLayout.addLayout( subLayout )
        testsLayout.addWidget( self.statsTestsTab )
        self.testsRepoBox.setLayout(testsLayout)

        # right widgets definition
        self.adaptersRepoBox = QGroupBox("Sut Adapters Repository")
        adaptersLayout =  QVBoxLayout()

        self.diskUsageAdaptersBox = DiskStats(parent=self, boxName='Disk Usage')
        self.repoUsageAdaptersBox = RepoStats(parent=self, boxName='Repository Usage')
        self.pyAdpFileBox = FileStats(parent=self, boxName='Adapter File')

        layoutAdpGrid = QGridLayout()
        layoutAdpGrid.addWidget(self.diskUsageAdaptersBox, 0, 0)
        layoutAdpGrid.addWidget(self.repoUsageAdaptersBox, 0, 1)
        layoutAdpGrid.addWidget(self.pyAdpFileBox, 0, 2)
        
        self.backupAdps =  BackupTree(self)


        adaptersLayout.addWidget( self.dockToolbarAdapters )
        adaptersLayout.addLayout( layoutAdpGrid )
        adaptersLayout.addWidget( self.backupAdps )
        self.adaptersRepoBox.setLayout(adaptersLayout)
        
        # right widgets definition
        self.librariesRepoBox = QGroupBox("Sut Libraries Repository")
        librariesLayout =  QVBoxLayout()
        
        self.diskUsageLibrairiesBox = DiskStats(parent=self, boxName='Disk Usage')
        self.repoUsageLibrairiesBox = RepoStats(parent=self, boxName='Repository Usage')
        self.pyLibFileBox = FileStats(parent=self, boxName='Library File')

        layoutLibAdpGrid = QGridLayout()
        layoutLibAdpGrid.addWidget(self.diskUsageLibrairiesBox, 0, 0)
        layoutLibAdpGrid.addWidget(self.repoUsageLibrairiesBox, 0, 1)
        layoutLibAdpGrid.addWidget(self.pyLibFileBox, 0, 2)
        
        self.backupLibAdps =  BackupTree(self)

        librariesLayout.addWidget( self.dockToolbarLibraries )
        librariesLayout.addLayout( layoutLibAdpGrid )
        librariesLayout.addWidget( self.backupLibAdps )
        self.librariesRepoBox.setLayout(librariesLayout)

        # new in v11.3
        self.repoUsageArchivesBox = RepoStats(parent=self, boxName='Repository Usage')
        self.diskUsageArchivesBox = DiskStats(parent=self, boxName='Disk Usage')
        self.trFileBox = FileStats(parent=self, boxName='TestResult File')
        self.zipFileBox = FileStats(parent=self, boxName='Zip File')
        self.pngArchFileBox = FileStats(parent=self, boxName='Image File')

        
        layoutGrid = QGridLayout()
        layoutGrid.addWidget(self.diskUsageArchivesBox, 0, 0)
        layoutGrid.addWidget(self.repoUsageArchivesBox, 0, 1)
        layoutGrid.addWidget(self.trFileBox, 0, 2)
        layoutGrid.addWidget(self.zipFileBox, 1, 1)
        layoutGrid.addWidget(self.pngArchFileBox, 1, 0)
        
        
        self.dockToolbarArchives = QToolBar(self)
        
        self.archivesRepoBox = QGroupBox("Results Repository")
        
        self.backupArchives =  BackupTree(self)
        
        layoutArchives = QVBoxLayout()
        
        self.prjArchivesComboBox = QComboBox(self) 
        self.prjArchivesComboBox.setMaximumWidth(250)
        sub2Layout = QHBoxLayout()
        sub2Layout.addWidget( self.prjArchivesComboBox )
        sub2Layout.addWidget( self.dockToolbarArchives )
        
        layoutArchives.addLayout( sub2Layout )
        layoutArchives.addLayout( layoutGrid )
        layoutArchives.addWidget( self.backupArchives )
        self.archivesRepoBox.setLayout(layoutArchives)

        self.statsTab = QTabWidget()
        
        self.devBox = QFrame(self)
        devLayout =  QHBoxLayout()
        devLayout.addWidget(self.adaptersRepoBox)
        devLayout.addWidget(self.librariesRepoBox)
        self.devBox.setLayout(devLayout)
        
        self.testBox = QFrame(self)
        testLayout =  QHBoxLayout()
        testLayout.addWidget(self.testsRepoBox)
        testLayout.addWidget(self.archivesRepoBox)
        self.testBox.setLayout(testLayout)

        self.statsTab.addTab(self.testBox, "Tests Repositories")
        self.statsTab.addTab(self.devBox, "Modules Repositories")
        
        layoutFinal = QHBoxLayout()
        layoutFinal.addWidget(self.statsTab)
        
        self.setLayout(layoutFinal)

    def createActions (self):
        """
        Actions defined:
         * remove all tests from repository
         * refresh statistics
         * backup tests
         * delete all backups
         * export one backup
         * uninstall adapters
         * refresh adapters statistics
         * backup adapters
         * delete all adapters backups
         * export one adapter backup
         * uninstall libraries
         * refresh libraries statistic
         * backup libraries
         * delete all libraries backups
         * export one library backup
        """
        # tests repository actions
        self.emptyAction = QtHelper.createAction(self, "&Empty", self.emptyTests, tip = 'Removes all tests', 
                                            icon = QIcon(":/trash.png") )
        self.refreshAction = QtHelper.createAction(self, "&Refresh", self.refreshStats, tip = 'Refresh statistics', 
                                            icon = QIcon(":/act-refresh.png") )
        self.backupAction = QtHelper.createAction(self, "&Create Backup", self.backupTests, tip = 'Backup tests', 
                                            icon = QIcon(":/file-zip.png") )
        self.deleteAllBackupsAction = QtHelper.createAction(self, "&Delete all backups", self.deleteAllBackupsTests, 
                                            tip = 'Delete all backups', icon = QIcon(":/file-zip-del-all.png") )
        self.exportBackupAction = QtHelper.createAction(self, "&Export", self.exportBackup, tip = 'Export the selected backup', 
                                            icon = QIcon(":/file-zip-save.png"))
        self.unlockTestsAction = QtHelper.createAction(self, "&Unlock", self.unlockTests, tip = 'Unlock all files', 
                                            icon = QIcon(":/unlock.png"))

        # adapters repository actions
        self.uninstallAdaptersAction = QtHelper.createAction(self, "&Uninstall", self.uninstallAdapters, tip = 'Uninstall adapters', 
                                            icon = QIcon(":/adapters-del.png") )
        self.refreshAdaptersAction = QtHelper.createAction(self, "&Refresh", self.refreshAdaptersStats, tip = 'Refresh statistics', 
                                            icon = QIcon(":/act-refresh.png") )
        self.backupAdaptersAction = QtHelper.createAction(self, "&Create Backup", self.backupAdapters, tip = 'Backup adapters', 
                                            icon = QIcon(":/file-zip.png") )
        self.deleteAllBackupsAdaptersAction = QtHelper.createAction(self, "&Delete all backups", self.deleteAllBackupsAdapters, 
                                            tip = 'Delete all backups', icon = QIcon(":/file-zip-del-all.png") )
        self.exportBackupAdapterAction = QtHelper.createAction(self, "&Export", self.exportBackupAdapter, tip = 'Export the selected backup', 
                                            icon = QIcon(":/file-zip-save.png"))
        self.unlockAdaptersAction = QtHelper.createAction(self, "&Unlock", self.unlockAdapters, tip = 'Unlock all files', 
                                            icon = QIcon(":/unlock.png"))
                                            
        # libraries repository actions
        self.uninstallLibrariesAction = QtHelper.createAction(self, "&Uninstall", self.uninstallLibraries, tip = 'Uninstall libraries', 
                                            icon = QIcon(":/libraries-del.png") )
        self.refreshLibrariesAction = QtHelper.createAction(self, "&Refresh", self.refreshLibrariesStats, tip = 'Refresh statistics', 
                                            icon = QIcon(":/act-refresh.png") )
        self.backupLibrariesAction = QtHelper.createAction(self, "&Create Backup", self.backupLibraries, tip = 'Backup libraries', 
                                            icon = QIcon(":/file-zip.png") )
        self.deleteAllBackupsLibrariesAction = QtHelper.createAction(self, "&Delete all backups", self.deleteAllBackupsLibraries, 
                                            tip = 'Delete all backups', icon = QIcon(":/file-zip-del-all.png") )
        self.exportBackupLibraryAction = QtHelper.createAction(self, "&Export", self.exportBackupLibrary, tip = 'Export the selected backup', 
                                            icon = QIcon(":/file-zip-save.png"))
        self.unlockLibrariesAction = QtHelper.createAction(self, "&Unlock", self.unlockLibraries, tip = 'Unlock all files', 
                                            icon = QIcon(":/unlock.png"))
                                            
        # backups archive sactions
        self.backupArchivesAction = QtHelper.createAction(self, "&Create Backup", self.backupAllArchives, 
                                                            tip = 'Create a complete backup of all archives', 
                                                            icon = QIcon(":/file-zip.png") )
        self.deleteAllBackupsArchivesAction = QtHelper.createAction(self, "&Delete Backups", self.deleteAllBackupsArchives, 
                                                            tip = 'Delete all backups', 
                                                            icon = QIcon(":/file-zip-del-all.png") )
        self.exportBackupArchivesAction = QtHelper.createAction(self, "&Export", self.exportBackupArchives, 
                                                            tip = 'Export the selected backup', 
                                                            icon = QIcon(":/file-zip-save.png"))
        # self.refreshArchivesAction = QtHelper.createAction(self, "&Refresh", self.refreshArchivesStats, 
                                                            # tip = 'Partail refresh of the statistics', 
                                                            # icon = QIcon(":/act-half-refresh.png") )
        self.refreshFullArchivesAction = QtHelper.createAction(self, "&Refresh Full", 
                                                                self.refreshAllArchivesStats, tip = 'Refresh all statistics', 
                                                                icon = QIcon(":/act-refresh.png") )

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-------||
        || Empty ||
        ||-------||
        """
        self.dockToolbar.setObjectName("Tests Repository toolbar")
        self.dockToolbar.addAction(self.refreshAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.emptyAction)
        self.dockToolbar.addAction(self.unlockTestsAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.backupAction)
        self.dockToolbar.addAction(self.deleteAllBackupsAction)
        self.dockToolbar.addAction(self.exportBackupAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

        self.dockToolbarAdapters.setObjectName("Adapters Repository toolbar")
        self.dockToolbarAdapters.addAction(self.refreshAdaptersAction)
        self.dockToolbarAdapters.addSeparator()
        self.dockToolbarAdapters.addAction(self.unlockAdaptersAction)
        self.dockToolbarAdapters.addAction(self.uninstallAdaptersAction)
        self.dockToolbarAdapters.addSeparator()
        self.dockToolbarAdapters.addAction(self.backupAdaptersAction)
        self.dockToolbarAdapters.addAction(self.deleteAllBackupsAdaptersAction)
        self.dockToolbarAdapters.addAction(self.exportBackupAdapterAction)
        self.dockToolbarAdapters.addSeparator()
        self.dockToolbarAdapters.setIconSize(QSize(16, 16))

        self.dockToolbarLibraries.setObjectName("Libraries Repository toolbar")
        self.dockToolbarLibraries.addAction(self.refreshLibrariesAction)
        self.dockToolbarLibraries.addSeparator()
        self.dockToolbarLibraries.addAction(self.unlockLibrariesAction)
        self.dockToolbarLibraries.addAction(self.uninstallLibrariesAction)
        self.dockToolbarLibraries.addSeparator()
        self.dockToolbarLibraries.addAction(self.backupLibrariesAction)
        self.dockToolbarLibraries.addAction(self.deleteAllBackupsLibrariesAction)
        self.dockToolbarLibraries.addAction(self.exportBackupLibraryAction)
        self.dockToolbarLibraries.addSeparator()
        self.dockToolbarLibraries.setIconSize(QSize(16, 16))
        
        self.dockToolbarArchives.setObjectName("Archives backup toolbar")
        # self.dockToolbarArchives.addAction(self.refreshArchivesAction)
        self.dockToolbarArchives.addAction(self.refreshFullArchivesAction)
        self.dockToolbarArchives.addSeparator()
        self.dockToolbarArchives.addAction(self.backupArchivesAction)
        self.dockToolbarArchives.addAction(self.deleteAllBackupsArchivesAction)
        self.dockToolbarArchives.addAction(self.exportBackupArchivesAction)
        self.dockToolbarArchives.setIconSize(QSize(16, 16))
        
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
            self.error( 'project not found : %s' % project )
        return pid

    def initializeProjects(self, projects=[], defaultProject=1):
        """
        Create the root item and load all subs items

        @param listing: 
        @type listing: list
        """
        self.projects = projects
        
        self.prjTestsComboBox.clear()
        self.prjArchivesComboBox.clear()
        
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
        
        # insert data
        pname = ''
        for p in projects:
            self.prjTestsComboBox.addItem ( p['name']  )
            self.prjArchivesComboBox.addItem ( p['name']  )
            if defaultProject == p['project_id']:
                pname = p['name']
        self.prjTestsComboBox.insertSeparator(1)
        
        for i in xrange(self.prjArchivesComboBox.count()):
            item_text = self.prjArchivesComboBox.itemText(i)
            if str(pname) == str(item_text):
                self.prjArchivesComboBox.setCurrentIndex(i)

        for i in xrange(self.prjTestsComboBox.count()):
            item_text = self.prjTestsComboBox.itemText(i)
            if str(pname) == str(item_text):
                self.prjTestsComboBox.setCurrentIndex(i)

    def cleanStatsArchives(self):
        """
        Clean all statistics
        """
        pass

    def onBackupArchivesDoubleClicked (self, backup):
        """
        Open result logs on double click

        @param backup: 
        @type backup:
        """
        self.exportBackupArchives()
        
    def onPopupMenuBackupArchives(self, pos):
        """
        Display menu on right click for backup tree view

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.backupArchives.itemAt(pos)
        if item:
            self.itemCurrent = item
            self.menu.addAction( "Export...", self.exportBackupArchives)
            self.menu.popup(self.backupArchives.mapToGlobal(pos))
            
    def currentItemChangedBackupArchives(self, currentItem, previousItem):
        """
        On current item changed in backup list

        @param currentItem: 
        @type currentItem:

        @param previousItem: 
        @type previousItem:
        """
        if currentItem is not None:
            self.itemBackupCurrent = currentItem
            if currentItem.type() ==  QTreeWidgetItem.UserType+0:
                self.exportBackupArchivesAction.setEnabled(True)
            else:
                self.exportBackupArchivesAction.setEnabled(False)
                
    def newBackupArchives(self, data ):
        """
        Add a new backup on the backup tree view
        Notify received on tcp channel

        @param data: 
        @type data:
        """
        if 'repo-archives' in data:
            backup = data['repo-archives']['backup']
            item = BackupItem(  parent = self.backupArchives, backupData=backup['fullname'], backupName=backup['name'],
                                backupDate=backup['date'], backupSize=backup['size'], newBackup=True )
            self.backupArchives.sortItems(COL_DATE, Qt.DescendingOrder)
            self.deleteAllBackupsArchivesAction.setEnabled(True)
        else:
            self.error( 'dest repo unknown: %s' % str(data) )

    def exportBackupArchives(self):
        """
        Download the backup from the server
        """
        if self.itemBackupCurrent is None:
            self.exportBackupArchivesAction.setEnabled(False)
            return 
        
        backupFileName = self.itemBackupCurrent.itemData # archive name
        extension = self.tr("All Files (*.*)")
        destfileName = QFileDialog.getSaveFileName(self, self.tr("Export backup"), 
                                                   backupFileName, extension )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = destfileName
        else:
            _fileName = destfileName
        # end of new
        
        if _fileName:
            RCI.instance().downloadBackupsResults(backupName=backupFileName,
                                                destName="%s" % _fileName )
            
    def deleteAllBackupsArchives(self):
        """
        Delete all archives backups on the server
        """
        reply = QMessageBox.question(self, "Delete all backups", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().removeBackupsResults()
            
    def backupAllArchives(self):
        """
        Create backup on server
        """
        reply = QMessageBox.question(self, "Backups all test results", 
                                    "A lot of data can be present in this storage!\nAre you really sure?",
                                    QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            txt, ok = QInputDialog.getText(self, "Create backup", 
                                           "Please to enter the name of the backup file:", QLineEdit.Normal)
            if ok and txt:
                try:
                    backupName = str(txt)
                    # workaround to detect special characters, same limitation as with python2 because of the server
                    # this limitation will be removed when the server side will be ported to python3
                    if sys.version_info > (3,): # python3 support only 
                        backupName.encode("ascii") 
                
                    RCI.instance().backupResults(backupName=backupName)
                except UnicodeEncodeError as e:
                    self.error(e)
                    QMessageBox.warning(self, "Backups" , 
                                        "Bad backup name!\nPerhaps one day, but not today, sorry for this limitation.")

    def unlockTests(self):
        """
        Unlock all tests files
        """
        reply = QMessageBox.question(self, "Unlock all files", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().unlockTests()
            
    def unlockAdapters(self):
        """
        Unlock all adapters files
        """
        reply = QMessageBox.question(self, "Unlock all files", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().unlockAdapters()
            
    def unlockLibraries(self):
        """
        Unlock all libraries files
        """
        reply = QMessageBox.question(self, "Unlock all files", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().unlockLibraries()
            
    def currentItemChanged(self, currentItem, previousItem):
        """
        Called on current item changed for backup tests treeview 

        @param currentItem: 
        @type currentItem:

        @param previousItem: 
        @type previousItem:
        """
        if currentItem is not None:
            self.itemCurrent = currentItem
            if currentItem.type() ==  QTreeWidgetItem.UserType+0:
                self.exportBackupAction.setEnabled(True)
            else:
                self.exportBackupAction.setEnabled(False)

    def currentItemChangedAdapters(self, currentItem, previousItem):
        """
        Called on current item changed for backup adapters treeview 

        @param currentItem: 
        @type currentItem:

        @param previousItem: 
        @type previousItem:
        """
        if currentItem is not None:
            self.itemCurrent = currentItem
            if currentItem.type() ==  QTreeWidgetItem.UserType+0:
                self.exportBackupAdapterAction.setEnabled(True)
            else:
                self.exportBackupAdapterAction.setEnabled(False)

    def currentItemChangedLibraries(self, currentItem, previousItem):
        """
        Called on current item changed for backup libraries treeview 

        @param currentItem: 
        @type currentItem:

        @param previousItem: 
        @type previousItem:
        """
        if currentItem is not None:
            self.itemCurrent = currentItem
            if currentItem.type() ==  QTreeWidgetItem.UserType+0:
                self.exportBackupLibraryAction.setEnabled(True)
            else:
                self.exportBackupLibraryAction.setEnabled(False)

    def onDoubleClicked (self, backup):
        """
        Open result logs on double click

        @param backup: 
        @type backup:
        """
        self.exportBackup()

    def onDoubleClickedAdapters (self, backup):
        """
        Open result logs on double click

        @param backup: 
        @type backup:
        """
        self.exportBackupAdapter()

    def onDoubleClickedLibraries (self, backup):
        """
        Open result logs on double click

        @param backup: 
        @type backup:
        """
        self.exportBackupLibrary()

    def onPopupMenu(self, pos):
        """
        Display menu on right click for backup list

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.backup.itemAt(pos)
        if item:
            self.itemCurrent = item
            self.menu.addAction( "Export...", self.exportBackup)
            self.menu.popup(self.backup.mapToGlobal(pos))

    def onPopupMenuAdapters(self, pos):
        """
        Display menu on right click for backup adapters list

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.backupAdps.itemAt(pos)
        if item:
            self.itemCurrent = item
            self.menu.addAction( "Export...", self.exportBackupAdapter)
            self.menu.popup(self.backupAdps.mapToGlobal(pos))

    def onPopupMenuLibraries(self, pos):
        """
        Display menu on right click for backup adapters list

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.backupLibAdps.itemAt(pos)
        if item:
            self.itemCurrent = item
            self.menu.addAction( "Export...", self.exportBackupLibrary)
            self.menu.popup(self.backupLibAdps.mapToGlobal(pos))

    def exportBackup(self):
        """
        Download backup test from server
        """
        if self.itemCurrent is None:
            self.exportBackupAction.setEnabled(False)
            return 

        backupFileName = self.itemCurrent.itemData # archive name
        extension = self.tr("All Files (*.*)")
    
        destfileName = QFileDialog.getSaveFileName(self, self.tr("Export backup"), backupFileName, extension )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = destfileName
        else:
            _fileName = destfileName
        # end of new
        
        if _fileName:
            RCI.instance().downloadBackupsTests(backupName=backupFileName,
                                                destName="%s" % _fileName )
    
    def exportBackupAdapter(self):
        """
        Download backup adapter from server
        """
        if self.itemCurrent is None:
            self.exportBackupAdaptersAction.setEnabled(False)
            return 

        backupFileName = self.itemCurrent.itemData # archive name
        extension = self.tr("All Files (*.*)")
    
        destfileName = QFileDialog.getSaveFileName(self, self.tr("Export backup"), backupFileName, extension )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = destfileName
        else:
            _fileName = destfileName
        # end of new
        
        if _fileName:
            RCI.instance().downloadBackupsAdapters(backupName=backupFileName,
                                                destName="%s" % _fileName )
    
    def exportBackupLibrary(self):
        """
        Download backup library from server
        """
        if self.itemCurrent is None:
            self.exportBackupLibrariesAction.setEnabled(False)
            return 

        backupFileName = self.itemCurrent.itemData # archive name
        extension = self.tr("All Files (*.*)")
    
        destfileName = QFileDialog.getSaveFileName(self, self.tr("Export backup"), backupFileName, extension )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = destfileName
        else:
            _fileName = destfileName
        # end of new
        
        if _fileName:
            RCI.instance().downloadBackupsLibraries(backupName=backupFileName,
                                                destName="%s" % _fileName )
    
    def deleteAllBackupsTests(self):
        """
        Delete all backups tests on the server
        """
        reply = QMessageBox.question(self, "Delete all tests backups", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().removeBackupsTests()
            
    def deleteAllBackupsAdapters(self):
        """
        Delete all backups adapters on the server
        """
        reply = QMessageBox.question(self, "Delete all adapters backups", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().removeBackupsAdapters()
            
    def deleteAllBackupsLibraries(self):
        """
        Delete all backups adapters on the server
        """
        reply = QMessageBox.question(self, "Delete all libraries backups", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().removeBackupsLibraries()
            
    def backupTests(self):
        """
        Create backup on server
        """
        txt, ok = QInputDialog.getText(self, "Create tests backup", 
                                       "Please to enter the name of the backup file:", QLineEdit.Normal)
        if ok and txt:
            try:
                backupName = str(txt)
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    backupName.encode("ascii") 

                RCI.instance().backupTests(backupName=backupName)
            except UnicodeEncodeError as e:
                self.error(e)
                QMessageBox.warning(self, "Backups" , 
                                    "Bad backup name!\nPerhaps one day, but not today, sorry for this limitation.")

    def backupAdapters(self):
        """
        Create backup on server
        """
        txt, ok = QInputDialog.getText(self, "Create adapters backup", 
                                       "Please to enter the name of the backup file:", QLineEdit.Normal)
        if ok and txt:
            try:
                backupName = str(txt)
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    backupName.encode("ascii") 

                RCI.instance().backupAdapters(backupName=backupName)
            except UnicodeEncodeError as e:
                self.error(e)
                QMessageBox.warning(self, "Backups" , 
                                    "Bad backup name!\nPerhaps one day, but not today, sorry for this limitation.")

    def backupLibraries(self):
        """
        Create backup on server
        """
        txt, ok = QInputDialog.getText(self, "Create libraries backup", 
                                       "Please to enter the name of the backup file:", QLineEdit.Normal)
        if ok and txt:
            try:
                backupName = str(txt)
                # workaround to detect special characters, same limitation as with python2 because of the server
                # this limitation will be removed when the server side will be ported to python3
                if sys.version_info > (3,): # python3 support only 
                    backupName.encode("ascii") 

                RCI.instance().backupLibraries(backupName=backupName)
            except UnicodeEncodeError as e:
                self.error(e)
                QMessageBox.warning(self, "Backups" , 
                                    "Bad backup name!\nPerhaps one day, but not today, sorry for this limitation.")

    def refreshStats(self):
        """
        Refresh statistics
        """
        projectName = self.prjTestsComboBox.currentText()
        projectId = self.getProjectId(project="%s" % projectName)
        
        RCI.instance().statisticsTests(projectId=projectId)
        
    def refreshAdaptersStats(self):
        """
        Refresh statistics for adapters
        """
        RCI.instance().statisticsAdapters()
        
    def refreshLibrariesStats(self):
        """
        Refresh statistics for libraries
        """
        RCI.instance().statisticsLibraries()

    def refreshAllArchivesStats(self):
        """
        Refresh statistics for archives
        """
        projectName = self.prjArchivesComboBox.currentText()
        projectId = self.getProjectId(project="%s" % projectName)
        
        RCI.instance().statisticsResults(projectId=projectId)
        
    def newBackup(self, data ):
        """
        Notify received on tcp channel
        Add backup on the treeview test or adapters

        @param data: 
        @type data:
        """
        if 'repo-tests' in data:
            backup = data['repo-tests']['backup']
            item = BackupItem(  parent = self.backup, backupData=backup['fullname'], backupName=backup['name'], 
                                backupDate=backup['date'], backupSize=backup['size'], newBackup=True )
            self.backup.sortItems(COL_DATE, Qt.DescendingOrder)
            self.deleteAllBackupsAction.setEnabled(True)

        elif 'repo-adapters' in data:
            backup = data['repo-adapters']['backup']
            item = BackupItem(  parent = self.backupAdps, backupData=backup['fullname'], backupName=backup['name'],
                                backupDate=backup['date'], backupSize=backup['size'], newBackup=True )
            self.backupAdps.sortItems(COL_DATE, Qt.DescendingOrder)
            self.deleteAllBackupsAdaptersAction.setEnabled(True)

        elif 'repo-libraries' in data:
            backup = data['repo-libraries']['backup']
            item = BackupItem(  parent = self.backupLibAdps, backupData=backup['fullname'], backupName=backup['name'],
                                backupDate=backup['date'], backupSize=backup['size'], newBackup=True )
            self.backupLibAdps.sortItems(COL_DATE, Qt.DescendingOrder)
            self.deleteAllBackupsLibrariesAction.setEnabled(True)
        else:
            self.error( 'dest repo unknown: %s' % str(data) )

    def loadData (self, data, backups=[]):
        """
        Load statistics and backups list for tests

        @param data: 
        @type data:

        @param backups: 
        @type backups:
        """
        # clear the backups treeview
        if len(backups):
            self.backup.clear()

        totalFiles = 0
        totalUsed = 0
        
        if 'tax' in data: 
            totalFiles += data['tax']['nb']
            totalUsed += data['tax']['total']
            self.taFileBox.loadStats(data=data['tax'])
        
        if 'tux' in data: 
            totalFiles += data['tux']['nb']
            totalUsed += data['tux']['total']
            self.tuFileBox.loadStats(data=data['tux'])
        
        if 'tsx' in data: 
            totalFiles += data['tsx']['nb']
            totalUsed += data['tsx']['total']
            self.tsFileBox.loadStats(data=data['tsx'])
        
        if 'tpx' in data: 
            totalFiles += data['tpx']['nb']
            totalUsed += data['tpx']['total']
            self.tpFileBox.loadStats(data=data['tpx'])
        
        if 'tgx' in data: 
            totalFiles += data['tgx']['nb']
            totalUsed += data['tgx']['total']
            self.tgxFileBox.loadStats(data=data['tgx'])
        
        if 'tcx' in data: 
            totalFiles += data['tcx']['nb']
            totalUsed += data['tcx']['total']
            self.tcFileBox.loadStats(data=data['tcx'])
        
        if 'tdx' in data: 
            totalFiles += data['tdx']['nb']
            totalUsed += data['tdx']['total']
            self.tdFileBox.loadStats(data=data['tdx'])
        
        if 'png' in data: 
            totalFiles += data['png']['nb']
            totalUsed += data['png']['total']
            self.pngFileBox.loadStats(data=data['png'])
            
        if 'disk-usage' in data: 
            self.diskUsageBox.loadStats(data=data['disk-usage'])
            self.numberFilesBox.loadStats(totalUsed=totalUsed,totalFiles=totalFiles)

        # load tests archives list
        try:
            for backup in  backups:
                #{'type': 'file', 'name': 'backuptests_lplm_2012-05-27_17-45-27.283.zip', 'size': '19415'}
                # backuptests1_testv3.1.0_final_2012-07-09_06-33-18.716.zip
                if backup['type'] == 'file':
                    backuptag, rightover = backup['name'].split('_', 1)
                    leftover, backuptime = rightover.rsplit('_', 1)
                    backupname, backupdate = leftover.rsplit('_', 1)
                    backupDate = "%s_%s" % ( backupdate, backuptime )
                    item = BackupItem(  parent = self.backup, backupData=backup['name'], 
                                        backupName=backupname, backupDate=backupDate, 
                                        backupSize=backup['size'], newBackup=False )
            if len(backups) > 0:
                self.deleteAllBackupsAction.setEnabled(True)
        except Exception as e:            
            self.error( e )
        self.backup.sortItems(COL_DATE, Qt.DescendingOrder)

    def loadDataAdapters (self, data, backups=[]):
        """
        Load statistics and backups list for adapters

        @param data: 
        @type data:

        @param backups: 
        @type backups:
        """
        # clear the backups treeview
        if len(backups):
            self.backupAdps.clear()

        totalFiles = 0
        totalUsed = 0
        
        if 'py' in data: 
            totalFiles += data['py']['nb']
            totalUsed += data['py']['total']
            self.pyAdpFileBox.loadStats(data=data['py'])

        if 'disk-usage' in data: 
            self.diskUsageAdaptersBox.loadStats(data=data['disk-usage'])
            self.repoUsageAdaptersBox.loadStats(totalUsed=totalUsed,totalFiles=totalFiles)

        # load tests archives list
        try:
            for backup in  backups:
                #{'type': 'file', 'name': 'backuptests_lplm_2012-05-27_17-45-27.283.zip', 'size': '19415'}
                if backup['type'] == 'file':
                    backuptag, rightover = backup['name'].split('_', 1)
                    leftover, backuptime = rightover.rsplit('_', 1)
                    backupname, backupdate = leftover.rsplit('_', 1)
                    backupDate = "%s_%s" % ( backupdate, backuptime )
                    item = BackupItem(  parent = self.backupAdps, backupData=backup['name'], 
                                        backupName=backupname,  backupDate=backupDate, 
                                        backupSize=backup['size'], newBackup=False )
            
            if len(backups) > 0:
                self.deleteAllBackupsAdaptersAction.setEnabled(True)
        except Exception as e:            
            self.error( e )
        self.backupAdps.sortItems(COL_DATE, Qt.DescendingOrder)

    def loadDataLibraries (self, data, backups=[]):
        """
        Load statistics and backups list for adapters

        @param data: 
        @type data:

        @param backups: 
        @type backups:
        """
        # clear the backups treeview
        if len(backups):
            self.backupLibAdps.clear()

        totalFiles = 0
        totalUsed = 0
        
        if 'py' in data: 
            totalFiles += data['py']['nb']
            totalUsed += data['py']['total']
            self.pyLibFileBox.loadStats(data=data['py'])

        if 'disk-usage' in data: 
            self.diskUsageLibrairiesBox.loadStats(data=data['disk-usage'])
            self.repoUsageLibrairiesBox.loadStats(totalUsed=totalUsed,totalFiles=totalFiles)

        # load tests archives list
        try:
            for backup in  backups:
                #{'type': 'file', 'name': 'backuptests_lplm_2012-05-27_17-45-27.283.zip', 'size': '19415'}
                if backup['type'] == 'file':
                    backuptag, rightover = backup['name'].split('_', 1)
                    leftover, backuptime = rightover.rsplit('_', 1)
                    backupname, backupdate = leftover.rsplit('_', 1)
                    backupDate = "%s_%s" % ( backupdate, backuptime )
                    item = BackupItem(  parent = self.backupLibAdps, backupData=backup['name'], 
                                        backupName=backupname, backupDate=backupDate, 
                                        backupSize=backup['size'], newBackup=False )
            
            if len(backups) > 0:
                self.deleteAllBackupsLibrariesAction.setEnabled(True)
        except Exception as e:            
            self.error( e )
        self.backupLibAdps.sortItems(COL_DATE, Qt.DescendingOrder)
        
    def loadDataArchives(self, data, backups=[]):
        """
        Load backups on treeview 

        @param backups: 
        @type backups:
        """
        # clear the backups treeview
        if len(backups):
            self.backupArchives.clear()

        totalFiles = 0
        totalUsed = 0

        if 'trx' in data: 
            totalFiles += data['trx']['nb']
            totalUsed += data['trx']['total']
            self.trFileBox.loadStats(data=data['trx'])

        if 'zip' in data: 
            totalFiles += data['zip']['nb']
            totalUsed += data['zip']['total']
            self.zipFileBox.loadStats(data=data['zip'])

        if 'png' in data: 
            totalFiles += data['png']['nb']
            totalUsed += data['png']['total']
            self.pngArchFileBox.loadStats(data=data['png'])

        if 'disk-usage' in data: 
            self.diskUsageArchivesBox.loadStats(data=data['disk-usage'])
            self.repoUsageArchivesBox.loadStats(totalUsed=totalUsed,totalFiles=totalFiles)

        # load tests archives list
        try:
            for backup in  backups:
                #{'type': 'file', 'name': 'backuparchives_lplm_2012-05-27_17-45-27.283.zip', 'size': '19415'}
                # backuptests1_testv3.1.0_final_2012-07-09_06-33-18.716.zip
                backuptag, rightover = backup['name'].split('_', 1)
                leftover, backuptime = rightover.rsplit('_', 1)
                backupname, backupdate = leftover.rsplit('_', 1)
                backupDate = "%s_%s" % ( backupdate, backuptime )
                item = BackupItem(  parent = self.backupArchives, backupData=backup['name'], 
                                    backupName=backupname, backupDate=backupDate, 
                                    backupSize=backup['size'], newBackup=False )
            if len(backups) > 0:
                self.deleteAllBackupsArchivesAction.setEnabled(True)
        except Exception as e:            
            self.error( e )
        self.backupArchives.sortItems(COL_DATE, Qt.DescendingOrder)
        
    def active (self):
        """
        Enables QTreeWidget
        """

        self.testsRepoBox.setEnabled(True)
        self.adaptersRepoBox.setEnabled(True)
        self.librariesRepoBox.setEnabled(True)
        self.archivesRepoBox.setEnabled(True)

        self.backupAdps.setEnabled(True)
        self.backupLibAdps.setEnabled(True)
        self.backup.setEnabled(True)
        self.backupArchives.setEnabled(True)

        self.refreshAction.setEnabled(True)
        self.backupAction.setEnabled(True)
        self.refreshAdaptersAction.setEnabled(True)
        self.backupAdaptersAction.setEnabled(True)

        self.refreshLibrariesAction.setEnabled(True)
        self.backupLibrariesAction.setEnabled(True)

        # new in v11.3
        self.backupArchives.setEnabled(True)
        self.backupArchivesAction.setEnabled(True)
        self.deleteAllBackupsArchivesAction.setEnabled(True)
        self.exportBackupArchivesAction.setEnabled(True)
        # end of new
                    
        if UCI.RIGHTS_ADMIN in RCI.instance().userRights:
            self.emptyAction.setEnabled(True)
            self.uninstallAdaptersAction.setEnabled(True)
            self.uninstallLibrariesAction.setEnabled(True)
            
            self.unlockTestsAction.setEnabled(True)
            self.unlockAdaptersAction.setEnabled(True)
            self.unlockLibrariesAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.testsRepoBox.setEnabled(False)
        self.adaptersRepoBox.setEnabled(False)
        self.librariesRepoBox.setEnabled(False)
        self.archivesRepoBox.setEnabled(False)
        
        self.backup.clear()
        self.backup.setEnabled(False)

        self.backupAdps.clear()
        self.backupAdps.setEnabled(False)

        self.backupLibAdps.clear()
        self.backupLibAdps.setEnabled(False)

        # new in v11.3
        self.backupArchives.clear()
        self.backupArchives.setEnabled(False)

        self.setDefaultActionsValues()

    def setDefaultActionsValues (self):
        """
        Set default values for qt actions
        """
        self.emptyAction.setEnabled(False)
        self.refreshAction.setEnabled(False)
        self.backupAction.setEnabled(False)

        self.refreshLibrariesAction.setEnabled(False)
        self.backupLibrariesAction.setEnabled(False)
        self.exportBackupLibraryAction.setEnabled(False)
        self.uninstallLibrariesAction.setEnabled(False)
        self.deleteAllBackupsLibrariesAction.setEnabled(False)

        self.refreshAdaptersAction.setEnabled(False)
        self.backupAdaptersAction.setEnabled(False)
        self.exportBackupAction.setEnabled(False)
        self.exportBackupAdapterAction.setEnabled(False)
        self.uninstallAdaptersAction.setEnabled(False)
        self.deleteAllBackupsAdaptersAction.setEnabled(False)
        self.deleteAllBackupsAction.setEnabled(False)
        
        self.unlockTestsAction.setEnabled(False)
        self.unlockAdaptersAction.setEnabled(False)
        self.unlockLibrariesAction.setEnabled(False)
        
        self.backupArchivesAction.setEnabled(False)
        self.deleteAllBackupsArchivesAction.setEnabled(False)
        self.exportBackupArchivesAction.setEnabled(False)
        
    def emptyTests(self):
        """
        Empty all tests on server
        """
        reply = QMessageBox.question(self, "Empty all tests", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().resetTests()
            
    def uninstallAdapters(self):
        """
        Removes all adapters on server
        """
        reply = QMessageBox.question(self, "Uninstall adapters", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().resetAdapters()
            
    def uninstallLibraries(self):
        """
        Removes all adapters on server
        """
        reply = QMessageBox.question(self, "Uninstall libraries", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().resetLibraries()
            
    def resetBackupTestsPart(self):
        """
        Reset the backup treeview tests and actions
        """
        self.backup.clear()
        self.deleteAllBackupsAction.setEnabled(False)
        self.exportBackupAction.setEnabled(False)

    def resetBackupArchivesPart(self):
        """
        Reset the backup treeview tests and actions
        """
        self.backupArchives.clear()
        self.deleteAllBackupsArchivesAction.setEnabled(False)
        self.exportBackupArchivesAction.setEnabled(False)

    def resetBackupAdpsPart(self):
        """
        Reset the backup adapters treeview and actions
        """
        self.backupAdps.clear()
        self.exportBackupAdapterAction.setEnabled(False)
        self.deleteAllBackupsAdaptersAction.setEnabled(False)

    def resetBackupLibsPart(self):
        """
        Reset the backup libraries treeview and actions
        """
        self.backupLibAdps.clear()
        self.exportBackupLibraryAction.setEnabled(False)
        self.deleteAllBackupsLibrariesAction.setEnabled(False)


RR = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return RR

def initialize (parent):
    """
    Initialize WStatistics widget
    """
    global RR
    RR = WRepositoriesSvr(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global RR
    if RR:
        RR = None