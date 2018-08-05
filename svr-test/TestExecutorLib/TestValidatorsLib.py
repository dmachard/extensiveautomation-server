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
    
import string
import random
import re

__DESCRIPTION__ = """The library provides validation of input text, generic or not."""

class TestValidatorsException(Exception): pass


# rfc5234
# Augmented BNF for Syntax Specifications: ABNF
# B.1.  Core Rules . . . . . . . . . . . . . . . . . . . . . . . . 13
CTL     =   r'[\x00-\x1F\x7F]'                      # controls
CR      =   r'\x0D'                                 # carriage return
DIGIT   =   r'\x30-\x39'                                # 0-9
DQUOTE  =   r'\x22'                                 # " (Double Quote)
VCHAR   =   r'[\x21-\x7E]'                          # visible (printing) characters
OCTET   =   r'[\x00-\xFF]'                          # 8 bits of data
LF      =   r'\x0A'                                 # linefeed
HTAB    =   r'\x09'                                 # horizontal tab
SP      =   r'\x20'
WSP     =   r'(?:' + SP + r'|' + HTAB + r')'                    # white space
CRLF    =   r'(?:' + CR + LF + r')'                                 # Internet standard newline
HEXDIG  =   r'[' + DIGIT + r'ABCDEFabcdef]' 
CHAR    =   r'[\x01-\x7F]'                          # any 7-bit US-ASCII character, excluding NUL
BIT     =   r'[01]'
ALPHA   =   r'\x41-\x5A\x61-\x7A'                   # A-Z / a-z
LWSP    =   r'(?:' + WSP + r'|' + r'('+CRLF + WSP + r')' + r')*'    # linear white space
# Internet Message Format rfc5322, 

# 4.1.  Miscellaneous Obsolete Tokens
OBS_NO_WS_CTL   =   r'[' + r'\x01-\x08'  +  r'\x0B' + r'\x0C'  +  r'\x0E-\x1F'  +  r'\x7F' + r']'
OBS_QP          =   r'(?:' + r"\\" + r'(?:' + '\x00' + r'|' + OBS_NO_WS_CTL + r'|' + LF + r'|' + CR + r')' + r')'

# 3.2.1.  Quoted characters
QUOTED_PAIR     =    r'(?:' + r'(?:' + r"\\" + r'(?:' + VCHAR  + r'|' + WSP + r')' + r')'  + r'|' + OBS_QP + r')'

# 4.1.  Miscellaneous Obsolete Tokens
OBS_CTEXT       =   OBS_NO_WS_CTL
OBS_QTEXT       =   r'\x01-\x08' +  r'\x0B'  + r'\x0C' +  r'\x0E-\x1F'  +  r'\x7F'
OBS_DTEXT       =   r'(?:' + OBS_NO_WS_CTL + r'|' + QUOTED_PAIR + r')'

# 4.2.  Obsolete Folding White Space
OBS_FWS         =   r'(?:' + WSP + r'+' + r'(?:' + CRLF + WSP+r'+' + r')*' + r')'

# 3.2.2.  Folding White Space and Comments
FWS             =   r'(?:' + r'(?:' +r'(?:' + WSP+r'*' + CRLF + r')?' + WSP + r'+' + r')' + r'|' + OBS_FWS + r')'   # Folding white space
CTEXT           =   r'(?:' + r'|' + r'\x21-\x27' + r'|' + r'\x2A-\x5B' + r'|' + r'\x5D-\x7E' + r'|' + OBS_CTEXT + r')'  # Non white space controls  ; The rest of the US-ASCII ;  characters not including "(", ;  ")", or "\"
CCONTENT        =   r'(?:' + CTEXT + r'|' + QUOTED_PAIR + r')'
COMMENT         =   r'(?:' + r'\(' + r'(?:' + FWS +r'?' + CCONTENT + r')*' + FWS+r'?' + r'\)' + r')'
CFWS            =   r'(?:' + r'(?:' + r'(?:' + FWS+r'?'+ COMMENT  + r')+' +  FWS+r'?' + r')' + r'|' + FWS  + r')'

