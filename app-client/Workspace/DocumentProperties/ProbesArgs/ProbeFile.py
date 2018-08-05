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
Probe file module
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
    from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                            QListWidget, QPushButton)
except ImportError:
    from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                                QListWidget, QPushButton)
    
from Libs import QtHelper, Logger

class FileArgs(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    File arguments dialog
    """
    def __init__(self, dataArgs, parent=None):
        """
        Dialog to fill arguments for the file probe

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(FileArgs, self).__init__(parent)
        self.dataArgs = dataArgs
        self.createDialog()
        self.createConnections()
        self.loadDefaultData()

    def createDialog (self):
        """
        Create qt dialog
        """
        mainLayout = QHBoxLayout()

        dataLayout = QVBoxLayout()
        self.labelHelp = QLabel("Path of the file to retrieve:") 
        self.lineEdit = QLineEdit()
        self.listBox = QListWidget()
        dataLayout.addWidget( self.labelHelp )
        dataLayout.addWidget( self.lineEdit )
        dataLayout.addWidget( self.listBox )

        buttonLayout = QVBoxLayout()
        self.addButton = QPushButton("Add", self)
        self.delButton = QPushButton("Remove", self)
        self.delButton.setEnabled(False)
        self.editButton = QPushButton("Edit", self)
        self.editButton.setEnabled(False)
        self.clearButton = QPushButton("Clear", self)
        self.okButton = QPushButton("Ok", self)
        self.cancelButton = QPushButton("Cancel", self)
        buttonLayout.addWidget( self.addButton )
        buttonLayout.addWidget( self.delButton )
        buttonLayout.addWidget( self.editButton )
        buttonLayout.addWidget( self.clearButton )
        buttonLayout.addWidget( self.okButton )
        buttonLayout.addWidget( self.cancelButton )

        mainLayout.addLayout( dataLayout ) 
        mainLayout.addLayout( buttonLayout ) 

        self.setLayout(mainLayout)

        self.setWindowTitle("File Probe > Arguments")
        

    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.addButton.clicked.connect(self.addItem)
        self.delButton.clicked.connect(self.delItem)
        self.editButton.clicked.connect(self.editItem)
        self.clearButton.clicked.connect(self.clearList)
        self.listBox.itemClicked.connect(self.onItemSelected)

    def clearList(self):
        """
        Clear the list
        """
        self.listBox.clear()

    def onItemSelected(self, itm):
        """
        Called when an item is selected
        """
        self.delButton.setEnabled(True)
        self.editButton.setEnabled(True)

    def editItem(self):
        """
        Edit the selected item
        """
        self.delButton.setEnabled(False)
        self.editButton.setEnabled(False)
        # retrieve value to put it in the line edit and then remove item 
        model = self.listBox.model()
        for selectedItem in self.listBox.selectedItems():
            qIndex = self.listBox.indexFromItem(selectedItem)
            if sys.version_info > (3,):
                self.lineEdit.setText( model.data(qIndex) )
            else:
                self.lineEdit.setText( model.data(qIndex).toString() )
            model.removeRow(qIndex.row())

    def delItem(self):
        """
        Delete the selected item
        """
        self.delButton.setEnabled(False)
        self.editButton.setEnabled(False)
        # remove item
        model = self.listBox.model()
        for selectedItem in self.listBox.selectedItems():
            qIndex = self.listBox.indexFromItem(selectedItem)
            model.removeRow(qIndex.row())

    def addItem(self):
        """
        Add item
        """
        txt = self.lineEdit.text()
        if txt != '':
            self.listBox.insertItem (0, txt)
            self.lineEdit.setText('')

    def loadDefaultData(self):
        """
        Load the default data
        """
        try:
            if len(self.dataArgs) ==0:
                return
            dat = eval(self.dataArgs)
            if 'files' in dat:
                list_files = dat['files']
                self.listBox.insertItems(0, list_files)
        except Exception as e:
            self.error( e )

    def getArgs(self):
        """
        Returns arguments
        Examples: {'files': [ '/etc/init.d/ntpd', '/root/wmi-1.3.14-2.el5.art.x86_64.rpm' ] }
        """
        listFiles = []
        model = self.listBox.model()
        # iterate all items in a QListWidget
        for index in xrange(self.listBox.count()):
            itm = self.listBox.item(index)
            qIndex = self.listBox.indexFromItem(itm)
            if sys.version_info > (3,):
                listFiles.append( model.data(qIndex) )
            else:
                listFiles.append( str(model.data(qIndex).toString()) )
        ret = {'files': listFiles } 
        if len(listFiles) == 0:
            ret = ''
        return str(ret)