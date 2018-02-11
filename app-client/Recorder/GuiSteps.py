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
Recorder Gui extension for the extensive client
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QPixmap, QImage, QBrush, QFont, QItemDelegate, QApplication, 
                            QStyleOptionButton, QStyle, QCheckBox, QTableView, QAbstractItemView, 
                            QFrame, QIcon, QMenu, QMessageBox, QColor, QClipboard)
    from PyQt4.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, 
                            QMimeData, QByteArray)
except ImportError:
    from PyQt5.QtGui import (QPixmap, QImage, QBrush, QFont, QIcon, QColor, QClipboard)
    from PyQt5.QtWidgets import (QItemDelegate, QApplication, QStyleOptionButton, QStyle, 
                                QCheckBox, QTableView, QAbstractItemView, QFrame, QMenu, 
                                QMessageBox)
    from PyQt5.QtCore import (QVariant, QAbstractTableModel, QModelIndex, Qt, pyqtSignal, 
                            QMimeData, QByteArray)
                            
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

import pickle
import base64 

COL_ICON            =   0
COL_ID              =   1
COL_NAME            =   2
COL_VALUE           =   3
COL_DESCRIPTION     =   4

HEADERS_DEF             = (  '', 'Id', 'Actions', 'Values', 'Description' )

ACTION_ANYTHING             = "Anything"
ACTION_BROWSER              = "Browser"
ACTION_ANDROID              = "Android"
ACTION_FRAMEWORK            = "Framework"
ACTION_SYSTEM               = "System"
ACTION_DB                   = "Database"

# sikuli actions
CLICK_WORD                  = 'CLICK ON WORD'
DOUBLE_CLICK_WORD           = 'DOUBLE CLICK ON WORD'
RIGHT_CLICK_WORD            = 'RIGHT CLICK ON WORD'
WAIT_WORD                   = 'WAIT WORD'
WAIT_CLICK_WORD             = 'WAIT AND CLICK ON WORD'

CLICK_IMAGE                 = 'CLICK ON IMAGE'
CLICK_IMAGE_ALL             = 'CLICK ON ALL'
DOUBLE_CLICK_IMAGE          = 'DOUBLE CLICK ON IMAGE'
DOUBLE_CLICK_IMAGE_ALL      = 'DOUBLE CLICK ON ALL'
RIGHT_CLICK_IMAGE           = 'RIGHT CLICK ON IMAGE'
RIGHT_CLICK_IMAGE_ALL       = 'RIGHT CLICK ON ALL'

HOVER_IMAGE                 = 'HOVER MOUSE ON'
DRAG_DROP_IMAGE             = 'DRAG IMAGE AND DROP TO'

DONT_FIND_IMAGE             = 'DONT FIND IMAGE'
FIND_IMAGE                  = 'FIND IMAGE'
FIND_CLICK_IMAGE            = 'FIND AND CLICK IMAGE'

WAIT_IMAGE                  = 'WAIT IMAGE'
WAIT_CLICK_IMAGE            = 'WAIT AND CLICK ON IMAGE'

TYPE_TEXT                   = 'TYPE TEXT'
TYPE_TEXT_PATH              = 'TYPE PATH'
TYPE_PASSWORD               = 'TYPE PASSWORD'
GET_TEXT                    = 'GET TEXT'
GET_TEXT_CLIPBOARD          = 'GET TEXT FROM CLIPBOARD'

TYPE_TEXT_ON                = 'TYPE TEXT ON'
AND_TYPE_TEXT               = 'AND TYPE TEXT IN'

MOUSE_WHEEL_DOWN            = 'MOUSE WHEEL DOWN'
MOUSE_WHEEL_UP              = 'MOUSE WHEEL UP'

MOUSE_CLICK_POSITION              = 'CLICK ON POSITION'
MOUSE_DOUBLE_CLICK_POSITION       = 'DOUBLE CLICK ON POSITION'
MOUSE_RIGHT_CLICK_POSITION        = 'RIGHT CLICK ON POSITION'
MOUSE_MOVE_POSITION               = 'MOVE TO POSITION'

SHORTCUT                    = 'KEYBOARD SHORTCUT'

# action help
ACTION_DESCR = [
        { CLICK_WORD:                "Detect the word on the screen and click on it" },  
        { DOUBLE_CLICK_WORD:         "Detect the word on the screen and double click on it" }, 
        { RIGHT_CLICK_WORD:          "Detect the word on the screen and right click on it" },    
        { WAIT_WORD:                 "Search the word until it appears" },   
        { WAIT_CLICK_WORD:           "Search the word until it appears and click on it" },  
        "",
        { CLICK_IMAGE:                "Detect the visual pattern on the screen and click on it" },      
        { DOUBLE_CLICK_IMAGE:         "Detect the visual pattern on the screen and double click on it" },      
        { RIGHT_CLICK_IMAGE:          "Detect the visual pattern on the screen and right click on it" },      
        { WAIT_IMAGE:                 "Search the visual pattern until the image appears" },   
        { WAIT_CLICK_IMAGE:           "Search the visual pattern until the image appears and click on it" },   
        { HOVER_IMAGE:                "Detect the visual pattern on the screen and mouve the cursor on it" },      
        { DRAG_DROP_IMAGE:            "Detect the visual pattern on the screen and drop it to the position (x,y)" },  
        "",
        { MOUSE_CLICK_POSITION:               "Click on the position (x,y)" }, 
        { MOUSE_DOUBLE_CLICK_POSITION:        "Double click on the position (x,y)" }, 
        { MOUSE_RIGHT_CLICK_POSITION:         "Right click on the position (x,y)" }, 
        { MOUSE_MOVE_POSITION:                "Move to the position (x,y)" }, 
        { MOUSE_WHEEL_UP:               "Mouse wheel up" }, 
        { MOUSE_WHEEL_DOWN:             "Mouse wheel down" }, 
        "",
        { TYPE_TEXT:                  "Simulate keyboard and type text" }, 
        { TYPE_TEXT_PATH:             "Simulate keyboard and type text path" }, 
        { TYPE_PASSWORD:              "Simulate keyboard and type password" }, 
        { SHORTCUT:                   "Simulate keyboard interactions" }, 
        { GET_TEXT_CLIPBOARD:         "Get text from clipboard" }
]

# selenium actions
BROWSER_OPEN                            = 'OPEN BROWSER'
BROWSER_OPEN_FIREFOX                    = 'OPEN FIREFOX'
BROWSER_OPEN_IE                         = 'OPEN IE'
BROWSER_OPEN_CHROME                     = 'OPEN CHROME'
BROWSER_CLOSE                           = 'CLOSE BROWSER'
BROWSER_MAXIMIZE                        = 'MAXIMIZE BROWSER'
BROWSER_WAIT_ELEMENT                    = 'WAIT HTML ELEMENT'
BROWSER_WAIT_CLICK_ELEMENT              = 'WAIT AND CLICK ON HTML ELEMENT'
BROWSER_WAIT_VISIBLE_ELEMENT            = 'WAIT VISIBLE HTML ELEMENT'
BROWSER_WAIT_NOT_VISIBLE_ELEMENT        = 'WAIT NOT VISIBLE HTML ELEMENT'
BROWSER_WAIT_VISIBLE_CLICK_ELEMENT      = 'WAIT VISIBLE AND CLICK ON HTML ELEMENT'
BROWSER_HOVER_ELEMENT                   = 'HOVER ON HTML ELEMENT'
BROWSER_DOUBLE_CLICK_ELEMENT            = 'DOUBLE CLICK ON HTML ELEMENT'
BROWSER_CLICK_ELEMENT                   = 'CLICK ON HTML ELEMENT'
BROWSER_GET_TEXT_ELEMENT                = 'GET TEXT FROM HTML ELEMENT'
BROWSER_GET_TITLE                       = 'GET PAGE TITLE'
BROWSER_GET_URL                         = 'GET PAGE URL'
BROWSER_GET_SOURCE                      = 'GET PAGE CODE SOURCE'
BROWSER_TYPE_KEY                        = 'TYPE KEYBOARD SHORTCUT'
BROWSER_TYPE_TEXT                       = 'TYPE TEXT ON HTML ELEMENT'
BROWSER_CLEAR_TEXT_ELEMENT              = 'CLEAR TEXT IN HTML ELEMENT' # new in v12

BROWSER_REFRESH                         = 'REFRESH PAGE'
BROWSER_GO_BACK                         = 'GO BACK'
BROWSER_GO_FORWARD                      = 'GO FORWARD'

BROWSER_CLOSE_WINDOW                    = 'CLOSE CURRENT WINDOW'
BROWSER_SWITCH_MAIN_WINDOW              = 'SWITCH TO MAIN WINDOW'
BROWSER_SWITCH_NEXT_WINDOW              = 'SWITCH TO NEXT WINDOW'
BROWSER_SWITCH_TO_FRAME                 = 'SWITCH TO FRAME'
BROWSER_SWITCH_TO_WINDOW                = 'SWITCH TO WINDOW'
BROWSER_SWITCH_TO_SESSION               = 'SWITCH TO SESSION'

