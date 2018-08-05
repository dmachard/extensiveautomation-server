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

	if (!defined('WS_OK'))
		exit( 'access denied' );


	function disconnectprobe( $name ) {
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		$redirect_page_url = "./index.php?p=".get_pindex('overview')."&s=".get_subpindex( 'overview', 'overview-probes' );

		// disconnect agent through rest api
        list($code, $details) = $RESTAPI->disconnectAgent($name=$name);
        
        $rsp["code"] = 500;
		if ($code == 401) {
			$rsp["msg"] = $details;
		} elseif ($code == 400) {
			$rsp["msg"] = $details;
		} elseif ($code == 500) {
			$rsp["msg"] = $details;
		} elseif ($code == 403) {
			$rsp["msg"] = $details;
		} elseif ($code == 404) {
			$rsp["msg"] = $details;
		} else {
            $rsp["code"] = 200;
            $rsp["msg"] = lang('ws-probe-disconnected');
		}


		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}
?>