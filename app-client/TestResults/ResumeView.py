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
Module to display the resume view
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QColor, QFont, QIcon, QTableView, QAbstractItemView, 
                            QWidget, QVBoxLayout)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, Qt, QModelIndex, pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QColor, QFont, QIcon)
    from PyQt5.QtWidgets import (QTableView, QAbstractItemView, QWidget, QVBoxLayout)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, Qt, QModelIndex, pyqtSignal)
    
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

DEFAULT_HEIGHT  = 80

COL_NUM         = 0
COL_TIMESTAMP   = 1
COL_EVENT       = 2
COL_FROM        = 3
COL_TEXT        = 4

class EventsTableModel2(QAbstractTableModel):
    """
    Events table model
    """
    def __init__(self, hdrs):
        """
        Constructor for events tables
        """
        QAbstractTableModel.__init__(self)
        self.hdrs = hdrs
        self.stored_data = []

    def rowCount(self, parent=None):
        """
        Returns the number of row
        """
        return len(self.stored_data)

    def columnCount(self, parent=None):
        """
        Returns the number of columns
        """
        return len(self.hdrs)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return header data
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.hdrs[section]

        return None

    def data(self, index, role):    
        """
        Set data
        """
        result = None
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.column() == COL_NUM:
                    if int(self.stored_data[ index.row() ]["ihm_id"]) > 1:
                        result = str( (int(self.stored_data[ index.row() ]["ihm_id"])-1) )
                    else:
                        result = self.stored_data[index.row()]['row-pos']
                if index.column() == COL_TIMESTAMP:
                    result = self.stored_data[index.row()]['timestamp']
                if index.column() == COL_EVENT:
                    result = self.stored_data[index.row()]['level'].upper()
                if index.column() == COL_FROM:
                    result = self.stored_data[ index.row() ]['from-component']
                if index.column() == COL_TEXT:
                    short_msg = self.stored_data[ index.row() ]['short-msg']
                    if sys.version_info > (3,): # python 3 support
                        try:
                            result = short_msg.splitlines()[0]
                        except Exception as e:
                            print('error, resume view: unable to split result: %s' % e )
                            result = ''
                    else:
                        try:
                            if len(short_msg):
                                result = short_msg.decode('utf8').splitlines()[0]
                            else:
                                result = ''
                        except UnicodeDecodeError as e:
                            result = short_msg.splitlines()[0]
                        except Exception as e:
                            print('error, resume view: failed to split result: %s' % str(e))
                            result = ''
                            
            elif role == Qt.ForegroundRole :
                if not 'color-text' in self.stored_data[ index.row() ]:
                    return None
                data_col = self.stored_data[ index.row() ]['color-text']
                result = QColor(0, 0, 0)
                result.setNamedColor( data_col )
                
            elif role == Qt.BackgroundColorRole:
                if not 'color' in self.stored_data[ index.row() ]:
                    return None
                data_col = self.stored_data[ index.row() ]['color']
                result = QColor(0, 0, 0)
                result.setNamedColor( data_col )
                
            elif role == Qt.FontRole:
                if index.column() == COL_TEXT:
                    result = QFont()
                    if 'bold' in self.stored_data[ index.row() ]:
                        data_col = self.stored_data[ index.row() ]['bold']
                        result.setBold(data_col)
                    if 'italic' in self.stored_data[ index.row() ]:
                        data_col = self.stored_data[ index.row() ]['italic']
                        result.setItalic(data_col)
                        
            elif role == Qt.DecorationRole:
                if index.column() == COL_TEXT:
                    if not 'level' in self.stored_data[ index.row() ]:
                        return None
                    data_col = self.stored_data[ index.row() ]['level']
                    if data_col == 'timer-started':
                        result = QIcon(":/timer.png")
                    if data_col == 'timer-stopped':
                        result = QIcon(":/timer_ok.png")
                    if data_col == 'timer-exceeded':
                        result = QIcon(":/timer_ko.png")
                    if data_col == 'received':
                        result = QIcon(":/arrow_left.png")
                    if data_col == 'send':
                        result = QIcon(":/arrow_right.png")
                    if data_col == 'step-failed':
                        result = QIcon(":/steps.png")
        return  result

    def setData(self, index, value, role=Qt.EditRole):
        """
        Set data
        """
        if not index.isValid(): return False
        return True

    def insertAtEnd(self, data):
        """
        Insert row at the end
        """
        row_pos = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_pos, row_pos)
        self.stored_data.append( data )
        self.endInsertRows()
        if row_pos == 0: 
            if sys.version_info > (3,):
                self.beginResetModel() 
                self.endResetModel()
            else:
                self.reset()
                
        return row_pos

    def clear(self):
        """
        Clear
        """
        self.stored_data = []

        if sys.version_info > (3,):
            self.beginResetModel() 
            self.endResetModel()
        else:
            self.reset()
            
    def flags(self, index):
        """
        Set flags
        """
        if not index.isValid(): return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

    def getData(self, index):
        """
        Return data according to the index passed on argument
        """
        return self.stored_data[index.row()]

