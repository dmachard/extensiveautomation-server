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

import time
import threading
import base64
import zlib
import json

try:
    import DbManager
    import TaskManager
    import Common
except ImportError: # python3 support
    from . import DbManager
    from . import TaskManager
    from . import Common
    
from Libs import Settings, Logger
from ServerInterfaces import EventServerInterface as ESI

class StatsManager(Logger.ClassLogger):
    """
    """
    PASS = "PASS"
    FAIL = "FAIL"
    UNDEFINED= "UNDEFINED"
    def __init__ (self):
        """
        Statistics Manager for tests
        """
        self.__mutex__ = threading.RLock()
        self.dbt_testcases = '%s-testcases-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_testunits = '%s-testunits-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_testabstracts = '%s-testabstracts-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_testsuites = '%s-testsuites-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_testplans = '%s-testplans-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_testglobals = '%s-testglobals-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_scripts = '%s-scripts-stats' % Settings.get( 'MySql', 'table-prefix')
        self.dbt_writing = '%s-writing-stats' % Settings.get( 'MySql', 'table-prefix')
        self.notifyUsers =  Settings.getInt( 'Notifications', 'statistics')

    def getStats (self):
        """
        Returns statistics
        """
        ret = {}
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            nbScriptCompleted = 0; nbScriptError = 0; nbScriptKilled = 0
            ret['scripts'] = {  'nb-completed': nbScriptCompleted, 'nb-error':nbScriptError, 'nb-killed': nbScriptKilled   }
            nbTgPass = 0; nbTgFail = 0; nbTgUndef = 0
            ret['testglobals'] =  { 'nb-pass': nbTgPass, 'nb-fail': nbTgFail, 'nb-undef': nbTgUndef }
            nbTpPass = 0; nbTpFail = 0; nbTpUndef = 0
            ret['testplans'] =  { 'nb-pass': nbTpPass, 'nb-fail': nbTpFail, 'nb-undef': nbTpUndef }
            nbTsPass = 0; nbTsFail = 0; nbTsUndef = 0
            ret['testsuites'] =  {  'nb-pass': nbTsPass, 'nb-fail': nbTsFail, 'nb-undef': nbTsUndef }
            nbTuPass = 0; nbTuFail = 0; nbTuUndef = 0
            ret['testunits'] =  { 'nb-pass': nbTuPass, 'nb-fail': nbTuFail, 'nb-undef': nbTuUndef }
            nbTaPass = 0; nbTaFail = 0; nbTaUndef = 0
            ret['testabstracts'] =  { 'nb-pass': nbTaPass, 'nb-fail': nbTaFail, 'nb-undef': nbTaUndef }
            nbTcPass = 0; nbTcFail = 0; nbTcUndef = 0
            ret['testcases'] =  { 'nb-pass': nbTcPass, 'nb-fail': nbTcFail, 'nb-undef': nbTcUndef }
            return ret
            
        self.trace('contructing tests stats' )
        nbScriptCompleted = 0; nbScriptError = 0; nbScriptKilled = 0
        try:
            sql_query = "SELECT SUM( IF(result = '%s', 1, 0) ) AS 'nbComplete', SUM( IF(result = '%s', 1, 0) ) AS 'nbError'," % ( TaskManager.STATE_COMPLETE, TaskManager.STATE_ERROR )
            sql_query += "SUM( IF(result = '%s', 1, 0) ) AS 'nbKilled' " % TaskManager.STATE_KILLED
            sql_query += " FROM `%s`;" % self.dbt_scripts
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbScriptCompleted = int(rows[0][0])
            if rows[0][1] is not None:
                nbScriptError = int(rows[0][1])
            if rows[0][2] is not None:
                nbScriptKilled = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem") 
        except Exception as e:
            self.error( "unable to get scripts stats: %s" % str(e) )
        ret['scripts'] = {  'nb-completed': nbScriptCompleted, 'nb-error':nbScriptError, 'nb-killed': nbScriptKilled   }
        self.trace('nb-completed %s, nb-error %s, nb-killed %s' %  ( nbScriptCompleted, nbScriptError, nbScriptKilled ) )

        nbTgPass = 0; nbTgFail = 0; nbTgUndef = 0
        try:
            sql_query = "SELECT SUM( IF(result = 'PASS', 1, 0) ) AS 'nbPass', SUM( IF(result = 'FAIL', 1, 0) ) AS 'nbFail',"
            sql_query += "SUM( IF(result = 'UNDEFINED', 1, 0) ) AS 'nbUndef' "
            sql_query += " FROM `%s`;" % self.dbt_testglobals
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbTgPass = int(rows[0][0])
            if rows[0][1] is not None:
                nbTgFail = int(rows[0][1])
            if rows[0][2] is not None:
                nbTgUndef = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem")
        except Exception as e:
            self.error( "unable to get testglobals stats: %s" % str(e) )
        ret['testglobals'] =  { 'nb-pass': nbTgPass, 'nb-fail': nbTgFail, 'nb-undef': nbTgUndef }
        self.trace('nb-tg-pass %s, nb-tg-fail %s, nb-tg-undef %s' %  ( nbTgPass, nbTgFail, nbTgUndef ) )

        nbTpPass = 0; nbTpFail = 0; nbTpUndef = 0
        try:
            sql_query = "SELECT SUM( IF(result = 'PASS', 1, 0) ) AS 'nbPass', SUM( IF(result = 'FAIL', 1, 0) ) AS 'nbFail',"
            sql_query += "SUM( IF(result = 'UNDEFINED', 1, 0) ) AS 'nbUndef' "
            sql_query += " FROM `%s`;" % self.dbt_testplans
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbTpPass = int(rows[0][0])
            if rows[0][1] is not None:
                nbTpFail = int(rows[0][1])
            if rows[0][2] is not None:
                nbTpUndef = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem")
        except Exception as e:
            self.error( "unable to get testplans stats: %s" % str(e) )
        ret['testplans'] =  { 'nb-pass': nbTpPass, 'nb-fail': nbTpFail, 'nb-undef': nbTpUndef }
        self.trace('nb-tp-pass %s, nb-tp-fail %s, nb-tp-undef %s' %  ( nbTpPass, nbTpFail, nbTpUndef ) )

        nbTsPass = 0; nbTsFail = 0; nbTsUndef = 0
        try:
            sql_query = "SELECT SUM( IF(result = 'PASS', 1, 0) ) AS 'nbPass', SUM( IF(result = 'FAIL', 1, 0) ) AS 'nbFail',"
            sql_query += "SUM( IF(result = 'UNDEFINED', 1, 0) ) AS 'nbUndef' "
            sql_query += " FROM `%s`;" % self.dbt_testsuites
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbTsPass = int(rows[0][0])
            if rows[0][1] is not None:
                nbTsFail = int(rows[0][1])
            if rows[0][2] is not None:
                nbTsUndef = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem")
        except Exception as e:
            self.error( "unable to get testsuites stats: %s" % str(e) )
        ret['testsuites'] =  {  'nb-pass': nbTsPass, 'nb-fail': nbTsFail, 'nb-undef': nbTsUndef }
        self.trace('nb-ts-pass %s, nb-ts-fail %s, nb-ts-undef %s' %  ( nbTsPass, nbTsFail, nbTsUndef ) )


        nbTuPass = 0; nbTuFail = 0; nbTuUndef = 0
        try:
            sql_query = "SELECT SUM( IF(result = 'PASS', 1, 0) ) AS 'nbPass', SUM( IF(result = 'FAIL', 1, 0) ) AS 'nbFail',"
            sql_query += "SUM( IF(result = 'UNDEFINED', 1, 0) ) AS 'nbUndef'"
            sql_query += " FROM `%s`;" % self.dbt_testunits
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbTuPass = int(rows[0][0])
            if rows[0][1] is not None:
                nbTuFail = int(rows[0][1])
            if rows[0][2] is not None:
                nbTuUndef = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem")
        except Exception as e:
            self.error( "unable to get testunits stats: %s" % str(e) )
        ret['testunits'] =  { 'nb-pass': nbTuPass, 'nb-fail': nbTuFail, 'nb-undef': nbTuUndef }
        self.trace('nb-tu-pass %s, nb-tu-fail %s, nb-tu-undef %s' %  ( nbTuPass, nbTuFail, nbTuUndef ) )

        nbTaPass = 0; nbTaFail = 0; nbTaUndef = 0
        try:
            sql_query = "SELECT SUM( IF(result = 'PASS', 1, 0) ) AS 'nbPass', SUM( IF(result = 'FAIL', 1, 0) ) AS 'nbFail',"
            sql_query += "SUM( IF(result = 'UNDEFINED', 1, 0) ) AS 'nbUndef'"
            sql_query += " FROM `%s`;" % self.dbt_testabstracts
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbTaPass = int(rows[0][0])
            if rows[0][1] is not None:
                nbTaFail = int(rows[0][1])
            if rows[0][2] is not None:
                nbTaUndef = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem")
        except Exception as e:
            self.error( "unable to get testabstracts stats: %s" % str(e) )
        ret['testabstracts'] =  { 'nb-pass': nbTaPass, 'nb-fail': nbTaFail, 'nb-undef': nbTaUndef }
        self.trace('nb-ta-pass %s, nb-ta-fail %s, nb-ta-undef %s' %  ( nbTaPass, nbTaFail, nbTaUndef ) )

        nbTcPass = 0; nbTcFail = 0; nbTcUndef = 0
        try:
            sql_query = "SELECT SUM( IF(result = 'PASS', 1, 0) ) AS 'nbPass', SUM( IF(result = 'FAIL', 1, 0) ) AS 'nbFail',"
            sql_query += "SUM( IF(result = 'UNDEFINED', 1, 0) ) AS 'nbUndef'"
            sql_query += " FROM `%s`;" % self.dbt_testcases
            mysqlret, rows = DbManager.instance().querySQL(  query = sql_query )
            if rows[0][0] is not None:
                nbTcPass = int(rows[0][0])
            if rows[0][1] is not None:
                nbTcFail = int(rows[0][1])
            if rows[0][2] is not None:
                nbTcUndef = int(rows[0][2])
            if not mysqlret:
                raise Exception("sql problem")
        except Exception as e:
            self.error( "unable to get testcases stats: %s" % str(e) )
        ret['testcases'] =  { 'nb-pass': nbTcPass, 'nb-fail': nbTcFail, 'nb-undef': nbTcUndef }
        self.trace('nb-tc-pass %s, nb-tc-fail %s, nb-tc-undef %s' %  ( nbTcPass, nbTcFail, nbTcUndef ) )

        return ret

    def getNbTests(self):
        """
        Get number of tests
        """
        nb = [ {'nbta': 0, 'nbtc': 0, 'nbsc': 0, 'nbtg': 0, 'nbtp': 0, 'nbts': 0, 'nbtu': 0} ]
        
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of tests')
        
        ok, nb_entries = DbManager.instance().querySQL( columnName=True, query="""SELECT 
                                        count(*) as nbsc, 
                                        (SELECT count(*) FROM `%s`) as nbtg,  
                                        (SELECT count(*) FROM `%s`) as nbtp,  
                                        (SELECT count(*) FROM `%s`) as nbts, 
                                        (SELECT count(*) FROM `%s`) as nbtu,
                                        (SELECT count(*) FROM `%s`) as nbta,
                                        (SELECT count(*) FROM `%s`) as nbtc
                                        FROM `%s`;""" % ( self.dbt_testglobals, self.dbt_testplans,
                                                          self.dbt_testsuites, self.dbt_testunits,
                                                          self.dbt_testabstracts, self.dbt_testcases,
                                                          self.dbt_scripts ) 
                    )
        if ok:
            self.trace('number of tests successfully retrieved')
            return nb_entries
        else:
            self.error('unable to retrieve the number of tests')
        return nb
        
    def getNbOfScripts(self):
        """
        Return the number of scripts, used on the module context 

        @return: nb sc in database
        @rtype: int
        """
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of sc')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_scripts )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of sc: %s' % nb)
        return nb

    def getNbOfTestglobals(self):
        """
        Return the number of testglobals, used on the module context

        @return: nb tp in database
        @rtype: int
        """
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of tg')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_testglobals )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of tg: %s' % nb)
        return nb

    def getNbOfTestplans(self):
        """
        Return the number of testplans, used on the module context

        @return: nb tp in database
        @rtype: int
        """
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of tp')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_testplans )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of tp: %s' % nb)
        return nb

    def getNbOfTestunits(self):
        """
        Return the number of testunits, used on the module context

        @return: nb ts in database
        @rtype: int
        """
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of tu')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_testunits )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of tu: %s' % nb)
        return nb
        
    def getNbOfTestabstracts(self):
        """
        Return the number of testabstracts, used on the module context

        @return: nb ts in database
        @rtype: int
        """
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of ta')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_testabstracts )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of ta: %s' % nb)
        return nb

    def getNbOfTestsuites(self):
        """
        Return the number of testsuites, used on the module context

        @return: nb ts in database
        @rtype: int
        """
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of ts')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_testsuites )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of ts: %s' % nb)
        return nb

    def getNbOfTestcases(self):
        """
        Return the number of testcases, used on the module context

        @return: nb tc in database
        @rtype: int
        """
        
        nb = 0
        if not Settings.getInt( 'MySql', 'read-test-statistics'):
            return nb
        self.trace('get number of tc')
        ok, nb_entries = DbManager.instance().querySQL( query="SELECT count(*) FROM `%s`" % self.dbt_testcases )
        if ok:
            nb = int( nb_entries[0][0] )
            self.trace('number of tc: %s' % nb)
        return nb

    def resetStats(self):
        """
        Reset statistics 

        @return: reset status
        @rtype: boolean
        """
        ret = False
        self.trace('empty statistics tables')
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            
            # truncate all tables
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_scripts)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_scripts)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_testabstracts)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_testabstracts)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_testunits)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_testunits)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_testsuites)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_testsuites)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_testplans)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_testplans)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_testglobals)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_testglobals)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_testcases)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_testcases)
            ret, rows = DbManager.instance().querySQL( query = "DELETE FROM `%s`;" % self.dbt_writing)
            if not ret:
                raise Exception("sql problem to reset %s" % self.dbt_writing)
            ret = True
        except Exception as e:
            self.error( "[resetStats]%s" % str(e) )
        return ret

    def addResultScript (self, scriptResult, scriptUser, scriptDuration, scriptProject ):
        """
        Add script result to db

        @param scriptResult: COMPLETE, ERROR, KILLED, etc...
        @type scriptResult: str

        @param scriptUser: username
        @type scriptUser: str

        @param scriptDuration: duration
        @type scriptDuration: str
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace('add result sc %s' % scriptResult)
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, project_id) VALUES ('%s','%s',%s,'%s','%s')" 
                                % (self.dbt_scripts, strDate, scriptResult, scriptUser, scriptDuration, scriptProject  ) )
            if not ret:
                raise Exception("failed to add result script in db")
        except Exception as e:
            self.error( e )
        else:
            if self.notifyUsers:
                data = ( 'stats', ( None, self.getStats() ) )   
                ESI.instance().notifyByUserTypes( body=data, 
                                                  admin=True, 
                                                  monitor=True, 
                                                  tester=False)

    def addResultTestCase(self, testResult, fromUser, testDuration, testProject):
        """
        Add testcase result to db

        @param testResult: PASS, FAIL, UNDEFINED
        @type testResult: str

        @param fromUser: username
        @type fromUser: str

        @param testDuration:
        @type testDuration: str
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace( 'add result tc %s' % testResult )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, project_id) VALUES ('%s','%s',%s,'%s',%s)" 
                                % (self.dbt_testcases, strDate, testResult, fromUser, testDuration, testProject ) )
            if not ret:
                raise Exception("unable to add result testcase in db")
        except Exception as e:
            self.error( e )
        self.__mutex__.release()

    def addResultTestUnit(self, tuResult, fromUser, tuDuration, nbTc, prjId):
        """
        Add testunit result to db 

        @param tsResult: PASS, FAIL, UNDEFINED
        @type tsResult: str

        @param fromUser: username
        @type fromUser: str

        @param tsDuration:
        @type tsDuration: str

        @param nbTc:
        @type nbTc: str
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace( 'add result tu %s' % tuResult )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, nbtc, project_id) VALUES ('%s','%s',%s,'%s',%s,%s)" 
                                % (self.dbt_testunits, strDate, tuResult, fromUser, tuDuration, nbTc, prjId ) )
            if not ret:
                raise Exception("unable to add result testunit in db")
        except Exception as e:
            self.error( e )
        self.__mutex__.release()
        
    def addResultTestAbstract(self, taResult, fromUser, taDuration, nbTc, prjId):
        """
        Add testabstract result to db 

        @param taResult: PASS, FAIL, UNDEFINED
        @type taResult: str

        @param fromUser: username
        @type fromUser: str

        @param taDuration:
        @type taDuration: str

        @param nbTc:
        @type nbTc: str
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace( 'add result ta %s' % taResult )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, nbtc, project_id) VALUES ('%s','%s',%s,'%s',%s,%s)" 
                                % (self.dbt_testabstracts, strDate, taResult, fromUser, taDuration, nbTc, prjId ) )
            if not ret:
                raise Exception("unable to add result testabstract in db")
        except Exception as e:
            self.error( e )
        self.__mutex__.release()
        
    def addResultTestSuite(self, tsResult, fromUser, tsDuration, nbTc, prjId):
        """
        Add testcase result to db

        @param tsResult: PASS, FAIL, UNDEFINED
        @type tsResult: str

        @param fromUser: username
        @type fromUser: str

        @param tsDuration:
        @type tsDuration: str

        @param nbTc:
        @type nbTc: str
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace( 'add result ts %s' % tsResult )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, nbtc, project_id) VALUES ('%s','%s',%s,'%s',%s,%s)" 
                                % (self.dbt_testsuites, strDate, tsResult, fromUser, tsDuration, nbTc, prjId ) )
            if not ret:
                raise Exception("unable to add result testsuite in db")
        except Exception as e:
            self.error( e )
        self.__mutex__.release()

    def addResultTestPlan(self, tpResult, fromUser, tpDuration, nbTs, nbTu, nbTc, prjId):
        """
        Add testcase result to db

        @param tpResult: PASS, FAIL, UNDEFINED
        @type tpResult: str

        @param fromUser: username
        @type fromUser: str

        @param tpDuration:
        @type tpDuration: str

        @param nbTs:
        @type nbTs: integer

        @param prjId:
        @type prjId: integer
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace( 'add result tp %s' % tpResult )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, nbts, nbtu, nbtc, project_id) VALUES ('%s','%s',%s,'%s',%s,%s,%s,%s)" 
                                % (self.dbt_testplans, strDate, tpResult, fromUser, tpDuration, nbTs, nbTu, nbTc, prjId ) )
            if not ret:
                raise Exception("unable to add result testplan in db")
        except Exception as e:
            self.error( e )
        self.__mutex__.release()

    def addResultTestGlobal(self, tgResult, fromUser, tgDuration, nbTs, nbTu, nbTc, prjId):
        """
        Add testcase result to db

        @param tpResult: PASS, FAIL, UNDEFINED
        @type tpResult: str

        @param fromUser: username
        @type fromUser: str

        @param tpDuration:
        @type tpDuration: str

        @param nbTp:
        @type nbTp: integer

        @param nbTs:
        @type nbTs: integer
        
        @param nbTu:
        @type nbTu: integer

        @param prjId:
        @type prjId: integer
        """
        if not Settings.getInt( 'MySql', 'insert-test-statistics'):
            return
        self.trace( 'add result tg %s' % tgResult )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, result, user_id, duration, nbts, nbtu, nbtc, project_id) VALUES ('%s','%s',%s,'%s',%s,%s,%s,%s)" 
                                % (self.dbt_testglobals, strDate, tgResult, fromUser, tgDuration, nbTs, nbTu, nbTc, prjId ) )
            if not ret:
                raise Exception("unable to add result testglobals in db")
        except Exception as e:
            self.error( e )
        self.__mutex__.release()

    def addWritingDuration(self, fromUser, prjId, writingDuration, isTs=False, isTp=False, isTu=False, isTg=False, isTa=False):
        """
        Add writing duration in database

        @param fromUser: user id
        @type fromUser: integer

        @param writtingDuration: writting duration
        @type writtingDuration: integer

        @param prjId: project id
        @type prjId: integer

        @param isTs: is testsuite
        @type isTs: boolean

        @param isTp: is testsuite
        @type isTp: boolean

        @param isTu: is testsuite
        @type isTu: boolean

        @param isTg: is testsuite
        @type isTg: boolean
        """
        rlt = True
        # if not Settings.getInt( 'MySql', 'insert-test-statistics'): return rlt
        self.trace( 'add writing duration %s sec.' % writingDuration )
        self.__mutex__.acquire()
        try:
            strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            #
            ret, rows = DbManager.instance().querySQL( 
                            query = "INSERT INTO `%s` (date, user_id, duration, project_id, is_ts, is_tp, is_tu, is_tg, is_ta) VALUES ('%s',%s,%s,%s,%s,%s,%s,%s,%s)" 
                                % (self.dbt_writing, strDate, fromUser, writingDuration, prjId, isTs, isTp, isTu, isTg, isTa ) )
            if not ret:
                raise Exception("unable to add writing duration in db")
        except Exception as e:
            self.error( e )
            rlt = False
        self.__mutex__.release()
        return rlt

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="STM - %s" % txt)

###############################
StatsMng = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return StatsMng

def initialize ():
    """
    Instance creation
    """
    global StatsMng
    StatsMng = StatsManager()

def finalize ():
    """
    Destruction of the singleton
    """
    global StatsMng
    if StatsMng:
        StatsMng = None