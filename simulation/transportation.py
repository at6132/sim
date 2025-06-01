from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TransportationType(Enum):
    # Land Transportation
    WALKING = "walking"
    RUNNING = "running"
    HORSE = "horse"
    CART = "cart"
    WAGON = "wagon"
    CARRIAGE = "carriage"
    RAILROAD = "railroad"
    AUTOMOBILE = "automobile"
    TRUCK = "truck"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    
    # Water Transportation
    RAFT = "raft"
    CANOE = "canoe"
    BOAT = "boat"
    SAILBOAT = "sailboat"
    GALLEY = "galley"
    CARAVEL = "caravel"
    GALLEON = "galleon"
    STEAMSHIP = "steamship"
    MOTORBOAT = "motorboat"
    YACHT = "yacht"
    CRUISE_SHIP = "cruise_ship"
    CARGO_SHIP = "cargo_ship"
    TANKER = "tanker"
    SUBMARINE = "submarine"
    
    # Air Transportation
    BALLOON = "balloon"
    AIRSHIP = "airship"
    GLIDER = "glider"
    AIRPLANE = "airplane"
    HELICOPTER = "helicopter"
    JET = "jet"
    SPACECRAFT = "spacecraft"
    
    # Special
    TELEPORT = "teleport"
    PORTAL = "portal"
    WORMHOLE = "wormhole"

