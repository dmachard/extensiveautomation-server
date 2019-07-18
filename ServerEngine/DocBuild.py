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

import sys

root = sys.argv[1]
var_tmp = sys.argv[2]
sut_pkg_installed = sys.argv[3]
check_syntax_only = sys.argv[4]
sutlib_pkg_installed = sys.argv[5]
check_syntax_sutlib_only = sys.argv[6]

cache_pathfile = '%s/documentations.dat' % var_tmp

sys.path.insert(0, root )

import pickle
import inspect
import ast

import traceback
try:
    import cStringIO
except ImportError: # support python 3
    import io as cStringIO

import DocInspect
from Libs import Settings

def getBackTrace():
    """
    Returns the current backtrace.

    @return:
    @rtype:
    """
    backtrace = cStringIO.StringIO()
    traceback.print_exc(None, backtrace)
    ret = backtrace.getvalue()
    backtrace.close()
    return ret
    
def getPublicDecorator(cls):
    """
    find decorators
    """
    target = cls
    decorators = []
    
    def visit_FunctionDef(node):
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            if name == "doc_public":
                decorators.append(node.name)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    node_iter.visit(ast.parse(inspect.getsource(target)))
    return decorators
    
def findDecorators(module):
    """
    New in v17
    """
    helper = []
    clsmembers = inspect.getmembers(module, inspect.isclass)
    for c, o in clsmembers:
        funcs = getPublicDecorator(cls=o)
        if len(funcs):
            helper.append( (c, funcs) )
    return helper
    
latestsublibRead = ''
def toInspect(help_mod, pkg):
    """
    Inspect module
    """
    global latestsublibRead
    toInspect = []
    for m in help_mod:
        latestsublibRead = m
        try:
            curMod =  getattr(pkg, m)
        except Exception as e:
            DocInspect.print_error( 'module %s doest not exist: %s' % (m, str(e)) )
        else:
            mod_descr =  getattr(curMod, '__DESCRIPTION__')
            try:
                mod_classes =  getattr(curMod, '__HELPER__')
            except Exception as e:
                mod_classes = findDecorators(module=curMod)
                
            toInspect.append( (m, mod_classes, mod_descr) )
    return toInspect

def extractTestExecutor(lib):
    """
    """
    pkg = __import__("TestExecutorLib.%s" % lib)
    descr_pkg =  getattr(pkg, '__DESCRIPTION__')
    lib_obj =  getattr(pkg, lib)
    lib_descr =  getattr(lib_obj, '__DESCRIPTION__')
    classes = findDecorators(lib_obj)
    
    pkgDesc = DocInspect.describePackage( pkg, modules=[ ( lib, classes, lib_descr ) ], descr=descr_pkg )
    return pkgDesc
    
