# Flyweight approach
from dataclasses import dataclass
from src import config as config

@dataclass(frozen=True)
class TerrainType:
    id: int
    name: str
    color: str


#zmienne statyczne
class TerrainRegistry:
    PLAIN = TerrainType(
        id=config.ID_PLAIN, name="równina", color='lightgreen'
    )
    
    FOREST = TerrainType(
        id=config.ID_FOREST, name="las", color='darkgreen'
    )
    
    WATER = TerrainType(
        id=config.ID_WATER, name="woda", color='blue'
    )
    
    CAMPFIRE = TerrainType(
        id=config.ID_CAMPFIRE, name="ognisko", color='orange'
    )

    _registry = {
        config.ID_PLAIN: PLAIN,
        config.ID_FOREST: FOREST,
        config.ID_WATER: WATER,
        config.ID_CAMPFIRE: CAMPFIRE
    }

    @classmethod
    def get(cls, terrain_id):
        return cls._registry.get(terrain_id, cls.PLAIN)
    