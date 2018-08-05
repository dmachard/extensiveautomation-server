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
Plugin probes
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QTreeWidgetItem, QIcon, QWidget, QHBoxLayout, QGroupBox, QLabel, 
                            QFormLayout, QVBoxLayout, QTreeWidget, QToolBar, QLineEdit, QSizePolicy, 
                            QTextEdit, QCheckBox, QGridLayout, QMenu, QMessageBox)
    from PyQt4.QtCore import (Qt, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QWidget, QHBoxLayout, QGroupBox, QLabel, 
                                QFormLayout, QVBoxLayout, QTreeWidget, QToolBar, QLineEdit, 
                                QSizePolicy, QTextEdit, QCheckBox, QGridLayout, QMenu, QMessageBox)
    from PyQt5.QtCore import (Qt, QSize)
    
import time

from Libs import QtHelper, Logger
# import UserClientInterface as UCI
import RestClientInterface as RCI

COL_RUNNING_PROBEID         = 0
COL_RUNNING_ADDRESS         = 1
COL_RUNNING_START_AT        = 2
COL_RUNNING_TYPE            = 3
COL_RUNNING_AUTO_STARTUP    = 4
COL_RUNNING_DESCRIPTION     = 5

COL_DEF_ENABLED         = 0
COL_DEF_NAME            = 1
COL_DEF_TYPE            = 2
COL_DEF_DESCRIPTION     = 3

class ProbeDefaultItem(QTreeWidgetItem):
    """
    Item treewidget for default probe
    """
    def __init__(self, probe, parent = None, root = False):
        """
        Constructs ProbeItem widget item

        @param probe: 
        @type probe: dict

        @param parent: 
        @type parent:

        @param root: 
        @type root: boolean
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.dataProbe = probe
        self.setText(   COL_DEF_ENABLED         , str( bool(eval(probe['enable'])))             )
        self.setText(   COL_DEF_NAME            , str(probe['name'])                )
        self.setText(   COL_DEF_TYPE            , str(probe['type'])                )
        self.setText(   COL_DEF_DESCRIPTION     , str(probe['description'])         )

class ProbeInstalledItem(QTreeWidgetItem):
    """
    Item treewidget for installed probe
    """
    def __init__(self, probe, parent = None):
        """
        Constructs ProbeInstalledItem widget item

        @param probe: {'type': 'textual', 'description': 'This probe enables to retrieve file logs on real time.'}
        @type probe: dict

        @param parent: 
        @type parent:

        @param root: 
        @type root: boolean
        """
        QTreeWidgetItem.__init__(self, parent)
        #
        self.dataProbe = probe
        self.setText(0, str(probe['type']) )
        self.setIcon(0, QIcon(":/probe.png") )




class ProbeItem(QTreeWidgetItem):
    """
    Item treewidget for probe
    """
    def __init__(self, probe, parent = None, root = False):
        """
        Constructs ProbeItem widget item

        @param probe: 
        @type probe: dict

        @param parent: 
        @type parent:

        @param root: 
        @type root: boolean
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.dataProbe = probe
        self.setText(   COL_RUNNING_PROBEID         , str(probe['id'])                                  )
        if 'publicip' in probe:
            self.setText(   COL_RUNNING_ADDRESS         , str(probe['publicip'])                          )
        else:
            self.setText(   COL_RUNNING_ADDRESS         , str(probe['address'][0])                          )
        self.setText(   COL_RUNNING_START_AT        , QtHelper.formatTimestamp( probe['start-at'] )     )
        self.setText(   COL_RUNNING_TYPE            , str(probe['type'])                                )
        self.setText(   COL_RUNNING_AUTO_STARTUP    , str(probe['auto-startup'])                        )
        self.setText(   COL_RUNNING_DESCRIPTION     , str(probe['description'])                         )
        
        if not root: 
            self.setIcon(COL_RUNNING_PROBEID, QIcon(":/probe.png") )
            self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def getProbeType(self):
        """
        Return the probe type
        """
        return self.dataProbe['type']


