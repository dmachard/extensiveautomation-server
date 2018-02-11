<?php
    /*
	---------------------------------------------------------------
	 Copyright (c) 2010-2018 Denis Machard. All rights reserved.

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

    class CORE {
        var $pwd_hash;
        var $user;
        function CORE(){
            $this->reset_ctx();
        }
        function reset_ctx() {
                $this->pwd_hash = null;
                $this->profile = null;
                $this->license = null;
                $this->license_error = null;
        }
        function login($login, $password){
            global $db, $__LWF_CFG, $__LWF_APP_SALT, $__LWF_DB_PREFIX;
        
            $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE login=\''.strip_tags( addslashes($login)).'\' AND active=1 AND web=1';
            $result = $db->query($sql_req) or fatal( 'login', 'Unable to read user ('.$sql_req.'): '.$db->error() );
            if (! $db->num_rows($result))
                return 0;

            $cur_u = $db->fetch_assoc($result);
            $hash_pwd_computed = sha1($__LWF_CFG['misc-salt'].sha1($password));


            if ( $hash_pwd_computed !=  $cur_u['password'])
            {
                return 0;
            }

            // login ok
            $this->profile = $cur_u;
            // save the hash of the user password without the salt in the cookie
            // use by the xml api
            $this->profile['user-password'] = sha1($password);
   
            //del_cookie($this->profile);
            set_cookie($this->profile);
            return 1;
        }
        
        function logout(){
                del_cookie($this->profile);
                $this->reset_ctx();
        }
        
        function check_cookie(){
            global $db, $__LWF_CFG, $__LWF_DB_PREFIX;

            $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE password=\''.$this->profile['password'].'\' AND login=\''.strip_tags( addslashes($this->profile['login'])).'\' AND active=1';
            $result = $db->query($sql_req) or fatal('check_cookie', 'Unable to find user ('.$sql_req.'): '.$db->error());
            if (! $db->num_rows($result) )
                    $this->reset_ctx();
            else
            {
                    # save user password hash from cookie, this hash does not exist on the server, only on the cookie
                    $user_pass = $this->profile['user-password'];
                    $cur_u = $db->fetch_assoc($result);
                    $this->profile = $cur_u;
                    # add a second time the hash password, used for the xml api
                    $this->profile['user-password'] = $user_pass;
            }
        }
    }

    global $CORE;
    $CORE = new CORE();
?>
