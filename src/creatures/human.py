from creatures import Creature
import config
from dataclasses import dataclass

@dataclass
class Human(Creature):
    hunger: float = 20.0
    thirsty: float = 20.0
    temp: float = 36.6
    energy: float = 100
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
        elif action_id == config.ACTION_STAY:
            self.energy = min(self.energy + 2, 100)
        elif action_id == config.ACTION_INTERACT:
            self.interact_with_environment(world)

        self.update_stats(world)
        self.actions_left -= 1
        

    def interact_with_environment(self, world):
        x, y = self.x, self.y
        tile = world.terrain_grid[x, y]

        if tile == config.ID_FOREST:
            gained = world.chop_tree(x, y)
            if gained > 0 and self.wood_inv < config.MAX_WOOD_INV:
                self.wood_inv += gained
                self.wood_inv = min(self.wood_inv, config.MAX_WOOD_INV)

        elif tile == config.ID_CAMPFIRE:
            if self.wood_inv > 0:
                world.campfire_fuel_grid[x, y] += 1
                self.wood_inv -= 1

        elif tile == config.ID_WATER:
            self.thirsty = min(self.thirsty + 10, 20)

    def update_stats(self, world):
        if not self.alive:
            return
            
        x, y = self.x, self.y
        tile_id = world.terrain_grid[x, y]
        fuel_amount = world.campfire_fuel_grid[x, y]

        is_active_campfire = (tile_id == config.ID_CAMPFIRE and fuel_amount > 0)

        if is_active_campfire:
            self.energy += 5
            self.temp += 1
            world.campfire_fuel_grid[x, y] = max(0, fuel_amount - 0.1) 
        else:
            self.temp -= config.TEMP_DOWN

        self.energy = min(self.energy, 100)
        self.temp = min(self.temp, 37.0)
        self.thirsty -= 0.1
        self.thirsty = min(self.thirsty, 20.0)

        if self.temp <= 34.0 or self.thirsty <= 0.01:
            self.alive = False
            return
        


