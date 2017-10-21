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
Plugin miscellaneous
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
    from PyQt4.QtGui import (QTreeWidgetItem, QWidget, QToolBar, QHBoxLayout, QVBoxLayout, 
                            QGroupBox, QLabel, QFormLayout, QFrame, QGridLayout, QTreeWidget, 
                            QIcon, QMessageBox, QColor, QAbstractItemView)
    from PyQt4.QtCore import (Qt, QRect, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon, QColor)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QWidget, QToolBar, QHBoxLayout, QVBoxLayout, 
                                QGroupBox, QLabel, QFormLayout, QFrame, QGridLayout, QTreeWidget, 
                                QMessageBox, QAbstractItemView)
    from PyQt5.QtCore import (Qt, QRect, QSize)
    
import Settings
import UserClientInterface as UCI
from Libs import QtHelper, Logger


try:
    xrange
except NameError: # support python3
    xrange = range
    
class ParamItem(QTreeWidgetItem):
    """
    Treewidget item for parameter
    """
    def __init__(self, param, parent = None):
        """
        Constructs ParamItem widget item

        @param param: 
        @type param: dict

        @param parent: 
        @type parent:
        """
        QTreeWidgetItem.__init__(self, parent)
        if 'network' in param:
            self.parseNetworkKey(param)
        elif 'test-environment' in param:
            self.parseTestEnvironment(param)
        elif 'projects' in param:
            self.parseProjects(param)
        else:
            self.setText(0, str( list(param.keys())[0].title() ) ) # wrap to list for python3 support
            self.setText(1,  str( list(param.values())[0] ) ) # wrap to list for python3 support

    def parseNetworkKey(self, data):
        """
        Parse the network key
        """
        tpl = []
        for eth in data['network']:
            if 'mac' in eth:
                tpl.append( '%s: mac=%s, ip=%s, bcast=%s, mask=%s' % (eth['name'], eth['mac'], eth['ip'], 
                                                                    eth['broadcast'], eth['mask'] ) )
            else:
                tpl.append( '%s: ip=%s, mask=%s' % (eth['name'], eth['ip'], eth['mask'] ) )
        self.setText(0, 'Network-Interfaces' )
        self.setText(1,  '\n'.join(tpl)  )

    def parseTestEnvironment(self, data):
        """
        Parse the test environment key
        """
        tpl = []
        for prj in data['test-environment']:
            tpl.append("%s (%s parameters)" % (prj['project_name'], len(prj['test_environment']) ) )

        self.setText(0, 'Test-Environment' )
        self.setText(1,  '\n'.join(tpl)  )

    def parseProjects(self, data):
        """
        Parse projects
        """
        tpl = []
        for prj in data['projects']:
            tpl.append("%s (Id=%s)" % (prj['name'], prj['project_id'] ) )
        self.setText(0, 'Projects' )
        self.setText(1,  '\n'.join(tpl)  )

