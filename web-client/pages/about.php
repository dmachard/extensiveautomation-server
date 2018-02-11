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

	if (!defined('CONFIG_OK'))
			exit( lang('access denied') );
	// prepare index page
	$INDEX_PAGE = get_pindex('about');
	$SUB_PAGE_DESCR = get_subpindex( 'about', 'about-description' ) ;
	$SUB_PAGE_RN = get_subpindex( 'about', 'about-release-notes' ) ;
	$SUB_PAGE_LICS = get_subpindex( 'about', 'about-licenses' ) ;

	// default sub-menu selected
	$s = $SUB_PAGE_DESCR;
	if ( isset($_GET['s']) )
	{
		$s_called = $_GET['s'];
		(!$s_called) ? $s=1 : $s=$s_called;
	}


?>
<div class="bxleft">
	<?php 
		// product description sub-menu
		( $s == $SUB_PAGE_DESCR ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_DESCR.'\')" >'.lang('about-description').'</div>';
		// release notes
		( $s == $SUB_PAGE_RN ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_RN.'\')" >'.lang('about-release-notes').'</div>';
		// licences
		( $s == $SUB_PAGE_LICS ) ? $active="selected" : $active ="";
		echo '<div class="link box-item '.$active.'" onclick="javascript:nav(\'./index.php?p='.$INDEX_PAGE.'&s='.$SUB_PAGE_LICS.'\')" >'.lang('about-licenses').'</div>';
	?>
</div>

<div class="bxcenter">
	<div id="box-warn"></div>
	<?php

		// specific function to parse rn
		function parseRn($lines){
			$rn = '';
			foreach ($lines as $line_num => $line) 
			{
				if ( ! startswith( $line, "\t") )
				{
					//$version = substr($line, 1); // remove *
					$rn .= "<h3>".htmlspecialchars($line)."</h3><p>";
				} elseif ( startswith( $line, "\t\t") ) {
					$rn .= '<p class="about-tab-sub-rn">'.htmlspecialchars($line)."</p>"; 
				} elseif ( startswith( $line, "\t") ) {
                    if ( startswith( $line, "\t---") ) {
                        $rn .= '<p class="about-tab-rn"><br />'.htmlspecialchars($line)."</p>";
                    } else {
                        $rn .= '<p class="about-tab-rn">'.htmlspecialchars($line)."</p>";
                    }
				} else {
					$rn .= "".htmlspecialchars($line)."<br />";
				}
			}
			return $rn;
		}

		// product description part
		if ( $s == $SUB_PAGE_DESCR )
		{
			// title
			echo '<div class="about-title-index">'.lang('about-description').'</div>';

			// body
			$tabsbody = array();
			$tb = "<h3>".$__LWF_APP_NAME." ".$__LWF_CFG['server-version']."</h3>".'<p>'.lang('about-product-description', $htmlentities=true).'<br /><br /><em>'.lang('about-developped-by').' '.$__LWF_APP_AUTHOR.'</em></p>';
			$tb .= '<h4>'.lang('contributors').'</h4>';
			$tb .= '<br /><em>Emmanuel Monsoro (extensive testing logo, ssh console adapter)</em>';
			$tb .= '<br /><em>Blaise Cador (security recommendations)</em>';
			$tb .= '<br /><em>Jean-Luc Pascal (support excel writting mode)</em>';
			$tb .= '<h4>'.lang('testers').'</h4>';
			$tb .= '<em>Emmanuel Monsoro</em>';
			$tb .= '<br /><em>Thibault Lecoq</em>';
			$tabsbody[] = $tb;
			echo construct_tabbody($tabsbody);
		}
		// release note 
		if ( $s == $SUB_PAGE_RN )
		{
			// title
			echo '<div class="about-title-index">'.lang('about-release-notes').'</div>';
			
			// construct tab menu
			$tabsmenu = array(	 lang('about-rn-server'), 
                                 lang('about-rn-adapters'), 
                                 lang('about-rn-libraries'), 
                                 lang('about-rn-toolbox') );
			echo construct_tabmenu($tabsmenu);

			// body
			$tabsbody = array();

            list($code, $details) = $RESTAPI->getReleaseNotes();
            
			if ( $code == 200 ) {
				// rn server
				//$lines = $RESTAPI->decodeData($details['core'],  $json=False) ;
				$tb = parseRn( explode("\n", $details['core']) );
				$tabsbody[] = $tb;

				// rn adapters
				//$lines = $RESTAPI->decodeData($details['adapters'],  $json=False) ;
				$tb = parseRn( explode("\n", $details['adapters']) );
				$tabsbody[] = $tb;

				// rn libraries
				//$lines = $RESTAPI->decodeData($details['libraries'],  $json=False) ;
				$tb = parseRn( explode("\n", $details['libraries']) );
				$tabsbody[] = $tb;

				// rn toolbox
				//$lines = $RESTAPI->decodeData($details['toolbox'],  $json=False) ;
				$tb = parseRn( explode("\n", $details['toolbox']) );
				$tabsbody[] = $tb;

			} else {
                $tb =  '<br /><img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > '.$details;
            }

			echo construct_tabbody($tabsbody);
		}
		// licenses part
		if ( $s == $SUB_PAGE_LICS )
		{

			// title
			echo '<div class="about-title-index">'.lang('about-licenses').'</div>';

			// body
			$tabsbody = array();
			$tb = "<h3>License agreements</h3>";
			$tb .= "<p><i>This product is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
<br /><br />
This product is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
<br /><br />
You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301 USA</i></p>";
		$tb .= "<h3>Others license agreements</h3>";
		$tb .= "This website is part of the extensive testing project; you can redistribute it and/or
modify it under the terms of the GNU General Public License, Version 3.
<br /><br />
This website is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
<br /><br />
You should have received a copy of the GNU General Public License,
along with this program. If not, see http://www.gnu.org/licenses/.";
			$tabsbody[] = $tb;
			echo construct_tabbody($tabsbody);
		}
	?>
	<!--</div>-->
</div>