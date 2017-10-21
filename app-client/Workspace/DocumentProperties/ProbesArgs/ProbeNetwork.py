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
Probe network module
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
    from PyQt4.QtGui import (QTreeWidgetItem, QHBoxLayout, QLabel, QComboBox, QLineEdit,
                            QVBoxLayout, QTreeWidget, QPushButton)
except ImportError:
    from PyQt5.QtWidgets import (QTreeWidgetItem, QHBoxLayout, QLabel, QComboBox, 
                                QLineEdit, QVBoxLayout, QTreeWidget, QPushButton)
    
from Libs import QtHelper, Logger

class NetItem(QTreeWidgetItem):
    """
    Network item widget
    """
    def __init__(self, parent, data ):
        """
        Constructs KeyItem widget item

        @param parent:
        @type parent: 
        """
        QTreeWidgetItem.__init__(self, parent)
        self.dataNet = data
        self.setText( 0, data['interface'] )
        self.setText( 1, data['filter'] )


class NetworkArgs(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Network arguments dialog
    """
    def __init__(self, dataArgs, parent=None):
        """
        Dialog to fill arguments for the network probe

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(NetworkArgs, self).__init__(parent)
        self.dataArgs = dataArgs
        self.createDialog()
        self.createConnections()
        self.loadDefaultData()

    def createDialog (self):
        """
        Create qt dialog
        """
        mainLayout = QHBoxLayout()

        paramLayout = QHBoxLayout()
        paramLayout.addWidget( QLabel("Interface:") )
        self.intComboBox = QComboBox()
        self.intComboBox.setEditable(1)
        self.intComboBox.addItems( [ 'any', 'eth0', 'eth1', 'eth2', 'eth3', 'eth4', 'lo0' ] )
        paramLayout.addWidget( self.intComboBox )
        paramLayout.addWidget( QLabel("Filter:") )
        self.filterEdit = QLineEdit()
        paramLayout.addWidget( self.filterEdit )

        dataLayout = QVBoxLayout()
        self.labelHelp = QLabel("Network interface to dump:\nIf the interface name does not exist in the list\nplease to edit the combox list to change it.") 
        
        self.listBox = QTreeWidget(self)
        self.listBox.setIndentation(0)

        self.labels = [ self.tr("Interface"), self.tr("Filter") ]
        self.listBox.setHeaderLabels(self.labels)

        dataLayout.addWidget( self.labelHelp )
        dataLayout.addLayout( paramLayout )
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

        self.setWindowTitle("Network Probe > Arguments")
        

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

    def onItemSelected(self, itm, row):
        """
        Called when an item is selected
        """
        self.delButton.setEnabled(True)
        self.editButton.setEnabled(True)

    def editItem(self):
        """
        Edit item
        """
        self.delButton.setEnabled(False)
        self.editButton.setEnabled(False)
        # retrieve value to put it in the line edit and then remove item 
        model = self.listBox.model()
        for selectedItem in self.listBox.selectedItems():
            qIndex = self.listBox.indexFromItem(selectedItem)
            eth = selectedItem.dataNet['interface']
            flt = selectedItem.dataNet['filter']
            self.filterEdit.setText( flt )
            self.intComboBox.setEditText( eth )
            model.removeRow(qIndex.row())

    def delItem(self):
        """
        Delete item
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
        eth = self.intComboBox.currentText()
        if eth != '':
            flt = self.filterEdit.text()
            tpl = {'interface': str(eth), 'filter': str(flt) }
            newParam = NetItem( data=tpl, parent=self.listBox)
            self.listBox.resizeColumnToContents(0)

    def loadDefaultData(self):
        """
        Load the default data
        """
        try:
            if len(self.dataArgs) ==0:
                return
            datObj = eval(str(self.dataArgs))
            if 'interfaces' in datObj:
                for eth in datObj['interfaces']:
                    newParam = NetItem( data=eth, parent=self.listBox)
        except Exception as e:
            self.error( "unable to load the default data: %s" % e )

    def getArgs(self):
        """
        Returns arguments
        Example list of files: {'interfaces': [ {'interface':'any', 'filter':''} ] }
        """
        listEth = []
        # iterate all items in a QListWidget
        root = self.listBox.invisibleRootItem()
        child_count = root.childCount()
        for i in xrange(child_count):
            itm = root.child(i)
            listEth.append( eval(str(itm.dataNet)) )
        ret = {'interfaces': listEth } 
        if len(listEth) == 0:
            ret = ''
        return str(ret)
