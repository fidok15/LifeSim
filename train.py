import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
import random
import math
from src.model.utils import SurvivalEnv
from src.model.model import DQNmodel
from src.model.buffer import ReplayBuffer
from src import config as config


#naprawde istnieje takei cos jak mps 
device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
print(device)
env = SurvivalEnv()
input_shape = env.observation_space[0].shape
num_stats = env.observation_space[1].shape[0]
n_actions = env.action_space.n
# teraz z góry przepraszam za ten fragment ale mi tak łatwiej było zrozumieć co się dzieję, bo 1. raz stosuje DQN
uczen = DQNmodel(input_shape, num_stats, n_actions).to(device)
nauczyciel = DQNmodel(input_shape, num_stats, n_actions).to(device)
# sieci startuja z takimi samymi wagami 
nauczyciel.load_state_dict(uczen.state_dict())
nauczyciel.eval()

optimizer = optim.AdamW(uczen.parameters(), lr=config.LR, amsgrad=True)
memory = ReplayBuffer(config.MEMORY_SIZE)

steps_done = 0

def select_action(state, current_eps):
    if random.random() > current_eps:
        with torch.no_grad():
            #mapa statystyki
            grid, stats = state
            # zmiana na tensor 
            grid_t = torch.tensor(grid, dtype=torch.float32).unsqueeze(0).to(device)
            stats_t = torch.tensor(stats, dtype=torch.float32).unsqueeze(0).to(device)
            #co nasz model sądzi o tej sytuacji zwraca 6 liczb (punkty dla każdej akcji)
            q_values = uczen((grid_t, stats_t))
            #wybieramy najwyzej punktowana
            return q_values.max(1)[1].item()
    else:
        return env.action_space.sample()

def nauka_ucznia():
    #sprawdzamy czy mamy wystarczajaco danych
    if len(memory) < config.BATCH_SIZE:
        return
    #tylko stany tylko akcje tylko nagrody tylko nastepne stany 
    batch_state, batch_action, batch_reward, batch_next_state, batch_done = memory.sample(config.BATCH_SIZE)

    #zamiana stanow na tenosry    
    state_grid = torch.tensor(np.array([s[0] for s in batch_state]), dtype=torch.float32).to(device)
    state_stats = torch.tensor(np.array([s[1] for s in batch_state]), dtype=torch.float32).to(device)
    
    next_state_grid = torch.tensor(np.array([s[0] for s in batch_next_state]), dtype=torch.float32).to(device)
    next_state_stats = torch.tensor(np.array([s[1] for s in batch_next_state]), dtype=torch.float32).to(device)
    
    #zmiana pozostaly rzeczy na tenosry 
    batch_action = torch.tensor(batch_action, dtype=torch.int64).unsqueeze(1).to(device)
    batch_reward = torch.tensor(batch_reward, dtype=torch.float32).to(device)
    batch_done = torch.tensor(batch_done, dtype=torch.float32).to(device)

    #co uczen mysli ze dostanie 
    uczen_predykcja = uczen((state_grid, state_stats)).gather(1, batch_action)

    with torch.no_grad():
        # co nauczyciel uwaza MAX wartość z nast stanu 
        nauczyciel_predykcja = nauczyciel((next_state_grid, next_state_stats)).max(1)[0]

        wzor_belmana = batch_reward + (config.GAMMA * nauczyciel_predykcja * (1 - batch_done))
    
    criterion = nn.SmoothL1Loss()
    loss = criterion(uczen_predykcja, wzor_belmana.unsqueeze(1))
    optimizer.zero_grad()
    loss.backward()
    #zabezpieczenie przed czyms
    torch.nn.utils.clip_grad_value_(uczen.parameters(), 1)
    optimizer.step()


print("Rozgrzewanie bufora pamięci...")
obs, _ = env.reset()
for _ in range(config.BATCH_SIZE * 5): # Zbieramy np. 5 batchy losowych danych
    action = env.action_space.sample() # Czysto losowe ruchy
    next_obs, reward, terminated, truncated, _ = env.step(action)
    done = terminated or truncated
    memory.push(obs, action, reward, next_obs, done)
    obs = next_obs
    if done:
        obs, _ = env.reset()
print("Bufor gotowy, zaczynamy trening!")

for episode in range(config.EPISODEDS):
    obs, _ = env.reset()
    total_reward = 0
    epsilon = config.EPS_END + (config.EPS_START - config.EPS_END) * math.exp(-1. * steps_done / config.EPS_DECAY)

    while True:
        action = select_action(obs, epsilon)
        steps_done += 1
        #wykonanie kroku
        next_obs, reward, terminated, truncated, _ = env.step(action)
        #czy zdech
        done = terminated or truncated
        #zapisanie do memory
        memory.push(obs, action, reward, next_obs, done)
        nauka_ucznia()
        obs = next_obs
        total_reward += reward
        if done:
            print(f"Epizod {episode+1}: Nagroda={total_reward:.2f}, Epsilon={epsilon:.2f}")
            break
    #aktualizacja nauczyciela co jakis czas 
    if episode % config.TARGET_UPDATE == 0:
        nauczyciel.load_state_dict(uczen.state_dict())