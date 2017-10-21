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
	$INDEX_PAGE = get_pindex('system');
	$SUB_PAGE_STATUS =  get_subpindex( 'system', 'system-status' ) ;
	$SUB_PAGE_DESCRIPTION =  get_subpindex( 'system', 'system-description' ) ;
	$SUB_PAGE_USAGE =  get_subpindex( 'system', 'system-usage' ) ;

	// default sub-menu selected
	$s = $SUB_PAGE_STATUS;
	if ( isset($_GET['s']) )
	{
		$s_called = $_GET['s'];
		(!$s_called) ? $s=1 : $s=$s_called;
	}


function readbleTime($seconds) {
	$y = floor($seconds / 60 / 60 / 24 / 365);
	$d = floor($seconds / 60 / 60 / 24) % 365;
	$h = floor(($seconds / 3600) % 24);
	$m = floor(($seconds / 60) % 60);
	$s = $seconds % 60;
	$string = '';
	if ($y > 0) {
	$yw = $y > 1 ? ' years ' : ' year ';
	$string .= $y . $yw;
	}
	if ($d > 0) {
	$dw = $d > 1 ? ' days ' : ' day ';
	$string .= $d . $dw;
	}
	if ($h > 0) {
	$hw = $h > 1 ? ' hours ' : ' hour ';
	$string .= $h . $hw;
	}
	if ($m > 0) {
	$mw = $m > 1 ? ' minutes ' : ' minute ';
	$string .= $m . $mw;
	}
	if ($s > 0) {
	$sw = $s > 1 ? ' seconds ' : ' second ';
	$string .= $s . $sw;
	}
	return preg_replace('/\s+/', ' ', $string);
}

