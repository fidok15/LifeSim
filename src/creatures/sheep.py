from creatures import Creature
import config
from dataclasses import dataclass
import random

@dataclass
class Sheep(Creature):
    color: str = 'white'
    
    def step_auto(self, world):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.move(dx, dy, world.size)