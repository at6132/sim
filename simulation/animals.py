from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import random
import math
import time
from datetime import datetime
import numpy as np
from .utils.logging_config import get_logger
from .cooking import CookingSystem, FoodType
import traceback

logger = get_logger(__name__)

class AnimalType(Enum):
    # Land Animals
    HORSE = "horse"
    WOLF = "wolf"
    DEER = "deer"
    BEAR = "bear"
    RABBIT = "rabbit"
    SHEEP = "sheep"
    COW = "cow"
    GOAT = "goat"

class WaterType(Enum):
    FRESHWATER = "freshwater"
    SALTWATER = "saltwater"
    BRACKISH = "brackish"  # Mix of fresh and salt water (estuaries, deltas)

class AnimalTemperament(Enum):
    DOCILE = "docile"
    NEUTRAL = "neutral"
    AGGRESSIVE = "aggressive"

@dataclass
class AnimalNeeds:
    hunger: float = 100.0  # 0-100, 0 means starving
    thirst: float = 100.0  # 0-100, 0 means dehydrated
    energy: float = 100.0  # 0-100, 0 means exhausted
    health: float = 100.0  # 0-100, 0 means dead
    reproduction_urge: float = 0.0  # 0-100, increases with age and health
    social_need: float = 50.0  # 0-100, varies by species
    comfort: float = 100.0  # 0-100, affected by environment
    water_quality: float = 100.0  # 0-100, affected by water type and pollution

@dataclass
class AnimalState:
    is_sick: bool = False
    disease_resistance: float = 100.0  # 0-100, affected by health and age
    pregnancy_progress: float = 0.0  # 0-100, for pregnant animals
    age: float = 0.0  # in years
    lifespan: float = 0.0  # in years, varies by species
    maturity_age: float = 0.0  # age at which animal can reproduce
    last_meal_time: float = 0.0
    last_water_time: float = 0.0
    last_rest_time: float = 0.0
    last_social_time: float = 0.0

@dataclass
class AnimalTerritory:
    """Represents a territory claimed by an animal"""
    center_longitude: float
    center_latitude: float
    radius: float  # in kilometers
    claimed_by: Optional[str] = None
    resources: Dict[str, float] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

@dataclass
class Animal:
    """Represents an animal in the simulation"""
    id: str
    type: AnimalType
    name: str
    temperament: AnimalTemperament
    size: float  # 0-1 scale
    speed: float  # 0-1 scale
    strength: float  # 0-1 scale
    intelligence: float  # 0-1 scale
    longitude: float
    latitude: float
    needs: AnimalNeeds = field(default_factory=AnimalNeeds)
    state: AnimalState = field(default_factory=AnimalState)
    is_domesticated: bool = False
    owner_id: Optional[str] = None
    training_progress: float = 0.0
    reproduction_cooldown: float = 0.0
    last_action: str = "idle"
    last_action_time: float = 0.0
    diet: List[str] = field(default_factory=list)
    social_group: Optional[str] = None
    territory: Optional[AnimalTerritory] = None
    energy: float = 100.0  # 0-100, 0 means exhausted

    def __init__(self, id: str, type: AnimalType, name: str, temperament: AnimalTemperament, size: float, speed: float, strength: float, intelligence: float, longitude: float, latitude: float, radius: float = 5.0):
        self.id = id
        self.type = type
        self.name = name
        self.temperament = temperament
        self.size = size
        self.speed = speed
        self.strength = strength
        self.intelligence = intelligence
        self.longitude = longitude
        self.latitude = latitude
        self.needs = AnimalNeeds()
        self.state = AnimalState()
        self.is_domesticated = False
        self.owner_id = None
        self.training_progress = 0.0
        self.reproduction_cooldown = 0.0
        self.last_action = "idle"
        self.last_action_time = 0.0
        self.diet = []
        self.social_group = None
        self.territory = AnimalTerritory(
            center_longitude=longitude,
            center_latitude=latitude,
            radius=radius,
            claimed_by=id
        )
        self.energy = 100.0

    def is_in_territory(self, longitude: float, latitude: float) -> bool:
        """Check if a location is within the animal's territory"""
        if not self.territory:
            return False
        distance = self.world.get_distance(
            longitude, latitude,
            self.territory.center_longitude,
            self.territory.center_latitude
        )
        return distance <= self.territory.radius

    def expand_territory(self, new_longitude: float, new_latitude: float, new_radius: float) -> None:
        """Expand the animal's territory to include a new area"""
        if not self.territory:
            self.territory = AnimalTerritory(
                center_longitude=new_longitude,
                center_latitude=new_latitude,
                radius=new_radius,
                claimed_by=self.id
            )
        else:
            # Calculate new center as midpoint between old center and new location
            self.territory.center_longitude = (self.territory.center_longitude + new_longitude) / 2
            self.territory.center_latitude = (self.territory.center_latitude + new_latitude) / 2
            self.territory.radius = max(self.territory.radius, new_radius)