# 3.2.3.  Atom
ATEXT           =   r'[' + ALPHA + DIGIT + r"\!\#\$\%\&\'\*\+\-\/=\?\^\_\`\{\|\}\~]"  # Any character except controls,;  SP, and specials.  ;  Used for atoms
ATOM            =  r'(?:' +  CFWS+r'?' + ATEXT+r'+' +  CFWS+r'?' + r')'
DOT_ATOM_TEXT   =  r'(?:' + ATEXT+r'+' + r'(?:' + r"\." + ATEXT+r'+' + r')*' + r')'
DOT_ATOM        =  r'(?:' + CFWS+r'?' + DOT_ATOM_TEXT + CFWS+r'?' + r')'


# 3.2.4.  Quoted Strings
QTEXT           =   r'[' + r'\x21' + r'\x23-\x5B' + r'\x5D-\x7E' + OBS_QTEXT + r']'
QCONTENT        =   r'(?:' + QTEXT + r'|' + QUOTED_PAIR + r')'
QUOTED_STRING   =   r'(?:' + CFWS+r'?' + DQUOTE + r'(' + FWS+r'?' + QCONTENT +r')*' + FWS+r'?' + DQUOTE + CFWS+r'?' + r')'

# 3.2.5.  Miscellaneous Tokens
WORD            =   r'(?:' + ATOM + r'|' + QUOTED_STRING + r')'

# 4.4. Obsolete Addressing
OBS_LOCAL_PART  =   r'(?:' + WORD + '(?:' + "\." + WORD +')*' + r')'
OBS_DOMAIN      =   r'(?:' + ATOM + '(?:' + "\." + ATOM + ')*' + r')'

# 3.4.1.  Addr-Spec Specification
DTEXT           =   r'[' + r'\x21-\x5A\x5E-\x7E' + r']' 
DOMAIN_LITERAL  =   r'(?:' + CFWS+r'?' + r"\[" + r'(?:' +FWS+r'?' + r'(?:' + DTEXT + r'|' + OBS_DTEXT + r')' + r')*' + FWS+r'?' + r"\]" + CFWS+r'?' + r')'
DOMAIN          =   r'(?:' + DOT_ATOM + r'|' + DOMAIN_LITERAL  + r'|' + OBS_DOMAIN  + r')'
LOCAL_PART      =   r'(?:' +  DOT_ATOM + r'|' + QUOTED_STRING + r'|' + OBS_LOCAL_PART + r')'
ADDR_SPEC       =   r'(?:' + LOCAL_PART + r"@" + DOMAIN + r')'


# rfc5954 Essential Correction for IPv6 ABNF and URI Comparison in RFC 3261
# 4.1. Resolution for Extra Colon in IPv4-Mapped IPv6 Address
D0          = r'[' + DIGIT + r']'
D10         = r'(?:' + r'[' + r'\x31-\x39' + r']' + D0 + r')'
D100        = r'(?:' + r"1" + D0 + r'{2}' + r')'
D200        = r'(?:' + r"2" + r'[' + r'\x30-\x34' + r']' + D0 + r')'
D250        = r'(?:' + r"25" + r'[' + r'\x30-\x35' + r']' + r')'
D8          = r'(?:' + D0 + r'|' + D10 + r'|' + D100 + r'|' + D200 + r'|' + D250 + r')'
IPV4ADDRESS = r'(?:' + D8 + r"\." + D8 + r"\." + D8 + r"\." + D8 + r')'


H16         =   r'(?:' + HEXDIG + r'{1,4}' + r')'
LS32        =   r'(?:' + r'(?:' + H16 + r"\:" + H16 + r')' + r'|' + IPV4ADDRESS + r')'

