import numpy as np
from src import config as config
from src.world import terrain
#zmienne dynamiczne
class World:
    def __init__(self):
        self.size = config.MAP_SIZE
        self.terrain_grid = np.zeros((self.size, self.size), dtype=int)
        self.wood_grid = np.zeros((self.size, self.size), dtype=float)
        self.entity_grid = np.full((self.size, self.size), None, dtype=object)
        self.generate_world()

    def generate_world(self):
        choices = [config.ID_PLAIN, config.ID_FOREST, config.ID_WATER, config.ID_CAMPFIRE]
        weights = [config.PLAIN_AMOUNT, config.FOREST_AMOUNT, config.WATER_AMOUNT, config.CAMPFIRE_AMOUNT]
        self.terrain_grid = np.random.choice(choices, (self.size, self.size), p=weights)

        for y in range(self.size):
            for x in range(self.size):
                terrain_id = self.terrain_grid[y, x]

                if terrain_id == config.ID_FOREST:
                    self.wood_grid[y, x] = np.random.randint(config.WOOD_MIN_SPAWN, config.WOOD_MAX_SPAWN)


    def chop_tree(self, x, y):
        if self.terrain_grid[y, x] != config.ID_FOREST:
            return 0 
        
        if self.wood_grid[y, x] <= 0:
            return 0

        self.wood_grid[y, x] -= 1
        return 1
    
    def add_fuel(self, x, y):
        if self.terrain_grid[y, x] != config.ID_CAMPFIRE:
            return 0
        
        if self.wood_grid[y, x] >= 5:
            return 0

        self.wood_grid[y, x] += 1
        return 1
    
    def update_world_tick(self):
        fires_mask = (self.terrain_grid == config.ID_CAMPFIRE) & (self.wood_grid > 0)
        self.wood_grid[fires_mask] -= 0.1
        self.wood_grid = np.maximum(self.wood_grid, 0)

    def move_creature(self, creature, new_x, new_y):
        self.world.entity_grid[creature.y, creature.x] = None
        creature.x = new_x
        creature.y = new_y
    
        self.world.entity_grid[new_y, new_x] = creature