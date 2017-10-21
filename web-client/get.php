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

	define('ROOT', './');
	require ROOT.'include/common.php';

	if (!defined('CONFIG_OK'))
		exit( lang('access denied') );
	
	if ( $CORE->profile == null )
		exit( lang('access denied') );

	define('DOWNLOAD_CLT', 'clt');
    define('DOWNLOAD_TLB', 'tlb');
	define('DOWNLOAD_DOC', 'doc');
	define('DOWNLOAD_MISC', 'misc');
	define('DOWNLOAD_CLT_PLUGINS', 'clt-plgs');
	define('DOWNLOAD_TLB_PLUGINS', 'tlb-plgs');
    
	// detect the download type
	if ( ! isset($_GET['dl']) )
		deny();
	$dl_type = $_GET['dl'];

	// dispatch download
	switch ($dl_type) {
		case DOWNLOAD_CLT:
			download_client($portable=false);
			break;
		case DOWNLOAD_TLB:
			download_tool($portable=false);
			break;
		case DOWNLOAD_CLT_PLUGINS:
			download_client_plugins();
			break;
		case DOWNLOAD_TLB_PLUGINS:
			download_toolbox_plugins();
			break;
		case DOWNLOAD_DOC:
			download_doc();
			break;
		case DOWNLOAD_MISC:
			download_misc();
			break;
		default:
			deny();
	}

	function download_doc(){
		global  $__LWF_CFG;

		//download.php?dl=doc&type=quickstart&lang=fr&file=xxxx.txt
		if ( ! isset($_GET['file']) )
			deny();

		if ( ! isset($_GET['type']) )
			deny();

		if ( ! isset($_GET['lang']) )
			deny();

		$file = pathinfo($_GET['file']);
		$doctype = $_GET['type'];
		$lang = $_GET['lang'];

		if( $doctype=="quickstart" ) {
			if ( $lang=="en" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/quickstart/en/".$file['basename'];
			elseif ( $lang=="fr" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/quickstart/fr/".$file['basename'];
			else
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/quickstart/en/".$file['basename'];
		}
		elseif( $doctype=="installation" ) {
			if ( $lang=="en" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/installation/en/".$file['basename'];
			elseif ( $lang=="fr" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/installation/fr/".$file['basename'];
			else
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/installation/en/".$file['basename'];
		}
		elseif( $doctype=="configuration" ) {
			if ( $lang=="en" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/configuration/en/".$file['basename'];
			elseif ( $lang=="fr" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/configuration/fr/".$file['basename'];
			else
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/configuration/en/".$file['basename'];
		}
		elseif( $doctype=="overview" ) {
			if ( $lang=="en" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/overview/en/".$file['basename'];
			elseif ( $lang=="fr" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/overview/fr/".$file['basename'];
			else
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/overview/en/".$file['basename'];
		}
		elseif( $doctype=="howto" ) {
			if ( $lang=="en" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/howto/en/".$file['basename'];
			elseif ( $lang=="fr" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/howto/fr/".$file['basename'];
			else
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/howto/en/".$file['basename'];
		}
		elseif( $doctype=="troubleshooting" ) {
			if ( $lang=="en" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/troubleshooting/en/".$file['basename'];
			elseif ( $lang=="fr" )
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/troubleshooting/fr/".$file['basename'];
			else
				$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/troubleshooting/en/".$file['basename'];
		}
		else {
			$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-docs']."/".$file['basename'];
		}

		if ( !file_exists($full_path) )
			deny();
	
		// download the file
		download($full_path=$full_path, $filename=$file['basename']);
	}

	function download_client(){
		global  $__LWF_CFG;

		//download.php?dl=clt&arch=linux2=file=TAC_3.2.0_Setup.exe
		if ( ! isset($_GET['arch']) )
			deny();
		if ( ! isset($_GET['file']) )
			deny();

		// securize the path
		$arch = pathinfo($_GET['arch']);
		$file = pathinfo($_GET['file']);

		$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-package']."/".$arch['basename']."/".$file['basename'];
		if ( !file_exists($full_path) )
			deny();

		// download the file
		download($full_path=$full_path, $filename=$file['basename']);
	}
    
	function download_tool(){
		global  $__LWF_CFG;

		//download.php?dl=tlb&arch=linux2=file=TAC_3.2.0_Setup.exe
		if ( ! isset($_GET['arch']) )
			deny();
		if ( ! isset($_GET['file']) )
			deny();

		// securize the path
		$arch = pathinfo($_GET['arch']);
		$file = pathinfo($_GET['file']);

		$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-tlb-package']."/".$arch['basename']."/".$file['basename'];
		if ( !file_exists($full_path) )
			deny();

		// download the file
		download($full_path=$full_path, $filename=$file['basename']);
	}
	
    function download_client_plugins(){
		global  $__LWF_CFG;

		//download.php?dl=clt-plgs&arch=linux2=file=XXX_3.2.0_Setup.exe
		if ( ! isset($_GET['arch']) )
			deny();
		if ( ! isset($_GET['file']) )
			deny();

		// securize the path
		$arch = pathinfo($_GET['arch']);
		$file = pathinfo($_GET['file']);

		$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-clt-plgs-package']."/".$arch['basename']."/".$file['basename'];
		if ( !file_exists($full_path) )
			deny();

		// download the file
		download($full_path=$full_path, $filename=$file['basename']);
	}
	
    function download_toolbox_plugins(){
		global  $__LWF_CFG;

		//download.php?dl=tlb-plgs&arch=linux2=file=XXX_3.2.0_Setup.exe
		if ( ! isset($_GET['arch']) )
			deny();
		if ( ! isset($_GET['file']) )
			deny();

		// securize the path
		$arch = pathinfo($_GET['arch']);
		$file = pathinfo($_GET['file']);

		$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-tlb-plgs-package']."/".$arch['basename']."/".$file['basename'];
		if ( !file_exists($full_path) )
			deny();

		// download the file
		download($full_path=$full_path, $filename=$file['basename']);
	}
    
	function download_misc(){
		global  $__LWF_CFG;

		//download.php?dl=tac&arch=linux2=file=TAC_3.2.0_Setup.exe
		if ( ! isset($_GET['arch']) )
			deny();
		if ( ! isset($_GET['file']) )
			deny();

		// securize the path
		$arch = pathinfo($_GET['arch']);
		$file = pathinfo($_GET['file']);

		$full_path =  $__LWF_CFG['paths-main']."/".$__LWF_CFG['paths-misc-package']."/".$file['basename'];
		if ( !file_exists($full_path) )
			deny();

		// download the file
		download($full_path=$full_path, $filename=$file['basename']);
	}

	function download($full_path, $filename){
		if ($fd = fopen ($full_path, "rb")) {

			$fsize = filesize($full_path);
			header("Content-type: application/text");
			header("Content-Disposition: attachment; filename=\"".$filename."\"");            
			header("Content-length: $fsize");
			header("Cache-control: private");

			while(!feof($fd)) {
				$buffer = fread($fd, 2048);
				echo $buffer;
			}
		}

		fclose ($fd);
		exit(0);
	}

	function deny (){
		header('HTTP/1.1 403 Refused');
		exit(0);
	}
?>