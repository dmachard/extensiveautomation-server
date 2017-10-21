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

    define('ADD_PROJECT',                   "addProject");
    define('DEL_PROJECT',                   "delProject");

    define('GET_TESTS_INFORMATIONS',        "refreshStatsRepo");

    define('GET_SERVER_INFORMATIONS',       "getServerInformations");
    define('GET_SERVER_USAGE',              "getServerUsage");

    define('GET_RUNNING_AGENTS',            "refreshRunningAgents");
    define('GET_RUNNING_PROBES',            "refreshRunningProbes");

    define('GET_RELEASE_NOTES',             "getReleaseNotes");
    define('DISCONNECT_USER',               "unauthenticateClient");

    define('GET_FILES_TESTS',               "refreshRepo");
    define('GET_FILES_TESTSRESULT',         "refreshRepo");
	define('REFRESH_TEST_ENVIRONMENT',      "refreshTestEnvironment");

    define('RUN_TEST',                      "scheduleTest");

	define('DISCONNECT_AGENT',               "disconnectAgent");
	define('DISCONNECT_PROBE',               "disconnectProbe");
    
    define('GET_TEST_PREVIEW',               "getTestPreview");
    
    define('REPO_TESTS',                    0);
    define('REPO_ARCHIVES',                 4);
    
    class INTERFACE_XMLRPC{

        function INTERFACE_XMLRPC(){
        }
        function getXmlClient(){
            global $__LWF_CFG;

            $http = "http://";
            if ( $__LWF_CFG['webservices-https'] == '1' ) $http = "https://";
            $client = new xmlrpc_client( $http.$__LWF_CFG['bind-ip-wsu'].":".$__LWF_CFG['bind-port-wsu'] );
            $client->setSSLVerifyPeer(False);
            //$client->setDebug(2);

            return $client;
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

        // Returns xml structure
        function getXmlMsg($cmd){
            global $__LWF_CFG, $CORE;

            $f=new xmlrpcmsg( $cmd );
            //$f->addParam( new xmlrpcval( $__LWF_CFG['default-user-sys'], "string" ) );
            //$f->addParam( new xmlrpcval( sha1($__LWF_CFG['default-user-sys-password']), "string") );
            $f->addParam( new xmlrpcval( $CORE->profile['login'], "string" ) );
            $f->addParam( new xmlrpcval( $CORE->profile['user-password'], "string") );
            return $f;
        }

        // Call GET_RUNNING_AGENTS
        function getReleaseNotes(){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( );

            $xml = $this->getXmlMsg( $cmd=GET_RELEASE_NOTES );      
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_RELEASE_NOTES ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call RUN_TEST
        function runTest($prjId, $extension, $filename, $path ){
            global $__LWF_CFG, $CORE;
            $client = $this->getXmlClient();

            $runAt = array( 0, 0, 0, 0, 0, 0 );
            $runFrom = array( 0, 0, 0, 0, 0, 0 );
            $runTo = array( 0, 0, 0, 0, 0, 0 );
            $data = array( 
                'nocontent'=> True,
                'testextension'=> $extension,
                'prj-id'=>$prjId,
                'prj-name'=>'',
                'testpath'=> $path,
                'testname'=>$filename,
                'user-id'=>$CORE->profile['id'],
                'user'=>$CORE->profile['login'],
                'test-id'=>0,
                'background'=>True,
                'runAt'=>$runAt,
                'runType'=>-1,
                'runNb'=>-1,
                'withoutProbes'=>False,
                'debugActivated'=>False,
                'withoutNotif'=> False,
                'noKeepTr'=>False,
                'fromTime'=> $runFrom,
                'toTime'=> $runTo,
                'step-by-step' => False,
                'breakpoint' => False
            );

            $json_encoded = json_encode( $data );
            $data_compressed = gzcompress( $json_encoded );

            $xml = $this->getXmlMsg( $cmd=RUN_TEST );       
            $xml->addParam( new xmlrpcval( $data_compressed, "base64" ) );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == RUN_TEST ) {
                    if ( $rsp[1] == '200') {
                        return '200'; //$rsp[2];
                    } elseif ( $rsp[1] == '404') {
                        return '404';
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call GET_FILES_TESTSRESULT
        function getFilesTestsResult($prjId){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( 
                'repo-dst'=>new xmlrpcval( REPO_ARCHIVES, "int"),
                'projectid'=>new xmlrpcval( $prjId, "int"),
                'partial'=>new xmlrpcval( True, "boolean"),
                'saveas-only'=>new xmlrpcval( False, "boolean"),
                'for-runs'=>new xmlrpcval( False, "boolean")
            );

            $xml = $this->getXmlMsg( $cmd=GET_FILES_TESTSRESULT );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_FILES_TESTSRESULT ) {
                    if ( $rsp[1] == '200') {
                        $ret = $this->decodeData( $rsp[2]['ret'], $json=True) ;
                        return $ret;
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }
        
        // Call GET_TEST_PREVIEW
        function getTestPreview($prjId, $trPath, $trName){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( 
                'projectid'=>new xmlrpcval( $prjId, "int"),
                'tr-path'=>new xmlrpcval( $trPath, "string" ),
                'tr-name'=>new xmlrpcval( $trName, "string" ),
            );

            $xml = $this->getXmlMsg( $cmd=GET_TEST_PREVIEW );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument
            
            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_TEST_PREVIEW ) {
                    if ( $rsp[1] == '200') {
                        return $this->decodeData($data=$rsp[2]['reports'],$json=False);
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }
        
        // Call GET_FILES_TESTS
        function getFilesTests($prjId){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( 
                'repo-dst'=>new xmlrpcval( REPO_TESTS, "int"),
                'projectid'=>new xmlrpcval( $prjId, "int"),
                'saveas-only'=>new xmlrpcval( False, "boolean"),
                'for-runs'=>new xmlrpcval( False, "boolean")
            );

            $xml = $this->getXmlMsg( $cmd=GET_FILES_TESTS );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_FILES_TESTS ) {
                    if ( $rsp[1] == '200') {
                        $ret = $this->decodeData( $rsp[2]['ret'], $json=True) ;
                        return $ret;
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call GET_RUNNING_AGENTS
        function getRunningAgents(){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( );

            $xml = $this->getXmlMsg( $cmd=GET_RUNNING_AGENTS );     
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_RUNNING_AGENTS ) {
                    if ( $rsp[1] == '200') {
                        return $this->decodeData( $rsp[2] );
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call GET_RUNNING_PROBES
        function getRunningProbes(){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( );

            $xml = $this->getXmlMsg( $cmd=GET_RUNNING_PROBES );     
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_RUNNING_PROBES ) {
                    if ( $rsp[1] == '200') {
                        return $this->decodeData( $rsp[2] );
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call GET_SERVER_USAGE
        function getServerUsage(){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( );

            $xml = $this->getXmlMsg( $cmd=GET_SERVER_USAGE );       
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_SERVER_USAGE ) {
                    if ( $rsp[1] == '200') {
                        return $this->decodeData( $rsp[2]['usage'] );
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call GET_TESTS_INFORMATIONS
        function getTestsInformations($prjId){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( 
                'repo-dst'=>new xmlrpcval( REPO_TESTS, "int"),
                'projectid'=>new xmlrpcval( $prjId, "int")
            );

            $xml = $this->getXmlMsg( $cmd=GET_TESTS_INFORMATIONS );     
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_TESTS_INFORMATIONS ) {
                    if ( $rsp[1] == '200') {
                        //return $this->decodeData( $rsp[2]['stats-repo-tests'] );
                        return $rsp[2]['stats-repo-tests'];
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        // Call GET_SERVER_INFORMATIONS
        function getServerStatus(){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array( );

            $xml = $this->getXmlMsg( $cmd=GET_SERVER_INFORMATIONS );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == GET_SERVER_INFORMATIONS ) {
                    if ( $rsp[1] == '200') {
                        return $this->decodeData( $rsp[2]['informations'] );
                    } else { return null; }
                } else { return null; }

            } else { return null; }

        }

        function disconnectProbe($name){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array(
                'name'=>new xmlrpcval($name, "string")
            );
            $xml = $this->getXmlMsg( $cmd=DISCONNECT_PROBE );    
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == DISCONNECT_PROBE ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }
        }

        function disconnectAgent($name){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array(
                'name'=>new xmlrpcval($name, "string")
            );
            $xml = $this->getXmlMsg( $cmd=DISCONNECT_AGENT );    
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == DISCONNECT_AGENT ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }
        }

        function disconnectUser($login){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array(
                'login'=>new xmlrpcval($login, "string")
            );
            $xml = $this->getXmlMsg( $cmd=DISCONNECT_USER );    
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == DISCONNECT_USER ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }
        }

        function refreshTestEnvironment(){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array();

            $xml = $this->getXmlMsg( $cmd=REFRESH_TEST_ENVIRONMENT );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == REFRESH_TEST_ENVIRONMENT ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }
        }

        function addProject($prjId){
            global $__LWF_CFG;
            $client = $this->getXmlClient();

            $data = array(
                'project-id'=>new xmlrpcval($prjId, "string")
            );

            $xml = $this->getXmlMsg( $cmd=ADD_PROJECT );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == ADD_PROJECT ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }
        }

        function delProject($prjId){
            global $__LWF_CFG;

            $client = $this->getXmlClient();

            $data = array(
                'project-id'=>new xmlrpcval($prjId, "string")
            );

            $xml = $this->getXmlMsg( $cmd=DEL_PROJECT );        
            $xml->addParam( new xmlrpcval( $data , "struct") );
            $xml->addParam( new xmlrpcval( False, "boolean") ); //fromGui argument

            $r= &$client->send($xml);
            if (!$r->faultCode()) {
                $rsp = php_xmlrpc_decode($r->value());
                if ( $rsp[0] == DEL_PROJECT ) {
                    if ( $rsp[1] == '200') {
                        return $rsp[2];
                    } else { return null; }
                } else { return null; }

            } else { return null; }
        }
    }


    global $XMLRPC;
    $XMLRPC = new INTERFACE_XMLRPC();
?>