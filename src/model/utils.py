import gymnasium as gym
import numpy as np
from src import config as config
from cycle import Cycle
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

    def reset(self, seed = config.SEED):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
        self.sim = Cycle()
        return self._observation(), {}
    
    def step(self, action):
        prev_h = self.sim.human
        prev_stats = {'hunger': prev_h.hunger, 'thirsty': prev_h.thirsty, 'temp': prev_h.temp, 'day_alive': prev_h.days_alive}
        self.sim.step(action)

        curent_h = self.sim.human
        obs = self._observation()
        terminated = not self.sim.human.alive
        truncated = False

        reward = 0
        if terminated:
            return obs, -10.0, terminated, truncated, {}
        
        reward += 0.1

        # if curent_h.days_alive > prev_stats['day_alive']:
        #     reward += 10 

        if curent_h.hunger - prev_stats['hunger'] > 0 or curent_h.thirsty - prev_stats['thirsty'] > 0 or (curent_h.temp - prev_stats['temp'] > 0 and prev_stats['temp'] < (config.TEMP_DIE + config.TEMP_MAX) / 2 ):
            reward += 5
            
        
        # if curent_h.hunger < 0.2 * config.HUNGER_MAX: reward -= 0.5
        # if curent_h.thirsty < 0.2 * config.THIRSTY_MAX: reward -= 0.5
        # if curent_h.temp < config.TEMP_DIE + (0.2 * (config.TEMP_MAX - config.TEMP_DIE)) : reward -= 0.5

        return obs, reward, terminated, truncated, {}
    
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