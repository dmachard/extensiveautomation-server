<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>23/09/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>remote-image</type><name>IMG</name><value>remote-tests(Common):/Samples/Images/calc_5.png</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class CHARTJS_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		# steps description
		self.step1 = self.addStep(expected="bar chart", description="step description", summary="step sample", enabled=True)
		self.step2 = self.addStep(expected="line chart", description="step description", summary="step sample", enabled=True)
		self.step3= self.addStep(expected="pie chart", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		# adapters and libraries
		self.LIB_CHART = SutLibraries.Media.ChartJS(parent=self, name=None, debug=False)
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
		
			# bar chart
			labelsAxes = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
			dataA = [12, 19, 3, 5, 2, 3]
			dataB = [22, 49, 3, 5, 23, 3]
			legendDatas = ["tets", "test"]
			backgroundColor = '#4BC0C0'
			borderColor = '#36A2EB'
			myChart = self.LIB_CHART.barChart(labelsAxes=labelsAxes, datas=[dataA, dataB], legendDatas=legendDatas, width=400, height=300,
																															backgroundColors=[borderColor, backgroundColor], borderColors=[borderColor, backgroundColor],
																															chartTitle="test")
			self.step1.setPassed(actual="chart", chart=myChart)
			
		if self.step2.isEnabled():
			self.step2.start()
			# line chart
			labelsAxes = ["January", "February", "March", "April", "May", "June", "July"]
			legendDatas = ["test", "test2"]
			dataA = [65, 59, 80, 81, 56, 55, 40]
			dataB = [15, 29, 30, 41, 26, 55, 20]
			backgroundColor = '#4BC0C0'
			borderColor = '#36A2EB'
			myChart2 = self.LIB_CHART.lineChart(labelsAxes=labelsAxes, legendDatas=legendDatas, datas=[ dataA, dataB ] , width=400, height=300, 
																												backgroundColors=[borderColor, backgroundColor], borderColors=[borderColor, backgroundColor],
																												fills=[False, False], chartTitle="test")
			self.step2.setPassed(actual="chart", chart=myChart2)
			
		if self.step3.isEnabled():
			self.step3.start()
			# pie chart
			legendData = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
			dataA = [12, 19, 3, 5, 2, 3]
			backgroundColors =[ "#FF6384", "#36A2EB", "#FFCE56"]
			myChart3 = self.LIB_CHART.pieChart(legendData=legendData, data=dataA, width=400, height=300,
																															backgroundColors=backgroundColors, chartTitle="test", doughnut=False)
			self.step3.setPassed(actual="chart", chart=myChart3)
			
	def cleanup(self, aborted):
		pass

class IMAGES_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.img = SutLibraries.Media.Image(parent=self, debug=get('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		color = self.img.mainColor(imgData=input('IMG'))
		self.info( color )
		
		self.step1.setPassed(actual="pass")
		
class DIALTONES_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.tonesGen = SutLibraries.Media.DialTones(parent=self, debug=get('DEBUG'), rate=8000, volume=100)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		samples = self.tonesGen.press0(duration=500)
		self.info( samples )
		
		samples = self.tonesGen.press1(duration=500)
		samples = self.tonesGen.press2(duration=500)
		samples = self.tonesGen.press3(duration=500)
		samples = self.tonesGen.press4(duration=500)
		samples = self.tonesGen.press5(duration=500)
		samples = self.tonesGen.press6(duration=500)
		samples = self.tonesGen.press7(duration=500)
		samples = self.tonesGen.press8(duration=500)
		samples = self.tonesGen.press9(duration=500)
		samples = self.tonesGen.pressA(duration=500)
		samples = self.tonesGen.pressB(duration=500)
		samples = self.tonesGen.pressC(duration=500)
		samples = self.tonesGen.pressD(duration=500)
		samples = self.tonesGen.pressPound(duration=500)
		samples = self.tonesGen.pressStar(duration=500)
		samples = self.tonesGen.pressStar(duration=500)
		samples = self.tonesGen.pressKeys(symbols='12', duration=500)

		self.step1.setPassed(actual="pass")
		
class DIALTONES_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.tonesGen = SutLibraries.Media.DialTones(parent=self, debug=get('DEBUG'), rate=8000, volume=100)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		samples = self.tonesGen.busyTone(country=SutLibraries.Media.UE)
		samples = self.tonesGen.busyTone(country=SutLibraries.Media.US)
		samples = self.tonesGen.busyTone(country=SutLibraries.Media.UK)
		self.info( samples )
		
		samples = self.tonesGen.dialTone(country=SutLibraries.Media.UE)
		samples = self.tonesGen.dialTone(country=SutLibraries.Media.US)
		samples = self.tonesGen.dialTone(country=SutLibraries.Media.UK)
		
		samples = self.tonesGen.ringbackTone(country=SutLibraries.Media.UE)
		samples = self.tonesGen.ringbackTone(country=SutLibraries.Media.US)
		samples = self.tonesGen.ringbackTone(country=SutLibraries.Media.UK)

		samples = self.tonesGen.specialInformationTone(code=SutLibraries.Media.SIT_RO)
		samples = self.tonesGen.specialInformationTone(code=SutLibraries.Media.SIT_RO2)
		samples = self.tonesGen.specialInformationTone(code=SutLibraries.Media.SIT_VC)
		samples = self.tonesGen.specialInformationTone(code=SutLibraries.Media.SIT_NC)
		
		self.step1.setPassed(actual="pass")
		
class NOISE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.noisesGen = SutLibraries.Media.Noise(parent=self, debug=get('DEBUG'), rate=500, amplitude=100, bits=SutLibraries.Media.SIGNED_16BITS)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		samples = self.noisesGen.silence(duration=100)
		self.info( samples )
		
		samples = self.noisesGen.vinyl(duration=100, x=0.25, y=0.02, f=10)
		samples = self.noisesGen.white(duration=100)
		
		self.step1.setPassed(actual="pass")
		
class WAVE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.wavesGen = SutLibraries.Media.Waves(parent=self, debug=get('DEBUG'), rate=500, amplitude=100, bits=SutLibraries.Media.SIGNED_16BITS)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		samples = self.wavesGen.deep(f=100, duration=100)
		self.info( samples )

		samples = self.wavesGen.modulation(f=100, duration=100, x=2, y=4)
		samples = self.wavesGen.overload(f=100, duration=100)
		samples = self.wavesGen.ping(f=100, duration=100)
		samples = self.wavesGen.sine(f=100, duration=100)
		samples = self.wavesGen.sonar(f=100, duration=100)
		samples = self.wavesGen.square(f=100, duration=100)
		samples = self.wavesGen.sweep(duration=100)

		self.step1.setPassed(actual="pass")

class WAV_CONTAINER_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.wav = SutLibraries.Media.WavContainer(parent=self, debug=get('DEBUG'), format=1, channels=1, rate=44100, bits=16, samples=[])
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		self.wav.setDataRaw(dataRaw='test')
		
		raw = self.wav.getRaw()
		self.info( raw )
		
		self.step1.setPassed(actual="pass")

class SDP_ENCODE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		sdp1 = """v=0
o=- 3552933831 3552933831 IN IP4 204.62.14.177
s=Blink 0.2.7 (Windows)
c=IN IP4 204.62.14.177
t=0 0
z=2882844526 -1h 2898848070 0
t=3034423619 3042462419
r=604800 3600 0 90000
a=sendrecv
k=base64:AAAAAAAAAAAAAAAA
m=audio 50000 RTP/AVP 9 104 103 102 0 8 101
a=rtcp:50001
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=sendrecv"""

		sdp2 = """v=0
o=jdoe 2890844526 2890842807 IN IP4 10.47.16.5
s=SDP Seminar
i=A Seminar on the session description protocol
u=http://www.example.com/seminars/sdp.pdf
e=j.doe@example.com (Jane Doe)
c=IN IP4 224.2.17.12/127
t=2873397496 2873404696
r=7d 1h 0 25h
a=recvonly
m=audio 49170 RTP/AVP 0
i=test
m=video 51372 RTP/AVP 99
a=rtpmap:99 h263-1998/90000
i=test2
k=base64:bbbbbbbbbb
c=IN IP4 224.2.17.12/127"""

		sdp3 = """v=0
o=RV-MCU 4085834044 4085834044 IN IP4 192.168.11.9
s=RV MCU Session
c=IN IP4 192.168.11.9
b=AS:2048
t=0 0
m=audio 16618 RTP/AVP 119 113 9 112 8 0 101
c=IN IP4 192.168.11.9
a=rtpmap:119 MP4A-LATM/32000
a=fmtp:119 profile-level-id=2;object=2;bitrate=96000
a=rtpmap:113 G7221/32000
a=fmtp:113 bitrate=48000
a=rtpmap:9 G722/8000
a=rtpmap:112 G7221/16000
a=fmtp:112 bitrate=32000
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
a=sendrecv
m=video 12348 RTP/AVP 97 34
c=IN IP4 192.168.11.9
b=TIAS:2048000
a=rtpmap:97 H264/90000
a=fmtp:97 profile-level-id=4DE028
a=rtpmap:34 H263/90000
a=fmtp:34 CIF=1;QCIF=1;CIF4=1
a=sendrecv
m=control 3337 tcp RvMcuNonStandard
c=IN IP4 192.168.11.9
a=fmtp:RvMcuNonStandard Identifier={1 3 6 1 4 1 903 300} Data={1 32 0 0 0 0 0 12 0 1 0 64 0 0 0 0 214 1 45 56}"""

		sdp4 = """v=0
o=CiscoSystemsCCM-SIP 2000 1 IN IP4 10.210.2.200
s=SIP Call
c=IN IP4 10.210.2.40
t=0 0
m=audio 16556 RTP/AVP 9 101
b=TIAS:64000
a=rtpmap:9 G722/8000
a=ptime:20
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
m=video 16558 RTP/AVP 97
b=TIAS:2250000
a=rtpmap:97 H264/90000
a=fmtp:97 profile-level-id=4D0028;sprop-parameter-sets=Z00AKBpZUAoAtyA=,aENuPIA=
a=mid:227796888
m=control 0 tcp 0"""
			
		sdp = SutLibraries.Media.SDP( parent=self, debug=get('DEBUG') ) 
		a = TestAdapter.Adapter(parent=self, name='mtp', debug=False)
		
		sdp_test = sdp.sdpCodec.decode(sdp=sdp1)
		s = TestTemplates.TemplateMessage()
		s.addLayer(layer=sdp_test)
		a.logRecvEvent(shortEvt='sdp test 1', tplEvt=s)
		
		sdp_test = sdp.sdpCodec.decode(sdp=sdp2)
		s = TestTemplates.TemplateMessage()
		s.addLayer(layer=sdp_test)
		a.logRecvEvent(shortEvt='sdp test 2', tplEvt=s)

		sdp_test = sdp.sdpCodec.decode(sdp=sdp3)
		s = TestTemplates.TemplateMessage()
		s.addLayer(layer=sdp_test)
		a.logRecvEvent(shortEvt='sdp test 3', tplEvt=s)

		sdp_test = sdp.sdpCodec.decode(sdp=sdp4)
		s = TestTemplates.TemplateMessage()
		s.addLayer(layer=sdp_test)
		a.logRecvEvent(shortEvt='sdp test 4', tplEvt=s)
		
		self.step1.setPassed(actual="pass")]]></testdefinition>
<testexecution><![CDATA[
CHARTJS_01(suffix=None).execute()
IMAGES_01(suffix=None).execute()
DIALTONES_01(suffix=None).execute()
DIALTONES_02(suffix=None).execute()
NOISE_01(suffix=None).execute()
WAVE_01(suffix=None).execute()
WAV_CONTAINER_01(suffix=None).execute()
SDP_ENCODE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106016.27</testdevelopment>
</file>