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

	/*
	Delete a project
	*/
	function delproject( $pid) {
		global $db, $CORE, $RESTAPI, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-projects' );

        list($code, $details) = $RESTAPI->delProject($pid=intval($pid));
        
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
            $rsp["msg"] = lang('ws-project-deleted');
		}

		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	/*
	Add a project
	*/
	function addproject( $name ) {
		global $db, $CORE, $RESTAPI, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

        list($code, $details) = $RESTAPI->addProject($projectName=$name);
        
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
            $rsp["msg"] = lang('ws-project-added');
		}
		return $rsp;
	}

	/*
	Update a project
	*/
	function updateproject( $name, $pid ) {
		global $db, $RESTAPI, $CORE, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;


        list($code, $details) = $RESTAPI->renameProject( $projectName=mysql_real_escape_string($name), 
                                                         $projectId=intval($pid) );
        
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
            $rsp["msg"] = lang('ws-project-updated');
		}
		return $rsp;
	}

	
	/*
	Return the project according to the identifier passed as argument
	*/
	// function getprojectbyid($pid)
	// {
		// global $db, $CORE, $__LWF_DB_PREFIX;
		// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE  id=\''.mysql_real_escape_string($pid).'\';';
		// $rslt = $db->query( $sql_req );
		// if ( !$rslt ) 
		// {
			// return null;
		// } else {
			// if ( $db->num_rows($rslt) == 0 )
			// {
				// return false;
			// } else {
				// return $db->fetch_assoc($rslt);
			// }
		// }
	// }

	/*
	Return the project according to the name passed as argument
	*/
	// function getprojectbyname($name)
	// {
		// global $db, $CORE, $__LWF_DB_PREFIX;
		// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE  name=\''.mysql_real_escape_string($name).'\';';
		// $rslt = $db->query( $sql_req );
		// if ( !$rslt ) 
		// {
			// return null;
		// } else {
			// if ( $db->num_rows($rslt) == 0 )
			// {
				// return false;
			// } else {
				// return $db->fetch_assoc($rslt);
			// }
		// }
	// }
?>