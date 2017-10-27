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
Test abstract generic dialog
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
    from PyQt4.QtGui import (QLabel, QFrame, QSizePolicy, QTabWidget, QVBoxLayout, QGridLayout, 
                            QRadioButton, QTextEdit, QLineEdit, QComboBox, QFont, QButtonGroup, QIntValidator, 
                            QDoubleValidator, QDialogButtonBox)
    from PyQt4.QtCore import (pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QFont, QIntValidator, QDoubleValidator)
    from PyQt5.QtWidgets import (QLabel, QFrame, QSizePolicy, QTabWidget, QVBoxLayout, 
                                QGridLayout, QRadioButton, QTextEdit, QLineEdit, QComboBox, 
                                QButtonGroup, QDialogButtonBox)
    from PyQt5.QtCore import (pyqtSignal)
    
from Libs import QtHelper, Logger

try:
    import OperatorsWidget
    import DictWidget
except ImportError: # support python3
    from . import OperatorsWidget
    from . import DictWidget
    
HEIGHT_TEXT_AREA            = 35
WIDTH_TEXT_AREA             = 250
MAX_ARGUMENT_TO_DISPLAY     = 15
MAX_ARGUMENT_TO_DISPLAY2    = 30

MAX_COL                     = 12

class QLabelEnhanced(QLabel):
    """
    Label enhanced widget
    """
    EnterLabel = pyqtSignal(str)  
    LeaveLabel = pyqtSignal()  
    def __init__(self, text, parent, data):
        """
        QLabel enhanced
        """
        QLabel.__init__(self, text, parent)
        self.__data = data
        
    def enterEvent(self, event):
        """
        On enter widget
        """
        self.EnterLabel.emit(self.__data)
        event.accept()

    def leaveEvent(self, event):
        """
        On leave widget
        """
        self.LeaveLabel.emit()
        event.accept()
        
