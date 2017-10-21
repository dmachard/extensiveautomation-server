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

	// load framework core
    define('ROOT', './');
	require ROOT.'include/common.php';

	$p = get_pindex('overview');
	if ( isset($_GET['p']) )
	{
		$p_called = $_GET['p'];
		(!$p_called) ? $p=1 : $p=$p_called;
	}

	if ( $p == "logout")
		$CORE->logout();


	// prepare html page
	$tpl_main = file_get_contents(ROOT.'index.tpl');
        
	$tpl_main = str_replace('<!-- lwf_local -->', 'xml:lang="'.$__LWF_APP_DFLT_LANG.'" lang="'.$__LWF_APP_DFLT_LANG.'" dir="'.$__LWF_APP_LANG_DIR.'"', $tpl_main);

	$tmp_str = '<link rel="icon"  type="image/png" href="./images/main.png" />';

	if ( ! $__LWF_ALLOW_ROBOTS )
                $tmp_str .= '<meta name="ROBOTS" content="NOINDEX, FOLLOW" />'."\n";
        else
                $tmp_str .=  '<meta name="keywords" content="'.$__LWF_KEYWORDS.'" />'."\n";
	
	// import javascript library
	$tmp_str .= '<script src="./js/lib.js" type="text/javascript"></script>'."\n";
	if ( $p == get_pindex('overview') && $CORE->profile != null)
		$tmp_str .= '<script src="./js/overview.js" type="text/javascript"></script>'."\n";
	if ( $p == get_pindex('tests'))
		$tmp_str .= '<script src="./js/tests.js" type="text/javascript"></script>'."\n";
	if ( $p == get_pindex('administration'))
		$tmp_str .= '<script src="./js/administration.js" type="text/javascript"></script>'."\n";
	if ( $p == get_pindex('system'))
		$tmp_str .= '<script src="./js/system.js" type="text/javascript"></script>'."\n";

	// import style css
	$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/common.css" />'."\n";
	if ( $CORE->profile == null)
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/login.css" />'."\n";
	if ( $p == get_pindex('overview') && $CORE->profile != null && $CORE->profile != null )
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/overview.css" />'."\n";
	if ( $p == get_pindex('tests') && $CORE->profile != null && $CORE->profile != null ) {
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/tests.css" />'."\n";
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/treeview.css" />'."\n";
	}
	if ( $p == get_pindex('administration') && $CORE->profile != null )
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/administration.css" />'."\n";
	if ( $p == get_pindex('system') && $CORE->profile != null )
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/system.css" />'."\n";
	if ( $p == get_pindex('about') && $CORE->profile != null )
		$tmp_str .= '<link rel="stylesheet" type="text/css" media="screen" href="./style/'.$__LWF_APP_DFLT_STYLE.'/about.css" />'."\n";

	// preloading images, not really nice...
	$tmp_str .= '<div id="preloaded-images">';
	$tmp_str .= '<img src="./style/default/img/tgx.png" width="1" height="1"/>';
	$tmp_str .= '<img src="./style/default/img/tux.png" width="1" height="1"/>';
	$tmp_str .= '<img src="./style/default/img/tsx.png" width="1" height="1"/>';
	$tmp_str .= '<img src="./style/default/img/tpx.png" width="1" height="1"/>';
	$tmp_str .= '<img src="./style/default/img/tdx.png" width="1" height="1"/>';
	$tmp_str .= '<img src="./style/default/img/tcx.png" width="1" height="1"/>';
	$tmp_str .= '<img src="./style/default/img/png.png" width="1" height="1"/>';
	$tmp_str .= '</div>';


	$tpl_main = str_replace('<!-- lwf_main_header -->', $tmp_str, $tpl_main);

	// load app body
	if ( $CORE->profile != null || $__LWF_COOKIE_ENABLE == 0)
	{
		// load app header
		require ROOT.'header.php';

		$default_p = ROOT."pages/overview.php";
		switch ($p) {
			case  get_pindex('overview'):
				include ROOT."pages/overview.php";
				break;
			case get_pindex('tests'):
				include ROOT."pages/tests.php";
				break;
			case get_pindex('administration'):
				include ROOT."pages/administration.php";
				break;
			case get_pindex('system'):
				include ROOT."pages/system.php";
				break;
			case get_pindex('about'):
				include ROOT."pages/about.php";
				break;
			default:
				include $default_p;
		}
		
		// load app footer
		require ROOT.'footer.php';
	}
	else
	{
		include ROOT."pages/login.php";
	}


?>
