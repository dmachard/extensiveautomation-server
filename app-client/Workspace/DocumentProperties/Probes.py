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
Test probes module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QFont, QItemDelegate, QComboBox, QAbstractItemDelegate, 
                            QApplication, QStyleOptionButton, QStyle, QCheckBox, QDialog, 
                            QLabel, QTextEdit, QDialogButtonBox, QVBoxLayout, QTableView, 
                            QFrame, QAbstractItemView, QIcon, QMenu, QMessageBox, QWidget, QToolBar)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QSize)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon)
    from PyQt5.QtWidgets import (QItemDelegate, QComboBox, QAbstractItemDelegate, QApplication, 
                                QStyleOptionButton, QStyle, QCheckBox, QDialog, QLabel, QTextEdit, 
                                QDialogButtonBox, QVBoxLayout, QTableView, QFrame, QAbstractItemView, 
                                QMenu, QMessageBox, QWidget, QToolBar)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QSize)
    
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
        
import ServerExplorer.Probes as ServerProbes


try:
    import ProbesArgs.ProbeFile as ProbeFile
    import ProbesArgs.ProbeTextual as ProbeTextual
    import ProbesArgs.ProbeNetwork as ProbeNetwork
    import ProbesArgs.ProbeCommand as ProbeCommand
except ImportError: # support python3
    from .ProbesArgs import ProbeFile as ProbeFile
    from .ProbesArgs import ProbeTextual as ProbeTextual
    from .ProbesArgs import ProbeNetwork as ProbeNetwork
    from .ProbesArgs import ProbeCommand as ProbeCommand
    
# import standard libraries
import operator
import json

COLUMN_ID       = 0
COLUMN_USE      = 1
COLUMN_NAME     = 2
COLUMN_TYPE     = 3
COLUMN_ARGS     = 4

HEADERS_DEF = ( 'Id', 'Use', 'Name', 'Type', 'Arguments' )

try:
    xrange
except NameError: # support python3
    xrange = range
    
class ProbesTableModel(QAbstractTableModel, Logger.ClassLogger):
    """
    Table model for probes
    """
    def __init__(self, parent):
        """
        Table model for probes

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        self.owner = parent
        self.nbCol = len(HEADERS_DEF)
        self._data = []

    def getData(self):
        """
        Return model data

        @return:
        @rtype:
        """
        return self._data

    def setDataModel(self, data):
        """
        Set model data

        @param data: 
        @type data:
        """
        self._data = data

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
        if index.column() == COLUMN_ID:
            return index.row() + 1
        elif index.column() == COLUMN_USE:
            return self._data[ index.row() ]['active']
        elif index.column() == COLUMN_NAME:
            return self._data[ index.row() ]['name']
        elif index.column() == COLUMN_TYPE:
            if 'type' in self._data[ index.row() ]: # new with 2.1.0
                return self._data[ index.row() ]['type']
            else:
                return ''
        elif index.column() == COLUMN_ARGS:
            return self._data[ index.row() ]['args']
        else:
            pass

    def getValueRow(self, index):
        """
        Return all current values of the row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        return self._data[ index.row() ]

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
        if role == Qt.FontRole:
            if index.column() == COLUMN_NAME:
                font = QFont()
                font.setBold(True)
                return q(font)

            elif index.column() == COLUMN_TYPE:
                font = QFont()
                font.setItalic(True)
                return q(font)

            elif index.column() == COLUMN_ARGS:
                font = QFont()
                font.setBold(True)
                return q(font)

        elif role == Qt.DisplayRole:
            if index.column() == COLUMN_ARGS: # exception for arguments
                ret = ''
                if len(value) != 0:
                    ret = ' [...]'
                return q(ret)

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
            return HEADERS_DEF[section]

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
        if index.column() == COLUMN_USE:
            orig_ = self._data[ index.row() ]['active']
            self._data[ index.row() ]['active'] = value
            if orig_ != value:
                dataChanged = True
        elif index.column() == COLUMN_NAME:
            orig_ = self._data[ index.row() ]['name']
            self._data[ index.row() ]['name'] = value
            if orig_ != value:
                dataChanged = True
                probeType = ServerProbes.instance().getProbeTypeByName(name=value)
                self._data[ index.row() ]['type'] = probeType.lower()
                self._data[ index.row() ]['args'] = ''
        elif index.column() == COLUMN_TYPE:
            if 'type' in self._data[ index.row() ]: # new with 2.1.0
                orig_ = self._data[ index.row() ]['type']
                self._data[ index.row() ]['type'] = value
                if orig_ != value:
                    dataChanged = True
            else:
                self._data[ index.row() ]['type'] = ''
        elif index.column() == COLUMN_ARGS:
            orig_ = self._data[ index.row() ]['args']
            self._data[ index.row() ]['args'] = value
            if orig_ != value:
                dataChanged = True

        self._data.sort(key=operator.itemgetter('name'))
        self.owner.adjustColumns()
        if dataChanged: self.owner.DataChanged.emit()

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
        if index.column() in [ COLUMN_ID, COLUMN_TYPE ]:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable)

