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

	// Make sure we have built in support for MySQL
	if (!function_exists('mysql_connect'))
		exit('This PHP environment doesn\'t have MySQL support built in.');

	class DBLayer
	{
			var $link_id;
			var $query_result;
			var $saved_queries = array();
			var $num_queries = 0;

			function DBLayer($db_host, $db_username, $db_password, $p_connect)
			{
					if ($p_connect)
							$this->link_id = @mysql_pconnect($db_host, $db_username, $db_password);
					else
							$this->link_id = @mysql_connect($db_host, $db_username, $db_password);

					if (!$this->link_id)
						fatal('DBLayer', 'Unable to connect to MySQL server. MySQL reported: '.mysql_error() );
							
			}
		
			function usedb($db_name)
			{
				if (@mysql_select_db($db_name, $this->link_id))
						return $this->link_id;
				else
						fatal('DBLayer', 'Unable to select database. MySQL reported: '.mysql_error() );

			}

			function query($sql, $unbuffered = false)
			{
					if (strlen($sql) > 140000)
							exit('Insane query. Aborting.');
				   // if (defined('NSF_SHOW_QUERIES'))
				   //         $q_start = get_microtime();
					if ($unbuffered)
							$this->query_result = @mysql_unbuffered_query($sql, $this->link_id);
					else
							$this->query_result = @mysql_query($sql, $this->link_id);
					if ($this->query_result)
					{
						//    if (defined('NSF_SHOW_QUERIES'))
						//           $this->saved_queries[] = array($sql, sprintf('%.5f', get_microtime() - $q_start));

							++$this->num_queries;
							return $this->query_result;
					}
					else
					{
						 //   if (defined('NSF_SHOW_QUERIES'))
						 //           $this->saved_queries[] = array($sql, 0);
							return false;
					}
			}

			function close()
			{
					if ($this->link_id)
					{
							if ($this->query_result)
									@mysql_free_result($this->query_result);

							return @mysql_close($this->link_id);
					}
					else
							return false;
			}

			function fetch_assoc($query_id = 0)
			{
					return ($query_id) ? @mysql_fetch_assoc($query_id) : false;
			}

			function result($query_id = 0, $row = 0)
			{
					return ($query_id) ? @mysql_result($query_id, $row) : false;
			}

			function fetch_row($query_id = 0)
			{
					return ($query_id) ? @mysql_fetch_row($query_id) : false;
			}
		   
			function num_rows($query_id = 0)
			{
					return ($query_id) ? @mysql_num_rows($query_id) : false;
			}
		   
			function get_errno()
			{
				return @mysql_errno($this->link_id);
			}

			function error()
			{
					$result['error_sql'] = @current(@end($this->saved_queries));
					$result['error_no'] = @mysql_errno($this->link_id);
					$result['error_msg'] = @mysql_error($this->link_id);

					return $result;
			}

			function str_error($details = '')
			{
					$result = $details.": (".@mysql_errno($this->link_id).") ".@mysql_error($this->link_id);
					return $result;
			}
	}

?>
