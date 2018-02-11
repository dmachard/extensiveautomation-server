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

	function formatBytes($size, $precision = 2)
	{
		$base = log($size) / log(1024);
		$suffixes = array('', 'k', 'M', 'G', 'T');   

		return round(pow(1024, $base - floor($base)), $precision) . $suffixes[floor($base)];
	}

	function handle($in) {
		file_put_contents("/tmp/app.log", $in, FILE_APPEND);
	}

	// Logger::error("Could not encrypt " . $file . ".enc");
	class Logger {
		public function debug($input) {
			handle(date("Y-m-d H:i:s") . ":: DEBUG :: " . $input . "\n");
		}
		public function info($input) {
			handle(date("Y-m-d H:i:s") . " :: INFO :: " . $input . "\n");
		}
		public function warn($input) {
			handle(date("Y-m-d H:i:s") . " :: WARN :: " . $input . "\n");
		}
		public function error($input) {
			handle(date("Y-m-d H:i:s") . " :: ERROR :: " . $input . "\n");
		}
		public function fatal($input) {
			handle(date("Y-m-d H:i:s") . " :: FATAL :: " . $input . "\n");
		}
	}

	function loadcfg(){
		global $db, $__LWF_CFG, $__LWF_DB_PREFIX;
		// read all config from database
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-config`';
		$allcfgfromdb = $db->query($sql_req) or fatal( 'loadcfg', 'Unable to fetch config ('.$sql_req.'): '.$db->error() );
		while ($cur_opt = $db->fetch_assoc($allcfgfromdb))
			$__LWF_CFG[$cur_opt['opt']] =  $cur_opt['value'];
	}

	function lang( $key, $htmlentities=true ) {
			global $LANG_DICT;
			if ( $htmlentities ) {
                // workaround not really nice
                // with php 5.4 utf8 is the default encoding
                // the encoding to iso-8858-1 is just a workaround
				$str_converted = htmlentities( $LANG_DICT[$key], ENT_NOQUOTES, $encoding='ISO-8859-1' );
			} else {
				$str_converted = $LANG_DICT[$key];
			}
			return $str_converted;
	}

	function parse_pindex($strp) {
		$default_p = "0100";
		if ( sizeof($strp) != 4) {
			return $default_p ;
		} else {
			return "1";
		}
	}

	function get_pindex2($p, $s) {
		if ( sizeof($p) == 1 )
			$p = "0".$p;
		if ( sizeof($s) == 1 )
			$s = "0".$s;
		$index = $p.$s;
		return $index;
	}

	function get_pindex( $pname) {
			global $__DEF_PAGES;

			$ret = array_search( lang($pname), $__DEF_PAGES ) + 1;
			return $ret;
	}

	function get_subpindex( $pname, $subpname) {
			global $__DEF_SUB_PAGES;

			$ret = array_search( lang($subpname), $__DEF_SUB_PAGES[get_pindex($pname) -1] ) + 1;
			return $ret;
	}

	//
	// Returns all installed language
	//
	function get_installed_lang(){
		$langs = array();
		if ($handle = opendir(ROOT.'/lang/')) {
			while (false !== ($file = readdir($handle))) {
				if ($file != "." && $file != "..") {
					if ( endswith($file, ".php") ) {
						$lang = preg_split( "/.php/", $file);
						array_push($langs, $lang[0] );
					}
				}
			}
			closedir($handle);
		}
		return $langs;
	}

	//
	// Returns all installed css style
	//
	function get_installed_style(){
		$styles = array();
		if ($handle = opendir(ROOT.'/style/')) {
			while (false !== ($file = readdir($handle))) {
				if ($file != "." && $file != "..") {
					array_push($styles, $file );
				}
			}
			closedir($handle);
		}
		return $styles;
	}

	//
	// Check email format 
	//
	function check_email_format($email)
	{
			if (strlen($email) > 50)
					return false;

			return preg_match('/^(([^<>()[\]\\.,;:\s@"\']+(\.[^<>()[\]\\.,;:\s@"\']+)*)|("[^"\']+"))@((\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\])|(([a-zA-Z\d\-]+\.)+[a-zA-Z]{2,}))$/', $email);
	}

	//
	// Pythonesque function: endswith  
	//
	function startswith($hay, $needle)
	{
			return substr($hay, 0, strlen($needle)) === $needle;
	}

	//
	// Pythonesque function: endswith  
	//
	function endswith($hay, $needle)
	{
			return substr($hay, -strlen($needle)) === $needle;
	}

	function strbool2int($value)
	{
		return $value == 'true' ? 1 : 0;
	}

	//
	// Read cookie
	//
	function read_cookie(&$cook)
	{
			global $__LWF_COOKIE_NAME;

			// If a cookie is set, we get the conf_id
			if (isset($_COOKIE[$__LWF_COOKIE_NAME]))
			{
					$cook =  @unserialize($_COOKIE[$__LWF_COOKIE_NAME]);
			}

	}

	//
	// Create cookie
	//
	function set_cookie($data)
	{
			global $__LWF_COOKIE_NAME, $__LWF_COOKIE_PATH, $__LWF_COOKIE_DOMAIN, $__LWF_COOKIE_SECURE;
			//
			$now = time();
			$expire = $now + 43200; // 12 hours
			//
			setcookie($__LWF_COOKIE_NAME, serialize($data), $expire, $__LWF_COOKIE_PATH, $__LWF_COOKIE_DOMAIN, $__LWF_COOKIE_SECURE);
	}

	//
	// Delete cookie
	//
	function del_cookie($data)
	{
			global $__LWF_COOKIE_NAME, $__LWF_COOKIE_PATH, $__LWF_COOKIE_DOMAIN, $__LWF_COOKIE_SECURE;
			//
			$now = time();
			$expire = $now - 86400 ;
			// cookie expired
			setcookie($__LWF_COOKIE_NAME, serialize($data), $expire, $__LWF_COOKIE_PATH, $__LWF_COOKIE_DOMAIN, $__LWF_COOKIE_SECURE );
	}

	//
	// Display a debug message
	//
	function debug($message)
	{
		echo $message.'<br />';
	}

	//
	// Display a fatal message
	//
	function fatal($from, $message)
	{
		global $__LWF_APP_NAME;
		// Empty output buffer and stop buffering
		@ob_end_clean();
	?>
		<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
		<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr">
		<head>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<title><?php echo  $__LWF_APP_NAME ?> / Fatal Error</title>
		<style type="text/css">
		<!--
		BODY {MARGIN: 10% 20% auto 20%; font: 10px Verdana, Arial, Helvetica, sans-serif}
		#errorbox {BORDER: 1px solid #B84623}
		H2 {MARGIN: 0; COLOR: #FFFFFF; BACKGROUND-COLOR: #B84623; FONT-SIZE: 1.1em; PADDING: 5px 4px}
		#errorbox DIV {PADDING: 6px 5px; BACKGROUND-COLOR: #F1F1F1}
		-->
		</style>
		</head>
		<body>
		<div id="errorbox">
				<h2>An error was encountered, raised by <?php echo $from ?></h2>
				<div><?php echo "\t\t".'<strong>'.$message.'.</strong>'."\n"; ?> </div>
			</div>
		</body>
		</html>
	<?php
		exit;
	}

	//
	// Construct tab menu
	//
	function construct_tabmenu($menus, $menuid_selected=0 )
	{
		$htmlmenutab = '<ul class="subtabmenu">';
		foreach ($menus as $i => $tab) {
				if ($tab == $menus[$menuid_selected])
					$menu_selected = "subtabmenu_selected";
				else
					$menu_selected = "";
				$htmlmenutab .= '<li><span class="'.$menu_selected.'" onclick="javascript:showsubtabmenu(\''.$i.'\', '.sizeof($menus).' )" id="stm'.$i.'">'.$tab.'</span></li>';
		}
		$htmlmenutab .= '</ul>';
		return $htmlmenutab;
	}

	//
	// Construct tab body
	//
	function construct_tabbody($bodys, $bodyid_selected=0 )
	{
		$htmlbodytab = '';
		foreach ($bodys as $i => $body) {
				if ($i == $bodyid_selected)
					$hide_body = "";
				else
					$hide_body = "hide_div";
			$htmlbodytab .= '<div class="subtabmenu_body '.$hide_body.'" id="stmb'.$i.'">';
			$htmlbodytab .= $body;
			$htmlbodytab .= '</div>';	
		}
		return $htmlbodytab;
	}

	//
	// nl2br 
	//
	function nl2br_changed($txt)
	{
		$ret = str_replace("\\r\\n", "<br />", $txt);
		$ret = str_replace("\\n", "<br />",$ret);
		return $ret;
	}	

	function get_ajaxloader($idname, $type)
	{
		global $__LWF_APP_DFLT_STYLE;
		$ret = "";
		if ( $type == "0")
		{
			$ret = ' <img  id="'.$idname.'" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" alt="ajax-loader" class="icon-loader">';
		}
		if ( $type == "1")
		{
			$ret = '<img  id="'.$idname.'" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-overview-gray.gif" class="icon-loader" alt="ajax-loader">';
		}
		return $ret;
	}

 
	function objectToArray($d) {
		if (is_object($d)) {
			// Gets the properties of the given object
			// with get_object_vars function
			$d = get_object_vars($d);
		}
 
		if (is_array($d)) {
			/*
			* Return array converted to object
			* Using __FUNCTION__ (Magic constant)
			* for recursive call
			*/
			return array_map(__FUNCTION__, $d);
		}
		else {
			// Return array
			return $d;
		}
	}

	function arrayToObject($d) {
		if (is_array($d)) {
			/*
			* Return array converted to object
			* Using __FUNCTION__ (Magic constant)
			* for recursive call
			*/
			return (object) array_map(__FUNCTION__, $d);
		}
		else {
			// Return object
			return $d;
		}
	}

	/*
	* Function which explodes string with delimiter, but if delimiter is "escaped" by backslash, function won't split in that point
	*/
	function explode_escaped($delimiter, $string){
        $exploded = explode($delimiter, $string);
        $fixed = array();
        for($k = 0, $l = count($exploded); $k < $l; ++$k){
            if($exploded[$k][strlen($exploded[$k]) - 1] == '\\') {
                if($k + 1 >= $l) {
                    $fixed[] = trim($exploded[$k]);
                    break;
                }
                $exploded[$k][strlen($exploded[$k]) - 1] = $delimiter;
                $exploded[$k] .= $exploded[$k + 1];
                array_splice($exploded, $k + 1, 1);
                --$l;
                --$k;
            } else $fixed[] = trim($exploded[$k]);
        }
        return $fixed;
    }

?>
