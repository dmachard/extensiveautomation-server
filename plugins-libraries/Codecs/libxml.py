#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
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

import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

from Libs.PyXmlDict import Dict2Xml
from Libs.PyXmlDict import Xml2Dict

import xml.etree.ElementTree as ET
import lxml                                                                     
from lxml import etree 
import StringIO
import copy
import sys

__NAME__="""XML"""


import re

def resolved_xpath(xpath, namespace):
	"""
	hack to support python 2.6
	"""
	result = xpath
	for short_name, url in namespace.items():
		result = re.sub(r'\b' + short_name + ':', '{' + url + '}', result)
	return result

class XML(TestLibraryLib.Library):
	@doc_public
	def __init__(self, parent, debug=False, coding='UTF-8', name=None, shared=False):
		"""
		XML coder-decoder to object
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param coding: expected value in UTF-8, ISO, etc ...
		@type coding: string
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.codecX2D = Xml2Dict.Xml2Dict( )
		self.codecD2X = Dict2Xml.Dict2Xml( coding = coding )
		self.rootXML = None
		self.ns = {}
	@doc_public
	def encode (self, xml_obj):
		"""
		Encode a XML object  to XML raw

		@param xml_obj: xml object
		@type xml_obj: xml object

		@return: xml raw value
		@rtype: string
		"""
		ret = None
		try:		
			ret = self.codecD2X.parseDict( dico = xml_obj )
		except Exception as e:
			self.error('failed to encode object to xml: %s' % str(e) )
		return ret			
	@doc_public
	def decode (self, xml_raw):
		"""
		Decode a XML raw to a XML object
	
		@param xml_raw: xml raw
		@type xml_raw: string

		@return: xml object 
		@rtype: xml object
		"""
		ret = None
		try:
			ret = self.codecX2D.parseXml( xml = xml_raw )
		except Exception as e:
			self.error('failed to decode xml to object: %s' % str(e) )
		return ret	
	@doc_public
	def validator(self, doc=None, xsd=None, docPath=None, xsdPath=None):
		"""
		XML Schema validator with content
		
		@param doc: xml document
		@type doc: string/none
		
		@param xsd: xsd schema
		@type xsd: string/none
		
		@param docPath: xml path for file
		@type docPath: string/none
		
		@param xsdPath: xsd path for file
		@type xsdPath: string/none
		
		@return: return True if the document is OK otherwise False
		@rtype: boolean
		"""
		if doc is None and xsd is None and docPath is None and xsdPath is None:
			raise Exception("no arguments are empty")
			
		valid = False
		self.debug( "xml doc:\n%s"  % doc )
		self.debug( "xsd:\n%s" % xsd )
		self.debug( "xml doc path:\n%s"  % docPath )
		self.debug( "xsd path :\n%s" % xsdPath )
		try:
			# init the schema
			if xsdPath is not None:
				s = open(xsdPath)
			else:
				s = StringIO.StringIO(xsd)
			docXsd = etree.parse(s) 
			try:                                                                        
				schemaObj = etree.XMLSchema(docXsd)                                           
			except lxml.etree.XMLSchemaParseError as e:                                 
				self.error("unable to load schema: %s" % e)
			else:
				
				# init the doc
				if docPath is not None:
					d = open(docPath)
				else:
					d = StringIO.StringIO(doc)
				docXml = etree.parse(d)
				try:                                                                        
					schemaObj.assertValid(docXml)
					valid = True
				except lxml.etree.DocumentInvalid as e:
					self.warning("Invalid Document: %s" % e)
		except Exception as e:
			self.error("generic error on validator: %s" % e)
		return valid
	@doc_public
	def read(self, content, ns={}):
		"""
		Read XML content

		@param content: content to read
		@type content: string
		
		@param ns: namespace
		@type ns: dict
		"""
		try:
			self.rootXML = etree.fromstring(content)
			self.ns = ns
		except Exception as e:
			self.error("unable to read xml content: %s" % e)
	@doc_public
	def getElement(self, xpath, parentElement=None):
		"""
		Using XPath to get element
		
		@param xpath: xpath
		@type xpath: string
		
		@param parentElement: parent element
		@type parentElement: node/none
		
		@return: xml element
		@rtype: object/none
		"""
		if self.rootXML is None: raise Exception('no xml content provided')
		if sys.version_info >= (2,7):
			if parentElement is not None:
				return parentElement.find(xpath, self.ns)
			return self.rootXML.find(xpath, self.ns)
		else:
			if parentElement is not None:
				return parentElement.find(resolved_xpath(xpath, self.ns))
			return self.rootXML.find(resolved_xpath(xpath, self.ns))
	@doc_public
	def copyElement(self, element):
		"""
		Copy XML element
		
		@param element: xml element
		@type element: object
		
		@return: copy of the xml element
		@rtype: object
		"""
		return copy.deepcopy(element)
	@doc_public	
	def getElements(self, xpath, parentElement=None):
		"""
		Using XPath to get all elements
		
		@param xpath: xpath
		@type xpath: string
		
		@param parentElement: parent element
		@type parentElement: node/none
		
		@return: xml element
		@rtype: list/none
		"""
		if self.rootXML is None: raise Exception('no xml content provided')
		if sys.version_info >= (2,7):
			if parentElement is not None:
				return parentElement.findall(xpath, self.ns)
			return self.rootXML.findall(xpath, self.ns)
		else:
			if parentElement is not None:
				return parentElement.findall(resolved_xpath(xpath, self.ns))
			return self.rootXML.findall(resolved_xpath(xpath, self.ns))
	@doc_public
	def addElement(self, xpath, element, parentElement=None):
		"""
		Add XML element according to the xpath
		
		@param xpath: xpath
		@type xpath: string
		
		@param parentElement: parent element
		@type parentElement: node/none
		
		@param element: xml element
		@type element: object
		"""
		if self.rootXML is None: raise Exception('no xml content provided')
		if sys.version_info >= (2,7):
			if parentElement is not None:
				parent = parentElement.find(xpath, self.ns)
			else:
				parent = self.rootXML.find(xpath, self.ns)
		else:
			if parentElement is not None:
				parent = parentElement.find(resolved_xpath(xpath, self.ns))
			else:
				parent = self.rootXML.find(resolved_xpath(xpath, self.ns))
		parent.append(element)
	@doc_public
	def delElement(self, xpath, element, parentElement=None):
		"""
		Delete XML element according to the xpath
		
		@param xpath: xpath
		@type xpath: string
		
		@param parentElement: parent element
		@type parentElement: node/none
		
		@param element: xml element
		@type element: object
		"""
		if self.rootXML is None: raise Exception('no xml content provided')
		if sys.version_info >= (2,7):
			if parentElement is not None:
				parent = parentElement.find(xpath, self.ns)
			else:
				parent = self.rootXML.find(xpath, self.ns)
		else:
			if parentElement is not None:
				parent = parentElement.find(resolved_xpath(xpath, self.ns))
			else:
				parent = self.rootXML.find(resolved_xpath(xpath, self.ns))
		parent.remove(element)
	@doc_public
	def getText(self, xpath, element=None):
		"""
		Using XPath to get text
		
		@param xpath: xpath
		@type xpath: string
		
		@param element: xml element
		@type element: object/none
		
		@return: xml node text
		@rtype: string/none
		"""
		ret = None
		if self.rootXML is None: raise Exception('no xml content provided')
		if element is not None:
			if sys.version_info >= (2,7):
				el = element.find(xpath.strip(), self.ns)
			else:
				el = element.find(resolved_xpath(xpath.strip(), self.ns))
		else:
			if sys.version_info >= (2,7):
				el = self.rootXML.find(xpath.strip(), self.ns)
			else:
				el = self.rootXML.find(resolved_xpath(xpath.strip(), self.ns))
		if el is not None: ret = el.text
		return ret
	@doc_public
	def setText(self, xpath, text, element=None):
		"""
		Using XPath to set text
		
		@param xpath: xpath
		@type xpath: string
		
		@param text: new text
		@type text: string
		
		@param element: xml element
		@type element: object/none
		
		@return: True on success, False otherwise
		@rtype: boolean
		"""
		ret = False
		if self.rootXML is None: raise Exception('no xml content provided')
		if element is not None:
			if sys.version_info >= (2,7):
				el = element.find(xpath.strip(), self.ns)
			else:
				el = element.find(resolved_xpath(xpath.strip(), self.ns))
		else:
			if sys.version_info >= (2,7):
				el = self.rootXML.find(xpath.strip(), self.ns)
			else:
				el = self.rootXML.find(resolved_xpath(xpath.strip(), self.ns))
		if el is not None: 
			el.text = "%s" % text
			ret = True
		return ret
	@doc_public
	def toString(self, encoding='utf-8', pretty=False):
		"""
		Return content to string
		
		@param encoding: xml encoding (default=utf8)
		@type encoding: string
		
		@return: the new xml content
		@rtype: string
		"""
		if self.rootXML is None: raise Exception('no xml content provided')
		return etree.tostring(self.rootXML, pretty_print=pretty, encoding=encoding)
	@doc_public
	def getValue(self, xpath, xml, ns={}):
		"""
		Get text value according to the xpath provided
		
		@param xpath: xml path
		@type xpath: string
	
		@param xml: xml string
		@type xml: string
	
		@param ns: namespace
		@type ns: dict
		
		@return: the value on match, None otherwise
		@rtype: string or none if not found
		"""
		try:
			rootXML = etree.XML(xml)
			findXML = etree.XPath(xpath, namespaces=ns)
			xml_values = [ "%s" % match for match in findXML(rootXML)  ]
			if len(xml_values) >= 1: 
				el = xml_values[0]
				if isinstance(el, etree._Element ):
					return "%s" % el.text
				else:
					return "%s" % el 
		except Exception as e:
			self.error('library - unable to get xml value: %s' % str(e) )
		return None
	@doc_public
	def getValues(self, xpath, xml, ns={}):
		"""
		Get all text values according to the xpath provided
		
		@param xpath: xml path
		@type xpath: string
	
		@param xml: xml string
		@type xml: string
	
		@param ns: namespace
		@type ns: dict
		
		@return: all values on match, empty list otherwise
		@rtype: list
		"""
		try:
			rootXML = etree.XML(xml)
			findXML= etree.XPath(xpath, namespaces=ns)
			retXML =  findXML(rootXML)
			xml_values = []
			for el in retXML:
				if isinstance(el, etree._Element ):
					xml_values.append( "%s" % el.text)
				else:
					xml_values.append( "%s" % el )
			return xml_values
		except Exception as e:
			self.error('library - unable to get all xml values: %s' % str(e) )
		return []
	@doc_public
	def toHuman(self, content):
		"""
		Return XML data to human-readable form

		@param content: content to read
		@type content: string
		
		@return: xml with indentation
		@rtype: string
		"""
		try:
			x = etree.fromstring(content)
			return etree.tostring(x, pretty_print = True)
		except Exception as e:
			self.error("unable to read xml: %s" % e)
	@doc_public
	def isValid(self, xml):
		"""
		Xml is valid ?
		
		@param xml: xml string
		@type xml: string
		
		@return: True on valid, False otherwise
		@rtype: boolean
		"""
		try:
			rootXML = etree.XML(xml)
			del rootXML
			return True
		except Exception as e:
			return False