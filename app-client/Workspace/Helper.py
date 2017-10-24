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
Helper module
"""

import sys
import base64
try:
    import pickle 
except ImportError: # support python3
    import cPickle as pickle
import zlib

try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QTreeWidgetItem, QTreeWidget, QDrag, QTreeView, QWidget, QLabel, QFont, 
                            QTextEdit, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QGridLayout, 
                            QHBoxLayout, QCheckBox, QFileDialog, QMessageBox, QToolBar, QTabWidget, 
                            QIcon, QSplitter, QMenu, QDialog, QFrame)
    from PyQt4.QtCore import (QMimeData, Qt, pyqtSignal, QSize, QFile, QIODevice, QByteArray)
except ImportError:
    from PyQt5.QtGui import (QDrag, QFont, QIcon)
    from PyQt5.QtWidgets import (QTreeWidgetItem, QTreeWidget, QTreeView, QWidget, QLabel, 
                                QTextEdit, QVBoxLayout, QLineEdit, QComboBox, QPushButton, 
                                QGridLayout, QHBoxLayout, QCheckBox, QFileDialog, QMessageBox, 
                                QToolBar, QTabWidget, QSplitter, QMenu, QDialog, QFrame)
    from PyQt5.QtCore import (QMimeData, Qt, pyqtSignal, QSize, QFile, QIODevice, QByteArray)
    
import Settings
from Libs import QtHelper, Logger
import DefaultTemplates
import UserClientInterface as UCI


class Item(QTreeWidgetItem):
    """
    tree widget item
    """
    def __init__( self, data, parent = None, type = QTreeWidgetItem.UserType+0, icon=None,
                        hide=False, isDefault=False, isGeneric=False):
        """
        Constructor

        @param data: {'default-args': [['description', 'None']], 'args': ['expected', 'description'], 'type': 'method', 'name': 'addStep', 'desc': 'todo'}
        @type data:

        @param parent: 
        @type parent:

        @param type:  0=root
        @type type:

        @param icon:
        @type icon:

        @param hide:
        @type hide:
        """
        QTreeWidgetItem.__init__(self, parent, type)
        
        self.parent = parent
        self.itemData = data
        self.metadata = None
        self.docString = {}
        self.returnValue = False
        
        self.isGeneric = isGeneric
        self.isDefault = isDefault
        
        self.parseDocString()
        self.setMetadata()

        if isGeneric and isDefault and self.itemData['type'] in [ 'libraries', 'adapters' ]:
            self.setText(0, "%s (default)" % self.itemData['name'])
            self.setExpanded(True)
        else:  
            if isGeneric and self.itemData['type'] in [ 'libraries', 'adapters' ] :
                self.setText(0, "%s (generic)" % self.itemData['name'])
                self.setExpanded(True)
            elif isDefault and self.itemData['type'] in [ 'libraries', 'adapters' ] :
                self.setText(0, "%s (default)" % self.itemData['name'])
                self.setExpanded(True)
            else:
                self.setText(0, self.itemData['name'])

        if self.itemData['name'] in [ 'TestExecutor', 'TestInteroperability' ]:
            self.setExpanded(True)

        self.setToolTip(0, self.itemData['name'])
        if type == QTreeWidgetItem.UserType+1: # root
            self.setExpanded(True)

        if icon is not None:
            self.setIcon(0, icon)

        if hide:
            self.setHidden(hide)

    def getFullName(self):
        """
        Returns full name
        """

        if self.parent is not None:
            try:
                name = self.parent.itemData['name']
            except Exception as e:
                name = ''
        name += " > %s" % self.itemData['name']
        return name

    def setMetadata(self):
        """
        Set metadata

        self.metadata = [ test definition destination, test execution destination ]
        """
        # handle class 
        if  self.itemData['type'] == 'class':
            
            # handle exception: testcase from TestExecutor library, drag and drop of the testcase 
            # return the default associated template configured on the client
            if self.parent.itemData['name'] == 'TestExecutor':
                if self.itemData['name'] == 'TestCase'  : 
                    defaultTemplates = DefaultTemplates.Templates()
                    self.metadata = [defaultTemplates.getTestDefinition(), defaultTemplates.getTestExecution(), 
                                       defaultTemplates.getTestUnitDefinition() ]
                if self.itemData['name'] == 'BreakPoint'  : 
                    className = self.itemData['name']
                    self.metadata = [ '%s(self)' % (className) , '%s(self)' % (className), '%s(self)' % (className) ]
                    
            elif self.parent.itemData['name'] == 'TestReporting':
                if self.itemData['name'] == 'TestCases'  : 
                    parentClassName = self.parent.itemData['name']
                    className = self.itemData['name']
                    self.itemData['desc'] = ''
                    initItem = self.getInitFunction(parent=self)
                    if initItem is not None:
                        self.parseDocString(parent=initItem.itemData)
                        if 'desc' in initItem.itemData: # issue 105
                            self.itemData['desc'] = initItem.itemData['desc']
                        else:
                            self.itemData['desc'] = ''
                        methodName, methodArgs = self.getArgsValue( dat= initItem.itemData )
                    else:
                        methodArgs = ''
                    self.metadata = [ '@obj = %s.%s(%s)' % (parentClassName,className,methodArgs) , 
                                        '@obj = %s.%s(%s)' % (parentClassName,className,methodArgs) ]

                
            # handle exceptions: 
            elif self.parent.itemData['name'] == 'TestValidators' or self.parent.itemData['name'] == 'TestOperators' or \
                    self.parent.itemData['name'] == 'TestProperties' or self.parent.itemData['name'] == 'TestTemplates' or \
                        self.parent.itemData['name'] == 'SutAdapter' or self.parent.itemData['name'] == 'SutLibrary' or \
                            self.parent.itemData['name'] == 'TestManipulators' or self.parent.itemData['name'] == 'TestInteroperability' or \
                                self.parent.itemData['name'] == 'TestRepositories' :
                parentClassName = self.parent.itemData['name']
                className = self.itemData['name']
                self.itemData['desc'] = ''
                initItem = self.getInitFunction(parent=self)
                if initItem is not None:
                    self.parseDocString(parent=initItem.itemData)
                    if 'desc' in initItem.itemData: # issue 105
                        self.itemData['desc'] = initItem.itemData['desc']
                    else:
                        self.itemData['desc'] = ''
                    methodName, methodArgs = self.getArgsValue( dat= initItem.itemData )
                else:
                    methodArgs = ''
                self.metadata = [ '@obj = %s.%s(%s)' % (parentClassName,className,methodArgs) , 
                                    '@obj = %s.%s(%s)' % (parentClassName,className,methodArgs) ]

            else: 
                className = self.itemData['name']
                self.itemData['desc'] = ''
                initItem = self.getInitFunction(parent=self)
                if initItem is not None:
                    self.parseDocString(parent=initItem.itemData)
                    if 'desc' in initItem.itemData: # issue 105
                        self.itemData['desc'] = initItem.itemData['desc']
                    else:
                        self.itemData['desc'] = ''
                    methodName, methodArgs = self.getArgsValue( dat= initItem.itemData )
                else:
                    methodArgs = ''

                if self.isGeneric and not self.isDefault:
                    if self.parent.itemData['realname'].startswith("SutAdapters."):
                        __name = self.parent.itemData['realname'].split("SutAdapters.")[1]
                        self.metadata = [ '@obj = SutAdapters.Generic.%s.%s(%s)' % (__name, className,methodArgs) , '']
                    elif self.parent.itemData['realname'].startswith("SutLibraries."):
                        __name = self.parent.itemData['realname'].split("SutLibraries.")[1]
                        self.metadata = [ '@obj = SutLibraries.Generic.%s.%s(%s)' % (__name, className,methodArgs) , '']
                    else:
                        self.metadata = [ '@obj = %s.%s(%s)' % (self.parent.itemData['realname'], className,methodArgs) , '']
                else:
                    self.metadata = [ '@obj = %s.%s(%s)' % (self.parent.itemData['realname'], className,methodArgs) , '']
        
        # handle class methods
        elif self.itemData['type'] == 'method':
            methodName, methodArgs = self.getArgsValue( dat= self.itemData )
            # handle exception: testcase, step, cache
            if self.parent.itemData['name'] == 'TestCase':
                if not self.returnValue:
                    self.metadata = [ 'self.%s(%s)' % (methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = self.%s(%s)' % (methodName, methodArgs), '' ]

            elif self.parent.itemData['name'] == 'Step':
                if methodName == 'setFailed' or  methodName == 'setPassed' or  methodName == 'start' or  methodName == 'setSummary' \
                    or  methodName == 'setDescription' or  methodName == 'setExpected' or  methodName == 'setEnabled' \
                    or  methodName == 'setDisabled' or  methodName == 'getId' or  methodName == 'isEnabled'  :
                    self.metadata = [ '@obj.%s(%s)' % (methodName, methodArgs), '' ]
                else:
                    if not self.returnValue:
                        self.metadata = [ 'self.%s(%s)' % (methodName, methodArgs), '' ]
                    else:
                        self.metadata = [ '@obj = self.%s(%s)' % (methodName, methodArgs), '' ]
                        
            # new in v11            
            elif self.parent.itemData['name'] == 'Cache':
                if not self.returnValue:
                    self.metadata = [ '%s().%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s().%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            # end of new
                        
            # new in v11.2           
            elif self.parent.itemData['name'] == 'Time':
                if not self.returnValue:
                    self.metadata = [ '%s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            elif self.parent.itemData['name'] == 'Public':
                if not self.returnValue:
                    self.metadata = [ '%s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            elif self.parent.itemData['name'] == 'Private':
                if not self.returnValue:
                    self.metadata = [ '%s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            # end of new
            # new in v15
            elif self.parent.itemData['name'] == 'Interact':
                if not self.returnValue:
                    self.metadata = [ '%s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            elif self.parent.itemData['name'] == 'Trace':
                if not self.returnValue:
                    self.metadata = [ '%s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            # end of new
            # new in v18
            elif self.parent.itemData['name'] == 'Test':
                if not self.returnValue:
                    self.metadata = [ '%s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
                else:
                    self.metadata = [ '@obj = %s(self).%s(%s)' % (self.parent.itemData['name'], methodName, methodArgs), '' ]
            # end of new 
            else:
                if not self.returnValue:
                    self.metadata = [ '@obj.%s(%s)' % (methodName, methodArgs),  '@obj.%s(%s)' % (methodName, methodArgs) ]
                else:
                    self.metadata = [ '@obj = @obj.%s(%s)' % (methodName, methodArgs), '@obj = @obj.%s(%s)' % (methodName, methodArgs) ]
       
        elif self.itemData['type'] == 'function':
            methodName, methodArgs = self.getArgsValue( dat= self.itemData )
            if self.parent.itemData['name'] == 'TestExecutor':
                if methodName in [ 'wait' ] :
                    tpl = '%s(%s)' % ( methodName, methodArgs )
                    self.metadata = [ tpl, tpl ]
            elif self.parent.itemData['name'] == 'TestProperties':
                if methodName in [ 'get', 'parameter', 'description', 'input', 'output', 'inputs', 'excel'
                                    'outputs', 'setInput', 'setOutput', 'agent', 'agents', 'shared', 'running' ] :
                    tpl = '%s(%s)' % ( methodName, methodArgs )
                    self.metadata = [ tpl, tpl ]
            elif self.parent.itemData['name'] == 'TestTemplates':
                parentName = self.parent.itemData['name']
                if not self.returnValue:
                    self.metadata = [ '%s.%s(%s)' % (parentName, methodName, methodArgs),  '%s.%s(%s)' % (parentName, methodName, methodArgs) ]
                else:
                    self.metadata = [ '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs), '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs) ]
                    
            elif self.parent.itemData['name'] == 'SutAdapter':
                parentName = "SutAdapter"
                if not self.returnValue:
                    self.metadata = [ '%s.%s(%s)' % (parentName, methodName, methodArgs),  '%s.%s(%s)' % (parentName, methodName, methodArgs) ]
                else:
                    self.metadata = [ '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs), '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs) ]
                    
            elif self.parent.itemData['name'] == 'SutLibrary':
                parentName = "SutLibrary"
                if not self.returnValue:
                    self.metadata = [ '%s.%s(%s)' % (parentName, methodName, methodArgs),  '%s.%s(%s)' % (parentName, methodName, methodArgs) ]
                else:
                    self.metadata = [ '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs), '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs) ]
            
            elif self.parent.itemData['name'] == 'TestRepositories':
                parentName = "TestRepositories"
                if not self.returnValue:
                    self.metadata = [ '%s.%s(%s)' % (parentName, methodName, methodArgs),  '%s.%s(%s)' % (parentName, methodName, methodArgs) ]
                else:
                    self.metadata = [ '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs), '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs) ]
        
            else:
                parentName = self.parent.itemData['realname']
                if not self.returnValue:
                    self.metadata = [ '%s.%s(%s)' % (parentName, methodName, methodArgs),  '%s.%s(%s)' % (parentName, methodName, methodArgs) ]
                else:
                    self.metadata = [ '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs), '@obj = %s.%s(%s)' % (parentName, methodName, methodArgs) ]
        
        elif self.itemData['type'] == 'module':
            pass    
       
        elif self.itemData['type'] in [ 'package', 'package-libraries', 'package-adapters' ]:
            pass
       
        elif self.itemData['type'] in [ 'libraries', 'adapters' ]:
            pass
        
        else:
            print("set metadata, type not supported : %s" % self.itemData['type'])
    
    def parseDocString(self, parent=None):
        """
        Parse docstring

        @param parent:
        @type parent:
        """
        p = self.itemData
        if parent is not None:
            p = parent
        if 'desc' in p: 
            desc = p['desc'].strip()
            desc_splitted = desc.splitlines()
            paramName = None
            for line in desc_splitted:
                line = line.strip() 
                if line.startswith('@param '):
                    paramName = line.split(':', 1)[0].split('@param ')[1].strip()
                elif line.startswith('@type '):
                    paramType = line.split(':', 1)[1].strip()
                    if paramName is not None:
                        self.docString[paramName] = paramType
                elif line.startswith('@return'):
                    self.returnValue = True
                elif line.startswith('@rtype'):
                    self.returnValue = True
                else:   
                    pass

    def getInitFunction(self, parent):
        """
        Returns init function

        @param parent:
        @type parent:
        """
        ret = None
        for i in xrange(parent.childCount()):
            chld = parent.child(i)
            if chld.itemData['name'] == '__init__':
                ret = chld
                break
        return ret
    
    def getArgsValue(self, dat):
        """
        Returns args value

        @param dat:
        @type dat:
        """
        # get method name
        methodName = dat['name']
        methodArgs = ''
        # contruct arguments
        if not 'args' in dat:
            print('helper err - no args detected')
        else:
            for a in dat['args']:
                defarg = self.__getdefaultval(parent=dat, arg=a)
                if defarg is not None:
                    if a in self.docString:
                        if  self.docString[a].lower() in [ "strconstant" , "string" ]:
                            tpl= "%s='%s', " % (a,defarg )
                        else:
                            tpl = "%s=%s, " % (a,defarg )
                    else:
                        tpl = '%s=%s, ' % (a,defarg )
                    methodArgs += tpl
                else:
                    if not a in self.docString:
                        methodArgs += '%s=, ' % a
                    else:
                        if a == "parent" and self.docString[a] == "testcase":
                            methodArgs += '%s=self, ' % a
                        else:
                            methodArgs += '%s=@%s, ' % ( a, self.docString[a] )
        if methodArgs.endswith(', '):
            methodArgs = methodArgs[:-2]
        return methodName, methodArgs

    def __getdefaultval(self, parent,arg):
        """
        Returns default value

        @param parent:
        @type parent:

        @param arg:
        @type arg:
        """
        defarg = None
        if 'default-args' in parent:
            for d in parent['default-args']:
                k, v = d
                if k == arg:
                    defarg = v
        return defarg

class TreeWidgetHelper(QTreeWidget):
    """
    Tree widget for assistant
    """
    def __init__(self, parent=None):
        """
        Class constructor

        @param parent:
        @type parent:
        """
        QTreeWidget.__init__(self, parent)
        
        self.setExpandsOnDoubleClick(False)

    def startDrag(self, dropAction):
        """
        Start drag

        @param dropAction:
        @type dropAction:
        """
        itemsSelected = self.selectedItems()
        if itemsSelected:
            itemsSelected[0].setMetadata() # refresh metadata, perhaps testcase template has been updated ?
            if itemsSelected[0].metadata is not None:
                meta = QByteArray()
                meta.append( str(itemsSelected[0].metadata) )
                
                # create mime data object
                mime = QMimeData()
                mime.setData('application/x-%s-help-item' % Settings.instance().readValue( key = 'Common/acronym' ).lower(), 
                                meta )
                # start drag 
                drag = QDrag(self)
                drag.setMimeData(mime) 
                
                drag.exec_(Qt.CopyAction)

    def setSytleSheetTree(self):
        """
        Set the stylesheet of the tree
        """
        self.setStyleSheet ( """background-color: #EAEAEA;
                                        background-position: center;
                                        background-repeat: no-repeat;
                                        background-attachment: fixed;""" )

    def unsetSytleSheetTree(self):
        """
        Unset the stylesheet of the tree
        """
        self.setStyleSheet ( """background-color: #FFFFFF;""" )

    def mousePressEvent(self, event):
        """
        On mouse press
        """
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)

