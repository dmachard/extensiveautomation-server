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
                            QCheckBox, QSplitter, QMessageBox, QDesktopWidget, QValidator, QDialogButtonBox,
                            QPushButton)
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
import base64

try:
    import GuiSteps
except ImportError: # python3 support
    from . import GuiSteps
    
# sikuli params
KEY_MODIFIERS = [
    "None",
    "CTRL",
    "SHIFT",
    "ALT",
    "META",
    "CMD",
    "WIN"
]

KEYS = [
        "ENTER",
        "TAB",
        "ESC",
        "BACKSPACE",
        "DELETE",
        "INSERT",
        "SPACE",
        "",
        "F1",
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
        "",
        "NUM0",
        "NUM1",
        "NUM2",
        "NUM3",
        "NUM4",
        "NUM5",
        "NUM6",
        "NUM7",
        "NUM8",
        "NUM9",
        "",
        "ADD",
        "MINUS",
        "MULTIPLY",
        "DIVIDE",
        "",
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
]


KEY_LETTERS = [
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'O',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'X',
        'Y',
        'Z',
]

EMPTY_VALUE = ''
EMPTY_IMG = b''
       
INDEX_TEXT = 0
INDEX_CACHE = 1
INDEX_ALIAS = 2
       
LIST_TYPES = ["TEXT", "CACHE", "ALIAS"]

class ValidatorUpper(QValidator):
    """
    """
    def validate(self, string, pos):
        """
        """
        return QValidator.Acceptable, string.upper(), pos
        
