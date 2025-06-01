from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random
import math
import time
import logging
import numpy as np
import uuid

logger = logging.getLogger(__name__)

class PlantType(Enum):
    WHEAT = "wheat"
    CORN = "corn"
    RICE = "rice"
    POTATO = "potato"
    CARROT = "carrot"
    TOMATO = "tomato"
    GRASS = "grass"  # For grazing animals
    TREE = "tree"
    UNDERGROWTH = "undergrowth"
    FLOWER = "flower"
    CACTUS = "cactus"
    SHRUB = "shrub"
    MOSS = "moss"
    LICHEN = "lichen"

class GrowthStage(Enum):
    SEED = "seed"
    SPROUT = "sprout"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    MATURE = "mature"
    HARVESTABLE = "harvestable"
    DEAD = "dead"

@dataclass
class PlantNeeds:
    water: float = 100.0  # 0-100, 0 means dead
    nutrients: float = 100.0  # 0-100, affects growth rate
    health: float = 100.0  # 0-100, 0 means dead
    pest_resistance: float = 100.0  # 0-100, affects pest damage

@dataclass
class PlantState:
    growth_stage: GrowthStage = GrowthStage.SEED
    growth_progress: float = 0.0  # 0-100
    age: float = 0.0  # in days
    last_watered: float = 0.0
    last_fertilized: float = 0.0
    last_weeded: float = 0.0
    has_pests: bool = False
    pest_damage: float = 0.0
    is_harvested: bool = False

@dataclass
class Plant:
    id: str
    type: PlantType
    longitude: float
    latitude: float
    planted_by: Optional[str] = None  # Agent ID who planted it
    needs: PlantNeeds = field(default_factory=PlantNeeds)
    state: PlantState = field(default_factory=PlantState)
    field_id: Optional[str] = None  # ID of the field it belongs to
    last_action: str = "planted"

