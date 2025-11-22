from src.world import World
from src.creatures.human import Human
# 1. Tworzymy świat
swiat = World()
human = Human()
x, y = 5, 5

id_pola = swiat.terrain_grid[x, y]
print(f"Stoję na polu typu ID: {id_pola}")
