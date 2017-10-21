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

	 // test type
	if ( !isset($_GET['tt']) )
		exit( lang('access denied') );
	$test_type = $_GET['tt'];
	if ( !($test_type == 's' ||  $test_type == 't' ||  $test_type == 'h' ) )
		exit( lang('access denied') );

	 // test data
	if ( !isset($_GET['d']) )
		exit( lang('access denied') );
	$test_data = $_GET['d'];
	$data_arr = explode( ',', $test_data);

	// limit  data
	if (sizeof($data_arr) >= 15) {
		exit( lang('access denied') );
	}

	/* pChart library inclusions */
	include(ROOT."include/pChart/class/pData.class.php");
	include(ROOT."include/pChart/class/pDraw.class.php");
	include(ROOT."include/pChart/class/pPie.class.php");
	include(ROOT."include/pChart/class/pImage.class.php");

	/* Create and populate the pData object */
	$MyData = new pData(); 
	$MyData->addPoints( $data_arr,"ScoreA" );

	/* Define the absissa serie */
	$nbtotal = array_sum($data_arr);
	if ($test_type == 's') {
		$percentOk = round( ( 100 * $data_arr[0] ) /  $nbtotal );
		$percentKo = round( ( 100 * $data_arr[1] ) /  $nbtotal );
		$percentOther = round( ( 100 * $data_arr[2] ) /  $nbtotal );
		$MyData->addPoints(array(COMPLETE." "."(".$percentOk."%)",ERROR." "."(".$percentKo."%)",KILLED." "."(".$percentOther."%)"),"Labels");
	}
	if ($test_type == 't') {
		$percentOk = round( ( 100 * $data_arr[0] ) /  $nbtotal );
		$percentKo = round( ( 100 * $data_arr[1] ) /  $nbtotal );
		$percentOther = round( ( 100 * $data_arr[2] ) /  $nbtotal );
		$MyData->addPoints(array(PASS." "."(".$percentOk."%)",FAIL." "."(".$percentKo."%)",UNDEFINED." "."(".$percentOther."%)"),"Labels");
	}
	if ($test_type == 'h') {
		$percentNow = round( ( 100 * $data_arr[0] ) /  $nbtotal );
		$percentAt = round( ( 100 * $data_arr[1] ) /  $nbtotal );
		$percentIn = round( ( 100 * $data_arr[2] ) /  $nbtotal );
		$percentEverySec = round( ( 100 * $data_arr[3] ) /  $nbtotal );
		$percentEveryMin = round( ( 100 * $data_arr[4] ) /  $nbtotal );
		$percentEveryHour = round( ( 100 * $data_arr[5] ) /  $nbtotal );
		$percentHourly = round( ( 100 * $data_arr[6] ) /  $nbtotal );
		$percentDaily = round( ( 100 * $data_arr[7] ) /  $nbtotal );
		$percentWeekly = round( ( 100 * $data_arr[8] ) /  $nbtotal );
		$percentSuccessive = round( ( 100 * $data_arr[9] ) /  $nbtotal );
		$percentUndef = round( ( 100 * $data_arr[10] ) /  $nbtotal );

		$pointsArr  = array();
		$pointsArr[] = NOW." "."(".$percentNow."%)";
		$pointsArr[] = AT." "."(".$percentAt."%)";
		$pointsArr[] = IN." "."(".$percentIn."%)";
		$pointsArr[] = EVERYSECOND." "."(".$percentEverySec."%)";
		$pointsArr[] = EVERYMINUTE." "."(".$percentEveryMin."%)";
		$pointsArr[] = EVERYHOUR." "."(".$percentEveryHour."%)";
		$pointsArr[] = HOURLY." "."(".$percentHourly."%)";
		$pointsArr[] = DAILY." "."(".$percentDaily."%)";
		$pointsArr[] = WEEKLY." "."(".$percentWeekly."%)";
		$pointsArr[] = SUCCESSIVE." "."(".$percentSuccessive."%)";
		$pointsArr[] = RUNUNDEFINED." "."(".$percentUndef."%)";
		$MyData->addPoints($pointsArr,"Labels");
	}
	$MyData->setAbscissa("Labels");

	/* Create the pChart object */
	if ($test_type == 'h') {
		$myPicture = new pImage(550,380,$MyData,TRUE);
	} else {
		$myPicture = new pImage(450,280,$MyData,TRUE);
	}

	/* Set the default font properties */ 
	$myPicture->setFontProperties(array("FontName"=> ROOT."include/pChart/fonts/Forgotte.ttf","FontSize"=>12,"R"=>80,"G"=>80,"B"=>80));

	/* Create the pPie object */ 
	$PieChart = new pPie($myPicture,$MyData);

	/* Enable shadow computing */ 
	$myPicture->setShadow(TRUE,array("X"=>3,"Y"=>3,"R"=>0,"G"=>0,"B"=>0,"Alpha"=>10));

	/* Draw a splitted pie chart */ 
	$PieChart->setSliceColor(0, array("R" => 0, "G" => 128, "B" => 0)); // green
	$PieChart->setSliceColor(1, array("R" => 128, "G" => 0, "B" => 0)); // red
	$PieChart->setSliceColor(2, array("R" => 0, "G" => 0,"B" => 128)); // blue
	$PieChart->setSliceColor(4, array("R" => 0, "G" => 128, "B" => 0)); // green
	$PieChart->setSliceColor(5, array("R" => 0, "G" => 0, "B" => 0)); // red
	$PieChart->setSliceColor(6, array("R" => 0, "G" => 0,"B" => 128)); // blue
	$PieChart->setSliceColor(7, array("R" => 0, "G" => 255,"B" => 255)); // blue
	$PieChart->setSliceColor(8, array("R" => 255, "G" => 255,"B" => 0)); // yellow
	$PieChart->setSliceColor(9, array("R" => 255, "G" => 0,"B" => 255)); // blue
	$PieChart->setSliceColor(10, array("R" => 192, "G" => 192,"B" => 192)); // grey
	$PieChart->setSliceColor(11, array("R" => 255, "G" => 0,"B" => 0)); // blue
	
	$PieChart->draw3DPie(120,90,array( "Radius"=>100,"DataGapAngle"=>10,"DataGapRadius"=>6,"Border"=>TRUE, "WriteValues"=>PIE_VALUE_PERCENTAGE ));

	/* Write the legend box */ 
	$myPicture->setFontProperties(array("FontName"=> ROOT."include/pChart/fonts/calibri.ttf","FontSize"=>10,"R"=>0,"G"=>0,"B"=>0));
	$PieChart->drawPieLegend(90,160,array("Style"=>LEGEND_NOBORDER,"Mode"=>LEGEND_VERTICAL));
	/* Render the picture (choose the best way) */
	$myPicture->stroke(); # Issue 150

?>