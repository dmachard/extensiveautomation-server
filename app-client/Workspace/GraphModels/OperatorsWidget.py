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
Test abstract operators widget
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
    from PyQt4.QtGui import (QDialogButtonBox, QHBoxLayout, QLabel, QFont, QComboBox, 
                            QTextEdit, QButtonGroup, QRadioButton, QVBoxLayout, QPushButton, 
                            QDialog)
except ImportError:
    from PyQt5.QtGui import (QFont)
    from PyQt5.QtWidgets import (QDialogButtonBox, QHBoxLayout, QLabel, QComboBox, 
                                QTextEdit, QButtonGroup, QRadioButton, QVBoxLayout, 
                                QPushButton, QDialog)

from Libs import QtHelper, Logger

HEIGHT_TEXT_AREA            = 40
WIDTH_TEXT_AREA             = 200

OP_ANY                  = "any"
OP_EQUALS               = "equals"
OP_NOT_EQUALS           = "not equals"
OP_GREATER_THAN         = "greater than"
OP_LOWER_THAN           = "lower than"
OP_CONTAINS             = "contains"
OP_NOT_CONTAINS         = "not contains"
OP_STARTSWITH           = "startswith"
OP_ENDSWITH             = "endswith"
OP_NOT_STARTSWITH       = "not startswith"
OP_NOT_ENDSWITH         = "not endswith"
OP_REG_EX               = "reg ex"
OP_NOT_REG_EX           = "not reg ex"

OP_GREATER_EQUAL_THAN   = "greater than or equal"
OP_LOWER_EQUAL_THAN     = "lower than or equal"

LIST_CONDITIONS = [ 
                    OP_ANY,
                    OP_EQUALS, OP_NOT_EQUALS, 
                    OP_GREATER_THAN, OP_LOWER_THAN, 
                    OP_CONTAINS, OP_NOT_CONTAINS, 
                    OP_STARTSWITH, OP_ENDSWITH, 
                    OP_NOT_STARTSWITH, OP_NOT_ENDSWITH,
                    OP_REG_EX, OP_NOT_REG_EX,
                    OP_GREATER_EQUAL_THAN, OP_LOWER_EQUAL_THAN,
                  ]

LIST_CONDITIONS_LITE = [ 
                    OP_EQUALS, OP_NOT_EQUALS, 
                    OP_GREATER_THAN, OP_LOWER_THAN, 
                    OP_CONTAINS, OP_NOT_CONTAINS, 
                     OP_STARTSWITH, OP_ENDSWITH, 
                    OP_NOT_STARTSWITH, OP_NOT_ENDSWITH, 
                    OP_GREATER_EQUAL_THAN, OP_LOWER_EQUAL_THAN,
                  ]
        
