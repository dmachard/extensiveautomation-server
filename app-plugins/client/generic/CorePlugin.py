#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive automation project
# Copyright (c) 2010-2018 Denis Machard
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
#
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensiveautomation.org
# -------------------------------------------------------------------

import sys
import time
import base64
import json
import os
import uuid
try:
    import StringIO
except ImportError: # support python 3
    import io as StringIO

try:
    from PyQt4.QtGui import (QWidget, QMessageBox, QLabel, QVBoxLayout, QTextEdit, QTextCursor,
                            QPushButton, QHBoxLayout, QTabWidget, QApplication, QIcon)
    from PyQt4.QtCore import (QThread, pyqtSignal, Qt, QByteArray, QBuffer, QIODevice, QFile)
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QMessageBox, QLabel, QVBoxLayout, QTextEdit, QTextCursor,
                                QPushButton, QHBoxLayout, QTabWidget, QApplication )
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtCore import (QThread, pyqtSignal, Qt, QByteArray, QBuffer, QIODevice, QFile)

from Resources import Resources
from . import Settings
from .Libs import Logger

LICENSE = """<br />
Default plugin for the Extensive Testing Client
Developed and maintained by Denis Machard

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301 USA<br />
"""

class ClientAlive(QThread):
    """
    Thread for alive client
    """
    ClientDead = pyqtSignal()
    def __init__(self, parent):
        """
        Constructor
        """
        super(ClientAlive, self).__init__()
        self.maxAlive = 15
        self.lastTimestamp = time.time()
        
    def run(self):
        """
        Update last activated
        Emit Qt signal if timeout raised
        """
        timeout = False
        while (not timeout):
            time.sleep(0.1)
            if (time.time() - self.lastTimestamp) >= self.maxAlive:
                timeout = True 
        print("no packet received")
        self.ClientDead.emit()
        
class ReadStdin(QThread):
    """
    Read STD in
    """
    DataIn = pyqtSignal(str)
    def __init__(self, parent):
        """
        Constructor
        """
        super(ReadStdin, self).__init__()

    def run(self):
        """
        Read STD in in loop
        Emit qt signal on data
        """
        while True:
            time.sleep(0.1)

            data = sys.stdin.readline()
            if len(data):
                self.DataIn.emit(data)

