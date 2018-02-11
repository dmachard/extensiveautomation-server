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
Plugin test manager
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
    from PyQt4.QtGui import (QTreeWidgetItem, QIcon, QBrush, QWidget, QTabWidget, QVBoxLayout, 
                            QHBoxLayout, QGroupBox, QFrame, QTreeWidget, QAbstractItemView, QColor,
                            QToolBar, QSplitter, QLabel, QFormLayout, QDialog, QMessageBox, QMenu)
    from PyQt4.QtCore import (Qt, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon, QBrush, QColor)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                                QGroupBox, QFrame, QTreeWidget, QAbstractItemView, QToolBar, 
                                QSplitter, QLabel, QFormLayout, QDialog, QMessageBox, QMenu)
    from PyQt5.QtCore import (Qt, QSize)
    
import time

try:
    xrange
except NameError: # support python3
    xrange = range
    
import UserClientInterface as UCI
import RestClientInterface as RCI
from Libs import QtHelper, Logger
from Workspace import ScheduleDialog

STATE_INIT = 'INIT'
STATE_WAITING = 'WAITING'
STATE_RUNNING = 'RUNNING'
STATE_COMPLETE = 'COMPLETE'
STATE_ERROR = 'ERROR'
STATE_DISABLED = 'DISABLED'

STATE_KILLING = 'KILLING'
STATE_KILLED = 'KILLED'

STATE_CANCELLING = 'CANCELLING'
STATE_CANCELLED = 'CANCELLED'

SCHED_TYPE_UNDEFINED    = -2

SCHED_NOW           =   -1      # one run 
SCHED_AT            =   0       # run postponed
SCHED_IN            =   1       # run postponed
SCHED_EVERY_SEC     =   2
SCHED_EVERY_MIN     =   3
SCHED_HOURLY        =   4
SCHED_DAILY         =   5
SCHED_EVERY_X_MIN   =   6
SCHED_WEEKLY        =   7
SCHED_NOW_MORE      =   8
SCHED_QUEUE         =   9
SCHED_QUEUE_AT      =   10

def formatTimestamp ( timestamp ):
    """
    Returns human-readable time

    @param timestamp: 
    @type timestamp:

    @return:
    @rtype:
    """
    if isinstance( timestamp, str):
        return "  %s  " % timestamp
    ret = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(timestamp) ) 
    return ret


COL_RUNNING_ID              = 0
COL_RUNNING_PROJECT         = 1
COL_RUNNING_NAME            = 2
COL_RUNNING_START           = 3
COL_RUNNING_AUTHOR          = 4
COL_RUNNING_RECURSIVE       = 5


class TaskEnqueuedItem(QTreeWidgetItem, Logger.ClassLogger):
    """
    Treewidget item for task enqueued
    """
    def __init__(self, text, parent = None, icon=None):
        """
        Constructs TaskItem widget item

        @param task: 
        @type task: list

        @param parent: 
        @type parent:
        """
        QTreeWidgetItem.__init__(self, parent)

        self.setText(COL_RUNNING_ID, text )
        self.setIcon(COL_RUNNING_ID, QIcon(":/processes.png") )
        if icon is not None:
            self.setIcon(COL_RUNNING_ID, icon )

