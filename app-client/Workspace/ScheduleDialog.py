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
Scheduler module
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QLabel, QLineEdit, QIntValidator, QVBoxLayout, QRadioButton, 
                            QDateTimeEdit, QGroupBox, QGridLayout, QHBoxLayout, QIcon, QPushButton, 
                            QMessageBox, QWidget, QComboBox, QCheckBox, QButtonGroup, QStackedWidget, QFrame)
    from PyQt4.QtCore import (QDateTime, Qt, QTime, QDate, QRect)
except ImportError:
    from PyQt5.QtGui import (QIntValidator, QIcon)
    from PyQt5.QtWidgets import (QLabel, QLineEdit, QVBoxLayout, QRadioButton, QDateTimeEdit, 
                                QGroupBox, QGridLayout, QHBoxLayout, QPushButton, QMessageBox, 
                                QWidget, QComboBox, QCheckBox, QButtonGroup, QStackedWidget, QFrame)
    from PyQt5.QtCore import (QDateTime, Qt, QTime, QDate, QRect)
    
from Libs import QtHelper, Logger
import UserClientInterface as UCI

import Settings

class SchedSuccessiveDialog(QtHelper.EnhancedQDialog):
    """
    Schedule successive dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor
        """
        QtHelper.EnhancedQDialog.__init__(self, parent)

        self.name = self.tr("Successive run")

        self.createDialog()
        self.createConnections()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( self.name )

        nbLabel = QLabel( "Number of run ?" )
        self.nbLineEdit = QLineEdit("2")
        self.nbLineEdit.setValidator(QIntValidator(self.nbLineEdit))

        layout = QVBoxLayout()
        layout.addWidget(  nbLabel )
        layout.addWidget(  self.nbLineEdit )

        self.schedImmed = QRadioButton(self.tr("Immediality"))
        self.schedImmed.setChecked(True)
        self.schedAt = QRadioButton(self.tr("At:"))
        self.schedAtDateEdit = QDateTimeEdit( QDateTime.currentDateTime() )

        self.configBox = QGroupBox("Start time ?")
        configLayout = QGridLayout()
        configLayout.addWidget(self.schedImmed, 0, 0)
        configLayout.addWidget(self.schedAt, 1, 0)
        configLayout.addWidget(self.schedAtDateEdit, 1, 1)
        self.configBox.setLayout(configLayout)


        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton(self.tr("OK"), self)
        self.cancelButton = QPushButton(self.tr("Cancel"), self)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        layout.addWidget(self.configBox)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

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

    def acceptClicked (self):
        """
        Called on accept button
        """
        runNb = self.nbLineEdit.text()
        if not len(runNb):
            runNb = 0
        if int(runNb) < 2:
            QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
        else:
            self.accept()

    def getParameters(self):
        """
        Returns parameters
        """ 
        if self.schedImmed.isChecked():
            fromTime = (0,0,0,0,0,0)
        else:
            pydt = self.schedAtDateEdit.dateTime().toPyDateTime()
            fromTime = (pydt.year, pydt.month, pydt.day, pydt.hour, pydt.minute, pydt.second)
        runNb = self.nbLineEdit.text()
        return ( int(runNb), fromTime ) 

