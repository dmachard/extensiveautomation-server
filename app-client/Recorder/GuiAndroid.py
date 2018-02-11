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
Android assistant module
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
    from PyQt4.QtGui import (QWidget, QKeySequence, QPixmap, QDialog, QApplication, QCursor, 
                            QIcon, QToolBar, QGroupBox, QLineEdit, QDoubleValidator, QComboBox, 
                            QGridLayout, QLabel, QFrame, QVBoxLayout, QIntValidator, QHBoxLayout, 
                            QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, QFont, QDialogButtonBox,
                            QCheckBox, QSplitter, QMessageBox, QDesktopWidget, QValidator, QPushButton)
    from PyQt4.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QKeySequence, QPixmap, QCursor, QIcon, QDoubleValidator, 
                                QIntValidator, QValidator, QFont)
    from PyQt5.QtWidgets import (QWidget, QDialog, QApplication, QToolBar, QGroupBox, QLineEdit, QDialogButtonBox,
                                QComboBox, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                                QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                                QCheckBox, QSplitter, QMessageBox, QPushButton)
    from PyQt5.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal)
        
from Libs import QtHelper, Logger
import Settings

try:
    import GuiSteps
except ImportError: # python3 support
    from . import GuiSteps
    
KEYS_SHORTCUT_ANDROID = [
        "HOME",
        "BACK",
        "LEFT",
        "RIGHT",
        "UP",
        "DOWN",
        "CENTER",
        "MENU",
        "SEARCH",
        "ENTER",
        "DELETE",
        "RECENT",
        "VOLUMEUP",
        "VOLUMEDOWN",
        "VOLUMEMUTE",
        "CAMERA",
        "POWER",
]

EMPTY_VALUE = ''

INDEX_TEXT = 0
INDEX_CACHE = 1
INDEX_ALIAS = 2
       
LIST_TYPES = ["TEXT", "CACHE", "ALIAS"]

class ValidatorUpper(QValidator):
    """
    Vaidator upper
    """
    def validate(self, string, pos):
        """
        validate
        """
        return QValidator.Acceptable, string.upper(), pos
        
class ValidatorAll(QValidator):
    """
    Validator all
    """
    def validate(self, string, pos):
        """
        validate
        """
        return QValidator.Acceptable, string, pos
        
class OptionsDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Update locations dialog
    """
    def __init__(self, parent=None):
        """
        Dialog to rename file or folder

        @param currentName: 
        @type currentName: 

        @param folder: 
        @type folder:

        @param parent: 
        @type parent: 
        """
        super(OptionsDialog, self).__init__(parent)

        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        
        self.TIMEOUT_ANDROID_ACTION = Settings.instance().readValue( key = 'TestGenerator/timeout-android-action' )

        self.timeoutAndroidLine = QLineEdit()
        self.timeoutAndroidLine.setText(str(self.TIMEOUT_ANDROID_ACTION))
        validatorAndroid = QDoubleValidator(self)
        validatorAndroid.setNotation(QDoubleValidator.StandardNotation)
        self.timeoutAndroidLine.setValidator(validatorAndroid)
        self.timeoutAndroidLine.installEventFilter(self)

        self.agentNameLineAndroid = QLineEdit("AGENT_ANDROID")

        self.agentsAndroidList = QComboBox()
        self.agentsAndroidList.setMinimumWidth(300)
        
        optionAndroidLayout = QGridLayout()
        optionAndroidLayout.addWidget(QLabel( self.tr("Max time to run action:") ), 1, 0)
        optionAndroidLayout.addWidget(self.timeoutAndroidLine, 1, 1)

        optionAndroidLayout.addWidget(QLabel( self.tr("Agent Key Name:") ), 3, 0)
        optionAndroidLayout.addWidget(self.agentNameLineAndroid, 3, 1)

        optionAndroidLayout.addWidget(QLabel( self.tr("Agent:") ), 4, 0)
        optionAndroidLayout.addWidget(self.agentsAndroidList, 4, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(optionAndroidLayout)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Android Options"))

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        
class WAndroid(QWidget, Logger.ClassLogger):
    """
    Android widget
    """
    # action, description, misc, parameters
    AddStep = pyqtSignal(str, str, str, dict)
    UpdateStep = pyqtSignal(str, str, str, dict)    
    CancelEdit = pyqtSignal()
    def __init__(self, parent):
        """
        Constructor
        """
        QWidget.__init__(self)

        self.createActions()
        self.createWidgets()
        self.createToolbar()
        self.createConnections()
    
    def createActions(self):
        """
        Create qt actions
        """
        self.addAndroidAction = QPushButton(QIcon(":/add_black.png"), '&Add Action', self)
        self.addAndroidAction.setMinimumHeight(40)         
        self.addAndroidAction.setMaximumWidth(150)
        
        self.cancelAndroidAction = QtHelper.createAction(self, "&Cancel", self.cancelStep, 
                                            icon=None, tip = 'Cancel update')
        self.cancelAndroidAction.setEnabled(False)
        
        self.optionsAction = QtHelper.createAction(self, "&", self.openOptions, 
                                            icon=QIcon(":/recorder-mobile-small.png"), tip = 'Android options')
                                            
    def createWidgets(self):
        """
        Create qt widgets
        """
        self.optionsDialog  = OptionsDialog(self)
        
        self.validatorUpper = ValidatorUpper(self)
        self.validatorAll = ValidatorAll(self)
        self.validatorInt = QIntValidator(self)

        ###################### android action #########################

        self.actionsAndroidComboBox = QComboBox(self)
        self.actionsAndroidComboBox.setMinimumHeight(40)
        for i in xrange(len(GuiSteps.ACTION_ANDROID_DESCR)):
            if not len( GuiSteps.ACTION_ANDROID_DESCR[i] ):
                self.actionsAndroidComboBox.insertSeparator(i+1)
            else:
                el = GuiSteps.ACTION_ANDROID_DESCR[i].keys()
                self.actionsAndroidComboBox.addItem( list(el)[0] )
            
        self.descriptionAndroidLine = QLineEdit(self)
        self.descriptionAndroidLine.setPlaceholderText("Step purpose description")
        self.descriptionAndroidLine.hide()

        self.labelActionAndroidDescr = QLabel( )
        self.labelActionAndroidDescr.hide()
        self.labelActionAndroidDescr.setText( "%s\n" % GuiSteps.ACTION_ANDROID_DESCR[0][GuiSteps.ANDROID_WAKEUP_UNLOCK])
        self.labelActionAndroidDescr.setWordWrap(True)
        
        actionsLayout = QHBoxLayout()
        actionsLayout.addWidget(self.actionsAndroidComboBox)
        
        actionLayoutAndroid = QGridLayout()
        actionLayoutAndroid.addLayout(actionsLayout, 0, 1)

        self.createWidgetShortcut()
        self.createWidgetCode()
        self.createWidgetStart()
        self.createWidgetXY()
        self.createWidgetEndXY()
        self.createWidgetElement()
        self.createWidgetTextTo()
        self.createWidgetLine()
        self.createWidgetLine2()
        
        actionLayoutAndroid2 = QGridLayout()
        actionLayoutAndroid2.addWidget( self.shortcutAndroidGroup , 0, 0)
        actionLayoutAndroid2.addWidget( self.codeAndroidGroup , 0, 0)
        actionLayoutAndroid2.addWidget( self.elemenAndroidGroup , 0, 0)
        actionLayoutAndroid2.addWidget( self.xyAndroidGroup , 0, 0)
        actionLayoutAndroid2.addWidget( self.startAndroidGroup , 0, 0)
        actionLayoutAndroid2.addWidget( self.lineAndroidGroup , 1, 0)
        actionLayoutAndroid2.addWidget( self.line2AndroidGroup , 0, 1)
        actionLayoutAndroid2.addWidget( self.textToGlobalGroup , 0, 1)
        actionLayoutAndroid2.addWidget( self.endXyAndroidGroup, 0, 1)
        
        font = QFont()
        font.setBold(True)
        
        labelAct = QLabel( self.tr("Action: ") )
        labelAct.setFont( font) 
        
        self.arrowLabel = QLabel("")
        self.arrowLabel.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))
        self.arrowLabel.hide()
        
        self.arrowLabel2 = QLabel("")
        self.arrowLabel2.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))

        layoutAndroid = QHBoxLayout()
        layoutAndroid.addWidget( labelAct )
        layoutAndroid.addLayout( actionLayoutAndroid )
        layoutAndroid.addWidget( self.arrowLabel )
        layoutAndroid.addLayout( actionLayoutAndroid2 )
        layoutAndroid.addWidget( self.arrowLabel2 )
        layoutAndroid.addWidget(self.addAndroidAction)

        layoutAndroid.addStretch(1)
        self.setLayout(layoutAndroid)
        
    def createToolbar(self):
        """
        Create qt toolbar
        """
        pass
        
    def openOptions(self):
        """
        Open options
        """
        if self.optionsDialog.exec_() == QDialog.Accepted:
            pass
            
    def createWidgetLine2(self):
        """
        Create line widget
        """
        self.valueAndroidLine2 = QLineEdit(self)
        self.valueAndroidLine2.setMinimumWidth(150)
        self.valueAndroidCombo2 = QComboBox(self)
        self.valueAndroidCombo2.addItems( LIST_TYPES )

        self.line2AndroidGroup = QGroupBox(self.tr(""))
        
        line2Androidlayout = QGridLayout()
        line2Androidlayout.addWidget( QLabel( self.tr("Text to type:") ), 0, 0  ) 
        line2Androidlayout.addWidget( self.valueAndroidCombo2, 0, 1 )
        line2Androidlayout.addWidget( self.valueAndroidLine2, 0, 2 )

        self.line2AndroidGroup.setLayout(line2Androidlayout)
        self.line2AndroidGroup.hide()
        
    def createWidgetLine(self):
        """
        Create line widget
        """
        self.lineAndroidGroup = QGroupBox(self.tr(""))
        lineAndroidlayout = QGridLayout()
        self.valueAndroidLine = QLineEdit(self)
        self.valueAndroidLine.setMinimumWidth(300)
        lineAndroidlayout.addWidget( QLabel( self.tr("Value:") ) , 0,1)
        lineAndroidlayout.addWidget( self.valueAndroidLine , 0, 2)
        self.lineAndroidGroup.setLayout(lineAndroidlayout)
        self.lineAndroidGroup.hide()
        
    def createWidgetTextTo(self):
        """
        Create text widget
        """
        self.valueTextCacheGlobalLine = QLineEdit(self)
        self.valueTextCacheGlobalLine.setMinimumWidth(150)
        self.valueTextCacheGlobalCombo = QComboBox(self)
        self.valueTextCacheGlobalCombo.addItems( ["CACHE"] )
        
        self.textToGlobalGroup = QGroupBox(self.tr(""))
        textToGloballayout = QGridLayout()
        textToGloballayout.addWidget( QLabel( self.tr("Save text in:") ) , 0, 0)
        textToGloballayout.addWidget( self.valueTextCacheGlobalCombo , 0, 1)
        textToGloballayout.addWidget( self.valueTextCacheGlobalLine , 0, 2)
        self.textToGlobalGroup.setLayout(textToGloballayout)
        self.textToGlobalGroup.hide()
        
    def createWidgetElement(self):
        """
        Create text widget
        """
        self.elemenAndroidGroup = QGroupBox(self.tr(""))
        
        self.elementTextAndroidLine = QLineEdit(self)
        self.elementTextAndroidLine.setMinimumWidth(300)
        self.elementTextCombo = QComboBox(self)
        self.elementTextCombo.addItems( LIST_TYPES )
        
        self.elementDescriptionAndroidLine = QLineEdit(self)
        self.elementDescriptionAndroidLine.setMinimumWidth(300)
        self.elementClassAndroidLine = QLineEdit(self)
        self.elementClassAndroidLine.setMinimumWidth(300)
        self.elementRessourceIdAndroidLine = QLineEdit(self)
        self.elementRessourceIdAndroidLine.setMinimumWidth(300)
        self.elementPackageAndroidLine = QLineEdit(self)
        self.elementPackageAndroidLine.setMinimumWidth(300)

        # get  text end
        elementAndroidlayout = QGridLayout()
        elementAndroidlayout.addWidget( QLabel( self.tr("Text Element:") ) , 0,1)
        elementAndroidlayout.addWidget( self.elementTextCombo , 0, 2)
        elementAndroidlayout.addWidget( self.elementTextAndroidLine , 0, 3)
        elementAndroidlayout.addWidget( QLabel( self.tr("Description Element:") ) , 1,1)
        elementAndroidlayout.addWidget( self.elementDescriptionAndroidLine , 1, 3)
        elementAndroidlayout.addWidget( QLabel( self.tr("Class Name:") ) , 2,1)
        elementAndroidlayout.addWidget( self.elementClassAndroidLine , 2, 3)
        elementAndroidlayout.addWidget( QLabel( self.tr("Resource ID:") ) , 3,1)
        elementAndroidlayout.addWidget( self.elementRessourceIdAndroidLine , 3, 3)
        elementAndroidlayout.addWidget( QLabel( self.tr("Package Name:") ) , 4,1)
        elementAndroidlayout.addWidget( self.elementPackageAndroidLine , 4, 3)
        self.elemenAndroidGroup.setLayout(elementAndroidlayout)
        self.elemenAndroidGroup.hide()
        
    def createWidgetEndXY(self):
        """
        Create widget 
        """
        self.endXyAndroidGroup = QGroupBox(self.tr(""))
        endXyAndroidlayout = QGridLayout()
        
        self.endxAndroidLine = QLineEdit(self)
        validatorEndXAndroid = QIntValidator (self)
        self.endxAndroidLine.setValidator(validatorEndXAndroid)
        self.endxAndroidLine.installEventFilter(self)
        
        self.endyAndroidLine = QLineEdit(self)
        validatorEndYAndroid = QIntValidator (self)
        self.endyAndroidLine.setValidator(validatorEndYAndroid)
        self.endyAndroidLine.installEventFilter(self)
        
        endXyAndroidlayout.addWidget( QLabel( self.tr("Destination Coordinate X:") ) , 0, 0)
        endXyAndroidlayout.addWidget( self.endxAndroidLine , 0, 1)
        endXyAndroidlayout.addWidget( QLabel( self.tr("Destination Coordinate Y:") ) , 1,0)
        endXyAndroidlayout.addWidget( self.endyAndroidLine , 1, 1)
        
        self.endXyAndroidGroup.setLayout(endXyAndroidlayout)
        self.endXyAndroidGroup.hide()
        
    def createWidgetXY(self):
        """
        Create text widget
        """
        self.xyAndroidGroup = QGroupBox(self.tr(""))
        xyAndroidlayout = QGridLayout()
        
        self.xAndroidLine = QLineEdit(self)
        validatorXAndroid = QIntValidator (self)
        self.xAndroidLine.setValidator(validatorXAndroid)
        self.xAndroidLine.installEventFilter(self)
        
        self.yAndroidLine = QLineEdit(self)
        validatorYAndroid = QIntValidator (self)
        self.yAndroidLine.setValidator(validatorYAndroid)
        self.yAndroidLine.installEventFilter(self)
        
        xyAndroidlayout.addWidget( QLabel( self.tr("Coordinate X:") ) , 0,0)
        xyAndroidlayout.addWidget( self.xAndroidLine , 0, 1)
        xyAndroidlayout.addWidget( QLabel( self.tr("Coordinate Y:") ) , 1,0)
        xyAndroidlayout.addWidget( self.yAndroidLine , 1, 1)
        
        self.xyAndroidGroup.setLayout(xyAndroidlayout)
        self.xyAndroidGroup.hide()
        
    def createWidgetStart(self):
        """
        Create text widget
        """
        self.startAndroidGroup = QGroupBox(self.tr(""))
        startAndroidlayout = QGridLayout()
        
        self.startXAndroidLine = QLineEdit(self)
        validatorStartXAndroid = QIntValidator (self)
        self.startXAndroidLine.setValidator(validatorStartXAndroid)
        self.startXAndroidLine.installEventFilter(self)
        
        self.startYAndroidLine = QLineEdit(self)
        validatorStartYAndroid = QIntValidator (self)
        self.startYAndroidLine.setValidator(validatorStartYAndroid)
        self.startYAndroidLine.installEventFilter(self)
        
        self.stopXAndroidLine = QLineEdit(self)
        validatorStopXAndroid = QIntValidator (self)
        self.stopXAndroidLine.setValidator(validatorStopXAndroid)
        self.stopXAndroidLine.installEventFilter(self)
        
        self.stopYAndroidLine = QLineEdit(self)
        validatorStopYAndroid = QIntValidator (self)
        self.stopYAndroidLine.setValidator(validatorStopYAndroid)
        self.stopYAndroidLine.installEventFilter(self)
        
        startAndroidlayout.addWidget( QLabel( self.tr("From X:") ) , 0,1)
        startAndroidlayout.addWidget( self.startXAndroidLine , 0, 2)
        startAndroidlayout.addWidget( QLabel( self.tr("From Y:") ) , 0,3)
        startAndroidlayout.addWidget( self.startYAndroidLine , 0, 4)
        startAndroidlayout.addWidget( QLabel( self.tr("To X:") ) ,1,1)
        startAndroidlayout.addWidget( self.stopXAndroidLine , 1, 2)
        startAndroidlayout.addWidget( QLabel( self.tr("To Y:") ) , 1,3)
        startAndroidlayout.addWidget( self.stopYAndroidLine , 1 , 4)
        self.startAndroidGroup.setLayout(startAndroidlayout)
        self.startAndroidGroup.hide()
        
    def createWidgetShortcut(self):
        """
        Create shortcut widget
        """
        self.shortcutAndroidGroup = QGroupBox(self.tr(""))
        shortcutAndroidlayout = QGridLayout()

        self.shortcutAndroidComboBox = QComboBox(self)
        for i in xrange(len(KEYS_SHORTCUT_ANDROID)):
            if len(KEYS_SHORTCUT_ANDROID[i]) == 0:
                self.shortcutAndroidComboBox.insertSeparator(i + 2)
            else:
                self.shortcutAndroidComboBox.addItem (KEYS_SHORTCUT_ANDROID[i])

        shortcutAndroidlayout.addWidget( QLabel( self.tr("Button:") ) , 0,1)
        shortcutAndroidlayout.addWidget(self.shortcutAndroidComboBox, 0, 2)
        
        self.shortcutAndroidGroup.setLayout(shortcutAndroidlayout)
        self.shortcutAndroidGroup.hide()

    def createWidgetCode(self):
        """
        Create code widget
        """
        self.codeAndroidGroup = QGroupBox(self.tr(""))
        self.codeAndroidLine = QLineEdit(self)
        validatorCodeAndroid = QIntValidator (self)
        self.codeAndroidLine.setValidator(validatorCodeAndroid)
        self.codeAndroidLine.installEventFilter(self)
        
        codeAndroidlayout = QGridLayout()
        codeAndroidlayout.addWidget( QLabel( self.tr("Code:") ) , 0,1)
        codeAndroidlayout.addWidget( self.codeAndroidLine , 0, 2)
        self.codeAndroidGroup.setLayout(codeAndroidlayout)
        self.codeAndroidGroup.hide()
        
    def pluginDataAccessor(self):
        """
        Return data for plugin
        """
        return { "data": "" } 
        
    def onPluginImport(self, dataJson):
        """
        Received data from plugin
        """
        pass

    def createConnections(self):
        """
        Create qt connections
        """
        self.actionsAndroidComboBox.currentIndexChanged.connect(self.onActionAndroidChanged)
        self.addAndroidAction.clicked.connect(self.addStep)
        self.valueAndroidCombo2.currentIndexChanged.connect(self.onValueAndroid2TypeChanged)
        self.elementTextCombo.currentIndexChanged.connect(self.onElementTextTypeChanged)
        
    def onElementTextTypeChanged(self):
        """
        On element text changed
        """
        if self.elementTextCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.elementTextAndroidLine.setValidator(self.validatorAll)
            
        if self.elementTextCombo.currentText() == "ALIAS":
            self.elementTextAndroidLine.setText( self.elementTextAndroidLine.text().upper() )
            self.elementTextAndroidLine.setValidator(self.validatorUpper)
            
    def onValueAndroid2TypeChanged(self):
        """
        On value changed
        """
        if self.valueAndroidCombo2.currentText() in [ "TEXT", "CACHE" ]:
            self.valueAndroidLine2.setValidator(self.validatorAll)
            
        if self.valueAndroidCombo2.currentText() == "ALIAS":
            self.valueAndroidLine2.setText( self.valueAndroidLine2.text().upper() )
            self.valueAndroidLine2.setValidator(self.validatorUpper)

    def addStep(self):
        """
        Add step
        """
        action = self.actionsAndroidComboBox.currentText()
        descr = self.descriptionAndroidLine.text()
        descr = unicode(descr).replace('"', '')
        
        signal = self.AddStep
        if self.cancelAndroidAction.isEnabled():
            signal = self.UpdateStep
            
        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_WAKUP, GuiSteps.ANDROID_UNLOCK, GuiSteps.ANDROID_REBOOT, 
                                                        GuiSteps.ANDROID_SLEEP, GuiSteps.ANDROID_FREEZE_ROTATION, GuiSteps.ANDROID_UNFREEZE_ROTATION, 
                                                        GuiSteps.ANDROID_BOOTLOADER, GuiSteps.ANDROID_RECOVERY, GuiSteps.ANDROID_NOTIFICATION, 
                                                        GuiSteps.ANDROID_SETTINGS, GuiSteps.ANDROID_DEVICEINFO, GuiSteps.ANDROID_GET_LOGS, 
                                                        GuiSteps.ANDROID_CLEAR_LOGS , GuiSteps.ANDROID_WAKEUP_UNLOCK, GuiSteps.ANDROID_LOCK,
                                                        GuiSteps.ANDROID_SLEEP_LOCK ]:
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, {} )
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_TYPE_SHORTCUT]:
            shorcut = self.shortcutAndroidComboBox.currentText()
            signal.emit( str(action), unicode(descr), shorcut, {} )
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_TYPE_KEYCODE ]:
            code = self.codeAndroidLine.text()
            if not len(code):
                QMessageBox.warning(self, "Recording for Gui" , "Please to set a value!")
            else:
                signal.emit( str(action), unicode(descr), code, {} )
                
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_CLEAR_ELEMENT, GuiSteps.ANDROID_CLICK_ELEMENT, GuiSteps.ANDROID_LONG_CLICK_ELEMENT,
                                                            GuiSteps.ANDROID_EXIST_ELEMENT, GuiSteps.ANDROID_WAIT_ELEMENT, GuiSteps.ANDROID_TYPE_TEXT_ELEMENT,
                                                            GuiSteps.ANDROID_GET_TEXT_ELEMENT, GuiSteps.ANDROID_DRAG_ELEMENT, GuiSteps.ANDROID_WAIT_CLICK_ELEMENT ]:
            textAndroid = self.elementTextAndroidLine.text()
            descrAndroid = self.elementDescriptionAndroidLine.text()
            classAndroid = self.elementClassAndroidLine.text()
            ressourceAndroid = self.elementRessourceIdAndroidLine.text()
            packageAndroid = self.elementPackageAndroidLine.text()
            if not len(textAndroid) and not len(classAndroid) and not len(ressourceAndroid) and not len(packageAndroid) and not len(descrAndroid):
                QMessageBox.warning(self, "Recording for Gui" , "Please to set one value!")
            else:
                # read text from cache or not ?
                fromElCache = False
                if self.elementTextCombo.currentText() == "CACHE": fromElCache = True
                fromElAlias = False
                if self.elementTextCombo.currentText() == "ALIAS": fromElAlias = True
                        
                if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_TYPE_TEXT_ELEMENT:
                    newTextAndroid = self.valueAndroidLine2.text()
                    if not len(newTextAndroid):
                        QMessageBox.warning(self, "Recording for Gui" , "Please to set a text value!")
                    else:
                        # read text from cache or not ?
                        fromCache = False
                        if self.valueAndroidCombo2.currentText() == "CACHE": fromCache = True
                        fromAlias = False
                        if self.valueAndroidCombo2.currentText() == "ALIAS": fromAlias = True
                        
                        parameters = {'text': textAndroid, 'class': classAndroid, 'ressource': ressourceAndroid, 
                                        'package': packageAndroid, 'description': descrAndroid, 'new-text': newTextAndroid,
                                        'from-cache': fromCache, 'from-alias': fromAlias,
                                        'from-el-cache': fromElCache, 'from-el-alias': fromElAlias }
                        signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                
                elif self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_GET_TEXT_ELEMENT:       
                    # read text from cache or not ?
                    cacheKey = ''
                    toCache = True
                    cacheKey = self.valueTextCacheGlobalLine.text()
                        
                    parameters = {'text': textAndroid, 'class': classAndroid, 'ressource': ressourceAndroid, 
                                    'package': packageAndroid, 'description': descrAndroid, 'cache-key': cacheKey,
                                    'to-cache': toCache, 'from-el-cache': fromElCache, 'from-el-alias': fromElAlias }
                    signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                    
                elif self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_DRAG_ELEMENT:       
                    xAndroid = self.endxAndroidLine.text()
                    yAndroid = self.endyAndroidLine.text()
                    if not len(xAndroid) and not len(yAndroid):
                        QMessageBox.warning(self, "Recording for Gui" , "Please to set values!")
                    else:
                        parameters = {'text': textAndroid, 'class': classAndroid, 'ressource': ressourceAndroid, 
                                    'package': packageAndroid, 'description': descrAndroid,
                                    'from-el-cache': fromElCache, 'from-el-alias': fromElAlias,
                                    'x': xAndroid, 'y': yAndroid }
                        signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                    
                else:

                    parameters = {'text': textAndroid, 'class': classAndroid, 'ressource': ressourceAndroid, 
                                    'package': packageAndroid, 'description': descrAndroid,
                                    'from-el-cache': fromElCache, 'from-el-alias': fromElAlias }
                    signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                    
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_CLICK_POSITION ]:
            xAndroid = self.xAndroidLine.text()
            yAndroid = self.yAndroidLine.text()
            if not len(xAndroid) and not len(yAndroid):
                QMessageBox.warning(self, "Recording for Gui" , "Please to set values!")
            else:
                parameters = { 'x': xAndroid, 'y': yAndroid }
                signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_DRAG_ELEMENT, GuiSteps.ANDROID_DRAG_POSITION, 
                                                            GuiSteps.ANDROID_SWIPE_POSITION]:
            startXAndroid = self.startXAndroidLine.text()
            startYAndroid = self.startYAndroidLine.text()
            stopXAndroid = self.stopXAndroidLine.text()
            stopYAndroid = self.stopYAndroidLine.text()
            if not len(startXAndroid) and not len(startYAndroid) and not len(stopXAndroid) and not len(stopYAndroid):
                QMessageBox.warning(self, "Recording for Gui" , "Please to set values!")
            else:
                parameters = { 'start-x': startXAndroid, 'start-y': startYAndroid, 'stop-x': stopXAndroid, 'stop-y': stopYAndroid }
                signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )

        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_COMMAND, GuiSteps.ANDROID_SHELL, GuiSteps.ANDROID_RESET_APP,
                                                            GuiSteps.ANDROID_STOP_APP]:
            miscStr = self.valueAndroidLine.text()
            if not len(miscStr):
                QMessageBox.warning(self, "Recording for Gui" , "Please to set a value!")
            else:
                if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_COMMAND:
                    parameters = { 'cmd': miscStr }
                elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_RESET_APP, GuiSteps.ANDROID_STOP_APP ]:
                    parameters = { 'pkg': miscStr }
                else:
                    parameters = { 'sh': miscStr }
                signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                
        else:
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, {} )
        
    def cancelStep(self):
        """
        Cancel step
        """
        self.addAndroidAction.setText( "&Add" )
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addAndroidAction.setFont(buttonFont)
        
        self.cancelAndroidAction.setEnabled(False)
        
        self.CancelEdit.emit()
    
    def finalizeUpdate(self):
        """
        Finalize the update of a step
        """
        self.addAndroidAction.setText( "&Add Action" )
        
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addAndroidAction.setFont(buttonFont)
        self.cancelAndroidAction.setEnabled(False)
        
    def onActionAndroidChanged(self):
        """
        On action changed
        """
        descr = 'No description available!'
        i = 0
        for el in GuiSteps.ACTION_ANDROID_DESCR:
            if isinstance(el, dict):
                if self.actionsAndroidComboBox.currentText() in el:
                    descr = GuiSteps.ACTION_ANDROID_DESCR[i][self.actionsAndroidComboBox.currentText()]
                    break
            i += 1
        self.labelActionAndroidDescr.setText( "%s\n" % descr )

            
        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_TYPE_SHORTCUT ]:
            self.shortcutAndroidGroup.show()   
            self.codeAndroidGroup.hide()  
            self.elemenAndroidGroup.hide()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_TYPE_KEYCODE ]:
            self.codeAndroidGroup.show()   
            self.shortcutAndroidGroup.hide()    
            self.elemenAndroidGroup.hide()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_CLEAR_ELEMENT, GuiSteps.ANDROID_CLICK_ELEMENT, GuiSteps.ANDROID_LONG_CLICK_ELEMENT,
                                                            GuiSteps.ANDROID_EXIST_ELEMENT, GuiSteps.ANDROID_WAIT_ELEMENT, GuiSteps.ANDROID_WAIT_CLICK_ELEMENT ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.show()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_DRAG_ELEMENT ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.show()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.show()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_GET_TEXT_ELEMENT ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.show()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.show()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_CLICK_POSITION ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.hide()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.show()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_DRAG_POSITION, GuiSteps.ANDROID_SWIPE_POSITION ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.hide()
            self.startAndroidGroup.show()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_COMMAND, GuiSteps.ANDROID_SHELL, GuiSteps.ANDROID_RESET_APP, 
                                                            GuiSteps.ANDROID_STOP_APP  ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.hide()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.show()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
             
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_TYPE_TEXT_ELEMENT ]:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.show()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.show()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        else:
            self.shortcutAndroidGroup.hide()   
            self.codeAndroidGroup.hide()       
            self.elemenAndroidGroup.hide()
            self.startAndroidGroup.hide()
            self.xyAndroidGroup.hide()
            self.lineAndroidGroup.hide()
            self.line2AndroidGroup.hide()
            self.textToGlobalGroup.hide()
            self.endXyAndroidGroup.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.show()
            
    def setTimeout(self, timeout):
        """
        Set the timeout
        """
        self.optionsDialog.timeoutAndroidLine.setText(timeout)
        
    def getTimeout(self):
        """
        Return the timeout
        """
        return self.optionsDialog.timeoutAndroidLine.text()
        
    def getAgentName(self):
        """
        Get the agent name
        """
        return self.optionsDialog.agentNameLineAndroid.text()
        
    def getAgentList(self):
        """
        Return the agent list
        """
        return self.optionsDialog.agentsAndroidList
     
    def editStep(self, stepData):
        """
        Edit a step
        """
        self.addAndroidAction.setText( "&Update" )
        buttonFont = QFont()
        buttonFont.setBold(True)
        self.addAndroidAction.setFont(buttonFont)
        
        self.cancelAndroidAction.setEnabled(True)
            
        # set the current value for actions combo
        for i in xrange(self.actionsAndroidComboBox.count()):
            item_text = self.actionsAndroidComboBox.itemText(i)
            if unicode(stepData["action"]) == unicode(item_text):
                self.actionsAndroidComboBox.setCurrentIndex(i)
                break
        # and then refresh options
        self.onActionAndroidChanged()
        
        # finally fill all fields
        self.descriptionAndroidLine.setText( stepData["description"] )

        if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_COMMAND:
            self.valueAndroidLine.setText( stepData["parameters"]["cmd"] )
            
        if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_SHELL:
            self.valueAndroidLine.setText( stepData["parameters"]["sh"] )
            
        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_RESET_APP, GuiSteps.ANDROID_STOP_APP ]:
            self.valueAndroidLine.setText( stepData["parameters"]["pkg"] )
            
        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_CLEAR_ELEMENT, GuiSteps.ANDROID_TYPE_TEXT_ELEMENT, 
                                                          GuiSteps.ANDROID_CLICK_ELEMENT, GuiSteps.ANDROID_LONG_CLICK_ELEMENT,
                                                          GuiSteps.ANDROID_EXIST_ELEMENT, GuiSteps.ANDROID_WAIT_ELEMENT,
                                                          GuiSteps.ANDROID_GET_TEXT_ELEMENT, GuiSteps.ANDROID_DRAG_ELEMENT,
                                                          GuiSteps.ANDROID_WAIT_CLICK_ELEMENT ]:
                                                          
            self.elementTextAndroidLine.setText( "" )
            self.elementDescriptionAndroidLine.setText( "" )
            self.elementClassAndroidLine.setText( "" )
            self.elementRessourceIdAndroidLine.setText( "" )
            self.elementPackageAndroidLine.setText( "" )
            self.valueAndroidLine2.setText( "" )
            
            if "text" in stepData["parameters"]:
                if stepData["parameters"]["from-el-cache"]:
                    self.elementTextCombo.setCurrentIndex(INDEX_CACHE)
                    self.elementTextAndroidLine.setValidator(self.validatorAll)
                elif stepData["parameters"]["from-el-alias"]:
                    self.elementTextCombo.setCurrentIndex(INDEX_ALIAS)
                    self.elementTextAndroidLine.setValidator(self.validatorUpper) 
                else:
                    self.elementTextCombo.setCurrentIndex(INDEX_TEXT)
                    self.elementTextAndroidLine.setValidator(self.validatorAll)
                
                self.elementTextAndroidLine.setText ( stepData["parameters"]["text"] )

            if "description" in stepData["parameters"]:
                self.elementDescriptionAndroidLine.setText( stepData["parameters"]["description"] )
            if "class" in stepData["parameters"]:
                self.elementClassAndroidLine.setText( stepData["parameters"]["class"] )
            if "ressource" in stepData["parameters"]:
                self.elementRessourceIdAndroidLine.setText( stepData["parameters"]["ressource"] )
            if "package" in stepData["parameters"]:
                self.elementPackageAndroidLine.setText( stepData["parameters"]["package"] )
            if "new-text" in stepData["parameters"]:
                self.valueAndroidLine2.setText( stepData["parameters"]["new-text"] )

            if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_DRAG_ELEMENT:
                if "x" in stepData["parameters"]:
                    self.endxAndroidLine.setText( stepData["parameters"]["x"] )
                if "y" in stepData["parameters"]:
                    self.endyAndroidLine.setText( stepData["parameters"]["y"] )
                
            if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_TYPE_TEXT_ELEMENT:
                if stepData["parameters"]["from-cache"]:
                    self.valueAndroidCombo2.setCurrentIndex(INDEX_CACHE)
                    self.valueAndroidLine2.setValidator(self.validatorAll)
                elif stepData["parameters"]["from-alias"]:
                    self.valueAndroidCombo2.setCurrentIndex(INDEX_ALIAS)
                    self.valueAndroidLine2.setValidator(self.validatorUpper) 
                else:
                    self.valueAndroidCombo2.setCurrentIndex(INDEX_TEXT)
                    self.valueAndroidLine2.setValidator(self.validatorAll)
                
            if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_GET_TEXT_ELEMENT:
                self.valueTextCacheGlobalLine.setText ( stepData["parameters"]["cache-key"] )

        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_CLICK_POSITION]:
            if "x" in stepData["parameters"]:
                self.xAndroidLine.setText( stepData["parameters"]["x"] )
            if "y" in stepData["parameters"]:
                self.yAndroidLine.setText( stepData["parameters"]["y"] )
                
        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_DRAG_POSITION, GuiSteps.ANDROID_SWIPE_POSITION]:
            if "start-x" in stepData["parameters"]:
                self.startXAndroidLine.setText( stepData["parameters"]["start-x"] )
            if "start-y" in stepData["parameters"]:
                self.startYAndroidLine.setText( stepData["parameters"]["start-y"] )
            if "stop-x" in stepData["parameters"]:
                self.stopXAndroidLine.setText( stepData["parameters"]["stop-x"] )
            if "stop-y" in stepData["parameters"]:
                self.stopYAndroidLine.setText( stepData["parameters"]["stop-y"] )

        if self.actionsAndroidComboBox.currentText() == GuiSteps.ANDROID_TYPE_KEYCODE:
            self.codeAndroidLine.setText( stepData["misc"] )
            
        if self.actionsAndroidComboBox.currentText() in [ GuiSteps.ANDROID_TYPE_SHORTCUT ]:
            # set default
            for i in xrange(self.shortcutAndroidComboBox.count()):
                item_text = self.shortcutAndroidComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.shortcutAndroidComboBox.setCurrentIndex(i)
                    break
