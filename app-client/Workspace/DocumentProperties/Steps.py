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
Test abstract steps table
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QColor, QItemDelegate, QDialog, QLineEdit, QDialogButtonBox, 
                            QLabel, QGridLayout, QRadioButton, QTextEdit, QComboBox, QVBoxLayout, 
                            QTableView, QSortFilterProxyModel, QFrame, QAbstractItemView, QIcon, 
                            QMenu, QMessageBox, QWidget, QToolBar)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QSize)
except ImportError:
    from PyQt5.QtGui import (QColor, QIcon)
    from PyQt5.QtWidgets import (QItemDelegate, QDialog, QLineEdit, QDialogButtonBox, QLabel, 
                                QGridLayout, QRadioButton, QTextEdit, QComboBox, QVBoxLayout, 
                                QTableView, QFrame, QAbstractItemView, 
                                QMenu, QMessageBox, QWidget, QToolBar)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QSize,
                              QSortFilterProxyModel)
    
from Libs import QtHelper, Logger


def q(v=""):
    """
    Return the value argument without do anything
    Only to support python 2.x and python 3.x
    
    @param v: the value to convert
    @type v: string
    """
    if sys.version_info > (3,): 
        return v
    else:
        return QVariant(v)
        
import operator

import Workspace.Helper as Helper



DESCRIPTION_HEADERS            = ( 'Id', 'Summary'  )

COL_ID_STEP = 0
COL_SUMMARY_STEP = 1

try:
    xrange
except NameError: # support python3
    xrange = range
    
class DescriptionTableModel(QAbstractTableModel):
    """
    Table model for parameters
    """
    def __init__(self, parent):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
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
        # self.reset()
        if sys.version_info > (3,):
            self.beginResetModel()
            self.endResetModel()
        else:
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
        if index.column() == COL_ID_STEP:
            self.mydata[ index.row() ]['id'] = "%s" % (index.row() + 1)
            return "#%s" % (index.row() + 1)

        elif index.column() == COL_SUMMARY_STEP:
            return self.mydata[ index.row() ]['summary']['value']
        else:
            pass

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

        if role == Qt.TextAlignmentRole:
            if index.column() == COL_ID_STEP:
                return Qt.AlignCenter

        if role == Qt.ToolTipRole:
            if index.column() == COL_SUMMARY_STEP:
                return q(value)

        if role == Qt.DisplayRole:
            if index.column() == COL_ID_STEP:
                return q(value)
            if index.column() == COL_SUMMARY_STEP:
                return q(value)

        if role == Qt.BackgroundColorRole:
            return q( QColor("#F2FBFC") )

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

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        self.owner.DataChanged.emit()

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
        if index.column() == COL_ID_STEP:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
    
class StepSummaryDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Name delegate item
    """
    def __init__ (self, parent ):
        """
        Contructs NameDelegate item delegate
        
        @param parent: 
        @type parent:

        @param items_: 
        @type items_:

        @param col_: 
        @type col_:
        """
        QItemDelegate.__init__(self, parent)
        self.owner = parent

    def getValue(self, index):
        """
        Return value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValue(sourceIndex)

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
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            proxyIndex.model().sourceModel().setValue(sourceIndex, value)

    def getValueRow(self, index):
        """
        Return value by row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValueRow(sourceIndex)

    def createEditor(self, parent, option, index):
        """
        Create the editor

        @param parent: 
        @type parent:

        @param option: 
        @type option:

        @param index: 
        @type index:

        @return: editor delegate
        @rtype:
        """
        value = self.getValueRow(index)
        if index.column() == COL_SUMMARY_STEP:
            helpFramework = self.owner.getHelpFramework()
            stepDialog = StepDialog(helpFramework)
            stepDialog.setCurrentData(value)
            if stepDialog.exec_() == QDialog.Accepted:
                stepParams = stepDialog.getValues()
                sourceIndex = self.owner.proxyModel.mapToSource( index )
                index.model().sourceModel().mydata[ sourceIndex.row() ] = stepParams

                self.owner.DataChanged.emit()

    def setModelData(self, editor, model, index):
        """
        Accessor to set the model of data

        @param editor: 
        @type editor:

        @param model: 
        @type model:

        @param index: 
        @type index:
        """
        if type(editor) == QLineEdit:
            qvalue = editor.text()
        value = QtHelper.displayToValue( q(qvalue) )
        self.setValue(index, value)

class StepDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Step dialog 
    """
    def __init__(self, stepData, parent=None, stepId=0):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(StepDialog, self).__init__(parent)
        self.stepData = stepData
        self.stepId = stepId

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

        self.stepIdLabel = QLabel("%s" % self.stepId)
        stepTitleLayout = QGridLayout()

        # mandatory args
        self.argsLayout = QGridLayout()
        for i in xrange(len(self.stepData['obj'])):
            self.argsLayout.addWidget(QLabel( self.stepData['obj'][i]['name']), i, 0)
            typeParam  = QRadioButton( self.stepData['obj'][i]['type'])
            typeParam.setEnabled(False)
            self.argsLayout.addWidget(typeParam, i, 1)
            if self.stepData['obj'][i]['type'] == 'string':
                typeParam.setChecked(True)
                self.argsLayout.addWidget(QTextEdit( ), i, 2)
            if self.stepData['obj'][i]['type'] == "boolean":
                boolCombo = QComboBox( )
                valBool = [ "True", "False" ]
                boolCombo.addItems(valBool)
                boolCombo.setEnabled(False) # feature not yet available in abstract mode
                typeParam.setChecked(True)
                self.argsLayout.addWidget(boolCombo, i, 2)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(stepTitleLayout)
        mainLayout.addLayout(self.argsLayout)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Step configuration"))
        self.resize(450, 250)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def setCurrentData(self, currentData):
        """
        Set current data
        """
        self.stepId = currentData['id']
        self.stepIdLabel.setText( "%s" % currentData['id'])

        for key, val in currentData.items():
            if isinstance(val, dict):
                for i in xrange(len(self.stepData['obj'])):
                    widgetKey = self.argsLayout.itemAtPosition(i, 0).widget()
                    widgetKeyName = unicode(widgetKey.text())
                    if  widgetKeyName == key:
                        widgetVal = self.argsLayout.itemAtPosition(i, 2)
                        if widgetVal is not None:
                            widgetVal = widgetVal.widget()
                            if val['type'] == 'string' and isinstance(widgetVal, QTextEdit):
                                widgetVal.setText(val['value'])
                            if val['type'] == 'boolean' and isinstance(widgetVal, QComboBox):
                                if val['value'] == "True": 
                                    widgetVal.setCurrentIndex(0)
                                else:
                                    widgetVal.setCurrentIndex(1)
    def getValues(self):
        """
        Get values
        """
        ret = { }
        for i in xrange(len(self.stepData['obj'])):
            widgetKey = self.argsLayout.itemAtPosition(i, 0).widget()
            widgetKeyName = unicode(widgetKey.text())
            if  widgetKeyName not in ret:
                ret[widgetKeyName] = {}

            widgetVal = self.argsLayout.itemAtPosition(i, 2)
            if widgetVal is not None:
                widgetVal = widgetVal.widget()
                if isinstance(widgetVal, QTextEdit):
                    ret[widgetKeyName]['type'] = self.stepData['obj'][i]['type']
                    ret[widgetKeyName]['value'] = unicode( widgetVal.toPlainText() )
                if isinstance(widgetVal, QComboBox):
                    ret[widgetKeyName]['type'] = "boolean"
                    ret[widgetKeyName]['value'] = str(widgetVal.currentText())
        return ret

