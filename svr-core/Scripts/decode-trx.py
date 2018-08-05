#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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
from __future__ import division

import getopt
import sys
import cStringIO
import base64
import cPickle

sys.path.insert(0, '../' )
import Libs.FileModels.TestResult as TestResult

def help():
    """
    Display help
    """
    print("./decode-trx --trx=<file>")

def error(msg):
    """
    """
    print("ERROR: %s" % msg)
    
def info(msg):
    """
    """
    print("%s" % msg)

def displayErrors(errors):
    """
    """
    info("errors listing (%s):" % len(errors) )
    for err in errors:
        info( "\t%s - %s" % (err['timestamp'], err['short-msg']) )
    
def displayStats(stats):
    """
    """
    info("")
    
    nbDebugPercent = 0
    nbInfoPercent = 0
    nbWarningPercent = 0
    nbErrorPercent = 0
    if stats["nb-total"]: nbDebugPercent = ( stats["nb-debug"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbInfoPercent = ( stats["nb-info"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbWarningPercent = ( stats["nb-warning"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbErrorPercent = ( stats["nb-error"] * 100 ) / stats["nb-total"]
        
    nbAdapterPercent = 0
    nbTimerPercent = 0
    nbStepPercent = 0
    nbStepFailedPercent = 0
    nbStepPassedPercent = 0
    nbMatchPercent = 0
    if stats["nb-total"]: nbAdapterPercent = ( stats["nb-adapter"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbTimerPercent = ( stats["nb-timer"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbStepPercent = ( stats["nb-step"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbStepFailedPercent = ( stats["nb-step-failed"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbStepPassedPercent = ( stats["nb-step-passed"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbMatchPercent = ( stats["nb-match"] * 100 ) / stats["nb-total"]
    
    nbSectionPercent = 0
    nbOthersPercent = 0
    if stats["nb-total"]: nbSectionPercent = ( stats["nb-section"] * 100 ) / stats["nb-total"]
    if stats["nb-total"]: nbOthersPercent = ( stats["nb-others"] * 100 ) / stats["nb-total"]
    
    info("statistics:")
    info("\ttotal events:\t\t%s\t\t(100%%)" % stats["nb-total"])
    info("")
    info("\tdebug events:\t\t%s\t\t(%.2f%%)" % (stats["nb-debug"], nbDebugPercent) )
    info("\tinfo events:\t\t%s\t\t(%.2f%%)" % (stats["nb-info"], nbInfoPercent) )
    info("\twarning events:\t\t%s\t\t(%.2f%%)" % (stats["nb-warning"], nbWarningPercent) )
    info("\terror events:\t\t%s\t\t(%.2f%%)" % (stats["nb-error"], nbErrorPercent) )
    info("")
    info("\tadapter events:\t\t%s\t\t(%.2f%%)" % (stats["nb-adapter"], nbAdapterPercent) )
    info("\ttimer events:\t\t%s\t\t(%.2f%%)" % (stats["nb-timer"], nbTimerPercent) )
    info("\tstep events:\t\t%s\t\t(%.2f%%)" % (stats["nb-step"], nbStepPercent) )
    # info("\t\tpassed:\t\t%s\t\t(%.2f%%)" % (stats["nb-step-passed"], nbStepPassedPercent) )
    # info("\t\tfailed:\t\t%s\t\t(%.2f%%)" % (stats["nb-step-failed"], nbStepFailedPercent) )
    info("\tmatch events:\t\t%s\t\t(%.2f%%)" % (stats["nb-match"], nbMatchPercent) )
    info("")
    info("\tsection events:\t\t%s\t\t(%.2f%%)" % (stats["nb-section"], nbSectionPercent) )
    info("\tothers events:\t\t%s\t\t(%.2f%%)" % (stats["nb-others"], nbOthersPercent) )
    info("")
    
def decodeStats(tr):
    """
    """
    info("constructing statistics...")
    
    statisticsEvents = { 'nb-total': 0, 'nb-info': 0, 'nb-error': 0, 'nb-warning': 0, 'nb-debug': 0,
                    'nb-timer': 0, 'nb-step': 0, 'nb-adapter': 0, 'nb-match': 0, 'nb-section': 0,
                    'nb-others': 0, 'nb-step-failed': 0, 'nb-step-passed': 0}
    errorsEvents = []
    
    try:
        f = cStringIO.StringIO( tr.testresult )
    except Exception as e:
        error( "unable to read test result.." )
    else:
        all = f.readlines()
        try:
            for line in all:
                statisticsEvents["nb-total"] += 1
                
                l = base64.b64decode(line)
                event = cPickle.loads( l )
                
                if "level" in event:
                    if event["level"] == "info": statisticsEvents["nb-info"] += 1
                    if event["level"] == "warning": statisticsEvents["nb-warning"] += 1
                    if event["level"] == "error": 
                        statisticsEvents["nb-error"] += 1
                        errorsEvents.append( event )
                    if event["level"] == "debug": statisticsEvents["nb-debug"] += 1
                
                    if event["level"] in [ "send", "received" ]:  statisticsEvents["nb-adapter"] += 1
                    if event["level"].startswith("step"): statisticsEvents["nb-step"] += 1
                    # if event["level"].startswith("step-failed"): statisticsEvents["nb-step-failed"] += 1
                    # if event["level"].startswith("step-passed"): statisticsEvents["nb-step-passed"] += 1
                    if event["level"].startswith("timer"): statisticsEvents["nb-timer"] += 1
                    if event["level"].startswith("match"): statisticsEvents["nb-match"] += 1
                    if event["level"] == "section": statisticsEvents["nb-section"] += 1
                else:
                    statisticsEvents["nb-others"] += 1
                    
        except Exception as e:
            error("unable to unpickle: %s" % e)
        else:
            displayStats(statisticsEvents)
            displayErrors(errorsEvents)
            
def decodeFile(trxFile):
    """
    """
    doc = TestResult.DataModel()
    doc.error = error
    
    info("reading the testresult...")
    res = doc.load( absPath = trxFile )
    if res: 
        decodeStats(tr=doc)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", [ "trx="])
    except getopt.error, msg:
        print(msg)
        help()
        sys.exit(2)
    if len(opts) == 0:
        help()
        sys.exit(0)

    trxFile = None

    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit(0)
        elif o in ["--trx"]:  
            trxFile = a
    
    if trxFile is not None:
        info("")
        decodeFile(trxFile=trxFile)
    else:
        help()
        sys.exit(0)