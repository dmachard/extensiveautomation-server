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
Mobile widget
"""

import sys

try:
	from PyQt4.QtGui import (QWidget, QLabel, QCheckBox, QVBoxLayout, QTreeView, QAbstractItemView, 
							QHBoxLayout, QIcon, QMenu, QCursor, QApplication, QPainter, QPen,
							QPixmap, QListWidget, QToolBar, QTableView, QDesktopWidget)
	from PyQt4.QtCore import (Qt, QFile, QIODevice, QModelIndex, QAbstractTableModel, pyqtSignal, 
							QSize, QEvent, QPoint, QAbstractItemModel)
	from PyQt4.QtXml import (QDomDocument)
except ImportError:
	from PyQt5.QtCore import (Qt, QFile, QIODevice, QModelIndex, QAbstractTableModel, pyqtSignal, 
							QSize, QEvent, QPoint, QAbstractItemModel)
	from PyQt5.QtXml import (QDomDocument)
	from PyQt5.QtWidgets import (QLabel, QCheckBox, QTreeView, QAbstractItemView, 
							QMenu, QWidget, QHBoxLayout, QVBoxLayout,
							QListWidget, QToolBar, QTableView, QDesktopWidget)
	from PyQt5.QtGui import (QIcon, QCursor, QPainter, QPen, QPixmap)
	
from Libs import Logger, Settings, QtHelper

class DomItem(object):
    """
    Dom item object
    """
    def __init__(self, node, row, parent=None):
        """
        Constructor
        """
        self.domNode = node
        # Record the item's location within its parent.
        self.rowNumber = row
        self.parentItem = parent
        self.childItems = {}

    def node(self):
        """
        return a node
        """
        return self.domNode

    def parent(self):
        """
        return the parent
        """
        return self.parentItem

    def child(self, i):
        """
        get child of the item
        """
        if i in self.childItems:
            return self.childItems[i]

        if i >= 0 and i < self.domNode.childNodes().count():
            childNode = self.domNode.childNodes().item(i)
            childItem = DomItem(childNode, i, self)
            self.childItems[i] = childItem
            return childItem

        return None

    def row(self):
        """
        return the row number
        """
        return self.rowNumber

class DomModel(QAbstractItemModel):
    """
    Dom model
    """
    def __init__(self, document, parent=None):
        """
        Constructor
        """
        super(DomModel, self).__init__(parent)

        self.domDocument = document

        self.rootItem = DomItem(self.domDocument, 0)

    def columnCount(self, parent):
        """
        return the number of column
        """
        return 1

    def data(self, index, role):
        """
        Data
        """
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        node = item.node()
        # attributes = []
        attributeMap = node.attributes()

        if index.column() == 0:
            nodeName = node.nodeName()
            completedName = False
            for i in range(0, attributeMap.count()):
                attribute = attributeMap.item(i)
                if attribute.nodeName() == "text" and len(attribute.nodeValue()):
                    nodeName = attribute.nodeValue()
                    completedName = True
                    break
            if not completedName:
                for i in range(0, attributeMap.count()):
                    attribute = attributeMap.item(i)
                    if attribute.nodeName() == "class" and len(attribute.nodeValue()):
                        nodeName = attribute.nodeValue()
                        break
            return nodeName


        return None

    def flags(self, index):
        """
        Flags
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        """
        Header
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Name"

        return None

    def index(self, row, column, parent):
        """
        Index
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, child):
        """
        Get parent of the child
        """
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.parent()

        if not parentItem or parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        """
        Return the number of row
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.node().childNodes().count()

class MyTableModel(QAbstractTableModel):
    """
    Table model
    """
    def __init__(self, parent, mylist, header, *args):
        """
        Constructor
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        
    def rowCount(self, parent):
        """
        Return the number of row
        """
        return len(self.mylist)
        
    def columnCount(self, parent):
        """
        Return the number of column
        """
        return len(self.header)
        
    def data(self, index, role):
        """
        Return data
        """
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]
        
    def headerData(self, col, orientation, role):
        """
        Return header
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

class MobileWidget(QWidget): 
    """
    Mobile widget
    """
    RefreshScreen = pyqtSignal()  
    RefreshAutomatic = pyqtSignal(bool)  
    TapOn = pyqtSignal(int, int)  
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(MobileWidget, self).__init__(parent)

        self.origWidth=0
        self.origHeight=0
        self.imagePath = None
        
        self.createActions()
        self.createWidget()
        self.createToolbar()
        self.center()
        
    def createActions(self):
        """
        Create qt actions
        """
        self.refreshAction = QtHelper.createAction(self, self.tr("&Refresh"), self.refreshScreen, icon = None )
        self.refreshAction.setEnabled(False)
        
        self.copyAction = QtHelper.createAction(self, self.tr("&Copy"), self.copyItem, icon = None )
        
    def createWidget(self):
        """
        Create qt widget
        """
        
        self.screenResolutionLabel = QLabel(self)
        self.screenTapLabel = QLabel(self)
        
        
        mobileLayout = QVBoxLayout()
        
        self.mobileDockToolbar = QToolBar(self)
        self.mobileDockToolbar.setStyleSheet("QToolBar { border: 0px }");
        self.mobileDockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.mobileImageLabel = QLabel(self)
        self.mobileImageLabel.setMouseTracking(True)
        self.mobileImageLabel.installEventFilter(self)
        self.mobileImageLabel.setScaledContents(True)
        self.mobileImageLabel.mousePressEvent = self.pixelSelect

        self.refreshCheckbox = QCheckBox("Automatic Refresh", self)
        self.refreshCheckbox.setEnabled(False)
        self.refreshCheckbox.stateChanged.connect(self.onRefreshChanged)
        
        self.clickCheckbox = QCheckBox("Enable Tap", self)
        self.clickCheckbox.setEnabled(False)

        self.model = DomModel(QDomDocument(), self)
        self.mobileTreeView = QTreeView(self)
        self.mobileTreeView.setMinimumWidth(300)
        self.mobileTreeView.setModel(self.model)
        self.mobileTreeView.clicked.connect(self.onTreeViewClicked)
        
        
        header=["Attribute", "Value"]
        self.tableModel = MyTableModel(self, [], header)
        self.mobileTableView = QTableView(self)
        self.mobileTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mobileTableView.setModel(self.tableModel)
        self.mobileTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mobileTableView.customContextMenuRequested.connect( self.onContextMenuEvent )
        self.mobileTableView.setMinimumWidth(300)

        mobileViewLayout = QHBoxLayout()
        mobileViewLayout.addWidget(self.mobileImageLabel)
        mobileViewLayout.addWidget(self.mobileTreeView)
        mobileViewLayout.addWidget(self.mobileTableView)

        mobileLayout.addWidget(self.mobileDockToolbar)
        mobileLayout.addLayout(mobileViewLayout)

        
        self.setLayout(mobileLayout)

    def createToolbar(self):
        """
        Create qt toolbar
        """
        self.mobileDockToolbar.setObjectName("Toolbar")
        self.mobileDockToolbar.addWidget(self.refreshCheckbox)
        self.mobileDockToolbar.addWidget(self.clickCheckbox)
        self.mobileDockToolbar.addSeparator()
        self.mobileDockToolbar.addAction(self.refreshAction)
        self.mobileDockToolbar.addSeparator()
        self.mobileDockToolbar.addWidget(self.screenResolutionLabel)
        self.mobileDockToolbar.addSeparator()
        self.mobileDockToolbar.addWidget(self.screenTapLabel)
        self.mobileDockToolbar.addSeparator()
        self.mobileDockToolbar.setIconSize(QSize(16, 16))
    
    def center(self):
        """
        Center the dialog
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def eventFilter(self, srcEvent, event):   
        """
        On event filtering
        """
        if srcEvent==self.mobileImageLabel:
            
            if event.type() == QEvent.MouseMove: 
                    x=event.pos().x() 
                    y=event.pos().y()
                    
                    pixmap = self.mobileImageLabel.pixmap()
                    if pixmap is not None:
                        x_scaled = int( ( self.origWidth * x ) / pixmap.width() )
                        y_scaled = int( ( self.origHeight * y ) / pixmap.height() )
                        self.mobileImageLabel.setToolTip("%sx%s" % (x_scaled,y_scaled) )

        return False
        
    def onContextMenuEvent(self, event):
        """
        On context menu event
        """
        menu = QMenu(self)
        menu.addAction(self.copyAction)
        menu.popup(QCursor.pos())

    def copyItem(self):
        """
        Copy the item
        """
        indexes = self.mobileTableView.selectedIndexes()
        if len(indexes):
            data = self.tableModel.mylist[indexes[0].row()][indexes[0].column()]
            
            clipboard = QApplication.clipboard() 
            clipboard.setText(data) 
            
    def onTreeViewClicked(self, qindex):
        """
        On click in the treeview
        """
        item = qindex.internalPointer()
        attributes = []
        node = item.node()
        attributeMap = node.attributes()
        nodeName = node.nodeName()

        bounds_str = None
        for i in range(0, attributeMap.count()):
            attribute = attributeMap.item(i)
            attributes.append( (attribute.nodeName(),attribute.nodeValue()) )
            
            if attribute.nodeName() == 'bounds':
                bounds_str = attribute.nodeValue()
 
        self.tableModel.mylist = attributes

        if sys.version_info > (3,):
            self.tableModel.beginResetModel()
            self.tableModel.endResetModel()
        else:
            self.tableModel.reset()
            
        self.mobileTableView.resizeColumnsToContents ()
        self.mobileTableView.resizeRowsToContents()
        
        # redraw image with rectangle
        if bounds_str is not None:
            xy = bounds_str.split('][')[0].split('[')[1]
            wh = bounds_str.split('][')[1].split(']')[0]
            x, y = xy.split(',')
            w, h = wh.split(',')
            
            # get label size
            pixmap = self.mobileImageLabel.pixmap()
            xlabel = pixmap.width()
            ylabel = pixmap.height()
            
            # resize the rectangle
            y_scaled = (pixmap.height()* int(y)) / self.origHeight
            x_scaled = (pixmap.width()*int(x)) / self.origWidth
            
            h_scaled = (pixmap.height()* (int(h)-int(y)) ) / self.origHeight
            w_scaled = (pixmap.width()*(int(w)-int(x)) ) / self.origWidth
            
            # finally reload
            self.reloadScreen(x=int(x_scaled), y=int(y_scaled), w=int(w_scaled), h=int(h_scaled))
        
    def onDeviceReady(self):
        """
        On device ready
        """
        self.refreshAction.setEnabled(True)
        self.refreshCheckbox.setEnabled(True)
        self.clickCheckbox.setEnabled(True)
    
    def refreshScreen(self):
        """
        Refresh the screen
        """
        self.RefreshScreen.emit()

    def onRefreshChanged(self, state):
        """
        On refresh changed
        """
        if state == Qt.Checked:
            self.RefreshAutomatic.emit(True)
        else:
            self.RefreshAutomatic.emit(False)

                        
    def pixelSelect( self, event ):
        """
        Select pixel to click
        """
        position = QPoint( event.pos().x(),  event.pos().y())
        
        x = event.pos().x()
        y = event.pos().y()
        
        pixmap = self.mobileImageLabel.pixmap()
    
        x_scaled = int( ( self.origWidth * x ) / pixmap.width() )
        y_scaled = int( ( self.origHeight * y ) / pixmap.height() )
        
        self.screenTapLabel.setText("Tap on (%s,%s)" % (x_scaled, y_scaled) )
        
        if self.clickCheckbox.isChecked():
            self.TapOn.emit(x_scaled, y_scaled)
        
    def drawRectangle(self, x=0, y=0, w=0, h=0):
        """
        Draw a rectangle
        """
        self.mobileImageLabel.update()
        pixmap = self.mobileImageLabel.pixmap()
        if pixmap is not None:

            p = QPainter(pixmap)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            p.setPen(pen)
            p.drawRect(x,y,w,h)
            p.end()  

    def reloadScreen(self, x, y, w, h):
        """
        Reload the screen
        """
        if self.imagePath is not None:
            self.updateScreen(filename=self.imagePath, xmlPath='', x=x,y=y,w=w,h=h, reloadMode=True)
            
    def updateScreen(self, filename, xmlPath, x=0,y=0,w=0,h=0, reloadMode=False):
        """
        Update the screen
        """
        self.imagePath = filename
        
        if not reloadMode:
            self.tableModel.mylist = []
            self.tableModel.beginResetModel()
            self.tableModel.endResetModel()
            
        pixmap = QPixmap(filename)
        if pixmap is not None:
            self.origWidth=pixmap.width()
            self.origHeight=pixmap.height()
            
            self.screenResolutionLabel.setText("Resolution=%sx%s" % (self.origWidth,self.origHeight) )

            #portrait
            if self.origWidth < self.origHeight:
                pixmap = pixmap.scaledToHeight( Settings.getInt('MobileAndroid', 'resolution-screen-height') , 
                                                mode=Qt.SmoothTransformation)
                self.mobileImageLabel.setPixmap(pixmap)
            else:
                pixmap = pixmap.scaledToWidth( Settings.getInt('MobileAndroid', 'resolution-screen-width') , 
                                                mode=Qt.SmoothTransformation)
                self.mobileImageLabel.setPixmap(pixmap)
            
            self.drawRectangle(x=x, y=y, w=w, h=h)
            
        self.resize(pixmap.width(), pixmap.height())
        
        # convert xml to dict
        if len(xmlPath):
            f = QFile(xmlPath)
            if f.open(QIODevice.ReadOnly):
                document = QDomDocument()
                if document.setContent(f):
                    newModel = DomModel(document, self)
                    self.mobileTreeView.setModel(newModel)
                    self.mobileTreeView.expandAll()
                    self.mobileTreeView.resizeColumnToContents(0)
                f.close()    
