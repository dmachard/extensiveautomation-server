#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive automation project
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
Module to display events logs
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QColor, QFont, QIcon, QSortFilterProxyModel, QTableView, 
                            QFrame, QAbstractItemView, QWidget, QVBoxLayout)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, Qt, QModelIndex, QTimer, 
                            pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QColor, QFont, QIcon)
    from PyQt5.QtWidgets import (QTableView, QFrame, QAbstractItemView, 
                                QWidget, QVBoxLayout)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, Qt, QModelIndex, QTimer, 
                            pyqtSignal, QSortFilterProxyModel)
                            
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

import Settings


try:
    xrange
except NameError: # support python3
    xrange = range
    
COL_NUM         = 0
COL_TIMESTAMP   = 1
COL_EVENT       = 4
COL_FROM        = 5
COL_FROM_LEVEL  = 2
COL_TO_LEVEL    = 3
COL_TEXT        = 6

ROW_HEIGHT      = 20

class EventsTableModel2(QAbstractTableModel):
    """
    Events table model
    """
    def __init__(self, hdrs):
        """
        Events table model
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
        Returns the number of column
        """
        return len(self.hdrs)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Handle header data
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.hdrs[section]

        return None

    def data(self, index, role):    
        """
        Handle data
        """
        result = None
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.column() == COL_NUM:
                    if self.stored_data[index.row()]['ihm_id'] > 0 :
                        result = str( self.stored_data[index.row()]['ihm_id']-1 )
                    else:
                        result = str( index.row() )
                    
                if index.column() == COL_TIMESTAMP:
                    result = self.stored_data[index.row()]['timestamp']
                if index.column() == COL_EVENT:
                    result = self.stored_data[index.row()]['level'].upper()
                if index.column() == COL_FROM:
                    result = self.stored_data[ index.row() ]['from-component']
                if index.column() == COL_FROM_LEVEL:
                    result = self.stored_data[ index.row() ]['from-level']
                if index.column() == COL_TO_LEVEL:
                    result = self.stored_data[ index.row() ]['to-level']
                if index.column() == COL_TEXT:
                    short_msg = self.stored_data[ index.row() ]['short-msg']
                    multiline = False
                    if 'multiline' in self.stored_data[ index.row() ]:
                        multiline = self.stored_data[ index.row() ]['multiline']
                    if multiline:
                        if sys.version_info > (3,): # py3 support
                            result = short_msg
                        else:
                            try:
                                result = short_msg.decode('utf8')
                            except Exception as e:
                                result = short_msg
                    else:
                        if not len(short_msg):
                            result = ''
                        else:
                            if sys.version_info > (3,): # py3 support
                                result = short_msg.splitlines()[0]
                            else:
                                try:
                                    result = short_msg.decode('utf8').splitlines()[0]
                                except Exception as e:
                                    result = short_msg.splitlines()[0]
                                    
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
                        if isinstance(data_col, bool):
                            result.setBold(data_col)
                    if 'italic' in self.stored_data[ index.row() ]:
                        data_col = self.stored_data[ index.row() ]['italic']
                        if isinstance(data_col, bool):
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
        data.update( {'row_id': row_pos } )
        self.stored_data.append( data )
        self.endInsertRows()
        if row_pos == 0: 
            # self.reset()
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
        # self.reset()
        if sys.version_info > (3,):
            self.beginResetModel() 
            self.endResetModel()
        else:
            self.reset()
            
    def flags(self, index):
        """
        Hanhle falgs
        """
        if not index.isValid(): return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

    def getData(self, index):
        """
        Return data
        """
        try:
            ret = self.stored_data[ int(index) ]
        except Exception as e:
            ret = None
        return ret