class WProbes(QWidget, Logger.ClassLogger):
    """
    Widget for probes
    """
    def __init__(self, parent):
        """
        Constructs WProbes widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Probes")
        self.itemCurrentRunning = None
        self.itemCurrentInstalled = None
        self.itemCurrentDefault = None
        self.probes = {}

        self.nbPrbs = 0
        # self.prbsInstalled = None

        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.createToolbar()
        self.deactivate()

    def createWidgets (self):
        """
        QtWidgets creation

        QTreeWidget (Name, Running on address, Type, Sched at, Version, Description)
         _______________
        |               |
        |---------------|
        |               |
        |               |
        |_______________|
        """
        layout = QHBoxLayout()

        self.deployBox = QGroupBox("Default probes")
        self.probesAvailable = QTreeWidget(self)
        self.probesAvailable.setIndentation(10)
        self.labelsAvail = [ self.tr("Installed") ]
        self.probesAvailable.setHeaderLabels(self.labelsAvail)

        self.runningBox = QGroupBox("Running")
        self.probesRegistered = QTreeWidget(self)
        self.probesRegistered.setIndentation(10)
        self.runningDockToolbar = QToolBar(self)
        self.runningDockToolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.availDockToolbar = QToolBar(self)
        self.availDockToolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.labels = [ self.tr("Name"), self.tr("Running on address"), self.tr("Started at"), 
                        self.tr("Type"), self.tr("Auto Startup"), self.tr("Description") ]        
        self.probesRegistered.setHeaderLabels(self.labels)
        self.probesRegistered.setColumnWidth(0, 180)
        self.probesRegistered.setColumnWidth(1, 120)
        self.probesRegistered.setColumnWidth(2, 150)
        self.probesRegistered.setColumnWidth(3, 70)
        self.probesRegistered.setContextMenuPolicy(Qt.CustomContextMenu)

        self.probesDefault = QTreeWidget(self)
        self.probesDefault.setIndentation(10)
        self.labelsDefault = [ self.tr("Enabled"), self.tr("Name"), self.tr("Type"), self.tr("Description") ]
        self.probesDefault.setHeaderLabels(self.labelsDefault)
        self.probesDefault.setContextMenuPolicy(Qt.CustomContextMenu)
        self.probesDefault.setColumnWidth(1, 180)


        layoutRunning = QVBoxLayout()
        layoutRunning.addWidget(self.runningDockToolbar)
        layoutRunning.addWidget(self.probesRegistered)
        self.runningBox.setLayout(layoutRunning)

        self.probeNameEdit = QLineEdit('')
        self.probeNameEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

        self.probeDescEdit = QLineEdit('')
        self.probeDescEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

        self.probeTypeEdit = QLineEdit('')
        self.probeTypeEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.probeTypeEdit.setEnabled(False)
        
        self.probeDescrInstalledEdit = QTextEdit('')
        self.probeDescrInstalledEdit.setEnabled(False)
        
        self.checkAutoStartOption = QCheckBox()
        self.checkStartNowOption = QCheckBox()

        paramLayout = QGridLayout()
        paramLayout.addWidget(QLabel("Type:"), 0, 0, Qt.AlignRight)
        paramLayout.addWidget(self.probeTypeEdit, 0, 1)
        paramLayout.addWidget(QLabel("Name:"), 1, 0, Qt.AlignRight)
        paramLayout.addWidget(self.probeNameEdit, 1, 1)
        paramLayout.addWidget(QLabel("Description:"), 2, 0, Qt.AlignRight)
        paramLayout.addWidget(self.probeDescEdit, 2, 1)
        paramLayout.addWidget(QLabel("Startup on boot:"), 3, 0, Qt.AlignRight)
        paramLayout.addWidget(self.checkAutoStartOption, 3, 1)
        paramLayout.addWidget(QLabel("Start now:"), 4, 0, Qt.AlignRight)
        paramLayout.addWidget(self.checkStartNowOption, 4, 1)
      
        layoutLeft = QVBoxLayout()

        layoutAvail = QHBoxLayout()
        layoutAvail.addWidget(self.probesAvailable)
        layoutAvail.addWidget(self.probeDescrInstalledEdit)
        
        layoutLeft.addLayout(layoutAvail)
        layoutLeft.addWidget(self.runningBox)

        layoutDeploy = QVBoxLayout()
        layoutDeploy.addWidget(self.availDockToolbar)
        layoutDeploy.addLayout(paramLayout)
        layoutDeploy.addWidget(self.probesDefault)
        self.deployBox.setLayout(layoutDeploy)

        layoutRight = QVBoxLayout()
        layoutRight.addWidget(self.deployBox)   

        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)

    def createConnections (self):
        """
        Create Qt Connections
        """
        self.probesRegistered.customContextMenuRequested.connect(self.onPopupMenu)
        self.probesRegistered.currentItemChanged.connect(self.currentItemChanged)
        self.probesRegistered.itemClicked.connect(self.itemClicked)

        self.probesAvailable.currentItemChanged.connect(self.currentItemChanged)

        self.probesDefault.currentItemChanged.connect(self.currentItemChanged)
        self.probesDefault.customContextMenuRequested.connect(self.onPopupMenuDefault)

    def createActions (self):
        """
        Actions defined:
         * stop probe
         * start probe
         * delete one probe
         * clear fields
         * refresh running probes
         * refresh default probes
        """
        self.stopAction = QtHelper.createAction(self, "&Stop", self.stopProbe, tip = 'Stop probe', 
                                        icon = QIcon(":/act-stop.png"))
        self.startAction = QtHelper.createAction(self, "&Add / Start", self.startProbe, tip = 'Add default probe', 
                                        icon = QIcon(":/probe-add.png"))
        self.delProbeAction = QtHelper.createAction(self, "&Delete", self.delProbe, tip = 'Delete default probe', 
                                        icon = QIcon(":/probe-del.png"))
        self.cancelAction = QtHelper.createAction(self, "&Clear", self.resetProbe, tip = 'Clear fields', 
                                        icon = QIcon(":/clear.png") )
        self.refreshRunningAction = QtHelper.createAction(self, "&Refresh", 
                                        self.refreshRunningProbe, tip = 'Refresh running probes', 
                                        icon = QIcon(":/act-refresh.png") )
        self.refreshDefaultAction = QtHelper.createAction(self, "&Refresh", 
                                        self.refreshDefaultProbe, tip = 'Refresh default probes', 
                                        icon = QIcon(":/act-refresh.png") )

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-------||
        || Empty ||
        ||-------||
        """
        self.runningDockToolbar.setObjectName("Registered Probe toolbar")
        self.runningDockToolbar.addAction(self.refreshRunningAction)
        self.runningDockToolbar.addSeparator()
        self.runningDockToolbar.addAction(self.stopAction)
        self.runningDockToolbar.addSeparator()
        self.runningDockToolbar.setIconSize(QSize(16, 16))

        self.availDockToolbar.setObjectName("Installed Probe toolbar")
        self.availDockToolbar.addAction(self.refreshDefaultAction)
        self.availDockToolbar.addSeparator()
        self.availDockToolbar.addAction(self.startAction)
        self.availDockToolbar.addAction(self.delProbeAction)
        self.availDockToolbar.addSeparator()
        self.availDockToolbar.addAction(self.cancelAction)
        self.availDockToolbar.addSeparator()
        self.availDockToolbar.setIconSize(QSize(16, 16))

    def itemClicked(self, currentItem):
        """
        On item clicked

        @param currentItem: 
        @type currentItem:  
        """
        if currentItem is not None:
            if isinstance( currentItem, ProbeItem ):
                self.itemCurrentRunning = currentItem
                self.stopAction.setEnabled(True)

    def currentItemChanged(self, currentItem, previousItem):
        """
        On current item changed

        @param currentItem: 
        @type currentItem:  

        @param previousItem: 
        @type previousItem: 
        """
        if currentItem is not None:
            if isinstance( currentItem, ProbeInstalledItem ):
                self.itemCurrentInstalled = currentItem
                if 'description' in currentItem.dataProbe:
                    self.probeDescrInstalledEdit.setText( currentItem.dataProbe['description'] )
                    self.probeTypeEdit.setText( currentItem.dataProbe['type'] )
                else:
                    self.probeDescrInstalledEdit.setText( '' )
            elif isinstance( currentItem, ProbeItem ):
                self.itemCurrentRunning = currentItem
                self.stopAction.setEnabled(True)
            elif isinstance( currentItem, ProbeDefaultItem ):
                self.itemCurrentDefault = currentItem
                self.delProbeAction.setEnabled(True)
            else:
                self.stopAction.setEnabled(False)
                self.delProbeAction.setEnabled(False)
                self.probeDescrInstalledEdit.setText( '' )

    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.probesRegistered.itemAt(pos)
        if item:
            self.itemCurrentRunning = item
            self.menu.addAction( "Stop...", self.stopProbe)
            self.menu.popup(self.probesRegistered.mapToGlobal(pos))

    def onPopupMenuDefault(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.probesDefault.itemAt(pos)
        if item:
            self.itemCurrentDefault = item
            self.menu.addAction( "Delete...", self.delProbe)
            self.menu.popup(self.probesDefault.mapToGlobal(pos))


    def refreshDefaultProbe(self):
        """
        Refresh the default list of probes
        """
        RCI.instance().defaultProbes()
        
    def refreshRunningProbe(self):
        """
        Refresh the running list of probes
        """
        RCI.instance().runningProbes()
        
    def delProbe(self):
        """
        Delete probe
        """
        if self.itemCurrentDefault is not None:
            reply = QMessageBox.question(self, "Stop probe", "Are you sure ?",
                QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                probeName = self.itemCurrentDefault.dataProbe['name']
                self.delProbeAction.setEnabled(False)
                
                # rest call
                RCI.instance().removeProbe(probeName=probeName)
                
    def stopProbe(self):
        """
        Stop the selected probe
        """
        if self.itemCurrentRunning is not None:
            reply = QMessageBox.question(self, "Stop probe", "Are you sure ?",
                QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                probeName = self.itemCurrentRunning.dataProbe['id']
                self.itemCurrentRunning = None
                self.stopAction.setEnabled(False)
                
                # rest call
                RCI.instance().disconnectProbe(probeName=probeName)
                
    def startProbe(self):
        """
        Start a new probe
        """
        # some checks before
        if self.probeTypeEdit.text() == '':
            QMessageBox.information(self, "Add Default Probe" , "Please select the probe type.")
            return
        if self.probeNameEdit.text() == '':
            QMessageBox.information(self, "Add Default Probe" , "Probe name is mandatory.")
            return
        if not self.checkAutoStartOption.isChecked() and not self.checkStartNowOption.isChecked():
            QMessageBox.information(self, "Add Default Probe" , "Select startup option.")
            return
            
        # call web services
        probeType = str( self.probeTypeEdit.text() )
        probeName = str( self.probeNameEdit.text() )
        probeDescription =  str( self.probeDescEdit.text() )
        probeAutoStart = self.checkAutoStartOption.isChecked()

        if not self.checkStartNowOption.isChecked():
            RCI.instance().addProbe(probeName=probeName, probeType=probeType, 
                                    probeDescription=probeDescription)
        else:
            RCI.instance().connectProbe(probeName=probeName, probeType=probeType, 
                                        probeDescription=probeDescription, 
                                        probeBoot=probeAutoStart)
                                        
    def resetProbe(self):
        """
        Clear probe field
        """
        self.probeDescrInstalledEdit.setText( '' )
        self.probeDescEdit.setText( '' )
        self.probeNameEdit.setText( '' )
        self.probeTypeEdit.setText( '' )
        
        # clear selection
        itms = self.probesAvailable.selectedItems()
        for i in itms:
            if i.isSelected():
                i.setSelected(False)
        self.itemCurrentInstalled = None

    def active (self):
        """
        Enables QTreeWidget
        """
        self.probesRegistered.setEnabled(True)
        self.probesAvailable.setEnabled(True)
        self.deployBox.setEnabled(True)
        self.runningBox.setEnabled(True)

        self.refreshRunningAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.checkAutoStartOption.setCheckState(Qt.Unchecked) 
        self.checkStartNowOption.setCheckState(Qt.Unchecked) 

        self.probesAvailable.clear()
        self.probeDescrInstalledEdit.setText('')
        
        self.probesRegistered.clear()
        self.probesDefault.clear()
        self.probes = {}
        
        self.probesRegistered.setEnabled(False)
        self.probesAvailable.setEnabled(False)
        self.deployBox.setEnabled(False)
        self.runningBox.setEnabled(False)

        # actions
        self.stopAction.setEnabled(False)
        self.delProbeAction.setEnabled(False)
        
        self.itemCurrentRunning = None
        self.itemCurrentInstalled = None

        self.probeDescEdit.setText( '' )
        self.probeTypeEdit.setText( '' )
        self.probeNameEdit.setText( '' )

        self.resetNbProbes()

        self.refreshRunningAction.setEnabled(False)

    def getRunningProbes(self):
        """
        Get running probes 
        """
        if sys.version_info > (3,): # python3 support
            return list(self.probes.keys())
        else:
            return self.probes.keys()

    def getProbeTypeByName(self, name):
        """
        Get probe type by name

        @param name: 
        @type name:
        """
        if name in self.probes:
            return self.probes[name].getProbeType()
        else:
            return ''

    def loadDefault (self, data):
        """
        Loads default probes

        @param data: 
        @type data: dict
        """
        self.probesDefault.clear()

        for defProbe in data:
            defProbeItem = ProbeDefaultItem( probe = defProbe, parent= self.probesDefault)

    def loadData (self, data, dataInstalled=None):
        """
        Loads probes

        @param data: 
        @type data: dict

        @param dataInstalled: 
        @type dataInstalled:
        """
        if isinstance(data, dict):
            data = [ data ]

        self.probesRegistered.clear()

        for probe in data:
            probeItem = ProbeItem( probe = probe, parent= self.probesRegistered)
            self.probes[probe['id']] = probeItem

        # load tests stats
        if dataInstalled is not None:
            if len(dataInstalled) == 0:
                self.deployBox.setEnabled(False)
                self.probesAvailable.setEnabled(False)

    def resetNbProbes(self, data=None):
        """
        Reset the number of probes
        """
        pass

    def refreshData (self, data, action):
        """
        Refresh probes

        @param data: 
        @type data: dict

        @param action: expected values in 'del' and 'add'
        @type action: string
        """
        if action == 'del':
            self.probesRegistered.clear()
            self.probes = {}
            self.resetNbProbes(data=data)
            self.loadData( data = data )
        elif action == 'add':
            self.resetNbProbes(data=data)
            self.loadData( data = data )        
        else:
            self.error( 'action unknown: %s' % str(action) )
    
    def refreshDataDefault(self, data, action):
        """
        Refresh probes

        @param data: 
        @type data: dict

        @param action: expected values in 'del' and 'add'
        @type action: string
        """
        if action == 'del':
            self.probesDefault.clear()
            self.loadDefault( data = data )
        elif action == 'add':
            self.probesDefault.clear()
            self.loadDefault( data = data )     
        else:
            self.error( 'action unknown: %s' % str(action) )

PR = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return PR

def initialize (parent):
    """
    Initialize WProbesRegistered widget
    """
    global PR
    PR = WProbes(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global PR
    if PR:
        PR = None