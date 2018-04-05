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
Test plan module
"""
# import standard modules
import sys
import copy
import os
import json

try:
    import pickle as pickle
except ImportError: # support python 3
    import cPickle as pickle
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QStyledItemDelegate, QTreeView, QMessageBox, QToolBar,QVBoxLayout, 
                            QTreeWidget, QAbstractItemView, QFrame, QLabel, QFont, QIcon, QMenu, 
                            QInputDialog, QLineEdit, QTreeWidgetItem, QApplication, QDialog, 
                            QFileDialog, QClipboard, QGroupBox, QHBoxLayout, QColor, QDialogButtonBox,
                            QBrush)
    from PyQt4.QtCore import (Qt, QSize, QRect, QMimeData, QByteArray, pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QFont, QIcon, QClipboard, QColor, QBrush)
    from PyQt5.QtWidgets import (QStyledItemDelegate, QTreeView, QMessageBox, QToolBar, QDialogButtonBox,
                                QVBoxLayout, QTreeWidget, QAbstractItemView, QFrame, QLabel, 
                                QMenu, QInputDialog, QLineEdit, QTreeWidgetItem, QApplication, 
                                QDialog, QFileDialog, QGroupBox, QHBoxLayout)
    from PyQt5.QtCore import (Qt, QSize, QRect, QMimeData, QByteArray, pyqtSignal)
    
from Libs import QtHelper, Logger

try:
    import Document
except ImportError: # python3 support
    from . import Document


import UserClientInterface as UCI
import RestClientInterface as RCI
import Settings


try:
    import FileModels.TestPlan as FileModelTestPlan
    import FileModels.TestSuite as FileModelTestSuite
    import FileModels.TestUnit as FileModelTestUnit
    import FileModels.TestAbstract as FileModelTestAbstract
except ImportError: # python3 support
    from .FileModels import TestPlan as FileModelTestPlan
    from .FileModels import TestSuite as FileModelTestSuite
    from .FileModels import TestUnit as FileModelTestUnit
    from .FileModels import TestAbstract as FileModelTestAbstract


try:    
    import TestSuite
    import TestUnit
    import TestAbstract
except ImportError: # python3 support
    from . import TestSuite
    from . import TestUnit
    from . import TestAbstract
    
TYPE                    = 'tpx'
TYPE_GLOBAL             = 'tgx'

FROM_OTHER              = 'other'
FROM_LOCAL_REPO         = 'local'
FROM_REMOTE_REPO        = 'remote'

# old type deprecated
FROM_HDD                = 'hdd'
FROM_LOCAL_REPO_OLD     = 'local repository'

TS_ENABLED              = "2"
TS_DISABLED             = "0"


COL_NAME                = 0
COL_CONTROL             = 1
COL_ID                  = 2
COL_TAG_COLOR           = 3
COL_CONDITION_BEGIN     = 4
COL_ACTION              = 5
COL_RESULT              = 6
COL_CONDITION_END       = 7
COL_ENABLE              = 8
COL_REPO                = 9
COL_ALIAS               = 10
COL_DESCR               = 11

ITEM_TEST               = 0

# Define the Qt.ItemDataRole we will be using 
MyBorderRole = Qt.UserRole + 1

class UpdateLocationsDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Update locations dialog
    """
    def __init__(self, parent=None):
        """
        Dialog to rename file or folder

        @param currentName: 
        @type currentName: 

        @param folder: 
        @type folder:

        @param parent: 
        @type parent: 
        """
        super(UpdateLocationsDialog, self).__init__(parent)

        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.currentLabel = QLabel(self.tr("Path to replace:") )
        self.currentEdit = QLineEdit(self)
        self.currentEdit.setStyleSheet("QLineEdit { background-color : #F0F0F0; }");

        self.newLabel = QLabel(self.tr("New path:") )
        self.newnameEdit = QLineEdit(self)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.currentLabel)
        mainLayout.addWidget(self.currentEdit)
        mainLayout.addWidget(self.newLabel)
        mainLayout.addWidget(self.newnameEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Update locations"))
        
        self.resize(300, 100)

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.acceptLocations)
        self.buttonBox.rejected.connect(self.reject)

    def acceptLocations(self):
        """
        Called on accept
        """
        currentLocation = self.currentEdit.text()
        if not len(currentLocation):
            QMessageBox.warning(self, self.tr("Update locations") , 
                                self.tr("Path to replace cannot be empty!") )
            return
            
        newLocation = self.newnameEdit.text()
        if not len(newLocation):
            QMessageBox.warning(self, self.tr("Update locations") , 
                                self.tr("New path cannot be empty!") )
            return
            
        self.accept()

    def getNewLocations(self):
        """
        Returns the new name
        """
        oldloc = self.currentEdit.text()
        newloc = self.newnameEdit.text()
        return (oldloc, newloc)
        
class BorderItemDelegate(QStyledItemDelegate):
    """
    Border item delegate
    """
    def __init__(self, parent, borderRole):
        """
        Constructor
        """
        super(BorderItemDelegate, self).__init__(parent)
        self.borderRole = borderRole

    def sizeHint(self, option, index):  
        """
        Size hint
        """
        size = super(BorderItemDelegate, self).sizeHint(option, index)
        pen = index.data(self.borderRole).toPyObject()
        if pen is not None:        
            # Make some room for the border
            # When width is 0, it is a cosmetic pen which
            # will be 1 pixel anyways, so set it to 1
            width = max(pen.width(), 1)            
            size = size + QSize(2 * width, 2 * width)
        return size

    def paint(self, painter, option, index):
        """
        Paint
        """
        pen = index.data(self.borderRole).toPyObject()
        # copy the rect for later...
        rect = QRect(option.rect)
        if pen is not None:
            width = max(pen.width(), 1)
            # ...and remove the extra room we added in sizeHint...
            option.rect.adjust(width, width, -width, -width)      

        # ...before painting with the base class method...
        super(BorderItemDelegate, self).paint(painter, option, index)

        # ...then paint the borders
        if pen is not None:
            painter.save()  
            # The pen is drawn centered on the rectangle lines 
            # with pen.width()/2 width on each side of these lines.
            # So, rather than shifting the drawing of pen.width()/2
            # we double the pen width and clip the part that would 
            # go outside the rect.
            painter.setClipRect(rect, Qt.ReplaceClip);          
            pen.setWidth(2 * width)
            painter.setPen(pen)
            painter.drawRect(rect)     
            painter.restore()

class PrintTreeView(QTreeView):
    def __init__(self):
        """
        Printer accessor for treeview
        """
        super(PrintTreeView, self).__init__()
    
    def print_(self, printer):
        """
        Internal print function
        """
        # remove scrollbar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # expand all branches
        self.expandAll()
        
        # resize all columns
        for i in xrange(COL_DESCR):
            self.resizeColumnToContents(i)

        # move the second column (id) on the first
        self.header().moveSection(0, COL_CONTROL)        
        # move the second column (id) on the first
        self.header().moveSection(1, COL_ID)
        # move the third column (cond) on the second
        self.header().moveSection(2, COL_TAG_COLOR)
        # move the third column (cond) on the second
        self.header().moveSection(3, COL_CONDITION_BEGIN)
        # move the sixty column (action) on the third
        self.header().moveSection(4, COL_ACTION)
        
        # hide elements not needed
        self.setFrameStyle(0)
        self.header().hide()
        self.hideColumn(COL_ID)
        self.hideColumn(COL_TAG_COLOR)
        self.hideColumn(COL_ENABLE)
        self.hideColumn(COL_REPO)
        self.hideColumn(COL_ALIAS)
        
        # final resize according to the printer
        self.resize(printer.width(), printer.height())
        self.render(printer)

class AliasDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Alias dialog
    """
    def __init__(self, alias, parent=None):
        """
        Dialog to rename file or folder

        @param currentName: 
        @type currentName: 

        @param folder: 
        @type folder:

        @param parent: 
        @type parent: 
        """
        super(AliasDialog, self).__init__(parent)
        self.alias = alias

        self.createDialog()
        self.createConnections()

        self.currentAlias.setFocus()
        self.currentAlias.selectAll()


    def createDialog (self):
        """
        Create qt dialog
        """
        self.currentLabel = QLabel(self.tr("New test name:") )
        self.currentAlias = QLineEdit(self)
        self.currentAlias.setText(self.alias)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.currentLabel)
        mainLayout.addWidget(self.currentAlias)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Update test alias"))
        
        self.resize(600, 100)

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getAlias(self):
        """
        Returns the new name
        """
        try:
            alias = self.currentAlias.text()
            
            # workaround to detect special characters, same limitation as with python2 because of the server
            # this limitation will be removed when the server side will be ported to python3
            if sys.version_info > (3,): # python3 support only 
                alias.encode("ascii") 
                        
            return alias
        except UnicodeEncodeError as e:
            QMessageBox.critical(self, self.tr("Alias") , self.tr("Invalid alias.") )
            return ""

      
class QTreeWidgetEnhancement(QTreeWidget):
    InsertTest = pyqtSignal(dict, object) 
    def __init__(self, document):
        """
        """
        super(QTreeWidgetEnhancement, self).__init__()
        self.document = document
        
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """
        Drag enter event
        """
        if event.mimeData().hasFormat('application/x-%s-repo-openfile' % Settings.instance().readValue( key = 'Common/acronym' ).lower() ):
            event.accept()
        else:
            QTreeWidget.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        """
        Drag move event
        """
        if event.mimeData().hasFormat("application/x-%s-repo-openfile" % Settings.instance().readValue( key = 'Common/acronym' ).lower()):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            QTreeWidget.dragMoveEvent(self, event)
            
    def dropEvent(self, event):
        """
        Drop event
        """
        if (event.mimeData().hasFormat('application/x-%s-repo-openfile' % Settings.instance().readValue( key = 'Common/acronym' ).lower() )):

            data = pickle.loads( event.mimeData().data("application/x-%s-repo-openfile" % Settings.instance().readValue( key = 'Common/acronym' ).lower() ) )
            if self.document.testGlobal:
                if data["ext"] not in [ RCI.EXT_TESTUNIT, RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT, RCI.EXT_TESTPLAN ]:
                    QTreeWidget.dropEvent(self, event)
                    return
            else:
                if data["ext"] not in [ RCI.EXT_TESTUNIT, RCI.EXT_TESTSUITE, RCI.EXT_TESTABSTRACT ]:
                    QTreeWidget.dropEvent(self, event)
                    return

            event.acceptProposedAction()
            
            position = event.pos() 
            parentItem = self.itemAt(position)

            self.InsertTest.emit(data, parentItem)
        else:
            QTreeWidget.dropEvent(self, event) 
            
class WTestPlan(Document.WDocument):
    """
    Test plan widget
    """
    CONDITION_IF            = "IF"
    CONDITION_OK            = ") IS PASSED"
    CONDITION_KO            = ") IS FAILED"
    CONDITION_PARENTHESE    = ")"
    CONDITION_IS            = "IS"
    CONDITION_RUN           = "RUN ("
    CONDITION_THEN          = "THEN"
    CONDITION_DO            = "DO"
    CONDITION_DONT          = "DONT"
    def __init__(self, parent = None, path = None, filename = None, 
                    extension = None, nonameId = None, 
                    remoteFile=False, repoDest=None, project=0, iRepo=None, 
                    testGlobal=False, lRepo=None, isLocked=False):
        """
        Widget test plan

        @param parent:
        @type parent:

        @param path:
        @type path:

        @param filename:
        @type filename:

        @param extension:
        @type extension:

        @param nonameId:
        @type nonameId:
        """
        Document.WDocument.__init__(self, parent, path, filename, extension, 
                                    nonameId, remoteFile, repoDest, project, isLocked)
        
        self.loaderDialog = QtHelper.MessageBoxDialog(dialogName = self.tr("Loading"))
        
        self.iRepo = iRepo
        self.lRepo = lRepo
        
        userName = Settings.instance().readValue( key = 'Server/last-username' )
        if not 'default-library' in Settings.instance().serverContext:
            if not Settings.instance().offlineMode:
                QMessageBox.critical(self, self.tr("Open") , 
                    self.tr("Server context incomplete (default library is missing), please to reconnect!") )
            defLibrary = 'v000'
        else:
            defLibrary = Settings.instance().serverContext['default-library']
        if not 'default-adapter' in Settings.instance().serverContext:
            if not Settings.instance().offlineMode:
                QMessageBox.critical(self, self.tr("Open") , 
                    self.tr("Server context incomplete (default adapter is missing), please to reconnect!") )
            defAdapter = 'v000'
        else:
            defAdapter = Settings.instance().serverContext['default-adapter']

        # new in v17
        defaultTimeout = Settings.instance().readValue( key = 'TestProperties/default-timeout' )
        
        _defaults_inputs = []
        _defaults_outputs = []
        try:
            defaultInputs = Settings.instance().readValue( key = 'TestProperties/default-inputs')
            _defaults_inputs = json.loads(defaultInputs)
        except Exception as e:
            self.error("bad default inputs provided: %s - %s" % (e,defaultInputs))
        try:
            defaultOutputs = Settings.instance().readValue( key = 'TestProperties/default-outputs')
            _defaults_outputs = json.loads(defaultOutputs)
        except Exception as e:
            self.error("bad default outputs provided: %s - %s" % (e,defaultOutputs))
        # end of new
        
        self.dataModel = FileModelTestPlan.DataModel(userName=userName, defLibrary=defLibrary, 
                                                    defAdapter=defAdapter, isGlobal=testGlobal,
                                                    timeout=defaultTimeout, inputs=_defaults_inputs, 
                                                     outputs=_defaults_outputs)

        self.tp = None
        self.tpRoot = None
        self.tsId = -1
        self.localConfigured = None
        self.editActive=False
        self.items = [] 
        self.itemsExpanded = True
        self.itemDoubleClicked=False   

        self.allItemsEnabled=True
        self.testGlobal = testGlobal
        
        self.__mime__ = "application/x-%s-test" % Settings.instance().readValue( key='Common/acronym' ).lower()

        # new in v12.2
        self.CONDITION_IF            = Settings.instance().readValue( key = 'TestPlan/condition-if' )
        self.CONDITION_OK            = Settings.instance().readValue( key = 'TestPlan/condition-ok' )
        self.CONDITION_KO            = Settings.instance().readValue( key = 'TestPlan/condition-ko' )
        self.CONDITION_IS            = Settings.instance().readValue( key = 'TestPlan/condition-is' )
        self.CONDITION_RUN           = Settings.instance().readValue( key = 'TestPlan/condition-run' )
        self.CONDITION_THEN          = Settings.instance().readValue( key = 'TestPlan/condition-then' )
        self.CONDITION_DO            = Settings.instance().readValue( key = 'TestPlan/condition-do' )
        self.CONDITION_DONT          = Settings.instance().readValue( key = 'TestPlan/condition-dont' )
        # end of new
        
        self.insertQueue = []
        self.insertDetails = None
        
        self.createActions()
        self.createWidgets()
        self.createConnections()    
        self.createToolbar()

    def getTsId (self):
        """
        Return an unique test id
        """
        self.tsId += 1
        return str(self.tsId)

    def viewer(self):
        """
        return the document viewer
        """
        return self.parent
       
    def createWidgets (self):
        """
        Create qt widget
        """
        self.dockToolbarMove = QToolBar(self)
        self.dockToolbarMove.setStyleSheet("QToolBar { border: 0px; margin: 0px; }") # remove 3D border
        self.dockToolbarMove.setOrientation(Qt.Vertical)
        
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarUpdate = QToolBar(self)
        self.dockToolbarUpdate.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarUpdate.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarClipboard = QToolBar(self)
        self.dockToolbarClipboard.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        
        self.dockToolbarClipboard2 = QToolBar(self)
        self.dockToolbarClipboard2.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.dockToolbarMisc = QToolBar(self)
        self.dockToolbarMisc.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        
        self.dockToolbarMisc2 = QToolBar(self)
        self.dockToolbarMisc2.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.dockToolbarParams = QToolBar(self)
        self.dockToolbarParams.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarParams.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.dockToolbarMass = QToolBar(self)
        self.dockToolbarMass.setStyleSheet("QToolBar { border: 0px }") # remove 3D border
        self.dockToolbarMass.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        layout = QVBoxLayout()

        self.tp = QTreeWidgetEnhancement(document=self)
        self.tp.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.tp.setFrameShape(QFrame.NoFrame)
        
        self.tp.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tp.setStyleSheet("""QTreeWidget::item{ height: 25px;}""");

        self.labels = [ self.tr("Name"), self.tr(""), self.tr("Id"),  self.tr("Tag"),  
                        self.tr(""), self.tr(""), self.tr(""), self.tr(""),
                        self.tr("Run"), self.tr("Repository"), self.tr("Alias"), 
                        self.tr("Description") ]
        self.tp.setHeaderLabels(self.labels)

        # move the second column (id) on the first
        self.tp.header().moveSection(0, COL_CONTROL)        
        # move the second column (id) on the first
        self.tp.header().moveSection(1, COL_ID)
        # move the third column (cond) on the second
        self.tp.header().moveSection(2, COL_TAG_COLOR)
        # move the third column (cond) on the second
        self.tp.header().moveSection(3, COL_CONDITION_BEGIN)
        # move the sixty column (action) on the third
        self.tp.header().moveSection(4, COL_ACTION)

        if self.testGlobal:
            title = QLabel(self.tr("Test Global Definition:"))
        else:
            title = QLabel(self.tr("Test Plan Definition:"))
        title.setStyleSheet("QLabel { padding-left: 2px; padding-top: 2px }")
        font = QFont()
        font.setBold(True)
        title.setFont(font)

        # toolbars init
        self.testsBox = QGroupBox("Tests")
        self.testsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
                                        
        layoutTestsBox = QHBoxLayout()
        layoutTestsBox.addWidget(self.dockToolbar)
        layoutTestsBox.setContentsMargins(0,0,0,0)
        self.testsBox.setLayout(layoutTestsBox)
        
        self.updateBox = QGroupBox("Update")
        self.updateBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutUpdateBox = QHBoxLayout()
        layoutUpdateBox.addWidget(self.dockToolbarUpdate)
        layoutUpdateBox.setContentsMargins(0,0,0,0)
        self.updateBox.setLayout(layoutUpdateBox)
        
        self.clipBox = QGroupBox("Clip.")
        self.clipBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutClipBox = QVBoxLayout()
        layoutClipBox.addWidget(self.dockToolbarClipboard)
        layoutClipBox.addWidget(self.dockToolbarClipboard2)
        layoutClipBox.setContentsMargins(0,0,0,0)
        self.clipBox.setLayout(layoutClipBox)
        
        self.miscBox = QGroupBox("Misc.")
        self.miscBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutMiscBox = QVBoxLayout()
        layoutMiscBox.addWidget(self.dockToolbarMisc)
        layoutMiscBox.addWidget(self.dockToolbarMisc2)
        layoutMiscBox.setContentsMargins(0,0,0,0)
        self.miscBox.setLayout(layoutMiscBox)
        
        self.paramsBox = QGroupBox("Inputs/Outputs")
        self.paramsBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutParamsBox = QHBoxLayout()
        layoutParamsBox.addWidget(self.dockToolbarParams)
        layoutParamsBox.setContentsMargins(0,0,0,0)
        self.paramsBox.setLayout(layoutParamsBox)
        
        self.massBox = QGroupBox("Mass actions")
        self.massBox.setStyleSheet( """
                                           QGroupBox { font: normal; border: 1px solid silver; border-radius: 2px; } 
                                           QGroupBox { padding-bottom: 10px; background-color: #FAFAFA; } 
                                           QGroupBox::title { subcontrol-position: bottom center;}
                                       """ )
        layoutMassBox = QHBoxLayout()
        layoutMassBox.addWidget(self.dockToolbarMass)
        layoutMassBox.setContentsMargins(0,0,0,0)
        self.massBox.setLayout(layoutMassBox)
        
        self.currentEdit = QLineEdit()
        self.currentEdit.setReadOnly(True)
        self.currentEdit.setStyleSheet("QLineEdit { background-color : #F0F0F0; color: grey; }")
        
        layoutToolbars = QHBoxLayout()
        layoutToolbars.addWidget(self.testsBox)
        layoutToolbars.addWidget(self.updateBox)
        layoutToolbars.addWidget(self.massBox)
        layoutToolbars.addWidget(self.paramsBox)
        layoutToolbars.addWidget(self.clipBox)
        layoutToolbars.addWidget(self.miscBox)
        layoutToolbars.addStretch(1)
        layoutToolbars.setContentsMargins(5,0,0,0)
        
        layoutVToolbars = QHBoxLayout()
        layoutVToolbars.addWidget(self.dockToolbarMove)
        layoutVToolbars.addWidget(self.tp)
        layoutVToolbars.setContentsMargins(5,0,0,0)

        # final layout
        layout.addWidget(title)
        layout.addLayout(layoutToolbars)
        layout.addLayout(layoutVToolbars)
        layout.addWidget(self.currentEdit)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # column size
        self.tp.setColumnWidth(COL_NAME, 50)
        self.tp.setColumnWidth(COL_CONTROL, 30)
        self.tp.setColumnWidth(COL_ID, 30)
        self.tp.setColumnWidth(COL_TAG_COLOR, 30)
        self.tp.setColumnWidth(COL_ENABLE, 30)
        self.tp.setColumnWidth(COL_CONDITION_BEGIN, 40)
        self.tp.setColumnWidth(COL_RESULT, 75)
        self.tp.setColumnWidth(COL_CONDITION_END, 45)
        self.tp.setColumnWidth(COL_ACTION, 65)
        
        if Settings.instance().readValue( key = 'TestPlan/hide-repo-column' ):
            self.tp.hideColumn(COL_REPO)
        if Settings.instance().readValue( key = 'TestPlan/hide-alias-column' ):
            self.tp.hideColumn(COL_ALIAS)
        if Settings.instance().readValue( key = 'TestPlan/hide-tag-column' ):
            self.tp.hideColumn(COL_TAG_COLOR)
        if Settings.instance().readValue( key = 'TestPlan/hide-run-column' ):
            self.tp.hideColumn(COL_ENABLE)
            
    def createConnections (self):
        """
        create qt connection
        """
        self.tp.customContextMenuRequested.connect(self.onPopupMenu)
        self.tp.itemClicked.connect(self.onItemClicked)
        self.tp.itemSelectionChanged.connect(self.onSelectionChanged)
        self.tp.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.tp.currentItemChanged.connect(self.onCurrentItemChanged)
        
        self.tp.InsertTest.connect(self.onDropTest)
            
    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|--|||
        || Add  |  |||
        ||------|--|||
        """
        self.dockToolbar.setObjectName("Test Plan toolbar")
        self.dockToolbar.addAction( self.addAction )
        self.dockToolbar.addAction( self.insertAboveAction )
        self.dockToolbar.addAction( self.insertBelowAction )
        self.dockToolbar.addAction(self.delAction)
        self.dockToolbar.setIconSize(QSize(16, 16))
        
        self.dockToolbarParams.setObjectName("Params toolbar")
        self.dockToolbarParams.addAction( self.reloadParametersAction )
        self.dockToolbarParams.addAction( self.mergeParametersAction )
        self.dockToolbarParams.addAction(self.clearParamsAction)
        self.dockToolbarParams.setIconSize(QSize(16, 16))
        
        self.dockToolbarClipboard.setObjectName("Clipboard toolbar")
        self.dockToolbarClipboard.addAction(self.copyAction)
        self.dockToolbarClipboard.setIconSize(QSize(16, 16))
        
        self.dockToolbarClipboard2.setObjectName("Clipboard toolbar")
        self.dockToolbarClipboard2.addAction(self.pasteAction)
        self.dockToolbarClipboard2.setIconSize(QSize(16, 16))
        
        self.dockToolbarMisc.setObjectName("Misc toolbar")
        self.dockToolbarMisc.addAction(self.toggleExpandAllAction)
        self.dockToolbarMisc.addAction(self.colorsAction)
        self.dockToolbarMisc.setIconSize(QSize(16, 16))
        
        self.dockToolbarMisc2.setObjectName("Misc 2 toolbar")
        self.dockToolbarMisc2.addAction(self.checkAllAction)
        self.dockToolbarMisc2.addAction(self.openAction)
        self.dockToolbarMisc2.setIconSize(QSize(16, 16))

        self.dockToolbarUpdate.setObjectName("Update toolbar")
        self.dockToolbarUpdate.addAction(self.updateAliasAction)
        self.dockToolbarUpdate.addAction(self.updatePathAction)
        self.dockToolbarUpdate.setIconSize(QSize(16, 16))
        
        self.dockToolbarMass.setObjectName("Mass toolbar")
        self.dockToolbarMass.addAction(self.updateProjectsAction)
        self.dockToolbarMass.addAction(self.updateMainLocationsAction)
        self.dockToolbarMass.addAction(self.updateAliasAllAction)
        self.dockToolbarMass.addAction(self.openAllAction)
        self.dockToolbarMass.setIconSize(QSize(16, 16))

        
        self.dockToolbarMove.setObjectName("Move toolbar")
        self.dockToolbarMove.addSeparator()
        self.dockToolbarMove.addAction(self.enableTestAction)
        self.dockToolbarMove.addAction(self.disableTestAction)
        self.dockToolbarMove.addSeparator()
        self.dockToolbarMove.addAction(self.moveUpAction)
        self.dockToolbarMove.addAction(self.moveDownAction)
        self.dockToolbarMove.addAction(self.moveLeftAction)
        self.dockToolbarMove.addAction(self.moveRightAction)
        self.dockToolbarMove.addSeparator()
        self.dockToolbarMove.addAction(self.ifOkAction)
        self.dockToolbarMove.addAction(self.ifKoAction)
        self.dockToolbarMove.addSeparator()
        self.dockToolbarMove.setIconSize(QSize(16, 16))
        
    def createActions (self):
        """
        Create Qt Actions
        """
        self.copyAction = QtHelper.createAction(self, self.tr("&Copy\nTest"), self.copyTestFile, 
                                        icon = QIcon(":/duplicate-test.png"), tip = self.tr('Copy test') )
        self.cutAction = QtHelper.createAction(self, self.tr("&Cut\nTest"), self.cutTestFile, 
                                        icon = None, tip = self.tr('Cut test') )
        self.pasteChildAction = QtHelper.createAction(self, self.tr("&Paste Child"), self.onPasteTestFileChild, 
                                        icon = None, tip = self.tr('Paste test as child') )
        self.pasteAboveAction = QtHelper.createAction(self, self.tr("&Paste Above"), self.onPasteTestFileAbove, 
                                        icon = None, tip = self.tr('Paste test above the selection') )
        self.pasteBelowAction = QtHelper.createAction(self, self.tr("&Paste Below"), self.onPasteTestFileBelow, 
                                        icon = None, tip = self.tr('Paste test below the selection') )
        self.menuPaste = QMenu(self.tr("Paste"))
        self.menuPaste.addAction( self.pasteChildAction )
        self.menuPaste.addAction( self.pasteAboveAction )
        self.menuPaste.addAction( self.pasteBelowAction )
        self.pasteAction = QtHelper.createAction(self, self.tr("&Paste"), None, tip = self.tr('Paste'), 
                                        icon=QIcon(":/paste-test.png") )
        self.pasteAction.setMenu(self.menuPaste)


        self.delAction = QtHelper.createAction(self, self.tr("&Remove"), self.delItem, shortcut = "Delete", 
                                        icon = QIcon(":/tp-del.png"), tip = self.tr('Remove test') )
        self.delAllAction = QtHelper.createAction(self, self.tr("&Remove All"), self.delItem, shortcut = "Delete", 
                                        icon = QIcon(":/tp-del.png"), tip = self.tr('Remove test(s)') )
        self.openAction = QtHelper.createAction(self, self.tr("&Open original"), self.openTestFile, 
                                        icon = QIcon(":/open-test.png"), tip = self.tr('Open the selected test') )
        self.openAllAction = QtHelper.createAction(self, self.tr("&Open\nAll"), self.openAllTestFile, 
                                        icon = QIcon(":/open-test.png"), tip = self.tr('Open all tests') )
        self.updateAliasAllAction = QtHelper.createAction(self, self.tr("&Default\nAliases"), self.updateAllDefaultAliases, 
                                        icon = QIcon(":/tc-name.png"), tip = self.tr('Open all tests') )
        
        self.reloadParametersAction = QtHelper.createAction(self, self.tr("&Reload"), self.reloadTestProperties, 
                                        icon = QIcon(":/refresh-test.png"), tooltip=self.tr('Reload test properties'), 
                                        tip = self.tr('Reload test properties from the original test') )
        self.mergeParametersAction = QtHelper.createAction(self, self.tr("&Merge"), self.mergeTestProperties, 
                                        icon = QIcon(":/test-parameter-merge.png"), tooltip=self.tr('Merge test properties'), 
                                        tip = self.tr('Merge original test properties with actual') )
        self.clearParametersAction = QtHelper.createAction(self, self.tr("&Clear"), self.clearTestProperties, 
                                        icon = QIcon(":/test-parameter-clear.png"), tooltip=self.tr('Clear test properties'), 
                                        tip = self.tr('Clear test properties of the selected test') )
        self.clearAllParametersAction = QtHelper.createAction(self, self.tr("&Clear All"), self.clearAllTestProperties, 
                                        icon = QIcon(":/test-parameter-clear.png"), tooltip=self.tr('Clear test properties'), 
                                        tip = self.tr('Clear all test properties') )
                                        
        self.menuClear = QMenu(self.tr("Clear"))
        self.menuClear.addAction( self.clearParametersAction )
        self.menuClear.addAction( self.clearAllParametersAction )
        self.clearParamsAction = QtHelper.createAction(self, self.tr("Clear"), self.clearTestProperties, 
                                        icon = QIcon(":/test-parameter-clear.png") )
        self.clearParamsAction.setMenu(self.menuClear)
        
        self.menuParameters = QMenu(self.tr("Inputs/Outputs"))
        self.menuParameters.addAction( self.reloadParametersAction )
        self.menuParameters.addAction( self.mergeParametersAction )
        self.menuParameters.addAction( self.clearParametersAction )
        
        self.reloadAction = QtHelper.createAction(self, self.tr("Inputs/Outputs"), None, 
                                        icon = QIcon(":/test-parameter-clear.png") )
        self.reloadAction.setMenu(self.menuParameters)

        self.toggleExpandAllAction = QtHelper.createAction(self, self.tr("&Expand\nCollapse"), self.toggleExpandAll, 
                                        icon = QIcon(":/toggle-expand.png"), tip = self.tr('Expand or collapse all items') )
        self.expandAllAction = QtHelper.createAction(self, self.tr("&Expand All..."), self.expandAllItems, 
                                        icon = None, tip = self.tr('Expand all items') )
        self.collapseAllAction = QtHelper.createAction(self, self.tr("&Collapse All..."), self.collapseAllItems, 
                                        icon = None, tip = self.tr('Collapse all items') )

        self.refreshAction = QtHelper.createAction(self, self.tr("Refresh"), self.refreshContent, 
                                        icon = QIcon(":/act-refresh.png"), tip = self.tr('Refresh the tree') )
        
        self.menuUpdate = QMenu(self.tr("Update"))
        self.updatePathAction = QtHelper.createAction(self, self.tr("&Location"), self.updateTest, 
                                        icon = QIcon(":/location.png") )
        self.updateTcNameAction = QtHelper.createAction(self, self.tr("&TestCase\nName"), self.updateTcName, 
                                        icon = QIcon(":/tc-name.png") )
                                        
        self.updateProjectAction = QtHelper.createAction(self, self.tr("&Project"), self.updateProject, 
                                        icon = QIcon(":/project.png") )
        self.updateAliasAction = QtHelper.createAction(self, self.tr("&Alias\nName"), self.updateAlias, 
                                        icon = QIcon(":/tc-name.png") )
        self.updateProjectsAction = QtHelper.createAction(self, self.tr("&Update\nProject"), self.updateProjects, 
                                        icon = QIcon(":/project.png") )
        self.updateMainLocationsAction = QtHelper.createAction(self, self.tr("&Replace\nLocations"), self.updateMainLocations, 
                                        icon = QIcon(":/location.png") )
        self.menuUpdate.addAction( self.updateAliasAction )
        self.menuUpdate.addAction( self.updateProjectAction )
        self.menuUpdate.addAction( self.updatePathAction )
        self.menuUpdate.addAction( self.updateTcNameAction )
        self.updateAction = QtHelper.createAction(self, self.tr("Update"), None, 
                                        icon = None )
        self.updateAction.setMenu(self.menuUpdate)
        
        self.moveUpAction = QtHelper.createAction(self, self.tr("&Move Up"), self.moveUpTestFile,
                                        icon = QIcon(":/up.png"), tip = self.tr('up') )
        self.moveDownAction = QtHelper.createAction(self, self.tr("&Move Down"), self.moveDownTestFile,
                                        icon = QIcon(":/down.png"), tip = self.tr('down') )

        self.moveRightAction = QtHelper.createAction(self, self.tr("&Move Right"), self.moveRightTestFile, 
                                        icon = QIcon(":/right.png"), tip = self.tr('right') )
        self.moveLeftAction = QtHelper.createAction(self, self.tr("&Move Left"), self.moveLeftTestFile, 
                                        icon = QIcon(":/left.png"), tip = self.tr('left') )
        if self.testGlobal:
            self.moveRightAction.setEnabled(False)
            self.moveLeftAction.setEnabled(False)
            
        self.addAction = QtHelper.createAction(self, self.tr("&Insert\nChild"), self.addTestFile, 
                                        icon = QIcon(":/tp-insert-child.png"), tip = self.tr('Add test as child') )
        self.insertBelowAction = QtHelper.createAction(self, self.tr("&Insert\nBelow"), self.insertBelow, 
                                        icon = QIcon(":/tp-insert-bellow.png"), tip = self.tr('Add test below') )
        self.insertAboveAction = QtHelper.createAction(self, self.tr("&Insert\nAbove"), self.insertAbove, 
                                        icon = QIcon(":/tp-insert-above.png"), tip = self.tr('Add test above') )
        self.menuInsert = QMenu(self.tr("Add Test"))
        self.menuInsert.addAction( self.addAction )
        self.menuInsert.addAction( self.insertAboveAction )
        self.menuInsert.addAction( self.insertBelowAction )
        self.insertAction = QtHelper.createAction(self, self.tr("&Insert Test"), self.addTestFile, tip = self.tr('Add a test'), 
                                        icon=QIcon(":/tp-add.png") )
        self.insertAction.setMenu(self.menuInsert)

        self.addOrangeColorAction = QtHelper.createAction(self, self.tr("&Orange"), self.addOrangeColor, 
                                        icon = None, tip = self.tr('Orange color') )
        self.addYellowColorAction = QtHelper.createAction(self, self.tr("&Yellow"), self.addYellowColor, 
                                        icon = None, tip = self.tr('Yellow color') )
        self.addBlueColorAction = QtHelper.createAction(self, self.tr("&Blue"), self.addBlueColor, 
                                        icon = None, tip = self.tr('Blue color') )
        self.addGreenColorAction = QtHelper.createAction(self, self.tr("&Green"), self.addGreenColor, 
                                        icon = None, tip = self.tr('Green color') )
        self.addRedColorAction = QtHelper.createAction(self, self.tr("&Red"), self.addRedColor, 
                                        icon = None, tip = self.tr('Red color') )
        self.addWhiteColorAction = QtHelper.createAction(self, self.tr("&None"), self.addWhiteColor, 
                                        icon = None, tip = self.tr('None color') )
        self.addGrayColorAction = QtHelper.createAction(self, self.tr("&Gray"), self.addGrayColor, 
                                        icon = None, tip = self.tr('Gray color') )
        self.addCyanColorAction = QtHelper.createAction(self, self.tr("&Cyan"), self.addCyanColor, 
                                        icon = None, tip = self.tr('Cyan color') )
        self.addMagentaColorAction = QtHelper.createAction(self, self.tr("&Magenta"), self.addMagentaColor, 
                                        icon = None, tip = self.tr('Magenta color') )
        self.addPurpleColorAction = QtHelper.createAction(self, self.tr("&Purple"), self.addPurpleColor, 
                                        icon = None, tip = self.tr('Purple color') )

        self.menuColor = QMenu(self.tr("Add colors"))
        self.menuColor.addAction( self.addOrangeColorAction )
        self.menuColor.addAction( self.addGreenColorAction )
        self.menuColor.addAction( self.addRedColorAction )
        self.menuColor.addAction( self.addBlueColorAction )
        self.menuColor.addAction( self.addYellowColorAction )
        self.menuColor.addAction( self.addGrayColorAction )
        self.menuColor.addAction( self.addCyanColorAction )
        self.menuColor.addAction( self.addMagentaColorAction )
        self.menuColor.addAction( self.addPurpleColorAction )
        self.menuColor.addSeparator()
        self.menuColor.addAction( self.addWhiteColorAction )

        self.colorsAction = QtHelper.createAction(self, self.tr("&Colors"), None, tip = self.tr('Add colors'), 
                                        icon=QIcon(":/colors.png") )
        self.colorsAction.setMenu(self.menuColor)

        self.checkAllAction = QtHelper.createAction(self, self.tr("Enable/disable all tests"), self.checkAll, 
                                        icon = QIcon(":/checkall.png"), tip = self.tr('Enable/disable all tests'))
        self.enableTestAction = QtHelper.createAction(self, self.tr("Enable"), self.enableTest, 
                                        icon = QIcon(":/check.png"), tip = self.tr('Enable the current test'))
        self.disableTestAction = QtHelper.createAction(self, self.tr("Disable"), self.disableTest, 
                                        icon = QIcon(":/uncheck.png"), tip = self.tr('Disable the current test'))

                             
        self.ifOkAction = QtHelper.createAction(self, self.tr("IF OK"), self.updateIfOk, 
                                        icon = QIcon(":/ifok.png"), tip = self.tr('IF OK'))
        self.ifKoAction = QtHelper.createAction(self, self.tr("IF KO"), self.updateIfKo, 
                                        icon = QIcon(":/ifko.png"), tip = self.tr('IF KO'))
        if self.testGlobal:
            self.ifOkAction.setEnabled(False)
            self.ifKoAction.setEnabled(False)
        self.defaultActions()

    def updateIfOk(self):
        """
        """
        selectedItems  = self.tp.selectedItems()
        if not len(selectedItems): return
        
        # ignore other items
        selectedItem = selectedItems[0]
        if selectedItem.type() != 0: return
        if selectedItem.childCount() == 0: return

        selectedItem.setText(COL_RESULT, self.CONDITION_OK)
        for i in range(selectedItem.childCount()):
            itmChild = selectedItem.child(i)
            testId = str(itmChild.text(COL_ID))
            self.dataModel.updateTestFileParentCondition(itemId=str(testId), 
                                                         parentCondition=FileModelTestPlan.IF_OK )
            
        self.setModify()
        
    def updateIfKo(self):
        """
        """
        selectedItems  = self.tp.selectedItems()
        if not len(selectedItems): return
        
        # ignore other items
        selectedItem = selectedItems[0]
        if selectedItem.type() != 0: return
        if selectedItem.childCount() == 0: return

        selectedItem.setText(COL_RESULT, self.CONDITION_KO)
        for i in range(selectedItem.childCount()):
            itmChild = selectedItem.child(i)
            testId = str(itmChild.text(COL_ID))
            self.dataModel.updateTestFileParentCondition(itemId=str(testId), 
                                                         parentCondition=FileModelTestPlan.IF_KO )
            
        self.setModify()
        
    def onDropTest(self, test, parentItem):
        """
        """
        if parentItem is None: return
            
        parentId = parentItem.text(COL_ID)
        parentId = int(parentId)
        
        insertAction = 1
        if parentId == 0: insertAction = 0
        
        if self.testGlobal:
            RCI.instance().openFileTests(projectId=int(test['projectid']), 
                                         filePath=test['pathfile'], 
                                         ignoreLock=True, 
                                         readOnly=False, 
                                         customParam=parentId, 
                                         actionId=insertAction, 
                                         destinationId=RCI.FOR_DEST_TG)                            
                                        
        else:
            RCI.instance().openFileTests(projectId=int(test['projectid']), 
                                         filePath=test['pathfile'], 
                                         ignoreLock=True, 
                                         readOnly=False, 
                                         customParam=parentId, 
                                         actionId=insertAction, 
                                         destinationId=RCI.FOR_DEST_TP) 
    def updateAllDefaultAliases(self):
        """
        """
        answer = QMessageBox.question(self,  self.tr("Default aliases"),  
                                      self.tr("Do you want to set all tests with default aliases?"), 
            QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            testfiles = self.dataModel.testplan['testplan']['testfile']
            
            for  tf in testfiles:
                _testpath = tf['file'].split(":")[1]
                _testname = _testpath.rsplit("/", 1)
                if len(_testname) == 2:
                    aliasItem = _testname[1]
                else:
                    aliasItem = _testname[0]
                # remove extension
                aliasItem = aliasItem.rsplit(".", 1)[0]
                
                self.dataModel.updateTestFileAlias( tf["id"], self.safeAlias(alias=aliasItem) ) 
                
                self.__updateTestAlias(itmParent=self.tpRoot, aliasName=aliasItem.upper(), testId=tf["id"])
            
            self.resizeColumns()
            self.setModify()

    def __updateTestAlias(self, itmParent, aliasName, testId):
        """
        """
        for i in xrange(itmParent.childCount()):
            itmChild = itmParent.child(i)
            
            if int(itmChild.text(COL_ID)) == int(testId):
                itmChild.setText(COL_NAME, aliasName)
                itmChild.setText(COL_ALIAS, aliasName)
                itmChild.setIcon(COL_NAME, QIcon(":/tc-name.png") )
            else:
                if itmChild.childCount():
                    self.__updateTestAlias(itmParent=itmChild, aliasName=aliasName, testId=testId)
                
    def defaultActions(self):
        """
        Set default actions values
        """
        self.addAction.setEnabled(False)
        self.delAction.setEnabled(False)
        self.delAllAction.setEnabled(False)
        self.openAction.setEnabled(False)
        self.openAllAction.setEnabled(False)
        self.reloadAction.setEnabled(False)

        self.refreshAction.setEnabled(True)
        
        self.reloadParametersAction.setEnabled(False)
        self.mergeParametersAction.setEnabled(False)
        self.clearParametersAction.setEnabled(False)
        self.clearAllParametersAction.setEnabled(False)
        
        self.addOrangeColorAction.setEnabled(True)
        self.addYellowColorAction.setEnabled(True)
        self.addBlueColorAction.setEnabled(True)
        self.addGreenColorAction.setEnabled(True)
        self.addRedColorAction.setEnabled(True)
        self.addWhiteColorAction.setEnabled(True)
        self.addGrayColorAction.setEnabled(True)
        self.addCyanColorAction.setEnabled(True)
        self.addMagentaColorAction.setEnabled(True)
        self.addPurpleColorAction.setEnabled(True)
        self.menuColor.setEnabled(False)

        self.insertAction.setEnabled(True)
        self.updatePathAction.setEnabled(False)
        self.updateTcNameAction.setEnabled(False)
        self.updateProjectAction.setEnabled(False)
        self.updateAliasAction.setEnabled(False)
            
        self.copyAction.setEnabled(False)
        self.pasteAboveAction.setEnabled(False)
        self.pasteBelowAction.setEnabled(False)
        self.pasteChildAction.setEnabled(False)

    def updateAlias(self):
        """
        """
        selectedItem  = self.tp.selectedItems()[0]
        if selectedItem.type() != 0:
            return
            
        testId = str(selectedItem.text(COL_ID))
        modelFile = self.dataModel.getTestFile( testId )

        aliasItem = selectedItem.text(COL_ALIAS)
        
        if not len(aliasItem):
            _testpath = selectedItem.text(COL_NAME).split(":")[1]
            _testname = _testpath.rsplit("/", 1)
            if len(_testname) == 2:
                aliasItem = _testname[1]
            else:
                aliasItem = _testname[0]
                
        aliasDialog = AliasDialog( alias=aliasItem, parent=self )
        if aliasDialog.exec_() == QDialog.Accepted:
            newAlias = aliasDialog.getAlias()
            newAlias = newAlias.upper()
            
            self.dataModel.updateTestFileAlias( testId, self.safeAlias(alias=newAlias) ) 

            if len(newAlias): 
                selectedItem.setIcon(COL_NAME, QIcon(":/tc-name.png") )
            else:
                extension = modelFile["extension"]
                if extension == TestSuite.TYPE:
                    selectedItem.setIcon(COL_NAME, QIcon(":/%s.png" % TestSuite.TYPE) )
                elif extension == TYPE:
                    selectedItem.setIcon(COL_NAME, QIcon(":/%s.png" % TYPE) )
                elif extension == TestAbstract.TYPE:
                    selectedItem.setIcon(COL_NAME, QIcon(":/%s.png" % TestAbstract.TYPE) )
                else:
                    selectedItem.setIcon(COL_NAME, QIcon(":/%s.png" % TestUnit.TYPE) )
                
            if sys.version_info > (3,): # py3 support
                selectedItem.setText(COL_ALIAS, newAlias)
                if len(newAlias): 
                    selectedItem.setText(COL_NAME,newAlias)
                else:
                    selectedItem.setText(COL_NAME, selectedItem.toolTip(COL_NAME) )
                    
            else:
                if isinstance(newAlias, str):
                    selectedItem.setText(COL_ALIAS, newAlias.decode('utf-8') )
                else:
                    selectedItem.setText(COL_ALIAS, newAlias )

                if len(newAlias):
                    if isinstance(newAlias, str):
                        selectedItem.setText(COL_NAME, newAlias.decode('utf-8') )
                    else:
                        selectedItem.setText(COL_NAME, newAlias )
                else:
                    selectedItem.setText(COL_NAME, selectedItem.toolTip(COL_NAME) )
                    
            self.resizeColumns()
            self.setModify()
            
    def updateTcName(self):
        """
        Update test case name
        """
        selectedItem  = self.tp.selectedItems()[0]
        if selectedItem.type() != 0:
            return

        testId = str(selectedItem.text(COL_ID))
        modelFile = self.dataModel.getTestFile( testId )

        descrTest = modelFile['properties']['descriptions']['description']
        i = 0
        for d in descrTest:
            if d['key'] == 'name':
                break
            i += 1

        text, ok = QInputDialog.getText(self, "TestCase Name", 
                                 "TestCase name:", QLineEdit.Normal,
                                 modelFile['properties']['descriptions']['description'][i]['value'])
        if ok and text != '':
            modelFile['properties']['descriptions']['description'][i]['value'] = str(text)

        self.dataModel.updateTestFileProperties(itemId=str(testId), properties=modelFile['properties'])
    
        self.setModify()

    def updateTest(self):
        """
        Update the path of a test
        """
        item_id = self.itemCurrent.text(COL_ID)
        update_location = False
        ret = self.addTestFile(updatePath=True)
        if ret is None:
            return
        
        if len(ret) == 4:
            (testName, fromRepo, currentItem, projectId ) = ret
        else:
            (testName, fromRepo, currentItem, projectId, update_location) = ret

        # dbr13 >>>
        # prepare old file name
        old_test_file_name = None
        if update_location:
            for test_file in self.dataModel.testplan['testplan']['testfile']:
                if item_id == test_file['id']:
                    old_test_file_name = test_file['file']
                    break
        # dbr13 <<<

        # local file
        if projectId is None:
            QMessageBox.warning(self, self.tr("Information") , self.tr("Local file not yet supported") )
        else:
            info = testName[0]
            # parse the argument info  in three variables ( path, filename and extension )
            extension = str(info).rsplit(".", 1)[1]
            tmp = str(info).rsplit("/", 1)
            if len(tmp) > 1 :
                path = tmp[0]
                filename = tmp[1].rsplit(".", 1)[0]
                absPath = '%s/%s.%s' % (path, filename, extension)
            else:
                path = ""
                filename = tmp[0].rsplit(".", 1)[0]
                absPath = '%s.%s' % ( filename, extension)

            if self.testGlobal:
                RCI.instance().openFileTests(projectId=int(projectId), filePath=absPath, 
                                             ignoreLock=False, readOnly=False, 
                                             customParam=int(currentItem.text(COL_ID)), 
                                             actionId=RCI.ACTION_UPDATE_PATH, destinationId=RCI.FOR_DEST_TG,
                                             # dbr13 >>>
                                             extra={'update_location': update_location,
                                                    'file_name': old_test_file_name})
                                             # dbr13 <<<
            else:
                RCI.instance().openFileTests(projectId=int(projectId), filePath=absPath, 
                                             ignoreLock=False, readOnly=False, 
                                             customParam=int(currentItem.text(COL_ID)), 
                                             actionId=RCI.ACTION_UPDATE_PATH, destinationId=RCI.FOR_DEST_TP,
                                             # dbr13 >>>
                                             extra={'update_location': update_location,
                                                    'file_name': old_test_file_name})
                                             # dbr13 <<<

    def updateMainLocations(self):
        """
        Update projects of all remote tests
        """
        dialog = UpdateLocationsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            oldLoc, newLoc = dialog.getNewLocations()

            testfiles = self.dataModel.testplan['testplan']['testfile']
            for  tf in testfiles:
                if tf['type'] == 'remote':
                    curPrj, oldPath = tf["file"].split(":", 1)
                    newPath = oldPath.replace(oldLoc, newLoc)
                    tf["file"] = "%s:%s" % (curPrj, newPath)
            
            self.__updateTestLoc(itmParent=self.tpRoot, oldLoc=oldLoc, newLoc=newLoc)
            
            self.resizeColumns()
            self.setModify()
            
    def __updateTestLoc(self, itmParent, oldLoc, newLoc):
        """
        """
        for i in xrange(itmParent.childCount()):
            itmChild = itmParent.child(i)
            
            tsFile = itmChild.toolTip(COL_NAME)
            curPrj, oldPath = tsFile.split(":", 1)
            newPath = oldPath.replace(oldLoc, newLoc)
            newFile = "%s:%s" % (curPrj, newPath)
            tsname = newFile.rsplit(".", 1) # remove extension file before display
            
            if not len(itmChild.text(COL_ALIAS)): 
                itmChild.setText(COL_NAME, tsname[0])
            itmChild.setToolTip(COL_NAME, tsname[0])
            self.currentEdit.setText( itmChild.toolTip(COL_NAME) )
            
            if itmChild.childCount():
                self.__updateTestLoc(itmParent=itmChild, oldLoc=oldLoc, newLoc=newLoc)

    def updateProjects(self):
        """
        Update projects of all remote test
        """
        prjsList = []
        for prj in self.iRepo.remote().projects:
            prjsList.append(prj["name"])
        newPrj, ok = QInputDialog.getItem (self, "Project",  "Select the new project:", prjsList, 0, False)
        if ok:
            testfiles = self.dataModel.testplan['testplan']['testfile']
            for  tf in testfiles:
                if tf['type'] == 'remote':
                    newFile = "%s:%s" % (newPrj, tf["file"].split(":", 1)[1] )
                    tf["file"] = newFile
                    
                    
            
            self.__updateTestPrj(itmParent=self.tpRoot, prjName=newPrj)
            
            self.resizeColumns()
            self.setModify()

    def __updateTestPrj(self, itmParent, prjName):
        """
        """
        for i in xrange(itmParent.childCount()):
            itmChild = itmParent.child(i)
            
            tsFile = itmChild.toolTip(COL_NAME)
            newFile = "%s:%s" % (prjName, tsFile.split(":", 1)[1] )
            tsname = newFile.rsplit(".", 1) # remove extension file before display

            if not len(itmChild.text(COL_ALIAS)): itmChild.setText(COL_NAME, tsname[0])
            itmChild.setToolTip(COL_NAME, tsname[0])
            self.currentEdit.setText( itmChild.toolTip(COL_NAME) )
            
            if itmChild.childCount():
                self.__updateTestPrj(itmParent=itmChild, prjName=prjName)
                
    def updateProject(self):
        """
        Update projects of all remote test
        """
        selectedItem  = self.tp.selectedItems()[0]
        if selectedItem.type() != 0:
            return
            
        testId = str(selectedItem.text(COL_ID))
        modelFile = self.dataModel.getTestFile( testId )
        
        fileModel = modelFile["file"]
        
        prjsList = []
        for prj in self.iRepo.remote().projects:
            prjsList.append(prj["name"])
        newPrj, ok = QInputDialog.getItem (self, "Project",  "Select the new project:", prjsList, 0, False)
        if ok:
        
            newFile = "%s:%s" % (newPrj, fileModel.split(":", 1)[1] )
            self.dataModel.updateTestFileOnly( testId, newFile ) 
            
            tsname = newFile.rsplit(".", 1) # remove extension file before display
            
            if not len(selectedItem.text(COL_ALIAS)): selectedItem.setText(COL_NAME, tsname[0])
            selectedItem.setToolTip(COL_NAME, tsname[0])
                
            self.resizeColumns()
            self.setModify()
            
    def refreshContent(self):
        """
        Refresh content
        """
        self.updateStatsTestPlan()
        
    def insertAbove(self):
        """
        Insert item above
        """
        if self.itemCurrent is not None:
            self.addTestFile( insertTest=RCI.ACTION_INSERT_AFTER)
            
        # refresh stats
        self.updateStatsTestPlan()

    def insertBelow(self):
        """
        Insert item below
        """
        if self.itemCurrent is not None:
            self.addTestFile( insertTest=RCI.ACTION_INSERT_BELOW)
            
        # refresh stats
        self.updateStatsTestPlan()

    def checkAll(self):
        """
        Check all items
        """
        if self.allItemsEnabled:
            self.allItemsEnabled = False
            self.enableAllTests(itmParent=self.tpRoot, state=0) # disable
        else:
            self.allItemsEnabled = True
            self.enableAllTests(itmParent=self.tpRoot, state=2) # enable
        
        # refresh stats
        self.updateStatsTestPlan()

    def enableAllTests(self, itmParent, state):
        """
        Enable all tests
        """
        for i in xrange(itmParent.childCount()):
            itmChild = itmParent.child(i)
            itmChild.setCheckState (COL_ENABLE, state )
            self.updateFontItem( itmChild )
            if state == 0: # disable
                itmChild.setText(COL_CONDITION_BEGIN, self.CONDITION_DONT)
                itmChild.setText(COL_RESULT, self.CONDITION_PARENTHESE)
                itmChild.setText(COL_CONDITION_END,  "")
                self.updateFontItem( itmChild, strike=True )
            if state ==  2: # enable
                itmChild.setText(COL_CONDITION_BEGIN, "")
                self.updateFontItem( itmChild )
                if itmChild.childCount():
                    itmChild.setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
                    itmChild.setText(COL_RESULT, self.CONDITION_OK)
                    itmChild.setText(COL_CONDITION_END, self.CONDITION_THEN)
                    self.updateFontItem(itmChild)

            if itmChild.childCount():
                self.enableAllTests(itmParent=itmChild, state=state)
                
        # refresh stats
        self.updateStatsTestPlan()
        
    def disableTest(self):
        """
        Disable test
        """
        for testSelected in self.tp.selectedItems():
            if testSelected.type() != 0:
                continue
            testSelected.setCheckState (COL_ENABLE, 0 )
        # refresh stats
        self.updateStatsTestPlan()

    def enableTest(self):
        """
        Enable test
        """
        for testSelected in self.tp.selectedItems():
            if testSelected.type() != 0:
                continue
            testSelected.setCheckState (COL_ENABLE, 2 )
            
        # refresh stats
        self.updateStatsTestPlan()
        
    def addColor(self, color):
        """
        Add color to the item
        """
        for testSelected in self.tp.selectedItems():
            if testSelected.type() != 0:
                continue
            qLabel = QLabel('')
            if color == "transparent":
                testSelected.setBackground (COL_NAME, QBrush(QColor(Qt.transparent)) )
                qLabel.setStyleSheet("QLabel { background-color : %s; margin: 5px 10px 5px 10px; border: 1px solid grey;}" % color)
            else:
                qLabel.setStyleSheet("QLabel { background-color : %s; margin: 5px 10px 5px 10px; border: 1px solid grey;}" % color)
                self.tp.setItemWidget(testSelected, COL_TAG_COLOR, qLabel )
            
                qcolor = QColor(color) 
                qcolor.setAlpha( int( Settings.instance().readValue( key = 'TestPlan/color-transparent' ) ) )
                testSelected.setBackground (COL_NAME, QBrush(qcolor) )
                
            self.setModify()
            self.dataModel.updateTestFileColor( str(testSelected.text(COL_ID)), color ) 

    def addWhiteColor(self):
        """
        Add white color
        """
        self.addColor(color="transparent")

    def addPurpleColor(self):
        """
        Add gray color
        """
        self.addColor(color="#DBADFF")

    def addOrangeColor(self):
        """
        Add gray color
        """
        self.addColor(color="orange")

    def addYellowColor(self):
        """
        Add yellow color
        """
        self.addColor(color="#FDFFBD")

    def addGrayColor(self):
        """
        Add gray color
        """
        self.addColor(color="gray")

    def addMagentaColor(self):
        """
        Add magenta color
        """
        self.addColor(color="magenta")

    def addCyanColor(self):
        """
        Add cyan color
        """
        self.addColor(color="cyan")

    def addBlueColor(self):
        """
        Add blue color
        """
        self.addColor(color="#C1EEFF")

    def addGreenColor(self):
        """
        Add green color
        """
        self.addColor(color="#D4FFAF")

    def addRedColor(self):
        """
        Add red color
        """
        self.addColor(color="#FF5B61")

    def toggleExpandAll(self):
        """
        Toggle expand all
        """
        if self.itemsExpanded:
            self.collapseAllItems()
        else:
            self.expandAllItems()

    def moveUpTestFile(self):
        """
        Move up the test file
        """
        selectedItems  = self.tp.selectedItems()
        if len(selectedItems) > 1: return
        
        selectedItem  = selectedItems[0]
        if selectedItem.type() != 0: return
        
        # return if item has child 
        if selectedItem.childCount(): return
        
        # find the previous item
        itemPrevious = self.tp.itemAbove(selectedItem)
        if itemPrevious is None: return
        
        # get id
        previousId = int(itemPrevious.text(COL_ID))
        if previousId == 0: return
        previousModel = self.dataModel.getTestFile( str(previousId) )
        
        testId = str(selectedItem.text(COL_ID))
        testModel = self.dataModel.getTestFile( testId )
        
        # find the same parent
        noItem = False
        while str(previousModel['parent']) != str(testModel['parent']):
            itemPrevious = self.tp.itemAbove(itemPrevious)
            if itemPrevious is None:
                noItem = True
                break
            previousId = int(itemPrevious.text(COL_ID))
            if previousId == 0: 
                noItem=True
                return
            previousModel = self.dataModel.getTestFile( str(previousId) )

        if noItem: return

        # cut the file and paste as child
        self.cutTestFile()
        self.pasteTestFileAbove(parentId=previousId)
        
    def moveDownTestFile(self):
        """
        Move down the test file
        """
        selectedItems  = self.tp.selectedItems()
        if len(selectedItems) > 1: return
        
        selectedItem  = selectedItems[0]
        if selectedItem.type() != 0: return
        
        # return if item has child 
        if selectedItem.childCount(): return
        
        # find the previous item
        itemAfter = self.tp.itemBelow(selectedItem)
        if itemAfter is None: return
        
        # get id
        afterId = int(itemAfter.text(COL_ID))
        afterModel = self.dataModel.getTestFile( str(afterId) )
        
        testId = str(selectedItem.text(COL_ID))
        testModel = self.dataModel.getTestFile( testId )
        
        if testModel['parent'] != afterModel['parent']: return

        # cut the file and paste as child
        self.cutTestFile()
        self.pasteTestFileBelow(parentId=afterId)
        
    def moveLeftTestFile(self):
        """
        Move left the test file
        """
        if self.testGlobal: return
        
        selectedItems  = self.tp.selectedItems()
        if len(selectedItems) > 1: return
        
        selectedItem  = selectedItems[0]
        if selectedItem.type() != 0: return
        
        # return if item has child 
        if selectedItem.childCount(): return
        
        testId = str(selectedItem.text(COL_ID))
        testModel = self.dataModel.getTestFile( testId )
        if str(testModel['parent']) == '0': return
        
        # cut the file and paste as child
        self.cutTestFile()
        self.pasteTestFileBelow(parentId=testModel['parent'])
        
    def moveRightTestFile(self):
        """
        Move right the test file
        """
        if self.testGlobal: return
        
        selectedItems  = self.tp.selectedItems()
        if len(selectedItems) > 1: return
        
        selectedItem  = selectedItems[0]
        if selectedItem.type() != 0: return

        # return if item has child 
        if selectedItem.childCount(): return
        
        # find the previous item
        itemPrevious = self.tp.itemAbove(selectedItem)
        if itemPrevious is None: return
        
        # get the previous id
        testId = str(selectedItem.text(COL_ID))
        testModel = self.dataModel.getTestFile( testId )

        previousId = int(itemPrevious.text(COL_ID))
        previousModel = self.dataModel.getTestFile( str(previousId) )
        if previousId == 0: return
        
        # find the same parent
        noItem = False
        while str(previousModel['parent']) != str(testModel['parent']):
            itemPrevious = self.tp.itemAbove(itemPrevious)
            if itemPrevious is None:
                noItem = True
                break
            previousId = int(itemPrevious.text(COL_ID))
            if previousId == 0: 
                noItem=True
                return
            previousModel = self.dataModel.getTestFile( str(previousId) )

        if noItem: return
        if str(testModel['parent']) == str(previousId): return

        # cut the file and paste as child
        self.cutTestFile()
        self.pasteTestFileChild(parentId=previousId)
        
    def mergeTestProperties(self):
        """
        Merge test properties
        """
        self.reloadTestProperties(mergeProperties=True)
        
    def clearAllTestProperties(self):
        """
        Clear all test properties
        """
        properties =  self.dataModel.cleartAllTestParameters()
        
        # update the view
        self.setModify()
        self.viewer().PropertiesChanged.emit( properties, False )

    def clearTestProperties(self):
        """
        Clear all test properties
        """
        if self.itemCurrent is None:
            return

        # update the file model
        properties = self.dataModel.cleartTestParameters(itemId=str(self.itemCurrent.text(COL_ID)))
        
        # update the view
        self.setModify()
        self.viewer().PropertiesChanged.emit( properties, False )

    def reloadTestProperties(self, mergeProperties=False):
        """
        Reload the test properties
        """
        answer = QMessageBox.question(self,  self.tr("Reload"),  self.tr("Are you sure to reload test properties from the original test?"), 
                                        QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            if self.itemCurrent is not None:
                if str(self.itemCurrent.text(COL_REPO)) == FROM_LOCAL_REPO or str(self.itemCurrent.text(COL_REPO)) == FROM_LOCAL_REPO_OLD \
                        or str(self.itemCurrent.text(COL_REPO)) == FROM_OTHER or str(self.itemCurrent.text(COL_REPO)) == FROM_HDD:
                    # local file
                    absPath = None
                    if str(self.itemCurrent.text(COL_REPO)) == FROM_LOCAL_REPO or str(self.itemCurrent.text(COL_REPO)) == FROM_LOCAL_REPO_OLD:
                        self.localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
                        if self.localConfigured != "Undefined":
                            absPath = "%s\%s" % (self.localConfigured, self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['file'] ) 
                        else:
                            QMessageBox.information(self, self.tr("Information") , self.tr("Local repository not configured.") )
                    if str(self.itemCurrent.text(COL_REPO)) == FROM_OTHER or str(self.itemCurrent.text(COL_REPO)) == FROM_HDD:
                        absPath = self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['file']
                    if absPath is not None:
                        # open the file
                        if not os.path.exists( absPath ):
                            QMessageBox.warning(self, self.tr("Information") , self.tr("This file does not exist!") )
                        else:
                            if self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['extension'] == TestSuite.TYPE:
                                doc = FileModelTestSuite.DataModel()
                            if self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['extension'] == TYPE:
                                doc = FileModelTestPlan.DataModel()
                            if self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['extension'] == TestUnit.TYPE:
                                doc = FileModelTestUnit.DataModel()
                            if self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['extension'] == TestAbstract.TYPE:
                                doc = FileModelTestAbstract.DataModel()
                            res = doc.load( absPath = absPath )
                            if not res:
                                QMessageBox.critical(self, self.tr("Open") , self.tr("Corrupted file") )
                                return
                            properties =  copy.deepcopy(doc.properties)

                            self.dataModel.updateTestFileProperties(itemId=str(self.itemCurrent.text(COL_ID)), 
                                                                    properties=properties['properties'])
                            self.setModify()

                            self.viewer().PropertiesChanged.emit( properties['properties'], False )
                
                # load from remote
                elif str(self.itemCurrent.text(COL_REPO)) == FROM_REMOTE_REPO:
                    if RCI.instance().isAuthenticated:
                        absPath = self.dataModel.getTestFile(self.itemCurrent.text(COL_ID) )['file']
                        # get projectid
                        try:
                            prjName, absPath = absPath.split(':', 1)
                            prjId = self.iRepo.remote().getProjectId(project=prjName)
                        except Exception as e:
                            prjId=0
                        actionId = RCI.ACTION_RELOAD_PARAMS
                        if mergeProperties:
                            actionId = RCI.ACTION_MERGE_PARAMS
                        if self.testGlobal:
                            RCI.instance().openFileTests(projectId=int(projectId), filePath=absPath, 
                                                         ignoreLock=False, readOnly=False, 
                                                         customParam=int(self.itemCurrent.text(COL_ID)), 
                                                         actionId=RCI.ACTION_UPDATE_PATH, destinationId=RCI.FOR_DEST_TG)
                        else:
                            RCI.instance().openFileTests(projectId=int(projectId), filePath=absPath, 
                                                         ignoreLock=False, readOnly=False, 
                                                         customParam=int(self.itemCurrent.text(COL_ID)), 
                                                         actionId=RCI.ACTION_UPDATE_PATH, destinationId=RCI.FOR_DEST_TP)
                    else:
                        QMessageBox.information(self, self.tr("Information") , self.tr("Connect to the server first.") )
                else:
                    raise Exception("[WTestPlan][reloadtestproperties] test type unknown: %s" % self.itemCurrent.text(COL_REPO) )
        
    def openAllTestFile(self):
        """
        Open all test files
        """
        testfiles = self.dataModel.testplan['testplan']['testfile']
        for  tf in testfiles:
            if tf['type'] == 'remote':
                self.openFromRemote(absPath=tf['file'])

    def openTestFile(self):
        """
        Open the current test file 
        """ 
        for testSelected in self.tp.selectedItems():
            if testSelected.type() != 0:
                continue
            if str(testSelected.text(COL_REPO)) == FROM_LOCAL_REPO or str(testSelected.text(COL_REPO)) == FROM_LOCAL_REPO_OLD \
                or str(testSelected.text(COL_REPO)) == FROM_OTHER or str(testSelected.text(COL_REPO)) == FROM_HDD:
                # local file
                absPath = None
                if str(testSelected.text(COL_REPO)) == FROM_LOCAL_REPO or str(testSelected.text(COL_REPO)) == FROM_LOCAL_REPO_OLD:
                    self.localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
                    if self.localConfigured != "Undefined":
                        absPath = "%s\%s" % (self.localConfigured, self.dataModel.getTestFile(testSelected.text(COL_ID) )['file'] ) 
                    else:
                        QMessageBox.information(self, self.tr("Information") , self.tr("Local repository not configured.") )
                if str(testSelected.text(COL_REPO)) == FROM_OTHER or str(testSelected.text(COL_REPO)) == FROM_HDD:
                    absPath = self.dataModel.getTestFile(testSelected.text(COL_ID) )['file']
                if absPath is not None:
                    try:
                        # separate path and filename
                        tmp = str(absPath).rsplit("\\", 1)
                        path = tmp[0]
                        filename = tmp[1].rsplit(".", 1)[0]
                        extension = self.dataModel.getTestFile(testSelected.text(COL_ID) )['extension']
                    except Exception as e:
                        self.error( 'unable to parse filename: %s' % e)
                        return
                    # open the file
                    if not os.path.exists( absPath ):
                        QMessageBox.warning(self, self.tr("Information") , self.tr("This file does not exist!") )
                    else:
                        repoDest = RCI.REPO_UNDEFINED
                        if str(testSelected.text(COL_REPO)) == FROM_LOCAL_REPO or str(testSelected.text(COL_REPO)) == FROM_LOCAL_REPO_OLD:
                            repoDest = RCI.REPO_TESTS_LOCAL
                        if str(testSelected.text(COL_REPO)) == FROM_OTHER or str(testSelected.text(COL_REPO)) == FROM_HDD:
                            repoDest = RCI.REPO_UNDEFINED
                        # the parent of the test plan is a the document viewer
                        self.parent.newTab( path = path, filename = filename, extension = extension, repoDest=repoDest )
            elif str(testSelected.text(COL_REPO)) == FROM_REMOTE_REPO:
                absPath = self.dataModel.getTestFile(testSelected.text(COL_ID) )['file']
                self.openFromRemote(absPath=absPath)
            else:
                raise Exception("[WTestPlan][openTestFile] test type unknown: %s" % testSelected.text(COL_REPO) )
    
    def openFromRemote(self, absPath):
        """
        Open the remote file
        """
        if RCI.instance().isAuthenticated:
            # get projectid
            try:
                prjName, absPath = absPath.split(':', 1)
                prjId = self.iRepo.remote().getProjectId(project=prjName)
            except Exception as e:
                prjId=0
            
            # web call
            RCI.instance().openFileTests(projectId=int(prjId), filePath=absPath)
        else:
            QMessageBox.information(self, self.tr("Information") , self.tr("Connect to the server first.") )
    
    def delItem(self):
        """
        Delete the current item
        """
        if self.itemCurrent is not None:
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+0: # root
                self.removeAllTestFiles()
            else:
                self.removeTestFile()

    def onCurrentItemChanged(self, currentItem, previousItem):
        """
        Called on current item selection changed
        """
        if previousItem is not None:
            if currentItem is not None:
                currentItem.setFlags(Qt.ItemIsEnabled |  Qt.ItemIsSelectable)
        if previousItem is not None:
            previousItem.setFlags(Qt.ItemIsEnabled |  Qt.ItemIsSelectable)

    def onTestFileChanged(self, item, col):
        """
        Called on test file changed 

        @param item:
        @type item:

        @param col:
        @type col:
        """
        if col == COL_ENABLE:  # column enable
            self.setModify()
            self.dataModel.updateTestFileEnable( str(item.text(COL_ID)), item.checkState(COL_ENABLE) ) 
            # Uncheck all childs if checkState is unchecked, otherwise re-check all
            if item.checkState(COL_ENABLE) == int(TS_DISABLED):
                item.setCheckState (COL_ENABLE, item.checkState(COL_ENABLE) )
                item.setText(COL_CONDITION_BEGIN, self.CONDITION_DONT)
                item.setText(COL_RESULT, self.CONDITION_PARENTHESE)
                item.setText(COL_CONDITION_END,  "")
                self.updateFontItem(item, strike=True)

                for i in xrange( item.childCount() ):
                    item.child(i).setCheckState (COL_ENABLE, item.checkState(COL_ENABLE) )
                    item.child(i).setText(COL_CONDITION_BEGIN, self.CONDITION_DONT)
                    item.child(i).setText(COL_RESULT, self.CONDITION_PARENTHESE)
                    item.child(i).setText(COL_CONDITION_END,  "")
                    self.updateFontItem(item.child(i), strike=True)

            # On check, all parents must be checked too
            if item.checkState(COL_ENABLE) == int(TS_ENABLED):
                item.setText(COL_CONDITION_BEGIN, "")
                self.updateFontItem(item)
                if item.childCount():
                    item.setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
                    item.setText(COL_RESULT, self.CONDITION_OK)
                    item.setText(COL_CONDITION_END, self.CONDITION_THEN)
                    self.updateFontItem(item)

                itm = item.parent()
                while itm.checkState(COL_ENABLE) != int(TS_ENABLED) and itm.type() == 0 :
                    itm.setCheckState (COL_ENABLE, int(TS_ENABLED) )
                    itm = itm.parent()

            # update stats
            self.updateStatsTestPlan()

        elif self.editActive:
            tsId = str(item.text(COL_ID))
            if tsId != "0": # not root node
                if col in [ COL_DESCR, COL_ALIAS ]: # column description
                    item.setFlags(Qt.ItemIsEnabled |  Qt.ItemIsSelectable)

                    self.setModify()
                    if col == COL_DESCR:
                        self.dataModel.updateTestFileDescr( str(item.text(COL_ID)), item.text(COL_DESCR) ) 
                    if col == COL_ALIAS:
                        aliasItem = item.text(COL_ALIAS)
                        item.setText(COL_ALIAS, self.safeAlias(alias=aliasItem) )
                        self.dataModel.updateTestFileAlias( str(item.text(COL_ID)), self.safeAlias(alias=aliasItem) ) 
                        self.resizeColumns()
                    self.editActive=False

    def safeAlias(self, alias):
        """
        Make alias safe
        """
        alias = alias.replace("'", "")
        return alias.upper()
        
    def onItemDoubleClicked(self, item, col):
        """
        Called on item double clicked

        @param item:
        @type item:

        @param col:
        @type col:
        """

        self.itemDoubleClicked=True    

        tsId = item.text(COL_ID)
        if tsId != "0": # not root node
            if col == COL_NAME:# column name, open testsuite file
                if QtHelper.str2bool( Settings.instance().readValue( key = 'TestPlan/open-doubleclick' ) ): 
                    self.openTestFile()
            if col in [ COL_DESCR, COL_ALIAS ]: # column description,  editDescription
                item.setFlags(Qt.ItemIsEnabled |Qt.ItemIsEditable |  Qt.ItemIsSelectable)
                self.editActive=True    

    def defaultLoad (self):
        """
        Default load
        """
        self.createRootItem()
        self.setReadOnly( readOnly=False )
        # BEGIN Issue 425
        self.tp.itemChanged.connect(self.onTestFileChanged)

    def load (self, content=None):
        """
        Load the testplan
        """

        if content is not None:
            res =  self.dataModel.load( rawData = content )
        else:
            absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
            res = self.dataModel.load( absPath = absPath )
        if res:
            testfiles = self.dataModel.testplan['testplan']['testfile']
            if len(testfiles) > 100:
                self.loaderDialog.setLoading()
                self.loaderDialog.show()
        
            self.constructTree()
        
            if len(testfiles) > 100:
                self.loaderDialog.done(0)
            
        return res

    def constructTree(self):
        """
        Construct tree
        """
        self.createRootItem()
        
        testfiles = self.dataModel.testplan['testplan']['testfile']
        maxId = 0
        i = 0
        for  tf in testfiles:
            if len(testfiles) > 100:
                self.loaderDialog.updateDataReadProgress(i, len(testfiles) ) 
            i+=1
            parent = self.getItem( parentId = tf['parent'] )
            if parent is not None:
                if not 'description' in tf: tf['description'] = ''
                if not 'alias' in tf: tf['alias'] = ''

                tfEnabled = False
                if 'enable' in tf: 
                    if tf['enable'] == TS_ENABLED: tfEnabled = True
                else:
                    tfEnabled = True

                tfExtension = TestSuite.TYPE
                if 'extension' in tf:  tfExtension = tf['extension']

                itmColor = ""
                if "color" in tf: itmColor = tf['color']

                itmCond = self.CONDITION_OK
                if "parent-condition" in tf: itmCond = tf["parent-condition"]
                
                if parent.type() == 0:
                    pEnabled = parent.checkState(COL_ENABLE)
                    if pEnabled:
                        parent.setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
                        if itmCond == FileModelTestPlan.IF_OK:
                            parent.setText(COL_RESULT, self.CONDITION_OK)
                        else:
                            parent.setText(COL_RESULT, self.CONDITION_KO)
                        parent.setText(COL_CONDITION_END, self.CONDITION_THEN)
                        parent.setText(COL_ACTION, self.CONDITION_RUN)
                    else:
                        parent.setText(COL_ACTION, self.CONDITION_RUN)
                        parent.setText(COL_CONDITION_BEGIN, self.CONDITION_DONT)
                    self.updateFontItem(parent, strike=not pEnabled)

                itemTs = QTreeWidgetItem(parent, 0)
                self.initItem(  itemTree=itemTs, txt=tf['file'], id=tf['id'], isRoot = False, fromType = tf['type'], 
                                description=tf['description'],  enabled=tfEnabled, extension=tfExtension, color=itmColor, 
                                testGlobal=False, alias=tf['alias'] )
                # begin issue 435
                if tfEnabled:
                    itemTs.setText(COL_ACTION, self.CONDITION_RUN)
                else:
                    itemTs.setText(COL_ACTION, self.CONDITION_RUN)
                    itemTs.setText(COL_CONDITION_BEGIN, self.CONDITION_DONT)
                # end issue 
                itemTs.setText(COL_RESULT, self.CONDITION_PARENTHESE)
                itemTs.setExpanded(True)
                self.updateFontItem(itemTree=itemTs, strike=not tfEnabled)

                # new in v17
                if tf["control"] == "missing":
                    itemTs.setIcon(COL_CONTROL, QIcon(":/warning.png") )
                else:
                    itemTs.setIcon(COL_CONTROL, QIcon())
                
                self.items.append( itemTs )

            if int(tf['id']) >= maxId:
                maxId = int(tf['id'])

        # update testplan stats
        self.updateStatsTestPlan()
        
        # connect signal
        self.tp.itemChanged.connect(self.onTestFileChanged)       
        
        self.tsId = maxId
        self.setReadOnly( readOnly=False )
        self.resizeColumns()

    def updateFontItem(self, itemTree, strike=False):
        """
        Update the font item
        """
        font = QFont()
        if str(itemTree.text(COL_CONDITION_BEGIN)) != self.CONDITION_DONT:
            font.setBold(True)
        else:
            font.setBold(False)
        itemTree.setFont(COL_CONDITION_BEGIN, font)
        itemTree.setFont(COL_CONDITION_END, font)

        font = QFont()
        font.setItalic(True)
        itemTree.setFont(COL_RESULT, font)
        itemTree.setFont(COL_ACTION, font)
        
        # new in v16
        font2 = QFont()
        if strike:
            font2.setStrikeOut (True)
            itemTree.setFont(COL_NAME, font2)
        else:
            font2.setStrikeOut (False)
            itemTree.setFont(COL_NAME, font2)
            
    def initItem(self, itemTree, txt, id, isRoot = False, fromType = 'local', description="", 
                        enabled=True, extension=TestSuite.TYPE, color="", testGlobal=False,
                        alias=""):
        """
        Init item
        """
        itemTree.setText(COL_NAME, txt)
        itemTree.setText(COL_ID, id)
        if testGlobal:
            itemTree.setIcon(COL_NAME, QIcon(":/tgx.png") )
        else:
            itemTree.setIcon(COL_NAME, QIcon(":/tpx.png") )
        if not isRoot:
            tsname = txt.rsplit(".", 1) # remove extension file before display
            itemTree.setText(COL_NAME, tsname[0])
            itemTree.setToolTip(COL_NAME, tsname[0])
            if extension == TestSuite.TYPE:
                itemTree.setIcon(COL_NAME, QIcon(":/%s.png" % TestSuite.TYPE) )
            elif extension == TYPE:
                itemTree.setIcon(COL_NAME, QIcon(":/%s.png" % TYPE) )
            elif extension == TestAbstract.TYPE:
                itemTree.setIcon(COL_NAME, QIcon(":/%s.png" % TestAbstract.TYPE) )
            else:
                itemTree.setIcon(COL_NAME, QIcon(":/%s.png" % TestUnit.TYPE) )
            
            if enabled:
                itemTree.setCheckState (COL_ENABLE, Qt.Checked )
            else:
                itemTree.setCheckState (COL_ENABLE, Qt.Unchecked )
                
            itemTree.setText(COL_REPO, fromType)
            
            # new in v16
            if len(alias): itemTree.setIcon(COL_NAME, QIcon(":/tc-name.png") )
            # end of new
            
            if sys.version_info > (3,): # py3 support
                itemTree.setText(COL_DESCR, description)
                itemTree.setToolTip(COL_DESCR, description)
                itemTree.setText(COL_ALIAS, alias)
                
                # new in v16
                if len(alias): itemTree.setText(COL_NAME,alias)
                # end of new
                
            else:
                if isinstance(description, str):
                    itemTree.setText(COL_DESCR, description.decode('utf-8') )
                    itemTree.setToolTip(COL_DESCR, description.decode('utf-8') )
                else:
                    itemTree.setText(COL_DESCR, description )
                    itemTree.setToolTip(COL_DESCR, description)
                    
                if isinstance(alias, str):
                    itemTree.setText(COL_ALIAS, alias.decode('utf-8') )
                else:
                    itemTree.setText(COL_ALIAS, alias )
                 
                # new in v16
                if len(alias):
                    if isinstance(alias, str):
                        itemTree.setText(COL_NAME, alias.decode('utf-8') )
                    else:
                        itemTree.setText(COL_NAME, alias )
                # end of new
                
            if color == "transparent":
                itemTree.setBackground (COL_NAME, QBrush(QColor(Qt.transparent)) )
            else:
                if len(color):
                    qcolor = QColor(color) 
                    qcolor.setAlpha(100)
                    itemTree.setBackground(COL_NAME, QBrush(qcolor) )
                
                    qLabel = QLabel('')
                    qLabel.setStyleSheet("QLabel { background-color : %s; margin: 5px 10px 5px 10px; border: 1px solid grey;}" % color)
                    self.tp.setItemWidget(itemTree, COL_TAG_COLOR, qLabel )
                else:
                    itemTree.setBackground(COL_NAME, QBrush(QColor(Qt.transparent)) )
                    
                    qLabel = QLabel('')
                    qLabel.setStyleSheet("QLabel { background-color : transparent; margin: 5px 10px 5px 10px; border: 1px solid grey;}")
                    self.tp.setItemWidget(itemTree, COL_TAG_COLOR, qLabel )
                
    def getItem (self, parentId):
        """
        Get item according to the parent id passed as argument

        @param parentId:
        @type parentId:
        """
        for itm in self.items:
            if str(itm.text(COL_ID)) == str(parentId):
                return itm
        return None

    def write (self, force = False):
        """
        Write the file

        @param force:
        @type force:
        """
        if not force:
            if not self.isModified():
                return False
        saved = self.dataModel.write( absPath='%s/%s.%s' % (self.path, self.filename, self.extension) )
        if saved:
            self.setUnmodify()
            return True
        else:
            self.path = None
            return None
    
    def getraw_encoded(self):
        """
        Return the data raw file encoded in base 64
        """
        return self.dataModel.getRaw()

    def onSelectionChanged(self):
        """
        On selection changed
        """
        self.itemDoubleClicked = False
        selectedTs = self.tp.selectedItems()
        if len(selectedTs) > 0:
            tsItem = selectedTs[0]
            self.loadProperties( tsItem, col = 0 )

            self.currentEdit.setText( tsItem.toolTip(COL_NAME) )
    
    def onItemClicked(self, item, col):
        """
        On item clicked
        """
        self.itemDoubleClicked = False
        if col == COL_ENABLE: 
            item.setFlags(Qt.ItemIsEnabled |Qt.ItemIsUserCheckable |  Qt.ItemIsSelectable)

    def loadProperties (self, item, col):
        """
        Load properties

        @param item:
        @type item:

        @param col:
        @type col:
        """
        # issue 418
        if self.itemDoubleClicked:
            self.itemDoubleClicked = False
            return
        # issue 418
        
        self.itemCurrent = item
        self.addAction.setEnabled(True)
        self.insertAction.setEnabled(True)

        
        
        if col == COL_ENABLE: 
            item.setFlags(Qt.ItemIsEnabled |Qt.ItemIsUserCheckable |  Qt.ItemIsSelectable)

        if self.itemCurrent.type() == 0:
            self.openAction.setEnabled(True)
            self.reloadAction.setEnabled(True)
            self.menuColor.setEnabled(True)
            if self.testGlobal: self.addAction.setEnabled(False) # new in v16
            self.insertBelowAction.setEnabled(True)
            self.insertAboveAction.setEnabled(True)
            self.updatePathAction.setEnabled(True)
            self.updateTcNameAction.setEnabled(True)
            self.updateProjectAction.setEnabled(True)
            self.updateAliasAction.setEnabled(True)
            # copy/paste actions
            self.copyAction.setEnabled(True)
            self.pasteAboveAction.setEnabled(True)
            self.pasteBelowAction.setEnabled(True)
            
            # new in v16
            if self.testGlobal:
                self.pasteChildAction.setEnabled(False) 
            else:
                self.pasteChildAction.setEnabled(True) 
            # end of new
            
            # params
            self.reloadParametersAction.setEnabled(True)
            self.mergeParametersAction.setEnabled(True)
            self.clearParametersAction.setEnabled(True)
        else:
            self.updatePathAction.setEnabled(False)
            self.updateTcNameAction.setEnabled(False)
            self.openAction.setEnabled(False)
            self.openAllAction.setEnabled(True)
            self.reloadAction.setEnabled(False)
            self.menuColor.setEnabled(False)
            self.insertBelowAction.setEnabled(False)
            self.insertAboveAction.setEnabled(False)
            self.updateProjectAction.setEnabled(False)
            self.updateAliasAction.setEnabled(False)
            # copy/paste actions
            self.copyAction.setEnabled(False)
            self.pasteAboveAction.setEnabled(False)
            self.pasteBelowAction.setEnabled(False)
            self.pasteChildAction.setEnabled(True)
            # params
            self.reloadParametersAction.setEnabled(False)
            self.mergeParametersAction.setEnabled(False)
            self.clearParametersAction.setEnabled(False)
        
        self.clearAllParametersAction.setEnabled(True)
            
        nbChild = self.itemCurrent.childCount()
        if nbChild > 0 :
            self.delAllAction.setEnabled(True)
            self.delAction.setEnabled(True)     
        else:
            if self.itemCurrent.type() == QTreeWidgetItem.UserType+0:
                self.delAction.setEnabled(False)
                self.delAllAction.setEnabled(True)
            else:
                self.delAllAction.setEnabled(False)
                self.delAction.setEnabled(True)     
        
        tsId = str(item.text(COL_ID))
        if tsId == "0":
            properties = self.dataModel.properties['properties']
            root = True
        else:
            properties = self.dataModel.getProperties(id=tsId)
            root = False

        self.viewer().PropertiesChanged.emit(properties, root )

    def onPopupMenu(self, pos):
        """
        Called on popup menu

        @param pos:
        @type pos:
        """
        item = self.tp.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.itemCurrent = item
            # main test
            if item.type() in [ QTreeWidgetItem.UserType+0 ]:
                self.menu.addAction( self.expandAllAction )
                self.menu.addAction( self.collapseAllAction )
                self.menu.addAction( self.refreshAction )
                self.menu.addSeparator()

                self.menu.addAction( self.insertAction )
                self.menu.addAction( self.openAllAction )
                self.menu.addAction( self.delAllAction )

                self.menu.addSeparator()
                self.menu.addAction( self.pasteAction )

            # all other
            if item.type() in [ 0 ]:
                self.menu.addAction( self.insertAction )
                self.menu.addAction( self.delAction )
                self.menu.addAction( self.openAction )
                self.menu.addSeparator()
                self.menu.addAction( self.updateAction )
                self.menu.addSeparator()
                self.menu.addAction( self.copyAction )
                self.menu.addAction( self.cutAction )
                self.menu.addAction( self.pasteAction )
                self.menu.addSeparator()
                
                self.menu.addAction( self.reloadAction )
                self.menu.addSeparator()

                self.menu.addAction( self.enableTestAction )
                self.menu.addAction( self.disableTestAction )
                
                self.menu.addSeparator()
                self.menu.addAction( self.moveLeftAction )
                self.menu.addAction( self.moveRightAction )
                self.menu.addAction( self.moveDownAction )
                self.menu.addAction( self.moveUpAction )
                self.menu.addSeparator()
                
                self.menu.addMenu( self.menuColor )
            self.menu.popup(self.mapToGlobal(pos))

    def createRootItem (self):
        """
        Create the root item of the tree
        """
        self.items = []
        title = self.dataModel.getName().upper()

        self.tpRoot = QTreeWidgetItem(self.tp, QTreeWidgetItem.UserType+0)
        self.initItem(  itemTree=self.tpRoot, txt=title, id=self.getTsId(), 
                        isRoot = True, testGlobal=self.testGlobal )
        self.tpRoot.setExpanded(True)
        self.tpRoot.setSelected(True)
        self.items.append( self.tpRoot )
        self.resizeColumns()

    def expandAllItems(self):
        """
        Expand all items
        """
        self.itemsExpanded=True
        self.tp.expandAll()
    
    def collapseAllItems(self):
        """
        Collapse all items
        """
        self.itemsExpanded=False
        self.tp.collapseAll()

    def copyTestFile(self):
        """
        Copy the test file
        """
        # self.copyTestsFile()
        
        selectedItem  = self.tp.selectedItems()[0]
        if selectedItem.type() != 0:
            return

        # retrieve test from model
        testId = str(selectedItem.text(COL_ID))
        modelFile = self.dataModel.getTestFile( testId )

        # copy to clipboard
        mime = QMimeData()
        mime.setData( self.__mime__ , QByteArray(pickle.dumps(modelFile)) )

        QApplication.clipboard().setMimeData(mime,QClipboard.Clipboard)

    def copyTestsFile(self):
        """
        """
        selectedItems  = self.tp.selectedItems()
        
        copyError = False
        testsModel = []
        for itm in selectedItems:
            if itm.type() != 0:
                copyError = True
                break
            modelFile = self.dataModel.getTestFile( str(itm.text(COL_ID)) )
            testsModel.append(modelFile)
            
        if copyError: return
        
        mime = QMimeData()
        mime.setData( self.__mime__ , QByteArray(pickle.dumps(testsModel)) )

        QApplication.clipboard().setMimeData(mime,QClipboard.Clipboard)
        
    def cutTestFile(self):
        """
        """
        # firstly copy the test
        self.copyTestFile()
        
        # remove them
        self.removeTestFile()
        
    def pasteTestFile(self):
        """
        Read test from clipboard
        """
        ret = None

        # read from clipboard
        mimeData = QApplication.clipboard().mimeData()
        if not mimeData.hasFormat(self.__mime__):
            return ret

        data = mimeData.data(self.__mime__)
        if not data:
            return ret
        try:
            ret = pickle.loads(data.data())
        except Exception as e:
            self.error( "unable to deserialize %s" % str(e) )
        return ret
    
    def onPasteTestFileChild(self):
        """
        Paste the test file as child 
        """
        self.pasteTestFileChild()

    def pasteTestsFileChild(self, parentId=None):
        """
        Paste the test file as child 
        """
        testsPaste = self.pasteTestFile()
        if testsPaste is None:
            return

        if parentId is None:
            parentId = self.itemCurrent.text(COL_ID)

        parentCondition = "0"
        parentItem = self.findParentId(testId=parentId)
        if parentItem.text(COL_RESULT) == self.CONDITION_KO:
            parentCondition = "1"

        for testPaste in testsPaste:
            self.addRemoteSubItem(
                                    pathFile='', nameFile='', extFile=testPaste['extension'], 
                                    contentFile='', project=0, 
                                    propertiesTest=testPaste, absPath=testPaste['file'],
                                    descriptionTest = testPaste['description'], 
                                    colorTest = testPaste['color'], parentCondition= parentCondition,
                                    aliasTest = testPaste['alias'], testParentId=int(parentId)
                                 )
     
    def pasteTestFileChild(self, parentId=None):
        """
        Paste the test file as child 
        """
        testPaste = self.pasteTestFile()
        if testPaste is None:
            return

        if parentId is None:
            parentId = self.itemCurrent.text(COL_ID)

        parentCondition = "0"
        parentItem = self.findParentId(testId=parentId)
        if parentItem.text(COL_RESULT) == self.CONDITION_KO:
            parentCondition = "1"
        
        self.addRemoteSubItem(
                                pathFile='', nameFile='', extFile=testPaste['extension'], 
                                contentFile='', project=0, 
                                propertiesTest=testPaste, absPath=testPaste['file'],
                                descriptionTest = testPaste['description'], colorTest = testPaste['color'], 
                                parentCondition= parentCondition, control=testPaste['control'],
                                aliasTest = testPaste['alias'], testParentId=int(parentId)
                             )
    
    def onPasteTestFileAbove(self):
        """
        Paste the test file as child 
        """
        self.pasteTestFileAbove()
        
    def pasteTestFileAbove(self, parentId=None):
        """
        Paste the test file above the selection
        """
        testPaste = self.pasteTestFile()
        if testPaste is None:
            return

        if parentId is None:
            parentId = self.itemCurrent.text(COL_ID)

        parentCondition = "0"
        parentItem = self.findParentId(testId=parentId)
        if parentItem.parent().text(COL_RESULT) == self.CONDITION_KO:
            parentCondition = "1"

        self.insertRemoteSubItem( 
                                    pathFile='', nameFile='', extFile=testPaste['extension'], 
                                    contentFile='', project=0,
                                    below=False, propertiesTest=testPaste, absPath=testPaste['file'],
                                    descriptionTest=testPaste['description'], colorTest=testPaste['color'],
                                    aliasTest=testPaste['alias'], testParentId=int(parentId), 
                                    parentCondition= parentCondition, control=testPaste['control']
                                 )
    
    def onPasteTestFileBelow(self):
        """
        Paste the test file as child 
        """
        self.pasteTestFileBelow()
        
    def pasteTestFileBelow(self, parentId=None):
        """
        Paste the test file below the selection
        """
        testPaste = self.pasteTestFile()

        if testPaste is None:
            return

        if parentId is None:
            parentId = self.itemCurrent.text(COL_ID)
            
        parentCondition = "0"
        parentItem = self.findParentId(testId=parentId)
        if parentItem.parent().text(COL_RESULT) == self.CONDITION_KO:
            parentCondition = "1"
        
        self.insertRemoteSubItem( 
                                    pathFile='', nameFile='', extFile=testPaste['extension'], 
                                    contentFile='', project=0,
                                    below=True, propertiesTest=testPaste, absPath=testPaste['file'],
                                    descriptionTest=testPaste['description'], colorTest=testPaste['color'],
                                    aliasTest = testPaste['alias'], testParentId=int(parentId), 
                                    parentCondition= parentCondition, control=testPaste['control']
                                 )

    def getAllSubItemsID(self, itmParent):
        """
        Enable all tests
        """
        IDs = []
        for i in xrange(itmParent.childCount()):
            itmChild = itmParent.child(i)
            IDs.append( str(itmChild.text(COL_ID)) )
            if itmChild.childCount():
                IDs.extend( self.getAllSubItemsID(itmParent=itmChild) )
        return IDs
        
    def removeTestFile (self):
        """
        Remove the test file ir more
        """
        for testSelected in self.tp.selectedItems():
            if testSelected.type() != 0:
                continue
                
            self.currentEdit.setText("")
            nbChild = testSelected.childCount()
            if nbChild > 0:
                answer = QMessageBox.question(self,  self.tr("Remove"),  self.tr("Do you want to remove all sub tests?"), 
                QMessageBox.Yes | QMessageBox.No)
                if answer == QMessageBox.Yes:

                    TestsID = self.getAllSubItemsID( itmParent=testSelected)
                    TestsID.append( str(testSelected.text(COL_ID)) )
                    
                    # delete the child
                    parentItem = testSelected.parent()
                    parentItem.removeChild( testSelected )
                    
                    # delete the test from the datamodel
                    for ID in TestsID:
                        self.dataModel.delTestFile( ID )
                    
                    # resize column
                    self.resizeColumns()
                    self.setModify()
                    
                    # update root test plan item
                    self.updateStatsTestPlan()
                    
                    # update condition
                    if parentItem.type() == ITEM_TEST:
                        nbChild = parentItem.childCount()
                        if nbChild == 0:
                            parentItem.setText(COL_CONDITION_BEGIN, "")
                            parentItem.setText(COL_CONDITION_END, "")
                            parentItem.setText(COL_ACTION, self.CONDITION_RUN)
                            parentItem.setText(COL_RESULT, self.CONDITION_PARENTHESE)

                    # finally disable del action if the parent is the root
                    if parentItem.type() == QTreeWidgetItem.UserType+0:
                        nbChild = parentItem.childCount()
                        if nbChild == 0:
                            self.delAction.setEnabled(False)
                            self.insertBelowAction.setEnabled(False)
                            self.insertAboveAction.setEnabled(False)
                            parentItem.setSelected(True)
                            
            else:
                # delete the test from the datamodel
                self.dataModel.delTestFile( str(testSelected.text(COL_ID)) )
                
                # remove item from the tree
                parentItem = testSelected.parent()
                parentItem.removeChild( testSelected )
                
                # resize column and set to modify
                self.resizeColumns()
                self.setModify()
                
                # update root test plan item
                self.updateStatsTestPlan()
                
                # update condition
                if parentItem.type() == ITEM_TEST:
                    nbChild = parentItem.childCount()
                    if nbChild == 0:
                        parentItem.setText(COL_CONDITION_BEGIN, "")
                        parentItem.setText(COL_CONDITION_END, "")
                        parentItem.setText(COL_ACTION, self.CONDITION_RUN)
                        parentItem.setText(COL_RESULT, self.CONDITION_PARENTHESE)

                # finally disable del action if the parent is the root
                if parentItem.type() == QTreeWidgetItem.UserType+0:
                    nbChild = parentItem.childCount()
                    if nbChild == 0:
                        self.delAction.setEnabled(False)
                        self.insertBelowAction.setEnabled(False)
                        self.insertAboveAction.setEnabled(False)
                        parentItem.setSelected(True)

    def removeAllTestFiles (self):
        """
        Remove all test files
        """
        answer = QMessageBox.question(self,  self.tr("Remove"),  self.tr("Do you want to remove all sub tests?"), 
            QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.tp.clear()
            self.currentEdit.setText("")
            self.dataModel.reset()
            self.tsId = -1
            self.createRootItem()
            self.setModify()
            # update root test plan item
            self.updateStatsTestPlan()

    def addTestFile(self, insertTest=False, updatePath=False):
        """
        Add a test file
        """
        self.localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )

        # import test from local
        if self.localConfigured != "Undefined":
            buttons = QMessageBox.Yes | QMessageBox.No
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("Import test from local repository") , buttons)
            if answer == QMessageBox.Yes:
                if self.testGlobal:
                    dialog = self.lRepo.SaveOpenToRepoDialog( self , "", type = self.lRepo.MODE_OPEN,
                                typeFile=[ TYPE, TestSuite.TYPE, TestUnit.TYPE, TestAbstract.TYPE ], multipleSelection=True )
                    dialog.hideFiles(hideTsx=False, hideTpx=False, hideTcx=True, hideTdx=True, hideTux=False, hidePng=True, hideTgx=True, hideTax=False)
                else:
                    dialog = self.lRepo.SaveOpenToRepoDialog( self , "", type = self.lRepo.MODE_OPEN,
                                typeFile=[ TestSuite.TYPE, TestUnit.TYPE, TestAbstract.TYPE ], multipleSelection=True )
                    dialog.hideFiles(hideTsx=False, hideTpx=True, hideTcx=True, hideTdx=True, hideTux=False, hidePng=True, hideTgx=True, hideTax=False)
                if dialog.exec_() == QDialog.Accepted:
                    if updatePath:
                        return (dialog.getSelection(), FROM_LOCAL_REPO, self.itemCurrent, None)
                    else:
                        self.addSubItems( files = dialog.getSelection() , fromType = FROM_LOCAL_REPO, parentTs=self.itemCurrent, insertTest=insertTest )
            
            else:
                if RCI.instance().isAuthenticated: # no then perhaps in remo repo if connected?
                    prjName = self.iRepo.remote().getCurrentProject()
                    prjId = self.iRepo.remote().getProjectId(project=prjName)
                    if self.testGlobal:
                        self.iRepo.remote().saveAs.getFilename(multipleSelection=True, project=prjName, type= [TYPE, TestSuite.TYPE, TestUnit.TYPE, TestAbstract.TYPE] )
                    else:
                        self.iRepo.remote().saveAs.getFilename(multipleSelection=True, project=prjName, type= [TestSuite.TYPE, TestUnit.TYPE, TestAbstract.TYPE] )
                    dialog = self.iRepo.remote().saveAs
                    if dialog.exec_() == QDialog.Accepted:
                        prjName = dialog.getProjectSelection()
                        prjId = self.iRepo.remote().getProjectId(project=prjName)
                        if updatePath:
                            return (dialog.getSelection(), FROM_REMOTE_REPO, self.itemCurrent, prjId)
                        else:
                            self.addSubItems( files = dialog.getSelection() , fromType = FROM_REMOTE_REPO, parentTs=self.itemCurrent, project=prjId, insertTest=insertTest)
                else:
                    QMessageBox.warning(self, self.tr("Import") , self.tr("Connect to the test center first!") )
        
        # import test from remote
        elif RCI.instance().isAuthenticated: # no then perhaps in remo repo if connected?
            prjName = self.iRepo.remote().getCurrentProject()
            prjId = self.iRepo.remote().getProjectId(project=prjName)
            if self.testGlobal:
                self.iRepo.remote().saveAs.getFilename(multipleSelection=True, project=prjName, 
                                                       type=[TYPE, TestSuite.TYPE, TestUnit.TYPE, TestAbstract.TYPE],
                                                       # dbr13 >>>
                                                       update_path=updatePath)
                                                       # dbr13 <<<
            else:
                self.iRepo.remote().saveAs.getFilename(multipleSelection=True, project=prjName, 
                                                       type=[TestSuite.TYPE, TestUnit.TYPE, TestAbstract.TYPE],
                                                       # dbr13 >>>
                                                       update_path=updatePath)
                                                       # dbr13 <<<
            dialog = self.iRepo.remote().saveAs
            if dialog.exec_() == QDialog.Accepted:
                prjName = dialog.getProjectSelection()
                prjId = self.iRepo.remote().getProjectId(project=prjName)
                # dbr13 >>>
                update_location_in_tests = dialog.update_location_in_tests.isChecked()
                # dbr13 <<<
                if updatePath:
                    # dbr13 >>> added - update_location
                    return (dialog.getSelection(), FROM_REMOTE_REPO, self.itemCurrent, prjId, update_location_in_tests)
                    # dbr13 <<<
                else:
                    self.addSubItems(files=dialog.getSelection(), fromType=FROM_REMOTE_REPO,
                                     parentTs=self.itemCurrent, project=prjId, insertTest=insertTest)
                    #  dbr13 >>>
                    self.updateProjectsAction.setEnabled(True)
                    #  dbr13 <<<
        else:
            QMessageBox.warning(self, self.tr("Import") , self.tr("Connect to the test center first!")     )   

    def addSubItems (self, files, fromType, parentTs=None, project=0, insertTest=False):
        """
        Add severals items
        """
        # reverse the list of files only for insert mode as below 
        if insertTest == RCI.ACTION_INSERT_BELOW:
            files.reverse()
            
        # memorize the insert options
        self.insertQueue = files
        self.insertDetails = (fromType, parentTs, project, insertTest)
        
        # insert the first one
        if len(self.insertQueue):
            f = self.insertQueue.pop(0)
            ret = self.addSubItem( info=f, fromType=fromType, parentTs=parentTs, project=project , insertTest=insertTest)

    def updateStatsTestPlan(self):
        """
        Update the statics of the test plan
        number of tests
        """
        if not self.tpRoot.childCount():
            self.tpRoot.setText(0, self.dataModel.getName().upper() )
        else:
            total = self.dataModel.getSorted()
            #keep test enable only
            enabled = []
            for i in total:
                if i['enable'] == "2":
                    enabled.append(i)

            nbTot = len(total)
            nbEn = len(enabled)
            if nbTot == 1:
                self.tpRoot.setText(0, "%s ( %s active / %s test )" % (self.dataModel.getName().upper(), nbEn, nbTot) )
            else:
                self.tpRoot.setText(0, "%s ( %s actives / %s tests )" % (self.dataModel.getName().upper(), nbEn, nbTot) )
                
        # update parent conditions
        self.updateAllParentConditions()
        
        self.resizeColumns()

    def getNbChild(self, itm):
        """
        Return the number of child according to the item passed as argument
        Recursive function
        """
        ret = itm.childCount()
        for i in xrange(itm.childCount()):
            ret += self.getNbChild(itm=itm.child(i))
        return ret

    def addSubItem (self, info, fromType, parentTs=None, project=0, insertTest=0 ):
        """
        Add sub item

        @param info:
        @rtype info:

        @param fromType:
        @rtype fromType:
        """
        # parse the argument info
        # in three variables ( path, filename and extension )
        extension = str(info).rsplit(".", 1)[1]
        tmp = str(info).rsplit("/", 1)
        if len(tmp) > 1 :
            path = tmp[0]
            filename = tmp[1].rsplit(".", 1)[0]
            absPath = '%s/%s.%s' % (path, filename, extension)
        else:
            path = ""
            filename = tmp[0].rsplit(".", 1)[0]
            absPath = '%s.%s' % ( filename, extension)

        if fromType == FROM_REMOTE_REPO:

            parentId = 0
            if parentTs is not None:
                parentId = int(parentTs.text(COL_ID))
                
            # go the to function insertRemoteSubItem to see the response to the following action
            if self.testGlobal:
                RCI.instance().openFileTests(projectId=int(project), filePath=absPath, ignoreLock=False, readOnly=False, 
                                             customParam=parentId, actionId=insertTest, destinationId=RCI.FOR_DEST_TG)
            else:
                RCI.instance().openFileTests(projectId=int(project), filePath=absPath, ignoreLock=False, readOnly=False, 
                                             customParam=parentId, actionId=insertTest, destinationId=RCI.FOR_DEST_TP)
        else:
        
            # this part is only to import a local file in the testplan
            
            # open the file from local
            if extension == TestSuite.TYPE:
                doc = FileModelTestSuite.DataModel()
            elif extension == TestAbstract.TYPE:
                doc = FileModelTestAbstract.DataModel()
            elif extension == TYPE:
                doc = FileModelTestPlan.DataModel()
            else:
                doc = FileModelTestUnit.DataModel()
            absPath = '%s/%s.%s' % (path, filename, extension)
            res = doc.load( absPath = absPath )
            if not res:
                QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted file") )
                return
            properties =  copy.deepcopy(doc.properties)
            del doc
            
            if fromType != FROM_OTHER:
                tmp = info.split(self.localConfigured)
                if len(tmp) > 1:
                    info =  tmp[1]
                else:
                    info = tmp[0]
            if info.startswith("/"): info = info[1:]
                
            if insertTest:
                below = False
                if insertTest == 1: below = True

                # retrieve index item from the tree
                idx = self.tp.indexFromItem(self.itemCurrent)
                idxParent = self.tp.indexFromItem(self.itemCurrent.parent())
            
                # get the model of the tree and insert the new item
                model = self.tp.model()
                newRow =  idx.row()
                if below: newRow = idx.row()+1
                ret = model.insertRow(newRow, parent=idxParent)
            
                # find the new item in the tree
                if below:
                    newIdx = idx.sibling( idx.row()+1, idx.column() )
                    ts = self.tp.itemFromIndex( newIdx )
                else:
                    ts = self.tp.itemAbove(self.itemCurrent)

                # fill the new item 
                tsId = self.getTsId()
                tsname = absPath.rsplit(".", 1) # remove extension file before display
                tsname_final = tsname[0]
                if fromType != FROM_OTHER:
                    tmp = tsname_final.split(self.localConfigured)
                    if len(tmp) > 1:
                        tsname_final =  tmp[1]
                    else:
                        tsname_final = tmp[0]
                if self.itemCurrent.parent().type() == QTreeWidgetItem.UserType+0:
                    tsEnabled = Qt.Checked
                else:
                    tsEnabled = self.itemCurrent.parent().checkState(COL_ENABLE)

                ts.setText(COL_ID, tsId)
                ts.setText(COL_NAME, tsname_final )
                ts.setToolTip(COL_NAME, tsname_final )
                ts.setText(COL_REPO, fromType )
                ts.setCheckState (COL_ENABLE, tsEnabled )
                if extension == TestSuite.TYPE:
                    ts.setIcon(COL_NAME, QIcon(":/%s.png" % TestSuite.TYPE) )
                elif extension == TestAbstract.TYPE:
                    ts.setIcon(COL_NAME, QIcon(":/%s.png" % TestAbstract.TYPE) )
                elif extension == TYPE:
                    ts.setIcon(COL_NAME, QIcon(":/%s.png" % TYPE) )
                else:
                    ts.setIcon(COL_NAME, QIcon(":/%s.png" % TestUnit.TYPE) )
                ts.setText(COL_DESCR, '' )
                ts.setToolTip(COL_DESCR, '' )
                ts.setText(COL_ALIAS, '' )

                if self.itemCurrent.parent().type() == 0:
                    self.itemCurrent.parent().setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
                    self.itemCurrent.parent().setText(COL_RESULT, self.CONDITION_OK)
                    self.itemCurrent.parent().setText(COL_CONDITION_END, self.CONDITION_THEN)
                    self.itemCurrent.parent().setText(COL_ACTION, self.CONDITION_RUN)
                    self.updateFontItem(self.itemCurrent.parent())
                ts.setText(COL_ACTION, self.CONDITION_RUN)
                ts.setText(COL_RESULT, self.CONDITION_PARENTHESE)
                self.updateFontItem(ts)

                # update the model file
                if below:
                    self.dataModel.insertAfterTestFile( fileName = "%s.%s" % (tsname_final, extension) , 
                                                        type = fromType, itemId = tsId,
                                                        parentId = str(self.itemCurrent.parent().text(COL_ID)), 
                                                        currentId=str(self.itemCurrent.text(COL_ID)),
                                                        properties = properties, enabled=tsEnabled, 
                                                        extension=extension)
                else:
                    self.dataModel.insertBeforeTestFile(    fileName = "%s.%s" % (tsname_final, extension) , 
                                                            type = fromType, itemId = tsId,
                                                            parentId = str(self.itemCurrent.parent().text(COL_ID)), 
                                                            currentId=str(self.itemCurrent.text(COL_ID)),
                                                            properties = properties, enabled=tsEnabled, 
                                                            extension=extension  )

            else:
                # Create tree widget item
                tsId = self.getTsId()

                tsEnabled = True
                if self.itemCurrent.type() == 0:
                    tsEnabled = self.itemCurrent.checkState(COL_ENABLE)

                parentItem = self.itemCurrent
                if parentTs is not None:
                    parentItem = parentTs
                if parentItem.type() == 0:
                    parentItem.setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
                    parentItem.setText(COL_RESULT, self.CONDITION_OK)
                    parentItem.setText(COL_CONDITION_END, self.CONDITION_THEN)
                    parentItem.setText(COL_ACTION, self.CONDITION_RUN)
                    self.updateFontItem(parentItem)

                ts = QTreeWidgetItem(parentItem, 0)
                self.initItem( itemTree=ts, txt=info, id=tsId, 
                               isRoot = False, fromType = fromType, 
                               enabled=tsEnabled, extension=extension)
                ts.setExpanded(True)
                ts.setText(COL_ACTION, self.CONDITION_RUN)
                ts.setText(COL_RESULT, self.CONDITION_PARENTHESE)
                self.updateFontItem(itemTree=ts)
                
                # Add test suite to data model
                tsEnabled = TS_DISABLED
                if tsEnabled: tsEnabled = TS_ENABLED
                self.dataModel.addTestFile( fileName = info , type = fromType, itemId = tsId,
                                             parentId = str(parentItem.text(COL_ID)), 
                                             properties = properties,
                                             enabled=tsEnabled, extension=extension )
            
            self.setModify()
            self.resizeColumns()
            
            self.resetSelection()
            ts.setSelected(True)
            
            self.items.append( ts )
            # update root test plan item
            self.updateStatsTestPlan()
        
        return True
        
    def onUpdateRemoteTestSubItem(self, pathFile, nameFile, extFile, contentFile, testId, project):
        """
        On update remote test
        """
        if self.itemCurrent is not None:
            # get project name
            prjName = self.iRepo.remote().getProjectName(project=project)
            if len(pathFile):
                absPath = '%s:%s/%s.%s' % (prjName, pathFile, nameFile, extFile)
            else:
                absPath = '%s:%s.%s' % (prjName, nameFile, extFile)

            # remove extension file before display
            tsname = absPath.rsplit(".", 1) 

            # update name
            self.itemCurrent.setText(COL_NAME, tsname[0] )
            self.itemCurrent.setToolTip(COL_NAME, tsname[0])
            self.itemCurrent.setIcon(COL_CONTROL, QIcon())
            
            if extFile == TestSuite.TYPE:
                self.itemCurrent.setIcon(COL_NAME, QIcon(":/%s.png" % TestSuite.TYPE) )
            elif extFile == TestAbstract.TYPE:
                self.itemCurrent.setIcon(COL_NAME, QIcon(":/%s.png" % TestAbstract.TYPE) )
            elif extFile == TYPE:
                self.itemCurrent.setIcon(COL_NAME, QIcon(":/%s.png" % TYPE) )
            else:
                self.itemCurrent.setIcon(COL_NAME, QIcon(":/%s.png" % TestUnit.TYPE) )

            if extFile == TestSuite.TYPE:
                doc = FileModelTestSuite.DataModel()
            elif extFile == TestAbstract.TYPE:
                doc = FileModelTestAbstract.DataModel()
            elif extFile == TestUnit.TYPE:
                doc = FileModelTestUnit.DataModel()
            else:
                doc = FileModelTestPlan.DataModel()
            properties =  copy.deepcopy(doc.properties)
            del doc

            # update datamodel
            self.dataModel.updateTestFile( itemId = str(testId), testName=absPath, 
                                            testExtension=extFile, 
                                            testDescriptions=properties['properties']['descriptions']['description'] )
            self.setModify()
            self.resizeColumns()

    def onUpdateRemotePropertiesSubItem(self, pathFile, nameFile, extFile, contentFile, 
                                            testId, project, mergeParameters=False):
        """
        Update the properties of the remote test
        """
        prjName = self.iRepo.remote().getProjectName(project=project)
        if pathFile != "":
            absPath = '%s:%s/%s.%s' % (prjName, pathFile, nameFile, extFile)
        else:
            absPath = '%s:%s.%s' % ( prjName, nameFile, extFile )
        if extFile == TestSuite.TYPE:
            doc = FileModelTestSuite.DataModel()
        elif extFile == TestUnit.TYPE:
            doc = FileModelTestUnit.DataModel()
        elif extFile == TestAbstract.TYPE:
            doc = FileModelTestAbstract.DataModel()
        else:
            doc = FileModelTestPlan.DataModel()
        res = doc.load(rawData=contentFile)
        if not res:
            QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted file") )
            return

        # copy properties
        properties =  copy.deepcopy(doc.properties)
        del doc
        
        # update the datamodel
        if mergeParameters:
            self.dataModel.mergeTestFileProperties(itemId=str(testId), properties=properties['properties'])
        else:
            self.dataModel.updateTestFileProperties(itemId=str(testId), properties=properties['properties'])
        self.setModify()

        self.viewer().PropertiesChanged.emit( properties['properties'], False )

    def insertRemoteSubItem(self, pathFile, nameFile, extFile, contentFile, project, 
                                  below=False, propertiesTest=None, absPath=None,
                                  descriptionTest="", colorTest="", aliasTest="", 
                                  testParentId=0, parentCondition="0", control=""):
        """
        Insert a remote test
        """

        # find the parent test according to the id
        currentItem = self.findParentId(testId=testParentId)
        if currentItem is None:
            QMessageBox.warning(self, self.tr("Insert test") , 
                                self.tr("The test parent with ID=%s not found!" % testParentId)     )   
            return

        if propertiesTest is not None:
            properties = {'properties': propertiesTest['properties'] }
        else:
            # read file content
            prjName = self.iRepo.remote().getProjectName(project=project)
            if pathFile != "":
                absPath = '%s:%s/%s.%s' % (prjName, pathFile, nameFile, extFile)
            else:
                absPath = '%s:%s.%s' % ( prjName, nameFile, extFile)
        
            if extFile == TestSuite.TYPE:
                doc = FileModelTestSuite.DataModel()
            elif extFile == TestAbstract.TYPE:
                doc = FileModelTestAbstract.DataModel()
            elif extFile == TYPE:
                doc = FileModelTestPlan.DataModel()
            else:
                doc = FileModelTestUnit.DataModel()
            res = doc.load(rawData=contentFile)
            if not res:
                QMessageBox.critical(self, self.tr("Open") , 
                                     self.tr("Unable to open! Corrupted file!") )
                return
            properties =  copy.deepcopy(doc.properties)
            del doc

        # retrieve index item from the tree
        idx = self.tp.indexFromItem(currentItem)
        idxParent = self.tp.indexFromItem(currentItem.parent())

        # get the model of the tree and insert the new item
        model = self.tp.model()
        newRow =  idx.row()
        if below: newRow = idx.row()+1
        ret = model.insertRow(newRow, parent=idxParent)

        # find the new item in the tree
        if below:
            newIdx = idx.sibling( idx.row()+1, idx.column() )
            itemNew = self.tp.itemFromIndex( newIdx )
            if currentItem.parent().text(COL_RESULT) == self.CONDITION_KO:
                parentCondition = "1"
        else:
            itemNew = self.tp.itemAbove(currentItem)
            if currentItem.parent().text(COL_RESULT) == self.CONDITION_KO:
                parentCondition = "1"

        # fill the new item 
        tsId = self.getTsId()
        tsname = absPath.rsplit(".", 1) # remove extension file before display

        if currentItem.parent().type() == QTreeWidgetItem.UserType+0:
            tsEnabled = Qt.Checked
        else:
            tsEnabled = currentItem.parent().checkState(COL_ENABLE)
        fromType = FROM_REMOTE_REPO

        itemNew.setText(COL_ID, tsId)
        itemNew.setText(COL_NAME, tsname[0] )
        itemNew.setToolTip(COL_NAME, tsname[0])
        itemNew.setText(COL_REPO, fromType )
        itemNew.setCheckState (COL_ENABLE, tsEnabled )

        if sys.version_info > (3,): # py3 support
            itemNew.setText(COL_DESCR, descriptionTest)
            itemNew.setToolTip(COL_DESCR, descriptionTest)
            itemNew.setText(COL_ALIAS, aliasTest)
        else:
            if isinstance(descriptionTest, str):
                itemNew.setText(COL_DESCR, descriptionTest.decode('utf-8') )
                itemNew.setToolTip(COL_DESCR, descriptionTest.decode('utf-8') )
            else:
                itemNew.setText(COL_DESCR, descriptionTest )
                itemNew.setToolTip(COL_DESCR, descriptionTest)
            if isinstance(aliasTest, str):
                itemNew.setText(COL_ALIAS, aliasTest.decode('utf-8') )
            else:
                itemNew.setText(COL_ALIAS, aliasTest )

        if extFile == TestSuite.TYPE:
            itemNew.setIcon(COL_NAME, QIcon(":/%s.png" % TestSuite.TYPE) )
        elif extFile == TestAbstract.TYPE:
            itemNew.setIcon(COL_NAME, QIcon(":/%s.png" % TestAbstract.TYPE) )
        elif extFile == TYPE:
            itemNew.setIcon(COL_NAME, QIcon(":/%s.png" % TYPE) )
        else:
            itemNew.setIcon(COL_NAME, QIcon(":/%s.png" % TestUnit.TYPE) )

        if len(aliasTest):
            if sys.version_info > (3,): # py3 support
                itemNew.setText(COL_NAME, aliasTest)
            else:
                if isinstance(aliasTest, str):
                    itemNew.setText(COL_NAME, aliasTest.decode('utf-8') )
                else:
                    itemNew.setText(COL_NAME, aliasTest )
            itemNew.setIcon(COL_NAME, QIcon(":/tc-name.png") )

        if len(colorTest):
            if colorTest == 'transparent':
                itemNew.setBackground (COL_NAME, QBrush(QColor(Qt.transparent)) )
            else:
                qcolor = QColor(colorTest) 
                qcolor.setAlpha(100)
                itemNew.setBackground (COL_NAME, QBrush(qcolor) )
            
            qLabel = QLabel('')
            qLabel.setStyleSheet("QLabel { background-color : %s; margin: 5px 10px 5px 10px; border: 1px solid grey;}" % colorTest)
            self.tp.setItemWidget(itemNew, COL_TAG_COLOR, qLabel )
        else:
            itemNew.setBackground (COL_NAME, QBrush(QColor(Qt.transparent)) )
            
            qLabel = QLabel('')
            qLabel.setStyleSheet("QLabel { background-color : transparent; margin: 5px 10px 5px 10px; border: 1px solid grey;}")
            self.tp.setItemWidget(itemNew, COL_TAG_COLOR, qLabel )

        if currentItem.parent().type() == 0:
            currentItem.parent().setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
            if parentCondition == FileModelTestPlan.IF_OK :
                currentItem.parent().setText(COL_RESULT, self.CONDITION_OK)
            else:
                currentItem.parent().setText(COL_RESULT, self.CONDITION_KO)
            currentItem.parent().setText(COL_CONDITION_END, self.CONDITION_THEN)
            currentItem.parent().setText(COL_ACTION, self.CONDITION_RUN)
            self.updateFontItem(currentItem.parent())
        itemNew.setText(COL_ACTION, self.CONDITION_RUN)
        itemNew.setText(COL_RESULT, self.CONDITION_PARENTHESE)
        
        if control == "missing":
            itemNew.setIcon(COL_CONTROL, QIcon(":/warning.png") )
        else:
            itemNew.setIcon(COL_CONTROL, QIcon())
            
        # update the model file
        if below:
            self.dataModel.insertAfterTestFile( fileName = absPath , type = fromType, itemId = tsId,
                                         parentId = str(currentItem.parent().text(COL_ID)), 
                                         currentId=str(currentItem.text(COL_ID)),
                                         properties = properties, enabled=tsEnabled, 
                                         extension=extFile, descr=descriptionTest, 
                                         color=colorTest, alias=aliasTest, parentCondition=parentCondition, 
                                         control=control)
        else:
            self.dataModel.insertBeforeTestFile( fileName = absPath , type = fromType, itemId = tsId,
                                         parentId = str(currentItem.parent().text(COL_ID)), 
                                         currentId=str(currentItem.text(COL_ID)),
                                         properties = properties, enabled=tsEnabled, 
                                         extension=extFile, descr=descriptionTest, 
                                         color=colorTest, alias=aliasTest, parentCondition=parentCondition, 
                                         control=control)
                                         
        self.setModify()
        self.resizeColumns()
        
        self.resetSelection()
        itemNew.setSelected(True)

        self.items.append( itemNew )
        
        # update root test plan item
        self.updateStatsTestPlan()
        
        # more test to insert ?
        if len(self.insertQueue):
            f = self.insertQueue.pop(0)
            ret = self.addSubItem( info=f, fromType=self.insertDetails[0], 
                                   parentTs=self.insertDetails[1], 
                                   project=self.insertDetails[2] , 
                                   insertTest=self.insertDetails[3])
                                    
    def addRemoteSubItem(self, pathFile, nameFile, extFile, contentFile, project, 
                               propertiesTest=None, absPath=None, 
                               descriptionTest="", colorTest="", aliasTest="", 
                               testParentId=0, parentCondition="0", control=""):
        """
        Add remote test
        """  
        if propertiesTest is not None:
            properties = {'properties': propertiesTest['properties'] }
        else:
            prjName = self.iRepo.remote().getProjectName(project=project)
            if pathFile != "":
                absPath = '%s:%s/%s.%s' % (prjName, pathFile, nameFile, extFile)
            else:
                absPath = '%s:%s.%s' % ( prjName, nameFile, extFile)
            if extFile == TestSuite.TYPE:
                doc = FileModelTestSuite.DataModel()
            elif extFile == TestAbstract.TYPE:
                doc = FileModelTestAbstract.DataModel()
            elif extFile == TYPE:
                doc = FileModelTestPlan.DataModel()
            else:
                doc = FileModelTestUnit.DataModel()
            res = doc.load(rawData=contentFile)
            if not res:
                QMessageBox.critical(self, self.tr("Open Failed") , self.tr("Corrupted file") )
                return
            properties =  copy.deepcopy(doc.properties)
            del doc
        
        # add the item in the tree
        added = self.createTreeWidgetItem(properties=properties, pathFile=absPath, 
                                    fromType=FROM_REMOTE_REPO, extFile=extFile,
                                    descriptionTest=descriptionTest, colorTest=colorTest, aliasTest=aliasTest, 
                                    testParentId=testParentId, parentCondition=parentCondition, control=control ) 
        
        # more test to insert ?
        if len(self.insertQueue):
            f = self.insertQueue.pop(0)
            ret = self.addSubItem( info=f, fromType=self.insertDetails[0], parentTs=self.insertDetails[1], 
                                    project=self.insertDetails[2] , insertTest=self.insertDetails[3])
            
    def findParentId(self, testId):
        """
        """
        parentItem = None
        for i in xrange(self.tp.topLevelItemCount()):
            curItem = self.tp.topLevelItem(i)
            if int(testId) == int(curItem.text(COL_ID)):
                parentItem = curItem
                break
            if curItem.childCount():
                subParentItem = self.__findParentId(parentItem=curItem, testId=testId)
                if subParentItem is not None:
                    parentItem = subParentItem
                    break
        return parentItem
        
    def __findParentId(self, parentItem, testId):
        """
        """
        subParentItem = None
        for i in xrange(parentItem.childCount()):
            curItem = parentItem.child(i)
            if int(testId) == int(curItem.text(COL_ID)):
                subParentItem = curItem
                break
            if curItem.childCount():
                nextParentItem = self.__findParentId(parentItem=curItem, testId=testId)
                if nextParentItem is not None:
                    subParentItem = nextParentItem
                    break
        return subParentItem
        
    def createTreeWidgetItem(self, properties, pathFile, fromType, extFile=TestSuite.TYPE, descriptionTest="", 
                                    colorTest="", aliasTest="", testParentId=0, parentCondition="0", control="" ):
        """
        Create a item for the treewidget
        """
        # find the parent test according to the id
        parentItem = self.findParentId(testId=testParentId)
        if parentItem is None:
            QMessageBox.warning(self, self.tr("Add test") , 
                                self.tr("The test parent with ID=%s not found!" % testParentId)     ) 
            return

        # get a new test id
        tsId = self.getTsId()

        # parentItem = self.itemCurrent

        tsEnabled = True
        if parentItem.type() == 0:
            tsEnabled = parentItem.checkState(COL_ENABLE)
        
        if parentItem.type() == 0:
            parentItem.setText(COL_CONDITION_BEGIN, self.CONDITION_IF)
            
            if parentCondition == FileModelTestPlan.IF_OK:
                parentItem.setText(COL_RESULT, self.CONDITION_OK)
            else:
                parentItem.setText(COL_RESULT, self.CONDITION_KO)
                
            parentItem.setText(COL_CONDITION_END, self.CONDITION_THEN)
            parentItem.setText(COL_ACTION, self.CONDITION_RUN)
            parentItem.setExpanded(True)

        self.trace("testplan - create item, parent item id: %s" % parentItem.text(COL_ID))
        ts = QTreeWidgetItem(parentItem, 0)
        self.initItem(  
                        itemTree=ts, txt=pathFile, id=tsId, isRoot = False, fromType = fromType,
                        enabled=tsEnabled, extension=extFile, testGlobal=self.testGlobal,
                        description=descriptionTest, color=colorTest, alias=aliasTest
                      )
        ts.setExpanded(True)
        ts.setText(COL_ACTION, self.CONDITION_RUN)
        ts.setText(COL_RESULT, self.CONDITION_PARENTHESE)
        self.updateFontItem(itemTree=ts, strike=not tsEnabled)
        
        if control == "missing":
            ts.setIcon(COL_CONTROL, QIcon(":/warning.png") )
        else:
            ts.setIcon(COL_CONTROL, QIcon())
            
        # Add test suite to data model
        # BEGIN new in 3.0.0
        if tsEnabled:
            tsEnabled = TS_ENABLED
        else:
            tsEnabled = TS_DISABLED
        # END new in 3.0.0

        self.dataModel.addTestFile( 
                                    fileName = pathFile , type = fromType, itemId = tsId,
                                     parentId = str(parentItem.text(COL_ID)), properties = properties,
                                     enabled=tsEnabled, extension=extFile, descr=descriptionTest, color=colorTest,
                                     alias=aliasTest, parentCondition=parentCondition, control=control
                                  )

        self.setModify()
        
        self.resizeColumns()
        
        self.resetSelection()
        ts.setSelected(True)
        
        self.items.append( ts )
        
        # update root test plan item
        self.updateStatsTestPlan()
        
        return True

    def updateAllParentConditions(self):
        """
        Make sure all child are the good parent conditions according the column result of the parent
        """
        for i in xrange(self.tp.topLevelItemCount()):
            curItem = self.tp.topLevelItem(i)
            if curItem.childCount():
                self.__updateAllParentConditions( parentItem=curItem, parentCondition="0" )
                
    def __updateAllParentConditions(self, parentItem, parentCondition="0"):
        """
        """
        for i in xrange(parentItem.childCount()):
            curItem = parentItem.child(i)
            self.dataModel.updateTestFileParentCondition( itemId=str(curItem.text(COL_ID)), 
                                                          parentCondition=parentCondition )
            if curItem.childCount():
                if curItem.text(COL_RESULT) == self.CONDITION_OK:
                    newParentCondition = "0"
                else:
                    newParentCondition = "1"
                self.__updateAllParentConditions( parentItem=curItem, parentCondition=newParentCondition )    
    
    def getDataModelSorted (self):
        """
        Returns the data model sorted
        Deprecated function

        @return:
        @rtype:
        """
        ret = self.dataModel.getSorted()

        n = []
        for i in ret:
            if ( Settings.instance().readValue( key = 'TestPlan/export-all' ) == 'True' ):
                n.append(i)
            else:
                # only enabled tests
                if i['enable'] == "2":
                    n.append(i)
        return n

    def getDepth (self, item):
        """
        Return the depth according to the item passed as argument
        Deprecated function

        @param item:
        @type item:

        @return:
        @rtype:
        """
        itm = item
        depth = 0
        while itm.parent() is not None:
            itm = itm.parent()
            depth += 1
        return depth

    def resetSelection (self):
        """
        Unselects all items
        """
        selectedItem = self.tp.selectedItems()
        for itm in selectedItem:
            itm.setSelected(False)

    def reloadSelectedItem (self):
        """
        Reload the selected item
        Called from document viewer
        """
        selectedItem = self.tp.selectedItems()
        if len(selectedItem) == 0:
            self.tpRoot.setSelected(True)
        else:
            self.loadProperties( selectedItem[0], 0 )

    def resizeColumns (self):
        """
        Resite columns
        """
        self.tp.resizeColumnToContents(COL_NAME)
        self.tp.resizeColumnToContents(COL_ALIAS)