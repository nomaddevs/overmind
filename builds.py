import sys

build = sys.argv[1]

class BuildStep():
	def __init__(self, supply_target, building):
		super()

		self.supply_target = supply_target
		self.building = building

class BuildOrder():
	def __init__(self, build_file):
		super()

		self.order = []
		
		with open(build_file) as f:
			line = f.readline()
			while line:
				instruction = line.split(',')
				step = BuildStep(instruction[0], instruction[1])
				self.order.append(step)
				line = f.readline()
