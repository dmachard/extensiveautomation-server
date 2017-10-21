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

	if (!defined('WS_OK'))
		exit( 'access denied' );

	/*
	Parse test files, response from xml api
	*/
	function parseFiles($items, $index, $parent, $projectid){
		global $CORE, $__LWF_APP_DFLT_STYLE;

		$ret = '';
		$j = 0;
		$ret .= '<ul>';
		foreach ($items as $item) {
			if ( $item->type == 'folder' ) {
					$ret .= '<li>';
					$ret .= '<input type="checkbox" id="item-'.$index.'-'.$j.'" /><label for="item-'.$index.'-'.$j.'">'.$item->name.'</label>';
					$ret .= parseFiles($item->content, $j, $parent."/".$item->name, $projectid);
					$ret .= '</li>';
			}

			if ( $item->type == 'file' ) {
				$ret .= '<li>';
				$extension = '';
				if ( endswith($item->name, TAX) ) {
					$ret .= '<span id="'.TAX.'">'.$item->name.'</span>'; 
					$extension = TAX;
				}
				elseif ( endswith($item->name, TUX) ) {
					$ret .= '<span id="'.TUX.'">'.$item->name.'</span>'; 
					$extension = TUX;
				}
				elseif ( endswith($item->name, TSX) ) {
					$ret .= '<span id="'.TSX.'">'.$item->name.'</span>'; 
					$extension = TSX;
				}
				elseif ( endswith($item->name, TPX) ) {
					$ret .= '<span id="'.TPX.'">'.$item->name.'</span>'; 
					$extension = TPX;
				}
				elseif ( endswith($item->name, TGX) ) {
					$ret .= '<span id="'.TGX.'">'.$item->name.'</span>'; 
					$extension = TGX;
				}
				elseif ( endswith($item->name, TCX) ) {
					$ret .= '<span id="'.TCX.'">'.$item->name.'</span>'; 
					$extension = TCX;
				}
				elseif ( endswith($item->name, TDX) ) {
					$ret .= '<span id="'.TDX.'">'.$item->name.'</span>'; 
					$extension = TDX;
				}
				elseif ( endswith($item->name, PNG)) {
					$ret .= '<span id="'.PNG.'">'.$item->name.'</span>'; 
					$extension = PNG;
				} else {
					$ret .= '<span>'.$item->name.'</span>'; 
				}
				$filename = substr($item->name, 0, strlen($item->name) - strlen(".".$extension) );
				$full_path =  $parent."/".$item->name ;
				$pathfile =  substr($full_path, 0, strlen($full_path) - strlen(".".$extension) );

				if ( endswith($item->name, TAX) or endswith($item->name, TSX) or endswith($item->name, TGX) or endswith($item->name, TPX) or endswith($item->name, TUX) ) {
					$ret .= '<a href="javascript:run_test('.$CORE->profile['id'].', '.$projectid.', \''.$extension.'\', \''.$filename.'\', \''.$pathfile.'\')">Run</a>';
					$ret .= '</li>';
				} else {
					$ret .= '</li>';
				}
			}
			$j++;
		}
		$ret .= '</ul>';
		return $ret;
	}

	/*
	Parse test result files, response from xml api
	*/
	function parseFilesResults($items, $index, $parent, $projectid){
		global $CORE, $__LWF_APP_DFLT_STYLE;

		$ret = '';
		$j = 0;
		$ret .= '<ul>';
		foreach ($items as $item) {
			if ( $item->type == 'folder' ) {
					$ret .= '<li>';
					$ret .= '<input type="checkbox" id="item-'.$index.'-'.$j.'" />';
                    if (strpos($item->name, '.') !== false) {
                        $testdetails = explode(".", $item->name); //timeArch, milliArch, testName, testUser
                        $test_name = base64_decode($testdetails[2]);
                        $test_user = $testdetails[3];
                        $test_time = explode("_",  $testdetails[0]); //2015-06-07_11:22:22
                        
                        $ret .= '<label for="item-'.$index.'-'.$j.'">'.$test_name.' - '.$test_user.' - '.$test_time[1].'</label>';
                    } else {
                        $ret .= '<label for="item-'.$index.'-'.$j.'">'.$item->name.'</label>';
                    }

					$ret .= parseFilesResults($item->content, $j, $parent."/".$item->name, $projectid);
					$ret .= '</li>';
			}

			if ( $item->type == 'file' ) {
				$ret .= '<li>';
				//$extension = '';
				//if ( endswith($item->name, ZIP) ) {
				//	$ret .= '<span id="'.ZIP.'">'.$item->name.'</span>'; 
				//}
                if ( endswith($item->name, TRX) ) {
                    // Noname1_0_UNDEFINED_0.trx  [testname] [replayid] [verdict] [nbcomments]
                    $test_result = 'pass';
                    if (strpos($item->name, FAIL) !== false) { $test_result='fail'; }
                    if (strpos($item->name, UNDEFINED) !== false) { $test_result='undef'; }
                    
					$ret .= '<span id="'.$test_result.'">'.$item->name.'</span>'; 
                    $ret .= '<a href="javascript:open_report('.$projectid.', \''.$parent.'\', \''.$item->name.'\', \'container-test-report\')">test report</a> ';
				} 
                //else {
				//	$ret .= '<span>'.$item->name.'</span>'; 
				//}
                
				$ret .= '</li>';
			}
			$j++;
		}
		$ret .= '</ul>';
		return $ret;
	}
    
	/*
	Execute a remote test
	*/
	function run_test($loginid, $projectid, $extension, $filename, $path){
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		// security check todo
		// checking if this loginid is attached to the projectid
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-relations-projects` WHERE  user_id=\''.mysql_real_escape_string($loginid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 603;
			$rsp["msg"] = 'User not attached the project!';
			return $rsp;
		} else {
			if ( $db->num_rows($rslt) == 0 )
			{
				$rsp["code"] = 603;
				$rsp["msg"] = 'User not attached the project!';
				return $rsp;
			} 
		}


		// continue, then execute the test
		$run =  $XMLRPC->runTest( intval($projectid), $extension, $filename, $path );
		if ( is_null($run) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = 'Error on the server!';
        } elseif ( $run == '404' ) {
			$rsp["code"] = 500;
			$rsp["msg"] = 'Unable to prepare, test missing';
		} else {
			$rsp["code"] = 200;
			$rsp["msg"] = "The test ".$filename." is running in background";
		}
		return $rsp;	

	}

	function tests_getrepositorystats($loginid, $type, $projectid){
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		// security check todo
		// checking if this loginid is attached to the projectid
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-relations-projects` WHERE  user_id=\''.mysql_real_escape_string($loginid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 603;
			$rsp["msg"] = 'User not attached the project!';
			return $rsp;
		} else {
			if ( $db->num_rows($rslt) == 0 )
			{
				$rsp["code"] = 603;
				$rsp["msg"] = 'User not attached the project!';
				return $rsp;
			} 
		}


		$rsp["code"] = 200;
		$rsp["msg"] = get_informations_tests($projectid=$projectid);

		return $rsp;	

	}

	function strbool($value){
		return $value ? 'True' : 'False';
	}

	function get_definition_env($projectid){
		global $db, $CORE, $__LWF_DB_PREFIX, $__LWF_CFG;
        if ( $__LWF_CFG['mysql-test-environment-encrypted'] ) {
            $sql_req = 'SELECT id, name, AES_DECRYPT(value, "'.$__LWF_CFG['mysql-test-environment-password'].'") as value FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE project_id=\''.mysql_real_escape_string($projectid).'\' ORDER BY name;';
		} else {
            $sql_req = 'SELECT id, name, value FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE project_id=\''.mysql_real_escape_string($projectid).'\' ORDER BY name;'; 
        }
        $tb = '';
        $rlst_envs = $db->query( $sql_req );
		if ( $rlst_envs ) 
		{
			$tb = '<table id="testenvs"><tr><td><b>'.lang('test-environment-name').'</b></td><td><b>'.lang('test-environment-value').'</b></td>';
            $tb .= '<td></td><td></td><td></td><td></td></tr>';
			while ($cur_u = $db->fetch_assoc($rlst_envs))
			{
				$env_name = htmlentities($cur_u['name']);
				$env_value = $cur_u['value'];

				$values_arr = json_decode($env_value, true);
				$values_str = '';
				if ( $values_arr === null)
					$values_str = 'error';

                // string, numeric and bool values
				if ( is_string($values_arr) or is_numeric($values_arr) or is_bool($values_arr) )
				{
                    $link_more = '';
					if ( is_bool($values_arr) )
					{
                        $values_str .= strbool($values_arr)."<br />";
					} else {
                        if ( strlen($values_arr) > 10 ) {
                                $values_str .= substr($values_arr, 0, 5)."...<br />";
                        } else {
                                $values_str .= $values_arr."<br />";
                        }
					}
				} else {
                
                    // dict values
                    $link_more = '[ <a href="#env-flag-'.$cur_u['id'].'" onclick="toggle_paramvalue(\'title-env-'.$cur_u['id'].'\', \'panel-env-'.$cur_u['id'].'\');"  >'.lang('expand').'</a> ]';

                    $values_str = '<div id="title-env-'.$cur_u['id'].'">...</div>';
                    $values_str .= '<div id="panel-env-'.$cur_u['id'].'" style="display: none;">';
                    
					foreach ($values_arr as $key => $value)
					{
						if ( is_bool($value) )
						{
							$values_str .= $key.': '.strbool($value)."<br />";
						}  else  {
							$values_str .= $key.': '.$value."<br />";
						}
					}
                    $values_str .= '</div>';
				}
                

				$link_edit = '[ <a href="./index.php?p='.get_pindex('tests').'&s='.get_subpindex( 'tests', 'test-environment' ).'&c=edit&id='.$cur_u['id'].'&prj='.$projectid.'">'.lang('edit').'</a> ] ';
				$link_delete = ' [ <a href="./index.php?p='.get_pindex('tests').'&s='.get_subpindex( 'tests', 'test-environment' ).'&c=del&id='.$cur_u['id'].'&prj='.$projectid.'
                ">'.lang('delete').'</a> ] ';
                $link_duplicate =  ' [ <a href="javascript:duplicateelementenv('.$cur_u['id'].', '.$projectid.')">'.lang('duplicate').'</a> ] ';
                
				//$tb .= '<tr class="list"><td>'.$env_name.'</td><td>'.$values_str.'</td><td>'.$link_edit.'</td><td>'.$link_delete.'</td><td>'.$link_duplicate.'</td><td>'.$link_more.'</td></tr>' ;
                $tb .= '<tr class="list"><td><div id="env-flag-'.$cur_u['id'].'">'.$env_name.'</div></td><td>'.$values_str.'</td><td>'.$link_edit.$link_delete.$link_duplicate.$link_more.'</td></tr>' ;
			}
			$tb .= "</table>";
		}
		return $tb;
	}

	/*
	Return all tests result tree through the xmlrpc interface
	*/
	function get_listing_testsresult($projectid){
		global $XMLRPC, $__LWF_APP_DFLT_STYLE;

		$listingFiles =  $XMLRPC->getFilesTestsResult($prjId=$projectid);
		$tb = '<span class="dotted">'.lang('results').'</span>';
		$tb .= ' <img  id="loader-run" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" class="icon-loader" alt="ajax-loader">';
		$tb .= '<br /><br />';
		$tb .= '<div class="css-treeview">';	
		$tb .= parseFilesResults($listingFiles, 0, '', $projectid);
		$tb .= '</div>';
		return $tb;
	}
	
	/*
	Return all tests tree through the xmlrpc interface
	*/
	function get_listing_tests($projectid){
		global $XMLRPC, $__LWF_APP_DFLT_STYLE;

		$listingFiles =  $XMLRPC->getFilesTests($prjId=$projectid);
		$tb = '<span class="dotted">'.lang('tests').'</span>';
		$tb .= ' <img  id="loader-run" src="./style/'.$__LWF_APP_DFLT_STYLE.'/img/ajax-loader-horizontal.gif" class="icon-loader" alt="ajax-loader">';
		$tb .= '<br /><br />';
		$tb .= '<div class="css-treeview">';	
		$tb .= parseFiles($listingFiles, 0, '', $projectid);
		$tb .= '</div>';
		return $tb;
	}

	/*
	Get test report throught xml interface
	*/
	function open_test_report( $projectid, $trpath, $trname ) {
		global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX, $XMLRPC, $__LWF_APP_DFLT_STYLE;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

        $report =  $XMLRPC->getTestPreview($prjId=$projectid, $trPath=$trpath, $trName=$trname);
		if ( is_null($report) ) {
			$rsp["code"] = 500;
			$rsp["msg"] = 'No report available';
        } else {
            $rsp["code"] = 200;
            $rsp["msg"] = "<br />".$report;
        }
		return $rsp;	
	}
    
    
	/*
	Return global statistics for tests through the xmlrpc interface
	*/
	function get_informations_tests($projectid){
		global $XMLRPC, $__LWF_APP_DFLT_STYLE;

		$testInfo =  $XMLRPC->getTestsInformations($prjId=$projectid);
		if ( is_null($testInfo) ) {
				$tb =  '<img src="./style/'. $__LWF_APP_DFLT_STYLE.'/img/stop_round.png" > The server is stopped!';
		} else {
            // if ( !array_key_exists(TUX, $testInfo) ) 
            // {
            // }
            
			$tb = '<span class="dotted">'.lang('tests-files').'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('testunit').'</td><td>'.$testInfo[TUX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('testabstract').'</td><td>'.$testInfo[TAX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('testsuite').'</td><td>'.$testInfo[TSX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('testplan').'</td><td>'.$testInfo[TPX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('testglobal').'</td><td>'.$testInfo[TGX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('testconfig').'</td><td>'.$testInfo[TCX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('testdata').'</td><td>'.$testInfo[TDX]['nb'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('image').'</td><td>'.$testInfo[PNG]['nb'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey"></td><td>'.$testInfo->{'nb-tot'}.'</td></tr></table>';

			$tb .= '<br /><span class="dotted">'.lang('testunit').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TUX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TUX]['max'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-tu'}.'</td></tr></table>';
            
            $tb .= '<br /><span class="dotted">'.lang('testabstract').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TAX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TAX]['max'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-ta'}.'</td></tr></table>';

			$tb .= '<br /><span class="dotted">'.lang('testsuite').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TSX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TSX]['max'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-ts'}.'</td></tr></table>';

			$tb .= '<br /><span class="dotted">'.lang('testplan').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TPX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TPX]['max'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-tp'}.'</td></tr></table>';

			$tb .= '<br /><span class="dotted">'.lang('testglobal').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TGX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TGX]['max'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-tg'}.'</td></tr></table>';

			$tb .= '<br /><span class="dotted">'.lang('testconfig').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TCX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TCX]['max'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-tc'}.'</td></tr></table>';

			$tb .= '<br /><span class="dotted">'.lang('testdata').' ('.lang('bytes').')'.'</span>';
			$tb .= '<table><tr><td class="table tablekey">'.lang('minimum').'</td><td>'.$testInfo[TDX]['min'].'</td></tr>';
			$tb .= '<tr><td class="table tablekey">'.lang('maximum').'</td><td>'.$testInfo[TDX]['max'].'</td></tr>';
            $tb .= '<tr><td class="table tablekey"></td><td></td></tr></table>';
			//$tb .= '<tr><td class="table tablekey">'.lang('average').'</td><td>'.$testInfo->{'size-avg-td'}.'</td></tr></table>';

		}
		return $tb;
	}

	/*
	Return statistics for script
	*/
	function get_stats_script($table, $loginid=null, $graph=true, $projectid=null){
		global $db;

		$sql_req = "SELECT ";
        $sql_req .= "SUM( IF(result = '".COMPLETE."', 1, 0) ) AS ".COMPLETE.", ";
        $sql_req .= "SUM( IF(result = '".ERROR."', 1, 0) ) AS ".ERROR.", ";
        $sql_req .= "SUM( IF(result = '".KILLED."', 1, 0) ) AS ".KILLED.", ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()), 1, 0) ) AS 'TODAY', ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()), 1, 0) ) AS 'WEEK', ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()), 1, 0) ) AS 'MONTH', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY), 1, 0) ) AS 'YESTERDAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()) AND result = '".COMPLETE."', 1, 0) ) AS 'COMPLETE_TODAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()) AND result = '".ERROR."', 1, 0) ) AS 'ERROR_TODAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()) AND result = '".KILLED."', 1, 0) ) AS 'KILLED_TODAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY) AND result = '".COMPLETE."', 1, 0) ) AS 'COMPLETE_YESTERDAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY) AND result = '".ERROR."', 1, 0) ) AS 'ERROR_YESTERDAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY) AND result = '".KILLED."', 1, 0) ) AS 'KILLED_YESTERDAY', ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()) AND result = '".COMPLETE."', 1, 0) ) AS 'COMPLETE_WEEK', ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()) AND result = '".ERROR."', 1, 0) ) AS 'ERROR_WEEK', ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()) AND result = '".KILLED."', 1, 0) ) AS 'KILLED_WEEK', ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()) AND result = '".COMPLETE."', 1, 0) ) AS 'COMPLETE_MONTH', ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()) AND result = '".ERROR."', 1, 0) ) AS 'ERROR_MONTH', ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()) AND result = '".KILLED."', 1, 0) ) AS 'KILLED_MONTH' ";
        $sql_req .= "FROM `".$table."`";
        
		if ( $loginid!=null)
			$sql_req .= " WHERE user_id='".$loginid."'";
		if ( $projectid!=null) {
			if ( $loginid!=null) {
				$sql_req .= " AND project_id='".$projectid."'";
			} else {
				$sql_req .= " WHERE project_id='".$projectid."'";
			}
		}

		$rlst_usrs = $db->query($sql_req);
		if ( ! $rlst_usrs)
			$tb = 'Unable to get stats scripts '.$db->str_error();
		else
		{
			$nb_total = 0; $nb_complete = 0; $nb_error = 0; $nb_killed = 0;
			$nb_total_today = 0; $nb_complete_today = 0; $nb_error_today = 0; $nb_killed_today = 0;
			$nb_total_yesterday = 0; $nb_complete_yesterday = 0; $nb_error_yesterday = 0; $nb_killed_yesterday = 0;
			$nb_today = 0; $nb_week = 0; $nb_month = 0; $nb_yesterday = 0;
			$nb_total_week = 0; $nb_complete_week = 0; $nb_error_week = 0; $nb_killed_week = 0;
			$nb_total_month = 0; $nb_complete_month = 0; $nb_error_month = 0; $nb_killed_month = 0;

			$cur_stats = $db->fetch_assoc($rlst_usrs);
			if ( $cur_stats['COMPLETE_WEEK'] != null ) $nb_complete_week = $cur_stats['COMPLETE_WEEK'];  
			if ( $cur_stats['ERROR_WEEK'] != null ) $nb_error_week = $cur_stats['ERROR_WEEK'];  
			if ( $cur_stats['KILLED_WEEK'] != null ) $nb_killed_week = $cur_stats['KILLED_WEEK'];  
			
			if ( $cur_stats['COMPLETE_MONTH'] != null ) $nb_complete_month = $cur_stats['COMPLETE_MONTH'];  
			if ( $cur_stats['ERROR_MONTH'] != null ) $nb_error_month = $cur_stats['ERROR_MONTH'];  
			if ( $cur_stats['KILLED_MONTH'] != null ) $nb_killed_month = $cur_stats['KILLED_MONTH'];  

			if ( $cur_stats['COMPLETE_TODAY'] != null ) $nb_complete_today = $cur_stats['COMPLETE_TODAY'];  
			if ( $cur_stats['ERROR_TODAY'] != null ) $nb_error_today = $cur_stats['ERROR_TODAY'];  
			if ( $cur_stats['KILLED_TODAY'] != null ) $nb_killed_today = $cur_stats['KILLED_TODAY'];  

			if ( $cur_stats['COMPLETE_YESTERDAY'] != null ) $nb_complete_yesterday = $cur_stats['COMPLETE_YESTERDAY'];  
			if ( $cur_stats['ERROR_YESTERDAY'] != null ) $nb_error_yesterday = $cur_stats['ERROR_YESTERDAY'];  
			if ( $cur_stats['KILLED_YESTERDAY'] != null ) $nb_killed_yesterday = $cur_stats['KILLED_YESTERDAY'];  


			// extract nb ok, ko in all
			if ( $cur_stats['COMPLETE'] != null ) $nb_complete = $cur_stats[COMPLETE];  
			if ( $cur_stats['ERROR'] != null ) $nb_error = $cur_stats[ERROR]; 
			if ( $cur_stats['KILLED'] != null ) $nb_killed = $cur_stats[KILLED];
			
			// extract nb run
			if ( $cur_stats['TODAY'] != null ) $nb_today = $cur_stats['TODAY']; 
			if ( $cur_stats['WEEK'] != null ) $nb_week = $cur_stats['WEEK']; 
			if ( $cur_stats['MONTH'] != null ) $nb_month = $cur_stats['MONTH']; 
			if ( $cur_stats['YESTERDAY'] != null ) $nb_yesterday = $cur_stats['YESTERDAY']; 
			
			// count all
			$nb_total = $nb_complete + $nb_error + $nb_killed;
			$nb_total_today = $nb_complete_today + $nb_error_today + $nb_killed_today;
			$nb_total_yesterday = $nb_complete_yesterday + $nb_error_yesterday + $nb_killed_yesterday;
			$nb_total_week = $nb_complete_week + $nb_error_week + $nb_killed_week;
			$nb_total_month = $nb_complete_month + $nb_error_month + $nb_killed_month;
			
			// get percents in all
            if ($nb_total == 0){
                $nb_complete_percent = 0;
                $nb_error_percent = 0;
                $nb_killed_percent = 0;
            } else {
                $nb_complete_percent = round( ( 100 * $nb_complete ) / $nb_total, 0 );
                $nb_error_percent  = round( ( 100 * $nb_error ) / $nb_total, 0 );
                $nb_killed_percent = round( ( 100 * $nb_killed ) / $nb_total, 0 );
            }
            
			// get percents today
            if ($nb_total_today == 0){
                $nb_complete_today_percent = 0;
                $nb_error_today_percent = 0;
                $nb_killed_today_percent = 0;
            } else {
                $nb_complete_today_percent = round( ( 100 * $nb_complete_today ) / $nb_total_today, 0 );
                $nb_error_today_percent  = round( ( 100 * $nb_error_today ) / $nb_total_today, 0 );
                $nb_killed_today_percent = round( ( 100 * $nb_killed_today ) / $nb_total_today, 0 );
            }
            
			// get percents yesterday
            if ($nb_total_yesterday == 0){
                $nb_complete_yesterday_percent = 0;
                $nb_error_yesterday_percent = 0;
                $nb_killed_yesterday_percent = 0;
            } else {
                $nb_complete_yesterday_percent = round( ( 100 * $nb_complete_yesterday ) / $nb_total_yesterday, 0 );
                $nb_error_yesterday_percent  = round( ( 100 * $nb_error_yesterday ) / $nb_total_yesterday, 0 );
                $nb_killed_yesterday_percent = round( ( 100 * $nb_killed_yesterday ) / $nb_total_yesterday, 0 );
            }
            
			// get percents week
            if ($nb_total_week == 0){
                $nb_complete_week_percent = 0;
                $nb_error_week_percent = 0;
                $nb_killed_week_percent = 0;
            } else {
                $nb_complete_week_percent = round( ( 100 * $nb_complete_week ) / $nb_total_week, 0 );
                $nb_error_week_percent  = round( ( 100 * $nb_error_week ) / $nb_total_week, 0 );
                $nb_killed_week_percent = round( ( 100 * $nb_killed_week ) / $nb_total_week, 0 );
            }
            
			// get percents month
            if ($nb_total_month == 0){
                $nb_complete_month_percent = 0;
                $nb_error_month_percent = 0;
                $nb_killed_month_percent = 0;
            } else {
                $nb_complete_month_percent = round( ( 100 * $nb_complete_month ) / $nb_total_month, 0 );
                $nb_error_month_percent  = round( ( 100 * $nb_error_month ) / $nb_total_month, 0 );
                $nb_killed_month_percent = round( ( 100 * $nb_killed_month ) / $nb_total_month, 0 );
            }

			$tb = '<span class="dotted">'.lang('result').'</span>';
			$tb .= '<table class="table">';
			$tb .= '<tr><td class="firstcolumn"></td><td></td><td>'.lang('total').'</td><td>'.lang('today').'</td><td>'.lang('yesterday').'</td><td>'.lang('this-week').'</td><td>'.lang('this-month').'</td></tr>';
			$tb .= '<tr><td class="firstcolumn"></td><td>'.lang('complete').'</td><td class="tablevalue">'.$nb_complete.' ('.$nb_complete_percent.'%)'.'</td><td class="tablevalue">'.$nb_complete_today.' ('.$nb_complete_today_percent.'%)'.'</td><td class="tablevalue">'.$nb_complete_yesterday.' ('.$nb_complete_yesterday_percent.'%)'.'</td><td class="tablevalue">'.$nb_complete_week.' ('.$nb_complete_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_complete_month.' ('.$nb_complete_month_percent.'%)'.'</td></tr>';

			$tb .= '<tr><td class="firstcolumn"></td><td>'.lang('error').'</td><td class="tablevalue">'.$nb_error.' ('.$nb_error_percent.'%)'.'</td><td class="tablevalue">'.$nb_error_today.' ('.$nb_error_today_percent.'%)'.'</td><td class="tablevalue">'.$nb_error_yesterday.' ('.$nb_error_yesterday_percent.'%)'.'</td><td class="tablevalue">'.$nb_error_week.' ('.$nb_error_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_error_month.' ('.$nb_error_month_percent.'%)'.'</td></tr>';

			$tb .= '<tr><td class="firstcolumn"></td><td>'.lang('killed').'</td><td class="tablevalue">'.$nb_killed.' ('.$nb_killed_percent.'%)'.'</td><td class="tablevalue">'.$nb_killed_today.' ('.$nb_killed_today_percent.'%)'.'</td><td class="tablevalue">'.$nb_killed_yesterday.' ('.$nb_killed_yesterday_percent.'%)'.'</td><td class="tablevalue">'.$nb_killed_week.' ('.$nb_killed_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_killed_month.' ('.$nb_killed_month_percent.'%)'.'</td></tr>';
			//$tb .= '<tr class="tablevalue"><td class="firstcolumn"></td><td></td><td>'.$nb_total.'</td><td>'.$nb_total_today.'</td><td>'.$nb_total_yesterday.'</td><td>'.$nb_total_week.'</td><td>'.$nb_total_month.'</td></tr>';
			$tb .= '</table>';

			$tb .= '<br /><span class="dotted">'.lang('run').'</span>';
			$tb .= '<table class="table">';
			$tb .=  '<tr><td class="firstcolumn"></td><td>'.lang('total').'</td><td>'.lang('today').'</td><td>'.lang('yesterday').'</td><td>'.lang('this-week').'</td><td>'.lang('this-month').'</td></tr>';
			$tb .= '<tr class="tablevalue"><td class="firstcolumn"></td><td>'.$nb_total.'</td><td>'.$nb_total_today.'</td><td>'.$nb_total_yesterday.'</td><td>'.$nb_total_week.'</td><td>'.$nb_month.'</td></tr>';
			$tb .= '</table>';

			$sql_req = "SELECT duration FROM  `".$table."`";
			if ( $loginid!=null)
				$sql_req .= " WHERE user_id='".$loginid."'";
			if ( $projectid!=null) {
				if ( $loginid!=null) {
					$sql_req .= " AND project_id='".$projectid."'";
				} else {
					$sql_req .= " WHERE project_id='".$projectid."'";
				}
			}

			$rlst_usrs = $db->query($sql_req);
			if ( ! $rlst_usrs)
				$tb = 'Unable to get duration stats '.$db->str_error();
			else
			{
				$min = 0; $max = 0; $avg = 0;
				$durations = array();
				while ($cur = $db->fetch_assoc($rlst_usrs))
					array_push($durations, $cur['duration']);

				if (count($durations) > 0 ) {
					$min = round( min($durations) ,2);
					$max = round( max($durations) ,2);
					$avg = round( array_sum($durations) / count($durations) ,2);
				}

				$tb .= '<br /><span class="dotted">'.lang('duration').'</span>';
				$tb .= '<table class="table"><tr><td class="firstcolumn"></td><td>'.lang('minimum').'</td><td class="tablevalue">'.$min.'</td></tr>';
				$tb .= '<tr><td></td><td>'.lang('maximum').'</td><td class="tablevalue">'.$max.'</td></tr>';
				$tb .= '<tr><td></td><td>'.lang('average').'</td><td class="tablevalue">'.$avg.'</td></tr></table>';
			}

			// add graphic
			if ($graph  && $nb_total ) {
				$tb .= '<br /><span class="dotted">'.lang('graphic').'</span>';
				$tb .= '<table class="table"><tr><td class="firstcolumn"></td><td><img src="chart.php?tt=s&amp;d='.$nb_complete.','.$nb_error.','.$nb_killed.'"/>';
				$tb .= '</td></tr></table>';
			}

		}
		return $tb;
	}

	/*
	Return statistics for tests 
	*/
	function get_stats_tests($table, $loginid=null, $graph=true, $projectid=null){
		global $db, $__LWF_DB_PREFIX;

		$sql_req = "SELECT ";
        $sql_req .= "SUM( IF(result = '".PASS."', 1, 0) ) AS ".PASS.", ";
        $sql_req .= "SUM( IF(result = '".FAIL."', 1, 0) ) AS ".FAIL.", ";
        $sql_req .= "SUM( IF(result = '".UNDEFINED."', 1, 0) ) AS ".UNDEFINED.", ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()), 1, 0) ) AS 'TODAY', ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()), 1, 0) ) AS 'WEEK', ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()), 1, 0) ) AS 'MONTH', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY), 1, 0) ) AS 'YESTERDAY', ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()) AND result = '".PASS."', 1, 0) ) AS PASS_TODAY, ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()) AND result = '".FAIL."', 1, 0) ) AS FAIL_TODAY, ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()) AND result = '".UNDEFINED."', 1, 0) ) AS UNDEFINED_TODAY, ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY) AND result = '".PASS."', 1, 0) ) AS PASS_YESTERDAY, ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY) AND result = '".FAIL."', 1, 0) ) AS FAIL_YESTERDAY, ";
        $sql_req .= "SUM( IF(DAY(date)=DAY(NOW()- INTERVAL 1 DAY) AND result = '".UNDEFINED."', 1, 0) ) AS UNDEFINED_YESTERDAY, ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()) AND result = '".PASS."', 1, 0) ) AS PASS_WEEK, ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()) AND result = '".FAIL."', 1, 0) ) AS FAIL_WEEK, ";
        $sql_req .= "SUM( IF(WEEK(date)=WEEK(NOW()) AND result = '".UNDEFINED."', 1, 0) ) AS UNDEFINED_WEEK, ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()) AND result = '".PASS."', 1, 0) ) AS PASS_MONTH, ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()) AND result = '".FAIL."', 1, 0) ) AS FAIL_MONTH, ";
        $sql_req .= "SUM( IF(MONTH(date)=MONTH(NOW()) AND result = '".UNDEFINED."', 1, 0) ) AS UNDEFINED_MONTH ";
        $sql_req .= "FROM `".$table."`";
        
		if ( $loginid!=null)
			$sql_req .= " WHERE user_id='".$loginid."'";
		if ( $projectid!=null) {
			if ( $loginid!=null) {
				$sql_req .= " AND project_id='".$projectid."'";
			} else {
				$sql_req .= " WHERE project_id='".$projectid."'";
			}
		}
        
		$rlst_usrs = $db->query($sql_req);
		if ( ! $rlst_usrs)
			$tb = 'Unable to get stats '.$db->str_error();
		else
		{
			$nb_total = 0; $nb_pass = 0; $nb_fail = 0; $nb_undef = 0; 
			$nb_total_today = 0; $nb_pass_today = 0; $nb_fail_today = 0; $nb_undef_today = 0; 
			$nb_total_yesterday = 0; $nb_pass_yesterday = 0; $nb_fail_yesterday = 0; $nb_undef_yesterday = 0; 
			$nb_total_week = 0; $nb_pass_week = 0; $nb_fail_week = 0; $nb_undef_week = 0; 
			$nb_total_month = 0; $nb_pass_month = 0; $nb_fail_month = 0; $nb_undef_month = 0; 
			$nb_today = 0; $nb_week = 0; $nb_month = 0; $nb_yesterday = 0;

			$cur_stats = $db->fetch_assoc($rlst_usrs);
			if ( $cur_stats['PASS_MONTH'] != null ) $nb_pass_month = $cur_stats['PASS_MONTH'];  
			if ( $cur_stats['FAIL_MONTH'] != null ) $nb_fail_month = $cur_stats['FAIL_MONTH']; 
			if ( $cur_stats['UNDEFINED_MONTH'] != null ) $nb_undef_month = $cur_stats['UNDEFINED_MONTH'];

			if ( $cur_stats['PASS_WEEK'] != null ) $nb_pass_week = $cur_stats['PASS_WEEK'];  
			if ( $cur_stats['FAIL_WEEK'] != null ) $nb_fail_week = $cur_stats['FAIL_WEEK']; 
			if ( $cur_stats['UNDEFINED_WEEK'] != null ) $nb_undef_week = $cur_stats['UNDEFINED_WEEK'];

			if ( $cur_stats['PASS_TODAY'] != null ) $nb_pass_today = $cur_stats['PASS_TODAY'];  
			if ( $cur_stats['FAIL_TODAY'] != null ) $nb_fail_today = $cur_stats['FAIL_TODAY']; 
			if ( $cur_stats['UNDEFINED_TODAY'] != null ) $nb_undef_today = $cur_stats['UNDEFINED_TODAY'];

			if ( $cur_stats['PASS_YESTERDAY'] != null ) $nb_pass_yesterday = $cur_stats['PASS_YESTERDAY'];  
			if ( $cur_stats['FAIL_YESTERDAY'] != null ) $nb_fail_yesterday = $cur_stats['FAIL_YESTERDAY']; 
			if ( $cur_stats['UNDEFINED_YESTERDAY'] != null ) $nb_undef_yesterday = $cur_stats['UNDEFINED_YESTERDAY'];

			if ( $cur_stats[PASS] != null ) $nb_pass = $cur_stats[PASS];  
			if ( $cur_stats[FAIL] != null ) $nb_fail = $cur_stats[FAIL]; 
			if ( $cur_stats[UNDEFINED] != null ) $nb_undef = $cur_stats[UNDEFINED];

			if ( $cur_stats['TODAY'] != null ) $nb_today = $cur_stats['TODAY']; 
			if ( $cur_stats['WEEK'] != null ) $nb_week = $cur_stats['WEEK']; 
			if ( $cur_stats['MONTH'] != null ) $nb_month = $cur_stats['MONTH']; 

			$nb_total = $nb_pass + $nb_fail + $nb_undef;
			$nb_total_today = $nb_pass_today + $nb_fail_today + $nb_undef_today;
			$nb_total_yesterday = $nb_pass_yesterday + $nb_fail_yesterday + $nb_undef_yesterday;
			$nb_total_week = $nb_pass_week + $nb_fail_week + $nb_undef_week;
			$nb_total_month = $nb_pass_month + $nb_fail_month + $nb_undef_month;
			
			# get percents
			if ($nb_total > 0 ) {
				$nb_pass_percent = round( ( 100 * $nb_pass ) / $nb_total, 0 );
				$nb_fail_percent  = round( ( 100 * $nb_fail ) / $nb_total, 0 );
				$nb_undef_percent = round( ( 100 * $nb_undef ) / $nb_total, 0 );
			} else {
				$nb_pass_percent = 0;
				$nb_fail_percent = 0;
				$nb_undef_percent = 0;
			}

			# get percents today
			if ($nb_total_today > 0 ) {
				$nb_pass_today_percent = round( ( 100 * $nb_pass_today ) / $nb_total_today, 0 );
				$nb_fail_today_percent  = round( ( 100 * $nb_fail_today ) / $nb_total_today, 0 );
				$nb_undef_today_percent = round( ( 100 * $nb_undef_today ) / $nb_total_today, 0 );
			} else {
				$nb_pass_today_percent = 0;
				$nb_fail_today_percent = 0;
				$nb_undef_today_percent = 0;
			}

			# get percents yesterday
			if ($nb_total_yesterday > 0 ) {
				$nb_pass_yesterday_percent = round( ( 100 * $nb_pass_yesterday ) / $nb_total_yesterday, 0 );
				$nb_fail_yesterday_percent  = round( ( 100 * $nb_fail_yesterday ) / $nb_total_yesterday, 0 );
				$nb_undef_yesterday_percent = round( ( 100 * $nb_undef_yesterday ) / $nb_total_yesterday, 0 );
			} else {
				$nb_pass_yesterday_percent = 0;
				$nb_fail_yesterday_percent = 0;
				$nb_undef_yesterday_percent = 0;
			}

			# get percents this week
			if ($nb_total_week > 0 ) {
				$nb_pass_week_percent = round( ( 100 * $nb_pass_week ) / $nb_total_week, 0 );
				$nb_fail_week_percent  = round( ( 100 * $nb_fail_week ) / $nb_total_week, 0 );
				$nb_undef_week_percent = round( ( 100 * $nb_undef_week ) / $nb_total_week, 0 );
			} else {
				$nb_pass_week_percent = 0;
				$nb_fail_week_percent = 0;
				$nb_undef_week_percent = 0;
			}

			# get percents this month
			if ($nb_total_month > 0 ) {
				$nb_pass_month_percent = round( ( 100 * $nb_pass_month ) / $nb_total_month, 0 );
				$nb_fail_month_percent  = round( ( 100 * $nb_fail_month ) / $nb_total_month, 0 );
				$nb_undef_month_percent = round( ( 100 * $nb_undef_month ) / $nb_total_month, 0 );
			} else {
				$nb_pass_month_percent = 0;
				$nb_fail_month_percent = 0;
				$nb_undef_month_percent = 0;
			}

			$tb = '<span class="dotted">'.lang('result').'</span>';
			$tb .= '<table class="table">';
			$tb .= '<tr><td class="firstcolumn"></td><td></td><td>'.lang('total').'</td><td>'.lang('today').'</td><td>'.lang('yesterday').'</td><td>'.lang('this-week').'</td><td>'.lang('this-month').'</td></tr>';
			$tb .= '<tr><td></td><td>'.lang('pass').'</td><td class="tablevalue">'.$nb_pass.' ('.$nb_pass_percent.'%)'.'</td><td class="tablevalue">'.$nb_pass_today.' ('.$nb_pass_today_percent.'%)'.'</td><td class="tablevalue">'.$nb_pass_yesterday.' ('.$nb_pass_yesterday_percent.'%)'.'</td><td class="tablevalue">'.$nb_pass_week.' ('.$nb_pass_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_pass_month.' ('.$nb_pass_month_percent.'%)'.'</td></tr>';

			$tb .= '<tr><td></td><td>'.lang('fail').'</td><td class="tablevalue">'.$nb_fail.' ('.$nb_fail_percent.'%)'.'</td><td class="tablevalue">'.$nb_fail_today.' ('.$nb_fail_today_percent.'%)'.'</td><td class="tablevalue">'.$nb_fail_yesterday.' ('.$nb_fail_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_fail_week.' ('.$nb_fail_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_fail_month.' ('.$nb_fail_month_percent.'%)'.'</td></tr>';

			$tb .= '<tr><td></td><td >'.lang('undef').'</td><td class="tablevalue">'.$nb_undef.' ('.$nb_undef_percent.'%)'.'</td><td class="tablevalue">'.$nb_undef_today.' ('.$nb_undef_today_percent.'%)'.'</td><td class="tablevalue">'.$nb_undef_yesterday.' ('.$nb_undef_yesterday_percent.'%)'.'</td><td class="tablevalue">'.$nb_undef_week.' ('.$nb_undef_week_percent.'%)'.'</td><td class="tablevalue">'.$nb_undef_month.' ('.$nb_undef_month_percent.'%)'.'</td></tr>';
			//$tb .= '<tr class="tablevalue"><td></td><td></td><td >'.$nb_total.'</td><td>'.$nb_total_today.'</td><td>'.$nb_total_yesterday.'</td></tr>';
			$tb .= '</table>';

			$tb .= '<br /><span class="dotted">'.lang('run').'</span>';
			$tb .= '<table class="table">';
			$tb .=  '<tr><td class="table firstcolumn"></td><td>'.lang('total').'</td><td>'.lang('today').'</td><td>'.lang('yesterday').'</td><td>'.lang('this-week').'</td><td>'.lang('this-month').'</td></tr>';
			$tb .= '<tr class="tablevalue"><td ></td><td >'.$nb_total.'</td><td>'.$nb_today.'</td><td>'.$nb_total_yesterday.'</td><td>'.$nb_total_week.'</td><td>'.$nb_total_month.'</td></tr>';
			$tb .= '</table>';

			$sql_req = "SELECT duration FROM  `".$table."`";
			if ( $loginid!=null)
				$sql_req .= " WHERE user_id='".$loginid."'";
			if ( $projectid!=null) {
				if ( $loginid!=null) {
					$sql_req .= " AND project_id='".$projectid."'";
				} else {
					$sql_req .= " WHERE project_id='".$projectid."'";
				}
			}

			$rlst_usrs = $db->query($sql_req);
			if ( ! $rlst_usrs)
				$tb = 'Unable to get duration stats'.$db->str_error();
			else
			{
				$min = 0; $max = 0; $avg = 0;
				$durations = array();
				while ($cur = $db->fetch_assoc($rlst_usrs))
					array_push($durations, $cur['duration']);

				if (count($durations) > 0 ) {
					$min = round(min($durations), 2);
					$max = round(max($durations) ,2);
					$avg = round( array_sum($durations) / count($durations) ,2);
				}

				$tb .= '<br /><span class="dotted">'.lang('duration').'</span>';
				$tb .= '<table class="table"><tr><td class="firstcolumn"></td><td>'.lang('minimum').'</td><td class="tablevalue">'.$min.'</td></tr>';
				$tb .= '<tr><td></td><td>'.lang('maximum').'</td><td class="tablevalue">'.$max.'</td></tr>';
				$tb .= '<tr><td></td><td>'.lang('average').'</td><td class="tablevalue">'.$avg.'</td></tr></table>';
			}

			if ( $table == $__LWF_DB_PREFIX.'-testglobals-stats' or $table == $__LWF_DB_PREFIX.'-testplans-stats' or $table == $__LWF_DB_PREFIX.'-testsuites-stats' or $table == $__LWF_DB_PREFIX.'-testunits-stats' or $table == $__LWF_DB_PREFIX.'-testabstracts-stats' ) {

				$sql_req = "SELECT duration FROM  `".$__LWF_DB_PREFIX."-writing-stats`";
				if ( $table == $__LWF_DB_PREFIX.'-testplans-stats' ) {
					$sql_req .= " WHERE is_tp='1'";
				} elseif ( $table == $__LWF_DB_PREFIX.'-testsuites-stats' ) {
					$sql_req .= " WHERE is_ts='1'";
				} elseif ( $table == $__LWF_DB_PREFIX.'-testabstracts-stats' ) {
					$sql_req .= " WHERE is_ta='1'";
				} else {
					$sql_req .= " WHERE is_tu='1'";
				}
				if ( $loginid!=null)
					$sql_req .= " AND user_id='".$loginid."'";
				if ( $projectid!=null) {
					if ( $loginid!=null) {
						$sql_req .= " AND project_id='".$projectid."'";
					} else {
						$sql_req .= " AND project_id='".$projectid."'";
					}
				}
	
				$rlst_dev = $db->query($sql_req);
				if ( ! $rlst_dev)
					$tb = 'Unable to get duration writing stats '.$db->str_error();
				else
				{
					$min_dev = 0; $max_dev = 0; $avg_dev = 0;
					$durations_dev = array();
					while ($cur = $db->fetch_assoc($rlst_dev))
						array_push($durations_dev, $cur['duration']);

					if (count($durations_dev) > 0 ) {
						$min_dev = round(min($durations_dev), 2);
						$max_dev = round(max($durations_dev) ,2);
						$avg_dev = round( array_sum($durations_dev) / count($durations_dev) ,2);
					}

					$tb .= '<br /><span class="dotted">'.lang('duration-dev').'</span>';
					$tb .= '<table class="table"><tr><td class="firstcolumn"></td><td>'.lang('minimum').'</td><td class="tablevalue">'.$min_dev.'</td></tr>';
					$tb .= '<tr><td></td><td>'.lang('maximum').'</td><td class="tablevalue">'.$max_dev.'</td></tr>';
					$tb .= '<tr><td></td><td>'.lang('average').'</td><td class="tablevalue">'.$avg_dev.'</td></tr></table>';
				}
			}

			// add graphic
			if ($graph && $nb_total) {
				$tb .= '<br /><span class="dotted">'.lang('graphic').'</span>';
				$tb .= '<table class="table"><tr><td class="firstcolumn"></td><td><img src="chart.php?tt=t&amp;d='.$nb_pass.','.$nb_fail.','.$nb_undef.''.'"/>';
				$tb .= '</td></tr></table>';
			}


		}
		return $tb;
	}

	/*
	Return all tests tree
	*/
	function tests_getlisting( $loginid, $type, $projectid ) {
		global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$rsp["code"] = 200;
		$rsp["msg"] = get_listing_tests($projectid=$projectid);

		return $rsp;	
	}
	
    /*
	Reset all statistics
	*/
    function tests_resetallstats() {
        global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
        
		// truncate
		$sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-scripts-stats`;';
		$rslt1 = $db->query( $sql_req );

        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-testglobals-stats`;';
        $rslt2 = $db->query( $sql_req );

        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-testplans-stats`;';
        $rslt3 = $db->query( $sql_req );
        
        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-testsuites-stats`;';
        $rslt4 = $db->query( $sql_req );
        
        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-testabstracts-stats`;';
        $rslt5 = $db->query( $sql_req );
        
        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-testunits-stats`;';
        $rslt6 = $db->query( $sql_req );
        
        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-testcases-stats`;';
        $rslt7 = $db->query( $sql_req );
        
        $sql_req = 'TRUNCATE `'.$__LWF_DB_PREFIX.'-writing-stats`;';
        $rslt8 = $db->query( $sql_req );
        
        if ( !$rslt1 and !$rslt2 and !$rslt3 and !$rslt4 and !$rslt5 and !$rslt6 and !$rslt7 and !rslt8 ) 
        {
            $rsp["code"] = 500;
            $rsp["msg"] = $db->str_error("Unable to reset tests statistics")."(".$sql_req.")";
            return $rsp;
        } else {
            $rsp["msg"] = lang('tests-stats-reseted');
            $rsp["code"] = 200;
        } 
        
        return $rsp;
    }
    
    /*
	Reset tests statistics by user and project
	*/
    function tests_resetstatsby($loginid, $projectid) {
        global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-scripts-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt1 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-testglobals-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt2 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-testplans-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt3 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-testsuites-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt4 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-testabstracts-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt5 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-testunits-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt6 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-testcases-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt7 = $db->query( $sql_req );
        
        $sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-writing-stats` WHERE user_id=\''.$loginid.'\' and project_id=\''.$projectid.'\' ;';
		$rslt8 = $db->query( $sql_req );
        
        if ( !$rslt1 and !$rslt2 and !$rslt3 and !$rslt4 and !$rslt5 and !$rslt6 and !$rslt7 and !rslt8 ) 
        {
            $rsp["code"] = 500;
            $rsp["msg"] = $db->str_error("Unable to reset tests users statistics")."(".$sql_req.")";
            return $rsp;
        } else {
            $rsp["msg"] = lang('tests-stats-reseted');
            $rsp["code"] = 200;
        } 
        
        return $rsp;
    }
    
	/*
	Return all statistics for tests
	*/
	function tests_getstats( $loginid, $type, $projectid ) {
		global $db, $CORE, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$rsp["code"] = 200;
		if ( $loginid == -1 ) $loginid = null;
		if ( $projectid == -1 ) $projectid = null;

		if ( $type == SCRIPT ) 
			$rsp["msg"] = get_stats_script($table=$__LWF_DB_PREFIX.'-scripts-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);

		if ( $type == TESTGLOBAL ) 
			$rsp["msg"] = get_stats_tests($table=$__LWF_DB_PREFIX.'-testglobals-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);

		if ( $type == TESTPLAN ) 
			$rsp["msg"] = get_stats_tests($table=$__LWF_DB_PREFIX.'-testplans-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);

		if ( $type == TESTSUITE ) 
			$rsp["msg"] = get_stats_tests($table=$__LWF_DB_PREFIX.'-testsuites-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);

		if ( $type == TESTUNIT ) 
			$rsp["msg"] = get_stats_tests($table=$__LWF_DB_PREFIX.'-testunits-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);
		
        if ( $type == TESTABSTRACT ) 
			$rsp["msg"] = get_stats_tests($table=$__LWF_DB_PREFIX.'-testabstracts-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);

		if ( $type == TESTCASE ) 
			$rsp["msg"] = get_stats_tests($table=$__LWF_DB_PREFIX.'-testcases-stats', $loginid=$loginid, $graph=true, $projectid=$projectid);

		return $rsp;	
	}

    /***************
    Accessors for test environment data 
    ****************/
    
    /*
    Import all variables
    */
    function env_importall( $values ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;
        
		$redirect_page_url = "./index.php?p=".get_pindex('tests')."&s=".get_subpindex( 'tests', 'test-environment' );

        $temp_file = tempnam(sys_get_temp_dir(), uniqid() );
        
        $handle = fopen($temp_file, "w");
        fwrite($handle, $values);
        fclose($handle);

        $handle2 = fopen($temp_file, "r");
        while (($data = fgetcsv($handle2, 1000, ",")) !== FALSE) {
            env_addelement( $name=$data[0], $values=base64_decode($data[1]), $pid=$data[2] );
        }
        
        fclose($handle2);

        $rsp["code"] = 200;
        $rsp["msg"] = lang('ws-env-added-all');
		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
    }
    
	/*
	Export all variables
	*/
	function env_exportall( $projectid ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
        
        $rows = array( array('name', 'value', 'project_id') ) ; 
        
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE project_id='.$projectid.';';
		$rslt = $db->query( $sql_req );
		if ( $rslt ) 
		{
            while ( $cur_p = $db->fetch_assoc($rslt) )
            {
                $tmp = array();
                $tmp[] = $cur_p['name'];
                $tmp[] = base64_encode($cur_p['value']);
                $tmp[] = $cur_p['project_id'];
                
                $rows[] = $tmp;
            }
		}
        
        $fp = fopen('php://output', 'w'); 
        if ($fp) 
        {     
               header('Content-Type: text/csv');
               header('Content-Disposition: attachment; filename="export2.csv"');
               header('Pragma: no-cache');    
               header('Expires: 0');
               //fputcsv($fp, $headers); 
               foreach ($rows as $fields) {
                    fputcsv($fp, $fields);
               }
               fclose($fp);
        die; 
       }
	}

	/*
	Add element on the test environment
	*/
	function env_addelement( $name, $values, $pid ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

        //refused separator ":" in name
        if ( strpos($name, ":") !== false )
        {
			$rsp["code"] = 603;
			$rsp["msg"] = lang('ws-env-bad-name');
			return $rsp;
        }
        
		// check if the name is not already used
		$ret = getenv_elementbyname($name, $pid);
		if ( $ret )
		{
			$rsp["code"] = 603;
			$rsp["msg"] = lang('ws-env-duplicate-1').$name.lang('ws-env-duplicate-2');
			return $rsp;
		}

		// good json ?
		$json_values = json_decode($values);
		if ( $json_values === null)
		{
			$rsp["msg"] = lang('ws-env-bad-value');
			$rsp["code"] = 500;
			return $rsp;
		}
		//else {
		//	$json_values = array_change_key_case($json_values, CASE_UPPER);
		//	$values = json_encode($json_values);
		//}

		// this name is free then create project
		$active = 1;
        if ( $__LWF_CFG['mysql-test-environment-encrypted'] ) {
            $sql_req = 'INSERT INTO `'.$__LWF_DB_PREFIX.'-test-environment` (`name`, `value`, `project_id` ) VALUES(\''.mysql_real_escape_string(strtoupper($name)).'\', AES_ENCRYPT(\''.$values.'\',\''.$__LWF_CFG['mysql-test-environment-password'].'\'), \''.$pid.'\');';
        } else {
            $sql_req = 'INSERT INTO `'.$__LWF_DB_PREFIX.'-test-environment` (`name`, `value`, `project_id` ) VALUES(\''.mysql_real_escape_string(strtoupper($name)).'\', \''.mysql_real_escape_string($values).'\', \''.$pid.'\');';
		}
        $rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to add environment")."(".$sql_req.")";
			return $rsp;
		}  else {
			$XMLRPC->refreshTestEnvironment();

			$rsp["msg"] = lang('ws-env-added');
			$rsp["code"] = 200;
		}

		return $rsp;
	}
	
    /*
	Duplicate element from the test environment
	*/
	function env_duplicateelement( $eid, $pid ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('tests')."&s=".get_subpindex( 'tests', 'test-environment' )."&prj=".$pid;
        
		// check eid
		$project = getenv_elementbyid($eid);
		if ( $project == null || $project == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-env-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}
        
        // get random id
        $uniq = uniqid();
        
        // duplicate the element
        $rsp = env_addelement($name=$project['name']."-COPY#".$uniq, $values=$project['value'], $pid=$project['project_id']);
        
        // change the user message
        if ( $rsp["code"] == 200 ) {
			$rsp["msg"] = lang('ws-env-duplicated');
		}
        
		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	/*
	Delete element from the test environment
	*/
	function env_delelement( $eid, $pid ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		$redirect_page_url = "./index.php?p=".get_pindex('tests')."&s=".get_subpindex( 'tests', 'test-environment' )."&prj=".$pid;

		// check eid
		$project = getenv_elementbyid($eid);
		if ( $project == null || $project == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-env-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}


		// delete element in db
		$sql_req = 'DELETE FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE id=\''.$eid.'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to delete element on test environment")."(".$sql_req.")";
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		} else {
			$XMLRPC->refreshTestEnvironment();

			$rsp["msg"] = lang('ws-env-deleted');
			$rsp["code"] = 200;
		}
		
		

		$rsp["moveto"] = $redirect_page_url;
		return $rsp;
	}

	/*
	Update element on the test environment
	*/
	function env_updateelement( $eid, $name, $values, $pid ) {
		global $db, $CORE, $XMLRPC, $__LWF_CFG, $__LWF_DB_PREFIX;
		$rsp = array();
		$rsp["code"] = 100;
		$rsp["msg"] = lang('ws-trying');
		$rsp["moveto"] = null;

		// check eid
		$project = getenv_elementbyid($eid);
		if ( $project == null || $project == false)
		{
			$rsp["code"] = 404;
			$rsp["msg"] = lang('ws-env-not-found');
			$rsp["moveto"] = $redirect_page_url;
			return $rsp;
		}

		// good json ?
		$json_values = json_decode($values);
		if ( $json_values === null)
		{
			$rsp["msg"] = lang('ws-env-bad-value');
			$rsp["code"] = 500;
			return $rsp;
		}

        if ( $__LWF_CFG['mysql-test-environment-encrypted'] ) {
            $sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-test-environment` SET name=\''.mysql_real_escape_string(strtoupper($name)).'\', value=AES_ENCRYPT(\''.$values.'\',\''.$__LWF_CFG['mysql-test-environment-password'].'\'), project_id='.$pid.' WHERE id=\''.$eid.'\';';
        } else {
            $sql_req = 'UPDATE `'.$__LWF_DB_PREFIX.'-test-environment` SET name=\''.mysql_real_escape_string(strtoupper($name)).'\', value=\''.mysql_real_escape_string($values).'\', project_id='.$pid.' WHERE id=\''.$eid.'\';';
		}
        $rslt = $db->query( $sql_req ) ;
		
		if ( !$rslt ) 
		{
			$rsp["code"] = 500;
			$rsp["msg"] = $db->str_error("Unable to update element")."(".$sql_req.")";
		} else {
			$XMLRPC->refreshTestEnvironment();

			$rsp["code"] = 200;
			$rsp["msg"] = lang('ws-env-updated');
		}

		return $rsp;
	}

	/*
	Return the element according to the identifier passed as argument
	*/
	function getenv_elementbyid($eid)
	{
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE  id=\''.mysql_real_escape_string($eid).'\';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			return null;
		} else {
			if ( $db->num_rows($rslt) == 0 )
			{
				return false;
			} else {
				return $db->fetch_assoc($rslt);
			}
		}
	}

	/*
	Return the element according to the name passed as argument
	*/
	function getenv_elementbyname($name, $pid)
	{
		global $db, $CORE, $__LWF_DB_PREFIX;
		$sql_req = 'SELECT * FROM `'.$__LWF_DB_PREFIX.'-test-environment` WHERE  name=\''.mysql_real_escape_string($name).'\' AND project_id='.$pid.';';
		$rslt = $db->query( $sql_req );
		if ( !$rslt ) 
		{
			return null;
		} else {
			if ( $db->num_rows($rslt) == 0 )
			{
				return false;
			} else {
				return $db->fetch_assoc($rslt);
			}
		}
	}
?>