class StepsTableView(QTableView):
    """
    Steps table view
    """
    DataChanged = pyqtSignal() 
    def __init__(self, parent, helper):
        """
        Description table view constructor
        """
        QTableView.__init__(self, parent)
        self.helper = helper
        self.createWidgets()
        self.createConnections()
        self.createActions()

    def createWidgets (self):
        """
        Create qt widgets
        """
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setDynamicSortFilter(True)

        self.model = DescriptionTableModel(self)
        self.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.model)

        self.setFrameShape(QFrame.StyledPanel)
        self.setShowGrid(True)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)

        self.setItemDelegateForColumn( COL_SUMMARY_STEP, StepSummaryDelegate(self) )

        self.setColumnWidth(COL_ID_STEP, 45)

    def createConnections (self):
        """
        Create qt connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)
        self.clicked.connect( self.onAbstractItemClicked)  

    def createActions (self):
        """
        Qt actions
        """
        self.addAction = QtHelper.createAction(self, self.tr("&Add"), self.addStep, icon = QIcon(":/step-add.png"),
                                                    tip = self.tr('Add a new step') )
        self.delAction = QtHelper.createAction(self, self.tr("&Delete"), self.deleteAction, icon = QIcon(":/step-del.png"),
                                                    tip = self.tr('Delete the selected step'))
        self.delAllAction = QtHelper.createAction(self, self.tr("&Delete All"), self.clearItems, icon = QIcon(":/test-parameter-clear.png"),
                                                    tip = self.tr('Delete all steps'))
        
        # set default actions
        self.delAction.setEnabled(False)
        self.delAllAction.setEnabled(False)
        
    def onAbstractItemClicked(self):
        """
        Called on item clicked
        """
        indexes = self.selectedIndexes()
        if not indexes:
            self.delAction.setEnabled(False)
        else:
            self.delAction.setEnabled(True)
            
    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu(self)
        index = self.currentIndex()
        indexes = self.selectedIndexes()
        if not indexes:
            self.delAction.setEnabled(False)
        
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
        else:
            self.delAction.setEnabled(True)
            
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
        self.menu.popup( self.mapToGlobal(pos) )

    def getHelpFramework(self):
        """
        Get help from framework
        """
        self.helper = Helper.instance()
        val = self.helper.helpFramework(moduleName='TestExecutor', className='TestCase', functionName='addStep')
        if val is None:
            val = {}
            val['obj'] = {}
        else:
            desc = val['desc'].strip()
            desc_splitted = desc.splitlines()
            
            val['return-value'] = False
            params = []
            param = {}
            for line in desc_splitted:
                line = line.strip() 
                if line.startswith('@param '):
                    paramName = line.split(':', 1)[0].split('@param ')[1].strip()
                    param['name'] = paramName
                elif line.startswith('@type '):
                    paramType = line.split(':', 1)[1].strip()
                    param['type'] = paramType
                    params.append( param )
                    param = {}
                elif line.startswith('@return'):
                    val['return-value'] = True
                else:   
                    pass

            val['obj'] = params
        return val

    def addStep(self):
        """
        Add step
        """
        helpFramework = self.getHelpFramework()
        stepDialog = StepDialog(helpFramework) #, stepId=stepId)
        if stepDialog.exec_() == QDialog.Accepted:
            stepParams = stepDialog.getValues()
            self.insertItem(stepParams=stepParams)
                                       
    def insertItem(self, stepParams):
        """
        Insert item
        """
        indexes = self.selectedIndexes()
        if not len(indexes):
            row = self.model.rowCount()
        else:
            index = self.currentIndex()
            row = index.row()
        data = self.model.getData()

        # add data to model
        stepParams['id'] = "%s" % (len(data) + 1)
        data.insert(row + 1, stepParams)

        if sys.version_info > (3,): 
            self.model.beginResetModel()
            self.model.endResetModel()
        else:
            self.reset()
            
        self.delAllAction.setEnabled(True)
        
        self.setData()

    def deleteAction(self):
        """
        Delete action
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return

        # map proxy indexes to source
        sourceIndexes = []
        for proxyIndex in indexes:
            if not proxyIndex.isValid():
                return
            else:
                sourceIndexes.append( self.proxyModel.mapToSource( proxyIndex ) )
        
        if sourceIndexes:
            answer = QMessageBox.question(self,  self.tr("Remove"),  
                                            self.tr("Do you want to remove the selection?"), 
                                            QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                self.removeValues(sourceIndexes)

    def removeValues(self, indexes):
        """
        Remove values from data

        @param indexes: 
        @type indexes:
        """
        if not indexes:
            return
        
        # data from model
        datas = self.model.getData()

        # remove duplicate index
        cleanIndexes = {}
        for index in indexes:
            if index.row() not in cleanIndexes:
                cleanIndexes[index.row()] = index

        for cleanIndex in list(cleanIndexes.keys()): # for python3 support
            datas.pop(cleanIndex)

        if sys.version_info > (3,): 
            self.model.beginResetModel()
            self.model.endResetModel()
        else:
            self.reset()
            
        self.setData( signal = True )

    def setSteps(self, steps):
        """
        Set steps
        """
        self.model.setDataModel( steps )
        self.setData( signal = False )
        
    def clearItems(self):
        """
        Clear all items
        """
        reply = QMessageBox.question(self, self.tr("Clear all steps"), 
                                        self.tr("Are you sure ?"),
                                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            data = self.model.getData()
            try:
                for i in xrange(len(data)):
                    data.pop()
            except Exception as e:
                pass

            if sys.version_info > (3,): 
                self.model.beginResetModel()
                self.model.endResetModel()
            else:
                self.reset()
                
            self.setData()
            
            self.delAllAction.setEnabled(False)
            self.delAction.setEnabled(False)
            
    def clear (self):
        """
        clear contents
        """
        self.model.setDataModel( [] )

    def setData(self, signal = True):
        """
        Set table data

        @param signal: 
        @type signal: boolean
        """
        if signal: self.DataChanged.emit()

class StepsQWidget(QWidget, Logger.ClassLogger):
    """
    Steps widget
    """
    def __init__(self, parent, helper=None):
        """
        Contructs Parameters Widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.helper = helper

        self.createWidgets()
        self.createToolbar()
        self.createConnections()

    def createToolbar(self):
        """
        Probe
        """
        self.dockToolbar.setObjectName("Document Properties toolbar probes")
        self.dockToolbar.addAction(self.table().addAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.table().delAction)
        self.dockToolbar.addAction(self.table().delAllAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()

        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border

        self.stepsTable = StepsTableView(self, helper=self.helper)

        layout.addWidget(self.stepsTable)
        layout.addWidget(self.dockToolbar)
        
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def createConnections(self):
        """
        Create qt connections
        """
        pass

    def clear(self):
        """
        Clear all widget
        """
        self.stepsTable.clear()

    def table(self):
        """
        Return the probes table view
        """
        return self.stepsTable