class MultiQSortFilterProxyModel(QSortFilterProxyModel):
    """
    Multi filter for proxy model
    """
    def __init__(self, parent):
        """
        Mutti qsort filter for proxy model
        """
        QSortFilterProxyModel.__init__(self, parent)

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
        self.scrollingActivated = False

        self.createWidgets()

    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.model = EventsTableModel2( hdrs=['No.', 'Timestamp', 'From', 'To', 'Event Type', 'Component Type', 'Text' ] )
        if  QtHelper.str2bool( Settings.instance().readValue( key = 'TestRun/auto-scrolling-textual' ) ):
            self.activeAutoscrolling()

        self.proxyModel = MultiQSortFilterProxyModel(self)
        self.proxyModel.setDynamicSortFilter(True)

        self.setModel(self.proxyModel)
        self.setSortingEnabled(False)

        self.proxyModel.setSourceModel(self.model)

        self.setFrameShape(QFrame.NoFrame)
        self.setShowGrid(True)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setStyleSheet("""
            gridline-color: white; 
            selection-color: %s;
            selection-background-color: %s;
        """ % (
                Settings.instance().readValue( key = 'TestRun/textual-text-selection-color' ), 
                Settings.instance().readValue( key = 'TestRun/textual-selection-color' ), 
              )
        )
                
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(False)

        self.setColumnWidth(COL_NUM, 50) # No.
        self.setColumnWidth(COL_TIMESTAMP, 80) # timestamp
        self.setColumnWidth(COL_EVENT, 110) # timestamp
        self.setColumnWidth(COL_FROM, 150) # component
        widthFrom = Settings.instance().readValue( key = 'TestRun/column-from-width' )
        self.setColumnWidth(COL_FROM_LEVEL, int(widthFrom) ) # from
        widthTo = Settings.instance().readValue( key = 'TestRun/column-to-width' )
        self.setColumnWidth(COL_TO_LEVEL, int(widthTo) ) # to
    
    def verticalScrollbarValueChanged(self, value):
        """
        On vertical scrollbar value changed
        """
        QTableView.verticalScrollbarValueChanged(self, value)
        scrollbar = self.verticalScrollBar()

    def activeAutoscrolling(self):
        """
        Active autoscrolling
        """
        self.scrollingActivated = True
        self.model.rowsInserted.connect(self.autoScroll)
    
    def disableAutoscrolling(self):
        """
        Disable autoscrolling
        """
        self.scrollingActivated = False
        self.model.rowsInserted.disconnect(self.autoScroll)

    def autoScroll(self):
        """
        On autoscroll
        """
        QTimer.singleShot(0, self.scrollToBottom)

    def insertItem(self, dataEvent):
        """
        Insert item
        """
        row_pos = self.model.insertAtEnd(data=dataEvent)
        self.setRowsHeight()

        return row_pos

    def clear (self):
        """
        clear contents
        """
        self.model.clear()

    def setRowsHeight(self):
        """
        Set rows height
        """
        for i in xrange(len(self.model.stored_data)):
            rowHeight = ROW_HEIGHT
            if 'multiline' in self.model.stored_data[i]:
                if self.model.stored_data[i]['multiline']:
                    rowHeight = ROW_HEIGHT*len(self.model.stored_data[i]['short-msg'].splitlines())
            self.setRowHeight( i  , rowHeight )

