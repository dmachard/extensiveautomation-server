#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive testing project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

import sys
sys.path.insert(0, '../' )

import hashlib
from binascii import hexlify
import os

import MySQLdb
from  Libs import Settings

Settings.initialize(path="../../")

prefix_table = Settings.get( 'MySql', 'table-prefix')

def querySQL ( query, db = Settings.get( 'MySql', 'db') ):
    """
    @param query: sql query
    @type query: string
    """
    try:
        conn = MySQLdb.connect ( host = Settings.get( 'MySql', 'ip') ,
                                 user = Settings.get( 'MySql', 'user'),
                                 passwd = Settings.get( 'MySql', 'pwd'),
                                 db = db,
                                 unix_socket=Settings.get( 'MySql', 'sock') )
        #
        cursor = conn.cursor ()
        cursor.execute ( query )
        cursor.close ()
        #
        conn.commit ()
        conn.close ()
        ret = True
    except MySQLdb.Error, e:
        print("[querySQL] %s" % str(e))
        sys.exit(1)

print("Create the database %s" % Settings.get('MySql', 'db'))
querySQL( query = """
CREATE DATABASE `%s` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
""" % Settings.get( 'MySql', 'db') , db = "")

print("Create the table '%s-scripts-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-scripts-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-testglobals-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-testglobals-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `nbts` INT,
  `nbtu` INT,
  `nbtc` INT,
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-testplans-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-testplans-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `nbts` INT,
  `nbtu` INT,
  `nbtc` INT,
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-testsuites-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-testsuites-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `nbtc` INT,
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-testunits-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-testunits-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `nbtc` INT,
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-testabstracts-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-testabstracts-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `nbtc` INT,
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-testcases-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-testcases-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `result` varchar(10) NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-writing-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-writing-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date` datetime NOT NULL,
  `user_id` INT,
  `duration` VARCHAR(20),
  `project_id` INT,
  `is_ts` INT,
  `is_tp` INT,
  `is_tu` INT,
  `is_tg` INT,
  `is_ta` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-users'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-users` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `login` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `administrator` INT,
  `leader` INT,
  `developer` INT,
  `tester` INT,
  `system` INT,
  `email` varchar(200) NOT NULL,
  `lang` varchar(50) NOT NULL,
  `style` varchar(50) NOT NULL,
  `active` INT,
  `default` INT,
  `online` INT,
  `cli` INT,
  `gui` INT,
  `web` INT,
  `notifications` varchar(200) NOT NULL,
  `defaultproject` INT,
  `apikey_id` varchar(200),
  `apikey_secret` varchar(200)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""" % prefix_table)

print("Create the table '%s-users-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-users-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user` varchar(50) NOT NULL,
  `connection` INT,
  `date` datetime NOT NULL,
  `duration` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-agents'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-agents` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `login` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `active` INT,
  `online` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""" % prefix_table)

