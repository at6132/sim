from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import random
import math
import logging
from datetime import datetime, timedelta
import numpy as np
import time

logger = logging.getLogger(__name__)

# Define marine species characteristics
MARINE_SPECIES = {
    "whale": {
        "max_age": 100,
        "max_size": 30.0,
        "max_weight": 150000,
        "habitat": {
            "type": "open_ocean",
            "temperature_range": (0, 30),
            "salinity_range": (30, 40),
            "oxygen_range": (4, 8),
            "depth_range": (0, 1000),
            "preferred_temperature": 15,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 200
        },
        "diet": ["plankton", "small_fish"],
        "migration": True,
        "social": True,
        "gestation_period": 365,
        "offspring_count": (1, 1),
        "maturity_age": 10,
        "breeding_season": "winter",
        "swimming_ability": 0.8
    },
    "dolphin": {
        "max_age": 50,
        "max_size": 4.0,
        "max_weight": 300,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 30),
            "salinity_range": (30, 40),
            "oxygen_range": (4, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 20,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["fish", "squid"],
        "migration": True,
        "social": True,
        "gestation_period": 365,
        "offspring_count": (1, 1),
        "maturity_age": 5,
        "breeding_season": "summer",
        "swimming_ability": 0.9
    },
    "shark": {
        "max_age": 70,
        "max_size": 6.0,
        "max_weight": 2000,
        "habitat": {
            "type": "open_ocean",
            "temperature_range": (5, 30),
            "salinity_range": (30, 40),
            "oxygen_range": (4, 8),
            "depth_range": (0, 1000),
            "preferred_temperature": 20,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 200
        },
        "diet": ["fish", "seals"],
        "migration": True,
        "social": False,
        "gestation_period": 365,
        "offspring_count": (2, 10),
        "maturity_age": 15,
        "breeding_season": "summer",
        "swimming_ability": 0.95
    },
    "tuna": {
        "max_age": 15,
        "max_size": 2.5,
        "max_weight": 250,
        "habitat": {
            "type": "open_ocean",
            "temperature_range": (15, 30),
            "salinity_range": (30, 40),
            "oxygen_range": (4, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 25,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 100
        },
        "diet": ["fish", "squid"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (1000, 2000),
        "maturity_age": 2,
        "breeding_season": "summer",
        "swimming_ability": 0.9
    },
    "salmon": {
        "max_age": 7,
        "max_size": 1.5,
        "max_weight": 30,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 20),
            "salinity_range": (0, 35),
            "oxygen_range": (5, 9),
            "depth_range": (0, 100),
            "preferred_temperature": 12,
            "preferred_salinity": 20,
            "preferred_oxygen": 7,
            "preferred_depth": 50
        },
        "diet": ["plankton", "small_fish"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (2000, 5000),
        "maturity_age": 2,
        "breeding_season": "fall",
        "swimming_ability": 0.8
    },
    "cod": {
        "max_age": 25,
        "max_size": 1.2,
        "max_weight": 40,
        "habitat": {
            "type": "coastal",
            "temperature_range": (0, 15),
            "salinity_range": (30, 35),
            "oxygen_range": (5, 8),
            "depth_range": (0, 600),
            "preferred_temperature": 8,
            "preferred_salinity": 32,
            "preferred_oxygen": 6,
            "preferred_depth": 150
        },
        "diet": ["small_fish", "crustaceans"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (5000, 10000),
        "maturity_age": 3,
        "breeding_season": "winter",
        "swimming_ability": 0.7
    },
    "sardine": {
        "max_age": 5,
        "max_size": 0.3,
        "max_weight": 0.5,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 25),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 100),
            "preferred_temperature": 18,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["plankton", "small_crustaceans"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (10000, 20000),
        "maturity_age": 1,
        "breeding_season": "summer",
        "swimming_ability": 0.8
    },
    "mackerel": {
        "max_age": 20,
        "max_size": 0.8,
        "max_weight": 3.5,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 25),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 18,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 100
        },
        "diet": ["small_fish", "crustaceans"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (2000, 5000),
        "maturity_age": 2,
        "breeding_season": "summer",
        "swimming_ability": 0.9
    },
    "herring": {
        "max_age": 15,
        "max_size": 0.4,
        "max_weight": 1.0,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 20),
            "salinity_range": (30, 35),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 12,
            "preferred_salinity": 32,
            "preferred_oxygen": 6,
            "preferred_depth": 100
        },
        "diet": ["plankton", "small_crustaceans"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (10000, 30000),
        "maturity_age": 2,
        "breeding_season": "spring",
        "swimming_ability": 0.8
    },
    "anchovy": {
        "max_age": 4,
        "max_size": 0.2,
        "max_weight": 0.3,
        "habitat": {
            "type": "coastal",
            "temperature_range": (15, 30),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 100),
            "preferred_temperature": 22,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["plankton", "small_crustaceans"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (20000, 50000),
        "maturity_age": 1,
        "breeding_season": "summer",
        "swimming_ability": 0.7
    },
    "bass": {
        "max_age": 20,
        "max_size": 1.0,
        "max_weight": 10,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 25),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 100),
            "preferred_temperature": 18,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["fish", "crustaceans"],
        "migration": False,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (1000, 2000),
        "maturity_age": 3,
        "breeding_season": "spring",
        "swimming_ability": 0.8
    },
    "trout": {
        "max_age": 7,
        "max_size": 0.8,
        "max_weight": 5,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 20),
            "salinity_range": (0, 35),
            "oxygen_range": (5, 9),
            "depth_range": (0, 50),
            "preferred_temperature": 12,
            "preferred_salinity": 20,
            "preferred_oxygen": 7,
            "preferred_depth": 25
        },
        "diet": ["insects", "small_fish"],
        "migration": True,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (1000, 3000),
        "maturity_age": 2,
        "breeding_season": "fall",
        "swimming_ability": 0.7
    },
    "catfish": {
        "max_age": 15,
        "max_size": 1.5,
        "max_weight": 20,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 30),
            "salinity_range": (0, 35),
            "oxygen_range": (4, 8),
            "depth_range": (0, 50),
            "preferred_temperature": 20,
            "preferred_salinity": 20,
            "preferred_oxygen": 6,
            "preferred_depth": 25
        },
        "diet": ["fish", "crustaceans", "insects"],
        "migration": False,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (2000, 5000),
        "maturity_age": 3,
        "breeding_season": "summer",
        "swimming_ability": 0.6
    },
    "shrimp": {
        "max_age": 2,
        "max_size": 0.1,
        "max_weight": 0.05,
        "habitat": {
            "type": "coastal",
            "temperature_range": (15, 30),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 50),
            "preferred_temperature": 22,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 25
        },
        "diet": ["plankton", "detritus"],
        "migration": False,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (1000, 5000),
        "maturity_age": 0.5,
        "breeding_season": "summer",
        "swimming_ability": 0.5
    },
    "crab": {
        "max_age": 10,
        "max_size": 0.3,
        "max_weight": 2.0,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 30),
            "salinity_range": (20, 38),
            "oxygen_range": (4, 8),
            "depth_range": (0, 100),
            "preferred_temperature": 20,
            "preferred_salinity": 30,
            "preferred_oxygen": 6,
            "preferred_depth": 10
        },
        "diet": ["detritus", "small_fish", "algae"],
        "migration": False,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (1000, 2000),
        "maturity_age": 2,
        "breeding_season": "summer",
        "swimming_ability": 0.4
    },
    "lobster": {
        "max_age": 50,
        "max_size": 0.6,
        "max_weight": 5.0,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 25),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 15,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["fish", "crustaceans", "mollusks"],
        "migration": False,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (5000, 10000),
        "maturity_age": 5,
        "breeding_season": "summer",
        "swimming_ability": 0.6
    },
    "oyster": {
        "max_age": 20,
        "max_size": 0.2,
        "max_weight": 0.5,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 30),
            "salinity_range": (20, 35),
            "oxygen_range": (4, 8),
            "depth_range": (0, 20),
            "preferred_temperature": 20,
            "preferred_salinity": 30,
            "preferred_oxygen": 6,
            "preferred_depth": 5
        },
        "diet": ["plankton", "algae"],
        "migration": False,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (100000, 1000000),
        "maturity_age": 1,
        "breeding_season": "summer",
        "swimming_ability": 0.0
    },
    "mussel": {
        "max_age": 15,
        "max_size": 0.1,
        "max_weight": 0.2,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 25),
            "salinity_range": (20, 35),
            "oxygen_range": (4, 8),
            "depth_range": (0, 20),
            "preferred_temperature": 15,
            "preferred_salinity": 30,
            "preferred_oxygen": 6,
            "preferred_depth": 5
        },
        "diet": ["plankton", "algae"],
        "migration": False,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (10000, 100000),
        "maturity_age": 1,
        "breeding_season": "summer",
        "swimming_ability": 0.0
    },
    "clam": {
        "max_age": 30,
        "max_size": 0.2,
        "max_weight": 0.5,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 25),
            "salinity_range": (20, 35),
            "oxygen_range": (4, 8),
            "depth_range": (0, 20),
            "preferred_temperature": 15,
            "preferred_salinity": 30,
            "preferred_oxygen": 6,
            "preferred_depth": 5
        },
        "diet": ["plankton", "algae"],
        "migration": False,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (10000, 100000),
        "maturity_age": 2,
        "breeding_season": "summer",
        "swimming_ability": 0.0
    },
    "seal": {
        "max_age": 30,
        "max_size": 2.0,
        "max_weight": 150,
        "habitat": {
            "type": "coastal",
            "temperature_range": (-2, 20),
            "salinity_range": (30, 35),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 10,
            "preferred_salinity": 32,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["fish", "squid"],
        "migration": True,
        "social": True,
        "gestation_period": 330,
        "offspring_count": (1, 1),
        "maturity_age": 5,
        "breeding_season": "spring",
        "swimming_ability": 0.9
    },
    "sea_lion": {
        "max_age": 25,
        "max_size": 2.5,
        "max_weight": 300,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 25),
            "salinity_range": (30, 35),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 15,
            "preferred_salinity": 32,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["fish", "squid"],
        "migration": True,
        "social": True,
        "gestation_period": 350,
        "offspring_count": (1, 1),
        "maturity_age": 4,
        "breeding_season": "summer",
        "swimming_ability": 0.9
    },
    "otter": {
        "max_age": 15,
        "max_size": 1.2,
        "max_weight": 30,
        "habitat": {
            "type": "coastal",
            "temperature_range": (5, 20),
            "salinity_range": (20, 35),
            "oxygen_range": (5, 8),
            "depth_range": (0, 50),
            "preferred_temperature": 12,
            "preferred_salinity": 30,
            "preferred_oxygen": 6,
            "preferred_depth": 10
        },
        "diet": ["shellfish", "fish", "crustaceans"],
        "migration": False,
        "social": True,
        "gestation_period": 60,
        "offspring_count": (1, 2),
        "maturity_age": 3,
        "breeding_season": "spring",
        "swimming_ability": 0.8
    },
    "squid": {
        "max_age": 2,
        "max_size": 0.5,
        "max_weight": 2.0,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 25),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 18,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 100
        },
        "diet": ["fish", "crustaceans"],
        "migration": True,
        "social": True,
        "gestation_period": 0,
        "offspring_count": (1000, 2000),
        "maturity_age": 0.5,
        "breeding_season": "summer",
        "swimming_ability": 0.9
    },
    "octopus": {
        "max_age": 3,
        "max_size": 1.0,
        "max_weight": 10,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 25),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 18,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 100
        },
        "diet": ["fish", "crustaceans", "mollusks"],
        "migration": False,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (1000, 2000),
        "maturity_age": 1,
        "breeding_season": "summer",
        "swimming_ability": 0.8
    },
    "jellyfish": {
        "max_age": 1,
        "max_size": 0.3,
        "max_weight": 0.5,
        "habitat": {
            "type": "coastal",
            "temperature_range": (10, 30),
            "salinity_range": (30, 38),
            "oxygen_range": (4, 8),
            "depth_range": (0, 100),
            "preferred_temperature": 20,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["plankton", "small_fish"],
        "migration": True,
        "social": False,
        "gestation_period": 0,
        "offspring_count": (1000, 5000),
        "maturity_age": 0.2,
        "breeding_season": "summer",
        "swimming_ability": 0.3
    },
    "sea_turtle": {
        "max_age": 80,
        "max_size": 1.5,
        "max_weight": 200,
        "habitat": {
            "type": "coastal",
            "temperature_range": (15, 30),
            "salinity_range": (30, 38),
            "oxygen_range": (5, 8),
            "depth_range": (0, 200),
            "preferred_temperature": 25,
            "preferred_salinity": 35,
            "preferred_oxygen": 6,
            "preferred_depth": 50
        },
        "diet": ["jellyfish", "algae", "seagrass"],
        "migration": True,
        "social": False,
        "gestation_period": 60,
        "offspring_count": (50, 200),
        "maturity_age": 20,
        "breeding_season": "summer",
        "swimming_ability": 0.7
    }
}

