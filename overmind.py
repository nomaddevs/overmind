import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import HATCHERY, LARVA, DRONE, OVERLORD, EXTRACTOR, SPAWNINGPOOL, ZERGLING, ROACHWARREN, ROACH

import numpy
import random

overmindVersion = "0.0.1"

class Overmind(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 70

    async def on_step(self, iteration):
        self.iteration = iteration
        if iteration == 0:
            await self.chat_send("Overmind: Alpha Build {}".format(overmindVersion))
        await self.distribute_workers()
        await self.build_workers()
        await self.build_overlords()
        await self.build_extractors()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def intel(self):
        game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)
        for hatch in self.units(HATCHERY):
            hatch_pos = hatch.position
            print(hatch_pos)
            cv2.circle(game_data, (int(hatch_pos[0]), int(hatch_pos[1])), 10, (0, 255, 0), -1)  # BGR

        flipped = cv2.flip(game_data, 0)
        resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)

        cv2.imshow('Intel', resized)
        cv2.waitKey(1)

    async def build_workers(self):
        if (len(self.units(HATCHERY)) * 16) > len(self.units(DRONE)) and len(self.units(DRONE)) < self.MAX_WORKERS:
            for larvae in self.units(LARVA):#.ready.noqueue:
                if self.can_afford(DRONE):
                    await self.do(larvae.train(DRONE))

    async def build_overlords(self):
        if self.supply_left < 5 and not self.already_pending(OVERLORD):
            for larvae in self.units(LARVA):
                if self.can_afford(OVERLORD):
                    await self.do(larvae.train(OVERLORD))

    async def build_extractors(self):
        for hatch in self.units(HATCHERY).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, hatch)
            for vespene in vaspenes:
                if not self.can_afford(EXTRACTOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                if not self.units(EXTRACTOR).closer_than(1.0, vespene).exists:
                    await self.do(worker.build(EXTRACTOR, vespene))

    async def expand(self):
        if self.units(HATCHERY).amount < (self.iteration / self.ITERATIONS_PER_MINUTE) and self.can_afford(HATCHERY):
            await self.expand_now()

    async def offensive_force_buildings(self):
        hatches = self.units(HATCHERY).ready
        if hatches.exists:
            if self.units(SPAWNINGPOOL).ready.exists and not self.units(ROACHWARREN):
                if self.can_afford(ROACHWARREN) and not self.already_pending(ROACHWARREN):
                    await self.build(ROACHWARREN, near=hatches.first)
        
            elif len(self.units(SPAWNINGPOOL)) < 1:
                if self.can_afford(SPAWNINGPOOL) and not self.already_pending(SPAWNINGPOOL):
                    await self.build(SPAWNINGPOOL, near=hatches.first)
    
    async def build_offensive_force(self):
        larvae = self.units(LARVA)
        if larvae.exists and self.supply_left > 0:
            if self.can_afford(ZERGLING) and self.units(SPAWNINGPOOL).ready.exists:
                await self.do(larvae.random.train(ZERGLING))
            if self.can_afford(ROACH) and self.units(ROACHWARREN).ready.exists:
                await self.do(larvae.random.train(ROACH))

#            if not self.units(ROACH).amount > self.units(ZERGLING).amount:
#                if self.can_afford(ROACH) and self.supply_left > 0:
#                    await self.do(larvae.train(ROACH))
#            if self.can_afford(ZERGLING) and self.supply_left > 0:
#                await self.do(larvae.train(ZERGLING))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        aggressive_units = {
            ZERGLING: [15, 5],
            ROACH: [8, 3]
        }
        # {UNIT: [n to fight, n to defend]}
        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, Overmind()),
    Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=False)

# from pysc2.agents import base_agent
# from pysc2.env import sc2_env
# from pysc2.lib import actions, features, units
# 
# import numpy
# import random
# 
# class zerg(base_agent.BaseAgent):
# 	def __init__(self):
# 		super(zerg, self).__init__()
# 
# 		self.attack_coordinates = None
# 		self.bases = 1
# 		self.overlord_count = 1
# 		self.drone_count = 12
# 		self.stepchoices = {
# 			0: self.macro,
# 			1: self.scout
# 		}
# 		self.train_data = []
# 
# 	def is_selected(self, obs, unit_type):
# 		if(len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type):
# 			return True
# 		if(len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type):
# 			return True
# 		return False
# 
# 	def get_units_by_type(self, obs, unit_type):
# 		return [unit for unit in obs.observation.feature_units if unit.unit_type == unit_type]
# 
# 	def can_do(self, obs, action):
# 		return action in obs.observation.available_actions
# 
# 	def available_supply(self, obs):
# 		return obs.observation.player.food_cap - obs.observation.player.food_used
# 
# 	def free_supply(self, obs):
# 		return obs.observation.player.food_cap - obs.observation.player.food_used
# 
# 	def macro(self, obs):
# 		if self.is_selected(obs, units.Zerg.Larva):
# 			if self.free_supply(obs) <= 2:
# 				if self.can_do(obs, actions.FUNCTIONS.Train_Overlord_quick.id):
# 					return actions.FUNCTIONS.Train_Overlord_quick('now')
# 			if self.can_do(obs, actions.FUNCTIONS.Train_Drone_quick.id):
# 				return actions.FUNCTIONS.Train_Drone_quick('now')
# 
# 		larva_units = self.get_units_by_type(obs, units.Zerg.Larva)
# 
# 		if len(larva_units) > 0:
# 			larva_unit = random.choice(larva_units)
# 			return actions.FUNCTIONS.select_point('select_all_type', (larva_unit.x, larva_unit.y))
# 
# 		return actions.FUNCTIONS.no_op()
# 
# 	def scout(self, obs):
# 		overlords = self.get_units_by_type(obs, units.Zerg.Overlord)
# 		if len(overlords) > 0:
# 			if self.is_selected(obs, units.Zerg.Overlord):
# 				if self.can_do(obs, actions.FUNCTIONS.Move_minimap.id):
# 					x = random.randint(0, 63)
# 					y = random.randint(0, 63)
# 					return actions.FUNCTIONS.Move_minimap('now', (x, y))
# 		return actions.FUNCTIONS.no_op()
# 
# 	def skip_step(self, obs):
# 		return actions.FUNCTIONS.no_op()
# 
# 	def step(self, obs):
# 		super(zerg, self).step(obs)
# 
# 		if obs.first():
# 			player_y, player_x = (obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
# 			xmean = player_x.mean()
# 			ymean = player_y.mean()
#  	
# 			if xmean <= 31 and ymean <= 31:
# 				self.attack_coordinates = (47, 47)
# 			else:
# 				self.attack_coordinates = (12, 16)
# 
# 		choice = random.randint(0, len(self.stepchoices))
# 
# 		decision_data = numpy.zeros(len(self.stepchoices))
# 		decision_data[choice] = 1
# 		print(decision_data)
# 		self.train_data.append([y, ])
# 
# 		func = self.stepchoices.get(choice, self.skip_step)
# 
# 		return func(obs)
# 