#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

"""
Fifo module with callback
"""
import sys
import threading
try:
    import Queue
except ImportError:  # support python 3
    import queue as Queue

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class FifoCallbackThread(threading.Thread):
    """
    Fifo with callback and thread
    """

    def __init__(self):
        """
        Construct a fifo callback function thread
        """
        threading.Thread.__init__(self)
        self.queue = Queue.Queue(0)  # FIFO size is infinite
        self.running = True
        self.event = threading.Event()

    def putItem(self, callback):
        """
        Adds callback in the queue

        @param callback:
        @type callback:
        """
        self.queue.put(callback)
        self.event.set()

    def run(self):
        """
        Main loop
        """
        while self.running:
            self.event.wait()
            if self.running:
                while not self.queue.empty():
                    try:
                        callback = self.queue.get(False)
                        callback()
                    except Queue.Empty:
                        self.event.clear()
                    except Exception:
                        pass
                self.event.clear()
        self.event.clear()
        self.onStop()

    def onStop(self):
        """
        On stop
        """
        pass

    def stop(self):
        """
        Stops the thread
        """
        self.running = False
        self.event.set()
