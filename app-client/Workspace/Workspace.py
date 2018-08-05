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
Workspace module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QHBoxLayout, QSplitter, QIcon, QTabWidget)
    from PyQt4.QtCore import (pyqtSignal, Qt)
except ImportError:
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QSplitter, QTabWidget)
    from PyQt5.QtCore import (pyqtSignal, Qt)
    
try:
    import DocumentProperties as WDocumentProperties
    import Repositories as WRepositories
    import DocumentViewer as WDocumentViewer  
except ImportError: # support python3
    from . import DocumentProperties as WDocumentProperties
    from . import Repositories as WRepositories
    from . import DocumentViewer as WDocumentViewer

import Settings
try:
    import TestConfig
    import TestAdapter
    import TestLibrary
    import TestPlan
    import TestTxt
    import TestData
    import TestPng
    import TestAbstract
    import TestUnit
    import TestSuite
except ImportError: # support python3
    from . import TestConfig
    from . import TestAdapter
    from . import TestLibrary
    from . import TestPlan
    from . import TestTxt
    from . import TestData
    from . import TestPng
    from . import TestAbstract
    from . import TestUnit
    from . import TestSuite
    
try:
    from PythonEditor import WCursorPosition
except ImportError: # support python3
    from .PythonEditor import WCursorPosition

import UserClientInterface as UCI
import RestClientInterface as RCI

from Libs import QtHelper, Logger
try:
    import Helper as WHelper
except ImportError: # support python3
    from . import Helper as WHelper

TAB_REPOSITORIES    = 0
TAB_PROPERTIES      = 1
 
