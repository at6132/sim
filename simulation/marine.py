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
        self.species = species
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
        self.species_info = MARINE_SPECIES[species]
        self.max_age = self.species_info["max_age"]
        self.maturity_age = self.species_info["maturity_age"]
        self.reproduction_rate = self.species_info["reproduction_rate"]
        self.migration_rate = self.species_info["migration_rate"]
        self.social_behavior = self.species_info["social_behavior"]
        self.territory_size = self.species_info["territory_size"]
        self.swimming_ability = self.species_info["swimming_ability"]
        self.habitat = self.species_info["habitat"]
        
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
        self.world = world
        self.creatures: Dict[str, MarineCreature] = {}
        self.species_data = self._initialize_species_data()
        self.fishing_zones: Dict[Tuple[float, float], Dict] = {}  # position -> fishing data
        self.migration_routes: Dict[str, List[Tuple[float, float]]] = {}
        self.social_groups: Dict[str, Set[str]] = {}  # group_id -> set of creature IDs
        self.territories: Dict[str, Tuple[float, float, float]] = {}  # creature_id -> (center, radius)
        self.initialize_marine()
        
    def initialize_marine(self):
        """Initialize the marine system."""
        logger.info("Initializing marine system...")
        
        # Initialize marine life distribution
        for lon in range(-180, 181, 5):  # Every 5 degrees
            for lat in range(-90, 91, 5):
                terrain = self.world.terrain.get_terrain_at(lon, lat)
                if terrain['type'] in ['water', 'deep_water']:
                    self._spawn_marine_life(lon, lat)
                    
        # Initialize migration routes
        self._initialize_migration_routes()
        
        # Initialize social groups
        self._initialize_social_groups()
        
        # Initialize territories
        self._initialize_territories()
        
        logger.info("Marine system initialization complete")
        
    def _spawn_marine_life(self, lon: float, lat: float):
        """Spawn marine creatures at a location."""
        # Determine depth and water conditions
        depth = self.world.terrain.get_depth_at(lon, lat)
        temperature = self.world.climate.get_temperature_at(lon, lat)
        salinity = self.world.terrain.get_salinity_at(lon, lat)
        oxygen = self.world.terrain.get_oxygen_at(lon, lat)
        
        # Spawn appropriate species based on conditions
        for species, data in self.species_data.items():
            if (data['depth_range'][0] <= depth <= data['depth_range'][1] and
                data['temperature_range'][0] <= temperature <= data['temperature_range'][1] and
                data['salinity_range'][0] <= salinity <= data['salinity_range'][1] and
                data['oxygen_range'][0] <= oxygen <= data['oxygen_range'][1]):
                
                # Spawn a group of this species
                group_size = random.randint(1, 10)
                for _ in range(group_size):
                    creature_id = f"{species.value}_{lon}_{lat}_{random.randint(0, 1000)}"
                    self.creatures[creature_id] = MarineCreature(
                        id=creature_id,
                        species=species,
                        longitude=lon + random.uniform(-0.1, 0.1),
                        latitude=lat + random.uniform(-0.1, 0.1),
                        world_size=self.world_size
                    )
                    
    def _initialize_migration_routes(self):
        """Initialize migration routes for marine species."""
        # Create major ocean currents as migration routes
        currents = [
            # Pacific Ocean
            {"name": "Kuroshio Current", "start": (130, 30), "end": (150, 40)},
            {"name": "California Current", "start": (-130, 40), "end": (-120, 30)},
            {"name": "Peru Current", "start": (-80, -10), "end": (-70, -20)},
            # Atlantic Ocean
            {"name": "Gulf Stream", "start": (-80, 25), "end": (-50, 40)},
            {"name": "Canary Current", "start": (-20, 30), "end": (-10, 20)},
            {"name": "Benguela Current", "start": (10, -30), "end": (20, -20)},
            # Indian Ocean
            {"name": "Agulhas Current", "start": (30, -35), "end": (40, -25)},
            {"name": "West Australian Current", "start": (110, -30), "end": (120, -20)}
        ]
        
        for current in currents:
            route_id = f"route_{current['name']}"
            self.migration_routes[route_id] = self._generate_route_points(
                current['start'],
                current['end']
            )
            
    def _generate_route_points(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Generate points along a migration route."""
        points = []
        steps = 10  # Number of points to generate
        
        for i in range(steps + 1):
            t = i / steps
            lon = start[0] + (end[0] - start[0]) * t
            lat = start[1] + (end[1] - start[1]) * t
            points.append((lon, lat))
            
        return points
        
    def _initialize_social_groups(self):
        """Initialize social groups for marine creatures."""
        # Group creatures by species and proximity
        species_groups = {}
        for creature_id, creature in self.creatures.items():
            if creature.species not in species_groups:
                species_groups[creature.species] = []
            species_groups[creature.species].append(creature)
            
        # Create social groups for each species
        for species, creatures in species_groups.items():
            if self.species_data[species]['social']:
                # Group creatures that are close to each other
                for creature in creatures:
                    nearby = self._find_nearby_creatures(creature, creatures)
                    if nearby:
                        group_id = f"group_{species.value}_{len(self.social_groups)}"
                        self.social_groups[group_id] = {c.id for c in nearby}
                        
    def _find_nearby_creatures(self, creature: MarineCreature, all_creatures: List[MarineCreature], max_distance: float = 1.0) -> List[MarineCreature]:
        """Find creatures near a given creature."""
        nearby = []
        for other in all_creatures:
            if other.id != creature.id:
                distance = self._calculate_distance(creature, other)
                if distance <= max_distance:
                    nearby.append(other)
        return nearby
        
    def _calculate_distance(self, c1: MarineCreature, c2: MarineCreature) -> float:
        """Calculate distance between two creatures."""
        return ((c2.longitude - c1.longitude) ** 2 + (c2.latitude - c1.latitude) ** 2) ** 0.5
        
    def _initialize_territories(self):
        """Initialize territories for territorial marine creatures."""
        for creature_id, creature in self.creatures.items():
            if self.species_data[creature.species].get('territorial', False):
                # Create a territory around the creature's position
                territory_size = self.species_data[creature.species].get('territory_size', 1.0)
                self.territories[creature_id] = (
                    creature.longitude,
                    creature.latitude,
                    territory_size
                )
        
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
        
    def update(self, time_delta: float, marine_state: Dict):
        """Update marine system state."""
        # Update all creatures
        for creature in list(self.creatures.values()):
            # Get environmental conditions at creature's location
            conditions = {
                "temperature": marine_state["temperature"](creature.position),
                "salinity": marine_state["salinity"](creature.position),
                "oxygen": marine_state["oxygen"](creature.position),
                "current": marine_state["current"](creature.position),
                "depth": marine_state["depth"](creature.position),
                "tidal_range": marine_state["tidal_range"](creature.position)
            }
            
            # Update creature state
            creature.update(time_delta, conditions)
            
            # Check if creature should die
            if creature.should_die(conditions):
                self.creatures.pop(creature.id)
                continue
                
            # Check if creature should mate
            if creature.should_mate(conditions):
                self._handle_mating(creature)
                
            # Check if creature should migrate
            if creature.should_migrate(conditions):
                self._handle_migration(creature, conditions)
                
            # Update creature's position based on currents
            self._update_position(creature, conditions)
            
        # Spawn new creatures if needed
        if len(self.creatures) < self.max_creatures:
            self.spawn_creature(random.choice(list(MarineSpecies)))
            
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