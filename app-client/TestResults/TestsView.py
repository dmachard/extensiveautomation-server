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
Module to display tests
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QTreeWidgetItem, QIcon, QWidget, QPushButton, QVBoxLayout, QLabel, 
                            QLineEdit, QHBoxLayout, QTreeWidget, QToolBar, QFrame, QFormLayout, 
                            QGridLayout, QGroupBox, QComboBox, QCheckBox, QTabWidget, QProgressBar, 
                            QMenu, QDialog, QBrush, QColor, QMovie, QSizePolicy, QPixmap)
    from PyQt4.QtCore import (QTimer, QSize, pyqtSignal, Qt, QRect, QRegExp)
except ImportError:
    from PyQt5.QtGui import (QIcon, QBrush, QColor, QMovie, QPixmap )
    from PyQt5.QtWidgets import (QTreeWidgetItem, QWidget, QPushButton, QVBoxLayout, 
                                QLabel, QLineEdit, QHBoxLayout, QTreeWidget, QToolBar, QFrame, 
                                QFormLayout, QGridLayout, QGroupBox, QComboBox, QCheckBox,
                                QTabWidget, QProgressBar, QMenu, QDialog, QSizePolicy)
    from PyQt5.QtCore import (QTimer, QSize, pyqtSignal, Qt, QRect, QRegExp)
    
from Libs import QtHelper, Logger

import Settings
try:
    import ExportStatistics
except ImportError:
    from . import ExportStatistics
    
import UserClientInterface as UCI

COL_ID            = 1
COL_NAME          = 0
COL_DURATION      = 2

TAB_SUMMARY_POS     = 0
TAB_OPTIONS_POS     = 1
TAB_PAUSE_POS       = 2
TAB_BREAKPOINT_POS  = 3
TAB_INTERACT_POS    = 4

class LabelMovie(QWidget):
    """
    Label movie widget
    """
    def __init__(self, parent, testcaseName, running=False):
        """
        Constructor
        """
        QWidget.__init__(self, parent)
        self.testcaseName = testcaseName
        self.isRunning = running
        
        self.createWidgets()

        #if self.isRunning: 
        self.startMovie()

    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QHBoxLayout()

        self.labelPass = QLabel()
        pixmap =  QPixmap(":/ok.png")
        self.labelPass.setPixmap( pixmap.scaledToHeight(16) )
        self.labelPass.hide()
        
        self.labelFail = QLabel()
        pixmap =  QPixmap(":/ko.png")
        self.labelFail.setPixmap( pixmap.scaledToHeight(16) )
        self.labelFail.hide()
        
        self.labelUndef = QLabel()
        pixmap =  QPixmap(":/kill.png")
        self.labelUndef.setPixmap( pixmap.scaledToHeight(16) )
        self.labelUndef.hide()
        
        self.labelMovie = QLabel()
        self.labelText = QLabel(self.testcaseName)
        self.labelText.setToolTip(self.testcaseName)
        self.labelText.setAlignment(Qt.AlignLeft)

        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)
        self.labelText.setSizePolicy (policy)
        
        self.movie = QMovie(":/loading.gif") 
        self.labelMovie.setMovie( self.movie )
        
        layout.addWidget(self.labelMovie)
        layout.addWidget(self.labelPass)
        layout.addWidget(self.labelFail)
        layout.addWidget(self.labelUndef)
        layout.addWidget(self.labelText)
        
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
    def startMovie(self):
        """
        Start the movie icon
        """
        self.movie.start()
        
    def setPASS(self):
        """
        Set the result icon as pass
        """
        self.labelText.setStyleSheet('color: darkGreen')
        # hide the loading movie
        self.movie.stop()
        self.labelMovie.hide()
        # show the pass icon
        self.labelPass.show()
        self.labelFail.hide()
        self.labelUndef.hide()
        
        self.isRunning = False
        
    def setFAIL(self):
        """
        Set the icon as fail
        """
        self.labelText.setStyleSheet('color: red')
        self.movie.stop()
        self.labelMovie.hide()
        self.labelFail.show()
        self.labelUndef.hide()
        
        self.isRunning = False
        
    def setUNDEF(self):
        """
        Set undef
        """
        self.labelText.setStyleSheet('color: black')
        self.movie.stop()
        self.labelMovie.hide()
        self.labelFail.hide()
        self.labelUndef.show()
        
        self.isRunning = False
        
class TestItem(QTreeWidgetItem):
    """
    Test item
    """
    def __init__(self, testName, testId, parent = None, typeItem = 'testsuite', internalId='',
                    startIndex=0, stopIndex=0):
        """
        Constructs TestItem widget item

        @param testName:
        @type testName: 

        @param testId:
        @type testId: 

        @param parent:
        @type parent: 

        @param typeItem:
        @type typeItem:
        """
        QTreeWidgetItem.__init__(self, parent)
        
        self.owner = parent
        
        if len(internalId):
            self.setText(COL_ID, "%s" % internalId.zfill(3))
        self.setText(COL_NAME, testName)
        self.setToolTip(COL_NAME, testName)
        self.testId = testId
        
        # new in v11.2
        self.testName = testName
        self.startIndex = startIndex
        self.stopIndex = stopIndex
        self.dataLoaded = False
        self.result="UNDEFINED"
        # end of new 
        
        if typeItem == 'testunit':
            self.setIcon(COL_NAME, QIcon(":/tux.png") )
        elif typeItem == 'testabstract':
            self.setIcon(COL_NAME, QIcon(":/tax.png") )
        elif typeItem == 'testsuite':
            self.setIcon(COL_NAME, QIcon(":/tsx.png") )
        elif typeItem == 'testplan':
            self.setIcon(COL_NAME, QIcon(":/tpx.png") )
        elif typeItem == 'testglobal':
            self.setIcon(COL_NAME, QIcon(":/tgx.png") )
        else:
            pass

        self.typeItem = typeItem

    def setResult(self, result):
        """
        Set the result
        """
        self.result = result
        
    def getResult(self):
        """
        Return the result
        """
        return self.result
        
    def setDuration(self, duration):
        """
        Set the duration
        """
        self.setText(COL_DURATION, "%s" % duration)
        
    def setTooltipDuration(self, duration):
        """
        Set the duration
        """
        self.setToolTip(COL_NAME, "%s - %s sec." % (self.testName, duration))

