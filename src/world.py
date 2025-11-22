import numpy as np
from . import config
from . import terrain
#zmienne dynamiczne
class World:
    def __init__(self):
        self.size = config.MAP_SIZE
        self.terrain_grid = np.zeros((self.size, self.size), dtype=int)
        self.tree_amount_grid = np.zeros((self.size, self.size), dtype=float)
        self.campfire_fuel_grid = np.zeros((self.size, self.size), dtype=float)
        self.generate_world()

    def generate_world(self):
        choices = [config.ID_PLAIN, config.ID_FOREST, config.ID_WATER, config.ID_CAMPFIRE]
        weights = [config.PLAIN_AMOUNT, config.FOREST_AMOUNT, config.WATER_AMOUNT, config.CAMPFIRE_AMOUNT]
        self.terrain_grid = np.random.choice(choices, (self.size, self.size), p=weights)

        for y in range(self.size):
            for x in range(self.size):
                terrain_id = self.terrain_grid[x, y]

                if terrain_id == config.ID_FOREST:
                    self.tree_amount_grid[x, y] = np.random.randint(3, 10)
                elif terrain_id == config.ID_CAMPFIRE:
                    self.campfire_fuel_grid[x, y] = np.random.uniform(1.0, 3.0)

    def chop_tree(self, x, y):
        if self.terrain_grid[x, y] != config.ID_FOREST:
            return 0 
        
        if self.tree_amount_grid[x, y] <= 0:
            return 0

        self.tree_amount_grid[x, y] -= 1
        return 1