####################################################        
################# Delegate items ###################
####################################################    
class ComboBoxProbesActiveDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Combobox delegate
    """
    def __init__ (self, parent, items_, col_ ):
        """
        ComboBox delegate

        @param parent: 
        @type parent:

        @param items_: 
        @type items_:

        @param col_: 
        @type col_:
        """
        QItemDelegate.__init__(self, parent)
        self.items_ = items_
        self.col_ = col_

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
        # get running probe from context
        self.items_ = ServerProbes.instance().getRunningProbes()
        self.items_ = sorted(self.items_) # sort agents list, new in v12.2
        
        # load probs in combobox
        value = self.getValue(index)
        if index.column() == self.col_:
            editor = QComboBox(parent)
            editor.activated.connect(self.onItemActivated)
            editor.addItem (value)
            editor.insertSeparator(1)
            editor.addItems(self.items_)
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
        Set the editor

        @param editor: 
        @type editor:

        @param index: 
        @type index:
        """
        if index.column() == self.col_:
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
        Set the model

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


class CheckBoxActiveDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Checkbox active delegate
    """
    def __init__(self, owner):
        """
        Checkbox delegate

        @param value: 
        @type value:
        """
        QItemDelegate.__init__(self, owner)
 
    def paint(self, painter, option, index):
        """
        Paint

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        # Get item data
        if sys.version_info > (3,): # python 3 support
            value = index.data(Qt.DisplayRole)
            if isinstance(value, str):
                value = QtHelper.str2bool(value)
        else:
            value = index.data(Qt.DisplayRole).toBool()
 
        # fill style options with item data
        style = QApplication.style()
        opt = QStyleOptionButton()
        opt.state |= QStyle.State_On if value else QStyle.State_Off
        opt.state |= QStyle.State_Enabled
        opt.text = ""
        opt.rect = option.rect
 
        # draw item data as CheckBox
        style.drawControl(QStyle.CE_CheckBox, opt, painter)
 
    def createEditor(self, parent, option, index):
        """
        Create the editor

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        # create check box as our editor.
        editor = QCheckBox(parent)
        editor.installEventFilter(self)
        
        return editor
 
    def setEditorData(self, editor, index):
        """
        Set the editor

        @param value: 
        @type value:

        @param value: 
        @type value:
        """
        # set editor data
        if sys.version_info > (3,): # python 3 support
            value = index.data(Qt.DisplayRole)
            if isinstance(value, str):
                value = QtHelper.str2bool(value)
        else:
            value = index.data(Qt.DisplayRole).toBool()
        editor.setChecked(value)
 
    def setModelData(self, editor, model, index):
        """
        Set the model

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        value = editor.checkState()
        if value == 0:
            value = "False"
        if value == 2:
            value = "True"
        
        model.setData(index, q(value))
 
    def updateEditorGeometry(self, editor, option, index):
        """
        Update the geometry of the editor

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        editor.setGeometry(option.rect)
 
class ArgumentsDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Arguments delegate
    """
    def __init__(self, parent, col_):
        """
        Arguments delegate

        @param value: 
        @type value:

        @param value: 
        @type value:
        """
        QItemDelegate.__init__(self, parent)
        self.col_ = col_
    
    def getValue(self, index):
        """
        Returns value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        if index.isValid():
            return index.model().getValue(index)

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
        """
        value = self.getValueRow(index)
        if index.column() == self.col_:
            if not 'type' in value:
                self.setDefaultEditor( data=value['args'], index=index )
            else:
                probeType = value['type']
                if probeType == 'file':
                    editorDialog = ProbeFile.FileArgs(value['args'])
                    if editorDialog.exec_() == QDialog.Accepted:
                        argsProbe = editorDialog.getArgs()
                        index.model().setData(index,q(argsProbe))
                            
                elif probeType == 'textual':
                    editorDialog = ProbeTextual.FileLogArgs(value['args'])
                    if editorDialog.exec_() == QDialog.Accepted:
                        argsProbe = editorDialog.getArgs()
                        index.model().setData(index,q(argsProbe))
                            
                elif probeType == 'network':
                    editorDialog = ProbeNetwork.NetworkArgs(value['args'])
                    if editorDialog.exec_() == QDialog.Accepted:
                        argsProbe = editorDialog.getArgs()
                        index.model().setData(index,q(argsProbe))
                            
                elif probeType == 'command':
                    editorDialog = ProbeCommand.CommandArgs(value['args'])
                    if editorDialog.exec_() == QDialog.Accepted:
                        argsProbe = editorDialog.getArgs()
                        index.model().setData(index,q(argsProbe))
                        
                else:
                    self.setDefaultEditor( data=value['args'], index=index )

    def setDefaultEditor(self, data, index):
        """
        Set the default editor

        @param data: 
        @type data:

        @param index: 
        @type index:
        """
        editorDialog = DefaultArgs(data)
        if editorDialog.exec_() == QDialog.Accepted:
            argsProbe = editorDialog.getArgs()
            index.model().setData(index,q(argsProbe))

