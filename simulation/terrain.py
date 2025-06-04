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
        """Initialize the terrain system."""
        logger.info("Initializing terrain system...")
        self.world = world
        self.terrain_data = {}  # (longitude, latitude) -> Dict
        self.elevation_data = {}  # (longitude, latitude) -> float
        self.resource_data = {}  # (longitude, latitude) -> Dict
        self.ocean_currents = {}  # (longitude, latitude) -> OceanCurrent
        self.tidal_ranges = {}  # (longitude, latitude) -> float
        self.seasonal_factors = {}  # (longitude, latitude) -> Dict
        self.salinity_data = {}  # (longitude, latitude) -> float
        self.oxygen_data = {}  # (longitude, latitude) -> float
        
        # Initialize terrain
        logger.info("Setting up basic terrain...")
        self._initialize_basic_terrain()
        logger.info("Basic terrain initialized")
        
        logger.info("Setting up elevation data...")
        self._initialize_elevation()
        logger.info("Elevation data initialized")
        
        logger.info("Setting up resource data...")
        self._initialize_resources()
        logger.info("Resource data initialized")
        
        logger.info("Setting up ocean systems...")
        self._initialize_ocean_systems()
        logger.info("Ocean systems initialized")
        
        logger.info("Terrain system initialization complete")
        
    def _initialize_basic_terrain(self):
        """Initialize basic terrain data."""
        logger.info("Initializing basic terrain...")
        
        # Calculate total points for progress tracking
        total_points = len(np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution)) * \
                      len(np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution))
        points_processed = 0
        last_progress = 0
        
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                terrain_type = self._generate_terrain_type(lon, lat)
                self.terrain_data[(lon, lat)] = {
                    "type": terrain_type,
                    "elevation": self._generate_elevation(lon, lat),
                    "resources": self._generate_resources(lon, lat)
                }
                points_processed += 1
                
                # Log progress every 10%
                progress = (points_processed / total_points) * 100
                if progress - last_progress >= 10:
                    logger.info(f"Basic terrain initialization progress: {progress:.1f}%")
                    last_progress = progress
                
        logger.info("Basic terrain initialization complete")
        
    def _initialize_elevation(self):
        """Initialize elevation data using vectorized operations."""
        logger.info("Initializing elevation data...")
        
        # Create coordinate grids
        lons = np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution)
        lats = np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution)
        
        # Calculate total points for progress tracking
        total_points = len(lons) * len(lats)
        points_processed = 0
        last_progress = 0
        
        # Process in chunks to show progress
        chunk_size = 1000  # Process 1000 points at a time
        
        for i in range(0, len(lons), chunk_size):
            lon_chunk = lons[i:i + chunk_size]
            for j in range(0, len(lats), chunk_size):
                lat_chunk = lats[j:j + chunk_size]
                
                # Create meshgrid for vectorized operations
                lon_grid, lat_grid = np.meshgrid(lon_chunk, lat_chunk)
                
                # Vectorized elevation generation
                elevations = np.vectorize(self._generate_elevation)(lon_grid, lat_grid)
                
                # Store results
                for idx_lon, lon in enumerate(lon_chunk):
                    for idx_lat, lat in enumerate(lat_chunk):
                        self.elevation_data[(lon, lat)] = elevations[idx_lat, idx_lon]
                        points_processed += 1
                
                # Log progress every 10%
                progress = (points_processed / total_points) * 100
                if progress - last_progress >= 10:
                    logger.info(f"Elevation initialization progress: {progress:.1f}%")
                    last_progress = progress
        
        logger.info("Elevation initialization complete")
        
    def _initialize_resources(self):
        """Initialize resource data using vectorized operations."""
        logger.info("Initializing resource data...")
        
        # Create coordinate grids
        lons = np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution)
        lats = np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution)
        
        # Calculate total points for progress tracking
        total_points = len(lons) * len(lats)
        points_processed = 0
        last_progress = 0
        
        # Process in chunks to show progress
        chunk_size = 1000  # Process 1000 points at a time
        
        for i in range(0, len(lons), chunk_size):
            lon_chunk = lons[i:i + chunk_size]
            for j in range(0, len(lats), chunk_size):
                lat_chunk = lats[j:j + chunk_size]
                
                # Create meshgrid for vectorized operations
                lon_grid, lat_grid = np.meshgrid(lon_chunk, lat_chunk)
                
                # Vectorized resource generation
                resources = np.vectorize(self._generate_resources)(lon_grid, lat_grid)
                
                # Store results
                for idx_lon, lon in enumerate(lon_chunk):
                    for idx_lat, lat in enumerate(lat_chunk):
                        self.resource_data[(lon, lat)] = resources[idx_lat, idx_lon]
                        points_processed += 1
                
                # Log progress every 10%
                progress = (points_processed / total_points) * 100
                if progress - last_progress >= 10:
                    logger.info(f"Resource initialization progress: {progress:.1f}%")
                    last_progress = progress
        
        logger.info("Resource initialization complete")
        
    def _initialize_ocean_systems(self):
        """Initialize ocean-related systems."""
        logger.info("Initializing ocean systems...")
        
        # Initialize ocean currents
        logger.info("Setting up ocean currents...")
        self._initialize_currents()
        logger.info("Ocean currents initialized")
        
        # Initialize tidal systems
        logger.info("Setting up tidal systems...")
        self._initialize_tides()
        logger.info("Tidal systems initialized")
        
        # Initialize salinity
        logger.info("Setting up salinity data...")
        self._initialize_salinity()
        logger.info("Salinity data initialized")
        
        # Initialize oxygen levels
        logger.info("Setting up oxygen levels...")
        self._initialize_oxygen()
        logger.info("Oxygen levels initialized")
        
        logger.info("Ocean systems initialization complete")
        
    def _initialize_currents(self):
        """Initialize ocean currents."""
        logger.info("Initializing ocean currents...")
        
        # Initialize major ocean currents
        logger.info("Setting up major ocean currents...")
        self._initialize_major_currents()
        logger.info("Major ocean currents initialized")
        
        # Initialize local currents
        logger.info("Setting up local currents...")
        self._initialize_local_currents()
        logger.info("Local currents initialized")
        
        # Initialize current interactions
        logger.info("Setting up current interactions...")
        self._initialize_current_interactions()
        logger.info("Current interactions initialized")
        
        logger.info("Ocean currents initialization complete")
        
    def _initialize_major_currents(self):
        """Initialize major ocean currents."""
        logger.info("Initializing major ocean currents...")
        
        # Initialize equatorial currents
        logger.info("Setting up equatorial currents...")
        self._initialize_equatorial_currents()
        logger.info("Equatorial currents initialized")
        
        # Initialize western boundary currents
        logger.info("Setting up western boundary currents...")
        self._initialize_western_boundary_currents()
        logger.info("Western boundary currents initialized")
        
        # Initialize eastern boundary currents
        logger.info("Setting up eastern boundary currents...")
        self._initialize_eastern_boundary_currents()
        logger.info("Eastern boundary currents initialized")
        
        # Initialize circumpolar currents
        logger.info("Setting up circumpolar currents...")
        self._initialize_circumpolar_currents()
        logger.info("Circumpolar currents initialized")
        
        logger.info("Major ocean currents initialization complete")
        
    def _initialize_local_currents(self):
        """Initialize local ocean currents."""
        logger.info("Initializing local ocean currents...")
        
        # Initialize coastal currents
        logger.info("Setting up coastal currents...")
        self._initialize_coastal_currents()
        logger.info("Coastal currents initialized")
        
        # Initialize upwelling zones
        logger.info("Setting up upwelling zones...")
        self._initialize_upwelling_zones()
        logger.info("Upwelling zones initialized")
        
        # Initialize eddies
        logger.info("Setting up eddies...")
        self._initialize_eddies()
        logger.info("Eddies initialized")
        
        logger.info("Local ocean currents initialization complete")
        
    def _initialize_current_interactions(self):
        """Initialize interactions between ocean currents."""
        logger.info("Initializing current interactions...")
        
        # Initialize current convergence zones
        logger.info("Setting up current convergence zones...")
        self._initialize_convergence_zones()
        logger.info("Current convergence zones initialized")
        
        # Initialize current divergence zones
        logger.info("Setting up current divergence zones...")
        self._initialize_divergence_zones()
        logger.info("Current divergence zones initialized")
        
        # Initialize current mixing zones
        logger.info("Setting up current mixing zones...")
        self._initialize_mixing_zones()
        logger.info("Current mixing zones initialized")
        
        logger.info("Current interactions initialization complete")
        
    def _generate_terrain_type(self, lon: float, lat: float) -> str:
        """Generate terrain type based on coordinates."""
        # First determine if this is ocean or land based on a simple pattern
        # Use a combination of sine waves to create realistic continent shapes
        ocean_factor = (
            math.sin(lon * 0.1) * 0.3 +  # East-west variation
            math.sin(lat * 0.1) * 0.3 +  # North-south variation
            math.sin((lon + lat) * 0.05) * 0.2  # Diagonal variation
        )
        
        # Add some randomness
        ocean_factor += random.uniform(-0.1, 0.1)
        
        # If ocean_factor is positive, this is ocean
        if ocean_factor > 0:
            # Determine ocean type based on latitude and longitude
            if abs(lat) > 60:  # Polar regions
                return TerrainType.CONTINENTAL_SHELF.value
            elif abs(lat) > 30:  # Temperate regions
                if random.random() < 0.3:
                    return TerrainType.CONTINENTAL_SHELF.value
                elif random.random() < 0.5:
                    return TerrainType.CONTINENTAL_SLOPE.value
                else:
                    return TerrainType.DEEP_OCEAN.value
            else:  # Tropical regions
                if random.random() < 0.2:
                    return TerrainType.CORAL_REEF.value
                elif random.random() < 0.4:
                    return TerrainType.CONTINENTAL_SHELF.value
                elif random.random() < 0.6:
                    return TerrainType.CONTINENTAL_SLOPE.value
                else:
                    return TerrainType.DEEP_OCEAN.value
        
        # If not ocean, determine land type
        if abs(lat) > 60:  # Polar regions
            return TerrainType.TUNDRA.value
        elif abs(lat) > 30:  # Temperate regions
            if random.random() < 0.3:
                return TerrainType.FOREST.value
            elif random.random() < 0.5:
                return TerrainType.GRASSLAND.value
            else:
                return TerrainType.HILLS.value
        else:  # Tropical regions
            if random.random() < 0.4:
                return TerrainType.DESERT.value
            elif random.random() < 0.6:
                return TerrainType.TROPICAL_RAINFOREST.value
            else:
                return TerrainType.SAVANNA.value
    
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
        
        # Get terrain data, default to deep ocean if not found
        terrain = self.terrain_data.get((lon_rounded, lat_rounded), {'type': TerrainType.DEEP_OCEAN.value})
        
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
        """Initialize salinity data for ocean areas."""
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                terrain = self.get_terrain_at(lon, lat)
                if terrain in ['deep_ocean', 'continental_shelf', 'continental_slope', 'ocean_trench', 'coral_reef', 'seamount', 'abyssal_plain']:
                    # Base salinity on latitude and depth
                    base_salinity = 35.0  # Average ocean salinity in ppt
                    
                    # Adjust for latitude (lower near poles due to ice melt)
                    lat_factor = 1.0 - (abs(lat) / 90.0) * 0.2
                    
                    # Adjust for depth (higher in deep water)
                    depth = self.get_depth_at(lon, lat)
                    depth_factor = 1.0 + (depth / 4000.0) * 0.1
                    
                    # Add some random variation
                    variation = random.uniform(-0.5, 0.5)
                    
                    salinity = base_salinity * lat_factor * depth_factor + variation
                    self.salinity_data[(lon, lat)] = salinity
                else:
                    # Non-ocean areas have zero salinity
                    self.salinity_data[(lon, lat)] = 0.0

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
        """Initialize all terrain systems."""
        logger.info("Starting terrain system initialization...")
        
        # Initialize basic terrain
        logger.info("Step 1/5: Initializing basic terrain...")
        self._initialize_basic_terrain()
        
        # Initialize elevation
        logger.info("Step 2/5: Initializing elevation data...")
        self._initialize_elevation()
        
        # Initialize resources
        logger.info("Step 3/5: Initializing resource data...")
        self._initialize_resources()
        
        # Initialize ocean systems
        logger.info("Step 4/5: Initializing ocean systems...")
        self._initialize_ocean_systems()
        
        # Final verification
        logger.info("Step 5/5: Verifying terrain data...")
        if not self.verify_initialization():
            logger.error("Terrain system initialization verification failed")
            raise RuntimeError("Terrain system initialization verification failed")
        
        logger.info("Terrain system initialization complete")

    def verify_initialization(self) -> bool:
        """Verify that the terrain system is properly initialized."""
        logger.info("Verifying terrain system initialization...")
        
        # Check terrain data
        if not self.terrain_data:
            logger.error("Terrain data not initialized")
            return False
            
        # Check elevation data
        if not self.elevation_data:
            logger.error("Elevation data not initialized")
            return False
            
        # Check resource data
        if not self.resource_data:
            logger.error("Resource data not initialized")
            return False
            
        # Check ocean systems
        if not self.ocean_currents or not self.tidal_ranges:
            logger.error("Ocean systems not initialized")
            return False
            
        # Check environmental data
        if not self.salinity_data or not self.oxygen_data:
            logger.error("Environmental data not initialized")
            return False
            
        logger.info("Terrain system initialization verified successfully")
        return True
    
    def get_state(self) -> Dict:
        """Get current terrain system state."""
        return {
            'terrain_data': self.terrain_data,
            'elevation_data': self.elevation_data,
            'resource_data': self.resource_data
        } 