class BasicWidget(QFrame, Logger.ClassLogger):
    """
    Basic widget
    """
    def __init__(self, actionData, owner, variables, testParams, parent, adapterMode=False, stepMode=False):
        """
        Constructs WDocumentViewer widget 

        @param parent: 
        @type parent:
        """
        QFrame.__init__(self, parent)
        self.parent = parent
        self.testParams = testParams
        self.owner = owner
        self.variables = variables
        self.adapterMode = adapterMode

        self.actionData = actionData
        self.createWidget()

    def createWidget(self):
        """
        Create widget
        """ 
        self.labelDescr = QLabel("\n\n")
        self.labelDescr.setFrameStyle(QFrame.StyledPanel)
        self.labelDescr.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed) # added to avoid a resize of the window
        
        self.mainTab = QTabWidget()
        self.mainFrame = QFrame()
        self.moreFrame = QFrame()
        self.more2Frame = QFrame()
        
        self.mainTab.addTab(self.mainFrame, "Arguments")
        self.mainTab.addTab(self.moreFrame, "Next ...")
        self.mainTab.addTab(self.more2Frame, "More...")
        self.mainTab.setTabEnabled(1, False)
        self.mainTab.setTabEnabled(2, False)
        
        self.widgetLayout = QVBoxLayout()
        self.widgetLayout.addWidget(self.mainTab)
        self.widgetLayout.addWidget(self.labelDescr)
        
        self.mainLayout = QGridLayout()
        self.mainFrame.setLayout(self.mainLayout)

        self.moreLayout = QGridLayout()
        self.moreFrame.setLayout(self.moreLayout)

        self.more2Layout = QGridLayout()
        self.more2Frame.setLayout(self.more2Layout)
        
        self.setLayout(self.widgetLayout)

        self.addWidgets()

    def __getOption(self, targetLayout, i, z=1):
        """
        Get option
        """
        widgetOpt = None
        widgetVal = None
        widgetOptTmp = targetLayout.itemAtPosition(i, z).widget()
        if isinstance(widgetOptTmp, QRadioButton):
            widgetOpt = widgetOptTmp
            if widgetOpt.isChecked():
                widgetValTmp = targetLayout.itemAtPosition(i, z+1)
                if widgetValTmp is not None:
                    widgetVal = widgetValTmp.widget()
            else:
                if z < MAX_COL:
                    widgetOpt, widgetVal = self.__getOption(targetLayout=targetLayout, i=i, z=z+2)
        return (widgetOpt, widgetVal)

    def setValues(self):
        """
        Set values
        """
        nbArgument = 0

        layoutUsed = self.mainLayout
        
        for i in xrange(len(self.actionData['data']['obj'])):
            nbArgument += 1

            if nbArgument > MAX_ARGUMENT_TO_DISPLAY  :
                layoutUsed = self.moreLayout
            if nbArgument > MAX_ARGUMENT_TO_DISPLAY2:
                layoutUsed = self.more2Layout

            widgetKey = layoutUsed.itemAtPosition(i, 0).widget()
            widgetKeyName = unicode(widgetKey.text())
            if self.actionData['data']['obj'][i]['name'] == widgetKeyName:

                widgetOpt, widgetVal = self.__getOption(targetLayout=layoutUsed, i=i, z=1)

                # set the user value and the type selected for each parameters
                if widgetOpt is not None:
                    self.actionData['data']['obj'][i]['selected-type'] = unicode( widgetOpt.text() ) 
                if widgetVal is not None:  
                    if unicode( widgetOpt.text() )  == 'testcase' :
                        self.actionData['data']['obj'][i]['value'] = 'self'
                        
                    if unicode( widgetOpt.text() )  == 'object' and isinstance(widgetVal, QTextEdit):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.toPlainText() )

                    elif unicode( widgetOpt.text() )  == 'string' and isinstance(widgetVal, QTextEdit):
                        self.actionData['data']['obj'][i]['value'] = unicode(widgetVal.toPlainText())

                    elif unicode( widgetOpt.text() )  == 'dict' and isinstance(widgetVal, DictWidget.DictWidget):
                        self.actionData['data']['obj'][i]['value'] = { 'dict': widgetVal.getCurrentDict() }

                    elif unicode( widgetOpt.text() )  == 'dictadvanced' and isinstance(widgetVal, DictWidget.DictWidget):
                        self.actionData['data']['obj'][i]['value'] = { 'dictadvanced': widgetVal.getCurrentDict() }

                    elif unicode( widgetOpt.text() )  == 'list' and isinstance(widgetVal, QTextEdit):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.toPlainText() )

                    elif unicode( widgetOpt.text() )  == 'integer' and isinstance(widgetVal, QLineEdit):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.text() )

                    elif unicode( widgetOpt.text() )  == 'float' and isinstance(widgetVal, QLineEdit):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.text() )
                    
                    elif unicode( widgetOpt.text() )  == 'boolean' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'strconstant' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'intconstant' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'inputs' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'outputs' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'agents' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'variables' and isinstance(widgetVal, QComboBox):
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.currentText() )

                    elif unicode( widgetOpt.text() )  == 'operators' and isinstance(widgetVal, OperatorsWidget.OperatorsWidget):
                        self.actionData['data']['obj'][i]['value'] = widgetVal.currentOperator()

                    elif unicode( widgetOpt.text() )  == 'condition' and isinstance(widgetVal, OperatorsWidget.OperatorsWidget):
                        self.actionData['data']['obj'][i]['value'] = widgetVal.currentOperator()

                    else:
                        self.actionData['data']['obj'][i]['value'] = unicode( widgetVal.toPlainText() )

    def getValues(self):
        """
        Get values
        """
        return self.actionData['data']['obj']

    def loadArgumentDescription(self, description):
        """
        Load argument description
        """
        self.labelDescr.setText( "\n%s\n" % description)
        
    def clearArgumentDescription(self):
        """
        Clear argument description
        """
        self.labelDescr.setText( "\n\n" )
        
    def addWidgets(self):
        """
        Add widgets
        """
        nbArgument = 0
        layoutUsed = self.mainLayout
        
        fontBold = QFont()
        fontBold.setBold(True)

        fontNormal = QFont()
        fontNormal.setBold(False)

        for i in xrange(len(self.actionData['data']['obj'])):
            # prevent to limit the display of all arguments
            # split all arguments in two tabulations if necessary
            nbArgument += 1
            if nbArgument > MAX_ARGUMENT_TO_DISPLAY:
                layoutUsed = self.moreLayout # the second tab
                self.mainTab.setTabEnabled(1, True)
            if nbArgument > MAX_ARGUMENT_TO_DISPLAY2:
                layoutUsed = self.more2Layout # the second tab
                self.mainTab.setTabEnabled(2, True)
                
            # extract the name of the function
            varName = self.actionData['data']['obj'][i]['name']
            #argNameLabel = QLabel( varName )
            argNameLabel = QLabelEnhanced( varName, parent=self, data=self.actionData['data']['obj'][i]['descr'])
            argNameLabel.EnterLabel.connect(self.loadArgumentDescription)
            argNameLabel.LeaveLabel.connect(self.clearArgumentDescription)
            #argNameLabel.setToolTip(self.actionData['data']['obj'][i]['descr'])
            layoutUsed.addWidget(argNameLabel, i, 0)

            typeDetected = self.actionData['data']['obj'][i]['type'].split("/")

            opDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'operators':
                    opDetected = True
                    break
                if typeDetected[j].lower() == 'condition':
                    opDetected = True
                    break

            labDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'label':
                    labDetected = True
                    break

            constDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() in [ 'strconstant', 'intconstant' ]:
                    constDetected = True
                    break

            dictDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'dict':
                    dictDetected = True
                    break

            tplMDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'templatemessage':
                    tplMDetected = True
                    break
            if tplMDetected:
                typeDetected.pop(j)

            tplLDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'templatelayer':
                    tplLDetected = True
                    break
            if tplLDetected:
                typeDetected.pop(j)

            # exception for testcase parent in adapters or libraries
            if self.actionData['data']['obj'][i]['type'] != "testcase":
                if not self.adapterMode:
                    if dictDetected or tplMDetected or tplLDetected:
                        typeDetected.extend( [ 'variables' ] )
                    else:
                        if not opDetected:
                            if not labDetected:
                                if not constDetected:
                                    typeDetected.extend( ['inputs', 'outputs', 'variables' ] )
                else:
                    if not constDetected:
                        typeDetected.extend( ['inputs', 'outputs' ] )

            # second exception for agent mode
            if self.adapterMode and varName == "agent":
                if "none" in typeDetected or "None" in typeDetected: typeDetected = [ 'agents', "none" ]
                else: typeDetected = [ 'agents' ]

            # move none if exists on the list to the end
            noneDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'none':
                    noneDetected = True
                    break
            if noneDetected:
                typeDetected.pop(j)
                typeDetected.append( "none" )

            # remove image type
            imgDetected = False
            for j in xrange(len(typeDetected)):
                if typeDetected[j].lower() == 'image':
                    imgDetected = True
                    break
            if imgDetected:
                typeDetected.pop(j)

            # remove string type if operators exists
            strDetected = False
            if opDetected:
                for j in xrange(len(typeDetected)):
                    if typeDetected[j].lower() == 'string':
                        strDetected = True
                        break
                if strDetected:
                    typeDetected.pop(j)

            radioGroup=QButtonGroup(self)

            shiftWidget = 1
            deltaWidget = 0
            radioSelected = shiftWidget

            for j in xrange(len(typeDetected)):
                #if typeDetected[j].lower() == "list":
                #    continue

                radioButton  = QRadioButton( typeDetected[j].lower() )
                radioButton.setFont(fontNormal)
                radioGroup.addButton( radioButton )
                layoutUsed.addWidget(radioButton, i, j+shiftWidget+deltaWidget)

                if typeDetected[j].lower() == "testcase":
                    pass

                elif typeDetected[j].lower() == "none":
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                    else:
                        if 'default-value' in self.actionData['data']['obj'][i]:
                            if not len(self.actionData['data']['obj'][i]['selected-type']) and self.actionData['data']['obj'][i]['default-value'] == 'None':
                                radioSelected = j+shiftWidget+deltaWidget
 
                elif typeDetected[j].lower() in [ "inputs", "outputs", "agents", "variables" ]:
                    paramCombo = QComboBox( )
                    layoutUsed.addWidget( paramCombo , i, j+shiftWidget+deltaWidget+1)

                    if typeDetected[j].lower() == 'inputs':
                        for inpt in self.owner.getInputs(): paramCombo.addItem(inpt['name'])
                    if typeDetected[j].lower() == 'outputs':
                        for inpt in self.owner.getOutputs(): paramCombo.addItem(inpt['name'])
                    if typeDetected[j].lower() == 'agents':
                        for inpt in self.owner.getAgents(): paramCombo.addItem(inpt['name'])
                    if typeDetected[j].lower() == 'variables':
                        paramCombo.addItems(self.variables)

                    # set as default value or not ?
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        for x in xrange(paramCombo.count()):
                            if paramCombo.itemText(x) == self.actionData['data']['obj'][i]['value']:
                                paramCombo.setCurrentIndex(x) 
                    deltaWidget += 1

                elif typeDetected[j].lower() == "string":
                    textArea = QTextEdit( )
                    textArea.setMinimumHeight(HEIGHT_TEXT_AREA)  
                    textArea.setMinimumWidth(WIDTH_TEXT_AREA)    
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        try:
                            if sys.version_info > (3,): # python 3 support 
                                self.actionData['data']['obj'][i]['value'] = self.actionData['data']['obj'][i]['value']
                            else:
                                self.actionData['data']['obj'][i]['value'] = self.actionData['data']['obj'][i]['value'].decode('utf8')
                            textArea.setText( self.actionData['data']['obj'][i]['value'] )
                        except UnicodeDecodeError as e:
                            textArea.setText( self.actionData['data']['obj'][i]['value'] )
                        except UnicodeEncodeError as e:
                            textArea.setText( self.actionData['data']['obj'][i]['value'] )
                    else:
                        if 'none' not in self.actionData['data']['obj'][i]['type'].lower():
                            if 'default-value' in self.actionData['data']['obj'][i]: 
                                textArea.setText( self.actionData['data']['obj'][i]['default-value'] )
                    layoutUsed.addWidget(textArea, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() in [ "integer", "float" ]:
                    lineEdit = QLineEdit( )
                    if typeDetected[j].lower() == "integer":
                        validator = QIntValidator (lineEdit)
                    else:
                        validator = QDoubleValidator(lineEdit)
                        validator.setNotation(QDoubleValidator.StandardNotation)
                    lineEdit.setValidator(validator)
                    lineEdit.installEventFilter(self)

                    if self.actionData['data']['obj'][i]['selected-type'] in [ 'integer', 'float' ]:
                        radioSelected = j+shiftWidget+deltaWidget
                        lineEdit.setText( "%s" % self.actionData['data']['obj'][i]['value'] )
                    else:
                        if 'default-value' in self.actionData['data']['obj'][i]: 
                            lineEdit.setText( str(self.actionData['data']['obj'][i]['default-value']) )
                    layoutUsed.addWidget(lineEdit, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() in [ "strconstant", "intconstant" ]:

                    consCombo = QComboBox( )
                    # extract values
                    tmpconstant =  self.actionData['data']['obj'][i]['descr']
                    tmpvals = tmpconstant.split("|")
                    # extract all constant and detect the default
                    vals = []
                    defConstant = 0
                    defConstantVal = ''
                    for zz in xrange(len(tmpvals)):
                        if '(default)' in tmpvals[zz]:
                            nameConstant = tmpvals[zz].split('(default)')[0].strip()
                            vals.append( nameConstant )
                            defConstant = zz
                            defConstantVal = nameConstant
                        else:
                            vals.append( tmpvals[zz].strip() )
                    # append all constant to the combobox
                    consCombo.addItems(vals)
                    
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        for x in xrange(len(vals)):
                            if vals[x] == str(self.actionData['data']['obj'][i]['value']):
                                consCombo.setCurrentIndex(x)
                    else:            
                        # set the current index for default value
                        consCombo.setCurrentIndex(defConstant)

                    layoutUsed.addWidget(consCombo, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "boolean":
                    boolCombo = QComboBox( )
                    valBool = [ "True", "False" ]
                    boolCombo.addItems(valBool)

                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        for x in xrange(len(valBool)):
                            if valBool[x] == str(self.actionData['data']['obj'][i]['value']):
                                boolCombo.setCurrentIndex(x)
                    else:
                        # set the default value
                        if 'default-value' in self.actionData['data']['obj'][i]:
                            for x in xrange(len(valBool)):
                                if valBool[x] == str(self.actionData['data']['obj'][i]['default-value']):
                                    boolCombo.setCurrentIndex(x)
                    layoutUsed.addWidget(boolCombo, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "dict":
                    dictWidget = DictWidget.DictWidget(parent=self, advancedMode=False, testParams=self.testParams, variables=self.variables)

                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget

                        if not isinstance(self.actionData['data']['obj'][i]['value'], dict):
                            self.actionData['data']['obj'][i]['value'] = {'dict': [] }

                        dictVal = self.actionData['data']['obj'][i]['value']['dict']
                        dictWidget.setCurrentDict( dictVal = dictVal)
 
                    layoutUsed.addWidget(dictWidget, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "dictadvanced":
                    dictWidget = DictWidget.DictWidget(parent=self, advancedMode=True, testParams=self.testParams, variables=self.variables)

                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget

                        if not isinstance(self.actionData['data']['obj'][i]['value'], dict):
                            self.actionData['data']['obj'][i]['value'] = {'dictadvanced': [] }

                        dictVal = self.actionData['data']['obj'][i]['value']['dictadvanced']
                        dictWidget.setCurrentDict( dictVal = dictVal)
 
                    layoutUsed.addWidget(dictWidget, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "operators":
                    opWidget = OperatorsWidget.OperatorsWidget(self, testParams=self.testParams, variables=self.variables) 
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        opWidget.setCurrentOperator( operatorVal=self.actionData['data']['obj'][i]['value'] )

                    layoutUsed.addWidget(opWidget, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "condition":
                    opWidget = OperatorsWidget.OperatorsWidget(self, testParams=self.testParams, variables=self.variables, liteMode=True) 
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        opWidget.setCurrentOperator( operatorVal=self.actionData['data']['obj'][i]['value'] )

                    layoutUsed.addWidget(opWidget, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "templatelayer":
                    textArea = QLineEdit( ) 
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        textArea.setText( self.actionData['data']['obj'][i]['value'] )
                    else:
                        if 'none' not in self.actionData['data']['obj'][i]['type'].lower():
                            if 'default-value' in self.actionData['data']['obj'][i]: 
                                textArea.setText( self.actionData['data']['obj'][i]['default-value'] )
                    layoutUsed.addWidget(textArea, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                elif typeDetected[j].lower() == "object":
                    textArea = QTextEdit( )
                    textArea.setFixedHeight(HEIGHT_TEXT_AREA)  
                    textArea.setMinimumWidth(WIDTH_TEXT_AREA)    
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        textArea.setText( self.actionData['data']['obj'][i]['value'] )
                    else:
                        # typeParam.setChecked(True) # fix bug 
                        if 'none' not in self.actionData['data']['obj'][i]['type'].lower():
                            if 'default-value' in self.actionData['data']['obj'][i]: 
                                textArea.setText( self.actionData['data']['obj'][i]['default-value'] )
                    layoutUsed.addWidget(textArea, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

                else:
                    textArea = QTextEdit( )
                    textArea.setFixedHeight(HEIGHT_TEXT_AREA)  
                    textArea.setMinimumWidth(WIDTH_TEXT_AREA)    
                    if self.actionData['data']['obj'][i]['selected-type'] == typeDetected[j].lower():
                        radioSelected = j+shiftWidget+deltaWidget
                        textArea.setText( self.actionData['data']['obj'][i]['value'] )
                    else:
                        if 'none' not in self.actionData['data']['obj'][i]['type'].lower():
                            if 'default-value' in self.actionData['data']['obj'][i]: 
                                textArea.setText( self.actionData['data']['obj'][i]['default-value'] )
                    layoutUsed.addWidget(textArea, i, j+shiftWidget+deltaWidget+1)
                    deltaWidget += 1

            widgetRadio = layoutUsed.itemAtPosition(i, radioSelected).widget()
            widgetRadio.setChecked(True)
            widgetRadio.setFont(fontBold)

        if nbArgument < MAX_ARGUMENT_TO_DISPLAY:
            self.mainTab.setTabEnabled(1, False)

class ActionDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Action dialog 
    """
    def __init__(self, parent, helper, actionData, owner, variables, testParams, adapterMode=False, noCancel=False):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(ActionDialog, self).__init__(parent)
        self.actionData = actionData
        self.testParams = testParams
        self.owner = owner
        self.variables = variables
        self.adapterMode = adapterMode
        self.noCancel = noCancel
        
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);
        }""")
        if self.noCancel:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Ok )
        else:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            
        self.argsWidget = BasicWidget(self.actionData, self.owner, self.variables, parent=self, testParams=self.testParams,
                                        adapterMode=self.adapterMode)

        # input
        mainLayout = QVBoxLayout()
        inputText = ""
        if "action-descr" in self.actionData['data']:
                inputText = self.actionData['data']["action-descr"]
        finalTitle = "%s" % self.actionData['data']['function']
        if len(inputText):
            finalTitle += " - %s" % inputText.lower()
        titleLabel = QLabel( finalTitle )
        font = QFont()
        font.setBold(True)
        titleLabel.setFont(font)
        
        # output
        outputText = "nothing"
        if self.actionData['data']['return-value'] == 'True':
            outputText = self.actionData['data']['return-descr']
        outputLabel = QLabel( "Output: %s" % outputText )
        font = QFont()
        font.setItalic(True)
        outputLabel.setFont(font)
        
        mainLayout.addWidget(titleLabel)
        mainLayout.addWidget(outputLabel)
        mainLayout.addWidget(self.argsWidget)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Configuration action"))

        self.resize(self.minimumSizeHint())
        self.resize(750, self.height() )

        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getValues(self):
        """
        Get values
        """
        self.argsWidget.setValues()
        return self.actionData['data']['obj']