class WServerInformation(QWidget, Logger.ClassLogger):
    """
    Widget for the global server information
    """
    def __init__(self, parent = None):
        """
        Constructs WServerInformation widget 

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Miscellaneous")
        self.createWidgets()
        self.createActions()
        self.createToolbar()
        self.deactivate()

    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarReset = QToolBar(self)
        self.dockToolbarReset.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarReset.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarGen = QToolBar(self)
        self.dockToolbarGen.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarGen.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.refreshBox = QGroupBox("Refresh")
        self.refreshBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutRefreshBox = QHBoxLayout()
        layoutRefreshBox.addWidget(self.dockToolbar)
        layoutRefreshBox.setContentsMargins(0,0,0,0)
        self.refreshBox.setLayout(layoutRefreshBox)
        
        self.resetBox = QGroupBox("Reset")
        self.resetBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutResetBox = QHBoxLayout()
        layoutResetBox.addWidget(self.dockToolbarReset)
        layoutResetBox.setContentsMargins(0,0,0,0)
        self.resetBox.setLayout(layoutResetBox)
        
        self.genBox = QGroupBox("Prepare")
        self.genBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutGenBox = QHBoxLayout()
        layoutGenBox.addWidget(self.dockToolbarGen)
        layoutGenBox.setContentsMargins(0,0,0,0)
        self.genBox.setLayout(layoutGenBox)
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.refreshBox)
        layoutToolbars.addWidget(self.genBox)
        layoutToolbars.addWidget(self.resetBox)
        layoutToolbars.addStretch(1)
        
        layoutFinal = QHBoxLayout()
        layoutLeft = QVBoxLayout()

        layoutRight = QVBoxLayout()
        layoutRight.addLayout( layoutToolbars )
        
        self.diskUsageBox = QGroupBox("Disk Usage")
        self.nbSizeLogsOnDiskLabel = QLabel("0")
        self.nbSizeTmpOnDiskLabel = QLabel("0")
        self.nbSizeArchivesOnDiskLabel = QLabel("0")
        self.nbSizeAdpOnDiskLabel = QLabel("0")
        self.nbSizeLibOnDiskLabel = QLabel("0")
        self.nbSizeBakOnDiskLabel = QLabel("0")
        self.nbSizeTestsOnDiskLabel = QLabel("0")
        layout2 = QFormLayout()
        layout2.addRow(QLabel("Logs"), self.nbSizeLogsOnDiskLabel )
        layout2.addRow(QLabel("Tmp"), self.nbSizeTmpOnDiskLabel )
        layout2.addRow(QLabel("Archives"), self.nbSizeArchivesOnDiskLabel )
        layout2.addRow(QLabel("Tests"), self.nbSizeTestsOnDiskLabel )
        layout2.addRow(QLabel("Adapters"), self.nbSizeAdpOnDiskLabel )
        layout2.addRow(QLabel("Libraries"), self.nbSizeLibOnDiskLabel )
        layout2.addRow(QLabel("Backups"), self.nbSizeBakOnDiskLabel )
        self.diskUsageBox.setLayout(layout2)

        self.tablesStatsBox = QGroupBox("Tables (Number of lines)")
        self.nbLinesScriptsStatsLabel = QLabel("0")
        self.nbLinesTestCasesStatsLabel = QLabel("0")
        self.nbLinesTestSuitesStatsLabel = QLabel("0")
        self.nbLinesTestUnitsStatsLabel = QLabel("0")
        self.nbLinesTestAbstractsStatsLabel = QLabel("0")
        self.nbLinesTestPlansStatsLabel = QLabel("0")
        self.nbLinesTestGlobalsStatsLabel = QLabel("0")
        self.nbLinesUsersLabel = QLabel("0")
        self.nbTotLinesLabel = QLabel("0")
        layoutNbLines = QFormLayout()
        layoutNbLines.addRow(QLabel("Table users"), self.nbLinesUsersLabel )
        layoutNbLines.addRow(QLabel("Table scripts"), self.nbLinesScriptsStatsLabel )
        layoutNbLines.addRow(QLabel("Table testcases"), self.nbLinesTestCasesStatsLabel )
        layoutNbLines.addRow(QLabel("Table testsuites"), self.nbLinesTestSuitesStatsLabel )
        layoutNbLines.addRow(QLabel("Table testunits"), self.nbLinesTestUnitsStatsLabel )
        layoutNbLines.addRow(QLabel("Table testabstracts"), self.nbLinesTestAbstractsStatsLabel )
        layoutNbLines.addRow(QLabel("Table testplans"), self.nbLinesTestPlansStatsLabel )
        layoutNbLines.addRow(QLabel("Table testglobals"), self.nbLinesTestGlobalsStatsLabel )
        self.lineNbLines = QFrame()
        self.lineNbLines.setGeometry(QRect(110, 221, 51, 20))
        self.lineNbLines.setFrameShape(QFrame.HLine)
        self.lineNbLines.setFrameShadow(QFrame.Sunken)
        layoutNbLines.addRow(self.lineNbLines )
        layoutNbLines.addRow(QLabel("Total"), self.nbTotLinesLabel )
        self.tablesStatsBox.setLayout(layoutNbLines)

        layoutGrid = QGridLayout()
        layoutGrid.addWidget(self.tablesStatsBox, 0, 0)
        layoutGrid.addWidget(self.diskUsageBox, 0, 1)
        layoutRight.addLayout( layoutGrid )
        layoutRight.addStretch(1)
        
        self.informations = QTreeWidget(self)
        self.informations.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.informations.setIndentation(10)
        self.labels = [ self.tr("Key"), self.tr("Value") ]
        self.informations.setHeaderLabels(self.labels)
        
        layoutLeft.addWidget( self.informations )
        layoutFinal.addLayout(layoutLeft)
        layoutFinal.addLayout(layoutRight)

        self.setLayout(layoutFinal)

    def createActions (self):
        """
        Actions defined:
         * generate the cache for the documentation
         * generate all packages
         * refresh statistics
         * refresh the context of the server
         * check the syntax of adapters
         * reset statistics
        """
        self.genCacheHelpAction = QtHelper.createAction(self, "&Generate\nDocumentations", self.genCacheHelp, 
                                                tip = 'Generate the cache for the documentation', 
                                                icon = QIcon(":/generate-doc.png") )
        self.genTarHelpAction = QtHelper.createAction(self, "&Packaging\nAll", self.genPackagesTar, 
                                                tip = 'Generate adapters, libraries and samples packages', 
                                                icon = QIcon(":/generate-tar.png") )
                                                
        self.refreshAction = QtHelper.createAction(self, "&Statistics", self.refreshStats, 
                                                tip = 'Refresh statistics',tooltip='Refresh statistics', 
                                                icon = QIcon(":/refresh-statistics.png") )
        self.refreshCtxAction = QtHelper.createAction(self, "&Session", self.refreshCtx, 
                                                tip = 'Refresh server context', tooltip='Refresh server context', 
                                                icon = QIcon(":/act-refresh.png") )

        self.resetAction = QtHelper.createAction(self, "&Reset\nStatistics", self.resetStats, 
                                                tip = 'Reset all statistics', 
                                                icon = QIcon(":/reset-counter.png") )
        self.unlockAllAction = QtHelper.createAction(self, "&Unlock\nTests", self.unlockAll, 
                                                tip = 'Unlock all files', 
                                                icon = QIcon(":/unlock.png") )
                                                
    def createToolbar(self):
        """
        Toolbar creation
        """
        self.dockToolbar.setObjectName("Misc toolbar")
        self.dockToolbar.addAction(self.refreshCtxAction)
        self.dockToolbar.addAction(self.refreshAction)
        self.dockToolbar.setIconSize(QSize(16, 16))
        
        self.dockToolbarGen.setObjectName("Generate toolbar")
        self.dockToolbarGen.addAction(self.genCacheHelpAction)
        self.dockToolbarGen.addAction(self.genTarHelpAction)
        self.dockToolbarGen.setIconSize(QSize(16, 16))
        
        self.dockToolbarReset.setObjectName("Reset toolbar")
        self.dockToolbarReset.addAction(self.resetAction)
        self.dockToolbarReset.addAction(self.unlockAllAction)
        self.dockToolbarReset.setIconSize(QSize(16, 16))
        
    def unlockAll(self):
        """
        Unlock all files
        """
        UCI.instance().cleanupLockFiles(tests=True, adapters=True, libraries=True)
        
    def genPackagesTar(self):
        """
        Generate all tar packages
        """
        UCI.instance().generateAll()

    def checkSyntaxAdapters(self):
        """
        Check syntax adapters
        """
        UCI.instance().checkSyntaxAdapters()

    def resetStats(self):
        """
        Reset statistic manually
        """
        reply = QMessageBox.question(self, "Reset statistics", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            UCI.instance().resetTestsStatistics()

    def refreshCtx(self):
        """
        Call the server to refresh context of the server
        """
        UCI.instance().refreshContextServer()

    def refreshStats(self):
        """
        Call the server to refresh statistics of the server
        """
        UCI.instance().refreshStatsServer()

    def genCacheHelp(self):
        """
        Call the server to generate the cache documentation
        """
        reply = QMessageBox.question(self, "Generate cache", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            UCI.instance().genCacheHelp()

    def active (self):
        """
        Enables QTreeWidget
        """
        self.diskUsageBox.setEnabled(True)
        self.tablesStatsBox.setEnabled(True)

        self.informations.setEnabled(True)

        self.genCacheHelpAction.setEnabled(True)
        self.resetAction.setEnabled(True)
        self.unlockAllAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.diskUsageBox.setEnabled(False)
        self.tablesStatsBox.setEnabled(False)

        self.informations.clear()
        self.informations.setEnabled(False)
        self.genCacheHelpAction.setEnabled(False)
        self.resetAction.setEnabled(False)
        self.unlockAllAction.setEnabled(False)

        self.nbSizeLogsOnDiskLabel.setText("0")
        self.nbSizeTmpOnDiskLabel.setText("0")
        self.nbSizeArchivesOnDiskLabel.setText("0")
        self.nbSizeAdpOnDiskLabel.setText("0")
        self.nbSizeLibOnDiskLabel.setText("0")
        self.nbSizeBakOnDiskLabel.setText("0")
        self.nbSizeTestsOnDiskLabel.setText("0")

    def cleanContext(self):
        """
        Clear the context
        Removes all items
        """
        self.informations.clear()

    def loadStats(self, data):
        """
        Load statistics
        """
        self.nbLinesUsersLabel.setText( str(data['nb-line-table-users']) )
        self.nbLinesScriptsStatsLabel.setText( str(data['nb-line-table-scriptsstats']) )
        self.nbLinesTestCasesStatsLabel.setText( str(data['nb-line-table-testcasesstats']) )
        self.nbLinesTestGlobalsStatsLabel.setText( str(data['nb-line-table-testglobalsstats']) )
        self.nbLinesTestPlansStatsLabel.setText( str(data['nb-line-table-testplansstats']) )
        self.nbLinesTestSuitesStatsLabel.setText( str(data['nb-line-table-testsuitesstats']) )
        self.nbLinesTestUnitsStatsLabel.setText( str(data['nb-line-table-testunitsstats']) )
        self.nbLinesTestAbstractsStatsLabel.setText( str(data['nb-line-table-testabstractsstats']) )
        self.nbTotLinesLabel.setText( str(data['nb-line-total']) )
        
        self.nbSizeLogsOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-logs']) ) )
        self.nbSizeTmpOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-tmp']) ) )

        self.nbSizeArchivesOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-testresults']) ) )
        self.nbSizeAdpOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-adapters']) ) )
        self.nbSizeLibOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-libraries']) ) )
        self.nbSizeBakOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-backups']) ) )
        self.nbSizeTestsOnDiskLabel.setText( str( QtHelper.bytes2human(data['disk-usage-tests']) ) )

    def loadData (self, data):
        """
        Load all config keys

        @param data: 
        @type data:
        """
        if isinstance(data, dict):
            data = [ data ]
        for param in data:
            probeItem = ParamItem( param = param, parent= self.informations)
        
        # resize collums
        for i in xrange(len(self.labels) - 1):
            self.informations.resizeColumnToContents(i)


SI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return SI

def initialize (parent):
    """
    Initialize WServerInformation widget
    """
    global SI
    SI = WServerInformation(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global SI
    if SI:
        SI = None