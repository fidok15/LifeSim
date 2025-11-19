from src.world import World
from src.visualization import render_map
# 1. Tworzymy świat
swiat = World()

x, y = 5, 5

id_pola = swiat.terrain_grid[x, y]
print(f"Stoję na polu typu ID: {id_pola}")

render_map(swiat)