#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""
Module to make some code analysis
"""

from pylint import lint
from pylint.reporters.text import TextReporter

import os
import sys
import copy


try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
# retrieve the path
arg = sys.argv[0]
pathname = os.path.dirname(arg)
PATH = os.path.abspath(pathname)

GenerateRepport=False

if len(sys.argv) == 2:
    if sys.argv[1] == "--report":
        GenerateRepport = True

class WritableObject(object):
    """
    dummy output stream for pylint
    """
    def __init__(self):
        """
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
# http://pylint-messages.wikidot.com/all-codes
# Argument for pylint
#  * [R]efactor for a "good practice" metric violation
#  * [C]onvention for coding standard violation
#  * [W]arning for stylistic problems, or minor programming issues
#  * [E]rror for important programming issues (i.e. most probably bug)
#  * [F]atal for errors which prevented further processing

# disable all check and enable error and fatal messages
# Astroid was not able to interpret all possible types of this variable, so we disable the following code
# E1101 = no-member
# E1103 = maybe-no-member 
# E0611 = no-name-in-module

# Enable following because code can contains error:
#W0631: Using possibly undefined loop variable 

ARGS = [ "--disable=all",  "--enable=E", "--enable=F", "--disable=E1101" , "--disable=E0611", "--disable=E1103",
            "--enable=W0631", "--enable=C0111", "--enable=C0112"
          ] 

# "--enable=C0111", "--enable=C0112"

# report generation or not ?
if GenerateRepport:
    ARGS.extend( [  "-r", "y" ] )
else:
    ARGS.extend( [  "-r", "n" ] )
    pathName = "code_analysis"
    prefixName = "Code"

# exceptions
EXCEPTIONS = [
]

print("Checking code according to PEP8 - Style Guide for Python Code")
print("Analysing ERROR or FATAL messages...")

# walk on the project folder and returns just python
# files on a list
result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.py']
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
    os.mkdir( "%s\\Scripts\\%s\\" % (PATH,pathName) )

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
            f = open( "%s\\Scripts\\%s\\%s_%s.log" % (PATH, pathName, prefixName, os.path.basename(filename) ), 'w')
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