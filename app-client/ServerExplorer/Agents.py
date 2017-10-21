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
Plugin agents
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
import UserClientInterface as UCI


COL_RUNNING_AGENTID         = 0
COL_RUNNING_ADDRESS         = 1
COL_RUNNING_START_AT        = 2
COL_RUNNING_TYPE            = 3
COL_RUNNING_AUTO_STARTUP    = 4
COL_RUNNING_DESCRIPTION     = 5

COL_DEF_ENABLED         = 0
COL_DEF_NAME            = 1
COL_DEF_TYPE            = 2
COL_DEF_DESCRIPTION     = 3

class AgentDefaultItem(QTreeWidgetItem):
    """
    Item treewidget for default agent
    """
    def __init__(self, agent, parent = None, root = False):
        """
        Constructs AgentItem widget item

        @param Agent: 
        @type Agent: dict

        @param parent: 
        @type parent:

        @param root: 
        @type root: boolean
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.dataAgent = agent
        self.setText(   COL_DEF_ENABLED         , str( bool(eval(agent['enable'])))             )
        self.setText(   COL_DEF_NAME            , str(agent['name'])                )
        self.setText(   COL_DEF_TYPE            , str(agent['type'])                )
        self.setText(   COL_DEF_DESCRIPTION     , str(agent['description'])         )

class AgentInstalledItem(QTreeWidgetItem):
    """
    Item treewidget for installed agent
    """
    def __init__(self, agent, parent = None):
        """
        Constructs AgentInstalledItem widget item

        @param Agent: {'type': 'textual', 'description': 'This Agent enables to retrieve file logs on real time.'}
        @type Agent: dict

        @param parent: 
        @type parent:

        @param root: 
        @type root: boolean
        """
        QTreeWidgetItem.__init__(self, parent)
        #
        self.dataAgent = agent
        self.setText(0, str(agent['type']) )
        self.setIcon(0, QIcon(":/agent.png") )




class AgentItem(QTreeWidgetItem):
    """
    Item treewidget for agent
    """
    def __init__(self, agent, parent = None, root = False):
        """
        Constructs AgentItem widget item

        @param Agent: 
        @type Agent: dict

        @param parent: 
        @type parent:

        @param root: 
        @type root: boolean
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.dataAgent = agent
        self.setText(   COL_RUNNING_AGENTID         , str(agent['id'])                                  )
        if 'publicip' in agent:
            self.setText(   COL_RUNNING_ADDRESS         , str(agent['publicip'])                          )
        else:
            self.setText(   COL_RUNNING_ADDRESS         , str(agent['address'][0])                          )
        self.setText(   COL_RUNNING_START_AT        , QtHelper.formatTimestamp( agent['start-at'] )     )
        self.setText(   COL_RUNNING_TYPE            , str(agent['type'])                                )
        self.setText(   COL_RUNNING_AUTO_STARTUP    , str(agent['auto-startup'])                        )
        self.setText(   COL_RUNNING_DESCRIPTION     , str(agent['description'])                         )
        
        if not root: 
            self.setIcon(COL_RUNNING_AGENTID, QIcon(":/agent.png") )
            self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def getAgentType(self):
        """
        Returns agent type
        """
        return self.dataAgent['type']

