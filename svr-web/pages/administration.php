<?php
	/*
	---------------------------------------------------------------
	 Copyright (c) 2010-2017 Denis Machard. All rights reserved.

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

	if (!defined('CONFIG_OK'))
			exit( lang('access denied') );
	
	if ( $CORE->profile == null )
		exit( lang('access denied') );

	// prepare index page
	$INDEX_PAGE = get_pindex('administration');
	$SUB_PAGE_PROFILE =  get_subpindex( 'administration', 'admin-profile' ) ;
	$SUB_PAGE_USERS =  get_subpindex( 'administration', 'admin-users' ) ;
	$SUB_PAGE_PROJECTS =  get_subpindex( 'administration', 'admin-projects' ) ;
	$SUB_PAGE_CONFIG =  get_subpindex( 'administration', 'admin-config' ) ;

	// default sub-menu selected
	if ( $CORE->profile['administrator'] )
		$s = $SUB_PAGE_USERS;
	else
		$s = $SUB_PAGE_PROFILE;

	if ( isset($_GET['s']) )
	{
		$s_called = $_GET['s'];
		(!$s_called) ? $s=1 : $s=$s_called;
	}

	$c_called = null;
	if ( isset($_GET['c']) )
	{
		$c_called = $_GET['c'];
		if ( !( $c_called == "new" || $c_called == "edit" || $c_called == "del" || $c_called == "pwd" ) )
			$c_called = null;
	}
	$button_name = lang('add');
?>
<div class="bxleft">
	<?php 
		
		( $s == $SUB_PAGE_PROFILE ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_PROFILE.'\')" >'.lang('admin-profile').'</div>';

		if ( $CORE->profile['administrator'] )
		{
			( $s == $SUB_PAGE_USERS ) ? $active="selected" : $active ="";
			echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_USERS.'\')" >'.lang('admin-users').'</div><img onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_USERS.'&c=new\')" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/add-green.png" class="link icon-add" alt="add" title="'.lang('admin-users-new-account').'">';

			( $s == $SUB_PAGE_PROJECTS ) ? $active="selected" : $active ="";
			echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_PROJECTS.'\')" >'.lang('admin-projects').'</div><img onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_PROJECTS.'&c=new\')" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/add-green.png" class="link icon-add" alt="add" title="'.lang('admin-projects-new').'">';

			( $s == $SUB_PAGE_CONFIG ) ? $active="selected" : $active ="";
			echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_CONFIG.'\')" >'.lang('admin-config').'</div>';

		}
	?>
</div>

<!--<div class="bxright">
	<div class="help"><?php echo lang('help') ?><?php echo get_ajaxloader("loader-help", "0") ?></div>
	<div>
		<ul class="help_list">
		<?php
			if ( $CORE->profile['administrator'] ) {
				echo '<li><a href="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_USERS.'&c=new\')">'.lang('admin-users-new-account').'?</a>'.'<ul><li>'.lang('admin-users-email').': '.lang('admin-users-edit-help').'</li></ul> </li>';
				echo '<li><a href="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_USERS.'\')">'.lang('admin-users-user').' '.lang('status').'</a>: <ul><li>'.lang('admin-users-online').': '.lang('admin-users-online-round').'</li><li>'.lang('admin-users-offline').': '.lang('admin-users-offline-round').'</li><li>'.lang('admin-users-disabled').': '.lang('admin-users-disabled-round').'</li></ul> </li>';
				echo '<li><a href="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_PROFILE.'&c=new\')">'.lang('admin-users-update-my-pwd').'</a>'.'</li>';
			} else {
				echo '<li><a href="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_PROFILE.'&c=new\')">'.lang('admin-users-update-my-pwd').'</a>'.'</li>';
			}
		?>
		</ul>
	</div>
</div>-->

<div class="bxcenter">
	<div id="box-warn"></div>

<?php

		// profile part
		if ( $s == $SUB_PAGE_PROFILE )
		{

			// title
			echo '<div class="admin-title-index">'.lang('admin-profile').'</div>';

			// construct tab menu
			$tabsmenu = array( lang('account'), lang('password') );
			if ( $CORE->profile['administrator'] || $CORE->profile['tester']  ) {
				array_push($tabsmenu, lang('admin-users-notifications'));
			}
			echo construct_tabmenu($tabsmenu);
			
			// login
			$tb = '<table border="0" ><tr><td  class="col1">'.lang('admin-users-login').': </td><td><input disabled id="req_login" type="text" value="'.$CORE->profile['login'] .'"></td></tr>';
			$tb .= '<tr><td  class="col1">'.lang('admin-users-email').': </td><td><input disabled id="req_login" type="text" value="'.$CORE->profile['email'] .'"></td></tr>';
			$tb .= '<tr><td  class="col1">'.lang('admin-users-lang').': </td><td><input disabled id="req_login" type="text" value="'.$CORE->profile['lang'] .'"></td></tr>';
			$tb .= '<tr><td  class="col1">'.lang('admin-users-style').': </td><td><input disabled id="req_login" type="text" value="'.$CORE->profile['style'] .'"></td></tr>';
			$tb .= "</table>";
	
			$tabsbody[] = $tb;

			// construct tab body
			$tb = '<p>'.lang('admin-users-pass').'</p>';
			$tb .= '<table border="0"><tbody><tr><td class="col1">'.lang('admin-users-old-pwd').': </td><td><input id="req_old_pwd" type="password"></td></tr>';
			$tb .= '<tr><td class="col1">'.lang('admin-users-new-pwd').': </td><td><input id="req_new_pwd" type="password"></td></tr>';
			$tb .= '<tr><td></td><td align="right"><input value="'.lang('update').'" type="submit" onclick="javascript:changepwduser('.$CORE->profile['id'].')"></td></tr></tbody></table>';
			$tabsbody[] = $tb;
			
			
			$checked = '';
			$visible = 'style="display:block"';
			$notifications = explode(";", $CORE->profile['notifications'] );

			if ( $notifications[0] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs = '<input type="checkbox" id="pass" '.$checked.' >'.lang('pass');
			if ( $notifications[1] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs .= '<input type="checkbox" id="fail" '.$checked.' >'.lang('fail');
			if ( $notifications[2] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs .= '<input type="checkbox" id="undef" '.$checked.' >'.lang('undef');
			$tb = '<table id="notifs" '.$visible.'><tr><td  class="col1">'.lang('my-tests-runs').': </td><td>'.$notifs .'</td></tr>';

			if ( $notifications[3] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs_tasks = '<input type="checkbox" id="complete" '.$checked.' >'.lang('complete');
			if ( $notifications[4] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs_tasks .= '<input type="checkbox" id="error" '.$checked.' >'.lang('error');
			if ( $notifications[5] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs_tasks .= '<input type="checkbox" id="killed" '.$checked.' >'.lang('killed');
			if ( $notifications[6] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
			$notifs_tasks .= '<input type="checkbox" id="cancelled" '.$checked.' >'.lang('cancelled');
			$tb .= '<tr><td class="col1">'.lang('my-tasks-runs').': </td><td>'.$notifs_tasks .'</td></tr>';
			
			$tb .= '<tr><td></td><td align="right"><input value="'.lang('update').'" type="submit" onclick="javascript:changenotifsuser('.$CORE->profile['id'].')"></td></tr></table>';


			array_push($tabsbody, $tb);
		
			echo construct_tabbody($tabsbody);

		}

		// config part
		if ( $s == $SUB_PAGE_CONFIG )
		{
			if ( ! $CORE->profile['administrator'] ) {
				echo lang('access denied');
				return;
			} 

			// title
			echo '<div class="admin-title-index">'.lang('admin-config').'</div>';

			// construct tab menu
			$tabsmenu = array();
			$tabsmenu[] = lang('admin-config-list');

			echo construct_tabmenu($tabsmenu);

			// prepare body for each tabs
			$tabsbody = array();

			$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-config`';
			$rlst_prjs = $db->query($sql_req);
			if ( ! $rlst_prjs)
				$tb = 'Unable to fetch config'.$db->str_error();
			else
			{	
				$tb = '<table id="tusrlst"><tr><td><b>'.lang('name').'</b></td><td><b>'.lang('value').'</b></td></tr>';

				while ($cur_u = $db->fetch_assoc($rlst_prjs))
				{
					$tb .= '<tr id="box-admin-row" class="list"><td>'.htmlentities($cur_u['opt']).'</td><td>'.htmlentities($cur_u['value']).'</td></tr>' ;
				}
				$tb .= "</table>";
				
			}
			$tabsbody[] = $tb;
			// construct tab body
			echo construct_tabbody($tabsbody);
		}
	
		// projects part
		if ( $s == $SUB_PAGE_PROJECTS )
		{
			if ( ! $CORE->profile['administrator'] ) {
				echo lang('access denied');
				return;
			} 

			// title
			echo '<div class="admin-title-index">'.lang('admin-projects').'</div>';

			if ( $c_called == "del")
			{
				// prepare body for each tabs
				$tabsbody = array();

				if ( isset($_GET['id']) && is_numeric($_GET['id']) )
				{
					$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE id='.$_GET['id'].' ORDER BY name';
					$rlst_usrs = $db->query($sql_req);
					if ( ! $rlst_usrs)
						$tb = 'Unable to get projects'.$db->str_error();
					else
					{	
						$cur_usr = $db->fetch_assoc($rlst_usrs);
						$id =  $cur_usr['id'];
						$tb = '<table border="0"><tbody><tr><td>'.lang('are you sure').' ('.$cur_usr['name'].')</td></tr>';
                        $tb .= '<tr><td><a href="javascript:delproject('.$cur_usr['id'].')">'.lang('yes').'</a>';
                        $tb .= ' -- ';
                        $tb .= '<a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'">'.lang('no').'</a></td></tr></tbody></table>';
                        // $tb .= '<a href="javascript:history.back()">'.lang('no').'</a></td></tr></tbody></table>';
					}
				}
				$tabsbody[] = $tb;
				// construct tab body
				echo construct_tabbody($tabsbody);

			}
			elseif ( $c_called == "new" || $c_called == "edit")
			{
				// construct tab menu
				$tabsmenu = array();
				if ( $c_called == "new" )
					$tabsmenu[] = lang('admin-projects-new');
				if ( $c_called == "edit" )
					$tabsmenu[] = lang('admin-projects-edit');
				echo construct_tabmenu($tabsmenu);

				// prepare body for each tabs
				$tabsbody = array();

				$val_name = "";
				$id = null;
				if ($c_called == "edit")
				{
					if ( isset($_GET['id']) && is_numeric($_GET['id']) )
					{
						$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE id='.$_GET['id'].' ORDER BY name';
						$rlst_prjts = $db->query($sql_req);
						if ( ! $rlst_prjts)
							$tabsbody[] = 'Unable to get projects'.$db->str_error();
						else
						{	
							$cur_prj = $db->fetch_assoc($rlst_prjts);
							$val_name = htmlentities($cur_prj['name']);
							$button_name = "Update";
							$id =  $cur_prj['id'];
						}
					}
				}

				$tb = '<table border="0" ><tr><td  class="col1">'.lang('admin-projects-name').': </td><td><input  id="req_name" type="text" value="'.$val_name.'"></td></tr>';

				$tb .= '<br /><table><tr><td class="col1"></td><td align="right" class="col2"><input value="'.$button_name.'" type="submit" onclick="javascript:addproject('.$id.')"></td></tr></table>';

				$tabsbody[] = $tb;
				// construct tab body
				echo construct_tabbody($tabsbody);
			}
			else // display all projects
			{
				// construct tab menu
				$tabsmenu = array( lang('admin-projects-list'), lang('admin-projects-statistics') );
				echo construct_tabmenu($tabsmenu);

				// prepare body for each tabs
				$tabsbody = array();

				// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` ORDER BY name';
                
                $sql_req = '(SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE name="Common")';
                $sql_req .= 'UNION ALL';
                $sql_req .= '(SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE name<>"Common" ORDER BY name)';
                
				$rlst_prjs = $db->query($sql_req);
				if ( ! $rlst_prjs)
					$tb = 'Unable to fetch projects'.$db->str_error();
				else
				{	
					$tb = '<table id="tusrlst"><tr><td><b>'.lang('id').'</b></td><td><b>'.lang('name').'</b></td><td></td><td></td></tr>';

					while ($cur_u = $db->fetch_assoc($rlst_prjs))
					{
						$log = htmlentities($cur_u['name']);
						$link_edit = '<a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'&c=edit&id='.$cur_u['id'].'">'.lang('edit').'</a>';
						$link_delete = '<a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'&c=del&id='.$cur_u['id'].'">'.lang('delete').'</a>';
						
						// default project common can not be deleted
						if ( $cur_u['id'] == 1 )
						{
							$link_delete = "";
						}

						$tb .= '<tr id="box-admin-row" class="list"><td>'.$cur_u['id'].'</td><td>'.htmlentities($cur_u['name']).'</td><td>'.$link_edit.'</td><td>'.$link_delete.'</td></tr>' ;
					}
					$tb .= "</table>";
					
				}
				$tabsbody[] = $tb;

				// statistic
				$tb = '';
				$sql_req = 'SELECT COUNT(*) as prjNb FROM  `'.$__LWF_DB_PREFIX.'-projects`';
				$rlst_usrs_stats = $db->query($sql_req);
				if ( ! $rlst_usrs_stats)
					$tb = 'Unable to get project stats '.$db->str_error();
				else
				{
					$cur_prjs_stats = $db->fetch_assoc($rlst_usrs_stats);
					$tb .= '<span class="dotted">'.lang('total').'</span>';
					$tb .= '<table><tr><td class="table tablekey">'.lang('admin-projects-total').'</td><td>'.$cur_prjs_stats['prjNb'].'</td></tr>';
					$tb .= '</table>';
				}

				
				array_push($tabsbody, $tb);

				// construct tab body
				echo construct_tabbody($tabsbody);
			}
		}

		// users part
		if ( $s == $SUB_PAGE_USERS )
		{
			if ( ! $CORE->profile['administrator'] ) {
				echo lang('access denied');
				return;
			} 

			// title
			echo '<div class="admin-title-index">'.lang('admin-users').'</div>';

			// confirm user deletion form
			if ( $c_called == "del")
			{
				// prepare body for each tabs
				$tabsbody = array();

				if ( isset($_GET['id']) && is_numeric($_GET['id']) )
				{
					$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE id='.$_GET['id'];
					$rlst_usrs = $db->query($sql_req);
					if ( ! $rlst_usrs)
						$tb = 'Unable to get user'.$db->str_error();
					else
					{	
						$cur_usr = $db->fetch_assoc($rlst_usrs);
						$id =  $cur_usr['id'];
						$tb = '<table border="0"><tbody><tr><td>'.lang('are you sure').' ('.$cur_usr['login'].')</td></tr>';
                        $tb .= '<tr><td><a href="javascript:deluser('.$cur_usr['id'].')">'.lang('yes').'</a>';
                        $tb .= ' -- ';
                        $tb .= '<a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'">'.lang('no').'</a></td></tr></tbody></table>';
					}
				}
				$tabsbody[] = $tb;
				// construct tab body
				echo construct_tabbody($tabsbody);
			}
			// change password form
			elseif ( $c_called == "pwd")
			{
				// construct tab menu
				$tabsmenu = array( lang('password') );
				echo construct_tabmenu($tabsmenu);

				// prepare body for each tabs
				$tabsbody = array();

				if ( isset($_GET['id']) && is_numeric($_GET['id']) )
				{
					$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE id='.$_GET['id'];
					$rlst_usrs = $db->query($sql_req);
					if ( ! $rlst_usrs)
						$tb = 'Unable to get user'.$db->str_error();
					else
					{	
						$cur_usr = $db->fetch_assoc($rlst_usrs);
						$id =  $cur_usr['id'];
						$button_name = lang('update');
						$tb = lang('admin-users-user').': '.$cur_usr['login'].'<br /><br />';
						$tb .= '<table border="0"><tbody><tr><td class="col1">'.lang('admin-users-old-pwd').': </td><td><input id="req_old_pwd" type="password"></td></tr>';
						$tb .= '<tr><td class="col1">'.lang('admin-users-new-pwd').': </td><td><input id="req_new_pwd" type="password"></td></tr>';
						$tb .= '<tr><td></td><td align="right">';
						if ( $CORE->profile['administrator'] ) {
							$tb .= '<input value="'.lang('reset').'" type="submit" onclick="javascript:resetpwduser('.$id.')">';
						}
						$tb .= '<input value="'.$button_name.'" type="submit" onclick="javascript:changepwduser('.$id.')">';
						$tb .= '</td></tr>';
						$tb .= '</tbody></table>';
					}
				}
				
				$tabsbody[] = $tb;
				// construct tab body
				echo construct_tabbody($tabsbody);
			}
			// add or edit user form
			elseif ( $c_called == "new" || $c_called == "edit")
			{
				// construct tab menu
				$tabsmenu = array();
				if ( $c_called == "new" )
					$tabsmenu[] = lang('admin-users-new-account');
				if ( $c_called == "edit" )
					$tabsmenu[] = lang('admin-users-edit-account');

				echo construct_tabmenu($tabsmenu);

				// prepare body for each tabs
				$tabsbody = array();

				$val_login = ""; $val_pwd = ""; $val_email = "";
				$id = null;
				$selected_admin = null;
				$selected_monitor = null;
				$selected_tester = null;
				// $selected_developer = null;
				// $selected_system = null;
				$selected_style = null;
				$selected_lang = null;
				$notifications = null;
				// $selected_cli = null;
				// $selected_gui = null;
				// $selected_web = null;
				$default_project = null;
				if ($c_called == "edit")
				{
					if ( isset($_GET['id']) && is_numeric($_GET['id']) )
					{
						$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` WHERE id='.$_GET['id'];
						$rlst_usrs = $db->query($sql_req);
						if ( ! $rlst_usrs)
							$tabsbody[] = 'Unable to get user'.$db->str_error();
						else
						{	
							$cur_usr = $db->fetch_assoc($rlst_usrs);
							$user_id = htmlentities($cur_usr['id']);
							$val_login = htmlentities($cur_usr['login']);
							$val_email = htmlentities($cur_usr['email']);
							$button_name = "Update";
							$id =  $cur_usr['id'];
							$selected_admin = $cur_usr['administrator'];
							$selected_monitor = $cur_usr['leader'];
							$selected_tester = $cur_usr['tester'];
							$selected_lang = $cur_usr['lang'];
							$selected_style = $cur_usr['style'];
							$default_project = $cur_usr['defaultproject'];
							// PASS;FAIL;UNDEF;COMPLETE;ERROR;KILLED;CANCELLED
							// false;false;false;false;false;false;false;
							$notifications = explode(";", $cur_usr['notifications']);
						}
					}
				}

				// login
				$req_login = "";
                if ($id <= 6) {
                    if ($c_called == "edit")
                        $req_login = "disabled";
                }
				$tb = '<table border="0" ><tr><td></td><td><div class="line" /></div> </td></tr>';
                $tb .= '<tr><td  class="col1">'.lang('admin-users-login').': </td><td><input '.$req_login.' id="req_login" type="text" value="'.$val_login.'"></td></tr>';
				
				// password
				$req_pwd = "";
				if ($c_called == "edit") {
					$req_pwd = "disabled";
				}
				$tb .= '<tr><td  class="col1">'.lang('password').': </td><td><input '.$req_pwd.' id="req_pwd" type="password" value="'.$val_pwd.'"></td></tr>';
				
                $val_apikey = '';
                
                if ($c_called == "edit") {
                    $val_apiid = $cur_usr['apikey_id'];
                    $val_apisecret = $cur_usr['apikey_secret'];
                    if ( $val_apiid != null and $val_apisecret != null) {
                      $val_apikey = base64_encode( $val_apiid.":".$val_apisecret);
                    }
                }
                $tb .= '<tr><td  class="col1">'.lang('api-key').': </td><td><label>'.$val_apikey.'</label></td></tr>';
                
				// levels
				$checked = '';
				$disabled = '';
				if ($c_called == "edit")
				{
					if ($id <= 6) {
						$disabled = 'disabled';
					}
				}
                
				if ( $selected_admin ) { $checked='checked="true"'; } else {$checked = ''; };
				$levels = '<input type="radio" name="level" id="req_level_admin" '.$checked.' '.$disabled.' />'.lang('administrator');
				if ( $selected_monitor ) { $checked='checked="true"'; } else {$checked = ''; };
				$levels .= '<input type="radio" name="level" id="req_level_monitor" '.$checked.' '.$disabled.' />'.lang('monitor');
				if ( $selected_tester ) { $checked='checked="true"'; } else {$checked = ''; };
                // set default value to tester if nothing is checked
                if ( !$selected_admin and !$selected_monitor and !$selected_tester) {
                    $checked='checked="true"';
                }
				$levels .= '<input type="radio" name="level" id="req_level_tester" '.$checked.' '.$disabled.' />'.lang('tester');

				$tb .= '<tr><td></td><td><div class="line" /></div> </td></tr><tr><td  class="col1">'.lang('admin-users-rights').': </td><td>'.$levels.'</td></tr>';

				// email
				$tb .= '<tr><td></td><td><div class="line" /></div> </td></tr><tr><td  class="col1">'.lang('admin-users-email').': </td><td><input id="req_email" type="text" size="30" value="'.$val_email.'"></td><td><small>(ex: user1@foo.com; user2@foo.com)</small></td></tr>';
				
				// language
				$selected = "";
				$langs_available = get_installed_lang();
				$opts = "";
				foreach ($langs_available as $cur_lang) {
					if ( $selected_lang != null &&  $selected_lang == $cur_lang)
						$selected = "selected=\"selected\"";
					else
						$selected = "";
					$opts .= '<option value="'.$cur_lang.'" '.$selected.'>'.$cur_lang.'</option>' ;
				}
				$tb .= '<tr><td  class="col1">'.lang('admin-users-lang').': </td><td><select id="req_lang">'.$opts.'</select></td></tr>';
				
				// style
				$selected = "";
				$style_available = get_installed_style();
				$opts = "";
				foreach ($style_available as $style) {
					if ( $selected_style != null &&  $selected_style == $style)
						$selected = "selected=\"selected\"";
					else
						$selected = "";
					$opts .= '<option value="'.$style.'" '.$selected.'>'.$style.'</option>' ;
				}
				$tb .= '<tr><td  class="col1">'.lang('admin-users-style').': </td><td><select id="req_style">'.$opts.'</select></td></tr></table>';
			
				// notifications
				$checked = '';
				if ( $notifications[0] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs = '<input type="checkbox" id="pass" '.$checked.' >'.lang('pass');
				if ( $notifications[1] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs .= '<input type="checkbox" id="fail" '.$checked.' >'.lang('fail');
				if ( $notifications[2] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs .= '<input type="checkbox" id="undef" '.$checked.' >'.lang('undef');
				$tb .= '<table id="notifs" style="display:block"><tr><td></td><td><div class="line" /></div> </td></tr><tr><td  class="col1">'.lang('my-tests-runs').': </td><td>'.$notifs .'</td></tr>';

				if ( $notifications[3] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs_tasks = '<input type="checkbox" id="complete" '.$checked.' >'.lang('complete');
				if ( $notifications[4] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs_tasks .= '<input type="checkbox" id="error" '.$checked.' >'.lang('error');
				if ( $notifications[5] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs_tasks .= '<input type="checkbox" id="killed" '.$checked.' >'.lang('killed');
				if ( $notifications[6] == "true" ) { $checked='checked="true"'; } else {$checked = ''; };
				$notifs_tasks .= '<input type="checkbox" id="cancelled" '.$checked.' >'.lang('cancelled');
				$tb .= '<tr><td class="col1">'.lang('my-tasks-runs').': </td><td>'.$notifs_tasks .'</td></tr></table>';

				//projects
				$projects = '';
				$sql_req = "SELECT * FROM `".$__LWF_DB_PREFIX."-relations-projects` ";
				if ($c_called == "edit")
				{
					$sql_req .= " WHERE user_id='".$user_id."'";
				}

				$rlt_prjs = $db->query($sql_req);
				if ( ! $rlt_prjs)
					$tb = 'Unable to fetch relations projects'.$db->str_error();
				else
				{	
					// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` ORDER BY name';
                    
                    $sql_req = '(SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE name="Common")';
                    $sql_req .= 'UNION ALL';
                    $sql_req .= '(SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE name<>"Common" ORDER BY name)';
                    
					$rlst_prjs = $db->query($sql_req);
					if ( ! $rlst_prjs)
						$tb = 'Unable to fetch projects'.$db->str_error();
					else
					{	
						$i = 0;
						$all_prjs = array();
						while ($cur_r = $db->fetch_assoc($rlt_prjs))
						{
							array_push($all_prjs, $cur_r);
						}
						while ($cur_u = $db->fetch_assoc($rlst_prjs))
						{
							$checked='';
							$disabled_prj='';
							if ( $id != null ) {
								foreach ($all_prjs as $v) {
									if ( $v['project_id'] == $cur_u['id']) { $checked='checked="true"';  }
								}
							}
							if ($cur_u['id']== "1") { $disabled_prj='disabled'; $checked='checked="true"'; }
							$projects .= '<input type="checkbox" name="checkbox_projects" '.$checked.' '.$disabled_prj.' value="'.$cur_u['id'].'">'.$cur_u['name'];
							if ( $i % 2) { $projects .=  '<br />'; };
							$i++;
						}
		
					}
				}
				$tb .= '<table id="projects" style="display:block"><tr><td></td><td><div class="line" /></div> </td></tr><tr><td  class="col1">'.lang('admin-projects').': </td><td>'.$projects .'</td></tr>';
				//default project
				$selected_prj = "";
				// $sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` ORDER BY name';
                
                $sql_req = '(SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE name="Common")';
                $sql_req .= 'UNION ALL';
                $sql_req .= '(SELECT * FROM `'.$__LWF_DB_PREFIX.'-projects` WHERE name<>"Common" ORDER BY name)';
                
				$rlst_prjs = $db->query($sql_req);
				if ( ! $rlst_prjs)
					$tb = 'Unable to fetch projects'.$db->str_error();
				else
				{	
					$opts = "";
					while ($cur_p = $db->fetch_assoc($rlst_prjs))
					{
						if ($c_called == "edit")
						{
							if ( $default_project != null && $cur_p['id'] == $default_project ) {
								$selected_prj = "selected=\"selected\"";
							} else {
								$selected_prj = "";
							}
						}
						$opts .= '<option value="'.$cur_p['id'].'" '.$selected_prj.'>'.$cur_p['name'].'</option>' ;
					}
					$tb .= '<tr><td  class="col1">'.lang('admin-default-project').': </td><td><select id="req_default_project">'.$opts.'</select></td></tr><tr><td></td><td><div class="line" /></div> </td></tr></table>';
				}


				$tb .= '<br /><table><tr><td class="col1"></td><td align="right" class="col2"><input value="'.$button_name.'" type="submit" onclick="javascript:adduser('.$id.')"></td></tr></table>';


				$tabsbody[] = $tb;
				// construct tab body
				echo construct_tabbody($tabsbody);
			}
			else // display all users form
			{
				// construct tab menu
				$tabsmenu = array( lang('admin-users-list-users'), lang('admin-users-statistics') );

				echo construct_tabmenu($tabsmenu);

				// prepare body for each tabs
				$tabsbody = array();

				$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-users` ORDER BY login';
				$rlst_prjs = $db->query($sql_req);
				if ( ! $rlst_prjs)
					$tb = 'Unable to fetch users'.$db->str_error();
				else
				{	
					$tb = '<table id="tusrlst"><tr><td><b>'.lang('status').'</b></td><td><b>'.lang('login').'</b></td><td><b>'.lang('admin-users-default').'</b></td><td><b>'.lang('admin-users-rights').'</b></td><td><b>'.lang('admin-users-email').'</b></td>';
                    $tb .= '<td></td><td></td><td></td><td></td><td></td><td></td></tr>';

					while ($cur_u = $db->fetch_assoc($rlst_prjs))
					{
                        if ( $cur_u['login'] == "system" ) {
                            continue;
                        }
                        
						$log = htmlentities($cur_u['login']);
						$link_edit = ' [ <a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'&c=edit&id='.$cur_u['id'].'">'.lang('edit').'</a> ] ';
						$link_delete = ' [ <a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'&c=del&id='.$cur_u['id'].'">'.lang('delete').'</a> ] ';
						$link_changepwd = ' [ <a href="./index.php?p='.$INDEX_PAGE.'&s='.$s.'&c=pwd&id='.$cur_u['id'].'">'.lang('password').'</a> ] ';
						$link_duplicate = ' [ <a href="javascript:duplicateuser('.$cur_u['id'].', 1)">'.lang('duplicate').'</a> ] ';
                        
						// online status
						$online =  '<img src="./images/status-offline.png">';
						if ( $cur_u['online'] ) {
							$online =  '<img src="./images/status-online.png">';
							$link_disconnect = ' [ <a href="javascript:disconnectuser(\''.$cur_u['login'].'\')">'.lang('admin-users-disconnect').'</a> ] ';
						} else {
							$link_disconnect = '';
						}

						if ( $cur_u['active'] ) {
							$link_active = ' [ <a href="javascript:enableuser('.$cur_u['id'].', 0)">'.lang('disable').'</a> ] ';
							
						} else {
							$link_active = ' [ <a href="javascript:enableuser('.$cur_u['id'].', 1)">'.lang('enable').'</a> ] ';
							$online =  '<img src="./images/status-disabled.png">';
						}

						// default user can not be deleted
						if ( $cur_u['default'] )
						{
							$link_delete = "";
							//$link_active = "";
						}


						if ( $cur_u['login'] == $CORE->profile['login'] )
						{
							$link_delete = "";
						}

						// extract access level
						$access_level = '';
						if ( $cur_u['administrator'] )
							$access_level .= lang('administrator').", ";
						if ( $cur_u['tester'] )
							$access_level .= lang('tester').", ";
						if ( $cur_u['leader'] )
							$access_level .= lang('monitor').", ";
						// if ( $cur_u['developer'] )
							// $access_level .= lang('developer').", ";
						// if ( $cur_u['system'] )
							// $access_level .= lang('system').", ";
						# remove , at the end
						if ( endswith($hay=$access_level, $needle=', ') ) {
							$access_level = substr($access_level, 0, -2);
						}

						// extract default info
						$default =  lang('no');
						if ( $cur_u['default'] )
							$default =  lang('yes');
						
						$tb .= '<tr id="box-admin-row" class="list"><td>'.$online.'</td><td>'.$log.'</td><td>'.$default.'</td><td>'.$access_level.'</td><td>'.htmlentities($cur_u['email']).'</td><td>'.$link_edit.'</td><td>'.$link_delete.'</td><td>'.$link_changepwd.'</td><td>'.$link_duplicate.'</td><td>'.$link_active.'</td><td>'.$link_disconnect.'</td></tr>' ;
					}
					$tb .= "</table>";
					
				}

				$tabsbody[] = $tb;

				// statistic
				$tb = '';
				$sql_req = 'SELECT COUNT(*) as connNb FROM  `'.$__LWF_DB_PREFIX.'-users-stats`';
				$rlst_usrs_stats = $db->query($sql_req);
				if ( ! $rlst_usrs_stats)
					$tb = 'Unable to get users stats '.$db->str_error();
				else
				{
					$sql_req = 'SELECT COUNT(*) as userNb FROM  `'.$__LWF_DB_PREFIX.'-users`';
					$rlst_usrs = $db->query($sql_req);
					if ( ! $rlst_usrs)
						$tb = 'Unable to get nb users '.$db->str_error();
					else
					{
						$sql_req = 'SELECT duration FROM  `'.$__LWF_DB_PREFIX.'-users-stats`';
						$rlst_usrs_stats2 = $db->query($sql_req);
						if ( ! $rlst_usrs_stats2)
							$tb = 'Unable to get users stats2'.$db->str_error();
						else
						{
							$cur_users = $db->fetch_assoc($rlst_usrs);
							$cur_users_stats = $db->fetch_assoc($rlst_usrs_stats);

							$min = 0; $max = 0; $avg = 0;
							$durations = array();
							while ($cur_users_stats2 = $db->fetch_assoc($rlst_usrs_stats2))
								array_push($durations, $cur_users_stats2['duration']);
							if (count($durations) > 0 ) {
								$min = round(min($durations), 2);
								$max = round(max($durations) ,2);
								$avg = round( array_sum($durations) / count($durations) ,2);
							}

							$tb .= '<span class="dotted">'.lang('total').'</span>';
							$tb .= '<table><tr><td class="table tablekey">'.lang('admin-users-total').'</td><td>'.$cur_users['userNb'].'</td></tr>';
							$tb .= '<table><tr><td class="table tablekey">'.lang('admin-users-stats-total').'</td><td>'.$cur_users_stats['connNb'].'</td></tr>';
							$tb .= '</table>';

							$tb .= '<br /><span class="dotted">'.lang('duration-conn').'</span>';
							$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$min.'</td></tr>';
							$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$max.'</td></tr>';
							$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$avg.'</td></tr></table>';
						}
					}
				}

				
				array_push($tabsbody, $tb);

				// construct tab body
				echo construct_tabbody($tabsbody);
			}
		}
?>

</div>