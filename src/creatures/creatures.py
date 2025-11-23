from dataclasses import dataclass
import random
from src import config as config

@dataclass
class Creature:
    id: int
    x: int
    y: int

    def move(self, dx, dy, world_size):
        new_x = max(0, min(self.x + dx, world_size - 1))
        new_y = max(0, min(self.y + dy, world_size - 1))
        self.x = new_x
        self.y = new_y

    