class InteractWidget(QWidget):
    """
    Interact dialog
    """
    def __init__(self, parent):
        """
        Interact dialog

        @param parent:
        @type parent:
        """
        super(InteractWidget, self).__init__(parent)
        self.__parent = parent

        self.start_time = 0
        self.timer = QTimer(self)

        self.createWidgets()
        self.createConnections()

    def createWidgets(self):
        """
        Create qt widgets

        @param filename:
        @type filename:
        """
        self.setWindowTitle('Interact ...')
        self.userResponse = None

        self.acceptButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        layout = QVBoxLayout()

        self.labelAsk = QLabel( )
        self.labelCount = QLabel( )
        layout.addWidget( self.labelAsk )
        layout.addWidget( self.labelCount )

        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.acceptButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
  
    def setDefaultValue(self, default):
        """
        Set the default value
        """
        self.lineEdit.setText(default)
		
    def interactInfo(self, ask, counter):
        """
        Set interact info
        """
        if sys.version_info > (3,): # python3 support
            self.labelAsk.setText( ask )
        else:
            self.labelAsk.setText( unicode(ask.toLatin1(), 'utf-8') )
        self.labelCount.setText("Time left to answer: %s s" % str(counter))
        self.lineEdit.setText("")
        self.start_time = counter
        
    def startCounter(self):
        """
        Starts the counter
        """
        self.timer.start(1000)

    def setTid(self, tid):
        """
        Set the transaction id
        """
        self.__tid = tid

    def createConnections(self):
        """
        Create qt connections
        """
        self.acceptButton.clicked.connect(self.onInteract)
        self.cancelButton.clicked.connect(self.onCancel)
        self.timer.timeout.connect(self.updateCounter)
        self.lineEdit.returnPressed.connect(self.acceptButton.click)

    def updateCounter(self):
        """
        Update the counter
        """
        self.start_time -= 1
        if self.start_time >= 0:
            self.labelCount.setText( "Time left to answer: %s s" %  str(self.start_time) )
        else:
            self.timer.stop()

    def onInteract(self):
        """
        On button accept clicked
        """
        self.__parent.deactiveBreakpoint()
        self.__parent.deactivePause()
        self.__parent.deactiveInteract()

        rsp = unicode(self.lineEdit.text())
        UCI.instance().ok(tid=self.__tid, body=rsp )

    def onCancel(self):
        """
        On cancel
        """
        pass
        
class BreakPointWidget(QWidget):
    """
    BreakPoint widget
    """
    def __init__(self, parent):
        """
        Constructor for the widget

        @param parent:
        @type parent:
        """
        super(BreakPointWidget, self).__init__(parent)

        self.__tid = 0
        self.__parent = parent

        self.createWidgets()
        self.createConnections()

    def createWidgets(self):
        """
        Create qt widgets

        @param filename:
        @type filename:
        """
        layout = QVBoxLayout()

        self.runButton = QPushButton("Continue")
        self.runButton.setIcon(QIcon(':/test-play.png'))
        self.runButton.setIconSize(QSize(24,24))
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setIcon(QIcon(':/test-close-black.png'))
        self.cancelButton.setIconSize(QSize(24,24))

        textMsg = ["Breakpoint detected on test, continue ?"]
        textMsg.append("")

        self.labelText = QLabel('\r\n'.join(textMsg))
        layout.addWidget( self.labelText )

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.runButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def createConnections(self):
        """
        Create qt connections
        """
        self.runButton.clicked.connect(self.onContinue)
        self.cancelButton.clicked.connect(self.onCancel)

    def setTid(self, tid):
        """
        Set the transaction id
        """
        self.__tid = tid

    def onContinue(self):
        """
        On continue
        """
        self.__parent.deactiveBreakpoint()
        self.__parent.deactivePause()
        self.__parent.deactiveInteract()
        UCI.instance().ok(tid=self.__tid, body='continue' )

    def onCancel(self):
        """
        On cancel
        """
        self.__parent.deactiveBreakpoint()
        self.__parent.deactivePause()
        self.__parent.deactiveInteract()
        UCI.instance().ok(tid=self.__tid, body='cancel' )

class PauseWidget(QWidget, Logger.ClassLogger):
    """
    Pause widget
    """
    def __init__(self, parent):
        """
        Constructor for the widget

        @param parent:
        @type parent:
        """
        super(PauseWidget, self).__init__(parent)
        self.__parent = parent
        
        self.createWidgets()
        self.createConnections()
        
    def setTid(self, tid):
        """
        Set the transaction id
        """
        self.__tid = tid
        
    def createWidgets(self):
        """
        Create qt widgets

        @param filename:
        @type filename:
        """
        layout = QVBoxLayout()

        self.runButton = QPushButton("Run-It")
        self.runButton.setIcon(QIcon(':/test-play.png'))
        self.runButton.setIconSize(QSize(24,24))
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setIcon(QIcon(':/test-close-black.png'))
        self.cancelButton.setIconSize(QSize(24,24))

        self.labelText = QLabel()
        layout.addWidget( self.labelText )

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.runButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def createConnections(self):
        """
        Create qt connections
        """
        self.runButton.clicked.connect(self.onStepRun)
        self.cancelButton.clicked.connect(self.onStepCancel)

    def setStepInfo(self, stepId, stepSummary):
        """
        Set step 
        """
        textMsg = [""]
        textMsg.append("Test paused, click on run-it to continue")
        textMsg.append("")
        if sys.version_info > (3,): # py3 support
            textMsg.append("Step %s: %s" % (stepId, stepSummary ) )
        else:
            textMsg.append("Step %s: %s" % (stepId,unicode(stepSummary.toLatin1(), 'utf-8') ) )
        textMsg.append("")

        self.labelText.setText('\r\n'.join(textMsg))
        
    def onStepRun(self):
        """
        On step run
        """
        self.__parent.deactiveBreakpoint()
        self.__parent.deactivePause()
        self.__parent.deactiveInteract()
        UCI.instance().ok(tid=self.__tid, body='run' )

    def onStepCancel(self):
        """
        On step cancel
        """
        self.__parent.deactiveBreakpoint()
        self.__parent.deactivePause()
        self.__parent.deactiveInteract()
        UCI.instance().ok(tid=self.__tid, body='cancel' )

class LogsTreeWidget(QTreeWidget):
    """
    Logs tree widget
    """
    KeyUpDownPressed = pyqtSignal()
    def __init__(self, parent):
        """
        Constructor
        """
        QTreeWidget.__init__(self, parent)
        
    def keyPressEvent(self, event):
        """
        On key press event
        """
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            QTreeWidget.keyPressEvent(self, event)
            self.KeyUpDownPressed.emit()
        else:
            QTreeWidget.keyPressEvent(self, event)

            