BROWSER_ACCEPT_ALERT                    = 'ACCEPT ALERT'
BROWSER_DISMISS_ALERT                   = 'DISMISS ALERT'
BROWSER_GET_TEXT_ALERT                  = 'GET TEXT ALERT'
BROWSER_AUTHENTICATE_ALERT              = 'AUTHENTICATE ALERT'

BROWSER_FIND_TEXT_ELEMENT               = 'FIND TEXT IN HTML ELEMENT'
BROWSER_FIND_TEXT_TITLE                 = 'FIND TEXT IN TITLE'
BROWSER_FIND_TEXT_GET_URL               = 'FIND TEXT IN URL'
BROWSER_FIND_TEXT_GET_SOURCE            = 'FIND TEXT IN CODE SOURCE'

BROWSER_SELECT_TEXT                     = 'SELECT ITEM BY TEXT'
BROWSER_SELECT_VALUE                    = 'SELECT ITEM BY VALUE'

BROWSER_EXECUTE_JS                      = 'EXECUTE JAVASCRIPT ON HTML ELEMENT'

MOVE_DOWN    = -1
MOVE_UP      = 1

ACTION_BROWSER_DESCR = [
        { BROWSER_OPEN:                           "Open browser on the desktop and load the url.\n\nNote for Internet Explorer: \n- Adding the domain of the site to the list of Trusted Sites!\n- Enhanced Protected Mode must be disabled for IE 10 and higher!\n- The browser zoom level must be set to 100%!\n- Registry entry FEATURE_BFCACHE must be added!" },
        { BROWSER_CLOSE:                          "Close the current browser on the desktop" },
        { BROWSER_MAXIMIZE:                       "Maximize the browser" },
        "",
        { BROWSER_EXECUTE_JS:                     "Execute javascript on html element" },
        "",
        { BROWSER_REFRESH:                        "Refresh the current page" },
        { BROWSER_GO_BACK:                        "Go back" },
        { BROWSER_GO_FORWARD:                     "Go forward" },
        "",
        { BROWSER_FIND_TEXT_ELEMENT:              "Find text in the specified html element" },
        { BROWSER_FIND_TEXT_TITLE:                "Find text in title of the html page" },
        { BROWSER_FIND_TEXT_GET_URL:              "Find text in the url" },
        { BROWSER_FIND_TEXT_GET_SOURCE:           "Find text in the web source page" },
        "",
        { BROWSER_CLOSE_WINDOW:                   "Close the current window" },
        { BROWSER_SWITCH_MAIN_WINDOW:             "Switch to main window"},
        { BROWSER_SWITCH_NEXT_WINDOW:             "Switch to the next window" },
        { BROWSER_SWITCH_TO_FRAME:                "Switch to the frame" },
        { BROWSER_SWITCH_TO_WINDOW:               "Switch to the window" },
        { BROWSER_SWITCH_TO_SESSION:              "Switch to the session" },
        "",
        { BROWSER_ACCEPT_ALERT:                   "Accept the javascript alert" },
        { BROWSER_DISMISS_ALERT:                  "Dismiss the javascript alert" },
        { BROWSER_GET_TEXT_ALERT:                 "Get the text in the javascript alert" },
        "",
        { BROWSER_WAIT_ELEMENT:                   "Wait html element to appear on the DOM page" },
        { BROWSER_WAIT_CLICK_ELEMENT:             "Wait html element to appear on the DOM page and click on it" },
        { BROWSER_WAIT_VISIBLE_ELEMENT:           "Wait html element to be visible" },
        { BROWSER_WAIT_NOT_VISIBLE_ELEMENT:       "Wait html element to be not visible" },
        { BROWSER_WAIT_VISIBLE_CLICK_ELEMENT:     "Wait html element to be visible and click on it" },
        { BROWSER_HOVER_ELEMENT:                  "Move the mouse on the html element" },
        { BROWSER_CLICK_ELEMENT:                  "Click on the html element" },
        { BROWSER_DOUBLE_CLICK_ELEMENT:            "Double click on the html element" },
        { BROWSER_CLEAR_TEXT_ELEMENT:             "Clear the text on the html element" },
        "",
        { BROWSER_GET_TEXT_ELEMENT:               "Get the text of the html element" },
        { BROWSER_GET_TITLE:                      "Get the title of the web page" },
        { BROWSER_GET_URL:                        "Get the url" },
        { BROWSER_GET_SOURCE:                     "Get the source of the web page" },
        "",
        { BROWSER_SELECT_TEXT:                    "Select item according to the text" },
        { BROWSER_SELECT_VALUE:                   "Select item according to the value attribute" },
        "",
        { BROWSER_TYPE_KEY:                       "Type key shorcut on html element" },
        { BROWSER_TYPE_TEXT:                      "Type text on html element" },
]

# android mobile
ANDROID_WAKUP               = "WAKE UP"
ANDROID_UNLOCK              = "UNLOCK"
ANDROID_LOCK                = "LOCK"
ANDROID_REBOOT              = "REBOOT"
ANDROID_SLEEP               = "SLEEP"
ANDROID_FREEZE_ROTATION     = "FREEZE ROTATION"
ANDROID_UNFREEZE_ROTATION   = "UNFREEZE ROTATION"
ANDROID_BOOTLOADER          = "BOOTLOADER"
ANDROID_RECOVERY            = "RECOVERY"
ANDROID_NOTIFICATION        = "OPEN NOTIFICATION"
ANDROID_SETTINGS            = "OPEN SETTINGS"
ANDROID_TYPE_SHORTCUT       = "TYPE SHORTCUT"
ANDROID_TYPE_KEYCODE        = "TYPE KEYCODE"
ANDROID_DEVICEINFO          = "DEVICE INFO"
ANDROID_GET_LOGS            = "GET LOGS"
ANDROID_CLEAR_LOGS          = "CLEAR LOGS"
ANDROID_CLEAR_ELEMENT       = "CLEAR XML ELEMENT"
ANDROID_CLICK_ELEMENT       = "CLICK ON XML ELEMENT"
ANDROID_LONG_CLICK_ELEMENT  = "LONG CLICK ON XML ELEMENT"
ANDROID_EXIST_ELEMENT       = "EXIST XML ELEMENT"
ANDROID_WAIT_ELEMENT        = "WAIT XML ELEMENT"
ANDROID_COMMAND             = "INPUT"
ANDROID_SHELL               = "SHELL"
ANDROID_RESET_APP           = "RESET APPLICATION"
ANDROID_STOP_APP            = "STOP APPLICATION"

ANDROID_TYPE_TEXT_ELEMENT   = "TYPE TEXT ON XML ELEMENT"
ANDROID_GET_TEXT_ELEMENT    = "GET TEXT FROM XML ELEMENT"

ANDROID_CLICK_POSITION      = "CLICK TO POSITION"
ANDROID_DRAG_ELEMENT        = "DRAG XML ELEMENT"
ANDROID_DRAG_POSITION       = "DRAG FROM POSITION"
ANDROID_SWIPE_POSITION      = "SWIPE FROM POSITION"

ANDROID_SLEEP_LOCK          = "SLEEP AND LOCK"
ANDROID_WAKEUP_UNLOCK       = "WAKE UP AND UNLOCK"
ANDROID_WAIT_CLICK_ELEMENT  = "WAIT AND CLICK ON XML ELEMENT"

ACTION_ANDROID_DESCR = [
            { ANDROID_WAKEUP_UNLOCK:          "Wake up and unlock the device" },
            { ANDROID_WAKUP:                  "Wake up the device" },
            { ANDROID_UNLOCK:                 "Unlock the device" },
            { ANDROID_LOCK:                   "Lock the device" },
            { ANDROID_REBOOT:                 "Reboot the device" },
            { ANDROID_SLEEP:                  "Go to sleep" },
            { ANDROID_SLEEP_LOCK:             "Go to sleep and lock the device" },
            "",
            { ANDROID_FREEZE_ROTATION:        "Freeze the rotation on the device" },
            { ANDROID_UNFREEZE_ROTATION:      "Unfreeze the rotation on the device" },
            "",
            { ANDROID_BOOTLOADER:             "Reboot the device into the bootloader" },
            { ANDROID_RECOVERY:               "Reboot the device into the recovery mode" },
            "",
            { ANDROID_NOTIFICATION:           "Open notification panel" },
            { ANDROID_SETTINGS:               "Open settings panel" },
            { ANDROID_DEVICEINFO:             "Device info" },
            "",
            { ANDROID_GET_LOGS:               "Get device logs" },
            { ANDROID_CLEAR_LOGS:             "Clear device logs" },
            "",
            { ANDROID_TYPE_SHORTCUT:          "Type shortcut on device" },
            { ANDROID_TYPE_KEYCODE:           "Type key code on device" },
            { ANDROID_COMMAND:                "Run system command on device with input adb" },
            { ANDROID_SHELL:                  "Run shell command on device with input adb" },
            "",
            { ANDROID_STOP_APP:               "Stop application according to the package name" },
            { ANDROID_RESET_APP:              "Reset the application, stop it and clear all user data" },
            "",
            { ANDROID_CLEAR_ELEMENT:          "Clear the text in the ui element" },
            { ANDROID_CLICK_ELEMENT:          "Click on the ui element" },
            { ANDROID_LONG_CLICK_ELEMENT:     "Long click on the ui element" },
            { ANDROID_EXIST_ELEMENT:          "Check if the ui element exists" },
            { ANDROID_WAIT_ELEMENT:           "Wait ui element to appear on mobile screen" },
            { ANDROID_DRAG_ELEMENT:            "Drag ui element to x2,y2" },
            { ANDROID_WAIT_CLICK_ELEMENT:      "Wait ui element to appear on mobile screen and click on it" },
            "",
            { ANDROID_TYPE_TEXT_ELEMENT:      "Type text on ui element" },
            { ANDROID_GET_TEXT_ELEMENT:         "Get text from the ui element" },
            "",
            { ANDROID_CLICK_POSITION:           "Click on position x,y" },
            { ANDROID_DRAG_POSITION:            "Drag from position x1,y1 to x2,y2" },
            { ANDROID_SWIPE_POSITION:           "Swipe from position x1,y1 to x2,y2" },
]

