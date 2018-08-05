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
Test description module
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QFont, QItemDelegate, QDialog, QComboBox, QLineEdit, QAbstractItemDelegate, 
                            QVBoxLayout, QHBoxLayout, QDialogButtonBox, QIcon, QToolBar, QTextEdit, 
                            QMessageBox, QTableView, QAbstractItemView, QFrame, QMenu, QDrag, QWidget)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, QSize, 
                            pyqtSignal, QMimeData, QByteArray)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon, QDrag)
    from PyQt5.QtWidgets import (QItemDelegate, QDialog, QComboBox, QLineEdit, 
                                QAbstractItemDelegate, QVBoxLayout, QHBoxLayout, QDialogButtonBox, 
                                QToolBar, QTextEdit, QMessageBox, QTableView, QAbstractItemView, 
                                QFrame, QMenu, QWidget)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, QSize, 
                            pyqtSignal, QMimeData, QByteArray)
 
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
import RestClientInterface as RCI

import Workspace

import operator
import base64
import time
import copy

COL_KEY             =   0
COL_VALUE           =   1

ROW_AUTHOR          =   0
ROW_DATE            =   1
ROW_SUMMARY         =   2
ROW_PREREQUISITES   =   3
ROW_COMMENTS        =   4
ROW_LIBRARIES       =   5
ROW_ADAPTERS        =   6
ROW_STATE           =   7

try:
    xrange
except NameError: # support python3
    xrange = range
    
class DescriptionsTableModel(QAbstractTableModel, Logger.ClassLogger):
    """
    Descriptions table model
    """
    def __init__(self, parent):
        """
        Table model for probes

        @param parent: 
        @type parent:
        """
        QAbstractTableModel.__init__(self, parent)
        self.owner = parent
        self.nbCol = 2
        self._data = []
        self.wdoc = None

    def setWdoc(self, wdoc):
        """
        Set the widget document
        """
        self.wdoc = wdoc

    def getWdocData(self):
        """
        Return the datamodel of the widget document
        """
        return self.wdoc.dataModel

    def getWdoc(self):
        """
        Return the widget document
        """
        return self.wdoc

    def getData(self):
        """
        Return model data

        @return:
        @rtype:
        """
        return self._data

    def getValueRow(self, index):
        """
        Return all current values of the row

        @param index: 
        @type index:

        @return:
        @rtype:
        """
        return self._data[ index.row() ]

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
        if index.column() == COL_KEY:
            return self._data[ index.row() ]['key'].title()
        elif index.column() == COL_VALUE:
            return self._data[ index.row() ]['value']
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
        if role == Qt.FontRole:
            if index.column() == COL_KEY:
                font = QFont()
                font.setBold(True)
                return q(font)
            if index.column() == COL_VALUE:
                font = QFont()
                font.setItalic(True)
                return q(font)
                
        elif role == Qt.DisplayRole:
            if index.row() == ROW_COMMENTS:
                if index.column() == COL_VALUE:
                    ret = ''

                    if isinstance(value, str) or isinstance(value, unicode) or  isinstance(value, bytes): # change to support py3
                        value =  { 'comments': {'comment': []} }

                    if isinstance(value['comments'], str) or isinstance(value['comments'], bytes): # change to support py3
                        value['comments'] =  {'comment': []}
                    if isinstance( value['comments']['comment'], dict):
                        nbcomments = 1
                    else:
                        nbcomments = len(value['comments']['comment'])
                    ret = '- %s -' % nbcomments
                    return q(ret)
                else:
                    return q(value)
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
            headers = ( 'Key', 'Value' )
            return headers[section]

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
        
        if index.column() == COL_KEY:
            orig_ = self._data[ index.row() ]['key']
            self._data[ index.row() ]['key'] = value
            if orig_ != value:
                dataChanged = True
        elif index.column() == COL_VALUE:
            orig_ = self._data[ index.row() ]['value']
            self._data[ index.row() ]['value'] = value
            if orig_ != value:
                dataChanged = True
                self.owner.setData(signal=False)

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
        if index.row() == ROW_COMMENTS:
            self.setValue(index, value )
        else:
            value = QtHelper.displayToValue( value )
            self.setValue(index, value )        
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
        if index.column() == COL_VALUE:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsDragEnabled)

