from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units

import numpy
import random

class zerg(base_agent.BaseAgent):
	def __init__(self):
		super(zerg, self).__init__()

		self.attack_coordinates = None
		self.bases = 1
		self.overlord_count = 1
		self.drone_count = 12
		self.stepchoices = {
			0: self.macro,
			1: self.scout
		}

	def is_selected(self, obs, unit_type):
		if(len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type):
			return True
		if(len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type):
			return True
		return False

	def get_units_by_type(self, obs, unit_type):
		return [unit for unit in obs.observation.feature_units if unit.unit_type == unit_type]

	def can_do(self, obs, action):
		return action in obs.observation.available_actions

	def available_supply(self, obs):
		return obs.observation.player.food_cap - obs.observation.player.food_used

	def free_supply(self, obs):
		return obs.observation.player.food_cap - obs.observation.player.food_used

	def macro(self, obs):
		if self.is_selected(obs, units.Zerg.Larva):
			if self.free_supply(obs) <= 2:
				if self.can_do(obs, actions.FUNCTIONS.Train_Overlord_quick.id):
					return actions.FUNCTIONS.Train_Overlord_quick('now')
			if self.can_do(obs, actions.FUNCTIONS.Train_Drone_quick.id):
				return actions.FUNCTIONS.Train_Drone_quick('now')

		larva_units = self.get_units_by_type(obs, units.Zerg.Larva)

		if len(larva_units) > 0:
			larva_unit = random.choice(larva_units)
			return actions.FUNCTIONS.select_point('select_all_type', (larva_unit.x, larva_unit.y))

		return actions.FUNCTIONS.no_op()

	def scout(self, obs):
		overlords = self.get_units_by_type(obs, units.Zerg.Overlord)
		if len(overlords) > 0:
			if self.is_selected(obs, units.Zerg.Overlord):
				if self.can_do(obs, actions.FUNCTIONS.Move_minimap.id):
					x = random.randint(0, 63)
					y = random.randint(0, 63)
					return actions.FUNCTIONS.Move_minimap('now', (x, y))
		return actions.FUNCTIONS.no_op()

	def skip_step(self, obs):
		return actions.FUNCTIONS.no_op()

	def step(self, obs):
		super(zerg, self).step(obs)

		if obs.first():
			player_y, player_x = (obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
			xmean = player_x.mean()
			ymean = player_y.mean()
 	
			if xmean <= 31 and ymean <= 31:
				self.attack_coordinates = (47, 47)
			else:
				self.attack_coordinates = (12, 16)

		choice = random.randint(0, len(self.stepchoices))

		func = self.stepchoices.get(choice, self.skip_step)

		return func(obs)
