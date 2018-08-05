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
Test abstract module
"""
import sys
import json

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QMessageBox, QIcon, QLabel, QVBoxLayout)
except ImportError:
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QMessageBox, QLabel, QVBoxLayout)

from Libs import QtHelper, Logger
import json

try:
    import Document
except ImportError: # python3 support
    from . import Document

try:
    import FileModels.TestAbstract as FileModelTestAbstract
except ImportError: # python3 support
    from .FileModels import TestAbstract as FileModelTestAbstract

try:
    import GraphModels.GraphScene as GraphScene
    import GraphModels.OperatorsWidget as OperatorsWidget
except ImportError: # python3 support
    from .GraphModels import GraphScene as GraphScene
    from .GraphModels import OperatorsWidget as OperatorsWidget
    
import Settings
import DefaultTemplates

try:
    import DocumentProperties
except ImportError: # python3 support
    from . import DocumentProperties
    
TYPE = 'tax'
DEFAULT_STEP = { 
                    'id': '1',
                    'expected': {'type': 'string', 'value': 'result expected'}, 
                    'description': {'type': 'string', 'value': 'step description'}, 
                    'summary': {'type': 'string', 'value': 'step sample'}
                }
try:
    import Helper
except ImportError: # support python3
    from . import Helper
    
class WTestAbstract(Document.WDocument):
    """
    Test abstract widget
    """
    def __init__(self, parent = None, path = None, filename = None, extension = None, nonameId = None, 
                        remoteFile=False, repoDest=None, project=0, isLocked=False):
        """
        Constructs WScript widget

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
        Document.WDocument.__init__(self, parent, path, filename, extension, nonameId, 
                                    remoteFile, repoDest, project, isLocked)

        # prepare model with default value
        userName = Settings.instance().readValue( key = 'Server/last-username' )
        defaultTemplates = DefaultTemplates.Templates()
        testdef = defaultTemplates.getTestUnitDefinition()
        if not 'default-library' in Settings.instance().serverContext:
            if not Settings.instance().offlineMode:
                QMessageBox.critical(self, "Open" , 
                                     "Server context incomplete (default library is missing), please to reconnect!")
            defLibrary = 'v000'
        else:
            defLibrary = Settings.instance().serverContext['default-library']
        if not 'default-adapter' in Settings.instance().serverContext:
            if not Settings.instance().offlineMode:
                QMessageBox.critical(self, "Open" , 
                                     "Server context incomplete (default adapter is missing), please to reconnect!")
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
        
        self.dataModel = FileModelTestAbstract.DataModel(userName=userName, 
                                                        testDef=testdef, 
                                                        defLibrary=defLibrary, 
                                                        defAdapter=defAdapter,
                                                        timeout=defaultTimeout, 
                                                        inputs=_defaults_inputs, 
                                                        outputs=_defaults_outputs)
        

        self.defaultTemplates = DefaultTemplates.Templates()
        
        self.createActions()
        
        self.createWidgets()
        self.createToolbar()
        self.createConnections()  

    def createActions(self):
        """
        Create actions
        """
        self.toTestUnitAction = QtHelper.createAction(self, 
                                                      self.tr("&Convert\nTest Unit"), 
                                                      self.toTestUnit,
                                                      icon = QIcon(":/tux.png") )

    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|------|||
        || Open | Save |||
        ||------|------|||
        """
        pass

    def createWidgets (self):
        """
        QtWidgets creation
        """
        self.graphScene = GraphScene.GraphAbstract(self, helper=Helper.instance(), 
                                                   testParams=DocumentProperties.instance())
        self.graphScene.dockToolbarTest.addAction(self.toTestUnitAction)

        layoutFinal = QVBoxLayout()
        layoutFinal.addWidget(self.graphScene)
        layoutFinal.setContentsMargins(0,0,0,0)

        self.setLayout(layoutFinal)
 
    def createConnections (self):
        """
        QtSignals connection
        """
        self.graphScene.AddStep.connect(self.addStep)

    def addStep(self):
        """
        """
        DocumentProperties.instance().steps.table().addStep()

    def print_(self, printer):
        """
        Print accessor for the grahical scene
        """
        self.graphScene.print_(printer=printer)
    
    def toTestUnit(self):
        """
        """
        self.parent.newTestUnitWithContent( 
                                testDef=self.constructTestDef(),
                                testInputs=self.graphScene.getInputs(), 
                                testOutputs=self.graphScene.getInputs(), 
                                testAgents=self.graphScene.getAgents()
                    )
        
    def defaultLoad(self):
        """
        Default load
        """
        self.setReadOnly( readOnly=False )
        
        # adding start item
        self.graphScene.loadDefault()
        
        # adding default step
        self.dataModel.steps['steps']['step'] = [DEFAULT_STEP]
        DocumentProperties.instance().steps.table().insertItem(stepParams=DEFAULT_STEP)

    def steps(self):
        """
        Returns steps properties instance
        """
        return DocumentProperties.instance().steps.table()

    def adapters(self):
        """
        Returns adapters properties instance
        """
        return DocumentProperties.instance().adapters.table()

    def libraries(self):
        """
        Returns libraries properties instance
        """
        return DocumentProperties.instance().libraries.table()

    def getHelpLibraries(self, generic=False):
        """
        Return the help of all libraries according to the current
        version of the test
        """
        if generic:
            return Helper.instance().helpLibraries(generic=generic)
        else:
            testDescrs = DocumentProperties.instance().descrs.table().model.getData()
            currentLibVersion = None
            for descr in testDescrs:
                if descr['key'] == 'libraries':
                    currentLibVersion = descr['value']
                    break
            return Helper.instance().helpLibraries(name=currentLibVersion)
        
    def getHelpAdapters(self, generic=False):
        """
        Return the help of all adapters according to the current
        version of the test
        """
        if generic:
            return Helper.instance().helpAdapters(generic=generic)
        else:
            testDescrs = DocumentProperties.instance().descrs.table().model.getData()
            currentAdpVersion = None
            for descr in testDescrs:
                if descr['key'] == 'adapters':
                    currentAdpVersion = descr['value']
                    break
            return Helper.instance().helpAdapters(name=currentAdpVersion)
        
    def load (self, content=None):
        """
        Open file and contruct the data model
        """
        if content is not None:
            res =  self.dataModel.load( rawData = content )
        else:
            absPath = '%s/%s.%s' % (self.path, self.filename, self.extension)
            res = self.dataModel.load( absPath = absPath )
        if res:
            self.setReadOnly( readOnly=False )

            DocumentProperties.instance().steps.table().setSteps(steps=self.dataModel.steps['steps']['step'] )
            DocumentProperties.instance().adapters.table().setAdapters(adapters=self.dataModel.adapters['adapters']['adapter'] )
            self.graphScene.loadData(actions=self.dataModel.actions['actions']['action'])
            self.graphScene.DataChanged.connect(self.setModify)
        
        return res

    def write (self, force = False ):
        """
        Save the data model to file
        """
        # update data model
        self.dataModel.setSteps( steps=DocumentProperties.instance().steps.table().model.getData() )
        self.dataModel.setActions( actions=self.getModelDataActions()  )
        self.dataModel.setAdapters( adapters=DocumentProperties.instance().adapters.table().model.getData() )

        # if not forced and no change in the document, do nothing and return
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
        Returns raw data encoded
        """
        # update data model
        self.dataModel.setSteps( steps=DocumentProperties.instance().steps.table().model.getData() )
        self.dataModel.setAdapters( adapters=DocumentProperties.instance().adapters.table().model.getData() )
        self.dataModel.setActions( actions=self.getModelDataActions() )
        
        # construct the complete test from model
        self.dataModel.setTestDef(testDef=self.constructTestDef() )

        # return raw file
        ret = self.dataModel.getRaw()
        return ret
    
    def __parseString(self, strIn):
        """
        Parse string
        """
        ret = ''
        if len(strIn.splitlines()) > 1:
            valueEscaped = json.dumps(strIn)[1:-1]
            ret = '"""%s"""' % valueEscaped
        else:
            if strIn.endswith('\n'):
                valueEscaped = json.dumps(strIn)[1:-1]
                ret = '"""%s"""' % valueEscaped
            else:
                ret = "'%s'" % strIn
        return ret

    def __constructDefaultValue(self, param, params, default):
        """
        Constructs default value
        """
        if param['type'] == 'testcase':
            params.append( '%s=self' % (param['name']) )
            
        elif param['type'].lower() == 'none':
            params.append( '%s=None' % (param['name']) )
            
        elif param['type'].lower() == 'string':
            params.append( '%s=%s' % (param['name'],self.__parseString(default)) )

        elif param['type'].lower() == 'condition':
            params.append( '%s=%s' % (param['name'], self.__parseString(param['value']) ) )

        else:
            if len(default):
                params.append( '%s=%s' % (param['name'],default) )
            else:
                params.append( "%s=''" % (param['name']) )

    def __constructOperator(self, opName, opType, opValue):
        """
        Construct operator
        """
        ret = ''
        opName = opName.lower()
        if opName in [ OperatorsWidget.OP_EQUALS, OperatorsWidget.OP_NOT_EQUALS]:
            if opType == 'string':
                ret =  "%s" % self.__parseString(opValue)
            elif opType == 'inputs':
                ret = 'input("%s")' %  opValue
            elif opType == 'outputs':
                ret =  'outputs("%s")' % opValue
            elif opType == 'variables':
                ret = '%s' %  opValue 
                
        elif opName == OperatorsWidget.OP_GREATER_EQUAL_THAN:
            if opType == 'string':
                ret =  'TestOperators.GreaterThan(x=%s, equal=True)' % opValue
            elif opType == 'inputs':
                ret =  'TestOperators.GreaterThan(x=input("%s"), equal=True)' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.GreaterThan(x=output("%s"), equal=True)' % opValue
            elif opType == 'variables':
                ret =  'TestOperators.GreaterThan(x=%s, equal=True)' % opValue

        elif opName == OperatorsWidget.OP_LOWER_EQUAL_THAN:
            if opType == 'string':
                ret = 'TestOperators.LowerThan(x=%s, equal=True)' %  opValue
            elif opType == 'inputs':
                ret =  'TestOperators.LowerThan(x=input("%s"), equal=True)' % opValue
            elif opType == 'outputs':
                ret =  'TestOperators.LowerThan(x=output("%s"), equal=True)' % opValue
            elif opType == 'variables':
                ret =  'TestOperators.LowerThan(x=%s, equal=True)' % opValue
                
        elif opName == OperatorsWidget.OP_GREATER_THAN:
            if opType == 'string':
                ret =  'TestOperators.GreaterThan(x=%s, equal=False)' % opValue
            elif opType == 'inputs':
                ret =  'TestOperators.GreaterThan(x=input("%s"), equal=False)' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.GreaterThan(x=output("%s"), equal=False)' % opValue
            elif opType == 'variables':
                ret =  'TestOperators.GreaterThan(x=%s, equal=False)' % opValue

        elif opName == OperatorsWidget.OP_LOWER_THAN:
            if opType == 'string':
                ret = 'TestOperators.LowerThan(x=%s, equal=False)' %  opValue
            elif opType == 'inputs':
                ret =  'TestOperators.LowerThan(x=input("%s"), equal=False)' % opValue
            elif opType == 'outputs':
                ret =  'TestOperators.LowerThan(x=output("%s"), equal=False)' % opValue
            elif opType == 'variables':
                ret =  'TestOperators.LowerThan(x=%s, equal=False)' % opValue

        elif opName == OperatorsWidget.OP_CONTAINS:
            if opType == 'string':
                ret =  'TestOperators.Contains(needle=%s, AND=True, OR=False)' % self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.Contains(needle=input("%s"), AND=True, OR=False)' % opValue
            elif opType == 'outputs':
                ret =  'TestOperators.Contains(needle=output("%s"), AND=True, OR=False)' %  opValue 
            elif opType == 'variables':
                ret =  'TestOperators.Contains(needle=%s, AND=True, OR=False)' %  opValue
        elif opName == OperatorsWidget.OP_NOT_CONTAINS:
            if opType == 'string':
                ret =  'TestOperators.NotContains(needle=%s, AND=True, OR=False)' %  self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.NotContains(needle=input("%s"), AND=True, OR=False)' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.NotContains(needle=output("%s"), AND=True, OR=False)' %  opValue 
            elif opType == 'variables':
                ret =  'TestOperators.NotContains(needle=%s, AND=True, OR=False)' %  opValue

        elif opName == OperatorsWidget.OP_STARTSWITH:
            if opType == 'string':
                ret =  'TestOperators.Startswith(needle=%s)' %  self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.Startswith(needle=input("%s"))' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.Startswith(needle=output("%s"))' % opValue
            elif opType == 'variables':
                ret =  'TestOperators.Startswith(needle=%s)' %  opValue
        elif opName == OperatorsWidget.OP_NOT_STARTSWITH:
            if opType == 'string':
                ret =  'TestOperators.NotStartswith(needle=%s)' %  self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.NotStartswith(needle=input("%s"))' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.NotStartswith(needle=output("%s"))' % opValue
            elif opType == 'variables':
                ret =  'TestOperators.NotStartswith(needle=%s)' %  opValue

        elif opName == OperatorsWidget.OP_ENDSWITH:
            if opType == 'string':
                ret =  'TestOperators.Endswith(needle=%s)' % self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.Endswith(needle=input("%s"))' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.Endswith(needle=output("%s"))' %  opValue
            elif opType == 'variables':
                ret =  'TestOperators.Endswith(needle=%s)' %  opValue
        elif opName == OperatorsWidget.OP_NOT_ENDSWITH:
            if opType == 'string':
                ret =  'TestOperators.NotEndswith(needle=%s)' %  self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.NotEndswith(needle=input("%s"))' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.NotEndswith(needle=output("%s"))' %  opValue
            elif opType == 'variables':
                ret =  'TestOperators.NotEndswith(needle=%s)' %  opValue

        elif opName == OperatorsWidget.OP_REG_EX:
            if opType == 'string':
                ret =  'TestOperators.RegEx(needle=%s)' %  self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.RegEx(needle=input("%s"))' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.RegEx(needle=output("%s"))' %  opValue
            elif opType == 'variables':
                ret =  'TestOperators.RegEx(needle=%s)' %  opValue
        elif opName == OperatorsWidget.OP_NOT_REG_EX:
            if opType == 'string':
                ret =  'TestOperators.NotRegEx(needle=%s)' %  self.__parseString(opValue)
            elif opType == 'inputs':
                ret =  'TestOperators.NotRegEx(needle=input("%s"))' %  opValue
            elif opType == 'outputs':
                ret =  'TestOperators.NotRegEx(needle=output("%s"))' %  opValue
            elif opType == 'variables':
                ret =  'TestOperators.NotRegEx(needle=%s)' % opValue

        elif opName == OperatorsWidget.OP_ANY:
            ret =  'TestOperators.Any()'

        else:
            ret =  '%s' % self.__parseString(opValue) 

        return ret

    def __constructArgument(self, param, params):
        """
        Constructs argument, code factoring
        """
        if len(param['selected-type']):
        
            if param['selected-type'].lower() == 'testcase':
                params.append( '%s=self' % (param['name']) )

            elif param['selected-type'].lower() == 'none':
                params.append( '%s=None' % (param['name']) )
                        
            elif param['selected-type'].lower() == 'string':
                params.append( '%s=%s' % (param['name'], self.__parseString(param['value']) ) )

            elif param['selected-type'].lower() == 'condition':
                params.append( '%s=%s' % (param['name'], self.__parseString(param['value']['operator'].lower()) ) )

            elif param['selected-type'].lower() in [ 'boolean' ]:
                params.append( '%s=%s' % (param['name'],param['value'])    )   

            elif param['selected-type'].lower() in [ 'integer', 'float', 'object', 'list', 'tuple' ]:
                if len(param['value']):
                    params.append( '%s=%s' % (param['name'],param['value'])    )   
                else:
                    params.append( '%s' % (param['name'])    ) 

            elif param['selected-type'].lower() == 'dict':
                # fix value
                if not isinstance(param['value'], dict):  param['value'] = {'dict': [] }
                if isinstance(param['value']['dict'], dict): param['value']['dict'] = [param['value']['dict']] 

                dictParams = []
                for kv in param['value']['dict']:
                    dictParams.append( "'%s': '%s'" % (kv['key'], kv['value'] ) )
                params.append( '%s={%s}' %  (param['name'], ', '.join(dictParams))  )

            elif param['selected-type'].lower() == 'dictadvanced':
                # fix value
                if not isinstance(param['value'], dict):  param['value'] = {'dictadvanced': [] }
                if isinstance(param['value']['dictadvanced'], dict): param['value']['dictadvanced'] = [param['value']['dictadvanced']] 

                dictParams = []
                for kv in param['value']['dictadvanced']:
                    opKey = kv['key']
                    opKeyName = opKey['operator']
                    opKeyValue = opKey['value']
                    opKeyType = opKey['type']

                    opValue = kv['value']
                    opValueName = opValue['operator']
                    opValueValue = opValue['value']
                    opValueType = opValue['type']

                    dictParams.append( "%s: %s" % ( self.__constructOperator(opName=opKeyName, opType=opKeyType, opValue=opKeyValue),
                                                    self.__constructOperator(opName=opValueName, opType=opValueType, opValue=opValueValue) ) )
                params.append( '%s={%s}' %  (param['name'], ', '.join(dictParams))  )

            elif param['selected-type'].lower() == 'operators':
                opData = param['value']
                opName = opData['operator']
                opValue = opData['value']
                opType = opData['type']

                if opData['type'] == OperatorsWidget.OP_NOT_EQUALS:
                    params.append( '%s!=%s' % (param['name'], self.__constructOperator(opName=opName, opType=opType, opValue=opValue) ) )
                else:
                    params.append( '%s=%s' % (param['name'], self.__constructOperator(opName=opName, opType=opType, opValue=opValue) ) )

            elif param['selected-type'].lower() == 'agents':
                params.append( '%s=agent("%s")' % (param['name'],param['value'])    )

            elif param['selected-type'].lower() in ['strconstant', 'intconstant']:
                params.append( '%s=%s' % (param['name'],param['value'])    )

            elif param['selected-type'].lower() == 'inputs':
                params.append( '%s=input("%s")' % (param['name'],param['value'])    )   

            elif param['selected-type'].lower() == 'outputs':
                params.append( '%s=output("%s")' % (param['name'],param['value'])    ) 
                
            elif param['selected-type'].lower() == 'variables':
                if not len(param['value']):
                    params.append( '%s=%s' % (param['name'], 'ACTION0')    )  
                else:
                    params.append( '%s=%s' % (param['name'],param['value'])    )   

            else:
                params.append( '%s=%s' % (param['name'], self.__parseString(param['value']))    )   
        else:
            # set the default value
            if 'default-value' in param:
                self.__constructDefaultValue(param=param, params=params, default=param['default-value'])
            else:
                self.__constructDefaultValue(param=param, params=params, default=param['value'])
              
    def getModelDataActions(self):
        """
        Get model data for actions
        """
        dataModel = []
        for gItem in self.graphScene.scene.items():
            if not isinstance(gItem, GraphScene.DiagramItem):
                continue  
            if isinstance(gItem, GraphScene.DiagramItem):
                gItem.setPosition()
                gItem.setLinks()
                dataModel.append( gItem.data )
        return dataModel

    def getFirstItem(self):
        """
        Get the first item
        """
        firstItem = None
        for gItem in self.graphScene.scene.items():
            if not isinstance(gItem, GraphScene.DiagramItem):
                continue  
            if gItem.diagramType == GraphScene.DiagramItem.StartEnd:
                firstItem = gItem
                break
        return firstItem

    def getNextItem(self, arrow):
        """
        Get the next item
        """
        nextItem = None
        try:
            for gItem in self.graphScene.scene.items():
                if not isinstance(gItem, GraphScene.DiagramItem):
                    continue  
                if gItem.hasInputs():
                    if arrow == gItem.getInput(0):
                        nextItem = gItem
                        break
        except Exception as e:
            print("error on get next item: %s" % e)
            
        return nextItem

    def readNextItem(self, currentItem):
        """
        Read the next item
        Recursive function
        """
        actionList = []
        try:
            if currentItem.diagramType in [ GraphScene.DiagramItem.Conditional, GraphScene.DiagramItem.Do ]:
                if not currentItem.hasOutputs():
                    actionList.append( currentItem.data['item-data'] )
                    actionList.append( self.graphScene.addPass() )
                else:
                    # read next item on condition true
                    actionList.append( currentItem.data['item-data'] )
                    if currentItem.hasOutputs():
                        nextSubItem = self.getNextItem( arrow=currentItem.getOutput(0) )
                        if nextSubItem is not None:
                            subactions = self.readNextItem(currentItem=nextSubItem)
                            actionList.extend(  subactions )
                    
                    # read next item on condition false
                    if currentItem.hasOutputs() == 2:
                        nextSubItem = self.getNextItem( arrow=currentItem.getOutput(1) )
                        if nextSubItem is not None:
                            actionList.append( self.graphScene.addElse() )
                            subactions = self.readNextItem(currentItem=nextSubItem)
                            actionList.extend(  subactions )
                        
                    actionList.append( self.graphScene.addEndIf() )
            else:
                actionList.append( currentItem.data['item-data'] )
                # read next item
                if currentItem.hasOutputs():
                    nextSubItem = self.getNextItem( arrow=currentItem.getOutput(0) )
                    if nextSubItem is not None:
                        subactions = self.readNextItem(currentItem=nextSubItem)
                        actionList.extend(  subactions )
        except Exception as e:
            print("error on read next item: %s" % e)
        
        return actionList
        
    def prepareActions(self):
        """
        """
        actionList = []

        firstItem = self.getFirstItem()
        if firstItem is None:
            print('error, first element not found')
        else:

            if firstItem.hasOutputs():
                nextItem = self.getNextItem( arrow=firstItem.getOutput(0) )
                
                if nextItem is not None:
                    subactions = self.readNextItem(currentItem=nextItem)
                    actionList.extend(  subactions )   
        return actionList

    def constructTestDef(self):
        """
        Construct test definition
        """
        # get test templates
        newTest = self.defaultTemplates.getTestUnitDefinitionAuto()

        # construct step part
        stepsModel = DocumentProperties.instance().steps.table().model.getData()
        stepsList = []
        for stp in stepsModel:
            # read all param
            stpParams = []
            for k,v in stp.items():
                if isinstance(v, dict):
                    # type can be missing
                    if 'type' in v:
                        if v['type'] == 'string':
                            valueEscaped = json.dumps(v['value'])[1:-1]
                            stpParams.append( '%s="""%s"""' % (k,valueEscaped) )

            stepsList.append("self.STEP%s = self.addStep(%s)" % (stp['id'], ', '.join(stpParams) ) )

        newTest = newTest.replace( "<<STEPS>>", '\n\t%s' % '\n\t'.join(stepsList) )

        newTest = newTest.replace( "<<PURPOSE>>", 'pass' )

        newTest = newTest.replace( "<<INIT>>", 'pass' )
        newTest = newTest.replace( "<<CLEANUP>>", 'pass' )
    
        # construct adapters part
        adaptersModel = DocumentProperties.instance().adapters.table().model.getData()
        adaptersList = []
        y = 0
        for adp in adaptersModel:
            adpParams = []
            y += 1
            for param in adp['data']['obj']:
                self.__constructArgument(param=param, params=adpParams)

            extra_adp = ""
            if "is-default" in adp['data']:
                if adp['data']['is-default'] == "True":
                    extra_adp = ".Extra"
            adaptersList.append("self.ADAPTER%s = SutAdapters%s.%s.%s(%s)" % (y,
                                                                            extra_adp,
                                                                            adp['data']['main-name'], 
                                                                            adp['data']['sub-name'], 
                                                                            ', '.join(adpParams) ) )

        # construct libraries part
        librariesModel = DocumentProperties.instance().libraries.table().model.getData()
        librariesList = []
        y = 0
        for lib in librariesModel:
            libParams = []
            y += 1
            for param in lib['data']['obj']:
                self.__constructArgument(param=param, params=libParams)

            extra_lib = ""
            if "is-default" in adp['data']:
                if adp['data']['is-default'] == "True":
                    extra_lib = ".Extra"
            adaptersList.append("self.LIBRARY%s = SutLibraries%s.%s.%s(%s)" % (y,
                                                                             extra_lib,
                                                                             lib['data']['main-name'], 
                                                                             lib['data']['sub-name'], 
                                                                             ', '.join(libParams) ) )


        newTest = newTest.replace( "<<ADPS>>", '\n\t%s' % '\n\t'.join(adaptersList) )
        
        # construct test part
        actionsModel = self.prepareActions()

        actionsList = []
        nbIf = 0
        y = 0
        for act in actionsModel:
            y += 1

            if 'obj' not in act['data']:
                act['data']['obj'] = []

            # prepare if condition for adapter
            if act['action'] == GraphScene.ACTION_DO:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)

                actionsList.append("%sACTION%s = self.ADAPTER%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['adapter-id'], act['data']['function'], ', '.join(actParams) ) )
                actionsList.append("%sif ACTION%s:" % (("\t" * nbIf),act['item-id'] ) )
    
                nbIf += 1

            # prepare if condition
            if act['action'] == GraphScene.ACTION_CONDITION_IF:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                condParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=condParams)

                actionsList.append("%sif self.%s(%s):" % (("\t" * nbIf), act['data']['function'], ', '.join(condParams) ) )
                nbIf += 1

            # prepare pass
            if act['action'] == GraphScene.ACTION_PASS:
                actionsList.append("%spass" % ("\t" * nbIf) )

            # prepare else condition
            if act['action'] == GraphScene.ACTION_CONDITION_ELSE:
                actionsList.append("%selse:" % ("\t" * (nbIf-1)) )

            # prepare end if
            if act['action'] == GraphScene.ACTION_CONDITION_ENDIF:
                nbIf -= 1
            
            # prepare breakpoint
            if act['action'] == GraphScene.ACTION_BREAKPOINT:
                actionsList.append("%sBreakPoint(self)" % ("\t" * nbIf) )
            
            # prepare step action
            if act['action'] == GraphScene.ACTION_STEP:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                stpParams = []

                for param in act['data']['obj']:
                    # type can be missing
                    if 'type' in param:
                        if param['type'] == 'string':
                            valueEscaped = json.dumps(param['value'])[1:-1]
                            stpParams.append( '%s="""%s"""' % (param['name'],valueEscaped) )
                
                    # function can be missing
                if 'function' in act['data']:
                    actionsList.append("%sself.STEP%s.%s(%s)" % (("\t" * nbIf), act['step-id'], act['data']['function'], ', '.join(stpParams) ) )

            # prepare adapter definition
            if act['action'] == GraphScene.ACTION_ADAPTER:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)

                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = self.ADAPTER%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['adapter-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sself.ADAPTER%s.%s(%s)" % (("\t" * nbIf), act['adapter-id'], act['data']['function'], ', '.join(actParams) ) )

            # prepare library definition
            if act['action'] == GraphScene.ACTION_LIBRARY:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)

                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = self.LIBRARY%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['library-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sself.LIBRARY%s.%s(%s)" % (("\t" * nbIf), act['library-id'], act['data']['function'], ', '.join(actParams) ) )


            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_TESTCASE:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = self.%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sself.%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )

            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_CACHE:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = Cache().%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sCache().%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )
                    
            # prepare trace definition
            if act['action'] == GraphScene.ACTION_TRACE:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = Trace(self).%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sTrace(self).%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )
                    
            # prepare trace definition
            if act['action'] == GraphScene.ACTION_INTERACT:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = Interact(self).%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sInteract(self).%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )
                    
            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_TIME:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = Time(self).%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sTime(self).%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )
                    
            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_PRIVATE:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = Private(self).%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sPrivate(self).%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )
                    
            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_PUBLIC:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = Public(self).%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sPublic(self).%s(%s)" % (("\t" * nbIf), act['data']['function'], ', '.join(actParams) ) )
                    
            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_TEMPLATE:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                actionsList.append( "%sself.TEMPLATE%s = TestTemplates.Template()" %  (("\t" * nbIf), act['item-id']) )
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = self.TEMPLATE%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sself.TEMPLATE%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
        

            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_MANIPULATOR:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                actionsList.append( "%sself.MANIPULATOR%s = TestManipulators.%s()" %  (("\t" * nbIf), act['item-id'], act['data']['main-name'] ) )
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = self.MANIPULATOR%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sself.MANIPULATOR%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
        

            # prepare testcase definition
            if act['action'] == GraphScene.ACTION_VALIDATOR:
                if isinstance(act['data']['obj'], dict):
                    act['data']['obj'] = [act['data']['obj']]

                actParams = []
                for param in act['data']['obj']:
                    self.__constructArgument(param=param, params=actParams)
                
                actionsList.append( "%sself.VALIDATOR%s = TestValidators.%s()" %  (("\t" * nbIf), act['item-id'], act['data']['main-name'] ) )
                if act['data']['return-value'] == 'True':
                    actionsList.append("%sACTION%s = self.VALIDATOR%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['item-id'], act['data']['function'], ', '.join(actParams) ) )
                else:
                    actionsList.append("%sself.VALIDATOR%s.%s(%s)" % (("\t" * nbIf), act['item-id'], act['data']['function'], ', '.join(actParams) ) )
        


        if len(actionsList):
            newTest = newTest.replace( "<<TESTS>>", '\n\t%s' % '\n\t'.join(actionsList) )
        else:
            newTest = newTest.replace( "<<TESTS>>", '\n\tpass' )

        return newTest