class TransportationSystem:
    def __init__(self, world):
        self.world = world
        self.routes = {}  # (start_lon, start_lat, end_lon, end_lat) -> Route
        self.vehicles = {}  # vehicle_id -> Vehicle
        self.ports = {}  # (lon, lat) -> Port
        self.roads = {}  # (lon, lat) -> Road
        self.initialize_transportation()
        
    def initialize_transportation(self):
        """Initialize the transportation system."""
        logger.info("Initializing transportation system...")
        
        # Initialize basic transportation infrastructure
        self._initialize_roads()
        self._initialize_ports()
        self._initialize_routes()
        
        logger.info("Transportation system initialization complete")
        
    def _initialize_roads(self):
        """Initialize basic road network."""
        # Create roads between major settlements
        for lon in range(-180, 181, 10):  # Every 10 degrees
            for lat in range(-90, 91, 10):
                if not self.world.terrain.get_terrain_at(lon, lat)['is_water']:
                    self.roads[(lon, lat)] = {
                        'type': 'dirt',
                        'quality': 0.5,
                        'capacity': 1.0,
                        'connections': []
                    }
        
        # Connect nearby roads
        for (lon1, lat1), road1 in self.roads.items():
            for (lon2, lat2), road2 in self.roads.items():
                if (lon1, lat1) != (lon2, lat2):
                    distance = ((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) ** 0.5
                    if distance <= 15:  # Connect roads within 15 degrees
                        road1['connections'].append((lon2, lat2))
                        road2['connections'].append((lon1, lat1))
        
    def _initialize_ports(self):
        """Initialize basic port network."""
        # Create ports along coastlines
        for lon in range(-180, 181, 5):  # Every 5 degrees
            for lat in range(-90, 91, 5):
                terrain = self.world.terrain.get_terrain_at(lon, lat)
                if terrain['is_water']:
                    # Check for nearby land
                    has_land = False
                    for dlon in [-1, 0, 1]:
                        for dlat in [-1, 0, 1]:
                            if not self.world.terrain.get_terrain_at(lon + dlon, lat + dlat)['is_water']:
                                has_land = True
                                break
                        if has_land:
                            break
                    
                    if has_land:
                        self.ports[(lon, lat)] = {
                            'type': 'basic',
                            'capacity': 1.0,
                            'connections': []
                        }
        
        # Connect nearby ports
        for (lon1, lat1), port1 in self.ports.items():
            for (lon2, lat2), port2 in self.ports.items():
                if (lon1, lat1) != (lon2, lat2):
                    distance = ((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) ** 0.5
                    if distance <= 30:  # Connect ports within 30 degrees
                        port1['connections'].append((lon2, lat2))
                        port2['connections'].append((lon1, lat1))
        
    def _initialize_routes(self):
        """Initialize basic transportation routes."""
        # Create routes between connected roads
        for (lon1, lat1), road1 in self.roads.items():
            for end_lon, end_lat in road1['connections']:
                route_id = (lon1, lat1, end_lon, end_lat)
                if route_id not in self.routes:
                    self.routes[route_id] = {
                        'type': 'road',
                        'distance': ((end_lon - lon1) ** 2 + (end_lat - lat1) ** 2) ** 0.5,
                        'capacity': 1.0,
                        'quality': 0.5
                    }
        
        # Create routes between connected ports
        for (lon1, lat1), port1 in self.ports.items():
            for end_lon, end_lat in port1['connections']:
                route_id = (lon1, lat1, end_lon, end_lat)
                if route_id not in self.routes:
                    self.routes[route_id] = {
                        'type': 'sea',
                        'distance': ((end_lon - lon1) ** 2 + (end_lat - lat1) ** 2) ** 0.5,
                        'capacity': 2.0,
                        'quality': 0.7
                    }
    
    def get_route(self, start_lon: float, start_lat: float, end_lon: float, end_lat: float) -> Optional[Dict]:
        """Get route information between two points."""
        route_id = (start_lon, start_lat, end_lon, end_lat)
        return self.routes.get(route_id)
    
    def get_road(self, lon: float, lat: float) -> Optional[Dict]:
        """Get road information at a location."""
        return self.roads.get((lon, lat))
    
    def get_port(self, lon: float, lat: float) -> Optional[Dict]:
        """Get port information at a location."""
        return self.ports.get((lon, lat))
    
    def get_state(self) -> Dict:
        """Get current transportation system state."""
        return {
            'routes': self.routes,
            'roads': self.roads,
            'ports': self.ports,
            'vehicles': self.vehicles
        }

    def _initialize_technology_tree(self) -> Dict[TransportationType, List[TransportationType]]:
        """Initialize the technology tree for transportation types."""
        return {
            TransportationType.WALKING: [],
            TransportationType.RUNNING: [TransportationType.WALKING],
            TransportationType.HORSE: [TransportationType.WALKING],
            TransportationType.CART: [TransportationType.HORSE],
            TransportationType.WAGON: [TransportationType.CART],
            TransportationType.CARRIAGE: [TransportationType.WAGON],
            TransportationType.RAILROAD: [TransportationType.CARRIAGE],
            TransportationType.AUTOMOBILE: [TransportationType.RAILROAD],
            TransportationType.TRUCK: [TransportationType.AUTOMOBILE],
            TransportationType.BUS: [TransportationType.AUTOMOBILE],
            TransportationType.MOTORCYCLE: [TransportationType.AUTOMOBILE],
            TransportationType.BICYCLE: [TransportationType.WALKING],
            
            TransportationType.RAFT: [TransportationType.WALKING],
            TransportationType.CANOE: [TransportationType.RAFT],
            TransportationType.BOAT: [TransportationType.CANOE],
            TransportationType.SAILBOAT: [TransportationType.BOAT],
            TransportationType.GALLEY: [TransportationType.SAILBOAT],
            TransportationType.CARAVEL: [TransportationType.GALLEY],
            TransportationType.GALLEON: [TransportationType.CARAVEL],
            TransportationType.STEAMSHIP: [TransportationType.GALLEON],
            TransportationType.MOTORBOAT: [TransportationType.STEAMSHIP],
            TransportationType.YACHT: [TransportationType.MOTORBOAT],
            TransportationType.CRUISE_SHIP: [TransportationType.YACHT],
            TransportationType.CARGO_SHIP: [TransportationType.CRUISE_SHIP],
            TransportationType.TANKER: [TransportationType.CARGO_SHIP],
            TransportationType.SUBMARINE: [TransportationType.TANKER],
            
            TransportationType.BALLOON: [TransportationType.SAILBOAT],
            TransportationType.AIRSHIP: [TransportationType.BALLOON],
            TransportationType.GLIDER: [TransportationType.AIRSHIP],
            TransportationType.AIRPLANE: [TransportationType.GLIDER],
            TransportationType.HELICOPTER: [TransportationType.AIRPLANE],
            TransportationType.JET: [TransportationType.AIRPLANE],
            TransportationType.SPACECRAFT: [TransportationType.JET],
            
            TransportationType.TELEPORT: [TransportationType.SPACECRAFT],
            TransportationType.PORTAL: [TransportationType.TELEPORT],
            TransportationType.WORMHOLE: [TransportationType.PORTAL]
        }
        
    def _initialize_travel_speeds(self) -> Dict[TransportationType, float]:
        """Initialize base travel speeds in km/h."""
        return {
            TransportationType.WALKING: 5.0,
            TransportationType.RUNNING: 15.0,
            TransportationType.HORSE: 30.0,
            TransportationType.CART: 20.0,
            TransportationType.WAGON: 15.0,
            TransportationType.CARRIAGE: 25.0,
            TransportationType.RAILROAD: 60.0,
            TransportationType.AUTOMOBILE: 80.0,
            TransportationType.TRUCK: 70.0,
            TransportationType.BUS: 60.0,
            TransportationType.MOTORCYCLE: 90.0,
            TransportationType.BICYCLE: 25.0,
            
            TransportationType.RAFT: 3.0,
            TransportationType.CANOE: 5.0,
            TransportationType.BOAT: 10.0,
            TransportationType.SAILBOAT: 20.0,
            TransportationType.GALLEY: 15.0,
            TransportationType.CARAVEL: 25.0,
            TransportationType.GALLEON: 20.0,
            TransportationType.STEAMSHIP: 30.0,
            TransportationType.MOTORBOAT: 40.0,
            TransportationType.YACHT: 35.0,
            TransportationType.CRUISE_SHIP: 45.0,
            TransportationType.CARGO_SHIP: 40.0,
            TransportationType.TANKER: 35.0,
            TransportationType.SUBMARINE: 50.0,
            
            TransportationType.BALLOON: 20.0,
            TransportationType.AIRSHIP: 40.0,
            TransportationType.GLIDER: 60.0,
            TransportationType.AIRPLANE: 300.0,
            TransportationType.HELICOPTER: 250.0,
            TransportationType.JET: 800.0,
            TransportationType.SPACECRAFT: 28000.0,
            
            TransportationType.TELEPORT: float('inf'),
            TransportationType.PORTAL: float('inf'),
            TransportationType.WORMHOLE: float('inf')
        }
        
    def _initialize_terrain_penalties(self) -> Dict[TransportationType, Dict[str, float]]:
        """Initialize terrain movement penalties for each transportation type."""
        return {
            TransportationType.WALKING: {
                "mountain": 0.3,
                "hills": 0.7,
                "forest": 0.8,
                "swamp": 0.5,
                "desert": 0.7,
                "snow": 0.6,
                "ice": 0.4,
                "water": 0.0
            },
            TransportationType.HORSE: {
                "mountain": 0.2,
                "hills": 0.8,
                "forest": 0.6,
                "swamp": 0.3,
                "desert": 0.8,
                "snow": 0.5,
                "ice": 0.3,
                "water": 0.0
            },
            TransportationType.CART: {
                "mountain": 0.1,
                "hills": 0.6,
                "forest": 0.4,
                "swamp": 0.2,
                "desert": 0.7,
                "snow": 0.4,
                "ice": 0.2,
                "water": 0.0
            },
            TransportationType.RAILROAD: {
                "mountain": 0.2,
                "hills": 0.8,
                "forest": 0.9,
                "swamp": 0.7,
                "desert": 0.9,
                "snow": 0.8,
                "ice": 0.7,
                "water": 0.0
            },
            TransportationType.AUTOMOBILE: {
                "mountain": 0.3,
                "hills": 0.7,
                "forest": 0.5,
                "swamp": 0.2,
                "desert": 0.8,
                "snow": 0.4,
                "ice": 0.3,
                "water": 0.0
            },
            TransportationType.BOAT: {
                "mountain": 0.0,
                "hills": 0.0,
                "forest": 0.0,
                "swamp": 0.0,
                "desert": 0.0,
                "snow": 0.0,
                "ice": 0.0,
                "water": 1.0
            },
            TransportationType.SAILBOAT: {
                "mountain": 0.0,
                "hills": 0.0,
                "forest": 0.0,
                "swamp": 0.0,
                "desert": 0.0,
                "snow": 0.0,
                "ice": 0.0,
                "water": 1.0
            },
            TransportationType.STEAMSHIP: {
                "mountain": 0.0,
                "hills": 0.0,
                "forest": 0.0,
                "swamp": 0.0,
                "desert": 0.0,
                "snow": 0.0,
                "ice": 0.0,
                "water": 1.0
            },
            TransportationType.AIRPLANE: {
                "mountain": 1.0,
                "hills": 1.0,
                "forest": 1.0,
                "swamp": 1.0,
                "desert": 1.0,
                "snow": 1.0,
                "ice": 1.0,
                "water": 1.0
            }
        }
        
    def _initialize_weather_effects(self) -> Dict[TransportationType, Dict[str, float]]:
        """Initialize weather effects on transportation."""
        return {
            TransportationType.WALKING: {
                "rain": 0.8,
                "snow": 0.6,
                "storm": 0.4,
                "fog": 0.7,
                "wind": 0.9
            },
            TransportationType.HORSE: {
                "rain": 0.9,
                "snow": 0.7,
                "storm": 0.5,
                "fog": 0.8,
                "wind": 0.9
            },
            TransportationType.CART: {
                "rain": 0.7,
                "snow": 0.5,
                "storm": 0.3,
                "fog": 0.6,
                "wind": 0.8
            },
            TransportationType.RAILROAD: {
                "rain": 0.9,
                "snow": 0.8,
                "storm": 0.7,
                "fog": 0.8,
                "wind": 0.9
            },
            TransportationType.AUTOMOBILE: {
                "rain": 0.8,
                "snow": 0.6,
                "storm": 0.5,
                "fog": 0.7,
                "wind": 0.8
            },
            TransportationType.BOAT: {
                "rain": 0.9,
                "snow": 0.8,
                "storm": 0.4,
                "fog": 0.7,
                "wind": 0.6
            },
            TransportationType.SAILBOAT: {
                "rain": 0.9,
                "snow": 0.8,
                "storm": 0.3,
                "fog": 0.7,
                "wind": 0.5
            },
            TransportationType.STEAMSHIP: {
                "rain": 0.95,
                "snow": 0.9,
                "storm": 0.7,
                "fog": 0.8,
                "wind": 0.8
            },
            TransportationType.AIRPLANE: {
                "rain": 0.9,
                "snow": 0.7,
                "storm": 0.4,
                "fog": 0.6,
                "wind": 0.8
            }
        }
        
    def can_research(self, transport_type: TransportationType) -> bool:
        """Check if a transportation type can be researched."""
        if transport_type in self.researched_types:
            return False
            
        # Check if all prerequisites are researched
        prerequisites = self.technology_tree.get(transport_type, [])
        return all(prereq in self.researched_types for prereq in prerequisites)
        
    def start_research(self, transport_type: TransportationType):
        """Start researching a new transportation type."""
        if not self.can_research(transport_type):
            logger.warning(f"Cannot research {transport_type.value}: prerequisites not met")
            return
            
        self.current_research = transport_type
        self.research_progress = 0.0
        logger.info(f"Started researching {transport_type.value}")
        
    def update_research(self, research_points: float):
        """Update research progress."""
        if not self.current_research:
            return
            
        self.research_progress += research_points
        if self.research_progress >= 100.0:
            self.complete_research()
            
    def complete_research(self):
        """Complete current research and unlock new transportation type."""
        if not self.current_research:
            return
            
        self.researched_types.add(self.current_research)
        self.available_types.add(self.current_research)
        logger.info(f"Completed research on {self.current_research.value}")
        
        self.current_research = None
        self.research_progress = 0.0
        
    def calculate_travel_time(self, 
                            start: Tuple[float, float],
                            end: Tuple[float, float],
                            transport_type: TransportationType,
                            weather: str = "clear") -> timedelta:
        """Calculate travel time between two points."""
        # Calculate distance
        distance = self.world.calculate_distance(start, end)
        
        # Get base speed
        base_speed = self.travel_speeds.get(transport_type, 5.0)
        
        # Apply terrain penalties
        terrain_penalty = 1.0
        if transport_type in self.terrain_penalties:
            # Sample terrain along path
            terrain_types = self._sample_terrain_along_path(start, end)
            for terrain in terrain_types:
                penalty = self.terrain_penalties[transport_type].get(terrain, 1.0)
                terrain_penalty = min(terrain_penalty, penalty)
                
        # Apply weather effects
        weather_effect = 1.0
        if transport_type in self.weather_effects:
            weather_effect = self.weather_effects[transport_type].get(weather, 1.0)
            
        # Calculate final speed
        final_speed = base_speed * terrain_penalty * weather_effect
        
        # Calculate time
        hours = distance / final_speed
        return timedelta(hours=hours)
        
    def _sample_terrain_along_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[str]:
        """Sample terrain types along a path between two points."""
        # Simplified: just get terrain at start and end points
        start_terrain = self.world.terrain_system.get_terrain_at(*start)
        end_terrain = self.world.terrain_system.get_terrain_at(*end)
        
        return [start_terrain.value, end_terrain.value]
        
    def get_available_types(self) -> List[TransportationType]:
        """Get list of available transportation types."""
        return list(self.available_types)
        
    def get_researched_types(self) -> List[TransportationType]:
        """Get list of researched transportation types."""
        return list(self.researched_types)
        
    def get_current_research(self) -> Optional[Tuple[TransportationType, float]]:
        """Get current research progress."""
        if not self.current_research:
            return None
        return (self.current_research, self.research_progress) 