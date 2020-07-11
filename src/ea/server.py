#!/usr/bin/python

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
Provide cli usage of the server
"""

from optparse import OptionParser
import sys
import platform

from ea.serverengine import AutomationServer as Core
from ea.servercontrols import CliFunctions as Cli

# checking python version before to start the server
if sys.version_info[0] == 2:
    if sys.version_info[1] <= 6:
        print("Python %s not supported" % platform.python_version())
        sys.exit(2)
elif sys.version_info[0] == 3:
    if sys.version_info[1] < 5:
        print("Python %s not supported" % platform.python_version())
        sys.exit(2)
else:
    print("Python %s not supported" % platform.python_version())
    sys.exit(2)

# prepare the command line with all options
parser = OptionParser()
if platform.system() != "Linux":
    parser.set_usage(
        "./extensiveautomation.py [start|version|install_adapter|decodetrx|apikey|convert2yaml]")
else:
    parser.set_usage("./extensiveautomation.py [start|stop|reload|version|\
install_adapter|decodetrx|apikey|convert2yaml]")

parser.add_option('--start', dest='start', default=False,
                  action='store_true',
                  help="Start the server.")
if platform.system() == "Linux":
    parser.add_option('--stop', dest='stop', default=False,
                      action='store_true',
                      help="Stop the server.")
    parser.add_option('--status', dest='status', default=False,
                      action='store_true',
                      help='Show the current status of the server.')
    parser.add_option('--reload', dest='reload', default=False,
                      action='store_true',
                      help='Reload the configuration of the server.')
parser.add_option('--version', dest='version', default=False,
                  action='store_true',
                  help='Show the version.')
parser.add_option('--apikey', dest='apikey', default=False,
                  action='store_true',
                  help='Generate key for rest api (argument: <username>)')
parser.add_option('--apisecret', dest='apisecret', default=False,
                  action='store_true',
                  help='Get api secret for user <username>')
parser.add_option('--decodetrx', dest='decodetrx', default=False,
                  action='store_true',
                  help='Decode trx file (argument: <file>)')
parser.add_option('--install_adapter', dest='install_adapter', default=False,
                  action='store_true',
                  help='Install sut adapter (argument: <plugin name>)')
parser.add_option('--convert2yaml', dest='convert2yaml', default=False,
                  action='store_true',
                  help='Convert test XML to YAML')
parser.add_option('--datastorage', dest='datastorage', default=False,
                  action='store_true',
                  help='Show the path of the datastorage')
(options, args) = parser.parse_args()


def cli():
    """
    Function to control the server according to the argument
    provided
    """
    Core.initialize()

    if platform.system() == "Linux":

        if options.stop is True:
            Core.stop()
            sys.exit(0)

        if options.status is True:
            Core.status()
            sys.exit(0)

        if options.reload is True:
            Cli.instance().reload()
            sys.exit(0)

    if options.start is True:
        Core.start()
        sys.exit(0)

    if options.version is True:
        Cli.instance().version()
        sys.exit(0)

    if options.apikey is True:
        if not args:
            parser.print_help()
            sys.exit(2)
        Cli.instance().generateKey(username=args[0])
        sys.exit(0)

    if options.apisecret is True:
        if not args:
            parser.print_help()
            sys.exit(2)
        Cli.instance().getSecret(username=args[0])
        sys.exit(0)
        
    if options.decodetrx is True:
        if not args:
            parser.print_help()
            sys.exit(2)
        Cli.instance().decodeTrx(filename=args[0])
        sys.exit(0)

    if options.install_adapter is True:
        if not args:
            parser.print_help()
            sys.exit(2)
        Cli.instance().installAdapter(name=args[0])
        sys.exit(0)
        
    if options.convert2yaml is True:
        Cli.instance().convert2yaml()
        sys.exit(0)
        
    if options.datastorage is True:
        Cli.instance().show_data_storage()
        sys.exit(0)
        
    parser.print_help()
    sys.exit(2)
