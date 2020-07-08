#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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

import hashlib
from binascii import hexlify
import os
import json
import sys

from common_bdd import querySQL

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
new_dir_path = os.sep.join(dir_path.split(os.sep)[:-2])

DIR_EXEC = os.path.normpath("%s/" % new_dir_path)
JSON_FILES_DIR = "%s/scripts/database" % (DIR_EXEC)


def read_json_file(filename):
    """
    """
    with open('%s/%s' % (JSON_FILES_DIR, filename), 'r') as f:
        json_text = f.read()
    return json.loads(json_text)


def add_configs():
    """
    """
    # generate a salt
    auth_salt = hexlify(os.urandom(20))
    if sys.version_info > (3,):
        auth_salt = auth_salt.decode("utf8")

    cfg = {"auth-salt": auth_salt}

    # insert them in the config table
    sql_query = "INSERT INTO `config` "
    sql_query += "(`opt`, `value`) "
    sql_query += "VALUES ('auth-salt', '%s');" % auth_salt

    # run the sql query
    querySQL(query=sql_query)

    return cfg


def add_users(auth_salt):
    """
    """
    users = read_json_file(filename="data_users.json")

    for usr in users:
        # prepare hash for password
        t1 = hashlib.sha1()
        t1.update(usr["password"].encode("utf8"))
        pwd_hash = t1.hexdigest()

        # password with salt
        pwd_salt = "%s%s" % (auth_salt, pwd_hash)

        # final hash of the password
        t2 = hashlib.sha1()
        if sys.version_info < (3,):
            t2.update(pwd_salt)
        else:
            t2.update(pwd_salt.encode('utf-8'))
        pwd_sha = t2.hexdigest()

        # prepare apikey secret
        k1_secret = hexlify(os.urandom(20))
        if sys.version_info > (3,):
            k1_secret = k1_secret.decode("utf8")

        # level of the user
        level_admin = 0
        level_monitor = 0
        level_tester = 0
        if usr["level"] == "administrator":
            level_admin = 1
        elif usr["level"] == "monitor":
            level_monitor = 1
        else:
            level_tester = 1

        # prepare the sql query
        sql_query = "INSERT INTO `users` "
        sql_query += "(`login`, `password`, `administrator`, `monitor`,"
        sql_query += "`tester`, `email`, `lang`, `style`, `active`, "
        sql_query += "`online`, `notifications`, `defaultproject`, "
        sql_query += "`apikey_id`, `apikey_secret` ) "
        sql_query += "VALUES ('%s', '%s', %s, " % (
            usr["login"], pwd_sha, level_admin)
        sql_query += "%s, %s, '%s', 'en'," % (
            level_monitor, level_tester, usr["email"])
        sql_query += "'default', 1, 0,  'false;false;false;false;false;false;false;'"
        sql_query += ", %s, '%s', '%s');" % (
            usr["default-project"], usr["login"], k1_secret)

        # execute the query
        user_id = querySQL(query=sql_query)

        # finally add the relations between user and projects
        add_relations(user_id=user_id, user_projects=usr["projects"])


def add_projects():
    """
    """
    projects = read_json_file(filename="data_projects.json")

    for prj in projects:
        # prepare the sql query
        sql_query = "INSERT INTO `projects` "
        sql_query += "(`name`, `active`) "
        sql_query += "VALUES ('%s', %s);" % (prj["name"], prj["id"])

        # run the sql query
        querySQL(query=sql_query)


def add_relations(user_id, user_projects):
    """
    """
    # Insert default relation between projet and user
    for prj_id in user_projects:
        # prepare the sql query
        sql_query = "INSERT INTO `relations-projects` "
        sql_query += "(`user_id`, `project_id`) "
        sql_query += "VALUES (%s, %s);" % (user_id, prj_id)

        # run the sql query
        querySQL(query=sql_query)


def add_globals():
    """
    """
    global_variables = read_json_file(filename="data_globals.json")

    for v in global_variables:
        # prepare the sql query
        sql_query = "INSERT INTO `test-environment` "
        sql_query += "(`name`, `value`, `project_id`) "
        sql_query += "VALUES ('%s', '%s', %s);" % (v["name"],
                                                   json.dumps(v["value"]),
                                                   v["project-id"])

        # run the sql query
        querySQL(query=sql_query)
