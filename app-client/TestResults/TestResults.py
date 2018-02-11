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
Module to handle all test results
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QTabWidget, QVBoxLayout, QIcon, QToolButton, QTabBar, QWidget)
    from PyQt4.QtCore import (Qt, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QTabWidget, QVBoxLayout, QToolButton, QTabBar, QWidget)
    from PyQt5.QtCore import (Qt, QSize)
    
import threading

from Libs import QtHelper, Logger
try:
    import TestResult
except ImportError: # python 3 support
    from . import TestResult
    
import Settings

class SeparateResults(QtHelper.EnhancedQDialog):
    """
    Separate results dialog
    """
    def __init__(self, parent):
        """
        Result in an other dialog
        """
        QtHelper.EnhancedQDialog.__init__(self, parent)
        self.createDialog()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( "Realtime Results" )
        flags = Qt.WindowFlags()
        flags |= Qt.WindowMinimizeButtonHint
        flags |= Qt.WindowMaximizeButtonHint
        self.setWindowFlags(flags)

        self.secondTab = QTabWidget()
        self.secondTab.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.secondTab.setDocumentMode(True)
        self.secondTab.setTabPosition(QTabWidget.South)

        layout = QVBoxLayout()
        layout.addWidget(self.secondTab)
        self.setLayout(layout)

        layout.setContentsMargins(0,0,0,0)

    def closeEvent(self, event):
        """
        On close event
        """
        if instance() is not None:
            for wd in instance().getWidgetTests():
                wd.closeTest()
            instance().resetTests()
        event.accept()

    def updateTabColor(self, wTestResult, color):
        """
        Update the color of tabulation text
        """
        tabId =  self.secondTab.indexOf(wTestResult)
        self.secondTab.tabBar().setTabTextColor(tabId, color )

    def delResult(self, wTestResult):
        """
        Remove tab, delete a result
        """
        tabId =  self.secondTab.indexOf(wTestResult)
        self.secondTab.removeTab( tabId )
        return tabId

    def addResult(self, wTestResult):
        """
        Add a result to the tab manager
        """
        self.secondTab.addTab( wTestResult , QIcon(":/trx.png"), wTestResult.name )
            
        button = QToolButton()
        button.setIcon(QIcon(":/test-close.png"))
        button.setToolTip(self.tr("Close"))
        button.setIconSize(QSize(15,15))
        button.setStyleSheet( """
                     QToolButton {
                         border: none;
                         padding-right: 1px;

                     }

                     QToolButton:hover
                    {
                        border: 1px solid #8f8f91;
                        
                    }

                  """)

        button.released.connect(wTestResult.closeTest)

        self.secondTab.tabBar().setTabButton(self.secondTab.count()-1, QTabBar.RightSide, button)

        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-focus' ) ):
            self.secondTab.setCurrentWidget( wTestResult )

class WTestResults(QWidget, Logger.ClassLogger):
    """
    Test results widget
    """
    def __init__(self, parent):
        """
        Constructs WTestResults widget 

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.__mutex = threading.RLock()
        self.testId = 0
        self.tests = {}

    def resetTests(self):
        """
        Reset tests
        """
        self.tests = {}

    def getNumberOfTests(self):
        """
        Returns the number of tests
        """
        return len(self.tests)

    def getWidgetTests (self):
        """
        Returns all widgets tests
        """
        ret = []
        for wtest in list(self.tests.values()): # wrap to list for python3 support
            ret.append(wtest)
        return ret

    def getTestId (self):
        """
        Returns test Id
        """
        self.testId += 1
        return self.testId

    def delWidgetTest (self, testId):
        """
        Delete the widget test
        """
        if testId in self.tests:
            wtr = self.tests[testId]
            wtr.delLocalData()
            del wtr
            
    def getTestIdByWidget(self, wd):
        """
        Return test id by widget
        """
        ret=None
        for w in self.tests.items():
            tid,tw = w
            if tw == wd:
                ret = tid
                break
        return ret

    def getWidgetTest (self, testId):
        """
        Return widget test according to the testid passed as argument
        """
        ret = None
        if testId in self.tests:
            ret = self.tests[testId]
        return ret

    def newTest (self, name, tid = None, local = False, projectId=1):
        """
        Create a new test result widget
        Emit the signal "addTestTab"

        @param name: 
        @type name:

        @param tid: test id
        @type tid: int
        """
        wtr = TestResult.WTestResult( name, tid, self.parent, local, projectId )
        self.tests.update( { self.testId: wtr })
        return wtr

    def onLoadLocalTestResultTerminated(self, testId):
        """
        On load local test result terminated
        """
        if testId in self.tests:
            WTestResult = self.tests[testId]
            WTestResult.onTerminated( )
        else:
            pass # error
        
    def dispatchNotify (self, data, fromLocal=False):
        """
        Dispatch notify received

        @param data: 
        @type data:
        """
        testId = int(data['test-id'])
        if testId in self.tests:
            WTestResult = self.tests[testId]
            WTestResult.notifyReceived( data = data, fromLocal=fromLocal )
        else:
            pass # error

    def killWidgetTest(self, tid):
        """
        Kill the wdiget test
        """
        testId = int(tid)
        wdgs = self.getWidgetTests()
        for wt in wdgs:
            if wt.TID == testId:
                wt.killWidgetTest()
                
    def killWidgetTests(self, tids):
        """
        Kill the wdiget test
        """
        for tid in tids:
            self.killWidgetTest(tid=tid)

                
TR = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return TR

def initialize (parent):
    """
    Initialize WTestResults widget
    """
    global TR
    TR = WTestResults(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global TR
    if TR:
        TR = None