class EventsTableView(QTableView):
    """
    Events table view
    """
    def __init__(self, parent):
        """
        Contructs ParametersTableView table view

        @param parent: 
        @type parent:
        """
        QTableView.__init__(self, parent)
        self.model = None

        self.createWidgets()

    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.model = EventsTableModel2( hdrs=['No.', 'Timestamp', 'Event Type', 'Component', 'Text' ] )
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setEnabled(False)
        
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(True)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setStyleSheet("gridline-color: white;")
             
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(False)

        self.setColumnWidth(COL_NUM, 50) # No.
        self.setColumnWidth(COL_TIMESTAMP, 80) # timestamp
        self.setColumnWidth(COL_EVENT, 110) # timestamp
        self.setColumnWidth(COL_FROM, 220) # component
    
    
    def insertItem(self, dataEvent):
        """
        Insert one item
        """
        row_pos = self.model.insertAtEnd(data=dataEvent)
        self.setRowHeight( row_pos  , 20)

    def clear (self):
        """
        clear contents
        """
        self.model.clear()

class TextualView(QWidget):
    """
    Textual view
    """
    # new in v12.1
    GotoEvent = pyqtSignal(dict)
    # end of new
    def __init__(self, parent):
        """
        Constructs TextualLogView widget 

        @param parent:
        @type parent: 
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.eventId = None

        self.createWidgets()
        self.createConnections()

    def createWidgets (self):
        """
        QtWidgets creation

        QTreeWidget (Timestamp, Component, Text)
         _______________
        |  QStringList  |
        |---------------|
        |               |
        |               |
        |_______________|
        """
        layout = QVBoxLayout()
        
        self.textualViewer = EventsTableView( self )
        
        layout.addWidget(self.textualViewer)
        layout.setContentsMargins(0,0,0,0)
        self.setFixedHeight(DEFAULT_HEIGHT)
        self.setLayout(layout)
    
    def createConnections (self):
        """
        QtSignals connection
        """
        self.textualViewer.clicked.connect(self.onClick)

    def onClick(self, index):
        """
        On click
        """
        dataRow = self.textualViewer.model.getData(index)
        self.GotoEvent.emit( dataRow )

    def selectionChanged(self, selected, deselected):
        """
        On selection changed
        """
        index = selected.indexes()[0]
        dataRow = self.textualViewer.model.getData(index)
        self.GotoEvent.emit( dataRow )

    def addEvent (self, event, rowp, ihmId=0):
        """
        Adds event

        #       {'task-id': '15', 'from': 'admin', 'test-id': '1', 'level': 'info', 'from-compon
        #ent': 'TESTSUITE', 'timestamp': '19:45:04.7822', 'short-msg': 'BEGIN', 'script_n
        #ame': 'Noname1', 'color': '#E7E6FF', 'script_id': '15_1_0', 'event': 'script'}

        @param event:
        @type event: 
        """
        if event['level'] == 'step-failed' or event['level'] == 'error'   :
            event['row-pos'] = rowp
            # event['ihm_id'] = ihmId+1
            self.textualViewer.setEnabled(True)
            self.textualViewer.insertItem( dataEvent=event)
            
            if event['event'] == 'script':
                self.eventId =  event['script_id']
            elif event['event'] == 'testcase':
                self.eventId =  event['tc_id']
            else:
                self.eventId = None

    def reset (self):
        """
        Clear the textual log view
        Removes all events
        """
        self.eventId = None
        self.textualViewer.clear()
        self.textualViewer.setEnabled(False)
        



