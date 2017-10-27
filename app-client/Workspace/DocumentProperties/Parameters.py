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
Test parameters inputs/outputs module
"""

import sys
import os

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QFont, QIcon, QPixmap, QImage, QColor, QItemDelegate, QLineEdit,
                            QComboBox, QDoubleValidator, QIntValidator, QDialog, QDateEdit, QPlainTextEdit,
                            QTimeEdit, QDateTimeEdit, QAbstractItemDelegate, QLabel, QHBoxLayout, 
                            QTextEdit, QDialogButtonBox, QVBoxLayout, QMessageBox, QListView, 
                            QSortFilterProxyModel, QListWidgetItem, QPushButton, QListWidget, 
                            QGridLayout, QTableView, QDrag, QAbstractItemView, QFrame, QApplication, 
                            QMenu, QFileDialog, QWidget, QToolBar, QClipboard, QRegExpValidator,
                            QSyntaxHighlighter, QTextCharFormat, QBrush, QPalette, QCheckBox,
                            QCompleter)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, QDate, QTime, QDateTime, 
                            QAbstractListModel, QRegExp, pyqtSignal, QMimeData, QByteArray, QBuffer, 
                            QIODevice, QFile, QSize)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon, QPixmap, QImage, QColor, QDoubleValidator, 
                            QIntValidator, QDrag, QClipboard, QRegExpValidator,
                            QSyntaxHighlighter, QTextCharFormat, QBrush, QPalette)
    from PyQt5.QtWidgets import (QItemDelegate, QLineEdit, QComboBox, QDialog, QDateEdit, QPlainTextEdit,
                                QTimeEdit, QDateTimeEdit, QAbstractItemDelegate, QLabel, QHBoxLayout, 
                                QTextEdit, QDialogButtonBox, QVBoxLayout, QMessageBox, QListView, 
                                QListWidgetItem, QPushButton, QListWidget, QCheckBox,
                                QGridLayout, QTableView, QAbstractItemView, QFrame, QApplication, 
                                QMenu, QFileDialog, QWidget, QToolBar, QCompleter)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, QDate, QTime, QDateTime, 
                            QAbstractListModel, QRegExp, pyqtSignal, QMimeData, QByteArray, QBuffer, 
                            QIODevice, QFile, QSize, QSortFilterProxyModel)
                            
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
import UserClientInterface as UCI
import Workspace
import Recorder

import operator
import pickle
import base64

COL_ID              =   0
COL_NAME            =   1
COL_TYPE            =   2
COL_VALUE           =   3
COL_DESCRIPTION     =   4

HEADERS             = ( 'Id', 'Name', 'Type', 'Value', 'Description' )
TYPES_PARAM         = [ 
                        'str', 'text', 'custom', 'pwd', 'list', 'bool', 'hex', 'json', '' ,
                        'none', 'alias', 'shared', 'list-shared', 'cache', '',
                        'int', 'float', '',
                        'dataset', 'remote-image', 'local-image', 'snapshot-image', '',
                        'local-file', '',
                        'date', 'time', 'date-time', '', 
                        'self-ip', 'self-mac', 'self-eth'
                       ]
                       
try:
    xrange
except NameError: # support python3
    xrange = range
    
class ParametersTableModel(QAbstractTableModel, Logger.ClassLogger):
    """
    Table model for parameters
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
        self.mydata = []

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
        elif index.column() == COL_TYPE:
            return self.mydata[ index.row() ]['type']
        elif index.column() == COL_VALUE:
            return self.mydata[ index.row() ]['value']
        elif index.column() == COL_DESCRIPTION:
            return self.mydata[ index.row() ]['description']
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
            return q()
        value = self.getValue(index)
        
        # tooltip display
        if role == Qt.ToolTipRole:
            if self.mydata[ index.row() ]['type'] in [ 'local-image', 'snapshot-image' ]:
                if index.column() == COL_VALUE:
                    return q()
                    
            if self.mydata[ index.row() ]['type'] in [ 'local-file' ]:
                if index.column() == COL_VALUE:
                    return q()
                    
            if self.mydata[ index.row() ]['type'] in [ 'list' ]:
                if index.column() == COL_VALUE:
                    try:
                        els = value.split(",")
                        ret = []
                        for e in els:
                            ret.append( e )
                        return q( "\r\n".join(ret) )    
                    except Exception as e:
                        return q("")
                        
            if self.mydata[ index.row() ]['type'] in [ 'list-shared' ]:
                if index.column() == COL_VALUE:
                    try:
                        els = value.split(",")
                        ret = []
                        for e in els:
                            prjid, prjkey = e.split(':', 1)
                            prjName = Workspace.Repositories.instance().remote().getProjectName( int(prjid) )
                            ret.append( "%s>%s" % (prjName, prjkey) )
                        return q( "\r\n".join(ret) )    
                    except Exception as e:
                        return q("")
                    
            if self.mydata[ index.row() ]['type'] in [ 'shared' ]:
                if index.column() == COL_VALUE:
                    try:
                        projectId, projectName, mainKey, secondKey = value.split(':')
                        if len(secondKey):
                            return q( '>'.join( [projectName, mainKey, secondKey] ) )
                        else:
                            return q( '>'.join( [projectName, mainKey] ) )
                    except Exception as e:
                        return q(value)

            if index.column() == COL_VALUE:
                return q(value)
                
            if index.column() == COL_NAME:
                descrParam = self.mydata[ index.row() ]['description']
                nameParam = self.mydata[ index.row() ]['name']
                if len(descrParam):
                    return q( "%s\n\n%s" % (nameParam, descrParam) )
                else:
                    return q(nameParam)
                    
            if index.column() == COL_DESCRIPTION:
                if sys.version_info > (3,):
                    return self.mydata[ index.row() ]['description']
                else:
                    return q( self.mydata[ index.row() ]['description'] )


        # font display
        if role == Qt.FontRole:
            if index.column() == COL_NAME:
                font = QFont()
                font.setBold(True)
                return q(font)
            if index.column() == COL_TYPE:
                font = QFont()
                font.setItalic(True)
                return q(font)
            if index.column() == COL_DESCRIPTION:
                font = QFont()
                font.setItalic(True)
                return q(font)

        # icon display
        if role == Qt.DecorationRole:
            if self.mydata[ index.row() ]['type'] == 'dataset':
                if index.column() == COL_VALUE:
                    return q(QIcon(":/tdx.png"))
            if self.mydata[ index.row() ]['type'] == 'remote-image':
                if index.column() == COL_VALUE:
                    return q(QIcon(":/png.png"))
            
            # new v11.1
            if self.mydata[ index.row() ]['type'] == 'local-file':
                if index.column() == COL_VALUE:
                    return q(QIcon(":/binary.png"))
                    
            # new in 8.1
            if self.mydata[ index.row() ]['type'] in [ 'local-image', 'snapshot-image' ]:
                if index.column() == COL_VALUE:
                    shortcut = base64.b64decode( value )
                    thumbail = QPixmap()
                    thumbail.loadFromData(shortcut)
                    if thumbail.height() > 120 and thumbail.width() > 120:
                        return QImage(thumbail).scaled(120,120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    else:
                        return QImage(thumbail)

        # main display
        if role == Qt.DisplayRole:
            if self.mydata[ index.row() ]['type'] in [ 'pwd' ]:
                if index.column() == COL_VALUE:
                    return q("*********")
                    
            if self.mydata[ index.row() ]['type'] in [ 'list' ]:
                if index.column() == COL_VALUE:
                    try:
                        els = value.split(",")
                        ret = []
                        for e in els:
                            ret.append( e )
                        return q( "\r\n".join(ret) )    
                    except Exception as e:
                        return q("")
                    
            if self.mydata[ index.row() ]['type'] in [ 'list-shared' ]:
                if index.column() == COL_VALUE:
                    try:
                        els = value.split(",")
                        ret = []
                        for e in els:
                            prjid, prjkey = e.split(':', 1)
                            prjName = Workspace.Repositories.instance().remote().getProjectName( int(prjid) )
                            ret.append( "%s>%s" % (prjName, prjkey) )
                        return q( "\r\n".join(ret) )    
                    except Exception as e:
                        return q("")
                    
            if self.mydata[ index.row() ]['type'] in [ 'shared' ]:
                if index.column() == COL_VALUE:
                    try:
                        projectId, projectName, mainKey, secondKey = value.split(':')
                        if len(secondKey):
                            return q( '>'.join( [projectName, mainKey, secondKey] ) )
                        else:
                            return q( '>'.join( [projectName, mainKey] ) )
                    except Exception as e:
                        return q(value)
            
            if self.mydata[ index.row() ]['type'] in [ 'local-image', 'snapshot-image' ]:
                if index.column() == COL_VALUE:
                    return q()
                    
            if self.mydata[ index.row() ]['type'] in [ 'local-file' ]:
                if index.column() == COL_VALUE:
                    try:
                        fName, fSize, fData= value.split(":", 2)
                    except Exception as e:
                        fName = ""
                    return q("%s" % fName)
                    
            if self.mydata[ index.row() ]['type'] in [ 'dataset', 'remote-image' ]:
                if index.column() == COL_VALUE:
                    # return the filename only
                    try:
                        return q( value.rsplit('.', 1)[0].rsplit('/', 1)[1] )
                    except Exception as e:
                        return q(value)
                        
            if index.column() == COL_VALUE:
                # fix added in v12.1
                if isinstance(value, float) or isinstance(value, int):
                        value = str(value)
                # end of fix
                
                limitValue = 20
                if len(value) > limitValue:
                    return q( "%s [...]" % value[:limitValue] )
                else:
                    return q(value)
                    
            elif index.column() == COL_DESCRIPTION:
                lines = value.splitlines()
                if len(lines) > 1:
                    return q( "%s [...]" % lines[0] )
                else:
                    return q(value)
            else:
                return q(value)
        
        # on edit
        elif role == Qt.EditRole:
            return q(value)
        
        # set background color
        elif role == Qt.BackgroundRole:
            # extract the color to use
            newColor = Settings.instance().readValue( key = 'TestProperties/parameters-default-color' )
            if 'color' in self.mydata[ index.row() ]:
                if len(self.mydata[ index.row() ]['color']):
                    newColor = self.mydata[ index.row() ]['color']
            # apply it
            return q( QBrush(QColor(newColor)) )
            
        elif role == Qt.ForegroundRole:
            if 'color' in self.mydata[ index.row() ]:
                if self.mydata[ index.row() ]['color'] == "#000000":
                    return q( QBrush(QColor("#FFFFFF")) )
            return q( QBrush(QColor("#000000")) )
            
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
            orig_ = self.mydata[ index.row() ]['name']
            name_ = self.checkName( index.row(), value)
            # new in v11: not accept special character on test parameter
            try:
                name_.encode("ascii")
            except Exception as e:
                name_ = orig_
            # end of new
            self.mydata[ index.row() ]['name'] = name_
            if orig_ != name_:
                dataChanged = True
                self.owner.NameParameterUpdated.emit(orig_, name_  )
        
        elif index.column() == COL_TYPE:
            orig_ = self.mydata[ index.row() ]['type']
            self.mydata[ index.row() ]['type'] = value
            if orig_ != value:
                dataChanged = True
                self.mydata[ index.row() ]['value'] = ''
        
        elif index.column() == COL_VALUE:
            orig_ = self.mydata[ index.row() ]['value']
            self.mydata[ index.row() ]['value'] = value
            if orig_ != value:
                dataChanged = True
        
        elif index.column() == COL_DESCRIPTION:
            orig_ = self.mydata[ index.row() ]['description']
            self.mydata[ index.row() ]['description'] = value
            if orig_ != value:
                dataChanged = True
                self.owner.setData(signal=False) # resize column
        else:
            pass

        sortSupported = Settings.instance().readValue( key = 'TestProperties/parameters-sort-auto' )
        if QtHelper.str2bool(sortSupported):
            self.mydata.sort(key=operator.itemgetter('name'))
        self.owner.adjustColumns()   
        self.owner.adjustRows()    
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
        if index.column() == COL_ID:
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
        sav = self.mydata[row]['name']
        
        if not len(name): # issue 211
            return sav

        for it in self.mydata:
            if it['name'] == name.upper():
                return sav
        if name.isdigit():
            return sav
        
        if name[0] in [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', '-' ]:
            return sav
        
        return name.upper() 

################# Delegate items ###################
class NameDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Name delegate item
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
        self.owner = parent
        self.col_ = col_

    def getValue(self, index):
        """
        Return value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValue(sourceIndex)

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
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            proxyIndex.model().sourceModel().setValue(sourceIndex, value)

    def getValueRow(self, index):
        """
        Return value by row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValueRow(sourceIndex)

    def createEditor(self, parent, option, index):
        """
        Create the editor

        @param parent: 
        @type parent:

        @param option: 
        @type option:

        @param index: 
        @type index:

        @return: editor delegate
        @rtype:
        """
        value = self.getValue(index)
        if index.column() == self.col_:
            editor = QLineEdit(parent)
            return editor
        return QItemDelegate.createEditor(self, parent, option, index)

    def setModelData(self, editor, model, index):
        """
        Accessor to set the model of data

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

class ValueDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Value delegate item
    """
    def __init__ (self, parent, colVal, colDescr):
        """
        Contructs ValueDelegate item delegate
        
        @param parent: 
        @type parent:

        @param items_: 
        @type items_:

        @param colVal: 
        @type colVal:

        @param colDescr: 
        @type colDescr:
        """
        QItemDelegate.__init__(self, parent)
        self.owner = parent
        self.colVal = colVal
        self.colDescr = colDescr

    def getValue(self, index):
        """
        Return value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValue(sourceIndex)
    
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
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            proxyIndex.model().sourceModel().setValue(sourceIndex, value)

    def getValueRow(self, index):
        """
        Returns value by row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValueRow(sourceIndex)

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
        value = self.getValueRow(index)

        if index.column() == self.colVal:
            if value['type'] == 'none':
                return None
            
            elif value['type'] == 'str':
                editor = QLineEdit(parent)

            elif value['type'] == 'cache':
                editor = QLineEdit(parent)

            elif value['type'] == 'pwd':
                editor = QLineEdit(parent)

            elif value['type'] == 'alias':
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                params = []
                for pr in self.owner.model.getData() :
                    if value['name'] == pr['name']:
                        continue
                    params.append(pr['name'])
                editor.addItems ( params  )
            
            elif value['type'] == 'float':
                editor = QLineEdit(parent)
                validator = QDoubleValidator(editor)
                validator.setNotation(QDoubleValidator.StandardNotation)
                editor.setValidator(validator)
                editor.installEventFilter(self)
            
            elif value['type'] == 'int':
                editor = QLineEdit(parent)
                validator = QIntValidator (editor)
                editor.setValidator(validator)
                editor.installEventFilter(self)
                
            elif value['type'] == 'hex':
                editor = QLineEdit(parent)
                validator = QRegExpValidator(editor)
                validator.setRegExp(QRegExp("[0-9a-fA-F]+"))
                editor.setValidator(validator)
                editor.installEventFilter(self)
                
            elif value['type'] == 'dataset':
                dataset = self.owner.importDataset()
                if dataset is not None:
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(dataset))
                return None
            
            elif value['type'] == 'local-image':
                image = self.owner.importEmbeddedImage()
                if image is not None:
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    if sys.version_info > (3,): # python 3 support
                        index.model().sourceModel().setData(sourceIndex, q( str(image, "utf8") ))
                    else:
                        index.model().sourceModel().setData(sourceIndex, q(image))
                return None
                
            elif value['type'] == 'local-file':
                anyFile = self.owner.importEmbeddedFile()
                if anyFile is not None:
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex, q(anyFile))
                return None
                
            elif value['type'] == 'snapshot-image':
                sourceIndex = self.owner.proxyModel.mapToSource( index )
                self.owner.importSnapshotImage(sourceIndex.row())
                return None

            elif value['type'] == 'remote-image':
                image = self.owner.importImage()
                if image is not None:
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(image))
                return None
            
            elif value['type'] == 'self-ip':
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                serverEths = Settings.instance().serverContext['network']
                ips = []
                for eth in serverEths:
                    if 'ip' in eth and 'name' in eth :
                        ips.append( "%s (%s)" % ( eth['ip'], eth['name'] )  )
                editor.addItems ( ips  )
            
            elif value['type'] == 'self-mac':
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                serverEths = Settings.instance().serverContext['network']
                macs = []
                for eth in serverEths:
                    if 'mac' in eth and 'name' in eth:
                        macs.append( "%s (%s)" % ( eth['mac'], eth['name'] ) )
                editor.addItems ( macs  )
           
            elif value['type'] == 'self-eth':
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                serverEths = Settings.instance().serverContext['network']
                eths = []
                for eth in serverEths:
                    if 'name' in eth and eth['name'] != 'all':
                        eths.append( eth['name'] )
                editor.addItems ( eths  )
            
            elif value['type'] == 'bool':
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                editor.addItems ( ['False', 'True']  )
                
            elif value['type'] == 'list-shared':
                editorDialog = ListSharedParameter(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    paramValues = editorDialog.getValues()
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(paramValues))
                return None
                
            elif value['type'] == 'shared':
                editorDialog = SharedParameter()
                if editorDialog.exec_() == QDialog.Accepted:
                    paramValues = editorDialog.getValues()
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(paramValues))
                return None

            elif value['type'] == 'list':
                editorDialog = ListValues(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    paramValues = editorDialog.getValues()
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(paramValues))
                return None
                
            elif value['type'] == 'text':
                editorDialog = TextValues(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    paramText = editorDialog.getText()
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(paramText))
                return None
                
            elif value['type'] == 'json':
                editorDialog = JsonValues(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    paramText = editorDialog.getText()
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(paramText))
                return None
                
            elif value['type'] == 'custom':
                editorDialog = CustomValues(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    paramText = editorDialog.getText()
                    sourceIndex = self.owner.proxyModel.mapToSource( index )
                    index.model().sourceModel().setData(sourceIndex,q(paramText))
                return None
                
            elif value['type'] == 'date':
                try:
                    dayDescr, monthDescr, yearDescr = value['value'].split('/')
                    dateDescr =  QDate( int(yearDescr), int(monthDescr), int(dayDescr) )
                except Exception as e:
                    dateDescr = QDate.currentDate()
                editor = QDateEdit(dateDescr, parent)
            
            elif value['type'] == 'time':
                try:
                    hourDescr, minDescr, secDescr = value['value'].split(':')
                    timeDescr =  QTime( int(hourDescr), int(minDescr), int(secDescr) )
                except Exception as e:
                    timeDescr = QTime.currentTime()
                editor = QTimeEdit(timeDescr, parent)
            
            elif value['type'] == 'date-time':
                try:
                    dateVal = value['value'].split(' ')
                    dayDescr, monthDescr, yearDescr = dateVal[0].split('/')
                    hourDescr, minDescr, secDescr =  dateVal[1].split(':')
                    datetimeDescr =  QDateTime( int(yearDescr), int(monthDescr), int(dayDescr), 
                                                int(hourDescr), int(minDescr), int(secDescr) )
                except Exception as e:
                    datetimeDescr = QDateTime.currentDateTime()
                editor = QDateTimeEdit(datetimeDescr, parent)
            
            elif value['type'] == 'ipv4-address':
                editor = QLineEdit(parent)
                editor.setInputMask('000.000.000.000')
            
            elif value['type'] == 'ipv6-address':
                editor = QLineEdit(parent)
                editor.setInputMask('HHHH:HHHH:HHHH:HHHH:HHHH:HHHH:HHHH:HHHH')
            
            elif value['type'] == 'mac-address':
                editor = QLineEdit(parent)
                editor.setInputMask('HH:HH:HH:HH:HH:HH')
            
            elif value['type'] == 'phonenumber-fr':
                editor = QLineEdit(parent)
                editor.setInputMask('99 99 99 99 99;_')
            
            else:
                editor = QLineEdit(parent)
            
            return editor
        return QItemDelegate.createEditor(self, parent, option, index)

    def setModelData(self, editor, model, index):
        """
        Accessor to set the model of data

        @param editor: 
        @type editor:

        @param model: 
        @type model:

        @param index: 
        @type index:
        """
        if type(editor) == QLineEdit:
            qvalue = editor.text()
        elif type(editor) == QComboBox:
            qvalue = editor.currentText()
        elif type(editor) == QDateEdit:
            qvalue = editor.text()
        elif type(editor) == QTimeEdit:
            qvalue = editor.text()
        elif type(editor) == QDateTimeEdit:
            qvalue = editor.text()
        else:
            qvalue = 'Undefined'
        
        value = QtHelper.displayToValue( q(qvalue) )
        self.setValue(index, value)
    
    def onItemActivated(self, index): 
        """
        Close editor on index changed
        """
        self.commitData.emit(self.sender())
        self.closeEditor.emit(self.sender(), QAbstractItemDelegate.NoHint)
        
class ComboTypeDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Combo type delegate item
    """
    def __init__ (self, parent, items_, col_ ):
        """
        Contructs ComboTypeDelegate item delegate
        
        @param parent: 
        @type parent:

        @param items_: 
        @type items_:

        @param col_: 
        @type col_:
        """
        QItemDelegate.__init__(self, parent)
        self.owner = parent
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
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValue(sourceIndex)

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
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            proxyIndex.model().sourceModel().setValue(sourceIndex, value)

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
            editor = QComboBox(parent)
            editor.activated.connect(self.onItemActivated)
            editor.addItem (value)
            editor.insertSeparator(1)
            for i in xrange(len(self.items_)):
                if len(self.items_[i]) == 0:
                    editor.insertSeparator(i + 2)
                else:
                    editor.addItem (self.items_[i])
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
        Set the data editor

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
        Set the data model

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

class DescriptionsDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Descriptions delegate item
    """
    def __init__(self, parent, col_):
        """
        @param value: 
        @type value:

        @param value: 
        @type value:
        """
        QItemDelegate.__init__(self, parent)
        self.owner = parent
        self.col_ = col_
    
    def getValue(self, index):
        """
        Returns value

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValue(sourceIndex)

    def getValueRow(self, index):
        """
        Returns value by row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            return proxyIndex.model().sourceModel().getValueRow(sourceIndex)

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
        proxyIndex = index
        if proxyIndex.isValid():
            sourceIndex = self.owner.proxyModel.mapToSource( proxyIndex )
            proxyIndex.model().sourceModel().setValue(sourceIndex, value)

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
        value = self.getValue(index)

        if index.column() == self.col_:
            editorDialog = DescriptionDialog(value)
            if editorDialog.exec_() == QDialog.Accepted:
                argsProbe = editorDialog.getDescr()
                sourceIndex = self.owner.proxyModel.mapToSource( index )
                index.model().sourceModel().setData(sourceIndex,q(argsProbe))

##################### Dialogs ######################
class AddParameterDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Add parameter dialog
    """
    def __init__(self, parent, paramName='PARAM', datasetView=False):
        """
        Dialog to add parameters

        @param parent: 
        @type parent:
        """
        super(AddParameterDialog, self).__init__(parent)
        self.paramName=paramName
        self.parent__ = parent
        self.datasetView__ = datasetView
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.labelName = QLabel(self.tr("Parameter Name:") )
        self.nameEdit = QLineEdit(self.paramName)
        nameLayout = QHBoxLayout()
        nameLayout.addWidget( self.labelName )
        nameLayout.addWidget( self.nameEdit )

        self.labelDescr = QLabel(self.tr("Description:") )
        self.descrEdit = QTextEdit()

        self.labelType= QLabel(self.tr("Type:") )
        self.comboType = QComboBox()
        self.initComboType()
        typeLayout = QHBoxLayout()
        typeLayout.addWidget( self.labelType )
        typeLayout.addWidget( self.comboType )

        self.labelValue= QLabel(self.tr("Value:") )
        self.valueEdit = QLineEdit()
        self.valueLayout = QHBoxLayout()
        self.valueLayout.addWidget( self.labelValue )
        self.valueLayout.addWidget( self.valueEdit )

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
        mainLayout.addLayout(self.valueLayout)
        mainLayout.addWidget(self.labelDescr)
        mainLayout.addWidget(self.descrEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Test Config > Add Parameter"))
        self.resize(350, 250)
        self.center()

    def initComboType(self):
        """
        Initialize the combobox of parameters type
        """
        for i in xrange(len(TYPES_PARAM)):
            if len(TYPES_PARAM[i]) == 0:
                self.comboType.insertSeparator(i + 2)
            else:
                self.comboType.addItem (TYPES_PARAM[i])

    def createConnections (self):
        """
        Create pyqt connection
        """
        self.buttonBox.accepted.connect(self.onAdd)
        self.buttonBox.rejected.connect(self.reject)
        self.comboType.currentIndexChanged[str].connect(self.onTypeChanged)

    def onAdd(self):
        """
        Called on add paramter
        """
        # new in v11: not accept special character on test parameter
        try:
            if sys.version_info > (3,): # python3 support
                self.nameEdit.text().encode("ascii")
        except Exception as e:
            QMessageBox.critical(self, self.tr("Test Parameter") , self.tr("Invalid parameter name!") )
        else:
        # end of new
            if sys.version_info > (3,): # python3 support
                if unicode(self.nameEdit.text().upper()):
                    self.accept()
            else:
                if unicode(self.nameEdit.text().toUpper()):
                    self.accept()

    def onTypeChanged(self, paramType):
        """
        Called when the type of parameters is changed
        """
        self.valueLayout.removeWidget(self.valueEdit)
        self.valueEdit.hide()
        self.valueEdit.setEnabled(True)

        if paramType == 'str':
            self.valueEdit = QLineEdit(self)
            
        elif paramType == 'cache':
            self.valueEdit = QLineEdit(self)
 
        elif paramType == 'pwd':
            self.valueEdit = QLineEdit(self)

        elif paramType == 'none':
            self.valueEdit = QLineEdit(self)
            self.valueEdit.setEnabled(False)
        
        elif paramType == 'alias':
            self.valueEdit = QComboBox(self)
            params = []
            for pr in self.parent__.model.getData() :
                params.append(pr['name'])
            self.valueEdit.addItems ( params  )
        
        elif paramType == 'float':
            self.valueEdit = QLineEdit(self)
            validator = QDoubleValidator(self.valueEdit)
            validator.setNotation(QDoubleValidator.StandardNotation)
            self.valueEdit.setValidator(validator)
            self.valueEdit.installEventFilter(self)
                
        elif paramType == 'hex':
            self.valueEdit = QLineEdit(self)
            validator = QRegExpValidator(self.valueEdit)
            validator.setRegExp(QRegExp("[0-9a-fA-F]+"))
            self.valueEdit.setValidator(validator)
            self.valueEdit.installEventFilter(self)
            
        elif paramType == 'int':
            self.valueEdit = QLineEdit(self)
            validator = QIntValidator (self.valueEdit)
            self.valueEdit.setValidator(validator)
            self.valueEdit.installEventFilter(self)
        
        elif paramType == 'dataset':
            dataset = self.parent__.importDataset()
            if dataset is not None:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(dataset)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)

        elif paramType == 'local-image':
                image = self.parent__.importEmbeddedImage()
                self.raise_()
                self.activateWindow()

                if image is not None:
                    self.valueEdit = QLineEdit(self)
                    if sys.version_info > (3,): # python 3 support
                        self.valueEdit.setText( str(image,"utf8" ) )
                    else:
                        self.valueEdit.setText( image )
                    self.valueEdit.setEnabled(False)
                else:
                    self.valueEdit = QLineEdit(self)
                    self.valueEdit.setEnabled(False)
                    
        elif paramType == 'local-file':
                anyFile = self.parent__.importEmbeddedFile()
                self.raise_()
                self.activateWindow()

                if anyFile is not None:
                    self.valueEdit = QLineEdit(self)
                    self.valueEdit.setText( anyFile )
                    self.valueEdit.setEnabled(False)
                else:
                    self.valueEdit = QLineEdit(self)
                    self.valueEdit.setEnabled(False)
                    
        elif paramType == 'snapshot-image':
            self.valueEdit.setEnabled(False)

        elif paramType == 'remote-image':
            image = self.parent__.importImage()
            if image is not None:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(image)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)
        
        elif paramType == 'shared':
            editorDialog = SharedParameter()
            if editorDialog.exec_() == QDialog.Accepted:
                paramValues = editorDialog.getValues()
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(paramValues)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)

        elif paramType == 'list-shared':
            editorDialog = ListSharedParameter("")
            if editorDialog.exec_() == QDialog.Accepted:
                paramValues = editorDialog.getValues()
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(paramValues)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)
                
        elif paramType == 'list':
            editorDialog = ListValues('')
            if editorDialog.exec_() == QDialog.Accepted:
                paramValues = editorDialog.getValues()
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(paramValues)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)
                
        elif paramType == 'text':
            editorDialog = TextValues('')
            if editorDialog.exec_() == QDialog.Accepted:
                paramText = editorDialog.getText()
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(paramText)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)                
                
        elif paramType == 'json':
            editorDialog = JsonValues('')
            if editorDialog.exec_() == QDialog.Accepted:
                paramText = editorDialog.getText()
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(paramText)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)
                
        elif paramType == 'custom':
            editorDialog = CustomValues('')
            if editorDialog.exec_() == QDialog.Accepted:
                paramText = editorDialog.getText()
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setText(paramText)
                self.valueEdit.setEnabled(False)
            else:
                self.valueEdit = QLineEdit(self)
                self.valueEdit.setEnabled(False)  
                
        elif paramType == 'self-ip':
            self.valueEdit = QComboBox(self)
            serverEths = Settings.instance().serverContext['network']
            ips = []
            for eth in serverEths:
                if 'ip' in eth and 'name' in eth :
                    ips.append( "%s (%s)" % ( eth['ip'], eth['name'] )  )
            self.valueEdit.addItems ( ips  )
       
        elif paramType == 'self-mac':
            self.valueEdit = QComboBox(self)
            serverEths = Settings.instance().serverContext['network']
            macs = []
            for eth in serverEths:
                if 'mac' in eth and 'name' in eth:
                    macs.append( "%s (%s)" % ( eth['mac'], eth['name'] ) )
            self.valueEdit.addItems ( macs  )
        
        elif paramType == 'self-eth':
            self.valueEdit = QComboBox(self)
            serverEths = Settings.instance().serverContext['network']
            eths = []
            for eth in serverEths:
                if 'name' in eth and eth['name'] != 'all':
                    eths.append( eth['name'] )
            self.valueEdit.addItems ( eths  )
        
        elif paramType == 'bool':
            self.valueEdit = QComboBox(self)
            self.valueEdit.addItems ( ['False', 'True']  )
        
        elif paramType == 'date':
            dateDescr = QDate.currentDate()
            self.valueEdit = QDateEdit(dateDescr, self)
        
        elif paramType == 'time':
            timeDescr = QTime.currentTime()
            self.valueEdit = QTimeEdit(timeDescr, self)
       
        elif paramType == 'date-time':
            datetimeDescr = QDateTime.currentDateTime()
            self.valueEdit = QDateTimeEdit(datetimeDescr, self)
        
        else:
            self.valueEdit = QLineEdit(self)
        
        self.valueLayout.addWidget(self.valueEdit)

        self.valueEdit.show()

    def getParameterValue(self):
        """
        Returns the value of the parameter
        """
        if type(self.valueEdit) == QComboBox:
            qvalue = self.valueEdit.currentText()
        else:
            qvalue = self.valueEdit.text()
        if sys.version_info > (3,): # python3 support
            nameUpper = unicode(self.nameEdit.text().upper())
        else:
            nameUpper = unicode(self.nameEdit.text().toUpper())
        r = {'name': nameUpper, 'type': unicode(self.comboType.currentText()),
                'description': unicode(self.descrEdit.toPlainText()), 'value': unicode(qvalue)}
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

        self.setWindowTitle(self.tr("Test Config > Parameter Description"))
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

##################### List shared ######################
class SharedListModel(QAbstractListModel):
    """
    Shared list model
    """
    def __init__(self, parent=None): 
        """
        Constructor
        """
        super(SharedListModel, self).__init__(parent)
        self.listdata = []
 
    def rowCount(self, parent=QModelIndex()): 
        """
        Return the number of row
        """
        return len(self.listdata) 
        
    def getData(self):
        """
        Return model data

        @return:
        @rtype:
        """
        return self.listdata
        
    def setDataModel(self, datain):
        """
        Set model data

        @param datain: 
        @type datain:
        """
        self.listdata = datain

        if sys.version_info > (3,):
            self.beginResetModel()
            self.endResetModel()
        else:
            self.reset()
            
    def data(self, index, role=Qt.DisplayRole): 
        """
        Return data
        """
        if not index.isValid():
            return q()
        
        if role == Qt.DisplayRole:
            return q(self.listdata[index.row()]['name'])
            
        return q()
        
class SharedListView(QListView, Logger.ClassLogger):
    """
    Shared list view
    """
    def __init__(self, parent):
        """
        Contructs ParametersTableView table view

        @param parent: 
        @type parent:
        """
        QListView.__init__(self, parent)

        self.model__ = SharedListModel(self)

        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setDynamicSortFilter(True)
        
        self.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.model__)
        
    def clear(self):
        """
        Clear the list
        """
        self.model__.setDataModel( [] )
    
    def addItems(self, items):
        """
        Add items in the list
        """
        items.sort(key=operator.itemgetter('name'))
        self.model__.setDataModel( items )
        
class ListItemEnhanced(QListWidgetItem):
    """
    List item enhanced
    """
    def __init__(self, key, value):
        """
        Item for shared parameters
        """
        QListWidgetItem.__init__(self, key)
        self.keyName = key
        self.keyValue = value
        
class ListItemEnhanced2(QListWidgetItem):
    """
    List item enhanced
    """
    def __init__(self, key, projectId, projectName):
        """
        Item for list shared parameters
        """
        QListWidgetItem.__init__(self, key)
        self.projectId = projectId
        self.setToolTip( "Project: %s" % projectName )

class ListSharedParameter(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    List of shared parameters dialog
    """
    def __init__(self, dataValues, parent=None):
        """
        Dialog to fill arguments for the dict

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(ListSharedParameter, self).__init__(parent)
        self.testEnvironment = Settings.instance().serverContext['test-environment']
        self.dataValues = dataValues
        
        self.createDialog()
        self.createConnections()

        # init first main list
        self.onProjectChanged(projectId=0)
        self.loadDefaultData()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.setMinimumHeight(500)
        mainLayout = QVBoxLayout()

        self.projectCombo = QComboBox(self)
        projects = []
        for prj in self.testEnvironment :
            projects.append(prj['project_name'])
            
        # sort project list by  name
        projects= sorted(projects)
        i = 0
        for p in projects:
            if p.lower() == "common":
                break
            i += 1
        common = projects.pop(i)      
        projects.insert(0, common)
        
        self.projectCombo.addItems ( projects  )
        self.projectCombo.insertSeparator(1)
        
        # set the current project
        project = Workspace.Repositories.instance().remote().getCurrentProject()
        for i in xrange(self.projectCombo.count()):
            item_text = self.projectCombo.itemText(i)
            if str(project) == str(item_text):
                self.projectCombo.setCurrentIndex(i)

        self.mainList = SharedListView(self)

        
        self.paramSelected = QListWidget(self)
        self.valueLabel = QLabel()

        self.mainFilterText = QLineEdit(self)
        self.mainFilterText.setToolTip(self.tr("Name filter"))

        buttonLayout = QVBoxLayout()
        self.delButton = QPushButton(self.tr("Delete"), self)
        self.delButton.setEnabled(False)
        self.clearButton = QPushButton(self.tr("Remove All"), self)
        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Ok"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"),  self.tr("Cancel"), self)
        self.upButton = QPushButton( self.tr("Move Up"), self)
        self.upButton.setEnabled(False)
        self.downButton = QPushButton( self.tr("Move Down"), self)
        self.downButton.setEnabled(False)

        buttonLayout.addWidget( self.upButton )
        buttonLayout.addWidget( self.downButton )
        buttonLayout.addWidget( self.delButton )
        buttonLayout.addWidget( self.clearButton )

        buttonLayout.addWidget( self.okButton )
        buttonLayout.addWidget( self.cancelButton )
        buttonLayout.addStretch(1)
        
        keyLayout = QVBoxLayout()
        keyLayout.addWidget(self.mainFilterText)
        keyLayout.addWidget(self.mainList)

        selectedLayout = QVBoxLayout()
        selectedLayout.addWidget(QLabel("Selected Parameters"))
        selectedLayout.addWidget(self.paramSelected)
        
        listLayout = QHBoxLayout()
        listLayout.addLayout(keyLayout)
        listLayout.addLayout(selectedLayout)
        listLayout.addLayout(buttonLayout)

        mainLayout.addWidget(self.projectCombo)
        mainLayout.addLayout(listLayout)
        mainLayout.addWidget(self.valueLabel)

        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Test Config > List of shared parameters") )

    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.projectCombo.currentIndexChanged.connect(self.onProjectChanged)
        self.mainFilterText.textChanged.connect(self.onMainFilterChanged)
        self.mainList.clicked.connect(self.onMainListClicked)
        self.mainList.doubleClicked.connect(self.onMainListDoubleClicked)
        self.clearButton.clicked.connect(self.clearList)
        self.upButton.clicked.connect(self.upItem)
        self.downButton.clicked.connect(self.downItem)
        self.delButton.clicked.connect(self.delItem)
        
        self.paramSelected.itemClicked.connect(self.onItemSelected)
        self.paramSelected.itemSelectionChanged.connect(self.onItemSelectionChanged)

    def onItemSelectionChanged(self):
        """
        Called on item selection changed
        """
        self.onItemSelected(itm=None)

    def onItemSelected(self, itm):
        """
        Call on item selected
        """
        selectedItems = self.paramSelected.selectedItems()
        if len(selectedItems):
            self.delButton.setEnabled(True)
            self.upButton.setEnabled(True)
            self.downButton.setEnabled(True)
        else:
            self.delButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.downButton.setEnabled(False)
            
    def clearList(self):
        """
        Clear the list
        """
        self.paramSelected.clear()
        self.delButton.setEnabled(False)
        self.upButton.setEnabled(False)
        
    def upItem(self):
        """
        Up item
        """
        currentRow = self.paramSelected.currentRow()
        currentItem = self.paramSelected.takeItem(currentRow)
        self.paramSelected.insertItem(currentRow - 1, currentItem)

    def downItem(self):
        """
        Down item
        """
        currentRow = self.paramSelected.currentRow()
        currentItem = self.paramSelected.takeItem(currentRow)
        self.paramSelected.insertItem(currentRow + 1, currentItem)

    def delItem(self):
        """
        Delete item
        """
        self.delButton.setEnabled(False)
        # remove item
        model = self.paramSelected.model()
        for selectedItem in self.paramSelected.selectedItems():
            qIndex = self.paramSelected.indexFromItem(selectedItem)
            model.removeRow(qIndex.row())

    def onProjectChanged(self, projectId):
        """
        On project changed
        """
        # clear the list
        self.mainList.clear()

        # read the current project
        parameters = None
        for prj in self.testEnvironment :
            if prj['project_name'] == self.projectCombo.currentText():
                parameters = prj['test_environment']
                break
        
        # load the main list
        if parameters is not None:
            mains = []
            allItems = []
            for param in parameters :
                allItems.append( {'name': param['name'].upper(), 'value': param['value'] } )
                
            # adding params to the list view
            allItems.sort(key=operator.itemgetter('name'))
            self.mainList.addItems( allItems )
    def onMainFilterChanged(self):
        """
        On main filter changed
        """
        # Qt.MatchExactly 	0 	Performs QVariant-based matching.
        # Qt.MatchFixedString 	8 	Performs string-based matching. String-based comparisons are case-insensitive unless the MatchCaseSensitive flag is also specified.
        # Qt.MatchContains 	1 	The search term is contained in the item.
        # Qt.MatchStartsWith 	2 	The search term matches the start of the item.
        # Qt.MatchEndsWith 	3 	The search term matches the end of the item.
        # Qt.MatchCaseSensitive 	16 	The search is case sensitive.
        # Qt.MatchRegExp 	4 	Performs string-based matching using a regular expression as the search term.
        # Qt.MatchWildcard 	5 	Performs string-based matching using a string with wildcards as the search term.
        # Qt.MatchWrap 	32 	Perform a search that wraps around, so that when the search reaches the last item in the model, it begins again at the first item and continues until all items have been examined.
        # Qt.MatchRecursive 	64 	Searches the entire hierarchy.
        syntax = QRegExp.RegExp
        caseSensitivity = Qt.CaseInsensitive
        regExp = QRegExp(self.mainFilterText.text(),  caseSensitivity, syntax)

        self.mainList.proxyModel.setFilterKeyColumn( 0 )
        self.mainList.proxyModel.setFilterRegExp(regExp)
        
    def onMainListDoubleClicked(self):
        """
        On double click on the main list
        """
        proxyIndexes = self.mainList.selectedIndexes()
        if not proxyIndexes:
            return

        sourceIndex = self.mainList.proxyModel.mapToSource( proxyIndexes[0] )
        selectedIndex = sourceIndex.row()
        row = self.mainList.model__.getData()[selectedIndex]
        
        project = self.projectCombo.currentText()
        projectId = None
        for prj in self.testEnvironment :
            if prj['project_name'] == self.projectCombo.currentText():
                projectId = prj['project_id']
                break
                
        if projectId is not None:       
            newItem = ListItemEnhanced2( key=row['name'], projectId=projectId, projectName="%s"% project)
            self.paramSelected.addItem( newItem )

    def onMainListClicked(self):
        """
        On click on the main list
        """
        proxyIndexes = self.mainList.selectedIndexes()
        if not proxyIndexes:
            return
            
        sourceIndex = self.mainList.proxyModel.mapToSource( proxyIndexes[0] )
        selectedIndex = sourceIndex.row()
        row = self.mainList.model__.getData()[selectedIndex]
        
        if isinstance(row['value'], dict):
            self.valueLabel.setText( "%s: ..." % row['name'] )
        else:
            self.valueLabel.setText( "%s: %s" % (row['name'], row['value']) )

    def loadDefaultData(self):
        """
        Load default data
        """
        try:
            if self.dataValues != '':
            
                allValues = self.dataValues.split(',')
                for v in allValues: 
                    prjid, prjkey = v.split(':')
                    prjName = ''
                    for prj in self.testEnvironment :
                        if int( prj['project_id'] ) == int(prjid):
                            prjName  = prj['project_name']
                    newItem = ListItemEnhanced2( key=prjkey, projectId=prjid, projectName="%s"% prjName)
                    self.paramSelected.addItem( newItem )

        except Exception as e:
            self.error( "unable to load default data: %s" % e )
            
    def getValues(self):
        """
        Return values
        """
        ret = []
        
        for i in xrange(self.paramSelected.count()):
            qitem = self.paramSelected.item(i)
            ret.append( "%s:%s" % (qitem.projectId, qitem.text() ) )
        

        retStr = ','.join(ret)

        if retStr.endswith(','):
            retStr = retStr[:-1]
        return retStr
        
class SharedParameter(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Shared parameters dialog
    """
    def __init__(self, parent=None):
        """
        Dialog to fill arguments for the dict

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(SharedParameter, self).__init__(parent)
        self.testEnvironment = Settings.instance().serverContext['test-environment']
        self.createDialog()
        self.createConnections()

        # init first main list
        self.onProjectChanged(projectId=0)

    def createDialog (self):
        """
        Create qt dialog
        """
        self.setMinimumHeight(500)
        mainLayout = QVBoxLayout()

        buttonLayout = QVBoxLayout()
        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Ok"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"),  self.tr("Cancel"), self)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addStretch(1)
        
        self.projectCombo = QComboBox(self)
        projects = []
        for prj in self.testEnvironment :
            projects.append(prj['project_name'])
            
        # sort project list by  name
        projects = sorted(projects)
        i = 0
        for p in projects:
            if p.lower() == "common":
                break
            i += 1
        common = projects.pop(i)      
        projects.insert(0, common)
        
        self.projectCombo.addItems ( projects  )
        self.projectCombo.insertSeparator(1)
        
        # set the current project
        project = Workspace.Repositories.instance().remote().getCurrentProject()
        for i in xrange(self.projectCombo.count()):
            item_text = self.projectCombo.itemText(i)
            if str(project) == str(item_text):
                self.projectCombo.setCurrentIndex(i)

        self.mainList = SharedListView(self)
        
        self.secondList = QListWidget(self)
        self.secondList.setSortingEnabled(True)
        self.valueLabel = QLabel()

        self.mainFilterText = QLineEdit(self)
        self.mainFilterText.setToolTip(self.tr("Name filter"))

        keyLayout = QVBoxLayout()
        keyLayout.addWidget(self.mainFilterText)
        
        keyLayout.addWidget(self.mainList)

        listLayout = QHBoxLayout()
        listLayout.addLayout(keyLayout)
        listLayout.addWidget(self.secondList)
        listLayout.addLayout(buttonLayout)

        mainLayout.addWidget(self.projectCombo)
        mainLayout.addLayout(listLayout)
        mainLayout.addWidget(self.valueLabel)
        

        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Test Config > Shared parameters") )

    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.projectCombo.currentIndexChanged.connect(self.onProjectChanged)
        self.secondList.itemSelectionChanged.connect(self.onSecondListSelectionChanged)
        self.mainList.clicked.connect(self.onMainListClicked)
        self.secondList.currentItemChanged.connect(self.onSecondListClicked)
        self.mainFilterText.textChanged.connect(self.onMainFilterChanged)
        
    def onProjectChanged(self, projectId):
        """
        On project changed
        """
        # clear the list
        self.mainList.clear()

        # read the current project
        parameters = None
        for prj in self.testEnvironment :
            if prj['project_name'] == self.projectCombo.currentText():
                parameters = prj['test_environment']
                break
        
        # load the main list
        if parameters is not None:
            mains = []
            allItems = []
            for param in parameters :
                allItems.append( {'name': param['name'].upper(), 'value': param['value'] } )

            # adding params to the list view
            allItems.sort(key=operator.itemgetter('name'))
            self.mainList.addItems( allItems )
            
    def onMainListSelectionChanged(self):
        """
        On selection changed on main list
        """
        # clear the list
        self.secondList.clear()

        # read the current project
        parameters = None
        for prj in self.testEnvironment :
            if prj['project_name'] == self.projectCombo.currentText():
                parameters = prj['test_environment']
                break

        proxyIndexes = self.mainList.selectedIndexes()
        if not proxyIndexes:
            return
            
        # load the main list
        if parameters is not None:
            sourceIndex = self.mainList.proxyModel.mapToSource( proxyIndexes[0] )
            selectedIndex = sourceIndex.row()
            row = self.mainList.model__.getData()[selectedIndex]
            
            subParameters = None
            for param in parameters :
                if param['name'].upper() ==  str(row['name']).upper():
                    subParameters = param['value']
                    break
            
            # load the second list
            if subParameters is not None:
                #seconds = []
                if isinstance( subParameters, dict):
                    for k, v in subParameters.items() :
                        subItem = ListItemEnhanced( key=k.upper(), value=v)
                        subItem.setToolTip( "%s" % v )
                        self.secondList.addItem( subItem )

    def onSecondListSelectionChanged(self):
        """
        On selection changed on second list
        """
        pass
    
    def onMainFilterChanged(self):
        """
        On main filter changed
        """
        # Qt.MatchExactly 	0 	Performs QVariant-based matching.
        # Qt.MatchFixedString 	8 	Performs string-based matching. String-based comparisons are case-insensitive unless the MatchCaseSensitive flag is also specified.
        # Qt.MatchContains 	1 	The search term is contained in the item.
        # Qt.MatchStartsWith 	2 	The search term matches the start of the item.
        # Qt.MatchEndsWith 	3 	The search term matches the end of the item.
        # Qt.MatchCaseSensitive 	16 	The search is case sensitive.
        # Qt.MatchRegExp 	4 	Performs string-based matching using a regular expression as the search term.
        # Qt.MatchWildcard 	5 	Performs string-based matching using a string with wildcards as the search term.
        # Qt.MatchWrap 	32 	Perform a search that wraps around, so that when the search reaches the last item in the model, it begins again at the first item and continues until all items have been examined.
        # Qt.MatchRecursive 	64 	Searches the entire hierarchy.

        syntax = QRegExp.RegExp
        caseSensitivity = Qt.CaseInsensitive
        regExp = QRegExp(self.mainFilterText.text(),  caseSensitivity, syntax)

        self.mainList.proxyModel.setFilterKeyColumn( 0 )
        self.mainList.proxyModel.setFilterRegExp(regExp)

    def onMainListClicked(self):
        """
        On second list clicked
        """
        proxyIndexes = self.mainList.selectedIndexes()
        if not proxyIndexes:
            return
            
        sourceIndex = self.mainList.proxyModel.mapToSource( proxyIndexes[0] )
        selectedIndex = sourceIndex.row()
        row = self.mainList.model__.getData()[selectedIndex]
        
        if isinstance(row['value'], dict):
            self.valueLabel.setText( "%s: ..." % row['name'] )
        else:
            self.valueLabel.setText( "%s: %s" % (row['name'], row['value']) )
        
        self.secondList.clear()
        
        # read the current project
        parameters = None
        for prj in self.testEnvironment :
            if prj['project_name'] == self.projectCombo.currentText():
                parameters = prj['test_environment']
                break
                
        # load the main list
        if parameters is not None:
            sourceIndex = self.mainList.proxyModel.mapToSource( proxyIndexes[0] )
            selectedIndex = sourceIndex.row()
            row = self.mainList.model__.getData()[selectedIndex]
            
            
            # itemSelected = items[0].text()
            subParameters = None
            for param in parameters :
                if param['name'].upper() ==  str(row['name']).upper():
                    subParameters = param['value']
                    break
            
            # load the second list
            if subParameters is not None:
                #seconds = []
                if isinstance( subParameters, dict):
                    for k, v in subParameters.items() :
                        subItem = ListItemEnhanced( key=k.upper(), value=v)
                        subItem.setToolTip( "%s" % v )
                        self.secondList.addItem( subItem )

    def onSecondListClicked(self, itemCurrent, itemPrevious ):
        """
        On second list clicked
        """
        if itemCurrent is None:
            return
        self.valueLabel.setText( "%s: %s" % (itemCurrent.keyName, itemCurrent.keyValue) )
        
    def getValues(self):
        """
        Return values
        """
        project = self.projectCombo.currentText()
        projectId = None
        for prj in self.testEnvironment :
            if prj['project_name'] == self.projectCombo.currentText():
                projectId = prj['project_id']
                break

        proxyIndexes = self.mainList.selectedIndexes()
        if not proxyIndexes:
            return
        sourceIndex = self.mainList.proxyModel.mapToSource( proxyIndexes[0] )
        selectedIndex = sourceIndex.row()
        row = self.mainList.model__.getData()[selectedIndex]
        
        itemSecond = self.secondList.selectedItems()

        if len(row) and len(itemSecond):
            return "%s:%s:%s:%s" % (projectId, project, row['name'], itemSecond[0].text())
        elif not len(row) and not len(itemSecond):
            return "%s:%s::" % (projectId, project)
        elif len(row) and not len(itemSecond):
            return "%s:%s:%s:" % (projectId, project, row['name'])
        else:
            return ':::'

class MyHighlighter( QSyntaxHighlighter ):
    """
    My highlighter syntax
    """
    def __init__( self, parent ):
        """
        Constructor
        """
        QSyntaxHighlighter.__init__( self, parent )
        self.parent = parent

        comment = QTextCharFormat()
        caches = QTextCharFormat()
        inputs = QTextCharFormat()
        captures = QTextCharFormat()
        others1 = QTextCharFormat()
        others2 = QTextCharFormat()
        others3 = QTextCharFormat()
            
        self.highlightingRules = []

        # cache
        brush = QBrush( Qt.darkBlue, Qt.SolidPattern )
        pattern = QRegExp( "\[!CACHE:[\w-]+(:[\w-]+)*:\]" )
        pattern.setMinimal( True )
        caches.setForeground( brush )
        caches.setFontWeight( QFont.Bold )
        ruleCaches = HighlightingRule( pattern, caches )

        # input
        brush2 = QBrush( Qt.darkCyan, Qt.SolidPattern )
        pattern2 = QRegExp( "\[!INPUT:[\w-]+:\]" )
        pattern2.setMinimal( True )
        inputs.setForeground( brush2 )
        inputs.setFontWeight( QFont.Bold )
        ruleInputs = HighlightingRule( pattern2, inputs )

        # comment
        brush3 = QBrush( Qt.red, Qt.SolidPattern )

        pattern3 = QRegExp( "^#.*$" )
        pattern3.setMinimal( True )
        comment.setForeground( brush3 )
        ruleComment = HighlightingRule( pattern3, comment )

        # capture
        brush4 = QBrush( Qt.darkYellow, Qt.SolidPattern )
        pattern4 = QRegExp( "\[!CAPTURE:[\w-]+(:.*)?:\]" )
        pattern4.setMinimal( True )
        captures.setForeground( brush4 )
        captures.setFontWeight( QFont.Bold )
        ruleCaptures = HighlightingRule( pattern4, captures )

        # others keywords
        brush6 = QBrush( Qt.darkBlue, Qt.SolidPattern )
        pattern6 = QRegExp( Settings.instance().readValue( key='Editor/parameter-custom-keywords1' ) )
        pattern6.setMinimal( True )
        others1.setForeground( brush6 )
        ruleOthers1 = HighlightingRule( pattern6, others1 )
        
        # others keywords
        brush7 = QBrush( Qt.darkGray, Qt.SolidPattern )
        pattern7 = QRegExp( Settings.instance().readValue( key='Editor/parameter-custom-keywords2' ) )
        pattern7.setMinimal( True )
        others2.setForeground( brush7 )
        ruleOthers2 = HighlightingRule( pattern7, others2 )
        
        # others keywords
        brush8 = QBrush( Qt.darkCyan, Qt.SolidPattern )
        pattern8 = QRegExp( Settings.instance().readValue( key='Editor/parameter-custom-keywords3' ) )
        pattern8.setMinimal( True )
        others3.setForeground( brush8 )
        ruleOthers3 = HighlightingRule( pattern8, others3 )
        
        self.highlightingRules.append( ruleComment )
        self.highlightingRules.append( ruleCaches )
        self.highlightingRules.append( ruleInputs )
        self.highlightingRules.append( ruleCaptures )
        self.highlightingRules.append( ruleOthers1 )
        self.highlightingRules.append( ruleOthers2 )
        self.highlightingRules.append( ruleOthers3 )
                
    def highlightBlock( self, text ):
        """
        Highligh block
        """
        for rule in self.highlightingRules:
            expression = QRegExp( rule.pattern )
            index = expression.indexIn( text )
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat( index, length, rule.format )
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState( 0 )

class HighlightingRule():
    """
    Highlighting rule
    """
    def __init__( self, pattern, format ):
        """
        Constructor
        """
        self.pattern = pattern
        self.format = format
        
class CustomValues(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Custom values dialog
    """
    def __init__(self, dataValues, parent=None):
        """
        Dialog to fill arguments for the list

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(CustomValues, self).__init__(parent)
        self.dataValues = dataValues
        self.isTextChanged = False
        self.createDialog()
        self.createConnections()
        
        self.wrapCheckbox.setChecked(True)
        
    def createDialog (self):
        """
        Create qt dialog
        """
        self.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);

            dialog-yes-icon: url(:/ok.png);
            dialog-no-icon: url(:/ko.png);

            dialog-open-icon: url(:/ok.png);

            dialog-apply-icon: url(:/ok.png);
            dialog-reset-icon: url(:/ko.png);
        }""")
        self.setMinimumHeight(500)
        self.setMinimumWidth(800)
        
        mainLayout = QGridLayout()

        self.globalText = QtHelper.LineTextWidget()
        self.textEdit = self.globalText.getTextEdit()

        self.rawFind = QtHelper.RawFind(parent=self, editor=self.textEdit, buttonNext=True)
        
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.textEdit.setStyleSheet("""font: 9pt "Courier";""")
        self.textEdit.setPlainText(self.dataValues)
        highlighter = MyHighlighter( self.textEdit )

        self.wrapCheckbox = QCheckBox("Line wrap mode")

        buttonLayout = QVBoxLayout()

        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Ok"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"), self.tr("Cancel"), self)

        buttonLayout.addWidget( self.okButton )
        buttonLayout.addWidget( self.cancelButton )
        buttonLayout.addWidget( QLabel("") ) 
        buttonLayout.addWidget( self.wrapCheckbox ) 
        buttonLayout.addWidget( QLabel("") ) 
        buttonLayout.addWidget( QLabel("Available Keywords:") )
        
        labelInput = QLabel("\t[!INPUT: :]")
        labelCache = QLabel("\t[!CACHE: :]")
        labelCapture = QLabel("\t[!CAPTURE: :]")
        
        labelFromInput = QLabel("\t[!FROM:INPUT: :]")
        labelFromCache = QLabel("\t[!FROM:CACHE: :]")
        
        labelFont = QFont()
        labelFont.setBold(True)
        labelInput.setFont(labelFont)
        labelCache.setFont(labelFont)
        labelCapture.setFont(labelFont)

        paletteFromInput = QPalette()
        paletteFromInput.setColor(QPalette.Foreground,Qt.darkCyan)
        paletteFromCache = QPalette()
        paletteFromCache.setColor(QPalette.Foreground,Qt.darkBlue)
        paletteInput = QPalette()
        paletteInput.setColor(QPalette.Foreground,Qt.darkCyan)
        paletteCache = QPalette()
        paletteCache.setColor(QPalette.Foreground,Qt.darkBlue)
        paletteCapture = QPalette()
        paletteCapture.setColor(QPalette.Foreground,Qt.darkYellow)
        labelInput.setPalette(paletteInput)
        labelCache.setPalette(paletteCache)
        labelCapture.setPalette(paletteCapture)
        labelFromInput.setPalette(paletteFromInput)
        labelFromCache.setPalette(paletteFromCache)

        buttonLayout.addWidget( labelInput ) 
        buttonLayout.addWidget( labelCache )
        buttonLayout.addWidget( labelCapture )
        buttonLayout.addWidget( QLabel("") )
        buttonLayout.addWidget( labelFromInput )
        buttonLayout.addWidget( labelFromCache )
        
        buttonLayout.addStretch(1)

        mainLayout.addWidget(self.globalText, 1, 0)
        mainLayout.addWidget(self.rawFind, 2, 0)
        mainLayout.addLayout(buttonLayout, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Test Config > Custom Values") )
        
        # maximize button
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        
        showMaximize = Settings.instance().readValue( key = 'TestProperties/custom-dialog-maximized' )
        if QtHelper.str2bool(showMaximize):
            self.showMaximized()
        
    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.onCancel)
        self.wrapCheckbox.stateChanged.connect(self.onWrapModeChanged)
        self.textEdit.textChanged.connect(self.onTextChanged)
        
    def onCancel(self):
        """
        On cancel
        """
        if self.isTextChanged:
            reply = QMessageBox.question(self, self.tr("Custom parameter"), self.tr("Are you sure to cancel?"),
                                            QMessageBox.Yes | QMessageBox.No )
            if reply == QMessageBox.Yes:
                self.isTextChanged = False
                self.reject()
        else:
            self.isTextChanged = False
            self.reject()
        
    def onTextChanged(self):
        """
        On text changed
        """
        if self.textEdit.toPlainText() != self.dataValues:
            self.isTextChanged = True
            self.dataValues = self.textEdit.toPlainText()
        else:
            self.isTextChanged = False
            
    def onWrapModeChanged(self, mode):
        """
        On wrap mode changed
        """
        if mode == Qt.Checked:
            self.textEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        
    def getText(self):
        """
        Return text
        """
        return self.textEdit.toPlainText()
        