class TestsView(QWidget):
    """
    Tests view widget
    """
    PASS = "PASS"
    FAIL = "FAIL"
    ExportVerdict = pyqtSignal()
    ExportReport = pyqtSignal()
    ExportDesign = pyqtSignal()
    AddPostTest = pyqtSignal()
    KillTest = pyqtSignal()
    ReplayTest = pyqtSignal()
    CloseTest = pyqtSignal()
    LoadTest = pyqtSignal(str, str)
    LoadNext = pyqtSignal()
    # new in v12.1
    ActiveScrollingEventLogs = pyqtSignal()
    DisableScrollingEventLogs = pyqtSignal()
    ActiveScrollingDiagram = pyqtSignal()
    DisableScrollingDiagram = pyqtSignal()
    HideResumeView = pyqtSignal()
    ShowResumeView = pyqtSignal()
    RegExpUpdated = pyqtSignal(object)
    FilterColumnUpdated = pyqtSignal(int)
    # new in v16
    TestName = pyqtSignal(str)
    def __init__(self, parent, local):
        """
        Constructs TestsItem widget

        @param parent:
        @type parent: 
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.logs = None
        self.isKilled = False
        
        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.createToolbars()

        self.nbOk = 0
        self.nbKo = 0
        self.nbUnd = 0
        self.parentLogs = self.logs

        self.nb_min_avg_max_ts = []
        self.nb_min_avg_max_tc = []
        self.nb_min_avg_max_tu = []
        self.nb_min_avg_max_ta = []
        self.nb_min_avg_max_tp = []
        self.nb_min_avg_max_tg = []

        self.local = local

    def createActions(self):
        """
        QtActions creation:
         * close
        """
        self.closeResultAction = QtHelper.createAction(self, "&Close Result", self.closeTest, 
                                    icon = QIcon(":/test-close.png"))
        self.replayAction = QtHelper.createAction(self, "&Replay", self.replayTest, 
                                    icon = QIcon(":/test-replay.png") )
        self.killAction = QtHelper.createAction(self, "&Kill", self.killTest, 
                                    icon = QIcon(":/test-stop.png") )
        self.addCommentAction = QtHelper.createAction(self, "&Comment", self.addComment, 
                                    icon = QIcon(":/add_comment.png") )
        self.exportVerdictAction = QtHelper.createAction(self, "&Verdict", self.exportVerdict, 
                                    icon = QIcon(":/tvr.png") )
        self.exportReportAction = QtHelper.createAction(self, "&Report", self.exportReport, 
                                    icon = QIcon(":/trp.png") )
        self.exportDesignAction = QtHelper.createAction(self, "&Design", self.exportDesign, 
                                    icon = QIcon(":/tds.png") )
        self.exportStatisticsAction = QtHelper.createAction(self, "&Statistics", self.exportStatistics, 
                                    icon = QIcon(":/tst.png") )

        self.setDefaultActions()
        
        self.expandAllAction = QtHelper.createAction(self, "&Expand All...", self.expandAllItems, 
                                    icon = None, tip = 'Expand all items' )
        self.collapseAllAction = QtHelper.createAction(self, "&Collapse All...", self.collapseAllItems, 
                                    icon = QIcon(":/collapse.png"), tip = 'Collapse all items' )

    def setDefaultActions(self):
        """
        Set the default actions
        """
        self.replayAction.setEnabled( False )       
        self.killAction.setEnabled( False )
        self.addCommentAction.setEnabled( False )
        self.exportVerdictAction.setEnabled( False )
        self.exportReportAction.setEnabled( False )
        self.exportDesignAction.setEnabled( False )
        self.exportStatisticsAction.setEnabled( False )

    def createWidgets (self):
        """
        QtWidgets creation
        
         QToolBar
         _______
        |       |
        | Close |
        |_______|

         QGroupBox
         _______________
        |               |
        | QLabel QLabel |
        | QLabel QLabel |
        | QLabel QLabel |
        |    QFrame     |
        | QLabel QLabel |
        |_______________|
         _______________
        |               |
        |               |
        |  QTreeWidget  |
        |               |
        |_______________|
        """
        layout = QVBoxLayout()

        self.toolbar = QToolBar(self)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbarExports = QToolBar(self)
        self.toolbarExports.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.toolbarExports.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.controlsBox = QGroupBox("Controls")
        self.controlsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutControls = QHBoxLayout()
        layoutControls.addWidget(self.toolbar)
        layoutControls.setContentsMargins(0,0,0,0)
        self.controlsBox.setLayout(layoutControls)
        
        self.exportsBox = QGroupBox("Exports")
        self.exportsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutExports = QHBoxLayout()
        layoutExports.addWidget(self.toolbarExports)
        layoutExports.setContentsMargins(0,0,0,0)
        self.exportsBox.setLayout(layoutExports)
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.controlsBox)
        layoutToolbars.addWidget(self.exportsBox)
        layoutToolbars.addStretch(1)
        
        layout.addLayout(layoutToolbars)

        self.nbOkLabel = QLabel()
        self.nbKoLabel = QLabel()
        self.nbUndLabel = QLabel()
        self.nbTotLabel = QLabel()
        
        self.line = QFrame()
        self.line.setGeometry(QRect(110, 221, 51, 20))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        layoutSummary = QFormLayout()
        layoutSummary.addRow(QLabel(""), QLabel("") )
        layoutSummary.addRow(QLabel("OK"), self.nbOkLabel )
        layoutSummary.addRow(QLabel("KO"), self.nbKoLabel )
        layoutSummary.addRow(QLabel("UNDEFINED"), self.nbUndLabel )
        layoutSummary.addRow(self.line )
        layoutSummary.addRow(QLabel("TOTAL"), self.nbTotLabel )

        layoutStats = QHBoxLayout()
        
        self.nb_TaLabel = QLabel("0")
        self.min_TaLabel = QLabel("0.000")
        self.avg_TaLabel = QLabel("0.000")
        self.max_TaLabel = QLabel("0.000")
        
        self.nb_TuLabel = QLabel("0")
        self.min_TuLabel = QLabel("0.000")
        self.avg_TuLabel = QLabel("0.000")
        self.max_TuLabel = QLabel("0.000")

        self.nb_TsLabel = QLabel("0")
        self.min_TsLabel = QLabel("0.000") 
        self.avg_TsLabel = QLabel("0.000")
        self.max_TsLabel = QLabel("0.000")

        self.nb_TcLabel = QLabel("0")
        self.min_TcLabel = QLabel("0.000")
        self.avg_TcLabel = QLabel("0.000")
        self.max_TcLabel = QLabel("0.000")

        self.nb_TpLabel = QLabel("0")
        self.min_TpLabel = QLabel("0.000")
        self.avg_TpLabel = QLabel("0.000")
        self.max_TpLabel = QLabel("0.000")

        self.nb_TgLabel = QLabel("0")
        self.min_TgLabel = QLabel("0.000")
        self.avg_TgLabel = QLabel("0.000")
        self.max_TgLabel = QLabel("0.000")


        layoutStats = QGridLayout() 
        layoutStats.addWidget(QLabel(), 0, 0 )
        layoutStats.addWidget(QLabel("NB"), 0, 1 )
        layoutStats.addWidget(QLabel("MIN"), 0, 2 )
        layoutStats.addWidget(QLabel("AVG"), 0, 3 )
        layoutStats.addWidget(QLabel("MAX"), 0, 4 )

        layoutStats.addWidget(QLabel("TESTCASE"), 1, 0 )
        layoutStats.addWidget(self.nb_TcLabel, 1, 1 )
        layoutStats.addWidget(self.min_TcLabel, 1, 2 )
        layoutStats.addWidget(self.avg_TcLabel, 1, 3 )
        layoutStats.addWidget(self.max_TcLabel, 1, 4 )

        layoutStats.addWidget(QLabel("TESTABSTRACT"), 2, 0 )
        layoutStats.addWidget(self.nb_TaLabel, 2, 1 )
        layoutStats.addWidget(self.min_TaLabel, 2, 2 )
        layoutStats.addWidget(self.avg_TaLabel, 2, 3 )
        layoutStats.addWidget(self.max_TaLabel, 2, 4 )
        
        layoutStats.addWidget(QLabel("TESTUNIT"), 3, 0 )
        layoutStats.addWidget(self.nb_TuLabel, 3, 1 )
        layoutStats.addWidget(self.min_TuLabel, 3, 2 )
        layoutStats.addWidget(self.avg_TuLabel, 3, 3 )
        layoutStats.addWidget(self.max_TuLabel, 3, 4 )

        layoutStats.addWidget(QLabel("TESTSUITE"), 4, 0 )
        layoutStats.addWidget(self.nb_TsLabel, 4, 1 )
        layoutStats.addWidget(self.min_TsLabel, 4, 2 )
        layoutStats.addWidget(self.avg_TsLabel, 4, 3 )
        layoutStats.addWidget(self.max_TsLabel, 4, 4 )

        layoutStats.addWidget(QLabel("TESTPLAN"), 5, 0 )
        layoutStats.addWidget(self.nb_TpLabel, 5, 1 )
        layoutStats.addWidget(self.min_TpLabel, 5, 2 )
        layoutStats.addWidget(self.avg_TpLabel, 5, 3 )
        layoutStats.addWidget(self.max_TpLabel, 5, 4 )

        layoutStats.addWidget(QLabel("TESTGLOBAL"), 6, 0 )
        layoutStats.addWidget(self.nb_TgLabel, 6, 1 )
        layoutStats.addWidget(self.min_TgLabel, 6, 2 )
        layoutStats.addWidget(self.avg_TgLabel, 6, 3 )
        layoutStats.addWidget(self.max_TgLabel, 6, 4 )

        layoutStatsFinal = QHBoxLayout()
        layoutStatsFinal.addLayout(layoutSummary) 
        layoutStatsFinal.addLayout(layoutStats) 

        self.filterBox = QGroupBox("Events Filter")
        layoutV = QVBoxLayout()
        layoutV.addWidget(self.filterBox)

        layoutFilter = QFormLayout()

        self.filterColumnComboBox = QComboBox(self)
        self.filterColumnComboBox.addItem("No.")
        self.filterColumnComboBox.addItem("Timestamp")
        self.filterColumnComboBox.addItem("From")
        self.filterColumnComboBox.addItem("To")
        self.filterColumnComboBox.addItem("Event Type")
        self.filterColumnComboBox.addItem("Component Type")
        self.filterColumnComboBox.addItem("Text")
        self.filterColumnLabel = QLabel("&Column:")

        self.filterPatternLineEdit = QComboBox()
        self.filterPatternLineEdit.setEditable(1)
        
        self.filterSyntaxComboBox = QComboBox()
        self.filterSyntaxComboBox.addItem("Regular expression",  QRegExp.RegExp)
        self.filterSyntaxComboBox.addItem("Wildcard", QRegExp.Wildcard)
        self.filterSyntaxComboBox.addItem("Fixed string", QRegExp.FixedString)
        self.filterSyntaxLabel = QLabel("Filter &syntax:")

        self.filterCaseSensitivityCheckBox = QCheckBox("Case sensitive filter")

        layoutFilter.addRow(QLabel("Pattern:"), self.filterPatternLineEdit)
        layoutFilter.addRow(QLabel("Syntax:"), self.filterSyntaxComboBox)
        layoutFilter.addRow(QLabel("Column:"), self.filterColumnComboBox)
        layoutFilter.addRow( QLabel("") , self.filterCaseSensitivityCheckBox)

        self.filterBox.setLayout(layoutFilter)

        self.logs = LogsTreeWidget(self)
        self.logs.setHeaderHidden(False)
        self.logs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labels = [  self.tr("Name"), self.tr("Id"), self.tr("Time (sec.)") ]
        self.logs.setHeaderLabels(self.labels)
        self.logs.setColumnWidth(COL_NAME, 240)
        self.logs.setColumnWidth(COL_ID, 25)
        self.logs.setColumnWidth(COL_DURATION, 30)
        self.logs.setMinimumWidth( 350 )
        self.logs.header().moveSection(0, COL_ID)

        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-scrolling-tests' ) ):
            self.logs.model().rowsInserted.connect(self.autoScroll)

        # options
        self.hideResumeViewCheckBox = QCheckBox('Hide resume view')
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/hide-resume-view' ) ):
            self.hideResumeViewCheckBox.setChecked(True)
        self.autoscrollTestLogsCheckBox = QCheckBox('Autoscrolling on tests logs')
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-scrolling-tests' ) ):
            self.autoscrollTestLogsCheckBox.setChecked(True)
        self.autoscrollEventsViewCheckBox = QCheckBox('Autoscrolling on events logs')
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-scrolling-textual' ) ):
            self.autoscrollEventsViewCheckBox.setChecked(True)

        self.autoscrollDiagramViewCheckBox = QCheckBox('Autoscrolling on diagram')
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-scrolling-graph' ) ):
            self.autoscrollDiagramViewCheckBox.setChecked(True)

        layoutOptions = QVBoxLayout()
        layoutOptions.addWidget(self.hideResumeViewCheckBox)
        layoutOptions.addWidget(self.autoscrollTestLogsCheckBox)
        layoutOptions.addWidget(self.autoscrollEventsViewCheckBox)
        layoutOptions.addWidget(self.autoscrollDiagramViewCheckBox)

        self.optionsWidget = QWidget(self)
        self.optionsWidget.setLayout(layoutOptions)


        self.summaryWidget = QWidget(self)
        self.summaryWidget.setLayout(layoutStatsFinal)

        self.testPausedWidget = PauseWidget(self)
        self.testBreakpointWidget = BreakPointWidget(self)
        self.testInteractWidget = InteractWidget(self)
        
        self.optionsTab = QTabWidget()
        self.optionsTab.setMaximumHeight(150)
        self.optionsTab.addTab( self.summaryWidget, "Summary" )
        self.optionsTab.addTab( self.optionsWidget, "Options" )
        self.optionsTab.addTab( self.testPausedWidget, "Pause" )
        self.optionsTab.setTabEnabled( TAB_PAUSE_POS, False )
        self.optionsTab.addTab( self.testBreakpointWidget, "BreakPoint" )
        self.optionsTab.setTabEnabled( TAB_BREAKPOINT_POS, False )
        self.optionsTab.addTab( self.testInteractWidget, "Interact" )
        self.optionsTab.setTabEnabled( TAB_INTERACT_POS, False )

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMaximumHeight(5)
        self.progressBar.setTextVisible(False)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        
        self.progressNext = QPushButton("Next")
        self.progressNext.setEnabled(False)
        self.progressNext.setMaximumHeight(15)
        self.progressNext.setMaximumWidth(50)
        self.progressNext.setFlat(False)
        
        layoutProgress = QHBoxLayout()
        layoutProgress.addWidget(self.progressBar)
        layoutProgress.addWidget(self.progressNext)
        
        layout.addWidget(self.optionsTab)
        layout.addWidget(self.filterBox)
        layout.addLayout(layoutProgress)
        layout.addWidget(self.logs)
        

        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def disableControls(self):
        """
        Disable controls
        """
        self.progressNext.setEnabled(False)

    def enableControls(self):
        """
        Enable controls
        """
        self.progressNext.setEnabled(True)

    def activeBreakpoint(self, tid):
        """
        Active breakpoint
        """
        self.deactiveInteract()
        self.deactivePause()
        self.testBreakpointWidget.setTid(tid=tid)
        self.optionsTab.setTabEnabled( TAB_BREAKPOINT_POS, True )
        self.optionsTab.setCurrentIndex( TAB_BREAKPOINT_POS )

    def deactiveBreakpoint(self):
        """
        Deactive breakpoint
        """
        self.optionsTab.setTabEnabled( TAB_BREAKPOINT_POS, False )
        self.optionsTab.setCurrentIndex( TAB_SUMMARY_POS )

    def activePause(self, tid, stepId, stepSummary):
        """
        Active pause
        """
        self.deactiveInteract()
        self.deactiveBreakpoint()
        
        self.testPausedWidget.setTid(tid=tid)
        self.testPausedWidget.setStepInfo(stepId=stepId, stepSummary=stepSummary)
        
        self.optionsTab.setTabEnabled( TAB_PAUSE_POS, True )
        self.optionsTab.setCurrentIndex( TAB_PAUSE_POS )

    def deactivePause(self):
        """
        Deactive Pause
        """
        self.optionsTab.setTabEnabled( TAB_PAUSE_POS, False )
        self.optionsTab.setCurrentIndex( TAB_SUMMARY_POS )

    def activeInteract(self, tid, ask, counter, default):
        """
        Active interact
        """
        self.deactivePause()
        self.deactiveBreakpoint()
        
        self.testInteractWidget.setTid(tid=tid)
        self.testInteractWidget.interactInfo(ask, counter)
        self.testInteractWidget.setDefaultValue(default=default)
        self.testInteractWidget.startCounter()
        
        self.optionsTab.setTabEnabled( TAB_INTERACT_POS, True )
        self.optionsTab.setCurrentIndex( TAB_INTERACT_POS )

    def deactiveInteract(self):
        """
        Deactive Interact
        """
        self.optionsTab.setTabEnabled( TAB_INTERACT_POS, False )
        self.optionsTab.setCurrentIndex( TAB_SUMMARY_POS )

    def createConnections (self):
        """
        QtSignals connection
         * self.logs <=> loadTest
        """
        self.logs.itemClicked.connect(self.loadTest)
        self.logs.KeyUpDownPressed.connect(self.onUpDownPressed)
        self.logs.customContextMenuRequested.connect(self.onPopupMenu)

        self.filterPatternLineEdit.editTextChanged.connect(self.filterRegExpChanged)
        self.filterSyntaxComboBox.currentIndexChanged.connect(self.filterRegExpChanged)
        self.filterCaseSensitivityCheckBox.toggled.connect(self.filterRegExpChanged)
        self.filterColumnComboBox.currentIndexChanged.connect(self.filterColumnChanged)
        self.filterCaseSensitivityCheckBox.toggled.connect(self.filterRegExpChanged)

        self.hideResumeViewCheckBox.stateChanged.connect(self.hideResumeView)
        self.autoscrollTestLogsCheckBox.stateChanged.connect(self.toggleScrollingTestLogs)
        self.autoscrollEventsViewCheckBox.stateChanged.connect(self.toggleScrollingTestEvents)
        self.autoscrollDiagramViewCheckBox.stateChanged.connect(self.toggleScrollingDiagram)
        
        self.progressNext.clicked.connect(self.loadNextEvents)
        
    def loadNextEvents(self):
        """
        Load next events
        """
        self.LoadNext.emit()
        
    def onUpDownPressed(self):
        """
        On up/down key pressed
        """
        events = self.logs.selectedItems()
        if len(events) > 0:
            event = events[0]
            self.loadTest( event )
        
    def setDefaultFilter(self):
        """
        Set the default filter
        """
        defaultSyntax = Settings.instance().readValue( key = 'TestRun/event-filter-syntax' )
        if len(defaultSyntax):
            self.filterSyntaxComboBox.setCurrentIndex(int(defaultSyntax))
            self.filterRegExpChanged()

        defaultColumn = Settings.instance().readValue( key = 'TestRun/event-filter-column' )
        if len(defaultColumn):
            self.filterColumnComboBox.setCurrentIndex(int(defaultColumn))
            self.filterColumnChanged()

        defaultPattern = Settings.instance().readValue( key = 'TestRun/event-filter-pattern' )
        if len(defaultPattern):
            
            # log patterns from settings
            self.filterPatternLineEdit.addItems( Settings.instance().readValue( key = 'TestRun/event-filter-patterns', rType = 'qlist') )
            
            self.filterPatternLineEdit.setEditText(defaultPattern)

            self.filterRegExpChanged()

    def toggleScrollingTestEvents(self, state):
        """
        Toggle scrolling on tests events
        """
        if state == 2:
            self.ActiveScrollingEventLogs.emit()
        else:
            self.DisableScrollingEventLogs.emit()

    def toggleScrollingDiagram(self, state):
        """
        Toggle scrolling on tests events
        """
        if state == 2:
            self.ActiveScrollingDiagram.emit()
        else:
            self.DisableScrollingDiagram.emit()
            
    def toggleScrollingTestLogs(self, state):
        """
        Toggle scrolling on test logs
        """
        if state == 2:
            self.logs.model().rowsInserted.connect(self.autoScroll)
        else:
            self.logs.model().rowsInserted.disconnect(self.autoScroll)

    def hideResumeView(self, state):
        """
        Hide the resume view
        """
        if state == 2:
            self.HideResumeView.emit()
        else:
            self.ShowResumeView.emit()

    def filterRegExpChanged(self):
        """
        On filter regexp changed
        """
        syntax_nr = self.filterSyntaxComboBox.itemData(self.filterSyntaxComboBox.currentIndex())
        if sys.version_info > (3,): # python3 support
            syntax = QRegExp.PatternSyntax( syntax_nr )
        else:
            syntax = QRegExp.PatternSyntax( syntax_nr.toString() )

        if self.filterCaseSensitivityCheckBox.isChecked(): 
            caseSensitivity = Qt.CaseSensitive
        else: 
            caseSensitivity = Qt.CaseInsensitive

        regExp = QRegExp(self.filterPatternLineEdit.currentText(),  caseSensitivity, syntax)
        
        self.RegExpUpdated.emit(regExp )
        
    def autoScroll(self):
        """
        On auto scroll
        """
        QTimer.singleShot(0, self.logs.scrollToBottom)

    def filterColumnChanged(self):
        """
        On filter column changed
        """
        self.FilterColumnUpdated.emit( self.filterColumnComboBox.currentIndex() )

    def createToolbars(self):
        """
        Toolbar creation
        """
        self.toolbar.setObjectName("Result toolbar")
        self.toolbar.addAction(self.replayAction)
        self.toolbar.addAction(self.killAction)
        self.toolbar.addAction(self.addCommentAction)
        self.toolbar.setIconSize(QSize(20, 20))
        
        self.toolbarExports.setObjectName("Exports toolbar")
        self.toolbarExports.addAction(self.exportVerdictAction)
        self.toolbarExports.addAction(self.exportReportAction)
        self.toolbarExports.addAction(self.exportDesignAction)
        self.toolbarExports.addAction(self.exportStatisticsAction)
        self.toolbarExports.setIconSize(QSize(20, 20))
        
    def reset (self):
        """
        Reset
        """
        self.logs.clear()
        self.isKilled = False
        self.nbOk = 0
        self.nbKo = 0
        self.nbUnd = 0

        self.nb_min_avg_max_ts = []
        self.nb_min_avg_max_tc = []
        self.nb_min_avg_max_tu = []
        self.nb_min_avg_max_ta = []
        self.nb_min_avg_max_tp = []

        self.replayAction.setEnabled( False )
        self.killAction.setEnabled( False )
        self.addCommentAction.setEnabled( False )
        
        self.exportVerdictAction.setEnabled( False )
        self.exportReportAction.setEnabled( False )
        self.exportDesignAction.setEnabled( False )
        self.exportStatisticsAction.setEnabled( False )
    
        self.nbOkLabel.setText( "0" )
        self.nbKoLabel.setText( "0.000" )
        self.nbUndLabel.setText( "0.000" )
        self.nbTotLabel.setText( "0.000" )
        
        self.nb_TaLabel.setText( "0" )
        self.min_TaLabel.setText( "0.000" )
        self.avg_TaLabel.setText( "0.000" )
        self.max_TaLabel.setText( "0.000" )
        
        self.nb_TuLabel.setText( "0" )
        self.min_TuLabel.setText( "0.000" )
        self.avg_TuLabel.setText( "0.000" )
        self.max_TuLabel.setText( "0.000" )

        self.nb_TsLabel.setText( "0" )
        self.min_TsLabel.setText( "0.000" )
        self.avg_TsLabel.setText( "0.000" )
        self.max_TsLabel.setText( "0.000" )

        self.nb_TcLabel.setText( "0" )
        self.min_TcLabel.setText( "0.000" )
        self.avg_TcLabel.setText( "0.000" )
        self.max_TcLabel.setText( "0.000" )

        self.nb_TpLabel.setText( "0" )
        self.min_TpLabel.setText( "0.000" )
        self.avg_TpLabel.setText( "0.000" )
        self.max_TpLabel.setText( "0.000" )

        self.nb_TgLabel.setText( "0" )
        self.min_TgLabel.setText( "0.000" )
        self.avg_TgLabel.setText( "0.000" )
        self.max_TgLabel.setText( "0.000" )

    def onPopupMenu(self, pos):
        """
        On popup menu

        @param pos:
        @type pos:
        """
        item = self.logs.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.menu.addAction( self.expandAllAction )
            self.menu.addAction( self.collapseAllAction )
            self.menu.popup(self.logs.mapToGlobal(pos))

    def exportStatistics(self):
        """
        Export statistics
        """
        statsDialog = ExportStatistics.WExportStatistics(parent=self,dataXml=self.statsToXml() )
        if statsDialog.exec_() == QDialog.Accepted:
            del statsDialog

    def exportVerdict(self):
        """
        Export verdict
        """
        self.ExportVerdict.emit()

    def exportReport(self):
        """
        Export report
        """
        self.ExportReport.emit()

    def exportDesign(self):
        """
        Export design
        """
        self.ExportDesign.emit()

    def expandAllItems(self):
        """
        Expand all items
        """
        self.logs.expandAll()
    
    def collapseAllItems(self):
        """
        Collapse all items
        """
        self.logs.collapseAll()

    def addComment(self):
        """
        Add comment
        """
        self.AddPostTest.emit()

    def killTest(self):
        """
        Kill the test
        """
        self.KillTest.emit()

    def replayTest (self):
        """
        Replay the test
        """
        self.ReplayTest.emit()

    def closeTest (self):
        """
        Signal "closeTest" emited when the button "Close" is clicked
        """
        self.CloseTest.emit()
    
    def updateSummary (self):
        """
        Updates statistics of the test
        Number of PASS, FAIL, etc ... 
        """
        self.nbOkLabel.setText( str(self.nbOk) )
        self.nbKoLabel.setText( str(self.nbKo) )
        self.nbUndLabel.setText( str(self.nbUnd) )
        self.nbTotLabel.setText( str(self.nbOk + self.nbKo + self.nbUnd ) )
    
    def statsToXml(self):
        """
        Statistics to xml
        """
        avgTp = 0
        avgTg = 0
        avgTs = 0
        avgTu = 0
        avgTa = 0
        avgtc = 0
        if len(self.nb_min_avg_max_tp):
            avgTp = sum(self.nb_min_avg_max_tp) / len(self.nb_min_avg_max_tp)
        if len(self.nb_min_avg_max_tg):
            avgTg = sum(self.nb_min_avg_max_tg) / len(self.nb_min_avg_max_tg)
        if len(self.nb_min_avg_max_ts):
            avgTs = sum(self.nb_min_avg_max_ts) / len(self.nb_min_avg_max_ts)
        if len(self.nb_min_avg_max_tu):
            avgTu= sum(self.nb_min_avg_max_tu) / len(self.nb_min_avg_max_tu)
        if len(self.nb_min_avg_max_ta):
            avgTa= sum(self.nb_min_avg_max_ta) / len(self.nb_min_avg_max_ta)
        if len(self.nb_min_avg_max_tc):
            avgTc = sum(self.nb_min_avg_max_tc) / len(self.nb_min_avg_max_tc)

        ret = [ '<?xml version="1.0" encoding="UTF-8"?>' ]
        ret.append( '<statistics>' )

        ret.append( '\t<testglobal max="%s" >' % len(self.nb_min_avg_max_tg) )
        if not len(self.nb_min_avg_max_tg):
            ret[len(ret)-1] = '\t<testglobal max="0" />'
        else:
            ret.append( '\t\t<min>%s</min>' % min(self.nb_min_avg_max_tg) )
            ret.append( '\t\t<avg>%.3f</avg>' % avgTg )
            ret.append( '\t\t<max>%s</max>' % max(self.nb_min_avg_max_tg) )
            ret.append( '\t</testglobal>' )

        ret.append( '\t<testplan max="%s" >' % len(self.nb_min_avg_max_tp) )
        if not len(self.nb_min_avg_max_tp):
            ret[len(ret)-1] = '\t<testplan max="0" />'
        else:
            ret.append( '\t\t<min>%s</min>' % min(self.nb_min_avg_max_tp) )
            ret.append( '\t\t<avg>%.3f</avg>' % avgTp )
            ret.append( '\t\t<max>%s</max>' % max(self.nb_min_avg_max_tp) )
            ret.append( '\t</testplan>' )

        ret.append( '\t<testsuite max="%s" >' % len(self.nb_min_avg_max_ts) )
        if not len(self.nb_min_avg_max_ts):
            ret[len(ret)-1] = '\t<testsuite max="0" />'
        else:
            ret.append( '\t\t<min>%s</min>' % min(self.nb_min_avg_max_ts) )
            ret.append( '\t\t<avg>%.3f</avg>' % avgTs )
            ret.append( '\t\t<max>%s</max>' % max(self.nb_min_avg_max_ts) )
            ret.append( '\t</testsuite>' )
        
        ret.append( '\t<testunit max="%s" >' % len(self.nb_min_avg_max_tu) )
        if not len(self.nb_min_avg_max_tu):
            ret[len(ret)-1] = '\t<testunit max="0" />'
        else:
            ret.append( '\t\t<min>%s</min>' % min(self.nb_min_avg_max_tu) )
            ret.append( '\t\t<avg>%.3f</avg>' % avgTu )
            ret.append( '\t\t<max>%s</max>' % max(self.nb_min_avg_max_tu) )
            ret.append( '\t</testunit>' )
            
        ret.append( '\t<testabstract max="%s" >' % len(self.nb_min_avg_max_ta) )
        if not len(self.nb_min_avg_max_ta):
            ret[len(ret)-1] = '\t<testabstract max="0" />'
        else:
            ret.append( '\t\t<min>%s</min>' % min(self.nb_min_avg_max_ta) )
            ret.append( '\t\t<avg>%.3f</avg>' % avgTa )
            ret.append( '\t\t<max>%s</max>' % max(self.nb_min_avg_max_ta) )
            ret.append( '\t</testabstract>' )
            
        ret.append( '\t<testcase max="%s" >' % len(self.nb_min_avg_max_tc) )
        if not len(self.nb_min_avg_max_tc):
            ret[len(ret)-1] = '\t<testcase max="0" />'
        else:
            ret.append( '\t\t<min>%s</min>' % min(self.nb_min_avg_max_tc) )
            ret.append( '\t\t<avg>%.3f</avg>' % avgTc )
            ret.append( '\t\t<max>%s</max>' % max(self.nb_min_avg_max_tc) )
            ret.append( '\t</testcase>' )

        ret.append( '</statistics>' )
        return '\n'.join(ret)

    def updateStatsTs (self):
        """
        Update statistics of testsuite
        """
        nbTs = len(self.nb_min_avg_max_ts)
        minTs = min(self.nb_min_avg_max_ts)
        avgTs = sum(self.nb_min_avg_max_ts) / nbTs
        maxTs = max(self.nb_min_avg_max_ts)
        self.nb_TsLabel.setText( "%s" % nbTs )
        self.min_TsLabel.setText( "%s" % minTs )
        self.avg_TsLabel.setText( "%.3f" % avgTs )
        self.max_TsLabel.setText( "%s" % maxTs )

    def updateStatsTu (self):
        """
        Update statistics of testunit
        """
        nbTu = len(self.nb_min_avg_max_tu)
        minTu = min(self.nb_min_avg_max_tu)
        avgTu = sum(self.nb_min_avg_max_tu) / nbTu
        maxTu = max(self.nb_min_avg_max_tu)
        self.nb_TuLabel.setText( "%s" % nbTu )
        self.min_TuLabel.setText( "%s" % minTu )
        self.avg_TuLabel.setText( "%.3f" % avgTu )
        self.max_TuLabel.setText( "%s" % maxTu )
        
    def updateStatsTa (self):
        """
        Update statistics of testabstract
        """
        nbTa = len(self.nb_min_avg_max_ta)
        minTa = min(self.nb_min_avg_max_ta)
        avgTa = sum(self.nb_min_avg_max_ta) / nbTa
        maxTa = max(self.nb_min_avg_max_ta)
        self.nb_TaLabel.setText( "%s" % nbTa )
        self.min_TaLabel.setText( "%s" % minTa )
        self.avg_TaLabel.setText( "%.3f" % avgTa )
        self.max_TaLabel.setText( "%s" % maxTa )
        
    def updateStatsTc (self):
        """
        Update statistics of testcase
        """
        nbTc = len(self.nb_min_avg_max_tc)
        minTc = min(self.nb_min_avg_max_tc)
        avgTc = sum(self.nb_min_avg_max_tc) / nbTc
        maxTc = max(self.nb_min_avg_max_tc)
        self.nb_TcLabel.setText( "%s" % nbTc )
        self.min_TcLabel.setText( "%s" % minTc )
        self.avg_TcLabel.setText( "%.3f" % avgTc )
        self.max_TcLabel.setText( "%s" % maxTc )

    def updateStatsTp (self):
        """
        Update statistics of testplan
        """
        nbTp = len(self.nb_min_avg_max_tp)
        minTp = min(self.nb_min_avg_max_tp)
        avgTp = sum(self.nb_min_avg_max_tp) / nbTp
        maxTp = max(self.nb_min_avg_max_tp)
        self.nb_TpLabel.setText( "%s" % nbTp )
        self.min_TpLabel.setText( "%s" % minTp )
        self.avg_TpLabel.setText( "%.3f" % avgTp, )
        self.max_TpLabel.setText( "%s" % maxTp )

    def updateStatsTg (self):
        """
        Update statistics of testglobal
        """
        nbTg = len(self.nb_min_avg_max_tg)
        minTg = min(self.nb_min_avg_max_tg)
        avgTg = sum(self.nb_min_avg_max_tg) / nbTg
        maxTg = max(self.nb_min_avg_max_tg)
        self.nb_TgLabel.setText( "%s" % nbTg )
        self.min_TgLabel.setText( "%s" % minTg )
        self.avg_TgLabel.setText( "%.3f" % avgTg )
        self.max_TgLabel.setText( "%s" % maxTg )

    def beforeLoadTest (self):
        """
        Before load the test
        """
        events = self.logs.selectedItems()
        if len(events) > 0:
            event = events[0]
            self.loadTest( event )

    def loadTest (self, wtest):
        """
        Signal "loadTest" emited when log item is clicked

        @param wtest: expected widget in TestItem
        @type wtest: QTreeWidgetItem
        """
        testId = wtest.testId
        testName = wtest.testName
        
        if not len(testName):
            w = self.logs.itemWidget(wtest, 0) 
            testName = w.testcaseName

        self.emitTestName(testName=testName, testItem=wtest)
        
        self.LoadTest.emit( "%s" % testId, testName ) 

    def emitTestName(self, testName, testItem):
        """
        New in v16
        """
        if isinstance(testItem.owner, TestItem):
            parentOwner = testItem.owner
            parentName = parentOwner.testName

            if isinstance(parentOwner.owner, TestItem):
                parentMain = parentOwner.owner.testName
                self.TestName.emit( "%s > %s > %s" % ( parentMain, parentName, testName) )
            else:
                self.TestName.emit( "%s > %s" % ( parentName, testName) )
        else:
            self.TestName.emit( testName )

    def createTestplanSeparator(self, event):
        """
        Create testplan separator for testglobal
        """
        typeItem= 'testplan'
        testInternalId = ''
        if 'test-internal-id' in event: # for backward compatibility
            testInternalId = str(event['test-internal-id'])
        
        if sys.version_info > (3,): # py3 support
            testplanName = event['testname']
        else:
            testplanName = event['testname'].decode('utf8')
            
        # new in v11
        if "alias" in event:
            if len(event['alias']):
                if sys.version_info > (3,): # py3 support
                    testplanName = event['alias']
                else:
                    testplanName = event['alias'].decode('utf8')
        # end of new

        rootItem = TestItem( testName = testplanName, testId = 0, #str(event['script_id'])
                                parent= self.parentLogs, typeItem = typeItem, internalId=testInternalId )
        rootItem.setExpanded( QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/tests-expanded' ) ) )
        rootItem.setForeground(COL_NAME, QBrush( QColor( Qt.blue ) ) )
        
        self.emitTestName(testName=testplanName, testItem=rootItem)
        
        self.parentLogs = rootItem
        return rootItem 

    def createRootItem (self , event, typeItem= 'testsuite' ):
        """
        Returns the root item test

        @param event:
        @type event: dict

        @return: root tree item 
        @rtype: TestItem
        """
        testInternalId = ''
        if 'test-internal-id' in event: # for backward compatibility
            testInternalId = str(event['test-internal-id'])
        if sys.version_info > (3,): # py3 support
            testsuiteName = event['script_name']
        else:
            testsuiteName = event['script_name'].decode('utf8')
            
        # new in v11
        if "alias" in event:
            if len(event['alias']):
                if sys.version_info > (3,): # py3 support
                    testsuiteName = event['alias']
                else:
                    testsuiteName = event['alias'].decode('utf8')
        # end of new
        
        # new in v11.2
        startIndex = 0
        if "header-index" in event: startIndex = event["header-index"]
        # end of new
        

        rootItem = TestItem( 
                            testName = testsuiteName, testId = str(event['script_id']),
                            parent= self.parentLogs, typeItem = typeItem, internalId=testInternalId,
                            startIndex=startIndex
                            )
        rootItem.setExpanded( QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/tests-expanded' ) ) )
        rootItem.setSelected(True)
        rootItem.setForeground(COL_NAME, QBrush(QColor(Qt.darkCyan ) ) )
        
        self.emitTestName(testName=testsuiteName, testItem=rootItem)
        
        return rootItem 

    def finishTestplanSeparator (self, itemSep, duration=None ):
        """
        Updates the color the root item test

        @param rootItem:
        @type rootItem: TestItem
        """
        self.parentLogs = self.logs

        itemSep.setTooltipDuration(duration=duration)
        
        self.nb_min_avg_max_tp.append( float(duration) )
        self.updateStatsTp()

    def finishRootItem (self, rootItem, duration=None, typeItem='testsuite', event={} ):
        """
        Updates the color the root item test

        @param rootItem:
        @type rootItem: TestItem
        """
        # new in v11.2
        if len(event):
            if "header-index" in event:
                rootItem.stopIndex = event['header-index']
        # end of new
        
        rootItem.setSelected(False)
        rootItem.setForeground(COL_NAME, QBrush( QColor( Qt.blue ) ) )
        
        # new in v11.2
        fail = False
        for i in range(rootItem.childCount()):
            if rootItem.child(i).getResult() == self.FAIL:
                fail=True
                break
        if fail:
            rootItem.setForeground(COL_NAME, QBrush( QColor( Qt.red ) ) )
            # new in v17
            if rootItem.parent() is not None:
                rootItem.parent().setForeground(COL_NAME, QBrush( QColor( Qt.red ) ) )
            # end of new
        # end of new

            
        if duration is not None:
            rootItem.setTooltipDuration(duration=duration)
            if typeItem == 'testsuite':
                self.nb_min_avg_max_ts.append( float(duration) )
                self.updateStatsTs()
            if typeItem == 'testunit':
                self.nb_min_avg_max_tu.append( float(duration) )
                self.updateStatsTu()
            if typeItem == 'testabstract':
                self.nb_min_avg_max_ta.append( float(duration) )
                self.updateStatsTa()
            if typeItem == 'testplan':
                self.nb_min_avg_max_tp.append( float(duration) )
                self.updateStatsTp()
            if typeItem == 'testglobal':
                self.nb_min_avg_max_tg.append( float(duration) )
                self.updateStatsTg()

    def activeKill(self):
        """
        Active the kill button
        """
        if not self.local:
            if not self.isKilled:
                self.killAction.setEnabled( True )

    def deactiveKill(self):
        """
        Deactive the kill button
        """
        if not self.local:
            self.killAction.setEnabled( False )
            self.isKilled = True

    def activeReplay (self):
        """
        Active the replay button
        """
        if not self.local:
            self.replayAction.setEnabled( True )
            self.addCommentAction.setEnabled( True )
            self.exportVerdictAction.setEnabled( True )
            self.exportReportAction.setEnabled( True )
            self.exportDesignAction.setEnabled( True )
            self.exportStatisticsAction.setEnabled( True )
        else:
            self.exportStatisticsAction.setEnabled( True )

    def createTestcase (self, rootItem, event, fromLocal=False ):
        """
        Returns the testcase item

        @param rootItem: Parent
        @type rootItem: TestItem

        @param event: 
        @type event: 

        @return:
        @rtype: TestItem
        """
        
        if sys.version_info > (3,): # py3 support
            testcaseName = event['name']
        else:
            testcaseName = event['name'].decode('utf8')
            
        
        # new in v11.2
        startIndex = 0
        if "header-index" in event: startIndex = event["header-index"]
        # end of new

        testcaseItem = TestItem( 
                                testName = "", testId = event['tc_id'], parent = rootItem ,
                                typeItem = 'testcase', startIndex=startIndex
                                )
        if not fromLocal: testcaseItem.setSelected(True)

        self.emitTestName(testName=testcaseName, testItem=testcaseItem )
        
        loading = LabelMovie(self, testcaseName, not self.isKilled)
        self.logs.setItemWidget(testcaseItem, 0, loading )
        
        return testcaseItem
    
    def finishTestcase (self, testcaseItem, result, duration=None, event={} ):
        """
        Update the testcase item color and icon
        Calls the function updateStats()

        @param testcaseItem:
        @type testcaseItem: TestItem

        @param result: value expected = "FAIL", "PASS" 
        @type result: string
        """
        # new in v11.2
        if len(event):
            if "header-index" in event:
                testcaseItem.stopIndex = event['header-index']
        testcaseItem.setResult(result)
        # end of new
        
        if result == self.PASS:
            wtc = self.logs.itemWidget(testcaseItem, 0)
            wtc.setPASS()
            
            self.nbOk += 1
        elif result == self.FAIL:
            wtc = self.logs.itemWidget(testcaseItem, 0)
            wtc.setFAIL()
            
            self.nbKo += 1
        else:
            wtc = self.logs.itemWidget(testcaseItem, 0)
            wtc.setUNDEF()
            
            self.nbUnd += 1
        
        # New in 3.0.0
        if duration is not None:
            testcaseItem.setDuration(duration=duration)
            self.nb_min_avg_max_tc.append( float(duration) )
        
        # Update summary and stats
        self.updateSummary()
        self.updateStatsTc()
        