class QDoc(QWidget):
    """
    Doc widget
    """
    def __init__(self, parent):
        """
        Constructor
        """
        QWidget.__init__(self, parent)
        self.createWidgets()

    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.labelSelection = QLabel(self.tr('Documentations'))
        font = QFont()
        font.setBold(True)
        self.labelSelection.setFont(font)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setEnabled(False)
        self.setSytleSheetTextEdit()

        layoutDoc = QVBoxLayout()
        layoutDoc.addWidget( self.labelSelection )
        layoutDoc.addWidget( self.textEdit )
        layoutDoc.setContentsMargins(0,0,0,0)
        
        self.setLayout(layoutDoc)
    
    def setEnabled(self, en):
        """
        Set enabled
        """
        self.textEdit.setEnabled(en)

    def setText(self, text):
        """
        Set text
        """
        self.textEdit.setText(text)

    def setHtml(self, text):
        """
        Set test as html
        """
        self.textEdit.setHtml(text)

    def setSytleSheetTextEdit(self):
        """
        Set the stylesheet of the textedit
        """
        self.textEdit.setStyleSheet ( """background-color: #EAEAEA;
                                        background-image: url(:/main_logo.png);
                                        background-position: center;
                                        background-repeat: no-repeat;
                                        background-attachment: fixed;""" )

    def unsetSytleSheetTextEdit(self):
        """
        Unset the stylesheet of the textedit
        """
        self.textEdit.setStyleSheet ( """background-color: #EAEAEA;""" )

