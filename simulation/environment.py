from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class Environment:
    """Represents the physical environment of the simulation."""
    world: 'World'  # Reference to parent World
    width: int = 1000  # Width in units
    height: int = 1000  # Height in units
    type: str = "terrestrial"
    name: str = "Earth"
    description: str = "A simulated Earth-like environment"
    temperature: float = 20.0  # Average temperature in Celsius
    humidity: float = 0.5  # 0-1 scale
    precipitation: float = 0.3  # 0-1 scale
    wind_speed: float = 0.0  # m/s
    wind_direction: float = 0.0  # degrees
    time_of_day: float = 0.0  # 0-24 hours
    season: str = "summer"
    created_at: float = field(default_factory=datetime.now().timestamp)
    last_update: float = field(default_factory=datetime.now().timestamp)
    pressure: float = 1013.25  # hPa (standard atmospheric pressure)
    visibility: float = 10.0  # km

    def __post_init__(self):
        """Initialize environment after creation."""
        self.logger = get_logger(__name__)
        self.logger.info(f"Initializing environment: {self.name}")
        
    def get_terrain_at(self, x: float, y: float) -> str:
        """Get terrain type at specified coordinates."""
        # Convert world coordinates to terrain grid coordinates
        grid_x = int(x * self.width / self.world.max_longitude)
        grid_y = int(y * self.height / self.world.max_latitude)
        
        # Get terrain from terrain system
        return self.world.terrain.get_terrain_at(grid_x, grid_y)
        
    def get_temperature_at(self, x: float, y: float) -> float:
        """Get temperature at specified coordinates."""
        base_temp = self.temperature
        # Add variation based on terrain and elevation
        terrain = self.get_terrain_at(x, y)
        if terrain == "mountain":
            base_temp -= 10.0
        elif terrain == "desert":
            base_temp += 5.0
        return base_temp
        
    def get_humidity_at(self, x: float, y: float) -> float:
        """Get humidity at specified coordinates."""
        base_humidity = self.humidity
        # Add variation based on terrain and precipitation
        terrain = self.get_terrain_at(x, y)
        if terrain == "swamp":
            base_humidity += 0.3
        elif terrain == "desert":
            base_humidity -= 0.2
        return max(0.0, min(1.0, base_humidity))
        
    def get_wind_at(self, x: float, y: float) -> Tuple[float, float]:
        """Get wind speed and direction at specified coordinates."""
        # Add terrain-based wind variations
        terrain = self.get_terrain_at(x, y)
        speed_modifier = 1.0
        if terrain == "mountain":
            speed_modifier = 1.5
        elif terrain == "forest":
            speed_modifier = 0.7
        return (self.wind_speed * speed_modifier, self.wind_direction)
        
    def update(self, time_delta: float):
        """Update environment state."""
        # Update time of day
        self.time_of_day = (self.time_of_day + time_delta) % 24.0
        
        # Update temperature based on time of day
        if 6 <= self.time_of_day < 18:  # Daytime
            self.temperature += 0.1 * time_delta
        else:  # Nighttime
            self.temperature -= 0.1 * time_delta
            
        # Update wind
        self.wind_speed += random.uniform(-0.1, 0.1) * time_delta
        self.wind_speed = max(0.0, min(30.0, self.wind_speed))
        self.wind_direction = (self.wind_direction + random.uniform(-5, 5)) % 360.0
        
        # Update precipitation
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            self.precipitation = random.uniform(0.0, 1.0)
            
        self.last_update = datetime.now().timestamp()
        
    def get_state(self) -> Dict:
        """Get current environment state."""
        return {
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "time_of_day": self.time_of_day,
            "season": self.season,
            "width": self.width,
            "height": self.height
        }

    def to_dict(self) -> Dict:
        """Convert environment state to dictionary for serialization."""
        return {
            'temperature': self.temperature,
            'precipitation': self.precipitation,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'visibility': self.visibility
        }

