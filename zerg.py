from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units

import random

class ZergAgent(base_agent.BaseAgent):
	def step(self, obs):
		super(ZergAgent, self).step(obs)

		larva_units = [unit for unit in obs.observation.feature_units
		if unit.unit_type == units.Zerg.Larva]

		if len(larva_units) > 0:
			larva_unit = random.choice(larva_units)
			return actions.FUNCTIONS.select_point('select_all_type', (larva_unit.x, larva_unit.y))

		return actions.FUNCTIONS.no_op()
