from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import logging
import math
import numpy as np

logger = logging.getLogger(__name__)

class WeatherType(Enum):
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    HEAVY_SNOW = "heavy_snow"
    FOG = "fog"
    WINDY = "windy"
    DROUGHT = "drought"
    HEAT_WAVE = "heat_wave"
    COLD_SNAP = "cold_snap"
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    MONSOON = "monsoon"

@dataclass
class WeatherState:
    temperature: float  # Celsius
    humidity: float  # 0-1
    wind_speed: float  # km/h
    wind_direction: float  # degrees
    precipitation: float  # mm
    cloud_cover: float  # 0-1
    weather_type: WeatherType
    severity: float  # 0-1
    pressure: float  # hPa
    visibility: float  # km
    uv_index: float  # 0-11

class WeatherSystem:
    def __init__(self, world):
        self.world = world
        self.current_weather = WeatherState(
            temperature=20.0,
            humidity=0.5,
            wind_speed=10.0,
            wind_direction=0.0,
            precipitation=0.0,
            cloud_cover=0.2,
            weather_type=WeatherType.CLEAR,
            severity=0.0,
            pressure=1013.25,
            visibility=10.0,
            uv_index=5.0
        )
        self.weather_history: List[WeatherState] = []
        self.season = "spring"  # spring, summer, fall, winter
        self.day_length = 12  # hours of daylight
        self.time_of_day = 0  # 0-23 hours
        self.weather_fronts: List[Dict] = []  # List of active weather fronts
        self.air_masses: Dict[str, Dict] = {}  # Active air masses
        self.initialize_weather_systems()
        
    def initialize_weather_systems(self):
        """Initialize weather systems like fronts and air masses."""
        # Initialize major air masses
        self.air_masses = {
            "arctic": {"temperature": -20, "humidity": 0.3, "pressure": 1020},
            "polar": {"temperature": -5, "humidity": 0.4, "pressure": 1015},
            "tropical": {"temperature": 25, "humidity": 0.7, "pressure": 1010},
            "equatorial": {"temperature": 30, "humidity": 0.8, "pressure": 1008}
        }
        
        # Initialize weather fronts
        self.weather_fronts = [
            {
                "type": "cold",
                "position": (0, 0),
                "direction": (1, 0),
                "speed": 20,
                "intensity": 0.7
            },
            {
                "type": "warm",
                "position": (0, 0),
                "direction": (-1, 0),
                "speed": 15,
                "intensity": 0.5
            }
        ]
    
    def update(self, time_delta: float) -> None:
        """Update weather state based on time, season, and global patterns."""
        # Update time of day
        self.time_of_day = (self.time_of_day + time_delta) % 24
        
        # Update season based on time
        if self.time_of_day == 0:  # New day
            self._update_season()
        
        # Update global weather patterns
        self._update_air_masses()
        self._update_weather_fronts()
        
        # Update local weather
        self._update_temperature()
        self._update_humidity()
        self._update_wind()
        self._update_pressure()
        self._update_precipitation()
        self._update_cloud_cover()
        self._update_weather_type()
        self._update_visibility()
        self._update_uv_index()
        
        # Store weather history
        self.weather_history.append(self.current_weather)
        if len(self.weather_history) > 100:  # Keep last 100 weather states
            self.weather_history.pop(0)
            
        logger.info(f"Weather updated: {self.current_weather.weather_type.value} "
                   f"at {self.current_weather.temperature:.1f}°C")
    
    def _update_air_masses(self):
        """Update positions and properties of air masses."""
        for mass_name, mass in self.air_masses.items():
            # Seasonal temperature adjustments
            if self.season == "summer":
                mass["temperature"] += 5
            elif self.season == "winter":
                mass["temperature"] -= 5
                
            # Random variations
            mass["temperature"] += random.uniform(-0.5, 0.5)
            mass["humidity"] += random.uniform(-0.05, 0.05)
            mass["pressure"] += random.uniform(-1, 1)
            
            # Keep values within reasonable bounds
            mass["humidity"] = max(0.1, min(0.9, mass["humidity"]))
            mass["pressure"] = max(980, min(1040, mass["pressure"]))
    
    def _update_weather_fronts(self):
        """Update positions and properties of weather fronts."""
        for front in self.weather_fronts:
            # Move front
            front["position"] = (
                front["position"][0] + front["direction"][0] * front["speed"],
                front["position"][1] + front["direction"][1] * front["speed"]
            )
            
            # Random intensity changes
            front["intensity"] += random.uniform(-0.1, 0.1)
            front["intensity"] = max(0.1, min(1.0, front["intensity"]))
            
            # Random direction changes
            if random.random() < 0.1:  # 10% chance to change direction
                angle = random.uniform(-30, 30)
                rad = math.radians(angle)
                cos = math.cos(rad)
                sin = math.sin(rad)
                front["direction"] = (
                    front["direction"][0] * cos - front["direction"][1] * sin,
                    front["direction"][0] * sin + front["direction"][1] * cos
                )
    
    def _update_temperature(self) -> None:
        """Update temperature based on season, time of day, and air masses."""
        # Base temperature by season
        base_temp = {
            "spring": 15.0,
            "summer": 25.0,
            "fall": 15.0,
            "winter": 5.0
        }[self.season]
        
        # Daily temperature variation (colder at night)
        daily_variation = 10.0 * math.sin(math.pi * (self.time_of_day - 6) / 12)
        
        # Air mass influence
        air_mass_temp = 0
        for mass in self.air_masses.values():
            air_mass_temp += mass["temperature"]
        air_mass_temp /= len(self.air_masses)
        
        # Front influence
        front_temp = 0
        for front in self.weather_fronts:
            if front["type"] == "cold":
                front_temp -= 5 * front["intensity"]
            else:
                front_temp += 3 * front["intensity"]
        
        # Random variation
        random_variation = random.uniform(-2.0, 2.0)
        
        # Combine all factors
        self.current_weather.temperature = (
            base_temp + 
            daily_variation + 
            air_mass_temp * 0.3 + 
            front_temp * 0.2 + 
            random_variation
        )
    
    def _update_humidity(self) -> None:
        """Update humidity based on weather, season, and air masses."""
        # Base humidity by season
        base_humidity = {
            "spring": 0.6,
            "summer": 0.5,
            "fall": 0.7,
            "winter": 0.4
        }[self.season]
        
        # Air mass influence
        air_mass_humidity = 0
        for mass in self.air_masses.values():
            air_mass_humidity += mass["humidity"]
        air_mass_humidity /= len(self.air_masses)
        
        # Weather effects
        if self.current_weather.weather_type in [WeatherType.RAINY, WeatherType.HEAVY_RAIN, WeatherType.THUNDERSTORM]:
            base_humidity += 0.2
        elif self.current_weather.weather_type == WeatherType.DROUGHT:
            base_humidity -= 0.3
            
        # Combine factors
        self.current_weather.humidity = max(0.0, min(1.0, 
            base_humidity * 0.4 + 
            air_mass_humidity * 0.4 + 
            random.uniform(-0.1, 0.1)
        ))
    
    def _update_wind(self) -> None:
        """Update wind speed and direction based on pressure gradients and fronts."""
        # Base wind by season
        base_wind = {
            "spring": 15.0,
            "summer": 10.0,
            "fall": 20.0,
            "winter": 25.0
        }[self.season]
        
        # Pressure gradient influence
        pressure_gradient = 0
        for mass in self.air_masses.values():
            pressure_gradient += mass["pressure"]
        pressure_gradient = abs(pressure_gradient - 1013.25) / 1013.25
        
        # Front influence
        front_wind = 0
        for front in self.weather_fronts:
            front_wind += front["speed"] * front["intensity"]
        
        # Weather effects
        if self.current_weather.weather_type == WeatherType.THUNDERSTORM:
            base_wind *= 2.0
        elif self.current_weather.weather_type == WeatherType.HURRICANE:
            base_wind *= 3.0
        elif self.current_weather.weather_type == WeatherType.TORNADO:
            base_wind *= 4.0
        elif self.current_weather.weather_type == WeatherType.CLEAR:
            base_wind *= 0.8
            
        # Update wind speed
        self.current_weather.wind_speed = max(0.0, 
            base_wind + 
            pressure_gradient * 20 + 
            front_wind * 0.5 + 
            random.uniform(-5.0, 5.0)
        )
        
        # Update wind direction
        if random.random() < 0.1:  # 10% chance to change direction
            self.current_weather.wind_direction = random.uniform(0, 360)
    
    def _update_pressure(self) -> None:
        """Update atmospheric pressure based on weather systems."""
        # Base pressure
        base_pressure = 1013.25
        
        # Air mass influence
        air_mass_pressure = 0
        for mass in self.air_masses.values():
            air_mass_pressure += mass["pressure"]
        air_mass_pressure /= len(self.air_masses)
        
        # Weather effects
        if self.current_weather.weather_type in [WeatherType.THUNDERSTORM, WeatherType.HURRICANE]:
            base_pressure -= 20
        elif self.current_weather.weather_type == WeatherType.CLEAR:
            base_pressure += 5
            
        # Combine factors
        self.current_weather.pressure = max(950, min(1050,
            base_pressure * 0.3 + 
            air_mass_pressure * 0.7 + 
            random.uniform(-2, 2)
        ))
    
    def _update_precipitation(self) -> None:
        """Update precipitation based on weather, humidity, and temperature."""
        if self.current_weather.weather_type in [WeatherType.RAINY, WeatherType.HEAVY_RAIN, WeatherType.THUNDERSTORM]:
            base_precip = 1.0
            if self.current_weather.weather_type == WeatherType.HEAVY_RAIN:
                base_precip = 3.0
            elif self.current_weather.weather_type == WeatherType.THUNDERSTORM:
                base_precip = 5.0
                
            # Adjust for humidity
            humidity_factor = self.current_weather.humidity * 2
            
            # Adjust for temperature (snow vs rain)
            if self.current_weather.temperature < 0:
                base_precip *= 0.7  # Less snow than rain
                
            self.current_weather.precipitation = base_precip * humidity_factor
        else:
            self.current_weather.precipitation = 0.0
    
    def _update_cloud_cover(self) -> None:
        """Update cloud cover based on weather and humidity."""
        base_clouds = {
            "spring": 0.4,
            "summer": 0.3,
            "fall": 0.5,
            "winter": 0.6
        }[self.season]
        
        # Weather effects
        if self.current_weather.weather_type in [WeatherType.RAINY, WeatherType.HEAVY_RAIN, WeatherType.THUNDERSTORM]:
            base_clouds = 0.9
        elif self.current_weather.weather_type == WeatherType.CLEAR:
            base_clouds = 0.1
        elif self.current_weather.weather_type == WeatherType.FOG:
            base_clouds = 0.8
            
        # Humidity influence
        humidity_factor = self.current_weather.humidity * 0.5
        
        self.current_weather.cloud_cover = max(0.0, min(1.0, 
            base_clouds * 0.6 + 
            humidity_factor * 0.4 + 
            random.uniform(-0.1, 0.1)
        ))
    
    def _update_visibility(self) -> None:
        """Update visibility based on weather conditions."""
        base_visibility = 10.0  # km
        
        # Weather effects
        if self.current_weather.weather_type == WeatherType.FOG:
            base_visibility *= 0.2
        elif self.current_weather.weather_type == WeatherType.HEAVY_RAIN:
            base_visibility *= 0.4
        elif self.current_weather.weather_type == WeatherType.THUNDERSTORM:
            base_visibility *= 0.3
        elif self.current_weather.weather_type == WeatherType.BLIZZARD:
            base_visibility *= 0.1
        elif self.current_weather.weather_type == WeatherType.SANDSTORM:
            base_visibility *= 0.2
            
        # Precipitation effects
        if self.current_weather.precipitation > 0:
            base_visibility *= (1 - self.current_weather.precipitation * 0.1)
            
        self.current_weather.visibility = max(0.1, min(10.0, base_visibility))
    
    def _update_uv_index(self) -> None:
        """Update UV index based on time of day, season, and cloud cover."""
        # Base UV by season
        base_uv = {
            "spring": 5.0,
            "summer": 8.0,
            "fall": 4.0,
            "winter": 2.0
        }[self.season]
        
        # Time of day effect (peak at noon)
        time_factor = math.sin(math.pi * (self.time_of_day - 6) / 12)
        
        # Cloud cover effect
        cloud_factor = 1 - (self.current_weather.cloud_cover * 0.7)
        
        self.current_weather.uv_index = max(0.0, min(11.0,
            base_uv * time_factor * cloud_factor
        ))
    
    def _update_weather_type(self) -> None:
        """Update weather type based on conditions and fronts."""
        # Calculate probabilities for different weather types
        probabilities = {
            WeatherType.CLEAR: 0.3,
            WeatherType.CLOUDY: 0.2,
            WeatherType.RAINY: 0.1,
            WeatherType.HEAVY_RAIN: 0.05,
            WeatherType.THUNDERSTORM: 0.05,
            WeatherType.SNOW: 0.05,
            WeatherType.BLIZZARD: 0.02,
            WeatherType.SANDSTORM: 0.02,
            WeatherType.FOG: 0.05,
            WeatherType.WINDY: 0.1,
            WeatherType.DROUGHT: 0.02,
            WeatherType.HEAT_WAVE: 0.02,
            WeatherType.COLD_SNAP: 0.02,
            WeatherType.HURRICANE: 0.01,
            WeatherType.TORNADO: 0.01,
            WeatherType.MONSOON: 0.02
        }
        
        # Adjust probabilities based on season
        if self.season == "winter":
            probabilities[WeatherType.SNOW] += 0.2
            probabilities[WeatherType.BLIZZARD] += 0.1
            probabilities[WeatherType.HEAT_WAVE] = 0.0
            probabilities[WeatherType.DROUGHT] = 0.0
        elif self.season == "summer":
            probabilities[WeatherType.HEAT_WAVE] += 0.1
            probabilities[WeatherType.DROUGHT] += 0.1
            probabilities[WeatherType.THUNDERSTORM] += 0.1
            probabilities[WeatherType.SNOW] = 0.0
            probabilities[WeatherType.BLIZZARD] = 0.0
        elif self.season == "spring":
            probabilities[WeatherType.RAINY] += 0.1
            probabilities[WeatherType.FOG] += 0.1
        elif self.season == "fall":
            probabilities[WeatherType.WINDY] += 0.1
            probabilities[WeatherType.FOG] += 0.1
            
        # Adjust based on current conditions
        if self.current_weather.humidity > 0.8:
            probabilities[WeatherType.RAINY] += 0.2
            probabilities[WeatherType.HEAVY_RAIN] += 0.1
            probabilities[WeatherType.THUNDERSTORM] += 0.1
        if self.current_weather.temperature > 30:
            probabilities[WeatherType.HEAT_WAVE] += 0.2
            probabilities[WeatherType.DROUGHT] += 0.1
        if self.current_weather.temperature < 0:
            probabilities[WeatherType.COLD_SNAP] += 0.2
            probabilities[WeatherType.SNOW] += 0.1
        if self.current_weather.wind_speed > 50:
            probabilities[WeatherType.HURRICANE] += 0.1
            probabilities[WeatherType.TORNADO] += 0.1
            
        # Front influence
        for front in self.weather_fronts:
            if front["type"] == "cold":
                probabilities[WeatherType.RAINY] += 0.1
                probabilities[WeatherType.THUNDERSTORM] += 0.05
            else:
                probabilities[WeatherType.CLOUDY] += 0.1
                probabilities[WeatherType.FOG] += 0.05
            
        # Normalize probabilities
        total = sum(probabilities.values())
        probabilities = {k: v/total for k, v in probabilities.items()}
        
        # Select weather type
        weather_types = list(probabilities.keys())
        weights = list(probabilities.values())
        self.current_weather.weather_type = random.choices(weather_types, weights=weights)[0]
        
        # Update severity
        self.current_weather.severity = random.random()
    
    def get_weather_effects(self) -> Dict[str, float]:
        """Get effects of current weather on various systems."""
        effects = {
            "temperature": self.current_weather.temperature,
            "humidity": self.current_weather.humidity,
            "wind_speed": self.current_weather.wind_speed,
            "precipitation": self.current_weather.precipitation,
            "cloud_cover": self.current_weather.cloud_cover,
            "pressure": self.current_weather.pressure,
            "visibility": self.current_weather.visibility,
            "uv_index": self.current_weather.uv_index
        }
        
        # Add specific weather type effects
        if self.current_weather.weather_type == WeatherType.THUNDERSTORM:
            effects["damage_risk"] = 0.2
            effects["visibility"] = 0.3
            effects["agriculture"] = 0.8
            effects["construction"] = 0.7
        elif self.current_weather.weather_type == WeatherType.HEAT_WAVE:
            effects["water_consumption"] = 1.5
            effects["crop_growth"] = 0.7
            effects["health"] = 0.8
            effects["energy_consumption"] = 1.3
        elif self.current_weather.weather_type == WeatherType.COLD_SNAP:
            effects["food_consumption"] = 1.3
            effects["crop_growth"] = 0.5
            effects["health"] = 0.8
            effects["energy_consumption"] = 1.5
        elif self.current_weather.weather_type == WeatherType.DROUGHT:
            effects["crop_growth"] = 0.3
            effects["water_consumption"] = 1.2
            effects["agriculture"] = 0.5
        elif self.current_weather.weather_type == WeatherType.HURRICANE:
            effects["damage_risk"] = 0.8
            effects["visibility"] = 0.1
            effects["agriculture"] = 0.3
            effects["construction"] = 0.2
            effects["movement"] = 0.1
        elif self.current_weather.weather_type == WeatherType.TORNADO:
            effects["damage_risk"] = 0.9
            effects["visibility"] = 0.2
            effects["agriculture"] = 0.2
            effects["construction"] = 0.1
            effects["movement"] = 0.2
        elif self.current_weather.weather_type == WeatherType.MONSOON:
            effects["precipitation"] *= 2.0
            effects["agriculture"] = 1.2
            effects["construction"] = 0.6
            effects["movement"] = 0.7
            
        return effects

    def get_state(self) -> Dict:
        """Get current weather state for serialization."""
        return {
            "current_weather": {
                "temperature": self.current_weather.temperature,
                "humidity": self.current_weather.humidity,
                "wind_speed": self.current_weather.wind_speed,
                "wind_direction": self.current_weather.wind_direction,
                "precipitation": self.current_weather.precipitation,
                "cloud_cover": self.current_weather.cloud_cover,
                "weather_type": self.current_weather.weather_type.value,
                "severity": self.current_weather.severity,
                "pressure": self.current_weather.pressure,
                "visibility": self.current_weather.visibility,
                "uv_index": self.current_weather.uv_index
            },
            "season": self.season,
            "day_length": self.day_length,
            "time_of_day": self.time_of_day,
            "effects": self.get_weather_effects()
        }
    
    def get_forecast(self, hours_ahead: int = 24) -> List[WeatherState]:
        """Get weather forecast for the next N hours."""
        forecast = []
        current = self.current_weather
        
        for _ in range(hours_ahead):
            # Create a copy of current weather
            next_weather = WeatherState(
                temperature=current.temperature,
                humidity=current.humidity,
                wind_speed=current.wind_speed,
                wind_direction=current.wind_direction,
                precipitation=current.precipitation,
                cloud_cover=current.cloud_cover,
                weather_type=current.weather_type,
                severity=current.severity,
                pressure=current.pressure,
                visibility=current.visibility,
                uv_index=current.uv_index
            )
            
            # Apply some random changes
            next_weather.temperature += random.uniform(-1.0, 1.0)
            next_weather.humidity += random.uniform(-0.1, 0.1)
            next_weather.wind_speed += random.uniform(-2.0, 2.0)
            next_weather.pressure += random.uniform(-1.0, 1.0)
            
            forecast.append(next_weather)
            current = next_weather
            
        return forecast 