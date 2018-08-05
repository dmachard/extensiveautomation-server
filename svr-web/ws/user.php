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

	function changenotfisuser( $uid, $notifications ) {
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
        
        // update user through rest api
        list($code, $details) = $RESTAPI->updateUserNotifications(
                                                  $uid=intval($uid),
                                                  $notifications=$notifications
                                                  );
        
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
            $rsp["msg"] = lang('ws-user-updated');
        }
        return $rsp;
	}

	function resetpwduser( $uid ) {
		global $db, $CORE, $RESTAPI, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
		
		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );
        
		// reset password user through rest api
        list($code, $details) = $RESTAPI->resetPasswordUser($id=intval($uid));
        
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
            $rsp["msg"] = lang('ws-user-pwd-reseted');
            $rsp["moveto"] = $redirect_page_url;
		}
        
		return $rsp;	
	}

	function changepwduser( $uid, $oldpwd, $newpwd ) {
		global $db, $CORE, $RESTAPI, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
		
		if ( $CORE->profile['administrator'] ) {
			$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );
		} else {
			$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-profile' );
		}

		// update password user through rest api
        list($code, $details) = $RESTAPI->updatePasswordUser($id=intval($uid),
                                                             $oldpwd=$oldpwd, 
                                                             $newpwd=$newpwd);
        
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
            $rsp["msg"] = lang('ws-user-pwd-updated');
            $rsp["moveto"] = $redirect_page_url;
		}
        
		return $rsp;
	}

	function disconnectuser( $login ) {
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// disconnect user through rest api
        list($code, $details) = $RESTAPI->disconnectUser($login=$login);
        
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
            $rsp["msg"] = lang('ws-user-disconnected');
		}

		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	function enableuser( $uid, $status) {
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// disconnect user through rest api
        list($code, $details) = $RESTAPI->enableUser($id=intval($uid), 
                                                     $status=intval($status));
        
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
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// delete user through rest api
        list($code, $details) = $RESTAPI->deleteUser($id=intval($uid));
        
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
            $rsp["msg"] = lang('ws-user-deleted');
		}

        $rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

    function duplicateuser( $uid ) {
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('administration')."&s=".get_subpindex( 'administration', 'admin-users' );

		// delete user through rest api
        list($code, $details) = $RESTAPI->duplicateUser($id=intval($uid));
        
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
            $rsp["msg"] = lang('ws-user-duplicated');
		}

        $rsp["moveto"] = $redirect_page_url;
		return $rsp;
        
    }
    
	function adduser( $login, $password, $email, $admin, $monitor, $tester, 
                        $lang, $style, $notifications, $projects, $defaultproject) {
		global $db, $CORE, $RESTAPI, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
	
        $level = "tester";
        if ( strbool2int($admin) ) $level = "admin";
        if ( strbool2int($monitor) ) $level = "monitor";
        if ( strbool2int($tester) ) $level = "tester";

        // add user through rest api
        list($code, $details) = $RESTAPI->addUser($login=$login, 
                                                  $password=$password,
                                                  $email=$email, 
                                                  $level=$level,
                                                  $lang=$lang, 
                                                  $style=$style,
                                                  $notifications=$notifications,
                                                  $default=intval($defaultproject), 
                                                  $projects=explode( ';', $projects )
                                                  );
        
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
            $rsp["msg"] = lang('ws-user-added');
		}
		return $rsp;
	}

	function updateuser( $login, $email, $admin, $monitor, $tester, $lang, 
                         $style, $notifications, $projects, $defaultproject, 
                         $uid) {
		global $db, $CORE, $RESTAPI, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

        $level = "tester";
        if ( strbool2int($admin) ) $level = "admin";
        if ( strbool2int($monitor) ) $level = "monitor";
        if ( strbool2int($tester) ) $level = "tester";
        
        // update user through rest api
        list($code, $details) = $RESTAPI->updateUser(
                                                  $uid=intval($uid),
                                                  $login=$login, 
                                                  $email=$email, 
                                                  $level=$level,
                                                  $lang=$lang, 
                                                  $style=$style,
                                                  $notifications=$notifications,
                                                  $default=intval($defaultproject), 
                                                  $projects=explode( ';', $projects )
                                                  );
        
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
            $rsp["msg"] = lang('ws-user-updated');
        }
        return $rsp;
	}

	// function getuserbyid($uid){
		// global $db, $CORE, $__LWF_DB_PREFIX;
		// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE  id=\''.mysql_real_escape_string($uid).'\';';
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

	// function getuserbylogin($login){
		// global $db, $CORE, $__LWF_DB_PREFIX;
		// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE  login=\''.mysql_real_escape_string($login).'\';';
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
    
	// function getuserbylogin_expectuid($login, $uid){
		// global $db, $CORE, $__LWF_DB_PREFIX;
		// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE  login=\''.mysql_real_escape_string($login).'\' AND id!='.$uid.' ;';
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