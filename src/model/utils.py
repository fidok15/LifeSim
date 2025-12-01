import gymnasium as gym
import numpy as np
from src import config as config
from cycle import Cycle
from collections import deque
class SurvivalEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.sim = Cycle()
        self.view_range = config.MODEL_VIEW // 2
        self.max_terrain_id = max(config.ID_PLAIN, config.ID_FOREST, config.ID_WATER, config.ID_CAMPFIRE)
        self.observation_space = gym.spaces.Tuple((
            gym.spaces.Box(low=0, high=1, shape=(5, config.MODEL_VIEW, config.MODEL_VIEW), dtype=np.float32),
            gym.spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)
        ))
        self.action_space = gym.spaces.Discrete(6)
        self.recent_positions = deque(maxlen=20) 
        self.steps_without_moving = 0

    def reset(self, seed = config.SEED):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
        self.sim = Cycle()
        self.recent_positions.clear()
        self.steps_without_moving = 0
        return self._observation(), {}
    
    def step(self, action):
        prev_h = self.sim.human
        prev_stats = {'hunger': prev_h.hunger, 'thirsty': prev_h.thirsty, 'temp': prev_h.temp, 'wood_inv': prev_h.wood_inv}
        prev_pos = (prev_h.x, prev_h.y)
        self.sim.step(action)

        curent_h = self.sim.human
        obs = self._observation()
        terminated = not self.sim.human.alive
        truncated = False

        info = {}

        reward = 0
        if terminated:
            info['death_cause'] = getattr(curent_h, 'death_cause', 'unknown')
            return obs, -50.0, terminated, truncated, info
        
        reward += 0.1
        curr_pos = (curent_h.x, curent_h.y)
        
        is_safe_temp = curent_h.temp > config.TEMP_MAX * 0.4
        is_safe_energy = curent_h.energy > config.ENERGY_MAX * 0.4

        if curr_pos == prev_pos:
            self.steps_without_moving += 1
            if self.steps_without_moving > 3:
                reward -= 1.0
        else:
            self.steps_without_moving = 0
            if curr_pos not in self.recent_positions:
                reward += 0.5 
                self.recent_positions.append(curr_pos)

        if curent_h.thirsty > prev_stats['thirsty']:
            if prev_stats['thirsty'] < config.THIRSTY_MAX * 0.2:
                reward += 5.0
            else:
                reward += 0.0
        
        if curent_h.hunger > prev_stats['hunger']:
            if prev_stats['hunger'] < config.HUNGER_MAX * 0.2:
                reward += 5.0
            else:
                reward += 0.0
        
        if curent_h.wood_inv > prev_stats['wood_inv']:
            if prev_stats['wood_inv'] < 3:
                reward += 2.0
            else:
                reward += 0.5

        
        if curent_h.wood_inv < prev_stats['wood_inv']:
            x, y = curent_h.x, curent_h.y
            if self.sim.world.terrain_grid[y, x] == config.ID_CAMPFIRE:
                reward += 10.0
                if not is_safe_temp:
                    reward += 5.0
        
        if curent_h.temp > prev_stats['temp']:
            if prev_stats['temp'] < config.TEMP_MAX * 0.5:
                # Bardzo duża nagroda za ogrzewanie się, gdy jesteśmy zmarznięci
                reward += 3.0
            else:
                reward += 0.5
        
        if curent_h.hunger < config.HUNGER_MAX * 0.2:
            reward -= 0.5
        
        if curent_h.temp < config.TEMP_MAX * 0.2:
            reward -= 1.0

        # if curent_h.days_alive > prev_stats['day_alive']:
        #     reward += 10 

        # if curent_h.hunger - prev_stats['hunger'] > 0 or curent_h.thirsty - prev_stats['thirsty'] > 0 or (curent_h.temp - prev_stats['temp'] > 0 and prev_stats['temp'] < (config.TEMP_DIE + config.TEMP_MAX) / 2 ):
        #     reward += 5
            
        # nie mozna go karac za bycie w zlym stanie bo dostaje depresi i chce sie zabic
        # if curent_h.hunger < 0.2 * config.HUNGER_MAX: reward -= 0.5
        # if curent_h.thirsty < 0.2 * config.THIRSTY_MAX: reward -= 0.5
        # if curent_h.temp < config.TEMP_DIE + (0.2 * (config.TEMP_MAX - config.TEMP_DIE)) : reward -= 0.5

        return obs, reward, terminated, truncated, info
    
    def _observation(self):
        h = self.sim.human
        w = self.sim.world
        size = w.size
        view = np.zeros((5, config.MODEL_VIEW, config.MODEL_VIEW), dtype=np.float32)
        start_y, end_y = h.y - self.view_range, h.y + self.view_range + 1
        start_x, end_x = h.x - self.view_range, h.x + self.view_range + 1
        for i, y in enumerate(range(start_y, end_y)):
            for j, x in enumerate(range(start_x,end_x)):
                if 0 <= y < size and 0 <= x < size:
                    #teren
                    view[0, i, j] = w.terrain_grid[y, x] / self.max_terrain_id
                    #drewno
                    view[1,i,j] = w.wood_grid[y,x] / config.WOOD_MAX_SPAWN
                    #creature 
                    ent = w.entity_grid[y, x]
                    if ent:
                        name = type(ent).__name__
                        if name == 'Wolf':
                            view[2, i, j] = 1.0
                        elif name == 'Sheep':
                            view[3, i, j] = 1.0
                        elif name == 'Knight':
                            view[4, i, j] = 1.0
                else:
                    pass
        stats = np.array([
            h.hunger / config.HUNGER_MAX,
            h.thirsty / config.THIRSTY_MAX,
            h.temp / config.TEMP_MAX,
            h.energy / config.ENERGY_MAX,
            h.wood_inv / config.MAX_WOOD_INV
        ], dtype=np.float32)

        return (view, stats)