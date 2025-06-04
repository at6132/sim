from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import logging
from datetime import datetime, timedelta
from simulation.utils.logging_config import get_logger

logger = get_logger('TransportationSystem')

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
        self.logger = get_logger('TransportationSystem')
        self.logger.info("Initializing TransportationSystem...")
        self.roads = {}
        self.paths = {}
        self.ports = {}
        self.trade_routes = {}
        self.transport_networks = {
            "land": {"nodes": {}, "edges": {}},
            "water": {"nodes": {}, "edges": {}},
            "air": {"nodes": {}, "edges": {}}
        }
        self.initialize()
        
    def initialize(self):
        """Initialize the transportation system."""
        self.logger.info("Starting transportation system initialization...")
        
        try:
            # Initialize road network
            self.logger.info("Initializing road network...")
            self._initialize_paths()
            
            # Initialize water routes
            self.logger.info("Initializing water routes...")
            self._initialize_trade_routes()
            
            # Initialize air routes
            self.logger.info("Initializing air routes...")
            self._initialize_transport_networks()
            
            # Initialize ports
            self.logger.info("Setting up ports...")
            self._initialize_ports()
            
            # Initialize technology tree
            self.logger.info("Setting up transportation technology tree...")
            self.technology_tree = self._initialize_technology_tree()
            
            # Initialize travel speeds
            self.logger.info("Setting up travel speeds...")
            self.travel_speeds = self._initialize_travel_speeds()
            
            # Verify initialization
            if not self.verify_initialization():
                self.logger.error("Transportation system initialization verification failed")
                raise RuntimeError("Transportation system initialization verification failed")
            
            self.logger.info("Transportation system initialization complete")
            
        except Exception as e:
            self.logger.error(f"Error during transportation system initialization: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
        
    def verify_initialization(self) -> bool:
        """Verify that the transportation system is properly initialized."""
        self.logger.info("Verifying transportation system initialization...")
        
        try:
            # Check road network
            if not hasattr(self, 'roads') or not self.roads:
                self.logger.error("Roads not initialized")
                return False
                
            # Check water routes
            if not hasattr(self, 'trade_routes') or not self.trade_routes:
                self.logger.error("Trade routes not initialized")
                return False
                
            # Check air routes
            if not hasattr(self, 'transport_networks') or not self.transport_networks:
                self.logger.error("Transport networks not initialized")
                return False
                
            # Check technology tree
            if not hasattr(self, 'technology_tree') or not self.technology_tree:
                self.logger.error("Technology tree not initialized")
                return False
                
            # Check travel speeds
            if not hasattr(self, 'travel_speeds') or not self.travel_speeds:
                self.logger.error("Travel speeds not initialized")
                return False
                
            self.logger.info("Transportation system initialization verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during transportation system verification: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
        
    def _initialize_paths(self):
        """Initialize transportation paths between settlements."""
        self.logger.info("Initializing transportation paths...")
        
        # Get all settlements
        settlements = self.world.settlements
        
        # Create paths between nearby settlements
        for settlement_id, settlement in settlements.items():
            # Find nearest settlements
            nearest = self._find_nearest_settlements(settlement, settlements, max_distance=200.0)
            
            # Create paths to nearest settlements
            for target_id, distance in nearest:
                if self._is_valid_path(settlement, settlements[target_id]):
                    path_id = f"path_{settlement_id}_{target_id}"
                    self.paths[path_id] = {
                        "start": settlement_id,
                        "end": target_id,
                        "distance": distance,
                        "type": "land",
                        "status": "active",
                        "traffic": 0.0
                    }
                    self.logger.debug(f"Created path {path_id} between settlements {settlement_id} and {target_id}")
        
        self.logger.info(f"Created {len(self.paths)} transportation paths")
        
    def _find_nearest_settlements(self, settlement, max_distance: float) -> List[Dict]:
        """Find nearest settlements within max_distance."""
        nearest = []
        for other in self.world.settlements.values():
            if other.id != settlement.id:
                distance = self._calculate_distance(
                    (settlement.longitude, settlement.latitude),
                    (other.longitude, other.latitude)
                )
                if distance <= max_distance:
                    nearest.append(other)
        return nearest
        
    def _is_valid_path(self, start_settlement, end_settlement) -> bool:
        """Check if a path between settlements is valid (stays on land)."""
        # Get path points
        path_points = self._get_path_points(
            start_settlement.longitude, start_settlement.latitude,
            end_settlement.longitude, end_settlement.latitude
        )
        
        # Check if all points are on land
        for lon, lat in path_points:
            if self._is_on_water(lon, lat):
                return False
                
        return True
        
    def _get_path_points(self, start_lon: float, start_lat: float, end_lon: float, end_lat: float) -> List[Tuple[float, float]]:
        """Get points along a path between two coordinates."""
        points = []
        
        # Calculate number of points based on distance
        distance = self.world.get_distance(start_lon, start_lat, end_lon, end_lat)
        num_points = max(2, int(distance / 10.0))  # One point every 10km
        
        # Generate points
        for i in range(num_points):
            t = i / (num_points - 1)
            lon = start_lon + (end_lon - start_lon) * t
            lat = start_lat + (end_lat - start_lat) * t
            points.append((lon, lat))
            
        return points
        
    def _is_on_water(self, longitude: float, latitude: float) -> bool:
        """Check if a position is on water."""
        terrain = self.world.terrain.get_terrain_at(longitude, latitude)
        return terrain == "water"
        
    def _initialize_trade_routes(self):
        """Initialize trade routes between settlements."""
        self.logger.info("Initializing trade routes...")
        
        # Create trade routes between settlements
        for settlement in self.world.settlements.values():
            # Find nearest settlements for trade
            nearest_settlements = self._find_nearest_settlements(settlement, max_distance=200.0)
            
            for target in nearest_settlements:
                # Create trade route if it doesn't exist
                route_id = f"trade_{settlement.id}_{target.id}"
                if route_id not in self.trade_routes:
                    # Check if there's a valid path between settlements
                    path = self._find_land_path(
                        (settlement.longitude, settlement.latitude),
                        (target.longitude, target.latitude)
                    )
                    if path:
                        self.trade_routes[route_id] = {
                            "id": route_id,
                            "start": settlement.id,
                            "end": target.id,
                            "path": path,
                            "type": "land",
                            "status": "active",
                            "traffic": 0.0,
                            "goods": {}  # Will be populated with traded goods
                        }
                        self.logger.debug(f"Created trade route {route_id} between settlements {settlement.id} and {target.id}")
        
        self.logger.info(f"Created {len(self.trade_routes)} trade routes")
        
    def _initialize_transport_networks(self):
        """Initialize transport networks."""
        self.logger.info("Initializing transport networks...")
        
        # Initialize land network
        self.logger.info("Setting up land transport network...")
        self._initialize_land_network()
        self.logger.info("Land transport network initialized")
        
        # Initialize water network
        self.logger.info("Setting up water transport network...")
        self._initialize_water_network()
        self.logger.info("Water transport network initialized")
        
        # Initialize air network
        self.logger.info("Setting up air transport network...")
        self._initialize_air_network()
        self.logger.info("Air transport network initialized")
        
        self.logger.info("Transport networks initialization complete")
        
    def _initialize_land_network(self):
        """Initialize land transport network."""
        network = self.transport_networks["land"]
        
        # Add settlements as nodes
        for settlement_id, settlement in self.world.settlements.items():
            network["nodes"][settlement_id] = {
                "type": "settlement",
                "position": (settlement.longitude, settlement.latitude),
                "connections": []
            }
        
        # Add paths as edges
        for path_id, path in self.paths.items():
            start_id = path["start"]
            end_id = path["end"]
            
            # Add edge
            edge_id = f"edge_{start_id}_{end_id}"
            network["edges"][edge_id] = {
                "start": start_id,
                "end": end_id,
                "type": "path",
                "distance": path["distance"]
            }
            
            # Update node connections
            network["nodes"][start_id]["connections"].append(end_id)
            network["nodes"][end_id]["connections"].append(start_id)
            
    def _initialize_water_network(self):
        """Initialize water transport network."""
        network = self.transport_networks["water"]
        
        # Add ports as nodes
        for port_id, port in self.ports.items():
            network["nodes"][port_id] = {
                "type": "port",
                "position": (port["longitude"], port["latitude"]),
                "connections": []
            }
        
        # Add shipping routes as edges
        for route_id, route in self.trade_routes.items():
            if route["type"] == "water":
                start_id = route["start"]
                end_id = route["end"]
                
                # Add edge
                edge_id = f"edge_{start_id}_{end_id}"
                network["edges"][edge_id] = {
                    "start": start_id,
                    "end": end_id,
                    "type": "shipping",
                    "distance": self.world.get_distance(
                        self.ports[start_id]["longitude"], self.ports[start_id]["latitude"],
                        self.ports[end_id]["longitude"], self.ports[end_id]["latitude"]
                    )
                }
                
                # Update node connections
                network["nodes"][start_id]["connections"].append(end_id)
                network["nodes"][end_id]["connections"].append(start_id)
                
    def _initialize_air_network(self):
        """Initialize air transport network."""
        network = self.transport_networks["air"]
        
        # Add airports as nodes
        for settlement_id, settlement in self.world.settlements.items():
            if settlement.population >= 1000:  # Only settlements with sufficient population
                network["nodes"][settlement_id] = {
                    "type": "airport",
                    "position": (settlement.longitude, settlement.latitude),
                    "connections": []
                }
        
        # Add air routes as edges
        for start_id, start_node in network["nodes"].items():
            for end_id, end_node in network["nodes"].items():
                if start_id != end_id:
                    distance = self.world.get_distance(
                        start_node["position"][0], start_node["position"][1],
                        end_node["position"][0], end_node["position"][1]
                    )
                    
                    if distance <= 1000.0:  # Only connect airports within 1000km
                        # Add edge
                        edge_id = f"edge_{start_id}_{end_id}"
                        network["edges"][edge_id] = {
                            "start": start_id,
                            "end": end_id,
                            "type": "air_route",
                            "distance": distance
                        }
                        
                        # Update node connections
                        network["nodes"][start_id]["connections"].append(end_id)
                        network["nodes"][end_id]["connections"].append(start_id)
                        
    def update(self, time_delta: float):
        """Update transportation system state."""
        # Update path conditions
        self._update_paths(time_delta)
        
        # Update trade routes
        self._update_trade_routes(time_delta)
        
        # Update transport networks
        self._update_transport_networks(time_delta)
        
    def _update_paths(self, time_delta: float):
        """Update path conditions and traffic."""
        for path_id, path in self.paths.items():
            # Update traffic
            path["traffic"] = max(0.0, path["traffic"] - 0.1 * time_delta)
            
            # Check path conditions
            if not self._is_valid_path(
                self.world.settlements[path["start"]],
                self.world.settlements[path["end"]]
            ):
                path["status"] = "blocked"
            else:
                path["status"] = "active"
                
    def _update_trade_routes(self, time_delta: float):
        """Update trade routes and traffic."""
        for route_id, route in self.trade_routes.items():
            # Update traffic
            route["traffic"] = max(0.0, route["traffic"] - 0.1 * time_delta)
            
            # Check route conditions
            if not self._is_valid_path(
                self.world.settlements[route["start"]],
                self.world.settlements[route["end"]]
            ):
                route["status"] = "blocked"
            else:
                route["status"] = "active"
                
    def _update_transport_networks(self, time_delta: float):
        """Update transport networks."""
        # Update land network
        self._update_land_network(time_delta)
        
        # Update water network
        self._update_water_network(time_delta)
        
        # Update air network
        self._update_air_network(time_delta)
        
    def _update_land_network(self, time_delta: float):
        """Update land transport network."""
        network = self.transport_networks["land"]
        
        # Update node states
        for node_id, node in network["nodes"].items():
            settlement = self.world.settlements[node_id]
            node["population"] = settlement.population
            node["status"] = "active" if settlement.population > 0 else "inactive"
            
        # Update edge states
        for edge_id, edge in network["edges"].items():
            path = self.paths.get(f"path_{edge['start']}_{edge['end']}")
            if path:
                edge["status"] = path["status"]
                edge["traffic"] = path["traffic"]
                
    def _update_water_network(self, time_delta: float):
        """Update water transport network."""
        network = self.transport_networks["water"]
        
        # Update node states
        for node_id, node in network["nodes"].items():
            port = self.ports[node_id]
            node["status"] = "active" if port["status"] == "active" else "inactive"
            
        # Update edge states
        for edge_id, edge in network["edges"].items():
            route = self.trade_routes.get(f"trade_{edge['start']}_{edge['end']}")
            if route:
                edge["status"] = route["status"]
                edge["traffic"] = route["traffic"]
                
    def _update_air_network(self, time_delta: float):
        """Update air transport network."""
        network = self.transport_networks["air"]
        
        # Update node states
        for node_id, node in network["nodes"].items():
            settlement = self.world.settlements[node_id]
            node["status"] = "active" if settlement.population >= 1000 else "inactive"
            
        # Update edge states
        for edge_id, edge in network["edges"].items():
            # Check if both airports are active
            start_node = network["nodes"][edge["start"]]
            end_node = network["nodes"][edge["end"]]
            
            if start_node["status"] == "active" and end_node["status"] == "active":
                edge["status"] = "active"
            else:
                edge["status"] = "inactive"
    
    def get_state(self) -> Dict:
        """Get current transportation system state."""
        return {
            "paths": self.paths,
            "trade_routes": self.trade_routes,
            "transport_networks": self.transport_networks
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
            self.logger.warning(f"Cannot research {transport_type.value}: prerequisites not met")
            return
            
        self.current_research = transport_type
        self.research_progress = 0.0
        self.logger.info(f"Started researching {transport_type.value}")
        
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
        self.logger.info(f"Completed research on {self.current_research.value}")
        
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

    def _initialize_ports(self):
        """Initialize basic port network."""
        # Create ports along coastlines
        for lon in range(-180, 181, 5):  # Every 5 degrees
            for lat in range(-90, 91, 5):
                terrain = self.world.terrain.get_terrain_at(lon, lat)
                if terrain == 'water':
                    # Check for nearby land
                    has_land = False
                    for dlon in [-1, 0, 1]:
                        for dlat in [-1, 0, 1]:
                            if self.world.terrain.get_terrain_at(lon + dlon, lat + dlat) != 'water':
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

    def _initialize_paths(self):
        """Initialize transportation paths between settlements."""
        self.logger.info("Initializing transportation paths...")
        
        # Create paths between settlements
        for settlement in self.world.settlements.values():
            # Find nearest settlements
            nearest_settlements = self._find_nearest_settlements(settlement, max_distance=100.0)
            
            for target in nearest_settlements:
                # Create path if it doesn't exist
                path_id = f"path_{settlement.id}_{target.id}"
                if path_id not in self.paths:
                    path = self._create_path(settlement, target)
                    if path:
                        self.paths[path_id] = path
                        
        self.logger.info("Transportation paths initialization complete")
        
    def _find_nearest_settlements(self, settlement, max_distance: float) -> List[Dict]:
        """Find nearest settlements within max_distance."""
        nearest = []
        for other in self.world.settlements.values():
            if other.id != settlement.id:
                distance = self._calculate_distance(
                    (settlement.longitude, settlement.latitude),
                    (other.longitude, other.latitude)
                )
                if distance <= max_distance:
                    nearest.append(other)
        return nearest
        
    def _create_path(self, start: Dict, end: Dict) -> Optional[Dict]:
        """Create a path between two settlements."""
        # Find path that stays on land
        path = self._find_land_path(
            (start.longitude, start.latitude),
            (end.longitude, end.latitude)
        )
        if not path:
            return None
            
        return {
            "id": f"path_{start.id}_{end.id}",
            "start": start.id,
            "end": end.id,
            "points": path,
            "type": "land",
            "status": "active",
            "traffic": 0.0
        }
        
    def _find_land_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """Find a path between two points that stays on land."""
        # Simple straight line path for now
        # TODO: Implement proper pathfinding
        path = []
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            lon = start[0] + (end[0] - start[0]) * t
            lat = start[1] + (end[1] - start[1]) * t
            if self._is_on_water(lon, lat):
                return None
            path.append((lon, lat))
        return path
        
    def _is_on_water(self, longitude: float, latitude: float) -> bool:
        """Check if a position is on water."""
        terrain = self.world.terrain.get_terrain_at(longitude, latitude)
        return terrain == "water"

    def _initialize_trade_routes(self):
        """Initialize trade routes between settlements."""
        self.logger.info("Initializing trade routes...")
        
        # Create trade routes between settlements
        for settlement in self.world.settlements.values():
            # Find nearest settlements for trade
            nearest_settlements = self._find_nearest_settlements(settlement, max_distance=200.0)
            
            for target in nearest_settlements:
                # Create trade route if it doesn't exist
                route_id = f"trade_{settlement.id}_{target.id}"
                if route_id not in self.trade_routes:
                    # Check if there's a valid path between settlements
                    path = self._find_land_path(
                        (settlement.longitude, settlement.latitude),
                        (target.longitude, target.latitude)
                    )
                    if path:
                        self.trade_routes[route_id] = {
                            "id": route_id,
                            "start": settlement.id,
                            "end": target.id,
                            "path": path,
                            "type": "land",
                            "status": "active",
                            "traffic": 0.0,
                            "goods": {}  # Will be populated with traded goods
                        }
                        
        self.logger.info("Trade routes initialization complete") 

    def _initialize_transport_networks(self):
        """Initialize transport networks connecting different transportation systems."""
        self.logger.info("Initializing transport networks...")
        
        # Initialize networks for different transport types
        self.transport_networks = {
            'land': {
                'roads': self.roads,
                'paths': self.paths,
                'connections': {}
            },
            'water': {
                'ports': self.ports,
                'routes': {},
                'connections': {}
            },
            'air': {
                'airports': {},
                'routes': {},
                'connections': {}
            }
        }
        
        # Connect land networks
        for road_id, road in self.roads.items():
            start_pos = road['start']
            end_pos = road['end']
            
            # Add connections to transport network
            if start_pos not in self.transport_networks['land']['connections']:
                self.transport_networks['land']['connections'][start_pos] = []
            if end_pos not in self.transport_networks['land']['connections']:
                self.transport_networks['land']['connections'][end_pos] = []
                
            self.transport_networks['land']['connections'][start_pos].append(end_pos)
            self.transport_networks['land']['connections'][end_pos].append(start_pos)
            
        # Connect water networks
        for port_pos, port in self.ports.items():
            if port_pos not in self.transport_networks['water']['connections']:
                self.transport_networks['water']['connections'][port_pos] = []
                
            for connection in port['connections']:
                self.transport_networks['water']['connections'][port_pos].append(connection)
                
        self.logger.info("Transport networks initialization complete") 

    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate the distance between two points."""
        return self.world.get_distance(point1[0], point1[1], point2[0], point2[1]) 