<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>27/01/2016 09:31:17</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>10</value><scope>local</scope></parameter><parameter><color /><description /><type>bool</type><name>VERBOSE</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>adb</type><name>AGENT</name><value>agent.win.adb01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)

	def prepare(self):
		# adapters and libraries
			
		self.MOBILE = SutAdapters.GUI.Adb(parent=self, name=None, debug=False, shared=False, agent=agent('AGENT'))

	def cleanup(self, aborted):
		pass

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()

		cmdId = self.MOBILE.wakeUp()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to wake up the device")

		cmdId = self.MOBILE.unlock()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to unlock the device")

		cmdId = self.MOBILE.typeShortcut(shortcut=SutAdapters.GUI.ADB_KEY_HOME)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to run action on device")

		self.MOBILE.freezeRotation()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT')) is None:
			self.error("unable to freeze rotation")

		self.MOBILE.deviceInfo()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT')) is None:
			self.error("unable to get device info")

		cmdId = self.MOBILE.clickPosition(x=720, y=780)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.dragPosition(startX=163, startY=451, endX=150, endY=1529)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to drag on device")

		cmdId = self.MOBILE.dragElement(text="Maps", endX=150, endY=1529)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to drag on device")

		cmdId = self.MOBILE.typeKeyCode(code=SutAdapters.GUI.ADB_KEYCODE_NUM_LOCK)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to type key code on device")
			
		cmdId = self.MOBILE.swipePosition(startX=1104, startY=1523, endX=486, endY=1673)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to swipe on device")

		cmdId = self.MOBILE.clickElement(description="Maps2", text="Maps")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.longClickElement(description="Maps", text="Maps")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.existElement( text="Maps")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.waitElement( text="Maps", timeout=15.0)
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to wait element on device")

		cmdId = self.MOBILE.clearTextElement( resourceId="com.google.android.googlequicksearchbox:id/launcher_search_button")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.getTextElement( resourceId="com.google.android.googlequicksearchbox:id/say_ok_google")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.longClickElement(resourceId="com.google.android.googlequicksearchbox:id/say_ok_google")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.clearTextElement( resourceId="com.google.android.googlequicksearchbox:id/search_box")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.typeText( text="aaaa")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")
	
		cmdId = self.MOBILE.typeTextElement( newText="aaaa", resourceId="com.google.android.apps.messaging:id/compose_message_text")
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to click on device")

		cmdId = self.MOBILE.openNotification()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to open notification action on device")

		cmdId = self.MOBILE.openQuickSettings()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to open notification action on device")

		cmdId = self.MOBILE.sleep()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to run action on device")

		cmdId = self.MOBILE.getLogs()
		if self.MOBILE.isActionAccepted(timeout=input('TIMEOUT'), actionId=cmdId) is None:
			self.error("unable to run adb command")
			
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1453883477.57288</testdevelopment>
</file>