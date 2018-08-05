#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive automation project
# Copyright (c) 2010-2018 Denis Machard
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
#
# Author: Emmanuel Monsoro
# Contact: e1gle1984@gmail.com
# Website: www.extensiveautomation.org
# -------------------------------------------------------------------

"""
Main module 
"""
# to support new print style on python 2.x
from __future__ import print_function 

# name of the main developer
__AUTHOR__ = 'Emmanuel Monsoro'
# email of the main developer
__EMAIL__ = 'e1gle1984@gmail.com'
# list of contributors
__CONTRIBUTORS__ = [ "Denis Machard" ]
# list of contributors
__TESTERS__ = [ "Denis Machard" ]
# project start in year
__BEGIN__="2016"
# year of the latest build
__END__="2017"
# date and time of the buid
__BUILDTIME__="27/05/2017 12:15:54"
# debug mode
DEBUGMODE=False

try:
    from PyQt4.QtGui import (QWidget, QApplication, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                QMessageBox, QFileDialog, QLabel, QAbstractItemView, QTableView, QTreeView, QTextEdit,
                                QPen, QPainter, QSizePolicy, QFrame, QSplitter, QLineEdit, QFormLayout, QColor,
                                QMenu, QAction, QCursor, QItemSelectionModel, QPixmap, QTabWidget)
    from PyQt4.QtCore import ( QFile, Qt, QIODevice, pyqtSignal, QAbstractTableModel, QAbstractItemModel, QModelIndex, QRectF, Qt,
                                QRect)
    from PyQt4.QtWebKit import QWebView, QWebPage
    
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                 QMessageBox, QFileDialog, QLabel, QAbstractItemView, QTableView, QTreeView, QTextEdit,
                                QPen, QPainter, QSizePolicy, QFrame, QSplitter, QLineEdit, QFormLayout, QColor,
                                QMenu, QAction, QCursor, QRect, QItemSelectionModel, QPixmap, QTabWidget)
    from PyQt5.QtCore import ( QFile, Qt, QIODevice, pyqtSignal, QAbstractTableModel, QAbstractItemModel, QModelIndex, QRectF,  Qt,
                                QRect)
    from PyQt5.QtWebKit import QWebView, QWebPage 
    
from Core import CorePlugin
from Core import Settings
from Core.Libs import QtHelper, Logger

import SSHParser

import sys
import json
import sip
import os
import re
import html

# adding missing folders
if not os.path.exists( "%s/Core/Logs/" % QtHelper.dirExec() ):
    os.mkdir( "%s/Core/Logs" % QtHelper.dirExec() )

LICENSE = """<br />
%s plugin <b>%s</b> for the <b>%s</b><br />
Developed and maintained by <b>Emmanuel Monsoro</b><br />
Contributors: <b>%s</b><br />
<br />
This program is free software; you can redistribute it and/or<br />
modify it under the terms of the GNU Lesser General Public<br />
License as published by the Free Software Foundation; either<br />
version 2.1 of the License, or (at your option) any later version.<br />
<br />
This library is distributed in the hope that it will be useful,<br />
but WITHOUT ANY WARRANTY; without even the implied warranty of<br />
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU<br />
Lesser General Public License for more details.<br />
<br />
You should have received a copy of the GNU Lesser General Public<br />
License along with this library; if not, write to the Free Software<br />
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,<br />
MA 02110-1301 USA<br />
"""

COL_ID       =   0
COL_ACTION   =   1
COL_TYPE     =   2
COL_VALUE    =   3
COL_DISABLE  =   4

HEADERS      = ( 'Id', 'Action', 'type', 'Command')

class ActionsTreeModel(QAbstractItemModel):
    """
    Table model for parameters
    """
    def __init__(self, parent, core):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractItemModel.__init__(self, parent)
        
        self.mydata = []
        self.owner = parent
        self.__core = core
        self.nbCol = len(HEADERS)

    def core(self):
        """
        """
        return self.__core
    
    def index(self, row, column, parent):
        """
        """
        return self.createIndex(row, column, self.mydata[row])
    
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
        self.beginResetModel()
        self.endResetModel()

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
        if index.column() == COL_ACTION:
            return self.mydata[ index.row() ]['action-name']
        elif index.column() == COL_DISABLE:
            return self.mydata[ index.row() ]['action-disable']
        elif index.column() == COL_TYPE:
            return self.mydata[ index.row() ]['action-type']
        elif index.column() == COL_VALUE:
            return self.mydata[ index.row() ]['action-value']
        elif index.column() == COL_ID:
            return self.mydata[ index.row() ]['action-id']
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
        if not index.isValid(): return None
        value = self.getValue(index)
        
        if role == Qt.DisplayRole:
            if index.column()<COL_DISABLE:
                return value
        elif role == Qt.EditRole:
            return value
        elif role == Qt.BackgroundColorRole:
            if self.mydata[ index.row() ]['action-disable']:
                bgColor=QColor(189,189,189,255)
            elif self.mydata[ index.row() ]['action-name']=="SEND":
                bgColor=QColor(100,254,46,200)
            else:
                bgColor=QColor(254,154,46,255)
            return bgColor
            
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
        if index.column() == COL_ACTION:
            self.mydata[ index.row() ]['action-name'] = value
        elif index.column() == COL_TYPE:
            self.mydata[ index.row() ]['action-type'] = value
        elif index.column() == COL_VALUE:
            self.mydata[ index.row() ]['action-value'] = value
        elif index.column() == COL_DISABLE:
            self.mydata[ index.row() ]['action-disable'] = value
        elif index.column() == COL_ID:
            self.mydata[ index.row() ]['action-id'] = value
        
        self.dataChanged.emit(index,index)
        
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
        if not index.isValid(): return False
        value = QtHelper.displayToValue( value )
        self.setValue(index, value)
        return True
    def setDataFromRowColumn(self, row, column, value):
        """
        Cell content change

        @param row: 
        @type row:
        
        @param column: 
        @type column:

        @param value: 
        @type value:

        @param role: 
        @type role:
        
        @return:
        @rtype:
        """
        index = self.index(row, column)
        self.setValue(index, value)
        return True
        
    def setEnableDisableCommand(self, row):
        peer_row = row+1
        
        if self.mydata[ row ]['action-name'] == "EXPECT":
            peer_row = row-1
        b = self.mydata[ row ]['action-disable']
        if b:
            self.mydata[ row ]['action-disable'] = False
            self.mydata[ peer_row ]['action-disable'] = False
        else:
            self.mydata[ row ]['action-disable'] = True
            self.mydata[ peer_row ]['action-disable'] = True
        index = self.index(row, COL_DISABLE)
        peer_index =  self.index(peer_row, COL_DISABLE)
        self.dataChanged.emit(index,peer_index)
            
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
        if index.column() == COL_ID or index.column() == COL_ACTION or index.column() == COL_TYPE or index.column() == COL_DISABLE :
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
    
    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)       
        row = self.mydata.pop(position)
        self.endRemoveRows()

        return True

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        if self.mydata[position]["action-type"] == "EXPECT" and position>0: position-=1
        line = self.mydata[position]["action-line"]
        prompt = self.mydata[position]["action-prompt"]
        id=self.mydata[position]["action-id"]
        for row in range(0,len(self.mydata) - position,2):
            current=str(int(self.mydata[row+position]['action-id']) + rows)
            self.mydata[row+position]['action-id'] = current
            self.mydata[row+position+1]['action-id'] = current
        for row in range(0,rows,2):

            stp1 ={
                        "action-id":id,
                        "action-type":"FIXED",
                        "action-prompt":prompt,
                        "action-line":line,
                        "action-name":"SEND",
                        "action-value":"[TBD]",
                        "action-disable":True,
                        "action-editable":True
                   }
            stp2 ={
                        "action-id":id,
                        "action-type":"CONTAINS",
                        "action-prompt":prompt,
                        "action-line":line,
                        "action-name":"EXPECT",
                        "action-value":"[TBD]",
                        "action-disable":True,
                        "action-editable":True
                  }
            self.mydata.insert(position + row,  stp1)
            self.mydata.insert(position + row + 1,  stp2)
        self.endInsertRows()
        return True
        
