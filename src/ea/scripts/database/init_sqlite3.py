#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

from common_bdd import querySQL


def create_sqlite3_model():
    print("Initializing new database...")
    print()

    querySQL(query="CREATE TABLE `users` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`login` varchar(50) NOT NULL, \
`password` varchar(200) NOT NULL, \
`administrator` INT, \
`monitor` INT, \
`tester` INT, \
`email` varchar(200) NOT NULL, \
`lang` varchar(50) NOT NULL, \
`style` varchar(50) NOT NULL, \
`active` INT, \
`online` INT, \
`notifications` varchar(200) NOT NULL, \
`defaultproject` INT, \
`apikey_id` varchar(200), \
`apikey_secret` varchar(200) \
);")

    querySQL(query="CREATE TABLE `tasks-history` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`eventtype` INT not null, \
`eventargs` VARCHAR(50), \
`eventtime` VARCHAR(20), \
`eventname` VARCHAR(200), \
`eventauthor` VARCHAR(50), \
`realruntime` VARCHAR(20), \
`eventduration` VARCHAR(20), \
`eventresult` VARCHAR(20), \
`projectid` INT \
) ;")

    querySQL(query="CREATE TABLE `config` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`opt` TEXT, \
`value` TEXT \
);")

    querySQL(query="CREATE TABLE `projects` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`name` TEXT, \
`active` INT, \
`description` TEXT \
);")

    querySQL(query="CREATE TABLE `relations-projects` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`user_id` INT, \
`project_id` INT \
);")

    querySQL(query="CREATE TABLE `test-environment` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`name` TEXT, \
`value` TEXT, \
`project_id` INT \
);")

    querySQL(query="CREATE TABLE `agents` (\
`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
`token` INT, \
`name` varchar(50) NOT NULL, \
`project_id` INT \
);")