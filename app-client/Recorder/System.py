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
System module (ssh)
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
                            QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, QFont,
                            QCheckBox, QSplitter, QMessageBox, QDesktopWidget, QValidator, QPushButton,
                            QTextEdit, QDialogButtonBox)
    from PyQt4.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QKeySequence, QPixmap, QCursor, QIcon, QDoubleValidator, 
                                QIntValidator, QValidator, QFont)
    from PyQt5.QtWidgets import (QWidget, QDialog, QApplication, QToolBar, QGroupBox, QLineEdit, 
                                QComboBox, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
                                QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                                QCheckBox, QSplitter, QMessageBox, QPushButton, QTextEdit, QDialogButtonBox)
    from PyQt5.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal)
        
from Libs import QtHelper, Logger
import Settings

try:
    import GuiSteps
except ImportError: # python3 support
    from . import GuiSteps
    
EMPTY_VALUE = ''

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
    Validate all
    """
    def validate(self, string, pos):
        """
        validate
        """
        return QValidator.Acceptable, string, pos
       
INDEX_TEXT = 0
INDEX_CACHE = 1
INDEX_ALIAS = 2
       
LIST_TYPES = ["TEXT", "CACHE", "ALIAS"]

KEY_CTRLC = 'CTRLC'
KEY_ENTER = 'ENTER'
        
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
                
        self.TIMEOUT_ACTION = Settings.instance().readValue( key = 'TestGenerator/timeout-system-action' )

        self.timeoutLine = QLineEdit()
        self.timeoutLine.setText(str(self.TIMEOUT_ACTION))
        validatorTimeout = QDoubleValidator(self)
        validatorTimeout.setNotation(QDoubleValidator.StandardNotation)
        self.timeoutLine.setValidator(validatorTimeout)
        self.timeoutLine.installEventFilter(self)
        
        self.agentNameLine = QLineEdit("AGENT_SYSTEM")
        
        self.agentsList = QComboBox()
        self.agentsList.setMinimumWidth(300)
        
        optionLayout = QGridLayout()
        optionLayout.addWidget(QLabel( self.tr("Max time to run action:") ), 1, 0)
        optionLayout.addWidget(self.timeoutLine, 1, 1)
        
        optionLayout.addWidget(QLabel( self.tr("Agent Key Name:") ), 2, 0)
        optionLayout.addWidget(self.agentNameLine, 2, 1)

        optionLayout.addWidget(QLabel( self.tr("Agent:") ), 3, 0)
        optionLayout.addWidget(self.agentsList, 3, 1)


        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(optionLayout)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("System Options"))

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

class WSystem(QWidget, Logger.ClassLogger):
    """
    System widget
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
        self.addAction = QPushButton(QIcon(":/add_black.png"), '&Add Action', self)
        self.addAction.setMinimumHeight(40)
        self.addAction.setMaximumWidth(150)
        self.cancelAction = QtHelper.createAction(self, "&Cancel", self.cancelStep, 
                                            icon=QIcon(":/undo.png"), tip = 'Cancel update')
        self.cancelAction.setEnabled(False)
        
        self.optionsAction = QtHelper.createAction(self, "&", self.openOptions, 
                                            icon=QIcon(":/system-small.png"), tip = 'System options')
        
    def openOptions(self):
        """
        Open options dialog
        """
        if self.optionsDialog.exec_() == QDialog.Accepted:
            pass
             
    def createWidgets(self):
        """
        Create qt widgets
        """
        self.optionsDialog  = OptionsDialog(self)
        
        self.validatorUpper = ValidatorUpper(self)
        self.validatorAll = ValidatorAll(self)
        self.validatorInt = QIntValidator(self)

        self.actionsComboBox = QComboBox(self)
        self.actionsComboBox.setMinimumHeight(40)
        for i in xrange(len(GuiSteps.ACTION_SYSTEM_DESCR)):
            if not len( GuiSteps.ACTION_SYSTEM_DESCR[i] ):
                self.actionsComboBox.insertSeparator(i+1)
            else:
                el = GuiSteps.ACTION_SYSTEM_DESCR[i].keys()
                self.actionsComboBox.addItem( list(el)[0] )
            
        self.labelActionDescr = QLabel(self)
        self.labelActionDescr.hide()
        self.descriptionLine = QLineEdit(self)
        self.descriptionLine.setPlaceholderText("Step purpose description")
        self.descriptionLine.hide()
        
        actionsLayout = QHBoxLayout()
        actionsLayout.addWidget(self.actionsComboBox)
        
        actionLayout1 = QGridLayout()
        actionLayout1.addLayout(actionsLayout, 0, 1)

        self.createWidgetSession()        
        self.createWidgetText()
        self.createWidgetShortcut()
        self.createWidgetScreen()
        
        actionLayout2 = QGridLayout()
        actionLayout2.addWidget( self.sessionGroup , 1, 0)
        actionLayout2.addWidget( self.textGroup , 1, 0)
        actionLayout2.addWidget( self.shortcutGroup , 1, 0)
        actionLayout2.addWidget( self.screenGroup , 1, 0)

        font = QFont()
        font.setBold(True)
        
        labelAct = QLabel( self.tr("Action: ") )
        labelAct.setFont( font) 
        
        self.arrowLabel = QLabel("")
        self.arrowLabel.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))
        
        self.arrowLabel2 = QLabel("")
        self.arrowLabel2.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))

        layoutFinal = QHBoxLayout()
        layoutFinal.addWidget( labelAct )
        layoutFinal.addLayout( actionLayout1 )
        layoutFinal.addWidget( self.arrowLabel )
        layoutFinal.addLayout( actionLayout2 )
        layoutFinal.addWidget( self.arrowLabel2 )
        layoutFinal.addWidget( self.addAction )
        
        layoutFinal.addStretch(1)
        self.setLayout(layoutFinal)
        
    def createToolbar(self):
        """
        Create toolbar
        """
        pass
        
    def createWidgetScreen(self):
        """
        Create screen widget
        """
        self.screenGroup = QGroupBox(self.tr(""))

        # text
        self.checkComboBox = QComboBox(self)
        self.checkComboBox.addItems( [ GuiSteps.OP_ANY, GuiSteps.OP_CONTAINS, GuiSteps.OP_NOTCONTAINS, GuiSteps.OP_REGEXP, GuiSteps.OP_NOTREGEXP,
                                       GuiSteps.OP_STARTSWITH, GuiSteps.OP_NOTSTARTSWITH, GuiSteps.OP_ENDSWITH, 
                                       GuiSteps.OP_NOTENDSWITH ] )
                                       
        self.screenLine = QLineEdit(self)
        self.screenLine.setMinimumWidth(300)
        self.screenLine.setEnabled(False)
        self.screenLine.hide()
        self.screenArea = QTextEdit(self)
        self.screenArea.setMinimumWidth(300)
        self.screenArea.setEnabled(False)
        
        self.screenCombo = QComboBox(self)
        self.screenCombo.addItems( LIST_TYPES )
        self.screenCombo.setEnabled(False)
        
        self.screenSaveCombo = QComboBox(self)
        self.screenSaveCombo.addItems( ["VARIABLE", "CACHE" ] )
        self.screenSaveLine = QLineEdit(self)
        self.screenSaveLine.setMinimumWidth(300)
        self.screenSaveLine.setEnabled(False)
        
        mainTextlayout = QGridLayout()
        mainTextlayout.addWidget(  QLabel( self.tr("Checking if the screen: ") ), 0, 0 )
        mainTextlayout.addWidget( self.checkComboBox, 0, 1 )
        mainTextlayout.addWidget(  QLabel( self.tr("The value:") ), 1, 0 )
        mainTextlayout.addWidget(  self.screenCombo, 1, 1 )
        mainTextlayout.addWidget(  self.screenLine, 2, 1 )
        mainTextlayout.addWidget(  self.screenArea, 2, 1 )
        mainTextlayout.addWidget(  QLabel( self.tr("And save the screen in:") ), 0, 2)
        mainTextlayout.addWidget(  self.screenSaveCombo, 1, 2 )
        mainTextlayout.addWidget(  self.screenSaveLine, 2, 2 )
        
        self.screenGroup.setLayout(mainTextlayout)
        self.screenGroup.hide()
        
    def createWidgetText(self):
        """
        Create text widget
        """
        self.textGroup = QGroupBox(self.tr(""))

        # text
        self.textLine = QLineEdit(self)
        self.textLine.setMinimumWidth(300)
        self.textCombo = QComboBox(self)
        self.textCombo.addItems( LIST_TYPES )

        mainTextlayout = QGridLayout()
        mainTextlayout.addWidget(  QLabel( self.tr("Send the value:") ), 0, 0 )
        mainTextlayout.addWidget(  self.textCombo, 0, 1 )
        mainTextlayout.addWidget(  self.textLine, 0, 2 )

        self.textGroup.setLayout(mainTextlayout)
        self.textGroup.hide()
        
    def createWidgetShortcut(self):
        """
        Create shortcut widget
        """
        self.shortcutGroup = QGroupBox(self.tr(""))

        # text
        self.shortcutComboBox = QComboBox()
        self.shortcutComboBox.addItems( [KEY_CTRLC, KEY_ENTER] )
        self.shortcutComboBox.setMinimumWidth(300)
        
        mainTextlayout = QGridLayout()
        mainTextlayout.addWidget(  QLabel( self.tr("Shortcut:") ), 0, 0 )
        mainTextlayout.addWidget(  self.shortcutComboBox, 0, 1 )

        self.shortcutGroup.setLayout(mainTextlayout)
        self.shortcutGroup.hide()
        
    def createWidgetSession(self):
        """
        Create session widget
        """
        self.sessionGroup = QGroupBox(self.tr(""))

        # login
        self.loginLine = QLineEdit(self)
        self.loginLine.setMinimumWidth(300)
        self.loginCombo = QComboBox(self)
        self.loginCombo.addItems( LIST_TYPES )


        # password
        self.pwdLine = QLineEdit(self)
        self.pwdLine.setMinimumWidth(300)
        self.pwdCombo = QComboBox(self)
        self.pwdCombo.addItems( LIST_TYPES )

        # ip
        self.ipLine = QLineEdit(self)
        self.ipLine.setMinimumWidth(300)
        self.ipCombo = QComboBox(self)
        self.ipCombo.addItems( LIST_TYPES )
        
        # port
        self.portLine = QLineEdit(self)
        self.portLine.setMinimumWidth(300)
        self.portLine.setText("22")
        self.portLine.setValidator(self.validatorInt)
        self.portCombo = QComboBox(self)
        self.portCombo.addItems( LIST_TYPES )

        # agent support
        self.useAgent = QCheckBox("Use with agent mode")
        
        mainTextlayout = QGridLayout()
        mainTextlayout.addWidget(  QLabel( self.tr("Host:") ), 0, 0 )
        mainTextlayout.addWidget(  self.ipCombo, 0, 1 )
        mainTextlayout.addWidget(  self.ipLine, 0, 2 )
        mainTextlayout.addWidget(  QLabel( self.tr("Port (optional):") ), 1, 0 )
        mainTextlayout.addWidget(  self.portCombo, 1, 1 )
        mainTextlayout.addWidget(  self.portLine, 1, 2 )
        mainTextlayout.addWidget(  QLabel( self.tr("Login:") ), 2, 0 )
        mainTextlayout.addWidget(  self.loginCombo, 2, 1 )
        mainTextlayout.addWidget(  self.loginLine, 2, 2 )
        mainTextlayout.addWidget(  QLabel( self.tr("Password:") ), 3, 0 )
        mainTextlayout.addWidget(  self.pwdCombo, 3, 1 )
        mainTextlayout.addWidget(  self.pwdLine, 3, 2 )

        mainTextlayout.addWidget(  self.useAgent, 4, 0 )

        
        self.sessionGroup.setLayout(mainTextlayout)
   
    def createConnections(self):
        """
        Create qt connections
        """
        self.actionsComboBox.currentIndexChanged.connect(self.onActionChanged)
        self.addAction.clicked.connect(self.addStep)
        
        self.ipCombo.currentIndexChanged.connect(self.onIpTypeChanged)
        self.portCombo.currentIndexChanged.connect(self.onPortTypeChanged)
        self.loginCombo.currentIndexChanged.connect(self.onLoginTypeChanged)
        self.pwdCombo.currentIndexChanged.connect(self.onPwdTypeChanged)
        
        self.textCombo.currentIndexChanged.connect(self.onTextTypeChanged)
        self.screenCombo.currentIndexChanged.connect(self.onScreenTypeChanged)
        self.checkComboBox.currentIndexChanged.connect(self.onScreenOperatorChanged)
        self.screenSaveCombo.currentIndexChanged.connect(self.onScreenSaveChanged)
        
    def pluginDataAccessor(self):
        """
        Return data to plugin
        """
        return { "data": "" } 
        
    def onPluginImport(self, dataJson):
        """
        Received data from plugins
        """
        if "steps" not in dataJson:
            QMessageBox.warning(self, "Assistant Automation" , "bad import")
            return
            
        if not isinstance(dataJson['steps'], list):
            QMessageBox.warning(self, "Assistant Automation" , "bad import")
            return
        
        if not( 'ip' in dataJson and 'login' in dataJson and 'password' in dataJson ):
            QMessageBox.warning(self, "Assistant Automation" , "bad import")
            return
            
        # emit open session
        parameters = { 
                       'dest-ip': dataJson['ip'], 'dest-port': 22, 
                       'login': dataJson['login'], 'password': dataJson['password'], 
                       
                       'from-cache-ip': False, 'from-alias-ip': False,
                       'from-cache-port': False, 'from-alias-port': False, 
                       'from-cache-login': False, 'from-alias-login': False,
                       'from-cache-pwd': False, 'from-alias-pwd': False,
                       'agent-support': False
                    }
        self.AddStep.emit( GuiSteps.SYSTEM_SESSION, EMPTY_VALUE, EMPTY_VALUE, parameters )
        
        for stp in dataJson['steps']:
            if isinstance(stp, dict):
            
                # new in v16
                fromCache = False
                fromAlias = False
                if "type-value" in stp: 
                    if stp["type-value"].lower() == "cache": fromCache=True
                    if stp["type-value"].lower() == "alias": fromAlias=True
                # end of new
                
                if stp["action-name"] == "SEND":
                    parameters = {'text': stp["action-value"],  'from-cache': fromCache, 'from-alias': fromAlias }   
                    self.AddStep.emit( GuiSteps.SYSTEM_TEXT, EMPTY_VALUE, EMPTY_VALUE, parameters )
                elif stp["action-name"] == "EXPECT":
                    op = "Contains"
                    if stp["action-type"] == "REGEX":
                        op = "RegEx"  
                    parameters = {'value': stp["action-value"],  'from-cache': fromCache, 'from-alias': fromAlias, 'operator': op, 
                                    'to-cache': False, 'cache-key': '' }  
                    self.AddStep.emit( GuiSteps.SYSTEM_CHECK_SCREEN, EMPTY_VALUE, EMPTY_VALUE, parameters )
                else:
                    QMessageBox.warning(self, "Assistant Automation" , "action not yet supported: %s" % stp["action-name"])
                
        # close
        self.AddStep.emit( GuiSteps.SYSTEM_CLOSE, EMPTY_VALUE, EMPTY_VALUE, {} )
        
    def onScreenOperatorChanged(self):
        """
        On screen operator changed
        """
        if self.checkComboBox.currentText() == GuiSteps.OP_ANY:
            self.screenLine.setEnabled(False)
            self.screenArea.setEnabled(False)
            self.screenCombo.setEnabled(False)
        else:
            self.screenLine.setEnabled(True)
            self.screenArea.setEnabled(True)
            self.screenCombo.setEnabled(True)
            
    def onScreenSaveChanged(self):
        """
        On screen save changed
        """
        if self.screenSaveCombo.currentText() == "VARIABLE":
            self.screenSaveLine.setEnabled(False)
        else:
            self.screenSaveLine.setEnabled(True)
            
    def onScreenTypeChanged(self):
        """
        On screen type changed
        """
        if self.screenCombo.currentText() in [ "TEXT" ]:
            self.screenArea.show()
            self.screenLine.hide()
        else:
            self.screenLine.show()
            self.screenArea.hide()
            if self.screenCombo.currentText() in ["CACHE" ]:
                self.screenLine.setValidator(self.validatorAll)

            if self.screenCombo.currentText() == "ALIAS":
                self.screenLine.setText( self.screenLine.text().upper() )
                self.screenLine.setValidator(self.validatorUpper)
            
    def onTextTypeChanged(self):
        """
        On text type changed
        """
        if self.textCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.textLine.setValidator(self.validatorAll)

        if self.textCombo.currentText() == "ALIAS":
            self.textLine.setText( self.textLine.text().upper() )
            self.textLine.setValidator(self.validatorUpper)
            
    def onLoginTypeChanged(self):
        """
        On login type changed
        """
        if self.loginCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.loginLine.setValidator(self.validatorAll)

        if self.loginCombo.currentText() == "ALIAS":
            self.loginLine.setText( self.loginLine.text().upper() )
            self.loginLine.setValidator(self.validatorUpper)
            
    def onPwdTypeChanged(self):
        """
        On password type changed
        """
        if self.pwdCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.pwdLine.setValidator(self.validatorAll)

        if self.pwdCombo.currentText() == "ALIAS":
            self.pwdLine.setText( self.pwdLine.text().upper() )
            self.pwdLine.setValidator(self.validatorUpper)
    
    def onIpTypeChanged(self):
        """
        On ip type changed
        """
        if self.ipCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.ipLine.setValidator(self.validatorAll)

        if self.ipCombo.currentText() == "ALIAS":
            self.ipLine.setText( self.ipLine.text().upper() )
            self.ipLine.setValidator(self.validatorUpper)
    
    def onPortTypeChanged(self):
        """
        On port type changed
        """
        if self.portCombo.currentText() in [ "TEXT" ]:
            self.portLine.setText( "22" )
            self.portLine.setValidator(self.validatorInt)
            
        if self.portCombo.currentText() in [ "CACHE" ]:
            self.portLine.setValidator(self.validatorAll)

        if self.portCombo.currentText() == "ALIAS":
            self.portLine.setText( self.portLine.text().upper() )
            self.portLine.setValidator(self.validatorUpper)
            
    def onActionChanged(self):
        """
        On action changed
        """
        descr = 'No description available!'
        i = 0
        for el in GuiSteps.ACTION_SYSTEM_DESCR:
            if isinstance(el, dict):
                if self.actionsComboBox.currentText() in el:
                    descr = GuiSteps.ACTION_SYSTEM_DESCR[i][self.actionsComboBox.currentText()]
                    break
            i += 1
        self.labelActionDescr.setText( "%s\n" % descr )
        
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_SESSION ]:
            self.sessionGroup.show()
            self.textGroup.hide()
            self.shortcutGroup.hide()
            self.screenGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_CLOSE ]:
            self.sessionGroup.hide()
            self.textGroup.hide()
            self.shortcutGroup.hide()
            self.screenGroup.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_CLEAR_SCREEN ]:
            self.sessionGroup.hide()
            self.textGroup.hide()
            self.shortcutGroup.hide()
            self.screenGroup.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_TEXT ]:
            self.sessionGroup.hide()
            self.textGroup.show()
            self.shortcutGroup.hide()
            self.screenGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_SHORTCUT ]:
            self.sessionGroup.hide()
            self.textGroup.hide()
            self.shortcutGroup.show()
            self.screenGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_CHECK_SCREEN ]:
            self.sessionGroup.hide()
            self.textGroup.hide()
            self.shortcutGroup.hide()
            self.screenGroup.show()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        else:
            self.sessionGroup.hide()
            self.textGroup.hide()
            self.shortcutGroup.hide()
            self.screenGroup.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.hide()

    def addStep(self):
        """
        Add step
        """
        action = self.actionsComboBox.currentText()
        descr = self.descriptionLine.text()
        descr = unicode(descr).replace('"', '')
        
        signal = self.AddStep
        if self.cancelAction.isEnabled():
            signal = self.UpdateStep

        if action in [ GuiSteps.SYSTEM_SESSION ]:
            fromCacheIp = False
            if self.ipCombo.currentText() == "CACHE": fromCacheIp = True
            fromAliasIp = False
            if self.ipCombo.currentText() == "ALIAS": fromAliasIp = True

            fromCachePort = False
            if self.portCombo.currentText() == "CACHE": fromCachePort = True
            fromAliasPort  = False
            if self.portCombo.currentText() == "ALIAS": fromAliasPort = True
            
            fromCacheLogin = False
            if self.loginCombo.currentText() == "CACHE": fromCacheLogin = True
            fromAliasLogin = False
            if self.loginCombo.currentText() == "ALIAS": fromAliasLogin = True
            
            fromCachePwd = False
            if self.pwdCombo.currentText() == "CACHE": fromCachePwd = True
            fromAliasPwd = False
            if self.pwdCombo.currentText() == "ALIAS": fromAliasPwd = True
            
            newIp = self.ipLine.text()
            if not len(newIp):
                QMessageBox.warning(self, "Assistant" , "Please to provide a ip!")
                return
                
            newPort = self.portLine.text()
            if not len(newPort):
                QMessageBox.warning(self, "Assistant" , "Please to provide a port!")
                return
                
            newLogin = self.loginLine.text()
            if not len(newLogin):
                QMessageBox.warning(self, "Assistant" , "Please to provide a login!")
                return
            
            newPwd = self.pwdLine.text()
            agentSupport = "False"
            if self.useAgent.isChecked(): agentSupport = "True"
            
            parameters = { 
                           'dest-ip': newIp, 'dest-port': newPort, 'login': newLogin, 'password': newPwd, 
                           'from-cache-ip': fromCacheIp, 'from-alias-ip': fromAliasIp,
                           'from-cache-port': fromCachePort, 'from-alias-port': fromAliasPort, 
                           'from-cache-login': fromCacheLogin, 'from-alias-login': fromAliasLogin,
                           'from-cache-pwd': fromCachePwd, 'from-alias-pwd': fromAliasPwd,
                           'agent-support': agentSupport
                        }
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                
        elif action in [ GuiSteps.SYSTEM_CLOSE ]:
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, {} )
            
        elif action in [ GuiSteps.SYSTEM_CLEAR_SCREEN ]:
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, {} )
            
        elif action in [ GuiSteps.SYSTEM_TEXT ]:
            fromCache = False
            if self.textCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.textCombo.currentText() == "ALIAS": fromAlias = True

            newText = self.textLine.text()
            if not len(newText):
                QMessageBox.warning(self, "Assistant" , "Please to provide text!")
                return
            parameters = {'text': newText,  'from-cache': fromCache, 'from-alias': fromAlias }   
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
            
        elif action in [ GuiSteps.SYSTEM_SHORTCUT ]:
        
            newShortcut = self.shortcutComboBox.currentText()
            parameters = {'shortcut': newShortcut }   
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
            
        elif action in [ GuiSteps.SYSTEM_CHECK_SCREEN ]:
            op = self.checkComboBox.currentText()
            fromCache = False
            if self.screenCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.screenCombo.currentText() == "ALIAS": fromAlias = True

            toCache = False
            if self.screenSaveCombo.currentText() == "CACHE": toCache = True
            keyCache = self.screenSaveLine.text()
            
            newText = ""
            if op != GuiSteps.OP_ANY:
                if fromCache or fromAlias:
                    newText = self.screenLine.text()
                else:
                    newText = self.screenArea.toPlainText ()
                if not len(newText):
                    QMessageBox.warning(self, "Assistant" , "Please to provide value to search!")
                    return
                
            parameters = {'value': newText,  'from-cache': fromCache, 'from-alias': fromAlias, 'operator': op, 
                          'to-cache': toCache, 'cache-key': keyCache }  
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )

        else:
            signal.emit( str(action), unicode(descr), EMPTY_VALUE, {} )
            
    def cancelStep(self):
        """
        Cancel step
        """
        self.addAction.setText( "&Add" )
        
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addAction.setFont(buttonFont)
        self.cancelAction.setEnabled(False)
        
        self.CancelEdit.emit()
    
    def finalizeUpdate(self):
        """
        Finalize the update of the step
        """
        self.addAction.setText( "&Add Action" )
        
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addAction.setFont(buttonFont)
        self.cancelAction.setEnabled(False)

    def editStep(self, stepData):
        """
        Edit step
        """
        self.addAction.setText( "&Update" )
        buttonFont = QFont()
        buttonFont.setBold(True)
        self.addAction.setFont(buttonFont)
        
        self.cancelAction.setEnabled(True)
        
            
        # set the current value for actions combo
        for i in xrange(self.actionsComboBox.count()):
            item_text = self.actionsComboBox.itemText(i)
            if unicode(stepData["action"]) == unicode(item_text):
                self.actionsComboBox.setCurrentIndex(i)
                break
                
        # and then refresh options
        self.onActionChanged()
        
        # finally fill all fields
        self.descriptionLine.setText( stepData["description"] )
                
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_SESSION ] :
            self.ipLine.setText ( stepData["parameters"]["dest-ip"] )
            self.portLine.setText ( "%s" % stepData["parameters"]["dest-port"] )
            self.loginLine.setText ( stepData["parameters"]["login"] )
            self.pwdLine.setText ( stepData["parameters"]["password"] )
            
            if stepData["parameters"]["from-cache-ip"]:
                self.ipLine.setValidator(self.validatorAll)
                self.ipCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias-ip"]:
                self.ipLine.setValidator(self.validatorUpper)
                self.ipCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.ipLine.setValidator(self.validatorAll)
                self.ipCombo.setCurrentIndex(INDEX_TEXT)
                
            if stepData["parameters"]["from-cache-port"]:
                self.portLine.setValidator(self.validatorAll)
                self.portCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias-port"]:
                self.portLine.setValidator(self.validatorUpper)
                self.portCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.portLine.setValidator(self.validatorInt)
                self.portCombo.setCurrentIndex(INDEX_TEXT)
                
            if stepData["parameters"]["from-cache-login"]:
                self.loginLine.setValidator(self.validatorAll)
                self.loginCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias-login"]:
                self.loginLine.setValidator(self.validatorUpper)
                self.loginCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.loginLine.setValidator(self.validatorAll)
                self.loginCombo.setCurrentIndex(INDEX_TEXT)
                
            if stepData["parameters"]["from-cache-pwd"]:
                self.pwdLine.setValidator(self.validatorAll)
                self.pwdCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias-pwd"]:
                self.pwdLine.setValidator(self.validatorUpper)
                self.pwdCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.pwdLine.setValidator(self.validatorAll)
                self.pwdCombo.setCurrentIndex(INDEX_TEXT)
                
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_CLOSE ]:
            pass
            
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_CLEAR_SCREEN ]:
            pass
            
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_TEXT ]:
        
            if stepData["parameters"]["from-cache"]:
                self.textLine.setValidator(self.validatorAll)
                self.textCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias"]:
                self.textLine.setValidator(self.validatorUpper)
                self.textCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.textLine.setValidator(self.validatorAll)
                self.textCombo.setCurrentIndex(INDEX_TEXT)
                
            self.textLine.setText(stepData["parameters"]["text"])
            
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_SHORTCUT ]:

            for i in xrange(self.shortcutComboBox.count()):
                item_text = self.shortcutComboBox.itemText(i)
                if unicode(stepData["parameters"]["shortcut"]) == unicode(item_text):
                    self.shortcutComboBox.setCurrentIndex(i)
                    break
            
        if self.actionsComboBox.currentText() in [ GuiSteps.SYSTEM_CHECK_SCREEN ]:
                
            if stepData["parameters"]["from-cache"]:
                self.screenLine.setValidator(self.validatorAll)
                self.screenCombo.setCurrentIndex(INDEX_CACHE)
                self.screenLine.setText(stepData["parameters"]["value"])
            elif stepData["parameters"]["from-alias"]:
                self.screenLine.setValidator(self.validatorUpper)
                self.screenCombo.setCurrentIndex(INDEX_ALIAS)
                self.screenLine.setText(stepData["parameters"]["value"])
            else:
                self.screenCombo.setCurrentIndex(INDEX_TEXT)
                self.screenArea.setPlainText(stepData["parameters"]["value"])

            for i in xrange(self.checkComboBox.count()):
                item_text = self.checkComboBox.itemText(i)
                if unicode(stepData["parameters"]["operator"]) == unicode(item_text):
                    self.checkComboBox.setCurrentIndex(i)
                    break
                    
            if stepData["parameters"]["to-cache"]:
                self.screenSaveCombo.setCurrentIndex(1)
                self.screenSaveLine.setText(stepData["parameters"]["cache-key"])
            else:
                self.screenSaveCombo.setCurrentIndex(0)
                
    def getTimeout(self):
        """
        Return timeout value
        """
        return self.optionsDialog.timeoutLine.text() 
        
    def setTimeout(self, timeout):
        """
        Set the timeout
        """
        return self.optionsDialog.timeoutLine.setText(timeout) 
        
    def getAgentName(self):
        """
        Return the agent name
        """
        return self.optionsDialog.agentNameLine.text()
        
    def getAgentList(self):
        """
        Return the agent list
        """
        return self.optionsDialog.agentsList