from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class Discovery:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    type: str = ""  # Let agents define types
    description: str = ""
    significance: float = 0.0  # 0-1 scale
    verified_by: Set[str] = field(default_factory=set)  # Set of agent IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Map:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    scale: float = 1.0  # Units per pixel
    center: Tuple[float, float] = (0.0, 0.0)
    bounds: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)  # (min_x, min_y, max_x, max_y)
    features: List[str] = field(default_factory=list)  # List of discovery names
    accuracy: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Route:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    waypoints: List[Tuple[float, float]] = field(default_factory=list)
    difficulty: float = 0.0  # 0-1 scale
    safety: float = 1.0  # 0-1 scale
    resources_required: Dict[str, float] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class ExplorationSystem:
    def __init__(self, world):
        """Initialize the exploration system."""
        self.world = world
        self.discoveries: Dict[str, Discovery] = {}
        self.maps: Dict[str, Map] = {}
        self.routes: Dict[str, Route] = {}
        
    def create_discovery(self, name: str, creator: str,
                        location: Tuple[float, float], type: str,
                        description: str = "") -> Discovery:
        """Create a new discovery."""
        if name in self.discoveries:
            logger.warning(f"Discovery {name} already exists")
            return self.discoveries[name]
            
        discovery = Discovery(
            name=name,
            creator=creator,
            location=location,
            type=type,
            description=description
        )
        
        self.discoveries[name] = discovery
        logger.info(f"Created new discovery: {name}")
        return discovery
        
    def create_map(self, name: str, creator: str,
                  scale: float, center: Tuple[float, float],
                  bounds: Tuple[float, float, float, float]) -> Map:
        """Create a new map."""
        if name in self.maps:
            logger.warning(f"Map {name} already exists")
            return self.maps[name]
            
        map_obj = Map(
            name=name,
            creator=creator,
            scale=scale,
            center=center,
            bounds=bounds
        )
        
        self.maps[name] = map_obj
        logger.info(f"Created new map: {name}")
        return map_obj
        
    def create_route(self, name: str, creator: str,
                    waypoints: List[Tuple[float, float]]) -> Route:
        """Create a new route."""
        if name in self.routes:
            logger.warning(f"Route {name} already exists")
            return self.routes[name]
            
        route = Route(
            name=name,
            creator=creator,
            waypoints=waypoints
        )
        
        self.routes[name] = route
        logger.info(f"Created new route: {name}")
        return route
        
    def add_discovery_to_map(self, map_name: str, discovery_name: str):
        """Add a discovery to a map."""
        if map_name in self.maps and discovery_name in self.discoveries:
            self.maps[map_name].features.append(discovery_name)
            logger.info(f"Added discovery {discovery_name} to map {map_name}")
            
    def verify_discovery(self, discovery_name: str, agent_id: str):
        """Add a verification to a discovery."""
        if discovery_name in self.discoveries:
            self.discoveries[discovery_name].verified_by.add(agent_id)
            logger.info(f"Added verification by {agent_id} to discovery {discovery_name}")
            
    def evolve_discovery(self, name: str, time_delta: float):
        """Evolve a discovery over time."""
        if name not in self.discoveries:
            return
            
        discovery = self.discoveries[name]
        
        # Update significance based on verifications
        verification_factor = min(1.0, len(discovery.verified_by) / 10.0)
        discovery.significance = (discovery.significance * 0.9 + verification_factor * 0.1)
        
    def evolve_map(self, name: str, time_delta: float):
        """Evolve a map over time."""
        if name not in self.maps:
            return
            
        map_obj = self.maps[name]
        
        # Update accuracy based on verified discoveries
        verified_features = sum(
            1 for feature in map_obj.features
            if feature in self.discoveries
            and len(self.discoveries[feature].verified_by) > 0
        )
        
        if map_obj.features:
            accuracy_factor = verified_features / len(map_obj.features)
            map_obj.accuracy = (map_obj.accuracy * 0.9 + accuracy_factor * 0.1)
            
    def evolve_route(self, name: str, time_delta: float):
        """Evolve a route over time."""
        if name not in self.routes:
            return
            
        route = self.routes[name]
        
        # Update safety based on random events
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            route.safety = max(0.0,
                route.safety - random.uniform(0.0, 0.1))
                
        # Update difficulty based on safety
        route.difficulty = 1.0 - route.safety
        
    def update(self, time_delta: float):
        """Update exploration system state."""
        # Evolve discoveries
        for name in list(self.discoveries.keys()):
            self.evolve_discovery(name, time_delta)
            
        # Evolve maps
        for name in list(self.maps.keys()):
            self.evolve_map(name, time_delta)
            
        # Evolve routes
        for name in list(self.routes.keys()):
            self.evolve_route(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert exploration system state to dictionary for serialization."""
        return {
            "discoveries": {
                name: {
                    "name": discovery.name,
                    "creator": discovery.creator,
                    "creation_date": discovery.creation_date,
                    "location": discovery.location,
                    "type": discovery.type,
                    "description": discovery.description,
                    "significance": discovery.significance,
                    "verified_by": list(discovery.verified_by),
                    "created_at": discovery.created_at,
                    "last_update": discovery.last_update
                }
                for name, discovery in self.discoveries.items()
            },
            "maps": {
                name: {
                    "name": map_obj.name,
                    "creator": map_obj.creator,
                    "creation_date": map_obj.creation_date,
                    "scale": map_obj.scale,
                    "center": map_obj.center,
                    "bounds": map_obj.bounds,
                    "features": map_obj.features,
                    "accuracy": map_obj.accuracy,
                    "created_at": map_obj.created_at,
                    "last_update": map_obj.last_update
                }
                for name, map_obj in self.maps.items()
            },
            "routes": {
                name: {
                    "name": route.name,
                    "creator": route.creator,
                    "creation_date": route.creation_date,
                    "waypoints": route.waypoints,
                    "difficulty": route.difficulty,
                    "safety": route.safety,
                    "resources_required": route.resources_required,
                    "created_at": route.created_at,
                    "last_update": route.last_update
                }
                for name, route in self.routes.items()
            }
        } 