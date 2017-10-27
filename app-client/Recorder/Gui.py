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
Recorder Gui extension for the extensive client
"""
import sys
import time
import re

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QWidget, QKeySequence, QPixmap, QDialog, QApplication, QCursor, 
                            QIcon, QToolBar, QGroupBox, QLineEdit, QDoubleValidator, QComboBox, 
                            QGridLayout, QLabel, QFrame, QVBoxLayout, QIntValidator, QHBoxLayout, 
                            QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                            QCheckBox, QSplitter, QMessageBox, QDesktopWidget, QShortcut )
    from PyQt4.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal, QT_VERSION_STR, QEvent)
except ImportError:
    from PyQt5.QtGui import (QKeySequence, QPixmap, QCursor, QIcon, QDoubleValidator, QIntValidator,
                            QGuiApplication )
    from PyQt5.QtWidgets import (QWidget, QDialog, QApplication, QToolBar, QGroupBox, QLineEdit, 
                                QComboBox, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                                QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                                QCheckBox, QSplitter, QMessageBox, QDesktopWidget, QShortcut)
    from PyQt5.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal, QT_VERSION_STR, QEvent)

from Libs import QtHelper, Logger

import ServerExplorer.Agents as ServerAgents

import Settings
import UserClientInterface as UCI
import Workspace as WWorkspace
import DefaultTemplates


try:
    import GuiSnapshot
    import GuiSteps
    import GuiAndroid
    import GuiSelenium
    import GuiSikuli
    import Framework
    import System
except ImportError: # python3 support
    from . import GuiSnapshot
    from . import GuiSteps
    from . import GuiAndroid
    from . import GuiSelenium
    from . import GuiSikuli
    from . import Framework
    from . import System
    
TAG_COMMENT                     = "##CAPTURE>"
TAG_COMMENT_BROWSER             = "##CAPTURE_BROWSER>"
TAG_COMMENT_ANDROID             = "##CAPTURE_ANDROID>"
TAG_COMMENT_FRAMEWORK           = "##CAPTURE_FRAMEWORK>"
TAG_COMMENT_SYS                 = "##CAPTURE_SYS>"
TAG_USER                        = "##CAPTURE_USER>"
TAG_USER_CODE                   = "##CAPTURE_USERCODE>"
TAG_USER_BEGIN                  = "##CAPTURE_USER_BEGIN>"
TAG_USER_END                    = "##CAPTURE_USER_END>"
    
POS_TAB_BASIC   = 0
POS_TAB_SSH     = 1
POS_TAB_APP     = 2
POS_TAB_WEB     = 3
POS_TAB_ANDROID = 4

class WRecorderGui(QWidget, Logger.ClassLogger):        
    """
    Recorder Gui dialog
    """
    def __init__(self, parent = None, offlineMode=False, mainParent=None):
        """
        Constructor

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self)
        self.parent = parent
        self.offlineMode = offlineMode
        self.mainParent = mainParent

        self.stepsTable = GuiSteps.StepsTableView(self)
        self.defaultTemplates = DefaultTemplates.Templates()

        self.recorderActivated = False
        self.snapshotActivated = False
        self.mouseActivated = False
        self.locationActivated = False
        
        self.destRow = None
        self.currentDocument = None
        self.stepIdUnique = 0

        self.stepId = 0
        
        self.userParams = []
        self.isTu = True
        self.isTs = False
        
        # new in v11
        self.jQuery = ""
        fd = QFile(":/jquery.min.js")
        if fd.open(QIODevice.ReadOnly | QFile.Text):
            self.jQuery = QTextStream(fd).readAll()
            
        self.DEFAULT_SIMILAR_VALUE = Settings.instance().readValue( key = 'TestGenerator/default-similar-threshold' )

        self.spDialogOpened = False
        self.spMouseDialogOpened = False
        self.spLocationDialogOpened = False

        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.createToolbar()
        
    def restoreAssistant(self):
        """
        Restore assistant
        """
        self.setCursor(QCursor(Qt.ArrowCursor) )
        self.recorderActivated = False
        self.spDialogOpened = False
        
        self.locationActivated = False
        self.spLocationDialogOpened = False
        self.spMouseDialogOpened = False
        self.mouseActivated = False 
        self.snapshotActivated = False
        self.spDialogOpened = False
        
        self.setVisible(True)
        
    def onGlobalShortcutPressed(self):
        """
        On global shortcut pressed
        """
        self.mainParent.captureRecorderAction.setEnabled(False)

        if self.recorderActivated: # called from automation assistant
            if self.sikuliGroup.getCurrentAction() in [ GuiSteps.TYPE_TEXT, GuiSteps.TYPE_TEXT_PATH, 
                                                        GuiSteps.FRAMEWORK_WAIT, GuiSteps.SHORTCUT ]:
                return

            if self.spDialogOpened: return
            
            # take a screenshot of the desktop
            if QT_VERSION_STR.startswith("4."):
                screenshotDesktop = QPixmap.grabWindow(QApplication.desktop().winId())
            else:
                primaryScreen = QGuiApplication.primaryScreen()
                screenshotDesktop = primaryScreen.grabWindow(QApplication.desktop().winId())
            
            self.spDialogOpened = True
            self.spDialog = GuiSnapshot.DSnapshot(self)
            self.spDialog.setBackground( pixmap=screenshotDesktop )
            
            if self.spDialog.exec_() == QDialog.Accepted:
                snapshot = self.spDialog.getSnapshot()
                if self.sikuliGroup.getCurrentAction() in ["%s %s" % (GuiSteps.TYPE_TEXT_ON,GuiSteps.AND_TYPE_TEXT) ]:
                    self.sikuliGroup.setSnapshotText(snapshot)
                elif self.sikuliGroup.getCurrentAction() in [ GuiSteps.DRAG_DROP_IMAGE ]:
                    self.sikuliGroup.setSnapshotDrag(snapshot)
                else:
                    self.sikuliGroup.setSnapshotImage(snapshot)

            self.setCursor(QCursor(Qt.ArrowCursor) )
            self.recorderActivated = False
            self.spDialogOpened = False
            self.setVisible(True)
            
        elif self.locationActivated:
            if self.spLocationDialogOpened: return
            
            # take a screenshot of the desktop
            if QT_VERSION_STR.startswith("4."):
                screenshotDesktop = QPixmap.grabWindow(QApplication.desktop().winId())
            else:
                primaryScreen = QGuiApplication.primaryScreen()
                screenshotDesktop = primaryScreen.grabWindow(QApplication.desktop().winId())
            
            self.spLocationDialogOpened = True
            self.spDialog = GuiSnapshot.DSnapshot(self)
            self.spDialog.setBackground( pixmap=screenshotDesktop )
            
            if self.spDialog.exec_() == QDialog.Accepted:
                x, y, w, h = self.spDialog.getLocation()
                self.sikuliGroup.setMouseLocation(posX=x, posY=y, posW=w, posH=h)

            self.setCursor(QCursor(Qt.ArrowCursor) )
            self.locationActivated = False
            self.spLocationDialogOpened = False
            self.setVisible(True)
            
        elif self.mouseActivated:
        
            if self.spMouseDialogOpened: return
            
            # take a screenshot of the desktop
            if QT_VERSION_STR.startswith("4."):
                screenshotDesktop = QPixmap.grabWindow(QApplication.desktop().winId())
            else:
                primaryScreen = QGuiApplication.primaryScreen()
                screenshotDesktop = primaryScreen.grabWindow(QApplication.desktop().winId())
                
            self.spMouseDialogOpened = True
            self.spMouseDialog = GuiSnapshot.DCaptureMouse(self)          
            if self.spMouseDialog.exec_() == QDialog.Accepted:
                self.sikuliGroup.setMousePosition(self.spMouseDialog.posLabel.posX, self.spMouseDialog.posLabel.posY)

            self.spMouseDialogOpened = False
            self.mouseActivated = False 
            self.setCursor(QCursor(Qt.ArrowCursor) )
            self.setVisible(True)
        
        else:
            if self.snapshotActivated: # called from test parameters
                if self.spDialogOpened: return
                
                # take a screenshot of the desktop
                if QT_VERSION_STR.startswith("4."):
                    screenshotDesktop = QPixmap.grabWindow(QApplication.desktop().winId())
                else:
                    primaryScreen = QGuiApplication.primaryScreen()
                    screenshotDesktop = primaryScreen.grabWindow(QApplication.desktop().winId())
                
                self.spDialogOpened = False   
                self.spDialog = GuiSnapshot.DSnapshot(self)
                self.spDialog.setBackground( pixmap=screenshotDesktop )
                
                if self.spDialog.exec_() == QDialog.Accepted:
                    snapshot = self.spDialog.getSnapshot()
                    self.onGlobalShortcutPressedFromParameters(snapshot=snapshot, destRow=self.destRow)
     
                self.setCursor(QCursor(Qt.ArrowCursor) )
                self.snapshotActivated = False
                self.spDialogOpened = False
            else:
                return

    def onGlobalShortcutPressedFromParameters(self, snapshot, destRow):
        """
        Function to reimplement
        """
        pass

    def createActions (self):
        """
        Create qt actions
        """
        self.cancelAction = QtHelper.createAction(self, "&Exit\nAssistant", self.cancelRecording, 
                                            icon=QIcon(":/test-close-black.png"), tip = 'Cancel')
                                            
        self.exportTUAction = QtHelper.createAction(self, "&Test\nUnit", self.exportToTU, 
                                            icon=QIcon(":/%s.png" % WWorkspace.TestUnit.TYPE), tip = 'Export to Test Unit')
        self.exportTSAction = QtHelper.createAction(self, "&Test\nSuite", self.exportToTS, 
                                            icon=QIcon(":/%s.png" % WWorkspace.TestSuite.TYPE),  tip = 'Export to Test Suite')

        self.exportStepsAction = QtHelper.createAction(self, "&Create Test", self.exportToTest,
                                            icon=QIcon(":/ok.png") ,  tip = 'Export to tests' )
        self.updateStepsAction = QtHelper.createAction(self, "Current\nTest", self.updateTest, 
                                            icon=QIcon(":/update-test.png") ,  tip = 'Export to tests' )
        self.updateStepsAction.setEnabled(False)
        self.exportStepsAction.setEnabled(False)
        self.clearStepsAction = QtHelper.createAction(self, "&Clear All", self.clearSteps, 
                                            icon=QIcon(":/test-close.png"),  tip = 'Clear steps')

    def createWidgets(self):
        """
        Create widget
        """

        self.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);

            dialog-yes-icon: url(:/ok.png);
            dialog-no-icon: url(:/ko.png);

            dialog-apply-icon: url(:/ok.png);
            dialog-reset-icon: url(:/ko.png);
        }""")
        
        self.dockToolbarPlugins = QToolBar(self)
        self.dockToolbarPlugins.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarPlugins.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbar2 = QToolBar(self)
        self.dockToolbar2.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbar3 = QToolBar(self)
        self.dockToolbar3.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarClipboard = QToolBar(self)
        self.dockToolbarClipboard.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.dockToolbarClipboard2 = QToolBar(self)
        self.dockToolbarClipboard2.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.dockToolbarMiscs = QToolBar(self)
        self.dockToolbarMiscs.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarMiscs.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarExport = QToolBar(self)
        self.dockToolbarExport.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarExport.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarOptions = QToolBar(self)
        self.dockToolbarOptions.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        
        self.dockToolbarOptions2 = QToolBar(self)
        self.dockToolbarOptions2.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.setWindowTitle( self.tr("%s - Assistant Automation" % Settings.instance().readValue( key = 'Common/name' ) ) )
        self.setWindowIcon( QIcon(":/main.png") )
        
        self.stopOnError  = QCheckBox( " " )
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestGenerator/stop-on-failure' ) ):
            self.stopOnError.setChecked(True)
        
        self.oneStepCheck  = QCheckBox( " " )
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestGenerator/merge-all-steps' ) ):
            self.oneStepCheck.setChecked(True)

        listGroup = QFrame()
        
        listGroup.setMinimumWidth(800)

        self.insertBox = QGroupBox("Prepare")
        self.insertBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutInsertBox = QHBoxLayout()
        layoutInsertBox.addWidget(self.dockToolbar2)
        layoutInsertBox.setContentsMargins(0,0,0,0)
        self.insertBox.setLayout(layoutInsertBox)

        self.clipboardBox = QGroupBox("Clip.")
        self.clipboardBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutClipboardBox = QVBoxLayout()
        layoutClipboardBox.addWidget(self.dockToolbarClipboard)
        layoutClipboardBox.addWidget(self.dockToolbarClipboard2)
        layoutClipboardBox.setContentsMargins(10,0,0,10)
        self.clipboardBox.setLayout(layoutClipboardBox)
        

        self.miscBox = QGroupBox("Miscellaneous")
        self.miscBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutMiscBox = QHBoxLayout()
        layoutMiscBox.addWidget(self.dockToolbarMiscs)
        layoutMiscBox.setContentsMargins(0,0,0,0)
        self.miscBox.setLayout(layoutMiscBox)
        
        self.generateBox = QGroupBox("Terminate")
        self.generateBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutGenerateBox = QHBoxLayout()
        layoutGenerateBox.addWidget(self.dockToolbar3)
        layoutGenerateBox.setContentsMargins(0,0,0,0)
        self.generateBox.setLayout(layoutGenerateBox)
        
        self.exportBox = QGroupBox("Export To")
        self.exportBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutExportBox = QHBoxLayout()
        layoutExportBox.addWidget(self.dockToolbarExport)
        layoutExportBox.setContentsMargins(0,0,0,0)
        self.exportBox.setLayout(layoutExportBox)
        
        self.optsBox = QGroupBox("Options")
        self.optsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutOptBox = QVBoxLayout()
        layoutOptBox.addWidget(self.dockToolbarOptions)
        layoutOptBox.addWidget(self.dockToolbarOptions2)
        layoutOptBox.setContentsMargins(0,0,0,0)
        self.optsBox.setLayout(layoutOptBox)
        
        # get screen size
        screenResolution = QApplication.desktop().screenGeometry()
        
        self.infoGroupBox = QGroupBox(self.tr("Screens"))
        self.infoGroupBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        infoGroupLayout = QGridLayout()
        infoGroupLayout.addWidget( QLabel( self.tr("Number:") ) , 0, 0)
        if QT_VERSION_STR.startswith("4."):
            infoGroupLayout.addWidget( QLabel("%s" % QDesktopWidget().numScreens()) , 0, 1)
        else:
            infoGroupLayout.addWidget( QLabel("%s" % QDesktopWidget().screenCount()) , 0, 1)
        infoGroupLayout.addWidget( QLabel( self.tr("Primary Size:") ) , 1, 0)
        infoGroupLayout.addWidget( QLabel( "%s x %s" % (screenResolution.width(), screenResolution.height()) ) , 1, 1)
        self.infoGroupBox.setLayout(infoGroupLayout)

        self.automaticAdp = QRadioButton("Automatic")
        self.automaticAdp.setChecked(True)
        self.defaultAdp = QRadioButton("Default")
        self.genericAdp = QRadioButton("Generic")
        
        self.adaptersBox = QGroupBox("Adapters Version")
        self.adaptersBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        
        layoutAdpAllBox = QVBoxLayout()
        layoutAdpAllBox.setContentsMargins(0,0,0,0)
        
        layoutAdpBox = QVBoxLayout()
        layoutAdpBox.addWidget(self.automaticAdp)

        layoutAdpBox2 = QHBoxLayout()
        layoutAdpBox2.addWidget(self.defaultAdp)
        layoutAdpBox2.addWidget(self.genericAdp)

        layoutAdpAllBox.addLayout(layoutAdpBox)
        layoutAdpAllBox.addLayout(layoutAdpBox2)
        
        self.adaptersBox.setLayout(layoutAdpAllBox)

        self.globalGroupBox = QGroupBox(self.tr("Steps"))
        self.globalGroupBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        globalGroupLayout = QGridLayout()
        globalGroupLayout.addWidget( QLabel( self.tr("Stop on failure?") ) , 0, 0)
        globalGroupLayout.addWidget(self.stopOnError, 0, 1)
        globalGroupLayout.addWidget( QLabel( self.tr("Merge all in one?") ) , 1, 0)
        globalGroupLayout.addWidget(self.oneStepCheck, 1, 1)
        self.globalGroupBox.setLayout(globalGroupLayout)

        self.pluginsBox = QGroupBox("Plugins")
        self.pluginsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutPlugnsBox = QHBoxLayout()
        layoutPlugnsBox.addWidget(self.dockToolbarPlugins)
        layoutPlugnsBox.setContentsMargins(0,0,0,0)
        self.pluginsBox.setLayout(layoutPlugnsBox)
        self.pluginsBox.hide()
        
        toolbarsLayout = QHBoxLayout()
        toolbarsLayout.addWidget(self.exportBox)
        toolbarsLayout.addWidget(self.insertBox)
        toolbarsLayout.addWidget(self.clipboardBox)
        toolbarsLayout.addWidget(self.miscBox)
        toolbarsLayout.addWidget(self.adaptersBox)
        toolbarsLayout.addWidget(self.globalGroupBox)
        toolbarsLayout.addWidget(self.infoGroupBox)
        toolbarsLayout.addWidget(self.optsBox)
        toolbarsLayout.addWidget(self.pluginsBox)
        toolbarsLayout.addWidget(self.generateBox)
        toolbarsLayout.addStretch(1)
        toolbarsLayout.setContentsMargins(0,0,0,0)
        
        self.tcPurposeLine = QLineEdit(self)
        self.tcPurposeLine.setText("Testcase generated by test assistant")

        tcLayout = QHBoxLayout()
        tcLayout.addWidget( QLabel( self.tr("Testcase Purpose:") ) )
        tcLayout.addWidget( self.tcPurposeLine )

        listLayoutGlobalGroup = QVBoxLayout()
        listLayoutGlobalGroup.addLayout(toolbarsLayout)
        listLayoutGlobalGroup.addLayout(tcLayout)
        
        listLayoutGroup = QGridLayout()
        listLayoutGroup.addWidget(self.stepsTable, 0, 0)

        listLayoutGlobalGroup.addLayout(listLayoutGroup)
        listLayoutGlobalGroup.setContentsMargins(0,0,0,0)
        
        listGroup.setLayout(listLayoutGlobalGroup)
        listGroup.setMinimumHeight(300)
        
        
        ###################### final layout #########################

        self.sikuliGroup = GuiSikuli.WSikuliX(self)
        self.seleniumGroup = GuiSelenium.WSelenium(self)
        self.androidGroup = GuiAndroid.WAndroid(self)
        self.frameworkGroup = Framework.WFramework(self)
        self.sshGroup = System.WSystem(self)

        self.masterTab = QTabWidget()

        self.masterTab.addTab( self.frameworkGroup,  QIcon(":/recorder-basic-small.png"), self.tr("Framework") )
        self.masterTab.addTab( self.sshGroup,  QIcon(":/system-small.png"), self.tr("System") )
        self.masterTab.addTab( self.sikuliGroup, QIcon(":/recorder-app-small.png"), self.tr("Application") )
        self.masterTab.addTab( self.seleniumGroup, QIcon(":/recorder-web-small.png"), self.tr("Browser") )
        self.masterTab.addTab( self.androidGroup,  QIcon(":/recorder-mobile-small.png"), self.tr("Android") )

        self.masterTab.setTabPosition(QTabWidget.South)

        self.hSplitter = QSplitter(self)
        self.hSplitter.setOrientation(Qt.Vertical)
        
        self.hSplitter.addWidget(listGroup)
        self.hSplitter.addWidget(self.masterTab)
        self.hSplitter.setStretchFactor(0, 1)

        layoutFinal = QVBoxLayout()
        layoutFinal.addWidget(self.hSplitter)

        self.setWindowState(Qt.WindowMaximized)
        self.setLayout(layoutFinal)

    def createToolbar(self):
        """
        Create toolbar
        """
        self.dockToolbar2.setObjectName("Toolbar 2")
        self.dockToolbar2.addAction(self.stepsTable.editAction)
        self.dockToolbar2.addAction(self.stepsTable.upAction)
        self.dockToolbar2.addAction(self.stepsTable.downAction)
        self.dockToolbar2.addAction(self.stepsTable.delAction)
        self.dockToolbar2.addAction(self.clearStepsAction)
        self.dockToolbar2.setIconSize(QSize(16, 16))

        self.dockToolbar3.setObjectName("Toolbar 3")
        self.dockToolbar3.addAction(self.cancelAction)
        self.dockToolbar3.setIconSize(QSize(16, 16))
        
        self.dockToolbarMiscs.setObjectName("Toolbar Miscs")
        self.dockToolbarMiscs.addAction(self.stepsTable.enableAction)
        self.dockToolbarMiscs.addAction(self.stepsTable.disableAction)
        self.dockToolbarMiscs.setIconSize(QSize(16, 16))
        
        self.dockToolbarClipboard.setObjectName("Toolbar Clipboard")
        self.dockToolbarClipboard.addAction(self.stepsTable.copyAction)
        self.dockToolbarClipboard.setIconSize(QSize(16, 16))
        
        self.dockToolbarClipboard2.setObjectName("Toolbar Clipboard")
        self.dockToolbarClipboard2.addAction(self.stepsTable.pasteAction)
        self.dockToolbarClipboard2.setIconSize(QSize(16, 16))
        
        self.dockToolbarExport.setObjectName("Toolbar 3")
        self.dockToolbarExport.addAction(self.exportTSAction)
        self.dockToolbarExport.addAction(self.exportTUAction)
        self.dockToolbarExport.addAction(self.updateStepsAction)
        self.dockToolbarExport.setIconSize(QSize(16, 16))
        
        self.dockToolbarOptions.setObjectName("Toolbar Options")
        self.dockToolbarOptions.addAction(self.frameworkGroup.optionsAction)
        self.dockToolbarOptions.addAction(self.sikuliGroup.optionsAction)
        self.dockToolbarOptions.addAction(self.seleniumGroup.optionsAction)
        self.dockToolbarOptions.setIconSize(QSize(16, 16))
        
        self.dockToolbarOptions2.setObjectName("Toolbar Options")
        self.dockToolbarOptions2.addAction(self.androidGroup.optionsAction)
        self.dockToolbarOptions2.addAction(self.sshGroup.optionsAction)
        self.dockToolbarOptions2.setIconSize(QSize(16, 16))
        
    def addPlugin(self, action):
        """
        Add plugin in toolbar
        """
        self.dockToolbarPlugins.addAction(action)
        self.pluginsBox.show()
        
    def cleanup(self):
        """
        Cleanup
        """

    def createConnections(self):
        """
        Create toolbar
        """
        self.stepsTable.EditStep.connect(self.onEditStep)
        self.stepsTable.StepDeleted.connect(self.onStepRemoved)
        
        self.sikuliGroup.TakeSnapshot.connect(self.onTakeSnapshot)
        self.sikuliGroup.TakeMousePosition.connect(self.onTakeMousePosition)
        self.sikuliGroup.TakeMouseLocation.connect(self.onTakeMouseLocation)
       
        self.sikuliGroup.AddStep.connect(self.onAddSikuliStep)
        self.androidGroup.AddStep.connect(self.onAddAndroidStep)
        self.seleniumGroup.AddStep.connect(self.onAddSeleniumStep)
        self.frameworkGroup.AddStep.connect(self.onAddFrameworkStep)
        self.sshGroup.AddStep.connect(self.onAddSshStep)
        
        self.sikuliGroup.UpdateStep.connect(self.onUpdateSikuliStep)
        self.androidGroup.UpdateStep.connect(self.onUpdateAndroidStep)
        self.seleniumGroup.UpdateStep.connect(self.onUpdateSeleniumStep)
        self.frameworkGroup.UpdateStep.connect(self.onUpdateFrameworkStep)
        self.sshGroup.UpdateStep.connect(self.onUpdateSshStep)
        
        self.sikuliGroup.CancelEdit.connect(self.cancelStep)
        self.androidGroup.CancelEdit.connect(self.cancelAndroidStep)
        self.seleniumGroup.CancelEdit.connect(self.cancelBrStep)
        self.frameworkGroup.CancelEdit.connect(self.cancelFrameworkStep)
        self.sshGroup.CancelEdit.connect(self.cancelSshStep)
        
    def onCurrentTabChanged(self, index):
        """
        On current tabulation changed
        """
        self.stepsTable.setUnboldAll()
        
    def onCancelStep(self):
        """
        On cancel a step
        """
        self.seleniumGroup.setEnabled(True)
        self.sikuliGroup.setEnabled(True)
        self.androidGroup.setEnabled(True)
        self.frameworkGroup.setEnabled(True)
        self.sshGroup.setEnabled(True)
        
    def sikuli(self):
        """
        Return sikuli widget
        """
        return self.sikuliGroup
        
    def selenium(self):
        """
        Return selenium widget
        """
        return self.seleniumGroup
        
    def android(self):
        """
        Return android widget
        """
        return self.androidGroup
        
    def framework(self):
        """
        Return framework widget
        """
        return self.frameworkGroup
        
    def system(self):
        """
        Return system widget
        """
        return self.sshGroup
        
    def cancelStep(self):
        """
        Cancel step
        """
        self.stepId = 0

        self.seleniumGroup.setEnabled(True)
        self.sikuliGroup.setEnabled(True)
        self.androidGroup.setEnabled(True)
        self.frameworkGroup.setEnabled(True)
        self.sshGroup.setEnabled(True)

        self.masterTab.setEnabled(True)
        
        self.stepsTable.setEnabled(True)
        
    def cancelBrStep(self):
        """
        Cancel browser step
        """
        self.stepId = 0

        self.seleniumGroup.setEnabled(True)
        self.sikuliGroup.setEnabled(True)
        self.androidGroup.setEnabled(True)
        self.frameworkGroup.setEnabled(True)
        self.sshGroup.setEnabled(True)

        self.masterTab.setEnabled(True)
        
        self.stepsTable.setEnabled(True)
        
    def cancelAndroidStep(self):
        """
        Cancel android step
        """
        self.stepId = 0

        self.seleniumGroup.setEnabled(True)
        self.sikuliGroup.setEnabled(True)
        self.androidGroup.setEnabled(True)
        self.frameworkGroup.setEnabled(True)
        self.sshGroup.setEnabled(True)

        self.masterTab.setEnabled(True)
        
        self.stepsTable.setEnabled(True)
        
    def cancelFrameworkStep(self):
        """
        Cancel android step
        """
        self.stepId = 0

        self.seleniumGroup.setEnabled(True)
        self.sikuliGroup.setEnabled(True)
        self.androidGroup.setEnabled(True)
        self.frameworkGroup.setEnabled(True)
        self.sshGroup.setEnabled(True)

        self.masterTab.setEnabled(True)
        
        self.stepsTable.setEnabled(True)
        
    def cancelSshStep(self):
        """
        Cancel android step
        """
        self.stepId = 0

        self.seleniumGroup.setEnabled(True)
        self.sikuliGroup.setEnabled(True)
        self.androidGroup.setEnabled(True)
        self.frameworkGroup.setEnabled(True)
        self.sshGroup.setEnabled(True)

        self.masterTab.setEnabled(True)
        
        self.stepsTable.setEnabled(True)
        
    def focusWebPart(self):
        """
        Activate the web tabulation
        """
        self.masterTab.setCurrentIndex(POS_TAB_WEB)

    def focusMobPart(self):
        """
        Activate the mobile android tabulation
        """
        self.masterTab.setCurrentIndex(POS_TAB_ANDROID)
        
    def focusAppPart(self):
        """
        Activate the application tabulation
        """
        self.masterTab.setCurrentIndex(POS_TAB_APP)

    def focusBasPart(self):
        """
        Activate the basic tabulation
        """
        self.masterTab.setCurrentIndex(POS_TAB_BASIC)

    def focusSysPart(self):
        """
        Activate the system tabulation
        """
        self.masterTab.setCurrentIndex(POS_TAB_SSH)
        
    def onEditStep(self, stepData):
        """
        On edit step
        """
        # self.editMode = True
        self.stepId = stepData['id']
        
        # add default value and key if missing
        if "action-type" not in stepData:  stepData["action-type"] = GuiSteps.ACTION_ANYTHING
        
        # new in v12
        if "option-similar" not in stepData:  stepData["option-similar"] = self.DEFAULT_SIMILAR_VALUE
        
        # dispatch according to the action type
        if stepData["action-type"] == GuiSteps.ACTION_ANYTHING:
            self.masterTab.setEnabled(True)
            self.masterTab.setCurrentIndex(POS_TAB_APP)

            self.seleniumGroup.setEnabled(False)
            self.sikuliGroup.setEnabled(True)
            self.androidGroup.setEnabled(False)
            self.sshGroup.setEnabled(False)
            
            self.sikuliGroup.editStep(stepData=stepData)
            
        if stepData["action-type"] == GuiSteps.ACTION_ANDROID:
            self.masterTab.setEnabled(True)
            self.masterTab.setCurrentIndex(POS_TAB_ANDROID)

            self.seleniumGroup.setEnabled(False)
            self.sikuliGroup.setEnabled(False)
            self.androidGroup.setEnabled(True)
            self.sshGroup.setEnabled(False)
            
            self.androidGroup.editStep(stepData=stepData)

        if stepData["action-type"] == GuiSteps.ACTION_BROWSER:
            self.masterTab.setEnabled(True)
            self.masterTab.setCurrentIndex(POS_TAB_WEB)

            self.seleniumGroup.setEnabled(True)
            self.sikuliGroup.setEnabled(False)
            self.androidGroup.setEnabled(False)
            self.sshGroup.setEnabled(False)
            
            self.seleniumGroup.editStep(stepData=stepData)
            
        if stepData["action-type"] == GuiSteps.ACTION_FRAMEWORK:
            self.masterTab.setEnabled(True)
            self.masterTab.setCurrentIndex(POS_TAB_BASIC)
            
            self.seleniumGroup.setEnabled(False)
            self.sikuliGroup.setEnabled(False)
            self.androidGroup.setEnabled(False)
            self.frameworkGroup.setEnabled(True)
            
            self.frameworkGroup.editStep(stepData=stepData)
            
        if stepData["action-type"] == GuiSteps.ACTION_SYSTEM:
            self.masterTab.setEnabled(True)
            self.masterTab.setCurrentIndex(POS_TAB_SSH)
            
            self.sshGroup.setEnabled(True)
            self.seleniumGroup.setEnabled(False)
            self.sikuliGroup.setEnabled(False)
            self.androidGroup.setEnabled(False)
            
            self.sshGroup.editStep(stepData=stepData)
            
    def exportToTS(self):
        """
        Export to test suite
        """
        self.exportToTest(TS=True, TU=False)

    def exportToTU(self):
        """
        Export to test unit
        """
        self.exportToTest(TS=False, TU=True)

    def updateTest(self):
        """
        Update test
        """
        if self.currentDocument is None:
            self.updateStepsAction.setEnabled(False)
            return
        
        (newTest, newInputs, agentTpl) = self.exportToTest(TS=self.isTs, TU=self.isTu, updateTest=True)

        # update main test
        self.currentDocument.srcEditor.setText(newTest)
        self.currentDocument.srcEditor.foldAllLines()

        # update test properties
        self.currentDocument.dataModel.properties['properties']['inputs-parameters']['parameter'] = newInputs
        self.currentDocument.dataModel.properties['properties']['agents']['agent'] = agentTpl
        WWorkspace.DocumentProperties.instance().parameters.table().loadData( data ={'parameter': newInputs} )
        WWorkspace.DocumentProperties.instance().agents.table().loadData( data ={'agent': agentTpl} )

        self.close()
    
    def parseSearch(self, searchBy, j, fromCache=False):
        """
        Parse search
        """
        args = "name=None, tagName=None, className=None, id=None, xpath=None, linkText=None, partialLinkText=None, cssSelector=None"
        if searchBy == GuiSelenium.BROWSER_BY_NAME:
            if fromCache:
                args = args.replace("name=None", "name=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j )
            else:
                args = args.replace("name=None", "name=input('BROWSER_TEXT_BY_%s')" % j )
        if searchBy == GuiSelenium.BROWSER_BY_TAG_NAME:
            if fromCache:
                args = args.replace("tagName=None", "tagName=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j )
            else:
                args = args.replace("tagName=None", "tagName=input('BROWSER_TEXT_BY_%s')" % j )
        if searchBy == GuiSelenium.BROWSER_BY_CLASS_NAME:
            if fromCache:
                args = args.replace("className=None", "className=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j ) 
            else:
                args = args.replace("className=None", "className=input('BROWSER_TEXT_BY_%s')" % j ) 
        if searchBy == GuiSelenium.BROWSER_BY_ID:
            if fromCache:
                args = args.replace("id=None", "id=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j ) 
            else:
                args = args.replace("id=None", "id=input('BROWSER_TEXT_BY_%s')" % j ) 
        if searchBy == GuiSelenium.BROWSER_BY_XPATH:
            if fromCache:
                args = args.replace("xpath=None", "xpath=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j ) 
            else:
                args = args.replace("xpath=None", "xpath=input('BROWSER_TEXT_BY_%s')" % j ) 
        if searchBy == GuiSelenium.BROWSER_BY_LINK_TEXT:
            if fromCache:
                args = args.replace("linkText=None", "linkText=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j ) 
            else:
                args = args.replace("linkText=None", "linkText=input('BROWSER_TEXT_BY_%s')" % j ) 
        if searchBy == GuiSelenium.BROWSER_BY_PARTIAL_LINK_TEXT:
            if fromCache:
                args = args.replace("partialLinkText=None", "partialLinkText=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j ) 
            else:
                args = args.replace("partialLinkText=None", "partialLinkText=input('BROWSER_TEXT_BY_%s')" % j ) 
        if searchBy == GuiSelenium.BROWSER_BY_CSS_SELECTOR:
            if fromCache:
                args = args.replace("cssSelector=None", "cssSelector=Cache().get(name=input('BROWSER_TEXT_BY_%s'))" % j ) 
            else:
                args = args.replace("cssSelector=None", "cssSelector=input('BROWSER_TEXT_BY_%s')" % j ) 
        return args
        
    def searchGUI(self):
        """
        Search GUI module in assistant
        """
        # modules accessor
        ret = "SutAdapters"
        if self.automaticAdp.isChecked():
            isGeneric = WWorkspace.Helper.instance().isGuiGeneric(name="GUI")
            if isGeneric:
                ret =  "SutAdapters.Generic"
        elif self.defaultAdp.isChecked():
            return ret
        elif self.genericAdp.isChecked():
            ret =  "SutAdapters.Generic"
        else:
            pass
        return ret
        
    def checkDuplicateAlias(self, inputs, alias):
        """
        Check all alias duplicated
        """
        duplicate = False
        for inp in inputs:
            if inp['name'] == alias: 
                duplicate = True
                break
        return duplicate
        
    def exportToTest(self, TS=True, TU=False, updateTest=False):
        """
        Export steps
        """
        if not self.offlineMode:
            if not UCI.instance().isAuthenticated():
                QMessageBox.warning(self, "Assistant Automation" , "Connect to the test center in first!")
                return

        if TS:
            newTest = self.defaultTemplates.getTestDefinitionAuto()
            newTestExec = self.defaultTemplates.getTestExecutionAuto()
        if TU:
            newTest = self.defaultTemplates.getTestUnitDefinitionAuto()

        stepsReg = self.stepsTable.getData()
        if sys.version_info < (3,):
            for s in stepsReg:
                s["description"] = unicode(s["description"])

        # detect id browser is present
        browserStepDetected = False
        for i in xrange(len(stepsReg)):
            if stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_USERCODE, GuiSteps.FRAMEWORK_WAIT ]:
                continue
                
            if "action-type" not in stepsReg[i]:
                stepsReg[i]["action-type"] = GuiSteps.ACTION_ANYTHING
                
            if stepsReg[i]["action-type"] == GuiSteps.ACTION_BROWSER:
                browserStepDetected = True
                break
                
        anythingStepDetected = False
        for i in xrange(len(stepsReg)):
            if stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_USERCODE , GuiSteps.FRAMEWORK_WAIT ]:
                continue
                
            if "action-type" not in stepsReg[i]:
                stepsReg[i]["action-type"] = GuiSteps.ACTION_ANYTHING
                
            if stepsReg[i]["action-type"] == GuiSteps.ACTION_ANYTHING:
                anythingStepDetected = True
                break
        
        # detect id browser is present
        androidStepDetected = False
        for i in xrange(len(stepsReg)):
            if stepsReg[i]['action'] in [GuiSteps.FRAMEWORK_USERCODE, GuiSteps.FRAMEWORK_WAIT ] :
                continue
                
            if "action-type" not in stepsReg[i]:
                stepsReg[i]["action-type"] = GuiSteps.ACTION_ANYTHING
                
            if stepsReg[i]["action-type"] == GuiSteps.ACTION_ANDROID:
                androidStepDetected = True
                break
        
        # detect if framework action is present
        frameworkStepDetected = False
        for i in xrange(len(stepsReg)):
            if stepsReg[i]["action-type"] == GuiSteps.ACTION_FRAMEWORK:
                frameworkStepDetected = True
                break
                
        # detect if framework action is present
        sysStepDetected = False
        for i in xrange(len(stepsReg)):
            if stepsReg[i]["action-type"] == GuiSteps.ACTION_SYSTEM:
                sysStepDetected = True
                break
                
        # set the agent
        agentKeyName = self.sikuliGroup.getAgentName() 
        agentBrowserKeyName = self.seleniumGroup.getAgentName() 
        agentAndroidKeyName = self.androidGroup.getAgentName() 
        agentSystemKeyName = self.sshGroup.getAgentName() 
        
        # init adapter
        adpsGui = [ ]
        self.searchGUI()
        if anythingStepDetected:
            adpsGui.append( "self.ADP_GUI = %s.GUI.Sikuli(parent=self, agent=agent('%s'), debug=input('DEBUG'))" % (self.searchGUI(), str(agentKeyName))  )
        if browserStepDetected:
            adpsGui.append( "self.ADP_GUI_BROWSER = %s.GUI.Selenium(parent=self, agent=agent('%s'), debug=input('DEBUG'), navigId=Cache().get(name='selenium-navig-id'))" % (self.searchGUI(),str(agentBrowserKeyName)) )
        if androidStepDetected:
            adpsGui.append( "self.ADP_ANDROID = %s.GUI.Adb(parent=self, agent=agent('%s'), debug=input('DEBUG'))" % (self.searchGUI(), str(agentAndroidKeyName))  )

        # construct new inputs
        newInputs = []
                
        newInputs.extend( self.userParams  )
        
        j = 0
        # z = 0
        openBrowserDetected = False
        for i in xrange(len(stepsReg)):
            if stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_USERCODE ]:
                # z += 1
                pass
            else:
                # j = i + 1 - z
                j = i + 1 

                # system
                if stepsReg[i]["action-type"] == GuiSteps.ACTION_SYSTEM:
                    if stepsReg[i]['action'] in [ GuiSteps.SYSTEM_SESSION ]:
                        if stepsReg[i]['parameters']['from-alias-login']:
                            newInputs.append( {'type': 'alias', 'name': 'SYS_LOGIN', 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['login'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['login']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['login'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } ) 
                        elif stepsReg[i]['parameters']['from-cache-login']: 
                            newInputs.append( {'type': 'str', 'name': 'SYS_LOGIN_KEY' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['login']), 'color': '' } ) 
                        else:
                            newInputs.append( {'type': 'str', 'name': 'SYS_LOGIN' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['login']), 'color': '' } ) 
                                        
                        if stepsReg[i]['parameters']['from-alias-pwd']:
                            newInputs.append( {'type': 'alias', 'name': 'SYS_PWD', 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['password'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['password']):
                                newInputs.append( {'type': 'pwd', 'name': stepsReg[i]['parameters']['password'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )   
                        elif stepsReg[i]['parameters']['from-cache-pwd']: 
                            newInputs.append( {'type': 'pwd', 'name': 'SYS_PWD_KEY' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['password']), 'color': '' } )           
                        else:
                            newInputs.append( {'type': 'pwd', 'name': 'SYS_PWD' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['password']), 'color': '' } ) 
                                        
                        if stepsReg[i]['parameters']['from-alias-ip']:
                            newInputs.append( {'type': 'alias', 'name': 'SYS_DEST_HOST', 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['dest-ip'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['dest-ip']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['dest-ip'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )  
                        elif stepsReg[i]['parameters']['from-cache-ip']: 
                            newInputs.append( {'type': 'str', 'name': 'SYS_DEST_HOST_KEY' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['dest-ip']), 'color': '' } )                   
                        else:
                            newInputs.append( {'type': 'str', 'name': 'SYS_DEST_HOST' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['dest-ip']), 'color': '' } ) 
                                        
                        if stepsReg[i]['parameters']['from-alias-port']:
                            newInputs.append( {'type': 'alias', 'name': 'SYS_DEST_PORT', 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['dest-port'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['dest-port']):
                                newInputs.append( {'type': 'int', 'name': stepsReg[i]['parameters']['dest-port'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )   
                        elif stepsReg[i]['parameters']['from-cache-port']: 
                            newInputs.append( {'type': 'int', 'name': 'SYS_DEST_PORT_KEY' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['dest-port']), 'color': '' } )               
                        else:
                            newInputs.append( {'type': 'int', 'name': 'SYS_DEST_PORT' , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['dest-port']), 'color': '' } ) 
                                        
                        newInputs.append( {'type': 'bool', 'name': 'SYS_AGT_SUPPORT' , 'description': stepsReg[i]['description'],
                                            'value' : str(stepsReg[i]['parameters']['agent-support']), 'color': '' } )      
                    if stepsReg[i]['action'] in [ GuiSteps.SYSTEM_TEXT ]:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'SYS_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['text'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['text']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['text'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )    
                        else:
                            newInputs.append( {'type': 'str', 'name': 'SYS_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['text'], 'color': '' } )  
                    if stepsReg[i]['action'] in [  GuiSteps.SYSTEM_CHECK_SCREEN ]:
                        if stepsReg[i]['parameters']['operator'] != GuiSteps.OP_ANY:
                            if stepsReg[i]['parameters']['from-alias']:
                                newInputs.append( {'type': 'alias', 'name': 'SYS_SCREEN_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['parameters']['value'], 'color': '' } )    
                                if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['value']):
                                    newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['value'] , 
                                                        'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )    
                            else:
                                newInputs.append( {'type': 'str', 'name': 'SYS_SCREEN_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['parameters']['value'], 'color': '' } )  
                        if stepsReg[i]['parameters']['to-cache']:
                            newInputs.append( {'type': 'str', 'name': 'SYS_CACHE_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['cache-key'], 'color': '' } )  
                            
                # framework
                elif stepsReg[i]["action-type"] == GuiSteps.ACTION_FRAMEWORK:
                    if stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_INFO, GuiSteps.FRAMEWORK_WARNING ]:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'FWK_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['text'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['text']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['text'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )    
                        else:
                            newInputs.append( {'type': 'str', 'name': 'FWK_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['text'], 'color': '' } )     
                                        
                    elif stepsReg[i]['action'] == GuiSteps.FRAMEWORK_WAIT:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'FWK_WAIT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['misc']), 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=str(stepsReg[i]['misc'])):
                                newInputs.append( {'type': 'int', 'name': str(stepsReg[i]['misc']) , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )    
                        elif stepsReg[i]['parameters']['from-cache']:  
                            newInputs.append( {'type': 'str', 'name': 'FWK_WAIT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['misc']), 'color': '' } )   
                        else:
                            newInputs.append( {'type': 'int', 'name': 'FWK_WAIT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['misc']), 'color': '' } )     

                    elif stepsReg[i]['action'] == GuiSteps.FRAMEWORK_CACHE_SET:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'FWK_CACHE_VALUE_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['value'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['value']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['value'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )    
                        else:
                            newInputs.append( {'type': 'str', 'name': 'FWK_CACHE_VALUE_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['value'], 'color': '' } )     
                        newInputs.append( {'type': 'str', 'name': 'FWK_CACHE_KEY_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['parameters']['key'], 'color': '' } )
                                        
                    elif stepsReg[i]['action'] == GuiSteps.FRAMEWORK_CHECK_STRING:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'FWK_CHECK_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['value'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['value']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['value'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )       
                        else:
                            newInputs.append( {'type': 'str', 'name': 'FWK_CHECK_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['value']), 'color': '' } )     
                        newInputs.append( {'type': 'str', 'name': 'FWK_CHECK_KEY_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : str(stepsReg[i]['parameters']['key']), 'color': '' } )        
                                        
                    elif stepsReg[i]['action'] == GuiSteps.FRAMEWORK_INTERACT:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'FWK_ASK_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['value'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['value']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['value'] , 
                                                    'description': stepsReg[i]['description'],  'value' : '', 'color': '' } )       
                        else:
                            newInputs.append( {'type': 'str', 'name': 'FWK_ASK_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : str(stepsReg[i]['parameters']['value']), 'color': '' } )     
                        newInputs.append( {'type': 'str', 'name': 'FWK_ASK_KEY_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : str(stepsReg[i]['parameters']['key']), 'color': '' } )      
                                            
                # android    
                elif stepsReg[i]["action-type"] == GuiSteps.ACTION_ANDROID:
                    if stepsReg[i]['action'] in [ GuiSteps.ANDROID_WAIT_ELEMENT, GuiSteps.ANDROID_CLEAR_ELEMENT, GuiSteps.ANDROID_CLICK_ELEMENT,
                                                     GuiSteps.ANDROID_LONG_CLICK_ELEMENT, GuiSteps.ANDROID_EXIST_ELEMENT, GuiSteps.ANDROID_TYPE_TEXT_ELEMENT,
                                                     GuiSteps.ANDROID_GET_TEXT_ELEMENT, GuiSteps.ANDROID_DRAG_ELEMENT, GuiSteps.ANDROID_WAIT_CLICK_ELEMENT ] :
                        if 'text' in stepsReg[i]['parameters']:                             
                            if len(stepsReg[i]['parameters']['text']):
                                if stepsReg[i]['parameters']['from-el-alias']:
                                    newInputs.append( {'type': 'alias', 'name': 'ANDROID_UI_TXT_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['text'], 'color': '' } )
                                    if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['text']):
                                        newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['text'] , 'description': '',  'value' : '', 'color': '' } )
                                else:
                                    newInputs.append( {'type': 'str', 'name': 'ANDROID_UI_TXT_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['text'], 'color': '' } )
                        if 'description' in stepsReg[i]['parameters']:            
                            if len(stepsReg[i]['parameters']['description']):
                                newInputs.append( {'type': 'str', 'name': 'ANDROID_UI_DESCR_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['description'], 'color': '' } )  
                        if 'class' in stepsReg[i]['parameters']:            
                            if len(stepsReg[i]['parameters']['class']):
                                newInputs.append( {'type': 'str', 'name': 'ANDROID_UI_CLS_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['class'], 'color': '' } )  
                        if 'ressource' in stepsReg[i]['parameters']:            
                            if len(stepsReg[i]['parameters']['ressource']):
                                newInputs.append( {'type': 'str', 'name': 'ANDROID_UI_RES_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['ressource'], 'color': '' } )  
                        if 'package' in stepsReg[i]['parameters']:            
                            if len(stepsReg[i]['parameters']['package']):
                                newInputs.append( {'type': 'str', 'name': 'ANDROID_UI_PKG_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['package'], 'color': '' } )   
                            
                    if stepsReg[i]['action'] in [ GuiSteps.ANDROID_CLICK_POSITION, GuiSteps.ANDROID_DRAG_ELEMENT ] :
                        if len(stepsReg[i]['parameters']['x']):
                            newInputs.append( {'type': 'int', 'name': 'ANDROID_UI_X_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['x'], 'color': '' } )  
                        if len(stepsReg[i]['parameters']['y']):
                            newInputs.append( {'type': 'int', 'name': 'ANDROID_UI_Y_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['y'], 'color': '' } )  
                            
                    if stepsReg[i]['action'] in [ GuiSteps.ANDROID_DRAG_POSITION, GuiSteps.ANDROID_SWIPE_POSITION ] :
                        if len(stepsReg[i]['parameters']['start-x']):
                            newInputs.append( {'type': 'int', 'name': 'ANDROID_UI_START_X_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['start-x'], 'color': '' } )  
                        if len(stepsReg[i]['parameters']['start-y']):
                            newInputs.append( {'type': 'int', 'name': 'ANDROID_UI_START_Y_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['start-y'], 'color': '' } )  
                        if len(stepsReg[i]['parameters']['stop-x']):
                            newInputs.append( {'type': 'int', 'name': 'ANDROID_UI_STOP_X_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['stop-x'], 'color': '' } )  
                        if len(stepsReg[i]['parameters']['stop-y']):
                            newInputs.append( {'type': 'int', 'name': 'ANDROID_UI_STOP_Y_%s' % j , 'description': '',  'value' : stepsReg[i]['parameters']['stop-y'], 'color': '' } )  

                    if stepsReg[i]['action'] == GuiSteps.ANDROID_COMMAND:
                        newInputs.append( {'type': 'str', 'name': 'ANDROID_CMD_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['cmd'], 'color': '' } )
                                        
                    if stepsReg[i]['action'] == GuiSteps.ANDROID_SHELL:
                        newInputs.append( {'type': 'str', 'name': 'ANDROID_SH_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['sh'], 'color': '' } )
                                        
                    if stepsReg[i]['action'] in [ GuiSteps.ANDROID_RESET_APP, GuiSteps.ANDROID_STOP_APP ]:
                        newInputs.append( {'type': 'str', 'name': 'ANDROID_PKG_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['pkg'], 'color': '' } )
                                        
                    if stepsReg[i]['action'] == GuiSteps.ANDROID_TYPE_TEXT_ELEMENT:
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'ANDROID_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['new-text'], 'color': '' } )    
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['new-text']):
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['new-text'] , 'description': stepsReg[i]['description'],
                                        'value' : '', 'color': '' } )    
                        else:
                            newInputs.append( {'type': 'str', 'name': 'ANDROID_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['new-text'], 'color': '' } )             
                    
                    elif stepsReg[i]['action'] == GuiSteps.ANDROID_GET_TEXT_ELEMENT:
                        if "to-cache" in stepsReg[i]['parameters']:
                            if stepsReg[i]['parameters']['to-cache']:
                                newInputs.append( {'type': 'str', 'name': 'ANDROID_CACHE_%s' % j , 'description': stepsReg[i]['description'], 
                                                    'value' : stepsReg[i]['parameters']['cache-key'], 'color': '' } )
                
                # browser
                elif stepsReg[i]["action-type"] == GuiSteps.ACTION_BROWSER:
                    if 'from-alias' not in stepsReg[i]: # for backward compatibility
                        stepsReg[i]['from-alias'] = False
                        
                    # selenium  
                    if stepsReg[i]['action'] == GuiSteps.BROWSER_OPEN:
                        # adding input only one time
                        # if openBrowserDetected:
                            # continue
                            
                        openBrowserDetected = True    
                        
                        # set the browser selected
                        isFirefox = "False"
                        isIe = "False"
                        isChrome = "False"
                        isOpera = "False"
                        isEdge = "False"
                        useGecko = "True"
                        if str(stepsReg[i]['misc']) == GuiSelenium.BROWSER_FIREFOX: isFirefox = "True"
                        if str(stepsReg[i]['misc']) == GuiSelenium.BROWSER_IE: isIe = "True"
                        if str(stepsReg[i]['misc']) == GuiSelenium.BROWSER_CHROME: isChrome = "True"
                        if str(stepsReg[i]['misc']) == GuiSelenium.BROWSER_OPERA: isOpera = "True"
                        if str(stepsReg[i]['misc']) == GuiSelenium.BROWSER_EDGE: isEdge = "True"
                        
                        # adding default step
                        newInputs.append( {'type': 'bool', 'name': 'BROWSER_USE_FIREFOX_%s' % j, 'description': '',  'value' : isFirefox, 'color': '' } )
                        newInputs.append( {'type': 'bool', 'name': 'BROWSER_USE_IE_%s' % j, 'description': '',  'value' : isIe, 'color': '' } )
                        newInputs.append( {'type': 'bool', 'name': 'BROWSER_USE_CHROME_%s' % j , 'description': '',  'value' : isChrome, 'color': '' } )
                        newInputs.append( {'type': 'bool', 'name': 'BROWSER_USE_OPERA_%s' % j , 'description': '',  'value' : isOpera, 'color': '' } )
                        newInputs.append( {'type': 'bool', 'name': 'BROWSER_USE_EDGE_%s' % j , 'description': '',  'value' : isEdge, 'color': '' } )
                        # newInputs.append( {'type': 'bool', 'name': 'BROWSER_DRIVER_GECKO_%s' % j , 'description': '',  'value' : useGecko, 'color': '' } )
                        
                        # adding url
                        if stepsReg[i]["parameters"]['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                        'value' : stepsReg[i]['text'], 'color': '' } )
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text']):            
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text'] , 'description': stepsReg[i]['description'], 
                                            'value' : '', 'color': '' } )
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                        'value' : stepsReg[i]['text'], 'color': '' } )

                        if "session-name" in stepsReg[i]["parameters"]:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_SESSION_%s' % j , 'description': stepsReg[i]['description'], 
                                        'value' : stepsReg[i]["parameters"]['session-name'], 'color': '' } )
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_SESSION_%s' % j , 'description': stepsReg[i]['description'], 
                                        'value' : "default", 'color': '' } )

                        if "use-gecko" in stepsReg[i]["parameters"]:
                            newInputs.append( {'type': 'bool', 'name': 'BROWSER_DRIVER_GECKO_%s' % j , 'description': stepsReg[i]['description'], 
                                        'value' : "%s" % stepsReg[i]["parameters"]['use-gecko'], 'color': '' } )
                        else:
                            newInputs.append( {'type': 'bool', 'name': 'BROWSER_DRIVER_GECKO_%s' % j , 'description': stepsReg[i]['description'], 
                                        'value' : "True", 'color': '' } )
                                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_CLOSE:
                        pass
                    
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_MAXIMIZE:
                        pass
                    
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_CLOSE_WINDOW:
                        pass
                    
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_NEXT_WINDOW:
                        pass
                    
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_MAIN_WINDOW:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_REFRESH:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_GO_BACK:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_GO_FORWARD:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_DISMISS_ALERT:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_ACCEPT_ALERT:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_GET_URL:
                        if stepsReg[i]["parameters"]['to-cache']:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text-more'], 'color': '' } )
                            
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_GET_SOURCE:
                        if stepsReg[i]["parameters"]['to-cache']:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                            'value' : stepsReg[i]['text-more'], 'color': '' } )
                            
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_GET_TITLE:
                        if stepsReg[i]["parameters"]['to-cache']:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['text-more'], 'color': '' } )
                            
                    elif stepsReg[i]['action'] == GuiSteps.BROWSER_GET_TEXT_ALERT:
                        if stepsReg[i]["parameters"]['to-cache']:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                            'value' : stepsReg[i]['text-more'], 'color': '' } )
                            
                    elif stepsReg[i]['action'] in [ GuiSteps.BROWSER_SWITCH_TO_FRAME, GuiSteps.BROWSER_WAIT_ELEMENT, GuiSteps.BROWSER_HOVER_ELEMENT, 
                                                    GuiSteps.BROWSER_CLICK_ELEMENT, GuiSteps.BROWSER_DOUBLE_CLICK_ELEMENT,
                                                    GuiSteps.BROWSER_TYPE_KEY, GuiSteps.BROWSER_WAIT_CLICK_ELEMENT, GuiSteps.BROWSER_CLEAR_TEXT_ELEMENT,
                                                    GuiSteps.BROWSER_WAIT_VISIBLE_ELEMENT, GuiSteps.BROWSER_WAIT_VISIBLE_CLICK_ELEMENT,
                                                    GuiSteps.BROWSER_WAIT_NOT_VISIBLE_ELEMENT ] :
                        if stepsReg[i]["parameters"]['from-el-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'BROWSER_TEXT_BY_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } ) 
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text'].upper()):                                
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text'].upper() , 'description': stepsReg[i]['description'], 
                                                'value' : '', 'color': '' } )   
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_BY_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } )      
                                                
                    elif stepsReg[i]['action'] in [ GuiSteps.BROWSER_GET_TEXT_ELEMENT ] : 
                        if stepsReg[i]["parameters"]['to-cache']:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'],  
                                            'value' : stepsReg[i]['text-more'], 'color': '' } )
                                            
                        if stepsReg[i]["parameters"]['from-el-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'BROWSER_TEXT_BY_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } ) 
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text'].upper()):                                
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text'].upper() , 'description': stepsReg[i]['description'], 
                                                'value' : '', 'color': '' } )   
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_BY_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } )      

                                                
                    elif stepsReg[i]['action'] in [ GuiSteps.BROWSER_TYPE_TEXT, GuiSteps.BROWSER_FIND_TEXT_ELEMENT,
                                                    GuiSteps.BROWSER_SELECT_TEXT, GuiSteps.BROWSER_SELECT_VALUE,
                                                    GuiSteps.BROWSER_EXECUTE_JS ] :
                        if stepsReg[i]["parameters"]['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text-more'], 'color': '' } ) 
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text-more'].upper()):                                
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text-more'].upper() , 'description': stepsReg[i]['description'], 
                                                'value' : '', 'color': '' } )   
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text-more'], 'color': '' } )     
                                                
                        if stepsReg[i]["parameters"]['from-el-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'BROWSER_TEXT_BY_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } ) 
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text'].upper()):                                
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text'].upper() , 'description': stepsReg[i]['description'], 
                                                'value' : '', 'color': '' } )   
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_BY_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } )      

                    elif stepsReg[i]['action'] in [ GuiSteps.BROWSER_FIND_TEXT_TITLE, GuiSteps.BROWSER_FIND_TEXT_GET_URL,
                                                    GuiSteps.BROWSER_FIND_TEXT_GET_SOURCE, GuiSteps.BROWSER_SWITCH_TO_WINDOW,
                                                    GuiSteps.BROWSER_SWITCH_TO_SESSION ] :
                        if stepsReg[i]["parameters"]['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text-more'], 'color': '' } ) 
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text-more'].upper()):                                
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text-more'].upper() , 'description': stepsReg[i]['description'], 
                                                'value' : '', 'color': '' } )   
                        else:
                            newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text-more'], 'color': '' } )    
                                                
                    else:
                        newInputs.append( {'type': 'str', 'name': 'BROWSER_TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['text'], 'color': '' } )    
                
                # sikuli
                else:
                    if 'option-similar' not in stepsReg[i]: # for backward compatibility
                        stepsReg[i]['option-similar'] = self.DEFAULT_SIMILAR_VALUE
                    if 'from-alias' not in stepsReg[i]: # for backward compatibility
                        stepsReg[i]['from-alias'] = False
                        
                    # sikuli

                    if stepsReg[i]['action'] in [ GuiSteps.MOUSE_WHEEL_UP, GuiSteps.MOUSE_WHEEL_DOWN]:
                        newInputs.append( {'type': 'int', 'name': 'WHEEL_%s' % j , 'description': '',
                                        'value' : str(stepsReg[i]['misc']), 'color': '' } )       
                    elif stepsReg[i]['action'] == GuiSteps.SHORTCUT:
                        pass
                        
                    elif stepsReg[i]['action'] == GuiSteps.TYPE_TEXT:
                        if stepsReg[i]["parameters"]['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['text'], 'color': '' } )
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text']):                             
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text'], 'description': stepsReg[i]['description'],
                                            'value' : '', 'color': '' } )
                        else:
                            newInputs.append( {'type': 'str', 'name': 'TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['text'], 'color': '' } )
                    elif stepsReg[i]['action'] == GuiSteps.TYPE_TEXT_PATH:
                        if stepsReg[i]["parameters"]['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['text'], 'color': '' } )
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text']):                      
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['text'] , 'description': stepsReg[i]['description'],
                                            'value' : '', 'color': '' } )
                        else:
                            newInputs.append( {'type': 'str', 'name': 'TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                            'value' : stepsReg[i]['text'], 'color': '' } )
                    elif stepsReg[i]['action'] == GuiSteps.TYPE_PASSWORD:
                        if stepsReg[i]["parameters"]['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['text'], 'color': '' } )
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['text']):                  
                                newInputs.append( {'type': 'pwd', 'name': stepsReg[i]['text'] , 'description': stepsReg[i]['description'],
                                        'value' : '', 'color': '' } )
                        else:
                            newInputs.append( {'type': 'pwd', 'name': 'TEXT_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['text'], 'color': '' } )
                                        
                    elif stepsReg[i]['action'] == GuiSteps.TYPE_TEXT_ON:
                        newInputs.append( {'type': 'str', 'name': 'TEXT_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['text'], 'color': '' } )
                        newInputs.append( {'type': 'snapshot-image', 'name': 'IMG_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['image'], 'color': '' } )
                        newInputs.append( {'type': 'float', 'name': 'IMG_%s_SIMILAR' % j , 'description': '',
                                        'value' : stepsReg[i]['option-similar'], 'color': '' } )
                    elif stepsReg[i]['action'] == GuiSteps.DRAG_DROP_IMAGE:
                        newInputs.append( {'type': 'int', 'name': 'DROP_Y_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['text'], 'color': '' } )
                        newInputs.append( {'type': 'int', 'name': 'DROP_X_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['misc'], 'color': '' } )
                        newInputs.append( {'type': 'snapshot-image', 'name': 'IMG_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['image'], 'color': '' } )
                        newInputs.append( {'type': 'float', 'name': 'IMG_%s_SIMILAR' % j , 'description': '',
                                        'value' : stepsReg[i]['option-similar'], 'color': '' } )
                    elif stepsReg[i]['action'] in [ GuiSteps.MOUSE_CLICK_POSITION, GuiSteps.MOUSE_DOUBLE_CLICK_POSITION, 
                                                        GuiSteps.MOUSE_RIGHT_CLICK_POSITION, GuiSteps.MOUSE_MOVE_POSITION ] :
                        newInputs.append( {'type': 'int', 'name': 'TO_X_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['text'], 'color': '' } )
                        newInputs.append( {'type': 'int', 'name': 'TO_Y_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['misc'], 'color': '' } )
                    elif stepsReg[i]['action'] in [ GuiSteps.CLICK_WORD, GuiSteps.DOUBLE_CLICK_WORD, 
                                                        GuiSteps.RIGHT_CLICK_WORD, GuiSteps.WAIT_WORD, GuiSteps.WAIT_CLICK_WORD ] :
                        if stepsReg[i]['parameters']['from-alias']:
                            newInputs.append( {'type': 'alias', 'name': 'WORD_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['parameters']['location-word'], 'color': '' } )
                            if not self.checkDuplicateAlias(inputs=newInputs, alias=stepsReg[i]['parameters']['location-word']):                  
                                newInputs.append( {'type': 'str', 'name': stepsReg[i]['parameters']['location-word'] , 'description': stepsReg[i]['description'],
                                                    'value' : '', 'color': '' } )
                        else:                
                            newInputs.append( {'type': 'str', 'name': 'WORD_%s' % j , 'description': '',
                                            'value' : stepsReg[i]['parameters']['location-word'], 'color': '' } ) 
                        newInputs.append( {'type': 'int', 'name': 'TO_LOC_X_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['parameters']['location-x'], 'color': '' } )
                        newInputs.append( {'type': 'int', 'name': 'TO_LOC_Y_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['parameters']['location-y'], 'color': '' } )
                        newInputs.append( {'type': 'int', 'name': 'TO_LOC_W_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['parameters']['location-w'], 'color': '' } ) 
                        newInputs.append( {'type': 'int', 'name': 'TO_LOC_H_%s' % j , 'description': '',
                                        'value' : stepsReg[i]['parameters']['location-h'], 'color': '' } ) 
                    elif stepsReg[i]['action'] == GuiSteps.GET_TEXT_CLIPBOARD:
                        if stepsReg[i]["parameters"]['from-cache']:
                            newInputs.append( {'type': 'str', 'name': 'APP_CACHE_%s' % j , 'description': stepsReg[i]['description'], 
                                                'value' : stepsReg[i]['text'], 'color': '' } )  
                                                
                    # default
                    else:
                        newInputs.append( {'type': 'snapshot-image', 'name': 'IMG_%s' % j , 'description': stepsReg[i]['description'],
                                        'value' : stepsReg[i]['image'], 'color': '' } )
                        newInputs.append( {'type': 'float', 'name': 'IMG_%s_SIMILAR' % j , 'description': '',
                                        'value' : stepsReg[i]['option-similar'], 'color': '' } )

        # get timeout
        timeout = self.sikuliGroup.getTimeout()
        if not len(timeout): timeout = 10.0

        timeoutBrowser = self.seleniumGroup.getTimeout()
        if not len(timeoutBrowser): timeoutBrowser = 25.0

        timeoutAndroid = self.androidGroup.getTimeout()
        if not len(timeoutAndroid): timeoutAndroid = 10.0
        
        timeoutFramework = self.frameworkGroup.getTimeout()
        if not len(timeoutFramework): timeoutFramework = 30.0
        
        timeoutSys = self.sshGroup.getTimeout()
        if not len(timeoutSys): timeoutSys = 20.0
        
        newInputs.append( {'type': 'bool', 'name': 'DEBUG', 'description': '', 'value' : 'False', 'color': '' } )
        
        if anythingStepDetected:
            newInputs.append( {'type': 'float', 'name': 'TIMEOUT_GUI', 'description': '', 'value' : '%s' % str(timeout), 'color': '' } )
        if browserStepDetected:
           newInputs.append( {'type': 'float', 'name': 'TIMEOUT_GUI_BROWSER', 'description': '', 'value' : '%s' % str(timeoutBrowser), 'color': '' } ) 
        if androidStepDetected:
           newInputs.append( {'type': 'float', 'name': 'TIMEOUT_ANDROID', 'description': '', 'value' : '%s' % str(timeoutAndroid), 'color': '' } ) 
        if frameworkStepDetected:
           newInputs.append( {'type': 'float', 'name': 'TIMEOUT_FWK', 'description': '', 'value' : '%s' % str(timeoutFramework), 'color': '' } ) 
        if sysStepDetected:
           newInputs.append( {'type': 'float', 'name': 'TIMEOUT_SYS', 'description': '', 'value' : '%s' % str(timeoutSys), 'color': '' } ) 

        # set the agent
        agentName = self.sikuliGroup.getAgentList().currentText()
        agentBrowserName = self.seleniumGroup.getAgentList().currentText()
        agentAndroidName = self.androidGroup.getAgentList().currentText()
        agentSysName = self.sshGroup.getAgentList().currentText()

        agentTpl = []
        if anythingStepDetected:
            agentTpl.append( { 'name': '%s' % agentKeyName, 'description': '', 'value' : '%s' % str(agentName), 'type': 'sikulixserver' } )
        if browserStepDetected:
            agentTpl.append( { 'name': '%s' % agentBrowserKeyName, 'description': '', 'value' : '%s' % str(agentBrowserName), 'type': 'seleniumserver' } )
        if androidStepDetected:
            agentTpl.append( { 'name': '%s' % agentAndroidKeyName, 'description': '', 'value' : '%s' % str(agentAndroidName), 'type': 'adb' } )
        if sysStepDetected:
            agentTpl.append( { 'name': '%s' % agentSystemKeyName, 'description': '', 'value' : '%s' % str(agentSysName), 'type': 'ssh' } )
            
            
        # construct all steps
        steps = []
        j = 0
        z = 0
        oneStep = self.oneStepCheck.isChecked()
        if oneStep:
            _stepsDescr = []
            for i in xrange(len(stepsReg)):
                if stepsReg[i]['active'] == "True":
                    if len(stepsReg[i]['description']):
                        _stepsDescr.append(stepsReg[i]['description'])
                
            steps.append( 'self.step1 = self.addStep(expected="Action(s) executed with success", description="%s", summary="%s", enabled=True)' % 
                            (  "\\n- ".join(_stepsDescr),  "\\n- ".join(_stepsDescr) ) )
        else:
            for i in xrange(len(stepsReg)):
                j = i + 1 - z
                steps.append( 'self.step%s = self.addStep(expected="%s", description="%s", summary="%s", enabled=%s)' % 
                                (j, stepsReg[i]['expected'], stepsReg[i]['description'],
                                    stepsReg[i]['description'], stepsReg[i]['active'] ) )

        # construct the content of the test
        testdef = []
        j = 0 # step ID
        # z = 0
        tab = ''
        
        if oneStep:
            testdef.append( 'if self.step1.isEnabled():' )
            testdef.append( '\tself.step1.start()' )
            testdef.append( "" )
            
        for i in xrange(len(stepsReg)):
            j = i + 1
            
            # if oneStep:
                # if stepsReg[i]['active'] == "False":
                    # continue
  
            if stepsReg[i]['action'] == GuiSteps.FRAMEWORK_USERCODE:
                # remove endding characters
                while stepsReg[i]['misc'].endswith('\n') or stepsReg[i]['misc'].endswith('\t'):
                    stepsReg[i]['misc'] = stepsReg[i]['misc'][:-1]

                if oneStep:
                    testdef.append( "\t%s %s" % (TAG_USER, stepsReg[i]['description']) )
                    testdef.append( "\t%s" % (stepsReg[i]['misc']) )
                    testdef.append( "\t%s" % (TAG_USER_END) )
                else:    
                    testdef.append( "%s%s" % (tab,TAG_USER_CODE) )
                    testdef.append( '%sif self.step%s.isEnabled():' % (tab,j) )
                    testdef.append( '%s\tself.step%s.start()' % (tab,j) )
                    testdef.append( "%s\t%s %s" % (tab,TAG_USER, stepsReg[i]['description']) )
                    testdef.append( "%s\t%s" % (tab,stepsReg[i]['misc']) )
                    testdef.append( "%s\t%s" % (tab,TAG_USER_END) )
                    testdef.append( "%s\tself.step%s.setPassed('action ok')" % (tab,j) )
                    
                    if self.stopOnError.isChecked():
                        tab += '\t'

            else:

                if oneStep:  tab = ''
                
                if not oneStep:    
                    if stepsReg[i]["action-type"] == GuiSteps.ACTION_FRAMEWORK:
                        testdef.append( '%s%s%s' % (tab, TAG_COMMENT_FRAMEWORK, stepsReg[i]['description']) )
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_SYSTEM:
                        testdef.append( '%s%s%s' % (tab, TAG_COMMENT_SYS, stepsReg[i]['description']) )
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_BROWSER:
                        testdef.append( '%s%s%s' % (tab, TAG_COMMENT_BROWSER, stepsReg[i]['description']) )
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_ANDROID:
                        testdef.append( '%s%s%s' % (tab, TAG_COMMENT_ANDROID, stepsReg[i]['description']) )
                    else:
                        testdef.append( '%s%s%s' % (tab, TAG_COMMENT, stepsReg[i]['description']) )
                else:
                    if stepsReg[i]["action-type"] == GuiSteps.ACTION_FRAMEWORK:
                        testdef.append( '\t%s%s' % (TAG_COMMENT_FRAMEWORK, stepsReg[i]['description']) )
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_SYSTEM:
                        testdef.append( '\t%s%s' % (TAG_COMMENT_SYS, stepsReg[i]['description']) )
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_BROWSER:
                        testdef.append( '\t%s%s' % (TAG_COMMENT_BROWSER, stepsReg[i]['description']) )
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_ANDROID:
                        testdef.append( '\t%s%s' % (TAG_COMMENT_ANDROID, stepsReg[i]['description']) )
                    else:
                        testdef.append( '\t%s%s' % (TAG_COMMENT, stepsReg[i]['description']) )
                        
                if not oneStep:
                    testdef.append( '%sif self.step%s.isEnabled():' % (tab,j) )
                    testdef.append( '%s\tself.step%s.start()' % (tab,j) )
                 
                if oneStep:
                    if stepsReg[i]['active'] == "False":
                        testdef.append( '%s\tif False:' % (tab) )
                        tab = '\t'
                    else:
                        tab = ''
                        
                if stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_WAIT ]:
                    args = []
                    if stepsReg[i]['parameters']['from-cache']:
                        args.append("timeout=Cache().get(name=input('FWK_WAIT_%s'))" % j )          
                    else:
                        args.append("timeout=input('FWK_WAIT_%s')" % j )   
                    testdef.append( "%s\tself.wait(%s)" % (tab,','.join(args)) )
                    
                    if not oneStep:
                        testdef.append( "%s\tself.step%s.setPassed('action ok')" % (tab,j) )
                        if self.stopOnError.isChecked():
                            tab += '\t'
                    testdef.append( "" )
                    
                elif stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_INFO, GuiSteps.FRAMEWORK_WARNING ]:
                    args = []
                    if stepsReg[i]['parameters']['from-cache']:
                        args.append("txt=Cache().get(name=input('FWK_TEXT_%s'))" % j )          
                    else:
                        args.append("txt=input('FWK_TEXT_%s')" % j )     
                    if stepsReg[i]['action'] == GuiSteps.FRAMEWORK_INFO:
                        testdef.append( "%s\tself.info(%s)" % (tab, ','.join(args) ) )
                    else:
                        testdef.append( "%s\tself.warning(%s)" % (tab, ','.join(args) ) )
                    
                    if not oneStep:
                        testdef.append( "%s\tself.step%s.setPassed('action ok')" % (tab,j) )
                        if self.stopOnError.isChecked():
                            tab += '\t'
                    testdef.append( "" )
                    
                elif stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_CACHE_SET ]: 
                    args = []
                    args.append( "name=input('FWK_CACHE_KEY_%s')" % j)
                    if stepsReg[i]['parameters']['from-cache']:
                        args.append("data=Cache().get(name=input('FWK_CACHE_VALUE_%s'))" % j )          
                    else:
                        args.append("data=input('FWK_CACHE_VALUE_%s')" % j )  
                        
                    testdef.append( "%s\tCache().set(flag=True, %s)" % (tab, ','.join(args) ) )
                    
                    if not oneStep:
                        testdef.append( "%s\tself.step%s.setPassed('action ok')" % (tab,j) )
                        if self.stopOnError.isChecked():
                            tab += '\t'
                    testdef.append( "" )
                    
                elif stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_CHECK_STRING ]:
                    op = stepsReg[i]['parameters']['operator']
                    args = []
                    
                    if stepsReg[i]['parameters']['from-cache']:
                        args.append("needle=Cache().get(name=input('FWK_CHECK_%s'))" % j )     
                    else:
                        args.append( "needle=input('FWK_CHECK_%s')" % j)
                        
                    testdef.append( "%s\tFWK_RET%s = TestOperators.%s(%s).seekIn(haystack=Cache().get(name=input('FWK_CHECK_KEY_%s')))" % (tab, j, op, ','.join(args), j) ) 

                    if not oneStep:
                        testdef.append( "%s\tif not FWK_RET%s:" % (tab,j) )
                        testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                        testdef.append( "%s\telse:" % tab )
                        testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                        testdef.append( "" )
                        
                        if self.stopOnError.isChecked():
                            tab += '\t\t'
                    else:
                        testdef.append( "%s\tif not FWK_RET%s:" % (tab, j) )
                        if self.stopOnError.isChecked():
                            testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab, stepsReg[i]['description'].lower()) )
                        else:
                            testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab, stepsReg[i]['description'].lower()) )
                        testdef.append( "" )
                        
                elif stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_INTERACT ]:
                    args = []
                    if stepsReg[i]['parameters']['from-cache']:
                        args.append("ask=Cache().get(name=input('FWK_ASK_%s'))" % j )     
                    else:
                        args.append( "ask=input('FWK_ASK_%s')" % j)
                    
                    if len(stepsReg[i]['parameters']['key']):
                        testdef.append( "%s\tFWK_RET%s = Interact(self).interact(%s, timeout=input('TIMEOUT_FWK'), default=None, cache=input('FWK_ASK_KEY_%s'))" % (tab, j, ','.join(args), j) ) 
                    else:
                        testdef.append( "%s\tFWK_RET%s = Interact(self).interact(%s, timeout=input('TIMEOUT_FWK'), default=None)" % (tab, j, ','.join(args)) ) 
                    
                    if not oneStep:
                        testdef.append( "%s\tif not FWK_RET%s:" % (tab,j) )
                        testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                        testdef.append( "%s\telse:" % tab )
                        testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                        testdef.append( "" )
                        
                        if self.stopOnError.isChecked():
                            tab += '\t\t'
                    else:
                        testdef.append( "%s\tif not FWK_RET%s:" % (tab,j) )
                        if self.stopOnError.isChecked():
                            testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                        else:
                            testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                        testdef.append( "" )
                    
                elif stepsReg[i]['action'] in [ GuiSteps.FRAMEWORK_CACHE_RESET ]: 
                    testdef.append( "%s\tCache().reset()" % tab )
                    
                    if not oneStep:
                        testdef.append( "%s\tself.step%s.setPassed('action ok')" % (tab,j) )
                        if self.stopOnError.isChecked():
                            tab += '\t'
                    testdef.append( "" )
                    
                else:
                    if stepsReg[i]["action-type"] == GuiSteps.ACTION_SYSTEM:    
                        if stepsReg[i]['action'] == GuiSteps.SYSTEM_SESSION:
                            args = []
                            if stepsReg[i]['parameters']['from-cache-ip']:
                                args.append( "destIp=Cache().get(name=input('SYS_DEST_HOST_KEY'))" )
                            else:
                                args.append( "destIp=input('SYS_DEST_HOST')")
                            if stepsReg[i]['parameters']['from-cache-port']:
                                args.append( "destPort=Cache().get(name=input('SYS_DEST_PORT_KEY'))" )
                            else:
                                args.append( "destPort=input('SYS_DEST_PORT')")
                            if stepsReg[i]['parameters']['from-cache-login']:
                                args.append( "login=Cache().get(name=input('SYS_LOGIN_KEY'))" )
                            else:
                                args.append( "login=input('SYS_LOGIN')")
                            if stepsReg[i]['parameters']['from-cache-pwd']:
                                args.append( "password=Cache().get(name=input('SYS_PWD_KEY'))" )
                            else:
                                args.append( "password=input('SYS_PWD')")
                                
                            args.append( "agent=agent('%s')" %   str(agentSystemKeyName) )
                            args.append( "debug=input('DEBUG')" )
                            args.append( "agentSupport=input('SYS_AGT_SUPPORT')")
                            adpsGui.append( "self.ADP_SYS = %s.SSH.Terminal(parent=self, %s )" % (self.searchGUI(), ",".join(args) )  )
                            
                            testdef.append( "%s\tSYS_RET%s = self.ADP_SYS.doSession(timeout=input('TIMEOUT_SYS'))" % (tab, j) )
                        if stepsReg[i]['action'] == GuiSteps.SYSTEM_CLOSE:
                            testdef.append( "%s\tSYS_RET%s = self.ADP_SYS.doClose(timeout=input('TIMEOUT_SYS'))" % (tab, j) )
                        if stepsReg[i]['action'] == GuiSteps.SYSTEM_CLEAR_SCREEN:
                            testdef.append( "%s\tSYS_RET%s = self.ADP_SYS.doClear()" % (tab, j) )
                        if stepsReg[i]['action'] == GuiSteps.SYSTEM_TEXT:
                            args = []
                            if stepsReg[i]['parameters']['from-cache']:
                                args.append("text=Cache().get(name=input('SYS_TEXT_%s'))" % j )          
                            else:
                                args.append("text=input('SYS_TEXT_%s')" % j )  
                            testdef.append( "%s\tSYS_RET%s = self.ADP_SYS.doText(%s)" % (tab, j, ','.join(args) ) )
                        if stepsReg[i]['action'] == GuiSteps.SYSTEM_SHORTCUT:
                            shortcut = stepsReg[i]["parameters"]['shortcut']
                            testdef.append( "%s\tSYS_RET%s = self.ADP_SYS.doShortcut(key=%s.SSH.KEY_%s)" % (tab, j, self.searchGUI(), shortcut) )
                        if stepsReg[i]['action'] == GuiSteps.SYSTEM_CHECK_SCREEN:
                            op = stepsReg[i]['parameters']['operator']
                            args = []
                            if op != GuiSteps.OP_ANY:
                                if stepsReg[i]['parameters']['from-cache']:
                                    args.append("needle=Cache().get(name=input('SYS_SCREEN_%s'))" % j )     
                                else:
                                    args.append( "needle=input('SYS_SCREEN_%s')" % j)
                            testdef.append( "%s\tSYS_RET%s = self.ADP_SYS.hasReceivedScreen(timeout=input('TIMEOUT_SYS'), text=TestOperators.%s(%s))" % (tab, j, op, ','.join(args) ) )
                            
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_BROWSER:
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_OPEN:
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doOpen(timeout=input('TIMEOUT_GUI_BROWSER'), targetUrl=Cache().get(name=input('BROWSER_TEXT_%s')), withFirefox=input('BROWSER_USE_FIREFOX_%s'), withIe=input('BROWSER_USE_IE_%s'), withChrome=input('BROWSER_USE_CHROME_%s'), withOpera=input('BROWSER_USE_OPERA_%s'), withEdge=input('BROWSER_USE_EDGE_%s'), useMarionette=input('BROWSER_DRIVER_GECKO_%s'), sessionName=input('BROWSER_SESSION_%s') )" % (tab, j, j, j, j, j, j, j, j, j) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doOpen(timeout=input('TIMEOUT_GUI_BROWSER'), targetUrl=input('BROWSER_TEXT_%s'), withFirefox=input('BROWSER_USE_FIREFOX_%s'), withIe=input('BROWSER_USE_IE_%s'), withChrome=input('BROWSER_USE_CHROME_%s'), withOpera=input('BROWSER_USE_OPERA_%s'), withEdge=input('BROWSER_USE_EDGE_%s'), useMarionette=input('BROWSER_DRIVER_GECKO_%s'), sessionName=input('BROWSER_SESSION_%s') )" % (tab, j, j, j, j, j, j, j, j, j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_CLOSE:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doClose(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_MAXIMIZE:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doMaximizeWindow(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_CLOSE_WINDOW:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doCloseWindow(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_NEXT_WINDOW:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToNextWindow(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_MAIN_WINDOW:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToDefaultWindow(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_ACCEPT_ALERT:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doAcceptAlert(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_DISMISS_ALERT:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doDismissAlert(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GET_TEXT_ALERT:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGetTextAlert(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            if stepsReg[i]['parameters']['to-cache']:
                                testdef.append( "%s\tCache().set(name=input('BROWSER_TEXT_%s'), data=BROWSER_RET%s)" % (tab, j, j) )
                                
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_REFRESH:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doRefreshPage(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GO_BACK:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGoBack(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GO_FORWARD:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGoForward(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GET_URL:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGetPageUrl(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            if stepsReg[i]['parameters']['to-cache']:
                                testdef.append( "%s\tCache().set(name=input('BROWSER_TEXT_%s'), data=BROWSER_RET%s)" % (tab, j, j) )
                                
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GET_TITLE:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGetPageTitle(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            if stepsReg[i]['parameters']['to-cache']:
                                testdef.append( "%s\tCache().set(name=input('BROWSER_TEXT_%s'), data=BROWSER_RET%s)" % (tab, j, j) )
                                
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GET_SOURCE:
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGetPageSource(timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j) )
                            if stepsReg[i]['parameters']['to-cache']:
                                testdef.append( "%s\tCache().set(name=input('BROWSER_TEXT_%s'), data=BROWSER_RET%s)" % (tab, j, j) )
                                
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_WAIT_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doWaitElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )
                                
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_WAIT_VISIBLE_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doWaitVisibleElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )
                                
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_WAIT_NOT_VISIBLE_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doWaitNotVisibleElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_TO_FRAME:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToFrame(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_WAIT_CLICK_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doWaitClickElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_WAIT_VISIBLE_CLICK_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doWaitVisibleClickElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_HOVER_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache'])

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doHoverElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_CLICK_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doClickElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_DOUBLE_CLICK_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doDoubleClickElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_CLEAR_TEXT_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doClearTextElement(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_GET_TEXT_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 

                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doGetText(timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, args) )
                            
                            if stepsReg[i]['parameters']['to-cache']:
                                testdef.append( "%s\tCache().set(name=input('BROWSER_TEXT_%s'), data=BROWSER_RET%s)" % (tab, j, j) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_TYPE_TEXT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doTypeText(text=Cache().get(name=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doTypeText(text=input('BROWSER_TEXT_%s'), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_EXECUTE_JS:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doRunJsElement(js=Cache().get(name=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doRunJsElement(js=input('BROWSER_TEXT_%s'), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SELECT_TEXT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSelectByText(text=Cache().get(name=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSelectByText(text=input('BROWSER_TEXT_%s'), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SELECT_VALUE:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSelectByValue(text=Cache().get(name=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSelectByValue(text=input('BROWSER_TEXT_%s'), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_TYPE_KEY:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            keyRepeat = 0
                            keyStr = stepsReg[i]['text-more']
                            if ";" in stepsReg[i]['text-more']:
                                keyStr, keyRepeat = stepsReg[i]['text-more'].split(";")
                            keyArg = "%s.GUI.SELENIUM_KEY_%s" % (self.searchGUI(), keyStr)
                            
                            testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doTypeKey(key=%s, timeout=input('TIMEOUT_GUI_BROWSER'), %s, repeat=%s)" % ( tab, j, keyArg, args, keyRepeat) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_FIND_TEXT_ELEMENT:
                            args = self.parseSearch(searchBy=stepsReg[i]['misc'], j=j, fromCache=stepsReg[i]['parameters']['from-el-cache']) 
                            
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindText(expectedText=TestOperators.Contains(needle=Cache().get(name=input('BROWSER_TEXT_%s'))), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindText(expectedText=TestOperators.Contains(needle=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'), %s)" % (tab, j, j, args) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_FIND_TEXT_TITLE:
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindTextPageTitle(expectedText=TestOperators.Contains(needle=Cache().get(name=input('BROWSER_TEXT_%s'))), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindTextPageTitle(expectedText=TestOperators.Contains(needle=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_TO_WINDOW:
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToWindow(windowName=Cache().get(name=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToWindow(windowName=input('BROWSER_TEXT_%s'), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )

                        if stepsReg[i]['action'] == GuiSteps.BROWSER_SWITCH_TO_SESSION:
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToSession(sessionName=Cache().get(name=input('BROWSER_TEXT_%s')))" % (tab, j, j) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doSwitchToSession(sessionName=input('BROWSER_TEXT_%s'))" % (tab, j, j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_FIND_TEXT_GET_URL:
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindTextPageUrl(expectedText=TestOperators.Contains(needle=Cache().get(name=input('BROWSER_TEXT_%s'))), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindTextPageUrl(expectedText=TestOperators.Contains(needle=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.BROWSER_FIND_TEXT_GET_SOURCE:
                            if stepsReg[i]['parameters']['from-cache']:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindTextPageSource(expectedText=TestOperators.Contains(needle=Cache().get(name=input('BROWSER_TEXT_%s'))), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )
                            else:
                                testdef.append( "%s\tBROWSER_RET%s = self.ADP_GUI_BROWSER.doFindTextPageSource(expectedText=TestOperators.Contains(needle=input('BROWSER_TEXT_%s')), timeout=input('TIMEOUT_GUI_BROWSER'))" % (tab, j, j) )

                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_ANDROID:
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_WAKEUP_UNLOCK:
                            testdef.append( "%s\tANDROID_RET%s = self.ADP_ANDROID.doWakeupUnlock(timeout=input('TIMEOUT_ANDROID'))" % (tab, j) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_SLEEP_LOCK:
                            testdef.append( "%s\tANDROID_RET%s = self.ADP_ANDROID.doSleepLock(timeout=input('TIMEOUT_ANDROID'))" % (tab, j) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_WAKUP:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.wakeUp()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_UNLOCK:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.unlock()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_LOCK:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.lock()" % (tab) ) 
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_REBOOT:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.reboot()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_SLEEP:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.sleep()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_FREEZE_ROTATION:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.freezeRotation()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_UNFREEZE_ROTATION:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.unfreezeRotation()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_BOOTLOADER:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.bootloader()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_RECOVERY:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.recovery()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_NOTIFICATION:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.openNotification()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_SETTINGS:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.openQuickSettings()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_DEVICEINFO:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.deviceInfo()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_GET_LOGS:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.getLogs()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_CLEAR_LOGS:
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.clearLogs()" % (tab) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_TYPE_SHORTCUT:
                            key = stepsReg[i]['misc']
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.typeShortcut(shortcut=%s.GUI.ADB_KEY_%s)" % (tab, self.searchGUI(), key) )
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_TYPE_KEYCODE:
                            code = stepsReg[i]['misc']
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.typeKeyCode(code=%s)" % (tab, code) )
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_WAIT_ELEMENT, GuiSteps.ANDROID_CLEAR_ELEMENT, GuiSteps.ANDROID_CLICK_ELEMENT,
                                                     GuiSteps.ANDROID_LONG_CLICK_ELEMENT, GuiSteps.ANDROID_EXIST_ELEMENT, GuiSteps.ANDROID_TYPE_TEXT_ELEMENT,
                                                      GuiSteps.ANDROID_GET_TEXT_ELEMENT, GuiSteps.ANDROID_DRAG_ELEMENT, GuiSteps.ANDROID_WAIT_CLICK_ELEMENT  ] :
                            args = [] 
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_TYPE_TEXT_ELEMENT:
                                if len(stepsReg[i]['parameters']['new-text']): 
                                    if stepsReg[i]['parameters']['from-cache']:
                                        args.append("newText=Cache().get(name=input('ANDROID_TEXT_%s'))" % j )          
                                    else:
                                        args.append("newText=input('ANDROID_TEXT_%s')" % j )     
                                        
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_DRAG_ELEMENT:
                                if len(stepsReg[i]['parameters']['x']): args.append("endX=input('ANDROID_UI_X_%s')" % j ) 
                                if len(stepsReg[i]['parameters']['y']): args.append("endY=input('ANDROID_UI_Y_%s')" % j ) 
                                
                            if 'text' in stepsReg[i]['parameters']:
                                if len(stepsReg[i]['parameters']['text']): 
                                    if stepsReg[i]['parameters']['from-el-cache']:
                                        args.append("text=Cache().get(name=input('ANDROID_UI_TXT_%s'))" % j ) 
                                    else:
                                        args.append("text=input('ANDROID_UI_TXT_%s')" % j ) 
                                        
                            if 'description' in stepsReg[i]['parameters']:
                                if len(stepsReg[i]['parameters']['description']): args.append("description=input('ANDROID_UI_DESCR_%s')" % j ) 
                            if 'class' in stepsReg[i]['parameters']:
                                if len(stepsReg[i]['parameters']['class']): args.append("className=input('ANDROID_UI_CLS_%s')" % j ) 
                            if 'ressource' in stepsReg[i]['parameters']:
                                if len(stepsReg[i]['parameters']['ressource']): args.append("resourceId=input('ANDROID_UI_RES_%s')" % j )
                            if 'package' in stepsReg[i]['parameters']:
                                if len(stepsReg[i]['parameters']['package']): args.append("packageName=input('ANDROID_UI_PKG_%s')" % j )                        
                            
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_GET_TEXT_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.getTextElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_TYPE_TEXT_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.typeTextElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_CLICK_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.clickElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_LONG_CLICK_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.longClickElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_CLEAR_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.clearTextElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_EXIST_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.existElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_WAIT_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.waitElement(%s, timeout=input('TIMEOUT_ANDROID'))" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_DRAG_ELEMENT:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.dragElement(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_WAIT_CLICK_ELEMENT:
                                testdef.append( "%s\tANDROID_RET%s = self.ADP_ANDROID.doWaitClickElement(%s, timeout=input('TIMEOUT_ANDROID'))" % (tab, j, ','.join(args)) )
                                
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_CLICK_POSITION ] :
                            args = [] 
                            if len(stepsReg[i]['parameters']['x']): args.append("x=input('ANDROID_UI_X_%s')" % j ) 
                            if len(stepsReg[i]['parameters']['y']): args.append("y=input('ANDROID_UI_Y_%s')" % j ) 
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.clickPosition(%s)" % (tab, ','.join(args) ) )
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_COMMAND ] :
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.input(command=input('ANDROID_CMD_%s'))" % (tab, j ) )
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_SHELL ] :
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.shell(command=input('ANDROID_SH_%s'))" % (tab, j ) )
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_RESET_APP ] :
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.resetApplication(packageName=input('ANDROID_PKG_%s'))" % (tab, j ) )
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_STOP_APP ] :
                            testdef.append( "%s\tactionId = self.ADP_ANDROID.stopApplication(packageName=input('ANDROID_PKG_%s'))" % (tab, j ) )
                        if stepsReg[i]['action'] in [ GuiSteps.ANDROID_DRAG_POSITION, GuiSteps.ANDROID_SWIPE_POSITION ] :
                            args = [] 
                            if len(stepsReg[i]['parameters']['start-x']): args.append("startX=input('ANDROID_UI_START_X_%s')" % j ) 
                            if len(stepsReg[i]['parameters']['start-y']): args.append("startY=input('ANDROID_UI_START_Y_%s')" % j ) 
                            if len(stepsReg[i]['parameters']['stop-x']): args.append("endX=input('ANDROID_UI_STOP_X_%s')" % j ) 
                            if len(stepsReg[i]['parameters']['stop-y']): args.append("endY=input('ANDROID_UI_STOP_Y_%s')" % j ) 
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_DRAG_POSITION:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.dragPosition(%s)" % (tab, ','.join(args) ) )
                            if stepsReg[i]['action'] == GuiSteps.ANDROID_SWIPE_POSITION:
                                testdef.append( "%s\tactionId = self.ADP_ANDROID.swipePosition(%s)" % (tab, ','.join(args) ) )
                    
                    else:
                        # sikuli
                        if stepsReg[i]['action'] == GuiSteps.DRAG_DROP_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.dragDropImage( img=input('IMG_%s'), toY=input('DROP_Y_%s'), toX=input('DROP_X_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR') )" % 
                                            (tab, j, j, j, stepsReg[i]['description'], j) )
                                            
                        if stepsReg[i]['action'] == GuiSteps.MOUSE_CLICK_POSITION:
                            testdef.append( "%s\tactionId = self.ADP_GUI.clickPosition( toX=input('TO_X_%s'), toY=input('TO_Y_%s'), description=\"%s\")" 
                                % (tab, j, j, stepsReg[i]['description']) )
                                            
                        if stepsReg[i]['action'] == GuiSteps.MOUSE_DOUBLE_CLICK_POSITION:
                            testdef.append( "%s\tactionId = self.ADP_GUI.doubleClickPosition( toX=input('TO_X_%s'), toY=input('TO_Y_%s'), description=\"%s\")" 
                                % (tab, j, j, stepsReg[i]['description']) )
                                            
                        if stepsReg[i]['action'] == GuiSteps.MOUSE_RIGHT_CLICK_POSITION:
                            testdef.append( "%s\tactionId = self.ADP_GUI.rightClickPosition( toX=input('TO_X_%s'), toY=input('TO_Y_%s'), description=\"%s\")" 
                                % (tab, j, j, stepsReg[i]['description']) )
                                
                        if stepsReg[i]['action'] == GuiSteps.MOUSE_MOVE_POSITION:
                            testdef.append( "%s\tactionId = self.ADP_GUI.mouseMovePosition( toX=input('TO_X_%s'), toY=input('TO_Y_%s'), description=\"%s\")" 
                                % (tab, j, j, stepsReg[i]['description']) )
                                
                        if stepsReg[i]['action'] == GuiSteps.MOUSE_WHEEL_UP:
                            testdef.append( "%s\tactionId = self.ADP_GUI.mouseWheelUp( steps=input('WHEEL_%s'), description=\"%s\")" 
                                % (tab, j, stepsReg[i]['description']) )
                                
                        if stepsReg[i]['action'] == GuiSteps.MOUSE_WHEEL_DOWN:
                            testdef.append( "%s\tactionId = self.ADP_GUI.mouseWheelDown( steps=input('WHEEL_%s'), description=\"%s\")" 
                                % (tab, j, stepsReg[i]['description']) )
                                
                        if stepsReg[i]['action'] == GuiSteps.HOVER_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.hoverImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR') )" % (tab, j, stepsReg[i]['description'],j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.CLICK_WORD:
                            args = []
                            if stepsReg[i]['parameters']['from-cache']:
                                args.append( "word=Cache().get(name=input('WORD_%s'))" % j )          
                            else:
                                args.append( "word=input('WORD_%s')" % j )
                            testdef.append( "%s\tactionId = self.ADP_GUI.clickWord(%s, locX=input('TO_LOC_X_%s'), locY=input('TO_LOC_Y_%s'), locW=input('TO_LOC_W_%s'), locH=input('TO_LOC_H_%s'), description=\"%s\" )" % (tab, ','.join(args), j, j, j, j, stepsReg[i]['description']) )
                        
                        if stepsReg[i]['action'] == GuiSteps.DOUBLE_CLICK_WORD:
                            args = []
                            if stepsReg[i]['parameters']['from-cache']:
                                args.append( "word=Cache().get(name=input('WORD_%s'))" % j )          
                            else:
                                args.append( "word=input('WORD_%s')" % j  )
                            testdef.append( "%s\tactionId = self.ADP_GUI.doubleClickWord(%s, locX=input('TO_LOC_X_%s'), locY=input('TO_LOC_Y_%s'), locW=input('TO_LOC_W_%s'), locH=input('TO_LOC_H_%s'), description=\"%s\" )" % (tab, ','.join(args), j, j, j, j, stepsReg[i]['description']) )
                        
                        if stepsReg[i]['action'] == GuiSteps.RIGHT_CLICK_WORD:
                            args = []
                            if stepsReg[i]['parameters']['from-cache']:
                                args.append( "word=Cache().get(name=input('WORD_%s'))" % j )          
                            else:
                                args.append( "word=input('WORD_%s')" % j  )
                            testdef.append( "%s\tactionId = self.ADP_GUI.rightClickWord(%s, locX=input('TO_LOC_X_%s'), locY=input('TO_LOC_Y_%s'), locW=input('TO_LOC_W_%s'), locH=input('TO_LOC_H_%s'), description=\"%s\" )" % (tab, ','.join(args), j, j, j, j, stepsReg[i]['description']) )
                        
                        if stepsReg[i]['action'] == GuiSteps.WAIT_WORD:
                            args = []
                            if stepsReg[i]['parameters']['from-cache']:
                                args.append( "word=Cache().get(name=input('WORD_%s'))" % j )          
                            else:
                                args.append( "word=input('WORD_%s')" % j  )
                            testdef.append( "%s\tactionId = self.ADP_GUI.waitWord(%s, locX=input('TO_LOC_X_%s'), locY=input('TO_LOC_Y_%s'), locW=input('TO_LOC_W_%s'), locH=input('TO_LOC_H_%s'), description=\"%s\" )" % (tab, ','.join(args), j, j, j, j, stepsReg[i]['description']) )
                        
                        if stepsReg[i]['action'] == GuiSteps.WAIT_CLICK_WORD:
                            args = []
                            if stepsReg[i]['parameters']['from-cache']:
                                args.append( "word=Cache().get(name=input('WORD_%s'))" % j )          
                            else:
                                args.append( "word=input('WORD_%s')"% j  )
                            testdef.append( "%s\tactionId = self.ADP_GUI.waitClickWord(%s, locX=input('TO_LOC_X_%s'), locY=input('TO_LOC_Y_%s'), locW=input('TO_LOC_W_%s'), locH=input('TO_LOC_H_%s'), description=\"%s\" )" % (tab,','.join(args), j, j, j, j, stepsReg[i]['description']) )
                        
                        if stepsReg[i]['action'] == GuiSteps.CLICK_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.clickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR') )" % (tab, j, stepsReg[i]['description'], j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.CLICK_IMAGE_ALL:
                            testdef.append( "%s\tactionId = self.ADP_GUI.clickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), findAll=True )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.DOUBLE_CLICK_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.doubleClickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR') )" % (tab, j, stepsReg[i]['description'],j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.DOUBLE_CLICK_IMAGE_ALL:
                            testdef.append( "%s\tactionId = self.ADP_GUI.doubleClickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), findAll=True )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.RIGHT_CLICK_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.rightClickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR') )" % (tab, j, stepsReg[i]['description'],j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.RIGHT_CLICK_IMAGE_ALL:
                            testdef.append( "%s\tactionId = self.ADP_GUI.rightClickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), findAll=True )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.FIND_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.findImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), timeout=input('TIMEOUT_GUI') )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.DONT_FIND_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.dontFindImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), timeout=input('TIMEOUT_GUI') )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.FIND_CLICK_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.findClickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), timeout=input('TIMEOUT_GUI') )" % (tab, j, stepsReg[i]['description'],j) )
                        
                        if stepsReg[i]['action'] == GuiSteps.WAIT_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.waitImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), timeout=input('TIMEOUT_GUI') )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.WAIT_CLICK_IMAGE:
                            testdef.append( "%s\tactionId = self.ADP_GUI.waitClickImage( img=input('IMG_%s'), description=\"%s\", similar=input('IMG_%s_SIMILAR'), timeout=input('TIMEOUT_GUI') )" % (tab, j, stepsReg[i]['description'],j) )

                        if stepsReg[i]['action'] == GuiSteps.TYPE_TEXT:
                            if stepsReg[i]['from-cache']:
                                testdef.append( "%s\tactionId = self.ADP_GUI.typeText( text=Cache().get(name=input('TEXT_%s')), description=\"%s\" )" % (tab, j, stepsReg[i]['description']) )
                            else:
                                testdef.append( "%s\tactionId = self.ADP_GUI.typeText( text=input('TEXT_%s'), description=\"%s\" )" % (tab, j, stepsReg[i]['description']) )
                        
                        if stepsReg[i]['action'] == GuiSteps.TYPE_TEXT_PATH:
                            if stepsReg[i]['from-cache']:
                                testdef.append( "%s\tactionId = self.ADP_GUI.typePath( text=Cache().get(name=input('TEXT_%s')), description=\"%s\" )" % (tab, j, stepsReg[i]['description']) )
                            else:
                                testdef.append( "%s\tactionId = self.ADP_GUI.typePath( text=input('TEXT_%s'), description=\"%s\" )" % (tab, j, stepsReg[i]['description']) )
                            
                        if stepsReg[i]['action'] == GuiSteps.TYPE_PASSWORD:
                            if stepsReg[i]['from-cache']:
                                testdef.append( "%s\tactionId = self.ADP_GUI.typeText( text=Cache().get(name=input('TEXT_%s')), description=\"%s\" )" % (tab, j, stepsReg[i]['description']) )
                            else:
                                testdef.append( "%s\tactionId = self.ADP_GUI.typeText( text=input('TEXT_%s'), description=\"%s\" )" % (tab, j, stepsReg[i]['description']) )

                        if stepsReg[i]['action'] == GuiSteps.TYPE_TEXT_ON:
                            testdef.append( "%s\tactionId = self.ADP_GUI.typeText( text=input('TEXT_%s'), description=\"%s\", img=('IMG_%s') )" % 
                                             (tab, j, stepsReg[i]['description'], j) )
                                             
                        if stepsReg[i]['action'] == GuiSteps.GET_TEXT_CLIPBOARD:
                            testdef.append( "%s\tactionId = self.ADP_GUI.getTextClipboard( description=\"%s\" )" % (tab, stepsReg[i]['description']) )
                                             
                        if stepsReg[i]['action'] == GuiSteps.SHORTCUT:

                            mainKey = 'None'
                            modifierKey = 'None'
                            specialKey = 'None'
                            otherKey = 'None'

                            modifiersKeys = stepsReg[i]['misc'].split('+')
                            modifiersFinal = []

                            # extra key modifiers
                            for key in modifiersKeys:
                                if len(key):
                                    modifiersFinal.append( "%s.GUI.KEY_%s" % (self.searchGUI(), key) )
                            
                            if len(modifiersFinal) == 1:
                                mainKey = modifiersFinal[0]
                            if len(modifiersFinal) == 2:
                                mainKey = modifiersFinal[0]
                                modifierKey = modifiersFinal[1]

                            # add text key
                            if len(stepsReg[i]['text']):
                                letterDetected = False
                                for k in GuiSikuli.KEY_LETTERS:
                                    if stepsReg[i]['text'] == k:
                                        letterDetected = True
                                        otherKey = stepsReg[i]['text'].lower()

                                if not letterDetected:
                                    specialKey =  "%s.GUI.KEY_%s" % (self.searchGUI(), stepsReg[i]['text'])

                            if otherKey != 'None':
                                otherKey ="'%s'" % otherKey
                                
                            if 'option-similar' in stepsReg[i]:
                                if str(stepsReg[i]['option-similar']) == '0.7':
                                    repeat = 0
                                else:
                                    repeat = stepsReg[i]['option-similar']
                            else:
                                repeat = 0
                            testdef.append( "%s\tactionId = self.ADP_GUI.typeShorcut(key=%s, modifier=%s, special=%s, other=%s, repeat=%s)" % 
                                                (
                                                    tab, 
                                                    mainKey,
                                                    modifierKey,
                                                    specialKey,
                                                    otherKey,
                                                    repeat,
                                                )
                                            )
                                               
                    # adding check action
                    if stepsReg[i]["action-type"] == GuiSteps.ACTION_SYSTEM:
                        if not oneStep:
                            testdef.append( "%s\tif not SYS_RET%s:" % (tab,j) )
                            testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                            testdef.append( "%s\telse:" % tab )
                            if stepsReg[i]["action"] == GuiSteps.SYSTEM_CHECK_SCREEN:
                                if stepsReg[i]['parameters']['to-cache']:
                                    testdef.append( "%s\t\tCache().set(name=input('SYS_CACHE_%s'), data=SYS_RET%s.get('TERM', 'data'))" % (tab, j, j) )
                            testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                        else:
                            testdef.append( "%s\tif not SYS_RET%s:" % (tab,j) )
                            if self.stopOnError.isChecked():
                                testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                            else:
                                testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                            
                            if stepsReg[i]["action"] == GuiSteps.SYSTEM_CHECK_SCREEN:
                                if stepsReg[i]['parameters']['to-cache']:
                                    testdef.append( "\telse:" )
                                    testdef.append( "%s\t\tCache().set(name=input('SYS_CACHE_%s'), data=SYS_RET%s.get('TERM', 'data'))" % (tab,j, j) )
                        testdef.append( "" )
                        
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_BROWSER:
                        if not oneStep:
                            testdef.append( "%s\tif not BROWSER_RET%s:" % (tab,j) )
                            testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                            testdef.append( "%s\telse:" % tab )
                            testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                        else:
                            testdef.append( "%s\tif not BROWSER_RET%s:" % (tab,j) )
                            if self.stopOnError.isChecked():
                                testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                            else:
                                testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                        testdef.append( "" )
                        
                    elif stepsReg[i]["action-type"] == GuiSteps.ACTION_ANDROID:
                        if stepsReg[i]['action'] == GuiSteps.ANDROID_GET_TEXT_ELEMENT:
                            testdef.append( "%s\tANDROID_RET%s = self.ADP_ANDROID.isActionAccepted(timeout=input('TIMEOUT_ANDROID'), actionId=actionId)" % (tab, j) )
                            if not oneStep:
                                testdef.append( "%s\tif ANDROID_RET%s is None:" % (tab,j))
                                testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                                testdef.append( "%s\telse:" % tab )
                                if stepsReg[i]['parameters']['to-cache']:
                                    testdef.append( "%s\t\tCache().set(name=input('ANDROID_CACHE_%s'), data=ANDROID_RET%s.get('GUI', 'value'))" % (tab, j, j) )
                                testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                            else:
                                testdef.append( "%s\tif ANDROID_RET%s is None:" % (tab,j))
                                if self.stopOnError.isChecked():
                                    testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                                else:
                                    testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab,stepsReg[i]['description'].lower() ) )
                                testdef.append( "%s\telse:" % tab )
                                if stepsReg[i]['parameters']['to-cache']:
                                    testdef.append( "%s\t\tCache().set(name=input('ANDROID_CACHE_%s'), data=ANDROID_RET%s.get('GUI', 'value'))" % (tab, j, j) )
                            testdef.append( "" )
                            
                        elif stepsReg[i]['action'] in [ GuiSteps.ANDROID_WAKEUP_UNLOCK, GuiSteps.ANDROID_SLEEP_LOCK, GuiSteps.ANDROID_WAIT_CLICK_ELEMENT ]:
                            if not oneStep:
                                testdef.append( "%s\tif not ANDROID_RET%s:" % (tab,j) )
                                testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                                testdef.append( "%s\telse:" % tab )
                                testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                            else:
                                testdef.append( "%s\tif not ANDROID_RET%s:" % (tab,j) )
                                if self.stopOnError.isChecked():
                                    testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % ( tab, stepsReg[i]['description'].lower() ) )
                                else:
                                    testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % ( tab, stepsReg[i]['description'].lower() ) )

                            testdef.append( "" )
                        
                        else:
                            testdef.append( "%s\tif not self.ADP_ANDROID.isActionAccepted(timeout=input('TIMEOUT_ANDROID'), actionId=actionId):" % tab )
                            if not oneStep:
                                testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                                testdef.append( "%s\telse:" % tab )
                                testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                            else:
                                if self.stopOnError.isChecked():
                                    testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab, stepsReg[i]['description'].lower() ) )
                                else:
                                    testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab, stepsReg[i]['description'].lower() ) )
                                
                            testdef.append( "" )
                    
                    else:
                        testdef.append( "%s\tAPP_RET%s = self.ADP_GUI.isActionAccepted(timeout=input('TIMEOUT_GUI'), actionId=actionId)" % (tab,j) )
                        if not oneStep:
                            testdef.append( "%s\tif APP_RET%s is None:" % (tab,j) )
                            testdef.append( "%s\t\tself.step%s.setFailed(\"Unable to %s\")"  % (tab, j, stepsReg[i]['description'].lower() ) )
                            testdef.append( "%s\telse:" % tab )
                            if stepsReg[i]['action'] == GuiSteps.GET_TEXT_CLIPBOARD:
                                if stepsReg[i]['from-cache']:
                                    testdef.append( "%s\t\tCache().set(name=input('APP_CACHE_%s'), data=APP_RET%s.get('GUI', 'text-result'))" % (tab, j, j) )
                            testdef.append( "%s\t\tself.step%s.setPassed(\"Executing with success: %s\")" % (tab, j, stepsReg[i]['description'].lower()) )
                        else:
                            testdef.append( "%s\tif APP_RET%s is None:" % (tab, j) )
                            if self.stopOnError.isChecked():
                                testdef.append( "%s\t\tself.abort(\"Unable to %s\")"  % (tab, stepsReg[i]['description'].lower() ) )
                            else:
                                testdef.append( "%s\t\tself.step1.setFailed(\"Unable to %s\")"  % (tab, stepsReg[i]['description'].lower() ) )
                            if stepsReg[i]['action'] == GuiSteps.GET_TEXT_CLIPBOARD:
                                if stepsReg[i]['from-cache']:
                                    testdef.append( "%s\telse:" % tab )
                                    testdef.append( "%s\t\tCache().set(name=input('APP_CACHE_%s'), data=APP_RET%s.get('GUI', 'text-result'))" % ( tab, j, j) )
                        testdef.append( "" )
                    
                    if not oneStep:                    
                        if self.stopOnError.isChecked():
                            tab += '\t\t'
        
        if oneStep:
            testdef.append( '\tself.step1.setPassed("test terminated")' )
            
        # finally replace all keys in the template
        newTest = newTest.replace( "<<PURPOSE>>", 'self.setPurpose(purpose="%s")' % self.tcPurposeLine.text() )
        if not len(adpsGui): adpsGui = [ "pass" ]
        newTest = newTest.replace( "<<ADPS>>", '\n\t'.join(adpsGui) )
        
        if not len(steps): steps = [ "pass" ]
        
        if TS: newTest = newTest.replace( "<<STEPS>>", '\n\t\t'.join(steps) )
        if TU: newTest = newTest.replace( "<<STEPS>>", '\n\t'.join(steps) )
        newTest = newTest.replace( "<<INIT>>", "" )
        
        if oneStep:
            newTest = newTest.replace( "<<CLEANUP>>", "if aborted: self.step1.setFailed(aborted)" )
        else:
            newTest = newTest.replace( "<<CLEANUP>>", "pass" )
        if TS: newTest = newTest.replace( "<<TESTS>>", '\n\t\t'.join(testdef) )
        if TU: newTest = newTest.replace( "<<TESTS>>", '\n\t'.join(testdef) )

        if updateTest:
            return (newTest, newInputs, agentTpl)
        else:
            # export to workspace
            if TS:
                WWorkspace.WDocumentViewer.instance().newTestSuiteWithContent(testDef=newTest, testExec=newTestExec, 
                                                                            testInputs=newInputs, testAgents=agentTpl)
            if TU:
                WWorkspace.WDocumentViewer.instance().newTestUnitWithContent(testDef=newTest, testInputs=newInputs, 
                                                                            testAgents=agentTpl)

            self.close()

    def onStepRemoved(self):
        """
        Delete step
        """
        self.cancelStep()
        self.cancelBrStep()
        self.cancelAndroidStep()
        self.cancelFrameworkStep()
        
    def clearSteps(self):
        """
        Clear steps
        """
        self.cancelStep()
        self.cancelBrStep()
        self.cancelAndroidStep()
        self.cancelFrameworkStep()
        # self.exportStepsAction.setEnabled(False)
        self.stepsTable.clear()
        self.stepsTable.editAction.setEnabled(False)
    
    def onAddFrameworkStep(self, action, description, misc, parameters):
        """
        Onn add step from framework
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(    actionName=action, imagePixmap='', textStr='', 
                                    miscStr=misc, actionType=GuiSteps.ACTION_FRAMEWORK,
                                    descriptionStr=description, updateMode=False, 
                                    stepId=self.stepId, parameters=parameters, bold=True)
            
    def onUpdateFrameworkStep(self, action, description, misc, parameters):
        """
        On update step from framework
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(    actionName=action, imagePixmap='', textStr='', 
                                    miscStr=misc, actionType=GuiSteps.ACTION_FRAMEWORK,
                                    descriptionStr=description, updateMode=True, 
                                    stepId=self.stepId, parameters=parameters, bold=True)
        self.frameworkGroup.finalizeUpdate()
        self.cancelFrameworkStep()
    
    def onAddSshStep(self, action, description, misc, parameters):
        """
        On add step from ssh
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(    actionName=action, imagePixmap='', textStr='', 
                                    miscStr=misc, actionType=GuiSteps.ACTION_SYSTEM,
                                    descriptionStr=description, updateMode=False, 
                                    stepId=self.stepId, parameters=parameters, bold=True)
            
    def onUpdateSshStep(self, action, description, misc, parameters):
        """
        On update step from ssh
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(    actionName=action, imagePixmap='', textStr='', 
                                    miscStr=misc, actionType=GuiSteps.ACTION_SYSTEM,
                                    descriptionStr=description, updateMode=True, 
                                    stepId=self.stepId, parameters=parameters, bold=True)
        self.sshGroup.finalizeUpdate()
        self.cancelSshStep()
        
    def onAddSikuliStep(self, action, description, image, text, misc, similar, cache, alias, parameters={}):
        """
        On add step from sikuli
        """
        self.exportStepsAction.setEnabled(True)
        
        self.stepsTable.addStep(actionName=action, imagePixmap=image, textStr=text, miscStr=misc, descriptionStr=description,
                                    updateMode=False, stepId=self.stepId, optionSimilar=similar, fromCache=cache, 
                                    fromAlias=alias, bold=True, parameters=parameters)
                    
    def onUpdateSikuliStep(self, action, description, image, text, misc, similar, cache, alias, parameters={}):
        """
        On update step from sikuli
        """
        self.exportStepsAction.setEnabled(True)
        
        self.stepsTable.addStep(actionName=action, imagePixmap=image, textStr=text, miscStr=misc, descriptionStr=description,
                                    updateMode=True, stepId=self.stepId, optionSimilar=similar, fromCache=cache, 
                                    fromAlias=alias, bold=True, parameters=parameters)
        self.sikuliGroup.finalizeUpdate()
        self.cancelStep()

    def onAddSeleniumStep(self,action, description, text, misc, textmore, parameters):
        """
        On add step from selenium
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(actionName=action, imagePixmap='', textStr=text, miscStr=misc,
                                    descriptionStr=description, actionType=GuiSteps.ACTION_BROWSER, 
                                    updateMode=False, stepId=self.stepId, textMoreStr=textmore,
                                    bold=True, parameters=parameters)

    def onUpdateSeleniumStep(self,action, description, text, misc, textmore, parameters):
        """
        On update step from selenium
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(actionName=action, imagePixmap='', textStr=text, miscStr=misc,
                                    descriptionStr=description, actionType=GuiSteps.ACTION_BROWSER,
                                    updateMode=True, stepId=self.stepId, textMoreStr=textmore,
                                     bold=True, parameters=parameters)
        self.seleniumGroup.finalizeUpdate()
        self.cancelBrStep()
            
    def onAddAndroidStep(self, action, description, misc, parameters):
        """
        On add step from android
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(    actionName=action, imagePixmap='', textStr='', 
                                    miscStr=misc, actionType=GuiSteps.ACTION_ANDROID,
                                    descriptionStr=description, updateMode=False, 
                                    stepId=self.stepId, parameters=parameters, bold=True)

    def onUpdateAndroidStep(self, action, description, misc, parameters):
        """
        On update step from android
        """
        self.exportStepsAction.setEnabled(True)
        self.stepsTable.addStep(    actionName=action, imagePixmap='', textStr='', 
                                    miscStr=misc, actionType=GuiSteps.ACTION_ANDROID,
                                    descriptionStr=description, updateMode=True, 
                                    stepId=self.stepId, parameters=parameters, bold=True)
        self.androidGroup.finalizeUpdate()
        self.cancelAndroidStep()

    def getParameterWait(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        waitParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'WAIT_%s' % paramId:
                waitParam = p
                break
        return waitParam
        
    def getParametersWord(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        parameters = {}
        for p in testInputs['parameter']:
            if p['name'] == 'WORD_%s' % paramId:
                parameters["location-word"] = p["value"]
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
            if p['name'] == 'TO_LOC_X_%s' % paramId:
                parameters["location-x"] = p["value"]
            if p['name'] == 'TO_LOC_Y_%s' % paramId:
                parameters["location-y"] = p["value"]
            if p['name'] == 'TO_LOC_W_%s' % paramId:
                parameters["location-w"] = p["value"]
            if p['name'] == 'TO_LOC_H_%s' % paramId:
                parameters["location-h"] = p["value"]
        return parameters
        
    def getParameterWheel(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        waitParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'WHEEL_%s' % paramId:
                waitParam = p
                break
        return waitParam
        
    def getParameterText(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        textPwd = False
        textAlias = False
        textParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'TEXT_%s' % paramId:
                textParam = p
                if p['type'] == 'pwd': textPwd = True
                if p['type'] == 'alias': textAlias = True
                break
        return (textParam,textPwd, textAlias)
        
    def getParameterCache(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        textPwd = False
        textAlias = False
        textParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'APP_CACHE_%s' % paramId:
                textParam = p
                break
        return textParam
        
    def getParameterToY(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        imageParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'TO_Y_%s' % paramId:
                imageParam = p
                break
        return imageParam
        
    def getParameterToX(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        imageParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'TO_X_%s' % paramId:
                imageParam = p
                break
        return imageParam
        
    def getParameterDropY(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        imageParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'DROP_Y_%s' % paramId:
                imageParam = p
                break
        return imageParam
        
    def getParameterDropX(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        imageParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'DROP_X_%s' % paramId:
                imageParam = p
                break
        return imageParam

    def getParameterImage(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        imageParam = None
        for p in testInputs['parameter']:
            if p['name'] == 'IMG_%s' % paramId:
                imageParam = p
                break
        if imageParam is not None:
            imageParam['similar'] = self.DEFAULT_SIMILAR_VALUE
            
        for p in testInputs['parameter']:
            if p['name'] == 'IMG_%s_SIMILAR' % paramId:
                imageParam['similar'] = p['value']
                break
        return imageParam
        
    def getParameterTextBrowser(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        textParam = None
        textAlias = False
        for p in testInputs['parameter']:
            if p['name'] == 'BROWSER_TEXT_%s' % paramId:
                textParam = p
                if p['type'] == 'alias': textAlias = True
                break
        return (textParam, textAlias)
        
    def getParameterTextByBrowser(self, testInputs, paramId):
        """
        Return the text parameter according to the id
        """
        textParam = None
        textAlias = False
        for p in testInputs['parameter']:
            if p['name'] == 'BROWSER_TEXT_BY_%s' % paramId:
                textParam = p
                if p['type'] == 'alias': textAlias = True
                break
        return (textParam, textAlias)
        
    def getParametersUIAndroid(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        parameters = {}
        for p in testInputs['parameter']:
            if p['name'] == 'ANDROID_UI_TXT_%s' % paramId:
                parameters['text'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-el-alias'] = True
                else:
                    parameters['from-el-alias'] = False
                    
            if p['name'] == 'ANDROID_UI_DESCR_%s' % paramId:
                parameters['description'] = p['value']
            if p['name'] == 'ANDROID_UI_CLS_%s' % paramId:
                parameters['class'] = p['value']
            if p['name'] == 'ANDROID_UI_RES_%s' % paramId:
                parameters['ressource'] = p['value']
            if p['name'] == 'ANDROID_UI_PKG_%s' % paramId:
                parameters['package'] = p['value']
            if p['name'] == 'ANDROID_UI_X_%s' % paramId:
                parameters['x'] = p['value']
            if p['name'] == 'ANDROID_UI_Y_%s' % paramId:
                parameters['y'] = p['value']
            if p['name'] == 'ANDROID_UI_START_X_%s' % paramId:
                parameters['start-x'] = p['value']
            if p['name'] == 'ANDROID_UI_START_Y_%s' % paramId:
                parameters['start-y'] = p['value']
            if p['name'] == 'ANDROID_UI_STOP_X_%s' % paramId:
                parameters['stop-x'] = p['value']
            if p['name'] == 'ANDROID_UI_STOP_Y_%s' % paramId:
                parameters['stop-y'] = p['value']
            if p['name'] == 'ANDROID_CMD_%s' % paramId:
                parameters['cmd'] = p['value']
            if p['name'] == 'ANDROID_SH_%s' % paramId:
                parameters['sh'] = p['value']
            if p['name'] == 'ANDROID_TEXT_%s' % paramId:
                parameters['new-text'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
                    
            if p['name'] == 'ANDROID_PKG_%s' % paramId:
                parameters['pkg'] = p['value']
                
            if p['name'] == 'ANDROID_CACHE_%s' % paramId:
                parameters['to-cache'] = True 
                parameters['cache-key'] = p['value']
                
        return parameters
    
    def getParametersFramework(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        parameters = {}
        for p in testInputs['parameter']:
            if p['name'] == 'FWK_WAIT_%s' % paramId:
                parameters['text'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
                    
            if p['name'] == 'FWK_TEXT_%s' % paramId:
                parameters['text'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
  
            if p['name'] == 'FWK_CACHE_KEY_%s' % paramId:
                parameters['key'] = p['value']
                
            if p['name'] == 'FWK_CACHE_VALUE_%s' % paramId:
                parameters['value'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
 
            if p['name'] == 'FWK_CHECK_%s' % paramId:
                parameters['value'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
                    
            if p['name'] == 'FWK_CHECK_KEY_%s' % paramId:
                parameters['key'] = p['value']
 
            if p['name'] == 'FWK_ASK_%s' % paramId:
                parameters['value'] = p['value']
                if p['type'] == 'alias': 
                    parameters['from-alias'] = True
                else:
                    parameters['from-alias'] = False
                    
            if p['name'] == 'FWK_ASK_KEY_%s' % paramId:
                parameters['key'] = p['value']

        return parameters
    
    def getDefaultStepsParameters(self):
        """
        Return default steps parameter
        """
        parameters = { "from-el-alias": False, "from-el-cache": False, 
                        "from-alias": False, "from-cache": False,
                         "to-cache": False, "to-cache": False}
        return parameters
        
    def getParametersSysSession(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        parameters = { "from-alias-ip": False, "from-alias-port": False, 
                        "from-alias-login": False, "from-alias-pwd": False,
                        "from-cache-ip": False, "from-cache-port": False, 
                        "from-cache-login": False, "from-cache-pwd": False,
                        "agent-support": False}
        for p in testInputs['parameter']:
            if p['name'] == 'SYS_AGT_SUPPORT':
                parameters['agent-support'] = p['value']

            if p['name'] == 'SYS_DEST_HOST':
                parameters['dest-ip'] = p['value']
                if p['type'] == 'alias': parameters['from-alias-ip'] = True

            if p['name'] == 'SYS_DEST_PORT':
                parameters['dest-port'] = p['value']
                if p['type'] == 'alias': parameters['from-alias-port'] = True

            if p['name'] == 'SYS_LOGIN':
                parameters['login'] = p['value']
                if p['type'] == 'alias':parameters['from-alias-login'] = True

            if p['name'] == 'SYS_PWD':
                parameters['password'] = p['value']
                if p['type'] == 'alias': parameters['from-alias-pwd'] = True
                
            if p['name'] == 'SYS_DEST_HOST_KEY':
                parameters['dest-ip'] = p['value']
                parameters['from-cache-ip'] = True

            if p['name'] == 'SYS_DEST_PORT_KEY':
                parameters['dest-port'] = p['value']
                parameters['from-cache-port'] = True

            if p['name'] == 'SYS_LOGIN_KEY':
                parameters['login'] = p['value']
                parameters['from-cache-login'] = True

            if p['name'] == 'SYS_PWD_KEY':
                parameters['password'] = p['value']
                parameters['from-cache-pwd'] = True
                
        return parameters
        
    def getParametersSys(self, testInputs, paramId):
        """
        Return the image parameter according to the id
        """
        parameters = { "from-alias": False, "from-cache": False, "value": "", 
                            "to-cache": False, "cache-key": "" }
        for p in testInputs['parameter']:
            if p['name'] == 'SYS_TEXT_%s' % paramId:
                parameters['text'] = p['value']
                if p['type'] == 'alias': parameters['from-alias'] = True
            if p['name'] == 'SYS_SCREEN_%s' % paramId:
                parameters['value'] = p['value']
                if p['type'] == 'alias': parameters['from-alias'] = True
            if p['name'] == 'SYS_CACHE_%s' % paramId:
                parameters['cache-key'] = p['value']
                parameters['to-cache'] = True
        return parameters
        
    def prepareNextStep(self, actionType=GuiSteps.ACTION_ANYTHING):
        """
        Prepare next step
        """
        stp = { 'id': self.getUniqueId(), 'action': '', 'misc': '', 'text': '', 'image': '', 'description': '',
                 'active': "True", "action-type": actionType, 'expected': 'Action executed with success' }
        return stp
        
    def getUniqueId(self):
        """
        Return unique id
        """
        self.stepIdUnique += 1
        return self.stepIdUnique
    
    def setStepState(self, step, stepId, stateSteps):
        """
        Set the state of the step
        """
        stateStep = "True"
        if stepId in stateSteps:
            stateStep = stateSteps[stepId]
        step["active"] = stateStep
        
    def setStepExpected(self, step, stepId, expectedSteps):
        """
        Set the expected of the step
        """
        expectedStep = "Action executed with success"
        if stepId in expectedSteps:
            expectedStep = expectedSteps[stepId]
        step["expected"] = expectedStep
        
    def loadCurrentTest(self, currentDoc, testContent, testInputs, testAgents, isTu=True, isTs=False):
        """
        Load current test
        """

        self.isTu = isTu
        self.isTs = isTs
        self.userParams = []
        self.stepIdUnique = 0
        self.updateStepsAction.setEnabled(True)
        self.currentDocument = currentDoc

        # new in v13
        try:
            tcPurpose = unicode(testContent).split('self.setPurpose(purpose="')[1].split('"', 1)[0]
        except Exception as e:
            tcPurpose = "Testcase generated by test assistant"
        self.tcPurposeLine.setText( tcPurpose )
        # end of new
        
        # extract all steps definitions and try to detect if the step if enabled or not
        stateSteps = {}
        expectedSteps = {}
        stepsDef = unicode(testContent).split('def description(self):')[1].split("def prepare(self):")[0]
        i = 0
        for line in stepsDef.splitlines():
            if line.strip().startswith("self.step"):
                i += 1
                if "enabled" in line:
                    stepState = line.split("enabled=")[1].split(")")[0]
                else:
                    stepState = "True"
                stateSteps[i] = stepState
                expectedSteps[i] = line.split('expected="')[1].split('",', 1)[0]
    
        # extract all steps
        testDef = unicode(testContent).split('def definition(self):')[1]

        steps = []

        i = 0
        # prepare the first step
        stp = self.prepareNextStep()
        self.setStepState(step=stp, stepId=i+1, stateSteps=stateSteps)
        self.setStepExpected(step=stp, stepId=i+1, expectedSteps=expectedSteps)
        userCodeDetected=False
        for line in testDef.splitlines():

            if userCodeDetected:
                # end of user code detected ?
                if line.strip().startswith(TAG_COMMENT):
                    userCodeDetected = False
                    
                    # adding user code in steps list
                    if stp['misc'].startswith('\t'):
                        stp['misc'] = stp['misc'][1:]
                    steps.append(stp) 
                   
                    # prepare the next step
                    i += 1
                    stp = self.prepareNextStep(actionType=GuiSteps.ACTION_ANYTHING)
                    self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                    self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_ANYTHING
                    
                elif line.strip().startswith(TAG_COMMENT_BROWSER):
                    userCodeDetected = False

                    # adding user code in steps list
                    if stp['misc'].startswith('\t'):
                        stp['misc'] = stp['misc'][1:]
                    steps.append(stp) 
                   
                    # prepare the next step
                    i += 1
                    stp = self.prepareNextStep(actionType=GuiSteps.ACTION_BROWSER)
                    self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                    self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_BROWSER)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_BROWSER
                    
                elif line.strip().startswith(TAG_COMMENT_ANDROID):
                    userCodeDetected = False

                    # adding user code in steps list
                    if stp['misc'].startswith('\t'):
                        stp['misc'] = stp['misc'][1:]
                    steps.append(stp) 
                   
                    # prepare the next step
                    i += 1
                    stp = self.prepareNextStep(actionType=GuiSteps.ACTION_ANDROID)
                    self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                    self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_ANDROID)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_ANDROID
                    
                elif line.strip().startswith(TAG_COMMENT_FRAMEWORK):
                    userCodeDetected = False

                    # adding user code in steps list
                    if stp['misc'].startswith('\t'):
                        stp['misc'] = stp['misc'][1:]
                    steps.append(stp) 
                   
                    # prepare the next step
                    i += 1
                    stp = self.prepareNextStep(actionType=GuiSteps.ACTION_FRAMEWORK)
                    self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                    self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_FRAMEWORK)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_FRAMEWORK
                    
                elif line.strip().startswith(TAG_COMMENT_SYS):
                    userCodeDetected = False

                    # adding user code in steps list
                    if stp['misc'].startswith('\t'):
                        stp['misc'] = stp['misc'][1:]
                    steps.append(stp) 
                   
                    # prepare the next step
                    i += 1
                    stp = self.prepareNextStep(actionType=GuiSteps.ACTION_SYSTEM)
                    self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                    self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_SYS)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_SYSTEM
                    
                elif line.strip().startswith(TAG_USER_END):
                    userCodeDetected = False
                    
                    # adding user code in steps list
                    while stp['misc'].startswith('\t'):
                        stp['misc'] = stp['misc'][1:]
                    steps.append(stp) 
                    
                    # prepare the next step
                    stp = self.prepareNextStep()

                else:
                    stp['misc'] += line + '\n'
            else:
                # user code detected
                if line.strip().startswith(TAG_USER):

                    # adding previous step if exists
                    if len(stp['action']):
                        steps.append(stp)

                    # prepare step for usercode
                    userCodeDetected = True

                    descr_tmp = line.split(' ', 1)
                    if len(descr_tmp) > 1:
                        description = descr_tmp[1]
                    else:
                        description = descr_tmp[0]

                    stp = { 'id': self.getUniqueId(), 'action': GuiSteps.FRAMEWORK_USERCODE, 'misc': '', 'text': '',
                            'image': '', 'description': description, 'active': 'True', 
                            'expected': 'User code executed with success', 'action-type': GuiSteps.ACTION_FRAMEWORK }
                    self.setStepState(step=stp, stepId=i+1, stateSteps=stateSteps)
                    
                    i += 1
                    
                # new step detected anything
                if line.strip().startswith(TAG_COMMENT):
                    # new step detected 
                    i += 1
                    
                
                    # adding the previous step if exist to the list
                    if len(stp['action']):
                        steps.append(stp)
                            
                        # and finally prepare the next step
                        stp = self.prepareNextStep()
                        self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                        self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_ANYTHING

                # new step detected for browser
                if line.strip().startswith(TAG_COMMENT_BROWSER):
                    # new step detected 
                    i += 1
                    
                
                    # adding the previous step if exist to the list
                    if len(stp['action']):
                        steps.append(stp)
                            
                        # and finally prepare the next step
                        stp = self.prepareNextStep(actionType=GuiSteps.ACTION_ANYTHING)
                        self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                        self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_BROWSER)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_BROWSER
                    
                # new step detected for android
                if line.strip().startswith(TAG_COMMENT_ANDROID):
                    # new step detected 
                    i += 1
                    
                
                    # adding the previous step if exist to the list
                    if len(stp['action']):
                        steps.append(stp)
                            
                        # and finally prepare the next step
                        stp = self.prepareNextStep(actionType=GuiSteps.ACTION_ANYTHING)
                        self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                        self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_ANDROID)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_ANDROID
                    
                # new step detected for framework
                if line.strip().startswith(TAG_COMMENT_FRAMEWORK):
                    # new step detected 
                    i += 1
                    
                
                    # adding the previous step if exist to the list
                    if len(stp['action']):
                        steps.append(stp)
                            
                        # and finally prepare the next step
                        stp = self.prepareNextStep(actionType=GuiSteps.ACTION_FRAMEWORK)
                        self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                        self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_FRAMEWORK)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_FRAMEWORK

                # new step detected for android
                if line.strip().startswith(TAG_COMMENT_SYS):
                    # new step detected 
                    i += 1
                    
                
                    # adding the previous step if exist to the list
                    if len(stp['action']):
                        steps.append(stp)
                            
                        # and finally prepare the next step
                        stp = self.prepareNextStep(actionType=GuiSteps.ACTION_SYSTEM)
                        self.setStepState(step=stp, stepId=i, stateSteps=stateSteps)
                        self.setStepExpected(step=stp, stepId=i, expectedSteps=expectedSteps)
                    stp['description'] = line.split(TAG_COMMENT_SYS)[1].strip()
                    stp['action-type'] = GuiSteps.ACTION_SYSTEM
                 
                # new in v16
                if "if False" in line: stp['active'] = "False"
                # end of new
                
                # framework
                self.reconstructStepsFramework(line, i, stp, testInputs)
                
                # system
                self.reconstructStepsSystem(line, i, stp, testInputs)
                
                # android
                self.reconstructStepsAndroid(line, i, stp, testInputs)
                
                # sikuli
                self.reconstructStepsSikuli(line, i, stp, testInputs)
                
                # selenium
                self.reconstructStepsSelenium(line, i, stp, testInputs)

        if userCodeDetected:
            userCodeDetected = False
            while stp['misc'].startswith('\t'):
                stp['misc'] = stp['misc'][1:]

            steps.append(stp)
            stp = self.prepareNextStep()

        if len(stp['action']):
            steps.append(stp)
            stp = {}

        # extract time
        for inParam in testInputs['parameter']:
            if inParam['name'].startswith('USER_'):
                self.userParams.append( inParam )
            if inParam['name'] == 'TIMEOUT_GUI':
                self.sikuliGroup.setTimeout( inParam['value'] )
            if inParam['name'] == 'TIMEOUT_GUI_BROWSER':
                self.seleniumGroup.setTimeout( inParam['value'] )
            if inParam['name'] == 'TIMEOUT_GUI_ANDROID':
                self.androidGroup.setTimeout( inParam['value'] )
            if inParam['name'] == 'TIMEOUT_FWK':
                self.frameworkGroup.setTimeout( inParam['value'] )
            if inParam['name'] == 'TIMEOUT_SYS':
                self.sshGroup.setTimeout( inParam['value'] )
        
        # extract agent
        for agtParam in testAgents['agent']:
            if agtParam['name'] == 'AGENT_GUI' and agtParam['type'] == 'sikulixserver':
                self.sikuliGroup.getAgentList().insertSeparator( self.sikuliGroup.getAgentList().count() )
                self.sikuliGroup.getAgentList().addItems( [agtParam["value"]] )
        
                for i in xrange(self.sikuliGroup.getAgentList().count()):
                    item_text = self.sikuliGroup.getAgentList().itemText(i)
                    if str(agtParam["value"]) == str(item_text):
                        self.sikuliGroup.getAgentList().setCurrentIndex(i)
                        
            if agtParam['name'] == 'AGENT_GUI_BROWSER' and agtParam['type'] == 'seleniumserver':
                self.seleniumGroup.getAgentList().insertSeparator( self.seleniumGroup.getAgentList().count() )
                self.seleniumGroup.getAgentList().addItems( [agtParam["value"]] )
        
                for i in xrange(self.seleniumGroup.getAgentList().count()):
                    item_text = self.seleniumGroup.getAgentList().itemText(i)
                    if str(agtParam["value"]) == str(item_text):
                        self.seleniumGroup.getAgentList().setCurrentIndex(i)
                        
            if agtParam['name'] == 'AGENT_ANDROID' and agtParam['type'] == 'adb':
                self.androidGroup.getAgentList().insertSeparator( self.androidGroup.getAgentList().count() )
                self.androidGroup.getAgentList().addItems( [agtParam["value"]] )
        
                for i in xrange(self.androidGroup.getAgentList().count()):
                    item_text = self.androidGroup.getAgentList().itemText(i)
                    if str(agtParam["value"]) == str(item_text):
                        self.androidGroup.getAgentList().setCurrentIndex(i)
                        
            if agtParam['name'] == 'AGENT_SYSTEM' and agtParam['type'] == 'ssh':
                self.sshGroup.getAgentList().insertSeparator( self.sshGroup.getAgentList().count() )
                self.sshGroup.getAgentList().addItems( [agtParam["value"]] )
        
                for i in xrange(self.sshGroup.getAgentList().count()):
                    item_text = self.sshGroup.getAgentList().itemText(i)
                    if str(agtParam["value"]) == str(item_text):
                        self.sshGroup.getAgentList().setCurrentIndex(i)
            
        # set data to datamodel
        dataModel = self.stepsTable.getData()
        dataModel.extend( steps )

        self.stepsTable.model.beginResetModel() 
        self.stepsTable.model.endResetModel() 
        
        self.stepsTable.stepIdUnique = self.stepIdUnique
        self.stepsTable.setData()

        self.stepsTable.setUnboldAll()
        self.exportStepsAction.setEnabled(True)
    
    def reconstructStepsFramework(self, line, i, stp, testInputs):
        """
        Reconstruct steps from framework
        """
        if 'self.wait' in line:
            stp['action'] = GuiSteps.FRAMEWORK_WAIT
            # old style
            waitParam = self.getParameterWait(testInputs=testInputs, paramId=i)
            if waitParam is not None:
                stp['misc'] = waitParam['value']
                stp['action-type'] = GuiSteps.ACTION_FRAMEWORK
                stp['parameters'] = {"from-cache": False, "from-alias": False}
            else:
                stp['parameters'] = self.getParametersFramework(testInputs=testInputs, paramId=i)
                stp['misc'] = stp['parameters']["text"]
                if 'timeout=Cache().get(name=' in line: 
                    stp['parameters'].update( {'from-cache': True} )   
                else:
                    stp['parameters'].update( {'from-cache': False} )  
                    
        if 'self.info' in line:
            stp['action'] = GuiSteps.FRAMEWORK_INFO
            stp['parameters'] = self.getParametersFramework(testInputs=testInputs, paramId=i)
            if 'txt=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'self.warning' in line:
            stp['action'] = GuiSteps.FRAMEWORK_WARNING
            stp['parameters'] = self.getParametersFramework(testInputs=testInputs, paramId=i)
            if 'txt=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'Cache().reset()' in line:
            stp['action'] = GuiSteps.FRAMEWORK_CACHE_RESET
            stp['parameters'] = {}
            
        if 'Cache().set(flag=' in line:
            stp['action'] = GuiSteps.FRAMEWORK_CACHE_SET
            stp['parameters'] = self.getParametersFramework(testInputs=testInputs, paramId=i)
            if 'data=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'TestOperators.' in line and 'seekIn' in line:
            stp['action'] = GuiSteps.FRAMEWORK_CHECK_STRING
            stp['parameters'] = self.getParametersFramework(testInputs=testInputs, paramId=i)
            op = line.split('TestOperators.')[1].split("(",1)[0]
            stp['parameters'].update( {'operator': op} )
            if 'needle=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'Interact(self).interact' in line:
            stp['action'] = GuiSteps.FRAMEWORK_INTERACT
            stp['parameters'] = self.getParametersFramework(testInputs=testInputs, paramId=i)
            if 'ask=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
         
    def reconstructStepsSystem(self, line, i, stp, testInputs):
        """
        Reconstruct steps for system (ssh)
        """
        if 'self.ADP_SYS.doSession' in line:
            stp['action'] = GuiSteps.SYSTEM_SESSION
            stp['parameters'] = self.getParametersSysSession(testInputs=testInputs, paramId=i)
        if 'self.ADP_SYS.doClose' in line:
            stp['action'] = GuiSteps.SYSTEM_CLOSE
        if 'self.ADP_SYS.doClear' in line:
            stp['action'] = GuiSteps.SYSTEM_CLEAR_SCREEN
        if 'self.ADP_SYS.doText' in line:
            stp['action'] = GuiSteps.SYSTEM_TEXT
            stp['parameters'] = self.getParametersSys(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
        if 'self.ADP_SYS.doShortcut' in line:
            stp['action'] = GuiSteps.SYSTEM_SHORTCUT
            keySys = line.split("key=")[1].split(")", 1)[0]
            keysSysFinal = None
            if 'SutAdapters.SSH' in keySys:
                keysSysFinal = keySys.split('SutAdapters.SSH.KEY_')[1].strip()
            if 'SutAdapters.Generic.SSH' in keySys:
                keysSysFinal = keySys.split('SutAdapters.Generic.SSH.KEY_')[1].strip()
            stp['parameters'] = {"shortcut": keysSysFinal }
        if 'self.ADP_SYS.hasReceivedScreen' in line:
            stp['action'] = GuiSteps.SYSTEM_CHECK_SCREEN
            stp['parameters'] = self.getParametersSys(testInputs=testInputs, paramId=i)
            op = line.split('TestOperators.')[1].split("(",1)[0]
            stp['parameters'].update( {'operator': op} )
            if 'needle=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
    def reconstructStepsAndroid(self, line, i, stp, testInputs):
        """
        Reconstruct steps from android
        """
        if 'self.ADP_ANDROID.doWakeupUnlock' in line:
            stp['action'] = GuiSteps.ANDROID_WAKEUP_UNLOCK
        if 'self.ADP_ANDROID.doSleepLock' in line:
            stp['action'] = GuiSteps.ANDROID_SLEEP_LOCK
        if 'self.ADP_ANDROID.wakeUp' in line:
            stp['action'] = GuiSteps.ANDROID_WAKUP
        if 'self.ADP_ANDROID.sleep' in line:
            stp['action'] = GuiSteps.ANDROID_SLEEP
        if 'self.ADP_ANDROID.recovery' in line:
            stp['action'] = GuiSteps.ANDROID_RECOVERY
        if 'self.ADP_ANDROID.bootloader' in line:
            stp['action'] = GuiSteps.ANDROID_BOOTLOADER
        if 'self.ADP_ANDROID.reboot' in line:
            stp['action'] = GuiSteps.ANDROID_REBOOT
        if 'self.ADP_ANDROID.unlock' in line:
            stp['action'] = GuiSteps.ANDROID_UNLOCK
        if 'self.ADP_ANDROID.lock' in line:
            stp['action'] = GuiSteps.ANDROID_LOCK
        if 'self.ADP_ANDROID.freezeRotation' in line:
            stp['action'] = GuiSteps.ANDROID_FREEZE_ROTATION
        if 'self.ADP_ANDROID.unfreezeRotation' in line:
            stp['action'] = GuiSteps.ANDROID_UNFREEZE_ROTATION
        if 'self.ADP_ANDROID.openNotification' in line:
            stp['action'] = GuiSteps.ANDROID_NOTIFICATION
        if 'self.ADP_ANDROID.openQuickSettings' in line:
            stp['action'] = GuiSteps.ANDROID_SETTINGS
        if 'self.ADP_ANDROID.deviceInfo' in line:
            stp['action'] = GuiSteps.ANDROID_DEVICEINFO
        if 'self.ADP_ANDROID.getLogs' in line:
            stp['action'] = GuiSteps.ANDROID_GET_LOGS
        if 'self.ADP_ANDROID.clearLogs' in line:
            stp['action'] = GuiSteps.ANDROID_CLEAR_LOGS
        if 'self.ADP_ANDROID.typeShortcut(shortcut=' in line:
            keyAndroid = line.split("shortcut=")[1].split(")", 1)[0]
            keysAndroidFinal = None
            if 'SutAdapters.GUI' in keyAndroid:
                keysAndroidFinal = keyAndroid.split('SutAdapters.GUI.ADB_KEY_')[1].strip()
            if 'SutAdapters.Generic.GUI' in keyAndroid:
                keysAndroidFinal = keyAndroid.split('SutAdapters.Generic.GUI.ADB_KEY_')[1].strip()
            if keysAndroidFinal is not None:
                stp['action'] = GuiSteps.ANDROID_TYPE_SHORTCUT
                stp['misc'] = keysAndroidFinal
        if 'self.ADP_ANDROID.typeKeyCode(code=' in line:
            codeAndroid = line.split("code=")[1].split(")", 1)[0]
            stp['action'] = GuiSteps.ANDROID_TYPE_KEYCODE
            stp['misc'] = codeAndroid
        if 'self.ADP_ANDROID.clickElement(' in line:
            stp['action'] = GuiSteps.ANDROID_CLICK_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )   
        if 'self.ADP_ANDROID.longClickElement(' in line:
            stp['action'] = GuiSteps.ANDROID_LONG_CLICK_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
        if 'self.ADP_ANDROID.waitElement(' in line:
            stp['action'] = GuiSteps.ANDROID_WAIT_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
        if 'self.ADP_ANDROID.doWaitClickElement(' in line:
            stp['action'] = GuiSteps.ANDROID_WAIT_CLICK_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
        if 'self.ADP_ANDROID.getTextElement(' in line:
            stp['action'] = GuiSteps.ANDROID_GET_TEXT_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'to-cache' not in stp['parameters']:
                stp['parameters'].update( {'to-cache': False} )   
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
        if 'self.ADP_ANDROID.existElement(' in line:
            stp['action'] = GuiSteps.ANDROID_EXIST_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
        if 'self.ADP_ANDROID.clearTextElement(' in line:
            stp['action'] = GuiSteps.ANDROID_CLEAR_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
        if 'self.ADP_ANDROID.dragElement(' in line:
            stp['action'] = GuiSteps.ANDROID_DRAG_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
                
        if 'self.ADP_ANDROID.swipePosition(' in line:
            stp['action'] = GuiSteps.ANDROID_SWIPE_POSITION
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.dragPosition(' in line:
            stp['action'] = GuiSteps.ANDROID_DRAG_POSITION
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.clickPosition(' in line:
            stp['action'] = GuiSteps.ANDROID_CLICK_POSITION
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.input(' in line:
            stp['action'] = GuiSteps.ANDROID_COMMAND
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.shell(' in line:
            stp['action'] = GuiSteps.ANDROID_SHELL
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.resetApplication(' in line:
            stp['action'] = GuiSteps.ANDROID_RESET_APP
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.stopApplication(' in line:
            stp['action'] = GuiSteps.ANDROID_STOP_APP
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
        if 'self.ADP_ANDROID.typeTextElement(' in line:
            stp['action'] = GuiSteps.ANDROID_TYPE_TEXT_ELEMENT
            stp['parameters'] = self.getParametersUIAndroid(testInputs=testInputs, paramId=i)
            if 'text=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-el-cache': True} )   
            else:
                stp['parameters'].update( {'from-el-cache': False} )  
                
            if 'newText=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
    def reconstructStepsSikuli(self, line, i, stp, testInputs):
        """
        Reconstruct steps from sikuli
        """
        if 'parameters' not in stp:
            stp['parameters'] = self.getDefaultStepsParameters()  
        
        if 'self.ADP_GUI.getTextClipboard' in line:
            textParam = self.getParameterCache(testInputs=testInputs, paramId=i)
            
            stp['action'] = GuiSteps.GET_TEXT_CLIPBOARD
            if textParam is not None:
                stp['text'] = textParam['value']
                stp['parameters'].update( {'from-cache': True} ) 
                # stp['from-cache'] = True
                
        if 'self.ADP_GUI.hoverImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.HOVER_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']   
                
        if 'self.ADP_GUI.clickWord' in line:
            stp['action'] = GuiSteps.CLICK_WORD
            stp['parameters'] = self.getParametersWord(testInputs=testInputs, paramId=i)
            if 'word=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'self.ADP_GUI.doubleClickWord' in line:
            stp['action'] = GuiSteps.DOUBLE_CLICK_WORD
            stp['parameters'] = self.getParametersWord(testInputs=testInputs, paramId=i)
            if 'word=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'self.ADP_GUI.rightClickWord' in line:
            stp['action'] = GuiSteps.RIGHT_CLICK_WORD
            stp['parameters'] = self.getParametersWord(testInputs=testInputs, paramId=i)
            if 'word=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'self.ADP_GUI.waitWord' in line:
            stp['action'] = GuiSteps.WAIT_WORD
            stp['parameters'] = self.getParametersWord(testInputs=testInputs, paramId=i)
            if 'word=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'self.ADP_GUI.waitClickWord' in line:
            stp['action'] = GuiSteps.WAIT_CLICK_WORD
            stp['parameters'] = self.getParametersWord(testInputs=testInputs, paramId=i)
            if 'word=Cache().get(name=' in line: 
                stp['parameters'].update( {'from-cache': True} )   
            else:
                stp['parameters'].update( {'from-cache': False} )  
                
        if 'self.ADP_GUI.clickImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.CLICK_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.clickImage' in line and 'findAll=True' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.CLICK_IMAGE_ALL
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.doubleClickImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.DOUBLE_CLICK_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.doubleClickImage' in line and 'findAll=True' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.DOUBLE_CLICK_IMAGE_ALL
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.rightClickImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.RIGHT_CLICK_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.rightClickImage' in line and 'findAll=True' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.RIGHT_CLICK_IMAGE_ALL
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if "self.ADP_GUI.dragDropImage" in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.DRAG_DROP_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
            toY = self.getParameterDropY(testInputs=testInputs, paramId=i)
            if toY is not None:
                stp['text'] = toY['value']
            toX = self.getParameterDropX(testInputs=testInputs, paramId=i)
            if toX is not None:
                stp['misc'] = toX['value']  
                
        if 'self.ADP_GUI.mouseWheelDown' in line:
            waitParam = self.getParameterWheel(testInputs=testInputs, paramId=i)
            if waitParam is not None:
                stp['action'] = GuiSteps.MOUSE_WHEEL_DOWN
                stp['misc'] = waitParam['value']
                
        if 'self.ADP_GUI.mouseWheelUp' in line:
            waitParam = self.getParameterWheel(testInputs=testInputs, paramId=i)
            if waitParam is not None:
                stp['action'] = GuiSteps.MOUSE_WHEEL_UP
                stp['misc'] = waitParam['value']
                
        if "self.ADP_GUI.clickPosition" in line:
            stp['action'] = GuiSteps.MOUSE_CLICK_POSITION
            toX = self.getParameterToX(testInputs=testInputs, paramId=i)
            if toX is not None:
                stp['text'] = toX['value']
            toY = self.getParameterToY(testInputs=testInputs, paramId=i)
            if toY is not None:
                stp['misc'] = toY['value']   
                
        if "self.ADP_GUI.doubleClickPosition" in line:
            stp['action'] = GuiSteps.MOUSE_DOUBLE_CLICK_POSITION
            toX = self.getParameterToX(testInputs=testInputs, paramId=i)
            if toX is not None:
                stp['text'] = toX['value']
            toY = self.getParameterToY(testInputs=testInputs, paramId=i)
            if toY is not None:
                stp['misc'] = toY['value']   
                
        if "self.ADP_GUI.rightClickPosition" in line:
            stp['action'] = GuiSteps.MOUSE_RIGHT_CLICK_POSITION
            toX = self.getParameterToX(testInputs=testInputs, paramId=i)
            if toX is not None:
                stp['text'] = toX['value']
            toY = self.getParameterToY(testInputs=testInputs, paramId=i)
            if toY is not None:
                stp['misc'] = toY['value']  
                
        if "self.ADP_GUI.mouseMovePosition" in line:
            stp['action'] = GuiSteps.MOUSE_MOVE_POSITION
            toX = self.getParameterToX(testInputs=testInputs, paramId=i)
            if toX is not None:
                stp['text'] = toX['value']
            toY = self.getParameterToY(testInputs=testInputs, paramId=i)
            if toY is not None:
                stp['misc'] = toY['value']  
                
        if "self.ADP_GUI.typeText" in line:
            textParam,textPwd,textAlias = self.getParameterText(testInputs=testInputs, paramId=i)
            if textParam is not None:
                stp['action'] = GuiSteps.TYPE_TEXT
                if textPwd: stp['action'] = GuiSteps.TYPE_PASSWORD
                stp['text'] = textParam['value']
                if textAlias: 
                    stp["parameters"]['from-alias'] = True
                else:
                    if 'Cache().get(name=' in line: stp["parameters"]['from-cache'] = True     
 
        if 'self.ADP_GUI.typePath' in line:
            textParam,textPwd,textAlias = self.getParameterText(testInputs=testInputs, paramId=i)
            if textParam is not None:
                stp['action'] = GuiSteps.TYPE_TEXT_PATH
                stp['text'] = textParam['value']
                if textAlias: 
                    stp["parameters"]['from-alias'] = True
                else:
                    if 'Cache().get(name=' in line: stp["parameters"]['from-cache'] = True      
                    
        if "self.ADP_GUI.typeShorcut(" in line:
            try:
                mainKey = line.split("typeShorcut(key=")[1].split(",", 1)[0]
                modifierKey = line.split("modifier=")[1].split(",", 1)[0]
                specialKey = line.split("special=")[1].split(",", 1)[0]
                
                if 'repeat=' in line:
                    finalKey = line.split("other=")[1].split(",", 1)[0]

                    repeatValue = line.split("repeat=")[1].split(")", 1)[0]
                    stp['option-similar'] = repeatValue
                else:
                    finalKey = line.split("other=")[1].split(")", 1)[0]
                
                if finalKey.startswith("'") and finalKey.endswith("'"):
                    finalKey = finalKey[1:-1]
                    
            except Exception as e :
                self.error("unable to detect shortcut line: %s" % e )
            else:
                stp['action'] = GuiSteps.SHORTCUT
                keysFinal = []
                if mainKey != 'None':
                    if 'SutAdapters.GUI' in mainKey:
                        keysFinal.append(mainKey.split('SutAdapters.GUI.KEY_')[1].strip())
                    if 'SutAdapters.Generic.GUI' in mainKey:
                        keysFinal.append(mainKey.split('SutAdapters.Generic.GUI.KEY_')[1].strip())
                if modifierKey != 'None':
                    if 'SutAdapters.GUI' in modifierKey:
                        keysFinal.append(modifierKey.split('SutAdapters.GUI.KEY_')[1].strip())
                    if 'SutAdapters.Generic.GUI' in modifierKey:
                        keysFinal.append(modifierKey.split('SutAdapters.Generic.GUI.KEY_')[1].strip())
                if specialKey != 'None':
                    if 'SutAdapters.GUI' in specialKey:
                        keysFinal.append(specialKey.split('SutAdapters.GUI.KEY_')[1].strip())
                    if 'SutAdapters.Generic.GUI' in specialKey:
                        keysFinal.append(specialKey.split('SutAdapters.Generic.GUI.KEY_')[1].strip())
                stp['misc'] = '+'.join(keysFinal)
                if finalKey != 'None':
                    stp['text'] = finalKey.upper()

                if len(stp['text']):
                    stp['misc'] = "%s+" % stp['misc']
                    
        if 'self.ADP_GUI.findImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.FIND_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']   
                
        if 'self.ADP_GUI.dontFindImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.DONT_FIND_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']   
                
        if 'self.ADP_GUI.waitImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.WAIT_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.findClickImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.FIND_CLICK_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']
                
        if 'self.ADP_GUI.waitClickImage' in line:
            imageParam = self.getParameterImage(testInputs=testInputs, paramId=i)
            if imageParam is not None:
                stp['action'] = GuiSteps.WAIT_CLICK_IMAGE
                stp['image'] = imageParam['value']
                stp['option-similar'] = imageParam['similar']                   

    def reconstructStepsSelenium(self, line, i, stp, testInputs):
        """
        Reconstruct step for selenium actions
        """
        if 'parameters' not in stp:
            stp['parameters'] = self.getDefaultStepsParameters()  
        
        if 'self.ADP_GUI_BROWSER.doOpen' in line:
            textUrl, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textUrl is not None:
                stp['action'] = GuiSteps.BROWSER_OPEN
                stp['text'] = textUrl['value']
                browser = GuiSelenium.BROWSER_FIREFOX
                sessionName = "default"
                useGecko = "False"
                for p in testInputs['parameter']:
                    if p['name'].startswith('BROWSER_USE_IE_%s' % i):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_IE
                            break
                    if p['name'].startswith('BROWSER_USE_FIREFOX_%s' % i):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_FIREFOX
                            break
                    if p['name'].startswith('BROWSER_USE_CHROME_%s' % i):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_CHROME
                            break
                    if p['name'].startswith('BROWSER_USE_OPERA_%s' % i):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_OPERA
                            break
                    if p['name'].startswith('BROWSER_USE_EDGE_%s' % i):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_EDGE
                            break
                    # old params just kept for compatibility
                    if p['name'].startswith('BROWSER_USE_IE'):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_IE
                            break
                    if p['name'].startswith('BROWSER_USE_FIREFOX'):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_FIREFOX
                            break
                    if p['name'].startswith('BROWSER_USE_CHROME'):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_CHROME
                            break
                    if p['name'].startswith('BROWSER_USE_OPERA'):
                        if p['value'] == "True": 
                            browser = GuiSelenium.BROWSER_OPERA
                            break
                            
                for p in testInputs['parameter']:
                    if p['name'].startswith('BROWSER_SESSION_%s' % i):
                        sessionName = p['value']
                        break
                        
                for p in testInputs['parameter']:
                    if p['name'].startswith('BROWSER_USE_DRIVER_GECKO'):
                        useGecko = p['value']
                        break
                    if p['name'].startswith('BROWSER_DRIVER_GECKO_%s' % i):
                        useGecko = p['value']
                        break
                        
                stp['misc'] = browser  
                stp['parameters']['session-name'] = sessionName  
                stp['parameters']['use-gecko'] = useGecko
                if 'Cache().get(name=' in line: stp['parameters']['from-cache'] = True
                if textAlias: stp['parameters']['from-alias'] = True

        if 'self.ADP_GUI_BROWSER.doClose' in line:
            stp['action'] = GuiSteps.BROWSER_CLOSE    
            
        if 'self.ADP_GUI_BROWSER.doDismissAlert' in line:
            stp['action'] = GuiSteps.BROWSER_DISMISS_ALERT 
            
        if 'self.ADP_GUI_BROWSER.doAcceptAlert' in line:
            stp['action'] = GuiSteps.BROWSER_ACCEPT_ALERT   
            
        if 'self.ADP_GUI_BROWSER.doGetTextAlert' in line:
            stp['action'] = GuiSteps.BROWSER_GET_TEXT_ALERT
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                # stp['from-cache'] = True     
                stp['parameters']['from-cache'] = True
                
        if 'self.ADP_GUI_BROWSER.doMaximizeWindow' in line:
            stp['action'] = GuiSteps.BROWSER_MAXIMIZE         
            
        if 'self.ADP_GUI_BROWSER.doCloseWindow' in line:
            stp['action'] = GuiSteps.BROWSER_CLOSE_WINDOW   
            
        if 'self.ADP_GUI_BROWSER.doSwitchToNextWindow' in line:
            stp['action'] = GuiSteps.BROWSER_SWITCH_NEXT_WINDOW   
            
        if 'self.ADP_GUI_BROWSER.doSwitchToDefaultWindow' in line:
            stp['action'] = GuiSteps.BROWSER_SWITCH_MAIN_WINDOW
            
        if 'self.ADP_GUI_BROWSER.doRefreshPage' in line:
            stp['action'] = GuiSteps.BROWSER_REFRESH  
            
        if 'self.ADP_GUI_BROWSER.doGoBack' in line:
            stp['action'] = GuiSteps.BROWSER_GO_BACK  
            
        if 'self.ADP_GUI_BROWSER.doGoForward' in line:
            stp['action'] = GuiSteps.BROWSER_GO_FORWARD   
            
        if 'self.ADP_GUI_BROWSER.doGetPageSource' in line:
            stp['action'] = GuiSteps.BROWSER_GET_SOURCE
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                stp['parameters']['to-cache'] = True                 
        
        if 'self.ADP_GUI_BROWSER.doGetPageUrl' in line:
            stp['action'] = GuiSteps.BROWSER_GET_URL
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                stp['parameters']['to-cache'] = True             
       
        if 'self.ADP_GUI_BROWSER.doGetPageTitle' in line:
            stp['action'] = GuiSteps.BROWSER_GET_TITLE
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                stp['parameters']['to-cache'] = True    
                
        if 'self.ADP_GUI_BROWSER.doWaitClickElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_WAIT_CLICK_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)    
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
                
        if 'self.ADP_GUI_BROWSER.doWaitVisibleClickElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_WAIT_VISIBLE_CLICK_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)    
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doClickElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_CLICK_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line) 

            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doDoubleClickElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_DOUBLE_CLICK_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)  
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doClearTextElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_CLEAR_TEXT_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)    
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doHoverElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_HOVER_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doSwitchToFrame' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_SWITCH_TO_FRAME
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doWaitElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_WAIT_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doWaitVisibleElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_WAIT_VISIBLE_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doWaitNotVisibleElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_WAIT_NOT_VISIBLE_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
        if 'self.ADP_GUI_BROWSER.doGetText' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_GET_TEXT_ELEMENT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            if isAlias: stp['parameters']['from-el-alias'] = True
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                stp['parameters']['to-cache'] = True
                
        if 'self.ADP_GUI_BROWSER.doTypeText' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_TYPE_TEXT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            if isAlias: stp['parameters']['from-el-alias'] = True
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                if textAlias: stp['parameters']['from-alias'] = True
            
            if 'text=Cache().get(name=' in line: stp['parameters']['from-cache'] = True
            
            match = re.search( '(name|tagName|className|id|xpath|linkText|partialLinkText|cssSelector)=Cache\(\).get\(name=', line)
            if match: stp['parameters']['from-el-cache'] = True
                
        if 'self.ADP_GUI_BROWSER.doRunJsElement' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_EXECUTE_JS
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            if isAlias: stp['parameters']['from-el-alias'] = True
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                if textAlias: stp['parameters']['from-alias'] = True
            
            if 'js=Cache().get(name=' in line: stp['parameters']['from-cache'] = True
            
            match = re.search( '(name|tagName|className|id|xpath|linkText|partialLinkText|cssSelector)=Cache\(\).get\(name=', line)
            if match: stp['parameters']['from-el-cache'] = True

        if 'self.ADP_GUI_BROWSER.doSelectByText' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_SELECT_TEXT
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            if isAlias: stp['parameters']['from-el-alias'] = True

            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                if textAlias: stp['parameters']['from-alias'] = True
            
            if 'text=Cache().get(name=' in line:  stp['parameters']['from-cache'] = True
            
            match = re.search( '(name|tagName|className|id|xpath|linkText|partialLinkText|cssSelector)=Cache\(\).get\(name=', line)
            if match: stp['parameters']['from-el-cache'] = True
                
        if 'self.ADP_GUI_BROWSER.doSelectByValue' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_SELECT_VALUE
                stp['text'] = textSearch['value']
                # if 'Cache().get(name=' in line: stp['from-cache'] = True
            stp['misc'] = self.getSearchBY(line=line)
            if isAlias: stp['parameters']['from-el-alias'] = True
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                if textAlias: stp['parameters']['from-alias'] = True
            
            if 'text=Cache().get(name=' in line:  stp['parameters']['from-cache'] = True
            
            match = re.search( '(name|tagName|className|id|xpath|linkText|partialLinkText|cssSelector)=Cache\(\).get\(name=', line)
            if match: stp['parameters']['from-el-cache'] = True
                
        if 'self.ADP_GUI_BROWSER.doTypeKey' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_TYPE_KEY
                stp['text'] = textSearch['value']
            stp['misc'] = self.getSearchBY(line=line)
            if isAlias: stp['parameters']['from-el-alias'] = True
            if 'Cache().get(name=' in line: stp['parameters']['from-el-cache'] = True
            
            # extract key
            if 'SutAdapters.GUI' in line:
                keyStr = line.split("key=SutAdapters.GUI.SELENIUM_KEY_")[1].split(",", 1)[0].strip()
            if 'SutAdapters.Generic.GUI' in line:
                keyStr = line.split("key=SutAdapters.Generic.GUI.SELENIUM_KEY_")[1].split(",", 1)[0].strip()
                
            # repeat
            repeatStr = 0
            if "repeat=" in line:
                repeatStr = line.split("repeat=")[1].split(")")[0].strip()
                
            stp['text-more'] = "%s;%s" % (keyStr, repeatStr)
            
        if 'self.ADP_GUI_BROWSER.doFindText' in line:
            textSearch, isAlias = self.getParameterTextByBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_FIND_TEXT_ELEMENT
                stp['text'] = textSearch['value']
                # if 'Cache().get(name=' in line: stp['from-cache'] = True
            stp['misc'] = self.getSearchBY(line=line)
            if isAlias: stp['parameters']['from-el-alias'] = True
            
            
            textValue, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textValue is not None:
                stp['text-more'] = textValue['value']
                if textAlias: stp['parameters']['from-alias'] = True
            
            if 'needle=Cache().get(name=' in line: 
                stp['parameters']['from-cache'] = True
            
            match = re.search( '(name|tagName|className|id|xpath|linkText|partialLinkText|cssSelector)=Cache\(\).get\(name=', line)
            if match: stp['parameters']['from-el-cache'] = True

        if 'self.ADP_GUI_BROWSER.doFindTextPageTitle' in line:
            textSearch, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_FIND_TEXT_TITLE
                stp['text'] = textSearch['value']
                if 'Cache().get(name=' in line: stp['parameters']['from-cache'] = True
                if textAlias: stp['parameters']['from-alias'] = True

        if 'self.ADP_GUI_BROWSER.doSwitchToWindow' in line:
            textSearch, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_SWITCH_TO_WINDOW
                stp['text-more'] = textSearch['value']
                if 'Cache().get(name=' in line: stp['parameters']['from-cache'] = True
                if textAlias: stp['parameters']['from-alias'] = True

        if 'self.ADP_GUI_BROWSER.doSwitchToSession' in line:
            textSearch, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_SWITCH_TO_SESSION
                stp['text-more'] = textSearch['value']
                if 'Cache().get(name=' in line: stp['parameters']['from-cache'] = True
                if textAlias: stp['parameters']['from-alias'] = True
                
        if 'self.ADP_GUI_BROWSER.doFindTextPageUrl' in line:
            textSearch, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_FIND_TEXT_GET_URL
                stp['text'] = textSearch['value'] 
                if 'Cache().get(name=' in line: stp['parameters']['from-cache'] = True
                if textAlias: stp['parameters']['from-alias'] = True
                
        if 'self.ADP_GUI_BROWSER.doFindTextPageSource' in line:
            textSearch, textAlias = self.getParameterTextBrowser(testInputs=testInputs, paramId=i)
            if textSearch is not None:
                stp['action'] = GuiSteps.BROWSER_FIND_TEXT_GET_SOURCE
                stp['text'] = textSearch['value']
                if 'Cache().get(name=' in line: stp['parameters']['from-cache'] = True
                if textAlias: stp['parameters']['from-alias'] = True
                 
    def getSearchBY(self, line):
        """
        Parse search by
        """
        searchBy  = GuiSelenium.BROWSER_BY_NAME
        if "name=None" not in line: 
            if "name=" in line: searchBy = GuiSelenium.BROWSER_BY_NAME
        if "tagName=None" not in line: 
            if "tagName=" in line: searchBy = GuiSelenium.BROWSER_BY_TAG_NAME
        if "className=None" not in line: 
            if "className=" in line: searchBy = GuiSelenium.BROWSER_BY_CLASS_NAME
        if "id=None" not in line: 
            if "id=" in line: searchBy = GuiSelenium.BROWSER_BY_ID
        if "xpath=None" not in line: 
            if "xpath=" in line: searchBy = GuiSelenium.BROWSER_BY_XPATH
        if "linkText=None" not in line: 
            if "linkText=" in line: searchBy = GuiSelenium.BROWSER_BY_LINK_TEXT
        if "partialLinkText=None" not in line: 
            if "partialLinkText=" in line: searchBy = GuiSelenium.BROWSER_BY_PARTIAL_LINK_TEXT
        if "cssSelector=None" not in line: 
            if "cssSelector=" in line: searchBy = GuiSelenium.BROWSER_BY_CSS_SELECTOR
        
        return searchBy 
        
    def loadAgents(self):
        """
        Load agents
        """
        self.updateStepsAction.setEnabled(False)

        self.sikuliGroup.getAgentList().clear()
        self.seleniumGroup.getAgentList().clear()
        self.androidGroup.getAgentList().clear()
        self.sshGroup.getAgentList().clear()
        runningAgents = ServerAgents.instance().getRunningAgentsComplete()
        for agt in runningAgents:
            if agt['type'].lower() in ['sikulix', 'sikulixserver' ]:
                self.sikuliGroup.getAgentList().addItem ( agt['name'] )
            if agt['type'].lower() in ['selenium', 'seleniumserver' ]:
                self.seleniumGroup.getAgentList().addItem ( agt['name'] )
            if agt['type'].lower() == 'adb':
                self.androidGroup.getAgentList().addItem ( agt['name'] )
            if agt['type'].lower() == 'ssh':
                self.sshGroup.getAgentList().addItem ( agt['name'] )
                
    def onTakeSnapshot(self):
        """
        On snapshot taken
        """
        self.takeSnapshot()
        
    def takeSnapshot(self):
        """
        Take a snapshot
        """
        self.recorderActivated = True
        self.snapshotActivated = False
        self.mouseActivated = False

        self.mainParent.captureRecorderAction.setEnabled(True)
        self.setVisible(False)
        
        self.mainParent.showRecordButton()

    def takeSnapshotFromParameters(self, destRow):
        """
        Take a snapshot from test propertiess
        """
        self.snapshotActivated = True
        self.recorderActivated = False
        self.mouseActivated = False
        self.destRow = destRow

        self.mainParent.captureRecorderAction.setEnabled(True)
        self.setVisible(False)
        self.mainParent.showRecordButton()
        
    def onTakeMousePosition(self):
        """
        On take mouse position
        """
        self.takeMousePosition()
        
    def onTakeMouseLocation(self):
        """
        On take mouse location
        """
        self.takeMouseLocation()
        
    def takeMousePosition(self):
        """
        Take a snapshot
        """
        self.recorderActivated = False
        self.snapshotActivated = False
        self.mouseActivated = True
        
        self.mainParent.showRecordButton(mousePosition=True)
        self.mainParent.captureRecorderAction.setEnabled(True)
        self.setVisible(False)
        
    def takeMouseLocation(self):
        """
        Take a snapshot
        """
        self.recorderActivated = False
        self.snapshotActivated = False
        self.mouseActivated = False
        self.locationActivated = True
        
        self.mainParent.showRecordButton(mouseLocation=True)
        self.mainParent.captureRecorderAction.setEnabled(True)
        self.setVisible(False)
        
    def closeEvent(self, event):
        """
        Close window
        """
        self.mainParent.captureRecorderAction.setEnabled(False)

        event.accept()
        self.parent.stopGui()

    def cancelRecording(self):
        """
        Cancel recording
        """
        self.close()

GUI = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return GUI

def initialize (parent, offlineMode=False, mainParent=None):
    """
    Initialize WServerInformation widget
    """
    global GUI
    GUI = WRecorderGui(parent, offlineMode=offlineMode, mainParent=mainParent)

def finalize ():
    """
    Destroy Singleton
    """
    global GUI
    if GUI:
        GUI.cleanup()
        del GUI
        GUI = None