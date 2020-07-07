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

import time
import sys
import signal
import os
import platform

from ea.serverengine import DbManager
from ea.serverengine import AgentsManager
from ea.serverengine import TaskManager
from ea.serverengine import Context
from ea.serverengine import HelperManager
from ea.serverengine import ProjectsManager
from ea.serverengine import UsersManager
from ea.serverengine import VariablesManager
from ea.serverengine import StorageDataAdapters
from ea.serverrepositories import (RepoAdapters,
                                   RepoTests,
                                   RepoArchives,
                                   RepoPublic)
from ea.serverinterfaces import (AgentServerInterface,
                                 EventServerInterface,
                                 TestServerInterface)
from ea.servercontrols import (CliFunctions, RestServerInterface)
from ea.libs import (daemon, Settings, Logger)


class AutomationServer(Logger.ClassLogger, daemon.Daemon):
    """
    Main automation server
    """

    def prepareDaemon(self):
        """
        Prepare daemon
        """
        if not Settings.cfgFileIsPresent():
            sys.stdout.write(" (config file doesn't exist)")
            sys.exit(2)

        try:
            # Initialize
            Settings.initialize(path="./", cfgname='settings.ini')

            # create missing folders in var ?
            folder_var_run = "%s/%s" % (Settings.getDirExec(),
                                        Settings.get('Paths', 'run'))
            if not os.path.exists(folder_var_run):
                os.mkdir(folder_var_run, 0o755)

            folder_var_pub = "%s/%s" % (Settings.getDirExec(),
                                        Settings.get('Paths', 'public'))
            if not os.path.exists(folder_var_pub):
                os.mkdir(folder_var_pub, 0o755)

            folder_var_log = "%s/%s" % (Settings.getDirExec(),
                                        Settings.get('Paths', 'logs'))
            if not os.path.exists(folder_var_log):
                os.mkdir(folder_var_log, 0o755)

            folder_var_tmp = "%s/%s" % (Settings.getDirExec(),
                                        Settings.get('Paths', 'tmp'))
            if not os.path.exists(folder_var_tmp):
                os.mkdir(folder_var_tmp, 0o755)

            tests = "%s/%s" % (Settings.getDirExec(),
                               Settings.get('Paths', 'tests'))
            if not os.path.exists(tests):
                os.mkdir(tests, 0o755)

            folder_var_testsresults = "%s/%s" % (
                Settings.getDirExec(), Settings.get('Paths', 'testsresults'))
            if not os.path.exists(folder_var_testsresults):
                os.mkdir(folder_var_testsresults, 0o755)

            folder_var_bkp_tasks = "%s/%s" % (Settings.getDirExec(),
                                              Settings.get('Paths', 'backups-tasks'))
            if not os.path.exists(folder_var_bkp_tasks):
                os.mkdir(folder_var_bkp_tasks, 0o755)

            folder_adapters = "%s/%s" % (Settings.getDirExec(),
                                         Settings.get('Paths', 'packages-sutadapters'))
            if not os.path.exists(folder_adapters):
                os.mkdir(folder_adapters, 0o755)

            Logger.initialize()
            CliFunctions.initialize(parent=self)
        except Exception as e:
            self.error("Unable to initialize settings: %s" % str(e))
        else:

            app_name = Settings.get('Server', 'name')
            app_name = app_name.replace(" ", "").lower()

            # config file exist so prepare the deamon
            self.prepare(pidfile="%s/%s/%s.pid" % (Settings.getDirExec(),
                                                   Settings.get(
                                                       'Paths', 'run'),
                                                   app_name),
                         name=Settings.get('Server', 'name'),
                         stdout="%s/%s/output.log" % (Settings.getDirExec(),
                                                      Settings.get('Paths', 'logs')),
                         stderr="%s/%s/output.log" % (Settings.getDirExec(),
                                                      Settings.get('Paths', 'logs')),
                         stdin="/dev/null",
                         runningfile="%s/%s/%s.running" % (Settings.getDirExec(),
                                                           Settings.get(
                                                               'Paths', 'run'),
                                                           app_name),
                         )

    def initialize(self):
        """
        Starts all modules
        Exit if the service is alreayd running or if the config file is missing
        """
        starttime = time.time()
        if self.isrunning():
            sys.stdout.write(" (server is already running)")
            sys.exit(1)

        # run the server as daemon only for linux
        if platform.system() == "Linux":
            self.daemonize()

        try:
            # Initialize
            self.info("Starting up server...")
            self.trace("** System encoding (in): %s" % sys.stdin.encoding)
            self.trace("** System encoding (out): %s" % sys.stdout.encoding)
            self.info("Settings, Logger and CLI ready")

            DbManager.initialize()
            DbManager.instance().isUp()
            self.info("Database manager ready")

            # Initialize the core
            Context.initialize()
            self.info("Context ready")

            ProjectsManager.initialize(context=Context.instance())
            self.info("Projects Manager ready")
            UsersManager.initialize(context=Context.instance())
            self.info("Users Manager ready")
            VariablesManager.initialize(context=Context.instance())
            self.info("Variables Manager ready")

            TaskManager.initialize(context=Context)
            self.info("Task Manager ready")

            # Initialize all repositories
            RepoTests.initialize(context=Context.instance())
            self.info("Repo manager for tests ready")
            RepoArchives.initialize(context=Context.instance())
            self.info("Repo manager for archives ready")
            RepoAdapters.initialize(context=Context.instance())
            StorageDataAdapters.initialize(context=Context.instance())
            self.info("Adapters Manager and Storage Data ready")
            RepoPublic.initialize()
            self.info("Repo manager for public area is ready")

            HelperManager.initialize()
            self.info("Helper manager ready")

            AgentsManager.initialize(context=Context.instance())
            self.info("Agents Manager ready")

            # Initialize all interfaces
            self.info("Starting ESI on %s:%s" % (Settings.get('Bind', 'ip-esi'),
                                                 Settings.getInt('Bind', 'port-esi')))
            EventServerInterface.initialize(listeningAddress=(Settings.get('Bind', 'ip-esi'),
                                                              Settings.getInt(
                'Bind', 'port-esi')
            ),
                sslSupport=Settings.getInt(
                'Client_Channel', 'channel-ssl'),
                wsSupport=Settings.getInt(
                'Client_Channel', 'channel-websocket-support'),
                context=Context.instance()
            )
            self.info("Starting TSI on %s:%s" % (Settings.get('Bind', 'ip-tsi'),
                                                 Settings.getInt('Bind', 'port-tsi')))
            TestServerInterface.initialize(listeningAddress=(Settings.get('Bind', 'ip-tsi'),
                                                             Settings.getInt(
                                                                 'Bind', 'port-tsi')
                                                             ),
                                           context=Context.instance()
                                           )
            self.info("Starting RSU on %s:%s" % (Settings.get('Bind', 'ip-rsi'),
                                                 Settings.getInt('Bind', 'port-rsi')))
            RestServerInterface.initialize(listeningAddress=(Settings.get('Bind', 'ip-rsi'),
                                                             Settings.getInt(
                'Bind', 'port-rsi')
            )
            )
            self.info("Starting ASI on %s:%s" % (Settings.get('Bind', 'ip-asi'),
                                                 Settings.getInt('Bind', 'port-asi')))
            AgentServerInterface.initialize(listeningAddress=(Settings.get('Bind', 'ip-asi'),
                                                              Settings.getInt(
                'Bind', 'port-asi')
            ),
                sslSupport=Settings.getInt(
                'Agent_Channel', 'channel-ssl'),
                wsSupport=Settings.getInt(
                'Agent_Channel', 'channel-websocket-support'),
                tsi=TestServerInterface.instance(),
                context=Context.instance()
            )

            # Start on modules
            RestServerInterface.instance().start()
            self.info("RSI is listening on tcp://%s:%s" % (Settings.get('Bind', 'ip-rsi'),
                                                           Settings.get('Bind', 'port-rsi')))
            EventServerInterface.instance().startSA()
            self.info("ESI is listening on tcp://%s:%s" % (Settings.get('Bind', 'ip-esi'),
                                                           Settings.get('Bind', 'port-esi')))
            TestServerInterface.instance().startSA()
            self.info("TSI is listening on tcp://%s:%s" % (Settings.get('Bind', 'ip-tsi'),
                                                           Settings.get('Bind', 'port-tsi')))
            AgentServerInterface.instance().startSA()
            self.info("ASI is listening on tcp://%s:%s" % (Settings.get('Bind', 'ip-asi'),
                                                           Settings.get('Bind', 'port-asi')))

            # Now start the scheduler and reload tasks
            taskReloaded = TaskManager.instance().loadBackups()
            if taskReloaded is None:
                self.info("Reload tasks disabled")
            elif taskReloaded:
                self.info("Tasks reloaded")
            else:
                self.error("Failed to reload tasks")

        except Exception as e:
            self.error("Unable to start server: %s" % str(e))
            self.cleanup()
            sys.exit(3)

        stoptime = time.time()
        self.info("%s successfully started (in %s sec.)" % (Settings.get('Server', 'name'),
                                                            int(stoptime - starttime)))

        # only for windows platform
        if platform.system() == "Windows":
            print("Server successfully started...")

        self.setrunning()
        self.run()

    def cleanup(self):
        """
        Cleanup the server
        """
        self.info('Cleanup...')

        self.trace("Cleanup agent manager")
        try:
            AgentsManager.finalize()
        except Exception:
            pass

        self.trace("Cleanup context")
        try:
            Context.finalize()
        except Exception:
            pass

        self.trace("Cleanup projects manager")
        try:
            ProjectsManager.finalize()
        except Exception:
            pass

        self.trace("Cleanup users manager")
        try:
            UsersManager.finalize()
        except Exception:
            pass

        self.trace("Cleanup variables manager")
        try:
            VariablesManager.finalize()
        except Exception:
            pass
            
        self.trace("Cleanup task manager")
        try:
            TaskManager.finalize()
        except Exception:
            pass

        self.trace("Cleanup test public manager")
        try:
            RepoPublic.finalize()
        except Exception:
            pass

        self.trace("Cleanup test repo manager")
        try:
            RepoTests.finalize()
        except Exception:
            pass

        self.trace("Cleanup test archives manager")
        try:
            RepoArchives.finalize()
        except Exception:
            pass

        self.trace("Cleanup helper manager")
        try:
            HelperManager.finalize()
        except Exception:
            pass

        self.trace("Cleanup adapters manager")
        try:
            RepoAdapters.finalize()
        except Exception:
            pass

        self.trace("Cleanup adapters data storage")
        try:
            StorageDataAdapters.finalize()
        except Exception:
            pass

        self.trace("Cleanup WSU")
        try:
            RestServerInterface.instance().stop()
            RestServerInterface.finalize()
        except Exception:
            pass

        self.trace("Cleanup ESI")
        try:
            EventServerInterface.instance().stopSA()
            EventServerInterface.finalize()
        except Exception:
            pass

        self.trace("Cleanup TSI")
        try:
            TestServerInterface.instance().stopSA()
            TestServerInterface.finalize()
        except Exception:
            pass

        self.trace("Cleanup ASI")
        try:
            AgentServerInterface.instance().stopSA()
            AgentServerInterface.finalize()
        except Exception:
            pass

        self.trace("Cleanup db manager")
        try:
            DbManager.finalize()
        except Exception:
            pass

        self.trace("Cleanup settings")
        try:
            Settings.finalize()
        except Exception:
            pass

        self.trace("Cleanup logger, cli")
        try:
            CliFunctions.finalize()
            Logger.finalize()
        except Exception:
            pass

    def stopping(self):
        """
        On stopping the server
        """
        self.info("Stopping server...")

        # cleanup all child processes
        for f in os.listdir("%s/%s" % (Settings.getDirExec(),
                                       Settings.get('Paths', 'run'))):
            if f.endswith(".pid"):
                pid = f.split(".pid")[0]

                # kill the process
                if pid.isdigit():
                    self.info('Stopping chid processes %s...' % pid)
                    try:
                        while True:
                            os.kill(int(pid), signal.SIGTERM)
                            time.sleep(0.1)
                    except OSError:
                        pass
                    time.sleep(1)
                    # just to be sure, delete a second time
                    try:
                        os.remove("%s/%s/%s.pid" % (Settings.getDirExec(),
                                                    Settings.get('Paths', 'run'), pid))
                    except Exception:
                        pass

    def stopped(self):
        """
        On server stopped
        """
        self.info("%s successfully stopped!" % Settings.get('Server', 'name'))

    def finalize(self):
        """
        Stops all modules
        """
        self.stop()

    def run(self):
        """
        Running in loop
        """
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stopping()
            self.cleanup()

    def hupHandler(self, signum, frame):
        """
        Hup handler
        """
        self.info('Reloading configuration...')

        # reload settings ini
        Settings.finalize()
        Settings.initialize()

        # reload config from database
        Context.instance().readConfigDb()

        # reconfigure the level of log message
        Logger.reconfigureLevel()

        # reload cache
        UsersManager.instance().loadCache()

        self.info('Configuration reloaded!')


SERVER = None  # singleton


def instance():
    """
    Returns the singleton
    """
    return SERVER


def start():
    """
    Start the server
    """
    instance().initialize()


def stop():
    """
    Stop the server
    """
    instance().finalize()


def status():
    """
    Return the status of the automation server
    """
    instance().status()


def initialize():
    """
    Instance creation
    """
    global SERVER
    SERVER = AutomationServer()
    SERVER.prepareDaemon()
