import logging
import traceback
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from simulation.utils.logging_config import get_logger

logger = get_logger(__name__)

class MarineType(Enum):
    # Fish Types
    TUNA = "tuna"  # Saltwater
    SALMON = "salmon"  # Can live in both but spawn in freshwater
    TROUT = "trout"  # Freshwater
    BASS = "bass"  # Freshwater
    SHARK = "shark"  # Saltwater
    COD = "cod"  # Saltwater
    CATFISH = "catfish"  # Freshwater
    TILAPIA = "tilapia"  # Freshwater
    ANCHOVY = "anchovy"  # Saltwater
    SARDINE = "sardine"  # Saltwater
    
    # Other Marine Life
    WHALE = "whale"
    DOLPHIN = "dolphin"
    SEAL = "seal"
    OCTOPUS = "octopus"
    SQUID = "squid"
    CRAB = "crab"
    LOBSTER = "lobster"
    SHRIMP = "shrimp"

class WaterType(Enum):
    FRESHWATER = "freshwater"
    SALTWATER = "saltwater"
    BRACKISH = "brackish"  # Mix of fresh and salt water (estuaries, deltas)

@dataclass
class MarineNeeds:
    hunger: float = 100.0  # 0-100, 0 means starving
    energy: float = 100.0  # 0-100, 0 means exhausted
    health: float = 100.0  # 0-100, 0 means dead
    reproduction_urge: float = 0.0  # 0-100, increases with age and health
    social_need: float = 50.0  # 0-100, varies by species
    water_quality: float = 100.0  # 0-100, affected by water type and pollution

@dataclass
class MarineState:
    is_sick: bool = False
    disease_resistance: float = 100.0  # 0-100, affected by health and age
    pregnancy_progress: float = 0.0  # 0-100, for pregnant animals
    age: float = 0.0  # in years
    lifespan: float = 0.0  # in years, varies by species
    maturity_age: float = 0.0  # age at which animal can reproduce
    last_meal_time: float = 0.0
    last_rest_time: float = 0.0
    last_social_time: float = 0.0

@dataclass
class Marine:
    id: str
    type: MarineType
    species: str
    position: Tuple[float, float]
    age: float = 0.0
    health: float = 100.0
    size: float = 1.0
    growth_rate: float = 0.1
    reproduction_rate: float = 0.1
    spread_rate: float = 0.1
    biomass: float = 1.0
    carbon_sequestration: float = 0.0
    oxygen_production: float = 0.0
    habitat_value: float = 0.0
    resource_production: float = 0.0
    environment: Dict = field(default_factory=dict)
    needs: MarineNeeds = field(default_factory=MarineNeeds)
    state: MarineState = field(default_factory=MarineState)