class TextualView2(QWidget):
    """
    Textual view
    """
    # new in v12.1
    ShowHexaView = pyqtSignal(object, object, object)
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
        self.expectedEventId = None
        self.steps = {}
        self.endEventDetected = False

        self.createWidgets()
        self.createConnections()

    def createWidgets (self):
        """
        QtWidgets creation

        QTreeWidget (Timestamp, Component, Text)
         _______________
        |               |
        |---------------|
        |               |
        |               |
        |_______________|
        """
        layout = QVBoxLayout()
        
        self.textualViewer = EventsTableView( self )
        
        layout.addWidget(self.textualViewer)
        
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    
    def createConnections (self):
        """
        QtSignals connection
        """
        self.textualViewer.selectionModel().selectionChanged.connect(self.selectionChanged)

    def updateFilterRegExp(self, regExp):
        """
        Update the filter regexp
        """
        self.textualViewer.proxyModel.setFilterRegExp(regExp)
        self.textualViewer.setRowsHeight()

    def updateFilterColumn(self, currentIndex):
        """
        Update the filter column
        """
        self.textualViewer.proxyModel.setFilterKeyColumn( currentIndex )
        self.textualViewer.setRowsHeight()

    def selectionChanged(self, selected, deselected):
        """
        On selection changed
        """
        if not selected.indexes():
            return

        index = selected.indexes()[0]

        # retrieve the first row
        dataRow0 = self.textualViewer.model.getData( 0 )

        if sys.version_info > (3,): # python3 support
            if dataRow0["ihm_id"] > 1:
                newIndex = int(index.data()) - (dataRow0["ihm_id"]-1)
            else:
                newIndex = int(index.data())
        else:
            if dataRow0["ihm_id"] > 1:
                newIndex = int(index.data().toString()) - (dataRow0["ihm_id"]-1)
            else:
                newIndex = int(index.data().toString())
                
        dataRow = self.textualViewer.model.getData( newIndex )
        if dataRow is None:
            return

        data = None
        dataType = None
        shortName = None
        shortName = dataRow['short-msg']
        if 'type-msg' in dataRow:
            dataType = dataRow['type-msg']
        if 'data-msg' in dataRow:
            data = dataRow['data-msg']
        else:
            if 'short-msg' in dataRow:
                data = dataRow['short-msg']
        if not ( isinstance( data, list ) or    isinstance( data, tuple ) or    isinstance( data, dict ) ):

            if sys.version_info < (3,): # py3 support
                try:
                    data = data.decode('utf8')
                except UnicodeDecodeError as e:
                    pass
            
                try:
                    shortName = shortName.decode('utf8')
                except UnicodeDecodeError as e:
                    pass

        self.ShowHexaView.emit( data, dataType, shortName )

    def setExpectedEventId(self, testId):
        """
        Set the expected event id
        """
        self.expectedEventId = testId
        
    def getExpectedEventId(self):
        """
        Return the expected event id
        """
        return self.expectedEventId
        
    def addEvent (self, event, expected=False, ihmId=0):
        """
        Adds event

        #       {'task-id': '15', 'from': 'admin', 'test-id': '1', 'level': 'info', 'from-compon
        #ent': 'TESTSUITE', 'timestamp': '19:45:04.7822', 'short-msg': 'BEGIN', 'script_n
        #ame': 'Noname1', 'color': '#E7E6FF', 'script_id': '15_1_0', 'event': 'script'}

        @param event:
        @type event: 
        """
        event["ihm_id"] = ihmId
        
        # new in v11.2
        if 'tc_id' in event:
            if self.expectedEventId != event['tc_id']:  
                return
        else:
            if self.expectedEventId != event['script_id']:  
                return
        # end of new
        
        # new in v12.1, no more display events after the "END" testcase event
        if self.endEventDetected:
            return
            
        if "flag-end" in event:
            if event['flag-end']:
                self.endEventDetected = True
        # end of new
        
        if event['level'] in [ 'info', 'warning', 'error' ]:
            if event['short-msg'] in [ 'BEGIN', 'END' ]:
                h = 40; w = 100;
            else:
                h = 40; w = 300;
            msg = event['short-msg']
            if len(msg) > 50:
                msg = "%s..." % msg[:50]
            if 'color' in event:
                color = event['color']
            else:
                color = "#000000"
            self.parent.graphView.addStep(text=msg, color=color, 
                                          width=w, height=h, 
                                          data=event['short-msg'], 
                                          timestamp=event['timestamp'])

        if event['level'] in 'step-started':
            h = 40; w = 400;
            stepName, stepExpected = event['data-msg'][0]
            stepMsg = event['short-msg']
            if len(stepMsg) > 50:
                stepMsg = "%s..." % stepMsg[:50]
            blockItem = self.parent.graphView.addStep(text="%s: %s" % (stepName,stepMsg), 
                                                      color=event['color'], 
                                                      width=w, height=h, 
                                                      data=event['data-msg'], 
                                                      timestamp=event['timestamp'])
            self.steps[event['from-component']] = blockItem

        # update the graph
        if event['level'] in ['step-passed', 'step-failed' ]:
            if event['from-component'] in self.steps:
                blockItem = self.steps[event['from-component']]
                
                # new in v12
                if event['level'] == 'step-passed' and blockItem.status != False:
                    blockItem.status = True
                if event['level'] == 'step-failed':
                    blockItem.status = False

                if event['level'] == 'step-passed' and blockItem.status == False:
                    pass # don't change the color, keep the previous
                else:
                    blockItem.setColor(blockColor=event['color'])
                # end of new
                
                blockItem.setData(data=event['data-msg'])

        row_pos = self.textualViewer.insertItem( dataEvent=event)
        
        if event['event'] == 'script':
            self.eventId =  event['script_id']
        elif event['event'] == 'testcase':
            self.eventId =  event['tc_id']
        else:
            self.eventId = None
        return row_pos

    def reset (self):
        """
        Clear the textual log view
        Removes all events
        """
        self.endEventDetected = False
        self.eventId = None
        self.textualViewer.clear()
        self.steps = {}
        
        self.parent.graphView.reset()