class JsonValues(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Text values dialog
    """
    def __init__(self, dataValues, parent=None):
        """
        Dialog to fill arguments for the list

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(JsonValues, self).__init__(parent)
        self.dataValues = dataValues
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.setMinimumHeight(500)
        self.setMinimumWidth(800)
        
        mainLayout = QGridLayout()

        self.textEdit = QtHelper.CustomEditor(self, jsonLexer=False)
        self.textEdit.setText(self.dataValues)
        
        buttonLayout = QVBoxLayout()

        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Ok"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"), self.tr("Cancel"), self)

        buttonLayout.addWidget( self.okButton )
        buttonLayout.addWidget( self.cancelButton )
        buttonLayout.addStretch(1)

        mainLayout.addWidget(self.textEdit, 1, 0)
        mainLayout.addLayout(buttonLayout, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Test Config > Json Values") )
       
    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def getText(self):
        """
        Return text
        """
        return self.textEdit.text()
        
class TextValues(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Text values dialog
    """
    def __init__(self, dataValues, parent=None):
        """
        Dialog to fill arguments for the list

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(TextValues, self).__init__(parent)
        self.dataValues = dataValues
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.setMinimumHeight(500)
        self.setMinimumWidth(800)
        
        mainLayout = QGridLayout()

        self.textEdit = QTextEdit ()
        self.textEdit.setPlainText(self.dataValues)
        
        buttonLayout = QVBoxLayout()

        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Ok"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"), self.tr("Cancel"), self)

        buttonLayout.addWidget( self.okButton )
        buttonLayout.addWidget( self.cancelButton )
        buttonLayout.addStretch(1)

        mainLayout.addWidget(self.textEdit, 1, 0)
        mainLayout.addLayout(buttonLayout, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Test Config > Text Values") )
       
    def createConnections (self):
        """
        Create qt connections
        """
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def getText(self):
        """
        Return text
        """
        return self.textEdit.toPlainText()
        
class ListValues(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    List values dialog
    """
    def __init__(self, dataValues, parent=None):
        """
        Dialog to fill arguments for the list

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(ListValues, self).__init__(parent)
        self.dataValues = dataValues
        self.createDialog()
        self.createConnections()
        self.loadDefaultData()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)
        mainLayout = QGridLayout()

        editLayout = QHBoxLayout()
        self.labelHelp = QLabel(self.tr("Value to add:") )
        self.lineEdit = QLineEdit()
        self.addButton = QPushButton(self.tr("Add"), self)
        
        editLayout.addWidget( self.labelHelp )
        editLayout.addWidget( self.lineEdit )
        editLayout.addWidget( self.addButton )

        self.listBox = QListWidget()

        buttonLayout = QVBoxLayout()

        self.delButton = QPushButton(self.tr("Remove"), self)
        self.delButton.setEnabled(False)
        self.editButton = QPushButton(self.tr("Edit"), self)
        self.editButton.setEnabled(False)
        self.clearButton = QPushButton(self.tr("Remove All"), self)
        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Ok"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"), self.tr("Cancel"), self)
        self.upButton = QPushButton( self.tr("Move Up"), self)
        self.upButton.setEnabled(False)
        self.downButton = QPushButton( self.tr("Move Down"), self)
        self.downButton.setEnabled(False)

        buttonLayout.addWidget( self.upButton )
        buttonLayout.addWidget( self.downButton )

        buttonLayout.addWidget( self.delButton )
        buttonLayout.addWidget( self.editButton )
        buttonLayout.addWidget( self.clearButton )

        buttonLayout.addWidget( self.okButton )
        buttonLayout.addWidget( self.cancelButton )
        buttonLayout.addStretch(1)

        mainLayout.addLayout(editLayout, 0, 0)
        mainLayout.addWidget(self.listBox, 1, 0)
        mainLayout.addLayout(buttonLayout, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Test Config > List Values") )
       
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
        self.upButton.clicked.connect(self.upItem)
        self.downButton.clicked.connect(self.downItem)
        self.listBox.itemClicked.connect(self.onItemSelected)
        self.listBox.itemSelectionChanged.connect(self.onItemSelectionChanged)

    def clearList(self):
        """
        Clear the list
        """
        self.listBox.clear()
        self.delButton.setEnabled(False)
        self.editButton.setEnabled(False)
        self.upButton.setEnabled(False)
        self.downButton.setEnabled(False)

    def onItemSelectionChanged(self):
        """
        Called on item selection changed
        """
        self.onItemSelected(itm=None)

    def onItemSelected(self, itm):
        """
        Call on item selected
        """
        selectedItems = self.listBox.selectedItems()
        if len(selectedItems):
            self.delButton.setEnabled(True)
            self.editButton.setEnabled(True)
            self.upButton.setEnabled(True)
            self.downButton.setEnabled(True)
        else:
            self.delButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.downButton.setEnabled(False)

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
            if sys.version_info > (3,): # python3 support
                self.lineEdit.setText( model.data(qIndex) )
            else:
                self.lineEdit.setText( model.data(qIndex).toString() )
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
        # separator in value ?
        if "," in self.lineEdit.text():
            QMessageBox.warning(self, self.tr("Prepare list"), self.tr("Incorrect value!") )
        else:
            txt = self.lineEdit.text()
            if txt != '':
                self.listBox.insertItem (self.listBox.count(), txt)
                self.lineEdit.setText('')

    def upItem(self):
        """
        Up item
        """
        currentRow = self.listBox.currentRow()
        currentItem = self.listBox.takeItem(currentRow)
        self.listBox.insertItem(currentRow - 1, currentItem)

    def downItem(self):
        """
        Down item
        """
        currentRow = self.listBox.currentRow()
        currentItem = self.listBox.takeItem(currentRow)
        self.listBox.insertItem(currentRow + 1, currentItem)

    def loadDefaultData(self):
        """
        Load default data
        """
        try:
            if self.dataValues != '':
                allValues = self.dataValues.split(',')
                self.listBox.insertItems(0, allValues)
        except Exception as e:
            self.error( "unable to load default data: %s" % e )

    def getValues(self):
        """
        Return list of values
        """
        listValues = []
        model = self.listBox.model()
        # iterate all items in a QListWidget
        for index in xrange(self.listBox.count()):
            itm = self.listBox.item(index)
            qIndex = self.listBox.indexFromItem(itm)
            if sys.version_info > (3,): # python 3 support
                listValues.append( unicode(model.data(qIndex)) )
            else:
                listValues.append( unicode(model.data(qIndex).toString()) )

        listValuesStr = ','.join(listValues)

        if listValuesStr.endswith(','):
            listValuesStr = listValuesStr[:-1]
        return listValuesStr

##############   main table view   #################
class ParametersTableView(QTableView, Logger.ClassLogger):
    """
    Parameters table view
    """
    NameParameterUpdated = pyqtSignal(str, str) 
    DataChanged = pyqtSignal() 
    NbParameters = pyqtSignal(int)
    def __init__(self, parent, forParamsOutput=False, forTestConfig=False):
        """
        Contructs ParametersTableView table view

        @param parent: 
        @type parent:
        """
        QTableView.__init__(self, parent)

        self.forParamsOutput = forParamsOutput
        self.forTestConfig = forTestConfig
        self.model = None
        self.__mime__ = "application/x-%s-test-config-parameters" % Settings.instance().readValue( key='Common/acronym' ).lower()
        self.datasetView = False

        self.cacheUndo = []
        self.undoCut = False
        self.undoPaste = False

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

        # map proxy indexes to source
        sourceIndexes = []
        for proxyIndex in indexes:
            if not proxyIndex.isValid():
                return
            else:
                sourceIndexes.append( self.proxyModel.mapToSource( proxyIndex ) )

        if sourceIndexes:
            rowVal = self.model.getValueRow( sourceIndexes[0] )
            if len(rowVal) > 1 :
                
                meta = QByteArray()
                
                if self.datasetView:
                    meta.append( "__%s__" % rowVal['name'] )
                else:
                    if self.forParamsOutput:
                        meta.append( "output('%s')" % rowVal['name'] )
                    else:
                        meta.append( "input('%s')" % rowVal['name'] )

                # create mime data object
                mime = QMimeData()
                mime.setData('application/x-%s-parameter-item' % Settings.instance().readValue( key='Common/acronym' ).lower() , 
                            meta )
                # start drag )
                drag = QDrag(self)
                drag.setMimeData(mime)    
                
                drag.exec_(Qt.CopyAction)

    def createWidgets (self):
        """
        Create qt widgets
        """
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setDynamicSortFilter(True)

        self.model = ParametersTableModel(self)

        self.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.model)

        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)

        self.setFrameShape(QFrame.NoFrame)
        self.setShowGrid(True)
        self.setGridStyle (Qt.DotLine)

        self.setItemDelegateForColumn( COL_NAME, NameDelegate(self, COL_NAME) )
        # empty value is to indicate a separator
        self.setItemDelegateForColumn( COL_TYPE, ComboTypeDelegate(self, TYPES_PARAM, COL_TYPE) )
        self.setItemDelegateForColumn( COL_VALUE, ValueDelegate(self, COL_VALUE, COL_DESCRIPTION) )
        self.setItemDelegateForColumn( COL_DESCRIPTION, DescriptionsDelegate(self, COL_DESCRIPTION) )

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.adjustRows()
        
        # adjust default columns
        self.setColumnWidth(COL_ID, 25)
        self.setColumnWidth(COL_NAME, 60)
        self.setColumnWidth(COL_TYPE, 50)
        self.setColumnWidth(COL_VALUE, 50)
        self.setColumnWidth(COL_DESCRIPTION, 100)

    def createConnections (self):
        """
        Create qt connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)
        self.clicked.connect( self.onAbstractItemClicked)  
        QApplication.clipboard().dataChanged.connect(self.onClipboardUpdated) 
        QApplication.clipboard().changed.connect(self.onClipboardUpdatedNew) 

    def createActions (self):
        """
        Actions defined:
         * add 
         * del
         * copy
         * paste
         * clear
        """
        self.addAction = QtHelper.createAction(self, self.tr("&Add\nParameter"), self.addParameter, icon = QIcon(":/test-parameter-add.png"),
                                                    tip = self.tr('Add a new parameter') )
        self.delAction = QtHelper.createAction(self, self.tr("&Delete"), self.removeItem, icon = QIcon(":/test-parameter-del.png"),
                                                    tip = self.tr('Delete selected parameter(s)') )
        self.copyAction = QtHelper.createAction(self, self.tr("Copy"), self.copyItem, icon = QIcon(":/test-parameter-copy.png"), 
                                                    tip = self.tr('Copy selected parameter(s)'), shortcut='Ctrl+C' )
        self.pasteAction = QtHelper.createAction(self, self.tr("Paste"), self.pasteItem, icon = QIcon(":/test-parameter-paste.png"),
                                                    tip = self.tr('Paste parameter(s)'), shortcut='Ctrl+V' )
        self.cutAction = QtHelper.createAction(self, self.tr("Cut"), self.cutItem, icon = None, 
                                                    tip = self.tr('Cut selected parameter(s)') )

        self.undoAction = QtHelper.createAction(self, self.tr("Undo"), self.undoItem, icon = QIcon(":/test-parameter-undo.png"),
                                                    tip = self.tr('Undo') )

        self.clearAction = QtHelper.createAction(self, self.tr("Clear"), self.clearItems, icon = QIcon(":/test-parameter-clear.png"), 
                                                    tip = self.tr('Clear all parameters') )
        self.openAction = QtHelper.createAction(self, self.tr("Open"), self.openItem, icon = QIcon(":/open-test.png"),
                                                    tip = self.tr('Open') )

        self.addPurpleColorAction = QtHelper.createAction(self, self.tr("&Purple"), self.addPurpleColor, icon = None,
                                                    tip = self.tr('Purple color') )
        self.addYellowColorAction = QtHelper.createAction(self, self.tr("&Yellow"), self.addYellowColor, icon = None,
                                                    tip = self.tr('Yellow color') )
        self.addBlueColorAction = QtHelper.createAction(self, self.tr("&Blue"), self.addBlueColor, icon = None, 
                                                    tip = self.tr('Blue color') )
        self.addGreenColorAction = QtHelper.createAction(self, self.tr("&Green"), self.addGreenColor, icon = None, 
                                                    tip = self.tr('Green color') )
        self.addRedColorAction = QtHelper.createAction(self, self.tr("&Red"), self.addRedColor, icon = None, 
                                                    tip = self.tr('Red color') )
        self.addDefaultColorAction = QtHelper.createAction(self, self.tr("&Default"), self.addDefaultColor, icon = None,
                                                    tip = self.tr('Default color') )
        self.addWhiteColorAction = QtHelper.createAction(self, self.tr("&White"), self.addWhiteColor, icon = None, 
                                                    tip = self.tr('White color') )
        self.addOrangeColorAction = QtHelper.createAction(self, self.tr("&Orange"), self.addOrangeColor, icon = None,
                                                    tip = self.tr('Orange color') )
        self.addGrayColorAction = QtHelper.createAction(self, self.tr("&Gray"), self.addGrayColor, icon = None,
                                                    tip = self.tr('Gray color') )
        self.menuColor = QMenu(self.tr("Add colors"))
        self.menuColor.addAction( self.addOrangeColorAction )
        self.menuColor.addAction( self.addPurpleColorAction )
        self.menuColor.addAction( self.addGreenColorAction )
        self.menuColor.addAction( self.addRedColorAction )
        self.menuColor.addAction( self.addBlueColorAction )
        self.menuColor.addAction( self.addYellowColorAction )
        self.menuColor.addAction( self.addGrayColorAction )
        self.menuColor.addAction( self.addWhiteColorAction )
        self.menuColor.addSeparator()
        self.menuColor.addAction( self.addDefaultColorAction )

        self.colorsAction = QtHelper.createAction(self, self.tr("&Colors"), None, 
                                                    tip = self.tr('Add colors'), icon=QIcon(":/colors.png") )
        self.colorsAction.setMenu(self.menuColor)

        # set default values
        self.defaultActions()

    def defaultActions(self):
        """
        Set default actions
        """
        self.addAction.setEnabled(True)
        self.delAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.cutAction.setEnabled(False)
        self.pasteAction.setEnabled(False)
        self.clearAction.setEnabled(True)
        self.openAction.setEnabled(False)
        self.undoAction.setEnabled(False)
        self.colorsAction.setEnabled(False)

    def addPurpleColor(self):
        """
        Add purple color
        """
        self.addColor(color="#DBADFF")

    def addGreenColor(self):
        """
        Add green color
        """
        self.addColor(color="#D4FFAF")

    def addRedColor(self):
        """
        Add red color
        """
        self.addColor(color="#FCABBD")
        
    def addOrangeColor(self):
        """
        Add red color
        """
        self.addColor(color="#FFD800")

    def addBlueColor(self):
        """
        Add blue color
        """
        self.addColor(color="#C1EEFF")

    def addGrayColor(self):
        """
        Add blue color
        """
        self.addColor(color="#C3C3C3")
        
    def addYellowColor(self):
        """
        Add yellow color
        """
        self.addColor(color="#FDFFBD")

    def addWhiteColor(self):
        """
        Add white color
        """
        self.addColor(color="#FFFFFF")

    def addDefaultColor(self):
        """
        Add default color
        """
        self.addColor(color=Settings.instance().readValue( key = 'TestProperties/parameters-default-color' ))

    def addColor(self, color):
        """
        Add generic color
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return

        # map proxy indexes to source
        sourceIndexes = []
        for proxyIndex in indexes:
            if not proxyIndex.isValid():
                return
            else:
                sourceIndexes.append( self.proxyModel.mapToSource( proxyIndex ) )

        for sourceIndex in sourceIndexes:
            self.model.getValueRow(sourceIndex)['color'] = color

        self.setData()
        self.model.beginResetModel()
        self.model.endResetModel()
        
    def onAbstractItemClicked(self):
        """
        Called on item clicked
        """
        proxyIndexes = self.selectedIndexes()
        if not proxyIndexes:
            self.colorsAction.setEnabled(False)
            return

        self.delAction.setEnabled(True)
        self.copyAction.setEnabled(True)
        self.cutAction.setEnabled(True)
        self.colorsAction.setEnabled(True)

        if len(proxyIndexes) <= len(HEADERS):
            sourceIndex = self.proxyModel.mapToSource( proxyIndexes[0] )
            selectedIndex = sourceIndex.row()
            row = self.model.getData()[selectedIndex]
            if row['type'] in [ 'dataset', 'remote-image', 'local-file']:
                self.openAction.setEnabled(True)
            else:
                self.openAction.setEnabled(False)
        else:
            self.openAction.setEnabled(False)

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
            self.colorsAction.setEnabled(False)
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.pasteAction )
            self.menu.addAction( self.undoAction )
            self.menu.addSeparator()
            self.menu.addAction( self.clearAction )
        else:
            self.colorsAction.setEnabled(True)
            self.menu.addAction( self.colorsAction )
            self.menu.addSeparator()
            self.menu.addAction( self.delAction )
            self.menu.addAction( self.addAction )
            self.menu.addSeparator()
            self.menu.addAction( self.cutAction )
            self.menu.addAction( self.copyAction )
            self.menu.addAction( self.pasteAction )
            self.menu.addAction( self.undoAction )
            self.menu.addSeparator()
            self.menu.addAction( self.openAction )
            self.menu.addSeparator()
            self.menu.addAction( self.clearAction )
        self.menu.popup( self.mapToGlobal(pos) )

    def undoItem(self):
        """
        Undo latest action cut or paste
        """
        if len(self.cacheUndo):
            if self.undoCut:
                for cache in self.cacheUndo:
                    for item in cache:
                        self.insertItem( newData=item )
                
            if self.undoPaste:
                for cache in self.cacheUndo:
                    for item in cache:
                        self.removeValue( paramName=item["name"] )
                self.setData( signal = True )
                
        self.undoCut = False
        self.undoPaste = False
        self.cacheUndo = []
        self.undoAction.setEnabled(False)
         
    def openItem(self):
        """
        Open item
        """
        proxyIndexes = self.selectedIndexes()
        if not proxyIndexes:
            return

        if len(proxyIndexes) > len(HEADERS):
            return
        
        # map proxy index to source
        sourceIndex = self.proxyModel.mapToSource( proxyIndexes[0] )
        selectedIndex = sourceIndex.row()

        # try to open the file
        row = self.model.getData()[selectedIndex]
        if row['type'] in [ 'dataset', 'remote-image']:
            if row['value'].startswith('remote-tests('):
                fileName = row['value'].split('):/', 1)[1]
                projectName = row['value'].split('remote-tests(', 1)[1].split('):/', 1)[0]
                projectId = Workspace.WRepositories.instance().remote().getProjectId(projectName)
                UCI.instance().openFileRepo(pathFile=fileName, repo=UCI.REPO_TESTS, project=projectId)
            elif row['value'].startswith('local-tests:/'):
                fileAll = row['value'].split('local-tests:/')[1]

                fileExtension = fileAll.rsplit(".", 1)[1]
                filePath, leftdata = fileAll.rsplit('/', 1)
                fileName = leftdata.rsplit('.', 1)[0]

                Workspace.WDocumentViewer.instance().newTab(path = filePath, filename = fileName, extension = fileExtension, repoDest=UCI.REPO_TESTS_LOCAL)

            elif row['value'].startswith('undefined:/'):
                fileAll = row['value'].split('undefined:/')[1]

                fileExtension = fileAll.rsplit(".", 1)[1]
                filePath, leftdata = fileAll.rsplit('/', 1)
                fileName = leftdata.rsplit('.', 1)[0]

                Workspace.WDocumentViewer.instance().newTab(path = filePath, filename = fileName, extension = fileExtension, repoDest=UCI.REPO_UNDEFINED)

            else:
                pass
        elif row['type'] in [ 'local-file' ]:
        
            try:
                fName, fSize, fData= row['value'].split(":", 2)
            except Exception as e:
                fName = ""
                        
            fileName = QFileDialog.getSaveFileName(self, self.tr("Save file"), fName, "*.*")
            if len(fileName):
                f = open(fileName, 'wb')
                f.write( base64.b64decode(fData)  )
                f.close()
        else:
            self.openAction.setEnabled(False)
            
    def cutItem(self):
        """
        Cut the selected rom (delete and coy
        """
        self.copyItem(saveCache=True)
        self.removeItem(question=False)

        self.undoCut = True
        self.undoPaste = False
        self.undoAction.setEnabled(True)
        
    def copyItem(self, saveCache=False):
        """
        Copy the selected row or more to the clipboard
        """
        self.trace('Test Param > Starting to copy, retrieving data from model')
        # retrieve data from model      
        rowData = []
        for proxyIndex in self.selectionModel().selectedRows():
            sourceIndex = self.proxyModel.mapToSource( proxyIndex )
            rowData.append(self.model.getData()[sourceIndex.row()])

        if rowData:
            self.trace('Test Param > Picke data: %s' % rowData )
            
            if saveCache:  
                self.cacheUndo = []
                self.cacheUndo.append(rowData) 
                
            # pickle data
            mime = QMimeData()
            mime.setData( self.__mime__ , QByteArray(pickle.dumps(rowData)) )
            
            self.trace('Test Param > Copying to clipboard')
            # copy to clipboard
            QApplication.clipboard().setMimeData(mime,QClipboard.Clipboard)
            self.trace('Test Param > Coppied to clipboard')
            self.pasteAction.setEnabled(True)

    def pasteItem(self):
        """
        Paste item
        """
        self.trace('Test Param > Starting to paste, read from clipboard')
        # read from clipboard
        mimeData = QApplication.clipboard().mimeData()
        if not mimeData.hasFormat(self.__mime__):
            return None
        
        self.trace('Test Param > Unpickle data')
        data = mimeData.data(self.__mime__)
        if not data:
            return None
        try:
            objects = pickle.loads(data.data())
            # save to cache to undo 
            self.cacheUndo = []
            self.cacheUndo.append(objects) 
            # insert
            for o in objects:
                self.insertItem( newData=o )
        except Exception as e:
            self.error( "unable to deserialize %s" % str(e) )
            return None
        
        self.undoCut = False
        self.undoPaste = True
        self.undoAction.setEnabled(True)
        
    def onClipboardUpdatedNew(self, mode):
        """
        On clipboard updated
        """
        self.trace( 'New - clipboard updated' )
        c = QApplication.clipboard()
        formatsList = c.mimeData().formats() 
        if sys.version_info > (3,):
            self.trace('New - Test Param > something in the clipboard: %s' % ",".join(formatsList) )
        else:
            self.trace('New - Test Param > something in the clipboard: %s' % formatsList.join(",") ) # formatsList = QStringList

    def onClipboardUpdated(self):
        """
        On clipboard updated
        """
        self.trace( 'clipboard updated' )
        c = QApplication.clipboard()
        formatsList = c.mimeData().formats() 
        if sys.version_info > (3,):
            self.trace('Test Param > something in the clipboard: %s' % ",".join(formatsList) )
        else:
            self.trace('Test Param > something in the clipboard: %s' % formatsList.join(",") ) # formatsList = QStringList
        
        if c.mimeData().hasFormat(self.__mime__):
            self.trace('Test Param > clipboard: its for me' )
            self.pasteAction.setEnabled(True)
        else:
            self.trace('Test Param > clipboard: not for me' )
            self.pasteAction.setEnabled(False)

    def addParameter(self):
        """
        Add parameter
        """
        addDialog = AddParameterDialog(parent=self, datasetView=self.datasetView)
        if addDialog.exec_() == QDialog.Accepted:
            parameter = addDialog.getParameterValue()
            self.insertItem(newData=parameter)

    def insertItem(self, newData=False):
        """
        Insert item
        """
        index = self.currentIndex()
        if not index.isValid():
            row = self.model.rowCount()
        else:
            row = index.row()
        data = self.model.getData()
       
        # default param or not
        if newData:
            tpl = newData
        else:
            tpl =   {'name': 'PARAM', 'type': 'str', 'description': '', 'value': '', 'color': ''}
        
        # name must be unique
        for it in data:
            if it['name'] == tpl['name']:
                tpl['name'] += '_1'
        
        # add data to model
        data.insert(row + 1, tpl)
        
        sortSupported = Settings.instance().readValue( key = 'TestProperties/parameters-sort-auto' )
        if QtHelper.str2bool(sortSupported):
            data.sort(key=operator.itemgetter('name'))

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
        Clear all items
        """
        reply = QMessageBox.question(self, self.tr("Clear all parameters"), self.tr("Are you sure ?"),
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

    def clear (self):
        """
        clear contents
        """
        self.model.setDataModel( [] )
        self.NbParameters.emit( 0 )
        
    def removeItem (self, question=True):
        """
        Removes the selected row 
        """
        # get selected proxy indexes
        indexes = self.selectedIndexes()
        if not indexes:
            return
         
        # map proxy indexes to source
        sourceIndexes = []
        for proxyIndex in indexes:
            if not proxyIndex.isValid():
                return
            else:
                sourceIndexes.append( self.proxyModel.mapToSource( proxyIndex ) )
        
        if sourceIndexes:
            if not question:
                self.removeValues(sourceIndexes)
            else:
                answer = QMessageBox.question(self,  self.tr("Remove"),  self.tr("Do you want to remove selected parameter (s)?"), 
                        QMessageBox.Yes | QMessageBox.No)
                if answer == QMessageBox.Yes:
                    self.removeValues(sourceIndexes)

    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [COL_NAME, COL_TYPE, COL_VALUE]:
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
        params = data['parameter']
        
        # sort params
        sortSupported = Settings.instance().readValue( key = 'TestProperties/parameters-sort-auto' )
        if QtHelper.str2bool(sortSupported):
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
        
        datas = self.model.getData()
        self.NbParameters.emit( len(datas) )
        
    def removeValues(self, indexes):
        """
        Remove values from data

        @param indexes: 
        @type indexes:
        """
        if not indexes:
            return
        
        # extract name, name are unique
        datas = self.model.getData()
        allNames = []

        # remove duplicate index
        cleanIndexes = {}
        for index in indexes:
            if index.row() not in cleanIndexes:
                cleanIndexes[index.row()] = index

        for cleanIndex in list(cleanIndexes.keys()): # for python3 support
            allNames.append( datas[cleanIndex]['name'] )

        self.trace('Parameter to remove: %s' % allNames)
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

        self.model.beginResetModel()
        self.model.endResetModel()

    def setDefaultView(self):
        """
        Set the default view
        """
        self.datasetView = False
        self.setColumnHidden(COL_TYPE,False)

    def setDatasetView(self):
        """
        Set dataset view
        """
        self.datasetView = True
        self.setColumnHidden(COL_TYPE,True)

    def onSnapshotImage(self, snapshot, destRow):
        """
        On snapshot image
        """
        # no more hide the main application
        Recorder.instance().restoreMainApplication()

        # get data from model
        datas = self.model.getData()

        # save snapshot (pixmap) to QByteArray via QBuffer.
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        snapshot.save(buffer, 'PNG')

        # convert to base64
        data64 = base64.b64encode(byte_array)
        if sys.version_info > (3,):
            datas[destRow]['value'] = str(data64, 'utf8')
        else:
            datas[destRow]['value'] = data64

        self.model.beginResetModel()
        self.model.endResetModel()
        self.setData()

    def importSnapshotImage(self, destRow):
        """
        Import snapshot image
        """
        # connect module
        Recorder.Gui.instance().onGlobalShortcutPressedFromParameters = self.onSnapshotImage
        
        # hide the app
        Recorder.instance().hideMainApplication()
        Recorder.Gui.instance().takeSnapshotFromParameters(destRow=destRow)
        
    def importEmbeddedFile(self):
        """
        Import external file from local disk
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Import file"), "", "Files (*.*)" )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if not len(_fileName):
            return None

        fileAny = QFile(_fileName)
        if not fileAny.open(QIODevice.ReadOnly):
            QMessageBox.warning(self, self.tr("Open local file failed"), self.tr("unable to read content") )
            return None
        else:
            fileData= fileAny.readAll()

        baseName = os.path.basename(_fileName)
        lenFile = len(fileData)
        
        if sys.version_info > (3,): # python 3 support
            return "%s:%s:%s" % ( baseName, lenFile, str(base64.b64encode(fileData), "utf8") )
        else:
            return "%s:%s:%s" % ( baseName, lenFile, base64.b64encode(fileData) )

    def importEmbeddedImage(self):
        """
        Import external image from local disk
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Import image"), "", "Images (*.%s)" % Workspace.Repositories.LocalRepository.EXTENSION_PNG )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if not len(_fileName):
            return None
        
        if not ( str(_fileName).endswith( Workspace.Repositories.LocalRepository.EXTENSION_PNG ) ):
            QMessageBox.warning(self, self.tr("Open local image failed") , self.tr("Image file not supported") )
            return None

        image = QImage(_fileName)
        if image.isNull():
            QMessageBox.warning(self, self.tr("Open local image failed") , self.tr("Image file not supported, unable to read") )
            return None

        fileImage = QFile(_fileName)
        if not fileImage.open(QIODevice.ReadOnly):
            QMessageBox.warning(self, self.tr("Open local image failed"), self.tr("Image file not supported, unable to read content") )
            return None
        else:
            imageData= fileImage.readAll()

        return base64.b64encode(imageData)

    def importImage(self):
        """
        Import image from local or remote repository
        Or from anywhere
        """
        editor = None

        # import from local repo
        localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
        if localConfigured != "Undefined":
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("Import image from local repository") , buttons)
            if answer == QMessageBox.Yes:
                editor = self.loadImageFromLocal() # load local image file
            else:
                if UCI.instance().isAuthenticated(): # no then perhaps in remo repo if connected?
                    editor = self.loadImageFromRemote() # load remote test config file
                else:
                    QMessageBox.warning(self, self.tr("Import") , self.tr("Connect to the test center first!") )
        
        # import from remote repo
        elif UCI.instance().isAuthenticated(): # no then perhaps in remo repo if connected?
            editor = self.loadImageFromRemote() # load remote dataset file

        else:
            QMessageBox.warning(self, self.tr("Import") , self.tr("Connect to the test center first!") )
        return editor

    def importDataset(self):
        """
        Import dataset from local or remote repository
        or from anywhere
        """
        editor = None

        # import from local repo
        localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
        if localConfigured != "Undefined":
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("Import dataset from local repository") , buttons)
            if answer == QMessageBox.Yes:
                editor = self.loadFromLocal() # load local dataset file
            else:
                if UCI.instance().isAuthenticated(): # no then perhaps in remo repo if connected?
                    editor = self.loadFromRemote() # load remote test config file
                else:
                    QMessageBox.warning(self, self.tr("Import") , self.tr("Connect to the test center first!") )
        
        # import from remote repo
        elif UCI.instance().isAuthenticated(): # no then perhaps in remo repo if connected?
            editor = self.loadFromRemote() # load remote dataset file

        else:
            QMessageBox.warning(self, self.tr("Import") , self.tr("Connect to the test center first!") )
        return editor

    def loadFromLocal(self):
        """
        Load from local repository
        """
        editor = Workspace.Repositories.LocalRepository.SaveOpenToRepoDialog( self , "", type = Workspace.Repositories.LocalRepository.MODE_OPEN,
                                                                                typeFile=[ Workspace.Repositories.LocalRepository.EXTENSION_TDX ]) 
        editor.hideFiles(hideTsx=True, hideTpx=True, hideTcx=True, hideTdx=False, hideTux=True, hidePng=True)
        if editor.exec_() == QDialog.Accepted:
            return editor.getSelection(withRepoName=True)
        else:
            return None

    def loadFromAnywhere(self):
        """
        Load from anywhere
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Import dataset"), "", "Tdx Data Files (*.%s)" % Workspace.Repositories.LocalRepository.EXTENSION_TDX )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if not len(_fileName):
            return None
        
        if not ( str(_fileName).endswith( Workspace.Repositories.LocalRepository.EXTENSION_TDX ) ):
            QMessageBox.critical(self, self.tr("Open Failed") , self.tr("File not supported") )
            return None

        return "undefined:/%s" %  _fileName

    def loadFromRemote(self):
        """
        Load from remote repository
        """
        project = Workspace.Repositories.instance().remote().getCurrentProject()
        Workspace.Repositories.instance().remote().saveAs.getFilename(type= Workspace.Repositories.RemoteRepository.EXTENSION_TDX, project=project)
        editor = Workspace.Repositories.instance().remote().saveAs
        if editor.exec_() == QDialog.Accepted:
            return editor.getSelection(withRepoName=True, withProject=True)
        else:
            return None

    def loadImageFromLocal(self):
        """
        Load image from local repository
        """
        editor = Workspace.Repositories.LocalRepository.SaveOpenToRepoDialog( self , "", type = Workspace.Repositories.LocalRepository.MODE_OPEN,
                                                                                typeFile=[ Workspace.Repositories.LocalRepository.EXTENSION_PNG ]) 
        editor.hideFiles(hideTsx=True, hideTpx=True, hideTcx=True, hideTdx=True, hideTux=True, hidePng=False)
        if editor.exec_() == QDialog.Accepted:
            return editor.getSelection(withRepoName=True)
        else:
            return None

    def loadImageFromAnywhere(self):
        """
        Load image from anywhere
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Import image"), "", "Images (*.%s)" % Workspace.Repositories.LocalRepository.EXTENSION_PNG )
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        if not len(_fileName):
            return None
        
        if not ( str(_fileName).endswith( Workspace.Repositories.LocalRepository.EXTENSION_PNG ) ):
            QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Image file not supported") )
            return None

        return "undefined:/%s" %  _fileName

    def loadImageFromRemote(self):
        """
        Load image from remote repository
        """
        project = Workspace.Repositories.instance().remote().getCurrentProject()
        Workspace.Repositories.instance().remote().saveAs.getFilename(type= Workspace.Repositories.RemoteRepository.EXTENSION_PNG, project=project)
        editor = Workspace.Repositories.instance().remote().saveAs
        if editor.exec_() == QDialog.Accepted:
            return editor.getSelection(withRepoName=True, withProject=True)
        else:
            return None

class ParametersQWidget(QWidget, Logger.ClassLogger):
    """
    Parameters widget
    """
    def __init__(self, parent, forParamsOutput=False, forTestConfig=False):
        """
        Contructs Parameters Widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.forParamsOutput = forParamsOutput
        self.forTestConfig = forTestConfig

        self.createWidgets()
        self.createToolbar()
        self.createConnections()

    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|------|||
        || Open | Save |||
        ||------|------|||
        """
        self.dockToolbarParams.setObjectName("Document Properties toolbar input")
        self.dockToolbarParams.addAction(self.table().addAction)
        self.dockToolbarParams.addAction(self.table().delAction)
        self.dockToolbarParams.addAction(self.table().clearAction)
        self.dockToolbarParams.addAction(self.table().openAction)
        self.dockToolbarParams.addSeparator()
        self.dockToolbarParams.addAction(self.table().copyAction)
        self.dockToolbarParams.addAction(self.table().pasteAction)
        self.dockToolbarParams.addAction(self.table().undoAction)
        self.dockToolbarParams.addSeparator()
        self.dockToolbarParams.addAction(self.table().colorsAction)
        self.dockToolbarParams.addSeparator()
        self.dockToolbarParams.setIconSize(QSize(16, 16))
        
    def toolbar(self):
        """
        return toolbar instance
        """
        return self.dockToolbarParams
        
    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()

        self.dockToolbarParams = QToolBar(self)
        self.dockToolbarParams.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border

        self.parametersTable = ParametersTableView(self, forParamsOutput=self.forParamsOutput, forTestConfig=self.forTestConfig)
        self.parametersTable.setColumnHidden(COL_DESCRIPTION, 
                                    QtHelper.str2bool(Settings.instance().readValue( key = 'TestProperties/parameters-hide-description' ))
                                )
        
        self.filterText = QLineEdit(self)
        self.filterText.setToolTip(self.tr("Name filter"))
        self.filterText.setPlaceholderText("Search in parameters")
        
        layout.addWidget(self.parametersTable)
        layout.addWidget(self.filterText)
        layout.addWidget(self.dockToolbarParams)
        
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def createConnections(self):
        """
        Create qt connections
        """
        self.filterText.textChanged.connect(self.filterRegExpChanged)

    def clear(self):
        """
        Clear all widget
        """
        self.parametersTable.clear()
        self.filterText.setText("")

    def table(self):
        """
        Return the parameter table view
        """
        return self.parametersTable

    def usedAsAlias(self, paramName):
        """
        Used as alias
        """
        isAlias = False
        for param in self.table().model.getData():
            if param['type'] == 'alias':
                if param['value'] == paramName:
                    isAlias = True
                    break
        return isAlias
        
    def markUnusedInputs(self, editorSrc, editorExec):
        """
        Mark unused inputs
        """
        for param in self.table().model.getData():
            match = False
            if "color" not in param: param["color"] = ""
            if editorSrc is not None:
                if "input('%s')" % param['name'] in editorSrc.text():
                    match = True
                if 'input("%s")' % param['name'] in editorSrc.text():
                    match = True
                if 'input("""%s""")' % param['name'] in editorSrc.text():
                    match = True
            if editorExec is not None:
                if "input('%s')" % param['name'] in editorExec.text():
                    match = True
                if 'input("%s")' % param['name'] in editorExec.text():
                    match = True
                if 'input("""%s""")' % param['name'] in editorExec.text():
                    match = True
            
            # checking if the param is not used as alias ?
            if not match:
                match = self.usedAsAlias(paramName=param['name'])
            
            if not match:    
                param['color'] = "#000000"
            else:
                if param['color'] == "#000000" :
                    param['color'] = ""
                
        self.table().model.beginResetModel()
        self.table().model.endResetModel()

    def markUnusedOutputs(self, editorSrc, editorExec):
        """
        Mark unused outputs
        """
        for param in self.table().model.getData():
            match = False
            if "color" not in param: param["color"] = ""
            if editorSrc is not None:
                if "output('%s')" % param['name'] in editorSrc.text():
                    match = True
                if 'output("%s")' % param['name'] in editorSrc.text():
                    match = True
                if 'output("""%s""")' % param['name'] in editorSrc.text():
                    match = True
            if editorExec is not None:
                if "output('%s')" % param['name'] in editorExec.text():
                    match = True
                if 'output("%s")' % param['name'] in editorExec.text():
                    match = True
                if 'output("""%s""")' % param['name'] in editorExec.text():
                    match = True
                    
            # checking if the param is not used as alias ?
            if not match:
                match = self.usedAsAlias(paramName=param['name'])
                
            if not match:    
                param['color'] = "#000000"
            else:
                if param['color'] == "#000000" :
                    param['color'] = ""
                    
        self.table().model.beginResetModel()
        self.table().model.endResetModel()

    def filterRegExpChanged(self):
        """
        On filter regexp changed
        """
        syntax = QRegExp.RegExp
        caseSensitivity = Qt.CaseInsensitive
        regExp = QRegExp(self.filterText.text(),  caseSensitivity, syntax)

        self.parametersTable.proxyModel.setFilterKeyColumn( COL_NAME )
        self.parametersTable.proxyModel.setFilterRegExp(regExp)

        self.parametersTable.adjustColumns()
        self.parametersTable.adjustRows()