IPV6_FORM1  =   r'(?:' + r'(?:' + H16 + r":" + r'){6}' + LS32 + r')'
IPV6_FORM2  =   r'(?:' + r"::" + r'(?:' + H16 + r":" + r'){5}' + LS32 + r')'    
IPV6_FORM3  =   r'(?:' + H16 + r'?' + r"::" + r'(?:' + H16 + r":" + r'){4}' + LS32 + r')'
IPV6_FORM4  =   r'(?:' + r'(?:' + r'(?:' + H16 + r":" + r')?' + H16 + r')' + r'?' + r"::" + r'(?:' + H16 + r":" + r'){3}' + LS32 + r')'
IPV6_FORM5  =   r'(?:' + r'(?:' + r'(?:' + H16 + r":" + r'){0,2}' + H16 + r')' + r'?' + r"::" + r'(?:' + H16 + r":" + r'){2}' + LS32 + r')'
IPV6_FORM6  =   r'(?:' + r'(?:' + r'(?:' + H16 + r":" + r'){0,3}' + H16 + r')' + r'?' + r"::" + r'(?:' + H16 + r":" + r')' + LS32 + r')'
IPV6_FORM7  =   r'(?:' + r'(?:' + r'(?:' + H16 + r":" + r'){0,4}' + H16 + r')' + r'?' + r"::" + LS32 + r')'
IPV6_FORM8  =   r'(?:' + r'(?:' + r'(?:' + H16 + r":" + r'){0,5}' + H16 + r')' + r'?' + r"::" + H16 + r')'
IPV6_FORM9  =   r'(?:' + r'(?:' + r'(?:' + H16 + r":" + r'){0,6}' + H16 + r')' + r'?' + r"::" + r')'

IPV6ADDRESS =   r'(?:' + IPV6_FORM1 + r'|' + IPV6_FORM2 + r'|' + IPV6_FORM3 + r'|' + IPV6_FORM4 + r'|' + IPV6_FORM5 + r'|' + IPV6_FORM6 + r'|' + IPV6_FORM7+ r'|' + IPV6_FORM8+ r'|' + IPV6_FORM9    + r')'

OCTET       =   r'(?:' + HEXDIG + r'{2}' + r')'
MACADDRESS  =   r'(?:' + OCTET + r':' + OCTET + r':' + OCTET + r':' + OCTET + r':' + OCTET + r':' + OCTET + r')'

# rfc1738
# ; Miscellaneous definitions
DIGITS          =   r'[' + DIGIT + r']+'
SAFE            =   r"\$\-\_\.\+"
EXTRA           =   r"\!\*\'\(\)\,"
UNRESERVED      =   r'[' + ALPHA + DIGIT + SAFE + EXTRA + r']+'
ESCAPE          =   r'(?:' + r"%" + HEXDIG + HEXDIG + r')'
UCHAR           =   r'(?:' + UNRESERVED + r'|' + ESCAPE + r')'

# 5. BNF for specific URL schemes
# URL schemeparts for ip based protocols:
ALPHADIGIT     = r'[' + ALPHA + DIGIT + r']'
TOPLABEL       = r'(?:' +  r'[' + ALPHA + r']' + r'|' + r'(?:' + r'[' + ALPHA + r']' + r'(' +  ALPHADIGIT + r'|' + r"-" + r')*' + ALPHADIGIT + r')' + r')'
DOMAINLABEL    = r'(?:' + ALPHADIGIT + r'|' + r'(?:' + ALPHADIGIT + r'(?:' + ALPHADIGIT + r'|' +  r"-" + r')*' + ALPHADIGIT + r')' + r')'
HOSTNAME       = r'(?:' + r'(?:' + DOMAINLABEL + "\." + r')*' + TOPLABEL + r')'
PORT           = DIGITS
HOST           = r'(?:' + HOSTNAME + r'|' + IPV4ADDRESS + r'|' + IPV6ADDRESS + r')'
HOSTPORT       = r'(?:' + HOST + r'(?:' + r"\:" + PORT + r')?' + r')'
USER           = r'(?:' + UCHAR + r'|' + r"\;" + r'|' + r"\?" + r'|' + r"\&" + r'|' + r"\=" + r')*'
PASSWORD       = r'(?:' + UCHAR + r'|' + r"\;" + r'|' + r"\?" + r'|' + r"\&" + r'|' + r"\=" + r')*'
LOGIN          = r'(?:' + r'(?:' + USER +  r'(?:' + ":" + PASSWORD + r')?' + "\@" + r')?' + HOSTPORT + r')'