OP_ANY = "Any"
OP_CONTAINS = "Contains"
OP_NOTCONTAINS = "NotContains"
OP_REGEXP = "RegEx"
OP_NOTREGEXP = "NotRegEx"
OP_STARTSWITH = "Startswith"
OP_NOTSTARTSWITH = "NotStartswith"
OP_ENDSWITH = "Endswith"
OP_NOTENDSWITH = "NotEndswith"

FRAMEWORK_INFO              = "LOG MESSAGE"
FRAMEWORK_WARNING           = "LOG WARNING"
FRAMEWORK_USERCODE          = "USERCODE"
FRAMEWORK_WAIT              = "WAIT DURING"
FRAMEWORK_CACHE_SET         = "SET VALUE"
FRAMEWORK_CACHE_RESET       = "RESET CACHE"
FRAMEWORK_CACHE_DELETE      = "DELETE CACHE"
FRAMEWORK_INTERACT          = "ASK SOMETHING"
FRAMEWORK_CHECK_STRING      = "CHECKING IF VALUE"
ACTION_FRAMEWORK_DESCR = [
        { FRAMEWORK_INFO:               "Display an information message" },
        { FRAMEWORK_WARNING:            "Display a warning message" },
        "",
        { FRAMEWORK_CACHE_SET:          "Save data in cache" },
        { FRAMEWORK_CACHE_RESET:        "Reset the cache, delete all data"},
        "",
        { FRAMEWORK_USERCODE:           "Add specific actions in generated test" }, 
        { FRAMEWORK_WAIT:               "Just wait during XX seconds" },
        "",
        { FRAMEWORK_CHECK_STRING:       "Checking the value and expect to find something" },
        { FRAMEWORK_INTERACT:           "Interact with user" } 
]

SYSTEM_SESSION              = "OPEN SSH SESSION"
SYSTEM_CLOSE                = "CLOSE SESSION"
SYSTEM_CLEAR_SCREEN         = "CLEAR SCREEN"
SYSTEM_TEXT                 = "SEND TEXT"
SYSTEM_SHORTCUT             = "SEND SHORTCUT"
SYSTEM_CHECK_SCREEN         = "CHECKING IF SCREEN"

ACTION_SYSTEM_DESCR = [
        { SYSTEM_SESSION:             "Open a ssh session" },
        { SYSTEM_CLOSE:               "Close the ssh session" },
        "",
        { SYSTEM_CLEAR_SCREEN:        "Clear the screen" },  
        "",
        { SYSTEM_TEXT:                  "Send text" }, 
        { SYSTEM_SHORTCUT:               "Send shortcut" }, 
        "",
        { SYSTEM_CHECK_SCREEN:            "Expect text in screen" }
]

