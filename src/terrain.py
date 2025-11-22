# Flyweight approach no podejście 

from dataclasses import dataclass
from . import config

@dataclass(frozen=True)
class TerrainType:
    id: int
    name: str
    color: str
    field_temp: float


#zmienne statyczne
class TerrainRegistry:
    PLAIN = TerrainType(
        id=config.ID_PLAIN, name="równina", color='lightgreen', field_temp= -0.5
    )
    
    FOREST = TerrainType(
        id=config.ID_FOREST, name="las", color='darkgreen', field_temp= -0.5
    )
    
    WATER = TerrainType(
        id=config.ID_WATER, name="woda", color='blue', field_temp= -0.5
    )
    
    CAMPFIRE = TerrainType(
        id=config.ID_CAMPFIRE, name="ognisko", color='orange', field_temp= -0.5
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
    