print("Create the table '%s-agents-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-agents-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `agent-id` varchar(50) NOT NULL,
  `connection` INT,
  `date` datetime NOT NULL,
  `duration` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-probes'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-probes` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `login` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `active` INT,
  `online` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
""" % prefix_table)

print("Create the table '%s-probes-stats'" % prefix_table)
querySQL( query = """
CREATE TABLE IF NOT EXISTS `%s-probes-stats` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `probe-id` varchar(50) NOT NULL,
  `connection` INT,
  `date` datetime NOT NULL,
  `duration` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-tasks-history'" % prefix_table)
querySQL( query = """
CREATE TABLE `%s-tasks-history` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `eventtype` INT not null,
    `eventargs` VARCHAR(50),
    `eventtime` VARCHAR(20),
    `eventname` VARCHAR(200),
    `eventauthor` VARCHAR(50),
    `realruntime` VARCHAR(20),
    `eventduration` VARCHAR(20),
    `eventresult` VARCHAR(20),
    `projectid` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-config'" % prefix_table)
querySQL( query = """
CREATE TABLE `%s-config` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `opt` TEXT,
    `value` TEXT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-projects'" % prefix_table)
querySQL( query = """
CREATE TABLE `%s-projects` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` TEXT,
    `active` INT,
    `description` TEXT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-relations-projects'" % prefix_table)
querySQL( query = """
CREATE TABLE `%s-relations-projects` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT,
    `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

print("Create the table '%s-test-environment'" % prefix_table)
querySQL( query = """
CREATE TABLE `%s-test-environment` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` TEXT,
    `value` TEXT,
    `project_id` INT
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""% prefix_table)

# prepare hash for password
def_pwd = ''
t1 = hashlib.sha1()
t1.update( def_pwd )
pwd_hash = t1.hexdigest()

t2 = hashlib.sha1()
t2.update( "%s%s" % ( Settings.get('Misc', 'salt'), pwd_hash ) )
pwd_sha = t2.hexdigest()

def_pwd_sys = Settings.get('Default', 'user-sys-password')
t1 = hashlib.sha1()
t1.update( def_pwd_sys )
pwd_hash_sys = t1.hexdigest()

t2 = hashlib.sha1()
t2.update( "%s%s" % ( Settings.get('Misc', 'salt'), pwd_hash_sys ) )
pwd_hash_sys = t2.hexdigest()

# prepare apikey secret
k1_secret = hexlify(os.urandom(20))
k2_secret = hexlify(os.urandom(20))
k3_secret = hexlify(os.urandom(20))

# Insert default users
print("Insert default users" )
querySQL( query = """
INSERT INTO `%s-users` (`login`, `password`, `administrator`, `leader`, `developer`, `tester`, `system`, `email`, `lang`, `style`, `active`, `default`, `online`, `cli`, `gui`, `web`, `notifications`, `defaultproject`, `apikey_id`, `apikey_secret`  ) VALUES
('%s', '%s', 0, 0, 0, 0, 1, '%s@localhost', '%s', '%s',  1, 1, 0, 1, 0, 0, 'false;false;false;false;false;false;false;', 1, null, null ),
('%s', '%s', 1, 0, 0, 0, 0, '%s@localhost', '%s', '%s',  1, 1, 0, 1, 1, 1, 'false;false;false;false;false;false;false;', 1, '%s', '%s' ),
('%s', '%s', 0, 1, 0, 0, 0, '%s@localhost',  '%s', '%s', 1, 1, 0, 1, 1, 1, 'false;false;false;false;false;false;false;', 1, '%s', '%s' ),
('%s', '%s', 0, 0, 1, 1, 0, '%s@localhost',  '%s', '%s', 1, 1, 0, 1, 1, 0, 'false;false;false;false;false;false;false;', 1, '%s', '%s' );
""" % ( prefix_table, 
        Settings.get('Default', 'user-sys' ), pwd_hash_sys, Settings.get('Default', 'user-sys' ), 
        Settings.get('Default', 'lang' ), Settings.get('Default', 'style'),
        
        Settings.get('Default', 'user-admin' ), pwd_sha, Settings.get('Default', 'user-admin' ), 
        Settings.get('Default', 'lang' ), Settings.get('Default', 'style'),
        Settings.get('Default', 'user-admin' ), k1_secret,
        
        Settings.get('Default', 'user-monitor' ), pwd_sha, Settings.get('Default', 'user-monitor' ), 
        Settings.get('Default', 'lang' ), Settings.get('Default', 'style'),
        Settings.get('Default', 'user-monitor' ), k2_secret,
        
        Settings.get('Default', 'user-tester' ), pwd_sha, Settings.get('Default', 'user-tester' ), 
        Settings.get('Default', 'lang' ), Settings.get('Default', 'style'),
        Settings.get('Default', 'user-tester' ), k3_secret
    )
)

# Insert default project
print("Insert default project" )
querySQL( query = """
INSERT INTO `%s-projects` (`name`, `active` ) VALUES ('%s', 1 );
""" % ( prefix_table, Settings.get('Default', 'project-common'  ) ) )

# Insert default relation between projet and user
print("Insert default relations projects" )
querySQL( query = """
INSERT INTO `%s-relations-projects` (`user_id`, `project_id` ) VALUES
(1, 1 ),
(2, 1 ),
(3, 1 ),
(4, 1 ),
(5, 1 ),
(6, 1 );
""" % ( prefix_table ) )

# Insert default environment
print("Insert default project variables" )
db_name = Settings.get( 'MySql', 'db')
ip_ext = Settings.get( 'Bind', 'ip-ext')
querySQL( query = """
INSERT INTO `%s-test-environment` (`name`, `value`, `project_id` ) VALUES
('DEBUG', 'false', 1),
('TIMEOUT', '1.0', 1),
('SAMPLE_NODE', '{
    "COMMON": {
        "HOSTNAME": "extensivetesting"
    },
    "INSTANCES": {
        "SSH": {
            "ADMIN": {
                "SSH_DEST_HOST": "%s",
                "SSH_DEST_PORT": 22,
                "SSH_DEST_LOGIN": "root",
                "SSH_DEST_PWD": "",
                "SSH_PRIVATE_KEY": null,
                "SSH_PRIVATE_KEY_PATH": null,
                "SSH_AGENT_SUPPORT": false,
                "SSH_AGENT": {
                    "type": "ssh",
                    "name": "agent.ssh01"
                }
            }
        },
        "HTTP": {
            "REST": {
                "HTTP_DEST_HOST": "%s",
                "HTTP_DEST_PORT": 443,
                "HTTP_DEST_SSL": true,
                "HTTP_HOSTNAME": "www.extensvitesting.org",
                "HTTP_AGENT_SUPPORT": false,
                "HTTP_AGENT": {
                    "type": "socket",
                    "name": "agent.socket01"
                },
                "HTTP_BASE_PATH": "/rest"
            },
            "WEB": {
                "HOST": "%s",
                "LOGIN": "tester",
                "PWD": ""
            }
        },
       "DB": {
           "MYSQL": {
               "DB_HOST": "%s",
               "DB_NAME":   "%s",
               "DB_LOGIN":   "root",
               "DB_PWD":    ""
           },
           "LDAP": {
               "DB_HOST": "%s",
               "DB_PORT": 389,
               "DB_LOGIN":  "cn=ldapadm,dc=extensivetesting,dc=local",
               "DB_PWD":  ""
           }
       }
    }
}', 1),
('SAMPLE_DATASET_AUTH', '{
         "login":         "admin",
         "password":      ""
}', 1),
('SAMPLE_DATASET_PROJECT', '{
         "name":             "auto",
         "name_new":     "auto-updated"
}', 1),
('SAMPLE_DATASET_USER', '{
         "login":             "auto",
         "email":             "hello@world.test",
         "password":          "",

         "password_new":      "auto_new",
         "email_new":         "new@world.test"
}', 1),
('SAMPLE_DATASET_TEST', '{
         "project_name":          "Common",
         "test_path":             "/Snippets/Do/01_Wait.tux",
         "dir_name":              "auto"
}', 1),
('SAMPLE_DATASET_VARIABLE', '{
         "project_name":          "Common",
         "variable_name":         "VAR_AUTO",
         "variable_value":        "1.0"
}', 1),
('SAMPLE_ENVIRONMENT', '{
    "PLATFORM": {
        "CLUSTER": [
            { "NODE": "Common:SAMPLE_NODE" }
        ]
    },
    "DATASET": [
        { "AUTH": "Common:SAMPLE_DATASET_AUTH" },
        { "PROJECT": "Common:SAMPLE_DATASET_PROJECT" },
        { "USER": "Common:SAMPLE_DATASET_USER" },
        { "TEST": "Common:SAMPLE_DATASET_TEST" },
        { "VARIABLE": "Common:SAMPLE_DATASET_VARIABLE" }
    ]
}', 1)""" % ( prefix_table, ip_ext, ip_ext, ip_ext, ip_ext, db_name, ip_ext) )

Settings.finalize()

sys.exit(0)