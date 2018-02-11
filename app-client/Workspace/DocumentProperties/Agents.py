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
This module handles agents parameters in test properties
Based on a table view
"""

import sys

    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    from PyQt4.QtGui import (QFont, QItemDelegate, QLineEdit, QComboBox, QAbstractItemDelegate, 
                            QDialog, QLabel, QHBoxLayout, QTextEdit, QDialogButtonBox, QVBoxLayout, 
                            QTableView, QDrag, QAbstractItemView, QFrame, QApplication, QIcon, 
                            QMenu, QMessageBox, QWidget, QToolBar)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, 
                            QMimeData, QSize)
    if sys.version_info < (3,):
        from PyQt4.QtCore import (QString)
except ImportError:
    from PyQt5.QtGui import (QFont, QDrag, QIcon)
    from PyQt5.QtWidgets import (QItemDelegate, QLineEdit, QComboBox, QAbstractItemDelegate, 
                                QDialog, QLabel, QHBoxLayout, QTextEdit, QDialogButtonBox, 
                                QVBoxLayout, QTableView, QAbstractItemView, QFrame, QApplication, 
                                QMenu, QMessageBox, QWidget, QToolBar)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, 
                            QMimeData, QSize)
                            
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

import ServerExplorer.Agents as ServerAgents

import Settings
import UserClientInterface as UCI
import Workspace

import operator
import pickle

COL_ID              =   0
COL_NAME            =   1
COL_TYPE            =   2
COL_VALUE           =   3
COL_DESCRIPTION     =   4

#NB_COL              =   3

HEADERS              = ( 'Id', 'Name',  'Type', 'Value', 'Description' )

try:
    xrange
except NameError: # support python3
    xrange = range
    
class AgentsTableModel(QAbstractTableModel, Logger.ClassLogger):
    """
    Agents table model
    """
    def __init__(self, parent):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        self.owner = parent
        self.nbCol = len(HEADERS)
        self._data = []

    def getData(self):
        """
        Return model data

        @return:
        @rtype:
        """
        return self._data

    def getValueRow(self, index):
        """
        Return all current values of the row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        return self._data[ index.row() ]

    def setDataModel(self, data):
        """
        Set model data

        @param data: 
        @type data:
        """
        self._data = data
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
        return len( self._data )
  
    def getValue(self, index):
        """
        Return current value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.column() == COL_ID:
            return index.row() + 1
        elif index.column() == COL_NAME:
            return self._data[ index.row() ]['name']
        elif index.column() == COL_VALUE:
            return self._data[ index.row() ]['value']
        elif index.column() == COL_TYPE:
            return self._data[ index.row() ]['type']
        elif index.column() == COL_DESCRIPTION:
            return self._data[ index.row() ]['description']
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
        if role == Qt.ToolTipRole:
            if index.column() == COL_VALUE:
                return q(value)
        if role == Qt.FontRole:
            if index.column() == COL_NAME:
                font = QFont()
                font.setBold(True)
                return q(font)
            if index.column() == COL_DESCRIPTION:
                font = QFont()
                font.setItalic(True)
                return q(font)
        if role == Qt.DisplayRole:
            if index.column() == COL_VALUE:
                if len(value) > 25:
                    return q( "%s [...]" % value[:25])
                else:
                    return q(value)
            elif index.column() == COL_DESCRIPTION:
                lines = value.splitlines()
                if len(lines) > 1:
                    return q( "%s [...]" % lines[0])
                else:
                    return q(value)
            else:
                return q(value)
        elif role == Qt.EditRole:
            return q(value)
    
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
            return HEADERS[section]

        return None

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        dataChanged = False
        if index.column() == COL_NAME:
            orig_ = self._data[ index.row() ]['name']
            name_ = self.checkName( index.row(), value)
            self._data[ index.row() ]['name'] = name_
            if orig_ != name_:
                dataChanged = True
        elif index.column() == COL_VALUE:
            orig_ = self._data[ index.row() ]['value']
            self._data[ index.row() ]['value'] = value
            if orig_ != value:
                dataChanged = True
        elif index.column() == COL_TYPE:
            orig_ = self._data[ index.row() ]['type']
            self._data[ index.row() ]['type'] = value
            if orig_ != value:
                dataChanged = True
        elif index.column() == COL_DESCRIPTION:
            orig_ = self._data[ index.row() ]['description']
            self._data[ index.row() ]['description'] = value
            if orig_ != value:
                dataChanged = True
                self.owner.setData(signal=False) # resize column
        self._data.sort(key=operator.itemgetter('name'))
        self.owner.adjustColumns()      
        if dataChanged:
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
        if index.column() in [ COL_ID, COL_TYPE ]:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
    
    def checkName (self, row, name ):
        """
        Check name

        @param row: 
        @type row:

        @param name: 
        @type name:

        @return:
        @rtype:
        """
        sav = self._data[row]['name']
        
        if not len(name): # issue 211
            return sav

        for it in self._data:
            if it['name'] == name.upper():
                return sav
        if name.isdigit():
            return sav
        
        if name[0] in [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', '-' ]:
            return sav
        return name.upper() 

class NameDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Delegate items for name
    """
    def __init__ (self, parent, col_ ):
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
        self.col_ = col_

    def getValue(self, index):
        """
        Get value

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
        Get value row

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
        value = self.getValue(index)
        if index.column() == self.col_:
            editor = QLineEdit(parent)
            return editor
        return QItemDelegate.createEditor(self, parent, option, index)

    def setModelData(self, editor, model, index):
        """
        Accessor to set data in model

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

class ComboValueDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Delegate items for combo value
    """
    def __init__ (self, parent, col_ ):
        """
        Contructs ComboValueDelegate item delegate
        
        @param parent: 
        @type parent:

        @param items_: 
        @type items_:

        @param col_: 
        @type col_:
        """
        QItemDelegate.__init__(self, parent)
        self.parent = parent

    def getValue(self, index):
        """
        Get value

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
        value = self.getValue(index)
        if index.column() == COL_VALUE:
            editor = QComboBox(parent)
            editor.activated.connect(self.onItemActivated)
            editor.addItem (value)
            editor.insertSeparator(1)
            
            # get running agents from context
            runningAgents = ServerAgents.instance().getRunningAgents()
            runningAgents = sorted(runningAgents) # sort agents list, new in v12.2
            
            for i in xrange(len(runningAgents)):
                if len(runningAgents[i]) == 0:
                    editor.insertSeparator(i + 2)
                else:
                    editor.addItem (runningAgents[i])
            editor.insertSeparator(len(runningAgents) + 2)
            
            # add alias
            params = []
            for pr in self.parent.model.getData() :
                params.append(pr['name'])
            editor.addItems ( params  )
            
            return editor
        return QItemDelegate.createEditor(self, parent, option, index)
        
    def onItemActivated(self, index): 
        """
        Close editor on index changed
        """
        self.commitData.emit(self.sender())
        self.closeEditor.emit(self.sender(), QAbstractItemDelegate.NoHint)
        
    def setEditorData(self, editor, index):
        """
        Accessor to set editor data

        @param editor: 
        @type editor:

        @param index: 
        @type index:
        """
        if index.column() == COL_VALUE:
            if sys.version_info > (3,): # python3 support
                value = index.data()
            else:
                value = str(index.data().toString())
            i = editor.findText(value)
            editor.setCurrentIndex (i)
        else:
            QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """
        Accessor to set data in model

        @param editor: 
        @type editor:

        @param model: 
        @type model:

        @param index: 
        @type index:
        """
        qvalue = editor.currentText()
        value = QtHelper.displayToValue( q(qvalue) )

        self.setValue(index, value)

        datas = self.parent.model.getData()
        currentData = datas[index.row()]

        currentAgentType = 'alias'
        for agt in ServerAgents.instance().getRunningAgentsComplete():
            if unicode(agt['name']) == unicode(value):
                currentAgentType = unicode(agt['type'].lower())
                break

        datas[index.row()]['type'] = currentAgentType
        self.parent.adjustColumns()

class DescriptionsDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Delegate items descriptions
    """
    def __init__(self, parent, col_):
        """
        @param value: 
        @type value:

        @param value: 
        @type value:
        """
        QItemDelegate.__init__(self, parent)
        self.col_ = col_
    
    def getValue(self, index):
        """
        Get value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.isValid():
            return index.model().getValue(index)

    def getValueRow(self, index):
        """
        Get value row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.isValid():
            return index.model().getValueRow(index)

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

    def createEditor(self, parent, option, index):
        """
        Create editor

        @param parent: 
        @type parent:

        @param option: 
        @type option:

        @param index: 
        @type index:
        """
        value = self.getValue(index)
        if index.column() == self.col_:
            editorDialog = DescriptionDialog(value)
            if editorDialog.exec_() == QDialog.Accepted:
                argsProbe = editorDialog.getDescr()
                index.model().setData(index,q(argsProbe))

##################### Dialogs ######################
class AddAgentDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Add agent dialog
    """
    def __init__(self, parent, agentName='AGENT', datasetView=False):
        """
        Constructor

        @param parent: parent window
        @type parent: instance

        @param agentName: 
        @type agentName: string

        @param datasetView: 
        @type datasetView: boolean
        """
        super(AddAgentDialog, self).__init__(parent)
        self.agentName=agentName
        self.parent__ = parent
        self.datasetView__ = datasetView
        self.createDialog()
        self.createConnections()

        self.initComboType()
    def createDialog (self):
        """
        Create dialog
        """
        self.labelName = QLabel("Agent Name:") 
        self.nameEdit = QLineEdit(self.agentName)
        nameLayout = QHBoxLayout()
        nameLayout.addWidget( self.labelName )
        nameLayout.addWidget( self.nameEdit )

        self.labelDescr = QLabel("Description:") 
        self.descrEdit = QTextEdit()

        self.labelValue= QLabel("Value:") 
        self.comboValue = QComboBox()

        typeLayout = QHBoxLayout()
        typeLayout.addWidget( self.labelValue )
        typeLayout.addWidget( self.comboValue )

        self.labelType = QLabel("Type:") 
        self.typeEdit = QLineEdit()
        self.typeEdit.setEnabled(False)
        type2Layout = QHBoxLayout()
        type2Layout.addWidget( self.labelType )
        type2Layout.addWidget( self.typeEdit )

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(nameLayout)
        if not self.datasetView__:
            mainLayout.addLayout(typeLayout)
            mainLayout.addLayout(type2Layout)
        mainLayout.addWidget(self.labelDescr)
        mainLayout.addWidget(self.descrEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Test Config > Add agent")
        self.resize(350, 250)
        self.center()

    def initComboType(self):
        """
        Initialize the combobox type with running agents
        """
        TYPES_PARAM = ServerAgents.instance().getRunningAgentsComplete()
        for i in xrange(len(TYPES_PARAM)):
            if len(TYPES_PARAM[i]) == 0:
                self.comboValue.insertSeparator(i + 2)
            else:
                self.comboValue.addItem (TYPES_PARAM[i]['name'])

        #self.onAgentChanged(id=0)

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.onAdd)
        self.buttonBox.rejected.connect(self.reject)
        self.comboValue.currentIndexChanged.connect(self.onAgentChanged)

    def onAgentChanged(self, id):
        """
        Called on agent changed on combobox
        """
        currentAgent = self.comboValue.currentText()
        currentAgent = unicode(currentAgent)

        currentAgentType = ''
        for agt in ServerAgents.instance().getRunningAgentsComplete():
            if unicode(agt['name']) == currentAgent:
                currentAgentType = unicode(agt['type'].lower())
                break
        
        self.typeEdit.setText(currentAgentType)

    def onAdd(self):
        """
        Called on add
        """
        if sys.version_info > (3,): # python3 support
            if unicode(self.nameEdit.text().upper()):
                self.accept()
        else:
            if unicode(self.nameEdit.text().toUpper()):
                self.accept()

    def getParameterValue(self):
        """
        Returns parameter value
        """
        qvalue = self.comboValue.currentText()
        if sys.version_info > (3,): # python3 support
            nameUpper = unicode(self.nameEdit.text().upper())
        else:
            nameUpper = unicode(self.nameEdit.text().toUpper())
        r = { 'name': nameUpper, 'description': unicode(self.descrEdit.toPlainText()),
                'value': unicode(qvalue), 'type': unicode(self.typeEdit.text()) }
        return r

class DescriptionDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Description dialog
    """
    def __init__(self, dataDescr, parent=None):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(DescriptionDialog, self).__init__(parent)
        self.dataDescr = dataDescr
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.descrEdit = QTextEdit()
        self.descrEdit.setPlainText(self.dataDescr)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.descrEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Test Config > Agent description")
        self.resize(350, 250)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getDescr(self):
        """
        Returns description
        """
        return self.descrEdit.toPlainText()

##############   main table view   #################
class AgentsTableView(QTableView, Logger.ClassLogger):
    """
    Agents table view
    """
    DataChanged = pyqtSignal() 
    def __init__(self, parent ):
        """
        Contructs ParametersTableView table view

        @param parent: 
        @type parent:
        """
        QTableView.__init__(self, parent)

        self.model = None
        self.__mime__ = "application/x-%s-test-config-agents" % Settings.instance().readValue( key='Common/acronym' ).lower()
        self.datasetView = False
        self.itemsPasted = []
        
        self.createWidgets()
        self.createConnections()
        self.createActions()

    def keyPressEvent(self, event):
        """
        Reimplemented from tableview
        """ 
        return QTableView.keyPressEvent(self, event)
    
    def startDrag(self, dropAction):
        """
        Start drag

        @param dropAction:
        @type dropAction:
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
        for index in indexes:
            if not index.isValid():
                return
        rowVal = self.model.getValueRow( indexes[0] )
        if len(rowVal) > 1 :
            if self.datasetView:
                meta = "__%s__" % rowVal['name']
            else:
                meta = "agent('%s')" % rowVal['name']
            # create mime data object
            mime = QMimeData()
            mime.setData('application/x-%s-agent-item' % Settings.instance().readValue( key='Common/acronym' ).lower() , meta )
            # start drag )
            drag = QDrag(self)
            drag.setMimeData(mime) 
            
            drag.exec_(Qt.CopyAction)

    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.model = AgentsTableModel(self)
        self.setModel(self.model)

        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)

        self.setFrameShape(QFrame.NoFrame)
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)

        self.setItemDelegateForColumn( COL_NAME, NameDelegate(self, COL_NAME) )
        # empty value is to indicate a separator
        self.setItemDelegateForColumn( COL_VALUE, ComboValueDelegate(self, COL_VALUE) )
        self.setItemDelegateForColumn( COL_DESCRIPTION, DescriptionsDelegate(self, COL_DESCRIPTION) )

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color: #FFFFBF;")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)     
        self.horizontalHeader().setStretchLastSection(True)
        
        self.adjustRows()

        # adjust default columns
        self.setColumnWidth(COL_ID, 25)
        self.setColumnWidth(COL_NAME, 60)
        self.setColumnWidth(COL_VALUE, 50)
        self.setColumnWidth(COL_DESCRIPTION, 100)

    def createConnections (self):
        """
        Create qt connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)
        self.clicked.connect(self.onAbstractItemClicked)
        QApplication.clipboard().dataChanged.connect(self.onClipboardUpdated) 
        
    def createActions (self):
        """
        Actions defined:
         * add 
         * del
         * copy
         * paste
         * clear
        """
        self.addAction = QtHelper.createAction(self, self.tr("&Add"), self.addAgent, 
                                        icon = QIcon(":/tc-add.png"), tip = 'Add a new agent' )
        self.delAction = QtHelper.createAction(self, self.tr("&Delete"), self.removeItem, 
                                        icon = QIcon(":/tc-del.png"), tip = 'Delete the selected agent' )
        self.copyAction = QtHelper.createAction(self, self.tr("Copy"), self.copyItem, 
                                        icon = QIcon(":/param-copy.png"),  tip = 'Copy the selected agent', shortcut='Ctrl+C' )
        self.pasteAction = QtHelper.createAction(self, self.tr("Paste"), self.pasteItem, 
                                        icon = QIcon(":/param-paste.png"), tip = 'Paste agent', shortcut='Ctrl+V')
        self.undoPasteAction = QtHelper.createAction(self, self.tr("Undo"), self.undoPasteItem, 
                                        icon = QIcon(":/test-parameter-undo.png"), tip = self.tr('Undo paste agent') )
        self.clearAction = QtHelper.createAction(self, self.tr("Clear"), self.clearItems, 
                                        icon = QIcon(":/param-delete.png"), tip = 'Clear all agents' )
        
        # then disable all
        self.defaultActions()

    def undoPasteItem(self):
        """
        Undo paste item
        """
        # flush the list and disable action
        self.itemsPasted = []
        self.undoPasteAction.setEnabled(False)
        
    def defaultActions(self):
        """
        Set default actions
        """
        self.addAction.setEnabled(True)
        self.delAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.pasteAction.setEnabled(False)
        self.clearAction.setEnabled(True)
        self.undoPasteAction.setEnabled(False)

    def onAbstractItemClicked(self):
        """
        Called on abstract item clicked
        """
        self.delAction.setEnabled(True)
        self.copyAction.setEnabled(True)

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
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.pasteAction )
            self.menu.addAction( self.undoPasteAction )
            self.menu.addSeparator()
            self.menu.addAction( self.clearAction )
        else:
            self.menu.addAction( self.delAction )
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.copyAction )
            self.menu.addAction( self.pasteAction )
            self.menu.addAction( self.undoPasteAction )
            self.menu.addSeparator()
            self.menu.addAction( self.clearAction )
        self.menu.popup( self.mapToGlobal(pos) )

    def copyItem(self):
        """
        Copy the selected row to the clipboard
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
        # retrieve data from model      
        rowData = []
        for id in self.selectionModel().selectedRows():
            rowData.append(self.model.getData()[id.row()])

        # pickle data
        mimeData = QMimeData()
        if sys.version_info > (3,):
            mimeData.setData( self.__mime__, pickle.dumps(rowData))
        else:
            mimeData.setData( QString(self.__mime__) , pickle.dumps(rowData))
        # copy to clipboard
        QApplication.clipboard().setMimeData(mimeData)

    def pasteItem(self):
        """
        Paste item
        """
        self.itemsPasted = []
        
        mimeData = QApplication.clipboard().mimeData()
        if not mimeData.hasFormat(self.__mime__):
            return None
        data = mimeData.data(self.__mime__)
        if not data:
            return None
        try:
            objects = pickle.loads(data.data())
            for o in objects:
                self.insertItem( newData=o, insertFromPaste=True )
        except Exception as e:
            self.error( "unable to deserialize %s" % str(e) )
            return None
        
        self.undoPasteAction.setEnabled(True)
        
    def onClipboardUpdated(self):
        """
        Called on clipboard updated
        """
        c = QApplication.clipboard()
        if c.mimeData().hasFormat(self.__mime__):
            self.pasteAction.setEnabled(True)
        else:
            self.pasteAction.setEnabled(False)

    def addAgent(self):
        """
        Add agent
        """
        addDialog = AddAgentDialog(parent=self, datasetView=self.datasetView)
        if addDialog.exec_() == QDialog.Accepted:
            parameter = addDialog.getParameterValue()
            self.insertItem(newData=parameter)

    def insertItem(self, newData=False, insertFromPaste=False):
        """
        Insert item

        @param newData: 
        @type newData: boolean
        """
        index = self.currentIndex()
        if not index.isValid():
            row = self.model.rowCount()
        else:
            row = index.row()
        data = self.model.getData()
        
        #
        if newData:
            tpl = newData
        else:
            tpl =   {'name': 'AGENT', 'description': '', 'value': 'agent-dummy01', 'type': 'dummy'}
        
        # name must be unique
        for it in data:
            if it['name'] == tpl['name']:
                tpl['name'] += '_1'
        
        if insertFromPaste:
            self.itemsPasted.append( tpl['name'] )
            
        # add data to model
        data.insert(row + 1, tpl)
        data.sort(key=operator.itemgetter('name'))
        # self.model.reset()
        self.model.beginResetModel()
        self.model.endResetModel()
        self.setData()

        # select item #Enhancement 183
        for i in  xrange(len(data)):
            if data[i]['name'] == tpl['name']:
                self.selectRow(i)
                break
        
    def clearItems(self):
        """
        Clear items
        """
        reply = QMessageBox.question(self, "Clear all", "Are you sure ?",
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
            self.delAction.setEnabled(False)

    def clear (self):
        """
        Clear contents
        """
        self.model.setDataModel( [] )

    def removeItem (self):
        """
        Removes the selected row 
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
        for index in indexes:
            if not index.isValid():
                return
        answer = QMessageBox.question(self,  "Remove",  "Do you want to remove selected agent?", 
                QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.removeValues(indexes)

    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_NAME, COL_VALUE, COL_TYPE, COL_DESCRIPTION]:
            self.resizeColumnToContents(col)
        self.setColumnWidth(COL_DESCRIPTION, 100)
    
    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in xrange(len(data)):
            self.resizeRowToContents(row)

    def loadData (self, data):
        """
        Load data

        @param data: 
        @type data:
        """
        params = data['agent']
        params.sort(key=operator.itemgetter('name'))
        self.model.setDataModel( params )
        self.setData( signal = False )

    def setData(self, signal = True):
        """
        Set table data

        @param signal: 
        @type signal: boolean
        """
        self.adjustColumns()
        self.adjustRows()
        if signal: self.DataChanged.emit()

    def removeValues(self, indexes):
        """
        Remove values from data

        @param indexes: 
        @type indexes:
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
        
        # extract name, name are unique
        datas = self.model.getData()
        allNames = []
        for i in xrange(0, len(indexes), len(HEADERS) ):
            allNames.append( datas[indexes[i].row()]['name'] )
        
        for paramName in allNames:
            self.removeValue( paramName=paramName )
        self.setData( signal = True )

    def removeValue(self, paramName):
        """
        Remove one parameter according to the name passed on argument
        """
        datas = self.model.getData()
        i = None
        for i in xrange(len(datas)):
            if datas[i]['name'] == paramName:
                break
        if i is not None:
            param = datas.pop( i )
            del param
        # self.model.reset()
        self.model.beginResetModel()
        self.model.endResetModel()
        
class AgentsQWidget(QWidget, Logger.ClassLogger):
    """
    Agents widget
    """
    def __init__(self, parent):
        """
        Contructs Parameters Widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)

        self.createWidgets()
        self.createToolbar()
        self.createConnections()

    def createToolbar(self):
        """
        Probe
        """
        self.dockToolbar.setObjectName("Document Properties toolbar agents")
        #self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.table().addAction)
        self.dockToolbar.addAction(self.table().delAction)
        self.dockToolbar.addAction(self.table().clearAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.table().copyAction)
        self.dockToolbar.addAction(self.table().pasteAction)
        self.dockToolbar.addAction(self.table().undoPasteAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()

        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border

        self.agentsTable = AgentsTableView(self)

        layout.addWidget(self.agentsTable)
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
        self.agentsTable.clear()

    def table(self):
        """
        Return the probes table view
        """
        return self.agentsTable