class WeeklyWidget(QWidget, Logger.ClassLogger):
    """
    Weekly widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(WeeklyWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """
        self.schedWeekly = QRadioButton("Weekly on")
        self.schedWeekly.setChecked(True)
        self.schedWeeklyH = QDateTimeEdit( )
        self.schedWeeklyH.setDisplayFormat("hh")
        self.schedWeeklyM = QDateTimeEdit( )
        self.schedWeeklyM.setDisplayFormat("mm")
        self.schedWeeklyS = QDateTimeEdit( )
        self.schedWeeklyS.setDisplayFormat("ss")

        self.comboBoxDays = QComboBox()
        #for d in UCI.SCHED_DAYS_DICT.values():
        for d in list(UCI.SCHED_DAYS_DICT.values()): # wrap to list for support python3
            self.comboBoxDays.addItem( d.title())

        self.schedNb= QCheckBox( "Number of runs" )
        self.schedNbLineEdit = QLineEdit('Unlimited')
        self.schedNbLineEdit.setValidator(QIntValidator(self.schedNbLineEdit))
        self.schedNbLineEdit.setEnabled(False)
        
        subLayout = QGridLayout()
        subLayout.addWidget(self.schedWeekly, 0, 0)
        subLayout.addWidget(self.comboBoxDays, 0, 1)
        subLayout.addWidget(QLabel(" at:"), 0, 2)
        subLayout.addWidget(self.schedWeeklyH, 0, 3)
        subLayout.addWidget( QLabel( self.tr("hour(s)") ), 0, 4)
        subLayout.addWidget(self.schedWeeklyM, 0, 5)
        subLayout.addWidget( QLabel( self.tr("minute(s)") ), 0, 6)
        subLayout.addWidget(self.schedWeeklyS, 0, 7)
        subLayout.addWidget( QLabel( self.tr("second(s)") ), 0, 8)
        
        subLayout.addWidget(self.schedNb, 1, 0)
        subLayout.addWidget(self.schedNbLineEdit, 1, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        
    def createConnections(self):
        """
        Create connections
        """
        self.schedNb.toggled.connect(self.onCheckNbToggled)
    
    def onCheckNbToggled(self, toggled):
        """
        Called on check nb toggled
        """
        if toggled:
            self.schedNbLineEdit.setEnabled(True)
            self.schedNbLineEdit.setText('')
        else:
            self.schedNbLineEdit.setEnabled(False)
            self.schedNbLineEdit.setText('Unlimited')
    
    def setTime(self, d, h, mn, s):
        """
        Set the time
        """
        self.schedWeeklyH.setTime( QTime( int(h), 0, 0 ) )
        self.schedWeeklyM.setTime( QTime( 0, int(mn), 0 ) )
        self.schedWeeklyS.setTime( QTime( 0, 0, int(s) ) )
        self.comboBoxDays.setCurrentIndex( int(d) )
            
    def setNbRun(self, nbRun):
        """
        Set number of run
        """
        if nbRun > 0:
            self.schedNb.setChecked(True)
            self.schedNbLineEdit.setText(str(nbRun))
            self.schedNbLineEdit.setEnabled(True)
            
    def getSettings(self):
        """
        Get settings
        """
        # default value
        ret = { 'run-at': (0, 0, 0, 0, 0, 0),  'run-type': UCI.SCHED_NOW, 'run-nb': -1  }

        if self.schedNb.isChecked():
            runNb = self.schedNbLineEdit.text()
            if not len(runNb): runNb = 0
            runNbInt = int(runNb)
            if runNbInt <= 1:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
                return None
            else:
                ret['run-nb'] = runNbInt
                
        if self.schedWeekly.isChecked():
            pydtH = self.schedWeeklyH.dateTime().toPyDateTime()
            pydtM = self.schedWeeklyM.dateTime().toPyDateTime()
            pydtS = self.schedWeeklyS.dateTime().toPyDateTime()
            ret['run-at'] = (0, 0, self.comboBoxDays.currentIndex(), pydtH.hour, pydtM.minute, pydtS.second)
            ret['run-type'] = UCI.SCHED_WEEKLY
            
        return ret
        
class DailyWidget(QWidget, Logger.ClassLogger):
    """
    Daily widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(DailyWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """
        self.schedDaily = QRadioButton("Daily at: ")
        self.schedDaily.setChecked(True)
        self.schedDailyH = QDateTimeEdit( )
        self.schedDailyH.setDisplayFormat("hh")
        self.schedDailyM = QDateTimeEdit( )
        self.schedDailyM.setDisplayFormat("mm")
        self.schedDailyS = QDateTimeEdit( )
        self.schedDailyS.setDisplayFormat("ss")
        
        self.schedNb= QCheckBox( "Number of runs" )
        self.schedNbLineEdit = QLineEdit('Unlimited')
        self.schedNbLineEdit.setValidator(QIntValidator(self.schedNbLineEdit))
        self.schedNbLineEdit.setEnabled(False)
        
        subLayout = QGridLayout()
        subLayout.addWidget(self.schedDaily, 0, 0)
        subLayout.addWidget(self.schedDailyH, 0, 1)
        subLayout.addWidget( QLabel( self.tr("hour(s)") ), 0, 2)
        subLayout.addWidget(self.schedDailyM, 0, 3)
        subLayout.addWidget( QLabel( self.tr("minute(s)") ), 0, 4)
        subLayout.addWidget(self.schedDailyS, 0, 5)
        subLayout.addWidget( QLabel( self.tr("second(s)") ), 0, 6)
        
        subLayout.addWidget(self.schedNb, 1, 0)
        subLayout.addWidget(self.schedNbLineEdit, 1, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        
    def createConnections(self):
        """
        Create connections
        """
        self.schedNb.toggled.connect(self.onCheckNbToggled)
    
    def setNbRun(self, nbRun):
        """
        Set number of run
        """
        if nbRun > 0:
            self.schedNb.setChecked(True)
            self.schedNbLineEdit.setText(str(nbRun))
            self.schedNbLineEdit.setEnabled(True)
            
    def onCheckNbToggled(self, toggled):
        """
        Called on check nb toggled
        """
        if toggled:
            self.schedNbLineEdit.setEnabled(True)
            self.schedNbLineEdit.setText('')
        else:
            self.schedNbLineEdit.setEnabled(False)
            self.schedNbLineEdit.setText('Unlimited')
    
    def setTime(self, h, mn, s):
        """
        Set the time
        """
        self.schedDailyH.setTime( QTime( int(h), 0, 0 ) )
        self.schedDailyM.setTime( QTime( 0, int(mn), 0 ) )
        self.schedDailyS.setTime( QTime( 0, 0, int(s) ) )
        
    def getSettings(self):
        """
        Get settings
        """
        # default value
        ret = { 'run-at': (0, 0, 0, 0, 0, 0),  'run-type': UCI.SCHED_NOW, 'run-nb': -1  } 
        
        if self.schedNb.isChecked():
            runNb = self.schedNbLineEdit.text()
            if not len(runNb): runNb = 0
            runNbInt = int(runNb)
            if runNbInt <= 1:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
                return None
            else:
                ret['run-nb'] = runNbInt
                
        if self.schedDaily.isChecked():
            pydtH = self.schedDailyH.dateTime().toPyDateTime()
            pydtM = self.schedDailyM.dateTime().toPyDateTime()
            pydtS = self.schedDailyS.dateTime().toPyDateTime()
            ret['run-at'] = (0, 0, 0, pydtH.hour, pydtM.minute, pydtS.second)
            ret['run-type'] = UCI.SCHED_DAILY  
        return ret
        
class HourlyWidget(QWidget, Logger.ClassLogger):
    """
    Hourly widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(HourlyWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """

        self.schedHourly = QRadioButton( "Hourly at: " )
        self.schedHourly.setChecked(True)
        self.schedHourlyM = QDateTimeEdit( )
        self.schedHourlyM.setDisplayFormat("mm")
        self.schedHourlyS = QDateTimeEdit( )
        self.schedHourlyS.setDisplayFormat("ss")
        
        self.schedNb= QCheckBox( "Number of runs" )
        self.schedNbLineEdit = QLineEdit('Unlimited')
        self.schedNbLineEdit.setValidator(QIntValidator(self.schedNbLineEdit))
        self.schedNbLineEdit.setEnabled(False)
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(self.schedHourly, 0, 0)
        subLayout.addWidget(self.schedHourlyM, 0, 1)
        subLayout.addWidget( QLabel( self.tr("minute(s)") ), 0, 2)
        subLayout.addWidget(self.schedHourlyS, 0, 3)
        subLayout.addWidget( QLabel( self.tr("second(s)") ), 0, 4)
        
        subLayout.addWidget(self.schedNb, 1, 0)
        subLayout.addWidget(self.schedNbLineEdit, 1, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        
    def createConnections(self):
        """
        Create connections
        """
        self.schedNb.toggled.connect(self.onCheckNbToggled)
    
    def onCheckNbToggled(self, toggled):
        """
        Called on check nb toggled
        """
        if toggled:
            self.schedNbLineEdit.setEnabled(True)
            self.schedNbLineEdit.setText('')
        else:
            self.schedNbLineEdit.setEnabled(False)
            self.schedNbLineEdit.setText('Unlimited')
    
    def setTime(self, mn, s):
        """
        Set the time
        """
        self.schedHourlyM.setTime( QTime( 0, int(mn), 0 ) )
        self.schedHourlyS.setTime( QTime( 0, 0, int(s) ) )
        
    def setNbRun(self, nbRun):
        """
        Set number of run
        """
        if nbRun > 0:
            self.schedNb.setChecked(True)
            self.schedNbLineEdit.setText(str(nbRun))
            self.schedNbLineEdit.setEnabled(True)    
            
    def getSettings(self):
        """
        Get settings
        """
        # default value
        ret = { 'run-at': (0, 0, 0, 0, 0, 0),  'run-type': UCI.SCHED_NOW, 'run-nb': -1 }
        
        if self.schedNb.isChecked():
            runNb = self.schedNbLineEdit.text()
            if not len(runNb): runNb = 0
            runNbInt = int(runNb)
            if runNbInt <= 1:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
                return None
            else:
                ret['run-nb'] = runNbInt

        if self.schedHourly.isChecked():
            pydtM = self.schedHourlyM.dateTime().toPyDateTime()
            pydtS = self.schedHourlyS.dateTime().toPyDateTime()
            ret['run-at'] = (0, 0, 0, 0, pydtM.minute, pydtS.second)
            ret['run-type'] = UCI.SCHED_HOURLY 
                    
        return ret
        
class SuccessiveWidget(QWidget, Logger.ClassLogger):
    """
    Successive widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(SuccessiveWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """
        self.schedImmed = QRadioButton(self.tr("Start immediality"))
        self.schedImmed.setChecked(True)
        
        self.schedAt = QRadioButton(self.tr("Start at:"))
        self.schedAtDateEdit = QDateTimeEdit( QDateTime.currentDateTime() )

        self.schedNb= QCheckBox( "Number of runs" )
        self.schedNbLineEdit = QLineEdit('Unlimited')
        self.schedNbLineEdit.setValidator(QIntValidator(self.schedNbLineEdit))
        self.schedNbLineEdit.setEnabled(False)
        
        subLayout = QGridLayout()
        subLayout.addWidget(self.schedImmed, 0, 0)
        subLayout.addWidget(self.schedAt, 1, 0)
        subLayout.addWidget(self.schedAtDateEdit, 1, 1)
        
        subLayout.addWidget(self.schedNb, 2, 0)
        subLayout.addWidget(self.schedNbLineEdit, 2, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        
    def createConnections(self):
        """
        Create connections
        """
        self.schedNb.toggled.connect(self.onCheckNbToggled)
        
    def onCheckNbToggled(self, toggled):
        """
        Called on check nb toggled
        """
        if toggled:
            self.schedNbLineEdit.setEnabled(True)
            self.schedNbLineEdit.setText('')
        else:
            self.schedNbLineEdit.setEnabled(False)
            self.schedNbLineEdit.setText('Unlimited')
    
    def setNbRun(self, nbRun):
        """
        Set number of run
        """
        if nbRun > 0:
            self.schedNb.setChecked(True)
            self.schedNbLineEdit.setText(str(nbRun))
            self.schedNbLineEdit.setEnabled(True)   
            
    def getSettings(self):
        """
        Get settings
        """
        # default value
        ret = { 'run-from': (0, 0, 0, 0, 0, 0),  'run-type': UCI.SCHED_NOW, 'run-nb': -1  }

        if self.schedNb.isChecked():
            runNb = self.schedNbLineEdit.text()
            if not len(runNb): runNb = 0
            runNbInt = int(runNb)
            if runNbInt <= 1:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
                return None
            else:
                ret['run-nb'] = runNbInt
                
        ret['run-type'] = UCI.SCHED_NOW_MORE
        if self.schedAt.isChecked():
            pydt = self.schedAtDateEdit.dateTime().toPyDateTime()
            ret['run-from'] =  (pydt.year, pydt.month, pydt.day, pydt.hour, pydt.minute, pydt.second)
            
        return ret
        
class EveryWidget(QWidget, Logger.ClassLogger):
    """
    Every widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(EveryWidget, self).__init__(parent)
        self.createWidgets()
        self.createConnections()
        
    def createWidgets(self):
        """
        Create widgets
        """

        self.schedEverySec = QRadioButton("Every minute at: ")
        self.schedEverySecValue = QDateTimeEdit( )
        self.schedEverySecValue.setDisplayFormat("ss")

        self.schedEvery = QRadioButton("Every: ")
        self.schedEvery.setChecked(True)
        self.schedEveryH = QDateTimeEdit( )
        self.schedEveryH.setDisplayFormat("hh")

        self.schedEveryM = QDateTimeEdit( )
        self.schedEveryM.setDisplayFormat("mm")
        
        self.schedEveryS = QDateTimeEdit( )
        self.schedEveryS.setDisplayFormat("ss")
        
        self.schedEveryFrom = QDateTimeEdit( )
        self.schedEveryFrom.setDisplayFormat("hh:mm")

        self.schedEveryTo = QDateTimeEdit( )
        self.schedEveryTo.setDisplayFormat("hh:mm")

        self.schedNb= QCheckBox( "Number of runs" )
        self.schedNbLineEdit = QLineEdit('Unlimited')
        self.schedNbLineEdit.setValidator(QIntValidator(self.schedNbLineEdit))
        self.schedNbLineEdit.setEnabled(False)
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(self.schedEverySec, 0, 0)
        subLayout.addWidget(self.schedEverySecValue, 0, 1)
        subLayout.addWidget( QLabel( self.tr("second(s)") ), 0, 2)
        
        subLayout.addWidget(self.schedEvery, 1, 0)
        subLayout.addWidget(self.schedEveryH, 1, 1)
        subLayout.addWidget( QLabel( self.tr("hour(s)") ), 1, 2)
        subLayout.addWidget(self.schedEveryM, 1, 3)
        subLayout.addWidget( QLabel( self.tr("minute(s)") ), 1, 4)
        subLayout.addWidget(self.schedEveryS, 1, 5)
        subLayout.addWidget( QLabel( self.tr("second(s)") ), 1, 6)
        
        subLayout.addWidget( QLabel( self.tr("From time: ") ), 2, 1)
        subLayout.addWidget(self.schedEveryFrom, 2, 2 )
        subLayout.addWidget( QLabel( self.tr("To time: ") ), 3, 1)
        subLayout.addWidget(self.schedEveryTo, 3, 2)
        
        subLayout.addWidget(self.schedNb, 4, 0)
        subLayout.addWidget(self.schedNbLineEdit, 4, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        
    def createConnections(self):
        """
        Create connections
        """
        self.schedNb.toggled.connect(self.onCheckNbToggled)
        
    def onCheckNbToggled(self, toggled):
        """
        Called on check nb toggled
        """
        if toggled:
            self.schedNbLineEdit.setEnabled(True)
            self.schedNbLineEdit.setText('')
        else:
            self.schedNbLineEdit.setEnabled(False)
            self.schedNbLineEdit.setText('Unlimited')
    
    def setNbRun(self, nbRun):
        """
        Set number of run
        """
        if nbRun > 0:
            self.schedNb.setChecked(True)
            self.schedNbLineEdit.setText(str(nbRun))
            self.schedNbLineEdit.setEnabled(True)

    def setTimeSec(self, h, mn, s):
        """
        Set time X
        """
        self.schedEverySec.setChecked(True)
        self.schedEverySecValue.setTime( QTime( int(h), int(mn), int(s) ) )
        
    def setTimeX(self, h, mn, s, hFrom, mnFrom, sFrom, hTo, mnTo, sTo):
        """
        Set time X
        """
        self.schedEvery.setChecked(True)
        self.schedEveryH.setTime( QTime( int(h), 0, 0 ) )
        self.schedEveryM.setTime( QTime( 0, int(mn), 0 ) )
        self.schedEveryS.setTime( QTime( 0, 0, int(s) ) )
        
        self.schedEveryFrom.setTime( QTime( int(hFrom), int(mnFrom), int(sFrom) ) )
        self.schedEveryTo.setTime( QTime( int(hTo), int(mnTo), int(sTo) ) )
                    
    def getSettings(self):
        """
        Get settings
        """
        # default value
        ret = { 'run-at': (0, 0, 0, 0, 0, 0),  'run-type': UCI.SCHED_NOW,
                'run-from': (0, 0, 0, 0, 0, 0), 'run-to': (0, 0, 0, 0, 0, 0),
                'run-nb': -1 }

        if self.schedNb.isChecked():
            runNb = self.schedNbLineEdit.text()
            if not len(runNb): runNb = 0
            runNbInt = int(runNb)
            if runNbInt <= 1:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
                return None
            else:
                ret['run-nb'] = runNbInt

                
        if self.schedEverySec.isChecked():
            pydt = self.schedEverySecValue.dateTime().toPyDateTime()
            ret['run-at'] = (0, 0, 0, 0, 0, pydt.second)
            ret['run-type'] = UCI.SCHED_EVERY_MIN  

        if self.schedEvery.isChecked():
            pydtH = self.schedEveryH.dateTime().toPyDateTime()
            pydtM = self.schedEveryM.dateTime().toPyDateTime()
            pydtS = self.schedEveryS.dateTime().toPyDateTime()
            if pydtH.hour == 0 and pydtM.minute == 0 and pydtS.second == 0:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct value.")
                return None
            else:
                ret['run-at'] = (0, 0, 0, pydtH.hour, pydtM.minute, pydtS.second)
                ret['run-type'] = UCI.SCHED_EVERY_X
                
                pydtFrom = self.schedEveryFrom.dateTime().toPyDateTime()
                pydtTo = self.schedEveryTo.dateTime().toPyDateTime()
                ret['run-from'] = (0, 0, 0, pydtFrom.hour, pydtFrom.minute, 0)
                ret['run-to'] = (0, 0, 0, pydtTo.hour, pydtTo.minute, 0)
                
        return ret
        
class OneTimeWidget(QWidget, Logger.ClassLogger):
    """
    One time widget
    """
    def __init__(self, parent=None):
        """
        Constructor
        """
        super(OneTimeWidget, self).__init__(parent)
        self.createWidgets()
        
    def createWidgets(self):
        """
        Create widgets
        """
        # in x seconds
        self.schedIn = QRadioButton("Start in x second(s): ")
        self.schedIn.setChecked(True)
        self.schedInValue = QLineEdit()
        self.schedInValue.setValidator(QIntValidator(self.schedInValue))
        
        # at date and time
        self.schedAt = QRadioButton("Start at: ")
        self.schedAtValue = QDateTimeEdit( QDateTime.currentDateTime() )
        
        # final layout
        subLayout = QGridLayout()
        subLayout.addWidget(self.schedIn, 0, 0)
        subLayout.addWidget(self.schedInValue, 0, 1)
        subLayout.addWidget(self.schedAt, 1, 0)
        subLayout.addWidget(self.schedAtValue, 1, 1)
        
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(subLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
    
    def setTimeIn(self, s):
        """
        Set time in
        """
        self.schedInValue.setText( str(s) )
        self.schedIn.setChecked(True)
    
    def setTimeAt(self, y, m, d, h, mn, s):
        """
        Set time at
        """
        self.schedAtValue.setTime( QTime( int(h), int(mn), int(s) ) )
        self.schedAtValue.setDate( QDate( int(y), int(m), int(d) )  )
        self.schedAt.setChecked(True)
        
    def getSettings(self):
        """
        Get settings
        """
        # default value
        ret = { 'run-at': (0, 0, 0, 0, 0, 0),  'run-type': UCI.SCHED_NOW }
        now = QDateTime( QDate.currentDate(), QTime.currentTime() )
        now = now.toPyDateTime()
        nowWithoutSecond = now.replace( second = 0 )
        
        if self.schedIn.isChecked():
            secStr = self.schedInValue.text()
            if not len(secStr): 
                secInt = 0
            else:
                secInt = int(secStr)
            if secInt <= 0:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of seconds.")
                return None
            else:
                ret['run-at'] = (0,0,0,0,0,secInt)
                ret['run-type'] = UCI.SCHED_IN 
        
        if self.schedAt.isChecked():
            pydt = self.schedAtValue.dateTime().toPyDateTime()
            delta = pydt - nowWithoutSecond
            if delta.days < 0:
                QMessageBox.information(self, self.tr("Scheduler") , "Too late...")
                return None
            else:
                ret['run-at'] = (pydt.year, pydt.month, pydt.day, pydt.hour, pydt.minute, pydt.second)
                ret['run-type'] = UCI.SCHED_AT 
                
        return ret
            
class SchedDialog(QtHelper.EnhancedQDialog):
    """
    Schedule dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor
        """
        QtHelper.EnhancedQDialog.__init__(self, parent)
        self.name = self.tr("Scheduling a run")
        self.delta = None

        self.options = {
            'run-at': (0, 0, 0, 0, 0, 0),
            'run-type': UCI.SCHED_NOW,
            'run-from': (0, 0, 0, 0, 0, 0),
            'run-to': (0, 0, 0, 0, 0, 0),
            'run-nb': -1,
            'no-probes': False,
            'no-notifs': False,
            'no-tr': False,
            'enabled': True
        }

        self.createDialog()
        self.createConnections()
        
    def createDialog(self):
        """
        Create qt dialog
        """       
        self.setWindowTitle( self.name )
        
        self.descriptionLabel = QLabel(self.tr("Schedule the test: "))

        # group of options
        self.typeGroup = QGroupBox("")
        
        self.groupRadio = QButtonGroup(self)
        
        self.oneRadio = QRadioButton("One Time")
        self.groupRadio.addButton(self.oneRadio, 0)
        self.oneRadio.setChecked(True)

        self.successiveRadio = QRadioButton("Successive")
        self.groupRadio.addButton(self.successiveRadio, 1)
        
        self.everyRadio = QRadioButton("Every")
        self.groupRadio.addButton(self.everyRadio, 2)
        
        self.hourlyRadio = QRadioButton("Hourly")
        self.groupRadio.addButton(self.hourlyRadio, 3)
        
        self.dailyRadio = QRadioButton("Daily")
        self.groupRadio.addButton(self.dailyRadio, 4)
        
        self.weeklyRadio = QRadioButton("Weekly")
        self.groupRadio.addButton(self.weeklyRadio, 5)

        layoutType = QVBoxLayout()
        layoutType.addWidget(self.oneRadio)
        layoutType.addWidget(self.successiveRadio)
        layoutType.addWidget(self.everyRadio)
        layoutType.addWidget(self.hourlyRadio)
        layoutType.addWidget(self.dailyRadio)
        layoutType.addWidget(self.weeklyRadio)
        self.typeGroup.setLayout(layoutType)

        # misc options
        self.miscGroup = QGroupBox("")
        
        self.withoutProbes  = QCheckBox( "Run without probes" )
        self.withoutNotifs  = QCheckBox( "Run without notifications" )
        self.noKeepTestResult  = QCheckBox( "Do not keep test result on success" )
        if QtHelper.str2bool(Settings.instance().readValue( key = 'ScheduleRun/dont-keep-result-on-success' )):
            self.noKeepTestResult.setChecked(True)
        
        layoutMisc = QVBoxLayout()
        layoutMisc.addWidget(self.withoutProbes)
        layoutMisc.addWidget(self.withoutNotifs)
        layoutMisc.addWidget(self.noKeepTestResult)
        self.miscGroup.setLayout(layoutMisc)
        
        # pages
        self.OneTimeConf = OneTimeWidget( self )
        self.EveryConf = EveryWidget( self )
        self.SuccessiveConf = SuccessiveWidget( self )
        self.HourlyConf = HourlyWidget( self )
        self.DailyConf = DailyWidget( self )
        self.WeeklyConf = WeeklyWidget( self )
 
        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.OneTimeConf)
        self.pagesWidget.addWidget(self.SuccessiveConf)
        self.pagesWidget.addWidget(self.EveryConf)
        self.pagesWidget.addWidget(self.HourlyConf)
        self.pagesWidget.addWidget(self.DailyConf)
        self.pagesWidget.addWidget(self.WeeklyConf)
        
        # buttons
        self.okButton = QPushButton( QIcon(":/schedule.png"), self.tr("Schedule"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"), self.tr("Cancel"), self)
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addWidget(self.cancelButton)
        
        # sub layout
        horizontalLayout = QGridLayout()
        horizontalLayout.addWidget(self.typeGroup, 0, 0)
        horizontalLayout.addWidget(self.pagesWidget, 0, 1)
        horizontalLayout.addWidget(self.miscGroup, 1, 1)
        
        # final layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.descriptionLabel)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(horizontalLayout)

        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)
        
        self.setLayout(mainLayout)
        
        flags = Qt.WindowFlags()
        flags |= Qt.WindowCloseButtonHint
        flags |= Qt.MSWindowsFixedSizeDialogHint
        self.setWindowFlags(flags)
    
    def changePage(self, current):
        """
        On change page
        """
        self.pagesWidget.setCurrentIndex(self.groupRadio.checkedId())
      
    def createConnections (self):
        """
        QtActions creation
         * ok
         * cancel
        """
        self.okButton.clicked.connect(self.acceptClicked)
        self.cancelButton.clicked.connect(self.reject)
        self.groupRadio.buttonClicked.connect(self.changePage)
        
    def fillFields(self, schedType, schedArgs, taskName, taskId, schedNb, withoutProbes, enabled=True,
                    noKeepTr=False, withoutNotifs=False, schedFrom=(0,0,0,0,0,0), schedTo=(0,0,0,0,0,0) ):
        """
        Fill fields
        """
        self.setWindowTitle( "Re-%s" % self.name )
        self.okButton.setText( "Re-Schedule" )
        self.okButton.setEnabled(True)
        
        self.descriptionLabel.setText( "Schedule the test [%s]: %s" % ( str(taskId), str(taskName)) )
        self.options['enabled'] = enabled

        ( y, m, d, h, mn, s) = schedArgs
        ( yFrom, mFrom, dFrom, hFrom, mnFrom, sFrom) = schedFrom
        ( yTo, mTo, dTo, hTo, mnTo, sTo) = schedTo
        
        if withoutProbes: self.withoutProbes.setChecked(True)
        if withoutNotifs: self.withoutNotifs.setChecked(True)
        if noKeepTr: 
            self.noKeepTestResult.setChecked(True)
        else: # bug fix, noKeepTestResult checked but should not
            self.noKeepTestResult.setChecked(False)
            
        if schedType == UCI.SCHED_NOW_MORE:
            self.okButton.setEnabled(False)
            self.withoutProbes.setEnabled(False)
            self.withoutNotifs.setEnabled(False)
            self.noKeepTestResult.setEnabled(False)
            self.SuccessiveConf.setEnabled(False)
        else:
            self.withoutProbes.setEnabled(True)
            self.withoutNotifs.setEnabled(True)
            self.noKeepTestResult.setEnabled(True)
            self.SuccessiveConf.setEnabled(True)
        
        if schedType == UCI.SCHED_IN:
            self.oneRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(0)
            self.OneTimeConf.setTimeIn(s=s)
            
        if schedType == UCI.SCHED_AT:
            self.oneRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(0)
            self.OneTimeConf.setTimeAt(y=y, m=m, d=d, h=h, mn=mn, s=s)
            
        if schedType == UCI.SCHED_NOW_MORE:    
            self.successiveRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(1)
            self.SuccessiveConf.setNbRun(nbRun=schedNb)
            
        if schedType == UCI.SCHED_EVERY_MIN:
            self.everyRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(2)
            self.EveryConf.setNbRun(nbRun=schedNb)
            self.EveryConf.setTimeSec(h=h, mn=mn, s=s )
                  
        if schedType == UCI.SCHED_EVERY_X:
            self.everyRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(2)
            self.EveryConf.setNbRun(nbRun=schedNb)
            self.EveryConf.setTimeX( h=h, mn=mn, s=s, 
                                    hFrom=hFrom, mnFrom=mnFrom, sFrom=sFrom, 
                                    hTo=hTo, mnTo=mnTo, sTo=sTo)
            
        if schedType == UCI.SCHED_HOURLY:
            self.hourlyRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(3)
            self.HourlyConf.setNbRun(nbRun=schedNb)
            self.HourlyConf.setTime(mn=mn, s=s)
            
        if schedType == UCI.SCHED_DAILY:
            self.dailyRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(4)
            self.DailyConf.setNbRun(nbRun=schedNb)
            self.DailyConf.setTime(h=h, mn=mn, s=s)
            
        if schedType == UCI.SCHED_WEEKLY:
            self.weeklyRadio.setChecked(True)
            self.pagesWidget.setCurrentIndex(5)
            self.WeeklyConf.setNbRun(nbRun=schedNb)
            self.WeeklyConf.setTime(d=d, h=h, mn=mn, s=s)
                   
    def acceptClicked (self):
        """
        Called on accept button
        """
        currentPage = self.pagesWidget.currentWidget()
        newSettings  = currentPage.getSettings()
        if newSettings != None:
            self.options.update(newSettings)
            # misc options
            if self.withoutProbes.isChecked(): self.options['no-probes'] = True
            if self.withoutNotifs.isChecked(): self.options['no-notifs'] = True
            if self.noKeepTestResult.isChecked(): self.options['no-tr'] = True
                
            self.accept()
        
    def getSchedtime(self):
        """
        Returns schedule time
        """ 
        return (    self.options['run-at'], self.options['run-type'], 
                    self.options['run-nb'], self.options['no-probes'], 
                    self.options['enabled'], self.options['no-tr'],
                    self.options['no-notifs'],  self.options['run-from'],
                    self.options['run-to']
                )
                    
class SchedDialogV1(QtHelper.EnhancedQDialog):
    """
    Schedule dialog
    """
    def __init__(self, dialogName, parent = None):
        """
        Constructor
        """
        QtHelper.EnhancedQDialog.__init__(self, parent)
        
        self.name = self.tr("Scheduling a run")
        self.delta = None
        self.taskEnabled = True
        
        self.createDialog()
        self.createConnections()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle( self.name )
        
        layout = QGridLayout()

        self.descriptionLabel = QLabel("%s:" % self.tr("Begin the test"))
        self.statusLabel = QLabel("%s:" % self.tr("Status"))

        self.configBox = QGroupBox("Postpone test")
        self.configBox.setCheckable(True)
        self.configBox.setChecked(True)

        self.schedIn = QRadioButton("Run one time in x second(s)")
        self.schedIn.setChecked(True)
        self.schedInLineEdit = QLineEdit()
        self.schedInLineEdit.setValidator(QIntValidator(self.schedInLineEdit))
        self.schedAt = QRadioButton("Run one time at")
        self.schedAtDateEdit = QDateTimeEdit( QDateTime.currentDateTime() )

        self.config2Box = QGroupBox("Repeat test")
        self.config2Box.setCheckable(True)
        self.config2Box.setChecked(False)

        self.schedEveryMin = QRadioButton("Every minutes at second (ss)")
        self.schedEveryMinDateEdit = QDateTimeEdit( )
        self.schedEveryMinDateEdit.setDisplayFormat("ss")

        self.schedEveryX = QRadioButton("Every hh:mm:ss")
        self.schedEveryXDateEdit = QDateTimeEdit( )
        self.schedEveryXDateEdit.setDisplayFormat("hh:mm:ss")

        self.schedEveryXFromEdit = QDateTimeEdit( )
        self.schedEveryXFromEdit.setDisplayFormat("hh:mm")

        self.schedEveryXToEdit = QDateTimeEdit( )
        self.schedEveryXToEdit.setDisplayFormat("hh:mm")


        self.schedHourly = QRadioButton( "Hourly at minute (mm) and second (ss)" )
        self.schedHourlyDateEdit = QDateTimeEdit( )
        self.schedHourlyDateEdit.setDisplayFormat("mm:ss")

        self.schedDaily = QRadioButton("Daily at hour (hh) and minute (mm) and second (ss)")
        self.schedDailyDateEdit = QDateTimeEdit( )
        self.schedDailyDateEdit.setDisplayFormat("hh:mm:ss")
        
        self.schedWeekly = QRadioButton("Weekly on")
        self.schedWeeklyDateEdit = QDateTimeEdit( QDateTime( 0, 0, 0, 0, 0, 0 ), self  )
        self.schedWeeklyDateEdit.setDisplayFormat("hh:mm:ss")
        self.schedWeeklyLabel = QLabel(" at:")

        self.comboBoxDays = QComboBox()
        for d in list(UCI.SCHED_DAYS_DICT.values()): # wrap to list to support python3 
            self.comboBoxDays.addItem( d.title())

        self.schedNb= QCheckBox( "Number of runs" )
        self.schedNbLineEdit = QLineEdit('Unlimited')
        self.schedNbLineEdit.setValidator(QIntValidator(self.schedInLineEdit))
        self.schedNbLineEdit.setEnabled(False)

        self.withoutProbes  = QCheckBox( "Run without probes" )
        self.withoutNotifs  = QCheckBox( "Run without notifications" )
        self.noKeepTestResult  = QCheckBox( "Do not keep test result on success" )
        if QtHelper.str2bool(Settings.instance().readValue( key = 'ScheduleRun/dont-keep-result-on-success' )):  
            self.noKeepTestResult.setChecked(True)
        
        configLayout = QGridLayout()
        configLayout.addWidget(self.schedIn, 0, 0)
        configLayout.addWidget(self.schedInLineEdit , 0, 1)
        configLayout.addWidget(self.schedAt, 1, 0)
        configLayout.addWidget(self.schedAtDateEdit , 1, 1)
        self.configBox.setLayout(configLayout)
    
        self.lineSep1 = QFrame()
        self.lineSep1.setGeometry(QRect(110, 221, 51, 20))
        self.lineSep1.setFrameShape(QFrame.HLine)
        self.lineSep1.setFrameShadow(QFrame.Sunken)

        self.lineSep2 = QFrame()
        self.lineSep2.setGeometry(QRect(110, 221, 51, 20))
        self.lineSep2.setFrameShape(QFrame.HLine)
        self.lineSep2.setFrameShadow(QFrame.Sunken)

        config2Layout = QGridLayout()
        config2Layout.addWidget(self.schedEveryMin, 2, 0)
        config2Layout.addWidget(self.schedEveryMinDateEdit , 2, 1)
        config2Layout.addWidget(self.schedEveryX, 3, 0)
        config2Layout.addWidget(self.schedEveryXDateEdit , 3, 1)
        config2Layout.addWidget(self.schedEveryXDateEdit , 3, 1)

        fromtoLayout = QHBoxLayout()
        fromtoLayout.setContentsMargins(15,0,0,0)
        fromtoLayout.addWidget( QLabel("  On each day from hh:mm") )
        fromtoLayout.addWidget( self.schedEveryXFromEdit )
        fromtoLayout.addWidget( QLabel("  to hh:mm") )
        fromtoLayout.addWidget( self.schedEveryXToEdit )

        config2Layout.addLayout(fromtoLayout, 4, 0) 

        config2Layout.addWidget(self.lineSep1, 5, 0)

        config2Layout.addWidget(self.schedHourly, 6, 0)
        config2Layout.addWidget(self.schedHourlyDateEdit , 6, 1)
        
        config2Layout.addWidget(self.schedDaily, 7, 0)
        config2Layout.addWidget(self.schedDailyDateEdit , 7, 1)
        self.config2Box.setLayout(config2Layout)
        
        weeklyLayout = QHBoxLayout()
        weeklyLayout.addWidget(self.schedWeekly)
        weeklyLayout.addWidget(self.comboBoxDays)
        weeklyLayout.addWidget(self.schedWeeklyLabel)

        config2Layout.addLayout(weeklyLayout, 8, 0)
        config2Layout.addWidget(self.schedWeeklyDateEdit , 8, 1)
        
        config2Layout.addWidget(self.lineSep2, 9, 0)
        config2Layout.addWidget(self.schedNb, 10, 0)
        config2Layout.addWidget(self.schedNbLineEdit , 10, 1)

        layout.addWidget(self.configBox, 0, 0)
        layout.addWidget(self.config2Box, 1, 0)

        buttonLayout = QVBoxLayout()
        self.okButton = QPushButton(self.tr("Schedule"), self)
        self.cancelButton = QPushButton(self.tr("Cancel"), self)

        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
       

        miscLayout = QVBoxLayout()
        miscLayout.addWidget(  QLabel() ) 
        miscLayout.addWidget(  self.withoutProbes )
        miscLayout.addWidget(  self.withoutNotifs )
        miscLayout.addWidget(  self.noKeepTestResult )
               

        layout.addLayout(buttonLayout, 0, 1)
        layout.addLayout(miscLayout, 1, 1)

        layout.addWidget(self.descriptionLabel, 2, 0)
        layout.addWidget(self.statusLabel, 3, 0)

        self.setLayout(layout)
        
        flags = Qt.WindowFlags()
        flags |= Qt.WindowCloseButtonHint
        flags |= Qt.MSWindowsFixedSizeDialogHint
        self.setWindowFlags(flags)

    def createConnections (self):
        """
        QtActions creation
         * ok
         * cancel
        """
        self.okButton.clicked.connect(self.acceptClicked)
        self.cancelButton.clicked.connect(self.reject)

        self.configBox.toggled.connect(self.onGroupPostponedToggled)
        self.config2Box.toggled.connect(self.onGroupRepeatToggled)

        self.schedNb.toggled.connect(self.onCheckNbToggled)

        self.schedInLineEdit.textChanged.connect(self.onSchedInLineChanged)
        self.schedAtDateEdit.dateTimeChanged.connect(self.onSchedAtDateChanged)

        self.schedHourlyDateEdit.dateTimeChanged.connect(self.onSchedHourlyDateChanged)
        self.schedEveryMinDateEdit.dateTimeChanged.connect(self.onSchedEveryMinDateChanged)
        self.schedEveryXDateEdit.dateTimeChanged.connect(self.onSchedEveryXDateChanged)
        self.schedWeeklyDateEdit.dateTimeChanged.connect(self.onSchedWeeklyDateChanged)
        self.schedDailyDateEdit.dateTimeChanged.connect(self.onSchedDailyDateChanged)
        self.schedEveryXFromEdit.dateTimeChanged.connect(self.onSchedEveryXFromDateChanged)
        self.schedEveryXToEdit.dateTimeChanged.connect(self.onSchedEveryXToDateChanged)

        self.comboBoxDays.currentIndexChanged.connect(self.onComboDayChanged)

    def onComboDayChanged(self, selected):
        """
        On combo day changed
        """
        self.schedWeekly.setChecked(True)

    def onSchedInLineChanged(self, t):
        """
        On sched in line changed
        """
        self.schedIn.setChecked(True)

    def onSchedAtDateChanged(self, dt):
        """
        On sched at data changed
        """
        self.schedAt.setChecked(True)

    def onSchedHourlyDateChanged(self, dt):
        """
        On sched hourly date changed
        """
        self.schedHourly.setChecked(True)

    def onSchedEveryMinDateChanged(self, dt):
        """
        On sched every minute date changed
        """
        self.schedEveryMin.setChecked(True)

    def onSchedEveryXDateChanged(self, dt):
        """
        On schedule every x data changed
        """
        self.schedEveryX.setChecked(True)

    def onSchedWeeklyDateChanged(self, dt):
        """
        On schedule weekly data changed
        """
        self.schedWeekly.setChecked(True)

    def onSchedDailyDateChanged(self, dt):
        """
        On schedule daily changed
        """
        self.schedDaily.setChecked(True)

    def onSchedEveryXFromDateChanged(self, dt):
        """
        On schedule every x from date changed
        """
        self.schedEveryX.setChecked(True)

    def onSchedEveryXToDateChanged(self, dt):
        """
        On schedule every data to changed
        """
        self.schedEveryX.setChecked(True)

    def onCheckNbToggled(self, toggled):
        """
        Called on check nb toggled
        """
        if toggled:
            self.schedNbLineEdit.setEnabled(True)
            self.schedNbLineEdit.setText('')
        else:
            self.schedNbLineEdit.setEnabled(False)
            self.schedNbLineEdit.setText('Unlimited')

    def onGroupPostponedToggled(self, toggled):
        """
        Called on group postponed toggled
        """
        if toggled:
            self.config2Box.setChecked(False)

    def onGroupRepeatToggled(self, toggled):
        """
        Called on group repeat toggled
        """
        if toggled:
            self.configBox.setChecked(False)

    def fillFields(self, schedType, schedArgs, taskName, taskId, schedNb, withoutProbes, enabled=True,
                            noKeepTr=False, withoutNotifs=False, schedFrom=(0,0,0,0,0,0), schedTo=(0,0,0,0,0,0)):
        """
        Fill fields
        """
        self.taskEnabled = enabled
        self.setWindowTitle( "Re-%s" % self.name )
        self.okButton.setText( "Re-Schedule" )
        self.okButton.setEnabled(True)
        self.descriptionLabel.setText( "Begin the test [%s]: %s" % ( str(taskId), str(taskName)) )

        if enabled:
            self.statusLabel.setText( "Status: Enabled" )
        else:
            self.statusLabel.setText( "Status: Disabled" )

        ( y, m, d, h, mn, s) = schedArgs
        ( yFrom, mFrom, dFrom, hFrom, mnFrom, sFrom) = schedFrom
        ( yTo, mTo, dTo, hTo, mnTo, sTo) = schedTo

        if schedType == UCI.SCHED_NOW_MORE:
            self.okButton.setEnabled(False)
            self.withoutProbes.setEnabled(False)
            self.withoutNotifs.setEnabled(False)
            self.noKeepTestResult.setEnabled(False)
            self.configBox.setEnabled(False)
            self.config2Box.setEnabled(False)
        else:
            self.withoutProbes.setEnabled(True)
            self.withoutNotifs.setEnabled(True)
            self.noKeepTestResult.setEnabled(True)

        # postponed
        if schedType == UCI.SCHED_IN:
            self.schedIn.setChecked(True)
            self.configBox.setChecked(True)
            self.config2Box.setChecked(False)
            self.schedInLineEdit.setText( str(s) )
        if schedType == UCI.SCHED_AT:
            self.schedAt.setChecked(True)
            self.configBox.setChecked(True)
            self.config2Box.setChecked(False)
            self.schedAtDateEdit.setTime( QTime( int(h), int(mn), int(s) ) )
            self.schedAtDateEdit.setDate( QDate( int(y), int(m), int(d) )  )
        # recursive
        if schedType == UCI.SCHED_EVERY_MIN:
            self.schedEveryMin.setChecked(True)
            self.configBox.setChecked(False)
            self.config2Box.setChecked(True)
            self.schedEveryMinDateEdit.setTime( QTime( int(h), int(mn), int(s) ) )
        if schedType == UCI.SCHED_HOURLY:
            self.schedHourly.setChecked(True)
            self.configBox.setChecked(False)
            self.config2Box.setChecked(True)
            self.schedHourlyDateEdit.setTime( QTime( int(h), int(mn), int(s) ) )
        if schedType == UCI.SCHED_DAILY:
            self.schedDaily.setChecked(True)
            self.configBox.setChecked(False)
            self.config2Box.setChecked(True)
            self.schedDailyDateEdit.setTime( QTime( int(h), int(mn), int(s) ) )
        # BEGIN new in 3.1.0
        if schedType == UCI.SCHED_EVERY_X:
            self.schedEveryX.setChecked(True)
            self.configBox.setChecked(False)
            self.config2Box.setChecked(True)
            self.schedEveryXDateEdit.setTime( QTime( int(h), int(mn), int(s) ) )

            self.schedEveryXFromEdit.setTime( QTime( int(hFrom), int(mnFrom), int(sFrom) ) )
            self.schedEveryXToEdit.setTime( QTime( int(hTo), int(mnTo), int(sTo) ) )

        # END
        # BEGIN new in 3.2.0
        if schedType == UCI.SCHED_WEEKLY:
            self.schedWeekly.setChecked(True)
            self.configBox.setChecked(False)
            self.config2Box.setChecked(True)
            self.schedWeeklyDateEdit.setTime( QTime( int(h), int(mn), int(s) ) )
            self.comboBoxDays.setCurrentIndex( int(d) )
        # END

        if schedNb > 0:
            self.schedNb.setChecked(True)
            self.schedNbLineEdit.setText(str(schedNb))
            self.schedNbLineEdit.setEnabled(True)

        if withoutProbes:
            self.withoutProbes.setChecked(True)

        if withoutNotifs:
            self.withoutNotifs.setChecked(True)

        if noKeepTr:
            self.noKeepTestResult.setChecked(True)

    def acceptClicked (self):
        """
        Called on accept button
        """
        now = QDateTime( QDate.currentDate(), QTime.currentTime() )
        now = now.toPyDateTime()
        nowWithoutSecond = now.replace( second = 0 )
        
        nbRunOk = True
        self.runFrom = (0,0,0,0,0,0)
        self.runTo = (0,0,0,0,0,0)
        self.runNb = -1 
        self.noProbes = False
        self.noNotifs = False
        self.noTr = False
        if self.schedNb.isChecked():
            runNb = self.schedNbLineEdit.text()
            if runNb == '': runNb = 0
            else:
                runNb_int = int(runNb)
            if runNb_int <= 0:
                QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of run.")
                nbRunOk = False
            else:
                self.runNb = runNb_int

        if self.withoutProbes.isChecked():
            self.noProbes = True

        if self.withoutNotifs.isChecked():
            self.noNotifs = True

        if self.noKeepTestResult.isChecked():
            self.noTr = True

        if nbRunOk:
            if self.configBox.isChecked():
                if self.schedIn.isChecked():
                    second_str = self.schedInLineEdit.text()
                    if second_str == '':
                        second_int = 0
                    else:
                        second_int = int(second_str)
                    if second_int <= 0:
                        QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct number of seconds.")
                    else:
                        self.runAt = (0,0,0,0,0, second_int)
                        self.runType = UCI.SCHED_IN     
                        self.accept()
                elif self.schedAt.isChecked():
                    pydt = self.schedAtDateEdit.dateTime().toPyDateTime()
                    self.delta = pydt - nowWithoutSecond
                    if self.delta.days < 0:
                        QMessageBox.information(self, self.tr("Scheduler") , "Too late...")
                    else:
                        self.runAt = (pydt.year, pydt.month, pydt.day, pydt.hour, pydt.minute, pydt.second)
                        self.runType = UCI.SCHED_AT 
                        self.accept()
            if self.config2Box.isChecked():
                if self.schedEveryMin.isChecked():
                    pydt = self.schedEveryMinDateEdit.dateTime().toPyDateTime()
                    self.runAt = (0, 0, 0, 0, 0, pydt.second)
                    self.runType = UCI.SCHED_EVERY_MIN  
                    self.accept()
                elif self.schedHourly.isChecked():
                    pydt = self.schedHourlyDateEdit.dateTime().toPyDateTime()
                    self.runAt = (0, 0, 0, 0, pydt.minute, pydt.second)
                    self.runType = UCI.SCHED_HOURLY 
                    self.accept()
                elif self.schedDaily.isChecked():
                    pydt = self.schedDailyDateEdit.dateTime().toPyDateTime()
                    self.runAt = (0, 0, 0, pydt.hour, pydt.minute, pydt.second)
                    self.runType = UCI.SCHED_DAILY  
                    self.accept()
                # BEGIN new schedulation type in 3.1.0
                elif self.schedEveryX.isChecked():
                    pydt = self.schedEveryXDateEdit.dateTime().toPyDateTime()
                    if pydt.hour == 0 and pydt.minute == 0 and pydt.second == 0:
                        QMessageBox.information(self, self.tr("Scheduler") , "Please to specify a correct value.")
                    else:
                        self.runAt = (0, 0, 0, pydt.hour, pydt.minute, pydt.second)
                        self.runType = UCI.SCHED_EVERY_X
                        pydtFrom = self.schedEveryXFromEdit.dateTime().toPyDateTime()
                        pydtTo = self.schedEveryXToEdit.dateTime().toPyDateTime()
                        self.runFrom = (0, 0, 0, pydtFrom.hour, pydtFrom.minute, 0)
                        self.runTo = (0, 0, 0, pydtTo.hour, pydtTo.minute, 0)
                        self.accept()

                # END 
                # BEGIN new schedulation type in 3.2.0
                elif self.schedWeekly.isChecked():
                    pydt = self.schedWeeklyDateEdit.dateTime().toPyDateTime()
                    self.runAt = (0, 0, self.comboBoxDays.currentIndex(), pydt.hour, pydt.minute, pydt.second)
                    self.runType = UCI.SCHED_WEEKLY
                    self.accept()
                # END 

    def getSchedtime(self):
        """
        Returns schedule time
        """ 
        return (self.runAt, self.runType, self.runNb, self.noProbes, self.taskEnabled, self.noTr, self.noNotifs,
                    self.runFrom, self.runTo)

