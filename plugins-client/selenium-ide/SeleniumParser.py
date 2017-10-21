#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2017 Denis Machard
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
# Gfi Informatique, Inc., hereby disclaims all copyright interest in the
# extensive testing project written by Denis Machard
# 
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

import copy
from html.parser import HTMLParser


class SeleniumIDEParser(HTMLParser):
    def __init__(self):
        """
        """
        HTMLParser.__init__(self)
        self.ide_supported = False
        self.ide_url = ""
        self.ide_actions = []

        self.ide_ready = False
        self.ide_ready_data = False
        
        self.nb_td = 0
        self.cur_act = []
    
    def handle_starttag(self, tag, attrs):
        """
        """
        # checking the head of the html file
        if tag == "head":
            for attrName, attrValue in attrs:
                if attrName == "profile" and "selenium-ide" in attrValue: self.ide_supported=True 

        # extract the link web site        
        if tag == "link":
            for attrName, attrValue in attrs:
                if attrName == "href": self.ide_url = attrValue
        
        if tag == "tbody":
            self.ide_ready = True
            
        if tag == "td" and self.ide_ready:
            self.ide_ready_data = True
            self.nb_td += 1

    def handle_endtag(self, tag):
        """
        """
        if tag == "tbody":
            self.ide_ready = False

        if tag == "td" and self.ide_ready:
            self.ide_ready_data = False
            
            if self.nb_td == 3:
                while len(self.cur_act) < 3:
                    self.cur_act.append( "" )
                self.ide_actions.append( copy.copy(self.cur_act) )
                self.cur_act.clear()
                self.nb_td = 0
            
    def handle_data(self, data):
        """
        """
        if self.ide_ready_data:
            self.cur_act.append( data )
