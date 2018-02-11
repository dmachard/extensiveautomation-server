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

var ADMINISTRATOR = "Administrator";
var TESTER = "Tester";

/**
 * Hide or display the notification part
 * @param {String} level
 */
function loadnotif(level)
{
	var notifs = getel('notifs');
	if (level == ADMINISTRATOR || level== TESTER) { notifs.style.display = "block"; } else {notifs.style.display = "none"; }
}

/**
 * Update notifications user options
 * @param {Integer} id
 */
function changenotifsuser(id)
{
	var warning = getel("box-warn");
	var input2reset = new Array();
	hidewarning(warning);
	// prepare request
	var cmd = null;
	var args = new Array(	
							arg( 'notifications', getcheck('pass') + ';' + getcheck('fail')  + ';' + getcheck('undef') + ';'
									+ getcheck('complete') + ';' + getcheck('error')  + ';' + getcheck('killed')  + ';' + getcheck('cancelled') + ';'  )
						);

	cmd = "user.change.notifications";
	args.push( arg( 'uid', id )  ) ;

	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = input2reset, 
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}

/**
 * Reset password user
 * @param {Integer} id
 */
function resetpwduser(id)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "user.reset.password";
	var args = new Array(	arg( 'uid', id ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr =  new Array(),
			el_div_dst = null,
			el_loader = null
	);
}

/**
 * Change password user
 * @param {Integer} id
 */
function changepwduser(id)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "user.change.password";
	var args = new Array(	arg( 'uid', id ),
							arg( 'oldpwd', encodeURIComponent(getval('req_old_pwd')) ),
							arg( 'newpwd', encodeURIComponent(getval('req_new_pwd')) )
						 );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr =  new Array(),
			el_div_dst = null,
			el_loader = null
	);
}

/**
 * Enable user
 * @param {Integer} id
 * @param {Integer} status
 */
function enableuser(id,status)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "user.enable";
	var args = new Array( arg( 'uid', id ), arg( 'enable', status ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}

/**
 * Disconnect user
 * @param {Integer} id
 * @param {Integer} status
 */
function disconnectuser(login)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "user.disconnect";
	var args = new Array( arg( 'login', login ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}

/**
 * Delete user
 * @param {Integer} id or null
 */
function deluser(id)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "user.delete";
	var args = new Array( arg( 'uid', id ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}

/**
 * Duplicate user
 * @param {Integer} id or null
 */
function duplicateuser(id)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "user.duplicate";
	var args = new Array( arg( 'uid', id ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}


/**
 * Add a new user
 * @param {Integer} id or null
 */
function adduser(id)
{
	var warning = getel("box-warn");
	var input2reset = new Array();
	hidewarning(warning);
	// prepare request
	var cmd = null;
	var args = new Array(	
							arg( 'email', getval('req_email') ),
							arg( 'admin', getcheck('req_level_admin') ),
							arg( 'monitor', getcheck('req_level_monitor') ),
							arg( 'tester', getcheck('req_level_tester') ),
							// arg( 'developer', getcheck('req_level_developer') ),
							arg( 'lang', getval('req_lang') ),
							arg( 'style', getval('req_style') ),
							arg( 'notifications', getcheck('pass') + ';' + getcheck('fail')  + ';' + getcheck('undef') + ';'
									+ getcheck('complete') + ';' + getcheck('error')  + ';' + getcheck('killed')  + ';' + getcheck('cancelled') + ';'  ),
							arg( 'defaultproject', getval('req_default_project') )
							// arg( 'cli', getcheck('req_access_cli') ),
							// arg( 'gui', getcheck('req_access_gui') ),
							// arg( 'web', getcheck('req_access_web') )
						);
	
	// append selected projects 
	var checkbox_projects = getelbyname('checkbox_projects');
	var projects = '';
	for (var i=0; i < checkbox_projects.length; i++) { 
		if (checkbox_projects[i].checked) { 
			projects += checkbox_projects[i].value + ';';
		}
	}
	projects = projects.substr(0,projects.length-1);

	args.push( arg( 'projects', projects ) );

	if (id == null) { 
		cmd = "user.add"; 
		args.push( arg( 'login', getval('req_login') ) );
		args.push( arg( 'password', encodeURIComponent(getval('req_pwd')) ) );
		input2reset.push( "req_login", "req_pwd", "req_email" ); 
	} else {
		cmd = "user.update"; 
        args.push( arg( 'uid', id )  ) ;
		args.push( arg( 'login', getval('req_login') ) );
	}
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = input2reset, 
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}


/**
 * Enable project
 * @param {Integer} id
 * @param {Integer} status
 */
function enableproject(id,status)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "project.enable";
	var args = new Array( arg( 'pid', id ), arg( 'enable', status ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}

/**
 * Delete project
 * @param {Integer} id or null
 */
function delproject(id)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "project.delete";
	var args = new Array( arg( 'pid', id ) );
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}

/**
 * Add a new project
 * @param {Integer} id or null
 */
function addproject(id)
{
	var warning = getel("box-warn");
	var input2reset = new Array();
	hidewarning(warning);
	// prepare request
	var cmd = null;
	var args = new Array(	
							arg( 'name', getval('req_name') )
						);
	if (id == null) { 
		cmd = "project.add"; 
		input2reset.push( "req_name"  ); 
	} else {
		cmd = "project.update"; args.push( arg( 'pid', id )  ) ;
	}
	// call webservice
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = input2reset, 
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = null
		);
}