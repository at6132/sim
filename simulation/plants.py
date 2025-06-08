python start_simulation.pyfrom enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random
import math
import time
import logging
import numpy as np
import uuid
from datetime import datetime
from .utils.logging_config import get_logger
from .cooking import FoodType

logger = get_logger(__name__)

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
    type: str  # Changed from PlantType to str to match usage
    species: str
    age: float
    health: float
    size: float
    position: Tuple[float, float]  # (longitude, latitude)
    growth_rate: float
    reproduction_rate: float
    resource_yield: Dict[str, float]
    planted_by: Optional[str] = None
    needs: PlantNeeds = field(default_factory=PlantNeeds)
    state: PlantState = field(default_factory=PlantState)
    field_id: Optional[str] = None
    last_action: str = "planted"

    @property
    def longitude(self) -> float:
        return self.position[0]

    @property
    def latitude(self) -> float:
        return self.position[1]

class PlantSystem:
    def __init__(self, world):
        """Initialize the plant system."""
        logger.info("Initializing plant system...")
        self.world = world
        self.plants: Dict[str, Plant] = {}
        self.fields: Dict[str, List[str]] = {}  # field_id -> list of plant_ids
        
        # Initialize plant types
        logger.info("Setting up plant types...")
        self.plant_types = self._initialize_plant_types()
        logger.info("Plant types initialized")
        
        # Initialize plants
        logger.info("Initializing plant distribution...")
        self.initialize_plants()
        logger.info("Plant distribution initialized")
        
        logger.info("Plant system initialization complete")
        
    def _initialize_plant_types(self):
        """Initialize plant types with their properties."""
        return {
            'TREE': {
                'name': 'Tree',
                'growth_rate': 0.1,
                'water_need': 0.7,
                'nutrient_need': 0.6,
                'health': 1.0,
                'growth_stages': {
                    'seed': 0.0,
                    'sprout': 0.2,
                    'sapling': 0.4,
                    'young': 0.6,
                    'mature': 0.8,
                    'old': 1.0
                },
                'maturity_age': 100,
                'lifespan': 1000,
                'reproduction_rate': 0.1,
                'spread_rate': 0.05,
                'biomass': 100.0,
                'carbon_sequestration': 0.5,
                'oxygen_production': 0.3,
                'soil_stabilization': 0.4,
                'habitat_value': 0.8,
                'resource_production': {
                    'wood': 50.0,
                    'fruit': 20.0,
                    'seeds': 10.0
                }
            },
            'GRASS': {
                'name': 'Grass',
                'growth_rate': 0.2,
                'water_need': 0.5,
                'nutrient_need': 0.4,
                'health': 1.0,
                'growth_stages': {
                    'seed': 0.0,
                    'sprout': 0.3,
                    'young': 0.6,
                    'mature': 0.8,
                    'old': 1.0
                },
                'maturity_age': 20,
                'lifespan': 100,
                'reproduction_rate': 0.3,
                'spread_rate': 0.2,
                'biomass': 10.0,
                'carbon_sequestration': 0.2,
                'oxygen_production': 0.2,
                'soil_stabilization': 0.6,
                'habitat_value': 0.3,
                'resource_production': {
                    'biomass': 5.0,
                    'seeds': 2.0
                }
            },
            'BUSH': {
                'name': 'Bush',
                'growth_rate': 0.15,
                'water_need': 0.6,
                'nutrient_need': 0.5,
                'health': 1.0,
                'growth_stages': {
                    'seed': 0.0,
                    'sprout': 0.25,
                    'young': 0.5,
                    'mature': 0.75,
                    'old': 1.0
                },
                'maturity_age': 50,
                'lifespan': 200,
                'reproduction_rate': 0.2,
                'spread_rate': 0.1,
                'biomass': 30.0,
                'carbon_sequestration': 0.3,
                'oxygen_production': 0.25,
                'soil_stabilization': 0.5,
                'habitat_value': 0.5,
                'resource_production': {
                    'berries': 15.0,
                    'biomass': 10.0,
                    'seeds': 5.0
                }
            },
            'SHRUB': {
                'name': 'Shrub',
                'growth_rate': 0.15,
                'water_need': 0.6,
                'nutrient_need': 0.5,
                'health': 1.0,
                'growth_stages': {
                    'seed': 0.0,
                    'sprout': 0.25,
                    'young': 0.5,
                    'mature': 0.75,
                    'old': 1.0
                },
                'maturity_age': 50,
                'lifespan': 200,
                'reproduction_rate': 0.2,
                'spread_rate': 0.1,
                'biomass': 30.0,
                'carbon_sequestration': 0.3,
                'oxygen_production': 0.25,
                'soil_stabilization': 0.5,
                'habitat_value': 0.5,
                'resource_production': {
                    'berries': 15.0,
                    'biomass': 10.0,
                    'seeds': 5.0
                }
            }
        }

    def _initialize_plant_species(self):
        """Set up a minimal list of plant species."""
        self.plant_species = {
            "generic": {"edible": False},
            "wheat": {"edible": True},
            "corn": {"edible": True},
        }

    def _initialize_plant_distribution(self):
        """Create a simple plant distribution map."""
        self.plant_distribution = {}
        self.plants = {}
        plant_id = 0
        for lon in range(int(self.world.min_longitude), int(self.world.max_longitude), 60):
            for lat in range(int(self.world.min_latitude), int(self.world.max_latitude), 60):
                self.plant_distribution[(lon, lat)] = ["generic"]
                for p_type in [PlantType.TREE, PlantType.SHRUB, PlantType.GRASS, PlantType.FLOWER, PlantType.WHEAT]:
                    plant = Plant(
                        id=p_type.value if plant_id < 5 else f"plant_{plant_id}",
                        type=p_type.value,
                        species="generic",
                        age=0.0,
                        health=1.0,
                        size=1.0,
                        position=(lon, lat),
                        growth_rate=0.1,
                        reproduction_rate=0.1,
                        resource_yield={"food": 0.1},
                    )
                    self.plants[plant.id] = plant
                    plant_id += 1

    def _initialize_growth_stages(self):
        """Define basic growth stages."""
        self.growth_stages = {
            "seed": 0.0,
            "sprout": 0.25,
            "mature": 1.0,
        }

    def _initialize_biome_distribution(self):
        """Create a dummy biome distribution mapping."""
        self.biome_distribution = {
            "forest": 0.3,
            "grassland": 0.3,
            "desert": 0.2,
            "tundra": 0.2,
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
            type=plant_type.value,
            species=random.choice(["default", "unknown"]),
            age=0.0,
            health=100.0,
            size=random.uniform(0.1, 0.5),
            position=(longitude, latitude),
            growth_rate=random.uniform(0.1, 0.3),
            reproduction_rate=random.uniform(0.1, 0.2),
            resource_yield={
                "food": random.uniform(0.2, 0.6),
                "water": random.uniform(0.1, 0.3),
                "wood": random.uniform(0.0, 0.2),
                "food": random.uniform(0.2, 0.6)
            },
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
        """Update plant growth based on current conditions."""
        try:
            # Get plant type data using string key
            plant_type = self.plant_types[plant.type.upper()]
            # Calculate growth rate based on conditions
            growth_rate = plant_type['growth_rate']
            # Apply environmental factors
            if 'temperature' in world_state:
                temp = world_state['temperature']
                if temp < 10 or temp > 35:  # Temperature stress
                    growth_rate *= 0.5
            if 'precipitation' in world_state:
                precip = world_state['precipitation']
                if precip < 0.1:  # Drought stress
                    growth_rate *= 0.3
            # Update growth progress
            plant.state.growth_progress += growth_rate
            # Check for stage transitions
            current_stage = plant.state.growth_stage
            stages = plant_type['growth_stages']
            # Find next stage
            next_stage = None
            for stage, threshold in stages.items():
                if plant.state.growth_progress >= threshold * 100:
                    next_stage = stage
            if next_stage and next_stage != current_stage:
                plant.state.growth_stage = GrowthStage(next_stage)
            # Update age
            plant.age += 1
            # Check for maturity
            if plant.age >= plant_type['maturity_age']:
                plant.state.growth_stage = GrowthStage.MATURE
            # Check for death
            if plant.age >= plant_type['lifespan']:
                plant.state.growth_stage = GrowthStage.DEAD
        except Exception as e:
            logger.error(f"Error updating plant growth: {e}")
            logger.error(f"Plant type: {plant.type}")
            logger.error(f"Available plant types: {list(self.plant_types.keys())}")
            raise

    def _update_needs(self, plant: Plant, current_time: float, world_state: Dict) -> None:
        """Update plant needs"""
        plant_type = self.plant_types[plant.type.upper()]
        
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

    def harvest_plant(self, plant_id: str) -> Optional[dict]:
        """Harvest a plant, returns a dict of food items and amounts."""
        if plant_id not in self.plants:
            return None
        plant = self.plants[plant_id]
        if plant.state.growth_stage != GrowthStage.HARVESTABLE:
            return None
        plant.state.is_harvested = True
        plant.last_action = "harvested"
        # Calculate yield based on health and growth
        base_yield = self.plant_types[plant.type.upper()]["yield"]
        health_factor = plant.needs.health / 100.0
        food_amount = base_yield * health_factor
        # Map plant type to FoodType
        plant_food_map = {
            "wheat": FoodType.RAW_GRAINS.value,
            "corn": FoodType.RAW_GRAINS.value,
            "potato": FoodType.RAW_VEGETABLES.value,
            "carrot": FoodType.RAW_VEGETABLES.value,
            "tomato": FoodType.RAW_VEGETABLES.value,
            "grass": None,  # Not edible for agents
            "tree": None,
            "undergrowth": None,
            "flower": None,
            "cactus": FoodType.RAW_VEGETABLES.value,
            "shrub": None,
            "moss": None,
            "lichen": None
        }
        food_type = plant_food_map.get(plant.type, None)
        if food_type:
            return {food_type: food_amount}
        return None

    def get_field_plants(self, field_id: str) -> List[Plant]:
        """Get all plants in a field"""
        if field_id not in self.fields:
            return []
            
        return [self.plants[pid] for pid in self.fields[field_id] 
                if pid in self.plants]

    def get_state(self) -> Dict:
        """Get the current state of the plant system."""
        return {
            'plants': {str(plant_id): {
                'id': plant.id,
                'type': plant.type,
                'species': plant.species,
                'age': plant.age,
                'health': plant.health,
                'size': plant.size,
                'position': [float(plant.longitude), float(plant.latitude)],
                'growth_rate': plant.growth_rate,
                'reproduction_rate': plant.reproduction_rate,
                'resource_yield': plant.resource_yield,
                'planted_by': plant.planted_by,
                'needs': {
                    'water': plant.needs.water,
                    'nutrients': plant.needs.nutrients,
                    'health': plant.needs.health,
                    'pest_resistance': plant.needs.pest_resistance
                },
                'state': {
                    'growth_stage': plant.state.growth_stage.value,
                    'growth_progress': plant.state.growth_progress,
                    'age': plant.state.age,
                    'last_watered': plant.state.last_watered,
                    'last_fertilized': plant.state.last_fertilized,
                    'last_weeded': plant.state.last_weeded,
                    'has_pests': plant.state.has_pests,
                    'pest_damage': plant.state.pest_damage,
                    'is_harvested': plant.state.is_harvested
                },
                'field_id': plant.field_id,
                'last_action': plant.last_action
            } for plant_id, plant in self.plants.items()},
            'fields': {str(field_id): [str(pid) for pid in plant_ids] for field_id, plant_ids in self.fields.items()}
        }

    def to_dict(self) -> Dict:
        """Convert plant system state to dictionary"""
        return self.get_state()

    def initialize_plants(self):
        """Initialize the plant system."""
        logger.info("Initializing plant system...")
        
        # Initialize plant species
        logger.info("Setting up plant species...")
        self._initialize_plant_species()
        
        # Initialize plant distribution
        logger.info("Setting up plant distribution...")
        self._initialize_plant_distribution()
        
        # Initialize growth stages
        logger.info("Setting up growth stages...")
        self._initialize_growth_stages()

        # Initialize biome distribution
        logger.info("Setting up biome distribution...")
        self._initialize_biome_distribution()
        
        # Verify initialization
        if not self.verify_initialization():
            logger.error("Plant system initialization verification failed")
            raise RuntimeError("Plant system initialization verification failed")
            
        logger.info("Plant system initialization complete")

    def verify_initialization(self) -> bool:
        """Verify that the plant system is properly initialized."""
        logger.info("Verifying plant system initialization...")
        
        # Check plants dictionary
        if not hasattr(self, 'plants') or not self.plants:
            logger.error("Plants not initialized")
            return False
            
        # Check plant distribution
        if not hasattr(self, 'plant_distribution') or not self.plant_distribution:
            logger.error("Plant distribution not initialized")
            return False
            
        # Check growth stages
        if not hasattr(self, 'growth_stages') or not self.growth_stages:
            logger.error("Growth stages not initialized")
            return False
            
        # Check biome distribution
        if not hasattr(self, 'biome_distribution') or not self.biome_distribution:
            logger.error("Biome distribution not initialized")
            return False
            
        # Check required plant types
        required_types = {'tree', 'shrub', 'grass', 'flower', 'wheat'}
        if not all(plant_type in self.plants for plant_type in required_types):
            logger.error("Not all required plant types initialized")
            return False
            
        logger.info("Plant system initialization verified successfully")
        return True

    def _initialize_plant_ecosystems(self):
        """Initialize plant ecosystems."""
        logger.info("Initializing plant ecosystems...")
        
        # Initialize forest ecosystems
        logger.info("Setting up forest ecosystems...")
        self._initialize_forest_ecosystems()
        logger.info("Forest ecosystems initialized")
        
        # Initialize grassland ecosystems
        logger.info("Setting up grassland ecosystems...")
        self._initialize_grassland_ecosystems()
        logger.info("Grassland ecosystems initialized")
        
        # Initialize desert ecosystems
        logger.info("Setting up desert ecosystems...")
        self._initialize_desert_ecosystems()
        logger.info("Desert ecosystems initialized")
        
        # Initialize tundra ecosystems
        logger.info("Setting up tundra ecosystems...")
        self._initialize_tundra_ecosystems()
        logger.info("Tundra ecosystems initialized")
        
        # Initialize swamp ecosystems
        logger.info("Setting up swamp ecosystems...")
        self._initialize_swamp_ecosystems()
        logger.info("Swamp ecosystems initialized")
        
        logger.info("Plant ecosystems initialization complete")
        
    def _initialize_plant_interactions(self):
        """Initialize plant interactions."""
        logger.info("Initializing plant interactions...")
        
        # Initialize competition
        logger.info("Setting up plant competition...")
        self._initialize_plant_competition()
        logger.info("Plant competition initialized")
        
        # Initialize symbiosis
        logger.info("Setting up plant symbiosis...")
        self._initialize_plant_symbiosis()
        logger.info("Plant symbiosis initialized")
        
        # Initialize pollination
        logger.info("Setting up pollination systems...")
        self._initialize_pollination_systems()
        logger.info("Pollination systems initialized")
        
        logger.info("Plant interactions initialization complete")
        
    def _generate_plants_for_terrain(self, lon: float, lat: float, terrain_type: str):
        """Generate plants based on terrain type."""
        logger.info(f"Generating plants for terrain type: {terrain_type}")
        
        if terrain_type == "forest":
            logger.info("Generating forest plants...")
            self._generate_forest_plants((lon, lat))
            logger.info("Forest plants generated")
        elif terrain_type == "grassland":
            logger.info("Generating grassland plants...")
            self._generate_grassland_plants((lon, lat))
            logger.info("Grassland plants generated")
        elif terrain_type == "desert":
            logger.info("Generating desert plants...")
            self._generate_desert_plants((lon, lat))
            logger.info("Desert plants generated")
        elif terrain_type == "tundra":
            logger.info("Generating tundra plants...")
            self._generate_tundra_plants((lon, lat))
            logger.info("Tundra plants generated")
        elif terrain_type == "swamp":
            logger.info("Generating swamp plants...")
            self._generate_swamp_plants((lon, lat))
            logger.info("Swamp plants generated")
        
    def _generate_forest_plants(self, position: Tuple[float, float]):
        """Generate forest plants at a location."""
        # Define forest plant types and counts
        forest_plants = [
            (PlantType.TREE, 20),  # (type, count)
            (PlantType.SHRUB, 15),
            (PlantType.MOSS, 30),
            (PlantType.LICHEN, 25),
            (PlantType.FLOWER, 10),
            (PlantType.UNDERGROWTH, 40)
        ]
        
        # Spawn each plant type
        for plant_type, count in forest_plants:
            for _ in range(count):
                # Calculate random offset from center position
                offset_lon = random.uniform(-0.1, 0.1)
                offset_lat = random.uniform(-0.1, 0.1)
                spawn_pos = (position[0] + offset_lon, position[1] + offset_lat)
                
                # Create the plant
                plant = Plant(
                    id=f"{plant_type.value}_{len(self.plants)}",
                    type=plant_type.value,
                    species=random.choice(["oak", "pine", "maple", "birch"]),
                    age=random.uniform(0.1, 10.0),
                    health=random.uniform(0.8, 1.0),
                    size=random.uniform(0.5, 2.0),
                    position=spawn_pos,
                    growth_rate=random.uniform(0.1, 0.3),
                    reproduction_rate=random.uniform(0.1, 0.2),
                    resource_yield={
                        "food": random.uniform(0.2, 0.6),
                        "water": random.uniform(0.1, 0.3),
                        "wood": random.uniform(0.5, 1.0)
                    }
                )
                
                self.plants[plant.id] = plant
                
    def _generate_grassland_plants(self, position: Tuple[float, float]):
        """Generate grassland plants at a location."""
        # Define grassland plant types and counts
        grassland_plants = [
            (PlantType.GRASS, 50),
            (PlantType.FLOWER, 20),
            (PlantType.SHRUB, 10),
            (PlantType.TREE, 5)
        ]
        
        # Spawn each plant type
        for plant_type, count in grassland_plants:
            for _ in range(count):
                # Calculate random offset from center position
                offset_lon = random.uniform(-0.1, 0.1)
                offset_lat = random.uniform(-0.1, 0.1)
                spawn_pos = (position[0] + offset_lon, position[1] + offset_lat)
                
                # Create the plant
                plant = Plant(
                    id=f"{plant_type.value}_{len(self.plants)}",
                    type=plant_type.value,
                    species=random.choice(["wheat", "rye", "barley", "wildflower"]),
                    age=random.uniform(0.1, 5.0),
                    health=random.uniform(0.8, 1.0),
                    size=random.uniform(0.3, 1.0),
                    position=spawn_pos,
                    growth_rate=random.uniform(0.2, 0.4),
                    reproduction_rate=random.uniform(0.2, 0.3),
                    resource_yield={
                        "food": random.uniform(0.3, 0.7),
                        "water": random.uniform(0.2, 0.4)
                    }
                )
                
                self.plants[plant.id] = plant
                
    def _generate_desert_plants(self, position: Tuple[float, float]):
        """Generate desert plants at a location."""
        # Define desert plant types and counts
        desert_plants = [
            (PlantType.CACTUS, 15),
            (PlantType.SHRUB, 10),
            (PlantType.GRASS, 5)
        ]
        
        # Spawn each plant type
        for plant_type, count in desert_plants:
            for _ in range(count):
                # Calculate random offset from center position
                offset_lon = random.uniform(-0.1, 0.1)
                offset_lat = random.uniform(-0.1, 0.1)
                spawn_pos = (position[0] + offset_lon, position[1] + offset_lat)
                
                # Create the plant
                plant = Plant(
                    id=f"{plant_type.value}_{len(self.plants)}",
                    type=plant_type.value,
                    species=random.choice(["saguaro", "prickly_pear", "barrel_cactus"]),
                    age=random.uniform(0.1, 20.0),
                    health=random.uniform(0.8, 1.0),
                    size=random.uniform(0.5, 1.5),
                    position=spawn_pos,
                    growth_rate=random.uniform(0.05, 0.15),
                    reproduction_rate=random.uniform(0.05, 0.1),
                    resource_yield={
                        "water": random.uniform(0.3, 0.6),
                        "food": random.uniform(0.1, 0.3)
                    }
                )
                
                self.plants[plant.id] = plant
                
    def _generate_tundra_plants(self, position: Tuple[float, float]):
        """Generate tundra plants at a location."""
        # Define tundra plant types and counts
        tundra_plants = [
            (PlantType.MOSS, 30),
            (PlantType.LICHEN, 25),
            (PlantType.GRASS, 15),
            (PlantType.SHRUB, 5)
        ]
        
        # Spawn each plant type
        for plant_type, count in tundra_plants:
            for _ in range(count):
                # Calculate random offset from center position
                offset_lon = random.uniform(-0.1, 0.1)
                offset_lat = random.uniform(-0.1, 0.1)
                spawn_pos = (position[0] + offset_lon, position[1] + offset_lat)
                
                # Create the plant
                plant = Plant(
                    id=f"{plant_type.value}_{len(self.plants)}",
                    type=plant_type.value,
                    species=random.choice(["arctic_moss", "reindeer_moss", "tundra_grass"]),
                    age=random.uniform(0.1, 8.0),
                    health=random.uniform(0.8, 1.0),
                    size=random.uniform(0.2, 0.8),
                    position=spawn_pos,
                    growth_rate=random.uniform(0.05, 0.15),
                    reproduction_rate=random.uniform(0.05, 0.1),
                    resource_yield={
                        "food": random.uniform(0.1, 0.3),
                        "water": random.uniform(0.2, 0.4)
                    }
                )
                
                self.plants[plant.id] = plant
                
    def _generate_swamp_plants(self, position: Tuple[float, float]):
        """Generate swamp plants at a location."""
        # Define swamp plant types and counts
        swamp_plants = [
            (PlantType.TREE, 10),
            (PlantType.SHRUB, 15),
            (PlantType.MOSS, 25),
            (PlantType.GRASS, 20)
        ]
        
        # Spawn each plant type
        for plant_type, count in swamp_plants:
            for _ in range(count):
                # Calculate random offset from center position
                offset_lon = random.uniform(-0.1, 0.1)
                offset_lat = random.uniform(-0.1, 0.1)
                spawn_pos = (position[0] + offset_lon, position[1] + offset_lat)
                
                # Create the plant
                plant = Plant(
                    id=f"{plant_type.value}_{len(self.plants)}",
                    type=plant_type.value,
                    species=random.choice(["cypress", "mangrove", "swamp_grass"]),
                    age=random.uniform(0.1, 15.0),
                    health=random.uniform(0.8, 1.0),
                    size=random.uniform(0.5, 2.0),
                    position=spawn_pos,
                    growth_rate=random.uniform(0.15, 0.25),
                    reproduction_rate=random.uniform(0.15, 0.2),
                    resource_yield={
                        "food": random.uniform(0.2, 0.4),
                        "water": random.uniform(0.3, 0.5),
                        "wood": random.uniform(0.3, 0.6)
                    }
                )
                
                self.plants[plant.id] = plant 