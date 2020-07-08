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

import sys
import operator
import inspect

try:
    xrange
except NameError:  # support python3
    xrange = range


def describeFunc(obj, method=False):
    """
    Describe the function object passed as argument.
    If this is a method object, the second argument
    will be passed as True

    @param obj:
    @type obj:

    @param method:
    @type method:
    """
    try:
        arginfo = inspect.getargspec(obj)
    except TypeError:
        sys.stderr.write("type error\n")
        return

    args = arginfo[0]

    desc = {}
    desc['name'] = obj.__name__
    if obj.__doc__ is not None:
        desc['desc'] = obj.__doc__

    if args:
        if args[0] == 'self':
            args.pop(0)

        desc['args'] = args

        if arginfo[3]:
            dl = len(arginfo[3])
            al = len(args)
            defargs = args[al - dl:al]
            if sys.version_info < (3,):
                desc['default-args'] = zip(defargs, arginfo[3])
            else:
                desc['default-args'] = list(zip(defargs, arginfo[3]))
            # convert None value to str 'None'
            for i in xrange(len(desc['default-args'])):
                k, v = desc['default-args'][i]
                if v is None:
                    desc['default-args'][i] = (k, str(v))
    else:
        desc['args'] = []

    if arginfo[1]:
        desc['pos-args'] = arginfo[1]
    if arginfo[2]:
        desc['keyword-args'] = arginfo[2]

    if method:
        desc['type'] = 'method'
    else:
        desc['type'] = 'function'
    return desc


def describeClass(obj, functions):
    """
    Describe the class object passed as argument including its methods

    @param obj:
    @type obj:

    @param functions:
    @type functions:
    """
    ret = []
    desc = {'name': obj.__name__, 'functions': ret, 'type': 'class'}
    if obj.__doc__ is not None:
        desc['desc'] = obj.__doc__

    for name in obj.__dict__:
        for f in functions:
            if f == name:
                item = getattr(obj, name)
                if sys.version_info < (3,):
                    if inspect.ismethod(item):
                        ret.append(describeFunc(item, True))
                else:
                    if inspect.isfunction(item):
                        ret.append(describeFunc(item, True))
    ret.sort(key=operator.itemgetter('name'))

    return desc


def describeModule(module, classes, descr='', removeVersion=False):
    """
    Describe the module object passed as argument
    including its classes and functions

    @param module:
    @type module:

    @param classes:
    @type classes:

    @param descr:
    @type descr:
    """

    ret = []
    completeName = module.__name__
    moduleName = completeName.rsplit('.', 1)

    # remove version in complete name
    if removeVersion:
        fullName = completeName.split('.')
        fullModuleName = "%s.%s" % (fullName[0], fullName[2])
    else:
        fullModuleName = module.__name__
    desc = {'name': moduleName[1],
            'realname': fullModuleName,
            'classes': ret,
            'type': 'module',
            'desc': descr}

    for name in dir(module):
        for m in classes:
            n, c = m
            if n == name:
                obj = getattr(module, name)
                if inspect.isclass(obj):
                    ret.append(describeClass(obj, c))
                elif (inspect.ismethod(obj) or inspect.isfunction(obj)):
                    ret.append(describeFunc(obj))

    return desc


def describePackage(package, modules, descr=''):
    """
    Describe the python package object passed as argument
    including its classes and functions

    pkg/
        module1/
        module2/
            submod1
                class1
            submod2
                class2

    @param package:
    @type package:

    @param modules:
    @type modules:

    @param descr:
    @type descr:
    """
    ret = []
    desc = {'name': package.__name__,
            'modules': ret,
            'type': 'package',
            'desc': descr}
    for name in dir(package):
        for m in modules:
            d = ''
            if len(m) == 2:
                n, c = m  # module name, next data to inspect
            else:
                n, c, d = m  # module name, next data to inspect, module description
            if n == name:
                obj = getattr(package, name)
                if inspect.ismodule(obj):
                    ret.append(describeModule(obj, c, d))
                if inspect.isclass(obj):
                    ret.append(describeClass(obj, c))
    return desc
