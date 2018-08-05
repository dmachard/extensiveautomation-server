<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'files': ['/var/log/messages']}</args><name>file01</name><type>file</type></probe><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>06/03/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><value>True</value><description /><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><value>www.google.com</value><description /><name>HOST</name><type>str</type><scope>local</scope></parameter><parameter><value>www.google.com,127.0.0.1,10.0.0.1</value><description /><name>HOSTS</name><type>list</type><scope>local</scope></parameter><parameter><value>10.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
class PINGER_HOST_IS_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		up = A.isUp(host=input('HOST'))
		if up:
			self.info( 'host %s is up' % input('HOST') ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'host %s is down' % input('HOST') ) 
			self.step1.setFailed(actual="error")

class PINGER_HOST_IS_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		ip = '234.233.232.223'
		up = A.isUp(host='234.233.232.223')
		if up:
			self.info( 'host %s is up' % ip ) 
			self.step1.setFailed(actual="error")
		else:
			self.info( 'host %s is down' % ip ) 
			self.step1.setPassed(actual="success")

class PINGER_HOST_IS_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		ip = '234.233.232.223'
		down = A.isDown(host=ip)
		if down:
			self.info( 'host %s is down' % ip ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'host %s is up' % ip ) 
			self.step1.setFailed(actual="error")

class PINGER_HOST_IS_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		down = A.isDown(host=input('HOST'))
		if down:
			self.info( 'host %s is down' % input('HOST') ) 
			self.step1.setFailed(actual="error")
		else:
			self.info( 'host %s is up' % input('HOST') ) 
			self.step1.setPassed(actual="success")
		
class PINGER_HOST_ARE_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		up = A.areUp(hosts=input('HOSTS'))
		if up:
			self.info( 'all hosts are up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is down' ) 
			self.step1.setFailed(actual="error")

class PINGER_HOST_ARE_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		up = A.areUp(hosts=input('HOSTS')[:-1])
		if up:
			self.info( 'all hosts are up' )
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is down' ) 
			self.step1.setFailed(actual="error")

class PINGER_HOST_ARE_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		ips = [ '234.233.232.223', '235.233.232.223' ]
		down = A.areDown(hosts=ips)
		if down:
			self.info( 'all hosts are down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is up' ) 
			self.step1.setFailed(actual="error")

class PINGER_HOST_ARE_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostICMP(parent=self, debug=input(name='DEBUG'))
		down = A.areDown(hosts=input('HOSTS')[:-1])
		if down:
			self.info( 'all hosts are down' )
			self.step1.setFailed(actual="error")
		else:
			self.info( 'one host (or more) is up' ) 
			self.step1.setPassed(actual="success")

##
##
class PINGER_TCP_HOST_IS_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'), destPort=443)
		up = A.isUp(host=input('HOST'), timeout=input('TIMEOUT'))
		if up:
			self.info( 'host %s is up' % input('HOST') ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'host %s is down' % input('HOST') ) 
			self.step1.setFailed(actual="error")

class PINGER_TCP_HOST_IS_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		ip = '234.233.232.223'
		up = A.isUp(host='234.233.232.223')
		if up:
			self.info( 'host %s is up' % ip ) 
			self.step1.setFailed(actual="error")
		else:
			self.info( 'host %s is down' % ip ) 
			self.step1.setPassed(actual="success")

class PINGER_TCP_HOST_IS_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		ip = '234.233.232.223'
		down = A.isDown(host=ip)
		if down:
			self.info( 'host %s is down' % ip ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'host %s is up' % ip ) 
			self.step1.setFailed(actual="error")

class PINGER_TCP_HOST_IS_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		down = A.isDown(host=input('HOST'))
		if down:
			self.info( 'host %s is down' % input('HOST') ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'host %s is up' % input('HOST') ) 
			self.step1.setFailed(actual="error")
			
class PINGER_TCP_HOST_ARE_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		up = A.areUp(hosts=input('HOSTS'))
		if up:
			self.info( 'all hosts are up' ) 
			self.step1.setFailed(actual="error")
		else:
			self.info( 'one host (or more) is down' ) 
			self.step1.setPassed(actual="success")