# HTTP
SEARCH          =   r'(?:' +  UCHAR + r'|' + r"\;" + r'|' + r"\:" + r'|' + r"\@" + r'|' + r"\&" + r'|' + r"\=" + r')*'
HSEGMENT        =   r'(?:' + UCHAR + r'|' + r"\;" + r'|' + r"\:" + r'|' + r"\@" + r'|' + r"\&" + r'|' + r"\=" + r')*'
HPATH           =   r'(?:' + HSEGMENT +  r'(?:' + r"\/" + HSEGMENT + r')*' + r')'
HTTPURL         =   r'(?:' + r"http\:\/\/" + HOSTPORT +  r'(?:' + r"\/" + HPATH + r'(?:' + r"\?" + SEARCH + r')?' + r')?' + r')'
HTTPSURL        =   r'(?:' + r"https\:\/\/" + HOSTPORT +  r'(?:' + r"\/" + HPATH + r'(?:' + r"\?" + SEARCH + r')?' + r')?' + r')'


# FTP (see also RFC959)
FTPTYPE        = r'(?:' + r"A" + r'|' + r"I" + r'|' + r"D" + r'|' + r"a" + r'|' + r"i" + r'|' + r"d" + r')'
FSEGMENT       = r'(?:' + UCHAR + r'|' + r"\?" + r'|' + r"\:" + r'|' + r"\@" + r'|' + r"\&" + r'|' + "\=" + r')*'
FPATH          = r'(?:' + FSEGMENT + r'(?:' + r"\/" + FSEGMENT + r')*' + r')'
FTPURL         = r'(?:' + r"ftp\:\/\/" + LOGIN + r'(?:' + r"\/" + FPATH + r'(?:' + r"\;\type\=" + FTPTYPE + r')?' + r')?' + r')'



#rfc3986
#Appendix A. Collected ABNF for URI
PCT_ENCODED         =   r'(?:' + r"\%" + HEXDIG + HEXDIG + r')'
UNRESERVED_RFC3986  =   r'[' + ALPHA + DIGIT + "\-\.\_\~" + r']+'
GEN_DELIMS          =   r'(?:' +  r"\:" + r'|' + r"\/" + r'|' + r"\?" + r'|' + r"\#" + r'|' + r"\[" + r'|' + r"\]" + r'|' + r"\@" + r')'
SUB_DELIMS          =   r'(?:' + r"\!" + r'|' + r"\$" + r'|' + r"\&" + r'|' + r"\'" + r'|' + r"\(" + r'|' + r"\)" + r'|' + r"\*" + r'|' + r"\+" + r'|' + r"\," + r'|' + r"\;" + r'|' + r"\=" + r')'
RESERVED            =   r'(?:' + GEN_DELIMS + r'|' + SUB_DELIMS + r')'
PCHAR               =   r'(?:' + UNRESERVED_RFC3986 + r'|' + PCT_ENCODED + r'|' + SUB_DELIMS + r'|' + r"\:" + r'|' + r"\@" + r')'
QUERY               =   r'(?:' + PCHAR + r'|' + r"\/" + r'|' + r"\?" + r')*'
FRAGMENT            =   r'(?:' + PCHAR + r'|' + r"\/"  + r'|' + r"\?" + r')*'

SEGMENT             =   r'(?:' + PCHAR + r')*'
SEGMENT_NZ          =   r'(?:' + PCHAR + r')+'
SEGMENT_NZ_NC       =   r'(?:' + UNRESERVED_RFC3986 + r'|' + PCT_ENCODED + r'|' + SUB_DELIMS + r'|' + r"\@" + r')+' # non-zero-length segment without any colon ":"

PATH_EMPTY          =   r'(?:' + PCHAR + r'){0}'
PATH_ROOTLESS       =   r'(?:' + SEGMENT_NZ + r'(?:' + r"/" + SEGMENT + r')*' + r')'
PATH_ABSOLUTE       =   r'(?:' + r"/" + r'(?:' + SEGMENT_NZ + r'(?:' + r"/"  + SEGMENT + r')*' + r')?' + r')'
PATH_ABEMPTY        =   r'(?:' + r"/" + SEGMENT + r')*'

