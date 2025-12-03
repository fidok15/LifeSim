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
        self.observation_space = gym.spaces.Tuple((
            gym.spaces.Box(low=0, high=1, shape=(8, config.MODEL_VIEW, config.MODEL_VIEW), dtype=np.float32),
            gym.spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)
        ))
        self.action_space = gym.spaces.Discrete(6)
        
        self.recent_positions = deque(maxlen=20)
        self.steps_without_moving = 0

    def reset(self, seed=config.SEED):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
        self.sim = Cycle()
        self.recent_positions.clear()
        self.steps_without_moving = 0
        self.visited_mask = np.zeros((config.MAP_SIZE, config.MAP_SIZE), dtype=bool)
        self.visited_mask[self.sim.human.y, self.sim.human.x] = True
        return self._observation(), {}

    def step(self, action):
        prev_h = self.sim.human
        
        # 1. GPS PRZED RUCHEM
        target_id = config.ID_FOREST if prev_h.wood_inv == 0 else config.ID_CAMPFIRE
        dist_before = self._get_distance_to_nearest(target_id, prev_h.x, prev_h.y)

        prev_stats = {
            'hunger': float(prev_h.hunger), 'thirsty': float(prev_h.thirsty),
            'temp': float(prev_h.temp), 'energy': float(prev_h.energy),
            'wood': int(prev_h.wood_inv), 'x': int(prev_h.x), 'y': int(prev_h.y)
        }
        target_x, target_y = prev_h.x, prev_h.y
        if action == config.ACTION_MOVE_UP: target_y -= 1
        elif action == config.ACTION_MOVE_DOWN: target_y += 1
        elif action == config.ACTION_MOVE_LEFT: target_x -= 1
        elif action == config.ACTION_MOVE_RIGHT: target_x += 1
        
        target_enemy_type = None
        # Sprawdzamy, czy w granicach mapy na polu docelowym stoi wróg
        if 0 <= target_x < config.MAP_SIZE and 0 <= target_y < config.MAP_SIZE:
            entity = self.sim.world.entity_grid[target_y, target_x]
            if entity:
                target_enemy_type = type(entity).__name__

        # 2. Wykonaj ruch
        self.sim.step(action)
        
        # 3. GPS PO RUCHU
        current_h = self.sim.human
        obs = self._observation()
        dist_after = self._get_distance_to_nearest(target_id, current_h.x, current_h.y)
        
        terminated = not current_h.alive
        truncated = False 
        info = {}
        reward = 0.0

        if terminated:
            info['death_cause'] = getattr(current_h, 'death_cause', 'unknown')
            if info['death_cause'] == "temperatura":
                return obs, -100.0, terminated, truncated, info
            return obs, -50.0, terminated, truncated, info

        # --- A. GPS: NAGRODA ZA ZBLIŻANIE SIĘ DO CELU ---
        if (current_h.x, current_h.y) != (prev_stats['x'], prev_stats['y']):
            diff = dist_before - dist_after
            if diff > 0: reward += 1.0   # Idziesz dobrze
            elif diff < 0: reward -= 1.5 # Idziesz źle

        # --- B. OGNISKO (Naprawiona logika) ---
        wood_used = prev_stats['wood'] - current_h.wood_inv
        is_on_campfire = (self.sim.world.terrain_grid[current_h.y, current_h.x] == config.ID_CAMPFIRE)
        
        # Jeśli rozpalił ogień (zużył drewno na polu ogniska)
        if is_on_campfire and wood_used > 0:
            reward += 30.0 # Wielka nagroda

        # Jeśli grzeje się przy ogniu
        is_fire_burning = self.sim.world.wood_grid[current_h.y, current_h.x] > 0
        if is_on_campfire and is_fire_burning and current_h.temp < config.TEMP_MAX * 0.9:
            reward += 3.0

        # Drewno
        if current_h.wood_inv > prev_stats['wood']:
            reward += 5.0

        # --- C. EKSPLORACJA I ZATRZYMYWANIE SIĘ (TU BYŁ BŁĄD) ---
        curr_pos = (current_h.x, current_h.y)
        prev_pos = (prev_stats['x'], prev_stats['y'])

        if current_h.x == target_x and current_h.y == target_y:
            if target_enemy_type == 'Knight':
                reward += 50.0  # Bardzo duża nagroda (trudny przeciwnik)
            elif target_enemy_type == 'Wolf':
                reward += 15.0  # Średnia nagroda
            elif target_enemy_type == 'Sheep':
                # Opcjonalnie: Za owcę już masz nagrodę w statystykach (jedzenie), 
                # ale możesz dodać mały bonus za sam fakt upolowania.
                reward += 5.0
        if curr_pos == prev_pos:
            self.steps_without_moving += 1
            allowed_to_camp = False
            
            # Odpoczynek (energia)
            if current_h.energy < config.ENERGY_MAX * 0.4: allowed_to_camp = True
            
            # Ognisko (ciepło) - TU BYŁ BŁĄD
            if is_on_campfire:
                # Pozwól stać, jeśli ogień płonie
                if is_fire_burning and current_h.temp < config.TEMP_MAX * 0.95: 
                    allowed_to_camp = True
                # WAŻNE: Pozwól stać, jeśli ogień ZGASŁ, ale masz drewno (żebyś mógł go rozpalić!)
                if not is_fire_burning and current_h.wood_inv > 0:
                    allowed_to_camp = True 

            if not allowed_to_camp:
                reward -= 1.0 * self.steps_without_moving
        else:
            self.steps_without_moving = 0
            if not self.visited_mask[current_h.y, current_h.x]:
                reward += 0.5
                self.visited_mask[current_h.y, current_h.x] = True
            if curr_pos in self.recent_positions:
                reward -= 0.5
            self.recent_positions.append(curr_pos)

        # Mała nagroda za przeżycie
        reward += 0.1

        return obs, reward, terminated, truncated, info

    def _observation(self):
        h = self.sim.human
        w = self.sim.world
        size = w.size
        view = np.zeros((8, config.MODEL_VIEW, config.MODEL_VIEW), dtype=np.float32)
        start_y, end_y = h.y - self.view_range, h.y + self.view_range + 1
        start_x, end_x = h.x - self.view_range, h.x + self.view_range + 1
        for i, y in enumerate(range(start_y, end_y)):
            for j, x in enumerate(range(start_x,end_x)):
                if 0 <= y < size and 0 <= x < size:
                    t_id = w.terrain_grid[y, x]
                    if t_id == config.ID_FOREST: view[0, i, j] = 1.0
                    elif t_id == config.ID_CAMPFIRE: view[1, i, j] = 1.0
                    elif t_id == config.ID_WATER: view[2, i, j] = 1.0
                    elif t_id == config.ID_PLAIN: view[3, i, j] = 1.0
                    view[4,i,j] = w.wood_grid[y,x] / config.WOOD_MAX_SPAWN
                    ent = w.entity_grid[y, x]
                    if ent:
                        name = type(ent).__name__
                        if name == 'Wolf': view[5, i, j] = 1.0
                        elif name == 'Sheep': view[6, i, j] = 1.0
                        elif name == 'Knight': view[7, i, j] = 1.0
        
        temp_norm = (h.temp - config.TEMP_DIE) / (config.TEMP_MAX - config.TEMP_DIE)
        temp_norm = np.clip(temp_norm, 0.0, 1.0)
        stats = np.array([
            h.hunger / config.HUNGER_MAX,
            h.thirsty / config.THIRSTY_MAX,
            temp_norm,
            h.energy / config.ENERGY_MAX,
            h.wood_inv / config.MAX_WOOD_INV
        ], dtype=np.float32)
        return (view, stats)