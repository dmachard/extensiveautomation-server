#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------

from pylint import lint
from pylint.reporters.text import TextReporter

import os
import sys
sys.path.insert(0, '../' )

import copy

from  Libs import Settings

PATH_TESTLIB = "%s/../TestExecutorLib/" % Settings.getDirExec()
PATH_CORE = "%s/../Core/" % Settings.getDirExec()
PATH_LIBS = "%s/../Libs/" % Settings.getDirExec()

GenerateRepport=False
if len(sys.argv) == 2:
    if sys.argv[1] == "--report":
        GenerateRepport = True

class WritableObject(object):
    def __init__(self):
        """
        dummy output stream for pylint
        """
        self.content = []
    
    def write(self, st):
        """
        dummy write
        """
        self.content.append(st)
    
    def read(self):
        """
        dummy read
        """
        return self.content

# All codes: http://docs.pylint.org/features.html
# Argument for pylint
#  * [R]efactor for a "good practice" metric violation
#  * [C]onvention for coding standard violation
#  * [W]arning for stylistic problems, or minor programming issues
#  * [E]rror for important programming issues (i.e. most probably bug)
#  * [F]atal for errors which prevented further processing

# disable all check and enable error and fatal messages, disable all not support on centos 5 ...
# Astroid was not able to interpret all possible types of this variable, so we disable the following code
# E1101 = no-member
# E1103 = maybe-no-member 
# E0611 = no-name-in-module
# C0301 = line too long
# C0111 = missing docstring
# C0103 = invalid name
# C0112 = empty docstring
# R0901 = Too many ancestors 
# R0904 = Too many public methods 
# R0915 = Too many statements
# R0912 = Too many branches
# C0324 = Comma not followed by a space (Old)
# C0323 = Operator not followed by a space (Old)
# C0322 =  Operator not preceded by a space (Old)
# R0201 = Method could be a function
# R0903 = Too few public methods
# C0321 = More than one statement on a single line
# C0302 = Too many lines in module
# R0902 = Too many instance attributes
# R0913 = Too many arguments
# R0914 = Too many local variables
# R0915 = Too many statements
# W0703 = Catching too general exception
# W0403 = Relative import
# W0603 = Using the global statement
# W0212 = Access to a protected member
# W0622 =  Redefining built-in
# W0613 = Unused argument
# W0612 = Unused variable
# W0231 = __init__ method from base class %r is not called
# W0141 = Used builtin function
# R0923 = Interface not implemented
# W0621 = Redefining name 
# R0911 = Too many return statements
# W0102 = Dangerous default value
# W0105 = String statement has no effect
# W0201 = Attribute %r defined outside __init__
# W0602 = Using global for %r but no assigment is done
# W0221 = Arguments number differs from %s method
# W0101 = Unreachable code
# W0233 = __init__ method from a non direct base
# W0108 = Lambda may not be necessary
# W0402 = Uses of a deprecated module (bug of pylint ?)
# W0601 = Global variable %r undefined at the module level

ARGS = [  "--enable=E", "--enable=F", "--disable=C0112", "--disable=C0103", "--disable=C0111", "--disable=C0301",
        "--disable=E1101" , "--disable=E0611", "--disable=E1103", "--disable=R0901", "--disable=R0904", "--disable=C0324",
        "--disable=R0915", "--disable=R0912", "--disable=C0323", "--disable=C0322", "--disable=R0201", "--disable=R0903"
        , "--disable=C0302", "--disable=C0321", "--disable=R0902", "--disable=R0913", "--disable=R0914", "--disable=R0915",
         "--disable=W0703", "--disable=W0403", "--disable=W0603", "--disable=W0212", "--disable=W0622", "--disable=W0613", 
         "--disable=W0612", "--disable=W0231", "--disable=W0141", "--disable=R0923", "--disable=W0621", "--disable=R0911",
         "--disable=W0102", "--disable=W0105", "--disable=W0201", "--disable=W0602", "--disable=W0221", "--disable=W0101",
          "--disable=W0233", "--disable=W0108", "--disable=W0402", "--disable=W0601" ] 

# report generation or not ?
if GenerateRepport:
    ARGS.extend( [  "-r", "y" ] )
else:
    ARGS.extend( [  "-r", "n" ] )
    pathName = "code_analysis"
    prefixName = "Code"

