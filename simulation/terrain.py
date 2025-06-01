from typing import Dict, Tuple, Optional, List
from enum import Enum
import numpy as np
import math
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class TerrainType(Enum):
    # Ocean Types
    DEEP_OCEAN = "deep_ocean"  # > 2000m
    CONTINENTAL_SHELF = "continental_shelf"  # 0-200m
    CONTINENTAL_SLOPE = "continental_slope"  # 200-2000m
    OCEAN_TRENCH = "ocean_trench"  # > 6000m
    CORAL_REEF = "coral_reef"
    SEAMOUNT = "seamount"
    ABYSSAL_PLAIN = "abyssal_plain"
    
    # Coastal Types
    BEACH = "beach"
    CLIFF = "cliff"
    COASTAL_DUNES = "coastal_dunes"
    ESTUARY = "estuary"
    DELTA = "delta"
    MANGROVE = "mangrove"
    SALT_MARSH = "salt_marsh"
    TIDAL_FLAT = "tidal_flat"
    
    # Land Types
    DESERT = "desert"
    SAVANNA = "savanna"
    TROPICAL_RAINFOREST = "tropical_rainforest"
    GRASSLAND = "grassland"
    WOODLAND = "woodland"
    FOREST = "forest"
    RAINFOREST = "rainforest"
    SWAMP = "swamp"
    MARSH = "marsh"
    TUNDRA = "tundra"
    TAIGA = "taiga"
    ALPINE = "alpine"
    MOUNTAIN = "mountain"
    HILLS = "hills"
    VALLEY = "valley"
    RIVER = "river"
    LAKE = "lake"
    GLACIER = "glacier"
    VOLCANO = "volcano"
    ISLAND = "island"
    ARCHIPELAGO = "archipelago"
    CANYON = "canyon"
    PLATEAU = "plateau"
    MESA = "mesa"
    BUTTE = "butte"
    DUNES = "dunes"
    OASIS = "oasis"
    WETLAND = "wetland"
    BOG = "bog"
    FEN = "fen"
    HEATH = "heath"
    MOOR = "moor"
    STEPPE = "steppe"
    PRAIRIE = "prairie"
    CHAPARRAL = "chaparral"
    SCRUBLAND = "scrubland"
    BADLANDS = "badlands"
    SALT_FLAT = "salt_flat"

class OceanCurrent:
    def __init__(self, name: str, direction: Tuple[float, float], speed: float, temperature: float):
        self.name = name
        self.direction = direction  # (dx, dy) normalized vector
        self.speed = speed  # km/h
        self.temperature = temperature  # Celsius

