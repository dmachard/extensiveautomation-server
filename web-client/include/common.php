<?php
	/*
	---------------------------------------------------------------
	 Copyright (c) 2010-2017 Denis Machard. All rights reserved.

	 This file is part of the extensive testing project; you can redistribute it and/or
	 modify it under the terms of the GNU General Public License, Version 3.

	 This file is distributed in the hope that it will be useful, but
	 WITHOUT ANY WARRANTY; without even the implied warranty of
	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
	 See the GNU General Public License for more details.
	 
	 You should have received a copy of the GNU General Public License,
	 along with this program. If not, see http://www.gnu.org/licenses/.
	---------------------------------------------------------------
	*/

	// Make sure PHP reports all errors except E_NOTICE.
	error_reporting(E_ALL);

	// load config, exit if missing
	require ROOT.'include/config.php';
	if (!defined('CONFIG_OK')) exit('The file config.php is missing');

	// default time zone
	date_default_timezone_set($__LWF_TIMEZONE);
	setlocale(LC_TIME, $__LWF_TIMELOCALE);

	// load general functions
	require ROOT.'include/functions.php';
	
	// load db adaptor
	if ($__LWF_DB_ENABLE && $__LWF_DB_TYPE == "mysql")
	{
		require ROOT.'include/dblayer.php';
		// create the database adapter object (and open/connect to/select db)
		$db = new DBLayer($__LWF_DB_HOST, $__LWF_DB_USER, $__LWF_DB_PWD, $__LWF_DB_CONNECT);
		$db->usedb($__LWF_DB_NAME);
		// load all configs
		$__LWF_CFG = array();
		loadcfg();
	}

    #if (!array_key_exists("server-level-admin",$__LWF_CFG)) {
    #    exit('The dynamic configuration is missing');
    #}
    
	// define users constant
	define('ADMINISTRATOR',		$__LWF_CFG['server-level-admin']	);
	define('TESTER',			$__LWF_CFG['server-level-tester']	);
	define('LEADER',			$__LWF_CFG['server-level-leader']	); 
	define('DEVELOPER',			$__LWF_CFG['server-level-developer']	);
	define('SYSTEM',			$__LWF_CFG['server-level-system']	);

	define('COMPLETE',		"COMPLETE");
	define('ERROR',			"ERROR");
	define('KILLED',		"KILLED");
	define('CANCELLED',		"CANCELLED");

	define('PASS',			"PASS");
	define('FAIL',			"FAIL");
	define('UNDEFINED',		"UNDEFINED");

	define('RUNUNDEFINED',	"UNDEFINED");
	define("NOW",			"NOW");
	define("AT",			"AT");
	define("IN",			"IN");
	define("EVERYSECOND",	"EVERY_SECOND");
	define("EVERYMINUTE",	"EVERY_MINUTE");
	define("EVERYHOUR",		"EVERY_HOUR");
	define("HOURLY",		"HOURLY");
	define("DAILY",			"DAILY");
	define("WEEKLY",		"WEEKLY");
	define("SUCCESSIVE",	"SUCCESSIVE");
    
	define("TAX",	"tax");
	define("TUX",	"tux");
	define("TSX",	"tsx");
	define("TPX",	"tpx");
	define("TGX",	"tgx");
	define("TDX",	"tdx");
	define("TCX",	"tcx");
	define("PNG",	"png");
	define("ZIP",	"zip");
	define("TRX",	"trx");
    
	define("DEFAULT_PROJECT",	1);

	// run type
	$RUN_TYPE = array(
		-2		=> "UNDEFINED",
		-1		=> "NOW",
		0		=> "AT",
		1		=> "IN",
		2		=> "EVERY_SECOND",
		3		=> "EVERY_MINUTE",
		4		=> "HOURLY",
		5		=> "DAILY",
		6		=> "EVERY_HOUR",
		7		=> "WEEKLY",
		8		=> "SUCCESSIVE"
	);
	
	// define constant
	define('SCRIPT', 'sc');
	define('TESTABSTRACT', 'ta');
	define('TESTGLOBAL', 'tg');
	define('TESTPLAN', 'tp');
	define('TESTSUITE',  'ts');
	define('TESTUNIT',  'tu');
	define('TESTCASE',  'tc');

	// just to support php 5.1, not nice at all
	if (!function_exists('json_decode')) {
		function json_decode($content, $assoc=false) {
						require_once ROOT.'include/JSON.php';
						if ($assoc) {
								$json = new Services_JSON(SERVICES_JSON_LOOSE_TYPE);
						}
						else {
								$json = new Services_JSON;
						}
						return $json->decode($content);
		}
     }

     if (!function_exists('json_encode')) {
          function json_encode($content) {
              require_once ROOT.'include/JSON.php';
              $json = new Services_JSON;
              return $json->encode($content);
          }
     }

	// load xmlrpc lib
	include( ROOT."include/xmlrpclib/xmlrpc.inc");

	// load app functions
	require ROOT.'include/core.php';

	// load app functions
	require ROOT.'include/corexmlrpc.php';
    
	$AUTH_RET = -1;
	// authenticate the client
	if ( isset($_POST['form_sent_login']) &&  $_POST['form_sent_login'] == 1)
	{
		if ( isset($_POST['req_login']) && $_POST['req_login'] != null &&  isset($_POST['req_passwd']) )
		{
			if (array_key_exists('misc-salt', $__LWF_CFG)) {
                $AUTH_RET = $CORE->login($_POST['req_login'], $_POST['req_passwd']);	
			} else {
				$AUTH_RET = 2; # server error, not correctly started ?
			}
		}
	} else {
		if ($__LWF_COOKIE_ENABLE)
		{
			read_cookie($CORE->profile);
			$CORE->check_cookie();
		}
	}

	// load language specific to the user profile
	if ( $CORE->profile != null )
	{
		require ROOT.'lang/'.$CORE->profile['lang'].'.php';
	}
	else 
	{
		// load default language, define in config.php
		require ROOT.'lang/'.$__LWF_APP_DFLT_LANG.'.php';
	}

	$__DEF_PAGES = array(	
				lang('overview'),
				lang('tests'),
				lang('administration'),
				lang('system'),
				lang('about')
	);

	$__DEF_SUB_PAGES = array( 
				array( lang('overview-index'), lang('overview-download'), lang('overview-docs'), lang('overview-agents'), lang('overview-probes')  ),
				array( lang('tests-repository'), lang('tests-result'), lang('test-environment'), lang('tests-my-statistic'), lang('tests-statistics'), lang('tests-history') ),
				array( lang('admin-profile'), lang('admin-users'), lang('admin-projects'), lang('admin-license'), lang('admin-config') ),
				array( lang('system-status'), lang('system-description'), lang('system-usage') ),
				array( lang('about-description'), lang('about-release-notes'), lang('about-licenses')  )
	);
	
?>
