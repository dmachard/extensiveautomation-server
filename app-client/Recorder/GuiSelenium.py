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
Selenium assistant module
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
    from PyQt5.QtWidgets import (QWidget, QDialog, QApplication, QToolBar, QGroupBox, QLineEdit, 
                                QComboBox, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                                QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, QDialogButtonBox,
                                QCheckBox, QSplitter, QMessageBox, QPushButton, QDesktopWidget)
    from PyQt5.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal)

from Libs import QtHelper, Logger
import Settings

try:
    import GuiSteps
except ImportError: # python3 support
    from . import GuiSteps

import copy

KEYS_BROWSER = [
    "NULL",
    "CANCEL",
    "HELP",
    "BACKSPACE",
    "TAB",
    "CLEAR",
    "RETURN",
    "ENTER",
    "SHIFT",
    "CONTROL",
    "ALT",
    "PAUSE",
    "ESCAPE",
    "SPACE",
    "PAGE_UP",
    "PAGE_DOWN",
    "END",
    "HOME",
    "LEFT",
    "UP",
    "RIGHT",
    "DOWN",
    "INSERT",
    "DELETE",
    "SEMICOLON",
    "EQUALS",
    "NUMPAD0",
    "NUMPAD1",
    "NUMPAD2",
    "NUMPAD3",
    "NUMPAD4",
    "NUMPAD5",
    "NUMPAD6",
    "NUMPAD7",
    "NUMPAD8",
    "NUMPAD9",
    "MULTIPLY",
    "ADD",
    "SEPARATOR",
    "SUBTRACT",
    "DECIMAL",
    "DIVIDE",
    "F1" ,
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
    "META",
    "COMMAND",
]

# selenium params
BROWSER_FIREFOX             = "Firefox"
BROWSER_IE                  = "Internet Explorer"
BROWSER_CHROME              = "Chrome"
BROWSER_OPERA               = "Opera"
BROWSER_EDGE                = "Edge"

BROWSER_DRIVER_GECKO        = "Gecko"

BROWSER_BY_NAME                 = "BY NAME"
BROWSER_BY_TAG_NAME             = "BY TAG NAME"
BROWSER_BY_CLASS_NAME           = "BY CLASS NAME"
BROWSER_BY_ID                   = "BY ID"
BROWSER_BY_XPATH                = "BY XPATH"
BROWSER_BY_LINK_TEXT            = "BY LINK TEXT"
BROWSER_BY_PARTIAL_LINK_TEXT    = "BY PARTIAL LINK TEXT"
BROWSER_BY_CSS_SELECTOR         = "BY CSS SELECTOR"

EMPTY_VALUE = ''

INDEX_TEXT = 0
INDEX_CACHE = 1
INDEX_ALIAS = 2
       
LIST_TYPES = ["TEXT", "CACHE", "ALIAS"]