class WWorkspace(QWidget):
    """
    Workspace widget
    """
    WORKSPACE = 0
    UpdateWindowTitle = pyqtSignal(str)
    RecentFile = pyqtSignal(dict)
    BusyCursor = pyqtSignal() 
    ArrowCursor = pyqtSignal() 
    def __init__(self, parent = None):
        """
        Constructs WWorkspace widget

        Signals emited:
         * updateWindowTitle

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.type = self.WORKSPACE
        self.name = self.tr('Workspace')
        
        # create each part
        WRepositories.initialize( parent = self )
        WDocumentViewer.initialize( parent = self, iRepo=WRepositories.instance(),
                                    lRepo=WRepositories.LocalRepository, 
                                    rRepo=WRepositories.RemoteRepository )
        WDocumentProperties.initialize( parent = self, iRepo=WRepositories.instance(),
                                        lRepo=WRepositories.LocalRepository, 
                                        rRepo=WRepositories.RemoteRepository )
        WHelper.initialize( parent = self )
        
        # splitter state
        self.splitterState = None
        self.splitterHelperState = None

        # create widget
        self.createWidgets()
        self.createActions()
        self.creationConnections()
    
    def createWidgets(self):
        """
        QtWidgets creation
           _________                _______________________      _________ 
          /         \__________    |                       |    /         \__
         |                     | Q |                       | Q |             |
         |   WRepositories     | S |                       | S |             |
         |                     | p |                       | p |             |
         |_____________________| l |                       | l |             |  
           _____QSplitter        i |     WDocumentViewer   | i |   WHelper   |
          /         \__________  t |                       | t |             |
         |                     | t |                       | t |             |
         | WDocumentProperties | e |                       | e |             |
         |                     | r |                       | r |             |
         |_____________________|   |_______________________|   |_____________|
        """

        self.wCursorPosition = WCursorPosition( self )
        self.parent.addWidgetToStatusBar( self.wCursorPosition )
        WDocumentProperties.instance().setDisabled(True)

        layout = QHBoxLayout(self)

        #  properties | viewer | helper
        self.vSplitter = QSplitter(self)

        if not QtHelper.str2bool( Settings.instance().readValue( key = 'View/tab-left' ) ):
            self.hSplitter = QSplitter(self)
            self.hSplitter.setOrientation(Qt.Vertical)

            self.hSplitter.addWidget( WRepositories.instance() )
            self.hSplitter.addWidget( WDocumentProperties.instance() )
            self.hSplitter.setContentsMargins(0,0,0,0)

            self.vSplitter.addWidget(self.hSplitter)
        else:
            WRepositories.instance().hideWidgetsHeader()
            WDocumentProperties.instance().hideWidgetsHeader()
            
            self.leftTab = QTabWidget(self)
            self.leftTab.addTab( WRepositories.instance(), QIcon(":/folders.png"), self.tr("Repositories") )
            self.leftTab.addTab( WDocumentProperties.instance(), QIcon(":/controls.png"),  self.tr("Test Properties") )
            self.vSplitter.addWidget( self.leftTab )

        self.vSplitter.addWidget( WDocumentViewer.instance() )
        self.vSplitter.setStretchFactor(1, 1)

        layout.addWidget(self.vSplitter)

        self.hSplitter2 = QSplitter(self)
        self.hSplitter2.setOrientation(Qt.Vertical)

        self.vSplitter.addWidget(self.hSplitter2)
        self.hSplitter2.addWidget( WHelper.instance() )

        self.setLayout(layout)
        
    def creationConnections (self):
        """
        QtSignals connection:
         * WRepositories <=> WDocumentViewer.newTab
         * WDocumentViewer <=> cursorPositionChanged
         * WDocumentViewer <=> focusChanged
        """
        WRepositories.instance().local().OpenFile.connect( WDocumentViewer.instance().newTab )

        WDocumentViewer.instance().CursorPositionChanged.connect(self.cursorPositionChanged)
        WDocumentViewer.instance().TotalLinesChanged.connect(self.totalLinesChanged)
        WDocumentViewer.instance().FocusChanged.connect(self.focusChanged)
        
        WDocumentViewer.instance().BusyCursor.connect(self.emitBusy)
        WDocumentViewer.instance().ArrowCursor.connect(self.emitIdle)
        WDocumentViewer.instance().CurrentDocumentChanged.connect(self.currentDocumentChanged)  
        WDocumentViewer.instance().DocumentOpened.connect(self.documentOpened)
        WDocumentViewer.instance().UpdateWindowTitle.connect(self.updateWindowTitle)
        WDocumentViewer.instance().DocumentViewerEmpty.connect(self.documentViewerEmpty)

        # from testplan when the test selection changed in the tree
        WDocumentViewer.instance().PropertiesChanged.connect(self.propertiesChanged)

        if WRepositories.instance().localConfigured != "Undefined":
            if RCI.instance().isAuthenticated():
                WDocumentViewer.instance().RefreshLocalRepository.connect(WRepositories.instance().localRepository.refreshAll)
                WDocumentProperties.instance().RefreshLocalRepository.connect(WRepositories.instance().localRepository.refreshAll)
        WDocumentViewer.instance().RecentFile.connect(self.recentFileUpdated)

        WHelper.instance().ShowAssistant.connect(self.onEnterAssistant)
        WHelper.instance().HideAssistant.connect(self.onLeaveAssistant)

        # new in v16
        WDocumentViewer.instance().ShowPropertiesTab.connect(self.onShowPropertiesTab)
        
    def onShowPropertiesTab(self):
        """
        On show properties tabulation
        """
        if QtHelper.str2bool( Settings.instance().readValue( key = 'View/tab-left' ) ): 
            self.leftTab.setCurrentIndex(TAB_PROPERTIES)  
        
    def onEnterAssistant(self):
        """
        On mouse enter in the online helper
        """
        pass

    def onLeaveAssistant(self):
        """
        On mouse leave in the online helper
        """
        pass
        
    def createActions (self):
        """
        Create qt actions
        """
        self.hideDeveloperModeAction = QtHelper.createAction(self, self.tr("Developer"), self.hideDeveloperMode, 
                                                        checkable=True, icon=QIcon(":/window-fit.png"), 
                                                        shortcut = Settings.instance().readValue( key = 'KeyboardShorcuts/developer' ),
                                                        tip = self.tr('Fit the document viewer to maximize the editor area') )
        WDocumentViewer.instance().addActionToolbar(action=self.hideDeveloperModeAction)

    def emitBusy(self):
        """
        Emit busy
        """
        self.BusyCursor.emit()
        
    def emitIdle(self):
        """
        Emit idle
        """
        self.ArrowCursor.emit()
        
    def hideDeveloperMode(self):
        """
        Hide developer mode
        """
        if not self.hideDeveloperModeAction.isChecked():
            Settings.instance().setValue( key = 'View/developer', value = 'False' )
            self.deactiveDeveloperView()
        else:
            Settings.instance().setValue( key = 'View/developer', value = 'True' )
            self.activeDeveloperView()

    def activeDeveloperView(self):
        """
        Activate developer view
        """
        self.splitterState = self.vSplitter.saveState()
        self.vSplitter.setSizes( [ 0, self.vSplitter.sizes()[1], 0 ] )

    def deactiveDeveloperView(self):
        """
        Deactive developer view
        """
        if self.splitterState is not None:
            self.vSplitter.restoreState(self.splitterState)

    def mainSplitterMoved(self, index, pos):
        """
        Memorize the new position of the splitter
        """
        Settings.instance().setValue( key = 'View/helper-pos', value = self.vSplitter.sizes()[2] )

    def hideHelper(self):
        """
        Hide assistant
        """
        self.splitterHelperState = self.vSplitter.saveState()
        self.vSplitter.setSizes( [ self.vSplitter.sizes()[0], self.vSplitter.sizes()[1], 0 ] )

    def showHelper(self):
        """
        Show assistant
        """
        if self.splitterHelperState is not None:
            self.vSplitter.restoreState(self.splitterHelperState)

    def documentViewerEmpty (self):
        """
        Called to deactivate the WDocumentProperties widget
        Hide the WCursorPosition widget in the status bar
        """
        WDocumentProperties.instance().clear()
        WDocumentProperties.instance().setDisabled(True)
        self.hideStatusBar()
        WDocumentViewer.instance().findWidget.hide()

    def currentDocumentChanged (self, wdocument):
        """
        Called when the current document is changed

        @param wdocument:
        @type wdocument:
        """
        # hide cursor position widget on disconnection or on the welcome page
        if isinstance(wdocument, WDocumentViewer.WelcomePage) :
            self.hideStatusBar()
            
        if not RCI.instance().isAuthenticated():
            WDocumentProperties.instance().setDisabled(True)
            return

        # test properties uneeded for test config, test adapter and library adapters
        # and welcome page
        if isinstance(wdocument, WDocumentViewer.WelcomePage) :

            WDocumentProperties.instance().setDisabled(True)
            WDocumentProperties.instance().clear()
        elif isinstance(wdocument, TestConfig.WTestConfig) or isinstance(wdocument, TestAdapter.WTestAdapter) \
                or isinstance(wdocument, TestTxt.WTestTxt)  or isinstance(wdocument, TestLibrary.WTestLibrary) \
                    or isinstance(wdocument, TestPng.WTestPng) : 
            WDocumentProperties.instance().setDisabled(True)
            WDocumentProperties.instance().clear()
        else:
            WDocumentProperties.instance().setDocument( wdoc = wdocument )
            WDocumentProperties.instance().setDisabled(False)
            WDocumentProperties.instance().addDescriptions( wdoc = wdocument )
            WDocumentProperties.instance().addParameters( wdoc = wdocument )        
            if not isinstance(wdocument, TestData.WTestData):
                WDocumentProperties.instance().addParametersOutput( wdoc = wdocument )
                WDocumentProperties.instance().addProbes( wdoc = wdocument )
                WDocumentProperties.instance().addAgents( wdoc = wdocument )
            WDocumentViewer.instance().updateActions( wdocument = wdocument )

            if isinstance(wdocument, TestData.WTestData):
                WDocumentProperties.instance().disableOutputParameters()
                WDocumentProperties.instance().disableAgents()
                WDocumentProperties.instance().disableProbes()
            else:
                WDocumentProperties.instance().enableOutputParameters()
                WDocumentProperties.instance().enableProbes()
                WDocumentProperties.instance().enableAgents()
   
            if not isinstance(wdocument, TestAbstract.WTestAbstract):
                WDocumentProperties.instance().disableSteps()
                WDocumentProperties.instance().disableAdapters()
                WDocumentProperties.instance().disableLibraries()
            else:
                WDocumentProperties.instance().addSteps( wdoc = wdocument )
                WDocumentProperties.instance().enableSteps()
                WDocumentProperties.instance().addAdapters( wdoc = wdocument )
                WDocumentProperties.instance().enableAdapters()
                WDocumentProperties.instance().addLibraries( wdoc = wdocument )
                WDocumentProperties.instance().enableLibraries()

            if isinstance(wdocument, TestUnit.WTestUnit) or isinstance(wdocument, TestSuite.WTestSuite):
                WDocumentProperties.instance().enableMarkUnused()
            else:
                WDocumentProperties.instance().disableMarkUnused()
                
        # disable/enable status bar
        if isinstance(wdocument, TestConfig.WTestConfig) \
                or isinstance(wdocument, TestPlan.WTestPlan) \
                or isinstance(wdocument, TestPng.WTestPng) \
                or  isinstance(wdocument, TestAbstract.WTestAbstract) \
                or isinstance(wdocument, WDocumentViewer.WelcomePage) :
            self.hideStatusBar()
        else:
            self.showStatusBar()
            self.wCursorPosition.setNumberLines(nb=wdocument.editor().lines())

    def propertiesChanged (self, properties, isRoot, testId):
        """
        Called when document propertis changed

        @param properties:
        @param properties: dict

        @param isRoot: 
        @type isRoot:
        """
        if isRoot:
            WDocumentProperties.instance().addDescriptions( wdoc = properties )
            WDocumentProperties.instance().addParameters( wdoc = properties )
            WDocumentProperties.instance().addParametersOutput( wdoc = properties )
            WDocumentProperties.instance().addAgents( wdoc = properties )
            WDocumentProperties.instance().addProbes( wdoc = properties )
            WDocumentProperties.instance().probes.setEnabled(True)
        else:
            WDocumentProperties.instance().addParameters( wdoc = properties )
            WDocumentProperties.instance().addAgents( wdoc = properties )
            WDocumentProperties.instance().addParametersOutput( wdoc = properties )
            WDocumentProperties.instance().probes.clear()
            WDocumentProperties.instance().probes.setEnabled(False)

        # new in v19
        WDocumentProperties.instance().updateCache(properties, isRoot, testId )
        
    def documentOpened (self, wdocument):
        """
        Called when a document is opened

        @param wdocument:
        @type wdocument:
        """
        WDocumentProperties.instance().setEnabled(True)
        self.currentDocumentChanged(wdocument = wdocument)

    def updateWindowTitle (self, windowTitle):
        """
        Emit the signal "updateWindowTitle" to update 
        the title of the application

        @param windowTitle: new window title
        @type windowTitle: string
        """
        self.UpdateWindowTitle.emit(windowTitle)

    def recentFileUpdated (self, fileDescription):
        """
        Emit the signal "recentFile" to update 
        the title of the application

        @param windowTitle: file descr with the complete path and type
        @type windowTitle: string
        """ 
        self.RecentFile.emit(fileDescription)

    def focusChanged (self, wdocument):
        """
        Called when the focus of the WDocumentViewer is changed

        @param wdocument:
        @type wdocument:
        """
        WDocumentViewer.instance().updateActions(wdocument = wdocument)
        self.wCursorPosition.setNumberLines(nb=wdocument.editor().lines())
        
    def totalLinesChanged (self, nb):
        """
        This function is automaticaly called when the cursor changed in both editors
        and enables to update the cursor's position in the widget WCursorPosition

        @param ln: line index
        @type ln: Integer
        
        @param col: column index
        @type col: Integer
        """
        self.wCursorPosition.setNumberLines(nb=nb)
        
    def cursorPositionChanged (self, ln, col):
        """
        This function is automaticaly called when the cursor changed in both editors
        and enables to update the cursor's position in the widget WCursorPosition

        @param ln: line index
        @type ln: Integer
        
        @param col: column index
        @type col: Integer
        """
        self.wCursorPosition.cursorPositionChanged(ln, col)
    
    def showStatusBar (self):
        """
        Show WCursorPosition widget
        """
        self.wCursorPosition.show()

    def hideStatusBar (self):
        """
        Hide WCursorPosition widget
        """
        self.wCursorPosition.hide()

Workspace = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return Workspace

def initialize (parent):
    """
    Initialize WWorkspace widget
    """
    global Workspace
    Workspace = WWorkspace(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global Workspace
    if Workspace:
        Workspace = None