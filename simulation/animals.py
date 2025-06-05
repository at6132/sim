from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import random
import math
import time
from datetime import datetime
import numpy as np
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class AnimalType(Enum):
    HORSE = "horse"
    WOLF = "wolf"
    DEER = "deer"
    BEAR = "bear"
    RABBIT = "rabbit"
    SHEEP = "sheep"  # New herding animal
    COW = "cow"      # New herding animal
    GOAT = "goat"    # New herding animal

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

    def _generate_animal_id(self, animal_type: str) -> str:
        """Generate a unique ID for a new animal."""
        # Get the list of animals of this type
        animal_list = getattr(self, f"{animal_type}s")
        # Generate ID with type and count
        new_animal_id = f"{animal_type}_{len(animal_list)}"
        return new_animal_id

class AnimalSystem:
    def __init__(self, world):
        """Initialize the animal system."""
        logger.info("Initializing animal system...")
        
        # Store world reference
        self.world = world
        
        # Initialize animal populations
        logger.info("Setting up animal populations...")
        self.herbivores = {}  # Plant-eating animals
        self.carnivores = {}  # Meat-eating animals
        self.omnivores = {}  # Mixed diet animals
        self.domesticated = {}  # Tamed animals
        logger.info("Animal populations initialized")


        # Unified mapping accessor for all animals is provided by the
        # ``animals`` property defined on the class.

    @property
    def animals(self) -> Dict[str, Dict]:
        """Return a combined mapping of all animals."""
        combined = {}
        combined.update(self.herbivores)
        combined.update(self.carnivores)
        combined.update(self.omnivores)
        combined.update(self.domesticated)
        return combined

    # Backwards compatibility for world code expecting ``creatures``
    @property
    def creatures(self) -> Dict[str, Dict]:
        """Alias for :pyattr:`animals`."""
        return self.animals

        
        # Initialize animal behaviors
        logger.info("Setting up animal behaviors...")
        self.behaviors = {
            "herbivore": {
                "foraging": 0.8,
                "fleeing": 0.7,
                "grazing": 0.9,
                "migration": 0.6
            },
            "carnivore": {
                "hunting": 0.8,
                "territorial": 0.7,
                "pack_behavior": 0.6,
                "stalking": 0.9
            },
            "omnivore": {
                "foraging": 0.7,
                "hunting": 0.5,
                "scavenging": 0.8,
                "adaptability": 0.9
            },
            "domesticated": {
                "obedience": 0.8,
                "loyalty": 0.7,
                "trainability": 0.6,
                "dependency": 0.9
            }
        }
        logger.info("Animal behaviors initialized")
        
        # Initialize animal traits
        logger.info("Setting up animal traits...")
        self.traits = {
            "herbivore": {
                "speed": 0.7,
                "strength": 0.4,
                "intelligence": 0.5,
                "senses": 0.6
            },
            "carnivore": {
                "speed": 0.8,
                "strength": 0.9,
                "intelligence": 0.7,
                "senses": 0.8
            },
            "omnivore": {
                "speed": 0.6,
                "strength": 0.6,
                "intelligence": 0.6,
                "senses": 0.7
            },
            "domesticated": {
                "speed": 0.5,
                "strength": 0.5,
                "intelligence": 0.8,
                "senses": 0.6
            }
        }
        logger.info("Animal traits initialized")
        
        # Initialize animal distribution
        logger.info("Initializing animal distribution...")
        self.initialize_animals()
        logger.info("Animal distribution initialized")
        
        logger.info("Animal system initialization complete")
        
    def initialize_animals(self):
        """Initialize animal distribution across the world."""
        logger.info("Initializing animal distribution...")
        
        # Calculate total points for progress tracking
        total_points = len(np.arange(self.world_size[0])) * len(np.arange(self.world_size[1]))
        points_processed = 0
        last_progress = 0
        
        # Process in chunks to show progress
        chunk_size = 1000  # Process 1000 points at a time
        
        for lon in np.arange(self.world_size[0]):
            for lat in np.arange(self.world_size[1]):
                # Get terrain type at location
                terrain_type = self.world.terrain.get_terrain_at(lon, lat)
                
                # Generate animals based on terrain
                logger.info(f"Generating animals for terrain type: {terrain_type}")
                self._generate_animals_for_terrain(lon, lat, terrain_type)
                
                points_processed += 1
                
                # Log progress every 10%
                progress = (points_processed / total_points) * 100
                if progress - last_progress >= 10:
                    logger.info(f"Animal distribution progress: {progress:.1f}%")
                    last_progress = progress
        
        # Initialize animal ecosystems
        logger.info("Setting up animal ecosystems...")
        self._initialize_animal_ecosystems()
        logger.info("Animal ecosystems initialized")
        
        # Initialize animal interactions
        logger.info("Setting up animal interactions...")
        self._initialize_animal_interactions()
        logger.info("Animal interactions initialized")
        
        logger.info("Animal distribution initialization complete")
        
    def _initialize_animal_ecosystems(self):
        """Initialize animal ecosystems."""
        logger.info("Initializing animal ecosystems...")
        
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
        
        logger.info("Animal ecosystems initialization complete")
        
    def _initialize_animal_interactions(self):
        """Initialize animal interactions."""
        logger.info("Initializing animal interactions...")
        
        # Initialize predator-prey relationships
        logger.info("Setting up predator-prey relationships...")
        self._initialize_predator_prey_relationships()
        logger.info("Predator-prey relationships initialized")
        
        # Initialize symbiotic relationships
        logger.info("Setting up symbiotic relationships...")
        self._initialize_symbiotic_relationships()
        logger.info("Symbiotic relationships initialized")
        
        # Initialize social structures
        logger.info("Setting up social structures...")
        self._initialize_social_structures()
        logger.info("Social structures initialized")
        
        logger.info("Animal interactions initialization complete")
        
    def _generate_animals_for_terrain(self, lon: float, lat: float, terrain_type: str):
        """Generate animals based on terrain type."""
        logger.info(f"Generating animals for terrain type: {terrain_type}")
        
        if terrain_type == "forest":
            logger.info("Generating forest animals...")
            self._generate_forest_animals(lon, lat)
            logger.info("Forest animals generated")
        elif terrain_type == "grassland":
            logger.info("Generating grassland animals...")
            self._generate_grassland_animals(lon, lat)
            logger.info("Grassland animals generated")
        elif terrain_type == "desert":
            logger.info("Generating desert animals...")
            self._generate_desert_animals(lon, lat)
            logger.info("Desert animals generated")
        elif terrain_type == "tundra":
            logger.info("Generating tundra animals...")
            self._generate_tundra_animals(lon, lat)
            logger.info("Tundra animals generated")
        elif terrain_type == "swamp":
            logger.info("Generating swamp animals...")
            self._generate_swamp_animals(lon, lat)
            logger.info("Swamp animals generated")
    
    def update(self, time_delta: float, environment: Dict):
        """Update animal system based on time and environment"""
        # Update animal populations
        self._update_populations(time_delta, environment)
        
        # Update animal behaviors
        self._update_behaviors(time_delta)
        
        # Update animal interactions
        self._update_interactions(time_delta)
        
        # Update animal habitats
        self._update_habitats(time_delta, environment)
        
        # Record significant events
        self._record_events()
    
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
        """Move animal based on its behavior"""
        # Get movement behavior
        behavior = self.behaviors[animal_type]
        
        # Calculate movement based on behavior
        if animal_type == "herbivore":
            if random.random() < behavior["migration"]:
                animal["position"] = (
                    animal["position"][0] + random.uniform(-1, 1),
                    animal["position"][1] + random.uniform(-1, 1)
                )
        elif animal_type == "carnivore":
            if random.random() < behavior["territorial"]:
                animal["position"] = (
                    animal["position"][0] + random.uniform(-2, 2),
                    animal["position"][1] + random.uniform(-2, 2)
                )
        elif animal_type == "omnivore":
            if random.random() < behavior["adaptability"]:
                animal["position"] = (
                    animal["position"][0] + random.uniform(-1.5, 1.5),
                    animal["position"][1] + random.uniform(-1.5, 1.5)
                )
        elif animal_type == "domesticated":
            if random.random() < behavior["obedience"]:
                # Stay near owner
                owner_pos = animal.get("owner_position", (0, 0))
                animal["position"] = (
                    owner_pos[0] + random.uniform(-0.5, 0.5),
                    owner_pos[1] + random.uniform(-0.5, 0.5)
                )
    
    def _reproduce_animal(self, animal_id: str, animal: Dict, animal_type: str):
        """Create new animal through reproduction"""
        if random.random() < 0.1:  # 10% chance of reproduction
            new_animal_id = self._generate_animal_id(animal_type)
            new_animal = {
                "position": (
                    animal["position"][0] + random.uniform(-0.5, 0.5),
                    animal["position"][1] + random.uniform(-0.5, 0.5)
                ),
                "health": 1.0,
                "age": 0.0,
                "traits": self._inherit_traits(animal.get("traits", {}), animal_type)
            }
            getattr(self, f"{animal_type}s")[new_animal_id] = new_animal
            self.populations[animal_type] += 1
    
    def _remove_animal(self, animal_id: str, animal_type: str):
        """Remove animal from population"""
        if animal_id in getattr(self, f"{animal_type}s"):
            del getattr(self, f"{animal_type}s")[animal_id]
            self.populations[animal_type] -= 1
    
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
    
    def get_animal_state(self) -> Dict:
        """Get current state of animal system"""
        return {
            "populations": self.populations,
            "habitats": {k: len(v) for k, v in self.habitats.items()},
            "behaviors": self.behaviors,
            "traits": self.traits,
            "interactions": {
                "predator_prey": len(self.predator_prey),
                "symbiotic": len(self.symbiotic),
                "competition": len(self.competition)
            }
        }
    
    def to_dict(self) -> Dict:
        """Convert animal system to dictionary"""
        return {
            "herbivores": self.herbivores,
            "carnivores": self.carnivores,
            "omnivores": self.omnivores,
            "domesticated": self.domesticated,
            "behaviors": self.behaviors,
            "traits": self.traits,
            "predator_prey": self.predator_prey,
            "symbiotic": self.symbiotic,
            "competition": self.competition,
            "habitats": {k: list(v) for k, v in self.habitats.items()},
            "populations": self.populations,
            "events": self.events
        }

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