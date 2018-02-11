#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard - Jean-Luc Pascal
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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

#import openpyxl # support xlsx files
import xlrd # support xls files for reading
import xlwt # support xls files for writing

import StringIO
import io
from datetime import date,time,datetime

__NAME__="""EXCEL"""

__MAXLINEBUFFER_WRITE__=10

class EXCEL(TestLibraryLib.Library):
	__INTERNAL_ROW_NB_WRITE=0
	@doc_public
	def __init__(self, parent, debug=False, name=None, shared=False):
		"""
		Codec support read/write excel file 97-2003 (xls)
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
	@doc_public
	def readCell(self, content, column, row, worksheet=None):
		"""
		Return cell value according the column and row id
		
		@param content: todo
		@type content: string
		
		@param row: row id
		@type row: integer
		
		@param column: column id
		@type column: integer
		
		@param worksheet: todo
		@type worksheet: string/none
		
		@return: cell content
		@rtype: string/none
		"""
		excelReady = False
		cell_value = None
		
		
		# old file format
		try:
			wb = xlrd.open_workbook( file_contents=content)
			excelReady = True
		except Exception as e:
			self.error( e )

		# opening ok continue
		if excelReady:
			# read sheet
			ws = wb.sheet_by_name(worksheet)
			
			# read cell
			col = ws.col_values( int(column) )
			cell_value = col[ int(row) ]
			
		wb.release_resources()
		return cell_value
	@doc_public
	def readColumn(self, content, column, worksheet=None):
		"""
		Return column value 
		
		@param content: content file
		@type content: string

		@param column: column id
		@type column: integer
		
		@param worksheet: todo
		@type worksheet: string/none
		
		@return: cell content
		@rtype: list
		"""
		excelReady = False
		cell_value = None

		try:
			wb = xlrd.open_workbook( file_contents=content)
			excelReady = True
		except Exception as e:
			self.error( e )

		# opening ok continue
		if excelReady:
			# read sheet
			ws = wb.sheet_by_name(worksheet)
			
			# read cell
			cell_value = ws.col_values( int(column) )
		wb.release_resources()
		return cell_value
	@doc_public
	def readRow(self, content, row, worksheet=None):
		"""
		Return row value
		
		@param content: content file
		@type content: string
		
		@param row: row id
		@type row: integer
		
		@param worksheet: todo
		@type worksheet: string/none
		
		@return: cell content
		@rtype: list
		"""
		excelReady = False
		cell_value = None
		
		# old file format
		try:
			wb = xlrd.open_workbook( file_contents=content)
			excelReady = True
		except Exception as e:
			self.error( e )
	
		# opening ok continue
		if excelReady:
			# read sheet
			ws = wb.sheet_by_name(worksheet)
			
			# read cell
			cell_value = ws.row_values( int(row) )
			
		wb.release_resources()
		
		return cell_value
	@doc_public
	def createWorkbook(self, sheetName):
		"""
		Create a new excellfile object 

		@param sheetName:  name of the sheet to create
		@type content: string

		@return: return Workbook created (one worksheet only)/none
		@rtype: workbook/none
		"""
		# old file format
		try:
			wb = xlwt.Workbook(encoding='utf-8')
			ws=wb.add_sheet(sheetName)
		except Exception as e:
			self.error( e )
			return None
		else:
			self.debug( "worksheet created" )
			return wb
	@doc_public
	def addRaw(self, workbook, rowid, rcontent):
		"""
		Add a new row into the workbook with a row id defined

		@param workbook:  workbook to modify
		@type workbook: workbook

		@param rowid: row id (starting from 0) 
		@type rowid: integer

		@param rcontent: raw content
		@type rcontent: list/none

		@return: Return true/false
		@rtype: boolean
		"""
		sheetReady = False
		formatReady = True
		cell_value = None
		
		# old file format
		try:
			sheet = workbook.get_sheet(0)
		except Exception as e:
			self.error( e )
			return False
		else:
			# opening ok continue
			self.debug( "worksheet found" )
			
			# row number calculation 
			rowid = rowid - self.__INTERNAL_ROW_NB_WRITE 
			self.debug( "row id = %d %d" %(rowid,self.__INTERNAL_ROW_NB_WRITE))
			# formatting of  each element in the row list
			c = 0
			for cell in rcontent :
				try:
					if type(cell) == type(1):
						self.debug( "integer found %d" %cell )
						sheet.row(rowid).set_cell_number(c,cell)
					elif type(cell) == type(1.1):
						self.debug( "float found %f" %cell )
						sheet.row(rowid).set_cell_number(c,cell)
					elif type(cell) == type(True):
						self.debug( "boolean found %s" %cell )
						sheet.row(rowid).set_cell_boolean(c,cell)
					elif type(cell) == type(date(2000,1,1)) or type(cell) == type(time(1,1,1)) or type(cell) == type(datetime.now()) or type(cell) == type(datetime(2000,1,1)) :
						self.debug( "date found %s" %cell )
						sheet.row(rowid).set_cell_date(c,cell)
					elif type(cell) == type("string"):
						self.debug( "string found %s" %cell )
						sheet.row(rowid).set_cell_text(c,cell)
					else: # ici on considère que l'on a une string
						self.debug( "nothing found %s" %cell )
						break
				except Exception as e:
					self.error( e )
					formatReady = False
				# column is incremented
				c= c + 1
		
		# write row 
		if formatReady  :
			# every x lines a flush is done to save memory
			if (rowid + 1) % __MAXLINEBUFFER_WRITE__ == 0 :
				self.debug( " flush file = %d" %rowid)
				sheet.flush_row_data()
				self.debug( " __INTERNAL_ROW_NB_WRITE = %d" %self.__INTERNAL_ROW_NB_WRITE)
			return True
		else:
			return False
	@doc_public
	def saveFile(self, workbook, filepath):
		"""
		Save the current  workbook 

		@param workbook:  workbook to save
		@type workbook: workbook
		
		@param filepath: content file path
		@type filepath: string

		@return: Return true/false
		@rtype: boolean
		"""
		# old file format
		try:
			self.debug( "save file = %s" %filepath)
			wb = workbook.save(filepath)
		except Exception as e:
			self.error( e )
			return False
		else:
			return True