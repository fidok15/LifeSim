from src.world import World
from src.creatures.human import Human
import numpy as np
from src import config as config
from src.creatures.wolf import Wolf
from src.creatures.sheep import Sheep
from src.creatures.knight import Knight
import os
class Cycle:
    def __init__(self):
        self.world = World()
        self.world.entity_grid = np.full((self.world.size, self.world.size), None, dtype=object)
        self.human = None
        self.creatures = []
        self.spawn_creature()

    def spawn_creature(self):
        x, y = self.valid_spawn()
        self.human = Human(id = 999, x=x, y=y)
        self.creatures.append(self.human)
        self.world.entity_grid[y, x] = self.human

        #spawn owiec 
        for i in range(config.NUM_SHEEP):
            x, y = self.valid_spawn()
            sheep = Sheep(id=i, x=x, y=y)
            self.creatures.append(sheep)
            self.world.entity_grid[y, x] = sheep
            
        # Spawn wilków
        for i in range(config.NUM_WOLVES):
            x, y = self.valid_spawn()
            wolf = Wolf(id=100+i, x=x, y=y)
            self.creatures.append(wolf)
            self.world.entity_grid[y, x] = wolf

    #sprawdzenie spnawnu, aby się nie waliły na sibię na raz 
    def valid_spawn(self):
        while True:
            x = np.random.randint(0, self.world.size)
            y = np.random.randint(0, self.world.size)
            if self.world.terrain_grid[y, x] == config.ID_WATER:
                continue
            if self.world.entity_grid[y, x] is not None:
                continue
            return x, y
    
    def update_grid(self):
        self.world.entity_grid.fill(None)
        for creature in self.creatures:
            if creature.alive:
                self.world.entity_grid[creature.y, creature.x] = creature

    def step(self, action_id):
        if not self.human.alive:
            return
        self.human.movement(action_id, self.world, self.creatures)
        self.update_grid()
        self.world.update_world_tick()
        if self.human.actions_left <= 0:
            self.end_of_day()

    def end_of_day(self):
        self.world.update_world_tick()
        
        for c in self.creatures:
            if c is self.human or not c.alive:
                continue
            
            #ruch zwirzakow 
            if isinstance(c, Wolf):
                c.wolf_move(self.world)
            elif isinstance(c, Sheep):
                c.sheep_move(self.world)

        #reset gracza
        self.human.actions_left = config.MAX_ACTIONS_PER_DAY
        self.human.days_alive += 1
        
        #sync do zwierzat 
        self.update_grid()

#quick mapka z chata potem TODO zorbic to dobrze nie od ch
def print_map(sim):
    """Rysuje mapę w konsoli używając kodów ASCII/Emoji"""
    os.system('cls' if os.name == 'nt' else 'clear') # Czyść ekran
    
    h = sim.human
    print(f"Dzień: {h.days_alive} | Akcje: {h.actions_left}/{config.MAX_ACTIONS_PER_DAY}")
    print(f"Zdrowie (Alive): {h.alive} | Energia: {h.energy:.1f} | Głód: {h.hunger:.1f} | Pragnienie: {h.thirsty:.1f}")
    print(f"Temp: {h.temp:.1f}°C | Drewno: {h.wood_inv}")
    print("-" * (sim.world.size + 2))

    # Prosty renderer wycinka mapy (żeby nie spamować całej konsoli przy dużej mapie)
    # Pokazuje np. 10x10 kratek wokół gracza
    view_range = 5
    start_y = max(0, h.y - view_range)
    end_y = min(sim.world.size, h.y + view_range + 1)
    start_x = max(0, h.x - view_range)
    end_x = min(sim.world.size, h.x + view_range + 1)

    for y in range(start_y, end_y):
        line = ""
        for x in range(start_x, end_x):
            # 1. Sprawdź czy jest tu jakaś istota
            entity = sim.world.entity_grid[y, x]
            
            if entity:
                if isinstance(entity, Human): char = "🤠"
                elif isinstance(entity, Wolf): char = "🐺"
                elif isinstance(entity, Sheep): char = "🐑"
                elif isinstance(entity, Knight): char = "🤺"
                else: char = "?"
            else:
                # 2. Jeśli pusto, rysuj teren
                terrain = sim.world.terrain_grid[y, x]
                if terrain == config.ID_WATER: char = "🟦"
                elif terrain == config.ID_FOREST: 
                    # Jeśli las ma drzewa vs ścięty
                    if sim.world.wood_grid[y, x] > 0: char = "🌲"
                    else: char = "🟫" # Pniaki
                elif terrain == config.ID_CAMPFIRE:
                    if sim.world.wood_grid[y, x] > 0: char = "🔥"
                    else: char = "🌑" # Zgaszone
                else: char = "🟩" # Równina
            
            line += char
        print(line)
    print("-" * (sim.world.size + 2))
    print("STEROWANIE: [W,A,S,D] - Ruch, [F] - stój w miejscu, [E] - Interakcja (Picie/Rąbanie/Palenie), [Q] - Wyjście")

# --- GŁÓWNY PROGRAM ---

if __name__ == "__main__":
    # 1. Inicjalizacja Symulacji
    sim = Cycle()

    # 2. Pętla Gry (To w przyszłości zastąpi pętla ucząca RL)
    while sim.human.alive:
        try:
            # Wyświetl stan
            print_map(sim)
            
            # Pobierz input od użytkownika
            key = input("Twoja akcja: ").upper()
            
            action = None
            if key == 'W': action = config.ACTION_MOVE_UP
            elif key == 'S': action = config.ACTION_MOVE_DOWN
            elif key == 'A': action = config.ACTION_MOVE_LEFT
            elif key == 'D': action = config.ACTION_MOVE_RIGHT
            elif key == 'E': action = config.ACTION_INTERACT
            elif key == 'F': action = config.ACTION_STAY
            elif key == 'Q': 
                print("Koniec gry.")
                break
            
            if action is not None:
                sim.step(action)
            
        except KeyboardInterrupt:
            break

    if not sim.human.alive:
        print("\n💀 GAME OVER - Twój człowiek umarł.")
        print(f"Przyczyna: Temp={sim.human.temp}, Pragnienie={sim.human.thirsty}, Energia={sim.human.energy}")
        
    