class TaskRunningItem(QTreeWidgetItem, Logger.ClassLogger):
    """
    Treewidget item for task running
    """
    def __init__(self, task, parent = None):
        """
        Constructs TaskItem widget item

        @param task: 
        @type task: list

        @param parent: 
        @type parent:
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.taskData = task
        self.taskId = task['id']
        self.taskState = None
        
        self.setText(COL_RUNNING_ID, str( task['id'] ) )
        self.setText(COL_RUNNING_PROJECT, instance().getProjectName(task['project-id']) )
        self.setText(COL_RUNNING_NAME, str(task['name']) )
        self.setText(COL_RUNNING_START, formatTimestamp( task['start-at'] )  ) 
        self.setText(COL_RUNNING_AUTHOR, str( task['user'] ) )
        self.setText(COL_RUNNING_RECURSIVE, str( task['recursive'] ) )
        
        self.setStateIcon( state=str(task['state']) )

    def setStateIcon(self, state):
        """
        Set the icon state
        """
        if state == STATE_RUNNING:
            self.setIcon(COL_RUNNING_ID, QIcon(":/process-icon.png") )
        self.taskState = state

COL_WAIT_ID         = 0
COL_WAIT_GROUP      = 1
COL_WAIT_TYPE       = 2
COL_WAIT_PROJECT    = 3
COL_WAIT_NAME       = 4
COL_WAIT_NEXT       = 5
COL_WAIT_REPEAT     = 6
COL_WAIT_PROBE      = 7
COL_WAIT_NOTIF      = 8
COL_WAIT_RESULT     = 9
COL_WAIT_AUTHOR     = 10

class TaskWaitingItem(QTreeWidgetItem, Logger.ClassLogger):
    """
    Treewidget item for waiting task
    """
    def __init__(self, task, parent = None):
        """
        Constructs TaskItem widget item

        @param task: 
        @type task: list

        @param parent: 
        @type parent:
        """
        QTreeWidgetItem.__init__(self, parent)
        
        eventid, eventtype, eventargs, eventtime, eventname, \
        author, realruntime, duration, result, eventnb, \
        eventnbcur, eventenabled, withoutprobes, withoutnotif, \
        nokeeptr, userid, projectid, eventfrom, eventto, groupid  = task
        
        self.taskId = eventid
        try:
            self.taskEventArgs = eval(eventargs)
        except Exception as e:
            self.error( "unable to eval event args (%s): %s" % (str(eventargs), str(e)) )
            self.taskEventArgs = (0,0,0,0,0,0)

        self.taskEventType = eventtype
        self.taskEventTime = eventtime
        self.taskEventName = eventname
        self.taskEventAuthor = author
        self.taskEventRealruntime = realruntime
        self.taskEventDuration = duration
        self.taskEventResult = result
        self.taskEventNb = eventnb
        self.taskEventNbCurrent = eventnbcur
        self.taskEventEnabled = eventenabled
        self.taskWithoutProbes = withoutprobes
        self.taskWithoutNotif = withoutnotif
        self.taskNoKeepTr = nokeeptr
        self.taskProjectId = projectid
        self.taskGroupId = groupid
        try:
            self.taskEventFrom = eval(eventfrom)
        except Exception as e:
            self.error( "unable to eval event args (%s): %s" % (str(eventfrom), str(e)) )
            self.taskEventFrom = (0,0,0,0,0,0)

        try:
            self.taskEventTo = eval(eventto)
        except Exception as e:
            self.error( "unable to eval event args (%s): %s" % (str(eventto), str(e)) )
            self.taskEventTo = (0,0,0,0,0,0)
        
        self.setText(COL_WAIT_ID, str( eventid ) )
        self.setText(COL_WAIT_GROUP, str( groupid ) )
        self.setEventType( eventType=eventtype )
        if eventtype in [ UCI.SCHED_QUEUE_AT, UCI.SCHED_QUEUE ]:
             self.setText(COL_WAIT_PROJECT, "N/A" )
        else:
            self.setText(COL_WAIT_PROJECT, instance().getProjectName( self.taskProjectId ) )
        if eventtype in [ UCI.SCHED_QUEUE_AT, UCI.SCHED_QUEUE ]:
            self.setText(COL_WAIT_NAME, "N/A" )
        else:
            self.setText(COL_WAIT_NAME, str(eventname))
        if float(eventtime) == 0:
            self.setText(COL_WAIT_NEXT, "N/A" )
        else:
            self.setText(COL_WAIT_NEXT, formatTimestamp( float(eventtime) )  )
        self.setText(COL_WAIT_PROBE, str(not withoutprobes) )
        self.setText(COL_WAIT_NOTIF, str(not withoutnotif) )
        self.setText(COL_WAIT_RESULT, str(not nokeeptr) )
        self.setText(COL_WAIT_AUTHOR, str(author) )
        

        if self.taskEventEnabled:
            self.setIcon(COL_WAIT_ID, QIcon(":/process-add-icon.png") )
        else:
            self.setIcon(COL_WAIT_ID, QIcon(":/process-pause-icon.png") )

    def setRepeat(self):
        """
        Set the number of repeat
        """
        maxRepeat = self.taskEventNb
        if maxRepeat == -1:
            maxRepeat = 'Unlimited'
        self.setText(COL_WAIT_REPEAT, "%s/%s" % ( str(self.taskEventNbCurrent+1), maxRepeat) )

    def setEventType(self, eventType):
        """
        Set the type of the event

        @param eventType: 
        @type eventType:
        """
        index_col = COL_WAIT_TYPE
        ( y, m, d, h, mn, s) = self.taskEventArgs
        if eventType == UCI.SCHED_NOW:
            self.setText(index_col, "Now" )
            self.setText(4, "0" )
        elif eventType in [ UCI.SCHED_QUEUE, UCI.SCHED_QUEUE_AT]:
            self.setText(index_col, "Grouped" )
            self.setText(4, "0" )
        elif eventType == UCI.SCHED_NOW_MORE:
            self.setText(index_col, "Successive" )
            self.setText(4, "0" )
        elif eventType == UCI.SCHED_AT:
            self.setText(index_col, "One time at %s-%s-%s %s:%s:%s" % (y, str(m).zfill(2), str(d).zfill(2), str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2)) )
            self.setText(4, "0" )
        elif eventType == UCI.SCHED_IN:
            self.setText(index_col, "One time in %s sec." % s )
            self.setText(4, "0" )
        elif eventType == UCI.SCHED_EVERY_SEC:
            self.setText(index_col, "Every seconds" )
            self.setRepeat()
        elif eventType == UCI.SCHED_EVERY_MIN:
            self.setText(index_col, "At xx:xx:%s every minutes" % str(s).zfill(2) )
            self.setRepeat()
        elif eventType == UCI.SCHED_HOURLY:
            self.setText(index_col, "At xx:%s:%s every hour" % ( str(mn).zfill(2), str(s).zfill(2)) )
            self.setRepeat()
        elif eventType == UCI.SCHED_DAILY:
            self.setText(index_col, "At %s:%s:%s every day" % ( str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2) ) )
            self.setRepeat()
        elif eventType == SCHED_TYPE_UNDEFINED:
            self.setText(index_col, "Undefined" )
        # BEGIN new schedulation type in 3.1.0
        elif eventType == UCI.SCHED_EVERY_X:
            self.setText(index_col, "Every %sh%sm%ss" % ( str(h).zfill(2), str(mn).zfill(2),  str(s).zfill(2) )  )
            self.setRepeat()
        # END
        # BEGIN new schedulation type in 3.2.0
        elif eventType == UCI.SCHED_WEEKLY:
            weekd = str(d)
            if d in UCI.SCHED_DAYS_DICT:
                weekd = UCI.SCHED_DAYS_DICT[d].title()
            self.setText(index_col, "Weekly on %s at %sh%sm%ss" % ( weekd , str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2) )  )
            self.setRepeat()
        # END
        else:
            self.error( 'unknown event type: %s' % str(eventType) )

COL_HISTORY_ID          = 0
COL_HISTORY_TYPE        = 1
COL_HISTORY_PROJECT     = 2
COL_HISTORY_NAME        = 3
COL_HISTORY_AT          = 4
COL_HISTORY_TIME_START  = 5
COL_HISTORY_TIME_END    = 6
COL_HISTORY_AUTHOR      = 7
COL_HISTORY_DURATION    = 8
COL_HISTORY_RESULT      = 9

class TaskHistoryItem(QTreeWidgetItem, Logger.ClassLogger):
    """
    Treewidget item for history item
    """
    def __init__(self, task, parent = None):
        """
        Constructs TaskItem widget item

        @param task: 
        @type task: list

        @param parent: 
        @type parent:
        """
        QTreeWidgetItem.__init__(self, parent)
        self.taskData = task
        dbid, eventtype, eventargs, eventtime, eventname, author, realruntime, duration, result, projectid  = task
        try:
            self.taskEventArgs = eval(eventargs)
        except Exception as e:
            self.error( "unable to eval event args (%s): %s" % (str(eventargs), str(e)) )
            self.taskEventArgs = (0,0,0,0,0,0)
        self.taskEventType = eventtype
        self.taskEventTime = eventtime
        self.taskEventName = eventname
        self.taskEventAuthor = author
        self.taskEventRealruntime = realruntime
        self.taskEventDuration = duration
        self.taskEventResult = result
        self.taskEventProjectID = projectid
        
        self.setText(COL_HISTORY_ID, str(dbid).zfill(7) ) # id = 6 digits

        self.setText(COL_HISTORY_PROJECT, instance().getProjectName(self.taskEventProjectID) ) 

        self.setEventType( eventType=eventtype )
        self.setText(COL_HISTORY_NAME, str(eventname))
        if float(eventtime) == 0:
            self.setText(COL_HISTORY_AT, "N/A" )
        else:
            self.setText(COL_HISTORY_AT, formatTimestamp( float(eventtime) ) )
        if realruntime == "N/A":
            self.setText(COL_HISTORY_TIME_START, "N/A" )
        elif float(realruntime) == 0:
            self.setText(COL_HISTORY_TIME_START, "N/A" )
        else:
            self.setText(COL_HISTORY_TIME_START, formatTimestamp( float(realruntime) ) )
        if realruntime != "N/A" and duration != "N/A" :
            self.setText(COL_HISTORY_TIME_END, formatTimestamp( float(realruntime)  + float(duration) ) )
        else:
            self.setText(COL_HISTORY_TIME_END, realruntime )
        self.setText(COL_HISTORY_AUTHOR, str(author) )
        if duration != "N/A" :
            self.setText(COL_HISTORY_DURATION, str( round( float(duration), 3) )  )
        else:
            self.setText(COL_HISTORY_DURATION, duration )
        self.setText(COL_HISTORY_RESULT, str(result)  )
        #
        self.setStateIcon( state = str(result) ) 
    
    def setStateIcon(self, state):
        """
        Set the icon of the state

        @param state: 
        @type state:
        """
        if state == STATE_COMPLETE:
            self.setIcon(COL_HISTORY_ID, QIcon(":/process-accept-icon.png") )
        if state == STATE_ERROR:
            self.setIcon(COL_HISTORY_ID, QIcon(":/process-remove-icon.png") )
            for i in xrange(9):
                self.setForeground( i, QBrush( QColor( Qt.red ) ) )
        if state == STATE_CANCELLED:
            self.setIcon(COL_HISTORY_ID, QIcon(":/process-kill-icon.png") )
            for i in xrange(9):
                self.setForeground( i, QBrush( QColor( Qt.darkYellow ) ) )
        if state == STATE_KILLED:
            self.setIcon(COL_HISTORY_ID, QIcon(":/process-kill-icon.png") )
            for i in xrange(9):
                self.setForeground( i, QBrush( QColor( Qt.darkRed ) ) )

    def setEventType(self, eventType):
        """
        Set the type of the event

        @param eventType: 
        @type eventType:
        """
        index_col = COL_HISTORY_TYPE
        ( y, m, d, h, mn, s) = self.taskEventArgs
        if eventType == UCI.SCHED_NOW:
            self.setText(index_col, "Now" )
        elif eventType in [ UCI.SCHED_QUEUE, UCI.SCHED_QUEUE_AT ]:
            self.setText(index_col, "Grouped" )
        elif eventType == UCI.SCHED_NOW_MORE:
            self.setText(index_col, "Successive" )
        elif eventType == UCI.SCHED_AT:
            self.setText(index_col, "One time at %s-%s-%s %s:%s:%s" % (y, str(m).zfill(2), str(d).zfill(2), str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2)) )
        elif eventType == UCI.SCHED_IN:
            self.setText(index_col, "One time in %s sec." % s )
        elif eventType == UCI.SCHED_EVERY_SEC:
            self.setText(index_col, "Every seconds" )
        elif eventType == UCI.SCHED_EVERY_MIN:
            self.setText(index_col, "At xx:xx:%s every minutes" % str(s).zfill(2) )
        elif eventType == UCI.SCHED_HOURLY:
            self.setText(index_col, "At xx:%s:%s every hour" % ( str(mn).zfill(2), str(s).zfill(2)) )
        elif eventType == UCI.SCHED_DAILY:
            self.setText(index_col, "At %s:%s:%s every day" % ( str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2) ) )
        elif eventType == SCHED_TYPE_UNDEFINED:
            self.setText(index_col, "Undefined" )
        # BEGIN new schedulation type in 3.1.0
        elif eventType == UCI.SCHED_EVERY_X:
            self.setText(index_col, "Every %sh%sm%ss" % ( str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2) )  )
        # END
        # BEGIN new schedulation type in 3.2.0
        elif eventType == UCI.SCHED_WEEKLY:
            weekd = str(d)
            if d in UCI.SCHED_DAYS_DICT:
                weekd = UCI.SCHED_DAYS_DICT[d].title()
            self.setText(index_col, "Weekly on %s at %sh%sm%ss" % ( weekd, str(h).zfill(2), str(mn).zfill(2), str(s).zfill(2) )  )
        # END
        else:
            self.error( 'unknown event type: %s' % str(eventType) )



class WTestManager(QWidget, Logger.ClassLogger):
    """
    Widget to display all tests in the scheduler
    """
    def __init__(self, parent):
        """
        Constructs WTestManager widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Task Manager")
        self.ascendingOrder = False
        self.ascendingOrderHistory = False
        self.ascendingOrderWaiting = False
        
        self.itemCurrent = None
        self.projects = []
        self.createWidgets()
        self.createActions()
        self.createConnections()
        self.createActions()
        self.createToolbar()
        self.deactivate()

    def createWidgets (self):
        """
        QtWidgets creation
        
        QTreeWidget (Id, Name, Init at, Sched at, Start at, Stop at, User, Duration)
         _______________
        |    QToolBar   |
        |---------------|
         _______________
        |               |
        |---------------|
        |               |
        |               |
        |_______________|
        """

        #self.mainTab = QTabWidget()


        layout = QVBoxLayout()

        topLayout = QHBoxLayout()

        # waiting tree widget
        self.tabWaiting = QTabWidget()

        #self.waitingBox = QGroupBox("Waiting")
        self.waitingBox = QFrame(self)
        self.testWaiting = QTreeWidget(self)
        self.testWaiting.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.waitingToolbar = QToolBar(self)
        self.labelsWaiting = [ self.tr("No.") , self.tr("Group"), self.tr("Schedulation Type"),
                              self.tr("Project"), self.tr("Name") , self.tr("Next run"), 
                              self.tr("Repeat"), self.tr("Probes"), self.tr("Notifications") , 
                              self.tr("Tests result"), self.tr("Author")  ]
        self.testWaiting.setHeaderLabels(self.labelsWaiting)
        self.testWaiting.setIndentation(10)
        self.testWaiting.setContextMenuPolicy(Qt.CustomContextMenu)
        layoutWaiting = QVBoxLayout()
        layoutWaiting.addWidget(self.waitingToolbar)
        layoutWaiting.addWidget(self.testWaiting)
        self.waitingBox.setLayout(layoutWaiting)

        self.tabWaiting.addTab( self.waitingBox, "Scheduled" )

        self.enqueuedBox = QFrame(self)
        layoutEnqueued = QVBoxLayout()

        self.testEnqueued = QTreeWidget(self)
        self.labelsEnqueued = [ self.tr("Group of tests")  ] 
        self.testEnqueued.setHeaderLabels(self.labelsEnqueued)
        self.testEnqueued.setIndentation(10)

        layoutEnqueued.addWidget(self.testEnqueued)
        self.enqueuedBox.setLayout(layoutEnqueued)
        self.tabWaiting.addTab( self.enqueuedBox, "Waiting" )


        # current tree widget
        self.currentBox = QGroupBox("Running")
        self.testManager = QTreeWidget(self)
        self.testManager.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dockToolbar = QToolBar(self)
        self.labels  = [ self.tr("No."), self.tr("Project"), self.tr("Name"), self.tr("Started at"),
                         self.tr("Author"), self.tr("Recursive") ]
        self.testManager.setHeaderLabels(self.labels)
        self.testManager.setIndentation(10)
        self.testManager.setContextMenuPolicy(Qt.CustomContextMenu)
        layoutCurrent = QVBoxLayout()
        layoutCurrent.addWidget(self.dockToolbar)
        layoutCurrent.addWidget(self.testManager)
        self.currentBox.setLayout(layoutCurrent)
        
        v_splitter = QSplitter(self)      
        v_splitter.addWidget( self.tabWaiting )
        v_splitter.addWidget( self.currentBox ) 
        topLayout.addWidget(v_splitter)

        # history tree widget
        self.historyBox = QGroupBox("History")
        self.testHistory = QTreeWidget(self)
        self.historyToolbar = QToolBar(self)
        self.labels2 = [ self.tr("Id"),  self.tr("Schedulation Type"),  self.tr("Project") , self.tr("Name"), 
                         self.tr("Sched at"), self.tr("Run start"), self.tr("Run end"), self.tr("Author"), 
                         self.tr("Duration (in sec.)"), self.tr("Run Result") ]
        self.testHistory.setHeaderLabels(self.labels2)
        
        self.statsBox = QGroupBox("Summary")
        self.nbRunningLabel = QLabel("0")
        self.nbWaitingLabel = QLabel("0")
        self.nbHistoryLabel = QLabel("0")
        self.nbCompleteHistoryLabel = QLabel("0")
        self.nbErrorHistoryLabel = QLabel("0")
        self.nbKilledHistoryLabel = QLabel("0")
        self.nbCancelledHistoryLabel = QLabel("0")
        layout2 = QFormLayout()
        layout2.addRow(QLabel("Running"), self.nbRunningLabel )
        layout2.addRow(QLabel("Waiting"), self.nbWaitingLabel )
        layout2.addRow( QLabel(""), QLabel("") )
        layout2.addRow(QLabel("History"), self.nbHistoryLabel )
        layout2.addRow(QLabel(" - COMPLETE"), self.nbCompleteHistoryLabel )
        layout2.addRow(QLabel(" - ERROR"), self.nbErrorHistoryLabel )
        layout2.addRow(QLabel(" - KILLED"), self.nbKilledHistoryLabel )
        layout2.addRow(QLabel(" - CANCELLED"), self.nbCancelledHistoryLabel )
        self.statsBox.setLayout(layout2)

        layoutHistory = QVBoxLayout()
        layoutHistory.addWidget(self.historyToolbar)
        layoutHistory.addWidget(self.testHistory)
        self.historyBox.setLayout(layoutHistory)
        
        subLayout = QHBoxLayout()
        subLayout.addWidget(self.historyBox)
        subLayout.addWidget(self.statsBox)

        frame_left = QFrame(self)
        frame_left.setFrameShape(QFrame.NoFrame)
        frame_left.setLayout(topLayout)

        frame_right = QFrame(self)
        frame_right.setFrameShape(QFrame.NoFrame)
        frame_right.setLayout(subLayout)

        topLayout.setContentsMargins(0,0,0,0)
        subLayout.setContentsMargins(0,0,0,0)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(frame_left)
        splitter1.addWidget(frame_right)

        layout.addWidget(splitter1)
        self.setLayout(layout)

    def createConnections(self):
        """
        Create Qt Connections
        """
        self.testWaiting.customContextMenuRequested.connect(self.onPopupMenuWaiting)
        self.testWaiting.currentItemChanged.connect(self.onCurrentWaitingItemChanged)

        self.testManager.customContextMenuRequested.connect(self.onPopupMenu)
        self.testManager.currentItemChanged.connect(self.onCurrentItemChanged)

        self.testWaiting.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def createActions (self):
        """
        Actions defined:
         * sort running task
         * sort waiting task
         * sort history task
         * kill one task
         * kill all tasks
         * cancel one task
         * cancel all task
         * clear the history
         * edit a waiting task
         * refresh waiting tasks
         * refresh running tasks
         * partial refresh of the history
         * complete refresh of the history
         * disable a waiting task
         * enable a waiting task
        """
        self.sortAction = QtHelper.createAction(self, "Ascending Order", self.toggleSort, toggled = True, 
                                icon = QIcon(":/ascending.png") )
        self.sortHistoryAction = QtHelper.createAction(self, "Ascending Order", self.toggleSortHistory, toggled = True, 
                                icon = QIcon(":/ascending.png") )
        self.sortWaitingAction = QtHelper.createAction(self, "Ascending Order", self.toggleSortWaiting, toggled = True, 
                                icon = QIcon(":/ascending.png") )
        self.killAction = QtHelper.createAction(self, "&Kill", self.killTask, tip = 'Kill selected test', 
                                icon = QIcon(":/process-kill.png") )
        self.killAllAction = QtHelper.createAction(self, "&Kill All", self.killAllTasks, tip = 'Kill all running tests', 
                                icon = QIcon(":/process-killall.png") )
        self.cancelAction = QtHelper.createAction(self, "&Cancel", self.cancelTask, tip = 'Cancel selected test', 
                                icon = QIcon(":/process-cancel.png") )
        self.cancelAllAction = QtHelper.createAction(self, "&Cancel All", self.cancelAllTasks, tip = 'Cancel all waiting tests', 
                                icon = QIcon(":/processes-cancelall.png") )
        
        self.clearHistoryAction = QtHelper.createAction(self, "&Clear history", self.clearHistory, tip = 'Clear history', 
                                icon = QIcon(":/trash.png"))
        self.editWaitingAction = QtHelper.createAction(self, "&Edit", self.editWaiting, tip = 'Edit the selected task', 
                                icon = QIcon(":/reschedule.png"))

        self.refreshWaitingAction = QtHelper.createAction(self, "Waiting tasks", self.refreshWaitingList, 
                                icon = QIcon(":/act-refresh.png"), tip="Refresh waiting tasks" )
        self.refreshRunningAction = QtHelper.createAction(self, "Running tasks", self.refreshRunningList, 
                                icon = QIcon(":/act-refresh.png"), tip="Refresh running tasks" )
        self.partialRefreshHistoryAction = QtHelper.createAction(self, "Partial history", self.partialRefreshHistoryList, 
                                icon = QIcon(":/act-half-refresh.png"), tip="Refresh partial history" )
        self.refreshHistoryAction = QtHelper.createAction(self, "Full history", self.refreshHistoryList, 
                                icon = QIcon(":/act-refresh.png"), tip="Refresh full history" )

        self.disableAction = QtHelper.createAction(self, "&Disable", self.disableTask, tip = 'Disable task', 
                                icon = QIcon(":/process-pause-icon.png") )
        self.enableAction = QtHelper.createAction(self, "&Enable", self.enableTask, tip = 'Enable task', 
                                icon = None)

    def createToolbar(self):
        """
        Toolbar creation
            
        ||----------||
        || Kill all ||
        ||----------||
        """
        self.dockToolbar.setObjectName("Test Manager toolbar")
        self.dockToolbar.addAction(self.sortAction)
        self.dockToolbar.addAction(self.refreshRunningAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.killAction)
        self.dockToolbar.addAction(self.killAllAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))
        #
        self.historyToolbar.setObjectName("Test Manager History toolbar")
        self.historyToolbar.addAction(self.sortHistoryAction)
        self.historyToolbar.addAction(self.partialRefreshHistoryAction)
        self.historyToolbar.addAction(self.refreshHistoryAction)
        self.historyToolbar.addSeparator()
        self.historyToolbar.addAction(self.clearHistoryAction)
        self.historyToolbar.setIconSize(QSize(16, 16))
        #
        self.waitingToolbar.setObjectName("Test Manager Waiting toolbar")
        self.waitingToolbar.addAction(self.sortWaitingAction)
        self.waitingToolbar.addAction(self.refreshWaitingAction)
        self.waitingToolbar.addSeparator()
        self.waitingToolbar.addAction(self.editWaitingAction)
        self.waitingToolbar.addAction(self.disableAction)
        self.waitingToolbar.addAction(self.cancelAction)
        self.waitingToolbar.addAction(self.cancelAllAction)
        self.waitingToolbar.addSeparator()
        self.waitingToolbar.setIconSize(QSize(16, 16))

    def onItemDoubleClicked(self, item):
        """
        On item double clicked in waiting task
        """
        if item.taskEventType in [ UCI.SCHED_QUEUE_AT, UCI.SCHED_QUEUE ]:
            pass
        else:
            self.editWaiting()
        
    def getProjectName(self, prjId):
        """
        Return the project name
        """
        pname = "UNKNOWN"
        
        if prjId == 0:
            return "UNDEFINED"

        for p in self.projects:
            if int(p['project_id']) == int(prjId):
                pname = p['name']
                break

        return pname

    def refreshWaitingList(self):
        """
        Refresh the waiting task list
        """
        RCI.instance().waitingTasks()
        
    def refreshRunningList(self):
        """
        Refresh the running task list
        """
        RCI.instance().runningTasks()
        
    def partialRefreshHistoryList(self):
        """
        Partial refresh of the history task list
        """
        RCI.instance().historyTasks()
        
    def refreshHistoryList(self):
        """
        Refresh the history task list
        """
        RCI.instance().historyTasksAll()
        
    def onCurrentItemChanged(self, witem1, witem2):
        """
        On current item changed 

        @param witem1: 
        @type witem1:

        @param witem2: 
        @type witem2:
        """
        # kill task available just for admin and tester
        if UCI.RIGHTS_ADMIN in RCI.instance().userRights  or UCI.RIGHTS_TESTER in RCI.instance().userRights :
            if witem1 is not None:
                if witem1.taskState == STATE_RUNNING :
                    self.itemCurrent = witem1
                    self.killAction.setEnabled(True)
                else:
                    self.killAction.setEnabled(False)

    def onCurrentWaitingItemChanged(self, witem1, witem2):
        """
        On current waiting task item changed

        @param witem1: 
        @type witem1:

        @param witem2: 
        @type witem2:
        """
        # kill task available just for admin and tester
        if UCI.RIGHTS_ADMIN in RCI.instance().userRights or UCI.RIGHTS_TESTER in RCI.instance().userRights :
            if witem1 is not None:
                self.itemCurrent = witem1
                self.cancelAction.setEnabled(True)
                self.editWaitingAction.setEnabled(True)
                self.disableAction.setEnabled(True)
            else:
                self.cancelAction.setEnabled(False)
                self.editWaitingAction.setEnabled(False)
                self.disableAction.setEnabled(False)

    def disableTask(self):
        """
        Disable a waiting task
        """
        # if self.itemCurrent is not None:
        for currentItem in self.testWaiting.selectedItems():
            RCI.instance().rescheduleTask(taskId=currentItem.taskId, taskEnabled=False, 
                                            scheduleType=currentItem.taskEventType,
                                            scheduleAt=currentItem.taskEventArgs, 
                                            scheduleRepeat=currentItem.taskEventNb, 
                                            probesEnabled=currentItem.taskWithoutProbes, 
                                            notificationsEnabled=currentItem.taskWithoutNotif, 
                                            debugEnabled=False, logsEnabled=currentItem.taskNoKeepTr, 
                                            fromTime=currentItem.taskEventFrom, toTime=currentItem.taskEventTo )
                                            
    def enableTask(self):
        """
        Enable a waiting task
        """
        # if self.itemCurrent is not None:
        for currentItem in self.testWaiting.selectedItems():
            RCI.instance().rescheduleTask(taskId=currentItem.taskId, taskEnabled=True, 
                                            scheduleType=currentItem.taskEventType,
                                            scheduleAt=currentItem.taskEventArgs, 
                                            scheduleRepeat=currentItem.taskEventNb, 
                                            probesEnabled=currentItem.taskWithoutProbes, 
                                            notificationsEnabled=currentItem.taskWithoutNotif, 
                                            debugEnabled=False, logsEnabled=currentItem.taskNoKeepTr, 
                                            fromTime=currentItem.taskEventFrom, toTime=currentItem.taskEventTo )
    
    def editWaiting(self):
        """
        Edit a waiting task
        """
        if self.itemCurrent is not None:
            if self.itemCurrent.taskEventType in [ UCI.SCHED_QUEUE_AT, UCI.SCHED_QUEUE ]:
                pass
            else:
                dSched = ScheduleDialog.SchedDialog( self )
                dSched.fillFields( schedType=self.itemCurrent.taskEventType, schedArgs=self.itemCurrent.taskEventArgs,
                                    taskName=self.itemCurrent.taskEventName, taskId=self.itemCurrent.taskId, 
                                    schedNb=self.itemCurrent.taskEventNb, withoutProbes=self.itemCurrent.taskWithoutProbes,
                                    enabled=self.itemCurrent.taskEventEnabled,
                                    withoutNotifs=self.itemCurrent.taskWithoutNotif, noKeepTr=self.itemCurrent.taskNoKeepTr,
                                    schedFrom=self.itemCurrent.taskEventFrom, schedTo=self.itemCurrent.taskEventTo )
                if dSched.exec_() == QDialog.Accepted:
                    runAt, runType, runNb, withoutProbes, runEnabled, noTr, withoutNotifs, runFrom, runTo = dSched.getSchedtime()

                    RCI.instance().rescheduleTask(taskId=self.itemCurrent.taskId, taskEnabled=runEnabled, scheduleType=runType,
                                                    scheduleAt=runAt, scheduleRepeat=runNb, 
                                                    probesEnabled=withoutProbes, notificationsEnabled=withoutNotifs, 
                                                    debugEnabled=False, logsEnabled=noTr, 
                                                    fromTime=runFrom, toTime=runTo )
    def clearHistory(self):
        """
        Call the server to clear the history
        """
        reply = QMessageBox.question(self, "Clear tasks history", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().clearHistory()
            
    def testKilled(self):
        """
        Test kiled
        """
        self.itemCurrent = None
        self.killAction.setEnabled(False)

    def testCancelled(self):
        """
        Test cancelled
        """
        self.itemCurrent = None
        self.cancelAction.setEnabled(False)

    def active (self):
        """
        Enables QTreeWidget 
        """
        self.waitingBox.setEnabled(True)
        self.currentBox.setEnabled(True)
        self.historyBox.setEnabled(True)
        self.statsBox.setEnabled(True)
        #
        self.testManager.setEnabled(True)
        self.testHistory.setEnabled(True)
        self.testWaiting.setEnabled(True)
        #
        self.sortAction.setEnabled(True)
        self.sortHistoryAction.setEnabled(True)
        self.sortWaitingAction.setEnabled(True)
        
        self.refreshWaitingAction.setEnabled(True)
        self.refreshRunningAction.setEnabled(True)
        self.refreshHistoryAction.setEnabled(True)
        self.partialRefreshHistoryAction.setEnabled(True)

        self.killAction.setEnabled(False)
        self.cancelAction.setEnabled(False)
        self.editWaitingAction.setEnabled(False)
        if UCI.RIGHTS_ADMIN in RCI.instance().userRights:
            self.killAllAction.setEnabled(True)
            self.cancelAllAction.setEnabled(True)
            self.clearHistoryAction.setEnabled(True)

        self.disableAction.setEnabled(False)
        self.enableAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.waitingBox.setEnabled(False)
        self.currentBox.setEnabled(False)
        self.historyBox.setEnabled(False)
        self.statsBox.setEnabled(False)
        
        self.testWaiting.clear()
        self.testWaiting.setEnabled(False)
        self.testManager.clear()
        self.testManager.setEnabled(False)
        self.testHistory.clear()
        self.testHistory.setEnabled(False)
        self.testEnqueued.clear()
        self.testHistory.setEnabled(False)

        self.nbRunningLabel.setText("0")
        self.nbWaitingLabel.setText("0")
        self.nbHistoryLabel.setText("0")
        self.nbCompleteHistoryLabel.setText("0")
        self.nbErrorHistoryLabel.setText("0")
        self.nbKilledHistoryLabel.setText("0")
        self.nbCancelledHistoryLabel.setText("0")
        self.itemCurrent = None
        
        self.setDefaultActionsValues()
    
    def setDefaultActionsValues (self):
        """
        Set default values for qt actions
        """
        self.sortAction.setEnabled(False)
        self.sortHistoryAction.setEnabled(False)
        self.sortWaitingAction.setEnabled(False)

        self.killAction.setEnabled(False)
        self.killAllAction.setEnabled(False)

        self.cancelAction.setEnabled(False)
        self.cancelAllAction.setEnabled(False)
        self.editWaitingAction.setEnabled(False)
        self.clearHistoryAction.setEnabled(False)

        self.refreshWaitingAction.setEnabled(False)
        self.refreshRunningAction.setEnabled(False)
        self.refreshHistoryAction.setEnabled(False)
        self.partialRefreshHistoryAction.setEnabled(False)

        self.disableAction.setEnabled(False)
        self.enableAction.setEnabled(False)

    def loadProjects(self, data):
        """
        Load all projects
        """
        self.projects = data

    def loadRunning (self, data):
        """
        Loads running tasks

        @param data: 
        @type data: dict
        """
        self.nbRunningLabel.setText( str( len(data) ) )
        for task in data:
            if self.getProjectName(task['project-id']) == "UNKNOWN":
                continue
            taskItem = TaskRunningItem(  task = task, parent= self.testManager )
        
        # resize cols
        for i in xrange(len(self.labels2) - 1):
            self.testManager.resizeColumnToContents(i)
        
        # change sort order
        if self.ascendingOrder:
            self.testWaiting.sortItems(2, Qt.AscendingOrder)     # sort by sched time
        self.testManager.sortItems(2, Qt.DescendingOrder)

    def updateRunning(self, data):
        """
        Update running tasks

        @param data: 
        @type data: 
        """
        self.testManager.clear()
        self.loadRunning( data=data )

    def loadWaiting (self, data):
        """
        Loads waiting tasks

        @param data: 
        @type data: dict
        """
        self.nbWaitingLabel.setText( str(len(data)) )
        for task in data:
            eventid, eventtype, eventargs, eventtime, eventname, author, realruntime, duration, result, eventnb, \
            eventnbcur, eventenabled, withoutprobes, withoutnotif, nokeeptr, userid, projectid, eventfrom, eventto, groupid  = task
            if self.getProjectName(projectid) == "UNKNOWN":
                continue
            taskItem = TaskWaitingItem(  task = task, parent= self.testWaiting )
        
        # resize cols
        for i in xrange(len(self.labels2) - 1):
            self.testWaiting.resizeColumnToContents(i)
        
        # change sort order
        if self.ascendingOrderHistory:
            self.testWaiting.sortItems(3, Qt.AscendingOrder)     
        self.testWaiting.sortItems(3, Qt.DescendingOrder)

    def updateWaiting(self, data):
        """
        Update waiting tasks

        @param data: 
        @type data: 
        """
        self.testWaiting.clear()
        self.loadWaiting( data=data )

    def loadEnqueued (self, data):
        """
        Loads enqueued tasks

        @param data: 
        @type data: dict
        """
        for (groupId, groupData) in data.items():
            groupName, groupsTests = groupData

            pluriel = ''
            if len(groupsTests) > 1:
                pluriel = ''
            groupTask = TaskEnqueuedItem( parent=self.testEnqueued, text="%s - %s - (%s test%s)" % (groupId, groupName, len(groupsTests), pluriel) )
            groupTask.setExpanded(True)
            for gTest in groupsTests:
                tDict = eval(gTest)
                tst = "%s:%s.%s" % ( self.getProjectName(tDict['prj-id']), tDict['test-path'], tDict['test-extension'])
                
                # set the icon according to the type of test
                if tDict['test-extension'] == 'tux':
                    testIcon = QIcon(":/tux.png")
                if tDict['test-extension'] == 'tax':
                    testIcon = QIcon(":/tax.png")
                if tDict['test-extension'] == 'tsx':
                    testIcon = QIcon(":/tsx.png")
                if tDict['test-extension'] == 'tpx':
                    testIcon = QIcon(":/tpx.png")
                if tDict['test-extension'] == 'tgx':
                    testIcon = QIcon(":/tgx.png")
                subTask = TaskEnqueuedItem(parent=groupTask, text=tst, icon=testIcon)

    def updateEnqueued(self, data):
        """
        Update enqueued tasks

        @param data: 
        @type data: 
        """
        self.testEnqueued.clear()
        self.loadEnqueued( data=data )

    def loadHistory (self, data):
        """
        Loads history tasks

        @param data: 
        @type data: dict
        """
        # Init counters
        nbComplete = int(self.nbCompleteHistoryLabel.text())
        nbError = int(self.nbErrorHistoryLabel.text())
        nbKilled = int(self.nbKilledHistoryLabel.text())
        nbCancelled = int(self.nbCancelledHistoryLabel.text())

        for task in data:
            dbid, eventtype, eventargs, eventtime, eventname, author, realruntime, duration, result, projectid  = task
            if self.getProjectName(projectid) == "UNKNOWN":
                continue
            taskItem = TaskHistoryItem(  task = task, parent= self.testHistory )
            if taskItem.taskEventResult == STATE_COMPLETE:
                nbComplete += 1
            if taskItem.taskEventResult == STATE_ERROR:
                nbError += 1
            if taskItem.taskEventResult == STATE_KILLED:
                nbKilled += 1
            if taskItem.taskEventResult == STATE_CANCELLED:
                nbCancelled += 1

        # resize cols
        for i in xrange(len(self.labels2) - 1):
            self.testHistory.resizeColumnToContents(i)
        
        # change sort order by sched at
        if self.ascendingOrderHistory:
            self.testHistory.sortItems(0, Qt.AscendingOrder)     
        self.testHistory.sortItems(0, Qt.DescendingOrder)
        
        # Update summary
        nbHistory = int(self.nbHistoryLabel.text())
        self.nbHistoryLabel.setText( str( len(data) + nbHistory ) )
        self.nbCompleteHistoryLabel.setText( str(nbComplete) )
        self.nbErrorHistoryLabel.setText( str(nbError) )
        self.nbKilledHistoryLabel.setText( str(nbKilled) )
        self.nbCancelledHistoryLabel.setText( str(nbCancelled) )

    def updateHistory(self, data):
        """
        Update history tasks

        @param data: 
        @type data: 
        """
        # reset counters
        self.nbHistoryLabel.setText("0")
        self.nbCompleteHistoryLabel.setText("0")
        self.nbErrorHistoryLabel.setText("0")
        self.nbKilledHistoryLabel.setText("0")
        self.nbCancelledHistoryLabel.setText("0")
        #
        self.testHistory.clear()
        self.loadHistory( data=data )
    
    def refreshRunningTask(self, data, action):
        """
        Refresh running task

        @param data: 
        @type data: 

        @param action: 
        @type action: 
        """
        if action == "add":
            self.loadRunning(data=data)
        elif action == "update":
            self.updateRunning(data=data)
        else:
            pass # error

    def refreshWaitingTask(self, data, action):
        """
        Refresh waiting task

        @param data: 
        @type data: 

        @param action: 
        @type action: 
        """
        if action == "update":
            self.updateWaiting(data=data)
        else:
            pass # error

    def refreshEnqueuedTask(self, data, action):
        """
        Refresh enqueued task

        @param data: 
        @type data: 

        @param action: 
        @type action: 
        """
        if action == "update":
            self.updateEnqueued(data=data)
        else:
            pass # error

    def refreshHistoryTask(self, data, action):
        """
        Refresh history task

        @param data: 
        @type data: 

        @param action: 
        @type action: 
        """
        if action == "add":
            self.loadHistory(data=data)
        elif action == "update":
            self.updateHistory(data=data)
        else:
            pass # error

    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.testManager.itemAt(pos)
        if item:
            self.itemCurrent = item
            # kill task available just for admin and tester
            if UCI.RIGHTS_ADMIN in RCI.instance().userRights or UCI.RIGHTS_TESTER in RCI.instance().userRights :
                if item.taskState == STATE_RUNNING :
                    self.menu.addAction( self.killAction )
                self.menu.popup(self.testManager.mapToGlobal(pos))

    def onPopupMenuWaiting(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        item = self.testWaiting.itemAt(pos)
        if item:
            self.itemCurrent = item
            # kill task available just for admin and tester
            if UCI.RIGHTS_ADMIN in RCI.instance().userRights or UCI.RIGHTS_TESTER in RCI.instance().userRights :
                self.menu.addAction( self.editWaitingAction )
                self.menu.addAction( self.cancelAction )
                self.menu.addSeparator()
                self.menu.addAction( self.disableAction )
                self.menu.addAction( self.enableAction )
                self.menu.popup(self.testWaiting.mapToGlobal(pos))

    def cancelTask(self):
        """
        Cancel the selected task
        """
        items = self.testWaiting.selectedItems()
        taskIds = []
        for itm in items:
            taskIds.append( itm.taskId )
        
        reply = QMessageBox.question(self, "Cancel test(s)", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().cancelTasks(taskIds=taskIds)
            
    def cancelAllTasks(self):
        """
        Cancel all tasks
        """
        reply = QMessageBox.question(self, "Cancel all tests", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().cancelTasksAll()
            
    def killTask(self):
        """
        Kill the selected task
        """
        items = self.testManager.selectedItems()
        taskIds = []
        for itm in items:
            taskIds.append( itm.taskId )
            
        reply = QMessageBox.question(self, "Kill test", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().killTasks(taskIds=taskIds)
            
    def killAllTasks(self):
        """
        Kill all tasks
        """
        reply = QMessageBox.question(self, "Kill all tests", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().killTasksAll()
    
    def toggleSort(self):
        """
        Toggle sort of running task
        """
        if not self.ascendingOrder:
            self.testManager.sortItems(2, Qt.AscendingOrder)
            self.ascendingOrder = True
        else:
            self.testManager.sortItems(2, Qt.DescendingOrder)
            self.ascendingOrder = False

    def toggleSortHistory(self):
        """
        Toggle sort of the history
        """
        if not self.ascendingOrderHistory:
            self.testHistory.sortItems(0, Qt.AscendingOrder)
            self.ascendingOrderHistory = True
        else:
            self.testHistory.sortItems(0, Qt.DescendingOrder)
            self.ascendingOrderHistory = False

    def toggleSortWaiting(self):
        """
        Toggle sort of the waiting 
        """
        if not self.ascendingOrderWaiting:
            self.testWaiting.sortItems(3, Qt.AscendingOrder)
            self.ascendingOrderWaiting = True
        else:
            self.testWaiting.sortItems(3, Qt.DescendingOrder)
            self.ascendingOrderWaiting = False



TM = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return TM

def initialize (parent):
    """
    Initialize WTestManager widget
    """
    global TM
    TM = WTestManager(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global TM
    if TM:
        TM = None