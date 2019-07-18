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

import TestExecutorLib
 
__DESCRIPTION__ = """The library enable to create test reporting in realtime."""
__HELPER__ = [
                ('Step', ['__init__', 'id', 'verdict', 'summary', 'expected', 'action']), 
                ('TestCase', ['__init__', 'verdict', 'name', 'id', 'steps', 'parent']), 
                ('TestCases', ['__init__'])
             ]
             
class TestCase(object):
    
    def __init__(self, id, name, root, parent, steps, verdict):
        """
        Testcase descriptor
        """
        self.__id = id
        self.__verdict = verdict
        self.__steps  = steps
        self.__name = name
        self.__parent = parent
        self.__root = root
    def __str__(self):
        """
        """
        return "%s #%s (%s)" % (self.__name, self.__id, self.__verdict)
    
    def verdict(self):
        """
        Return the verdict

        @return: testcase verdict
        @rtype: string 
        """
        return self.__verdict
    
    def name(self):
        """
        Return the name

        @return: testcase name
        @rtype: string 
        """
        return self.__name
    
    def id(self):
        """
        Return ID

        @return: testcase id
        @rtype: integer 
        """
        return self.__id
    
    def steps(self):
        """
        Return all steps
        
        @return: list of steps
        @rtype: list 
        """
        stps = []
        for stp in self.__steps:
            stps.append( Step(id=stp['id'], summary=stp['summary'], 
                                expected=stp['expected'], action=stp["action"], 
                                verdict=stp['verdict']) )
            
        return stps 
    
    def parent(self):
        """
        Return the parent name
        
        @return: parent name
        @rtype: string 
        """
        return self.__parent
        
class Step(object):
    
    def __init__(self, id, summary, expected, action, verdict):
        """
        Step descriptor
        """
        self.__id = id
        self.__verdict = verdict
        self.__summary = summary
        self.__expected = expected
        self.__action = action
        self.__verdict = verdict
    def __str__(self):
        """
        """
        return "Step #%s (%s)" % (self.__id, self.__verdict) 
    
    def id(self):
        """
        Return ID
        
        @return: step id
        @rtype: integer 
        """
        return self.__id
    
    def verdict(self):
        """
        Return the verdict
        
        @return: step verdict
        @rtype: string
        """
        return self.__verdict
    
    def summary(self):
        """
        Return the summary
        
        @return: step summary
        @rtype: string
        """
        return self.__summary
    
    def expected(self):
        """
        Return the expected
        
        @return: step expected
        @rtype: string
        """
        return self.__expected
    
    def action(self):
        """
        Return the action
        
        @return: step action
        @rtype: string
        """
        return self.__action
        
class TestCases(object):
    
    def __init__(self):
        """
        Get all testcases as an iterator.
        Iterate on each testcase to get the verdict.
        """
        self.i = -1
    def __str__(self):
        """
        """
        tcs = TestExecutorLib.getTsMgr().testcases()
        return "TestCases(nb=%s)" % len(tcs)
    
    def __iter__(self):
        """
        """
        return self
    
    def next(self):
        """
        """
        tcs = TestExecutorLib.getTsMgr().testcases()
        self.i += 1
        
        if self.i >=  len(tcs):
            raise StopIteration
        
        tc = tcs[self.i]
        testcase = TestCase(id=tc['id'], name=tc['name'], root=tc['root'], 
                                    parent=tc['parent'], steps=tc["steps"], 
                                    verdict=tc['verdict'])
                                    
        
        return testcase