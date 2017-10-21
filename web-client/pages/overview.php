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
	
	// prepare index page
	$OVERVIEW_PAGE = get_pindex('overview');
	$SUB_PAGE_INDEX =  get_subpindex( 'overview', 'overview-index' ) ;
	$SUB_PAGE_DL =  get_subpindex( 'overview', 'overview-download' ) ;
	$SUB_PAGE_DOCS =  get_subpindex( 'overview', 'overview-docs' ) ;
	$SUB_PAGE_AGENTS =  get_subpindex( 'overview', 'overview-agents' ) ;
	$SUB_PAGE_PROBES =  get_subpindex( 'overview', 'overview-probes' ) ;

	$ABOUT_PAGE = get_pindex('about');
	$SUB_PAGE_DESCR = get_subpindex( 'about', 'about-description' ) ;
	$SUB_PAGE_RN = get_subpindex( 'about', 'about-release-notes' ) ;

	$TESTS_PAGE = get_pindex('tests');
	$SUB_PAGE_TESTS_STATS = get_subpindex('tests', 'tests-statistics');

	$ADMIN_PAGE = get_pindex('administration');
	$SUB_PAGE_PROJECTS = get_subpindex('administration', 'admin-projects');
	$SUB_PAGE_USERS = get_subpindex('administration', 'admin-users');
	
	$SYSTEM_PAGE = get_pindex('system');
	$SUB_PAGE_SYSTEM = get_subpindex('system', 'system-usage');

	// default sub-menu selected
	$s = $SUB_PAGE_INDEX;
	if ( isset($_GET['s']) )
	{
		$s_called = $_GET['s'];
		(!$s_called) ? $s=1 : $s=$s_called;
	}

	// default tab selected
	$t = 0;
	if ( isset($_GET['t']) )
	{
		$t_called = $_GET['t'];
		(!$t_called) ? $t=0 : $t=$t_called;
	}
	if ( $t < 0) {
		$t=0;
	}