class ValidatorAll(QValidator):
    """
    """
    def validate(self, string, pos):
        """
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
        self.TIMEOUT_ACTION = Settings.instance().readValue( key = 'TestGenerator/timeout-sikuli-action' )

        self.timeoutLine = QLineEdit()
        self.timeoutLine.setText(str(self.TIMEOUT_ACTION))
        validator = QDoubleValidator(self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.timeoutLine.setValidator(validator)
        self.timeoutLine.installEventFilter(self)

        self.agentKeyNameLine = QLineEdit("AGENT_GUI")

        self.agentsList = QComboBox()
        self.agentsList.setMinimumWidth(300)
        
        optionLayoutlGroup = QGridLayout()
        optionLayoutlGroup.addWidget(QLabel( self.tr("Max time to run action:") ), 1, 0)
        optionLayoutlGroup.addWidget(self.timeoutLine, 1, 1)

        optionLayoutlGroup.addWidget(QLabel( self.tr("Agent Key Name:") ), 3, 0)
        optionLayoutlGroup.addWidget(self.agentKeyNameLine, 3, 1)

        optionLayoutlGroup.addWidget(QLabel( self.tr("Agent:") ), 4, 0)
        optionLayoutlGroup.addWidget(self.agentsList, 4, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(optionLayoutlGroup)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Application Options"))

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

class WSikuliX(QWidget, Logger.ClassLogger):
    """
    """
    # action, description, image, text, misc, similar, cache, alias
    AddStep = pyqtSignal(str, str, bytes, str, str, str, bool, bool, dict) 
    UpdateStep = pyqtSignal(str, str, bytes, str, str, str, bool, bool, dict) 
    TakeSnapshot = pyqtSignal()
    TakeMousePosition = pyqtSignal()
    TakeMouseLocation = pyqtSignal()
    CancelEdit = pyqtSignal()
    def __init__(self, parent):
        """
        """
        QWidget.__init__(self)
        
        self.DEFAULT_SIMILAR_VALUE = Settings.instance().readValue( key = 'TestGenerator/default-similar-threshold' )

        self.createActions()
        self.createWidgets()
        self.createToolbar()
        self.createConnections()
        
    def createActions(self):
        """
        """
        self.takeSnapshotAction = QPushButton(QIcon(":/screenshot.png"), '&Capture Visual Pattern', self)
        self.takeDragSnapshotAction = QPushButton(QIcon(":/screenshot.png"), '&Capture Visual Pattern', self)
        self.takeMouseAction = QPushButton(QIcon(":/mouse-position.png"), '&Capture Mouse Position', self)
        self.takeDragMouseAction = QPushButton(QIcon(":/mouse-position.png"), '&Capture Mouse Position', self)
        self.takeLocationAction = QPushButton(QIcon(":/mouse-position.png"), '&Capture Location', self)

        self.addStepAction = QPushButton(QIcon(":/add_black.png"), '&Add Action', self)
        self.addStepAction.setMinimumHeight(40)
        self.addStepAction.setMaximumWidth(150)
        
        self.cancelStepAction = QtHelper.createAction(self, "&Cancel", self.cancelStep, 
                                            icon=None, tip = 'Cancel update')
        self.cancelStepAction.setEnabled(False)
        
        self.optionsAction = QtHelper.createAction(self, "&", self.openOptions, 
                                    icon=QIcon(":/recorder-app-small.png"), tip = 'Application options')
                                    
        
    def openOptions(self):
        """
        """
        if self.optionsDialog.exec_() == QDialog.Accepted:
            pass
             
    def createWidgets(self):
        """
        """
        self.optionsDialog  = OptionsDialog(self)
        
        self.validatorUpper = ValidatorUpper(self)
        self.validatorAll = ValidatorAll(self)
        self.validatorInt = QIntValidator(self)

        # set the add step
        self.actionsComboBox = QComboBox(self)
        self.actionsComboBox.setMinimumHeight(40)
        for i in xrange(len(GuiSteps.ACTION_DESCR)):
            if not len( GuiSteps.ACTION_DESCR[i] ):
                self.actionsComboBox.insertSeparator(i+1)
            else:
                el = GuiSteps.ACTION_DESCR[i].keys()
                self.actionsComboBox.addItem( list(el)[0] )

        self.descriptionLine = QLineEdit(self)
        self.descriptionLine.hide()

        self.labelActionDescr = QLabel( )
        self.labelActionDescr.hide()
        self.labelActionDescr.setText( "%s\n" % GuiSteps.ACTION_DESCR[0][GuiSteps.CLICK_WORD])
        self.labelActionDescr.setWordWrap(True)
        
        actionsLayout = QHBoxLayout()
        actionsLayout.addWidget(self.actionsComboBox)

        actionLayoutGroup = QGridLayout()
        actionLayoutGroup.addLayout(actionsLayout, 0, 1)

        self.createWidgetDragDrop()   
        self.createWidgetLocation()     
        self.createWidgetShortcut() 
        self.createWidgetSnapshotImage() 
        self.createWidgetText() 
        self.createWidgetTextTo() 
        self.createWidgetPosXY() 
        self.createWidgetLine() 
        
        actionLayoutGroup2 = QGridLayout()
        actionLayoutGroup2.addWidget( self.lineGroup , 1, 0)
        actionLayoutGroup2.addWidget( self.textGroup , 1, 0)
        actionLayoutGroup2.addWidget( self.textToGroup, 1, 1)
        actionLayoutGroup2.addWidget( self.snapshotImageGroup , 1, 0)
        actionLayoutGroup2.addWidget( self.shortcutGroup , 1, 0)
        actionLayoutGroup2.addWidget( self.drgdrpGroup , 1, 0)
        actionLayoutGroup2.addWidget( self.xyGroup , 1, 0)
        actionLayoutGroup2.addWidget( self.locationGroup , 1, 0)
        
        font = QFont()
        font.setBold(True)
        
        labelAct = QLabel( self.tr("Action: ") )
        labelAct.setFont( font) 
        
        self.arrowLabel = QLabel("")
        self.arrowLabel.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))
        
        self.arrowLabel2 = QLabel("")
        self.arrowLabel2.setPixmap(QPixmap(":/arrow-right.png").scaledToWidth(32))

        layoutSikuli = QHBoxLayout()
        layoutSikuli.addWidget( labelAct )
        layoutSikuli.addLayout(actionLayoutGroup)
        layoutSikuli.addWidget( self.arrowLabel )
        layoutSikuli.addLayout(actionLayoutGroup2)
        layoutSikuli.addWidget( self.arrowLabel2 )
        layoutSikuli.addWidget(self.addStepAction)
        
        layoutSikuli.addStretch(1)
        self.setLayout(layoutSikuli)
  
    def createWidgetLine(self):
        """
        """
        self.lineGroup = QGroupBox(self.tr(""))
        
        self.valueWaitLine = QLineEdit(self)
        validator = QIntValidator (self)
        self.valueWaitLine.setValidator(validator)
        self.valueWaitLine.installEventFilter(self)

        linelayout = QGridLayout()
        linelayout.addWidget(QLabel( self.tr("Number of scroll:") ), 0, 0)
        linelayout.addWidget(self.valueWaitLine, 0, 1)

        self.lineGroup.setLayout(linelayout)
        self.lineGroup.hide()
        
    def createWidgetPosXY(self):
        """
        """
        self.xyGroup = QGroupBox(self.tr(""))
        self.x = QLineEdit(self)
        validator = QIntValidator (self)
        self.x.setValidator(validator)
        self.x.installEventFilter(self)
        self.y = QLineEdit(self)
        validator = QIntValidator (self)
        self.y.setValidator(validator)
        self.y.installEventFilter(self)
        
        xylayout = QGridLayout()
        xylayout.addWidget(QLabel( self.tr("Position (x)") ), 0, 0)
        xylayout.addWidget(self.x, 0, 1)
        xylayout.addWidget(QLabel( self.tr("Position (y)") ), 1, 0)
        xylayout.addWidget(self.y, 1, 1)
        # xylayout.addWidget( self.takeMouseAction, 1, 1)
        
        mainLayout = QHBoxLayout()
        mainLayout.addWidget( self.takeMouseAction )
        mainLayout.addLayout( xylayout )
        
        self.xyGroup.setLayout(mainLayout)
        self.xyGroup.hide()
        
    def createWidgetTextTo(self):
        """
        """
        self.valueTextToLine = QLineEdit(self)
        self.valueTextToLine.setMinimumWidth(300)
        self.valueTextToCombo = QComboBox(self)
        self.valueTextToCombo.addItems( [ "CACHE" ] )
        
        self.textToGroup = QGroupBox(self.tr(""))
        
        textTolayout = QGridLayout()
        textTolayout.addWidget( QLabel( self.tr("Save text in:") ) , 0,0)
        textTolayout.addWidget( self.valueTextToCombo , 0, 1)
        textTolayout.addWidget( self.valueTextToLine , 0, 2)
        
        self.textToGroup.setLayout(textTolayout)
        self.textToGroup.hide()
        
    def createWidgetText(self):
        """
        """
        self.valueTextLine = QLineEdit(self)
        self.valueTextLine.setMinimumWidth(300)
        self.valueTextCombo = QComboBox(self)
        self.valueTextCombo.addItems( LIST_TYPES )

        self.textGroup = QGroupBox(self.tr(""))
        textlayout = QGridLayout()
        textlayout.addWidget( QLabel( self.tr("Type text from:") ) , 0,0)
        textlayout.addWidget( self.valueTextCombo , 0, 1)
        textlayout.addWidget( self.valueTextLine , 0, 2)
        self.textGroup.setLayout(textlayout)
        self.textGroup.hide()
        
    def createWidgetSnapshotImage(self):
        """
        """

        self.thresholdSlider = QSlider(Qt.Horizontal)
        self.thresholdSlider.setFocusPolicy(Qt.StrongFocus)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(10)
        self.thresholdSlider.setSingleStep(1)
        self.thresholdSlider.setMinimum(0)
        self.thresholdSlider.setMaximum(100)
        self.thresholdSlider.setValue( float(self.DEFAULT_SIMILAR_VALUE)*100 )   
        self.thresholdSlider.setMinimumWidth(150)
        
        self.similarGroup = QGroupBox(self.tr("with similarity of"))
        similarLayout = QGridLayout()
        similarLayout.addWidget(self.thresholdSlider, 0, 0)

        self.similarGroup.setLayout(similarLayout)
        
        self.snapshotImageGroup = QGroupBox(self.tr(""))
        mainSnapshotLayout = QHBoxLayout()
        
        self.snapshotImageLabel = QLabel(self.tr(""))
        self.snapshotImageLabel.setPixmap(QPixmap(":/main_logo.png"))
        
        mainSnapshotLayout.addWidget( self.takeSnapshotAction )
        mainSnapshotLayout.addWidget( self.snapshotImageLabel )
        mainSnapshotLayout.addWidget( self.similarGroup )

        self.snapshotImageGroup.setLayout(mainSnapshotLayout)
        self.snapshotImageGroup.hide()

    def createWidgetShortcut(self):
        """
        """
        self.shortcutGroup = QGroupBox(self.tr(""))
        
        mainShortcutlayout = QGridLayout()
        
        shortcutlayout = QHBoxLayout()
        # load the first combo 
        self.modifier1ComboBox = QComboBox(self)
        for i in xrange(len(KEY_MODIFIERS)):
            if len(KEY_MODIFIERS[i]) == 0:
                self.modifier1ComboBox.insertSeparator(i + 2)
            else:
                self.modifier1ComboBox.addItem (KEY_MODIFIERS[i])
                
        # load the second combo 
        self.modifier2ComboBox = QComboBox(self)
        for i in xrange(len(KEY_MODIFIERS)):
            if len(KEY_MODIFIERS[i]) == 0:
                self.modifier2ComboBox.insertSeparator(i + 2)
            else:
                self.modifier2ComboBox.addItem (KEY_MODIFIERS[i])
        # load the third combo 
        self.modifier3ComboBox = QComboBox(self)
        for i in xrange(len(KEYS)):
            if len(KEYS[i]) == 0:
                self.modifier3ComboBox.insertSeparator(i + 2)
            else:
                self.modifier3ComboBox.addItem (KEYS[i])
        # load letters
        self.modifier3ComboBox.insertSeparator(len(KEYS))
        for i in xrange(len(KEY_LETTERS)):
            self.modifier3ComboBox.addItem (KEY_LETTERS[i])

        shortcutlayout.addWidget(self.modifier1ComboBox)
        shortcutlayout.addWidget( QLabel("+") )
        shortcutlayout.addWidget(self.modifier2ComboBox)
        shortcutlayout.addWidget( QLabel("+") )
        shortcutlayout.addWidget(self.modifier3ComboBox)

        self.repeartShortcut = QLineEdit( "0", self)
        validator = QIntValidator (self)
        self.repeartShortcut.setValidator(validator)
        self.repeartShortcut.installEventFilter(self)
        
        mainShortcutlayout.addWidget(QLabel( self.tr("Shortcut") ), 0, 0)
        mainShortcutlayout.addLayout(shortcutlayout, 0, 1)
        mainShortcutlayout.addWidget(QLabel( self.tr("Repeat") ), 1, 0)
        mainShortcutlayout.addWidget(self.repeartShortcut, 1, 1)
        
        self.shortcutGroup.setLayout(mainShortcutlayout)
        self.shortcutGroup.hide()

    def createWidgetDragDrop(self):
        """
        """

        self.thresholdSlider2 = QSlider(Qt.Horizontal)
        self.thresholdSlider2.setFocusPolicy(Qt.StrongFocus)
        self.thresholdSlider2.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider2.setTickInterval(10)
        self.thresholdSlider2.setSingleStep(1)
        self.thresholdSlider2.setMinimum(0)
        self.thresholdSlider2.setMaximum(100)
        self.thresholdSlider2.setValue( float(self.DEFAULT_SIMILAR_VALUE)*100 )   
        self.thresholdSlider2.setMinimumWidth(150)
        
        self.similarGroup2 = QGroupBox(self.tr("with similarity of"))
        similar2Layout = QGridLayout()
        similar2Layout.addWidget(self.thresholdSlider2, 0, 0)

        self.similarGroup2.setLayout(similar2Layout)
        
        self.toX = QLineEdit(self)
        validator = QIntValidator (self)
        self.toX.setValidator(validator)
        self.toX.installEventFilter(self)
        self.toY = QLineEdit(self)
        validator = QIntValidator (self)
        self.toY.setValidator(validator)
        self.toY.installEventFilter(self)
        
        self.snapshotDragImageLabel = QLabel(self.tr(""))
        self.snapshotDragImageLabel.setPixmap(QPixmap(":/main_logo.png"))

        self.drgdrpGroup = QGroupBox(self.tr(""))
        
        drgdrpLayout = QGridLayout()
        drgdrpLayout.addWidget(QLabel( self.tr("Drop to (y)") ), 0, 0)
        drgdrpLayout.addWidget(self.toY, 0, 1)
        drgdrpLayout.addWidget(QLabel( self.tr("Drop to (x)") ), 1, 0)
        drgdrpLayout.addWidget(self.toX, 1, 1)

        drgdrpMainLayout = QHBoxLayout()
        drgdrpMainLayout.addWidget(self.takeDragSnapshotAction )
        drgdrpMainLayout.addWidget(self.snapshotDragImageLabel )
        drgdrpMainLayout.addWidget( self.similarGroup2 )
        drgdrpMainLayout.addWidget( self.takeDragMouseAction )
        drgdrpMainLayout.addLayout(drgdrpLayout)

        self.drgdrpGroup.setLayout(drgdrpMainLayout)
        self.drgdrpGroup.hide()
        
    def createWidgetLocation(self):
        """
        """
        self.valueLocTextLine = QLineEdit(self)
        self.valueLocTextLine.setMinimumWidth(300)
        self.valueLocTextCombo = QComboBox(self)
        self.valueLocTextCombo.addItems( LIST_TYPES )

        self.locX = QLineEdit(self)
        self.locX.setValidator(self.validatorInt)

        self.locY = QLineEdit(self)
        self.locY.setValidator(self.validatorInt)

        self.locW = QLineEdit(self)
        self.locW.setValidator(self.validatorInt)

        self.locH = QLineEdit(self)
        self.locH.setValidator(self.validatorInt)

        self.locationGroup = QGroupBox(self.tr(""))
        
        locationLayoutXY = QGridLayout()
        locationLayoutXY.addWidget(QLabel( self.tr("Area (x)") ), 1, 0)
        locationLayoutXY.addWidget(self.locX, 1, 1)
        locationLayoutXY.addWidget(QLabel( self.tr("Area (y)") ), 1, 2)
        locationLayoutXY.addWidget(self.locY, 1, 3)
        locationLayoutXY.addWidget(QLabel( self.tr("Area (w)") ), 2, 0)
        locationLayoutXY.addWidget(self.locW, 2, 1)
        locationLayoutXY.addWidget(QLabel( self.tr("Area (h)") ), 2, 2)
        locationLayoutXY.addWidget(self.locH, 2, 3)
        
        locationLayout = QGridLayout()
        locationLayout.addWidget(QLabel( self.tr("The Word") ), 0, 0)
        locationLayout.addWidget(self.valueLocTextCombo, 0, 1)
        locationLayout.addWidget(self.valueLocTextLine, 0, 2)
        locationLayout.addWidget(QLabel( self.tr("Area to search") ), 1, 0)
        locationLayout.addWidget(self.takeLocationAction, 1, 1)
        locationLayout.addLayout(locationLayoutXY, 1, 2)
        
        self.locationGroup.setLayout(locationLayout)

    def createToolbar(self):
        """
        """
        pass

    def pluginDataAccessor(self):
        """
        """
        return { "data": "" } 

    def onPluginImport(self, dataJson):
        """
        """
        if "steps" not in dataJson:
            QMessageBox.warning(self, "Recording for Gui" , "bad import")
            
        if not isinstance(dataJson['steps'], list):
            QMessageBox.warning(self, "Recording for Gui" , "bad import")
            
        for stp in dataJson['steps']:
            if isinstance(stp, dict):
                if 'action-name' in stp and 'action-description' in stp:

                    actionName = str(stp["action-name"])
                    if self.checkActionName(actionName=actionName):
                        self.AddStep.emit( actionName, unicode(stp["action-description"]), bytes(stp['image-base64'], 'utf8'),
                                            EMPTY_VALUE, EMPTY_VALUE, str(stp['opt-c']), False, False)
                    else:
                        QMessageBox.warning(self, "Recording for Gui" , "action not yet supported: %s" % actionName)
 
    def checkActionName(self, actionName):
        """
        """
        found = False
        for act in GuiSteps.ACTION_DESCR:
            if actionName in act:
                found = True; break;
        return found
           
    def createConnections(self):
        """
        """
        self.actionsComboBox.currentIndexChanged.connect(self.onActionChanged)
        self.thresholdSlider.valueChanged.connect(self.onSimilarChanged)
        
        self.addStepAction.clicked.connect(self.addStep)
        self.takeSnapshotAction.clicked.connect(self.takeSnapshot)
        self.takeMouseAction.clicked.connect(self.takeMousePosition)
        self.takeLocationAction.clicked.connect(self.takeMouseLocation)
        self.takeDragSnapshotAction.clicked.connect(self.takeSnapshot)
        self.takeDragMouseAction.clicked.connect(self.takeMousePosition)
        
        self.valueLocTextCombo.currentIndexChanged.connect(self.onValueLocTextTypeChanged)
        self.valueTextCombo.currentIndexChanged.connect(self.onValueTextTypeChanged)

    def onValueTextTypeChanged(self):
        """
        """
        if self.valueTextCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.valueTextLine.setValidator(self.validatorAll)
            
        if self.valueTextCombo.currentText() == "ALIAS":
            self.valueTextLine.setText( self.valueTextLine.text().upper() )
            self.valueTextLine.setValidator(self.validatorUpper)
            
    def onValueLocTextTypeChanged(self):
        """
        """
        if self.valueLocTextCombo.currentText() in [ "TEXT", "CACHE" ]:
            self.valueLocTextLine.setValidator(self.validatorAll)
            
        if self.valueLocTextCombo.currentText() == "ALIAS":
            self.valueLocTextLine.setText( self.valueLocTextLine.text().upper() )
            self.valueLocTextLine.setValidator(self.validatorUpper)
            
    def onSimilarChanged(self, value):
        """
        """
        self.similarLabel.setText( self.tr("Similarity threshold\n(%s%%)" % value ) )

    def onActionChanged(self):
        """
        """
        descr = 'No description available!'
        i = 0
        for el in GuiSteps.ACTION_DESCR:
            if isinstance(el, dict):
                if self.actionsComboBox.currentText() in el:
                    descr = GuiSteps.ACTION_DESCR[i][self.actionsComboBox.currentText()]
                    break
            i += 1
        self.labelActionDescr.setText( "%s\n" % descr )
            
        if self.actionsComboBox.currentText() in [ GuiSteps.MOUSE_WHEEL_UP, GuiSteps.MOUSE_WHEEL_DOWN]:
            self.textGroup.hide()
            self.textToGroup.hide()
            
            self.snapshotImageGroup.hide()
            self.lineGroup.show()
            self.shortcutGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.GET_TEXT_CLIPBOARD ]:
            self.valueTextLine.setText("")
            self.textGroup.hide()
            self.textToGroup.show()
            self.snapshotImageGroup.hide()
            self.lineGroup.hide()
            self.shortcutGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.TYPE_PASSWORD ]:
            self.valueTextLine.setText("")
            self.textGroup.show()
            self.textToGroup.hide()
            self.snapshotImageGroup.hide()
            self.lineGroup.hide()
            self.shortcutGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.TYPE_TEXT ]:
            self.valueTextLine.setText("")
            self.textGroup.show()
            self.textToGroup.hide()
            self.valueTextLine.setEchoMode(QLineEdit.Normal)
            self.snapshotImageGroup.hide()
            self.lineGroup.hide()
            self.shortcutGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.TYPE_TEXT_PATH ]:
            self.valueTextLine.setText("")
            self.textGroup.show()
            self.textToGroup.hide()
            self.valueTextLine.setEchoMode(QLineEdit.Normal)
            self.snapshotImageGroup.hide()
            self.lineGroup.hide()
            self.shortcutGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SHORTCUT ]:
            self.textGroup.hide()
            self.textToGroup.hide()
            self.snapshotImageGroup.hide()
            self.lineGroup.hide()
            self.shortcutGroup.show()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)

        elif self.actionsComboBox.currentText() in [ GuiSteps.DRAG_DROP_IMAGE ]:
            self.shortcutGroup.hide()
            self.lineGroup.hide()
            self.textGroup.hide()
            self.textToGroup.hide()
            self.snapshotImageGroup.hide()
            self.takeSnapshotAction.setEnabled(True)
            self.drgdrpGroup.show()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(True)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.MOUSE_CLICK_POSITION, GuiSteps.MOUSE_DOUBLE_CLICK_POSITION, 
                                                    GuiSteps.MOUSE_RIGHT_CLICK_POSITION , GuiSteps.MOUSE_MOVE_POSITION ]:
            self.shortcutGroup.hide()
            self.lineGroup.hide()
            self.textGroup.hide()
            self.textToGroup.hide()
            self.snapshotImageGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.show()
            self.thresholdSlider.setEnabled(False)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.CLICK_WORD, GuiSteps.DOUBLE_CLICK_WORD, 
                                                    GuiSteps.RIGHT_CLICK_WORD , GuiSteps.WAIT_WORD, 
                                                    GuiSteps.WAIT_CLICK_WORD ]:
            self.shortcutGroup.hide()
            self.lineGroup.hide()
            self.textGroup.hide()
            self.textToGroup.hide()
            self.snapshotImageGroup.hide()
            self.takeSnapshotAction.setEnabled(False)
            self.drgdrpGroup.hide()
            self.locationGroup.show()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(False)
            
        else:
            self.shortcutGroup.hide()
            self.lineGroup.hide()
            self.textGroup.hide()
            self.textToGroup.hide()
            self.snapshotImageGroup.show()
            self.takeSnapshotAction.setEnabled(True)
            self.drgdrpGroup.hide()
            self.locationGroup.hide()
            self.xyGroup.hide()
            self.thresholdSlider.setEnabled(True)

    def takeSnapshot(self):
        """
        """
        self.TakeSnapshot.emit()
        
    def takeMousePosition(self):
        """
        """
        self.TakeMousePosition.emit()

    def takeMouseLocation(self):
        """
        """
        self.TakeMouseLocation.emit()

    def getCurrentAction(self):
        """
        """
        return self.actionsComboBox.currentText()
        
    def setTimeout(self, timeout):
        """
        """
        self.optionsDialog.timeoutLine.setText(timeout)
        
    def getTimeout(self):
        """
        """
        return self.optionsDialog.timeoutLine.text()
        
    def getAgentName(self):
        """
        """
        return self.optionsDialog.agentKeyNameLine.text()
        
    def getAgentList(self):
        """
        """
        return self.optionsDialog.agentsList
     
    def editStep(self, stepData):
        """
        """  
        # example stepData
        # {'bold': True, 'active': 'True', 'description': '', 'expected': 'dsq ', 'parameters': {}, 
        # 'action': 'FIND IMAGE', 'action-type': 'Anything', 'id': 2, 'misc': '', 
        # 'image': 'iVBORw0KGgoAAAANSUhEUgAAAHwAAAAbCAYAAAC+7+tcAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQ
        # BlSsOGwAAAYFJREFUaIHt2r9qg1AUBvBP8UEsJSCBu3XI6NA1iENwFrp2cc6YOYtDxswhgwRfIGOGbheyhfoeDulQYjXEaqH3+
        # OeeHwiJCdwDH8dzjTHyPL+C1fpYLLou4c9e9vvaz0zCOlgPcOCa4cA1w4Frxuq6AFWEEK2+J6VUXEm/cIcTmiUJZknS+rwKo+
        # 1woLl7214F/svJ94twT74PAEXQt/eqcYcTKwdNHTYAmMelgBClY3kkW1xX5YApwwYA8x0xpJTFET9/IiMtQT/leU01u2+s6M2
        # tnHDDUOmCTXNz7Lvm+8v4/UxXzbpkAGyStchRb8qaPJrZjzZyKhmO41ynUYpdaCtfbIhG9/BEphGwnkMIgWCb0VXFOmHCDrGT
        # EjL2cF7PeZc+cj/34e4KMo0wPWzAjT5e1R9e7CdMcMYl66YYpl4l8Gy7wQEeXl0A2RaBCL67ve41GxyreuviIZYruF1V00O/7
        # XiHyOD/tOmFH55ohgPXDAeuGQ5cMxy4ZjhwzXwBqL+D433xwRkAAAAASUVORK5CYII=', 
        # 'text': '', 'option-similar': '0.7'}
        
        # {'bold': True, 'active': 'True', 'description': 'dfs', 'from-cache': False, 'option-similar': '0.7', 
        # 'expected': 'Action executed with success', 'parameters': {}, 'action': 'TYPE TEXT', 
        # 'action-type': 'Anything', 'id': 6, 'misc': '', 'image': '', 'text': 'fds &', 'from-alias': False}
        self.thresholdSlider.setEnabled(False)

        self.addStepAction.setText( "&Update" )
        buttonFont = QFont()
        buttonFont.setBold(True)
        self.addStepAction.setFont(buttonFont)
        self.cancelStepAction.setEnabled(True)

        
        # set the current value for actions combo
        for i in xrange(self.actionsComboBox.count()):
            item_text = self.actionsComboBox.itemText(i)
            if unicode(stepData["action"]) == unicode(item_text):
                self.actionsComboBox.setCurrentIndex(i)
                break
                
        # and then refresh options
        self.onActionChanged()
        
        # finally fills all fields
        self.descriptionLine.setText( stepData["description"] )
        if self.actionsComboBox.currentText() in [ 
                                                    GuiSteps.HOVER_IMAGE, GuiSteps.CLICK_IMAGE, GuiSteps.RIGHT_CLICK_IMAGE, 
                                                    GuiSteps.RIGHT_CLICK_IMAGE_ALL, GuiSteps.DOUBLE_CLICK_IMAGE, 
                                                    GuiSteps.FIND_IMAGE, GuiSteps.DONT_FIND_IMAGE, 
                                                    GuiSteps.FIND_CLICK_IMAGE, GuiSteps.CLICK_IMAGE_ALL, 
                                                    GuiSteps.DOUBLE_CLICK_IMAGE_ALL, GuiSteps.WAIT_IMAGE, GuiSteps.WAIT_CLICK_IMAGE
                                                ]:
            pixmap = QPixmap()
            pixmap.loadFromData( base64.b64decode( stepData["image"] ) )
            self.snapshotImageLabel.setPixmap(pixmap)
            
            self.thresholdSlider.setEnabled(True)
            self.thresholdSlider.setValue( int(float(stepData["option-similar"])*100) )
            
        if self.actionsComboBox.currentText() in [ GuiSteps.SHORTCUT ]:

            # set default
            for i in xrange(self.modifier1ComboBox.count()):
                item_text = self.modifier1ComboBox.itemText(i)
                if unicode("None") == unicode(item_text):
                    self.modifier1ComboBox.setCurrentIndex(i)
                    break
            for i in xrange(self.modifier2ComboBox.count()):
                item_text = self.modifier2ComboBox.itemText(i)
                if unicode("None") == unicode(item_text):
                    self.modifier2ComboBox.setCurrentIndex(i)
                    break
            for i in xrange(self.modifier3ComboBox.count()):
                item_text = self.modifier3ComboBox.itemText(i)
                if unicode("None") == unicode(item_text):
                    self.modifier3ComboBox.setCurrentIndex(i)
                    break
            # set modifiers        
            modifiers = stepData["misc"].split("+")
            if len(modifiers) == 2:
                for i in xrange(self.modifier1ComboBox.count()):
                    item_text = self.modifier1ComboBox.itemText(i)
                    if unicode(modifiers[0]) == unicode(item_text):
                        self.modifier1ComboBox.setCurrentIndex(i)
                        break
                for i in xrange(self.modifier2ComboBox.count()):
                    item_text = self.modifier2ComboBox.itemText(i)
                    if unicode(modifiers[1]) == unicode(item_text):
                        self.modifier2ComboBox.setCurrentIndex(i)
                        break
            if len(modifiers) == 1:
                for i in xrange(self.modifier1ComboBox.count()):
                    item_text = self.modifier1ComboBox.itemText(i)
                    if unicode(modifiers[0]) == unicode(item_text):
                        self.modifier1ComboBox.setCurrentIndex(i)
                        break
                        
            if not len(stepData["text"]) and len(stepData["misc"]):
                for i in xrange(self.modifier3ComboBox.count()):
                    item_text = self.modifier3ComboBox.itemText(i)
                    if unicode(stepData["misc"]) == unicode(item_text):
                        self.modifier3ComboBox.setCurrentIndex(i)
                        break
            
            if len(stepData["text"]):
                for i in xrange(self.modifier3ComboBox.count()):
                    item_text = self.modifier3ComboBox.itemText(i)
                    if unicode(stepData["text"]) == unicode(item_text):
                        self.modifier3ComboBox.setCurrentIndex(i)
                        break
            
            if 'option-similar' in stepData:
                if str(stepData["option-similar"]) == '0.7':
                    self.repeartShortcut.setText( "0" )
                else:
                    self.repeartShortcut.setText( stepData["option-similar"] )
            else:
                self.repeartShortcut.setText( "0" )
                
        if self.actionsComboBox.currentText() in [ GuiSteps.TYPE_TEXT, GuiSteps.TYPE_TEXT_PATH, GuiSteps.TYPE_PASSWORD ]:
            self.valueTextLine.setText( stepData["text"] )
            
            if "from-alias" not in stepData: # for backward compatibility
                stepData["from-alias"] = False 
                
            if stepData["from-cache"]:
                self.valueTextCombo.setCurrentIndex(INDEX_CACHE)
                self.valueTextLine.setValidator(self.validatorAll)
            elif stepData["from-alias"]:
                self.valueTextCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueTextLine.setValidator(self.validatorUpper) 
            else:
                self.valueTextCombo.setCurrentIndex(INDEX_TEXT)
                self.valueTextLine.setValidator(self.validatorAll)
                 
        if self.actionsComboBox.currentText() in [ GuiSteps.DRAG_DROP_IMAGE ]:
            pixmap = QPixmap()
            pixmap.loadFromData( base64.b64decode( stepData["image"] ) )
            self.snapshotDragImageLabel.setPixmap(pixmap)
            
            self.toY.setText( stepData["text"] )
            self.toX.setText( stepData["misc"] )
            
            self.thresholdSlider2.setEnabled(True)
            self.thresholdSlider2.setValue( int(float(stepData["option-similar"])*100) )
            
        if self.actionsComboBox.currentText() in [ GuiSteps.MOUSE_CLICK_POSITION, GuiSteps.MOUSE_DOUBLE_CLICK_POSITION, 
                                                    GuiSteps.MOUSE_RIGHT_CLICK_POSITION, GuiSteps.MOUSE_MOVE_POSITION ]:

            self.x.setText( stepData["text"] )
            self.y.setText( stepData["misc"] )
            
        if self.actionsComboBox.currentText() in [ GuiSteps.CLICK_WORD, GuiSteps.DOUBLE_CLICK_WORD, 
                                                    GuiSteps.RIGHT_CLICK_WORD, GuiSteps.WAIT_WORD, GuiSteps.WAIT_CLICK_WORD  ]:

            self.locX.setText( stepData["parameters"]["location-x"] )
            self.locY.setText( stepData["parameters"]["location-y"] )
            self.locW.setText( stepData["parameters"]["location-w"] )
            self.locH.setText( stepData["parameters"]["location-h"] )

            if stepData["parameters"]["from-cache"]:
                self.valueLocTextLine.setText ( stepData["parameters"]["location-word"] )
                self.valueLocTextCombo.setCurrentIndex(INDEX_CACHE)
                self.valueLocTextLine.setValidator(self.validatorAll)
            elif stepData["parameters"]["from-alias"]:
                self.valueLocTextLine.setText ( stepData["parameters"]["location-word"].upper() )
                self.valueLocTextCombo.setCurrentIndex(INDEX_ALIAS)
                self.valueLocTextLine.setValidator(self.validatorUpper)
            else:
                self.valueLocTextLine.setText ( stepData["parameters"]["location-word"] )
                self.valueLocTextLine.setValidator(self.validatorAll)
                self.valueLocTextCombo.setCurrentIndex(INDEX_TEXT)
 
        if self.actionsComboBox.currentText() in [ GuiSteps.MOUSE_WHEEL_UP, GuiSteps.MOUSE_WHEEL_DOWN ]:
            self.valueWaitLine.setText( stepData["misc"] )
            
        if self.actionsComboBox.currentText() in [ GuiSteps.GET_TEXT_CLIPBOARD ]:      
            if stepData["from-cache"]:
                self.valueTextToLine.setText( stepData["text"] )
            else:
                self.valueTextToLine.setText( "" )
    
    def addStep(self):
        """
        """
        action = self.actionsComboBox.currentText()
        descr = self.descriptionLine.text()
        descr = unicode(descr).replace('"', '')
        
        signal = self.AddStep
        if self.cancelStepAction.isEnabled():
            signal = self.UpdateStep
            
        if self.actionsComboBox.currentText() in [ GuiSteps.HOVER_IMAGE, GuiSteps.CLICK_IMAGE, GuiSteps.RIGHT_CLICK_IMAGE, 
                                                    GuiSteps.RIGHT_CLICK_IMAGE_ALL,
                                                    GuiSteps.DOUBLE_CLICK_IMAGE, GuiSteps.FIND_IMAGE, GuiSteps.DONT_FIND_IMAGE, 
                                                    GuiSteps.FIND_CLICK_IMAGE,
                                                    GuiSteps.CLICK_IMAGE_ALL, GuiSteps.DOUBLE_CLICK_IMAGE_ALL,
                                                    GuiSteps.WAIT_IMAGE, GuiSteps.WAIT_CLICK_IMAGE, ]:
            pixmap = self.snapshotImageLabel.pixmap()
            # if no snapshot on label, nothing to add
            if pixmap is None:
                self.exportStepsAction.setEnabled(False)
                return
            
            # save QPixmap to QByteArray via QBuffer.
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, 'PNG')

            # convert to base64
            data64 = base64.b64encode(byte_array)

            # get similar
            similar = "%s" % (self.thresholdSlider.value()/100)
            
            # add the step in the datamodel
            parameters = {}
            signal.emit(str(action), unicode(descr), data64, EMPTY_VALUE, EMPTY_VALUE, similar, False, False, parameters)
                                    
        elif self.actionsComboBox.currentText() in [ GuiSteps.DRAG_DROP_IMAGE ]:
            pixmap = self.snapshotDragImageLabel.pixmap()
            # if no snapshot on label, nothing to add
            if pixmap is None:
                self.exportStepsAction.setEnabled(False)
                return
            
            # save QPixmap to QByteArray via QBuffer.
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, 'PNG')

            # convert to base64
            data64 = base64.b64encode(byte_array)

            toY = "%s" % self.toY.text()
            if not len(toY): toY = "0"
            toX = "%s" % self.toX.text()
            if not len(toX): toX = "0"
            
            # get similar
            similar = "%s" % (self.thresholdSlider2.value()/100)
            
            # add the step in the datamodel
            parameters = {}
            signal.emit("%s" % action, unicode(descr), data64, toY, toX, similar, False, False, parameters)
        
        elif self.actionsComboBox.currentText() in [ GuiSteps.MOUSE_CLICK_POSITION, GuiSteps.MOUSE_DOUBLE_CLICK_POSITION, 
                                                        GuiSteps.MOUSE_RIGHT_CLICK_POSITION, GuiSteps.MOUSE_MOVE_POSITION  ]:

            x = "%s" % self.x.text()
            if not len(x): x = "0"
            y = "%s" % self.y.text()
            if not len(y): y = "0"

            parameters = {}
            signal.emit("%s" % action, unicode(descr), EMPTY_IMG, x, y, EMPTY_VALUE, False, False, parameters)
        
        elif self.actionsComboBox.currentText() in [ GuiSteps.CLICK_WORD, GuiSteps.DOUBLE_CLICK_WORD, GuiSteps.WAIT_CLICK_WORD, 
                                                        GuiSteps.RIGHT_CLICK_WORD, GuiSteps.WAIT_WORD  ]:

            textStr = self.valueLocTextLine.text()
            
            fromCache = False
            if self.valueLocTextCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.valueLocTextCombo.currentText() == "ALIAS": fromAlias = True

            if fromCache and not len(textStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set a key name!")
                return
            elif fromAlias and not len(textStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set the alias name!")
                return
            elif not len(textStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set a word!")
                return

            x = "%s" % self.locX.text()
            if not len(x): x = "0"
            y = "%s" % self.locY.text()
            if not len(y): y = "0"
            w = "%s" % self.locW.text()
            if not len(w): w = "0"
            h = "%s" % self.locH.text()
            if not len(h): h = "0"

            parameters = { "location-x": x, "location-y": y, "location-w": w, "location-h": h, "location-word": textStr,
                            "from-cache": fromCache, "from-alias": fromAlias }
            signal.emit("%s" % action, unicode(descr), EMPTY_IMG, EMPTY_VALUE, EMPTY_VALUE, EMPTY_VALUE, False, False, parameters)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.SHORTCUT ]:
            repeat = self.repeartShortcut.text()
            if not len(repeat):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set a repeat value!")
            else:
                firstShorcut = self.modifier1ComboBox.currentText()
                secondShortcut = self.modifier2ComboBox.currentText()
                thirdShorcut = self.modifier3ComboBox.currentText()

                modifiers = ""
                if firstShorcut != "None":
                    modifiers = "%s+" % str(firstShorcut)

                if secondShortcut != "None":
                    modifiers += "%s+" % str(secondShortcut)
                
                # add the step in the datamodel
                parameters = {}
                signal.emit(str(action), unicode(descr), EMPTY_IMG, str(thirdShorcut), modifiers, str(repeat), False, False, parameters)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.TYPE_TEXT, GuiSteps.TYPE_TEXT_PATH, GuiSteps.TYPE_PASSWORD ]:
            textStr = self.valueTextLine.text()
            
            fromCache = False
            if self.valueTextCombo.currentText() == "CACHE": fromCache = True
            fromAlias = False
            if self.valueTextCombo.currentText() == "ALIAS": fromAlias = True

                
            if fromCache and not len(textStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set a key name!")
                return
            elif fromAlias and not len(textStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set the alias name!")
                return
            elif not len(textStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set the text to type!")
                return
                
            # add the step in the datamodel
            parameters = {}
            signal.emit(str(action), unicode(descr), EMPTY_IMG, unicode(textStr), EMPTY_VALUE, EMPTY_VALUE, fromCache, fromAlias, parameters)
            
        elif self.actionsComboBox.currentText() in [ GuiSteps.MOUSE_WHEEL_UP, GuiSteps.MOUSE_WHEEL_DOWN ]:
            miscStr = self.valueWaitLine.text()
            if not len(miscStr):
                QMessageBox.warning(self, "Automation Assistant" , "Please to set a value!")
            else:
                # add the step in the datamodel
                parameters = {}
                signal.emit(str(action), unicode(descr), EMPTY_IMG, EMPTY_VALUE, miscStr, EMPTY_VALUE, False, False, parameters)

        elif self.actionsComboBox.currentText() in [ GuiSteps.GET_TEXT_CLIPBOARD ]:
            toCache = True
            keyText = self.valueTextToLine.text()
            if not len(keyText):
                QMessageBox.warning(self, "Automation Assistant" , "Please to specify a key name!")
            else:
                parameters = {}
                signal.emit(str(action), unicode(descr), EMPTY_IMG, unicode(keyText), EMPTY_VALUE, EMPTY_VALUE, toCache, False, parameters)
            
        else:
            pass
            
    def cancelStep(self):
        """
        """
        self.addStepAction.setText( "&Add" )
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addStepAction.setFont(buttonFont)
        self.cancelStepAction.setEnabled(False)
        
        self.CancelEdit.emit()
    
    def finalizeUpdate(self):
        """
        """
        self.addStepAction.setText( "&Add Action" )
        
        buttonFont = QFont()
        buttonFont.setBold(False)
        self.addStepAction.setFont(buttonFont)
        self.cancelStepAction.setEnabled(False)
        
    def setSnapshotText(self, snapshot):
        """
        """
        self.snapshotTextLabel.setPixmap(snapshot)
        
    def setSnapshotDrag(self, snapshot):
        """
        """
        self.snapshotDragImageLabel.setPixmap(snapshot)
        
    def setSnapshotImage(self, snapshot):
        """
        """
        self.snapshotImageLabel.setPixmap(snapshot)
    
    def setMousePosition(self, posX, posY):
        """
        """
        self.x.setText( "%s" % posX)
        self.y.setText( "%s" % posY)
        
        self.toX.setText( "%s" % posX)
        self.toY.setText( "%s" % posY)

    def setMouseLocation(self, posX, posY, posW, posH):
        """
        """
        self.locX.setText( "%s" % posX)
        self.locY.setText( "%s" % posY)
        self.locW.setText( "%s" % posW)
        self.locH.setText( "%s" % posH)