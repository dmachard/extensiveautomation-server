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
		exit( 'access denied' );

	/*
	Delete a project
	*/
	function delproject( $pid) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-projects' );

		// not possible to delete default project common
		if ( $pid == 1) 
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('common-not-authorized');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		} 

		// check pid
		$project = getprojectbyid($pid);
		if ( $project == null || $project == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-project-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}

		// checking relation 
		$sql_req = 'SELECT COUNT(*) as nbrelation FROM `'.$__LWF_DB_PREFIX.'-relations-projects` WHERE project_id=\''.mysql_real_escape_string($pid).'\';';
		$rslt_relation = $db->query( $sql_req );
		if ( !$rslt_relation ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to count relation project with user")."(".$sql_req.")";
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		} else {
			$nb_relation = $db->fetch_assoc($rslt_relation);
			if ( $nb_relation['nbrelation'] ){
				$rsp["code"] = 603;
				$rsp["msg"] = 'The project '.$project['name'].' is linked with '.$nb_relation['nbrelation'].' users';
				return $rsp;
			}
		}
		
		// delete the folder
		$deleted = $XMLRPC->delProject($prjId=$pid);
		if ($deleted == null) {
			$rsp["code"] = 500;
			$rsp["msg"] = "Unable to delete project folder";
		} else {
			if ( $deleted ) {
				$rsp["msg"] = lang('ws-project-deleted');
				$rsp["code"] = 200;
			} else {
				$rsp["code"] = 500;
				$rsp["msg"] = "Unable to delete project folder";
			}
		}

		// delete project in db
		$sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE id=\''.$pid.'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to delete project")."(".$sql_req.")";
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		} 
		
		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	/*
	Add a project
	*/
	function addproject( $name ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		// check if the name is not already used
		$ret = getprojectbyname($name);
		if ( $ret )
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('ws-project-duplicate-1').$name.lang('ws-project-duplicate-2');
			return $rsp;
		}

		// check the license
		$CORE->read_license();
		if ( $CORE->license == null ) {
			$rsp["code"] = 603;
			$rsp["msg"] = $CORE->license_error;
			return $rsp;
		} 

		$sql_req = 'SELECT count(*) as nb FROM `'.$__LWF_DB_PREFIX.'-projects`;';
		$rslt = $db->query( $sql_req ) ;
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to count projects")."(".$sql_req.")";
			return $rsp;
		} else {
			$cur_u = $db->fetch_assoc($rslt);
			if ( $cur_u['nb'] >= $CORE->license['projects'] ){
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit for project is reached';
				return $rsp;
			}
		}

		// this name is free then create project
		$active = 1;
		$sql_req = 'INSERT INTO `'.$__LWF_DB_PREFIX.'-projects`(`name`, `active` ) VALUES(\''.mysql_real_escape_string($name).'\', \''.$active.'\');';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to add project")."(".$sql_req.")";
			return $rsp;
		} 

		$p = getprojectbyname(mysql_real_escape_string($name));
		if ( $p == null || $p == false)
		{
			$rsp["code"] = 500;
			$rsp["msg"] = "Unable to get project id";
			return $rsp;
		}

		$added =  $XMLRPC->addProject($prjId=$p['id']);
		if ($added == null) {
			$rsp["code"] = 500;
			$rsp["msg"] = "Unable to create project folder";
		} else {
			if ($added) {
				$rsp["msg"] = lang('ws-project-added');
				$rsp["code"] = 200;
			} else {
				$rsp["code"] = 500;
				$rsp["msg"] = "Unable to create project folder";
			}
		}
		return $rsp;
	}

	/*
	Update a project
	*/
	function updateproject( $name, $pid ) {
		global $db, $CORE, $XMLRPC, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$project = getprojectbyid($pid);
		if ( $project == null || $project == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-project-not-found');
			return $rsp;
		} 

		$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-projects` SET name=\''.mysql_real_escape_string($name).'\' WHERE id=\''.$pid.'\';';
		$rslt = $db->query( $sql_req ) ;
		
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to update project")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-project-updated');
		}
		
		return $rsp;
	}

	
	/*
	Return the project according to the identifier passed as argument
	*/
	function getprojectbyid($pid)
	{
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE  id=\''.mysql_real_escape_string($pid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			return null;
		} else {
			if ( $db->num_rows($rslt) == 0 )
			{
				return false;
			} else {
				return $db->fetch_assoc($rslt);
			}
		}
	}

	/*
	Return the project according to the name passed as argument
	*/
	function getprojectbyname($name)
	{
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE  name=\''.mysql_real_escape_string($name).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			return null;
		} else {
			if ( $db->num_rows($rslt) == 0 )
			{
				return false;
			} else {
				return $db->fetch_assoc($rslt);
			}
		}
	}
?>