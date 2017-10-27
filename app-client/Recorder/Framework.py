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
Framework assistant module
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
                                QRadioButton, QButtonGroup, QSlider, QSizePolicy, QTabWidget, 
                                QCheckBox, QSplitter, QMessageBox, QPushButton, QDialogButtonBox)
    from PyQt5.QtCore import (QFile, QIODevice, QTextStream, Qt, QSize, QUrl, QByteArray, QBuffer,
                                pyqtSignal)
        
from Libs import QtHelper, Logger
import Settings

try:
    import GuiSteps
except ImportError: # python3 support
    from . import GuiSteps
    
EMPTY_VALUE = ''

INDEX_TEXT = 0
INDEX_CACHE = 1
INDEX_ALIAS = 2
       
LIST_TYPES = ["TEXT", "CACHE", "ALIAS"]

class ValidatorUpper(QValidator):
    """
    Validator
    """
    def validate(self, string, pos):
        """
        validate
        """
        return QValidator.Acceptable, string.upper(), pos
        
class ValidatorAll(QValidator):
    """
    Validator
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
                
        self.TIMEOUT_ACTION = Settings.instance().readValue( key = 'TestGenerator/timeout-framework-action' )

        self.timeoutLine = QLineEdit()
        self.timeoutLine.setText(str(self.TIMEOUT_ACTION))
        validatorTimeout = QDoubleValidator(self)
        validatorTimeout.setNotation(QDoubleValidator.StandardNotation)
        self.timeoutLine.setValidator(validatorTimeout)
        self.timeoutLine.installEventFilter(self)

        optionLayout = QHBoxLayout()
        optionLayout.addWidget(QLabel( self.tr("Max time to run action (in seconds):") ) )
        optionLayout.addWidget(self.timeoutLine)

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

        self.setWindowTitle(self.tr("Framework Options"))

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        
class WFramework(QWidget, Logger.ClassLogger):
    """
    Framework widget
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
        self.addAction.setMaximumWidth(200)
        
        self.cancelAction = QtHelper.createAction(self, "&Cancel", self.cancelStep, 
                                            icon=QIcon(":/undo.png"), tip = 'Cancel update')
        self.cancelAction.setEnabled(False)
        
        self.optionsAction = QtHelper.createAction(self, "&", self.openOptions, 
                                            icon=QIcon(":/recorder-basic-small.png"), tip = 'Framework options')
        
    def openOptions(self):
        """
        Open options dialog
        """
        if self.optionsDialog.exec_() == QDialog.Accepted:
            pass
              
    def createWidgets(self):
        """
        Create all qt widgets
        """
        self.optionsDialog  = OptionsDialog(self)
        
        self.validatorUpper = ValidatorUpper(self)
        self.validatorAll = ValidatorAll(self)
        self.validatorInt = QIntValidator(self)

        font = QFont()
        font.setBold(True)

        self.actionsComboBox = QComboBox(self)
        self.actionsComboBox.setMinimumHeight(40)
        for i in xrange(len(GuiSteps.ACTION_FRAMEWORK_DESCR)):
            if not len( GuiSteps.ACTION_FRAMEWORK_DESCR[i] ):
                self.actionsComboBox.insertSeparator(i+1)
            else:
                el = GuiSteps.ACTION_FRAMEWORK_DESCR[i].keys()
                self.actionsComboBox.addItem( list(el)[0] )
            
        self.labelActionDescr = QLabel(self)
        self.labelActionDescr.setText( "%s\n" % GuiSteps.ACTION_FRAMEWORK_DESCR[0][GuiSteps.FRAMEWORK_INFO])
        self.labelActionDescr.setWordWrap(True)
        self.labelActionDescr.hide()
        
        self.descriptionLine = QLineEdit(self)
        self.descriptionLine.hide()

        actionLayout2 = QGridLayout()

        self.createWidgetGetText()        
        self.createWidgetGetWait()
        self.createWidgetCacheSet()
        self.createWidgetCheckString()
        self.createWidgetGetAsk()

        actionLayout2.addWidget( self.setCacheGroup , 0, 0)
        actionLayout2.addWidget( self.getCheckGroup , 1, 0)
        actionLayout2.addWidget( self.getTextGroup , 2, 0)
        actionLayout2.addWidget( self.getWaitGroup , 3, 0)
        actionLayout2.addWidget( self.getAskGroup , 4, 0)

        labelAct = QLabel( self.tr("Action: ") )
        labelAct.setFont( font) 
        
        self.arrowLabel = QLabel("")
        self.arrowLabel.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))

        self.arrowLabel2 = QLabel("")
        self.arrowLabel2.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))

        layoutFinal = QHBoxLayout()
        layoutFinal.addWidget( labelAct )
        layoutFinal.addWidget(self.actionsComboBox)
        layoutFinal.addWidget( self.arrowLabel )
        layoutFinal.addLayout( actionLayout2 )
        layoutFinal.addWidget( self.arrowLabel2 )
        layoutFinal.addWidget(self.addAction)

        layoutFinal.addStretch(1)
        self.setLayout(layoutFinal)
        
    def createToolbar(self):
        """
        Create toolbar
        """
        pass

    def createWidgetCheckString(self):
        """
        Create widget to check string
        """
        self.getCheckGroup = QGroupBox(self.tr(""))

        # check in ?
        self.checkInTextLine = QLineEdit(self)
        self.checkInTextLine.setMinimumWidth(300)
        self.checkInTextCombo = QComboBox(self)
        self.checkInTextCombo.addItems( [ "CACHE" ] )

        # operator   
        self.checkComboBox = QComboBox(self)
        self.checkComboBox.addItems( [ GuiSteps.OP_CONTAINS, GuiSteps.OP_NOTCONTAINS, GuiSteps.OP_REGEXP, GuiSteps.OP_NOTREGEXP,
                                       GuiSteps.OP_STARTSWITH, GuiSteps.OP_NOTSTARTSWITH, GuiSteps.OP_ENDSWITH, 
                                       GuiSteps.OP_NOTENDSWITH ] )
        
        # check what ?
        self.checkOutTextLine = QLineEdit(self)
        self.checkOutTextLine.setMinimumWidth(300)
        self.checkOutTextCombo = QComboBox(self)
        self.checkOutTextCombo.addItems( LIST_TYPES )

        # final layout
        mainChecklayout = QGridLayout()
        mainChecklayout.addWidget(  QLabel( self.tr("Checking from:") ), 0, 0 )
        mainChecklayout.addWidget(  self.checkInTextCombo, 0, 1 )
        mainChecklayout.addWidget(  self.checkInTextLine, 0, 2 )
        mainChecklayout.addWidget(  QLabel( self.tr("If:") ), 1, 0 )
        mainChecklayout.addWidget(  self.checkComboBox, 1, 1 )
        mainChecklayout.addWidget(  QLabel( self.tr("The Value:") ), 2, 0  )
        mainChecklayout.addWidget(  self.checkOutTextCombo, 2, 1 )
        mainChecklayout.addWidget(  self.checkOutTextLine, 2, 2 )

        self.getCheckGroup.setLayout(mainChecklayout)
        self.getCheckGroup.hide()
        
    def createWidgetGetText(self):
        """
        Create text widget 
        """
        self.getTextGroup = QGroupBox(self.tr(""))

        self.basicTextLine = QLineEdit(self)
        self.basicTextLine.setMinimumWidth(300)
        self.basicTextCombo = QComboBox(self)
        self.basicTextCombo.addItems( LIST_TYPES )

        mainTextlayout = QGridLayout()
        mainTextlayout.addWidget(  QLabel( self.tr("Value:") ), 0, 0 )
        mainTextlayout.addWidget(  self.basicTextCombo, 0, 1 )
        mainTextlayout.addWidget(  self.basicTextLine, 0, 2 )

        self.getTextGroup.setLayout(mainTextlayout)
    
    def createWidgetGetAsk(self):
        """
        Create ask widget
        """
        # ask
        self.getAskGroup = QGroupBox(self.tr(""))

        self.askTextLine = QLineEdit(self)
        self.askTextLine.setMinimumWidth(300)
        self.askTextCombo = QComboBox(self)
        self.askTextCombo.addItems( LIST_TYPES )

        self.askTextCacheLine = QLineEdit(self)
        self.askTextCacheLine.setMinimumWidth(300)
        self.askTextCacheCombo = QComboBox(self)
        self.askTextCacheCombo.addItems( [ "CACHE" ] )
        
        mainAsklayout = QGridLayout()
        mainAsklayout.addWidget(  QLabel( self.tr("Ask to user:") ), 0, 0 )
        mainAsklayout.addWidget(  self.askTextCombo, 0, 1 )
        mainAsklayout.addWidget(  self.askTextLine, 0, 2 )
        mainAsklayout.addWidget(  QLabel( self.tr("And save response in:") ), 1, 0 )
        mainAsklayout.addWidget(  self.askTextCacheCombo, 1, 1 )
        mainAsklayout.addWidget(  self.askTextCacheLine, 1, 2 )
        
        self.getAskGroup.setLayout(mainAsklayout)
        self.getAskGroup.hide()
        
    def createWidgetGetWait(self):
        """
        Create wait text widget
        """
        self.getWaitGroup = QGroupBox(self.tr(""))

        self.valueWaitLine = QLineEdit(self)
        self.valueWaitLine.setMinimumWidth(300)
        self.valueWaitLine.setValidator(self.validatorInt)
        self.valueWaitCombo = QComboBox(self)
        self.valueWaitCombo.addItems( LIST_TYPES )

        mainTextlayout = QGridLayout()
        mainTextlayout.addWidget(  QLabel( self.tr("Value (in seconds):") ), 0, 0 )
        mainTextlayout.addWidget(  self.valueWaitCombo, 0, 1 )
        mainTextlayout.addWidget(  self.valueWaitLine, 0, 2 )

        self.getWaitGroup.setLayout(mainTextlayout)
        self.getWaitGroup.hide()
        
    def createWidgetCacheSet(self):
        """
        Create cache widget
        """
        self.setCacheGroup = QGroupBox(self.tr(""))
        
        setCacheLayout = QGridLayout()
        
        self.cacheKeyName = QLineEdit(self)
        self.cacheKeyName.setMinimumWidth(300)
        
        setCacheLayout.addWidget( QLabel( self.tr("Key name:") ) , 0, 1)
        setCacheLayout.addWidget( self.cacheKeyName , 0, 2)

        self.setCacheGroup.setLayout(setCacheLayout)
        self.setCacheGroup.hide()
        
    def createConnections(self):
        """
        Createa qt connections
        """
        self.actionsComboBox.currentIndexChanged.connect(self.onActionChanged)
        self.addAction.clicked.connect(self.addStep)
        
        self.basicTextCombo.currentIndexChanged.connect(self.onBasicTextTypeChanged)
        self.valueWaitCombo.currentIndexChanged.connect(self.onValueWaitTypeChanged)
        self.checkOutTextCombo.currentIndexChanged.connect(self.onCheckOutTextTypeChanged)
        self.askTextCombo.currentIndexChanged.connect(self.onAskTextTypeChanged)
        
    def onAskTextTypeChanged(self):
        """
        On ask type changed
        """
        if self.askTextCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.askTextLine.setValidator(self.validatorAll)
            
        if self.askTextCombo.currentText() == "ALIAS":
            self.askTextLine.setText( self.askTextLine.text().upper() )
            self.askTextLine.setValidator(self.validatorUpper)
            
    def onCheckOutTextTypeChanged(self):
        """
        On check out type changed
        """
        if self.checkOutTextCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.checkOutTextLine.setValidator(self.validatorAll)
            
        if self.checkOutTextCombo.currentText() == "ALIAS":
            self.checkOutTextLine.setText( self.checkOutTextLine.text().upper() )
            self.checkOutTextLine.setValidator(self.validatorUpper)
            
    def onValueWaitTypeChanged(self):
        """
        On value wait changed
        """
        if self.valueWaitCombo.currentText() in [ "TEXT" ]:
            self.valueWaitLine.setText( "0" )
            self.valueWaitLine.setValidator(self.validatorInt)
            
        if self.valueWaitCombo.currentText() in [ "CACHE" ]:
            self.valueWaitLine.setValidator(self.validatorAll)
            
        if self.valueWaitCombo.currentText() == "ALIAS":
            self.valueWaitLine.setText( self.valueWaitLine.text().upper() )
            self.valueWaitLine.setValidator(self.validatorUpper)
            
    def onBasicTextTypeChanged(self):
        """
        On basic text changed
        """
        if self.basicTextCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.basicTextLine.setValidator(self.validatorAll)

        if self.basicTextCombo.currentText() == "ALIAS":
            self.basicTextLine.setText( self.basicTextLine.text().upper() )
            self.basicTextLine.setValidator(self.validatorUpper)
            
    def pluginDataAccessor(self):
        """
        Return data for plugins
        """
        return { "data": "" } 
        
    def onPluginImport(self, dataJson):
        """
        On call from plugin
        """
        pass 
    
    def onRadioAskChanged(self, button):
        """
        On radio ask changed
        """
        if button.text() == 'From alias parameter':
            self.askTextLine.setText( self.askTextLine.text().upper() )
            self.askTextLine.setValidator(self.validAskUpper)
        else:
            self.askTextLine.setValidator(self.validAskAll)

    def onActionChanged(self):
        """
        On action changed
        """
        descr = 'No description available!'
        i = 0
        for el in GuiSteps.ACTION_FRAMEWORK_DESCR:
            if isinstance(el, dict):
                if self.actionsComboBox.currentText() in el:
                    descr = GuiSteps.ACTION_FRAMEWORK_DESCR[i][self.actionsComboBox.currentText()]
                    break
            i += 1
        self.labelActionDescr.setText( "%s\n" % descr )
        
        if self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_INFO, GuiSteps.FRAMEWORK_WARNING ]:
            self.getTextGroup.show()
            self.getWaitGroup.hide()
            self.setCacheGroup.hide()
            self.getCheckGroup.hide()
            self.getAskGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_WAIT ]:
            self.getWaitGroup.show()
            self.getTextGroup.hide()
            self.setCacheGroup.hide()
            self.getCheckGroup.hide()
            self.getAskGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_CACHE_SET ]:
            self.getTextGroup.show()
            self.getWaitGroup.hide()
            self.setCacheGroup.show()
            self.getCheckGroup.hide()
            self.getAskGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_CHECK_STRING ]:
            self.getCheckGroup.show()
            self.getTextGroup.hide()
            self.getWaitGroup.hide()
            self.setCacheGroup.hide()
            self.getAskGroup.hide()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_INTERACT ]:
            self.getCheckGroup.hide()
            self.getTextGroup.hide()
            self.getWaitGroup.hide()
            self.setCacheGroup.hide()
            self.getAskGroup.show()
            
            self.arrowLabel.show()
            self.arrowLabel2.show()
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_USERCODE, GuiSteps.FRAMEWORK_CACHE_RESET ]:
            self.getCheckGroup.hide()
            self.getTextGroup.hide()
            self.getWaitGroup.hide()
            self.setCacheGroup.hide()
            self.getAskGroup.hide()
            
            self.arrowLabel.hide()
            self.arrowLabel2.show()
            
        else:
            self.getTextGroup.hide()
            self.getWaitGroup.hide()
            self.setCacheGroup.hide()
            self.getCheckGroup.hide()
            self.getAskGroup.hide()
            
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

        if action in [ GuiSteps.FRAMEWORK_INFO, GuiSteps.FRAMEWORK_WARNING ]:
            fromCache = False
            if self.basicTextCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.basicTextCombo.currentText() == "ALIAS": fromAlias = True
            
            newText = self.basicTextLine.text()
            if not len(newText):
                QMessageBox.warning(self, "Assistant" , "Please to set a value!")
            else:
                parameters = { 'text': newText, 'from-cache': fromCache, 'from-alias': fromAlias }
                signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
        
        elif action in [ GuiSteps.FRAMEWORK_INTERACT ]:
            # read text from cache, alias or not ?
            fromCache = False
            if self.askTextCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.askTextCombo.currentText() == "ALIAS": fromAlias = True
            
            askText = self.askTextLine.text()
            if not len(askText):
                QMessageBox.warning(self, "Assistant" , "Please to set question to ask!")
            else:
                saveAskText = self.askTextCacheLine.text()
                if not len(saveAskText):
                    QMessageBox.warning(self, "Assistant" , "Please to set key destination cache!")
                else:
                    parameters = { 'key': saveAskText, 'value': askText, 'from-cache': fromCache, 'from-alias': fromAlias }
                    signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                        
        elif action in [ GuiSteps.FRAMEWORK_CHECK_STRING ]:
            fromCache = False
            if self.checkOutTextCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.checkOutTextCombo.currentText() == "ALIAS": fromAlias = True
            
            inText = self.checkInTextLine.text()
            if not len(inText):
                QMessageBox.warning(self, "Assistant" , "Please to set a cache key value!")
            else:
                outText = self.checkOutTextLine.text()
                if not len(outText):
                    QMessageBox.warning(self, "Assistant" , "Please to set a value!")
                else:
                    op = self.checkComboBox.currentText()
                    parameters = { 'key': inText, 'value': outText, 'from-cache': fromCache,
                                    'from-alias': fromAlias, "operator": op }
                    signal.emit( str(action), unicode(descr), EMPTY_VALUE, parameters )
                    
        elif action in [ GuiSteps.FRAMEWORK_WAIT ]:
            fromCache = False
            if self.valueWaitCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.valueWaitCombo.currentText() == "ALIAS": fromAlias = True
            
            miscStr = self.valueWaitLine.text()
            if not len(miscStr):
                QMessageBox.warning(self, "Assistant" , "Please to set a value!")
            else:
                parameters = {'from-cache': fromCache, 'from-alias': fromAlias}
                signal.emit( str(action), unicode(descr), miscStr, parameters )
                
        elif action in [ GuiSteps.FRAMEWORK_CACHE_SET ]:
            fromCache = False
            if self.basicTextCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.basicTextCombo.currentText() == "ALIAS": fromAlias = True
            
            newText = self.basicTextLine.text()
            if not len(newText):
                QMessageBox.warning(self, "Assistant" , "Please to set a text value!")
            else:
                miscStr = self.cacheKeyName.text()
                if not len(miscStr):
                    QMessageBox.warning(self, "Assistant" , "Please to set a key name!")
                else:
                    parameters = { 'key': miscStr, 'value': newText, 'from-cache': fromCache, 'from-alias': fromAlias }
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
        Finalize update 
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
                
        if self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_INFO, GuiSteps.FRAMEWORK_WARNING ] :
            self.basicTextLine.setText ( stepData["parameters"]["text"] )
            if stepData["parameters"]["from-cache"]:
                self.basicTextLine.setValidator(self.validatorAll)
                self.basicTextCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias"]:
                self.basicTextLine.setValidator(self.validatorUpper)
                self.basicTextCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.basicTextLine.setValidator(self.validatorAll)
                self.basicTextCombo.setCurrentIndex(INDEX_TEXT)

        if self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_WAIT ]:
            self.valueWaitLine.setText ( stepData["misc"] )
            if stepData["parameters"]["from-cache"]:
                self.valueWaitLine.setValidator(self.validatorAll)
                self.valueWaitCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias"]:
                self.valueWaitLine.setValidator(self.validatorUpper)
                self.valueWaitCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.valueWaitLine.setValidator(self.validatorInt)
                self.valueWaitCombo.setCurrentIndex(INDEX_TEXT)
 
        if self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_CACHE_SET ]:
            self.basicTextLine.setText ( stepData["parameters"]["value"] )
            if stepData["parameters"]["from-cache"]:
                self.basicTextLine.setValidator(self.validatorAll)
                self.basicTextCombo.setCurrentIndex(INDEX_CACHE)
                
            elif stepData["parameters"]["from-alias"]:
                self.basicTextLine.setValidator(self.validatorUpper)
                self.basicTextCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.basicTextLine.setValidator(self.validatorAll)
                self.basicTextCombo.setCurrentIndex(INDEX_TEXT)
                
            self.cacheKeyName.setText( stepData["parameters"]["key"] ) 
            
        if self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_CHECK_STRING ]:

            self.checkOutTextLine.setText ( stepData["parameters"]["value"] )
                        
            if stepData["parameters"]["from-cache"]:
                self.checkOutTextLine.setValidator(self.validatorAll)
                self.checkOutTextCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias"]:
                self.checkOutTextLine.setValidator(self.validatorUpper)
                self.checkOutTextCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.checkOutTextLine.setValidator(self.validatorAll)
                self.checkOutTextCombo.setCurrentIndex(INDEX_TEXT)

            self.checkInTextLine.setText ( stepData["parameters"]["key"] )
            
            for i in xrange(self.checkComboBox.count()):
                item_text = self.checkComboBox.itemText(i)
                if unicode(stepData["parameters"]["operator"]) == unicode(item_text):
                    self.checkComboBox.setCurrentIndex(i)
                    break

        if self.actionsComboBox.currentText() in [ GuiSteps.FRAMEWORK_INTERACT ]:
            self.askTextLine.setText ( stepData["parameters"]["value"] )
            if stepData["parameters"]["from-cache"]:
                self.askTextLine.setValidator(self.validatorAll)
                self.askTextCombo.setCurrentIndex(INDEX_CACHE)
            elif stepData["parameters"]["from-alias"]:
                self.askTextLine.setValidator(self.validatorUpper)
                self.askTextCombo.setCurrentIndex(INDEX_ALIAS)
            else:
                self.askTextLine.setValidator(self.validatorAll)
                self.askTextCombo.setCurrentIndex(INDEX_TEXT)

            self.askTextCacheLine.setText ( stepData["parameters"]["key"] )
            
    def getTimeout(self):
        """
        Return timeout
        """
        return self.optionsDialog.timeoutLine.text() 
        
    def setTimeout(self, timeout):
        """
        Set the timeout
        """
        return self.optionsDialog.timeoutLine.setText(timeout) 