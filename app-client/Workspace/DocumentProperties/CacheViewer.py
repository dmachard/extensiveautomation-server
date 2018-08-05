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
Cache properties module
"""

import sys
import json
import re

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
                       
try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QWidget, QTabWidget, QIcon, QLabel, QFont, QVBoxLayout, 
                            QMessageBox, QDialog, QFileDialog, QTableView,
                            QSortFilterProxyModel, QLineEdit, QAbstractItemView)
    from PyQt4.QtCore import (pyqtSignal, QAbstractTableModel, QModelIndex,
                              QVariant, Qt, QRegExp)
except ImportError:
    from PyQt5.QtGui import (QIcon, QFont)
    from PyQt5.QtWidgets import (QWidget, QTabWidget, QLabel, QVBoxLayout, QMessageBox, 
                                QDialog, QFileDialog, QTableView, QLineEdit,
                                QAbstractItemView)
    from PyQt5.QtCore import (pyqtSignal, QAbstractTableModel, QSortFilterProxyModel,
                              QModelIndex ,QVariant, Qt, QRegExp)
    
from Libs import QtHelper, Logger

import Workspace.TestUnit as TestUnit
import Workspace.TestSuite as TestSuite
import Workspace.TestAbstract as TestAbstract
import Workspace.TestPlan as TestPlan

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
        
HEADERS             = ( 'Id', 'Type', '')

COL_ID              =   0
COL_NAME            =   2
COL_TYPE            =   1

class CacheTableModel(QAbstractTableModel, Logger.ClassLogger):
    """
    Table model
    """
    def __init__(self, parent):
        """
        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        self.mydata = []

    def getData(self):
        """
        """
        return self.mydata
        
    def columnCount(self, qindex=QModelIndex()):
        """
        """
        return len(HEADERS)
        
    def rowCount(self, qindex=QModelIndex()):
        """
        """
        return len( self.mydata )

    def setDataModel(self, data):
        """
        """
        self.mydata = data

        if sys.version_info > (3,):
            self.beginResetModel()
            self.endResetModel()
        else:
            self.reset()
            
    def getValue(self, index):
        """
        """
        if index.column() == COL_ID:
            return index.row() + 1
        elif index.column() == COL_NAME:
            return self.mydata[ index.row() ]['name']
        elif index.column() == COL_TYPE:
            return self.mydata[ index.row() ]['type']
        else:
            pass
            
    def data(self, index, role=Qt.DisplayRole):
        """
        """
        if not index.isValid():
            return q()
            
        value = self.getValue(index)
        
        if role == Qt.ToolTipRole:
            return q(self.mydata[ index.row() ]['value'])
            
        if role == Qt.DisplayRole:
            return q(value)
                
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[section]

        return None

    def flags(self, index):
        """
        """
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
    
class CacheTableView(QTableView, Logger.ClassLogger):
    """
    Cache table view
    """
    def __init__(self, parent):
        """
        @param parent: 
        @type parent:
        """
        QTableView.__init__(self, parent)
        self.createWidgets()
        
    def createWidgets(self):
        """
        """
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setDynamicSortFilter(True)

        self.model = CacheTableModel(self)

        self.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
    
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        
    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_ID, COL_TYPE]:
            self.resizeColumnToContents(col)
    
    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in xrange(len(data)):
            self.resizeRowToContents(row)
        
    def clear(self):
        """
        Clear the list
        """
        self.model.setDataModel( [] )
        
