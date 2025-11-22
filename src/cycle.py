from src import World
from src.creatures.human import Human
import numpy as np
from src import config
from src.creatures.wolf import Wolf
from src.creatures.sheep import Sheep
class Cycle:
    def __init__(self):
        self.world = World
        self.world.entity_grid = np.full((self.world.size, self.world.size), None, dtype=object)
        self.human = None
        self.creatures = []
        self.spawn_creature()

    def spawn_creature(self):
        x, y = self.valid_spawn()
        human = Human(id = 999, x=x, y=y, color='black')
        self.creatures.append(self.human)
        self.world.entity_grid[x, y] = self.human

        #spawn owiec 
        for i in range(config.NUM_SHEEP):
            x, y = self.valid_spawn()
            sheep = Sheep(id=i, x=x, y=y, color='white')
            self.creatures.append(sheep)
            self.world.entity_grid[x, y] = sheep
            
        # Spawn wilków
        for i in range(config.NUM_WOLVES):
            x, y = self.valid_spawn()
            wolf = Wolf(id=100+i, x=x, y=y, color='red')
            self.creatures.append(wolf)
            self.world.entity_grid[x, y] = wolf

    #sprawdzenie spnawnu, aby się nie waliły na sibię na raz 
    def valid_spawn(self):
        while True:
            x = np.random.randint(0, self.world.size)
            y = np.random.randint(0, self.world.size)
            if self.world.terrain_grid[x, y] == config.ID_WATER:
                continue
            if self.world.entity_grid[x, y] is not None:
                continue
            return x, y
    
    def update_grid(self):
        self.world.entity_grid.fill(None)
        for creature in self.creatures:
            if creature.alive:
                self.world.entity_grid[creature.y, creature.x] = creature

    def step(self, action_id):
        if not self.human.alive:
            return
        self.human.movement(action_id, self.world, self.creatures)
        self.update_grid()
        self.world.update_world_state()
        if self.human.actions_left <= 0:
            self.end_of_day()

    def end_of_day(self):

        for c in self.creatures:
            if c is self.human or not c.alive:
                continue
            
            #ruch zwirzakow 
            if isinstance(c, Wolf):
                c.movement_random(self.world)
            elif isinstance(c, Sheep):
                c.step_auto(self.world)

        #reset gracza
        self.human.actions_left = config.MAX_ACTIONS_PER_DAY
        self.human.days_alive += 1
        
        #sync do zwierzat 
        self._update_entity_grid()
        
    