class AnimalSystem:
    def __init__(self, world):
        """Initialize the animal system."""
        self.world = world
        self.logger = get_logger(__name__)
        
        # Initialize animal components
        self.animals = {}  # animal_id -> animal_data
        self.populations = {}  # animal_type -> count
        self.territories = {}  # territory_id -> territory_data
        self.social_groups = {}  # group_id -> group_data
        
        # Initialize animal types and their properties
        self._initialize_animal_types()
        
        # Initialize animal distribution
        self._initialize_animal_distribution()
        
        self.logger.info("Animal system initialized")

    def initialize_animal_system(self):
        """Initialize the complete animal system."""
        self.logger.info("Initializing animal system...")
        
        # Initialize animal types and their properties
        self._initialize_animal_types()
        
        # Initialize animal distribution
        self._initialize_animal_distribution()
        
        # Initialize relationships
        self._initialize_predator_prey_relationships()
        self._initialize_symbiotic_relationships()
        self._initialize_social_structures()
        
        self.logger.info("Animal system initialization complete")

    def _generate_animal_id(self, animal_type: str) -> str:
        """Generate a unique ID for a new animal."""
        # Get the list of animals of this type
        animal_list = getattr(self, f"{animal_type}s", {})
        # Generate ID with type and count
        new_animal_id = f"{animal_type}_{len(animal_list) + 1}"
        return new_animal_id

    def get_state(self) -> Dict:
        """Get the current state of the animal system."""
        logger.info("Starting animal system state serialization...")
        
        def convert_animal_to_dict(animal) -> Dict:
            try:
                # If it's already a dict, just convert its keys
                if isinstance(animal, dict):
                    logger.info(f"Converting animal dict with id {animal.get('id', 'unknown')}...")
                    return convert_dict(animal)
                
                # Otherwise convert Animal object to dict
                logger.info(f"Converting animal object {animal.id} to dict...")
                
                # Convert territory to dict if it exists
                territory = None
                if animal.territory:
                    territory = {
                        'center_longitude': animal.territory.center_longitude,
                        'center_latitude': animal.territory.center_latitude,
                        'radius': animal.territory.radius,
                        'claimed_by': animal.territory.claimed_by,
                        'resources': animal.territory.resources,
                        'history': animal.territory.history
                    }
                
                return {
                    'id': animal.id,
                    'type': animal.type.value,
                    'name': animal.name,
                    'temperament': animal.temperament.value,
                    'size': animal.size,
                    'speed': animal.speed,
                    'strength': animal.strength,
                    'intelligence': animal.intelligence,
                    'longitude': animal.longitude,
                    'latitude': animal.latitude,
                    'needs': {
                        'hunger': animal.needs.hunger,
                        'thirst': animal.needs.thirst,
                        'energy': animal.needs.energy,
                        'health': animal.needs.health,
                        'reproduction_urge': animal.needs.reproduction_urge,
                        'social_need': animal.needs.social_need,
                        'comfort': animal.needs.comfort,
                        'water_quality': animal.needs.water_quality
                    },
                    'state': {
                        'is_sick': animal.state.is_sick,
                        'disease_resistance': animal.state.disease_resistance,
                        'pregnancy_progress': animal.state.pregnancy_progress,
                        'age': animal.state.age,
                        'lifespan': animal.state.lifespan,
                        'maturity_age': animal.state.maturity_age,
                        'last_meal_time': animal.state.last_meal_time,
                        'last_water_time': animal.state.last_water_time,
                        'last_rest_time': animal.state.last_rest_time,
                        'last_social_time': animal.state.last_social_time
                    },
                    'is_domesticated': animal.is_domesticated,
                    'owner_id': animal.owner_id,
                    'training_progress': animal.training_progress,
                    'reproduction_cooldown': animal.reproduction_cooldown,
                    'last_action': animal.last_action,
                    'last_action_time': animal.last_action_time,
                    'diet': animal.diet,
                    'social_group': animal.social_group,
                    'territory': territory,
                    'energy': animal.energy
                }
            except Exception as e:
                logger.error(f"Error converting animal {getattr(animal, 'id', animal.get('id', 'unknown'))}: {e}")
                logger.error(traceback.format_exc())
                raise

        def convert_coords_to_str(coords):
            if isinstance(coords, tuple):
                return f"{coords[0]},{coords[1]}"
            return str(coords)

        def convert_dict(d):
            if isinstance(d, dict):
                return {str(k): convert_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [convert_dict(item) for item in d]
            elif isinstance(d, tuple):
                return convert_coords_to_str(d)
            elif isinstance(d, (AnimalType, AnimalTemperament, WaterType)):
                return d.value
            return d

        try:
            logger.info("Converting animals...")
            animals_dict = {str(animal_id): convert_animal_to_dict(animal) for animal_id, animal in self.animals.items()}
            logger.info(f"Converted {len(animals_dict)} animals")

            logger.info("Converting populations...")
            populations_dict = {str(k): v for k, v in self.populations.items()}
            logger.info(f"Converted populations: {populations_dict}")

            logger.info("Converting territories...")
            territories_dict = {convert_coords_to_str(territory_id): convert_dict(territory) for territory_id, territory in self.territories.items()}
            logger.info(f"Converted {len(territories_dict)} territories")

            logger.info("Converting social groups...")
            social_groups_dict = convert_dict(self.social_groups)
            logger.info(f"Converted {len(social_groups_dict)} social groups")

            state = {
                'animals': animals_dict,
                'populations': populations_dict,
                'territories': territories_dict,
                'social_groups': social_groups_dict
            }
            logger.info("Successfully created animal system state")
            return state

        except Exception as e:
            logger.error(f"Error getting animal state: {e}")
            logger.error(traceback.format_exc())
            return {'error': str(e)}

    def _initialize_animal_types(self):
        """Initialize animal types and their properties."""
        # Initialize traits for different animal types
        self.traits = {
            "herbivore": {
                "speed": 0.7,
                "strength": 0.4,
                "senses": 0.6,
                "intelligence": 0.5,
                "social": 0.6,
                "territorial": 0.4
            },
            "carnivore": {
                "speed": 0.8,
                "strength": 0.7,
                "senses": 0.8,
                "intelligence": 0.6,
                "social": 0.5,
                "territorial": 0.7
            },
            "omnivore": {
                "speed": 0.6,
                "strength": 0.5,
                "senses": 0.7,
                "intelligence": 0.7,
                "social": 0.7,
                "territorial": 0.5
            }
        }
        
        # Initialize behaviors for different animal types
        self.behaviors = {
            "herbivore": {
                "grazing": 0.8,
                "fleeing": 0.7,
                "socializing": 0.6,
                "territorial": 0.4
            },
            "carnivore": {
                "hunting": 0.8,
                "territorial": 0.7,
                "socializing": 0.5,
                "resting": 0.6
            },
            "omnivore": {
                "foraging": 0.7,
                "hunting": 0.5,
                "socializing": 0.6,
                "territorial": 0.5
            }
        }
        
        # Initialize habitats
        self.habitats = {
            "forest": set(),
            "grassland": set(),
            "mountain": set(),
            "river": set(),
            "lake": set(),
            "ocean": set()
        }
        
        # Initialize relationships
        self.predator_prey = {}
        self.symbiotic = {}
        self.competition = {}
        
        # Initialize events list
        self.events = []
        
    def _initialize_animal_distribution(self):
        """Initialize the distribution of animals across the world."""
        # Initialize populations for each animal type
        for animal_type in AnimalType:
            self.populations[animal_type.value] = 0
        
        # Initialize animal type-specific collections
        self.herbivores = {}
        self.carnivores = {}
        self.omnivores = {}
        self.domesticated = {}
        
        # Create initial animals
        self._create_initial_animals()
        
        # Initialize relationships
        self._initialize_predator_prey_relationships()
        self._initialize_symbiotic_relationships()
        self._initialize_social_structures()
        
        self.logger.info("Animal distribution initialized")

    def _create_initial_animals(self):
        """Create initial animals for the simulation."""
        self.logger.info("Starting to create initial animals...")
        
        # Define the number of pairs to create for each type
        pairs_per_type = 1  # 1 pair = 2 animals of each type
        total_animals = len(AnimalType) * pairs_per_type * 2
        animals_created = 0
        
        # Create pairs for each animal type
        for animal_type in AnimalType:
            self.logger.info(f"Creating {pairs_per_type} pairs of {animal_type.value}...")
            
            for i in range(pairs_per_type):
                # Create female
                female_id = self._generate_animal_id(animal_type.value)
                female = self._create_animal(female_id, animal_type)
                female['gender'] = 'female'
                self.animals[female_id] = female
                self.populations[animal_type.value] += 1
                animals_created += 1
                self.logger.info(f"Created female {animal_type.value} (ID: {female_id}) - {animals_created}/{total_animals} animals ({int(animals_created/total_animals*100)}% complete)")
                
                # Create male
                male_id = self._generate_animal_id(animal_type.value)
                male = self._create_animal(male_id, animal_type)
                male['gender'] = 'male'
                self.animals[male_id] = male
                self.populations[animal_type.value] += 1
                animals_created += 1
                self.logger.info(f"Created male {animal_type.value} (ID: {male_id}) - {animals_created}/{total_animals} animals ({int(animals_created/total_animals*100)}% complete)")
        
        self.logger.info(f"Animal creation complete. Created {animals_created} animals in total.")
        self.logger.info(f"Current populations: {self.populations}")

    def _create_animal(self, animal_id: str, animal_type: AnimalType) -> Dict:
        """Create a new animal with the given type."""
        # Generate random position within world bounds
        longitude = random.uniform(self.world.min_longitude, self.world.max_longitude)
        latitude = random.uniform(self.world.min_latitude, self.world.max_latitude)
        
        return {
            'id': animal_id,
            'type': animal_type.value,
            'name': f"{animal_type.value.capitalize()}_{animal_id}",
            'temperament': random.choice(list(AnimalTemperament)).value,
            'size': random.uniform(0.3, 1.0),
            'speed': random.uniform(0.3, 1.0),
            'strength': random.uniform(0.3, 1.0),
            'intelligence': random.uniform(0.3, 1.0),
            'longitude': longitude,
            'latitude': latitude,
            'needs': {
                'hunger': 100.0,
                'thirst': 100.0,
                'energy': 100.0,
                'health': 100.0,
                'reproduction_urge': 0.0,
                'social_need': 50.0,
                'comfort': 100.0,
                'water_quality': 100.0
            },
            'state': {
                'is_sick': False,
                'disease_resistance': 100.0,
                'pregnancy_progress': 0.0,
                'age': 0.0,
                'lifespan': random.uniform(5.0, 15.0),
                'maturity_age': random.uniform(1.0, 3.0),
                'last_meal_time': 0.0,
                'last_water_time': 0.0,
                'last_rest_time': 0.0,
                'last_social_time': 0.0
            },
            'is_domesticated': False,
            'owner_id': None,
            'training_progress': 0.0,
            'reproduction_cooldown': 0.0,
            'last_action': 'idle',
            'last_action_time': 0.0,
            'diet': [],
            'social_group': None,
            'territory': {
                'center_longitude': longitude,
                'center_latitude': latitude,
                'radius': 5.0,
                'claimed_by': animal_id,
                'resources': {},
                'history': []
            },
            'energy': 100.0
        }
    
    def _update_populations(self, time_delta: float, environment: Dict):
        """Update animal populations"""
        # Update herbivores
        self._update_herbivores(time_delta, environment)
        
        # Update carnivores
        self._update_carnivores(time_delta, environment)
        
        # Update omnivores
        self._update_omnivores(time_delta, environment)
        
        # Update domesticated animals
        self._update_domesticated(time_delta, environment)
    
    def _update_herbivores(self, time_delta: float, environment: Dict):
        """Update herbivore population"""
        for animal_id, animal in self.herbivores.items():
            # Animal eats
            self._update_animal_food(animal)
            # Update health based on food availability
            food_availability = environment.get("vegetation", 0.5)
            health_change = (food_availability - 0.5) * time_delta
            animal["health"] = max(0.0, min(1.0, animal["health"] + health_change))
            
            # Update position based on behavior
            if animal["health"] > 0.3:
                self._move_animal(animal_id, animal, "herbivore")
            
            # Check for reproduction
            if animal["health"] > 0.7 and animal["age"] > 2.0:
                self._reproduce_animal(animal_id, animal, "herbivore")
            
            # Check for death
            if animal["health"] < 0.1 or animal["age"] > 10.0:
                self._remove_animal(animal_id, "herbivore")
    
    def _update_carnivores(self, time_delta: float, environment: Dict):
        """Update carnivore population"""
        for animal_id, animal in self.carnivores.items():
            # Animal eats
            self._update_animal_food(animal)
            # Update health based on prey availability
            prey_availability = len(self.herbivores) / 100.0
            health_change = (prey_availability - 0.5) * time_delta
            animal["health"] = max(0.0, min(1.0, animal["health"] + health_change))
            
            # Update position based on behavior
            if animal["health"] > 0.3:
                self._move_animal(animal_id, animal, "carnivore")
            
            # Check for reproduction
            if animal["health"] > 0.7 and animal["age"] > 3.0:
                self._reproduce_animal(animal_id, animal, "carnivore")
            
            # Check for death
            if animal["health"] < 0.1 or animal["age"] > 8.0:
                self._remove_animal(animal_id, "carnivore")
    
    def _update_omnivores(self, time_delta: float, environment: Dict):
        """Update omnivore population"""
        for animal_id, animal in self.omnivores.items():
            # Animal eats
            self._update_animal_food(animal)
            # Update health based on food availability
            food_availability = (environment.get("vegetation", 0.5) + 
                               len(self.herbivores) / 100.0) / 2
            health_change = (food_availability - 0.5) * time_delta
            animal["health"] = max(0.0, min(1.0, animal["health"] + health_change))
            
            # Update position based on behavior
            if animal["health"] > 0.3:
                self._move_animal(animal_id, animal, "omnivore")
            
            # Check for reproduction
            if animal["health"] > 0.7 and animal["age"] > 2.5:
                self._reproduce_animal(animal_id, animal, "omnivore")
            
            # Check for death
            if animal["health"] < 0.1 or animal["age"] > 9.0:
                self._remove_animal(animal_id, "omnivore")
    
    def _update_domesticated(self, time_delta: float, environment: Dict):
        """Update domesticated animal population"""
        for animal_id, animal in self.domesticated.items():
            # Animal eats
            self._update_animal_food(animal)
            # Update health based on care
            care_quality = animal.get("care_quality", 0.5)
            health_change = (care_quality - 0.5) * time_delta
            animal["health"] = max(0.0, min(1.0, animal["health"] + health_change))
            
            # Update position based on behavior
            if animal["health"] > 0.3:
                self._move_animal(animal_id, animal, "domesticated")
            
            # Check for reproduction
            if animal["health"] > 0.7 and animal["age"] > 2.0:
                self._reproduce_animal(animal_id, animal, "domesticated")
            
            # Check for death
            if animal["health"] < 0.1 or animal["age"] > 12.0:
                self._remove_animal(animal_id, "domesticated")
    
    def _move_animal(self, animal_id: str, animal: Dict, animal_type: str):
        """Move an animal considering terrain, water type, and energy costs."""
        # Get current terrain info
        current_terrain = self.world.terrain.get_terrain_info_at(animal['longitude'], animal['latitude'])
        current_elevation = self.world.terrain.get_elevation_at(animal['longitude'], animal['latitude'])
        current_slope = self.world.terrain.get_slope_at(animal['longitude'], animal['latitude'])
        
        # Calculate movement cost based on terrain and animal type
        movement_cost = self._calculate_movement_cost(animal, current_terrain, current_slope)
        
        # Check if animal has enough energy to move
        if animal['needs']['energy'] < movement_cost:
            # Animal is too tired to move
            animal['last_action'] = "resting"
            animal['needs']['energy'] = min(100.0, animal['needs']['energy'] + 0.3)
            return
        
        # Calculate possible movement range based on energy and animal speed
        max_distance = min(0.01 * animal['speed'], animal['needs']['energy'] / movement_cost)
        
        # Generate random movement within energy constraints
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, max_distance)
        
        # Calculate new position
        new_lon = animal['longitude'] + distance * math.cos(angle)
        new_lat = animal['latitude'] + distance * math.sin(angle)
        
        # Check if new position is valid for this animal type
        if not self._is_valid_position(new_lon, new_lat, animal):
            return
        
        # Get terrain at new position
        new_terrain = self.world.terrain.get_terrain_info_at(new_lon, new_lat)
        new_elevation = self.world.terrain.get_elevation_at(new_lon, new_lat)
        new_slope = self.world.terrain.get_slope_at(new_lon, new_lat)
        
        # Calculate elevation change cost
        elevation_change = abs(new_elevation - current_elevation)
        elevation_cost = elevation_change * (2.0 / animal['size'])
        
        # Check if animal has enough energy for the elevation change
        if animal['needs']['energy'] < (movement_cost + elevation_cost):
            return
        
        # Update position
        animal['longitude'] = new_lon
        animal['latitude'] = new_lat
        
        # Update energy based on movement and terrain
        animal['needs']['energy'] = max(0.0, animal['needs']['energy'] - (movement_cost + elevation_cost))
        
        # Update last action
        if elevation_change > 0:
            animal['last_action'] = "climbing" if new_elevation > current_elevation else "descending"
        else:
            animal['last_action'] = "moving"
    
    def _calculate_movement_cost(self, animal: Dict, terrain_info: Dict, slope: float) -> float:
        """Calculate the energy cost of movement based on terrain, slope, and animal type."""
        base_cost = 1.0
        
        # Terrain-specific costs
        terrain_costs = {
            "MOUNTAIN": 5.0,
            "HILLS": 3.0,
            "FOREST": 2.0,
            "SWAMP": 4.0,
            "RIVER": 3.0,
            "LAKE": 5.0,  # Can't move through lakes
            "OCEAN": 10.0,  # Can't move through oceans
            "GLACIER": 6.0,
            "DESERT": 2.0,
            "GRASSLAND": 1.0,
            "PLAINS": 1.0
        }
        
        # Animal-specific terrain modifiers
        animal_terrain_modifiers = {
            "HORSE": {"PLAINS": 0.5, "GRASSLAND": 0.5, "HILLS": 1.5},  # Horses are fast on plains
            "WOLF": {"FOREST": 0.7, "HILLS": 0.8},  # Wolves are good in forests and hills
            "DEER": {"FOREST": 0.6, "GRASSLAND": 0.8},  # Deer are good in forests
            "BEAR": {"MOUNTAIN": 0.8, "FOREST": 0.7},  # Bears are good in mountains and forests
            "RABBIT": {"GRASSLAND": 0.5, "FOREST": 0.7},  # Rabbits are fast on grasslands
            "SHEEP": {"HILLS": 0.7, "GRASSLAND": 0.8},  # Sheep are good on hills
            "COW": {"PLAINS": 0.6, "GRASSLAND": 0.7},  # Cows are good on plains
            "GOAT": {"MOUNTAIN": 0.6, "HILLS": 0.7}  # Goats are good in mountains
        }
        
        terrain_type = terrain_info.get("type", "PLAINS")
        terrain_cost = terrain_costs.get(terrain_type, 1.0)
        
        # Apply animal-specific terrain modifier
        animal_type = animal['type'].value
        terrain_modifier = animal_terrain_modifiers.get(animal_type, {}).get(terrain_type, 1.0)
        
        # Slope cost (0-1 scale)
        slope_cost = 1.0 + (slope * 4.0)  # Steeper slopes cost more energy
        
        # Size modifier (smaller animals pay more for movement)
        size_modifier = 1.0 / animal['size']
        
        return base_cost * terrain_cost * terrain_modifier * slope_cost * size_modifier
    
    def _is_valid_position(self, lon: float, lat: float, animal: Dict) -> bool:
        """Check if a position is valid for movement for this animal type."""
        # Check world bounds
        if not (self.world.min_longitude <= lon <= self.world.max_longitude and
                self.world.min_latitude <= lat <= self.world.max_latitude):
            return False
        
        # Check if position is in impassable terrain
        terrain_info = self.world.terrain.get_terrain_info_at(lon, lat)
        terrain_type = terrain_info.get("type", "PLAINS")
        
        # Define impassable terrain for different animal types
        impassable_terrain = {
            "HORSE": {"OCEAN", "LAKE", "RIVER", "GLACIER", "MOUNTAIN"},
            "WOLF": {"OCEAN", "LAKE", "RIVER"},
            "DEER": {"OCEAN", "LAKE", "RIVER"},
            "BEAR": {"OCEAN", "LAKE"},
            "RABBIT": {"OCEAN", "LAKE", "RIVER", "MOUNTAIN"},
            "SHEEP": {"OCEAN", "LAKE", "RIVER", "MOUNTAIN"},
            "COW": {"OCEAN", "LAKE", "RIVER", "MOUNTAIN", "HILLS"},
            "GOAT": {"OCEAN", "LAKE", "RIVER"}
        }
        
        animal_type = animal['type'].value
        return terrain_type not in impassable_terrain.get(animal_type, {"OCEAN", "LAKE"})
    
    def _reproduce_animal(self, animal_id: str, animal: Dict, animal_type: str):
        """Create new animal through reproduction"""
        if random.random() < 0.1:  # 10% chance of reproduction
            new_animal_id = self._generate_animal_id(animal_type)
            new_animal = self._create_animal(new_animal_id, AnimalType(animal['type']))
            
            # Add to appropriate collection
            if animal_type == "herbivore":
                self.herbivores[new_animal_id] = new_animal
            elif animal_type == "carnivore":
                self.carnivores[new_animal_id] = new_animal
            elif animal_type == "omnivore":
                self.omnivores[new_animal_id] = new_animal
            elif animal_type == "domesticated":
                self.domesticated[new_animal_id] = new_animal
            
            # Add to main animals collection
            self.animals[new_animal_id] = new_animal
            
            # Update population count
            self.populations[animal['type']] = self.populations.get(animal['type'], 0) + 1
            
            # Record reproduction event
            self.events.append({
                "type": "reproduction",
                "timestamp": datetime.now().isoformat(),
                "parent_id": animal_id,
                "child_id": new_animal_id,
                "animal_type": animal['type']
            })
    
    def _remove_animal(self, animal_id: str, animal_type: str):
        """Remove animal from population"""
        if animal_id in self.animals:
            animal = self.animals[animal_id]
            
            # Remove from appropriate collection
            if animal_type == "herbivore" and animal_id in self.herbivores:
                del self.herbivores[animal_id]
            elif animal_type == "carnivore" and animal_id in self.carnivores:
                del self.carnivores[animal_id]
            elif animal_type == "omnivore" and animal_id in self.omnivores:
                del self.omnivores[animal_id]
            elif animal_type == "domesticated" and animal_id in self.domesticated:
                del self.domesticated[animal_id]
            
            # Remove from main animals collection
            del self.animals[animal_id]
            
            # Update population count
            if animal['type'] in self.populations:
                self.populations[animal['type']] = max(0, self.populations[animal['type']] - 1)
            
            # Record death event
            self.events.append({
                "type": "death",
                "timestamp": datetime.now().isoformat(),
                "animal_id": animal_id,
                "animal_type": animal['type'],
                "cause": animal.get('last_action', 'unknown')
            })
    
    def _inherit_traits(self, parent_traits: Dict, animal_type: str) -> Dict:
        """Create new traits based on parent traits"""
        base_traits = self.traits[animal_type].copy()
        for trait, value in base_traits.items():
            if trait in parent_traits:
                # Inherit with small mutation
                base_traits[trait] = max(0.0, min(1.0,
                    parent_traits[trait] + random.uniform(-0.1, 0.1)))
        return base_traits
    
    def _update_behaviors(self, time_delta: float):
        """Update animal behaviors"""
        for animal_type, behaviors in self.behaviors.items():
            for behavior, value in behaviors.items():
                # Behaviors can evolve slightly
                self.behaviors[animal_type][behavior] = max(0.0, min(1.0,
                    value + random.uniform(-0.01, 0.01) * time_delta))
    
    def _update_interactions(self, time_delta: float):
        """Update animal interactions"""
        # Update predator-prey relationships
        self._update_predator_prey(time_delta)
        
        # Update symbiotic relationships
        self._update_symbiotic(time_delta)
        
        # Update competitive relationships
        self._update_competition(time_delta)
    
    def _update_predator_prey(self, time_delta: float):
        """Update predator-prey relationships"""
        for predator_id, prey_id in self.predator_prey.items():
            if predator_id in self.carnivores and prey_id in self.herbivores:
                predator = self.carnivores[predator_id]
                prey = self.herbivores[prey_id]
                
                # Check if predator can catch prey
                if self._can_catch_prey(predator, prey):
                    # Predator catches prey
                    self._remove_animal(prey_id, "herbivore")
                    predator["health"] = min(1.0, predator["health"] + 0.3)
    
    def _can_catch_prey(self, predator: Dict, prey: Dict) -> bool:
        """Check if predator can catch prey"""
        predator_traits = predator.get("traits", self.traits["carnivore"])
        prey_traits = prey.get("traits", self.traits["herbivore"])
        
        # Calculate catch probability based on traits
        catch_prob = (
            predator_traits["speed"] * 0.4 +
            predator_traits["strength"] * 0.3 +
            predator_traits["senses"] * 0.3 -
            prey_traits["speed"] * 0.4 -
            prey_traits["senses"] * 0.3
        )
        
        return random.random() < catch_prob
    
    def _update_symbiotic(self, time_delta: float):
        """Update symbiotic relationships"""
        for animal1_id, animal2_id in self.symbiotic.items():
            if animal1_id in self.herbivores and animal2_id in self.herbivores:
                animal1 = self.herbivores[animal1_id]
                animal2 = self.herbivores[animal2_id]
                
                # Both animals benefit
                animal1["health"] = min(1.0, animal1["health"] + 0.01 * time_delta)
                animal2["health"] = min(1.0, animal2["health"] + 0.01 * time_delta)
    
    def _update_competition(self, time_delta: float):
        """Update competitive relationships"""
        for animal1_id, animal2_id in self.competition.items():
            if animal1_id in self.herbivores and animal2_id in self.herbivores:
                animal1 = self.herbivores[animal1_id]
                animal2 = self.herbivores[animal2_id]
                
                # Both animals lose health
                animal1["health"] = max(0.0, animal1["health"] - 0.01 * time_delta)
                animal2["health"] = max(0.0, animal2["health"] - 0.01 * time_delta)
    
    def _update_habitats(self, time_delta: float, environment: Dict):
        """Update animal habitats"""
        for habitat, animals in self.habitats.items():
            # Update habitat suitability
            suitability = environment.get(f"{habitat}_suitability", 0.5)
            
            # Animals can move between habitats
            if random.random() < 0.01 * time_delta:
                if suitability > 0.7:
                    # Animals move to this habitat
                    self._add_animal_to_habitat(habitat)
                elif suitability < 0.3:
                    # Animals leave this habitat
                    self._remove_animal_from_habitat(habitat)
    
    def _add_animal_to_habitat(self, habitat: str):
        """Add animal to habitat"""
        animal_type = random.choice(["herbivore", "carnivore", "omnivore"])
        if animal_type in self.populations:
            self.habitats[habitat].add(f"{animal_type}_{self.populations[animal_type]}")
    
    def _remove_animal_from_habitat(self, habitat: str):
        """Remove animal from habitat"""
        if self.habitats[habitat]:
            self.habitats[habitat].pop()
    
    def _record_events(self):
        """Record significant animal events"""
        # Record population changes
        if random.random() < 0.1:
            self.events.append({
                "type": "population_change",
                "timestamp": datetime.now().isoformat(),
                "description": f"Significant population change occurred",
                "populations": self.populations.copy()
            })

    def _initialize_predator_prey_relationships(self):
        """Initialize predator-prey relationships."""
        logger.info("Initializing predator-prey relationships...")
        
        # Initialize predator-prey relationships
        self.predator_prey = {}
        for predator_id, predator in self.carnivores.items():
            for prey_id, prey in self.herbivores.items():
                if self._can_catch_prey(predator, prey):
                    self.predator_prey[(predator_id, prey_id)] = True
        logger.info("Predator-prey relationships initialized")
    
    def _initialize_symbiotic_relationships(self):
        """Initialize symbiotic relationships."""
        logger.info("Initializing symbiotic relationships...")
        
        # Initialize symbiotic relationships
        self.symbiotic = {}
        for herbivore1_id, herbivore1 in self.herbivores.items():
            for herbivore2_id, herbivore2 in self.herbivores.items():
                if herbivore1_id != herbivore2_id:
                    self.symbiotic[(herbivore1_id, herbivore2_id)] = True
        logger.info("Symbiotic relationships initialized")
    
    def _initialize_social_structures(self):
        """Initialize social structures."""
        logger.info("Initializing social structures...")
        
        # Initialize social structures
        self.social_structures = {}
        for animal_id, animal in self.herbivores.items():
            self.social_structures[animal_id] = {
                "group": None,
                "territory": None
            }
        logger.info("Social structures initialized")
        
        logger.info("Animal ecosystems initialization complete")

    def _update_animal_food(self, animal: dict):
        """Update animal's food consumption using CookingSystem."""
        cooking_system = CookingSystem()
        food_items = [item for item in animal.get('inventory', {}) if item in FoodType._value2member_map_]
        for food_item in food_items:
            if animal['needs']['hunger'] < 80.0 and animal['inventory'][food_item] > 0:
                food_type = FoodType(food_item)
                props = cooking_system.get_food_properties(food_type)
                if not props:
                    continue
                # Consume one unit of food
                animal['inventory'][food_item] = max(0.0, animal['inventory'][food_item] - 1.0)
                # Update hunger
                animal['needs']['hunger'] = min(100.0, animal['needs']['hunger'] + props.nutritional_value)
                # Health effect
                animal['needs']['health'] = max(0.0, min(100.0, animal['needs']['health'] + props.health_effect))
                # Sickness risk
                if props.food_safety_risk > 50.0 and random.random() < (props.food_safety_risk / 100.0):
                    animal['needs']['health'] = max(0.0, animal['needs']['health'] - 20.0)  # Sickness penalty
                break  # Only eat one food per update

    def update(self, time_delta: float) -> None:
        """Update the animal system for the given time delta.
        
        Args:
            time_delta: Time elapsed in game minutes
        """
        self.logger.info(f"Updating animal system for {time_delta} minutes")
        
        # Get current environment state
        environment = self.world.to_dict()
        
        # Update populations
        self._update_populations(time_delta, environment)
        
        # Update different types of animals
        self._update_herbivores(time_delta, environment)
        self._update_carnivores(time_delta, environment)
        self._update_omnivores(time_delta, environment)
        self._update_domesticated(time_delta, environment)
        
        # Update behaviors and interactions
        self._update_behaviors(time_delta)
        self._update_interactions(time_delta)
        
        # Update habitats
        self._update_habitats(time_delta, environment)
        
        # Record events
        self._record_events()
        
        self.logger.info("Animal system update complete") 