class StepsTableModel(QAbstractTableModel, Logger.ClassLogger):
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
        self.nbCol = len(HEADERS_DEF)
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
            return HEADERS_DEF[section]

        return None

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
        if 'active' not in self.mydata[ index.row() ]: # backward compatibility
            self.mydata[ index.row() ]['active'] = "True"

        elif index.column() == COL_NAME:
            return self.mydata[ index.row() ]['action']
        
        elif index.column() == COL_VALUE:
            if 'parameters' not in self.mydata[ index.row() ]:
                self.mydata[ index.row() ]['parameters'] = {}
                
            if self.mydata[ index.row() ]['action'] in [ FRAMEWORK_WAIT, MOUSE_WHEEL_UP, MOUSE_WHEEL_DOWN ] :
                return self.mydata[ index.row() ]['misc']
                
            elif self.mydata[ index.row() ]['action'] in [ TYPE_TEXT, TYPE_TEXT_PATH, TYPE_PASSWORD ]:
                return self.mydata[ index.row() ]['text']
                
            else:
                return self.mydata[ index.row() ]['image']

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
        
        # begin fix model for backward compatibility
        if 'parameters' not in self.mydata[ index.row() ]:
            self.mydata[ index.row() ]['parameters'] = {}

        if 'from-cache' not in self.mydata[ index.row() ]:
            self.mydata[ index.row() ]['from-cache'] = False
        if 'from-alias' not in self.mydata[ index.row() ]:
            self.mydata[ index.row() ]['from-alias'] = False
            
        if 'from-cache' not in self.mydata[ index.row() ]['parameters']:
            self.mydata[ index.row() ]['parameters']['from-cache'] = self.mydata[ index.row() ]['from-cache']
        if 'from-alias' not in self.mydata[ index.row() ]['parameters']:
            self.mydata[ index.row() ]['parameters']['from-alias'] = self.mydata[ index.row() ]['from-alias']
        if 'from-el-cache' not in self.mydata[ index.row() ]['parameters']:
            self.mydata[ index.row() ]['parameters']['from-el-cache'] = self.mydata[ index.row() ]['from-cache']
        if 'from-el-alias' not in self.mydata[ index.row() ]['parameters']:
            self.mydata[ index.row() ]['parameters']['from-el-alias'] = self.mydata[ index.row() ]['from-alias'] 

        if 'to-cache' not in self.mydata[ index.row() ]['parameters']:
            self.mydata[ index.row() ]['parameters']['to-cache'] = self.mydata[ index.row() ]['from-cache']
        if 'to-alias' not in self.mydata[ index.row() ]['parameters']:
            self.mydata[ index.row() ]['parameters']['to-alias'] = self.mydata[ index.row() ]['from-alias']
        # end

        if role == Qt.DecorationRole:
            if index.column() == COL_VALUE:
                if self.mydata[ index.row() ]['action'] in [ CLICK_IMAGE, DOUBLE_CLICK_IMAGE, RIGHT_CLICK_IMAGE, WAIT_IMAGE, WAIT_CLICK_IMAGE, 
                                                            HOVER_IMAGE, DRAG_DROP_IMAGE ]:
                    shortcut = base64.b64decode(value)
                    thumbail = QPixmap()
                    thumbail.loadFromData(shortcut)
                    if thumbail.height() > 120 and thumbail.width() > 120:
                        return QImage(thumbail).scaled(120,120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    else:
                        return QImage(thumbail)
                        
            if index.column() in [ COL_ICON ]:
                if 'action-type' in self.mydata[ index.row() ]:
                    if self.mydata[ index.row() ]['action-type'] == ACTION_ANDROID:
                        return QIcon(":/recorder-mobile-small.png")
                    elif self.mydata[ index.row() ]['action-type'] == ACTION_BROWSER:
                        return QIcon(":/recorder-web-small.png")
                    elif self.mydata[ index.row() ]['action-type'] == ACTION_ANYTHING:
                        return QIcon(":/recorder-app-small.png")
                    elif self.mydata[ index.row() ]['action-type'] == ACTION_SYSTEM:
                        return QIcon(":/system-small.png")
                
        # color display
        elif role == Qt.ForegroundRole:
            # new in v16
            if self.mydata[ index.row() ]['active'] == "False":
                return q(QBrush(QColor(0, 0, 0)))
            # end of new 

            if index.column() in [ COL_NAME ]:
                return q(QBrush(QColor(0, 0, 0)))
                    
            if index.column() in [ COL_DESCRIPTION ]:
                return q(QBrush(QColor(128, 128, 128)))

            if index.column() in [ COL_VALUE ]:
                return q(QBrush(QColor(0, 0, 255)))
        
        elif role == Qt.ToolTipRole:
            if index.column() in [ COL_NAME ]:
                return q( "Double click to edit." )
            if index.column() in [ COL_VALUE ]:
                if self.mydata[ index.row() ]['action'] in [ SYSTEM_TEXT ] : 
                    return q( "%s" % ( self.mydata[ index.row() ]['parameters']['text'] ) )
                    
        # font display
        elif role == Qt.FontRole:
            
            # new in v16
            if self.mydata[ index.row() ]['active'] == "False":
                font = QFont()
                font.setItalic(True)
                font.setStrikeOut(True)
                return q(font)
            # end of new

            if index.column() in [ COL_NAME, COL_VALUE, COL_DESCRIPTION ]:
                if self.mydata[ index.row() ]['action'] in [ FRAMEWORK_USERCODE, FRAMEWORK_WAIT]:
                    font = QFont()
                    return q(font)
                else:  
                    if "bold" in self.mydata[ index.row() ]:
                        if self.mydata[ index.row() ]['bold']:
                            font = QFont()
                            font.setBold(True)
                            return q(font)
                        else:
                            font = QFont()
                            font.setBold(False)
                            return q(font)
                    else:
                        font = QFont()
                        return q(font)

        elif role == Qt.TextAlignmentRole:
            if index.column() in [ COL_ID, COL_VALUE ]:
                return q(Qt.AlignLeft| Qt.AlignVCenter)
            if index.column() == COL_NAME:
                return q(Qt.AlignRight | Qt.AlignVCenter)

        # main display
        elif role == Qt.DisplayRole: 
            if index.column() == COL_ID:
                return q(value)
            if index.column() == COL_DESCRIPTION:
                return q( " - %s" % value)
                    
            # display browser actions
            if self.mydata[ index.row() ]['action'] in [ BROWSER_OPEN ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append( "AND LOAD URL FROM CACHE" )
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append( "AND LOAD URL WITH ALIAS" )
                    else:
                        actions.append( "AND LOAD URL" )
                        
                    actions.append( "WITH SESSION NAME" )
                        
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE:    
                    values = [ "%s" % self.mydata[ index.row() ]['misc'] ] 
                    values.append( "%s" % self.mydata[ index.row() ]['text'] )
                    if "session-name" in self.mydata[ index.row() ]['parameters']:
                        values.append( "%s" % self.mydata[ index.row() ]['parameters']['session-name'] )
                    else:
                        values.append( "default" )
                    return q( "\n".join(values) )
            
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_CLOSE, BROWSER_MAXIMIZE, BROWSER_REFRESH, BROWSER_GO_BACK, BROWSER_GO_FORWARD,
                                                            BROWSER_CLOSE_WINDOW, BROWSER_SWITCH_NEXT_WINDOW, BROWSER_ACCEPT_ALERT, BROWSER_DISMISS_ALERT,
                                                            BROWSER_SWITCH_MAIN_WINDOW ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ]
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE:    
                    values = [ ] 
                    return q( "\n".join(values) )
            
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_FIND_TEXT_TITLE, BROWSER_FIND_TEXT_GET_URL, 
                                                            BROWSER_FIND_TEXT_GET_SOURCE, BROWSER_SWITCH_TO_WINDOW,
                                                            BROWSER_SWITCH_TO_SESSION ]:
                if index.column() == COL_NAME:
                    actions = [  ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append( "%s" % value )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE:    
                    values = [ ] 
                    values.append( "%s" % (self.mydata[ index.row() ]['text-more']) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_WAIT_ELEMENT, BROWSER_HOVER_ELEMENT, BROWSER_CLICK_ELEMENT, 
                                                          BROWSER_WAIT_CLICK_ELEMENT,BROWSER_SWITCH_TO_FRAME, BROWSER_CLEAR_TEXT_ELEMENT,
                                                          BROWSER_SWITCH_TO_FRAME, BROWSER_DOUBLE_CLICK_ELEMENT,
                                                          BROWSER_WAIT_VISIBLE_ELEMENT, BROWSER_WAIT_VISIBLE_CLICK_ELEMENT,
                                                          BROWSER_WAIT_NOT_VISIBLE_ELEMENT ]:
                if index.column() == COL_NAME:
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")
                    el = "%s %s" % (value,byel.upper())
                        
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append( "%s FROM CACHE" % el )
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append("%s FROM ALIAS" % el )
                    else:
                        actions.append( "%s" % el )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ "%s" % self.mydata[ index.row() ]['text'] ]
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_GET_URL, BROWSER_GET_SOURCE, BROWSER_GET_TEXT_ALERT, BROWSER_GET_TITLE ]:
                if index.column() == COL_NAME:
                    actions = [ "%s AND SAVE IT IN CACHE" % value ]
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( '%s' % self.mydata[ index.row() ]['text-more'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_SELECT_TEXT, BROWSER_SELECT_VALUE ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-cache']:
                        actions.append( "%s FROM CACHE" % value )
                    elif self.mydata[ index.row() ]["parameters"]['from-alias']:
                        actions.append( "%s FROM ALIAS" % value )
                    else:
                        actions.append( "%s" % value )  
                        
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")

                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append("IN HTML ELEMENT %s FROM CACHE" % byel.upper())
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append("IN HTML ELEMENT %s FROM ALIAS" % byel.upper())
                    else:
                        actions.append("IN HTML ELEMENT %s" % byel.upper() )
                        
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % (self.mydata[ index.row() ]['text-more']) )
                    values.append("%s" % self.mydata[ index.row() ]['text'])
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_TYPE_KEY ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-cache']:
                        actions.append( "%s FROM CACHE" % value )
                    elif self.mydata[ index.row() ]["parameters"]['from-alias']:
                        actions.append( "%s FROM ALIAS" % value )
                    else:
                        actions.append( "%s" % value )  
                        
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")

                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append("IN HTML ELEMENT %s FROM CACHE" % byel.upper())
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append("IN HTML ELEMENT %s FROM ALIAS" % byel.upper())
                    else:
                        actions.append("IN HTML ELEMENT %s" % byel.upper() )
                        
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    if ";" in self.mydata[ index.row() ]['text-more']:
                        keyStr, repeatStr = self.mydata[ index.row() ]['text-more'].split(";")
                    else:
                        keyStr = self.mydata[ index.row() ]['text-more']
                        repeatStr = "0"
                    if repeatStr == "0":
                        values.append( "%s" % keyStr )
                    else:
                        values.append( "%s x %s" % (int(repeatStr)+1, keyStr) )
                    values.append("%s" % self.mydata[ index.row() ]['text'])
                    return q( "\n".join(values) )

            elif self.mydata[ index.row() ]['action'] in [ BROWSER_TYPE_TEXT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-cache']:
                        actions.append("TYPE TEXT FROM CACHE")
                    elif self.mydata[ index.row() ]["parameters"]['from-alias']:
                        actions.append("TYPE TEXT FROM ALIAS")
                    else:
                        actions.append("TYPE TEXT")
                        
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")

                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append( "IN HTML ELEMENT %s FROM CACHE" % byel.upper())
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append( "IN HTML ELEMENT %s FROM ALIAS" % byel.upper())
                    else:
                        actions.append( "IN HTML ELEMENT %s" % byel.upper() )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % (self.mydata[ index.row() ]['text-more']) )
                    values.append("%s" % self.mydata[ index.row() ]['text'])
                    return q( "\n".join(values) )

            elif self.mydata[ index.row() ]['action'] in [ BROWSER_EXECUTE_JS ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-cache']:
                        actions.append("EXECUTE JAVASCRIPT FROM CACHE")
                    elif self.mydata[ index.row() ]["parameters"]['from-alias']:
                        actions.append("EXECUTE JAVASCRIPT FROM ALIAS")
                    else:
                        actions.append("EXECUTE JAVASCRIPT")
                        
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")

                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append( "IN HTML ELEMENT %s FROM CACHE" % byel.upper())
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append( "IN HTML ELEMENT %s FROM ALIAS" % byel.upper())
                    else:
                        actions.append( "IN HTML ELEMENT %s" % byel.upper() )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % (self.mydata[ index.row() ]['text-more']) )
                    values.append("%s" % self.mydata[ index.row() ]['text'])
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_FIND_TEXT_ELEMENT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-cache']:
                        actions.append("FIND TEXT FROM CACHE")
                    elif self.mydata[ index.row() ]["parameters"]['from-alias']:
                        actions.append("FIND TEXT FROM ALIAS")
                    else:
                        actions.append("FIND TEXT")
                        
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")

                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append("IN HTML ELEMENT %s FROM CACHE" % byel.upper())
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append("IN HTML ELEMENT %s FROM ALIAS" % byel.upper())
                    else:
                        actions.append("IN HTML ELEMENT %s" % byel.upper() )
                            
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % (self.mydata[ index.row() ]['text-more']) )
                    values.append( "%s" % self.mydata[ index.row() ]['text'])
                    return q( "\n".join(values) )
            
            elif self.mydata[ index.row() ]['action'] in [ BROWSER_GET_TEXT_ELEMENT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    byel = self.mydata[ index.row() ]['misc'].lower()
                    byel = byel.replace("by", "with")
                    el = "%s %s" % (value,byel.upper())
                    
                    if self.mydata[ index.row() ]["parameters"]['from-el-cache']:
                        actions.append( "%s FROM CACHE" % el)
                    elif self.mydata[ index.row() ]["parameters"]['from-el-alias']:
                        actions.append( "%s FROM ALIAS" % el)
                    else:
                        actions.append( "%s" % el)
                        
                    if self.mydata[ index.row() ]['parameters']['to-cache']:
                        actions.append( "AND SAVE IT IN CACHE")
                            
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['text'] )
                    values.append( '%s' % self.mydata[ index.row() ]['text-more'] )
                    return q( "\n".join(values) )
                    
            # display frameworks actions
            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_INFO, FRAMEWORK_WARNING ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['text'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_CACHE_SET ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                        
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("IN CACHE WITH KEY" )
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("IN CACHE WITH ALIAS" )
                    else:
                        actions.append("IN CACHE WITH KEY")
                        
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append("%s" % self.mydata[ index.row() ]['parameters']['value'] )
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['key'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_CACHE_RESET ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ]
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    return q( "\n".join(values) )

            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_USERCODE ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ]
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "........." )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_WAIT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append("%s" % value )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_CHECK_STRING ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s FROM CACHE" % value )
                    
                    op = self.mydata[ index.row() ]['parameters']['operator'].upper()
                    if op == "ANY": op = "CONTAINS ANY"
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % op )
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % op )
                    else:
                        actions.append("%s" % op )
                            
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['key'] )
                    
                    if len( "%s" % self.mydata[ index.row() ]['parameters']['value']) > 50:
                        values.append("%s ..." % ( "%s" % self.mydata[ index.row() ]['parameters']['value'][:50]) )
                    else:
                        values.append("%s" % (self.mydata[ index.row() ]['parameters']['value']) )
                    
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ FRAMEWORK_INTERACT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("USER INPUT PROMPT FROM CACHE" )
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("USER INPUT PROMPT FROM ALIAS" )
                    else:
                        actions.append("USER INPUT PROMPT" )
                        
                    actions.append("AND SAVE IT IN CACHE")
                    
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append("%s" % self.mydata[ index.row() ]['parameters']['value'] )
                    values.append("%s" % self.mydata[ index.row() ]['parameters']['key'] )
                    return q( "\n".join(values) )
                    
            # display system actions
            elif self.mydata[ index.row() ]['action'] in [ SYSTEM_SESSION ]:
                if index.column() == COL_NAME:
                    actions = [ ]

                    if self.mydata[ index.row() ]['parameters']['from-cache-ip']:
                        actions.append( "%s ON HOST FROM CACHE" % value )
                    elif self.mydata[ index.row() ]['parameters']['from-alias-ip']:
                        actions.append( "%s ON HOST WITH ALIAS" % value)
                    else:
                        actions.append("%s ON HOST" % value)
                            
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append("%s" % self.mydata[ index.row() ]['parameters']['dest-ip'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ SYSTEM_CLOSE, SYSTEM_CLEAR_SCREEN ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ SYSTEM_TEXT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]["parameters"]['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]["parameters"]['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        return q("%s" % value)   
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    if len(self.mydata[ index.row() ]['parameters']['text']) > 40 :
                        values.append("%s..." % ( self.mydata[ index.row() ]['parameters']['text'][:40] ) )
                    else:
                        values.append( "%s" % ( self.mydata[ index.row() ]['parameters']['text'] ) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ SYSTEM_SHORTCUT ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ]
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append("%s" % ( self.mydata[ index.row() ]['parameters']['shortcut'] ) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ SYSTEM_CHECK_SCREEN ]:
                if index.column() == COL_NAME:
                    actions = [ ]

                    op = self.mydata[ index.row() ]['parameters']['operator'].upper()
                    if op == "ANY": op = "CONTAINS ANY"
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s %s FROM CACHE" % (value,op) )
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s %s FROM ALIAS" % (value,op) )
                    else:
                        actions.append("%s %s" % (value,op) )
                            
                    if self.mydata[ index.row() ]['parameters']['to-cache']:
                        actions.append("AND SAVE IT IN CACHE WITH KEY"  )

                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    if len( "%s" % self.mydata[ index.row() ]['parameters']['value']) > 50:
                        values.append("%s ..." % ( "%s" % self.mydata[ index.row() ]['parameters']['value'][:50]) )
                    else:
                        values.append("%s" % (self.mydata[ index.row() ]['parameters']['value']) )
                    values.append("%s" % (self.mydata[ index.row() ]['parameters']['cache-key']) )
                    return q( "\n".join(values) )
             
            # display android actions
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_WAKEUP_UNLOCK, ANDROID_WAKUP, ANDROID_UNLOCK, ANDROID_REBOOT, ANDROID_SLEEP,
                                                            ANDROID_FREEZE_ROTATION, ANDROID_UNFREEZE_ROTATION, ANDROID_BOOTLOADER, ANDROID_RECOVERY,
                                                            ANDROID_NOTIFICATION, ANDROID_SETTINGS, ANDROID_DEVICEINFO, ANDROID_GET_LOGS, ANDROID_CLEAR_LOGS,
                                                          ANDROID_LOCK, ANDROID_SLEEP_LOCK ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_TYPE_SHORTCUT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s%s" % (self.mydata[ index.row() ]['misc'], self.mydata[ index.row() ]['text']) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_TYPE_KEYCODE ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s%s" % (self.mydata[ index.row() ]['misc'], self.mydata[ index.row() ]['text']) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_COMMAND ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['cmd'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_SHELL ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['sh'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_STOP_APP, ANDROID_RESET_APP ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['pkg'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_CLEAR_ELEMENT, ANDROID_CLICK_ELEMENT, ANDROID_LONG_CLICK_ELEMENT, ANDROID_EXIST_ELEMENT,
                                                            ANDROID_WAIT_ELEMENT, ANDROID_DRAG_ELEMENT, ANDROID_WAIT_CLICK_ELEMENT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)  
                    if self.mydata[ index.row() ]['parameters']['from-el-cache']:
                        actions.append( "WITH TEXT XML VALUE FROM CACHE" )
                    elif self.mydata[ index.row() ]['parameters']['from-el-alias']:
                        actions.append( "WITH TEXT XML VALUE FROM ALIAS" )
                    # else:
                        # actions.append( "" )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    descr = []
                    uiid = []
                    if 'text' in self.mydata[ index.row() ]['parameters']:
                        if self.mydata[ index.row() ]['parameters']['from-el-cache'] or self.mydata[ index.row() ]['parameters']['from-el-alias']:
                            pass # ignore
                        else:
                            if len(self.mydata[ index.row() ]['parameters']['text']):
                                uiid.append( "text=%s" % self.mydata[ index.row() ]['parameters']['text'] )
                    if 'description' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['description']):
                            uiid.append( "description=%s" % self.mydata[ index.row() ]['parameters']['description'] )
                    if 'class' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['class']):
                            uiid.append( "class=%s" % self.mydata[ index.row() ]['parameters']['class'] )
                    if 'ressource' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['ressource']):
                            uiid.append( "ressource=%s" % self.mydata[ index.row() ]['parameters']['ressource'] )
                    if 'package' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['package']):
                            uiid.append( "package=%s" % self.mydata[ index.row() ]['parameters']['package'] ) 
                    descr.append( ", ".join( uiid ) )
                        
                    values.append( "\n".join( descr ) )
                    
                    if self.mydata[ index.row() ]['parameters']['from-el-cache'] or self.mydata[ index.row() ]['parameters']['from-el-alias']:
                        values.append( "%s" % self.mydata[ index.row() ]['parameters']['text'] )

                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_TYPE_TEXT_ELEMENT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("TYPE TEXT FROM CACHE" )
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("TYPE TEXT WITH ALIAS" )
                    else:
                        actions.append("TYPE TEXT" )
                    
                    actions.append("ON XML ELEMENT" )
                    
                    if self.mydata[ index.row() ]['parameters']['from-el-cache']:
                        actions.append( "WITH TEXT XML VALUE FROM CACHE" )
                    elif self.mydata[ index.row() ]['parameters']['from-el-alias']:
                        actions.append( "WITH TEXT XML VALUE FROM ALIAS" )
                    # else:
                        # actions.append( "" )
                 
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    descr = []
                    uiid = []
                    
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['new-text'] )
                     
                     
                    if 'text' in self.mydata[ index.row() ]['parameters']:
                        if self.mydata[ index.row() ]['parameters']['from-el-cache'] or self.mydata[ index.row() ]['parameters']['from-el-alias']:
                            pass # ignore
                        else:
                            if len(self.mydata[ index.row() ]['parameters']['text']):
                                uiid.append( "text=%s" % self.mydata[ index.row() ]['parameters']['text'] )
                    if 'description' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['description']):
                            uiid.append( "description=%s" % self.mydata[ index.row() ]['parameters']['description'] )
                    if 'class' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['class']):
                            uiid.append( "class=%s" % self.mydata[ index.row() ]['parameters']['class'] )
                    if 'ressource' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['ressource']):
                            uiid.append( "ressource=%s" % self.mydata[ index.row() ]['parameters']['ressource'] )
                    if 'package' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['package']):
                            uiid.append( "package=%s" % self.mydata[ index.row() ]['parameters']['package'] ) 
                    descr.append( ", ".join( uiid ) )
                        
                    values.append( "\n".join( descr ) )
                    
                    if self.mydata[ index.row() ]['parameters']['from-el-cache'] or self.mydata[ index.row() ]['parameters']['from-el-alias']:
                        values.append( "%s" % self.mydata[ index.row() ]['parameters']['text'] )
                        
                    return q( "\n".join(values) )
            
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_GET_TEXT_ELEMENT ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append( "%s" % value)
                    
                    if self.mydata[ index.row() ]['parameters']['from-el-cache']:
                        actions.append( "WITH TEXT XML VALUE FROM CACHE" )
                    elif self.mydata[ index.row() ]['parameters']['from-el-alias']:
                        actions.append( "WITH TEXT XML VALUE FROM ALIAS" )
                    else:
                        pass

                    if self.mydata[ index.row() ]['parameters']['to-cache']:
                        actions.append("AND SAVE IT IN CACHE "  )
                    else:
                        actions.append("")
                            
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    
                    descr = []
                    uiid = []
                    if 'text' in self.mydata[ index.row() ]['parameters']:
                        if self.mydata[ index.row() ]['parameters']['from-el-cache'] or self.mydata[ index.row() ]['parameters']['from-el-alias']:
                            pass # ignore
                        else:
                            if len(self.mydata[ index.row() ]['parameters']['text']):
                                uiid.append( "text=%s" % self.mydata[ index.row() ]['parameters']['text'] )
                    if 'description' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['description']):
                            uiid.append( "description=%s" % self.mydata[ index.row() ]['parameters']['description'] )
                    if 'class' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['class']):
                            uiid.append( "class=%s" % self.mydata[ index.row() ]['parameters']['class'] )
                    if 'ressource' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['ressource']):
                            uiid.append( "ressource=%s" % self.mydata[ index.row() ]['parameters']['ressource'] )
                    if 'package' in self.mydata[ index.row() ]['parameters']:
                        if len(self.mydata[ index.row() ]['parameters']['package']):
                            uiid.append( "package=%s" % self.mydata[ index.row() ]['parameters']['package'] ) 
                    descr.append( ", ".join( uiid ) )

                    values.append( "\n".join( descr ) )
                    
                    if self.mydata[ index.row() ]['parameters']['from-el-cache'] or self.mydata[ index.row() ]['parameters']['from-el-alias']:
                        values.append( "%s" % self.mydata[ index.row() ]['parameters']['text'] )
                        
                    values.append( "%s" % self.mydata[ index.row() ]['parameters']['cache-key'] )
                    
                    return q( "\n".join(values) )
            
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_CLICK_POSITION ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    
                    descr = []
                    if len(self.mydata[ index.row() ]['parameters']['x']) and len(self.mydata[ index.row() ]['parameters']['y']):
                        descr.append( "x=%s, y=%s" % (self.mydata[ index.row() ]['parameters']['x'], 
                                                            self.mydata[ index.row() ]['parameters']['y']) ) 
                    values.append( "\n".join( descr ) )
                        
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_DRAG_POSITION ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    actions.append("TO POSITION ")
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]

                    if len(self.mydata[ index.row() ]['parameters']['start-x']) and len(self.mydata[ index.row() ]['parameters']['start-y']):
                        values.append("x=%s, y=%s" % (   self.mydata[ index.row() ]['parameters']['start-x'], 
                                                    self.mydata[ index.row() ]['parameters']['start-y']) ) 
                    else:
                        values.append( "x=, y=" )
                        
                    if len(self.mydata[ index.row() ]['parameters']['stop-x']) and len(self.mydata[ index.row() ]['parameters']['stop-y']):
                        values.append( "x=%s, y=%s" % (self.mydata[ index.row() ]['parameters']['stop-x'], 
                                                      self.mydata[ index.row() ]['parameters']['stop-y']) ) 
                    else:
                        values.append("x=, y=")
                        
                    # values.append("x=%s, y=%s" % (self.mydata[ index.row() ]['parameters']['x'], self.mydata[ index.row() ]['parameters']['y']))

                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ ANDROID_SWIPE_POSITION ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    actions.append("%s" % value)
                    actions.append("TO POSITION")
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]

                    if len(self.mydata[ index.row() ]['parameters']['start-x']) and len(self.mydata[ index.row() ]['parameters']['start-y']):
                        values.append("x=%s, y=%s" % (   self.mydata[ index.row() ]['parameters']['start-x'], 
                                                    self.mydata[ index.row() ]['parameters']['start-y']) ) 
                    else:
                        values.append("x=, y=" )
                        
                    if len(self.mydata[ index.row() ]['parameters']['stop-x']) and len(self.mydata[ index.row() ]['parameters']['stop-y']):
                        values.append( "x=%s, y=%s" % (self.mydata[ index.row() ]['parameters']['stop-x'], 
                                                      self.mydata[ index.row() ]['parameters']['stop-y']) ) 
                    else:
                        values.append( "x=, y=")
                        
                    return q( "\n".join(values) )
                    
            # display app actions
            if self.mydata[ index.row() ]['action'] in [ CLICK_WORD, DOUBLE_CLICK_WORD, RIGHT_CLICK_WORD, WAIT_WORD, WAIT_CLICK_WORD ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                        
                    actions.append("IN AREA")
                    
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % ( self.mydata[ index.row() ]['parameters']['location-word'] ) )
                    values.append("x=%s, y=%s, w=%s, h=%s" % (
                                            self.mydata[ index.row() ]['parameters']['location-x'],
                                            self.mydata[ index.row() ]['parameters']['location-y'],
                                            self.mydata[ index.row() ]['parameters']['location-w'],
                                            self.mydata[ index.row() ]['parameters']['location-h'],
                                        ) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ MOUSE_CLICK_POSITION, MOUSE_DOUBLE_CLICK_POSITION, MOUSE_RIGHT_CLICK_POSITION, MOUSE_MOVE_POSITION ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ] 
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "x=%s, y=%s" % (self.mydata[ index.row() ]['text'], self.mydata[ index.row() ]['misc']) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ GET_TEXT_CLIPBOARD ]:
                if index.column() == COL_NAME:
                    actions = [ "%s AND SAVE IT IN CACHE" % value ]
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "%s" % self.mydata[ index.row() ]['text'] )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ MOUSE_WHEEL_UP, MOUSE_WHEEL_DOWN ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ] 
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    values.append( "scroll=%s" % value )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ TYPE_TEXT, TYPE_TEXT_PATH ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ "%s" % value ]
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ TYPE_PASSWORD ]:
                if index.column() == COL_NAME:
                    actions = [ ]
                    if self.mydata[ index.row() ]['parameters']['from-cache']:
                        actions.append("%s FROM CACHE" % value)
                    elif self.mydata[ index.row() ]['parameters']['from-alias']:
                        actions.append("%s FROM ALIAS" % value)
                    else:
                        actions.append("%s" % value)
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    if self.mydata[ index.row() ]['from-cache'] or self.mydata[ index.row() ]['from-alias']:
                        values.append( "%s" % value )
                    else:
                        values.append( "*******" )
                
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ SHORTCUT ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value ] 
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    if 'option-similar' in self.mydata[ index.row() ]:
                        repeat = self.mydata[ index.row() ]['option-similar']
                        if str(repeat) == '0.7' or str(repeat) == '0':
                            values.append( "%s%s" % (self.mydata[ index.row() ]['misc'], self.mydata[ index.row() ]['text']) )
                        else:
                            values.append( "%s x (%s%s)" % ( int(repeat)+1, self.mydata[ index.row() ]['misc'], self.mydata[ index.row() ]['text']) )
                    else:
                        values.append( "%s%s" % (self.mydata[ index.row() ]['misc'], self.mydata[ index.row() ]['text']) )
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ CLICK_IMAGE, DOUBLE_CLICK_IMAGE, RIGHT_CLICK_IMAGE, WAIT_IMAGE, WAIT_CLICK_IMAGE, HOVER_IMAGE ]:
                if index.column() == COL_NAME:
                    actions = [ "%s" % value  ]
                    actions.append("WITH SIMILARITY OF %s%%" % (float(self.mydata[ index.row() ]['option-similar'])*100) )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    return q( "\n".join(values) )
                    
            elif self.mydata[ index.row() ]['action'] in [ DRAG_DROP_IMAGE ]:
                if index.column() == COL_NAME:
                    actions = [ "DRAG IMAGE"  ]
                    actions.append("WITH SIMILARITY OF %s%%" % (float(self.mydata[ index.row() ]['option-similar'])*100) )
                    actions.append( "AND DROP TO x=%s, y=%s" % (self.mydata[ index.row() ]['misc'], self.mydata[ index.row() ]['text']) )
                    return q( "\n".join(actions) )
                elif index.column() == COL_VALUE: 
                    values = [ ]
                    return q( "\n".join(values) )
                    
            else:            
                pass

        # on edit
        elif role == Qt.EditRole:
            return q(value)

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
            self.mydata[ index.row() ]['action'] = value

        elif index.column() == COL_VALUE:
            if self.mydata[ index.row() ]['misc'] == FRAMEWORK_WAIT:
                self.mydata[ index.row() ]['misc'] = value

            else:
                self.mydata[ index.row() ]['image'] = value

        elif index.column() == COL_DESCRIPTION:
            self.mydata[ index.row() ]['description'] = unicode(value).replace('"', '')

        else:
            pass

        self.owner.setData()

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

        if index.column() in [ COL_ID, COL_NAME, COL_VALUE ] :
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        else:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)| Qt.ItemIsEditable| Qt.ItemIsDragEnabled)