def generateTestExecutorLib():
    """
    Return help for the test executor library
    """
    try:
        pkgDesc = extractTestExecutor(lib="TestExecutorLib")
        pkgDesc['name'] = 'TestLibrary' 
        pkgDesc['modules'][0]['name'] = 'TestExecutor'
    except Exception as e:
        raise Exception("TE_EXE: %s" % e )
        
    try:
        pkgDesc2 = extractTestExecutor(lib="TestOperatorsLib")
        pkgDesc2['modules'][0]['name'] = 'TestOperators'
        pkgDesc['modules'].append( pkgDesc2['modules'][0] )
    except Exception as e:
        raise Exception("TE_OPE: %s" % e )
        
    try:
        pkgDesc3 = extractTestExecutor(lib="TestPropertiesLib")
        pkgDesc3['modules'][0]['name'] = 'TestProperties'
        pkgDesc['modules'].append( pkgDesc3['modules'][0] )
    except Exception as e:
        raise Exception("TE_PRO: %s" % e )
        
    try:
        pkgDesc4 = extractTestExecutor(lib="TestValidatorsLib")
        pkgDesc4['modules'][0]['name'] = 'TestValidators'
        pkgDesc['modules'].append( pkgDesc4['modules'][0] )
    except Exception as e:
        raise Exception("TE_VAL: %s" % e )
        
    try:
        pkgDesc5 = extractTestExecutor(lib="TestTemplatesLib")
        pkgDesc5['modules'][0]['name'] = 'TestTemplates'
        pkgDesc['modules'].append( pkgDesc5['modules'][0] )
    except Exception as e:
        raise Exception("TE_TPL: %s" % e )
        
    try:
        pkgDesc6 = extractTestExecutor(lib="TestManipulatorsLib")
        pkgDesc6['modules'][0]['name'] = 'TestManipulators'
        pkgDesc['modules'].append( pkgDesc6['modules'][0] )
    except Exception as e:
        raise Exception("TE_MAN: %s" % e )
        
    try: 
        pkgDesc7 = extractTestExecutor(lib="TestReportingLib")
        pkgDesc7['modules'][0]['name'] = 'TestReporting'
        pkgDesc['modules'].append( pkgDesc7['modules'][0] )
    except Exception as e:
        raise Exception("TE_REP: %s" % e )
        
    try: 
        pkgDesc8 = extractTestExecutor(lib="TestRepositoriesLib")
        pkgDesc8['modules'][0]['name'] = 'TestRepositories'
        pkgDesc['modules'].append( pkgDesc8['modules'][0] )
    except Exception as e:
        raise Exception("TE_RPO: %s" % e )
        
    try: 
        pkgDesc9 = extractTestExecutor(lib="TestAdapterLib")
        pkgDesc9['modules'][0]['name'] = 'SutAdapter'
        pkgDesc['modules'].append( pkgDesc9['modules'][0] )
    except Exception as e:
        raise Exception("TE_ADP: %s" % e )
        
    try: 
        pkgDesc10 = extractTestExecutor(lib="TestLibraryLib")
        pkgDesc10['modules'][0]['name'] = 'SutLibrary'
        pkgDesc['modules'].append( pkgDesc10['modules'][0] )
    except Exception as e:
        raise Exception("TE_LIB: %s" % e )

    return [ pkgDesc ]

def saveDataToCache( data, file):
    """
    Save data to the cache file
    The cache file is sent to users to construct the documentation
    
    @param data:
    @type data:

    @param file:
    @type file:
    """
    fd = open(file, 'wb')
    fd.write( pickle.dumps(data) )
    fd.close()

if __name__ == "__main__":
    if eval(check_syntax_only): 
        return_code = 0
        try:
            pkg = __import__("Var.SutAdapters")
        except Exception as e:
            return_code = 1
            DocInspect.print_error( 'error to import sut adapters: %s' % str(e) )
        sys.exit(return_code)
        
    elif eval(check_syntax_sutlib_only):    
        return_code = 0
        try:
            pkg = __import__("Var.SutLibraries")
        except Exception as e:
            return_code = 1
            DocInspect.print_error( 'error to import sut libraries: %s' % str(e) )
        sys.exit(return_code)
        
    else:  
        return_code = 0
        # initialize settings 
        try:
            Settings.initialize(path="../")
            if not Settings.cfgFileIsPresent(path="../"):
                raise Exception("config file is missing")
        except Exception as e:
            DocInspect.print_error("Unable to initialize settings: %s" % e)
            return_code = 1
        else:
            ret = []
            # construct testexecutorlib documentations
            try:
                docTestLib = generateTestExecutorLib()
                ret.extend( docTestLib )
            except Exception as e:
                DocInspect.print_error( 'Test Library: %s' % str(e) )
                return_code = 1

            # save to cache
            try:
                if not return_code:
                    saveDataToCache(data=ret, file=cache_pathfile)
            except Exception as e:
                DocInspect.print_error( 'error to save data in the cache: %s' % str(e) )
                return_code = 1
            
        # finalize settings 
        try:
            Settings.finalize()
        except Exception as e:
            DocInspect.print_error("Unable to finalize settings: %s" % e)
            return_code = 1
            
        # exit with result code 
        # 0 = OK
        # 1 = ERROR
        sys.exit(return_code)