####################################################        
################# Delegate items ###################
####################################################    
class ValueDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Value delegate
    """
    def __init__ (self, parent, col_ ):
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
        Return value by row

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

        @return:
        @rtype:
        """
        value = self.getValueRow(index)
        if index.column() == self.col_:
            if value['key'] == 'summary' or value['key'] == 'prerequisites':
                editorDialog = DescriptionDialog(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    testDescr = editorDialog.getDescr()
                    index.model().setData(index,q(testDescr))
                return None
            if value['key'] == 'comments':
                editorDialog = CommentsDialog(value['value'])
                if editorDialog.exec_() == QDialog.Accepted:
                    comments = editorDialog.getComments()
                    index.model().setData(index,comments)
                return None
            elif value['key'] == 'date': # deprecated
                return None
            elif value['key'] == 'creation date':
                return None
            elif value['key'] == 'data mode':
                wdoc = index.model().getWdoc()
                if wdoc.extension != Workspace.TestData.TYPE:
                    return None
                editorDialog = DataModeDialog()
                if editorDialog.exec_() == QDialog.Accepted:
                    dataMode = editorDialog.getSelectedMode()
                    # update lexer on editor
                    if dataMode == 'Raw':
                        wdoc.deactiveXmlLexer()
                    else:
                        wdoc.activeXmlLexer()
                    # update table
                    index.model().setData(index,dataMode)
                return None
            elif value['key'] == 'libraries':
                serverSutLibs = Settings.instance().serverContext['libraries']
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                editor.addItems ( serverSutLibs.split(',')  )
                return editor
            elif value['key'] == 'adapters':
                serverSutAdps = Settings.instance().serverContext['adapters']
                editor = QComboBox(parent)
                editor.activated.connect(self.onItemActivated)
                editor.addItems ( serverSutAdps.split(',') )
                return editor
            elif value['key'] == 'state':
                wdoc = index.model().getWdoc()
                
                if wdoc is None:
                    return
                    
                if not wdoc.isSaved():
                    return

                isTp = False
                isTs = False
                isTu = False
                isTg = False
                isTa = False
                if wdoc.extension == Workspace.TestUnit.TYPE:
                    isTu=True
                if wdoc.extension == Workspace.TestAbstract.TYPE:
                    isTa=True
                if wdoc.extension == Workspace.TestSuite.TYPE:
                    isTs=True
                if wdoc.extension == Workspace.TestPlan.TYPE:
                    isTp=True
                if wdoc.extension == Workspace.TestPlan.TYPE_GLOBAL:
                    isTg=True
                editorDialog = StateDialog()
                if editorDialog.exec_() == QDialog.Accepted:
                    stateTest = editorDialog.getSelectedState()
                    if value['value'] != stateTest:
                        # uci call
                        if stateTest == 'Executing':
                            duration = time.time() - float(wdoc.dataModel.testdev)
                          
                            # rest call
                            RCI.instance().durationTestsWritingMetrics( duration=int(duration), 
                                                                        projectId=wdoc.project, 
                                                                        isTp=isTp, 
                                                                        isTs=isTs, 
                                                                        isTu=isTu, 
                                                                        isTg=isTg, 
                                                                        isTa=isTa)
                            
                        # update data model
                        if stateTest == 'Writing':
                            wdoc.dataModel.testdev=time.time()
                        # update table
                        index.model().setData(index,stateTest)
                return None
            else:
                editor = editor = QLineEdit(parent)
                return editor
        return QItemDelegate.createEditor(self, parent, option, index)

    def setModelData(self, editor, model, index):
        """
        Set datamodel

        @param editor: 
        @type editor:

        @param model: 
        @type model:

        @param index: 
        @type index:
        """
        if type(editor) == QComboBox:
            qvalue = editor.currentText()
        else:
            qvalue = editor.text()
        value = QtHelper.displayToValue( q(qvalue) )
        self.setValue(index, value)
        
    def onItemActivated(self, index): 
        """
        Close editor on index changed
        """
        self.commitData.emit(self.sender())
        self.closeEditor.emit(self.sender(), QAbstractItemDelegate.NoHint)
        
####################################################        
##################### Dialogs ######################
####################################################
class DataModeDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    State dialog
    """
    def __init__(self, parent=None):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(DataModeDialog, self).__init__(parent)
        # make a copy
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        mainLayout = QVBoxLayout()
        
        self.comboType = QComboBox()
        self.comboType.addItem("Raw")
        self.comboType.addItem("Xml")

        typeLayout = QHBoxLayout()
        typeLayout.addWidget( self.comboType )

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

        mainLayout.addLayout(typeLayout)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle("Test Description > Data Mode")
        self.setFixedWidth(350)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)

    def getSelectedMode(self):
        """
        Returns selected state
        """
        return q(self.comboType.currentText()) 

class StateDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    State dialog
    """
    def __init__(self, parent=None):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(StateDialog, self).__init__(parent)
        # make a copy
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        mainLayout = QVBoxLayout()
        
        self.comboType = QComboBox()
        self.comboType.addItem("Writing")
        self.comboType.addItem("Executing")

        typeLayout = QHBoxLayout()
        typeLayout.addWidget( self.comboType )

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

        mainLayout.addLayout(typeLayout)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle("Test Description > State")
        self.setFixedWidth(350)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)

    def getSelectedState(self):
        """
        Returns selected state
        """
        return q(self.comboType.currentText()) 

class CommentsDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Comments dialog
    """
    def __init__(self, dataComments, parent=None):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(CommentsDialog, self).__init__(parent)

        # dataComments has been reseted, reconstruct the right form
        if isinstance(dataComments, str) or isinstance(dataComments, unicode):
            dataComments = {'comments': {'comment': []}}
        # make a copy
        self.dataComments = copy.deepcopy(dataComments) 
        if isinstance(self.dataComments['comments'], str):
            self.comments = self.dataComments['comments']
            self.comments = []
        else:
            self.comments = self.dataComments['comments']['comment']
        self.createDialog()
        self.createActions()
        self.createToolbar()
        self.createConnections()
        self.loadComments()

    def createActions (self):
        """
        Create qt actions
        """     
        self.addCommentAction = QtHelper.createAction(self, "&Add", self.addComment, 
                                                    tip = 'Add comment', icon = QIcon(":/add_post.png") )
        self.clearAction = QtHelper.createAction(self, "&Clear", self.clearText, 
                                                    tip = 'Clear fields', icon = QIcon(":/clear.png") )
        self.delCommentsAction = QtHelper.createAction(self, "&Delete all", self.delComments,   
                                                    tip = 'Delete all comments', icon = QIcon(":/del-posts.png") )
        self.setDefaultActionsValues()

    def setDefaultActionsValues (self):
        """
        Set default values for qt actions
        """
        self.addCommentAction.setEnabled(False)
        self.delCommentsAction.setEnabled(True)
        self.clearAction.setEnabled(False)


    def createDialog (self):
        """
        Create qt dialog
        """
        mainLayout = QVBoxLayout()

        self.dockToolbarComments = QToolBar(self)

        self.commentTextarea = QTextEdit()
        self.commentTextarea.setFixedHeight(150)

        self.commentsTextarea = QTextEdit()
        self.commentsTextarea.setReadOnly(True)
        self.commentsTextarea.setStyleSheet ( """background-color: #EAEAEA; """ )

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/test-close-black.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout.addWidget(self.dockToolbarComments)
        mainLayout.addWidget(self.commentTextarea)
        mainLayout.addWidget( self.commentsTextarea)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle("Test Description > Comments")
        self.setFixedWidth(450)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.commentTextarea.textChanged.connect(self.onTextChanged)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def createToolbar(self):
        """
        Toolbar creation
            
        ||-------||
        || Empty ||
        ||-------||
        """
        self.dockToolbarComments.setObjectName("Archives comments toolbar")
        self.dockToolbarComments.addAction(self.delCommentsAction)
        self.dockToolbarComments.addSeparator()
        self.dockToolbarComments.addAction(self.addCommentAction)       
        self.dockToolbarComments.addAction(self.clearAction)
        self.dockToolbarComments.addSeparator()
        self.dockToolbarComments.setIconSize(QSize(16, 16))

    def onTextChanged(self):
        """
        On text changed
        """
        newPost = self.commentTextarea.toPlainText()
        if len(newPost):
            self.addCommentAction.setEnabled(True)
            self.clearAction.setEnabled(True)
        else:
            self.addCommentAction.setEnabled(False)
            self.clearAction.setEnabled(False)

    def loadComments(self):
        """
        Load all comments
        """     
        commentsParsed = []

        # When there is just one comment, the container is not a list but a dict
        if isinstance( self.comments, dict):
            self.comments = [ self.comments ]
        
        for tPost in self.comments:
            dt = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( float(tPost['datetime'])) )  + \
                    ".%3.3d" % int(( float(tPost['datetime']) * 1000) % 1000 )
            post_decoded = base64.b64decode(tPost['post'])
            post_decoded = post_decoded.decode('utf8').replace('\n', '<br />')
            commentsParsed.append( 'By <b>%s</b>, %s<p style="margin-left:20px">%s</p>' % (tPost['author'], dt, post_decoded) )
        commentsParsed.reverse()
        self.commentsTextarea.setHtml( "<br />".join(commentsParsed)   )


    def delComments(self):
        """
        Delete all comments
        """
        reply = QMessageBox.question(self, "Delete all comments", "Are you really sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            self.comments = []
            self.loadComments()

    def addComment(self):
        """
        Add comment
        """
        tPost = self.commentTextarea.toPlainText()
        if sys.version_info > (3,): # python 3 support
            postEncoded = base64.b64encode(bytes(tPost, 'utf8'))
            postEncoded = str(postEncoded, 'utf8')
        else:
            postEncoded = base64.b64encode(tPost.toUtf8())
        self.comments.append( {'author': UCI.instance().getLogin() , 
                               'datetime': str(time.time()), 'post': postEncoded } )
        self.clearText()
        self.loadComments()


    def clearText(self):
        """
        Clear the comment text area
        """
        self.commentTextarea.setText('')

    def getComments(self):
        """
        Returns all comments
        """
        tpl = {}
        tpl['comments'] = {}
        tpl['comments']['comment'] = self.comments
        return tpl

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
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok )

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.descrEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Test Description > Value")
        self.resize(350, 250)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)

    def getDescr(self):
        """
        Returns description
        """
        return self.descrEdit.toPlainText()

