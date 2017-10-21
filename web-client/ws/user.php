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

	function licencereached($level, $uid=null) {
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT count(*) as nb FROM `'.$__LWF_DB_PREFIX.'-users` WHERE '.$level.'=1';
		if ( $uid != null) {
			$sql_req .= ' AND id <> \''.$uid.'\';';
		}
		$sql_req .= ';';
		$rslt = $db->query( $sql_req ) ;
		if ( !$rslt ) 
		{
			return -1;
		} else {
			$cur_u = $db->fetch_assoc($rslt);
			if ( $CORE->license['users'][$level] == 'UNLIMITED' ) {
				return false;
			}
			if ( $cur_u['nb'] >= $CORE->license['users'][$level] ){
				return true;
			}
		}
		return false;
	}

	function changenotfisuser( $uid, $notifications ) {
		global $db, $CORE, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		// check uid
		if ( ! $CORE->profile['administrator'] ) {
			if ( $CORE->profile['id'] != $uid ) {
				$rsp["code"] = 603;
				$rsp["msg"] = lang('request denied');
				return $rsp;
			}
		}	

		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			return $rsp;
		} 

		// notifications
		$regex = '/^(((true)|(false));){7}/'; 
		if ( !preg_match($regex, $notifications) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 

		// update db
		$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-users` SET notifications=\''.$notifications.'\'  WHERE id=\''.$uid.'\';';
		$rslt = $db->query( $sql_req ) ;
		
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to update notifications user")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-user-updated');
		}
		
		return $rsp;
	}

	function resetpwduser( $uid ) {
		global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
		
		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// check uid
		if ( $CORE->profile['administrator'] != 1 ) {
			$rsp["code"] = 603;
			$rsp["msg"] = lang('request denied');
			return $rsp;
		}		

		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			return $rsp;	
		}	

		// update password
		$resetpwd = '';
		$reset_pwd_sha = sha1($__LWF_CFG['misc-salt'].sha1($resetpwd));
		$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-users` SET password=\''.$reset_pwd_sha.'\' WHERE id=\''.$uid.'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to reset user password")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-user-pwd-reseted');
			$rsp["moveto"] = $redirect_page_url;
		}

		return $rsp;	
	}

	function changepwduser( $uid, $oldpwd, $newpwd ) {
		global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
		
		if ( $CORE->profile['administrator'] ) {
			$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );
		} else {
			$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-profile' );
		}

		// check uid
		if ( $CORE->profile['administrator'] != 1 ) {
			if ( $CORE->profile['id'] != $uid ) {
				$rsp["code"] = 603;
				$rsp["msg"] = lang('request denied');
				return $rsp;
			}
		}		

		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			return $rsp;	
		}	

		// check password
		$old_pwd_sha = sha1($__LWF_CFG['misc-salt'].sha1($oldpwd));
		if ( $old_pwd_sha != $user['password'])
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('ws-user-wrong-old-pwd');
			return $rsp;
		} 

		// update password
		$new_pwd_sha = sha1($__LWF_CFG['misc-salt'].sha1($newpwd));
		$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-users` SET password=\''.$new_pwd_sha.'\' WHERE id=\''.$uid.'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to update user password")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-user-pwd-updated');
			$rsp["moveto"] = $redirect_page_url;
		}

		return $rsp;	
	}

	function disconnectuser( $login ) {
		global $db, $CORE, $XMLRPC, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// check if login is exist
		$user = getuserbylogin($login);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}

		// disconnect user through xmlrpc
		$disconnect =  $XMLRPC->disconnectUser($login);
		if ( is_null($disconnect) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = "Unable to disconnect user";
		} else {
			if ( $disconnect ) {
				$rsp["code"] = 200;
				$rsp["msg"] = lang('ws-user-disconnected');
			} else {
				$rsp["code"] = 500;
				$rsp["msg"] = "Unable to disconnect user";
			}
		}

		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	function enableuser( $uid, $status) {
		global $db, $CORE, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// not possible to disable default users
		//if ( $uid <= 6)  
		//{
		//	$rsp["code"] = 603;
		//	$rsp["msg"] = lang('common-not-authorized');
		//	$rsp["moveto"] = $redirect_page_url;
		//	return $rsp;
		//}

		// check uid
		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}

		// update user
		$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-users` SET active=\''.mysql_real_escape_string($status).'\' WHERE id=\''.mysql_real_escape_string($uid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to enable/disable user")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			if ( mysql_real_escape_string($status) == "1" )
			{
				$rsp["msg"] = lang('ws-user-enabled');
			} else {
				$rsp["msg"] = lang('ws-user-disabled');
			}
		}

		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	function deluser( $uid) {
		global $db, $CORE, $XMLRPC, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// not possible to delete default users
		if ( $uid <= 4) 
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('common-not-authorized');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		} 

		// check uid
		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}

		// him self deletion deny
		if ( $CORE->profile['login'] == $user['login'] )
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('common-not-authorized');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}

		// disconnect user through xmlrpc
		$disconnect =  $XMLRPC->disconnectUser($user['login']);

		// delete user
		$sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-users` WHERE id=\''.mysql_real_escape_string($uid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to delete user")."(".$sql_req.")";
			return $rsp;
		} 
		
		// delete relation
		$sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-relations-projects` WHERE user_id=\''.mysql_real_escape_string($uid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to delete user relations with project")."(".$sql_req.")";
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-user-deleted');
		}

		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

    function duplicateuser( $uid ) {
		global $db, $CORE, $XMLRPC, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );
        
		// check uid
		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}
        
        // get random id
        $uniq = uniqid();

        $is_admin=false;
        $is_leader=false;
        $is_tester=false;
        $is_developer=false;
        if($user['administrator'] == 1) $is_admin = "true";
        if($user['leader'] == 1) $is_leader = "true";
        if($user['tester'] == 1) $is_tester = "true";
        if($user['developer'] == 1) $is_developer = "true";
        
        // create the duplication, default project not duplicated
        $rsp = adduser($login=$user['login'].'-COPY#'.$uniq, $password=$user['password'], $email=$user['email'], $admin=$is_admin, $leader=$is_leader, 
                    $tester=$is_tester, $developer=$is_developer, $lang=$user['lang'], $style=$user['style'], 
                    $notifications=$user['notifications'], $projects="1", $defaultproject="1", 
                    $cli=$user['cli'], $gui=$user['gui'], $web=$user['web']);
        // duplicate project
        // todo
        
        // change the user message
        if ( $rsp["code"] == 200 ) {
			$rsp["msg"] = lang('ws-user-duplicated');
		}
		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
    }
    
	function adduser( $login, $password, $email, $admin, $leader, $tester, $developer, $lang, $style, $notifications, $projects, $defaultproject, $cli, $gui, $web ) {
		global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		//projects format: 22;32;23;22
		$regex = '/^(\d+;)*(\d+)\z/'; 
		if ( !preg_match($regex, $projects) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 
		# starts with 1
		$regex = '/(^1\z|^1;(.*))/'; 
		if ( !preg_match($regex, $projects) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 

		$projects_exploded = explode( ';', $projects );
		$defprj_found = false;
		for($i = 0; $i < count($projects_exploded); ++$i) {
			if ( intval($projects_exploded[$i])	== intval($defaultproject) ) { $defprj_found = true; }
		}
		if ( !$defprj_found ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('ws-project-bad-default'); 
			return $rsp;
		} 

		// check if login is not already used
		$ret = getuserbylogin($login);
		if ( $ret )
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('ws-user-duplicate-1').$login.lang('ws-user-duplicate-2');
			return $rsp;
		}

		// lang
		if ( ! in_array( $lang, get_installed_lang() ) ) 
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-lang-unknown');
			return $rsp;
		}

		// style
		if ( ! in_array( $style, get_installed_style() ) ) 
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-style-unknown');
			return $rsp;
		}


		// check the license
		$CORE->read_license();
		if ( $CORE->license == null ) {
			$rsp["code"] = 603;
			$rsp["msg"] = $CORE->license_error;
			return $rsp;
		} 

        // set default values
        if ( !strbool2int($admin) and !strbool2int($leader) and !strbool2int($tester) and !strbool2int($developer) ) {
            $tester = "true";
        }
        if ( !strbool2int($cli) and !strbool2int($gui) and !strbool2int($web) ) {
            $gui = "true";
            $web = "true";
        }
        
		if ( strbool2int($admin) ) {
			$reached = licencereached($level="administrator");
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count administrator users");
				return $rsp;
			} elseif ($reached) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for administrator';
				return $rsp;
			}
		}

		if ( strbool2int($leader) ) {
			$reached = licencereached($level="leader");
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count leader users");
				return $rsp;
			} elseif ($reached) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for leader';
				return $rsp;
			}
		}

		if ( strbool2int($tester) ) {
			$reached = licencereached($level="tester");
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count tester users");
				return $rsp;
			} elseif ($reached == true) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for tester';
				return $rsp;
			}
		}

		if ( strbool2int($developer) ) {
			$reached = licencereached($level="developer");
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count developer users");
				return $rsp;
			} elseif ($reached) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for developer';
				return $rsp;
			}
		}

		// notifications
		$regex = '/^(((true)|(false));){7}/'; 
		if ( !preg_match($regex, $notifications) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 
		
		// this login is free then create user
		$active = 1;
		$default = 0;
		$online = 0;
		$system = 0;
		$pwd_sha = sha1($__LWF_CFG['misc-salt'].sha1($password));

		$sql_req = 'INSERT INTO `'.$__LWF_DB_PREFIX.'-users`(`login`, `password`, `administrator`, `leader`, `tester`, `developer`, `system`, `email`, `lang`, `style`, `active`, `default`, `online`, `notifications`, `defaultproject`, `cli`, `gui`, `web`) VALUES(\''.mysql_real_escape_string($login).'\',\''.$pwd_sha.'\',\''.strbool2int($admin).'\',\''.strbool2int($leader).'\',\''.strbool2int($tester).'\',\''.strbool2int($developer).'\',\''.$system.'\',\''.mysql_real_escape_string($email).'\',\''.$lang.'\',\''.$style.'\',\''.$active.'\',\''.$default.'\',\''.$online.'\',\''.$notifications.'\',\''.$defaultproject.'\',\''.strbool2int($cli).'\',\''.strbool2int($gui).'\',\''.strbool2int($web).'\');';

		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to add user")."(".$sql_req.")";
			return $rsp;
		} 
		
		// get user id 
		$user = getuserbylogin(mysql_real_escape_string($login));
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to get the new user id")."(".$sql_req.")";
			return $rsp;
		} 

		// update relations
		$sql_req = 'INSERT INTO `'.$__LWF_DB_PREFIX.'-relations-projects`(`user_id`, `project_id`) VALUES';
		for($i = 0; $i < count($projects_exploded); ++$i) {
			$sql_req .= ' (\''.$user['id'].'\', \''.$projects_exploded[$i].'\' )';
			if ( $i < ( count($projects_exploded) -1) ) { $sql_req .= ', '; }
		}
		$sql_req .= ';';

		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to add relations")."(".$sql_req.")";
			return $rsp;
		} 
		else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-user-added');
		}
		
		
		return $rsp;
	}

	function updateuser( $login, $email, $admin, $leader, $tester, $developer, $lang, $style, $notifications, $projects, $defaultproject, $uid, $cli, $gui, $web ) {
		global $db, $CORE, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		//projects 
		// 22;32;23;22
		$regex = '/^(\d+;)*(\d+)\z/'; 
		if ( !preg_match($regex, $projects) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 
		# starts with 1
		$regex = '/(^1\z|^1;(.*))/'; 
		if ( !preg_match($regex, $projects) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 
		$projects_exploded = explode( ';', $projects );
		$defprj_found = false;
		for($i = 0; $i < count($projects_exploded); ++$i) {
			if ( intval($projects_exploded[$i])	== intval($defaultproject) ) { $defprj_found = true; }
		}
		if ( !$defprj_found ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('ws-project-bad-default'); 
			return $rsp;
		} 

		$user = getuserbyid($uid);
		if ( $user == null || $user == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-not-found');
			return $rsp;
		} 

		// lang
		if ( ! in_array( $lang, get_installed_lang() ) ) 
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-lang-unknown');
			return $rsp;
		}

		// style
		if ( ! in_array( $style, get_installed_style() ) ) 
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-user-style-unknown');
			return $rsp;
		}

		// check if login is not already used
		$ret = getuserbylogin_expectuid($login, $uid);
		if ( $ret )
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('ws-user-duplicate-1').$login.lang('ws-user-duplicate-2');
			return $rsp;
		}

		// check the license
		$CORE->read_license();
		if ( $CORE->license == null ) {
			$rsp["code"] = 603;
			$rsp["msg"] = $CORE->license_error;
			return $rsp;
		} 

		if ( strbool2int($admin) ) {
			$reached = licencereached($level="administrator", $uid=$uid);
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count administrator users");
				return $rsp;
			} elseif ($reached) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for administrator';
				return $rsp;
			}
		}

		if ( strbool2int($leader) ) {
			$reached = licencereached($level="leader", $uid=$uid);
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count leader users");
				return $rsp;
			} elseif ($reached) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for leader';
				return $rsp;
			}
		}

		if ( strbool2int($tester) ) {
			$reached = licencereached($level="tester", $uid=$uid);
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count tester users");
				return $rsp;
			} elseif ($reached == true) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for tester';
				return $rsp;
			}
		}

		if ( strbool2int($developer) ) {
			$reached = licencereached($level="developer", $uid=$uid);
			if ( $reached === -1) {
				$rsp["code"] = 500;
				$rsp["msg"] = $db->str_error("Unable to count developer users");
				return $rsp;
			} elseif ($reached) {
				$rsp["code"] = 603;
				$rsp["msg"] = 'The license limit is reached for developer';
				return $rsp;
			}
		}


		// notifications
		$regex = '/^(((true)|(false));){7}/'; 
		if ( !preg_match($regex, $notifications) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = lang('common-not-authorized'); 
			return $rsp;
		} 

		// not possible to change group id for the default users
		if ( $uid >= 6 )
			$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-users` SET  login=\''.mysql_real_escape_string($login).'\', administrator=\''.strbool2int($admin).'\', leader=\''.strbool2int($leader).'\', tester=\''.strbool2int($tester).'\', developer=\''.strbool2int($developer).'\', email=\''.mysql_real_escape_string($email).'\', lang=\''.$lang.'\', style=\''.$style.'\', notifications=\''.$notifications.'\', defaultproject=\''.$defaultproject.'\', cli=\''.strbool2int($cli).'\', gui=\''.strbool2int($gui).'\', web=\''.strbool2int($web).'\' WHERE id=\''.$uid.'\';';
		else
			$sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-users` SET email=\''.mysql_real_escape_string($email).'\', lang=\''.$lang.'\', style=\''.$style.'\', notifications=\''.$notifications.'\', defaultproject=\''.$defaultproject.'\' WHERE id=\''.$uid.'\';';
		$rslt = $db->query( $sql_req ) ;
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to update user")."(".$sql_req.")";
			return $rsp;
		}

		// delete relation to update it
		$sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-relations-projects` WHERE user_id=\''.mysql_real_escape_string($uid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to delete user relations with project")."(".$sql_req.")";
			return $rsp;
		} 
		
		// update relations
		$sql_req = 'INSERT INTO `'.$__LWF_DB_PREFIX.'-relations-projects`(`user_id`, `project_id`) VALUES';
		for($i = 0; $i < count($projects_exploded); ++$i) {
			$sql_req .= ' (\''.$uid.'\', \''.$projects_exploded[$i].'\' )';
			if ( $i < ( count($projects_exploded) -1) ) { $sql_req .= ', '; }
		}
		$sql_req .= ';';

		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to add relations on update")."(".$sql_req.")";
			return $rsp;
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-user-updated');
		}
		
		return $rsp;
	}

	function getuserbyid($uid){
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE  id=\''.mysql_real_escape_string($uid).'\';';
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

	function getuserbylogin($login){
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE  login=\''.mysql_real_escape_string($login).'\';';
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
    
	function getuserbylogin_expectuid($login, $uid){
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE  login=\''.mysql_real_escape_string($login).'\' AND id!='.$uid.' ;';
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