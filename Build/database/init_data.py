#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
# This file is part of the extensive automation project
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

from common_bdd import querySQL

import hashlib
from binascii import hexlify
import os

import sys
sys.path.insert(0, '../../' )

from  Libs import Settings
Settings.initialize(path="../../")

def add_users():
    """
    """
    # prepare hash for password
    def_pwd = 'password'
    t1 = hashlib.sha1()
    t1.update( def_pwd )
    pwd_hash = t1.hexdigest()

    t2 = hashlib.sha1()
    t2.update( "%s%s" % ( Settings.get('Misc', 'salt'), pwd_hash ) )
    pwd_sha = t2.hexdigest()
    
    # prepare apikey secret
    k1_secret = hexlify(os.urandom(20))
    k2_secret = hexlify(os.urandom(20))
    k3_secret = hexlify(os.urandom(20))

    # Insert default users
    querySQL( query = """
    INSERT INTO `users` (`login`, `password`, `administrator`, `leader`, `developer`, `tester`, `system`, `email`, `lang`, `style`, `active`, `default`, `online`, `cli`, `gui`, `web`, `notifications`, `defaultproject`, `apikey_id`, `apikey_secret`  ) VALUES
    ('admin', '%s', 1, 0, 0, 0, 0, 'admin@localhost', 'en', 'default',  1, 1, 0, 1, 1, 1, 'false;false;false;false;false;false;false;', 1, 'admin', '%s' ),
    ('monitor', '%s', 0, 1, 0, 0, 0, 'monitor@localhost',  'en', 'default', 1, 1, 0, 1, 1, 1, 'false;false;false;false;false;false;false;', 1, 'monitor', '%s' ),
    ('tester', '%s', 0, 0, 1, 1, 0, 'tester@localhost',  'en', 'default', 1, 1, 0, 1, 1, 0, 'false;false;false;false;false;false;false;', 1, 'tester', '%s' );
    """ % ( 
            pwd_sha, k1_secret,
            pwd_sha, k2_secret,
            pwd_sha, k3_secret
        )
    )

def add_projects():
    """
    """
    querySQL( query = """
    INSERT INTO `projects` (`name`, `active` ) VALUES ('Common', 1 );
    """ )

    # Insert default relation between projet and user
    querySQL( query = """
    INSERT INTO `relations-projects` (`user_id`, `project_id` ) VALUES
    (1, 1 ),
    (2, 1 ),
    (3, 1 );
    """ )

def add_globals():
    """
    """
    querySQL( query = """
    INSERT INTO `test-environment` (`name`, `value`, `project_id` ) VALUES
    ('DEBUG', 'false', 1),
    ('TIMEOUT', '1.0', 1),
    ('SAMPLE_NODE', '{
        "SSH_ADMIN": {
            "SSH_AGENT_SUPPORT": false,
            "SSH_DEST_PORT": 22,
            "SSH_AGENT": {
                "type": "ssh",
                "name": "agent.ssh01"
            },
            "SSH_PRIVATE_KEY": null,
            "SSH_PRIVATE_KEY_PATH": null,
            "SSH_DEST_PWD": "<replace_me>",
            "SSH_DEST_LOGIN": "root",
            "SSH_DEST_HOST": "127.0.0.1"
        },
        "REST_API": {
            "HTTP_BASE_PATH": "/rest",
            "HTTP_DEST_PORT": 443,
            "HTTP_AGENT_SUPPORT": false,
            "HTTP_DEST_HOST": "127.0.0.1",
            "HTTP_AGENT": {
                "type": "socket",
                "name": "agent.socket01"
            },
            "HTTP_HOSTNAME": "www.extensiveautomation.org",
            "HTTP_DEST_SSL": true
        }
    }', 1),
    ('SAMPLE_DATA', '{
        "PROJECT": {
            "name": "auto",
            "name_new": "auto-updated"
        },
        "TEST": {
            "dir_name": "auto",
            "project_name": "Common",
            "test_path": "/Snippets/Do/01_Wait.tux"
        },
        "VARIABLE": {
            "variable_value": "1.0",
            "project_name": "Common",
            "variable_name": "VAR_AUTO"
        },
        "USER": {
            "password_new": "auto_new",
            "email_new": "new@world.test",
            "password": "",
            "login": "auto",
            "email": "hello@world.test"
        },
        "AUTH": {
            "login": "admin",
            "password": "password"
        }
    }', 1)""" )