class PlantSystem:
    def __init__(self, world_size: int, world=None):
        self.world_size = world_size
        self.world = world
        self.plants: Dict[str, Plant] = {}
        self.fields: Dict[str, List[str]] = {}  # field_id -> list of plant_ids
        self.plant_types = self._initialize_plant_types()
        self.initialize_plants()

    def _initialize_plant_types(self) -> Dict[PlantType, Dict]:
        return {
            PlantType.WHEAT: {
                "growth_time": 120.0,  # days to mature
                "water_need": 0.8,  # water consumption rate
                "nutrient_need": 0.6,
                "yield": 1.0,
                "pest_resistance": 0.7,
                "stages": {
                    GrowthStage.SEED: 0.0,
                    GrowthStage.SPROUT: 0.2,
                    GrowthStage.VEGETATIVE: 0.4,
                    GrowthStage.FLOWERING: 0.6,
                    GrowthStage.MATURE: 0.8,
                    GrowthStage.HARVESTABLE: 1.0
                }
            },
            PlantType.CORN: {
                "growth_time": 90.0,
                "water_need": 1.0,
                "nutrient_need": 0.8,
                "yield": 1.2,
                "pest_resistance": 0.5,
                "stages": {
                    GrowthStage.SEED: 0.0,
                    GrowthStage.SPROUT: 0.15,
                    GrowthStage.VEGETATIVE: 0.35,
                    GrowthStage.FLOWERING: 0.55,
                    GrowthStage.MATURE: 0.75,
                    GrowthStage.HARVESTABLE: 1.0
                }
            },
            PlantType.GRASS: {
                "growth_time": 30.0,
                "water_need": 0.5,
                "nutrient_need": 0.4,
                "yield": 0.8,
                "pest_resistance": 0.9,
                "stages": {
                    GrowthStage.SEED: 0.0,
                    GrowthStage.SPROUT: 0.3,
                    GrowthStage.VEGETATIVE: 0.6,
                    GrowthStage.MATURE: 0.8,
                    GrowthStage.HARVESTABLE: 1.0
                }
            }
        }

    def create_field(self, longitude: float, latitude: float, size: float) -> str:
        """Create a new field for planting"""
        field_id = f"field_{len(self.fields)}"
        self.fields[field_id] = []
        return field_id

    def plant_seed(self, plant_type: PlantType, longitude: float, latitude: float, 
                  planted_by: str, field_id: Optional[str] = None) -> Plant:
        """Plant a new seed"""
        plant = Plant(
            id=f"{plant_type.value}_{len(self.plants)}",
            type=plant_type,
            longitude=longitude,
            latitude=latitude,
            planted_by=planted_by,
            field_id=field_id
        )
        
        self.plants[plant.id] = plant
        if field_id:
            self.fields[field_id].append(plant.id)
            
        return plant

    def update(self, current_time: float, world_state: Dict) -> None:
        """Update all plants' states"""
        for plant in list(self.plants.values()):
            self._update_growth(plant, current_time, world_state)
            self._update_needs(plant, current_time, world_state)
            self._update_pests(plant)
            self._handle_death(plant)

    def _update_growth(self, plant: Plant, current_time: float, world_state: Dict) -> None:
        """Update plant growth"""
        if plant.state.is_harvested or plant.state.growth_stage == GrowthStage.DEAD:
            return

        plant_type = self.plant_types[plant.type]
        growth_rate = 1.0

        # Growth rate affected by needs
        if plant.needs.water < 30:
            growth_rate *= 0.5
        if plant.needs.nutrients < 30:
            growth_rate *= 0.7
        if plant.needs.health < 50:
            growth_rate *= 0.8

        # Weather effects
        weather = world_state.get("weather", "clear")
        if weather == "rain":
            growth_rate *= 1.2
        elif weather == "drought":
            growth_rate *= 0.5

        # Update growth progress
        plant.state.growth_progress += (1.0 / plant_type["growth_time"]) * growth_rate
        plant.state.age += 1.0

        # Update growth stage
        stages = plant_type["stages"]
        for stage, threshold in sorted(stages.items(), key=lambda x: x[1]):
            if plant.state.growth_progress >= threshold:
                plant.state.growth_stage = stage

    def _update_needs(self, plant: Plant, current_time: float, world_state: Dict) -> None:
        """Update plant needs"""
        plant_type = self.plant_types[plant.type]
        
        # Water consumption
        time_since_watered = current_time - plant.state.last_watered
        water_consumption = plant_type["water_need"] * time_since_watered
        
        # Natural water from rain
        weather = world_state.get("weather", "clear")
        if weather == "rain":
            water_consumption *= 0.5
        elif weather == "drought":
            water_consumption *= 1.5

        plant.needs.water = max(0, plant.needs.water - water_consumption)

        # Nutrient consumption
        time_since_fertilized = current_time - plant.state.last_fertilized
        nutrient_consumption = plant_type["nutrient_need"] * time_since_fertilized
        plant.needs.nutrients = max(0, plant.needs.nutrients - nutrient_consumption)

        # Health affected by needs
        if plant.needs.water < 20 or plant.needs.nutrients < 20:
            plant.needs.health = max(0, plant.needs.health - 0.5)

    def _update_pests(self, plant: Plant) -> None:
        """Handle pest infestations"""
        if plant.state.has_pests:
            # Increase pest damage
            plant.state.pest_damage += 0.1
            plant.needs.health = max(0, plant.needs.health - 0.2)
            
            # Chance to overcome pests
            if random.random() < (plant.needs.pest_resistance / 100):
                plant.state.has_pests = False
                plant.state.pest_damage = 0.0
        else:
            # Chance to get pests
            if random.random() < 0.01:  # 1% chance per update
                plant.state.has_pests = True

    def _handle_death(self, plant: Plant) -> None:
        """Handle plant death"""
        if (plant.needs.health <= 0 or 
            plant.needs.water <= 0 or
            plant.state.pest_damage >= 100):
            
            plant.state.growth_stage = GrowthStage.DEAD
            
            # Remove from field if applicable
            if plant.field_id and plant.field_id in self.fields:
                self.fields[plant.field_id].remove(plant.id)
            
            # Remove plant
            del self.plants[plant.id]

    def water_plant(self, plant_id: str) -> bool:
        """Water a plant"""
        if plant_id not in self.plants:
            return False
            
        plant = self.plants[plant_id]
        plant.needs.water = min(100, plant.needs.water + 50)
        plant.state.last_watered = time.time()
        plant.last_action = "watered"
        return True

    def fertilize_plant(self, plant_id: str) -> bool:
        """Fertilize a plant"""
        if plant_id not in self.plants:
            return False
            
        plant = self.plants[plant_id]
        plant.needs.nutrients = min(100, plant.needs.nutrients + 50)
        plant.state.last_fertilized = time.time()
        plant.last_action = "fertilized"
        return True

    def weed_field(self, field_id: str) -> bool:
        """Remove weeds from a field"""
        if field_id not in self.fields:
            return False
            
        for plant_id in self.fields[field_id]:
            if plant_id in self.plants:
                plant = self.plants[plant_id]
                plant.state.last_weeded = time.time()
                plant.last_action = "weeded"
                plant.needs.health = min(100, plant.needs.health + 10)
        return True

    def harvest_plant(self, plant_id: str) -> Optional[float]:
        """Harvest a plant, returns yield amount"""
        if plant_id not in self.plants:
            return None
            
        plant = self.plants[plant_id]
        if plant.state.growth_stage != GrowthStage.HARVESTABLE:
            return None
            
        plant.state.is_harvested = True
        plant.last_action = "harvested"
        
        # Calculate yield based on health and growth
        base_yield = self.plant_types[plant.type]["yield"]
        health_factor = plant.needs.health / 100.0
        return base_yield * health_factor

    def get_field_plants(self, field_id: str) -> List[Plant]:
        """Get all plants in a field"""
        if field_id not in self.fields:
            return []
            
        return [self.plants[pid] for pid in self.fields[field_id] 
                if pid in self.plants]

    def to_dict(self) -> Dict:
        """Convert plant system state to dictionary"""
        return {
            "plants": {
                plant_id: {
                    "id": plant.id,
                    "type": plant.type.value,
                    "position": (plant.longitude, plant.latitude),
                    "needs": {
                        "water": plant.needs.water,
                        "nutrients": plant.needs.nutrients,
                        "health": plant.needs.health,
                        "pest_resistance": plant.needs.pest_resistance
                    },
                    "state": {
                        "growth_stage": plant.state.growth_stage.value,
                        "growth_progress": plant.state.growth_progress,
                        "age": plant.state.age,
                        "has_pests": plant.state.has_pests,
                        "pest_damage": plant.state.pest_damage,
                        "is_harvested": plant.state.is_harvested
                    },
                    "planted_by": plant.planted_by,
                    "field_id": plant.field_id,
                    "last_action": plant.last_action
                }
                for plant_id, plant in self.plants.items()
            },
            "fields": self.fields
        }

    def initialize_plants(self):
        """Initialize plants across the world."""
        logger.info("Initializing plant system...")
        
        # Initialize plants for each coordinate
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                terrain = self.world.terrain.get_terrain_at(lon, lat)
                
                # Generate plants based on terrain type
                if terrain == 'forest':
                    self._generate_forest_plants(lon, lat)
                elif terrain == 'grassland':
                    self._generate_grassland_plants(lon, lat)
                elif terrain == 'desert':
                    self._generate_desert_plants(lon, lat)
                elif terrain == 'tundra':
                    self._generate_tundra_plants(lon, lat)
                elif terrain == 'swamp':
                    self._generate_swamp_plants(lon, lat)
                    
        logger.info("Plant system initialization complete")
        
    def _generate_forest_plants(self, lon: float, lat: float):
        """Generate forest plants at a location."""
        # Generate trees
        num_trees = random.randint(5, 15)
        for _ in range(num_trees):
            tree = Plant(
                id=str(uuid.uuid4()),
                type="tree",
                species=random.choice(["oak", "pine", "maple", "birch"]),
                age=random.uniform(1, 100),
                health=random.uniform(0.7, 1.0),
                size=random.uniform(0.5, 1.0),
                position=(lon, lat),
                growth_rate=random.uniform(0.1, 0.3),
                reproduction_rate=random.uniform(0.1, 0.2),
                resource_yield={
                    "wood": random.uniform(0.5, 1.0),
                    "food": random.uniform(0.1, 0.3)
                }
            )
            self.plants[tree.id] = tree
            
        # Generate undergrowth
        num_undergrowth = random.randint(10, 30)
        for _ in range(num_undergrowth):
            plant = Plant(
                id=str(uuid.uuid4()),
                type="undergrowth",
                species=random.choice(["fern", "moss", "berry_bush"]),
                age=random.uniform(0.1, 5),
                health=random.uniform(0.8, 1.0),
                size=random.uniform(0.1, 0.3),
                position=(lon, lat),
                growth_rate=random.uniform(0.2, 0.4),
                reproduction_rate=random.uniform(0.2, 0.3),
                resource_yield={
                    "food": random.uniform(0.2, 0.4)
                }
            )
            self.plants[plant.id] = plant
            
    def _generate_grassland_plants(self, lon: float, lat: float):
        """Generate grassland plants at a location."""
        # Generate grass
        num_grass = random.randint(20, 50)
        for _ in range(num_grass):
            grass = Plant(
                id=str(uuid.uuid4()),
                type="grass",
                species=random.choice(["wheat", "rye", "barley"]),
                age=random.uniform(0.1, 2),
                health=random.uniform(0.8, 1.0),
                size=random.uniform(0.1, 0.4),
                position=(lon, lat),
                growth_rate=random.uniform(0.3, 0.5),
                reproduction_rate=random.uniform(0.3, 0.4),
                resource_yield={
                    "food": random.uniform(0.3, 0.6)
                }
            )
            self.plants[grass.id] = grass
            
    def _generate_desert_plants(self, lon: float, lat: float):
        """Generate desert plants at a location."""
        # Generate cacti and other desert plants
        num_plants = random.randint(1, 5)
        for _ in range(num_plants):
            plant = Plant(
                id=str(uuid.uuid4()),
                type="desert_plant",
                species=random.choice(["cactus", "succulent", "desert_flower"]),
                age=random.uniform(1, 20),
                health=random.uniform(0.6, 0.9),
                size=random.uniform(0.2, 0.5),
                position=(lon, lat),
                growth_rate=random.uniform(0.05, 0.1),
                reproduction_rate=random.uniform(0.05, 0.1),
                resource_yield={
                    "food": random.uniform(0.1, 0.3),
                    "water": random.uniform(0.1, 0.2)
                }
            )
            self.plants[plant.id] = plant
            
    def _generate_tundra_plants(self, lon: float, lat: float):
        """Generate tundra plants at a location."""
        # Generate moss and lichen
        num_plants = random.randint(10, 30)
        for _ in range(num_plants):
            plant = Plant(
                id=str(uuid.uuid4()),
                type="tundra_plant",
                species=random.choice(["moss", "lichen", "tundra_flower"]),
                age=random.uniform(0.5, 5),
                health=random.uniform(0.7, 0.9),
                size=random.uniform(0.1, 0.3),
                position=(lon, lat),
                growth_rate=random.uniform(0.1, 0.2),
                reproduction_rate=random.uniform(0.1, 0.2),
                resource_yield={
                    "food": random.uniform(0.1, 0.2)
                }
            )
            self.plants[plant.id] = plant
            
    def _generate_swamp_plants(self, lon: float, lat: float):
        """Generate swamp plants at a location."""
        # Generate water plants and trees
        num_plants = random.randint(5, 15)
        for _ in range(num_plants):
            plant = Plant(
                id=str(uuid.uuid4()),
                type="swamp_plant",
                species=random.choice(["mangrove", "lily", "reed"]),
                age=random.uniform(0.5, 10),
                health=random.uniform(0.7, 1.0),
                size=random.uniform(0.2, 0.6),
                position=(lon, lat),
                growth_rate=random.uniform(0.2, 0.3),
                reproduction_rate=random.uniform(0.2, 0.3),
                resource_yield={
                    "food": random.uniform(0.2, 0.4),
                    "wood": random.uniform(0.1, 0.3)
                }
            )
            self.plants[plant.id] = plant 