class PINGER_TCP_HOST_ARE_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		up = A.areUp(hosts=input('HOSTS')[:-1])
		if up:
			self.info( 'all hosts are up' )
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is down' ) 
			self.step1.setFailed(actual="error")

class PINGER_TCP_HOST_ARE_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		ips = [ '234.233.232.223', '2.233.232.223' ]
		down = A.areDown(hosts=ips)
		if down:
			self.info( 'all hosts are down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is up' ) 
			self.step1.setFailed(actual="error")

class PINGER_TCP_HOST_ARE_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		down = A.areDown(hosts=input('HOSTS')[:-1])
		if down:
			self.info( 'all hosts are down' )
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is up' ) 
			self.step1.setFailed(actual="error")

class PINGER_TCP_HOST_PORTS_ARE_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		up = A.portsAreUp(host=input('HOST'), ports=[ 80, 443 ])
		if up:
			self.info( 'all hosts are up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is down' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_TCP_HOST_PORTS_ARE_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		up = A.portsAreUp(host=input('HOST'), ports=[ 80, 443, 43])
		if up:
			self.info( 'all hosts are up' ) 
			self.step1.setFailed(actual="error")		
		else:
			self.info( 'one host (or more) is down' ) 
			self.step1.setPassed(actual="success")
			
class PINGER_TCP_HOST_PORTS_ARE_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		down = A.portsAreDown(host=input('HOST'), ports=[ 5455, 3434 ])
		if down:
			self.info( 'all hosts are down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'one host (or more) is up' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_TCP_HOST_PORTS_ARE_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.HostTCP(parent=self, debug=input(name='DEBUG'))
		down = A.portsAreDown(host=input('HOST'), ports=[ 80, 22, 43])
		if down:
			self.info( 'all hosts are down' ) 
			self.step1.setPassed(actual="success")		
		else:
			self.info( 'one host (or more) is up' ) 
			self.step1.setFailed(actual="error")
##
##
class PINGER_URL_IS_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		up = A.isUp(url='www.google.com')
		if up is not None:
			self.info( 'url is up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'url is down' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_IS_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		up = A.isUp(url='www.titidfs.com')
		if up is not None:
			self.info( 'url is up' ) 
			self.step1.setFailed(actual="error")		
		else:
			self.info( 'url is down' ) 
			self.step1.setPassed(actual="success")
			
class PINGER_URL_IS_UP_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, https=True, debug=input(name='DEBUG'))
		up = A.isUp(url='www.google.com')
		if up is not None:
			self.info( 'url is up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'url is down' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_IS_UP_BODY_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		up = A.isUp(url='www.google.com', bodyExpected=TestOperators.Contains(needle='test') )
		if up is not None:
			self.info( 'url is up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'url is down' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_IS_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		down = A.isDown(url='www.azzdeazdezagoogle.com')
		if down is not None:
			self.info( 'url is down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'url is up' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_IS_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		down = A.isDown(url='www.google.com')
		if down is not None:
			self.info( 'url is down' ) 
			self.step1.setFailed(actual="error")		
		else:
			self.info( 'url is up' ) 
			self.step1.setPassed(actual="success")
			
class PINGER_URL_IS_DOWN_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, https=True, debug=input(name='DEBUG'))
		down = A.isDown(url='www.aaagoogle.com')
		if down is not None:
			self.info( 'url is down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'url is up' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_ARE_UP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		up = A.areUp(urls= ['www.google.com', 'www.microsoft.com'] )
		if up:
			self.info( 'all urls are up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'all urls are down' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_ARE_UP_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		up = A.areUp(urls=[ 'www.titidfs.com', 'www.google.com' ] )
		if up:
			self.info( 'all urls are up' ) 
			self.step1.setFailed(actual="error")		
		else:
			self.info( 'all urls are down' ) 
			self.step1.setPassed(actual="success")
			
class PINGER_URL_ARE_UP_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, https=True, debug=input(name='DEBUG'))
		up = A.areUp( urls=['www.google.com', 'www.facebook.com'] )
		if up:
			self.info( 'all urls are up' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'all urls are down' ) 
			self.step1.setFailed(actual="error")
			
class PINGER_URL_ARE_DOWN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		down = A.areDown(urls=[ 'www.azzdeazdezagoogle.com', 'dsqdzdeazdezagoogle.com'] )
		if down:
			self.info( 'all urls are down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'all urls are up' ) 
			self.step1.setFailed(actual="error")

class PINGER_URL_ARE_DOWN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, debug=input(name='DEBUG'))
		down = A.areDown(urls=['www.google.com', 'www.microsoft.com'])
		if down:
			self.info( 'all urls are down' ) 
			self.step1.setFailed(actual="error")		
		else:
			self.info( 'all urls are up' ) 
			self.step1.setPassed(actual="success")
			
class PINGER_URL_ARE_DOWN_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		A = SutAdapters.Pinger.URL(parent=self, https=True, debug=input(name='DEBUG'))
		down = A.areDown(urls= ['www.aaagoogle.com','www.dsqdsqdqdsqdsq.com' ] )
		if down:
			self.info( 'all urls are down' ) 
			self.step1.setPassed(actual="success")
		else:
			self.info( 'all urls are up' ) 
			self.step1.setFailed(actual="error")]]></testdefinition>
<testexecution><![CDATA[
PINGER_HOST_IS_UP_01(suffix=None).execute()
PINGER_HOST_IS_UP_02(suffix=None).execute()
PINGER_HOST_IS_DOWN_01(suffix=None).execute()
PINGER_HOST_IS_DOWN_02(suffix=None).execute()

PINGER_HOST_ARE_UP_01(suffix=None).execute()
PINGER_HOST_ARE_UP_02(suffix=None).execute()
PINGER_HOST_ARE_DOWN_01(suffix=None).execute()
PINGER_HOST_ARE_DOWN_02(suffix=None).execute()

PINGER_TCP_HOST_IS_UP_01(suffix=None).execute()
PINGER_TCP_HOST_IS_UP_02(suffix=None).execute()
PINGER_TCP_HOST_IS_DOWN_01(suffix=None).execute()
PINGER_TCP_HOST_IS_DOWN_02(suffix=None).execute()

PINGER_TCP_HOST_ARE_UP_01(suffix=None).execute()
PINGER_TCP_HOST_ARE_UP_02(suffix=None).execute()
PINGER_TCP_HOST_ARE_DOWN_01(suffix=None).execute()
PINGER_TCP_HOST_ARE_DOWN_02(suffix=None).execute()

PINGER_TCP_HOST_PORTS_ARE_UP_01(suffix=None).execute()
PINGER_TCP_HOST_PORTS_ARE_UP_02(suffix=None).execute()
PINGER_TCP_HOST_PORTS_ARE_DOWN_01(suffix=None).execute()
PINGER_TCP_HOST_PORTS_ARE_DOWN_02(suffix=None).execute()

PINGER_URL_IS_UP_01(suffix=None).execute()
PINGER_URL_IS_UP_02(suffix=None).execute()
PINGER_URL_IS_UP_03(suffix=None).execute()
PINGER_URL_IS_DOWN_01(suffix=None).execute()
PINGER_URL_IS_DOWN_02(suffix=None).execute()
PINGER_URL_IS_DOWN_03(suffix=None).execute()

PINGER_URL_ARE_UP_01(suffix=None).execute()
PINGER_URL_ARE_UP_02(suffix=None).execute()
PINGER_URL_ARE_UP_03(suffix=None).execute()
PINGER_URL_ARE_DOWN_01(suffix=None).execute()
PINGER_URL_ARE_DOWN_02(suffix=None).execute()
PINGER_URL_ARE_DOWN_03(suffix=None).execute()

PINGER_URL_IS_UP_BODY_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105830.47</testdevelopment>
</file>