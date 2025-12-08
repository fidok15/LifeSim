from src.world.world import World
from src.world.creatures.human import Human
import numpy as np
from src import config as config
from src.world.creatures.wolf import Wolf
from src.world.creatures.sheep import Sheep
from src.world.creatures.knight import Knight
import os
class Cycle:
    def __init__(self):
        # inicjalizacja świata
        self.world = World()
        #inicjalizacja tablicy gdzie będą przechowywane wiadomosci gdzie stoja poszczegulne zwierzeta
        self.world.entity_grid = np.full((self.world.size, self.world.size), None, dtype=object)
        self.human = None
        self.next_entity_id = 0
        # tablica szybkie przejscie przez zywe istoty
        self.creatures = []
        self.spawn_creature()

    #wszystkie jednostki maja unikalne id 
    def get_new_id(self):
        id = self.next_entity_id
        self.next_entity_id += 1
        return id
    
    #pojawienie się jednostke 
    def spawn_creature(self):
        x, y = self.valid_spawn()
        self.human = Human(id=self.get_new_id(), x=x, y=y)
        self.creatures.append(self.human)
        self.world.entity_grid[y, x] = self.human

        #spawn owiec 
        for _ in range(config.NUM_SHEEP):
            x, y = self.valid_spawn()
            sheep = Sheep(id=self.get_new_id(), x=x, y=y)
            self.creatures.append(sheep)
            self.world.entity_grid[y, x] = sheep
            
        # Spawn wilków
        for _ in range(config.NUM_WOLVES):
            x, y = self.valid_spawn()
            wolf = Wolf(id=self.get_new_id(), x=x, y=y)
            self.creatures.append(wolf)
            self.world.entity_grid[y, x] = wolf

        for _ in range(config.NUM_KNIGHTS):
            x, y = self.valid_spawn()
            knight = Knight(id=self.get_new_id(), x=x, y=y)
            self.creatures.append(knight)
            self.world.entity_grid[y, x] = knight

    #sprawdzenie spnawnu, aby się nie waliły na sibię na raz 
    def valid_spawn(self):
        while True:
            x = np.random.randint(0, self.world.size)
            y = np.random.randint(0, self.world.size)
            if self.world.terrain_grid[y, x] == config.ID_WATER:
                continue
            if self.world.entity_grid[y, x] is not None:
                continue
            return x, y
    
    # TODO mozna to zoptymalizować lepiej 
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
        self.world.update_world_tick()
        if self.human.actions_left <= 0:
            self.end_of_day()

    def end_of_day(self):
        self.world.update_world_tick()
        
        for c in self.creatures:
            if c is self.human or not c.alive:
                continue
            
            #ruch zwirzakow 
            if isinstance(c, Wolf):
                c.wolf_move(self.world)
            elif isinstance(c, Sheep):
                c.sheep_move(self.world)
            if isinstance(c, Knight):
                c.knight_move(self.world)

        #reset gracza
        self.human.actions_left = config.MAX_ACTIONS_PER_DAY
    
        #sync do zwierzat 
        self.update_grid()