class ActionsTreeView(QTreeView):
    insertLineSignal = pyqtSignal(int)
    eraseLineSignal = pyqtSignal()
    def __init__(self, parent, core):
        """
        """
        QTreeView.__init__(self, parent)
        self.__core = core
        
        self.createWidgets()
        self.createConnections()
    
    def core(self):
        """
        """
        return self.__core
        
    def createConnections(self):
        """
        """
        self.clicked.connect( self.onAbstractItemClicked) 
        self.doubleClicked.connect( self.onAbstractItemDoubleClicked) 
        
    def createWidgets(self):
        """
        """
        self.model = ActionsTreeModel(self, core=self.core())
        self.setModel(self.model)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def onAbstractItemClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
    def onAbstractItemDoubleClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return

    def clear(self):
        """
        Clear all widget
        """
        self.model.setDataModel( [] )
        
    def loadTable (self, data):
        """
        Load data

        @param data: 
        @type data:
        """
        self.model.setDataModel( data )

    def mouseReleaseEvent(self, event):
        """
        """
        QTableView.mouseReleaseEvent(self,event)
        if (event.button() == Qt.RightButton):
            self.setSelection(QRect(event.pos(),event.pos()), QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
            contextMenu = QMenu()
            insertActionAbove = QAction("Insert line above",self)
            insertActionAbove.triggered.connect(self.insertLine)
            contextMenu.addAction(insertActionAbove)
            contextMenu.popup( QCursor.pos() )
            contextMenu.exec_()

    def insertLine(self):
        """
        """
        index = self.currentIndex()
        self.insertLineSignal.emit(index.row())
        
    def eraseLine(self):
        """
        """
        self.eraseLineSignal.emit()

 
class ActionsTableModel(QAbstractTableModel):
    """
    Table model for parameters
    """
    def __init__(self, parent, core):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        
        self.mydata = []
        self.owner = parent
        self.__core = core
        self.nbCol = len(HEADERS)

    def core(self):
        """
        """
        return self.__core
        
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
        self.beginResetModel()
        self.endResetModel()

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
        if index.column() == COL_ACTION:
            return self.mydata[ index.row() ]['action-name']
        elif index.column() == COL_DISABLE:
            return self.mydata[ index.row() ]['action-disable']
        elif index.column() == COL_TYPE:
            return self.mydata[ index.row() ]['action-type']
        elif index.column() == COL_VALUE:
            return self.mydata[ index.row() ]['action-value']
        elif index.column() == COL_ID:
            return self.mydata[ index.row() ]['action-id']
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
        if not index.isValid(): return None
        value = self.getValue(index)
        
        if role == Qt.DisplayRole:
            if index.column()<COL_DISABLE:
                if type(value) is list:
                    return str(value)
                return value
        elif role == Qt.EditRole:
            return value
        elif role == Qt.BackgroundColorRole:
            if self.mydata[ index.row() ]['action-disable']:
                bgColor=QColor(189,189,189,255)
            elif self.mydata[ index.row() ]['action-name']=="SEND":
                bgColor=QColor(100,254,46,200)
            else:
                bgColor=QColor(254,154,46,255)
            return bgColor
            
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
        if index.column() == COL_ACTION:
            self.mydata[ index.row() ]['action-name'] = value
        elif index.column() == COL_TYPE:
            self.mydata[ index.row() ]['action-type'] = value
        elif index.column() == COL_VALUE:
            self.mydata[ index.row() ]['action-value'] = value
        elif index.column() == COL_DISABLE:
            self.mydata[ index.row() ]['action-disable'] = value
        elif index.column() == COL_ID:
            self.mydata[ index.row() ]['action-id'] = value
        
        self.dataChanged.emit(index,index)
        
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
        if not index.isValid(): return False
        value = QtHelper.displayToValue( value )
        self.setValue(index, value)
        return True
    def setDataFromRowColumn(self, row, column, value):
        """
        Cell content change

        @param row: 
        @type row:
        
        @param column: 
        @type column:

        @param value: 
        @type value:

        @param role: 
        @type role:
        
        @return:
        @rtype:
        """
        index = self.index(row, column)
        self.setValue(index, value)
        return True
        
    def setEnableDisableCommand(self, row, value=None):
        """
        Function to toggle between enabling and disabling a command and its associated expected result
        
        @param row: row number of the line to enable/disable
        @type row: integer
        
        @param value: optional parameter to force the enabling/disabling
        @type value: boolean
        """
        peer_row = row+1
        
        if self.mydata[ row ]['action-name'] == "EXPECT":
            if row>0:
                peer_row = row-1
            else:
                peer_row = 0
        if value is None:
            b = self.mydata[ row ]['action-disable']
            if b:
                self.mydata[ row ]['action-disable'] = False
                self.mydata[ peer_row ]['action-disable'] = False
            else:
                self.mydata[ row ]['action-disable'] = True
                self.mydata[ peer_row ]['action-disable'] = True
        else:
            self.mydata[ row ]['action-disable'] = value
            self.mydata[ peer_row ]['action-disable'] = value
        index = self.index(row, COL_DISABLE)
        peer_index =  self.index(peer_row, COL_VALUE)
        self.dataChanged.emit(index,peer_index)
    
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
        if index.column() == COL_ID or index.column() == COL_ACTION or index.column() == COL_TYPE or index.column() == COL_DISABLE :
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
    
    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)       
        row = self.mydata.pop(position)
        self.endRemoveRows()

        return True

    def insertRows(self, position, rows=1, index=QModelIndex(), above=True):
        self.beginInsertRows(QModelIndex(), position, position + rows)
        if above is False:
            position+=2
            if position>len(self.mydata)-1:
                position=len(self.mydata)-1
                line = str(int(self.mydata[position]["action-line"])+1)
                prompt = self.mydata[position]["action-prompt"]
                id=str(int(self.mydata[position]["action-id"])+1)
                for row in range(0,rows,2):
                    stp1 ={
                            "action-id":id,
                            "action-type":"FIXED",
                            "action-prompt":prompt,
                            "action-line":line,
                            "action-name":"SEND",
                            "action-value":"[TBD]",
                            "action-disable":True,
                            "action-editable":True
                            }
                    stp2 ={
                            "action-id":id,
                            "action-type":"CONTAINS",
                            "action-prompt":prompt,
                            "action-line":line,
                            "action-name":"EXPECT",
                            "action-value":"[TBD]",
                            "action-disable":True,
                            "action-editable":True
                            }
                    self.mydata.append(stp1)
                    self.mydata.append(stp2)
                self.endInsertRows()
                return True
        if self.mydata[position]["action-type"] == "EXPECT" and position>0: position-=1
        line = self.mydata[position]["action-line"]
        prompt = self.mydata[position]["action-prompt"]
        id=self.mydata[position]["action-id"]
        
        for row in range(0,len(self.mydata) - position,2):
            current=str(int(self.mydata[row+position]['action-id']) + rows)
            self.mydata[row+position]['action-id'] = current
            self.mydata[row+position+1]['action-id'] = current
        for row in range(0,rows,2):
            stp1 ={
                    "action-id":id,
                    "action-type":"FIXED",
                    "action-prompt":prompt,
                    "action-line":line,
                    "action-name":"SEND",
                    "action-value":"[TBD]",
                    "action-disable":True,
                    "action-editable":True
                   }
            stp2 ={
                    "action-id":id,
                    "action-type":"CONTAINS",
                    "action-prompt":prompt,
                    "action-line":line,
                    "action-name":"EXPECT",
                    "action-value":"[TBD]",
                    "action-disable":True,
                    "action-editable":True
                   }
            self.mydata.insert(position + row,  stp1)
            self.mydata.insert(position + row + 1,  stp2)
        self.endInsertRows()
        return True
        
