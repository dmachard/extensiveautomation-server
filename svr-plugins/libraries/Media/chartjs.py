#!/usr/bin/env python
# -*- coding=utf-8 -*-

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

import TestExecutorLib.TestLibraryLib as TestLibrary
from TestExecutorLib.TestExecutorLib import doc_public

__NAME__="""CHARTJS"""

class ChartJS(TestLibrary.Library):
	@doc_public
	def __init__(self, parent, name=None, debug=False, shared=False):
		"""
		Chart.js library
		Online documentation http://www.chartjs.org/docs/

		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none

		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibrary.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.chartId = 0
		
	def body(self, tpl, width=400, height=400, chartTitle="My Chart"):
		"""
		"""
		ret =  [ "<!-- BEGIN_CHART_REPORT -->" ]
		ret.append( "<div>" )
		ret.append( "<canvas id=\"myChart%s_%s\" width=\"%s\" height=\"%s\"></canvas>" % ( self.testcase().getId(), self.chartId, width, height ) )
		
		# begin global config
		ret.append( "<script>")
		ret.append( "Chart.defaults.global.tooltips.enabled = true;" )
		ret.append( "Chart.defaults.global.title.display = true;")
		ret.append( "Chart.defaults.global.legend.position = \"bottom\";")
		ret.append( "Chart.defaults.global.title.text = \"%s\";" % chartTitle)
		ret.append( "</script>" )
		# end of global config
		
		ret.append( tpl )
		ret.append( "</div>" )
		ret.append( "<!-- END_CHART_REPORT -->" )
		return "\n".join(ret)
		
	def chart(self, type, data, options, width=400, height=400, chartTitle="My Chart"):
		"""
		"""
		self.chartId += 1
				
		tpl = [ "<script>" ]
		tpl.append( "\n".join(data) ) 
		tpl.append( "\n".join(options) ) 
		tpl.append( "var ctx = document.getElementById(\"myChart%s_%s\");" % (self.testcase().getId(), self.chartId) )
		tpl.append( "var myChart = new Chart(ctx, {" )
		tpl.append( "type: '%s'," % type)
		tpl.append( "data: data,")
		tpl.append( "options: options")
		tpl.append( "});")
		tpl.append( "</script>")
		
		return self.body(tpl="\n".join(tpl), width=width, height=height, chartTitle=chartTitle)
	
	def options(self):
		"""
		"""
		tpl_opts = ["var options = {"]
		tpl_opts.append( "responsive: false,")
		tpl_opts.append( "scales: { yAxes: [{ ticks: { beginAtZero:true } }]  },")
		tpl_opts.append( "}")
		return tpl_opts
	@doc_public
	def barChart(self, labelsAxes=[], datas=[],  legendDatas=[], backgroundColors=[], 
													borderColors=[], horizontalBar=False, chartTitle="My Chart", width=400, height=400):
		"""
		Create a bar(s) chart
		
		@param labelsAxes:  labels name on Y axe
		@type labelsAxes: list
		
		@param datas:  list of datas
		@type datas: list
		
		@param legendDatas:  legend for datas
		@type legendDatas: list
		
		@param backgroundColors:  background colors
		@type backgroundColors: list
		
		@param borderColors:  border colors
		@type borderColors: list

		@param horizontalBar: horizontal bar (default=False)
		@type horizontalBar: boolean
		
		@param chartTitle:  title chart (default=My Chart)
		@type chartTitle: string
		
		@param width:  chart width (default=400px)
		@type width: integer
		
		@param height:  chart height (default=400px)
		@type height: integer
		
		@return: chart js representation
		@rtype: string		
		"""
		tpl_data = ["var data = {"]
		tpl_data.append( "labels: %s," % labelsAxes)
		tpl_data.append( "datasets: [")
		for i in xrange(len(datas)):
			tpl_data.append( "{ "  )
			try:
				tpl_data.append( "label: '%s'," % legendDatas[i] )
			except Exception as e:
				pass
				
			tpl_data.append( "data: %s," % datas[i])
			try:
				tpl_data.append( "backgroundColor: \"%s\"," % backgroundColors[i] )
			except Exception as e:
				pass
				
			try:
				tpl_data.append( " borderColor: \"%s\"," % borderColors[i] )
			except Exception as e:
				pass
			tpl_data.append( "borderWidth: 1")
			tpl_data.append( "},")
		tpl_data.append( "]")
		tpl_data.append( "}")

		if horizontalBar:
			barType = 'horizontalBar'
		else:
			barType = 'bar'
			
		return self.chart(type=barType,  data=tpl_data, options=self.options(), width=width, height=height, chartTitle=chartTitle)
	@doc_public
	def lineChart(self,  labelsAxes=[], legendDatas=[], datas=[], backgroundColors=[], 
															 borderColors=[], fills=[], chartTitle="My Chart", width=400, height=400,  ):
		"""
		Create line(s) chart
		
		@param labelsAxes:  labels name on Y axe
		@type labelsAxes: list
		
		@param datas:  list of datas
		@type datas: list
		
		@param legendDatas:  legend for datas
		@type legendDatas: list
		
		@param backgroundColors:  background colors
		@type backgroundColors: list
		
		@param borderColors:  border colors
		@type borderColors: list

		@param fills: fills under line
		@type fills: list
		
		@param chartTitle:  title chart (default=My Chart)
		@type chartTitle: string
		
		@param width:  chart width (default=400px)
		@type width: integer
		
		@param height:  chart height (default=400px)
		@type height: integer
		
		@return: chart js representation
		@rtype: string		
		"""
		tpl_data = ["var data = {"]
		tpl_data.append( "labels: %s," % labelsAxes)
		tpl_data.append( "datasets: [")
		for i in xrange(len(datas)):
			tpl_data.append( "{ "  )
			try:
				tpl_data.append( "label: '%s'," % legendDatas[i] )
			except Exception as e:
				pass
				
			tpl_data.append( "data: %s," % datas[i])
			try:
				tpl_data.append( "backgroundColor: \"%s\"," % backgroundColors[i] )
			except Exception as e:
				pass
				
			try:
				tpl_data.append( " borderColor: \"%s\"," % borderColors[i] )
			except Exception as e:
				pass
				
			try:
				if fills[i]:
					tpl_data.append( "fill: true")
				else:
					tpl_data.append( "fill: false")
			except Exception as e:
				pass
				
			tpl_data.append( "},")
		tpl_data.append( "]")
		
		tpl_data.append( "}")
		
		return self.chart(type="line",  data=tpl_data, options=self.options(), width=width, height=height, chartTitle=chartTitle)
	@doc_public
	def pieChart(self,  legendData=[], data=[], backgroundColors=[], chartTitle="My Chart", width=400, height=400,  doughnut=False):
		"""
		Create pie chart
		
		@param data:  list of int data
		@type data: list
		
		@param legendData:  legend for datas
		@type legendData: list
		
		@param backgroundColors:  background colors
		@type backgroundColors: list

		@param chartTitle:  title chart (default=My Chart)
		@type chartTitle: string
		
		@param width:  chart width (default=400px)
		@type width: integer
		
		@param height:  chart height (default=400px)
		@type height: integer
		
		@param doughnut: doughnut chart style (default=False)
		@type doughnut: boolean
		
		@return: chart js representation
		@rtype: string		
		"""
		tpl_data = ["var data = {"]
		tpl_data.append( "labels: %s," % legendData)
		tpl_data.append( "datasets: [")
		tpl_data.append( "{ "  )
		tpl_data.append( "data: %s," % data)
		tpl_data.append( "backgroundColor: %s," % backgroundColors )

		tpl_data.append( "},")
		tpl_data.append( "]")
		
		tpl_data.append( "}")
		
		chartStyle = 'pie'
		if doughnut: chartStyle = 'doughnut'
		return self.chart(type=chartStyle,  data=tpl_data, options=self.options(), width=width, height=height, chartTitle=chartTitle)
		