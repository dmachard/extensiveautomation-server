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
    from PyQt4.QtGui import (QIcon, QColor, QItemDelegate, QMessageBox, QDialog, 
                            QLineEdit, QTableView, QSortFilterProxyModel, QFrame, 
                            QAbstractItemView, QMenu, QWidget, QVBoxLayout, QToolBar)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon, QColor)
    from PyQt5.QtWidgets import (QItemDelegate, QMessageBox, QDialog, QLineEdit, QTableView, 
                                QFrame, QAbstractItemView, QMenu, QWidget, 
                                QVBoxLayout, QToolBar)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, 
                              QSize, QSortFilterProxyModel)
    
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
import Workspace.GraphModels.GenericConfigDialog as GenericConfigDialog

DESCRIPTION_HEADERS            = ( 'Id', 'Action'  )

COL_ID_ACTION = 0
COL_SUMMARY_ACTION = 1

ACTION_ADAPTER             = "TestCase"

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
        if index.column() == COL_ID_ACTION:
            #return index.row() + 1
            return "#%s" % (index.row() + 1)
            #return self.mydata[ index.row() ]['id']
        elif index.column() == COL_SUMMARY_ACTION:
            # old stype to display text
            if 'display' in self.mydata[ index.row() ]:
                return self.mydata[ index.row() ]['display']
            else:
                actionType = self.mydata[ index.row() ]['action']

                if actionType == ACTION_ADAPTER:
                    funcName = self.mydata[ index.row() ]['data']['function']
                    return  "%s" % (funcName)

                else:
                    return "unknonw action type: %s" % actionType
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
            #return q()
            return ''
        value = self.getValue(index)

        if role == Qt.TextAlignmentRole:
            if index.column() == COL_ID_ACTION:
                return Qt.AlignCenter

        if role == Qt.ToolTipRole:
            if index.column() == COL_SUMMARY_ACTION:
                return q(value)

        if role == Qt.DisplayRole:
            if index.column() == COL_ID_ACTION:
                return q(value)
            if index.column() == COL_SUMMARY_ACTION:
                return q(value)
        
        if role == Qt.DecorationRole:
            if index.column() == COL_SUMMARY_ACTION:
                if 'return-value' in self.mydata[ index.row() ]['data']:
                    if self.mydata[ index.row() ]['data']['return-value'] == 'True':
                        pass

        if role == Qt.BackgroundColorRole:
            if self.mydata[ index.row() ]['action'] == ACTION_ADAPTER:
                return q( QColor("#DFFFD1") )
            else:
                return q( QColor("#FFFFFF") )

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
        if index.column() == COL_ID_ACTION:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)

class AdapterDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Action delegate item
    """
    def __init__ (self, parent ):
        """
        Contructs Action item delegate
        
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
        if index.column() == COL_SUMMARY_ACTION:

            # edit only if params exists on the function
            if not len(value['data']['obj']):
                QMessageBox.information(self.owner, "Configuration action", "No argument for this action")
            else:
                actionDialog = GenericConfigDialog.ActionDialog(self, self.owner.helper, value, owner=self.owner, variables=[], 
                                                    adapterMode=True,testParams=self.owner.testParams)

                if actionDialog.exec_() == QDialog.Accepted:
                    actionParams = actionDialog.getValues()
                    value['data']['obj'] = actionParams
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().mydata[ sourceIndex.row() ] = value

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

