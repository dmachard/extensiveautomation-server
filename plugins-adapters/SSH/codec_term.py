#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestAdapterLib as TestAdapter
import sys

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

import templates_term

import re
import time
import codecs
import binascii

import pyte
import threading

class Observer(threading.Thread):
	"""
	"""
	def __init__(self, parent, cycleSnap=1):
		"""
		"""
		threading.Thread.__init__(self)
		self.parent = parent
		self.watchEvery = cycleSnap
		self.stopEvent = threading.Event()
		self.watching = False
		
	def stop(self):
		"""
		"""
		self.watching = False
		self.stopEvent.set()
		
	def unwatch(self):
		"""
		"""
		self.watching = False
		
	def watch(self):
		"""
		"""
		self.watching = True
		
	def run(self):
		"""
		"""
		while not self.stopEvent.isSet():   
			time.sleep(self.watchEvery)
			if self.watching: self.onWatch()
			
	def onWatch(self):
		"""
		"""
		pass
		
class Codec(object):
	def __init__(self, parent, terminalWidth, terminalHeight, cycleSnap):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info

		self.connected = False

		self.snapshot_screen = ""
		self.obs = Observer(parent=self, cycleSnap=cycleSnap)
		self.obs.onWatch = self.onWatchScreen
		self.obs.start()
		
		self.stream = pyte.ByteStream()
		self.screen = pyte.Screen(terminalWidth, terminalHeight)

		self.stream.attach(self.screen) 

	def reset(self):
		"""
		"""
		self.obs.stop()

	def unwatch(self):
		"""
		"""
		self.screen.reset()
		self.connected=False
		self.obs.unwatch()
		
	def onWatchScreen(self):
		"""
		"""
		current = "%s" % "\n".join(self.screen.display)

		if current != self.snapshot_screen:
			if not self.connected:
				self.connected=True
#				self.handleScreen(screen=("opened", templates_term.term_opened(data=current.strip() )  ))
				self.handleScreen(screen=("opened", templates_term.term_opened(data="success")  ))
				self.handleScreen(screen=("screen", templates_term.term_data(data=current.strip() )  ))
			else:
				self.handleScreen(screen=("screen", templates_term.term_data(data=current.strip() )  ))
			self.snapshot_screen = current

	def handleScreen(self, screen):
		"""
		"""
		pass
		
	def encode(self, ssh_cmd):
		"""
		"""
		evt = ssh_cmd.get('event')
		data = ssh_cmd.get('data')
		return evt.title(), data

	def decode(self, data):
		"""
		"""
		if not self.connected: self.obs.watch()
		self.debug("%s" % data)
		self.stream.feed(data)




