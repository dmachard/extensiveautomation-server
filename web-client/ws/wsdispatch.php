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

	if (!defined('WS_OK'))
		exit( 'access denied' );

	// load web services functions
	require ROOT.'ws/config.php';
	require ROOT.'ws/user.php';
	require ROOT.'ws/tests.php';
	require ROOT.'ws/project.php';
	require ROOT.'ws/agent.php';
	require ROOT.'ws/probe.php';

	if ( $CORE->profile != null)
	{
		// admin only
		if ( $CORE->profile['administrator'] )
		{
			/*  
			* ENVIRONMENT.EXPORT, expected args: 
			*  - projectid: integer
			*/
			if ( $req->cmd == "environment.export")
			{
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the project." );
				// request seems to be ok, call ws
				$rsp = env_exportall( get_str_arg($req->args->projectid) );
			}
            
			/*  
			* ENVIRONMENT.IMPORT, expected args: 
			*  - projectid: integer
			*/
			if ( $req->cmd == "environment.import")
			{
				if ( empty_obj( $req->args->values ) )
					response(400, "You must fill the field values." );
				// request seems to be ok, call ws
				$rsp = env_importall( get_str_arg($req->args->values) );
			}
            
			/*  
			* TESTS.STATS.RESET, expected args: 
			*/
			if ( $req->cmd == "tests.stats.reset")
			{
				// request seems to be ok, call ws
				$rsp = tests_resetallstats( );
			}
            
			/*  
			* TESTS.STATS.RESET.BY, expected args: 
			*/
			if ( $req->cmd == "tests.stats.reset.by")
			{
				if ( empty_obj( $req->args->loginid ) or ! is_numeric( $req->args->loginid ) )
					response(400, "You must fill the field login id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the field project id." );
				// request seems to be ok, call ws
				$rsp = tests_resetstatsby( $req->args->loginid, $req->args->projectid );
			}

			/*  
			* PROJECT.DELETE, expected args: 
			*  - uid: integer
			*/
			if ( $req->cmd == "project.delete")
			{
				if ( empty_obj( $req->args->pid ) or ! is_numeric( $req->args->pid ) )
					response(400, "You must fill the project  id (integer)." );
				// request seems to be ok, call ws
				$rsp = delproject( $req->args->pid  );
			}

			/*  
			* PROJECT.ADD, expected args: 
			*  - name: string not null
			*/
			if ( $req->cmd == "project.add")
			{
				if ( empty_obj( $req->args->name ) )
					response(400, "You must fill the field name." );
				// request seems to be ok, call ws
				$rsp = addproject( get_str_arg($req->args->name) );
			}

			/*  
			* PROJECT.UPDATE, expected args: 
			*  - name: string not null
			*  - pid: integer
			*/
			if ( $req->cmd == "project.update")
			{					
				if ( empty_obj( $req->args->name ) )
					response(400, "You must fill the field name." );
				if ( empty_obj( $req->args->pid ) or ! is_numeric( $req->args->pid ) )
					response(400, "You must fill the project  id (integer)." );
				// request seems to be ok, call ws
				$rsp = updateproject( get_str_arg($req->args->name), $req->args->pid );
			}

			/*  
			* USER.RESET.PASSWORD, expected args: 
			*  - uid: integer
			*/
			if ( $req->cmd == "user.reset.password")
			{
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the field user id (integer)." );
				// request seems to be ok, call ws
				$rsp = resetpwduser( $req->args->uid );
			}

			/*  
			* USER.ENABLE, expected args: 
			*  - uid: integer
			*  - enable: integer
			*/
			if ( $req->cmd == "user.enable")
			{
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the field user id (integer)." );
				if ( empty_obj( $req->args->enable ) or ! is_numeric( $req->args->enable ) )
					response(400, "You must fill the field enable id (integer)." );
				// request seems to be ok, call ws
				$rsp = enableuser( $req->args->uid, $req->args->enable  );
			}

			/*  
			* USER.DISCONNECT, expected args: 
			*  - login: string
			*/
			if ( $req->cmd == "user.disconnect")
			{
				if ( empty_obj( $req->args->login ) )
					response(400, "You must fill the login user (string)." );
				// request seems to be ok, call ws
				$rsp = disconnectuser( $req->args->login );
			}


			/*  
			* USER.DELETE, expected args: 
			*  - uid: integer
			*/
			if ( $req->cmd == "user.delete")
			{
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the user  id (integer)." );
				// request seems to be ok, call ws
				$rsp = deluser( $req->args->uid  );
			}
            
			/*  
			* USER.DUPLICATE, expected args: 
			*  - uid: integer
			*/
			if ( $req->cmd == "user.duplicate")
			{
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the user  id (integer)." );
				// request seems to be ok, call ws
				$rsp = duplicateuser( $req->args->uid  );
			}
            
			/*  
			* USER.ADD, expected args: 
			*  - login: string not null
			*  - password: string not null
			*  - email: string not null
			*  - admin: string not null
			*  - leader: string not null
			*  - tester: string not null
			*  - developer: string not null
			*  - lang: string not null
			*  - style: string not null
			*/
			if ( $req->cmd == "user.add")
			{
				if ( empty_obj( $req->args->login ) )
					response(400, "You must fill the field login." );
				if ( empty_obj( $req->args->password ) )
					$req->args->password = '';
				if ( empty_obj( $req->args->email ) )
					response(400, "You must fill the field email." );
				if ( empty_obj( $req->args->admin ) )
					response(400, "You must fill the field administrator." );
				if ( empty_obj( $req->args->monitor )  )
					response(400, "You must fill the field monitor." );
				if ( empty_obj( $req->args->tester )  )
					response(400, "You must fill the field tester." );
				// if ( empty_obj( $req->args->developer ) )
					// response(400, "You must fill the field developer." );
				if ( empty_obj( $req->args->lang ) )
					response(400, "You must fill the field language." );
				if ( empty_obj( $req->args->style ) )
					response(400, "You must fill the field style." );
				if ( empty_obj( $req->args->notifications ) )
					response(400, "You must fill the field notifications." );
				if ( empty_obj( $req->args->projects ) )
					response(400, "You must fill the field projects." );
				if ( empty_obj( $req->args->defaultproject )or ! is_numeric( $req->args->defaultproject ) )
					response(400, "You must fill the field default project." );
				// if ( empty_obj( $req->args->cli )  )
					// response(400, "You must fill the field cli." );
				// if ( empty_obj( $req->args->gui )  )
					// response(400, "You must fill the field gui." );
				// if ( empty_obj( $req->args->web )  )
					// response(400, "You must fill the field web." );
				// request seems to be ok, call ws
				$rsp = adduser( get_str_arg($req->args->login), get_str_arg($req->args->password), get_str_arg($req->args->email),
								get_str_arg($req->args->admin), get_str_arg($req->args->monitor), get_str_arg($req->args->tester),
								get_str_arg($req->args->lang), get_str_arg($req->args->style), get_str_arg($req->args->notifications), 
                                get_str_arg($req->args->projects), get_str_arg($req->args->defaultproject) );
			}

			/*  
			* USER.UPDATE, expected args: 
			*  - login: string not null
			*  - email: string not null
			*  - admin: string not null
			*  - leader: string not null
			*  - tester: string not null
			*  - developer: string not null
			*  - lang: string not null
			*  - style: string not null
			*  - notifications: string not null
			*  - uid: integer
			*/
			if ( $req->cmd == "user.update")
			{		
				if ( empty_obj( $req->args->login ) )
					response(400, "You must fill the field login." );			
				if ( empty_obj( $req->args->email ) )
					response(400, "You must fill the field email." );
				if ( empty_obj( $req->args->admin ) )
					response(400, "You must fill the field administrator." );
				if ( empty_obj( $req->args->monitor ) )
					response(400, "You must fill the field monitor." );
				if ( empty_obj( $req->args->tester ) )
					response(400, "You must fill the field tester." );
				// if ( empty_obj( $req->args->developer ) )
					// response(400, "You must fill the field developer." );
				if ( empty_obj( $req->args->lang ) )
					response(400, "You must fill the field language." );
				if ( empty_obj( $req->args->style ) )
					response(400, "You must fill the field style." );
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the user  id (integer)." );
				if ( empty_obj( $req->args->notifications ) )
					response(400, "You must fill the field style." );
				if ( empty_obj( $req->args->projects ) )
					response(400, "You must fill the projects style." );
				if ( empty_obj( $req->args->defaultproject ) or ! is_numeric( $req->args->defaultproject ) )
					response(400, "You must fill the default project." );
				// if ( empty_obj( $req->args->cli )  )
					// response(400, "You must fill the field cli." );
				// if ( empty_obj( $req->args->gui )  )
					// response(400, "You must fill the field gui." );
				// if ( empty_obj( $req->args->web )  )
					// response(400, "You must fill the field web." );
				// request seems to be ok, call ws
				$rsp = updateuser( get_str_arg($req->args->login), get_str_arg($req->args->email), get_str_arg($req->args->admin), get_str_arg($req->args->monitor), get_str_arg($req->args->tester), get_str_arg($req->args->lang), get_str_arg($req->args->style),
						get_str_arg($req->args->notifications),	get_str_arg($req->args->projects), get_str_arg($req->args->defaultproject) , $req->args->uid);
			}
		}

		// all users
		if ( $CORE->profile['administrator'] || $CORE->profile['tester'] || $CORE->profile['leader'] || $CORE->profile['developer']  )
		{
			/*  
			* USER.CHANGE.PASSWORD, expected args: 
			*  - uid: integer
			*  - oldpwd: string
			*  - newpwd: string
			*/
			if ( $req->cmd == "user.change.password")
			{
				if ( empty_obj( $req->args->oldpwd ) )
					$req->args->password = '';
					//response(400, "You must fill the old password." );
				if ( empty_obj( $req->args->newpwd ) )
					$req->args->password = '';
					//response(400, "You must fill the new password." );
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the field user id (integer)." );
				// request seems to be ok, call ws
				$rsp = changepwduser( $req->args->uid, get_str_arg($req->args->oldpwd), get_str_arg($req->args->newpwd) );
			}
		}

		// admin or tester
		if ( $CORE->profile['administrator'] || $CORE->profile['tester']  ) {
			/*  
			* USER.CHANGE.NOTIFICATIONS, expected args: 
			*  - uid: integer
			*  - notifications: string not null
			*/
			if ( $req->cmd == "user.change.notifications")
			{					
				if ( empty_obj( $req->args->uid ) or ! is_numeric( $req->args->uid ) )
					response(400, "You must fill the user  id (integer)." );
				if ( empty_obj( $req->args->notifications ) )
					response(400, "You must fill the field style." );
				// request seems to be ok, call ws
				$rsp = changenotfisuser( $req->args->uid, get_str_arg($req->args->notifications) );
			}
		}

		// admin or leader or tester
		if ( $CORE->profile['administrator'] || $CORE->profile['leader'] || $CORE->profile['tester'] ) {
			/*  
			* AGENT.DISCONNECT, expected args: 
			*  - name: string
			*/
			if ( $req->cmd == "agent.disconnect")
			{
				if ( empty_obj( $req->args->name ) )
					response(400, "You must fill the name (string)." );
				// request seems to be ok, call ws
				$rsp = disconnectagent( $req->args->name );
			}

			/*  
			* PROBE.DISCONNECT, expected args: 
			*  - name: string
			*/
			if ( $req->cmd == "probe.disconnect")
			{
				if ( empty_obj( $req->args->name ) )
					response(400, "You must fill the name (string)." );
				// request seems to be ok, call ws
				$rsp = disconnectprobe( $req->args->name );
			}

			/*  
			* ENVIRONMENT.ELEMENT.ADD, expected args: 
			*  - name: string not null
			*/
			if ( $req->cmd == "environment.element.add")
			{
				if ( empty_obj( $req->args->name ) )
					response(400, "You must fill the field name." );
				if ( empty_obj( $req->args->values ) )
					response(400, "You must fill the field values." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the project." );
				// request seems to be ok, call ws
				$rsp = env_addelement( get_str_arg($req->args->name), get_str_arg($req->args->values),  get_str_arg($req->args->projectid) );
			}

			/*  
			* ENVIRONMENT.ELEMENT.DELETE, expected args: 
			*  - elementid: integer
			*/
			if ( $req->cmd == "environment.element.delete")
			{
				if ( empty_obj( $req->args->elementid ) or ! is_numeric( $req->args->elementid ) )
					response(400, "You must fill the element id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the project." );
				// request seems to be ok, call ws
				$rsp = env_delelement( get_str_arg($req->args->elementid), get_str_arg($req->args->projectid) );
			}
            
			/*  
			* ENVIRONMENT.ELEMENT.DUPLICATE, expected args: 
			*  - elementid: integer
			*/
			if ( $req->cmd == "environment.element.duplicate")
			{
				if ( empty_obj( $req->args->elementid ) or ! is_numeric( $req->args->elementid ) )
					response(400, "You must fill the element id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the project." );
				// request seems to be ok, call ws
				$rsp = env_duplicateelement( get_str_arg($req->args->elementid), get_str_arg($req->args->projectid) );
			}
            
			/*  
			* ENVIRONMENT.ELEMENT.UPDATE, expected args: 
			*  - name: string not null
			*  - values: string not null
			*  - projectid: integer
			*/
			if ( $req->cmd == "environment.element.update")
			{
				if ( empty_obj( $req->args->elementid ) or ! is_numeric( $req->args->elementid ) )
					response(400, "You must fill the element id." );
				if ( empty_obj( $req->args->name ) )
					response(400, "You must fill the field name." );
				if ( empty_obj( $req->args->values ) )
					response(400, "You must fill the field values." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the project." );
				// request seems to be ok, call ws
				$rsp = env_updateelement( get_str_arg($req->args->elementid), get_str_arg($req->args->name), get_str_arg($req->args->values),  get_str_arg($req->args->projectid) );
			}
			/*  
			* GET.TESTS.STATS, expected args: 
			*  - login: string
			*  - type: string
			*/
			if ( $req->cmd == "get.tests.stats")
			{
				if ( empty_obj( $req->args->loginid ) or ! is_numeric( $req->args->loginid ) )
					response(400, "You must fill the field login id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the field project id." );
				if ( empty_obj( $req->args->type ) )
					response(400, "You must fill the field type." );
				// request seems to be ok, call ws
				$rsp = tests_getstats( $req->args->loginid, $req->args->type, $req->args->projectid );
			}

			/*  
			* GET.TESTS.STATS, expected args: 
			*  - login: string
			*  - type: string
			*/
			if ( $req->cmd == "get.repository.tests.stats")
			{
				if ( empty_obj( $req->args->loginid ) or ! is_numeric( $req->args->loginid ) )
					response(400, "You must fill the field login id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the field project id." );
				if ( empty_obj( $req->args->type ) )
					response(400, "You must fill the field type." );
				// request seems to be ok, call ws
				$rsp = tests_getrepositorystats( $req->args->loginid, $req->args->type, $req->args->projectid );
			}

			/* 
			* GET.TESTS.LISTING, expected args: 
			*  - projectid: integer
			*/
			if ( $req->cmd == "get.repository.tests.listing")
			{
				if ( empty_obj( $req->args->loginid ) or ! is_numeric( $req->args->loginid ) )
					response(400, "You must fill the field login id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the field project id." );
				if ( empty_obj( $req->args->type ) )
					response(400, "You must fill the field type." );
				// request seems to be ok, call ws
				$rsp = tests_getlisting(  $req->args->loginid, $req->args->type, $req->args->projectid );
			}

			/*  
			* RUN.TEST, expected args: 
			*  - loginid: integer
			*  - projectid: integer
			*  - extension: string
			*  - filename: string
			*  - path: string
			*/
			if ( $req->cmd == "run.test")
			{
				if ( empty_obj( $req->args->loginid ) or ! is_numeric( $req->args->loginid ) )
					response(400, "You must fill the field login id." );
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the field project id." );
				if ( empty_obj( $req->args->extension ) )
					response(400, "You must fill the field extension." );
				if ( empty_obj( $req->args->filename ) )
					response(400, "You must fill the field filename." );
				if ( empty_obj( $req->args->path ) )
					response(400, "You must fill the field path." );
				// request seems to be ok, call ws
				$rsp = run_test( $req->args->loginid, $req->args->projectid, $req->args->extension, $req->args->filename, $req->args->path );
			}
            
            /*  
			* OPEN.TEST.REPORT, expected args: 
			*  - projectid: integer
			*  - trpath: string
			*  - trname: string
			*/
			if ( $req->cmd == "open.test.report")
			{
				if ( empty_obj( $req->args->projectid ) or ! is_numeric( $req->args->projectid ) )
					response(400, "You must fill the field project id." );
				if ( empty_obj( $req->args->testid ) )
					response(400, "You must fill the field test id." );
				// request seems to be ok, call ws
				$rsp = open_test_report( $req->args->projectid, $req->args->testid );
			}
		}
	} 
?>
