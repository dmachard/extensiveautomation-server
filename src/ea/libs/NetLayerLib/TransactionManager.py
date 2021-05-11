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
Transaction module manager
"""

import sys
import threading
import time

from ea.libs.NetLayerLib import FifoCallBack

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


class TransactionManager(object):
    """
    Transaction manager
    """
    ID_MAX = 99999

    def __init__(self):
        """
        Constructor
        """
        self.__started = False
        self.__fifo_incoming_events_thread = None

        self.__mutex = threading.RLock()
        self.__transactionId = 0
        self.__outgoingTransactions = {}

    def getNewTransactionId(self):
        """
        Return a new transaction id

        @return:
        @rtype:
        """
        self.__mutex.acquire()
        if self.__transactionId == self.ID_MAX:
            self.__transactionId = 0
        self.__transactionId += 1
        ret = self.__transactionId
        self.__mutex.release()
        return ret

    def newTransaction(self, waitResponse=False, client=0):
        """
        Return a new transaction

        @param waitResponse:
        @type waitResponse:

        @param client:
        @type client:

        @return:
        @rtype:
        """
        event = None
        transactionId = self.getNewTransactionId()
        if waitResponse:
            event = threading.Event()
        self.__mutex.acquire()
        transaction = {
            'tid': transactionId,
            'timestamp': time.time(),
            'event': event}
        self.__outgoingTransactions[(client, transactionId)] = transaction
        self.__mutex.release()
        return transactionId, event

    def waitResponse(self, event, transactionId,
                     responseTimeout=30.0, client=0, cancelEvent=None):
        """
        Wait response

        @param event:
        @type event:

        @param transactionId:
        @type transactionId:

        @param responseTimeout:
        @type responseTimeout:

        @param client:
        @type client:

        @return:
        @rtype:
        """
        timeout = False
        startTime = self.__outgoingTransactions[(
            client, transactionId)]['timestamp']
        if cancelEvent is not None:
            while (not event.isSet()) and (
                    not timeout) and (not cancelEvent.isSet()):
                time.sleep(0.1)
                if (time.time() - startTime) >= responseTimeout:
                    timeout = True
        else:
            while (not event.isSet()) and (not timeout):
                time.sleep(0.1)
                if (time.time() - startTime) >= responseTimeout:
                    timeout = True
        if cancelEvent is not None:
            if cancelEvent.isSet():
                self.__mutex.acquire()
                del self.__outgoingTransactions[(client, transactionId)]
                self.__mutex.release()
                self.trace(
                    "request transaction id %s cancelled" %
                    (transactionId))
                return None

        if not timeout:
            self.__mutex.acquire()
            response = self.__outgoingTransactions[(
                client, transactionId)]['response']
            del self.__outgoingTransactions[(client, transactionId)]
            self.__mutex.release()
            return response
        else:
            self.__mutex.acquire()
            del self.__outgoingTransactions[(client, transactionId)]
            self.__mutex.release()
            self.trace(
                "client %s timeout on synchronous request transaction id %s" %
                (client, transactionId))
            return None

    def onMessage(self, message, client=0):
        """
        On message

        @param message:
        @type message:

        @param client:
        @type client:
        """
        typ, mess = message[0], message[1]
        transactionId = int(mess['tid'])
        if typ == 'request':
            self.trace(
                "<-- %s %s from %s" %
                (mess['cmd'], transactionId, client))
            self.__fifo_incoming_events_thread.putItem(
                lambda: self.onRequest(client, transactionId, mess))
        if typ == 'response':
            self.__mutex.acquire()
            if (client, transactionId) in self.__outgoingTransactions:
                entry = self.__outgoingTransactions[(client, transactionId)]
                # synchronous request ?
                if entry['event']:
                    self.__outgoingTransactions[(
                        client, transactionId)]['response'] = mess
                    entry['event'].set()
                else:
                    del self.__outgoingTransactions[(client, transactionId)]
                self.__mutex.release()
                self.trace(
                    "<-- %s %s %s from %s - took %fs" %
                    (mess['code'],
                     transactionId,
                     mess['phrase'],
                        client,
                        time.time() -
                        entry['timestamp']))
                if not entry['event']:
                    self.__fifo_incoming_events_thread.putItem(
                        lambda: self.onResponse(client, transactionId, mess))
            else:
                self.__mutex.release()
                self.trace(
                    "<-- response from %s to unknown transaction ID %s" %
                    (client, transactionId))
                self.trace(self.__outgoingTransactions)
                return

    def start(self):
        """
        Start the manager
        """
        if not self.__started:
            self.__fifo_incoming_events_thread = FifoCallBack.FifoCallbackThread()
            self.__fifo_incoming_events_thread.start()
            self.__started = True
            self.trace("Transaction Manager Started.")

    def stop(self):
        """
        Stop the manager
        """
        if self.__started:
            self.__fifo_incoming_events_thread.stop()
            self.__fifo_incoming_events_thread.join()
            self.__started = False
            self.trace("Transaction Manager Stopped.")

    def trace(self, txt):
        """
        You should override this method

        @param txt:
        @type txt:
        """
        print(txt)

    def onResponse(self, client, tid, response):
        """
        You should override this method

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        pass

    def onRequest(self, client, tid, request):
        """
        You should override this method

        @param client:
        @type client:

        @param tid:
        @type tid:

        @param request:
        @type request:
        """
        pass