class EnableDelegate(QItemDelegate, Logger.ClassLogger):
    """
    Checkbox active delegate
    """
    def __init__(self, owner):
        """
        Checkbox delegate

        @param value: 
        @type value:
        """
        QItemDelegate.__init__(self, owner)
 
    def paint(self, painter, option, index):
        """
        Paint

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        # Get item data
        if sys.version_info > (3,):
            value = index.data(Qt.DisplayRole)
            if isinstance(value, str): value = QtHelper.str2bool(value)
        else:
            value = index.data(Qt.DisplayRole).toBool()

        # fill style options with item data
        style = QApplication.style()
        opt = QStyleOptionButton()
        opt.state |= QStyle.State_On if value else QStyle.State_Off
        opt.state |= QStyle.State_Enabled
        opt.text = ""
        opt.rect = option.rect

        # draw item data as CheckBox
        style.drawControl(QStyle.CE_CheckBox, opt, painter)
 
    def createEditor(self, parent, option, index):
        """
        Create the editor

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        # create check box as our editor.
        editor = QCheckBox(parent)
        editor.installEventFilter(self)
        
        return editor
 
    def setEditorData(self, editor, index):
        """
        Set the editor

        @param value: 
        @type value:

        @param value: 
        @type value:
        """
        # set editor data
        if sys.version_info > (3,):
            value = index.data(Qt.DisplayRole)
            if isinstance(value, str):
                value = QtHelper.str2bool(value)
        else:
            value = index.data(Qt.DisplayRole).toBool()
        editor.setChecked(value)
 
    def setModelData(self, editor, model, index):
        """
        Set the model

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        value = editor.checkState()
        if value == 0:
            value = "False"
        if value == 2:
            value = "True"
        
        model.setData(index, q(value))
 
    def updateEditorGeometry(self, editor, option, index):
        """
        Update the geometry of the editor

        @param value: 
        @type value:

        @param value: 
        @type value:

        @param index: 
        @type index:
        """
        editor.setGeometry(option.rect)
        
class StepsTableView(QTableView, Logger.ClassLogger):
    """
    Parameters table view
    """
    EditStep = pyqtSignal(dict)  
    StepDeleted = pyqtSignal()  
    def __init__(self, parent):
        """
        Contructs ParametersTableView table view

        @param parent: 
        @type parent:
        """
        QTableView.__init__(self, parent)
        self.model = None
        self.stepIdUnique = 0
        self.__mime__ = "application/x-%s-steps" % Settings.instance().readValue( key='Common/acronym' ).lower()

        self.model = StepsTableModel(self)
        
        self.createWidgets()
        self.createActions()
        self.createConnections()

        self.setModel(self.model)

    def getUniqueId(self):
        """
        Return unique id
        """
        self.stepIdUnique += 1
        return self.stepIdUnique

    def createWidgets (self):
        """
        Create qt widgets
        """        
        self.activeAction = EnableDelegate(self)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setShowGrid(False)
        self.setGridStyle (Qt.DotLine)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # self.setItemDelegateForColumn(COL_ENABLE, self.activeAction )

        self.adjustRows()

        appStyle = """
                QTableView::item {
                     border-bottom: 1px dotted  #d9d9d9;
                     padding: 5px;
                }
        """
        self.setStyleSheet(appStyle)
        
        # self.setColumnWidth(COL_ENABLE, 10)    
        self.setColumnWidth(COL_ID, 30)
        self.setColumnWidth(COL_NAME, 400)
        self.setColumnWidth(COL_ICON, 30)
        self.setColumnWidth(COL_DESCRIPTION, 500)

    def createConnections (self):
        """
        Create qt connections
        """
        self.customContextMenuRequested.connect(self.onPopupMenu)
        QApplication.clipboard().dataChanged.connect(self.onClipboardUpdated) 
        QApplication.clipboard().changed.connect(self.onClipboardUpdatedNew)
        self.doubleClicked.connect(self.onDoubleClick)

    def createActions (self):
        """
        Create actions
        """
        self.delAction = QtHelper.createAction(self, self.tr("&Delete\nSelection"), self.removeItem, icon = QIcon(":/test-parameter-del.png"),
                                                tip = self.tr('Delete the selected step'), shortcut='Del' )
        self.copyAction = QtHelper.createAction(self, self.tr("Copy"), self.copyItem, icon = QIcon(":/test-parameter-copy.png"), 
                                                tip = self.tr('Copy the selected step'), shortcut='Ctrl+C' )
        self.pasteAction = QtHelper.createAction(self, self.tr("Paste"), self.pasteItem, icon = QIcon(":/test-parameter-paste.png"),
                                                tip = self.tr('Paste step'), shortcut='Ctrl+V' )
        self.upAction = QtHelper.createAction(self, self.tr("Move\nUp"), self.moveUpItem, icon = QIcon(":/test-parameter-up.png"),
                                                tip='Move Up')
        self.downAction = QtHelper.createAction(self, self.tr("Move\nDown"), self.moveDownItem, icon = QIcon(":/test-parameter-down.png"),
                                                tip='Move Down' )

        self.enableAction = QtHelper.createAction(self, self.tr("&Enable"), self.enableItem, icon = QIcon(":/check.png"),
                                                tip='Enable action(s)')   
        self.disableAction = QtHelper.createAction(self, self.tr("&Disable"), self.disableItem, icon = QIcon(":/uncheck.png"),
                                                tip='Disable action(s)')    
        
        self.editAction = QtHelper.createAction(self, self.tr("&Edit\nAction"), self.editItem, icon = QIcon(":/writing-state.png"),
                                                tip='Edit action')  

        # set default values
        self.defaultActions()

    def defaultActions(self):
        """
        Set default actions
        """
        self.delAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.pasteAction.setEnabled(False)
        self.upAction.setEnabled(False)
        self.downAction.setEnabled(False)
        
        self.enableAction.setEnabled(False)
        self.disableAction.setEnabled(False)
        
        self.editAction.setEnabled(False)

    def onDoubleClick(self, index):
        """
        Edit item on double click
        """
        if index.column() in [ COL_NAME ]:

            self.editItem()
            
            # new in v15
            self.setEnabled(False)
            
    def editItem(self):
        """
        Edit item
        """
        selectedRow = self.selectionModel().selectedRows()
        if not selectedRow:
            return
        
        data = self.model.getData()
        self.EditStep.emit( data[selectedRow[0].row()] )
        
    def enableItem(self):
        """
        Enable item
        """
        selectedRow = self.selectionModel().selectedRows()
        if not selectedRow:
            return
        
        for index in selectedRow:
            data = self.model.getData()
            data[index.row()]['active'] = "True"

        self.model.beginResetModel() 
        self.model.endResetModel() 
        
        self.adjustColumns()
        self.adjustRows()
        
    def disableItem(self):
        """
        Disable item
        """
        selectedRow = self.selectionModel().selectedRows()
        if not selectedRow:
            return
        
        for index in selectedRow:    
            data = self.model.getData()
            data[index.row()]['active'] = "False"

        self.model.beginResetModel() 
        self.model.endResetModel() 
        
        self.adjustColumns()
        self.adjustRows()
        
    def onPopupMenu(self, pos):
        """
        Display menu on right click

        @param pos: 
        @type pos:
        """
        self.menu = QMenu(self)
        index = self.currentIndex()
        indexes = self.selectedIndexes()
        if indexes:
            self.menu.addAction( self.delAction )
            self.menu.addSeparator()
            self.menu.addAction( self.copyAction )
            self.menu.addAction( self.pasteAction )
            self.menu.addSeparator()
            self.menu.addAction( self.upAction )
            self.menu.addAction( self.downAction )
            self.menu.addSeparator()
            self.menu.addAction( self.enableAction )
            self.menu.addAction( self.disableAction )
            self.menu.addSeparator()
            self.menu.addAction( self.editAction )
            self.menu.addSeparator()
            
        self.menu.popup( self.mapToGlobal(pos) )

    def selectionChanged(self, selected, deselected):
        """
        selection changed
        """
        QTableView.selectionChanged(self, selected, deselected)

        indexes = self.selectedIndexes()
        if not indexes:
            self.delAction.setEnabled(False)
            self.editAction.setEnabled(False)
            return

        
        self.delAction.setEnabled(True)
        self.copyAction.setEnabled(True)
        data = self.model.getData()
        if len(data) >= 1:
            self.upAction.setEnabled(True)
            self.downAction.setEnabled(True)
            self.editAction.setEnabled(True)

            self.enableAction.setEnabled(True)
            self.disableAction.setEnabled(True)

    def onClipboardUpdatedNew(self, mode):
        """
        On clipboard updated
        """
        self.trace( 'New Steps - clipboard updated' )
        c = QApplication.clipboard()
        formatsList = c.mimeData().formats() 
        if sys.version_info > (3,):
            self.trace( 'New - Steps > something in the clipboard: %s' % (",").join(formatsList) )
        else:
            self.trace( 'New - Steps > something in the clipboard: %s' % formatsList.join(",") ) # formatsList = QStringList
        
    def onClipboardUpdated(self):
        """
        On clipboard updated
        """
        self.trace( 'clipboard updated for steps' )
        c = QApplication.clipboard()
        formatsList = c.mimeData().formats() 
        if sys.version_info > (3,):
            self.trace('Steps > something in the clipboard: %s' % ",".join(formatsList) )
        else:
            self.trace('Steps > something in the clipboard: %s' % formatsList.join(",") ) # formatsList = QStringList
        
        if c.mimeData().hasFormat(self.__mime__):
            self.trace('Steps > clipboard: its for me' )
            self.pasteAction.setEnabled(True)
        else:
            self.trace('Steps > clipboard: not for me' )
            self.pasteAction.setEnabled(False)

    def moveUpItem(self):
        """
        Move up item
        """
        self.moveItem(direction=MOVE_DOWN)

    def moveDownItem(self):
        """
        Move down item
        """
        self.moveItem(direction=MOVE_UP)

    def moveItem(self, direction):
        """
        Move item up or down
        """
        selectedRow = self.selectionModel().selectedRows()
        if not selectedRow:
            return

        index = selectedRow[0]
        data = self.model.getData()
        dataRow = data.pop(index.row())

        data.insert(index.row()+direction, dataRow)

        self.model.beginResetModel() 
        self.model.endResetModel() 

        self.selectRow(index.row()+direction)

    def pasteItem(self):
        """
        Paste item
        """
        itemsPasted = []
        
        self.trace('Steps > Starting to paste, read from clipboard')
        # read from clipboard
        mimeData = QApplication.clipboard().mimeData()
        if not mimeData.hasFormat(self.__mime__):
            return None
        
        self.trace('Steps > Unpickle data')
        data = mimeData.data(self.__mime__)
        if not data:
            return None
        try:
            steps = pickle.loads(data.data())
            for stp in steps:
                stepAct = ACTION_ANYTHING
                if 'action-type' in stp: stepAct = stp['action-type']
                textMore = ''
                if 'text-more' in stp: textMore = stp['text-more']
                fromCache=False
                if 'from-cache' in stp: fromCache = stp['from-cache']
                fromAlias=False
                if 'from-alias' in stp: fromAlias = stp['from-alias']
                optionSimilar = 0.7
                if 'option-similar' in stp: optionSimilar = stp['option-similar']
                parameters = {}     
                if 'parameters' in stp: parameters = stp['parameters']
                self.addStep(actionName=stp['action'], imagePixmap=stp['image'], textStr=stp['text'],
                                miscStr=stp['misc'], descriptionStr=stp['description'], actionType=stepAct,
                                textMoreStr=textMore, expectedStr=stp['expected'], fromCache=fromCache,
                                optionSimilar=optionSimilar, parameters=parameters, fromAlias=fromAlias)

        except Exception as e:
            self.error( "unable to deserialize step %s" % str(e) )
            return None
        
    def copyItem(self):
        """
        Copy the selected row to the clipboard
        """
        # retrieve data from model      
        rowData = []

        selected = self.selectionModel().selectedRows()
        if not selected:
            return

        for index in selected:
            rowData.append(self.model.getData()[index.row()])

        if rowData:
            self.trace('Test Param > Picke data: %s' % rowData )
            # pickle data
            mime = QMimeData()
            mime.setData( self.__mime__ , QByteArray(pickle.dumps(rowData)) )
            
            self.trace('Steps to copy> Copying to clipboard')
            # copy to clipboard
            QApplication.clipboard().setMimeData(mime,QClipboard.Clipboard)
            self.trace('Steps to copy > Coppied to clipboard')
            self.pasteAction.setEnabled(True)

    def removeItem(self):
        """
        Removes the selected row 
        """
        # get selected proxy indexes
        indexes = self.selectedIndexes()
        if not indexes:
            return
 
        if indexes:
            answer = QMessageBox.question(self,  self.tr("Remove"),  
                                        self.tr("Do you want to remove selected step?"), 
                                        QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                self.StepDeleted.emit()
                self.removeValues(indexes)
        
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
        allStepsId = []

        # remove duplicate index
        cleanIndexes = {}
        for index in indexes:
            if index.row() not in cleanIndexes:
                cleanIndexes[index.row()] = index
        
        for cleanIndex in list(cleanIndexes.keys()): # for python3 support
            allStepsId.append( datas[cleanIndex]['id'] )

        self.trace('Step to remove: %s' % allStepsId)
        for stepId in allStepsId:
            self.removeValue( stepId=stepId )
        self.setData( signal = True )

    def removeValue(self, stepId):
        """
        Remove one step according to the name passed on argument
        """
        datas = self.model.getData()
        i = None
        for i in xrange(len(datas)):
            if datas[i]['id'] == stepId:
                break
        if i is not None:
            step = datas.pop( i )
            del step

        self.model.beginResetModel() 
        self.model.endResetModel() 
        
        self.delAction.setEnabled(False)

        data = self.model.getData()
        if not len(data):
            self.copyAction.setEnabled(False)
            self.upAction.setEnabled(False)
            self.downAction.setEnabled(False)

    def clear (self):
        """
        clear contents
        """
        self.copyAction.setEnabled(False)
        self.upAction.setEnabled(False)
        self.downAction.setEnabled(False)
        self.delAction.setEnabled(False)
        self.model.setDataModel( [] )

    def getData(self):
        """
        Return data of the model
        """
        return self.model.getData()

    def addStep(self, actionName, imagePixmap, textStr, miscStr, descriptionStr, textMoreStr='', fromCache=False,
                    actionType=ACTION_ANYTHING, updateMode=False, stepId=0, expectedStr='Action executed with success',
                    optionSimilar=0.7, parameters={}, fromAlias=False, bold=False ):
        """
        Add step
        """
        if sys.version_info > (3,):
            if isinstance(imagePixmap, bytes):
                imagePixmap = str(imagePixmap, 'utf8')
        if updateMode:
            tpl =   {   'id': stepId ,  'action': actionName, 'image': imagePixmap, 'text': textStr, 
                        'misc': miscStr, 'text-more': textMoreStr,  'description': descriptionStr, 'active': True,
                        'action-type': actionType, 'expected': expectedStr, 'from-cache': fromCache,
                        'option-similar':  optionSimilar, 'parameters': parameters, 'from-alias': fromAlias, 
                        'bold': bold }
            data = self.model.getData()
            if len(data):
                i = None
                for i in xrange(len(data)):
                    if data[i]['id'] == stepId:
                        break
                if i is not None:
                    data[i] = tpl
        else:
            index = self.currentIndex()
            if not index.isValid():
                row = self.model.rowCount()
            else:
                row = index.row()

            tpl =   {   'id': self.getUniqueId() ,  'action': actionName, 'image': imagePixmap, 'text': textStr, 
                        'misc': miscStr, 'text-more': textMoreStr,  'description': descriptionStr, 'active': True,
                        'action-type': actionType, 'expected': expectedStr, 'from-cache': fromCache, 
                        'option-similar':  optionSimilar, 'parameters': parameters, 'from-alias': fromAlias, 
                        'bold': bold }
        
            data = self.model.getData()
            data.insert(row + 1, tpl)

        self.model.beginResetModel() 
        self.model.endResetModel() 
        self.setData()

    def setUnboldAll(self):
        """
        Set unbold all actions
        """
        data = self.model.getData()
        for d in data:
            if "bold" not in d:
                d.update( {'bold': False } )
            else:
                d['bold'] = False
                
        self.model.beginResetModel() 
        self.model.endResetModel() 
        self.setData()
   
    def setBoldAnything(self):
        """
        Set bold for anything actions
        """
        data = self.model.getData()
        for d in data:
            if 'action-type' not in d:
                d.update( {'action-type': ACTION_ANYTHING} )
                
            if d['action-type'] == ACTION_ANYTHING:
                d.update( {'bold': True } )
                
        self.model.beginResetModel() 
        self.model.endResetModel() 
        self.setData()
   
    def setBoldBrowser(self):
        """
        Set bold function for browser actions
        """
        data = self.model.getData()
        for d in data:
            if 'action-type' not in d:
                d.update( {'action-type': ACTION_ANYTHING} )
                
            if d['action-type'] == ACTION_BROWSER:
                d.update( {'bold': True } )
                
        self.model.beginResetModel() 
        self.model.endResetModel() 
        self.setData()
        
    def setBoldAndroid(self):
        """
        Set bold android actions
        """
        data = self.model.getData()
        for d in data:
            if 'action-type' not in d:
                d.update( {'action-type': ACTION_ANYTHING} )
                
            if d['action-type'] == ACTION_ANDROID:
                d.update( {'bold': True } )
                
        self.model.beginResetModel() 
        self.model.endResetModel() 
        self.setData()
        
    def setData(self, signal = True):
        """
        Set table data

        @param signal: 
        @type signal: boolean
        """
        self.setVisible(False)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setVisible(True)
        
        self.setColumnWidth(COL_ID, 30)
        self.setColumnWidth(COL_NAME, 400)
        self.setColumnWidth(COL_ICON, 30)
        self.setColumnWidth(COL_DESCRIPTION, 500)

    def adjustColumns(self):
        """
        Resize two first columns to contents
        """
        for col in [  COL_VALUE ]:
            self.resizeColumnToContents(col)

    def adjustRows (self):
        """
        Resize row to contents
        """
        data = self.model.getData()
        for row in xrange(len(data)):
            self.resizeRowToContents(row)