TAB_FRAMEWORK       = 0
TAB_ADAPTERS        = 1
TAB_LIBRARIES       = 2

class WsdlDialog(QtHelper.EnhancedQDialog):
    """
    Wsdl dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor
        """
        QtHelper.EnhancedQDialog.__init__(self, parent)
        self.name = self.tr("Adapter generator from WSDL")

        self.createDialog()
        self.createConnections()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( self.name )
        
        urlLabel = QLabel( "WSDL Url:" )
        self.urlLineEdit = QLineEdit()
        
        pkgLabel = QLabel( "Package version:" )
        self.pkgLineEdit = QComboBox(self)
        self.pkgLineEdit.addItems( Settings.instance().serverContext['adapters'].split(",") )
        
        fileLabel = QLabel( "WSDL+XSD File:" )
        self.fileLineEdit = QLineEdit()
        self.fileLineEdit.setEnabled(False)
        self.fileButton = QPushButton(self.tr("Browse..."))
        
        layout = QGridLayout()

        layout.addWidget(  urlLabel, 0, 0 )
        layout.addWidget(  self.urlLineEdit, 0, 1 )
        
        layoutFile = QHBoxLayout()

        layoutFile.addWidget(  self.fileLineEdit )
        layoutFile.addWidget(  self.fileButton )

        layout.addWidget(  fileLabel, 1, 0 )
        layout.addLayout(  layoutFile, 1, 1 )

        layout.addWidget(  pkgLabel, 2, 0 )
        layout.addWidget(  self.pkgLineEdit, 2, 1 )
        
        
        self.overwriteCheckBox = QCheckBox( "Overwrite adapter if already exists!")
        layout.addWidget(  self.overwriteCheckBox, 3, 1 )
        
        buttonLayout = QHBoxLayout()

        self.okButton = QPushButton(self.tr("OK"), self)
        self.cancelButton = QPushButton(self.tr("Cancel"), self)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        layout.addLayout(  buttonLayout, 4, 1 )

        
        layoutMain = QVBoxLayout()
        descr = [ 'Use this module to generate one adapter from the wsdl. ' ]
        descr.append('Provide the URL of the WSDL or the file him self.' )
        
        layoutMain.addWidget(QLabel( '\n'.join(descr) ))
        layoutMain.addLayout(layout)
        
        self.setLayout(layoutMain)
        
        self.setMinimumWidth(400)
        
        flags = Qt.WindowFlags()
        flags |= Qt.WindowCloseButtonHint
        flags |= Qt.MSWindowsFixedSizeDialogHint
        self.setWindowFlags(flags)
        
    def createConnections (self):
        """
        create qt connections
         * ok
         * cancel
        """
        self.okButton.clicked.connect( self.acceptClicked )
        self.cancelButton.clicked.connect( self.reject )
        self.fileButton.clicked.connect(self.getFile)
            
    def getFile (self):
        """
        Returns the path of the repository
        """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open WSDL file"),  '', "Files (*.*)")
        if fileName:
            self.fileLineEdit.setText(fileName)
            
    def acceptClicked (self):
        """
        Called on accept button
        """
        url = self.urlLineEdit.text()
        fileWsdl = self.fileLineEdit.text()
        if not len(url) and not len(fileWsdl):
            QMessageBox.information(self, self.tr("Wsdl Handler") , "Please to specify an url or file.")
        else:  
            if len(url):
                if not( str(url).startswith('http://') or str(url).startswith('https://') ):
                    QMessageBox.information(self, self.tr("Wsdl Handler") , "Please to specify http:// or https://")
                    return
            pkg = self.pkgLineEdit.currentText()
            if not len(pkg):
                QMessageBox.information(self, self.tr("Wsdl Handler") , "Please to specify the package version.")
            
            else:
                self.accept()
        
    def getParameters(self):
        """
        """
        url = self.urlLineEdit.text()
        fileWsdl = self.fileLineEdit.text()
        pkg = self.pkgLineEdit.currentText()
        if self.overwriteCheckBox.checkState():
            overwrite = True
        else:
            overwrite = False
        return (url, fileWsdl, pkg, overwrite)
        
