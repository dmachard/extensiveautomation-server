
class TESTCASE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		# adapters and libraries
		pass
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
	def cleanup(self, aborted):
		pass
