from typing import Dict, Tuple, Optional
from enum import Enum
import numpy as np
import math
import logging
import random
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class ClimateType(Enum):
    # Polar Climates
    TUNDRA = "tundra"
    ICE_CAP = "ice_cap"
    
    # Continental Climates
    SUBARCTIC = "subarctic"
    CONTINENTAL = "continental"
    WARM_SUMMER = "warm_summer"
    COLD_SUMMER = "cold_summer"
    
    # Temperate Climates
    MEDITERRANEAN = "mediterranean"
    HUMID_SUBTROPICAL = "humid_subtropical"
    MARINE_WEST_COAST = "marine_west_coast"
    
    # Tropical Climates
    TROPICAL_RAINFOREST = "tropical_rainforest"
    TROPICAL_MONSOON = "tropical_monsoon"
    TROPICAL_SAVANNA = "tropical_savanna"
    
    # Arid Climates
    HOT_DESERT = "hot_desert"
    COLD_DESERT = "cold_desert"
    STEPPE = "steppe"
    
    # Highland Climates
    ALPINE = "alpine"
    SUBALPINE = "subalpine"
    MONTANE = "montane"

class ClimateSystem:
    def __init__(self, world):
        """Initialize the climate system."""
        self.world = world
        self.climate_data = {}  # (longitude, latitude) -> Dict
        self.temperature_data = {}  # (longitude, latitude) -> float
        self.precipitation_data = {}  # (longitude, latitude) -> float
        self.humidity_data = {}  # (longitude, latitude) -> float
        self.wind_data = {}  # (longitude, latitude) -> Dict
        
        # Define coordinate ranges
        self.longitude_range = np.arange(-180.0, 180.0, 1.0)  # 1-degree resolution
        self.latitude_range = np.arange(-90.0, 90.0, 1.0)  # 1-degree resolution
        
        # Initialize maps
        self.temperature_map = np.zeros((len(self.longitude_range), len(self.latitude_range)))
        self.precipitation_map = np.zeros((len(self.longitude_range), len(self.latitude_range)))

        self.wind_map = np.zeros((len(self.longitude_range), len(self.latitude_range)))

        # Simulation time tracking
        self.current_time = 0.0

        self.wind_map = np.zeros((len(self.longitude_range), len(self.latitude_range)))

        # Simulation time tracking
        self.current_time = 0.0

        
        self.initialize_earth_climate()
        
    def initialize_earth_climate(self):
        """Initialize Earth-like climate system."""
        logger.info("Initializing Earth climate system...")
        total_steps = len(self.longitude_range) * len(self.latitude_range)
        current_step = 0
        
        for i, lon in enumerate(self.longitude_range):
            for j, lat in enumerate(self.latitude_range):
                # Initialize temperature
                self.temperature_map[i][j] = self._calculate_base_temperature(lat)
                
                # Initialize precipitation
                self.precipitation_map[i][j] = self._calculate_base_precipitation(lat, lon)
                
                # Initialize wind
                self.wind_map[i][j] = self._calculate_base_wind(lat, lon)
                
                # Update progress
                current_step += 1
                if current_step % 100 == 0:
                    progress = (current_step / total_steps) * 100
                    logger.info(f"Climate initialization progress: {progress:.1f}%")
        
        logger.info("Earth climate system initialized successfully")

    def verify_initialization(self) -> bool:
        """Verify that the climate system is properly initialized."""
        logger.info("Verifying climate system initialization...")
        
        # Check temperature map
        if not hasattr(self, 'temperature_map') or not self.temperature_map.any():
            logger.error("Temperature map not initialized")
            return False
            
        # Check precipitation map
        if not hasattr(self, 'precipitation_map') or not self.precipitation_map.any():
            logger.error("Precipitation map not initialized")
            return False
            
        # Check wind map
        if not hasattr(self, 'wind_map') or not self.wind_map.any():
            logger.error("Wind map not initialized")
            return False
            
        # Check current conditions
        if not hasattr(self, 'current_conditions') or not self.current_conditions:
            logger.error("Current conditions not initialized")
            return False
            
        logger.info("Climate system initialization verified successfully")
        return True
        
    def _initialize_climate_zones(self):
        """Initialize climate zones based on temperature and precipitation."""
        logger.info("Initializing climate zones...")
        
        # Initialize polar climates
        logger.info("Setting up polar climates...")
        self._initialize_polar_climates()
        logger.info("Polar climates initialized")
        
        # Initialize continental climates
        logger.info("Setting up continental climates...")
        self._initialize_continental_climates()
        logger.info("Continental climates initialized")
        
        # Initialize temperate climates
        logger.info("Setting up temperate climates...")
        self._initialize_temperate_climates()
        logger.info("Temperate climates initialized")
        
        # Initialize tropical climates
        logger.info("Setting up tropical climates...")
        self._initialize_tropical_climates()
        logger.info("Tropical climates initialized")
        
        # Initialize arid climates
        logger.info("Setting up arid climates...")
        self._initialize_arid_climates()
        logger.info("Arid climates initialized")
        
        # Initialize highland climates
        logger.info("Setting up highland climates...")
        self._initialize_highland_climates()
        logger.info("Highland climates initialized")
        
        logger.info("Climate zones initialization complete")
        
    def _initialize_seasonal_variations(self):
        """Initialize seasonal variations in climate."""
        logger.info("Initializing seasonal variations...")
        
        # Initialize temperature variations
        logger.info("Setting up temperature variations...")
        self._initialize_temperature_variations()
        logger.info("Temperature variations initialized")
        
        # Initialize precipitation variations
        logger.info("Setting up precipitation variations...")
        self._initialize_precipitation_variations()
        logger.info("Precipitation variations initialized")
        
        # Initialize wind variations
        logger.info("Setting up wind variations...")
        self._initialize_wind_variations()
        logger.info("Wind variations initialized")
        
        logger.info("Seasonal variations initialization complete")
        
    def _initialize_weather_patterns(self):
        """Initialize weather patterns."""
        logger.info("Initializing weather patterns...")
        
        # Initialize storm systems
        logger.info("Setting up storm systems...")
        self._initialize_storm_systems()
        logger.info("Storm systems initialized")
        
        # Initialize pressure systems
        logger.info("Setting up pressure systems...")
        self._initialize_pressure_systems()
        logger.info("Pressure systems initialized")
        
        # Initialize wind patterns
        logger.info("Setting up wind patterns...")
        self._initialize_wind_patterns()
        logger.info("Wind patterns initialized")
        
        logger.info("Weather patterns initialization complete")
        
    def _generate_temperature(self, longitude: float, latitude: float) -> float:
        """Generate temperature based on longitude and latitude."""
        # Base temperature on latitude (solar angle)
        base_temp = 30 * math.cos(math.radians(latitude))  # 30°C at equator, -30°C at poles
        
        # Adjust for ocean currents and continental effects
        if longitude < -100:  # Western North America
            if latitude > 40:  # Pacific Northwest
                base_temp += 5  # Warmer due to Pacific currents
            elif latitude > 30:  # California
                base_temp += 8  # Mediterranean climate
        elif longitude > 100:  # Eastern Asia
            if latitude > 30:  # Japan/Korea
                base_temp += 5  # Warmer due to Kuroshio current
        elif longitude < -20:  # Western Europe
            if latitude > 40:  # Mediterranean
                base_temp += 8  # Mediterranean climate
            else:
                base_temp += 5  # Warmer due to Gulf Stream
                
        # Add elevation effects
        elevation = self.world.terrain.get_elevation_at(longitude, latitude)
        if elevation > 2000:
            base_temp -= (elevation - 2000) * 0.0065  # Temperature decreases 6.5°C per 1000m
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "summer":
            base_temp += 10
        elif season == "winter":
            base_temp -= 10
            
        return base_temp
        
    def _generate_precipitation(self, longitude: float, latitude: float) -> float:
        """Generate precipitation based on longitude and latitude."""
        # Base precipitation on latitude and terrain
        if abs(latitude) > 60:  # Polar regions
            precip = 200  # Low precipitation
        elif abs(latitude) > 45:  # Temperate regions
            if longitude < -100:  # Western North America
                precip = 1500  # High precipitation in Pacific Northwest
            elif longitude > 100:  # Eastern Asia
                precip = 1200  # High precipitation in East Asia
            else:
                precip = 800  # Moderate precipitation
        elif abs(latitude) > 30:  # Subtropical regions
            if longitude < -100:  # Western North America
                precip = 300  # Low precipitation in Southwest
            elif longitude > 100:  # Eastern Asia
                precip = 1500  # High precipitation in East Asia
            else:
                precip = 1000  # Moderate precipitation
        elif abs(latitude) > 15:  # Tropical regions
            if longitude < -100:  # Western North America
                precip = 500  # Moderate precipitation
            elif longitude > 100:  # Eastern Asia
                precip = 2000  # Very high precipitation
            else:
                precip = 1500  # High precipitation
        else:  # Equatorial regions
            precip = 2500  # Very high precipitation
            
        # Adjust for terrain
        terrain = self.world.terrain.get_terrain_at(longitude, latitude)
        if terrain in ['mountain', 'hills']:
            precip *= 1.5  # Orographic precipitation
        elif terrain in ['desert', 'steppe']:
            precip *= 0.3  # Low precipitation
        elif terrain in ['rainforest', 'tropical_rainforest']:
            precip *= 1.5  # High precipitation
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "summer":
            if abs(latitude) < 30:  # Tropical monsoon
                precip *= 2.0
            else:
                precip *= 1.2
        elif season == "winter":
            if abs(latitude) < 30:  # Tropical monsoon
                precip *= 0.5
            else:
                precip *= 0.8
            
        return precip
        
    def _generate_humidity(self, longitude: float, latitude: float) -> float:
        """Generate humidity based on longitude and latitude."""
        # Base humidity on latitude and terrain
        if abs(latitude) < 15:  # Equatorial regions
            base_humidity = 0.8
        elif abs(latitude) < 30:  # Tropical regions
            base_humidity = 0.7
        elif abs(latitude) < 45:  # Subtropical regions
            base_humidity = 0.6
        elif abs(latitude) < 60:  # Temperate regions
            base_humidity = 0.5
        else:  # Polar regions
            base_humidity = 0.4
            
        # Adjust for terrain and proximity to water
        terrain = self.world.terrain.get_terrain_at(longitude, latitude)
        if terrain in ['rainforest', 'tropical_rainforest', 'swamp', 'marsh']:
            base_humidity += 0.2
        elif terrain in ['desert', 'steppe']:
            base_humidity -= 0.2
            
        # Adjust for proximity to large water bodies
        if self._is_near_large_water(longitude, latitude):
            base_humidity += 0.1
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "summer":
            base_humidity += 0.1
        elif season == "winter":
            base_humidity -= 0.1
            
        return min(1.0, max(0.0, base_humidity))
        
    def _is_near_large_water(self, longitude: float, latitude: float) -> bool:
        """Check if coordinates are near a large water body."""
        # Check surrounding tiles for water
        for dlon in [-1, 0, 1]:
            for dlat in [-1, 0, 1]:
                if dlon == 0 and dlat == 0:
                    continue
                check_lon = longitude + dlon * self.world.longitude_resolution
                check_lat = latitude + dlat * self.world.latitude_resolution
                if self.world.terrain.get_terrain_at(check_lon, check_lat) in ['deep_ocean', 'continental_shelf']:
                    return True
        return False
        
    def _generate_wind(self, longitude: float, latitude: float) -> Dict:
        """Generate wind data based on longitude and latitude."""
        # Base wind speed on latitude and terrain
        if abs(latitude) < 15:  # Equatorial regions
            base_speed = 5.0  # m/s
        elif abs(latitude) < 30:  # Tropical regions
            base_speed = 7.0
        elif abs(latitude) < 45:  # Subtropical regions
            base_speed = 10.0
        elif abs(latitude) < 60:  # Temperate regions
            base_speed = 8.0
        else:  # Polar regions
            base_speed = 12.0
            
        # Adjust for terrain
        terrain = self.world.terrain.get_terrain_at(longitude, latitude)
        if terrain in ['mountain', 'hills']:
            base_speed *= 1.5  # Higher winds in mountains
        elif terrain in ['forest', 'rainforest']:
            base_speed *= 0.7  # Reduced winds in forests
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "winter":
            base_speed *= 1.2
            
        # Generate wind direction based on latitude and season
        if abs(latitude) < 15:  # Equatorial regions
            direction = random.uniform(0, 360)  # Variable winds
        elif abs(latitude) < 30:  # Tropical regions
            if latitude > 0:  # Northern hemisphere
                direction = random.uniform(0, 60)  # Northeast trades
            else:  # Southern hemisphere
                direction = random.uniform(120, 180)  # Southeast trades
        elif abs(latitude) < 60:  # Temperate regions
            direction = random.uniform(240, 300)  # Westerlies
        else:  # Polar regions
            direction = random.uniform(0, 360)  # Variable winds
            
        return {
            "speed": base_speed,
            "direction": direction
        }
        
    def _get_season(self, latitude: float) -> str:
        """Get current season based on latitude and time of year."""
        # Calculate day of year (0-365)
        day_of_year = (self.world.time % self.world.year_length) / self.world.day_length
        
        # Determine season based on latitude and day of year
        if abs(latitude) < 15:  # Equatorial regions
            return "summer"  # No distinct seasons
        elif latitude > 0:  # Northern hemisphere
            if day_of_year < 80 or day_of_year > 355:
                return "winter"
            elif day_of_year < 172:
                return "spring"
            elif day_of_year < 264:
                return "summer"
            else:
                return "autumn"
        else:  # Southern hemisphere
            if day_of_year < 80 or day_of_year > 355:
                return "summer"
            elif day_of_year < 172:
                return "autumn"
            elif day_of_year < 264:
                return "winter"
            else:
                return "spring"
                
    def get_climate_at(self, longitude: float, latitude: float) -> Dict:
        """Get climate data at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        
        return self.climate_data.get((lon_grid, lat_grid), {
            "temperature": 15.0,  # Default temperature
            "precipitation": 500.0,  # Default precipitation
            "humidity": 0.5,  # Default humidity
            "wind": {
                "speed": 5.0,
                "direction": 0.0,
                "gust_speed": 7.0
            }
        })
        

    def get_temperature_at(self, longitude: float, latitude: float) -> float:
        """Get temperature at given coordinates in Celsius."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.temperature_data.get((lon_grid, lat_grid), 20.0)

    def get_temperature(self, longitude: float, latitude: float) -> float:
        """Alias for get_temperature_at."""
        return self.get_temperature_at(longitude, latitude)
        
    def get_precipitation_at(self, longitude: float, latitude: float) -> float:
        """Get precipitation at given coordinates in mm/year."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.precipitation_data.get((lon_grid, lat_grid), 0.0)

    # Backwards compatibility for older code
    def get_precipitation(self, longitude: float, latitude: float) -> float:
        return self.get_precipitation_at(longitude, latitude)

    def get_temperature_at(self, longitude: float, latitude: float) -> float:
        """Get temperature at given coordinates in Celsius."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.temperature_data.get((lon_grid, lat_grid), 20.0)

    def get_temperature(self, longitude: float, latitude: float) -> float:
        """Alias for get_temperature_at."""
        return self.get_temperature_at(longitude, latitude)
        
    def get_precipitation_at(self, longitude: float, latitude: float) -> float:
        """Get precipitation at given coordinates in mm/year."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.precipitation_data.get((lon_grid, lat_grid), 0.0)

    # Backwards compatibility for older code
    def get_precipitation(self, longitude: float, latitude: float) -> float:
        return self.get_precipitation_at(longitude, latitude)

        
    def get_humidity_at(self, longitude: float, latitude: float) -> float:
        """Get humidity at given coordinates (0-1)."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.humidity_data.get((lon_grid, lat_grid), 0.5)
        
    def get_wind_at(self, longitude: float, latitude: float) -> Dict:
        """Get wind data at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.wind_data.get((lon_grid, lat_grid), {"speed": 0.0, "direction": 0.0})
        
    def get_state(self) -> Dict:
        """Get current climate system state."""
        return {
            'climate_data': self.climate_data,
            'temperature_data': self.temperature_data,
            'precipitation_data': self.precipitation_data,
            'humidity_data': self.humidity_data,
            'wind_data': self.wind_data
        }
        
    def get_climate_effects(self, longitude: float, latitude: float) -> Dict[str, float]:
        """Get effects of climate on various activities."""
        temp = self.get_temperature_at(longitude, latitude)
        precip = self.get_precipitation_at(longitude, latitude)
        climate = self.get_climate_at(longitude, latitude)
        
        effects = {
            "agriculture": 1.0,
            "construction": 1.0,
            "movement": 1.0,
            "health": 1.0,
            "resource_gathering": 1.0
        }
        
        # Temperature effects
        if temp < 0:
            effects["agriculture"] *= 0.5
            effects["movement"] *= 0.8
            effects["health"] *= 0.9
        elif temp > 35:
            effects["agriculture"] *= 0.7
            effects["movement"] *= 0.7
            effects["health"] *= 0.8
            
        # Precipitation effects
        if precip < 250:  # Arid
            effects["agriculture"] *= 0.5
            effects["health"] *= 0.9
        elif precip > 2000:  # Very wet
            effects["construction"] *= 0.8
            effects["movement"] *= 0.8
            effects["health"] *= 0.9
            
        # Climate-specific effects
        if climate in [ClimateType.TROPICAL_RAINFOREST, ClimateType.TROPICAL_MONSOON]:
            effects["resource_gathering"] *= 1.2
            effects["health"] *= 0.9
        elif climate in [ClimateType.HOT_DESERT, ClimateType.COLD_DESERT]:
            effects["agriculture"] *= 0.3
            effects["health"] *= 0.8
        elif climate in [ClimateType.TUNDRA, ClimateType.ICE_CAP]:
            effects["agriculture"] *= 0.2
            effects["movement"] *= 0.6
            effects["health"] *= 0.7
            
        return effects

    def _initialize_temperature_map(self):
        """Initialize the temperature map based on latitude and elevation."""
        logger.info("Initializing temperature map...")
        for lon in np.arange(-180, 180, self.world.longitude_resolution):
            for lat in np.arange(-90, 90, self.world.latitude_resolution):
                # Base temperature varies with latitude
                base_temp = 30 - abs(lat) * 0.5  # 30°C at equator, decreasing towards poles
                
                # Adjust for elevation
                elevation = self.world.terrain.get_elevation(lon, lat)
                elevation_factor = -0.0065 * elevation  # -6.5°C per 1000m
                
                # Add seasonal variation
                season_factor = 10 * np.sin(2 * np.pi * self.current_time / (365 * 24 * 60))  # 10°C seasonal variation
                
                # Add random variation
                random_factor = np.random.normal(0, 2)  # 2°C standard deviation
                
                temperature = base_temp + elevation_factor + season_factor + random_factor
                self.temperature_map[(lon, lat)] = temperature
        logger.info("Temperature map initialized")

    def _initialize_precipitation_map(self):
        """Initialize the precipitation map based on temperature and terrain."""
        logger.info("Initializing precipitation map...")
        for lon in np.arange(-180, 180, self.world.longitude_resolution):
            for lat in np.arange(-90, 90, self.world.latitude_resolution):
                # Base precipitation varies with latitude
                base_precip = 100 * np.cos(lat * np.pi / 180)  # More precipitation near equator
                
                # Adjust for elevation (more precipitation at higher elevations)
                elevation = self.world.terrain.get_elevation(lon, lat)
                elevation_factor = elevation * 0.1  # 0.1mm per meter
                
                # Adjust for temperature (more precipitation in warmer areas)
                temperature = self.temperature_map.get((lon, lat), 20)
                temp_factor = max(0, temperature - 10) * 2  # 2mm per degree above 10°C
                
                # Add random variation
                random_factor = np.random.normal(0, 20)  # 20mm standard deviation
                
                precipitation = max(0, base_precip + elevation_factor + temp_factor + random_factor)
                self.precipitation_map[(lon, lat)] = precipitation
        logger.info("Precipitation map initialized")

    def _initialize_wind_map(self):
        """Initialize the wind map based on pressure gradients."""
        logger.info("Initializing wind map...")
        for lon in np.arange(-180, 180, self.world.longitude_resolution):
            for lat in np.arange(-90, 90, self.world.latitude_resolution):
                # Base wind speed varies with latitude
                base_speed = 5 + abs(lat) * 0.1  # Stronger winds at higher latitudes
                
                # Add seasonal variation
                season_factor = 2 * np.sin(2 * np.pi * self.current_time / (365 * 24 * 60))
                
                # Add random variation
                random_factor = np.random.normal(0, 1)  # 1 m/s standard deviation
                
                wind_speed = max(0, base_speed + season_factor + random_factor)
                
                # Wind direction (in degrees)
                wind_direction = (lon + 180) % 360  # Basic eastward flow
                
                self.wind_map[(lon, lat)] = (wind_speed, wind_direction)
        logger.info("Wind map initialized")

    def _initialize_current_conditions(self):
        """Initialize current weather conditions."""
        logger.info("Initializing current conditions...")
        for lon in np.arange(-180, 180, self.world.longitude_resolution):
            for lat in np.arange(-90, 90, self.world.latitude_resolution):
                temperature = self.temperature_map.get((lon, lat), 20)
                precipitation = self.precipitation_map.get((lon, lat), 0)
                wind_speed, wind_direction = self.wind_map.get((lon, lat), (0, 0))
                
                # Determine weather type
                if precipitation > 50:
                    weather = "rain"
                elif precipitation > 20:
                    weather = "cloudy"
                elif temperature < 0:
                    weather = "snow"
                else:
                    weather = "clear"
                
                self.current_conditions[(lon, lat)] = {
                    "temperature": temperature,
                    "precipitation": precipitation,
                    "wind_speed": wind_speed,
                    "wind_direction": wind_direction,
                    "weather": weather
                }
        logger.info("Current conditions initialized")

    def update(self, time_delta: float):
        """Update climate conditions over time."""
        logger.info(f"Updating climate conditions for {time_delta} minutes...")
        self.current_time += time_delta
        
        # Update temperature map
        self._update_temperature_map(time_delta)
        
        # Update precipitation map
        self._update_precipitation_map(time_delta)
        
        # Update wind map
        self._update_wind_map(time_delta)
        
        # Update current conditions
        self._update_current_conditions()
        
        logger.info("Climate conditions updated")

    def _update_temperature_map(self, time_delta: float):
        """Update temperature map over time."""

        for (i, j), temp in np.ndenumerate(self.temperature_map):

        for (i, j), temp in np.ndenumerate(self.temperature_map):

            # Daily cycle
            daily_factor = 5 * np.sin(2 * np.pi * (self.current_time % (24 * 60)) / (24 * 60))
            
            # Seasonal cycle
            seasonal_factor = 10 * np.sin(2 * np.pi * self.current_time / (365 * 24 * 60))
            
            # Random variation
            random_factor = np.random.normal(0, 0.1) * time_delta
            

            self.temperature_map[i][j] = temp + daily_factor + seasonal_factor + random_factor

    def _update_precipitation_map(self, time_delta: float):
        """Update precipitation map over time."""
        for (i, j), precip in np.ndenumerate(self.precipitation_map):

            self.temperature_map[i][j] = temp + daily_factor + seasonal_factor + random_factor

    def _update_precipitation_map(self, time_delta: float):
        """Update precipitation map over time."""
        for (i, j), precip in np.ndenumerate(self.precipitation_map):

            # Seasonal variation
            seasonal_factor = 50 * np.sin(2 * np.pi * self.current_time / (365 * 24 * 60))
            
            # Random variation
            random_factor = np.random.normal(0, 5) * time_delta

            self.precipitation_map[i][j] = max(0, precip + seasonal_factor + random_factor)

    def _update_wind_map(self, time_delta: float):
        """Update wind map over time."""
        for (i, j), (speed, direction) in np.ndenumerate(self.wind_map):
            # Seasonal variation in speed
            speed_factor = 2 * np.sin(2 * np.pi * self.current_time / (365 * 24 * 60))
            
            # Random variation
            random_speed = np.random.normal(0, 0.5) * time_delta
            random_direction = np.random.normal(0, 5) * time_delta
            
            new_speed = max(0, speed + speed_factor + random_speed)
            new_direction = (direction + random_direction) % 360
            
            self.wind_map[i][j] = (new_speed, new_direction)

    def _update_current_conditions(self):
        """Update current weather conditions based on maps."""
        for (i, j), temperature in np.ndenumerate(self.temperature_map):
            lon = self.longitude_range[i]
            lat = self.latitude_range[j]
            precipitation = self.precipitation_map[i][j]
            wind_speed, wind_direction = self.wind_map[i][j]
            self.precipitation_map[i][j] = max(0, precip + seasonal_factor + random_factor)

    def _update_wind_map(self, time_delta: float):
        """Update wind conditions across the map."""
        logger.info("Updating wind conditions...")
        
        # Create a new wind map with the same shape
        new_wind_map = np.zeros_like(self.wind_map)
        
        # Update each point
        for i in range(self.wind_map.shape[0]):
            for j in range(self.wind_map.shape[1]):
                # Get current wind speed
                current_speed = self.wind_map[i, j]
                
                # Calculate new wind speed based on time and location
                lat = self.latitude_range[j]
                lon = self.longitude_range[i]
                
                # Base wind speed on latitude (stronger at higher latitudes)
                base_speed = abs(lat) * 0.1
                
                # Add some random variation
                variation = np.random.normal(0, 0.1)
                
                # Calculate new speed
                new_speed = base_speed + variation
                
                # Ensure non-negative
                new_speed = max(0.0, new_speed)
                
                # Store in new map
                new_wind_map[i, j] = new_speed
        
        # Update the wind map
        self.wind_map = new_wind_map
        logger.info("Wind conditions updated")

    def _update_current_conditions(self):
        """Update current weather conditions based on maps."""
        for (i, j), temperature in np.ndenumerate(self.temperature_map):
            lon = self.longitude_range[i]
            lat = self.latitude_range[j]
            precipitation = self.precipitation_map[i][j]
            wind_speed, wind_direction = self.wind_map[i][j]
            
            # Determine weather type
            if precipitation > 50:
                weather = "rain"
            elif precipitation > 20:
                weather = "cloudy"
            elif temperature < 0:
                weather = "snow"
            else:
                weather = "clear"
            
            self.current_conditions[(lon, lat)] = {
                "temperature": temperature,
                "precipitation": precipitation,
                "wind_speed": wind_speed,
                "wind_direction": wind_direction,
                "weather": weather
            }

    def _calculate_base_temperature(self, latitude: float) -> float:
        """Placeholder temperature model based on latitude."""
        return 30.0 - abs(latitude) * 0.3

    def _calculate_base_precipitation(self, latitude: float, longitude: float) -> float:
        """Placeholder precipitation model."""
        return max(0.0, 1.0 - abs(latitude) / 90.0)

    def _calculate_base_wind(self, latitude: float, longitude: float) -> float:
        """Placeholder wind speed model."""
        return abs(latitude) * 0.1 