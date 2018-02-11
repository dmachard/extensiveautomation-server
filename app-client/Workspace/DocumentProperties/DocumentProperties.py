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
Document properties module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QTabWidget, QIcon, QLabel, QFont, QVBoxLayout, 
                            QMessageBox, QDialog, QFileDialog)
    from PyQt4.QtCore import (pyqtSignal)
except ImportError:
    from PyQt5.QtGui import (QIcon, QFont)
    from PyQt5.QtWidgets import (QWidget, QTabWidget, QLabel, QVBoxLayout, QMessageBox, 
                                QDialog, QFileDialog)
    from PyQt5.QtCore import (pyqtSignal)
    
from Libs import QtHelper, Logger



try:
    import Descriptions
    import Parameters
    import Probes
    import Agents
    # new in v10
    import Steps
    import Adapters
    import Libraries
except ImportError as e: # support python3
    from . import Descriptions
    from . import Parameters
    from . import Probes
    from . import Agents
    from . import Steps
    from . import Adapters
    from . import Libraries

import Workspace.TestData as TestData
import Workspace.TestConfig as TestConfig

import Workspace.TestUnit as TestUnit
import Workspace.TestSuite as TestSuite

import Workspace.FileModels.TestConfig as FileModelTestConfig

import Settings
import UserClientInterface as UCI
import RestClientInterface as RCI


import base64

DEFAULT_NAME = 'Noname'

TAB_DESCRIPTION     =   0
TAB_STEPS           =   1

TAB_INPUTS          =   0
TAB_OUTPUTS         =   1
TAB_ADAPTERS        =   2
TAB_LIBRARIES       =   3

TAB_AGENTS          =   0
TAB_PROBES          =   1

