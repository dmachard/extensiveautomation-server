#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2017 Denis Machard
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
# Gfi Informatique, Inc., hereby disclaims all copyright interest in the
# extensive testing project written by Denis Machard
# 
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

try:
    from PyQt4.QtGui import (QWidget, QApplication, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                QMessageBox, QFileDialog,QAbstractItemView, QTableView, QTabWidget, QLabel,
                                QProgressBar, QLineEdit, QGridLayout, QCheckBox )
    from PyQt4.QtCore import ( Qt, QObject, pyqtSignal, QAbstractTableModel, QModelIndex )         
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                                 QMessageBox, QFileDialog, QAbstractItemView, QTableView, QTabWidget, QLabel,
                                 QProgressBar, QLineEdit, QGridLayout, QCheckBox)
    from PyQt5.QtCore import ( Qt, QObject, pyqtSignal, QAbstractTableModel, QModelIndex )    

from Core.Libs import QtHelper, Logger

import xml.etree.ElementTree as ET

# verdict use on debug mode only       
VERDICT_EXAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<tests max="16" user="admin" project="Common" path="/Samples/Tests_Global/" name="0001_All_testplans" >
	<test id="1" name="004_Sequential" result="FAIL" max="0" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
	</test>
	<test id="2" name="01_Initial_test" result="FAIL" max="1" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
		<testcase id="1" name="TESTCASE" result="FAIL" max="1"  >
			<step id="1" name="Step 1" result="FAIL" actual="success" />
		</testcase>
	</test>
	<test id="3" name="01_Initial_Test" result="PASS" max="2" status="executed"  project="Common" path="/" original="Noname1" extension="tux" >
		<testcase id="1" name="TESTCASE_01" result="PASS" max="1"  >
			<step id="1" name="Step 1" result="PASS" actual="success" />
		</testcase>
		<testcase id="2" name="TESTCASE_02_test" result="PASS" max="1"  >
			<step id="1" name="Step 1" result="PASS" actual="success" />
		</testcase>
	</test>
	<test id="5" name="005_Conditionnal" result="UNDEFINED" max="0" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
	</test>
	<test id="6" name="01_Initial_test" result="FAIL" max="1" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
		<testcase id="1" name="TESTCASE" result="FAIL" max="1"  >
			<step id="1" name="Step 1" result="FAIL" actual="success" />
		</testcase>
	</test>
	<test id="7" name="01_Initial_Test" result="UNDEFINED" max="0" status="not-executed"  project="Common" path="/" original="Noname1" extension="tux">
	</test>
	<test id="8" name="01_Set Result" result="UNDEFINED" max="3" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
		<testcase id="1" name="PASS" result="PASS" max="1"  >
			<step id="1" name="Step 1" result="PASS" actual="pass" />
		</testcase>
		<testcase id="2" name="FAIL" result="FAIL" max="1"  >
			<step id="1" name="Step 1" result="FAIL" actual="fail" />
		</testcase>
		<testcase id="3" name="UNDEFINED" result="UNDEFINED" max="1"  >
			<step id="1" name="Step 1" result="UNDEFINED" actual="" />
		</testcase>
	</test>
	<test id="9" name="01_Initial_test" result="UNDEFINED" max="0" status="not-executed"  project="Common" path="/" original="Noname1" extension="tux">
	</test>
	<test id="11" name="006_SpecialCharacters" result="FAIL" max="0" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
	</test>
	<test id="12" name="AAAA" result="FAIL" max="1" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
		<testcase id="1" name="TESTCASE" result="FAIL" max="1"  >
			<step id="1" name="Step 1" result="FAIL" actual="success" />
		</testcase>
	</test>
	<test id="14" name="test_amp" result="PASS" max="0" status="executed"  project="Common" path="/Bugs/" original="test_amp2" extension="tux">
	</test>
	<test id="15" name="01_Wait" result="PASS" max="1" status="executed"  project="Common" path="/" original="Noname1" extension="tux">
		<testcase id="1" name="TESTCASE" result="PASS" max="1"  >
			<step id="1" name="Step 1" result="PASS" actual="action ok" />
		</testcase>
	</test>
	<test id="16" name="007_Sub_Parameters" result="UNDEFINED" max="0" status="disabled"  project="Common" path="/" original="Noname1" extension="tux">
	</test>