?>
<div class="bxleft">	
	<?php 
		( $s == $SUB_PAGE_INDEX ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_INDEX.'\')" >'.lang('overview-index').'</div>';
		( $s == $SUB_PAGE_DL ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_DL.'\')" >'.lang('overview-center').'</div>';
		( $s == $SUB_PAGE_DOCS ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_DOCS.'\')" >'.lang('overview-docs').'</div>';
		( $s == $SUB_PAGE_AGENTS ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_AGENTS.'\')" >'.lang('overview-agents').'</div>';
		( $s == $SUB_PAGE_PROBES ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_PROBES.'\')" >'.lang('overview-probes').'</div>';
	?>
</div>

<!--<div class="bxright">
	<div class="help"><?php echo lang('help') ?><?php echo get_ajaxloader("loader-help", "0") ?></div>
	<div>
		<ul class="help_list">
			<li><?php echo '<a href="javascript:nav(\'./index.php?p='.$ABOUT_PAGE.'&s='.$SUB_PAGE_DESCR.'&c=new\')">'.lang('about-what').'</a>'; ?></li>
			<li><?php echo '<a href="javascript:nav(\'./index.php?p='.$ABOUT_PAGE.'&s='.$SUB_PAGE_RN.'&c=new\')">'.lang('about-what-new').'</a>'; ?></li>
		</ul>
	</div>
</div>-->

<div class="bxcenter">
	
	<div id="box-warn"></div>
<?php
		// index part
		if ( $s == $SUB_PAGE_INDEX )
		{

			// title
			echo '<div class="overview-title-index">'.lang('overview-welcome').'</div>';
			
			// body
			$tabsbody = array();
			$tb = '<div><h2>'.lang('OVERVIEW_020').$__LWF_APP_NAME.' '.$__LWF_CFG['server-version'].'</h2>';
			$tb .= '<ul>';
			$tb .= '<li><h3>'.lang('OVERVIEW_021').'</h3></li>';
			$tb .= '<ul><li><a href="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_DL.'\')">'.lang('OVERVIEW_022').'</a>';
			$tb .= '<p class="description"><i>'.lang('OVERVIEW_023').'</i></p>';
			$tb .= '</li></ul>';
            $tb .= '<ul><li><a href="javascript:nav(\'./index.php?p='.$OVERVIEW_PAGE.'&s='.$SUB_PAGE_DL.'&t=1\')">'.lang('overview-download-tool').'</a>';
			$tb .= '<p class="description"><i>'.lang('OVERVIEW_025').'</i></p>';
            $tb .= '<p class="description"><i>'.lang('OVERVIEW_027').'</i></p>';
			$tb .= '</li></ul>';

			if ( $CORE->profile['leader'] or $CORE->profile['administrator'] ) {
				$tb .= '<li><h3>'.lang('OVERVIEW_028').'</h3></li>';
				$tb .= '<ul><li><a href="javascript:nav(\'./index.php?p='.$TESTS_PAGE.'&s='.$SUB_PAGE_TESTS_STATS.'\')">'.lang('OVERVIEW_029').'</a>';
				$tb .= '<p class="description"><i>'.lang('OVERVIEW_030').'</i></p>';
				$tb .= '</li></ul>';
			}

			if ( $CORE->profile['administrator'] ) {
				$tb .= '<li><h3>'.lang('OVERVIEW_031').'</h3></li>';
				$tb .= '<ul><li><a href="javascript:nav(\'./index.php?p='.$ADMIN_PAGE.'&s='.$SUB_PAGE_PROJECTS.'\')">'.lang('OVERVIEW_032').'</a>';
				$tb .= '<p class="description"><i>'.lang('OVERVIEW_033').'</i></p>';
				$tb .= '</li></ul>';

				$tb .= '<ul><li><a href="javascript:nav(\'./index.php?p='.$ADMIN_PAGE.'&s='.$SUB_PAGE_USERS.'\')">'.lang('OVERVIEW_034').'</a>';
				$tb .= '<p class="description"><i>'.lang('OVERVIEW_035').'</i></p>';
				$tb .= '</li></ul>';

				$tb .= '<ul><li><a href="javascript:nav(\'./index.php?p='.$SYSTEM_PAGE.'&s='.$SUB_PAGE_SYSTEM.'\')">'.lang('OVERVIEW_036').'</a>';
				$tb .= '<p class="description"><i>'.lang('OVERVIEW_037').'</i></p>';
				$tb .= '</li></ul>';
			}

			$tb .= '</ul>';
			$tb .= '</div>';
			$tabsbody[] = $tb;
			echo construct_tabbody($tabsbody);
		}

		// download part
		if ( $s == $SUB_PAGE_DL )
		{
			// title
			echo '<div class="overview-title-index">'.lang('overview-download').'</div>';

			// construct tab menu
			$tabsmenu = array( lang('overview-clients'), lang('overview-toolbox') );
			if( $t >= count($tabsmenu)  ) {
				$t=0;
			}
			echo construct_tabmenu($tabsmenu, $menuid_selected=$t);

			// body
			$tabsbody = array();

			$__CLIENT_CLI_RC__ ="xtcpyrc.tar.gz";
            
			$__CLIENT_PLUGIN_DUMMY__ ="Dummy";
			$__CLIENT_PLUGIN_HPQC__ ="HP ALM QC";
			$__CLIENT_PLUGIN_SELENIUMIDE__ ="SeleniumIDE";
			$__CLIENT_PLUGIN_JENKINS__ ="Jenkins";
            $__CLIENT_PLUGIN_SSHRECORDER__ ="Shell-Recorder";

			$__TOOLBOX_PLUGIN_DUMMY__ ="Dummy";
            
            $arch = "win64";
            
			$tb = '<br />'.lang('overview-ide');
			$tb .= '<ul>';
            if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-package']."/".$arch."/".$__LWF_CFG['misc-client-win']) )
                $tb .= '<li>'.lang('overview-platform-win').': <a href="get.php?dl=clt&arch='.$arch.'&file='.$__LWF_CFG['misc-client-win'].'">'.lang('overview-download-action').'</a></li><br />';
            if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-package']."/".$arch."/".$__LWF_CFG['misc-client-win-portable']) )
                $tb .= '<li>'.lang('overview-platform-win-portable').': <a href="get.php?dl=clt&arch='.$arch.'&file='.$__LWF_CFG['misc-client-win-portable'].'">'.lang('overview-download-action').'</a></li><br />';
			if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-package']."/linux2/".$__LWF_CFG['misc-client-linux']) )
                $tb .= '<li>'.lang('overview-platform-linux').': <a href="get.php?dl=clt&arch=linux2&file='.$__LWF_CFG['misc-client-linux'].'">'.lang('overview-download-action').'</a></li>';
			$tb .= '</ul>';
            
			$tb .= '<br />'.lang('overview-client-plugins');
			$tb .= '<ul>';
            if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-plgs-package']."/".$arch."/ExtensiveTestingClient_".$__CLIENT_PLUGIN_DUMMY__.".zip") )
                $tb .= '<li>'.$__CLIENT_PLUGIN_DUMMY__.': '.lang('overview-clt-plugin-dummy').' <a href="get.php?dl=clt-plgs&arch='.$arch.'&file=ExtensiveTestingClient_'.$__CLIENT_PLUGIN_DUMMY__.'.zip">'.lang('overview-download-action').'</a></li>';
			if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-plgs-package']."/".$arch."/ExtensiveTestingClient_".$__CLIENT_PLUGIN_HPQC__.".zip") )
                $tb .= '<li>'.$__CLIENT_PLUGIN_HPQC__.': '.lang('overview-clt-plugin-hpqc').' <a href="get.php?dl=clt-plgs&arch='.$arch.'&file=ExtensiveTestingClient_'.$__CLIENT_PLUGIN_HPQC__.'.zip">'.lang('overview-download-action').'</a></li>';
			if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-plgs-package']."/".$arch."/ExtensiveTestingClient_".$__CLIENT_PLUGIN_SELENIUMIDE__.".zip") )
                $tb .= '<li>'.$__CLIENT_PLUGIN_SELENIUMIDE__.': '.lang('overview-clt-plugin-seleniumide').' <a href="get.php?dl=clt-plgs&arch='.$arch.'&file=ExtensiveTestingClient_'.$__CLIENT_PLUGIN_SELENIUMIDE__.'.zip">'.lang('overview-download-action').'</a></li>';
            if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-plgs-package']."/".$arch."/ExtensiveTestingClient_".$__CLIENT_PLUGIN_JENKINS__.".zip") )
                $tb .= '<li>'.$__CLIENT_PLUGIN_JENKINS__.': '.lang('overview-clt-plugin-jenkins').' <a href="get.php?dl=clt-plgs&arch='.$arch.'&file=ExtensiveTestingClient_'.$__CLIENT_PLUGIN_JENKINS__.'.zip">'.lang('overview-download-action').'</a></li>';
            if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-plgs-package']."/".$arch."/ExtensiveTestingClient_".$__CLIENT_PLUGIN_SSHRECORDER__.".zip") )
                $tb .= '<li>'.$__CLIENT_PLUGIN_SSHRECORDER__.': '.lang('overview-clt-plugin-sshrecorder').' <a href="get.php?dl=clt-plgs&arch='.$arch.'&file=ExtensiveTestingClient_'.$__CLIENT_PLUGIN_SSHRECORDER__.'.zip">'.lang('overview-download-action').'</a></li>';
            $tb .= '</ul>';

			array_push($tabsbody, $tb);

			$tb = '<br />'.lang('overview-toolbox-description');
			$tb .= '<ul>';
			if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-tlb-package']."/".$arch."/".$__LWF_CFG['misc-toolbox-win']) )
                $tb .= '<li>'.lang('overview-platform-win').': <a href="get.php?dl=tlb&arch='.$arch.'&file='.$__LWF_CFG['misc-toolbox-win'].'">'.lang('overview-download-action').'</a></li><br />';
            if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-tlb-package']."/".$arch."/".$__LWF_CFG['misc-toolbox-win-portable']) )
                $tb .= '<li>'.lang('overview-platform-win-portable').': <a href="get.php?dl=tlb&arch='.$arch.'&file='.$__LWF_CFG['misc-toolbox-win-portable'].'">'.lang('overview-download-action').'</a></li><br />';
			if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-tlb-package']."/".$arch."/".$__LWF_CFG['misc-toolbox-linux']) )
                $tb .= '<li>'.lang('overview-platform-linux').': <a href="get.php?dl=tlb&arch=linux2&file='.$__LWF_CFG['misc-toolbox-linux'].'">'.lang('overview-download-action').'</a></li>';
			$tb .= '</ul>';	
            
			$tb .= '<br />'.lang('overview-toolbox-plugins');
			$tb .= '<ul>';
			if ( file_exists($__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-tlb-plgs-package']."/".$arch."/ExtensiveTestingToolbox_".$__TOOLBOX_PLUGIN_DUMMY__.".zip") )
                $tb .= '<li>'.$__TOOLBOX_PLUGIN_DUMMY__.': '.lang('overview-tlb-plugin-dummy').' <a href="get.php?dl=tlb-plgs&arch='.$arch.'&file=ExtensiveTestingToolbox_'.$__TOOLBOX_PLUGIN_DUMMY__.'.zip">'.lang('overview-download-action').'</a></li>';
            $tb .= '</ul>';
            
			array_push($tabsbody, $tb);
            
			echo construct_tabbody($tabsbody, $bodyid_selected=$t);
		}

		// documentations part
		if ( $s == $SUB_PAGE_DOCS )
		{
			// title
			echo '<div class="overview-title-index">'.lang('overview-docs').'</div>';

			// construct tab menu
			$tabsmenu = array(	 lang('quickstart') );
			echo construct_tabmenu($tabsmenu);

			// body
			$tabsbody = array();
            
            $tb .= '<br /><b>'.lang('online').'</b><br />';
            $tb .= '<ul>';
            $tb .= '<li class="docslist"><a href="http://documentations.extensivetesting.org/docs" target="_blank">ExtensiveTesting.ORG</a></li>';
            $tb .= '</ul>';
            
            $tb .= '<br /><b>'.lang('api').'</b><br />';
            $tb .= '<ul>';
            $tb .= '<li class="docslist"><a href="./api-rest/index.html" target="_blank">'.lang('overview-ws-rest').'</a></li>';
            $tb .= '<ul>';
            $tb .= '<li class="docslist"><a href="./api-rest/extensivetesting.json" target="_blank">swagger.json</a></li>';
            $tb .= '<li class="docslist"><a href="./api-rest/extensivetesting.yaml" target="_blank">swagger.yaml</a></li>';
            $tb .= '</ul>';
            $tb .= '</ul>';
            
            $tb .= '<ul>';
            $tb .= '<li class="docslist"><a href="./api-rest/previous/index.html" target="_blank">'.lang('overview-ws-rest-old').'</a></li>';
            $tb .= '<li class="docslist"><a href="./api/index.html" target="_blank">'.lang('overview-ws').'</a></li>';
            $tb .= '</ul>';
            
			array_push($tabsbody, $tb);

			echo construct_tabbody($tabsbody);
		}

		// agents part
		if ( $s == $SUB_PAGE_AGENTS )
		{
			// title
			echo '<div class="overview-title-index">'.lang('overview-agents').'</div>';

			// construct tab menu
			$tabsmenu = array(	 lang('overview-running') );
			echo construct_tabmenu($tabsmenu);

			// prepare body for each tabs
			$tabsbody = array();
			
			$agentsRunning =  $XMLRPC->getRunningAgents();
			
			$tb = '';

			if ( is_null($agentsRunning) ) {
				$tb .=  '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > Server is stopped';
			} else {
				$tb .= '<table id="agentlist"><tr><td><b>'.lang('name').'</b></td><td><b>'.lang('address').'</b></td><td><b>'.lang('type').'</b></td><td><b>'.lang('description').'</b></td><td></td></tr>';
					
				foreach ($agentsRunning as $agent) {
					$tb .= '<tr id="box-admin-row" class="list"><td>'.$agent->id.'</td>';
					$tb .= '<td>'.$agent->publicip.'</td><td>'.$agent->type.'</td><td>'.$agent->description.'</td>';
					$tb .= '<td><a href="javascript:disconnectagent(\''.$agent->id.'\')">'.lang('overview-agents-disconnect').'</a></td></tr>' ;
				}
				$tb .= '</table>';
			}
			

			$tabsbody[] = $tb;	
			// construct tab body
			echo construct_tabbody($tabsbody);
		}

		// probes part
		if ( $s == $SUB_PAGE_PROBES )
		{
			// title
			echo '<div class="overview-title-index">'.lang('overview-probes').'</div>';

			// construct tab menu
			$tabsmenu = array(	 lang('overview-running') );
			echo construct_tabmenu($tabsmenu);

			// prepare body for each tabs
			$tabsbody = array();
			
			$probesRunning =  $XMLRPC->getRunningProbes();
			
			$tb = '';

			if ( is_null($probesRunning) ) {
				$tb =  '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > Server is stopped';
			} else {
				$tb = '<table id="probelist"><tr><td><b>'.lang('name').'</b></td><td><b>'.lang('address').'</b></td><td><b>'.lang('type').'</b></td><td><b>'.lang('description').'</b></td><td></td></tr>';
					
				foreach ($probesRunning as $probe) {
					$tb .= '<tr id="box-admin-row" class="list"><td>'.$probe->id.'</td>';
					$tb .= '<td>'.$probe->publicip.'</td><td>'.$probe->type.'</td><td>'.$probe->description.'</td>';
					$tb .= '<td><a href="javascript:disconnectprobe(\''.$probe->id.'\')">'.lang('overview-probes-disconnect').'</a></td></tr>' ;
				}
				$tb .= '</table>';
			}
			
			$tabsbody[] = $tb;	
			// construct tab body
			echo construct_tabbody($tabsbody);
		}
?>
</div>



