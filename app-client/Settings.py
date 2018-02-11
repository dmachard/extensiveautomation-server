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
Module to handle settings
"""

try:
    from PyQt4.QtGui import (QWidget, QGroupBox, QComboBox, QGridLayout, QLabel, QCheckBox, QPushButton, 
                            QVBoxLayout, QFileDialog, QFont, QHBoxLayout, QColor, QPalette, QFontDialog, 
                            QColorDialog, QLineEdit, QTabWidget, QSizePolicy, QIntValidator , QMessageBox, 
                            QTableWidget, QAbstractItemView, QTableWidgetItem, QMenu, QDialog, QFrame, QStyleFactory,
                            QListWidget, QListView, QStackedWidget, QDialogButtonBox, QListWidgetItem, QIcon)
    from PyQt4.QtCore import (Qt, QSize, QSettings)
except ImportError:
    from PyQt5.QtGui import (QFont, QColor, QPalette, QIntValidator, QIcon)
    from PyQt5.QtWidgets import (QWidget, QGroupBox, QComboBox, QGridLayout, QLabel, 
                            QCheckBox, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout, 
                            QFontDialog, QColorDialog, QLineEdit, QTabWidget, QSizePolicy, 
                            QMessageBox, QTableWidget, QAbstractItemView, QTableWidgetItem, 
                            QMenu, QDialog, QFrame, QListWidget, QListView, QStackedWidget, 
                            QDialogButtonBox, QListWidgetItem, QStyleFactory)
    from PyQt5.QtCore import (Qt, QSize, QSettings)
    
import sys
import os
import hashlib


try:
    xrange
except NameError: # support python3
    xrange = range
    
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
from Libs import QtHelper, Logger, PyBlowFish
import DefaultTemplates

arg = sys.argv[0]
pathname = os.path.dirname(arg)
DIR_EXEC = os.path.abspath(pathname)

def getDirExec():
    """
    Dummy function
    """
    return DIR_EXEC

def get(section, key):
    """
    Dummy function
    """
    return ""

def getInt(section, key):
    """
    Dummy function
    """
    return 0

class RepositoriesWidget(QWidget, Logger.ClassLogger):
    """
    Repositories widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(RepositoriesWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # repositories setting
        viewGroup = QGroupBox(self.tr('Default View'))
        self.reposComboBox = QComboBox(self)
        self.reposComboBox.addItem("Local Tests")
        self.reposComboBox.addItem("Remote Tests")
        self.reposComboBox.addItem("Adapters")
        self.reposComboBox.addItem("Libraries")
        self.reposComboBox.setCurrentIndex( int(instance().readValue( key = 'Repositories/default-repo-test' )) )

        self.reposDevComboBox = QComboBox(self)
        self.reposDevComboBox.addItem("Local Tests")
        self.reposDevComboBox.addItem("Remote Tests")
        self.reposDevComboBox.addItem("Adapters")
        self.reposDevComboBox.addItem("Libraries")
        self.reposDevComboBox.setCurrentIndex( int(instance().readValue( key = 'Repositories/default-repo-dev' )) )
        
        optsDfltLayout = QGridLayout()
        optsDfltLayout.addWidget( QLabel( self.tr("Defaut for tester: ") ), 0,0)
        optsDfltLayout.addWidget( self.reposComboBox, 0, 1)
        optsDfltLayout.addWidget( QLabel( self.tr("Defaut for developer: ") ), 1,0)
        optsDfltLayout.addWidget( self.reposDevComboBox, 1, 1)        
        viewGroup.setLayout(optsDfltLayout)
        
        # local repository setting
        localGroup = QGroupBox(self.tr('Local Repository Location'))
        self.repoPathSetting = instance().readValue( key = 'Repositories/local-repo' )
        self.currentRepoFolder = QLabel( self.tr("Current Folder: ") + "%s" % self.repoPathSetting )
        self.repoActiveCheckBox = QCheckBox( "%s\n%s" % (self.tr("Set the default local repository location to save"),
                                                    self.tr("your tests files."))  )
        self.localRepositoryButton = QPushButton(self.tr("Browse..."))
        self.localRepositoryButton.setEnabled(False)
        if self.repoPathSetting != "Undefined":
            self.repoActiveCheckBox.setChecked(True)
            self.localRepositoryButton.setEnabled(True)
        
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget( QLabel( "%s" % self.tr('Warning: use the remote repository for all features!') ) )
        optionsLayout.addWidget(self.repoActiveCheckBox)
        optionsLayout.addWidget(self.localRepositoryButton)
        optionsLayout.addWidget(self.currentRepoFolder)
        localGroup.setLayout(optionsLayout)

        # final layout   
        subLayout = QGridLayout()
        subLayout.addWidget(localGroup, 0, 0)
        subLayout.addWidget(viewGroup, 0, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        
    def createConnections (self):
        """
        Create pyqt connection
        """
        self.repoActiveCheckBox.stateChanged.connect(self.enableLocalRepo)
        self.localRepositoryButton.clicked.connect(self.getLocalPathRepository)

    def getLocalPathRepository (self):
        """
        Returns path repository
        """
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, self.tr("Settings -> Directory"), "", options)
        if directory:
            self.repoPathSetting = directory 

    def enableLocalRepo(self, state):
        """
        Enable repository
        """
        if state != 0:
            self.localRepositoryButton.setEnabled(True)
        else:
            self.localRepositoryButton.setEnabled(False)
            self.repoPathSetting = "Undefined"
            
    def saveSettings(self):
        """
        Save settings
        """
        # retrieve user values
        newRepoTest = "%s" % self.reposComboBox.currentIndex()
        newRepoDev = "%s" % self.reposDevComboBox.currentIndex()

        # save it
        instance().setValue( key = 'Repositories/local-repo', value = self.repoPathSetting )
        instance().setValue( key = 'Repositories/default-repo-test', value = newRepoTest )
        instance().setValue( key = 'Repositories/default-repo-dev', value = newRepoDev )

class TestsWritingWidget(QWidget, Logger.ClassLogger):
    """
    Tests writing widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TestsWritingWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # editor settings
        editorGroup = QGroupBox(self.tr("Test Code Editor"))
        
        self.codeWrappingCheckBox = QCheckBox( self.tr("Use code wrapping") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/code-wrapping' )): 
            self.codeWrappingCheckBox.setChecked(True)
        
        self.codeFoldingCheckBox = QCheckBox( self.tr("Use code folding") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/code-folding' )): 
            self.codeFoldingCheckBox.setChecked(True)

        self.indentGuidesCheckBox = QCheckBox( self.tr("Show indent guides") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/indent-guides-visible' )):  
            self.indentGuidesCheckBox.setChecked(True)

        self.wsCheckBox = QCheckBox( self.tr("Show all whitespaces and tabultations") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/ws-visible' )):  
            self.wsCheckBox.setChecked(True)

        self.lnCheckBox = QCheckBox( self.tr("Show lines numbering") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/lines-numbering' )):  
            self.lnCheckBox.setChecked(True)
        
        self.acbCheckBox = QCheckBox( self.tr("Automatic close bracket") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/auto-close-bracket' )):  
            self.acbCheckBox.setChecked(True)

        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.codeWrappingCheckBox)
        optionsLayout.addWidget(self.codeFoldingCheckBox)
        optionsLayout.addWidget(self.indentGuidesCheckBox)
        optionsLayout.addWidget(self.wsCheckBox)
        optionsLayout.addWidget(self.lnCheckBox)
        optionsLayout.addWidget(self.acbCheckBox)
        editorGroup.setLayout(optionsLayout)

        # font options
        fontGroup = QGroupBox(self.tr("Test Font Editor"))
        fontSetting = instance().readValue( key = 'Editor/font' )
        self.font = QLabel( fontSetting )
        self.font.setStyleSheet("QLabel { background-color: white; color: black;}")
        self.font.setFont( QFont(fontSetting)  )
        self.fontButton = QPushButton("Edit")
        layoutFont = QHBoxLayout()
        layoutFont.addWidget( QLabel( self.tr("Default font: ") )  )
        layoutFont.addWidget( self.font  )
        layoutFont.addWidget( self.fontButton )
        fontGroup.setLayout(layoutFont)

         # find and replace options
        findGroup = QGroupBox(self.tr("Find And Replace Bar"))
        
        self.findCaseCheckBox = QCheckBox( self.tr("Case sensitive") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/find-case-sensitive' )):  
            self.findCaseCheckBox.setChecked(True)
        self.findWholeCheckBox = QCheckBox( self.tr("Whole word") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/find-whole-word' )):  
            self.findWholeCheckBox.setChecked(True)
        self.findWrapCheckBox = QCheckBox( self.tr("Wrap at the end") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/find-wrap' )):    
            self.findWrapCheckBox.setChecked(True)
        self.findRegexpCheckBox = QCheckBox( self.tr("Regular expression") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/find-regexp' )):   
            self.findRegexpCheckBox.setChecked(True)
        self.replaceAllCheckBox = QCheckBox( self.tr("Replace all occurrences") )
        if QtHelper.str2bool(instance().readValue( key = 'Editor/replace-all' )):   
            self.replaceAllCheckBox.setChecked(True)
        
        layoutFind = QVBoxLayout()
        layoutFind.addWidget(self.findCaseCheckBox)
        layoutFind.addWidget(self.findWholeCheckBox)
        layoutFind.addWidget(self.findWrapCheckBox)
        layoutFind.addWidget(self.findRegexpCheckBox)
        layoutFind.addWidget(self.replaceAllCheckBox)
        findGroup.setLayout(layoutFind)

        # test properties setting
        propertiesGroup = QGroupBox(self.tr("Test Properties"))
        self.inputsAsDefaultCheckBox = QCheckBox(self.tr("Inputs tabulation as default view"))
        if QtHelper.str2bool(instance().readValue( key = 'TestProperties/inputs-default-tab' )):   
            self.inputsAsDefaultCheckBox.setChecked(True)
            
        self.renameAutoCheckBox = QCheckBox(self.tr("Rename automatic of inputs/outputs in tests on changed"))
        if QtHelper.str2bool(instance().readValue( key = 'TestProperties/parameters-rename-auto' )):  
            self.renameAutoCheckBox.setChecked(True)
            
        self.sortAutoCheckBox = QCheckBox(self.tr("Automatically sorting inputs/outputs"))
        if QtHelper.str2bool(instance().readValue( key = 'TestProperties/parameters-sort-auto' )):  
            self.sortAutoCheckBox.setChecked(True)
            
        self.hideDescrCheckBox = QCheckBox(self.tr("Hide description column in test parameters"))
        if QtHelper.str2bool(instance().readValue( key = 'TestProperties/parameters-hide-description' )):  
            self.hideDescrCheckBox.setChecked(True)
            
        self.showOpeningCheckBox = QCheckBox(self.tr("Always show test properties on opening"))
        if QtHelper.str2bool(instance().readValue( key = 'TestProperties/show-on-opening' )):  
            self.showOpeningCheckBox.setChecked(True)
            
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.inputsAsDefaultCheckBox)
        optionsLayout.addWidget(self.renameAutoCheckBox)
        optionsLayout.addWidget(self.sortAutoCheckBox)
        optionsLayout.addWidget(self.hideDescrCheckBox)
        optionsLayout.addWidget(self.showOpeningCheckBox)
        propertiesGroup.setLayout(optionsLayout)
        
        # colors 
        colorGroup = QGroupBox(self.tr("Colors Editor"))
        self.labelCurrentLine = QLabel( self.tr("Current Line") )
        self.eventCurrentLineColorLabel = QLabel(instance().readValue( key = 'Editor/color-current-line' ))
        color2 = QColor(instance().readValue( key = 'Editor/color-current-line' ))
        if color2.isValid(): 
            self.eventCurrentLineColorLabel.setText(color2.name())
            self.eventCurrentLineColorLabel.setPalette(QPalette(color2))
            self.eventCurrentLineColorLabel.setAutoFillBackground(True)

        self.currentLineColorButton = QPushButton("Edit")
        layoutCurrentLine = QHBoxLayout()
        layoutCurrentLine.addWidget(self.labelCurrentLine)
        layoutCurrentLine.addWidget(self.eventCurrentLineColorLabel)
        layoutCurrentLine.addWidget(self.currentLineColorButton)
            
        self.labelSelectedText = QLabel( self.tr("Selected Text") )
        self.eventSelectedTextColorLabel = QLabel(instance().readValue( key = 'Editor/color-selection-background' ))
        color2 = QColor(instance().readValue( key = 'Editor/color-selection-background' ))
        if color2.isValid(): 
            self.eventSelectedTextColorLabel.setText(color2.name())
            self.eventSelectedTextColorLabel.setPalette(QPalette(color2))
            self.eventSelectedTextColorLabel.setAutoFillBackground(True)
            
        self.selectedTextColorButton = QPushButton("Edit")
        layoutEventSelectedText = QHBoxLayout()
        layoutEventSelectedText.addWidget(self.labelSelectedText)
        layoutEventSelectedText.addWidget(self.eventSelectedTextColorLabel)
        layoutEventSelectedText.addWidget(self.selectedTextColorButton)
            
        self.labelIndicator = QLabel( self.tr("Indicator") )
        self.eventIndicatorColorLabel = QLabel(instance().readValue( key = 'Editor/color-indicator' ))
        color2 = QColor(instance().readValue( key = 'Editor/color-indicator' ))
        if color2.isValid(): 
            self.eventIndicatorColorLabel.setText(color2.name())
            self.eventIndicatorColorLabel.setPalette(QPalette(color2))
            self.eventIndicatorColorLabel.setAutoFillBackground(True)
            
        self.indicatorColorButton = QPushButton("Edit")
        layoutEventIndicator = QHBoxLayout()
        layoutEventIndicator.addWidget(self.labelIndicator)
        layoutEventIndicator.addWidget(self.eventIndicatorColorLabel)
        layoutEventIndicator.addWidget(self.indicatorColorButton)
        
        optionsColorLayout = QVBoxLayout()
        optionsColorLayout.addLayout(layoutCurrentLine)
        optionsColorLayout.addLayout(layoutEventSelectedText)
        optionsColorLayout.addLayout(layoutEventIndicator)
        colorGroup.setLayout(optionsColorLayout)
        
        # automation assistant
        automationGroup = QGroupBox(self.tr("Automation Assistant"))
        self.stopFailureCheckBox = QCheckBox(self.tr("Stop on step failure ?"))
        if QtHelper.str2bool(instance().readValue( key = 'TestGenerator/stop-on-failure' )):   
            self.stopFailureCheckBox.setChecked(True)
        self.mergeStepsCheckBox = QCheckBox(self.tr("Merge all steps in one?"))
        if QtHelper.str2bool(instance().readValue( key = 'TestGenerator/merge-all-steps' )):   
            self.mergeStepsCheckBox.setChecked(True)
            
        layoutAutomation = QVBoxLayout()
        layoutAutomation.addWidget(self.stopFailureCheckBox)
        layoutAutomation.addWidget(self.mergeStepsCheckBox)
        automationGroup.setLayout(layoutAutomation)
        
        # test plan or global
        tpGroup = QGroupBox(self.tr("Test Plan or Global"))
        self.hideTpRepoColumnCheckBox = QCheckBox(self.tr("Hide repository column"))
        if QtHelper.str2bool(instance().readValue( key = 'TestPlan/hide-repo-column' )):   
            self.hideTpRepoColumnCheckBox.setChecked(True)
            
        self.hideTpAliasColumnCheckBox = QCheckBox(self.tr("Hide alias column"))
        if QtHelper.str2bool(instance().readValue( key = 'TestPlan/hide-alias-column' )):   
            self.hideTpAliasColumnCheckBox.setChecked(True)
            
        self.hideTpTagColumnCheckBox = QCheckBox(self.tr("Hide tag column"))
        if QtHelper.str2bool(instance().readValue( key = 'TestPlan/hide-tag-column' )):   
            self.hideTpTagColumnCheckBox.setChecked(True)
            
        self.hideTpRunColumnCheckBox = QCheckBox(self.tr("Hide run column"))
        if QtHelper.str2bool(instance().readValue( key = 'TestPlan/hide-run-column' )):   
            self.hideTpRunColumnCheckBox.setChecked(True)
            
        self.openDoubleClickCheckBox = QCheckBox(self.tr("Open original test on double click"))
        if QtHelper.str2bool(instance().readValue( key = 'TestPlan/open-doubleclick' )):   
            self.openDoubleClickCheckBox.setChecked(True)
            
        layoutTp = QVBoxLayout()
        layoutTp.addWidget(self.hideTpRepoColumnCheckBox)
        layoutTp.addWidget(self.hideTpAliasColumnCheckBox)
        layoutTp.addWidget(self.hideTpTagColumnCheckBox)
        layoutTp.addWidget(self.hideTpRunColumnCheckBox)
        layoutTp.addWidget(self.openDoubleClickCheckBox)
        tpGroup.setLayout(layoutTp)
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(editorGroup, 0, 0)
        subLayout.addWidget(findGroup, 0, 1)
        subLayout.addWidget(fontGroup, 1, 0)
        subLayout.addWidget(colorGroup, 1, 1)
        subLayout.addWidget(propertiesGroup, 2, 0)
        subLayout.addWidget(automationGroup, 2, 1)
        subLayout.addWidget(tpGroup, 3, 0)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
    
    def createConnections(self):
        """
        Create connections
        """
        self.fontButton.clicked.connect(self.setFont)
        self.currentLineColorButton.clicked.connect(self.setColorCurrentLine)
        self.selectedTextColorButton.clicked.connect(self.setColorSelectedText)
        self.indicatorColorButton.clicked.connect(self.setColorIndicator)
        
    def setFont(self):
        """
        Set the font of the python editor
        """
        fontSettings = self.font.text()
        fontSettings = fontSettings.split(",")
        defaultFont = QFont(fontSettings[0], int(fontSettings[1]))
        font, ok = QFontDialog.getFont(defaultFont, self)
        if ok:
            self.font.setText( font.key() )
            self.font.setFont(font)   
    
    def setColorCurrentLine(self):
        """
        Set the color of the selection event
        """
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid(): 
            self.eventCurrentLineColorLabel.setText(color.name())
            self.eventCurrentLineColorLabel.setPalette(QPalette(color))
            self.eventCurrentLineColorLabel.setAutoFillBackground(True)
    
    def setColorSelectedText(self):
        """
        Set the color of the selection event
        """
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid(): 
            self.eventSelectedTextColorLabel.setText(color.name())
            self.eventSelectedTextColorLabel.setPalette(QPalette(color))
            self.eventSelectedTextColorLabel.setAutoFillBackground(True)
    
    def setColorIndicator(self):
        """
        Set the color of the selection event
        """
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid(): 
            self.eventIndicatorColorLabel.setText(color.name())
            self.eventIndicatorColorLabel.setPalette(QPalette(color))
            self.eventIndicatorColorLabel.setAutoFillBackground(True)
            
    def saveSettings(self):
        """
        Save settings
        """
        renameAuto = False
        sortAuto = False
        defaultTab = False
        hideDescr = False
        showOpening = False
        
        autoBracket = False
        codeWrapping = False
        codeFolding = False
        guidesVisible = False
        wsVisible = False
        lineNumbering = False
        caseSensitive = False
        wholeWord = False
        wrapAll = False
        regExp = False
        replaceAll = False
        
        stopFailure = False
        mergeSteps = False
        
        # retrieve user values
        if self.stopFailureCheckBox.checkState() :  stopFailure = True
        if self.mergeStepsCheckBox.checkState() :  mergeSteps = True
        
        if self.inputsAsDefaultCheckBox.checkState() :  defaultTab = True
        if self.renameAutoCheckBox.checkState() : renameAuto = True
        if self.sortAutoCheckBox.checkState() : sortAuto = True
        if self.hideDescrCheckBox.checkState() : hideDescr = True
        if self.showOpeningCheckBox.checkState() : showOpening = True
        
        if self.codeWrappingCheckBox.checkState() :  codeWrapping = True
        if self.codeFoldingCheckBox.checkState() :  codeFolding = True
        if self.indentGuidesCheckBox.checkState() :   guidesVisible = True
        if self.wsCheckBox.checkState() : wsVisible = True
        if self.lnCheckBox.checkState() : lineNumbering= True
        if self.acbCheckBox.checkState() : autoBracket= True
        if self.findCaseCheckBox.checkState() : caseSensitive= True
        if self.findWholeCheckBox.checkState() : wholeWord = True
        if self.findWrapCheckBox.checkState() : wrapAll = True
        if self.findRegexpCheckBox.checkState() : regExp = True
        if self.replaceAllCheckBox.checkState() : replaceAll = True
        newFont =  "%s" % self.font.text()
        
        currentLineColor = "%s" % self.eventCurrentLineColorLabel.text()
        selectedTextColor  = "%s" % self.eventSelectedTextColorLabel.text()
        indicatorColor  = "%s" % self.eventIndicatorColorLabel.text()
        
        hideTpRepoColumn = False
        hideTpAliasColumn = False
        hideTpTagColumn = False
        hideTpRunColumn = False
        openDoubleClick = False
        if self.hideTpRepoColumnCheckBox.checkState() :  hideTpRepoColumn = True
        if self.hideTpAliasColumnCheckBox.checkState() :  hideTpAliasColumn = True
        if self.hideTpTagColumnCheckBox.checkState() :  hideTpTagColumn = True
        if self.hideTpRunColumnCheckBox.checkState() :  hideTpRunColumn = True
        if self.openDoubleClickCheckBox.checkState() :  openDoubleClick = True
        
        # save it
        instance().setValue( key = 'TestGenerator/stop-on-failure', value = "%s" % stopFailure )
        instance().setValue( key = 'TestGenerator/merge-all-steps', value = "%s" % mergeSteps )
        
        instance().setValue( key = 'TestPlan/hide-repo-column', value = "%s" % hideTpRepoColumn )
        instance().setValue( key = 'TestPlan/hide-alias-column', value = "%s" % hideTpAliasColumn )
        instance().setValue( key = 'TestPlan/hide-tag-column', value = "%s" % hideTpTagColumn )
        instance().setValue( key = 'TestPlan/hide-run-column', value = "%s" % hideTpRunColumn )
        instance().setValue( key = 'TestPlan/open-doubleclick', value = "%s" % openDoubleClick )
        
        instance().setValue( key = 'TestProperties/inputs-default-tab', value = "%s" % defaultTab )
        instance().setValue( key = 'TestProperties/parameters-rename-auto', value = "%s" % renameAuto)
        instance().setValue( key = 'TestProperties/parameters-sort-auto', value = "%s" % sortAuto)
        instance().setValue( key = 'TestProperties/parameters-hide-description', value = "%s" % hideDescr)
        instance().setValue( key = 'TestProperties/show-on-opening', value = "%s" % showOpening)
        
        instance().setValue( key = 'Editor/code-wrapping', value = "%s" % codeWrapping)
        instance().setValue( key = 'Editor/code-folding', value = "%s" % codeFolding)
        instance().setValue( key = 'Editor/indent-guides-visible',  value = "%s" % guidesVisible  )
        instance().setValue( key = 'Editor/ws-visible', value = "%s" % wsVisible )
        instance().setValue( key = 'Editor/lines-numbering', value = "%s" % lineNumbering )
        instance().setValue( key = 'Editor/font', value = newFont )
        instance().setValue( key = 'Editor/auto-close-bracket', value = "%s" % autoBracket )
        
        instance().setValue( key = 'Editor/find-wrap', value = "%s" % wrapAll )
        instance().setValue( key = 'Editor/find-case-sensitive', value = "%s" % caseSensitive )
        instance().setValue( key = 'Editor/find-whole-word', value = "%s" % wholeWord )
        instance().setValue( key = 'Editor/find-regexp', value = "%s" % regExp )
        instance().setValue( key = 'Editor/replace-all', value = "%s" % replaceAll )
        
        instance().setValue( key = 'Editor/color-current-line', value = currentLineColor )
        instance().setValue( key = 'Editor/color-selection-background', value = selectedTextColor )
        instance().setValue( key = 'Editor/color-indicator', value = indicatorColor )

class TestsArchivingWidget(QWidget, Logger.ClassLogger):
    """
    Tests archiving widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TestsArchivingWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # run settings
        viewGroup = QGroupBox(self.tr("Default Tabulation View"))
        self.reportComboBox = QComboBox(self)
        self.reportComboBox.addItem("Advanced")
        self.reportComboBox.addItem("Basic")
        self.reportComboBox.setCurrentIndex( int(instance().readValue( key = 'TestArchives/default-report-tab' )) )

        optsDfltLayout = QGridLayout()
        optsDfltLayout.addWidget( QLabel( self.tr("Test report: ") ), 0,0)
        optsDfltLayout.addWidget( self.reportComboBox, 0, 1)    
        viewGroup.setLayout(optsDfltLayout)

        
        # archives setting
        archivesGroup = QGroupBox(self.tr('Archives Repository Location'))
        self.archivesSettings = instance().readValue( key = 'TestArchives/download-directory' )
        self.currentArchivesFolder = QLabel( self.tr("Current Folder: ") + "%s" % self.archivesSettings )
        
        self.archivesActiveCheckBox = QCheckBox( "%s\n%s" % (self.tr("Set the default downloads location to save"), 
                                                    self.tr("your test results files.")) )
        self.archiveRepositoryButton = QPushButton(self.tr("Browse..."))
        self.archiveRepositoryButton.setEnabled(False)
        if self.archivesSettings != "Undefined":
            self.archivesActiveCheckBox.setChecked(True)
            self.archiveRepositoryButton.setEnabled(True)

        archivesLayout = QVBoxLayout()
        archivesLayout.addWidget(self.archivesActiveCheckBox)
        archivesLayout.addWidget(self.archiveRepositoryButton)
        archivesLayout.addWidget(self.currentArchivesFolder)
        archivesGroup.setLayout(archivesLayout)

        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(viewGroup, 0, 0)
        subLayout.addWidget(archivesGroup, 0, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        
    def createConnections (self):
        """
        Create pyqt connection
        """
        self.archivesActiveCheckBox.stateChanged.connect(self.enableArchivesRepo)
        self.archiveRepositoryButton.clicked.connect(self.getArchivesPathRepository)
            
    def getArchivesPathRepository (self):
        """
        Returns the path of the repository
        """
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, self.tr("Settings -> Directory"), "", options)
        if directory:
            self.archivesSettings = directory
            self.currentArchivesFolder.setText( self.tr("Current Folder: ") + "%s" % self.archivesSettings )

    def enableArchivesRepo(self, state):
        """
        Enable repository
        """
        if state != 0:
            self.archiveRepositoryButton.setEnabled(True)
        else:
            self.archiveRepositoryButton.setEnabled(False)
            self.archivesSettings = "Undefined"
            
    def saveSettings(self):
        """
        Save settings
        """
        newTabReport = "%s" % self.reportComboBox.currentIndex()
        
        instance().setValue( key = 'TestArchives/default-report-tab', value = newTabReport )
        instance().setValue( key = 'TestArchives/download-directory', value = self.archivesSettings )
        
class TestsRunWidget(QWidget, Logger.ClassLogger):
    """
    Tests run widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TestsRunWidget, self).__init__(parent)
        self.createWidgets()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # run settings
        runGroup = QGroupBox(self.tr("Immediate Run"))

        self.autoFocusTrCheckBox = QCheckBox(self.tr("Automatic focus on test run"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-focus' )):  self.autoFocusTrCheckBox.setChecked(True)
        self.autoSaveTrCheckBox = QCheckBox(self.tr("Automatic save before test execution"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-save' )):  self.autoSaveTrCheckBox.setChecked(True)
        self.newWindowCheckBox = QCheckBox(self.tr("New window on test run (dual screen)"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/new-window' )):   self.newWindowCheckBox.setChecked(True)
        self.minimizeAppCheckBox = QCheckBox(self.tr("Minimize application on test run"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/minimize-app' )):   self.minimizeAppCheckBox.setChecked(True)
        self.reduceAppCheckBox = QCheckBox(self.tr("Reduce application on test run"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/reduce-app' )):   self.reduceAppCheckBox.setChecked(True)
        
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.autoFocusTrCheckBox)
        optionsLayout.addWidget(self.autoSaveTrCheckBox)
        optionsLayout.addWidget(self.newWindowCheckBox)
        optionsLayout.addWidget(self.minimizeAppCheckBox)
        optionsLayout.addWidget(self.reduceAppCheckBox)
        runGroup.setLayout(optionsLayout)
        
        # schedule settings
        scheduleGroup = QGroupBox(self.tr("Schedule Run"))
        self.keepTrCheckBox = QCheckBox(self.tr("Do not keep test result on success"))
        if QtHelper.str2bool(instance().readValue( key = 'ScheduleRun/dont-keep-result-on-success' )):  self.keepTrCheckBox.setChecked(True)
        schedLayout = QVBoxLayout()
        schedLayout.addWidget(self.keepTrCheckBox)
        scheduleGroup.setLayout(schedLayout)
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(runGroup, 0, 0)
        subLayout.addWidget(scheduleGroup, 1, 0)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        
    def saveSettings(self):
        """
        Save settings
        """
        minimizeApp = False
        reduceApp = False
        autoFocus = False
        autoSave = False
        newWindow = False
        dontKeep = False
        
        # retrieve user values
        if self.autoFocusTrCheckBox.checkState() :  autoFocus = True
        if self.autoSaveTrCheckBox.checkState() : autoSave = True
        if self.newWindowCheckBox.checkState() : newWindow = True
        if self.minimizeAppCheckBox.checkState() :  minimizeApp = True
        if self.reduceAppCheckBox.checkState() : reduceApp = True
        if self.keepTrCheckBox.checkState() : dontKeep = True
        
        # save it
        instance().setValue( key = 'TestRun/auto-focus', value = "%s" % autoFocus )
        instance().setValue( key = 'TestRun/auto-save', value = "%s" % autoSave )
        instance().setValue( key = 'TestRun/new-window', value = "%s" % newWindow )
        instance().setValue( key = 'TestRun/minimize-app', value = "%s" % minimizeApp )
        instance().setValue( key = 'TestRun/reduce-app', value = "%s" % reduceApp )
        instance().setValue( key = 'ScheduleRun/dont-keep-result-on-success', value = "%s" % dontKeep )
        
class TestsAnalysisWidget(QWidget, Logger.ClassLogger):
    """
    Tests analysis widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TestsAnalysisWidget, self).__init__(parent)

        self.createWidgets()
        self.createConnections()
        
    def createConnections(self):
        """
        Create connections
        """
        self.eventColorButton.clicked.connect(self.setColorSelectionEvent)
        self.eventColor2Button.clicked.connect(self.setColorTextSelectionEvent)
        
    def createWidgets(self):
        """
        Create widgets
        """
        # general settings
        generalGroup = QGroupBox(self.tr("General"))

        self.hideResumeViewCheckBox = QCheckBox(self.tr("Hide resume view"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/hide-resume-view' )):    self.hideResumeViewCheckBox.setChecked(True)
        self.askKillCheckBox = QCheckBox(self.tr("Ask before kill a test"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/ask-before-kill' )):   self.askKillCheckBox.setChecked(True)
        
        self.alwaysExpandedCheckBox = QCheckBox(self.tr("Tests always expanded"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/tests-expanded' )):   self.alwaysExpandedCheckBox.setChecked(True)
        
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.hideResumeViewCheckBox)
        optionsLayout.addWidget(self.askKillCheckBox)
        optionsLayout.addWidget(self.alwaysExpandedCheckBox)
        generalGroup.setLayout(optionsLayout)
        
         # view detailed
        viewFilterGroup = QGroupBox(self.tr("Detailed view"))
        self.labelViewFilterCol = QLabel( self.tr("Defaut column") )
        self.filterViewColumnComboBox = QComboBox(self)
        self.filterViewColumnComboBox.addItem("Raw")
        self.filterViewColumnComboBox.addItem("Xml")
        self.filterViewColumnComboBox.addItem("Html")
        self.filterViewColumnComboBox.addItem("Image")
        self.filterViewColumnComboBox.addItem("Hexa")
        self.filterViewColumnComboBox.setCurrentIndex( int(instance().readValue( key = 'TestRun/default-tab-view' )) )
        optionsViewFilterLayout = QHBoxLayout()
        optionsViewFilterLayout.addWidget(self.labelViewFilterCol)
        optionsViewFilterLayout.addWidget(self.filterViewColumnComboBox)
        viewFilterGroup.setLayout(optionsViewFilterLayout)

        # view logging
        viewLoggingGroup = QGroupBox(self.tr("Logging view"))
        self.labelViewLoggingCol = QLabel( self.tr("Defaut logging view") )
        self.loggingViewColumnComboBox = QComboBox(self)
        self.loggingViewColumnComboBox.addItem("Events")
        self.loggingViewColumnComboBox.addItem("Diagram")
        self.loggingViewColumnComboBox.setCurrentIndex( int(instance().readValue( key = 'TestRun/default-tab-run' )) )
        optionsViewLoggingLayout = QHBoxLayout()
        optionsViewLoggingLayout.addWidget(self.labelViewLoggingCol)
        optionsViewLoggingLayout.addWidget(self.loggingViewColumnComboBox)
        viewLoggingGroup.setLayout(optionsViewLoggingLayout)

        # filter
        filterGroup = QGroupBox(self.tr("Filter"))
        self.labelFilter = QLabel( self.tr("Defaut pattern") )
        self.filterPatternLineEdit = QLineEdit( instance().readValue( key = 'TestRun/event-filter-pattern' ) )
        self.filterEvent = QHBoxLayout()
        self.filterEvent.addWidget(self.labelFilter)
        self.filterEvent.addWidget(self.filterPatternLineEdit)

        self.labelFilterCol = QLabel( self.tr("Defaut column") )
        self.filterColumnComboBox = QComboBox(self)
        self.filterColumnComboBox.addItem("No.")
        self.filterColumnComboBox.addItem("Timestamp")
        self.filterColumnComboBox.addItem("From")
        self.filterColumnComboBox.addItem("To")
        self.filterColumnComboBox.addItem("Event Type")
        self.filterColumnComboBox.addItem("Component Type")
        self.filterColumnComboBox.addItem("Text")
        self.filterColumnComboBox.setCurrentIndex(int( instance().readValue( key = 'TestRun/event-filter-column' ) ))

        self.filterColumnEvent = QHBoxLayout()
        self.filterColumnEvent.addWidget(self.labelFilterCol)
        self.filterColumnEvent.addWidget(self.filterColumnComboBox)
        
        optionsFilterLayout = QVBoxLayout()
        optionsFilterLayout.addLayout(self.filterEvent)
        optionsFilterLayout.addLayout(self.filterColumnEvent)
        filterGroup.setLayout(optionsFilterLayout)

        # colors 
        colorGroup = QGroupBox(self.tr("Colors"))
        self.labelEventSelection = QLabel( self.tr("Event selection") )
        self.eventSelectionColorLabel = QLabel(instance().readValue( key = 'TestRun/textual-selection-color' ))
        color2 = QColor(instance().readValue( key = 'TestRun/textual-selection-color' ))
        if color2.isValid(): 
            self.eventSelectionColorLabel.setText(color2.name())
            self.eventSelectionColorLabel.setPalette(QPalette(color2))
            self.eventSelectionColorLabel.setAutoFillBackground(True)

        self.eventColorButton = QPushButton("Edit")
        self.layoutEvent = QHBoxLayout()
        self.layoutEvent.addWidget(self.labelEventSelection)
        self.layoutEvent.addWidget(self.eventSelectionColorLabel)
        self.layoutEvent.addWidget(self.eventColorButton)

        self.labelEventSelectionText = QLabel( self.tr("Event selection text") )
        self.eventTextSelectionColorLabel = QLabel()
        color = QColor(instance().readValue( key = 'TestRun/textual-text-selection-color' ))
        if color.isValid(): 
            self.eventTextSelectionColorLabel.setText(color.name())
            self.eventTextSelectionColorLabel.setPalette(QPalette(color))
            self.eventTextSelectionColorLabel.setAutoFillBackground(True)

        self.eventColor2Button = QPushButton("Edit")
        self.layoutEvent2 = QHBoxLayout()
        self.layoutEvent2.addWidget(self.labelEventSelectionText)
        self.layoutEvent2.addWidget(self.eventTextSelectionColorLabel)
        self.layoutEvent2.addWidget(self.eventColor2Button)

        optionsColorLayout = QVBoxLayout()
        optionsColorLayout.addLayout(self.layoutEvent)
        optionsColorLayout.addLayout(self.layoutEvent2)
        colorGroup.setLayout(optionsColorLayout)

        # details view
        detailsGroup = QGroupBox(self.tr("Details Events View"))

        self.layoutDetails = QVBoxLayout()
        self.autoSelectTemplatesCheckBox = QCheckBox(self.tr("Automatic item selection on events template comparaison"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-selection-templates' )):   self.autoSelectTemplatesCheckBox.setChecked(True)

        self.autoExpandTemplatesCheckBox = QCheckBox( self.tr("Automatic expand/collapse for template events comparaison"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-expandcollapse-templates' )):  self.autoExpandTemplatesCheckBox.setChecked(True)

        self.autoExpandEventsCheckBox = QCheckBox( self.tr("Automatic expand/collapse for events"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-expandcollapse-events' )):  self.autoExpandEventsCheckBox.setChecked(True)
        
        self.layoutDetails.addWidget(self.autoExpandTemplatesCheckBox)
        self.layoutDetails.addWidget(self.autoExpandEventsCheckBox)
        self.layoutDetails.addWidget(self.autoSelectTemplatesCheckBox)
        
        optionsDetailsLayout = QVBoxLayout()
        optionsDetailsLayout.addLayout(self.layoutDetails)
        detailsGroup.setLayout(optionsDetailsLayout)
        
        # autoscrolling settings
        autoscrollGroup = QGroupBox(self.tr("Auto scrolling options"))
        self.autoScrollTrCheckBox = QCheckBox( "%s\n%s" % (self.tr("Autoscolling on events view"),
                                    self.tr("Warning: be careful with this option, high cpu utilization can happened!")))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-scrolling-textual' )):  self.autoScrollTrCheckBox.setChecked(True)

        self.autoScrollTestsTrCheckBox = QCheckBox(self.tr("Autoscolling on tests view"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-scrolling-tests' )): self.autoScrollTestsTrCheckBox.setChecked(True)

        self.autoScrollDiagramTrCheckBox = QCheckBox(self.tr("Autoscolling on diagram"))
        if QtHelper.str2bool(instance().readValue( key = 'TestRun/auto-scrolling-graph' )): self.autoScrollDiagramTrCheckBox.setChecked(True)
            
        optionsAutoLayout = QVBoxLayout()
        optionsAutoLayout.addWidget(self.autoScrollTrCheckBox)
        optionsAutoLayout.addWidget(self.autoScrollTestsTrCheckBox)
        optionsAutoLayout.addWidget(self.autoScrollDiagramTrCheckBox)
        autoscrollGroup.setLayout(optionsAutoLayout)
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(viewFilterGroup, 0, 0)
        subLayout.addWidget(viewLoggingGroup, 0, 1)
        subLayout.addWidget(filterGroup, 1, 0)
        subLayout.addWidget(colorGroup, 1, 1)
        subLayout.addWidget(detailsGroup, 2, 0)
        subLayout.addWidget(autoscrollGroup, 2, 1)
        subLayout.addWidget(generalGroup, 3, 0)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
    
    def setColorSelectionEvent(self):
        """
        Set the color of the selection event
        """
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid(): 
            self.eventSelectionColorLabel.setText(color.name())
            self.eventSelectionColorLabel.setPalette(QPalette(color))
            self.eventSelectionColorLabel.setAutoFillBackground(True)

    def setColorTextSelectionEvent(self):
        """
        Set color text selection event
        """
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid(): 
            self.eventTextSelectionColorLabel.setText(color.name())
            self.eventTextSelectionColorLabel.setPalette(QPalette(color))
            self.eventTextSelectionColorLabel.setAutoFillBackground(True)   
            
    def saveSettings(self):
        """
        Save settings
        """
        alwaysExpanded = False
        beforeKill = False
        autoExpandTemplates = False
        autoSelectionTemplates = False
        autoExpandEvents = False
        autoScrollText = False
        autoScrollTests = False
        autoScrollGraph = False
        hideResume = False
        
        # retrieve user values
        if self.alwaysExpandedCheckBox.checkState() : alwaysExpanded = True
        if self.askKillCheckBox.checkState() : beforeKill = True
        if self.autoExpandTemplatesCheckBox.checkState() : autoExpandTemplates = True
        if self.autoSelectTemplatesCheckBox.checkState() : autoSelectionTemplates = True
        if self.autoExpandEventsCheckBox.checkState() :  autoExpandEvents = True
        if self.autoScrollTrCheckBox.checkState() : autoScrollText = True
        if self.autoScrollTestsTrCheckBox.checkState() : autoScrollTests = True
        if self.autoScrollDiagramTrCheckBox.checkState() : autoScrollGraph = True
        if self.hideResumeViewCheckBox.checkState() :    hideResume = True
        newFilterPattern = "%s" % self.filterPatternLineEdit.text()
        newFilterColumn = "%s" % self.filterColumnComboBox.currentIndex()
        newViewColumn = "%s" % self.filterViewColumnComboBox.currentIndex()
        newTabRun = "%s" % self.loggingViewColumnComboBox.currentIndex()
        newColor = "%s" % self.eventSelectionColorLabel.text()
        newTextColor = "%s" % self.eventTextSelectionColorLabel.text()
        
        # save it
        instance().setValue( key = 'TestRun/auto-expandcollapse-templates', value = "%s" % autoExpandTemplates )
        instance().setValue( key = 'TestRun/auto-expandcollapse-events', value = "%s" % autoExpandEvents )
        instance().setValue( key = 'TestRun/auto-selection-templates', value = "%s" % autoSelectionTemplates )
        instance().setValue( key = 'TestRun/auto-scrolling-textual', value = "%s" % autoScrollText )
        instance().setValue( key = 'TestRun/auto-scrolling-tests', value = "%s" % autoScrollTests )
        instance().setValue( key = 'TestRun/hide-resume-view', value = "%s" % hideResume )
        instance().setValue( key = 'TestRun/event-filter-pattern', value = newFilterPattern )
        instance().setValue( key = 'TestRun/event-filter-column', value = newFilterColumn )
        instance().setValue( key = 'TestRun/default-tab-view', value = newViewColumn )
        instance().setValue( key = 'TestRun/textual-selection-color', value = newColor )
        instance().setValue( key = 'TestRun/textual-text-selection-color', value = newTextColor )
        instance().setValue( key = 'TestRun/auto-scrolling-graph', value = "%s" % autoScrollGraph )
        instance().setValue( key = 'TestRun/default-tab-run', value = newTabRun )
        instance().setValue( key = 'TestRun/ask-before-kill', value = "%s" % beforeKill )
        instance().setValue( key = 'TestRun/tests-expanded', value = "%s" % alwaysExpanded )

class TestsTemplatesWidget(QWidget, Logger.ClassLogger):
    """
    Tests templates widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(TestsTemplatesWidget, self).__init__(parent)
        self.defaultTemplates = DefaultTemplates.Templates()
        
        self.createWidgets()
        self.loadTemplates()
        
    def createWidgets(self):
        """
        Create widgets
        """
        self.mainTab = QTabWidget()

        # test suite
        self.tsTab = QTabWidget()
        self.tsTab.setTabPosition(QTabWidget.East)
        self.tsManualWidget = QWidget()
        self.tsAutoWidget = QWidget()
 
        self.tplDefEdit = QtHelper.RawPythonEditor(parent=self)
        self.tplExecEdit = QtHelper.RawPythonEditor(parent=self)
        self.tplDefEditAuto = QtHelper.RawPythonEditor(parent=self)
        self.tplExecEditAuto = QtHelper.RawPythonEditor(parent=self)

        tsLayout = QVBoxLayout()
        tsLayout.addWidget( self.tplDefEdit )
        tsLayout.addWidget( self.tplExecEdit )
        self.tsManualWidget.setLayout(tsLayout)

        tsLayoutAuto = QVBoxLayout()
        tsLayoutAuto.addWidget( self.tplDefEditAuto )
        tsLayoutAuto.addWidget( self.tplExecEditAuto )
        self.tsAutoWidget.setLayout(tsLayoutAuto)

        self.tsTab.addTab( self.tsManualWidget, self.tr('Manual') )
        self.tsTab.addTab( self.tsAutoWidget, self.tr('Automatic') )

        # test unit
        self.tuTab = QTabWidget()
        self.tuTab.setTabPosition(QTabWidget.East)
        
        self.tuManualWidget = QWidget()
        self.tuAutoWidget = QWidget()

        self.tuTplDefEdit = QtHelper.RawPythonEditor(parent=self)
        self.tuTplDefEdit.setFixedHeight(500)
        tuLayout = QVBoxLayout()
        tuLayout.addWidget( self.tuTplDefEdit )
        self.tuManualWidget.setLayout(tuLayout)

        self.tuTplDefEditAuto = QtHelper.RawPythonEditor(parent=self)
        
        tuLayoutAuto = QVBoxLayout()
        tuLayoutAuto.addWidget( self.tuTplDefEditAuto )
        self.tuAutoWidget.setLayout(tuLayoutAuto)
        
        self.tuTab.addTab( self.tuManualWidget, self.tr('Manual') )
        self.tuTab.addTab( self.tuAutoWidget, self.tr('Automatic') )

        # add tab to main
        self.mainTab.addTab( self.tuTab, self.tr('Test Unit') )
        self.mainTab.addTab( self.tsTab, self.tr('Test Suite') )

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.mainTab)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
    
    def loadTemplates(self):
        """
        Load templates
        """
        # test unit
        self.tuTplDefEdit.setText( self.defaultTemplates.getTestUnitDefinition() )
        self.tuTplDefEditAuto.setText( self.defaultTemplates.getTestUnitDefinitionAuto() )
        
        # test suite
        self.tplDefEdit.setText( self.defaultTemplates.getTestDefinition() )
        self.tplExecEdit.setText( self.defaultTemplates.getTestExecution() )
        # auto
        self.tplDefEditAuto.setText( self.defaultTemplates.getTestDefinitionAuto() )
        self.tplExecEditAuto.setText( self.defaultTemplates.getTestExecutionAuto() )

    def toUtf8(self, string):
        """
        To utf8
        Will be deprecated with python3
        """
        return string.encode("utf8")
        
    def saveTemplates(self):
        """
        Save templates
        """
        if sys.version_info > (3,): # python3 support
            # test unit
            self.defaultTemplates.setTestUnitDefinition( data= self.tuTplDefEdit.toPlainText() )
            self.defaultTemplates.setTestUnitDefinitionAuto( data= self.tuTplDefEditAuto.toPlainText() )
            
            # test suite
            self.defaultTemplates.setTestDefinition( data=self.tplDefEdit.toPlainText() )
            self.defaultTemplates.setTestExecution( data=self.tplExecEdit.toPlainText() )
            self.defaultTemplates.setTestDefinitionAuto( data=self.tplDefEditAuto.toPlainText() )
            self.defaultTemplates.setTestExecutionAuto( data=self.tplExecEditAuto.toPlainText() )
        else:
            # test unit
            self.defaultTemplates.setTestUnitDefinition( data= self.tuTplDefEdit.toPlainText().toUtf8() )
            self.defaultTemplates.setTestUnitDefinitionAuto( data= self.tuTplDefEditAuto.toPlainText().toUtf8() )
            
            # test suite
            self.defaultTemplates.setTestDefinition( data=self.tplDefEdit.toPlainText().toUtf8() )
            self.defaultTemplates.setTestExecution( data=self.tplExecEdit.toPlainText().toUtf8() )
            self.defaultTemplates.setTestDefinitionAuto( data=self.tplDefEditAuto.toPlainText().toUtf8() )
            self.defaultTemplates.setTestExecutionAuto( data=self.tplExecEditAuto.toPlainText().toUtf8() )

    def saveSettings(self):
        """
        Save settings
        """
        # save it
        try:
            self.saveTemplates()
        except Exception as e:
            self.error( "unable to save templates for tests: %s" % e )
           
class ModulesTemplatesWidget(QWidget, Logger.ClassLogger):
    """
    Modules templates widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ModulesTemplatesWidget, self).__init__(parent)
        self.defaultTemplates = DefaultTemplates.Templates()
        
        self.createWidgets()
        self.loadTemplates()

    def createWidgets(self):
        """
        Create widgets
        """
        self.mainTab = QTabWidget()

        # adapter
        self.adpTplDefEdit = QtHelper.RawPythonEditor(parent=self)
        self.adpTplDefEdit.setFixedHeight(500)
        
        # library
        self.libTplDefEdit = QtHelper.RawPythonEditor(parent=self)

        # add tab to main
        self.mainTab.addTab( self.adpTplDefEdit, self.tr('Adapter') )
        self.mainTab.addTab( self.libTplDefEdit, self.tr('Library') )
        
        # final layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.mainTab)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def loadTemplates(self):
        """
        Load template
        """
        self.adpTplDefEdit.setText( self.defaultTemplates.getAdapter() )
        self.libTplDefEdit.setText( self.defaultTemplates.getLibrary() )

    def saveTemplates(self):
        """
        Save template
        """
        self.defaultTemplates.setAdapter( data=str( self.adpTplDefEdit.toPlainText() ) )
        self.defaultTemplates.setLibrary( data=str( self.libTplDefEdit.toPlainText() ) )

    def saveSettings(self):
        """
        Save settings
        """
        # save it
        try:
            self.saveTemplates()
        except Exception as e:
            self.error( "unable to save templates for development: %s" % e )
            
class NetworkWidget(QWidget, Logger.ClassLogger):
    """
    Network widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(NetworkWidget, self).__init__(parent)
        self.createWidgets()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # secure
        secureGroup = QGroupBox(self.tr('SSL Support'))

        httpsWsSetting = QtHelper.str2bool( instance().readValue( key = 'Server/api-ssl' ) )
        self.httpsWsCheckBox = QCheckBox( self.tr("Api Channel") )
        if httpsWsSetting: self.httpsWsCheckBox.setChecked(True)
        dataSetting = QtHelper.str2bool( instance().readValue( key = 'Server/data-ssl' ) )
        self.dataSslCheckBox = QCheckBox( self.tr("Data Channel") )
        if dataSetting: self.dataSslCheckBox.setChecked(True)
        
        secureLayout = QVBoxLayout()
        secureLayout.addWidget( self.httpsWsCheckBox)
        secureLayout.addWidget( self.dataSslCheckBox)
        secureGroup.setLayout(secureLayout)

        # ports setting
        portsGroup = QGroupBox(self.tr('Ports'))

        self.portDataEdit = QLineEdit(instance().readValue( key = 'Server/port-data' ))
        self.portDataEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        validator = QIntValidator (self)
        self.portDataEdit.setValidator(validator)

        self.portWsEdit = QLineEdit(instance().readValue( key = 'Server/port-api' ))
        self.portWsEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        validator = QIntValidator (self)
        self.portWsEdit.setValidator(validator)
        
        portsLayout = QGridLayout()
        portsLayout.addWidget( QLabel("Tcp/Data: "), 1, 0 )
        portsLayout.addWidget( self.portDataEdit, 1, 1 )
        portsLayout.addWidget( QLabel("Tcp/Api: "), 2, 0 )
        portsLayout.addWidget( self.portWsEdit, 2, 1 )
        portsGroup.setLayout(portsLayout)
        
        # new in v12.1 - proxy setting
        proxyGroup = QGroupBox(self.tr('Proxy'))
        
        proxySetting = QtHelper.str2bool( instance().readValue( key = 'Server/proxy-active' ) )
        self.proxyCheckBox = QCheckBox( self.tr("Use proxy for server access") )
        if proxySetting: self.proxyCheckBox.setChecked(True)
        
        proxyWebSetting = QtHelper.str2bool( instance().readValue( key = 'Server/proxy-web-active' ) )
        self.proxyWebCheckBox = QCheckBox( self.tr("Use proxy for internet access") )
        if proxyWebSetting: self.proxyWebCheckBox.setChecked(True)

        self.portProxyEdit = QLineEdit(instance().readValue( key = 'Server/port-proxy-http' ))
        self.portProxyEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        validator = QIntValidator (self)
        self.portProxyEdit.setValidator(validator)

        self.addressProxyEdit = QLineEdit(instance().readValue( key = 'Server/addr-proxy-http' ))
        
        proxyLayout = QGridLayout()
        proxyLayout.addWidget( QLabel("Proxy Address"), 1, 0 )
        proxyLayout.addWidget( self.addressProxyEdit, 1, 1 )
        proxyLayout.addWidget( QLabel("Proxy Port"), 2, 0 )
        proxyLayout.addWidget( self.portProxyEdit, 2, 1 )
        proxyLayout.addWidget( self.proxyCheckBox, 3, 0 )
        proxyLayout.addWidget( self.proxyWebCheckBox, 4, 0 )
        
        proxyGroup.setLayout(proxyLayout)
        # end of new
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(secureGroup, 0, 0)
        subLayout.addWidget(portsGroup, 0, 1)
        subLayout.addWidget(proxyGroup, 1, 0)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)
        
        self.setLayout(mainLayout)
        
    def saveSettings(self):
        """
        Save settings
        """
        newApiSsl = False
        newDataSsl = False  
        
        # retrieve user values
        if self.httpsWsCheckBox.checkState(): newApiSsl = True
        if self.dataSslCheckBox.checkState(): newDataSsl = True

        portApi = "%s" % self.portWsEdit.text()
        portData = "%s" % self.portDataEdit.text()

        instance().setValue( key = 'Server/api-ssl', value = "%s" % newApiSsl )
        instance().setValue( key = 'Server/data-ssl', value = "%s" % newDataSsl )
        instance().setValue( key = 'Server/port-api', value = portApi )
        instance().setValue( key = 'Server/port-data', value = portData )
        
        # new in v12.1
        proxyActivated = False
        proxyWebActivated = False  
        if self.proxyCheckBox.checkState(): proxyActivated = True
        if self.proxyWebCheckBox.checkState(): proxyWebActivated = True
        proxyAddr = "%s" % self.addressProxyEdit.text()
        proxyPort = "%s" % self.portProxyEdit.text()
        
        instance().setValue( key = 'Server/proxy-active', value = "%s" % proxyActivated )
        instance().setValue( key = 'Server/proxy-web-active', value = "%s" % proxyWebActivated )
        instance().setValue( key = 'Server/addr-proxy-http', value = proxyAddr )
        instance().setValue( key = 'Server/port-proxy-http', value = proxyPort )
        
class GeneralWidget(QWidget, Logger.ClassLogger):
    """
    General widget
    """
    def __init__(self, parent=None):
        """
        Constrcutor
        """
        super(GeneralWidget, self).__init__(parent)
        self.stylesItem = QStyleFactory.keys()

        self.langsItem = ("us_US", )
        self.levelsItem = ("INFO", "DEBUG" )
        self.createWidgets()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # user interface setting
        styleGroup = QGroupBox(self.tr("User Interface"))
        welcomeSetting = QtHelper.str2bool( instance().readValue( key = 'Common/welcome-page' ) )
        self.welcomeCheckBox = QCheckBox("Show welcome page")
        if welcomeSetting: self.welcomeCheckBox.setChecked(True)
        
        styleSetting = instance().readValue( key = 'Common/style-%s' % sys.platform )
        self.styleComboBox = QComboBox(self)
        self.styleComboBox.setMinimumWidth (250)
        
        tabLeftSetting = QtHelper.str2bool( instance().readValue( key = 'View/tab-left' ) )
        self.tabLeftCheckBox = QCheckBox("Use widget tabulation on left part")
        if tabLeftSetting: self.tabLeftCheckBox.setChecked(True)
        
        currentIndex = 0
        for i in xrange(len(self.stylesItem)):
            if self.stylesItem[i] == styleSetting :
                currentIndex = i
            self.styleComboBox.addItem(self.stylesItem[i])
        self.styleComboBox.setCurrentIndex(currentIndex)
        
        styleLayout = QVBoxLayout()
        
        styleSubLayout = QHBoxLayout()
        styleSubLayout.addWidget( QLabel( self.tr("Look and feel:") ) )
        styleSubLayout.addWidget( self.styleComboBox )
        
        styleLayout.addLayout( styleSubLayout )
        styleLayout.addWidget( self.welcomeCheckBox )
        styleLayout.addWidget( self.tabLeftCheckBox )
        styleGroup.setLayout(styleLayout)

        # user language setting
        langGroup = QGroupBox(self.tr("User Language"))
        langSetting = instance().readValue( key = 'Common/language' )
        self.langComboBox = QComboBox(self)
        self.langComboBox.setMinimumWidth (250)
        currentIndex = 0
        for i in xrange(len(self.langsItem)):
            if self.langsItem[i] == langSetting :
                currentIndex = i
            self.langComboBox.addItem(self.langsItem[i])
        self.langComboBox.setCurrentIndex(currentIndex)
        langLayout = QHBoxLayout()
        langLayout.addWidget( QLabel( self.tr("Language:") ) )
        langLayout.addWidget( self.langComboBox )
        langGroup.setLayout(langLayout)
        
        # notification setting
        updateGroup = QGroupBox(self.tr("Update"))
        updateSetting = QtHelper.str2bool( instance().readValue( key = 'Update/enable' ) )
        self.updateMessageCheckBox = QCheckBox("Automatic check update")
        if updateSetting: self.updateMessageCheckBox.setChecked(True)
        updateLayout = QHBoxLayout()
        updateLayout.addWidget(self.updateMessageCheckBox)
        updateGroup.setLayout(updateLayout)
        
        # notification setting
        notifGroup = QGroupBox(self.tr("Notifications"))
        notifSetting = QtHelper.str2bool( instance().readValue( key = 'Common/systray-notifications' ) )
        self.systrayMessageCheckBox = QCheckBox("Enable notifications on system tray")
        if notifSetting: self.systrayMessageCheckBox.setChecked(True)
        notifLayout = QHBoxLayout()
        notifLayout.addWidget(self.systrayMessageCheckBox)
        notifGroup.setLayout(notifLayout)
        
        # trace setting
        traceGroup = QGroupBox(self.tr("Logging Application"))
        traceSetting = instance().readValue( key = 'Trace/level' )
        self.traceComboBox = QComboBox(self)
        self.traceComboBox.setMinimumWidth (250)
        currentIndex = 0
        for i in xrange(len(self.levelsItem)):
            if self.levelsItem[i] == traceSetting :
                currentIndex = i
            self.traceComboBox.addItem(self.levelsItem[i])
        self.traceComboBox.setCurrentIndex(currentIndex)
        traceLayout = QHBoxLayout()
        traceLayout.addWidget( QLabel( self.tr("Level:") ) )
        traceLayout.addWidget( self.traceComboBox )
        traceGroup.setLayout(traceLayout)

        # keyboard shorcuts
        shorcutsGroup = QGroupBox(self.tr("Keyboard shorcuts"))

        self.developerShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/developer' ))
        self.exitShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/exit' ))
        self.fullShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/fullscreen' ))
        self.searchShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/search' ))
        self.saveShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/save' ))
        self.printShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/print' ))
        self.runShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/run' ))
        self.stepsShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/steps' ))
        self.breakpointShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/breakpoint' ))
        self.assistantShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/assistant' ))
        self.syntaxShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/syntax' ))
        self.aboutShorcutEdit = QLineEdit(instance().readValue( key = 'KeyboardShorcuts/about' ))
        
        shorcutsLayout = QGridLayout()
        shorcutsLayout.addWidget( QLabel("Developer View: "), 2, 0 )
        shorcutsLayout.addWidget( self.developerShorcutEdit, 2, 1 )
        shorcutsLayout.addWidget( QLabel("Run test: "), 3, 0 )
        shorcutsLayout.addWidget( self.runShorcutEdit, 3, 1 )
        shorcutsLayout.addWidget( QLabel("Check the syntax of a test: "), 4, 0 )
        shorcutsLayout.addWidget( self.syntaxShorcutEdit, 4, 1 )
        shorcutsLayout.addWidget( QLabel("Open test assistant: "), 5, 0 )
        shorcutsLayout.addWidget( self.assistantShorcutEdit, 5, 1 )
        shorcutsLayout.addWidget( QLabel("Open about page: "), 6, 0 )
        shorcutsLayout.addWidget( self.aboutShorcutEdit, 6, 1 )
        shorcutsLayout.addWidget( QLabel("Run a test with breakpoint: "), 7, 0 )
        shorcutsLayout.addWidget( self.breakpointShorcutEdit, 7, 1 )
        shorcutsLayout.addWidget( QLabel("Run a test step by step: "), 8, 0 )
        shorcutsLayout.addWidget( self.stepsShorcutEdit, 8, 1 )
        shorcutsLayout.addWidget( QLabel("Enter in fullscreen mode: "), 9, 0 )
        shorcutsLayout.addWidget( self.fullShorcutEdit, 9, 1 )
        shorcutsLayout.addWidget( QLabel("Open search text module: "), 10, 0 )
        shorcutsLayout.addWidget( self.searchShorcutEdit, 10, 1 )
        shorcutsLayout.addWidget( QLabel("Save a test: "), 11, 0 )
        shorcutsLayout.addWidget( self.saveShorcutEdit, 11, 1 )
        shorcutsLayout.addWidget( QLabel("Print a test: "), 12, 0 )
        shorcutsLayout.addWidget( self.printShorcutEdit, 12, 1 )
        shorcutsLayout.addWidget( QLabel("Exit application: "), 13, 0 )
        shorcutsLayout.addWidget( self.exitShorcutEdit, 13, 1 )
        shorcutsGroup.setLayout(shorcutsLayout)
        
        # final layout
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(styleGroup)
        leftLayout.addWidget(langGroup)
        leftLayout.addWidget(notifGroup)
        leftLayout.addWidget(updateGroup)
        leftLayout.addWidget(traceGroup)
        leftLayout.addStretch(1)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(shorcutsGroup)
        
        
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)

        self.setLayout(mainLayout)

    def saveSettings(self):
        """
        Save settings
        """
        newUpdate = False
        newNotif = False
        welcomePage = False
        tabLeft = False
        
        # retrieve user values
        newStyle = "%s" % self.styleComboBox.currentText()
        newLang = "%s" % self.langComboBox.currentText()
        newLevel = "%s" % self.traceComboBox.currentText()
        if self.systrayMessageCheckBox.checkState(): newNotif = True
        if self.welcomeCheckBox.checkState(): welcomePage = True
        if self.updateMessageCheckBox.checkState(): newUpdate = True
        if self.tabLeftCheckBox.checkState(): tabLeft = True
        
        developerData = "%s" % self.developerShorcutEdit.text()
        runData = "%s" % self.runShorcutEdit.text()
        syntaxData = "%s" % self.syntaxShorcutEdit.text()
        assistantData = "%s" % self.assistantShorcutEdit.text()
        aboutData = "%s" % self.aboutShorcutEdit.text()
        breakpointData = "%s" % self.breakpointShorcutEdit.text()
        stepsData = "%s" % self.stepsShorcutEdit.text()
        fullData = "%s" % self.fullShorcutEdit.text()
        searchData = "%s" % self.searchShorcutEdit.text()
        saveData = "%s" % self.saveShorcutEdit.text()
        printData = "%s" % self.printShorcutEdit.text()
        exitData = "%s" % self.exitShorcutEdit.text()
        
        # save it
        instance().setValue( key = 'Trace/level' , value = newLevel )
        Logger.reloadLevel(level=newLevel)
        instance().setValue( key = 'Common/systray-notifications' , value = "%s" % newNotif  )
        instance().setValue( key = 'Update/enable' , value = "%s" % newUpdate  )
        instance().setValue( key = 'Common/welcome-page' , value = "%s" % welcomePage  )
        instance().setValue( key = 'View/tab-left' , value = "%s" % tabLeft  )
        oldSetting = instance().readValue( key = 'Common/style-%s' % sys.platform )
        if newStyle != oldSetting:
            instance().setValue( key = 'Common/style-%s' % sys.platform , value = newStyle )
            QMessageBox.information(self, self.tr("Preferences > User Interface") ,  self.tr("Please to restart the application!") )

        # new in v13.1
        instance().setValue( key = 'KeyboardShorcuts/fullscreen', value = fullData )
        instance().setValue( key = 'KeyboardShorcuts/developer', value = developerData )
        instance().setValue( key = 'KeyboardShorcuts/save', value = saveData )
        instance().setValue( key = 'KeyboardShorcuts/print', value = printData )
        instance().setValue( key = 'KeyboardShorcuts/steps', value = stepsData )
        instance().setValue( key = 'KeyboardShorcuts/breakpoint', value = breakpointData )
        instance().setValue( key = 'KeyboardShorcuts/syntax', value = syntaxData )
        instance().setValue( key = 'KeyboardShorcuts/assistant', value = assistantData )
        instance().setValue( key = 'KeyboardShorcuts/about', value = aboutData )
        instance().setValue( key = 'KeyboardShorcuts/exit', value = exitData )
        instance().setValue( key = 'KeyboardShorcuts/run', value = runData )
        instance().setValue( key = 'KeyboardShorcuts/search', value = searchData )

        
class ToolsExternalWidget(QWidget, Logger.ClassLogger):
    """
    Tools external
    """
    ToolEnable, ToolName, ToolPath, ToolType, ToolLocal = range(5)
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ToolsExternalWidget, self).__init__(parent)
        self.createWidgets()
        self.createActions()
        self.createConnections()
        self.populateTable()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # list  setting
        toolsGroup = QGroupBox(self.tr("List of tools"))
        
        self.tableWidget = QTableWidget(0, 5)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        headerLabels = ("Enable","Name", "Path", "Application", "Local")
        self.tableWidget.setHorizontalHeaderLabels(headerLabels)
        
        toolsLayout = QHBoxLayout()
        toolsLayout.addWidget(self.tableWidget)
        toolsGroup.setLayout(toolsLayout)

        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(toolsGroup, 0, 0)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def createActions(self):
        """
        Create actions
        """
        self.addAction = QtHelper.createAction(self, self.tr("&Add"), self.addTool, icon = None, 
                                            tip = self.tr('Add a new application') )
        self.delAction = QtHelper.createAction(self, self.tr("&Delete"), self.delTool, icon = None, 
                                            tip = self.tr('Delete the selected application') )

    def createConnections(self):
        """
        Create connections
        """
        self.tableWidget.customContextMenuRequested.connect(self.onPopupMenu)
    
    def addTool(self):
        """
        Add tool
        """
        nbRows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(nbRows) 
        
        itemEnable = QTableWidgetItem()
        itemEnable.setCheckState(True)
        itemEnable.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable )
        self.tableWidget.setItem(nbRows, 0, itemEnable)
        
        itemType = QTableWidgetItem()
        itemType.setCheckState(True)
        itemType.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable )
        self.tableWidget.setItem(nbRows, 3, itemType)
        
        itemLocal = QTableWidgetItem()
        itemLocal.setCheckState(False)
        itemLocal.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable )
        self.tableWidget.setItem(nbRows, 4, itemLocal)
        
    def delTool(self):
        """
        Del tool
        """
        rowId = self.tableWidget.currentRow()
        self.tableWidget.removeRow(rowId) 
          
    def onPopupMenu(self, pos):
        """
        On popup menu
        """
        self.menu = QMenu()
        self.menu.addAction( self.addAction )
        self.menu.addAction( self.delAction )
        self.menu.addSeparator()
        self.menu.popup( self.tableWidget.mapToGlobal(pos))
        
    def populateTable(self):
        """
        Populate table
        """
        tableData = []
        
        i = 1
        toolInfo =  instance().readToolValue( key = 'Tool_%s/app-name' % i )
        if len(toolInfo):
            toolEnable = instance().readToolValue( key = 'Tool_%s/app-enable' % i )
            toolName = instance().readToolValue( key = 'Tool_%s/app-name' % i )
            toolLocal = instance().readToolValue( key = 'Tool_%s/app-local' % i )
            toolType = instance().readToolValue( key = 'Tool_%s/app-ide' % i )
            toolPath = instance().readToolValue( key = 'Tool_%s/app-path' % i )
            tableData.append( (toolEnable, toolName, toolPath, toolType, toolLocal) )
            
        while len(toolInfo):
            i += 1
            toolInfo = instance().readToolValue( key = 'Tool_%s/app-name' % i )
            if len(toolInfo):
                toolEnable = instance().readToolValue( key = 'Tool_%s/app-enable' % i )
                toolName = instance().readToolValue( key = 'Tool_%s/app-name' % i )
                toolLocal = instance().readToolValue( key = 'Tool_%s/app-local' % i )
                toolType = instance().readToolValue( key = 'Tool_%s/app-ide' % i )
                toolPath = instance().readToolValue( key = 'Tool_%s/app-path' % i )
                tableData.append( (toolEnable, toolName, toolPath, toolType, toolLocal) )

        for row, (toolEnable, toolName, toolPath, toolType, toolLocal) in enumerate(tableData):
            self.addTool()
            item0 = QTableWidgetItem()
            item0.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable )
            if toolEnable == "True": item0.setCheckState(True)
            else:  item0.setCheckState(False)
            
            item1 = QTableWidgetItem(toolName)
            item2 = QTableWidgetItem(toolPath)
            
            item3 = QTableWidgetItem()
            item3.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable )
            if toolType == "True": item3.setCheckState(True)
            else:  item3.setCheckState(False)
            
            item4 = QTableWidgetItem()
            item4.setFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable )
            if toolLocal == "True":   item4.setCheckState(True)
            else:    item4.setCheckState(False)
            
            self.tableWidget.setItem(row, 0, item0)
            self.tableWidget.setItem(row, 1, item1)
            self.tableWidget.setItem(row, 2, item2)
            self.tableWidget.setItem(row, 3, item3)
            self.tableWidget.setItem(row, 4, item4)
        
        self.tableWidget.resizeColumnsToContents()
        
    def saveSettings(self):
        """
        Save settings
        """
        # remove tools from settings
        i = 1
        toolInfo =  instance().readToolValue( key = 'Tool_%s/app-name' % i )
        if len(toolInfo):
            instance().removeToolValue('Tool_%s' % i  )
        while len(toolInfo):
            i += 1
            toolInfo = instance().readToolValue( key = 'Tool_%s/app-name' % i )
            if len(toolInfo):
                instance().removeToolValue('Tool_%s' % i  )
                
        # adding new tools from table
        for rowId in xrange(self.tableWidget.rowCount()):
            qItem = self.tableWidget.item( rowId, ToolsExternalWidget.ToolEnable )
            if qItem is not None: 
                isEnable = "False"
                if qItem.checkState(): isEnable = "True"
                instance().setToolValue(key="Tool_%s/app-enable" % (rowId+1), value=isEnable)
            qItem = self.tableWidget.item( rowId, ToolsExternalWidget.ToolName )
            if qItem is not None:  
                instance().setToolValue(key="Tool_%s/app-name" % (rowId+1), value=qItem.text())
            qItem = self.tableWidget.item( rowId, ToolsExternalWidget.ToolPath )
            if qItem is not None:  
                instance().setToolValue(key="Tool_%s/app-path" % (rowId+1), value=qItem.text())
            qItem = self.tableWidget.item( rowId, ToolsExternalWidget.ToolType )
            if qItem is not None:  
                isEnable = "False"
                if qItem.checkState(): isEnable = "True"
                instance().setToolValue(key="Tool_%s/app-ide" % (rowId+1), value=isEnable)
            qItem = self.tableWidget.item( rowId, ToolsExternalWidget.ToolLocal )
            if qItem is not None:  
                isEnable = "False"
                if qItem.checkState(): isEnable = "True"
                instance().setToolValue(key="Tool_%s/app-local" % (rowId+1), value=isEnable)
                
class SettingsDialog(QDialog, Logger.ClassLogger):
    """
    Main dialog for settings
    """
    def __init__(self, parent=None):
        """
        Main Dialog to configure the application

        @param parent:
        @type parent:
        """
        super(SettingsDialog, self).__init__(parent)

        self.createDialog()
        self.createConnections()
        self.createIcons()
        
    def createDialog(self):
        """
        Create dialog v2 
        """
        frameStyle = QFrame.Sunken | QFrame.Panel
        
        self.GeneralConf = GeneralWidget( self )
        self.RepositoriesConf = RepositoriesWidget( self )
        self.TestsTemplatesConf = TestsTemplatesWidget( self )
        self.ModulesTemplatesConf = ModulesTemplatesWidget( self )
        self.TestsWritingConf = TestsWritingWidget( self )
        self.TestsRunConf = TestsRunWidget(self)
        self.TestsAnalysisConf = TestsAnalysisWidget( self )
        self.NetworkConf = NetworkWidget( self )
        self.ToolsConf = ToolsExternalWidget( self )
        self.TestsArchivingConf = TestsArchivingWidget( self )
        
        self.contentsWidget = QListWidget()
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.contentsWidget.setIconSize(QSize(24, 24))
        self.contentsWidget.setMovement(QListView.Static)
        self.contentsWidget.setMinimumWidth(110)
        self.contentsWidget.setMaximumWidth(110)
        self.contentsWidget.setSpacing(10)

        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.GeneralConf)
        self.pagesWidget.addWidget(self.NetworkConf)
        self.pagesWidget.addWidget(self.ModulesTemplatesConf)
        self.pagesWidget.addWidget(self.RepositoriesConf)
        self.pagesWidget.addWidget(self.TestsTemplatesConf)
        self.pagesWidget.addWidget(self.TestsWritingConf)
        self.pagesWidget.addWidget(self.TestsRunConf)
        self.pagesWidget.addWidget(self.TestsAnalysisConf)
        self.pagesWidget.addWidget(self.TestsArchivingConf)
        self.pagesWidget.addWidget(self.ToolsConf)
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.contentsWidget.setCurrentRow(0)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.buttonBox)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)
       
        self.setWindowTitle(self.tr("Preferences"))

    def changePage(self, current, previous):
        """
        Change page
        """
        if not current:
            current = previous

        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))
    
    def createIcons(self):
        """
        Create qt icons
        """
        generalButton = QListWidgetItem(self.contentsWidget)
        generalButton.setIcon(QIcon(':/setting-general.png'))
        generalButton.setText("Application")
        generalButton.setTextAlignment(Qt.AlignHCenter)
        generalButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        networkButton = QListWidgetItem(self.contentsWidget)
        networkButton.setIcon(QIcon(':/setting-network.png'))
        networkButton.setText("Networking")
        networkButton.setTextAlignment(Qt.AlignHCenter)
        networkButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        modulesTemplatesButton = QListWidgetItem(self.contentsWidget)
        modulesTemplatesButton.setIcon(QIcon(':/setting-development.png'))
        modulesTemplatesButton.setText("Development")
        modulesTemplatesButton.setTextAlignment(Qt.AlignHCenter)
        modulesTemplatesButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        repositoriesButton = QListWidgetItem(self.contentsWidget)
        repositoriesButton.setIcon(QIcon(':/setting-database.png'))
        repositoriesButton.setText("Test Listing")
        repositoriesButton.setTextAlignment(Qt.AlignHCenter)
        repositoriesButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        testTemplatesButton = QListWidgetItem(self.contentsWidget)
        testTemplatesButton.setIcon(QIcon(':/setting-tests-templates.png'))
        testTemplatesButton.setText("Test Template")
        testTemplatesButton.setTextAlignment(Qt.AlignHCenter)
        testTemplatesButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        testWritingButton = QListWidgetItem(self.contentsWidget)
        testWritingButton.setIcon(QIcon(':/setting-writing.png'))
        testWritingButton.setText("Test Writing")
        testWritingButton.setTextAlignment(Qt.AlignHCenter)
        testWritingButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        testRunButton = QListWidgetItem(self.contentsWidget)
        testRunButton.setIcon(QIcon(':/setting-testrun.png'))
        testRunButton.setText("Test Running")
        testRunButton.setTextAlignment(Qt.AlignHCenter)
        testRunButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        testAnalysisButton = QListWidgetItem(self.contentsWidget)
        testAnalysisButton.setIcon(QIcon(':/setting-analysis.png'))
        testAnalysisButton.setText("Test Analysis")
        testAnalysisButton.setTextAlignment(Qt.AlignHCenter)
        testAnalysisButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        testArchivingButton = QListWidgetItem(self.contentsWidget)
        testArchivingButton.setIcon(QIcon(':/setting-archive.png'))
        testArchivingButton.setText("Test Archives")
        testArchivingButton.setTextAlignment(Qt.AlignHCenter)
        testArchivingButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        toolsButton = QListWidgetItem(self.contentsWidget)
        toolsButton.setIcon(QIcon(':/setting-tools.png'))
        toolsButton.setText("External Tools")
        toolsButton.setTextAlignment(Qt.AlignHCenter)
        toolsButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        
        self.contentsWidget.currentItemChanged.connect(self.changePage)
        
    def createConnections(self):
        """
        Create qt connection
        """
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.reject)
    
    def onAccept(self):
        """
        On accept
        """
        self.GeneralConf.saveSettings()
        self.RepositoriesConf.saveSettings()
        self.TestsTemplatesConf.saveSettings()
        self.ModulesTemplatesConf.saveSettings()
        self.TestsWritingConf.saveSettings()
        self.TestsRunConf.saveSettings()
        self.TestsAnalysisConf.saveSettings()
        self.TestsArchivingConf.saveSettings()
        self.NetworkConf.saveSettings()
        self.ToolsConf.saveSettings()

        self.accept()

class Settings(object):
    """
    Settings accessor
    """
    def __init__(self, parent = None, offlineMode=False):
        """
        Settings of the application

        @param parent:
        @type parent:
        """
        self.offlineMode = offlineMode
        self.serverContext = {}
        self.dirExec = QtHelper.dirExec()
        # global settings
        self.settingsFileName = "settings.ini"
        self.fileName = "%s/Files/%s" % ( self.dirExec, self.settingsFileName )
        self.settings = QSettings( self.fileName,  QSettings.IniFormat    )
        
        # tools
        self.toolsFileName = "tools.ini"
        self.fileNameTools = "%s/Files/%s" % ( self.dirExec, self.toolsFileName )
        self.settingsTools = QSettings( self.fileNameTools,  QSettings.IniFormat    )
        
        self.appName = self.readValue( key = 'Common/Name' )

    def setServerContext (self, data):
        """
        Set server context

        @param data:
        @type data:
        """
        for key in  data:
            self.serverContext.update(key)

    def syncValues(self):
        """
        Synchronize value
        """
        self.settings.sync()
        self.settingsTools.sync()

    def readValue (self, key, rType = 'str'):
        """
        Read value

        @param key:
        @type key:

        @param rType: expected values in str, qstr an qlist
        @type rType: string

        @return:
        @rtype: str
        """
        ret = self.settings.value(key)
        if ret is None:
            return ''
        if rType == 'str':
            if isinstance(ret, str): # python3 support
                return ret
            return str(ret.toString())
        elif rType == 'int':
            if isinstance(ret, str): # python3 support
                return int(ret)
            return int(ret.toString())
        elif rType == 'qstr':
            if sys.version_info > (3,):  # python3 support
                return ret
            return ret.toString()
        elif rType == 'qlist':
            if sys.version_info > (3,):  # python3 support
                return ret
            return ret.toStringList()
        else:
            return ret

    def setValue(self, key, value):
        """
        Set value

        @param key:
        @type key:

        @param value:
        @type value:
        """
        self.settings.setValue( key, value)
        self.settings.sync()
        
    def removeValue(self, key):
        """
        Remove value
        """
        self.settings.remove(key)

    def readToolValue (self, key, rType = 'str'):
        """
        Read value

        @param key:
        @type key:

        @param rType: expected values in str, qstr an qlist
        @type rType: string

        @return:
        @rtype: str
        """
        ret = self.settingsTools.value(key)
        if ret is None:
            return ''
        if rType == 'str':
            if isinstance(ret, str):  # python3 support
                return ret
            return str(ret.toString())
        elif rType == 'int':
            if isinstance(ret, str):  # python3 support
                return int(ret)
            return int(ret.toString())
        elif rType == 'qstr':
            if sys.version_info > (3,):  # python3 support
                return ret
            return ret.toString()
        elif rType == 'qlist':
            if sys.version_info > (3,):   # python3 support
                return ret
            return ret.toStringList()
        else:
            return ret

    def setToolValue(self, key, value):
        """
        Set value

        @param key:
        @type key:

        @param value:
        @type value:
        """
        self.settingsTools.setValue( key, value)
        self.settingsTools.sync()
        
    def removeToolValue(self, key):
        """
        Remove value
        """
        self.settingsTools.remove(key)
        
ST = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return ST

def initialize (parent = None, offlineMode=False):
    """
    Initialize the class Settings

    @param parent:
    @type: parent:
    """
    global ST
    ST = Settings(parent, offlineMode=offlineMode)

def finalize ():
    """
    Destroy Singleton
    """
    global ST
    if ST:
        ST = None