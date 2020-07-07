#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
# This file is part of the extensive automation project
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
A tasks scheduler class.

This module provides a tasks scheduler threaded with callback function.
Tasks are stored in a queue of type heap with time priority.
A task is identified by severals parameters:
    * author
    * event name
    * mode (recursive or not)
    * timestamp
    * id
    * callback function
    * arguments

@author: Denis Machard
@date: 21/01/2013
"""

import time
import datetime
import heapq
import threading
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

INFO = "INFO"
ERROR = "ERROR"

SCHED_UNDEFINED = -1
SCHED_NOW = 0      # one run
SCHED_AT = 1       # run postponed
SCHED_IN = 2       # run postponed
SCHED_EVERY_SEC = 3
SCHED_EVERY_MIN = 4
SCHED_HOURLY = 5
SCHED_DAILY = 6
SCHED_WEEKLY = 7


class Event(object):
    def __init__(self, author, name, mode, timestamp,
                 timeref, id, cb, args, kwargs):
        """
        Event class

        @param author: author name
        @type author: string

        @param name: event description
        @type name: string

        @param mode: type of event
        @type mode: constant

        @param timestamp: start time
        @type timestamp:

        @param timeref: time referentiel
        @type timeref:

        @param id: event id
        @type id:

        @param cb: callback function
        @type cb:

        @param args: callback args
        @type args:

        @param kwargs: callback kwargs
        @type kwargs:
        """
        self.name = name
        self.author = author
        self.mode = mode
        self.timestamp = timestamp
        self.timeref = timeref
        self.id = id
        self.callback = cb
        self.args = args
        self.kwargs = kwargs

    def toTuple(self):
        """
        """
        return (self.id, self.mode, self.timestamp, self.name, self.author)

    def getId(self):
        """
        """
        return self.id

    def setId(self, eventId):
        """
        """
        self.id = eventId

    def schedType(self):
        """
        """
        return self.mode

    def getName(self):
        """
        """
        return self.name

    def getAuthor(self):
        """
        """
        return self.author

    def getTimeSched(self):
        """
        """
        return self.timestamp


class SchedulerThread(threading.Thread):
    def __init__(self, out=None, err=None):
        """
        Initialize the scheduler class

        @param out: redirect info messages
        @type  out: file descriptor

        @param err: redirect error messages
        @type  err: file descriptor
        """
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.mutex = threading.RLock()
        self.queue = []
        self.timer = time.time
        self.running = True
        self.expire = None
        self.addEvent = False
        self.idEvent = 0
        self.precision = 10000  # 4 decimals
        #
        self.out = out
        self.err = err
        #
        self.log("Starting scheduler thread...")

    def convertTimestamp(self, timestamp):
        """
        Convert integer time representation in a form readable

        @param timestamp:
        @type  timestamp:
        """
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)
                          ) + ".%3.3d" % int((timestamp * 1000) % 1000)
        return t

    def log(self, txt, level=INFO):
        """
        Prints log on screen with timestamp (debug informations, errors, etc...)

        @param txt: message
        @type  txt: string

        @param level:
        @type  level: constant
        """
        timestamp = self.convertTimestamp(self.timer())
        if self.out is not None:
            if level == ERROR:
                self.err(unicode(txt).encode('utf-8'))
            else:
                self.out(unicode(txt).encode('utf-8'))
        else:
            print(
                "%s - %s - %s - %s" %
                (timestamp,
                 level,
                 self.__class__.__name__,
                 unicode(txt).encode('utf-8')))

    def getEventId(self):
        """
        """
        self.mutex.acquire()
        self.idEvent += 1
        self.mutex.release()
        return self.idEvent

    def getEventTimestamp(self, regId, timeref, weekly=None, daily=None, hourly=None,
                          everyMin=None, everySec=None, at=None, delay=None, timesec=None):
        """
        """
        if weekly is not None:
            d, h, m, s = weekly
            cur_dt = time.localtime()
            next_dt = datetime.datetime(
                cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, h, m, s, 0)
            delta = datetime.timedelta(days=1)
            while next_dt.weekday() != d:
                next_dt = next_dt + delta
            timestamp = time.mktime(next_dt.timetuple())
            mode = SCHED_WEEKLY
            msg = ">> added event [%s-%s]: weekly %s" % (
                regId, mode, self.convertTimestamp(timestamp))
        elif daily is not None:
            h, m, s = daily
            cur_dt = time.localtime()
            next_dt = datetime.datetime(
                cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, h, m, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            mode = SCHED_DAILY
            msg = ">> added event [%s-%s]: daily %s" % (
                regId, mode, self.convertTimestamp(timestamp))
        elif hourly is not None:
            m, s = hourly
            cur_dt = time.localtime()
            next_dt = datetime.datetime(
                cur_dt.tm_year,
                cur_dt.tm_mon,
                cur_dt.tm_mday,
                cur_dt.tm_hour,
                m,
                s,
                0)
            timestamp = time.mktime(next_dt.timetuple())
            mode = SCHED_HOURLY
            msg = ">> added event [%s-%s]: hourly %s" % (
                regId, mode, self.convertTimestamp(timestamp))
        elif everyMin is not None:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(
                cur_dt.tm_year,
                cur_dt.tm_mon,
                cur_dt.tm_mday,
                cur_dt.tm_hour,
                cur_dt.tm_min,
                everyMin,
                0)
            timestamp = time.mktime(next_dt.timetuple())
            mode = SCHED_EVERY_MIN
            msg = ">> added event [%s-%s]: every min %s" % (
                regId, mode, self.convertTimestamp(timestamp))
        elif everySec is not None:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(
                cur_dt.tm_year,
                cur_dt.tm_mon,
                cur_dt.tm_mday,
                cur_dt.tm_hour,
                cur_dt.tm_min,
                cur_dt.tm_sec,
                everySec * 1000)
            timestamp = time.mktime(next_dt.timetuple())
            mode = SCHED_EVERY_SEC
            msg = ">> added event [%s-%s]: every sec %s" % (
                regId, mode, self.convertTimestamp(timestamp))
        elif at is not None:
            y, m, d, h, ms, s = at
            dt = datetime.datetime(y, m, d, h, ms, s, 0)
            timestamp = time.mktime(dt.timetuple())
            mode = SCHED_AT
            msg = ">> added event [%s-%s]: at %s" % (
                regId, mode, self.convertTimestamp(timestamp))
        elif delay is not None:
            timestamp = timeref + delay
            mode = SCHED_IN
            msg = ">> added event [%s-%s]: in %s seconds" % (
                regId, mode, delay)
        elif timesec is not None:
            timestamp = timesec
            mode = SCHED_NOW
            msg = ">> added now event [%s-%s]: in %s seconds" % (
                regId, mode, self.convertTimestamp(timestamp))
        else:
            raise Exception("Invalid mode")
        return (mode, timestamp, msg)

    def registerEvent(self, id, author, name, weekly, daily, hourly,
                      everyMin, everySec, at, delay, timesec, callback, *args, **kwargs):
        """
        Adds an event in the queue.
        An example to use: registerEvent(None, delay=0.2,callback=Myfunction,argA=1,argB=2)

        @param id:
        @type  id: int

        @param author:
        @type  author: string

        @param name:
        @type  name: string

        @param weekly: (day, hour,minute,second) to call the function
        @type  weekly: tuple

        @param daily: (hour,minute,second) to call the function
        @type  daily: tuple

        @param hourly: (minute,second) to call the function
        @type  hourly:  tuple

        @param everyMin: second value to call the function
        @type  everyMin:integer

        @param everySec: call the function each second
        @type  everySec: integer

        @param at: time to call the function (hour,minute,second)
        @type  at: tuple or None

        @param delay: time elapsed before to call the function (in seconds)
        @type  delay: integer or float or None

        @param timesec: now
        @type  timesec: integer or float or None

        @param  callback: function to callback  when the timeout is expired
        @type: memory address

        @param  args, kwargs: arguments for the callback function
        @type: memory address

        @rtype: Event object
        @return: Event which can be used to remove it
        """
        self.mutex.acquire()
        try:
            # Init some variables
            self.addEvent = True
            timeref = self.timer()

            # Init the event id
            if id is None:
                self.idEvent += 1
                regId = self.idEvent
            else:
                regId = id

            # Init the event timestamp (start time and mode)
            mode, timestamp, msg = self.getEventTimestamp(
                regId, timeref, weekly, daily, hourly, everyMin, everySec, at, delay, timesec)

            # Create the event and push on the queue
            action = Event(
                author,
                name,
                mode,
                timestamp,
                timeref,
                regId,
                callback,
                args,
                kwargs)
            heapq.heappush(self.queue, (timestamp, action))
            self.event.set()
            self.log(msg)
        except Exception as e:
            msg = ">>> Exception caught while adding the event in the queue: " + \
                str(e)
            self.log(msg, level=ERROR)
            action = None
        self.mutex.release()
        return action

    def unregisterEvent(self, event):
        """
        Removes an event from the queue before the expiration time.
        If the event is not in the queue, an error is raised.

        @type   event: Event object, returned by registerEvent(...)
        @param  event: this param enables to recognize the event in the queue

        @rtype: True on success, False otherwise
        @return: boolean
        """
        self.mutex.acquire()
        unregistered = True
        if self.queue:
            try:
                self.queue.remove((event.timestamp, event))
                heapq.heapify(self.queue)
                self.log("<< removed event %s" % event.id)
                del event
            except Exception as e:
                msg = ">>> Exception caught while removing the event from the queue: " + \
                    str(e)
                self.log(msg, level=ERROR)
                unregistered = False
        self.mutex.release()
        return unregistered

    def updateEvent(self, event, weekly, daily, hourly,
                    everyMin, everySec, at, delay, timesec):
        """
        Updates an event from the queue before the expiration time.
        If the event is not in the queue, an error is raised.

        @param weekly: (day, hour,minute,second) to call the function
        @type  weekly: tuple

        @param hourly: (minute,second) to call the function
        @type  hourly:  tuple

        @param hourly: (minute,second) to call the function
        @type  hourly:  tuple

        @param everyMin: second value to call the function
        @type  everyMin:integer

        @param everySec: call the function each second
        @type  everySec: integer

        @param at: time to call the function (hour,minute,second)
        @type  at: tuple or None

        @param delay: time elapsed before to call the function (in seconds)
        @type  delay: integer or float or None

        @param timesec:
        @type  timesec: integer or float or None

        @rtype: True on success, False otherwise
        @return: boolean
        """
        self.mutex.acquire()
        if self.queue:
            try:
                # Init some variables
                self.addEvent = True
                timeref = self.timer()

                # Remove the current event from the queue
                self.queue.remove((event.timestamp, event))
                heapq.heapify(self.queue)
                self.log("<< update event %s" % event.id)

                # Update the event timestamp (start time and mode)
                mode, timestamp, msg = self.getEventTimestamp(
                    event.id, timeref, weekly, daily, hourly, everyMin, everySec, at, delay, timesec)
                event.mode = mode
                event.timestamp = timestamp
                event.timeref = timeref

                # Re-push the event in the queue
                heapq.heappush(self.queue, (timestamp, event))
                self.event.set()
                self.log(msg)
            except Exception as e:
                msg = ">>> Exception caught while updating the event from the queue: " + \
                    str(e)
                self.log(msg, level=ERROR)
                self.mutex.release()
                return False
        self.mutex.release()
        return True

    def stop(self):
        """
        Stops the scheduler thread
        """
        self.mutex.acquire()
        self.running = False
        self.event.set()
        self.log("Scheduler thread stopped.")
        self.mutex.release()

    def run(self):
        """
        Executes events

        Default, the thread does nothing (sleeping). The thread leaves his sleep when an event
        is added or when an event must be executed.
        """
        while self.running:
            self.event.wait(self.expire)
            if self.running:
                self.mutex.acquire()
                if self.queue:
                    if self.addEvent:
                        self.addEvent = False
                        timestamp, evt = self.queue[0]
                        self.expire = evt.timestamp - self.timer()
                        self.event.clear()
                    else:
                        istoolate = False
                        timestamp, evt = self.queue[0]
                        if (evt.mode > SCHED_IN):
                            if (evt.timestamp - evt.timeref) < 0:
                                istoolate = True
                            initial = evt.timestamp
                            real = self.timer()
                        else:
                            initial = evt.timestamp - evt.timeref
                            real = self.timer() - evt.timeref
                        diff = real - initial
                        initialTime = float(
                            int(initial * self.precision)) / self.precision
                        realTime = float(
                            int(real * self.precision)) / self.precision
                        diffTime = float(
                            int(diff * self.precision)) / self.precision
                        if istoolate:
                            heapq.heappop(self.queue)
                            self.log("Too late. remove event %s" % evt.id)
                            # reschedule event for the next iteration
                            self.nextEvent(evt, -1)
                            self.expire = evt.timestamp - self.timer()
                            self.event.clear()
                        else:
                            if diff < 0:
                                diffTime = diffTime * -1
                                self.log(
                                    "The scheduler thread wakes up %s sec. too early." %
                                    diffTime)
                                self.expire = evt.timestamp - self.timer()
                                self.event.clear()
                            else:
                                msg = "Running event %s [ init/real/diff =  %s / %s / %s s ]" % (
                                    evt.id, initialTime, realTime, diffTime)
                                self.log(msg)
                                try:
                                    t = threading.Thread(
                                        target=evt.callback, args=evt.args, kwargs=evt.kwargs)
                                    t.start()
                                except Exception as e:
                                    msg = ">>> Exception caught while executing timer callback: " + \
                                        str(e)
                                    self.log(msg)
                                heapq.heappop(self.queue)
                                # recursive event ?
                                self.nextEvent(evt, realTime, diffTime)
                                if self.queue:
                                    timestamp, evt = self.queue[0]
                                    self.expire = evt.timestamp - self.timer()
                                    self.event.clear()
                                else:
                                    self.expire = None
                                    self.event.clear()
                self.mutex.release()
            else:
                self.log("Stopping scheduler thread...")

    def nextEvent(self, event, realruntime, difftime=0):
        """
        Compute the next start of the event
        Only for recursive event

        @type   event: Event object
        @param  event:

        @type   realruntime:
        @param  realruntime: integer

        @type   difftime:
        @param  difftime: integer
        """
        if event.mode == SCHED_NOW or event.mode == SCHED_AT or event.mode == SCHED_IN:
            return
        if event.mode == SCHED_WEEKLY:
            event.timestamp += 7 * 60 * 60 * 24
        elif event.mode == SCHED_DAILY:
            event.timestamp += 60 * 60 * 24
        elif event.mode == SCHED_HOURLY:
            event.timestamp += 60 * 60
        elif event.mode == SCHED_EVERY_MIN:
            event.timestamp += 60
        elif event.mode == SCHED_EVERY_SEC:
            event.timestamp += 1
        msg = ">> reschedule event %s: %s %s" % (
            event.id, event.mode, self.convertTimestamp(event.timestamp))
        heapq.heappush(self.queue, (event.timestamp, event))
        self.log(msg)
        self.onEventRescheduled(event=event)

    def onEventRescheduled(self, event):
        """
        Should be reimplement

        @type   event: Event object
        @param  event:
        """
        pass

##########################################################################
# Functions which allows to used the SchedulerThread class
# with just one instance "singleton"
##########################################################################


TheSchedulerThread = None


def initialize(out=None, err=None):
    """
    Initialize the scheduler
    Thread started

    @param out: redirect info messages
    @type  out: file descriptor

    @param err: redirect error messages
    @type  err: file descriptor
    """
    global TheSchedulerThread
    if not TheSchedulerThread:
        TheSchedulerThread = SchedulerThread(out, err)
    TheSchedulerThread.start()


def finalize():
    """
    Finalize the scheduler
    Thread stopped
    """
    global TheSchedulerThread
    if TheSchedulerThread:
        TheSchedulerThread.stop()
        TheSchedulerThread.join()
        TheSchedulerThread = None


def registerEvent(id=None, author=None, name=None, weekly=None, daily=None, hourly=None, everySec=None,
                  everyMin=None, at=None, delay=None, timesec=None, callback=None, *args, **kwargs):
    """
    Adds event

    @param id: event id
    @type  id: int

    @param author: author of the task
    @type  author: string

    @param name: name of the task
    @type  name: string

    @param weekly: (day, hour,minute,second) to call the function
    @type  weekly: tuple

    @param daily: (hour,minute,second) to call the function
    @type  daily: tuple

    @param hourly: (minute,second) to call the function
    @type  hourly:  tuple

    @param everyMin: second value to call the function
    @type  everyMin:integer

    @param everySec: call the function each second
    @type  everySec: integer

    @param at: time to call the function (hour,minute,second)
    @type  at: tuple or None

    @param delay: timer in seconds
    @type  delay: Integer

    @param  callback: function to callback  when the timeout is expired
    @type: memory address

    @param  args, kwargs: arguments for the callback function
    @type: memory address

    @rtype: Event object
    @return: Event which can be used to remove it
    """
    registeredEvent = TheSchedulerThread.registerEvent(id, author, name, weekly, daily, hourly, everyMin,
                                                       everySec, at, delay, timesec, callback, *args, **kwargs)
    return registeredEvent


def unregisterEvent(evt):
    """
    Removes event

    @param evt: event
    @type  evt: object

    @rtype: True on success, False otherwise
    @return: boolean
    """
    return TheSchedulerThread.unregisterEvent(evt)


def updateEvent(evt, weekly=None, daily=None, hourly=None,
                everySec=None, everyMin=None, at=None, delay=None, timesec=None):
    """
    Update event

    @param evt: event
    @type  evt: object

    @param weekly: (day, hour,minute,second) to call the function
    @type  weekly: tuple

    @param daily: (hour,minute,second) to call the function
    @type  daily: tuple

    @param hourly: (minute,second) to call the function
    @type  hourly:  tuple

    @param everyMin: second value to call the function
    @type  everyMin:integer

    @param everySec: call the function each second
    @type  everySec: integer

    @param at: time to call the function (hour,minute,second)
    @type  at: tuple or None

    @param delay: timer in seconds
    @type  delay: Integer

    @param timesec: now
    @type  timesec: integer or float or None

    @rtype: True on success, False otherwise
    @return: boolean
    """
    return TheSchedulerThread.updateEvent(
        evt, weekly, daily, hourly, everyMin, everySec, at, delay, timesec)

##########################################################################
# Unit Test
##########################################################################


def func1(arg1, arg2):
    """
    @param arg1:
    @type  arg1:

    @param arg2:
    @type  arg2:
    """
    print("running funtion... ", arg1, arg2)


# if __name__ == "__main__":
    # """
    # """
    # initialize()
    # id1 = registerEvent(delay=10,  callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # id2 = registerEvent(at=(11,00,1), callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # id3 = registerEvent(everySec=0, callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # id4 = registerEvent(everyMin=30, callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # id5 = registerEvent(hourly=(4,30), callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # id6 = registerEvent(daily=(22,54,0), callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # id7 = registerEvent(weekly=(0,22,54,0), callback=func1, arg1 = 'myarg1', arg2 = 'myarg2')
    # unregisterEvent(id6)
    # time.sleep(3850)
    # unregisterEvent(id3)
    # time.sleep(3)
    # finalize()