USERINFO            =   r'(?:' + UNRESERVED_RFC3986 + r'|' + PCT_ENCODED + r'|' + SUB_DELIMS + r'|' + r"\:" + r')*'
REG_NAME            =   r'(?:' + UNRESERVED_RFC3986 + r'|' + PCT_ENCODED + r'|' + SUB_DELIMS + r')*'
IPVFUTURE           =   r'(?:' + r"v" + HEXDIG + r"+" + r"\." + r'(?:' + UNRESERVED_RFC3986 + r'|' +  SUB_DELIMS + r'|' + r"\:" + r')*' + r')'
IP_LITERAL          =   r'(?:' + r"\[" + r'(?:' + IPV6ADDRESS + r'|' +  IPVFUTURE  + r')' + r"\]" + r')'
HOST_RFC3986        =   r'(?:' + IP_LITERAL + r'|' + IPV4ADDRESS + r'|' + REG_NAME + r')'
PORT_RFC3986        =   r'(?:' + DIGIT + r')*'
AUTHORITY           =   r'(?:' + r'(?:' + USERINFO + r"\@" + r')?' + HOST_RFC3986 + r'(?:' + r"\:" + PORT_RFC3986 + r')?' + r')'

HIER_PART           =   r'(?:' +   r'(?:' + r"//" + AUTHORITY + PATH_ABEMPTY + r')' + r'|' + PATH_ABSOLUTE + r'|' + PATH_ROOTLESS + r'|' +  PATH_EMPTY  + r')'
SCHEME              =   r'(?:' + r'[' + ALPHA + r']' + r'(?:' + r'[' + ALPHA + r']' + r'|' + r'[' + DIGIT + r']' + r'|' + r"\+" + r'|' + r"\-" + r'|' + r"\." + r')*' + r')'
URI                 =   r'(?:' + SCHEME + r":" + HIER_PART + r'(?:' + r"\?" + QUERY + r')?' + r'(?:' + r"\#" + FRAGMENT + r')?' + r')'

