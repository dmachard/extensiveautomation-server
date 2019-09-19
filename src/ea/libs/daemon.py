#!/usr/bin/env python

import sys
import os
import time
import atexit
import signal


def log_exception(*args):
    """
    Log exception
    """
    timestamp = time.time()
    c, e, traceback = args

    # extract number line, function name and file
    lineno = traceback.tb_lineno
    frame = traceback.tb_frame
    name = frame.f_code.co_name
    filename = frame.f_code.co_filename

    sys.stderr.write(
        '%s Traceback Num=%s Function=%s File=%s' %
        (timestamp, lineno, name, filename))
    sys.stderr.write('%s')

# a simple unix/linux daemon in Python by Sander Marechal
# adaptation for this project


class Daemon(object):
    def __init__(self):
        """
        A generic daemon class.
        """
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pidfile = None
        self.runningfile = None
        self.name = None

    def prepare(self, pidfile, name, stdin, stdout, stderr, runningfile):
        """
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.runningfile = runningfile
        self.name = name

    def sendSignal(self, pid, sig):
        """
        """
        try:
            os.kill(pid, sig)
            return pid
        except OSError:
            return False
        return True

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" %
                (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" %
                (e.errno, e.strerror))
            sys.exit(1)

        # Setup our signal handlers
        signal.signal(signal.SIGHUP, self.hupHandler)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        if sys.version_info < (3,):
            si = open(self.stdin, 'r')
            so = open(self.stdout, 'a+')
            se = open(self.stderr, 'a+', 0)
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
        else:
            # 1 to select line buffering (only usable in text mode)
            sys.stdout = open(self.stdout, "a+", 1)
            sys.stderr = open(self.stderr, "a+", 1)
            sys.excepthook = log_exception

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

        # write running file
        self.delrunning()

    def hupHandler(self, signum, frame):
        """
        """
        pass

    def stopping(self):
        """
        """
        pass

    def stopped(self):
        """
        """
        pass

    def checkpid(self, pid):
        """
        Check for the existence of a unix pid.
        """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def isrunning(self):
        """
        Check for a pidfile to see if the daemon already runs
        """
        pid = self.getPid()

        if pid is not None:
            # Second verif, check if the process is present
            if self.checkpid(pid=pid):
                return True
            else:
                return False
        else:
            return False

    def delpid(self):
        """
        """
        try:
            os.remove(self.pidfile)
        except BaseException:
            pass

    def getPid(self):
        """
        """
        if self.pidfile is None:
            sys.stderr.write(" (no pid file detected!)")
            sys.exit(1)
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        return pid

    def delrunning(self):
        """
        """
        try:
            os.remove(self.runningfile)
        except BaseException:
            pass

    def setrunning(self):
        """
        """
        open(self.runningfile, 'w+').write("OK")

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        pid = self.getPid()

        if pid is not None:
            # Second verif, check if the process is present
            if self.checkpid(pid=pid):
                sys.stderr.write(" (process already running.)")
                sys.exit(1)
            else:
                sys.stdout.write(
                    " (pid file exist but without process, crash ? whatever removing pidfile and start...)")
                sys.stdout.flush()
                self.delpid()
                self.delrunning()

        # Start the daemon
        self.daemonize()
        self.run()

    def status(self):
        """
        Daemon status
        """
        # get the pid from the pidfile
        pid = self.getPid()

        # initial state
        started = False
        running = False

        if pid is not None:
            # second verif, check if the process is present
            if self.checkpid(pid=pid):
                started = True
            else:
                started = False

        if os.path.exists(self.runningfile):
            running = True

        if started and not running:
            message = "%s is starting...\n"
            sys.stdout.write(message % self.name)
        elif started and running:
            message = "%s is running\n"
            sys.stdout.write(message % self.name)
        else:
            message = "%s is not running\n"
            sys.stdout.write(message % self.name)

        return running

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        pid = self.getPid()

        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)
        if os.path.exists(self.runningfile):
            os.remove(self.runningfile)

        if pid is None:
            return  # not an error in a restart

        self.stopping()
        # Try killing the daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                self.stopped()
            else:
                print(str(err))
                sys.exit(1)
            sys.exit(0)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        pass
