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

/**
 * Pretty json
 * @param {String} login
 */
function prettyJsonPrint() {
    var ugly = document.getElementById('req_element_values').value;
    var obj = JSON.parse(ugly);
    var pretty = JSON.stringify(obj, undefined, 4);
    document.getElementById('req_element_values').value = pretty;
}

/**
 * Load statistics by user
 * @param {String} login
 */
function loadstats(type, ct)
{
	var loader = getel('loader-stats-'+ type);
	var users = getel('userstatslist-'+ type);
	var projects = getel('projectstatslist-'+ type);
	var ct_dst = getel(ct);
	var cmd = "get.tests.stats"
	var args = new Array(
							arg( 'loginid', users.options[users.selectedIndex].value ),
							arg( 'type', type ),
							arg( 'projectid', projects.options[projects.selectedIndex].value )
		);
	// call webservice
	showloader(loader);
	callws(	data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = getel( "box-warn" ),
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = ct_dst,
			el_loader = loader
			);
}


/**
 * Load statistics by user
 * @param {String} login
 */
function loadstats_user(loginid, type, ct)
{
	var loader = getel('loader-stats-'+ type);
	var projects = getel('projectstatslist-'+ type);
	var ct_dst = getel(ct);
	var cmd = "get.tests.stats"
	var args = new Array(
							arg( 'loginid', loginid ),
							arg( 'type', type ),
							arg( 'projectid', projects.options[projects.selectedIndex].value )
		);
	// call webservice
	showloader(loader);
	callws(	data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = getel( "box-warn" ),
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = ct_dst,
			el_loader = loader
			);
}

/**
 * Load statistics by repository
 * @param {String} login
 */
function loadstats_tests(loginid, type, ct)
{
	var loader = getel('loader-stats-'+ type);
	var projects = getel('projectstatslist-'+ type);
	var ct_dst = getel(ct);
	var cmd = "get.repository.tests.stats"
	var args = new Array(
							arg( 'loginid', loginid ),
							arg( 'type', type ),
							arg( 'projectid', projects.options[projects.selectedIndex].value )
		);
	// call webservice
	showloader(loader);
	callws(	data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = getel( "box-warn" ),
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = ct_dst,
			el_loader = loader
			);
}


/**
 * Load tests by user
 * @param {String} login
 */
function loadtests_user(loginid, type, ct)
{
	var loader = getel('loader-tests-'+ type);
	var projects = getel('projecttestslist-'+ type);
	var ct_dst = getel(ct);
	var cmd = "get.tests.listing"
	var args = new Array(
							arg( 'loginid', loginid ),
							arg( 'type', type ),
							arg( 'projectid', projects.options[projects.selectedIndex].value )
		);
	// call webservice
	showloader(loader);
	callws(	data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = getel( "box-warn" ),
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = ct_dst,
			el_loader = loader
			);
}

/**
 * Export all global variables
 * @param {Integer} projectid
 */
function exportglobalvariables(projectid)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "environment.export";
	var args = new Array( arg( 'projectid', projectid ) );
	// call webservice
	callws_file( data = request(cmd = cmd, args = args.join("")) ,
			callback = readfile_cb
		);
}

/**
 * Import all global variables
 */
function importglobalvariables()
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "environment.import";
	var args = new Array( arg( 'values', getval('req_env_import') ) );
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
 * Open test report
 */
function open_report(projectid, testid, ct)
{
	var loader = getel('loader-run');
	var ct_dst = getel(ct);
	var cmd = "open.test.report"
	var args = new Array(
							arg( 'projectid', projectid),
							arg( 'testid', testid )
                        );
	// call webservice
	showloader(loader);
	callws(	data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = getel( "box-warn" ),
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = loader,
            new_page = true
			);
}


/**
 * Run test
 */
function run_test(loginid, projectid, extension, filename, path)
{
	var loader = getel('loader-run');
//	var ct_dst = getel(ct);
	var cmd = "run.test"
	var args = new Array(
							arg( 'loginid', loginid ),
							arg( 'projectid', projectid),
							arg( 'extension', extension),
							arg( 'filename', filename),
							arg( 'path', path)
		);
	// call webservice
	showloader(loader);
	callws(	data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = getel( "box-warn" ),
			input_clr = new Array(),
			div_clr = new Array(),
			el_div_dst = null,
			el_loader = loader
			);
}

/**
 * Add a new element
 * @param {Integer} id or null
 */
function addelementenv(id)
{
	var warning = getel("box-warn");
	var input2reset = new Array();
	hidewarning(warning);
	// prepare request
	var cmd = null;
	var args = new Array(	
							arg( 'name', getval('req_element_name') ),
							arg( 'values', encodeURIComponent(getval('req_element_values') )),
							arg( 'projectid', getval('req_environment_project') )
						);
	if (id == null) { 
		cmd = "environment.element.add"; 
		input2reset.push( "req_element_name"  ); 
		input2reset.push( "req_environment_project"  ); 
	} else {
		cmd = "environment.element.update"; args.push( arg( 'elementid', id )  ) ;
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
 * Delete element
 * @param {Integer} id or null
 */
function delelementenv(id, pid)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "environment.element.delete";
	var args = new Array( arg( 'elementid', id ), arg( 'projectid', pid ) );
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
 * Duplicate element
 * @param {Integer} id or null
 */
function duplicateelementenv(id, pid)
{
	var warning = getel("box-warn");
	hidewarning(warning);
	// prepare request
	var cmd = "environment.element.duplicate";
	var args = new Array( arg( 'elementid', id ), arg( 'projectid', pid ) );
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
 * Toggle test environment
 * @param {Integer} id 
 */
function toggle_paramvalue(id_title, id_panel)
{
	var title = document.getElementById(id_title);
    var panel = document.getElementById(id_panel);
	if(panel.style.display == "block")
	{
        title.style.display = "block";
    	panel.style.display = "none";
	} else {
        title.style.display = "none";
		panel.style.display = "block";
	}
}

/**
 * Reset all statistics
 */
function resetallstats()
{
	var warning = getel("box-warn");
	hidewarning(warning);

	// prepare request
	var cmd = "tests.stats.reset";
	var args = new Array( );
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
 * Reset tests statistics by user and project
 */
function resetstatsby(type)
{
	var warning = getel("box-warn");
	hidewarning(warning);
    
    var projects = getel('projectstatslist-'+ type);
    var users = getel('userstatslist-'+ type);
    
	// prepare request
	var cmd = "tests.stats.reset.by";
	var args = new Array(  
                    arg( 'projectid', projects.options[projects.selectedIndex].value ),
                    arg( 'loginid', users.options[users.selectedIndex].value )
                );
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