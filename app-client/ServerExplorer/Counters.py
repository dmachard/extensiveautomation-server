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
Plugin counter
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QGridLayout, QFont, QLabel, QPalette, 
                            QLCDNumber, QFrame, QIcon, QMenu, QMessageBox)
    from PyQt4.QtCore import (Qt)
except ImportError:
    from PyQt5.QtGui import (QFont, QPalette, QIcon)
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QLCDNumber, QFrame, 
                                QMenu, QMessageBox)
    from PyQt5.QtCore import (Qt)
    
from Libs import QtHelper, Logger
import Settings
import zlib

# import UserClientInterface as UCI
import RestClientInterface as RCI

FONT_NAME="SansSerif"
FONT_SIZE=30
FONT_SIZE2=20
FONT_SIZE3=18

NB_LCD_DIGITS=6

class WCounters(QWidget, Logger.ClassLogger):
    """
    Widget to display some counters
    """
    def __init__(self, parent = None):
        """
        Constructs WCounter widget 

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.name = self.tr("Counters")
        self.tests_stats = {}
        self.createWidgets()
        self.createConnections()
        self.createActions()
        self.deactivate()

    def createWidgets(self):
        """
        QtWidgets creation
        """
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        mainLayout = QVBoxLayout()

        gridLayout = QGridLayout()

        font = QFont(FONT_NAME, FONT_SIZE)
        font.setBold(True)


        self.passLabel = QLabel("PASS")
        self.passLabel.setFont(font)          
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.passLabel.setPalette(passPalette)
        self.passLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.failLabel = QLabel("FAILED")
        self.failLabel.setFont(font)    
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.failLabel.setPalette(failPalette)
        self.failLabel.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)

        self.undefLabel = QLabel("UNDEFINED")
        font2 = QFont(FONT_NAME, FONT_SIZE2)
        font2.setBold(False)
        self.undefLabel.setFont(font2)    
        self.undefLabel.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)

        self.totalLabel = QLabel()
        self.totalLabel.setStyleSheet ( """background-color: #EAEAEA;
                                        background-image: url(:/main_logo.png);
                                        background-position: center;
                                        background-repeat: no-repeat;
                                        background-attachment: fixed;""" )
        self.totalLabel.setAlignment(Qt.AlignHCenter)

        self.logoLabel = QLabel()

        # testglobal
        self.counterTgPass = QLCDNumber(self)
        try: # this function does not exist on linux centos 6.3
            self.counterTgPass.setDigitCount(NB_LCD_DIGITS)
        except AttributeError: 
            pass
        self.counterTgPass.setSegmentStyle(QLCDNumber.Flat)
        self.counterTgPass.setFrameShape(QFrame.NoFrame)
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.counterTgPass.setPalette(passPalette)

        self.counterTgFail = QLCDNumber(self)
        try:
            self.counterTgFail.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTgFail.setSegmentStyle(QLCDNumber.Flat)
        self.counterTgFail.setFrameShape(QFrame.NoFrame)
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.counterTgFail.setPalette(failPalette)
        
        self.counterTgUndef = QLCDNumber(self)
        try:
            self.counterTgUndef.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTgUndef.setSegmentStyle(QLCDNumber.Flat)
        self.counterTgUndef.setFrameShape(QFrame.NoFrame)
        underPalette = QPalette()
        underPalette.setColor( QPalette.WindowText,Qt.darkBlue)
        self.counterTgUndef.setPalette(underPalette)
        
        self.counterTgTotal = QLCDNumber(self)
        self.counterTgTotal.setSegmentStyle(QLCDNumber.Flat)
        self.counterTgTotal.setFrameShape(QFrame.NoFrame)

        # testplan
        self.counterTpPass = QLCDNumber(self)
        try:
            self.counterTpPass.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTpPass.setSegmentStyle(QLCDNumber.Flat)
        self.counterTpPass.setFrameShape(QFrame.NoFrame)
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.counterTpPass.setPalette(passPalette)

        self.counterTpFail = QLCDNumber(self)
        try:
            self.counterTpFail.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTpFail.setSegmentStyle(QLCDNumber.Flat)
        self.counterTpFail.setFrameShape(QFrame.NoFrame)
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.counterTpFail.setPalette(failPalette)
        
        self.counterTpUndef = QLCDNumber(self)
        try:
            self.counterTpUndef.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTpUndef.setSegmentStyle(QLCDNumber.Flat)
        self.counterTpUndef.setFrameShape(QFrame.NoFrame)
        underPalette = QPalette()
        underPalette.setColor( QPalette.WindowText,Qt.darkBlue)
        self.counterTpUndef.setPalette(underPalette)
        
        self.counterTpTotal = QLCDNumber(self)
        self.counterTpTotal.setSegmentStyle(QLCDNumber.Flat)
        self.counterTpTotal.setFrameShape(QFrame.NoFrame)

        # testsuites
        self.counterTsPass = QLCDNumber(self)
        try:
            self.counterTsPass.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTsPass.setSegmentStyle(QLCDNumber.Flat)
        self.counterTsPass.setFrameShape(QFrame.NoFrame)
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.counterTsPass.setPalette(passPalette)

        self.counterTsFail = QLCDNumber(self)
        try:
            self.counterTsFail.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTsFail.setSegmentStyle(QLCDNumber.Flat)
        self.counterTsFail.setFrameShape(QFrame.NoFrame)
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.counterTsFail.setPalette(failPalette)
        
        self.counterTsUndef = QLCDNumber(self)
        try:
            self.counterTsUndef.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTsUndef.setSegmentStyle(QLCDNumber.Flat)
        self.counterTsUndef.setFrameShape(QFrame.NoFrame)
        underPalette = QPalette()
        underPalette.setColor( QPalette.WindowText,Qt.darkBlue)
        self.counterTsUndef.setPalette(underPalette)
        
        self.counterTsTotal = QLCDNumber(self)
        self.counterTsTotal.setSegmentStyle(QLCDNumber.Flat)
        self.counterTsTotal.setFrameShape(QFrame.NoFrame)

        # testunit
        self.counterTuPass = QLCDNumber(self)
        try:
            self.counterTuPass.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTuPass.setSegmentStyle(QLCDNumber.Flat)
        self.counterTuPass.setFrameShape(QFrame.NoFrame)
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.counterTuPass.setPalette(passPalette)

        self.counterTuFail = QLCDNumber(self)
        try:
            self.counterTuFail.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTuFail.setSegmentStyle(QLCDNumber.Flat)
        self.counterTuFail.setFrameShape(QFrame.NoFrame)
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.counterTuFail.setPalette(failPalette)
        
        self.counterTuUndef = QLCDNumber(self)
        try:
            self.counterTuUndef.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTuUndef.setSegmentStyle(QLCDNumber.Flat)
        self.counterTuUndef.setFrameShape(QFrame.NoFrame)
        underPalette = QPalette()
        underPalette.setColor( QPalette.WindowText,Qt.darkBlue)
        self.counterTuUndef.setPalette(underPalette)
        
        self.counterTuTotal = QLCDNumber(self)
        self.counterTuTotal.setSegmentStyle(QLCDNumber.Flat)
        self.counterTuTotal.setFrameShape(QFrame.NoFrame)


        # testabstracts
        self.counterTaPass = QLCDNumber(self)
        try:
            self.counterTaPass.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTaPass.setSegmentStyle(QLCDNumber.Flat)
        self.counterTaPass.setFrameShape(QFrame.NoFrame)
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.counterTaPass.setPalette(passPalette)

        self.counterTaFail = QLCDNumber(self)
        try:
            self.counterTaFail.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTaFail.setSegmentStyle(QLCDNumber.Flat)
        self.counterTaFail.setFrameShape(QFrame.NoFrame)
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.counterTaFail.setPalette(failPalette)
        
        self.counterTaUndef = QLCDNumber(self)
        try:
            self.counterTaUndef.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTaUndef.setSegmentStyle(QLCDNumber.Flat)
        self.counterTaUndef.setFrameShape(QFrame.NoFrame)
        underPalette = QPalette()
        underPalette.setColor( QPalette.WindowText,Qt.darkBlue)
        self.counterTaUndef.setPalette(underPalette)
        
        self.counterTaTotal = QLCDNumber(self)
        self.counterTaTotal.setSegmentStyle(QLCDNumber.Flat)
        self.counterTaTotal.setFrameShape(QFrame.NoFrame)

        # testcases
        self.counterTcPass = QLCDNumber(self)
        try:
            self.counterTcPass.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTcPass.setSegmentStyle(QLCDNumber.Flat)
        self.counterTcPass.setFrameShape(QFrame.NoFrame)
        passPalette = QPalette()
        passPalette.setColor( QPalette.WindowText,Qt.darkGreen)
        self.counterTcPass.setPalette(passPalette)

        self.counterTcFail = QLCDNumber(self)
        try:
            self.counterTcFail.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTcFail.setSegmentStyle(QLCDNumber.Flat)
        self.counterTcFail.setFrameShape(QFrame.NoFrame)
        failPalette = QPalette()
        failPalette.setColor( QPalette.WindowText,Qt.red)
        self.counterTcFail.setPalette(failPalette)
        
        self.counterTcUndef = QLCDNumber(self)
        try:
            self.counterTcUndef.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTcUndef.setSegmentStyle(QLCDNumber.Flat)
        self.counterTcUndef.setFrameShape(QFrame.NoFrame)
        underPalette = QPalette()
        underPalette.setColor( QPalette.WindowText,Qt.darkBlue)
        self.counterTcUndef.setPalette(underPalette)
        
        self.counterTcTotal = QLCDNumber(self)
        try:
            self.counterTcTotal.setDigitCount(NB_LCD_DIGITS)
        except AttributeError:
            pass
        self.counterTcTotal.setSegmentStyle(QLCDNumber.Flat)
        self.counterTcTotal.setFrameShape(QFrame.NoFrame)


        font2 = QFont(FONT_NAME, FONT_SIZE2)
        font2.setBold(True)
        self.tgLabel = QLabel("Tests\nGlobal")
        self.tgLabel.setFont(font2)          
        self.tgLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tpLabel = QLabel("Tests\nPlan")
        self.tpLabel.setFont(font2)          
        self.tpLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tsLabel = QLabel("Tests\nSuite")
        self.tsLabel.setFont(font2)          
        self.tsLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tuLabel = QLabel("Tests\nUnit")
        self.tuLabel.setFont(font2)          
        self.tuLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.taLabel = QLabel("Tests\nAbstract")
        self.taLabel.setFont(font2)          
        self.taLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tcLabel = QLabel("Tests\nCase")
        self.tcLabel.setFont(font2)          
        self.tcLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.totLabel = QLabel("TOTAL")
        self.totLabel.setFont(font2)          
        self.totLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        font3 = QFont(FONT_NAME, FONT_SIZE3)
        font3.setItalic(True)
        self.totPassValue = QLabel("0<br />0%")
        self.totPassValue.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.totPassValue.setFont(font3)          
        self.totFailedValue = QLabel("0<br />0%")
        self.totFailedValue.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.totFailedValue.setFont(font3)          
        self.totUndefValue = QLabel("0<br />0%")
        self.totUndefValue.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.totUndefValue.setFont(font3)          
        self.totValue = QLabel("0<br />0%")
        self.totValue.setFont(font3)
        
        self.totValue.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
         
        #gridLayout.addWidget(self.totalLabel, 0, 0)
        
        gridLayout.addWidget(self.tgLabel , 0, 1)
        gridLayout.addWidget(self.tpLabel , 0, 2)
        gridLayout.addWidget(self.tsLabel , 0, 3)
        gridLayout.addWidget(self.tuLabel , 0, 4)
        gridLayout.addWidget(self.taLabel , 0, 5)
        gridLayout.addWidget(self.tcLabel , 0, 6)

        gridLayout.addWidget(self.passLabel, 1, 0)
        gridLayout.addWidget(self.counterTgPass, 1, 1)
        gridLayout.addWidget(self.counterTpPass, 1, 2)
        gridLayout.addWidget(self.counterTsPass, 1, 3)
        gridLayout.addWidget(self.counterTuPass, 1, 4)
        gridLayout.addWidget(self.counterTaPass, 1, 5)
        gridLayout.addWidget(self.counterTcPass, 1, 6)

        gridLayout.addWidget(self.failLabel, 2, 0)
        gridLayout.addWidget(self.counterTgFail, 2, 1)
        gridLayout.addWidget(self.counterTpFail, 2, 2)
        gridLayout.addWidget(self.counterTsFail, 2, 3)
        gridLayout.addWidget(self.counterTuFail, 2, 4)
        gridLayout.addWidget(self.counterTaFail, 2, 5)
        gridLayout.addWidget(self.counterTcFail, 2, 6)

        gridLayout.addWidget(self.undefLabel, 3, 0)
        gridLayout.addWidget(self.counterTgUndef, 3, 1)
        gridLayout.addWidget(self.counterTpUndef, 3, 2)
        gridLayout.addWidget(self.counterTsUndef, 3, 3)
        gridLayout.addWidget(self.counterTuUndef, 3, 4)
        gridLayout.addWidget(self.counterTaUndef, 3, 5)
        gridLayout.addWidget(self.counterTcUndef, 3, 6)

        gridLayout.addWidget(self.counterTgTotal, 4, 1)
        gridLayout.addWidget(self.counterTpTotal, 4, 2)
        gridLayout.addWidget(self.counterTsTotal, 4, 3)
        gridLayout.addWidget(self.counterTuTotal, 4, 4)
        gridLayout.addWidget(self.counterTaTotal, 4, 5)
        gridLayout.addWidget(self.counterTcTotal, 4, 6)

        gridLayout.addWidget(self.totLabel, 0, 7)
        gridLayout.addWidget(self.totPassValue, 1, 7)
        gridLayout.addWidget(self.totFailedValue, 2, 7)
        gridLayout.addWidget(self.totUndefValue, 3, 7)
        gridLayout.addWidget(self.totValue, 4, 7)

        mainLayout.addLayout(gridLayout)

        self.setLayout(mainLayout)

    def createConnections(self):
        """
        Create connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)
    
    def createActions(self):
        """
        Create qt actions
        """
        self.resetAction = QtHelper.createAction(self, "&Reset Statistics", self.resetStats, 
                                            tip = 'Reset all statistics', icon = QIcon(":/reset-counter.png"))

    def onPopupMenu(self, pos):
        """
        On popup menu
        """
        self.menu = QMenu()
        self.menu.addAction( self.resetAction )
        self.menu.addSeparator()
        self.menu.popup( self.mapToGlobal(pos) )

                
    def resetStats(self):
        """
        Reset statistic manually
        """
        reply = QMessageBox.question(self, "Reset statistics", "Are you sure ?",
                                     QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            RCI.instance().resetTestsMetrics()
            
    def active (self):
        """
        Enables
        """
        self.resetAction.setEnabled(True)

    def deactivate (self):
        """
        Clears QTreeWidget and disables it
        """
        self.resetAction.setEnabled(False)


    def resetCounters(self):
        """
        Reset counters
        """
        counters = {
                'testglobals': { 'nb-pass': 0, 'nb-fail': 0, 'nb-undef': 0 },
                'testplans': { 'nb-pass': 0, 'nb-fail': 0, 'nb-undef': 0  },
                'testsuites': { 'nb-pass': 0, 'nb-fail': 0, 'nb-undef': 0  },
                'testunits': { 'nb-pass': 0, 'nb-fail': 0, 'nb-undef': 0  },
                'testabstracts': { 'nb-pass': 0, 'nb-fail': 0, 'nb-undef': 0  },
                'testcases': { 'nb-pass': 0, 'nb-fail': 0, 'nb-undef': 0  }
        }
        self.loadData( counters=counters )
        
    def loadData (self, counters):
        """
        Load value of each counters

        @param parent: 
        @type parent:
        """
        self.tests_stats = counters

        self.counterTgPass.display(counters['testglobals']['nb-pass'])
        self.counterTgFail.display(counters['testglobals']['nb-fail'])
        self.counterTgUndef.display(counters['testglobals']['nb-undef'])
        self.counterTgTotal.display( counters['testglobals']['nb-pass'] + counters['testglobals']['nb-fail'] + counters['testglobals']['nb-undef'])

        self.counterTpPass.display(counters['testplans']['nb-pass'])
        self.counterTpFail.display(counters['testplans']['nb-fail'])
        self.counterTpUndef.display(counters['testplans']['nb-undef'])
        self.counterTpTotal.display( counters['testplans']['nb-pass'] + counters['testplans']['nb-fail'] + counters['testplans']['nb-undef'])

        self.counterTsPass.display(counters['testsuites']['nb-pass'])
        self.counterTsFail.display(counters['testsuites']['nb-fail'])
        self.counterTsUndef.display(counters['testsuites']['nb-undef'])
        self.counterTsTotal.display( counters['testsuites']['nb-pass'] + counters['testsuites']['nb-fail'] + counters['testsuites']['nb-undef'])

        self.counterTuPass.display(counters['testunits']['nb-pass'])
        self.counterTuFail.display(counters['testunits']['nb-fail'])
        self.counterTuUndef.display(counters['testunits']['nb-undef'])
        self.counterTuTotal.display( counters['testunits']['nb-pass'] + counters['testunits']['nb-fail'] + counters['testunits']['nb-undef'])

        self.counterTaPass.display(counters['testabstracts']['nb-pass'])
        self.counterTaFail.display(counters['testabstracts']['nb-fail'])
        self.counterTaUndef.display(counters['testabstracts']['nb-undef'])
        self.counterTaTotal.display( counters['testabstracts']['nb-pass'] + counters['testabstracts']['nb-fail'] + counters['testabstracts']['nb-undef'])

        self.counterTcPass.display(counters['testcases']['nb-pass'])
        self.counterTcFail.display(counters['testcases']['nb-fail'])
        self.counterTcUndef.display(counters['testcases']['nb-undef'])
        self.counterTcTotal.display( counters['testcases']['nb-pass'] + counters['testcases']['nb-fail'] + counters['testcases']['nb-undef'])

        nbPass =  counters['testglobals']['nb-pass']+counters['testplans']['nb-pass']+counters['testsuites']['nb-pass']+counters['testunits']['nb-pass'] \
                    + counters['testabstracts']['nb-pass']+counters['testcases']['nb-pass']
        nbUndef = counters['testglobals']['nb-undef']+counters['testplans']['nb-undef']+counters['testsuites']['nb-undef']+counters['testunits']['nb-undef'] \
                    + counters['testabstracts']['nb-undef'] + counters['testcases']['nb-undef']
        nbFailed = counters['testglobals']['nb-fail']+counters['testplans']['nb-fail']+counters['testsuites']['nb-fail']+counters['testunits']['nb-fail'] \
                    + counters['testabstracts']['nb-fail'] + counters['testcases']['nb-fail']
        nbTot = nbPass+nbUndef+nbFailed
        if nbTot:
            self.totPassValue.setText( "%s<br />(%s%%)" % (nbPass, round( (nbPass*100)/ float(nbTot), 1 ) ) )
            self.totFailedValue.setText( "%s<br />(%s%%)" % (nbFailed, round( (nbFailed*100)/ float(nbTot), 1) ) )
            self.totUndefValue.setText( "%s<br />(%s%%)" % (nbUndef, round( (nbUndef*100)/ float(nbTot), 1) ) )
        else:
            self.totPassValue.setText( "0<br />(0%)" )
            self.totFailedValue.setText( "0<br />(0%)" )
            self.totUndefValue.setText( "0<br />(0%)" )
            
        self.totValue.setText( "%s" % nbTot )

    def refreshData(self, data, action ):
        """
        Refresh counters

        @param parent: 
        @type parent:

        @param parent: 
        @type parent:
        """
        self.loadData(counters=data)

CTR = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return CTR

def initialize (parent):
    """
    Initialize WCounters widget

    @param parent: 
    @type parent:
    """
    global CTR
    CTR = WCounters(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global CTR
    if CTR:
        CTR = None