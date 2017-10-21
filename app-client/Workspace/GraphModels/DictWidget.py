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
    from PyQt4.QtGui import (QItemDelegate, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, 
                            QFrame, QAbstractItemView, QIcon, QMessageBox, QMenu, QPushButton)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt)
except ImportError:
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QItemDelegate, QDialog, QDialogButtonBox, QVBoxLayout, 
                                QTableView, QFrame, QAbstractItemView, QMessageBox, 
                                QMenu, QPushButton)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt)
    
from Libs import QtHelper, Logger

# python 3 support
# support old variant style
# will be remove in the future
def q(v=""): 
    return QVariant(v)
if sys.version_info > (3,): 
    def q(v=""): 
        return v
        
        
import operator

try:
    import OperatorsWidget
except ImportError: # support python3
    from . import OperatorsWidget
    
DESCRIPTION_HEADERS            = ( 'Key', 'Value'  )

COL_KEY         = 0
COL_VALUE       = 1

class DictTableModel(QAbstractTableModel):
    """
    Table model for parameters
    """
    def __init__(self, parent, advancedMode=False):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        self.advancedMode = advancedMode
        self.owner = parent
        self.nbCol = len(DESCRIPTION_HEADERS)
        self.mydata = []

    def getData(self):
        """
        Return model data

        @return:
        @rtype:
        """
        return self.mydata

    def getValueRow(self, index):
        """
        Return all current values of the row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        return self.mydata[ index.row() ]

    def setDataModel(self, data):
        """
        Set model data

        @param data: 
        @type data:
        """
        self.mydata = data
        self.reset()

    def columnCount(self, qindex=QModelIndex()):
        """
        Array column number
    
        @param qindex: 
        @type qindex:

        @return:
        @rtype:
        """
        return self.nbCol

    def rowCount(self, qindex=QModelIndex()):
        """
        Array row number
    
        @param qindex: 
        @type qindex:
    
        @return:
        @rtype:
        """
        return len( self.mydata )

    def getValue(self, index):
        """
        Return current value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.column() == COL_KEY:
            return self.mydata[ index.row() ]['key']
        if index.column() == COL_VALUE:
            return self.mydata[ index.row() ]['value']

    def data(self, index, role=Qt.DisplayRole):
        """
        Cell content

        @param index: 
        @type index:

        @param role: 
        @type role:

        @return:
        @rtype:
        """
        if not index.isValid():
            return q()
        value = self.getValue(index)

        if role == Qt.DisplayRole:
            if index.column() == COL_KEY:
                if self.advancedMode:
                    if value['type'] == 'string':
                        return q( "%s('%s')" % (value['operator'], value['value']) )
                    if value['type'] == 'inputs':
                        return q( "%s(input('%s'))" % (value['operator'], value['value']) )
                    if value['type'] == 'outputs':
                        return q( "%s(output('%s'))" % (value['operator'], value['value']) )
                    if value['type'] == 'variables':
                        return q( "%s(%s)" % (value['operator'], value['value']) )
                else:
                    return q(value)
            if index.column() == COL_VALUE:
                if self.advancedMode :
                    if value['type'] == 'string':
                        return q( "%s('%s')" % (value['operator'], value['value']) )
                    if value['type'] == 'inputs':
                        return q( "%s(input('%s'))" % (value['operator'], value['value']) )
                    if value['type'] == 'outputs':
                        return q( "%s(output('%s'))" % (value['operator'], value['value']) )
                    if value['type'] == 'variables':
                        return q( "%s(%s)" % (value['operator'], value['value']) )
                else:
                    return q(value)
        # on edit
        elif role == Qt.EditRole:
            return q(value)
        
        else:
            pass
            
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Overriding method headerData

        @param section: 
        @type section:

        @param orientation: 
        @type orientation:

        @param role: 
        @type role:

        @return:
        @rtype:
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return DESCRIPTION_HEADERS[section]

        return None
        # if role != Qt.DisplayRole:
            # if role == Qt.FontRole:
                # return q()
            # else:
                # return q()
        # i_column = int(section)
        # if orientation == Qt.Horizontal:
            # return q( DESCRIPTION_HEADERS[i_column] )
        # else:
            # return q()

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        if index.column() == COL_KEY:
            self.mydata[ index.row() ]['key'] = value
        if index.column() == COL_VALUE:
            self.mydata[ index.row() ]['value'] = value
        else:
            pass

    def setData(self, index, value, role=Qt.EditRole):
        """
        Cell content change

        @param index: 
        @type index:

        @param value: 
        @type value:

        @param role: 
        @type role:

        @return:
        @rtype:
        """
        if not index.isValid():
            return False
        if not self.advancedMode:
            value = QtHelper.displayToValue( value )
        self.setValue(index, value)
        return True

    def flags(self, index):
        """
        Overriding method flags

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)


class ItemComboDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Item Combo delegate item
    """
    def __init__ (self, parent, colId):
        """
        Contructs ItemComboDelegate item delegate
        
        @param parent: 
        @type parent:

        @param colId: 
        @type colId:
        """
        QItemDelegate.__init__(self, parent)
        self.owner = parent
        self.colId = colId

    def getValue(self, index):
        """
        Return value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.isValid():
            return index.model().getValue(index)
    
    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:

        @return:
        @rtype:
        """
        if index.isValid():
            index.model().setValue(index, value)

    def getValueRow(self, index):
        """
        Returns value by row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.isValid():
            return index.model().getValueRow(index)

    def createEditor(self, parent, option, index):
        """
        Create the editor

        @param parent: 
        @type parent:

        @param option: 
        @type option:

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        value = self.getValueRow(index)

        if index.column() == self.colId:
            if self.colId == COL_KEY:
                value = value['key']
            if self.colId == COL_VALUE:
                value = value['value']
            editor = OperatorsWidget.OperatorValueDialog(self.owner, currentOperator=value)
            if editor.exec_() == QDialog.Accepted:
                ret = editor.getValue()
                index.model().setData(index, ret)

class DictValueDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Dict dialog 
    """
    def __init__(self, parent, testParams, variables, advancedMode=False ):
        """
        Operator to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(DictValueDialog, self).__init__(parent)
        self.advancedMode = advancedMode
        self.testParams = testParams
        self.variables = variables

        self.createDialog()
        self.createConnections()
        self.createActions()
        
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

        mainLayout = QVBoxLayout()
        
        self.dictTable = QTableView(self)
        self.model = DictTableModel(self, advancedMode=self.advancedMode)
        self.dictTable.setModel(self.model)
        self.dictTable.setFrameShape(QFrame.StyledPanel)
        self.dictTable.setShowGrid(True)
        self.dictTable.setGridStyle (Qt.DotLine)

        self.dictTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dictTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dictTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dictTable.verticalHeader().setVisible(False)
        self.dictTable.horizontalHeader().setHighlightSections(False)
        self.dictTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.dictTable.horizontalHeader().setStretchLastSection(True)
        self.dictTable.setColumnWidth(COL_KEY, 200)

        # delegate item on advanced mode
        if self.advancedMode:
            self.dictTable.setItemDelegateForColumn( COL_KEY, ItemComboDelegate(self, COL_KEY) )
            self.dictTable.setItemDelegateForColumn( COL_VALUE, ItemComboDelegate(self, COL_VALUE) )


        mainLayout.addWidget(self.dictTable)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Dict configuration"))

        self.setMinimumWidth(500)
        self.center()


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


    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.dictTable.customContextMenuRequested.connect(self.onPopupMenu)
        
    def getValue(self):
        """
        Return value
        """
        return self.model.getData()

    def createActions (self):
        """
        Actions defined:
         * add 
         * del
        """
        self.addAction = QtHelper.createAction(self, self.tr("&Add"), self.addKey, icon = QIcon(":/test-parameter-add.png"),
                                tip = self.tr('Add a new key') )
        self.delAction = QtHelper.createAction(self, self.tr("&Delete"), self.delKey, icon = QIcon(":/test-parameter-del.png"), 
                                tip = self.tr('Delete the selected key') )
        self.delAllAction = QtHelper.createAction(self, self.tr("&Delete All"), self.delKeys, icon = QIcon(":/test-parameter-del.png"),
                                tip = self.tr('Delete the selected key') )
    
    
    def addKey(self):
        """
        Add key
        """
        self.delAllAction.setEnabled(True)
        
        index = self.dictTable.currentIndex()
        if not index.isValid():
            row = self.model.rowCount()
        else:
            row = index.row()

        data = self.model.getData()
        
        if self.advancedMode:
            tpl =   { 'key': { 'operator': '', 'value': '', 'type': '' }, 'value': { 'operator': '', 'value': '', 'type': '' } }
        else:
            tpl =   { 'key': 'my key', 'value': 'my value' }
                
        # add data to model
        data.insert(row + 1, tpl)
        self.model.reset()

    def clear (self):
        """
        clear contents
        """
        self.model.setDataModel( [] )
    
    def delKey(self):
        """
        Delete key
        """
        # get selected proxy indexes
        indexes = self.dictTable.selectedIndexes()
        if not indexes:
            return
         
        if indexes:
            answer = QMessageBox.question(self,  self.tr("Remove"),  self.tr("Do you want to remove selected key?"), 
                    QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                self.removeValues(indexes)

    def removeValues(self, indexes):
        """
        Remove values from data

        @param indexes: 
        @type indexes:
        """
        if not indexes:
            return
        
        # extract name, name are unique
        datas = self.model.getData()
        allNames = []

        # remove duplicate index
        cleanIndexes = {}
        for index in indexes:
            if index.row() not in cleanIndexes:
                cleanIndexes[index.row()] = index
                
        #for cleanIndex in cleanIndexes.keys():
        for cleanIndex in list(cleanIndexes.keys()): # for python3 support
            allNames.append( datas[cleanIndex]['key'] )

        self.trace('Key to remove: %s' % allNames)
        for paramName in allNames:
            self.removeValue( paramName=paramName )

    def removeValue(self, paramName):
        """
        Remove one parameter according to the name passed on argument
        """
        datas = self.model.getData()
        i = None
        for i in xrange(len(datas)):
            if datas[i]['key'] == paramName:
                break
        if i is not None:
            param = datas.pop( i )
            del param
        self.model.reset()
        
    def delKeys(self):
        """
        Clear all keys
        """
        reply = QMessageBox.question(self, 
                        self.tr("Clear all keys"), self.tr("Are you sure ?"),
                        QMessageBox.Yes | QMessageBox.No 
                )
        if reply == QMessageBox.Yes:
            data = self.model.getData()
            try:
                for i in xrange(len(data)):
                    data.pop()
            except Exception as e:
                pass
            self.model.reset()
            self.delAllAction.setEnabled(False)

            
    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu(self.dictTable)
        index = self.dictTable.currentIndex()
        indexes = self.dictTable.selectedIndexes()
        if not indexes:
            self.menu.addAction( self.delAction )
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.delAllAction )
            self.menu.addSeparator()
        else:
            self.menu.addAction( self.delAction )
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.delAllAction )
            self.menu.addSeparator()

        self.menu.popup( self.mapToGlobal(pos) )

    def loadData(self, data):
        """
        Load data
        """
        if isinstance(data, dict):
            data = [data]
        self.model.setDataModel( data )
        
class DictWidget(QPushButton):
    """
    Dict widget
    """
    def __init__(self, parent, testParams, variables, advancedMode=False):
        """
        Constructor
        """
        QPushButton .__init__(self, parent)
        self.currentDict = []
        self.testParams = testParams
        self.variables = variables
        self.advancedMode = advancedMode

        self.setText("Setup...")
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
        dictDialog = DictValueDialog(self, advancedMode=self.advancedMode, testParams=self.testParams, variables=self.variables)
        dictDialog.loadData(data=self.currentDict)
        if dictDialog.exec_() == QDialog.Accepted:
            self.currentDict = dictDialog.getValue()
    
    def getCurrentDict(self):
        """
        Get current dict
        """
        return self.currentDict

    def setCurrentDict(self, dictVal):
        """
        Set current dict
        """
        self.currentDict = dictVal