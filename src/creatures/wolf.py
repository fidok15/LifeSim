from creatures import Creature
import config
from dataclasses import dataclass
import random

@dataclass
class Wolf(Creature):
    energy: float = 10.0
    color: str = 'red'

    def movement_random(self, word):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.move(dx, dy, word.size)