class Uri(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for uri according to the rfc3986 which returns True if the uri is valid, and False otherwise.
        """
        pass
    @doc_public
    def isValid(self, uri):
        """
        Check if the format of the uri gived as argument is valid

        @param uri: uri to evaluate
        @type uri: unknown

        @return: valid or not
        @rtype: boolean
        """
        regex = r'^%s$' % URI
        if re.match(regex, uri) is None:
            return False
        else:
            return True

class Email(object):
    @doc_public
    def __init__(self):
        """
        Validator for emails, according to the RFC5322 and RFC3696 which returns True if the email is valid, and False otherwise.
        """
        pass
    @doc_public
    def isValid(self, email):
        """
        Check if the format of the email gived as argument is valid

        @param email: email to evaluate
        @type email: unknown

        @return: True if valid or False otherwise
        @rtype: boolean
        """
        if re.match(r'^%s$' % ADDR_SPEC, email) is None:
            return False
        else:
            # total length of 320 characters
            if len(email) > 320:
                return False
            else:
                local_part, domain_part = email.split('@', 1)
                # That limit is a maximum of 64 characters (octets)   in the "local part"
                if len(local_part) > 64:
                    return False
                else:
                    # a maximum of 255 characters (octets) in the domain part
                    if len(domain_part) > 255:
                        return False
                    else:
                        return True


class Hostname(object):
    @doc_public
    def __init__(self):
        """
        Validator for domain, according to the RFC1738 which returns True if the hostname is valid, and False otherwise.
        """
        pass
    @doc_public
    def isValid(self, hostname):
        """
        Check if the format of the hostname gived as argument is valid

        @param hostname: hostname to evaluate
        @type hostname: unknown

        @return: valid or not
        @rtype: boolean
        """
        if re.match(r'^%s$' % HOSTNAME, hostname) is None:
            return False
        else:
            #  A complete, fully-qualified, domain name must not exceed 255 octets.
            if len(hostname) > 255: 
                return False
            else:
                return True

class FtpUrl(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for ftp url according to the rfc1738 which returns True if the ftp url is valid, and False otherwise.
        """
        pass
    @doc_public
    def isValid(self, url):
        """
        Check if the format of the ftp url gived as argument is valid

        @param ftp: ftp url to evaluate
        @type ftp: unknown

        @return: valid or not
        @rtype: boolean
        """
        regex = r'^%s$' % FTPURL
        if re.match(regex, url) is None:
            return False
        else:
            return True

class HttpUrl(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for http url according to the rfc1738 which returns True if the http url is valid, and False otherwise.
        """
        pass
    @doc_public
    def isValid(self, url, https=False):
        """
        Check if the format of the http url gived as argument is valid

        @param url: http url to evaluate
        @type url: unknown

        @param https: secure http
        @type https: boolean

        @return: valid or not
        @rtype: boolean
        """
        regex = r'^%s$' % HTTPURL
        if https:   regex = r'^%s$' % HTTPSURL
        if re.match(regex, url) is None:
            return False
        else:
            return True


class IPv6Address(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for ip v6 address.
        """
        pass
    @doc_public
    def isValid(self, ip):
        """
        Check if the format of the ip gived as argument is valid

        @param ip: ip to evaluate
        @type ip: unknown

        @return: valid or not
        @rtype: boolean
        """
        if re.match(r'^%s$' % IPV6ADDRESS, ip) is None:
            return False
        else:
            return True

class IPv4Address(object):
    @doc_public
    def __init__(self, separator='.'):
        """
        This class provides a validator for ip v4 address or can be also used to generate random ip or more.

        @param separator: separator (default=.)
        @type separator: string
        """
        self.hln = 4
        self.sep = separator
    @doc_public
    def isValid(self, ip):
        """
        Check if the format of the ip gived as argument is valid

        @param ip: ip to evaluate
        @type ip: unknown

        @return: valid or not
        @rtype: boolean
        """
        IPV4ADDRESS = r'(?:' + D8 + r"\%s" % self.sep + D8 + r"\%s" % self.sep + D8 + r"\%s" % self.sep + D8 + r')'
        if re.match(r'^%s$' % IPV4ADDRESS, ip) is None:
            return False
        else:
            return True
    @doc_public
    def toList(self, ip):
        """
        Return IP address as a list of integer
        0.0.0.0 -> [ 0, 0, 0, 0 ]

        @param ip: ip address
        @type ip: string

        @return: ip address as a list
        @rtype: list
        """
        return [ int(x) for x in ip.split(self.sep) ]
    @doc_public
    def getLocalhost(self):
        """
        Return a localhost IP address

        @return: ip address
        @rtype: string
        """
        ip_local = [ '127', '0', '0', '0' ]
        return self.sep.join(ip_local)
    @doc_public
    def getRandom(self):
        """
        Return a random IP address

        @return: ip address
        @rtype: string
        """
        ip = [ str( random.randrange(0,255+1) ) for x in xrange(self.hln) ]
        return self.sep.join(ip)
    @doc_public
    def getNull(self):
        """
        Return a null IP address (0.0.0.0)

        @return: ip v4 address
        @rtype: string
        """
        null =  [ '0' for x in xrange(self.hln) ]
        return self.sep.join(null)
    @doc_public
    def getBroadcast(self):
        """
        Return a broadcast IP address (255.255.255.255)

        @return: ip address
        @rtype: string
        """
        broadcast =  [ '255' for x in xrange(self.hln) ]
        return self.sep.join(broadcast)

class MacAddress(object):
    @doc_public
    def __init__(self, separator=':'):
        """
        This class provides a validator for mac address or can be also used to generate random mac or more.

        @param separator: separator (default=:)
        @type separator: string
        """
        self.hln = 6  # mac len
        self.sep = separator
    @doc_public
    def toList(self, mac):
        """
        Return MAC address as a list of integer
        00:00:00:00:00:00 -> [ 0, 0, 0, 0, 0, 0 ]

        @param mac: mac address
        @type mac: string

        @return: mac address as a list
        @rtype: list
        """
        return [ int(x, 16) for x in mac.split(self.sep) ]

    @doc_public
    def getRandom(self):
        """
        Return a random mac address

        @return: mac address
        @rtype: string
        """
        mac = [ "%0.2X" % random.randrange(0,255+1) for x in xrange(self.hln) ]
        return self.sep.join(mac)
    @doc_public
    def getNull(self):
        """
        Return a null (00) MAC address

        @return: mac address
        @rtype: string
        """
        broadcast =  [ '00' for x in xrange(self.hln) ]
        return self.sep.join(broadcast)
    @doc_public
    def getBroadcast(self):
        """
        Return a broadcast (FF) MAC address

        @return: mac address
        @rtype: string
        """
        broadcast =  [ 'FF' for x in xrange(self.hln) ]
        return self.sep.join(broadcast)
    @doc_public
    def isValid(self, mac):
        """
        Check if the format of the mac gived as argument is valid

        @param mac: mac to evaluate
        @type mac: unknown

        @return: valid or not
        @rtype: boolean
        """
        MACADDRESS  =   r'(?:' + OCTET + r'%s' % self.sep + OCTET + r'%s' % self.sep + OCTET + r'%s' % self.sep + OCTET + r'%s' % self.sep + OCTET + r'%s' % self.sep + OCTET + r')'
        if re.match(r'^%s$' % MACADDRESS, mac) is None:
            return False
        else:
            return True

class String(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for string or can be also used to generate some random string with different combinations of characters.
        """
        pass
    @doc_public
    def isValid(self, strVal):
        """
        Returns True if the argument strVal is valid, and False otherwise.

        @param strVal: argument to evaluate
        @type strVal: unknown

        @return: valid or not
        @rtype: boolean
        """
        if isinstance( strVal, str):
            return True
        elif isinstance( strVal, unicode):
            return True
        else:
            return False
    @doc_public
    def containsDigits(self, strVal):
        """
        Evaluate the argument strVal and return the number of digits detected

        @param strVal: string to evaluate
        @type strVal: string

        @return: number of digits
        @rtype: integer
        """
        if not ( isinstance( strVal, str) or isinstance( strVal, unicode) ):
            raise TestValidatorsException( "ERR_VAL_001: string expected %s" % type(strVal) )
        nbDigits = 0
        for ch in strVal:
            if ch in string.digits:
                nbDigits += 1
        return nbDigits
    @doc_public
    def containsUpperCase(self, strVal):
        """
        Evaluate the argument strVal and return the number of letters detected in upper case

        @param strVal: string to evaluate
        @type strVal: string

        @return: number of letters in uppercase
        @rtype: integer
        """
        if not ( isinstance( strVal, str) or isinstance( strVal, unicode) ):
            raise TestValidatorsException( "ERR_VAL_002: string expected %s" % type(strVal) )
        nbLetterInUpper = 0
        for ch in strVal:
            if ch in string.ascii_uppercase:
                nbLetterInUpper += 1
        return nbLetterInUpper
    @doc_public
    def containsLowerCase(self, strVal):
        """
        Evaluate the argument strVal and return the number of letters detected in lower case

        @param strVal: string to evaluate
        @type strVal: string

        @return: number of letters in lowercase
        @rtype: integer
        """
        if not ( isinstance( strVal, str) or isinstance( strVal, unicode) ):
            raise TestValidatorsException( "ERR_VAL_003: string expected %s" % type(strVal) )
        nbLetterInLower = 0
        for ch in strVal:
            if ch in string.ascii_lowercase:
                nbLetterInLower += 1
        return nbLetterInLower
    @doc_public
    def containsWhitespaces(self, strVal):
        """
        Evaluate the argument strVal and return the number of whitespace detected

        @param strVal: string to evaluate
        @type strVal: string

        @return: number of whitespace
        @rtype: integer
        """
        if not ( isinstance( strVal, str) or isinstance( strVal, unicode) ):
            raise TestValidatorsException( "ERR_VAL_004: string expected %s" % type(strVal) )
        nbWhitespaces = 0
        for ch in strVal:
            if ch in string.whitespace:
                nbWhitespaces += 1
        return nbWhitespaces
    @doc_public
    def containsPunctuations(self, strVal):
        """
        Evaluate the argument strVal and return the number of punctuation detected

        @param strVal: string to evaluate
        @type strVal: string

        @return: number of punctuation
        @rtype: integer
        """
        if not ( isinstance( strVal, str) or isinstance( strVal, unicode) ):
            raise TestValidatorsException( "ERR_VAL_005: string expected %s" % type(strVal) )
        nbPunctuations = 0
        for ch in strVal:
            if ch in string.punctuation:
                nbPunctuations += 1
        return nbPunctuations
    @doc_public
    def getRandom(self, length=8, withLetterLowerCase=True, withLetterUpperCase=True, withPunctuation=False, withDigits=False, withWhitespace=False, withHexdigits=False):
        """
        Get a random string with various combination of characters

        @param length: string output length
        @type length: integer

        @param withLetterLowerCase: 'abcdefghijklmnopqrstuvwxyz'
        @type withLetterLowerCase: boolean

        @param withLetterUpperCase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        @type withLetterUpperCase: boolean

        @param withPunctuation: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
        @type withPunctuation: boolean

        @param withDigits: '0123456789'
        @type withDigits: boolean

        @param withWhitespace: authorize whitespace
        @type withWhitespace: boolean

        @param withHexdigits: '0123456789abcdefABCDEF'.
        @type withHexdigits: boolean

        @return: a random string of the length passed as argument
        @rtype: string
        """
        chars = ''
        if withLetterLowerCase:
            chars += string.ascii_lowercase
        if withLetterUpperCase:
            chars += string.ascii_uppercase
        if withDigits:
            chars += string.digits
        if withPunctuation:
            chars += string.punctuation
        if withWhitespace:
            chars += string.whitespace
        if withHexdigits:
            chars += string.hexdigits
        if not len(chars):
            return ''
        return ''.join([random.choice(chars) for i in range(length)])

class Integer(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for integer or can be also used to generate some random integer.
        """
        pass
    @doc_public
    def isValid(self, n):
        """
        Returns True if the argument n is valid, and False otherwise.

        @param n: argument to evaluate
        @type n: unknown

        @return: valid or not
        @rtype: boolean
        """
        try:
            dummy = int(n)
            return True
        except ValueError:
            return False
    @doc_public
    def getRandom(self, imin=0, imax=10):
        """
        Returns an integral random value from the interval [imin,imax]

        @param imin: minimun value of the interval
        @type imin: integer

        @param imax: maximum value of the interval
        @type imax: integer

        @return:  an integral random value
        @rtype: integer
        """
        irand = random.randrange( imin, imax + 1)
        return irand

class Float(object):
    @doc_public
    def __init__(self):
        """
        This class provides a validator for float or can be also used to generate some random float number
        """
        pass
    @doc_public
    def isValid(self, n):
        """
        Returns True if the argument n is valid, and False otherwise.

        @param n: argument to evaluate
        @type n: unknown

        @return: valid or not
        @rtype: boolean
        """
        try:
            dummy = float(n)
            return True
        except ValueError:
            return False
    @doc_public
    def getRandom(self, fmin=0.0, fmax=10.0):
        """
        Returns a floating-point random value from the interval [fmin,fmax]

        @param fmin: minimun value of the interval
        @type fmin: float

        @param fmax: maximum value of the interval
        @type fmax: float

        @return:  a floating-point random value
        @rtype: float
        """
        frand = random.uniform( fmin, fmax + 1)
        return frand



class PhoneNumber(object):
    def __init__(self, phone_number):
        """
        """
        self.phonenumber_str = phone_number
    def isValid(self):
        """
        """
        pass

class Date(object):
    def __init__(self, d):
        """
        This class provides a validator for date or can be also used to generate some random date.

        @param d: human date
        @type d: string
        """
        self.d = d
    def __str__(self):
        """
        """
        return self.d

class Time(object):
    def __init__(self, t):
        """
        This class provides a validator for time or can be also used to generate some random time.

        @param t: human time
        @type t: string
        """
        self.t = t
    def __str__(self):
        """
        """
        return self.t

class DateTime(object):
    
    def __init__(self, dt):
        """
        This class provides a validator for date and time or can be also used to generate some random date or/and time.

        @param dt: human date time
        @type dt: string
        """
        self.dt = dt
    def __str__(self):
        """
        """
        return self.dt