class AboutPage(QWidget):
    """
    About page
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(AboutPage, self).__init__()
        self.createWidget()
        
    def createWidget(self):
        """
        Create all widgets
        """
        self.aboutLabel = QLabel(LICENSE)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.aboutLabel)
        self.setLayout(mainLayout)
        
    def updateAbout(self, text):
        """
        Update the about label
        """
        about = "<b>Change logs:</b><br /><span>%s</span>" % self.parseRn()
        about += text
        self.aboutLabel.setText(about)
        
    def parseRn(self):
        """
        """
        fh = QFile(":/releasenotes.txt")
        fh.open(QFile.ReadOnly)
        rn = fh.readAll()
        rn = str(rn, 'utf8')
        fh.close()
        
        rnHtml = [ "<br/>" ]
        for line in rn.splitlines():
            if not line.startswith('\t'):
                pass
            elif line.startswith('\t\t'):
                rnHtml.append("<span>&nbsp;&nbsp;%s</span><br/>" % line)
            elif line.startswith('\t'):
                rnHtml.append("&nbsp;%s<br/>" % line)

        return "".join(rnHtml)
        
class DebugPage(QWidget):
    """
    Debug page
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(DebugPage, self).__init__()  
        self.createWidget()
    
    def createWidget(self):
        """
        Create all widgets
        """
        self.logsEdit = QTextEdit()
        self.logsEdit.setReadOnly(True)
        self.logsEdit.setOverwriteMode(True)
        self.logsEdit.setMinimumWidth(450)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.logsEdit)
        self.setLayout(mainLayout)
        
    def formatTimestamp ( self, timestamp, milliseconds=False):
        """
        Returns human-readable time
        
        @param timestamp: 
        @type timestamp:
        
        @param milliseconds: 
        @type milliseconds: boolean
        
        @return:
        @rtype:
        """
        if isinstance( timestamp, str):
            return "  %s  " % timestamp
        t = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(timestamp) ) 
        if milliseconds:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) + ".%3.3d" % int((timestamp * 1000)  % 1000)
        return t
        
    def autoScrollOnTextEdit(self):
        """
        Autoscroll on text edit
        """
        cursor = self.logsEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logsEdit.setTextCursor(cursor)
        
    def strip_html(self, txt):
        """
        Strip html
        """
        if "<" in txt:
            txt = txt.replace( '<', '&lt;' )
        if ">" in txt:
            txt = txt.replace( '>', '&gt;' )
        return txt
        
    def addLogSuccess(self, txt):
        """
        Add log success
        """
        Logger.instance().info(txt)
        self.logsEdit.insertHtml( "<span style='color:darkgreen'>%s - %s</span><br />" % ( self.formatTimestamp(time.time()), self.strip_html(txt)) )
        self.autoScrollOnTextEdit()

    def addLogWarning(self, txt):
        """
        Add log warning
        """
        Logger.instance().info(txt)
        self.logsEdit.insertHtml( "<span style='color:darkorange'>%s - %s</span><br />" % (self.formatTimestamp(time.time()), self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()
        
    def addLogError(self, txt):
        """
        Add log error
        """
        Logger.instance().error(txt)
        self.logsEdit.insertHtml( "<span style='color:red'>%s - %s</span><br />" % (self.formatTimestamp(time.time()), self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()
        
    def addLog(self, txt):
        """
        Append log to the logsEdit widget
        """
        Logger.instance().debug(txt)
        self.logsEdit.insertHtml( "%s - %s<br />" % (self.formatTimestamp(time.time()), unicode( self.strip_html(txt) )) )
        self.autoScrollOnTextEdit()
        
TAB_ABOUT_PAGE          = 0
TAB_DEBUG_PAGE          = 1

class MainWindow(QWidget):
    """
    Main window
    """
    def __init__(self, pluginName='undefined', pluginType='dummy', debugMode=False, pluginVersion='1.0.0', 
                        pluginIcon=None, pluginDescription='undefined', showMaximized=True ):
        """
        Constructor
        """
        super(MainWindow, self).__init__()
        
        self.debugMode = debugMode
        self.bufSdtIn = ''
        self.clientTmpPath = ''
        self.pluginName = pluginName
        self.pluginType = pluginType
        self.pluginVersion = pluginVersion
        self.pluginIcon = pluginIcon
        self.__showMaximized = showMaximized
        self.isRegistered = False
        
        if self.pluginIcon is None: self.pluginIcon = QIcon(':/plugin.png')
        self.pluginDescription = pluginDescription
        
        self.mainPage = None
        self.settingsPage = None
        self.TAB_MAIN_PAGE = None
        self.TAB_SETTINGS_PAGE = None

        if not self.debugMode: 
            # connect sdtin
            self.stdClient = ReadStdin(self)
            self.stdClient.DataIn.connect(self.on_stdinReadyRead)
            self.stdClient.start()
            
            self.aliveClient = ClientAlive(self)
            self.aliveClient.ClientDead.connect(self.onClientDead)
            self.aliveClient.start()

        self.createWidgets()
    
    def configure(self, pluginName='undefined', pluginType='dummy', pluginVersion='1.0.0', 
                        pluginIcon=None, pluginDescription='undefined', showMaximized=True):
        """
        """
        self.pluginName = pluginName
        self.pluginType = pluginType
        self.pluginVersion = pluginVersion
        self.pluginIcon = pluginIcon
        self.pluginDescription = pluginDescription
        self.__showMaximized = showMaximized
        if self.pluginIcon is None: self.pluginIcon = QIcon(':/plugin.png')
        self.setWindowTitle("%s - %s - %s" % (Settings.instance().readValue( key = 'Common/name' ),
                                    self.pluginName, self.pluginVersion ) )
        
        

        # register the plugin
        if not self.debugMode: self.sendMessage(cmd='register')

    def prepare(self):
        """
        """
        Logger.instance().debug("preparing plugin")
        
        # convert qicon to base64
        pixmapIcon = self.pluginIcon.pixmap(64, 64, mode=QIcon.Normal, state=QIcon.Off  )
        
        byteArray = QByteArray()
        buffer = QBuffer(byteArray)
        buffer.open(QIODevice.WriteOnly)
        pixmapIcon.save(buffer, "png", quality=100 )

        iconBase64 = byteArray.toBase64().data()

        Logger.instance().debug("icon converted to base64")
        
        self.sendMessage(cmd='configure', data=str(iconBase64, 'utf8'), more={"description": self.pluginDescription} )
        
    def createWidgets(self):
        """
        Create all widgets
        """
        self.setWindowIcon(QIcon(':/plugin.png'))
        
        self.mainTab = QTabWidget( )
        
        self.aboutPage = AboutPage(parent=self)
        self.debugPage = DebugPage(parent=self)

        self.mainTab.addTab( self.aboutPage, "About" )
        self.mainTab.addTab( self.debugPage, "Debug" )

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.mainTab)
        self.setLayout(mainLayout)

        self.setWindowTitle("%s - %s - %s" % (Settings.instance().readValue( key = 'Common/name' ), 
                                            self.pluginName, self.pluginVersion ) )
        
        flags = Qt.WindowFlags()
        if not self.debugMode: flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
    def debug(self):
        """
        Return debug page
        """
        return self.debugPage
    
    def about(self):
        """
        Return about page
        """
        return self.aboutPage
        
    def main(self):
        """
        Return main page
        """
        return self.mainPage
        
    def settings(self):
        """
        Return about page
        """
        return self.settingsPage
        
    def closeEvent(self, event):
        """
        On window close event
        """
        if not self.debugMode: 
            self.hide()
            event.ignore()
        
    def addMainPage(self, pageName, widget):
        """
        Add the main page to the tabwidget
        """
        self.mainPage = widget
        if self.settingsPage is not None: 
            self.settingsPage.ReloadSettings.connect(self.mainPage.onReloadSettings)
        self.mainTab.addTab( widget, pageName )
        self.TAB_MAIN_PAGE = self.mainTab.indexOf(widget)
     
    def addSettingsPage(self,  widget):
        """
        Add the settings page to the tabwidget
        """
        self.settingsPage = widget
        self.mainTab.addTab( widget, "Settings" )
        self.TAB_SETTINGS_PAGE = self.mainTab.indexOf(widget)
        
    def updateAboutPage(self, text):
        """
        Update the about text
        """
        self.aboutPage.updateAbout(text=text)
        
    def onClientDead(self):
        """"
        On client terminattion, no more keepalive received from the client
        """
        self.stdClient.terminate()
        self.stdClient.wait()
        
        self.aliveClient.terminate()
        self.aliveClient.wait()
        
        QApplication.quit()
        
    def on_stdinReadyRead(self, data):
        """
        On data in  STD in
        """
        try:
            self.bufSdtIn += data

            pdus = self.bufSdtIn.split("\n\n")
            for pdu in pdus[:-1]:
                try:
                    datagramDecoded = base64.b64decode(pdu)
                    if sys.version_info > (3,): # python 3 support
                        messageJson = json.loads( str(datagramDecoded, "utf8") )
                    else:
                        messageJson = json.loads( datagramDecoded )
                except Exception as e:
                    self.debugPage.addLogError(txt="decode: %s" % e)
                else:
                    self.onPluginMessage(msg=messageJson)
            self.bufSdtIn = pdus[-1]
        except Exception as e:
            self.debugPage.addLogError(txt=e)

    def onPluginMessage(self, msg):
        """
        On message received from the client
        """
        try:
            if not self.isRegistered and msg['cmd'] == 'registered':
                Logger.instance().debug("plugin registered")
                self.clientTmpPath = msg['tmp-path']
                self.debugPage.addLogSuccess(txt="plugin registered [Type=%s]" % self.pluginType)
                self.isRegistered = True
                self.prepare()
                
            elif msg['cmd'] == 'keepalive':
                self.aliveClient.lastTimestamp = time.time()
                Logger.instance().debug("keepalive received")
                
            elif msg['cmd'] == 'run':
                data=None
                
                #read data
                if msg['in-data']:
                    # read the file
                    f = open( "%s/%s" % ( self.clientTmpPath, msg['data-id'] ), 'r')
                    all = f.read()
                    f.close()
                    
                    dataJson = json.loads( all )

                    # delete them
                    os.remove( "%s/%s" % ( self.clientTmpPath, msg['data-id']  ) )
                
                self.__onPluginRun(data=dataJson)
                
            elif msg['cmd'] == 'open-main':
                if self.mainPage is None:
                    return

                if self.TAB_MAIN_PAGE is not None:
                    self.mainTab.setCurrentIndex(self.TAB_MAIN_PAGE)

                self.__showWindows()

                if msg['in-data']:
                    # read the file
                    f = open( "%s/%s" % ( self.clientTmpPath, msg['data-id'] ), 'r')
                    all = f.read()
                    f.close()
                    
                    dataJson = json.loads( all )
                        
                    self.mainPage.insertData(data=dataJson)

                    # delete them
                    os.remove( "%s/%s" % ( self.clientTmpPath, msg['data-id']  ) )

            else:
                pass
        except Exception as e:
            self.debugPage.addLogError(txt="error: %s" % e)
            self.mainTab.setCurrentIndex(TAB_DEBUG_PAGE)
            
            self.__showWindows()

     
    def __showWindows(self):
        """"
        """
        if self.__showMaximized:
            self.showMaximized()
        else:
            self.show()

    def __onPluginRun(self, data):
        """
        Function to reimplement
        """
        try:
            self.onPluginRun(data=data)
            self.sendMessage(cmd="success")
        except Exception as e:
            self.sendMessage(cmd="error", more={"msg": "%s" % e})
            
    def onPluginRun(self, data):
        """
        """
        pass
        
    def sendMessage(self, cmd, data='', more={}):
        """
        Send a message to the client
        """
        inData = False
        msg = {'cmd': cmd }
        
        # save data to temp area
        idFile = ''
        
        
        if len(data):
            try:
                idFile = "%s" % uuid.uuid4()
                pluginDataFile = '%s/%s' % (self.clientTmpPath, idFile)
                with open( pluginDataFile, mode='w') as myfile:
                    myfile.write( json.dumps( data ) )
                inData = True
            except Exception as e:
                print("unable to write data file from plugin: %s" % e)
                Logger.instance().error("unable to write data file from plugin: %s" % e)
                self.debug().addLogError("internal error on send message")

        msg.update( { 'in-data': inData } )

        # add data parameters
        if inData: msg.update( { 'data-id': idFile } )
             
        # add more params
        msg.update(more)
        
        # adding reference
        msg.update( { 'id': self.pluginName, 'name': self.pluginName, 'type': self.pluginType } )
        Logger.instance().debug("%s" % msg)
        
        # encode message and send to stdout
        datagram = json.dumps( msg ) 

        datagramEncoded = base64.b64encode( bytes(datagram, "utf8")  )
        print( str(datagramEncoded, "utf8") )
        sys.stdout.flush()