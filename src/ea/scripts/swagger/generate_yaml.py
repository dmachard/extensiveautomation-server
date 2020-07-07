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

import inspect
import ast
import sys
import os

sys.path.insert(0, '../../../')

from ea.servercontrols import RestAdminFunctions as AdminFunctions
from ea.servercontrols import RestTesterFunctions as TesterFunctions
from ea.servercontrols import RestCommonFunctions as CommonFunctions
from ea.libs import Settings

# initialize settings module to read the settings.ini file
Settings.initialize(path="./")


SWAGGER_EMAIL = "d.machard@gmail.com"


def getYamlDecorators(cls, deco="_to_yaml"):
    """
    find decorators
    """
    target = cls
    decorators = []

    def visit_FunctionDef(node):
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(
                    n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            if name == deco:
                decorators.append(node.name)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    node_iter.visit(ast.parse(inspect.getsource(target)))
    return decorators


def findDecorators(module, deco="_to_yaml"):
    """
    New in v17
    """
    helper = []
    clsmembers = inspect.getmembers(module, inspect.isclass)
    for c, o in clsmembers:
        funcs = getYamlDecorators(cls=o, deco=deco)
        if len(funcs):
            helper.append((c, funcs))
    return helper


# params for public functions
swagger = []
swagger_version = "2.0"
swagger_email = SWAGGER_EMAIL
swagger_licence = "LGPL 2.1"
swagger_info = [
    ("description", "Control your test server with %s API" %
     Settings.get('Server', 'name')),
    ("version", Settings.getVersion()),
    ("title", "Swagger Tester - %s" %
     Settings.get('Server', 'name')),
]
swagger_schemes = [
    "https"
]
swagger_host = '127.0.0.1'
swagger_base_path = "/rest"

swagger_paths = ["paths:"]
swagger_tab = 2

# extract yaml python code in rest server interface
py_tab = 4
py_decorators = findDecorators(module=TesterFunctions)
for (c, fcs) in py_decorators:
    obj = getattr(TesterFunctions, c)
    json_path = obj.__doc__.strip("\n").rstrip("\n ")
    json_path = json_path[py_tab:]
    cur = " " * swagger_tab
    swagger_paths.append("%s%s:" % (cur, json_path))
    for f in fcs:
        func = getattr(obj, f)
        cur += " " * swagger_tab
        swagger_paths.append("%s%s:" % (cur, f))
        if func.__doc__ is not None:
            epydoc = func.__doc__.strip("\n").rstrip("\n ")
            cur += " " * swagger_tab
            for l in epydoc.splitlines():
                swagger_paths.append("%s%s" % (cur, l[py_tab * 2:]))

# find defintions
swagger_defs = []
py_decorators = findDecorators(module=TesterFunctions, deco="_to_yaml_defs")
if len(py_decorators):
    swagger_defs = ["definitions:"]
    for (c, fcs) in py_decorators:
        obj = getattr(TesterFunctions, c)
        for f in fcs:
            func = getattr(obj, f)
            cur = " " * swagger_tab
            swagger_defs.append("%s%s:" % (cur, f))
            if func.__doc__ is not None:
                epydoc = func.__doc__.strip("\n").rstrip("\n ")
                cur += " " * swagger_tab
                for l in epydoc.splitlines():
                    swagger_defs.append("%s%s" % (cur, l[py_tab * 2:]))

swagger_tags = []
py_decorators = findDecorators(module=TesterFunctions, deco="_to_yaml_tags")
if len(py_decorators):
    for (c, fcs) in py_decorators:
        obj = getattr(TesterFunctions, c)
        for f in fcs:
            func = getattr(obj, f)
            if func.__doc__ is not None:
                epydoc = func.__doc__.strip("\n").rstrip("\n ")
                for l in epydoc.splitlines():
                    swagger_tags.append(("%s" % f, l[py_tab * 2:]))

# construct swagger
swagger.append("swagger: '%s'" % swagger_version)
swagger.append("info:")
for (k, v) in swagger_info:
    cur = " " * swagger_tab
    swagger.append("%s%s: %s" % (cur, k, v))
swagger.append("%scontact:" % cur)
swagger.append("%s%semail: %s" % (cur, cur, swagger_email))
swagger.append("%slicense:" % cur)
swagger.append("%s%sname: %s" % (cur, cur, swagger_licence))
swagger.append("host: %s" % swagger_host)
swagger.append("basePath: %s" % swagger_base_path)

if len(swagger_tags):
    swagger.append("tags:")
    for (k, v) in swagger_tags:
        cur = " " * swagger_tab
        swagger.append("%s- name: %s" % (cur, k))
        swagger.append("%s%sdescription: %s" % (cur, cur, v))

if len(swagger_schemes):
    swagger.append("schemes:")
    for (s) in swagger_schemes:
        swagger.append("%s- %s" % (cur, s))

swagger.extend(swagger_paths)
swagger.extend(swagger_defs)

# write the file
yaml_path = "/%s/scripts/swagger/tester_restapi.yaml" % (Settings.getDirExec())
with open(yaml_path, "wt") as f:
    f.write("\n".join(swagger))

##################
##################
# params for admins functions
##################
##################
swagger = []
swagger_version = "2.0"
swagger_email = SWAGGER_EMAIL
swagger_licence = "LGPL 2.1"
swagger_info = [
    ("description", "Control your test server with %s API" %
     Settings.get('Server', 'name')),
    ("version", Settings.getVersion()),
    ("title", "Swagger Admin - %s" %
     Settings.get('Server', 'name')),
]
swagger_schemes = [
    "https"
]
swagger_host = '127.0.0.1'
swagger_base_path = "/rest"

swagger_paths = ["paths:"]
swagger_tab = 2

# extract yaml python code in rest server interface
py_tab = 4
py_decorators = findDecorators(module=AdminFunctions)
for (c, fcs) in py_decorators:
    obj = getattr(AdminFunctions, c)
    json_path = obj.__doc__.strip("\n").rstrip("\n ")
    json_path = json_path[py_tab:]
    cur = " " * swagger_tab
    swagger_paths.append("%s%s:" % (cur, json_path))
    for f in fcs:
        func = getattr(obj, f)
        cur += " " * swagger_tab
        swagger_paths.append("%s%s:" % (cur, f))
        if func.__doc__ is not None:
            epydoc = func.__doc__.strip("\n").rstrip("\n ")
            cur += " " * swagger_tab
            for l in epydoc.splitlines():
                swagger_paths.append("%s%s" % (cur, l[py_tab * 2:]))

# find defintions
swagger_defs = []
py_decorators = findDecorators(module=AdminFunctions, deco="_to_yaml_defs")
if len(py_decorators):
    swagger_defs = ["definitions:"]
    for (c, fcs) in py_decorators:
        obj = getattr(AdminFunctions, c)
        for f in fcs:
            func = getattr(obj, f)
            cur = " " * swagger_tab
            swagger_defs.append("%s%s:" % (cur, f))
            if func.__doc__ is not None:
                epydoc = func.__doc__.strip("\n").rstrip("\n ")
                cur += " " * swagger_tab
                for l in epydoc.splitlines():
                    swagger_defs.append("%s%s" % (cur, l[py_tab * 2:]))

swagger_tags = []
py_decorators = findDecorators(module=AdminFunctions, deco="_to_yaml_tags")
if len(py_decorators):
    for (c, fcs) in py_decorators:
        obj = getattr(AdminFunctions, c)
        for f in fcs:
            func = getattr(obj, f)
            if func.__doc__ is not None:
                epydoc = func.__doc__.strip("\n").rstrip("\n ")
                for l in epydoc.splitlines():
                    swagger_tags.append(("%s" % f, l[py_tab * 2:]))

# construct swagger
swagger.append("swagger: '%s'" % swagger_version)
swagger.append("info:")
for (k, v) in swagger_info:
    cur = " " * swagger_tab
    swagger.append("%s%s: %s" % (cur, k, v))
swagger.append("%scontact:" % cur)
swagger.append("%s%semail: %s" % (cur, cur, swagger_email))
swagger.append("%slicense:" % cur)
swagger.append("%s%sname: %s" % (cur, cur, swagger_licence))
swagger.append("host: %s" % swagger_host)
swagger.append("basePath: %s" % swagger_base_path)

if len(swagger_tags):
    swagger.append("tags:")
    for (k, v) in swagger_tags:
        cur = " " * swagger_tab
        swagger.append("%s- name: %s" % (cur, k))
        swagger.append("%s%sdescription: %s" % (cur, cur, v))

if len(swagger_schemes):
    swagger.append("schemes:")
    for (s) in swagger_schemes:
        swagger.append("%s- %s" % (cur, s))

swagger.extend(swagger_paths)
swagger.extend(swagger_defs)

# write the file
yaml_path = "/%s/scripts/swagger/admin_restapi.yaml" % (Settings.getDirExec())
with open(yaml_path, "wt") as f:
    f.write("\n".join(swagger))

##################
##################
# Common functions
##################
##################
swagger = []
swagger_version = "2.0"
swagger_email = SWAGGER_EMAIL
swagger_licence = "LGPL 2.1"
swagger_info = [
    ("description", "Control your test server with %s API" %
     Settings.get('Server', 'name')),
    ("version", Settings.getVersion()),
    ("title", "Swagger Common - %s" %
     Settings.get('Server', 'name')),
]
swagger_schemes = [
    "https"
]
swagger_host = '127.0.0.1'
swagger_base_path = "/rest"

swagger_paths = ["paths:"]
swagger_tab = 2

# extract yaml python code in rest server interface
py_tab = 4
py_decorators = findDecorators(module=CommonFunctions)
for (c, fcs) in py_decorators:
    obj = getattr(CommonFunctions, c)
    json_path = obj.__doc__.strip("\n").rstrip("\n ")
    json_path = json_path[py_tab:]
    cur = " " * swagger_tab
    swagger_paths.append("%s%s:" % (cur, json_path))
    for f in fcs:
        func = getattr(obj, f)
        cur += " " * swagger_tab
        swagger_paths.append("%s%s:" % (cur, f))
        if func.__doc__ is not None:
            epydoc = func.__doc__.strip("\n").rstrip("\n ")
            cur += " " * swagger_tab
            for l in epydoc.splitlines():
                swagger_paths.append("%s%s" % (cur, l[py_tab * 2:]))

# find defintions
swagger_defs = []
py_decorators = findDecorators(module=CommonFunctions, deco="_to_yaml_defs")
if len(py_decorators):
    swagger_defs = ["definitions:"]
    for (c, fcs) in py_decorators:
        obj = getattr(CommonFunctions, c)
        for f in fcs:
            func = getattr(obj, f)
            cur = " " * swagger_tab
            swagger_defs.append("%s%s:" % (cur, f))
            if func.__doc__ is not None:
                epydoc = func.__doc__.strip("\n").rstrip("\n ")
                cur += " " * swagger_tab
                for l in epydoc.splitlines():
                    swagger_defs.append("%s%s" % (cur, l[py_tab * 2:]))

swagger_tags = []
py_decorators = findDecorators(module=CommonFunctions, deco="_to_yaml_tags")
if len(py_decorators):
    for (c, fcs) in py_decorators:
        obj = getattr(CommonFunctions, c)
        for f in fcs:
            func = getattr(obj, f)
            if func.__doc__ is not None:
                epydoc = func.__doc__.strip("\n").rstrip("\n ")
                for l in epydoc.splitlines():
                    swagger_tags.append(("%s" % f, l[py_tab * 2:]))

# construct swagger
swagger.append("swagger: '%s'" % swagger_version)
swagger.append("info:")
for (k, v) in swagger_info:
    cur = " " * swagger_tab
    swagger.append("%s%s: %s" % (cur, k, v))
swagger.append("%scontact:" % cur)
swagger.append("%s%semail: %s" % (cur, cur, swagger_email))
swagger.append("%slicense:" % cur)
swagger.append("%s%sname: %s" % (cur, cur, swagger_licence))
swagger.append("host: %s" % swagger_host)
swagger.append("basePath: %s" % swagger_base_path)

if len(swagger_tags):
    swagger.append("tags:")
    for (k, v) in swagger_tags:
        cur = " " * swagger_tab
        swagger.append("%s- name: %s" % (cur, k))
        swagger.append("%s%sdescription: %s" % (cur, cur, v))

if len(swagger_schemes):
    swagger.append("schemes:")
    for (s) in swagger_schemes:
        swagger.append("%s- %s" % (cur, s))

swagger.extend(swagger_paths)
swagger.extend(swagger_defs)

# write the file
yaml_path = "/%s/scripts/swagger/common_restapi.yaml" % (Settings.getDirExec())
with open(yaml_path, "wt") as f:
    f.write("\n".join(swagger))

Settings.finalize()

sys.exit(0)
