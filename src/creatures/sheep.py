from creatures import Creature
import config
from dataclasses import dataclass
import random

@dataclass
class Sheep(Creature):
    energy: float = config.SHEEP_START_ENERGY
    alive: bool = True
    color: str = 'white'
    
    def step_auto(self, world):
        if not self.alive: return
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.move(dx, dy, world.size)