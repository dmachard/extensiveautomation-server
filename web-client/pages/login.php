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

		// construct main menu
		$tmp_lwf_h = '<ul class="mainnav">';
		$tmp_lwf_h .= '<li><span class="mainnav_selected" onclick="javascript:nav(\'./index.php\')">'.lang('login').'</span></li>';
		$tmp_lwf_h .=  '</ul>';
		$tmp_lwf_h .= '<div class="main_logo"><img src="./images/main_logo.png" /></div>';

   $tpl_main = str_replace('<!-- lwf_header -->', $tmp_lwf_h, $tpl_main);

    // initialize body
    ob_start();
?>
<div class="signin">
	<br /><br />
    <div class="signinlogo">
      <!--  <ul >
        </li>-->
        <img src="./images/main_logo_extensivetesting.png" />
        
        <!--</li>-->
<?php
	if ( !array_key_exists('server-version', $__LWF_CFG) ) {
		echo '<div id="box-warn-login" style="display:block">'.lang('server error').'</div>';
	} else {
?>
      <!--  <li></li>
        </ul>-->
        <small><b><?php echo $__LWF_CFG['server-version']; ?></b></small>
	</div>
	<br />
	<!--<small><?php echo lang('propulsed by').' '.$__LWF_CFG['server-product-name']; ?></small><br />-->
    <?php
        /*
        AUTH_RET == -1 => Not logged
        AUTH_RET == 0 => Login failed
        AUTH_RET == 1 => Login OK
        AUTH_RET == 2 => Server problem
        */
        if ($AUTH_RET == 0 )
            echo '<br /><div id="box-warn-login" style="display:block">'.lang('login failed').'</div>';
        if ($AUTH_RET == 2 )
            echo '<br /><div id="box-warn-login" style="display:block">'.lang('server error').'</div>';
    ?>
    <br />
        <form method="post" action="index.php" name="login" >
        <input name="form_sent_login" value="1" type="hidden">
        <table>
            <tr id="email-row">
                <td><?php echo lang('login') ?>:</td>
                <td><input name="req_login" id="req_login" tabindex=1 size="18" value="" type="text"></td>
                <td class="button-login" ><input name="login" tabindex=3 value="<?php echo lang('login') ?>" type="submit"></td>
            </tr>
            <tr id="pwd-row">
                <td><?php echo lang('password') ?>:</td>
                <td><input name="req_passwd" id="req_passwd" tabindex=2 size="18" type="password"></td>
            </tr>
            <tr>
                <td></td>
                
            </tr>
        </table>
        </form>
    <br /><br />
</div>
<?php
		if ( $__LWF_CFG['misc-mode-demo'] ) {

			echo '<div class="signin-demo">';
			echo "<b>".lang('login-demo')."</b>";
			echo "<ul>";
			echo "<li>".lang('login-demo-tester').": tester/demo</li>";
			echo "</ul></div>";
		}
}
?>
<?php
    // finalize body
        $tpl_temp = trim(ob_get_contents());
        $tpl_main = str_replace('<!-- lwf_body -->', '<div id="lwf_b">'.$tpl_temp.'</div>', $tpl_main);
        ob_end_clean();

    // set page name
    $tpl_main = str_replace('<!-- lwf_title -->', $__LWF_APP_NAME, $tpl_main);

    exit($tpl_main);
?>