class CacheViewerQWidget(QWidget, Logger.ClassLogger):
    """
    Parameters widget
    """
    def __init__(self, parent):
        """
        Contructs Parameters Widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        
        self.currentDoc = None
        
        self.createWidgets()
        self.createConnections()
        
    def cache(self):
        """
        """
        return self.cacheTable.model.getData()
        
    def createWidgets(self):
        """
        """
        layout = QVBoxLayout()
        
        self.setMaximumHeight(350)
        
        title = QLabel("Cache preview")
        font = QFont()
        font.setBold(True)
        title.setFont(font)
        
        self.cacheTable = CacheTableView(self)
        
        self.filterText = QLineEdit(self)
        self.filterText.setToolTip(self.tr("Name filter"))
        self.filterText.setPlaceholderText("Search in cache")
        
        layout.addWidget( title )
        layout.addWidget(self.cacheTable)
        layout.addWidget(self.filterText)
        
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def createConnections(self):
        """
        Create qt connections
        """
        self.filterText.textChanged.connect(self.filterRegExpChanged)

    def filterRegExpChanged(self):
        """
        On filter regexp changed
        """
        syntax = QRegExp.RegExp
        caseSensitivity = Qt.CaseInsensitive
        regExp = QRegExp(self.filterText.text(),  caseSensitivity, syntax)

        self.cacheTable.proxyModel.setFilterKeyColumn( COL_NAME )
        self.cacheTable.proxyModel.setFilterRegExp(regExp)

        self.cacheTable.adjustColumns()
        self.cacheTable.adjustRows()
        
    def clear(self):
        """
        """
        self.currentDoc = None
        
        self.cacheTable.clear()
        self.filterText.setText("")
        
    def loadItems(self, wdoc):
        """
        """
        self.currentDoc  = wdoc
        
        self.cacheTable.clear()
        cache_preview = self.cacheTable.model.getData()
        
        # read inputs-parameters
        self.__read_params(params=wdoc.dataModel.properties['properties']["inputs-parameters"]["parameter"], cache_preview=cache_preview)

        # read outputs-parameters
        self.__read_params(params=wdoc.dataModel.properties['properties']["outputs-parameters"]["parameter"], cache_preview=cache_preview)

        self.cacheTable.model.setDataModel( cache_preview )
        
        self.cacheTable.adjustColumns()
        self.cacheTable.adjustRows()
        
    def updateCache(self, testId):
        """
        """
        if self.currentDoc is None: return
        if not isinstance(self.currentDoc, TestPlan.WTestPlan): return
        
        self.cacheTable.clear()
        cache_preview = self.cacheTable.model.getData()
        
        # main params
        self.__read_params(params=self.currentDoc.dataModel.properties['properties']["inputs-parameters"]["parameter"], cache_preview=cache_preview)
        self.__read_params(params=self.currentDoc.dataModel.properties['properties']["outputs-parameters"]["parameter"], cache_preview=cache_preview)
                           
        if testId != "0":
            for f in self.currentDoc.dataModel.getSorted():
                self.__read_params(params=f['properties']["inputs-parameters"]["parameter"], 
                                   cache_preview=cache_preview)
                self.__read_params(params=f['properties']["outputs-parameters"]["parameter"], 
                                   cache_preview=cache_preview)
                            
                if f["id"] == testId:
                    break
        
        self.cacheTable.model.setDataModel( cache_preview )
        
        self.cacheTable.adjustColumns()
        self.cacheTable.adjustRows()
        
    def __already_exists(self, cache, name):  
        """
        """
        already_exists = False
        for c in cache: 
            if c["name"] == name:
                already_exists = True
                break
        return already_exists
        
    def __read_params(self, params, cache_preview):
        """
        """
        for inp in params:
            # to support old test
            if "scope" not in inp: inp["scope"] == "local"
            
            if inp["type"] in [ "text", "custom" ]:
                captures = re.findall("\[!CAPTURE:[\w-]+(?:\:.*?)??\:\]", inp["value"])
                for c in captures:
                    k = c.split("[!CAPTURE:")[1].split(":", 1)[0]
                    tmp_param = {"name": k,  "value": "", "type": "str" }
                    if not self.__already_exists(cache=cache_preview, name=k):
                        cache_preview.append(tmp_param)
            if inp["scope"] == "cache":
                if inp["type"] == "json":
                    if not len(inp["value"]):
                        continue
                        
                    if not self.__already_exists(cache=cache_preview, name=inp["name"]):
                        cache_preview.append( {"name": inp["name"], 
                                               "value": inp["value"], 
                                               "type": inp["type"] } )

                    custom_json = re.sub(r"#.*", "", inp["value"])
                    custom_json = re.sub(r"\[!INPUT:[\w-]+(?:\:[\w-]+)*\:\]", "true", custom_json)
                    custom_json = re.sub(r"\[!CACHE:[\w-]+(?:\:[\w-]+)*\:\]", "true", custom_json)
            
                    parsed = json.loads(custom_json)
                    if isinstance(parsed, dict):
                        for k,v in parsed.items():
                            val_name = "%s_%s" % (inp["name"],k)
                            tmp_param = {"name": val_name, 
                                         "value": "%s" % v, 
                                         "type": "json" }
                            
                            if not self.__already_exists(cache=cache_preview, name=val_name):
                                cache_preview.append(tmp_param)
                else:
                    if not self.__already_exists(cache=cache_preview, name=inp["name"]):
                        cache_preview.append( {"name": inp["name"], 
                                               "value": inp["value"], 
                                               "type": inp["type"] } )