####################################################        
##################### Dialogs ######################
####################################################    
class DefaultArgs(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Default args
    """
    def __init__(self, dataArgs, parent=None):
        """
        Dialog to fill arguments for default probe

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(DefaultArgs, self).__init__(parent)
        self.dataArgs = dataArgs
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        argsLabel = QLabel("Arguments:" )
        self.argsEdit = QTextEdit()
        self.argsEdit.setPlainText(self.dataArgs)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(argsLabel)
        mainLayout.addWidget(self.argsEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Default Probe > Arguments")
        

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getArgs(self):
        """
        Returns arguments
        """
        return self.argsEdit.toPlainText()

####################################################        
##############   main table view   #################
####################################################    
class ProbesTableView(QTableView, Logger.ClassLogger):
    """
    Probes table view
    """
    DataChanged = pyqtSignal() 
    def __init__(self, parent):
        """
        Contructs ProbesTableView table view

        @param parent: 
        @type parent:
        """
        QTableView.__init__(self, parent)
        self.model = None
        #
        self.createWidgets()
        self.createConnections()
        self.createActions()

    def keyPressEvent(self, event):
        """
        Reimplemented from tableview
        """
        if event.key() == Qt.Key_Delete:
            self.removeItem()       
        return QTableView.keyPressEvent(self, event)


    def createWidgets (self):
        """
        Create qt widgets
        """
        self.model = ProbesTableModel(self)
        self.setModel(self.model)
        
        self.setShowGrid(False)
        self.setFrameShape(QFrame.NoFrame)
        
        self.activeProbe = CheckBoxActiveDelegate(self)
        self.probesRegistered = ComboBoxProbesActiveDelegate(self, [''], COLUMN_NAME)
        self.probesArgs = ArgumentsDelegate(self, COLUMN_ARGS)

        self.setItemDelegateForColumn(COLUMN_USE, self.activeProbe )
        self.setItemDelegateForColumn(COLUMN_NAME, self.probesRegistered  )
        self.setItemDelegateForColumn(COLUMN_ARGS, self.probesArgs )

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color: #F6F6F6")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)

        self.adjustRows()
        # adjust default columns
        self.setColumnWidth(COLUMN_ID, 25)

    def createConnections (self):
        """
        Create qt connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)
        self.clicked.connect(self.onAbstractItemClicked)

    def createActions (self):
        """
        Actions defined:
         * add 
         * del
         * clear
        """
        self.addAction = QtHelper.createAction(self, "&Add", self.insertItem, 
                                                icon = QIcon(":/tc-add.png"), tip = 'Add a new probe' )
        self.delAction = QtHelper.createAction(self, "&Delete", self.removeItem,
                                                icon = QIcon(":/tc-del.png"), tip = 'Delete the selected probe' )
        self.clearAction = QtHelper.createAction(self, "Clear", self.clearItems, 
                                                icon = QIcon(":/param-delete.png"),  tip = 'Clear all probes' )
        
        self.defaultActions()

    def defaultActions(self):
        """
        Set default actions
        """
        self.addAction.setEnabled(True)
        self.delAction.setEnabled(False)
        self.clearAction.setEnabled(True)

    def onAbstractItemClicked(self):
        """
        Called when a abstract item is clicked
        """
        self.delAction.setEnabled(True)

    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu()
        index = self.currentIndex()
        indexes = self.selectedIndexes()
        if not indexes:
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.clearAction )
        else:
            self.menu.addAction( self.delAction )
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.clearAction )
        self.menu.popup(self.mapToGlobal(pos))

    def clearItems(self):
        """
        Clear all items
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

            self.model.beginResetModel()
            self.model.endResetModel()
            self.setData()
            self.delAction.setEnabled(False)


    def insertItem(self):
        """
        Insert row
        """
        index = self.currentIndex()
        if not index.isValid():
            row = self.model.rowCount()
        else:
            row = index.row()
        data = self.model.getData()

        tpl = { 'active': 'False', 'args': '', 'name': 'probe01', 'type': 'default'}

        data.insert(row + 1, tpl)
        data.sort(key=operator.itemgetter('name'))

        self.model.beginResetModel()
        self.model.endResetModel()
        self.setData()
    
    def clear (self):
        """
        Clears contents
        """
        self.model.setDataModel( [] )
        self.adjustColumns()
        self.adjustRows()

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
        answer = QMessageBox.question(self,  "Remove", 
                    "Do you want to remove selected parameter", 
                        QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.removeValues(indexes)

    def adjustColumns(self):
        """
        Resize three first columns to contents
        """
        for col in [COLUMN_USE, COLUMN_NAME, COLUMN_TYPE, COLUMN_ARGS]:
            self.resizeColumnToContents(col)


    def adjustRows (self):
        """
        Adjust rows
        """
        data = self.model.getData()
        for row in xrange(len(data)):
            self.resizeRowToContents(row)

    def loadData (self, data):
        """
        Load data and set the datamodel with-it

        @param data: 
        @type data:
        """
        probes = data['probe']
        probes.sort(key=operator.itemgetter('name'))
        self.model.setDataModel( probes )
        self.setData( signal = False)

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
        for i in xrange(0, len(indexes), len(HEADERS_DEF) ):
            allNames.append( datas[indexes[i].row()]['name'] )
        
        for paramName in allNames:
            self.removeValue( paramName=paramName )
        self.setData( signal = True )

    def removeValue(self, paramName):
        """
        Remove one parameter according to the name passed on argument
        """
        i = None
        datas = self.model.getData()
        for i in xrange(len(datas)):
            if datas[i]['name'] == paramName:
                break
        if i is not None:
            param = datas.pop( i )
            del param

        self.model.beginResetModel()
        self.model.endResetModel()

class ProbesQWidget(QWidget, Logger.ClassLogger):
    """
    Probes widget
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
        self.dockToolbar.setObjectName("Document Properties toolbar probes")
        self.dockToolbar.addAction(self.table().addAction)
        self.dockToolbar.addAction(self.table().delAction)
        self.dockToolbar.addAction(self.table().clearAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()

        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border

        self.probesTable = ProbesTableView(self)

        layout.addWidget(self.probesTable)
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
        self.probesTable.clear()

    def table(self):
        """
        Return the probes table view
        """
        return self.probesTable