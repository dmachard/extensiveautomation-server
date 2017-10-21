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

	// initialize header
	ob_start();
	
	if (!defined('CONFIG_OK'))
		exit("Access Denied");
	
	if ( $CORE->profile == null )
		exit("Access Denied");

	$menu_css = 'mainnav_text';
	$main_menu_css = 'mainnav_selected';

	// construct main menu
	$tmp_lwf_h = '<ul class="mainnav">';

	$p == get_pindex('overview') ?  $called_p = $main_menu_css : $called_p = $menu_css;
	$tmp_lwf_h .= '<li><span class="'.$called_p.'" onclick="javascript:nav(\'./index.php?p=1\')">'.lang('overview').'</span></li>';

	$p == get_pindex('tests') ?  $called_p = $main_menu_css : $called_p = $menu_css;
	$tmp_lwf_h .= '<li><span class="'.$called_p.'" onclick="javascript:nav(\'./index.php?p='.get_pindex('tests').'\')">'.lang('tests').'</span></li>';

	$p == get_pindex('administration') ?  $called_p = $main_menu_css : $called_p = $menu_css;
	$tmp_lwf_h .= '<li><span class="'.$called_p.'" onclick="javascript:nav(\'./index.php?p='.get_pindex('administration').'\')" >'.lang('administration').'</span></li>';

	$p == get_pindex('system') ?  $called_p = $main_menu_css : $called_p = $menu_css;
	$tmp_lwf_h .= '<li><span class="'.$called_p.'" onclick="javascript:nav(\'./index.php?p='.get_pindex('system').'\')" >'.lang('system').'</span></li>';

	$p == get_pindex('about') ?  $called_p = $main_menu_css : $called_p = $menu_css;
	$tmp_lwf_h .= '<li><span class="'.$called_p.'" onclick="javascript:nav(\'./index.php?p='.get_pindex('about').'\')" >'.lang('about').'</span></li>';
	
	$tmp_lwf_h .= '<li><span class="'.$menu_css.'" onclick="javascript:nav(\'./index.php?p=logout\')" >'.lang('logout').' ('.$CORE->profile['login'].') </span></li>';

	$tmp_lwf_h .=  '</ul>';
	$tmp_lwf_h .= '<div class="main_logo"><a href="http://www.extensivetesting.org"><img src="./images/main_logo.png" /></a></div>';
	echo $tmp_lwf_h;

	// finalize header
	$tpl_temp = trim(ob_get_contents());
	$tpl_main = str_replace('<!-- lwf_header -->', $tpl_temp, $tpl_main);

	// Empty output buffer and stop buffering
	ob_end_clean();

	// initialize body
	ob_start();
?>
