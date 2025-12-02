from src.world.creatures.creatures import Creature
import src.config as config
from dataclasses import dataclass

@dataclass
class Human(Creature):
    hunger: float = config.HUNGER_MAX
    thirsty: float = config.THIRSTY_MAX
    temp: float = config.TEMP_MAX
    energy: float = config.ENERGY_MAX
    days_alive: int = 0
    wood_inv: int = 0
    alive: bool = True
    actions_left: int = config.MAX_ACTIONS_PER_DAY
    death_cause: str = None

    def movement(self, action_id, world, creatures_list):
        if not self.alive or self.actions_left <= 0:
            return
        
        if self.energy >= config.ENERGY_LOSS_PER_MOVE:
            if action_id == config.ACTION_MOVE_UP:
                self.move(0, -1, world.size)
            elif action_id == config.ACTION_MOVE_DOWN:
                self.move(0, 1, world.size)
            elif action_id == config.ACTION_MOVE_LEFT:
                self.move(-1, 0, world.size)
            elif action_id == config.ACTION_MOVE_RIGHT:
                self.move(1, 0, world.size)
            elif action_id == config.ACTION_STAY:
                self.energy += config.REST_ENERGY_GAIN + config.ENERGY_LOSS_PER_MOVE
            elif action_id == config.ACTION_INTERACT:
                self.interact_with_environment(world, creatures_list)
        else:
            self.energy += config.REST_ENERGY_GAIN + config.ENERGY_LOSS_PER_MOVE
            
        self.colision(world, creatures_list)
        self.update_stats(world)
        self.actions_left -= 1
        

    def interact_with_environment(self, world, creatures_list):
        x, y = self.x, self.y
        tile = world.terrain_grid[y, x]

        if tile == config.ID_FOREST:
            gained = world.chop_tree(x, y)
            # TODO do poprawy
            if gained > 0 and self.wood_inv + gained <= config.MAX_WOOD_INV:
                self.wood_inv += gained
                self.energy -= config.CHOP_TREE_ENERGY_COST
                self.wood_inv = min(self.wood_inv, config.MAX_WOOD_INV)

        elif tile == config.ID_CAMPFIRE:
            if self.wood_inv > 0:
                success = world.add_fuel(x, y)
                if success == 1:
                    self.wood_inv -= 1                  

        elif tile == config.ID_WATER:
            self.thirsty = min(self.thirsty + config.THIRSTY_GAIN, config.THIRSTY_MAX)
            
        for creature in creatures_list:
            if creature is self or not creature.alive:
                continue
            
            if creature.x == x and creature.y == y and type(creature).__name__ == 'Sheep':
                creature.alive = False
                self.hunger += config.SHEEP_HUNGER_GAIN
                self.energy += config.SHEEP_ENERGY_GAIN
                break

    def update_stats(self, world):
        if not self.alive:
            return
            
        x, y = self.x, self.y
        tile_id = world.terrain_grid[y, x]
        fuel_amount = world.wood_grid[y, x]

        is_active_campfire = (tile_id == config.ID_CAMPFIRE and fuel_amount > 0)

        if is_active_campfire:
            self.energy += config.CAMPFIRE_ENERGY_GAIN + config.ENERGY_LOSS_PER_MOVE
            self.temp += config.CAMPFIRE_TEMP_GAIN + config.TEMP_LOSS_PER_MOVE
        else:
            self.temp -= config.TEMP_LOSS_PER_MOVE

        self.temp = max(0, min(self.temp, config.TEMP_MAX))
        self.thirsty -= config.THIRSTY_LOSS_PER_MOVE
        self.thirsty = max(0, min(self.thirsty, config.THIRSTY_MAX))
        self.energy -= config.ENERGY_LOSS_PER_MOVE
        self.energy = max(0, min(self.energy, config.ENERGY_MAX))
        self.hunger -= config.HUNGER_LOSS_PER_MOVE
        self.hunger = max(0, min(self.hunger, config.HUNGER_MAX))        
        
        if self.temp <= config.TEMP_DIE:
            self.alive = False
            self.death_cause = "temperatura"
            return
        
        if self.thirsty <= config.THIRSTY_DIE:
            self.alive = False
            self.death_cause = "picie"
            return

        if self.hunger <= config.HUNGER_DIE:
            self.alive = False
            self.death_cause = "jedzenie"
            return
        
    def colision(self, world, creature_list):
        for creature in creature_list:
            if creature is self or not creature.alive:
                continue
            
            if creature.x == self.x and creature.y == self.y:
                if type(creature).__name__ == 'Wolf':
                    if self.energy > creature.energy:
                        creature.alive = False
                        self.energy += config.COMBAT_WOLF_ENERGY_GAIN
                        self.hunger += config.COMBAT_WOLF_HUNGER_GAIN
                    else:
                        self.alive = False
                        self.death_cause = 'wilczek'
                        return
                    
            if creature.x == self.x and creature.y == self.y:
                if type(creature).__name__ == 'Knight':
                    if self.energy > creature.energy:
                        creature.alive = False
                        self.energy += config.COMBAT_KNIGHT_ENERGY_GAIN
                        self.hunger += config.COMBAT_KNIGHT_HUNGER_GAIN
                    else:
                        self.alive = False
                        self.death_cause = 'rycerz'
                        return        
                    
    def new_day(self):
        self.actions_left = config.MAX_ACTIONS_PER_DAY



