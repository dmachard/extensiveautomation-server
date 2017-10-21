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
Module to create a test result
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


try:
    from PyQt4.QtGui import (QLabel, QTextEdit, QDialogButtonBox, QVBoxLayout, QPushButton, 
                            QHBoxLayout, QWidget, QTabWidget, QSplitter, QDialog, QMessageBox, 
                            QCursor, QApplication, QColor, QLineEdit, QFrame)
    from PyQt4.QtCore import (Qt)
except ImportError:
    from PyQt5.QtGui import (QCursor, QColor)
    from PyQt5.QtWidgets import (QLabel, QTextEdit, QDialogButtonBox, QVBoxLayout, 
                                QPushButton, QHBoxLayout, QWidget, QTabWidget, QSplitter, 
                                QDialog, QMessageBox, QApplication, QLineEdit, QFrame)
    from PyQt5.QtCore import (Qt)
    
import time
import base64
import os

try:
    import cStringIO
except ImportError: # support python 3
    import io as cStringIO
try:
    import cPickle
except ImportError: # support python 3
    import pickle as cPickle

try:
    xrange
except NameError: # support python3
    xrange = range

from Libs import QtHelper, Logger

import Settings
import Workspace.FileModels.TestResult as TestResultModel


try:
    import GraphView
    import ResumeView
    import TextualView
    import TestsView
    import DetailedView
except ImportError:
    from . import GraphView
    from . import ResumeView
    from . import TextualView
    from . import TestsView
    from . import DetailedView
    
import UserClientInterface as UCI

DURATION_PRECISION = 3

class CommentDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Comment dialog
    """
    def __init__(self, parent=None):
        """
        Dialog to add comment to the test result

        @param parent: 
        @type parent:
        """
        super(CommentDialog, self).__init__(parent)
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        commentLabel = QLabel("Add a comment on this test result:" )
        self.commentEdit = QTextEdit()
        self.commentEdit.setMinimumWidth(650)
        self.commentEdit.setMinimumWidth(500)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttonLayout = QVBoxLayout()
        self.okButton = QPushButton("Add", self)
        self.cancelButton = QPushButton("Cancel", self)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        mainLayout = QVBoxLayout()
        subMainLayout = QHBoxLayout()
        mainLayout.addWidget(commentLabel)
        subMainLayout.addWidget(self.commentEdit)
        subMainLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subMainLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle("Test Result > Add comment")
        
    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.acceptClicked)
        self.cancelButton.clicked.connect(self.reject)

    def acceptClicked(self):
        """
        Called when accept is clicked
        """
        if len(self.commentEdit.toPlainText()) > 0:
            self.accept()

    def getComment(self):
        """
        Return comment
        """
        return self.commentEdit.toPlainText()

class WTestResult(QWidget, Logger.ClassLogger):
    """
    Test result widget
    """
    TEST_RESULT = 2
    def __init__(self, name, tid = None, parent = None, local = False, projectId=1):
        """
        Constructs TestResult widget 

        @param name:
        @type name: 

        @param tid:
        @type tid: 

        @param parent:
        @type parent: 
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.local = local
        self.name = name
        self.PID = projectId
        self.TID = tid
        self.type = self.TEST_RESULT
        
        # default variables
        self.script = {}
        self.scriptEvents = {}
        self.testcases = {}
        self.separators = {}
        
        # construct widget
        self.createWidgets()
        self.createConnections()
        
        #
        self.isRunning = False
        self.tpTreeItem = None
        self.isTp = False
        
        # new in v11.2
        self.localFilename = ''
        self.dataModel = None
        self.headerReady = False
        self.isLoading = False

        # new in v16
        self.bigTr = False
        self.bigCache = { 'index': 0, 'testId': '', 'testName': '', "nb-total": 0 }
        
        self.setDefaultFilter()

    def createWidgets(self):
        """
        QtWidgets creation

         ___________   _________________
        |           | |                 |
        |           | |                 |
        |           | |                 |
        | TestsItem | | TextualLogView  |
        |           | |                 |
        |           | |                 |
        |___________| |_________________|
        """
        layout = QHBoxLayout()
        
        self.logsItem = TestsView.TestsView(parent=self, local = self.local)
        
        self.resumeView = ResumeView.TextualView(parent=self)
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/hide-resume-view' ) ):
            self.hideResumeView()

        self.graphView = GraphView.FlowChartView(parent=self)
        self.logsView = TextualView.TextualView2(parent=self)
        self.hexLogsView = DetailedView.DetailedView(parent=self)
    
        self.displayTab = QTabWidget()

        hSplitter = QSplitter(self)
        hSplitter.setOrientation(Qt.Vertical)

        hSplitter.addWidget( self.resumeView )
        hSplitter.addWidget( self.logsView )
        hSplitter.addWidget( self.hexLogsView )

        self.displayTab.addTab(hSplitter, self.tr('Events') )
        self.displayTab.addTab(self.graphView, self.tr('Diagram') )
        
        defaultTab = Settings.instance().readValue( key = 'TestRun/default-tab-run' )
        self.displayTab.setCurrentIndex(int(defaultTab))   
        
        self.currentEdit = QLineEdit()
        self.currentEdit.setReadOnly(True)
        self.currentEdit.setStyleSheet("QLineEdit { background-color : #F0F0F0; color: grey; }")

        leftFrame = QFrame()
        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)     
        leftFrame.setLayout(leftLayout)

        leftLayout.addWidget(self.currentEdit)
        leftLayout.addWidget(self.displayTab)

        v_splitter = QSplitter(self)      
        v_splitter.addWidget( self.logsItem )
        v_splitter.addWidget( leftFrame )
        v_splitter.setStretchFactor(1, 1)

        layout.addWidget(v_splitter)
        
        self.setLayout(layout)
    
    def createConnections (self):
        """
        QtSignals connection
        """
        self.logsItem.CloseTest.connect(self.closeTest)
        self.logsItem.ReplayTest.connect(self.replayTest)
        self.logsItem.KillTest.connect(self.killTest)
        self.logsItem.LoadTest.connect( self.loadTest )
        self.logsItem.TestName.connect( self.refreshTestName )
        self.logsView.ShowHexaView.connect( self.showHexaView )
        self.resumeView.GotoEvent.connect( self.gotoEvent )
        self.logsItem.AddPostTest.connect( self.addPostTest )
        self.logsItem.ExportVerdict.connect(self.exportVerdict)
        self.logsItem.ExportReport.connect(self.exportReport)
        self.logsItem.ExportDesign.connect(self.exportDesign)
        # connect for filter
        self.logsItem.FilterColumnUpdated.connect(self.updateFilterColumn )
        self.logsItem.RegExpUpdated.connect(self.updateFilterRegExp )
        # connect for options
        self.logsItem.HideResumeView.connect(self.hideResumeView)
        self.logsItem.ShowResumeView.connect(self.showResumeView)
        self.logsItem.ActiveScrollingEventLogs.connect(self.activeScrollingEventLogs)
        self.logsItem.DisableScrollingEventLogs.connect(self.disableScrollingEventLogs)
        # new in v12
        self.logsItem.ActiveScrollingDiagram.connect(self.activeScrollingDiagram)
        self.logsItem.DisableScrollingDiagram.connect(self.disableScrollingDiagram)
        # new in v16
        self.logsItem.LoadNext.connect( self.loadNext )
        
    def setDefaultFilter(self):
        """
        Set the default filer
        """
        self.logsItem.setDefaultFilter()

    def activeScrollingDiagram(self):
        """
        """
        pass

    def disableScrollingDiagram(self):
        """
        """
        pass
        
    def activeScrollingEventLogs(self):
        """
        Active scrolling on events logs
        """
        self.logsView.textualViewer.activeAutoscrolling()

    def disableScrollingEventLogs(self):
        """
        Disable scrolling on event logs
        """
        self.logsView.textualViewer.disableAutoscrolling()

    def setLocalData(self, filename):
        """
        """
        self.localFilename = filename
        self.dataModel = TestResultModel.DataModel()
        loaded = self.dataModel.load( absPath=self.localFilename )
        if not loaded:
            self.error( 'unable to load local data model (%s)' % self.localFilename  )

    def delLocalData(self):
        """
        Delete the local file
        """
        try:
            if len(self.localFilename): os.remove(self.localFilename)
        except Exception as e:
            pass
            
    def showResumeView(self):
        """
        Show the resume view
        """
        self.resumeView.setFixedHeight(ResumeView.DEFAULT_HEIGHT)

    def hideResumeView(self):
        """
        Hide the resume view
        """
        self.resumeView.setFixedHeight(0)

    def updateFilterRegExp(self, regExp):
        """
        Update the filter regexp
        """
        self.logsView.updateFilterRegExp(regExp=regExp)

    def updateFilterColumn(self, currentIndex):
        """
        Update the filter column
        """
        self.logsView.updateFilterColumn(currentIndex=currentIndex)

    def resetActions (self):
        """
        Reset all actions
        """

        self.logsItem.setDefaultActions()

    def exportVerdict(self):
        """
        Export the verdict
        """
        # call web services
        UCI.instance().exportTestVerdict(testId = self.TID, projectId=self.PID)

    def exportReport(self):
        """
        Export the report
        """
        # call web services
        UCI.instance().exportTestReport(testId = self.TID, projectId=self.PID)

    def exportDesign(self):
        """
        Export the design
        """
        # call web services
        UCI.instance().exportTestDesign(testId = self.TID, projectId=self.PID)

    def addPostTest(self):
        """
        Add post test
        """
        commentDialog = CommentDialog()
        if commentDialog.exec_() == QDialog.Accepted:
            trComment = commentDialog.getComment()
            if sys.version_info > (3,): # python 3 support
                postComment_encoded = base64.b64encode( bytes(trComment, 'utf8') )
                postComment_encoded = str(postComment_encoded, 'utf8')
            else:
                postComment_encoded = base64.b64encode( trComment.toUtf8() )
            # call web services
            UCI.instance().addCommentArchive( archiveFile = False, testId = self.TID , archivePost = postComment_encoded,
                                                postTimestamp=time.time() )

    def gotoEvent(self, data):
        """
        Go to event
        """
        if data['row-pos'] is None:
            self.error( 'none value on row position: %s' % data  )
            return
        self.logsView.textualViewer.setFocus()
        self.logsView.textualViewer.selectRow( data['row-pos'] ) 

    def showHexaView (self, data, dataType, shortName):
        """
        Show the hexa view 

        @param data:
        @type data:
        """
        self.hexLogsView.display( data = data, dataType = dataType, shortName = shortName)

    def killTest (self):
        """
        Kill the test
        """
        if not ( Settings.instance().readValue( key = 'TestRun/ask-before-kill' ) == 'True' ):
            UCI.instance().killTask(taskId=self.TID, taskIds=[self.TID] )
        else:
            reply = QMessageBox.warning(self, "Kill test", "Are you sure you want to stop the execution of the test?",
                            QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                UCI.instance().killTask(taskId=self.TID, taskIds=[self.TID] )

    def replayTest (self):
        """
        Replay the test
        """
        self.reset()
        UCI.instance().replayTest(  testId = self.TID )
        
    def closeTest (self):
        """
        Closes the test result tab widget
        """
        self.parent.delTab( self )

    def refreshTestName(self, testName):
        """
        """
        # new in v16
        self.currentEdit.setText( "%s" % testName)
        # end of new
        
    def loadTest (self, testId, testName):
        """
        Called when the user selects an test item
        Clear the textual log view and adds event

        @param testId:
        @type testId: 
        """
        # new in v16
        # self.currentEdit.setText( "%s" % testName)
        # end of new
        
        self.bigTr = False
        self.bigCache = { 'index': 0, 'testId': '', 'testName': '', "nb-total": 0 }
        self.logsItem.disableControls()
        
        if sys.version_info < (3,):
            testId = "%s" % testId
            testName = "%s" % testName
           
        # new in v12.1
        # reload all events from selected testcase each time for local testresult only
        if self.local:
            del self.scriptEvents
            self.scriptEvents = {}
        # end of new
        
        self.graphView.reset()
        self.resumeView.reset()
        self.logsView.reset()
            
        if self.isLoading:
            return
            
        self.isLoading = True
        
        if not self.isRunning:
            self.hexLogsView.reset() # fix bad behaviour to be confirm
            
        # new in v11.2
        self.logsView.setExpectedEventId(testId)

        if testId not in self.scriptEvents:  
            if self.local and self.headerReady: 
                self.setCursor(QCursor(Qt.BusyCursor) )
                self.loadLocalData(testId=testId, testName=testName)

        if testId in self.scriptEvents:
            nbMax = len(self.scriptEvents[ testId ])

            self.trace("test result: nb event detected in testcase %s" % (nbMax) )
            
            self.logsItem.progressBar.setMaximum( nbMax )
            if len(self.scriptEvents[ testId ]) > 200:
                self.setCursor(QCursor(Qt.BusyCursor) )

            # add limitation to avoid freeze, new in v16
            if not self.isRunning:
                if len(self.scriptEvents[ testId ]) > int(Settings.instance().readValue( key = 'TestRun/chunk-events' )): 
                    nbMax = int(Settings.instance().readValue( key = 'TestRun/chunk-events' ))
                    self.bigTr = True
                    self.logsItem.progressBar.setMaximum( nbMax )
                
            i = 0
            for evt in self.scriptEvents[ testId ][:nbMax]:
                # add progress bar
                i += 1
                self.logsItem.progressBar.setValue(i)
               
                # exit loop if the expected event id changed
                if self.logsView.getExpectedEventId() != testId:
                    break
                    
                # load data
                if Settings.instance() is None:
                    break
                    
                row_pos = self.logsView.addEvent( event = evt, ihmId=i)
                self.resumeView.addEvent( event = evt, rowp = row_pos, ihmId=i )

        self.setCursor(QCursor(Qt.ArrowCursor) )
        self.isLoading = False
        
        if self.bigTr:
            # memorize somes informations
            self.bigCache['index'] = i
            self.bigCache['testId'] = testId
            self.bigCache['testName'] = testName
            self.bigCache['nb-total'] = len(self.scriptEvents[ testId ])
            
            self.logsItem.enableControls()
            self.parent.showMessageTray( msg='Test %s is truncated...' % self.name )

    def loadNext(self):
        """
        """
        if not self.bigTr:
            self.logsItem.disableControls()
            return

        nbMax = int(Settings.instance().readValue( key = 'TestRun/chunk-events' ))
        
        if (self.bigCache['nb-total'] - self.bigCache['index']) <nbMax:
            self.logsItem.progressBar.setMaximum( (self.bigCache['nb-total'] - self.bigCache['index']) )
        else:
            self.logsItem.progressBar.setMaximum( nbMax )
        
        if self.bigCache['index'] >= self.bigCache['nb-total']:
            self.logsItem.disableControls()
            return
            
        i = 0
        self.graphView.reset()
        self.resumeView.reset()
        self.logsView.reset()

        for evt in self.scriptEvents[ self.bigCache['testId'] ][ self.bigCache['index']: self.bigCache['index']+nbMax+1]:
            i += 1

            self.logsItem.progressBar.setValue(i)
        
            row_pos = self.logsView.addEvent( event = evt, ihmId=self.bigCache['index']+i )
            self.resumeView.addEvent( event = evt, rowp = i, ihmId= self.bigCache['index'])
        
        self.bigCache['index'] = self.bigCache['index'] + i

        if self.bigCache['index'] >= self.bigCache['nb-total']:
            self.logsItem.disableControls()
            return
            
    def loadLocalData(self, testId, testName):
        """
        """
        if self.dataModel is None:
            return

        # read start and stop index
        startIndex = 0
        stopIndex = 0
        itemSelected = None
        if testId in self.script:
            itemSelected = self.script[testId]
            startIndex = self.script[testId].startIndex
            stopIndex = self.script[testId].stopIndex
        if testId in self.testcases:
            itemSelected = self.testcases[testId]
            startIndex = self.testcases[testId].startIndex
            stopIndex = self.testcases[testId].stopIndex
        if itemSelected is None:
            return
        
        self.trace("read index from %s to %s" % (startIndex, stopIndex) )
        startFlag = time.time()
        try:
            self.trace("local data: convert to io")
            f = cStringIO.StringIO( self.dataModel.testresult )
        except Exception as e:
            self.error( "unable to convert to io logs: %s" % str(e) )
            return
        else:
            self.logsItem.progressBar.setMaximum( stopIndex-startIndex )
            self.setCursor(QCursor(Qt.BusyCursor) )
            
            i = 0
            scriptId = None
            for n,line in enumerate(f):
                # exit loop if the expected event id changed
                if self.logsView.getExpectedEventId() != testId:
                    break
                    
                if stopIndex == 0 and n+1 > startIndex: # test can be kill so stop index can be equal to zero?
                    i += 1
                    self.logsItem.progressBar.setValue(i)
                    try:
                        #decode in base 64 and unpickle the data
                        if sys.version_info > (3,): # python3 support
                            l = base64.b64decode(line)
                            event = cPickle.loads( l, encoding="bytes")
                            event = QtHelper.bytes_to_unicode(event)
                        else:
                            l = base64.b64decode(line)
                            event = cPickle.loads( l )
                    except Exception as e:
                        self.error( line )
                        self.error( "unable to load line: %s" % e )
                    else:
                        event['test-id'] = testId
                        
                        # new in v12.1 change for parallel testcase
                        if scriptId is None: scriptId = event['script_id']
                        if scriptId != event['script_id']: 
                            continue
                        # end of new
                        
                        if n == startIndex:
                            # cleanup all testcases
                            if 'tc_id' in event:
                                if event['tc_id'] in self.scriptEvents:
                                    del self.scriptEvents[ "%s" % event['tc_id'] ]
                            else:
                                if event['script_id'] in self.scriptEvents:
                                    del self.scriptEvents[ "%s" % event['script_id'] ]
                        self.populateData(event=event, typeData=itemSelected.typeItem)
                        
                if n+1 in list(xrange(startIndex,stopIndex)): # or n in [25,29] 
                    i += 1
                    self.logsItem.progressBar.setValue(i)
                    try:
                        #decode in base 64 and unpickle the data
                        if sys.version_info > (3,): # python3 support
                            l = base64.b64decode(line)
                            event = cPickle.loads( l, encoding="bytes")
                            event = QtHelper.bytes_to_unicode(event)
                        else:
                            l = base64.b64decode(line)
                            event = cPickle.loads( l )
                    except Exception as e:
                        self.error( line )
                        self.error( "unable to load line: %s" % e )
                    else:
                        event['test-id'] = testId
                        
                        # new in v12.1 change for parallel testcase
                        if scriptId is None: scriptId = event['script_id']
                        if scriptId != event['script_id']: 
                            continue
                        # end of new
                            
                        if n == startIndex:
                            # cleanup all testcases
                            if 'tc_id' in event:
                                if event['tc_id'] in self.scriptEvents:
                                    del self.scriptEvents[ "%s" % event['tc_id'] ]
                            else:
                                if event['script_id'] in self.scriptEvents:
                                    del self.scriptEvents[ "%s" % event['script_id'] ]
                        self.populateData(event=event, typeData=itemSelected.typeItem)
                        
                # workaround in v11.2 to avoid app gui freeze
                QApplication.processEvents()
                
            self.setCursor(QCursor(Qt.ArrowCursor) )
        stopFlag = time.time()
        self.trace("time to load a part of the local test result (in seconds): %0.2f" % (stopFlag-startFlag))
    
    def populateData(self, event, typeData='testcase'):
        """
        """
        # normalize test id to str
        if 'script_id' in event:
            event['script_id'] = "%s" % event['script_id']
        if 'tc_id' in event:
            event['tc_id'] = "%s" % event['tc_id']

        if event['event'] == 'testglobal' and typeData == 'testglobal':
            if not event['script_id'] in self.scriptEvents:
                self.scriptEvents[ event['script_id'] ] = [ event ]
            else:
                self.scriptEvents[ event['script_id'] ].append( event )
            if not event['script_id'] in self.script:
                return
                
        if event['event'] == 'testplan' and typeData == 'testplan':
            if not event['script_id'] in self.scriptEvents:
                self.scriptEvents[ event['script_id'] ] = [ event ]
            else:
                self.scriptEvents[ event['script_id'] ].append( event )
            if not event['script_id'] in self.script:
                return
                
        if event['event'] == 'testabstract' and typeData == 'testabstract':
            if not event['script_id']  in self.scriptEvents:
                self.scriptEvents[ event['script_id'] ] = [ event ]
            else:
                self.scriptEvents[ event['script_id'] ].append( event )
            if not event['script_id'] in self.script:
                return
                
        if event['event'] == 'testsuite' and typeData == 'testsuite':
            if not event['script_id']  in self.scriptEvents:
                self.scriptEvents[ event['script_id'] ] = [ event ]
            else:
                self.scriptEvents[ event['script_id'] ].append( event )
            if not event['script_id'] in self.script:
                return
                
        if event['event'] == 'testunit' and typeData == 'testunit':
            if not event['script_id']  in self.scriptEvents:
                self.scriptEvents[ event['script_id'] ] = [ event ]
            else:
                self.scriptEvents[ event['script_id'] ].append( event )
            if not event['script_id'] in self.script:
                return
        
        if event['event'] == 'testcase' and typeData == 'testcase':
            if not event['script_id'] in self.script:
                return  # error
            if not event['tc_id'] in self.scriptEvents:
                self.scriptEvents[ event['tc_id'] ] = [ event ]
            else:
                self.scriptEvents[ event['tc_id'] ].append( event )
                
    def killWidgetTest(self):
        """
        Kill the widget test
        """
        self.logsItem.deactiveKill()
        self.parent.updateTabColor( self, color = QColor(Qt.red) )
        
        # new in v12.1
        for tcId, tcItem in self.testcases.items():
            wtc = self.logsItem.logs.itemWidget(tcItem, 0)
            if wtc.isRunning:  wtc.setUNDEF()

    def reset (self):
        """
        Reset global
        """
        self.isLoading = False
        
        self.graphView.reset()
        self.logsItem.reset()
        self.logsView.reset()
        self.hexLogsView.reset()
        self.resumeView.reset()

        self.tpTreeItem = None
        self.script = {}
        self.scriptEvents = {}
        self.testcases = {}
        
        self.currentEdit.setText( "" )
        
        self.bigTr = False
        self.bigCache = { 'index': 0, 'testId': '', 'testName': '', "nb-total": 0 }
        self.logsItem.disableControls()

    def breakpoint(self, tid):
        """
        Put breakpoint
        """
        self.logsItem.activeBreakpoint(tid=tid)

    def pause(self, tid, stepId, stepSummary):
        """
        Put pause
        """
        self.logsItem.activePause(tid=tid, stepId=stepId, stepSummary=stepSummary)

    def interact(self, tid, ask, counter, default):
        """
        interact
        """
        self.logsItem.activeInteract(tid=tid, ask=ask, counter=counter, default=default)
        
    def addGlobalTime(self, duration):
        """
        """
        firstItem = self.logsItem.logs.topLevelItem(0)
        firstItem.setDuration( "%.3f" % float(duration) )
    
    def onTerminated(self):
        """
        Called only when the local header of the test result is terminated
        """
        
        # new in v12.1
        for tcId, tcItem in self.testcases.items():
            wtc = self.logsItem.logs.itemWidget(tcItem, 0)
            if wtc.isRunning:  wtc.setUNDEF()

    def notifyReceived (self, data, fromLocal=False):
        """
        Dispatch events

        @param data:
        @type data: dict
        """

        # normalize test id to str
        if 'script_id' in data:
            data['script_id'] = "%s" % data['script_id']
        if 'tc_id' in data:
            data['tc_id'] = "%s" % data['tc_id']
        if 'test-internal-id' in data:
            data['test-internal-id'] = "%s" % data['test-internal-id']

        ############# Global events
        if data['event'] == 'script-started':
            self.parent.showMessageTray( msg='Test %s starting...' % self.name )
            self.isRunning = True
            #self.logsItem.activeReplay()
            self.parent.updateTabColor( self, color = QColor(Qt.darkCyan) )
            
        elif data['event'] == 'script-stopped':
            self.isRunning = False
            self.logsItem.deactiveKill()
            self.parent.updateTabColor( self, color = QColor(Qt.blue) )   
            
            self.addGlobalTime(duration=float(data['duration']))
            
            self.parent.showMessageTray( msg='Test %s terminated.' % self.name )
            # show the app
            if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/show-test-terminated' ) ):
                self.parent.setVisible(True)

        ############# test global events
        elif data['event'] == 'testglobal-started':
            self.isTp = True
            self.logsItem.activeKill()
            
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.resumeView.reset()
                self.logsView.reset()
            self.tpTreeItem = self.logsItem.createRootItem( event = data, typeItem='testglobal' )
            self.script[ data['script_id'] ] = self.tpTreeItem          
        elif data['event'] == 'testglobal-stopped':
            self.logsItem.deactiveKill()
            if self.isTp :
                self.logsItem.activeReplay()
            if not data['script_id'] in self.script:
                return  # error
            rootTreeItem = self.script[ data['script_id'] ] 
            # new in 3.0.0
            duration = None
            if 'duration' in data:
                duration = "%.3f" % float(data['duration'])
            self.logsItem.finishRootItem( rootItem = rootTreeItem, duration=duration, typeItem='testglobal', event=data)            
        elif data['event'] == 'testglobal':
            if not data['script_id'] in self.scriptEvents:
                self.scriptEvents[ data['script_id'] ] = [ data ]
            else:
                self.scriptEvents[ data['script_id'] ].append( data )
            if not data['script_id'] in self.script:
                return
            
            itemsSelected = self.logsItem.logs.selectedItems()
            rootTreeItem = self.script[ data['script_id'] ]
            if len(itemsSelected) > 1:
                rootTreeItem.setSelected(False)
            if rootTreeItem.isSelected():
                self.logsView.setExpectedEventId(data['script_id'])
                row_pos = self.logsView.addEvent( event = data )
                self.resumeView.addEvent( event = data, rowp = row_pos, ihmId=row_pos  )

        ############# test plan events
        elif data['event'] == 'testplan-separator-terminated':
            duration = "%.3f" % float(data['duration'])

            itemSeparator = self.separators[ data['test-internal-id'] ] 
            self.logsItem.finishTestplanSeparator( itemSep = itemSeparator, duration=duration)

        elif data['event'] == 'testplan-separator':
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.logsView.reset()
            itemSeparator = self.logsItem.createTestplanSeparator( event = data )
            self.separators[ data['test-internal-id'] ] = itemSeparator

        elif data['event'] == 'testplan-started':
            self.isTp = True
            self.logsItem.activeKill()
            
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.resumeView.reset()
                self.logsView.reset()
            self.tpTreeItem = self.logsItem.createRootItem( event = data, typeItem='testplan' )
            self.script[ data['script_id'] ] = self.tpTreeItem          
        elif data['event'] == 'testplan-stopped':
            self.logsItem.deactiveKill()
            if self.isTp :
                self.logsItem.activeReplay()
            if not data['script_id'] in self.script:
                return  # error
            rootTreeItem = self.script[ data['script_id'] ] 
            # new in 3.0.0
            duration = None
            if 'duration' in data:
                duration = "%.3f" % float(data['duration'])
            self.logsItem.finishRootItem( rootItem = rootTreeItem, duration=duration, typeItem='testplan', event=data)          
        elif data['event'] == 'testplan':
            if not data['script_id'] in self.scriptEvents:
                self.scriptEvents[ data['script_id'] ] = [ data ]
            else:
                self.scriptEvents[ data['script_id'] ].append( data )
            if not data['script_id'] in self.script:
                return
                
            itemsSelected = self.logsItem.logs.selectedItems()
            rootTreeItem = self.script[ data['script_id'] ]
            if len(itemsSelected) > 1:
                rootTreeItem.setSelected(False)
            if rootTreeItem.isSelected():
                self.logsView.setExpectedEventId(data['script_id'])
                row_pos = self.logsView.addEvent( event = data )
                self.resumeView.addEvent( event = data, rowp = row_pos, ihmId=row_pos )
        
        ############# test abstract events
        elif data['event'] == 'testabstract-started':
            self.logsItem.activeKill()
            if self.tpTreeItem is not None:
                self.tpTreeItem.setSelected(False)
                
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.resumeView.reset()
                self.logsView.reset()
            rootTreeItem = self.logsItem.createRootItem( event = data, typeItem='testabstract' )
            self.script[ data['script_id'] ] = rootTreeItem         
        elif data['event'] == 'testabstract-stopped':
            if not self.isTp :
                self.logsItem.activeReplay()
            if not data['script_id'] in self.script:
                return  # error
            rootTreeItem = self.script[ data['script_id'] ] 
            # new in 3.0.0
            duration = None
            if 'duration' in data:
                duration = "%.3f" % float(data['duration'])
            self.logsItem.finishRootItem( rootItem = rootTreeItem, duration=duration, typeItem='testabstract' , event=data)     
        elif data['event'] == 'testabstract':
            if not data['script_id']  in self.scriptEvents:
                self.scriptEvents[ data['script_id'] ] = [ data ]
            else:
                self.scriptEvents[ data['script_id'] ].append( data )
            if not data['script_id'] in self.script:
                return
            rootTreeItem = self.script[ data['script_id'] ]
            if rootTreeItem.isSelected():
                self.logsView.setExpectedEventId(data['script_id'])
                row_pos = self.logsView.addEvent( event = data )
                self.resumeView.addEvent( event = data, rowp = row_pos, ihmId=row_pos )
                
        ############# test unit events
        elif data['event'] == 'testunit-started':
            self.logsItem.activeKill()
            if self.tpTreeItem is not None:
                self.tpTreeItem.setSelected(False)
                
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.resumeView.reset()
                self.logsView.reset()
            rootTreeItem = self.logsItem.createRootItem( event = data, typeItem='testunit' )
            self.script[ data['script_id'] ] = rootTreeItem         
        elif data['event'] == 'testunit-stopped':
            if not self.isTp :
                self.logsItem.activeReplay()
            if not data['script_id'] in self.script:
                return  # error
            rootTreeItem = self.script[ data['script_id'] ] 
            # new in 3.0.0
            duration = None
            if 'duration' in data:
                duration = "%.3f" % float(data['duration'])
            self.logsItem.finishRootItem( rootItem = rootTreeItem, duration=duration, typeItem='testunit', event=data )     
        elif data['event'] == 'testunit':
            if not data['script_id']  in self.scriptEvents:
                self.scriptEvents[ data['script_id'] ] = [ data ]
            else:
                self.scriptEvents[ data['script_id'] ].append( data )
            if not data['script_id'] in self.script:
                return
            
            itemsSelected = self.logsItem.logs.selectedItems()
            rootTreeItem = self.script[ data['script_id'] ]
            if len(itemsSelected) > 1:
                rootTreeItem.setSelected(False)
            if rootTreeItem.isSelected():
                self.logsView.setExpectedEventId(data['script_id'])
                row_pos = self.logsView.addEvent( event = data )
                self.resumeView.addEvent( event = data, rowp = row_pos, ihmId=row_pos )

        ############# test suite events
        elif data['event'] == 'testsuite-started':
            self.logsItem.activeKill()
            if self.tpTreeItem is not None:
                self.tpTreeItem.setSelected(False)
                
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.resumeView.reset()
                self.logsView.reset()
            rootTreeItem = self.logsItem.createRootItem( event = data )
            self.script[ data['script_id'] ] = rootTreeItem         
        elif data['event'] == 'testsuite-stopped':
            if not self.isTp :
                self.logsItem.activeReplay()
            if not data['script_id'] in self.script:
                return  # error
            rootTreeItem = self.script[ data['script_id'] ] 
            # new in 3.0.0
            duration = None
            if 'duration' in data:
                duration = "%.3f" % float(data['duration'])
            self.logsItem.finishRootItem( rootItem = rootTreeItem, duration=duration, event=data )      
        elif data['event'] == 'testsuite':
            if not data['script_id']  in self.scriptEvents:
                self.scriptEvents[ data['script_id'] ] = [ data ]
            else:
                self.scriptEvents[ data['script_id'] ].append( data )
            if not data['script_id'] in self.script:
                return
                
            itemsSelected = self.logsItem.logs.selectedItems()
            rootTreeItem = self.script[ data['script_id'] ]
            if len(itemsSelected) > 1:
                rootTreeItem.setSelected(False)
            if rootTreeItem.isSelected():
                self.logsView.setExpectedEventId(data['script_id'])
                row_pos = self.logsView.addEvent( event = data )
                self.resumeView.addEvent( event = data, rowp = row_pos, ihmId=row_pos )
        
        ############# test case events
        elif data['event'] == 'testcase-started':
            if not data['script_id'] in self.script:
                return  # error
            #
            rootTreeItem = self.script[ data['script_id'] ]
            rootTreeItem.setSelected(False)
            
            itemsSelected = self.logsItem.logs.selectedItems()
            if not len(itemsSelected):
                self.graphView.reset()
                self.resumeView.reset()
                self.logsView.reset()

            testcaseTreeItem = self.logsItem.createTestcase( rootItem = rootTreeItem, event = data, fromLocal=fromLocal )
            self.testcases[ data['tc_id'] ] = testcaseTreeItem
        elif data['event'] == 'testcase-stopped':
            if not data['tc_id'] in self.testcases:
                return  # error
            #
            testcaseItem = self.testcases[ data['tc_id'] ]
            testcaseItem.setSelected(False)
            # new in 3.0.0
            duration = None
            if 'duration' in data:
                duration = "%.3f" % float(data['duration'])
            self.logsItem.finishTestcase( testcaseItem = testcaseItem, result = data['result'], duration=duration, event=data )
        elif data['event'] == 'testcase':
            # Issue 41: incorrect event displayed in test result
            # ignore invalid events
            if not data['script_id'] in self.script:
                return  # error
            #
            if not data['tc_id'] in self.scriptEvents:
                self.scriptEvents[ data['tc_id'] ] = [ data ]
            else:
                self.scriptEvents[ data['tc_id'] ].append( data )
            if not data['tc_id'] in self.testcases:
                return
            itemsSelected = self.logsItem.logs.selectedItems()
            testcaseItem = self.testcases[ data['tc_id'] ]
            
            # wtc = self.logsItem.logs.itemWidget(testcaseItem, 0)
            # wtc.startMovie()
            
            if len(itemsSelected) > 1:
                testcaseItem.setSelected(False)
            if testcaseItem.isSelected():
                self.logsView.setExpectedEventId(data['tc_id'])
                row_pos = self.logsView.addEvent( event = data )
                self.resumeView.addEvent( event = data, rowp = row_pos, ihmId=row_pos )