?>
<div class="bxleft">
	<?php 
		( $s == $SUB_PAGE_STATUS ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_STATUS.'\')" >'.lang('system-status').'</div>';
		( $s == $SUB_PAGE_DESCRIPTION ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_DESCRIPTION.'\')" >'.lang('system-description').'</div>';
		( $s == $SUB_PAGE_USAGE ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_USAGE.'\')" >'.lang('system-usage').'</div>';
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
		// status part
		if ( $s == $SUB_PAGE_STATUS )
		{
			// title
			echo '<div class="title-index">'.lang('system-status').'</div>';

			// construct tab menu
			$tabsmenu = array(	
									lang('system-status-server'),
								);
			echo construct_tabmenu($tabsmenu);
		
			// prepare body for each tabs
			$tabsbody = array();

			$tb = '<h3>'.lang('system-general').':</h3><ul>';
			$status =  $XMLRPC->getServerStatus();
			if ( is_null($status) ) {
				$tb .=  '<br /><img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > '.lang('system-server-stopped');
			} else {
				$tb .=  '<li><img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/running_round.png" > '.lang('system-server-running').'</li>';
			}
			$tb .= '</ul>';

			$tb .= '<h3>'.lang('system-datetime').':</h3><ul>';
			$status =  $XMLRPC->getServerStatus();
			if ($status == null) {
				$tb .=  '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > '.lang('system-server-stopped');
			} else {
				foreach ($status as $info) {
					foreach($info as $key => $value) {
						if ( $key == 'server-date') { # used
							$tb .= '<li>'.lang('system-date').': '.$value.'</li>';
						}
						if ( $key == 'start-at') { # used
							$tb .= '<li>'.lang('system-startedsince').': '.$value.'</li>';
						}
					}
				}
			}
			$uptime = shell_exec("cat /proc/uptime");
			$tb .= '<li>'.lang('uptime').': '.readbleTime( $uptime ).'</li>';

			$tb .= "</ul>";
			//}

			$tabsbody[] = $tb;	

			// construct tab body
			echo construct_tabbody($tabsbody);
		}

		// description part
		if ( $s == $SUB_PAGE_DESCRIPTION )
		{
			// title
			echo '<div class="title-index">'.lang('system-description').'</div>';

			// construct tab menu
			$tabsmenu = array(	
									lang('system-description-server'),
								);
			echo construct_tabmenu($tabsmenu);
		
			// prepare body for each tabs
			$tabsbody = array();

			$status =  $XMLRPC->getServerStatus();
			if ( is_null($status) ) {
				$tb =  '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > '.lang('system-server-stopped');
			} else {
				$tb = '<h3>'.lang('system-versions').':</h3><ul>';
				foreach ($status as $info) {
					foreach($info as $key => $value) {
						if ( $key == 'version') { # used
							$tb .= '<li>'.lang('system-version').': '.$value.'</li>';
						}
						if ( $key == 'database') { # used
							$tb .= '<li>'.lang('system-database').': '.$value.'</li>';
						}
						if ( $key == 'server-web') { # used
							$tb .= '<li>'.lang('system-webserver').': '.$value.'</li>';
						}
					}
				}
				$tb .= "</ul>";

				$tb .= '<h3>'.lang('system-packages').':</h3><ul>';
				foreach ($status as $info) {
					foreach($info as $k => $v) {
						if ( $k == 'adapters') { # used
							$tb .= '<li>'.lang('system-adapters').': '.$v.'</li>';
						}
						if ( $k == 'libraries') { # used
							$tb .= '<li>'.lang('system-libraries').': '.$v.'</li>';
						}
						if ( $k == 'default-adapter') { # used
							$tb .= '<li>'.lang('system-current-adapter').': '.$v.'</li>';
						}
						if ( $k == 'default-library') { # used
							$tb .= '<li>'.lang('system-current-library').': '.$v.'</li>';
						}
					}
				}
				$tb .= "</ul>";

				/*$tb .= '<h3>All:</h3><ul>';
				$tb .= shell_exec("rpm -qa");
				$tb .= "</ul>";*/
			}

			$tabsbody[] = $tb;	

			// construct tab body
			echo construct_tabbody($tabsbody);
		}

		// usage part
		if ( $s == $SUB_PAGE_USAGE )
		{

			// title
			echo '<div class="title-index">'.lang('system-usage').'</div>';


			// construct tab menu
			$tabsmenu = array(	
									lang('system-usage-server'),
								);
			echo construct_tabmenu($tabsmenu);
		
			$usage =  $XMLRPC->getServerUsage();
			if ( is_null($usage) ) {
				$tb =  '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > '.lang('system-server-stopped');
			} else {

				$tb = '<h3>'.lang('system-disk-usage').':</h3><ul>';
				foreach($usage as $key => $value) {
					if ( $key == 'disk-usage') { # total/used/free
						$disk_percent = round($value[1] / $value[0] * 100);
						$disk_alert = '';
						if ($disk_percent >= '90')
							$disk_alert = ' <img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/warning.png" >';
						$tb .= '<li>'.lang('system-disk-global').': '.formatBytes($value[0], 1).' / '.formatBytes($value[1], 1).' / '.formatBytes($value[2], 1).$disk_alert.'</li>';
					}
					if ( $key == 'disk-usage-logs') { # used
						$tb .= '<li>'.lang('system-disk-logs').': '.formatBytes($value, 1).'</li>';
					}
					if ( $key == 'disk-usage-tmp') { # used
						$tb .= '<li>'.lang('system-disk-tmp').': '.formatBytes($value, 1).'</li>';
					}
					if ( $key == 'disk-usage-testresults') { # used
						$tb .= '<li>'.lang('system-disk-archives').': '.formatBytes($value, 1).'</li>';
					}
					if ( $key == 'disk-usage-tests') { # used
						$tb .= '<li>'.lang('system-tests').': '.formatBytes($value, 1).'</li>';
					}
					if ( $key == 'disk-usage-backups') { # used
						$tb .= '<li>'.lang('system-backups').': '.formatBytes($value, 1).'</li>';
					}
					if ( $key == 'disk-usage-adapters') { # used
						$tb .= '<li>'.lang('system-adapters').': '.formatBytes($value, 1).'</li>';
					}
					if ( $key == 'disk-usage-libraries') { # used
						$tb .= '<li>'.lang('system-libraries').': '.formatBytes($value, 1).'</li>';
					}
				}
				$tb  .= '</ul>';

				// memory
				$out = shell_exec('free -mo'); // -o no more exist on centos7
                if ($out == null) {  $out = shell_exec('free -m');  }
                
				preg_match_all('/\s+([0-9]+)/', $out, $matches);
				list($total, $used, $free, $shared, $buffers, $cached, $total_swap, $used_swap, $free_swap) = $matches[1];
	
				$mem_free = $free; //+ $buffers + $cached;
				$mem_used = $used; //- $buffers - $cached;
				$mem_total= $total; // - $cached;

                if ( $total) { 
                    $mem_percent = round(($mem_used * 100) / ( $total ) );
                } else {
                    $mem_percent = 0;
                }
				$mem_alert = '';
				if ($mem_percent >= '90')
					$mem_alert = '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/warning.png" >';

				$tb .= '<h3>'.lang('system-mem-usage').':</h3><ul>';
				$tb .= '<li>'.lang('system-mem-free').': '.$mem_free.' MB '.$mem_alert.'</li>';
				$tb .= '<li>'.lang('system-mem-used').': '.$mem_used.' MB</li>';
				$tb .= '<li>'.lang('system-mem-total').': '.$mem_total.' MB'.'</li>';

				$tb .= '</ul>';

				// swap
                if ( $total_swap ) {
                    $swap_percent = round($used_swap / $total_swap * 100);
                } else {
                    $swap_percent = 0;
                }
				$swap_alert = '';
				if ($swap_percent >= '90')
					$swap_alert = '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/warning.png" >';
				$tb .= '<h3>'.lang('system-swap-usage').':</h3><ul>';
				$tb .= '<li>'.lang('system-swap-free').': '.$free_swap.' MB '.$swap_alert.'</li>';
				$tb .= '<li>'.lang('system-swap-used').': '.$used_swap.' MB'.'</li>';
				$tb .= '<li>'.lang('system-swap-total').': '.$total_swap.' MB'.'</li>';

				$tb .= '</ul>';


				// cpu load
				$getLoad = sys_getloadavg();
				$load_alert = '';
				if ($getLoad[0] > 1)
					$load_alert = ' <img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/warning.png" >';
				$tb .= '<h3>'.lang('system-load-usage').':</h3><ul>';
				$tb .= '<li>'.lang('system-load-1').': '.$getLoad[0].$load_alert.'</li>';
				$tb .= '<li>'.lang('system-load-5').': '.$getLoad[1].'</li>';
				$tb .= '<li>'.lang('system-load-15').': '.$getLoad[2].'</li>';

				$tb .= '</ul>';
			}

			$tabsbody[] = $tb;	

			// construct tab body
			echo construct_tabbody($tabsbody);
		}
?>

</div>