class ValidatorUpper(QValidator):
    """
    Validator upper
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
        self.TIMEOUT_BROWSER_ACTION = Settings.instance().readValue( key = 'TestGenerator/timeout-selenium-action' )

        self.timeoutBrLine = QLineEdit()
        self.timeoutBrLine.setText(str(self.TIMEOUT_BROWSER_ACTION))
        validator = QDoubleValidator(self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.timeoutBrLine.setValidator(validator)
        self.timeoutBrLine.installEventFilter(self)

        self.agentBrNameLine = QLineEdit("AGENT_GUI_BROWSER")

        self.agentsBrList = QComboBox()
        self.agentsBrList.setMinimumWidth(300)
        
        optBrLayoutGroup = QGridLayout()
        optBrLayoutGroup.addWidget(QLabel( self.tr("Max time to run action:") ), 1, 0)
        optBrLayoutGroup.addWidget(self.timeoutBrLine, 1, 1)
        
        optBrLayoutGroup.addWidget(QLabel( self.tr("Agent Key Name:") ), 3, 0)
        optBrLayoutGroup.addWidget(self.agentBrNameLine, 3, 1)

        optBrLayoutGroup.addWidget(QLabel( self.tr("Agent:") ), 4, 0)
        optBrLayoutGroup.addWidget(self.agentsBrList, 4, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(optBrLayoutGroup)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Browser Options"))

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

  
class WSelenium(QWidget, Logger.ClassLogger):
    """
    Selenium widget
    """
    # action, description, text, misc, textmore, cache, alias
    AddStep = pyqtSignal(str, str, str, str, str, dict)
    UpdateStep = pyqtSignal(str, str, str, str, str, dict)   
    CancelEdit = pyqtSignal()
    def __init__(self, parent):
        """
        Contructor
        """
        QWidget.__init__(self)

        self.tagList = {}
        self.idList = {}
        self.classList = {}
        self.nameList = {}
        self.linkList = {}
        self.cssList = {}  
        
        self.createActions()
        self.createWidgets()
        self.createToolbar()
        self.createConnections()
        
    def createActions(self):
        """
        Create qt actions
        """
        self.addBrowserAction = QPushButton(QIcon(":/add_black.png"), '&Add Action', self)
        self.addBrowserAction.setMinimumHeight(40)
        self.addBrowserAction.setMaximumWidth(150)
        
        self.cancelBrowserAction = QtHelper.createAction(self, "&Cancel", self.cancelStep, 
                                            icon=None, tip = 'Cancel update')
        self.cancelBrowserAction.setEnabled(False)

        self.optionsAction = QtHelper.createAction(self, "&", self.openOptions, 
                                            icon=QIcon(":/recorder-web-small.png"), tip = 'Browser options')
        
    def createWidgets(self):
        """
        Create widgets
        """
        self.optionsDialog  = OptionsDialog(self)
        
        self.validatorUpper = ValidatorUpper(self)
        self.validatorAll = ValidatorAll(self)
        self.validatorInt = QIntValidator(self)

        self.actionsBrComboBox = QComboBox(self)
        self.actionsBrComboBox.setMinimumHeight(40)
        for i in xrange(len(GuiSteps.ACTION_BROWSER_DESCR)):
            if not len( GuiSteps.ACTION_BROWSER_DESCR[i] ):
                self.actionsBrComboBox.insertSeparator(i+1)
            else:
                el = GuiSteps.ACTION_BROWSER_DESCR[i].keys()
                self.actionsBrComboBox.addItem( list(el)[0] )

        self.descriptionBrLine = QLineEdit(self)
        self.descriptionBrLine.hide()
        
        self.labelActionBrDescr = QLabel( )
        self.labelActionBrDescr.hide()
        self.labelActionBrDescr.setText( "%s\n" % GuiSteps.ACTION_BROWSER_DESCR[0][GuiSteps.BROWSER_OPEN])
        self.labelActionBrDescr.setWordWrap(True)
        
        actionsLayout = QHBoxLayout()
        actionsLayout.addWidget(self.actionsBrComboBox)

        actionBrLayoutGroup = QGridLayout()
        actionBrLayoutGroup.addLayout(actionsLayout, 0, 1)

        self.createWidgetOpenBrowser()
        self.createWidgetTextTo()
        self.createWidgetGetText()
        self.createWidgetTextToGlobal()
        self.createWidgetBrowserBy()
        
        self.valueBrTextLine = QLineEdit(self)
        self.valueBrTextLine.setMinimumWidth(400)
        self.valueBrTextLine.hide()

        # set layout
        self.actionBrLayoutGroup2 = QGridLayout()
        self.actionBrLayoutGroup2.addWidget( self.brByGroup , 0, 0 )
        self.actionBrLayoutGroup2.addWidget( self.openBrGroup , 0, 0 )
        self.actionBrLayoutGroup2.addWidget( self.valueBrTextLine, 0, 0 )
        self.actionBrLayoutGroup2.addWidget( self.textToGlobalBrGroup, 0, 0 )

        
        
        actionBrLayoutGroup3 = QGridLayout()
        actionBrLayoutGroup3.addWidget(self.textBrGroup, 0, 0)
        actionBrLayoutGroup3.addWidget(self.textToBrGroup, 0, 0)

        ###################### browser action #########################

        
        font = QFont()
        font.setBold(True)
        
        labelAct = QLabel( self.tr("Action: ") )
        labelAct.setFont( font) 
        
        self.arrowLabel = QLabel("")
        self.arrowLabel.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))
        
        self.arrowLabel2 = QLabel("")
        self.arrowLabel2.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))
        self.arrowLabel2.hide()

        self.arrowLabel4 = QLabel("")
        self.arrowLabel4.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))

        layoutBrowser = QHBoxLayout()
        layoutBrowser.addWidget( labelAct )
        layoutBrowser.addLayout(actionBrLayoutGroup)
        
        layoutBrowser.addWidget( self.arrowLabel )
        layoutBrowser.addLayout( self.actionBrLayoutGroup2 )
        
        layoutBrowser.addWidget( self.arrowLabel2 )
        layoutBrowser.addLayout(actionBrLayoutGroup3)

        layoutBrowser.addWidget( self.arrowLabel4 )
        layoutBrowser.addWidget(self.addBrowserAction)
        layoutBrowser.addStretch(1)
        self.setLayout(layoutBrowser)
      
    def openOptions(self):
        """
        Open options
        """
        if self.optionsDialog.exec_() == QDialog.Accepted:
            pass

    def createWidgetOpenBrowser(self):
        """
        Create open browser widget
        """
        self.openBrGroup = QGroupBox()
        openBrLayout = QGridLayout()

        self.browserComboBox = QComboBox(self)
        self.browserComboBox.addItem(BROWSER_FIREFOX)
        self.browserComboBox.addItem(BROWSER_IE)
        self.browserComboBox.addItem(BROWSER_CHROME)
        self.browserComboBox.addItem(BROWSER_OPERA)
        self.browserComboBox.addItem(BROWSER_EDGE)

        self.valueTextOpenBrowserLine = QLineEdit(self)
        self.valueTextOpenBrowserLine.setMinimumWidth(400)
        self.valueTextOpenCombo = QComboBox(self)
        self.valueTextOpenCombo.addItems( LIST_TYPES )

        self.sessionNameLine = QLineEdit(self)
        self.sessionNameLine.setText("default") 
        
        openBrLayout.addWidget(QLabel( self.tr("URL") ), 0, 0)
        openBrLayout.addWidget(self.valueTextOpenCombo, 0, 1)
        openBrLayout.addWidget(self.valueTextOpenBrowserLine, 0, 2)
        
        openBrLayout.addWidget(QLabel( self.tr("Browser") ), 1, 0)
        openBrLayout.addWidget(self.browserComboBox, 1, 1)

        openBrLayout.addWidget(QLabel( self.tr("Session name") ), 2, 0)
        openBrLayout.addWidget(self.sessionNameLine, 2, 2)
        
        self.openBrGroup.setLayout(openBrLayout)

    def createWidgetTextToGlobal(self):
        """
        Create text widget
        """
        self.valueTextCacheGlobalBrowserLine = QLineEdit(self)
        self.valueTextCacheGlobalBrowserLine.setMinimumWidth(400)
        self.valueTextCacheGlobalCombo = QComboBox(self)
        self.valueTextCacheGlobalCombo.addItems( ["CACHE"] )

        self.textToGlobalBrGroup = QGroupBox(self.tr(""))
        textToGlobalBrlayout = QGridLayout()
        textToGlobalBrlayout.addWidget( QLabel( self.tr("Save text in:") ) , 0,0)
        textToGlobalBrlayout.addWidget( self.valueTextCacheGlobalCombo , 0, 1)
        textToGlobalBrlayout.addWidget( self.valueTextCacheGlobalBrowserLine , 0, 2)
        self.textToGlobalBrGroup.setLayout(textToGlobalBrlayout)
        self.textToGlobalBrGroup.hide()
        
    def createWidgetBrowserBy(self):
        """
        Create browser by widget
        """
        self.brByGroup = QGroupBox()
        brByLayout = QGridLayout()
        self.browserByComboBox = QComboBox(self)
        self.browserByComboBox.addItem(BROWSER_BY_NAME)
        self.browserByComboBox.addItem(BROWSER_BY_TAG_NAME)
        self.browserByComboBox.addItem(BROWSER_BY_CLASS_NAME)
        self.browserByComboBox.addItem(BROWSER_BY_ID)
        self.browserByComboBox.addItem(BROWSER_BY_XPATH)
        self.browserByComboBox.addItem(BROWSER_BY_LINK_TEXT)
        self.browserByComboBox.addItem(BROWSER_BY_PARTIAL_LINK_TEXT)
        self.browserByComboBox.addItem(BROWSER_BY_CSS_SELECTOR)
        self.browserByComboBox.setMinimumWidth(250)
        
        self.valueBrowserLine = QComboBox(self)
        self.valueBrowserLine.setEditable(True)
        self.valueBrowserLine.setMinimumWidth(250)

        self.valueKeyBrowserLine = QComboBox(self)
        self.valueKeyBrowserLine.addItems(KEYS_BROWSER)
        self.valueKeyBrowserLine.hide()
        
        self.valueBrowserByCombo = QComboBox(self)
        self.valueBrowserByCombo.addItems( LIST_TYPES )
        
        brByLayout2 = QHBoxLayout()
        brByLayout2.addWidget( self.valueBrowserByCombo )
        brByLayout2.addWidget( self.valueBrowserLine )
        
        # get text element for open browser
        brByLayout.addWidget(QLabel( self.tr("Search Element") ), 0, 0)
        brByLayout.addWidget(self.browserByComboBox, 0, 1)
        brByLayout.addWidget(QLabel( self.tr("Where localor is") ), 1, 0)
        brByLayout.addLayout( brByLayout2, 1, 1 )
        brByLayout.addWidget(self.valueKeyBrowserLine, 2, 1)
  
        self.repeartLabel = QLabel( self.tr("Repeat") )
        self.repeartLabel.hide()
        self.repeartShortcut = QLineEdit( "0", self)
        self.repeartShortcut.setValidator(self.validatorInt)
        self.repeartShortcut.hide()

        brByLayout.addWidget(self.repeartLabel, 3, 0)
        brByLayout.addWidget(self.repeartShortcut, 3, 1)
            
        self.brByGroup.setLayout(brByLayout)
        self.brByGroup.hide() # hide by default

    def createWidgetTextTo(self):
        """
        Create text widget
        """
        self.valueTextCacheBrowserLine = QLineEdit(self)
        self.valueTextCacheBrowserLine.setMinimumWidth(250)
        self.valueTextCacheCombo = QComboBox(self)
        self.valueTextCacheCombo.addItems( ["CACHE"] )

        self.textToBrGroup = QGroupBox(self.tr(""))
        
        textToBrlayout = QGridLayout()
        textToBrlayout.addWidget( QLabel( self.tr("Save text in:") ) , 0, 0)
        textToBrlayout.addWidget( self.valueTextCacheCombo , 0, 1)
        textToBrlayout.addWidget( self.valueTextCacheBrowserLine , 0, 2)
        
        self.textToBrGroup.setLayout(textToBrlayout)
        self.textToBrGroup.hide()

    def createWidgetGetText(self):
        """
        Create text widget
        """

        self.valueTextBrowserLine = QLineEdit(self)
        self.valueTextBrowserLine.setMinimumWidth(250)
        self.valueTextBrowserCombo = QComboBox(self)
        self.valueTextBrowserCombo.addItems( LIST_TYPES )

        self.textBrGroup = QGroupBox(self.tr(""))
        
        mainTextBrlayout = QGridLayout()
        mainTextBrlayout.addWidget( QLabel( self.tr("Specify text:") ), 0, 0 )

        mainTextBrlayout.addWidget( self.valueTextBrowserCombo, 0, 1 )
        mainTextBrlayout.addWidget( self.valueTextBrowserLine, 0, 2 )

        self.textBrGroup.setLayout(mainTextBrlayout)
        self.textBrGroup.hide()
    
    def createToolbar(self):
        """
        Create toolbar
        """
        pass

    def createConnections(self):
        """
        Create connections
        """
        self.actionsBrComboBox.currentIndexChanged.connect(self.onActionBrowserChanged)
        self.browserByComboBox.currentIndexChanged.connect(self.onByBrowserChanged)

        self.addBrowserAction.clicked.connect(self.addStep)

        self.valueTextOpenCombo.currentIndexChanged.connect(self.onValueTextOpenTypeChanged)
        self.valueTextBrowserCombo.currentIndexChanged.connect(self.onValueTextBrowserTypeChanged)
        self.valueBrowserByCombo.currentIndexChanged.connect(self.onValueBrowserByChanged)
        
    def onValueTextBrowserTypeChanged(self):
        """
        On vaue browser changed
        """
        if self.valueTextBrowserCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.valueTextBrowserLine.setValidator(self.validatorAll)
            
        if self.valueTextBrowserCombo.currentText() == "ALIAS":
            self.valueTextBrowserLine.setText( self.valueTextBrowserLine.text().upper() )
            self.valueTextBrowserLine.setValidator(self.validatorUpper)
            
    def onValueTextOpenTypeChanged(self):
        """
        On value changed
        """
        if self.valueTextOpenCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.valueTextOpenBrowserLine.setValidator(self.validatorAll)
            
        if self.valueTextOpenCombo.currentText() == "ALIAS":
            self.valueTextOpenBrowserLine.setText( self.valueTextOpenBrowserLine.text().upper() )
            self.valueTextOpenBrowserLine.setValidator(self.validatorUpper)
            
    def onValueBrowserByChanged(self):
        """
        On value changed
        """
        if self.valueBrowserByCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.valueBrowserLine.setValidator(self.validatorAll)
            
        if self.valueBrowserByCombo.currentText() == "ALIAS":
            self.valueBrowserLine.setEditText( self.valueBrowserLine.currentText().upper() )
            self.valueBrowserLine.setValidator(self.validatorUpper)
            
    def pluginDataAccessor(self):
        """
        return data for plugin
        """
        return { "data": "" } 

    def onPluginImport(self, dataJson):
        """
        Received data from plugin
        """
        if "steps" not in dataJson:
            QMessageBox.warning(self, "Assistant Automation" , "bad import")
            return
            
        if not isinstance(dataJson['steps'], list):
            QMessageBox.warning(self, "Assistant Automation" , "bad import")
            return
            
        parameters =    { 
                            "from-el-cache": False, "from-el-alias": False,
                            "from-cache": False, "from-alias": False,
                            "to-cache": False, "to-alias": False
                        }
                        
        for stp in dataJson['steps']:
            if isinstance(stp, dict):
                if 'action-name' in stp and 'action-params' in stp and 'action-value' in stp and \
                        'action-description' in stp:
                    
                    actionName = str(stp['action-name'])
                    actionDescription = stp['action-description']
                    searchBy = ''; searchValue = '';
                    searchBy, searchValue = self.findSearchBy(stp['action-params'])
                    actionValue = stp['action-value']
   
                    if self.checkActionName(actionName=actionName):
                        if actionName == GuiSteps.BROWSER_OPEN:
                            self.AddStep.emit( GuiSteps.BROWSER_OPEN, unicode(actionDescription), actionValue, BROWSER_FIREFOX, EMPTY_VALUE, parameters )
                        else:
                            self.AddStep.emit( actionName, unicode(actionDescription), unicode(searchValue), 
                                                unicode(searchBy), actionValue, parameters )
                    else:
                        QMessageBox.warning(self, "Assistant Automation" , "action not yet supported: %s" % actionName)
 
    def checkActionName(self, actionName):
        """
        Check the name of action
        """
        found = False
        for act in GuiSteps.ACTION_BROWSER_DESCR:
            if actionName in act:
                found = True; break;
        return found

    def findSearchBy(self, actionParams):
        """
        Find search by
        """
        searchBy = BROWSER_BY_ID
        seachValue = ''
        if "=" in actionParams:
            seachValue = actionParams.split("=")[1]

        if actionParams.startswith("id="):
            searchBy = BROWSER_BY_ID
        if actionParams.startswith("xpath="):
            searchBy = BROWSER_BY_XPATH
        if actionParams.startswith("//"):
            searchBy = BROWSER_BY_XPATH
            seachValue = actionParams
        if actionParams.startswith("link="):
            searchBy = BROWSER_BY_LINK_TEXT
        if actionParams.startswith("css="):
            searchBy = BROWSER_BY_CSS_SELECTOR
        if actionParams.startswith("name="):
            searchBy = BROWSER_BY_NAME
        if actionParams.startswith("class="):
            searchBy = BROWSER_BY_CLASS_NAME
        return  (searchBy, seachValue)                   

    def onActionBrowserChanged(self):
        """
        On action changed
        """
        descr = 'No description available!'
        i = 0
        for el in GuiSteps.ACTION_BROWSER_DESCR:
            if isinstance(el, dict):
                if self.actionsBrComboBox.currentText() in el:
                    descr = GuiSteps.ACTION_BROWSER_DESCR[i][self.actionsBrComboBox.currentText()]
                    break
            i += 1
        self.labelActionBrDescr.setText( "%s\n" % descr )

        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_OPEN ]:
            
            self.brByGroup.hide()
            self.openBrGroup.show()
            self.textBrGroup.hide()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.hide()
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_GET_TEXT_ELEMENT ]:
            self.brByGroup.show()
            self.openBrGroup.hide()
            self.textBrGroup.hide()
            self.textToBrGroup.show()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
   
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()

            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_CLICK_ELEMENT, GuiSteps.BROWSER_HOVER_ELEMENT, GuiSteps.BROWSER_WAIT_ELEMENT,
                                                       GuiSteps.BROWSER_WAIT_CLICK_ELEMENT,GuiSteps.BROWSER_SWITCH_TO_FRAME,
                                                       GuiSteps.BROWSER_CLEAR_TEXT_ELEMENT, GuiSteps.BROWSER_DOUBLE_CLICK_ELEMENT,
                                                       GuiSteps.BROWSER_WAIT_VISIBLE_ELEMENT, GuiSteps.BROWSER_WAIT_VISIBLE_CLICK_ELEMENT,
                                                       GuiSteps.BROWSER_WAIT_NOT_VISIBLE_ELEMENT  ]:
            self.brByGroup.show()
            self.openBrGroup.hide()
            self.textBrGroup.hide()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.hide()
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_TYPE_TEXT, GuiSteps.BROWSER_FIND_TEXT_ELEMENT,
                                                       GuiSteps.BROWSER_SELECT_TEXT, GuiSteps.BROWSER_SELECT_VALUE,
                                                       GuiSteps.BROWSER_EXECUTE_JS ]:
            self.brByGroup.show()
            self.openBrGroup.hide()
            self.textBrGroup.show()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_FIND_TEXT_TITLE, GuiSteps.BROWSER_FIND_TEXT_GET_URL, 
                                                        GuiSteps.BROWSER_FIND_TEXT_GET_SOURCE, GuiSteps.BROWSER_SWITCH_TO_WINDOW,
                                                        GuiSteps.BROWSER_SWITCH_TO_SESSION ]:
            self.brByGroup.hide()
            self.openBrGroup.hide()
            self.textBrGroup.show()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.hide()
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_TYPE_KEY ]:
            self.brByGroup.show()
            self.openBrGroup.hide()
            self.textBrGroup.hide()
            self.valueKeyBrowserLine.show()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.show()
            self.repeartLabel.show()
            
            self.arrowLabel.show()
            self.arrowLabel2.hide()
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_CLOSE, GuiSteps.BROWSER_MAXIMIZE, GuiSteps.BROWSER_REFRESH,
                                                        GuiSteps.BROWSER_GO_BACK, GuiSteps.BROWSER_GO_FORWARD,GuiSteps.BROWSER_ACCEPT_ALERT, 
                                                        GuiSteps.BROWSER_DISMISS_ALERT, GuiSteps.BROWSER_CLOSE_WINDOW, 
                                                        GuiSteps.BROWSER_SWITCH_NEXT_WINDOW, GuiSteps.BROWSER_SWITCH_MAIN_WINDOW ]:
            self.brByGroup.hide() 
            self.openBrGroup.hide()
            self.textBrGroup.hide()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.hide()
            
        elif self.actionsBrComboBox.currentText() in [  GuiSteps.BROWSER_GET_TITLE, GuiSteps.BROWSER_GET_URL, GuiSteps.BROWSER_GET_SOURCE,
                                                        GuiSteps.BROWSER_GET_TEXT_ALERT]:
            self.brByGroup.hide()
            self.openBrGroup.hide()
            self.textBrGroup.hide()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.show()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.hide()
            
        else:
            self.brByGroup.hide()

            self.openBrGroup.show()
            self.openBrGroup.setEnabled(False)
            self.textBrGroup.hide()
            self.valueKeyBrowserLine.hide()
            self.valueBrTextLine.hide()
            self.textToBrGroup.hide()
            self.textToGlobalBrGroup.hide()
            self.repeartShortcut.hide()
            self.repeartLabel.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.hide()
            
    def onUpdateTagsHtml(self, tagList, idList, classList, nameList, linkList, cssList):
        """
        On update tags html
        """
        self.tagList = tagList
        self.idList = idList
        self.classList = classList
        self.nameList = nameList
        self.linkList = linkList
        self.cssList = cssList
        self.onByBrowserChanged(self.browserByComboBox.currentIndex())
        
    def onByBrowserChanged(self, index):
        """
        On browser changed
        """
        # save current text before to clear
        current = self.valueBrowserLine.currentText()

        # clear on each change
        self.valueBrowserLine.clear()


        if index == 0: # by name
            self.valueBrowserLine.addItems( [""] + list(self.nameList.keys()) )
            
        if index == 1: # by tag name
            self.valueBrowserLine.addItems( [""] + list(self.tagList.keys()) )

        if index == 2: # by class name
            self.valueBrowserLine.addItems( [""] + list(self.classList.keys()) )

        if index == 3: # by id
            self.valueBrowserLine.addItems( [""] + list(self.idList.keys()) )

        if index == 5 or index == 6: # by text link
            self.valueBrowserLine.addItems( [""] + list(self.linkList.keys()) )
        
        if index == 7: # by css selector
            self.valueBrowserLine.addItems( [""] + list(self.cssList.keys()) )
            
        # set the previous value 
        self.valueBrowserLine.setEditText ( current )
        
    def addStep(self):
        """
        Add step
        """
        action = self.actionsBrComboBox.currentText()
        descr = self.descriptionBrLine.text()
        descr = unicode(descr).replace('"', '')
        
        signal = self.AddStep
        if self.cancelBrowserAction.isEnabled():
            signal = self.UpdateStep
            
        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_OPEN ]:
            fromCache = False
            if self.valueTextOpenCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.valueTextOpenCombo.currentText() == "ALIAS": fromAlias = True

            url = self.valueTextOpenBrowserLine.text()
            if not len(url):
                QMessageBox.warning(self, "Assistant Automation" , "Please to specific a value!")
            else:
                if not unicode(url).startswith("http") and not fromCache and not fromAlias:
                    QMessageBox.warning(self, "Assistant Automation" , "Please to start the url with http(s)://!")
                else:   
                    browser = self.browserComboBox.currentText()
                    
                    sessionName = self.sessionNameLine.text()
                    
                    parameters =    { 
                                        "from-el-cache": False, "from-el-alias": False,
                                        "from-cache": fromCache, "from-alias": fromAlias,
                                        "to-cache": False, "to-alias": False,
                                        "session-name": sessionName, "use-gecko": True,
                                    }
                    signal.emit(str(action), unicode(descr), unicode(url), unicode(browser), EMPTY_VALUE, parameters )

        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_WAIT_ELEMENT, GuiSteps.BROWSER_HOVER_ELEMENT,
                                                        GuiSteps.BROWSER_CLICK_ELEMENT,  GuiSteps.BROWSER_WAIT_CLICK_ELEMENT,
                                                        GuiSteps.BROWSER_SWITCH_TO_FRAME, GuiSteps.BROWSER_CLEAR_TEXT_ELEMENT,
                                                        GuiSteps.BROWSER_DOUBLE_CLICK_ELEMENT, GuiSteps.BROWSER_WAIT_NOT_VISIBLE_ELEMENT, 
                                                        GuiSteps.BROWSER_WAIT_VISIBLE_ELEMENT, GuiSteps.BROWSER_WAIT_VISIBLE_CLICK_ELEMENT ]:
            searchBy = self.browserByComboBox.currentText()
            searchValue = self.valueBrowserLine.currentText()
            
            fromCache = False
            if self.valueBrowserByCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.valueBrowserByCombo.currentText() == "ALIAS": fromAlias = True
            
            if not len(searchValue):
                QMessageBox.warning(self, "Assistant Automation" , "Please to set a value!")
            else:
                    
                parameters =    { 
                                    "from-el-cache": fromCache, "from-el-alias": fromAlias,
                                    "from-cache": False, "from-alias": False,
                                    "to-cache": False, "to-alias": False
                                }
                signal.emit(str(action), unicode(descr), unicode(searchValue), unicode(searchBy), EMPTY_VALUE, parameters )

        elif self.actionsBrComboBox.currentText() in [  GuiSteps.BROWSER_GET_TEXT_ELEMENT ]:
            searchBy = self.browserByComboBox.currentText()
            searchValue = self.valueBrowserLine.currentText()
            
            fromCache = False
            if self.valueBrowserByCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.valueBrowserByCombo.currentText() == "ALIAS": fromAlias = True
            
            if not len(searchValue):
                QMessageBox.warning(self, "Assistant Automation" , "Please to set a value!")
            else:
                # save to cache ?
                textMoreStr = ''

                toCache = True
                textMoreStr = self.valueTextCacheBrowserLine.text()

                parameters =    { 
                                    "from-el-cache": fromCache, "from-el-alias": fromAlias,
                                    "from-cache": False, "from-alias": False,
                                    "to-cache": toCache, "to-alias": False
                                }
                signal.emit(str(action), unicode(descr), unicode(searchValue), unicode(searchBy), textMoreStr, parameters )

        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_GET_URL, GuiSteps.BROWSER_GET_SOURCE, GuiSteps.BROWSER_GET_TEXT_ALERT,
                                                       GuiSteps.BROWSER_GET_TITLE ]:
            # read text from cache or not ?
            textMore = ''
            toCache = True
            textMore = self.valueTextCacheGlobalBrowserLine.text()
                
            if toCache and not len(textMore):
                QMessageBox.warning(self, "Assistant Automation" , "Please to set a key destination name for the cache!")
                return
                    
            parameters =    { 
                                "from-el-cache": False, "from-el-alias": False,
                                "from-cache": False, "from-alias": False,
                                "to-cache": toCache, "to-alias": False
                            }
            signal.emit(str(action), unicode(descr), EMPTY_VALUE, EMPTY_VALUE, textMore, parameters )
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_TYPE_TEXT, GuiSteps.BROWSER_FIND_TEXT_ELEMENT,
                                                        GuiSteps.BROWSER_SELECT_TEXT, GuiSteps.BROWSER_SELECT_VALUE,
                                                        GuiSteps.BROWSER_EXECUTE_JS ]:
            searchBy = self.browserByComboBox.currentText()
            searchValue = self.valueBrowserLine.currentText()
            if not len(searchValue):
                QMessageBox.warning(self, "Assistant Automation" , "Please to set a value!")
            else:
                textValue = self.valueTextBrowserLine.text()
                    
                # read text from cache or not ?
                fromCache = False
                if self.valueTextBrowserCombo.currentText() == "CACHE": fromCache = True
                fromAlias = False
                if self.valueTextBrowserCombo.currentText() == "ALIAS": fromAlias = True

                if fromCache and not len(textValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a key destination name for the cache!")
                    return
                elif fromAlias and not len(textValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a alias name!")
                    return
                elif not len(textValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a text!")
                    return
            
                fromELCache = False
                if self.valueBrowserByCombo.currentText() == "CACHE": fromELCache = True
                fromELAlias = False
                if self.valueBrowserByCombo.currentText() == "ALIAS": fromELAlias = True
            
                parameters =    { 
                                    "from-el-cache": fromELCache, "from-el-alias": fromELAlias,
                                    "from-cache": fromCache, "from-alias": fromAlias,
                                    "to-cache": False, "to-alias": False
                                }
                signal.emit(str(action), unicode(descr), unicode(searchValue), unicode(searchBy), 
                                unicode(textValue), parameters )
                                
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_FIND_TEXT_TITLE, GuiSteps.BROWSER_FIND_TEXT_GET_URL,
                                                       GuiSteps.BROWSER_FIND_TEXT_GET_SOURCE, GuiSteps.BROWSER_SWITCH_TO_WINDOW,
                                                       GuiSteps.BROWSER_SWITCH_TO_SESSION ]:
            textValue = self.valueTextBrowserLine.text()
            if not len(textValue):
                QMessageBox.warning(self, "Assistant Automation" , "Please to set a value!")
            else:   
                    
                # read text from cache or not ?
                fromCache = False
                if self.valueTextBrowserCombo.currentText() == "CACHE": fromCache = True
                fromAlias = False
                if self.valueTextBrowserCombo.currentText() == "ALIAS": fromAlias = True

                if fromCache and not len(textValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a key destination name for the cache!")
                    return
                elif fromAlias and not len(textValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a alias name!")
                    return
                elif not len(textValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a text!")
                    return
                    
                parameters =    { 
                                    "from-el-cache": False, "from-el-alias": False,
                                    "from-cache": fromCache, "from-alias": fromAlias,
                                    "to-cache": False, "to-alias": False
                                }
                signal.emit(str(action), unicode(descr), EMPTY_VALUE, EMPTY_VALUE,  unicode(textValue), parameters )
            
        elif self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_TYPE_KEY ]:
            searchBy = self.browserByComboBox.currentText()
            searchValue = self.valueBrowserLine.currentText()
            if not len(searchValue):
                QMessageBox.warning(self, "Assistant Automation" , "Please to set a value!")
            else:
                keyValue = self.valueKeyBrowserLine.currentText()
                repeatValue = self.repeartShortcut.text()
                if not len(repeatValue):
                    QMessageBox.warning(self, "Assistant Automation" , "Please to set a repeat value!")
                else:
                
                    fromELCache = False
                    if self.valueBrowserByCombo.currentText() == "CACHE": fromELCache = True
                    fromELAlias = False
                    if self.valueBrowserByCombo.currentText() == "ALIAS": fromELAlias = True
            
                    parameters =    { 
                                        "from-el-cache": fromELCache, "from-el-alias": fromELAlias,
                                        "from-cache": False, "from-alias": False,
                                        "to-cache": False, "to-alias": False
                                    }
                    signal.emit(str(action), unicode(descr), unicode(searchValue), unicode(searchBy), 
                                    unicode("%s;%s" % (keyValue, repeatValue)), parameters )

        else:
                    
            parameters =    { 
                                "from-el-cache": False, "from-el-alias": False,
                                "from-cache": False, "from-alias": False,
                                "to-cache": False, "to-alias": False
                            }
            signal.emit(str(action), unicode(descr), EMPTY_VALUE, EMPTY_VALUE, EMPTY_VALUE, parameters )
            
    def cancelStep(self):
        """
        Cancel step
        """
        self.addBrowserAction.setText( "&Add" )
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addBrowserAction.setFont(buttonFont)
        
        self.cancelBrowserAction.setEnabled(False)
        
        self.CancelEdit.emit()
    
    def finalizeUpdate(self):
        """
        Finalise step update
        """
        self.addBrowserAction.setText( "&Add Action"  )
        
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addBrowserAction.setFont(buttonFont)
        self.cancelBrowserAction.setEnabled(False)

    def setTimeout(self, timeout):
        """
        Set the timeout
        """
        self.optionsDialog.timeoutBrLine.setText(timeout)
        
    def getTimeout(self):
        """
        Return the timeout
        """
        return self.optionsDialog.timeoutBrLine.text()
        
    def getAgentName(self):
        """
        Return the agent name
        """
        return self.optionsDialog.agentBrNameLine.text()
        
    def getAgentList(self):
        """
        Return the list of agent
        """
        return self.optionsDialog.agentsBrList
     
    def editStep(self, stepData):
        """
        Edit a step
        """
        # change button text           
        self.addBrowserAction.setText( "&Update" )
        buttonFont = QFont()
        buttonFont.setBold(True)
        self.addBrowserAction.setFont(buttonFont)
        
        self.cancelBrowserAction.setEnabled(True)
        
        # set the current value for actions combo
        for i in xrange(self.actionsBrComboBox.count()):
            item_text = self.actionsBrComboBox.itemText(i)
            if unicode(stepData["action"]) == unicode(item_text):
                self.actionsBrComboBox.setCurrentIndex(i)
                break
                
        # and then refresh options
        self.onActionBrowserChanged()
        
        # finally fill all fields
        self.descriptionBrLine.setText( stepData["description"] )
        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_OPEN ]:
            # if "from-alias" not in stepData: # for backward compatibility
                # stepData["from-alias"] = False 
                
            if stepData["parameters"]["from-cache"]:
                self.valueTextOpenCombo.setCurrentIndex(INDEX_CACHE)
                self.valueTextOpenBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-alias"]:
                self.valueTextOpenCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueTextOpenBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueTextOpenCombo.setCurrentIndex(INDEX_TEXT)
                self.valueTextOpenBrowserLine.setValidator(self.validatorAll)
                
            self.valueTextOpenBrowserLine.setText( stepData["text"] )
            
            if "session-name" in stepData["parameters"]:
                self.sessionNameLine.setText( stepData["parameters"]["session-name"] )
            else:
                self.sessionNameLine.setText( "default" )
                
            for i in xrange(self.browserComboBox.count()):
                item_text = self.browserComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.browserComboBox.setCurrentIndex(i)
                    break
                    
        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_WAIT_ELEMENT, GuiSteps.BROWSER_HOVER_ELEMENT,
                                                     GuiSteps.BROWSER_CLICK_ELEMENT, GuiSteps.BROWSER_GET_TEXT_ELEMENT,
                                                     GuiSteps.BROWSER_WAIT_CLICK_ELEMENT, GuiSteps.BROWSER_SWITCH_TO_FRAME,
                                                     GuiSteps.BROWSER_CLEAR_TEXT_ELEMENT, GuiSteps.BROWSER_DOUBLE_CLICK_ELEMENT,
                                                     GuiSteps.BROWSER_WAIT_VISIBLE_ELEMENT, GuiSteps.BROWSER_WAIT_VISIBLE_CLICK_ELEMENT,
                                                     GuiSteps.BROWSER_WAIT_NOT_VISIBLE_ELEMENT  ]:
                    
            if stepData["parameters"]["from-el-cache"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_CACHE)
                self.valueBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-el-alias"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_TEXT)
                self.valueBrowserLine.setValidator(self.validatorAll)
                
            self.valueBrowserLine.setEditText ( stepData["text"] )
            for i in xrange(self.browserByComboBox.count()):
                item_text = self.browserByComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.browserByComboBox.setCurrentIndex(i)
                    break

        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_GET_TEXT_ELEMENT ]:
                    
            if stepData["parameters"]["from-el-cache"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_CACHE)
                self.valueBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-el-alias"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_TEXT)
                self.valueBrowserLine.setValidator(self.validatorAll)
                
            self.valueBrowserLine.setEditText ( stepData["text"])
            for i in xrange(self.browserByComboBox.count()):
                item_text = self.browserByComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.browserByComboBox.setCurrentIndex(i)
                    break

            self.valueTextCacheBrowserLine.setText ( stepData["text-more"])

        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_GET_URL, GuiSteps.BROWSER_GET_SOURCE, GuiSteps.BROWSER_GET_TEXT_ALERT,
                                                     GuiSteps.BROWSER_GET_TITLE ]:
            self.valueTextCacheGlobalBrowserLine.setText( stepData["text-more"] )

        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_TYPE_TEXT, GuiSteps.BROWSER_FIND_TEXT_ELEMENT,
                                                     GuiSteps.BROWSER_SELECT_TEXT, GuiSteps.BROWSER_SELECT_VALUE,
                                                     GuiSteps.BROWSER_EXECUTE_JS ]:   
            if stepData["parameters"]["from-cache"]:
                self.valueTextBrowserCombo.setCurrentIndex(INDEX_CACHE)
                self.valueTextBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-alias"]:
                self.valueTextBrowserCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueTextBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueTextBrowserCombo.setCurrentIndex(INDEX_TEXT)
                self.valueTextBrowserLine.setValidator(self.validatorAll)
                    
            if stepData["parameters"]["from-el-cache"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_CACHE)
                self.valueBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-el-alias"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_TEXT)
                self.valueBrowserLine.setValidator(self.validatorAll)
                
            self.valueBrowserLine.setEditText ( stepData["text"])
            self.valueTextBrowserLine.setText( stepData["text-more"] )
            for i in xrange(self.browserByComboBox.count()):
                item_text = self.browserByComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.browserByComboBox.setCurrentIndex(i)
                    break
 
        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_FIND_TEXT_TITLE, GuiSteps.BROWSER_FIND_TEXT_GET_URL,
                                                     GuiSteps.BROWSER_FIND_TEXT_GET_SOURCE, GuiSteps.BROWSER_SWITCH_TO_WINDOW,
                                                     GuiSteps.BROWSER_SWITCH_TO_SESSION ]:   

            if stepData["parameters"]["from-cache"]:
                self.valueTextBrowserCombo.setCurrentIndex(INDEX_CACHE)
                self.valueTextBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-alias"]:
                self.valueTextBrowserCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueTextBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueTextBrowserCombo.setCurrentIndex(INDEX_TEXT)
                self.valueTextBrowserLine.setValidator(self.validatorAll)
                
            self.valueTextBrowserLine.setText( stepData["text-more"] )
            for i in xrange(self.browserByComboBox.count()):
                item_text = self.browserByComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.browserByComboBox.setCurrentIndex(i)
                    break

        if self.actionsBrComboBox.currentText() in [ GuiSteps.BROWSER_TYPE_KEY ]:
                    
            if stepData["parameters"]["from-el-cache"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_CACHE)
                self.valueBrowserLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-el-alias"]:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueBrowserLine.setValidator(self.validatorUpper) 
            else:
                self.valueBrowserByCombo.setCurrentIndex(INDEX_TEXT)
                self.valueBrowserLine.setValidator(self.validatorAll)
                
            self.valueBrowserLine.setEditText ( stepData["text"])

            for i in xrange(self.valueKeyBrowserLine.count()): # fix error, set the value properly
                item_text = self.valueKeyBrowserLine.itemText(i)
                if ";" in unicode(stepData["text-more"]):
                    keyStr, keyRepeat = unicode(stepData["text-more"]).split(";")
                else:
                    keyStr = unicode(stepData["text-more"])
                    keyRepeat = "0"
                if keyStr == unicode(item_text):
                    self.valueKeyBrowserLine.setCurrentIndex(i)
                    self.repeartShortcut.setText(keyRepeat)
                    break

            for i in xrange(self.browserByComboBox.count()):
                item_text = self.browserByComboBox.itemText(i)
                if unicode(stepData["misc"]) == unicode(item_text):
                    self.browserByComboBox.setCurrentIndex(i)
                    break
