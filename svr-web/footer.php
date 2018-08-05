<?php
	/*
	---------------------------------------------------------------
	 Copyright (c) 2010-2018 Denis Machard. All rights reserved.

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

	// finalize body
        $tpl_temp = trim(ob_get_contents());
        $tpl_main = str_replace('<!-- lwf_body -->', '<div id="lwf_body">'.$tpl_temp.'</div>', $tpl_main);
        ob_end_clean();

	// set page name
	$tpl_main = str_replace('<!-- lwf_title -->', $__LWF_APP_NAME, $tpl_main);

	exit($tpl_main);
?>
