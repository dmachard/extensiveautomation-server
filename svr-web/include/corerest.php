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

    
    class INTERFACE_REST{

        function INTERFACE_REST(){
        }
        
        // Decode data base64 -> zlib -> json
        function decodeData($data, $json=True){
            $b64data =  base64_decode( $data );
            $uncompressed = gzuncompress( $b64data );
            if ($json) {
                $ret = json_decode( $uncompressed );
            } else {
                $ret = $uncompressed;
            }
            return $ret;
        }
        
        function getRestClient($method, $uri, $json, $headers){
            global $__LWF_CFG;

            $url = "http://".$__LWF_CFG['bind-ip-rsi'].":".$__LWF_CFG['bind-port-rsi'];
 
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url.$uri);
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers );
            curl_setopt($ch, CURLOPT_POSTFIELDS, $json);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            
            $response =  json_decode(curl_exec($ch),true);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); 
            curl_close ($ch) ;
            return array($code,$response) ;
        }
        
        function renameProject($projectName, $projectId){
            global $__LWF_CFG, $CORE;

            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];

            // add project
            $req = json_encode( array('project-name' => $projectName, 'project-id' => $projectId) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/projects/rename", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
            
        }
        
        function addProject($projectName){
            global $__LWF_CFG, $CORE;

            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];

            // add project
            $req = json_encode( array('project-name' => $projectName) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/projects/add", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
            
        }
        
        function delProject($pid) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // remove project
            $req = json_encode( array('project-id' => $pid) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/projects/remove", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function addVariable($pid, $name, $value) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // add variable
            $req = json_encode( array('project-id' => $pid,
                                      'variable-name' => $name,
                                      'variable-value' => $value) );
            list($code, $rsp) = $this->getRestClient("POST", "/variables/add", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function deleteVariable($pid, $id) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // delete variable
            $req = json_encode( array('project-id' => $pid,
                                      'variable-id' => $id) );
            list($code, $rsp) = $this->getRestClient("POST", "/variables/remove", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function duplicateVariable($pid, $id) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // duplicate variable
            $req = json_encode( array('project-id' => $pid,
                                      'variable-id' => $id) );
            list($code, $rsp) = $this->getRestClient("POST", "/variables/duplicate", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function updateVariable($pid, $id, $name, $value) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // update variable
            $req = json_encode( array('project-id' => $pid,
                                      'variable-id' => $id,
                                      'variable-name' => $name,
                                      'variable-value' => $value) );
            list($code, $rsp) = $this->getRestClient("POST", "/variables/update", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function disconnectUser($login) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            //disconnect user
            $req = json_encode( array('login' => $login) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/channel/disconnect", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }

        function enableUser($id, $status) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // set status
            $req = json_encode( array('user-id' => $id, 'enabled' => $status) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/status", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function deleteUser($id) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // delete user
            $req = json_encode( array('user-id' => $id) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/remove", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function duplicateUser($id) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // delete user
            $req = json_encode( array('user-id' => $id) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/duplicate", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function resetPasswordUser($id) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // delete user
            $req = json_encode( array('user-id' => $id) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/password/reset", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function updatePasswordUser($id, $oldpwd, $newpwd) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // delete user
            $req = json_encode( array('user-id' => $id,
                                      'current-password' => $oldpwd,
                                      'new-password' => $newpwd) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/password/update", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function addUser($login, $password, $email, $level, $lang, $style, $notifications, $default, $projects) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // delete user
            $req = json_encode( array('login' => $login,
                                      'password' => $password,
                                      'level' => $level, 
                                      'email' => $email,
                                      'lang' => $lang,
                                      'style' => $style,
                                      'notifications' => $notifications,
                                      'default' => $default,
                                      'projects' => $projects) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/add", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        function updateUser($uid, $login, $email, $level, $lang, 
                            $style, $notifications, $default, $projects) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // update user
            $req = json_encode( array('user-id' => $uid,
                                      'login' => $login,
                                      'level' => $level, 
                                      'email' => $email,
                                      'lang' => $lang,
                                      'style' => $style,
                                      'notifications' => $notifications,
                                      'default' => $default,
                                      'projects' => $projects) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/update", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        
        function updateUserNotifications($uid, $notifications) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // update user notifications
            $req = json_encode( array('user-id' => $uid,
                                      'notifications' => $notifications) );
            list($code, $rsp) = $this->getRestClient("POST", "/administration/users/update", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }
        
        
        function disconnectAgent($name) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            //disconnect user
            $req = json_encode( array('agent-name' => $name) );
            list($code, $rsp) = $this->getRestClient("POST", "/agents/disconnect", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }   
        
        function disconnectProbe($name) {
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            //disconnect user
            $req = json_encode( array('probe-name' => $name) );
            list($code, $rsp) = $this->getRestClient("POST", "/probes/disconnect", 
                                                     $req, 
                                                     array("Content-Type: appplication/json",
                                                           "Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp);
        }     
        
        function getRunningAgents(){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get running agents
            list($code, $rsp2) = $this->getRestClient("GET", "/agents/running", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);
        }
        
        function getRunningProbes(){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get running agents
            list($code, $rsp2) = $this->getRestClient("GET", "/probes/running", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);
        }
        
        function getReleaseNotes(){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            list($code, $rsp2) = $this->getRestClient("GET", "/system/about", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2['about']['changelogs']);
        }  
        
        function getServerVersions(){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            list($code, $rsp2) = $this->getRestClient("GET", "/system/about", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2['about']['version']);
        }  
        
        function getServerUsages(){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get usages
            list($code, $rsp2) = $this->getRestClient("GET", "/system/usages", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2['usages']['disk']);
        }  
        
        function getServerStatus(){
                        global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get server status
            list($code, $rsp2) = $this->getRestClient("GET", "/system/status", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);        
        }
            
        function getFilesTests($prjId){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            $req = json_encode( array('project-id' => $prjId) );
            list($code, $rsp2) = $this->getRestClient("POST", "/tests/listing", $req, 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2['listing']);
        }  
        
        function getStatisticsTests($prjId){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            $req = json_encode( array('project-id' => $prjId) );
            list($code, $rsp2) = $this->getRestClient("POST", "/tests/statistics", $req, 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2['statistics']);
        } 
            
        function getFilesTestResults($prjId){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            $req = json_encode( array('project-id' => $prjId) );
            list($code, $rsp2) = $this->getRestClient("POST", "/results/listing/files", $req, 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2['listing']);
        }  
        
        function getTestPreview($prjId, $testId){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            $req = json_encode( array('project-id' => $prjId, 'test-id' => $testId) );
            list($code, $rsp2) = $this->getRestClient("POST", "/results/report/reviews", $req, 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);
        } 
        
        function refreshTestEnvironment($prjId, $testId){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // get releases notes
            list($code, $rsp2) = $this->getRestClient("GET", "/session/context/notify", "", 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);
        }  

        function runTest($prjId, $extension, $filename, $path ){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // run test
            $req = json_encode( array('project-id' => intval($prjId), 
                                      'test-definition' => '',
                                      'test-execution' => '',
                                      'test-properties' => '',
                                      'test-extension' => $extension,
                                      'test-path' => $path,
                                      'test-name' => $filename,
                                      'schedule-id' => -1,
                                      'schedule-at' => array( 0, 0, 0, 0, 0, 0 ) ) );
            list($code, $rsp2) = $this->getRestClient("POST", "/tests/schedule", $req, 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);
        }
        
        function runTestTpg($prjId, $extension, $filename, $path ){
            global $__LWF_CFG, $CORE;
            
            // login
            $req = json_encode( array('login' => $CORE->profile['login'], 
                                      'password' => $CORE->profile['user-password']) );
            list($code, $rsp) = $this->getRestClient("POST", "/session/login", 
                                                     $req, 
                                                     array("Content-Type: appplication/json"));
            if ( $code != 200 ) { return array($code,$rsp['error']); }

            $session_id = $rsp['session_id'];
            
            // run test
            $req = json_encode( array('project-id' => intval($prjId), 
                                      'test-definition' => '',
                                      'test-execution' => '',
                                      'test-properties' => '',
                                      'test-extension' => $extension,
                                      'test-path' => $path,
                                      'test-name' => $filename,
                                      'schedule-id' => -1,
                                      'schedule-at' => array( 0, 0, 0, 0, 0, 0 ) ) );
            list($code, $rsp2) = $this->getRestClient("POST", "/tests/schedule/tpg", $req, 
                                                     array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp2['error']); }
            
            // logout
            list($code,$rsp) = $this->getRestClient("GET", "/session/logout", "", 
                                                    array("Cookie: session_id=".$session_id));
            if ( $code != 200 ) { return array($code,$rsp['error']); }                                        

            return array($code, $rsp2);
        }
        
    }
    
    global $RESTAPI;
    $RESTAPI = new INTERFACE_REST();
?>