<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>11/01/2014 19:39:48</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>HOST_DST</name><value>localhost</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>MYSQL_DB</name><value>xtc190</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>MYSQL_LOGIN</name><value>root</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>MYSQL_PWD</name><value /><scope>local</scope></parameter><parameter><description /><type>str</type><name>POSTGRES_DB</name><value>postgres</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>POSTGRES_LOGIN</name><value>postgres</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>POSTGRES_PWD</name><value>postgres</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>TABLE_PREFIX</name><value>xtc</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>10.0</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>VERBOSE</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT_DB</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class MYSQL_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="connected", description="connect to the database", summary="connect to the database")
		self.step2 = self.addStep(expected="one response", description="select all users from the table", 
																						summary="get the id of the user admin from the table")
		self.step3 = self.addStep(expected="disconnected", description="disconnect from the database", summary="disconnect from the databse")
	
	def prepare(self):

		# adapters
		self.ADP_MYSQL = SutAdapters.Database.MySQL( parent=self, host=input('HOST_DST'), user=input('MYSQL_LOGIN'),
													password=input('MYSQL_PWD'), debug=input('DEBUG'), verbose=input('VERBOSE'),
													agent=agent('AGENT_DB'), agentSupport=input('SUPPORT_AGENT')
											)

		self.ADP_MYSQL.connect(dbName=input('MYSQL_DB'), timeout=input('TIMEOUT'))
		
		self.step1.start()
		if not self.ADP_MYSQL.isConnected(timeout=input('TIMEOUT')):
			self.abort('connect failed')
		else:
			self.step1.setPassed(actual='connected')
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)

	def definition(self):
		self.step2.start()
		self.ADP_MYSQL.query(query='SELECT id FROM `%s-users` WHERE login="admin"' % input('TABLE_PREFIX'))
		rsp = self.ADP_MYSQL.hasReceivedRow(timeout=input('TIMEOUT'))
		if not rsp:
			self.step2.setFailed(actual='response failed')
		else:
			self.step2.setPassed(actual='response received')
			
			row =  rsp.get('DB', 'row') 
			self.info( "result: id=%s" % row.get('id') )
			
			Cache().set(name="result", data=row)
			
		self.step3.start()
		self.ADP_MYSQL.disconnect()
		if not self.ADP_MYSQL.isDisconnected(timeout=input('TIMEOUT')):
			self.step3.setFailed(actual='disconnect failed')
		else:
			self.step3.setPassed(actual='disconnected')
		
		
class POSTGRESQL_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="connected", description="connect to the database", summary="connect to the database")
		self.step2 = self.addStep(expected="one response", description="select all users from the table", 
																						summary="get the id of the user admin from the table")
		self.step3 = self.addStep(expected="disconnected", description="disconnect from the database", summary="disconnect from the databse")
	
	def prepare(self):

		# adapters
		self.ADP_POSTGRES = SutAdapters.Database.PostgreSQL( parent=self, host=input('HOST_DST'), user=input('POSTGRES_LOGIN'),
													password=input('POSTGRES_PWD'), debug=input('DEBUG'),
													agent=agent('AGENT_DB'), agentSupport=input('SUPPORT_AGENT')
											)

		# connect to the database
		self.step1.start()
		self.ADP_POSTGRES.connect(dbName=input('POSTGRES_DB'), timeout=input('TIMEOUT'))
		if not self.ADP_POSTGRES.isConnected(timeout=input('TIMEOUT')):
			self.step1.setFailed(actual='connect failed')
		else:
			self.step1.setPassed(actual='connected')
	def cleanup(self, aborted):
		self.step3.start()
		self.ADP_POSTGRES.disconnect()
		if not self.ADP_POSTGRES.isDisconnected(timeout=input('TIMEOUT')):
			self.step3.setFailed(actual='disconnect failed')
		else:
			self.step3.setPassed(actual='disconnected')
		
	def definition(self):
		self.step2.start()

		self.ADP_POSTGRES.query(query="""INSERT INTO playground (type, color, location, install_date) VALUES ('slide', 'blue', 'south', '2014-04-28')""")
		rsp = self.ADP_POSTGRES.isExecuted(timeout=input('TIMEOUT'))
		if not rsp:
			self.step2.setFailed(actual='response failed')
		else:
			self.step2.setPassed(actual='response received')

		self.ADP_POSTGRES.query(query="""UPDATE playground SET color = 'green' WHERE type = 'swing'""")
		rsp = self.ADP_POSTGRES.isExecuted(timeout=input('TIMEOUT'))
		if not rsp:
			self.step2.setFailed(actual='response failed')
		else:
			self.step2.setPassed(actual='response received')

		self.ADP_POSTGRES.query(query="""SELECT * from playground""")
		rsp = self.ADP_POSTGRES.isExecuted(timeout=input('TIMEOUT'))
		if not rsp:
			self.step2.setFailed(actual='response failed')
		else:
			self.step2.setPassed(actual='response received')

		self.ADP_POSTGRES.query(query="""DELETE FROM playground WHERE type = 'slide'""")
		rsp = self.ADP_POSTGRES.isExecuted(timeout=input('TIMEOUT'))
		if not rsp:
			self.step2.setFailed(actual='response failed')
		else:
			self.step2.setPassed(actual='response received')]]></testdefinition>
<testexecution><![CDATA[
MYSQL_01(suffix=None).execute()
#POSTGRESQL_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1389465588.39</testdevelopment>
</file>