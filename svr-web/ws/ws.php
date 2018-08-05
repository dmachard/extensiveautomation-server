<?php
	/*
	---------------------------------------------------------------
	 Copyright (c) 2010-2018 Denis Machard. All rights reserved.

	 This file is part of the extensive automation project; you can redistribute it and/or
	 modify it under the terms of the GNU General Public License, Version 3.

	 This file is distributed in the hope that it will be useful, but
	 WITHOUT ANY WARRANTY; without even the implied warranty of
	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
	 See the GNU General Public License for more details.
	 
	 You should have received a copy of the GNU General Public License,
	 along with this program. If not, see http://www.gnu.org/licenses/.
	---------------------------------------------------------------
	*/

	define('ROOT', './../');
	require ROOT.'include/common.php';

    // read cookie
    if ($__LWF_COOKIE_ENABLE)
    {
		read_cookie($CORE->profile);
		$CORE->check_cookie();
	}
	
	// authentication failed, request refused
	if ( $CORE->profile == null)
		response(403, lang('request denied') );

	// decode request
	$req = readRequest();
	$rsp = null;

	define('WS_OK', 1);

	// ws specific handler
	include "wsdispatch.php";

	if ( $rsp != null )
		response($rsp['code'], $rsp['msg'], $rsp['moveto']);
	else
		response(403, lang('denied'));

	function readRequest()
	{
		$raw = file_get_contents('php://input');
		$xml = simplexml_load_string($raw);
		$json = json_encode($xml);
		return  json_decode($json);
	}

	function response($code, $msg, $moveto=null)
	{
		header("Content-Type: text/xml");
		$rsp = "<?xml version=\"1.0\" encoding=\"utf-8\"?>";
		$rsp .= "<rsp><code>".$code."</code><msg>".htmlspecialchars($msg)."</msg>";
		if ( $moveto != null )
			$rsp .= "<moveto>".htmlentities($moveto)."</moveto>";
		$rsp .= "</rsp>";
		$rsp = utf8_encode($rsp); 
		die($rsp);
	}

	function empty_obj(&$object)
	{
		$obj = (array)$object;
		if (empty($obj))
			return true;
		return false;
	}

	function get_str_arg($arg)
	{
		return urldecode($arg);
	}
?>
