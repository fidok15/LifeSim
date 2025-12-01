import torch
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import time
from src.model.utils import SurvivalEnv
from src.model.model import DQNmodel
from src import config as config

# --- KONFIGURACJA TESTU ---
MODEL_PATH = "checkpoint_3800.pth"  # Zmień na nazwę swojego zapisanego pliku!
STEP_DELAY = 2                  # Czas (w sekundach) między krokami dla oka
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

def get_death_reason(human, creature_list):
    """Analizuje stan humana i zwraca przyczynę zgonu."""
    if human.alive:
        return "Nadal żyje"
    
    # Sprawdzenie parametrów życiowych
    if human.temp <= config.TEMP_DIE:
        return f"Hipotermia (Temp: {human.temp:.2f})"
    if human.thirsty <= config.THIRSTY_DIE:
        return f"Odwodnienie (Woda: {human.thirsty:.2f})"
    if human.hunger <= config.HUNGER_DIE:
        return f"Głód (Głód: {human.hunger:.2f})"
    
    # Sprawdzenie walki (jeśli parametry są ok, a nie żyje, to pewnie walka)
    # W Twoim kodzie walka ustawia alive=False bezpośrednio.
    # Musimy sprawdzić otoczenie, czy stoi na wilku/rycerzu.
    # To jest heurystyka, bo po śmierci world state może się lekko zmienić w logice,
    # ale zazwyczaj pozycja jest ta sama.
    return "Zabity przez drapieżnika lub wroga"

def visualize_simulation():
    # 1. Inicjalizacja środowiska i modelu
    env = SurvivalEnv()
    input_shape = env.observation_space[0].shape
    num_stats = env.observation_space[1].shape[0]
    n_actions = env.action_space.n
    
    model = DQNmodel(input_shape, num_stats, n_actions).to(DEVICE)
    
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        print(f"Załadowano model z {MODEL_PATH}")
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku modelu. Upewnij się, że wytrenowałeś model i podałeś dobrą ścieżkę.")
        return

    model.eval() # Tryb ewaluacji (wyłącza dropout itp.)
    
    obs, _ = env.reset(seed=config.SEED)
    terminated = False
    truncated = False
    
    # 2. Konfiguracja wykresu
    plt.ion() # Tryb interaktywny
    fig, (ax_map, ax_stats) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Mapa kolorów dla terenu (Plain, Forest, Water, Campfire)
    # ID: 1=Forest, 2=Campfire, 3=Water, 4=Plain (wg config.py)
    cmap = mcolors.ListedColormap(['darkgreen', 'orange', 'blue', 'lightgreen'])
    bounds = [0.5, 1.5, 2.5, 3.5, 4.5] # Granice dla ID 1, 2, 3, 4
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    step_counter = 0

    while not (terminated or truncated):
        # --- LOGIKA MODELU ---
        grid, stats = obs
        grid_t = torch.tensor(grid, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        stats_t = torch.tensor(stats, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        
        with torch.no_grad():
            q_values = model((grid_t, stats_t))
            action = q_values.max(1)[1].item() # Wybieramy najlepszą akcję (Greedy)
            
        # Wykonanie ruchu
        obs, reward, terminated, truncated, _ = env.step(action)
        human = env.sim.human
        
        # --- WIZUALIZACJA ---
        ax_map.clear()
        ax_stats.clear()
        
        # Rysowanie mapy
        terrain_grid = env.sim.world.terrain_grid
        ax_map.imshow(terrain_grid, cmap=cmap, norm=norm)
        
        # Rysowanie agenta (czerwona kropka)
        ax_map.scatter(human.x, human.y, c='red', s=100, label='Human', edgecolors='black')
        
        # Opcjonalnie: Rysowanie innych stworzeń (uproszczone)
        # Możesz to rozbudować iterując po env.sim.world.entity_grid
        
        ax_map.set_title(f"Step: {step_counter} | Action: {action}\nPos: ({human.x}, {human.y})")
        ax_map.legend(loc='upper right')
        ax_map.grid(False)

        # Rysowanie statystyk
        stats_labels = ['Głód', 'Pragnienie', 'Temp', 'Energia', 'Drewno']
        stats_values = [human.hunger, human.thirsty, human.temp, human.energy, human.wood_inv]
        stats_max = [config.HUNGER_MAX, config.THIRSTY_MAX, config.TEMP_MAX, config.ENERGY_MAX, config.MAX_WOOD_INV]
        
        # Normalizacja do paska 0-1 dla wizualizacji
        norm_values = [v/m if m > 0 else 0 for v, m in zip(stats_values, stats_max)]
        
        colors = ['green', 'blue', 'red', 'yellow', 'brown']
        ax_stats.barh(stats_labels, norm_values, color=colors)
        ax_stats.set_xlim(0, 1.0)
        ax_stats.set_title("Parametry Życiowe Agenta")
        
        # Dodanie wartości liczbowych obok pasków
        for i, v in enumerate(stats_values):
            ax_stats.text(0.05, i, f"{v:.1f}/{stats_max[i]}", color='black', fontweight='bold', va='center')

        plt.draw()
        plt.pause(STEP_DELAY)
        step_counter += 1

    # --- KONIEC EPIZODU ---
    plt.ioff()
    reason = get_death_reason(env.sim.human, []) # Lista stworzeń nie jest łatwo dostępna z poziomu env.sim w tym miejscu bez modyfikacji, 
                                                 # ale logika parametrów wystarczy w 90% przypadków.
    
    print("="*30)
    print(f"KONIEC SYMULACJI")
    print(f"Przeżyto kroków: {step_counter}")
    print(f"Przyczyna śmierci: {reason}")
    print("="*30)
    plt.show()

if __name__ == "__main__":
    visualize_simulation()