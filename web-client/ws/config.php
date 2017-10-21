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

	if (!defined('WS_OK'))
		exit( lang('access denied') );

	//
	// Update table configuration 
	//
	function updatecfg ( $key, $value ) {
		global $db, $TAS, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-config SET value=\''.mysql_real_escape_string($value).'\' WHERE opt=\''.mysql_real_escape_string($key).'\';';
		$rslt = $db->query( $sql_req ) ;
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to update configuration")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-config-updated');
		}
		return $rsp;
	}
?>