class AdaptersTableView(QTableView):
    """
    Adapters table view
    """
    DataChanged = pyqtSignal() 
    def __init__(self, parent, helper, testParams, testDescrs):
        """
        Description table view constructor
        """
        QTableView.__init__(self, parent)

        self.__parent = parent
        self.helper = helper
        self.testParams = testParams
        self.testDescrs = testDescrs
        self.createWidgets()
        self.createConnections()
        self.createActions()

    def getAgents(self):
        """
        Get test agents 
        """
        return self.testParams.agents.table().model.getData()
        
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
        self.setGridStyle (Qt.DotLine)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)

        self.setItemDelegateForColumn( COL_SUMMARY_ACTION, AdapterDelegate(self) )

        self.setColumnWidth(COL_ID_ACTION, 45)

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
        self.delAction = QtHelper.createAction(self, self.tr("&Delete"), self.deleteAction, 
                                        icon = QIcon(":/adapters-del.png"), tip = self.tr('Delete the selected adapter'))
        self.delAllAction = QtHelper.createAction(self, self.tr("&Delete All"), self.clearItems,
                                        icon = QIcon(":/test-parameter-clear.png"), tip = self.tr('Delete all adapters'))
        
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
            answer = QMessageBox.question(self,  self.tr("Remove"),  self.tr("Do you want to remove the selection?"), 
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

        self.model.beginResetModel()
        self.model.endResetModel()
        self.setData( signal = True )
    
    def getHelpAdapters(self):
        """
        Return the help of all adapters according to the current
        version of the test
        """
        testDescrs = self.testDescrs.table().model.getData()
        currentAdpVersion = None
        for descr in testDescrs:
            if descr['key'] == 'adapters':
                currentAdpVersion = descr['value']
                break
        return Helper.instance().helpAdapters(name=currentAdpVersion)
        
    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu(self)
        index = self.currentIndex()
        indexes = self.selectedIndexes()

        adapters = self.getHelpAdapters()
        
        # adapters
        adpsMenu = QMenu("Add", self)
        if adapters is not None:
            for adp in adapters:

                adpMenu = QMenu(adp['name'], self)
                adpsMenu.addMenu(adpMenu)
                
                for cls in adp['classes']:

                    # extract __init__ function only
                    fct = None
                    for fct in cls['functions']:
                        if fct['name'] == '__init__':
                            break
                    
                    if fct is not None:
                        argsFct = self.parseDocString(docstring=fct['desc'])
                        argsFct['function'] = "%s::%s" % (adp['name'],cls['name'])
                        argsFct['main-name'] = "%s" % adp['name']
                        argsFct['sub-name'] = "%s" % cls['name']
                        if 'default-args' in fct:
                            self.addDefaultValues(defaultValues=fct['default-args'], currentFunction=argsFct)
                        
                        adpMenu.addAction(QtHelper.createAction(self, cls['name'], self.addAdapter, cb_arg=argsFct ))    
            
        if not indexes:
            self.delAction.setEnabled(False)

            self.menu.addAction( self.delAction )
            self.menu.addSeparator()
            self.menu.addMenu( adpsMenu )
            self.menu.addSeparator()
            
        else:
            self.delAction.setEnabled(True)

            self.menu.addAction( self.delAction )
            self.menu.addSeparator()
            self.menu.addMenu( adpsMenu )
            self.menu.addSeparator()
             
        self.menu.popup( self.mapToGlobal(pos) )

    def addDefaultValues(self, defaultValues, currentFunction):
        """
        Add default values
        """
        for curArg in currentFunction['obj']:
            for k,v in defaultValues:
                if k == curArg['name']:
                    curArg['advanced'] = "True"
                    if curArg['type'] in ['strconstant', 'intconstant']:
                        curArg['default-value'] =  self.parseConstant(descr=curArg['descr'])
                    else:
                        curArg['default-value'] = unicode(v)

    def parseDocString(self, docstring):
        """
        Parse doc string
        """
        val = {}

        desc = docstring.strip()
        desc_splitted = desc.splitlines()
        
        val['return-value'] = "False"

        params = []
        param = {}
        for line in desc_splitted:
            line = line.strip() 
            if line.startswith('@param '):
                paramName = line.split(':', 1)[0].split('@param ')[1].strip()
                paramDescr = line.split(':', 1)[1].strip()
                param['name'] = paramName
                param['value'] = ''
                param['descr'] = paramDescr
                param['selected-type'] = ''
                param['advanced'] = "False"
            elif line.startswith('@type '):
                paramType = line.split(':', 1)[1].strip()
                param['type'] = paramType
                params.append( param )
                param = {}
            elif line.startswith('@return'):
                val['return-value'] = "True"
                val['return-descr'] = line.split(':', 1)[1].strip()
            else:   
                pass

        val['obj'] = params
        return val

    def parseConstant(self, descr):
        """
        Parse constant
        """
        tmpvals = descr.split("|")
        nameConstant = ''
        for zz in xrange(len(tmpvals)):
            if '(default)' in tmpvals[zz]:
                nameConstant = tmpvals[zz].split('(default)')[0].strip()
        return nameConstant 

    def addAdapter(self, fctParams):
        """
        Add testcase function
        """ 
        actionId = self.getActionId()
        tpl = { 'action': ACTION_ADAPTER,  'data': fctParams }
        self.insertItem(actionParams=tpl)

    def getActionId(self):
        """
        Return action Id
        """
        data = self.model.getData()
        actionId = len(data) + 1
        return actionId

    def insertItem(self, actionParams):
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
        data.insert(row + 1, actionParams)
        # self.model.reset()
        self.model.beginResetModel()
        self.model.endResetModel()
        
        # open properties on adding, workaround to fix an error (bad agent type)
        actionDialog = GenericConfigDialog.ActionDialog(self, self.helper, actionParams, owner=self, variables=[], 
                                    adapterMode=True,testParams=self.testParams, noCancel=True)
        actionDialog.exec_()
        newActionParams = actionDialog.getValues()
        data[row]['data']['obj'] = newActionParams
      
        self.delAllAction.setEnabled(True)

        self.setData()

    def setAdapters(self, adapters):
        """
        Set adapters
        """
        self.model.setDataModel( adapters )
        self.setData( signal = False )
    
    def clearItems(self):
        """
        Clear all items
        """
        reply = QMessageBox.question(self, self.tr("Clear all adapters"), self.tr("Are you sure ?"),
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            data = self.model.getData()
            try:
                for i in xrange(len(data)):
                    data.pop()
            except Exception as e:
                pass
            # self.model.reset()
            self.model.beginResetModel()
            self.model.endResetModel()
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

class AdaptersQWidget(QWidget, Logger.ClassLogger):
    """
    Adapters widget
    """
    def __init__(self, parent, helper=None, testParams=None, testDescrs=None):
        """
        Contructs Parameters Widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.helper = helper
        self.testParams = testParams
        self.testDescrs = testDescrs

        self.createWidgets()
        self.createToolbar()
        self.createConnections()

    def createToolbar(self):
        """
        Probe
        """
        self.dockToolbar.setObjectName("Document Properties toolbar probes")
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

        self.adaptersTable = AdaptersTableView(self, helper=self.helper, testParams=self.testParams, testDescrs=self.testDescrs)

        layout.addWidget(self.adaptersTable)
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
        self.adaptersTable.clear()

    def table(self):
        """
        Return the probes table view
        """
        return self.adaptersTable