# exceptions
EXCEPTIONS = [
    ( "hashlib.py", "" ), # external lib
    ( "pexpect.py", "" ), # external lib
    ( "WebSocket.py", "--disable=F0401"), # unable to import (haslib), support python 2.4
    ( "UsersManager.py", "--disable=F0401"), # unable to import (haslib), support python 2.4
    ( "Context.py", "--disable=F0401"), # unable to import (haslib), support python 2.4
    ( "Xml2Dict.py", "--disable=F0401"), # unable to import (xml.etree.ElementTree), support python 2.4
    ( "Dict2Xml.py", "--disable=F0401"), # unable to import (xml.etree.ElementTree), support python 2.4
]

# print init
print("Checking code according to PEP8 - Style Guide for Python Code")
print("Analysing ERROR or FATAL messages...")

# walk on the project folder and returns just python
# files on a list, inspect only the core, libs and testlib
result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH_TESTLIB) for f in filenames if os.path.splitext(f)[1] == '.py']
result.extend( [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH_CORE) for f in filenames if os.path.splitext(f)[1] == '.py'] )
result.extend( [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH_LIBS) for f in filenames if os.path.splitext(f)[1] == '.py'] )
print("%s files to inspect" % len(result))

# nb errors counters
nbAllError = 0
nbAllFatal = 0
nbAllWarning = 0
nbAllRefactor = 0
nbAllConvention = 0
nbTot = 0

# note on 10
notes = []

# creating the output folder
if not GenerateRepport:
    os.mkdir( "%s/%s" % (Settings.getDirExec(), pathName) )

nbExceptions = 0
for filename in result:
    print("Inspecting the file %s" % filename)

    # checking files exception and update pylint arguments if needed
    ARGS_RUN = copy.copy(ARGS)
    exceptDetected  = False
    for val in EXCEPTIONS:
        fName, fMsg = val
        if fName == os.path.basename(filename):
            if not len(fMsg):
                exceptDetected = True
                break
            ARGS_RUN.append(fMsg)

    if exceptDetected:
        nbExceptions += 1
        continue

    print(ARGS_RUN)

    # execute pylint to analyze the code
    pylint_output = WritableObject()
    lint.Run([filename]+ARGS_RUN, reporter=TextReporter(pylint_output), exit=False)

    if GenerateRepport:
        # extract the note
        note = 0
        for line in pylint_output.read():
            if line.startswith("Your code has been rated at"):
                note = line.split("Your code has been rated at ")[1].split('/10')[0]
                notes.append( float(note) )
                break
    else:
        nbTotError = 0
        nbTotFatal = 0
        nbTotWarning = 0
        nbTotRefactor = 0
        nbTotConvention = 0
        nbTot = 0
        if not len( pylint_output.read() ):
            print('\tNo error or fatal message detected')
        else:
            f = open( "%s/%s/%s_%s.log" % (Settings.getDirExec(), pathName, prefixName, os.path.basename(filename) ), 'w')
            f.write( ''.join(pylint_output.read()) )
            f.close()
            for line in pylint_output.read():
                if line.startswith("E:"): nbTotError += 1
                if line.startswith("F:"): nbTotFatal += 1
                if line.startswith("W:"): nbTotWarning += 1
                if line.startswith("R:"): nbTotRefactor += 1
                if line.startswith("C:"): nbTotConvention += 1
            
            if nbTotError:
                print('\t%s error(s) detected' % (nbTotError))
                nbAllError += nbTotError
            if nbTotFatal:
                print('\t%s fatal(s) detected' % (nbTotFatal))
                nbAllFatal += nbTotFatal
            if nbTotWarning:
                print('\t%s warning(s) detected' % (nbTotWarning))
                nbAllWarning += nbTotWarning
            if nbTotRefactor:
                print('\t%s refactor(s) detected' % (nbTotRefactor))
                nbAllRefactor += nbTotRefactor
            if nbTotConvention:
                print('\t%s convention(s) detected' % (nbTotConvention))
                nbAllConvention += nbTotConvention

# final report
if not GenerateRepport:
    print("")
    print("To validate the code:")
    print("\t- No error message")
    print("\t- No fatal message")
    print("If it's the case, your code is no valid, please to fix it")
    print("")
    print("Total: %s error(s) detected" % nbAllError)
    print("Total: %s fatal(s) detected" % nbAllFatal)
    print("Total: %s warning(s) detected" % nbAllWarning)
    print("Total: %s refactor(s) detected" % nbAllRefactor)
    print("Total: %s convention(s) detected" % nbAllConvention)
else:
    print("")
    print("Criteria:")
    print("\t- No error message")
    print("\t- No fatal message")
    print("If the note is not equal to 10, please to review your code")
    print("")
    print("Global evaluation: %s/10" %  (sum(notes) / (len(result) - nbExceptions) ))