class MarineSpecies(Enum):
    # Fish
    TUNA = "tuna"
    SALMON = "salmon"
    COD = "cod"
    SARDINE = "sardine"
    MACKEREL = "mackerel"
    HERRING = "herring"
    ANCHOVY = "anchovy"
    BASS = "bass"
    TROUT = "trout"
    CATFISH = "catfish"
    
    # Shellfish
    SHRIMP = "shrimp"
    CRAB = "crab"
    LOBSTER = "lobster"
    OYSTER = "oyster"
    MUSSEL = "mussel"
    CLAM = "clam"
    
    # Marine Mammals
    DOLPHIN = "dolphin"
    WHALE = "whale"
    SEAL = "seal"
    SEA_LION = "sea_lion"
    OTTER = "otter"
    
    # Other Marine Life
    SQUID = "squid"
    OCTOPUS = "octopus"
    JELLYFISH = "jellyfish"
    SEA_TURTLE = "sea_turtle"
    SHARK = "shark"

class MarineHabitat(Enum):
    COASTAL = "coastal"
    REEF = "reef"
    OPEN_OCEAN = "open_ocean"
    DEEP_SEA = "deep_sea"
    ESTUARY = "estuary"
    POLAR = "polar"
    TROPICAL = "tropical"

@dataclass
class MarineCreature:
    """Represents a marine creature in the simulation."""
    
    def __init__(self, id: int, species: str, longitude: float, latitude: float, world_size: int):
        self.id = id
        self.species = species.value if isinstance(species, MarineSpecies) else species
        self.longitude = longitude
        self.latitude = latitude
        self.world_size = world_size
        self.age = 0
        self.health = 100
        self.energy = 100
        self.reproduction_ready = False
        self.mating_cooldown = 0
        self.migration_cooldown = 0
        self.social_group = None
        self.territory = None
        self.last_action = "idle"
        self.last_action_time = time.time()
        
        # Get species info
        self.species_info = MARINE_SPECIES[self.species]
        self.max_age = self.species_info["max_age"]
        self.maturity_age = self.species_info["maturity_age"]
        self.reproduction_rate = 0.1  # Default value
        self.migration_rate = 0.2 if self.species_info["migration"] else 0.0
        self.social_behavior = self.species_info["social"]
        self.territory_size = 1.0  # Default value
        self.swimming_ability = self.species_info["swimming_ability"]
        self.habitat = self.species_info["habitat"]
        self.size = 0.1  # Start small
        self.weight = 0.1  # Start light
        self.is_dead = False
        self.is_migrating = False
        self.is_mating = False
        self.gestation_period = None
        self.migration_target = None
        self.diet = self.species_info["diet"]
        self.reproduction_status = "immature"
        self.last_updated = datetime.now()
        
    def update(self, time_delta: float, conditions: Dict):
        """Update creature state based on environmental conditions."""
        # Update age
        self.age += time_delta
        
        # Update energy based on conditions
        self._update_energy(conditions)
        
        # Update health based on conditions
        self._update_health(conditions)
        
        # Update reproduction state
        self._update_reproduction()
        
        # Update cooldowns
        if self.mating_cooldown > 0:
            self.mating_cooldown -= time_delta
        if self.migration_cooldown > 0:
            self.migration_cooldown -= time_delta
            
    def _update_energy(self, conditions: Dict):
        """Update energy based on environmental conditions."""
        # Base energy consumption
        energy_consumption = 0.1
        
        # Adjust for temperature
        temp = conditions["temperature"]
        if temp < self.habitat["temperature_range"][0] or temp > self.habitat["temperature_range"][1]:
            energy_consumption *= 1.5
            
        # Adjust for salinity
        salinity = conditions["salinity"]
        if salinity < self.habitat["salinity_range"][0] or salinity > self.habitat["salinity_range"][1]:
            energy_consumption *= 1.3
            
        # Adjust for oxygen
        oxygen = conditions["oxygen"]
        if oxygen < self.habitat["oxygen_range"][0]:
            energy_consumption *= 2.0
            
        # Adjust for depth
        depth = conditions["depth"]
        if depth < self.habitat["depth_range"][0] or depth > self.habitat["depth_range"][1]:
            energy_consumption *= 1.2
            
        # Update energy
        self.energy = max(0, self.energy - energy_consumption)
        
    def _update_health(self, conditions: Dict):
        """Update health based on environmental conditions."""
        # Base health change
        health_change = 0.1
        
        # Adjust for temperature
        temp = conditions["temperature"]
        if temp < self.habitat["temperature_range"][0] or temp > self.habitat["temperature_range"][1]:
            health_change -= 0.2
            
        # Adjust for salinity
        salinity = conditions["salinity"]
        if salinity < self.habitat["salinity_range"][0] or salinity > self.habitat["salinity_range"][1]:
            health_change -= 0.15
            
        # Adjust for oxygen
        oxygen = conditions["oxygen"]
        if oxygen < self.habitat["oxygen_range"][0]:
            health_change -= 0.3
            
        # Adjust for depth
        depth = conditions["depth"]
        if depth < self.habitat["depth_range"][0] or depth > self.habitat["depth_range"][1]:
            health_change -= 0.1
            
        # Update health
        self.health = max(0, min(100, self.health + health_change))
        
    def _update_reproduction(self):
        """Update reproduction state."""
        if self.age >= self.maturity_age and not self.reproduction_ready:
            self.reproduction_ready = True
            
    def should_die(self, conditions: Dict) -> bool:
        """Check if creature should die based on conditions."""
        # Die if health or energy is too low
        if self.health <= 0 or self.energy <= 0:
            return True
            
        # Die if too old
        if self.age >= self.max_age:
            return True
            
        # Die if conditions are too extreme
        temp = conditions["temperature"]
        salinity = conditions["salinity"]
        oxygen = conditions["oxygen"]
        depth = conditions["depth"]
        
        if (temp < self.habitat["temperature_range"][0] * 0.8 or 
            temp > self.habitat["temperature_range"][1] * 1.2 or
            salinity < self.habitat["salinity_range"][0] * 0.8 or
            salinity > self.habitat["salinity_range"][1] * 1.2 or
            oxygen < self.habitat["oxygen_range"][0] * 0.5 or
            depth < self.habitat["depth_range"][0] * 0.8 or
            depth > self.habitat["depth_range"][1] * 1.2):
            return True
            
        return False
        
    def should_mate(self, conditions: Dict) -> bool:
        """Check if creature should mate based on conditions."""
        if not self.reproduction_ready or self.mating_cooldown > 0:
            return False
            
        # Check if conditions are suitable for mating
        temp = conditions["temperature"]
        salinity = conditions["salinity"]
        oxygen = conditions["oxygen"]
        depth = conditions["depth"]
        
        if (temp < self.habitat["temperature_range"][0] or 
            temp > self.habitat["temperature_range"][1] or
            salinity < self.habitat["salinity_range"][0] or
            salinity > self.habitat["salinity_range"][1] or
            oxygen < self.habitat["oxygen_range"][0] or
            depth < self.habitat["depth_range"][0] or
            depth > self.habitat["depth_range"][1]):
            return False
            
        # Random chance based on reproduction rate
        return np.random.random() < self.reproduction_rate
        
    def should_migrate(self, conditions: Dict) -> bool:
        """Check if creature should migrate based on conditions."""
        if self.migration_cooldown > 0:
            return False
            
        # Check if conditions are unsuitable
        temp = conditions["temperature"]
        salinity = conditions["salinity"]
        oxygen = conditions["oxygen"]
        depth = conditions["depth"]
        
        if (temp < self.habitat["temperature_range"][0] * 0.9 or 
            temp > self.habitat["temperature_range"][1] * 1.1 or
            salinity < self.habitat["salinity_range"][0] * 0.9 or
            salinity > self.habitat["salinity_range"][1] * 1.1 or
            oxygen < self.habitat["oxygen_range"][0] * 0.9 or
            depth < self.habitat["depth_range"][0] * 0.9 or
            depth > self.habitat["depth_range"][1] * 1.1):
            return True
            
        # Random chance based on migration rate
        return np.random.random() < self.migration_rate