class OperatorValueDialog(QtHelper.EnhancedQDialog):
    """
    Operator dialog 
    """
    def __init__(self, parent, currentOperator={}, liteMode=False):
        """
        Operator to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(OperatorValueDialog, self).__init__(parent)
        self.parentWidget = parent
        self.liteMode = liteMode
        self.currentOperator = currentOperator

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
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QHBoxLayout()
        main2Layout = QHBoxLayout()

        titleLabel = QLabel( self.currentOperator['operator'] )
        font = QFont()
        font.setBold(True)
        titleLabel.setFont(font)
        
        self.opType = QComboBox( )
        if not self.liteMode:
            for i in xrange(len(LIST_CONDITIONS)):
                self.opType.addItem(LIST_CONDITIONS[i].title())
                if self.currentOperator['operator'] == LIST_CONDITIONS[i].title():
                    self.opType.setCurrentIndex(i)
        else:
            for i in xrange(len(LIST_CONDITIONS_LITE)):
                self.opType.addItem(LIST_CONDITIONS_LITE[i].title())
                if self.currentOperator['operator'] == LIST_CONDITIONS_LITE[i].title():
                    self.opType.setCurrentIndex(i)

        main2Layout.addWidget(titleLabel)
        main2Layout.addWidget(self.opType)

        if not self.liteMode:
            self.textValue = QTextEdit()
            self.textValue.setFixedHeight(HEIGHT_TEXT_AREA)  
            self.textValue.setMinimumWidth(WIDTH_TEXT_AREA)    
            
            radioGroup=QButtonGroup(self)
            self.strRadioButton  = QRadioButton( "string" )
            self.strRadioButton.setChecked(True)
            self.inRadioButton  = QRadioButton( "inputs" )
            self.outRadioButton  = QRadioButton( "outputs" )
            self.varRadioButton  = QRadioButton( "variables" )

            radioGroup.addButton( self.strRadioButton )
            radioGroup.addButton( self.inRadioButton )
            radioGroup.addButton( self.outRadioButton )
            radioGroup.addButton( self.varRadioButton )

            self.inputsCombo = QComboBox( )
            for inpt in self.parentWidget.getInputs(): self.inputsCombo.addItem(inpt['name'])

            self.outputsCombo = QComboBox( )
            for inpt in self.parentWidget.getOutputs(): self.outputsCombo.addItem(inpt['name'])

            self.variablesCombo = QComboBox( )
            self.variablesCombo.addItems(self.parentWidget.variables)


            if self.currentOperator['type'] == 'string':
                self.strRadioButton.setChecked(True)
                self.textValue.setText(self.currentOperator['value'])

            if self.currentOperator['type'] == 'inputs':
                self.inRadioButton.setChecked(True)
                for x in xrange(self.inputsCombo.count()):
                    if self.inputsCombo.itemText(x) == self.currentOperator['value']:
                        self.inputsCombo.setCurrentIndex(x) 

            if self.currentOperator['type'] == 'outputs':
                self.outRadioButton.setChecked(True)
                for x in xrange(self.outputsCombo.count()):
                    if self.outputsCombo.itemText(x) == self.currentOperator['value']:
                        self.outputsCombo.setCurrentIndex(x) 

            if self.currentOperator['type'] == 'variables':
                self.varRadioButton.setChecked(True)
                for x in xrange(self.variablesCombo.count()):
                    if self.variablesCombo.itemText(x) == self.currentOperator['value']:
                        self.variablesCombo.setCurrentIndex(x) 

            mainLayout.addWidget(self.strRadioButton)
            mainLayout.addWidget(self.textValue)

            mainLayout.addWidget(self.inRadioButton)
            mainLayout.addWidget(self.inputsCombo)

            mainLayout.addWidget(self.outRadioButton)
            mainLayout.addWidget(self.outputsCombo)

            mainLayout.addWidget(self.varRadioButton)
            mainLayout.addWidget(self.variablesCombo)

        finalLayout = QVBoxLayout()
        finalLayout.addLayout(main2Layout)
        finalLayout.addLayout(mainLayout)
        finalLayout.addWidget(self.buttonBox)

        self.setLayout(finalLayout)

        self.setWindowTitle(self.tr("Operators configuration"))

        self.setMinimumWidth(500)
        self.center()
        
    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getValue(self):
        """
        Return value
        """
        self.currentOperator['operator'] = unicode( self.opType.currentText() )

        if not self.liteMode:

            if self.currentOperator['operator'].lower() == OP_ANY:
                self.currentOperator['type'] = 'string'
                self.currentOperator['value'] = ''
            else:
                if self.strRadioButton.isChecked():
                    self.currentOperator['type'] = 'string'
                    self.currentOperator['value'] = unicode( self.textValue.toPlainText() )

                if self.inRadioButton.isChecked():
                    self.currentOperator['type'] = 'inputs'
                    self.currentOperator['value'] = unicode( self.inputsCombo.currentText() )

                if self.outRadioButton.isChecked():
                    self.currentOperator['type'] = 'outputs'
                    self.currentOperator['value'] = unicode( self.outputsCombo.currentText() )

                if self.varRadioButton.isChecked():
                    self.currentOperator['type'] = 'variables'
                    self.currentOperator['value'] = unicode( self.variablesCombo.currentText() )

        return self.currentOperator
        

class OperatorsWidget(QPushButton):
    """
    Dict widget
    """
    def __init__(self, parent, testParams, variables, liteMode=False):
        """
        Constructor
        """
        QPushButton .__init__(self, parent)
        if liteMode:
            self.currentOp = { 'operator': 'undefined', 'value': '', 'type': 'string' }
        else:
            self.currentOp = { 'operator': '', 'value': '', 'type': 'string' }
        self.parentWidget = parent
        self.testParams = testParams
        self.variables = variables
        self.liteMode = liteMode

        self.setText("Undefined")
        self.createConnections()

    def getInputs(self):
        """
        Get test inputs 
        """
        return self.testParams.parameters.table().model.getData()

    def getOutputs(self):
        """
        Get test outputs 
        """
        return self.testParams.parametersOutput.table().model.getData()

    def createConnections(self):
        """
        Create connection
        """
        self.clicked.connect(self.onButtonClicked)
    
    def onButtonClicked(self):
        """
        On button clicked
        """
        opDialog = OperatorValueDialog(self, currentOperator=self.currentOp, liteMode=self.liteMode)
        if opDialog.exec_() == QDialog.Accepted:
            self.currentOp = opDialog.getValue()
            self.setText("%s" % self.currentOp['operator'] )
    
    def setCurrentOperator(self, operatorVal):
        """
        Set the current operator
        """
        self.currentOp = operatorVal
        self.setText("%s" % self.currentOp['operator'] )

    def currentOperator(self):
        """
        Returns the current operator
        """
        return self.currentOp