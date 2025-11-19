import numpy as np
from . import config
from . import terrain
#zmienne dynamiczne
class World:
    def __init__(self):
        self.size = config.MAP_SIZE
        self.terrain_grid = np.zeros((self.size, self.size), dtype=int)
        self.tree_ammount_grid = np.zeros((self.size, self.size), dtype=float)
        self.campfire_fuel_grid = np.zeros((self.size, self.size), dtype=float)
        self.generate_world()

    def generate_world(self):
        choices = [config.ID_PLAIN, config.ID_FOREST, config.ID_WATER, config.ID_CAMPFIRE]
        weights = [config.PLAIN_AMMOUNT, config.FOREST_AMMOUNT, config.WATER_AMMOUNT, config.CAMPFIRE_AMMOUNT]
        self.terrain_grid = np.random.choice(choices, (self.size, self.size), p=weights)