####################################################        
##############   main table view   #################
####################################################
class DescriptionsTableView(QTableView, Logger.ClassLogger):
    """
    Descriptions table view
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
        self.datasetView = False

        self.createWidgets()
        self.createConnections()
        self.createActions()

    def createWidgets (self):
        """
        Create qt widgets
        """
        self.model = DescriptionsTableModel(self)
        self.setModel(self.model)
        
        colValue = 1
        self.setItemDelegateForColumn( colValue, ValueDelegate(self, colValue) )

        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)

        self.setShowGrid(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color: #D4F1FD;")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setVisible(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        self.horizontalHeader().setStretchLastSection(True)
        self.adjustRows()

    def createConnections (self):
        """
        Create qt connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)

    def createActions (self):
        """
        Create qt actions
        """
        self.clearAction = QtHelper.createAction(self, "Clear all parameters", self.clearItems,
                    icon = QIcon(":/test-parameter-clear.png"),  tip = 'Clear all parameters' )
        self.setDefaultsAction = QtHelper.createAction(self, "Set default adapters and libraries", self.setDefaults, 
                    icon = QIcon(":/refresh-test.png"),  tip = 'Set default adapters and libraries' )
        self.writingAction = QtHelper.createAction(self, "Set writing state", self.stateWritingTest, 
                    icon = QIcon(":/writing-state.png"),  tip = 'Set writing state')
        self.executingAction = QtHelper.createAction(self, "Set executing state", self.stateExecutingTest, 
                    icon = QIcon(":/state_right.png"),  tip = 'Set executing state')
        self.defaultActions()

    def defaultActions(self):
        """
        Set default actions
        """
        self.clearAction.setEnabled(True)
        self.setDefaultsAction.setEnabled(True)
        self.writingAction.setChecked(False)
        self.executingAction.setChecked(False)

    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu(self)
        self.menu.addAction( self.clearAction )
        self.menu.addAction( self.setDefaultsAction )
        self.menu.addSeparator()
        self.menu.addAction( self.writingAction )
        self.menu.addAction( self.executingAction )
        self.menu.popup( self.mapToGlobal(pos) )

    def setDefaults(self):
        """
        Set default values for adapters and libraries version
        """
        defaultSutAdp = Settings.instance().serverContext['default-adapter']
        defaultSutLib = Settings.instance().serverContext['default-library']
        data = self.model.getData()
        for kv in data:
            if kv['key'] == 'adapters':
                kv['value'] = defaultSutAdp
            if kv['key'] == 'libraries':
                kv['value'] = defaultSutLib
        self.setData()

    def stateExecutingTest(self):
        """
        Set the executing state for the current test
        """
        wdoc = self.model.getWdoc()
        if wdoc is None:
            return
            
        if not wdoc.isSaved():
            return
            
        isTp = False
        isTs = False
        isTu = False
        isTg = False
        if wdoc.extension == Workspace.TestUnit.TYPE:
            isTu=True
        if wdoc.extension == Workspace.TestSuite.TYPE:
            isTs=True
        if wdoc.extension == Workspace.TestPlan.TYPE:
            isTp=True
        if wdoc.extension == Workspace.TestPlan.TYPE_GLOBAL:
            isTg=True
        duration = time.time() - float(wdoc.dataModel.testdev)

        data = self.model.getData()
        for kv in data:
            if kv['key'] == 'state':
                kv['value'] = 'Executing'
                self.setData()
                break

        # call web service
        RCI.instance().durationTestsWritingMetrics( duration=int(duration), 
                                                    projectId=wdoc.project, 
                                                    isTp=isTp, 
                                                    isTs=isTs, 
                                                    isTu=isTu, 
                                                    isTg=isTg, 
                                                    isTa=isTa)
                                                                        
    def stateWritingTest(self):
        """
        Set the writing state for the current test
        """
        wdoc = self.model.getWdoc()
        if wdoc is None:
            return

        wdoc.dataModel.testdev=time.time()
        data = self.model.getData()
        for kv in data:
            if kv['key'] == 'state':
                kv['value'] = 'Writing'
                self.setData()
                break

    def startDrag(self, dropAction):
        """
        Start drag

        @param dropAction:
        @type dropAction:
        """
        if self.datasetView:
            return
            
        # check indexes
        indexes = self.selectedIndexes()
        if not indexes:
            return
        for index in indexes:
            if not index.isValid():
                return
                
        rowVal = self.model.getValueRow( indexes[0] )
        if len(rowVal) > 1 :
            meta = QByteArray()
            meta.append( "description('%s')" % rowVal['key'] )
            
            # create mime data object
            mime = QMimeData()
            m = 'application/x-%s-description-item' % Settings.instance().readValue( key='Common/acronym' ).lower() 
            mime.setData( m, meta )
            # start drag 
            drag = QDrag(self)
            drag.setMimeData(mime)
            
            drag.exec_(Qt.CopyAction)


    def clearItems(self):
        """
        Clear all items except creation date
        """
        reply = QMessageBox.question(self, "Clear all values", "Are you sure ?",
                        QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            data = self.model.getData()
            try:
                for i in xrange(len(data)):
                    if data[i]['key'] != 'creation date':
                        data[i]['value'] = ''
            except Exception as e:
                self.error( 'unable to clear all values on description: %s' % str(e) )

            self.model.beginResetModel()
            self.model.endResetModel()
            self.setData()

    def clear (self):
        """
        Clears contents
        """
        #self.wdocData = None
        self.model.setWdoc( None )
        self.model.setDataModel( [] )
        self.adjustColumns()
        self.adjustRows()

    def adjustColumns(self):
        """
        Resize three first columns to contents
        """
        for col in [0, 1]:
            self.resizeColumnToContents(col)
    
    def adjustRows (self):
        """
        Adjust rows
        """
        data = self.model.getData()
        for row in xrange(len(data)):
            self.resizeRowToContents(row)

    def setWdoc(self, wdoc):
        """
        Set the model with the widget document passed as argument
        """
        self.model.setWdoc( wdoc )

    def loadData (self, data):
        """
        Load the model with data passed as argument

        @param data: 
        @type data:
        """
        descrs = data['description']
        self.model.setDataModel( descrs )
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

    def setDefaultView(self):
        """
        Set the default view
        """
        self.datasetView = False

    def setDatasetView(self):
        """
        Set the dataset view
        """
        self.datasetView = True

class DescriptionsQWidget(QWidget, Logger.ClassLogger):
    """
    Description widget
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
        self.dockToolbar.setObjectName("Document Properties toolbar description")
        self.dockToolbar.addAction(self.table().clearAction)
        self.dockToolbar.addAction(self.table().setDefaultsAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.table().writingAction)
        self.dockToolbar.addAction(self.table().executingAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()

        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px; }") # remove 3D border

        self.descrsTable = DescriptionsTableView(self)

        
        layout.addWidget(self.descrsTable)
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
        self.descrsTable.clear()

    def table(self):
        """
        Return the probes table view
        """
        return self.descrsTable