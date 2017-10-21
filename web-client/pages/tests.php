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

	if (!defined('CONFIG_OK'))
		exit( lang('access denied') );

	define('WS_OK', 1);
	require ROOT.'ws/tests.php';

	// prepare index page
	$TESTS_PAGE = get_pindex('tests');
	$SUB_PAGE_REPO =  get_subpindex( 'tests', 'tests-repository' ) ;
	$SUB_PAGE_RESULTS =  get_subpindex( 'tests', 'tests-result' ) ;
	$SUB_PAGE_ENV =  get_subpindex( 'tests', 'test-environment' ) ;
	$SUB_PAGE_STATS =  get_subpindex( 'tests', 'tests-statistics' ) ;
	$SUB_PAGE_MYSTAT =  get_subpindex( 'tests', 'tests-my-statistic' ) ;
	$SUB_PAGE_HISTORY =  get_subpindex( 'tests', 'tests-history' ) ;

	// default sub-menu selected
	$s = $SUB_PAGE_REPO;
	
	if ( isset($_GET['s']) )
	{
		$s_called = $_GET['s'];
		(!$s_called) ? $s=1 : $s=$s_called;
	}
	
	//$prj_called = DEFAULT_PROJECT; //"default project
    $prj_called = $CORE->profile['defaultproject'];
	if ( isset($_POST['project']) )
	{
		$prj_called = $_POST['project'];
	}
	if ( isset($_GET['prj']) )
	{
		$prj_called = $_GET['prj'];
	}

	$c_called = null;
	if ( isset($_GET['c']) )
	{
		$c_called = $_GET['c'];
		if ( !( $c_called == "new" || $c_called == "edit" || $c_called == "del" || $c_called == "import" ) )
			$c_called = null;
	}
	$button_name = lang('add');

	// return combo with user list
	function getusers($stats, $container){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;

		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users`';
		$rlst_usrs = $db->query($sql_req);
		if ( ! $rlst_usrs )
			$tb = 'Unable to fetch users'.$db->str_error();
		else {
            $tb = '<div class="line" /></div>';
			$tb .= lang('tests-show-stats').' '.lang('tests-by-user').': <select id="userstatslist-'.$stats.'" style="width:150px" onchange="javascript:loadstats(\''.$stats.'\', \''.$container.'\')"><option value="-1">All</option>';
			while ( $cur_u = $db->fetch_assoc($rlst_usrs) )
				$tb .= '<option value="'.$cur_u['id'].'">'.$cur_u['login'].'</option>';
			$tb .= '</select>';
		}

		return $tb;
	}

    
	// return combo with user list
	function getusers_select($stats){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;

		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users`';
		$rlst_usrs = $db->query($sql_req);
		if ( ! $rlst_usrs )
			$tb = 'Unable to fetch users'.$db->str_error();
		else {
			$tb = lang('tests-by-user').': <select id="userstatslist-'.$stats.'" style="width:150px" >';
			while ( $cur_u = $db->fetch_assoc($rlst_usrs) )
				$tb .= '<option value="'.$cur_u['id'].'">'.$cur_u['login'].'</option>';
			$tb .= '</select>';
		}

		return $tb;
	}
    
	// return combo with project list 
	function getprojects_select($stats){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;

		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` ORDER BY `name`';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = ' '.lang('tests-by-project').': <select id="projectstatslist-'.$stats.'" style="width:150px"><option value="0">Undefined</option>';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) )
				$tb .= '<option value="'.$cur_u['id'].'">'.$cur_u['name'].'</option>';
			$tb .= '</select> <img  id="loader-stats-'.$stats.'" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" class="icon-loader" alt="ajax-loader">';
		}

		return $tb;
	} 

	// return combo with project list 
	function getprojects($stats, $container){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;

		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` ORDER BY `name`';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = ' '.lang('tests-by-project').': <select id="projectstatslist-'.$stats.'" style="width:150px" onchange="javascript:loadstats(\''.$stats.'\', \''.$container.'\')"><option value="-1">All</option><option value="0">Undefined</option>';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) )
				$tb .= '<option value="'.$cur_u['id'].'">'.$cur_u['name'].'</option>';
			$tb .= '</select> <img  id="loader-stats-'.$stats.'" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" class="icon-loader" alt="ajax-loader">';
			$tb .= '<div class="line" /></div>';
		}

		return $tb;
	} 

	// return combo with project list 
	function getprojects_by_user_for_env($stats, $container, $user_id, $selected){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;
		
		$sql_req = 'SELECT `'.$__LWF_DB_PREFIX.'-projects`.id, `'.$__LWF_DB_PREFIX.'-projects`.name FROM `'.$__LWF_DB_PREFIX.'-relations-projects` INNER JOIN `'.$__LWF_DB_PREFIX.'-projects` on `'.$__LWF_DB_PREFIX.'-relations-projects`.project_id = `'.$__LWF_DB_PREFIX.'-projects`.id WHERE `'.$__LWF_DB_PREFIX.'-relations-projects`.user_id='.$user_id.' ORDER BY `'.$__LWF_DB_PREFIX.'-projects`.name';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = '<div class="line" /></div>';
			
			$tb .= '<form action="./index.php?p='.get_pindex('tests').'&s='.get_subpindex( 'tests', 'test-environment' ).'" method="post">';
			$tb .= lang('tests-show-tests').' <label>'.lang('tests-by-project').'</label>: ';
			$tb .= '<select name="project">';
			$default_val ='';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) ) {
				if ($selected == $cur_u['id']) 
					$default_val = 'selected';
				else
					$default_val = '';
				$tb .= '<option value="'.$cur_u['id'].'" '.$default_val.'>'.$cur_u['name'].'</option>';
			}
			$tb .= '</select>';
			$tb .= ' <button type="submit">'.lang('reload').'</button></form> ';
			$tb .= '<div class="line" /></div>';
		}
		return $tb;
	}

	function getprojects_by_user_for_repo($stats, $container, $user_id, $selected){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;
		
		$sql_req = 'SELECT `'.$__LWF_DB_PREFIX.'-projects`.id, `'.$__LWF_DB_PREFIX.'-projects`.name FROM `'.$__LWF_DB_PREFIX.'-relations-projects` INNER JOIN `'.$__LWF_DB_PREFIX.'-projects` on `'.$__LWF_DB_PREFIX.'-relations-projects`.project_id = `'.$__LWF_DB_PREFIX.'-projects`.id WHERE `'.$__LWF_DB_PREFIX.'-relations-projects`.user_id='.$user_id.' ORDER BY `'.$__LWF_DB_PREFIX.'-projects`.name';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = '<div class="line" /></div>';
			
			$tb .= '<form action="./index.php?p='.get_pindex('tests').'&s='.get_subpindex( 'tests', 'tests-repository' ).'" method="post">';
			$tb .= lang('tests-show-tests').' <label>'.lang('tests-by-project').'</label>: ';
			$tb .= '<select name="project">';
			$default_val ='';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) ) {
				if ($selected == $cur_u['id']) 
					$default_val = 'selected';
				else
					$default_val = '';
				$tb .= '<option value="'.$cur_u['id'].'" '.$default_val.'>'.$cur_u['name'].'</option>';
			}
			$tb .= '</select>';
			$tb .= ' <button type="submit">'.lang('reload').'</button></form> ';
			$tb .= '<div class="line" /></div>';
		}
		return $tb;
	} 
    
	function getprojects_by_user_for_testsresult($stats, $container, $user_id, $selected){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;
		
		$sql_req = 'SELECT `'.$__LWF_DB_PREFIX.'-projects`.id, `'.$__LWF_DB_PREFIX.'-projects`.name FROM `'.$__LWF_DB_PREFIX.'-relations-projects` INNER JOIN `'.$__LWF_DB_PREFIX.'-projects` on `'.$__LWF_DB_PREFIX.'-relations-projects`.project_id = `'.$__LWF_DB_PREFIX.'-projects`.id WHERE `'.$__LWF_DB_PREFIX.'-relations-projects`.user_id='.$user_id.' ORDER BY `'.$__LWF_DB_PREFIX.'-projects`.name';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = '<div class="line" /></div>';
			
			$tb .= '<form action="./index.php?p='.get_pindex('tests').'&s='.get_subpindex( 'tests', 'tests-result' ).'" method="post">';
			$tb .= lang('tests-show-tests').' <label>'.lang('tests-by-project').'</label>: ';
			$tb .= '<select name="project">';
			$default_val ='';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) ) {
				if ($selected == $cur_u['id']) 
					$default_val = 'selected';
				else
					$default_val = '';
				$tb .= '<option value="'.$cur_u['id'].'" '.$default_val.'>'.$cur_u['name'].'</option>';
			}
			$tb .= '</select>';
			$tb .= ' <button type="submit">'.lang('partial-reload').'</button></form> ';
			$tb .= '<div class="line" /></div>';
		}
		return $tb;
	} 
	
    // return combo with project list 
	function getprojects_by_user_for_stats($stats, $container, $user_id, $selected){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE, $CORE;
		
		if ( $CORE->profile['administrator'] || $CORE->profile['leader']  )
			$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects`';
		else
			$sql_req = 'SELECT `'.$__LWF_DB_PREFIX.'-projects`.id, `'.$__LWF_DB_PREFIX.'-projects`.name FROM `'.$__LWF_DB_PREFIX.'-relations-projects` INNER JOIN `'.$__LWF_DB_PREFIX.'-projects` on `'.$__LWF_DB_PREFIX.'-relations-projects`.project_id = `'.$__LWF_DB_PREFIX.'-projects`.id WHERE `'.$__LWF_DB_PREFIX.'-relations-projects`.user_id='.$user_id.' ORDER BY `'.$__LWF_DB_PREFIX.'-projects`.name';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = '<div class="line" /></div>';
			
			$tb .= lang('tests-show-stats');
			$func = 'loadstats_tests';
			$selectname = 'projectstatslist';
			$tb .= ' '.lang('tests-by-project').': <select id="'.$selectname.'-'.$stats.'" style="width:150px" onchange="javascript:'.$func.'('.$user_id.', \''.$stats.'\', \''.$container.'\')">';
			
			$default_val ='';
			if ( $CORE->profile['administrator'] || $CORE->profile['leader']  )
				$tb .= '<option value="0">All</option>';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) ) {
				if ($selected == $cur_u['id']) 
					$default_val = 'selected';
				else
					$default_val = '';
				$tb .= '<option value="'.$cur_u['id'].'" '.$default_val.'>'.$cur_u['name'].'</option>';
			}

			$loader_name = 'stats';
			$tb .= '</select> <img  id="loader-'.$loader_name.'-'.$stats.'" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" class="icon-loader" alt="ajax-loader">';
			$tb .= '<div class="line" /></div>';
		}
		return $tb;
	} 

	// return combo with project list 
	function getprojects_by_user($stats, $container, $user_id, $listing=False){
		global $db, $__LWF_DB_PREFIX, $__LWF_APP_DFLT_STYLE;
		
		$sql_req = 'SELECT `'.$__LWF_DB_PREFIX.'-projects`.id, `'.$__LWF_DB_PREFIX.'-projects`.name FROM `'.$__LWF_DB_PREFIX.'-relations-projects` INNER JOIN `'.$__LWF_DB_PREFIX.'-projects` on `'.$__LWF_DB_PREFIX.'-relations-projects`.project_id = `'.$__LWF_DB_PREFIX.'-projects`.id WHERE `'.$__LWF_DB_PREFIX.'-relations-projects`.user_id='.$user_id.' ORDER BY `'.$__LWF_DB_PREFIX.'-projects`.name';

		$rlst_prjs = $db->query($sql_req);
		if ( ! $rlst_prjs )
			$tb = 'Unable to fetch projects'.$db->str_error();
		else {
			$tb = '<div class="line" /></div>';
			
			if ($listing) {
				$tb .= lang('tests-show-tests');
			} else {
				$tb .= lang('tests-show-stats');
			}
			
			$func = 'loadstats_user';
			if ($listing)
				$func = 'loadtests_user';

			$selectname = 'projectstatslist';
			if ($listing)
				$selectname = 'projecttestslist';

			$tb .= ' '.lang('tests-by-project').': <select id="'.$selectname.'-'.$stats.'" style="width:150px" onchange="javascript:'.$func.'('.$user_id.', \''.$stats.'\', \''.$container.'\')">';

			if (!$listing)
				$tb .= '<option value="-1">All</option><option value="0">Undefined</option>';
			while ( $cur_u = $db->fetch_assoc($rlst_prjs) )
				$tb .= '<option value="'.$cur_u['id'].'">'.$cur_u['name'].'</option>';

			$loader_name = 'stats';
			if ($listing)
				$loader_name = 'tests';
			$tb .= '</select> <img  id="loader-'.$loader_name.'-'.$stats.'" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" class="icon-loader" alt="ajax-loader">';
			$tb .= '<div class="line" /></div>';
		}
		return $tb;
	} 

?>

<div class="bxleft">	
	<?php 
		( $s == $SUB_PAGE_REPO ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_REPO.'\')" >'.lang('tests-repository').'</div>';

		( $s == $SUB_PAGE_RESULTS ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_RESULTS.'\')" >'.lang('tests-result').'</div>';

		( $s == $SUB_PAGE_ENV ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_ENV.'\')" >'.lang('test-environment').'</div><img onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_ENV.'&c=new\')" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/add-green.png" class="link icon-add" alt="add">';

		( $s == $SUB_PAGE_MYSTAT ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_MYSTAT.'\')" >'.lang('tests-my-statistic').'</div>';

		if ( $CORE->profile['administrator']  || $CORE->profile['leader']  )
		{
			( $s == $SUB_PAGE_STATS ) ? $active="selected" : $active ="";
			echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_STATS.'\')" >'.lang('tests-statistics').'</div>';

			( $s == $SUB_PAGE_HISTORY ) ? $active="selected" : $active ="";
			echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_HISTORY.'\')" >'.lang('tests-history').'</div>';
		}
	?>
</div>

<!--<div class="bxright">
	<div class="help"><?php echo lang('help') ?><?php echo get_ajaxloader("loader-help", "0") ?></div>
	<div>
		<ul class="help_list">
		</ul>
	</div>
</div>-->


<div class="bxcenter">
	<div id="box-warn"></div>
<?php
	// gd library is installed ?
	$testGD = get_extension_funcs("gd"); // Grab function list 
	if (!$testGD) 
		echo '<div class="box-warn">GD not installed!</div>';

	// repo
	if ( $s == $SUB_PAGE_REPO )
	{
		// title
		echo '<div class="tests-title-index">'.lang('tests-repository').'</div>';

		$tabsmenu = array( lang('tests-repository-listing') );

		if ( $CORE->profile['administrator'] || $CORE->profile['leader']  ) {
			array_push($tabsmenu, lang('tests-repository-statistics') );
		}

		echo construct_tabmenu($tabsmenu);

		$tb = getprojects_by_user_for_repo( $stats='projects', $container='container-listing-tests', $login=$CORE->profile['id'], $selected=$prj_called);
		$tb .= '<div id="container-listing-tests">';
		$tb .= get_listing_tests($prjId=$prj_called);
		$tb .= '</div>';
		$tabsbody[] = $tb;

		if ( $CORE->profile['administrator'] || $CORE->profile['leader']  ) {
			// statistics
			$tb = '';
			$tb = getprojects_by_user_for_stats( $stats='projects', $container='container-informations-tests', $login=$CORE->profile['id'], $selected=$prj_called);
			$tb .= '<div id="container-informations-tests">';
			$tb .= get_informations_tests($prjId=$prj_called);
			$tb .= '</div>';
			array_push($tabsbody, $tb);
		}

		echo construct_tabbody($tabsbody);

	}

    // test result
	if ( $s == $SUB_PAGE_RESULTS )
	{
		// title
		echo '<div class="tests-title-index">'.lang('tests-result').'</div>';

		$tabsmenu = array( lang('tests-repository-listing') );

		echo construct_tabmenu($tabsmenu);

		$tb = getprojects_by_user_for_testsresult( $stats='projects', $container='container-listing-testsresult', $login=$CORE->profile['id'], $selected=$prj_called);
		$tb .= '<div id="container-listing-testsresult">';
		$tb .= get_listing_testsresult($prjId=$prj_called);
		$tb .= '</div>';
		$tb .= '<div id="container-test-report">';
		$tb .= '</div>';
		$tabsbody[] = $tb;

		echo construct_tabbody($tabsbody);

	}
    
	// environment
	if ( $s == $SUB_PAGE_ENV )
	{
		// title
		echo '<div class="tests-title-index">'.lang('test-environment').'</div>';

		// confirm user deletion form
		if ( $c_called == "del")
		{
			// prepare body for each tabs
			$tabsbody = array();

			if ( isset($_GET['id']) && is_numeric($_GET['id']) )
			{
				$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE id='.$_GET['id'];
				$rlst_usrs = $db->query($sql_req);
				if ( ! $rlst_usrs)
					$tb = 'Unable to get environment'.$db->str_error();
				else
				{	
					$cur_usr = $db->fetch_assoc($rlst_usrs);
					$id =  $cur_usr['id'];
					$tb = '<table border="0"><tbody><tr><td>'.lang('are you sure').' ('.$cur_usr['name'].')</td></tr>';
                    $tb .= '<tr><td><a href="javascript:delelementenv('.$cur_usr['id'].','.$prj_called.')">'.lang('yes').'</a>';
                    $tb .= ' -- ';
                    $tb .= '<a href="./index.php?p='.$TESTS_PAGE.'&s='.$s.'&prj='.$prj_called.'">'.lang('no').'</a></td></tr></tbody></table>';
                    //$tb .= '<a href="javascript:history.back()">'.lang('no').'</a></td></tr></tbody></table>';
				}
			}
			$tabsbody[] = $tb;
		} 
		if ( $c_called == "new" || $c_called == "edit" )
		{
			// construct tab menu
			$tabsmenu = array();
			if ( $c_called == "new" )
				$tabsmenu[] = lang('test-environment-new');
			if ( $c_called == "edit" )
				$tabsmenu[] = lang('test-environment-edit');
			echo construct_tabmenu($tabsmenu);

			// prepare body for each tabs
			$tabsbody = array();

			$el_name = '';
			$el_value = '';
			$el_id = null;
			$el_projectid = $CORE->profile['defaultproject'];

			if ($c_called == "edit")
			{
				if ( isset($_GET['id']) && is_numeric($_GET['id']) )
				{
                    if ( $__LWF_CFG['mysql-test-environment-encrypted'] ) {
                        $sql_req = 'SELECT id, name, AES_DECRYPT(value, "'.$__LWF_CFG['mysql-test-environment-password'].'") as value, project_id FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE id='.$_GET['id'];
                    } else {
                        $sql_req = 'SELECT id, name, value, project_id FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE id='.$_GET['id'];   
                    }
					$rlst_env = $db->query($sql_req);
					if ( ! $rlst_env)
						$tabsbody[] = 'Unable to get element'.$db->str_error();
					else
					{	
						$cur_el = $db->fetch_assoc($rlst_env);
						$el_id = htmlentities($cur_el['id']);
						$el_name = htmlentities($cur_el['name']);
						$el_value = htmlentities($cur_el['value']);
						$el_projectid =  $cur_el['project_id'];
						$button_name = "Update";
						
					}
				}
			}

			$sql_req = 'SELECT `'.$__LWF_DB_PREFIX.'-projects`.id, `'.$__LWF_DB_PREFIX.'-projects`.name FROM `'.$__LWF_DB_PREFIX.'-relations-projects` INNER JOIN `'.$__LWF_DB_PREFIX.'-projects` on `'.$__LWF_DB_PREFIX.'-relations-projects`.project_id = `'.$__LWF_DB_PREFIX.'-projects`.id WHERE `'.$__LWF_DB_PREFIX.'-relations-projects`.user_id='.$CORE->profile['id'];
			$rlst_prjs = $db->query($sql_req);
			if ( ! $rlst_prjs )
				$tb = 'Unable to fetch projects'.$db->str_error();
			else {

				$projects_select = '<select id="req_environment_project" style="width:150px" onchange="">';
				while ( $cur_p = $db->fetch_assoc($rlst_prjs) )
				{
					if ($c_called == "edit" or $c_called == "new")
					{
						if ( $el_projectid != null && $cur_p['id'] == $el_projectid ) {
							$selected_prj = "selected=\"selected\"";
						} else {
							$selected_prj = "";
						}
					}
					$projects_select .= '<option value="'.$cur_p['id'].'" '.$selected_prj.'>'.$cur_p['name'].'</option>';
				}
				$projects_select .= '</select>';

				$tb = '<table border="0" >';
				$tb .= '<tr><td  class="col1">'.lang('test-environment-name').': </td><td><input  id="req_element_name" type="text" value="'.$el_name.'" size="40"></td></tr>';
				$tb .= '<tr><td  class="col1">'.lang('test-environment-project').': </td><td>'.$projects_select.'</td></tr>';

				$tb .= '<tr><td  class="col1">'.lang('test-environment-value').': </td><td>';
  
                //$tb .= '<br /><input type="radio" name="typeval"  value="text" checked disabled />text';
                ///$tb .= '<input type="radio" name="typeval"  value="number" disabled />number';
                //$tb .= '<input type="radio" name="typeval"  value="boolean" disabled />boolean';
                //$tb .= '<input type="radio" name="typeval"  value="dict" disabled />key/value<br />';
                $tb .= '<div class="textwrapper"><textarea  id="req_element_values" type="text" cols="100" rows="20">'.$el_value.'</textarea></div>';
                
                $tb .= '</td></tr>';
                // <button onclick="prettyJsonPrint()">Pretty JSON</button>
				$tb .= '<tr><td class="col1"></td><td align="right" class="col2"><br />';
                $tb .= '[ <a href="javascript:prettyJsonPrint()">Pretty JSON</a> ] ';
                if ($c_called == "edit") {
                    $tb .= '[ <a href="./index.php?p='.$TESTS_PAGE.'&s='.$s.'&prj='.$prj_called.'">'.lang('back').'</a> ] ';
                }
                $tb .= '<input value="'.$button_name.'" type="submit" onclick="javascript:addelementenv('.$el_id.')">';
				$tb .= '</td></tr></table>';
			}
			$tabsbody[] = $tb;
		} elseif ( $c_called == "import" ) {
            $button_name = 'Import';
            
			// construct tab menu
			$tabsmenu = array();
			$tabsmenu[] = lang('test-environment-import');
            echo construct_tabmenu($tabsmenu);
            
            // prepare body for each tabs
			$tabsbody = array();
            
            $tb = '<table border="0" >';
            $tb .= '<tr><td  class="col1">'.lang('test-environment-value').': </td><td><textarea  id="req_env_import" type="text" cols="40" rows="6">';
            if ($_FILES['csv']['size'] > 0) { 
                //get the csv file
                $file = $_FILES['csv']['tmp_name'];
                $handle = fopen($file,"r"); 
                $fileContents = fread($handle, filesize($file));
                fclose($handle);
                $tb .= $fileContents;
            }
            $tb .= '</textarea></td></tr>';
            $tb .= '<tr><td class="col1"></td><td align="right" class="col2"><input value="'.$button_name.'" type="submit" onclick="javascript:importglobalvariables()"></td></tr>';
            $tb .= '</table>';
            $tabsbody[] = $tb;
        } 
        else 
        {
			$tabsmenu = array( lang('test-environment-definition') );
            if ( $CORE->profile['administrator'] )
                $tabsmenu[] = lang('test-environment-manage');
			echo construct_tabmenu($tabsmenu);

			$tb = getprojects_by_user_for_env( $stats='projects', $container='container-definition-env', $login=$CORE->profile['id'], $selected=$prj_called);
			$tb .= '<div id="container-definition-env">';
			$tb .= get_definition_env($prjId=$prj_called);
			$tb .= '</div>';

			$tabsbody[] = $tb;
            
            if ( $CORE->profile['administrator'] ) {
                $tb = '<label>'.lang('test-environment-current').'</label>';
                $tb .= '<ul>';
                $tb .= '<li><input value="'.lang('test-environment-export').'" type="submit" onclick="javascript:exportglobalvariables('.$prj_called.')"></li>';
                

                $tb .= '<li><form action="./index.php?p='.get_pindex('tests').'&s='.get_subpindex( 'tests', 'test-environment' ).'&c=import" method="post" enctype="multipart/form-data" >';
                $tb .= '<input type="submit" name="Submit" value="'.lang('test-environment-import').'" />';
                $tb .= '<input name="csv" type="file" id="csv" />';
                $tb .= '</form></li>'; 
                $tb .= '</ul>';
                array_push($tabsbody, $tb);
            }
		}
		echo construct_tabbody($tabsbody);
	}

	// my statistic
	if ( $s == $SUB_PAGE_MYSTAT )
	{
		// title
		echo '<div class="tests-title-index">'.lang('tests-my-statistic').'</div>';

		$tabsmenu = array( lang('tests-scripts'), lang('tests-testglobals'), lang('tests-testplans'), lang('tests-testsuites'), lang('tests-testunits'), lang('tests-testabstracts'), lang('tests-testcases') );
		echo construct_tabmenu($tabsmenu);

		// extract script statistics
		$tb = getprojects_by_user($stats='sc', $container='container-stats-sc', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-sc">'.get_stats_script($table=$__LWF_DB_PREFIX.'-scripts-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		$tabsbody[] = $tb;

		// extract testglobals statistics
		$tb = getprojects_by_user($stats='tg', $container='container-stats-tg', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-tg">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testglobals-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testplans statistics
		$tb = getprojects_by_user($stats='tp', $container='container-stats-tp', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-tp">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testplans-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testsuites statistics
		$tb = getprojects_by_user($stats='ts', $container='container-stats-ts', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-ts">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testsuites-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testunits statistics
		$tb = getprojects_by_user($stats='tu', $container='container-stats-tu', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-tu">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testunits-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);
        
		// extract testabstracts statistics
		$tb = getprojects_by_user($stats='ta', $container='container-stats-ta', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-ta">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testabstracts-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testcases statistics
		$tb = getprojects_by_user($stats='tc', $container='container-stats-tc', $login=$CORE->profile['id']);
		$tb .= '<div id="container-stats-tc">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testcases-stats', $loginid=$CORE->profile['id'], $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		echo construct_tabbody($tabsbody);
	}

	// statistics
	if ( $s == $SUB_PAGE_STATS )
	{
		if ( !( $CORE->profile['administrator'] || $CORE->profile['leader'] ) ) {
			echo lang('access denied');
			return;
		}

		// title
		echo '<div class="tests-title-index">'.lang('tests-statistics').'</div>';

		$tabsmenu = array( lang('tests-scripts'), lang('tests-testglobals'), lang('tests-testplans'), 
                            lang('tests-testsuites'), lang('tests-testunits'), lang('tests-testabstracts'),
                            lang('tests-testcases'), lang('tests-manage') );
		echo construct_tabmenu($tabsmenu);

		// extract script statistics
		$tb = getusers($stats='sc', $container='container-stats-sc');
		$tb .= getprojects($stats='sc', $container='container-stats-sc');
	//	$tb .= '<br />';
		$tb .= '<div id="container-stats-sc">'.get_stats_script($table=$__LWF_DB_PREFIX.'-scripts-stats', $loginid=null, $graph=$testGD).'</div>';
		$tabsbody[] = $tb;

		// extract testglobals statistics
		$tb = getusers($stats='tg', $container='container-stats-tg');
		$tb .= getprojects($stats='tg', $container='container-stats-tg');
	//	$tb .= '<br />';
		$tb .= '<div id="container-stats-tg">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testglobals-stats', $loginid=null, $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testplans statistics
		$tb = getusers($stats='tp', $container='container-stats-tp');
		$tb .= getprojects($stats='tp', $container='container-stats-tp');
	//	$tb .= '<br />';
		$tb .= '<div id="container-stats-tp">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testplans-stats', $loginid=null, $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testsuites statistics
		$tb = getusers($stats='ts', $container='container-stats-ts');
		$tb .= getprojects($stats='ts', $container='container-stats-ts');
	//	$tb .= '<br />';
		$tb .= '<div id="container-stats-ts">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testsuites-stats', $loginid=null, $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testunits statistics
		$tb = getusers($stats='tu', $container='container-stats-tu');
		$tb .= getprojects($stats='tu', $container='container-stats-tu');
	//	$tb .= '<br />';
		$tb .= '<div id="container-stats-tu">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testunits-stats', $loginid=null, $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);

		// extract testabstracts statistics
		$tb = getusers($stats='ta', $container='container-stats-ta');
		$tb .= getprojects($stats='ta', $container='container-stats-ta');
	//	$tb .= '<br />';
		$tb .= '<div id="container-stats-ta">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testabstracts-stats', $loginid=null, $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);
        
		// extract testcases statistics
		$tb = getusers($stats='tc', $container='container-stats-tc');
		$tb .= getprojects($stats='tc', $container='container-stats-tc');
		//$tb .= '<br />';
		$tb .= '<div id="container-stats-tc">'.get_stats_tests($table=$__LWF_DB_PREFIX.'-testcases-stats', $loginid=null, $graph=$testGD).'</div>';
		array_push($tabsbody, $tb);
        
        $tb = '<ul>';
        $tb .= '<li><input value="'.lang('tests-reset-all').'" type="submit" onclick="javascript:resetallstats()"></li><br />';
        $tb .= '<li><input value="'.lang('tests-reset-by').'" type="submit" onclick="javascript:resetstatsby(\'rst\')"> '.getusers_select('rst').getprojects_select('rst').'</li><br />';
        $tb .= '</ul>';
        array_push($tabsbody, $tb);
        
		echo construct_tabbody($tabsbody);
	}

	// run history
	if ( $s == $SUB_PAGE_HISTORY )
	{
		if ( !( $CORE->profile['administrator'] || $CORE->profile['leader'] ) ) {
			echo lang('access denied');
			return;
		}
		
		// title
		echo '<div class="tests-title-index">'.lang('tests-history').'</div>';

		$tabsmenu = array( lang('tests-history-runs'), lang('tests-history-statistics') );
		echo construct_tabmenu($tabsmenu);

		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-tasks-history` ORDER BY id DESC';
		$rlst_tasks = $db->query($sql_req);
		if ( ! $rlst_tasks)
			$tb = 'Unable to fetch tasks history'.$db->str_error();
		else
		{
			$tb = '';
			$tb = '<table id="taskhistory"><tr><td><b>'.lang('tests-history-date').'</b></td><td><b>'.lang('tests-history-duration').'</b><td><b>'.lang('tests-history-task').'</b></td><td><b>'.lang('tests-history-author').'</b></td><td><b>'.lang('tests-history-type').'</b></td><td><b>'.lang('tests-history-result').'</b></td></tr>';

				while ($cur_t = $db->fetch_assoc($rlst_tasks))
				{
					$tb .= '<tr class="list"><td>'.date('Y-m-d H:i:s', floatval($cur_t['realruntime'])).'</td><td>'.round($cur_t['eventduration'], 2).'</td><td>'.$cur_t['eventname'].'</td><td>'.$cur_t['eventauthor'].'</td><td>'.$RUN_TYPE[$cur_t['eventtype']].'</td><td>'.$cur_t['eventresult'].'</td></tr>';
				}
				$tb .= "</table>";
		}

		$tabsbody[] = $tb;

		// statistics
		$sql_req = 'SELECT SUM( IF(eventtype='.array_search(NOW, $RUN_TYPE).',1,0) ) AS \''.NOW.'\', SUM( IF(eventtype='.array_search(AT, $RUN_TYPE).',1,0) ) AS \''.AT.'\', SUM( IF(eventtype='.array_search(IN, $RUN_TYPE).',1,0) ) AS \''.IN.'\', SUM( IF(eventtype='.array_search(EVERYSECOND, $RUN_TYPE).',1,0) ) AS \''.EVERYSECOND.'\', SUM( IF(eventtype='.array_search(EVERYMINUTE, $RUN_TYPE).',1,0) ) AS \''.EVERYMINUTE.'\', SUM( IF(eventtype='.array_search(EVERYHOUR, $RUN_TYPE).',1,0) ) AS \''.EVERYHOUR.'\', SUM( IF(eventtype='.array_search(HOURLY, $RUN_TYPE).',1,0) ) AS \''.HOURLY.'\', SUM( IF(eventtype='.array_search(DAILY, $RUN_TYPE).',1,0) ) AS \''.DAILY.'\', SUM( IF(eventtype='.array_search(WEEKLY, $RUN_TYPE).',1,0) ) AS \''.WEEKLY.'\', SUM( IF(eventtype='.array_search(SUCCESSIVE, $RUN_TYPE).',1,0) ) AS \''.SUCCESSIVE.'\', SUM( IF(eventtype='.array_search(RUNUNDEFINED, $RUN_TYPE).',1,0) ) AS \''.RUNUNDEFINED.'\' FROM `'.$__LWF_DB_PREFIX.'-tasks-history`';
		
		$rlst_tasks = $db->query($sql_req);
		if ( ! $rlst_tasks)
			$tb = 'Unable to get stats tasks '.$db->str_error();
		else
		{
			// init variables
			$nb_total = 0; $nb_now = 0; $nb_at = 0; $nb_in = 0; $nb_everysec = 0;
			$nb_everymin = 0; $nb_everyhour = 0; $nb_daily = 0; $nb_hourly = 0; 
			$nb_weekly = 0; $nb_successive = 0; $nb_undef = 0;

			// fetch data
			$cur_stats = $db->fetch_assoc($rlst_tasks);
			$nb_now = $cur_stats[NOW]; $nb_at = $cur_stats[AT]; $nb_in = $cur_stats[IN]; $nb_everysec = $cur_stats[EVERYSECOND];
			$nb_everymin = $cur_stats[EVERYMINUTE]; $nb_everyhour = $cur_stats[EVERYHOUR]; $nb_daily = $cur_stats[DAILY]; $nb_hourly = $cur_stats[HOURLY]; 
			$nb_weekly = $cur_stats[WEEKLY]; $nb_successive = $cur_stats[SUCCESSIVE]; $nb_undef = $cur_stats[RUNUNDEFINED];

			// compute total
			$nb_total = $nb_now + $nb_at + $nb_in + $nb_everysec + $nb_everymin + $nb_everyhour + $nb_daily + $nb_hourly + $nb_weekly + $nb_successive + $nb_undef;

			$tb = '<span class="dotted">'.lang('result').'</span>';
			$tb .= '<table>';
			$tb .= '<tr><td class="table tablekey">'.NOW.'</td><td>'.$nb_now.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.AT.'</td><td>'.$nb_at.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.IN.'</td><td>'.$nb_in.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.EVERYSECOND.'</td><td>'.$nb_everysec.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.EVERYMINUTE.'</td><td>'.$nb_everymin.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.EVERYHOUR.'</td><td>'.$nb_everyhour.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.DAILY.'</td><td>'.$nb_daily.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.HOURLY.'</td><td>'.$nb_hourly.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.WEEKLY.'</td><td>'.$nb_weekly.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.SUCCESSIVE.'</td><td>'.$nb_successive.'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.RUNUNDEFINED.'</td><td>'.$nb_undef.'</td></tr>';
			$tb .= '<tr><td class="table tablekey"></td><td>'.$nb_total.'</td></tr>';
			$tb .= '</table>';;


			if ($nb_total) {
				$tb .= '<br /><span class="dotted">'.lang('graphic').'</span>';
				$tb .= '<br/><img class="tablekey" src="chart.php?tt=h&amp;d='.$nb_now.','.$nb_at.','.$nb_in.','.$nb_everysec.','.$nb_everymin.','.$nb_everyhour.','.$nb_hourly.','.$nb_daily.','.$nb_weekly.','.$nb_successive.','.$nb_undef.'"/><br/>';
			} else {
				$tb = '';
			}
		}

		array_push($tabsbody, $tb);
		echo construct_tabbody($tabsbody);
	}
?>
</div>