class ActionsTableView(QTableView):
    insertLineSignal = pyqtSignal(int)
    eraseLineSignal = pyqtSignal()
    def __init__(self, parent, core):
        """
        """
        QTableView.__init__(self, parent)
        self.__core = core
        
        self.createWidgets()
        self.createConnections()
    
    def core(self):
        """
        """
        return self.__core
        
    def createConnections(self):
        """
        """
        self.clicked.connect( self.onAbstractItemClicked) 
        self.doubleClicked.connect( self.onAbstractItemDoubleClicked) 
        
    def createWidgets(self):
        """
        """
        self.model = ActionsTableModel(self, core=self.core())
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

    def onAbstractItemClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
    def onAbstractItemDoubleClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
            
    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in range(len(data)):
            self.setRowHeight (row, 30)

    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_ACTION, COL_VALUE, COL_DISABLE, COL_ID]:
            self.resizeColumnToContents(col)

    def clear(self):
        """
        Clear all widget
        """
        self.model.setDataModel( [] )
        
    def loadTable (self, data):
        """
        Load data

        @param data: 
        @type data:
        """
        self.model.setDataModel( data )
        
        self.adjustRows()
        self.adjustColumns()
        
    def mouseReleaseEvent(self, event):
        QTableView.mouseReleaseEvent(self,event)
        if (event.button() == Qt.RightButton):
            self.setSelection(QRect(event.pos(),event.pos()), QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
            contextMenu = QMenu()
            insertActionAbove = QAction("Insert line above",self)
            insertActionAbove.triggered.connect(self.insertLine)

            index = self.currentIndex()
            if self.model.getValueRow(index)['action-disable']:
                disableT="Enable"
            else:
                disableT="Disable"
            disableAction = QAction("%s this line"%disableT,self)
            disableAction.triggered.connect(self.onDisableAction)
            
            toggleContainsRegexAction = QAction("Toggle between CONTAINS/REGEX",self)
            toggleContainsRegexAction.triggered.connect(self.onToggleExpectAction)
            
            contextMenu.addAction(insertActionAbove)
            contextMenu.addAction(disableAction)
            
            index = self.currentIndex()
            if self.model.getValueRow(index)['action-name']=="EXPECT":
                contextMenu.addAction(toggleContainsRegexAction)

            contextMenu.popup( QCursor.pos() )
            contextMenu.exec_()
    
    def onDisableAction(self):
        """
        """
        index = self.currentIndex()
        self.model.setEnableDisableCommand(index.row())
    
    def onToggleExpectAction(self):
        """
        """
        index = self.currentIndex()
        index=self.model.index(index.row(), COL_TYPE)
        self.doubleClicked.emit(index)
    
    def keyPressEvent(self, event):
        """
        """
        index = self.currentIndex()
        if not index.isValid(): return
        if (event.key() == Qt.Key_Delete):
            self.model.setEnableDisableCommand(index.row(), value=True)
        QTableView.keyPressEvent(self,event)
        
    def insertLine(self):
        """
        """
        index = self.currentIndex()
        self.insertLineSignal.emit(index.row())
        
    def eraseLine(self):
        """
        """
        self.eraseLineSignal.emit()

class PromptTableModel(QAbstractTableModel):
    """
    Table model for prompts
    """
    def __init__(self, parent, core):
        """
        Table Model for parameters

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        
        self.mydata = []
        self.owner = parent
        self.__core = core
        self.nbCol = 1

    def core(self):
        """
        """
        return self.__core
        
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
        templist = []
        for p in data :
            templist.append(re.escape(p))
        self.mydata = data #templist
        self.beginResetModel()
        self.endResetModel()

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
        return self.mydata[ index.row() ]
        
    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)       
        row = self.mydata.pop(position)
        self.endRemoveRows()

        return True

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.mydata.insert(position + row,  "")
        self.endInsertRows()
        return True
        
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
        if not index.isValid(): return None
        value = self.getValue(index)
        
        if role == Qt.DisplayRole:
            return value
        elif role == Qt.EditRole:
            return value
        elif role == Qt.BackgroundColorRole:
            bgColor=QColor(100,254,46,200)
            return bgColor
            
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
        if role == Qt.DisplayRole:
            return "Detected prompts"

        return None

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        self.mydata[ index.row() ] = value
        self.dataChanged.emit(index,index)
        
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
        if not index.isValid(): return False
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

class PromptsTableView(QTableView):
    insertLineSignal = pyqtSignal()
    eraseLineSignal = pyqtSignal(str)
    def __init__(self, parent, core):
        """
        """
        QTableView.__init__(self, parent)
        self.__core = core
        
        self.createWidgets()
        self.createConnections()
    
    def core(self):
        """
        """
        return self.__core
        
    def createConnections(self):
        """
        """
        self.clicked.connect( self.onAbstractItemClicked) 
        self.doubleClicked.connect( self.onAbstractItemDoubleClicked) 
        
    def createWidgets(self):
        """
        """
        self.model = PromptTableModel(self, core=self.core())
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

    def onAbstractItemClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
    def onAbstractItemDoubleClicked(self):
        """
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return
            
    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in range(len(data)):
            self.setRowHeight (row, 30)

    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_ACTION, COL_VALUE, COL_DISABLE, COL_ID]:
            self.resizeColumnToContents(col)

    def clear(self):
        """
        Clear all widget
        """
        self.model.setDataModel( [] )
        
    def loadTable (self, data):
        """
        Load data

        @param data: 
        @type data:
        """
        self.model.setDataModel( data )
        
        self.adjustRows()
        self.adjustColumns()
    def keyPressEvent(self, event):
        """
        """
        index = self.currentIndex()
        if not index.isValid(): return
        if (event.key() == Qt.Key_Delete):
            self.eraseLine()
        
    def mouseReleaseEvent(self, event):
        """
        """
        QTableView.mouseReleaseEvent(self,event)
        if (event.button() == Qt.RightButton):
            self.setSelection(QRect(event.pos(),event.pos()), QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
            contextMenu = QMenu()
            insertAction = QAction("Insert new prompt",self)
            insertAction.triggered.connect(self.insertLine)
            eraseAction = QAction("Erase selected prompt",self)
            eraseAction.triggered.connect(self.eraseLine)
            
            contextMenu.addAction(insertAction)
            contextMenu.addAction(eraseAction)
            contextMenu.popup( QCursor.pos() )
            contextMenu.exec_()
        
        
    def insertLine(self):
        """
        """
        index = self.currentIndex()
        self.model.insertRows(index.row())
        self.selectionModel().select(index, QItemSelectionModel.SelectCurrent|QItemSelectionModel.ClearAndSelect);

    def eraseLine(self):
        """
        """
        index = self.currentIndex()
        prompt = self.model.getData()[index.row()]
        self.model.removeRows(index.row())
        self.eraseLineSignal.emit(prompt)
        
class CustomQWebView(QWebView):
    """
    """
    TextSelected = pyqtSignal()
    mouseClicked = pyqtSignal(str)
    buttonClicked = pyqtSignal(str)
    webViewEdited = pyqtSignal(str)
    elementModified = pyqtSignal(str)
    insertButtonClicked = pyqtSignal(str)
    def __init__(self, parent=None):
        """
        """
        super(CustomQWebView, self).__init__(parent)
        self.currentframe = None
        self.currentpage = None
        self.currently_selected_block_element= None
        self.currently_edited_block_element=None
        self.saveButton=None
        self.loadFinished.connect(self.setframeafterloadfinished)

    def keyPressEvent(self, event):
        """
        """
        if (event.key() == Qt.Key_Enter):# or event.key() == Qt.Key_Return):
            if self.currently_edited_block_element is not None:
                self.stopEdition()
                return
        QWebView.keyPressEvent(self,event)
    
    def keyReleaseEvent(self, event):
        """
        """
        QWebView.keyPressEvent(self,event)

    def stopEdition(self):
        """
        """
        self.currently_edited_block_element.setAttribute("contenteditable","false")
        self.currently_edited_block_element.setAttribute("title","Select some text to filter or double-click to edit.")
        self.webViewEdited.emit(self.currently_edited_block_element.attribute("id"))
        self.currently_edited_block_element=None
        self.saveButton.setAttribute("visible","false")
        self.saveButton=None
        
    def setframeafterloadfinished(self):
        """
        """
        self.currentpage = self.page()
        self.currentframe = self.currentpage.mainFrame()
    
    def mouseReleaseEvent(self, event):
        """
        """
        QWebView.mouseReleaseEvent(self,event)
        
        html=self.selectedHtml()
        hittestresult = self.currentframe.hitTestContent(event.pos())
        element = hittestresult.element()
        if element.hasClass("button"):
            if element.attribute("title") == "Add":
                self.insertButtonClicked.emit(element.attribute("rel"))
            else:
                if element.attribute("title") == "Disable":
                    element.setAttribute("title","Enable")
                    element.setAttribute("value","o")
                else:
                    element.setAttribute("title","Disable")
                    element.setAttribute("value","x")
                self.buttonClicked.emit(element.nextSibling().attribute("id"))
            return
        elif element.hasClass("editButton"):
            if element.attribute("title") == "Save":
                if self.currently_edited_block_element is not None:
                    self.stopEdition()
        self.currently_selected_block_element = hittestresult.enclosingBlockElement()

        if len(html):
            if self.currently_edited_block_element is not None:
                if self.currently_selected_block_element.hasAttribute("id"):
                        if self.currently_edited_block_element.hasAttribute("id"):
                            if self.currently_selected_block_element.attribute("id") == self.currently_edited_block_element.attribute("id"):
                                return
            self.TextSelected.emit()
        else:
            if self.currently_selected_block_element.hasAttribute("id"):
                self.mouseClicked.emit(self.currently_selected_block_element.attribute("id"))
    
    def mouseDoubleClickEvent (self, event):
        """
        """
        if self.currently_edited_block_element is not None:
            if self.currently_edited_block_element.attribute("contenteditable")=="true":
                hittestresult = self.currentframe.hitTestContent(event.pos())
                if hittestresult:
                    element = hittestresult.element()
                    enclosing_element = hittestresult.enclosingBlockElement()
                    if enclosing_element.hasAttribute("id"):
                        if self.currently_edited_block_element.hasAttribute("id"):
                            if enclosing_element.attribute("id") != self.currently_edited_block_element.attribute("id"):
                                self.stopEdition()
                            else:
                                QWebView.mouseDoubleClickEvent(self,event)
                        else:
                            self.stopEdition()
                    else:
                        self.stopEdition()
                return
        hittestresult = self.currentframe.hitTestContent(event.pos())
        element = hittestresult.element()
        self.currently_edited_block_element = hittestresult.enclosingBlockElement()
        self.saveButton = self.currently_edited_block_element.lastChild()
        
        if self.currently_edited_block_element.lastChild().previousSibling().tagName() == "CODE":
            self.currently_edited_block_element=self.currently_edited_block_element.lastChild().previousSibling()
        else:
            self.saveButton = self.currently_edited_block_element.parent().lastChild()
        if not self.currently_edited_block_element.hasAttribute("id"):
            self.currently_edited_block_element = None
            return
        
        #cleaning the element
        replacement = self.currently_edited_block_element.toInnerXml()
        replacement = re.sub(re.compile(r'</?span.*?>'), '', replacement)
        self.currently_edited_block_element.setInnerXml (replacement)
        self.currently_edited_block_element.setAttribute("contenteditable","true")
        self.currently_edited_block_element.setAttribute("title","Double click outside the edition area to validate the modifications.")
        self.saveButton.setAttribute("visible","true")
     
class MainPage(QWidget):
    """
    """
    def __init__(self, parent):
        """
        """
        super(MainPage, self).__init__()
        self.__core = parent
        self.sshLogs = ""
        self.ignored_lines = []
        self.multiselection = False

        if DEBUGMODE: self.core().debug().addLogWarning("Debug mode activated")
        
        self.createWidgets()
        self.createConnections()
        
    def core(self):
        """
        """
        return self.__core
    
    def createConnections(self):
        """
        """
        self.readButton.clicked.connect(self.onRead)
        self.readFromClipboardButton.clicked.connect(self.onReadFromClipboard)
        self.exportButton.clicked.connect(self.onImport)
        self.refreshButton.clicked.connect(self.refreshParsing)
        self.sshOutput.mouseClicked.connect(self.onLineClicked)
        self.sshOutput.TextSelected.connect(self.onTextSelected)
        self.sshOutput.webViewEdited.connect(self.onWebViewEdited)
        self.sshOutput.buttonClicked.connect(self.onDisableButtonClickedInWebView)
        self.sshOutput.insertButtonClicked.connect(self.onInsertButtonClickedInWebView)
        self.actsTable.doubleClicked.connect( self.onItemDoubleClicked)
        self.actsTable.clicked.connect( self.onCellClicked)
        self.actsTable.model.dataChanged.connect( self.onDataChanged)
        self.actsTable.insertLineSignal.connect( self.onDataInserted)
        self.promptView.eraseLineSignal.connect(self.onPromptChangedOrErased)
        self.promptView.model.dataChanged.connect(self.onPromptChangedOrErased)

    def createWidgets(self):
        """
        """
        self.readButton = QPushButton("&Read SSH log file\n(text File)")
        self.readFromClipboardButton = QPushButton("&Read from Clipboard")
        self.exportButton = QPushButton("&Import in %s" % Settings.instance().readValue( key = 'Common/product-name' ))
        self.exportButton.setEnabled(False)
        self.refreshButton = QPushButton("&Reset Data")
        self.refreshButton.setEnabled(False)
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("ip")
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("login")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        self.promptView = PromptsTableView(self, core=self.core())
        
        self.sshOutput = CustomQWebView()
        self.sshOutput.page().setLinkDelegationPolicy (QWebPage.DelegateAllLinks)

        self.actsTable = ActionsTableView(self, core=self.core())
        
        tabWidget = QTabWidget()
        tabWidget.addTab(self.sshOutput, "Terminal View")
        tabWidget.addTab(self.actsTable, "Table View")
        
        self.caption1 = QLabel("command to send")
        self.caption2 = QLabel("expected text")
        self.caption3 = QLabel("ignored text")
        
        self.caption12 = QLabel()
        self.caption22 = QLabel()
        self.caption32 = QLabel()
        
        green = QPixmap(30, 15)
        green.fill(QColor(100,254,46,255))
        red = QPixmap(30, 15)
        red.fill(QColor(254,154,46,255))
        grey = QPixmap(30, 15)
        grey.fill(QColor(189,189,189,255))

        self.caption12.setPixmap(green)
        self.caption22.setPixmap(red)
        self.caption32.setPixmap(grey)
        formlt = QFormLayout()
        formlt.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        formlt.setLabelAlignment(Qt.AlignCenter)
        formlt.addRow(self.caption12, self.caption1)
        formlt.addRow(self.caption22, self.caption2)
        formlt.addRow(self.caption32, self.caption3)
        layoutWidgetCaption = QFrame(self)
        layoutWidgetCaption.setLayout(formlt)
        formlayout = QFormLayout()
        formlayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        formlayout.setLabelAlignment(Qt.AlignCenter)

        formlayout.addRow('Destination Host:', self.ip_edit)
        formlayout.addRow('Login:', self.login_edit)
        formlayout.addRow('Password:', self.password_edit)
        formlayout.addRow('Prompts:', self.promptView)
        formlayout.addRow('Caption', layoutWidgetCaption)
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(QLabel("Controls"))
        rightLayout.addLayout(formlayout)
        rightLayout.addWidget(self.readButton)
        rightLayout.addWidget(self.readFromClipboardButton)
        rightLayout.addWidget(self.exportButton)
        rightLayout.addWidget(self.refreshButton)

        rightLayout.addStretch(1)

        splitter2 = QSplitter(self)
        splitter2.addWidget(tabWidget)
        layoutWidget3 = QFrame(self)
        layoutWidget3.setLayout(rightLayout)
        splitter2.addWidget(layoutWidget3)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(splitter2)

        self.setLayout(mainLayout)
    
    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Control):
            self.multiselection = True
        QWidget.keyPressEvent(self,event)
    
    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key_Control):
            self.multiselection = False
        QWidget.keyPressEvent(self,event)
    
    def handleFocusIn(self, element_name):
        """
        """
        QtGui.QMessageBox.information(
            self, "HTML Event", "Focus In: " + element_name)

    def handleFocusOut(self, element_name):
        """
        """
        QtGui.QMessageBox.information(
            self, "HTML Event", "Focus Out: " + element_name)
    
    def onPromptChangedOrErased(self, prompt):
        """
        Called when a prompt is changed or erased from the list
        """
        self.refreshParsing()
        
    def refreshParsing(self):
        """
        Refreshing the parsing
        """
        self.parseSSHLogs(self.sshLogs, prompts=self.promptView.model.getData())
        
    def onCellClicked(self,index, scroll=True):
        """
        """
        id = self.actsTable.model.getValueRow(index)['action-id']
        action_name = self.actsTable.model.getValueRow(index)['action-name']
        if action_name == "SEND":
            anchor="c%s"%id
        else:
            anchor="o%s"%id
        if scroll:
            self.sshOutput.page().mainFrame().scrollToAnchor(anchor)

    def onLineClicked(self, hrefContent):
        """
        Called by the webview when a line is clicked
        """
        id=int(hrefContent[1:])
        
        if id>0:
            row = self.getTableRowFromElementId(hrefContent)
            if row >-1:
                self.actsTable.selectRow(row)
                
    def onWebViewEdited(self, id):
        if len(id):
            if id[0]=='c':
                element=self.sshOutput.page().mainFrame().documentElement().findFirst('code[id="%s"]'%id)
            else:
                element=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="%s"]'%id)
            row = self.getTableRowFromElementId(id)
            extractedhtml=re.sub(re.compile(r'</?br.*?>'), '\n',element.toInnerXml())
            extractedhtml = re.sub(re.compile(r'<.*?>'), '', extractedhtml)
            self.actsTable.model.setDataFromRowColumn(row,COL_VALUE,html.unescape(extractedhtml))
            return
        
    def onDataChanged(self, indexStart, indexEnd):
        """
        """
        if indexStart == indexEnd: #1 cell changed
            if indexStart.column() == COL_VALUE:
                action_properties = self.actsTable.model.getValueRow(indexStart)
                action = action_properties['action-name']
                id = action_properties['action-id']
                value = action_properties['action-value']
                if not action_properties["action-editable"]:
                    if action == "EXPECT":
                        element=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id)
                        if action_properties['action-type'] == "CONTAINS":
                            self.highlightText(element, value, False)
                        else:
                            self.highlightText(element, value, True)
                else:# COMMAND OR Editable EXPECT
                    if action == "SEND": #COMMAND                        
                        element=self.sshOutput.page().mainFrame().documentElement().findFirst('code[id="c%s"]'%id)
                        if element.toPlainText().find(value)==-1:
                            element.setPlainText (value)
                            self.actsTable.model.setEnableDisableCommand(indexStart.row(), value=False)
                        if not action_properties['action-disable']:
                            self.highlightText(element, value, False)
                        
                    else:#EXPECTED RESPONSE
                        element=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id)
                        if action_properties['action-type'] == "CONTAINS":
                            if type(value) is list:
                                value = value[len(value)-1]
                            if len(value)==0 or element.toPlainText().find(value)==-1:
                                element.setPlainText (value)
                            if not action_properties['action-disable']:
                                self.highlightText(element, value, False)
                        else:#IF REGEX, no text is inserted in the webview
                            if not action_properties['action-disable']:
                                self.highlightText(element, value, True)
        elif indexStart.column() == COL_DISABLE or (indexStart.column() == -1 and indexEnd.column()>0):
            id = self.actsTable.model.getValueRow(indexEnd)['action-id']
            disable = self.actsTable.model.getValueRow(indexEnd)['action-disable']
            self.enableDisableCommandInWebView(int(id),disable)
                
    def getTableRowFromElementId(self,id):
        """
        """
        if id[0]=="c":
            row = int(id[1:])*2-1
        else:
            row = int(id[1:])*2
        return row

    def onDisableButtonClickedInWebView(self, id):
        """
        """
        row=self.getTableRowFromElementId(id)
        self.actsTable.model.setEnableDisableCommand(row)
    
    def onItemDoubleClicked(self, index):
        """
        Disable a given command, excluding it from the sequence
        """
        
        if index.column() == COL_VALUE:
            return
        if index.column() == COL_TYPE:
            action_properties = self.actsTable.model.getValueRow(index)
            action = action_properties['action-name']
            if action == "EXPECT":
                id = action_properties['action-id']
                element=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id)
                if action_properties['action-type'] == "CONTAINS":
                    self.actsTable.model.setData(index, "REGEX")
                    self.highlightText(element, action_properties['action-value'], True)
                else:
                    self.actsTable.model.setData(index, "CONTAINS")
                    self.highlightText(element, action_properties['action-value'], False)
                return
        else:
            self.actsTable.model.setEnableDisableCommand(index.row())

    def enableDisableCommandInWebView(self, id, disable=None):
        """
        """
        if id>0:
            elements = [self.sshOutput.page().mainFrame().documentElement().findFirst('code[id="c%s"]'%id)]
        else:
            elements = []
        elements += self.sshOutput.page().mainFrame().documentElement().findAll('p[id="o%s"]'%id)
   
        for element in elements:
            replacement = element.toInnerXml()
            replacementtext = element.toPlainText()
            replacement = re.sub(re.compile(r'</?span.*?>'), '', replacement)

            row = self.getTableRowFromElementId(element.attribute("id"))
                
            if row >-1:
                text_to_set = html.unescape(re.sub(re.compile(r'</?br.*?>'), '\n',replacement))#html2text.html2text(replacement)
                if self.actsTable.model.getData()[row]['action-value']!=text_to_set:
                    self.actsTable.model.setDataFromRowColumn(row, COL_VALUE, text_to_set)
            element.setInnerXml (replacement)
            if disable is None:
                if element.hasClass("command"):
                    element.removeClass("command")
                    element.addClass("excluded_command")
                elif element.hasClass("excluded_command"):
                    element.removeClass("excluded_command")
                    element.addClass("command")
                elif element.hasClass("output_line"):
                    element.removeClass("output_line")
                    element.addClass("excluded_output_line")
                elif element.hasClass("excluded_output_line"):
                    element.removeClass("excluded_output_line")
                    element.addClass("output_line")
            elif disable:
                if element.hasClass("command"):
                    element.removeClass("command")
                    element.addClass("excluded_command")
                elif element.hasClass("output_line"):
                    element.removeClass("output_line")
                    element.addClass("excluded_output_line")
            else:
                if element.hasClass("excluded_command"):
                    element.removeClass("excluded_command")
                    element.addClass("command")
                elif element.hasClass("excluded_output_line"):
                    element.removeClass("excluded_output_line")
                    element.addClass("output_line")
  
    def onTextSelected(self):
        """
        Called by the webview when a text is selected
        """
        selected_html=re.sub(re.compile(r'</?br.*?>'), '\n',self.sshOutput.selectedHtml())
        selected_html = re.sub(re.compile(r'<.*?>'), '', selected_html)
        if len(selected_html)==0:
            return
        element=self.sshOutput.currently_selected_block_element
        
        
        if element is not None:
            if element.hasAttribute("id"):
                id=int(element.attribute("id")[1:])
                
                if id>0:
                    row = self.getTableRowFromElementId(element.attribute("id"))
                    
                    if row >-1:
                        
                        self.actsTable.selectRow(row)
                        text_to_set = html.unescape(selected_html)

                        if self.multiselection:
                            text_from_cell = self.actsTable.model.getData()[row]['action-value']
                            if type(text_from_cell) is list:
                                text_from_cell.append(text_to_set)
                                text_to_set = text_from_cell
                            else:
                                text_to_set = [text_from_cell,text_to_set]

                        self.actsTable.model.setDataFromRowColumn(row, COL_VALUE, text_to_set)
                        self.actsTable.model.setDataFromRowColumn(row, COL_DISABLE, False)

    def highlightText(self, element, text, regexp=False):
        """
        """
        if type(text) is list:
            text = text[len(text)-1]
        replacement = element.toInnerXml()
        if self.multiselection is False:
            replacement = re.sub(re.compile(r'</?span.*?>'), '', replacement)
        replacement = re.sub(re.compile(r'</?br.*?>'), '\n', replacement)
        replacement = html.unescape(replacement)

        if element.hasClass("command"):
            element.removeClass("command")
            element.addClass("excluded_command")
            replacement = replacement.replace(text,'</span><span class="command" contenteditable="false">' + text + '</span><span class="excluded_command">')
            element.setInnerXml ('<span class="excluded_command">' + replacement.replace("\n","<br/>") + '</span>')

        elif element.hasClass("excluded_command"):
            replacement = replacement.replace(text,'</span><span class="command" contenteditable="false">' + text + '</span><span class="excluded_command">')
            element.setInnerXml ('<span class="excluded_command">' + replacement.replace("\n","<br/>") + '</span>')
            
        elif element.hasClass("output_line"):
            element.removeClass("output_line")
            if regexp:
                replacement = re.sub(re.compile(r'('+text+')',re.S), '</span><span class="output_line" contenteditable="false">\\1</span><span class="excluded_output_line">',replacement)
            else:
                replacement = replacement.replace(text,'</span><span class="output_line" contenteditable="false">' + text + '</span><span class="excluded_output_line">')
            element.setInnerXml ('<span class="excluded_output_line">' + replacement.replace("\n","<br/>") + '</span>')
            element.addClass("excluded_output_line")
            
        elif element.hasClass("excluded_output_line"):
            if regexp:
                replacement = re.sub(re.compile(r'('+text+')',re.S), '</span><span class="output_line" contenteditable="false">\\1</span><span class="excluded_output_line">',replacement)
            else:
                replacement = replacement.replace(text,'</span><span class="output_line" contenteditable="false">' + text + '</span><span class="excluded_output_line">')
            element.setInnerXml ('<span class="excluded_output_line">' + replacement.replace("\n","<br/>") + '</span>')
                        
        
    def onReloadSettings(self):
        """
        Called by the core when settings are updated
        """
        pass
        
    def insertData(self, data):
        """
        Called by the core when new data are received
        """
        pass
        
    def onInsertButtonClickedInWebView(self,idtoset):
        """
        """
        element1=self.sshOutput.page().mainFrame().documentElement().findFirst('input.button[rel="%s"]'%idtoset)
        elementparent = element1.parent()
        element1.removeFromDocument()
        elementparent.removeFromDocument()
        row = self.getTableRowFromElementId("c" + str(int(idtoset)+1))
        self.onDataInserted(row, scroll=False)
        
    def onDataInserted(self,row, scroll=True):
        """
        Called when the user inserts some new data
        """
        if row == 0:
            row=1
        elif row >= len(self.actsTable.model.getData())-1:
            row=len(self.actsTable.model.getData())-1

            id_before = int(self.actsTable.model.getData()[row]["action-id"])
            current_id = id_before+1
            prompt = self.actsTable.model.getData()[row]["action-prompt"]
            element1=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="c%s"]'%id_before)
            element2=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id_before)

            lines_to_insert = '<div contenteditable="false" class="container" title="insert"><input type="button" rel="%s" value="+" class="button" title="Add">-</div>'%(id_before)
            lines_to_insert += '<div contenteditable="false" class="container"><input type="button" value="o" class="button" title="Enable">'
            lines_to_insert += '<p contenteditable="false" id="c%s"><code class="prompt">%s</code> <code id="c%s" contenteditable="false" class="excluded_command" title="Select some text to filter or double-click to edit.">[TBD]</code><input type="button" value="save" visible="false" class="editButton" title="Save"></p>'%(current_id,prompt,current_id)
            lines_to_insert += '<p id="o%s" contenteditable="false" class="excluded_output_line" title="Select some text to filter or double-click to edit.">[TBD]</p>'%(current_id)
            lines_to_insert += '<input type="button" value="save" visible="false" class="editButton" title="Save"></div>'
            lines_to_insert += '<div contenteditable="false" class="container" title="insert"><input type="button" rel="%s" value="+" class="button" title="Add">-</div>'%(current_id)
            
            if element2 is not None:
                elementparent = element2.parent()
                elementparent.appendOutside(lines_to_insert)
            elif element1 is not None:
                elementparent = element1.parent()
                elementparent.appendOutside(lines_to_insert)
            self.actsTable.model.insertRows(row+1, above=False)
            self.actsTable.selectRow(row)
            index = self.actsTable.model.index(row, COL_ID)
            self.onCellClicked(index, scroll)
            return
        elif self.actsTable.model.getData()[row]["action-name"]=="EXPECT" and row>0:
            row-=1
        current_id=int(self.actsTable.model.getData()[row]["action-id"])
        id_before=current_id-1
        line = self.actsTable.model.getData()[row]["action-line"]
        prompt = self.actsTable.model.getData()[row]["action-prompt"]
        for i in range(len(self.actsTable.model.getData())-1,row,-2):
            id=int(self.actsTable.model.getData()[i]["action-id"])
            element1=self.sshOutput.page().mainFrame().documentElement().findFirst('code[id="c%s"]'%id)
            if element1 is not None:
                element1.setAttribute ("id", "c%s"%str(id+1))
            element2=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="c%s"]'%id)
            if element2 is not None:
                element2.setAttribute ("id", "c%s"%str(id+1))
            element3=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id)
            if element3 is not None:
                element3.setAttribute ("id", "o%s"%str(id+1))
            element4=self.sshOutput.page().mainFrame().documentElement().findFirst('input[rel="%s"]'%id)
            if element4 is not None:
                element4.setAttribute ("rel", "%s"%str(id+1))

        if id_before >0:
            element1=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="c%s"]'%id_before)
            element2=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id_before)
        elif id_before==0:
            element1=None
            element2=self.sshOutput.page().mainFrame().documentElement().findFirst('p[id="o%s"]'%id_before)

        lines_to_insert = '<div contenteditable="false" class="container" title="insert"><input type="button" rel="%s" value="+" class="button" title="Add">-</div>'%(id_before)
        lines_to_insert += '<div contenteditable="false" class="container"><input type="button" value="o" class="button" title="Enable">'
        lines_to_insert += '<p contenteditable="false" id="c%s"><code class="prompt">%s</code> <code id="c%s" contenteditable="false" class="excluded_command" title="Select some text to filter or double-click to edit.">[TBD]</code><input type="button" value="save" visible="false" class="editButton" title="Save"></p>'%(current_id,prompt,current_id)
        lines_to_insert += '<p id="o%s" contenteditable="false" class="excluded_output_line" title="Select some text to filter or double-click to edit.">[TBD]</p>'%(current_id)
        lines_to_insert += '<input type="button" value="save" visible="false" class="editButton" title="Save"></div>'
        lines_to_insert += '<div contenteditable="false" class="container" title="insert"><input type="button" rel="%s" value="+" class="button" title="Add">-</div>'%(current_id)
        
        if element2 is not None:
            elementparent = element2.parent()
            elementparent.appendOutside(lines_to_insert)
        elif element1 is not None:
            elementparent = element1.parent()
            elementparent.appendOutside(lines_to_insert)
        
        self.actsTable.model.insertRows(row)
        self.actsTable.selectRow(row)
        index = self.actsTable.model.index(row, COL_ID)
        self.onCellClicked(index, scroll)

    def onReadFromClipboard(self):
        """
        """
        self.sshLogs = QApplication.clipboard().text()
        self.parseSSHLogs(self.sshLogs)
        
    def onRead(self):
        """
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open SSH log file"),
                            '', "text file (*.txt)")
        if not len(fileName):
            return

        # read the file
        file = QFile(fileName)
        if not file.open(QIODevice.ReadOnly):
            QMessageBox.warning(self, self.tr("Error opening text file"), self.tr("Could not open the file ") + fileName)
            return

        self.sshLogs = file.readAll()
        self.sshLogs = str(self.sshLogs, "utf8")
        self.parseSSHLogs(self.sshLogs)
        
    def parseSSHLogs(self, sshLogs, prompts=None):
        """
        Parse the ssh logs
        """
        parser = SSHParser.SSHParser()
        text = parser.txt2html(sshLogs, prompts)
        header = """<head>
                    <meta charset="utf-8">
                    <title>Test</title>
                    <style type="text/css">
                    
                    body {
                        max-width: 20cm;
                        margin-left: auto;
                        margin-right: auto;
                        text-align: justify;
                    }
                    a {
                        color: black;
                        text-decoration: none;
                    }
                    .prompt {
                        background-color: #FE2E2E
                    }
                    .command {
                        background-color: #64FE2E
                    }
                    .output_line {
                        background-color: #FE9A2E
                    }
                    .excluded_command {
                        background-color: #BDBDBD
                    }
                    .excluded_output_line {
                        background-color: #BDBDBD
                    }
                    .output_line:hover {
                        background-color: #FE9A2E;
                        border-style: solid;
                        border-color: black;
                        border-width: 2px;
                    }
                    .command:hover {
                        background-color: #64FE2E;
                        border-style: solid;
                        border-color: black;
                        border-width: 2px;
                    }
                    .excluded_command:hover {
                        background-color: #A4A4A4;
                        border-style: solid;
                        border-color: black;
                        border-width: 2px;
                    }
                    </style>
                </head>"""

        steps = []
        try:
            if len(parser.ip): self.ip_edit.setText(parser.ip)
            if len(parser.login): self.login_edit.setText(parser.login)
            if len(parser.prompts): self.promptView.loadTable(parser.prompts)
            for index in parser.commands_line_indices:
                
                stp1 = {}
                stp2 = {}
                command = parser.commands_dict[index]["command"]
                if len(command):
                    stp1["action-value"] = parser.commands_dict[index]["command"]
                    stp1["action-line"] = parser.commands_dict[index]["line_index"]
                    stp1["action-prompt"] = parser.commands_dict[index]["prompt"]
                    stp1["action-name"] = "SEND"#parser.commands_dict[index]["command"]
                    stp1["action-id"] = index
                    stp1["action-type"] = "FIXED"
                    stp1["action-editable"] = True
                    stp1["action-disable"] = False
                    stp2["action-disable"] = False
                else:
                    stp2["action-disable"] = True
                stp2["action-line"] = parser.commands_dict[index]["line_index"]
                stp2["action-prompt"] = parser.commands_dict[index]["prompt"]
                stp2["action-name"] = "EXPECT"
                stp2["action-type"] = "CONTAINS"
                stp2["action-id"] = index
                
                stp2["action-editable"] = False
                if "expected" in parser.commands_dict[index].keys():
                    stp2["action-value"] = parser.commands_dict[index]["expected"]
                    if stp2["action-value"] == "[TO BE DEFINED]":
                        stp2["action-editable"] = True
                else:
                    stp2["action-value"] = ""
                    

                if len(stp1): steps.append(stp1)
                if len(stp2): steps.append(stp2)

        except Exception as e:
            self.core().debug().addLogError( "%s - %s" % (e, parser.commands_dict) )
            QMessageBox.critical(self, self.tr("Error reading shell logs"), "Parser error, more details in debug page." )
            return
        else:
            self.actsTable.loadTable(data=steps)
            self.setHtmlPage()
            if len(steps): 
                self.exportButton.setEnabled(True)
                self.refreshButton.setEnabled(True)

    def setHtmlPage(self):
        """
        """
        header = """<head>
                    <meta charset="utf-8">
                    <title>Test</title>
                    <style type="text/css">
                    
                    body {
                        max-width: 20cm;
                        margin-left: auto;
                        margin-right: auto;
                        text-align: justify;
                    }
                    a {
                        color: black;
                        text-decoration: none;
                    }
                    code {
                        font-family: monospace;
                    }
                    p{
                        width: 750px;
                        font-family: monospace;
                        /*overflow: hidden;
                        text-overflow: ellipsis;
                        word-wrap: break-word;
                        hyphens: auto;
                        white-space: nowrap;*/
                    }
                    [contenteditable="true"]{
                        background-color: #FFFFFF;
                        border-style: solid;
                        border-color: #A9D0F5;
                        border-width: 1px;
                    }
                    .prompt {
                        /*background-color: #FE2E2E;*/
                        background-color: #BDBDBD;
                        /*color: #FF8900;*/
                    }
                    .command[contenteditable="false"] {
                        background-color: #64FE2E
                    }
                    .output_line[contenteditable="false"] {
                        background-color: #FE9A2E
                    }
                    .excluded_command[contenteditable="false"] {
                        background-color: #BDBDBD
                    }
                    .excluded_output_line[contenteditable="false"] {
                        background-color: #BDBDBD
                    }
                    .output_line[contenteditable="false"]:hover {
                        background-color: #FE9A2E;
                        border-style: solid;
                        border-color: black;
                        border-width: 2px;
                    }
                    .command[contenteditable="false"]:hover {
                        background-color: #64FE2E;
                        border-style: solid;
                        border-color: black;
                        border-width: 2px;
                    }
                    .excluded_command[contenteditable="false"]:hover {
                        background-color: #A4A4A4;
                        border-style: solid;
                        border-color: black;
                        border-width: 2px;
                    }
                    .container:hover{
                        background-color: #FFFFFF;
                        border-style: dashed;
                        border-color: #A9D0F5;
                        border-width: 1px;
                    }
                    .tooltip {
                        position: relative;
                        display: inline-block;
                        border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
                    }

                    /* Tooltip text */
                    .tooltip .tooltiptext {
                        visibility: hidden;
                        width: 120px;
                        background-color: black;
                        color: #fff;
                        text-align: center;
                        padding: 5px 0;
                        border-radius: 6px;
                     
                        /* Position the tooltip text - see examples below! */
                        position: absolute;
                        z-index: 1;
                    }

                    /* Show the tooltip text when you mouse over the tooltip container */
                    .tooltip:hover .tooltiptext {
                        visibility: visible;
                    }
                    
                    [property="tooltip2"]{
                        display: inline;
                        position: relative;
                    }
                    
                    [property="tooltip2"]:hover:after{
                        background: #333;
                        background: rgba(0,0,0,.8);
                        border-radius: 5px;
                        bottom: 26px;
                        color: #fff;
                        content: attr(title);
                        left: 20%;
                        padding: 5px 15px;
                        position: absolute;
                        z-index: 98;
                        width: 220px;
                    }
                    
                    [property="tooltip2"]:hover:before{
                        border: solid;
                        border-color: #333 transparent;
                        border-width: 6px 6px 0 6px;
                        bottom: 20px;
                        content: "";
                        left: 50%;
                        position: absolute;
                        z-index: 99;
                    }
                    .button {
                        background-color: #FFFFFF; /* white */
                        float: right;
                        
                        color: grey;
                        padding: 1px 1px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 10px;
                        visibility: hidden;
                        transition-duration: 0.4s;
                    }
                    .button[value="+"] {
                        float: left;
                    }
                    .editButton {
                        background-color: #FFFFFF; /* white */
                        float: right;
                        
                        color: grey;
                        padding: 1px 1px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 10px;
                        visibility: hidden;
                        transition-duration: 0.4s;
                    }
                    .button[value="x"] {
                        /*border: 2px solid grey; /* Grey */
                        color: red;
                    }
                    .button[value="o"] {
                        /*border: 2px solid #4CAF50; /* Green */
                        color: green;
                    }

                    .button[value="o"]:hover {
                        background-color: #64FE2E; /* Green */
                        color: white;
                    }
                    
                    .button[value="x"]:hover {
                        background-color: #BDBDBD; /* Grey */
                        color: white;
                    }
                    .button[value="+"]:hover {
                        background-color: #A1A2FF; /* Grey */
                        color: white;
                    }
                    .container:hover .button {
                        visibility: visible;
                    }
                    /*.container:hover .button[value="o"] {
                        visibility: visible;
                    }
                    .container:hover .button[value="+"] {
                        visibility: visible;
                    }*/
                    .editButton[visible="true"] {
                        visibility: visible;
                        float:none;
                    }
                    .editButton[visible="true"]:hover {
                        background-color: #BDBDBD; /* Grey */
                        color: white;
                    }
                    .container[title="insert"]{
                        width=100%;
                        padding: 1px 1x;
                        color: white;
                    }
                    
                    </style>
                </head>"""
  
        data = self.actsTable.model.getData()
        numberOfLines = len(data)
        html_content = ""
        for row in range(numberOfLines):
            if data[row]['action-name'] == "SEND":
                htmlid = "c%s"%data[row]['action-id']
                if data[row]['action-disable']:
                    htmlclass = "excluded_command"
                else:
                    htmlclass = "command"
                html_content += '<div contenteditable="false" class="container"><input type="button" value="x" class="button" title="Disable">'
                html_content += '<p contenteditable="false" id="%s"><code class="prompt">%s</code> <code contenteditable="false" id="%s" class="command" title="Select some text to filter or double-click to edit.">%s</code><input type="button" visible="false" value="save" class="editButton" title="Save"></p>'%(htmlid,data[row]['action-prompt'],htmlid,data[row]['action-value'])

            else:
                htmlid = "o%s"%data[row]['action-id']
                if data[row]['action-disable']:
                    htmlclass = "excluded_output_line"
                else:
                    htmlclass = "output_line"
                if row==0:
                    html_content += '<div contenteditable="false" class="container"><input type="button" value="x" class="button" title="Disable">'
                html_content +='<p contenteditable="false" id="%s" class="%s" title="Select some text to filter or double-click to edit.">%s</p><input type="button" value="save" visible="false" class="editButton" title="Save">'%(htmlid,htmlclass, data[row]['action-value'].replace("\n","<br/>"))
                html_content += '</div>'
                html_content += '<div contenteditable="false" class="container" title="insert"><input type="button" rel="%s" value="+" class="button" title="Add">-</div>'%(data[row]['action-id'])

        self.sshOutput.setHtml(header + "<body>" + html_content + "</body>" )
    
    def onImport(self):
        """
        """
        actions = self.actsTable.model.getData()
        filtered_actions = []
        for action in actions:
            if action["action-disable"] == False:
                filtered_actions.append(action)
        if DEBUGMODE: self.core().debug().addLogWarning("List actions to import: %s" % filtered_actions)
        
        if not DEBUGMODE: 
            self.core().sendMessage( cmd='import', data = {"ip":self.ip_edit.text(),"login":self.login_edit.text(),
                                                            "password":self.password_edit.text(), "steps": filtered_actions} )
            self.core().hide()
        
class SettingsPage(QWidget):
    """
    """
    ReloadSettings = pyqtSignal()
    def __init__(self, parent):
        """
        """
        super(SettingsPage, self).__init__()
        self.__core = parent
        self.config = None
        
        self.createWidget()
        self.loadCfg()

    def createWidget(self):
        """
        """
        self.inDataEdit = QPlainTextEdit("No settings!")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.inDataEdit)

        self.setLayout(mainLayout)
        
    def loadCfg(self):
        """
        """
        with open( "%s/config.json" % (QtHelper.dirExec()) ) as f:
            CONFIG_RAW = f.read()
        self.config = json.loads(CONFIG_RAW)
        
    def cfg(self):
        """
        """
        return self.config

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # initiliaze settings application, read settings from the ini file
    Settings.initialize()
    
    # initialize logger
    logPathFile = "%s/%s" % ( QtHelper.dirExec(), Settings.instance().readValue( key = 'Trace/file' ) )
    level = Settings.instance().readValue( key = 'Trace/level' )
    size = Settings.instance().readValue( key = 'Trace/max-size-file' )
    nbFiles = int( Settings.instance().readValue( key = 'Trace/nb-backup-max' ) )
    Logger.initialize( logPathFile=logPathFile, level=level, size=size, nbFiles=nbFiles, noSettings=True )
    
    
    # init the core plugin
    MyPlugin = CorePlugin.MainWindow(debugMode=DEBUGMODE)
   
    # create the main  widget   
    WidgetSettings = SettingsPage(parent=MyPlugin)
    MyPlugin.addSettingsPage( widget=WidgetSettings )

    WidgetMain = MainPage(parent=MyPlugin) 
    MyPlugin.addMainPage(  
                            pageName=WidgetSettings.cfg()["plugin"]["name"], 
                            widget=WidgetMain
                        )
                        
                        
    # register the main and settings page of the plugin
    name = Settings.instance().readValue( key = 'Common/name' )
    MyPlugin.configure(
                        pluginName=WidgetSettings.cfg()["plugin"]["name"], 
                        pluginType=WidgetSettings.cfg()["plugin"]["type"],
                        pluginVersion=WidgetSettings.cfg()["plugin"]["version"],
                        pluginDescription=WidgetSettings.cfg()["plugin"]["description"]
                       )

    lic = LICENSE % (WidgetSettings.cfg()["plugin"]["name"], 
                    WidgetSettings.cfg()["plugin"]["version"],
                    name, ','.join(__CONTRIBUTORS__) )   
    aboutPage = "<br/><br/><b>License:</b><br /><span>%s</span>" % lic
    MyPlugin.updateAboutPage(text=aboutPage)
    
    # debug mode
    if DEBUGMODE: 
        MyPlugin.show()
        #MyPlugin.showMaximized()
    
    sys.exit(app.exec_())