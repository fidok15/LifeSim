from creatures import Creature
import config
from dataclasses import dataclass

@dataclass
class Human(Creature):
    hunger: int = 0
    thirsty: int = 0
    temp: float = 36.6
    age: int = 0
    wood_inv: int = 0
    alive: bool = True
    actions_left: int = config.MAX_ACTIONS_PER_DAY

    def movement(self, action_id, world):
        if not self.alive or self.actions_left <= 0:
            return
        
        if action_id == config.ACTION_MOVE_UP:
            self.move(-1, 0, world.size)
        elif action_id == config.ACTION_MOVE_DOWN:
            self.move(1, 0, world.size)
        elif action_id == config.ACTION_MOVE_LEFT:
            self.move(0, -1, world.size)
        elif action_id == config.ACTION_MOVE_RIGHT:
            self.move(0, 1, world.size)

        elif action_id == config.ACTION_INTERACT:
            self._interact_with_environment(world)

        self.actions_left -= 1
        

    def _interact_with_environment(self, world):
        x, y = self.x, self.y
        tile = world.terrain_grid[y, x]

        if tile == config.ID_FOREST:
            gained = world.chop_tree(x, y)
            if gained > 0:
                self.wood_inv += gained

        elif tile == config.ID_CAMPFIRE:
            if self.wood_inv > 0:
                world.campfire_fuel_grid[y, x] += 1
                self.wood_inv -= 1

        elif tile == config.ID_WATER:
            self.thirsty = max(0, self.thirsty - 5)
