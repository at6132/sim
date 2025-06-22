from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import logging
from datetime import datetime, timedelta
from simulation.utils.logging_config import get_logger
import traceback

logger = get_logger(__name__)

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
        self.logger = get_logger(__name__)
        
        # Initialize transportation components
        self.roads = {}  # road_id -> road_data
        self.paths = {}  # path_id -> path_data
        self.vehicles = {}  # vehicle_id -> vehicle_data
        self.transport_routes = {}  # route_id -> route_data
        self.trade_routes = {}  # route_id -> route_data
        self.ports = {}  # port_id -> port_data
        
        # Initialize transport networks
        self.transport_networks = {
            "land": {
                "roads": {},
                "paths": {},
                "nodes": {},
                "edges": {},
                "connections": {}
            },
            "water": {
                "ports": {},
                "routes": {},
                "nodes": {},
                "edges": {},
                "connections": {}
            },
            "air": {
                "airports": {},
                "routes": {},
                "nodes": {},
                "edges": {},
                "connections": {}
            }
        }
        
        self.logger.info("Transportation system initialized")
    
    def initialize_transportation(self):
        """Initialize the transportation system with basic structures."""
        self.logger.info("Initializing transportation system...")
        
        # Initialize roads
        self._initialize_roads()
        
        # Initialize paths
        self._initialize_paths()
        
        # Initialize vehicles
        self._initialize_vehicles()
        
        # Initialize transport routes
        self._initialize_transport_routes()
        
        self.logger.info("Transportation system initialization complete")
    
    def _initialize_roads(self):
        """Initialize basic roads."""
        self.logger.info("Initializing roads...")
        
        self.roads = {
            'road_1': {
                'name': 'Northern Trade Route',
                'start': (0, 0),
                'end': (2, 2),
                'type': 'dirt_road',
                'condition': 0.8,
                'traffic': 0.3
            },
            'road_2': {
                'name': 'River Road',
                'start': (2, 2),
                'end': (4, 4),
                'type': 'stone_road',
                'condition': 0.9,
                'traffic': 0.5
            }
        }
    
    def _initialize_paths(self):
        """Initialize basic paths."""
        self.logger.info("Initializing paths...")
        
        self.paths = {
            'path_1': {
                'name': 'Hunting Trail',
                'start': (0, 0),
                'end': (1, 1),
                'type': 'footpath',
                'condition': 0.6,
                'usage': 0.4
            },
            'path_2': {
                'name': 'Gathering Path',
                'start': (2, 2),
                'end': (3, 3),
                'type': 'footpath',
                'condition': 0.7,
                'usage': 0.3
            }
        }
    
    def _initialize_vehicles(self):
        """Initialize basic vehicles."""
        self.logger.info("Initializing vehicles...")
        
        self.vehicles = {
            'vehicle_1': {
                'name': 'Trade Cart',
                'type': 'cart',
                'capacity': 100,
                'speed': 5,
                'condition': 0.8,
                'location': (0, 0)
            },
            'vehicle_2': {
                'name': 'River Boat',
                'type': 'boat',
                'capacity': 200,
                'speed': 8,
                'condition': 0.9,
                'location': (2, 2)
            }
        }
    
    def _initialize_transport_routes(self):
        """Initialize basic transport routes."""
        self.logger.info("Initializing transport routes...")
        
        self.transport_routes = {
            'route_1': {
                'name': 'Northern Trade Route',
                'type': 'land',
                'stops': [(0, 0), (1, 1), (2, 2)],
                'vehicle': 'vehicle_1',
                'frequency': 1.0,  # trips per day
                'cargo': {'goods': 50, 'passengers': 10}
            },
            'route_2': {
                'name': 'River Trade Route',
                'type': 'water',
                'stops': [(2, 2), (3, 3), (4, 4)],
                'vehicle': 'vehicle_2',
                'frequency': 2.0,  # trips per day
                'cargo': {'goods': 100, 'passengers': 20}
            }
        }
    
    def update(self, time_delta: float):
        """Update transportation state."""
        self.logger.debug(f"Updating transportation with time delta: {time_delta}")
        
        # Update roads
        self._update_roads(time_delta)
        
        # Update paths
        self._update_paths(time_delta)
        
        # Update vehicles
        self._update_vehicles(time_delta)
        
        # Update transport routes
        self._update_transport_routes(time_delta)
    
    def _update_roads(self, time_delta: float):
        """Update road states."""
        for road_id, road in self.roads.items():
            # Update condition
            wear_rate = 0.001 * time_delta * road['traffic']
            road['condition'] = max(0.0, road['condition'] - wear_rate)
            
            # Update traffic
            traffic_change = 0.002 * time_delta
            road['traffic'] = min(1.0, road['traffic'] + traffic_change)
    
    def _update_paths(self, time_delta: float):
        """Update path states."""
        for path_id, path in self.paths.items():
            # Update condition
            wear_rate = 0.002 * time_delta * path['usage']
            path['condition'] = max(0.0, path['condition'] - wear_rate)
            
            # Update usage
            usage_change = 0.001 * time_delta
            path['usage'] = min(1.0, path['usage'] + usage_change)
    
    def _update_vehicles(self, time_delta: float):
        """Update vehicle states."""
        for vehicle_id, vehicle in self.vehicles.items():
            # Update condition
            wear_rate = 0.001 * time_delta
            vehicle['condition'] = max(0.0, vehicle['condition'] - wear_rate)
            
            # Update location based on assigned route
            for route in self.transport_routes.values():
                if route['vehicle'] == vehicle_id:
                    self._update_vehicle_location(vehicle, route, time_delta)
    
    def _update_vehicle_location(self, vehicle: Dict, route: Dict, time_delta: float):
        """Update vehicle location along its route."""
        if not route['stops']:
            return
        
        # Calculate progress along route
        progress = (time_delta * route['frequency']) % 1.0
        
        # Get current and next stop
        current_stop_idx = int(progress * (len(route['stops']) - 1))
        next_stop_idx = min(current_stop_idx + 1, len(route['stops']) - 1)
        
        # Interpolate position between stops
        current_stop = route['stops'][current_stop_idx]
        next_stop = route['stops'][next_stop_idx]
        
        segment_progress = (progress * (len(route['stops']) - 1)) % 1.0
        vehicle['location'] = (
            current_stop[0] + (next_stop[0] - current_stop[0]) * segment_progress,
            current_stop[1] + (next_stop[1] - current_stop[1]) * segment_progress
        )
    
    def _update_transport_routes(self, time_delta: float):
        """Update transport route states."""
        for route_id, route in self.transport_routes.items():
            # Update cargo
            for cargo_type, amount in route['cargo'].items():
                if cargo_type == 'goods':
                    route['cargo'][cargo_type] *= (1 - 0.05 * time_delta)
                else:  # passengers
                    route['cargo'][cargo_type] *= (1 - 0.02 * time_delta)
            
            # Update frequency based on demand
            demand_change = 0.001 * time_delta
            route['frequency'] = min(5.0, route['frequency'] + demand_change)
    
    def _update_trade_routes(self, time_delta: float):
        """Update trade routes."""
        for route_id, route in self.transport_routes.items():
            # Update cargo
            if 'cargo' in route:
                for cargo_type, amount in route['cargo'].items():
                    # Simulate cargo movement
                    route['cargo'][cargo_type] = max(0, amount - time_delta * 0.1)
            
            # Update vehicle location
            if 'vehicle' in route and route['vehicle'] in self.vehicles:
                self._update_vehicle_location(self.vehicles[route['vehicle']], route, time_delta)
    
    def get_state(self) -> Dict:
        """Get current transportation system state."""
        def convert_coords_to_str(coords):
            if isinstance(coords, tuple):
                return f"{coords[0]},{coords[1]}"
            return coords

        def convert_dict(d):
            if isinstance(d, dict):
                return {convert_coords_to_str(k): convert_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return convert_list(d)
            elif isinstance(d, tuple):
                return convert_coords_to_str(d)
            return d

        def convert_list(l):
            if isinstance(l, list):
                return [convert_dict(item) for item in l]
            return l

        def convert_network(network):
            if not isinstance(network, dict):
                return network
            return {
                'roads': convert_dict(network.get('roads', {})),
                'paths': convert_dict(network.get('paths', {})),
                'nodes': convert_dict(network.get('nodes', {})),
                'edges': convert_dict(network.get('edges', {})),
                'connections': convert_dict(network.get('connections', {}))
            }

        try:
            return {
                'roads': convert_dict(self.roads),
                'paths': convert_dict(self.paths),
                'vehicles': convert_dict(self.vehicles),
                'transport_routes': convert_dict(self.transport_routes),
                'trade_routes': convert_dict(self.trade_routes),
                'ports': convert_dict(self.ports),
                'transport_networks': {
                    'land': convert_network(self.transport_networks.get('land', {})),
                    'water': convert_network(self.transport_networks.get('water', {})),
                    'air': convert_network(self.transport_networks.get('air', {}))
                }
            }
        except Exception as e:
            logger.error(f"Error getting transportation state: {e}")
            logger.error(traceback.format_exc())
            return {'error': str(e)}

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
        
        for settlement_id, settlement in self.world.settlements.items():
            lon, lat = settlement.get("location", (
                settlement.get("longitude"), settlement.get("latitude")
            ))
            nearest_settlements = self._find_nearest_settlements(
                settlement_id, lon, lat, max_distance=100.0
            )

            for target_id, (t_lon, t_lat) in nearest_settlements:
                path_id = f"path_{settlement_id}_{target_id}"
                if path_id not in self.paths:
                    path = self._create_path(
                        settlement_id, lon, lat, target_id, t_lon, t_lat
                    )
                    if path:
                        self.paths[path_id] = path
                        
        self.logger.info("Transportation paths initialization complete")
        
    def _find_nearest_settlements(self, sid: str, lon: float, lat: float, max_distance: float) -> List[Tuple[str, Tuple[float, float]]]:
        """Find nearest settlements within max_distance."""
        nearest = []
        for other_id, other in self.world.settlements.items():
            if other_id != sid:
                o_lon, o_lat = other.get("location", (
                    other.get("longitude"), other.get("latitude")
                ))
                distance = self._calculate_distance((lon, lat), (o_lon, o_lat))
                if distance <= max_distance:
                    nearest.append((other_id, (o_lon, o_lat)))
        return nearest
        
    def _create_path(self, start_id: str, start_lon: float, start_lat: float, end_id: str, end_lon: float, end_lat: float) -> Optional[Dict]:
        """Create a path between two settlements."""
        path = self._find_land_path((start_lon, start_lat), (end_lon, end_lat))
        if not path:
            return None
            
        return {
            "id": f"path_{start_id}_{end_id}",
            "start": start_id,
            "end": end_id,
            "points": path,
            "type": "land",
            "status": "active",
            "traffic": 0.0,
        }

    def _calculate_distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Wrapper around world's distance calculation."""
        return self.world.get_distance(a[0], a[1], b[0], b[1])
        
    def _find_land_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """Find an optimal land path between two points."""
        # First try to find an existing road or path
        road_path = self._find_road_path(start, end)
        if road_path:
            return road_path
            
        # If no road exists, use A* with terrain considerations
        return self._find_path(start, end, TransportationType.WALKING)
        
    def _find_road_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """Find a path using existing roads."""
        # Find nearest road segments to start and end points
        start_road = self._find_nearest_road(start)
        end_road = self._find_nearest_road(end)
        
        if not start_road or not end_road:
                return None
            
        # If start and end are on the same road, use direct path
        if start_road == end_road:
            return [start, end]
            
        # Find path through road network
        road_path = self._find_path_through_roads(start_road, end_road)
        if not road_path:
            return None
            
        # Add start and end points to path
        return [start] + road_path + [end]
        
    def _find_nearest_road(self, point: Tuple[float, float]) -> Optional[Dict]:
        """Find the nearest road segment to a point."""
        nearest_road = None
        min_distance = float('inf')
        
        for road_id, road in self.roads.items():
            # Calculate distance to road segment
            distance = self._distance_to_road_segment(point, road)
            if distance < min_distance:
                min_distance = distance
                nearest_road = road
                
        return nearest_road
        
    def _distance_to_road_segment(self, point: Tuple[float, float], road: Dict) -> float:
        """Calculate distance from point to road segment."""
        start = road['start']
        end = road['end']
        
        # Calculate perpendicular distance to line segment
        x, y = point
        x1, y1 = start
        x2, y2 = end
        
        # Vector from start to end
        dx = x2 - x1
        dy = y2 - y1
        
        # Vector from start to point
        px = x - x1
        py = y - y1
        
        # Project point onto road segment
        t = max(0, min(1, (px * dx + py * dy) / (dx * dx + dy * dy)))
        
        # Calculate closest point on road
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Calculate distance to closest point
        return self._calculate_distance(point, (closest_x, closest_y))
        
    def _find_path_through_roads(self, start_road: Dict, end_road: Dict) -> Optional[List[Tuple[float, float]]]:
        """Find a path through the road network."""
        # Use A* to find path through road network
        open_set = {start_road}
        closed_set = set()
        
        came_from = {}
        g_score = {start_road: 0}
        f_score = {start_road: self._heuristic(start_road, end_road)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end_road:
                return self._reconstruct_road_path(came_from, current)
                
            open_set.remove(current)
            closed_set.add(current)
            
            # Get connected roads
            for neighbor in self._get_connected_roads(current):
                if neighbor in closed_set:
                    continue
                    
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + self._get_road_distance(current, neighbor)
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue
                    
                # This path is the best so far
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, end_road)
                
        return None
        
    def _get_connected_roads(self, road: Dict) -> List[Dict]:
        """Get roads connected to the given road."""
        connected = []
        road_end = road['end']
        
        for other_road in self.roads.values():
            if other_road == road:
                continue
                
            # Check if roads are connected
            if (road_end == other_road['start'] or 
                road_end == other_road['end'] or
                road['start'] == other_road['start'] or
                road['start'] == other_road['end']):
                connected.append(other_road)
                
        return connected
        
    def _get_road_distance(self, road1: Dict, road2: Dict) -> float:
        """Calculate distance between two roads."""
        # Use the distance between their closest points
        return self._calculate_distance(road1['end'], road2['start'])
        
    def _reconstruct_road_path(self, came_from: Dict[Dict, Dict], current: Dict) -> List[Tuple[float, float]]:
        """Reconstruct path through road network."""
        path = []
        while current in came_from:
            path.append(current['end'])
            current = came_from[current]
        path.append(current['start'])
        path.reverse()
        return path
        
    def _find_path(self, start: Tuple[float, float], end: Tuple[float, float], transport_type: TransportationType) -> Optional[List[Tuple[float, float]]]:
        """Find a path between two points using A* pathfinding."""
        if not self._is_valid_path(start, end):
            return None
            
        # Initialize open and closed sets
        open_set = {start}
        closed_set = set()
        
        # Initialize path tracking
        came_from = {}
        g_score = {start: 0}  # Cost from start to current
        f_score = {start: self._heuristic(start, end)}  # Estimated total cost
        
        while open_set:
            # Get node with lowest f_score
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end:
                return self._reconstruct_path(came_from, current)
                
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            for neighbor in self._get_neighbors(current, transport_type):
                if neighbor in closed_set:
                    continue
                    
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + self._get_distance(current, neighbor)
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue
                    
                # This path is the best so far
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, end)
                
        return None  # No path found
        
    def _heuristic(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Calculate heuristic (straight-line distance) between two points."""
        return self._calculate_distance(a, b)
        
    def _get_neighbors(self, point: Tuple[float, float], transport_type: TransportationType) -> List[Tuple[float, float]]:
        """Get valid neighboring points based on transportation type."""
        lon, lat = point
        neighbors = []
        
        # Define movement directions (8-way for land, 4-way for water)
        if transport_type in [TransportationType.WALKING, TransportationType.RUNNING, 
                            TransportationType.HORSE, TransportationType.CART, 
                            TransportationType.WAGON, TransportationType.CARRIAGE,
                            TransportationType.RAILROAD, TransportationType.AUTOMOBILE,
                            TransportationType.TRUCK, TransportationType.BUS,
                            TransportationType.MOTORCYCLE, TransportationType.BICYCLE]:
            # 8-way movement for land vehicles
            directions = [
                (0.1, 0), (0.1, 0.1), (0, 0.1), (-0.1, 0.1),
                (-0.1, 0), (-0.1, -0.1), (0, -0.1), (0.1, -0.1)
            ]
        else:
            # 4-way movement for water and air vehicles
            directions = [(0.1, 0), (0, 0.1), (-0.1, 0), (0, -0.1)]
            
        for dlon, dlat in directions:
            new_lon = lon + dlon
            new_lat = lat + dlat
            
            # Check if new point is valid
            if self._is_valid_point((new_lon, new_lat), transport_type):
                neighbors.append((new_lon, new_lat))
                
        return neighbors
        
    def _is_valid_point(self, point: Tuple[float, float], transport_type: TransportationType) -> bool:
        """Check if a point is valid for the given transportation type."""
        lon, lat = point
        
        # Check world bounds
        if not self.world.is_valid_position(lon, lat):
            return False
            
        # Check terrain type
        terrain = self.world.get_terrain_at(lon, lat)
        
        if transport_type in [TransportationType.RAFT, TransportationType.CANOE,
                            TransportationType.BOAT, TransportationType.SAILBOAT,
                            TransportationType.GALLEY, TransportationType.CARAVEL,
                            TransportationType.GALLEON, TransportationType.STEAMSHIP,
                            TransportationType.MOTORBOAT, TransportationType.YACHT,
                            TransportationType.CRUISE_SHIP, TransportationType.CARGO_SHIP,
                            TransportationType.TANKER, TransportationType.SUBMARINE]:
            # Water vehicles can only move on water
            return terrain.is_water()
            
        elif transport_type in [TransportationType.BALLOON, TransportationType.AIRSHIP,
                              TransportationType.GLIDER, TransportationType.AIRPLANE,
                              TransportationType.HELICOPTER, TransportationType.JET,
                              TransportationType.SPACECRAFT]:
            # Air vehicles can move anywhere
            return True
            
        else:
            # Land vehicles can only move on land
            return not terrain.is_water()
            
    def _reconstruct_path(self, came_from: Dict[Tuple[float, float], Tuple[float, float]], 
                         current: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Reconstruct path from came_from dictionary."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
        
    def get_route(self, start_lon: float, start_lat: float, end_lon: float, end_lat: float) -> Optional[Dict]:
        """Get a route between two points."""
        start = (start_lon, start_lat)
        end = (end_lon, end_lat)
        
        # Try different transportation types in order of preference
        transport_types = [
            TransportationType.WALKING,  # Most basic
            TransportationType.HORSE,    # Basic land transport
            TransportationType.CART,     # Basic cargo transport
            TransportationType.BOAT,     # Basic water transport
            TransportationType.AIRPLANE  # Advanced transport
        ]
        
        for transport_type in transport_types:
            path = self._find_path(start, end, transport_type)
            if path:
                return {
                    'type': transport_type,
                    'path': path,
                    'distance': self._calculate_path_distance(path),
                    'estimated_time': self.calculate_travel_time(start, end, transport_type)
                }
                
        return None
        
    def _calculate_path_distance(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total distance of a path."""
        total_distance = 0.0
        for i in range(len(path) - 1):
            total_distance += self._calculate_distance(path[i], path[i + 1])
        return total_distance 