class WHelper(QWidget, Logger.ClassLogger):
    """
    Assistant widget
    """
    HideAssistant = pyqtSignal() 
    ShowAssistant = pyqtSignal() 
    def __init__(self, parent=None):
        """
        Constructs WHelper widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.assistantData = []

        self.setMouseTracking(True)

        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.createToolbar()
   
    def enterEvent(self,event):
        """
        """
        self.ShowAssistant.emit()
    
    def leaveEvent(self,event):
        """
        """
        self.HideAssistant.emit()

    def createWidgets(self):
        """
        create qt widget
        """
        self.dockToolbar = QToolBar(self)

        self.masterTab = QTabWidget()
        self.masterTab.setTabPosition(QTabWidget.North)
        self.masterTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border

        self.areaTab = QTabWidget()
        self.areaTab.setTabPosition(QTabWidget.North)
        self.areaTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border
        
        self.extsTab = QTabWidget()
        self.extsTab.setTabPosition(QTabWidget.North)
        self.extsTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border

        self.helper = TreeWidgetHelper()
        self.helper.setSytleSheetTree()
        self.helper.setFocusPolicy( Qt.NoFocus )
        self.helper.setHeaderHidden(True)
        self.helper.setEnabled(False)
        self.helper.setDragEnabled(True)
        self.helper.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.helperInterop = TreeWidgetHelper()
        self.helperInterop.setSytleSheetTree()
        self.helperInterop.setFocusPolicy( Qt.NoFocus )
        self.helperInterop.setHeaderHidden(True)
        self.helperInterop.setEnabled(False)
        self.helperInterop.setDragEnabled(True)
        self.helperInterop.setContextMenuPolicy(Qt.CustomContextMenu)

        self.helperAdapters = TreeWidgetHelper()
        self.helperAdapters.setSytleSheetTree()
        self.helperAdapters.setFocusPolicy( Qt.NoFocus )
        self.helperAdapters.setHeaderHidden(True)
        self.helperAdapters.setEnabled(False)
        self.helperAdapters.setDragEnabled(True)
        self.helperAdapters.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.helperLibraries = TreeWidgetHelper()
        self.helperLibraries.setSytleSheetTree()
        self.helperLibraries.setFocusPolicy( Qt.NoFocus )
        self.helperLibraries.setHeaderHidden(True)
        self.helperLibraries.setEnabled(False)
        self.helperLibraries.setDragEnabled(True)
        self.helperLibraries.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.areaTab.addTab(self.helper, QIcon(":/processes.png"), "Framework")
        self.areaTab.addTab(self.helperInterop, QIcon(":/plugin.png"), "Interoperability")
        self.extsTab.addTab(self.helperAdapters, QIcon(":/adapters-help.png"), "Adapters")
        self.extsTab.addTab(self.helperLibraries, QIcon(":/libraries-help.png"), "Libraries")

        self.masterTab.addTab(self.areaTab, QIcon(":/main.png"), "Test Library")
        self.masterTab.addTab(self.extsTab, QIcon(":/adapters.png"), "SUT Extensions")
        
        # self.labelHelp = QLabel(self.tr("Drag and drop object or method in your test to add-it"))
        # font = QFont()
        # font.setItalic(True)
        # self.labelHelp.setFont(font)

        self.setMinimumWidth( 300 )
        
        self.textEdit = QDoc(parent=self)
        self.textEdit.setMaximumHeight  ( 300 )

        self.hSplitter = QSplitter(self)
        self.hSplitter.setOrientation(Qt.Vertical)

        frame = QFrame()
        layoutFrame = QVBoxLayout()
        layoutFrame.setContentsMargins(0,0,0,0)
        layoutFrame.addWidget(self.masterTab)
        layoutFrame.addWidget(self.dockToolbar)
        frame.setLayout(layoutFrame)
        
        
        # self.hSplitter.addLayout( subLayout )
        self.hSplitter.addWidget( frame )
        # self.hSplitter.addWidget(self.dockToolbar)
        self.hSplitter.addWidget( self.textEdit )
        self.hSplitter.setContentsMargins(0,0,0,0)
        
        layout = QVBoxLayout()
        # layout.addWidget(self.dockToolbar)
        # layout.addWidget(self.labelHelp)
        layout.addWidget(self.hSplitter)
        
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

    def createActions(self):
        """
        Create qt actions
        """
        self.expandSubtreeAction = QtHelper.createAction(self, self.tr("Expand subtree..."), self.expandSubtreeItem, 
                    icon = None, tip = self.tr('Expand subtree...') )
        self.expandAllAction = QtHelper.createAction(self, self.tr("Expand All..."), self.expandAllItems, 
                    icon = None, tip = self.tr('Expand All...') )
        self.collapseAllAction = QtHelper.createAction(self, self.tr("Collapse All..."), self.collapseAllItems, 
                    icon = None, tip = self.tr('Collapse All...') )
        self.reloadAllAction = QtHelper.createAction(self, self.tr("Reload"), self.reloadAll, 
                    icon =  QIcon(":/act-refresh.png"), tip = self.tr('Refresh') )
        self.rebuildCacheAction = QtHelper.createAction(self, self.tr("Rebuild documentations"), self.rebuild, 
                    icon = QIcon(":/generate-doc.png"), tip = self.tr('Rebuild') )
        self.generateAdaptersAction = QtHelper.createAction(self, self.tr("Packaging Adapters"), self.generateAdapters, 
                    icon = QIcon(":/generate-tar.png"), tip = self.tr('Packaging') )
        self.generateLibrariesAction = QtHelper.createAction(self, self.tr("Packaging Libraries"), self.generateLibraries, 
                    icon = QIcon(":/generate-tar.png"), tip = self.tr('Packaging') )
        self.generateAllAction = QtHelper.createAction(self, self.tr("Packaging all"), self.generateAll, 
                    icon = QIcon(":/generate-tar.png"), tip = self.tr('Packaging all adapters and libraries') )
        self.prepareAssistantAction = QtHelper.createAction(self, self.tr("Prepare Framework"), self.prepareAssistant, 
                    icon = QIcon(":/build.png"), tip = self.tr('Prepare framework') )
        self.generateAdapterWsdlAction = QtHelper.createAction(self, self.tr("Generate adapter from WSDL"), self.generateAdapterWSDL, 
                    icon = QIcon(":/api.png"), tip = self.tr('Generate adapter from WSDL') )
        self.setDefaultActionsValues()

    def createToolbar(self):
        """
        create qt toolbar
        """
        self.dockToolbar.setObjectName("toolbar")
        self.dockToolbar.addAction(self.reloadAllAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.prepareAssistantAction)
        self.dockToolbar.addAction(self.rebuildCacheAction)
        self.dockToolbar.addAction(self.generateAllAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.generateAdapterWsdlAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))
        
    def createConnections (self):
        """
        Create qt connections
        """
        self.helper.currentItemChanged.connect(self.currentItemChanged)
        self.helperInterop.currentItemChanged.connect(self.currentItemChanged)
        self.helperAdapters.currentItemChanged.connect(self.currentItemChanged)
        self.helperLibraries.currentItemChanged.connect(self.currentItemChanged)
 
    def setDefaultActionsValues (self):
        """
        Set default values for qt actions
        """
        self.masterTab.setEnabled(False)
        
        # self.labelHelp.setEnabled(False)
        self.reloadAllAction.setEnabled(False)
        self.rebuildCacheAction.setEnabled(False)
        self.expandSubtreeAction.setEnabled(False)
        self.expandAllAction.setEnabled(False)
        self.collapseAllAction.setEnabled(False)
        self.generateAdaptersAction.setEnabled(False)
        self.generateLibrariesAction.setEnabled(False)
        self.generateAllAction.setEnabled(False)
        # new in v11.1
        self.prepareAssistantAction.setEnabled(False)
        self.generateAdapterWsdlAction.setEnabled(False)

    def generateAdapterWSDL(self):
        """
        Generate adapter from WSDL file or url
        """
        if not UCI.instance().isAuthenticated():
            QMessageBox.warning(self, "Capture desktop" , "Connect to the test center in first!")
            return

        dWsdl = WsdlDialog( self )
        if dWsdl.exec_() == QDialog.Accepted:
            url, fileWsdl, pkg, overwrite = dWsdl.getParameters()
            wsdlEncoded = b''
            if len(fileWsdl):
                # read the file
                fd = QFile(fileWsdl)
                if not fd.open(QIODevice.ReadOnly):
                    QMessageBox.warning(self, self.tr("Error opening file"), self.tr("Could not open the file ") + fileWsdl)
                else:
                    wsdlData= fd.readAll()
                    wsdlEncoded = base64.b64encode(wsdlData)
            
            UCI.instance().generateAdapterFromWSDL(wsdlUrl=url, wsdlFile=wsdlEncoded, pkg=pkg, overwrite=overwrite)
        
    def prepareAssistant(self):
        """
        Generate all packages
        """
        reply = QMessageBox.question(self, self.tr("Prepare assistant"), self.tr("Are you sure to prepare assistant?"),
                        QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            UCI.instance().prepareAssistant()
            
    def generateAll(self):
        """
        Generate all packages
        """
        reply = QMessageBox.question(self, self.tr("Generate all"), self.tr("Are you sure to re-generate all packages?"),
                        QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            UCI.instance().generateAll()

    def generateAdapters(self):
        """
        Generate adapters
        """
        reply = QMessageBox.question(self, self.tr("Generate adapters"), self.tr("Are you sure to re-generate adapters?"),
                        QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            UCI.instance().generateAdapters()

    def generateLibraries(self):
        """
        Generate libraries
        """
        reply = QMessageBox.question(self, self.tr("Generate librairies"), self.tr("Are you sure to re-generate libraries?"),
                        QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            UCI.instance().generateLibraries()

    def rebuild(self):
        """
        Rebuild cache
        """
        reply = QMessageBox.question(self, self.tr("Generate documentation"), self.tr("Are you sure to re-generate the documentation?"),
                        QMessageBox.Yes | QMessageBox.Cancel )
        if reply == QMessageBox.Yes:
            UCI.instance().genCacheHelp()

    def reloadAll(self):
        """
        Reload the tree
        """
        UCI.instance().reloadHelper()

    def expandItem(self, itm):
        """
        Expand item
        """
        itm.setExpanded(True)
        if itm.childCount() > 0:
            for i in xrange( itm.childCount() ):
                itm.child(i).setExpanded(True)
                if itm.child(i).childCount() > 0:
                    self.expandItem(itm=itm.child(i))

    def expandSubtreeItem(self):
        """
        Expand subitem of the tree
        """
        if self.areaTab.currentIndex() == TAB_ADAPTERS:
            treeHelper = self.helperAdapters
        elif self.areaTab.currentIndex() == TAB_LIBRARIES:
            treeHelper = self.helperLibraries
        else:
            treeHelper = self.helper
        currentItem = treeHelper.currentItem()
        if currentItem is not None:
            self.expandItem(itm=currentItem)

    def expandAllItems(self):
        """
        Expand all items
        """
        if self.areaTab.currentIndex() == TAB_ADAPTERS:
            treeHelper = self.helperAdapters
        elif self.areaTab.currentIndex() == TAB_LIBRARIES:
            treeHelper = self.helperLibraries
        else:
            treeHelper = self.helper
        treeHelper.expandAll()
    
    def collapseAllItems(self):
        """
        Collapse all items
        """
        if self.areaTab.currentIndex() == TAB_ADAPTERS:
            treeHelper = self.helperAdapters
        elif self.areaTab.currentIndex() == TAB_LIBRARIES:
            treeHelper = self.helperLibraries
        else:
            treeHelper = self.helper
        treeHelper.collapseAll()

    def currentItemChanged(self, currentItem, previousItem):
        """
        Called on current item changed

        @param currentItem:
        @type currentItem:

        @param previousItem:
        @type previousItem:
        """
        if currentItem is not None:
            if 'desc' in currentItem.itemData:
                currentItem.setMetadata()
                desc = currentItem.itemData['desc'] 
                desc = desc.strip()
                desc_splitted = desc.splitlines()

                # init result and append the title
                lines = []
                lines.append( '<font color="grey"><u><b>%s</b></u></font>' % currentItem.getFullName()  )
                lines.append( '' )

                paramFinal = None; paramType = None; paramName = None; paramDesc = None
                returnFinal = None; returnDesc = None; returnType = None
                firstArgument = True
                for line in desc_splitted:
                    line = line.strip() 
                    if line.startswith('@param '):
                        paramName = line.split(':', 1)[0].split('@param ')[1]
                        paramDesc = line.split(':', 1)[1]
                    elif line.startswith('@type '):
                        paramType = line.split(':', 1)[1]
                        paramType = paramType.strip()
                        paramFinal = ' - <b>%s</b> (<i>%s</i>): %s' % (paramName, paramType, paramDesc)
                        if firstArgument:
                            firstArgument = False
                            lines.append( "<u>Arguments:</u>" )
                        lines.append( paramFinal )
                    elif line.startswith('@return'):
                        returnDesc = line.split(':', 1)[1]
                    elif line.startswith('@rtype'):
                        returnType = line.split(':', 1)[1]
                        returnType = returnType.strip()
                        lines.append( "<u>On exit:</u>" )
                        returnFinal = ' - <b>return</b> (<i>%s</i>): %s' % (returnType, returnDesc)
                        lines.append( returnFinal )
                    else:   
                        lines.append( line )
                desc = '<br />'.join(lines)

                self.textEdit.setHtml( desc )
                self.textEdit.unsetSytleSheetTextEdit()
            else:
                
                self.textEdit.setText('')

    def setNotConnected(self):
        """
        Set not connected
        """
        # self.labelHelp.setEnabled(False)
        self.textEdit.setSytleSheetTextEdit()
        self.setDefaultActionsValues()

    def setConnected(self, hideLabel=False):
        """
        Set connected

        @param hideLabel:
        @type hideLabel:
        """
        self.masterTab.setEnabled(True)
        
        # if hideLabel:
            # self.labelHelp.setEnabled(False)
            # self.labelHelp.hide()
        # else:
            # self.labelHelp.setEnabled(True)
            # self.labelHelp.show()
        
        self.reloadAllAction.setEnabled(True)
        if UCI.RIGHTS_ADMIN in UCI.instance().userRights or  UCI.RIGHTS_DEVELOPER in UCI.instance().userRights :
            self.rebuildCacheAction.setEnabled(True)
            self.generateAdaptersAction.setEnabled(True)
            self.generateLibrariesAction.setEnabled(True)
            self.generateAllAction.setEnabled(True)
            self.prepareAssistantAction.setEnabled(True)
            self.generateAdapterWsdlAction.setEnabled(True)
        else:
            self.rebuildCacheAction.setEnabled(False)
            self.generateAdaptersAction.setEnabled(False)
            self.generateLibrariesAction.setEnabled(False)
            self.generateAllAction.setEnabled(False)
            self.prepareAssistantAction.setEnabled(False)
            self.generateAdapterWsdlAction.setEnabled(False)
            
        self.expandSubtreeAction.setEnabled(True)
        self.expandAllAction.setEnabled(True)
        self.collapseAllAction.setEnabled(True)

    def initialize(self, listing):
        """
        Create the root item and load all subs items

        @param listing: 
        @type listing: list
        """
        self.helper.clear()
        self.helperInterop.clear()
        self.helperAdapters.clear()
        self.helperLibraries.clear()

        self.createTree(listing=listing, parent=self.helper, framework=True, adapters=False, libraries=False, interops=False)
        self.createTree(listing=listing, parent=self.helperInterop, framework=False, interops=True)
        self.createTree(listing=listing, parent=self.helperAdapters, framework=False, adapters=True, libraries=False)
        self.createTree(listing=listing, parent=self.helperLibraries, framework=False, adapters=False, libraries=True)

    def createTree(self, listing, parent, framework=False, adapters=False, libraries=False, isGeneric=False, isDefault=False, interops=False ):
        """
        Create the tree

        @param listing: 
        @type listing: list

        @param parent: 
        @type parent:

        """
        try:
            for dct in  listing:
                if dct["type"] in ["package", "package-libraries", "package-adapters"]:
                    if dct["type"] == "package" and dct["name"] != "TestInteroperability" and not framework:
                        continue
                    if dct["type"] == "package" and dct["name"] != "TestLibrary" and not interops:
                        continue
                    if dct["type"] == "package-libraries" and not libraries:
                        continue
                    if dct["type"] == "package-adapters" and not adapters:
                        continue

                    icon = QIcon(":/package.png") 
                    item = Item( parent = parent, data = dct, type = QTreeWidgetItem.UserType+1, icon=icon )
                    if 'libraries' in dct:
                        for lib in dct["libraries"]:
                            self.createTree(  [lib] , item, framework=framework, adapters=adapters, libraries=libraries,
                                                isGeneric=isGeneric, isDefault=isDefault, interops=interops)
                    elif 'adapters' in dct:
                        for lib in dct["adapters"]:
                            self.createTree(  [lib] , item, framework=framework, adapters=adapters, libraries=libraries,
                                                isGeneric=isGeneric, isDefault=isDefault )
                    elif 'modules' in dct:
                        self.createTree(  dct["modules"] , item, framework=framework, adapters=adapters, libraries=libraries,
                                                isGeneric=isGeneric, isDefault=isDefault, interops=interops )
                    else:
                        # exception for testexucutorlib
                        self.createTree(  dct["classes"] , item, framework=framework, adapters=adapters, libraries=libraries,
                                                isGeneric=isGeneric, isDefault=isDefault, interops=interops )
                
                elif dct["type"] in [ "libraries", "adapters" ] :
                    icon = QIcon(":/package.png") 
                    if dct["type"] == "libraries":
                        icon = QIcon(":/libraries.png") 
                    if dct["type"] == "adapters":
                        icon = QIcon(":/adapters.png")
                    item = Item( parent = parent, data = dct, type = QTreeWidgetItem.UserType+5, icon=icon, 
                                isDefault=dct["is-default"], isGeneric=dct["is-generic"] )
                    if 'modules' in dct:
                        self.createTree(  dct["modules"] , item, framework=framework, adapters=adapters, libraries=libraries,
                                            isGeneric=dct["is-generic"], isDefault=dct["is-default"], interops=interops )
                    else:
                        # exception for testexucutorlib
                        self.createTree(  dct["classes"] , item, framework=framework, adapters=adapters, libraries=libraries,
                                            isGeneric=isGeneric, isDefault=isDefault, interops=interops )
                
                elif dct["type"] == "module":
                    item = Item( parent = parent, data = dct, type = QTreeWidgetItem.UserType+2, icon=QIcon(":/module.png") )
                    self.createTree(  dct["classes"] , item, framework=framework, adapters=adapters, libraries=libraries,
                                        isGeneric=isGeneric, isDefault=isDefault, interops=interops )
                
                elif dct["type"] == "class":
                    item = Item( parent = parent, data = dct, type = QTreeWidgetItem.UserType+3, icon=QIcon(":/class.png"),
                                    isDefault=isDefault, isGeneric=isGeneric )
                    self.createTree(  dct["functions"] , item, framework=framework, adapters=adapters, libraries=libraries,
                                        isGeneric=isGeneric, isDefault=isDefault, interops=interops )
                
                elif dct["type"] == "method":
                    hide = False
                    if dct['name'] == '__init__': # hide __init__ function
                        hide = True
                    item = Item( parent = parent, data = dct , type = QTreeWidgetItem.UserType+4, icon=QIcon(":/methods.png"), hide=hide )
                
                elif dct["type"] == "function":
                    item = Item( parent = parent, data = dct , type = QTreeWidgetItem.UserType+4, icon=QIcon(":/functions.png") )
                
                else:
                    self.error( "type not supported: %s" % dct )

        except Exception as e:
            self.error( e )

    def onLoad(self, data):
        """
        On load from remote server

        @param data:
        @type data:
        """
        self.helper.unsetSytleSheetTree()
        self.helperInterop.unsetSytleSheetTree()
        self.helperAdapters.unsetSytleSheetTree()
        self.helperLibraries.unsetSytleSheetTree()
        
        helpObj = []
        
        try:
            helpDecoded = zlib.decompress( base64.b64decode(data['help']) )
        except Exception as e:
            self.error( 'unable to decompress helper data: %s' % str(e) )
            
        else:
            try:
                if sys.version_info > (3,):
                    helpObj = pickle.loads( helpDecoded, encoding="utf8" )
                else:
                    helpObj = pickle.loads( helpDecoded )
                self.assistantData = helpObj
            except Exception as e:
                self.error( 'unable to loads helper data: %s' % str(e) )

        if  UCI.RIGHTS_ADMIN in UCI.instance().userRights or UCI.RIGHTS_TESTER in UCI.instance().userRights or \
                UCI.RIGHTS_DEVELOPER in UCI.instance().userRights:
            self.setConnected() 

            self.helper.setEnabled(True)
            self.helperInterop.setEnabled(True)
            self.helperAdapters.setEnabled(True)
            self.helperLibraries.setEnabled(True)

            self.textEdit.setEnabled(True)
            self.initialize(listing=helpObj)
         
    def helpAllObjects(self):
        """
        return help all objects
        """
        return self.assistantData

    def helpFramework(self, moduleName=None, className=None, functionName=None):
        """
        return help all objects
        """
        if not len(self.assistantData):
            return None
            
        for h in self.assistantData:
            if  h['type'] == 'package':
                if moduleName is None:
                    return h['modules']
                else:
                    for m in h['modules']:
                        if m['name'] == moduleName:
                            if functionName is not None and className is None:
                                for c in m['classes']:
                                    if  c['type'] == 'function':
                                        if c['name'] == functionName: 
                                            return c
                            else:
                                if className is None:
                                    return m['classes']
                                else:
                                    for c in m['classes']:
                                        if c['name'] == className: 
                                            if functionName is None:
                                                return c['functions']
                                            else:
                                                for f in c['functions']:
                                                    if f['name'] == functionName: 
                                                        return f

    def helpAdapters(self, name=None):
        """
        return help all objects
        """
        if not len(self.assistantData):
            return None
        for h in self.assistantData:
            if  h['type'] == 'package-adapters':
                for sutadp in h['adapters']:
                    if name is not None:
                        if sutadp['name'] == name:
                            return sutadp['modules']
                    else:
                        if sutadp['is-default']:
                            return sutadp['modules']
                return []

    def isGuiGeneric(self, name="GUI"):
        """
        """
        isGeneric = False
        for h in self.assistantData:
            if  h['type'] == 'package-adapters':
                for sutadp in h['adapters']:
                    # search in default
                    if sutadp['is-generic'] and not sutadp['is-default']:
                        for m in sutadp['modules']:
                            if m['name'] == name:
                                isGeneric = True
                                break
        return isGeneric
        
    def helpLibraries(self, name=None):
        """
        return help all objects
        """
        if not len(self.assistantData):
            return None
        for h in self.assistantData:
            if  h['type'] == 'package-libraries':
                for sutlib in h['libraries']:
                    if name is not None:
                        if sutlib['name'] == name:
                            return sutlib['modules']
                    else:
                        if sutlib['is-default']:
                            return sutlib['modules']
                return []

    def onReset(self):
        """
        On reset from remote server
        """
        self.assistantData = []

        self.helper.setSytleSheetTree()
        self.helperInterop.setSytleSheetTree()
        self.helperAdapters.setSytleSheetTree()
        self.helperLibraries.setSytleSheetTree()

        self.setNotConnected() 
        self.helper.clear()
        self.helper.setEnabled(False)
        
        self.helperInterop.clear()
        self.helperInterop.setEnabled(False)
        
        self.helperAdapters.clear()
        self.helperAdapters.setEnabled(True)

        self.helperLibraries.clear()
        self.helperLibraries.setEnabled(True)

        self.textEdit.setEnabled(False)
        self.textEdit.setText('')

    def onRefresh(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        self.helper.clear()
        self.helperInterop.clear()
        self.helperAdapters.clear()
        self.helperLibraries.clear()
        self.onLoad( data )

WH = None # Singleton
def instance ():
    """
    Returns Singleton
    """
    return WH

def initialize (parent):
    """
    Initialize WRepositories widget
    """
    global WH
    WH = WHelper(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global WH
    if WH:
        WH = None