class TerrainSystem:
    def __init__(self, world):
        self.world = world
        self.terrain_data = {}  # (longitude, latitude) -> Dict
        self.elevation_data = {}  # (longitude, latitude) -> float
        self.resource_data = {}  # (longitude, latitude) -> Dict
        self.ocean_currents = {}  # (longitude, latitude) -> OceanCurrent
        self.tidal_ranges = {}  # (longitude, latitude) -> float
        self.seasonal_factors = {}  # (longitude, latitude) -> Dict
        
        # Initialize terrain
        self._initialize_basic_terrain()
        self._initialize_elevation()
        self._initialize_resources()
        self._initialize_ocean_systems()
        
    def _initialize_basic_terrain(self):
        """Initialize basic terrain data."""
        logger.info("Initializing basic terrain...")
        
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                terrain_type = self._generate_terrain_type(lon, lat)
                self.terrain_data[(lon, lat)] = {
                    "type": terrain_type,
                    "elevation": self._generate_elevation(lon, lat),
                    "resources": self._generate_resources(lon, lat)
                }
                
        logger.info("Basic terrain initialization complete")
        
    def _initialize_elevation(self):
        """Initialize elevation data."""
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                elevation = self._generate_elevation(lon, lat)
                self.elevation_data[(lon, lat)] = elevation
        
    def _initialize_resources(self):
        """Initialize resource data."""
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                resources = self._generate_resources(lon, lat)
                self.resource_data[(lon, lat)] = resources
        
    def _initialize_ocean_systems(self):
        """Initialize ocean systems."""
        # Major ocean currents
        currents = [
            # Pacific Ocean
            {"name": "Kuroshio Current", "start": (130, 30), "end": (150, 40), "speed": 5.0, "temp": 20},
            {"name": "California Current", "start": (-130, 40), "end": (-120, 30), "speed": 2.0, "temp": 15},
            {"name": "Peru Current", "start": (-80, -10), "end": (-70, -20), "speed": 1.0, "temp": 18},
            # Atlantic Ocean
            {"name": "Gulf Stream", "start": (-80, 25), "end": (-50, 40), "speed": 6.0, "temp": 25},
            {"name": "Canary Current", "start": (-20, 30), "end": (-10, 20), "speed": 1.0, "temp": 18},
            {"name": "Benguela Current", "start": (10, -30), "end": (20, -20), "speed": 1.0, "temp": 16},
            # Indian Ocean
            {"name": "Agulhas Current", "start": (30, -35), "end": (40, -25), "speed": 4.0, "temp": 22},
            {"name": "West Australian Current", "start": (110, -30), "end": (120, -20), "speed": 1.0, "temp": 18},
        ]
        
        # Initialize currents
        for current in currents:
            self._initialize_current(current)
            
        # Initialize tidal data
        self._initialize_tides()
        
        # Initialize salinity and oxygen data
        self._initialize_salinity()
        self._initialize_oxygen()
        
    def _generate_terrain_type(self, lon: float, lat: float) -> str:
        """Generate terrain type based on coordinates."""
        # Base terrain on latitude (climate zones)
        if abs(lat) > 60:  # Polar regions
            return 'tundra'
        elif abs(lat) > 30:  # Temperate regions
            if random.random() < 0.3:
                return 'forest'
            elif random.random() < 0.5:
                return 'grassland'
            else:
                return 'land'
        else:  # Tropical regions
            if random.random() < 0.4:
                return 'desert'
            elif random.random() < 0.6:
                return 'forest'
            else:
                return 'grassland'
    
    def _generate_elevation(self, lon: float, lat: float) -> float:
        """Generate elevation for a coordinate."""
        # Base elevation on terrain type
        terrain = self.terrain_data.get((lon, lat), 'land')
        if terrain == 'mountain':
            return random.uniform(1000, 5000)
        elif terrain == 'land':
            return random.uniform(0, 1000)
        else:
            return random.uniform(-1000, 0)  # Below sea level
    
    def _generate_resources(self, lon: float, lat: float) -> Dict:
        """Generate resources for a coordinate based on terrain type."""
        resources = {
            'water': 0.0,
            'food': 0.0,
            'wood': 0.0,
            'stone': 0.0,
            'metal': 0.0
        }
        
        terrain_type = self.terrain_data.get((lon, lat), 'land')
        if terrain_type == 'water':
            resources['water'] = 1.0
            resources['food'] = random.uniform(0.3, 0.7)
        elif terrain_type == 'forest':
            resources['wood'] = random.uniform(0.6, 1.0)
            resources['food'] = random.uniform(0.4, 0.8)
        elif terrain_type == 'mountain':
            resources['stone'] = random.uniform(0.7, 1.0)
            resources['metal'] = random.uniform(0.5, 0.9)
        elif terrain_type == 'grassland':
            resources['food'] = random.uniform(0.5, 0.9)
            resources['water'] = random.uniform(0.3, 0.7)
        elif terrain_type == 'desert':
            resources['stone'] = random.uniform(0.3, 0.7)
            resources['metal'] = random.uniform(0.2, 0.6)
        
        return resources
    
    def _initialize_current(self, current_data: Dict):
        """Initialize an ocean current."""
        start_lon, start_lat = current_data["start"]
        end_lon, end_lat = current_data["end"]
        
        # Calculate direction vector
        dx = end_lon - start_lon
        dy = end_lat - start_lat
        length = math.sqrt(dx*dx + dy*dy)
        direction = (dx/length, dy/length)
        
        # Create current object
        current = OceanCurrent(
            name=current_data["name"],
            direction=direction,
            speed=current_data["speed"],
            temperature=current_data["temp"]
        )
        
        # Add current to grid points
        for lon in np.arange(start_lon, end_lon, self.world.longitude_resolution):
            for lat in np.arange(start_lat, end_lat, self.world.latitude_resolution):
                if self._is_in_range(lon, lat, (start_lon, start_lat), length):
                    self.ocean_currents[(lon, lat)] = current
                    
    def _initialize_tides(self):
        """Initialize tidal data."""
        # Simplified tidal model
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                if self._is_ocean(lon, lat):
                    # Base tidal range
                    base_range = 2.0  # meters
                    
                    # Add variation based on location
                    if abs(lon) < 20:  # Atlantic coast
                        base_range *= 1.5
                    elif 100 < lon < 140:  # Pacific coast
                        base_range *= 1.2
                        
                    self.tidal_ranges[(lon, lat)] = base_range
                    
    def get_current_at(self, longitude: float, latitude: float) -> Optional[OceanCurrent]:
        """Get ocean current at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.ocean_currents.get((lon_grid, lat_grid))
        
    def get_tidal_range_at(self, longitude: float, latitude: float) -> float:
        """Get tidal range at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.tidal_ranges.get((lon_grid, lat_grid), 0.0)
        
    def get_seasonal_factors_at(self, longitude: float, latitude: float) -> Dict[str, float]:
        """Get seasonal factors at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.seasonal_factors.get((lon_grid, lat_grid), {
            "temperature": 1.0,
            "precipitation": 1.0,
            "day_length": 1.0
        })
        
    def get_terrain_at(self, longitude: float, latitude: float) -> str:
        """Get terrain type at given coordinates."""
        # Round to nearest grid point
        lon_rounded = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_rounded = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        
        # Get terrain data, default to water if not found
        terrain = self.terrain_data.get((lon_rounded, lat_rounded), {'type': 'water'})
        
        # Return the terrain type
        return terrain['type']
        
    def get_terrain_info_at(self, longitude: float, latitude: float) -> Dict:
        """Get complete terrain information at specific coordinates."""
        # Round coordinates to nearest grid point
        lon_rounded = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_rounded = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        
        # Get terrain data with defaults
        terrain = self.terrain_data.get((lon_rounded, lat_rounded), {'type': 'water'})
        elevation = self.elevation_data.get((lon_rounded, lat_rounded), 0.0)
        resources = self.resource_data.get((lon_rounded, lat_rounded), {})
        
        return {
            'type': terrain['type'],
            'elevation': elevation,
            'resources': resources,
            'is_water': terrain['type'] == 'water'
        }
        
    def get_elevation_at(self, longitude: float, latitude: float) -> float:
        """Get elevation at given coordinates in meters."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.elevation_data.get((lon_grid, lat_grid), 0.0)
        
    def get_slope_at(self, longitude: float, latitude: float) -> float:
        """Calculate slope at given coordinates in degrees."""
        current_elevation = self.get_elevation_at(longitude, latitude)
        
        # Get elevations at 8 surrounding points
        surrounding_elevations = []
        for dlon in [-1, 0, 1]:
            for dlat in [-1, 0, 1]:
                if dlon == 0 and dlat == 0:
                    continue
                surrounding_elevations.append(
                    self.get_elevation_at(
                        longitude + dlon * self.world.longitude_resolution,
                        latitude + dlat * self.world.latitude_resolution
                    )
                )
                
        # Calculate maximum slope
        max_slope = 0.0
        for elev in surrounding_elevations:
            # Calculate distance to surrounding point
            distance = self.world.get_tile_size(latitude)[0]  # Use longitude distance
            elevation_diff = abs(elev - current_elevation)
            slope = math.degrees(math.atan2(elevation_diff, distance))
            max_slope = max(max_slope, slope)
            
        return max_slope 

    def get_ocean_tiles(self) -> List[Tuple[float, float]]:
        """Get all ocean tile coordinates."""
        ocean_types = {
            TerrainType.DEEP_OCEAN,
            TerrainType.CONTINENTAL_SHELF,
            TerrainType.CONTINENTAL_SLOPE,
            TerrainType.OCEAN_TRENCH
        }
        return [(lon, lat) for (lon, lat), terrain in self.terrain_data.items()
                if terrain['type'] in ocean_types]
                
    def get_depth_at(self, longitude: float, latitude: float) -> float:
        """Get ocean depth at given coordinates in meters."""
        if (longitude, latitude) not in self.elevation_data:
            return 0.0
        elevation = self.elevation_data[(longitude, latitude)]
        return abs(min(0, elevation))  # Convert negative elevation to positive depth
        
    def get_salinity_at(self, longitude: float, latitude: float) -> float:
        """Get ocean salinity at given coordinates in parts per thousand (ppt)."""
        if (longitude, latitude) not in self.salinity_data:
            return 35.0  # Default ocean salinity
        return self.salinity_data[(longitude, latitude)]
        
    def get_oxygen_at(self, longitude: float, latitude: float) -> float:
        """Get ocean oxygen level at given coordinates in mg/L."""
        if (longitude, latitude) not in self.oxygen_data:
            return 6.0  # Default ocean oxygen level
        return self.oxygen_data[(longitude, latitude)]
        
    def get_ocean_current_at(self, longitude: float, latitude: float) -> Optional[OceanCurrent]:
        """Get ocean current at given coordinates."""
        return self.ocean_currents.get((longitude, latitude))
        
    def _initialize_salinity(self):
        """Initialize ocean salinity data."""
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                if self._is_ocean(lon, lat):
                    # Base salinity
                    base_salinity = 35.0  # ppt
                    
                    # Add variation based on location
                    if abs(lat) < 30:  # Tropical regions
                        base_salinity += 2.0  # Higher salinity due to evaporation
                    elif abs(lat) > 60:  # Polar regions
                        base_salinity -= 2.0  # Lower salinity due to ice melt
                        
                    # Add variation based on depth
                    depth = self.get_depth_at(lon, lat)
                    if depth > 1000:  # Deep ocean
                        base_salinity += 0.5
                        
                    self.salinity_data[(lon, lat)] = base_salinity
                    
    def _initialize_oxygen(self):
        """Initialize ocean oxygen data."""
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                if self._is_ocean(lon, lat):
                    # Base oxygen level
                    base_oxygen = 6.0  # mg/L
                    
                    # Add variation based on temperature
                    temperature = self.world.climate.get_temperature_at(lon, lat)
                    if temperature > 25:  # Warm water holds less oxygen
                        base_oxygen -= 1.0
                    elif temperature < 5:  # Cold water holds more oxygen
                        base_oxygen += 1.0
                        
                    # Add variation based on depth
                    depth = self.get_depth_at(lon, lat)
                    if depth > 1000:  # Deep ocean has less oxygen
                        base_oxygen -= 2.0
                        
                    self.oxygen_data[(lon, lat)] = max(0.0, base_oxygen)  # Ensure non-negative
                    
    def _is_in_range(self, lon: float, lat: float, center: Tuple[float, float], radius: float) -> bool:
        """Check if a point is within a circular range."""
        dx = lon - center[0]
        dy = lat - center[1]
        return (dx*dx + dy*dy) <= (radius*radius)
        
    def _is_ocean(self, longitude: float, latitude: float) -> bool:
        """Check if coordinates are in ocean."""
        ocean_types = {
            TerrainType.DEEP_OCEAN,
            TerrainType.CONTINENTAL_SHELF,
            TerrainType.CONTINENTAL_SLOPE,
            TerrainType.OCEAN_TRENCH
        }
        return self.terrain_data.get((longitude, latitude))['type'] in ocean_types 

    def initialize_terrain(self):
        """Initialize the world's terrain."""
        logger.info("Initializing terrain...")
        
        # Initialize terrain data for each coordinate
        for lon in range(-180, 181, 1):
            for lat in range(-90, 91, 1):
                # Generate base terrain
                terrain_type = self._generate_terrain_type(lon, lat)
                self.terrain_data[(lon, lat)] = {
                    "type": terrain_type,
                    "elevation": self._generate_elevation(lon, lat),
                    "resources": self._generate_resources(lon, lat)
                }
                
                # Generate elevation
                elevation = self._generate_elevation(lon, lat)
                self.elevation_data[(lon, lat)] = elevation
                
                # Generate resources
                resources = self._generate_resources(lon, lat)
                self.resource_data[(lon, lat)] = resources
        
        logger.info("Terrain initialization complete")
    
    def get_state(self) -> Dict:
        """Get current terrain system state."""
        return {
            'terrain_data': self.terrain_data,
            'elevation_data': self.elevation_data,
            'resource_data': self.resource_data
        } 