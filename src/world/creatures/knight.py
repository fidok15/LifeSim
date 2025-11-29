from src.world.creatures.creatures import Creature
import src.config as config
from dataclasses import dataclass
import random

@dataclass
class Knight(Creature):
    energy: float = config.KNIGHT_START_ENERGY
    alive: bool = True

    def wolf_move(self, world):
        if not self.alive: return
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.move(dx, dy, world.size)