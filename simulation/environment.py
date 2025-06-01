from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import random
import logging
from .weather import WeatherType, WeatherState, WeatherSystem
from .terrain import TerrainType
from .climate import ClimateType
from datetime import datetime

logger = logging.getLogger(__name__)

class TerrainType(Enum):
    GRASSLAND = "grassland"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    TUNDRA = "tundra"
    WATER = "water"
    SWAMP = "swamp"
    HILLS = "hills"
    PLAINS = "plains"

class WeatherType(Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    BLIZZARD = "blizzard"
    SANDSTORM = "sandstorm"
    FOG = "fog"
    WINDY = "windy"

@dataclass
class Terrain:
    type: TerrainType
    elevation: float  # 0-1 scale
    fertility: float  # 0-1 scale
    water_content: float  # 0-1 scale
    vegetation_density: float  # 0-1 scale
    resource_richness: float  # 0-1 scale

class Environment:
    def __init__(self):
        # Physical world
        self.terrain = {}  # Terrain features
        self.climate = {}  # Climate zones
        self.weather = {}  # Current weather
        self.resources = {}  # Natural resources
        
        # World dimensions
        self.width = 1000
        self.height = 1000
        self.grid_size = 10
        
        # Climate parameters
        self.temperature = 15.0  # Average temperature in Celsius
        self.humidity = 0.5  # Average humidity (0-1)
        self.precipitation = 0.5  # Average precipitation (0-1)
        self.wind_speed = 5.0  # Average wind speed in m/s
        
        # Resource parameters
        self.resource_types = {
            "water": {"renewable": True, "abundance": 0.7},
            "food": {"renewable": True, "abundance": 0.6},
            "wood": {"renewable": True, "abundance": 0.5},
            "stone": {"renewable": False, "abundance": 0.4},
            "metal": {"renewable": False, "abundance": 0.3},
            "energy": {"renewable": True, "abundance": 0.4}
        }
        
        # Environmental events
        self.events = []
        
        # Initialize world
        self._initialize_world()
    
    def _initialize_world(self):
        """Initialize the world with terrain, climate, and resources"""
        # Generate terrain
        self._generate_terrain()
        
        # Generate climate zones
        self._generate_climate_zones()
        
        # Generate initial weather
        self._generate_weather()
        
        # Generate resources
        self._generate_resources()
    
    def _generate_terrain(self):
        """Generate terrain features"""
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                # Generate terrain type
                terrain_type = random.choice([
                    "plains", "forest", "mountains", "desert", "water"
                ])
                
                # Generate terrain features
                elevation = random.uniform(0, 1000)
                fertility = random.uniform(0, 1)
                water_content = random.uniform(0, 1)
                
                self.terrain[(x, y)] = {
                    "type": terrain_type,
                    "elevation": elevation,
                    "fertility": fertility,
                    "water_content": water_content
                }
    
    def _generate_climate_zones(self):
        """Generate climate zones"""
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                # Generate climate based on latitude
                latitude = y / self.height
                
                if latitude < 0.2:
                    climate_type = "tropical"
                elif latitude < 0.4:
                    climate_type = "subtropical"
                elif latitude < 0.6:
                    climate_type = "temperate"
                elif latitude < 0.8:
                    climate_type = "subarctic"
                else:
                    climate_type = "arctic"
                
                self.climate[(x, y)] = {
                    "type": climate_type,
                    "temperature": self._get_temperature(latitude),
                    "humidity": self._get_humidity(climate_type),
                    "precipitation": self._get_precipitation(climate_type)
                }
    
    def _get_temperature(self, latitude: float) -> float:
        """Get temperature based on latitude"""
        base_temp = 30.0 - (latitude * 60.0)  # 30°C at equator, -30°C at poles
        return base_temp + random.uniform(-5, 5)
    
    def _get_humidity(self, climate_type: str) -> float:
        """Get humidity based on climate type"""
        base_humidity = {
            "tropical": 0.8,
            "subtropical": 0.7,
            "temperate": 0.6,
            "subarctic": 0.5,
            "arctic": 0.4
        }
        return base_humidity[climate_type] + random.uniform(-0.1, 0.1)
    
    def _get_precipitation(self, climate_type: str) -> float:
        """Get precipitation based on climate type"""
        base_precipitation = {
            "tropical": 0.8,
            "subtropical": 0.6,
            "temperate": 0.5,
            "subarctic": 0.4,
            "arctic": 0.3
        }
        return base_precipitation[climate_type] + random.uniform(-0.1, 0.1)
    
    def _generate_weather(self):
        """Generate initial weather conditions"""
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                climate = self.climate[(x, y)]
                
                # Generate weather based on climate
                weather_type = self._get_weather_type(climate)
                temperature = climate["temperature"] + random.uniform(-5, 5)
                humidity = climate["humidity"] + random.uniform(-0.1, 0.1)
                wind_speed = random.uniform(0, 20)
                
                self.weather[(x, y)] = {
                    "type": weather_type,
                    "temperature": temperature,
                    "humidity": humidity,
                    "wind_speed": wind_speed
                }
    
    def _get_weather_type(self, climate: Dict) -> str:
        """Get weather type based on climate"""
        if climate["type"] == "tropical":
            return random.choice(["sunny", "rainy", "stormy"])
        elif climate["type"] == "subtropical":
            return random.choice(["sunny", "cloudy", "rainy"])
        elif climate["type"] == "temperate":
            return random.choice(["sunny", "cloudy", "rainy", "snowy"])
        elif climate["type"] == "subarctic":
            return random.choice(["cloudy", "snowy", "stormy"])
        else:  # arctic
            return random.choice(["snowy", "stormy", "blizzard"])
    
    def _generate_resources(self):
        """Generate natural resources"""
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                terrain = self.terrain[(x, y)]
                climate = self.climate[(x, y)]
                
                # Generate resources based on terrain and climate
                self.resources[(x, y)] = self._get_resources(terrain, climate)
    
    def _get_resources(self, terrain: Dict, climate: Dict) -> Dict:
        """Get resources based on terrain and climate"""
        resources = {}
        
        # Water is available everywhere but amount varies
        resources["water"] = min(1.0, terrain["water_content"] * climate["precipitation"])
        
        # Food depends on terrain fertility and climate
        if terrain["type"] in ["plains", "forest"]:
            resources["food"] = terrain["fertility"] * climate["precipitation"]
        
        # Wood depends on forest presence
        if terrain["type"] == "forest":
            resources["wood"] = random.uniform(0.5, 1.0)
        
        # Stone and metal depend on mountains
        if terrain["type"] == "mountains":
            resources["stone"] = random.uniform(0.3, 0.8)
            resources["metal"] = random.uniform(0.1, 0.5)
        
        # Energy depends on climate and terrain
        if climate["type"] in ["tropical", "subtropical"]:
            resources["energy"] = random.uniform(0.6, 1.0)  # Solar
        elif terrain["type"] == "mountains":
            resources["energy"] = random.uniform(0.4, 0.8)  # Wind/Hydro
        
        return resources
    
    def update(self, time_delta: float):
        """Update environment based on time"""
        # Update weather
        self._update_weather(time_delta)
        
        # Update resources
        self._update_resources(time_delta)
        
        # Update climate
        self._update_climate(time_delta)
        
        # Record significant events
        self._record_events()
    
    def _update_weather(self, time_delta: float):
        """Update weather conditions"""
        for pos, weather in self.weather.items():
            climate = self.climate[pos]
            
            # Update temperature
            weather["temperature"] = climate["temperature"] + random.uniform(-2, 2)
            
            # Update humidity
            weather["humidity"] = max(0.0, min(1.0,
                climate["humidity"] + random.uniform(-0.05, 0.05)))
            
            # Update wind speed
            weather["wind_speed"] = max(0.0,
                self.wind_speed + random.uniform(-1, 1))
            
            # Update weather type
            if random.random() < 0.01 * time_delta:
                weather["type"] = self._get_weather_type(climate)
    
    def _update_resources(self, time_delta: float):
        """Update natural resources"""
        for pos, resources in self.resources.items():
            for resource, amount in resources.items():
                resource_info = self.resource_types[resource]
                
                if resource_info["renewable"]:
                    # Renewable resources regenerate
                    regen_rate = 0.01 * time_delta
                    resources[resource] = min(1.0,
                        amount + regen_rate * resource_info["abundance"])
                else:
                    # Non-renewable resources deplete
                    deplete_rate = 0.005 * time_delta
                    resources[resource] = max(0.0,
                        amount - deplete_rate)
    
    def _update_climate(self, time_delta: float):
        """Update climate zones"""
        # Climate changes very slowly
        if random.random() < 0.001 * time_delta:
            for pos, climate in self.climate.items():
                # Small random changes to climate parameters
                climate["temperature"] += random.uniform(-0.1, 0.1)
                climate["humidity"] = max(0.0, min(1.0,
                    climate["humidity"] + random.uniform(-0.01, 0.01)))
                climate["precipitation"] = max(0.0, min(1.0,
                    climate["precipitation"] + random.uniform(-0.01, 0.01)))
    
    def _record_events(self):
        """Record significant environmental events"""
        # Record extreme weather events
        for pos, weather in self.weather.items():
            if weather["temperature"] > 40 or weather["temperature"] < -20:
                self.events.append({
                    "type": "extreme_temperature",
                    "timestamp": datetime.now().isoformat(),
                    "position": pos,
                    "temperature": weather["temperature"]
                })
            
            if weather["wind_speed"] > 15:
                self.events.append({
                    "type": "strong_wind",
                    "timestamp": datetime.now().isoformat(),
                    "position": pos,
                    "wind_speed": weather["wind_speed"]
                })
    
    def get_environment_state(self) -> Dict:
        """Get current state of environment"""
        return {
            "dimensions": {
                "width": self.width,
                "height": self.height,
                "grid_size": self.grid_size
            },
            "climate": {
                "temperature": self.temperature,
                "humidity": self.humidity,
                "precipitation": self.precipitation,
                "wind_speed": self.wind_speed
            },
            "resources": {
                resource: info["abundance"]
                for resource, info in self.resource_types.items()
            }
        }
    
    def get_terrain_at(self, x: float, y: float) -> Dict:
        """Get terrain information at specific coordinates"""
        grid_x = (x // self.grid_size) * self.grid_size
        grid_y = (y // self.grid_size) * self.grid_size
        return self.terrain.get((grid_x, grid_y), {})
    
    def get_climate_at(self, x: float, y: float) -> Dict:
        """Get climate information at specific coordinates"""
        grid_x = (x // self.grid_size) * self.grid_size
        grid_y = (y // self.grid_size) * self.grid_size
        return self.climate.get((grid_x, grid_y), {})
    
    def get_weather_at(self, x: float, y: float) -> Dict:
        """Get weather information at specific coordinates"""
        grid_x = (x // self.grid_size) * self.grid_size
        grid_y = (y // self.grid_size) * self.grid_size
        return self.weather.get((grid_x, grid_y), {})
    
    def get_resources_at(self, x: float, y: float) -> Dict:
        """Get resource information at specific coordinates"""
        grid_x = (x // self.grid_size) * self.grid_size
        grid_y = (y // self.grid_size) * self.grid_size
        return self.resources.get((grid_x, grid_y), {})
    
    def to_dict(self) -> Dict:
        """Convert environment to dictionary"""
        return {
            "terrain": self.terrain,
            "climate": self.climate,
            "weather": self.weather,
            "resources": self.resources,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "precipitation": self.precipitation,
            "wind_speed": self.wind_speed,
            "events": self.events
        } 