class WAgents(QWidget, Logger.ClassLogger):
    """
    Widgets for agents
    """
    def __init__(self, parent):
        """
        Constructs WAgents widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Agents")
        self.itemCurrentRunning = None
        self.itemCurrentInstalled = None
        self.itemCurrentDefault = None
        self.agents = {}

        self.nbAgts = 0
        self.agtsInstalled = None

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
        
        self.statsBox = QGroupBox("Summary")
        self.nbInstalledLabel = QLabel("0")
        self.nbConfiguredLabel = QLabel("0")
        self.nbRegisteredLabel = QLabel("0")
        layout2 = QFormLayout()
        layout2.addRow(QLabel("Installed"), self.nbInstalledLabel )
        layout2.addRow(QLabel("Configured"), self.nbConfiguredLabel )
        layout2.addRow(QLabel("Registered"), self.nbRegisteredLabel )
        self.statsBox.setLayout(layout2)

        # group licence
        self.licenceBox = QGroupBox("Licences")
        self.nbRegistrationLabel = QLabel("0")
        self.nbDefaultLabel = QLabel("0")
        layoutNbLicence = QFormLayout()
        layoutNbLicence.addRow(QLabel("Max Registrations"), self.nbRegistrationLabel )
        layoutNbLicence.addRow(QLabel("Max Defaults"), self.nbDefaultLabel )
        self.licenceBox.setLayout(layoutNbLicence)


        self.nbRunningBox = QGroupBox("Running")
        self.nbAgtLabel = QLabel()
        layoutRunning = QVBoxLayout()
        layoutRunning.addWidget(self.nbAgtLabel)
        self.nbRunningBox.setLayout(layoutRunning)


        self.deployBox = QGroupBox("Default agents")
        self.agentsAvailable = QTreeWidget(self)
        self.agentsAvailable.setIndentation(10)
        self.labelsAvail = [ self.tr("Installed") ]
        self.agentsAvailable.setHeaderLabels(self.labelsAvail)

        self.runningBox = QGroupBox("Running")
        self.agentsRegistered = QTreeWidget(self)
        self.agentsRegistered.setIndentation(10)
        self.runningDockToolbar = QToolBar(self)
        self.runningDockToolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.availDockToolbar = QToolBar(self)
        self.availDockToolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.labels = [ self.tr("Name"), self.tr("Running on address"), self.tr("Started at"), self.tr("Type"), self.tr("Auto Startup"), self.tr("Description") ] 
        self.agentsRegistered.setHeaderLabels(self.labels)
        self.agentsRegistered.setColumnWidth(0, 180)
        self.agentsRegistered.setColumnWidth(1, 120)
        self.agentsRegistered.setColumnWidth(2, 150)
        self.agentsRegistered.setColumnWidth(3, 70)
        self.agentsRegistered.setContextMenuPolicy(Qt.CustomContextMenu)

        self.agentsDefault = QTreeWidget(self)
        self.agentsDefault.setIndentation(10)
        self.labelsDefault = [ self.tr("Enabled"), self.tr("Name"), self.tr("Type"), self.tr("Description") ]
        self.agentsDefault.setHeaderLabels(self.labelsDefault)
        self.agentsDefault.setContextMenuPolicy(Qt.CustomContextMenu)
        self.agentsDefault.setColumnWidth(1, 180)

        layoutRunning = QVBoxLayout()
        layoutRunning.addWidget(self.runningDockToolbar)
        layoutRunning.addWidget(self.agentsRegistered)
        self.runningBox.setLayout(layoutRunning)

        self.agentNameEdit = QLineEdit('')
        self.agentNameEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

        self.agentDescEdit = QLineEdit('')
        self.agentDescEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

        self.agentTypeEdit = QLineEdit('')
        self.agentTypeEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.agentTypeEdit.setEnabled(False)
        
        self.agentDescrInstalledEdit = QTextEdit('')
        self.agentDescrInstalledEdit.setEnabled(False)
        
        self.checkAutoStartOption = QCheckBox()
        self.checkStartNowOption = QCheckBox()

        paramLayout = QGridLayout()
        paramLayout.addWidget(QLabel("Type:"), 0, 0, Qt.AlignRight)
        paramLayout.addWidget(self.agentTypeEdit, 0, 1)
        paramLayout.addWidget(QLabel("Name:"), 1, 0, Qt.AlignRight)
        paramLayout.addWidget(self.agentNameEdit, 1, 1)
        paramLayout.addWidget(QLabel("Description:"), 2, 0, Qt.AlignRight)
        paramLayout.addWidget(self.agentDescEdit, 2, 1)
        paramLayout.addWidget(QLabel("Startup on boot:"), 3, 0, Qt.AlignRight)
        paramLayout.addWidget(self.checkAutoStartOption, 3, 1)
        paramLayout.addWidget(QLabel("Start now:"), 4, 0, Qt.AlignRight)
        paramLayout.addWidget(self.checkStartNowOption, 4, 1)
        
        layoutLeft = QVBoxLayout()

        layoutAvail = QHBoxLayout()
        layoutAvail.addWidget(self.agentsAvailable)
        layoutAvail.addWidget(self.agentDescrInstalledEdit)
        
        layoutLeft.addLayout(layoutAvail)
        layoutLeft.addWidget(self.runningBox)

        layoutDeploy = QVBoxLayout()
        layoutDeploy.addWidget(self.availDockToolbar)
        layoutDeploy.addLayout(paramLayout)
        layoutDeploy.addWidget(self.agentsDefault)
        self.deployBox.setLayout(layoutDeploy)
        
        layoutRightTop = QHBoxLayout()       
        layoutRightTop.addWidget(self.statsBox)
        layoutRightTop.addWidget(self.nbRunningBox)
        layoutRightTop.addWidget(self.licenceBox)

        layoutRight = QVBoxLayout()
        layoutRight.addLayout(layoutRightTop)
        layoutRight.addWidget(self.deployBox)   

        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)

    def createConnections (self):
        """
        Create Qt Connections
        """
        self.agentsRegistered.customContextMenuRequested.connect(self.onPopupMenu)
        self.agentsRegistered.currentItemChanged.connect(self.currentItemChanged)
        self.agentsRegistered.itemClicked.connect(self.itemClicked)

        self.agentsAvailable.currentItemChanged.connect(self.currentItemChanged)

        self.agentsDefault.currentItemChanged.connect(self.currentItemChanged)
        self.agentsDefault.customContextMenuRequested.connect(self.onPopupMenuDefault)

    def createActions (self):
        """
        Actions defined:
         * stop an agent
         * start an agent
         * delete an agent
         * clear all fields
         * refresh running agents
         * refresh default agents 
        """
        self.stopAction = QtHelper.createAction(self, "&Stop", self.stopAgent, tip = 'Stop agent', icon = QIcon(":/act-stop.png"))
        self.startAction = QtHelper.createAction(self, "&Add / Start", self.startAgent, tip = 'Add default agent', icon = QIcon(":/probe-add.png"))
        self.delAgentAction = QtHelper.createAction(self, "&Delete", self.delAgent, tip = 'Delete default agent', icon = QIcon(":/probe-del.png"))
        self.cancelAction = QtHelper.createAction(self, "&Clear", self.resetAgent, tip = 'Clear fields', icon = QIcon(":/clear.png") )
        self.refreshRunningAction = QtHelper.createAction(self, "&Refresh", self.refreshRunningAgent, tip = 'Refresh running agents', icon = QIcon(":/act-refresh.png") )
        self.refreshDefaultAction = QtHelper.createAction(self, "&Refresh", self.refreshDefaultAgent, tip = 'Refresh default agents', icon = QIcon(":/act-refresh.png") )

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-------||
        || Empty ||
        ||-------||
        """
        self.runningDockToolbar.setObjectName("Registered agent toolbar")
        self.runningDockToolbar.addAction(self.refreshRunningAction)
        self.runningDockToolbar.addSeparator()
        self.runningDockToolbar.addAction(self.stopAction)
        self.runningDockToolbar.addSeparator()
        self.runningDockToolbar.setIconSize(QSize(16, 16))

        self.availDockToolbar.setObjectName("Installed agent toolbar")
        self.availDockToolbar.addAction(self.refreshDefaultAction)
        self.availDockToolbar.addSeparator()
        self.availDockToolbar.addAction(self.startAction)
        self.availDockToolbar.addAction(self.delAgentAction)
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
            if isinstance( currentItem, AgentItem ):
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
            if isinstance( currentItem, AgentInstalledItem ):
                self.itemCurrentInstalled = currentItem
                if 'description' in currentItem.dataAgent:
                    self.agentDescrInstalledEdit.setText( currentItem.dataAgent['description'] )
                    self.agentTypeEdit.setText( currentItem.dataAgent['type'] )
                else:
                    self.agentDescrInstalledEdit.setText( '' )
            elif isinstance( currentItem, AgentItem ):
                self.itemCurrentRunning = currentItem
                self.stopAction.setEnabled(True)
            elif isinstance( currentItem, AgentDefaultItem ):
                self.itemCurrentDefault = currentItem
                self.delAgentAction.setEnabled(True)
            else:
                self.stopAction.setEnabled(False)
                self.delAgentAction.setEnabled(False)
                self.agentDescrInstalledEdit.setText( '' )

    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.agentsRegistered.itemAt(pos)
        if item:
            self.itemCurrentRunning = item
            self.menu.addAction( "Stop...", self.stopAgent)
            self.menu.popup(self.agentsRegistered.mapToGlobal(pos))

    def onPopupMenuDefault(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.agentsDefault.itemAt(pos)
        if item:
            self.itemCurrentDefault = item
            self.menu.addAction( "Delete...", self.delAgent)
            self.menu.popup(self.agentsDefault.mapToGlobal(pos))


    def refreshDefaultAgent(self):
        """
        Refresh the default list of Agents
        """
        UCI.instance().refreshDefaultAgents()

    def refreshRunningAgent(self):
        """
        Refresh the running list of Agents
        """
        UCI.instance().refreshRunningAgents()

    def delAgent(self):
        """
        Delete agent
        """
        if self.itemCurrentDefault is not None:
            reply = QMessageBox.question(self, "Stop agent", "Are you sure ?",
                QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                agentName = self.itemCurrentDefault.dataAgent['name']
                self.delAgentAction.setEnabled(False)
                UCI.instance().delAgent(agentName=agentName)

    def stopAgent(self):
        """
        Stop the selected Agent
        """
        if self.itemCurrentRunning is not None:
            reply = QMessageBox.question(self, "Stop agent", "Are you sure ?",
                QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                agentName = self.itemCurrentRunning.dataAgent['id']
                self.itemCurrentRunning = None
                self.stopAction.setEnabled(False)
                UCI.instance().stopAgent(agentName=agentName)

    def startAgent(self):
        """
        Start a new Agent
        """
        # some checks before
        if self.agentTypeEdit.text() == '':
            QMessageBox.information(self, "Add default agent" , "Please select the agent type.")
            return
        if self.agentNameEdit.text() == '':
            QMessageBox.information(self, "Add default agent" , "Agent name is mandatory.")
            return
        if not self.checkAutoStartOption.isChecked() and not self.checkStartNowOption.isChecked():
            QMessageBox.information(self, "Add default agent" , "Select startup option.")
            return
        # call web services
        agentType = str( self.agentTypeEdit.text() )
        agentName = str( self.agentNameEdit.text() )
        agentDescription =  str( self.agentDescEdit.text() )
        agentAutoStart = self.checkAutoStartOption.isChecked()

        if not self.checkStartNowOption.isChecked():
            UCI.instance().addAgent(agentType=agentType, agentName=agentName, agentDescription=agentDescription)
        else:
            UCI.instance().startAgent(agentType=agentType, agentName=agentName, agentDescription=agentDescription, agentAutoStart=agentAutoStart )

    def resetAgent(self):
        """
        Clear Agent field
        """
        self.agentDescrInstalledEdit.setText( '' )
        self.agentDescEdit.setText( '' )
        self.agentNameEdit.setText( '' )
        self.agentTypeEdit.setText( '' )
        # clear selection
        itms = self.agentsAvailable.selectedItems()
        for i in itms:
            if i.isSelected():
                i.setSelected(False)
        self.itemCurrentInstalled = None

    def active (self):
        """
        Enables QTreeWidget
        """
        self.agentsRegistered.setEnabled(True)
        self.agentsAvailable.setEnabled(True)
        self.deployBox.setEnabled(True)
        self.runningBox.setEnabled(True)
        self.statsBox.setEnabled(True)
        self.nbRunningBox.setEnabled(True)
        self.licenceBox.setEnabled(True)

        self.refreshRunningAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.nbRegistrationLabel.setText( "0" )
        self.nbDefaultLabel.setText( "0" )
        self.checkAutoStartOption.setCheckState(Qt.Unchecked) 
        self.checkStartNowOption.setCheckState(Qt.Unchecked) 

        self.agentsAvailable.clear()
        self.agentDescrInstalledEdit.setText('')
        
        self.agentsRegistered.clear()
        self.agentsDefault.clear()
        self.agents = {}
        
        self.agentsRegistered.setEnabled(False)
        self.agentsAvailable.setEnabled(False)
        self.deployBox.setEnabled(False)
        self.runningBox.setEnabled(False)
        self.licenceBox.setEnabled(False)

        # actions
        self.stopAction.setEnabled(False)
        self.delAgentAction.setEnabled(False)
        self.refreshRunningAction.setEnabled(False)

        self.itemCurrentRunning = None
        self.itemCurrentInstalled = None
        self.agtsInstalled = None

        self.agentDescEdit.setText( '' )
        self.agentTypeEdit.setText( '' )
        self.agentNameEdit.setText( '' )
        
        self.statsBox.setEnabled(False)
        self.nbInstalledLabel.setText( "0" )
        self.nbConfiguredLabel.setText( "0" )
        
        self.nbRunningBox.setEnabled(False)
        self.resetNbAgents()
        self.nbAgtLabel.setText('' )

    def getRunningAgents(self):
        """
        Get running Agents 
        """
        if sys.version_info > (3,): # python3 support
            return list(self.agents.keys())
        else:
            return self.agents.keys()

    def getRunningAgentsComplete(self):
        """
        Get running Agents with complete description
        """
        agents = []
        for agent, agentItem in self.agents.items():
            agt = {'name': agent}
            agt.update( agentItem.dataAgent )
            agents.append( agt )
        return agents

    def getAgentTypeByName(self, name):
        """
        Get Agent type by name

        @param name: 
        @type name:
        """
        if name in self.agents:
            return self.agents[name].getAgentType()
        else:
            return ''

    def loadStats(self, data):
        """
        Loads statistics

        @param data: 
        @type data: dict
        """
        self.nbRegistrationLabel.setText( str(data['max-reg']) )
        self.nbDefaultLabel.setText( str(data['max-def']) )

    def loadDefault (self, data):
        """
        Loads default Agents

        @param data: 
        @type data: dict
        """
        self.agentsDefault.clear()

        for defAgent in data:
            defAgentItem = AgentDefaultItem( agent = defAgent, parent= self.agentsDefault)
        totConfigured = len(data)
        self.nbConfiguredLabel.setText( str(totConfigured) ) 

    def loadData (self, data, dataInstalled=None):
        """
        Loads Agents

        @param data: 
        @type data: dict

        @param dataInstalled: 
        @type dataInstalled:
        """
        if isinstance(data, dict):
            data = [ data ]

        self.agentsRegistered.clear()

        for agent in data:
            agentItem = AgentItem( agent = agent, parent= self.agentsRegistered)
            self.agents[agent['id']] = agentItem

        totRunning = len(data)
        self.nbRegisteredLabel.setText( str(totRunning) ) 

        # load tests stats
        if dataInstalled is not None:
            if len(dataInstalled) == 0:
                self.deployBox.setEnabled(False)
                self.agentsAvailable.setEnabled(False)
            else:
                self.agtsInstalled = dataInstalled
                running = {}
                for p in dataInstalled:
                    running[ str(p['type']).lower() ] = 0
                    agentItem = AgentInstalledItem( agent = p, parent= self.agentsAvailable)
                self.nbInstalledLabel.setText( str(len(dataInstalled)) ) 

                for agent in data:
                    if agent['type'].lower() in running:
                        running[agent['type'].lower() ] += 1
                runningList = []
                for k,v in running.items():
                    runningList.append( '%s: %s' % (k.title(), v) )
                self.nbAgtLabel.setText( '\n'.join(runningList) )


    def resetNbAgents(self, data=None):
        """
        Reset the number of agents
        """
        if data is None:
            self.nbAgtLabel.setText( '' )
        else:
            if self.agtsInstalled is not None:
                running = {}
                for p in self.agtsInstalled:
                    running[ str(p['type']).lower() ] = 0

                for agent in data:
                    if agent['type'].lower() in running:
                        running[agent['type'].lower() ] += 1
                runningList = []
                for k,v in running.items():
                    runningList.append( '%s: %s' % (k.title(), v) )
                self.nbAgtLabel.setText( '\n'.join(runningList) )

    def refreshData (self, data, action):
        """
        Refresh Agents

        @param data: 
        @type data: dict

        @param action: expected values in 'del' and 'add'
        @type action: string
        """
        if action == 'del':
            self.agentsRegistered.clear()
            self.agents = {}
            self.resetNbAgents(data=data)
            self.loadData( data = data )
        elif action == 'add':
            self.resetNbAgents(data=data)
            self.loadData( data = data )        
        else:
            self.error( 'action unknown: %s' % str(action) )
    
    def refreshDataDefault(self, data, action):
        """
        Refresh Agents

        @param data: 
        @type data: dict

        @param action: expected values in 'del' and 'add'
        @type action: string
        """
        if action == 'del':
            self.agentsDefault.clear()
            self.loadDefault( data = data )
        elif action == 'add':
            self.agentsDefault.clear()
            self.loadDefault( data = data )     
        else:
            self.error( 'action unknown: %s' % str(action) )

AGENTS = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return AGENTS

def initialize (parent):
    """
    Initialize WAgentsRegistered widget
    """
    global AGENTS
    AGENTS = WAgents(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global AGENTS
    if AGENTS:
        AGENTS = None