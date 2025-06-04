from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Zone:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    size: float = 0.0  # Area in square units
    purpose: str = ""
    buildings: List[str] = field(default_factory=list)  # List of building IDs
    population: int = 0
    development_level: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Building:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    zone: str  # Zone name
    purpose: str = ""
    size: float = 0.0  # Area in square units
    capacity: int = 0
    occupants: Set[str] = field(default_factory=set)  # Set of agent IDs
    condition: float = 1.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Infrastructure:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    type: str = ""  # Road, bridge, water system, etc.
    location: List[Tuple[float, float]] = field(default_factory=list)
    connected_zones: List[str] = field(default_factory=list)  # List of zone names
    capacity: float = 0.0
    condition: float = 1.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class City:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    zones: List[str] = field(default_factory=list)  # List of zone names
    infrastructure: List[str] = field(default_factory=list)  # List of infrastructure IDs
    population: int = 0
    development_level: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class UrbanSystem:
    def __init__(self, world):
        """Initialize the urban system."""
        self.world = world
        self.zones: Dict[str, Zone] = {}
        self.buildings: Dict[str, Building] = {}
        self.infrastructure: Dict[str, Infrastructure] = {}
        self.cities: Dict[str, City] = {}
        
    def create_zone(self, name: str, creator: str,
                   location: Tuple[float, float], size: float,
                   purpose: str = "") -> Zone:
        """Create a new zone."""
        if name in self.zones:
            logger.warning(f"Zone {name} already exists")
            return self.zones[name]
            
        zone = Zone(
            name=name,
            creator=creator,
            location=location,
            size=size,
            purpose=purpose
        )
        
        self.zones[name] = zone
        logger.info(f"Created new zone: {name}")
        return zone
        
    def create_building(self, name: str, creator: str,
                       location: Tuple[float, float], zone: str,
                       purpose: str = "", size: float = 0.0,
                       capacity: int = 0) -> Building:
        """Create a new building."""
        if name in self.buildings:
            logger.warning(f"Building {name} already exists")
            return self.buildings[name]
            
        building = Building(
            name=name,
            creator=creator,
            location=location,
            zone=zone,
            purpose=purpose,
            size=size,
            capacity=capacity
        )
        
        self.buildings[name] = building
        if zone in self.zones:
            self.zones[zone].buildings.append(name)
        logger.info(f"Created new building: {name}")
        return building
        
    def create_infrastructure(self, name: str, creator: str,
                            type: str, location: List[Tuple[float, float]],
                            capacity: float = 0.0) -> Infrastructure:
        """Create new infrastructure."""
        if name in self.infrastructure:
            logger.warning(f"Infrastructure {name} already exists")
            return self.infrastructure[name]
            
        infrastructure = Infrastructure(
            name=name,
            creator=creator,
            type=type,
            location=location,
            capacity=capacity
        )
        
        self.infrastructure[name] = infrastructure
        logger.info(f"Created new infrastructure: {name}")
        return infrastructure
        
    def create_city(self, name: str, creator: str,
                   location: Tuple[float, float]) -> City:
        """Create a new city."""
        if name in self.cities:
            logger.warning(f"City {name} already exists")
            return self.cities[name]
            
        city = City(
            name=name,
            creator=creator,
            location=location
        )
        
        self.cities[name] = city
        logger.info(f"Created new city: {name}")
        return city
        
    def add_zone_to_city(self, city: str, zone: str):
        """Add a zone to a city."""
        if city in self.cities and zone in self.zones:
            self.cities[city].zones.append(zone)
            logger.info(f"Added zone {zone} to city {city}")
            
    def add_infrastructure_to_city(self, city: str, infrastructure: str):
        """Add infrastructure to a city."""
        if city in self.cities and infrastructure in self.infrastructure:
            self.cities[city].infrastructure.append(infrastructure)
            logger.info(f"Added infrastructure {infrastructure} to city {city}")
            
    def add_occupant_to_building(self, building: str, agent_id: str):
        """Add an occupant to a building."""
        if building in self.buildings:
            if len(self.buildings[building].occupants) < self.buildings[building].capacity:
                self.buildings[building].occupants.add(agent_id)
                logger.info(f"Added occupant {agent_id} to building {building}")
            else:
                logger.warning(f"Building {building} is at capacity")
                
    def remove_occupant_from_building(self, building: str, agent_id: str):
        """Remove an occupant from a building."""
        if building in self.buildings:
            self.buildings[building].occupants.discard(agent_id)
            logger.info(f"Removed occupant {agent_id} from building {building}")
            
    def evolve_zone(self, name: str, time_delta: float):
        """Evolve a zone over time."""
        if name not in self.zones:
            return
            
        zone = self.zones[name]
        
        # Update development level based on buildings and population
        building_factor = min(1.0, len(zone.buildings) / 100.0)
        population_factor = min(1.0, zone.population / 1000.0)
        zone.development_level = (zone.development_level * 0.9 + 
                                (building_factor * 0.6 + population_factor * 0.4) * 0.1)
                                
    def evolve_building(self, name: str, time_delta: float):
        """Evolve a building over time."""
        if name not in self.buildings:
            return
            
        building = self.buildings[name]
        
        # Update condition based on occupancy
        occupancy_factor = len(building.occupants) / building.capacity
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            building.condition = max(0.0,
                building.condition - (1.0 - occupancy_factor) * 0.01)
                
    def evolve_infrastructure(self, name: str, time_delta: float):
        """Evolve infrastructure over time."""
        if name not in self.infrastructure:
            return
            
        infrastructure = self.infrastructure[name]
        
        # Update condition based on usage
        usage_factor = len(infrastructure.connected_zones) / 10.0
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            infrastructure.condition = max(0.0,
                infrastructure.condition - (1.0 - usage_factor) * 0.01)
                
    def evolve_city(self, name: str, time_delta: float):
        """Evolve a city over time."""
        if name not in self.cities:
            return
            
        city = self.cities[name]
        
        # Update population
        city.population = sum(
            len(self.buildings[b].occupants)
            for z in city.zones
            if z in self.zones
            for b in self.zones[z].buildings
            if b in self.buildings
        )
        
        # Update development level
        zone_development = sum(
            self.zones[z].development_level
            for z in city.zones
            if z in self.zones
        )
        if city.zones:
            zone_development /= len(city.zones)
            
        infrastructure_development = sum(
            self.infrastructure[i].condition
            for i in city.infrastructure
            if i in self.infrastructure
        )
        if city.infrastructure:
            infrastructure_development /= len(city.infrastructure)
            
        city.development_level = (city.development_level * 0.9 + 
                                (zone_development * 0.6 + infrastructure_development * 0.4) * 0.1)
                                
    def update(self, time_delta: float):
        """Update urban system state."""
        # Evolve zones
        for name in list(self.zones.keys()):
            self.evolve_zone(name, time_delta)
            
        # Evolve buildings
        for name in list(self.buildings.keys()):
            self.evolve_building(name, time_delta)
            
        # Evolve infrastructure
        for name in list(self.infrastructure.keys()):
            self.evolve_infrastructure(name, time_delta)
            
        # Evolve cities
        for name in list(self.cities.keys()):
            self.evolve_city(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert urban system state to dictionary for serialization."""
        return {
            "zones": {
                name: {
                    "name": zone.name,
                    "creator": zone.creator,
                    "creation_date": zone.creation_date,
                    "location": zone.location,
                    "size": zone.size,
                    "purpose": zone.purpose,
                    "buildings": zone.buildings,
                    "population": zone.population,
                    "development_level": zone.development_level,
                    "created_at": zone.created_at,
                    "last_update": zone.last_update
                }
                for name, zone in self.zones.items()
            },
            "buildings": {
                name: {
                    "name": building.name,
                    "creator": building.creator,
                    "creation_date": building.creation_date,
                    "location": building.location,
                    "zone": building.zone,
                    "purpose": building.purpose,
                    "size": building.size,
                    "capacity": building.capacity,
                    "occupants": list(building.occupants),
                    "condition": building.condition,
                    "created_at": building.created_at,
                    "last_update": building.last_update
                }
                for name, building in self.buildings.items()
            },
            "infrastructure": {
                name: {
                    "name": infra.name,
                    "creator": infra.creator,
                    "creation_date": infra.creation_date,
                    "type": infra.type,
                    "location": infra.location,
                    "connected_zones": infra.connected_zones,
                    "capacity": infra.capacity,
                    "condition": infra.condition,
                    "created_at": infra.created_at,
                    "last_update": infra.last_update
                }
                for name, infra in self.infrastructure.items()
            },
            "cities": {
                name: {
                    "name": city.name,
                    "creator": city.creator,
                    "creation_date": city.creation_date,
                    "location": city.location,
                    "zones": city.zones,
                    "infrastructure": city.infrastructure,
                    "population": city.population,
                    "development_level": city.development_level,
                    "created_at": city.created_at,
                    "last_update": city.last_update
                }
                for name, city in self.cities.items()
            }
        } 