class WDocumentProperties(QWidget, Logger.ClassLogger):
    """
    Document properties widget
    """
    RefreshLocalRepository = pyqtSignal()
    def __init__(self, parent=None, iRepo=None, lRepo=None, rRepo=None):
        """
        Widget document properties

        @param parent: 
        @type parent:

         / Description \_/ Parameters \_ / Probes \___
        |                                             |
        |                                             |
        | ____________________________________________|
        """
        QWidget.__init__(self, parent)
        
        self.descrs = None
        self.parameters = None
        self.probes = None
        self.agents = None
        self.steps = None
        self.adapters = None
        self.libraries = None
        self.parametersTab = None
        self.currentDoc = None
        self.currentTab = None
        self.iRepo = iRepo
        self.lRepo = lRepo # local repo dialog
        self.rRepo = rRepo # remote repo dialog
        self.wdoc  = None
        
        self.createActions()
        self.createWidgets()
        self.createConnections()    
        
        self.initToolbarParameters()

    def createWidgets(self):
        """
        Create qt widgets

        QTabWidget
         / QWidget \/ QWidget \_________________
        |                                       |
        | ______________________________________|
        """
        self.steps = Steps.StepsQWidget(self)
        self.descrs = Descriptions.DescriptionsQWidget(self)
        self.parameters = Parameters.ParametersQWidget(self)
        self.parametersOutput = Parameters.ParametersQWidget(self, forParamsOutput=True)
        self.probes = Probes.ProbesQWidget(self)
        self.agents = Agents.AgentsQWidget(self)
        self.adapters = Adapters.AdaptersQWidget(self, testParams=self, testDescrs=self.descrs)
        self.libraries = Libraries.LibrariesQWidget(self, testParams=self, testDescrs=self.descrs)
        
        self.parametersTab = QTabWidget()
        self.parametersTab.setTabPosition(QTabWidget.North)
        self.parametersTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border
        self.parametersTab.addTab(self.descrs, QIcon(":/test-config.png"), "Description")
        self.parametersTab.addTab(self.steps, QIcon(":/run-state.png"), "Steps")

        self.paramsTab = QTabWidget()
        self.paramsTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border
        self.paramsTab.setTabPosition(QTabWidget.North)
        self.paramsTab.addTab(self.parameters, QIcon(":/test-input.png"), "Inputs")
        self.paramsTab.addTab(self.parametersOutput, QIcon(":/test-output.png"), "Outputs")
        self.paramsTab.addTab(self.adapters, QIcon(":/adapters.png"), "Adapters")
        self.paramsTab.addTab(self.libraries, QIcon(":/libraries.png"), "Libraries")

        self.miscsTab = QTabWidget()
        self.miscsTab.setStyleSheet("QTabWidget { border: 0px; }") # remove 3D border
        self.miscsTab.setTabPosition(QTabWidget.North)
        self.miscsTab.addTab(self.agents, QIcon(":/agent.png"), "Agents")
        self.miscsTab.addTab(self.probes, QIcon(":/probe.png"), "Probes")

        self.title = QLabel("Test Properties")
        font = QFont()
        font.setBold(True)
        self.title.setFont(font)

        self.labelHelp = QLabel("Prepare the test.")
        font = QFont()
        font.setItalic(True)
        self.labelHelp.setFont(font)

        self.mainTab = QTabWidget()
        self.mainTab.setTabPosition(QTabWidget.North)
        
        self.mainTab.addTab(self.parametersTab, QIcon(":/test-description.png"), "Test Design")
        self.mainTab.addTab(self.paramsTab, QIcon(":/repository.png"), "Test Data")
        self.mainTab.addTab(self.miscsTab, QIcon(":/server-config.png"), "Miscellaneous")


        if Settings.instance().readValue( key = 'TestProperties/inputs-default-tab' ) == "True":
            self.mainTab.setCurrentIndex(1)
            self.paramsTab.setCurrentIndex(TAB_INPUTS)

        layout = QVBoxLayout()
        layout.addWidget( self.title )
        layout.addWidget( self.labelHelp )

        layout.addWidget(self.mainTab)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)
    
    def hideWidgetsHeader(self):
        """
        Hide the title of the widget
        """
        self.title.hide()
        self.labelHelp.hide()
        
    def showWidgetsHeader(self):
        """
        Show widget header
        """
        self.title.show()
        self.labelHelp.show()
        
    def createConnections(self):
        """
        Create qt connections
         * DescriptionTableView <=> dataChanged
         * ParametersTableView <=> dataChanged
         * ProbesTableView <=> dataChanged
        """
        self.descrs.table().DataChanged.connect(self.dataChanged)

        self.parameters.table().DataChanged.connect(self.dataChanged)
        if Settings.instance().readValue( key = 'TestProperties/parameters-rename-auto' ) == "True":
            self.parameters.table().NameParameterUpdated.connect(self.inputNameChanged)
        self.parameters.table().NbParameters.connect(self.onUpdateInputsNumber)
        
        self.parametersOutput.table().DataChanged.connect(self.dataChanged)
        if Settings.instance().readValue( key = 'TestProperties/parameters-rename-auto' ) == "True":
            self.parametersOutput.table().NameParameterUpdated.connect(self.outputNameChanged)
        self.parametersOutput.table().NbParameters.connect(self.onUpdateOutputsNumber)
        
        self.probes.table().DataChanged.connect(self.dataChanged)
        self.agents.table().DataChanged.connect(self.dataChanged)

        # to support test abstract
        self.steps.table().DataChanged.connect(self.dataChanged)
        self.adapters.table().DataChanged.connect(self.dataChanged)
        self.libraries.table().DataChanged.connect(self.dataChanged)

    def createActions (self):
        """
        Actions defined:
         * import 
         * export
        """
        self.importAction = QtHelper.createAction(self, "&Import inputs", self.importInputs, 
                    icon = QIcon(":/tc-import.png"), tip = 'Import inputs from Test Config' )
        self.exportAction = QtHelper.createAction(self, "&Export inputs", self.exportInputs, 
                    icon = QIcon(":/tc-export.png"), tip = 'Export inputs as Test Config' )
        self.importOutputsAction = QtHelper.createAction(self, "&Import outputs", self.importOutputs, 
                    icon = QIcon(":/tc-import.png"), tip = 'Import outputs from Test Config' )
        self.exportOutputsAction = QtHelper.createAction(self, "&Export outputs", self.exportOutputs,
                    icon = QIcon(":/tc-export.png"), tip = 'Export outputs as Test Config' )
                    
        self.markUnusedAction = QtHelper.createAction(self, "&Mark unused inputs", self.markUnusedInputs,
                    icon = QIcon(":/input-unused.png"), tip = 'Marks all unused inputs' )
        self.markUnusedOutputsAction = QtHelper.createAction(self, "&Mark unused ouputs", self.markUnusedOutputs,
                    icon = QIcon(":/input-unused.png"), tip = 'Marks all unused outputs' )

    def onUpdateInputsNumber(self, nbParams):
        """
        On update the number of inputs in the tabulation name
        """
        self.paramsTab.setTabText(0, "Inputs (%s)" % nbParams )

    def onUpdateOutputsNumber(self, nbParams):
        """
        On update the number of outputs in the tabulation name
        """
        self.paramsTab.setTabText(1, "Outputs (%s)" % nbParams )
        
    def initToolbarParameters(self):
        """
        Init toolbar parameters
        """
        self.parameters.toolbar().addSeparator()
        self.parameters.toolbar().addAction(self.markUnusedAction)
        self.parameters.toolbar().addSeparator()
        self.parameters.toolbar().addAction(self.importAction)
        self.parameters.toolbar().addAction(self.exportAction)

        self.parametersOutput.toolbar().addSeparator()
        self.parametersOutput.toolbar().addAction(self.markUnusedOutputsAction)
        self.parametersOutput.toolbar().addSeparator()
        self.parametersOutput.toolbar().addAction(self.importOutputsAction)
        self.parametersOutput.toolbar().addAction(self.exportOutputsAction)
        
    def setDocument(self, wdoc):
        """
        Save the address to the document
        """
        self.wdoc = wdoc
        
    def enableMarkUnused(self):
        """
        Active the button mark inputs as unused
        """
        self.markUnusedAction.setEnabled(True)
        self.markUnusedOutputsAction.setEnabled(True)
        
    def disableMarkUnused(self):
        """
        Disable the mark button
        """
        self.markUnusedAction.setEnabled(False)
        self.markUnusedOutputsAction.setEnabled(False)
 
    def markUnusedInputs(self):
        """
        Mark all inputs unused
        """
        if self.wdoc is None: return
        
        editorExec = None
        editorSrc = None
        
        if isinstance(self.wdoc, TestUnit.WTestUnit):
            editorSrc = self.wdoc.srcEditor
            
        if isinstance(self.wdoc, TestSuite.WTestSuite):
            editorSrc = self.wdoc.srcEditor
            editorExec = self.wdoc.execEditor
        
        self.parameters.markUnusedInputs(editorSrc=editorSrc, editorExec=editorExec)
        
    def markUnusedOutputs(self):
        """
        Mark all outputs unused
        """
        if self.wdoc is None: return
        
        editorExec = None
        editorSrc = None
        
        if isinstance(self.wdoc, TestUnit.WTestUnit):
            editorSrc = self.wdoc.srcEditor
            
        if isinstance(self.wdoc, TestSuite.WTestSuite):
            editorSrc = self.wdoc.srcEditor
            editorExec = self.wdoc.execEditor
        
        self.parameters.markUnusedOutputs(editorSrc=editorSrc, editorExec=editorExec)
        
    def addNew(self):
        """
        Add item on parameters or probes 
        """
        self.currentTab.insertItem()

    def delSelection(self):
        """
        Delete selected item on parameters or probes 
        """
        self.currentTab.removeItem()

    def exportOutputs (self):
        """
        Export all outputs
        """
        return self.export(inputs=False)

    def exportInputs (self):
        """
        Export all inputs
        """
        return self.export(inputs=True)

    def export (self, inputs):
        """
        Export test config, dispatch to local, remote or other 
        """
        ret = False
        
        self.localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
        
        # first in local repo if configured
        if self.localConfigured != "Undefined": 
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("Export to local repository") , buttons)
            if answer == QMessageBox.Yes:
                ret = self.saveToLocal(inputs=inputs)
            elif answer == QMessageBox.No:
                if RCI.instance().isAuthenticated: # no then perhaps in remo repo if connected?
                     ret = self.saveToRemote(inputs=inputs)
                else:
                    QMessageBox.warning(self, "Save" , "Connect to the test center first!")
        
        # not configured then in remo repo if connected ?
        elif RCI.instance().isAuthenticated:
             ret = self.saveToRemote(inputs=inputs)
        else:
            QMessageBox.warning(self, "Save" , "Connect to the test center first!")
        return ret 

    def splitFileName(self, fileName):
        """
        Split the filename
        """
        tmp = str(fileName).rsplit("/", 1)
        path = tmp[0]
        filename = tmp[1]
        return (path, filename)

    def saveToLocal(self, inputs=True):
        """
        Export test config to local repository
        """
        ret = False
        dialog = self.lRepo.SaveOpenToRepoDialog( parent=self, filename=DEFAULT_NAME )
        #
        if dialog.exec_() == QDialog.Accepted:
            fileName = dialog.getSelection()
            path, filename = self.splitFileName(fileName=fileName)
 
            doc = TestConfig.WTestConfig(self, path = path, filename=filename, extension=self.rRepo.EXTENSION_TCX) 
            if inputs:
                doc.dataModel.properties['properties']['parameters']['parameter'] = self.parameters.table().model.getData()
            else:
                doc.dataModel.properties['properties']['parameters']['parameter'] = self.parametersOutput.table().model.getData()
            ret = doc.write(force = True, fromExport=True)
            if ret:
                self.RefreshLocalRepository.emit()
        return ret

    def saveToRemote(self, inputs=True):
        """
        Export test config to remote repository
        """
        ret = False
        project = self.iRepo.remote().getCurrentProject()
        prjId = self.iRepo.remote().getProjectId(project=str(project))
        self.iRepo.remote().saveAs.setFilename(filename=DEFAULT_NAME, project=project)
        dialog = self.iRepo.remote().saveAs
        if dialog.exec_() == QDialog.Accepted:
            fileName = dialog.getSelection()
            path, filename = self.splitFileName(fileName=fileName)
            doc = TestConfig.WTestConfig(self,path = path, filename=filename, extension=self.rRepo.EXTENSION_TCX, remoteFile=True)
            if inputs:
                doc.dataModel.properties['properties']['parameters']['parameter'] = self.parameters.table().model.getData()
            else:
                doc.dataModel.properties['properties']['parameters']['parameter'] = self.parametersOutput.table().model.getData()
            
            # rest call
            RCI.instance().uploadTestFile(filePath=doc.path, 
                                          fileName=doc.filename, 
                                          fileExtension=doc.extension, 
                                          fileContent=doc.getraw_encoded(), 
                                          projectId=int(prjId), 
                                          updateMode=False, 
                                          closeTabAfter=False)
                       
            ret = True
        return ret

    def saveToAnywhere (self, inputs=True):
        """
        Save test config to anywhere
        Deprecated function
        """

        fileName = QFileDialog.getSaveFileName(self, "Export Test Config", "", "*.%s" % self.rRepo.EXTENSION_TCX )
        if fileName.isEmpty():
                return

        config = FileModelTestConfig.DataModel()
        if inputs:
            config.properties['properties']['parameters']['parameter'] = self.parameters.table().model.getData()
        else:
            config.properties['properties']['parameters']['parameter'] = self.parametersOutput.table().model.getData()
        config.write( absPath=fileName )
        del config

    def importOutputs(self):
        """
        Import all outputs
        """
        self.import__(inputs=False)

    def importInputs(self):
        """
        Import all inputs
        """
        self.import__(inputs=True)

    def import__(self, inputs):
        """
        Import test config, dispatch to local, remote or other 
        """
        # import from local repo
        self.localConfigured = Settings.instance().readValue( key = 'Repositories/local-repo' )
        if self.localConfigured != "Undefined":
            buttons = QMessageBox.Yes | QMessageBox.No
            answer = QMessageBox.question(self, Settings.instance().readValue( key = 'Common/name' ), 
                            self.tr("Import Test Config from local repository") , buttons)
            if answer == QMessageBox.Yes:
                self.loadFromLocal(inputs=inputs) # load local test config file
            else:
                if RCI.instance().isAuthenticated: # no then perhaps in remo repo if connected?
                    self.loadFromRemote(inputs=inputs) # load remote test config file
                else:
                    QMessageBox.warning(self, "Save" , "Connect to the test center first!")
        
        # import from remote repo
        elif RCI.instance().isAuthenticated: # no then perhaps in remo repo if connected?
            self.loadFromRemote(inputs=inputs) # load remote test config file
        else:
            QMessageBox.warning(self, "Save" , "Connect to the test center first!")        

    def loadFromRemote(self, inputs=True):
        """
        Load test config from remote repository
        """
        project = self.iRepo.remote().getCurrentProject()
        prjId = self.iRepo.remote().getProjectId(project=str(project))

        self.iRepo.remote().saveAs.getFilename(type=self.rRepo.EXTENSION_TCX, project=project)
        dialog = self.iRepo.remote().saveAs
        if dialog.exec_() == QDialog.Accepted:
            if inputs:
                RCI.instance().openFileTests(projectId=int(prjId), 
                                             filePath=dialog.getSelection(), 
                                             ignoreLock=False, 
                                             readOnly=False, 
                                             customParam=None, 
                                             actionId=UCI.ACTION_IMPORT_INPUTS, 
                                             destinationId=UCI.FOR_DEST_ALL)
            else:
                RCI.instance().openFileTests(projectId=int(prjId), 
                                             filePath=dialog.getSelection(), 
                                             ignoreLock=False, 
                                             readOnly=False, 
                                             customParam=None, 
                                             actionId=UCI.ACTION_IMPORT_OUTPUTS, 
                                             destinationId=UCI.FOR_DEST_ALL)
    def loadFromLocal(self, inputs=True):
        """
        Load test config from local repository
        """
        dialog = self.lRepo.SaveOpenToRepoDialog( self , "", type = self.lRepo.MODE_OPEN, typeFile=self.lRepo.EXTENSION_TCX ) 
        dialog.hideFiles(hideTsx=True, hideTpx=True, hideTcx=False, hideTdx=True)
        if dialog.exec_() == QDialog.Accepted:
            self.loadFromAnywhere(pathFilename=dialog.getSelection(), inputs=inputs)

    def loadFromAnywhere (self, pathFilename=None, inputs=True):
        """
        Load test config from anywhere
        Deprecated function

        @param pathFilename: 
        @type pathFilename: 
        """
        if pathFilename is None:
            fileName = QFileDialog.getOpenFileName(self, self.tr("Import File"), "", "Tcx Config Files (*.%s)" % self.rRepo.EXTENSION_TCX )
            # new in v18 to support qt5
            if QtHelper.IS_QT5:
                _fileName, _type = fileName
            else:
                _fileName = fileName
            # end of new
            
            if _fileName.isEmpty():
                return

            if not ( str(_fileName).endswith( self.rRepo.EXTENSION_TCX ) ):
                QMessageBox.critical(self, "Open Failed" , "File not supported")
                return
        else:
            _fileName=pathFilename
        
        config = FileModelTestConfig.DataModel()
        res = config.load( absPath = _fileName )
        if not res:
            QMessageBox.critical(self, "Open Failed" , "Corrupted file")
            return  
        
        if inputs:
            self.parameters.table().loadData(  data = config.properties['properties']['parameters'] )
            self.currentDoc.dataModel.properties['properties']['inputs-parameters'] = config.properties['properties']['parameters']
        else:
            self.parametersOutput.table().loadData(  data = config.properties['properties']['parameters'] )
            self.currentDoc.dataModel.properties['properties']['outputs-parameters'] = config.properties['properties']['parameters']

        self.currentDoc.setModify()

        del config

    def addRemoteTestConfigToTestsuite(self, data, inputs=True):
        """
        Add remote test config to a test

        @param data: 
        @type data: 
        """
        path_file, name_file, ext_file, encoded_data, project = data
        content = base64.b64decode(encoded_data)

        config = FileModelTestConfig.DataModel()
        res = config.load( rawData=content )
        if not res:
            QMessageBox.critical(self, "Open Failed" , "Corrupted file")
            return  
        
        if inputs:
            self.parameters.table().loadData(  data = config.properties['properties']['parameters'] )
            self.currentDoc.dataModel.properties['properties']['inputs-parameters'] = config.properties['properties']['parameters']
        else:
            self.parametersOutput.table().loadData(  data = config.properties['properties']['parameters'] )
            self.currentDoc.dataModel.properties['properties']['outputs-parameters'] = config.properties['properties']['parameters']
        self.currentDoc.setModify()
        del config

    def dataChanged (self):
        """
        Called when data on all table view changed
        On description
        """
        if self.currentDoc is not None:  
            if isinstance(self.currentDoc, self.lRepo.TestPlan.WTestPlan):
                self.currentDoc.updateStatsTestPlan()
            self.currentDoc.setModify()

    def clear (self):
        """
        Clear contents
        """
        self.descrs.clear()
        self.descrs.table().defaultActions()
        
        self.parameters.clear()
        self.parametersOutput.clear()
        
        self.probes.clear()
        self.agents.clear()
        
        self.steps.clear()
        self.adapters.clear()
        self.libraries.clear()

    def addDescriptions (self, wdoc):
        """
        Add description

        @param wdoc: 
        @type wdoc:
        """
        if isinstance(wdoc, TestData.WTestData):
            self.descrs.table().setDatasetView()
        else:
            self.descrs.table().setDefaultView()
        if type(wdoc) == dict:
            if not 'descriptions' in wdoc:
                wdoc['descriptions'] = { 'description': [  { 'key': 'author', 'value': '' }, 
                                                            { 'key':  'date', 'value':  '' },
                                                            { 'key': 'summary', 'value': '' } ] }
            self.descrs.table().loadData( data = wdoc['descriptions'] )
        else:
            self.currentDoc = wdoc
            data = wdoc.dataModel.properties['properties']['descriptions']
            self.descrs.table().loadData( data = data )
            self.descrs.table().setWdoc( wdoc=wdoc )

    def addAgents (self, wdoc):
        """
        Add agents

        @param wdoc: 
        @type wdoc:
        """
        if type(wdoc) == dict:
            self.agents.table().loadData( data = wdoc['agents'] )
        else:
            self.currentDoc = wdoc
            data = wdoc.dataModel.properties['properties']['agents']
            self.agents.table().loadData( data = data )

    def addParameters (self, wdoc):
        """
        Add parameters

        @param wdoc: 
        @type wdoc:
        """
        if isinstance(wdoc, TestData.WTestData):
            self.parameters.table().setDatasetView()
        else:
            self.parameters.table().setDefaultView()
        if type(wdoc) == dict:
            self.parameters.table().loadData( data = wdoc['inputs-parameters'] )
        else:
            self.currentDoc = wdoc
            data = wdoc.dataModel.properties['properties']['inputs-parameters']
            self.parameters.table().loadData( data = data )

    def addParametersOutput (self, wdoc):
        """
        Add parameters

        @param wdoc: 
        @type wdoc:
        """
        if isinstance(wdoc, TestData.WTestData):
            self.parametersOutput.table().setDatasetView()
        else:
            self.parametersOutput.table().setDefaultView()
        if type(wdoc) == dict:
            self.parametersOutput.table().loadData( data = wdoc['outputs-parameters'] )
        else:
            self.currentDoc = wdoc
            data = wdoc.dataModel.properties['properties']['outputs-parameters']
            self.parametersOutput.table().loadData( data = data )

    def addProbes (self, wdoc):
        """
        Add probes

        @param wdoc: 
        @type wdoc:
        """
        if type(wdoc) == dict:
            self.probes.table().loadData( data = wdoc['probes'] )
        else:
            self.currentDoc = wdoc
            data = wdoc.dataModel.properties['properties']['probes']
            self.probes.table().loadData(data = data)

    def addSteps (self, wdoc):
        """
        Add steps

        @param wdoc: 
        @type wdoc:
        """
        self.steps.table().setSteps(steps=wdoc.dataModel.steps['steps']['step'] )

    def addAdapters (self, wdoc):
        """
        Add adapters

        @param wdoc: 
        @type wdoc:
        """
        self.adapters.table().setAdapters(adapters=wdoc.dataModel.adapters['adapters']['adapter'] )

    def addLibraries (self, wdoc):
        """
        Add libraries

        @param wdoc: 
        @type wdoc:
        """
        self.libraries.table().setLibraries(libraries=wdoc.dataModel.libraries['libraries']['library'] )

    def disableOutputParameters(self):
        """
        Disable output parameters tabulation
        """
        self.parametersOutput.clear()
        self.paramsTab.setTabEnabled(TAB_OUTPUTS, False)

    def enableOutputParameters(self):
        """
        Enable output parameters tabulation
        """
        self.paramsTab.setTabEnabled(TAB_OUTPUTS, True)

    def disableAgents(self):
        """
        Disable agents tabulation
        """
        self.agents.clear()
        self.miscsTab.setTabEnabled(TAB_AGENTS, False)

    def enableAgents(self):
        """
        Enable agents tabulation
        """
        self.miscsTab.setTabEnabled(TAB_AGENTS, True)

    def disableProbes(self):
        """
        Disable probes tabulation
        """
        self.probes.clear()
        self.miscsTab.setTabEnabled(TAB_PROBES, False)

    def enableProbes(self):
        """
        Enable probes tabulation
        """
        self.miscsTab.setTabEnabled(TAB_PROBES, True)

    def disableSteps(self):
        """
        Disable steps tabulation
        """
        self.steps.clear()
        self.parametersTab.setTabEnabled(TAB_STEPS, False)

    def enableSteps(self):
        """
        Enable steps tabulation
        """
        self.parametersTab.setTabEnabled(TAB_STEPS, True)

    def disableAdapters(self):
        """
        Disable adapters tabulation
        """
        self.adapters.clear()
        self.paramsTab.setTabEnabled(TAB_ADAPTERS, False)

    def enableAdapters(self):
        """
        Enable adapters tabulation
        """
        self.paramsTab.setTabEnabled(TAB_ADAPTERS, True)

    def disableLibraries(self):
        """
        Disable libraries tabulation
        """
        self.libraries.clear()
        self.paramsTab.setTabEnabled(TAB_LIBRARIES, False)

    def enableLibraries(self):
        """
        Enable libraries tabulation
        """
        self.paramsTab.setTabEnabled(TAB_LIBRARIES, True)

    def inputNameChanged(self, oldName, newName):
        """
        On input name changed
        """
        if self.currentDoc is not None:
            if isinstance(self.currentDoc, TestUnit.WTestUnit):
                editor = self.currentDoc.srcEditor
                newText = editor.text().replace("input('%s')" % oldName, "input('%s')" % newName)
                editor.setText(newText)
            elif isinstance(self.currentDoc, TestSuite.WTestSuite):
                editorSrc = self.currentDoc.srcEditor
                editorExec = self.currentDoc.execEditor
                editorSrc.setText( editorSrc.text().replace("input('%s')" % oldName, "input('%s')" % newName) )
                editorExec.setText( editorExec.text().replace("input('%s')" % oldName, "input('%s')" % newName) )
            else:
                self.error('unknown file type')

    def outputNameChanged(self, oldName, newName):
        """
        On output name changed
        """
        if self.currentDoc is not None:
            if isinstance(self.currentDoc, TestUnit.WTestUnit):
                editor = self.currentDoc.srcEditor
                newText = editor.text().replace("output('%s')" % oldName, "output('%s')" % newName)
                editor.setText(newText)
            elif isinstance(self.currentDoc, TestSuite.WTestSuite):
                editorSrc = self.currentDoc.srcEditor
                editorExec = self.currentDoc.execEditor
                editorSrc.setText( editorSrc.text().replace("output('%s')" % oldName, "output('%s')" % newName) )
                editorExec.setText( editorExec.text().replace("output('%s')" % oldName, "output('%s')" % newName) )
            else:
                self.error('unknown file type')

WDP = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return WDP

def initialize (parent, iRepo, lRepo, rRepo):
    """
    Initialize WDocumentProperties widget
    """
    global WDP
    WDP = WDocumentProperties(parent, iRepo, lRepo, rRepo)

def finalize ():
    """
    Destroy Singleton
    """
    global WDP
    if WDP:
        WDP = None