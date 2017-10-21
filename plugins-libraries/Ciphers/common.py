#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
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

def decodeHex(t, size):
	"""
	Parses a string of hexadecimal characters into a list of numbers according to the size
	Example: BA1076F1AE1EEE28 to [3121641201L, 2921262632L]
	
	@param t: a string of hexadecimal characters.
	@type t: str

	@param size: the number of hexadecimal characters to parse as one number (4bits => size=1)
	@type size: int
	
	@rtype: list
	"""
	if ( len(t) % size ):
		raise Exception("length of hexadecimal string must be a multiple of %s" % len)
	a=[]
	for i in xrange(0, len(t), size):
		a.append( int(t[i:i+size],16) )  
	return a

def decodeBytes(t, size):
	"""
	Parses a string of 8-bit characters into a list of numbers  according to the size
	Example: 1234♦♦♦♦ to [825373492, 67372036]

	@param t: a string of 8-bit characters.
	@type t: str
	
	@param size: number destination size(8bits => 1)
	@type size: int
	
	@rtype: list
	"""
	if ( len(t) % size ):
		raise Exception("length of byte string must be a multiple of %s." % size)
	a=[]
	for i in xrange( 0, len(t), size ):
		w = ord(t[i]) << 24 | ord(t[i+1]) << 16 | ord(t[i+2]) << 8  | ord(t[i+3])
		a.append(w)
	return a


def encodeHex(a, size):
	"""
	Converts a list of numbers into a array of hexadecimal characters.
	Example: [3121641201L, 2921262632L] to ['F', '2', '5', '1', 'C', '8', 'F', '6', '6', 'F', '2', 'F', '0', 'F', '8', '1']

	@param a: an array of 32-bit numbers.
	@type a: list
	
	@param size: integer size in bits
	@type size: int
	
	@rtype: list
	"""
	r = []
	for  i in xrange(len(a)):
		w = a[i]
		
		if size>=32: c7=w>>28&0xf
		if size>=28: c6=w>>24&0xf
		if size>=24: c5=w>>20&0xf
		if size>=20: c4=w>>16&0xf
		if size>=16: c3=w>>12&0xf
		if size>=12: c2=w>>8&0xf
		if size>=8: c1=w>>4&0xf
		if size>=4: c0=w&0xf
		
		if size>=32:
			tmp = 55
			if c7<10: tmp = 48
			r.append( chr(c7+tmp) )
		if size>=28:
			tmp = 55
			if c6<10: tmp = 48
			r.append( chr(c6+tmp) )
		if size>=24:
			tmp = 55
			if c5<10: tmp = 48
			r.append( chr(c5+tmp) )
		if size>=20:
			tmp = 55
			if c4<10: tmp = 48
			r.append( chr(c4+tmp) )
		if size>=16:
			tmp = 55
			if c3<10: tmp = 48
			r.append( chr(c3+tmp) )
		if size>=12:
			tmp = 55
			if c2<10: tmp = 48
			r.append( chr(c2+tmp) )
		if size>=8:
			tmp = 55
			if c1<10: tmp = 48
			r.append( chr(c1+tmp) )
		if size>=4:
			tmp = 55
			if c0<10: tmp = 48
			r.append( chr(c0+tmp) )
	return r
	


def encodeBytes(a):
	"""
	Converts a list of numbers into an array of 8-bit characters.
	Example: [3372355810L, 945969924L] to ['\xc9\x02\x10\xe2', '8b[\x04']

	@param a: an array of 32-bit numbers.
	@type a: list
	
	@rtype: list
	"""
	r = []
	for i in xrange( len(a) ):
		r.append( chr(a[i]>>24&0xff) + chr(a[i]>>16&0xff) + chr(a[i]>>8&0xff) +  chr(a[i]&0xff) )
	return r