@dataclass
class Resource:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    type: str = ""
    quantity: float = 0.0
    regeneration_rate: float = 0.0
    depletion_rate: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class ClimateZone:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    size: float = 0.0  # Area in square units
    temperature: float = 0.0
    precipitation: float = 0.0
    humidity: float = 0.0
    wind_speed: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class EnvironmentalImpact:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    type: str = ""
    severity: float = 0.0  # 0-1 scale
    duration: float = 0.0  # Time in hours
    affected_resources: List[str] = field(default_factory=list)  # List of resource names
    affected_zones: List[str] = field(default_factory=list)  # List of zone names
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Ecosystem:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    size: float = 0.0  # Area in square units
    biodiversity: float = 0.0  # 0-1 scale
    stability: float = 1.0  # 0-1 scale
    resources: List[str] = field(default_factory=list)  # List of resource names
    climate_zone: Optional[str] = None  # Zone name
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class EnvironmentalSystem:
    def __init__(self, world):
        """Initialize the environmental system."""
        self.world = world
        self.width = 1000  # Default width in units
        self.height = 1000  # Default height in units
        self.environments: Dict[str, Environment] = {}
        self.resources: Dict[str, Resource] = {}
        self.climate_zones: Dict[str, ClimateZone] = {}
        self.impacts: Dict[str, EnvironmentalImpact] = {}
        self.ecosystems: Dict[str, Ecosystem] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the environmental system with minimal structure."""
        logger.info("Initializing environmental system...")
        
        # Create a basic environment - but don't prescribe its type
        self.environments["initial_environment"] = Environment(
            world=self.world,
            width=self.world.max_longitude,
            height=self.world.max_latitude
        )
        
        logger.info("Environmental system initialization complete")
        
    def create_environment(self, type: str, name: str, description: str,
                          properties: Dict[str, Any] = None) -> Environment:
        """Create new environment with custom properties."""
        environment = Environment(
            world=self.world,
            width=self.world.max_longitude,
            height=self.world.max_latitude,
            type=type,
            name=name,
            description=description,
            properties=properties or {}
        )
        
        environment_id = f"environment_{len(self.environments)}"
        self.environments[environment_id] = environment
        logger.info(f"Created new environment: {name} of type {type}")
        return environment
        
    def create_resource(self, name: str, creator: str,
                       location: Tuple[float, float], type: str,
                       quantity: float, regeneration_rate: float) -> Resource:
        """Create a new resource."""
        if name in self.resources:
            logger.warning(f"Resource {name} already exists")
            return self.resources[name]
            
        resource = Resource(
            name=name,
            creator=creator,
            location=location,
            type=type,
            quantity=quantity,
            regeneration_rate=regeneration_rate
        )
        
        self.resources[name] = resource
        logger.info(f"Created new resource: {name}")
        return resource
        
    def create_climate_zone(self, name: str, creator: str,
                           location: Tuple[float, float], size: float) -> ClimateZone:
        """Create a new climate zone."""
        if name in self.climate_zones:
            logger.warning(f"Climate zone {name} already exists")
            return self.climate_zones[name]
            
        zone = ClimateZone(
            name=name,
            creator=creator,
            location=location,
            size=size
        )
        
        self.climate_zones[name] = zone
        logger.info(f"Created new climate zone: {name}")
        return zone
        
    def create_impact(self, name: str, creator: str,
                     location: Tuple[float, float], type: str) -> EnvironmentalImpact:
        """Create a new environmental impact."""
        if name in self.impacts:
            logger.warning(f"Impact {name} already exists")
            return self.impacts[name]
            
        impact = EnvironmentalImpact(
            name=name,
            creator=creator,
            location=location,
            type=type
        )
        
        self.impacts[name] = impact
        logger.info(f"Created new impact: {name}")
        return impact
        
    def create_ecosystem(self, name: str, creator: str,
                        location: Tuple[float, float], size: float) -> Ecosystem:
        """Create a new ecosystem."""
        if name in self.ecosystems:
            logger.warning(f"Ecosystem {name} already exists")
            return self.ecosystems[name]
            
        ecosystem = Ecosystem(
            name=name,
            creator=creator,
            location=location,
            size=size
        )
        
        self.ecosystems[name] = ecosystem
        logger.info(f"Created new ecosystem: {name}")
        return ecosystem
        
    def add_resource_to_ecosystem(self, ecosystem: str, resource: str):
        """Add a resource to an ecosystem."""
        if ecosystem in self.ecosystems and resource in self.resources:
            self.ecosystems[ecosystem].resources.append(resource)
            logger.info(f"Added resource {resource} to ecosystem {ecosystem}")
            
    def add_impact_to_resource(self, impact: str, resource: str):
        """Add a resource to an impact's affected resources."""
        if impact in self.impacts and resource in self.resources:
            self.impacts[impact].affected_resources.append(resource)
            logger.info(f"Added resource {resource} to impact {impact}")
            
    def add_impact_to_zone(self, impact: str, zone: str):
        """Add a zone to an impact's affected zones."""
        if impact in self.impacts and zone in self.climate_zones:
            self.impacts[impact].affected_zones.append(zone)
            logger.info(f"Added zone {zone} to impact {impact}")
            
    def evolve_resource(self, name: str, time_delta: float):
        """Evolve a resource over time."""
        if name not in self.resources:
            return
            
        resource = self.resources[name]
        
        # Update quantity based on regeneration and depletion
        net_change = (resource.regeneration_rate - resource.depletion_rate) * time_delta
        resource.quantity = max(0.0, resource.quantity + net_change)
        
    def evolve_climate_zone(self, name: str, time_delta: float):
        """Evolve a climate zone over time."""
        if name not in self.climate_zones:
            return
            
        zone = self.climate_zones[name]
        
        # Update climate parameters
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            zone.temperature += random.uniform(-0.1, 0.1)
            zone.precipitation += random.uniform(-0.1, 0.1)
            zone.humidity += random.uniform(-0.1, 0.1)
            zone.wind_speed += random.uniform(-0.1, 0.1)
            
    def evolve_impact(self, name: str, time_delta: float):
        """Evolve an environmental impact over time."""
        if name not in self.impacts:
            return
            
        impact = self.impacts[name]
        
        # Update duration
        impact.duration += time_delta
        
        # Update severity based on affected resources and zones
        resource_factor = min(1.0, len(impact.affected_resources) / 10.0)
        zone_factor = min(1.0, len(impact.affected_zones) / 5.0)
        impact.severity = (impact.severity * 0.9 + 
                         (resource_factor * 0.6 + zone_factor * 0.4) * 0.1)
                         
    def evolve_ecosystem(self, name: str, time_delta: float):
        """Evolve an ecosystem over time."""
        if name not in self.ecosystems:
            return
            
        ecosystem = self.ecosystems[name]
        
        # Update biodiversity based on resources
        resource_factor = min(1.0, len(ecosystem.resources) / 20.0)
        ecosystem.biodiversity = (ecosystem.biodiversity * 0.9 + resource_factor * 0.1)
        
        # Update stability based on climate and impacts
        climate_stability = 1.0
        if ecosystem.climate_zone in self.climate_zones:
            zone = self.climate_zones[ecosystem.climate_zone]
            climate_stability = 1.0 - abs(zone.temperature) - abs(zone.precipitation)
            
        impact_stability = 1.0
        for impact in self.impacts.values():
            if ecosystem.name in impact.affected_zones:
                impact_stability *= (1.0 - impact.severity)
                
        ecosystem.stability = (ecosystem.stability * 0.9 + 
                             (climate_stability * 0.6 + impact_stability * 0.4) * 0.1)
                             
    def update(self, time_delta: float):
        """Update environmental system state."""
        # Evolve resources
        for name in list(self.resources.keys()):
            self.evolve_resource(name, time_delta)
            
        # Evolve climate zones
        for name in list(self.climate_zones.keys()):
            self.evolve_climate_zone(name, time_delta)
            
        # Evolve impacts
        for name in list(self.impacts.keys()):
            self.evolve_impact(name, time_delta)
            
        # Evolve ecosystems
        for name in list(self.ecosystems.keys()):
            self.evolve_ecosystem(name, time_delta)
        
    def to_dict(self) -> Dict:
        """Convert environmental system state to dictionary for serialization."""
        return {
            "environments": {
                environment_id: {
                    "type": environment.type,
                    "name": environment.name,
                    "description": environment.description,
                    "temperature": environment.temperature,
                    "humidity": environment.humidity,
                    "precipitation": environment.precipitation,
                    "wind_speed": environment.wind_speed,
                    "wind_direction": environment.wind_direction,
                    "time_of_day": environment.time_of_day,
                    "season": environment.season,
                    "width": environment.width,
                    "height": environment.height,
                    "created_at": environment.created_at,
                    "last_update": environment.last_update
                }
                for environment_id, environment in self.environments.items()
            },
            "resources": {
                name: {
                    "name": resource.name,
                    "creator": resource.creator,
                    "creation_date": resource.creation_date,
                    "location": resource.location,
                    "type": resource.type,
                    "quantity": resource.quantity,
                    "regeneration_rate": resource.regeneration_rate,
                    "depletion_rate": resource.depletion_rate,
                    "created_at": resource.created_at,
                    "last_update": resource.last_update
                }
                for name, resource in self.resources.items()
            },
            "climate_zones": {
                name: {
                    "name": zone.name,
                    "creator": zone.creator,
                    "creation_date": zone.creation_date,
                    "location": zone.location,
                    "size": zone.size,
                    "temperature": zone.temperature,
                    "precipitation": zone.precipitation,
                    "humidity": zone.humidity,
                    "wind_speed": zone.wind_speed,
                    "created_at": zone.created_at,
                    "last_update": zone.last_update
                }
                for name, zone in self.climate_zones.items()
            },
            "impacts": {
                name: {
                    "name": impact.name,
                    "creator": impact.creator,
                    "creation_date": impact.creation_date,
                    "location": impact.location,
                    "type": impact.type,
                    "severity": impact.severity,
                    "duration": impact.duration,
                    "affected_resources": impact.affected_resources,
                    "affected_zones": impact.affected_zones,
                    "created_at": impact.created_at,
                    "last_update": impact.last_update
                }
                for name, impact in self.impacts.items()
            },
            "ecosystems": {
                name: {
                    "name": ecosystem.name,
                    "creator": ecosystem.creator,
                    "creation_date": ecosystem.creation_date,
                    "location": ecosystem.location,
                    "size": ecosystem.size,
                    "biodiversity": ecosystem.biodiversity,
                    "stability": ecosystem.stability,
                    "resources": ecosystem.resources,
                    "climate_zone": ecosystem.climate_zone,
                    "created_at": ecosystem.created_at,
                    "last_update": ecosystem.last_update
                }
                for name, ecosystem in self.ecosystems.items()
            }
        } 