class MarineSystem:
    def __init__(self, world):
        self.world = world
        self.logger = get_logger('MarineSystem')
        self.logger.info("Initializing MarineSystem...")
        
        # Initialize system components
        self.ocean_currents = {}
        self.marine_life = {}  # marine_id -> marine_data
        self.marine_resources = {}
        self.populations = {}  # marine_type -> count
        
        # Initialize the system
        self.initialize_marine_system()
        
    def initialize_marine_system(self):
        """Initialize the complete marine system."""
        self.logger.info("Starting marine system initialization...")
        
        # Initialize ocean currents
        self.logger.info("Initializing ocean currents...")
        self._initialize_ocean_currents()
        
        # Initialize marine life
        self.logger.info("Initializing marine life...")
        self._initialize_marine_life()
        
        # Initialize marine resources
        self.logger.info("Initializing marine resources...")
        self._initialize_marine_resources()
        
        self.logger.info("Marine system initialization complete")

    def _initialize_ocean_currents(self):
        """Initialize ocean currents."""
        self.logger.info("Setting up ocean currents...")
        # Very simplified ocean current model
        self.ocean_currents = {
            "equatorial_current": {
                "direction": (1.0, 0.0),
                "speed": 1.0,
                "temperature": 25.0,
            },
            "gulf_stream": {
                "direction": (0.5, 0.5),
                "speed": 2.0,
                "temperature": 18.0,
            },
            "antarctic_circumpolar": {
                "direction": (1.0, 0.0),
                "speed": 1.5,
                "temperature": 2.0,
            },
        }
        
    def _initialize_marine_life(self):
        """Initialize marine life populations."""
        self.logger.info("Setting up marine life...")
        
        # Initialize populations for each marine type
        for marine_type in MarineType:
            self.populations[marine_type.value] = 0
        
        # Create initial marine life
        self._create_initial_marine_life()
        
    def _initialize_marine_resources(self):
        """Initialize marine resources."""
        self.logger.info("Setting up marine resources...")
        self.marine_resources = {
            "plankton": 1000.0,
            "algae": 800.0,
            "coral": 500.0,
            "kelp": 600.0
        }

    def _generate_marine_id(self, marine_type: str) -> str:
        """Generate a unique ID for a new marine creature."""
        # Get the list of marine life of this type
        marine_list = {id: marine for id, marine in self.marine_life.items() 
                      if marine['type'].startswith(marine_type)}
        # Generate ID with type and count
        new_marine_id = f"{marine_type}_{len(marine_list) + 1}"
        return new_marine_id

    def _create_initial_marine_life(self):
        """Create initial marine life for the simulation."""
        self.logger.info("Starting to create initial marine life...")
        
        # Define the number of pairs to create for each type
        fish_pairs = 8  # 8 pairs = 16 fish
        mammal_pairs = 3  # 3 pairs = 6 mammals
        total_creatures = (fish_pairs * 2) + (mammal_pairs * 2)
        creatures_created = 0
        
        # Create fish pairs
        self.logger.info(f"Creating {fish_pairs} pairs of fish...")
        fish_types = [
            MarineType.TUNA, MarineType.SALMON, MarineType.TROUT,
            MarineType.BASS, MarineType.SHARK, MarineType.COD,
            MarineType.CATFISH, MarineType.TILAPIA, MarineType.ANCHOVY,
            MarineType.SARDINE
        ]
        
        for i in range(fish_pairs):
            fish_type = random.choice(fish_types)
            self.logger.info(f"Creating pair {i+1}/{fish_pairs} of {fish_type.value}...")
            
            # Create female
            female_id = self._generate_marine_id("fish")
            female = self._create_marine(female_id, fish_type, is_female=True)
            self.marine_life[female_id] = female
            self.populations[fish_type.value] += 1
            creatures_created += 1
            self.logger.info(f"Created female {fish_type.value} (ID: {female_id}) - {creatures_created}/{total_creatures} creatures ({int(creatures_created/total_creatures*100)}% complete)")
            
            # Create male
            male_id = self._generate_marine_id("fish")
            male = self._create_marine(male_id, fish_type, is_female=False)
            self.marine_life[male_id] = male
            self.populations[fish_type.value] += 1
            creatures_created += 1
            self.logger.info(f"Created male {fish_type.value} (ID: {male_id}) - {creatures_created}/{total_creatures} creatures ({int(creatures_created/total_creatures*100)}% complete)")
        
        # Create mammal pairs
        self.logger.info(f"Creating {mammal_pairs} pairs of marine mammals...")
        mammal_types = [
            MarineType.WHALE, MarineType.DOLPHIN, MarineType.SEAL
        ]
        
        for i in range(mammal_pairs):
            mammal_type = random.choice(mammal_types)
            self.logger.info(f"Creating pair {i+1}/{mammal_pairs} of {mammal_type.value}...")
            
            # Create female
            female_id = self._generate_marine_id("mammal")
            female = self._create_marine(female_id, mammal_type, is_female=True)
            self.marine_life[female_id] = female
            self.populations[mammal_type.value] += 1
            creatures_created += 1
            self.logger.info(f"Created female {mammal_type.value} (ID: {female_id}) - {creatures_created}/{total_creatures} creatures ({int(creatures_created/total_creatures*100)}% complete)")
            
            # Create male
            male_id = self._generate_marine_id("mammal")
            male = self._create_marine(male_id, mammal_type, is_female=False)
            self.marine_life[male_id] = male
            self.populations[mammal_type.value] += 1
            creatures_created += 1
            self.logger.info(f"Created male {mammal_type.value} (ID: {male_id}) - {creatures_created}/{total_creatures} creatures ({int(creatures_created/total_creatures*100)}% complete)")
        
        self.logger.info(f"Marine life creation complete. Created {creatures_created} creatures in total.")
        self.logger.info(f"Current populations: {self.populations}")

    def _create_marine(self, marine_id: str, marine_type: MarineType, is_female: bool = True) -> Marine:
        """Create a new marine creature with the given type."""
        # Generate random position within world bounds
        longitude = random.uniform(self.world.min_longitude, self.world.max_longitude)
        latitude = random.uniform(self.world.min_latitude, self.world.max_latitude)
        
        # Create Marine instance
        return Marine(
            id=marine_id,
            type=marine_type,
            species=marine_type.value,
            position=(longitude, latitude),
            age=0.0,
            health=100.0,
            size=random.uniform(0.3, 1.0),
            growth_rate=0.1,
            reproduction_rate=0.1,
            spread_rate=0.1,
            biomass=1.0,
            carbon_sequestration=0.0,
            oxygen_production=0.0,
            habitat_value=0.0,
            resource_production=0.0,
            environment={
                'terrain_type': 'WATER',
                'resources': {},
                'climate': 'TEMPERATE',
                'weather': 'CLEAR'
            },
            needs=MarineNeeds(
                hunger=100.0,
                energy=100.0,
                health=100.0,
                reproduction_urge=0.0,
                social_need=50.0,
                water_quality=100.0
            ),
            state=MarineState(
                is_sick=False,
                disease_resistance=100.0,
                pregnancy_progress=0.0,
                age=0.0,
                lifespan=random.uniform(5.0, 15.0),
                maturity_age=random.uniform(1.0, 3.0),
                last_meal_time=0.0,
                last_rest_time=0.0,
                last_social_time=0.0
            )
        )

    def _is_in_water(self, lon: float, lat: float) -> bool:
        """Check if a location is in water."""
        terrain_info = self.world.terrain.get_terrain_info_at(lon, lat)
        terrain_type = terrain_info.get("type", "PLAINS")
        return terrain_type in {"OCEAN", "LAKE", "RIVER", "ESTUARY", "DELTA"}

    def _get_water_type_at(self, lon: float, lat: float) -> Optional[WaterType]:
        """Get the type of water at a given location."""
        terrain_info = self.world.terrain.get_terrain_info_at(lon, lat)
        terrain_type = terrain_info.get("type", "PLAINS")
        
        # Map terrain types to water types
        water_type_map = {
            "OCEAN": WaterType.SALTWATER,
            "LAKE": WaterType.FRESHWATER,
            "RIVER": WaterType.FRESHWATER,
            "ESTUARY": WaterType.BRACKISH,
            "DELTA": WaterType.BRACKISH
        }
        
        return water_type_map.get(terrain_type)
        
    def update(self, time_delta: float):
        """Update the marine system state."""
        self.logger.debug(f"Updating marine system with time delta: {time_delta}")
        
        # Update each marine creature
        for marine_id, marine in list(self.marine_life.items()):
            # Update needs
            self._update_marine_needs(marine, time_delta)
            
            # Update position
            self._update_marine_position(marine, time_delta)
            
            # Check for reproduction
            if self._can_reproduce(marine):
                self._reproduce_marine(marine_id, marine)
            
            # Check for death
            if self._should_die(marine):
                self._remove_marine(marine_id, marine)

    def _update_marine_needs(self, marine: Marine, time_delta: float):
        """Update the needs of a marine creature."""
        # Decrease needs over time
        marine.needs.hunger = max(0.0, marine.needs.hunger - 0.1 * time_delta)
        marine.needs.energy = max(0.0, marine.needs.energy - 0.05 * time_delta)
        
        # Check water type compatibility
        current_water_type = self._get_water_type_at(marine.position[0], marine.position[1])
        if current_water_type != marine.environment.get('water_type'):
            marine.needs.health = max(0.0, marine.needs.health - 5.0 * time_delta)
        
        # Increase reproduction urge with age and health
        if marine.state.age > marine.state.maturity_age:
            marine.needs.reproduction_urge = min(100.0,
                marine.needs.reproduction_urge + 0.1 * time_delta)

    def _update_marine_position(self, marine: Marine, time_delta: float):
        """Update the position of a marine creature."""
        if marine.needs.energy < 20.0:
            marine.state.last_rest_time = time_delta
            marine.needs.energy = min(100.0, marine.needs.energy + 10.0 * time_delta)
            return
        
        # Calculate movement based on speed and energy
        max_distance = marine.size * (marine.needs.energy / 100.0)
        dx = random.uniform(-max_distance, max_distance)
        dy = random.uniform(-max_distance, max_distance)
        
        new_lon = marine.position[0] + dx
        new_lat = marine.position[1] + dy
        
        # Check if new position is valid
        if self._is_valid_position(new_lon, new_lat, marine):
            marine.position = (new_lon, new_lat)
            marine.needs.energy = max(0.0, marine.needs.energy - 5.0 * time_delta)
            marine.state.last_social_time = time_delta
        else:
            marine.state.last_rest_time = time_delta

    def _is_valid_position(self, lon: float, lat: float, marine: Marine) -> bool:
        """Check if a position is valid for a marine creature."""
        # Check world bounds
        if not (self.world.min_longitude <= lon <= self.world.max_longitude and
                self.world.min_latitude <= lat <= self.world.max_latitude):
            return False
        
        # Check if position is in water
        if not self._is_in_water(lon, lat):
            return False
        
        # Check water type compatibility
        water_type = self._get_water_type_at(lon, lat)
        if water_type != marine.environment.get('water_type'):
            return False
        
        return True

    def _can_reproduce(self, marine: Marine) -> bool:
        """Check if a marine creature can reproduce."""
        return (marine.needs.health > 70.0 and
                marine.needs.energy > 70.0 and
                marine.needs.reproduction_urge > 80.0 and
                marine.state.age > marine.state.maturity_age)

    def _reproduce_marine(self, parent_id: str, parent: Marine):
        """Create new marine creature through reproduction."""
        if random.random() < 0.1:  # 10% chance of reproduction
            marine_id = self._generate_marine_id(parent.type.value)
            marine = self._create_marine(marine_id, parent.type, is_female=not parent.state.is_female)
            self.marine_life[marine_id] = marine
            self.populations[parent.type.value] += 1
            
            # Reset parent's reproduction urge
            parent.needs.reproduction_urge = 0.0

    def _should_die(self, marine: Marine) -> bool:
        """Check if a marine creature should die."""
        return (marine.needs.health <= 0.0 or
                marine.needs.energy <= 0.0 or
                marine.state.age >= marine.state.lifespan)

    def _remove_marine(self, marine_id: str, marine: Marine):
        """Remove a marine creature from the system."""
        if marine_id in self.marine_life:
            del self.marine_life[marine_id]
            self.populations[marine.type.value] -= 1

    def get_state(self) -> Dict:
        """Get the current state of the marine system."""
        return {
            'marine_life': self.marine_life,
            'populations': self.populations,
            'ocean_currents': self.ocean_currents,
            'marine_resources': self.marine_resources
        }