class MarineSystem:
    def __init__(self, world):
        """Initialize the marine system."""
        logger.info("Initializing marine system...")
        self.world = world
        self.creatures: Dict[int, MarineCreature] = {}
        self.habitats: Dict[str, Dict] = {}
        self.food_webs: Dict[str, Dict] = {}
        self.migration_patterns: Dict[str, List[Tuple[float, float]]] = {}
        self.reproduction_cycles: Dict[str, Dict] = {}
        self.predation_relationships: Dict[str, List[str]] = {}
        self.symbiotic_relationships: Dict[str, List[str]] = {}
        self.competition_relationships: Dict[str, List[str]] = {}
        self.fishing_zones: Dict[str, Dict] = {}
        
        # Initialize marine system
        logger.info("Initializing marine distribution...")
        self.initialize_marine()
        logger.info("Marine distribution initialized")
        
        logger.info("Marine system initialization complete")
        
    def initialize_marine(self):
        """Initialize the marine system."""
        logger.info("Initializing marine system...")
        
        # Initialize marine species
        logger.info("Setting up marine species...")
        self._initialize_marine_species()
        
        # Initialize marine populations
        logger.info("Setting up marine populations...")
        self._initialize_marine_populations()
        
        # Initialize social groups
        logger.info("Setting up social groups...")
        self._initialize_social_groups()
        
        # Initialize territories
        logger.info("Setting up territories...")
        self._initialize_territories()
        
        # Verify initialization
        if not self.verify_initialization():
            logger.error("Marine system initialization verification failed")
            raise RuntimeError("Marine system initialization verification failed")
            
        logger.info("Marine system initialization complete")

    def verify_initialization(self) -> bool:
        """Verify that the marine system is properly initialized."""
        logger.info("Verifying marine system initialization...")
        
        # Check creatures dictionary
        if not hasattr(self, 'creatures') or not self.creatures:
            logger.error("Marine creatures not initialized")
            return False
            
        # Check social groups
        if not hasattr(self, 'social_groups') or not self.social_groups:
            logger.error("Marine social groups not initialized")
            return False
            
        # Check territories
        if not hasattr(self, 'territories') or not self.territories:
            logger.error("Marine territories not initialized")
            return False
            
        # Check spatial grid
        if not hasattr(self, 'spatial_grid') or not self.spatial_grid:
            logger.error("Marine spatial grid not initialized")
            return False
            
        # Check required marine types
        required_types = {'fish', 'mammal', 'invertebrate', 'reptile'}
        if not all(any(creature.type == marine_type for creature in self.creatures.values()) 
                  for marine_type in required_types):
            logger.error("Not all required marine types initialized")
            return False
            
        logger.info("Marine system initialization verified successfully")
        return True
        
    def _initialize_marine_species(self):
        """Initialize marine species."""
        logger.info("Initializing marine species...")
        
        # Initialize habitats
        logger.info("Setting up marine habitats...")
        self._initialize_habitats()
        logger.info("Marine habitats initialized")
        
        # Initialize food webs
        logger.info("Setting up food webs...")
        self._initialize_food_webs()
        logger.info("Food webs initialized")
        
        # Initialize migration patterns
        logger.info("Setting up migration patterns...")
        self._initialize_migration_patterns()
        logger.info("Migration patterns initialized")
        
        # Initialize reproduction cycles
        logger.info("Setting up reproduction cycles...")
        self._initialize_reproduction_cycles()
        logger.info("Reproduction cycles initialized")
        
        # Initialize predation relationships
        logger.info("Setting up predation relationships...")
        self._initialize_predation_relationships()
        logger.info("Predation relationships initialized")
        
        # Initialize symbiotic relationships
        logger.info("Setting up symbiotic relationships...")
        self._initialize_symbiotic_relationships()
        logger.info("Symbiotic relationships initialized")
        
        # Initialize competition relationships
        logger.info("Setting up competition relationships...")
        self._initialize_competition_relationships()
        logger.info("Competition relationships initialized")
        
        # Initialize fishing zones
        logger.info("Setting up fishing zones...")
        self._initialize_fishing_zones()
        logger.info("Fishing zones initialized")
        
        # Initialize species data
        logger.info("Setting up species data...")
        self._initialize_species_data()
        logger.info("Species data initialized")
        
        # Calculate total points for progress tracking
        total_points = len(np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution)) * \
                      len(np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution))
        points_processed = 0
        last_progress = 0
        
        # Process in chunks to show progress
        chunk_size = 1000  # Process 1000 points at a time
        
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                # Get terrain type at location
                terrain_type = self.world.terrain.get_terrain_at(lon, lat)
                
                # Generate marine life based on terrain
                logger.info(f"Generating marine life for terrain type: {terrain_type}")
                self._generate_marine_life_for_terrain(lon, lat, terrain_type)
                
                points_processed += 1
                
                # Log progress every 10%
                progress = (points_processed / total_points) * 100
                if progress - last_progress >= 10:
                    logger.info(f"Marine distribution progress: {progress:.1f}%")
                    last_progress = progress
        
        logger.info("Marine distribution initialization complete")
        
    def _initialize_habitats(self):
        """Initialize marine habitats."""
        logger.info("Initializing marine habitats...")
        
        # Initialize coastal habitats
        logger.info("Setting up coastal habitats...")
        self._initialize_coastal_habitats()
        logger.info("Coastal habitats initialized")
        
        # Initialize reef habitats
        logger.info("Setting up reef habitats...")
        self._initialize_reef_habitats()
        logger.info("Reef habitats initialized")
        
        # Initialize open ocean habitats
        logger.info("Setting up open ocean habitats...")
        self._initialize_open_ocean_habitats()
        logger.info("Open ocean habitats initialized")
        
        # Initialize deep sea habitats
        logger.info("Setting up deep sea habitats...")
        self._initialize_deep_sea_habitats()
        logger.info("Deep sea habitats initialized")
        
        # Initialize estuary habitats
        logger.info("Setting up estuary habitats...")
        self._initialize_estuary_habitats()
        logger.info("Estuary habitats initialized")
        
        # Initialize polar habitats
        logger.info("Setting up polar habitats...")
        self._initialize_polar_habitats()
        logger.info("Polar habitats initialized")
        
        # Initialize tropical habitats
        logger.info("Setting up tropical habitats...")
        self._initialize_tropical_habitats()
        logger.info("Tropical habitats initialized")
        
        logger.info("Marine habitats initialization complete")
        
    def _initialize_food_webs(self):
        """Initialize marine food webs."""
        logger.info("Initializing marine food webs...")
        
        # Initialize plankton food web
        logger.info("Setting up plankton food web...")
        self._initialize_plankton_food_web()
        logger.info("Plankton food web initialized")
        
        # Initialize fish food web
        logger.info("Setting up fish food web...")
        self._initialize_fish_food_web()
        logger.info("Fish food web initialized")
        
        # Initialize mammal food web
        logger.info("Setting up mammal food web...")
        self._initialize_mammal_food_web()
        logger.info("Mammal food web initialized")
        
        # Initialize predator food web
        logger.info("Setting up predator food web...")
        self._initialize_predator_food_web()
        logger.info("Predator food web initialized")
        
        logger.info("Marine food webs initialization complete")
        
    def _initialize_migration_patterns(self):
        """Initialize migration patterns."""
        logger.info("Setting up migration patterns...")
        
        # Initialize migration patterns for each species
        total_species = len(MarineSpecies)
        for i, species in enumerate(MarineSpecies):
            self.migration_patterns[species.value] = self._determine_migration_pattern(species)
            progress = ((i + 1) / total_species) * 100
            logger.info(f"Migration pattern initialization progress: {progress:.1f}%")
        
        logger.info("Migration patterns initialized")
        
    def _initialize_reproduction_cycles(self):
        """Initialize reproduction cycles."""
        logger.info("Setting up reproduction cycles...")
        
        # Initialize reproduction cycles for each species
        total_species = len(MarineSpecies)
        for i, species in enumerate(MarineSpecies):
            self.reproduction_cycles[species.value] = self._determine_reproduction_cycle(species)
            progress = ((i + 1) / total_species) * 100
            logger.info(f"Reproduction cycle initialization progress: {progress:.1f}%")
        
        logger.info("Reproduction cycles initialized")
        
    def _initialize_predation_relationships(self):
        """Initialize predation relationships."""
        logger.info("Setting up predation relationships...")
        
        # Initialize predation relationships for each species
        total_species = len(MarineSpecies)
        for i, species in enumerate(MarineSpecies):
            self.predation_relationships[species.value] = self._determine_predation_relationships(species)
            progress = ((i + 1) / total_species) * 100
            logger.info(f"Predation relationship initialization progress: {progress:.1f}%")
        
        logger.info("Predation relationships initialized")
        
    def _initialize_symbiotic_relationships(self):
        """Initialize symbiotic relationships."""
        logger.info("Setting up symbiotic relationships...")
        
        # Initialize symbiotic relationships for each species
        total_species = len(MarineSpecies)
        for i, species in enumerate(MarineSpecies):
            self.symbiotic_relationships[species.value] = self._determine_symbiotic_relationships(species)
            progress = ((i + 1) / total_species) * 100
            logger.info(f"Symbiotic relationship initialization progress: {progress:.1f}%")
        
        logger.info("Symbiotic relationships initialized")
        
    def _initialize_competition_relationships(self):
        """Initialize competition relationships."""
        logger.info("Setting up competition relationships...")
        
        # Initialize competition relationships for each species
        total_species = len(MarineSpecies)
        for i, species in enumerate(MarineSpecies):
            self.competition_relationships[species.value] = self._determine_competition_relationships(species)
            progress = ((i + 1) / total_species) * 100
            logger.info(f"Competition relationship initialization progress: {progress:.1f}%")
        
        logger.info("Competition relationships initialized")
        
    def _initialize_fishing_zones(self):
        """Initialize fishing zones."""
        logger.info("Setting up fishing zones...")
        
        # Calculate total points for progress tracking
        total_points = len(np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution)) * \
                      len(np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution))
        points_processed = 0
        last_progress = 0
        
        # Process in chunks to show progress
        chunk_size = 1000  # Process 1000 points at a time
        
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                # Initialize fishing zone data
                self.fishing_zones[(lon, lat)] = self._determine_fishing_zone(lon, lat)
                points_processed += 1
                
                # Log progress every 10%
                progress = (points_processed / total_points) * 100
                if progress - last_progress >= 10:
                    logger.info(f"Fishing zone initialization progress: {progress:.1f}%")
                    last_progress = progress
        
        logger.info("Fishing zones initialized")
        
    def _initialize_species_data(self) -> Dict[MarineSpecies, Dict]:
        """Initialize data for each marine species."""
        return {
            MarineSpecies.TUNA: {
                "max_age": 15,
                "max_size": 2.5,
                "max_weight": 250,
                "habitat": MarineHabitat.OPEN_OCEAN,
                "diet": ["fish", "squid"],
                "migration": True,
                "social": True,
                "gestation_period": 0,  # lays eggs
                "offspring_count": (1000, 2000),
                "maturity_age": 2,
                "breeding_season": "summer",
                "depth_range": (0, 200),
                "temperature_range": (15, 30),
                "salinity_range": (30, 40),
                "oxygen_range": (4, 8)
            },
            MarineSpecies.SALMON: {
                "max_age": 7,
                "max_size": 1.5,
                "max_weight": 30,
                "habitat": MarineHabitat.COASTAL,
                "diet": ["plankton", "small_fish"],
                "migration": True,
                "social": True,
                "gestation_period": 0,  # lays eggs
                "offspring_count": (2000, 5000),
                "maturity_age": 2,
                "breeding_season": "fall",
                "depth_range": (0, 100),
                "temperature_range": (5, 20),
                "salinity_range": (0, 35),
                "oxygen_range": (5, 9)
            },
            # Add more species data...
        }
        
    def spawn_creature(self, species: str, longitude: Optional[float] = None, latitude: Optional[float] = None) -> MarineCreature:
        """Spawn a new marine creature"""
        if species not in MARINE_SPECIES:
            raise ValueError(f"Unknown marine species: {species}")
        
        # Generate random position if none provided
        if longitude is None or latitude is None:
            longitude = random.uniform(-180, 180)
            latitude = random.uniform(-90, 90)
        
        creature = MarineCreature(
            id=len(self.creatures),
            species=species,
            longitude=longitude,
            latitude=latitude,
            world_size=self.world_size
        )
        
        self.creatures[creature.id] = creature
        return creature
        
    def _update_position(self, creature: MarineCreature, conditions: Dict):
        """Update creature's position based on currents and behavior."""
        # Get current at position
        current = conditions["current"]
        
        # Calculate movement based on current and creature's swimming ability
        movement = np.array([
            current[0] * creature.swimming_ability,
            current[1] * creature.swimming_ability
        ])
        
        # Add some random movement
        movement += np.random.normal(0, 0.1, 2)
        
        # Update position
        creature.longitude += movement[0]
        creature.latitude += movement[1]
        
        # Keep within bounds
        creature.longitude = (creature.longitude + 180) % 360 - 180
        creature.latitude = max(-90, min(90, creature.latitude))
        
    def _handle_migration(self, creature: MarineCreature, conditions: Dict):
        """Handle creature migration to find better conditions."""
        # Find suitable habitat
        target = self._find_suitable_habitat(creature, conditions)
        if target is not None:
            # Move towards target
            direction = target - np.array([creature.longitude, creature.latitude])
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                creature.longitude += direction[0]
                creature.latitude += direction[1]
                
    def _find_suitable_habitat(self, creature: MarineCreature, current_conditions: Dict) -> Optional[np.ndarray]:
        """Find suitable habitat for creature based on environmental conditions."""
        # Search in a radius around current position
        search_radius = 50
        best_position = None
        best_score = float('-inf')
        
        for _ in range(10):  # Try 10 random positions
            # Generate random position within search radius
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(0, search_radius)
            offset = np.array([
                distance * np.cos(angle),
                distance * np.sin(angle)
            ])
            position = np.array([creature.longitude, creature.latitude]) + offset
            
            # Keep within bounds
            position[0] = (position[0] + 180) % 360 - 180
            position[1] = max(-90, min(90, position[1]))
            
            # Get conditions at position
            conditions = {
                "temperature": self.world.climate.get_temperature_at(position),
                "salinity": self.world.terrain.get_salinity_at(position),
                "oxygen": self.world.terrain.get_oxygen_at(position),
                "current": self.world.terrain.get_current_at(position),
                "depth": self.world.terrain.get_depth_at(position),
                "tidal_range": self.world.terrain.get_tidal_range_at(position)
            }
            
            # Calculate suitability score
            score = self._calculate_habitat_suitability(creature, conditions)
            
            if score > best_score:
                best_score = score
                best_position = position
                
        return best_position if best_score > 0 else None
        
    def _calculate_habitat_suitability(self, creature: MarineCreature, conditions: Dict) -> float:
        """Calculate habitat suitability for a creature based on environmental conditions."""
        # Get ideal conditions
        ideal_temp = creature.habitat["preferred_temperature"]
        ideal_salinity = creature.habitat["preferred_salinity"]
        ideal_oxygen = creature.habitat["preferred_oxygen"]
        ideal_depth = creature.habitat["preferred_depth"]
        
        # Calculate differences from ideal conditions
        temp_diff = abs(conditions["temperature"] - ideal_temp)
        salinity_diff = abs(conditions["salinity"] - ideal_salinity)
        oxygen_diff = abs(conditions["oxygen"] - ideal_oxygen)
        depth_diff = abs(conditions["depth"] - ideal_depth)
        
        # Calculate score (higher is better)
        score = 1.0
        score -= temp_diff / 10  # Temperature difference penalty
        score -= salinity_diff / 5  # Salinity difference penalty
        score -= oxygen_diff / 2  # Oxygen difference penalty
        score -= depth_diff / 100  # Depth difference penalty
        
        return max(0, score)  # Ensure non-negative score
        
    def _update_creature(self, creature: MarineCreature, time_delta: float):
        """Update a single creature's state."""
        species_info = self.species_data[creature.species]
        
        # Update age
        creature.age += time_delta / 365  # Convert to years
        
        # Check for death
        if creature.age >= species_info["max_age"]:
            creature.is_dead = True
            return
            
        # Update energy based on activity and environment
        energy_loss = self._calculate_energy_loss(creature, time_delta)
        creature.energy = max(0, creature.energy - energy_loss)
        
        # Update health based on energy and environment
        health_change = self._calculate_health_change(creature, time_delta)
        creature.health = max(0, min(1, creature.health + health_change))
        
        # Check for death from low energy or health
        if creature.energy <= 0 or creature.health <= 0:
            creature.is_dead = True
            return
            
        # Update size and weight
        if creature.age < species_info["maturity_age"]:
            growth_rate = self._calculate_growth_rate(creature)
            creature.size = min(species_info["max_size"], 
                              creature.size + growth_rate * time_delta)
            creature.weight = min(species_info["max_weight"],
                                creature.weight + growth_rate * 10 * time_delta)
                                
    def _calculate_energy_loss(self, creature: MarineCreature, time_delta: float) -> float:
        """Calculate energy loss based on activity and environment."""
        base_loss = 0.1 * time_delta
        
        # Activity modifiers
        if creature.is_migrating:
            base_loss *= 2.0
        if creature.is_mating:
            base_loss *= 1.5
            
        # Environmental modifiers
        temperature = self.world.climate.get_temperature_at(creature.longitude, creature.latitude)
        species_info = self.species_data[creature.species]
        
        if temperature < species_info["temperature_range"][0]:
            base_loss *= 1.5
        elif temperature > species_info["temperature_range"][1]:
            base_loss *= 1.5
            
        return base_loss
        
    def _calculate_health_change(self, creature: MarineCreature, time_delta: float) -> float:
        """Calculate health change based on energy and environment."""
        # Base health change from energy
        health_change = (creature.energy - 0.5) * 0.1 * time_delta
        
        # Environmental factors
        temperature = self.world.climate.get_temperature_at(creature.longitude, creature.latitude)
        salinity = self.world.terrain.get_salinity_at(creature.longitude, creature.latitude)
        oxygen = self.world.terrain.get_oxygen_at(creature.longitude, creature.latitude)
        
        species_info = self.species_data[creature.species]
        
        # Temperature effects
        if temperature < species_info["temperature_range"][0]:
            health_change -= 0.1 * time_delta
        elif temperature > species_info["temperature_range"][1]:
            health_change -= 0.1 * time_delta
            
        # Salinity effects
        if salinity < species_info["salinity_range"][0]:
            health_change -= 0.1 * time_delta
        elif salinity > species_info["salinity_range"][1]:
            health_change -= 0.1 * time_delta
            
        # Oxygen effects
        if oxygen < species_info["oxygen_range"][0]:
            health_change -= 0.2 * time_delta
            
        return health_change
        
    def _calculate_growth_rate(self, creature: MarineCreature) -> float:
        """Calculate growth rate based on conditions."""
        species_info = self.species_data[creature.species]
        max_size = species_info["max_size"]
        maturity_age = species_info["maturity_age"]
        
        # Base growth rate
        growth_rate = max_size / maturity_age
        
        # Modify based on conditions
        if creature.energy < 0.5:
            growth_rate *= 0.5
        if creature.health < 0.5:
            growth_rate *= 0.5
            
        return growth_rate
        
    def _update_migration(self, creature: MarineCreature, time_delta: float):
        """Update creature's migration."""
        if not creature.migration_target:
            # Find new migration target
            creature.migration_target = self._find_migration_target(creature)
            if not creature.migration_target:
                creature.is_migrating = False
                return
                
        # Move towards target
        current_lon, current_lat = creature.longitude, creature.latitude
        target_lon, target_lat = creature.migration_target
        
        # Calculate movement
        distance = self.world.get_distance((current_lon, current_lat), (target_lon, target_lat))
        speed = self._calculate_migration_speed(creature)
        movement = speed * time_delta
        
        if movement >= distance:
            # Reached target
            creature.longitude, creature.latitude = target_lon, target_lat
            creature.migration_target = None
            creature.is_migrating = False
        else:
            # Move towards target
            ratio = movement / distance
            new_lon = current_lon + (target_lon - current_lon) * ratio
            new_lat = current_lat + (target_lat - current_lat) * ratio
            creature.longitude, creature.latitude = new_lon, new_lat
            
    def _find_migration_target(self, creature: MarineCreature) -> Optional[Tuple[float, float]]:
        """Find a suitable migration target for a creature."""
        species_info = self.species_data[creature.species]
        
        # Get migration route if available
        if creature.species in self.migration_routes:
            route = self.migration_routes[creature.species]
            current_pos = (creature.longitude, creature.latitude)
            
            # Find next point in route
            for i, point in enumerate(route):
                if self.world.get_distance(current_pos, point) < 0.1:
                    if i + 1 < len(route):
                        return route[i + 1]
                    else:
                        return route[0]  # Start over
                        
        # If no route, find suitable habitat
        return self._find_suitable_habitat(creature.habitat)
        
    def _calculate_migration_speed(self, creature: MarineCreature) -> float:
        """Calculate migration speed based on species and conditions."""
        species_info = self.species_data[creature.species]
        base_speed = 50  # km/day
        
        # Modify based on size and energy
        size_factor = creature.size / species_info["max_size"]
        energy_factor = creature.energy
        
        return base_speed * size_factor * energy_factor
        
    def _update_mating(self, creature: MarineCreature, time_delta: float):
        """Update creature's mating state."""
        species_info = self.species_data[creature.species]
        
        if creature.gestation_period is not None:
            # Update gestation
            creature.gestation_period -= time_delta
            if creature.gestation_period <= 0:
                # Give birth
                self._give_birth(creature)
                creature.gestation_period = None
                creature.is_mating = False
        else:
            # Check if it's breeding season
            current_season = self.world.weather.get_season()
            if current_season == species_info["breeding_season"]:
                # Look for mate
                mate = self._find_mate(creature)
                if mate:
                    self._initiate_mating(creature, mate)
                    
    def _find_mate(self, creature: MarineCreature) -> Optional[MarineCreature]:
        """Find a suitable mate for a creature."""
        species_info = self.species_data[creature.species]
        
        # Check if creature is mature enough
        if creature.age < species_info["maturity_age"]:
            return None
            
        # Look for nearby potential mates
        for other in self.creatures.values():
            if (other.species == creature.species and
                other.age >= species_info["maturity_age"] and
                not other.is_mating and
                not other.is_dead):
                
                distance = self.world.get_distance((creature.longitude, creature.latitude), (other.longitude, other.latitude))
                if distance < 1.0:  # Within 1 degree
                    return other
                    
        return None
        
    def _initiate_mating(self, creature: MarineCreature, mate: MarineCreature):
        """Initiate mating between two creatures."""
        species_info = self.species_data[creature.species]
        
        # Set mating state
        creature.is_mating = True
        mate.is_mating = True
        
        # Set gestation period if applicable
        if species_info["gestation_period"] > 0:
            creature.gestation_period = species_info["gestation_period"]
            mate.gestation_period = species_info["gestation_period"]
            
    def _give_birth(self, creature: MarineCreature):
        """Handle birth of offspring."""
        species_info = self.species_data[creature.species]
        
        # Determine number of offspring
        min_offspring, max_offspring = species_info["offspring_count"]
        offspring_count = random.randint(min_offspring, max_offspring)
        
        # Create offspring
        for _ in range(offspring_count):
            offspring_id = f"marine_{len(self.creatures)}"
            offspring = MarineCreature(
                id=offspring_id,
                species=creature.species,
                longitude=creature.longitude,
                latitude=creature.latitude,
                world_size=self.world_size
            )
            
            self.creatures[offspring_id] = offspring
            
            # Add to social group if parent is in one
            if creature.social_group:
                self._add_to_social_group(offspring, creature.social_group)
                
    def _update_social_behavior(self, creature: MarineCreature, time_delta: float):
        """Update creature's social behavior."""
        if not creature.social_group:
            return
            
        # Get other creatures in social group
        group_members = self.social_groups[creature.social_group]
        
        # Update social bonds
        for member_id in group_members:
            if member_id != creature.id:
                member = self.creatures[member_id]
                if not member.is_dead:
                    # Strengthen social bond
                    self._update_social_bond(creature, member, time_delta)
                    
    def _update_social_bond(self, creature1: MarineCreature, creature2: MarineCreature, time_delta: float):
        """Update social bond between two creatures."""
        # Calculate distance
        distance = self.world.get_distance((creature1.longitude, creature1.latitude), (creature2.longitude, creature2.latitude))
        
        # Update social behavior based on distance
        if distance < 0.1:  # Very close
            # Cooperative behavior
            self._cooperate(creature1, creature2)
        elif distance < 0.5:  # Nearby
            # Social interaction
            self._interact(creature1, creature2)
            
    def _cooperate(self, creature1: MarineCreature, creature2: MarineCreature):
        """Handle cooperative behavior between creatures."""
        # Share food
        if creature1.energy > 0.8 and creature2.energy < 0.3:
            transfer = (creature1.energy - 0.8) * 0.5
            creature1.energy -= transfer
            creature2.energy += transfer
        elif creature2.energy > 0.8 and creature1.energy < 0.3:
            transfer = (creature2.energy - 0.8) * 0.5
            creature2.energy -= transfer
            creature1.energy += transfer
            
    def _interact(self, creature1: MarineCreature, creature2: MarineCreature):
        """Handle social interaction between creatures."""
        # Increase energy slightly from social interaction
        creature1.energy = min(1.0, creature1.energy + 0.01)
        creature2.energy = min(1.0, creature2.energy + 0.01)
        
    def _update_territory(self, creature: MarineCreature, time_delta: float):
        """Update creature's territory."""
        if not creature.territory:
            return
            
        center, radius = creature.territory
        
        # Check for intruders
        for other in self.creatures.values():
            if other.id != creature.id and not other.is_dead:
                distance = self.world.get_distance((creature.longitude, creature.latitude), (other.longitude, other.latitude))
                if distance < radius:
                    # Handle territorial behavior
                    self._handle_territorial_conflict(creature, other)
                    
    def _handle_territorial_conflict(self, creature: MarineCreature, intruder: MarineCreature):
        """Handle territorial conflict between creatures."""
        # Calculate strength based on size and energy
        creature_strength = creature.size * creature.energy
        intruder_strength = intruder.size * intruder.energy
        
        if creature_strength > intruder_strength:
            # Drive away intruder
            self._drive_away(creature, intruder)
        else:
            # Lose territory
            creature.territory = None
            
    def _drive_away(self, creature: MarineCreature, intruder: MarineCreature):
        """Drive away an intruder from territory."""
        # Calculate direction away from territory center
        center_lon, center_lat = creature.territory
        current_lon, current_lat = intruder.longitude, intruder.latitude
        center_lon, center_lat = center_lon, center_lat
        
        # Move intruder away
        angle = math.atan2(current_lat - center_lat, current_lon - center_lon)
        distance = 0.1  # Move 0.1 degrees away
        new_lon = current_lon + distance * math.cos(angle)
        new_lat = current_lat + distance * math.sin(angle)
        
        intruder.longitude, intruder.latitude = new_lon, new_lat
        
    def _update_fishing(self, creature: MarineCreature, time_delta: float):
        """Update fishing activities affecting the creature."""
        # Check if creature is in a fishing zone
        fishing_zone = self.fishing_zones.get((creature.longitude, creature.latitude))
        if not fishing_zone:
            return
            
        # Calculate catch probability
        catch_prob = self._calculate_catch_probability(creature, fishing_zone)
        
        # Check if caught
        if random.random() < catch_prob * time_delta:
            creature.is_dead = True
            self._handle_catch(creature, fishing_zone)
            
    def _calculate_catch_probability(self, creature: MarineCreature, fishing_zone: Dict) -> float:
        """Calculate probability of creature being caught."""
        base_prob = 0.1
        
        # Modify based on creature size
        size_factor = creature.size / self.species_data[creature.species]["max_size"]
        
        # Modify based on fishing intensity
        intensity_factor = fishing_zone.get("intensity", 1.0)
        
        # Modify based on fishing method
        method_factor = fishing_zone.get("method_efficiency", 1.0)
        
        return base_prob * size_factor * intensity_factor * method_factor
        
    def _handle_catch(self, creature: MarineCreature, fishing_zone: Dict):
        """Handle a creature being caught."""
        # Update fishing zone statistics
        fishing_zone["catches"] = fishing_zone.get("catches", 0) + 1
        fishing_zone["total_weight"] = fishing_zone.get("total_weight", 0) + creature.weight
        
        # Log catch
        logger.info(f"Caught {creature.species.value} (ID: {creature.id}) "
                   f"at {creature.longitude}, {creature.latitude}, weight: {creature.weight:.1f}kg")
                   
    def get_state(self) -> Dict:
        """Get current marine system state."""
        return {
            "creatures": {
                creature_id: {
                    "species": creature.species.value,
                    "age": creature.age,
                    "size": creature.size,
                    "weight": creature.weight,
                    "health": creature.health,
                    "energy": creature.energy,
                    "position": (creature.longitude, creature.latitude),
                    "depth": creature.depth,
                    "habitat": creature.habitat.value,
                    "is_migrating": creature.is_migrating,
                    "is_mating": creature.is_mating,
                    "is_dead": creature.is_dead
                }
                for creature_id, creature in self.creatures.items()
            },
            "fishing_zones": self.fishing_zones,
            "social_groups": {
                group_id: list(members)
                for group_id, members in self.social_groups.items()
            }
        } 