</tests>"""

QC_PASSED      = "Passed"
QC_FAILED      = "Failed"
QC_UNCOMPLETED = "Not Completed"

STEPS_COL_ID      =   0
STEPS_COL_RESULT  =   1
STEPS_COL_ACTUAL  =   2
STEPS_HEADERS             = ( 'Id', 'Result', 'Actual' )
 
class StepsTableModel(QAbstractTableModel):
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
        self.nbCol = len(STEPS_HEADERS)

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
        if index.column() == STEPS_COL_ID:
            return index.row() + 1
        elif index.column() == STEPS_COL_ACTUAL:
            return self.mydata[ index.row() ]['actual']
        elif index.column() == STEPS_COL_RESULT:
            return self.mydata[ index.row() ]['result']
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
            return value
        elif role == Qt.EditRole:
            return value
            
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
            return STEPS_HEADERS[section]

        return None

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        if index.column() == STEPS_COL_ACTUAL:
            self.mydata[ index.row() ]['actual'] = value
        elif index.column() == STEPS_COL_RESULT:
            self.mydata[ index.row() ]['result'] = value

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
        if index.column() == STEPS_COL_ID:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
     
class StepsTableView(QTableView):
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
        pass
        
    def createWidgets(self):
        """
        """
        self.model = StepsTableModel(self, core=self.core())
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)

    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [STEPS_COL_ID, STEPS_COL_ACTUAL, STEPS_COL_RESULT  ]:
            self.resizeColumnToContents(col)

    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in range(len(data)):
            self.resizeRowToContents(row)

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

TESTCASES_COL_ID      =   0
TESTCASES_COL_RESULT  =   1
TESTCASES_COL_NAME    =   2

TESTCASES_HEADERS             = ( 'Id', 'Result', 'Name' )
 
class TestcasesTableModel(QAbstractTableModel):
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
        self.nbCol = len(TESTCASES_HEADERS)

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
        if index.column() == TESTCASES_COL_ID:
            return index.row() + 1
        elif index.column() == TESTCASES_COL_NAME:
            return self.mydata[ index.row() ]['name']
        elif index.column() == TESTCASES_COL_RESULT:
            return self.mydata[ index.row() ]['result']
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
            return value
        elif role == Qt.EditRole:
            return value
            
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
            return TESTCASES_HEADERS[section]

        return None

    def setValue(self, index, value):
        """
        Set value

        @param index: 
        @type index:

        @param value: 
        @type value:
        """
        if index.column() == TESTCASES_COL_NAME:
            self.mydata[ index.row() ]['name'] = value
        elif index.column() == TESTCASES_COL_RESULT:
            self.mydata[ index.row() ]['result'] = value

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
        if index.column() == TESTCASES_COL_ID:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
     
class TestcasesTableView(QTableView):
    LoadSteps = pyqtSignal(list) 
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
        
    def createWidgets(self):
        """
        """
        self.model = TestcasesTableModel(self, core=self.core())
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)

    def onAbstractItemClicked(self):
        """
        """
        sourceIndex = self.selectedIndexes()
        if not sourceIndex:
            return
        
        selectedIndex = sourceIndex[0].row()
        row = self.model.getData()[selectedIndex]
        
        self.LoadSteps.emit(row['steps'])
    
    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [TESTCASES_COL_ID, TESTCASES_COL_NAME, TESTCASES_COL_RESULT  ]:
            self.resizeColumnToContents(col)

    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in range(len(data)):
            self.resizeRowToContents(row)

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

        
COL_ID      =   0
COL_RESULT  =   1
COL_NAME    =   2

HEADERS             = ( 'Id', 'Result', 'Name' )
 
class TestsTableModel(QAbstractTableModel):
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
        if index.column() == COL_ID:
            return index.row() + 1
        elif index.column() == COL_NAME:
            return self.mydata[ index.row() ]['name']
        elif index.column() == COL_RESULT:
            return self.mydata[ index.row() ]['result']
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
            return value
        elif role == Qt.EditRole:
            return value
            
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
        if index.column() == COL_NAME:
            self.mydata[ index.row() ]['name'] = value
        elif index.column() == COL_RESULT:
            self.mydata[ index.row() ]['result'] = value

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
        if index.column() == COL_ID:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)
     
class TestsTableView(QTableView):
    LoadTestcases = pyqtSignal(list) 
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
        
    def createWidgets(self):
        """
        """
        self.model = TestsTableModel(self, core=self.core())
        self.setModel(self.model)
        
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)

    def onAbstractItemClicked(self):
        """
        """
        sourceIndex = self.selectedIndexes()
        if not sourceIndex:
            return
        
        selectedIndex = sourceIndex[0].row()
        row = self.model.getData()[selectedIndex]

        self.LoadTestcases.emit(row['testcases'])
    
    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_ID, COL_NAME, COL_RESULT  ]:
            self.resizeColumnToContents(col)

    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in range(len(data)):
            self.resizeRowToContents(row)

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

class VerdictPage(QWidget):
    """
    Verdict Export Page
    """
    ExportResults = pyqtSignal(list, dict) 
    def __init__(self, parent, core, debugMode=False):
        """
        Constructor
        @param parent:
        """
        QWidget.__init__(self, parent)
        self.__core = core
        self.__debugMode = debugMode
        self.__rawXml = ""
        
        self.createWidgets()
        self.creationConnections()
        
        if self.__debugMode:  self.onCheckboxesChanged(toggled=False)

    def core(self):
        """
        """
        return self.__core
        
    def creationConnections (self):
        """
        QtSignals connection:
        """
        self.testsTable.LoadTestcases.connect( self.onLoadTestcases )
        self.testcasesTable.LoadSteps.connect( self.onLoadSteps )
        self.ignoreTestcases.toggled.connect(self.onCheckboxesChanged)
        self.ignoreUncomplete.toggled.connect(self.onCheckboxesChanged)
        self.exportButton.clicked.connect( self.onExportClicked )
        
    def createWidgets(self):
        """
        """
        self.listingTab = QTabWidget()
        self.listingTab.setMinimumWidth(650)
        
        layoutGrid = QGridLayout()
        
        self.testSetPath = QLineEdit()
        self.testSetName = QLineEdit()
        
        self.testsTable = TestsTableView(self, core=self.core())
        self.testcasesTable = TestcasesTableView(self, core=self.core())
        
        self.stepsTable = StepsTableView(self, core=self.core())

        self.listingTab.addTab( self.testsTable, "Test(s)")
        self.listingTab.addTab( self.testcasesTable, "Testcase(s)")
        self.listingTab.addTab( self.stepsTable, "Steps(s)")
        
        self.ignoreTestcases = QCheckBox("Ignore testcase(s)")
        if self.core().settings().cfg()["export-results"]["ignore-testcase"]:
            self.ignoreTestcases.setCheckState(Qt.Checked) 
        
        self.ignoreUncomplete = QCheckBox("Ignore uncomplete result(s)")
        if self.core().settings().cfg()["export-results"]["ignore-uncomplete"]:
            self.ignoreUncomplete.setCheckState(Qt.Checked) 
            
        self.addMissingFoldersCheckBox = QCheckBox(self.tr("Create missing folders"))
        if self.core().settings().cfg()["export-results"]["add-folders"]:
            self.addMissingFoldersCheckBox.setCheckState(Qt.Checked) 
            
        self.addTestsetCheckBox = QCheckBox(self.tr("Create testset"))
        if self.core().settings().cfg()["export-results"]["add-testset"]:
            self.addTestsetCheckBox.setCheckState(Qt.Checked) 
            
        self.addTestinstanceCheckBox = QCheckBox(self.tr("Add test instance in testset"))
        if self.core().settings().cfg()["export-results"]["add-testinstance"]:
            self.addTestinstanceCheckBox.setCheckState(Qt.Checked) 
            
        optionsLayout = QHBoxLayout()
        optionsLayout.addWidget(self.ignoreTestcases)
        optionsLayout.addWidget(self.ignoreUncomplete)
        optionsLayout.addStretch(1)
            
        optionsTsLayout = QHBoxLayout()
        optionsTsLayout.addWidget(self.addTestsetCheckBox)
        optionsTsLayout.addWidget(self.addTestinstanceCheckBox)
        optionsTsLayout.addStretch(1)
        
        layoutGrid.addWidget(QLabel("Remote Test Set Path:"), 0, 0)
        layoutGrid.addWidget(self.testSetPath, 0, 1)
        layoutGrid.addWidget(self.addMissingFoldersCheckBox, 1, 1)
        layoutGrid.addWidget(QLabel("Remote Test Set Name:"), 2, 0)
        layoutGrid.addWidget(self.testSetName, 2, 1)
        layoutGrid.addLayout(optionsTsLayout, 3, 1)
        layoutGrid.addWidget(QLabel("Local result(s):"), 4, 0)
        layoutGrid.addLayout(optionsLayout, 4, 1)
        layoutGrid.addWidget(QLabel("Test(s) Verdict:"), 5, 0)
        layoutGrid.addWidget(self.listingTab, 5, 1)

        self.exportStatusLabel = QLabel( "Status: Disconnected", self)
        self.exportButton = QPushButton(self.tr("Export Result"), self)
        self.exportButton.setMinimumWidth(300)
        
        layoutRight = QHBoxLayout()
        layoutRight.addWidget(self.exportButton)
        layoutRight.addWidget(self.exportStatusLabel)
        layoutRight.addStretch(1)
        
        layoutGrid.addWidget(QLabel("Controls:"), 6, 0)
        layoutGrid.addLayout(layoutRight, 6, 1)
        
        layoutMain = QHBoxLayout()
        layoutMain.addLayout(layoutGrid)

        self.setLayout(layoutMain)
        
    def onExportClicked(self):
        """
        """
        testsetPath = self.testSetPath.text()
        if not len(testsetPath):
            QMessageBox.warning(self, self.tr("Export Result") , 
                                self.tr("Please to specific the remote testset path!") )
            return
        testsetName = self.testSetName.text()
        if not len(testsetName):
            QMessageBox.warning(self, self.tr("Export Result") , 
                                self.tr("Please to specific the remote testset name!") )
            return
        
        testcases = []
        if self.ignoreTestcases.isChecked():
            indexes = self.testsTable.selectionModel().selectedRows()
            if not len(indexes):
                QMessageBox.warning(self, self.tr("Export Result") , 
                                    self.tr("Please to select one test!") )
                return
        
            error = False
            for index in indexes:
                selectedIndex = index.row()
                row = self.testsTable.model.getData()[selectedIndex]
                testcases.append(row)

        else:
            indexes = self.testcasesTable.selectionModel().selectedRows()
            if not len(indexes):
                QMessageBox.warning(self, self.tr("Export Result") , 
                                    self.tr("Please to select one testcase!") )
                return
        
            error = False
            for index in indexes:
                selectedIndex = index.row()
                row = self.testcasesTable.model.getData()[selectedIndex]
                testcases.append(row)

        config = { 
                    "TestSet_Path": testsetPath, 
                    "TestSet_Name": testsetName, 
                    "Add_Folders": self.addMissingFoldersCheckBox.isChecked(),
                    "Add_TestSet": self.addTestsetCheckBox.isChecked(),
                    "Add_TestInstance": self.addTestinstanceCheckBox.isChecked()
                 }
        for cfg in self.core().settings().cfg()["custom-testset-fields"]:
            config.update( {cfg["key"]: cfg["value"] } )
            
        self.disableExport()
        self.ExportResults.emit(testcases, config)
        
    def logStatus(self, status):
        """
        """
        self.exportStatusLabel.setText(status)
        
    def enableExport(self):
        """
        """
        self.exportButton.setEnabled(True)
        
    def disableExport(self):
        """
        """
        self.exportButton.setEnabled(False)
           
    def onCheckboxesChanged(self, toggled):
        """
        """
        if self.ignoreUncomplete.isChecked() or self.ignoreTestcases.isChecked():
            self.testcasesTable.setEnabled(False)
            self.testcasesTable.clear()
            self.stepsTable.setEnabled(False)
            self.stepsTable.clear()
            
        if not self.ignoreTestcases.isChecked():
            self.testcasesTable.setEnabled(True)
            self.stepsTable.setEnabled(True)

        # reload data
        if self.__debugMode: 
            self.readXml(rawXml=VERDICT_EXAMPLE)
        else:
            self.readXml(rawXml=self.__rawXml)
        
    def clearTables(self):
        """
        Clear all tables
        """
        self.stepsTable.clear()
        self.testcasesTable.clear()
        self.testsTable.clear()
        
    def onLoadSteps(self, steps):
        """
        """
        self.stepsTable.loadTable(data=steps)

    def onLoadTestcases(self, testcases):
        """
        """
        if self.ignoreTestcases.isChecked():
            return
            
        self.stepsTable.clear()
        self.testcasesTable.loadTable(data=testcases)
        
    def onLoadTests(self, data):
        """
        """
        # clear the table before to start
        self.clearTables()
        
        # load tables according to the data provided
        self.testsTable.loadTable(data=data)

    def convertResult(self, result):
        """
        """
        if result == "PASS":
            return QC_PASSED
        elif result == "FAIL":
            return QC_FAILED
        else:
            return QC_UNCOMPLETED
        
    def readXml(self, rawXml):
        """
        """
        # init and save the xml provided
        self.__rawXml = rawXml
        try:
            root = ET.fromstring(rawXml)
        except Exception as e:
            self.core().debug().addLogError("Unable to read xml: %s"  % e )
        else:
            tests = []
            testsVerdict = root.find(".")
            
            testPath = testsVerdict.attrib["path"]
            testProject = testsVerdict.attrib["project"]
            testName = testsVerdict.attrib["name"]
            self.testSetPath.setText(testPath)
            self.testSetName.setText(testName)
            
            # read all tests
            testsName = {}
            for ts in testsVerdict:
                if ts.attrib["status"] in  [ "not-executed", "disabled" ]:
                    continue
                    
                tcs = ts.findall("testcase")
                if len(tcs) and self.ignoreTestcases.isChecked():
                    continue
                    
                tsName = ts.attrib["name"]
                tsName = tsName.strip()
                
                if tsName not in testsName: 
                    testsName[tsName] = 1
                else:
                    testsName[tsName] += 1
                ts_result = self.convertResult(ts.attrib["result"]) 
                if self.ignoreUncomplete.isChecked():
                    if ts_result == QC_UNCOMPLETED:
                        continue
                    
                testname_instance = "[%s]%s" % (testsName[tsName], tsName)
                if self.core().settings().cfg()["qc-server"]["use-rest"]:
                    testname_instance = "%s [%s]" % (tsName, testsName[tsName])
                test = { 
                        "name": testname_instance, 
                        "result": ts_result,
                        "testpath": ts.attrib["path"],
                        "testname": tsName
                       }
                # read all testcases
                testcases = []
                tcsName = {}
                for tc in tcs:
                    tcName = tc.attrib["name"]
                    
                    # read all steps
                    stepsVerdict = tc.findall("step")
                    steps = []
                    for stp in stepsVerdict:
                        steps.append( {"result": self.convertResult(stp.attrib["result"]), 
                                        "actual": stp.attrib["actual"] } )
                        
                    if tcName not in tcsName: 
                        tcsName[tcName] = 1
                    else:
                        tcsName[tcName] += 1
                    tc_result = self.convertResult(tc.attrib["result"])
                    testcases.append( {"name": "[%s]%s" % (tcsName[tcName], tcName), 
                                        "result": tc_result, 
                                        "steps": steps})
                
                test.update({"testcases": testcases})
                tests.append(test)
            self.core().debug().addLogSuccess("Export results detected: %s"  % len(tests) )
            if len(tests): self.onLoadTests(data=tests)
         