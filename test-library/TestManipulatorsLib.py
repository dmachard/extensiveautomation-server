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

import wrapt

@wrapt.decorator
def doc_public(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for documentation
    """
    return wrapped(*args, **kwargs)
    
__DESCRIPTION__ = """The library provides somes importants manipulators."""

class TestManipulatorsException(Exception): pass


class String(object):
    """
    String
    """
    @doc_public
    def __init__(self):
        """
        This class provides an manipulator for string
        """
        pass
    @doc_public
    def toInteger(self, txt):
        """
        Convert string to integer
        
        @param txt: the string to convert
        @type tx: string

        @return: string converted to integer
        @rtype: integer
        """
        try:
            ret = int(txt)
        except Exception as e:
            raise TestManipulatorsException("ERR_MAN_001: unable to convert string to integer %s" % e)
        return ret
    @doc_public    
    def concatenate(self, a, b, separator='' ):
        """
        Concatene b to a

        @param a: the string a
        @type a: string

        @param b: the string b
        @type b: string

        @param separator: string separator (default is empty)
        @type separator: string

        @return: string concatenated
        @rtype: string
        """
        try:
            ret = "%s%s%s" % (a, separator, b)
        except Exception as e:
            raise TestManipulatorsException("ERR_MAN_001: unable to concatenate %s" % e)
        return ret

class Integer(object):
    """
    Integer
    """
    @doc_public
    def __init__(self):
        """
        This class provides an manipulator for integer
        """
        pass
    @doc_public
    def plus(self, a, b):
        """
        Compute a plus b

        @param a: number a
        @type a: integer

        @param b: number b
        @type b: integer

        @return: result of the addition
        @rtype: integer
        """
        try:
            ret = int(a)+int(b)
        except Exception as e:
            raise TestManipulatorsException("ERR_MAN_002: unable to make the addition %s" % e)
        return ret
    @doc_public
    def minus(self, a, b):
        """
        Compute a minus b

        @param a: number a
        @type a: integer

        @param b: number b
        @type b: integer

        @return: result of the subtraction
        @rtype: integer
        """
        try:
            ret = int(a)-int(b)
        except Exception as e:
            raise TestManipulatorsException("ERR_MAN_002: unable to make the substraction %s" % e)
        return ret
    @doc_public
    def multiply(self, a, b):
        """
        Compute a multiply b

        @param a: number a
        @type a: integer

        @param b: number b
        @type b: integer

        @return: result of the multiplication
        @rtype: integer
        """
        try:
            ret = int(a)*int(b)
        except Exception as e:
            raise TestManipulatorsException("ERR_MAN_002: unable to make the multiplication %s" % e)
        return ret 
    @doc_public
    def toString(self, num):
        """
        Convert integer to string
        
        @param num: integer to convert in string
        @type num: integer

        @return: num converted to string
        @rtype: string
        """
        try:
            ret = str(num)
        except Exception as e:
            raise TestManipulatorsException("ERR_MAN_002: unable to convert integer to string %s" % e)
        return ret