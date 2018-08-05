#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

import wrapt

@wrapt.decorator
def doc_public(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for documentation
    """
    return wrapped(*args, **kwargs)
    
    
__DESCRIPTION__ = """The library provides somes importants operators."""

OP_ANY                  = "any"
OP_EQUALS               = "equals"
OP_NOT_EQUALS           = "not equals"
OP_GREATER_THAN         = "greater than"
OP_LOWER_THAN           = "lower than"
OP_CONTAINS             = "contains"
OP_NOT_CONTAINS         = "not contains"
OP_STARTSWITH           = "startswith"
OP_ENDSWITH             = "endswith"
OP_NOT_STARTSWITH       = "not startswith"
OP_NOT_ENDSWITH         = "not endswith"
OP_REG_EX               = "reg ex"
OP_NOT_REG_EX           = "not reg ex"
# new in v12
OP_GREATER_EQUAL_THAN   = "greater than or equal"
OP_LOWER_EQUAL_THAN     = "lower than or equal"

class TestOperatorsException(Exception): pass

import re

class Any:
    """
    Any
    """
    @doc_public
    def __init__(self):
        """
        This class provides an operator to match anything
        """
        pass
    def __unicode__(self):
        """
        To unicode
        """
        return u"$blany()"

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()
    
    def toStr(self, clr=''):
        """
        To string
        """
        return  u"%sany()" % (clr)

class RegEx:
    """
    RegEx
    """
    @doc_public
    def __init__(self, needle):
        """
        This class provides an operator to match a specific regular expression.
        
        Special characters
            \   escape special characters
            .   matches any character
            ^   matches beginning of string
            $   matches end of string
            [5b-d]  matches any chars '5', 'b', 'c' or 'd'
            [^a-c6]     matches any char except 'a', 'b', 'c' or '6'
            R|S     matches either regex R or regex S
            ()  creates a capture group and indicates precedence

        Quantifiers
            *   0 or more (append ? for non-greedy)
            +   1 or more (append ? for non-greedy)
            ?   0 or 1 (append ? for non-greedy)
            {m}     exactly mm occurrences
            {m, n}  from m to n. m defaults to 0, n to infinity
            {m, n}?     from m to n, as few as possible

        Special sequences
            \A  start of string
            \b  matches empty string at word boundary (between \w and \W)
            \B  matches empty string not at word boundary
            \d  digit
            \D  non-digit
            \s  whitespace: [\t\n\r\f\v]
            \S  non-whitespace
            \w  alphanumeric: [0-9a-zA-Z_]
            \W  non-alphanumeric
            \Z  end of string
            \g<id>  matches a previously defined group
            (?iLmsux)   matches empty string, sets re.X flags
            (?:...)     non-capturing version of regular parentheses
            (?P...)     matches whatever matched previously named group
            (?P=)   digit
            (?#...)     a comment; ignored
            (?=...)     lookahead assertion: matches without consuming
            (?!...)     negative lookahead assertion
            (?<=...)    lookbehind assertion: matches if preceded
            (?<!...)    negative lookbehind assertion
            (?(id)yes|no)   match 'yes' if group 'id' matched, else 'no'

        @param needle: the regular expression to match
        @type needle: string
        """
        self.needle = needle
        try:
            self.needle = unicode(self.needle)
        except UnicodeDecodeError:
            self.needle = self.needle.decode("utf8")
            
    @doc_public       
    def seekIn(self, haystack):
        """
        Seeking to match the needle in the haystack
        If needle match, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle found on the start
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")

        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        m = re.match( re.compile(self.needle, flags=re.S), haystack )
        if m:
            return True
        else:
            return False

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blregex('%s')" % self.needle

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return  u"%sregex('%s')" % (clr,self.needle)

class NotRegEx:
    @doc_public
    def __init__(self, needle):
        """
        This class provides an operator to not match a specific regular expression.

        @param needle: the regular expression
        @type needle: string
        """
        self.needle = needle
        try:
            self.needle = unicode(self.needle)
        except UnicodeDecodeError:
            self.needle = self.needle.decode("utf8")
    @doc_public        
    def seekIn(self, haystack):
        """
        Seeking to not match the needle in the haystack
        If needle not match, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle found on the start
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        m = re.match( re.compile(self.needle, re.S), haystack)
        if not m:
            return True
        else:
            return False

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blnotregex('%s')" % self.needle

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()
        
    def toStr(self, clr=''):
        """
        To string
        """
        return  u"%snotregex('%s')" % (clr,self.needle)

class Startswith:
    @doc_public
    def __init__(self, needle):
        """
        This class provides an operator to check if a string starts with the characters passed as argument.

        @param needle: the string to search
        @type needle: string
        """
        self.needle = needle
        try:
            self.needle = unicode(self.needle)
        except UnicodeDecodeError:
            self.needle = self.needle.decode("utf8")
    @doc_public       
    def seekIn(self, haystack):
        """
        Seeking needle in the haystack
        If needle is found, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle found on the start
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        if haystack.startswith( self.needle ):
            return True
        else:
            return False

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blstartswith('%s')" % self.needle

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return  u"%sstartswith('%s')" % (clr,self.needle)

class NotStartswith:
    @doc_public
    def __init__(self, needle):
        """
        This class provides an operator to check if a string not starts with the characters passed as argument.

        @param needle: the string to search
        @type needle: string
        """
        self.needle = needle
        try:
            self.needle = unicode(self.needle)
        except UnicodeDecodeError:
            self.needle = self.needle.decode("utf8")
    @doc_public        
    def seekIn(self, haystack):
        """
        Seeking needle in the haystack
        If needle is not found, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle not found on the start
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        if not haystack.startswith( self.needle ):
            return True
        else:
            return False

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blnotstartswith('%s')" % self.needle

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%snotstartswith('%s')" % (clr,self.needle)

class Endswith:
    @doc_public
    def __init__(self, needle):
        """
        This class provides an operator to check if a string ends with the characters passed as argument.

        @param needle: the string to search
        @type needle: string
        """
        self.needle = needle
        try:
            self.needle = unicode(self.needle)
        except UnicodeDecodeError:
            self.needle = self.needle.decode("utf8")
    @doc_public        
    def seekIn(self, haystack):
        """
        Seeking needle in the haystack
        If needle is found, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle found on the end
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        if haystack.endswith( self.needle ):
            return True
        else:
            return False

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blendswith('%s')" % self.needle

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%sendswith('%s')" % (clr,self.needle)

class NotEndswith:
    @doc_public
    def __init__(self, needle):
        """
        This class provides an operator to check if a string not ends with the characters passed as argument.

        @param needle: the string to search
        @type needle: string
        """
        self.needle = needle
        try:
            self.needle = unicode(self.needle)
        except UnicodeDecodeError:
            self.needle = self.needle.decode("utf8")
    @doc_public        
    def seekIn(self, haystack):
        """
        Seeking needle in the haystack
        If needle is not found, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle not found on the end
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        if not haystack.endswith( self.needle ):
            return True
        else:
            return False

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blnotendswith('%s')" % self.needle

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%snotendswith('%s')" % (clr,self.needle)

class Contains:
    @doc_public
    def __init__(self, needle, AND=True, OR=False):
        """
        This class provides an operator to check if a string contains the characters passed as argument.

        @param needle: the string(s) to search
        @type needle: string or list

        @param AND: and condition (default=True)
        @type AND: boolean

        @param OR: or condition (default=False)
        @type OR: boolean
        """
        self.needle = needle
        if not isinstance(self.needle, list):
            try:
                self.needle = unicode(self.needle)
            except UnicodeDecodeError:
                self.needle = self.needle.decode("utf8")
            
        self.AND = AND
        self.OR = OR
    @doc_public
    def seekIn(self, haystack):
        """
        Seeking needle in the haystack
        If needle is found, returns True. 

        @param haystack: the string to search in
        @type haystack: string
    
        @return: True if needle found 
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        needles = self.needle
        if not isinstance(self.needle, list):
            needles = [ self.needle ]
        if self.AND:
            found = True
            for needle in needles:
                if not( needle in haystack ):
                    found = False
            return found
        elif self.OR:
            found = False
            for needle in needles:
                if needle in haystack:
                    found = True
            return found
        else:
            raise TestOperatorsException("ERR_OP_001: No condition defined")

    def __unicode__(self):
        """
        To unicode
        """
        if isinstance( self.needle, list):
            return u"$blcontains('%s', AND=%s, OR=%s)" % (self.needle,self.AND,self.OR)
        else:
            return u"$blcontains('%s')" % (self.needle)

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        if isinstance( self.needle, list):
            return u"%scontains('%s', AND=%s, OR=%s)" % (clr,self.needle,self.AND,self.OR)
        else:
            return u"%scontains('%s')" % (clr,self.needle)

class NotContains:
    @doc_public
    def __init__(self, needle, AND=True, OR=False):
        """
        This class provides an operator to check if a string not constains the characters passed as argument.

        @param needle: the string(s) to search
        @type needle: string or list

        @param AND: and condition (default=True)
        @type AND: boolean

        @param OR: or condition (default=False)
        @type OR: boolean
        """
        self.needle = needle
        if not isinstance(self.needle, list):
            try:
                self.needle = unicode(self.needle)
            except UnicodeDecodeError:
                self.needle = self.needle.decode("utf8")
            
        self.AND = AND
        self.OR = OR
    @doc_public
    def seekIn(self, haystack):
        """
        Seeking needle in the haystack
        If needle is not found, returns True. 

        @param haystack: the string to search in
        @type haystack: string

        @return: True if needle not found 
        @rtype: boolean
        """
        if haystack is None: raise TestOperatorsException("ERR_OP_011: string expected not none")
        
        try:
            haystack = unicode(haystack)
        except UnicodeDecodeError:
            haystack = haystack.decode("utf8")
            
        needles = self.needle
        if not isinstance(self.needle, list):
            needles = [ self.needle ]
        if self.AND:
            found = True
            for needle in needles:
                if not( needle in haystack ):
                    found = False
            return not found
        elif self.OR:
            found = False
            for needle in needles:
                if needle in haystack :
                    found = True
            return not found
        else:
            raise TestOperatorsException("ERR_OP_002: No condition defined")

    def __unicode__(self):
        """
        To unicode
        """
        if isinstance( self.needle, list):
            return u"$blnotcontains('%s', AND=%s, OR=%s)" % (self.needle,self.AND,self.OR)
        else:
            return u"$blnotcontains('%s')" % (self.needle)

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        if isinstance( self.needle, list):
            return u"%snotcontains('%s', AND=%s, OR=%s)" % (clr,self.needle,self.AND,self.OR)
        else:
            return u"%snotcontains('%s')" % (clr,self.needle)

class GreaterThan:
    @doc_public
    def __init__(self, x, equal=False):
        """
        This class provides an operator to check if an integer is greater than the value passed as argument.

        @param x: integer to compare
        @type x: float or integer

        @param equal: greater or equal than (default=False)
        @type equal: boolean
        """
        self.equal = equal
        try:
            self.x = float(x)
        except Exception as e:
            raise TestOperatorsException("ERR_OP_003: integer expected on init - %s" % e)
    @doc_public
    def comp(self, y):
        """
        Compare y with x
        If y is greater than x, returns True

        @param y: integer to compare
        @type y: float or integer

        @return: True if greater 
        @rtype: boolean
        """
        try:
            if self.equal:
                if float(y) == self.x :    
                    return True

            if float(y) > self.x :    
                return True
            else:
                return False
        except Exception as e:
            raise TestOperatorsException("ERR_OP_004: integer expected: %s" % e)

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blgreaterthan(%s)" % self.x

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%sgreaterthan(%s)" % (clr,self.x)

class NotGreaterThan:
    @doc_public
    def __init__(self, x):
        """
        This class provides an operator to check if an integer is not greater than the value passed as argument.

        @param x: integer to compare
        @type x: float or integer
        """
        try:
            self.x = float(x)
        except Exception as e:
            raise TestOperatorsException("ERR_OP_007: integer expected on init - %s" % e)
    @doc_public
    def comp(self, y):
        """
        Compare y with x
        If y is not greater than x, returns True

        @param y: integer to compare
        @type y: float or integer

        @return: True if greater 
        @rtype: boolean
        """
        try:
            if float(y) > self.x :    
                return False
            else:
                return True
        except Exception as e:
            raise TestOperatorsException("ERR_OP_008: integer expected: %s" % e)

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blnotgreaterthan(%s)" % self.x

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%snotgreaterthan(%s)" % (clr,self.x)

class LowerThan:
    @doc_public
    def __init__(self, x, equal=False):
        """
        This class provides an operator to check if an integer is lower than the value passed as argument.

        @param x: integer to compare
        @type x: float or integer

        @param equal: greater or equal than (default=False)
        @type equal: boolean
        """
        self.equal = equal
        try:
            self.x = float(x)
        except Exception as e:
            raise TestOperatorsException("ERR_OP_005: integer expected on init - %s" % e)
    @doc_public
    def comp(self, y):
        """
        Compare y with x
        If y is lower than x, returns True

        @param y: integer to compare
        @type y: float or integer

        @return: True if lower 
        @rtype: boolean
        """
        try:
            if self.equal:
                if float(y) == self.x :    
                    return True

            if float(y) < self.x :    
                return True
            else:
                return False
        except Exception as e:
            raise TestOperatorsException("ERR_OP_006: integer expected %s" % e)

    def __unicode__(self):
        """
        To unicode
        """
        return u"$bllowerthan(%s)" % self.x

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%slowerthan(%s)" % (clr, self.x)

class NotLowerThan:
    @doc_public
    def __init__(self, x):
        """
        This class provides an operator to check if an integer is not lower than the value passed as argument.

        @param x: integer to compare
        @type x: float or integer
        """
        try:
            self.x = float(x)
        except Exception as e:
            raise TestOperatorsException("ERR_OP_009: integer expected on init - %s" % e)
    @doc_public
    def comp(self, y):
        """
        Compare y with x
        If y is not lower than x, returns True

        @param y: integer to compare
        @type y: float or integer

        @return: True if lower 
        @rtype: boolean
        """
        try:
            if float(y) < self.x :    
                return False
            else:
                return True
        except Exception as e:
            raise TestOperatorsException("ERR_OP_010: integer expected %s" % e)

    def __unicode__(self):
        """
        To unicode
        """
        return u"$blnotlowerthan(%s)" % self.x

    def __str__(self):
        """
        To str
        """
        return self.__unicode__()

    def toStr(self, clr=''):
        """
        To string
        """
        return u"%snotlowerthan(%s)" % (clr, self.x)