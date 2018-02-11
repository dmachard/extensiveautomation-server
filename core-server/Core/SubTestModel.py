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

# /!\ WARNING /!\
# Don't replace tab to space on python code generated for test
# the test is not compliant with python recommandation
# /!\ WARNING /!\

import sys

try:
    import TestModel
    import RepoAdapters
    import RepoLibraries
    import Common
except ImportError: # python3 support
    from . import TestModel
    from . import RepoAdapters
    from . import RepoLibraries
    from . import Common
    
# indent = Common.indent

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
def createSubTest(dataTest, descriptions, trPath, defaultLibrary='', defaultAdapter='', isTestUnit=True, 
                    isTestAbstract=False, isTestPlan=False, isTestGlobal=False):
    """
    """

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()

    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()

    srcTest = dataTest['test-definition']
 
    # te construction
    te = []

    # import python libraries
    te.append( TestModel.IMPORT_PY_LIBS )

    te.append( """import re\nimport TestExecutorLib.TestRepositoriesLib as TestRepositories\n""" )
    
    # import static arguments
    te.append( TestModel.getStaticArgs() )

    te.append( """test_result_path = '%s'\n""" % trPath )

    te.append("""
result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 
""")

    # import test executor libraries
    te.append( TestModel.IMPORT_TE_LIBS )

    if isTestPlan or isTestGlobal:
        te.append( """
ParametersHandler = TestProperties.instance()

try:
	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def output(name):
		return ParametersHandler.parameterOut(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setOutput(name, value):
		return ParametersHandler.setParameterOut(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agent(name):
		return ParametersHandler.agent(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
        
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def outputs():
		return ParametersHandler.outputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agents():
		return ParametersHandler.agents(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)

	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")
    else:
        te.append("""
try:
	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions() 
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility

	def description(name):
		return TestProperties.Descriptions().get(name=name)
	
""")
    te.append(TestModel.INPUT_CUSTOM)
    te.append(TestModel.INPUT_CACHE)
    
    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")
        
    te.append("""

	# !! default local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('Default SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! default local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('Default SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )

    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    if isTestUnit or isTestAbstract:
        te.append("""
	# !! test injection
	class TESTCASE(TestCase):
""")
    else:
        te.append("""
	# !! test injection
""")
    if isTestUnit or isTestAbstract:
        te.append(Common.indent(srcTest, nbTab=2))
    else:

        te.append(Common.indent(srcTest, nbTab=1))

    te.append("""	
except Exception as e:
	raise Exception( e )
""")
    return unicode(''.join(te)).encode('utf-8')