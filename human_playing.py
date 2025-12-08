from src.world.world import World
from src.world.creatures.human import Human
import numpy as np
from src import config as config
from src.world.creatures.wolf import Wolf
from src.world.creatures.sheep import Sheep
from src.world.creatures.knight import Knight
from src.world.cycle import Cycle
import os

def print_map(sim):
    """Rysuje mapę w konsoli używając kodów ASCII/Emoji"""
    os.system('cls' if os.name == 'nt' else 'clear') # Czyść ekran
    
    h = sim.human
    print(f"Ilość ruchów: {h.moves_alive} | Akcje: {h.actions_left}/{config.MAX_ACTIONS_PER_DAY}")
    print(f"Zdrowie (Alive): {h.alive} | Energia: {h.energy:.1f} | Głód: {h.hunger:.1f} | Pragnienie: {h.thirsty:.1f}")
    print(f"Temp: {h.temp:.1f}°C | Drewno: {h.wood_inv}")
    print(f"Punkty: {h.points:.1f}")
    print("-" * (sim.world.size + 2))

    # pokazuje 11x11 kratek wokół gracza
    view_range = 5
    start_y = max(0, h.y - view_range)
    end_y = min(sim.world.size, h.y + view_range + 1)
    start_x = max(0, h.x - view_range)
    end_x = min(sim.world.size, h.x + view_range + 1)

    for y in range(start_y, end_y):
        line = ""
        for x in range(start_x, end_x):
            # sprawdz czy jest istota
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


if __name__ == "__main__":
    # inicjalizacja symulacji
    sim = Cycle()

    # pętla gry
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
        print(f"Przyczyna: Temp={sim.human.temp:.2f}, Pragnienie={sim.human.thirsty:.2f}, Głód={sim.human.hunger:.2f}")
        
    