from typing import Dict, Tuple, Optional
from enum import Enum
import numpy as np
import math
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

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
        self.world = world
        self.climate_data = {}  # (longitude, latitude) -> Dict
        self.temperature_data = {}  # (longitude, latitude) -> float
        self.precipitation_data = {}  # (longitude, latitude) -> float
        self.humidity_data = {}  # (longitude, latitude) -> float
        self.wind_data = {}  # (longitude, latitude) -> Dict
        
        # Initialize climate
        self.initialize_earth_climate()
        
    def initialize_earth_climate(self):
        """Initialize Earth's climate system."""
        logger.info("Initializing Earth climate...")
        
        for lon in np.arange(self.world.min_longitude, self.world.max_longitude, self.world.longitude_resolution):
            for lat in np.arange(self.world.min_latitude, self.world.max_latitude, self.world.latitude_resolution):
                # Generate base climate data
                temperature = self._generate_temperature(lon, lat)
                precipitation = self._generate_precipitation(lon, lat)
                humidity = self._generate_humidity(lon, lat)
                wind = self._generate_wind(lon, lat)
                
                # Store climate data
                self.climate_data[(lon, lat)] = {
                    "temperature": temperature,
                    "precipitation": precipitation,
                    "humidity": humidity,
                    "wind": wind
                }
                
                # Store individual components
                self.temperature_data[(lon, lat)] = temperature
                self.precipitation_data[(lon, lat)] = precipitation
                self.humidity_data[(lon, lat)] = humidity
                self.wind_data[(lon, lat)] = wind
                
        logger.info("Earth climate initialization complete")
        
    def _generate_temperature(self, longitude: float, latitude: float) -> float:
        """Generate temperature based on longitude and latitude."""
        # Basic climate types based on latitude
        if abs(latitude) > 60:  # Polar regions
            base_temp = -20 + 30 * math.cos(math.radians(latitude))  # Colder at poles
            precip = 200 + 100 * math.sin(math.radians(longitude))  # Some variation with longitude
        elif abs(latitude) > 45:  # Temperate regions
            if longitude < -100:  # Western North America
                base_temp = 10 + 20 * math.cos(math.radians(latitude))
                precip = 1000 + 500 * math.sin(math.radians(longitude))
            else:
                base_temp = 5 + 25 * math.cos(math.radians(latitude))
                precip = 500 + 300 * math.sin(math.radians(longitude))
        elif abs(latitude) > 30:  # Subtropical regions
            if longitude < -100:  # Western North America
                base_temp = 15 + 25 * math.cos(math.radians(latitude))
                precip = 400 + 200 * math.sin(math.radians(longitude))
            else:
                base_temp = 20 + 25 * math.cos(math.radians(latitude))
                precip = 1000 + 500 * math.sin(math.radians(longitude))
        elif abs(latitude) > 15:  # Tropical regions
            base_temp = 25 + 10 * math.cos(math.radians(latitude))
            precip = 800 + 400 * math.sin(math.radians(longitude))
        else:  # Equatorial regions
            base_temp = 27 + 5 * math.cos(math.radians(latitude))
            precip = 2000 + 500 * math.sin(math.radians(longitude))
            
        # Add elevation effects
        elevation = self.world.terrain.get_elevation_at(longitude, latitude)
        if elevation > 2000:
            base_temp -= (elevation - 2000) * 0.0065  # Temperature decreases 6.5°C per 1000m
            precip += elevation * 0.1  # More precipitation at higher elevations
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "summer":
            base_temp += 10
            precip *= 0.8
        elif season == "winter":
            base_temp -= 10
            precip *= 1.2
            
        return base_temp
        
    def _generate_precipitation(self, longitude: float, latitude: float) -> float:
        """Generate precipitation based on longitude and latitude."""
        # Basic climate types based on latitude
        if abs(latitude) > 60:  # Polar regions
            precip = 200 + 100 * math.sin(math.radians(longitude))  # Some variation with longitude
        elif abs(latitude) > 45:  # Temperate regions
            if longitude < -100:  # Western North America
                precip = 1000 + 500 * math.sin(math.radians(longitude))
            else:
                precip = 500 + 300 * math.sin(math.radians(longitude))
        elif abs(latitude) > 30:  # Subtropical regions
            if longitude < -100:  # Western North America
                precip = 400 + 200 * math.sin(math.radians(longitude))
            else:
                precip = 1000 + 500 * math.sin(math.radians(longitude))
        elif abs(latitude) > 15:  # Tropical regions
            precip = 800 + 400 * math.sin(math.radians(longitude))
        else:  # Equatorial regions
            precip = 2000 + 500 * math.sin(math.radians(longitude))
            
        # Add elevation effects
        elevation = self.world.terrain.get_elevation_at(longitude, latitude)
        if elevation > 2000:
            precip += elevation * 0.1  # More precipitation at higher elevations
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "summer":
            precip *= 0.8
        elif season == "winter":
            precip *= 1.2
            
        return precip
        
    def _generate_humidity(self, longitude: float, latitude: float) -> float:
        """Generate humidity based on longitude and latitude."""
        # Base humidity on temperature and precipitation
        temperature = self._generate_temperature(longitude, latitude)
        precipitation = self._generate_precipitation(longitude, latitude)
        
        # Higher humidity in tropical regions
        if abs(latitude) < 30:
            base_humidity = 0.7 + (precipitation / 2000) * 0.3
        else:
            base_humidity = 0.5 + (precipitation / 2000) * 0.3
            
        # Adjust for temperature
        if temperature > 25:
            base_humidity *= 1.2  # Warmer air can hold more moisture
        elif temperature < 0:
            base_humidity *= 0.8  # Colder air holds less moisture
            
        # Add seasonal variation
        season = self._get_season(latitude)
        if season == "summer":
            base_humidity *= 1.1
        elif season == "winter":
            base_humidity *= 0.9
            
        return min(1.0, max(0.0, base_humidity))  # Ensure between 0 and 1
        
    def _generate_wind(self, longitude: float, latitude: float) -> Dict:
        """Generate wind data based on longitude and latitude."""
        # Base wind speed on latitude (stronger at higher latitudes)
        base_speed = 5.0 + abs(latitude) * 0.1  # km/h
        
        # Add variation based on terrain
        terrain_type = self.world.terrain.get_terrain_at(longitude, latitude)
        if terrain_type == 'mountain':
            base_speed *= 1.5  # Stronger winds in mountains
        elif terrain_type == 'forest':
            base_speed *= 0.7  # Reduced winds in forests
            
        # Generate wind direction (simplified)
        # Use a combination of latitude-based prevailing winds and random variation
        if abs(latitude) > 60:  # Polar regions
            direction = random.uniform(0, 360)  # Variable winds
        elif abs(latitude) > 30:  # Temperate regions
            # Westerlies
            direction = random.uniform(240, 300)
        else:  # Tropical regions
            # Trade winds
            if latitude > 0:
                direction = random.uniform(0, 60)  # Northeast trades
            else:
                direction = random.uniform(120, 180)  # Southeast trades
                
        return {
            "speed": base_speed,
            "direction": direction,
            "gust_speed": base_speed * random.uniform(1.2, 1.5)
        }
        
    def _get_season(self, latitude: float) -> str:
        """Determine season based on latitude and current date."""
        # Get current date
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        
        # Calculate solar angle
        solar_angle = 23.5 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        
        # Determine season based on latitude and solar angle
        if abs(latitude) < 23.5:  # Tropical regions
            return "summer" if abs(latitude - solar_angle) < 10 else "winter"
        else:  # Temperate and polar regions
            if latitude > 0:  # Northern hemisphere
                if solar_angle > 0:
                    return "summer"
                else:
                    return "winter"
            else:  # Southern hemisphere
                if solar_angle > 0:
                    return "winter"
                else:
                    return "summer"
                    
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
        """Get temperature at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.temperature_data.get((lon_grid, lat_grid), 15.0)
        
    def get_precipitation_at(self, longitude: float, latitude: float) -> float:
        """Get precipitation at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.precipitation_data.get((lon_grid, lat_grid), 500.0)
        
    def get_humidity_at(self, longitude: float, latitude: float) -> float:
        """Get humidity at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.humidity_data.get((lon_grid, lat_grid), 0.5)
        
    def get_wind_at(self, longitude: float, latitude: float) -> Dict:
        """Get wind data at given coordinates."""
        lon_grid = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_grid = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        return self.wind_data.get((lon_grid, lat_grid), {
            "speed": 5.0,
            "direction": 0.0,
            "gust_speed": 7.0
        })
        
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