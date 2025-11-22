from src.creatures.creatures import Creature
import src.config as config
from dataclasses import dataclass
import random

@dataclass
class Wolf(Creature):
    energy: float = config.WOLF_START_ENERGY
    alive: bool = True
    color: str = 'red'

    def wolf_move(self, world):
        if not self.alive: return
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.move(dx, dy, world.size)