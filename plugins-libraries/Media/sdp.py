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
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
from TestExecutorLib.TestExecutorLib import doc_public

__NAME__="""SDP"""

# RFC4566: SDP: Session Description Protocol

CODEC_MAP = {
								0: 'PCMU/8000',
								3: 'GSM/8000',
								4: 'G723/8000',
								8: 'PCMA/8000', 
								18: 'G729/8000',
								34: 'H263/90000',
								97: 'H264/90000',
								99: 'H263-1998/90000',
								100: 'MP4V-ES/90000',
								101: 'telephone-event/8000'
						}

#templates
def tplsdp(session=None, time=None, media=None):
	"""
	Construct a  template for a SDP payload
	"""
	tpl = TestTemplatesLib.TemplateLayer('SDP')	

	if session is not None:
		if session.getLenItems() > 0:
			tpl.addKey(name='session', data=session )
	if time is not None:
		if time.getLenItems() > 0:
			tpl.addKey(name='timing', data=time )
	if media is not None:
		if media.getLenItems() > 0:
			tpl.addKey(name='medias', data=media )		
	return tpl

def tplsession(v=None, o=None, s=None, i=None, u=None, e=None, p=None, c=None, b=None, k=None, a=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if v is not None:
		tpl.addKey(name='version', data=v)

	if o is not None:
		tpl.addKey(name='origin', data=o)

	if s is not None:
		tpl.addKey(name='name', data=s)

	if i is not None:
		tpl.addKey(name='information', data=i)

	if u is not None:
		tpl.addKey(name='uri', data=u)
		
	if e is not None:
		tpl.addKey(name='email', data=e)
		
	if p is not None:
		tpl.addKey(name='phone', data=p)

	if c is not None:
		tpl.addKey(name='connection', data=c)

	if b is not None:
		tpl.addKey(name='bandwidth', data=b)

	if k is not None:
		tpl.addKey(name='encryption', data=k)
		
	if a is not None:
		tpl.addKey(name='attributes', data=a)
	return tpl

def tpltime(t=None, z=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if t is not None:
		tpl.addKey(name='session', data=t)
		
	if z is not None:
		tpl.addKey(name='time-zones', data=z)
	
	return tpl

def tplo(username=None, sess_id=None, sess_version=None, net_type=None, addr_type=None, unicast_addr=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if username is not None:
		tpl.addKey(name='username', data=username)	

	if sess_id is not None:
		tpl.addKey(name='session-id', data=sess_id)	

	if sess_version is not None:
		tpl.addKey(name='session-version', data=sess_version)	

	if net_type is not None:
		tpl.addKey(name='nettype', data=net_type)	

	if addr_type is not None:
		tpl.addKey(name='addrtype', data=addr_type)	

	if unicast_addr is not None:
		tpl.addKey(name='unicast-address', data=unicast_addr)	
	return tpl
	
def tplc(nettype=None, addrtype=None, connection_address=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if nettype is not None:
		tpl.addKey(name='nettype', data=nettype)	

	if addrtype is not None:
		tpl.addKey(name='addrtype', data=addrtype)	

	if connection_address is not None:
		tpl.addKey(name='connection-address', data=connection_address)		
	return tpl
	
def tplt(start_time=None, stop_time=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if start_time is not None:
		tpl.addKey(name='start-time', data=start_time)	

	if stop_time is not None:
		tpl.addKey(name='stop-time', data=stop_time)	
	return tpl
	
def tplk(method=None,encryption_key=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if method is not None:
		tpl.addKey(name='method', data=method)	

	if encryption_key is not None:
		tpl.addKey(name='encryption-key', data=encryption_key)	
	return tpl

def tpla(attribute=None, value=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if attribute is not None:
		tpl.addKey(name='attribute', data=attribute)	

	if value is not None:
		tpl.addKey(name='value', data=value)	
	return tpl

def tplm(media=None, port=None, proto=None, fmt=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if media is not None:
		tpl.addKey(name='media', data=media)	

	if port is not None:
		tpl.addKey(name='port', data=port)	
		
	if proto is not None:
		tpl.addKey(name='proto', data=proto)	

	if fmt is not None:
		tpl.addKey(name='fmt', data=fmt)	
		
	return tpl

def tplb(bwtype=None, bandwidth=None):
	"""
	"""
	tpl = TestTemplatesLib.TemplateLayer('')
	
	if bwtype is not None:
		tpl.addKey(name='bwtype', data=bwtype)	

	if bandwidth is not None:
		tpl.addKey(name='bandwidth', data=bandwidth)	
		
	return tpl
	
# codec
class Codec(object):
	def __init__(self, parent):
		"""
		"""
		self.parent = parent
		self.warning = self.parent.warning
		self.debug = self.parent.debug
		self.info = self.parent.info
		
	def encode(self, sdp):
		"""
		Encode dict SDP to text message
		"""
		if not sdp.has_key('session'): raise Exception('session key is mandatory')
		sess = sdp['session']
		if not sess.has_key('origin'): raise Exception('origin key in session is mandatory')
		if not sess.has_key('connection'): raise Exception('connection key in session is mandatory')
		orig = sess['origin']
		conn = sess['connection'] 
		
		sdpEncoded =  [ 'v=%s' % sess['version'] ]
		sdpEncoded.append(  'o=%s %s %s %s %s %s' % ( orig['username'], 
																	orig['session-id'], orig['session-version'], 
																	orig['nettype'], orig['addrtype'], orig['unicast-address'])  )
		sdpEncoded.append( 's=%s' % sess['name'] )
		sdpEncoded.append( 'c=%s %s %s' % ( conn['nettype'], conn['addrtype'], conn['connection-address'] ) )
		
		
		if sess.has_key('bandwidth'):
			bw = sess['bandwidth']
			sdpEncoded.append( 'b=%s:%s' % ( bw['bwtype'], bw['bandwidth']) )

		# encode timing not yet supported
		sdpEncoded.append( 't=0 0' )
		

		if sess.has_key('attributes'):
			for attr in sess['attributes']:
				if attr.has_key('value'):
					sdpEncoded.append( 'a=%s:%s' % (attr['attribute'], attr['value']) )
				else:
					medias.append( 'a=%s' % (attr['attribute']) )
					
		medias = []
		for media in sdp['medias']:
			m_descr = media['description']
			
			if media.has_key('connection-data'):
				m_conn = media['connection-data']
			else:
				m_conn = None
			m_attrs = media['attributes']
			
			medias.append( 'm=%s %s %s %s' % ( m_descr['media'], m_descr['port'], m_descr['proto'], m_descr['fmt'] ) )
			
			if media.has_key('media-title'):
				medias.append( 'i=%s' % media['media-title'] )
			
			if m_conn is not None:
				medias.append( 'c=%s %s %s' % ( m_conn['nettype'], m_conn['addrtype'], m_conn['connection-address'] ) )
			
			if media.has_key('encryption'):
				m_encrypt = media['encryption']
				medias.append( 'k=%s:%s' % (m_encrypt['method'], m_encrypt['encryption-key'] ) )
				
			if media.has_key('bandwidth'):
				m_bw = media['bandwidth']
				medias.append( 'b=%s:%s' % ( m_bw['bwtype'], m_bw['bandwidth']) )
				
			for attr in m_attrs:
				if attr.has_key('value'):
					medias.append( 'a=%s:%s' % ( attr['attribute'], attr['value'] ) )
				else:
					medias.append( 'a=%s' % (attr['attribute']) )
					
		sdpEncoded.extend( medias )
		
		# add nothing to add the last \r\n
		sdpEncoded.append('')
		return '\r\n'.join(sdpEncoded)
		
	def decode(self, sdp):
		"""
		Decode a sdp text message
		"""
		sess_v = None
		sess_o = None
		sess_s = None
		sess_i = None
		sess_u = None
		sess_e = None
		sess_p = None
		sess_c = None
		sess_b = None
		sess_k = None
		sess_a = None
		sess_t = None
		sess_z = None
		
		media = None
		media_a = None
		tpl_media = TestTemplatesLib.TemplateLayer('')
		
		# An SDP session description consists of a number of lines of text of <type>=<value>
		for line in sdp.splitlines():
			# split the type and value with the following separator =
			tv = line.split('=', 1)
			if len(tv) != 2: raise Exception('invalid sdp: %s' % tv)
							
			# remove uneeded spaces
			t = tv[0].strip() 
			v = tv[1]
			
			# The "v=" field gives the version of the Session Description Protocol.
			if t == "v":
				sess_v = v
			
			# globally unique identifier for the session
			# o=<username> <sess-id> <sess-version> <nettype> <addrtype> <unicast-address>
			if t == "o":
				v_parsed = v.split(' ')
				if len(v_parsed) != 6: raise Exception('invalid sdp: %s' % v_parsed)
				sess_o = tplo(username=v_parsed[0], sess_id=v_parsed[1], sess_version=v_parsed[2], 
												net_type=v_parsed[3], addr_type=v_parsed[4], unicast_addr=v_parsed[5])
				
			# s=<session name>
			if t == "s":
				sess_s = v
				
			# i=<session description>
			if t == "i":
				if media is not None:
					media.addKey(name='media-title', data=v)
				else:
					sess_i = v
			
			# u=<uri>	
			if t == "u":
				sess_u = v
				
			# e=<email-address>
			if t == "e":
				sess_e = v
				
			# p=<phone-number>
			if t == "p":
				sess_p = v	
			
			# c=<nettype> <addrtype> <connection-address>
			if t == "c":
				v_parsed = v.split(' ')
				if len(v_parsed) != 3: raise Exception('invalid sdp: %s' % v_parsed)
				tpl = tplc(nettype=v_parsed[0], addrtype=v_parsed[1], connection_address= v_parsed[2])
				if media is not None: 
					media.addKey(name='connection-data', data=tpl)
				else:
					# for session
					sess_c = tpl
		
			# b=<bwtype>:<bandwidth>
			if t == "b":
				v_parsed = v.split(':', 1)
				if len(v_parsed) != 2: raise Exception('invalid sdp: %s' % v_parsed)
				tpl = tplb(bwtype=v_parsed[0], bandwidth=v_parsed[1])
				if media is not None:
					media.addKey(name='bandwidth', data=tpl)
				else:
					sess_b = tpl
					
			# t=<start-time> <stop-time>	
			if t == "t":
				v_parsed = v.split(' ')
				if len(v_parsed) != 2: raise Exception('invalid sdp: %s' % v_parsed)
				tpl = tplt(start_time=v_parsed[0], stop_time=v_parsed[1])
				if sess_t is None:
					sess_t = TestTemplatesLib.TemplateLayer('')
					sess_t.addKey(name="%s" % sess_t.getLenItems(), data=tpl)						
				else:
					sess_t.addKey(name="%s" % sess_t.getLenItems(), data=tpl)	
			
			# r=<repeat interval> <active duration> <offsets from start-time>
			if t == "r":
				v_parsed = v.split(' ', 2)
				if len(v_parsed) != 3: raise Exception('invalid sdp: %s' % v_parsed)
				tpl.addKey(name='repeat-interval', data=v_parsed[0])
				tpl.addKey(name='active-duration', data=v_parsed[1])
				tpl.addKey(name='offsets-from-start-time', data=v_parsed[2])
			
			# z=<adjustment time> <offset> <adjustment time> <offset> ....
			if t == "z":
				sess_z = v
			
			#k=<method>
			#k=<method>:<encryption key>	
			if t == "k":
				v_parsed = v.split(':', 1)
				key = None
				if len(v_parsed) == 1:
					method = v_parsed[0]
				if len(v_parsed) == 2:
					method = v_parsed[0]
					key = v_parsed[1]
				tpl = tplk(method=method,encryption_key=key)
				if media is not None: 
					media.addKey(name='encryption', data=tpl)
				else:
					sess_k = tpl
					
			#a=<attribute>
			#a=<attribute>:<value>		
			if t == "a":
				v_parsed = v.split(':', 1)
				value = None
				if len(v_parsed) == 1:
					attribute = v_parsed[0]
				if len(v_parsed) == 2:
					attribute = v_parsed[0]
					value = v_parsed[1]
				tpl = tpla(attribute=attribute,value=value)
				if media is not None: 
					if media_a is None:
						media_a = TestTemplatesLib.TemplateLayer('')
						media_a.addKey(name="%s" % media_a.getLenItems(), data=tpl)
						media.addKey(name='attributes', data=media_a)						
					else:
						media_a.addKey(name="%s" % media_a.getLenItems(), data=tpl)	
				else:
					if sess_a is None:
						sess_a = TestTemplatesLib.TemplateLayer('')
						sess_a.addKey(name="%s" % sess_a.getLenItems(), data=tpl)						
					else:
						sess_a.addKey(name="%s" % sess_a.getLenItems(), data=tpl)	

			#m=<media> <port> <proto> <fmt> ...	
			if t == "m":
				if media is not None:
					tpl_media.addKey(name="%s" % tpl_media.getLenItems(), data=media)
					media_a = None	
					
				v_parsed = v.split(' ', 3)
				if len(v_parsed) != 4: raise Exception('invalid sdp: %s' % v_parsed)
				media_m = tplm(media=v_parsed[0], port=v_parsed[1], proto=v_parsed[2], fmt=v_parsed[3])
				media = TestTemplatesLib.TemplateLayer('')
				media.addKey(name='description', data=media_m)
		
		# add last if exists
		if media is not None:
			tpl_media.addKey(name="%s" % tpl_media.getLenItems(), data=media)				
			media = None
			
		# create  template
		tpl_session = tplsession(v=sess_v, o=sess_o, s=sess_s, i=sess_i, u=sess_u, e=sess_e, p=sess_p, c=sess_c, b=sess_b, k=sess_k, a=sess_a) 
		tpl_timing = tpltime(t=sess_t, z=sess_z)
		tpl = tplsdp(session=tpl_session, time=tpl_timing, media=tpl_media)
		return tpl
# class
class SDP(TestLibraryLib.Library):
	@doc_public
	def __init__ (self, parent, name=None, debug=False, sdpUsername='-', sessionName='extensivetesting', sdpVersion='0', codecsOrder=[ '8', '0' ], addrType='IP4',
									sessVersion='1', sessId='1', unicastAddress='127.0.0.1', connectionAddress='127.0.0.1', shared=False ):
		"""

		This class enables to encode/decode sdp and contructs sdp offer and answer.
		
		@param parent: testcase 
		@type parent: testcase

		@param name: library name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param sdpUsername: the sdp username (default=-)
		@type sdpUsername: string
		
		@param sessionName: the session name (default=extensivetesting)
		@type sessionName: string
		
		@param sdpVersion: sdp version (default=0)
		@type sdpVersion: string
		
		@param codecsOrder: list of codecs supported sorted by preference (default: [8, 0])
		@type codecsOrder: list of string
		
		@param addrType:  address type (defaut=IN4 )
		@type addrType: string
		
		@param sessVersion:  version number for this session (defaut=1 )
		@type sessVersion: string
		
		@param sessId: unique identifier for the session (defaut=1 )
		@type sessId: string
		
		@param unicastAddress:  unicast ip address (default=127.0.0.1)
		@type unicastAddress: string
		
		@param connectionAddress:  connection ip address (default=127.0.0.1)
		@type connectionAddress: string

		@param debug: True to activate debug mode (default=False)
		@type debug: boolean
		
		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""
		TestLibraryLib.Library.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name, shared=shared)
		self.username = sdpUsername
		self.sdpVersion = str(sdpVersion)
		self.sessName = str(sessionName)
		self.sessId = str(sessId)
		self.sessVersion = str(sessVersion)
		self.addrType = str(addrType)
		self.proto = str('RTP/AVP')
		self.codecs = codecsOrder
		self.connectionAddress = str(connectionAddress)
		self.unicastAddress = str(unicastAddress)

		# init the SDP encoder/decoder 
		self.sdpCodec = Codec(parent=self)
		self.__remote_sdp_offer = None
		self.__remote_sdp_answer = None
		self.__codec_choosed = None
	@doc_public
	def decode(self, sdp):
		"""
		Decode a sdp text message in  template
		
		@param sdp: raw sdp
		@type sdp: string
		
		@return: sdp decoded
		@rtype:	templatelayer	
		"""
		return self.sdpCodec.decode(sdp=sdp)
	@doc_public
	def encode(self, sdp):
		"""
		Encode dict SDP to text message
		
		@param sdp: sdp
		@type sdp: dict
		
		@return: sdp encoded 
		@rtype:	integer	
		"""
		return self.sdpCodec.encode(sdp=sdp)
	@doc_public
	def setConnectionAddress(self, connectionAddress):
		"""
		Set the connection address
		
		@param connectionAddress: connection ip address
		@type connectionAddress: string
		"""
		self.connectionAddress = connectionAddress
	@doc_public
	def setUnicastAddress(self, unicastAddress):
		"""
		Set the unicast address
		
		@param unicastAddress: unicast ip address
		@type unicastAddress: string
		"""
		self.unicastAddress = unicastAddress
	
	def __getSession(self, null):
		"""
		private function
		"""
		tpl = {}
		tpl['session'] = {'version': self.sdpVersion, 'name': self.sessName}
		tpl['session']['origin'] = { 'username':self.username, 'session-id': self.sessId, 'session-version': self.sessVersion,
																	'nettype': 'IN', 'addrtype': self.addrType, 'unicast-address': self.unicastAddress }
		tpl['session']['connection'] = { 'nettype': 'IN', 'addrtype': self.addrType }
		if null:
			tpl['session']['connection']['connection-address'] = '0.0.0.0'
		else:
			tpl['session']['connection']['connection-address'] = self.connectionAddress		
		return tpl 
	@doc_public
	def reorderCodecs(self, preferedCodec):
		"""
		Reorders codecs, put the prefered codec at the first place
		
		@param preferedCodec: prefered codec
		@type preferedCodec: integer
		"""
		try:
			for i in xrange(len(self.codecs)):
				if self.codecs[i] == str(preferedCodec):
					break
			# remove codec from the list
			self.codecs.pop(i)
			# add prefered codec to the first place
			self.codecs.insert(0, str(preferedCodec) )
		except Exception as e:
			self.error( 'failed to reorder codecs: %s' % str(e) )
	@doc_public
	def getOffer(self, null=False, audioPort=0):
		"""
		Contructs a sdp offer
		
		@param null: null
		@type null: boolean
		
		@param audioPort: source audio port
		@type audioPort: integer
		
		@return: sdp offer
		@rtype:	string	
		"""
		sdp_encoded = ''
		try:
			# prepare the session definition
			sdp = self.__getSession(null=null)
			# add default media supported
			# just audio 
			sdp['medias'] = []
			audio = {}
			audio['description'] = {'media': 'audio', 'port': str(audioPort), 'proto': self.proto, 'fmt': ' '.join(self.codecs) }
			audio['connection-data'] = { 'nettype': 'IN', 'addrtype': self.addrType, 'connection-address': self.connectionAddress }
			audio['attributes'] = []

			for c in self.codecs:
				attr = { 'attribute': 'rtpmap', 'value': '%s %s' % (c, CODEC_MAP[int(c)] )  }
				audio['attributes'].append( attr )

			if null:
				audio['attributes'].append( {'attribute': 'sendonly' } )
			else:
				audio['attributes'].append( {'attribute': 'sendrecv'  } )
			sdp['medias'].append(audio)

			# encode 
			sdp_encoded = self.sdpCodec.encode(sdp=sdp)
		except Exception as e:
			self.error( "get offer failed: %s" % str(e) )
		return sdp_encoded
	@doc_public
	def getAnswer(self, null=False, audioPort=0):
		"""
		Contructs a sdp offer
		
		@param null: null
		@type null: boolean
		
		@param audioPort: source audio port
		@type audioPort: integer
		
		@return: sdp answer
		@rtype:	string	
		"""
		sdp_encoded = ''
		try:
			# prepare the session definition
			sdp = self.__getSession(null=False)
			
			# just audio 
			sdp['medias'] = []
			if self.__codec_choosed is not None:
				audio = {}
				audio['description'] = {'media': 'audio', 'port': str(audioPort), 'proto': self.proto, 'fmt': str(self.__codec_choosed) }
				audio['connection-data'] = { 'nettype': 'IN', 'addrtype': self.addrType, 'connection-address': self.connectionAddress }
				audio['attributes'] = []
				for c in [ self.__codec_choosed ]:
					attr = { 'attribute': 'rtpmap', 'value': '%s %s' % (c, CODEC_MAP[int(c)] )  }
					audio['attributes'].append( attr )
			
			if null:
				audio['attributes'].append( {'attribute': 'recvonly' } )
			else:
				audio['attributes'].append( {'attribute': 'sendrecv'  } )
			sdp['medias'].append(audio)
			
			# encode 
			sdp_encoded = self.sdpCodec.encode(sdp=sdp)
		except Exception as e:
			self.error( "get answer failed: %s" % str(e) )
		return sdp_encoded
		
	def setRemoteOffer(self, sdp):
		"""
		"""
		self.__remote_sdp_offer = sdp

	def setRemoteAnswer(self, sdp):
		"""
		"""
		self.__remote_sdp_answer = sdp
	
	def getRemoteAnswer(self):
		"""
		"""
		return 	self.__remote_sdp_answer
		
	def getRemoteOffer(self):
		"""
		"""
		return 	self.__remote_sdp_offer
	@doc_public
	def negotiatesCodec(self, sdp):
		"""
		Negociate codecs
		
		@param sdp: sdp answer
		@type sdp:  template 
		
		@return: codec choosed, ip, port
		@rtype: tuple
		"""
		
		port = None
		ip = None
		codecsReceived = None
		codecChoosed = None
		try:
			sdpMedias = sdp.get('medias').getItems()
			
			sess = sdp.get('session')
			c_sess = sess.get('connection') # optional
			if c_sess is not None:
				ip = c_sess.get('connection-address')

			# search audio codecs list
			for k, v in sdpMedias:
				# extract ip if exists
				m_conn = v.get('connection-data')
				if m_conn is not None:
					ip = m_conn.get('connection-address')

				# extract codec
				m_descr = v.get('description')
				mtype = m_descr.get('media')
				if mtype == 'audio':
					codecsReceived = m_descr.get('fmt')
					port = m_descr.get('port')
					break

		
			for c1 in codecsReceived.split(' '):
				for c2 in self.codecs:
					if int(c1) == int(c2):
						codecChoosed = int(c2)
						break
				if codecChoosed is not None:
					break
			self.__codec_choosed = codecChoosed
		except Exception as e:
			self.error( 'unable to negotiate codec: %s' % str(e) )	
		return codecChoosed, ip, port